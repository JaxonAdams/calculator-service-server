import pytest

from services.calculator_service import CalculatorService


@pytest.fixture
def calculator():
    return CalculatorService()


def test_run_unknown_operation(calculator):
    with pytest.raises(NotImplementedError):
        calculator.calculate(99, [])


def test_addition(calculator):
    # assumed addition has key/ID 1

    simple_res = calculator.calculate(1, [2, 2])
    assert simple_res == 4

    many_operands_res = calculator.calculate(1, [0.1] * 100)
    assert many_operands_res == 10.0

    one_operand_res = calculator.calculate(1, [1])
    assert one_operand_res == 1

    mixed_num_types = calculator.calculate(1, [3, 7.6, -3])
    assert mixed_num_types == 7.6

    no_args = calculator.calculate(1, [])
    assert no_args == 0


def test_addition_errors(calculator):
    # assumed addition has key/ID 1

    with pytest.raises(ValueError):
        calculator.calculate(1, [7, "banana"])
        calculator.calculate(1, ["ape"])
