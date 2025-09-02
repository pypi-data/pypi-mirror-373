# 🧠 Modular Inductive Logic Programming System

A comprehensive, modular implementation of Inductive Logic Programming based on Muggleton & De Raedt (1994) "Inductive Logic Programming: Theory and Methods" with modern software engineering practices.

## 🎯 Overview

This system transforms the original monolithic ILP implementation into a clean, modular architecture using mixins while maintaining full backward compatibility. Each module focuses on a specific aspect of ILP, making the system easier to understand, extend, and maintain.

## 🏗️ Architecture

### Core Integration: `ilp_core.py`
The main `InductiveLogicProgrammer` class that integrates all specialized mixins:

```python
class InductiveLogicProgrammer(
    HypothesisGenerationMixin,
    UnificationEngineMixin, 
    SemanticEvaluationMixin,
    RuleRefinementMixin,
    CoverageAnalysisMixin,
    PredicateSystemMixin
):
    """Complete ILP system with all capabilities"""
```

### Specialized Modules

#### 1. **Logical Structures** (`logical_structures.py`)
- Core data structures: `LogicalTerm`, `LogicalAtom`, `LogicalClause`, `Example`
- Validation, string representations, and utility functions
- Foundation for all logical reasoning operations

#### 2. **Hypothesis Generation** (`hypothesis_generation.py`) 
- Pattern extraction from positive examples
- Background knowledge integration via unification
- Systematic candidate clause generation
- Implementation of Muggleton's hypothesis generation framework

#### 3. **Unification Engine** (`unification_engine.py`)
- Robinson's unification algorithm (1965)
- Occurs check for preventing infinite structures
- Substitution application and composition
- Theta-subsumption for clause ordering

#### 4. **Semantic Evaluation** (`semantic_evaluation.py`)
- Three semantic settings: Normal, Definite, Nonmonotonic
- Hypothesis validation under chosen semantics
- Entailment checking and logical inference
- Semantic-specific scoring for hypothesis ranking

#### 5. **Rule Refinement** (`rule_refinement.py`)
- Specialization operators (downward refinement)
- Generalization operators (upward refinement)  
- Statistical significance testing
- Quality metrics and rule assessment

