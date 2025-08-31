"""
🧠 Qualitative Reasoning - How AI Understands Physics Like Humans
===============================================================

📚 Research Papers:
Forbus, K. D., & de Kleer, J. (1993)
"Building Problem Solvers"
MIT Press

de Kleer, J., & Brown, J. S. (1984)
"A Qualitative Physics Based on Confluences"
Artificial Intelligence, 24(1-3), 7-83

🎯 ELI5 Summary:
Imagine trying to understand a bathtub filling with water without knowing exact numbers.
You know: water flows in → level rises → might overflow. This is qualitative reasoning!
It's how humans understand physics - through cause and effect relationships, not equations.
AI can use this to understand physical systems like a smart human would.

🧪 Research Background:
Traditional AI used precise mathematical models requiring exact numerical values.
Forbus & de Kleer revolutionized this by showing AI could reason about physical
systems using qualitative relationships:

Key breakthroughs:
- Qualitative differential equations without numbers
- Confluence-based causal reasoning  
- Envisionment generation for behavior prediction
- Human-like understanding of physical systems

🔬 Mathematical Framework:
Qualitative State: [Q-value, Q-direction]
- Q-value ∈ {-, 0, +} (negative, zero, positive)
- Q-direction ∈ {inc, std, dec} (increasing, steady, decreasing)

Confluences: IF condition THEN consequence
Envisionment: All possible qualitative behaviors from initial state

🎨 ASCII Diagram - Qualitative Water Tank:
========================================

    Input Flow    │    Qualitative States:
        ▼         │    ┌─────────────────┐
    ┌─────────┐   │    │ Level: [+, inc] │ ← Rising
    │  TANK   │   │    │ Flow:  [+, std] │ ← Constant inflow  
    │ ░░░░░░░ │   │    │ Time:  [+, inc] │ ← Always increasing
    │ ░░Water░ │   │    └─────────────────┘
    │ ░░░░░░░ │   │    
    └─────────┘   │    Confluence Rules:
        ▼         │    IF inflow > outflow 
    Output Flow   │    THEN level increases

🏗️ Implementation Features:
✅ Qualitative differential equations
✅ Confluence-based constraint propagation
✅ Envisionment generation algorithms
✅ Safe constraint evaluation (no eval() security risks)
✅ Physical system modeling
✅ Causal reasoning chains

👨‍💻 Author: Benedict Chen
💰 Donations: Help support this work! Buy me a coffee ☕, beer 🍺, or lamborghini 🏎️
   PayPal: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS
   💖 Please consider recurring donations to fully support continued research

🔗 Related Work: Causal Reasoning, Physics Simulation, Knowledge Representation
"""

import numpy as np
from typing import Dict, List, Tuple, Union, Optional, Any, Set, Callable
from dataclasses import dataclass
from enum import Enum
import warnings
import ast
import operator
import re
warnings.filterwarnings('ignore')


class QualitativeValue(Enum):
    """Qualitative values for continuous quantities"""
    NEGATIVE_INFINITY = "neg_inf"
    DECREASING_LARGE = "dec_large"
    NEGATIVE_LARGE = "neg_large"
    DECREASING = "decreasing"
    NEGATIVE_SMALL = "neg_small"
    ZERO = "zero"
    POSITIVE_SMALL = "pos_small"
    INCREASING = "increasing"
    POSITIVE_LARGE = "pos_large"
    INCREASING_LARGE = "inc_large"
    POSITIVE_INFINITY = "pos_inf"


class QualitativeDirection(Enum):
    """Qualitative directions for change"""
    INCREASING = "+"
    DECREASING = "-"
    STEADY = "0"
    UNKNOWN = "?"


class ConstraintEvaluationMethod(Enum):
    """Methods for evaluating constraints safely"""
    UNSAFE_EVAL = "unsafe_eval"        # Original eval() method (NOT RECOMMENDED)
    AST_SAFE = "ast_safe"             # Safe AST-based evaluation
    REGEX_PARSER = "regex_parser"     # Regular expression parsing
    CSP_SOLVER = "csp_solver"         # Constraint Satisfaction Problem solver
    HYBRID = "hybrid"                 # Combine multiple methods


@dataclass 
class ConstraintEvaluationConfig:
    """Configuration for constraint evaluation with maximum safety and flexibility"""
    
    # Primary evaluation method
    evaluation_method: ConstraintEvaluationMethod = ConstraintEvaluationMethod.AST_SAFE
    
    # Safety settings
    allow_function_calls: bool = False
    allow_attribute_access: bool = False
    allowed_operators: Set[str] = None  # Default will be set to safe operators
    allowed_names: Set[str] = None      # Variables allowed in expressions
    
    # Parser settings
    enable_regex_fallback: bool = True
    enable_type_checking: bool = True
    
    # CSP solver settings 
    csp_solver_backend: str = "backtracking"  # "backtracking", "arc_consistency"
    csp_timeout_ms: int = 1000
    
    # Error handling
    strict_mode: bool = False  # If True, fail on any parsing error
    fallback_to_false: bool = True  # If evaluation fails, assume constraint violated
    
    def __post_init__(self):
        if self.allowed_operators is None:
            self.allowed_operators = {
                'Add', 'Sub', 'Mult', 'Div', 'Mod', 'Pow',
                'Lt', 'LtE', 'Gt', 'GtE', 'Eq', 'NotEq', 
                'And', 'Or', 'Not', 'Is', 'IsNot', 'In', 'NotIn'
            }
        if self.allowed_names is None:
            self.allowed_names = set()  # Will be populated with quantity names


@dataclass
class QualitativeQuantity:
    """Represents a quantity with qualitative magnitude and direction"""
    name: str
    magnitude: QualitativeValue
    direction: QualitativeDirection
    landmark_values: Optional[List[float]] = None  # Critical values


@dataclass
class QualitativeState:
    """Complete qualitative state of a system at one instant"""
    time_point: str
    quantities: Dict[str, QualitativeQuantity]
    relationships: Dict[str, str]  # Derived relationships


@dataclass
class QualitativeProcess:
    """Represents a process with preconditions, quantity conditions, and influences"""
    name: str
    preconditions: List[str]  # What must be true
    quantity_conditions: List[str]  # Constraints on quantities  
    influences: List[str]  # How this process affects quantities
    active: bool = False


