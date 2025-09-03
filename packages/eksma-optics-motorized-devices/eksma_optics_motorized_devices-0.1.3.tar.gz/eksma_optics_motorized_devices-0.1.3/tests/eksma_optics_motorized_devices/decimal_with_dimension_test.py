import pytest
from eksma_optics_motorized_devices.decimal_with_dimension import DecimalWithDimension


def test_from_string_valid() -> None:
    value_with_dimension = DecimalWithDimension.from_string("123cm")
    assert value_with_dimension.value == 123
    assert value_with_dimension.dimension == "cm"


def test_from_string_no_dimension() -> None:
    with pytest.raises(ValueError, match="invalid format: 123"):
        DecimalWithDimension.from_string("123")


def test_from_string_no_value() -> None:
    with pytest.raises(ValueError, match="invalid format: cm"):
        DecimalWithDimension.from_string("cm")


def test_str_representation() -> None:
    value_with_dimension = DecimalWithDimension(123, "cm")
    assert str(value_with_dimension) == "123cm"


def test_int_conversion() -> None:
    value_with_dimension = DecimalWithDimension(123, "cm")
    assert int(value_with_dimension) == 123


def test_float_conversion() -> None:
    value_with_dimension = DecimalWithDimension(123, "cm")
    assert float(value_with_dimension) == 123.0


def test_from_string_empty() -> None:
    with pytest.raises(ValueError, match="invalid format: "):
        DecimalWithDimension.from_string("")


def test_from_string_whitespace() -> None:
    with pytest.raises(ValueError, match="invalid format:  123cm "):
        DecimalWithDimension.from_string(" 123cm ")


def test_from_string_negative_value() -> None:
    with pytest.raises(ValueError, match="invalid format: -123cm"):
        DecimalWithDimension.from_string("-123cm")


def test_from_string_numeric_dimension() -> None:
    value_with_dimension = DecimalWithDimension.from_string("123m2")
    assert value_with_dimension.value == 123
    assert value_with_dimension.dimension == "m2"
