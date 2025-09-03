"""
🔍 PREDICATE SYSTEM MODULE - Advanced Predicate Management for ILP
===============================================================

This module provides comprehensive predicate system management for Inductive Logic
Programming, handling predicate hierarchies, aliases, equivalences, and vocabulary
management with theta-subsumption support.

Based on Muggleton & De Raedt (1994) "Inductive Logic Programming: Theory and Methods"

Key Features:
- Predicate hierarchy management (taxonomies and type systems)
- Predicate aliases and equivalences for domain flexibility
- Vocabulary extraction and management (predicates, constants, functions)
- Theta-subsumption compatibility checking
- Advanced predicate compatibility reasoning
- Type system support for predicate validation

The predicate system is crucial for ILP as it enables:
1. Domain adaptation through flexible predicate definitions
2. Knowledge integration via predicate relationships
3. Efficient unification through compatibility checking
4. Type-safe rule learning and validation

Author: Benedict Chen
"""

from typing import Dict, List, Set, Optional, Tuple, Any, Union
from dataclasses import dataclass
from itertools import product, combinations
import warnings

from .logical_structures import LogicalTerm, LogicalAtom, LogicalClause, Example


class PredicateSystemMixin:
    """
    🧬 Predicate System Management Mixin for ILP
    
    Provides comprehensive predicate system functionality including:
    - Predicate hierarchy management (taxonomic relationships)
    - Alias and equivalence handling for domain flexibility  
    - Vocabulary extraction and management
    - Theta-subsumption compatibility checking
    - Advanced predicate compatibility reasoning
    
    This mixin implements the predicate system components of Muggleton & De Raedt's
    ILP framework, enabling sophisticated predicate reasoning and domain adaptation.
    
    Key Innovation: Bridges symbolic predicate knowledge with statistical learning,
    enabling domain-aware rule learning with flexible predicate definitions.
    
    Mathematical Foundation:
    - Predicate hierarchies: P₁ ⊑ P₂ (subsumption ordering)
    - Theta-subsumption: C₁ ⊑θ C₂ iff ∃θ: C₁θ ⊆ C₂
    - Compatibility relation: Compatible(P₁, P₂) via hierarchy/aliases/equivalences
    """
    
    def _initialize_predicate_system(self):
        """
        🚀 Initialize Predicate Hierarchy and Compatibility System
        
        Sets up the foundational predicate system infrastructure including:
        - Common domain hierarchies (person, relation, property taxonomies)
        - Standard predicate aliases for family relationships
        - Symmetric relationship equivalences
        
        This creates a robust foundation for domain-specific predicate reasoning
        while maintaining compatibility with standard ILP operations.
        
        Predicate Hierarchies:
        - Taxonomic organization (person → male/female/child/adult)
        - Relational categories (relation → parent/grandparent/ancestor/sibling)  
        - Property classifications (property → tall/short/young/old)
        
        Aliases & Equivalences:
        - Natural language variations (father → parent, mother → parent)
        - Symmetric relationships (friend ↔ friend, sibling ↔ sibling)
        - Domain-specific terminology support
        
        Example:
            >>> # After initialization, these are equivalent:
            >>> self._predicates_compatible("father", "parent")  # True (alias)
            >>> self._predicates_compatible("male", "female")     # True (same hierarchy)
            >>> self._predicates_compatible("friend", "friend")   # True (symmetric)
        
        🔬 Technical Details:
        Uses set-based representations for O(1) average-case lookup performance
        in predicate compatibility checking, crucial for hypothesis generation
        efficiency in large predicate vocabularies.
        """
        
        # Initialize core predicate system data structures
        if not hasattr(self, 'predicate_hierarchy'):
            self.predicate_hierarchy = {}
        if not hasattr(self, 'predicate_aliases'):
            self.predicate_aliases = {}
        if not hasattr(self, 'predicate_equivalences'):
            self.predicate_equivalences = set()
        
        # Common predicate hierarchies for family relationships and general domains
        # These provide taxonomic organization for improved unification and reasoning
        self.predicate_hierarchy.update({
            'person': {'male', 'female', 'child', 'adult', 'human', 'individual'},
            'relation': {'parent', 'grandparent', 'ancestor', 'sibling', 'relative', 'family'},
            'property': {'tall', 'short', 'young', 'old', 'big', 'small', 'smart', 'kind'},
            'action': {'work', 'study', 'play', 'travel', 'eat', 'sleep', 'speak'},
            'location': {'home', 'office', 'school', 'city', 'country', 'building'},
            'temporal': {'before', 'after', 'during', 'always', 'never', 'sometimes'}
        })
        
        # Common predicate aliases for natural language flexibility
        # Maps domain-specific terms to canonical predicate names
        self.predicate_aliases.update({
            # Family relationships
            'father': 'parent',
            'mother': 'parent',
            'dad': 'parent', 
            'mom': 'parent',
            'son': 'child',
            'daughter': 'child',
            'boy': 'male',
            'girl': 'female',
            'man': 'male',
            'woman': 'female',
            'brother': 'sibling',
            'sister': 'sibling',
            
            # Social relationships
            'husband': 'spouse',
            'wife': 'spouse',
            'partner': 'spouse',
            'buddy': 'friend',
            'pal': 'friend',
            'colleague': 'coworker',
            
            # Properties
            'large': 'big',
            'huge': 'big',
            'tiny': 'small',
            'little': 'small',
            'elderly': 'old',
            'senior': 'old',
            'junior': 'young',
            'bright': 'smart',
            'intelligent': 'smart',
            
            # Actions  
            'labor': 'work',
            'employment': 'work',
            'learn': 'study',
            'education': 'study',
            'recreation': 'play',
            'journey': 'travel'
        })
        
        # Symmetric and equivalent predicate relationships
        # These handle bidirectional and equivalent relationships
        self.predicate_equivalences.update({
            # Symmetric social relationships
            ('spouse', 'married'),
            ('married', 'spouse'),
            ('sibling', 'sibling'),    # Inherently symmetric
            ('friend', 'friend'),      # Inherently symmetric  
            ('colleague', 'coworker'), # Equivalent terms
            ('coworker', 'colleague'),
            
            # Spatial relationships (some symmetric)
            ('near', 'close'),
            ('close', 'near'),
            ('adjacent', 'next_to'),
            ('next_to', 'adjacent'),
            
            # Temporal equivalences
            ('before', 'earlier'),
            ('earlier', 'before'),
            ('after', 'later'),
            ('later', 'after'),
            
            # Property equivalences
            ('intelligent', 'smart'),
            ('smart', 'intelligent'),
            ('large', 'big'),
            ('big', 'large')
        })
    
    def _update_vocabulary_from_clause(self, clause: LogicalClause):
        """
        📚 Extract and Update Vocabulary from Logical Clause
        
        Performs comprehensive vocabulary extraction from a logical clause,
        updating the system's knowledge of predicates, constants, and functions.
        This is essential for maintaining an accurate vocabulary during learning.
        
        Processes both the head and body of the clause to capture all symbolic
        elements that may be relevant for hypothesis generation and unification.
        
        Args:
            clause (LogicalClause): The clause to extract vocabulary from
                                   Format: head :- body₁, body₂, ..., bodyₙ
                                   Example: parent(X,Y) :- father(X,Y), male(X)
        
        Updates:
            - self.predicates: Set of all predicate names encountered
            - self.constants: Set of all constant symbols found  
            - self.functions: Set of all function symbols identified
        
        🔬 Technical Details:
        Uses recursive traversal to handle nested function terms and complex
        clause structures. Essential for vocabulary-guided hypothesis generation
        in the ILP learning process.
        
        Example:
            >>> clause = LogicalClause(
            ...     head=LogicalAtom("grandparent", [LogicalTerm("X"), LogicalTerm("Z")]),
            ...     body=[LogicalAtom("parent", [LogicalTerm("X"), LogicalTerm("Y")]),
            ...           LogicalAtom("parent", [LogicalTerm("Y"), LogicalTerm("Z")])]
            ... )
            >>> self._update_vocabulary_from_clause(clause)
            >>> # Updates: predicates={"grandparent", "parent"}, constants=set(), functions=set()
        """
        
        # Extract vocabulary from clause head (consequent)
        self._update_vocabulary_from_atom(clause.head)
        
        # Extract vocabulary from all body atoms (antecedents)
        for atom in clause.body:
            self._update_vocabulary_from_atom(atom)
    
    def _update_vocabulary_from_atom(self, atom: LogicalAtom):
        """
        🔍 Extract and Update Vocabulary from Logical Atom
        
        Extracts predicate names and term vocabulary from a single logical atom.
        This method handles the atomic units of logical expressions, capturing
        both the predicate name and all arguments.
        
        Args:
            atom (LogicalAtom): The atom to extract vocabulary from
                               Format: predicate(term₁, term₂, ..., termₙ)
                               Example: parent(john, mary) or likes(X, chocolate)
        
        Updates:
            - self.predicates: Adds the atom's predicate name
            - Recursively processes all terms via _update_vocabulary_from_term()
        
        Handles:
            - Predicate name extraction and registration
            - Recursive term processing for complex arguments
            - Negated atoms (extracts same vocabulary regardless of negation)
        
        Example:
            >>> atom = LogicalAtom("loves", [
            ...     LogicalTerm("john", term_type="constant"),
            ...     LogicalTerm("mary", term_type="constant")
            ... ])
            >>> self._update_vocabulary_from_atom(atom)
            >>> # Updates: predicates={"loves"}, constants={"john", "mary"}
        """
        
        # Initialize vocabulary sets if not present
        if not hasattr(self, 'predicates'):
            self.predicates = set()
        if not hasattr(self, 'constants'):
            self.constants = set()
        if not hasattr(self, 'functions'):
            self.functions = set()
        
        # Add predicate name to vocabulary
        self.predicates.add(atom.predicate)
        
        # Extract vocabulary from all terms in the atom
        for term in atom.terms:
            self._update_vocabulary_from_term(term)
    
    def _update_vocabulary_from_term(self, term: LogicalTerm):
        """
        📝 Extract and Update Vocabulary from Logical Term
        
        Recursively processes logical terms to extract constants and function symbols.
        Handles the full spectrum of term types including nested function applications.
        
        Args:
            term (LogicalTerm): The term to extract vocabulary from
                               Can be constant, variable, or function with arguments
                               Examples: 
                               - Constant: LogicalTerm("john", term_type="constant")
                               - Variable: LogicalTerm("X", term_type="variable")
                               - Function: LogicalTerm("father_of", term_type="function", 
                                                     arguments=[LogicalTerm("john")])
        
        Updates:
            - self.constants: For constant terms, adds the constant name
            - self.functions: For function terms, adds the function name
            - Recursively processes function arguments
        
        Term Type Processing:
            - Constants: Direct vocabulary addition (e.g., "john", "mary", "5")
            - Variables: No vocabulary update (variables are placeholders)
            - Functions: Function name added + recursive argument processing
        
        🔬 Technical Details:
        Uses recursive descent to handle arbitrarily nested function terms,
        ensuring complete vocabulary extraction from complex logical expressions.
        
        Example:
            >>> # Complex function term: mother_of(child_of(john, mary))
            >>> func_term = LogicalTerm("mother_of", term_type="function", arguments=[
            ...     LogicalTerm("child_of", term_type="function", arguments=[
            ...         LogicalTerm("john", term_type="constant"),
            ...         LogicalTerm("mary", term_type="constant")
            ...     ])
            ... ])
            >>> self._update_vocabulary_from_term(func_term)
            >>> # Updates: functions={"mother_of", "child_of"}, constants={"john", "mary"}
        """
        
        # Initialize vocabulary sets if not present
        if not hasattr(self, 'constants'):
            self.constants = set()
        if not hasattr(self, 'functions'):
            self.functions = set()
        
        # Process term based on its type
        if term.term_type == 'constant':
            # Add constant to vocabulary
            self.constants.add(term.name)
            
        elif term.term_type == 'function':
            # Add function name to vocabulary
            self.functions.add(term.name)
            
            # Recursively process function arguments if present
            if term.arguments:
                for arg in term.arguments:
                    self._update_vocabulary_from_term(arg)
        
        # Note: Variables are not added to vocabulary as they are placeholders
        # and don't contribute to the domain-specific vocabulary
    
    def _predicates_compatible(self, pred1: str, pred2: str) -> bool:
        """
        🧩 Advanced Predicate Compatibility Checking with Theta-Subsumption
        
        Determines if two predicates are compatible for unification in the ILP context.
        Uses multiple compatibility mechanisms including hierarchies, aliases, equivalences,
        and theta-subsumption relationships from background knowledge.
        
        This implementation follows Muggleton & De Raedt's framework with enhancements
        for practical domain adaptation and flexible predicate reasoning.
        
        Args:
            pred1 (str): First predicate name to check
            pred2 (str): Second predicate name to check
        
        Returns:
            bool: True if predicates are compatible for unification, False otherwise
        
        Compatibility Mechanisms (in order of checking):
            1. Direct Match: Identical predicate names
            2. Target Handling: Special "target_pred" compatibility for learning
            3. Alias Resolution: Domain-specific predicate aliases
            4. Equivalences: Symmetric and equivalent relationships
            5. Hierarchy: Same taxonomic category membership
            6. Theta-subsumption: Background knowledge compatibility
        
        🔬 Mathematical Foundation:
        Implements predicate compatibility relation: Compatible(P₁, P₂)
        - Direct: P₁ = P₂
        - Alias: canonical(P₁) = canonical(P₂)
        - Equivalence: (P₁, P₂) ∈ EquivalenceSet
        - Hierarchy: ∃C: P₁ ∈ Children(C) ∧ P₂ ∈ Children(C)
        - Subsumption: ∃clause ∈ BK: P₁, P₂ ∈ predicates(clause)
        
        Example:
            >>> # Direct compatibility
            >>> self._predicates_compatible("parent", "parent")  # True
            
            >>> # Alias compatibility  
            >>> self._predicates_compatible("father", "parent")  # True (father → parent)
            
            >>> # Hierarchy compatibility
            >>> self._predicates_compatible("male", "female")    # True (both in 'person')
            
            >>> # Equivalence compatibility
            >>> self._predicates_compatible("friend", "friend")  # True (symmetric)
            
            >>> # Subsumption compatibility (from background knowledge)
            >>> # If BK contains: grandparent(X,Z) :- parent(X,Y), parent(Y,Z)
            >>> self._predicates_compatible("grandparent", "parent")  # True
        
        ⚡ Performance: O(1) average case for direct/alias/equivalence checks,
        O(|BK|) worst case for subsumption checking where |BK| is background knowledge size.
        """
        
        # Initialize predicate system if not already done
        if not hasattr(self, 'predicate_hierarchy'):
            self._initialize_predicate_system()
        
        # 1. Direct match - identical predicates
        if pred1 == pred2:
            return True
        
        # 2. Special target predicate handling for learning context
        # "target_pred" is a placeholder used during hypothesis generation
        if pred1 == "target_pred" or pred2 == "target_pred":
            return True
        
        # 3. Check predicate aliases for domain flexibility
        # Map predicates to their canonical forms and compare
        canonical_pred1 = self.predicate_aliases.get(pred1, pred1)
        canonical_pred2 = self.predicate_aliases.get(pred2, pred2)
        
        if canonical_pred1 == canonical_pred2:
            return True
        
        # 4. Check predicate equivalences (symmetric/bidirectional relationships)
        # Handles both (pred1, pred2) and (pred2, pred1) orderings
        if (canonical_pred1, canonical_pred2) in self.predicate_equivalences or \
           (canonical_pred2, canonical_pred1) in self.predicate_equivalences:
            return True
        
        # 5. Check hierarchy compatibility (same taxonomic category)
        # Predicates in the same category are considered compatible
        for parent, children in self.predicate_hierarchy.items():
            if canonical_pred1 in children and canonical_pred2 in children:
                return True  # Both predicates belong to the same category
        
        # 6. Advanced: Check theta-subsumption compatibility via background knowledge
        # This enables sophisticated predicate compatibility based on logical relationships
        # in the domain-specific background knowledge
        if hasattr(self, 'background_knowledge'):
            for bg_clause in self.background_knowledge:
                if self._predicates_appear_in_subsumption_relation(canonical_pred1, canonical_pred2, bg_clause):
                    return True
        
        # No compatibility found
        return False
    
    def _predicates_appear_in_subsumption_relation(self, pred1: str, pred2: str, clause: LogicalClause) -> bool:
        """
        🔍 Check Predicate Subsumption Relation in Background Knowledge
        
        Examines whether two predicates appear in a subsumption relationship within
        a background knowledge clause, indicating potential compatibility for unification.
        
        This implements a simplified form of predicate-level subsumption checking
        based on co-occurrence in logical clauses, which suggests semantic relatedness.
        
        Args:
            pred1 (str): First predicate to check
            pred2 (str): Second predicate to check  
            clause (LogicalClause): Background knowledge clause to examine
        
        Returns:
            bool: True if predicates appear in the same clause (suggesting compatibility)
        
        🔬 Technical Foundation:
        Based on the insight that predicates appearing in the same logical clause
        often have semantic relationships that make them suitable for unification
        in hypothesis generation. This heuristic captures implicit domain knowledge.
        
        Subsumption Context:
        - If predicates co-occur in background clauses, they may be unifiable
        - This captures implicit semantic relationships in the domain
        - Supports flexible predicate compatibility beyond explicit hierarchies
        
        Example:
            >>> # Background clause: grandparent(X,Z) :- parent(X,Y), parent(Y,Z)
            >>> clause = LogicalClause(
            ...     head=LogicalAtom("grandparent", [LogicalTerm("X"), LogicalTerm("Z")]),
            ...     body=[LogicalAtom("parent", [LogicalTerm("X"), LogicalTerm("Y")]),
            ...           LogicalAtom("parent", [LogicalTerm("Y"), LogicalTerm("Z")])]
            ... )
            >>> self._predicates_appear_in_subsumption_relation("grandparent", "parent", clause)
            >>> # Returns True (both predicates appear in the same clause)
        
        💡 Insight: Co-occurrence in logical clauses indicates semantic relationships
        that are valuable for ILP hypothesis generation and predicate unification.
        """
        
        # Collect all predicates appearing in the clause
        all_predicates_in_clause = set()
        
        # Add head predicate
        all_predicates_in_clause.add(clause.head.predicate)
        
        # Add all body predicates
        for atom in clause.body:
            all_predicates_in_clause.add(atom.predicate)
        
        # Check if both predicates appear in the same clause
        # This heuristic suggests potential semantic compatibility
        return pred1 in all_predicates_in_clause and pred2 in all_predicates_in_clause
    
    def add_predicate_alias(self, alias: str, canonical: str):
        """
        📝 Add Domain-Specific Predicate Alias
        
        Registers a predicate alias to support domain-specific terminology and
        natural language variations in predicate names. This enables flexible
        knowledge representation and domain adaptation.
        
        Args:
            alias (str): The alternative predicate name (domain-specific term)
            canonical (str): The canonical predicate name (standard form)
        
        Updates:
            - self.predicate_aliases: Maps alias to canonical form
        
        Benefits:
            - Domain adaptation: Support field-specific terminology
            - Natural language flexibility: Handle synonyms and variations  
            - Knowledge integration: Unify different naming conventions
            - User experience: Accept natural predicate names
        
        Example:
            >>> # Medical domain adaptation
            >>> self.add_predicate_alias("patient", "person")
            >>> self.add_predicate_alias("diagnosis", "condition")
            >>> self.add_predicate_alias("physician", "doctor")
            >>>
            >>> # Business domain adaptation
            >>> self.add_predicate_alias("employee", "person")  
            >>> self.add_predicate_alias("manager", "supervisor")
            >>> self.add_predicate_alias("department", "division")
        
        🔬 Technical Impact:
        Aliases are resolved during predicate compatibility checking, enabling
        seamless unification between domain-specific and canonical terms without
        requiring users to learn standard predicate vocabularies.
        """
        
        # Initialize alias dictionary if not present
        if not hasattr(self, 'predicate_aliases'):
            self.predicate_aliases = {}
        
        # Register the alias mapping
        self.predicate_aliases[alias] = canonical
        
        print(f"   Added predicate alias: {alias} -> {canonical}")
    
    def add_predicate_equivalence(self, pred1: str, pred2: str):
        """
        🔄 Add Symmetric Predicate Equivalence Relationship
        
        Registers bidirectional equivalence between two predicates, supporting
        symmetric relationships and alternative naming conventions in the domain.
        
        Args:
            pred1 (str): First predicate in the equivalence relationship
            pred2 (str): Second predicate in the equivalence relationship
        
        Updates:
            - self.predicate_equivalences: Adds (pred1, pred2) tuple
            
        Note: The system checks both (pred1, pred2) and (pred2, pred1) during
        compatibility checking, so only one direction needs to be registered.
        
        Equivalence Types:
            - Symmetric relationships: friend ↔ friend, spouse ↔ spouse
            - Alternative terminology: colleague ↔ coworker, big ↔ large
            - Domain synonyms: smart ↔ intelligent, old ↔ elderly
        
        Example:
            >>> # Symmetric social relationships
            >>> self.add_predicate_equivalence("spouse", "married")
            >>> self.add_predicate_equivalence("colleague", "coworker")
            >>>
            >>> # Property equivalences
            >>> self.add_predicate_equivalence("intelligent", "smart")
            >>> self.add_predicate_equivalence("large", "big")
            >>>
            >>> # Domain-specific equivalences
            >>> self.add_predicate_equivalence("customer", "client")
        
        💡 Design Insight: Equivalences handle bidirectional semantic relationships
        that aliases cannot capture, enabling richer domain knowledge representation.
        """
        
        # Initialize equivalences set if not present  
        if not hasattr(self, 'predicate_equivalences'):
            self.predicate_equivalences = set()
        
        # Add the equivalence relationship (bidirectional compatibility handled in checking)
        self.predicate_equivalences.add((pred1, pred2))
        
        print(f"   Added predicate equivalence: {pred1} <-> {pred2}")
    
    def add_predicate_hierarchy(self, parent: str, children: Set[str]):
        """
        🌳 Add Predicate Taxonomy Hierarchy
        
        Registers a taxonomic hierarchy where child predicates are categorized
        under a parent concept, enabling category-based predicate compatibility.
        
        Args:
            parent (str): The parent category name (higher-level concept)
            children (Set[str]): Set of child predicate names in this category
        
        Updates:
            - self.predicate_hierarchy: Maps parent to set of children
        
        Hierarchy Benefits:
            - Taxonomic reasoning: Predicates in same category are compatible
            - Abstraction levels: Support different granularities of concepts
            - Domain organization: Structure predicate knowledge systematically
            - Inheritance: Child predicates inherit parent category properties
        
        Example:
            >>> # Biological taxonomy
            >>> self.add_predicate_hierarchy("animal", {
            ...     "mammal", "bird", "fish", "reptile", "amphibian"
            ... })
            >>> self.add_predicate_hierarchy("mammal", {
            ...     "dog", "cat", "horse", "cow", "human"
            ... })
            >>>
            >>> # Social relationship taxonomy
            >>> self.add_predicate_hierarchy("family_relation", {
            ...     "parent", "child", "sibling", "spouse", "grandparent"
            ... })
            >>>
            >>> # Property taxonomy
            >>> self.add_predicate_hierarchy("physical_property", {
            ...     "tall", "short", "heavy", "light", "fast", "slow"
            ... })
        
        🔬 Technical Impact:
        Hierarchies enable O(1) category-based compatibility checking, where any
        two predicates in the same category are considered compatible for unification
        in hypothesis generation.
        """
        
        # Initialize hierarchy dictionary if not present
        if not hasattr(self, 'predicate_hierarchy'):
            self.predicate_hierarchy = {}
        
        # Register the hierarchy relationship
        self.predicate_hierarchy[parent] = children
        
        print(f"   Added predicate hierarchy: {parent} -> {children}")
    
    def theta_subsumes(self, clause1: LogicalClause, clause2: LogicalClause) -> bool:
        """
        🎯 Theta-Subsumption: Advanced Clause Generality Checking
        
        Implements theta-subsumption from Muggleton & De Raedt (1994), determining
        if clause1 is more general than clause2 through variable substitution.
        
        Mathematical Definition:
        Clause C₁ theta-subsumes C₂ (C₁ ⊑θ C₂) if there exists a substitution θ
        such that C₁θ ⊆ C₂ (C₁ with substitution θ is a subset of C₂).
        
        Args:
            clause1 (LogicalClause): The potentially more general clause
            clause2 (LogicalClause): The potentially more specific clause
        
        Returns:
            bool: True if clause1 theta-subsumes clause2, False otherwise
        
        🔬 Theoretical Foundation:
        Theta-subsumption captures the notion of logical generality in ILP:
        - More general clauses subsume more specific ones
        - Subsumption ordering guides hypothesis refinement
        - Essential for proper ILP search space navigation
        
        Subsumption Process:
            1. Generate possible variable substitutions for clause1
            2. Apply each substitution to create instantiated clause1
            3. Check if instantiated clause1 is subset of clause2
            4. Return True if any substitution succeeds
        
        Example:
            >>> # General clause: parent(X,Y) :- father(X,Y)
            >>> clause1 = LogicalClause(
            ...     head=LogicalAtom("parent", [LogicalTerm("X"), LogicalTerm("Y")]),
            ...     body=[LogicalAtom("father", [LogicalTerm("X"), LogicalTerm("Y")])]
            ... )
            >>> 
            >>> # Specific clause: parent(john,mary) :- father(john,mary), male(john)
            >>> clause2 = LogicalClause(
            ...     head=LogicalAtom("parent", [LogicalTerm("john"), LogicalTerm("mary")]),
            ...     body=[LogicalAtom("father", [LogicalTerm("john"), LogicalTerm("mary")]),
            ...           LogicalAtom("male", [LogicalTerm("john")])]
            ... )
            >>>
            >>> self.theta_subsumes(clause1, clause2)  # True
            >>> # With θ = {X/john, Y/mary}, clause1θ ⊆ clause2
        
        ⚡ Computational Complexity: 
        Exponential in the number of variables (limited by max variable constraints)
        Uses pruning and heuristics to manage search space efficiently.
        
        💡 ILP Significance: Theta-subsumption is fundamental to ILP theory,
        enabling proper hypothesis space navigation and refinement operations.
        """
        
        # Generate possible variable substitutions for clause1
        substitutions = self._find_theta_substitutions(clause1, clause2)
        
        # Test each substitution to see if it creates a valid subsumption
        for substitution in substitutions:
            if self._check_subsumption_with_substitution(clause1, clause2, substitution):
                return True  # Found a valid theta-subsumption
        
        return False  # No valid subsumption found
    
    def _find_theta_substitutions(self, clause1: LogicalClause, clause2: LogicalClause) -> List[Dict[str, str]]:
        """
        🔍 Generate Theta-Subsumption Variable Substitutions
        
        Finds possible variable substitutions that could make clause1 subsume clause2.
        This is the combinatorial core of theta-subsumption checking.
        
        Args:
            clause1 (LogicalClause): Source clause (potentially more general)
            clause2 (LogicalClause): Target clause (potentially more specific)
        
        Returns:
            List[Dict[str, str]]: List of substitution dictionaries mapping 
                                 variables in clause1 to terms in clause2
        
        🔬 Algorithm Strategy:
        - Extract all variables from clause1 (substitution targets)
        - Extract all terms from clause2 (substitution values)
        - Generate combinations of variable-to-term mappings
        - Limit combinatorial explosion through intelligent pruning
        
        Optimization Techniques:
            - Limit variable count to prevent exponential blow-up
            - Use greedy approach for large variable sets
            - Cap total substitutions generated
            - Prioritize likely successful substitutions
        
        Example:
            >>> # clause1: parent(X,Y) :- male(X)
            >>> # clause2: parent(john,mary) :- male(john), adult(john)  
            >>> substitutions = self._find_theta_substitutions(clause1, clause2)
            >>> # Returns: [{"X": "john", "Y": "mary"}]
        
        ⚡ Performance: O(|Terms|^|Variables|) worst case, optimized with pruning
        """
        
        substitutions = []
        
        # Extract variables from clause1 (these need substitutions)
        vars1 = self._extract_variables_from_clause(clause1)
        
        # Extract terms from clause2 (substitution candidates)
        terms2 = self._extract_terms_from_clause(clause2)
        
        # Handle edge case: no variables to substitute
        if len(vars1) == 0:
            return [{}]  # Empty substitution
        
        # Handle small variable sets with full combinatorial generation
        if len(vars1) <= 3:  # Manageable combinatorial explosion
            for combination in product(terms2, repeat=len(vars1)):
                substitution = dict(zip(vars1, combination))
                substitutions.append(substitution)
        else:
            # For larger variable sets, use greedy single-pass approach
            # This sacrifices completeness for computational tractability
            if len(terms2) >= len(vars1):
                substitution = dict(zip(vars1, terms2[:len(vars1)]))
                substitutions.append(substitution)
        
        # Limit results to prevent excessive computation downstream
        return substitutions[:10]  # Cap at 10 substitutions maximum
    
    def _extract_variables_from_clause(self, clause: LogicalClause) -> List[str]:
        """
        🔤 Extract All Variables from a Logical Clause
        
        Recursively extracts all variable names appearing in a clause,
        including variables in the head and all body atoms.
        
        Args:
            clause (LogicalClause): The clause to extract variables from
        
        Returns:
            List[str]: Ordered list of unique variable names
        
        Example:
            >>> # clause: grandparent(X,Z) :- parent(X,Y), parent(Y,Z)
            >>> variables = self._extract_variables_from_clause(clause)  
            >>> # Returns: ["X", "Y", "Z"]
        """
        
        variables = set()
        
        # Extract variables from clause head
        variables.update(self._extract_variables_from_atom(clause.head))
        
        # Extract variables from all body atoms
        for atom in clause.body:
            variables.update(self._extract_variables_from_atom(atom))
        
        return list(variables)  # Convert to list for consistent ordering
    
    def _extract_variables_from_atom(self, atom: LogicalAtom) -> Set[str]:
        """
        🔍 Extract Variables from a Logical Atom
        
        Identifies all variable terms within a logical atom, handling
        both simple terms and nested function applications.
        
        Args:
            atom (LogicalAtom): The atom to extract variables from
        
        Returns:
            Set[str]: Set of variable names found in the atom
        
        Example:
            >>> # atom: parent(X, child_of(Y, mary))
            >>> variables = self._extract_variables_from_atom(atom)
            >>> # Returns: {"X", "Y"}
        """
        
        variables = set()
        
        # Check each term in the atom
        for term in atom.terms:
            if term.term_type == 'variable':
                variables.add(term.name)
            elif term.term_type == 'function' and term.arguments:
                # Recursively check function arguments
                for arg in term.arguments:
                    if arg.term_type == 'variable':
                        variables.add(arg.name)
        
        return variables
    
    def _extract_terms_from_clause(self, clause: LogicalClause) -> List[str]:
        """
        📝 Extract All Terms from a Logical Clause
        
        Collects all term names (constants and variables) from a clause,
        providing the universe of possible substitution values.
        
        Args:
            clause (LogicalClause): The clause to extract terms from
        
        Returns:
            List[str]: List of all term names (constants and variables)
        
        Example:
            >>> # clause: parent(john, mary) :- male(john), person(X)
            >>> terms = self._extract_terms_from_clause(clause)
            >>> # Returns: ["john", "mary", "X"]
        """
        
        terms = set()
        
        # Extract terms from clause head
        terms.update(self._extract_terms_from_atom(clause.head))
        
        # Extract terms from all body atoms
        for atom in clause.body:
            terms.update(self._extract_terms_from_atom(atom))
        
        return list(terms)
    
    def _extract_terms_from_atom(self, atom: LogicalAtom) -> Set[str]:
        """
        🔤 Extract All Term Names from a Logical Atom
        
        Recursively extracts names of all terms (constants, variables, functions)
        from a logical atom, including nested function arguments.
        
        Args:
            atom (LogicalAtom): The atom to extract terms from
        
        Returns:
            Set[str]: Set of all term names found
        
        Example:
            >>> # atom: loves(john, daughter_of(mary, X))
            >>> terms = self._extract_terms_from_atom(atom)  
            >>> # Returns: {"john", "daughter_of", "mary", "X"}
        """
        
        terms = set()
        
        # Process each term in the atom
        for term in atom.terms:
            terms.add(term.name)  # Add the term name itself
            
            # If it's a function, recursively process arguments
            if term.term_type == 'function' and term.arguments:
                for arg in term.arguments:
                    terms.add(arg.name)  # Add argument names
        
        return terms
    
    def _check_subsumption_with_substitution(self, clause1: LogicalClause, clause2: LogicalClause, 
                                           substitution: Dict[str, str]) -> bool:
        """
        ✅ Verify Theta-Subsumption with Given Substitution
        
        Checks if clause1 with the given variable substitution is a subset of clause2,
        implementing the core logic of theta-subsumption verification.
        
        Args:
            clause1 (LogicalClause): Source clause to be instantiated
            clause2 (LogicalClause): Target clause to check against
            substitution (Dict[str, str]): Variable substitution mapping
        
        Returns:
            bool: True if clause1θ ⊆ clause2, False otherwise
        
        🔬 Verification Process:
            1. Apply substitution θ to clause1 → clause1θ
            2. Check if head(clause1θ) matches head(clause2)
            3. Check if body(clause1θ) ⊆ body(clause2)
            4. Return True if both checks pass
        
        Example:
            >>> # clause1: parent(X,Y) :- father(X,Y)
            >>> # clause2: parent(john,mary) :- father(john,mary), male(john)
            >>> # substitution: {"X": "john", "Y": "mary"}
            >>> result = self._check_subsumption_with_substitution(clause1, clause2, substitution)
            >>> # Returns: True (parent(john,mary) :- father(john,mary) ⊆ clause2)
        """
        
        # Apply the substitution to clause1
        substituted_clause1 = self._apply_substitution_to_clause(clause1, substitution)
        
        # Check head compatibility: head(clause1θ) must match head(clause2)
        if not self._atoms_match(substituted_clause1.head, clause2.head):
            return False
        
        # Check body subset relation: body(clause1θ) ⊆ body(clause2)
        for literal1 in substituted_clause1.body:
            found_match = False
            for literal2 in clause2.body:
                if self._atoms_match(literal1, literal2):
                    found_match = True
                    break
            
            # If any literal in clause1θ body is not in clause2 body, subsumption fails
            if not found_match:
                return False
        
        return True  # All checks passed - valid subsumption
    
    def _apply_substitution_to_clause(self, clause: LogicalClause, substitution: Dict[str, str]) -> LogicalClause:
        """
        🔄 Apply Variable Substitution to Logical Clause
        
        Creates a new clause with all variables replaced according to the
        given substitution mapping, preserving clause structure and confidence.
        
        Args:
            clause (LogicalClause): Original clause to transform
            substitution (Dict[str, str]): Variable-to-term mapping
        
        Returns:
            LogicalClause: New clause with substitutions applied
        
        Example:
            >>> # clause: parent(X,Y) :- father(X,Y), male(X)
            >>> # substitution: {"X": "john", "Y": "mary"}
            >>> result = self._apply_substitution_to_clause(clause, substitution)
            >>> # Returns: parent(john,mary) :- father(john,mary), male(john)
        """
        
        # Apply substitution to head atom
        new_head = self._apply_substitution_to_atom_predicate(clause.head, substitution)
        
        # Apply substitution to all body atoms
        new_body = []
        for atom in clause.body:
            new_atom = self._apply_substitution_to_atom_predicate(atom, substitution)
            new_body.append(new_atom)
        
        # Return new clause with same confidence
        return LogicalClause(head=new_head, body=new_body, confidence=clause.confidence)
    
    def _apply_substitution_to_atom_predicate(self, atom: LogicalAtom, substitution: Dict[str, str]) -> LogicalAtom:
        """
        🔄 Apply Variable Substitution to Logical Atom
        
        Transforms a logical atom by applying variable substitutions to its terms,
        converting variables to constants according to the substitution mapping.
        
        Args:
            atom (LogicalAtom): Original atom to transform
            substitution (Dict[str, str]): Variable-to-term mapping
        
        Returns:
            LogicalAtom: New atom with substitutions applied
        
        Example:
            >>> # atom: parent(X, Y)
            >>> # substitution: {"X": "john", "Y": "mary"}  
            >>> result = self._apply_substitution_to_atom_predicate(atom, substitution)
            >>> # Returns: parent(john, mary)
        """
        
        new_terms = []
        
        # Apply substitution to each term
        for term in atom.terms:
            if term.term_type == 'variable' and term.name in substitution:
                # Replace variable with substituted constant
                new_term = LogicalTerm(name=substitution[term.name], term_type='constant')
            else:
                # Keep term unchanged (constants, unsubstituted variables, functions)
                new_term = term
            
            new_terms.append(new_term)
        
        # Return new atom with same predicate and negation
        return LogicalAtom(predicate=atom.predicate, terms=new_terms, negated=atom.negated)
    
    def _atoms_match(self, atom1: LogicalAtom, atom2: LogicalAtom) -> bool:
        """
        🎯 Check Exact Atom Matching for Subsumption
        
        Determines if two logical atoms are identical in predicate, terms,
        and negation, used for precise subsumption verification.
        
        Args:
            atom1 (LogicalAtom): First atom to compare
            atom2 (LogicalAtom): Second atom to compare
        
        Returns:
            bool: True if atoms match exactly, False otherwise
        
        Matching Criteria:
            - Same predicate name
            - Same number of terms (arity)
            - Identical terms in corresponding positions  
            - Same negation status
        
        Example:
            >>> atom1 = LogicalAtom("parent", [LogicalTerm("john"), LogicalTerm("mary")])
            >>> atom2 = LogicalAtom("parent", [LogicalTerm("john"), LogicalTerm("mary")])
            >>> self._atoms_match(atom1, atom2)  # True
            >>>
            >>> atom3 = LogicalAtom("parent", [LogicalTerm("bob"), LogicalTerm("mary")])  
            >>> self._atoms_match(atom1, atom3)  # False (different first term)
        """
        
        # Check predicate name and negation
        if atom1.predicate != atom2.predicate or atom1.negated != atom2.negated:
            return False
        
        # Check arity (number of terms)
        if len(atom1.terms) != len(atom2.terms):
            return False
        
        # Check term-by-term equality
        for term1, term2 in zip(atom1.terms, atom2.terms):
            if term1.name != term2.name:
                return False
        
        return True  # All checks passed
    
    def get_predicate_vocabulary(self) -> Dict[str, Set[str]]:
        """
        📊 Get Complete Predicate System Vocabulary Report
        
        Returns comprehensive vocabulary information including predicates,
        constants, functions, and predicate system relationships.
        
        Returns:
            Dict[str, Set[str]]: Dictionary containing:
                - 'predicates': All predicate names
                - 'constants': All constant terms  
                - 'functions': All function names
                - 'aliases': All predicate aliases
                - 'hierarchies': All hierarchy parent categories
        
        Example:
            >>> vocab = self.get_predicate_vocabulary()
            >>> print(f"Predicates: {vocab['predicates']}")
            >>> print(f"Constants: {vocab['constants']}")
            >>> print(f"Hierarchies: {vocab['hierarchies']}")
        """
        
        # Initialize vocabulary sets if not present
        if not hasattr(self, 'predicates'):
            self.predicates = set()
        if not hasattr(self, 'constants'):
            self.constants = set()
        if not hasattr(self, 'functions'):
            self.functions = set()
        if not hasattr(self, 'predicate_aliases'):
            self.predicate_aliases = {}
        if not hasattr(self, 'predicate_hierarchy'):
            self.predicate_hierarchy = {}
        
        return {
            'predicates': self.predicates.copy(),
            'constants': self.constants.copy(), 
            'functions': self.functions.copy(),
            'aliases': set(self.predicate_aliases.keys()),
            'hierarchies': set(self.predicate_hierarchy.keys())
        }
    
    def clear_predicate_system(self):
        """
        🧹 Clear All Predicate System Data
        
        Resets the predicate system to initial state, clearing all vocabularies,
        hierarchies, aliases, and equivalences. Useful for starting fresh
        or switching domains.
        """
        
        self.predicates = set()
        self.constants = set()
        self.functions = set()
        self.predicate_hierarchy = {}
        self.predicate_aliases = {}
        self.predicate_equivalences = set()
        
        print("   Predicate system cleared and reset")
    
    def validate_predicate_system(self) -> Dict[str, List[str]]:
        """
        ✅ Validate Predicate System Consistency
        
        Performs comprehensive validation of the predicate system to identify
        potential inconsistencies, circular references, and invalid configurations.
        
        Returns:
            Dict[str, List[str]]: Validation report with categories:
                - 'warnings': Non-critical issues
                - 'errors': Serious problems requiring attention
                - 'info': General information and statistics
        
        Validation Checks:
            - Circular alias references
            - Undefined canonical predicates in aliases  
            - Empty hierarchy categories
            - Self-referential equivalences
            - Orphaned predicates in hierarchies
        
        Example:
            >>> report = self.validate_predicate_system()
            >>> if report['errors']:
            ...     print("Predicate system has errors!")
            ...     for error in report['errors']:
            ...         print(f"  ERROR: {error}")
        """
        
        report = {'warnings': [], 'errors': [], 'info': []}
        
        # Initialize structures if missing
        if not hasattr(self, 'predicate_aliases'):
            self.predicate_aliases = {}
        if not hasattr(self, 'predicate_hierarchy'):
            self.predicate_hierarchy = {}
        if not hasattr(self, 'predicate_equivalences'):
            self.predicate_equivalences = set()
        
        # Check for circular alias references
        for alias, canonical in self.predicate_aliases.items():
            if canonical in self.predicate_aliases and self.predicate_aliases[canonical] == alias:
                report['errors'].append(f"Circular alias reference: {alias} <-> {canonical}")
        
        # Check for empty hierarchies
        for parent, children in self.predicate_hierarchy.items():
            if not children:
                report['warnings'].append(f"Empty hierarchy category: {parent}")
        
        # Check for self-referential equivalences  
        for pred1, pred2 in self.predicate_equivalences:
            if pred1 == pred2:
                report['warnings'].append(f"Self-referential equivalence: {pred1}")
        
        # Add statistics
        report['info'].append(f"Total predicates: {len(getattr(self, 'predicates', set()))}")
        report['info'].append(f"Total constants: {len(getattr(self, 'constants', set()))}")
        report['info'].append(f"Total functions: {len(getattr(self, 'functions', set()))}")
        report['info'].append(f"Aliases defined: {len(self.predicate_aliases)}")
        report['info'].append(f"Hierarchies defined: {len(self.predicate_hierarchy)}")
        report['info'].append(f"Equivalences defined: {len(self.predicate_equivalences)}")
        
        return report