from __future__ import annotations

from pydantic import BaseModel, Field

from .field import BaseExtraField
from typing import Generic, TypeVar

__Device_ExtraT = TypeVar("__Device_ExtraT", bound = BaseExtraField)


class Device(BaseModel, Generic[__Device_ExtraT]):
    system: str
    hardware: str
    group: str
    desc: str = Field("")

    extra: __Device_ExtraT = Field(default_factory=BaseExtraField)

    def get_name(self):
        return "{:}-{:}-{:}".format(self.group, self.hardware, self.system)

    def get_domain(self):
        return "{:}-{:}.ssh.{:}".format(self.hardware, self.system, self.group)
