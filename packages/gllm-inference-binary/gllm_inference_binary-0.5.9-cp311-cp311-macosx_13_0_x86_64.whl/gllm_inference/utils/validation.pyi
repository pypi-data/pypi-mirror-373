from enum import StrEnum

def validate_string_enum(enum_type: type[StrEnum], value: str) -> None:
    """Validates that the provided value is a valid string enum value.

    Args:
        enum_type (type[StrEnum]): The type of the string enum.
        value (str): The value to validate.

    Raises:
        ValueError: If the provided value is not a valid string enum value.
    """
