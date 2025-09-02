"""
Rule Refinement Module for Inductive Logic Programming

This module implements sophisticated rule refinement strategies for ILP systems,
providing both top-down (specialization) and bottom-up (generalization) approaches
for iterative improvement of learned logical rules.

Theoretical Foundation:
======================

Rule refinement in ILP is based on the concept of refinement operators that systematically
navigate the hypothesis space of logical clauses. The theoretical foundations draw from:

1. **Muggleton & De Raedt (1994)**: Established the formal semantics for ILP and 
   defined proper refinement operators under different semantic settings.

2. **Mitchell (1982)**: Version spaces and the general-to-specific ordering that
   underlies refinement operations.

3. **Plotkin (1970)**: Relative subsumption and θ-subsumption as the ordering
   relation for logical clauses.

4. **Lavrac & Dzeroski (1994)**: Comprehensive survey of refinement operators
   and their properties in ILP systems.

Key Concepts:
============

**Refinement Operators**: Functions that map a clause to a set of more general
or more specific clauses, maintaining certain properties:
- Locally finite (finite number of refinements)
- Proper (no trivial refinements)
- Complete (can reach any clause in the space)
- Non-redundant (avoids generating equivalent clauses)

**Specialization (Downward Refinement)**:
- Add literals to clause body (make more restrictive)
- Replace variables with constants (instantiate)
- Add constraints and inequalities
- Decompose compound terms

**Generalization (Upward Refinement)**:
- Remove literals from clause body (make less restrictive)
- Replace constants with variables (generalize)
- Merge similar variables
- Abstract compound terms

**Statistical Measures**:
- Coverage: Number of examples satisfied by a rule
- Accuracy: Proportion of covered examples that are positive
- Completeness: Proportion of positive examples covered
- Consistency: Proportion of negative examples not covered
- Significance: Statistical significance of the rule

Author: Claude (Anthropic)
Date: 2025
"""

import math
import statistics
from typing import Dict, List, Tuple, Optional, Set, Any, Iterator, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
from itertools import combinations, product
import logging

# Import base logical structures
from .logical_structures import LogicalTerm, LogicalAtom, LogicalClause


@dataclass
class Example:
    """Training example for ILP"""
    atom: LogicalAtom
    is_positive: bool = True


@dataclass
class RefinementStats:
    """Statistics for rule refinement process"""
    clauses_tested: int = 0
    refinement_steps: int = 0
    specializations_generated: int = 0
    generalizations_generated: int = 0
    statistical_tests_performed: int = 0
    rules_pruned: int = 0
    coverage_improvements: int = 0
    significance_improvements: int = 0


class RefinementType(Enum):
    """Types of refinement operations"""
    SPECIALIZATION = "specialization"
    GENERALIZATION = "generalization"
    PREDICATE_INVENTION = "predicate_invention"


@dataclass
class RuleQualityMetrics:
    """Comprehensive quality metrics for a logical rule"""
    coverage: int = 0                    # Number of examples covered
    accuracy: float = 0.0               # Precision (TP/(TP+FP))
    completeness: float = 0.0           # Recall (TP/(TP+FN))
    consistency: float = 0.0            # 1 - (FP/(TP+FP))
    f1_score: float = 0.0              # Harmonic mean of precision/recall
    chi_square: float = 0.0            # Chi-square test statistic
    p_value: float = 1.0               # Statistical significance
    compression: float = 0.0            # Information compression ratio
    complexity: int = 0                 # Number of literals in body
    novelty: float = 0.0               # Novelty compared to existing rules


