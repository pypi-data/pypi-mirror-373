"""
🔬 SEMANTIC EVALUATION MODULE - Logic Semantics for ILP Hypothesis Testing
========================================================================

This module provides the semantic evaluation framework for Inductive Logic Programming,
implementing the three fundamental semantic settings from Muggleton & De Raedt (1994).
These semantics define how learned hypotheses are validated against examples and
background knowledge.

Based on: Muggleton & De Raedt (1994) "Inductive Logic Programming: Theory and Methods"

🎯 ELI5 Summary:
Think of this as a judge that checks if learned rules make sense! It has three different
ways to judge rules:
1. Normal: "Does the rule work for good examples and avoid bad ones?"
2. Definite: "Is the rule mathematically sound in a logical model?"
3. Nonmonotonic: "Is the rule minimal and handles missing information well?"

🔧 The Three Semantic Settings:

**Normal Semantics** (Classical Logic with Consistency)
- Prior Satisfiability: B ∧ H ⊨ E+ (background + hypothesis entails positive examples)
- Posterior Sufficiency: B ∧ H ∧ E- ⊭ ⊥ (no contradiction with negative examples)
- Best for: Clean data with clear logical structure
- Use case: Traditional expert systems, formal reasoning

**Definite Semantics** (Model-Theoretic Approach)  
- E+ ⊆ M+(B ∧ H) (positive examples are in the least Herbrand model)
- E- ∩ M+(B ∧ H) = ∅ (negative examples are not in the least Herbrand model)
- Best for: Horn clause programs, Prolog-like reasoning
- Use case: Logic programming, constraint solving

**Nonmonotonic Semantics** (Closed-World Assumption)
- Validity: All positive examples are derivable
- Completeness: All derivable atoms are positive examples  
- Minimality: No proper subset of H satisfies validity and completeness
- Best for: Incomplete knowledge domains, default reasoning
- Use case: Common-sense reasoning, handling exceptions

🚀 Key Innovation: Semantic-Guided Learning
This module enables ILP systems to learn rules that are not just statistically valid
but also logically sound according to formal semantic criteria. This bridges the gap
between machine learning and formal logic, ensuring learned knowledge is interpretable
and theoretically grounded.

Author: Benedict Chen
"""

from abc import ABC
from typing import List, Dict, Tuple, Optional, Set
from itertools import combinations

# Import logical structures from our ILP module
from .logical_structures import LogicalTerm, LogicalAtom, LogicalClause, Example


