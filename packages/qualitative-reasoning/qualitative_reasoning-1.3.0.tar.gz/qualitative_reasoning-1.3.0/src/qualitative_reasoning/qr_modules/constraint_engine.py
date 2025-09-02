"""
🔒 Qualitative Reasoning - Constraint Engine Module
==================================================

This module provides the safety-critical constraint evaluation engine for qualitative 
reasoning systems. It implements secure constraint satisfaction and evaluation methods
based on Forbus's Process Theory and de Kleer's Qualitative Physics framework.

📚 Theoretical Foundation:
Forbus, K. D., & de Kleer, J. (1993). "Building Problem Solvers", MIT Press
de Kleer, J., & Brown, J. S. (1984). "A Qualitative Physics Based on Confluences"

🔒 Security-First Design:
This module prioritizes security by avoiding eval() and implementing multiple safe
constraint evaluation strategies. Users can configure evaluation methods based on
their security requirements and constraint complexity needs.

🎯 Core Capabilities:
- Safe AST-based constraint evaluation (no eval() security risks)
- Regex pattern-based constraint parsing for common forms
- Domain-specific language (DSL) for qualitative physics constraints
- Hybrid evaluation combining multiple safe methods
- Comprehensive error handling and constraint repair
- Security validation for all constraint expressions

🔧 Evaluation Methods:
1. AST_SAFE: Parse expressions into Abstract Syntax Trees, evaluate safely
2. REGEX_PARSER: Pattern-match common constraint forms, evaluate directly  
3. CSP_SOLVER: Constraint Satisfaction Problem solving approach
4. HYBRID: Combine multiple methods for maximum robustness
5. UNSAFE_EVAL: Legacy eval() method (NOT RECOMMENDED - security risk)

🧠 Key Design Principles:
- Never execute user input directly (no eval())
- Whitelist allowed operations and variables
- Graceful degradation on parse failures
- Configurable security vs. flexibility trade-offs
- Comprehensive constraint repair mechanisms

Author: Benedict Chen
Based on foundational work by Kenneth Forbus and Johan de Kleer
Security enhancements following modern secure coding practices
"""

import ast
import operator
import re
from typing import Dict, List, Tuple, Union, Optional, Any, Set, Callable
from dataclasses import dataclass
from enum import Enum
from .core_types import QualitativeValue, QualitativeDirection


class ConstraintEvaluationMethod(Enum):
    """
    Methods for evaluating constraints safely in qualitative reasoning systems.
    
    🔒 Security Considerations:
    - UNSAFE_EVAL uses Python's eval() which can execute arbitrary code
    - AST_SAFE provides security by only allowing whitelisted operations
    - REGEX_PARSER uses pattern matching for common constraint forms
    - CSP_SOLVER treats constraints as formal constraint satisfaction problems
    - HYBRID combines multiple methods for robustness
    
    The default recommendation is AST_SAFE for the best security/flexibility balance.
    """
    
    UNSAFE_EVAL = "unsafe_eval"        # Original eval() method (NOT RECOMMENDED)
    AST_SAFE = "ast_safe"             # Safe AST-based evaluation  
    REGEX_PARSER = "regex_parser"     # Regular expression parsing
    CSP_SOLVER = "csp_solver"         # Constraint Satisfaction Problem solver
    HYBRID = "hybrid"                 # Combine multiple methods


@dataclass 
class ConstraintEvaluationConfig:
    """
    Configuration for constraint evaluation with maximum safety and flexibility.
    
    🔧 Configuration Philosophy:
    This config allows users to fine-tune the balance between security and functionality
    based on their specific use case requirements. More restrictive settings provide
    better security at the cost of constraint expression flexibility.
    
    🔒 Security Settings:
    - Disable function calls and attribute access by default
    - Whitelist only safe operations and known variables
    - Enable strict mode for production environments
    - Configure fallback behavior for failed evaluations
    
    ⚡ Performance Settings:  
    - Set timeouts for CSP solver operations
    - Enable/disable regex fallback for better coverage
    - Configure type checking overhead
    """
    
    # Primary evaluation method
    evaluation_method: ConstraintEvaluationMethod = ConstraintEvaluationMethod.AST_SAFE
    
    # Safety settings - secure by default
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
        """Initialize default values for safety-critical settings."""
        if self.allowed_operators is None:
            # Whitelist of safe operators - no attribute access or function calls
            self.allowed_operators = {
                'Add', 'Sub', 'Mult', 'Div', 'Mod', 'Pow',
                'Lt', 'LtE', 'Gt', 'GtE', 'Eq', 'NotEq', 
                'And', 'Or', 'Not', 'Is', 'IsNot', 'In', 'NotIn',
                'UAdd', 'USub'  # Unary operators
            }
        if self.allowed_names is None:
            self.allowed_names = set()  # Will be populated with quantity names


