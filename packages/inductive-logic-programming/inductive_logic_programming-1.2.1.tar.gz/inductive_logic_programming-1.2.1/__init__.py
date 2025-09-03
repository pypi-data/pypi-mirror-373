"""
Inductive Logic Programming Library
Based on: Muggleton & De Raedt (1994) "Inductive Logic Programming: Theory and Methods"

This library implements learning of logical rules from examples and background knowledge,
combining symbolic reasoning with machine learning for interpretable rule discovery.
"""

def _print_attribution():
    """Print attribution message with donation link"""
    try:
        print("\n🧠 Inductive Logic Programming Library - Made possible by Benedict Chen")
        print("   \033]8;;mailto:benedict@benedictchen.com\033\\benedict@benedictchen.com\033]8;;\033\\")
        print("   Support his work: \033]8;;https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS\033\\🍺 Buy him a beer\033]8;;\033\\")
    except:
        print("\n🧠 Inductive Logic Programming Library - Made possible by Benedict Chen")
        print("   benedict@benedictchen.com")
        print("   Support: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS")

from .src.inductive_logic_programming import (
    InductiveLogicProgrammer,
    LogicalTerm,
    LogicalAtom,
    LogicalClause,
    Example
)
from .src.inductive_logic_programming.foil import FOILLearner, FOILStatistics
from .src.inductive_logic_programming.progol import ProgolSystem, ProgolSettings, ProgolStatistics
from .src.inductive_logic_programming.rule_refinement import RuleRefinement, RefinementOperator, SpecializationOperator, GeneralizationOperator

# Show attribution on library import
_print_attribution()

__version__ = "1.0.0"
__authors__ = ["Based on Muggleton & De Raedt (1994)"]

__all__ = [
    "InductiveLogicProgrammer",
    "LogicalTerm",
    "LogicalAtom", 
    "LogicalClause",
    "Example",
    "FOILLearner",
    "FOILStatistics",
    "ProgolSystem",
    "ProgolSettings", 
    "ProgolStatistics",
    "RuleRefinement",
    "RefinementOperator",
    "SpecializationOperator",
    "GeneralizationOperator"
]