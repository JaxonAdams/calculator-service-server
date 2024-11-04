import math
from functools import reduce

import requests


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
            raise ValueError(
                "'Subtraction' operation accepts only number-type operands."
            )

        return reduce(lambda a, b: a - b, args)

    def _multiply(self, *args):

        if not all(isinstance(arg, int) or isinstance(arg, float) for arg in args):
            raise ValueError(
                "'Multiplication' operation accepts only number-type operands."
            )

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

        if len(args) != 1 or not isinstance(args[0], dict):
            raise ValueError(
                "'Random String' accepts a single operand, a dictionary of options."
            )

        opts = args[0]
        try:
            string_len = opts["string_length"]
            include_digits = opts["include_digits"]
            include_uppercase_letters = opts["include_uppercase_letters"]
            include_lowercase_letters = opts["include_lowercase_letters"]
        except KeyError as e:
            raise ValueError(
                f"Field {e} is required in the settings dictionary (first operand)."
            )

        vendor_url = "https://www.random.org/strings"
        params = {
            "num": 1,
            "len": string_len,
            "digits": "on" if include_digits else "off",
            "upperalpha": "on" if include_uppercase_letters else "off",
            "loweralpha": "on" if include_lowercase_letters else "off",
            "unique": "on",
            "format": "plain",
            "rnd": "new",
        }

        result = requests.get(vendor_url, params=params)
        if "Error:" in result.text:
            raise ValueError(result.text.split(":")[1].strip())

        return result.text.strip().split("\n")

    def calculate(self, operation_key: int, operands: list):

        if operation_key not in self.operation_map:
            raise NotImplementedError(
                f"Operation with ID '{operation_key}' not yet implemented"
            )

        return self.operation_map[operation_key](*operands)


if __name__ == "__main__":
    calc = CalculatorService()

    random_str_opts = {
        "string_length": 32,
        "include_digits": True,
        "include_uppercase_letters": True,
        "include_lowercase_letters": False,
    }

    print(calc.calculate(6, [random_str_opts]))
