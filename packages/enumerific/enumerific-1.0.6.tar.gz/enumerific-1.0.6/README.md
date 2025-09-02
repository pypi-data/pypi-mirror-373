# Enumerific Enums

The Enumerific library provides a greenfield implementation of enumerations with many unique features through the library's own `Enumeration` class, as well as separately offering several useful extra methods for the built-in standard library `enums.Enum` type.

The Enumerific library's `Enumeration` class offers the following features:

 * A greenfield implementation of enumerations compatible with Python 3.10 and later versions;
 * Enumerific enumerations can hold option values of the same or mixed types, including `int`, `float`, `complex`, `str`, `bytes`, `set`, `tuple`, `list`, `dict` as well as arbitrary `object` types;
 * Enumerific enumeration options can be accessed directly as native data types and enumeration options can be used anywhere that the corresponding native data types can be used;
 * Support for automatic typecasting of the `Enumeration` base class to support the use of enumeration option values interchangeably with native data type values;
 * Enumerific enumerations options can be added after an `Enumeration` class has been created either through extending an existing enumerations class by subclassing or by registering new options directly on an existing enumerations class via the `.register()` method; this is especially useful for cases where enumeration options may not all be known prior to runtime;
 * Enumerific enumerations options can be removed after an `Enumeration` class has been created via the `.unregister()` method; this specialised behaviour is prevented by default, but can be enabled for advanced use cases;
 * Enforcement of unique values for all options within an enumeration, unless overridden;
 * Support for aliasing enumeration options, and control over this behaviour;
 * Support for backfilling enumeration options on a superclass when subclassing, and control over this behaviour
 * Support for redefining enumeration options, and control over this behaviour;
 * Support for automatically generating unique number sequences for enumeration options, including powers of two for bitwise enumeration flags, as well as other sequences such as powers of other numbers and factoring;
 * Support for annotating enumeration options with additional arbitrary key-value pairs, which can be particularly useful for associating additional data with a given enumeration option, which may be accessed later anywhere in code that the enumeration option is available;
 * Simple one-line reconciliation of `Enumeration` class options to the corresponding `enums.Enum` class instance that represents the corresponding option; reconciliation by enumeration option name, value and enumeration class instance reference are all supported through the `.reconcile()` class method;
 * Simple one-line validation of `Enumeration` class options; validation by enumeration option name, value and enumeration class instance reference are all supported through the `.validate()` class method;
 * Simple access to all of the options provided by an `Enumeration` class instance through the `.options()` class method;
 * Access to all of the names of the `Enumeration` class options via the `.names()` method;
 * Access to all of the names/keys of the `Enumeration` class options via the `.keys()` method;
 * Access to all of the values of the `Enumeration` class options via the `.values()` method;
 * Access to all of the key-value pairs of the `Enumeration` class options via the `.items()` method;
 * Ability to determine if an enumeration option is an alias of another option, or is an option in its own right via the `Enumeration` class' `.aliased` property.
 * Ability to obtain the aliases for an enumeration option via the `.aliases` property.

Furthermore, as noted, the Enumerific library also offers extended functionality for the built-in standard library `enums.Enum` type:

 * Simple one-line reconciliation of `enums.Enum` options to the corresponding `enums.Enum` class instance that represents the corresponding option; reconciliation by enumeration option name, value and enumeration class instance reference are all supported through the `.reconcile()` class method;
 * Simple one-line validation of `enums.Enum` options; validation by enumeration option name, value and enumeration class instance reference are all supported through the `.validate()` class method;
 * Simple access to all of the options provided by an `enums.Enum` class instance through the `.options()` class method.

### Requirements

The Enumerific library has been tested with Python 3.10, 3.11, 3.12 and 3.13, and is not
compatible with Python 3.9 or earlier.

### Installation

Enumerific is available from the PyPI, so may be added to a project's dependencies via
its `requirements.txt` file or similar by referencing the library's name, `enumerific`,
or the library may be installed directly into your local runtime environment using `pip`
by entering the following command, and following any prompts:

	$ pip install enumerific

### Usage

To use the Enumerific library's implementation of enumerations import the `Enumeration` class from the Enumerific library:

