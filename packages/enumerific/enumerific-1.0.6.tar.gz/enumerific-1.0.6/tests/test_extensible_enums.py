import pytest
import logging
import types
import colorsys

import enumerific

from enumerific import (
    Enumeration,
    EnumerationType,
    EnumerationInteger,
    EnumerationString,
    EnumerationFloat,
    EnumerationComplex,
    EnumerationBytes,
    EnumerationTuple,
    EnumerationSet,
    EnumerationList,
    EnumerationDictionary,
    EnumerationFlag,
    EnumerationSubclassingError,
    EnumerationExtensibilityError,
    auto,
    anno,
)


logger = logging.getLogger(__name__)


def test_extensible_enumeration():
    """Test the creation of an extensible enumeration"""

    # This test enumeration contains options with a mixture of value data types
    class Colors(Enumeration):
        RED = (255, 0, 0)
        GREEN = (0, 255, 0)
        BLUE = (0, 0, 255)
        CLEAR = None

    # Ensure that the Colors class is a subclass of the Enumeration class
    assert issubclass(Colors, Enumeration)

    # As the Colors enumeration class uses a mixture of value data types, the generic
    # Enumeration class was used as its superclass, rather than one of the specialized
    # superclasses that support enumeration subclasses that have values of a single type
    assert not issubclass(Colors, EnumerationInteger)
    assert not issubclass(Colors, EnumerationFloat)
    assert not issubclass(Colors, EnumerationString)
    assert not issubclass(Colors, EnumerationBytes)
    assert not issubclass(Colors, EnumerationTuple)
    assert not issubclass(Colors, EnumerationSet)
    assert not issubclass(Colors, EnumerationList)
    assert not issubclass(Colors, EnumerationDictionary)

    # The .typed property notes what data type or types the enumeration options use
    assert Colors.typed is EnumerationType.MIXED

    # Test .__len__()
    assert len(Colors) == 4

    # Test .keys()
    assert Colors.keys() == ["RED", "GREEN", "BLUE", "CLEAR"]

    # Test .values()
    assert Colors.values() == [(255, 0, 0), (0, 255, 0), (0, 0, 255), None]

    # Test .items()
    assert Colors.items() == [
        ("RED", (255, 0, 0)),
        ("GREEN", (0, 255, 0)),
        ("BLUE", (0, 0, 255)),
        ("CLEAR", None),
    ]

    # Test .__getattr__()
    assert Colors.RED
    assert Colors.GREEN
    assert Colors.BLUE
    assert Colors.CLEAR

    # Test .__eq__()
    assert Colors.RED == (255, 0, 0)
    assert Colors.GREEN == (0, 255, 0)
    assert Colors.BLUE == (0, 0, 255)
    assert Colors.CLEAR == None

    try:
        # Ensure an exception is raised for access to non-existent enumeration options
        assert Colors.GRAY == (146, 146, 146)
    except enumerific.exceptions.EnumerationError as exception:
        assert (
            str(exception)
            == "The 'Colors' enumeration class, has no 'GRAY' enumeration option nor annotation property!"
        )

    # Test .__contains__() for the "RED" option
    assert "RED" in Colors
    assert (255, 0, 0) in Colors
    assert Colors.RED in Colors
    assert not "red" in Colors  # option name matching is case-sensitive

    # Test .__contains__() for the "GREEN" option
    assert "GREEN" in Colors
    assert (0, 255, 0) in Colors
    assert Colors.GREEN in Colors
    assert not "green" in Colors  # option name matching is case-sensitive

    # Test .__contains__() for the "BLUE" option
    assert "BLUE" in Colors
    assert (0, 255, 0) in Colors
    assert Colors.BLUE in Colors
    assert not "blue" in Colors  # option name matching is case-sensitive

    # Test .__contains__() for the non-existent "GRAY" option
    assert not "GRAY" in Colors
    assert not (146, 146, 146) in Colors

    try:
        # Ensure an exception is raised for access to non-existent enumeration options
        assert Colors.GRAY in Colors
    except enumerific.exceptions.EnumerationError as exception:
        assert (
            str(exception)
            == "The 'Colors' enumeration class, has no 'GRAY' enumeration option nor annotation property!"
        )

    # Test types, names and values for the RED option
    assert isinstance(Colors.RED, Enumeration)
    assert Colors.RED == (255, 0, 0)
    assert isinstance(Colors.RED.name, str)
    assert Colors.RED.name == "RED"
    assert isinstance(Colors.RED.value, tuple)
    assert Colors.RED.value == (255, 0, 0)

    # Test types, names and values for the GREEN option
    assert isinstance(Colors.GREEN, Enumeration)
    assert Colors.GREEN == (0, 255, 0)
    assert isinstance(Colors.GREEN.name, str)
    assert Colors.GREEN.name == "GREEN"
    assert isinstance(Colors.GREEN.value, tuple)
    assert Colors.GREEN.value == (0, 255, 0)

    # Test types, names and values for the BLUE option
    assert isinstance(Colors.BLUE, Enumeration)
    assert Colors.BLUE == (0, 0, 255)
    assert isinstance(Colors.BLUE.name, str)
    assert Colors.BLUE.name == "BLUE"
    assert isinstance(Colors.BLUE.value, tuple)
    assert Colors.BLUE.value == (0, 0, 255)

    # Test types, names and values for the CLEAR option
    assert isinstance(Colors.CLEAR, Enumeration)
    assert Colors.CLEAR == None
    assert isinstance(Colors.CLEAR.name, str)
    assert Colors.CLEAR.name == "CLEAR"
    assert Colors.CLEAR.value == None

    # Test .__getitem__()
    assert Colors["RED"] == Colors.RED
    assert Colors["GREEN"] == Colors.GREEN
    assert Colors["BLUE"] == Colors.BLUE
    assert Colors["CLEAR"] == Colors.CLEAR

    try:
        # Ensure an exception is raised for access to non-existent enumeration options
        assert Colors["GRAY"]
    except enumerific.exceptions.EnumerationError as exception:
        assert (
            str(exception)
            == "The 'Colors' enumeration class, has no 'GRAY' enumeration option!"
        )

    # Test .__call__() which reconciles enumeration option names or values to the option
    assert Colors("RED") == Colors.RED
    assert Colors("GREEN") == Colors.GREEN
    assert Colors("BLUE") == Colors.BLUE
    assert Colors("CLEAR") == Colors.CLEAR
    assert Colors("GRAY") == None  # Options that do not match yield None

    # Test the .reconcile() class method
    assert Colors.reconcile("RED") == Colors.RED
    assert Colors.reconcile("GREEN") == Colors.GREEN
    assert Colors.reconcile("BLUE") == Colors.BLUE
    assert Colors.reconcile("CLEAR") == Colors.CLEAR
    assert Colors.reconcile("GRAY") == None

    # Test the .validate() class method
    assert Colors.validate("RED") is True
    assert Colors.validate("GREEN") is True
    assert Colors.validate("BLUE") is True
    assert Colors.validate("CLEAR") is True
    assert Colors.validate("GRAY") is False

    # Test .__str__() instance method
    assert str(Colors.RED) == "Colors.RED"
    assert str(Colors.GREEN) == "Colors.GREEN"
    assert str(Colors.BLUE) == "Colors.BLUE"
    assert str(Colors.CLEAR) == "Colors.CLEAR"

    # Test .__repr__() instance method
    assert repr(Colors.RED) == "<Colors.RED: (255, 0, 0)>"
    assert repr(Colors.GREEN) == "<Colors.GREEN: (0, 255, 0)>"
    assert repr(Colors.BLUE) == "<Colors.BLUE: (0, 0, 255)>"
    assert repr(Colors.CLEAR) == "<Colors.CLEAR: None>"

    # Test .__iter__() instance method
    options: list[Enumeration] = []

    for enumeration in Colors:
        options.append(enumeration)

    assert len(options) == 4
    assert options == [Colors.RED, Colors.GREEN, Colors.BLUE, Colors.CLEAR]

    # Test .__iter__() instance method with reversed()
    options: list[Enumeration] = []

    for enumeration in reversed(Colors):
        options.append(enumeration)

    assert len(options) == 4
    assert options == [Colors.CLEAR, Colors.BLUE, Colors.GREEN, Colors.RED]

    # Test .__iter__() instance method with enumerate()
    options: list[Enumeration] = []

    for index, enumeration in enumerate(Colors):
        options.append(enumeration)

    assert len(options) == 4
    assert options == [Colors.RED, Colors.GREEN, Colors.BLUE, Colors.CLEAR]

    # Test .enumeration instance property
    assert Colors.RED.enumeration == Colors
    assert Colors.GREEN.enumeration == Colors
    assert Colors.BLUE.enumeration == Colors
    assert Colors.CLEAR.enumeration == Colors