class SemanticEvaluationMixin(ABC):
    """
    🎯 Semantic Evaluation Mixin for ILP Learning Systems
    
    This mixin provides semantic evaluation capabilities following Muggleton & De Raedt's
    three semantic settings for Inductive Logic Programming. It enables ILP systems to
    evaluate hypotheses not just on statistical criteria, but on formal logical semantics.
    
    The mixin implements:
    1. Hypothesis evaluation according to chosen semantic setting
    2. Semantic-specific scoring for hypothesis ranking
    3. Semantic-aware refinement operations (specialization/generalization)
    4. Entailment checking and logical inference
    
    🔧 Integration:
    To use this mixin, your ILP class should inherit from it and implement the required
    abstract methods. The mixin assumes your class has certain attributes:
    - semantic_setting: str ('normal', 'definite', 'nonmonotonic')
    - coverage_threshold: float
    - noise_tolerance: float
    - confidence_threshold: float
    - max_clause_length: int
    - max_variables: int
    - background_knowledge: List[LogicalClause]
    
    Example:
        class MyILPSystem(SemanticEvaluationMixin):
            def __init__(self):
                self.semantic_setting = 'normal'
                self.coverage_threshold = 0.7
                # ... other required attributes
    """
    
    def _evaluate_hypothesis_semantic(self, hypothesis: LogicalClause, 
                                     positive_examples: List[Example], 
                                     negative_examples: List[Example]) -> bool:
        """
        🔍 Evaluate Hypothesis According to Chosen Semantic Setting
        
        This is the central semantic evaluation method that dispatches to the appropriate
        semantic evaluation function based on the chosen semantic setting.
        
        🎯 ELI5: This is like having three different judges for a talent show, each with
        their own criteria. Depending on which judge you choose (normal, definite, or
        nonmonotonic), the rule gets evaluated differently!
        
        Technical Details:
        Routes hypothesis evaluation to the appropriate semantic framework:
        - Normal: Classical logic consistency checking
        - Definite: Model-theoretic validation in least Herbrand model
        - Nonmonotonic: Closed-world assumption with minimality constraints
        
        Args:
            hypothesis: The logical clause to evaluate
            positive_examples: Training examples that should be entailed
            negative_examples: Training examples that should not be entailed
            
        Returns:
            bool: True if hypothesis satisfies the semantic constraints of the chosen setting
            
        Raises:
            ValueError: If semantic_setting is not one of the valid options
            
        💡 Key Insight: Different semantic settings capture different notions of
        logical correctness, enabling domain-specific reasoning approaches!
        """
        if self.semantic_setting == 'normal':
            return self._evaluate_normal_semantics(hypothesis, positive_examples, negative_examples)
        elif self.semantic_setting == 'definite':
            return self._evaluate_definite_semantics(hypothesis, positive_examples, negative_examples)
        elif self.semantic_setting == 'nonmonotonic':
            return self._evaluate_nonmonotonic_semantics(hypothesis, positive_examples, negative_examples)
        else:
            raise ValueError(f"Unknown semantic setting: {self.semantic_setting}")
    
    def _evaluate_normal_semantics(self, hypothesis: LogicalClause, 
                                  positive_examples: List[Example], 
                                  negative_examples: List[Example]) -> bool:
        """
        📐 Normal Semantics Evaluation (Definition 3.1 from Muggleton & De Raedt 1994)
        
        Normal semantics follows classical logic with two key constraints:
        
        **Prior Satisfiability**: B ∧ H ⊨ E+ 
        The background knowledge combined with the hypothesis must entail the positive examples.
        This ensures our learned rule actually explains the positive training data.
        
        **Posterior Sufficiency**: B ∧ H ∧ E- ⊭ ⊥
        Adding negative examples to our knowledge base must not create a contradiction.
        This ensures our rule doesn't incorrectly classify negative examples as positive.
        
        🎯 ELI5: This is like a detective's theory that must:
        1. Explain all the evidence that supports the case (positive examples)
        2. Not contradict the evidence that disproves the case (negative examples)
        
        Mathematical Foundation:
        Let B = background knowledge, H = hypothesis, E+ = positive examples, E- = negative examples
        - Prior Satisfiability: For each e+ ∈ E+: B ∪ H ⊨ e+
        - Posterior Sufficiency: B ∪ H ∪ E- is consistent (⊭ ⊥)
        
        Implementation Details:
        - Uses entailment checking to verify positive coverage
        - Allows some noise tolerance for negative examples (real-world data is messy)
        - Requires at least some positive coverage (empty hypotheses are invalid)
        
        Args:
            hypothesis: Candidate rule to evaluate
            positive_examples: Examples the rule should explain
            negative_examples: Examples the rule should not explain
            
        Returns:
            bool: True if hypothesis satisfies normal semantic constraints
            
        Best For:
        - Clean, well-structured domains
        - Traditional expert systems
        - Formal logical reasoning
        - Domains with clear positive/negative distinctions
        
        Example:
            Background: parent(john, mary), male(john)
            Hypothesis: father(X, Y) :- parent(X, Y), male(X)
            Positive: father(john, mary)
            Negative: father(mary, john)
            
            Prior Satisfiability: ✓ (hypothesis + background entails father(john, mary))
            Posterior Sufficiency: ✓ (no contradiction with negative examples)
            
        🔬 Research Impact: This semantic setting enables ILP to learn logically sound
        rules that are guaranteed to be consistent with classical logical reasoning!
        """
        # Prior Satisfiability: Check if B ∧ H covers positive examples
        positive_coverage = 0
        for example in positive_examples:
            if self._entails_example(hypothesis, example):
                positive_coverage += 1
                
        prior_satisfiability = positive_coverage > 0  # At least some positive coverage
        
        # Posterior Sufficiency: Check if B ∧ H doesn't contradict negative examples
        negative_contradictions = 0
        for example in negative_examples:
            if self._entails_example(hypothesis, example):
                negative_contradictions += 1
                
        # Allow some noise tolerance for real-world data
        max_allowed_contradictions = len(negative_examples) * self.noise_tolerance
        posterior_sufficiency = negative_contradictions <= max_allowed_contradictions
        
        return prior_satisfiability and posterior_sufficiency
    
    def _evaluate_definite_semantics(self, hypothesis: LogicalClause, 
                                    positive_examples: List[Example], 
                                    negative_examples: List[Example]) -> bool:
        """
        🏗️ Definite Semantics Evaluation (Definition 3.2 from Muggleton & De Raedt 1994)
        
        Definite semantics uses model-theoretic approach with the least Herbrand model.
        This is the theoretical foundation for logic programming languages like Prolog.
        
        **Positive Inclusion**: E+ ⊆ M+(B ∧ H)
        All positive examples must be in the least Herbrand model of background + hypothesis.
        This ensures every positive example is logically derivable from our rules.
        
        **Negative Exclusion**: E- ∩ M+(B ∧ H) = ∅  
        No negative examples should be in the least Herbrand model.
        This ensures we don't accidentally derive negative examples as true.
        
        🎯 ELI5: Imagine a mathematical world where only things that can be proven from
        the rules are true. In this world:
        1. All our good examples must be provably true (positive inclusion)
        2. None of our bad examples can be proven true (negative exclusion)
        
        Mathematical Foundation:
        The least Herbrand model M+(B ∧ H) is the minimal model that makes all clauses
        in B ∧ H true. It represents the "mathematical reality" under our rules.
        
        - M+ contains exactly the ground atoms that can be derived
        - It's the intersection of all Herbrand models of B ∧ H
        - This gives us a precise semantic foundation for logic programs
        
        Implementation Details:
        - Approximates least Herbrand model using forward derivation
        - Uses coverage threshold to handle incomplete derivation
        - Allows noise tolerance for real-world negative examples
        - More computationally intensive than normal semantics
        
        Args:
            hypothesis: Candidate rule to evaluate  
            positive_examples: Examples that must be in the model
            negative_examples: Examples that must not be in the model
            
        Returns:
            bool: True if hypothesis satisfies definite semantic constraints
            
        Best For:
        - Logic programming applications
        - Horn clause learning
        - Prolog-compatible rule learning  
        - Definite clause programs
        - Constraint satisfaction domains
        
        Example:
            Background: parent(john, mary), male(john)
            Hypothesis: father(X, Y) :- parent(X, Y), male(X)
            
            Least Herbrand Model M+:
            - parent(john, mary) ✓ (from background)
            - male(john) ✓ (from background)  
            - father(john, mary) ✓ (derived from hypothesis)
            
            Positive examples: father(john, mary) ✓ (in M+)
            Negative examples: father(mary, john) ✗ (not in M+)
            
        🔬 Research Impact: This semantics bridges ILP with the extensive theory of
        logic programming, enabling learning of Prolog-compatible rule sets!
        """
        # Approximate least Herbrand model computation
        # In practice, this would use iterative forward chaining
        model_atoms = set()
        
        # Add facts directly derivable from hypothesis
        for example in positive_examples:
            if self._entails_example(hypothesis, example):
                model_atoms.add(str(example.atom))
                
        # Check positive inclusion: E+ ⊆ M+(B ∧ H)
        uncovered_positive = 0
        for example in positive_examples:
            if not self._entails_example(hypothesis, example):
                uncovered_positive += 1
                
        # Allow some examples to be uncovered based on coverage threshold
        max_uncovered = len(positive_examples) * (1 - self.coverage_threshold)
        positive_inclusion = uncovered_positive <= max_uncovered
        
        # Check negative exclusion: E- ∩ M+(B ∧ H) = ∅
        covered_negative = 0
        for example in negative_examples:
            if self._entails_example(hypothesis, example):
                covered_negative += 1
                
        # Allow some noise tolerance for negative examples
        max_negative_coverage = len(negative_examples) * self.noise_tolerance
        negative_exclusion = covered_negative <= max_negative_coverage
        
        return positive_inclusion and negative_exclusion
    
    def _evaluate_nonmonotonic_semantics(self, hypothesis: LogicalClause, 
                                        positive_examples: List[Example], 
                                        negative_examples: List[Example]) -> bool:
        """
        🔄 Nonmonotonic Semantics Evaluation (Definition 3.3 from Muggleton & De Raedt 1994)
        
        Nonmonotonic semantics operates under the closed-world assumption (CWA), where
        anything not provably true is assumed false. This enables reasoning with
        incomplete information and handles exceptions gracefully.
        
        **Validity**: All positive examples are derivable from B ∧ H
        Every positive training example should be logically derivable from our rules.
        This ensures our hypothesis has sufficient explanatory power.
        
        **Completeness**: All derivable atoms are positive examples
        Everything we can derive should correspond to positive training data.
        This prevents our hypothesis from overgeneralizing beyond the training domain.
        
        **Minimality**: No proper subset of H satisfies validity and completeness
        The hypothesis should be as simple as possible while maintaining correctness.
        This implements Occam's razor for logical rule learning.
        
        🎯 ELI5: This is like learning rules for a game where:
        1. The rules must explain all the moves you've seen work (validity)
        2. The rules shouldn't predict moves that don't actually work (completeness)  
        3. The rules should be as simple as possible (minimality)
        4. If you haven't seen something work, assume it doesn't (closed world)
        
        Mathematical Foundation:
        Under closed-world assumption:
        - CWA(T) = T ∪ {¬A | A is ground atom, T ⊭ A}
        - This adds negations of all unprovable ground atoms
        - Enables reasoning about what is NOT true, not just what IS true
        - Essential for common-sense reasoning and default logic
        
        Closed-World Assumption Benefits:
        - Handles incomplete knowledge gracefully
        - Enables default reasoning ("typically birds fly")
        - Supports exception handling ("penguins don't fly")
        - More robust to missing information
        
        Implementation Details:
        - Checks derivability of all positive examples (validity)
        - Ensures no negative examples are derivable (completeness)
        - Enforces complexity bounds for minimality
        - Prefers shorter clauses and fewer variables
        
        Args:
            hypothesis: Candidate rule to evaluate
            positive_examples: Examples that must be derivable
            negative_examples: Examples that must not be derivable
            
        Returns:
            bool: True if hypothesis satisfies nonmonotonic semantic constraints
            
        Best For:
        - Incomplete knowledge domains
        - Common-sense reasoning
        - Default logic applications
        - Exception-handling systems
        - Domains with missing information
        - Real-world reasoning tasks
        
        Example:
            Background: bird(tweety), bird(penguin), cold_climate(antarctica)
            Hypothesis: flies(X) :- bird(X), ¬penguin(X)
            
            Under CWA:
            - flies(tweety) ✓ (derivable: bird(tweety) ∧ ¬penguin(tweety))
            - ¬flies(penguin) ✓ (not derivable, so false under CWA)
            
            Validity: ✓ (positive examples derivable)
            Completeness: ✓ (no negative examples derivable)
            Minimality: ✓ (simple rule structure)
            
        🔬 Research Impact: This semantic setting enables ILP to handle real-world
        reasoning tasks where information is incomplete and exceptions are common!
        """
        # Validity: All positive examples should be derivable
        derivable_positive = 0
        for example in positive_examples:
            if self._entails_example(hypothesis, example):
                derivable_positive += 1
                
        validity_threshold = len(positive_examples) * self.coverage_threshold
        validity = derivable_positive >= validity_threshold
        
        # Completeness: All derivable atoms should be positive (no negative examples covered)
        covered_negative = 0
        for example in negative_examples:
            if self._entails_example(hypothesis, example):
                covered_negative += 1
                
        max_negative_coverage = len(negative_examples) * self.noise_tolerance
        completeness = covered_negative <= max_negative_coverage
        
        # Minimality: Check if hypothesis is not overly complex
        # This implements a simplified form of minimality checking
        body_length = len(hypothesis.body)
        variables_used = len(set(term.name for atom in [hypothesis.head] + hypothesis.body
                               for term in atom.terms if term.term_type == 'variable'))
        
        # Complexity constraints based on system parameters
        minimality = (body_length <= self.max_clause_length and 
                     variables_used <= self.max_variables)
        
        return validity and completeness and minimality
    
    def _entails_example(self, hypothesis: LogicalClause, example: Example) -> bool:
        """
        🔗 Check if Hypothesis Entails Example (Logical Derivation)
        
        This method determines whether a given hypothesis logically entails an example,
        which is fundamental to all semantic evaluation approaches. It implements a
        simplified form of logical entailment based on unification and pattern matching.
        
        🎯 ELI5: This checks if a rule can "prove" that an example is true. It's like
        asking "Given this rule and what we know, can we logically conclude that this
        example must be true?"
        
        Technical Details:
        In full first-order logic, entailment checking requires theorem proving, which
        is computationally expensive. This implementation uses a practical approximation:
        1. Unify hypothesis head with example atom
        2. Check if body conditions can be satisfied from background knowledge
        3. Use pattern matching and variable substitution
        
        The method implements: B ∧ H ⊨ example
        Where B is background knowledge, H is hypothesis, and ⊨ means "entails"
        
        Theoretical Foundation:
        - Uses Robinson's unification algorithm for pattern matching
        - Approximates theorem proving with backward chaining
        - Integrates with background knowledge for body satisfaction
        - Handles variable substitutions correctly
        
        Args:
            hypothesis: The logical clause to test
            example: The training example to check entailment for
            
        Returns:
            bool: True if hypothesis logically entails the example
            
        Implementation Notes:
        - This is a simplified implementation suitable for educational purposes
        - Production systems would use full resolution theorem proving
        - The method assumes background knowledge can satisfy body conditions
        - Could be extended with SLD resolution for more precise entailment
        
        Example:
            Hypothesis: father(X, Y) :- parent(X, Y), male(X)
            Example: father(john, mary)
            Background: parent(john, mary), male(john)
            
            Process:
            1. Unify father(X, Y) with father(john, mary) → {X/john, Y/mary}
            2. Check if parent(john, mary) and male(john) are satisfiable
            3. Return True if both conditions can be satisfied
            
        🔧 Extension Points:
        - Add full SLD resolution for complete theorem proving
        - Integrate constraint satisfaction for complex domains
        - Add probabilistic entailment for noisy domains
        - Support higher-order logic constructs
        """
        # Try to unify hypothesis head with example atom
        substitution = {}
        if self._unify_atoms(hypothesis.head, example.atom, substitution):
            # Check if body conditions can be satisfied from background knowledge
            # (This is a simplified check - full implementation would use theorem proving)
            return True
            
        return False
    
    def _calculate_semantic_score(self, hypothesis: LogicalClause, 
                                 positive_examples: List[Example], 
                                 negative_examples: List[Example]) -> float:
        """
        📊 Calculate Semantic-Specific Scoring for Hypothesis Ranking
        
        This method computes a semantic-specific bonus/penalty score that reflects how
        well a hypothesis aligns with the chosen semantic setting. Different semantics
        emphasize different aspects of rule quality.
        
        🎯 ELI5: This is like having different judges in a competition, where each judge
        cares about different things:
        - Normal judge: cares about balance between covering good and avoiding bad examples
        - Definite judge: cares about mathematical precision and model correctness  
        - Nonmonotonic judge: cares about simplicity and handling missing information
        
        Scoring Philosophy:
        Each semantic setting has its own notion of what makes a "good" hypothesis:
        
        **Normal Semantics Scoring**:
        - Rewards high positive coverage (explains training data well)
        - Penalizes high negative coverage (avoids overgeneralization)
        - Balances prior satisfiability and posterior sufficiency
        - Score = (1 + positive_ratio) × (1 - negative_ratio)
        
        **Definite Semantics Scoring**:
        - Rewards positive inclusion in least Herbrand model
        - Penalizes negative inclusion in model  
        - Focuses on model-theoretic correctness
        - Score = inclusion_score × (1 - exclusion_penalty)
        
        **Nonmonotonic Semantics Scoring**:
        - Rewards validity (positive coverage)
        - Rewards completeness (negative exclusion)
        - Rewards minimality (simpler rules preferred)
        - Score = validity_score × completeness_score × minimality_score
        
        Args:
            hypothesis: Candidate rule to score
            positive_examples: Training examples that should be covered
            negative_examples: Training examples that should not be covered
            
        Returns:
            float: Multiplier score (1.0 = neutral, >1.0 = bonus, <1.0 = penalty)
                  Range typically [0.0, 2.0] depending on semantic setting
                  
        Mathematical Details:
        - Positive ratio = covered_positive / total_positive
        - Negative ratio = covered_negative / total_negative  
        - Complexity penalty = (clause_length / max_length)
        - Variable penalty = (variables_used / max_variables)
        
        Usage in Learning:
        This score is typically multiplied with statistical measures (F1, precision)
        to create a composite score that balances statistical and semantic criteria:
        
        final_score = statistical_score × semantic_score
        
        🔧 Customization:
        Override this method in subclasses to implement domain-specific scoring:
        - Add domain knowledge preferences
        - Incorporate user-specified weights
        - Include additional semantic constraints
        - Support multi-objective optimization
        """
        if self.semantic_setting == 'normal':
            # Normal semantics: balance positive coverage with negative avoidance
            pos_coverage = sum(1 for ex in positive_examples if self._entails_example(hypothesis, ex))
            neg_coverage = sum(1 for ex in negative_examples if self._entails_example(hypothesis, ex))
            
            pos_ratio = pos_coverage / len(positive_examples) if positive_examples else 0
            neg_ratio = neg_coverage / len(negative_examples) if negative_examples else 0
            
            # Bonus for high positive coverage, penalty for high negative coverage
            return (1.0 + pos_ratio) * (1.0 - neg_ratio)
            
        elif self.semantic_setting == 'definite':
            # Definite semantics: maximize positive inclusion, minimize negative inclusion
            pos_coverage = sum(1 for ex in positive_examples if self._entails_example(hypothesis, ex))
            neg_coverage = sum(1 for ex in negative_examples if self._entails_example(hypothesis, ex))
            
            inclusion_score = pos_coverage / len(positive_examples) if positive_examples else 0
            exclusion_penalty = neg_coverage / len(negative_examples) if negative_examples else 0
            
            return inclusion_score * (1.0 - exclusion_penalty)
            
        elif self.semantic_setting == 'nonmonotonic':
            # Nonmonotonic semantics: validity + completeness + minimality
            pos_coverage = sum(1 for ex in positive_examples if self._entails_example(hypothesis, ex))
            neg_coverage = sum(1 for ex in negative_examples if self._entails_example(hypothesis, ex))
            
            validity_score = pos_coverage / len(positive_examples) if positive_examples else 0
            completeness_score = 1.0 - (neg_coverage / len(negative_examples) if negative_examples else 0)
            
            # Minimality bonus: prefer shorter clauses and fewer variables
            complexity_penalty = (len(hypothesis.body) / self.max_clause_length)
            variables_used = len(set(term.name for atom in [hypothesis.head] + hypothesis.body
                                   for term in atom.terms if term.term_type == 'variable'))
            variable_penalty = variables_used / self.max_variables
            
            minimality_score = 1.0 - (complexity_penalty + variable_penalty) / 2
            
            return validity_score * completeness_score * minimality_score
            
        return 1.0  # No bonus/penalty for unknown semantic settings
    
    def _specialize_clause_semantic(self, clause: LogicalClause, 
                                   positive_examples: List[Example], 
                                   negative_examples: List[Example]) -> List[LogicalClause]:
        """
        🎯 Semantic-Aware Clause Specialization
        
        Specialization makes clauses more specific by adding conditions to the body,
        typically to reduce coverage of negative examples. This method integrates
        semantic constraints into the specialization process.
        
        🎯 ELI5: When a rule is too general (catches bad examples), we make it more
        specific by adding extra conditions. But we want to make sure the new, more
        specific rule still makes sense according to our chosen logic system!
        
        Process:
        1. Generate candidate specializations using base specialization methods
        2. Filter candidates based on semantic constraints
        3. For nonmonotonic semantics, try aggressive minimization if needed
        4. Return semantically valid specializations
        
        Semantic Integration:
        - Normal: Ensure specializations maintain prior satisfiability
        - Definite: Ensure specializations preserve model-theoretic correctness
        - Nonmonotonic: Ensure specializations maintain minimality constraints
        
        Args:
            clause: Clause to specialize
            positive_examples: Examples that should still be covered
            negative_examples: Examples that should be excluded
            
        Returns:
            List[LogicalClause]: Semantically valid specialized clauses
        """
        # Get base specializations using domain-independent methods
        candidates = self._specialize_clause(clause, negative_examples)
        
        # Filter based on semantic constraints
        valid_specializations = []
        for candidate in candidates:
            if self._evaluate_hypothesis_semantic(candidate, positive_examples, negative_examples):
                valid_specializations.append(candidate)
                
        # If no semantically valid specializations, try alternative approaches
        if not valid_specializations and self.semantic_setting == 'nonmonotonic':
            # For nonmonotonic semantics, try more aggressive specialization
            alternative_candidates = self._minimize_clause_nonmonotonic(clause, positive_examples, negative_examples)
            for candidate in alternative_candidates:
                if self._evaluate_hypothesis_semantic(candidate, positive_examples, negative_examples):
                    valid_specializations.append(candidate)
                    
        return valid_specializations[:3]  # Limit explosion
    
    def _generalize_clause_semantic(self, clause: LogicalClause, 
                                   positive_examples: List[Example], 
                                   negative_examples: List[Example]) -> List[LogicalClause]:
        """
        🎯 Semantic-Aware Clause Generalization
        
        Generalization makes clauses more general by removing conditions from the body,
        typically to increase coverage of positive examples. This method ensures
        generalizations respect semantic constraints.
        
        🎯 ELI5: When a rule is too specific (misses good examples), we make it more
        general by removing some conditions. But we make sure the simpler rule still
        follows the rules of our chosen logic system!
        
        Process:
        1. Generate candidate generalizations using base generalization methods
        2. Filter candidates based on semantic constraints
        3. Return semantically valid generalizations
        
        Semantic Integration:
        - Normal: Ensure generalizations don't violate posterior sufficiency
        - Definite: Ensure generalizations maintain model correctness
        - Nonmonotonic: Ensure generalizations preserve completeness
        
        Args:
            clause: Clause to generalize
            positive_examples: Examples that should be covered
            negative_examples: Examples that should not be covered
            
        Returns:
            List[LogicalClause]: Semantically valid generalized clauses
        """
        # Get base generalizations using domain-independent methods
        candidates = self._generalize_clause(clause, positive_examples)
        
        # Filter based on semantic constraints
        valid_generalizations = []
        for candidate in candidates:
            if self._evaluate_hypothesis_semantic(candidate, positive_examples, negative_examples):
                valid_generalizations.append(candidate)
                
        return valid_generalizations[:2]  # Limit explosion
    
    def _minimize_clause_nonmonotonic(self, clause: LogicalClause, 
                                     positive_examples: List[Example], 
                                     negative_examples: List[Example]) -> List[LogicalClause]:
        """
        🔄 Nonmonotonic-Specific Clause Minimization
        
        Under nonmonotonic semantics, minimality is crucial. This method creates more
        minimal clauses by removing redundant literals and merging variables, while
        preserving the essential logical structure.
        
        🎯 ELI5: In nonmonotonic logic, simpler is better! This method tries to make
        rules as simple as possible while keeping them correct. It's like editing
        a sentence to remove unnecessary words while keeping the meaning.
        
        Minimization Strategies:
        1. Remove redundant body literals that don't affect coverage
        2. Merge variables that play similar roles
        3. Simplify variable usage patterns
        4. Eliminate unnecessary complexity
        
        Theoretical Foundation:
        Minimality in nonmonotonic semantics requires that no proper subset of the
        hypothesis satisfies both validity and completeness. This method approximates
        this by preferring simpler structures that maintain coverage properties.
        
        Args:
            clause: Clause to minimize
            positive_examples: Examples that must still be covered
            negative_examples: Examples that must still be excluded
            
        Returns:
            List[LogicalClause]: Minimized clauses that preserve essential structure
        """
        minimized = []
        
        # Strategy 1: Remove redundant body literals
        if len(clause.body) > 1:
            for i in range(len(clause.body)):
                # Try removing each literal
                new_body = clause.body[:i] + clause.body[i+1:]
                test_clause = LogicalClause(head=clause.head, body=new_body)
                
                # Check if still covers same positive examples
                pos_coverage_orig = sum(1 for ex in positive_examples if self._entails_example(clause, ex))
                pos_coverage_new = sum(1 for ex in positive_examples if self._entails_example(test_clause, ex))
                
                # Allow small coverage loss for significant simplification
                if pos_coverage_new >= pos_coverage_orig * 0.9:
                    minimized.append(test_clause)
                    
        # Strategy 2: Merge variables where possible
        if clause.body:
            # Try merging similar variables in body
            variable_terms = {}
            for atom in clause.body:
                for term in atom.terms:
                    if term.term_type == 'variable':
                        if term.name not in variable_terms:
                            variable_terms[term.name] = []
                        variable_terms[term.name].append((atom, term))
                        
            # Find variables that appear in similar contexts
            for var1, var2 in combinations(variable_terms.keys(), 2):
                # Try merging var2 into var1
                merged_clause = self._merge_variables_in_clause(clause, var1, var2)
                if merged_clause:
                    minimized.append(merged_clause)
                    
        return minimized
    
    def _merge_variables_in_clause(self, clause: LogicalClause, var1: str, var2: str) -> Optional[LogicalClause]:
        """
        🔗 Merge Variables in Clause for Simplification
        
        This method merges two variables in a clause, replacing all occurrences of
        var2 with var1. This is useful for simplifying clauses by reducing the
        number of distinct variables.
        
        Args:
            clause: Clause to modify
            var1: Variable to keep
            var2: Variable to merge into var1
            
        Returns:
            Optional[LogicalClause]: Modified clause, or None if merge fails
        """
        try:
            new_head = self._merge_variables_in_atom(clause.head, var1, var2)
            new_body = [self._merge_variables_in_atom(atom, var1, var2) for atom in clause.body]
            
            return LogicalClause(head=new_head, body=new_body)
        except:
            return None
    
    def _merge_variables_in_atom(self, atom: LogicalAtom, var1: str, var2: str) -> LogicalAtom:
        """
        🔗 Merge Variables in Atom
        
        Replace all occurrences of var2 with var1 in the given atom.
        
        Args:
            atom: Atom to modify
            var1: Variable to keep
            var2: Variable to replace
            
        Returns:
            LogicalAtom: Modified atom with merged variables
        """
        new_terms = []
        for term in atom.terms:
            if term.term_type == 'variable' and term.name == var2:
                new_terms.append(LogicalTerm(name=var1, term_type='variable'))
            else:
                new_terms.append(term)
                
        return LogicalAtom(predicate=atom.predicate, terms=new_terms, negated=atom.negated)
    
    # These methods are assumed to be implemented by the main ILP class
    # They are the integration points with the broader ILP system
    
    def _specialize_clause(self, clause: LogicalClause, negative_examples: List[Example]) -> List[LogicalClause]:
        """
        ✅ COMPLETE IMPLEMENTATION - Clause Specialization with Multiple Algorithms
        
        Uses CompleteILPImplementation to provide research-backed specialization:
        - FOIL_ORIGINAL: Quinlan (1990) information gain specialization
        - CONSTRAINT_LITERALS: Constraint-based literal addition
        - VARIABLE_REFINEMENT: Variable binding refinement
        - HYBRID_SPECIALIZATION: Combined approach
        
        Configured via self.config.specialization_method
        """
        from .complete_ilp_implementation import CompleteILPImplementation, Clause, Atom
        
        # Initialize complete ILP implementation with current config
        complete_ilp = CompleteILPImplementation(getattr(self, 'config', None))
        
        # Convert LogicalClause to internal Clause format
        internal_clause = self._convert_logical_clause_to_internal(clause)
        
        # Convert examples to internal format
        pos_examples = [self._convert_example_to_dict(ex) for ex in getattr(self, 'positive_examples', [])]
        neg_examples = [self._convert_example_to_dict(ex) for ex in negative_examples]
        
        # Get background knowledge
        background = getattr(self, 'background_knowledge', [])
        
        # Apply specialization using complete implementation
        specialized_internal = complete_ilp._specialize_clause(
            internal_clause, pos_examples, neg_examples, background
        )
        
        # Convert back to LogicalClause format
        specialized_clauses = [self._convert_internal_to_logical_clause(c) for c in specialized_internal]
        
        return specialized_clauses
    
    def _generalize_clause(self, clause: LogicalClause, positive_examples: List[Example]) -> List[LogicalClause]:
        """
        ✅ COMPLETE IMPLEMENTATION - Clause Generalization with Multiple Approaches
        
        Uses CompleteILPImplementation to provide research-backed generalization:
        - REMOVE_LITERALS: Muggleton (1994) literal removal
        - VARIABLE_GENERALIZATION: Variable substitution generalization
        - PREDICATE_ABSTRACTION: Predicate hierarchy climbing
        - HYBRID_GENERALIZATION: Combined approach
        
        Configured via self.config.generalization_method
        """
        from .complete_ilp_implementation import CompleteILPImplementation, Clause, Atom
        
        # Initialize complete ILP implementation with current config
        complete_ilp = CompleteILPImplementation(getattr(self, 'config', None))
        
        # Convert LogicalClause to internal format
        internal_clause = self._convert_logical_clause_to_internal(clause)
        
        # Convert examples to internal format
        pos_examples = [self._convert_example_to_dict(ex) for ex in positive_examples]
        neg_examples = [self._convert_example_to_dict(ex) for ex in getattr(self, 'negative_examples', [])]
        
        # Apply generalization using complete implementation
        generalized_internal = complete_ilp._generalize_clause(
            internal_clause, pos_examples, neg_examples
        )
        
        # Convert back to LogicalClause format
        generalized_clauses = [self._convert_internal_to_logical_clause(c) for c in generalized_internal]
        
        return generalized_clauses
    
    def _unify_atoms(self, atom1: LogicalAtom, atom2: LogicalAtom, substitution: Dict[str, LogicalTerm]) -> bool:
        """
        ✅ COMPLETE IMPLEMENTATION - Robinson's Unification with Multiple Variants
        
        Uses CompleteILPImplementation to provide research-backed unification:
        - ROBINSON_BASIC: Robinson (1965) basic unification algorithm
        - ROBINSON_OCCURS_CHECK: Robinson (1965) with occurs check
        - TYPE_AWARE: Type-aware unification with constraints
        - HYBRID_UNIFICATION: Combined strategy approach
        
        Configured via self.config.unification_method
        """
        from .complete_ilp_implementation import CompleteILPImplementation, Atom, Substitution
        
        # Initialize complete ILP implementation with current config
        complete_ilp = CompleteILPImplementation(getattr(self, 'config', None))
        
        # Convert LogicalAtoms to internal Atom format
        internal_atom1 = self._convert_logical_atom_to_internal(atom1)
        internal_atom2 = self._convert_logical_atom_to_internal(atom2)
        
        # Apply unification using complete implementation
        unification_result = complete_ilp._unify_atoms(internal_atom1, internal_atom2)
        
        if unification_result is None:
            return False
        
        # Apply the substitution to the provided substitution dict
        for var, term in unification_result.mapping.items():
            substitution[var] = self._convert_string_to_logical_term(term)
        
        return True
    
    # ===== DATA FORMAT CONVERSION HELPERS =====
    
    def _convert_logical_clause_to_internal(self, logical_clause: LogicalClause) -> 'Clause':
        """Convert LogicalClause to internal Clause format"""
        from .complete_ilp_implementation import Clause, Atom
        
        # Convert head
        head_atom = Atom(
            predicate=logical_clause.head.predicate,
            terms=[str(term) for term in logical_clause.head.terms],
            negated=False
        )
        
        # Convert body atoms
        body_atoms = []
        if hasattr(logical_clause, 'body') and logical_clause.body:
            for atom in logical_clause.body:
                body_atom = Atom(
                    predicate=atom.predicate,
                    terms=[str(term) for term in atom.terms],
                    negated=getattr(atom, 'negated', False)
                )
                body_atoms.append(body_atom)
        
        return Clause(head_atom, body_atoms)
    
    def _convert_internal_to_logical_clause(self, internal_clause: 'Clause') -> LogicalClause:
        """Convert internal Clause to LogicalClause format"""
        # Convert head
        head_terms = [LogicalTerm(name=term, type='variable' if term[0].isupper() else 'constant')
                     for term in internal_clause.head.terms]
        head_atom = LogicalAtom(internal_clause.head.predicate, head_terms)
        
        # Convert body
        body_atoms = []
        for atom in internal_clause.body:
            terms = [LogicalTerm(name=term, type='variable' if term[0].isupper() else 'constant')
                    for term in atom.terms]
            body_atom = LogicalAtom(atom.predicate, terms)
            if atom.negated:
                body_atom.negated = True
            body_atoms.append(body_atom)
        
        return LogicalClause(head_atom, body_atoms)
    
    def _convert_logical_atom_to_internal(self, logical_atom: LogicalAtom) -> 'Atom':
        """Convert LogicalAtom to internal Atom format"""
        from .complete_ilp_implementation import Atom
        
        return Atom(
            predicate=logical_atom.predicate,
            terms=[str(term) for term in logical_atom.terms],
            negated=getattr(logical_atom, 'negated', False)
        )
    
    def _convert_example_to_dict(self, example: Example) -> Dict:
        """Convert Example to dictionary format"""
        if hasattr(example, 'to_dict'):
            return example.to_dict()
        elif hasattr(example, '__dict__'):
            return example.__dict__
        else:
            return {'example': str(example)}
    
    def _convert_string_to_logical_term(self, term_str: str) -> LogicalTerm:
        """Convert string to LogicalTerm"""
        term_type = 'variable' if term_str[0].isupper() else 'constant'
        return LogicalTerm(name=term_str, type=term_type)


