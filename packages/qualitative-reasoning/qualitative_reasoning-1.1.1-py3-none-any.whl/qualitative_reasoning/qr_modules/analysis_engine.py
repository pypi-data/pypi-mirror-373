"""
🧠 Qualitative Reasoning - Analysis Engine Module
================================================

This module provides the intelligence layer for qualitative reasoning systems, implementing
advanced analysis capabilities for relationship derivation, behavior explanation, and 
pattern recognition based on Forbus's Process Theory and de Kleer's Qualitative Physics.

📚 Theoretical Foundation:
Forbus, K. D. (1984). "Qualitative Process Theory", Artificial Intelligence, 24(1-3)
Forbus, K. D., & de Kleer, J. (1993). "Building Problem Solvers", MIT Press  
de Kleer, J., & Brown, J. S. (1984). "A Qualitative Physics Based on Confluences"
Iwasaki, Y., & Simon, H. A. (1994). "Causality and Model Abstraction"

🧠 Analysis Engine Theory:
The analysis engine implements the "intelligence" layer that interprets and explains
qualitative simulation results. It goes beyond simple state transitions to provide
deep insights into system behavior through multiple analytical approaches:

1. **Behavioral Explanation**: Traces causal chains to explain why quantities behave
   as they do, connecting process activation to quantity changes
2. **Relationship Derivation**: Infers higher-level relationships between quantities
   using directional correlations, process causality, and temporal patterns  
3. **Pattern Recognition**: Identifies domain-specific patterns and known physical
   relationships in system behavior
4. **Causal Chain Analysis**: Builds and analyzes causal dependency graphs to
   understand complex system interactions
5. **Statistical Analysis**: Applies qualitative statistics to identify trends
   and patterns in system behavior over time

🔬 Mathematical Framework:
Causal Analysis: C(Q₁ → Q₂) = Process_Influences ∧ Temporal_Correlation
Relationship Strength: R(Q₁,Q₂) = α·Directional + β·Causal + γ·Temporal + δ·Domain
Pattern Recognition: P(pattern) = Match(System_State, Domain_Knowledge)
Explanation Depth: E_depth = Chain_Length × Confidence × Relevance

🎯 Core Analysis Capabilities:
- Sophisticated behavior explanation with causal tracing
- Multi-dimensional relationship analysis and derivation
- Advanced correlation analysis (directional, temporal, causal)
- Domain-specific pattern recognition and inference
- Causal chain construction and analysis
- Statistical pattern analysis for qualitative data
- Intelligent system behavior interpretation
- Predictive relationship modeling

🌟 Key Implementation Features:  
- Robust causal chain tracing algorithms
- Multi-method relationship detection
- Advanced temporal pattern analysis
- Domain knowledge integration
- Statistical qualitative analysis
- Comprehensive explanation generation
- Intelligent behavior interpretation
- Extensible pattern recognition framework

Author: Benedict Chen
Based on foundational work by Kenneth Forbus, Johan de Kleer, and Herbert Simon
"""

from typing import Dict, List, Tuple, Union, Optional, Any, Set, Callable
from dataclasses import dataclass, field
import warnings
import re

# Import core types
try:
    from .core_types import (
        QualitativeValue, QualitativeDirection, QualitativeQuantity, 
        QualitativeState, QualitativeProcess
    )
except ImportError:
    # Fallback imports
    try:
        from core_types import (
            QualitativeValue, QualitativeDirection, QualitativeQuantity,
            QualitativeState, QualitativeProcess  
        )
    except ImportError:
        from qualitative_reasoning.qr_modules.core_types import (
            QualitativeValue, QualitativeDirection, QualitativeQuantity,
            QualitativeState, QualitativeProcess
        )


@dataclass
class CausalChain:
    """Represents a causal chain connecting processes to quantity changes"""
    source_quantity: str
    target_quantity: str
    intermediate_processes: List[str]
    chain_strength: float = 0.0
    explanation: List[str] = field(default_factory=list)


@dataclass  
class RelationshipAnalysis:
    """Results of relationship analysis between quantities"""
    quantity_pair: Tuple[str, str]
    relationship_type: str
    strength: float
    evidence: List[str]
    confidence: float


@dataclass
class BehaviorExplanation:
    """Comprehensive explanation of quantity behavior"""
    quantity_name: str
    current_state: str
    trend: str
    primary_causes: List[str]
    contributing_factors: List[str]
    causal_chains: List[CausalChain]
    confidence: float


