from abc import abstractmethod
from typing import Protocol, runtime_checkable


@runtime_checkable
class PluginProtocol(Protocol):
    @abstractmethod
    def initialize(self, config: dict) -> None:
        """插件初始化方法"""
        ...

    @abstractmethod
    def execute(self, *args, **kwargs) -> dict:
        """执行插件功能"""
        ...