#### 6. **Coverage Analysis** (`coverage_analysis.py`)
- Comprehensive coverage metrics (precision, recall, F1-score)
- Statistical significance testing (Chi-square, Fisher's exact)
- Performance analysis and reporting
- Support for noisy data evaluation

#### 7. **Predicate System** (`predicate_system.py`)
- Predicate hierarchies and taxonomies
- Alias and equivalence management
- Compatibility reasoning for unification
- Vocabulary extraction and management

## 🚀 Quick Start

### Basic Usage

```python
from inductive_logic_programming import InductiveLogicProgrammer
from inductive_logic_programming import create_atom, create_constant

# Create ILP system
ilp = InductiveLogicProgrammer()

# Add background knowledge
parent_fact = create_fact(
    create_atom("parent", [create_constant("john"), create_constant("mary")])
)
ilp.add_background_knowledge(parent_fact)

# Add training examples
father_example = create_atom("father", [create_constant("john"), create_constant("mary")])
ilp.add_example(father_example, True)

# Learn rules
rules = ilp.learn_rules("father")
```

### Factory Functions

```python
# Educational system (simple rules, high confidence)
edu_ilp = create_educational_ilp()

# Research system (complex rules, advanced semantics)  
research_ilp = create_research_ilp_system()

# Production system (balanced, robust)
prod_ilp = create_production_ilp()

# Custom system
custom_ilp = create_custom_ilp(
    max_clause_length=8,
    semantic_setting='nonmonotonic',
    noise_tolerance=0.2
)
```

### Custom Mixin Systems

```python
from inductive_logic_programming import HypothesisGenerationMixin, UnificationEngineMixin

class MinimalILP(HypothesisGenerationMixin, UnificationEngineMixin):
    """Custom ILP system with only specific capabilities"""
    def __init__(self):
        self.max_variables = 3
        self.background_knowledge = []
        # ... minimal initialization
```

## 📊 Features

### ✨ Core ILP Capabilities
- **Rule Learning**: Automatic discovery of logical rules from examples
- **Background Knowledge**: Integration of domain expertise  
- **Query Answering**: Inference over learned knowledge
- **Explanation Generation**: Human-readable reasoning chains

### ✨ Advanced Features
- **Multiple Semantics**: Normal, Definite, Nonmonotonic reasoning
- **Statistical Analysis**: Significance testing, confidence intervals
- **Noise Handling**: Robust learning from imperfect data
- **Predicate Hierarchies**: Domain-specific knowledge integration
- **Performance Metrics**: Comprehensive evaluation and reporting

### ✨ Software Engineering
- **Modular Design**: Clean separation of concerns
- **Factory Functions**: Pre-configured systems for common use cases
- **Backward Compatibility**: Drop-in replacement for original system
- **Extensibility**: Easy to add new semantic settings, operators
- **Testing**: Each module can be tested in isolation

## 🔧 Configuration Options

### Learning Parameters
```python
InductiveLogicProgrammer(
    max_clause_length=5,        # Rule complexity limit
    max_variables=4,            # Variable count limit  
    confidence_threshold=0.8,   # Minimum rule confidence
    coverage_threshold=0.7,     # Minimum coverage requirement
    noise_tolerance=0.1,        # Tolerance for inconsistent data
    semantic_setting='normal'   # Reasoning semantics
)
```

### Semantic Settings
- **'normal'**: Classical logic with consistency checking
- **'definite'**: Horn clause semantics, Prolog-like reasoning
- **'nonmonotonic'**: Closed-world assumption with minimality

## 📈 Performance & Statistics

The system tracks comprehensive learning statistics:

```python
ilp.print_learning_statistics()
```

Output:
```
📊 Learning Statistics:
==============================
Clauses Generated: 18
Clauses Evaluated: 18
Semantic Evaluations: 18
Coverage Calculations: 18
Final Rules Selected: 3
Learning Time Seconds: 0.001

Vocabulary Size:
  Predicates: 6
  Constants: 7
  Variables: 2
  Functions: 0

Knowledge Base:
  Background Knowledge: 16 clauses
  Training Examples: 10 total
    Positive: 6
    Negative: 4
  Learned Rules: 3
```

## 🎓 Educational Use

Perfect for teaching ILP concepts:

```python
# Simple system for demonstrations
edu_ilp = create_educational_ilp()

# Learn basic family relationships
edu_ilp.add_background_knowledge(parent_facts)
edu_ilp.add_example(father_examples)
rules = edu_ilp.learn_rules("father")

# Show results
edu_ilp.print_learned_rules()
```

## 🔬 Research Applications

Advanced system for research:

```python
# Research-grade system
research_ilp = create_research_ilp_system()

# Complex domain with noise
research_ilp = create_custom_ilp(
    max_clause_length=10,
    semantic_setting='nonmonotonic',
    noise_tolerance=0.15,
    coverage_threshold=0.8
)

# Learn complex rules
rules = research_ilp.learn_rules("complex_predicate")

# Analyze performance
research_ilp.print_learning_statistics()
```

## 🏭 Production Deployment

Robust system for real applications:

```python
# Production-ready system
prod_ilp = create_production_ilp()

# Handle real-world data
for data_point in production_data:
    prod_ilp.add_example(data_point.atom, data_point.label)

# Learn reliable rules
rules = prod_ilp.learn_rules(target_predicate)

# Query system
result, confidence, proof = prod_ilp.query(query_atom)
if result:
    explanations = prod_ilp.explain_prediction(query_atom)
```

## 🧪 Testing & Validation

Each module can be tested independently:

```python
# Test individual components
from inductive_logic_programming import UnificationEngineMixin

class TestUnification(UnificationEngineMixin):
    def test_robinson_algorithm(self):
        atom1 = create_atom("father", [create_variable("X"), create_constant("mary")])
        atom2 = create_atom("father", [create_constant("john"), create_variable("Y")])
        
        substitution = self._robinson_unification(atom1, atom2)
        assert substitution == {"X": create_constant("john"), "Y": create_constant("mary")}
```

## 📁 File Structure

```
inductive_logic_programming/
├── ilp_core.py                          # Main integration class
├── ilp_modules/                         # Specialized modules
│   ├── __init__.py
│   ├── logical_structures.py           # Core data structures
│   ├── hypothesis_generation.py        # Hypothesis generation
│   ├── unification_engine.py          # Robinson's algorithm
│   ├── semantic_evaluation.py         # Semantic frameworks
│   ├── rule_refinement.py             # Refinement operators
│   ├── coverage_analysis.py           # Statistical analysis
│   └── predicate_system.py            # Predicate management
├── __init__.py                         # Package imports
└── demo_modular_ilp.py                # Comprehensive demo
```

## 🔄 Migration Guide

### From Original System
The modular system is a drop-in replacement:

```python
# Original usage - still works!
from inductive_logic_programming import InductiveLogicProgrammer

ilp = InductiveLogicProgrammer()
ilp.add_background_knowledge(clauses)
ilp.add_example(atom, True)
rules = ilp.learn_rules("target")
```

### New Features Available
```python
# Use factory functions
ilp = create_educational_ilp()

# Access individual mixins
from inductive_logic_programming import HypothesisGenerationMixin

# Enhanced query system
result, confidence, proof = ilp.query(atom)
explanations = ilp.explain_prediction(atom)
```

## 🤝 Contributing

### Adding New Modules
1. Create new mixin in `ilp_modules/`
2. Inherit from appropriate base class
3. Implement required methods
4. Add to `InductiveLogicProgrammer` inheritance
5. Update `__init__.py` exports

### Adding New Semantic Settings
1. Extend `SemanticEvaluationMixin`
2. Add evaluation method for new semantics
3. Update dispatcher in `_evaluate_hypothesis_semantic`
4. Test with various rule types

### Adding New Factory Functions
1. Define in `ilp_core.py`
2. Configure appropriate parameters
3. Document use case and benefits
4. Add to `__all__` exports

## 📚 References

1. Muggleton, S., & De Raedt, L. (1994). Inductive logic programming: Theory and methods. *Journal of Logic Programming*, 19, 629-679.

2. Robinson, J. A. (1965). A machine-oriented logic based on the resolution principle. *Journal of the ACM*, 12(1), 23-41.

3. Mitchell, T. M. (1982). Generalization as search. *Artificial Intelligence*, 18(2), 203-226.

4. Plotkin, G. D. (1970). A note on inductive generalization. *Machine Intelligence*, 5, 153-163.

## 📄 License

Same as original implementation. See LICENSE file for details.

## ✨ Acknowledgments

Built upon the foundational work of Stephen Muggleton and Luc De Raedt, whose 1994 paper launched the field of Inductive Logic Programming and continues to inspire automated knowledge discovery research.

---

**🚀 Ready to discover logical rules from your data? Try the modular ILP system today!**