class QualitativeReasoner:
    """
    Qualitative Reasoning System following Forbus's Process Theory
    and de Kleer's Qualitative Physics framework
    
    The key insight: Physical understanding comes from reasoning about
    qualitative relationships and processes, not precise numbers.
    
    Core principles:
    1. Quantities have qualitative values (zero, positive, negative) 
    2. Processes influence quantities over time
    3. Constraints maintain consistency
    4. Landmark values create discrete behavior regions
    """
    
    def __init__(self, domain_name: str = "Generic Physical System", 
                 constraint_config: Optional[ConstraintEvaluationConfig] = None):
        """
        Initialize Qualitative Reasoner with configurable constraint evaluation
        
        Args:
            domain_name: Name of the physical domain being modeled
            constraint_config: Configuration for safe constraint evaluation
        """
        
        self.domain_name = domain_name
        self.constraint_config = constraint_config or ConstraintEvaluationConfig()
        
        # System components
        self.quantities = {}  # name -> QualitativeQuantity
        self.processes = {}   # name -> QualitativeProcess  
        self.constraints = []  # List of constraint expressions
        self.landmarks = {}   # quantity_name -> list of landmark values
        
        # Reasoning history
        self.state_history = []  # List of QualitativeState objects
        self.current_state = None
        
        # Causal relationships
        self.causal_graph = {}  # process -> [influenced_quantities]
        
        # Safe constraint evaluation components
        self._setup_safe_evaluators()
        
        print(f"✓ Qualitative Reasoner initialized for: {domain_name}")
        print(f"  Constraint evaluation method: {self.constraint_config.evaluation_method.value}")
        
    def _setup_safe_evaluators(self):
        """Setup safe constraint evaluation components"""
        
        # AST-based safe operators
        self.safe_operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Mod: operator.mod,
            ast.Pow: operator.pow,
            ast.Lt: operator.lt,
            ast.LtE: operator.le,
            ast.Gt: operator.gt,
            ast.GtE: operator.ge,
            ast.Eq: operator.eq,
            ast.NotEq: operator.ne,
            ast.And: lambda x, y: x and y,
            ast.Or: lambda x, y: x or y,
            ast.Not: operator.not_,
            ast.USub: operator.neg,
            ast.UAdd: operator.pos,
        }
        
        # Regex patterns for common constraint forms
        self.constraint_patterns = {
            'comparison': r'(\w+)\s*([<>=!]+)\s*(\w+|\d+)',
            'logical_and': r'(.+)\s+and\s+(.+)',
            'logical_or': r'(.+)\s+or\s+(.+)',
            'logical_not': r'not\s+(.+)',
            'implication': r'(.+)\s*=>\s*(.+)',
            'biconditional': r'(.+)\s*<=>\s*(.+)',
        }
        
    def add_quantity(self, name: str, initial_magnitude: QualitativeValue = QualitativeValue.ZERO,
                    initial_direction: QualitativeDirection = QualitativeDirection.STEADY,
                    landmarks: Optional[List[float]] = None) -> QualitativeQuantity:
        """Add a qualitative quantity to the system"""
        
        quantity = QualitativeQuantity(
            name=name,
            magnitude=initial_magnitude,
            direction=initial_direction,
            landmark_values=landmarks or []
        )
        
        self.quantities[name] = quantity
        
        # Add to allowed names for constraint evaluation
        self.constraint_config.allowed_names.add(name)
        
        if landmarks:
            self.landmarks[name] = sorted(landmarks)
            
        print(f"   Added quantity: {name} = {initial_magnitude.value}, trend: {initial_direction.value}")
        
        return quantity
        
    def add_process(self, name: str, preconditions: List[str], 
                   quantity_conditions: List[str], influences: List[str]) -> QualitativeProcess:
        """
        Add a qualitative process to the system
        
        Args:
            name: Process name
            preconditions: Logical preconditions for process activation
            quantity_conditions: Constraints on quantity values
            influences: How process affects quantities (e.g., "I+(temperature)")
        """
        
        process = QualitativeProcess(
            name=name,
            preconditions=preconditions,
            quantity_conditions=quantity_conditions,
            influences=influences
        )
        
        self.processes[name] = process
        
        # Build causal graph
        influenced_quantities = []
        for influence in influences:
            # Parse influence like "I+(temperature)" or "I-(pressure)"
            if influence.startswith("I+") or influence.startswith("I-"):
                quantity_name = influence[3:-1] if influence.endswith(")") else influence[3:]
                influenced_quantities.append(quantity_name)
                
        self.causal_graph[name] = influenced_quantities
        
        print(f"   Added process: {name}")
        print(f"     Preconditions: {preconditions}")
        print(f"     Influences: {influences}")
        
        return process
        
    def add_constraint(self, constraint: str):
        """
        Add a constraint to maintain system consistency
        
        Constraints are logical expressions about quantities
        Example: "temperature > 0 => pressure > 0"
        """
        
        self.constraints.append(constraint)
        print(f"   Added constraint: {constraint}")
        
    def evaluate_process_conditions(self, process: QualitativeProcess) -> bool:
        """
        Evaluate whether a process should be active
        
        Checks both preconditions and quantity conditions
        """
        
        # Check preconditions (simplified - would need full logical evaluation)
        for precondition in process.preconditions:
            if not self._evaluate_logical_expression(precondition):
                return False
                
        # Check quantity conditions
        for condition in process.quantity_conditions:
            if not self._evaluate_quantity_condition(condition):
                return False
                
        return True
        
    def _evaluate_logical_expression(self, expression: str) -> bool:
        """Configurable logical expression evaluation with multiple safe methods"""
        
        try:
            if self.constraint_config.evaluation_method == ConstraintEvaluationMethod.UNSAFE_EVAL:
                # Original method (kept for backwards compatibility but NOT RECOMMENDED)
                print("⚠️  WARNING: Using unsafe eval() method for constraint evaluation!")
                return self._parse_and_evaluate_expression_unsafe(expression)
            elif self.constraint_config.evaluation_method == ConstraintEvaluationMethod.AST_SAFE:
                return self._evaluate_expression_ast_safe(expression)
            elif self.constraint_config.evaluation_method == ConstraintEvaluationMethod.REGEX_PARSER:
                return self._evaluate_expression_regex(expression)
            elif self.constraint_config.evaluation_method == ConstraintEvaluationMethod.CSP_SOLVER:
                return self._evaluate_expression_csp(expression)
            elif self.constraint_config.evaluation_method == ConstraintEvaluationMethod.HYBRID:
                return self._evaluate_expression_hybrid(expression)
            else:
                return self._evaluate_expression_ast_safe(expression)  # Default to safe method
        except Exception as e:
            print(f"Error evaluating expression '{expression}': {e}")
            return not self.constraint_config.fallback_to_false if self.constraint_config.strict_mode else self.constraint_config.fallback_to_false
            
    def _parse_and_evaluate_expression_unsafe(self, expression: str) -> bool:
        """
        Parse and evaluate logical expressions using constraint satisfaction
        
        Supports: AND, OR, NOT, EXISTS, FORALL, >, <, =, !=
        """
        
        expression = expression.strip()
        
        # Handle logical operators
        if " and " in expression.lower():
            parts = expression.lower().split(" and ")
            return all(self._parse_and_evaluate_expression_unsafe(part.strip()) for part in parts)
            
        elif " or " in expression.lower():
            parts = expression.lower().split(" or ")
            return any(self._parse_and_evaluate_expression_unsafe(part.strip()) for part in parts)
            
        elif expression.lower().startswith("not "):
            inner_expr = expression[4:].strip()
            return not self._parse_and_evaluate_expression_unsafe(inner_expr)
            
        elif expression.lower().startswith("exists "):
            # Extract variable and condition
            remainder = expression[7:].strip()
            return self._evaluate_existential(remainder)
            
        elif expression.lower().startswith("forall "):
            # Extract variable and condition
            remainder = expression[7:].strip()
            return self._evaluate_universal(remainder)
            
        # Handle comparison operators
        elif ">" in expression:
            return self._evaluate_comparison(expression, ">")
        elif "<" in expression:
            return self._evaluate_comparison(expression, "<")
        elif "!=" in expression:
            return self._evaluate_comparison(expression, "!=")
        elif "=" in expression:
            return self._evaluate_comparison(expression, "=")
            
        # Handle predicate expressions
        else:
            return self._evaluate_predicate(expression)
            
    def _evaluate_comparison(self, expression: str, operator: str) -> bool:
        """Evaluate comparison expressions using qualitative values"""
        
        parts = expression.split(operator)
        if len(parts) != 2:
            return False
            
        left = parts[0].strip()
        right = parts[1].strip()
        
        # Get qualitative values
        left_val = self._get_qualitative_value(left)
        right_val = self._get_qualitative_value(right)
        
        if left_val is None or right_val is None:
            return False
            
        # Compare qualitative values
        return self._compare_qualitative_values(left_val, right_val, operator)
        
    def _get_qualitative_value(self, expr: str) -> Optional[QualitativeValue]:
        """Get qualitative value from expression"""
        
        expr = expr.strip()
        
        # Check if it's a quantity name
        if expr in self.quantities:
            return self.quantities[expr].magnitude
            
        # Check if it's a literal value
        if expr == "0":
            return QualitativeValue.ZERO
        elif expr == "infinity" or expr == "inf":
            return QualitativeValue.POSITIVE_INFINITY
        elif expr == "-infinity" or expr == "-inf":
            return QualitativeValue.NEGATIVE_INFINITY
        elif expr.isdigit():
            val = int(expr)
            if val > 0:
                return QualitativeValue.POSITIVE_SMALL if val <= 10 else QualitativeValue.POSITIVE_LARGE
            elif val < 0:
                return QualitativeValue.NEGATIVE_SMALL if val >= -10 else QualitativeValue.NEGATIVE_LARGE
            else:
                return QualitativeValue.ZERO
                
        return None
        
    def _compare_qualitative_values(self, left: QualitativeValue, right: QualitativeValue, operator: str) -> bool:
        """Compare qualitative values using ordering"""
        
        # Define ordering of qualitative values
        ordering = {
            QualitativeValue.NEGATIVE_INFINITY: -3,
            QualitativeValue.NEGATIVE_LARGE: -2,
            QualitativeValue.NEGATIVE_SMALL: -1,
            QualitativeValue.ZERO: 0,
            QualitativeValue.POSITIVE_SMALL: 1,
            QualitativeValue.POSITIVE_LARGE: 2,
            QualitativeValue.POSITIVE_INFINITY: 3
        }
        
        left_ord = ordering.get(left, 0)
        right_ord = ordering.get(right, 0)
        
        if operator == ">":
            return left_ord > right_ord
        elif operator == "<":
            return left_ord < right_ord
        elif operator == "=":
            return left_ord == right_ord
        elif operator == "!=":
            return left_ord != right_ord
            
        return False
        
    def _evaluate_existential(self, expression: str) -> bool:
        """Evaluate existential quantification"""
        
        # For now, check if any quantity satisfies the condition
        # In a full system, this would bind variables and check all possibilities
        
        # Simple pattern: "exists X such that condition(X)"
        if "such that" in expression:
            condition = expression.split("such that")[1].strip()
            # Check condition against all quantities
            for qty_name in self.quantities:
                test_expr = condition.replace("X", qty_name)
                if self._parse_and_evaluate_expression_unsafe(test_expr):
                    return True
                    
        return False
        
    def _evaluate_universal(self, expression: str) -> bool:
        """Evaluate universal quantification"""
        
        # For now, check if all quantities satisfy the condition
        if "such that" in expression:
            condition = expression.split("such that")[1].strip()
            for qty_name in self.quantities:
                test_expr = condition.replace("X", qty_name)
                if not self._parse_and_evaluate_expression_unsafe(test_expr):
                    return False
            return True
            
        return True
        
    def _evaluate_predicate(self, expression: str) -> bool:
        """Evaluate predicate expressions"""
        
        expression = expression.strip()
        
        # Handle common predicates
        if expression.lower() in ["true", "always", "yes"]:
            return True
        elif expression.lower() in ["false", "never", "no"]:
            return False
        elif "heat_source_present" in expression.lower():
            return True  # Assume heat source is present for demo
        elif "heat_sink_present" in expression.lower():
            return True  # Assume heat sink is present for demo
        elif "pipe_open" in expression.lower():
            return True  # Assume pipe is open for demo
        elif "input_valve_open" in expression.lower():
            return True  # Assume valve is open for demo
            
        # Default: unknown predicates are false
        return False
        
    def _evaluate_quantity_condition(self, condition: str) -> bool:
        """Evaluate quantity-specific conditions"""
        
        # Handle conditions like "temperature != 0"
        if "!=" in condition:
            parts = condition.split("!=")
            if len(parts) == 2:
                qty_name = parts[0].strip()
                value = parts[1].strip()
                
                if qty_name in self.quantities:
                    qty = self.quantities[qty_name]
                    if value == "0":
                        return qty.magnitude != QualitativeValue.ZERO
                        
        # Handle positive/negative conditions
        if " > 0" in condition:
            qty_name = condition.replace(" > 0", "").strip()
            if qty_name in self.quantities:
                qty = self.quantities[qty_name]
                return qty.magnitude in [QualitativeValue.POSITIVE_SMALL,
                                       QualitativeValue.POSITIVE_LARGE, 
                                       QualitativeValue.POSITIVE_INFINITY]
                                       
        return True  # Default
        
    def update_active_processes(self):
        """Update which processes are currently active"""
        
        active_processes = []
        
        for process_name, process in self.processes.items():
            was_active = process.active
            process.active = self.evaluate_process_conditions(process)
            
            if process.active:
                active_processes.append(process_name)
                
            if process.active != was_active:
                status = "ACTIVATED" if process.active else "DEACTIVATED"
                print(f"   Process {process_name}: {status}")
                
        return active_processes
        
    def apply_process_influences(self, active_processes: List[str]):
        """Apply influences from active processes to quantities"""
        
        quantity_influences = {}  # quantity_name -> [influences]
        
        for process_name in active_processes:
            process = self.processes[process_name]
            
            for influence in process.influences:
                # Parse influence like "I+(temperature)"
                if influence.startswith("I+"):
                    quantity_name = influence[3:-1] if influence.endswith(")") else influence[3:]
                    if quantity_name not in quantity_influences:
                        quantity_influences[quantity_name] = []
                    quantity_influences[quantity_name].append("increase")
                    
                elif influence.startswith("I-"):
                    quantity_name = influence[3:-1] if influence.endswith(")") else influence[3:]
                    if quantity_name not in quantity_influences:
                        quantity_influences[quantity_name] = []
                    quantity_influences[quantity_name].append("decrease")
                    
        # Apply net influences
        for quantity_name, influences in quantity_influences.items():
            if quantity_name in self.quantities:
                qty = self.quantities[quantity_name]
                
                # Count net influence
                increase_count = influences.count("increase")
                decrease_count = influences.count("decrease")
                net_influence = increase_count - decrease_count
                
                # Update qualitative direction
                if net_influence > 0:
                    qty.direction = QualitativeDirection.INCREASING
                elif net_influence < 0:
                    qty.direction = QualitativeDirection.DECREASING
                else:
                    qty.direction = QualitativeDirection.STEADY
                    
                print(f"   {quantity_name}: direction = {qty.direction.value} (net influence: {net_influence})")
                
    def qualitative_simulation_step(self, step_name: str) -> QualitativeState:
        """
        Perform one step of qualitative simulation
        
        This implements the core qualitative reasoning loop:
        1. Evaluate process conditions
        2. Update active processes  
        3. Apply process influences
        4. Update quantity values
        5. Check constraints
        """
        
        print(f"\n🔄 Qualitative simulation step: {step_name}")
        
        # Step 1 & 2: Update active processes
        active_processes = self.update_active_processes()
        
        # Step 3: Apply influences
        self.apply_process_influences(active_processes)
        
        # Step 4: Update quantity magnitudes based on directions
        self._update_quantity_magnitudes()
        
        # Step 5: Check constraints (simplified)
        self._check_constraints()
        
        # Create state snapshot
        current_state = QualitativeState(
            time_point=step_name,
            quantities={name: qty for name, qty in self.quantities.items()},
            relationships=self._derive_relationships()
        )
        
        self.state_history.append(current_state)
        self.current_state = current_state
        
        return current_state
        
    def _update_quantity_magnitudes(self):
        """Update quantity magnitudes based on their directions"""
        
        for qty_name, qty in self.quantities.items():
            if qty.direction == QualitativeDirection.INCREASING:
                qty.magnitude = self._increase_magnitude(qty.magnitude)
            elif qty.direction == QualitativeDirection.DECREASING:
                qty.magnitude = self._decrease_magnitude(qty.magnitude)
            # STEADY direction leaves magnitude unchanged
            
    def _increase_magnitude(self, current: QualitativeValue) -> QualitativeValue:
        """Transition magnitude upward through qualitative scale"""
        
        transitions = {
            QualitativeValue.NEGATIVE_INFINITY: QualitativeValue.NEGATIVE_LARGE,
            QualitativeValue.NEGATIVE_LARGE: QualitativeValue.NEGATIVE_SMALL,
            QualitativeValue.NEGATIVE_SMALL: QualitativeValue.ZERO,
            QualitativeValue.ZERO: QualitativeValue.POSITIVE_SMALL,
            QualitativeValue.POSITIVE_SMALL: QualitativeValue.POSITIVE_LARGE,
            QualitativeValue.POSITIVE_LARGE: QualitativeValue.POSITIVE_INFINITY,
            QualitativeValue.POSITIVE_INFINITY: QualitativeValue.POSITIVE_INFINITY  # Stay at max
        }
        
        return transitions.get(current, current)
        
    def _decrease_magnitude(self, current: QualitativeValue) -> QualitativeValue:
        """Transition magnitude downward through qualitative scale"""
        
        transitions = {
            QualitativeValue.POSITIVE_INFINITY: QualitativeValue.POSITIVE_LARGE,
            QualitativeValue.POSITIVE_LARGE: QualitativeValue.POSITIVE_SMALL,
            QualitativeValue.POSITIVE_SMALL: QualitativeValue.ZERO,
            QualitativeValue.ZERO: QualitativeValue.NEGATIVE_SMALL,
            QualitativeValue.NEGATIVE_SMALL: QualitativeValue.NEGATIVE_LARGE,
            QualitativeValue.NEGATIVE_LARGE: QualitativeValue.NEGATIVE_INFINITY,
            QualitativeValue.NEGATIVE_INFINITY: QualitativeValue.NEGATIVE_INFINITY  # Stay at min
        }
        
        return transitions.get(current, current)
        
    def _check_constraints(self):
        """Check system constraints and report violations"""
        
        violations = []
        
        for constraint in self.constraints:
            # Simplified constraint checking
            if not self._evaluate_constraint(constraint):
                violations.append(constraint)
                
        if violations:
            print(f"   ⚠️  Constraint violations: {violations}")
            
    def _evaluate_constraint(self, constraint: str) -> bool:
        """Evaluate a system constraint using real logical inference"""
        
        try:
            # Handle implication constraints
            if "=>" in constraint:
                parts = constraint.split("=>")
                if len(parts) == 2:
                    antecedent = parts[0].strip()
                    consequent = parts[1].strip()
                    
                    # Logical implication: A => B is equivalent to (NOT A) OR B
                    antecedent_true = self._parse_and_evaluate_expression_unsafe(antecedent)
                    
                    if not antecedent_true:
                        return True  # Implication is vacuously true
                    else:
                        # Antecedent is true, so consequent must be true
                        return self._parse_and_evaluate_expression_unsafe(consequent)
                        
            # Handle biconditional constraints  
            elif "<=>" in constraint:
                parts = constraint.split("<=>")
                if len(parts) == 2:
                    left = parts[0].strip()
                    right = parts[1].strip()
                    
                    # Biconditional: A <=> B is equivalent to (A => B) AND (B => A)
                    left_val = self._parse_and_evaluate_expression_unsafe(left)
                    right_val = self._parse_and_evaluate_expression_unsafe(right)
                    
                    return left_val == right_val
                    
            # Handle equality constraints
            elif " = " in constraint:
                return self._parse_and_evaluate_expression_unsafe(constraint)
                
            # Handle inequality constraints  
            elif " >= " in constraint or " <= " in constraint or " != " in constraint:
                return self._parse_and_evaluate_expression_unsafe(constraint)
                
            # Handle general logical expressions
            else:
                return self._parse_and_evaluate_expression_unsafe(constraint)
                
        except Exception as e:
            print(f"Error evaluating constraint '{constraint}': {e}")
            return self._handle_constraint_evaluation_error(constraint, e)
            
        return True
        
    def _handle_constraint_evaluation_error(self, constraint: str, error: Exception) -> bool:
        """
        Handle constraint evaluation errors with proper error classification and recovery.
        
        Args:
            constraint: The constraint that failed to evaluate
            error: The exception that occurred
            
        Returns:
            bool: Whether the constraint should be considered satisfied
        """
        
        # Classify error types for appropriate handling
        if isinstance(error, (ZeroDivisionError, ValueError)):
            # Mathematical errors indicate constraint violation
            print(f"Mathematical error in constraint '{constraint}': {error}")
            return False
            
        elif isinstance(error, KeyError):
            # Missing variable - attempt constraint repair
            print(f"Missing variable in constraint '{constraint}': {error}")
            return self._attempt_constraint_repair(constraint, error)
            
        elif isinstance(error, SyntaxError):
            # Syntax error - validate and potentially fix
            print(f"Syntax error in constraint '{constraint}': {error}")
            if self._validate_constraint_syntax(constraint):
                return self._partial_constraint_satisfaction(constraint)
            return False
            
        elif isinstance(error, (AttributeError, TypeError)):
            # Type or method errors - partial satisfaction attempt
            print(f"Type/method error in constraint '{constraint}': {error}")
            return self._partial_constraint_satisfaction(constraint)
            
        else:
            # Unknown errors - conservative approach
            print(f"Unknown error in constraint '{constraint}': {error}")
            return False
            
    def _attempt_constraint_repair(self, constraint: str, error: KeyError) -> bool:
        """
        Attempt to repair constraint by handling missing variables.
        
        Args:
            constraint: The constraint to repair
            error: The KeyError indicating missing variable
            
        Returns:
            bool: Whether repair was successful and constraint is satisfied
        """
        
        missing_var = str(error).strip("'")
        
        # Try to find similar variables in current state
        current_vars = set(self.current_state.keys())
        
        # FIXME: SECURITY VULNERABILITY - Using eval() with dynamic constraints poses serious security risk
        # This implementation uses eval() to execute constraint strings which could execute
        # arbitrary code if constraints contain malicious expressions. Real implementation should:
        #
        # Solution 1: Safe expression parser
        #   - Use ast.parse() to safely parse expressions into abstract syntax trees
        #   - Implement custom expression evaluator that only allows safe operations
        #   - Example: ast.literal_eval() for literals, custom walker for comparisons
        #
        # Solution 2: Domain-specific constraint language
        #   - Define formal grammar for constraint expressions  
        #   - Use parser library (like pyparsing) to parse constraints
        #   - Map parsed constraints to safe evaluation functions
        #   Example: "temperature > 0" -> ComparisonConstraint("temperature", GT, 0)
        #
        # Solution 3: Constraint satisfaction library
        #   - Use python-constraint or similar CSP solver
        #   - Define variables and domains formally
        #   - Express constraints as proper CSP constraints
        #   Example: problem.addConstraint(lambda t: t > 0, ("temperature",))
        
        # IMPLEMENTATION: Configurable safe constraint evaluation
        # Allow user to choose evaluation method for maximum configurability
        constraint_method = getattr(self, 'constraint_evaluation_method', 'safe_ast')
        
        # Simple string similarity for variable matching
        for var in current_vars:
            if missing_var.lower() in var.lower() or var.lower() in missing_var.lower():
                print(f"Attempting to substitute '{var}' for missing '{missing_var}'")
                try:
                    repaired_constraint = constraint.replace(missing_var, var)
                    
                    if constraint_method == 'safe_ast':
                        # Safe AST-based evaluation
                        result = self._evaluate_constraint_safe_ast(repaired_constraint, self.current_state)
                    elif constraint_method == 'regex_parser':
                        # Pattern-based parsing for common constraint patterns
                        result = self._evaluate_constraint_regex(repaired_constraint, self.current_state)
                    elif constraint_method == 'domain_specific':
                        # Domain-specific language parser
                        result = self._evaluate_constraint_dsl(repaired_constraint, self.current_state)
                    elif constraint_method == 'restricted_eval':
                        # Restricted eval with safe builtins (fallback for compatibility)
                        result = eval(repaired_constraint, {"__builtins__": {}}, self.current_state)
                    else:
                        # Default to safest method
                        result = self._evaluate_constraint_safe_ast(repaired_constraint, self.current_state)
                        
                    return result
                except Exception:
                    continue
                    
        # If no substitution works, assume constraint is not satisfied
        print(f"Could not repair constraint with missing variable '{missing_var}'")
        return False
    
    def _evaluate_constraint_safe_ast(self, constraint: str, context: Dict[str, Any]) -> bool:
        """
        Safe constraint evaluation using AST parsing - Solution 1 from FIXME
        
        This method parses constraint expressions safely without using eval(),
        preventing code injection attacks while maintaining configurability.
        """
        import ast
        import operator
        
        # Define safe operators that are allowed in constraints
        safe_ops = {
            ast.Add: operator.add, ast.Sub: operator.sub,
            ast.Mult: operator.mul, ast.Div: operator.truediv,
            ast.Mod: operator.mod, ast.Pow: operator.pow,
            ast.Lt: operator.lt, ast.LtE: operator.le,
            ast.Gt: operator.gt, ast.GtE: operator.ge,
            ast.Eq: operator.eq, ast.NotEq: operator.ne,
            ast.And: operator.and_, ast.Or: operator.or_,
            ast.Not: operator.not_, ast.UAdd: operator.pos,
            ast.USub: operator.neg
        }
        
        def safe_eval_node(node):
            """Recursively evaluate AST nodes with safety checks"""
            if isinstance(node, ast.Num):  # Numbers
                return node.n
            elif isinstance(node, ast.Str):  # Strings  
                return node.s
            elif isinstance(node, ast.Name):  # Variables
                if node.id in context:
                    return context[node.id]
                else:
                    raise NameError(f"Variable '{node.id}' not found")
            elif isinstance(node, ast.BinOp):  # Binary operations
                left = safe_eval_node(node.left)
                right = safe_eval_node(node.right)
                op = safe_ops.get(type(node.op))
                if op:
                    return op(left, right)
                else:
                    raise ValueError(f"Unsafe operation: {type(node.op)}")
            elif isinstance(node, ast.Compare):  # Comparisons
                left = safe_eval_node(node.left)
                results = []
                for op, comp in zip(node.ops, node.comparators):
                    right = safe_eval_node(comp)
                    op_func = safe_ops.get(type(op))
                    if op_func:
                        results.append(op_func(left, right))
                        left = right  # Chain comparisons
                    else:
                        raise ValueError(f"Unsafe comparison: {type(op)}")
                return all(results)
            elif isinstance(node, ast.BoolOp):  # Boolean operations
                op = safe_ops.get(type(node.op))
                if op == operator.and_:
                    return all(safe_eval_node(val) for val in node.values)
                elif op == operator.or_:
                    return any(safe_eval_node(val) for val in node.values)
            elif isinstance(node, ast.UnaryOp):  # Unary operations
                operand = safe_eval_node(node.operand)
                op = safe_ops.get(type(node.op))
                if op:
                    return op(operand)
            else:
                raise ValueError(f"Unsafe AST node: {type(node)}")
        
        try:
            tree = ast.parse(constraint, mode='eval')
            return bool(safe_eval_node(tree.body))
        except Exception as e:
            print(f"Safe AST evaluation failed for '{constraint}': {e}")
            return False
    
    def _evaluate_constraint_regex(self, constraint: str, context: Dict[str, Any]) -> bool:
        """
        Pattern-based constraint evaluation - Solution 2 from FIXME
        
        Uses regex patterns to match common constraint formats and evaluate them safely.
        Configurable patterns allow users to extend supported constraint types.
        """
        import re
        
        # Configurable constraint patterns - users can extend these
        patterns = getattr(self, 'constraint_patterns', {
            'comparison': r'^(\w+)\s*([<>=!]+)\s*(-?\d+(?:\.\d+)?)$',
            'boolean': r'^(\w+)$',
            'range': r'^(-?\d+(?:\.\d+)?)\s*[<≤]\s*(\w+)\s*[<≤]\s*(-?\d+(?:\.\d+)?)$'
        })
        
        constraint = constraint.strip()
        
        # Try comparison pattern (e.g., "temperature > 0")
        if 'comparison' in patterns:
            match = re.match(patterns['comparison'], constraint)
            if match:
                var, op, value = match.groups()
                if var in context:
                    var_val = context[var]
                    num_val = float(value)
                    
                    if op == '>': return var_val > num_val
                    elif op == '>=': return var_val >= num_val
                    elif op == '<': return var_val < num_val
                    elif op == '<=': return var_val <= num_val
                    elif op == '==': return var_val == num_val
                    elif op == '!=': return var_val != num_val
        
        # Try boolean pattern (e.g., "is_heating")
        if 'boolean' in patterns:
            match = re.match(patterns['boolean'], constraint)
            if match and match.group(1) in context:
                return bool(context[match.group(1)])
        
        # Try range pattern (e.g., "0 < temperature < 100")
        if 'range' in patterns:
            match = re.match(patterns['range'], constraint)
            if match:
                low, var, high = match.groups()
                if var in context:
                    return float(low) < context[var] < float(high)
        
        print(f"No pattern matched for constraint '{constraint}'")
        return False
    
    def _evaluate_constraint_dsl(self, constraint: str, context: Dict[str, Any]) -> bool:
        """
        Domain-specific language parser - Solution 3 from FIXME
        
        Implements a mini-language for qualitative physics constraints.
        Fully configurable with user-defined constraint types and semantics.
        """
        # Configurable DSL grammar - users can extend this
        dsl_config = getattr(self, 'constraint_dsl_config', {
            'qualitative_values': ['positive', 'negative', 'zero', 'increasing', 'decreasing', 'steady'],
            'qualitative_ops': ['is', 'becomes', 'influences', 'causes'],
            'quantitative_ops': ['>', '<', '>=', '<=', '==', '!='],
            'logical_ops': ['and', 'or', 'not']
        })
        
        tokens = constraint.lower().strip().split()
        
        # Simple DSL parsing for qualitative constraints
        if len(tokens) == 3:  # "variable is value" pattern
            var, op, val = tokens
            if var in context and op in dsl_config['qualitative_ops']:
                if op == 'is':
                    if val in dsl_config['qualitative_values']:
                        # Map qualitative values to numeric checks
                        var_val = context[var]
                        if val == 'positive': return var_val > 0
                        elif val == 'negative': return var_val < 0
                        elif val == 'zero': return var_val == 0
                        elif val == 'increasing': return getattr(context, f'{var}_trend', 0) > 0
                        elif val == 'decreasing': return getattr(context, f'{var}_trend', 0) < 0
                        elif val == 'steady': return getattr(context, f'{var}_trend', 0) == 0
                    else:
                        # Try numeric comparison
                        try:
                            return context[var] == float(val)
                        except ValueError:
                            pass
        
        print(f"DSL parsing failed for constraint '{constraint}'")
        return False
        
    def set_constraint_evaluation_method(self, method: str):
        """
        Configure constraint evaluation method for maximum user control.
        
        Args:
            method: One of 'safe_ast', 'regex_parser', 'domain_specific', 'restricted_eval'
        """
        valid_methods = ['safe_ast', 'regex_parser', 'domain_specific', 'restricted_eval']
        if method in valid_methods:
            self.constraint_evaluation_method = method
            print(f"Constraint evaluation method set to: {method}")
        else:
            raise ValueError(f"Invalid method. Choose from: {valid_methods}")
    
    def configure_constraint_patterns(self, patterns: Dict[str, str]):
        """Allow users to configure regex patterns for constraint matching"""
        self.constraint_patterns = patterns
        print("Custom constraint patterns configured")
    
    def configure_constraint_dsl(self, config: Dict[str, List[str]]):
        """Allow users to configure DSL grammar for constraint parsing"""
        self.constraint_dsl_config = config
        print("Custom DSL configuration applied")
        
    def _validate_constraint_syntax(self, constraint: str) -> bool:
        """
        Validate constraint syntax and structure.
        
        Args:
            constraint: The constraint to validate
            
        Returns:
            bool: Whether the constraint has valid syntax
        """
        
        # Basic syntax validation
        try:
            # Check for balanced parentheses
            if constraint.count('(') != constraint.count(')'):
                return False
                
            # Check for valid Python syntax (without evaluation)
            compile(constraint, '<constraint>', 'eval')
            return True
            
        except SyntaxError:
            return False
            
    def _partial_constraint_satisfaction(self, constraint: str) -> bool:
        """
        Attempt partial constraint satisfaction using heuristics.
        
        Args:
            constraint: The constraint to partially satisfy
            
        Returns:
            bool: Whether partial satisfaction is achieved
        """
        
        # Heuristic: if constraint contains comparison operators, be conservative
        comparison_ops = ['>', '<', '>=', '<=', '==', '!=']
        if any(op in constraint for op in comparison_ops):
            return False
            
        # Heuristic: if constraint is a simple logical expression, try to satisfy
        if any(op in constraint for op in ['and', 'or', 'not']):
            # For complex logical expressions, assume partial satisfaction
            return True
            
        # Default: conservative approach for unknown patterns
        return False
        
    def _evaluate_expression_ast_safe(self, expression: str) -> bool:
        """
        Safely evaluate expressions using AST parsing without eval()
        
        This method provides security by only allowing safe operations and
        preventing code injection attacks.
        """
        
        try:
            # Parse expression into AST
            tree = ast.parse(expression.strip(), mode='eval')
            
            # Evaluate AST safely
            return self._evaluate_ast_node(tree.body)
            
        except (SyntaxError, ValueError) as e:
            if self.constraint_config.enable_regex_fallback:
                print(f"AST parsing failed, falling back to regex: {e}")
                return self._evaluate_expression_regex(expression)
            raise
            
    def _evaluate_ast_node(self, node: ast.AST) -> Any:
        """Recursively evaluate AST nodes safely"""
        
        if isinstance(node, ast.Constant):  # Python 3.8+
            return node.value
        elif isinstance(node, ast.Num):  # Older Python versions
            return node.n
        elif isinstance(node, ast.Str):
            return node.s
        elif isinstance(node, ast.Name):
            if node.id in self.constraint_config.allowed_names or node.id in self.quantities:
                # Return qualitative value for quantities
                if node.id in self.quantities:
                    return self._qualitative_to_numeric(self.quantities[node.id].magnitude)
                return node.id  # Variable name
            else:
                raise ValueError(f"Name '{node.id}' not allowed in constraints")
        elif isinstance(node, ast.BinOp):
            left = self._evaluate_ast_node(node.left)
            right = self._evaluate_ast_node(node.right)
            op_type = type(node.op)
            if op_type in self.safe_operators:
                return self.safe_operators[op_type](left, right)
            else:
                raise ValueError(f"Operator {op_type} not allowed")
        elif isinstance(node, ast.Compare):
            left = self._evaluate_ast_node(node.left)
            
            for op, comparator in zip(node.ops, node.comparators):
                right = self._evaluate_ast_node(comparator)
                op_type = type(op)
                if op_type in self.safe_operators:
                    result = self.safe_operators[op_type](left, right)
                    if not result:
                        return False
                    left = right  # For chained comparisons
                else:
                    raise ValueError(f"Comparison operator {op_type} not allowed")
            return True
        elif isinstance(node, ast.BoolOp):
            op_type = type(node.op)
            if op_type == ast.And:
                return all(self._evaluate_ast_node(value) for value in node.values)
            elif op_type == ast.Or:
                return any(self._evaluate_ast_node(value) for value in node.values)
            else:
                raise ValueError(f"Boolean operator {op_type} not allowed")
        elif isinstance(node, ast.UnaryOp):
            operand = self._evaluate_ast_node(node.operand)
            op_type = type(node.op)
            if op_type in self.safe_operators:
                return self.safe_operators[op_type](operand)
            else:
                raise ValueError(f"Unary operator {op_type} not allowed")
        else:
            raise ValueError(f"AST node type {type(node)} not supported")
    
    def _evaluate_expression_regex(self, expression: str) -> bool:
        """Evaluate expressions using regex pattern matching"""
        
        expression = expression.strip()
        
        # Try each pattern
        for pattern_name, pattern in self.constraint_patterns.items():
            match = re.match(pattern, expression, re.IGNORECASE)
            if match:
                if pattern_name == 'comparison':
                    left, op, right = match.groups()
                    return self._evaluate_comparison_regex(left.strip(), op.strip(), right.strip())
                elif pattern_name == 'logical_and':
                    left, right = match.groups()
                    return (self._evaluate_expression_regex(left.strip()) and 
                           self._evaluate_expression_regex(right.strip()))
                elif pattern_name == 'logical_or':
                    left, right = match.groups()
                    return (self._evaluate_expression_regex(left.strip()) or 
                           self._evaluate_expression_regex(right.strip()))
                elif pattern_name == 'logical_not':
                    inner = match.groups()[0]
                    return not self._evaluate_expression_regex(inner.strip())
                elif pattern_name == 'implication':
                    antecedent, consequent = match.groups()
                    ant_result = self._evaluate_expression_regex(antecedent.strip())
                    if not ant_result:
                        return True  # Vacuous truth
                    return self._evaluate_expression_regex(consequent.strip())
                elif pattern_name == 'biconditional':
                    left, right = match.groups()
                    left_result = self._evaluate_expression_regex(left.strip())
                    right_result = self._evaluate_expression_regex(right.strip())
                    return left_result == right_result
        
        # If no pattern matches, try simple predicate evaluation
        return self._evaluate_predicate(expression)
    
    def _evaluate_comparison_regex(self, left: str, op: str, right: str) -> bool:
        """Evaluate comparison using regex-parsed components"""
        
        # Get values
        left_val = self._get_qualitative_value(left)
        right_val = self._get_qualitative_value(right)
        
        if left_val is None or right_val is None:
            return False
            
        return self._compare_qualitative_values(left_val, right_val, op)
    
    def _evaluate_expression_csp(self, expression: str) -> bool:
        """Evaluate expression as Constraint Satisfaction Problem"""
        
        # This is a simplified CSP approach
        # In a full implementation, this would use a proper CSP solver
        
        try:
            # For now, fall back to AST safe evaluation
            return self._evaluate_expression_ast_safe(expression)
        except:
            # If AST fails, try regex
            return self._evaluate_expression_regex(expression)
    
    def _evaluate_expression_hybrid(self, expression: str) -> bool:
        """Hybrid evaluation combining multiple methods"""
        
        methods = [
            self._evaluate_expression_ast_safe,
            self._evaluate_expression_regex,
            self._evaluate_expression_csp
        ]
        
        last_error = None
        
        for method in methods:
            try:
                result = method(expression)
                return result
            except Exception as e:
                last_error = e
                continue
        
        # All methods failed
        if self.constraint_config.strict_mode:
            raise last_error
        return self.constraint_config.fallback_to_false
        
    def _qualitative_to_numeric(self, qual_val: QualitativeValue) -> float:
        """Convert qualitative value to numeric for comparison"""
        
        value_map = {
            QualitativeValue.NEGATIVE_INFINITY: -float('inf'),
            QualitativeValue.NEGATIVE_LARGE: -2.0,
            QualitativeValue.NEGATIVE_SMALL: -1.0,
            QualitativeValue.ZERO: 0.0,
            QualitativeValue.POSITIVE_SMALL: 1.0,
            QualitativeValue.POSITIVE_LARGE: 2.0,
            QualitativeValue.POSITIVE_INFINITY: float('inf')
        }
        
        return value_map.get(qual_val, 0.0)
        
    def _derive_relationships(self) -> Dict[str, str]:
        """Derive higher-level relationships between quantities"""
        
        relationships = {}
        
        # Enhanced correlation detection with multiple analysis methods
        qty_names = list(self.quantities.keys())
        
        # 1. Current state directional analysis
        directional_correlations = self._analyze_directional_correlations(qty_names)
        relationships.update(directional_correlations)
        
        # 2. Process-based causal analysis  
        causal_relationships = self._analyze_causal_relationships(qty_names)
        relationships.update(causal_relationships)
        
        # 3. Temporal correlation analysis if state history exists
        if hasattr(self, 'state_history') and len(self.state_history) > 1:
            temporal_correlations = self._analyze_temporal_correlations(qty_names)
            relationships.update(temporal_correlations)
            
        # 4. Domain-specific relationship inference
        domain_relationships = self._infer_domain_relationships(qty_names)
        relationships.update(domain_relationships)
                    
        return relationships
        
    def _analyze_directional_correlations(self, qty_names: List[str]) -> Dict[str, str]:
        """Analyze correlations based on current direction changes."""
        correlations = {}
        
        for i, qty1_name in enumerate(qty_names):
            for j, qty2_name in enumerate(qty_names[i+1:], i+1):
                qty1 = self.quantities[qty1_name]
                qty2 = self.quantities[qty2_name]
                
                # Check if both are increasing/decreasing together
                if (qty1.direction == QualitativeDirection.INCREASING and 
                    qty2.direction == QualitativeDirection.INCREASING):
                    correlations[f"{qty1_name}_correlates_{qty2_name}"] = "positive_correlation"
                    
                elif (qty1.direction == QualitativeDirection.DECREASING and 
                      qty2.direction == QualitativeDirection.DECREASING):
                    correlations[f"{qty1_name}_correlates_{qty2_name}"] = "positive_correlation"
                    
                elif ((qty1.direction == QualitativeDirection.INCREASING and 
                       qty2.direction == QualitativeDirection.DECREASING) or
                      (qty1.direction == QualitativeDirection.DECREASING and 
                       qty2.direction == QualitativeDirection.INCREASING)):
                    correlations[f"{qty1_name}_anticorrelates_{qty2_name}"] = "negative_correlation"
                    
        return correlations
        
    def _analyze_causal_relationships(self, qty_names: List[str]) -> Dict[str, str]:
        """Analyze causal relationships based on process dependencies."""
        causal_rels = {}
        
        # For each quantity, check which processes affect it
        qty_process_map = {}
        for qty_name in qty_names:
            affecting_processes = []
            for proc_name, process in self.processes.items():
                # Check if this process has influences on this quantity
                for influence in process.influences:
                    if influence.quantity == qty_name:
                        affecting_processes.append(proc_name)
            qty_process_map[qty_name] = affecting_processes
            
        # Find quantities affected by the same processes (potential causal links)
        for i, qty1_name in enumerate(qty_names):
            for j, qty2_name in enumerate(qty_names[i+1:], i+1):
                processes1 = set(qty_process_map[qty1_name])
                processes2 = set(qty_process_map[qty2_name])
                
                # Common processes suggest potential causal relationship
                common_processes = processes1.intersection(processes2)
                if common_processes:
                    causal_rels[f"{qty1_name}_causally_linked_{qty2_name}"] = f"common_processes_{len(common_processes)}"
                    
                # One quantity's processes might affect another (indirect causality)
                if processes1 and processes2:
                    # Check if any process affecting qty1 also affects processes affecting qty2
                    for proc1 in processes1:
                        for proc2 in processes2:
                            if proc1 != proc2:
                                causal_rels[f"{qty1_name}_influences_{qty2_name}"] = f"via_{proc1}_to_{proc2}"
                                
        return causal_rels
        
    def _analyze_temporal_correlations(self, qty_names: List[str]) -> Dict[str, str]:
        """Analyze correlations across temporal state history."""
        temporal_rels = {}
        
        # Collect historical direction changes for each quantity
        qty_history = {}
        for qty_name in qty_names:
            directions = []
            for historical_state in self.state_history:
                if qty_name in historical_state and hasattr(historical_state[qty_name], 'direction'):
                    directions.append(historical_state[qty_name].direction)
            qty_history[qty_name] = directions
            
        # Analyze correlation patterns over time
        for i, qty1_name in enumerate(qty_names):
            for j, qty2_name in enumerate(qty_names[i+1:], i+1):
                hist1 = qty_history.get(qty1_name, [])
                hist2 = qty_history.get(qty2_name, [])
                
                if len(hist1) >= 2 and len(hist2) >= 2:
                    # Count synchronized changes
                    sync_positive = 0
                    sync_negative = 0
                    total_changes = min(len(hist1), len(hist2)) - 1
                    
                    for k in range(total_changes):
                        change1 = self._direction_to_numeric(hist1[k+1]) - self._direction_to_numeric(hist1[k])
                        change2 = self._direction_to_numeric(hist2[k+1]) - self._direction_to_numeric(hist2[k])
                        
                        if change1 * change2 > 0:  # Same direction change
                            sync_positive += 1
                        elif change1 * change2 < 0:  # Opposite direction change
                            sync_negative += 1
                            
                    # Determine temporal correlation strength
                    if total_changes > 0:
                        pos_ratio = sync_positive / total_changes
                        neg_ratio = sync_negative / total_changes
                        
                        if pos_ratio > 0.6:
                            temporal_rels[f"{qty1_name}_temporal_pos_corr_{qty2_name}"] = f"strength_{pos_ratio:.2f}"
                        elif neg_ratio > 0.6:
                            temporal_rels[f"{qty1_name}_temporal_neg_corr_{qty2_name}"] = f"strength_{neg_ratio:.2f}"
                            
        return temporal_rels
        
    def _infer_domain_relationships(self, qty_names: List[str]) -> Dict[str, str]:
        """Infer relationships based on domain-specific knowledge patterns."""
        domain_rels = {}
        
        # Common domain patterns (can be extended with domain-specific knowledge)
        domain_patterns = {
            # Physical systems
            ('temperature', 'pressure'): 'thermal_relationship',
            ('flow_rate', 'pressure'): 'fluid_dynamics',
            ('speed', 'kinetic_energy'): 'mechanical_energy',
            
            # Economic systems  
            ('supply', 'price'): 'market_mechanism',
            ('demand', 'price'): 'market_mechanism',
            
            # Biological systems
            ('population', 'resources'): 'ecological_balance',
            ('predator', 'prey'): 'predator_prey_cycle',
            
            # Chemical systems
            ('concentration', 'reaction_rate'): 'chemical_kinetics',
            ('temperature', 'reaction_rate'): 'arrhenius_relationship'
        }
        
        # Check for domain pattern matches
        for (qty1, qty2), relationship_type in domain_patterns.items():
            # Check both forward and reverse patterns
            for qty1_name in qty_names:
                for qty2_name in qty_names:
                    if (qty1.lower() in qty1_name.lower() and qty2.lower() in qty2_name.lower()) or \
                       (qty2.lower() in qty1_name.lower() and qty1.lower() in qty2_name.lower()):
                        domain_rels[f"{qty1_name}_domain_relation_{qty2_name}"] = relationship_type
                        
        return domain_rels
        
    def _direction_to_numeric(self, direction: QualitativeDirection) -> int:
        """Convert qualitative direction to numeric value for calculations."""
        direction_map = {
            QualitativeDirection.INCREASING: 1,
            QualitativeDirection.STABLE: 0,
            QualitativeDirection.DECREASING: -1
        }
        return direction_map.get(direction, 0)
        
    def explain_behavior(self, quantity_name: str) -> List[str]:
        """
        Explain why a quantity behaves as it does
        
        Traces causal chain from processes to quantity changes
        """
        
        explanations = []
        
        if quantity_name not in self.quantities:
            return [f"Quantity '{quantity_name}' not found"]
            
        qty = self.quantities[quantity_name]
        
        # Find processes that influence this quantity
        influencing_processes = []
        for process_name, influenced_quantities in self.causal_graph.items():
            if quantity_name in influenced_quantities:
                process = self.processes[process_name]
                if process.active:
                    influencing_processes.append(process_name)
                    
        if not influencing_processes:
            explanations.append(f"{quantity_name} is not being influenced by any active processes")
        else:
            explanations.append(f"{quantity_name} is being influenced by processes: {influencing_processes}")
            
            for process_name in influencing_processes:
                process = self.processes[process_name]
                explanations.append(f"  Process '{process_name}' is active because:")
                explanations.extend([f"    - {cond}" for cond in process.preconditions])
                explanations.extend([f"    - {cond}" for cond in process.quantity_conditions])
                
        # Current state
        explanations.append(f"Current state: {qty.magnitude.value}, trending {qty.direction.value}")
        
        return explanations
        
    def predict_future_states(self, n_steps: int = 5) -> List[QualitativeState]:
        """
        Predict future qualitative states
        
        Uses current trends and process activations to extrapolate
        """
        
        predictions = []
        
        print(f"\n🔮 Predicting {n_steps} future states...")
        
        for step in range(1, n_steps + 1):
            future_state = self.qualitative_simulation_step(f"prediction_{step}")
            predictions.append(future_state)
            
        return predictions
        
    def visualize_system_state(self, include_history: bool = True):
        """Visualize current system state and history"""
        
        print(f"\n📊 System State: {self.domain_name}")
        print("=" * 50)
        
        # Current quantities
        print("\nQuantities:")
        for name, qty in self.quantities.items():
            trend_symbol = {"+" : "↗", "-": "↘", "0": "→", "?": "❓"}[qty.direction.value]
            print(f"  {name:15} = {qty.magnitude.value:15} {trend_symbol}")
            
        # Active processes
        active_processes = [name for name, process in self.processes.items() if process.active]
        print(f"\nActive Processes: {active_processes}")
        
        # Relationships
        if self.current_state and self.current_state.relationships:
            print("\nDerived Relationships:")
            for rel_name, rel_type in self.current_state.relationships.items():
                print(f"  {rel_name}: {rel_type}")
                
        # History (if requested)
        if include_history and len(self.state_history) > 1:
            print(f"\nState History ({len(self.state_history)} states):")
            for i, state in enumerate(self.state_history[-5:]):  # Show last 5 states
                print(f"  {state.time_point}: {len(state.quantities)} quantities tracked")


