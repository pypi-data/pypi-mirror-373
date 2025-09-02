# 🐷 PyG interface 🐽 class for defining blocks

from abc import ABC, abstractmethod
import threading

# base class for PyG blocks
class BlockBase(ABC):
    """
    Block base class
    """
    @abstractmethod
    def __init__(self):
        self.attrNamesArr = []  # New attribute name array for storing attribute names
    
    # instance method for loading attributes to instance
    def read_parameters(self, parDict: dict) -> None:
        """Reads parameters from the model parameters file."""
        """
        Read parameter values from parDict
        :param parDict: Parameter dictionary
        :raises: KeyError if required parameters are missing
        """
        # check if the required attrNamesArr are missing in the graph json file
        for attr_name in self.attrNamesArr:
            if attr_name not in parDict:
                raise KeyError(f"Missing required parameter: {attr_name}")
        
        # 2025-07-03 14:42:16
        # Allows additional parameters in parList
        # to be loaded as class members.
        # for the key-value pairs in the parDict, copy them to
        # the class members
        for key, value in parDict.items():
            setattr(self, key, value)

        # for attr_name in self.attrNamesArr:
        #     if attr_name not in parDict:
        #         raise KeyError(f"Missing required parameter: {attr_name}")
        #     # setattr(self, attr_name, parDict[attr_name])
    
    @abstractmethod
    def read_inputs(self, inputs: list) -> None:
        """Read inputs to the block, 
        report errors if inputs are not valid.
        Even for blocks without inputs, this method
        is expected, even with a simple pass."""
        raise NotImplementedError("Subclasses must implement read_inputs()")
        
    @abstractmethod
    def compute_outputs(self, time: float) -> list:
        """
        Compute outputs, receives time parameter
        :param time: Current time
        :return: Output list
        """
        raise NotImplementedError("Subclasses must implement compute_outputs()")

    @abstractmethod
    def reset(self) -> None:
        """Reset internal states of the block.
         optional method, as some blocks may not need internal states"""
        pass

################ model coder part ####################
class MySampleBlock(BlockBase):
    
    def __init__(self):
        super().__init__()
        self.state = 0
        self.attrNamesArr = ["par1", "par2"]

    def read_inputs(self, inputs: list) -> None:
        if len(inputs) != 2: # check input validity
            raise ValueError("Inputs must be two numbers")
        self.input1 = inputs[0]
        self.input2 = inputs[1]
        
    def compute_outputs(self, time = None) -> list:
        self.state += 1 # internal states are allowed, and used here as an example
        self.outputs = [self.input1+self.input2, self.par1 + self.par2 + self.state]
        return self.outputs

    def reset(self) -> None:
        self.state = 0

# test code
if __name__ == "__main__":
    myBlock = MySampleBlock()
    parDict = {
        "par1": 1,
        "par2": 2,
        "parX": 'x'
    }
    myBlock.read_parameters(parDict)
    
    inputs = [3,4]
    myBlock.read_inputs(inputs)
    outputs = myBlock.compute_outputs() # time is not required for this block
    for _ in range(5): # internal states are allowed, and used here as an example
        outputs = myBlock.compute_outputs()
        print(outputs)
    
    myBlock.reset()
    outputs = myBlock.compute_outputs() # time is not required for this block
    print(outputs)