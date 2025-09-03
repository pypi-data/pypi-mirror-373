"""
🏗️ LOGICAL STRUCTURES MODULE - Core Data Structures for ILP
===========================================================

This module provides the fundamental logical data structures for Inductive Logic
Programming, including terms, atoms, clauses, and examples. These form the
foundation for all logical reasoning operations.

Based on Muggleton & De Raedt (1994) "Inductive Logic Programming: Theory and Methods"

Key Features:
- Logical terms (constants, variables, functions)
- Logical atoms (predicates with arguments)
- Horn clauses (head :- body structure)
- Training examples (positive/negative)
- String representations and utilities

Author: Benedict Chen
"""

from dataclasses import dataclass
from typing import List, Optional, Any, Union


@dataclass
class LogicalTerm:
    """
    🔤 Represents a logical term in first-order logic
    
    Terms are the basic building blocks of logical expressions:
    - Constants: specific objects (e.g., 'john', 'mary', 5)
    - Variables: placeholders for objects (e.g., X, Y, Z)
    - Functions: structured terms with arguments (e.g., father(john))
    
    Examples:
        LogicalTerm('john', 'constant')           # constant term
        LogicalTerm('X', 'variable')              # variable term
        LogicalTerm('plus', 'function', [x, y])   # function term plus(X, Y)
    """
    name: str
    term_type: str  # 'constant', 'variable', 'function'
    arguments: Optional[List['LogicalTerm']] = None
    
    def __post_init__(self):
        """Validate term structure"""
        valid_types = {'constant', 'variable', 'function'}
        if self.term_type not in valid_types:
            raise ValueError(f"Invalid term type '{self.term_type}'. Must be one of {valid_types}")
        
        if self.term_type == 'function' and not self.arguments:
            raise ValueError("Function terms must have arguments")
        
        if self.term_type != 'function' and self.arguments:
            raise ValueError(f"{self.term_type} terms cannot have arguments")
    
    def __str__(self):
        """String representation of the logical term"""
        if self.term_type == 'function' and self.arguments:
            args_str = ", ".join(str(arg) for arg in self.arguments)
            return f"{self.name}({args_str})"
        return self.name
    
    def __repr__(self):
        """Detailed string representation"""
        if self.arguments:
            return f"LogicalTerm('{self.name}', '{self.term_type}', {self.arguments})"
        return f"LogicalTerm('{self.name}', '{self.term_type}')"
    
    def __eq__(self, other):
        """Equality comparison for terms"""
        if not isinstance(other, LogicalTerm):
            return False
        return (self.name == other.name and 
                self.term_type == other.term_type and
                self.arguments == other.arguments)
    
    def __hash__(self):
        """Hash function for use in sets and dictionaries"""
        args_tuple = tuple(self.arguments) if self.arguments else None
        return hash((self.name, self.term_type, args_tuple))
    
    def is_variable(self) -> bool:
        """Check if this term is a variable"""
        return self.term_type == 'variable'
    
    def is_constant(self) -> bool:
        """Check if this term is a constant"""
        return self.term_type == 'constant'
    
    def is_function(self) -> bool:
        """Check if this term is a function"""
        return self.term_type == 'function'
    
    def get_variables(self) -> set:
        """Get all variables appearing in this term"""
        variables = set()
        if self.is_variable():
            variables.add(self.name)
        elif self.is_function() and self.arguments:
            for arg in self.arguments:
                variables.update(arg.get_variables())
        return variables
    
    def substitute_variables(self, substitution: dict) -> 'LogicalTerm':
        """Apply variable substitution to this term"""
        if self.is_variable() and self.name in substitution:
            return substitution[self.name]
        elif self.is_function() and self.arguments:
            new_args = [arg.substitute_variables(substitution) for arg in self.arguments]
            return LogicalTerm(self.name, 'function', new_args)
        else:
            return self
    
    def complexity(self) -> int:
        """Calculate structural complexity of the term"""
        if self.is_function() and self.arguments:
            return 1 + sum(arg.complexity() for arg in self.arguments)
        return 1


