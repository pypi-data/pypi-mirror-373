"""
Qualitative Reasoning Package

A comprehensive Python library for qualitative reasoning systems based on
Forbus's Process Theory and de Kleer's Qualitative Physics framework.

This package enables AI systems to reason about physical systems using
qualitative relationships rather than precise numerical values, similar
to how humans understand physics intuitively.

Features:
- Modular architecture with clean separation of concerns
- Security-first constraint evaluation (no eval() vulnerabilities)
- Rich visualization and analysis capabilities
- Factory functions for common use cases
- Full backward compatibility with original implementation

Modules:
- qr_core: Integrated qualitative reasoning core
- qr_modules: Individual specialized components

Author: Benedict Chen
"""

__version__ = "1.0.0"

# Import from the new modular core
from .qr_core import (
    # Main class
    QualitativeReasoner,
    
    # Core types
    QualitativeValue,
    QualitativeDirection,
    QualitativeQuantity,
    QualitativeState, 
    QualitativeProcess,
    
    # Configuration classes
    ConstraintEvaluationMethod,
    ConstraintEvaluationConfig,
    VisualizationConfig,
    VisualizationReport,
    
    # Analysis classes
    CausalChain,
    RelationshipAnalysis,
    BehaviorExplanation,
    
    # Utility functions
    compare_qualitative_values,
    qualitative_to_numeric,
    numeric_to_qualitative,
    create_quantity,
    validate_qualitative_state,
    
    # Type aliases
    QValue,
    QDirection,
    QQuantity,
    QState,
    QProcess,
    
    # Factory functions
    create_educational_reasoner,
    create_research_reasoner,
    create_production_reasoner,
    create_demo_reasoner
)

__all__ = [
    # Main class
    "QualitativeReasoner",
    
    # Core types
    "QualitativeValue",
    "QualitativeDirection", 
    "QualitativeQuantity",
    "QualitativeState",
    "QualitativeProcess",
    
    # Configuration classes
    "ConstraintEvaluationMethod",
    "ConstraintEvaluationConfig", 
    "VisualizationConfig",
    "VisualizationReport",
    
    # Analysis classes
    "CausalChain",
    "RelationshipAnalysis",
    "BehaviorExplanation",
    
    # Utility functions
    "compare_qualitative_values",
    "qualitative_to_numeric",
    "numeric_to_qualitative", 
    "create_quantity",
    "validate_qualitative_state",
    
    # Type aliases
    "QValue",
    "QDirection",
    "QQuantity", 
    "QState",
    "QProcess",
    
    # Factory functions
    "create_educational_reasoner",
    "create_research_reasoner", 
    "create_production_reasoner",
    "create_demo_reasoner"
]