"""
Inductive Logic Programming Package
==================================

This package provides a modular implementation of Inductive Logic Programming (ILP)
based on Muggleton & De Raedt (1994) "Inductive Logic Programming: Theory and Methods".

The package is organized into modular components for maintainability and extensibility.

Quick Start:
-----------
    >>> from inductive_logic_programming import InductiveLogicProgrammer
    >>> from inductive_logic_programming import create_atom, create_constant
    >>> 
    >>> # Create an ILP system
    >>> ilp = InductiveLogicProgrammer()
    >>> 
    >>> # Add examples and learn rules
    >>> father_example = create_atom("father", [create_constant("john"), create_constant("mary")])
    >>> ilp.add_example(father_example, True)
    >>> rules = ilp.learn_rules("father")

Main Components:
---------------
- InductiveLogicProgrammer: Main ILP system class
- Factory functions: create_educational_ilp(), create_research_ilp_system(), etc.
- Logical structures: LogicalTerm, LogicalAtom, LogicalClause, Example
- Individual mixins for custom systems

Factory Functions:
-----------------
- create_educational_ilp(): Simple system for teaching/demos
- create_research_ilp_system(): Advanced system for research
- create_production_ilp(): Production-ready system
- create_custom_ilp(): Fully customizable system
"""

# Import main ILP system and factory functions
from .ilp_core import (
    InductiveLogicProgrammer,
    create_educational_ilp,
    create_research_ilp_system,
    create_production_ilp,
    create_custom_ilp
)

# Import logical structures
from .ilp_core import (
    LogicalTerm,
    LogicalAtom,
    LogicalClause,
    Example
)

# Import convenience functions
from .ilp_core import (
    create_variable,
    create_constant,
    create_function,
    create_atom,
    create_fact,
    create_rule,
    parse_term
)

# Import individual mixins for custom systems
from .ilp_core import (
    HypothesisGenerationMixin,
    UnificationEngineMixin,
    SemanticEvaluationMixin,
    RuleRefinementMixin,
    CoverageAnalysisMixin,
    PredicateSystemMixin
)

# Import all modules for backward compatibility
from .ilp_modules import *

# Import recovered core algorithms
# Import module groups - NO FAKE FALLBACKS!
from . import foil
from . import progol
from . import rule_refinement

# Import the main classes directly - NO FAKE FALLBACKS!
from .foil import FOILLearner
from .progol import ProgolSystem
print("✅ Connected to REAL FOIL and Progol implementations!")

__version__ = "2.0.0"
__author__ = "Benedict Chen"

# Define what gets imported with "from inductive_logic_programming import *"
__all__ = [
    # Main ILP system
    'InductiveLogicProgrammer',
    
    # Factory functions  
    'create_educational_ilp',
    'create_research_ilp_system',
    'create_production_ilp',
    'create_custom_ilp',
    
    # Logical structures
    'LogicalTerm',
    'LogicalAtom',
    'LogicalClause', 
    'Example',
    
    # Convenience functions
    'create_variable',
    'create_constant',
    'create_function',
    'create_atom',
    'create_fact',
    'create_rule',
    'parse_term',
    
    # Individual mixins
    'HypothesisGenerationMixin',
    'UnificationEngineMixin',
    'SemanticEvaluationMixin',
    'RuleRefinementMixin', 
    'CoverageAnalysisMixin',
    'PredicateSystemMixin',
    
    # Core algorithms (if available)
    'foil',
    'progol', 
    'rule_refinement',
    
    # Real ILP algorithm classes
    'FOILLearner',
    'ProgolSystem'
]