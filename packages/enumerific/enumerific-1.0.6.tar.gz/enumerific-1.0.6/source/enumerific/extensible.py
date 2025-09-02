from __future__ import annotations

import typing
import collections

from enumerific.logging import logger

from enumerific.exceptions import (
    EnumerationError,
    EnumerationOptionError,
    EnumerationSubclassingError,
    EnumerationExtensibilityError,
    EnumerationNonUniqueError,
)

from types import MappingProxyType


logger = logger.getChild(__name__)


class anno(collections.abc.Mapping):
    """The annotations class supports adding annotations to an Enumeration option."""

    _value: object = None
    _annotations: dict[str, object] = None

    def __init__(self, value: object, **annotations: dict[str, object]):
        self._value: object = value

        for key, value in annotations.items():
            if not isinstance(key, str):
                raise TypeError("All annotation values must have string keys!")

        self._annotations: dict[str, object] = annotations

    def __len__(self) -> int:
        return len(self._annotations)

    def __iter__(self) -> str:
        for key in self._annotations.keys():
            yield key

    def __contains__(self, other: object) -> bool:
        return other in self._annotations

    def __getitem__(self, key: str) -> object | None:
        if key in self._annotations:
            return self._annotations[key]
        else:
            raise KeyError(f"The annotation does not have an '{key}' item!")

    def __setitem__(self, key: str, value: object):
        raise NotImplementedError

    def __delitem__(self, key: str, value: object):
        raise NotImplementedError

    def __getattr__(self, name: str) -> object | None:
        if name.startswith("_"):
            return super().__getattr__(name)
        elif name in self._annotations:
            return self._annotations[name]
        else:
            raise AttributeError(f"The annotation does not have an '{name}' attribute!")

    def __setattr__(self, name: str, value: object):
        if name.startswith("_"):
            return super().__setattr__(name, value)
        else:
            raise NotImplementedError

    def __detattr__(self, name: str):
        raise NotImplementedError

    def get(self, name: str, default: object = None) -> object | None:
        if name in self._annotations:
            return self._annotations[name]
        else:
            return default

    def unwrap(self) -> object:
        return self._value


class auto(int, anno):
    """Generate an automatically inrementing integer each time the class is instantiated
    based on the previously supplied configuration, which allows the start and steps to
    be configured as well as if the integers should be generated as powers/flags."""

    start: int = 0
    steps: int = 1
    power: int = 0
    value: int = 0

    @classmethod
    def configure(
        cls,
        start: int = None,
        steps: int = None,
        times: int = None,
        power: int | bool = None,
        flags: bool = None,
    ):
        """Provide support for configuring the auto class with its start, steps, and
        power options, which once set will be used by all subsequent calls to the class'
        auto.__new__() method as called during each class instantiation."""

        if start is None:
            start = 1
        elif isinstance(start, int) and start >= 0:
            pass
        else:
            raise TypeError(
                "The 'start' argument, if specified, must have a positive integer value!"
            )

        if steps is None:
            steps = 1
        elif isinstance(steps, int) and steps >= 0:
            pass
        else:
            raise TypeError(
                "The 'steps' argument, if specified, must have a positive integer value!"
            )

        if times is None:
            times = 0
        elif isinstance(times, int) and times >= 0:
            pass
        else:
            raise TypeError(
                "The 'times' argument, if specified, must have a positive integer value!"
            )

        if power is None:
            power = 0
        elif isinstance(power, bool):
            power = 2 if power is True else 0
        elif isinstance(power, int) and power >= 0:
            pass
        else:
            raise TypeError(
                "The 'power' argument, if specified, must have a positive integer or boolean value!"
            )

        if flags is None:
            pass
        elif isinstance(flags, bool):
            if flags is True:
                power = 2
            elif flags is False:
                power = 0
        else:
            raise TypeError(
                "The 'flags' argument, if specified, must have a boolean value!"
            )

        if flags is True or power == 2:
            if not (start > 0 and (start & (start - 1) == 0)):
                raise ValueError(
                    "If 'flags' is 'True' or 'power' is '2', the 'start' argument must have a value that is a power of two!"
                )

        cls.start = start

        cls.steps = steps

        cls.times = times

        cls.power = power

        cls.value = cls.start

    def __new__(cls, **annotations: dict[str, object]):
        """Create a new integer (int) instance upon each call, incrementing the value as
        per the configuration defined before this method is called; the configuration
        can be changed at any time and the next call to this method will generate the
        next value based on the most recently specified configuration options."""

        if cls.times > 0:
            value = cls.value * cls.times
        elif cls.power > 0:
            value = pow(cls.power, (cls.value - 1))
        else:
            value = cls.value

        cls.value += cls.steps

        return super().__new__(cls, value)

    def __init__(self, **annotations: dict[str, object]):
        super().__init__(self.value, **annotations)


class EnumerationConfiguration(object):
    """The EnumerationConfiguration class holds the Enumeration configuration options"""

    _unique: bool = None
    _aliased: bool = None
    _backfill: bool = None
    _overwritable: bool = None
    _removable: bool = None
    _subclassable: bool = None
    _extensible: bool = None
    _raises: bool = None
    _flags: bool = None
    _start: int = None
    _steps: int = None
    _times: int = None
    _typecast: bool = None

    def __init__(
        self,
        unique: bool = None,
        aliased: bool = None,
        backfill: bool = None,
        overwritable: bool = None,
        removable: bool = None,
        subclassable: bool = None,
        extensible: bool = None,
        raises: bool = None,
        flags: bool = None,
        start: int = None,
        steps: int = None,
        times: int = None,
        typecast: bool = None,
    ):
        self.unique = unique
        self.aliased = aliased
        self.backfill = backfill
        self.overwritable = overwritable
        self.removable = removable
        self.subclassable = subclassable
        self.extensible = extensible
        self.raises = raises
        self.flags = flags
        self.start = start
        self.steps = steps
        self.times = times
        self.typecast = typecast

    def __dir__(self) -> list[str]:
        return [
            "unique",
            "aliased",
            "backfill",
            "overwritable",
            "removable",
            "subclassable",
            "extensible",
            "raises",
            "flags",
            "start",
            "steps",
            "times",
            "typecast",
        ]

    def update(
        self,
        configuration: EnumerationConfiguration,
        nullify: bool = False,
    ) -> EnumerationConfiguration:
        """Support updating of an existing EnumerationConfiguration class instance from
        another EnumerationConfiguration class instance by copying all the options."""

        if not isinstance(configuration, EnumerationConfiguration):
            raise TypeError(
                "The 'configuration' argument must have an EnumerationConfiguration class instance value!"
            )

        if not isinstance(nullify, bool):
            raise TypeError(
                "The 'nullify' argument, if specified, must have a boolean value!"
            )

        for name, value in configuration.options.items():
            if isinstance(value, bool) or nullify is True:
                setattr(self, name, value)

        return self

    def copy(self) -> EnumerationConfiguration:
        return EnumerationConfiguration(**self.options)

    def defaults(self, **options: dict[str, bool]) -> EnumerationConfiguration:
        for name, value in options.items():
            if getattr(self, name, None) is None:
                setattr(self, name, value)

        return self

    @property
    def unique(self) -> bool | None:
        return self._unique

    @unique.setter
    def unique(self, unique: bool | None):
        if unique is None:
            pass
        elif not isinstance(unique, bool):
            raise TypeError(
                "The 'unique' argument, if specified, must have a boolean value!"
            )
        self._unique = unique

    @property
    def aliased(self) -> bool | None:
        return self._aliased

    @aliased.setter
    def aliased(self, aliased: bool | None):
        if aliased is None:
            pass
        elif not isinstance(aliased, bool):
            raise TypeError(
                "The 'aliased' argument, if specified, must have a boolean value!"
            )
        self._aliased = aliased

    @property
    def backfill(self) -> bool | None:
        return self._backfill

    @backfill.setter
    def backfill(self, backfill: bool | None):
        if backfill is None:
            pass
        elif not isinstance(backfill, bool):
            raise TypeError(
                "The 'backfill' argument, if specified, must have a boolean value!"
            )
        self._backfill = backfill

    @property
    def overwritable(self) -> bool | None:
        return self._overwritable

    @overwritable.setter
    def overwritable(self, overwritable: bool | None):
        if overwritable is None:
            pass
        elif not isinstance(overwritable, bool):
            raise TypeError(
                "The 'overwritable' argument, if specified, must have a boolean value!"
            )
        self._overwritable = overwritable

    @property
    def removable(self) -> bool | None:
        return self._removable

    @removable.setter
    def removable(self, removable: bool | None):
        if removable is None:
            pass
        elif not isinstance(removable, bool):
            raise TypeError(
                "The 'removable' argument, if specified, must have a boolean value!"
            )
        self._removable = removable

    @property
    def subclassable(self) -> bool | None:
        return self._subclassable

    @subclassable.setter
    def subclassable(self, subclassable: bool | None):
        if subclassable is None:
            pass
        elif not isinstance(subclassable, bool):
            raise TypeError(
                "The 'subclassable' argument, if specified, must have a boolean value!"
            )
        self._subclassable = subclassable

    @property
    def extensible(self) -> bool | None:
        return self._extensible

    @extensible.setter
    def extensible(self, extensible: bool | None):
        if extensible is None:
            pass
        elif not isinstance(extensible, bool):
            raise TypeError(
                "The 'extensible' argument, if specified, must have a boolean value!"
            )
        self._extensible = extensible

    @property
    def raises(self) -> bool | None:
        return self._raises

    @raises.setter
    def raises(self, raises: bool | None):
        if raises is None:
            pass
        elif not isinstance(raises, bool):
            raise TypeError(
                "The 'raises' argument, if specified, must have a boolean value!"
            )
        self._raises = raises

    @property
    def flags(self) -> bool | None:
        return self._flags

    @flags.setter
    def flags(self, flags: bool | None):
        if flags is None:
            pass
        elif not isinstance(flags, bool):
            raise TypeError(
                "The 'flags' argument, if specified, must have a boolean value!"
            )
        self._flags = flags

    @property
    def start(self) -> int | None:
        return self._start

    @start.setter
    def start(self, start: int | None):
        if start is None:
            pass
        elif not (isinstance(start, int) and start >= 0):
            raise TypeError(
                "The 'start' argument, if specified, must have a positive integer value!"
            )
        self._start = start

    @property
    def steps(self) -> int | None:
        return self._steps

    @steps.setter
    def steps(self, steps: int | None):
        if steps is None:
            pass
        elif not (isinstance(steps, int) and steps >= 0):
            raise TypeError(
                "The 'steps' argument, if specified, must have a positive integer value!"
            )
        self._steps = steps

    @property
    def times(self) -> int | None:
        return self._times

    @times.setter
    def times(self, times: int | None):
        if times is None:
            pass
        elif not (isinstance(times, int) and times >= 0):
            raise TypeError(
                "The 'times' argument, if specified, must have a positive integer value!"
            )
        self._times = times

    @property
    def typecast(self) -> bool | None:
        return self._typecast

    @typecast.setter
    def typecast(self, typecast: bool | None):
        if typecast is None:
            pass
        elif not isinstance(typecast, bool):
            raise TypeError(
                "The 'typecast' argument, if specified, must have a boolean value!"
            )
        self._typecast = typecast

    @property
    def options(self) -> dict[str, bool]:
        properties: dict[str, bool] = {}

        for name in dir(self):
            properties[name] = getattr(self, name)

        return properties


