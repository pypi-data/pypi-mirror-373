# 🔍 PREDICATE SYSTEM MODULE - Advanced Predicate Management for ILP

## Overview

The **Predicate System Module** (`predicate_system.py`) provides comprehensive predicate management capabilities for Inductive Logic Programming systems. This module implements sophisticated predicate reasoning, vocabulary management, and compatibility checking essential for robust ILP operations.

## 🎯 Key Features

### 1. **Predicate Hierarchy Management**
- Taxonomic organization of predicates into categories
- Category-based compatibility checking
- Support for multi-level hierarchies
- Domain-specific predicate classification

### 2. **Alias & Equivalence System**
- Flexible predicate aliasing for domain adaptation
- Symmetric relationship handling
- Natural language predicate mapping
- Cross-domain terminology support

### 3. **Vocabulary Management**
- Automatic extraction from logical structures
- Comprehensive predicate, constant, and function tracking
- Dynamic vocabulary updates during learning
- Vocabulary reporting and analysis

### 4. **Theta-Subsumption Support**
- Full implementation of Muggleton & De Raedt theta-subsumption
- Variable substitution generation and testing
- Clause generality checking
- Advanced logical inference support

### 5. **Advanced Compatibility Checking**
- Multi-mechanism predicate compatibility
- Background knowledge integration
- Subsumption-based reasoning
- Efficient O(1) average-case lookups

## 🏗️ Architecture

```python
class PredicateSystemMixin:
    """Mixin providing predicate system functionality"""
    
    # Core initialization
    def _initialize_predicate_system(self)
    
    # Vocabulary management
    def _update_vocabulary_from_clause(self, clause)
    def _update_vocabulary_from_atom(self, atom)
    def _update_vocabulary_from_term(self, term)
    
    # Predicate compatibility
    def _predicates_compatible(self, pred1, pred2)
    def _predicates_appear_in_subsumption_relation(self, pred1, pred2, clause)
    
    # System management
    def add_predicate_alias(self, alias, canonical)
    def add_predicate_equivalence(self, pred1, pred2)
    def add_predicate_hierarchy(self, parent, children)
    
    # Theta-subsumption
    def theta_subsumes(self, clause1, clause2)
    def _find_theta_substitutions(self, clause1, clause2)
    def _check_subsumption_with_substitution(self, clause1, clause2, substitution)
    
    # Utilities
    def get_predicate_vocabulary(self)
    def validate_predicate_system(self)
    def clear_predicate_system(self)
```

## 🚀 Quick Start

### Basic Usage

```python
from inductive_logic_programming.ilp_modules import PredicateSystemMixin
from inductive_logic_programming.ilp_modules import LogicalTerm, LogicalAtom, LogicalClause

class MyILPSystem(PredicateSystemMixin):
    def __init__(self):
        self.background_knowledge = []
        self.predicates = set()
        self.constants = set()
        self.functions = set()
        self._initialize_predicate_system()

# Create system
ilp = MyILPSystem()

# Add domain-specific knowledge
ilp.add_predicate_alias("physician", "doctor")
ilp.add_predicate_hierarchy("medical_professional", {
    "doctor", "nurse", "surgeon", "therapist"
})
```

### Vocabulary Extraction

```python
# Create a logical clause
clause = LogicalClause(
    head=LogicalAtom("grandparent", [
        LogicalTerm("X", term_type="variable"),
        LogicalTerm("Z", term_type="variable")
    ]),
    body=[
        LogicalAtom("parent", [
            LogicalTerm("X", term_type="variable"),
            LogicalTerm("Y", term_type="variable")
        ]),
        LogicalAtom("parent", [
            LogicalTerm("Y", term_type="variable"),
            LogicalTerm("Z", term_type="variable")
        ])
    ]
)

# Extract vocabulary
ilp._update_vocabulary_from_clause(clause)
print(f"Extracted predicates: {ilp.predicates}")
# Output: {'grandparent', 'parent'}
```

### Predicate Compatibility

```python
# Check various compatibility mechanisms
print(ilp._predicates_compatible("father", "parent"))      # True (alias)
print(ilp._predicates_compatible("doctor", "nurse"))       # True (hierarchy)
print(ilp._predicates_compatible("spouse", "married"))     # True (equivalence)
print(ilp._predicates_compatible("parent", "house"))       # False (incompatible)
```

