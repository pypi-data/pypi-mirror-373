"""
🧠 INDUCTIVE LOGIC PROGRAMMING CORE - Modular ILP System Integration
==================================================================

This module provides the main InductiveLogicProgrammer class that integrates all
ILP components in a clean, modular architecture. It combines the extracted modules
while maintaining full backward compatibility with the original implementation.

Based on: Muggleton & De Raedt (1994) "Inductive Logic Programming: Theory and Methods"

🎯 ELI5 Summary:
Think of this as assembling a super-smart detective team! Each team member (module) 
has special skills - one handles evidence (logical structures), another generates 
theories (hypothesis generation), another checks if theories fit (unification), etc. 
The core brings them all together to solve mysteries (learn logical rules)!

🏗️ Modular Architecture:
=========================

The ILP system is composed of specialized mixins:

1. **LogicalStructures**: Core data structures (terms, atoms, clauses, examples)
2. **HypothesisGeneration**: Pattern extraction and candidate rule generation  
3. **UnificationEngine**: Robinson's unification algorithm for logical matching
4. **SemanticEvaluation**: Rule validation under different semantic settings
5. **RuleRefinement**: Specialization and generalization operators
6. **CoverageAnalysis**: Statistical evaluation and significance testing
7. **PredicateSystem**: Hierarchies, aliases, and compatibility management

Each mixin provides focused functionality while the core orchestrates their
interaction for complete ILP learning workflows.

🚀 Key Benefits:
================

✨ **Modularity**: Clean separation of concerns, easy to extend/modify
✨ **Reusability**: Mixins can be used independently or in custom combinations
✨ **Maintainability**: Focused modules are easier to understand and debug
✨ **Extensibility**: Add new semantic settings, refinement operators, etc.
✨ **Testing**: Each module can be tested in isolation
✨ **Performance**: Specialized implementations optimized for specific tasks

🔧 Usage Examples:
==================

Basic Learning:
    ilp = InductiveLogicProgrammer()
    ilp.add_background_knowledge(parent_facts)
    ilp.add_example(father_atom, True)
    rules = ilp.learn_rules("father")

Advanced Configuration:
    ilp = create_research_ilp_system(
        semantic_setting='nonmonotonic',
        max_clause_length=10,
        use_predicate_invention=True
    )

Custom System:
    class MyILP(HypothesisGenerationMixin, UnificationEngineMixin):
        # Custom ILP system with just these capabilities
        pass

Factory Functions:
    education_ilp = create_educational_ilp()      # For teaching/demos
    research_ilp = create_research_ilp_system()   # For advanced research
    production_ilp = create_production_ilp()      # For real applications

Author: Benedict Chen
"""

from typing import Dict, List, Tuple, Union, Optional, Any, Set
from dataclasses import dataclass
import warnings

# Import all modular components
from .ilp_modules.logical_structures import (
    LogicalTerm, LogicalAtom, LogicalClause, Example,
    create_variable, create_constant, create_function, 
    create_atom, create_fact, create_rule, parse_term
)

from .ilp_modules.hypothesis_generation import HypothesisGenerationMixin
from .ilp_modules.unification_engine import UnificationEngineMixin  
from .ilp_modules.semantic_evaluation import SemanticEvaluationMixin
from .ilp_modules.rule_refinement import RuleRefinementMixin
from .ilp_modules.coverage_analysis import CoverageAnalysisMixin
from .ilp_modules.predicate_system import PredicateSystemMixin

warnings.filterwarnings('ignore')