```python
from enumerific import Enumeration

class Colors(Enumeration):
    RED = 1
    GREEN = 2
    BLUE = 3

assert issubclass(Colors, Enumeration)

# Note that as all of the Colors enumeration options have integer values, the class was
# typecast to int so that its option values can be used interchangeably with integers:
assert issubclass(Colors, int)

color = Colors.RED

# Enumeration class options are instances of the class
assert isinstance(color, Colors)

# They can also be instances of the raw value that was assigned to the option
assert isinstance(color, int)

# Each enumeration class option has a name (the name used to define the option)
assert color.name == "RED"

# Each enumeration class option has a value (the value used when defining the option)
assert color.value == 1

# The identity of an enumeration option matches the option
assert color is Colors.RED

# The equality of an enumeration option can also be compared against the enumeration
# option directly, against the name of the option, or against the value:
assert color == Colors.RED
assert color == "RED"
assert color == 1
assert color != 2
```

#### Example 1: Reconciling a Value

```python
from enumerific import Enumeration

class Colors(Enumeration):
    RED = 1
    GREEN = 2
    BLUE = 3

# Given a string value in this case
value = 1

# Reconcile it to the associated enumeration option
color = Colors.reconcile(value)

assert color == Colors.RED  # asserts successfully
assert color is Colors.RED  # asserts successfully as Enumeration class options are singletons
```

#### Example 2: Reconciling an Enumeration Option Name

```python
from enumerific import Enumeration

class Colors(Enumeration):
    RED = 1
    GREEN = 2
    BLUE = 3

# Given a string value in this case
value = "RED"

# Reconcile it to the associated enumeration option
color = Colors.reconcile(value)

assert color == Colors.RED  # asserts successfully
assert color is Colors.RED  # asserts successfully as Enumeration class options are singletons

# Given a string value in this case
value = "red"

# Reconcile it to the associated enumeration option;
# values can be reconciled caselessly too:
color = Colors.reconcile(value, caselessly=True)

assert color == Colors.RED  # asserts successfully
assert color is Colors.RED  # asserts successfully as Enumeration class options are singletons
```

#### Example 3: Validating a Value

```python
from enumerific import Enumeration

class Colors(Enumeration):
    RED = 1
    GREEN = 2
    BLUE = 3

# The value can be an enumeration option's name, its value, or the enumeration option
value = "RED"
value = 1
value = Colors.RED

if Colors.validate(value) is True:
    # do something if the value could be validated
    pass
else:
    # do something else if the value could not be validated
    pass
```

#### Example 4: Iterating Over Enumeration Options

```python
from enumerific import Enumeration

class Colors(Enumeration):
    RED = 1
    GREEN = 2
    BLUE = 3

options = Colors.options()

for name, option in options.items():
    # do something with each option
    print(option.name, option.value)
```

#### Example 5: Iterating Over Enumeration Names

```python
from enumerific import Enumeration

class Colors(Enumeration):
    RED = 1
    GREEN = 2
    BLUE = 3

for name in Colors.names():
    # do something with each option name
    print(name)
```

#### Example 6: Iterating Over Enumeration Keys

```python
from enumerific import Enumeration

class Colors(Enumeration):
    RED = 1
    GREEN = 2
    BLUE = 3

for key in Colors.keys():
    # do something with each option key
    print(key)
```

#### Example 7: Iterating Over Enumeration Values

```python
from enumerific import Enumeration

class Colors(Enumeration):
    RED = 1
    GREEN = 2
    BLUE = 3

for value in Colors.values():
    # do something with each option key
    print(value)
```

#### Example 8: Registering New Options

```python
from enumerific import Enumeration

class Colors(Enumeration):
    RED = 1
    GREEN = 2
    BLUE = 3

Colors.register("PURPLE", 4)
Colors.register("GOLD", 5)

assert "PURPLE" in Colors
assert Colors.PURPLE.name == "PURPLE"
assert Colors.PURPLE.value == 4
assert Colors.PURPLE == 4

assert "GOLD" in Colors
assert Colors.GOLD.name == "GOLD"
assert Colors.GOLD.value == 5
assert Colors.GOLD == 5
```

#### Example 9: Subclassing