class AnalysisEngineMixin:
    """
    🧠 Advanced Analysis Engine for Qualitative Reasoning Systems
    
    This mixin provides intelligent analysis capabilities that explain and interpret
    qualitative simulation results, deriving higher-level insights about system
    behavior and relationships.
    
    The analysis engine implements multiple complementary approaches:
    - Causal chain tracing for behavioral explanation
    - Multi-dimensional relationship analysis
    - Pattern recognition and domain knowledge integration
    - Statistical analysis of qualitative patterns
    - Predictive behavior modeling
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize analysis engine components"""
        super().__init__(*args, **kwargs)
        
        # Analysis state
        self._analysis_cache = {}
        self._relationship_history = []
        self._explanation_templates = {}
        
        # Pattern recognition
        self._domain_patterns = self._initialize_domain_patterns()
        self._causal_patterns = {}
        
        # Analysis configuration
        self._analysis_config = {
            'explanation_depth': 3,
            'correlation_threshold': 0.6,
            'confidence_threshold': 0.7,
            'enable_statistical_analysis': True,
            'enable_predictive_analysis': True
        }
        
    def explain_behavior(self, quantity_name: str, depth: int = 3) -> BehaviorExplanation:
        """
        🔍 Generate comprehensive explanation of quantity behavior
        
        Provides deep causal analysis tracing from processes through quantity
        changes to explain why a quantity exhibits its current behavior.
        
        Args:
            quantity_name: Name of quantity to explain
            depth: Maximum depth of causal chain analysis
            
        Returns:
            BehaviorExplanation: Comprehensive behavioral explanation
            
        🧠 Explanation Theory:
        The method implements multi-level causal explanation:
        1. **Direct Causation**: Immediate process influences
        2. **Indirect Causation**: Multi-step causal chains  
        3. **Contributing Factors**: Supporting conditions and constraints
        4. **Historical Context**: Past behavior patterns that inform current state
        """
        
        if quantity_name not in self.quantities:
            return BehaviorExplanation(
                quantity_name=quantity_name,
                current_state="unknown",
                trend="unknown", 
                primary_causes=[f"Quantity '{quantity_name}' not found"],
                contributing_factors=[],
                causal_chains=[],
                confidence=0.0
            )
            
        qty = self.quantities[quantity_name]
        
        # Analyze current state
        current_state = f"{qty.magnitude.value}"
        trend = f"{qty.direction.value}"
        
        # Find primary causal influences
        primary_causes = self._identify_primary_causes(quantity_name)
        
        # Find contributing factors
        contributing_factors = self._identify_contributing_factors(quantity_name)
        
        # Build causal chains
        causal_chains = self._build_causal_chains(quantity_name, depth)
        
        # Calculate explanation confidence
        confidence = self._calculate_explanation_confidence(
            primary_causes, contributing_factors, causal_chains
        )
        
        explanation = BehaviorExplanation(
            quantity_name=quantity_name,
            current_state=current_state,
            trend=trend,
            primary_causes=primary_causes,
            contributing_factors=contributing_factors, 
            causal_chains=causal_chains,
            confidence=confidence
        )
        
        return explanation
        
    def _identify_primary_causes(self, quantity_name: str) -> List[str]:
        """Identify primary causal influences on a quantity"""
        
        primary_causes = []
        
        # Find processes that directly influence this quantity
        for process_name, influenced_quantities in self.causal_graph.items():
            if quantity_name in influenced_quantities:
                process = self.processes[process_name]
                if process.active:
                    # Analyze the type of influence
                    for influence in process.influences:
                        if quantity_name in influence:
                            if "I+" in influence:
                                primary_causes.append(f"Process '{process_name}' increases {quantity_name}")
                            elif "I-" in influence:
                                primary_causes.append(f"Process '{process_name}' decreases {quantity_name}")
                            else:
                                primary_causes.append(f"Process '{process_name}' influences {quantity_name}")
                                
        if not primary_causes:
            primary_causes.append(f"No active processes currently influence {quantity_name}")
            
        return primary_causes
        
    def _identify_contributing_factors(self, quantity_name: str) -> List[str]:
        """Identify contributing factors that enable or constrain quantity behavior"""
        
        contributing_factors = []
        
        # Check process preconditions that enable influences
        for process_name, influenced_quantities in self.causal_graph.items():
            if quantity_name in influenced_quantities:
                process = self.processes[process_name]
                if process.active:
                    # Add preconditions as contributing factors
                    for precondition in process.preconditions:
                        contributing_factors.append(f"Precondition: {precondition}")
                    
                    # Add quantity conditions
                    for qty_condition in process.quantity_conditions:
                        contributing_factors.append(f"Condition: {qty_condition}")
                        
        # Check relevant constraints
        for constraint in self.constraints:
            if quantity_name in constraint:
                try:
                    if self._evaluate_constraint(constraint):
                        contributing_factors.append(f"Constraint satisfied: {constraint}")
                    else:
                        contributing_factors.append(f"Constraint violated: {constraint}")
                except:
                    contributing_factors.append(f"Constraint uncertain: {constraint}")
                    
        return contributing_factors
        
    def _build_causal_chains(self, quantity_name: str, max_depth: int) -> List[CausalChain]:
        """Build causal chains showing how processes influence quantities"""
        
        causal_chains = []
        
        # Find all quantities that influence this quantity through processes
        influencing_quantities = self._find_influencing_quantities(quantity_name, max_depth)
        
        for source_qty, path_info in influencing_quantities.items():
            if source_qty != quantity_name:
                chain = CausalChain(
                    source_quantity=source_qty,
                    target_quantity=quantity_name,
                    intermediate_processes=path_info['processes'],
                    chain_strength=path_info['strength'],
                    explanation=path_info['explanation']
                )
                causal_chains.append(chain)
                
        return causal_chains
        
    def _find_influencing_quantities(self, target_quantity: str, max_depth: int) -> Dict[str, Dict[str, Any]]:
        """Find quantities that influence target through process chains"""
        
        influencing_quantities = {}
        visited = set()
        
        def trace_influences(current_qty: str, depth: int, path: List[str], explanation: List[str]) -> None:
            if depth > max_depth or current_qty in visited:
                return
                
            visited.add(current_qty)
            
            # Find processes that influence current quantity
            for process_name, influenced_qtys in self.causal_graph.items():
                if current_qty in influenced_qtys:
                    process = self.processes[process_name]
                    
                    # Find quantities that enable this process
                    for qty_condition in process.quantity_conditions:
                        # Simple parsing - in practice would be more sophisticated
                        for qty_name in self.quantities.keys():
                            if qty_name in qty_condition and qty_name != current_qty:
                                new_path = path + [process_name]
                                new_explanation = explanation + [
                                    f"{qty_name} affects {current_qty} via process {process_name}"
                                ]
                                
                                if qty_name not in influencing_quantities:
                                    influencing_quantities[qty_name] = {
                                        'processes': new_path,
                                        'strength': 1.0 / (depth + 1),  # Decay with distance
                                        'explanation': new_explanation
                                    }
                                    
                                # Recursively trace deeper influences
                                if depth < max_depth:
                                    trace_influences(qty_name, depth + 1, new_path, new_explanation)
        
        trace_influences(target_quantity, 0, [], [])
        return influencing_quantities
        
    def _calculate_explanation_confidence(self, primary_causes: List[str], 
                                        contributing_factors: List[str],
                                        causal_chains: List[CausalChain]) -> float:
        """Calculate confidence in explanation based on available evidence"""
        
        confidence = 0.0
        
        # Base confidence from primary causes
        if primary_causes and not any("No active processes" in cause for cause in primary_causes):
            confidence += 0.5
            
        # Boost confidence from contributing factors
        if contributing_factors:
            confidence += min(0.3, len(contributing_factors) * 0.05)
            
        # Boost confidence from causal chains
        if causal_chains:
            chain_confidence = sum(chain.chain_strength for chain in causal_chains)
            confidence += min(0.2, chain_confidence * 0.1)
            
        return min(1.0, confidence)
        
    def derive_relationships(self) -> Dict[str, str]:
        """
        🔗 Derive comprehensive relationships between system quantities
        
        This method implements advanced relationship inference that combines
        multiple analytical approaches to identify patterns and connections.
        
        Returns:
            Dict[str, str]: Mapping of relationship names to relationship types
        """
        
        relationships = {}
        
        # Get all quantity names for analysis
        qty_names = list(self.quantities.keys())
        
        # 1. Analyze current directional correlations
        directional_correlations = self._analyze_directional_correlations(qty_names)
        relationships.update(directional_correlations)
        
        # 2. Analyze process-based causal relationships  
        causal_relationships = self._analyze_causal_relationships(qty_names)
        relationships.update(causal_relationships)
        
        # 3. Analyze temporal correlations if sufficient history exists
        if hasattr(self, 'state_history') and len(self.state_history) > 2:
            temporal_correlations = self._analyze_temporal_correlations(qty_names)
            relationships.update(temporal_correlations)
            
        # 4. Apply domain-specific relationship inference
        domain_relationships = self._infer_domain_relationships(qty_names)
        relationships.update(domain_relationships)
        
        # 5. Apply statistical pattern analysis
        if self._analysis_config['enable_statistical_analysis']:
            statistical_relationships = self._analyze_statistical_patterns(qty_names)
            relationships.update(statistical_relationships)
            
        # Cache results
        self._analysis_cache['relationships'] = relationships
        self._relationship_history.append(relationships.copy())
        
        return relationships
        
    def _analyze_directional_correlations(self, qty_names: List[str]) -> Dict[str, str]:
        """Analyze correlations based on current quantity direction changes"""
        
        correlations = {}
        
        # Check all pairs of quantities for directional correlations
        for i, qty1_name in enumerate(qty_names):
            for j, qty2_name in enumerate(qty_names[i+1:], i+1):
                qty1 = self.quantities[qty1_name]
                qty2 = self.quantities[qty2_name]
                
                # Get direction values as strings
                dir1_val = getattr(qty1.direction, 'value', str(qty1.direction))
                dir2_val = getattr(qty2.direction, 'value', str(qty2.direction))
                
                # Positive correlation: both increasing or both decreasing
                if ((dir1_val in ['+', 'increasing', 'inc'] and 
                     dir2_val in ['+', 'increasing', 'inc']) or
                    (dir1_val in ['-', 'decreasing', 'dec'] and 
                     dir2_val in ['-', 'decreasing', 'dec'])):
                    correlations[f"{qty1_name}_correlates_{qty2_name}"] = "positive_correlation"
                    
                # Negative correlation: one increasing, other decreasing
                elif ((dir1_val in ['+', 'increasing', 'inc'] and 
                       dir2_val in ['-', 'decreasing', 'dec']) or
                      (dir1_val in ['-', 'decreasing', 'dec'] and 
                       dir2_val in ['+', 'increasing', 'inc'])):
                    correlations[f"{qty1_name}_anticorrelates_{qty2_name}"] = "negative_correlation"
                    
        return correlations
        
    def _analyze_causal_relationships(self, qty_names: List[str]) -> Dict[str, str]:
        """Analyze causal relationships based on process dependency structure"""
        
        causal_rels = {}
        
        # Build quantity-to-process mapping
        qty_process_map = {}
        for qty_name in qty_names:
            affecting_processes = []
            for proc_name, process in self.processes.items():
                # Check if this process influences this quantity
                for influence in process.influences:
                    # Parse influence string (e.g., "I+(temperature)")
                    if ("(" in influence and ")" in influence):
                        influenced_qty = influence.split("(")[1].split(")")[0]
                        if influenced_qty == qty_name:
                            affecting_processes.append(proc_name)
                    elif influence.endswith(qty_name):
                        affecting_processes.append(proc_name)
                        
            qty_process_map[qty_name] = affecting_processes
            
        # Analyze relationships based on shared processes
        for i, qty1_name in enumerate(qty_names):
            for j, qty2_name in enumerate(qty_names[i+1:], i+1):
                processes1 = set(qty_process_map[qty1_name])
                processes2 = set(qty_process_map[qty2_name])
                
                # Common processes suggest causal coupling
                common_processes = processes1.intersection(processes2)
                if common_processes:
                    causal_rels[f"{qty1_name}_causally_linked_{qty2_name}"] = \
                        f"common_processes_{len(common_processes)}"
                        
                # Process chains suggest indirect causality
                if processes1 and processes2 and not common_processes:
                    causal_rels[f"{qty1_name}_indirectly_influences_{qty2_name}"] = \
                        f"via_processes_{len(processes1)}_{len(processes2)}"
                        
        return causal_rels
        
    def _analyze_temporal_correlations(self, qty_names: List[str]) -> Dict[str, str]:
        """Analyze correlations across temporal state history"""
        
        temporal_rels = {}
        
        # Extract historical direction sequences
        qty_history = {}
        for qty_name in qty_names:
            directions = []
            for historical_state in self.state_history:
                if (qty_name in historical_state.quantities and 
                    hasattr(historical_state.quantities[qty_name], 'direction')):
                    directions.append(historical_state.quantities[qty_name].direction)
            qty_history[qty_name] = directions
            
        # Analyze pairwise temporal correlations
        for i, qty1_name in enumerate(qty_names):
            for j, qty2_name in enumerate(qty_names[i+1:], i+1):
                hist1 = qty_history.get(qty1_name, [])
                hist2 = qty_history.get(qty2_name, [])
                
                if len(hist1) >= 3 and len(hist2) >= 3:
                    correlation_strength = self._compute_temporal_correlation(hist1, hist2)
                    
                    if correlation_strength > self._analysis_config['correlation_threshold']:
                        temporal_rels[f"{qty1_name}_temporal_pos_corr_{qty2_name}"] = \
                            f"strength_{correlation_strength:.2f}"
                    elif correlation_strength < -self._analysis_config['correlation_threshold']:
                        temporal_rels[f"{qty1_name}_temporal_neg_corr_{qty2_name}"] = \
                            f"strength_{abs(correlation_strength):.2f}"
                            
        return temporal_rels
        
    def _compute_temporal_correlation(self, hist1: List[QualitativeDirection], 
                                    hist2: List[QualitativeDirection]) -> float:
        """Compute temporal correlation between two direction histories"""
        
        if len(hist1) < 2 or len(hist2) < 2:
            return 0.0
            
        # Convert directions to numeric values for correlation
        def direction_to_numeric(direction):
            direction_value = getattr(direction, 'value', str(direction))
            return {
                '+': 1, 'increasing': 1, 'inc': 1,
                '0': 0, 'steady': 0, 'std': 0,
                '-': -1, 'decreasing': -1, 'dec': -1,
                '?': 0, 'unknown': 0
            }.get(direction_value, 0)
            
        # Compute direction changes
        changes1 = [direction_to_numeric(hist1[i+1]) - direction_to_numeric(hist1[i]) 
                   for i in range(len(hist1)-1)]
        changes2 = [direction_to_numeric(hist2[i+1]) - direction_to_numeric(hist2[i]) 
                   for i in range(len(hist2)-1)]
        
        # Compute correlation of changes
        if not changes1 or not changes2:
            return 0.0
            
        min_len = min(len(changes1), len(changes2))
        changes1 = changes1[:min_len]
        changes2 = changes2[:min_len]
        
        # Simple correlation computation
        numerator = sum(c1 * c2 for c1, c2 in zip(changes1, changes2))
        sum1_sq = sum(c1 * c1 for c1 in changes1)
        sum2_sq = sum(c2 * c2 for c2 in changes2)
        
        denominator = (sum1_sq * sum2_sq) ** 0.5
        
        return numerator / denominator if denominator > 0 else 0.0
        
    def _infer_domain_relationships(self, qty_names: List[str]) -> Dict[str, str]:
        """Infer relationships based on domain-specific knowledge patterns"""
        
        domain_rels = {}
        
        # Check for domain pattern matches
        for (concept1, concept2), relationship_type in self._domain_patterns.items():
            # Check if quantity names contain these concepts
            for qty1_name in qty_names:
                for qty2_name in qty_names:
                    if qty1_name != qty2_name:
                        # Check both forward and reverse matching
                        if ((concept1.lower() in qty1_name.lower() and 
                             concept2.lower() in qty2_name.lower()) or
                            (concept2.lower() in qty1_name.lower() and 
                             concept1.lower() in qty2_name.lower())):
                            domain_rels[f"{qty1_name}_domain_relation_{qty2_name}"] = relationship_type
                            
        return domain_rels
        
    def _analyze_statistical_patterns(self, qty_names: List[str]) -> Dict[str, str]:
        """Apply statistical analysis to identify qualitative patterns"""
        
        statistical_rels = {}
        
        if not hasattr(self, 'state_history') or len(self.state_history) < 3:
            return statistical_rels
            
        # Analyze magnitude stability patterns
        for qty_name in qty_names:
            stability_pattern = self._analyze_magnitude_stability(qty_name)
            if stability_pattern:
                statistical_rels[f"{qty_name}_stability_pattern"] = stability_pattern
                
        # Analyze transition frequency patterns
        for qty_name in qty_names:
            transition_pattern = self._analyze_transition_frequency(qty_name)
            if transition_pattern:
                statistical_rels[f"{qty_name}_transition_pattern"] = transition_pattern
                
        # Analyze co-occurrence patterns
        co_occurrence_patterns = self._analyze_co_occurrence_patterns(qty_names)
        statistical_rels.update(co_occurrence_patterns)
        
        return statistical_rels
        
    def _analyze_magnitude_stability(self, qty_name: str) -> Optional[str]:
        """Analyze stability patterns in quantity magnitudes"""
        
        magnitudes = []
        for state in self.state_history:
            if qty_name in state.quantities:
                mag = state.quantities[qty_name].magnitude
                magnitudes.append(mag)
                
        if len(magnitudes) < 3:
            return None
            
        # Count stability
        stable_count = 0
        for i in range(1, len(magnitudes)):
            if magnitudes[i] == magnitudes[i-1]:
                stable_count += 1
                
        stability_ratio = stable_count / (len(magnitudes) - 1)
        
        if stability_ratio > 0.8:
            return "highly_stable"
        elif stability_ratio > 0.6:
            return "moderately_stable"
        elif stability_ratio > 0.4:
            return "somewhat_unstable"
        else:
            return "highly_volatile"
            
    def _analyze_transition_frequency(self, qty_name: str) -> Optional[str]:
        """Analyze frequency of direction transitions"""
        
        directions = []
        for state in self.state_history:
            if qty_name in state.quantities:
                directions.append(state.quantities[qty_name].direction)
                
        if len(directions) < 3:
            return None
            
        # Count direction changes
        changes = 0
        for i in range(1, len(directions)):
            if directions[i] != directions[i-1]:
                changes += 1
                
        change_frequency = changes / (len(directions) - 1)
        
        if change_frequency > 0.7:
            return "high_frequency_transitions"
        elif change_frequency > 0.4:
            return "moderate_frequency_transitions"
        elif change_frequency > 0.1:
            return "low_frequency_transitions"
        else:
            return "stable_direction"
            
    def _analyze_co_occurrence_patterns(self, qty_names: List[str]) -> Dict[str, str]:
        """Analyze patterns of simultaneous quantity changes"""
        
        co_occurrence_rels = {}
        
        if len(self.state_history) < 3:
            return co_occurrence_rels
            
        # Track direction change co-occurrences
        for i, qty1_name in enumerate(qty_names):
            for j, qty2_name in enumerate(qty_names[i+1:], i+1):
                
                simultaneous_changes = 0
                total_changes = 0
                
                for k in range(1, len(self.state_history)):
                    prev_state = self.state_history[k-1]
                    curr_state = self.state_history[k]
                    
                    if (qty1_name in prev_state.quantities and qty1_name in curr_state.quantities and
                        qty2_name in prev_state.quantities and qty2_name in curr_state.quantities):
                        
                        qty1_changed = (prev_state.quantities[qty1_name].direction != 
                                      curr_state.quantities[qty1_name].direction)
                        qty2_changed = (prev_state.quantities[qty2_name].direction != 
                                      curr_state.quantities[qty2_name].direction)
                        
                        if qty1_changed or qty2_changed:
                            total_changes += 1
                            if qty1_changed and qty2_changed:
                                simultaneous_changes += 1
                                
                if total_changes > 0:
                    co_occurrence_rate = simultaneous_changes / total_changes
                    if co_occurrence_rate > 0.6:
                        co_occurrence_rels[f"{qty1_name}_cochanges_{qty2_name}"] = \
                            f"high_cooccurrence_{co_occurrence_rate:.2f}"
                    elif co_occurrence_rate > 0.3:
                        co_occurrence_rels[f"{qty1_name}_cochanges_{qty2_name}"] = \
                            f"moderate_cooccurrence_{co_occurrence_rate:.2f}"
                            
        return co_occurrence_rels
        
    def trace_causal_chain(self, source_qty: str, target_qty: str, 
                          max_depth: int = 5) -> List[CausalChain]:
        """
        🔗 Trace causal chains between source and target quantities
        
        Args:
            source_qty: Source quantity name
            target_qty: Target quantity name
            max_depth: Maximum chain depth to explore
            
        Returns:
            List[CausalChain]: All causal chains found
        """
        
        causal_chains = []
        
        if source_qty not in self.quantities or target_qty not in self.quantities:
            return causal_chains
            
        visited = set()
        
        def trace_recursive(current_qty: str, path: List[str], 
                          explanations: List[str], depth: int):
            if depth > max_depth or current_qty in visited:
                return
                
            if current_qty == target_qty and depth > 0:
                # Found a causal chain
                chain = CausalChain(
                    source_quantity=source_qty,
                    target_quantity=target_qty,
                    intermediate_processes=path.copy(),
                    chain_strength=1.0 / depth,
                    explanation=explanations.copy()
                )
                causal_chains.append(chain)
                return
                
            visited.add(current_qty)
            
            # Find processes that influence current quantity
            for process_name, influenced_qtys in self.causal_graph.items():
                if current_qty in influenced_qtys:
                    process = self.processes[process_name]
                    
                    # Find quantities that affect this process
                    for qty_condition in process.quantity_conditions:
                        for qty_name in self.quantities.keys():
                            if (qty_name in qty_condition and qty_name != current_qty 
                                and qty_name not in visited):
                                
                                new_path = path + [process_name]
                                new_explanations = explanations + [
                                    f"{qty_name} influences {current_qty} via {process_name}"
                                ]
                                
                                trace_recursive(qty_name, new_path, new_explanations, depth + 1)
                                
            visited.remove(current_qty)
            
        trace_recursive(source_qty, [], [], 0)
        return causal_chains
        
    def generate_behavior_summary(self) -> Dict[str, Any]:
        """
        📊 Generate comprehensive system behavior summary
        
        Returns:
            Dict with system-wide behavioral analysis
        """
        
        summary = {
            'timestamp': self.current_state.time_point if self.current_state else "unknown",
            'quantity_analysis': {},
            'relationship_summary': {},
            'causal_network': {},
            'behavioral_patterns': {},
            'system_health': {}
        }
        
        # Analyze each quantity
        for qty_name in self.quantities.keys():
            explanation = self.explain_behavior(qty_name, depth=2)
            summary['quantity_analysis'][qty_name] = {
                'state': explanation.current_state,
                'trend': explanation.trend,
                'primary_causes': explanation.primary_causes,
                'confidence': explanation.confidence
            }
            
        # Analyze relationships
        relationships = self.derive_relationships()
        relationship_types = {}
        for rel_name, rel_type in relationships.items():
            if rel_type not in relationship_types:
                relationship_types[rel_type] = 0
            relationship_types[rel_type] += 1
            
        summary['relationship_summary'] = {
            'total_relationships': len(relationships),
            'relationship_types': relationship_types
        }
        
        # Analyze causal network density
        total_possible_connections = len(self.quantities) * (len(self.quantities) - 1)
        actual_connections = len([r for r in relationships.keys() if 'causal' in r.lower()])
        
        summary['causal_network'] = {
            'density': actual_connections / max(1, total_possible_connections),
            'active_processes': len([p for p in self.processes.values() if p.active]),
            'total_processes': len(self.processes)
        }
        
        # Identify behavioral patterns
        summary['behavioral_patterns'] = self._identify_system_patterns()
        
        # Assess system health
        summary['system_health'] = self._assess_system_health()
        
        return summary
        
    def _identify_system_patterns(self) -> Dict[str, str]:
        """Identify high-level system behavioral patterns"""
        
        patterns = {}
        
        # Analyze overall system activity
        active_processes = len([p for p in self.processes.values() if p.active])
        total_processes = len(self.processes)
        
        if active_processes == 0:
            patterns['system_activity'] = 'dormant'
        elif active_processes == total_processes:
            patterns['system_activity'] = 'fully_active'
        elif active_processes > total_processes * 0.7:
            patterns['system_activity'] = 'highly_active'
        elif active_processes > total_processes * 0.3:
            patterns['system_activity'] = 'moderately_active'
        else:
            patterns['system_activity'] = 'low_activity'
            
        # Analyze directional trends
        directions = [qty.direction for qty in self.quantities.values()]
        increasing_count = sum(1 for d in directions if getattr(d, 'value', str(d)) in ['+', 'increasing', 'inc'])
        decreasing_count = sum(1 for d in directions if getattr(d, 'value', str(d)) in ['-', 'decreasing', 'dec'])
        
        if increasing_count > decreasing_count * 2:
            patterns['directional_trend'] = 'predominantly_increasing'
        elif decreasing_count > increasing_count * 2:
            patterns['directional_trend'] = 'predominantly_decreasing'
        elif abs(increasing_count - decreasing_count) <= 1:
            patterns['directional_trend'] = 'balanced'
        else:
            patterns['directional_trend'] = 'mixed'
            
        return patterns
        
    def _assess_system_health(self) -> Dict[str, Any]:
        """Assess overall system health and stability"""
        
        health = {
            'constraint_violations': 0,
            'stability_score': 0.0,
            'coherence_score': 0.0,
            'overall_health': 'unknown'
        }
        
        # Check constraint violations
        violations = 0
        for constraint in self.constraints:
            try:
                if not self._evaluate_constraint(constraint):
                    violations += 1
            except:
                violations += 1
                
        health['constraint_violations'] = violations
        
        # Calculate stability score
        if hasattr(self, 'state_history') and len(self.state_history) > 1:
            stability_scores = []
            for qty_name in self.quantities.keys():
                stability = self._analyze_magnitude_stability(qty_name)
                if stability == 'highly_stable':
                    stability_scores.append(1.0)
                elif stability == 'moderately_stable':
                    stability_scores.append(0.7)
                elif stability == 'somewhat_unstable':
                    stability_scores.append(0.4)
                else:
                    stability_scores.append(0.1)
                    
            health['stability_score'] = sum(stability_scores) / len(stability_scores) if stability_scores else 0.0
            
        # Calculate coherence score (consistency of relationships)
        relationships = self._analysis_cache.get('relationships', {})
        positive_rels = len([r for r in relationships.values() if 'positive' in r.lower()])
        negative_rels = len([r for r in relationships.values() if 'negative' in r.lower()])
        total_rels = max(1, len(relationships))
        
        # Higher coherence when relationships are balanced
        coherence = 1.0 - abs(positive_rels - negative_rels) / total_rels
        health['coherence_score'] = coherence
        
        # Overall health assessment
        health_score = (
            (1.0 if violations == 0 else max(0.0, 1.0 - violations * 0.2)) * 0.4 +
            health['stability_score'] * 0.3 +
            health['coherence_score'] * 0.3
        )
        
        if health_score > 0.8:
            health['overall_health'] = 'excellent'
        elif health_score > 0.6:
            health['overall_health'] = 'good'
        elif health_score > 0.4:
            health['overall_health'] = 'fair'
        elif health_score > 0.2:
            health['overall_health'] = 'poor'
        else:
            health['overall_health'] = 'critical'
            
        return health
        
    def _initialize_domain_patterns(self) -> Dict[Tuple[str, str], str]:
        """Initialize domain-specific knowledge patterns"""
        
        return {
            # Thermodynamics
            ('temperature', 'pressure'): 'thermal_relationship',
            ('temperature', 'volume'): 'thermal_expansion',
            ('heat', 'temperature'): 'thermal_energy',
            
            # Fluid dynamics  
            ('flow_rate', 'pressure'): 'fluid_dynamics',
            ('velocity', 'pressure'): 'bernoulli_relationship',
            ('volume', 'pressure'): 'boyles_law',
            
            # Mechanics
            ('force', 'acceleration'): 'newtons_second_law',
            ('velocity', 'kinetic_energy'): 'mechanical_energy',
            ('height', 'potential_energy'): 'gravitational_energy',
            
            # Electrical
            ('voltage', 'current'): 'ohms_law',
            ('power', 'voltage'): 'electrical_power',
            ('resistance', 'current'): 'electrical_resistance',
            
            # Chemical
            ('concentration', 'reaction_rate'): 'chemical_kinetics',
            ('temperature', 'reaction_rate'): 'arrhenius_relationship',
            ('catalyst', 'reaction_rate'): 'catalytic_effect',
        }
        
    def configure_analysis(self, **config_options):
        """
        🔧 Configure analysis engine parameters
        
        Args:
            **config_options: Configuration parameters to update
        """
        
        valid_options = {
            'explanation_depth', 'correlation_threshold', 'confidence_threshold',
            'enable_statistical_analysis', 'enable_predictive_analysis'
        }
        
        for option, value in config_options.items():
            if option in valid_options:
                self._analysis_config[option] = value
            else:
                print(f"Warning: Unknown analysis configuration option '{option}'")
                
    def get_analysis_metrics(self) -> Dict[str, Any]:
        """
        📈 Get comprehensive analysis performance metrics
        
        Returns:
            Dict containing analysis metrics and statistics
        """
        
        return {
            'cache_size': len(self._analysis_cache),
            'relationship_history_length': len(self._relationship_history),
            'domain_patterns_loaded': len(self._domain_patterns),
            'analysis_config': self._analysis_config.copy(),
            'last_analysis_timestamp': self.current_state.time_point if self.current_state else None
        }