class EnumerationMetaClass(type):
    """EnumerationMetaClass is the metaclass for the Enumerific extensible enumerations
    base class, Enumeration, which can be used to create enumerations and extensible
    enumerations that can often be used in place of standard library enumerations where
    the additional functionality and flexibility to subclass and register or unregister
    options on existing enumerations are beneficial or required for a given use case."""

    _special: list[str] = ["mro", "__options__"]
    _instance: Enumeration = None
    _configuration: EnumerationConfiguration = None
    _enumerations: dict[str, Enumeration] = None

    def __prepare__(
        name: str,
        bases: tuple[type],
        unique: bool = None,
        aliased: bool = None,
        backfill: bool = None,
        overwritable: bool = None,
        subclassable: bool = None,
        extensible: bool = None,
        removable: bool = None,
        raises: bool = None,
        flags: bool = None,
        start: int = None,
        steps: int = None,
        times: int = None,
        typecast: bool = None,
        **kwargs,
    ) -> dict:
        """The __prepare__ method is called when the class signature has been parsed but
        before the class body, allowing us to configure futher class state before the
        class body is parsed. The return value must be a dictionary or dictionary-like
        value that will hold the class' __dict__ values. We are also able to intercept
        any other keyword arguments that are included in the class signature call."""

        logger.debug(
            "[EnumerationMetaClass] %s.__prepare__(name: %s, bases: %s, unique: %s, aliased: %s, backfill: %s, overwritable: %s, subclassable: %s, extensible: %s, removable: %s, raises: %s, flags: %s, start: %s, steps: %s, times: %s, typecast: %s, kwargs: %s)",
            name,
            name,
            bases,
            unique,
            aliased,
            backfill,
            overwritable,
            subclassable,
            extensible,
            removable,
            raises,
            flags,
            start,
            steps,
            times,
            typecast,
            kwargs,
        )

        # Check if the class has been marked with 'flags=True' or if the base class
        # is EnumerationFlag, for the purpose of configuring the auto() class correctly
        if flags is None:
            flags = False

            # Some calls to EnumerationMetaClass.__prepare__ occur before EnumerationFlag
            # has been parsed and created, so we cannot hardcode a reference to it below
            if isinstance(_EnumerationFlag := globals().get("EnumerationFlag"), type):
                for base in bases:
                    if issubclass(base, _EnumerationFlag):
                        flags = True
                        break
        elif isinstance(flags, bool):
            pass
        else:
            raise TypeError(
                "The 'flags' argument, if specified, must have a boolean value!"
            )

        # If an existing enumeration class is being subclassed, determine the maximum
        # value assigned to its options, if those options have integer values; this is
        # useful for enumeration classes that inherit from or automatically typecast to
        # EnumerationInteger or EnumerationFlag, combined with the use of auto() so that
        # if there is the need to subclass one of these classes to extend the available
        # options, that the next available option value assigned via auto() will use the
        # expected value, rather than restarting at the default start value
        if start is None:
            for base in bases:
                if issubclass(base, Enumeration):
                    _maximum_value: int = None

                    if _enumerations := base.enumerations:
                        for _enumeration in _enumerations.values():
                            if isinstance(_enumeration, Enumeration):
                                if isinstance(_enumeration.value, int):
                                    if _maximum_value is None:
                                        _maximum_value = _enumeration.value
                                    elif _enumeration.value > _maximum_value:
                                        _maximum_value = _enumeration.value

                    if isinstance(_maximum_value, int):
                        # Take the maximum value and increment by 1 for the next value
                        if flags is True:
                            start = _maximum_value
                        else:
                            start = _maximum_value + 1
        elif isinstance(start, int) and start >= 0:
            pass
        else:
            raise TypeError(
                "The 'start' argument, if specified, must have a positive integer value!"
            )

        if steps is None:
            pass
        elif isinstance(steps, int) and steps >= 1:
            pass
        else:
            raise TypeError(
                "The 'steps' argument, if specified, must have a positive integer value!"
            )

        if times is None:
            pass
        elif isinstance(times, int) and times >= 1:
            pass
        else:
            raise TypeError(
                "The 'times' argument, if specified, must have a positive integer value!"
            )

        # Configure the auto() class for subsequent use, resetting the sequence, setting
        # the new start value, and whether values should be flag values (powers of 2)
        auto.configure(start=start, steps=steps, times=times, flags=flags)

        return dict()

    def __new__(
        cls,
        *args,
        unique: bool = None,  # True
        aliased: bool = None,  # False
        backfill: bool = None,  # False
        overwritable: bool = None,  # False
        subclassable: bool = None,  # True
        extensible: bool = None,  # True
        removable: bool = None,  # False
        raises: bool = None,  # False
        flags: bool = None,  # False
        start: int = None,  # None
        steps: int = None,  # None
        times: int = None,  # None
        typecast: bool = None,  # True
        **kwargs,
    ):
        logger.debug(
            "[EnumerationMetaClass] %s.__new__(args: %s, kwargs: %s)",
            cls.__name__,
            args,
            kwargs,
        )

        if unique is None:
            pass
        elif not isinstance(unique, bool):
            raise TypeError(
                "The 'unique' argument, if specified, must have a boolean value!"
            )

        if aliased is None:
            pass
        elif not isinstance(aliased, bool):
            raise TypeError(
                "The 'aliased' argument, if specified, must have a boolean value!"
            )

        if backfill is None:
            pass
        elif not isinstance(backfill, bool):
            raise TypeError(
                "The 'backfill' argument, if specified, must have a boolean value!"
            )

        if overwritable is None:
            pass
        elif not isinstance(overwritable, bool):
            raise TypeError(
                "The 'overwritable' argument, if specified, must have a boolean value!"
            )

        if subclassable is None:
            pass
        elif not isinstance(subclassable, bool):
            raise TypeError(
                "The 'subclassable' argument, if specified, must have a boolean value!"
            )

        if extensible is None:
            pass
        elif not isinstance(extensible, bool):
            raise TypeError(
                "The 'extensible' argument, if specified, must have a boolean value!"
            )

        if removable is None:
            pass
        elif not isinstance(removable, bool):
            raise TypeError(
                "The 'removable' argument, if specified, must have a boolean value!"
            )

        if raises is None:
            pass
        elif not isinstance(raises, bool):
            raise TypeError(
                "The 'raises' argument, if specified, must have a boolean value!"
            )

        if flags is None:
            pass
        elif not isinstance(flags, bool):
            raise TypeError(
                "The 'flags' argument, if specified, must have a boolean value!"
            )

        if start is None:
            pass
        elif not (isinstance(start, int) and start >= 0):
            raise TypeError(
                "The 'start' argument, if specified, must have a positive integer value!"
            )

        if steps is None:
            pass
        elif not (isinstance(steps, int) and steps >= 0):
            raise TypeError(
                "The 'steps' argument, if specified, must have a positive integer value!"
            )

        if times is None:
            pass
        elif not (isinstance(times, int) and times >= 0):
            raise TypeError(
                "The 'times' argument, if specified, must have a positive integer value!"
            )

        if typecast is None:
            pass
        elif not isinstance(typecast, bool):
            raise TypeError(
                "The 'typecast' argument, if specified, must have a boolean value!"
            )

        configuration = EnumerationConfiguration(
            unique=unique,
            aliased=aliased,
            backfill=backfill,
            overwritable=overwritable,
            subclassable=subclassable,
            extensible=extensible,
            removable=removable,
            raises=raises,
            flags=flags,
            start=start,
            steps=steps,
            times=times,
            typecast=typecast,
        )

        (name, bases, attributes) = args  # Unpack the arguments passed to the metaclass

        logger.debug(" >>> name          => %s", name)
        logger.debug(" >>> bases         => %s", [base for base in bases])
        logger.debug(" >>> attributes    => %s", attributes)
        logger.debug(" >>> configuration => %s", configuration)

        if not bases:
            return super().__new__(cls, *args, **kwargs)

        enumerations: dict[str, object] = {}  # Keep track of the enumeration options
        annotations: dict[str, dict] = {}  # Keep track of the enumeration annotations

        names: list[object] = []  # Keep track of the option names to check uniqueness
        values: list[object] = []  # Keep track of the option values to check uniqueness

        # By default new Enumeration subclasses will be based on the Enumeration class
        baseclass: Enumeration = None

        _enumerations: dict[str, object] = None

        # Attempt to inherit enumeration options if an existing populated Enumeration
        # subclass is being subclassed; this is only performed for subclasses of
        # subclasses of Enumeration, not for direct subclasses, such as the specialized
        # Enumeration subclasses like EnumerationInteger which don't have any options
        for base in bases:
            logger.debug(" >>> analysing => %s", base)
            logger.debug(
                " >>> isinstance (meta) => %s", isinstance(base, EnumerationMetaClass)
            )
            logger.debug(" >>> issubclass (main) => %s", issubclass(base, Enumeration))

            if isinstance(base, EnumerationMetaClass) or issubclass(base, Enumeration):
                logger.debug(" >>> base (type)  => %s (%s)", base, type(base))

                if issubclass(base, Enumeration):
                    # Prevent an Enumeration class subclass from being created with two or more Enumeration base classes
                    if not baseclass is None:
                        raise TypeError(
                            "Subclassing an Enumeration from multiple Enumeration superclasses (bases) is not supported; enusure that only one of the base classes is an Enumeration class or one of its subclasses!"
                        )

                    baseclass = base

                    logger.debug(" >>> baseclass => %s", baseclass)

                    if isinstance(
                        base_configuration := base.configuration,
                        EnumerationConfiguration,
                    ):
                        logger.debug(
                            " >>> unique       => %s", base_configuration.unique
                        )
                        logger.debug(
                            " >>> aliased      => %s", base_configuration.aliased
                        )
                        logger.debug(
                            " >>> backfill     => %s", base_configuration.backfill
                        )
                        logger.debug(
                            " >>> overwritable => %s", base_configuration.overwritable
                        )
                        logger.debug(
                            " >>> subclassable => %s", base_configuration.subclassable
                        )
                        logger.debug(
                            " >>> extensible   => %s", base_configuration.extensible
                        )
                        logger.debug(
                            " >>> removable    => %s", base_configuration.removable
                        )
                        logger.debug(
                            " >>> raises       => %s", base_configuration.raises
                        )
                        logger.debug(
                            " >>> flags        => %s", base_configuration.flags
                        )
                        logger.debug(
                            " >>> start        => %s", base_configuration.start
                        )
                        logger.debug(
                            " >>> steps        => %s", base_configuration.steps
                        )
                        logger.debug(
                            " >>> times        => %s", base_configuration.times
                        )
                        logger.debug(
                            " >>> typecast     => %s", base_configuration.typecast
                        )

                        if (
                            base_configuration.subclassable is False
                            or base_configuration.extensible is False
                        ):
                            raise EnumerationSubclassingError(
                                "The '%s' enumeration class cannot be subclassed when the keyword arguments 'subclassable=False' or 'extensible=False` are passed to the class constructor!"
                                % (base.__name__)
                            )

                        # Copy the base class constructor options and update them with our local configuration
                        configuration = base_configuration.copy().update(
                            configuration, nullify=False
                        )

                        logger.debug(
                            " >>> (updated) unique       => %s", configuration.unique
                        )
                        logger.debug(
                            " >>> (updated) aliased      => %s", configuration.aliased
                        )
                        logger.debug(
                            " >>> (updated) backfill     => %s", configuration.backfill
                        )
                        logger.debug(
                            " >>> (updated) overwritable => %s",
                            configuration.overwritable,
                        )
                        logger.debug(
                            " >>> (updated) subclassable => %s",
                            configuration.subclassable,
                        )
                        logger.debug(
                            " >>> (updated) extensible => %s",
                            configuration.extensible,
                        )
                        logger.debug(
                            " >>> (updated) removable    => %s", configuration.removable
                        )
                        logger.debug(
                            " >>> (updated) raises       => %s", configuration.raises
                        )
                        logger.debug(
                            " >>> (updated) flags        => %s", configuration.flags
                        )
                        logger.debug(
                            " >>> (updated) start        => %s", configuration.start
                        )
                        logger.debug(
                            " >>> (updated) steps        => %s", configuration.steps
                        )
                        logger.debug(
                            " >>> (updated) times        => %s", configuration.times
                        )
                        logger.debug(
                            " >>> (updated) typecast     => %s", configuration.typecast
                        )

                    # logger.debug(" >>> found base (%s) that is an instance of EnumerationMetaClass and a subclass of Enumeration" % (base))

                    if not (base is Enumeration or Enumeration in base.__bases__):
                        _enumerations = base._enumerations

                    logger.debug("  >>> enumerations => %s" % (base._enumerations))

                    for attribute, enumeration in base._enumerations.items():
                        logger.debug(
                            " >>> found enumeration: %s => %s"
                            % (attribute, enumeration)
                        )

                        enumerations[attribute] = enumeration

                        names.append(enumeration.name)

                        values.append(enumeration.value)

        # Set sensible defaults for any configuration options that have not yet been set
        # these defaults are only applied for options that have not yet been set
        configuration.defaults(
            unique=True,
            aliased=False,
            backfill=False,
            overwritable=False,
            subclassable=True,
            extensible=True,
            removable=False,
            raises=False,
            flags=False,
            start=1,
            steps=1,
            times=None,
            typecast=True,
        )

        logger.debug(" >>> (after defaults) unique       => %s", configuration.unique)
        logger.debug(" >>> (after defaults) aliased      => %s", configuration.aliased)
        logger.debug(" >>> (after defaults) backfill     => %s", configuration.backfill)
        logger.debug(
            " >>> (after defaults) overwritable => %s", configuration.overwritable
        )
        logger.debug(
            " >>> (after defaults) subclassable => %s", configuration.subclassable
        )
        logger.debug(" >>> (after defaults) extensible => %s", configuration.extensible)
        logger.debug(
            " >>> (after defaults) removable    => %s", configuration.removable
        )
        logger.debug(" >>> (after defaults) raises       => %s", configuration.raises)
        logger.debug(" >>> (after defaults) flags        => %s", configuration.flags)
        logger.debug(" >>> (after defaults) start        => %s", configuration.start)
        logger.debug(" >>> (after defaults) steps        => %s", configuration.steps)
        logger.debug(" >>> (after defaults) times        => %s", configuration.times)
        logger.debug(" >>> (after defaults) typecast     => %s", configuration.typecast)

        # Iterate over the class attributes, looking for any enumeration options
        for index, (attribute, value) in enumerate(
            attributes.items(), start=configuration.start
        ):
            logger.debug(
                " >>> [%d] attribute => %s, value => %s (%s)"
                % (index, attribute, value, type(value))
            )

            if isinstance(value, auto):
                annotations[attribute] = value
            elif isinstance(value, anno):
                annotations[attribute] = value
                value = value.unwrap()  # unwrap the annotated value

            if attribute.startswith("_") or attribute in cls._special:
                continue
            elif attribute in names:
                raise EnumerationNonUniqueError(
                    "The enumeration option, '%s', has a name that duplicates the name of an existing enumeration option, however all enumeration options must have unique names; please ensure all option names are unique!"
                    % (attribute)
                )
            elif callable(value) and not isinstance(value, type):
                continue
            elif isinstance(value, classmethod):
                continue
            elif isinstance(value, property):
                continue
            elif configuration.unique is True and value in values:
                if configuration.aliased is True:
                    logger.debug(
                        " >>> attribute (alias) => %s, value => %s (%s)"
                        % (attribute, value, type(value))
                    )
                else:
                    raise EnumerationNonUniqueError(
                        "The enumeration option, '%s', has a non-unique value, %r, however, unless either the keyword argument 'unique=False' or 'aliased=True' are passed during class construction, all enumeration options must have unique values; existing values: %s!"
                        % (attribute, value, values)
                    )
            else:
                logger.debug(
                    " >>> attribute (option) => %s, value => %s (%s)"
                    % (attribute, value, type(value))
                )

            enumerations[attribute] = value

            names.append(attribute)

            if not value in values:
                values.append(value)

        # If an attribute was found to be an enumeration option, remove it from the list
        # of class attributes so during class creation it does not become an attribute:
        for attribute in enumerations.keys():
            if attribute in attributes:
                del attributes[attribute]

        logger.debug(
            "[EnumerationMetaClass] %s.__new__() >>> enumerations => %s",
            name,
            list(enumerations.keys()),
        )

        attributes["enumerations"] = enumerations

        if isinstance(_enumerations, dict):
            attributes["base_enumerations"] = _enumerations

        attributes["annotations"] = annotations

        # If the new enumeration class is not subclassing an existing enumeration class
        if configuration.typecast is True and (
            (baseclass is None) or (baseclass is Enumeration)
        ):
            baseclass = Enumeration

            # Determine the type(s) of the provided enumeration option values
            types: set[type] = set([type(value) for value in enumerations.values()])

            logger.debug(" >>> types => %s" % (types))

            # If the enumeration option values have a single data type, use the relevant
            # typed Enumeration superclass as the base for the new enumeration class
            if len(types) == 1 and isinstance(typed := types.pop(), type):
                if typed is str:
                    baseclass = EnumerationString
                elif typed is int:
                    baseclass = EnumerationInteger
                elif typed is auto:
                    baseclass = EnumerationInteger
                elif typed is float:
                    baseclass = EnumerationFloat
                elif typed is complex:
                    baseclass = EnumerationComplex
                elif typed is bytes:
                    baseclass = EnumerationBytes
                elif typed is tuple:
                    baseclass = EnumerationTuple
                elif typed is set:
                    baseclass = EnumerationSet
                elif typed is list:
                    baseclass = EnumerationList
                elif typed is dict:
                    baseclass = EnumerationDictionary
        elif baseclass is None:
            baseclass = Enumeration

        if flags is True:
            baseclass = EnumerationFlag

        logger.debug(" >>> baseclass     => %s", baseclass)
        logger.debug(" >>> new enum name => %s", name)
        logger.debug(" >>> bases         => %s", [base for base in bases])
        logger.debug(" >>> attributes    => %s", attributes)
        logger.debug(" " + ">" * 100)

        bases: tuple[type] = tuple(
            [base for base in bases if not issubclass(base, Enumeration)] + [baseclass]
        )

        logger.debug(" >>> bases         => %s", [base for base in bases])

        args: tuple[object] = (name, bases, attributes)

        # Create the new enumeration class instance
        instance = super().__new__(cls, *args, **kwargs)

        logger.debug(" >>> baseclass     => %s", baseclass)
        logger.debug(" >>> instance      => %s", instance)

        logger.debug(" >>> unique        => %s", configuration.unique)
        logger.debug(" >>> aliased       => %s", configuration.aliased)
        logger.debug(" >>> backfill      => %s", configuration.backfill)
        logger.debug(" >>> overwritable  => %s", configuration.overwritable)
        logger.debug(" >>> subclassable  => %s", configuration.subclassable)
        logger.debug(" >>> extensible    => %s", configuration.extensible)
        logger.debug(" >>> removable     => %s", configuration.removable)
        logger.debug(" >>> raises        => %s", configuration.raises)
        logger.debug(" >>> flags         => %s", configuration.flags)
        logger.debug(" >>> start         => %s", configuration.start)
        logger.debug(" >>> steps         => %s", configuration.steps)
        logger.debug(" >>> times         => %s", configuration.times)
        logger.debug(" >>> typecast      => %s", configuration.typecast)

        # Store the enumeration class configuration options for future reference
        instance._configuration = configuration

        return instance

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        (name, bases, attributes) = args

        logger.debug(
            "[EnumerationMetaClass] %s.__init__(args: %s, kwargs: %s) => name => %s => bases => %s",
            self.__name__,
            args,
            kwargs,
            name,
            bases,
        )

        if isinstance(base_enumerations := attributes.get("base_enumerations"), dict):
            if (
                self._configuration.backfill is True
                and self._configuration.extensible is True
            ):
                self._enumerations: dict[str, Enumeration] = base_enumerations
            else:
                self._enumerations: dict[str, Enumeration] = {}

                for enumeration_name, enumeration in base_enumerations.items():
                    self._enumerations[enumeration_name] = enumeration
        else:
            self._enumerations: dict[str, Enumeration] = {}

        logger.debug(
            " >>> id(%s._enumerations) => %s => %s",
            name,
            id(self._enumerations),
            self._enumerations,
        )

        logger.debug("+" * 100)

        if isinstance(enumerations := attributes.get("enumerations"), dict):
            annotations: dict[str, anno] = attributes.get("annotations") or {}

            for attribute, value in enumerations.items():
                if attribute in self._enumerations:
                    continue

                if isinstance(value, Enumeration):
                    self._enumerations[attribute] = enum = value
                else:
                    existing: Enumeration = None

                    if self.configuration.aliased is True:
                        logger.debug(
                            " >>> aliased is enabled, looking for alias for: %s<%s>",
                            attribute,
                            value,
                        )

                        for enumeration in self._enumerations.values():
                            logger.debug(" >>>> checking: %s", enumeration)

                            if enumeration.value == value:
                                existing = enumeration
                                logger.debug(
                                    " >>>> matched: %s (%s)",
                                    enumeration,
                                    type(existing),
                                )
                                break
                        else:
                            logger.debug(" >>>> no match found")

                    if isinstance(existing, Enumeration):
                        self._enumerations[attribute] = enum = existing
                    else:
                        self._enumerations[attribute] = enum = self(
                            enumeration=self,
                            name=attribute,
                            value=value,
                            annotations=annotations.get(attribute),
                        )

                logger.debug(
                    " => %s => %s => %s (%s)" % (attribute, value, enum, type(enum))
                )

        logger.debug(
            " => self._enumerations(%s) keys => %s",
            id(self._enumeration),
            [key for key in self._enumerations],
        )

        logger.debug("+" * 100)

    def __getattr__(self, name: str) -> object:
        # logger.debug("%s.__getattr__(name: %s)", self.__class__.__name__, name)

        if name.startswith("_") or name in self._special:
            return object.__getattribute__(self, name)
        elif self._enumerations and name in self._enumerations:
            return self._enumerations[name]
        else:
            # EnumerationOptionError subclasses AttributeError so we adhere to convention
            raise EnumerationOptionError(
                "The '%s' enumeration class, has no '%s' enumeration option nor annotation property!"
                % (self.__name__, name)
            )

    def __dir__(self) -> list[str]:
        members: set[str] = set()

        for member in object.__dir__(self):
            if member.startswith("_") or member in self._special:
                members.add(member)

        for name, enumeration in self._enumerations.items():
            members.add(name)

        for member in vars(self):
            members.add(member)

        return list(members)

    def __contains__(self, other: Enumeration | object) -> bool:
        logger.debug(
            "%s(%s).__contains__(other: %s)", self.__class__.__name__, self, other
        )

        contains: bool = False

        for name, enumeration in self._enumerations.items():
            if isinstance(other, Enumeration):
                if enumeration is other:
                    contains = True
                    break
            elif enumeration.value == other:
                contains = True
                break
            elif isinstance(other, str):
                if name == other:
                    contains = True
                    break

        return contains

    def __getitem__(self, name: str) -> Enumeration | None:
        item: Enumeration = None

        for attribute, enumeration in self._enumerations.items():
            if enumeration.name == name:
                item = enumeration
                break
        else:
            raise EnumerationOptionError(
                "The '%s' enumeration class, has no '%s' enumeration option!"
                % (self.__name__, name)
            )

        return item

    def __len__(self) -> int:
        """The '__len__' method returns the number of options held by the enumeration."""

        return len(self._enumerations)

    def __iter__(self) -> typing.Generator[Enumeration, None, None]:
        """The '__iter__' method yields each of the enumeration options one-by-one."""

        for enumeration in self._enumerations.values():
            yield enumeration

    def __reversed__(self) -> typing.Generator[Enumeration, None, None]:
        """The '__reversed__' method yields each of the enumeration options one-by-one
        in reverse order when compared to the '__iter__' method."""

        for enumeration in reversed(self._enumerations.values()):
            yield enumeration

    @property
    def __options__(self) -> MappingProxyType[str, Enumeration]:
        """The '__options__' property returns a read-only mapping proxy of the options."""

        return MappingProxyType(self._enumerations)

    @property
    def __members__(self) -> MappingProxyType[str, Enumeration]:
        """The '__members__' property returns a read-only mapping proxy of the options,
        and is provided for backwards compatibility with the built-in 'enum' package."""

        return MappingProxyType(self._enumerations)

    @property
    def __aliases__(self) -> MappingProxyType[str, Enumeration]:
        """The '__aliases__' property returns a read-only mapping proxy of the option
        names that are aliases for other options."""

        return MappingProxyType(
            {
                name: option
                for name, option in self.__options__.items()
                if option.name != name
            }
        )

    @property
    def configuration(self) -> EnumerationConfiguration:
        return self._configuration

    @property
    def enumerations(self) -> MappingProxyType[str, Enumeration]:
        logger.debug(
            "[EnumerationMetaClass] %s.enumerations() => %s",
            self.__class__.__name__,
            self._enumerations,
        )

        return MappingProxyType(self._enumerations)

    @property
    def typed(self) -> EnumerationType:
        types: set[EnumerationType | None] = set()

        for name, enumeration in self._enumerations.items():
            if typed := EnumerationType.reconcile(type(enumeration.value)):
                types.add(typed)
            else:
                types.add(None)

            logger.debug(
                "%s.typed() %s => %s -> %s [%d]",
                self.__class__.__name__,
                name,
                enumeration,
                typed,
                len(types),
            )

        return types.pop() if len(types) == 1 else EnumerationType.MIXED

    def names(self) -> list[str]:
        """The 'names' method returns a list of the enumeration option names."""

        logger.debug("%s(%s).names()", self.__class__.__name__, type(self))

        return [name for name in self._enumerations]

    def keys(self) -> list[str]:
        """The 'keys' method is an alias of 'names' method; the both return the same."""

        logger.debug("%s(%s).keys()", self.__class__.__name__, type(self))

        return self.names()

    def values(self) -> list[Enumeration]:
        """The 'values' method returns a list of enumeration option values."""

        logger.debug("%s(%s).values()", self.__class__.__name__, type(self))

        return [enumeration.value for enumeration in self._enumerations.values()]

    def items(self) -> list[tuple[str, Enumeration]]:
        """The 'items' method returns a list of tuples of enumeration option names and values."""

        logger.debug("%s(%s).items()" % (self.__class__.__name__, type(self)))

        return [
            (name, enumeration.value)
            for name, enumeration in self._enumerations.items()
        ]

    @property
    def name(self) -> str:
        """The 'name' property returns the class name of the enumeration class that was
        created by this metaclass."""

        return self._instance.__name__

    def register(self, name: str, value: object) -> Enumeration:
        """The 'register' method supports registering additional enumeration options for
        an existing enumeration class. The method accepts the name of the enumeration
        option and its corresponding value; these are then mapped into a new enumeration
        class instance and added to the list of available enumerations.

        If the specified name is the same as an enumeration option that has already been
        registered, either when the enumeration class was created or later through other
        calls to the 'register' method then an exception will be raised unless the class
        was constructed using the 'overwritable=True' argument which allows for existing
        enumeration options to be replaced by a new option stored with the same name. It
        should also be noted that when an enumeration option is replaced that it will
        have a new identity, as the class holding the option is replaced, so comparisons
        using 'is' will not compare between the old and the new, but access will remain
        the same using the <class-name>.<enumeration-option-name> access pattern and so
        comparisons made after the replacement when both instances are the same will be
        treat as equal when using the 'is' operator.

        One should be cautious using the 'overwritable' argument as depending on where
        and how the replacement of an existing enumeration option with a new replacement
        is used, it could cause unexpected results elsewhere in the program. As such the
        overwriting of existing options is prevented by default."""

        logger.debug(
            "[EnumerationMetaClass] %s.register(name: %s, value: %s)",
            self.__name__,
            name,
            value,
        )

        if self.configuration.extensible is False:
            raise EnumerationExtensibilityError(
                "The '%s' enumeration class has been configured to prevent extensibility, so cannot be extended with new options either through registration or subclassing, so the '%s' option cannot be registered!"
                % (self.__name__, name)
            )

        if self.configuration.overwritable is False and name in self._enumerations:
            raise EnumerationNonUniqueError(
                "The '%s' enumeration class already has an option named '%s', so a new option with the same name cannot be created unless the 'overwritable=True' argument is passed during class construction!"
                % (self.__name__, name)
            )

        self._enumerations[name] = enumeration = self(
            enumeration=self,
            name=name,
            value=value,
        )

        return enumeration

    def unregister(self, name: str):
        """The 'unregister' method supports unregistering existing enumeration options
        from an enumeration class, if the 'removable=True' argument was specified when
        the enumeration class was created.

        Removal of existing enumeration options should be used cautiously and only for
        enumeration options that will not be referenced or used during the remainder of
        a program's runtime, otherwise references to removed enumerations could result
        in EnumerationError exceptions being raised."""

        logger.debug(
            "[EnumerationMetaClass] %s.unregister(name: %s)",
            self.__class__.__name__,
            name,
        )

        if self.configuration.removable is False:
            raise EnumerationError(
                "The '%s' enumeration class by default does not support unregistering options, unless the 'removable=True' argument is passed during class construction!"
                % (self.__name__)
            )

        if name in self._enumerations:
            del self._enumerations[name]

    def reconcile(
        self,
        value: Enumeration | object = None,
        name: str = None,
        caselessly: bool = False,
    ) -> Enumeration | None:
        """The 'reconcile' method can be used to reconcile Enumeration type, enumeration
        values, or enumeration names to their matching Enumeration type instances. If a
        match is found the Enumeration type instance will be returned otherwise None will
        be returned, unless the class is configured to raise an error for mismatches."""

        if name is None and value is None:
            raise ValueError(
                "Either the 'value' or 'name' argument must be specified when calling the 'reconcile' function!"
            )

        if not value is None and not isinstance(value, (Enumeration, object)):
            raise TypeError(
                "The 'value' argument must reference an Enumeration type or have an enumeration value!"
            )

        if not name is None and not isinstance(name, str):
            raise TypeError("The 'name' argument must have a string value!")

        reconciled: Enumeration = None

        for attribute, enumeration in self._enumerations.items():
            if isinstance(value, Enumeration):
                if enumeration is value:
                    reconciled = enumeration
                    break
            elif isinstance(name, str) and (
                (enumeration.name == name)
                or (caselessly and (enumeration.name.casefold() == name.casefold()))
            ):
                reconciled = enumeration
                break
            elif isinstance(value, str) and (
                (enumeration.name == value)
                or (caselessly and (enumeration.name.casefold() == value.casefold()))
            ):
                reconciled = enumeration
                break
            elif enumeration.value == value:
                reconciled = enumeration
                break

        if reconciled is None and self.configuration.raises is True:
            if not name is None:
                raise EnumerationOptionError(
                    "Unable to reconcile %s option with name: %s!"
                    % (
                        self.__class__.__name__,
                        name,
                    )
                )
            elif not value is None:
                raise EnumerationOptionError(
                    "Unable to reconcile %s option with value: %s!"
                    % (
                        self.__class__.__name__,
                        value,
                    )
                )

        # When an enumeration option is reconciled, it may be defined in another class
        # but have been accessed through a subclass; in order for attribute lookups to
        # work within the subclass, we need to provide the current lookup context to the
        # reconciled enumeration option, so that any attribute access on this object can
        # perform their lookup in the correct part of the class hierarchy
        if isinstance(reconciled, Enumeration):
            reconciled._context = self

        return reconciled

    def validate(self, value: Enumeration | object = None, name: str = None) -> bool:
        """The 'validate' method can be used to verify if the Enumeration class contains
        the specified enumeration or enumeration value. The method returns True if a
        match is found for the enumeration value or name, otherwise it returns False."""

        return not self.reconcile(value=value, name=name) is None

    def options(self) -> MappingProxyType[str, Enumeration]:
        """The 'options' method returns a read-only mapping proxy of the options."""

        return MappingProxyType(self._enumerations)


