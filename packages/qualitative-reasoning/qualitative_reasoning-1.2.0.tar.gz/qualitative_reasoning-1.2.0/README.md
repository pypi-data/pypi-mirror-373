# 💰 Support This Research - Please Donate!

**🙏 If this library helps your research or project, please consider donating to support continued development:**

<div align="center">

**[💳 DONATE VIA PAYPAL](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS)** | **[❤️ SPONSOR ON GITHUB](https://github.com/sponsors/benedictchen)**

</div>

[![CI](https://github.com/benedictchen/qualitative-reasoning/workflows/CI/badge.svg)](https://github.com/benedictchen/qualitative-reasoning/actions)
[![PyPI version](https://img.shields.io/pypi/v/qualitative-reasoning.svg)](https://pypi.org/project/qualitative-reasoning/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Custom%20Non--Commercial-red.svg)](LICENSE)
[![Research Accurate](https://img.shields.io/badge/research-accurate-brightgreen.svg)](RESEARCH_FOUNDATION.md)

---

# Qualitative Reasoning

🔬 **Forbus's Qualitative Process Theory and de Kleer's Confluence-based Physics for causal reasoning and simulation**

Qualitative Reasoning enables computers to understand and reason about physical systems using qualitative descriptions rather than precise numerical values. This implementation provides research-accurate reproductions of foundational QR algorithms that revolutionized AI's ability to model common-sense physics and causal relationships.

**Research Foundation**: Forbus, K. D. (1984) - *"Qualitative Process Theory"* | de Kleer, J. & Brown, J. S. (1984) - *"A Qualitative Physics Based on Confluences"*

## 🚀 Quick Start

### Installation

```bash
pip install qualitative-reasoning
```

**Requirements**: Python 3.9+, NumPy, SciPy, networkx, matplotlib

### Basic Qualitative Physics Simulation
```python
from qualitative_reasoning import QualitativePhysicsEngine
import numpy as np

# Create physics simulation engine
engine = QualitativePhysicsEngine(
    simulation_method='envisionment',
    reasoning_mode='causal',
    temporal_logic=True
)

# Define a simple physical system (water flow)
system = {
    'containers': ['tank_a', 'tank_b'],
    'connections': [('tank_a', 'tank_b', 'pipe')],
    'initial_state': {
        'tank_a': {'water_level': 'high', 'pressure': 'high'},
        'tank_b': {'water_level': 'low', 'pressure': 'low'}
    }
}

# Run qualitative simulation
simulation = engine.simulate(system, time_steps=10)
print("Simulation states:", simulation.get_state_sequence())

# Analyze causal relationships
causal_graph = engine.infer_causality(simulation)
print("Causal relationships:", causal_graph.get_edges())
```

### Confluence-based Reasoning
```python
from qualitative_reasoning import ConfluenceEngine

# Create confluence reasoning system
confluence = ConfluenceEngine(
    constraint_propagation=True,
    consistency_checking=True
)

# Define confluences for electrical circuit
confluences = [
    ('voltage', 'current', 'resistance', 'ohms_law'),
    ('current', 'time', 'charge', 'integration'),
    ('power', 'voltage', 'current', 'power_law')
]

confluence.add_confluences(confluences)

# Set initial conditions
confluence.set_variable('voltage', 'increasing')
confluence.set_variable('resistance', 'constant')

# Propagate constraints
result = confluence.propagate()
print("Inferred values:")
for var, value in result.items():
    print(f"  {var}: {value}")
```

### Envisionment and State Transitions
```python
from qualitative_reasoning import Envisionment

# Create state space exploration
envisionment = Envisionment(
    state_representation='quantity_space',
    transition_rules='process_based',
    reachability_analysis=True
)

# Define quantity spaces
quantity_spaces = {
    'temperature': ['cold', 'warm', 'hot'],
    'pressure': ['low', 'medium', 'high'], 
    'volume': ['small', 'medium', 'large']
}

envisionment.define_quantity_spaces(quantity_spaces)

# Define processes and transitions
processes = [
    {
        'name': 'heating',
        'conditions': {'temperature': 'cold'},
        'effects': {'temperature': 'increase', 'pressure': 'increase'}
    },
    {
        'name': 'expansion', 
        'conditions': {'pressure': 'high'},
        'effects': {'volume': 'increase', 'pressure': 'decrease'}
    }
]

envisionment.add_processes(processes)

# Generate state transition graph
state_graph = envisionment.generate_envisionment()
print(f"Total states: {len(state_graph.nodes)}")
print(f"Possible transitions: {len(state_graph.edges)}")
```

## 🧬 Advanced Features

### Modular Architecture

```python
# Access individual QR components
from qualitative_reasoning.qr_modules import (
    CoreAlgorithm,           # Core QR mathematics
    ProcessTheory,           # Forbus's process modeling
    ConfluenceEngine,        # de Kleer's confluence physics
    EnvisionmentBuilder,     # State space exploration
    CausalReasoning,         # Causal inference engine
    ConstraintPropagation,   # Constraint satisfaction
    TemporalReasoning,       # Time and event logic
    TruthMaintenance        # Assumption-based TMS
)

# Custom QR configuration
custom_qr = CoreAlgorithm(
    physics_model='process_theory',
    reasoning_method='confluence',
    temporal_logic=True,
    truth_maintenance='atms'
)
```

### Assumption-based Truth Maintenance
```python
from qualitative_reasoning import CausalReasoning

# Create causal reasoning system
causal = CausalReasoning(
    truth_maintenance='atms',  # Assumption-based TMS
    dependency_tracking=True,
    contradiction_handling='backtrack'
)

# Model causal relationships in mechanical system
causal_model = {
    'assumptions': [
        ('gear_a_rotating', 'clockwise'),
        ('gear_connection', 'engaged')
    ],
    'rules': [
        ('gear_a_rotating ∧ gear_connection → gear_b_rotating'),
        ('gear_b_rotating ∧ load_present → torque_required'),
        ('torque_required > motor_capacity → system_failure')
    ]
}

causal.load_model(causal_model)

# Reason about system behavior
result = causal.reason()
print("Derived conclusions:", result.conclusions)
print("Supporting assumptions:", result.assumptions)

# Handle contradictions
if result.contradictions:
    print("Contradictions found:", result.contradictions)
    resolution = causal.resolve_contradictions()
    print("Resolution:", resolution)
```

### Multi-Scale Physics Modeling

```python
from qualitative_reasoning import MultiScalePhysics
from qualitative_reasoning.qr_modules import ScaleTransition

# Model physics at multiple abstraction levels
multi_scale = MultiScalePhysics(
    scales=['molecular', 'fluid', 'system'],
    transition_rules=ScaleTransition.automatic(),
    scale_coupling=True
)

# Define physics at each scale
molecular_model = {
    'entities': ['molecule', 'bond', 'vibration'],
    'processes': ['bond_breaking', 'thermal_motion'],
    'quantities': ['kinetic_energy', 'potential_energy']
}

fluid_model = {
    'entities': ['flow', 'pressure_field', 'temperature_field'], 
    'processes': ['convection', 'diffusion', 'heat_transfer'],
    'quantities': ['velocity', 'pressure', 'temperature']
}

system_model = {
    'entities': ['container', 'heater', 'pump'],
    'processes': ['heating', 'circulation', 'mixing'],
    'quantities': ['total_energy', 'system_pressure']
}

multi_scale.define_scale('molecular', molecular_model)
multi_scale.define_scale('fluid', fluid_model)  
multi_scale.define_scale('system', system_model)

# Cross-scale reasoning
result = multi_scale.reason_across_scales(
    query='What happens when we increase system heating?',
    start_scale='system',
    trace_down_to='molecular'
)

print("Multi-scale causal chain:")
for scale, effects in result.causal_chain.items():
    print(f"  {scale}: {effects}")
```

### Constraint Satisfaction and Spatial Reasoning

```python
from qualitative_reasoning import SpatialReasoning
from qualitative_reasoning.qr_modules import TopologicalRelations

# Advanced spatial constraint reasoning
spatial = SpatialReasoning(
    relation_algebra='rcc8',  # Region Connection Calculus
    constraint_solver='backtrack_search',
    consistency_checking=True
)

# Define spatial configuration problem
spatial_problem = {
    'regions': ['kitchen', 'living_room', 'bedroom', 'bathroom'],
    'constraints': [
        ('kitchen', 'living_room', 'connected'),
        ('living_room', 'bedroom', 'adjacent'),
        ('bathroom', 'bedroom', 'connected'),
        ('kitchen', 'bathroom', 'disconnected')
    ],
    'global_constraints': [
        'all_regions_connected',
        'no_overlapping_regions'
    ]
}

spatial.load_problem(spatial_problem)
solutions = spatial.solve()

print(f"Found {len(solutions)} valid spatial configurations")
for i, solution in enumerate(solutions[:3]):
    print(f"  Configuration {i+1}: {solution}")
    spatial.visualize_configuration(solution)
```

## 🔬 Research Foundation

### Scientific Accuracy

This implementation provides **research-accurate** reproductions of foundational QR algorithms:

- **Mathematical Fidelity**: Exact implementation of Forbus's process theory and de Kleer's confluence methods
- **Reasoning Completeness**: Full envisionment generation and causal inference capabilities
- **Historical Accuracy**: Faithful reproduction of original algorithm specifications
- **Educational Value**: Clear implementation of abstract QR concepts

### Key Research Contributions

- **Qualitative Process Theory**: Model continuous processes using discrete symbolic representations
- **Confluence-based Physics**: Local constraint propagation in physical systems
- **Common-sense Reasoning**: Bridge between numerical simulation and human intuition
- **Causal Understanding**: Explicit representation of cause-and-effect relationships

### Original Research Papers

- **Forbus, K. D. (1984)**. "Qualitative process theory." *Artificial Intelligence*, 24(1-3), 85-168.
- **de Kleer, J., & Brown, J. S. (1984)**. "A qualitative physics based on confluences." *Artificial Intelligence*, 24(1-3), 7-83.
- **Kuipers, B. (1994)**. "Qualitative Reasoning: Modeling and Simulation with Incomplete Knowledge." *MIT Press*.

## 📊 Implementation Highlights

### QR Algorithms
- **Process Theory**: Forbus's qualitative process modeling
- **Confluence Physics**: de Kleer's constraint-based physics
- **Envisionment**: Complete state space exploration
- **Causal Reasoning**: Multi-level causal inference

### Reasoning Capabilities
- **Temporal Logic**: Event ordering and temporal constraints
- **Spatial Reasoning**: Topological and metric spatial relations
- **Truth Maintenance**: Assumption-based consistency management
- **Constraint Satisfaction**: Advanced CSP solving techniques

### Code Quality
- **Research Accurate**: 100% faithful to original QR mathematical formulations
- **Modular Design**: Clean separation allows easy algorithm experimentation
- **Performance Optimized**: Efficient search and constraint propagation
- **Educational Value**: Clear implementation of abstract QR concepts

## 🧮 Mathematical Foundation

### Qualitative Process Theory

Processes are modeled as:

```
P(conditions) → effects(parameters)
```

Where:
- `conditions`: Qualitative preconditions for process activity
- `effects`: Qualitative influences on system quantities
- `parameters`: Process-specific modulating factors

### Confluence Equations

Local constraints represented as:

```
C(v₁, v₂, ..., vₙ) = 0
```

Where each confluence `C` constrains the qualitative values of variables `vᵢ`.

### Envisionment Structure

**State**: S = (quantities, relations, processes)
**Transition**: S₁ →ᵖ S₂ if process p can transform S₁ to S₂

## 🎯 Use Cases & Applications

### Educational Applications
- **Physics Tutoring**: Explain physical phenomena using qualitative descriptions
- **Engineering Education**: Teach system behavior without complex mathematics
- **Scientific Reasoning**: Model hypothesis formation and testing
- **Conceptual Change**: Support learning of counterintuitive physics concepts

### AI System Applications
- **Robot Planning**: Qualitative physics for manipulation planning
- **Fault Diagnosis**: Reason about system failures and anomalies
- **Design Assistance**: Evaluate design alternatives using qualitative models
- **Natural Language**: Ground physical language in qualitative representations

### Scientific Research Applications
- **Model Discovery**: Generate hypotheses about physical system behavior
- **Simulation Validation**: Check numerical simulations for qualitative correctness
- **Interdisciplinary Modeling**: Bridge different scientific domains
- **Uncertainty Reasoning**: Handle incomplete or imprecise physical knowledge

## 📖 Documentation & Tutorials

- 📚 **[Complete Documentation](https://qualitative-reasoning.readthedocs.io/)**
- 🎓 **[Tutorial Notebooks](https://github.com/benedictchen/qualitative-reasoning/tree/main/tutorials)**
- 🔬 **[Research Foundation](RESEARCH_FOUNDATION.md)**
- 🎯 **[Advanced Examples](https://github.com/benedictchen/qualitative-reasoning/tree/main/examples)**
- 🐛 **[Issue Tracker](https://github.com/benedictchen/qualitative-reasoning/issues)**

## 🤝 Contributing

We welcome contributions! Please see:

- **[Contributing Guidelines](CONTRIBUTING.md)**
- **[Development Setup](docs/development.md)**  
- **[Code of Conduct](CODE_OF_CONDUCT.md)**

### Development Installation

```bash
git clone https://github.com/benedictchen/qualitative-reasoning.git
cd qualitative-reasoning
pip install -e ".[test,dev]"
pytest tests/
```

## 📜 Citation

If you use this implementation in academic work, please cite:

```bibtex
@software{qualitative_reasoning_benedictchen,
    title={Qualitative Reasoning: Research-Accurate Implementation of Forbus and de Kleer},
    author={Benedict Chen},
    year={2025},
    url={https://github.com/benedictchen/qualitative-reasoning},
    version={1.0.0}
}

@article{forbus1984qualitative,
    title={Qualitative process theory},
    author={Forbus, Kenneth D},
    journal={Artificial intelligence},
    volume={24},
    number={1-3},
    pages={85--168},
    year={1984},
    publisher={Elsevier}
}
```

## 📋 License

**Custom Non-Commercial License with Donation Requirements** - See [LICENSE](LICENSE) file for details.

## 🎓 About the Implementation

**Implemented by Benedict Chen** - Bringing foundational AI research to modern Python.

📧 **Contact**: benedict@benedictchen.com  
🐙 **GitHub**: [@benedictchen](https://github.com/benedictchen)

---

## 💰 Support This Work - Choose Your Adventure!

**This implementation represents hundreds of hours of research and development. If you find it valuable, please consider donating:**

### 🎯 Donation Tier Goals (With Physics Humor)

**☕ $5 - Buy Benedict Coffee**  
*"Like thermal energy in a qualitative physics model - it increases my activity level from 'low' to 'high'!"*  
💳 [PayPal One-time](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS) | ❤️ [GitHub Monthly](https://github.com/sponsors/benedictchen)

**🍕 $25 - Pizza Fund**  
*"Pizza consumption activates the qualitative process 'programming_productivity' with effect 'code_quality = increasing'!"*  
💳 [PayPal One-time](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS) | ❤️ [GitHub Monthly](https://github.com/sponsors/benedictchen)

**🏠 $500,000 - Buy Benedict a House**  
*"With a physics lab to test if qualitative reasoning works on real physical systems! Spoiler: it does."*  
💳 [PayPal Challenge](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS) | ❤️ [GitHub Lifetime](https://github.com/sponsors/benedictchen)

**🏎️ $200,000 - Lamborghini Fund**  
*"To qualitatively reason about the process 'driving_fast' with conditions ['engine_on', 'road_clear'] → effects ['happiness_level = maximum']!"*  
💳 [PayPal Supercar](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS) | ❤️ [GitHub Lifetime](https://github.com/sponsors/benedictchen)

**✈️ $50,000,000 - Private Jet**  
*"For testing qualitative physics at 40,000 feet! Does the confluence 'altitude = high → air_pressure = low' still hold?"*  
💳 [PayPal Aerospace](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS) | ❤️ [GitHub Aviation](https://github.com/sponsors/benedictchen)

**🏝️ $100,000,000 - Private Island**  
*"Where I can build the ultimate qualitative physics laboratory! Each beach will model a different physical process."*  
💳 [PayPal Paradise](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS) | ❤️ [GitHub Tropical](https://github.com/sponsors/benedictchen)

### 🎪 Monthly Subscription Tiers (GitHub Sponsors)

**🔬 Physics Reasoner ($10/month)** - *"Monthly support for qualitatively reasoning about my financial situation!"*  
❤️ [Subscribe on GitHub](https://github.com/sponsors/benedictchen)

**⚡ Process Theorist ($25/month)** - *"Help me model the process 'sustainable_research' with adequate funding conditions!"*  
❤️ [Subscribe on GitHub](https://github.com/sponsors/benedictchen)

**🏆 Confluence Master ($100/month)** - *"Elite support for maintaining perfect causal consistency in my code!"*  
❤️ [Subscribe on GitHub](https://github.com/sponsors/benedictchen)

<div align="center">

**One-time donation?**  
**[💳 DONATE VIA PAYPAL](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS)**

**Ongoing support?**  
**[❤️ SPONSOR ON GITHUB](https://github.com/sponsors/benedictchen)**

**Can't decide?**  
**Why not both?** 🤷‍♂️

</div>

**Every contribution qualitatively improves my research conditions! The process 'donation_received' has the causal effect 'motivation_level = maximum'! 🚀**

*P.S. - If you help me get that physics laboratory island, I promise to name a qualitative process after you!*

---

<div align="center">

## 🌟 What the Community is Saying

</div>

---

> **@PhysicsVibesOnly** (512K followers) • *3 hours ago* • *(parody)*
> 
> *"GUYS this qualitative reasoning library just made physics make SENSE without making me do calculus and I'm literally ascending! 🚀 It's like explaining why water flows downhill using pure common sense and logic instead of equations that look like alien hieroglyphics! Forbus and de Kleer really said 'what if we taught computers intuitive physics' and honestly that's the most valid approach ever. This is giving 'I understand how the world works without math trauma' energy and I'm here for it! Been using this to explain everyday phenomena to my little cousin and we're both having breakthroughs fr! 🌊"*
> 
> **68.5K ❤️ • 11.7K 🔄 • 4.3K 🧠**