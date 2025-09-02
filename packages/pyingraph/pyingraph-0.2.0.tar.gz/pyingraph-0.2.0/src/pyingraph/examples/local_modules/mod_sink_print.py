from pyingraph import BlockBase

class SinkPrint(BlockBase):
    """
    A print sink block that prints all inputs it receives.
    This is useful for debugging and monitoring data flow in the graph.
    """
    
    def __init__(self):
        super().__init__()
        self.attrNamesArr = []  # No parameters needed
        self.inputs_received = None
    
    def read_inputs(self, inputs: list) -> None:
        """
        Store the inputs for printing.
        
        :param inputs: List of input values to be printed
        """
        self.inputs_received = inputs
    
    def compute_outputs(self, time: float = None) -> list:
        """
        Print the received inputs and return empty list (sink has no outputs).
        
        :param time: Current simulation time
        :return: Empty list (sinks don't produce outputs)
        """
        if self.inputs_received is not None:
            if time is not None:
                print(f"[t={time:.3f}] SinkPrint received: {self.inputs_received}")
            else:
                print(f"SinkPrint received: {self.inputs_received}")
        else:
            print("SinkPrint: No inputs received")
        
        return []  # Sink blocks typically don't produce outputs
    
    def reset(self) -> None:
        """
        No internal state to reset for print sink.
        """
        self.inputs_received = None

# Test code
if __name__ == "__main__":
    # Create instance
    print_sink = SinkPrint()
    
    # No parameters needed for this block
    params = {}
    print_sink.read_parameters(params)
    
    print("Testing SinkPrint:")
    
    # Test with single input
    print_sink.read_inputs([3.14])
    print_sink.compute_outputs(time=0.0)
    
    # Test with multiple inputs
    print_sink.read_inputs([1.0, 2.0, 3.0])
    print_sink.compute_outputs(time=1.0)
    
    # Test with different data types
    print_sink.read_inputs(["hello", 42, True])
    print_sink.compute_outputs(time=2.0)
    
    # Test reset
    print_sink.reset()
    print_sink.compute_outputs(time=3.0)
    
    # Test without time parameter
    print_sink.read_inputs([99.9])
    print_sink.compute_outputs()