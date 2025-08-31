from typing import Any, List

import pandas as pd
import structlog
from sqlalchemy.exc import NoResultFound
from sqlalchemy.pool import QueuePool
from sqlmodel import (
    Session,
    SQLModel,
    String,
    and_,
    create_engine,
    delete,
    func,
    select,
)
from sqlmodel.sql.expression import ColumnElement, SelectOfScalar

from no996.base.config import settings
from no996.base.date import Date

logger = structlog.get_logger(__name__)

engine = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_timeout=30,
    pool_recycle=3600,
    poolclass=QueuePool,
)


# https://github.com/fastapi/sqlmodel/issues/254
class DBMixin:
    def __init__(self, model: type[SQLModel], session: Session, show_log=True):
        self.model = model
        self.session = session
        self.show_log = show_log

    def get_model(self) -> type[SQLModel]:
        return self.model

    def get_pk_column(self) -> List[str]:
        primary_key_list = []
        for name, column in self.model.model_fields.items():
            if not hasattr(column, "primary_key"):
                return
            primary_key_status = column.primary_key
            if isinstance(primary_key_status, bool) and primary_key_status:
                primary_key_list.append(name)
        return primary_key_list

    def compile(self, statement: ColumnElement | SelectOfScalar):
        if self.show_log:
            # 编译SQL查询语句，获取编译结果
            compiled = statement.compile()
            #
            # 获取参数化的值
            params = compiled.params

            logger.info(f"SQL: {compiled}")
            logger.info(f"Params: {params}")

    def first(self):
        statement = select(self.model)
        return self.session.exec(statement).first()

    def max_field(self, field: str):
        statement = select(func.max(getattr(self.model, field)))
        self.compile(statement)
        return self.session.exec(statement).first()

    def one_by_id(self, _id: int):
        obj = self.session.get(self.model, _id)
        return obj

    def first_by_field(self, field: str, value: Any):
        return self.first_by_fields({field: value})

    def one_by_field(self, field: str, value: Any):
        return self.one_by_fields({field: value})

    def first_by_fields(
        self,
        where_statement: dict | ColumnElement,
        order_by: ColumnElement | None = None,
    ):
        statement = select(self.model)

        if isinstance(where_statement, ColumnElement):
            statement = statement.where(where_statement)
        else:
            for key, value in where_statement.items():
                statement = statement.where(getattr(self.model, key) == value)

        if order_by is not None:
            statement = statement.order_by(order_by)
        self.compile(statement)
        return self.session.exec(statement).first()

    def one_by_fields(self, fields: dict):
        statement = select(self.model)
        for key, value in fields.items():
            statement = statement.where(getattr(self.model, key) == value)
        try:
            return self.session.exec(statement).one()
        except NoResultFound:
            logger.error(f"{self.model}: one_by_fields failed, NoResultFound")
            return None

    def all_by_field(self, field: str, value: Any):
        statement = select(self.model).where(getattr(self.model, field) == value)
        return self.session.exec(statement).all()

    def all_by_fields(
        self,
        where_statement: dict | ColumnElement | None = None,
        order_by: ColumnElement | None = None,
    ):
        statement = select(self.model)

        if where_statement is not None:
            if isinstance(where_statement, ColumnElement):
                statement = statement.where(where_statement)
            else:
                for key, value in where_statement.items():
                    statement = statement.where(getattr(self.model, key) == value)

        if order_by is not None:
            statement = statement.order_by(order_by)

        self.compile(statement)
        return self.session.exec(statement).all()

    def convert_without_saving(
        self, source: dict | SQLModel, update: dict | None = None
    ) -> SQLModel:
        return self.model.model_validate(source, update=update)

    def create(self, source: dict | SQLModel, update: dict | None = None):
        obj = self.convert_without_saving(source, update)
        self.save(obj)
        return obj

    def create_one_a_day(
        self,
        source: dict | SQLModel,
        update: dict | None = None,
        where_dict: dict = None,
    ) -> SQLModel | None:
        """
        创建一条记录，一天仅仅就一条，会将 created_at 作为like条件，如果已经存在则不创建
        """
        if where_dict is None:
            where_dict = {}

        created_at = Date.date_now(settings.DB_FMT)
        if "created_at" in where_dict:
            created_at = where_dict["created_at"]
        else:
            where_dict.update({"created_at": created_at})

        where_list = [func.cast(self.model.created_at, String).like(f"%{created_at}%")]

        for key, value in where_dict.items():
            if key != "created_at":
                where_list.append(getattr(self.model, key) == value)

        count = self.get_count(and_(*where_list))
        if count > 0:
            logger.error("当天仅能记录一条记录. 不得再次创建.")
            return None
        else:
            return self.create(source, update)  # Create

    def create_or_update(
        self, source: dict | SQLModel, update: dict | None = None
    ) -> SQLModel | None:
        obj = self.convert_without_saving(source, update)
        pk = self.model.__mapper__.primary_key_from_instance(obj)

        if pk[0] is not None:
            self.update(obj, where_dict=source)
            return self.one_by_fields(source)
        else:
            return self.create(obj)

    # https://github.com/tiangolo/sqlmodel/issues/494
    def get_count(self, where_statement: dict | ColumnElement) -> int:
        statement = select(self.model)

        if isinstance(where_statement, dict):
            for key, value in where_statement.items():
                statement = statement.where(getattr(self.model, key) == value)
        else:
            statement = statement.where(where_statement)

        q = statement

        count_q = (
            q.with_only_columns(func.count())
            .order_by(None)
            .select_from(q.get_final_froms()[0])
        )

        self.compile(statement)

        result = self.session.exec(count_q)
        return result.one()

    def save(self, data: SQLModel | list[SQLModel], commit=True) -> bool:
        self.session.add(data)
        if commit:
            self.session.commit()

    def update(self, update_dict: dict | SQLModel, where_dict: dict | SQLModel):
        statement = select(self.model)
        for key, value in where_dict.items():
            statement = statement.where(getattr(self.model, key) == value)
        self.compile(statement)
        fetched_model = self.session.exec(statement).all()

        if not fetched_model:
            return 0

        for model in fetched_model:
            if isinstance(update_dict, SQLModel):
                update_dict = update_dict.model_dump(exclude_unset=True)
            for key, value in update_dict.items():
                setattr(model, key, value)  # 更新获取到的模型，而不是传入的模型
            self.save(model, commit=False)

        self.session.commit()

        return len(fetched_model)

    def delete(self, where_statement: dict | ColumnElement = None):
        if where_statement is None:
            where_statement = {}
        statement = delete(self.model)

        if isinstance(where_statement, dict):
            for key, value in where_statement.items():
                statement = statement.where(and_(getattr(self.model, key) == value))
        else:
            statement = statement.where(where_statement)

        self.compile(statement)
        result = self.session.exec(statement)
        self.session.commit()
        return result.rowcount

    def all(self):
        statement = select(self.model)
        self.compile(statement)
        return self.session.exec(statement).all()

    def to_pandas(self) -> pd.DataFrame:
        records = self.all()
        return pd.json_normalize([r.model_dump() for r in records], sep="_")

    # https://github.com/tiangolo/sqlmodel/issues/215
    def model2df(self, objects: List[SQLModel], set_index: bool = True) -> pd.DataFrame:
        if len(objects) > 0:
            records = [obj.model_dump() for obj in objects]
            columns = list(objects[0].model_json_schema()["properties"].keys())
            df = pd.DataFrame.from_records(records, columns=columns)
            return df.set_index(columns[0]) if set_index else df
        return pd.DataFrame()

    def df_to_model(self, df: pd.DataFrame):
        # self.session.bulk_insert_mappings(self.model, df.to_dict("records"))
        # self.session.commit()

        batch_size = 5000  # 根据硬件调整（500-5000）
        records = df.to_dict("records")
        for i in range(0, len(records), batch_size):
            self.session.execute(
                self.model.__table__.insert(), records[i : i + batch_size]
            )
            # self.session.bulk_insert_mappings(
            #     self.model,
            #     records[i:i+batch_size]
            # )
            self.session.commit()  # 每次提交一个批次
            self.session.expire_all()  # 清除会话缓存防内存膨胀
