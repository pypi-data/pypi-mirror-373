from sqlalchemy.orm import DeclarativeMeta, declarative_base
from typing import Any, Type
from .models.table import BaseTable


def create_base(cls: Type[Any] = BaseTable) -> DeclarativeMeta:
    return declarative_base(cls=cls)
