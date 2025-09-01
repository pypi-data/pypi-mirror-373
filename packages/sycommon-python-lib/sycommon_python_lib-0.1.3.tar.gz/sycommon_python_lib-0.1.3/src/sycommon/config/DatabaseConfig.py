from pydantic import BaseModel


class HikariConfig(BaseModel):
    minimum_idle: int
    maximum_pool_size: int
    idle_timeout: int


class DatabaseConfig(BaseModel):
    url: str
    username: str
    password: str
    driver_class_name: str
    time_between_eviction_runs_millis: int
    min_evictable_idle_time_millis: int
    validation_query: str
    test_while_idle: bool
    test_on_borrow: bool
    test_on_return: bool
    hikari: HikariConfig


def convert_key_to_snake_case(key):
    import re
    # 处理驼峰命名转换为下划线命名
    key = re.sub(r'(?<!^)(?=[A-Z])', '_', key).lower()
    return key.replace('-', '_')


def convert_dict_keys(d):
    if isinstance(d, dict):
        return {convert_key_to_snake_case(k): convert_dict_keys(v) for k, v in d.items()}
    return d
