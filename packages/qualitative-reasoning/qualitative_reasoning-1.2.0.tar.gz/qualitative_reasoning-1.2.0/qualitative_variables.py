"""
Qualitative Variables for Qualitative Physics
"""

from typing import Dict, List, Any, Optional
from enum import Enum
import numpy as np


class VariableType(Enum):
    """Types of qualitative variables"""
    QUANTITY = "quantity"
    DERIVATIVE = "derivative" 
    LANDMARK = "landmark"
    INTERVAL = "interval"


class QualitativeValue(Enum):
    """Qualitative values for variables"""
    NEGATIVE = -1
    ZERO = 0
    POSITIVE = 1
    UNKNOWN = "unknown"
    INCREASING = "inc"
    DECREASING = "dec"
    STEADY = "std"


class QualitativeVariable:
    """Represents a qualitative variable in the physics simulation"""
    
    def __init__(self, name: str, variable_type: VariableType, 
                 value: QualitativeValue = QualitativeValue.UNKNOWN):
        self.name = name
        self.variable_type = variable_type
        self.value = value
        self.constraints = []
        
    def set_value(self, value: QualitativeValue):
        """Set the qualitative value"""
        self.value = value
        
    def add_constraint(self, constraint):
        """Add a constraint involving this variable"""
        self.constraints.append(constraint)
        
    def __str__(self):
        return f"{self.name}: {self.value}"
        
    def __repr__(self):
        return f"QualitativeVariable('{self.name}', {self.variable_type}, {self.value})"