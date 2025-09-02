"""
⚙️ Qualitative Reasoning - Process Engine Module
===============================================

This module provides the core process management and causal reasoning engine for 
qualitative reasoning systems based on Forbus's Process Theory and de Kleer's 
Qualitative Physics framework.

📚 Theoretical Foundation:
Forbus, K. D. (1984). "Qualitative Process Theory", Artificial Intelligence, 24(1-3)
Forbus, K. D., & de Kleer, J. (1993). "Building Problem Solvers", MIT Press
de Kleer, J., & Brown, J. S. (1984). "A Qualitative Physics Based on Confluences"

🧠 Process Theory Core Concepts:
Forbus's Qualitative Process Theory revolutionized AI's understanding of physical 
systems by introducing the concept that physical behavior emerges from active 
processes that influence quantities over time. This is fundamentally different 
from static constraint-based approaches.

Key Theoretical Principles:
1. **Process Ontology**: The world consists of objects, quantities, and processes
2. **Process Activation**: Processes become active when their preconditions are met
3. **Causal Influences**: Active processes influence quantities through I+ and I- relations
4. **Temporal Reasoning**: Process behavior unfolds over qualitative time intervals
5. **Causal Explanation**: System behavior is explained through process activation chains

🔬 Mathematical Framework:
Process Definition: P = ⟨preconditions, quantity_conditions, influences⟩
Process State: Active(P,t) ↔ preconditions(P,t) ∧ quantity_conditions(P,t)  
Causal Influence: I±(quantity) → ∂quantity/∂t = ±
Process Interaction: Multiple processes can influence the same quantity

🎯 Core Process Engine Capabilities:
- Process condition evaluation and activation logic
- Causal influence application to quantity derivatives  
- Process interaction and conflict resolution
- Causal graph construction and management
- Process-based behavioral explanation
- Temporal process reasoning and prediction

🌟 Implementation Highlights:
- Secure process condition evaluation (no eval() vulnerabilities)
- Efficient process activation algorithms
- Robust causal influence computation
- Comprehensive process interaction handling
- Rich causal explanation generation
- Extensible process modeling framework

🔧 Integration:
This mixin integrates with the constraint engine for condition evaluation
and core types for process and quantity representations. It provides the
causal reasoning backbone for the entire qualitative reasoning system.

Author: Benedict Chen
Based on foundational work by Kenneth Forbus and Johan de Kleer
Implementation follows modern secure coding practices
"""

from typing import Dict, List, Tuple, Union, Optional, Any, Set
from dataclasses import dataclass
from .core_types import QualitativeProcess, QualitativeQuantity, QualitativeValue, QualitativeDirection, QualitativeState


