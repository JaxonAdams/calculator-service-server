import math
from functools import reduce

import requests


class CalculatorService:
    """The core calculator service that performs various operations."""

    def __init__(self):

        # HEY DEVELOPERS -- IF YOU ADD A NEW OPERATION, ADD IT TO THE MAP!
        # Otherwise it will not be accessible via the API
        self.operation_map = {
            1: self._add,
            2: self._subtract,
            3: self._multiply,
            4: self._divide,
            5: self._sqrt,
            6: self._random_string,
        }

        self.operation_options = {
            1: self._add_options,
            2: self._subtract_options,
            3: self._multiply_options,
            4: self._divide_options,
            5: self._sqrt_options,
            6: self._random_string_options,
        }

    def _add(self, *args):
        """Add any number of operands together."""

        if not all(isinstance(arg, int) or isinstance(arg, float) for arg in args):
            raise ValueError("'Addition' operation accepts only number-type operands.")

        return sum(args)
    
    def _add_options(self):
        """Return the options/settings for the 'Addition' operation."""

        return {
            "operand_type": "number",
            "operand_count": "variable",
            "description": "Add any number of operands together.",
        }

    def _subtract(self, *args):
        """Subtract any number of operands from the first operand."""

        if not all(isinstance(arg, int) or isinstance(arg, float) for arg in args):
            raise ValueError(
                "'Subtraction' operation accepts only number-type operands."
            )

        return reduce(lambda a, b: a - b, args)
    
    def _subtract_options(self):
        """Return the options/settings for the 'Subtraction' operation."""

        return {
            "operand_type": "number",
            "operand_count": "variable",
            "description": "Subtract any number of operands from the first operand.",
        }

    def _multiply(self, *args):
        """Multiply any number of operands together."""

        if not all(isinstance(arg, int) or isinstance(arg, float) for arg in args):
            raise ValueError(
                "'Multiplication' operation accepts only number-type operands."
            )

        return reduce(lambda a, b: a * b, args)
    
    def _multiply_options(self):
        """Return the options/settings for the 'Multiplication' operation."""

        return {
            "operand_type": "number",
            "operand_count": "variable",
            "description": "Multiply any number of operands together.",
        }

    def _divide(self, *args):
        """Divide the first operand by all subsequent operands."""

        if not all(isinstance(arg, int) or isinstance(arg, float) for arg in args):
            raise ValueError("'Division' operation accepts only number-type operands.")

        return reduce(lambda a, b: a / b, args)
    
    def _divide_options(self):
        """Return the options/settings for the 'Division' operation."""

        return {
            "operand_type": "number",
            "operand_count": "variable",
            "description": "Divide the first operand by all subsequent operands.",
        }

    def _sqrt(self, *args):
        """Calculate the square root of the operand."""

        if len(args) != 1:
            raise ValueError("'Square Root' operation accepts only a single operand.")

        if not (isinstance(args[0], int) or isinstance(args[0], float)):
            raise ValueError("'Square Root' operand must be a number.")

        return math.sqrt(args[0])
    
    def _sqrt_options(self):
        """Return the options/settings for the 'Square Root' operation."""

        return {
            "operand_type": "number",
            "operand_count": 1,
            "description": "Calculate the square root of the operand.",
        }

    def _random_string(self, *args):
        """Generate a random string based on the provided options.
        
        Random string generation is powered by a light integration to
        the random.org API. The API is used to generate a single random
        string based on the provided options.
        """

        # Validate the request input
        if len(args) != 1 or not isinstance(args[0], dict):
            raise ValueError(
                "'Random String' accepts a single operand, a dictionary of options."
            )

        # Extract the options from the request
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

        # Generate the random string using the random.org API
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

        # Make the API request and check for errors
        result = requests.get(vendor_url, params=params)
        if "Error:" in result.text:
            raise ValueError(result.text.split(":")[1].strip())

        return result.text.strip()
    
    def _random_string_options(self):
        """Return the options/settings for the 'Random String' operation."""
            
        return {
            "operand_type": "dictionary",
            "operand_count": 1,
            "description": "Generate a random string based on the provided options.",
            "options": {
                "string_length": {
                    "type": "int",
                    "description": "The length of the random string to generate.",
                },
                "include_digits": {
                    "type": "bool",
                    "description": "Include digits (0-9) in the random string.",
                },
                "include_uppercase_letters": {
                    "type": "bool",
                    "description": "Include uppercase letters (A-Z) in the random string.",
                },
                "include_lowercase_letters": {
                    "type": "bool",
                    "description": "Include lowercase letters (a-z) in the random string.",
                },
            },
        }

    def calculate(self, operation_key: int, operands: list):
        """Perform the requested calculation based on the provided operation key and operands."""

        if operation_key not in self.operation_map:
            raise NotImplementedError(
                f"Operation with ID '{operation_key}' not yet implemented"
            )

        return self.operation_map[operation_key](*operands)
    
    def get_operation_options(self, operation_key: int):
        """Return the options/settings for the requested operation."""

        if operation_key not in self.operation_options:
            raise NotImplementedError(
                f"Operation with ID '{operation_key}' not yet implemented"
            )

        return self.operation_options[operation_key]()


if __name__ == "__main__":
    # Use this branch to test the calculator service locally

    calc = CalculatorService()

    random_str_opts = {
        "string_length": 32,
        "include_digits": True,
        "include_uppercase_letters": True,
        "include_lowercase_letters": False,
    }

    print(calc.calculate(6, [random_str_opts]))
