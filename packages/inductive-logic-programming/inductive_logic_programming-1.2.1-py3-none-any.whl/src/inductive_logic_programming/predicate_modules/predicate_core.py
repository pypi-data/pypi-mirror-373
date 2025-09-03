"""
Core Predicate System Implementation
====================================

Author: Benedict Chen (benedict@benedictchen.com)

Core predicate system functionality extracted from predicate_system.py.
"""

from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass


@dataclass 
class PredicateDefinition:
    """Definition of a predicate with its properties"""
    name: str
    arity: int
    argument_types: List[str]
    is_builtin: bool = False
    description: str = ""


class CorePredicateSystem:
    """Core predicate system functionality"""
    
    def __init__(self):
        self.predicates: Dict[str, PredicateDefinition] = {}
        self.predicate_hierarchy: Dict[str, Set[str]] = {}
        self.predicate_aliases: Dict[str, str] = {}
        
    def add_predicate(self, predicate: PredicateDefinition):
        """Add a predicate to the system"""
        key = f"{predicate.name}/{predicate.arity}"
        self.predicates[key] = predicate
        
    def get_predicate(self, name: str, arity: int) -> Optional[PredicateDefinition]:
        """Get a predicate by name and arity"""
        key = f"{name}/{arity}"
        return self.predicates.get(key)
        
    def list_predicates(self) -> List[PredicateDefinition]:
        """List all predicates"""
        return list(self.predicates.values())
        
    def add_hierarchy(self, parent: str, child: str):
        """Add hierarchical relationship between predicates"""
        if parent not in self.predicate_hierarchy:
            self.predicate_hierarchy[parent] = set()
        self.predicate_hierarchy[parent].add(child)
        
    def add_alias(self, alias: str, target: str):
        """Add alias for predicate"""
        self.predicate_aliases[alias] = target