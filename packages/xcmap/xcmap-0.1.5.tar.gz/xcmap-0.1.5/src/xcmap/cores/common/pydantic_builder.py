from pydantic import BaseModel
from typing import TypeVar, Generic, Type, get_args

T = TypeVar("T", bound=BaseModel)


class PydanticBuilder(Generic[T]):
    def __init__(self, model_cls: Type[T], initial_data: dict | None = None):
        self._model_cls = model_cls
        self._data = initial_data or {}

    def __getattr__(self, name: str):
        """动态生成 setter，链式调用"""
        if name in self._model_cls.model_fields:
            field_type = self._model_cls.model_fields[name].annotation

            def setter(value: field_type):
                self._data[name] = value
                return self

            return setter
        raise AttributeError(f"{type(self).__name__} has no attribute '{name}'")

    def update(self, **kwargs):
        """一次性更新多个字段"""
        for k, v in kwargs.items():
            if k not in self._model_cls.model_fields:
                raise ValueError(f"Field '{k}' not in {self._model_cls.__name__}")
            self._data[k] = v
        return self

    def as_dict(self) -> dict:
        """导出当前数据（默认值 + 已设置的值）"""
        defaults = {
            name: field.default
            for name, field in self._model_cls.model_fields.items()
            if field.default is not None
        }
        return {**defaults, **self._data}

    def build(self) -> T:
        """生成 Pydantic 模型"""
        return self._model_cls(**self.as_dict())

    @classmethod
    def from_model(cls, model_cls: Type[T], initial_data: dict | None = None):
        """直接生成 Builder 实例"""
        return cls(model_cls, initial_data)

    @classmethod
    def from_instance(cls, instance: T):
        """从已有模型创建 Builder"""
        return cls(type(instance), instance.model_dump())

    def clone(self):
        """克隆当前 Builder"""
        return self.__class__.from_model(self._model_cls, self._data.copy())

