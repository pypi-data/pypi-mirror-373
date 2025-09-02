from typing import TypeVar, Type, Dict, Any
import yaml

# 定义一个泛型类型变量 T
T = TypeVar('T')


def load_config(file_path: str, config_class: Type[T]) -> T:
    """
    从 YAML 文件加载配置并返回指定类型的配置对象。

    :param file_path: 配置文件的路径
    :param config_class: 配置类的类型（例如 AppConfig）
    :return: 配置类的实例
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        config_data: Dict[str, Any] = yaml.safe_load(file)
    return config_class(**config_data)
