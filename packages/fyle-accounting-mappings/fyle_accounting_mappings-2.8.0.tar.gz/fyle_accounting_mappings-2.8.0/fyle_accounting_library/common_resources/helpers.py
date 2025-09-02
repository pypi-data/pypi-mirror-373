from datetime import datetime, timezone
from enum import Enum


def generate_choices_from_enum(enum_class: Enum) -> tuple:
    return tuple((enum.value, enum.value) for enum in enum_class)


def get_values_from_enums(enum: Enum) -> list:
    """
    Get values from enum
    :param enum: Enum
    :return: Values
    """
    return [e.value for e in enum]


def get_current_utc_datetime() -> datetime:
    """
    Get current UTC datetime
    :return: Current UTC datetime
    """
    return datetime.now(timezone.utc)
