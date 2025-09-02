import pytest
import enum
import enumerific


def test_type(EnumSampleA, EnumSampleB):
    """Ensure that Enumerific `Enum` classes are valid `enum.Enum` and `enumerific.Enum`
    classes by checking their inheritance hierarchy conforms to that which is expected
    """

    assert issubclass(EnumSampleA, enum.Enum)
    assert issubclass(EnumSampleA, enumerific.Enum)
    assert issubclass(EnumSampleB, enum.Enum)
    assert issubclass(EnumSampleB, enumerific.Enum)


def test_type_equivalence(EnumSampleA, EnumSampleB):
    """Ensure that the sample Enumerific `Enum` subclasses conform to their expected equivalence"""

    assert EnumSampleA is EnumSampleA
    assert EnumSampleA is not EnumSampleB
    assert EnumSampleB is EnumSampleB
    assert EnumSampleB is not EnumSampleA


def test_reconciliation_success(EnumSampleA):
    """Ensure that the enumeration values reconcile to their expected enumeration options"""

    assert EnumSampleA.reconcile("Value1") is EnumSampleA.Value1
    assert EnumSampleA.reconcile("Value2") is EnumSampleA.Value2
    assert EnumSampleA.reconcile(3) is EnumSampleA.Value3
    assert EnumSampleA.reconcile(EnumSampleA.Value2) is EnumSampleA.Value2


def test_reconciliation_failure(EnumSampleA):
    """Ensure that the enumeration values reconcile to their expected enumeration options"""

    assert EnumSampleA.reconcile("Value3", default=None) is not EnumSampleA.Value1
    assert EnumSampleA.reconcile("123", default=None) is not EnumSampleA.Value1
    assert EnumSampleA.reconcile(123, default=None) is not EnumSampleA.Value1
    assert EnumSampleA.reconcile(True, default=None) is not EnumSampleA.Value1


def test_reconciliation_without_default_fallback_success(EnumSampleA):
    """Ensure that attempting to reconcile an invalid enumeration value, while providing
    no default fallback value results in an EnumValueError exception being raised"""

    assert EnumSampleA.reconcile(4, default=EnumSampleA.Value1) is EnumSampleA.Value1
    assert EnumSampleA.reconcile(4, default=EnumSampleA.Value2) is EnumSampleA.Value2
    assert EnumSampleA.reconcile(4, default=EnumSampleA.Value3) is EnumSampleA.Value3


def test_reconciliation_failure_with_raises_exception_disabled(EnumSampleA):
    """Ensure that attempting to reconcile an invalid enumeration value, while providing
    a None default fallback value results in a None value being returned"""

    # Note the default value for the 'raises' keyword argument is False (disabled)
    assert EnumSampleA.reconcile("Value4", default=None) is None


def test_reconciliation_failure_with_raises_exception_enabled(EnumSampleA):
    """Ensure that attempting to reconcile an invalid enumeration value, while calling
    the reconcile method with the raises=True argument raises the expected exception"""

    # Set the 'raises' keyword argument to False to prevent raising an exception; this
    # is the default behaviour for the reconcile function, but is used below for clarity
    assert EnumSampleA.reconcile("Value4", raises=False) is None

    with pytest.raises(enumerific.EnumValueError) as exception:
        # Set the 'raises' keyword argument to True to enable raising an exception; this
        # overrides the default exception behaviour, and must be specified to override
        assert EnumSampleA.reconcile("Value4", raises=True) is None

        assert (
            str(exception)
            == "EnumValueError: The provided value, 'Value4', is invalid and does not correspond with this enumeration's options!"
        )


def test_validation_success(EnumSampleA, EnumSampleB):
    """Ensure that values which correspond to enumeration options validate as True"""

    assert EnumSampleA.validate("Value1") is True
    assert EnumSampleA.validate("Value2") is True
    assert EnumSampleA.validate(3) is True
    assert EnumSampleA.validate(EnumSampleA.Value1) is True
    assert EnumSampleA.validate(EnumSampleA.Value2) is True
    assert EnumSampleA.validate(EnumSampleA.Value3) is True
    assert EnumSampleA.validate("Value4") is False

    assert EnumSampleB.validate("Value1") is True
    assert EnumSampleB.validate("Value2") is True
    assert EnumSampleB.validate("Value3") is True
    assert EnumSampleB.validate("Value4") is True


def test_validation_failure(EnumSampleA, EnumSampleB):
    """Ensure that values which do not correspond to enumeration options validate as False"""

    assert EnumSampleA.validate("Value4") is False
    assert EnumSampleA.validate(1234243) is False
    assert EnumSampleA.validate(EnumSampleB.Value1) is False


def test_iteration(EnumSampleA, EnumSampleB):
    """Ensure that iterating over the enumeration options produces the expected result"""

    options = {}

    for option in EnumSampleA.options():
        options[option.name] = option.value

    # EnumSampleA defined in conftest.py has three options
    assert len(options) == 3

    assert options == {
        "Value1": "value1",
        "Value2": "value2",
        "Value3": 3,
    }

    options = {}

    for option in EnumSampleB.options():
        options[option.name] = option.value

    # EnumSampleB defined in conftest.py has four options
    assert len(options) == 4

    assert options == {
        "Value1": "value1",
        "Value2": "value2",
        "Value3": 3,
        "Value4": 4.5678,
    }
