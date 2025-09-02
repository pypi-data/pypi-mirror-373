"""
Constraint Propagation for Qualitative Physics
"""

from typing import Dict, List, Any, Optional, Set
from enum import Enum
from abc import ABC, abstractmethod
import numpy as np

from .qualitative_variables import QualitativeVariable, QualitativeValue


class ConstraintType(Enum):
    """Types of qualitative constraints"""
    CORRESPONDENCE = "correspondence"     # M+(x) ∝ M+(y)
    SUM_CONSTRAINT = "sum"               # Σ inflows = Σ outflows  
    MONOTONIC = "monotonic"              # monotonic relationships
    DERIVATIVE = "derivative"            # x' = f(x)
    ALGEBRAIC = "algebraic"              # algebraic constraints


class QualitativeConstraint(ABC):
    """Abstract base class for qualitative constraints"""
    
    def __init__(self, constraint_type: ConstraintType, variables: List[QualitativeVariable]):
        self.constraint_type = constraint_type
        self.variables = variables
        self.active = True
        
    @abstractmethod
    def propagate(self) -> bool:
        """
        🔄 Propagate Constraint - de Kleer & Brown 1984 Implementation!
        
        Performs constraint propagation to reduce variable domains by enforcing
        the qualitative constraint relationship between variables.
        
        Returns:
            bool: True if any variable domains were modified, False otherwise
            
        📚 **Reference**: de Kleer, J., & Brown, J. S. (1984)
        "A qualitative physics based on confluences"
        
        ⚙️ **Propagation Algorithm**:
        1. Check current variable domains
        2. Apply constraint-specific filtering rules
        3. Remove inconsistent values from domains
        4. Return True if domains changed
        
        📊 **Efficiency**: O(d1 * d2) where d1, d2 are domain sizes
        """
        # Default implementation for constraint propagation
        # Subclasses should override for specific constraint types
        
        changed = False
        
        # Check if constraint involves these variables
        constraint_vars = [var.name for var in self.variables]
        
        # Basic domain filtering based on constraint type
        if self.constraint_type == ConstraintType.CORRESPONDENCE:
            # For correspondence: if one variable changes, other should change similarly
            if len(self.variables) >= 2:
                var1, var2 = self.variables[0], self.variables[1]
                
                # If var1 is increasing, constrain var2 to increasing
                if var1.value == QualitativeValue.INCREASING:
                    if QualitativeValue.DECREASING in var2.domain:
                        var2.domain.discard(QualitativeValue.DECREASING)
                        changed = True
                elif var1.value == QualitativeValue.DECREASING:
                    if QualitativeValue.INCREASING in var2.domain:
                        var2.domain.discard(QualitativeValue.INCREASING)
                        changed = True
                        
        elif self.constraint_type == ConstraintType.INFLUENCE:
            # For influence: causal relationships between variables
            if len(self.variables) >= 2:
                cause_var, effect_var = self.variables[0], self.variables[1]
                
                # If cause is zero, effect should be zero
                if cause_var.value == QualitativeValue.ZERO:
                    if QualitativeValue.INCREASING in effect_var.domain:
                        effect_var.domain.discard(QualitativeValue.INCREASING)
                        changed = True
                    if QualitativeValue.DECREASING in effect_var.domain:
                        effect_var.domain.discard(QualitativeValue.DECREASING)
                        changed = True
                        
        elif self.constraint_type == ConstraintType.PROPORTIONALITY:
            # For proportionality: variables change in same direction
            if len(self.variables) >= 2:
                var1, var2 = self.variables[0], self.variables[1]
                
                # Same direction constraints
                if var1.value == QualitativeValue.INCREASING:
                    if QualitativeValue.DECREASING in var2.domain:
                        var2.domain.discard(QualitativeValue.DECREASING)
                        changed = True
                elif var1.value == QualitativeValue.DECREASING:
                    if QualitativeValue.INCREASING in var2.domain:
                        var2.domain.discard(QualitativeValue.INCREASING)
                        changed = True
        
        return changed
        
    @abstractmethod
    def is_satisfied(self) -> bool:
        """
        ✅ Check if Constraint is Satisfied - Confluence Verification!
        
        Verifies whether the current variable assignments satisfy the
        qualitative constraint based on confluence theory.
        
        Returns:
            bool: True if constraint is satisfied, False otherwise
            
        🎯 **Satisfaction Criteria**:
        - All variable values are instantiated (not None)
        - Values respect the qualitative relationship
        - Constraint-specific conditions are met
        
        🗒️ **Usage in CSP**:
        ```python
        if constraint.is_satisfied():
            print("Constraint satisfied ✅")
        else:
            print("Constraint violated ❌ - backtrack!")
        ```
        """
        # Default implementation for constraint satisfaction checking
        # Subclasses should override for specific constraint types
        
        # Check if all variables have assigned values
        for var in self.variables:
            if var.value is None:
                return False  # Cannot be satisfied with unassigned variables
        
        # Check constraint-specific satisfaction conditions
        if self.constraint_type == ConstraintType.CORRESPONDENCE:
            if len(self.variables) >= 2:
                var1, var2 = self.variables[0], self.variables[1]
                # Correspondence satisfied if both variables change in same direction
                if var1.value == var2.value:
                    return True
                # Or if both are zero (no change)
                return (var1.value == QualitativeValue.ZERO and 
                       var2.value == QualitativeValue.ZERO)
                       
        elif self.constraint_type == ConstraintType.INFLUENCE:
            if len(self.variables) >= 2:
                cause_var, effect_var = self.variables[0], self.variables[1]
                # Influence satisfied if cause->effect relationship holds
                if cause_var.value == QualitativeValue.ZERO:
                    return effect_var.value == QualitativeValue.ZERO
                # Non-zero cause should have non-zero effect
                return effect_var.value != QualitativeValue.ZERO
                
        elif self.constraint_type == ConstraintType.PROPORTIONALITY:
            if len(self.variables) >= 2:
                var1, var2 = self.variables[0], self.variables[1]
                # Proportionality satisfied if variables change in same direction
                if var1.value == QualitativeValue.INCREASING:
                    return var2.value == QualitativeValue.INCREASING
                elif var1.value == QualitativeValue.DECREASING:
                    return var2.value == QualitativeValue.DECREASING
                elif var1.value == QualitativeValue.ZERO:
                    return var2.value == QualitativeValue.ZERO
                    
        # Default: constraint is satisfied if no conflicts detected
        return True