class Enumeration(metaclass=EnumerationMetaClass):
    """The Enumeration class is the subclass of all enumerations and their subtypes."""

    _metaclass: EnumerationMetaClass = None
    _context: EnumerationMetaClass = None
    _enumeration: Enumeration = None
    _enumerations: dict[str, Enumeration] = None
    _annotations: anno = None
    _name: str = None
    _value: object = None
    _aliased: Enumeration = None

    # NOTE: This method is only called if the class is instantiated via class(..) syntax
    def __new__(
        cls,
        *args,
        enumeration: Enumeration = None,
        name: str = None,
        value: object = None,
        aliased: Enumeration = None,
        annotations: anno = None,
        **kwargs,
    ) -> Enumeration | None:
        # Supports reconciling enumeration options via their name/value via __new__ call
        if value is None and len(args) >= 1:
            value = args[0]

        logger.debug(
            "[Enumeration] %s.__new__(args: %s, enumeration: %s, name: %s, value: %s, aliased: %s, annotations: %s, kwargs: %s)",
            cls.__name__,
            args,
            enumeration,
            name,
            value,
            aliased,
            annotations,
            kwargs,
        )

        if enumeration is None and name is None and value is None:
            raise NotImplementedError
        elif enumeration is None and ((name is not None) or (value is not None)):
            if isinstance(
                reconciled := cls.reconcile(value=value, name=name), Enumeration
            ):
                return reconciled
            else:
                logger.debug(
                    "Unable to reconcile enumeration option <Enumeration(name=%s, value=%s)>",
                    name,
                    value,
                )
                return None
        else:
            return super().__new__(cls)

    # NOTE: This method is only called if the class is instantiated via class(..) syntax
    def __init__(
        self,
        *args,
        enumeration: Enumeration = None,
        name: str = None,
        value: object = None,
        aliased: Enumeration = None,
        annotations: anno = None,
        **kwargs,
    ) -> None:
        logger.debug(
            "[Enumeration] %s.__init__(args: %s, enumeration: %s, name: %s, value: %s, aliased: %s, annotations: %s, kwargs: %s)",
            self.__class__.__name__,
            args,
            enumeration,
            name,
            value,
            aliased,
            annotations,
            kwargs,
        )

        if enumeration is None:
            pass
        elif issubclass(enumeration, Enumeration):
            self._enumeration = enumeration

        if name is None:
            pass
        elif isinstance(name, str):
            self._name = name
        else:
            raise TypeError("The 'name' argument must have a string value!")

        if value is None:
            pass
        else:
            if isinstance(value, Enumeration):
                raise TypeError(
                    "The 'value' argument cannot be assigned to another Enumeration!"
                )
            self._value = value

        if aliased is None:
            pass
        elif isinstance(aliased, Enumeration):
            self._aliased = aliased
        else:
            raise TypeError(
                "The 'aliased' argument, if specified, must reference an Enumeration class instance!"
            )

        if annotations is None:
            self._annotations = anno(value=self.value)
        elif isinstance(annotations, anno):
            self._annotations = annotations
        else:
            raise TypeError(
                "The 'annotations' argument, if specified, must reference an anno class instance!"
            )

    # NOTE: This method is only called if the instance is called via instance(..) syntax
    def __call__(self, *args, **kwargs) -> Enumeration | None:
        logger.debug(
            "%s.__call__(args: %s, kwargs: %s)",
            self.__class__.__name__,
            args,
            kwargs,
        )

        return self.reconcile(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}.{self._name}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}.{self._name}: {self._value}>"

    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other: Enumeration | object) -> bool:
        logger.debug("%s(%s).__eq__(other: %s)", self.__class__.__name__, self, other)

        equals: bool = False

        if isinstance(other, Enumeration):
            equals = self is other
        elif self.name == other:
            equals = True
        elif self.value == other:
            equals = True

        return equals

    def __getattr__(self, name) -> object:
        """The '__getattr__' method provides support for accessing attribute values that
        have been assigned to the current enumeration option. If a matching attribute can
        be found, its value will be returned, otherwise an exception will be raised."""

        logger.debug("%s.__getattr__(name: %s)", self.__class__.__name__, name)

        if name.startswith("_") or name in self.__class__._special or name in dir(self):
            return object.__getattribute__(self, name)
        elif self._enumerations and name in self._enumerations:
            return self._enumerations[name]
        elif self._context and name in dir(self._context):
            # Handle class methods, instance methods and properties here; because we are
            # performing some special handling for enumerations, we need to reintroduce
            # the necessary context to the methods here via the descriptor protocol so
            # the methods and properties work as expected:
            if callable(attribute := object.__getattribute__(self._context, name)):
                return attribute.__get__(self)
            elif isinstance(attribute, property):
                return attribute.__get__(self)
            elif isinstance(attribute, classmethod):
                return attribute.__get__(self)
            else:
                return attribute
        elif self._annotations and name in self._annotations:
            return self._annotations[name]
        else:
            # EnumerationOptionError subclasses AttributeError so we adhere to convention
            raise EnumerationOptionError(
                "The '%s' enumeration class, has no '%s' enumeration option nor annotation property!"
                % (self.__class__.__name__, name)
            )

    def get(self, name: str, default: object = None) -> object | None:
        """The 'get' method provides support for accessing annotation values that may
        have been assigned to the current enumeration option. If a matching annotation
        can be found, its value will be returned, otherwise the default value will be
        returned, which defaults to None, but may be specified as any value."""

        if name in self._annotations:
            return self._annotations[name]
        else:
            return default

    @property
    def enumeration(self) -> Enumeration:
        return self._enumeration

    # @property
    # def enumerations(self) -> MappingProxyType[str, Enumeration]:
    #     return self._enumeration._enumerations

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> object:
        return self._value

    @property
    def annotations(self) -> anno:
        return self._annotations

    @property
    def aliased(self) -> bool:
        logger.debug(
            "%s.aliased() >>> id(%s) => %s (%s)",
            self.__class__.__name__,
            self,
            id(self._enumerations),
            type(self._enumerations),
        )

        for name, enumeration in self._enumerations.items():
            logger.debug(" >>> checking for alias: %s => %s", name, enumeration)

            if isinstance(enumeration, Enumeration):
                if self is enumeration and enumeration.name != name:
                    return True

        return False

    @property
    def aliases(self) -> list[Enumeration]:
        logger.debug(
            "%s.aliases() >>> id(%s) => %s (%s)",
            self.__class__.__name__,
            self,
            id(self._enumerations),
            type(self._enumerations),
        )

        aliases: list[Enumeration] = []

        for name, enumeration in self._enumerations.items():
            logger.debug(" >>> checking for alias: %s => %s", name, enumeration)

            if isinstance(enumeration, Enumeration):
                if self is enumeration and enumeration.name != name:
                    aliases.append(enumeration)

        return aliases

    @property
    def named(self) -> list[str]:
        logger.debug(
            "%s.names() >>> id(%s) => %s (%s)",
            self.__class__.__name__,
            self,
            id(self._enumerations),
            type(self._enumerations),
        )

        names: list[Enumeration] = [self.name]

        for name, enumeration in self._enumerations.items():
            logger.debug(" >>> checking for alias: %s => %s", name, enumeration)

            if isinstance(enumeration, Enumeration):
                if self is enumeration and enumeration.name != name:
                    if not name in names:
                        names.append(name)

        return names