```python
from enumerific import Enumeration

class Colors(Enumeration):
    RED = 1
    GREEN = 2
    BLUE = 3

# Ensure that Colors has the expected options
assert "RED" in Colors
assert "GREEN" in Colors
assert "BLUE" in Colors

# Create a subclass of Colors, inheriting its options
class MoreColors(Colors):
    PURPLE = 4
    GOLD = 5

# Ensure that MoreColors inherited the options from Colors, as well as adding its own
assert "RED" in MoreColors
assert "GREEN" in MoreColors
assert "BLUE" in MoreColors
assert "PURPLE" in MoreColors
assert "GOLD" in MoreColors

# As backfilling is off by default subclass options won't be available on the superclass
assert not "PURPLE" in Colors
assert not "GOLD" in Colors
```

#### Example 10: Subclassing with Backfilling

```python
from enumerific import Enumeration

# To override the default behaviour and to allow backfilling of options from subclasses,
# the `backfill` keyword argument can be set to `True` when creating the class. This
# effectively creates another way to extend an existing enumeration class through
# subclassing and its side-effect of backfilling, compared to using the `.register()`
# method to add new options to an existing enumeration class:
class Colors(Enumeration, backfill=True):
    RED = 1
    GREEN = 2
    BLUE = 3

assert "RED" in Colors
assert "GREEN" in Colors
assert "BLUE" in Colors

class MoreColors(Colors):
    PURPLE = 4
    GOLD = 5

assert "RED" in MoreColors
assert "GREEN" in MoreColors
assert "BLUE" in MoreColors
assert "PURPLE" in MoreColors
assert "GOLD" in MoreColors

# As backfilling has been enabled for the superclass, subclass options are available on
# both the subclass as seen above as well as on the superclass through backfilling:
assert "PURPLE" in Colors
assert "GOLD" in Colors
```

#### Example 11: Subclassing Over

```python
from enumerific import Enumeration

class Colors(Enumeration):
    RED = 1
    GREEN = 2
    BLUE = 3

assert "RED" in Colors
assert Colors.RED == 1

assert "GREEN" in Colors
assert Colors.GREEN == 2

assert "BLUE" in Colors
assert Colors.BLUE == 3

# Subclasses of Enumerations classes can be given the same name as the parent class, so
# within this scope, the subclass shadows the superclass; the subclass inherits all the
# enumeration options of its parent(s) superclasses:
class Colors(Colors):
    PURPLE = 4
    GOLD = 5

assert "RED" in Colors
assert "GREEN" in Colors
assert "BLUE" in Colors

assert "PURPLE" in Colors
assert Colors.PURPLE == 4

assert "GOLD" in Colors
assert Colors.GOLD == 5
```

#### Example 12: Unregistering Existing Option

```python
from enumerific import Enumeration

# Note that unregistering options is prevented by default; to all options to be removed
# the `removable` argument needs to be set to `True` when the class is created:
class Colors(Enumeration, removable=True):
    RED = 1
    GREEN = 2
    BLUE = 3

Colors.unregister("GREEN")

assert "RED" in Colors
assert "GREEN" not in Colors
assert "BLUE" in Colors
```

#### Example 13: Preventing Subclassing of Enumeration Classes

```python
from enumerific import Enumeration, EnumerationSubclassingError
import pytest

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
```

#### Example 14: Aliasing Options