### Theta-Subsumption

```python
# General clause: parent(X,Y) :- father(X,Y)
general_clause = LogicalClause(
    head=LogicalAtom("parent", [
        LogicalTerm("X", term_type="variable"),
        LogicalTerm("Y", term_type="variable")
    ]),
    body=[LogicalAtom("father", [
        LogicalTerm("X", term_type="variable"),
        LogicalTerm("Y", term_type="variable")
    ])]
)

# Specific clause: parent(john,mary) :- father(john,mary), male(john)
specific_clause = LogicalClause(
    head=LogicalAtom("parent", [
        LogicalTerm("john", term_type="constant"),
        LogicalTerm("mary", term_type="constant")
    ]),
    body=[
        LogicalAtom("father", [
            LogicalTerm("john", term_type="constant"),
            LogicalTerm("mary", term_type="constant")
        ]),
        LogicalAtom("male", [
            LogicalTerm("john", term_type="constant")
        ])
    ]
)

# Test subsumption
result = ilp.theta_subsumes(general_clause, specific_clause)
print(f"Theta-subsumption: {result}")  # True
```

## 🔧 Advanced Features

### Domain Hierarchies

```python
# Medical domain
ilp.add_predicate_hierarchy("medical_condition", {
    "disease", "syndrome", "disorder", "infection", "injury"
})

# Business domain  
ilp.add_predicate_hierarchy("business_role", {
    "manager", "employee", "director", "analyst", "consultant"
})

# Test cross-hierarchy compatibility
print(ilp._predicates_compatible("disease", "syndrome"))     # True (same hierarchy)
print(ilp._predicates_compatible("disease", "manager"))      # False (different hierarchies)
```

### Alias Management

```python
# Add domain-specific aliases
ilp.add_predicate_alias("patient", "person")
ilp.add_predicate_alias("diagnosis", "medical_condition") 
ilp.add_predicate_alias("staff", "employee")

# Aliases resolve during compatibility checking
print(ilp._predicates_compatible("patient", "person"))       # True
print(ilp._predicates_compatible("staff", "manager"))        # True (both resolve to business roles)
```

### System Validation

```python
# Validate predicate system consistency
report = ilp.validate_predicate_system()

print("Validation Results:")
for category, messages in report.items():
    if messages:
        print(f"{category.upper()}:")
        for msg in messages:
            print(f"  - {msg}")

# Example output:
# WARNINGS:
#   - Self-referential equivalence: friend
# INFO:
#   - Total predicates: 15
#   - Aliases defined: 12
#   - Hierarchies defined: 4
```

## 📊 Performance Characteristics

### Complexity Analysis

| Operation | Average Case | Worst Case | Notes |
|-----------|-------------|------------|-------|
| Predicate Compatibility | O(1) | O(\|BK\|) | Background knowledge dependent |
| Vocabulary Extraction | O(n) | O(n) | Linear in clause/atom size |
| Theta-Subsumption | O(k^v) | O(k^v) | k=terms, v=variables (limited) |
| Alias Lookup | O(1) | O(1) | Hash-based lookup |
| Hierarchy Check | O(1) | O(h) | h=hierarchy depth |

### Memory Usage

- **Vocabularies**: O(|P| + |C| + |F|) where P=predicates, C=constants, F=functions
- **Hierarchies**: O(|H| × |Ch|) where H=hierarchies, Ch=average children per hierarchy  
- **Aliases**: O(|A|) where A=alias mappings
- **Equivalences**: O(|E|) where E=equivalence pairs

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_predicate_system.py
```

### Test Coverage

- ✅ Vocabulary extraction from complex structures
- ✅ All predicate compatibility mechanisms
- ✅ Dynamic system management
- ✅ Theta-subsumption with variable substitutions
- ✅ System validation and reporting
- ✅ Cross-domain functionality
- ✅ Performance with large vocabularies

## 🔬 Theoretical Foundation

### Mathematical Basis

The predicate system implements several key theoretical concepts:

#### Predicate Compatibility Relation
```
Compatible(P₁, P₂) ≡ 
    P₁ = P₂ ∨                                    (Direct match)
    canonical(P₁) = canonical(P₂) ∨              (Alias resolution)
    (P₁, P₂) ∈ EquivalenceSet ∨                  (Equivalence relation)
    ∃C: P₁ ∈ Children(C) ∧ P₂ ∈ Children(C) ∨    (Hierarchy compatibility)
    ∃clause ∈ BK: P₁, P₂ ∈ predicates(clause)    (Subsumption compatibility)