class EnumerationType(Enumeration, typecast=False):
    """The EnumerationType class represents the type of value held by an enumeration."""

    MIXED = None
    INTEGER = int
    FLOAT = float
    COMPLEX = complex
    STRING = str
    BYTES = bytes
    # BOOLEAN = bool
    OBJECT = object
    TUPLE = tuple
    SET = set
    LIST = list
    DICTIONARY = dict


class EnumerationInteger(int, Enumeration):
    """An Enumeration subclass where all values are integer values."""

    def __new__(cls, *args, **kwargs):
        logger.debug(
            "EnumerationInteger.__new__(cls: %s, args: %s, kwargs: %s)",
            cls,
            args,
            kwargs,
        )

        if not isinstance(value := kwargs.get("value"), int):
            raise TypeError("The provided value must be an integer!")

        return super().__new__(cls, value)

    def __str__(self) -> str:
        return Enumeration.__str__(self)

    def __repr__(self) -> str:
        return Enumeration.__repr__(self)

    def __hash__(self) -> id:
        return super().__hash__()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, (int, self.__class__)):
            return super().__eq__(other)
        else:
            return Enumeration.__eq__(self, other)


class EnumerationFloat(float, Enumeration):
    """An Enumeration subclass where all values are float values."""

    def __new__(cls, *args, **kwargs):
        logger.debug(
            "EnumerationFloat.__new__(cls: %s, args: %s, kwargs: %s)", cls, args, kwargs
        )

        if not isinstance(value := kwargs.get("value"), float):
            raise TypeError("The provided value must be a float!")

        return super().__new__(cls, value)

    def __str__(self) -> str:
        return Enumeration.__str__(self)

    def __repr__(self) -> str:
        return Enumeration.__repr__(self)