```python
from enumerific import Enumeration

# Note that aliasing options is prevented by default to ensure that all options have
# unique values; to allow aliasing, the `aliased` argument needs to be set to `True`
# when the class is created; aliases can be added by referencing the original option's
# name or its value as demonstrated below with the ROUGE and VERTE aliases:
class Colors(Enumeration, aliased=True):
    RED = 1
    GREEN = 2
    BLUE = 3
    ROUGE = RED
    VERTE = 2

assert "RED" in Colors
assert "GREEN" in Colors
assert "BLUE" in Colors
assert "ROUGE" in Colors
assert "VERTE" in Colors

# Note that aliases are just different names for the same exact option, so the aliases
# can be used interchangeably with the original option, and they have the same identity:
assert Colors.RED is Colors.ROUGE
assert Colors.GREEN is Colors.VERTE

# All of the other properties of aliased options are also identical because the alias is
# just another reference to the same exact object in memory:
assert Colors.RED.name == Colors.ROUGE.name
assert Colors.RED.value == Colors.ROUGE.value

# Different options have their own distinct identities
assert not Colors.RED is Colors.VERTE

# Aliased options report that they have been aliased:
assert Colors.RED.aliased is True
assert Colors.GREEN.aliased is True
assert Colors.ROUGE.aliased is True
assert Colors.VERTE.aliased is True

# Non-aliased options do not report that they have been aliased:
assert Colors.BLUE.aliased is False

# The aliases for an option can be obtained via the .aliases property:
assert Colors.RED.aliases == [Colors.ROUGE]
assert Colors.GREEN.aliases == [Colors.VERTE]
assert Colors.BLUE.aliases == []  # BLUE has not been aliased

# The names including any aliases for an option can be obtained via the .named property
assert Colors.RED.named == ["RED", "ROUGE"]
assert Colors.GREEN.named == ["GREEN", "VERTE"]
assert Colors.BLUE.named == ["BLUE"]
```

#### Example 15: Non-Unique Options

```python
from enumerific import Enumeration

# Note that non-unique options are prevented by default to ensure that all options have
# unique values; to allow non-unique option values, the `unique` argument needs to be
# set to `False` when the class is created:
class Colors(Enumeration, unique=False):
    RED = 1
    GREEN = 1
    BLUE = 3

assert "RED" in Colors
assert Colors.RED.name == "RED"
assert Colors.RED.value == 1
assert Colors.RED == 1

assert "GREEN" in Colors
assert Colors.GREEN.name == "GREEN"
assert Colors.GREEN.value == 1
assert Colors.GREEN == 1

assert "BLUE" in Colors
assert Colors.BLUE.name == "BLUE"
assert Colors.BLUE.value == 3
assert Colors.BLUE == 3

# Note that although options can use the same values when the class has been configured
# to allow it, the enumeration options still maintain their own distinct identities:
assert not Colors.RED is Colors.GREEN
assert not Colors.BLUE is Colors.RED

# However, when enumeration options share values, options with the same values will
# compare as equal via equality checking (which is different than identity checking):
assert Colors.RED == Colors.GREEN
assert Colors.BLUE != Colors.RED
```

#### Example 16: Bit Wise Flags

```python
from enumerific import Enumeration

class Permissions(Enumeration, flags=True):
    READ = 1
    WRITE = 2
    EXECUTE = 4
    DELETE = 8

assert "READ" in Permissions
assert Permissions.READ.name == "READ"
assert Permissions.READ.value == 1
assert Permissions.READ == 1

assert "WRITE" in Permissions
assert Permissions.WRITE.name == "WRITE"
assert Permissions.WRITE.value == 2
assert Permissions.WRITE == 2

assert "EXECUTE" in Permissions
assert Permissions.EXECUTE.name == "EXECUTE"
assert Permissions.EXECUTE.value == 4
assert Permissions.EXECUTE == 4

# OR (add/merge) the READ and WRITE permission flags into the 'permissions' variable
permissions = Permissions.READ | Permissions.WRITE

assert str(permissions) == "Permissions.READ|WRITE"
assert Permissions.READ in permissions
assert Permissions.WRITE in permissions
assert not Permissions.EXECUTE in permissions

# Raises an exception as DELETE doesn't exist
assert not Permissions.DELETE in permissions

assert (permissions & Permissions.READ) == Permissions.READ
assert (permissions & Permissions.WRITE) == Permissions.WRITE

# XOR (remove) the WRITE permission from the 'permissions' variable
permissions = permissions ^ Permissions.WRITE

assert Permissions.READ in permissions
assert not Permissions.WRITE in permissions
assert not Permissions.EXECUTE in permissions

assert (permissions & Permissions.READ) == Permissions.READ
assert not (permissions & Permissions.WRITE) == Permissions.WRITE

assert not Permissions.WRITE in permissions
assert str(permissions) == "Permissions.READ"

# The order of the name components follows the order the underlaying flags were declared
assert str(Permissions.READ | Permissions.WRITE) == "Permissions.READ|WRITE"
assert str(Permissions.WRITE | Permissions.READ) == "Permissions.READ|WRITE"
assert (
    str(Permissions.WRITE | Permissions.READ | Permissions.EXECUTE)
    == "Permissions.READ|WRITE|EXECUTE"
)

# Assign 'permissions' to the (~) inverse (opposite) of EXECUTE,
# i.e. all Permissions options except EXECUTE
permissions = ~Permissions.EXECUTE

assert Permissions.READ in permissions
assert Permissions.WRITE in permissions
assert not Permissions.EXECUTE in permissions
assert Permissions.DELETE in permissions
assert str(permissions) == "Permissions.READ|WRITE|DELETE"
```

