"""
Progol (Programmable Goal-directed induction) Implementation
Based on: Muggleton (1995) "Inverse entailment and Progol"

Progol uses inverse entailment to construct the most specific clause
that entails a positive example, then searches for generalizations.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Set, Any
from dataclasses import dataclass, field
import logging
from itertools import product, combinations

from .ilp_core import (
    LogicalTerm, LogicalAtom, LogicalClause, Example,
    InductiveLogicProgrammer
)

@dataclass
class ProgolSettings:
    """Configuration settings for Progol"""
    max_clause_length: int = 6
    max_variables: int = 4
    noise_level: float = 0.0
    compression_threshold: int = 2
    evalfn_threshold: float = 0.5
    search_depth: int = 3
    beam_width: int = 5
    
@dataclass
class ProgolStatistics:
    """Statistics for Progol learning process"""
    most_specific_clauses_generated: int = 0
    generalizations_tested: int = 0
    compression_calculations: int = 0
    inverse_entailments: int = 0
    final_accuracy: float = 0.0
    total_compression: int = 0

class ProgolSystem:
    """
    Progol (Programmable Goal-directed induction) system
    
    Key features of Progol:
    1. Inverse Entailment: Construct most specific clause from examples
    2. Mode Declarations: Constrain the search space using mode specifications
    3. Compression-based Evaluation: Select clauses that compress the data
    4. Bottom Clause Construction: Build maximally specific clauses
    5. Generalization Search: Find good generalizations of bottom clause
    """
    
    def __init__(self, settings: Optional[ProgolSettings] = None):
        """
        Initialize Progol system
        
        Args:
            settings: Configuration settings for Progol
        """
        self.settings = settings or ProgolSettings()
        
        # Learning state
        self.background_knowledge = []
        self.positive_examples = []
        self.negative_examples = []
        self.mode_declarations = {}  # predicate -> mode specification
        self.learned_clauses = []
        
        # Vocabulary
        self.predicates = set()
        self.constants = set()
        self.functions = set()
        
        # Statistics
        self.stats = ProgolStatistics()
        
        print(f"✓ Progol System initialized:")
        print(f"   Max clause length: {self.settings.max_clause_length}")
        print(f"   Compression threshold: {self.settings.compression_threshold}")
        print(f"   Search depth: {self.settings.search_depth}")
    
    def add_mode_declaration(self, predicate: str, modes: List[str]):
        """
        Add mode declaration for predicate
        
        Args:
            predicate: Predicate name
            modes: List of mode specifications ('+' = input, '-' = output, '#' = constant)
        """
        self.mode_declarations[predicate] = modes
        print(f"   Added mode for {predicate}: {modes}")
    
    def add_background_knowledge(self, clause: LogicalClause):
        """Add background knowledge clause"""
        self.background_knowledge.append(clause)
        self._update_vocabulary_from_clause(clause)
        print(f"   Added background: {clause}")
    
    def add_example(self, atom: LogicalAtom, is_positive: bool):
        """Add training example"""
        example = Example(atom=atom, is_positive=is_positive)
        
        if is_positive:
            self.positive_examples.append(example)
        else:
            self.negative_examples.append(example)
            
        self._update_vocabulary_from_atom(atom)
        
        sign = "+" if is_positive else "-"
        print(f"   Added example: {sign} {atom}")
    
    def learn_rules(self, target_predicate: str) -> List[LogicalClause]:
        """
        Learn rules using Progol's inverse entailment approach
        
        Args:
            target_predicate: Predicate to learn rules for
            
        Returns:
            List of learned clauses
        """
        print(f"\n🧠 Progol Learning rules for predicate: {target_predicate}")
        
        # Get examples for target predicate
        pos_examples = [ex for ex in self.positive_examples 
                       if ex.atom.predicate == target_predicate]
        neg_examples = [ex for ex in self.negative_examples 
                       if ex.atom.predicate == target_predicate]
        
        print(f"   Examples: {len(pos_examples)} positive, {len(neg_examples)} negative")
        
        if not pos_examples:
            print("   No positive examples found!")
            return []
        
        learned_rules = []
        
        # For each positive example, attempt to learn a clause
        for i, pos_example in enumerate(pos_examples):
            print(f"\n   Processing positive example {i+1}: {pos_example.atom}")
            
            # Step 1: Construct bottom clause using inverse entailment
            bottom_clause = self._construct_bottom_clause(pos_example, target_predicate)
            
            if bottom_clause is None:
                print("   Could not construct bottom clause")
                continue
            
            print(f"   Bottom clause: {bottom_clause}")
            
            # Step 2: Search for good generalizations of bottom clause
            generalizations = self._search_generalizations(bottom_clause, pos_examples, neg_examples)
            
            # Step 3: Select best clause based on compression
            best_clause = self._select_best_clause(generalizations, pos_examples, neg_examples)
            
            if best_clause is not None:
                learned_rules.append(best_clause)
                print(f"   Learned clause: {best_clause}")
        
        # Remove redundant clauses
        final_rules = self._remove_redundant_clauses(learned_rules)
        self.learned_clauses = final_rules
        
        # Calculate statistics
        self._calculate_accuracy(final_rules, pos_examples, neg_examples)
        
        print(f"\n✓ Progol learned {len(final_rules)} rules")
        return final_rules
    
    def _construct_bottom_clause(self, pos_example: Example, target_predicate: str) -> Optional[LogicalClause]:
        """
        Construct bottom clause using inverse entailment
        
        The bottom clause is the most specific clause that, together with
        background knowledge, entails the positive example.
        """
        self.stats.most_specific_clauses_generated += 1
        self.stats.inverse_entailments += 1
        
        # Start with the positive example as head
        head = pos_example.atom
        
        # Create variable mapping
        variable_mapping = {}
        var_counter = 0
        
        # Convert constants in head to variables for generalization
        head_terms = []
        for term in head.terms:
            if term.term_type == 'constant':
                if term.name not in variable_mapping:
                    variable_mapping[term.name] = LogicalTerm(
                        name=f"V{var_counter}", 
                        term_type='variable'
                    )
                    var_counter += 1
                head_terms.append(variable_mapping[term.name])
            else:
                head_terms.append(term)
        
        generalized_head = LogicalAtom(predicate=head.predicate, terms=head_terms)
        
        # Construct body literals from background knowledge
        body_literals = []
        
        # Add literals that are related to the constants in the example
        example_constants = set()
        for term in pos_example.atom.terms:
            if term.term_type == 'constant':
                example_constants.add(term.name)
        
        # Generate literals using mode declarations
        for bg_clause in self.background_knowledge:
            if len(body_literals) >= self.settings.max_clause_length:
                break
                
            # Check if background knowledge is relevant to example
            bg_constants = set()
            for atom in [bg_clause.head] + bg_clause.body:
                for term in atom.terms:
                    if term.term_type == 'constant':
                        bg_constants.add(term.name)
            
            # If background knowledge shares constants with example, it's relevant
            if example_constants & bg_constants:
                # Add literals from background knowledge
                for atom in bg_clause.body:
                    if len(body_literals) < self.settings.max_clause_length:
                        # Convert to use variables from mapping
                        literal_terms = []
                        for term in atom.terms:
                            if term.term_type == 'constant' and term.name in variable_mapping:
                                literal_terms.append(variable_mapping[term.name])
                            else:
                                literal_terms.append(term)
                        
                        literal = LogicalAtom(
                            predicate=atom.predicate,
                            terms=literal_terms,
                            negated=atom.negated
                        )
                        
                        if literal not in body_literals:
                            body_literals.append(literal)
        
        # Add mode-based literals
        for predicate, modes in self.mode_declarations.items():
            if predicate == target_predicate:
                continue  # Don't add recursive calls
                
            if len(body_literals) >= self.settings.max_clause_length:
                break
            
            # Generate literal based on mode declaration
            mode_literal = self._generate_mode_literal(predicate, modes, variable_mapping)
            if mode_literal and mode_literal not in body_literals:
                body_literals.append(mode_literal)
        
        if not body_literals:
            # Create a simple body with basic predicates
            for predicate in list(self.predicates)[:3]:
                if predicate != target_predicate:
                    # Create simple binary literal
                    if len(head_terms) >= 2:
                        simple_literal = LogicalAtom(
                            predicate=predicate,
                            terms=head_terms[:2]
                        )
                        body_literals.append(simple_literal)
                        break
        
        if not body_literals:
            return None
        
        bottom_clause = LogicalClause(head=generalized_head, body=body_literals[:self.settings.max_clause_length])
        return bottom_clause
    
    def _generate_mode_literal(self, predicate: str, modes: List[str], 
                              variable_mapping: Dict[str, LogicalTerm]) -> Optional[LogicalAtom]:
        """Generate literal based on mode declaration"""
        terms = []
        variables = list(variable_mapping.values())
        
        for i, mode in enumerate(modes):
            if mode == '+':  # Input variable
                if i < len(variables):
                    terms.append(variables[i])
                else:
                    return None
            elif mode == '-':  # Output variable (new variable)
                new_var = LogicalTerm(name=f"V{len(variable_mapping)}", term_type='variable')
                terms.append(new_var)
            elif mode == '#':  # Constant
                # Use a constant from the domain
                if self.constants:
                    const_name = list(self.constants)[0]
                    const_term = LogicalTerm(name=const_name, term_type='constant')
                    terms.append(const_term)
                else:
                    return None
        
        if terms:
            return LogicalAtom(predicate=predicate, terms=terms)
        
        return None
    
    def _search_generalizations(self, bottom_clause: LogicalClause,
                              pos_examples: List[Example],
                              neg_examples: List[Example]) -> List[LogicalClause]:
        """
        Search for good generalizations of bottom clause using beam search
        """
        self.stats.generalizations_tested += 1
        
        # Start with bottom clause
        beam = [bottom_clause]
        all_generalizations = [bottom_clause]
        
        # Beam search for generalizations
        for depth in range(self.settings.search_depth):
            new_beam = []
            
            for clause in beam:
                # Generate generalizations by removing literals
                generalizations = self._generate_generalizations(clause)
                
                for gen_clause in generalizations:
                    # Evaluate generalization
                    score = self._evaluate_clause(gen_clause, pos_examples, neg_examples)
                    
                    if score > self.settings.evalfn_threshold:
                        new_beam.append((gen_clause, score))
                        all_generalizations.append(gen_clause)
            
            # Select top clauses for next iteration
            new_beam.sort(key=lambda x: x[1], reverse=True)
            beam = [clause for clause, score in new_beam[:self.settings.beam_width]]
            
            if not beam:
                break
        
        return all_generalizations
    
    def _generate_generalizations(self, clause: LogicalClause) -> List[LogicalClause]:
        """Generate generalizations by removing literals"""
        generalizations = []
        
        if len(clause.body) <= 1:
            return []
        
        # Remove each literal to create generalizations
        for i in range(len(clause.body)):
            new_body = clause.body[:i] + clause.body[i+1:]
            gen_clause = LogicalClause(head=clause.head, body=new_body)
            generalizations.append(gen_clause)
        
        # Remove pairs of literals
        if len(clause.body) >= 2:
            for i, j in combinations(range(len(clause.body)), 2):
                new_body = [lit for k, lit in enumerate(clause.body) if k not in (i, j)]
                gen_clause = LogicalClause(head=clause.head, body=new_body)
                generalizations.append(gen_clause)
        
        return generalizations
    
    def _evaluate_clause(self, clause: LogicalClause,
                        pos_examples: List[Example],
                        neg_examples: List[Example]) -> float:
        """
        Evaluate clause using Progol's compression-based evaluation
        
        Compression = (Pos covered) - (Neg covered) - (Clause length)
        """
        pos_covered = sum(1 for ex in pos_examples if self._clause_covers_example(clause, ex))
        neg_covered = sum(1 for ex in neg_examples if self._clause_covers_example(clause, ex))
        
        compression = pos_covered - neg_covered - len(clause.body)
        self.stats.compression_calculations += 1
        
        # Normalize to [0, 1] range
        max_possible = len(pos_examples) - len(clause.body)
        if max_possible <= 0:
            return 0.0
        
        return max(0, compression) / max_possible
    
    def _select_best_clause(self, clauses: List[LogicalClause],
                           pos_examples: List[Example],
                           neg_examples: List[Example]) -> Optional[LogicalClause]:
        """Select the best clause based on compression"""
        if not clauses:
            return None
        
        best_clause = None
        best_compression = -float('inf')
        
        for clause in clauses:
            pos_covered = sum(1 for ex in pos_examples if self._clause_covers_example(clause, ex))
            neg_covered = sum(1 for ex in neg_examples if self._clause_covers_example(clause, ex))
            
            compression = pos_covered - neg_covered - len(clause.body)
            
            if compression > best_compression and compression >= self.settings.compression_threshold:
                best_compression = compression
                best_clause = clause
        
        if best_clause:
            best_clause.confidence = self._calculate_confidence(best_clause, pos_examples, neg_examples)
            self.stats.total_compression += int(best_compression)
        
        return best_clause
    
    def _calculate_confidence(self, clause: LogicalClause,
                            pos_examples: List[Example],
                            neg_examples: List[Example]) -> float:
        """Calculate confidence (precision) of clause"""
        pos_covered = sum(1 for ex in pos_examples if self._clause_covers_example(clause, ex))
        neg_covered = sum(1 for ex in neg_examples if self._clause_covers_example(clause, ex))
        
        total_covered = pos_covered + neg_covered
        if total_covered == 0:
            return 0.0
        
        return pos_covered / total_covered
    
    def _clause_covers_example(self, clause: LogicalClause, example: Example) -> bool:
        """Check if clause covers example (simplified unification)"""
        # Try to unify clause head with example atom
        substitution = {}
        if not self._unify_atoms(clause.head, example.atom, substitution):
            return False
        
        # For simplicity, assume body literals are satisfied
        # In full implementation, this would involve resolution
        return True
    
    def _unify_atoms(self, atom1: LogicalAtom, atom2: LogicalAtom, 
                    substitution: Dict[str, LogicalTerm]) -> bool:
        """Simple unification of atoms"""
        if atom1.predicate != atom2.predicate or len(atom1.terms) != len(atom2.terms):
            return False
        
        for term1, term2 in zip(atom1.terms, atom2.terms):
            if not self._unify_terms(term1, term2, substitution):
                return False
        
        return True
    
    def _unify_terms(self, term1: LogicalTerm, term2: LogicalTerm,
                    substitution: Dict[str, LogicalTerm]) -> bool:
        """Simple term unification"""
        if term1.term_type == 'variable':
            if term1.name in substitution:
                return self._unify_terms(substitution[term1.name], term2, substitution)
            else:
                substitution[term1.name] = term2
                return True
        elif term2.term_type == 'variable':
            if term2.name in substitution:
                return self._unify_terms(term1, substitution[term2.name], substitution)
            else:
                substitution[term2.name] = term1
                return True
        else:
            return term1.name == term2.name and term1.term_type == term2.term_type
    
    def _remove_redundant_clauses(self, clauses: List[LogicalClause]) -> List[LogicalClause]:
        """Remove redundant or subsumed clauses"""
        if len(clauses) <= 1:
            return clauses
        
        non_redundant = []
        
        for clause in clauses:
            is_redundant = False
            
            # Check if this clause is subsumed by any existing clause
            for existing in non_redundant:
                if self._subsumes(existing, clause):
                    is_redundant = True
                    break
            
            if not is_redundant:
                # Remove any existing clauses that this one subsumes
                non_redundant = [existing for existing in non_redundant 
                               if not self._subsumes(clause, existing)]
                non_redundant.append(clause)
        
        return non_redundant
    
    def _subsumes(self, clause1: LogicalClause, clause2: LogicalClause) -> bool:
        """Check if clause1 subsumes clause2 (simplified)"""
        # Simplified subsumption: clause1 subsumes clause2 if clause1 is more general
        # Real subsumption involves theta-subsumption checking
        
        if len(clause1.body) > len(clause2.body):
            return False  # More specific clause can't subsume more general one
        
        # Check if all literals in clause1 appear in clause2 (simplified)
        for lit1 in clause1.body:
            found = False
            for lit2 in clause2.body:
                if lit1.predicate == lit2.predicate:
                    found = True
                    break
            if not found:
                return False
        
        return True
    
    def _update_vocabulary_from_clause(self, clause: LogicalClause):
        """Update vocabulary from clause"""
        self.predicates.add(clause.head.predicate)
        for atom in clause.body:
            self.predicates.add(atom.predicate)
            for term in atom.terms:
                if term.term_type == 'constant':
                    self.constants.add(term.name)
    
    def _update_vocabulary_from_atom(self, atom: LogicalAtom):
        """Update vocabulary from atom"""
        self.predicates.add(atom.predicate)
        for term in atom.terms:
            if term.term_type == 'constant':
                self.constants.add(term.name)
    
    def _calculate_accuracy(self, rules: List[LogicalClause],
                          pos_examples: List[Example],
                          neg_examples: List[Example]):
        """Calculate final accuracy"""
        correct = 0
        total = len(pos_examples) + len(neg_examples)
        
        # Check positive examples
        for example in pos_examples:
            covered = any(self._clause_covers_example(rule, example) for rule in rules)
            if covered:
                correct += 1
        
        # Check negative examples
        for example in neg_examples:
            covered = any(self._clause_covers_example(rule, example) for rule in rules)
            if not covered:  # Correctly rejected
                correct += 1
        
        self.stats.final_accuracy = correct / total if total > 0 else 0.0
        print(f"   Final accuracy: {self.stats.final_accuracy:.3f}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get learning statistics"""
        return {
            "algorithm": "Progol",
            "most_specific_clauses": self.stats.most_specific_clauses_generated,
            "generalizations_tested": self.stats.generalizations_tested,
            "compression_calculations": self.stats.compression_calculations,
            "inverse_entailments": self.stats.inverse_entailments,
            "final_accuracy": self.stats.final_accuracy,
            "total_compression": self.stats.total_compression,
            "learned_clauses": len(self.learned_clauses),
            "compression_threshold": self.settings.compression_threshold,
            "search_depth": self.settings.search_depth
        }


