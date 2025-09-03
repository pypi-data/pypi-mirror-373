"""
Rule Refinement for Inductive Logic Programming
Based on: Various ILP refinement operators and techniques from
         Muggleton & De Raedt (1994), Lavrac & Dzeroski (1994)

Implements refinement operators for systematic search through the
hypothesis space of logical clauses.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Set, Any, Iterator
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import logging

from .ilp_core import (
    LogicalTerm, LogicalAtom, LogicalClause, Example,
    InductiveLogicProgrammer
)

class RefinementType(Enum):
    """Types of refinement operations"""
    SPECIALIZATION = "specialization"     # Downward refinement (more specific)
    GENERALIZATION = "generalization"     # Upward refinement (more general)

@dataclass
class RefinementRule:
    """Rule for refinement operations"""
    name: str
    refinement_type: RefinementType
    operator_function: callable
    preconditions: List[callable] = field(default_factory=list)
    cost: float = 1.0
    description: str = ""

@dataclass
class RefinementStep:
    """Single step in refinement process"""
    original_clause: LogicalClause
    refined_clause: LogicalClause
    refinement_type: RefinementType
    operator_name: str
    cost: float
    improvement_score: float = 0.0

class RefinementOperator(ABC):
    """Abstract base class for refinement operators"""
    
    @abstractmethod
    def apply(self, clause: LogicalClause, **kwargs) -> List[LogicalClause]:
        """
        🎆 Apply Refinement Operator to Clause - Inductive Logic Programming!
        
        Applies the refinement operator to generate specialized versions of
        the input clause, following ILP refinement theory.
        
        Args:
            clause: Input logical clause to refine
            **kwargs: Additional parameters for refinement operation
            
        Returns:
            List[LogicalClause]: List of refined clauses (specializations)
            
        📚 **ILP Theory**: Refinement operators define the search space
        for hypothesis specialization in inductive learning.
        
        🔄 **Refinement Types**:
        - Add literal (specialization)
        - Add variable constraint  
        - Substitute terms
        - Apply theta-subsumption
        
        🎨 **Example**:
        ```python
        # Original: parent(X, Y) :- human(X)
        # Refined:  parent(X, Y) :- human(X), male(X)
        refined_clauses = operator.apply(original_clause)
        ```
        """
        # Default implementation - subclasses should override for specific operators
        # Return the original clause unchanged as a safe fallback
        if isinstance(clause, LogicalClause):
            return [clause]  # Return list for consistency
        else:
            # Convert to LogicalClause if needed
            return [LogicalClause(head=clause, body=[], variables=set())]
    
    @abstractmethod
    def can_apply(self, clause: LogicalClause) -> bool:
        """
        ✅ Check if Operator Can Be Applied - Refinement Applicability!
        
        Determines whether this refinement operator can be meaningfully
        applied to the given logical clause.
        
        Args:
            clause: Logical clause to test
            
        Returns:
            bool: True if operator is applicable, False otherwise
            
        🔍 **Applicability Checks**:
        - Clause structure compatibility
        - Variable/term requirements met
        - No redundant refinements
        - Within complexity limits
        
        ⚡ **Performance**: Fast pre-filtering to avoid expensive operations
        
        📈 **Usage**:
        ```python
        if operator.can_apply(clause):
            refined = operator.apply(clause)
        else:
            print("Operator not applicable")
        ```
        """
        # Default implementation - conservative applicability check
        # Subclasses should override for specific operator logic
        
        # Basic checks that apply to most refinement operators
        if not isinstance(clause, LogicalClause):
            return False
            
        # Check if clause has reasonable complexity for refinement
        max_body_length = getattr(self, 'max_body_length', 10)
        if len(clause.body) >= max_body_length:
            return False  # Too complex to refine further
            
        # Check if operator type matches clause structure
        operator_name = self.__class__.__name__.lower()
        
        if 'specialization' in operator_name:
            # Specialization operators can usually be applied if clause isn't too specific
            return len(clause.body) < max_body_length
        elif 'generalization' in operator_name:
            # Generalization operators need some body literals to remove
            return len(clause.body) > 0
        elif 'substitution' in operator_name:
            # Substitution operators need variables to substitute
            return len(clause.variables) > 0
            
        # Default: assume operator is applicable (conservative)
        return True
    
    @abstractmethod
    def get_cost(self) -> float:
        """
        💰 Get Cost of Applying Operator - ILP Search Economics!
        
        Returns the computational cost of applying this refinement operator,
        used for search prioritization and resource allocation.
        
        Returns:
            float: Cost value (higher = more expensive)
            
        📉 **Cost Factors**:
        - Computational complexity
        - Memory requirements
        - Expected search branching
        - Success probability
        
        🏆 **Search Strategy**:
        Lower cost operators are typically applied first in best-first
        search algorithms for efficient hypothesis space exploration.
        
        📊 **Cost Categories**:
        - Low (< 1.0): Simple literal additions
        - Medium (1.0-5.0): Variable substitutions
        - High (> 5.0): Complex structural changes
        """
        # Default implementation - cost based on operator complexity
        # Subclasses should override for specific cost models
        
        operator_name = self.__class__.__name__.lower()
        
        # Base costs by operator type (from ILP literature)
        if 'literal' in operator_name and 'add' in operator_name:
            return 0.5  # Adding literals is cheap
        elif 'literal' in operator_name and 'remove' in operator_name:
            return 0.8  # Removing literals is slightly more expensive
        elif 'specialization' in operator_name:
            return 1.0  # Specialization is medium cost
        elif 'generalization' in operator_name:
            return 2.0  # Generalization is more expensive
        elif 'substitution' in operator_name:
            return 1.5  # Variable substitution is medium-high cost
        elif 'predicate' in operator_name:
            return 3.0  # Predicate invention is expensive
        elif 'resolution' in operator_name:
            return 4.0  # Resolution is very expensive
        else:
            return 1.0  # Default medium cost

class SpecializationOperator(RefinementOperator):
    """Downward refinement operator (makes clauses more specific)"""
    
    def __init__(self, predicates: Set[str], constants: Set[str]):
        self.predicates = predicates
        self.constants = constants
    
    def apply(self, clause: LogicalClause, max_literals: int = 10) -> List[LogicalClause]:
        """Apply specialization by adding literals"""
        specializations = []
        
        if len(clause.body) >= max_literals:
            return specializations
        
        # Get variables from clause
        clause_vars = self._extract_variables(clause)
        
        # Generate new literals to add
        candidate_literals = self._generate_candidate_literals(clause_vars)
        
        for literal in candidate_literals:
            new_body = clause.body + [literal]
            specialized_clause = LogicalClause(
                head=clause.head,
                body=new_body,
                confidence=clause.confidence
            )
            specializations.append(specialized_clause)
        
        return specializations[:5]  # Limit number of specializations
    
    def can_apply(self, clause: LogicalClause) -> bool:
        """Check if we can specialize further"""
        return len(clause.body) < 10  # Arbitrary limit
    
    def get_cost(self) -> float:
        """Cost of specialization"""
        return 1.0
    
    def _extract_variables(self, clause: LogicalClause) -> Set[str]:
        """Extract variables from clause"""
        variables = set()
        
        for atom in [clause.head] + clause.body:
            for term in atom.terms:
                if term.term_type == 'variable':
                    variables.add(term.name)
        
        return variables
    
    def _generate_candidate_literals(self, clause_vars: Set[str]) -> List[LogicalAtom]:
        """Generate candidate literals for specialization"""
        candidates = []
        
        # Convert variables to terms
        var_terms = [LogicalTerm(name=var, term_type='variable') for var in clause_vars]
        
        # Add some constants
        const_terms = [LogicalTerm(name=const, term_type='constant') 
                      for const in list(self.constants)[:3]]
        
        all_terms = var_terms + const_terms
        
        # Generate literals with available predicates
        for predicate in list(self.predicates)[:5]:  # Limit predicates
            # Generate unary literals
            for term in all_terms[:3]:  # Limit terms
                literal = LogicalAtom(predicate=predicate, terms=[term])
                candidates.append(literal)
            
            # Generate binary literals
            if len(all_terms) >= 2:
                for i, term1 in enumerate(all_terms[:2]):
                    for term2 in all_terms[:2]:
                        if i != all_terms.index(term2):  # Avoid same term twice
                            literal = LogicalAtom(predicate=predicate, terms=[term1, term2])
                            candidates.append(literal)
        
        return candidates[:10]  # Limit candidates

class GeneralizationOperator(RefinementOperator):
    """Upward refinement operator (makes clauses more general)"""
    
    def apply(self, clause: LogicalClause) -> List[LogicalClause]:
        """Apply generalization by removing literals or substituting variables"""
        generalizations = []
        
        # Strategy 1: Remove literals from body
        if len(clause.body) > 0:
            for i in range(len(clause.body)):
                new_body = clause.body[:i] + clause.body[i+1:]
                generalized_clause = LogicalClause(
                    head=clause.head,
                    body=new_body,
                    confidence=clause.confidence
                )
                generalizations.append(generalized_clause)
        
        # Strategy 2: Variable substitution (unify variables)
        var_substitutions = self._generate_variable_substitutions(clause)
        for substitution in var_substitutions:
            generalized_clause = self._apply_substitution(clause, substitution)
            if generalized_clause:
                generalizations.append(generalized_clause)
        
        # Strategy 3: Replace constants with variables
        const_to_var = self._generate_constant_to_variable_substitutions(clause)
        for substitution in const_to_var:
            generalized_clause = self._apply_substitution(clause, substitution)
            if generalized_clause:
                generalizations.append(generalized_clause)
        
        return generalizations[:5]  # Limit generalizations
    
    def can_apply(self, clause: LogicalClause) -> bool:
        """Check if we can generalize further"""
        return len(clause.body) > 0 or self._has_constants_or_multiple_vars(clause)
    
    def get_cost(self) -> float:
        """Cost of generalization"""
        return 1.0
    
    def _has_constants_or_multiple_vars(self, clause: LogicalClause) -> bool:
        """Check if clause has constants or multiple variables that can be unified"""
        variables = set()
        has_constants = False
        
        for atom in [clause.head] + clause.body:
            for term in atom.terms:
                if term.term_type == 'variable':
                    variables.add(term.name)
                elif term.term_type == 'constant':
                    has_constants = True
        
        return has_constants or len(variables) > 1
    
    def _generate_variable_substitutions(self, clause: LogicalClause) -> List[Dict[str, str]]:
        """Generate variable unification substitutions"""
        variables = set()
        
        # Collect all variables
        for atom in [clause.head] + clause.body:
            for term in atom.terms:
                if term.term_type == 'variable':
                    variables.add(term.name)
        
        var_list = list(variables)
        substitutions = []
        
        # Generate pairwise variable unifications
        for i, var1 in enumerate(var_list):
            for var2 in var_list[i+1:]:
                # Unify var2 with var1 (replace var2 with var1)
                substitutions.append({var2: var1})
        
        return substitutions[:3]  # Limit substitutions
    
    def _generate_constant_to_variable_substitutions(self, clause: LogicalClause) -> List[Dict[str, str]]:
        """Generate substitutions that replace constants with variables"""
        constants = set()
        variables = set()
        
        # Collect constants and variables
        for atom in [clause.head] + clause.body:
            for term in atom.terms:
                if term.term_type == 'constant':
                    constants.add(term.name)
                elif term.term_type == 'variable':
                    variables.add(term.name)
        
        substitutions = []
        
        # Replace each constant with a new variable
        next_var_id = len(variables)
        for constant in list(constants)[:3]:  # Limit constants
            new_var_name = f"V{next_var_id}"
            substitutions.append({constant: new_var_name})
            next_var_id += 1
        
        return substitutions
    
    def _apply_substitution(self, clause: LogicalClause, substitution: Dict[str, str]) -> Optional[LogicalClause]:
        """Apply substitution to clause"""
        try:
            new_head = self._substitute_atom(clause.head, substitution)
            new_body = [self._substitute_atom(atom, substitution) for atom in clause.body]
            
            return LogicalClause(head=new_head, body=new_body, confidence=clause.confidence)
        except:
            return None
    
    def _substitute_atom(self, atom: LogicalAtom, substitution: Dict[str, str]) -> LogicalAtom:
        """Apply substitution to atom"""
        new_terms = []
        
        for term in atom.terms:
            if term.name in substitution:
                # Determine new term type
                if term.term_type == 'constant' and substitution[term.name].startswith('V'):
                    new_term = LogicalTerm(name=substitution[term.name], term_type='variable')
                else:
                    new_term = LogicalTerm(name=substitution[term.name], term_type=term.term_type)
            else:
                new_term = term
            
            new_terms.append(new_term)
        
        return LogicalAtom(predicate=atom.predicate, terms=new_terms, negated=atom.negated)

class ThetaSubsumptionRefinement(RefinementOperator):
    """Theta-subsumption based refinement operator"""
    
    def __init__(self, predicates: Set[str], constants: Set[str]):
        self.predicates = predicates
        self.constants = constants
    
    def apply(self, clause: LogicalClause, target_clauses: List[LogicalClause] = None) -> List[LogicalClause]:
        """Apply theta-subsumption refinement"""
        if target_clauses is None:
            target_clauses = []
        
        refinements = []
        
        # Generate more specific clauses that theta-subsume the original
        specializations = self._generate_theta_specializations(clause)
        
        # Generate more general clauses that are theta-subsumed by the original
        generalizations = self._generate_theta_generalizations(clause)
        
        refinements.extend(specializations)
        refinements.extend(generalizations)
        
        return refinements
    
    def can_apply(self, clause: LogicalClause) -> bool:
        """Always can apply theta-subsumption refinement"""
        return True
    
    def get_cost(self) -> float:
        """Cost of theta-subsumption refinement"""
        return 2.0
    
    def _generate_theta_specializations(self, clause: LogicalClause) -> List[LogicalClause]:
        """Generate theta-specializations"""
        specializations = []
        
        # Add literals (same as regular specialization)
        spec_op = SpecializationOperator(self.predicates, self.constants)
        if spec_op.can_apply(clause):
            specializations.extend(spec_op.apply(clause))
        
        return specializations
    
    def _generate_theta_generalizations(self, clause: LogicalClause) -> List[LogicalClause]:
        """Generate theta-generalizations"""
        generalizations = []
        
        # Remove literals and apply substitutions
        gen_op = GeneralizationOperator()
        if gen_op.can_apply(clause):
            generalizations.extend(gen_op.apply(clause))
        
        return generalizations

class RuleRefinement:
    """
    Rule refinement system for systematic hypothesis space search
    
    Implements various refinement operators and search strategies
    for improving learned rules through systematic refinement.
    """
    
    def __init__(self,
                 max_refinement_steps: int = 10,
                 beam_width: int = 5,
                 improvement_threshold: float = 0.1):
        """
        Initialize rule refinement system
        
        Args:
            max_refinement_steps: Maximum refinement iterations
            beam_width: Width of beam search
            improvement_threshold: Minimum improvement to continue refinement
        """
        self.max_refinement_steps = max_refinement_steps
        self.beam_width = beam_width
        self.improvement_threshold = improvement_threshold
        
        # Refinement operators
        self.operators = {}
        self.refinement_history = []
        
        # Statistics
        self.stats = {
            "refinements_applied": 0,
            "specializations": 0,
            "generalizations": 0,
            "theta_subsumptions": 0,
            "improvements_found": 0
        }
        
        print(f"✓ Rule Refinement System initialized:")
        print(f"   Max refinement steps: {max_refinement_steps}")
        print(f"   Beam width: {beam_width}")
        print(f"   Improvement threshold: {improvement_threshold}")
    
    def register_operator(self, name: str, operator: RefinementOperator):
        """Register a refinement operator"""
        self.operators[name] = operator
        print(f"   Registered operator: {name}")
    
    def refine_rule(self, initial_clause: LogicalClause,
                   positive_examples: List[Example],
                   negative_examples: List[Example],
                   predicates: Set[str],
                   constants: Set[str]) -> List[LogicalClause]:
        """
        Refine a rule using beam search with refinement operators
        
        Args:
            initial_clause: Starting clause to refine
            positive_examples: Positive training examples
            negative_examples: Negative training examples
            predicates: Available predicates
            constants: Available constants
            
        Returns:
            List of refined clauses
        """
        print(f"\n🔧 Refining rule: {initial_clause}")
        
        # Register default operators if not already registered
        if not self.operators:
            self._register_default_operators(predicates, constants)
        
        # Initialize beam with original clause
        beam = [(initial_clause, self._evaluate_clause(initial_clause, positive_examples, negative_examples))]
        best_clauses = [initial_clause]
        
        for step in range(self.max_refinement_steps):
            print(f"   Refinement step {step + 1}")
            
            new_candidates = []
            
            # Apply each operator to each clause in beam
            for clause, score in beam:
                for op_name, operator in self.operators.items():
                    if operator.can_apply(clause):
                        refinements = operator.apply(clause)
                        
                        for refined_clause in refinements:
                            new_score = self._evaluate_clause(refined_clause, positive_examples, negative_examples)
                            
                            # Record refinement step
                            refinement_step = RefinementStep(
                                original_clause=clause,
                                refined_clause=refined_clause,
                                refinement_type=self._get_operator_type(op_name),
                                operator_name=op_name,
                                cost=operator.get_cost(),
                                improvement_score=new_score - score
                            )
                            
                            self.refinement_history.append(refinement_step)
                            self.stats["refinements_applied"] += 1
                            
                            if refinement_step.improvement_score > self.improvement_threshold:
                                self.stats["improvements_found"] += 1
                            
                            new_candidates.append((refined_clause, new_score))
            
            if not new_candidates:
                print("   No more refinements possible")
                break
            
            # Select best candidates for next iteration
            new_candidates.sort(key=lambda x: x[1], reverse=True)
            beam = new_candidates[:self.beam_width]
            
            # Update best clauses
            for clause, score in beam[:3]:  # Keep top 3
                if clause not in best_clauses:
                    best_clauses.append(clause)
            
            print(f"   Generated {len(new_candidates)} candidates")
            print(f"   Best score: {beam[0][1]:.3f}")
            
            # Check for convergence
            if all(score < self.improvement_threshold for _, score in beam):
                print("   Convergence reached")
                break
        
        # Sort final results by score
        final_results = []
        for clause in best_clauses:
            score = self._evaluate_clause(clause, positive_examples, negative_examples)
            final_results.append((clause, score))
        
        final_results.sort(key=lambda x: x[1], reverse=True)
        
        print(f"✓ Refinement completed: {len(final_results)} refined clauses")
        return [clause for clause, score in final_results[:5]]  # Return top 5
    
    def _register_default_operators(self, predicates: Set[str], constants: Set[str]):
        """Register default refinement operators"""
        self.register_operator("specialization", SpecializationOperator(predicates, constants))
        self.register_operator("generalization", GeneralizationOperator())
        self.register_operator("theta_subsumption", ThetaSubsumptionRefinement(predicates, constants))
    
    def _evaluate_clause(self, clause: LogicalClause,
                        positive_examples: List[Example],
                        negative_examples: List[Example]) -> float:
        """
        Evaluate clause quality using precision and recall
        
        Returns a score between 0 and 1
        """
        pos_covered = sum(1 for ex in positive_examples if self._clause_covers_example(clause, ex))
        neg_covered = sum(1 for ex in negative_examples if self._clause_covers_example(clause, ex))
        
        # Calculate precision and recall
        precision = pos_covered / (pos_covered + neg_covered) if (pos_covered + neg_covered) > 0 else 0
        recall = pos_covered / len(positive_examples) if positive_examples else 0
        
        # F1 score
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        # Penalize overly complex clauses
        complexity_penalty = len(clause.body) * 0.01
        
        return max(0, f1 - complexity_penalty)
    
    def _clause_covers_example(self, clause: LogicalClause, example: Example) -> bool:
        """Check if clause covers example (simplified)"""
        # Simple unification check
        substitution = {}
        return self._unify_atoms(clause.head, example.atom, substitution)
    
    def _unify_atoms(self, atom1: LogicalAtom, atom2: LogicalAtom,
                    substitution: Dict[str, LogicalTerm]) -> bool:
        """Simple atom unification"""
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
    
    def _get_operator_type(self, op_name: str) -> RefinementType:
        """Get refinement type for operator"""
        if "special" in op_name.lower():
            return RefinementType.SPECIALIZATION
        elif "general" in op_name.lower():
            return RefinementType.GENERALIZATION
        else:
            return RefinementType.SPECIALIZATION
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get refinement statistics"""
        return {
            **self.stats,
            "refinement_steps_taken": len(self.refinement_history),
            "max_refinement_steps": self.max_refinement_steps,
            "beam_width": self.beam_width,
            "improvement_threshold": self.improvement_threshold,
            "registered_operators": list(self.operators.keys())
        }
    
    def get_refinement_trace(self) -> List[RefinementStep]:
        """Get history of refinement steps"""
        return self.refinement_history.copy()