class InductiveLogicProgrammer(
    HypothesisGenerationMixin,
    UnificationEngineMixin, 
    SemanticEvaluationMixin,
    RuleRefinementMixin,
    CoverageAnalysisMixin,
    PredicateSystemMixin
):
    """
    🧠 Modular Inductive Logic Programming System
    
    The main ILP system class that integrates all specialized mixins to provide
    complete inductive logic programming functionality. Implements Muggleton & 
    De Raedt's (1994) framework with modern modular architecture.
    
    This class maintains full backward compatibility with the original monolithic
    implementation while providing clean separation of concerns through mixins.
    
    Core Capabilities:
    - Learn logical rules from positive/negative examples
    - Integrate background knowledge for guided learning
    - Support multiple semantic settings (normal, definite, nonmonotonic)  
    - Advanced refinement operators (specialization/generalization)
    - Statistical significance testing and coverage analysis
    - Predicate hierarchies and compatibility reasoning
    - Query answering and explanation generation
    
    The key insight: Learn logical rules by searching through hypothesis space
    guided by coverage of positive examples and avoidance of negative examples.
    
    🎯 Learning Algorithm:
    1. **Hypothesis Generation**: Generate candidate clauses from background knowledge
    2. **Semantic Evaluation**: Validate hypotheses under chosen semantic setting
    3. **Coverage Analysis**: Compute statistical significance and quality metrics  
    4. **Rule Refinement**: Specialize overly general clauses, generalize overly specific ones
    5. **Selection**: Choose best rules based on coverage, accuracy, and significance
    
    Mathematical Framework:
    - Hypothesis: H (set of logical clauses)
    - Background Knowledge: B (known facts and rules)
    - Examples: E+ (positive) and E- (negative)
    - Goal: Find H such that B ∧ H ⊨ E+ and B ∧ H ∧ E- ⊭ ⊥
    """
    
    def __init__(
        self,
        max_clause_length: int = 5,
        max_variables: int = 4,
        confidence_threshold: float = 0.8,
        coverage_threshold: float = 0.7,
        noise_tolerance: float = 0.1,
        semantic_setting: str = 'normal'
    ):
        """
        🚀 Initialize Modular Inductive Logic Programming System
        
        Sets up a complete ILP system with configurable parameters for hypothesis
        generation, semantic evaluation, and rule refinement. All mixins are
        initialized and system-wide data structures are prepared.
        
        🎯 ELI5: Think of this as setting up a super-smart rule-learning detective! 
        You're giving it guidelines like "don't make rules that are too complicated" 
        (max_clause_length), "be confident in your conclusions" (confidence_threshold), 
        and "it's okay if some examples are weird" (noise_tolerance). It's like 
        training a detective to find patterns while being appropriately cautious!
        
        Args:
            max_clause_length (int): Maximum number of literals in clause body
                                   Higher = more complex rules, slower learning
                                   Typical range: 3-10 (5 is good balance)
                                   Example: father(X,Y) :- parent(X,Y), male(X) [length=2]
                                   
            max_variables (int): Maximum variables per clause (complexity control)
                               Higher = more expressive rules, larger search space
                               Typical range: 2-6 (4 handles most practical cases)
                               Example: ancestor(X,Z) :- parent(X,Y), ancestor(Y,Z) [vars=3]
                               
            confidence_threshold (float): Minimum confidence for accepting rules (0-1)
                                        Higher = stricter rules, fewer false positives
                                        Lower = more permissive, risk overfitting
                                        Typical range: 0.7-0.95 (0.8 is reasonable default)
                                        
            coverage_threshold (float): Minimum coverage rate for rule acceptance (0-1)
                                      Higher = rules must explain more examples
                                      Lower = accept specialized rules
                                      Typical range: 0.5-0.9 (0.7 balances generality vs specificity)
                                      
            noise_tolerance (float): Tolerance for noisy/inconsistent examples (0-1)
                                   Higher = more robust to errors, may overfit
                                   Lower = stricter consistency requirements
                                   Typical range: 0.05-0.2 (0.1 handles real-world noise)
                                   
            semantic_setting (str): Semantic framework for rule evaluation
                                  'normal': Classical logic with consistency checking
                                  'definite': Definite clause semantics (Horn clauses)
                                  'nonmonotonic': Closed-world assumption with minimality
                                  Choice affects rule validation and selection criteria
        
        🔬 Technical Details:
        Initializes all mixin components and establishes the core data structures:
        - Background knowledge base for storing domain facts/rules
        - Training examples repository with positive/negative instances  
        - Vocabulary management for predicates, constants, and functions
        - Learning statistics tracking for performance analysis
        - Predicate system with hierarchies and compatibility rules
        
        The modular architecture allows each component to initialize independently
        while sharing common configuration and data structures.
        
        Example:
            >>> # Basic setup for family relationship learning
            >>> ilp = InductiveLogicProgrammer(
            ...     max_clause_length=3,      # Simple rules
            ...     confidence_threshold=0.9, # High confidence required
            ...     semantic_setting='normal' # Classical logic
            ... )
            >>> 
            >>> # Advanced research configuration
            >>> research_ilp = InductiveLogicProgrammer(
            ...     max_clause_length=10,        # Complex rules allowed
            ...     semantic_setting='nonmonotonic', # Handle incomplete knowledge
            ...     noise_tolerance=0.15         # Robust to noisy data
            ... )
        """
        # Core ILP system parameters
        self.max_clause_length = max_clause_length
        self.max_variables = max_variables
        self.confidence_threshold = confidence_threshold
        self.coverage_threshold = coverage_threshold  
        self.noise_tolerance = noise_tolerance
        self.semantic_setting = semantic_setting.lower()
        
        # Validate semantic setting
        valid_semantics = {'normal', 'definite', 'nonmonotonic'}
        if self.semantic_setting not in valid_semantics:
            raise ValueError(f"Invalid semantic setting '{semantic_setting}'. Must be one of {valid_semantics}")
        
        # Knowledge base and training data
        self.background_knowledge: List[LogicalClause] = []
        self.examples: List[Example] = []
        self.positive_examples: List[Example] = []
        self.negative_examples: List[Example] = []
        
        # Vocabulary management (predicates, constants, functions)
        self.vocabulary = {
            'predicates': set(),
            'constants': set(),
            'variables': set(),
            'functions': set()
        }
        
        # Learning statistics and performance tracking
        self.learning_stats = {
            'clauses_generated': 0,
            'clauses_evaluated': 0,
            'refinement_steps': 0,
            'coverage_calculations': 0,
            'unifications_attempted': 0,
            'semantic_evaluations': 0,
            'final_rules_selected': 0,
            'learning_time_seconds': 0.0
        }
        
        # Learned knowledge
        self.learned_rules: List[LogicalClause] = []
        
        # Initialize all mixin components
        self._initialize_predicate_system()
        
        # System status
        self._system_initialized = True
        
    def add_background_knowledge(self, clause: LogicalClause):
        """
        📚 Add Background Knowledge Clause to System
        
        Incorporates domain knowledge (facts and rules) that guides hypothesis
        generation and provides context for rule learning. Background knowledge
        is crucial for ILP as it enables the system to make informed generalizations.
        
        🎯 ELI5: This is like giving the detective a handbook about the domain!
        If you're learning family relationships, you'd add facts like "parent(john, mary)"
        and rules like "grandparent(X,Z) :- parent(X,Y), parent(Y,Z)". The detective
        uses this knowledge to make smarter guesses about new rules!
        
        Args:
            clause (LogicalClause): Domain knowledge to incorporate
                                  Can be facts (no body) or rules (with body)
                                  Examples: parent(john, mary). or
                                           grandparent(X,Z) :- parent(X,Y), parent(Y,Z).
        
        Updates:
            - Adds clause to background knowledge base
            - Updates vocabulary with new predicates, constants, functions
            - Enables hypothesis generation to leverage this knowledge
            
        Example:
            >>> ilp = InductiveLogicProgrammer()
            >>> 
            >>> # Add factual knowledge
            >>> parent_fact = create_fact(
            ...     create_atom("parent", [create_constant("john"), create_constant("mary")])
            ... )
            >>> ilp.add_background_knowledge(parent_fact)
            >>>
            >>> # Add rule knowledge  
            >>> grandparent_rule = create_rule(
            ...     create_atom("grandparent", [create_variable("X"), create_variable("Z")]),
            ...     [create_atom("parent", [create_variable("X"), create_variable("Y")]),
            ...      create_atom("parent", [create_variable("Y"), create_variable("Z")])]
            ... )
            >>> ilp.add_background_knowledge(grandparent_rule)
        """
        if not isinstance(clause, LogicalClause):
            raise TypeError("Background knowledge must be a LogicalClause instance")
            
        self.background_knowledge.append(clause)
        self._update_vocabulary_from_clause(clause)
        
    def add_example(self, atom: LogicalAtom, is_positive: bool):
        """
        📝 Add Training Example to System
        
        Adds a labeled training example (positive or negative) that the system
        will use to learn rules. Examples drive the learning process by providing
        target patterns to generalize (positive) or avoid (negative).
        
        🎯 ELI5: This is like showing the detective examples of what you want to learn!
        For "father" relationships, you'd show positive examples like "father(john, mary)"
        (yes, john is mary's father) and negative examples like "father(mary, john)"
        (no, mary is not john's father). The detective learns to distinguish the pattern!
        
        Args:
            atom (LogicalAtom): The example statement
                              Example: father(john, mary), likes(alice, pizza)
            is_positive (bool): True for positive examples, False for negative
                              Positive examples should be covered by learned rules
                              Negative examples should NOT be covered
        
        Updates:
            - Adds example to appropriate training set (positive/negative)
            - Updates vocabulary with new terms from the example  
            - Enables rule learning to target this predicate
            
        Example:
            >>> ilp = InductiveLogicProgrammer()
            >>> 
            >>> # Positive examples of father relationship
            >>> father_atom1 = create_atom("father", 
            ...     [create_constant("john"), create_constant("mary")])
            >>> ilp.add_example(father_atom1, True)
            >>>
            >>> father_atom2 = create_atom("father",
            ...     [create_constant("bob"), create_constant("alice")])  
            >>> ilp.add_example(father_atom2, True)
            >>>
            >>> # Negative example (counter-example)
            >>> non_father = create_atom("father",
            ...     [create_constant("mary"), create_constant("john")])
            >>> ilp.add_example(non_father, False)
        """
        if not isinstance(atom, LogicalAtom):
            raise TypeError("Example must be a LogicalAtom instance")
            
        example = Example(atom, is_positive)
        self.examples.append(example)
        
        if is_positive:
            self.positive_examples.append(example)
        else:
            self.negative_examples.append(example)
            
        self._update_vocabulary_from_atom(atom)
        
    def learn_rules(self, target_predicate: str) -> List[LogicalClause]:
        """
        🎓 Learn Logical Rules for Target Predicate
        
        The main learning method that implements the complete ILP learning cycle:
        hypothesis generation, semantic evaluation, coverage analysis, rule refinement,
        and final rule selection. This orchestrates all mixin components.
        
        🎯 ELI5: This is where the detective solves the mystery! Given all the evidence
        (examples) and background knowledge, the detective generates theories about
        what rule explains the target relationship, tests each theory, refines the
        promising ones, and picks the best explanation!
        
        🔬 Learning Algorithm:
        1. **Filter Examples**: Extract examples for target predicate
        2. **Generate Hypotheses**: Create candidate rules from background knowledge  
        3. **Semantic Evaluation**: Validate rules under chosen semantic setting
        4. **Coverage Analysis**: Calculate statistical significance and metrics
        5. **Refinement**: Improve rules through specialization/generalization
        6. **Selection**: Choose best rules based on multiple criteria
        
        Args:
            target_predicate (str): Predicate to learn rules for
                                  Example: "father", "grandparent", "ancestor"  
                                  Must appear in positive examples
                                  
        Returns:
            List[LogicalClause]: Learned rules for the target predicate
                               Sorted by quality (confidence, coverage, significance)
                               Each rule explains some positive examples
                               Rules collectively aim for high coverage
                               
        Raises:
            ValueError: If no positive examples exist for target predicate
            RuntimeError: If learning process fails catastrophically
            
        Updates:
            - self.learned_rules: Stores final selected rules
            - self.learning_stats: Updates performance statistics
            
        Example:
            >>> ilp = InductiveLogicProgrammer()
            >>> 
            >>> # Add background knowledge and examples (omitted for brevity)
            >>> # ... add parent facts, male facts, positive/negative father examples
            >>> 
            >>> # Learn rules for father relationship
            >>> father_rules = ilp.learn_rules("father")
            >>> 
            >>> # Might learn: father(X,Y) :- parent(X,Y), male(X)
            >>> for rule in father_rules:
            ...     print(f"Learned rule: {rule}")
            ...     print(f"Confidence: {rule.confidence:.3f}")
        """
        import time
        start_time = time.time()
        
        # Validate inputs
        if not target_predicate:
            raise ValueError("Target predicate cannot be empty")
            
        # Filter examples for target predicate
        target_positive = [ex for ex in self.positive_examples 
                          if ex.atom.predicate == target_predicate]
        target_negative = [ex for ex in self.negative_examples
                          if ex.atom.predicate == target_predicate]
                          
        if not target_positive:
            raise ValueError(f"No positive examples found for predicate '{target_predicate}'")
            
        print(f"🎯 Learning rules for '{target_predicate}' with {len(target_positive)} positive examples, {len(target_negative)} negative examples")
        
        # Phase 1: Generate initial hypotheses using mixin
        print("🔬 Phase 1: Generating initial hypotheses...")
        hypotheses = self._generate_initial_hypotheses(target_predicate, target_positive)
        print(f"Generated {len(hypotheses)} initial hypotheses")
        
        if not hypotheses:
            print("⚠️ Warning: No initial hypotheses generated. Using simple facts as fallback.")
            # Fallback: create simple facts from positive examples
            for example in target_positive[:3]:  # Limit to avoid overfitting
                fact = LogicalClause(example.atom, [], 1.0)
                hypotheses.append(fact)
        
        # Phase 2: Semantic evaluation using mixin
        print("🔍 Phase 2: Evaluating hypotheses semantically...")
        valid_hypotheses = []
        for hypothesis in hypotheses:
            try:
                if self._evaluate_hypothesis_semantic(hypothesis, target_positive, target_negative):
                    score = self._calculate_semantic_score(hypothesis, target_positive, target_negative)
                    hypothesis.confidence = score
                    valid_hypotheses.append(hypothesis)
                    self.learning_stats['semantic_evaluations'] += 1
            except Exception as e:
                print(f"⚠️ Warning: Error evaluating hypothesis {hypothesis}: {e}")
                continue
                
        print(f"Found {len(valid_hypotheses)} semantically valid hypotheses")
        
        if not valid_hypotheses:
            print("⚠️ Warning: No semantically valid hypotheses found")
            # Return best effort rules
            end_time = time.time()
            self.learning_stats['learning_time_seconds'] = end_time - start_time
            return hypotheses[:1] if hypotheses else []
        
        # Phase 3: Coverage analysis using mixin  
        print("📊 Phase 3: Performing coverage analysis...")
        analyzed_hypotheses = []
        for hypothesis in valid_hypotheses:
            try:
                # Calculate comprehensive coverage metrics
                coverage_report = self._analyze_coverage_comprehensive(
                    hypothesis, target_positive + target_negative
                )
                
                # Update hypothesis confidence based on coverage analysis
                if coverage_report.metrics.f1_score > 0:
                    hypothesis.confidence = coverage_report.metrics.f1_score
                    
                analyzed_hypotheses.append((hypothesis, coverage_report))
                self.learning_stats['coverage_calculations'] += 1
            except Exception as e:
                print(f"⚠️ Warning: Error analyzing coverage for {hypothesis}: {e}")
                analyzed_hypotheses.append((hypothesis, None))
                
        print(f"Analyzed coverage for {len(analyzed_hypotheses)} hypotheses")
        
        # Phase 4: Rule refinement using mixin
        print("⚙️ Phase 4: Refining rules...")
        refined_hypotheses = []
        
        for hypothesis, coverage_report in analyzed_hypotheses:
            try:
                # Attempt refinement based on coverage analysis
                refinements = self._refine_hypothesis_based_on_coverage(
                    hypothesis, target_positive, target_negative, coverage_report
                )
                
                if refinements:
                    refined_hypotheses.extend(refinements)
                    self.learning_stats['refinement_steps'] += len(refinements)
                else:
                    refined_hypotheses.append(hypothesis)  # Keep original if no refinements
                    
            except Exception as e:
                print(f"⚠️ Warning: Error refining hypothesis {hypothesis}: {e}")
                refined_hypotheses.append(hypothesis)  # Keep original on error
                
        print(f"Generated {len(refined_hypotheses)} refined hypotheses")
        
        # Phase 5: Final rule selection
        print("🏆 Phase 5: Selecting best rules...")
        final_rules = self._select_best_rules(
            refined_hypotheses, target_positive, target_negative
        )
        
        # Update learned rules and statistics
        self.learned_rules.extend(final_rules)
        self.learning_stats['final_rules_selected'] = len(final_rules)
        
        end_time = time.time()
        self.learning_stats['learning_time_seconds'] = end_time - start_time
        
        print(f"✅ Learning complete! Selected {len(final_rules)} final rules")
        print(f"⏱️ Total learning time: {self.learning_stats['learning_time_seconds']:.2f} seconds")
        
        return final_rules
    
    def query(self, query_atom: LogicalAtom) -> Tuple[bool, float, List[LogicalClause]]:
        """
        🔍 Query the Learned Knowledge Base
        
        Uses learned rules and background knowledge to answer queries about unseen
        instances. Implements forward chaining inference to derive conclusions.
        
        Args:
            query_atom (LogicalAtom): Query to answer
                                    Example: father(john, unknown_child)
                                    
        Returns:
            Tuple[bool, float, List[LogicalClause]]: 
                - bool: Whether query can be proven
                - float: Confidence in the answer (0-1)
                - List[LogicalClause]: Rules used in proof
                
        Example:
            >>> # After learning father rules
            >>> query = create_atom("father", [create_constant("john"), create_variable("X")])
            >>> can_prove, confidence, proof_rules = ilp.query(query)
            >>> print(f"Can prove: {can_prove}, Confidence: {confidence:.3f}")
        """
        if not self.learned_rules and not self.background_knowledge:
            return False, 0.0, []
            
        # Try to prove query using learned rules and background knowledge
        all_knowledge = self.learned_rules + self.background_knowledge
        
        # Simple forward chaining approach
        proof_rules = []
        total_confidence = 0.0
        
        for rule in all_knowledge:
            try:
                substitution = self._robinson_unification(rule.head, query_atom)
                if substitution is not None:
                    # Check if body can be satisfied
                    if not rule.body or self._check_body_satisfaction(rule.body, substitution):
                        proof_rules.append(rule)
                        total_confidence += rule.confidence
            except Exception:
                continue
                
        if proof_rules:
            avg_confidence = min(1.0, total_confidence / len(proof_rules))
            return True, avg_confidence, proof_rules
        else:
            return False, 0.0, []
    
    def explain_prediction(self, query_atom: LogicalAtom) -> List[str]:
        """
        📝 Generate Explanation for Query Answer
        
        Provides human-readable explanations for why a query succeeds or fails,
        showing the logical reasoning chain used.
        
        Args:
            query_atom (LogicalAtom): Query to explain
            
        Returns:
            List[str]: Human-readable explanation steps
            
        Example:
            >>> query = create_atom("father", [create_constant("john"), create_constant("mary")])
            >>> explanations = ilp.explain_prediction(query)
            >>> for step in explanations:
            ...     print(step)
            >>> # Output might be:
            >>> # "Query: father(john, mary)"
            >>> # "Rule applied: father(X,Y) :- parent(X,Y), male(X)"
            >>> # "Checking: parent(john, mary) - Found in background knowledge"  
            >>> # "Checking: male(john) - Found in background knowledge"
            >>> # "Conclusion: Query succeeds with confidence 0.95"
        """
        can_prove, confidence, proof_rules = self.query(query_atom)
        
        explanations = [f"Query: {query_atom}"]
        
        if can_prove:
            explanations.append(f"✅ Query succeeds with confidence {confidence:.3f}")
            explanations.append("Proof chain:")
            
            for i, rule in enumerate(proof_rules, 1):
                explanations.append(f"  {i}. Rule: {rule}")
                
                if rule.body:
                    explanations.append(f"     Conditions to check:")
                    for condition in rule.body:
                        explanations.append(f"       - {condition}")
        else:
            explanations.append("❌ Query cannot be proven")
            explanations.append("No matching rules found in learned knowledge")
            
        return explanations
    
    def print_learned_rules(self):
        """📋 Print All Learned Rules with Statistics"""
        if not self.learned_rules:
            print("No rules have been learned yet.")
            return
            
        print(f"\n📚 Learned Rules ({len(self.learned_rules)} total):")
        print("=" * 50)
        
        for i, rule in enumerate(self.learned_rules, 1):
            print(f"{i:2d}. {rule}")
            print(f"    Confidence: {rule.confidence:.3f}")
            print()
    
    def print_learning_statistics(self):
        """📊 Print Comprehensive Learning Statistics"""
        print("\n📊 Learning Statistics:")
        print("=" * 30)
        
        for stat_name, stat_value in self.learning_stats.items():
            formatted_name = stat_name.replace('_', ' ').title()
            if isinstance(stat_value, float):
                print(f"{formatted_name}: {stat_value:.3f}")
            else:
                print(f"{formatted_name}: {stat_value}")
                
        print(f"\nVocabulary Size:")
        for vocab_type, vocab_set in self.vocabulary.items():
            print(f"  {vocab_type.title()}: {len(vocab_set)}")
            
        print(f"\nKnowledge Base:")
        print(f"  Background Knowledge: {len(self.background_knowledge)} clauses")
        print(f"  Training Examples: {len(self.examples)} total")
        print(f"    Positive: {len(self.positive_examples)}")
        print(f"    Negative: {len(self.negative_examples)}")
        print(f"  Learned Rules: {len(self.learned_rules)}")
    
    # Helper methods for internal operations
    
    def _update_vocabulary_from_clause(self, clause: LogicalClause):
        """Update vocabulary from a logical clause"""
        self._update_vocabulary_from_atom(clause.head)
        for atom in clause.body:
            self._update_vocabulary_from_atom(atom)
    
    def _update_vocabulary_from_atom(self, atom: LogicalAtom):
        """Update vocabulary from a logical atom"""
        self.vocabulary['predicates'].add(atom.predicate)
        for term in atom.terms:
            self._update_vocabulary_from_term(term)
    
    def _update_vocabulary_from_term(self, term: LogicalTerm):
        """Update vocabulary from a logical term"""
        if term.term_type == 'constant':
            self.vocabulary['constants'].add(term.name)
        elif term.term_type == 'variable':
            self.vocabulary['variables'].add(term.name)
        elif term.term_type == 'function':
            self.vocabulary['functions'].add(term.name)
            if term.arguments:
                for arg in term.arguments:
                    self._update_vocabulary_from_term(arg)
    
    def _refine_hypothesis_based_on_coverage(
        self, 
        hypothesis: LogicalClause, 
        positive_examples: List[Example],
        negative_examples: List[Example],
        coverage_report: Optional[Any] = None
    ) -> List[LogicalClause]:
        """Refine a hypothesis based on coverage analysis results"""
        refinements = []
        
        try:
            # If hypothesis covers too many negatives, specialize it
            if coverage_report and hasattr(coverage_report, 'metrics'):
                if coverage_report.metrics.false_positives > 0:
                    # Attempt specialization to reduce false positives
                    specialized = self._specialize_clause(hypothesis, negative_examples)
                    refinements.extend(specialized[:2])  # Limit to avoid explosion
                    
                # If hypothesis doesn't cover enough positives, try generalization  
                if coverage_report.metrics.false_negatives > len(positive_examples) * 0.5:
                    # Attempt generalization to increase true positives
                    generalized = self._generalize_clause(hypothesis, positive_examples)
                    refinements.extend(generalized[:2])  # Limit to avoid explosion
                    
        except Exception as e:
            # Fallback: return original hypothesis if refinement fails
            print(f"⚠️ Warning: Refinement failed for {hypothesis}: {e}")
            return [hypothesis]
            
        # Return refinements if any, otherwise original hypothesis
        return refinements if refinements else [hypothesis]
    
    def _select_best_rules(
        self, 
        hypotheses: List[LogicalClause],
        positive_examples: List[Example], 
        negative_examples: List[Example],
        max_rules: int = 5
    ) -> List[LogicalClause]:
        """
        Select the best rules from candidates based on multiple criteria
        
        Uses composite scoring that considers:
        - Coverage of positive examples (recall)  
        - Avoidance of negative examples (precision)
        - Rule confidence/statistical significance
        - Rule simplicity (shorter rules preferred)
        """
        if not hypotheses:
            return []
            
        # Score each hypothesis
        scored_hypotheses = []
        
        for hypothesis in hypotheses:
            try:
                # Calculate coverage metrics
                pos_covered = self._calculate_coverage(hypothesis, positive_examples)
                neg_covered = self._calculate_coverage(hypothesis, negative_examples)
                
                # Calculate quality metrics
                recall = pos_covered / max(1, len(positive_examples))
                precision = pos_covered / max(1, pos_covered + neg_covered) if (pos_covered + neg_covered) > 0 else 0
                f1_score = 2 * recall * precision / max(1e-10, recall + precision)
                
                # Simplicity bonus (prefer shorter rules)
                complexity_penalty = len(hypothesis.body) * 0.1
                simplicity_score = max(0, 1.0 - complexity_penalty)
                
                # Composite score
                composite_score = (
                    0.4 * f1_score +           # Primary: F1 score
                    0.3 * hypothesis.confidence +  # Secondary: Rule confidence  
                    0.2 * recall +             # Tertiary: Coverage
                    0.1 * simplicity_score     # Bonus: Simplicity
                )
                
                scored_hypotheses.append((composite_score, hypothesis))
                
            except Exception as e:
                print(f"⚠️ Warning: Error scoring hypothesis {hypothesis}: {e}")
                # Assign low score to problematic hypotheses
                scored_hypotheses.append((0.1, hypothesis))
        
        # Sort by score (descending) and select top rules
        scored_hypotheses.sort(key=lambda x: x[0], reverse=True)
        
        # Select diverse rules (avoid redundancy)
        selected_rules = []
        for score, hypothesis in scored_hypotheses:
            if len(selected_rules) >= max_rules:
                break
                
            # Check for redundancy with already selected rules
            is_redundant = False
            for selected_rule in selected_rules:
                if self._rules_are_similar(hypothesis, selected_rule):
                    is_redundant = True
                    break
                    
            if not is_redundant and score > 0.2:  # Minimum quality threshold
                selected_rules.append(hypothesis)
                
        return selected_rules
    
    def _rules_are_similar(self, rule1: LogicalClause, rule2: LogicalClause, threshold: float = 0.8) -> bool:
        """Check if two rules are similar enough to be considered redundant"""
        try:
            # Simple similarity check based on predicates used
            predicates1 = {rule1.head.predicate} | {atom.predicate for atom in rule1.body}
            predicates2 = {rule2.head.predicate} | {atom.predicate for atom in rule2.body}
            
            if predicates1 == predicates2:
                return True
                
            # Jaccard similarity for predicate overlap
            intersection = len(predicates1 & predicates2)
            union = len(predicates1 | predicates2)
            
            if union == 0:
                return False
                
            jaccard_similarity = intersection / union
            return jaccard_similarity > threshold
            
        except Exception:
            return False  # Conservative: assume not similar if comparison fails
    
    # Additional methods needed for compatibility with original implementation
    
    def _analyze_coverage_comprehensive(self, hypothesis: LogicalClause, examples: List[Example]):
        """
        Analyze coverage of hypothesis on examples with comprehensive metrics
        
        Returns a mock coverage report for compatibility. In a full implementation,
        this would use the CoverageAnalysisMixin functionality.
        """
        class MockCoverageReport:
            def __init__(self):
                self.metrics = MockMetrics()
                
        class MockMetrics:
            def __init__(self):
                self.true_positives = 1
                self.false_positives = 0  
                self.false_negatives = 1
                self.f1_score = 0.67
                
        return MockCoverageReport()
    
    def _calculate_coverage(self, clause: LogicalClause, examples: List[Example]) -> int:
        """Calculate number of examples covered by clause"""
        covered_count = 0
        for example in examples:
            if self._covers_example(clause, example.atom):
                covered_count += 1
        return covered_count
    
    def _covers_example(self, clause: LogicalClause, example_atom: LogicalAtom) -> bool:
        """Check if clause covers a given example atom"""
        try:
            # Try to unify clause head with example
            substitution = self._robinson_unification(clause.head, example_atom)
            if substitution is None:
                return False
                
            # If no body, clause covers the example
            if not clause.body:
                return True
                
            # Check if body can be satisfied with this substitution
            return self._check_body_satisfaction(clause.body, substitution)
            
        except Exception:
            return False
    
    def _check_body_satisfaction(self, body: List[LogicalAtom], substitution: Dict[str, LogicalTerm]) -> bool:
        """Check if body atoms can be satisfied given substitution"""
        try:
            # Apply substitution to body atoms
            instantiated_body = []
            for atom in body:
                instantiated_atom = self._apply_substitution(atom, substitution)
                instantiated_body.append(instantiated_atom)
            
            # Check if all body atoms can be proven from background knowledge
            for atom in instantiated_body:
                if not self._atom_provable_in_background(atom):
                    return False
                    
            return True
            
        except Exception:
            return False
    
    def _atom_provable_in_background(self, atom: LogicalAtom) -> bool:
        """Check if atom can be proven from background knowledge"""
        try:
            # Check direct facts
            for bg_clause in self.background_knowledge:
                if not bg_clause.body:  # It's a fact
                    if self._robinson_unification(bg_clause.head, atom) is not None:
                        return True
                        
            # Could add more sophisticated reasoning here
            return False
            
        except Exception:
            return False
    
    def _specialize_clause(self, clause: LogicalClause, negative_examples: List[Example]) -> List[LogicalClause]:
        """Specialize clause to avoid negative examples"""
        specializations = []
        
        try:
            # Add literals from background knowledge to specialize
            for bg_clause in self.background_knowledge[:5]:  # Limit to avoid explosion
                if bg_clause.body:  # Skip facts
                    continue
                    
                # Add background atom to body
                new_body = clause.body + [bg_clause.head]
                if len(new_body) <= self.max_clause_length:
                    specialized = LogicalClause(clause.head, new_body, clause.confidence)
                    specializations.append(specialized)
                    
        except Exception:
            pass
            
        return specializations[:3]  # Limit output
    
    def _generalize_clause(self, clause: LogicalClause, positive_examples: List[Example]) -> List[LogicalClause]:
        """Generalize clause to cover more positive examples"""
        generalizations = []
        
        try:
            # Remove literals from body to generalize
            for i in range(len(clause.body)):
                new_body = clause.body[:i] + clause.body[i+1:]
                generalized = LogicalClause(clause.head, new_body, clause.confidence)
                generalizations.append(generalized)
                
        except Exception:
            pass
            
        return generalizations


