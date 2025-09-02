"""
🔧 Qualitative Reasoning - Core Types Module
============================================

This module provides the fundamental data types and structures for qualitative reasoning
systems based on Forbus's Process Theory and de Kleer's Qualitative Physics framework.

📚 Theoretical Foundation:
Forbus, K. D., & de Kleer, J. (1993). "Building Problem Solvers", MIT Press
de Kleer, J., & Brown, J. S. (1984). "A Qualitative Physics Based on Confluences"

🎯 Core Concept:
Qualitative reasoning captures human-like understanding of physical systems through
discrete symbolic representations rather than continuous numerical values. This enables
AI systems to reason about physics without precise measurements, similar to how humans
understand that "more pressure leads to faster flow" without exact calculations.

🧠 Key Principles:
1. Quantities have qualitative magnitudes (negative, zero, positive, etc.)
2. Directions capture trends (increasing, decreasing, steady)  
3. Landmark values create discrete behavioral regions
4. Processes influence quantities through qualitative relationships

🔬 Mathematical Framework:
- Qualitative State: Q = [magnitude, direction]
- Magnitude ∈ {-∞, -large, -small, 0, +small, +large, +∞}  
- Direction ∈ {increasing, decreasing, steady, unknown}
- Process Influences: I±(quantity) affects quantity trends

Author: Benedict Chen
Based on foundational work by Kenneth Forbus and Johan de Kleer
"""

from typing import Dict, List, Tuple, Union, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import warnings


class QualitativeValue(Enum):
    """
    Qualitative magnitude values for continuous quantities.
    
    Based on Forbus's quantity space theory, these discrete values capture
    the essential behavioral distinctions needed for qualitative reasoning
    without requiring precise numerical measurements.
    
    🔬 Theoretical Background:
    Forbus demonstrated that many physical reasoning tasks only require
    distinguishing between qualitative regions like "positive" vs "negative"
    rather than exact values. This enum captures the minimal distinctions
    needed for robust physical reasoning.
    
    Values are ordered from most negative to most positive to enable
    qualitative comparison operations.
    """
    
    # Extreme negative values
    NEGATIVE_INFINITY = "neg_inf"      # Unboundedly negative (e.g., vacuum pressure)
    DECREASING_LARGE = "dec_large"     # Large negative change rate  
    NEGATIVE_LARGE = "neg_large"       # Large negative magnitude
    
    # Small negative values
    DECREASING = "decreasing"          # Generic negative trend
    NEGATIVE_SMALL = "neg_small"       # Small negative magnitude
    
    # Zero point - critical landmark
    ZERO = "zero"                      # Neutral/equilibrium value
    
    # Small positive values  
    POSITIVE_SMALL = "pos_small"       # Small positive magnitude
    INCREASING = "increasing"          # Generic positive trend
    
    # Large positive values
    POSITIVE_LARGE = "pos_large"       # Large positive magnitude
    INCREASING_LARGE = "inc_large"     # Large positive change rate
    POSITIVE_INFINITY = "pos_inf"      # Unboundedly positive (e.g., infinite heat)
    
    @classmethod
    def get_ordering(cls) -> Dict['QualitativeValue', int]:
        """
        Get numerical ordering for qualitative value comparisons.
        
        Returns:
            Dict mapping each qualitative value to its numeric order
            
        Example:
            >>> ordering = QualitativeValue.get_ordering()
            >>> ordering[QualitativeValue.ZERO] < ordering[QualitativeValue.POSITIVE_SMALL]
            True
        """
        return {
            cls.NEGATIVE_INFINITY: -5,
            cls.DECREASING_LARGE: -4,
            cls.NEGATIVE_LARGE: -3,
            cls.DECREASING: -2,
            cls.NEGATIVE_SMALL: -1,
            cls.ZERO: 0,
            cls.POSITIVE_SMALL: 1,
            cls.INCREASING: 2,
            cls.POSITIVE_LARGE: 3,
            cls.INCREASING_LARGE: 4,
            cls.POSITIVE_INFINITY: 5
        }
    
    def __lt__(self, other: 'QualitativeValue') -> bool:
        """Enable qualitative value ordering comparisons."""
        if not isinstance(other, QualitativeValue):
            return NotImplemented
        ordering = self.get_ordering()
        return ordering[self] < ordering[other]
    
    def __le__(self, other: 'QualitativeValue') -> bool:
        """Enable less-than-or-equal qualitative comparisons."""
        if not isinstance(other, QualitativeValue):
            return NotImplemented
        ordering = self.get_ordering()
        return ordering[self] <= ordering[other]
    
    def __gt__(self, other: 'QualitativeValue') -> bool:
        """Enable greater-than qualitative comparisons."""
        if not isinstance(other, QualitativeValue):
            return NotImplemented
        ordering = self.get_ordering()
        return ordering[self] > ordering[other]
    
    def __ge__(self, other: 'QualitativeValue') -> bool:
        """Enable greater-than-or-equal qualitative comparisons.""" 
        if not isinstance(other, QualitativeValue):
            return NotImplemented
        ordering = self.get_ordering()
        return ordering[self] >= ordering[other]
    
    def is_positive(self) -> bool:
        """Check if this qualitative value represents a positive quantity."""
        return self in {self.POSITIVE_SMALL, self.INCREASING, self.POSITIVE_LARGE, 
                       self.INCREASING_LARGE, self.POSITIVE_INFINITY}
    
    def is_negative(self) -> bool:
        """Check if this qualitative value represents a negative quantity."""
        return self in {self.NEGATIVE_INFINITY, self.DECREASING_LARGE, self.NEGATIVE_LARGE,
                       self.DECREASING, self.NEGATIVE_SMALL}
    
    def is_zero(self) -> bool:
        """Check if this qualitative value represents zero/equilibrium."""
        return self == self.ZERO
    
    def get_magnitude_class(self) -> str:
        """Get the magnitude classification (small, large, infinite, etc.)."""
        if self in {self.NEGATIVE_SMALL, self.POSITIVE_SMALL}:
            return "small"
        elif self in {self.NEGATIVE_LARGE, self.POSITIVE_LARGE}:
            return "large"
        elif self in {self.NEGATIVE_INFINITY, self.POSITIVE_INFINITY}:
            return "infinite"
        elif self == self.ZERO:
            return "zero"
        else:
            return "trend"


