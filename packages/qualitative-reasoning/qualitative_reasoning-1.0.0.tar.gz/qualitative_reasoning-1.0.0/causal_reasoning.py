"""
Causal Reasoning Implementation
Based on: de Kleer & Brown (1984) and Forbus (1984) causal ordering principles

Implements causal reasoning about physical processes and their effects,
enabling explanation and prediction of system behavior.
"""

import numpy as np
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass
from .qualitative_reasoning import QualitativeQuantity, QualitativeProcess


@dataclass
class CausalLink:
    """Represents a causal relationship between two quantities or processes"""
    cause: str
    effect: str
    polarity: str  # 'positive', 'negative', 'unknown'
    strength: float  # 0.0 to 1.0
    delay: float  # Time delay (qualitative or quantitative)
    conditions: List[str]  # Conditions under which link is active


@dataclass
class CausalChain:
    """Represents a chain of causal links"""
    links: List[CausalLink]
    start: str
    end: str
    strength: float
    plausibility: float


class CausalReasoner:
    """
    Causal Reasoning Engine
    
    Performs causal analysis of physical systems to understand
    cause-and-effect relationships and generate explanations.
    """
    
    def __init__(self, domain_knowledge: Optional[Dict[str, Any]] = None):
        """
        Initialize causal reasoner
        
        Args:
            domain_knowledge: Domain-specific causal knowledge
        """
        
        self.causal_links: List[CausalLink] = []
        self.quantities: Dict[str, QualitativeQuantity] = {}
        self.processes: Dict[str, QualitativeProcess] = {}
        
        # Domain knowledge
        self.domain_knowledge = domain_knowledge or {}
        
        # Reasoning parameters
        self.min_strength_threshold = 0.1
        self.max_chain_length = 5
        
        # Initialize with basic physical causal knowledge
        self._initialize_basic_causal_knowledge()
        
        print(f"✓ Causal Reasoner initialized:")
        print(f"   Basic causal links: {len(self.causal_links)}")
        
    def _initialize_basic_causal_knowledge(self):
        """Initialize basic physical causal relationships"""
        
        # Basic thermodynamics
        self.add_causal_link(
            'temperature_difference', 'heat_flow', 
            polarity='positive', strength=0.9
        )
        
        # Basic mechanics  
        self.add_causal_link(
            'force', 'acceleration',
            polarity='positive', strength=0.95
        )
        
        self.add_causal_link(
            'pressure_difference', 'fluid_flow',
            polarity='positive', strength=0.85
        )
        
        # Conservation principles
        self.add_causal_link(
            'mass_in', 'mass_total',
            polarity='positive', strength=1.0
        )
        
        self.add_causal_link(
            'energy_input', 'total_energy',
            polarity='positive', strength=1.0
        )
        
    def add_causal_link(self, cause: str, effect: str, 
                       polarity: str = 'positive', strength: float = 0.5,
                       delay: float = 0.0, conditions: List[str] = None):
        """Add a causal link to the knowledge base"""
        
        link = CausalLink(
            cause=cause,
            effect=effect,
            polarity=polarity,
            strength=strength,
            delay=delay,
            conditions=conditions or []
        )
        
        self.causal_links.append(link)
        
    def find_causal_chains(self, cause: str, effect: str, 
                          current_state: Dict[str, Any] = None) -> List[CausalChain]:
        """
        Find causal chains connecting cause to effect
        
        Args:
            cause: Starting quantity or process
            effect: Target quantity or process  
            current_state: Current system state for condition evaluation
            
        Returns:
            List of causal chains
        """
        
        chains = []
        visited = set()
        
        def search_chains(current: str, target: str, path: List[CausalLink], 
                         current_strength: float, depth: int):
            
            if depth > self.max_chain_length or current in visited:
                return
                
            if current == target and len(path) > 0:
                # Found complete chain
                chain = CausalChain(
                    links=path.copy(),
                    start=cause,
                    end=effect,
                    strength=current_strength,
                    plausibility=self._calculate_chain_plausibility(path, current_state)
                )
                chains.append(chain)
                return
                
            visited.add(current)
            
            # Find links from current node
            for link in self.causal_links:
                if link.cause == current and self._link_applicable(link, current_state):
                    new_strength = current_strength * link.strength
                    
                    if new_strength >= self.min_strength_threshold:
                        path.append(link)
                        search_chains(link.effect, target, path, new_strength, depth + 1)
                        path.pop()
                        
            visited.remove(current)
            
        search_chains(cause, effect, [], 1.0, 0)
        
        # Sort by strength and plausibility
        chains.sort(key=lambda c: (c.strength * c.plausibility), reverse=True)
        
        return chains
        
    def _link_applicable(self, link: CausalLink, current_state: Dict[str, Any]) -> bool:
        """Check if causal link is applicable in current state"""
        
        if not current_state:
            return True
            
        # Check conditions
        for condition in link.conditions:
            if not self._evaluate_condition(condition, current_state):
                return False
                
        return True
        
    def _evaluate_condition(self, condition: str, current_state: Dict[str, Any]) -> bool:
        """Evaluate a condition against current state"""
        
        # Simple condition evaluation
        # In full implementation, would parse logical expressions
        
        if condition in current_state:
            return bool(current_state[condition])
            
        # Check for inequality conditions
        if '>' in condition:
            parts = condition.split('>')
            if len(parts) == 2:
                left, right = parts[0].strip(), parts[1].strip()
                left_val = current_state.get(left, 0)
                right_val = current_state.get(right, 0) if right in current_state else float(right)
                return left_val > right_val
                
        return True  # Default to true for unknown conditions
        
    def _calculate_chain_plausibility(self, path: List[CausalLink], 
                                    current_state: Dict[str, Any]) -> float:
        """Calculate plausibility of a causal chain"""
        
        if not path:
            return 0.0
            
        # Base plausibility on chain length (shorter is more plausible)
        length_factor = 1.0 / (1.0 + 0.2 * len(path))
        
        # Consider link polarities (consistent polarities more plausible)
        polarity_factor = self._calculate_polarity_consistency(path)
        
        # Consider domain knowledge
        domain_factor = self._apply_domain_knowledge(path)
        
        return length_factor * polarity_factor * domain_factor
        
    def _calculate_polarity_consistency(self, path: List[CausalLink]) -> float:
        """Calculate consistency of polarities in chain"""
        
        if len(path) <= 1:
            return 1.0
            
        # Count polarity changes
        changes = 0
        for i in range(1, len(path)):
            if path[i].polarity != path[i-1].polarity:
                changes += 1
                
        # Fewer changes = higher consistency
        return 1.0 / (1.0 + 0.3 * changes)
        
    def _apply_domain_knowledge(self, path: List[CausalLink]) -> float:
        """Apply domain-specific knowledge to evaluate chain"""
        
        # Check for known patterns
        patterns = self.domain_knowledge.get('causal_patterns', [])
        
        for pattern in patterns:
            if self._matches_pattern(path, pattern):
                return pattern.get('plausibility_factor', 1.0)
                
        return 1.0  # Default factor
        
    def _matches_pattern(self, path: List[CausalLink], pattern: Dict) -> bool:
        """Check if causal chain matches a known pattern"""
        
        pattern_links = pattern.get('links', [])
        
        if len(path) != len(pattern_links):
            return False
            
        for i, link in enumerate(path):
            pattern_link = pattern_links[i]
            
            if (pattern_link.get('cause') != link.cause or 
                pattern_link.get('effect') != link.effect):
                return False
                
        return True
        
    def explain_change(self, quantity: str, change: str,
                      system_state: Dict[str, Any]) -> List[str]:
        """
        Explain why a quantity changed in a given direction
        
        Args:
            quantity: Name of quantity that changed
            change: Direction of change ('increase', 'decrease')
            system_state: Current system state
            
        Returns:
            List of explanations
        """
        
        explanations = []
        
        # Find potential causes
        potential_causes = self._find_potential_causes(quantity, change, system_state)
        
        for cause in potential_causes:
            chains = self.find_causal_chains(cause, quantity, system_state)
            
            for chain in chains[:3]:  # Top 3 chains
                explanation = self._generate_explanation(chain, change)
                explanations.append(explanation)
                
        return explanations
        
    def _find_potential_causes(self, quantity: str, change: str,
                              system_state: Dict[str, Any]) -> List[str]:
        """Find quantities that could cause the observed change"""
        
        causes = []
        
        for link in self.causal_links:
            if link.effect == quantity:
                # Check if polarity matches change direction
                if ((change == 'increase' and link.polarity == 'positive') or
                    (change == 'decrease' and link.polarity == 'negative') or
                    (change == 'increase' and link.polarity == 'negative') or  # Negative cause can increase effect
                    (change == 'decrease' and link.polarity == 'positive')):
                    
                    if self._link_applicable(link, system_state):
                        causes.append(link.cause)
                        
        return causes
        
    def _generate_explanation(self, chain: CausalChain, change: str) -> str:
        """Generate natural language explanation for causal chain"""
        
        if not chain.links:
            return f"{chain.end} {change}d for unknown reasons"
            
        # Build explanation from chain
        explanation = f"{chain.end} {change}d because "
        
        for i, link in enumerate(chain.links):
            if i == 0:
                explanation += f"{link.cause} "
            
            if link.polarity == 'positive':
                explanation += f"caused {link.effect} to {change}"
            elif link.polarity == 'negative':
                opposite_change = 'decrease' if change == 'increase' else 'increase'
                explanation += f"caused {link.effect} to {opposite_change}"
                
            if i < len(chain.links) - 1:
                explanation += ", which in turn "
                
        explanation += f" (strength: {chain.strength:.2f}, plausibility: {chain.plausibility:.2f})"
        
        return explanation
        
    def predict_effects(self, cause: str, change: str,
                       system_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Predict effects of a change in a given quantity
        
        Args:
            cause: Quantity that changed
            change: Direction of change
            system_state: Current system state
            
        Returns:
            List of predicted effects
        """
        
        predictions = []
        
        # Find direct effects
        for link in self.causal_links:
            if link.cause == cause and self._link_applicable(link, system_state):
                
                # Determine effect direction
                if link.polarity == 'positive':
                    effect_change = change
                elif link.polarity == 'negative':
                    effect_change = 'decrease' if change == 'increase' else 'increase'
                else:
                    effect_change = 'unknown'
                    
                prediction = {
                    'effect': link.effect,
                    'change': effect_change,
                    'confidence': link.strength,
                    'delay': link.delay,
                    'explanation': f"{cause} {change} causes {link.effect} to {effect_change}"
                }
                
                predictions.append(prediction)
                
        # Sort by confidence
        predictions.sort(key=lambda p: p['confidence'], reverse=True)
        
        return predictions
        
    def analyze_feedback_loops(self, system_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify feedback loops in the causal network"""
        
        loops = []
        
        # Find all quantities
        quantities = set()
        for link in self.causal_links:
            quantities.add(link.cause)
            quantities.add(link.effect)
            
        # For each quantity, try to find path back to itself
        for quantity in quantities:
            chains = self.find_causal_chains(quantity, quantity, system_state)
            
            for chain in chains:
                if len(chain.links) > 1:  # Must be actual loop, not self-loop
                    loop_type = self._classify_feedback_loop(chain)
                    
                    loop_info = {
                        'quantity': quantity,
                        'chain': chain,
                        'type': loop_type,
                        'strength': chain.strength,
                        'stability': self._analyze_loop_stability(chain)
                    }
                    
                    loops.append(loop_info)
                    
        return loops
        
    def _classify_feedback_loop(self, chain: CausalChain) -> str:
        """Classify feedback loop as positive or negative"""
        
        negative_links = sum(1 for link in chain.links if link.polarity == 'negative')
        
        if negative_links % 2 == 0:
            return 'positive'  # Even number of negative links = positive feedback
        else:
            return 'negative'  # Odd number of negative links = negative feedback
            
    def _analyze_loop_stability(self, chain: CausalChain) -> str:
        """Analyze stability implications of feedback loop"""
        
        loop_type = self._classify_feedback_loop(chain)
        
        if loop_type == 'positive':
            return 'potentially_unstable'  # Positive feedback can cause instability
        else:
            return 'stabilizing'  # Negative feedback typically stabilizes
            
    def get_causal_graph(self) -> Dict[str, Any]:
        """Get causal network as graph structure"""
        
        nodes = set()
        edges = []
        
        for link in self.causal_links:
            nodes.add(link.cause)
            nodes.add(link.effect)
            
            edges.append({
                'source': link.cause,
                'target': link.effect,
                'polarity': link.polarity,
                'strength': link.strength,
                'delay': link.delay
            })
            
        return {
            'nodes': list(nodes),
            'edges': edges,
            'statistics': {
                'total_nodes': len(nodes),
                'total_edges': len(edges),
                'positive_links': len([e for e in edges if e['polarity'] == 'positive']),
                'negative_links': len([e for e in edges if e['polarity'] == 'negative'])
            }
        }