# Utility functions
def create_rule_refiner(max_steps: int = 10, beam_width: int = 5) -> RuleRefinement:
    """
    Create a rule refinement system with common settings
    
    Args:
        max_steps: Maximum refinement steps
        beam_width: Beam search width
        
    Returns:
        Configured RuleRefinement system
    """
    return RuleRefinement(
        max_refinement_steps=max_steps,
        beam_width=beam_width,
        improvement_threshold=0.1
    )


# Example usage
if __name__ == "__main__":
    print("🔧 Rule Refinement for ILP - Systematic Hypothesis Space Search")
    print("=" * 70)
    
    # Create refinement system
    refiner = RuleRefinement()
    
    # Example clause to refine
    alice_term = LogicalTerm(name='alice', term_type='constant')
    bob_term = LogicalTerm(name='bob', term_type='constant')
    var_x = LogicalTerm(name='X', term_type='variable')
    var_y = LogicalTerm(name='Y', term_type='variable')
    
    # Initial clause: parent(X, Y) :- 
    head = LogicalAtom(predicate='parent', terms=[var_x, var_y])
    initial_clause = LogicalClause(head=head, body=[])
    
    # Create example data
    parent_alice_bob = LogicalAtom(predicate='parent', terms=[alice_term, bob_term])
    pos_example = Example(atom=parent_alice_bob, is_positive=True)
    
    parent_bob_alice = LogicalAtom(predicate='parent', terms=[bob_term, alice_term])
    neg_example = Example(atom=parent_bob_alice, is_positive=False)
    
    # Refine the rule
    predicates = {'parent', 'male', 'female'}
    constants = {'alice', 'bob', 'carol'}
    
    refined_clauses = refiner.refine_rule(
        initial_clause=initial_clause,
        positive_examples=[pos_example],
        negative_examples=[neg_example],
        predicates=predicates,
        constants=constants
    )
    
    print(f"\nRefined clauses ({len(refined_clauses)}):")
    for i, clause in enumerate(refined_clauses):
        print(f"  {i+1}. {clause}")
    
    # Print statistics
    stats = refiner.get_statistics()
    print(f"\nRefinement Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")