class ProcessEngineMixin:
    """
    Process Engine Mixin for Qualitative Reasoning Systems
    
    This mixin provides comprehensive process management capabilities based on
    Forbus's Qualitative Process Theory. It handles process activation, influence
    application, causal reasoning, and behavioral explanation.
    
    🧠 Theoretical Background:
    Process Theory views physical systems as collections of processes that become
    active under specific conditions and influence quantities through causal relationships.
    This differs from purely constraint-based approaches by explicitly representing
    the causal mechanisms that drive system behavior.
    
    Key Process Theory Concepts:
    - **Individual View**: Each object has associated quantities and participates in processes
    - **Process Activation**: Processes have preconditions that must be satisfied
    - **Quantity Conditions**: Additional constraints on quantity values for activation  
    - **Influences**: I+ increases quantity, I- decreases quantity over time
    - **Process Structure**: Captures the causal organization of physical phenomena
    
    🔧 Engine Components:
    1. Process Management: Add, configure, and track processes
    2. Condition Evaluation: Safe evaluation of process preconditions
    3. Activation Logic: Determine which processes are currently active
    4. Influence Application: Apply process effects to quantity derivatives
    5. Causal Graph: Track causal relationships between processes and quantities
    6. Behavioral Explanation: Generate causal explanations for quantity behavior
    """
    
    def __init__(self):
        """Initialize process engine components"""
        
        # Process storage and management
        self.processes: Dict[str, QualitativeProcess] = {}
        self.causal_graph: Dict[str, List[str]] = {}  # process -> [influenced_quantities]
        
        # Process interaction tracking
        self.process_dependencies: Dict[str, Set[str]] = {}  # process -> {required_processes}
        self.quantity_process_map: Dict[str, Set[str]] = {}  # quantity -> {affecting_processes}
        
        # Process activation history for temporal reasoning
        self.process_history: List[Dict[str, bool]] = []  # [{process_name: active_state}]
        self.activation_changes: List[Tuple[str, str, bool]] = []  # [(time, process, activated)]
        
    def add_process(self, name: str, preconditions: List[str], 
                   quantity_conditions: List[str], influences: List[str]) -> QualitativeProcess:
        """
        Add a qualitative process to the system
        
        This method implements Forbus's process definition framework, creating
        a complete process specification with preconditions, quantity conditions,
        and causal influences.
        
        Args:
            name: Unique process identifier
            preconditions: Logical preconditions for process activation (e.g., "heat_source_present")
            quantity_conditions: Constraints on quantity values (e.g., "temperature > 0")
            influences: Causal influences on quantities (e.g., "I+(temperature)", "I-(pressure)")
            
        Returns:
            QualitativeProcess: The created process object
            
        Example:
            >>> engine.add_process(
            ...     "heating",
            ...     preconditions=["heat_source_present", "contact_exists"],
            ...     quantity_conditions=["temperature_difference > 0"],
            ...     influences=["I+(temperature)", "I+(thermal_energy)"]
            ... )
            
        🧠 Process Theory Notes:
        Preconditions capture the structural requirements for process activation,
        while quantity conditions specify the numerical constraints. Influences
        define the causal effects using Forbus's I+ and I- notation.
        """
        
        # Create process object
        process = QualitativeProcess(
            name=name,
            preconditions=preconditions,
            quantity_conditions=quantity_conditions,
            influences=influences,
            active=False
        )
        
        # Store process
        self.processes[name] = process
        
        # Build causal graph - extract influenced quantities
        influenced_quantities = []
        for influence in influences:
            quantity_name = self._parse_influence_target(influence)
            if quantity_name:
                influenced_quantities.append(quantity_name)
                
                # Update quantity->process mapping
                if quantity_name not in self.quantity_process_map:
                    self.quantity_process_map[quantity_name] = set()
                self.quantity_process_map[quantity_name].add(name)
                
        self.causal_graph[name] = influenced_quantities
        
        # Analyze process dependencies (processes that might interact)
        self._analyze_process_dependencies(name)
        
        if hasattr(self, '_verbose') and self._verbose:
            print(f"   Added process: {name}")
            print(f"     Preconditions: {preconditions}")
            print(f"     Quantity conditions: {quantity_conditions}")
            print(f"     Influences: {influences}")
            print(f"     Affects quantities: {influenced_quantities}")
            
        return process
        
    def _parse_influence_target(self, influence: str) -> Optional[str]:
        """
        Parse influence expressions to extract target quantity names
        
        Supports multiple influence formats:
        - "I+(temperature)" -> "temperature"
        - "I-(pressure)" -> "pressure"  
        - "I+(heat_flow, rate=fast)" -> "heat_flow"
        - Future: "I+(temperature, magnitude=large)" -> "temperature"
        
        Args:
            influence: Influence expression string
            
        Returns:
            str or None: Target quantity name, or None if parsing fails
        """
        
        influence = influence.strip()
        
        # Standard format: I+(quantity) or I-(quantity)
        if influence.startswith("I+") or influence.startswith("I-"):
            # Extract quantity name between parentheses
            if "(" in influence and ")" in influence:
                start = influence.index("(") + 1
                end = influence.index(")")
                content = influence[start:end].strip()
                
                # Handle parameters: "quantity, param=value"
                if "," in content:
                    quantity_name = content.split(",")[0].strip()
                else:
                    quantity_name = content
                    
                return quantity_name if quantity_name else None
            else:
                # Format without parentheses: I+temperature
                return influence[2:].strip() if len(influence) > 2 else None
                
        return None
        
    def _analyze_process_dependencies(self, process_name: str):
        """
        Analyze dependencies between processes for interaction detection
        
        This method identifies potential process interactions by analyzing:
        1. Shared quantity influences (competing processes)
        2. Causal chains (output of one process affects another)
        3. Precondition dependencies (one process enables another)
        
        Args:
            process_name: Name of process to analyze dependencies for
        """
        
        process = self.processes[process_name]
        dependencies = set()
        
        # Find processes that influence quantities in our preconditions
        for precondition in process.preconditions:
            # Extract quantity names from preconditions
            for other_name, other_process in self.processes.items():
                if other_name != process_name:
                    for influence in other_process.influences:
                        target_qty = self._parse_influence_target(influence)
                        if target_qty and target_qty in precondition:
                            dependencies.add(other_name)
                            
        # Find processes that influence the same quantities (potential conflicts)
        our_influences = {self._parse_influence_target(inf) for inf in process.influences}
        our_influences.discard(None)
        
        for other_name, other_influences in self.causal_graph.items():
            if other_name != process_name:
                if our_influences.intersection(set(other_influences)):
                    dependencies.add(other_name)
                    
        self.process_dependencies[process_name] = dependencies
        
    def evaluate_process_conditions(self, process: QualitativeProcess) -> bool:
        """
        Evaluate whether a process should be active based on its conditions
        
        This implements the core process activation logic from Process Theory:
        A process is active iff its preconditions AND quantity conditions are satisfied.
        
        Args:
            process: The process to evaluate
            
        Returns:
            bool: True if process should be active, False otherwise
            
        🧠 Process Theory:
        Process activation is the central mechanism in Forbus's theory. A process
        can only influence quantities when it is active, and activation requires
        both structural preconditions (preconditions) and numerical constraints
        (quantity_conditions) to be satisfied simultaneously.
        """
        
        # Evaluate structural preconditions
        for precondition in process.preconditions:
            if not self._evaluate_logical_expression(precondition):
                return False
                
        # Evaluate quantity conditions  
        for condition in process.quantity_conditions:
            if not self._evaluate_quantity_condition(condition):
                return False
                
        return True
        
    def _evaluate_quantity_condition(self, condition: str) -> bool:
        """
        Evaluate quantity-specific conditions using qualitative comparisons
        
        This method handles qualitative constraint evaluation for process activation.
        It supports various comparison formats and qualitative value reasoning.
        
        Args:
            condition: Quantity condition string (e.g., "temperature > 0")
            
        Returns:
            bool: True if condition is satisfied, False otherwise
            
        Supported Formats:
        - "quantity > 0", "quantity < 0", "quantity = 0"
        - "quantity != 0" 
        - "quantity > quantity2"
        - "quantity positive", "quantity negative", "quantity zero"
        """
        
        condition = condition.strip()
        
        # Handle inequality conditions
        if "!=" in condition:
            parts = condition.split("!=")
            if len(parts) == 2:
                qty_name = parts[0].strip()
                value = parts[1].strip()
                
                if qty_name in self.quantities:
                    qty = self.quantities[qty_name]
                    if value == "0":
                        return qty.magnitude != QualitativeValue.ZERO
                    # Handle other value comparisons
                    other_val = self._parse_qualitative_value(value)
                    if other_val:
                        return qty.magnitude != other_val
                        
        # Handle positive/negative conditions
        elif " > 0" in condition:
            qty_name = condition.replace(" > 0", "").strip()
            if qty_name in self.quantities:
                qty = self.quantities[qty_name]
                return self._is_positive(qty.magnitude)
                
        elif " < 0" in condition:
            qty_name = condition.replace(" < 0", "").strip()
            if qty_name in self.quantities:
                qty = self.quantities[qty_name]
                return self._is_negative(qty.magnitude)
                
        elif " = 0" in condition or " == 0" in condition:
            qty_name = condition.replace(" = 0", "").replace(" == 0", "").strip()
            if qty_name in self.quantities:
                qty = self.quantities[qty_name]
                return qty.magnitude == QualitativeValue.ZERO
                
        # Handle qualitative comparisons between quantities
        elif " > " in condition:
            parts = condition.split(" > ")
            if len(parts) == 2:
                left_qty = parts[0].strip()
                right_qty = parts[1].strip()
                return self._compare_quantities(left_qty, right_qty, ">")
                
        elif " < " in condition:
            parts = condition.split(" < ")
            if len(parts) == 2:
                left_qty = parts[0].strip()
                right_qty = parts[1].strip()
                return self._compare_quantities(left_qty, right_qty, "<")
                
        # Handle qualitative state conditions
        elif " positive" in condition.lower():
            qty_name = condition.lower().replace(" positive", "").strip()
            if qty_name in self.quantities:
                qty = self.quantities[qty_name]
                return self._is_positive(qty.magnitude)
                
        elif " negative" in condition.lower():
            qty_name = condition.lower().replace(" negative", "").strip()
            if qty_name in self.quantities:
                qty = self.quantities[qty_name]
                return self._is_negative(qty.magnitude)
                
        # Default: assume condition is satisfied (conservative for demo)
        return True
        
    def _is_positive(self, magnitude: QualitativeValue) -> bool:
        """Check if qualitative value is positive"""
        positive_values = {
            QualitativeValue.POSITIVE_SMALL,
            QualitativeValue.POSITIVE_LARGE, 
            QualitativeValue.POSITIVE_INFINITY,
            QualitativeValue.INCREASING,
            QualitativeValue.INCREASING_LARGE
        }
        return magnitude in positive_values
        
    def _is_negative(self, magnitude: QualitativeValue) -> bool:
        """Check if qualitative value is negative"""
        negative_values = {
            QualitativeValue.NEGATIVE_SMALL,
            QualitativeValue.NEGATIVE_LARGE,
            QualitativeValue.NEGATIVE_INFINITY,
            QualitativeValue.DECREASING,
            QualitativeValue.DECREASING_LARGE
        }
        return magnitude in negative_values
        
    def _compare_quantities(self, left_name: str, right_name: str, operator: str) -> bool:
        """Compare two quantities qualitatively"""
        
        if left_name not in self.quantities or right_name not in self.quantities:
            return False
            
        left_qty = self.quantities[left_name]
        right_qty = self.quantities[right_name]
        
        # Get ordering values for comparison
        ordering = QualitativeValue.get_ordering()
        left_order = ordering.get(left_qty.magnitude, 0)
        right_order = ordering.get(right_qty.magnitude, 0)
        
        if operator == ">":
            return left_order > right_order
        elif operator == "<":
            return left_order < right_order
        elif operator == "=":
            return left_order == right_order
            
        return False
        
    def _parse_qualitative_value(self, value_str: str) -> Optional[QualitativeValue]:
        """Parse string representations into QualitativeValue enum"""
        
        value_str = value_str.lower().strip()
        
        # Direct enum value mapping
        value_mapping = {
            '0': QualitativeValue.ZERO,
            'zero': QualitativeValue.ZERO,
            'positive': QualitativeValue.POSITIVE_SMALL,
            'negative': QualitativeValue.NEGATIVE_SMALL,
            'pos': QualitativeValue.POSITIVE_SMALL,
            'neg': QualitativeValue.NEGATIVE_SMALL,
            'large': QualitativeValue.POSITIVE_LARGE,
            'small': QualitativeValue.POSITIVE_SMALL,
            'infinity': QualitativeValue.POSITIVE_INFINITY,
            'inf': QualitativeValue.POSITIVE_INFINITY,
        }
        
        return value_mapping.get(value_str, None)
        
    def update_active_processes(self) -> List[str]:
        """
        Update which processes are currently active based on current system state
        
        This implements the process activation cycle from Process Theory:
        1. Evaluate each process's activation conditions
        2. Track activation state changes
        3. Record process activation history
        4. Return list of currently active processes
        
        Returns:
            List[str]: Names of currently active processes
            
        🧠 Process Theory:
        Process activation is dynamic - processes can become active or inactive
        as system conditions change. This creates the temporal dynamics that
        drive qualitative simulation and behavioral prediction.
        """
        
        active_processes = []
        activation_changes = []
        current_time = len(self.process_history)  # Simple time counter
        
        for process_name, process in self.processes.items():
            was_active = process.active
            
            # Evaluate current activation conditions
            process.active = self.evaluate_process_conditions(process)
            
            if process.active:
                active_processes.append(process_name)
                
            # Track activation changes
            if process.active != was_active:
                status = "ACTIVATED" if process.active else "DEACTIVATED"
                activation_changes.append((process_name, status))
                
                # Record in activation history
                self.activation_changes.append((f"t_{current_time}", process_name, process.active))
                
                if hasattr(self, '_verbose') and self._verbose:
                    print(f"   Process {process_name}: {status}")
                    
        # Store activation state snapshot
        current_activation_state = {name: proc.active for name, proc in self.processes.items()}
        self.process_history.append(current_activation_state)
        
        return active_processes
        
    def apply_process_influences(self, active_processes: List[str]):
        """
        Apply influences from active processes to quantity derivatives
        
        This implements the core causal mechanism from Process Theory:
        Active processes influence quantities through I+ and I- relations,
        which are combined to determine the net qualitative derivative.
        
        Args:
            active_processes: List of currently active process names
            
        🧠 Process Theory:
        Influences represent the causal effects of processes on quantities.
        Multiple processes can influence the same quantity, requiring influence
        combination rules. The net influence determines the quantity's derivative.
        
        Influence Combination Rules:
        - I+ contributes +1 to net influence
        - I- contributes -1 to net influence  
        - Net > 0: quantity direction becomes INCREASING
        - Net < 0: quantity direction becomes DECREASING
        - Net = 0: quantity direction becomes STEADY
        """
        
        # Collect all influences on each quantity
        quantity_influences = {}  # quantity_name -> [influence_effects]
        influence_sources = {}    # quantity_name -> [(process_name, influence_type)]
        
        for process_name in active_processes:
            process = self.processes[process_name]
            
            for influence in process.influences:
                quantity_name = self._parse_influence_target(influence)
                if quantity_name and quantity_name in self.quantities:
                    
                    # Initialize tracking structures
                    if quantity_name not in quantity_influences:
                        quantity_influences[quantity_name] = []
                        influence_sources[quantity_name] = []
                        
                    # Determine influence type and strength
                    if influence.startswith("I+"):
                        influence_type = "increase"
                        influence_strength = self._parse_influence_strength(influence)
                        quantity_influences[quantity_name].extend(["increase"] * influence_strength)
                        
                    elif influence.startswith("I-"):
                        influence_type = "decrease" 
                        influence_strength = self._parse_influence_strength(influence)
                        quantity_influences[quantity_name].extend(["decrease"] * influence_strength)
                        
                    # Track influence sources for explanation
                    influence_sources[quantity_name].append((process_name, influence_type))
                    
        # Apply net influences to quantity derivatives
        for quantity_name, influences in quantity_influences.items():
            if quantity_name in self.quantities:
                qty = self.quantities[quantity_name]
                
                # Calculate net influence
                increase_count = influences.count("increase")
                decrease_count = influences.count("decrease")
                net_influence = increase_count - decrease_count
                
                # Store previous direction for change detection
                previous_direction = qty.direction
                
                # Update qualitative derivative (direction)
                if net_influence > 0:
                    qty.direction = QualitativeDirection.INCREASING
                elif net_influence < 0:
                    qty.direction = QualitativeDirection.DECREASING
                else:
                    qty.direction = QualitativeDirection.STEADY
                    
                # Track direction changes
                if qty.direction != previous_direction and hasattr(self, '_verbose') and self._verbose:
                    print(f"   {quantity_name}: direction = {qty.direction.value}")
                    print(f"     Net influence: {net_influence} (↑{increase_count}, ↓{decrease_count})")
                    print(f"     Sources: {influence_sources.get(quantity_name, [])}")
                    
    def _parse_influence_strength(self, influence: str) -> int:
        """
        Parse influence strength from influence expressions
        
        Future enhancement: Support parameterized influences like:
        - "I+(temperature, strength=strong)" -> strength 2
        - "I-(pressure, rate=slow)" -> strength 1
        
        Args:
            influence: Influence expression
            
        Returns:
            int: Influence strength (default: 1)
        """
        
        # For now, all influences have strength 1
        # Future: parse strength parameters from influence string
        return 1
        
    def explain_behavior(self, quantity_name: str) -> List[str]:
        """
        Generate causal explanation for quantity behavior using process chains
        
        This implements behavioral explanation from Process Theory by tracing
        the causal chain from active processes to quantity changes.
        
        Args:
            quantity_name: Name of quantity to explain
            
        Returns:
            List[str]: Explanation sentences describing causal chain
            
        Example:
            >>> explanations = engine.explain_behavior("temperature")
            >>> for explanation in explanations:
            ...     print(explanation)
            "temperature is being influenced by processes: ['heating']"
            "Process 'heating' is active because:"
            "  - heat_source_present"
            "  - temperature_difference > 0"
            "Current state: positive, trending increasing"
            
        🧠 Process Theory:
        Causal explanation in Process Theory traces the activation of processes
        and their influences on quantities. This provides human-understandable
        explanations for system behavior grounded in causal mechanisms.
        """
        
        explanations = []
        
        if quantity_name not in self.quantities:
            return [f"Quantity '{quantity_name}' not found in system"]
            
        qty = self.quantities[quantity_name]
        
        # Find active processes that influence this quantity
        influencing_processes = []
        for process_name, influenced_quantities in self.causal_graph.items():
            if quantity_name in influenced_quantities:
                process = self.processes[process_name]
                if process.active:
                    influencing_processes.append(process_name)
                    
        # Generate explanation
        if not influencing_processes:
            explanations.append(f"{quantity_name} is not being influenced by any active processes")
            
            # Check for inactive processes that could influence it
            potential_processes = []
            for process_name, influenced_quantities in self.causal_graph.items():
                if quantity_name in influenced_quantities:
                    process = self.processes[process_name]
                    if not process.active:
                        potential_processes.append(process_name)
                        
            if potential_processes:
                explanations.append(f"Potential influencing processes (currently inactive): {potential_processes}")
                
        else:
            explanations.append(f"{quantity_name} is being influenced by processes: {influencing_processes}")
            
            # Explain each influencing process
            for process_name in influencing_processes:
                process = self.processes[process_name]
                explanations.append(f"Process '{process_name}' is active because:")
                
                # List preconditions
                for precondition in process.preconditions:
                    explanations.append(f"  - {precondition}")
                    
                # List quantity conditions  
                for condition in process.quantity_conditions:
                    explanations.append(f"  - {condition}")
                    
                # Show influences from this process
                process_influences = [inf for inf in process.influences 
                                    if self._parse_influence_target(inf) == quantity_name]
                if process_influences:
                    explanations.append(f"  - Influences: {process_influences}")
                    
        # Current quantity state
        explanations.append(f"Current state: {qty.magnitude.value}, trending {qty.direction.value}")
        
        # Historical context if available
        if len(self.process_history) > 1:
            explanations.append(f"Process activation history: {len(self.process_history)} time steps recorded")
            
        return explanations
        
    def get_causal_chain(self, quantity_name: str) -> Dict[str, Any]:
        """
        Get detailed causal chain structure for a quantity
        
        This method returns a structured representation of the causal influences
        affecting a quantity, suitable for visualization or further analysis.
        
        Args:
            quantity_name: Name of quantity to analyze
            
        Returns:
            Dict containing causal chain structure:
            {
                'target_quantity': str,
                'direct_influences': [{'process': str, 'influence': str, 'type': str}],
                'active_processes': [str],
                'inactive_processes': [str], 
                'process_dependencies': {process: [dependencies]},
                'causal_depth': int
            }
        """
        
        if quantity_name not in self.quantities:
            return {'error': f"Quantity '{quantity_name}' not found"}
            
        causal_chain = {
            'target_quantity': quantity_name,
            'direct_influences': [],
            'active_processes': [],
            'inactive_processes': [],
            'process_dependencies': {},
            'causal_depth': 0
        }
        
        # Find all processes that can influence this quantity
        for process_name, influenced_quantities in self.causal_graph.items():
            if quantity_name in influenced_quantities:
                process = self.processes[process_name]
                
                # Categorize by activation state
                if process.active:
                    causal_chain['active_processes'].append(process_name)
                else:
                    causal_chain['inactive_processes'].append(process_name)
                    
                # Extract direct influences
                for influence in process.influences:
                    if self._parse_influence_target(influence) == quantity_name:
                        influence_info = {
                            'process': process_name,
                            'influence': influence,
                            'type': 'positive' if influence.startswith('I+') else 'negative',
                            'active': process.active
                        }
                        causal_chain['direct_influences'].append(influence_info)
                        
                # Include process dependencies
                if process_name in self.process_dependencies:
                    causal_chain['process_dependencies'][process_name] = list(self.process_dependencies[process_name])
                    
        # Calculate causal depth (maximum dependency chain length)
        max_depth = 0
        for process_name in causal_chain['active_processes']:
            depth = self._calculate_dependency_depth(process_name, set())
            max_depth = max(max_depth, depth)
        causal_chain['causal_depth'] = max_depth
        
        return causal_chain
        
    def _calculate_dependency_depth(self, process_name: str, visited: Set[str]) -> int:
        """Calculate maximum dependency chain depth for a process"""
        
        if process_name in visited:
            return 0  # Avoid cycles
            
        visited.add(process_name)
        dependencies = self.process_dependencies.get(process_name, set())
        
        if not dependencies:
            return 1
            
        max_depth = 0
        for dep_process in dependencies:
            depth = self._calculate_dependency_depth(dep_process, visited.copy())
            max_depth = max(max_depth, depth)
            
        return max_depth + 1
        
    def get_process_interactions(self) -> Dict[str, Any]:
        """
        Analyze interactions between processes in the system
        
        Returns comprehensive analysis of how processes interact:
        - Competing processes (influence same quantities)
        - Cooperative processes (enable each other)
        - Process cycles and feedback loops
        - Potential conflicts and their resolution
        
        Returns:
            Dict containing interaction analysis results
        """
        
        interactions = {
            'competing_processes': [],      # Processes influencing same quantities
            'cooperative_processes': [],    # Processes enabling each other
            'process_cycles': [],          # Circular dependencies
            'influence_conflicts': [],      # Opposing influences on same quantity
            'interaction_matrix': {}       # Process-to-process interaction strengths
        }
        
        # Find competing processes (same quantity influences)
        quantity_influencers = {}  # quantity -> [processes]
        for process_name, influenced_qtys in self.causal_graph.items():
            for qty in influenced_qtys:
                if qty not in quantity_influencers:
                    quantity_influencers[qty] = []
                quantity_influencers[qty].append(process_name)
                
        for qty, influencers in quantity_influencers.items():
            if len(influencers) > 1:
                # Check if influences are conflicting (I+ vs I-)
                pos_influences = []
                neg_influences = []
                
                for proc_name in influencers:
                    process = self.processes[proc_name]
                    for influence in process.influences:
                        if self._parse_influence_target(influence) == qty:
                            if influence.startswith('I+'):
                                pos_influences.append(proc_name)
                            elif influence.startswith('I-'):
                                neg_influences.append(proc_name)
                                
                if pos_influences and neg_influences:
                    interactions['influence_conflicts'].append({
                        'quantity': qty,
                        'positive_processes': pos_influences,
                        'negative_processes': neg_influences
                    })
                    
                interactions['competing_processes'].append({
                    'quantity': qty,
                    'processes': influencers
                })
                
        # Find cooperative processes (dependency relationships)
        for process_name, dependencies in self.process_dependencies.items():
            if dependencies:
                interactions['cooperative_processes'].append({
                    'process': process_name,
                    'enables': list(dependencies)
                })
                
        # Detect process cycles
        cycles = self._detect_process_cycles()
        interactions['process_cycles'] = cycles
        
        return interactions
        
    def _detect_process_cycles(self) -> List[List[str]]:
        """Detect circular dependencies in process network"""
        
        cycles = []
        visited = set()
        
        def dfs_cycle_detection(process: str, path: List[str], rec_stack: Set[str]):
            visited.add(process)
            rec_stack.add(process)
            path.append(process)
            
            dependencies = self.process_dependencies.get(process, set())
            for dep_process in dependencies:
                if dep_process in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(dep_process)
                    cycle = path[cycle_start:] + [dep_process]
                    cycles.append(cycle)
                elif dep_process not in visited:
                    dfs_cycle_detection(dep_process, path.copy(), rec_stack.copy())
            
            rec_stack.remove(process)
            
        for process_name in self.processes:
            if process_name not in visited:
                dfs_cycle_detection(process_name, [], set())
                
        return cycles
        
    def predict_process_evolution(self, n_steps: int = 5) -> List[Dict[str, bool]]:
        """
        Predict how process activation states will evolve over time
        
        Uses current system dynamics to predict future process activation
        patterns based on quantity trends and process dependencies.
        
        Args:
            n_steps: Number of future time steps to predict
            
        Returns:
            List[Dict[str, bool]]: Predicted activation states for each step
            
        🧠 Process Theory:
        Process evolution prediction uses the temporal dynamics inherent in
        Process Theory. As quantities change due to process influences,
        the activation conditions for other processes may be satisfied or
        violated, leading to predictable temporal patterns.
        """
        
        predictions = []
        
        # Save current state
        original_quantities = {name: (qty.magnitude, qty.direction) 
                             for name, qty in self.quantities.items()}
        original_processes = {name: proc.active for name, proc in self.processes.items()}
        
        try:
            for step in range(n_steps):
                # Update active processes
                active_processes = self.update_active_processes()
                
                # Apply influences to update quantity trends
                self.apply_process_influences(active_processes)
                
                # Simulate quantity magnitude changes based on directions
                self._simulate_quantity_evolution()
                
                # Record prediction
                prediction = {name: proc.active for name, proc in self.processes.items()}
                predictions.append(prediction)
                
        finally:
            # Restore original state
            for name, (magnitude, direction) in original_quantities.items():
                if name in self.quantities:
                    self.quantities[name].magnitude = magnitude
                    self.quantities[name].direction = direction
                    
            for name, active_state in original_processes.items():
                if name in self.processes:
                    self.processes[name].active = active_state
                    
        return predictions
        
    def _simulate_quantity_evolution(self):
        """Simulate one step of quantity evolution based on current directions"""
        
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
            QualitativeValue.POSITIVE_INFINITY: QualitativeValue.POSITIVE_INFINITY,  # Stay at max
            QualitativeValue.DECREASING_LARGE: QualitativeValue.DECREASING,
            QualitativeValue.DECREASING: QualitativeValue.ZERO,
            QualitativeValue.INCREASING: QualitativeValue.INCREASING_LARGE,
            QualitativeValue.INCREASING_LARGE: QualitativeValue.POSITIVE_INFINITY
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
            QualitativeValue.NEGATIVE_INFINITY: QualitativeValue.NEGATIVE_INFINITY,  # Stay at min
            QualitativeValue.INCREASING_LARGE: QualitativeValue.INCREASING,
            QualitativeValue.INCREASING: QualitativeValue.ZERO,
            QualitativeValue.DECREASING: QualitativeValue.DECREASING_LARGE,
            QualitativeValue.DECREASING_LARGE: QualitativeValue.NEGATIVE_INFINITY
        }
        
        return transitions.get(current, current)
        
    def visualize_process_network(self) -> Dict[str, Any]:
        """
        Create visualization-ready representation of the process network
        
        Returns network structure suitable for graph visualization libraries
        or ASCII art rendering.
        
        Returns:
            Dict containing nodes, edges, and layout information
        """
        
        network = {
            'nodes': [],
            'edges': [],
            'clusters': {},  # Group related processes
            'layout_hints': {}
        }
        
        # Add process nodes
        for process_name, process in self.processes.items():
            node = {
                'id': process_name,
                'type': 'process',
                'label': process_name,
                'active': process.active,
                'preconditions': len(process.preconditions),
                'influences': len(process.influences)
            }
            network['nodes'].append(node)
            
        # Add quantity nodes
        for qty_name in self.quantities:
            node = {
                'id': qty_name,
                'type': 'quantity',
                'label': qty_name,
                'magnitude': self.quantities[qty_name].magnitude.value,
                'direction': self.quantities[qty_name].direction.value
            }
            network['nodes'].append(node)
            
        # Add influence edges
        for process_name, influenced_quantities in self.causal_graph.items():
            for qty_name in influenced_quantities:
                # Determine influence type
                process = self.processes[process_name]
                influence_type = 'unknown'
                for influence in process.influences:
                    if self._parse_influence_target(influence) == qty_name:
                        influence_type = 'positive' if influence.startswith('I+') else 'negative'
                        break
                        
                edge = {
                    'source': process_name,
                    'target': qty_name,
                    'type': 'influence',
                    'influence_type': influence_type,
                    'active': process.active
                }
                network['edges'].append(edge)
                
        # Add dependency edges
        for process_name, dependencies in self.process_dependencies.items():
            for dep_process in dependencies:
                edge = {
                    'source': dep_process,
                    'target': process_name,
                    'type': 'dependency',
                    'active': (self.processes[dep_process].active and 
                             self.processes[process_name].active)
                }
                network['edges'].append(edge)
                
        return network
        
    def get_process_statistics(self) -> Dict[str, Any]:
        """
        Generate comprehensive statistics about the process system
        
        Returns:
            Dict containing various process system metrics
        """
        
        stats = {
            'process_count': len(self.processes),
            'quantity_count': len(self.quantities),
            'active_process_count': sum(1 for p in self.processes.values() if p.active),
            'total_influences': sum(len(p.influences) for p in self.processes.values()),
            'causal_connections': sum(len(influenced) for influenced in self.causal_graph.values()),
            'process_dependencies': len(self.process_dependencies),
            'average_influences_per_process': 0,
            'process_activation_rate': 0,
            'causal_complexity': 0
        }
        
        if stats['process_count'] > 0:
            stats['average_influences_per_process'] = stats['total_influences'] / stats['process_count']
            stats['process_activation_rate'] = stats['active_process_count'] / stats['process_count']
            
        # Calculate causal complexity (based on interaction density)
        total_possible_connections = stats['process_count'] * len(self.quantities)
        if total_possible_connections > 0:
            stats['causal_complexity'] = stats['causal_connections'] / total_possible_connections
            
        # Process activation history statistics
        if self.process_history:
            stats['simulation_steps'] = len(self.process_history)
            stats['activation_changes'] = len(self.activation_changes)
            
            # Calculate activation stability
            if len(self.process_history) > 1:
                changes_per_step = len(self.activation_changes) / (len(self.process_history) - 1)
                stats['activation_stability'] = 1.0 - min(changes_per_step, 1.0)
            else:
                stats['activation_stability'] = 1.0
                
        return stats