class EnumerationComplex(complex, Enumeration):
    """An Enumeration subclass where all values are complex values."""

    def __new__(cls, *args, **kwargs):
        logger.debug(
            "EnumerationComplex.__new__(cls: %s, args: %s, kwargs: %s)",
            cls,
            args,
            kwargs,
        )

        if not isinstance(value := kwargs.get("value"), complex):
            raise TypeError("The provided value must be a complex!")

        return super().__new__(cls, value)

    def __str__(self) -> str:
        return Enumeration.__str__(self)

    def __repr__(self) -> str:
        return Enumeration.__repr__(self)

    def __hash__(self) -> id:
        return super().__hash__()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, (float, self.__class__)):
            return super().__eq__(other)
        else:
            return Enumeration.__eq__(self, other)


class EnumerationString(str, Enumeration):
    """An Enumeration subclass where all values are string values."""

    def __new__(cls, *args, **kwargs):
        logger.debug(
            "EnumerationString.__new__(cls: %s, args: %s, kwargs: %s)",
            cls,
            args,
            kwargs,
        )

        if not isinstance(value := kwargs.get("value"), str):
            raise TypeError("The provided value must be a string!")

        return super().__new__(cls, value)

    def __str__(self) -> str:
        return Enumeration.__str__(self)

    def __repr__(self) -> str:
        return Enumeration.__repr__(self)

    def __hash__(self) -> id:
        return super().__hash__()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, (str, self.__class__)):
            return super().__eq__(other)
        else:
            return Enumeration.__eq__(self, other)