@dataclass  
class LogicalAtom:
    """
    ⚛️ Represents a logical atom (predicate applied to terms)
    
    Atoms are the basic statements in first-order logic, consisting of:
    - Predicate: the relation or property name
    - Terms: the arguments to the predicate
    - Negation: whether the atom is negated
    
    Examples:
        LogicalAtom('father', [john, mary])       # father(john, mary)
        LogicalAtom('male', [X], negated=True)    # ¬male(X)
    """
    predicate: str
    terms: List[LogicalTerm]
    negated: bool = False
    
    def __post_init__(self):
        """Validate atom structure"""
        if not isinstance(self.terms, list):
            raise ValueError("Terms must be a list")
        
        for term in self.terms:
            if not isinstance(term, LogicalTerm):
                raise ValueError("All terms must be LogicalTerm instances")
    
    def __str__(self):
        """String representation of the logical atom"""
        terms_str = ", ".join(str(term) for term in self.terms)
        atom_str = f"{self.predicate}({terms_str})"
        return f"¬{atom_str}" if self.negated else atom_str
    
    def __repr__(self):
        """Detailed string representation"""
        return f"LogicalAtom('{self.predicate}', {self.terms}, negated={self.negated})"
    
    def __eq__(self, other):
        """Equality comparison for atoms"""
        if not isinstance(other, LogicalAtom):
            return False
        return (self.predicate == other.predicate and
                self.terms == other.terms and
                self.negated == other.negated)
    
    def __hash__(self):
        """Hash function for use in sets and dictionaries"""
        return hash((self.predicate, tuple(self.terms), self.negated))
    
    def arity(self) -> int:
        """Get the arity (number of arguments) of this atom"""
        return len(self.terms)
    
    def get_variables(self) -> set:
        """Get all variables appearing in this atom"""
        variables = set()
        for term in self.terms:
            variables.update(term.get_variables())
        return variables
    
    def substitute_variables(self, substitution: dict) -> 'LogicalAtom':
        """Apply variable substitution to this atom"""
        new_terms = [term.substitute_variables(substitution) for term in self.terms]
        return LogicalAtom(self.predicate, new_terms, self.negated)
    
    def negate(self) -> 'LogicalAtom':
        """Return the negation of this atom"""
        return LogicalAtom(self.predicate, self.terms, not self.negated)
    
    def matches_signature(self, other: 'LogicalAtom') -> bool:
        """Check if this atom has the same predicate and arity as another"""
        return (self.predicate == other.predicate and 
                len(self.terms) == len(other.terms))
    
    def complexity(self) -> int:
        """Calculate structural complexity of the atom"""
        return 1 + sum(term.complexity() for term in self.terms)


@dataclass
class LogicalClause:
    """
    📜 Represents a logical clause (Horn clause: head :- body)
    
    Clauses are the fundamental units of logic programming, consisting of:
    - Head: single atom that is concluded
    - Body: list of atoms that must be proven
    - Confidence: statistical measure of rule reliability
    
    Examples:
        LogicalClause(father(X,Y), [parent(X,Y), male(X)])  # father(X,Y) :- parent(X,Y), male(X)
        LogicalClause(male(john), [])                        # male(john). (fact)
    """
    head: LogicalAtom
    body: List[LogicalAtom]
    confidence: float = 1.0
    
    def __post_init__(self):
        """Validate clause structure"""
        if not isinstance(self.head, LogicalAtom):
            raise ValueError("Head must be a LogicalAtom")
        
        if not isinstance(self.body, list):
            raise ValueError("Body must be a list")
        
        for atom in self.body:
            if not isinstance(atom, LogicalAtom):
                raise ValueError("All body atoms must be LogicalAtom instances")
        
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
    
    def __str__(self):
        """String representation of the logical clause"""
        if not self.body:
            return str(self.head)
        body_str = ", ".join(str(atom) for atom in self.body)
        confidence_str = f" [{self.confidence:.3f}]" if self.confidence < 1.0 else ""
        return f"{self.head} :- {body_str}{confidence_str}"
    
    def __repr__(self):
        """Detailed string representation"""
        return f"LogicalClause({self.head}, {self.body}, confidence={self.confidence})"
    
    def __eq__(self, other):
        """Equality comparison for clauses"""
        if not isinstance(other, LogicalClause):
            return False
        return (self.head == other.head and
                self.body == other.body and
                abs(self.confidence - other.confidence) < 1e-6)
    
    def __hash__(self):
        """Hash function for use in sets and dictionaries"""
        return hash((self.head, tuple(self.body), round(self.confidence, 6)))
    
    def is_fact(self) -> bool:
        """Check if this clause is a fact (no body)"""
        return len(self.body) == 0
    
    def is_rule(self) -> bool:
        """Check if this clause is a rule (has body)"""
        return len(self.body) > 0
    
    def arity(self) -> int:
        """Get the arity of the head predicate"""
        return self.head.arity()
    
    def length(self) -> int:
        """Get the length of the clause (number of body atoms)"""
        return len(self.body)
    
    def get_variables(self) -> set:
        """Get all variables appearing in this clause"""
        variables = set()
        variables.update(self.head.get_variables())
        for atom in self.body:
            variables.update(atom.get_variables())
        return variables
    
    def substitute_variables(self, substitution: dict) -> 'LogicalClause':
        """Apply variable substitution to this clause"""
        new_head = self.head.substitute_variables(substitution)
        new_body = [atom.substitute_variables(substitution) for atom in self.body]
        return LogicalClause(new_head, new_body, self.confidence)
    
    def add_body_atom(self, atom: LogicalAtom) -> 'LogicalClause':
        """Add an atom to the body, returning a new clause"""
        new_body = self.body + [atom]
        return LogicalClause(self.head, new_body, self.confidence)
    
    def remove_body_atom(self, index: int) -> 'LogicalClause':
        """Remove a body atom at given index, returning a new clause"""
        if 0 <= index < len(self.body):
            new_body = self.body[:index] + self.body[index+1:]
            return LogicalClause(self.head, new_body, self.confidence)
        return self
    
    def complexity(self) -> int:
        """Calculate structural complexity of the clause"""
        head_complexity = self.head.complexity()
        body_complexity = sum(atom.complexity() for atom in self.body)
        return head_complexity + body_complexity
    
    def get_predicates(self) -> set:
        """Get all predicates used in this clause"""
        predicates = {self.head.predicate}
        for atom in self.body:
            predicates.add(atom.predicate)
        return predicates