def test_extensible_enumeration_integer():
    """Test the creation of an enumeration with exclusively integer values"""

    class TestEnumInteger(Enumeration):
        YES = 1
        NO = 0

    assert issubclass(TestEnumInteger, Enumeration)
    assert issubclass(TestEnumInteger, EnumerationInteger)

    # Test .__len__()
    assert len(TestEnumInteger) == 2

    # Test .keys()
    assert TestEnumInteger.keys() == ["YES", "NO"]

    # Test .values()
    assert TestEnumInteger.values() == [1, 0]

    # Test .items()
    assert TestEnumInteger.items() == [("YES", 1), ("NO", 0)]

    # Test .__getattr__()
    assert TestEnumInteger.YES == 1
    assert TestEnumInteger.NO == 0

    try:
        # Ensure an exception is raised for access to a non-existent enumeration option
        assert TestEnumInteger.MAYBE == 2
    except enumerific.exceptions.EnumerationError as exception:
        assert (
            str(exception)
            == "The 'TestEnumInteger' enumeration class, has no 'MAYBE' enumeration option nor annotation property!"
        )

    # Test .__contains__() for the "NO" option
    assert "NO" in TestEnumInteger
    assert 0 in TestEnumInteger
    assert TestEnumInteger.NO in TestEnumInteger
    assert not "no" in TestEnumInteger  # option name matching is case-sensitive

    # Test .__contains__() for the "YES" option
    assert "YES" in TestEnumInteger
    assert 1 in TestEnumInteger
    assert TestEnumInteger.YES in TestEnumInteger
    assert not "yes" in TestEnumInteger  # option name matching is case-sensitive

    # Test .__contains__() for the non-existent "MAYBE" option
    assert not "MAYBE" in TestEnumInteger
    assert not 2 in TestEnumInteger

    try:
        # Ensure an exception is raised for access to a non-existent enumeration option
        assert TestEnumInteger.MAYBE in TestEnumInteger
    except enumerific.exceptions.EnumerationError as exception:
        assert (
            str(exception)
            == "The 'TestEnumInteger' enumeration class, has no 'MAYBE' enumeration option nor annotation property!"
        )

    # Test types and values for the YES option
    assert isinstance(TestEnumInteger.YES, Enumeration)
    assert isinstance(TestEnumInteger.YES, EnumerationInteger)
    assert isinstance(TestEnumInteger.YES, int)
    assert TestEnumInteger.YES == 1
    assert isinstance(TestEnumInteger.YES.name, str)
    assert TestEnumInteger.YES.name == "YES"
    assert isinstance(TestEnumInteger.YES.value, int)
    assert TestEnumInteger.YES.value == 1

    # Test types and values for the NO option
    assert isinstance(TestEnumInteger.NO, Enumeration)
    assert isinstance(TestEnumInteger.NO, EnumerationInteger)
    assert isinstance(TestEnumInteger.NO, int)
    assert TestEnumInteger.NO == 0
    assert isinstance(TestEnumInteger.NO.value, int)
    assert TestEnumInteger.NO.value == 0
    assert isinstance(TestEnumInteger.NO.name, str)
    assert TestEnumInteger.NO.name == "NO"

    # Test .__getitem__()
    assert TestEnumInteger["YES"] == TestEnumInteger.YES
    assert TestEnumInteger["NO"] == TestEnumInteger.NO

    try:
        # Ensure an exception is raised for access to a non-existent enumeration option
        assert TestEnumInteger["MAYBE"]
    except enumerific.exceptions.EnumerationError as exception:
        assert (
            str(exception)
            == "The 'TestEnumInteger' enumeration class, has no 'MAYBE' enumeration option!"
        )

    # Test .__int__()
    assert int(TestEnumInteger.NO) == 0

    # Test .__str__()
    assert str(TestEnumInteger.NO) == "TestEnumInteger.NO"

    # Test .__repr__()
    assert repr(TestEnumInteger.NO) == "<TestEnumInteger.NO: 0>"

    # Test .__iter__()
    options: list[Enumeration] = []

    for enumeration in TestEnumInteger:
        options.append(enumeration)

    assert len(options) == 2
    assert options == [TestEnumInteger.YES, TestEnumInteger.NO]

    # Test .__iter__() with reversed()
    options: list[Enumeration] = []

    for enumeration in reversed(TestEnumInteger):
        options.append(enumeration)

    assert len(options) == 2
    assert options == [TestEnumInteger.NO, TestEnumInteger.YES]

    # Test .__iter__() with enumerate()
    options: list[Enumeration] = []

    for index, enumeration in enumerate(TestEnumInteger):
        options.append(enumeration)

    assert len(options) == 2
    assert options == [TestEnumInteger.YES, TestEnumInteger.NO]


def test_extensible_enumeration_integer_non_unique():
    """Test enumerations with non-unique option names to ensure that any non-unqiue name
    becomes an alias to the first enumeration option that was created with the matching
    value, rather than becoming a distinct enumeration option that just happens to have
    a duplicate value."""

    class Colors(Enumeration, aliased=True):
        RED = 1
        GREEN = 2
        BLUE = 3
        ROUGE = 1

    # While there are only 3 distinct values, there are 4 options, due the alias for RED
    assert len(Colors) == 4

    # Ensure that the keys, names, values, items and options methods return as expected
    assert Colors.keys() == ["RED", "GREEN", "BLUE", "ROUGE"]
    assert Colors.names() == ["RED", "GREEN", "BLUE", "ROUGE"]
    assert Colors.values() == [1, 2, 3, 1]
    assert Colors.items() == [("RED", 1), ("GREEN", 2), ("BLUE", 3), ("ROUGE", 1)]
    assert Colors.options() == {"RED": 1, "GREEN": 2, "BLUE": 3, "ROUGE": 1}

    # Ensure that the aliased option has the expected identity and equality
    assert Colors.RED is Colors.ROUGE  # As ROUGE is an alias of RED, identity matches
    assert Colors.RED == Colors.ROUGE  # As ROUGE is an alias of RED, equality matches

    # Ensure that the property values of RED are as expected
    assert Colors.RED.name == "RED"
    assert Colors.RED.value == 1
    assert Colors.RED.aliased is True
    assert Colors.RED.aliases == [Colors.ROUGE]
    assert Colors.RED.named == ["RED", "ROUGE"]

    # Ensure that the property values of ROUGE are as expected (as an alias of RED)
    assert Colors.ROUGE.name == "RED"
    assert Colors.ROUGE.value == 1
    assert Colors.ROUGE.aliased is True
    assert Colors.ROUGE.aliases == [Colors.RED]
    assert Colors.ROUGE.named == ["RED", "ROUGE"]

    # Ensure that the property values of GREEN are as expected
    assert Colors.GREEN.name == "GREEN"
    assert Colors.GREEN.value == 2
    assert Colors.GREEN.aliased is False
    assert Colors.GREEN.aliases == []
    assert Colors.GREEN.named == ["GREEN"]

    # Ensure that the property values of BLUE are as expected
    assert Colors.BLUE.name == "BLUE"
    assert Colors.BLUE.value == 3
    assert Colors.BLUE.aliased is False
    assert Colors.BLUE.aliases == []
    assert Colors.BLUE.named == ["BLUE"]

    # We can find the aliases for the Colors enumeration by finding the options with
    # names that do no match their associated enumeration option name:
    assert [
        name for name, option in Colors.__options__.items() if option.name != name
    ] == [
        "ROUGE"
    ]  # ROUGE is an alias, so its name does not match the option it maps to

    # Ensure that the aliases map is as expected
    assert len(Colors.__aliases__) == 1
    assert Colors.__aliases__ == {"ROUGE": Colors.RED}
    assert list(Colors.__aliases__.items()) == [("ROUGE", Colors.RED)]