#### Example 17: Annotating Enumeration Option Values

```python
from enumerific import Enumeration, anno

# The 'anno' (annotation) class can be used to add annotations to enumeration options;
# these are arbitrary key-value pairs that can be used to hold any additional data that
# is useful to keep associated with the enumeration option; the annotation values are
# then accessible anywhere that the enumeration is, and can be accessed as attributes:
class Colors(Enumeration):
    RED = anno(1, rgb=(255, 0, 0), primary=True)
    GREEN = anno(2, rgb=(0, 255, 0), primary=True)
    BLUE = anno(3, rgb=(0, 0, 255), primary=True)
    PURPLE = anno(4, rgb=(255, 0, 255), primary=False)

assert "RED" in Colors
assert Colors.RED.name == "RED"
assert Colors.RED.value == 1
assert Colors.RED == 1
assert Colors.RED.rgb == (255, 0, 0)
assert Colors.RED.primary is True

assert "GREEN" in Colors
assert Colors.GREEN.name == "GREEN"
assert Colors.GREEN.value == 2
assert Colors.GREEN == 2
assert Colors.GREEN.rgb == (0, 255, 0)
assert Colors.GREEN.primary is True

assert "BLUE" in Colors
assert Colors.BLUE.name == "BLUE"
assert Colors.BLUE.value == 3
assert Colors.BLUE == 3
assert Colors.BLUE.rgb == (0, 0, 255)
assert Colors.BLUE.primary is True

assert "PURPLE" in Colors
assert Colors.PURPLE.name == "PURPLE"
assert Colors.PURPLE.value == 4
assert Colors.PURPLE == 4
assert Colors.PURPLE.rgb == (255, 0, 255)
assert Colors.PURPLE.primary is False
```

#### Example 18: Annotating Enumeration Option Values with Automatic Sequencing

```python
from enumerific import Enumeration, auto

# The 'auto' (automatic) class can be used to generate unique numeric sequence numbers
# for enumeration options and to optionally add annotations to those same options; the
# annotation key-value pairs can be used to hold any additional data that is useful to
# keep associated with the enumeration option; the annotation values are then accessible
# anywhere that the enumeration is, and can be accessed as attributes:
class Colors(Enumeration):
    RED = auto(rgb=(255, 0, 0), primary=True)
    GREEN = auto(rgb=(0, 255, 0), primary=True)
    BLUE = auto(rgb=(0, 0, 255), primary=True)
    PURPLE = auto(rgb=(255, 0, 255), primary=False)

assert "RED" in Colors
assert Colors.RED.name == "RED"
assert Colors.RED.value == 1
assert Colors.RED == 1
assert Colors.RED.rgb == (255, 0, 0)
assert Colors.RED.primary is True

assert "GREEN" in Colors
assert Colors.GREEN.name == "GREEN"
assert Colors.GREEN.value == 2
assert Colors.GREEN == 2
assert Colors.GREEN.rgb == (0, 255, 0)
assert Colors.GREEN.primary is True

assert "BLUE" in Colors
assert Colors.BLUE.name == "BLUE"
assert Colors.BLUE.value == 3
assert Colors.BLUE == 3
assert Colors.BLUE.rgb == (0, 0, 255)
assert Colors.BLUE.primary is True

assert "PURPLE" in Colors
assert Colors.PURPLE.name == "PURPLE"
assert Colors.PURPLE.value == 4
assert Colors.PURPLE == 4
assert Colors.PURPLE.rgb == (255, 0, 255)
assert Colors.PURPLE.primary is False
```

# Enumerific Library Enumerations: Classes & Methods