```

#### Theta-Subsumption
```
C₁ ⊑θ C₂ ⟺ ∃θ: C₁θ ⊆ C₂
```
Where:
- C₁, C₂ are logical clauses
- θ is a variable substitution  
- C₁θ is C₁ with substitution θ applied
- ⊆ is the subset relation on clause literals

#### Vocabulary Management
- **Predicates**: P = {p | p appears in any processed clause}
- **Constants**: C = {c | c is a constant term in any processed clause}  
- **Functions**: F = {f | f is a function symbol in any processed clause}

## 🔗 Integration

### With Main ILP System

The predicate system integrates seamlessly with the main ILP system through mixin inheritance:

```python
class InductiveLogicProgrammer(PredicateSystemMixin, ...):
    def __init__(self):
        # Initialize predicate system
        self._initialize_predicate_system()
        
    def learn_rules(self, target_predicate):
        # Predicate system methods available throughout learning
        pass
```

### With Other Modules

- **Unification Engine**: Uses `_predicates_compatible()` for unification decisions
- **Hypothesis Generation**: Leverages vocabulary and compatibility checking
- **Rule Refinement**: Utilizes theta-subsumption for refinement operations
- **Semantic Evaluation**: Benefits from enhanced predicate reasoning

## 🚨 Important Notes

### Limitations

1. **Combinatorial Explosion**: Theta-subsumption has exponential complexity in variable count
2. **Background Knowledge Size**: Compatibility checking can be O(|BK|) in worst case
3. **Memory Usage**: Large vocabularies consume significant memory

### Best Practices

1. **Hierarchy Design**: Keep hierarchies balanced and not too deep
2. **Alias Management**: Use canonical forms consistently
3. **Vocabulary Pruning**: Clear vocabularies when switching domains
4. **Validation**: Regularly validate system consistency

### Performance Tips

1. **Limit Variables**: Keep clause variables ≤ 4 for theta-subsumption efficiency
2. **Batch Updates**: Process vocabulary updates in batches when possible
3. **Cache Results**: Cache compatibility results for frequently used predicate pairs
4. **Prune Background**: Remove irrelevant background knowledge

## 🔮 Future Enhancements

### Planned Features

1. **Probabilistic Compatibility**: Soft compatibility scores based on statistical evidence
2. **Dynamic Learning**: Automatic hierarchy discovery from data
3. **Semantic Embeddings**: Vector-based predicate similarity
4. **Parallel Processing**: Multi-threaded theta-subsumption checking
5. **Incremental Updates**: Efficient vocabulary updates without full recomputation

### Research Directions

1. **Neural-Symbolic Integration**: Combine with embedding-based predicate similarity
2. **Ontology Integration**: Support for OWL/RDF ontology import
3. **Multi-Modal Predicates**: Handle predicates with different modalities
4. **Temporal Reasoning**: Support for temporal predicate relationships

## 📚 References

1. Muggleton, S. & De Raedt, L. (1994). "Inductive Logic Programming: Theory and Methods". Journal of Logic Programming, 19/20, 629-679.

2. Plotkin, G.D. (1970). "A Note on Inductive Generalization". Machine Intelligence, 5, 153-163.

3. Robinson, J.A. (1965). "A Machine-Oriented Logic Based on the Resolution Principle". Journal of the ACM, 12(1), 23-41.

4. Lloyd, J.W. (1987). "Foundations of Logic Programming". Springer-Verlag.

## 🏆 Summary

The **Predicate System Module** provides enterprise-grade predicate management for ILP systems, combining theoretical rigor with practical efficiency. It enables:

- ✅ **Domain Adaptation**: Flexible predicate definitions for any domain
- ✅ **Theoretical Soundness**: Full theta-subsumption and compatibility theory
- ✅ **Performance**: Optimized data structures and algorithms
- ✅ **Integration**: Seamless mixin-based integration
- ✅ **Validation**: Comprehensive system consistency checking

This module transforms ILP systems from rigid predicate handlers into flexible, domain-aware reasoning engines capable of sophisticated predicate relationship understanding and management.