def test_extensible_enumeration_flag():
    """Ensure that the creation of enumeration flag classes works as expected."""

    class Permissions(Enumeration, flags=True):
        READ = 1
        WRITE = 2
        # SOMETHING = 3  # needs to be a power of 2 (for the constructor)
        EXECUTE = 4
        # DELETE = 8

    assert issubclass(Permissions, Enumeration)
    assert issubclass(Permissions, EnumerationFlag)

    assert isinstance(Permissions.READ, Enumeration)
    assert isinstance(Permissions.READ, EnumerationFlag)
    assert isinstance(Permissions.READ, int)
    assert Permissions.READ == 1
    assert isinstance(Permissions.READ.name, str)
    assert Permissions.READ.name == "READ"
    assert isinstance(Permissions.READ.value, int)
    assert Permissions.READ.value == 1

    assert isinstance(Permissions.WRITE, Enumeration)
    assert isinstance(Permissions.WRITE, EnumerationFlag)
    assert isinstance(Permissions.WRITE, int)
    assert Permissions.WRITE == 2
    assert isinstance(Permissions.WRITE.name, str)
    assert Permissions.WRITE.name == "WRITE"
    assert isinstance(Permissions.WRITE.value, int)
    assert Permissions.WRITE.value == 2

    # assert Permissions.DELETE == 4
    # assert Permissions.SOMETHING == 3

    permissions = Permissions.READ | Permissions.WRITE

    assert str(permissions) == "Permissions.READ|WRITE"
    assert Permissions.READ in permissions
    assert Permissions.WRITE in permissions
    assert not Permissions.EXECUTE in permissions

    # assert not Permissions.DELETE in permissions  # raises an exception as DELETE doesn't exist

    assert (permissions & Permissions.READ) == Permissions.READ
    assert (permissions & Permissions.WRITE) == Permissions.WRITE

    permissions = permissions ^ Permissions.WRITE  # xor (remove) the WRITE permission

    assert Permissions.READ in permissions
    assert not Permissions.WRITE in permissions
    assert not Permissions.EXECUTE in permissions

    assert (permissions & Permissions.READ) == Permissions.READ
    assert not (permissions & Permissions.WRITE) == Permissions.WRITE

    assert not Permissions.WRITE in permissions
    assert str(permissions) == "Permissions.READ"

    # the order of the name components always follows the order that the underlaying flags were derived
    assert str(Permissions.READ | Permissions.WRITE) == "Permissions.READ|WRITE"
    assert str(Permissions.WRITE | Permissions.READ) == "Permissions.READ|WRITE"
    assert (
        str(Permissions.WRITE | Permissions.READ | Permissions.EXECUTE)
        == "Permissions.READ|WRITE|EXECUTE"
    )

    # Assign 'permissions' to the (~) inverse (opposite) of EXECUTE, i.e. all Permissions options except EXECUTE
    permissions = ~Permissions.EXECUTE

    assert Permissions.READ in permissions
    assert Permissions.WRITE in permissions
    assert not Permissions.EXECUTE in permissions
    assert str(permissions) == "Permissions.READ|WRITE"


def test_extensible_enum_instantiation():
    """Ensure that extensible enumerations can be instatiated in various ways with the
    expected results."""

    class TestEnumMixed(Enumeration):
        YES = "YES"
        NO = False

    assert issubclass(TestEnumMixed, Enumeration)
    assert not issubclass(TestEnumMixed, EnumerationString)
    assert not issubclass(TestEnumMixed, EnumerationInteger)
    assert not issubclass(TestEnumMixed, EnumerationFloat)
    assert not issubclass(TestEnumMixed, EnumerationBytes)

    class TestEnumString(Enumeration):
        YES = "YES"
        NO = "NO"

    assert issubclass(TestEnumString, Enumeration)
    assert issubclass(TestEnumString, EnumerationString)

    class TestEnumInteger(Enumeration):
        pass

    option = EnumerationInteger(enumeration=TestEnumInteger, name="abc", value=123)

    assert isinstance(option, Enumeration)
    assert isinstance(option, EnumerationInteger)
    assert isinstance(option, int)

    class TestEnumInteger(Enumeration):
        YES = 1
        NO = 0

    assert issubclass(TestEnumInteger, Enumeration)
    assert issubclass(TestEnumInteger, EnumerationInteger)

    assert isinstance(TestEnumInteger.YES, Enumeration)
    assert isinstance(TestEnumInteger.YES, EnumerationInteger)
    assert isinstance(TestEnumInteger.YES.value, int)
    assert TestEnumInteger.YES.value == 1
    assert isinstance(TestEnumInteger.YES, int)
    assert TestEnumInteger.YES == 1

    assert str(TestEnumInteger.YES) == "TestEnumInteger.YES"
    assert repr(TestEnumInteger.YES) == "<TestEnumInteger.YES: 1>"

    assert isinstance(TestEnumInteger.NO, EnumerationInteger)
    assert isinstance(TestEnumInteger.NO.value, int)
    assert TestEnumInteger.NO.value == 0
    assert isinstance(TestEnumInteger.NO, int)
    assert TestEnumInteger.NO == 0
    assert int(TestEnumInteger.NO) == 0

    assert str(TestEnumInteger.NO) == "TestEnumInteger.NO"
    assert repr(TestEnumInteger.NO) == "<TestEnumInteger.NO: 0>"

    class Colors(Enumeration, removable=True):
        RED = 1
        YELLOW = 2
        GREEN = 3
        BLUE = 4
        PURPLE = 5

    assert issubclass(Colors, Enumeration)
    assert issubclass(Colors, EnumerationInteger)

    assert isinstance(Colors.RED, Colors)
    assert Colors.RED.name == "RED"
    assert Colors.RED.value == 1

    assert isinstance(Colors.YELLOW, Colors)
    assert Colors.YELLOW.name == "YELLOW"
    assert Colors.YELLOW.value == 2

    assert isinstance(Colors.GREEN, Colors)
    assert Colors.GREEN.name == "GREEN"
    assert Colors.GREEN.value == 3

    assert isinstance(Colors.BLUE, Colors)
    assert Colors.BLUE.name == "BLUE"
    assert Colors.BLUE.value == 4

    assert isinstance(Colors.PURPLE, Colors)
    assert Colors.PURPLE.name == "PURPLE"
    assert Colors.PURPLE.value == 5

    assert Colors.configuration.unique is True
    assert Colors.configuration.overwritable is False
    assert Colors.configuration.subclassable is True

    assert len(Colors) == 5

    assert list(Colors.enumerations.items()) == [
        ("RED", Colors.RED),
        ("YELLOW", Colors.YELLOW),
        ("GREEN", Colors.GREEN),
        ("BLUE", Colors.BLUE),
        ("PURPLE", Colors.PURPLE),
    ]

    Colors.register("ORANGE", 6)

    assert isinstance(Colors.ORANGE, Colors)
    assert Colors.ORANGE.name == "ORANGE"
    assert Colors.ORANGE.value == 6

    assert Colors.reconcile(6) is Colors.ORANGE
    assert Colors.validate(6) is True

    assert Colors.validate(7) is False

    names: list[str] = [
        "RED",
        "YELLOW",
        "GREEN",
        "BLUE",
        "PURPLE",
        "ORANGE",
    ]

    value: list[int] = [
        1,
        2,
        3,
        4,
        5,
        6,
    ]

    for index, enumeration in enumerate(Colors):
        assert names[index] == enumeration.name
        assert value[index] == enumeration.value

    for index, key in enumerate(Colors.keys()):
        assert names[index] == key

    for index, name in enumerate(Colors.names()):
        assert names[index] == name

    Colors.unregister("ORANGE")
    assert Colors.validate(6) is False
    names.remove("ORANGE")

    for index, enumeration in enumerate(EnumerationType):
        logger.debug(
            "%d: %s, %s, %s",
            index,
            enumeration,
            enumeration.name,
            enumeration.value,
        )

    assert Colors.typed is EnumerationType.INTEGER

    # Test map/lambda iteration/generator functionality and the reconciliation of names
    # and values to enumeration options via calls on the enumeration class:
    assert list(map(lambda enumeration: enumeration.name, Colors)) == names


