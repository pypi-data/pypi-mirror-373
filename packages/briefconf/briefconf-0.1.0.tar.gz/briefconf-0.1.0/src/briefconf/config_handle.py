from contextlib import suppress
from typing import ClassVar, Self

from ruamel.yaml import YAML, YAMLError


# 非线程安全，但在单个事件循环下是协程安全的。
# 如果运行中不进行写入，只存在读取行为，则可以用于多线程
class BriefConfig():
    _yaml: ClassVar[YAML] = YAML()

    @classmethod
    def load(cls, config_path: str) -> Self:
        """将配置文件里的参数，赋予单独的变量，方便后面程序调用"""
        configs = cls._load_config(config_path)
        configs["logging"] # 实例化类的时候，用 configs 这里面提取的值作为参数
        return cls()

    @classmethod
    def _load_config(cls, config_path: str) -> dict:
        """加载一个配置文件，从中取出其他配置文件的路径（文件不存在不报错），最终合并得到一份配置，如果其他配置里也带有更多配置的路径，同样加载"""
        config = cls._load_config_file(config_path)
        cfg_files = config.pop("other_configs_path", None)
        if not cfg_files:
            return config

        other_configs = {}
        for f in cfg_files:
            with suppress(FileNotFoundError):
                other_config = cls._load_config(f)
                cls._update(other_configs, other_config)
        cls._update(other_configs, config)
        return other_configs

    @classmethod
    def _update(cls, config: dict, other_config: dict):
        """
        遍历新的配置中每个键值对，如果在当前配置中不存在，就新增；存在，若是不可变类型，就用新的覆盖；
        若是列表，就在原有的追加；若是字典，就递归。
        """
        for key, val in other_config.items():
            if key not in config:
                config[key] = val
                continue
            if isinstance(val, (bool, int, float, str)):
                config[key] = val
                continue
            if isinstance(val, list):
                config[key].extend(val)
                continue
            if isinstance(val, dict):
                cls._update(config[key], val)
                continue

    @classmethod
    def _load_config_file(cls, f: str) -> dict:
        try:
            with open(f, 'r', encoding="utf-8") as fp:
                return cls._yaml.load(fp)
        except YAMLError as e:
            raise YAMLError(f"The config file '{f}' is illegal as a YAML: {e}")
        except FileNotFoundError:
            raise FileNotFoundError(f"The config file '{f}' does not exist")