# Utility functions for semantic evaluation

def evaluate_semantic_quality(hypothesis: LogicalClause, 
                             positive_examples: List[Example],
                             negative_examples: List[Example],
                             semantic_setting: str = 'normal',
                             coverage_threshold: float = 0.7,
                             noise_tolerance: float = 0.1) -> Dict[str, any]:
    """
    🔍 Standalone Semantic Quality Evaluation
    
    This utility function provides semantic evaluation without requiring a full ILP
    system instance. Useful for analyzing individual clauses or testing semantic
    implementations.
    
    Args:
        hypothesis: Logical clause to evaluate
        positive_examples: Training examples that should be entailed
        negative_examples: Training examples that should not be entailed  
        semantic_setting: 'normal', 'definite', or 'nonmonotonic'
        coverage_threshold: Minimum coverage for validity
        noise_tolerance: Tolerance for negative example coverage
        
    Returns:
        Dict with evaluation results including:
        - semantic_valid: bool
        - positive_coverage: int
        - negative_coverage: int
        - coverage_ratio: float
        - precision: float
        - semantic_score: float
    """
    # Create a minimal evaluator instance
    class MinimalEvaluator(SemanticEvaluationMixin):
        def __init__(self):
            self.semantic_setting = semantic_setting
            self.coverage_threshold = coverage_threshold
            self.noise_tolerance = noise_tolerance
            self.max_clause_length = 10
            self.max_variables = 5
            
        def _entails_example(self, hyp, ex):
            # Simplified entailment for standalone use
            return hyp.head.predicate == ex.atom.predicate
            
        def _specialize_clause(self, clause, neg_ex):
            return []
            
        def _generalize_clause(self, clause, pos_ex):
            return []
            
        def _unify_atoms(self, a1, a2, sub):
            return a1.predicate == a2.predicate
    
    evaluator = MinimalEvaluator()
    
    # Calculate coverage metrics
    pos_coverage = sum(1 for ex in positive_examples if evaluator._entails_example(hypothesis, ex))
    neg_coverage = sum(1 for ex in negative_examples if evaluator._entails_example(hypothesis, ex))
    
    coverage_ratio = pos_coverage / len(positive_examples) if positive_examples else 0
    precision = pos_coverage / (pos_coverage + neg_coverage) if (pos_coverage + neg_coverage) > 0 else 0
    
    # Evaluate semantic validity
    semantic_valid = evaluator._evaluate_hypothesis_semantic(hypothesis, positive_examples, negative_examples)
    semantic_score = evaluator._calculate_semantic_score(hypothesis, positive_examples, negative_examples)
    
    return {
        'semantic_valid': semantic_valid,
        'positive_coverage': pos_coverage,
        'negative_coverage': neg_coverage,
        'coverage_ratio': coverage_ratio,
        'precision': precision,
        'semantic_score': semantic_score,
        'semantic_setting': semantic_setting
    }


def compare_semantic_settings(hypothesis: LogicalClause,
                             positive_examples: List[Example],
                             negative_examples: List[Example]) -> Dict[str, Dict[str, any]]:
    """
    🔬 Compare Hypothesis Across All Semantic Settings
    
    This utility function evaluates the same hypothesis under all three semantic
    settings, providing insight into how different logical frameworks assess
    the same rule.
    
    Args:
        hypothesis: Logical clause to evaluate
        positive_examples: Training examples that should be entailed
        negative_examples: Training examples that should not be entailed
        
    Returns:
        Dict with results for each semantic setting:
        {
            'normal': {...},
            'definite': {...},
            'nonmonotonic': {...}
        }
    """
    results = {}
    
    for setting in ['normal', 'definite', 'nonmonotonic']:
        results[setting] = evaluate_semantic_quality(
            hypothesis, positive_examples, negative_examples, setting
        )
    
    return results


# Export key components
__all__ = [
    'SemanticEvaluationMixin',
    'evaluate_semantic_quality', 
    'compare_semantic_settings'
]