class QualitativeDirection(Enum):
    """
    Qualitative directions representing trends in quantity changes.
    
    🔬 Theoretical Foundation:
    In Forbus's Process Theory, quantities have both a current value and a
    direction of change. This captures the essential temporal dynamics needed
    for physical reasoning - not just "what is" but "what is becoming".
    
    The direction is independent of magnitude, enabling fine-grained reasoning
    about system dynamics. For example, temperature can be positive but decreasing.
    """
    
    INCREASING = "+"    # Quantity is rising/growing (dQ/dt > 0)
    DECREASING = "-"    # Quantity is falling/shrinking (dQ/dt < 0)  
    STEADY = "0"        # Quantity is stable/constant (dQ/dt = 0)
    UNKNOWN = "?"       # Direction cannot be determined
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        direction_names = {
            self.INCREASING: "increasing",
            self.DECREASING: "decreasing", 
            self.STEADY: "steady",
            self.UNKNOWN: "unknown"
        }
        return direction_names[self]
    
    @classmethod
    def from_numeric_trend(cls, trend_value: float, threshold: float = 1e-6) -> 'QualitativeDirection':
        """
        Convert numeric trend to qualitative direction.
        
        Args:
            trend_value: Numeric rate of change
            threshold: Minimum magnitude to consider non-zero
            
        Returns:
            Corresponding qualitative direction
        """
        if abs(trend_value) < threshold:
            return cls.STEADY
        elif trend_value > 0:
            return cls.INCREASING
        else:
            return cls.DECREASING
    
    def to_numeric_sign(self) -> int:
        """Convert direction to numeric sign for calculations."""
        direction_map = {
            self.INCREASING: 1,
            self.DECREASING: -1,
            self.STEADY: 0,
            self.UNKNOWN: 0
        }
        return direction_map[self]
    
    def is_changing(self) -> bool:
        """Check if quantity is changing (not steady)."""
        return self in {self.INCREASING, self.DECREASING}
    
    def reverse(self) -> 'QualitativeDirection':
        """Get the opposite direction."""
        reversal_map = {
            self.INCREASING: self.DECREASING,
            self.DECREASING: self.INCREASING,
            self.STEADY: self.STEADY,
            self.UNKNOWN: self.UNKNOWN
        }
        return reversal_map[self]


