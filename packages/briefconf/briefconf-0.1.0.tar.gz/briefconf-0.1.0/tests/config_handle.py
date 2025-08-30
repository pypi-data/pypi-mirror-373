import logging.config
import os
from dataclasses import dataclass
from typing import Self

from briefconf.v0 import BriefConfig

configfile = os.getenv("BRIEF_CONF_CONFIG_FILE", default="tests/my_config.yaml")


@dataclass(frozen=True)
class Config(BriefConfig):
    # 用户关心、需要手动配置的参数
    is_production: bool

    redis_ip: str
    redis_port: int
    redis_user: str
    redis_password: str
    queue_name: str

    enabled_sth: list[str]
    valid_choices: dict[str, str]

    # 默认无须用户改动的参数
    data_dir: str

    # 用户不应该考虑，开发者可以改的参数
    some_name: str

    __slots__ = ("is_production", )

    @classmethod
    def load(cls, config_path: str) -> Self:
        configs = cls._load_config(config_path)
        logging.config.dictConfig(configs["logging"])

        redis_ip, redis_port = configs['redis_server'].split(':')

        return cls(
            is_production=configs['is_production'],
            redis_ip=redis_ip,
            redis_port=int(redis_port),
            redis_user=configs['redis_user'],
            redis_password=configs['redis_password'],
            queue_name=configs['queue_name'],

            enabled_sth=configs['enabled_sth'],
            valid_choices=configs['valid_choices'],

            data_dir=configs['data_dir'],

            some_name="abc",
        )


config = Config.load(os.path.abspath(configfile))

__all__ = ["config"]