@dataclass
class Example:
    """
    📚 Represents a training example (positive or negative)
    
    Examples are the training data for ILP, consisting of:
    - Atom: the logical statement to be learned
    - Is_positive: whether this is a positive or negative example
    
    Examples:
        Example(father(john, mary), True)   # Positive: john is mary's father
        Example(father(mary, john), False)  # Negative: mary is NOT john's father
    """
    atom: LogicalAtom
    is_positive: bool
    
    def __post_init__(self):
        """Validate example structure"""
        if not isinstance(self.atom, LogicalAtom):
            raise ValueError("Atom must be a LogicalAtom instance")
        
        if not isinstance(self.is_positive, bool):
            raise ValueError("is_positive must be a boolean")
    
    def __str__(self):
        """String representation of the example"""
        sign = "+" if self.is_positive else "-"
        return f"{sign} {self.atom}"
    
    def __repr__(self):
        """Detailed string representation"""
        return f"Example({self.atom}, is_positive={self.is_positive})"
    
    def __eq__(self, other):
        """Equality comparison for examples"""
        if not isinstance(other, Example):
            return False
        return (self.atom == other.atom and 
                self.is_positive == other.is_positive)
    
    def __hash__(self):
        """Hash function for use in sets and dictionaries"""
        return hash((self.atom, self.is_positive))
    
    def negate(self) -> 'Example':
        """Return the negation of this example"""
        return Example(self.atom, not self.is_positive)
    
    def get_predicate(self) -> str:
        """Get the predicate of this example"""
        return self.atom.predicate
    
    def get_variables(self) -> set:
        """Get all variables in this example"""
        return self.atom.get_variables()
    
    def substitute_variables(self, substitution: dict) -> 'Example':
        """Apply variable substitution to this example"""
        new_atom = self.atom.substitute_variables(substitution)
        return Example(new_atom, self.is_positive)


# Utility functions for working with logical structures

def create_variable(name: str) -> LogicalTerm:
    """Convenience function to create a variable term"""
    return LogicalTerm(name, 'variable')

def create_constant(name: str) -> LogicalTerm:
    """Convenience function to create a constant term"""
    return LogicalTerm(name, 'constant')

def create_function(name: str, args: List[LogicalTerm]) -> LogicalTerm:
    """Convenience function to create a function term"""
    return LogicalTerm(name, 'function', args)

def create_atom(predicate: str, terms: List[LogicalTerm], negated: bool = False) -> LogicalAtom:
    """Convenience function to create an atom"""
    return LogicalAtom(predicate, terms, negated)

def create_fact(head: LogicalAtom, confidence: float = 1.0) -> LogicalClause:
    """Convenience function to create a fact (clause with no body)"""
    return LogicalClause(head, [], confidence)

def create_rule(head: LogicalAtom, body: List[LogicalAtom], confidence: float = 1.0) -> LogicalClause:
    """Convenience function to create a rule"""
    return LogicalClause(head, body, confidence)

def parse_term(term_str: str) -> LogicalTerm:
    """Simple parser for term strings (basic implementation)"""
    term_str = term_str.strip()
    
    # Check if it's a function term (contains parentheses)
    if '(' in term_str and term_str.endswith(')'):
        func_name = term_str[:term_str.index('(')]
        args_str = term_str[term_str.index('(') + 1:-1]
        
        # Parse arguments
        args = []
        if args_str.strip():
            # Simple comma splitting (doesn't handle nested functions well)
            for arg_str in args_str.split(','):
                args.append(parse_term(arg_str.strip()))
        
        return create_function(func_name, args)
    
    # Check if it's a variable (starts with uppercase or '_')
    elif term_str[0].isupper() or term_str.startswith('_'):
        return create_variable(term_str)
    
    # Otherwise it's a constant
    else:
        return create_constant(term_str)

def variables_in_structures(*structures) -> set:
    """Get all variables from multiple logical structures"""
    variables = set()
    for structure in structures:
        if hasattr(structure, 'get_variables'):
            variables.update(structure.get_variables())
    return variables