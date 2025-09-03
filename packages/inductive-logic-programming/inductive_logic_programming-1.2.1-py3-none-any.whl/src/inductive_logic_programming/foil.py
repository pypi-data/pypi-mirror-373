"""
FOIL (First Order Inductive Learner) Implementation
Based on: Quinlan (1990) "Learning logical definitions from relations"

FOIL is a classic ILP algorithm that learns first-order Horn clauses
using a covering approach with information gain heuristics.

# FIXME: Critical Research Accuracy Issues Based on Quinlan (1990) FOIL Paper
#
# 1. INCORRECT INFORMATION GAIN FORMULA IMPLEMENTATION
#    - Quinlan's exact formula: FOIL_Gain(L,R) = t × (log₂(p₁/(p₁+n₁)) - log₂(p₀/(p₀+n₀)))
#    - Current implementation has approximation but misses key details:
#      * t = number of positive bindings for literal L that extend rule R
#      * p₀,n₀ = positive/negative bindings before adding literal L
#      * p₁,n₁ = positive/negative bindings after adding literal L
#    - Missing proper binding count (tuples that satisfy the partially-constructed rule)
#    - Research basis: Quinlan (1990) Section 3.2 "The learning algorithm", pages 245-247
#    - Solutions:
#      a) Implement proper binding enumeration for literals in first-order logic
#      b) Count variable instantiations that satisfy partial rules, not just examples
#      c) Use exact FOIL gain: gain = t * (log2(p1/(p1+n1)) - log2(p0/(p0+n0)))
#      d) Handle binding multiplicities when variables are shared between literals
#    - Example:
#      ```python
#      def calculate_foil_gain(self, literal, partial_rule, bindings_before, bindings_after):
#          t = len([b for b in bindings_after if b.is_positive])  # Positive bindings
#          p0, n0 = count_pos_neg_bindings(bindings_before)
#          p1, n1 = count_pos_neg_bindings(bindings_after)
#          return t * (log2(p1/(p1+n1)) - log2(p0/(p0+n0)))
#      ```
#
# 2. MISSING PROPER FIRST-ORDER VARIABLE BINDING MECHANISM
#    - FOIL operates on variable bindings (instantiations), not just examples
#    - Current implementation conflates examples with bindings
#    - Missing: θ-subsumption and proper unification for generating bindings
#    - Missing: handling of shared variables between literals in clause body
#    - Research basis: Quinlan (1990) Section 2 "Terminology", pages 241-244
#    - Solutions:
#      a) Implement binding generation: enumerate all variable instantiations that satisfy partial rule
#      b) Track bindings as tuples: θ = {X₁/a₁, X₂/a₂, ...} for variables Xᵢ and constants aᵢ
#      c) Maintain consistency when adding literals: new literal must be satisfiable under existing bindings
#      d) Implement θ-subsumption test for clause generality
#    - Example:
#      ```python
#      def generate_bindings(self, partial_clause):
#          bindings = []
#          for substitution in self.enumerate_substitutions(partial_clause):
#              if self.satisfies_background_knowledge(substitution, partial_clause):
#                  bindings.append(substitution)
#          return bindings
#      ```
#
# 3. INADEQUATE LITERAL GENERATION STRATEGY
#    - Quinlan's FOIL uses systematic literal generation based on background predicates
#    - Missing proper mode declarations (input/output argument specifications)
#    - No implementation of "determinate literals" (functional dependencies)
#    - Missing constraint on literal generation based on typing and shared variables
#    - Research basis: Quinlan (1990) Section 3.3 "Constructing literals", pages 247-249
#    - Solutions:
#      a) Implement mode declarations: +type (input), -type (output), #type (constant)
#      b) Add determinate literal detection: literals that determine values of other variables
#      c) Use background knowledge structure for guided literal generation
#      d) Implement variable typing constraints to avoid meaningless literals
#    - Example:
#      ```python
#      def generate_literals_with_modes(self, current_clause, mode_declarations):
#          literals = []
#          for predicate, modes in mode_declarations.items():
#              for mode in modes:
#                  if self.is_valid_literal_for_mode(current_clause, predicate, mode):
#                      literals.extend(self.instantiate_literal(predicate, mode, current_clause.variables))
#          return literals
#      ```
#
# 4. MISSING PROPER PRUNING AND COMPLEXITY CONTROL
#    - Quinlan's FOIL includes sophisticated pruning based on encoding length
#    - Missing: minimum description length (MDL) principle for clause selection
#    - No implementation of significance testing for literal addition
#    - Missing clause subsumption checking to avoid redundant rules
#    - Research basis: Quinlan (1990) Section 3.4 "Pruning", pages 249-251
#    - Solutions:
#      a) Implement encoding length calculation: L(H) + L(D|H) where H=hypothesis, D=data
#      b) Add significance testing: reject literals that don't significantly improve coverage
#      c) Implement clause subsumption: remove redundant or overly general clauses
#      d) Use cross-validation or separate test set for pruning decisions
#    - Example:
#      ```python
#      def calculate_encoding_length(self, clause, examples):
#          hypothesis_length = len(clause.body) * log2(len(self.predicates))  # Simplified
#          error_length = sum(1 for ex in examples if not self.covers(clause, ex))
#          return hypothesis_length + error_length
#      ```
#
# 5. INCORRECT COVERAGE TESTING AND THEOREM PROVING
#    - Current coverage testing is oversimplified (only checks predicate existence)
#    - FOIL requires proper theorem proving to determine if clause covers example
#    - Missing: SLD resolution for definite clause coverage testing
#    - Missing: integration with background knowledge during coverage computation
#    - Research basis: Quinlan (1990) Section 2.3 "Covering", pages 243-244
#    - Solutions:
#      a) Implement SLD resolution for definite clauses
#      b) Integrate background knowledge facts and rules in coverage computation
#      c) Handle negation as failure properly (closed-world assumption)
#      d) Implement efficient indexing for fast coverage testing
#    - CODE REVIEW SUGGESTION - Replace oversimplified coverage with proper SLD resolution:
#      ```python
#      def covers_example_sld(self, clause: LogicalClause, example: Example, 
#                           background_kb: List[LogicalClause]) -> bool:
#          # Proper coverage testing using SLD resolution for definite clauses
#          goal = example.atom
#          return self.sld_resolution(clause, goal, background_kb) is not None
#      
#      def sld_resolution(self, clause: LogicalClause, goal: LogicalAtom, 
#                        background_kb: List[LogicalClause]) -> Optional[Dict[str, str]]:
#          # SLD Resolution for definite clauses - returns substitution if provable
#          goals = [goal]
#          substitution = {}
#          max_steps = 100  # Prevent infinite loops
#          
#          for step in range(max_steps):
#              if not goals:
#                  return substitution  # Success - all goals resolved
#              
#              current_goal = goals.pop(0)  # Leftmost selection rule
#              resolver_clause = None
#              unification = {}
#              
#              # Try main clause first
#              if self.unify_atoms(current_goal, clause.head, unification.copy()):
#                  resolver_clause = clause
#                  resolver_substitution = unification
#              else:
#                  # Try background knowledge
#                  for bg_clause in background_kb:
#                      unification_attempt = {}
#                      if self.unify_atoms(current_goal, bg_clause.head, unification_attempt):
#                          resolver_clause = bg_clause
#                          resolver_substitution = unification_attempt
#                          break
#              
#              if resolver_clause is None:
#                  return None  # Failure - no clause can resolve current goal
#              
#              # Apply substitution and add body literals as new goals
#              substitution.update(resolver_substitution)
#              new_goals = [self.apply_substitution(lit, resolver_substitution) 
#                          for lit in resolver_clause.body]
#              goals = new_goals + goals
#          
#          return None  # Timeout
#      
#      def apply_substitution(self, atom: LogicalAtom, substitution: Dict[str, str]) -> LogicalAtom:
#          # Apply variable substitution θ to atom
#          new_terms = []
#          for term in atom.terms:
#              if term.term_type == 'variable' and term.name in substitution:
#                  new_terms.append(LogicalTerm(name=substitution[term.name], term_type='constant'))
#              else:
#                  new_terms.append(term)
#          return LogicalAtom(predicate=atom.predicate, terms=new_terms, negated=atom.negated)
#      ```
#
# 6. MISSING NOISE HANDLING AND STATISTICAL VALIDATION
#    - Quinlan's FOIL includes noise handling through statistical significance testing
#    - Missing: χ² test for literal significance
#    - No handling of inconsistent examples or noisy data
#    - Missing: confidence intervals for learned rules
#    - Research basis: Quinlan (1990) Section 4 "Experiments", pages 251-261
#    - Solutions:
#      a) Implement χ² significance test for literal addition
#      b) Add noise tolerance parameters and exception handling
#      c) Use Laplace correction for probability estimates
#      d) Implement statistical confidence measures for learned clauses
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Set, Any
from dataclasses import dataclass
import logging
from itertools import product, combinations

from .ilp_core import (
    LogicalTerm, LogicalAtom, LogicalClause, Example,
    InductiveLogicProgrammer
)

@dataclass
class FOILStatistics:
    """Statistics for FOIL learning process"""
    clauses_generated: int = 0
    literals_tested: int = 0
    information_gain_calculations: int = 0
    coverage_tests: int = 0
    final_accuracy: float = 0.0
    learning_time: float = 0.0

class FOILLearner:
    """
    FOIL (First Order Inductive Learner) algorithm implementation
    
    FOIL learns definite Horn clauses using a greedy search guided by
    information gain. It uses a covering approach - learn one clause
    at a time to cover positive examples.
    
    Key features:
    - Information gain heuristic for literal selection
    - Covering algorithm (separate-and-conquer)
    - Pruning of overly specific clauses
    - Negation as failure support
    """
    
    def __init__(self,
                 min_gain_threshold: float = 0.1,
                 max_clause_length: int = 6,
                 max_variables: int = 4,
                 enable_negation: bool = True,
                 pruning_threshold: float = 0.05):
        """
        Initialize FOIL learner
        
        Args:
            min_gain_threshold: Minimum information gain to add literal
            max_clause_length: Maximum literals in clause body
            max_variables: Maximum variables per clause
            enable_negation: Whether to consider negated literals
            pruning_threshold: Threshold for pruning low-gain clauses
        """
        self.min_gain_threshold = min_gain_threshold
        self.max_clause_length = max_clause_length
        self.max_variables = max_variables
        self.enable_negation = enable_negation
        self.pruning_threshold = pruning_threshold
        
        # Learning state
        self.background_knowledge = []
        self.positive_examples = []
        self.negative_examples = []
        self.learned_clauses = []
        
        # Vocabulary
        self.predicates = set()
        self.constants = set()
        self.functions = set()
        
        # Statistics
        self.stats = FOILStatistics()
        
        print(f"✓ FOIL Learner initialized:")
        print(f"   Min gain threshold: {min_gain_threshold}")
        print(f"   Max clause length: {max_clause_length}")
        print(f"   Negation enabled: {enable_negation}")
    
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
        Learn rules using FOIL algorithm
        
        Args:
            target_predicate: Predicate to learn rules for
            
        Returns:
            List of learned clauses
        """
        print(f"\n🧠 FOIL Learning rules for predicate: {target_predicate}")
        
        # Get examples for target predicate
        pos_examples = [ex for ex in self.positive_examples 
                       if ex.atom.predicate == target_predicate]
        neg_examples = [ex for ex in self.negative_examples 
                       if ex.atom.predicate == target_predicate]
        
        print(f"   Examples: {len(pos_examples)} positive, {len(neg_examples)} negative")
        
        if not pos_examples:
            print("   No positive examples found!")
            return []
        
        uncovered_positive = pos_examples.copy()
        learned_rules = []
        
        # FOIL covering loop
        while uncovered_positive:
            print(f"\n   Learning clause to cover {len(uncovered_positive)} remaining positive examples")
            
            # Learn one clause
            clause = self._learn_single_clause(target_predicate, uncovered_positive, neg_examples)
            
            if clause is None:
                print("   No more useful clauses can be learned")
                break
                
            learned_rules.append(clause)
            self.learned_clauses.append(clause)
            
            # Remove covered positive examples
            newly_covered = self._get_covered_examples(clause, uncovered_positive)
            uncovered_positive = [ex for ex in uncovered_positive 
                                if ex not in newly_covered]
            
            print(f"   Clause covers {len(newly_covered)} positive examples")
            print(f"   Remaining uncovered: {len(uncovered_positive)}")
        
        # Calculate final accuracy
        self._calculate_accuracy(learned_rules, pos_examples, neg_examples)
        
        print(f"\n✓ FOIL learned {len(learned_rules)} rules")
        return learned_rules
    
    def _learn_single_clause(self, target_predicate: str, 
                           pos_examples: List[Example],
                           neg_examples: List[Example]) -> Optional[LogicalClause]:
        """Learn a single clause using FOIL's greedy search"""
        
        # Initialize clause head with variables
        head_vars = [LogicalTerm(name=f"V{i}", term_type='variable') 
                    for i in range(self._get_predicate_arity(target_predicate))]
        head = LogicalAtom(predicate=target_predicate, terms=head_vars)
        
        current_clause = LogicalClause(head=head, body=[])
        current_pos = pos_examples.copy()
        current_neg = neg_examples.copy()
        
        print(f"      Starting clause: {head} :-")
        
        # FOIL greedy search for literals
        for literal_count in range(self.max_clause_length):
            if not current_neg:
                print(f"      No negative examples left - stopping")
                break
                
            # Generate candidate literals
            candidate_literals = self._generate_candidate_literals(current_clause)
            
            if not candidate_literals:
                print(f"      No more candidate literals available")
                break
            
            # Select best literal based on information gain
            best_literal, best_gain = self._select_best_literal(
                candidate_literals, current_clause, current_pos, current_neg
            )
            
            if best_literal is None or best_gain < self.min_gain_threshold:
                print(f"      Best gain {best_gain:.3f} below threshold {self.min_gain_threshold}")
                break
            
            # Add literal to clause
            current_clause.body.append(best_literal)
            
            # Update covered examples
            new_pos, new_neg = self._filter_examples_by_clause(
                current_clause, current_pos, current_neg
            )
            
            print(f"      Added literal: {best_literal}")
            print(f"      Gain: {best_gain:.3f}, Pos: {len(new_pos)}, Neg: {len(new_neg)}")
            
            current_pos = new_pos
            current_neg = new_neg
            
            if len(current_pos) == 0:
                print(f"      No positive examples left - clause too specific")
                return None
        
        # Prune if clause doesn't cover enough examples
        coverage_ratio = len(current_pos) / len(pos_examples)
        if coverage_ratio < self.pruning_threshold:
            print(f"      Clause coverage {coverage_ratio:.3f} below pruning threshold")
            return None
        
        # Set confidence based on precision
        precision = len(current_pos) / (len(current_pos) + len(current_neg))
        current_clause.confidence = precision
        
        print(f"      Final clause: {current_clause}")
        print(f"      Precision: {precision:.3f}")
        
        return current_clause
    
    def _generate_candidate_literals(self, current_clause: LogicalClause) -> List[LogicalAtom]:
        """Generate candidate literals for extending the clause"""
        candidates = []
        self.stats.literals_tested += 1
        
        # Get current variables in clause
        current_vars = set()
        for atom in [current_clause.head] + current_clause.body:
            for term in atom.terms:
                if term.term_type == 'variable':
                    current_vars.add(term.name)
        
        # Generate literals using existing predicates
        for predicate in self.predicates:
            if predicate == current_clause.head.predicate:
                continue  # Don't add recursive literals for now
                
            arity = self._get_predicate_arity(predicate)
            
            # Generate different variable/constant combinations
            for var_combo in self._generate_term_combinations(arity, current_vars):
                literal = LogicalAtom(predicate=predicate, terms=var_combo)
                candidates.append(literal)
                
                # Add negated version if enabled
                if self.enable_negation:
                    neg_literal = LogicalAtom(predicate=predicate, terms=var_combo, negated=True)
                    candidates.append(neg_literal)
        
        return candidates[:20]  # Limit candidates to avoid explosion
    
    def _generate_term_combinations(self, arity: int, current_vars: Set[str]) -> List[List[LogicalTerm]]:
        """Generate combinations of terms for literals"""
        combinations = []
        
        # Convert current variables to terms
        var_terms = [LogicalTerm(name=var, term_type='variable') for var in current_vars]
        
        # Add some constants
        const_terms = [LogicalTerm(name=const, term_type='constant') 
                      for const in list(self.constants)[:5]]  # Limit constants
        
        # Introduce new variables if needed
        next_var_id = len(current_vars)
        if next_var_id < self.max_variables:
            new_var = LogicalTerm(name=f"V{next_var_id}", term_type='variable')
            var_terms.append(new_var)
        
        all_terms = var_terms + const_terms
        
        # Generate combinations
        if arity == 1:
            for term in all_terms:
                combinations.append([term])
        elif arity == 2:
            for t1, t2 in product(all_terms, repeat=2):
                combinations.append([t1, t2])
        
        return combinations[:10]  # Limit combinations
    
    def _select_best_literal(self, candidates: List[LogicalAtom],
                           current_clause: LogicalClause,
                           pos_examples: List[Example],
                           neg_examples: List[Example]) -> Tuple[Optional[LogicalAtom], float]:
        """Select the literal with highest information gain"""
        
        best_literal = None
        best_gain = -1.0
        
        for candidate in candidates:
            self.stats.information_gain_calculations += 1
            
            # Create test clause with candidate literal
            test_clause = LogicalClause(
                head=current_clause.head,
                body=current_clause.body + [candidate]
            )
            
            # Calculate information gain
            gain = self._calculate_information_gain(
                test_clause, current_clause, pos_examples, neg_examples
            )
            
            if gain > best_gain:
                best_gain = gain
                best_literal = candidate
        
        return best_literal, best_gain
    
    def _calculate_information_gain(self, new_clause: LogicalClause, 
                                  old_clause: LogicalClause,
                                  pos_examples: List[Example],
                                  neg_examples: List[Example]) -> float:
        """
        Calculate information gain from adding a literal
        
        # FIXME: Critical Error in FOIL Information Gain Implementation
        #
        # 1. WRONG INTERPRETATION OF QUINLAN'S FORMULA
        #    - Current: treats examples as the unit of measurement
        #    - Quinlan's FOIL: operates on variable bindings (instantiations)
        #    - t should be number of positive bindings that satisfy the added literal
        #    - p₀,n₀,p₁,n₁ should count bindings, not examples
        #    - Solutions:
        #      a) Enumerate all variable bindings for partial clause
        #      b) Count bindings that satisfy new literal: t = |{θ: L(θ) ∧ θ ∈ pos_bindings}|
        #      c) Use binding-based counts for information calculation
        #    - CODE REVIEW SUGGESTION - Replace example-based with binding-based calculation:
        #      ```python
        #      from dataclasses import dataclass
        #      from itertools import product
        #      
        #      @dataclass 
        #      class VariableBinding:
        #          substitution: Dict[str, str]  # {variable: constant}
        #          is_positive: bool
        #          satisfies_clause: bool = False
        #      
        #      def calculate_foil_gain_proper(self, literal: LogicalAtom, partial_rule: LogicalClause,
        #                                    examples: List[Example]) -> float:
        #          # Proper FOIL gain using variable bindings, not examples
        #          # Generate bindings for partial rule
        #          bindings_before = self.generate_variable_bindings(partial_rule, examples)
        #          
        #          # Generate bindings after adding literal  
        #          extended_rule = LogicalClause(head=partial_rule.head, body=partial_rule.body + [literal])
        #          bindings_after = self.generate_variable_bindings(extended_rule, examples)
        #          
        #          # Count positive/negative bindings (not examples!)
        #          p0 = len([b for b in bindings_before if b.is_positive])
        #          n0 = len([b for b in bindings_before if not b.is_positive])
        #          p1 = len([b for b in bindings_after if b.is_positive]) 
        #          n1 = len([b for b in bindings_after if not b.is_positive])
        #          t = p1  # positive bindings that extend the rule
        #          
        #          if p0 == 0 or p1 == 0 or (p0 + n0) == 0 or (p1 + n1) == 0:
        #              return 0.0
        #          
        #          # Quinlan's exact formula with Laplace correction
        #          old_info = np.log2((p0 + 1) / (p0 + n0 + 2))
        #          new_info = np.log2((p1 + 1) / (p1 + n1 + 2)) 
        #          return t * (new_info - old_info)
        #      
        #      def generate_variable_bindings(self, clause: LogicalClause, examples: List[Example]) -> List[VariableBinding]:
        #          # Generate all variable instantiations that satisfy clause
        #          bindings = []
        #          variables = self.extract_variables(clause)
        #          constants = list(self.constants)
        #          
        #          # Generate all substitutions θ = {X₁/a₁, X₂/a₂, ...}
        #          for values in product(constants, repeat=len(variables)):
        #              substitution = dict(zip(variables, values))
        #              
        #              # Check if substitution satisfies clause body via SLD resolution
        #              if self.satisfies_clause_sld(clause, substitution):
        #                  # Check if corresponds to positive example
        #                  is_pos = self.matches_positive_example(clause.head, substitution, examples)
        #                  bindings.append(VariableBinding(substitution, is_pos, True))
        #          
        #          return bindings
        #      ```
        #
        # 2. MISSING PROPER LOGARITHMIC BASE AND SMOOTHING
        #    - Quinlan uses natural logarithm (ln) in some formulations
        #    - Current smoothing (1e-8) is ad-hoc, should use Laplace correction
        #    - Should handle cases where p₁=0 or n₁=0 more systematically
        #    - Solutions:
        #      a) Use consistent logarithmic base as in original FOIL
        #      b) Apply Laplace correction: (count + 1) / (total + 2)
        #      c) Handle degenerate cases with principled approach
        
        Uses FOIL's information gain formula:
        Gain = t * (log2(p1/(p1+n1)) - log2(p0/(p0+n0)))
        
        where:
        - t = number of positive examples covered by new clause
        - p0,n0 = positive,negative examples covered by old clause  
        - p1,n1 = positive,negative examples covered by new clause
        """
        # Get coverage for old clause
        old_pos, old_neg = self._filter_examples_by_clause(old_clause, pos_examples, neg_examples)
        p0, n0 = len(old_pos), len(old_neg)
        
        # Get coverage for new clause
        new_pos, new_neg = self._filter_examples_by_clause(new_clause, pos_examples, neg_examples)
        p1, n1 = len(new_pos), len(new_neg)
        
        if p1 == 0 or p0 == 0:
            return 0.0
        
        # FOIL information gain formula
        old_info = np.log2(p0 / (p0 + n0 + 1e-8))
        new_info = np.log2(p1 / (p1 + n1 + 1e-8))
        
        gain = p1 * (new_info - old_info)
        return gain
    
    def _filter_examples_by_clause(self, clause: LogicalClause,
                                 pos_examples: List[Example],
                                 neg_examples: List[Example]) -> Tuple[List[Example], List[Example]]:
        """Filter examples covered by clause"""
        self.stats.coverage_tests += 1
        
        covered_pos = []
        covered_neg = []
        
        for example in pos_examples:
            if self._clause_covers_example(clause, example):
                covered_pos.append(example)
        
        for example in neg_examples:
            if self._clause_covers_example(clause, example):
                covered_neg.append(example)
        
        return covered_pos, covered_neg
    
    def _clause_covers_example(self, clause: LogicalClause, example: Example) -> bool:
        """Check if clause covers example (simplified unification)"""
        # Try to unify clause head with example atom
        substitution = {}
        if not self._unify_atoms(clause.head, example.atom, substitution):
            return False
        
        # Check if all body literals are satisfied (simplified)
        # In full implementation, this would involve theorem proving
        for literal in clause.body:
            # For now, assume body literals are satisfied if they use valid predicates
            if literal.predicate not in self.predicates:
                return False
        
        return True
    
    def _unify_atoms(self, atom1: LogicalAtom, atom2: LogicalAtom, 
                    substitution: Dict[str, LogicalTerm]) -> bool:
        """Simple unification (same as in main ILP module)"""
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
    
    def _get_covered_examples(self, clause: LogicalClause, examples: List[Example]) -> List[Example]:
        """Get examples covered by clause"""
        covered = []
        for example in examples:
            if self._clause_covers_example(clause, example):
                covered.append(example)
        return covered
    
    def _get_predicate_arity(self, predicate: str) -> int:
        """Get arity of predicate from examples"""
        for example in self.positive_examples + self.negative_examples:
            if example.atom.predicate == predicate:
                return len(example.atom.terms)
        return 2  # Default arity
    
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
            "algorithm": "FOIL",
            "clauses_generated": self.stats.clauses_generated,
            "literals_tested": self.stats.literals_tested,
            "information_gain_calculations": self.stats.information_gain_calculations,
            "coverage_tests": self.stats.coverage_tests,
            "final_accuracy": self.stats.final_accuracy,
            "learned_clauses": len(self.learned_clauses),
            "predicates_learned": len(set(clause.head.predicate for clause in self.learned_clauses)),
            "min_gain_threshold": self.min_gain_threshold,
            "max_clause_length": self.max_clause_length
        }


