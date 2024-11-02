import math
from functools import reduce


# TODO: WRITE SOME UNIT TESTS FOR ME
class CalculatorService:

    def __init__(self):

        # HEY DEVELOPERS -- IF YOU ADD A NEW OPERATION, ADD IT TO THE MAP
        # otherwise it will not be accessible via the API
        self.operation_map = {
            1: self._add,
            2: self._subtract,
            3: self._multiply,
            4: self._divide,
            5: self._sqrt,
            6: self._random_string,
        }

    def _add(self, *args):

        if not all(isinstance(arg, int) or isinstance(arg, float) for arg in args):
            raise ValueError("'Addition' operation accepts only number-type operands.")

        return sum(args)

    def _subtract(self, *args):

        if not all(isinstance(arg, int) or isinstance(arg, float) for arg in args):
            raise ValueError("'Subtraction' operation accepts only number-type operands.")

        return reduce(lambda a, b: a - b, args)

    def _multiply(self, *args):

        if not all(isinstance(arg, int) or isinstance(arg, float) for arg in args):
            raise ValueError("'Multiplication' operation accepts only number-type operands.")

        return reduce(lambda a, b: a * b, args)

    def _divide(self, *args):

        if not all(isinstance(arg, int) or isinstance(arg, float) for arg in args):
            raise ValueError("'Division' operation accepts only number-type operands.")

        return reduce(lambda a, b: a / b, args)

    def _sqrt(self, *args):

        if len(args) != 1:
            raise ValueError("'Square Root' operation accepts only a single operand.")

        if not (isinstance(args[0], int) or isinstance(args[0], float)):
            raise ValueError("'Square Root' operand must be a number.")

        return math.sqrt(args[0])

    def _random_string(self, *args):
        
        raise NotImplementedError("Operation 'random_string' not yet implemented")

    def calculate(self, operation_key: int, operands: list):

        if operation_key not in self.operation_map:
            raise NotImplementedError(
                f"Operation with ID '{operation_key}' not yet implemented"
            )

        return self.operation_map[operation_key](*operands)
        