@dataclass
class QualitativeQuantity:
    """
    Represents a physical quantity with qualitative magnitude and direction.
    
    🔬 Theoretical Foundation:
    Forbus's central insight was that physical quantities can be represented
    as [magnitude, direction] pairs, capturing both current state and trend.
    This enables reasoning about system dynamics without numerical precision.
    
    Example: Water temperature might be [POSITIVE_SMALL, INCREASING], indicating
    warm water that is heating up.
    
    🎯 Key Features:
    - Magnitude captures current qualitative value
    - Direction captures trend/change over time  
    - Landmark values define critical behavioral boundaries
    - Name provides human-readable identification
    """
    
    name: str                                          # Human-readable quantity name
    magnitude: QualitativeValue                        # Current qualitative value
    direction: QualitativeDirection                    # Trend direction
    landmark_values: Optional[List[float]] = None      # Critical numerical boundaries
    units: Optional[str] = None                        # Physical units (if applicable)
    description: Optional[str] = None                  # Human-readable description
    
    def __post_init__(self):
        """Initialize derived fields after construction."""
        if self.landmark_values is None:
            self.landmark_values = []
        
        # Sort landmark values for efficient boundary checking
        if self.landmark_values:
            self.landmark_values = sorted(self.landmark_values)
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        direction_symbol = {
            QualitativeDirection.INCREASING: "↗",
            QualitativeDirection.DECREASING: "↘", 
            QualitativeDirection.STEADY: "→",
            QualitativeDirection.UNKNOWN: "?"
        }
        
        symbol = direction_symbol[self.direction]
        units_str = f" {self.units}" if self.units else ""
        
        return f"{self.name}: {self.magnitude.value}{units_str} {symbol}"
    
    def get_qualitative_state(self) -> Tuple[QualitativeValue, QualitativeDirection]:
        """Get the complete qualitative state as a tuple."""
        return (self.magnitude, self.direction)
    
    def is_stable(self) -> bool:
        """Check if quantity is in a stable state (not changing)."""
        return self.direction == QualitativeDirection.STEADY
    
    def is_positive(self) -> bool:
        """Check if quantity has positive magnitude."""
        return self.magnitude.is_positive()
    
    def is_negative(self) -> bool:
        """Check if quantity has negative magnitude."""
        return self.magnitude.is_negative()
    
    def is_zero(self) -> bool:
        """Check if quantity is at zero/equilibrium."""
        return self.magnitude.is_zero()
    
    def is_increasing(self) -> bool:
        """Check if quantity is increasing."""
        return self.direction == QualitativeDirection.INCREASING
    
    def is_decreasing(self) -> bool:
        """Check if quantity is decreasing."""
        return self.direction == QualitativeDirection.DECREASING
    
    def transition_magnitude(self, direction: Optional[QualitativeDirection] = None) -> QualitativeValue:
        """
        Get the next qualitative magnitude given a direction of change.
        
        Args:
            direction: Direction of change (uses self.direction if None)
            
        Returns:
            New qualitative magnitude after transition
        """
        if direction is None:
            direction = self.direction
            
        if direction == QualitativeDirection.STEADY:
            return self.magnitude
        elif direction == QualitativeDirection.INCREASING:
            return self._increase_magnitude(self.magnitude)
        elif direction == QualitativeDirection.DECREASING:
            return self._decrease_magnitude(self.magnitude)
        else:
            return self.magnitude
    
    def _increase_magnitude(self, current: QualitativeValue) -> QualitativeValue:
        """Transition magnitude upward through qualitative scale."""
        transitions = {
            QualitativeValue.NEGATIVE_INFINITY: QualitativeValue.NEGATIVE_LARGE,
            QualitativeValue.NEGATIVE_LARGE: QualitativeValue.NEGATIVE_SMALL,
            QualitativeValue.NEGATIVE_SMALL: QualitativeValue.ZERO,
            QualitativeValue.ZERO: QualitativeValue.POSITIVE_SMALL,
            QualitativeValue.POSITIVE_SMALL: QualitativeValue.POSITIVE_LARGE,
            QualitativeValue.POSITIVE_LARGE: QualitativeValue.POSITIVE_INFINITY,
            QualitativeValue.POSITIVE_INFINITY: QualitativeValue.POSITIVE_INFINITY
        }
        return transitions.get(current, current)
    
    def _decrease_magnitude(self, current: QualitativeValue) -> QualitativeValue:
        """Transition magnitude downward through qualitative scale."""
        transitions = {
            QualitativeValue.POSITIVE_INFINITY: QualitativeValue.POSITIVE_LARGE,
            QualitativeValue.POSITIVE_LARGE: QualitativeValue.POSITIVE_SMALL,
            QualitativeValue.POSITIVE_SMALL: QualitativeValue.ZERO,
            QualitativeValue.ZERO: QualitativeValue.NEGATIVE_SMALL,
            QualitativeValue.NEGATIVE_SMALL: QualitativeValue.NEGATIVE_LARGE,
            QualitativeValue.NEGATIVE_LARGE: QualitativeValue.NEGATIVE_INFINITY,
            QualitativeValue.NEGATIVE_INFINITY: QualitativeValue.NEGATIVE_INFINITY
        }
        return transitions.get(current, current)
    
    def copy(self) -> 'QualitativeQuantity':
        """Create a deep copy of this quantity."""
        return QualitativeQuantity(
            name=self.name,
            magnitude=self.magnitude,
            direction=self.direction,
            landmark_values=self.landmark_values.copy() if self.landmark_values else None,
            units=self.units,
            description=self.description
        )


