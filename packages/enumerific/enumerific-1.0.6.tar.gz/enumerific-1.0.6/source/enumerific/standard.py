from __future__ import annotations

from enum import Enum

from enumerific.logging import logger

from enumerific.exceptions import EnumValueError


logger = logger.getChild(__name__)


class Enum(Enum):
    """An extended Enum class that provides support for validating an Enum value and
    accepting either enumeration class properties as enumeration values or their string
    names or values, and providing straightforward access to the enumeration values an
    Enum class holds."""

    @classmethod
    def validate(cls, value: Enum | str | int | object) -> bool:
        """Determine if an enum value name or enum value is valid or not"""

        try:
            return cls.reconcile(value=value, default=None) is not None
        except EnumValueError as exception:
            return False

    @classmethod
    def reconcile(
        cls,
        value: Enum | str | int | object,
        default: Enum = None,
        raises: bool = False,
    ) -> Enum | None:
        """Reconcile enum values and enum names to their corresponding enum option, as
        well as allowing valid enum options to be returned unmodified; if the provided
        enum option, enum value or enum name cannot be reconciled and if a default value
        has been provided, the default value will be returned instead and a warning
        message will be logged, otherwise an EnumValueError exception will be raised."""

        if isinstance(value, str):
            for prop, enumeration in cls.__members__.items():
                if enumeration.name.casefold() == value.casefold():
                    return enumeration
                elif (
                    isinstance(enumeration.value, str)
                    and enumeration.value.casefold() == value.casefold()
                ):
                    return enumeration
        elif isinstance(value, int) and not isinstance(value, bool):
            for prop, enumeration in cls.__members__.items():
                if isinstance(enumeration.value, int) and enumeration.value == value:
                    return enumeration
        elif isinstance(value, bool):
            for prop, enumeration in cls.__members__.items():
                if enumeration.value is value:
                    return enumeration
        elif isinstance(value, cls):
            if value in cls:
                return value
        elif not value is None:
            for prop, enumeration in cls.__members__.items():
                if enumeration.value == value:
                    return enumeration

        if value is not None:
            if raises is True:
                raise EnumValueError(
                    "The provided value, %r, is invalid and does not correspond with this enumeration's options!"
                    % (value)
                )
            else:
                logger.debug(
                    "The provided value, %r, is invalid, but a default, %r, has been provided, and will be returned instead!",
                    value,
                    default,
                )

        return default

    @classmethod
    def options(cls) -> list[Enum]:
        """Provide straightforward access to the list of enumeration options"""

        return cls.__members__.values()
