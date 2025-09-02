#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module for a summing block.
"""

import pyingraph
import ast
import json

class Summer(pyingraph.BlockBase):
    """
    A block that computes a scaled sum of its inputs.
    """
    def __init__(self):
        super().__init__()
        self.attrNamesArr = ['scales']
        self._inputs = []
        self.scales = []  # Initialize scales list
    
    def read_parameters(self, params: dict) -> None:
        """
        Override to ensure scales are properly converted to numbers.
        """
        super().read_parameters(params)
        # Ensure scales are converted to numbers
        if hasattr(self, 'scales') and self.scales is not None:
            try:
                # If scales is a string representation of a list, parse it first
                if isinstance(self.scales, str):
                    try:
                        # Try JSON parsing first
                        self.scales = json.loads(self.scales)
                    except json.JSONDecodeError:
                        try:
                            # Fallback to ast.literal_eval for Python literal syntax
                            self.scales = ast.literal_eval(self.scales)
                        except (ValueError, SyntaxError):
                            print(f"Warning: Could not parse scales string '{self.scales}', using empty list")
                            self.scales = []
                            return
                
                # Convert all elements to float
                if isinstance(self.scales, list):
                    self.scales = [float(scale) for scale in self.scales]
                else:
                    # If it's a single value, convert to list
                    self.scales = [float(self.scales)]
                    
            except (ValueError, TypeError) as e:
                print(f"Warning: Could not convert scales '{self.scales}' to numbers: {e}, using empty list")
                self.scales = []

    def read_inputs(self, inputs: list) -> None:
        """Reads and stores the input values, ensuring they are converted to numbers."""
        # Convert all inputs to float, handling None values
        self._inputs = []
        for input_item in inputs:
            if input_item is None:
                self._inputs.append(0.0)
            else:
                try:
                    self._inputs.append(float(input_item))
                except (ValueError, TypeError):
                    print(f"Warning: Could not convert input '{input_item}' to number, using 0.0")
                    self._inputs.append(0.0)

    def compute_outputs(self, time: float) -> list:
        """Computes the scaled sum of the inputs."""
        if not hasattr(self, 'scales') or not self._inputs:
            return [0.0]

        if len(self.scales) != len(self._inputs):
            raise ValueError("Length of scales and inputs must be the same.")

        # Input conversion is now handled in read_inputs method
        scaled_inputs = [i * s for i, s in zip(self._inputs, self.scales)]
        total_sum = sum(scaled_inputs)
        return [total_sum]

    def reset(self) -> None:
        """Resets the internal state of the block."""
        self._inputs = []

# Example usage
if __name__ == "__main__":
    summer_block = Summer()
    
    # Set parameters
    params = {'scales': [0.5, 1.0, -2.0]}
    summer_block.read_parameters(params)
    
    # Provide inputs
    inputs = [10, 20, 5]
    summer_block.read_inputs(inputs)
    
    # Compute output
    output = summer_block.compute_outputs(time=0)
    print(f"Inputs: {inputs}")
    print(f"Scales: {summer_block.scales}")
    print(f"Computed Output: {output}") # Expected: (10*0.5) + (20*1.0) + (5*-2.0) = 5 + 20 - 10 = 15