"""
🧠 Qualitative Reasoning - Modular Core Integration
==================================================

This module provides the integrated qualitative reasoning core that combines all the 
extracted modular components into a unified, easy-to-use interface while maintaining
full backward compatibility with the original implementation.

📚 Theoretical Foundation:
Forbus, K. D., & de Kleer, J. (1993). "Building Problem Solvers", MIT Press
de Kleer, J., & Brown, J. S. (1984). "A Qualitative Physics Based on Confluences"

🎯 Modular Architecture:
This core integrates six specialized mixins:
1. ConstraintEngineMixin - Security-critical constraint evaluation
2. ProcessEngineMixin - Process theory and causal reasoning  
3. SimulationEngineMixin - Qualitative simulation and state transitions
4. AnalysisEngineMixin - Relationship analysis and behavior explanation
5. VisualizationEngineMixin - Visualization and reporting
6. Core types - Fundamental data structures

🌟 Key Features:
- Complete backward compatibility with original API
- Modular design for easy extension and maintenance
- Security-first constraint evaluation (no eval() vulnerabilities)
- Comprehensive analysis and visualization capabilities
- Factory functions for common use cases
- Rich documentation and type hints

🔧 Usage Examples:

Basic Usage:
    reasoner = QualitativeReasoner("Heat Transfer System")
    reasoner.add_quantity("temperature", QualitativeValue.POSITIVE_SMALL)
    reasoner.add_process("heating", ["heat_source_present"], ["temperature > 0"], ["I+(temperature)"])
    reasoner.run_simulation("step1")

Educational Use:
    reasoner = create_educational_reasoner("Physics Demo")
    # Pre-configured for learning with detailed explanations
    
Research Use:
    reasoner = create_research_reasoner("Advanced System", enable_predictions=True)
    # Full analytical capabilities enabled

Production Use:
    reasoner = create_production_reasoner("Industrial System", security_level="high")
    # Maximum security and performance optimization

🏗️ Architecture:
The QualitativeReasoner class inherits from all specialized mixins using multiple
inheritance, providing access to all capabilities while maintaining clean separation
of concerns. Each mixin handles a specific aspect of qualitative reasoning.

Author: Benedict Chen
Based on foundational work by Kenneth Forbus and Johan de Kleer
Modular architecture following best practices for maintainable AI systems
"""

from typing import Dict, List, Tuple, Union, Optional, Any, Set
from dataclasses import dataclass
import warnings

# Import all core types and utilities
from .qr_modules.core_types import (
    QualitativeValue, QualitativeDirection, QualitativeQuantity, 
    QualitativeState, QualitativeProcess,
    compare_qualitative_values, qualitative_to_numeric, numeric_to_qualitative,
    create_quantity, validate_qualitative_state,
    QValue, QDirection, QQuantity, QState, QProcess
)

# Import all engine mixins
from .qr_modules.constraint_engine import (
    ConstraintEngineMixin, ConstraintEvaluationMethod, ConstraintEvaluationConfig
)
from .qr_modules.process_engine import ProcessEngineMixin
from .qr_modules.simulation_engine import SimulationEngineMixin  
from .qr_modules.analysis_engine import (
    AnalysisEngineMixin, CausalChain, RelationshipAnalysis, BehaviorExplanation
)
from .qr_modules.visualization_engine import (
    VisualizationEngineMixin, VisualizationConfig, VisualizationReport
)