def test_extensible_enum_subclassing():
    """Ensure that subclassing of an extensible Enumeration works as expected given that
    subclassing is enabled by default for all extensible Enumeration classes."""

    class Colors(Enumeration):
        RED = 1
        GREEN = 2
        BLUE = 3

    assert "RED" in Colors
    assert "GREEN" in Colors
    assert "BLUE" in Colors

    assert not "ORANGE" in Colors
    assert not "YELLOW" in Colors
    assert not "PURPLE" in Colors

    class Colors(Colors):
        ORANGE = 4
        YELLOW = 5
        PURPLE = 6

    assert "ORANGE" in Colors
    assert "YELLOW" in Colors
    assert "PURPLE" in Colors


def test_prevention_of_subclassing():
    # To prevent an enumeration class from being extended through subclassing, the
    # `subclassable` keyword argument can be set when creating the class; this will
    # result in an `EnumerationSubclassingError` exception being raised on subclassing:
    class Colors(Enumeration, subclassable=False):
        RED = 1
        GREEN = 2
        BLUE = 3

    with pytest.raises(EnumerationSubclassingError):

        class MoreColors(Colors):
            PURPLE = 4


def test_prevention_of_extensibility():
    # To prevent an enumeration class from being extended through subclassing, the
    # `subclassable` keyword argument can be set when creating the class; this will
    # result in an `EnumerationSubclassingError` exception being raised on subclassing:
    class Colors(Enumeration, extensible=False):
        RED = 1
        GREEN = 2
        BLUE = 3

    with pytest.raises(EnumerationSubclassingError):

        class MoreColors(Colors):
            PURPLE = 4

    with pytest.raises(EnumerationExtensibilityError):
        Colors.register("PURPLE", 4)


def test_enumeration_option_backfilling():
    # By default when an Enumeration class is created, it does not allow the backfilling
    # of enumeration options from any subclasses; options defined on any subclasses will
    # only be available on that subclass, and will not affect the options offered by the
    # superclass itself; this behavior can be modified by setting the `backfill` keyword
    # argument to `True` when creating the enumeration class.

    # This first case demonstrates default behavior, where backfilling is prevented:
    class Colors(Enumeration):
        RED = 1
        GREEN = 2
        BLUE = 3

    # Create a subclass, adding options which are distinctly available on the subclass
    # but which will not affect the options available directly from the superclass:
    class MoreColors(Colors):
        PURPLE = 4
        GOLD = 5

    assert "RED" in Colors
    assert "GREEN" in Colors
    assert "BLUE" in Colors
    assert not "PURPLE" in Colors
    assert not "GOLD" in Colors

    assert "RED" in MoreColors
    assert "GREEN" in MoreColors
    assert "BLUE" in MoreColors
    assert "PURPLE" in MoreColors
    assert "GOLD" in MoreColors

    # To override default behavior and to allow backfilling of options from subclasses,
    # the `backfill` keyword argument can be set to `True` when creating the class. This
    # effectively creates an alternative to extend an existing enumeration class through
    # subclassing and the side-effect of backfilling rather than using the `.register()`
    # method to add new options to an existing enumeration class:
    class Colors(Enumeration, backfill=True):
        RED = 1
        GREEN = 2
        BLUE = 3

    class MoreColors(Colors):
        PURPLE = 4
        GOLD = 5

    assert "RED" in Colors
    assert "GREEN" in Colors
    assert "BLUE" in Colors
    assert "PURPLE" in Colors
    assert "GOLD" in Colors

    assert "RED" in MoreColors
    assert "GREEN" in MoreColors
    assert "BLUE" in MoreColors
    assert "PURPLE" in MoreColors
    assert "GOLD" in MoreColors


def test_extensible_enum_subclassing_with_duplicate_value_exception():
    """Ensure that subclassing an extensible Enumeration class then reusing an existing
    enumeration option value raises an exception when neither the `unique=False` or
    `aliased=True` constructor options are specified at enumeration class creation."""

    class Colors(Enumeration):
        RED = 1
        GREEN = 2
        BLUE = 3

    assert "RED" in Colors
    assert "GREEN" in Colors
    assert "BLUE" in Colors

    assert not "ORANGE" in Colors
    assert not "YELLOW" in Colors
    assert not "PURPLE" in Colors

    with pytest.raises(enumerific.exceptions.EnumerationNonUniqueError) as exception:
        # Attempt to subclass Colors and reuse the value (intentionally or otherwise)
        # for an existing enumeration option – in this case the value `3` – because the
        # base Colors enumeration class was created with neither the `aliased=True` nor
        # the `unique=False` constructor options, this behaviour raises an exception:
        class MoreColors(Colors):
            ORANGE = 3

        assert (
            str(exception)
            == "The enumeration option, 'ORANGE', has a non-unique value, 3, however, unless either the keyword argument 'unique=False' or 'aliased=True' are passed during class construction, all enumeration options must have unique values!"
        )


def test_extensible_enum_subclassing_with_duplicate_aliased_value():
    """Ensure that subclassing an extensible Enumeration class then reusing an existing
    enumeration option value raises an exception when neither the `unique=False` or
    `aliased=True` constructor options are specified at enumeration class creation."""

    class Colors(Enumeration, aliased=True, backfill=True):
        RED = 1
        ORANGE = 2
        YELLOW = 3
        GREEN = 4
        BLUE = 5
        VIOLET = 6

    assert "RED" in Colors
    assert Colors.RED.name == "RED"
    assert Colors.RED.value == 1

    assert "ORANGE" in Colors
    assert Colors.ORANGE.name == "ORANGE"
    assert Colors.ORANGE.value == 2

    assert "YELLOW" in Colors
    assert Colors.YELLOW.name == "YELLOW"
    assert Colors.YELLOW.value == 3

    assert "GREEN" in Colors
    assert Colors.GREEN.name == "GREEN"
    assert Colors.GREEN.value == 4

    assert "BLUE" in Colors
    assert Colors.BLUE.name == "BLUE"
    assert Colors.BLUE.value == 5

    assert "VIOLET" in Colors
    assert Colors.VIOLET.name == "VIOLET"
    assert Colors.VIOLET.value == 6

    assert not "PURPLE" in Colors

    # Attempt to subclass Colors and intentionally reuse an existing enumeration option
    # value – in this case the value `6` and ensure that the class behaves as expected:
    class Colors(Colors):
        PURPLE = 6

    # Ensure that the pre-existing enumeration options were carried into the subclass
    assert "RED" in Colors
    assert "ORANGE" in Colors
    assert "YELLOW" in Colors
    assert "GREEN" in Colors
    assert "BLUE" in Colors
    assert "VIOLET" in Colors

    # As the `aliased=True` constructor option was passed when the Colors enumeration
    # class was initially created, PURPLE becomes an alias to the enumeration option
    # that shares its non-unique value, which in this case is VIOLET.

    # Ensure that the new enumeration option has been created as an alias and not an option
    assert "PURPLE" in Colors
    assert Colors.PURPLE.aliased is True
    assert Colors.PURPLE.name == "VIOLET"
    assert Colors.PURPLE.value == 6

    # Note that VIOLET and PURPLE share the same value (6) so are aliases of each other
    assert Colors.VIOLET is Colors.PURPLE
    assert Colors.PURPLE is Colors.VIOLET


