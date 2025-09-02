# Research Foundation: Qualitative Reasoning

## Primary Research Papers

### Qualitative Process Theory
- **Forbus, K. D. (1984).** "Qualitative process theory." *Artificial Intelligence, 24(1-3), 85-168.*
- **Forbus, K. D. (1988).** "Qualitative physics: Past, present, and future." *Exploring Artificial Intelligence, 239-296.*
- **Forbus, K. D., & Gentner, D. (1997).** "Qualitative mental models: Simulations or memories?" *Proceedings of the Eleventh International Workshop on Qualitative Reasoning, 97-104.*

### Confluence-based Qualitative Physics  
- **de Kleer, J., & Brown, J. S. (1984).** "A qualitative physics based on confluences." *Artificial Intelligence, 24(1-3), 7-83.*
- **de Kleer, J. (1986).** "An assumption-based TMS." *Artificial Intelligence, 28(2), 127-162.*
- **Kuipers, B. (1986).** "Qualitative simulation." *Artificial Intelligence, 29(3), 289-338.*

### Envisionment and State Space Analysis
- **de Kleer, J., & Brown, J. S. (1983).** "Assumptions and ambiguities in mechanistic mental models." *Mental Models, 155-190.*
- **Weld, D. S. (1990).** "Theories of comparative analysis." *Artificial Intelligence, 36(3), 381-393.*
- **Iwasaki, Y., & Simon, H. A. (1994).** "Causality and model abstraction." *Artificial Intelligence, 67(1), 143-194.*

### Constraint-based Reasoning
- **Mackworth, A. K. (1977).** "Consistency in networks of relations." *Artificial Intelligence, 8(1), 99-118.*
- **Montanari, U. (1974).** "Networks of constraints: Fundamental properties and applications to picture processing." *Information Sciences, 7, 95-132.*
- **Freuder, E. C. (1982).** "A sufficient condition for backtrack-free search." *Journal of the ACM, 29(1), 24-32.*

### Truth Maintenance Systems
- **Doyle, J. (1979).** "A truth maintenance system." *Artificial Intelligence, 12(3), 231-272.*
- **de Kleer, J. (1986).** "An assumption-based TMS." *Artificial Intelligence, 28(2), 127-162.*
- **Reiter, R., & de Kleer, J. (1987).** "Foundations of assumption-based truth maintenance systems." *AAAI-87, 183-188.*

## Theoretical Foundations

### Qualitative Process Theory (QPT)
Kenneth Forbus's QPT provides a framework for reasoning about continuous processes:

#### Core Concepts
- **Processes**: Continuous activities that cause changes in the world
- **Objects**: Entities that participate in processes  
- **Quantity Spaces**: Discrete abstractions of continuous parameters
- **Process Structures**: Conditions and consequences of process activity

#### Mathematical Framework
Process definition structure:
```
Process(P):
  Individuals: I₁, I₂, ..., Iₙ
  Preconditions: C₁ ∧ C₂ ∧ ... ∧ Cₘ  
  Quantity Conditions: Q₁ > 0, Q₂ = max, ...
  Relations: R₁, R₂, ..., Rₖ
  Influences: I⁺(Q), I⁻(Q)
```

#### Temporal Reasoning
QPT handles temporal progression through:
- **Episodes**: Intervals where process activity is constant
- **Transitions**: Boundary events between episodes
- **Limit Analysis**: Behavior at quantity space boundaries

### Confluence-based Qualitative Physics
De Kleer and Brown's approach focuses on local constraint propagation:

#### Confluence Definition
A confluence relates three variables through functional dependency:
```
Confluence(X, Y, Z) : Z = f(X, Y)
```
With qualitative constraints on partial derivatives.

#### Constraint Propagation Rules
- **Monotonicity**: If ∂f/∂X > 0, then X↑ → Z↑
- **Addition**: If Z = X + Y, then X↑ ∧ Y→ ⇒ Z↑
- **Multiplication**: If Z = X × Y with constraints on signs

#### Global Consistency
Multiple confluences create constraint networks requiring:
- **Arc Consistency**: Each binary constraint is locally consistent
- **Path Consistency**: Transitive constraints are satisfied
- **Global Search**: Backtracking when local propagation insufficient

### Envisionment Theory
Systematic exploration of qualitative state spaces:

#### State Representation
- **Qualitative State**: Assignment of values from quantity spaces
- **Distinguishing States**: Qualitatively different system behaviors  
- **Transition Conditions**: Process start/stop conditions

#### State Space Generation
```
Envisionment Algorithm:
1. Start with initial state S₀
2. Determine active processes P(S)
3. Compute successor states Succ(S)
4. Add transitions (S, S') for S' ∈ Succ(S)
5. Repeat until no new states found
```