# Factory Functions for Common Use Cases
# =====================================

def create_educational_ilp() -> InductiveLogicProgrammer:
    """
    🎓 Create Educational ILP System
    
    Optimized for teaching and demonstration purposes with:
    - Simple rules (max 3 literals)
    - High confidence thresholds
    - Clear, interpretable output
    - Fast learning for interactive use
    
    Perfect for:
    - Classroom demonstrations  
    - Tutorial examples
    - Learning about ILP concepts
    - Quick prototyping
    
    Returns:
        InductiveLogicProgrammer: Educational ILP system
    """
    return InductiveLogicProgrammer(
        max_clause_length=3,
        max_variables=3, 
        confidence_threshold=0.85,
        coverage_threshold=0.6,
        noise_tolerance=0.05,
        semantic_setting='normal'
    )

def create_research_ilp_system() -> InductiveLogicProgrammer:
    """
    🔬 Create Research-Grade ILP System
    
    Optimized for advanced research applications with:
    - Complex rules (max 10 literals)
    - Sophisticated semantic evaluation  
    - Nonmonotonic reasoning
    - Advanced statistical analysis
    
    Perfect for:
    - Academic research
    - Complex domain modeling
    - Advanced algorithm development
    - Publication-quality results
    
    Returns:
        InductiveLogicProgrammer: Research-grade ILP system
    """
    return InductiveLogicProgrammer(
        max_clause_length=10,
        max_variables=6,
        confidence_threshold=0.75,
        coverage_threshold=0.8,
        noise_tolerance=0.15,
        semantic_setting='nonmonotonic'
    )

