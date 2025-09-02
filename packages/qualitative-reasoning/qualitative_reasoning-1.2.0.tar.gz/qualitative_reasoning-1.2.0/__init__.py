"""
Qualitative Reasoning Library
Based on: Forbus & de Kleer (1993) "Building Problem Solvers" and de Kleer & Brown (1984)

This library implements reasoning about physical systems without precise numerical values,
enabling AI to understand causality and physics through qualitative relationships.
"""

def _print_attribution():
    """Print attribution message with donation link"""
    try:
        print("\n🤔 Qualitative Reasoning Library - Made possible by Benedict Chen")
        print("   \033]8;;mailto:benedict@benedictchen.com\033\\benedict@benedictchen.com\033]8;;\033\\")
        print("   Support his work: \033]8;;https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS\033\\🍺 Buy him a beer\033]8;;\033\\")
    except:
        print("\n🤔 Qualitative Reasoning Library - Made possible by Benedict Chen")
        print("   benedict@benedictchen.com")
        print("   Support: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS")

from .qualitative_reasoning import (
    QualitativeReasoner, 
    QualitativeValue, 
    QualitativeDirection,
    QualitativeQuantity,
    QualitativeState,
    QualitativeProcess
)
from .envisionment import QualitativeEnvisionment
from .causal_reasoning import CausalReasoner
from .physics_engine import QualitativePhysicsEngine

# Show attribution on library import
_print_attribution()

__version__ = "1.0.0"
__authors__ = ["Based on Forbus & de Kleer (1993), de Kleer & Brown (1984)"]

__all__ = [
    "QualitativeReasoner",
    "QualitativeValue", 
    "QualitativeDirection",
    "QualitativeQuantity",
    "QualitativeState",
    "QualitativeProcess",
    "QualitativeEnvisionment",
    "CausalReasoner",
    "QualitativePhysicsEngine"
]