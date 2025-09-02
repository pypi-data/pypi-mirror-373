from enum import Enum
from typing import Type, Union, Dict


def extend_enum(
    name: str,
    base_enum: Type[Enum],
    additional_fields: Union[Dict[str, str], Type[Enum]]
) -> Type[Enum]:
    """
    Create a new Enum by extending an existing one with additional fields
    provided either as a dict or another Enum class.

    :param name: Name of the new Enum
    :param base_enum: The base Enum class to extend
    :param additional_fields: A dict or Enum class with new values
    :return: A new Enum class with combined values
    """
    base_members = {e.name: e.value for e in base_enum}
    extra_members = {}
    if isinstance(additional_fields, dict):
        extra_members = additional_fields
    elif isinstance(additional_fields, type) and issubclass(additional_fields, Enum):
        extra_members = {e.name: e.value for e in additional_fields}

    merged_members = {**base_members, **extra_members}

    return Enum(name, merged_members, type=str)