class EnumerationBytes(bytes, Enumeration):
    """An Enumeration subclass where all values are bytes values."""

    def __new__(cls, *args, **kwargs):
        logger.debug(
            "EnumerationBytes.__new__(cls: %s, args: %s, kwargs: %s)", cls, args, kwargs
        )

        if not isinstance(value := kwargs.get("value"), bytes):
            raise TypeError("The provided value must be a bytes!")

        return super().__new__(cls, value)

    def __str__(self) -> str:
        return Enumeration.__str__(self)

    def __repr__(self) -> str:
        return Enumeration.__repr__(self)

    def __hash__(self) -> id:
        return super().__hash__()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, (bytes, self.__class__)):
            return super().__eq__(other)
        else:
            return Enumeration.__eq__(self, other)


class EnumerationTuple(tuple, Enumeration):
    """An Enumeration subclass where all values are tuple values."""

    def __new__(cls, *args, **kwargs):
        logger.debug(
            "EnumerationTuple.__new__(cls: %s, args: %s, kwargs: %s)", cls, args, kwargs
        )

        if not isinstance(value := kwargs.get("value"), tuple):
            raise TypeError("The provided value must be a tuple!")

        return super().__new__(cls, value)

    def __str__(self) -> str:
        return Enumeration.__str__(self)

    def __repr__(self) -> str:
        return Enumeration.__repr__(self)

    def __hash__(self) -> id:
        return super().__hash__()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, (tuple, self.__class__)):
            return super().__eq__(other)
        else:
            return Enumeration.__eq__(self, other)