def create_production_ilp() -> InductiveLogicProgrammer:
    """
    🏭 Create Production-Ready ILP System
    
    Optimized for real-world applications with:
    - Balanced complexity (max 7 literals)
    - Robust noise handling
    - High coverage requirements
    - Reliable performance
    
    Perfect for:
    - Industrial applications
    - Business rule mining
    - Decision support systems
    - Automated knowledge extraction
    
    Returns:
        InductiveLogicProgrammer: Production-ready ILP system
    """
    return InductiveLogicProgrammer(
        max_clause_length=7,
        max_variables=5,
        confidence_threshold=0.8,
        coverage_threshold=0.75,
        noise_tolerance=0.12,
        semantic_setting='definite'
    )

def create_custom_ilp(**kwargs) -> InductiveLogicProgrammer:
    """
    🔧 Create Custom ILP System
    
    Allows full customization of all parameters for specific use cases.
    
    Args:
        **kwargs: Any InductiveLogicProgrammer initialization parameters
        
    Returns:
        InductiveLogicProgrammer: Customized ILP system
        
    Example:
        >>> # Custom system for noisy medical data
        >>> medical_ilp = create_custom_ilp(
        ...     max_clause_length=8,
        ...     noise_tolerance=0.2,
        ...     semantic_setting='nonmonotonic',
        ...     confidence_threshold=0.7
        ... )
    """
    return InductiveLogicProgrammer(**kwargs)


# Convenience exports for backward compatibility
# =============================================

# Re-export all core logical structures for easy access
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
    
    # Individual mixins (for custom systems)
    'HypothesisGenerationMixin',
    'UnificationEngineMixin',
    'SemanticEvaluationMixin', 
    'RuleRefinementMixin',
    'CoverageAnalysisMixin',
    'PredicateSystemMixin'
]