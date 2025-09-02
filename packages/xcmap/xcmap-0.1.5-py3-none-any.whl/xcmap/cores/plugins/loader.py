import subprocess
from importlib import reload
from typing import Type

import importlib_metadata
from importlib_metadata import entry_points

from xcmap.cores.plugins.interface import PluginProtocol


class PluginLoader:
    def __init__(self, group: str):
        self.group = group
        self._plugins: dict[str, Type[PluginProtocol]] = {}

    def discover(self) -> None:
        """发现所有可用插件"""
        try:
            eps = entry_points(group=self.group)
        except Exception as e:
            raise RuntimeError(f"Entry points loading failed: {str(e)}") from e

        for ep in eps:
            try:
                plugin_cls: Type[PluginProtocol] = ep.load()
                if not isinstance(plugin_cls, type):
                    raise TypeError(f"Invalid plugin type: {ep.name}")

                # 创建临时实例并检查协议
                temp_instance = plugin_cls()
                if not isinstance(temp_instance, PluginProtocol):
                    raise TypeError(f"Plugin {ep.name} does not conform to protocol")

                self._plugins[ep.name] = plugin_cls
            except (ImportError, AttributeError, TypeError) as e:
                print(f"Skipping invalid plugin {ep.name}: {str(e)}")

    def update_from_pypi(self, package_name: str):
        """从PyPI安装/更新指定插件包"""
        try:
            # 安装/更新包
            subprocess.check_call(
                ["pip", "install", "--upgrade", "--no-deps", package_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            # 重载元数据模块
            reload(importlib_metadata)

            # 重新发现插件
            self.discover()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Package update failed: {e}") from e
    def get_plugin(self, name: str) -> tuple[str, PluginProtocol]:
        """获取插件实例"""
        if name not in self._plugins:
            raise KeyError(f"Plugin {name} not found")
        cls_obj = self._plugins[name]()
        return cls_obj.__module__.split(".")[0], cls_obj

    def get_all_plugins(self, refresh: bool = False) -> dict[str, PluginProtocol]:
        if refresh or not self._plugins:  # 强制刷新或首次加载
            self.discover()
        """获取所有插件实例"""
        return {key: cls() for key, cls in self._plugins.items()}