def test_extensible_enum_subclassing_with_duplicate_non_unique_value():
    """Ensure that subclassing an extensible Enumeration class then reusing an existing
    enumeration option value raises an exception when neither the `unique=False` or
    `aliased=True` constructor options are specified at enumeration class creation."""

    class Colors(Enumeration, unique=False):
        RED = 1
        ORANGE = 2
        YELLOW = 3
        GREEN = 4
        BLUE = 5
        VIOLET = 6

    assert "RED" in Colors
    assert Colors.RED.name == "RED"
    assert Colors.RED.value == 1

    assert "ORANGE" in Colors
    assert Colors.ORANGE.name == "ORANGE"
    assert Colors.ORANGE.value == 2

    assert "YELLOW" in Colors
    assert Colors.YELLOW.name == "YELLOW"
    assert Colors.YELLOW.value == 3

    assert "GREEN" in Colors
    assert Colors.GREEN.name == "GREEN"
    assert Colors.GREEN.value == 4

    assert "BLUE" in Colors
    assert Colors.BLUE.name == "BLUE"
    assert Colors.BLUE.value == 5

    assert "VIOLET" in Colors
    assert Colors.VIOLET.name == "VIOLET"
    assert Colors.VIOLET.value == 6

    assert not "PURPLE" in Colors

    # Attempt to subclass Colors and intentionally reuse an existing enumeration option
    # value – in this case the value `6` and ensure that the class behaves as expected:
    class Colors(Colors):
        PURPLE = 6

    # As the `unique=False` constructor option was passed when the Colors enumeration
    # class was initially created, PURPLE becomes is own distinct enumeration option
    # separate from VIOLET in this case with which it shares its value

    assert "PURPLE" in Colors
    assert Colors.PURPLE.name == "PURPLE"
    assert Colors.PURPLE.value == 6

    # Note that although VIOLET and PURPLE share the same value (6) they are not aliases
    assert not Colors.VIOLET is Colors.PURPLE
    assert not Colors.PURPLE is Colors.VIOLET


def test_extensible_enum_options():
    class Colors(Enumeration):
        RED = 1
        GREEN = 2
        BLUE = 3

    options = Colors.options()

    assert isinstance(options, types.MappingProxyType)

    assert len(options) == 3

    for name, option in options.items():
        assert isinstance(option.name, str)
        assert isinstance(option.value, int)


def test_extensible_enum_subclassing_disabled_exception():
    """Ensure an exception is raised when an attempt is made to subclass an extensible
    Enumeration class that has had subclassing disabled via the 'subclassible=False'
    keyword argument when the class was originally created."""

    class Colors(Enumeration, subclassable=False):
        RED = 1
        GREEN = 2
        BLUE = 3

    assert "RED" in Colors
    assert "GREEN" in Colors
    assert "BLUE" in Colors

    assert not "ORANGE" in Colors

    with pytest.raises(enumerific.exceptions.EnumerationError) as exception:
        # Attempt to subclass Colors
        class MoreColors(Colors):
            ORANGE = 4

        assert (
            str(exception)
            == "The 'Colors' enumeration class cannot be subclassed when the keyword argument 'subclassable=False' was passed during its class construction!"
        )


def test_anno_type():
    """Test the anno() annotated value type ensuring that it holds and returns the value
    assigned to it, and that it can store optional annotation key-value pairs."""

    # Create an automatically generated sequence number; if this is the first call since
    # auto.configure() was called, expect the value to match the configured start value;
    # additionally, specify some annotations on the automatically generated sequence:
    value = anno(value=456, notes="these are some notes", another=123)

    # Expect that the value is an instance of the anno class
    assert isinstance(value, anno)

    # Expect that the value can be unwraped from the annotation
    assert value.unwrap() == 456

    # Expect that the assigned "notes" annotation exists and has the value we expect
    assert hasattr(value, "notes")
    assert "notes" in value
    assert isinstance(value.notes, str)
    assert value.notes == "these are some notes"
    assert value["notes"] == "these are some notes"
    assert value.get("notes") == "these are some notes"

    # Expect that the assigned "another" annotation exists and has the value we expect
    assert hasattr(value, "another")
    assert "another" in value
    assert isinstance(value.another, int)
    assert value.another == 123
    assert value["another"] == 123
    assert value.get("another") == 123

    # Expect that the unassigned "something" annotation does not exist
    assert not hasattr(value, "something")
    assert not "something" in value

    # Expect an AttributeError if we try to access an attribute that does not exist
    with pytest.raises(AttributeError):
        assert value.something == 123

    # Expect an AttributeError if we try to access an attribute that does not exist
    with pytest.raises(AttributeError):
        assert isinstance(value.something, None)

    # Expect an KeyError if we try to access an attribute that does not exist as an item
    with pytest.raises(KeyError):
        assert value["something"] == 123

    # We can use the .get() method to handle cases where some enumeration options may
    # have an annotation and others may not; .get() does not raise any exceptions if the
    # specified annotation does not exist; it just returns None by default, but another
    # default value can be specified instead of None when an annotation does not exist:
    assert value.get("something", default=123) == 123


def test_auto_type():
    """Test the auto() number sequence generator ensuring that it generates values of
    the expected class type, int."""

    # Configure the auto class with the relevant sequence generation options
    auto.configure(start=1, steps=1)

    # Create an automatically generated sequence number; if this is the first call since
    # auto.configure() was called, expect the value to match the configured start value:
    value = auto()

    # Expect that the value is an instance of the auto class
    assert isinstance(value, auto)

    # Expect that the value is an instance of the anno class, which auto subclasses
    assert isinstance(value, anno)

    # Expect that the value is an instance of the int class, which auto subclasses
    assert isinstance(value, int)

    # Expect that the value from the first call to auto() matches the configured start
    assert value == 1


def test_auto_type():
    """Test the auto() number sequence generator ensuring that it generates values of
    the expected class type, int, and that it can store optional annotations."""

    # Configure the auto class with the relevant sequence generation options
    auto.configure(start=1, steps=1)

    # Create an automatically generated sequence number; if this is the first call since
    # auto.configure() was called, expect the value to match the configured start value;
    # additionally, specify some annotations on the automatically generated sequence:
    value = auto(notes="these are some notes", another=123)

    # Expect that the value is an instance of the auto class
    assert isinstance(value, auto)

    # Expect that the value is an instance of the anno class, which auto subclasses
    assert isinstance(value, anno)

    # Expect that the value is an instance of the int class, which auto subclasses
    assert isinstance(value, int)

    # Expect that the value from the first call to auto() matches the configured start
    assert value == 1

    # Expect that the assigned "notes" annotation exists and has the value we expect
    assert hasattr(value, "notes")
    assert "notes" in value
    assert isinstance(value.notes, str)
    assert value.notes == "these are some notes"
    assert value["notes"] == "these are some notes"
    assert value.get("notes") == "these are some notes"

    # Expect that the assigned "another" annotation exists and has the value we expect
    assert hasattr(value, "another")
    assert "another" in value
    assert isinstance(value.another, int)
    assert value.another == 123
    assert value["another"] == 123
    assert value.get("another") == 123

    # Expect that the unassigned "something" annotation does not exist
    assert not hasattr(value, "something")
    assert not "something" in value

    # Expect an AttributeError if we try to access an attribute that does not exist
    with pytest.raises(AttributeError):
        assert value.something == 123

    # Expect an AttributeError if we try to access an attribute that does not exist
    with pytest.raises(AttributeError):
        assert isinstance(value.something, None)

    # Expect an KeyError if we try to access an attribute that does not exist as an item
    with pytest.raises(KeyError):
        assert value["something"] == 123

    # We can use the .get() method to handle cases where some enumeration options may
    # have an annotation and others may not; .get() does not raise any exceptions if the
    # specified annotation does not exist; it just returns None by default, but another
    # default value can be specified instead of None when an annotation does not exist:
    assert value.get("something", default=123) == 123


def test_auto_start_one_step_one():
    """Test the auto() number sequence generator; starting at one, and stepped by one on
    each call resulting in a contiguous sequence of numbers of the required length."""

    # Configure the auto class with the relevant sequence generation options
    auto.configure(start=1, steps=1)

    assert auto() == 1
    assert auto() == 2
    assert auto() == 3
    assert auto() == 4
    assert auto() == 5


