from __future__ import annotations
from typing import Any, overload, Self, TYPE_CHECKING
from types import ModuleType

import clearskies

if TYPE_CHECKING:
    from clearskies import Model


class Module(clearskies.Column):
    is_writeable = clearskies.configs.boolean.Boolean(default=False)
    _descriptor_config_map = None

    def __init__(self):
        super().__init__()

    @overload
    def __get__(self, instance: None, cls: type[Model]) -> Self:
        pass

    @overload
    def __get__(self, instance: Model, cls: type[Model]) -> ModuleType:
        pass

    def __get__(self, instance, cls):
        return super().__get__(instance, cls)

    def __set__(self, instance: Model, value: ModuleType) -> None:
        instance._next_data[self.name] = value

    def from_backend(self, value):
        return value

    def to_backend(self, data: dict[str, Any]) -> dict[str, Any]:
        if self.name not in data:
            return data
        return {**data, self.name: data[self.name]}