@dataclass  
class QualitativeState:
    """
    Complete qualitative state of a system at one time instant.
    
    🔬 Theoretical Foundation:
    Forbus's Process Theory represents system states as collections of
    quantities with their current qualitative values and trends. This
    captures the essential information needed for qualitative prediction
    and explanation.
    
    States form the nodes in a qualitative behavior graph, with processes
    driving transitions between states.
    
    🎯 Key Components:
    - Time point identifier for temporal reasoning
    - Quantities map with current qualitative values
    - Relationships capture derived/inferred properties
    - Metadata for additional context
    """
    
    time_point: str                                    # Temporal identifier
    quantities: Dict[str, QualitativeQuantity]         # Quantity name -> quantity state
    relationships: Dict[str, str] = field(default_factory=dict)  # Derived relationships
    metadata: Dict[str, Any] = field(default_factory=dict)       # Additional context
    
    def __post_init__(self):
        """Initialize derived state information."""
        if not self.relationships:
            self.relationships = {}
        if not self.metadata:
            self.metadata = {}
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        qty_summary = f"{len(self.quantities)} quantities"
        rel_summary = f"{len(self.relationships)} relationships"
        return f"QualitativeState[{self.time_point}]: {qty_summary}, {rel_summary}"
    
    def get_quantity_names(self) -> List[str]:
        """Get list of all quantity names in this state."""
        return list(self.quantities.keys())
    
    def get_quantity(self, name: str) -> Optional[QualitativeQuantity]:
        """Get quantity by name, returning None if not found."""
        return self.quantities.get(name)
    
    def has_quantity(self, name: str) -> bool:
        """Check if state contains a specific quantity."""
        return name in self.quantities
    
    def add_quantity(self, quantity: QualitativeQuantity) -> None:
        """Add a quantity to this state."""
        self.quantities[quantity.name] = quantity
    
    def remove_quantity(self, name: str) -> Optional[QualitativeQuantity]:
        """Remove and return a quantity from this state."""
        return self.quantities.pop(name, None)
    
    def get_changing_quantities(self) -> List[QualitativeQuantity]:
        """Get all quantities that are currently changing."""
        return [qty for qty in self.quantities.values() 
                if qty.direction != QualitativeDirection.STEADY]
    
    def get_stable_quantities(self) -> List[QualitativeQuantity]:
        """Get all quantities that are currently stable."""
        return [qty for qty in self.quantities.values() 
                if qty.direction == QualitativeDirection.STEADY]
    
    def get_positive_quantities(self) -> List[QualitativeQuantity]:
        """Get all quantities with positive magnitudes."""
        return [qty for qty in self.quantities.values() if qty.is_positive()]
    
    def get_negative_quantities(self) -> List[QualitativeQuantity]:
        """Get all quantities with negative magnitudes."""
        return [qty for qty in self.quantities.values() if qty.is_negative()]
    
    def get_zero_quantities(self) -> List[QualitativeQuantity]:
        """Get all quantities at zero/equilibrium."""
        return [qty for qty in self.quantities.values() if qty.is_zero()]
    
    def add_relationship(self, name: str, relationship_type: str) -> None:
        """Add a derived relationship to this state."""
        self.relationships[name] = relationship_type
    
    def get_relationship(self, name: str) -> Optional[str]:
        """Get relationship by name, returning None if not found."""
        return self.relationships.get(name)
    
    def copy(self) -> 'QualitativeState':
        """Create a deep copy of this state."""
        return QualitativeState(
            time_point=self.time_point,
            quantities={name: qty.copy() for name, qty in self.quantities.items()},
            relationships=self.relationships.copy(),
            metadata=self.metadata.copy()
        )
    
    def compare_with(self, other: 'QualitativeState') -> Dict[str, str]:
        """
        Compare this state with another state to identify differences.
        
        Args:
            other: Another qualitative state to compare with
            
        Returns:
            Dictionary describing differences between states
        """
        differences = {}
        
        # Check for quantity differences
        common_quantities = set(self.quantities.keys()) & set(other.quantities.keys())
        
        for qty_name in common_quantities:
            qty1 = self.quantities[qty_name]
            qty2 = other.quantities[qty_name]
            
            if qty1.magnitude != qty2.magnitude:
                differences[f"{qty_name}_magnitude"] = f"{qty1.magnitude.value} -> {qty2.magnitude.value}"
            
            if qty1.direction != qty2.direction:
                differences[f"{qty_name}_direction"] = f"{qty1.direction.value} -> {qty2.direction.value}"
        
        # Check for added/removed quantities
        added_quantities = set(other.quantities.keys()) - set(self.quantities.keys())
        if added_quantities:
            differences["added_quantities"] = list(added_quantities)
        
        removed_quantities = set(self.quantities.keys()) - set(other.quantities.keys())
        if removed_quantities:
            differences["removed_quantities"] = list(removed_quantities)
        
        return differences