class EnumerationSet(set, Enumeration):
    """An Enumeration subclass where all values are set values."""

    def __new__(cls, *args, **kwargs):
        logger.debug(
            "EnumerationSet.__new__(cls: %s, args: %s, kwargs: %s)", cls, args, kwargs
        )

        if not isinstance(value := kwargs.get("value"), set):
            raise TypeError("The provided value must be a set!")

        return super().__new__(cls, value)

    def __str__(self) -> str:
        return Enumeration.__str__(self)

    def __repr__(self) -> str:
        return Enumeration.__repr__(self)

    def __hash__(self) -> id:
        return super().__hash__()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, (set, self.__class__)):
            return super().__eq__(other)
        else:
            return Enumeration.__eq__(self, other)


class EnumerationList(list, Enumeration):
    """An Enumeration subclass where all values are list values."""

    def __new__(cls, *args, **kwargs):
        logger.debug(
            "EnumerationList.__new__(cls: %s, args: %s, kwargs: %s)", cls, args, kwargs
        )

        if not isinstance(value := kwargs.get("value"), list):
            raise TypeError("The provided value must be a list!")

        return super().__new__(cls, value)

    def __str__(self) -> str:
        return Enumeration.__str__(self)

    def __repr__(self) -> str:
        return Enumeration.__repr__(self)

    def __hash__(self) -> id:
        return super().__hash__()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, (list, self.__class__)):
            return super().__eq__(other)
        else:
            return Enumeration.__eq__(self, other)


class EnumerationDictionary(dict, Enumeration):
    """An Enumeration subclass where all values are dictionary values."""

    def __new__(cls, *args, **kwargs):
        logger.debug(
            "EnumerationDictionary.__new__(cls: %s, args: %s, kwargs: %s)",
            cls,
            args,
            kwargs,
        )

        if not isinstance(value := kwargs.get("value"), dict):
            raise TypeError("The provided value must be a dictionary!")

        return super().__new__(cls, value)

    def __str__(self) -> str:
        return Enumeration.__str__(self)

    def __repr__(self) -> str:
        return Enumeration.__repr__(self)

    def __hash__(self) -> id:
        return super().__hash__()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, (dict, self.__class__)):
            return super().__eq__(other)
        else:
            return Enumeration.__eq__(self, other)