def test_auto_start_zero_step_one():
    """Test the auto() number sequence generator; starting at zero and stepped by one on
    each call resulting in a contiguous sequence of numbers of the required length."""

    # Configure the auto class with the relevant sequence generation options
    auto.configure(start=0, steps=1)

    assert auto() == 0
    assert auto() == 1
    assert auto() == 2
    assert auto() == 3
    assert auto() == 4
    assert auto() == 5


def test_auto_start_zero_step_two():
    """Test the auto() number sequence generator; starting at zero and stepped by two on
    each call resulting in a contiguous sequence of numbers of the required length."""

    # Configure the auto class with the relevant sequence generation options
    auto.configure(start=0, steps=2)

    assert auto() == 0
    assert auto() == 2
    assert auto() == 4
    assert auto() == 6
    assert auto() == 8


def test_auto_start_one_step_three():
    """Test the auto() number sequence generator; starting at zero, stepped by one, with
    the number multipled (times) by three on each call; note that if times is specified
    it takes precedence over the power keyword argument; they cannot be combined."""

    # Configure the auto class with the relevant sequence generation options
    auto.configure(start=0, steps=1, times=3)

    assert auto() == 0
    assert auto() == 3
    assert auto() == 6
    assert auto() == 9
    assert auto() == 12
    assert auto() == 15
    assert auto() == 18


def test_auto_start_one_step_one_power_of_two():
    """Test the auto() number sequence generator; starting at one, stepped by one, with
    the numbers raised to the power of two to generate sequences which are needed for
    bitwise flag enumerations to ensure that no two enumeration options overlap in their
    bitwise representations, which allows multiple flags to be combined but to still be
    uniquely identified and determined from the whole; auto() also accepts a 'flags'
    keyword argument that defaults to raising the numbers to the power of two."""

    # Configure the auto class with the relevant sequence generation options
    auto.configure(start=1, steps=1, power=2)

    assert auto() == 1
    assert auto() == 2
    assert auto() == 4
    assert auto() == 8
    assert auto() == 16


def test_auto_start_one_step_one_flag_mode():
    """Test the auto() number sequence generator; starting at 1, in flag mode which by
    default generates number sequences to the power of two which are needed for bitwise
    flag enumerations to ensure that no two enumeration options overlap in their bitwise
    representations, which allows multiple flags to be combined but to still be uniquely
    identified and determined from the whole."""

    # Configure the auto class with the relevant sequence generation options
    auto.configure(start=1, steps=1, flags=True)

    assert auto() == 1
    assert auto() == 2
    assert auto() == 4
    assert auto() == 8
    assert auto() == 16
    assert auto() == 32
    assert auto() == 64
    assert auto() == 128
    assert auto() == 256


def test_auto_value_assignment():
    """Test the use of the automatic enumeration value assignment using auto()"""

    class Colors(Enumeration):
        RED = auto()
        GREEN = auto()
        BLUE = auto()

    assert issubclass(Colors, Enumeration)
    assert issubclass(Colors, EnumerationInteger)

    assert isinstance(Colors.RED, Colors)
    assert isinstance(Colors.GREEN, Colors)
    assert isinstance(Colors.BLUE, Colors)

    assert Colors.RED == 1
    assert Colors.GREEN == 2
    assert Colors.BLUE == 3


def test_auto_value_assignment_powers_via_flags_keyword_argument():
    """Test the use of the automatic enumeration value assignment using auto()"""

    class Permissions(Enumeration, flags=True):
        """Create a permissions enumeration based on the EnumerationFlag class, here
        indicated by the 'flags=True' keyword argument which switches the base class
        from Enumeration to EnumerationFlag."""

        READ = auto()
        WRITE = auto()
        EXECUTE = auto()
        DELETE = auto()

    assert issubclass(Permissions, Enumeration)
    assert issubclass(Permissions, EnumerationFlag)

    assert isinstance(Permissions.READ, Permissions)
    assert isinstance(Permissions.WRITE, Permissions)
    assert isinstance(Permissions.EXECUTE, Permissions)
    assert isinstance(Permissions.DELETE, Permissions)

    assert Permissions.READ == 1
    assert Permissions.WRITE == 2
    assert Permissions.EXECUTE == 4
    assert Permissions.DELETE == 8


def test_auto_value_assignment_powers_via_enumeration_flag_base_class():
    """Test the use of the automatic enumeration value assignment using auto()"""

    class Permissions(EnumerationFlag):
        """Create a permissions enumeration based on the EnumerationFlag class, here
        indicated by the subclassing of the EnumerationFlag class."""

        READ = auto()
        WRITE = auto()
        EXECUTE = auto()
        DELETE = auto()

    assert issubclass(Permissions, Enumeration)
    assert issubclass(Permissions, EnumerationFlag)

    assert isinstance(Permissions.READ, Permissions)
    assert isinstance(Permissions.WRITE, Permissions)
    assert isinstance(Permissions.EXECUTE, Permissions)
    assert isinstance(Permissions.DELETE, Permissions)

    assert Permissions.READ == 1
    assert Permissions.WRITE == 2
    assert Permissions.EXECUTE == 4
    assert Permissions.DELETE == 8


def test_auto_value_assignment_powers_via_enumeration_flag_base_class_with_start():
    """Test the use of the automatic enumeration value assignment using auto()"""

    class Permissions(EnumerationFlag, start=2):
        """Create a permissions enumeration based on the EnumerationFlag class, here
        indicated by the subclassing of the EnumerationFlag class."""

        READ = auto()
        WRITE = auto()
        EXECUTE = auto()
        DELETE = auto()

    assert issubclass(Permissions, Enumeration)
    assert issubclass(Permissions, EnumerationFlag)

    assert isinstance(Permissions.READ, Permissions)
    assert isinstance(Permissions.WRITE, Permissions)
    assert isinstance(Permissions.EXECUTE, Permissions)
    assert isinstance(Permissions.DELETE, Permissions)

    assert Permissions.READ == 2
    assert Permissions.WRITE == 4
    assert Permissions.EXECUTE == 8
    assert Permissions.DELETE == 16


def test_auto_value_assignment_powers_and_subclass_when_auto_starts_at_the_next_value():
    """Test the use of the automatic enumeration value assignment using auto()"""

    class Permissions(EnumerationFlag):
        """Create a permissions enumeration based on the EnumerationFlag class, here
        indicated by the subclassing of the EnumerationFlag class."""

        READ = auto()
        WRITE = auto()
        EXECUTE = auto()

    assert issubclass(Permissions, Enumeration)
    assert issubclass(Permissions, EnumerationFlag)

    assert isinstance(Permissions.READ, Permissions)
    assert isinstance(Permissions.WRITE, Permissions)
    assert isinstance(Permissions.EXECUTE, Permissions)

    assert Permissions.READ == 1
    assert Permissions.WRITE == 2
    assert Permissions.EXECUTE == 4

    class MorePermissions(Permissions):
        """Create a subclass of Permissions, and extend it with a new option that is
        automatically assigned its value via auto() to check that the next value created
        by auto() is the next available value in sequence after those created for the
        Permissions class above; the maximum value of the inherited class' enumerations
        is captured by the EnumerationMetaClass when a subclass is being created, with
        the next available value being configured for use by the next call to auto()."""

        DELETE = auto()

    assert issubclass(MorePermissions, Enumeration)
    assert issubclass(MorePermissions, EnumerationFlag)

    assert isinstance(Permissions.READ, Permissions)
    assert isinstance(Permissions.WRITE, Permissions)
    assert isinstance(Permissions.EXECUTE, Permissions)
    assert isinstance(MorePermissions.DELETE, Permissions)

    # Ensure that the next flag has the expected value, in this case it should be 8
    assert Permissions.READ == 1
    assert Permissions.WRITE == 2
    assert Permissions.EXECUTE == 4
    assert MorePermissions.DELETE == 8


