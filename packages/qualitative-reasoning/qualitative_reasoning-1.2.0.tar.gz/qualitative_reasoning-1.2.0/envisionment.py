"""
Qualitative Envisionment Implementation
Based on: de Kleer & Brown (1984) "A Qualitative Physics Based on Confluences"

Implements envisionment - the process of generating all possible qualitative
states and transitions of a physical system.
"""

import numpy as np
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass
from .qualitative_reasoning import QualitativeState, QualitativeProcess, QualitativeQuantity


@dataclass
class EnvisionmentNode:
    """A node in the envisionment graph representing a qualitative state"""
    state: QualitativeState
    id: int
    transitions: List[int]  # IDs of reachable states
    processes: List[QualitativeProcess]
    stability: str  # 'stable', 'unstable', 'unknown'


class QualitativeEnvisionment:
    """
    Qualitative Envisionment Generator
    
    Creates a graph of all possible qualitative states and transitions
    for a given physical system, enabling prediction and explanation.
    """
    
    def __init__(self, system_description: Dict[str, Any]):
        """
        Initialize envisionment for a physical system
        
        Args:
            system_description: Dictionary describing the system components,
                               quantities, and processes
        """
        
        self.system = system_description
        self.nodes: Dict[int, EnvisionmentNode] = {}
        self.next_node_id = 0
        self.initial_states: List[int] = []
        self.goal_states: List[int] = []
        
        # Quantities and their landmarks
        self.quantities = system_description.get('quantities', {})
        self.processes = system_description.get('processes', [])
        self.constraints = system_description.get('constraints', [])
        
        print(f"✓ Qualitative Envisionment initialized:")
        print(f"   Quantities: {len(self.quantities)}")
        print(f"   Processes: {len(self.processes)}")
        print(f"   Constraints: {len(self.constraints)}")
        
    def generate_envisionment(self, verbose: bool = True) -> Dict[str, Any]:
        """
        Generate the complete envisionment
        
        Returns:
            Envisionment statistics and structure
        """
        
        if verbose:
            print("🔄 Generating qualitative envisionment...")
            
        # Step 1: Generate initial state space
        initial_states = self._generate_initial_states()
        
        if verbose:
            print(f"   Generated {len(initial_states)} initial states")
            
        # Step 2: For each state, determine active processes
        for state in initial_states:
            node_id = self._add_state_node(state)
            self.initial_states.append(node_id)
            
        # Step 3: Generate transitions by process activation/deactivation
        self._generate_transitions(verbose)
        
        # Step 4: Analyze stability
        self._analyze_stability()
        
        results = {
            'total_states': len(self.nodes),
            'initial_states': len(self.initial_states),
            'transitions': sum(len(node.transitions) for node in self.nodes.values()),
            'stable_states': sum(1 for node in self.nodes.values() if node.stability == 'stable'),
            'unstable_states': sum(1 for node in self.nodes.values() if node.stability == 'unstable')
        }
        
        if verbose:
            print(f"✅ Envisionment complete:")
            print(f"   Total states: {results['total_states']}")
            print(f"   Transitions: {results['transitions']}")
            print(f"   Stable states: {results['stable_states']}")
            
        return results
        
    def _generate_initial_states(self) -> List[QualitativeState]:
        """Generate all consistent qualitative states"""
        
        states = []
        
        # Generate all combinations of qualitative values for each quantity
        quantity_combinations = self._generate_quantity_combinations()
        
        for combination in quantity_combinations:
            state = QualitativeState(
                quantities=combination,
                active_processes=[],
                constraints_satisfied=True
            )
            
            # Check if state satisfies system constraints
            if self._check_constraints(state):
                states.append(state)
                
        return states
        
    def _generate_quantity_combinations(self) -> List[Dict[str, QualitativeQuantity]]:
        """Generate all possible combinations of quantity values"""
        
        combinations = []
        
        if not self.quantities:
            return [{}]
            
        # For simplicity, use common qualitative values
        # In full implementation, would use landmark values from system description
        qualitative_values = ['zero', 'positive', 'negative']
        derivative_values = ['increasing', 'decreasing', 'steady']
        
        def generate_recursive(quantities_left, current_combo):
            if not quantities_left:
                combinations.append(current_combo.copy())
                return
                
            quantity_name = list(quantities_left.keys())[0]
            remaining = {k: v for k, v in quantities_left.items() if k != quantity_name}
            
            for value in qualitative_values:
                for derivative in derivative_values:
                    current_combo[quantity_name] = QualitativeQuantity(
                        name=quantity_name,
                        value=value,
                        derivative=derivative,
                        landmarks=quantities_left[quantity_name].get('landmarks', [])
                    )
                    generate_recursive(remaining, current_combo)
                    
        generate_recursive(self.quantities, {})
        
        # Limit combinations for practical purposes
        return combinations[:100]  # Truncate for demonstration
        
    def _check_constraints(self, state: QualitativeState) -> bool:
        """Check if a state satisfies system constraints"""
        
        # Basic constraint checking
        for constraint in self.constraints:
            if not self._evaluate_constraint(constraint, state):
                return False
                
        return True
        
    def _evaluate_constraint(self, constraint: Dict, state: QualitativeState) -> bool:
        """Evaluate a single constraint against a state"""
        
        constraint_type = constraint.get('type', 'unknown')
        
        if constraint_type == 'conservation':
            # Energy/mass conservation constraints
            return self._check_conservation(constraint, state)
        elif constraint_type == 'ordering':
            # Ordering constraints (A > B)
            return self._check_ordering(constraint, state)
        elif constraint_type == 'correspondence':
            # Correspondences between quantities
            return self._check_correspondence(constraint, state)
        else:
            return True  # Unknown constraints pass by default
            
    def _check_conservation(self, constraint: Dict, state: QualitativeState) -> bool:
        """Check conservation constraints"""
        # Simplified conservation check
        return True
        
    def _check_ordering(self, constraint: Dict, state: QualitativeState) -> bool:
        """Check ordering constraints"""
        # Simplified ordering check
        return True
        
    def _check_correspondence(self, constraint: Dict, state: QualitativeState) -> bool:
        """Check correspondence constraints"""
        # Simplified correspondence check
        return True
        
    def _add_state_node(self, state: QualitativeState) -> int:
        """Add a state to the envisionment graph"""
        
        node_id = self.next_node_id
        self.next_node_id += 1
        
        # Determine active processes for this state
        active_processes = self._determine_active_processes(state)
        
        node = EnvisionmentNode(
            state=state,
            id=node_id,
            transitions=[],
            processes=active_processes,
            stability='unknown'
        )
        
        self.nodes[node_id] = node
        return node_id
        
    def _determine_active_processes(self, state: QualitativeState) -> List[QualitativeProcess]:
        """Determine which processes are active in a given state"""
        
        active = []
        
        for process_desc in self.processes:
            if self._process_applies(process_desc, state):
                process = QualitativeProcess(
                    name=process_desc['name'],
                    conditions=process_desc.get('conditions', []),
                    effects=process_desc.get('effects', []),
                    active=True
                )
                active.append(process)
                
        return active
        
    def _process_applies(self, process_desc: Dict, state: QualitativeState) -> bool:
        """Check if a process applies in the given state"""
        
        conditions = process_desc.get('conditions', [])
        
        for condition in conditions:
            if not self._evaluate_process_condition(condition, state):
                return False
                
        return True
        
    def _evaluate_process_condition(self, condition: Dict, state: QualitativeState) -> bool:
        """Evaluate a process condition"""
        # Simplified condition evaluation
        return True
        
    def _generate_transitions(self, verbose: bool = True):
        """Generate state transitions based on process dynamics"""
        
        nodes_to_process = list(self.nodes.keys())
        
        for node_id in nodes_to_process:
            node = self.nodes[node_id]
            
            # For each active process, determine possible next states
            next_states = self._compute_next_states(node)
            
            for next_state in next_states:
                next_node_id = self._find_or_create_state_node(next_state)
                if next_node_id not in node.transitions:
                    node.transitions.append(next_node_id)
                    
        if verbose:
            total_transitions = sum(len(node.transitions) for node in self.nodes.values())
            print(f"   Generated {total_transitions} transitions")
            
    def _compute_next_states(self, node: EnvisionmentNode) -> List[QualitativeState]:
        """Compute possible next states from current node"""
        
        current_state = node.state
        next_states = []
        
        # Apply effects of each active process
        for process in node.processes:
            modified_state = self._apply_process_effects(current_state, process)
            if modified_state and modified_state != current_state:
                next_states.append(modified_state)
                
        # Consider process limit points (discontinuous changes)
        limit_states = self._compute_limit_points(current_state, node.processes)
        next_states.extend(limit_states)
        
        return next_states
        
    def _apply_process_effects(self, state: QualitativeState, 
                              process: QualitativeProcess) -> Optional[QualitativeState]:
        """Apply process effects to generate next state"""
        
        # Create new state with modified quantities
        new_quantities = {}
        for name, quantity in state.quantities.items():
            new_quantities[name] = QualitativeQuantity(
                name=quantity.name,
                value=quantity.value,
                derivative=quantity.derivative,
                landmarks=quantity.landmarks
            )
            
        # Apply process effects (simplified)
        for effect in process.effects:
            quantity_name = effect.get('quantity')
            if quantity_name in new_quantities:
                # Modify derivative based on effect
                if effect.get('change') == 'increase':
                    new_quantities[quantity_name].derivative = 'increasing'
                elif effect.get('change') == 'decrease':
                    new_quantities[quantity_name].derivative = 'decreasing'
                    
        new_state = QualitativeState(
            quantities=new_quantities,
            active_processes=[],
            constraints_satisfied=True
        )
        
        return new_state if self._check_constraints(new_state) else None
        
    def _compute_limit_points(self, state: QualitativeState, 
                             processes: List[QualitativeProcess]) -> List[QualitativeState]:
        """Compute limit points where discontinuous changes occur"""
        
        limit_states = []
        
        # Check for quantity transitions (e.g., positive -> zero -> negative)
        for name, quantity in state.quantities.items():
            if quantity.derivative == 'decreasing' and quantity.value == 'positive':
                # Approaching zero from positive
                zero_state = self._create_limit_state(state, name, 'zero')
                if zero_state:
                    limit_states.append(zero_state)
                    
        return limit_states
        
    def _create_limit_state(self, base_state: QualitativeState, 
                           quantity_name: str, new_value: str) -> Optional[QualitativeState]:
        """Create a limit state with modified quantity value"""
        
        new_quantities = {}
        for name, quantity in base_state.quantities.items():
            if name == quantity_name:
                new_quantities[name] = QualitativeQuantity(
                    name=quantity.name,
                    value=new_value,
                    derivative='steady',  # At limit point
                    landmarks=quantity.landmarks
                )
            else:
                new_quantities[name] = quantity
                
        new_state = QualitativeState(
            quantities=new_quantities,
            active_processes=[],
            constraints_satisfied=True
        )
        
        return new_state if self._check_constraints(new_state) else None
        
    def _find_or_create_state_node(self, state: QualitativeState) -> int:
        """Find existing state node or create new one"""
        
        # Look for existing equivalent state
        for node_id, node in self.nodes.items():
            if self._states_equivalent(node.state, state):
                return node_id
                
        # Create new node
        return self._add_state_node(state)
        
    def _states_equivalent(self, state1: QualitativeState, state2: QualitativeState) -> bool:
        """Check if two states are qualitatively equivalent"""
        
        if set(state1.quantities.keys()) != set(state2.quantities.keys()):
            return False
            
        for name in state1.quantities:
            q1 = state1.quantities[name]
            q2 = state2.quantities[name]
            
            if q1.value != q2.value or q1.derivative != q2.derivative:
                return False
                
        return True
        
    def _analyze_stability(self):
        """Analyze stability of each state"""
        
        for node_id, node in self.nodes.items():
            if not node.transitions:
                # No outgoing transitions - stable
                node.stability = 'stable'
            elif any(trans_id == node_id for trans_id in node.transitions):
                # Self-loop - potentially stable
                node.stability = 'stable'
            else:
                # Has outgoing transitions - unstable
                node.stability = 'unstable'
                
    def get_reachable_states(self, start_state_id: int, max_depth: int = 10) -> List[int]:
        """Get all states reachable from a starting state"""
        
        reachable = set()
        queue = [(start_state_id, 0)]
        
        while queue:
            node_id, depth = queue.pop(0)
            
            if node_id in reachable or depth > max_depth:
                continue
                
            reachable.add(node_id)
            
            if node_id in self.nodes:
                for next_id in self.nodes[node_id].transitions:
                    if next_id not in reachable:
                        queue.append((next_id, depth + 1))
                        
        return list(reachable)
        
    def predict_behavior(self, initial_state_id: int, steps: int = 5) -> List[int]:
        """Predict system behavior from initial state"""
        
        if initial_state_id not in self.nodes:
            return []
            
        path = [initial_state_id]
        current_id = initial_state_id
        
        for _ in range(steps):
            node = self.nodes[current_id]
            
            if not node.transitions:
                break  # Reached stable state
                
            # Choose first transition (could be made more sophisticated)
            next_id = node.transitions[0]
            path.append(next_id)
            current_id = next_id
            
        return path
        
    def get_envisionment_graph(self) -> Dict[str, Any]:
        """Get envisionment as graph structure for visualization"""
        
        nodes = []
        edges = []
        
        for node_id, node in self.nodes.items():
            nodes.append({
                'id': node_id,
                'stability': node.stability,
                'processes': len(node.processes),
                'quantities': {name: {'value': q.value, 'derivative': q.derivative} 
                              for name, q in node.state.quantities.items()}
            })
            
            for target_id in node.transitions:
                edges.append({'source': node_id, 'target': target_id})
                
        return {
            'nodes': nodes,
            'edges': edges,
            'statistics': {
                'total_nodes': len(nodes),
                'total_edges': len(edges),
                'stable_nodes': len([n for n in nodes if n['stability'] == 'stable'])
            }
        }