# Utility functions
def create_progol_system(compression_threshold: int = 2, 
                        search_depth: int = 3) -> ProgolSystem:
    """
    Create a Progol system with common settings
    
    Args:
        compression_threshold: Minimum compression for clause acceptance
        search_depth: Depth of generalization search
        
    Returns:
        Configured ProgolSystem
    """
    settings = ProgolSettings(
        compression_threshold=compression_threshold,
        search_depth=search_depth,
        beam_width=5,
        max_clause_length=6
    )
    
    return ProgolSystem(settings)


# Example usage
if __name__ == "__main__":
    print("🧠 Progol (Programmable Goal-directed induction) - Muggleton 1995")
    print("=" * 65)
    
    # Create Progol system
    progol = ProgolSystem()
    
    # Add mode declarations
    progol.add_mode_declaration('parent', ['+', '+'])  # Both arguments are input
    progol.add_mode_declaration('male', ['+'])         # Input argument
    progol.add_mode_declaration('female', ['+'])       # Input argument
    
    # Add background knowledge
    alice_term = LogicalTerm(name='alice', term_type='constant')
    bob_term = LogicalTerm(name='bob', term_type='constant')
    
    # Add examples
    parent_alice_bob = LogicalAtom(predicate='parent', terms=[alice_term, bob_term])
    progol.add_example(parent_alice_bob, True)
    
    # Learn rules
    learned_rules = progol.learn_rules('parent')
    
    print(f"\nLearned {len(learned_rules)} rules:")
    for i, rule in enumerate(learned_rules):
        print(f"  {i+1}. {rule}")
    
    # Print statistics
    stats = progol.get_statistics()
    print(f"\nProgol Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")