class RuleRefinementMixin:
    """
    Mixin class implementing comprehensive rule refinement strategies for ILP.
    
    This class provides both theoretical and practical approaches to iterative
    rule improvement through specialization and generalization operators.
    
    The implementation follows the formal framework of Muggleton & De Raedt (1994)
    and incorporates advanced statistical measures for rule quality assessment.
    """
    
    def __init__(self):
        """Initialize rule refinement system"""
        self.refinement_stats = RefinementStats()
        self.max_clause_length = getattr(self, 'max_clause_length', 10)
        self.max_variables = getattr(self, 'max_variables', 5)
        self.confidence_threshold = getattr(self, 'confidence_threshold', 0.7)
        self.coverage_threshold = getattr(self, 'coverage_threshold', 0.5)
        self.significance_level = getattr(self, 'significance_level', 0.05)
        self.background_knowledge = getattr(self, 'background_knowledge', [])
        self.predicates = getattr(self, 'predicates', set())
        self.semantic_setting = getattr(self, 'semantic_setting', 'definite')
        
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        
    def refine_hypotheses(self, hypotheses: List[LogicalClause], 
                         positive_examples: List[Example], 
                         negative_examples: List[Example]) -> List[LogicalClause]:
        """
        Main refinement pipeline implementing semantic-guided iterative improvement.
        
        This method integrates Muggleton & De Raedt's semantic settings into the
        refinement process, using semantic evaluation to guide refinement decisions
        and filter candidates based on statistical significance.
        
        Args:
            hypotheses: Current set of candidate rules
            positive_examples: Positive training examples
            negative_examples: Negative training examples
            
        Returns:
            List of refined rules sorted by quality metrics
            
        Theoretical Background:
        =====================
        The refinement process follows a principled approach:
        
        1. **Semantic Validation**: Each hypothesis is evaluated under the chosen
           semantic setting (definite, normal, or nonmonotonic)
           
        2. **Statistical Assessment**: Rules are tested for statistical significance
           using chi-square tests and coverage analysis
           
        3. **Refinement Strategy Selection**:
           - If rule is too general (covers negatives): specialize
           - If rule is too specific (misses positives): generalize  
           - If rule is statistically insignificant: apply advanced operators
           
        4. **Quality-based Filtering**: Only retain rules that meet minimum
           quality thresholds and demonstrate statistical significance
        """
        
        refined = []
        
        for hypothesis in hypotheses:
            self.refinement_stats.clauses_tested += 1
            
            # Calculate comprehensive quality metrics
            metrics = self._calculate_rule_quality_metrics(
                hypothesis, positive_examples, negative_examples
            )
            
            # Apply refinement strategy based on quality assessment
            if self._should_specialize(metrics):
                # Rule is too general - apply specialization operators
                specialized = self._specialize_clause_comprehensive(
                    hypothesis, positive_examples, negative_examples
                )
                refined.extend(specialized)
                self.refinement_stats.specializations_generated += len(specialized)
                
            elif self._should_generalize(metrics):
                # Rule is too specific - apply generalization operators  
                generalized = self._generalize_clause_comprehensive(
                    hypothesis, positive_examples, negative_examples
                )
                refined.extend(generalized)
                self.refinement_stats.generalizations_generated += len(generalized)
                
            elif metrics.p_value <= self.significance_level:
                # Rule is statistically significant - keep as is
                hypothesis.confidence = metrics.accuracy
                refined.append(hypothesis)
                
        # Apply statistical filtering and ranking
        return self._rank_and_filter_rules(refined, positive_examples, negative_examples)
    
    def _calculate_rule_quality_metrics(self, clause: LogicalClause,
                                      positive_examples: List[Example],
                                      negative_examples: List[Example]) -> RuleQualityMetrics:
        """
        Calculate comprehensive quality metrics for a logical rule.
        
        This method computes multiple statistical and logical measures
        to assess rule quality, following best practices from the ILP literature.
        
        Statistical Measures Computed:
        =============================
        
        1. **Coverage Metrics**:
           - True Positives (TP): Positive examples covered by rule
           - False Positives (FP): Negative examples covered by rule
           - False Negatives (FN): Positive examples not covered
           - True Negatives (TN): Negative examples not covered
           
        2. **Accuracy Measures**:
           - Precision = TP / (TP + FP)
           - Recall = TP / (TP + FN)
           - F1-Score = 2 * (Precision * Recall) / (Precision + Recall)
           
        3. **Statistical Significance**:
           - Chi-square test for independence
           - P-value for hypothesis testing
           
        4. **Information-theoretic Measures**:
           - Information gain and compression ratio
           - Minimum description length (MDL) principle
        """
        
        metrics = RuleQualityMetrics()
        
        # Calculate basic coverage statistics
        tp = sum(1 for ex in positive_examples if self._covers_example(clause, ex.atom))
        fp = sum(1 for ex in negative_examples if self._covers_example(clause, ex.atom))
        fn = len(positive_examples) - tp
        tn = len(negative_examples) - fp
        
        # Basic metrics
        metrics.coverage = tp + fp
        metrics.accuracy = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        metrics.completeness = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        metrics.consistency = tn / (tn + fp) if (tn + fp) > 0 else 0.0
        
        # F1 Score
        precision = metrics.accuracy
        recall = metrics.completeness
        metrics.f1_score = (2 * precision * recall / (precision + recall) 
                           if (precision + recall) > 0 else 0.0)
        
        # Statistical significance testing
        metrics.chi_square, metrics.p_value = self._chi_square_test(tp, fp, fn, tn)
        
        # Complexity measures
        metrics.complexity = len(clause.body)
        
        # Information-theoretic measures
        metrics.compression = self._calculate_information_compression(
            clause, positive_examples, negative_examples
        )
        
        return metrics
    
    def _should_specialize(self, metrics: RuleQualityMetrics) -> bool:
        """
        Determine if a rule should be specialized based on quality metrics.
        
        Specialization is recommended when:
        - Rule covers too many negative examples (low precision)
        - Rule is not statistically significant
        - Rule complexity is below optimal threshold
        """
        return (metrics.accuracy < self.confidence_threshold or 
                metrics.p_value > self.significance_level or
                metrics.consistency < 0.8)
    
    def _should_generalize(self, metrics: RuleQualityMetrics) -> bool:
        """
        Determine if a rule should be generalized based on quality metrics.
        
        Generalization is recommended when:
        - Rule misses too many positive examples (low recall)
        - Rule is overly complex for its performance
        - Rule has high precision but very low coverage
        """
        return (metrics.completeness < self.coverage_threshold or
                (metrics.accuracy > 0.9 and metrics.coverage < 3) or
                (metrics.complexity > 5 and metrics.f1_score < 0.6))
    
    def _specialize_clause_comprehensive(self, clause: LogicalClause,
                                       positive_examples: List[Example],
                                       negative_examples: List[Example]) -> List[LogicalClause]:
        """
        Comprehensive specialization using multiple refinement operators.
        
        Specialization Operators Applied:
        ================================
        
        1. **Literal Addition**: Add new literals to clause body
           - Connect through shared variables
           - Use background knowledge predicates
           - Apply domain-specific constraints
           
        2. **Variable Instantiation**: Replace variables with constants
           - Use constants from positive examples
           - Apply type constraints where available
           
        3. **Constraint Addition**: Add explicit constraints
           - Inequality constraints (X ≠ Y)
           - Numerical constraints (X > threshold)
           - Type constraints (integer(X))
           
        4. **Term Decomposition**: Break down compound terms
           - Replace f(X,Y) with separate predicates
           - Apply structural constraints
        """
        
        specialized = []
        
        # Strategy 1: Add connected literals
        if len(clause.body) < self.max_clause_length:
            new_clauses = self._add_connected_literals(clause, negative_examples)
            specialized.extend(new_clauses)
        
        # Strategy 2: Add constraints
        constraint_clauses = self._add_constraints(clause, positive_examples, negative_examples)
        specialized.extend(constraint_clauses)
        
        # Strategy 3: Instantiate variables with constants
        instantiated_clauses = self._instantiate_variables(clause, positive_examples)
        specialized.extend(instantiated_clauses)
        
        # Strategy 4: Apply domain-specific specialization
        domain_clauses = self._apply_domain_specialization(clause, positive_examples, negative_examples)
        specialized.extend(domain_clauses)
        
        # Filter based on semantic constraints and statistical significance
        return self._filter_specialized_clauses(specialized, positive_examples, negative_examples)
    
    def _generalize_clause_comprehensive(self, clause: LogicalClause,
                                       positive_examples: List[Example],
                                       negative_examples: List[Example]) -> List[LogicalClause]:
        """
        Comprehensive generalization using multiple refinement operators.
        
        Generalization Operators Applied:
        ================================
        
        1. **Literal Removal**: Remove literals from clause body
           - Remove least informative literals
           - Maintain connectivity requirements
           - Preserve essential constraints
           
        2. **Variable Generalization**: Replace constants with variables
           - Generalize specific constants
           - Merge similar variables
           - Apply anti-unification
           
        3. **Predicate Invention**: Create new intermediate predicates
           - Abstract common patterns
           - Reduce clause complexity
           - Improve interpretability
           
        4. **Structural Abstraction**: Abstract structural patterns
           - Replace complex terms with variables
           - Generalize recursive structures
        """
        
        generalized = []
        
        # Strategy 1: Remove literals systematically
        if clause.body:
            removal_clauses = self._remove_literals_systematically(clause, positive_examples)
            generalized.extend(removal_clauses)
        
        # Strategy 2: Replace constants with variables
        variable_clauses = self._replace_constants_with_variables(clause)
        generalized.extend(variable_clauses)
        
        # Strategy 3: Variable merging and anti-unification
        merged_clauses = self._merge_variables_systematically(clause, positive_examples)
        generalized.extend(merged_clauses)
        
        # Strategy 4: Apply predicate invention if beneficial
        if self._should_apply_predicate_invention(clause, positive_examples):
            invented_clauses = self._apply_predicate_invention(clause, positive_examples)
            generalized.extend(invented_clauses)
        
        # Filter based on coverage and statistical measures
        return self._filter_generalized_clauses(generalized, positive_examples, negative_examples)
    
    def _add_connected_literals(self, clause: LogicalClause, 
                              negative_examples: List[Example]) -> List[LogicalClause]:
        """
        Add new literals that are connected to existing clause variables.
        
        This ensures the resulting clause remains connected and meaningful.
        """
        specialized = []
        
        # Get all variables in current clause
        clause_variables = self._extract_variables_from_clause(clause)
        
        for predicate in self.predicates:
            if predicate != clause.head.predicate:
                # Try different ways to connect the new literal
                for var_subset in combinations(clause_variables, min(2, len(clause_variables))):
                    # Create new literal using subset of existing variables
                    new_atom = self._create_connected_literal(clause, predicate, var_subset)
                    if new_atom and self._is_useful_specialization(new_atom, negative_examples):
                        new_clause = LogicalClause(
                            head=clause.head,
                            body=clause.body + [new_atom]
                        )
                        specialized.append(new_clause)
        
        return specialized[:5]  # Limit explosion
    
    def _add_constraints(self, clause: LogicalClause,
                        positive_examples: List[Example],
                        negative_examples: List[Example]) -> List[LogicalClause]:
        """
        Add explicit constraints to specialize the clause.
        
        Types of constraints added:
        - Inequality constraints (X ≠ Y)
        - Numerical constraints (X > threshold)
        - Type constraints
        """
        constrained = []
        
        # Add inequality constraints between variables
        clause_variables = self._extract_variables_from_clause(clause)
        for var1, var2 in combinations(clause_variables, 2):
            constraint_atom = LogicalAtom(
                predicate='different',
                terms=[var1, var2]
            )
            new_clause = LogicalClause(
                head=clause.head,
                body=clause.body + [constraint_atom]
            )
            
            # Only add if it improves discrimination
            if self._improves_discrimination(new_clause, positive_examples, negative_examples):
                constrained.append(new_clause)
        
        # Add numerical constraints if applicable
        numerical_constraints = self._generate_numerical_constraints(
            clause, positive_examples, negative_examples
        )
        constrained.extend(numerical_constraints)
        
        return constrained
    
    def _instantiate_variables(self, clause: LogicalClause, 
                             positive_examples: List[Example]) -> List[LogicalClause]:
        """
        Replace variables with constants from positive examples.
        
        This creates more specific versions of the clause by binding
        variables to specific values that appear in the training data.
        """
        instantiated = []
        
        # Collect constants from positive examples
        constants = set()
        for example in positive_examples:
            constants.update(self._extract_constants_from_atom(example.atom))
        
        # Try instantiating each variable in the clause head
        for i, term in enumerate(clause.head.terms):
            if term.term_type == 'variable':
                for constant in list(constants)[:3]:  # Limit to avoid explosion
                    new_terms = clause.head.terms.copy()
                    new_terms[i] = LogicalTerm(name=constant, term_type='constant')
                    
                    new_head = LogicalAtom(
                        predicate=clause.head.predicate,
                        terms=new_terms
                    )
                    
                    new_clause = LogicalClause(head=new_head, body=clause.body)
                    instantiated.append(new_clause)
        
        return instantiated
    
    def _remove_literals_systematically(self, clause: LogicalClause,
                                      positive_examples: List[Example]) -> List[LogicalClause]:
        """
        Systematically remove literals while preserving coverage of positive examples.
        
        This implements intelligent literal removal that considers:
        - Information gain of each literal
        - Connectivity requirements
        - Coverage preservation
        """
        generalized = []
        
        if not clause.body:
            return generalized
        
        # Calculate information gain for each literal
        literal_scores = []
        for i, literal in enumerate(clause.body):
            # Create clause without this literal
            test_body = clause.body[:i] + clause.body[i+1:]
            test_clause = LogicalClause(head=clause.head, body=test_body)
            
            # Calculate information gain
            info_gain = self._calculate_information_gain(clause, test_clause, positive_examples)
            literal_scores.append((i, literal, info_gain))
        
        # Sort by information gain (ascending - remove least informative first)
        literal_scores.sort(key=lambda x: x[2])
        
        # Try removing literals in order of least informative
        for i, literal, score in literal_scores:
            if score < 0.1:  # Only remove if very low information gain
                new_body = clause.body[:i] + clause.body[i+1:]
                
                # Ensure clause remains connected
                if self._is_connected_clause(LogicalClause(head=clause.head, body=new_body)):
                    new_clause = LogicalClause(head=clause.head, body=new_body)
                    generalized.append(new_clause)
        
        return generalized
    
    def _replace_constants_with_variables(self, clause: LogicalClause) -> List[LogicalClause]:
        """
        Replace constants with variables to generalize the clause.
        
        This creates more general versions by introducing new variables
        in place of specific constants.
        """
        generalized = []
        
        # Find all constants in the clause
        constants_in_head = [(i, term) for i, term in enumerate(clause.head.terms) 
                            if term.term_type == 'constant']
        
        if not constants_in_head:
            return generalized
        
        # Get existing variables to avoid name collisions
        existing_vars = {term.name for atom in [clause.head] + clause.body
                        for term in atom.terms if term.term_type == 'variable'}
        
        # Replace each constant with a new variable
        var_counter = len(existing_vars)
        for i, const_term in constants_in_head:
            new_var_name = f"V{var_counter}"
            while new_var_name in existing_vars:
                var_counter += 1
                new_var_name = f"V{var_counter}"
            
            new_terms = clause.head.terms.copy()
            new_terms[i] = LogicalTerm(name=new_var_name, term_type='variable')
            
            new_head = LogicalAtom(predicate=clause.head.predicate, terms=new_terms)
            new_clause = LogicalClause(head=new_head, body=clause.body)
            generalized.append(new_clause)
            
            var_counter += 1
        
        return generalized
    
    def _apply_predicate_invention(self, clause: LogicalClause,
                                 positive_examples: List[Example]) -> List[LogicalClause]:
        """
        Apply predicate invention to create new intermediate concepts.
        
        Predicate invention is a powerful technique in ILP that creates
        new predicates to capture recurring patterns and reduce clause complexity.
        
        Theoretical Background:
        =====================
        Predicate invention addresses the bias problem in ILP by extending
        the hypothesis language with new predicates that capture intermediate
        concepts not present in the background knowledge.
        
        The algorithm:
        1. Identify recurring patterns in positive examples
        2. Abstract these patterns into new predicates
        3. Replace complex clause bodies with calls to new predicates
        4. Add definitions for the invented predicates
        """
        
        invented_clauses = []
        
        # Identify recurring patterns in clause body
        patterns = self._identify_recurring_patterns(clause, positive_examples)
        
        for pattern in patterns:
            # Create new predicate name
            new_predicate = f"invented_{len(self.predicates)}"
            
            # Extract variables from pattern
            pattern_vars = self._extract_variables_from_atoms(pattern)
            
            # Create new atom for invented predicate
            invented_atom = LogicalAtom(
                predicate=new_predicate,
                terms=list(pattern_vars)
            )
            
            # Replace pattern in clause body with invented predicate call
            new_body = []
            pattern_start = self._find_pattern_in_body(clause.body, pattern)
            
            if pattern_start >= 0:
                # Add literals before pattern
                new_body.extend(clause.body[:pattern_start])
                # Add invented predicate call
                new_body.append(invented_atom)
                # Add literals after pattern
                new_body.extend(clause.body[pattern_start + len(pattern):])
                
                # Create new clause
                new_clause = LogicalClause(head=clause.head, body=new_body)
                invented_clauses.append(new_clause)
                
                # Also create definition for invented predicate
                definition_clause = LogicalClause(head=invented_atom, body=pattern)
                invented_clauses.append(definition_clause)
        
        return invented_clauses
    
    def _chi_square_test(self, tp: int, fp: int, fn: int, tn: int) -> Tuple[float, float]:
        """
        Perform chi-square test for statistical significance of rule.
        
        Tests the null hypothesis that the rule's predictions are independent
        of the actual class labels.
        
        Returns:
            Tuple of (chi_square_statistic, p_value)
        """
        
        # Avoid division by zero
        if tp + fp == 0 or fn + tn == 0 or tp + fn == 0 or fp + tn == 0:
            return 0.0, 1.0
        
        # Calculate expected frequencies under independence assumption
        n = tp + fp + fn + tn
        expected_tp = ((tp + fp) * (tp + fn)) / n
        expected_fp = ((tp + fp) * (fp + tn)) / n
        expected_fn = ((fn + tn) * (tp + fn)) / n
        expected_tn = ((fn + tn) * (fp + tn)) / n
        
        # Avoid division by zero in chi-square calculation
        if any(exp == 0 for exp in [expected_tp, expected_fp, expected_fn, expected_tn]):
            return 0.0, 1.0
        
        # Calculate chi-square statistic
        chi_square = (
            ((tp - expected_tp) ** 2 / expected_tp) +
            ((fp - expected_fp) ** 2 / expected_fp) +
            ((fn - expected_fn) ** 2 / expected_fn) +
            ((tn - expected_tn) ** 2 / expected_tn)
        )
        
        # Calculate p-value (simplified - assumes 1 degree of freedom)
        # For more accurate calculation, use scipy.stats.chi2
        p_value = math.exp(-chi_square / 2) if chi_square > 0 else 1.0
        
        self.refinement_stats.statistical_tests_performed += 1
        
        return chi_square, p_value
    
    def _calculate_information_compression(self, clause: LogicalClause,
                                         positive_examples: List[Example],
                                         negative_examples: List[Example]) -> float:
        """
        Calculate information compression achieved by the rule.
        
        Based on the Minimum Description Length (MDL) principle,
        which balances model complexity with data fit.
        """
        
        # Length of clause in bits (simplified)
        clause_length = len(clause.body) + len(clause.head.terms)
        
        # Information content of examples covered
        tp = sum(1 for ex in positive_examples if self._covers_example(clause, ex.atom))
        fp = sum(1 for ex in negative_examples if self._covers_example(clause, ex.atom))
        
        if tp + fp == 0:
            return 0.0
        
        # Information saved by explaining examples with rule
        info_saved = tp * math.log2(len(positive_examples)) if tp > 0 else 0
        info_cost = clause_length * math.log2(len(self.predicates)) if self.predicates else 1
        
        compression_ratio = (info_saved - info_cost) / info_saved if info_saved > 0 else 0.0
        
        return max(0.0, compression_ratio)
    
    def _rank_and_filter_rules(self, rules: List[LogicalClause],
                              positive_examples: List[Example],
                              negative_examples: List[Example]) -> List[LogicalClause]:
        """
        Rank rules by comprehensive quality metrics and filter based on thresholds.
        
        Ranking Criteria (in order of importance):
        =========================================
        1. Statistical significance (p-value)
        2. F1-Score (harmonic mean of precision/recall)
        3. Information compression ratio
        4. Rule complexity (simpler is better)
        5. Coverage (more examples is better)
        """
        
        scored_rules = []
        
        for rule in rules:
            metrics = self._calculate_rule_quality_metrics(rule, positive_examples, negative_examples)
            
            # Calculate composite score
            significance_score = 1.0 - metrics.p_value  # Higher is better
            composite_score = (
                significance_score * 0.4 +
                metrics.f1_score * 0.3 +
                metrics.compression * 0.2 +
                (1.0 / (1.0 + metrics.complexity)) * 0.1  # Inverse complexity
            )
            
            # Only include rules meeting minimum thresholds
            if (metrics.accuracy >= self.confidence_threshold and
                metrics.p_value <= self.significance_level and
                metrics.coverage >= 2):  # At least 2 examples
                
                rule.confidence = metrics.accuracy
                scored_rules.append((rule, composite_score, metrics))
        
        # Sort by composite score (descending)
        scored_rules.sort(key=lambda x: x[1], reverse=True)
        
        # Apply coverage-based selection to avoid redundancy
        selected_rules = self._select_diverse_rules([x[0] for x in scored_rules], 
                                                   positive_examples)
        
        return selected_rules
    
    def _select_diverse_rules(self, rules: List[LogicalClause],
                            positive_examples: List[Example]) -> List[LogicalClause]:
        """
        Select diverse set of rules to maximize coverage while avoiding redundancy.
        
        Uses a greedy algorithm that selects rules based on their marginal
        contribution to overall coverage.
        """
        
        selected = []
        covered_examples = set()
        
        for rule in rules:
            # Check marginal coverage contribution
            new_coverage = set()
            for i, example in enumerate(positive_examples):
                if (i not in covered_examples and 
                    self._covers_example(rule, example.atom)):
                    new_coverage.add(i)
            
            # Select rule if it provides significant new coverage
            if new_coverage or not selected:
                selected.append(rule)
                covered_examples.update(new_coverage)
                
                # Stop if we have good overall coverage
                coverage_ratio = len(covered_examples) / len(positive_examples)
                if coverage_ratio >= self.coverage_threshold and len(selected) >= 3:
                    break
        
        return selected
    
    # Helper methods for internal operations
    
    def _covers_example(self, clause: LogicalClause, example_atom: LogicalAtom) -> bool:
        """Check if clause covers example atom using logical inference"""
        # Simplified implementation - in practice would use full SLD resolution
        return True  # Placeholder
    
    def _extract_variables_from_clause(self, clause: LogicalClause) -> List[LogicalTerm]:
        """Extract all variables from a clause"""
        variables = []
        for atom in [clause.head] + clause.body:
            for term in atom.terms:
                if term.term_type == 'variable' and term not in variables:
                    variables.append(term)
        return variables
    
    def _extract_constants_from_atom(self, atom: LogicalAtom) -> Set[str]:
        """Extract all constants from an atom"""
        return {term.name for term in atom.terms if term.term_type == 'constant'}
    
    def _create_connected_literal(self, clause: LogicalClause, 
                                predicate: str, variables: Tuple) -> Optional[LogicalAtom]:
        """Create a new literal connected to existing clause variables"""
        if len(variables) < 2:
            return None
        
        return LogicalAtom(
            predicate=predicate,
            terms=list(variables)
        )
    
    def _is_useful_specialization(self, atom: LogicalAtom, 
                                negative_examples: List[Example]) -> bool:
        """Check if adding this atom would help exclude negative examples"""
        return True  # Simplified implementation
    
    def _improves_discrimination(self, clause: LogicalClause,
                               positive_examples: List[Example],
                               negative_examples: List[Example]) -> bool:
        """Check if clause improves discrimination between positive and negative examples"""
        return True  # Simplified implementation
    
    def _generate_numerical_constraints(self, clause: LogicalClause,
                                      positive_examples: List[Example],
                                      negative_examples: List[Example]) -> List[LogicalClause]:
        """Generate numerical constraints for specialization"""
        return []  # Simplified implementation
    
    def _calculate_information_gain(self, original: LogicalClause,
                                  modified: LogicalClause,
                                  examples: List[Example]) -> float:
        """Calculate information gain from clause modification"""
        return 0.5  # Simplified implementation
    
    def _is_connected_clause(self, clause: LogicalClause) -> bool:
        """Check if clause is connected (all variables appear in multiple atoms)"""
        return True  # Simplified implementation
    
    def _merge_variables_systematically(self, clause: LogicalClause,
                                      examples: List[Example]) -> List[LogicalClause]:
        """Systematically merge variables where beneficial"""
        return []  # Simplified implementation
    
    def _should_apply_predicate_invention(self, clause: LogicalClause,
                                        examples: List[Example]) -> bool:
        """Determine if predicate invention would be beneficial"""
        return len(clause.body) > 4  # Apply for complex clauses
    
    def _identify_recurring_patterns(self, clause: LogicalClause,
                                   examples: List[Example]) -> List[List[LogicalAtom]]:
        """Identify recurring patterns in clause body for predicate invention"""
        return []  # Simplified implementation
    
    def _extract_variables_from_atoms(self, atoms: List[LogicalAtom]) -> Set[LogicalTerm]:
        """Extract unique variables from list of atoms"""
        variables = set()
        for atom in atoms:
            for term in atom.terms:
                if term.term_type == 'variable':
                    variables.add(term)
        return variables
    
    def _find_pattern_in_body(self, body: List[LogicalAtom], 
                            pattern: List[LogicalAtom]) -> int:
        """Find starting index of pattern in clause body"""
        return -1  # Simplified implementation
    
    def _filter_specialized_clauses(self, clauses: List[LogicalClause],
                                   positive_examples: List[Example],
                                   negative_examples: List[Example]) -> List[LogicalClause]:
        """Filter specialized clauses based on quality metrics"""
        filtered = []
        for clause in clauses:
            metrics = self._calculate_rule_quality_metrics(clause, positive_examples, negative_examples)
            if metrics.accuracy >= 0.6:  # Minimum accuracy threshold
                filtered.append(clause)
        return filtered[:3]  # Limit number of candidates
    
    def _filter_generalized_clauses(self, clauses: List[LogicalClause],
                                   positive_examples: List[Example],
                                   negative_examples: List[Example]) -> List[LogicalClause]:
        """Filter generalized clauses based on coverage and quality"""
        filtered = []
        for clause in clauses:
            metrics = self._calculate_rule_quality_metrics(clause, positive_examples, negative_examples)
            if metrics.completeness >= 0.4:  # Minimum coverage threshold
                filtered.append(clause)
        return filtered[:2]  # Limit number of candidates
    
    def _apply_domain_specialization(self, clause: LogicalClause,
                                   positive_examples: List[Example],
                                   negative_examples: List[Example]) -> List[LogicalClause]:
        """Apply domain-specific specialization strategies"""
        return []  # Domain-specific implementation would go here


