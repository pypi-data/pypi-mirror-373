"""
对 briefconf 的基本功能进行测试

cd packages/briefconf && uv run -m pytest -s tests/test_basic_func.py; cd -
"""
from tests.config_handle import Config


def test_basic_behavior():
    """两个配置文件没有重复项，看作加载一个配置文件，此时检查值是否和配置中写的一样"""
    config = Config.load("tests/config.example.yaml")
    assert not config.is_production
    assert config.redis_ip == "1.1.1.1"
    assert config.redis_port == 1111
    assert config.redis_user == "default"
    assert config.redis_password == "123abc"
    assert config.queue_name == "my_queue"

    assert config.enabled_sth == ['A', 'B']
    assert config.valid_choices == {"apple": "APPLE", "banana": "BANANA"}

    assert config.data_dir == "config_and_data_files"

def test_merge_behavior():
    """多个配置文件有重复项，此时检查是否按照规则合并"""
    config = Config.load("tests/my_config.yaml")
    # 字符串、数字、布尔是覆盖行为
    assert config.is_production
    assert config.redis_ip == "1.2.3.4"
    assert config.redis_port == 1234
    assert config.redis_user == "vfly2"
    assert config.redis_password == "abcdefg..-"
    assert config.queue_name == "briefconf_queue"

    assert config.enabled_sth == ['A', 'B', 'C', 'D', 'E']
    assert config.valid_choices == {"apple": "APPLE", "banana": "BANANA", "pear": "PEAR"}

    assert config.data_dir == "config_and_data_files"