@dataclass
class QualitativeProcess:
    """
    Represents a process with preconditions, quantity conditions, and influences.
    
    🔬 Theoretical Foundation:
    Forbus's Process Theory models physical causation through processes that
    are active when certain conditions are met, and which influence quantities
    in predictable ways. This captures the causal structure underlying physical
    system behavior.
    
    Processes are the dynamic engines of qualitative reasoning - they determine
    how systems evolve over time based on current conditions.
    
    🎯 Key Components:
    - Preconditions: Logical conditions for process activation
    - Quantity conditions: Constraints on quantity values
    - Influences: Effects on quantities when process is active
    - Activity state: Whether process is currently running
    """
    
    name: str                           # Human-readable process name
    preconditions: List[str]           # Logical preconditions for activation
    quantity_conditions: List[str]     # Constraints on quantity values
    influences: List[str]              # Effects on quantities (e.g., "I+(temperature)")
    active: bool = False               # Whether process is currently active
    description: Optional[str] = None  # Human-readable description
    priority: int = 0                  # Priority for process resolution conflicts
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        status = "ACTIVE" if self.active else "INACTIVE"
        return f"Process[{self.name}]: {status}, {len(self.influences)} influences"
    
    def get_influenced_quantities(self) -> List[str]:
        """
        Extract quantity names that this process influences.
        
        Returns:
            List of quantity names affected by this process
        """
        influenced = []
        for influence in self.influences:
            # Parse influences like "I+(temperature)" or "I-(pressure)"
            if influence.startswith("I+") or influence.startswith("I-"):
                if influence.endswith(")"):
                    # Extract quantity name from "I+(quantity_name)"
                    start_idx = influence.find("(") + 1
                    end_idx = influence.rfind(")")
                    if start_idx > 0 and end_idx > start_idx:
                        quantity_name = influence[start_idx:end_idx].strip()
                        influenced.append(quantity_name)
                else:
                    # Handle "I+quantity_name" format
                    quantity_name = influence[2:].strip()
                    influenced.append(quantity_name)
        return influenced
    
    def get_influence_type(self, quantity_name: str) -> Optional[str]:
        """
        Get the type of influence this process has on a specific quantity.
        
        Args:
            quantity_name: Name of the quantity to check
            
        Returns:
            "increase", "decrease", or None if no influence
        """
        for influence in self.influences:
            if quantity_name in influence:
                if influence.startswith("I+"):
                    return "increase"
                elif influence.startswith("I-"):
                    return "decrease"
        return None
    
    def has_influence_on(self, quantity_name: str) -> bool:
        """Check if this process influences a specific quantity."""
        return quantity_name in self.get_influenced_quantities()
    
    def get_activation_requirements(self) -> Dict[str, List[str]]:
        """
        Get structured activation requirements.
        
        Returns:
            Dictionary with 'preconditions' and 'quantity_conditions' lists
        """
        return {
            "preconditions": self.preconditions.copy(),
            "quantity_conditions": self.quantity_conditions.copy()
        }
    
    def copy(self) -> 'QualitativeProcess':
        """Create a deep copy of this process."""
        return QualitativeProcess(
            name=self.name,
            preconditions=self.preconditions.copy(),
            quantity_conditions=self.quantity_conditions.copy(),
            influences=self.influences.copy(),
            active=self.active,
            description=self.description,
            priority=self.priority
        )


