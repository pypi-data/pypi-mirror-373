class EnumValueError(ValueError):
    pass


class EnumerationError(RuntimeError):
    pass


class EnumerationOptionError(AttributeError, EnumerationError):
    pass


class EnumerationSubclassingError(EnumerationError):
    pass


class EnumerationExtensibilityError(EnumerationError):
    pass


class EnumerationNonUniqueError(EnumerationError):
    pass
