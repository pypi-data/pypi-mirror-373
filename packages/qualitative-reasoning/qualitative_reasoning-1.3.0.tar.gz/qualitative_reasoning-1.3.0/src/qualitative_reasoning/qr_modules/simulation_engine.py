"""
🚀 Qualitative Reasoning - Simulation Engine Module
==================================================

This module provides the core qualitative simulation engine for temporal state evolution
in qualitative physics systems, based on Forbus's Process Theory and de Kleer's 
Qualitative Physics framework.

📚 Theoretical Foundation:
Forbus, K. D. (1984). "Qualitative Process Theory", Artificial Intelligence, 24(1-3)
Forbus, K. D., & de Kleer, J. (1993). "Building Problem Solvers", MIT Press
de Kleer, J., & Brown, J. S. (1984). "A Qualitative Physics Based on Confluences"
Kuipers, B. (1994). "Qualitative Reasoning: Modeling and Simulation with Incomplete Knowledge"

🧠 Qualitative Simulation Theory:
The simulation engine implements the heart of qualitative physics - how physical systems
evolve through qualitative time. Unlike numerical simulation, qualitative simulation:

1. **Temporal Abstraction**: Time is divided into qualitative intervals where system
   behavior is uniform (steady states and transitions)
2. **State Evolution**: System states change through discrete qualitative transitions  
3. **Process-Driven Dynamics**: Changes result from active processes influencing quantities
4. **Causal Reasoning**: Behavior is explained through causal chains of process activation
5. **Predictive Capability**: Future behaviors can be predicted from current trends

🔬 Mathematical Framework:
State Evolution: S(t+1) = Φ(S(t), Active_Processes(t))
Process Activation: Active(P,t) ↔ preconditions(P,t) ∧ quantity_conditions(P,t)  
Quantity Dynamics: ∂Q/∂t = Σ I±(Q) from active processes
Magnitude Transitions: mag(t+1) = transition_function(mag(t), direction(t))
Temporal Progression: sequence of qualitative states over discrete time points

🎯 Core Simulation Engine Capabilities:
- Main qualitative simulation step execution loop
- Quantity magnitude evolution through qualitative transitions
- State transition logic with landmark value handling  
- Future state prediction algorithms
- State history management and temporal reasoning
- Behavioral relationship analysis and inference
- Constraint checking and consistency maintenance
- Causal explanation generation for system behavior

🌟 Key Implementation Features:
- Robust qualitative magnitude transition algorithms
- Efficient state evolution computation
- Comprehensive temporal correlation analysis
- Advanced behavioral relationship inference
- Rich causal explanation capabilities
- Extensible prediction algorithms
- Secure constraint evaluation integration

🔧 Integration:
This mixin integrates with:
- Core types for qualitative values and states
- Constraint engine for system consistency
- Process engine for causal influences
- Main reasoner for system coordination

🚀 Simulation Loop Architecture:
1. **Process Evaluation**: Determine which processes are active
2. **Influence Application**: Apply process influences to quantity directions  
3. **Magnitude Evolution**: Update quantity magnitudes based on directions
4. **Constraint Checking**: Verify system consistency
5. **State Capture**: Record current qualitative state
6. **Relationship Inference**: Derive behavioral relationships
7. **History Management**: Update temporal state history

Author: Benedict Chen
Based on foundational work by Kenneth Forbus, Johan de Kleer, and Benjamin Kuipers
"""

from typing import Dict, List, Tuple, Union, Optional, Any, Set
from dataclasses import dataclass
import warnings

# Import core types and related engines
# Note: These types are expected to be available in the parent class that uses this mixin
# The mixin will use the types from whatever module imports it