class CorrespondenceConstraint(QualitativeConstraint):
    """Correspondence constraint: changes in x correspond to changes in y"""
    
    def __init__(self, var1: QualitativeVariable, var2: QualitativeVariable):
        super().__init__(ConstraintType.CORRESPONDENCE, [var1, var2])
        self.var1 = var1
        self.var2 = var2
        
    def propagate(self) -> bool:
        """Propagate correspondence constraint"""
        changed = False
        
        # If var1 is increasing, var2 should increase
        if self.var1.value == QualitativeValue.INCREASING:
            if self.var2.value != QualitativeValue.INCREASING:
                self.var2.set_value(QualitativeValue.INCREASING)
                changed = True
                
        # If var1 is decreasing, var2 should decrease  
        elif self.var1.value == QualitativeValue.DECREASING:
            if self.var2.value != QualitativeValue.DECREASING:
                self.var2.set_value(QualitativeValue.DECREASING)
                changed = True
                
        return changed
        
    def is_satisfied(self) -> bool:
        """Check if correspondence constraint is satisfied"""
        if self.var1.value == QualitativeValue.INCREASING:
            return self.var2.value == QualitativeValue.INCREASING
        elif self.var1.value == QualitativeValue.DECREASING:
            return self.var2.value == QualitativeValue.DECREASING
        return True


class ConstraintPropagator:
    """System for propagating qualitative constraints"""
    
    def __init__(self):
        self.constraints: List[QualitativeConstraint] = []
        self.variables: Dict[str, QualitativeVariable] = {}
        self.max_iterations = 100
        
    def add_variable(self, variable: QualitativeVariable):
        """Add a variable to the system"""
        self.variables[variable.name] = variable
        
    def add_constraint(self, constraint: QualitativeConstraint):
        """Add a constraint to the system"""
        self.constraints.append(constraint)
        
    def propagate_constraints(self) -> int:
        """Propagate all constraints until fixed point"""
        iterations = 0
        
        while iterations < self.max_iterations:
            changed = False
            
            for constraint in self.constraints:
                if constraint.active:
                    if constraint.propagate():
                        changed = True
                        
            if not changed:
                break
                
            iterations += 1
            
        return iterations
        
    def check_consistency(self) -> bool:
        """Check if all constraints are satisfied"""
        for constraint in self.constraints:
            if constraint.active and not constraint.is_satisfied():
                return False
        return True
        
    def get_variable_values(self) -> Dict[str, QualitativeValue]:
        """Get current values of all variables"""
        return {name: var.value for name, var in self.variables.items()}