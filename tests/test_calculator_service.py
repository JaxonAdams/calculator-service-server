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


def test_subtraction(calculator):
    # assumed subtraction has key/ID 2

    simple_res = calculator.calculate(2, [4, 3])
    assert simple_res == 1

    many_operands_res = calculator.calculate(2, [100] + ([1] * 100))
    assert many_operands_res == 0

    one_operand_res = calculator.calculate(2, [1])
    assert one_operand_res == 1

    mixed_num_types = calculator.calculate(2, [10, 2.5, -1])
    assert mixed_num_types == 8.5


def test_subtraction_errors(calculator):
    # assumed subtraction has key/ID 2

    with pytest.raises(TypeError):
        calculator.calculate(2, [])

    with pytest.raises(ValueError):
        calculator.calculate(2, [4, "Three", "banana"])
        calculator.calculate(2, ["hello"])


def test_multiplication(calculator):
    # assumed multiplication has key/ID 3

    simple_res = calculator.calculate(3, [3, 4])
    assert simple_res == 12

    many_operands_res = calculator.calculate(3, [2] * 6)
    assert many_operands_res == 64

    one_operand_res = calculator.calculate(3, [7])
    assert one_operand_res == 7

    mixed_num_types = calculator.calculate(3, [10, 0.1, -1])
    assert mixed_num_types == -1


def test_multiplication_errors(calculator):
    # assumed multiplication has key/ID 3

    with pytest.raises(TypeError):
        calculator.calculate(3, [])

    with pytest.raises(ValueError):
        calculator.calculate(3, [4, "Three", "banana"])
        calculator.calculate(3, ["hello"])


def test_division(calculator):
    # assumed division has key/ID 4

    simple_res = calculator.calculate(4, [100, 10])
    assert simple_res == 10

    many_operands_res = calculator.calculate(4, [100, 10, 10, 10])
    assert many_operands_res == 0.1

    one_operand_res = calculator.calculate(4, [7])
    assert one_operand_res == 7

    mixed_num_types = calculator.calculate(4, [10, 0.1, -1])
    assert mixed_num_types == -100


def test_division_errors(calculator):
    # assumed division has key/ID 4

    with pytest.raises(ZeroDivisionError):
        calculator.calculate(4, [10, 0])
        calculator.calculate(4, [100, 10, 0, 23])

    with pytest.raises(TypeError):
        calculator.calculate(4, [])

    with pytest.raises(ValueError):
        calculator.calculate(4, [100, "Ten", "banana"])
        calculator.calculate(4, ["hello"])


def test_square_root(calculator):
    # assumed square root has key/ID 5

    simple_res = calculator.calculate(5, [16])
    assert simple_res == 4

    another_res = calculator.calculate(5, [16.0])
    assert simple_res == 4.0


def test_square_root_errors(calculator):
    # assumed square root has key/ID 5

    with pytest.raises(ValueError):
        calculator.calculate(5, [16, 9])
        calculator.calculate(5, ["rutabega"])
        calculator.calculate(5, [-9])