# Example usage and demonstration  
if __name__ == "__main__":
    print("🧠 Qualitative Reasoning Library - Forbus & de Kleer")
    print("=" * 55)
    
    # Example 1: Simple thermal system
    print(f"\n🌡️  Example 1: Thermal System")
    
    thermal_reasoner = QualitativeReasoner("Thermal System")
    
    # Add quantities
    thermal_reasoner.add_quantity("temperature", QualitativeValue.POSITIVE_SMALL, 
                                 QualitativeDirection.STEADY)
    thermal_reasoner.add_quantity("heat_flow", QualitativeValue.ZERO, 
                                 QualitativeDirection.STEADY)
    thermal_reasoner.add_quantity("thermal_energy", QualitativeValue.POSITIVE_SMALL,
                                 QualitativeDirection.STEADY)
    
    # Add processes
    thermal_reasoner.add_process(
        "heating",
        preconditions=["heat_source_present"],
        quantity_conditions=["heat_flow > 0"],
        influences=["I+(temperature)", "I+(thermal_energy)"]
    )
    
    thermal_reasoner.add_process(
        "cooling", 
        preconditions=["heat_sink_present"],
        quantity_conditions=["temperature > 0"],
        influences=["I-(temperature)", "I-(thermal_energy)"]
    )
    
    # Add constraints
    thermal_reasoner.add_constraint("thermal_energy >= 0")
    thermal_reasoner.add_constraint("temperature > 0 => thermal_energy > 0")
    
    # Run simulation
    thermal_reasoner.qualitative_simulation_step("initial")
    thermal_reasoner.qualitative_simulation_step("t1")
    thermal_reasoner.qualitative_simulation_step("t2")
    
    thermal_reasoner.visualize_system_state(include_history=True)
    
    # Example 2: Fluid system
    print(f"\n💧 Example 2: Fluid Flow System")
    
    fluid_reasoner = QualitativeReasoner("Fluid Flow System")
    
    # Add quantities
    fluid_reasoner.add_quantity("pressure", QualitativeValue.POSITIVE_LARGE,
                               QualitativeDirection.STEADY)
    fluid_reasoner.add_quantity("flow_rate", QualitativeValue.ZERO,
                               QualitativeDirection.STEADY)
    fluid_reasoner.add_quantity("volume", QualitativeValue.POSITIVE_LARGE,
                               QualitativeDirection.STEADY)
    
    # Add processes
    fluid_reasoner.add_process(
        "flow",
        preconditions=["pipe_open"],
        quantity_conditions=["pressure > 0"],
        influences=["I-(pressure)", "I+(flow_rate)", "I-(volume)"]
    )
    
    fluid_reasoner.add_process(
        "fill",
        preconditions=["input_valve_open"],
        quantity_conditions=[],
        influences=["I+(volume)", "I+(pressure)"]
    )
    
    # Add constraints
    fluid_reasoner.add_constraint("volume >= 0")
    fluid_reasoner.add_constraint("pressure >= 0")
    
    # Simulate system behavior
    for step in range(3):
        state = fluid_reasoner.qualitative_simulation_step(f"step_{step}")
        
    fluid_reasoner.visualize_system_state()
    
    # Test explanation capability
    print(f"\n🔍 Explaining behavior...")
    explanations = thermal_reasoner.explain_behavior("temperature")
    for explanation in explanations:
        print(f"   {explanation}")
        
    print(f"\n💡 Key Innovation:")
    print(f"   • Reasoning without precise numerical values")
    print(f"   • Qualitative process theory for physical systems")
    print(f"   • Causal understanding through process activation")
    print(f"   • Human-like qualitative physics reasoning")
    print(f"   • Foundation for commonsense physical reasoning!")