The Enumerific library's `Enumeration` class is a greenfield implementation of enumerations
and does not inherit from any of the standard library enumeration classes, but offers equivalent
and extended functionality implemented from scratch. Enumerific library enumerations can be used
in any situation that enumerations are needed, and can replace the use of standard library
enumerations in almost every case unless some very specific functionality or underlying behaviour
of standard library enumerations are relied upon in user code. For the majority of cases, the
functionality is sufficiently equivalent from an application binary interface (ABI) perspective
that the two implementations can be used interchangeably.

The Enumerific library's extended enumerations module offers the following classes:

 * `EnumerationConfiguration` – The `EnumerationConfiguration` class is used internally by the library
 to hold configuration information for an `Enumeration` class instance.

 * `EnumerationMetaClass` – The `EnumerationMetaClass` metaclass is responsible for creating instances of the `Enumeration` class for use, and provides an interface between the class definition and some of the special behaviours needed to facilitate enumerations, such as each enumeration option being an instance of the enumeration class.

 * `Enumeration` – The `Enumeration` class is the base class for all Enumerific library extended enumerations; the `Enumeration` class defines shared functionality used by all `Enumeration` class instances.

 * `EnumerationType` – The `EnumerationType` class is actually a subclass of `Enumeration` and is used internally by the library to track the data type of the options assigned to an enumeration class.

 * `EnumerationInteger` – The `EnumerationInteger` class is a subclass of `int` and `Enumeration` and supports interacting with enumeration options natively as `int` (integer) data types.

 * `EnumerationFloat` – The `EnumerationFloat` class is a subclass of `float` and `Enumeration` and supports interacting with enumeration options natively as `float` (floating point) data types.

 * `EnumerationComplex` – The `EnumerationComplex` class is a subclass of `complex` and `Enumeration` and supports interacting with enumeration options natively as `complex` (complex number) data types.

 * `EnumerationBytes` – The `EnumerationBytes` class is a subclass of `bytes` and `Enumeration` and supports interacting with enumeration options natively as `bytes` data types.

 * `EnumerationString` – The `EnumerationString` class is a subclass of `str` and `Enumeration` and supports interacting with enumeration options natively as `str` (string) data types.

 * `EnumerationTuple` – The `EnumerationTuple` class is a subclass of `tuple` and `Enumeration` and supports interacting with enumeration options natively as `tuple` data types.

 * `EnumerationSet` – The `EnumerationSet` class is a subclass of `set` and `Enumeration` and supports interacting with enumeration options natively as `set` data types.

 * `EnumerationList` – The `EnumerationList` class is a subclass of `list` and `Enumeration` and supports interacting with enumeration options natively as `list` data types.

 * `EnumerationDictionary` – The `EnumerationDictionary` class is a subclass of `dict` and `Enumeration` and supports interacting with enumeration options natively as `dict` (dictionary) data types.

 * `EnumerationFlag` – The `EnumerationFlag` class is a special subclass of `int` and `Enumeration` and supports interacting with enumeration options natively as `int` (integer) data types and supports bitwise operations on the enumeration options so that enumeration options can be used as bitwise flags.

The extended enumerations module also offers the following classes for annotating enumeration
options and for automatically generating sequence numbers for annotation options:

 * `anno` – The `anno` class provides support for annotating an enumeration option's value, allowing an enumeration option to carry both a value of any data type, and optional additional annotations of key-value pairs that can be accessed as properties on the annotated enumeration option.
 
 * `auto` – The `auto` class is a subclass of `anno` and provides support both for annotating and enumeration option's value as per the functionality supported by its superclass, and additionally provides support for automatically generating unique number sequences to use for enumeration options, obviating the need to manually assign unique values to each enumeration option; number sequences can be configured to suit a range of needs, including generating number sequences as powers of two, which is particularly useful for the enumeration of bitwise flags as supported by the `EnumerationFlag` subclass.

# Standard Library Enumerations: Classes & Methods

The Enumerific library's own `Enum` class is a subclass of the built-in `enum.Enum` class,
so all of the built-in functionality of `enum.Enum` is available, as well as several additional class methods:

* `reconcile(value: object, default: Enum = None, raises: bool = False)` (`Enum`) – The `reconcile()` method allows for an enumeration's value or an enumeration option's name to be reconciled against a matching enumeration option. If the provided value can be matched against one of the enumeration's available options, that option will be returned, otherwise there are two possible behaviours: if the `raises` keyword argument has been set to or left as `False` (its default), the value assigned to the `default` keyword argument will be returned, which may be `None` if no default value has been specified; if the `raises` argument has been set to `True` an `EnumValueError` exception will be raised as an alert that the provided value could not be matched. One can also provide an enumeration option as the input value to the `reconcile` method, and these will be validated and returned as-is.

* `validate(value: object)` (`bool`) – The `validate()` method takes the same range of input values as the `reconcile` method, and returns `True` when the provided value can be reconciled against an enumeration option, or `False` otherwise.

* `options()` (`list[Enum]`) – The `options()` method provides easy access to the list of the enumeration's available options.

The benefits of being able to validate and reconcile various input values against an enumeration, include allowing for a controlled vocabulary of options to be checked against, and the ability to convert enumeration values into their corresponding enumeration option. This can be especially useful when working with input data where you need to convert those values to their corresponding enumeration options, and to be able to do so without maintaining boilerplate code to perform the matching and assignment.

To make use of the extra functionality for the standard library's `Enum` class, import the `Enum` class from the Enumerific library:

```python
from enumerific import Enum

class Colors(Enum):
  RED = 1
  GREEN = 2

val = Colors.RED
```

You can also import the `Enum` class directly from the `enumerific` library and use it directly:

```python
from enumerific import Enum

class Colors(Enum):
  RED = 1
```

Some examples of use include the following code samples, where each make use of the example `Colors` class, defined as follows:

```python
from enumerific import Enum

class Colors(Enum):
  RED = 1
  GREEN = 2
```

#### Example 1: Reconciling a Value

```python
from enumerific import Enum

class Colors(Enum):
  RED = 1
  GREEN = 2

# Given a string value in this case
value = 1

# Reconcile it to the associated enumeration option
color = Colors.reconcile(value)

assert color == Colors.RED  # asserts successfully
assert color is Colors.RED  # asserts successfully as enums are singletons
```

#### Example 2: Reconciling an Enumeration Option Name

```python
from enumerific import Enum

class Colors(Enum):
  RED = 1
  GREEN = 2

# Given a string value in this case
value = "GREEN"

# Reconcile it to the associated enumeration option
color = Colors.reconcile(value)

assert color == Colors.GREEN  # asserts successfully
assert color is Colors.GREEN  # asserts successfully as enums are singletons
```

#### Example 3: Validating a Value

```python
from enumerific import Enum

class Colors(Enum):
  RED = 1
  GREEN = 2

# The value can be an enumeration option's name, its value, or the enumeration option
value = "RED"
value = 1
value = Colors.RED

if Colors.validate(value) is True:
    # do something if the value could be validated
    pass
else:
    # do something else if the value could not be validated
    pass
```

#### Example 4: Iterating Over Enumeration Options

```python
from enumerific import Enum

class Colors(Enum):
  RED = 1
  GREEN = 2

for option in Colors.options():
    # do something with each option
    print(option.name, option.value)
```

### Unit Tests

The Enumerific library includes a suite of comprehensive unit tests which ensure that the
library functionality operates as expected. The unit tests were developed with and are run via `pytest`.

To ensure that the unit tests are run within a predictable runtime environment where all of the necessary dependencies are available, a [Docker](https://www.docker.com) image is created within which the tests are run. To run the unit tests, ensure Docker and Docker Compose is [installed](https://docs.docker.com/engine/install/), and perform the following commands, which will build the Docker image via `docker compose build` and then run the tests via `docker compose run` – the output of running the tests will be displayed:

```shell
$ docker compose build
$ docker compose run tests
```

To run the unit tests with optional command line arguments being passed to `pytest`, append the relevant arguments to the `docker compose run tests` command, as follows, for example passing `-vv` to enable verbose output:

```shell
$ docker compose run tests -vv
```

See the documentation for [PyTest](https://docs.pytest.org/en/latest/) regarding available optional command line arguments.

### Copyright & License Information

Copyright © 2024–2025 Daniel Sissman; licensed under the MIT License.