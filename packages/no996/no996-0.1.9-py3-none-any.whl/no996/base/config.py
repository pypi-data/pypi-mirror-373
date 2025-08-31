from pydantic import AmqpDsn, PostgresDsn, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )

    TIME_ZONE: str

    DB_FMT: str
    DB_TIME_FMT: str

    POSTGRES_SERVER: str
    POSTGRES_DB: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    @computed_field  # type: ignore[misc]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    AMQP_SERVER: str
    AMQP_PORT: int = 5432
    AMQP_USER: str
    AMQP_PASSWORD: str
    AMQP_VHOST: str = "/"

    @computed_field
    @property
    def AMQP_URI(self) -> AmqpDsn:
        return MultiHostUrl.build(
            scheme="amqp",
            username=self.AMQP_USER,
            password=self.AMQP_PASSWORD,
            host=self.AMQP_SERVER,
            port=self.AMQP_PORT,
            path=self.AMQP_VHOST,
        )

    # REDIS_SERVER: str
    # REDIS_PORT: int
    # REDIS_USER: str
    # REDIS_PASSWORD: str

    # @computed_field
    # @property
    # def REDIS_URI(self) -> RedisDsn:
    #     return MultiHostUrl.build(
    #         scheme="redis",
    #         host=self.REDIS_SERVER,
    #         port=self.REDIS_PORT,
    #         password=self.REDIS_PASSWORD,
    #     )

    # @computed_field
    # @property
    # def TASKIQ_BACKEND_URI(self) -> RedisDsn:
    #     return MultiHostUrl.build(
    #         scheme="redis",
    #         host=self.REDIS_SERVER,
    #         username="default",
    #         port=self.REDIS_PORT,
    #         password=self.REDIS_PASSWORD,
    #         path="0",
    #     )


settings = Settings()
