"""
Confluence-based Qualitative Physics Engine
Based on: de Kleer & Brown (1984) "A Qualitative Physics Based on Confluences"

Key Innovation: Models physical systems using confluences - junctions where quantities flow
Revolutionary because: Systematic approach to qualitative simulation of continuous systems
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Set, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum, auto
from abc import ABC, abstractmethod
import networkx as nx
from collections import defaultdict
import warnings


class QuantityType(Enum):
    """Types of physical quantities"""
    AMOUNT = auto()          # A(x) - amount of substance x
    FLOW = auto()            # I(x,y) - flow of x from/to y  
    PRESSURE = auto()        # P(x) - pressure at x
    TEMPERATURE = auto()     # T(x) - temperature at x
    LEVEL = auto()          # L(x) - level/height at x
    RATE = auto()           # R(x) - rate of change
    VELOCITY = auto()       # V(x) - velocity at x


class ConfluenceType(Enum):
    """Types of confluences in qualitative physics"""
    CONTAINER = "container"       # Container confluence
    FLOW = "flow"                # Flow confluence  
    HEAT_FLOW = "heat_flow"      # Heat flow confluence
    BOILING = "boiling"          # Phase change confluence
    VALVE = "valve"              # Valve confluence


class QualitativeState(Enum):
    """Qualitative states of physical quantities"""
    ZERO = 0
    POSITIVE = 1
    NEGATIVE = -1
    INCREASING = "inc"
    DECREASING = "dec"
    STEADY = "std"


class QualitativeValue(Enum):
    """Qualitative values for quantities"""
    NEGATIVE = "-"          # Decreasing, flowing out, below normal
    ZERO = "0"             # Steady state, no flow, at normal
    POSITIVE = "+"         # Increasing, flowing in, above normal
    UNKNOWN = "?"          # Ambiguous or undetermined


@dataclass
class QualitativeQuantity:
    """
    Qualitative representation of a physical quantity
    
    In de Kleer & Brown's system, each quantity has:
    - A qualitative value (-, 0, +)
    - A derivative (rate of change)
    - Dependencies on other quantities
    """
    name: str
    quantity_type: QuantityType
    value: QualitativeValue = QualitativeValue.UNKNOWN
    derivative: QualitativeValue = QualitativeValue.UNKNOWN
    landmark_values: List[str] = field(default_factory=list)
    
    def __str__(self) -> str:
        return f"{self.name}[{self.value.value}, d{self.derivative.value}]"
    
    def __repr__(self) -> str:
        return self.__str__()


@dataclass 
class Confluence:
    """
    A confluence represents a physical junction where quantities meet
    
    Key insight from de Kleer & Brown: Physical systems can be modeled
    as networks of confluences where conservation laws apply.
    
    Examples:
    - Pipe junction: flow conservation (sum of flows = 0)
    - Heat junction: energy conservation
    - Electrical node: current conservation (Kirchhoff's law)
    """
    name: str
    confluence_type: str  # 'flow', 'heat', 'electrical', etc.
    quantities: List[QualitativeQuantity] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)  # Conservation laws
    
    def add_quantity(self, quantity: QualitativeQuantity) -> None:
        """Add a quantity to this confluence"""
        self.quantities.append(quantity)
    
    def get_flow_quantities(self) -> List[QualitativeQuantity]:
        """Get all flow quantities in this confluence"""
        return [q for q in self.quantities if q.quantity_type == QuantityType.FLOW]
    
    def apply_conservation_law(self) -> Dict[str, Any]:
        """
        Apply conservation constraints at this confluence
        
        For flow confluences: ΣI = 0 (sum of flows equals zero)
        For thermal: heat in = heat out
        For electrical: ΣI = 0 (Kirchhoff's current law)
        """
        results = {'constraints': [], 'implications': []}
        
        if self.confluence_type == 'flow':
            flows = self.get_flow_quantities()
            if len(flows) >= 2:
                constraint = f"sum({[f.name for f in flows]}) = 0"
                results['constraints'].append(constraint)
                
                # Derive implications from conservation
                # If we know n-1 flows, we can determine the nth
                unknown_flows = [f for f in flows if f.value == QualitativeValue.UNKNOWN]
                known_flows = [f for f in flows if f.value != QualitativeValue.UNKNOWN]
                
                if len(unknown_flows) == 1 and len(known_flows) >= 1:
                    # Can determine the unknown flow
                    unknown = unknown_flows[0]
                    known_sum = self._sum_qualitative_values([f.value for f in known_flows])
                    unknown.value = self._negate_qualitative_value(known_sum)
                    results['implications'].append(f"Determined {unknown.name} = {unknown.value.value}")
        
        return results
    
    def _sum_qualitative_values(self, values: List[QualitativeValue]) -> QualitativeValue:
        """Sum qualitative values using qualitative arithmetic"""
        if not values:
            return QualitativeValue.ZERO
        
        pos_count = sum(1 for v in values if v == QualitativeValue.POSITIVE)
        neg_count = sum(1 for v in values if v == QualitativeValue.NEGATIVE)
        zero_count = sum(1 for v in values if v == QualitativeValue.ZERO)
        unknown_count = sum(1 for v in values if v == QualitativeValue.UNKNOWN)
        
        if unknown_count > 0:
            return QualitativeValue.UNKNOWN
        elif pos_count > neg_count:
            return QualitativeValue.POSITIVE
        elif neg_count > pos_count:
            return QualitativeValue.NEGATIVE
        elif pos_count == neg_count:
            return QualitativeValue.ZERO
        else:
            return QualitativeValue.UNKNOWN
    
    def _negate_qualitative_value(self, value: QualitativeValue) -> QualitativeValue:
        """Negate a qualitative value"""
        if value == QualitativeValue.POSITIVE:
            return QualitativeValue.NEGATIVE
        elif value == QualitativeValue.NEGATIVE:
            return QualitativeValue.POSITIVE
        else:
            return value


@dataclass
class QualitativeConstraint:
    """
    Qualitative constraint between quantities
    
    Examples:
    - Monotonic: if A increases, B increases (M+[A,B])
    - Proportional: A proportional to B
    - Correspondence: if A is high, B is high
    """
    name: str
    constraint_type: str  # 'M+', 'M-', 'PROP', 'CORR'
    source_quantity: str
    target_quantity: str
    
    def apply(self, quantities: Dict[str, QualitativeQuantity]) -> List[str]:
        """Apply this constraint to propagate values"""
        implications = []
        
        if self.source_quantity not in quantities or self.target_quantity not in quantities:
            return implications
        
        source = quantities[self.source_quantity]
        target = quantities[self.target_quantity]
        
        if self.constraint_type == 'M+':
            # Monotonic increasing: if source increases, target increases
            if source.derivative == QualitativeValue.POSITIVE and target.derivative == QualitativeValue.UNKNOWN:
                target.derivative = QualitativeValue.POSITIVE
                implications.append(f"M+: {source.name} → {target.name} derivative = +")
            elif source.derivative == QualitativeValue.NEGATIVE and target.derivative == QualitativeValue.UNKNOWN:
                target.derivative = QualitativeValue.NEGATIVE
                implications.append(f"M+: {source.name} → {target.name} derivative = -")
        
        elif self.constraint_type == 'M-':
            # Monotonic decreasing: if source increases, target decreases
            if source.derivative == QualitativeValue.POSITIVE and target.derivative == QualitativeValue.UNKNOWN:
                target.derivative = QualitativeValue.NEGATIVE
                implications.append(f"M-: {source.name} → {target.name} derivative = -")
            elif source.derivative == QualitativeValue.NEGATIVE and target.derivative == QualitativeValue.UNKNOWN:
                target.derivative = QualitativeValue.POSITIVE
                implications.append(f"M-: {source.name} → {target.name} derivative = +")
        
        elif self.constraint_type == 'PROP':
            # Proportional relationship
            if source.value != QualitativeValue.UNKNOWN and target.value == QualitativeValue.UNKNOWN:
                target.value = source.value
                implications.append(f"PROP: {target.name} = {source.value.value}")
        
        return implications


class ConfluencePhysicsEngine:
    """
    de Kleer & Brown Confluence-based Qualitative Physics Engine
    
    Models physical systems as networks of confluences (junctions)
    where conservation laws apply. Enables qualitative simulation
    and reasoning about continuous physical systems.
    
    Key Features:
    - Confluence-based modeling
    - Conservation law enforcement  
    - Qualitative constraint propagation
    - State space exploration (envisionment)
    - Causal reasoning
    """
    
    def __init__(self):
        # System components
        self.quantities: Dict[str, QualitativeQuantity] = {}
        self.confluences: Dict[str, Confluence] = {}
        self.constraints: List[QualitativeConstraint] = []
        
        # Simulation state
        self.current_state: Dict[str, QualitativeQuantity] = {}
        self.state_history: List[Dict[str, Any]] = []
        self.time_step: int = 0
        
        # Analysis results
        self.envisionment_graph: Optional[nx.DiGraph] = None
        self.causal_graph: Optional[nx.DiGraph] = None
        
    def add_quantity(self, name: str, quantity_type: QuantityType, 
                    initial_value: QualitativeValue = QualitativeValue.UNKNOWN,
                    initial_derivative: QualitativeValue = QualitativeValue.UNKNOWN) -> QualitativeQuantity:
        """Add a qualitative quantity to the system"""
        quantity = QualitativeQuantity(name, quantity_type, initial_value, initial_derivative)
        self.quantities[name] = quantity
        self.current_state[name] = quantity
        return quantity
    
    def add_confluence(self, name: str, confluence_type: str) -> Confluence:
        """Add a confluence (junction) to the system"""
        confluence = Confluence(name, confluence_type)
        self.confluences[name] = confluence
        return confluence
    
    def connect_quantity_to_confluence(self, quantity_name: str, confluence_name: str) -> None:
        """Connect a quantity to a confluence"""
        if quantity_name in self.quantities and confluence_name in self.confluences:
            quantity = self.quantities[quantity_name]
            confluence = self.confluences[confluence_name]
            confluence.add_quantity(quantity)
    
    def add_constraint(self, name: str, constraint_type: str, 
                      source: str, target: str) -> None:
        """Add a qualitative constraint between quantities"""
        constraint = QualitativeConstraint(name, constraint_type, source, target)
        self.constraints.append(constraint)
    
    def propagate_constraints(self) -> List[str]:
        """
        Propagate constraints to derive new quantity values
        
        This implements the core constraint propagation algorithm
        from de Kleer & Brown's qualitative physics.
        """
        implications = []
        changed = True
        iteration = 0
        max_iterations = 100
        
        while changed and iteration < max_iterations:
            changed = False
            iteration += 1
            
            # Apply confluence constraints (conservation laws)
            for confluence in self.confluences.values():
                result = confluence.apply_conservation_law()
                if result['implications']:
                    implications.extend(result['implications'])
                    changed = True
            
            # Apply qualitative constraints
            for constraint in self.constraints:
                constraint_implications = constraint.apply(self.quantities)
                if constraint_implications:
                    implications.extend(constraint_implications)
                    changed = True
            
            # Update current state
            self.current_state = {name: q for name, q in self.quantities.items()}
        
        if iteration >= max_iterations:
            warnings.warn("Constraint propagation did not converge")
        
        return implications
    
    def simulate_step(self) -> Dict[str, Any]:
        """
        Perform one simulation step
        
        Updates quantity values based on their derivatives and
        applies constraint propagation.
        """
        self.time_step += 1
        step_results = {
            'time_step': self.time_step,
            'state_changes': [],
            'implications': []
        }
        
        # Update quantities based on derivatives
        for name, quantity in self.quantities.items():
            old_value = quantity.value
            
            # Simple qualitative integration: value += derivative
            if quantity.derivative == QualitativeValue.POSITIVE:
                if quantity.value == QualitativeValue.NEGATIVE:
                    quantity.value = QualitativeValue.ZERO
                elif quantity.value == QualitativeValue.ZERO:
                    quantity.value = QualitativeValue.POSITIVE
                # If already positive, stays positive
            elif quantity.derivative == QualitativeValue.NEGATIVE:
                if quantity.value == QualitativeValue.POSITIVE:
                    quantity.value = QualitativeValue.ZERO
                elif quantity.value == QualitativeValue.ZERO:
                    quantity.value = QualitativeValue.NEGATIVE
                # If already negative, stays negative
            
            if quantity.value != old_value:
                step_results['state_changes'].append(f"{name}: {old_value.value} → {quantity.value.value}")
        
        # Propagate constraints
        implications = self.propagate_constraints()
        step_results['implications'] = implications
        
        # Record state
        state_snapshot = {
            name: {'value': q.value, 'derivative': q.derivative}
            for name, q in self.quantities.items()
        }
        self.state_history.append(state_snapshot)
        
        return step_results
    
    def build_envisionment(self, max_states: int = 50) -> nx.DiGraph:
        """
        Build envisionment - the space of all possible qualitative states
        
        This is a key component of de Kleer & Brown's approach:
        systematically explore all reachable qualitative states.
        """
        envisionment = nx.DiGraph()
        
        # Generate all possible state combinations
        possible_values = [QualitativeValue.NEGATIVE, QualitativeValue.ZERO, QualitativeValue.POSITIVE]
        quantity_names = list(self.quantities.keys())
        
        from itertools import product
        
        state_count = 0
        for value_combination in product(possible_values, repeat=len(quantity_names)):
            if state_count >= max_states:
                break
            
            # Create state
            state = {}
            for i, name in enumerate(quantity_names):
                state[name] = {
                    'value': value_combination[i],
                    'derivative': QualitativeValue.UNKNOWN  # Will be determined by constraints
                }
            
            # Check if state is physically consistent
            if self._is_state_consistent(state):
                state_id = self._state_to_id(state)
                envisionment.add_node(state_id, state=state)
                state_count += 1
        
        # Add transitions between states
        for state_id in envisionment.nodes():
            state = envisionment.nodes[state_id]['state']
            next_states = self._get_successor_states(state)
            
            for next_state in next_states:
                next_state_id = self._state_to_id(next_state)
                if next_state_id in envisionment.nodes():
                    envisionment.add_edge(state_id, next_state_id)
        
        self.envisionment_graph = envisionment
        return envisionment
    
    def _is_state_consistent(self, state: Dict[str, Dict[str, QualitativeValue]]) -> bool:
        """Check if a qualitative state is physically consistent"""
        # Temporarily set quantities to this state
        original_quantities = {name: q.copy() for name, q in self.quantities.items()}
        
        try:
            for name, values in state.items():
                if name in self.quantities:
                    self.quantities[name].value = values['value']
                    self.quantities[name].derivative = values['derivative']
            
            # Check confluence constraints
            for confluence in self.confluences.values():
                result = confluence.apply_conservation_law()
                # If conservation law is violated, state is inconsistent
                if any('contradiction' in impl.lower() for impl in result.get('implications', [])):
                    return False
            
            return True
            
        finally:
            # Restore original quantities
            self.quantities = original_quantities
    
    def _state_to_id(self, state: Dict[str, Dict[str, QualitativeValue]]) -> str:
        """Convert state to unique identifier"""
        state_tuple = tuple(
            (name, values['value'].value, values['derivative'].value)
            for name, values in sorted(state.items())
        )
        return str(hash(state_tuple))
    
    def _get_successor_states(self, state: Dict[str, Dict[str, QualitativeValue]]) -> List[Dict[str, Dict[str, QualitativeValue]]]:
        """Get possible successor states from current state"""
        successors = []
        
        # For each quantity, if it has a non-zero derivative, compute next value
        next_state = state.copy()
        changed = False
        
        for name, values in state.items():
            derivative = values['derivative']
            current_value = values['value']
            
            if derivative == QualitativeValue.POSITIVE:
                if current_value == QualitativeValue.NEGATIVE:
                    next_state[name]['value'] = QualitativeValue.ZERO
                    changed = True
                elif current_value == QualitativeValue.ZERO:
                    next_state[name]['value'] = QualitativeValue.POSITIVE
                    changed = True
            elif derivative == QualitativeValue.NEGATIVE:
                if current_value == QualitativeValue.POSITIVE:
                    next_state[name]['value'] = QualitativeValue.ZERO
                    changed = True
                elif current_value == QualitativeValue.ZERO:
                    next_state[name]['value'] = QualitativeValue.NEGATIVE
                    changed = True
        
        if changed:
            successors.append(next_state)
        
        return successors
    
    def build_causal_graph(self) -> nx.DiGraph:
        """
        Build causal dependency graph showing how quantities influence each other
        """
        causal_graph = nx.DiGraph()
        
        # Add nodes for all quantities
        for name in self.quantities.keys():
            causal_graph.add_node(name)
        
        # Add edges from constraints
        for constraint in self.constraints:
            causal_graph.add_edge(constraint.source_quantity, constraint.target_quantity,
                                 constraint_type=constraint.constraint_type)
        
        # Add edges from confluences
        for confluence in self.confluences.values():
            quantities = [q.name for q in confluence.quantities]
            # In confluences, quantities mutually influence each other
            for i, q1 in enumerate(quantities):
                for j, q2 in enumerate(quantities):
                    if i != j:
                        causal_graph.add_edge(q1, q2, constraint_type='confluence')
        
        self.causal_graph = causal_graph
        return causal_graph
    
    def analyze_behavior(self, initial_conditions: Dict[str, Tuple[QualitativeValue, QualitativeValue]],
                        steps: int = 10) -> Dict[str, Any]:
        """
        Analyze system behavior from given initial conditions
        
        Args:
            initial_conditions: Dict mapping quantity names to (value, derivative) tuples
            steps: Number of simulation steps
        """
        # Set initial conditions
        for name, (value, derivative) in initial_conditions.items():
            if name in self.quantities:
                self.quantities[name].value = value
                self.quantities[name].derivative = derivative
        
        # Run simulation
        simulation_results = []
        for step in range(steps):
            step_result = self.simulate_step()
            simulation_results.append(step_result)
            
            # Check for equilibrium
            if not step_result['state_changes']:
                break
        
        # Analyze results
        analysis = {
            'initial_conditions': initial_conditions,
            'simulation_results': simulation_results,
            'final_state': {name: {'value': q.value, 'derivative': q.derivative} 
                          for name, q in self.quantities.items()},
            'reached_equilibrium': len(simulation_results) < steps,
            'state_trajectory': [result['state_changes'] for result in simulation_results]
        }
        
        return analysis
    
    def plot_system_structure(self, figsize: Tuple[int, int] = (12, 8)) -> None:
        """Plot the structure of confluences and quantities"""
        if not self.confluences and not self.quantities:
            print("No system structure to plot.")
            return
        
        plt.figure(figsize=figsize)
        
        # Create graph representation
        G = nx.Graph()
        
        # Add confluence nodes
        for name, confluence in self.confluences.items():
            G.add_node(name, node_type='confluence', confluence_type=confluence.confluence_type)
        
        # Add quantity nodes and connections
        for name, quantity in self.quantities.items():
            G.add_node(name, node_type='quantity', quantity_type=quantity.quantity_type.name)
            
            # Connect to confluences
            for conf_name, confluence in self.confluences.items():
                if quantity in confluence.quantities:
                    G.add_edge(name, conf_name)
        
        # Layout
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        # Draw confluence nodes
        confluence_nodes = [n for n, d in G.nodes(data=True) if d.get('node_type') == 'confluence']
        if confluence_nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=confluence_nodes, 
                                 node_color='lightblue', node_size=1000, 
                                 node_shape='s', alpha=0.8)
        
        # Draw quantity nodes
        quantity_nodes = [n for n, d in G.nodes(data=True) if d.get('node_type') == 'quantity']
        if quantity_nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=quantity_nodes,
                                 node_color='orange', node_size=800, 
                                 alpha=0.8)
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, alpha=0.5)
        
        # Add labels
        nx.draw_networkx_labels(G, pos, font_size=8)
        
        plt.title("Confluence-based System Structure\n(Blue squares = Confluences, Orange circles = Quantities)")
        plt.axis('off')
        plt.tight_layout()
        plt.show()
    
    def plot_causal_graph(self, figsize: Tuple[int, int] = (10, 8)) -> None:
        """Plot the causal dependency graph"""
        if self.causal_graph is None:
            self.build_causal_graph()
        
        plt.figure(figsize=figsize)
        
        # Layout for causal graph
        try:
            pos = nx.planar_layout(self.causal_graph)
        except:
            pos = nx.spring_layout(self.causal_graph, k=2)
        
        # Draw nodes
        nx.draw_networkx_nodes(self.causal_graph, pos, node_color='lightgreen', 
                              node_size=1000, alpha=0.8)
        
        # Draw edges with different styles for different constraint types
        edge_colors = []
        edge_styles = []
        
        for u, v, data in self.causal_graph.edges(data=True):
            constraint_type = data.get('constraint_type', 'unknown')
            if constraint_type == 'M+':
                edge_colors.append('blue')
                edge_styles.append('solid')
            elif constraint_type == 'M-':
                edge_colors.append('red')
                edge_styles.append('solid')
            elif constraint_type == 'confluence':
                edge_colors.append('purple')
                edge_styles.append('dashed')
            else:
                edge_colors.append('gray')
                edge_styles.append('solid')
        
        nx.draw_networkx_edges(self.causal_graph, pos, edge_color=edge_colors, 
                              arrows=True, arrowsize=20)
        
        # Add labels
        nx.draw_networkx_labels(self.causal_graph, pos, font_size=10)
        
        plt.title("Causal Dependency Graph")
        plt.axis('off')
        plt.tight_layout()
        plt.show()
    
    def get_system_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary of the qualitative physics system"""
        return {
            'quantities': len(self.quantities),
            'confluences': len(self.confluences),
            'constraints': len(self.constraints),
            'time_step': self.time_step,
            'quantity_details': {name: str(q) for name, q in self.quantities.items()},
            'confluence_types': list(set(c.confluence_type for c in self.confluences.values())),
            'constraint_types': list(set(c.constraint_type for c in self.constraints))
        }
    
    @classmethod
    def create_water_tank_system(cls) -> 'ConfluencePhysicsEngine':
        """
        Create demo water tank system with inflows and outflows
        
        Classic qualitative physics example: water tank with pipes
        demonstrating flow conservation at junctions.
        """
        engine = cls()
        
        # Add quantities
        tank_level = engine.add_quantity("tank_level", QuantityType.LEVEL, 
                                       QualitativeValue.POSITIVE, QualitativeValue.UNKNOWN)
        inflow = engine.add_quantity("inflow", QuantityType.FLOW,
                                   QualitativeValue.POSITIVE, QualitativeValue.ZERO)
        outflow = engine.add_quantity("outflow", QuantityType.FLOW,
                                    QualitativeValue.POSITIVE, QualitativeValue.ZERO)
        net_flow = engine.add_quantity("net_flow", QuantityType.FLOW,
                                     QualitativeValue.UNKNOWN, QualitativeValue.UNKNOWN)
        
        # Add confluence (tank junction)
        tank_junction = engine.add_confluence("tank_junction", "flow")
        engine.connect_quantity_to_confluence("inflow", "tank_junction")
        engine.connect_quantity_to_confluence("outflow", "tank_junction") 
        engine.connect_quantity_to_confluence("net_flow", "tank_junction")
        
        # Add constraints
        engine.add_constraint("level_flow", "M+", "net_flow", "tank_level")  # Net flow increases level
        engine.add_constraint("pressure_outflow", "M+", "tank_level", "outflow")  # Higher level increases outflow
        
        return engine
    
    @classmethod  
    def create_thermal_system(cls) -> 'ConfluencePhysicsEngine':
        """
        Create demo thermal system with heat flow
        
        Example: heat flow between two bodies through conduction
        """
        engine = cls()
        
        # Add quantities
        temp1 = engine.add_quantity("temp_body1", QuantityType.TEMPERATURE,
                                  QualitativeValue.POSITIVE, QualitativeValue.NEGATIVE)
        temp2 = engine.add_quantity("temp_body2", QuantityType.TEMPERATURE, 
                                  QualitativeValue.ZERO, QualitativeValue.POSITIVE)
        heat_flow = engine.add_quantity("heat_flow", QuantityType.FLOW,
                                       QualitativeValue.POSITIVE, QualitativeValue.UNKNOWN)
        
        # Heat junction
        heat_junction = engine.add_confluence("heat_junction", "heat")
        engine.connect_quantity_to_confluence("heat_flow", "heat_junction")
        
        # Constraints
        engine.add_constraint("temp_diff_flow", "M+", "temp_body1", "heat_flow")  # Higher temp1 increases flow
        engine.add_constraint("flow_cooling1", "M-", "heat_flow", "temp_body1")   # Flow cools body1
        engine.add_constraint("flow_heating2", "M+", "heat_flow", "temp_body2")   # Flow heats body2
        
        return engine