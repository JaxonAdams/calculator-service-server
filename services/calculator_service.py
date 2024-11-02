class CalculatorService():

    def __init__(self):

        self.operation_map = {
            1: self._add,
        }

    def _add(self, *args):

        if not all(isinstance(arg, int) for arg in args):
            raise ValueError("'Add' operation accepts only integer operands.")

        return sum(args)

    def calculate(self, operation_key: int, operands: list):

        if operation_key not in self.operation_map:
            raise NotImplementedError(
                f"Operation with ID '{operation_key}' not yet implemented"
            )

        return self.operation_map[operation_key](*operands)
        