# Utility functions for working with qualitative values

def compare_qualitative_values(left: QualitativeValue, right: QualitativeValue, 
                             operator: str) -> bool:
    """
    Compare two qualitative values using a comparison operator.
    
    Args:
        left: First qualitative value
        right: Second qualitative value
        operator: Comparison operator (">", "<", ">=", "<=", "==", "!=")
        
    Returns:
        Result of the comparison
        
    Example:
        >>> compare_qualitative_values(QualitativeValue.POSITIVE_SMALL, 
        ...                           QualitativeValue.ZERO, ">")
        True
    """
    if operator == ">":
        return left > right
    elif operator == "<":
        return left < right
    elif operator == ">=":
        return left >= right
    elif operator == "<=":
        return left <= right
    elif operator == "==" or operator == "=":
        return left == right
    elif operator == "!=":
        return left != right
    else:
        raise ValueError(f"Unsupported comparison operator: {operator}")


def qualitative_to_numeric(qual_value: QualitativeValue) -> float:
    """
    Convert qualitative value to representative numeric value.
    
    Args:
        qual_value: Qualitative value to convert
        
    Returns:
        Numeric representation for calculations
        
    Note:
        This is for computational purposes only - the exact values are not
        semantically meaningful in qualitative reasoning.
    """
    value_map = {
        QualitativeValue.NEGATIVE_INFINITY: -float('inf'),
        QualitativeValue.DECREASING_LARGE: -4.0,
        QualitativeValue.NEGATIVE_LARGE: -3.0,
        QualitativeValue.DECREASING: -2.0,
        QualitativeValue.NEGATIVE_SMALL: -1.0,
        QualitativeValue.ZERO: 0.0,
        QualitativeValue.POSITIVE_SMALL: 1.0,
        QualitativeValue.INCREASING: 2.0,
        QualitativeValue.POSITIVE_LARGE: 3.0,
        QualitativeValue.INCREASING_LARGE: 4.0,
        QualitativeValue.POSITIVE_INFINITY: float('inf')
    }
    return value_map.get(qual_value, 0.0)