def test_auto_value_assignment_and_subclass_when_auto_starts_at_the_next_value():
    """Test the use of the automatic enumeration value assignment using auto()"""

    class Colors(Enumeration):
        """Create a test Colors enumeration based on the Enumeration class."""

        RED = auto()
        ORANGE = auto()
        YELLOW = auto()
        GREEN = auto()
        BLUE = auto()
        VIOLET = auto()

    assert issubclass(Colors, Enumeration)
    assert issubclass(Colors, EnumerationInteger)

    assert isinstance(Colors.RED, Colors)
    assert isinstance(Colors.ORANGE, Colors)
    assert isinstance(Colors.YELLOW, Colors)
    assert isinstance(Colors.GREEN, Colors)
    assert isinstance(Colors.BLUE, Colors)
    assert isinstance(Colors.VIOLET, Colors)

    assert Colors.RED == 1
    assert Colors.ORANGE == 2
    assert Colors.YELLOW == 3
    assert Colors.GREEN == 4
    assert Colors.BLUE == 5
    assert Colors.VIOLET == 6

    class MetallicColors(Colors):
        """Create a subclass of Colors, and extend it with several new options that are
        automatically assigned their value via auto() to check that the next values that
        are created by auto() are the next available values in sequence after those
        created for the Colors class above; the maximum value of the inherited class'
        enumerations is captured by the EnumerationMetaClass when a subclass is being
        created, with the next available value being configured for use by auto()."""

        GOLD = auto()
        SILVER = auto()
        COPPER = auto()

    assert issubclass(MetallicColors, Enumeration)
    assert issubclass(MetallicColors, EnumerationInteger)

    assert isinstance(Colors.RED, Colors)
    assert isinstance(Colors.ORANGE, Colors)
    assert isinstance(Colors.YELLOW, Colors)
    assert isinstance(Colors.GREEN, Colors)
    assert isinstance(Colors.BLUE, Colors)
    assert isinstance(Colors.VIOLET, Colors)

    assert isinstance(MetallicColors.GOLD, Colors)
    assert isinstance(MetallicColors.SILVER, Colors)
    assert isinstance(MetallicColors.COPPER, Colors)

    # Ensure that the next options have the expected values, in this case 7, 8 and 9
    assert Colors.RED == 1
    assert Colors.ORANGE == 2
    assert Colors.YELLOW == 3
    assert Colors.GREEN == 4
    assert Colors.BLUE == 5
    assert Colors.VIOLET == 6

    assert MetallicColors.GOLD == 7
    assert MetallicColors.SILVER == 8
    assert MetallicColors.COPPER == 9


def test_enumeration_annotations():
    """Test the annotation of an enumeration option with manually assigned auto values"""

    class Colors(Enumeration):
        """Create a test Color enumeration based on the Enumeration class."""

        RED = anno(auto(), rgb=(255, 0, 0), primary=True)
        GREEN = anno(auto(), rgb=(0, 255, 0), primary=True)
        BLUE = anno(auto(), rgb=(0, 0, 255), primary=True)
        PURPLE = anno(auto(), rgb=(255, 0, 255), primary=False)

    assert issubclass(Colors, Enumeration)
    assert issubclass(Colors, EnumerationInteger)

    assert isinstance(Colors.RED, Colors)
    assert isinstance(Colors.GREEN, Colors)
    assert isinstance(Colors.BLUE, Colors)
    assert isinstance(Colors.PURPLE, Colors)

    assert Colors.RED == 1
    assert Colors.GREEN == 2
    assert Colors.BLUE == 3
    assert Colors.PURPLE == 4

    assert Colors.RED.rgb == (255, 0, 0)
    assert Colors.RED.primary is True
    assert Colors.GREEN.rgb == (0, 255, 0)
    assert Colors.GREEN.primary is True
    assert Colors.BLUE.rgb == (0, 0, 255)
    assert Colors.BLUE.primary is True
    assert Colors.PURPLE.rgb == (255, 0, 255)
    assert Colors.PURPLE.primary is False


def test_enumeration_annotations_with_automatic_value():
    """Test the annotation of an enumeration option with automatically assigned auto values"""

    class Colors(Enumeration):
        """Create a test Color enumeration based on the Enumeration class."""

        # Using annoauto() combines auto() and anno() to assign an automatic value and any annotations
        RED = auto(rgb=(255, 0, 0), primary=True)
        GREEN = auto(rgb=(0, 255, 0), primary=True)
        BLUE = auto(rgb=(0, 0, 255), primary=True)
        PURPLE = auto(rgb=(255, 0, 255), primary=False)

    assert issubclass(Colors, Enumeration)
    assert issubclass(Colors, EnumerationInteger)

    assert isinstance(Colors.RED, Colors)
    assert isinstance(Colors.GREEN, Colors)
    assert isinstance(Colors.BLUE, Colors)
    assert isinstance(Colors.PURPLE, Colors)

    assert Colors.RED == 1
    assert Colors.GREEN == 2
    assert Colors.BLUE == 3
    assert Colors.PURPLE == 4

    assert Colors.RED.rgb == (255, 0, 0)
    assert Colors.RED.primary is True
    assert Colors.GREEN.rgb == (0, 255, 0)
    assert Colors.GREEN.primary is True
    assert Colors.BLUE.rgb == (0, 0, 255)
    assert Colors.BLUE.primary is True
    assert Colors.PURPLE.rgb == (255, 0, 255)
    assert Colors.PURPLE.primary is False


def test_membership_in_list():
    """Test membership determination of an enumeration in a list"""

    class Colors(Enumeration):
        """Create a test Color enumeration based on the Enumeration class."""

        RED = auto()
        ORANGE = auto()
        YELLOW = auto()
        GREEN = auto()
        BLUE = auto()
        VIOLET = auto()

    assert issubclass(Colors, Enumeration)
    assert issubclass(Colors, EnumerationInteger)

    colors: list[Colors] = [
        Colors.RED,
        Colors.YELLOW,
    ]

    assert isinstance(colors, list)
    assert len(colors) == 2

    assert Colors.RED in colors
    assert Colors.ORANGE not in colors
    assert Colors.YELLOW in colors
    assert Colors.GREEN not in colors
    assert Colors.BLUE not in colors
    assert Colors.VIOLET not in colors


def test_membership_in_set():
    """Test membership determination of an enumeration in a set"""

    class Colors(Enumeration):
        """Create a test Color enumeration based on the Enumeration class."""

        RED = auto()
        ORANGE = auto()
        YELLOW = auto()
        GREEN = auto()
        BLUE = auto()
        VIOLET = auto()

    assert issubclass(Colors, Enumeration)
    assert issubclass(Colors, EnumerationInteger)

    colors: set[Colors] = set(
        [
            Colors.RED,
            Colors.YELLOW,
        ]
    )

    assert isinstance(colors, set)
    assert len(colors) == 2

    assert Colors.RED in colors
    assert Colors.ORANGE not in colors
    assert Colors.YELLOW in colors
    assert Colors.GREEN not in colors
    assert Colors.BLUE not in colors
    assert Colors.VIOLET not in colors


def test_membership_in_tuple():
    """Test membership determination of an enumeration in a tuple"""

    class Colors(Enumeration):
        """Create a test Color enumeration based on the Enumeration class."""

        RED = auto()
        ORANGE = auto()
        YELLOW = auto()
        GREEN = auto()
        BLUE = auto()
        VIOLET = auto()

    assert issubclass(Colors, Enumeration)
    assert issubclass(Colors, EnumerationInteger)

    colors: tuple[Colors] = tuple(
        [
            Colors.RED,
            Colors.YELLOW,
        ]
    )

    assert isinstance(colors, tuple)
    assert len(colors) == 2

    assert Colors.RED in colors
    assert Colors.ORANGE not in colors
    assert Colors.YELLOW in colors
    assert Colors.GREEN not in colors
    assert Colors.BLUE not in colors
    assert Colors.VIOLET not in colors


