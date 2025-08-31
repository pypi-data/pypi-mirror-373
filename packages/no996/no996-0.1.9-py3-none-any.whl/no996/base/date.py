import arrow
import pytz
import structlog

from no996.base.config import settings

logger = structlog.get_logger(__name__)


class Date:
    @staticmethod
    def date_fmt(date: str | arrow.Arrow, fmt: str) -> str:
        if isinstance(date, str):
            date = arrow.get(date)
        return date.format(fmt=fmt)

    @staticmethod
    def str2date(
        date: str, fmt: str, district: str | None = settings.TIME_ZONE
    ) -> arrow.Arrow:
        """字符串转日期

        Args:
            date (str): 日期字符串
            fmt (str): 日期格式
            district (Optional[str], optional): 时区. Defaults to 'Asia/Shanghai'.

        Returns:
            arrow.Arrow: 日期对象
        """
        if district.lower() != "utc":
            return arrow.get(date, fmt).replace(tzinfo=district)

        return arrow.get(date, fmt)

    @staticmethod
    def date_now(
        fmt: str | None = None, district: str | None = settings.TIME_ZONE
    ) -> arrow.Arrow | str:
        """获取当前区域的时间

        Args:
            fmt (Optional[str], optional): _description_. Defaults to None.
            district (Optional[str], optional): _description_. Defaults to 'Asia/Shanghai'.

        Returns:
            Union[arrow.Arrow, str]: _description_
        """

        current_time = arrow.utcnow()
        if district.lower() != "utc":
            timezone = pytz.timezone(district)
            current_time = current_time.to(timezone)

        if not fmt:
            return current_time
        return current_time.format(fmt)

    @staticmethod
    def date_range(
        start_date: str | arrow.Arrow,
        end_date: str | arrow.Arrow,
        fmt: str | None = None,
    ) -> list[arrow.Arrow] | list[str]:
        """获取日期区间内所有的日期


        Args:
            start_date (Union[str, arrow.Arrow]): 起始日期
            end_date (Union[str, arrow.Arrow]): 结束日期
            fmt (Optional[str], optional): 日期格式. Defaults to None.

        Returns:
            Union[List[arrow.Arrow], List[str]]: 返回类型
        """
        if isinstance(start_date, str):
            start_date = arrow.get(start_date)
        if isinstance(end_date, str):
            end_date = arrow.get(end_date)

        if not fmt:
            return [
                arrow.get(i) for i in arrow.Arrow.range("day", start_date, end_date)
            ]
        return [
            arrow.get(i).format(fmt)
            for i in arrow.Arrow.range("day", start_date, end_date)
        ]

    @staticmethod
    def date_range_by_quarter(
        start_date: str | arrow.Arrow,
        end_date: str | arrow.Arrow,
        fmt: str | None = None,
        is_first_day: bool = True,
    ) -> list[arrow.Arrow] | list[str]:
        """获取日期区间内所有的季度，可选季度第一天或者最后一天

        Args:
            start_date (Union[str, arrow.Arrow]): 起始日期
            end_date (Union[str, arrow.Arrow]): 结束日期
            fmt (Optional[str], optional): 日期格式. Defaults to None.

        Returns:
            Union[List[arrow.Arrow], List[str]]: 返回类型
        """
        if isinstance(start_date, str):
            start_date = arrow.get(start_date)
        if isinstance(end_date, str):
            end_date = arrow.get(end_date)

        if not fmt:
            if is_first_day:
                return [
                    arrow.get(i).replace(day=1)
                    for i in arrow.Arrow.range("quarter", start_date, end_date)
                ]
            return [
                quarter.shift(quarters=1).replace(day=1).shift(days=-1).format(fmt)
                for quarter in arrow.Arrow.range("quarter", start_date, end_date)
            ]
        if is_first_day:
            return [
                arrow.get(i).format(fmt)
                for i in arrow.Arrow.range("quarter", start_date, end_date)
            ]
        return [
            quarter.shift(quarters=1).replace(day=1).shift(days=-1).format(fmt)
            for quarter in arrow.Arrow.range("quarter", start_date, end_date)
        ]

    @staticmethod
    def get_dates_before_or_after(
        target_date: str | arrow.Arrow,
        date_list: list[str],
        fmt: str | None,
        before: bool = False,
        sort_dates: bool = False,
    ) -> list[str]:
        target_date_obj = (
            arrow.get(target_date) if isinstance(target_date, str) else target_date
        )
        date_obj_list = [arrow.get(date) for date in date_list]
        filtered_dates = filter(
            lambda date: (date <= target_date_obj and before)
            or (date >= target_date_obj and not before),
            date_obj_list,
        )
        if fmt:
            filtered_dates = [
                Date.date_fmt(date_obj, fmt=fmt) for date_obj in filtered_dates
            ]

        sorted_dates = sorted(filtered_dates) if sort_dates else list(filtered_dates)

        return sorted_dates

    @staticmethod
    def date_cal(
        date: str | arrow.Arrow, days: int, fmt: str = settings.DB_FMT
    ) -> str | arrow.Arrow:
        """日期计算器

        Args:
            date (Union[str, arrow.Arrow]): 日期
            days (int): 天数
            fmt (str): 日期格式. Defaults to DB_FMT.

        Returns:
            Union[str, arrow.Arrow]: 计算结果
        """
        current_date = arrow.get(date)
        new_date = current_date.shift(days=days)
        if isinstance(date, str):
            return new_date.format(fmt)
        return new_date

    @staticmethod
    def date_sep(
        start_date: str | arrow.Arrow,
        end_date: str | arrow.Arrow,
        fmt: str = settings.DB_FMT,
        max_value: int = 300,
    ) -> list[str | arrow.Arrow]:
        """日期分割器

        Args:
            start_date (Union[str, arrow.Arrow]): 起始日期
            end_date (Union[str, arrow.Arrow]): 当前日期
            fmt (str): 返回日期格式
            max_value (int): 分割间隔

        Yields:
            list: 日期列表
        """
        __start_date = start_date
        if isinstance(__start_date, str):
            start_date = arrow.get(start_date)
            end_date = arrow.get(end_date)

        while start_date <= end_date:
            current_date = start_date.shift(days=max_value)

            if current_date > end_date:
                current_date = end_date
                current_date_value = current_date.format(fmt)

            if isinstance(__start_date, str):
                start_date_value = start_date.format(fmt)
                current_date_value = current_date.format(fmt)
                yield [start_date_value, current_date_value]
            else:
                yield [start_date, current_date]

            start_date = current_date.shift(days=1)

    @staticmethod
    def date_compare(
        start_date: str | arrow.Arrow, end_date: str | arrow.Arrow
    ) -> bool:
        """日期比较器

        Args:
            start_date (Union[str, arrow.Arrow]): 起始日期
            end_date (Union[str, arrow.Arrow]): 结束日期

        Returns:
            bool: 布尔值
        """
        if isinstance(start_date, str):
            start_date = arrow.get(start_date)
        if isinstance(end_date, str):
            end_date = arrow.get(end_date)

        return end_date > start_date

    @staticmethod
    def date_quarter_list(
        start_date: str | arrow.Arrow, end_date: str | arrow.Arrow, fmt: str
    ) -> list[str]:
        """获取起始和结束之前的比当前日期小的季度日期

        Returns:
            _type_: _description_
        """
        if isinstance(start_date, str):
            start_date = arrow.get(start_date)
        if isinstance(end_date, str):
            end_date = arrow.get(end_date)

        date_list = []

        start_year = start_date.format("YYYY")
        end_year = end_date.format("YYYY")
        quarter_end_list = ["0331", "0630", "0930", "1231"]
        for year in range(int(start_year), int(end_year) + 1):
            for quarter_date in quarter_end_list:
                quarter_date = f"{year}{quarter_date}"
                if not Date.date_compare(quarter_date, Date.date_now()):
                    break
                quarter_date = arrow.get(quarter_date)
                if fmt:
                    quarter_date = quarter_date.format(fmt)
                date_list.append(quarter_date)
        return date_list

    @staticmethod
    def date_month_list(
        start_date: str | arrow.Arrow,
        end_date: str | arrow.Arrow,
        fmt: str | None = None,
    ) -> list[arrow.Arrow] | list[str]:
        """获取月份列表

        Args:
            start_date (Union[str, arrow.Arrow]): 起始日期
            end_date (Union[str, arrow.Arrow]): 结束日期
            fmt (Optional[str], optional): 日期格式. Defaults to None.

        Returns:
            Union[List[arrow.Arrow], List[str]]: 日期列表
        """
        if isinstance(start_date, str):
            start_date = arrow.get(start_date)
        if isinstance(end_date, str):
            end_date = arrow.get(end_date)

        month_list = []
        if fmt:
            month_list = [
                date.format(fmt)
                for date in arrow.Arrow.range("month", start_date, end_date)
            ]

        else:
            month_list = list(arrow.Arrow.range("month", start_date, end_date))

        return month_list

    @staticmethod
    # 判断日期是否是周末
    def is_weekend(date: str | arrow.Arrow) -> bool:
        """判断日期是否是周末

        Args:
            date (Union[str, arrow.Arrow]): 日期

        Returns:
            bool: 布尔值
        """
        if isinstance(date, str):
            date = arrow.get(date)
        return date.weekday() in [5, 6]

    @staticmethod
    def get_last_weekend(
        date: str | arrow.Arrow, weeks=-1, weekday=4, fmt: str | None = None
    ) -> str | arrow.Arrow:
        """
        获取当前周数前后的指定星期几

        Args:
            date (Union[str, arrow.Arrow]): The date to calculate the last weekend from.
            weeks (int, optional): The number of weeks to shift the date. Defaults to -1.
            weekday (int, optional): The weekday to consider as the weekend. Defaults to 4 (Friday).
            fmt (str, optional): The format to return the date in. Defaults to None.

        Returns:
            str: The date of the last weekend.

        """
        if isinstance(date, str):
            date = arrow.get(date)
        if date.weekday() in [5, 6]:
            date = date.shift(weeks=weeks, weekday=weekday)

        if fmt:
            return date.format(fmt)
        return date

    @staticmethod
    def get_last_date_or_today(
        provided_date: str | arrow.Arrow, fmt: str | None = None
    ) -> str | arrow.Arrow:
        """
        提供一个日期 比如 19910101 如果该日期小于今年，则要返回结束日期为 当年年底的日期 19911231 否则，返回今天日期
        """
        # 获取今天的日期
        today = arrow.now()

        if isinstance(provided_date, str):
            # 转换为 Arrow 对象
            provided_arrow = arrow.get(provided_date)
        else:
            provided_arrow = provided_date

        # 判断提供的日期是否小于今年
        if provided_arrow.year < today.year:
            start_date = arrow.get(provided_arrow.year, 1, 1)  # 获取年初日期
            end_date = start_date.shift(years=1, days=-1)  # 加1年再减一天
            result_date = end_date.format(fmt)
        else:
            result_date = today.format(fmt)
        return result_date