def numeric_to_qualitative(numeric_value: float, landmarks: Optional[List[float]] = None) -> QualitativeValue:
    """
    Convert numeric value to qualitative value using landmarks.
    
    Args:
        numeric_value: Numeric value to convert
        landmarks: Optional landmark values for region boundaries
        
    Returns:
        Corresponding qualitative value
        
    Example:
        >>> numeric_to_qualitative(5.0, landmarks=[0.0, 10.0])
        QualitativeValue.POSITIVE_SMALL
    """
    # Handle infinite values
    if numeric_value == float('inf'):
        return QualitativeValue.POSITIVE_INFINITY
    elif numeric_value == -float('inf'):
        return QualitativeValue.NEGATIVE_INFINITY
    
    # Handle zero
    if abs(numeric_value) < 1e-10:
        return QualitativeValue.ZERO
    
    # Use landmarks if provided
    if landmarks:
        landmarks = sorted(landmarks)
        
        # Find position relative to landmarks
        if numeric_value < landmarks[0]:
            return QualitativeValue.NEGATIVE_SMALL if numeric_value > landmarks[0] / 2 else QualitativeValue.NEGATIVE_LARGE
        elif numeric_value > landmarks[-1]:
            return QualitativeValue.POSITIVE_LARGE if numeric_value > landmarks[-1] * 2 else QualitativeValue.POSITIVE_SMALL
        else:
            # Value is between landmarks
            return QualitativeValue.POSITIVE_SMALL if numeric_value > 0 else QualitativeValue.NEGATIVE_SMALL
    
    # Default classification without landmarks
    if numeric_value > 0:
        if numeric_value < 1.0:
            return QualitativeValue.POSITIVE_SMALL
        else:
            return QualitativeValue.POSITIVE_LARGE
    else:
        if numeric_value > -1.0:
            return QualitativeValue.NEGATIVE_SMALL
        else:
            return QualitativeValue.NEGATIVE_LARGE


def create_quantity(name: str, magnitude: Union[QualitativeValue, str] = QualitativeValue.ZERO,
                   direction: Union[QualitativeDirection, str] = QualitativeDirection.STEADY,
                   landmarks: Optional[List[float]] = None,
                   units: Optional[str] = None,
                   description: Optional[str] = None) -> QualitativeQuantity:
    """
    Convenience function to create a qualitative quantity with flexible input types.
    
    Args:
        name: Quantity name
        magnitude: Qualitative magnitude (enum or string)
        direction: Qualitative direction (enum or string)
        landmarks: Optional landmark values
        units: Optional physical units
        description: Optional description
        
    Returns:
        New QualitativeQuantity instance
        
    Example:
        >>> qty = create_quantity("temperature", "pos_small", "increasing", 
        ...                      landmarks=[0.0, 100.0], units="°C")
    """
    # Convert string inputs to enums if necessary
    if isinstance(magnitude, str):
        magnitude = QualitativeValue(magnitude)
    
    if isinstance(direction, str):
        if direction in ["+", "inc", "increasing"]:
            direction = QualitativeDirection.INCREASING
        elif direction in ["-", "dec", "decreasing"]:
            direction = QualitativeDirection.DECREASING
        elif direction in ["0", "std", "steady"]:
            direction = QualitativeDirection.STEADY
        elif direction in ["?", "unknown"]:
            direction = QualitativeDirection.UNKNOWN
        else:
            direction = QualitativeDirection(direction)
    
    return QualitativeQuantity(
        name=name,
        magnitude=magnitude,
        direction=direction,
        landmark_values=landmarks,
        units=units,
        description=description
    )


def validate_qualitative_state(state: QualitativeState) -> List[str]:
    """
    Validate the consistency of a qualitative state.
    
    Args:
        state: Qualitative state to validate
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    # Check for duplicate quantity names
    quantity_names = list(state.quantities.keys())
    if len(quantity_names) != len(set(quantity_names)):
        errors.append("Duplicate quantity names found")
    
    # Check for valid quantity objects
    for name, qty in state.quantities.items():
        if not isinstance(qty, QualitativeQuantity):
            errors.append(f"Quantity '{name}' is not a QualitativeQuantity instance")
        elif qty.name != name:
            errors.append(f"Quantity name mismatch: key='{name}', quantity.name='{qty.name}'")
    
    # Check time point
    if not state.time_point or not isinstance(state.time_point, str):
        errors.append("Invalid time point - must be non-empty string")
    
    return errors


# Type aliases for convenience
QValue = QualitativeValue
QDirection = QualitativeDirection  
QQuantity = QualitativeQuantity
QState = QualitativeState
QProcess = QualitativeProcess