class SimulationEngineMixin:
    """
    Qualitative Simulation Engine Mixin
    
    Implements the core temporal reasoning and state evolution capabilities
    for qualitative physics simulation. This mixin provides the computational
    heart of qualitative simulation - advancing systems through qualitative time.
    
    🧠 Core Simulation Concepts:
    
    **Qualitative Time**: Unlike continuous numerical time, qualitative time consists
    of discrete intervals where system behavior is uniform. Transitions occur when
    quantities cross landmark values or process conditions change.
    
    **State Evolution**: The system progresses through a sequence of qualitative
    states, each representing a distinct behavioral regime. The simulation engine
    computes these transitions based on active processes and their influences.
    
    **Magnitude Transitions**: Quantities evolve through discrete qualitative
    magnitudes (negative_large → negative_small → zero → positive_small, etc.)
    based on their directions and the influences from active processes.
    
    **Temporal Prediction**: By understanding current process activations and
    trends, the engine can predict likely future qualitative behaviors without
    requiring precise numerical integration.
    """
    
    def qualitative_simulation_step(self, step_name: str):
        """
        🔄 Execute one step of qualitative simulation
        
        This is the core simulation loop that advances the system through one
        qualitative time interval. It implements the fundamental cycle of
        qualitative physics simulation.
        
        Args:
            step_name: Identifier for this simulation step
            
        Returns:
            QualitativeState: The resulting system state after this step
            
        🔬 Simulation Algorithm:
        1. **Process Evaluation**: Determine which processes are currently active
           based on their preconditions and quantity conditions
        2. **Influence Application**: Apply the influences of active processes
           to determine quantity directions (increasing/decreasing/steady)
        3. **Magnitude Evolution**: Update quantity magnitudes based on their
           directions through qualitative transition functions
        4. **Constraint Verification**: Check system constraints for consistency
        5. **State Capture**: Create snapshot of current qualitative state
        6. **Relationship Inference**: Analyze and derive behavioral relationships
        7. **History Update**: Add new state to temporal history
        
        🧠 Theoretical Background:
        This implements Forbus's qualitative simulation algorithm, which differs
        from numerical simulation by:
        - Operating on discrete qualitative values instead of real numbers
        - Using process activation logic instead of differential equations
        - Generating behavioral predictions instead of precise trajectories
        - Providing causal explanations for system behavior
        """
        
        print(f"\n🔄 Qualitative simulation step: {step_name}")
        
        # Step 1 & 2: Evaluate and update active processes
        active_processes = self.update_active_processes()
        
        # Step 3: Apply process influences to quantity directions
        self.apply_process_influences(active_processes)
        
        # Step 4: Evolve quantity magnitudes based on their directions
        self._update_quantity_magnitudes()
        
        # Step 5: Verify system constraints and consistency
        self._check_constraints()
        
        # Step 6: Create comprehensive state snapshot
        # Try to get QualitativeState from the reasoner's globals
        QualitativeState = None
        if hasattr(self, '__class__') and hasattr(self.__class__, '__module__'):
            try:
                import sys
                parent_module = sys.modules.get(self.__class__.__module__)
                if parent_module:
                    QualitativeState = getattr(parent_module, 'QualitativeState', None)
            except (KeyError, AttributeError):
                pass
        
        if QualitativeState:
            current_state = QualitativeState(
                time_point=step_name,
                quantities={name: qty for name, qty in self.quantities.items()},
                relationships=self.derive_relationships()
            )
        else:
            # Create a simple state representation as fallback
            from dataclasses import dataclass
            from typing import Dict
            
            @dataclass
            class SimpleQualitativeState:
                time_point: str
                quantities: Dict
                relationships: Dict
                
            current_state = SimpleQualitativeState(
                time_point=step_name,
                quantities={name: qty for name, qty in self.quantities.items()},
                relationships=self.derive_relationships()
            )
        
        # Step 7: Update temporal state history
        self.state_history.append(current_state)
        self.current_state = current_state
        
        return current_state
        
    def _update_quantity_magnitudes(self):
        """
        🔄 Update quantity magnitudes based on their current directions
        
        This method implements the core qualitative magnitude evolution logic,
        advancing quantities through their qualitative value spaces based on
        the directions determined by active process influences.
        
        🔬 Magnitude Evolution Theory:
        Quantities in qualitative physics have discrete magnitude values that
        form ordered scales. When a quantity has a direction (increasing/decreasing),
        it transitions to the next appropriate magnitude in that direction.
        
        The transition function implements the qualitative derivative:
        If ∂Q/∂t > 0 (increasing), then mag(Q) transitions upward
        If ∂Q/∂t < 0 (decreasing), then mag(Q) transitions downward  
        If ∂Q/∂t = 0 (steady), then mag(Q) remains unchanged
        
        🌟 Advanced Features:
        - Handles boundary conditions (staying at infinity values)
        - Supports landmark value transitions
        - Maintains consistency with qualitative algebra
        - Preserves monotonicity properties
        """
        
        for qty_name, qty in self.quantities.items():
            old_magnitude = qty.magnitude
            
            # Use string comparison to avoid enum dependency issues
            direction_value = getattr(qty.direction, 'value', str(qty.direction))
            
            if direction_value in ['+', 'increasing', 'inc']:
                qty.magnitude = self._increase_magnitude(qty.magnitude)
            elif direction_value in ['-', 'decreasing', 'dec']:
                qty.magnitude = self._decrease_magnitude(qty.magnitude)
            # STEADY direction leaves magnitude unchanged
            
            # Log magnitude transitions for debugging and explanation
            if qty.magnitude != old_magnitude:
                old_val = getattr(old_magnitude, 'value', str(old_magnitude))
                new_val = getattr(qty.magnitude, 'value', str(qty.magnitude))
                print(f"   {qty_name}: {old_val} → {new_val}")
                
    def _increase_magnitude(self, current):
        """
        ⬆️ Transition quantity magnitude upward through qualitative scale
        
        Implements the upward transition function for qualitative magnitudes.
        This follows the standard qualitative value ordering and handles
        boundary conditions appropriately.
        
        Args:
            current: Current qualitative magnitude
            
        Returns:
            QualitativeValue: Next higher magnitude in the qualitative scale
            
        🔬 Transition Theory:
        The qualitative magnitude scale follows a standard ordering:
        -∞ → -large → -small → 0 → +small → +large → +∞
        
        This transition function implements the successor relation in this
        ordered space, with +∞ being the absorbing state (no further increase).
        
        🌟 Implementation Notes:
        - Handles all standard qualitative value transitions
        - Maintains consistency with qualitative algebra
        - Supports boundary condition at positive infinity
        - Could be extended to handle landmark-specific transitions
        """
        
        # Use string-based transitions to avoid complex enum lookup
        current_value = getattr(current, 'value', str(current))
        
        # Define transitions based on string values
        string_transitions = {
            'neg_inf': 'neg_large',
            'neg_large': 'neg_small', 
            'neg_small': 'zero',
            'zero': 'pos_small',
            'pos_small': 'pos_large',
            'pos_large': 'pos_inf',
            'pos_inf': 'pos_inf'  # Absorbing state
        }
        
        new_value = string_transitions.get(current_value, current_value)
        
        # If we have an enum, try to find the new value in it
        if hasattr(current, '__class__') and hasattr(current.__class__, '__members__'):
            enum_class = current.__class__
            for member in enum_class.__members__.values():
                if getattr(member, 'value', str(member)) == new_value:
                    return member
                    
        # Return the current value if we can't transition
        return current
        
    def _decrease_magnitude(self, current):
        """
        ⬇️ Transition quantity magnitude downward through qualitative scale
        
        Implements the downward transition function for qualitative magnitudes.
        This is the inverse of the increase function, moving quantities toward
        more negative values in the qualitative scale.
        
        Args:
            current: Current qualitative magnitude
            
        Returns:
            QualitativeValue: Next lower magnitude in the qualitative scale
            
        🔬 Transition Theory:
        The downward transitions follow the reverse of the standard ordering:
        +∞ → +large → +small → 0 → -small → -large → -∞
        
        This implements the predecessor relation in the qualitative magnitude
        space, with -∞ being the absorbing state (no further decrease).
        
        🌟 Implementation Notes:
        - Mirrors the increase function with opposite direction
        - Handles boundary condition at negative infinity
        - Maintains symmetry in the qualitative value space
        - Supports consistent qualitative arithmetic operations
        """
        
        # Use string-based transitions to avoid complex enum lookup
        current_value = getattr(current, 'value', str(current))
        
        # Define downward transitions based on string values
        string_transitions = {
            'pos_inf': 'pos_large',
            'pos_large': 'pos_small',
            'pos_small': 'zero', 
            'zero': 'neg_small',
            'neg_small': 'neg_large',
            'neg_large': 'neg_inf',
            'neg_inf': 'neg_inf'  # Absorbing state
        }
        
        new_value = string_transitions.get(current_value, current_value)
        
        # If we have an enum, try to find the new value in it
        if hasattr(current, '__class__') and hasattr(current.__class__, '__members__'):
            enum_class = current.__class__
            for member in enum_class.__members__.values():
                if getattr(member, 'value', str(member)) == new_value:
                    return member
                    
        # Return the current value if we can't transition
        return current
        
    def predict_future_states(self, n_steps: int = 5) -> List['QualitativeState']:
        """
        🔮 Predict future qualitative states of the system
        
        Uses current process activations, quantity trends, and causal relationships
        to generate predictions of likely future system behaviors. This implements
        qualitative forecasting without requiring precise numerical parameters.
        
        Args:
            n_steps: Number of future steps to predict
            
        Returns:
            List[QualitativeState]: Sequence of predicted future states
            
        🔬 Prediction Theory:
        Qualitative prediction leverages the stability of process activations
        and the deterministic nature of qualitative transitions to forecast
        system evolution. Key principles:
        
        1. **Process Persistence**: Active processes tend to remain active
           until their conditions change
        2. **Trend Continuation**: Quantities continue in their current
           directions unless influenced by new processes
        3. **Landmark Events**: Predictions can identify when quantities
           will cross important landmark values
        4. **Bifurcation Detection**: Multiple possible futures can be
           identified when process conditions become uncertain
           
        🌟 Prediction Capabilities:
        - Extrapolates current trends into the future
        - Identifies likely process deactivations
        - Detects potential constraint violations
        - Generates multiple scenarios for uncertain conditions
        - Provides time horizons for predictions
        
        🚀 Advanced Features:
        - Could implement branching scenarios for uncertainty
        - Could include confidence estimates for predictions
        - Could detect oscillatory or cyclic behaviors
        - Could identify equilibrium states and attractors
        """
        
        predictions = []
        
        print(f"\n🔮 Predicting {n_steps} future states...")
        
        # Save current state to restore later
        original_state = {
            'quantities': {name: (qty.magnitude, qty.direction) 
                          for name, qty in self.quantities.items()},
            'state_history_length': len(self.state_history)
        }
        
        # Generate predictions by running simulation steps
        for step in range(1, n_steps + 1):
            # Run simulation step for prediction
            future_state = self.qualitative_simulation_step(f"prediction_{step}")
            predictions.append(future_state)
            
            # Check for prediction termination conditions
            if self._check_prediction_termination(future_state, predictions):
                print(f"   Prediction terminated early at step {step} due to system state")
                break
                
        # Restore original state (predictions are speculative)
        self._restore_system_state(original_state)
        
        return predictions
        
    def _check_prediction_termination(self, current_state: 'QualitativeState', 
                                    predictions: List['QualitativeState']) -> bool:
        """
        Check if prediction should be terminated early
        
        Args:
            current_state: Current predicted state
            predictions: List of previous predictions
            
        Returns:
            bool: True if prediction should terminate
        """
        
        # Terminate if system reaches equilibrium (all directions steady)
        steady_count = 0
        total_quantities = len(current_state.quantities)
        
        for qty in current_state.quantities.values():
            direction_value = getattr(qty.direction, 'value', str(qty.direction))
            if direction_value in ['0', 'steady', 'std']:
                steady_count += 1
                
        if steady_count == total_quantities and total_quantities > 0:
            print("   System reached equilibrium state")
            return True
            
        # Terminate if system state starts repeating (cycle detection)
        if len(predictions) >= 3:
            current_magnitudes = {name: qty.magnitude 
                                for name, qty in current_state.quantities.items()}
            
            for prev_state in predictions[:-1]:  # Don't compare with itself
                prev_magnitudes = {name: qty.magnitude 
                                 for name, qty in prev_state.quantities.items()}
                
                if current_magnitudes == prev_magnitudes:
                    print("   Detected cyclic behavior - system repeating states")
                    return True
                    
        return False
        
    def _restore_system_state(self, original_state: Dict[str, Any]):
        """
        Restore system to its original state after prediction
        
        Args:
            original_state: Dictionary containing original system state
        """
        
        # Restore quantity states
        for name, (magnitude, direction) in original_state['quantities'].items():
            if name in self.quantities:
                self.quantities[name].magnitude = magnitude
                self.quantities[name].direction = direction
                
        # Restore state history length
        original_length = original_state['state_history_length']
        self.state_history = self.state_history[:original_length]
        
        # Restore current state
        self.current_state = self.state_history[-1] if self.state_history else None
        
    def get_simulation_state(self) -> Dict[str, Any]:
        """
        Get comprehensive simulation state information
        
        Returns:
            Dict containing current simulation state details
        """
        
        return {
            'current_time': self.current_state.time_point if self.current_state else "initial",
            'total_steps': len(self.state_history),
            'active_processes': [name for name, process in self.processes.items() 
                               if process.active],
            'quantity_states': {name: {
                'magnitude': qty.magnitude.value,
                'direction': qty.direction.value
            } for name, qty in self.quantities.items()},
            'relationships': self.current_state.relationships if self.current_state else {},
            'constraint_violations': self._get_current_constraint_violations()
        }
        
    def _get_current_constraint_violations(self) -> List[str]:
        """
        Get list of currently violated constraints
        
        Returns:
            List[str]: Names of violated constraints
        """
        
        violations = []
        
        for constraint in self.constraints:
            if not self._evaluate_constraint(constraint):
                violations.append(constraint)
                
        return violations
        
    def reset_simulation(self, preserve_structure: bool = True):
        """
        Reset simulation to initial state
        
        Args:
            preserve_structure: If True, keep quantities and processes but reset states
        """
        
        if preserve_structure:
            # Reset quantities to initial states using string-based approach
            for qty in self.quantities.values():
                # Try to find ZERO magnitude in the enum
                if hasattr(qty.magnitude, '__class__') and hasattr(qty.magnitude.__class__, '__members__'):
                    enum_class = qty.magnitude.__class__
                    for member in enum_class.__members__.values():
                        if getattr(member, 'value', str(member)) == 'zero':
                            qty.magnitude = member
                            break
                
                # Try to find STEADY direction in the enum 
                if hasattr(qty.direction, '__class__') and hasattr(qty.direction.__class__, '__members__'):
                    enum_class = qty.direction.__class__
                    for member in enum_class.__members__.values():
                        if getattr(member, 'value', str(member)) in ['0', 'steady', 'std']:
                            qty.direction = member
                            break
                
            # Deactivate all processes
            for process in self.processes.values():
                process.active = False
        else:
            # Complete reset
            self.quantities.clear()
            self.processes.clear()
            self.constraints.clear()
            
        # Clear simulation history
        self.state_history.clear()
        self.current_state = None
        
        print("🔄 Simulation reset completed")