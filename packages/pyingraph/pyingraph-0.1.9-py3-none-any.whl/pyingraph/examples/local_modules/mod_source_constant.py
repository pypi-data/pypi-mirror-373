from pyingraph import BlockBase

class ConstantSource(BlockBase):
    """
    A constant source block that outputs a user-specified constant value.
    """
    
    def __init__(self):
        super().__init__()
        self.attrNamesArr = ["value"]  # Parameter name for the constant value
        self.value = 0.0  # Default value
    
    def read_parameters(self, params: dict) -> None:
        """
        Override to ensure value is properly converted to a number.
        """
        super().read_parameters(params)
        # Ensure value is converted to a number
        if hasattr(self, 'value'):
            try:
                self.value = float(self.value)
            except (ValueError, TypeError):
                print(f"Warning: Could not convert value '{self.value}' to number, using 0.0")
                self.value = 0.0
    
    def read_inputs(self, inputs: list) -> None:
        """
        Constant source doesn't need inputs, but method is required by BlockBase.
        """
        # No inputs needed for constant source
        pass
    
    def compute_outputs(self, time: float = None) -> list:
        """
        Return the constant value as output.
        
        :param time: Current simulation time (not used for constant source)
        :return: List containing the constant value
        """
        return [self.value]
    
    def reset(self) -> None:
        """
        No internal state to reset for constant source.
        """
        pass

# Test code
if __name__ == "__main__":
    # Create instance
    constant_block = ConstantSource()
    
    # Set parameter
    params = {"value": 3.14}
    constant_block.read_parameters(params)
    
    output = constant_block.compute_outputs(time=0.0)
    print(f"Output = {output}")