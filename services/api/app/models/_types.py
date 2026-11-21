from enum import StrEnum

from sqlalchemy import Enum


def str_enum(cls: type[StrEnum], name: str) -> Enum:
    """Store enums as text with a CHECK constraint: easy to migrate, still validated."""
    return Enum(
        cls,
        name=name,
        native_enum=False,
        create_constraint=True,
        length=20,
        values_callable=lambda e: [m.value for m in e],
    )
