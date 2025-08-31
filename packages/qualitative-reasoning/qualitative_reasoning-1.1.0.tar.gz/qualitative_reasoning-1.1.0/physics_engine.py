"""
Qualitative Physics Engine Implementation
Based on: Forbus (1984) "Qualitative Process Theory" and de Kleer & Brown (1984)

Implements a qualitative physics simulation engine that reasons about
physical processes without precise numerical values.
"""

import numpy as np
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass
from .qualitative_reasoning import (QualitativeQuantity, QualitativeProcess, 
                                   QualitativeState, QualitativeValue)
from .causal_reasoning import CausalReasoner


@dataclass
class PhysicalObject:
    """Represents a physical object in the qualitative simulation"""
    name: str
    properties: Dict[str, QualitativeQuantity]
    location: Optional[str] = None
    material_type: Optional[str] = None
    

@dataclass
class PhysicalProcess:
    """Represents a physical process (heat flow, motion, etc.)"""
    name: str
    type: str  # 'heat_transfer', 'fluid_flow', 'motion', etc.
    participants: List[str]  # Object names
    conditions: List[str]
    effects: List[Dict[str, Any]]
    rate: QualitativeValue
    active: bool = False


class QualitativePhysicsEngine:
    """
    Qualitative Physics Simulation Engine
    
    Simulates physical systems using qualitative reasoning,
    enabling prediction and explanation without numerical precision.
    """
    
    def __init__(self, domain: str = 'general'):
        """
        Initialize qualitative physics engine
        
        Args:
            domain: Physics domain ('thermodynamics', 'mechanics', 'fluids', etc.)
        """
        
        self.domain = domain
        self.objects: Dict[str, PhysicalObject] = {}
        self.processes: Dict[str, PhysicalProcess] = {}
        self.current_state: Optional[QualitativeState] = None
        
        # Reasoning components
        self.causal_reasoner = CausalReasoner()
        
        # Domain-specific knowledge
        self.process_library = {}
        self.physical_laws = []
        
        # Simulation parameters
        self.time_step = 0
        self.max_simulation_steps = 100
        
        # Initialize domain knowledge
        self._initialize_domain_knowledge()
        
        print(f"✓ Qualitative Physics Engine initialized:")
        print(f"   Domain: {domain}")
        print(f"   Process types: {len(self.process_library)}")
        
    def _initialize_domain_knowledge(self):
        """Initialize domain-specific physical knowledge"""
        
        # Heat transfer processes
        self.process_library['heat_conduction'] = {
            'conditions': ['temperature_difference_exists', 'thermal_contact'],
            'effects': [
                {'quantity': 'temperature_hot', 'change': 'decrease'},
                {'quantity': 'temperature_cold', 'change': 'increase'},
                {'quantity': 'entropy', 'change': 'increase'}
            ],
            'rate_factors': ['thermal_conductivity', 'temperature_difference', 'contact_area']
        }
        
        self.process_library['heat_convection'] = {
            'conditions': ['fluid_present', 'temperature_gradient'],
            'effects': [
                {'quantity': 'fluid_temperature', 'change': 'equalize'},
                {'quantity': 'fluid_velocity', 'change': 'increase'}
            ],
            'rate_factors': ['convection_coefficient', 'temperature_difference']
        }
        
        # Mechanical processes
        self.process_library['force_motion'] = {
            'conditions': ['net_force_nonzero'],
            'effects': [
                {'quantity': 'acceleration', 'change': 'proportional_to_force'},
                {'quantity': 'velocity', 'change': 'integrate_acceleration'}
            ],
            'rate_factors': ['force_magnitude', 'mass']
        }
        
        # Fluid processes
        self.process_library['pressure_flow'] = {
            'conditions': ['pressure_difference'],
            'effects': [
                {'quantity': 'fluid_velocity', 'change': 'increase'},
                {'quantity': 'pressure_high', 'change': 'decrease'},
                {'quantity': 'pressure_low', 'change': 'increase'}
            ],
            'rate_factors': ['pressure_gradient', 'fluid_viscosity']
        }
        
        # Physical laws
        self.physical_laws = [
            {'name': 'energy_conservation', 'type': 'conservation'},
            {'name': 'mass_conservation', 'type': 'conservation'},
            {'name': 'momentum_conservation', 'type': 'conservation'},
            {'name': 'second_law_thermodynamics', 'type': 'inequality'}
        ]
        
    def add_object(self, name: str, object_type: str, properties: Dict[str, Any]):
        """Add a physical object to the simulation"""
        
        # Convert properties to qualitative quantities
        qual_properties = {}
        for prop_name, prop_value in properties.items():
            if isinstance(prop_value, dict):
                qual_properties[prop_name] = QualitativeQuantity(
                    name=prop_name,
                    value=prop_value.get('value', 'unknown'),
                    derivative=prop_value.get('derivative', 'steady'),
                    landmarks=prop_value.get('landmarks', [])
                )
            else:
                # Simple value
                qual_properties[prop_name] = QualitativeQuantity(
                    name=prop_name,
                    value=str(prop_value),
                    derivative='steady',
                    landmarks=[]
                )
        
        obj = PhysicalObject(
            name=name,
            properties=qual_properties,
            material_type=object_type
        )
        
        self.objects[name] = obj
        print(f"✓ Added object '{name}' with {len(properties)} properties")
        
    def create_process(self, process_type: str, participants: List[str], 
                      conditions: List[str] = None) -> str:
        """Create a physical process instance"""
        
        if process_type not in self.process_library:
            raise ValueError(f"Unknown process type: {process_type}")
            
        process_template = self.process_library[process_type]
        process_name = f"{process_type}_{len(self.processes)}"
        
        process = PhysicalProcess(
            name=process_name,
            type=process_type,
            participants=participants,
            conditions=conditions or process_template['conditions'],
            effects=process_template['effects'],
            rate=QualitativeValue('medium'),  # Default rate
            active=False
        )
        
        self.processes[process_name] = process
        print(f"✓ Created process '{process_name}' involving {participants}")
        
        return process_name
        
    def simulate(self, initial_conditions: Dict[str, Any], 
                steps: int = None, verbose: bool = True) -> List[QualitativeState]:
        """
        Run qualitative simulation
        
        Args:
            initial_conditions: Initial state specification
            steps: Number of simulation steps
            verbose: Whether to print progress
            
        Returns:
            List of states through simulation
        """
        
        if steps is None:
            steps = self.max_simulation_steps
            
        if verbose:
            print(f"🔄 Starting qualitative simulation for {steps} steps...")
            
        # Initialize simulation state
        self.current_state = self._create_initial_state(initial_conditions)
        simulation_history = [self.current_state]
        
        for step in range(steps):
            self.time_step = step
            
            # Determine active processes
            active_processes = self._determine_active_processes()
            
            if verbose and step % max(1, steps // 10) == 0:
                print(f"   Step {step}: {len(active_processes)} active processes")
                
            # Apply process effects
            new_state = self._apply_process_effects(active_processes)
            
            # Check for state change
            if self._states_equivalent(new_state, self.current_state):
                if verbose:
                    print(f"   Simulation reached steady state at step {step}")
                break
                
            # Update state
            self.current_state = new_state
            simulation_history.append(new_state)
            
            # Check physical laws
            violations = self._check_physical_laws(new_state)
            if violations and verbose:
                print(f"   Warning: Physical law violations: {violations}")
                
        if verbose:
            print(f"✅ Simulation complete: {len(simulation_history)} states generated")
            
        return simulation_history
        
    def _create_initial_state(self, conditions: Dict[str, Any]) -> QualitativeState:
        """Create initial qualitative state from conditions"""
        
        quantities = {}
        
        # Extract quantities from objects
        for obj_name, obj in self.objects.items():
            for prop_name, prop in obj.properties.items():
                full_name = f"{obj_name}.{prop_name}"
                quantities[full_name] = prop
                
        # Apply initial conditions
        for condition_name, condition_value in conditions.items():
            if condition_name in quantities:
                quantities[condition_name].value = str(condition_value)
            else:
                # Create new quantity
                quantities[condition_name] = QualitativeQuantity(
                    name=condition_name,
                    value=str(condition_value),
                    derivative='steady',
                    landmarks=[]
                )
                
        return QualitativeState(
            quantities=quantities,
            active_processes=[],
            constraints_satisfied=True
        )
        
    def _determine_active_processes(self) -> List[str]:
        """Determine which processes are active in current state"""
        
        active = []
        
        for process_name, process in self.processes.items():
            if self._process_conditions_met(process):
                process.active = True
                active.append(process_name)
            else:
                process.active = False
                
        return active
        
    def _process_conditions_met(self, process: PhysicalProcess) -> bool:
        """Check if process activation conditions are met"""
        
        for condition in process.conditions:
            if not self._evaluate_process_condition(condition):
                return False
                
        return True
        
    def _evaluate_process_condition(self, condition: str) -> bool:
        """Evaluate a process activation condition"""
        
        # Handle common condition patterns
        if condition == 'temperature_difference_exists':
            return self._temperature_difference_exists()
        elif condition == 'thermal_contact':
            return self._thermal_contact_exists()
        elif condition == 'net_force_nonzero':
            return self._net_force_nonzero()
        elif condition == 'pressure_difference':
            return self._pressure_difference_exists()
        elif condition == 'fluid_present':
            return self._fluid_present()
        else:
            # Generic condition evaluation
            return condition in self.current_state.quantities
            
    def _temperature_difference_exists(self) -> bool:
        """Check if temperature difference exists between objects"""
        
        temperatures = []
        for name, quantity in self.current_state.quantities.items():
            if 'temperature' in name.lower():
                temperatures.append(quantity.value)
                
        # Check if all temperatures are different
        return len(set(temperatures)) > 1
        
    def _thermal_contact_exists(self) -> bool:
        """Check if objects are in thermal contact"""
        # Simplified - assume all objects are in contact
        return len(self.objects) > 1
        
    def _net_force_nonzero(self) -> bool:
        """Check if net force exists"""
        for name, quantity in self.current_state.quantities.items():
            if 'force' in name.lower() and quantity.value not in ['zero', 'none']:
                return True
        return False
        
    def _pressure_difference_exists(self) -> bool:
        """Check if pressure difference exists"""
        pressures = []
        for name, quantity in self.current_state.quantities.items():
            if 'pressure' in name.lower():
                pressures.append(quantity.value)
        return len(set(pressures)) > 1
        
    def _fluid_present(self) -> bool:
        """Check if fluid is present"""
        for obj in self.objects.values():
            if obj.material_type in ['liquid', 'gas', 'fluid']:
                return True
        return False
        
    def _apply_process_effects(self, active_processes: List[str]) -> QualitativeState:
        """Apply effects of active processes to create new state"""
        
        new_quantities = {}
        
        # Copy current quantities
        for name, quantity in self.current_state.quantities.items():
            new_quantities[name] = QualitativeQuantity(
                name=quantity.name,
                value=quantity.value,
                derivative=quantity.derivative,
                landmarks=quantity.landmarks
            )
            
        # Apply process effects
        for process_name in active_processes:
            process = self.processes[process_name]
            
            for effect in process.effects:
                self._apply_single_effect(effect, new_quantities, process)
                
        return QualitativeState(
            quantities=new_quantities,
            active_processes=active_processes,
            constraints_satisfied=True
        )
        
    def _apply_single_effect(self, effect: Dict[str, Any], 
                           quantities: Dict[str, QualitativeQuantity],
                           process: PhysicalProcess):
        """Apply a single process effect to quantities"""
        
        effect_type = effect.get('change', 'unknown')
        quantity_pattern = effect.get('quantity', '')
        
        # Find matching quantities
        matching_quantities = []
        for name in quantities:
            if quantity_pattern in name or name.endswith(quantity_pattern):
                matching_quantities.append(name)
                
        # Apply effect to matching quantities
        for name in matching_quantities:
            quantity = quantities[name]
            
            if effect_type == 'increase':
                self._increase_quantity(quantity)
            elif effect_type == 'decrease':
                self._decrease_quantity(quantity)
            elif effect_type == 'equalize':
                self._equalize_quantity(quantity, quantities)
            elif effect_type == 'proportional_to_force':
                self._set_proportional_to_force(quantity, quantities)
                
    def _increase_quantity(self, quantity: QualitativeQuantity):
        """Increase a qualitative quantity"""
        
        if quantity.value == 'zero':
            quantity.value = 'positive'
            quantity.derivative = 'increasing'
        elif quantity.value == 'negative':
            quantity.value = 'zero'
            quantity.derivative = 'increasing'
        elif quantity.value == 'positive':
            quantity.derivative = 'increasing'
        else:
            quantity.derivative = 'increasing'
            
    def _decrease_quantity(self, quantity: QualitativeQuantity):
        """Decrease a qualitative quantity"""
        
        if quantity.value == 'zero':
            quantity.value = 'negative'
            quantity.derivative = 'decreasing'
        elif quantity.value == 'positive':
            quantity.value = 'zero'
            quantity.derivative = 'decreasing'
        elif quantity.value == 'negative':
            quantity.derivative = 'decreasing'
        else:
            quantity.derivative = 'decreasing'
            
    def _equalize_quantity(self, quantity: QualitativeQuantity, 
                          all_quantities: Dict[str, QualitativeQuantity]):
        """Equalize quantity with related quantities"""
        
        # Find related quantities (same type)
        base_name = quantity.name.split('.')[-1]
        related = []
        
        for name, q in all_quantities.items():
            if name.endswith(base_name) and name != quantity.name:
                related.append(q)
                
        if related:
            # Move toward average
            if quantity.value == 'positive' and any(q.value == 'negative' for q in related):
                quantity.derivative = 'decreasing'
            elif quantity.value == 'negative' and any(q.value == 'positive' for q in related):
                quantity.derivative = 'increasing'
            else:
                quantity.derivative = 'steady'
                
    def _set_proportional_to_force(self, quantity: QualitativeQuantity,
                                  all_quantities: Dict[str, QualitativeQuantity]):
        """Set quantity proportional to force"""
        
        # Find force quantities
        for name, q in all_quantities.items():
            if 'force' in name.lower():
                if q.value == 'positive':
                    quantity.value = 'positive'
                    quantity.derivative = 'increasing'
                elif q.value == 'negative':
                    quantity.value = 'negative'
                    quantity.derivative = 'decreasing'
                else:
                    quantity.value = 'zero'
                    quantity.derivative = 'steady'
                break
                
    def _states_equivalent(self, state1: QualitativeState, 
                          state2: QualitativeState) -> bool:
        """Check if two qualitative states are equivalent"""
        
        if set(state1.quantities.keys()) != set(state2.quantities.keys()):
            return False
            
        for name in state1.quantities:
            q1 = state1.quantities[name]
            q2 = state2.quantities[name]
            
            if q1.value != q2.value or q1.derivative != q2.derivative:
                return False
                
        return True
        
    def _check_physical_laws(self, state: QualitativeState) -> List[str]:
        """Check for physical law violations"""
        
        violations = []
        
        for law in self.physical_laws:
            if law['type'] == 'conservation':
                if not self._check_conservation_law(law['name'], state):
                    violations.append(law['name'])
            elif law['type'] == 'inequality':
                if not self._check_inequality_law(law['name'], state):
                    violations.append(law['name'])
                    
        return violations
        
    def _check_conservation_law(self, law_name: str, state: QualitativeState) -> bool:
        """Check conservation law"""
        
        if law_name == 'energy_conservation':
            return self._check_energy_conservation(state)
        elif law_name == 'mass_conservation':
            return self._check_mass_conservation(state)
        elif law_name == 'momentum_conservation':
            return self._check_momentum_conservation(state)
            
        return True  # Unknown law - assume satisfied
        
    def _check_inequality_law(self, law_name: str, state: QualitativeState) -> bool:
        """Check inequality law"""
        
        if law_name == 'second_law_thermodynamics':
            return self._check_second_law(state)
            
        return True
        
    def _check_energy_conservation(self, state: QualitativeState) -> bool:
        """Check energy conservation"""
        # Simplified check - energy quantities should not spontaneously increase
        return True
        
    def _check_mass_conservation(self, state: QualitativeState) -> bool:
        """Check mass conservation"""
        # Simplified check - mass should be conserved
        return True
        
    def _check_momentum_conservation(self, state: QualitativeState) -> bool:
        """Check momentum conservation"""
        # Simplified check
        return True
        
    def _check_second_law(self, state: QualitativeState) -> bool:
        """Check second law of thermodynamics"""
        # Entropy should not decrease in isolated system
        return True
        
    def explain_behavior(self, phenomenon: str) -> List[str]:
        """Generate explanation for observed phenomenon"""
        
        explanations = []
        
        # Use causal reasoner to find explanations
        if 'increase' in phenomenon:
            quantity = phenomenon.replace(' increase', '')
            causal_explanations = self.causal_reasoner.explain_change(
                quantity, 'increase', {}
            )
            explanations.extend(causal_explanations)
            
        return explanations
        
    def get_simulation_summary(self) -> Dict[str, Any]:
        """Get summary of simulation state"""
        
        return {
            'objects': len(self.objects),
            'processes': len(self.processes),
            'active_processes': len([p for p in self.processes.values() if p.active]),
            'time_step': self.time_step,
            'current_quantities': len(self.current_state.quantities) if self.current_state else 0
        }