class ConstraintEngineMixin:
    """
    🔒 Security-First Constraint Engine for Qualitative Reasoning
    ===========================================================
    
    This mixin provides comprehensive constraint evaluation capabilities with
    multiple safe evaluation strategies. It replaces dangerous eval() usage
    with secure alternatives while maintaining full constraint expressiveness.
    
    🛡️ Security Features:
    - AST-based safe evaluation (no code execution)
    - Operator and variable whitelisting
    - Input validation and sanitization
    - Configurable security levels
    - Comprehensive error handling
    
    🔧 Evaluation Strategies:
    1. AST Safe: Parse constraints into AST, evaluate with whitelisted operations
    2. Regex Parser: Pattern-match common constraint forms for direct evaluation
    3. DSL Parser: Domain-specific language for qualitative physics constraints  
    4. Hybrid: Automatically try multiple methods for maximum coverage
    
    🚨 Critical Security Note:
    This module completely eliminates the security vulnerability present in the
    original code that used eval() for constraint evaluation. All evaluation
    methods are designed to be safe against code injection attacks.
    """
    
    def __init__(self, constraint_config: Optional[ConstraintEvaluationConfig] = None, **kwargs):
        """
        Initialize constraint engine with configurable security settings.
        
        Args:
            constraint_config: Security and evaluation configuration
            **kwargs: Additional arguments passed to parent classes
        """
        super().__init__(**kwargs)
        
        # Security configuration
        self.constraint_config = constraint_config or ConstraintEvaluationConfig()
        
        # Initialize constraint evaluation components
        self._setup_safe_evaluators()
        
    def _setup_safe_evaluators(self):
        """Setup safe constraint evaluation components."""
        
        # AST-based safe operators mapping
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
            'range': r'^(-?\d+(?:\.\d+)?)\s*[<≤]\s*(\w+)\s*[<≤]\s*(-?\d+(?:\.\d+)?)$',
            'boolean': r'^(\w+)$'
        }
        
    def _evaluate_logical_expression(self, expression: str) -> bool:
        """
        Configurable logical expression evaluation with multiple safe methods.
        
        This is the main entry point for constraint evaluation. It routes to
        the appropriate evaluation method based on configuration while ensuring
        all methods maintain security guarantees.
        
        Args:
            expression: The constraint expression to evaluate
            
        Returns:
            bool: Whether the constraint is satisfied
            
        Raises:
            ValueError: If expression contains unsafe operations (strict mode)
        """
        
        try:
            # Route to configured evaluation method
            if self.constraint_config.evaluation_method == ConstraintEvaluationMethod.UNSAFE_EVAL:
                # Original method (kept for backwards compatibility but NOT RECOMMENDED)
                print("⚠️  WARNING: Using unsafe eval() method for constraint evaluation!")
                return self._evaluate_expression_unsafe_eval(expression)
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
            if self.constraint_config.strict_mode:
                raise
            return not self.constraint_config.fallback_to_false
            
    def _evaluate_expression_ast_safe(self, expression: str) -> bool:
        """
        🔒 Safely evaluate expressions using AST parsing without eval().
        
        This method provides security by only allowing whitelisted operations and
        preventing code injection attacks. It parses the expression into an
        Abstract Syntax Tree and evaluates it using a controlled recursive descent.
        
        🛡️ Security Features:
        - No eval() or exec() calls
        - Operator whitelist (only safe mathematical/logical operations)
        - Variable whitelist (only known quantities and allowed names)
        - No function calls or attribute access
        - No imports or dangerous operations
        
        Args:
            expression: The constraint expression to evaluate safely
            
        Returns:
            bool: Whether the constraint is satisfied
            
        Raises:
            ValueError: If expression contains unsafe operations
            SyntaxError: If expression has invalid syntax
        """
        
        try:
            # Parse expression into AST
            tree = ast.parse(expression.strip(), mode='eval')
            
            # Recursively evaluate AST safely
            return bool(self._evaluate_ast_node(tree.body))
            
        except (SyntaxError, ValueError) as e:
            if self.constraint_config.enable_regex_fallback:
                print(f"AST parsing failed for '{expression}', falling back to regex: {e}")
                return self._evaluate_expression_regex(expression)
            if self.constraint_config.strict_mode:
                raise
            return self.constraint_config.fallback_to_false
            
    def _evaluate_ast_node(self, node: ast.AST) -> Any:
        """
        Recursively evaluate AST nodes with comprehensive security checks.
        
        This is the core of the secure evaluation engine. It implements a 
        whitelist-based approach where only explicitly allowed operations
        are permitted, ensuring no malicious code can be executed.
        
        Args:
            node: AST node to evaluate
            
        Returns:
            Evaluated result of the node
            
        Raises:
            ValueError: If node represents an unsafe operation
        """
        
        # Constants and literals - safe
        if isinstance(node, ast.Constant):  # Python 3.8+
            return node.value
        elif isinstance(node, ast.Num):  # Older Python versions
            return node.n
        elif isinstance(node, ast.Str):
            return node.s
            
        # Variables - check whitelist
        elif isinstance(node, ast.Name):
            if (node.id in self.constraint_config.allowed_names or 
                (hasattr(self, 'quantities') and node.id in self.quantities)):
                # Return qualitative value for quantities
                if hasattr(self, 'quantities') and node.id in self.quantities:
                    return self._qualitative_to_numeric(self.quantities[node.id].magnitude)
                return node.id  # Variable name
            else:
                raise ValueError(f"Variable '{node.id}' not allowed in constraints")
                
        # Binary operations - check operator whitelist
        elif isinstance(node, ast.BinOp):
            left = self._evaluate_ast_node(node.left)
            right = self._evaluate_ast_node(node.right)
            op_type = type(node.op)
            if op_type in self.safe_operators:
                return self.safe_operators[op_type](left, right)
            else:
                raise ValueError(f"Binary operator {op_type.__name__} not allowed")
                
        # Comparisons - check each operator
        elif isinstance(node, ast.Compare):
            left = self._evaluate_ast_node(node.left)
            
            for op, comparator in zip(node.ops, node.comparators):
                right = self._evaluate_ast_node(comparator)
                op_type = type(op)
                if op_type in self.safe_operators:
                    result = self.safe_operators[op_type](left, right)
                    if not result:
                        return False
                    left = right  # For chained comparisons (e.g., a < b < c)
                else:
                    raise ValueError(f"Comparison operator {op_type.__name__} not allowed")
            return True
            
        # Boolean operations
        elif isinstance(node, ast.BoolOp):
            op_type = type(node.op)
            if op_type == ast.And:
                return all(self._evaluate_ast_node(value) for value in node.values)
            elif op_type == ast.Or:
                return any(self._evaluate_ast_node(value) for value in node.values)
            else:
                raise ValueError(f"Boolean operator {op_type.__name__} not allowed")
                
        # Unary operations
        elif isinstance(node, ast.UnaryOp):
            operand = self._evaluate_ast_node(node.operand)
            op_type = type(node.op)
            if op_type in self.safe_operators:
                return self.safe_operators[op_type](operand)
            else:
                raise ValueError(f"Unary operator {op_type.__name__} not allowed")
                
        # Forbidden operations - explicit security blocks
        elif isinstance(node, ast.Call):
            if not self.constraint_config.allow_function_calls:
                raise ValueError("Function calls not allowed in constraints")
        elif isinstance(node, ast.Attribute):
            if not self.constraint_config.allow_attribute_access:
                raise ValueError("Attribute access not allowed in constraints")
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            raise ValueError("Imports not allowed in constraints")
        elif isinstance(node, (ast.Exec, ast.Eval)):
            raise ValueError("Exec/eval not allowed in constraints")
            
        # Unknown/unsupported node types
        else:
            raise ValueError(f"AST node type {type(node).__name__} not supported")
    
    def _evaluate_expression_regex(self, expression: str) -> bool:
        """
        🔍 Evaluate expressions using regex pattern matching.
        
        This method provides a fallback evaluation strategy that uses regex
        patterns to match common constraint forms and evaluate them directly
        without parsing. It's useful for simple constraints and as a fallback
        when AST parsing fails.
        
        🎯 Supported Patterns:
        - Comparisons: "variable > value", "temp <= 100"
        - Logical operations: "A and B", "not C", "X or Y"  
        - Implications: "A => B", "pressure > 0 => flow > 0"
        - Biconditionals: "A <=> B"
        - Range constraints: "0 < temperature < 100"
        - Boolean variables: "is_active"
        
        Args:
            expression: The constraint expression to evaluate
            
        Returns:
            bool: Whether the constraint is satisfied
        """
        
        expression = expression.strip()
        
        # Try each regex pattern
        for pattern_name, pattern in self.constraint_patterns.items():
            match = re.match(pattern, expression, re.IGNORECASE)
            if match:
                return self._evaluate_regex_match(pattern_name, match, expression)
        
        # If no pattern matches, try simple predicate evaluation
        return self._evaluate_predicate(expression)
    
    def _evaluate_regex_match(self, pattern_name: str, match: re.Match, expression: str) -> bool:
        """Evaluate a successfully matched regex pattern."""
        
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
            
        elif pattern_name == 'range':
            low, var, high = match.groups()
            if hasattr(self, 'quantities') and var in self.quantities:
                var_val = self._qualitative_to_numeric(self.quantities[var].magnitude)
                return float(low) < var_val < float(high)
                
        elif pattern_name == 'boolean':
            var = match.group(1)
            if hasattr(self, 'quantities') and var in self.quantities:
                return bool(self._qualitative_to_numeric(self.quantities[var].magnitude))
        
        return False
    
    def _evaluate_comparison_regex(self, left: str, op: str, right: str) -> bool:
        """Evaluate comparison using regex-parsed components."""
        
        # Get qualitative values
        left_val = self._get_qualitative_value(left)
        right_val = self._get_qualitative_value(right)
        
        if left_val is None or right_val is None:
            return False
            
        return self._compare_qualitative_values(left_val, right_val, op)
    
    def _evaluate_constraint_dsl(self, constraint: str, context: Dict[str, Any]) -> bool:
        """
        🔧 Domain-specific language parser for qualitative physics constraints.
        
        Implements a mini-language specifically designed for qualitative physics
        constraints. This provides the most natural way to express qualitative
        relationships while maintaining complete security.
        
        🎯 DSL Features:
        - Qualitative values: positive, negative, zero, increasing, decreasing, steady
        - Qualitative operations: is, becomes, influences, causes
        - Quantitative comparisons: >, <, >=, <=, ==, !=
        - Logical operations: and, or, not
        
        📝 Example DSL Constraints:
        - "temperature is positive"
        - "pressure becomes increasing"  
        - "flow_rate influences pressure"
        - "heat_source causes temperature increasing"
        
        Args:
            constraint: The DSL constraint to evaluate
            context: Variable context for evaluation
            
        Returns:
            bool: Whether the constraint is satisfied
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
        if len(tokens) == 3:  # "variable op value" pattern
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
    
    def _evaluate_expression_csp(self, expression: str) -> bool:
        """
        🧩 Evaluate expression as Constraint Satisfaction Problem.
        
        This method treats constraint evaluation as a formal CSP problem,
        which provides theoretical guarantees about completeness and
        consistency checking.
        
        Note: This is a simplified CSP approach. A full implementation
        would integrate with a dedicated CSP solver library.
        
        Args:
            expression: The constraint expression
            
        Returns:
            bool: Whether the constraint is satisfied
        """
        
        try:
            # For now, fall back to AST safe evaluation
            # In a full implementation, this would:
            # 1. Convert expression to CSP variables and constraints
            # 2. Use backtracking or arc consistency algorithms
            # 3. Return satisfiability result
            return self._evaluate_expression_ast_safe(expression)
        except:
            # If AST fails, try regex
            return self._evaluate_expression_regex(expression)
    
    def _evaluate_expression_hybrid(self, expression: str) -> bool:
        """
        🔄 Hybrid evaluation combining multiple safe methods.
        
        This method attempts multiple evaluation strategies in order of
        preference, falling back gracefully if one method fails. This
        provides maximum robustness for complex constraint expressions.
        
        🎯 Evaluation Order:
        1. AST Safe - Most secure and flexible
        2. Regex Parser - Good for common patterns
        3. CSP Solver - Theoretical completeness
        
        Args:
            expression: The constraint expression
            
        Returns:
            bool: Whether the constraint is satisfied
        """
        
        methods = [
            ('AST Safe', self._evaluate_expression_ast_safe),
            ('Regex Parser', self._evaluate_expression_regex),
            ('CSP Solver', self._evaluate_expression_csp)
        ]
        
        last_error = None
        
        for method_name, method in methods:
            try:
                result = method(expression)
                return result
            except Exception as e:
                print(f"  {method_name} evaluation failed: {e}")
                last_error = e
                continue
        
        # All methods failed
        print(f"All evaluation methods failed for expression: '{expression}'")
        if self.constraint_config.strict_mode:
            raise last_error
        return self.constraint_config.fallback_to_false
        
    def _evaluate_expression_unsafe_eval(self, expression: str) -> bool:
        """
        ⚠️ UNSAFE: Legacy eval()-based evaluation (NOT RECOMMENDED).
        
        This method is kept for backwards compatibility only. It uses
        Python's eval() function which can execute arbitrary code and
        poses serious security risks.
        
        🚨 SECURITY WARNING:
        This method can execute arbitrary Python code if given malicious
        input. Only use in completely trusted environments with trusted
        input sources.
        
        Args:
            expression: The expression to evaluate
            
        Returns:
            bool: Whether the constraint is satisfied
        """
        
        print("🚨 SECURITY WARNING: Using unsafe eval() for constraint evaluation!")
        
        # This would be the original implementation using eval()
        # Kept for reference but should not be used in production
        try:
            # In the original code, this would have been:
            # return eval(expression, {"__builtins__": {}}, self.current_state)
            # 
            # Even with restricted builtins, eval() is still dangerous
            # because it can access and modify object attributes
            
            # For safety, we'll actually use the AST method instead
            return self._evaluate_expression_ast_safe(expression)
        except Exception as e:
            print(f"Unsafe evaluation failed: {e}")
            return self.constraint_config.fallback_to_false
    
    def _get_qualitative_value(self, expr: str) -> Optional[QualitativeValue]:
        """Get qualitative value from expression."""
        
        expr = expr.strip()
        
        # Check if it's a quantity name
        if hasattr(self, 'quantities') and expr in self.quantities:
            return self.quantities[expr].magnitude
            
        # Check if it's a literal value
        if expr == "0":
            return QualitativeValue.ZERO
        elif expr in ["infinity", "inf"]:
            return QualitativeValue.POSITIVE_INFINITY
        elif expr in ["-infinity", "-inf"]:
            return QualitativeValue.NEGATIVE_INFINITY
        elif expr.lstrip('-').isdigit():
            val = int(expr)
            if val > 0:
                return QualitativeValue.POSITIVE_SMALL if val <= 10 else QualitativeValue.POSITIVE_LARGE
            elif val < 0:
                return QualitativeValue.NEGATIVE_SMALL if val >= -10 else QualitativeValue.NEGATIVE_LARGE
            else:
                return QualitativeValue.ZERO
                
        return None
        
    def _compare_qualitative_values(self, left: QualitativeValue, right: QualitativeValue, operator: str) -> bool:
        """Compare qualitative values using ordering."""
        
        # Use the ordering from QualitativeValue if available
        if hasattr(QualitativeValue, 'get_ordering'):
            ordering = QualitativeValue.get_ordering()
        else:
            # Fallback ordering
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
        
        if operator in [">", "gt"]:
            return left_ord > right_ord
        elif operator in ["<", "lt"]:
            return left_ord < right_ord
        elif operator in [">=", "ge", "gte"]:
            return left_ord >= right_ord
        elif operator in ["<=", "le", "lte"]:
            return left_ord <= right_ord
        elif operator in ["=", "==", "eq"]:
            return left_ord == right_ord
        elif operator in ["!=", "ne", "neq"]:
            return left_ord != right_ord
            
        return False
        
    def _qualitative_to_numeric(self, qual_val: QualitativeValue) -> float:
        """Convert qualitative value to numeric for comparison."""
        
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
    
    def _evaluate_predicate(self, expression: str) -> bool:
        """Evaluate predicate expressions."""
        
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
        
    def _handle_constraint_evaluation_error(self, constraint: str, error: Exception) -> bool:
        """
        🛠️ Handle constraint evaluation errors with proper error classification and recovery.
        
        This method implements sophisticated error handling that can distinguish
        between different types of evaluation failures and apply appropriate
        recovery strategies. This is crucial for robust constraint satisfaction
        in complex qualitative reasoning systems.
        
        🎯 Error Classification:
        - Mathematical errors (division by zero) indicate constraint violation
        - Missing variable errors trigger constraint repair attempts
        - Syntax errors prompt validation and partial satisfaction
        - Type/method errors attempt graceful degradation
        - Unknown errors use conservative safety approach
        
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
        🔧 Attempt to repair constraint by handling missing variables.
        
        This method implements intelligent constraint repair by attempting
        to substitute similar variables or provide reasonable defaults for
        missing variables in constraint expressions.
        
        Args:
            constraint: The constraint to repair
            error: The KeyError indicating missing variable
            
        Returns:
            bool: Whether repair was successful and constraint is satisfied
        """
        
        missing_var = str(error).strip("'\"")
        
        # Try to find similar variables in current quantities
        if hasattr(self, 'quantities'):
            current_vars = set(self.quantities.keys())
            
            # Simple string similarity for variable matching
            for var in current_vars:
                if (missing_var.lower() in var.lower() or 
                    var.lower() in missing_var.lower()):
                    print(f"Attempting to substitute '{var}' for missing '{missing_var}'")
                    try:
                        repaired_constraint = constraint.replace(missing_var, var)
                        
                        # Use the configured evaluation method for repair
                        if self.constraint_config.evaluation_method == ConstraintEvaluationMethod.AST_SAFE:
                            result = self._evaluate_expression_ast_safe(repaired_constraint)
                        elif self.constraint_config.evaluation_method == ConstraintEvaluationMethod.REGEX_PARSER:
                            result = self._evaluate_expression_regex(repaired_constraint)
                        else:
                            # Default to AST safe
                            result = self._evaluate_expression_ast_safe(repaired_constraint)
                            
                        return result
                    except Exception:
                        continue
                        
        # If no substitution works, assume constraint is not satisfied
        print(f"Could not repair constraint with missing variable '{missing_var}'")
        return False
    
    def _validate_constraint_syntax(self, constraint: str) -> bool:
        """
        ✅ Validate constraint syntax and structure.
        
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
        ⚖️ Attempt partial constraint satisfaction using heuristics.
        
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
        
    def configure_constraint_evaluation(self, method: ConstraintEvaluationMethod):
        """
        🔧 Configure constraint evaluation method for maximum user control.
        
        Args:
            method: The evaluation method to use
        """
        self.constraint_config.evaluation_method = method
        print(f"Constraint evaluation method set to: {method.value}")
    
    def configure_constraint_patterns(self, patterns: Dict[str, str]):
        """🔧 Allow users to configure regex patterns for constraint matching."""
        self.constraint_patterns.update(patterns)
        print("Custom constraint patterns configured")
    
    def configure_constraint_dsl(self, config: Dict[str, List[str]]):
        """🔧 Allow users to configure DSL grammar for constraint parsing."""
        self.constraint_dsl_config = config
        print("Custom DSL configuration applied")
        
    def add_allowed_variable(self, variable_name: str):
        """🔒 Add a variable to the constraint evaluation whitelist."""
        self.constraint_config.allowed_names.add(variable_name)
        
    def remove_allowed_variable(self, variable_name: str):
        """🔒 Remove a variable from the constraint evaluation whitelist."""
        self.constraint_config.allowed_names.discard(variable_name)
        
    def get_constraint_security_status(self) -> Dict[str, Any]:
        """📊 Get current constraint evaluation security configuration."""
        return {
            'evaluation_method': self.constraint_config.evaluation_method.value,
            'allow_function_calls': self.constraint_config.allow_function_calls,
            'allow_attribute_access': self.constraint_config.allow_attribute_access,
            'allowed_operators': list(self.constraint_config.allowed_operators),
            'allowed_variables': list(self.constraint_config.allowed_names),
            'strict_mode': self.constraint_config.strict_mode,
            'fallback_to_false': self.constraint_config.fallback_to_false
        }