# Utility functions
def create_foil_learner(min_gain: float = 0.1, max_clause_len: int = 6) -> FOILLearner:
    """
    Create a FOIL learner with common settings
    
    Args:
        min_gain: Minimum information gain threshold
        max_clause_len: Maximum clause length
        
    Returns:
        Configured FOILLearner
    """
    return FOILLearner(
        min_gain_threshold=min_gain,
        max_clause_length=max_clause_len,
        enable_negation=True,
        pruning_threshold=0.05
    )


# Example usage
if __name__ == "__main__":
    print("🧠 FOIL (First Order Inductive Learner) - Quinlan 1990")
    print("=" * 55)
    
    # Create FOIL learner
    foil = FOILLearner(min_gain_threshold=0.1)
    
    # Example: Learning family relationships
    # Add examples
    alice_term = LogicalTerm(name='alice', term_type='constant')
    bob_term = LogicalTerm(name='bob', term_type='constant')
    carol_term = LogicalTerm(name='carol', term_type='constant')
    
    # Positive examples: parent relationships
    parent_alice_bob = LogicalAtom(predicate='parent', terms=[alice_term, bob_term])
    parent_alice_carol = LogicalAtom(predicate='parent', terms=[alice_term, carol_term])
    
    foil.add_example(parent_alice_bob, True)
    foil.add_example(parent_alice_carol, True)
    
    # Negative examples
    parent_bob_alice = LogicalAtom(predicate='parent', terms=[bob_term, alice_term])
    foil.add_example(parent_bob_alice, False)
    
    # Learn rules
    learned_rules = foil.learn_rules('parent')
    
    print(f"\nLearned {len(learned_rules)} rules:")
    for i, rule in enumerate(learned_rules):
        print(f"  {i+1}. {rule}")
    
    # Print statistics
    stats = foil.get_statistics()
    print(f"\nFOIL Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")