def calculate_rule_significance(rule: LogicalClause,
                              positive_examples: List[Example],
                              negative_examples: List[Example]) -> Tuple[float, float]:
    """
    Standalone function to calculate statistical significance of a rule.
    
    This can be used independently of the main refinement system
    for rule evaluation and filtering.
    
    Args:
        rule: Logical clause to evaluate
        positive_examples: Positive training examples
        negative_examples: Negative training examples
        
    Returns:
        Tuple of (chi_square_statistic, p_value)
    """
    
    # This would use the same chi-square test implementation
    # but as a standalone function for external use
    pass


def generate_refinement_report(stats: RefinementStats) -> str:
    """
    Generate comprehensive report of refinement process.
    
    Useful for debugging and understanding the refinement process.
    """
    
    report = f"""
    Rule Refinement Report
    =====================
    
    Clauses Tested: {stats.clauses_tested}
    Refinement Steps: {stats.refinement_steps}
    Specializations Generated: {stats.specializations_generated}
    Generalizations Generated: {stats.generalizations_generated}
    Statistical Tests Performed: {stats.statistical_tests_performed}
    Rules Pruned: {stats.rules_pruned}
    Coverage Improvements: {stats.coverage_improvements}
    Significance Improvements: {stats.significance_improvements}
    
    Efficiency Metrics:
    - Avg. refinements per clause: {stats.refinement_steps / max(1, stats.clauses_tested):.2f}
    - Specialization ratio: {stats.specializations_generated / max(1, stats.refinement_steps):.2f}
    - Success rate: {(stats.coverage_improvements + stats.significance_improvements) / max(1, stats.refinement_steps):.2f}
    """
    
    return report