class EnumerationFlag(int, Enumeration):
    """An Enumeration subclass where all values are integer values to the power of 2."""

    _flags: set[EnumerationFlag] = None

    def __new__(
        cls,
        *args,
        flags: list[EnumerationFlag] = None,
        name: str = None,
        value: object = None,
        unique: bool = True,
        **kwargs,
    ):
        logger.debug(
            "%s.__new__(cls: %s, args: %s, flags: %s, name: %s, value: %s, unique: %s, kwargs: %s)",
            cls.__name__,
            cls,
            args,
            flags,
            name,
            value,
            unique,
            kwargs,
        )

        if flags is None:
            if isinstance(name, str) and isinstance(value, int):
                if isinstance(reconciled := cls.reconcile(name=name, value=value), cls):
                    return reconciled
        elif not isinstance(flags, list):
            raise TypeError(
                "The 'flags' argument must reference a list of '%s' instances!"
                % (cls.__name__)
            )
        else:
            for index, flag in enumerate(flags):
                if not isinstance(flag, cls):
                    raise TypeError(
                        "The 'flags' argument must reference a list of '%s' instances; the item at index %d is not a '%s' instance!"
                        % (cls.__name__, index, cls.__name__)
                    )

            if name is None:
                name = "|".join([flag.name for flag in flags])

            if value is None:
                value: int = 0

                for flag in flags:
                    # Use the bitwise 'or' operation to combine the flag bit masks
                    value = value | flag.value

        if value is None:
            if flags is None:
                raise ValueError(
                    "The 'flags' argument must be provided if the 'value' argument is not!"
                )
        elif isinstance(value, int):
            if value == 0 or (value > 0 and (value & (value - 1)) == 0):
                pass
            elif flags is None:
                raise ValueError(
                    "The 'value' argument, %r, is invalid; it must be have a positive integer value that is a power of two!"
                    % (value)
                )
        else:
            raise TypeError(
                "The 'value' argument, if specified, must have a positive integer value!"
            )

        if not unique is True:
            raise ValueError(
                "The 'unique' argument, if specified, must have a boolean 'True' value for all subclasses of the '%s' class!"
                % (cls.__name__)
            )

        return super().__new__(cls, value)

    def __init__(
        self,
        *args,
        flags: list[EnumerationFlag] = None,
        name: str = None,
        value: object = None,
        unique: bool = True,
        **kwargs,
    ):
        logger.debug(
            "%s.__init__(self: %s, args: %s, flags: %s, name: %s, value: %s, unique: %s, kwargs: %s)",
            self.__class__.__name__,
            self,
            args,
            flags,
            name,
            value,
            unique,
            kwargs,
        )

        if flags is None:
            pass
        elif not isinstance(flags, list):
            raise TypeError(
                "The 'flags' argument must reference a list of '%s' instances!"
                % (cls.__name__)
            )
        else:
            for index, flag in enumerate(flags):
                if not isinstance(flag, self.__class__):
                    raise TypeError(
                        "The 'flags' argument must reference a list of '%s' instances; the item at index %d is not a '%s' instance!"
                        % (self.__class__.__name__, index, self.__class__.__name__)
                    )

            if name is None:
                name = "|".join([flag.name for flag in flags])

            if value is None:
                value = 0

                for flag in flags:
                    value = (
                        value | flag.value
                    )  # use the bitwise 'or' operation to combine the values

        super().__init__(
            *args,
            name=name,
            value=value,
            unique=unique,
            **kwargs,
        )

    def __str__(self) -> str:
        return Enumeration.__str__(self)

    def __repr__(self) -> str:
        return Enumeration.__repr__(self)

    def __hash__(self) -> id:
        return super().__hash__()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, (int, self.__class__)):
            return super().__eq__(other)
        else:
            return Enumeration.__eq__(self, other)

    def __or__(self, other: EnumerationFlag):  # called for: "a | b" (bitwise or)
        """Support performing a bitwise or between the current EnumerationFlag
        instance's bitmask and the 'other' provided EnumerationFlag's bitmask;
        the return value from the operation is a new EnumerationFlag instance
        that represents the appropriately combined EnumerationFlags bitmasks."""

        logger.debug(
            "%s.__or__(self: %s, other: %s)", self.__class__.__name__, self, other
        )

        if not isinstance(other, self.__class__):
            raise TypeError(
                "The 'other' argument must be an instance of the '%s' class!"
                % (self.__class__.__name__)
            )

        flags = self.flags()

        if not other in flags:
            flags.append(other)

        logger.debug(" >>> flags => %s", flags)

        return self.__class__(
            enumeration=self.__class__,
            flags=sorted(flags),
        )

    def __xor__(self, other: EnumerationFlag):  # called for: "a ^ b" (bitwise xor)
        """Support performing a bitwise xor between the current EnumerationFlag
        instance's bitmask and the 'other' provided EnumerationFlag's bitmask;
        the return value from the operation is a new EnumerationFlag instance
        that represents the appropriately combined EnumerationFlags bitmasks."""

        logger.debug(
            "%s.__xor__(self: %s, other: %s)", self.__class__.__name__, self, other
        )

        if not isinstance(other, self.__class__):
            raise TypeError(
                "The 'other' argument must be an instance of the '%s' class!"
                % (self.__class__.__name__)
            )

        flags = self.flags()

        if other in flags:
            flags.remove(other)

        logger.debug(" >>> flags => %s", flags)

        return self.__class__(
            enumeration=self.__class__,
            flags=sorted(flags),
        )

    def __and__(self, other: EnumerationFlag):  # called for: "a & b" (bitwise add)
        """Support performing a bitwise and between the current EnumerationFlag
        instance's bitmask and the 'other' provided EnumerationFlag's bitmask;
        if the bitwise and finds an overlap, the return value from the operation
        is the 'other' provided EnumerationFlag. Otherwise the return value will
        be an 'empty' instance of the EnumerationFlag that doesn't match any."""

        logger.debug(
            "%s.__and__(self: %s, other: %s)", self.__class__.__name__, self, other
        )

        if not isinstance(other, self.__class__):
            raise TypeError(
                "The 'other' argument must be an instance of the '%s' class!"
                % (self.__class__.__name__)
            )

        flags = self.flags()

        if other in flags:
            return other
        else:
            # TODO: Return a singleton instance of the 'NONE' option; this may already
            # happen based on the superclass' behaviour but need to confirm this
            return self.__class__(
                enumeration=self.__class__,
                name="NONE",
                value=0,
            )

    def __invert__(self):  # called for: "~a" (bitwise inversion)
        """Support inverting the current EnumerationFlag instance's bitmask."""

        logger.debug("%s.__invert__(self: %s)", self.__class__.__name__, self)

        # Obtain a list of flags that is exclusive of the current flag
        flags = self.flags(exclusive=True)

        logger.debug(" >>> flags => %s", flags)

        return self.__class__(
            enumeration=self.__class__,
            flags=sorted(flags),
        )

    def __contains__(self, other: EnumerationFlag) -> bool:  # called for: "a in b"
        """Support determining if the current EnumerationFlag instance's bitmask
        overlaps with the 'other' provided EnumerationFlag instance's bitmask."""

        if not isinstance(other, self.__class__):
            raise TypeError(
                "The 'other' argument must be an instance of the '%s' class!"
                % (self.__class__.__name__)
            )

        return (self.value & other.value) == other.value

    def flags(self, exclusive: bool = False) -> list[EnumerationFlag]:
        """Return a list of EnumerationFlag instances matching the current
        EnumerationFlag's bitmask. By default the method will return all the
        flags which match the current bitmask, or when the 'exclusive' argument
        is set to 'True', the method will return all the flags which do not
        match the current EnumerationFlag's bitmask (an inversion)."""

        if not isinstance(exclusive, bool):
            raise TypeError("The 'exclusive' argument must have a boolean value!")

        flags: list[EnumerationFlag] = []

        for name, enumeration in self.enumeration._enumerations.items():
            logger.debug(
                "%s.flags() name => %s, enumeration => %s (%s)",
                self.__class__.__name__,
                name,
                enumeration,
                type(enumeration),
            )

            if ((self.value & enumeration.value) == enumeration.value) is not exclusive:
                flags.append(enumeration)

        return flags