def test_attribute_access():
    """Test access to attributes (methods, properties, etc) on an Enumeration subclass"""

    class Colors(Enumeration, backfill=True):
        """Create a test Color enumeration based on the Enumeration class"""

        RED = auto(RGB=(255, 0, 0))
        ORANGE = auto(RGB=(255, 165, 0))
        YELLOW = auto(RGB=(255, 255, 0))
        GREEN = auto(RGB=(0, 255, 0))
        BLUE = auto(RGB=(0, 0, 255))
        VIOLET = auto(RGB=(255, 0, 255))

        @property
        def HLS(self) -> tuple[float, float, float]:
            """Convert the RGB color code into its HLS equivalent."""

            # Normalize the RGB values into a 0-255 range first
            (h, l, s) = colorsys.rgb_to_hls(
                self.RGB[0] / 255.0,
                self.RGB[1] / 255.0,
                self.RGB[2] / 255.0,
            )

            # Normalize the HLS values into their normal 0-360º, 0-100%, 0-100% ranges
            return tuple([h * 360.0, l * 100.0, s * 100.0])

        def isWarm(self):
            """Roughly (just for test purposes) determine in the color is 'warm'"""

            (hue, lightness, saturation) = self.HLS

            return (
                (0 <= hue < 115) and (0 < lightness <= 80) and (10 <= saturation <= 100)
            )

        def isCool(self):
            """Roughly (just for test purposes) determine in the color is 'cool'"""

            (hue, lightness, saturation) = self.HLS

            return (
                (115 <= hue <= 360) and (lightness <= 100) and (saturation <= 100)
            ) or ((hue == 0) and (10 <= lightness <= 100) and (saturation == 0))

    # Ensure that the Colors enumeration subclass is of the expected types
    assert issubclass(Colors, Enumeration)
    assert issubclass(Colors, EnumerationInteger)

    # Ensure that the Colors enumeration subclass has the expected number of options
    assert len(Colors) == 6

    # Ensure that the Colors enumeration subclass has the expected options
    assert Colors.RED in Colors
    assert Colors.ORANGE in Colors
    assert Colors.YELLOW in Colors
    assert Colors.GREEN in Colors
    assert Colors.BLUE in Colors
    assert Colors.VIOLET in Colors

    # Ensure that the Colors enumeration subclass as the expected isWarm method
    assert hasattr(Colors, "isWarm")
    assert Colors.RED.isWarm() is True
    assert Colors.ORANGE.isWarm() is True
    assert Colors.YELLOW.isWarm() is True
    assert Colors.GREEN.isWarm() is False
    assert Colors.BLUE.isWarm() is False
    assert Colors.VIOLET.isWarm() is False

    # Ensure that the Colors enumeration subclass as the expected isCool method
    assert hasattr(Colors, "isCool")
    assert Colors.RED.isCool() is False
    assert Colors.ORANGE.isCool() is False
    assert Colors.YELLOW.isCool() is False
    assert Colors.GREEN.isCool() is True
    assert Colors.BLUE.isCool() is True
    assert Colors.VIOLET.isCool() is True

    # Create an enumeration subclass of the Colors enumeration, inheriting its options
    # and attributes, and adding a new GOLD option for testing:
    class MoreColors(Colors):
        GOLD = auto(RGB=(255, 215, 0), metallic=True)

    # Ensure that the MoreColors enumeration subclass is of the expected type
    assert issubclass(MoreColors, Enumeration)
    assert issubclass(MoreColors, EnumerationInteger)

    # Ensure that the MoreColors enumeration subclass has the expected number of options
    assert len(MoreColors) == 7

    # Ensure that the Colors enumeration superclass has the expected number of options,
    # which because we enabled backfilling, so that it gains any enumeration options
    # added to any of its subclasses, should be 7 at this point:
    assert len(Colors) == 7

    # Ensure that the MoreColors enumeration subclass has the expected options
    assert MoreColors.RED in Colors
    assert MoreColors.ORANGE in Colors
    assert MoreColors.YELLOW in Colors
    assert MoreColors.GREEN in Colors
    assert MoreColors.BLUE in Colors
    assert MoreColors.VIOLET in Colors
    assert MoreColors.GOLD in MoreColors

    # Ensure that the Colors enumeration superclass backfilled the new GOLD option which
    # was enabled by setting the backfill keyword argument to True when creating Colors:
    assert MoreColors.GOLD in Colors

    # Ensure that the MoreColors enumeration subclass as the expected methods
    assert hasattr(MoreColors, "isWarm")
    assert hasattr(MoreColors, "isCool")

    # Ensure that the MoreColors enumeration subclass methods return the expected values
    assert MoreColors.GOLD.isWarm() is True
    assert MoreColors.GOLD.isCool() is False

    # Keep a reference to the original instance of Colors for identity checking, etc.
    OriginalColors = Colors

    # Create an enumeration subclass of the Colors enumeration, inheriting its options
    # and attributes, and adding a new SILVER option for testing; note when subclassing,
    # the subclass can be given the same name as the class it inherits from, so in this
    # scope it effectively replaces the superclass, at least by its direct name:
    class Colors(MoreColors):
        SILVER = auto(RGB=(192, 192, 192), metallic=True)

        def isMetallic(self) -> bool:
            """Return `True` for metallic Colors options, and False otherwise; this is
            determined by checking if the Colors option has a 'metallic' annotation on
            its value, and if so, if 'metallic' has a value of `True`; note that we can
            use the `.get(name, default)` method to check if an annotation exists and
            to return an optional default or `None` if it does not. Accessing attributes
            that do not exist results in an exception being raised, so for attributes
            that are not consistently defined for all options on a given enumeration,
            using the `.get()` method offers a safe way to attempt access or default."""
            return self.get("metallic", default=False) is True

        @property
        def HEX(self) -> str:
            """Return the hexademimal string representation of the RGB color value."""
            return f"{self.RGB[0]:02X}{self.RGB[1]:02X}{self.RGB[2]:02X}"

        @classmethod
        def count(cls) -> int:
            return len(cls)

    # Ensure that the Colors enumeration subclass is of the expected type
    assert issubclass(Colors, Enumeration)
    assert issubclass(Colors, EnumerationInteger)

    # Ensure that the Colors enumeration subclass has the expected number of options
    assert len(Colors) == 8

    # Ensure that the Colors enumeration subclass has the expected options
    assert Colors.RED in Colors
    assert Colors.ORANGE in Colors
    assert Colors.YELLOW in Colors
    assert Colors.GREEN in Colors
    assert Colors.BLUE in Colors
    assert Colors.VIOLET in Colors
    assert Colors.GOLD in Colors
    assert Colors.SILVER in Colors

    # Ensure that the Colors enumeration subclass as the expected methods
    assert hasattr(Colors, "isWarm")
    assert hasattr(Colors, "isCool")

    # Ensure that the Colors enumeration subclass methods return the expected values
    assert Colors.SILVER.isWarm() is False
    assert Colors.SILVER.isCool() is True

    # Attempt to reconcile a Colors option, in this case via its name, "RED"
    color: Colors = Colors.reconcile("RED")
    assert isinstance(color, Enumeration)

    # Assert that the reconciled option is the one we expected
    assert color is Colors.RED
    assert color.name == "RED"
    assert color.value == 1
    assert color == 1

    # Note: As the second version of the "Colors" class defined above shadows the first,
    # we cannot perform identity checking on options associated with the first version
    # via the second class; they can only be performed if we have a reference to the
    # original class object, because while these two "Colors" classes share the same
    # name, they are distinct objects with different identities, and enumeration options
    # are always created as instances of the class they are defined within or registered
    # on; if giving a subclass of an enumeration class the same name, be aware that any
    # identity checking must be performed against the object that the option is tied to:
    assert isinstance(Colors.RED, OriginalColors)
    assert isinstance(color, OriginalColors)

    # Assert that attribute access to annotations, properties and methods works:
    assert color.RGB == (255, 0, 0)  # RGB is an annotation added to the option's value
    assert color.HLS == (0.0, 50.0, 100.0)  # HLS is a property on to the Colors class
    assert color.isWarm() is True  # isWarm() is a method on the first Colors class
    assert color.isMetallic() is False  # isMetallic() is defined on the Colors subclass
    assert color.HEX == "FF0000"  # HEX is a property defined on the Colors subclass
    assert color.count() == 8  # count() is a classmethod defined on the Colors subclass