#### Reachability Analysis
- **Forward Reachability**: States achievable from initial conditions
- **Backward Reachability**: States that can reach target conditions
- **Invariant Detection**: Properties maintained across all reachable states

## Implementation Features

### Qualitative Physics Engine
This implementation provides:

#### Process Modeling
- **Process Templates**: Reusable process definitions
- **Individual Binding**: Instantiation with specific objects
- **Condition Checking**: Precondition and quantity condition evaluation
- **Influence Resolution**: Computing net effects on quantities

#### Quantity Space Management
- **Landmark Values**: Critical points in continuous spaces
- **Intervals**: Regions between landmarks
- **Transitions**: Movement between intervals
- **Correspondence**: Relationships between quantity spaces

#### Temporal Simulation
- **Episode Generation**: Finding maximal consistent time intervals
- **Transition Analysis**: Determining possible next states
- **History Tracking**: Maintaining causal chains and dependencies

### Confluence Engine Implementation
Key algorithmic features:

#### Local Propagation
- **Arc Consistency**: AC-1, AC-3, and AC-4 algorithms
- **Value Propagation**: Forward and backward constraint propagation
- **Conflict Detection**: Identification of inconsistent value assignments

#### Ambiguity Handling
- **Multiple Solutions**: Representation of alternative interpretations
- **Assumption Management**: Tracking dependency on uncertain information
- **Disambiguation**: Strategies for resolving multiple solutions

#### Incremental Reasoning
- **Dynamic Updates**: Efficient handling of changing constraints
- **Dependency Maintenance**: Tracking reasons for derived values
- **Retraction**: Removing consequences of retracted assumptions

### Truth Maintenance System
Assumption-based Truth Maintenance System (ATMS) implementation:

#### Assumption Tracking
- **Labels**: Sets of assumptions supporting each conclusion
- **Environments**: Consistent sets of assumptions
- **Nogood Learning**: Recording conflicts for future avoidance

#### Dependency Networks
- **Justifications**: Rules connecting premises to conclusions
- **Support Networks**: Web of inferential dependencies
- **Contradiction Handling**: Backtracking and assumption revision

### Constraint Satisfaction
General constraint satisfaction capabilities:

#### Search Algorithms
- **Backtracking Search**: Systematic exploration with pruning
- **Forward Checking**: Maintaining arc consistency during search
- **Constraint Propagation**: Reducing search through inference

#### Optimization Techniques
- **Variable Ordering**: Choosing next variable to instantiate
- **Value Ordering**: Selecting promising values first
- **Constraint Ordering**: Prioritizing most restrictive constraints

## Applications and Domains

### Physical Systems Modeling
- **Mechanical Systems**: Gears, levers, springs, and linkages
- **Fluid Systems**: Flow, pressure, and level relationships
- **Thermal Systems**: Heat transfer and temperature dynamics
- **Electrical Circuits**: Voltage, current, and resistance relationships

### Engineering Diagnosis
- **Fault Modeling**: Representing abnormal component behaviors
- **Symptom Analysis**: Reasoning from observations to causes
- **Repair Planning**: Determining corrective actions
- **System Monitoring**: Real-time anomaly detection

### Scientific Modeling
- **Ecosystem Dynamics**: Population and resource interactions
- **Chemical Processes**: Reaction kinetics and equilibrium
- **Astronomical Systems**: Orbital mechanics and celestial phenomena
- **Geological Processes**: Formation, erosion, and structural changes

### Educational Applications
- **Physics Tutoring**: Teaching qualitative understanding
- **Mental Model Elicitation**: Discovering student misconceptions
- **Simulation Environments**: Interactive learning systems
- **Conceptual Assessment**: Evaluating qualitative reasoning skills

## Implementation Validation

### Benchmark Problems
Testing performed on classic QR benchmarks:
- **Water Tank System**: Multi-container fluid flow
- **Spring-Block Oscillator**: Mechanical dynamics
- **RC Circuit**: Electrical system analysis
- **Predator-Prey Model**: Ecological interactions

### Performance Characteristics
- **State Space Size**: Polynomial in quantity space size
- **Propagation Efficiency**: Linear in constraint network size
- **Memory Requirements**: Proportional to assumption set size
- **Convergence Properties**: Guaranteed for well-formed systems

### Educational Effectiveness
- **Conceptual Understanding**: Improved qualitative reasoning skills
- **Problem Solving**: Enhanced analytical thinking
- **Model Building**: Better system decomposition abilities
- **Transfer Learning**: Application to novel domains

This implementation serves as both a faithful reproduction of seminal qualitative reasoning research and a platform for exploring the intersection of AI, physics, and systems thinking in modern computational environments.