class QualitativeReasoner(
    ConstraintEngineMixin,
    ProcessEngineMixin, 
    SimulationEngineMixin,
    AnalysisEngineMixin,
    VisualizationEngineMixin
):
    """
    🧠 Integrated Qualitative Reasoning System
    ==========================================
    
    This class provides the complete qualitative reasoning system by integrating
    all specialized mixins into a unified interface. It maintains full backward
    compatibility with the original implementation while providing enhanced
    modularity, security, and analysis capabilities.
    
    🔬 Theoretical Foundation:
    Based on Forbus's Process Theory and de Kleer's Qualitative Physics framework,
    this system models physical phenomena using qualitative relationships rather
    than precise numerical values, enabling AI to understand physics the way
    humans do - through cause-and-effect reasoning.
    
    🏗️ Architecture:
    The system is built using multiple inheritance from specialized mixins:
    
    - **ConstraintEngineMixin**: Secure constraint evaluation without eval()
    - **ProcessEngineMixin**: Process activation and causal influence application
    - **SimulationEngineMixin**: Temporal state evolution and prediction
    - **AnalysisEngineMixin**: Behavioral explanation and relationship inference
    - **VisualizationEngineMixin**: Rich visualization and reporting capabilities
    
    🎯 Key Capabilities:
    - Qualitative quantity modeling with magnitudes and directions
    - Process-based causal reasoning and influence application
    - Safe constraint evaluation using multiple security methods
    - Temporal simulation with state history tracking
    - Advanced behavioral analysis and explanation generation
    - Rich visualization and multi-format export capabilities
    - Future state prediction and scenario analysis
    
    💡 Usage Philosophy:
    This system is designed to be:
    - **Intuitive**: Easy to understand and use for domain experts
    - **Secure**: Safe constraint evaluation without code injection risks
    - **Extensible**: Modular design allows easy addition of new capabilities
    - **Educational**: Rich explanations help users understand system behavior
    - **Research-Ready**: Advanced analysis tools for scientific investigation
    """
    
    def __init__(self, 
                 domain_name: str = "Generic Physical System", 
                 constraint_config: Optional[ConstraintEvaluationConfig] = None,
                 visualization_config: Optional[VisualizationConfig] = None,
                 verbose: bool = True):
        """
        Initialize the Qualitative Reasoning System
        
        Args:
            domain_name: Name of the physical domain being modeled
            constraint_config: Configuration for safe constraint evaluation
            visualization_config: Configuration for visualization and reporting
            verbose: Whether to print initialization and operation messages
            
        🧠 Initialization Process:
        1. **Core Setup**: Initialize basic data structures and settings
        2. **Security Configuration**: Setup safe constraint evaluation
        3. **Engine Initialization**: Initialize all specialized mixins
        4. **Causal Graph**: Prepare causal relationship tracking
        5. **History Management**: Setup temporal state tracking
        6. **Visualization**: Configure output and reporting systems
        
        🔒 Security Features:
        The system is initialized with secure-by-default settings:
        - AST-based constraint evaluation (no eval() by default)
        - Whitelisted operations and variables
        - Configurable security levels for different use cases
        - Comprehensive error handling and recovery
        """
        
        # Store configuration
        self.domain_name = domain_name
        self._verbose = verbose
        
        # Initialize core data structures
        self.quantities: Dict[str, QualitativeQuantity] = {}
        self.processes: Dict[str, QualitativeProcess] = {}
        self.constraints: List[str] = []
        self.landmarks: Dict[str, List[float]] = {}
        
        # Initialize temporal tracking
        self.state_history: List[QualitativeState] = []
        self.current_state: Optional[QualitativeState] = None
        
        # Initialize all mixin components individually
        # Each mixin has a different initialization signature
        ConstraintEngineMixin.__init__(self, constraint_config=constraint_config)
        ProcessEngineMixin.__init__(self)
        SimulationEngineMixin.__init__(self)
        AnalysisEngineMixin.__init__(self)
        VisualizationEngineMixin.__init__(self)
        
        # Configure visualization if provided
        if visualization_config:
            self._viz_config = visualization_config
        
        # Display initialization status
        if self._verbose:
            print(f"✓ Qualitative Reasoner initialized for: {domain_name}")
            print(f"  📊 Modules loaded: Constraint, Process, Simulation, Analysis, Visualization")
            print(f"  🔒 Security method: {self.constraint_config.evaluation_method.value}")
            print(f"  🎨 Visualization: {self._viz_config.detail_level} detail level")
            print()
            
    def add_quantity(self, 
                    name: str, 
                    initial_magnitude: QualitativeValue = QualitativeValue.ZERO,
                    initial_direction: QualitativeDirection = QualitativeDirection.STEADY,
                    landmarks: Optional[List[float]] = None,
                    units: Optional[str] = None,
                    description: Optional[str] = None) -> QualitativeQuantity:
        """
        Add a qualitative quantity to the system
        
        Args:
            name: Unique identifier for the quantity
            initial_magnitude: Starting qualitative magnitude
            initial_direction: Starting qualitative direction (trend)
            landmarks: Optional landmark values for behavioral boundaries
            units: Optional physical units for documentation
            description: Optional human-readable description
            
        Returns:
            QualitativeQuantity: The created quantity object
            
        🔬 Quantity Theory:
        In qualitative physics, quantities are represented as [magnitude, direction]
        pairs that capture both the current state and the trend. This enables
        reasoning about system dynamics without precise numerical values.
        
        Example:
            >>> reasoner.add_quantity("temperature", QualitativeValue.POSITIVE_SMALL, 
            ...                       QualitativeDirection.INCREASING, 
            ...                       landmarks=[0.0, 100.0], units="°C")
        """
        
        quantity = QualitativeQuantity(
            name=name,
            magnitude=initial_magnitude,
            direction=initial_direction,
            landmark_values=landmarks or [],
            units=units,
            description=description
        )
        
        self.quantities[name] = quantity
        
        # Add to allowed names for safe constraint evaluation
        self.add_allowed_variable(name)
        
        # Store landmarks
        if landmarks:
            self.landmarks[name] = sorted(landmarks)
            
        if self._verbose:
            print(f"   Added quantity: {name} = {initial_magnitude.value}, trend: {initial_direction.value}")
            if units:
                print(f"     Units: {units}")
            if landmarks:
                print(f"     Landmarks: {landmarks}")
                
        return quantity
        
    def add_constraint(self, constraint: str):
        """
        Add a constraint to maintain system consistency
        
        Args:
            constraint: Logical expression representing the constraint
            
        🔒 Security Note:
        Constraints are evaluated using the configured security method (AST-safe by default).
        This prevents code injection attacks while maintaining full expressiveness.
        
        Supported constraint formats:
        - Comparisons: "temperature > 0", "pressure != 0"
        - Logical: "A and B", "not C", "X or Y"  
        - Implications: "pressure > 0 => flow > 0"
        - Complex: "temperature > 0 and pressure > 0 => flow_rate > 0"
        
        Example:
            >>> reasoner.add_constraint("temperature > 0 => pressure > 0")
        """
        
        self.constraints.append(constraint)
        
        if self._verbose:
            print(f"   Added constraint: {constraint}")
            
    def run_simulation(self, step_name: str) -> QualitativeState:
        """
        Run one step of qualitative simulation
        
        Args:
            step_name: Identifier for this simulation step
            
        Returns:
            QualitativeState: The resulting system state
            
        🚀 Simulation Process:
        This method executes the complete qualitative simulation cycle:
        1. **Process Evaluation**: Determine which processes are active
        2. **Influence Application**: Apply process influences to quantities  
        3. **State Evolution**: Update quantity magnitudes based on directions
        4. **Constraint Checking**: Verify system consistency
        5. **Analysis**: Derive relationships and generate explanations
        6. **Visualization**: Display current state and changes
        
        This is the primary method for advancing the system through qualitative time.
        
        Example:
            >>> state = reasoner.run_simulation("heating_phase_1")
            >>> print(f"System now at: {state.time_point}")
        """
        
        if self._verbose:
            print(f"\n🚀 Running simulation step: {step_name}")
            
        # Execute simulation step (from SimulationEngineMixin)
        current_state = self.qualitative_simulation_step(step_name)
        
        # Display results (from VisualizationEngineMixin) 
        # Note: visualization is automatically called in simulation step
        
        return current_state
        
    def explain_quantity(self, quantity_name: str, depth: int = 3) -> BehaviorExplanation:
        """
        Generate comprehensive explanation of quantity behavior
        
        Args:
            quantity_name: Name of quantity to explain
            depth: Maximum depth of causal chain analysis
            
        Returns:
            BehaviorExplanation: Comprehensive behavioral explanation
            
        🧠 Explanation Philosophy:
        This method provides human-understandable explanations by tracing the
        causal chains from processes to quantity changes, following Forbus's
        approach to causal explanation in qualitative physics.
        
        Example:
            >>> explanation = reasoner.explain_quantity("temperature")
            >>> print(f"Primary causes: {explanation.primary_causes}")
            >>> print(f"Confidence: {explanation.confidence:.2f}")
        """
        
        # Use the AnalysisEngineMixin's explain_behavior method explicitly
        return AnalysisEngineMixin.explain_behavior(self, quantity_name, depth)
        
    def predict_future(self, n_steps: int = 5) -> List[QualitativeState]:
        """
        Predict future qualitative states
        
        Args:
            n_steps: Number of future steps to predict
            
        Returns:
            List[QualitativeState]: Sequence of predicted future states
            
        🔮 Prediction Theory:
        Qualitative prediction leverages the stability of process activations
        and the deterministic nature of qualitative transitions to forecast
        system evolution without requiring precise numerical parameters.
        
        Example:
            >>> predictions = reasoner.predict_future(3)
            >>> for i, state in enumerate(predictions, 1):
            ...     print(f"Step {i}: {len(state.quantities)} quantities")
        """
        
        return self.predict_future_states(n_steps)
        
    def generate_report(self, 
                       format_type: str = "text",
                       include_history: bool = True,
                       include_predictions: bool = False,
                       detail_level: str = "medium") -> str:
        """
        Generate comprehensive system analysis report
        
        Args:
            format_type: Report format ("text", "markdown", "json")
            include_history: Whether to include state history
            include_predictions: Whether to include future predictions
            detail_level: Level of detail ("basic", "medium", "detailed", "comprehensive")
            
        Returns:
            str: Formatted report string
            
        📋 Report Components:
        - **Executive Summary**: High-level system status
        - **Current State**: All quantities and their states
        - **Active Processes**: Currently running processes and influences
        - **Relationships**: Derived relationships between quantities
        - **History**: Temporal evolution (if requested)
        - **Predictions**: Future state forecasts (if requested)
        - **Analysis**: Behavioral patterns and insights
        
        Example:
            >>> report = reasoner.generate_report("markdown", include_predictions=True)
            >>> with open("system_report.md", "w") as f:
            ...     f.write(report)
        """
        
        # Generate comprehensive visualization report
        viz_report = self.generate_comprehensive_report(include_predictions)
        
        # Convert to requested format
        if format_type == "text":
            return viz_report.to_text()
        elif format_type == "markdown":
            return viz_report.to_markdown()
        elif format_type == "json":
            return viz_report.to_json()
        else:
            raise ValueError(f"Unsupported format: {format_type}")
            
    def export_system_state(self, 
                           filename: Optional[str] = None,
                           format_type: str = "json") -> str:
        """
        Export complete system state to file or string
        
        Args:
            filename: Optional filename to save to (if None, returns string)
            format_type: Export format ("json", "csv", "markdown", "text")
            
        Returns:
            str: Exported data as string
            
        💾 Export Capabilities:
        - **JSON**: Complete structured data export
        - **CSV**: Tabular data for spreadsheet analysis
        - **Markdown**: Human-readable formatted export
        - **Text**: Plain text summary export
        
        Example:
            >>> data = reasoner.export_system_state("system.json", "json")
            >>> reasoner.export_system_state("quantities.csv", "csv")
        """
        
        return self.export_data(format_type, filename)
        
    def reset_system(self, preserve_structure: bool = True):
        """
        Reset the system to initial state
        
        Args:
            preserve_structure: If True, keeps quantities/processes but resets states
            
        🔄 Reset Options:
        - **Preserve Structure**: Keeps system definition but resets all states
        - **Complete Reset**: Clears everything including quantities and processes
        
        Example:
            >>> reasoner.reset_system(preserve_structure=True)  # Keep definitions
            >>> reasoner.reset_system(preserve_structure=False)  # Clear everything
        """
        
        self.reset_simulation(preserve_structure)
        
        if self._verbose:
            reset_type = "structural" if preserve_structure else "complete"
            print(f"🔄 System reset completed ({reset_type})")
            
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status information
        
        Returns:
            Dict containing complete system metrics and status
            
        📊 Status Information:
        - **Quantities**: Count and current states
        - **Processes**: Activity levels and influences
        - **Constraints**: Satisfaction status
        - **History**: Temporal progression metrics
        - **Analysis**: Relationship and pattern statistics
        - **Health**: Overall system health assessment
        
        Example:
            >>> status = reasoner.get_system_status()
            >>> print(f"System health: {status['health']['overall_health']}")
        """
        
        status = {
            "domain_name": self.domain_name,
            "timestamp": self.current_state.time_point if self.current_state else "initial",
            "quantities": {
                "count": len(self.quantities),
                "states": {name: {
                    "magnitude": qty.magnitude.value,
                    "direction": qty.direction.value
                } for name, qty in self.quantities.items()}
            },
            "processes": {
                "total": len(self.processes),
                "active": len([p for p in self.processes.values() if p.active]),
                "activity_rate": len([p for p in self.processes.values() if p.active]) / max(1, len(self.processes))
            },
            "constraints": {
                "count": len(self.constraints),
                "violations": len(self._get_current_constraint_violations()) if hasattr(self, '_get_current_constraint_violations') else 0
            },
            "history": {
                "steps": len(self.state_history),
                "current_step": self.current_state.time_point if self.current_state else None
            }
        }
        
        # Add health assessment if analysis engine is available
        if hasattr(self, 'generate_behavior_summary'):
            try:
                behavior_summary = self.generate_behavior_summary()
                status["health"] = behavior_summary.get("system_health", {})
                status["patterns"] = behavior_summary.get("behavioral_patterns", {})
            except:
                status["health"] = {"status": "assessment_unavailable"}
                
        return status
        
    def configure_security(self, 
                          method: ConstraintEvaluationMethod = ConstraintEvaluationMethod.AST_SAFE,
                          strict_mode: bool = False,
                          allow_function_calls: bool = False):
        """
        Configure constraint evaluation security settings
        
        Args:
            method: Evaluation method to use
            strict_mode: Whether to fail on any parsing error
            allow_function_calls: Whether to allow function calls in constraints
            
        🔒 Security Configuration:
        - **AST_SAFE**: Recommended for most use cases (default)
        - **REGEX_PARSER**: Good for simple constraints
        - **HYBRID**: Maximum compatibility but slower
        - **UNSAFE_EVAL**: NOT RECOMMENDED (security risk)
        
        Example:
            >>> reasoner.configure_security(ConstraintEvaluationMethod.HYBRID, strict_mode=True)
        """
        
        self.constraint_config.evaluation_method = method
        self.constraint_config.strict_mode = strict_mode
        self.constraint_config.allow_function_calls = allow_function_calls
        
        if self._verbose:
            print(f"🔒 Security configured: {method.value}")
            print(f"  Strict mode: {strict_mode}")
            print(f"  Function calls: {allow_function_calls}")
            
    def configure_visualization(self, **config_options):
        """
        Configure visualization and reporting settings
        
        Args:
            **config_options: Visualization parameters to update
            
        🎨 Visualization Options:
        - detail_level: "basic", "medium", "detailed", "comprehensive"
        - export_format: "text", "json", "markdown", "csv"
        - show_unicode_symbols: Enable/disable trend symbols
        - max_history_items: Number of historical states to show
        
        Example:
            >>> reasoner.configure_visualization(detail_level="comprehensive", 
            ...                                  show_unicode_symbols=True)
        """
        
        super().configure_visualization(**config_options)
        
        if self._verbose:
            print(f"🎨 Visualization configured: {len(config_options)} options updated")

    # Backward compatibility aliases for original API
    def visualize_system_state(self, include_history: bool = True, detail_level: str = None):
        """Backward compatibility alias for system state visualization"""
        return super().visualize_system_state(include_history, detail_level)
    
    def _evaluate_constraint(self, constraint: str) -> bool:
        """Backward compatibility wrapper for constraint evaluation"""
        return self._evaluate_logical_expression(constraint)
        
    def _evaluate_quantity_condition(self, condition: str) -> bool:
        """Backward compatibility wrapper for quantity condition evaluation"""
        # This method is provided by ProcessEngineMixin
        return super()._evaluate_quantity_condition(condition)

    def _check_constraints(self):
        """Check all system constraints for consistency"""
        violations = []
        for constraint in self.constraints:
            try:
                if not self._evaluate_constraint(constraint):
                    violations.append(constraint)
            except Exception as e:
                violations.append(f"{constraint} (error: {e})")
                
        if violations and self._verbose:
            print(f"⚠️  Constraint violations: {len(violations)}")
            for violation in violations[:3]:  # Show first 3
                print(f"   - {violation}")
            if len(violations) > 3:
                print(f"   ... and {len(violations) - 3} more")


# Factory Functions for Common Use Cases
# =====================================

def create_educational_reasoner(domain_name: str = "Educational System") -> QualitativeReasoner:
    """
    Create a qualitative reasoner configured for educational use
    
    Args:
        domain_name: Name of the educational domain
        
    Returns:
        QualitativeReasoner: Pre-configured educational system
        
    🎓 Educational Configuration:
    - Verbose output for learning
    - Detailed explanations enabled
    - Safe constraint evaluation
    - Rich visualization with symbols
    - Comprehensive reporting
    
    Example:
        >>> reasoner = create_educational_reasoner("Physics 101: Heat Transfer")
        >>> # System is ready for educational demonstrations
    """
    
    # Configure for educational use
    constraint_config = ConstraintEvaluationConfig(
        evaluation_method=ConstraintEvaluationMethod.AST_SAFE,
        strict_mode=False,
        fallback_to_false=True,
        enable_regex_fallback=True
    )
    
    viz_config = VisualizationConfig(
        detail_level="detailed",
        show_unicode_symbols=True,
        show_confidence_scores=True,
        include_explanations=True,
        max_history_items=10
    )
    
    reasoner = QualitativeReasoner(
        domain_name=domain_name,
        constraint_config=constraint_config,
        visualization_config=viz_config,
        verbose=True
    )
    
    print("🎓 Educational reasoner created with detailed explanations enabled")
    return reasoner


def create_research_reasoner(domain_name: str = "Research System",
                           enable_predictions: bool = True,
                           max_analysis_depth: int = 5) -> QualitativeReasoner:
    """
    Create a qualitative reasoner configured for research use
    
    Args:
        domain_name: Name of the research domain
        enable_predictions: Whether to enable predictive capabilities
        max_analysis_depth: Maximum depth for causal analysis
        
    Returns:
        QualitativeReasoner: Pre-configured research system
        
    🔬 Research Configuration:
    - Maximum analytical capabilities
    - Advanced prediction algorithms
    - Comprehensive data export
    - Statistical pattern analysis
    - Deep causal chain analysis
    
    Example:
        >>> reasoner = create_research_reasoner("Advanced Thermodynamics", 
        ...                                     enable_predictions=True)
        >>> # Full analytical capabilities available
    """
    
    # Configure for research use
    constraint_config = ConstraintEvaluationConfig(
        evaluation_method=ConstraintEvaluationMethod.HYBRID,
        strict_mode=False,
        enable_regex_fallback=True,
        enable_type_checking=True
    )
    
    viz_config = VisualizationConfig(
        detail_level="comprehensive",
        show_unicode_symbols=True,
        show_confidence_scores=True,
        include_explanations=True,
        include_charts=True,
        max_history_items=20
    )
    
    reasoner = QualitativeReasoner(
        domain_name=domain_name,
        constraint_config=constraint_config,
        visualization_config=viz_config,
        verbose=True
    )
    
    # Configure analysis engine for research
    if hasattr(reasoner, 'configure_analysis'):
        reasoner.configure_analysis(
            explanation_depth=max_analysis_depth,
            enable_statistical_analysis=True,
            enable_predictive_analysis=enable_predictions,
            correlation_threshold=0.5
        )
    
    print("🔬 Research reasoner created with advanced analytics enabled")
    return reasoner


def create_production_reasoner(domain_name: str = "Production System",
                             security_level: str = "high") -> QualitativeReasoner:
    """
    Create a qualitative reasoner configured for production use
    
    Args:
        domain_name: Name of the production domain
        security_level: Security level ("high", "medium", "low")
        
    Returns:
        QualitativeReasoner: Pre-configured production system
        
    🏭 Production Configuration:
    - Maximum security settings
    - Optimized performance
    - Minimal verbose output
    - Error recovery mechanisms
    - Constraint violation monitoring
    
    Example:
        >>> reasoner = create_production_reasoner("Industrial Control", 
        ...                                       security_level="high")
        >>> # Ready for production deployment
    """
    
    # Configure security based on level
    security_configs = {
        "high": ConstraintEvaluationConfig(
            evaluation_method=ConstraintEvaluationMethod.AST_SAFE,
            strict_mode=True,
            allow_function_calls=False,
            allow_attribute_access=False,
            fallback_to_false=False
        ),
        "medium": ConstraintEvaluationConfig(
            evaluation_method=ConstraintEvaluationMethod.HYBRID,
            strict_mode=False,
            allow_function_calls=False,
            enable_regex_fallback=True,
            fallback_to_false=True
        ),
        "low": ConstraintEvaluationConfig(
            evaluation_method=ConstraintEvaluationMethod.REGEX_PARSER,
            strict_mode=False,
            enable_regex_fallback=True,
            fallback_to_false=True
        )
    }
    
    constraint_config = security_configs.get(security_level, security_configs["high"])
    
    # Minimal visualization for production
    viz_config = VisualizationConfig(
        detail_level="basic",
        show_unicode_symbols=False,
        show_confidence_scores=False,
        include_explanations=False,
        max_history_items=5
    )
    
    reasoner = QualitativeReasoner(
        domain_name=domain_name,
        constraint_config=constraint_config,
        visualization_config=viz_config,
        verbose=False  # Minimal output for production
    )
    
    print(f"🏭 Production reasoner created with {security_level} security")
    return reasoner


def create_demo_reasoner(domain_name: str = "Demo System") -> QualitativeReasoner:
    """
    Create a qualitative reasoner configured for demonstrations
    
    Args:
        domain_name: Name of the demo domain
        
    Returns:
        QualitativeReasoner: Pre-configured demo system
        
    🎬 Demo Configuration:
    - Balanced verbosity for presentations
    - Visual symbols for impact
    - Medium detail level
    - Stable constraint evaluation
    - Clear, understandable output
    
    Example:
        >>> reasoner = create_demo_reasoner("Conference Presentation")
        >>> # Perfect for live demonstrations
    """
    
    constraint_config = ConstraintEvaluationConfig(
        evaluation_method=ConstraintEvaluationMethod.AST_SAFE,
        strict_mode=False,
        enable_regex_fallback=True,
        fallback_to_false=True
    )
    
    viz_config = VisualizationConfig(
        detail_level="medium",
        show_unicode_symbols=True,
        show_confidence_scores=False,
        include_explanations=True,
        max_history_items=5
    )
    
    reasoner = QualitativeReasoner(
        domain_name=domain_name,
        constraint_config=constraint_config,
        visualization_config=viz_config,
        verbose=True
    )
    
    print("🎬 Demo reasoner created for presentations")
    return reasoner


# Export all public classes and functions
__all__ = [
    # Main class
    "QualitativeReasoner",
    
    # Core types
    "QualitativeValue", "QualitativeDirection", "QualitativeQuantity", 
    "QualitativeState", "QualitativeProcess",
    
    # Configuration classes
    "ConstraintEvaluationMethod", "ConstraintEvaluationConfig",
    "VisualizationConfig", "VisualizationReport",
    
    # Analysis classes  
    "CausalChain", "RelationshipAnalysis", "BehaviorExplanation",
    
    # Utility functions
    "compare_qualitative_values", "qualitative_to_numeric", "numeric_to_qualitative",
    "create_quantity", "validate_qualitative_state",
    
    # Type aliases
    "QValue", "QDirection", "QQuantity", "QState", "QProcess",
    
    # Factory functions
    "create_educational_reasoner", "create_research_reasoner", 
    "create_production_reasoner", "create_demo_reasoner"
]