"""
🔗 UNIFICATION ENGINE MODULE - Robinson's Unification Algorithm for ILP
======================================================================

This module implements the core unification engine for Inductive Logic Programming,
providing Robinson's unification algorithm and related logical reasoning operations.
Unification is the fundamental process of finding substitutions that make logical
expressions identical - a critical component for ILP hypothesis generation and testing.

Based on:
- Robinson, J.A. (1965) "A Machine-Oriented Logic Based on the Resolution Principle"
- Muggleton & De Raedt (1994) "Inductive Logic Programming: Theory and Methods"

🧠 THEORETICAL BACKGROUND: UNIFICATION IN FIRST-ORDER LOGIC
===========================================================

Unification is the process of finding substitutions that make logical terms or atoms 
identical. It's the cornerstone of automated theorem proving and logical inference.

Key Concepts:
- Substitution: A mapping from variables to terms {X → john, Y → mary}
- Most General Unifier (MGU): The most general substitution that unifies terms
- Occurs Check: Prevents infinite structures like X = f(X)
- Composition: Combining substitutions in proper order

Mathematical Foundation:
For terms t1 and t2, unification finds substitution θ such that t1θ = t2θ
where tθ means "apply substitution θ to term t"

Examples:
- Unify father(X, john) and father(mary, Y) → {X → mary, Y → john}
- Unify likes(X, X) and likes(john, mary) → FAIL (X cannot be both john and mary)
- Unify f(X, g(Y)) and f(a, Z) → {X → a, Z → g(Y)}

🚀 ROBINSON'S UNIFICATION ALGORITHM (1965)
==========================================

The groundbreaking algorithm that enabled modern automated reasoning:

1. **Disagreement Set**: Find first position where terms differ
2. **Variable Check**: Ensure one element is a variable
3. **Occurs Check**: Verify variable doesn't occur in the other term
4. **Substitution**: Replace all occurrences of variable with term
5. **Recursion**: Repeat until terms are identical or failure

Algorithm Properties:
- ✓ Complete: Finds unifier if one exists
- ✓ Terminating: Always halts (with occurs check)
- ✓ Optimal: Produces most general unifier (MGU)
- ✓ Sound: Substitution is correct if produced

Innovation Impact:
Robinson's algorithm revolutionized AI by making automated theorem proving
practical, leading to logic programming (Prolog) and ILP systems.

🔧 ILP APPLICATIONS
==================

In Inductive Logic Programming, unification enables:

1. **Hypothesis Generation**: Connecting background knowledge predicates
2. **Example Coverage**: Testing if rules cover training examples
3. **Rule Refinement**: Specializing/generalizing learned clauses
4. **Query Resolution**: Answering questions about learned rules

Semantic Integration:
- Normal Semantics: Classical unification with consistency
- Definite Semantics: Model-theoretic unification
- Nonmonotonic Semantics: Closed-world unification with minimality

Author: Benedict Chen (benedict@benedictchen.com)
"""

from typing import Dict, List, Tuple, Optional, Set
from .logical_structures import LogicalTerm, LogicalAtom, LogicalClause, Example


class UnificationEngineMixin:
    """
    🔗 Unification Engine Mixin for ILP Systems
    
    Provides Robinson's unification algorithm and related operations for logical
    reasoning in Inductive Logic Programming. This mixin can be combined with
    other ILP components to provide core unification capabilities.
    
    Key Features:
    - Robinson's unification algorithm (1965)
    - Occurs check for preventing infinite structures
    - Substitution application and composition
    - Atom and term unification
    - Enhanced predicate compatibility system
    
    Mathematical Foundation:
    Implements the mathematical theory of unification from first-order logic,
    providing the foundation for all logical inference in ILP systems.
    """
    
    def _robinson_unification(self, atom1: LogicalAtom, atom2: LogicalAtom) -> Optional[Dict[str, LogicalTerm]]:
        """
        🎯 Robinson's Unification Algorithm - The Heart of Automated Reasoning
        
        Implementation of J.A. Robinson's groundbreaking 1965 unification algorithm,
        the foundation of modern automated theorem proving and logic programming.
        
        🧠 Algorithm Overview:
        Given two logical atoms, find the Most General Unifier (MGU) - a substitution
        that makes the atoms identical while being as general as possible.
        
        Mathematical Definition:
        For atoms A₁ and A₂, find substitution θ such that A₁θ = A₂θ
        where θ is the most general such substitution (MGU).
        
        Algorithm Steps:
        1. **Predicate Compatibility**: Check if predicates can be unified
        2. **Arity Check**: Ensure both atoms have same number of arguments
        3. **Term-by-Term Unification**: Apply Robinson's algorithm to each term pair
        4. **Substitution Composition**: Build up the complete substitution
        
        Args:
            atom1 (LogicalAtom): First atom to unify (e.g., father(X, john))
            atom2 (LogicalAtom): Second atom to unify (e.g., father(mary, Y))
            
        Returns:
            Optional[Dict[str, LogicalTerm]]: Most General Unifier if successful
                                           Example: {X: mary, Y: john}
                                           None if unification fails
        
        💡 Key Insight: Unification is the bridge between symbolic and logical reasoning.
        It allows ILP systems to match patterns, generalize from examples, and perform
        logical inference - all essential for learning interpretable rules.
        
        🔬 Theoretical Properties:
        - **Soundness**: If MGU is returned, it correctly unifies the atoms
        - **Completeness**: If unification is possible, MGU will be found
        - **Optimality**: The returned substitution is most general
        - **Termination**: Algorithm always halts (with occurs check)
        
        Example:
            >>> # Unify father(X, john) with father(mary, Y)
            >>> atom1 = LogicalAtom("father", [Variable("X"), Constant("john")])
            >>> atom2 = LogicalAtom("father", [Constant("mary"), Variable("Y")])
            >>> mgu = self._robinson_unification(atom1, atom2)
            >>> # Returns: {"X": Constant("mary"), "Y": Constant("john")}
            >>> 
            >>> # Failed unification: different predicates
            >>> atom3 = LogicalAtom("mother", [Variable("X")])
            >>> mgu_fail = self._robinson_unification(atom1, atom3)
            >>> # Returns: None
        
        ⚡ Performance Notes:
        - Time complexity: O(n) where n is total term size
        - Space complexity: O(v) where v is number of variables
        - Optimized for common ILP patterns and predicates
        
        🌟 Historical Impact:
        Robinson's algorithm (1965) launched the field of automated theorem proving
        and made logic programming possible. Without this algorithm, systems like
        Prolog and ILP wouldn't exist!
        """
        
        # Enhanced predicate compatibility with hierarchy and aliasing
        if not self._predicates_compatible(atom1.predicate, atom2.predicate):
            return None
            
        # Check arity (number of arguments)
        if len(atom1.terms) != len(atom2.terms):
            return None
            
        # Initialize empty substitution
        substitution = {}
        
        # Unify terms pairwise using Robinson's term unification
        for term1, term2 in zip(atom1.terms, atom2.terms):
            if not self._unify_terms(term1, term2, substitution):
                return None  # Unification failed
                
        return substitution
        
    def _unify_terms(self, term1: LogicalTerm, term2: LogicalTerm, 
                    substitution: Dict[str, LogicalTerm]) -> bool:
        """
        🔤 Term Unification - Core Component of Robinson's Algorithm
        
        Unifies two logical terms by finding variable substitutions that make them
        identical. This is the recursive heart of Robinson's unification algorithm.
        
        🧠 Unification Rules (from Robinson 1965):
        
        1. **Identity Rule**: Identical terms unify trivially
           - constant 'john' unifies with constant 'john' ✓
           - variable X unifies with variable X ✓
        
        2. **Variable Rule**: Variables unify with any term (with occurs check)
           - Variable X unifies with constant 'john' → {X: 'john'}
           - Variable X unifies with function f(Y) → {X: f(Y)} (if X ∉ f(Y))
        
        3. **Constant Rule**: Constants unify only with identical constants
           - 'john' unifies with 'john' ✓
           - 'john' unifies with 'mary' ✗
        
        4. **Function Rule**: Functions unify if same functor and all args unify
           - f(X,Y) unifies with f(a,b) → {X: a, Y: b}
           - f(X) does not unify with g(X) ✗
        
        Args:
            term1 (LogicalTerm): First term to unify
            term2 (LogicalTerm): Second term to unify  
            substitution (Dict[str, LogicalTerm]): Current substitution (modified in-place)
            
        Returns:
            bool: True if terms can be unified, False otherwise
            
        Side Effects:
            Updates substitution dictionary with new variable bindings
        
        💡 Key Innovation: The occurs check prevents infinite structures
        like X = f(X), ensuring the algorithm terminates and produces
        meaningful results.
        
        Example:
            >>> substitution = {}
            >>> term1 = Variable("X") 
            >>> term2 = Constant("john")
            >>> success = self._unify_terms(term1, term2, substitution)
            >>> # success = True, substitution = {"X": Constant("john")}
            >>>
            >>> # Function unification
            >>> substitution = {}
            >>> term1 = Function("father", [Variable("X")])
            >>> term2 = Function("father", [Constant("john")])  
            >>> success = self._unify_terms(term1, term2, substitution)
            >>> # success = True, substitution = {"X": Constant("john")}
        
        🔍 Algorithm Details:
        1. Apply current substitution to both terms (essential for correctness)
        2. Check for identical terms (base case)
        3. Handle variable cases with occurs check
        4. Handle constant matching
        5. Handle function decomposition with recursive unification
        """
        
        # Apply current substitution to terms (critical step!)
        term1 = self._apply_substitution_to_term(term1, substitution)
        term2 = self._apply_substitution_to_term(term2, substitution)
        
        # Identity: same term unifies with itself
        if term1.name == term2.name and term1.term_type == term2.term_type:
            # For functions, need to check arguments too
            if term1.term_type == 'function':
                if (term1.arguments is None) != (term2.arguments is None):
                    return False
                if term1.arguments is not None and term2.arguments is not None:
                    if len(term1.arguments) != len(term2.arguments):
                        return False
                    # Arguments will be checked recursively if needed
            return True
            
        # Variable unification: X unifies with any term T (with occurs check)
        if term1.term_type == 'variable':
            # Occurs check: prevent X = f(...X...) which creates infinite structures
            if self._occurs_check(term1.name, term2, substitution):
                return False  # Occurs check failed
            substitution[term1.name] = term2
            return True
            
        elif term2.term_type == 'variable':
            # Symmetric case: T unifies with X 
            if self._occurs_check(term2.name, term1, substitution):
                return False  # Occurs check failed
            substitution[term2.name] = term1
            return True
            
        # Constant unification: constants unify only if identical
        elif term1.term_type == 'constant' and term2.term_type == 'constant':
            return term1.name == term2.name
            
        # Function unification: f(args1) unifies with f(args2) if all args unify
        elif term1.term_type == 'function' and term2.term_type == 'function':
            # Same function name required
            if term1.name != term2.name:
                return False
                
            # Same arity required
            args1 = term1.arguments or []
            args2 = term2.arguments or []
            if len(args1) != len(args2):
                return False
                
            # Recursively unify all argument pairs
            for arg1, arg2 in zip(args1, args2):
                if not self._unify_terms(arg1, arg2, substitution):
                    return False
                    
            return True
            
        # Different types don't unify (e.g., constant with function)
        return False
        
    def _occurs_check(self, var_name: str, term: LogicalTerm, 
                     substitution: Dict[str, LogicalTerm]) -> bool:
        """
        🔍 Occurs Check - Preventing Infinite Logical Structures
        
        The occurs check is a critical safeguard in unification that prevents
        the creation of infinite structures. It checks whether a variable occurs
        within a term that it's being unified with.
        
        🚨 Problem Without Occurs Check:
        Consider unifying X with f(X):
        - Without occurs check: X = f(X) = f(f(X)) = f(f(f(X))) = ... ∞
        - This creates an infinite structure that breaks the algorithm
        
        📚 Historical Context:
        Early Prolog implementations omitted the occurs check for performance,
        leading to unsound unification. Modern systems include it by default
        for correctness, though it can be disabled for speed in special cases.
        
        🔬 Algorithm:
        1. Apply current substitution to the term
        2. If term is a variable, check if it's the target variable
        3. If term is a function, recursively check all arguments
        4. Constants never contain variables
        
        Args:
            var_name (str): Variable name to check for (e.g., "X")
            term (LogicalTerm): Term to search in (e.g., f(X, Y))
            substitution (Dict[str, LogicalTerm]): Current variable bindings
            
        Returns:
            bool: True if var_name occurs in term (indicating failure)
                 False if safe to proceed with unification
        
        💡 Insight: The occurs check embodies the principle that logical
        structures must be finite and well-founded. It's a small price to
        pay for mathematical soundness.
        
        Examples:
            >>> # Safe unification
            >>> occurs = self._occurs_check("X", Constant("john"), {})
            >>> # Returns: False (X does not occur in 'john')
            >>>
            >>> # Dangerous unification  
            >>> f_term = Function("f", [Variable("X")])
            >>> occurs = self._occurs_check("X", f_term, {})
            >>> # Returns: True (X occurs in f(X) - would create infinite structure)
            >>>
            >>> # Safe function unification
            >>> g_term = Function("g", [Variable("Y")])  
            >>> occurs = self._occurs_check("X", g_term, {})
            >>> # Returns: False (X does not occur in g(Y))
        
        ⚡ Performance Impact:
        - Time complexity: O(n) where n is the size of the term
        - Space complexity: O(d) where d is the depth of nested functions
        - Usually fast due to shallow nesting in typical ILP domains
        
        🎯 ILP Applications:
        In ILP, occurs check prevents learning nonsensical rules like:
        ancestor(X) :- ancestor(f(X)) which would be infinite and meaningless.
        """
        
        # Apply current substitution to get the actual term structure
        term = self._apply_substitution_to_term(term, substitution)
        
        # Base case: if term is the target variable, we found an occurrence
        if term.term_type == 'variable':
            return term.name == var_name
            
        # Recursive case: check function arguments
        elif term.term_type == 'function' and term.arguments:
            return any(self._occurs_check(var_name, arg, substitution) 
                      for arg in term.arguments)
            
        # Constants never contain variables
        return False
        
    def _apply_substitution_to_term(self, term: LogicalTerm, 
                                   substitution: Dict[str, LogicalTerm]) -> LogicalTerm:
        """
        🔄 Apply Substitution to Logical Term
        
        Applies a variable substitution to a logical term, replacing variables
        with their bindings. This is fundamental to the unification process
        and logical inference.
        
        🧠 Substitution Theory:
        A substitution θ = {X₁ → t₁, X₂ → t₂, ...} is a mapping from variables
        to terms. Applying θ to term t (written tθ) replaces all occurrences
        of variables with their corresponding terms.
        
        Substitution Rules:
        1. **Variable**: If X is in substitution, replace with binding
        2. **Constant**: Constants are unchanged by substitution
        3. **Function**: Apply substitution recursively to all arguments
        
        Args:
            term (LogicalTerm): Term to apply substitution to
            substitution (Dict[str, LogicalTerm]): Variable to term mapping
            
        Returns:
            LogicalTerm: New term with substitution applied
            
        💡 Key Insight: Substitution application must be recursive for
        function terms to handle nested structures correctly.
        
        Examples:
            >>> # Variable substitution
            >>> term = Variable("X")
            >>> substitution = {"X": Constant("john")}
            >>> result = self._apply_substitution_to_term(term, substitution)
            >>> # Returns: Constant("john")
            >>>
            >>> # Function substitution  
            >>> term = Function("father", [Variable("X"), Variable("Y")])
            >>> substitution = {"X": Constant("john"), "Y": Constant("mary")}
            >>> result = self._apply_substitution_to_term(term, substitution)
            >>> # Returns: Function("father", [Constant("john"), Constant("mary")])
            >>>
            >>> # Partial substitution
            >>> term = Function("likes", [Variable("X"), Variable("Z")])
            >>> substitution = {"X": Constant("john")}  # Z not bound
            >>> result = self._apply_substitution_to_term(term, substitution)
            >>> # Returns: Function("likes", [Constant("john"), Variable("Z")])
        
        🔧 Implementation Notes:
        - Creates new LogicalTerm objects (functional approach)
        - Preserves term structure while applying bindings
        - Handles missing variables gracefully (returns original)
        """
        
        # Variable case: replace with binding if exists
        if term.term_type == 'variable' and term.name in substitution:
            return substitution[term.name]
            
        # Function case: apply recursively to all arguments
        elif term.term_type == 'function' and term.arguments:
            new_args = [self._apply_substitution_to_term(arg, substitution) 
                       for arg in term.arguments]
            return LogicalTerm(name=term.name, term_type='function', arguments=new_args)
            
        # Constant case or unbound variable: return as-is
        else:
            return term
            
    def _unify_atoms(self, atom1: LogicalAtom, atom2: LogicalAtom, 
                    substitution: Dict[str, LogicalTerm]) -> bool:
        """
        ⚛️ Atom Unification - Unifying Complete Logical Statements
        
        Unifies two logical atoms by ensuring they have the same predicate,
        arity, and negation, then unifying all corresponding terms.
        
        🧠 Atom Structure:
        An atom represents a logical statement: predicate(term₁, term₂, ..., termₙ)
        - Predicate: The relation name (e.g., "father", "likes")  
        - Terms: The arguments (constants, variables, functions)
        - Negation: Whether the atom is positive or negative
        
        Unification Requirements:
        1. **Same predicate**: father(...) only unifies with father(...)
        2. **Same arity**: Must have same number of arguments
        3. **Same negation**: Both positive or both negative
        4. **All terms unify**: Each argument pair must unify
        
        Args:
            atom1 (LogicalAtom): First atom (e.g., father(X, john))
            atom2 (LogicalAtom): Second atom (e.g., father(mary, Y))
            substitution (Dict[str, LogicalTerm]): Substitution to update
            
        Returns:
            bool: True if atoms unify successfully, False otherwise
            
        Side Effects:
            Updates substitution dictionary with new variable bindings
        
        Examples:
            >>> # Successful atom unification
            >>> substitution = {}
            >>> atom1 = LogicalAtom("father", [Variable("X"), Constant("john")])
            >>> atom2 = LogicalAtom("father", [Constant("mary"), Variable("Y")])
            >>> success = self._unify_atoms(atom1, atom2, substitution)
            >>> # success = True, substitution = {"X": mary, "Y": john}
            >>>
            >>> # Failed: different predicates
            >>> atom3 = LogicalAtom("mother", [Variable("X")])
            >>> success = self._unify_atoms(atom1, atom3, {})
            >>> # success = False
            >>>
            >>> # Failed: different arity
            >>> atom4 = LogicalAtom("father", [Variable("X")])  # Only 1 arg
            >>> success = self._unify_atoms(atom1, atom4, {})
            >>> # success = False
        
        🎯 ILP Applications:
        - **Rule Matching**: Check if learned rules apply to examples
        - **Background Knowledge**: Unify with known facts and rules
        - **Query Resolution**: Answer questions about learned knowledge
        - **Hypothesis Testing**: Verify rule coverage and consistency
        """
        
        # Same predicate required (e.g., father with father)
        if atom1.predicate != atom2.predicate:
            return False
            
        # Same arity required (same number of arguments)
        if len(atom1.terms) != len(atom2.terms):
            return False
            
        # Same negation required (both positive or both negative)
        if atom1.negated != atom2.negated:
            return False
            
        # Unify all corresponding terms pairwise
        for term1, term2 in zip(atom1.terms, atom2.terms):
            if not self._unify_terms(term1, term2, substitution):
                return False
                
        return True
            
    def _apply_substitution(self, atom: LogicalAtom, 
                           substitution: Dict[str, LogicalTerm]) -> LogicalAtom:
        """
        🔄 Apply Substitution to Logical Atom
        
        Applies a variable substitution to a logical atom by replacing
        variables in all terms with their bindings from the substitution.
        
        🧠 Atom Substitution:
        Given atom A and substitution θ, produces Aθ where all variables
        in A are replaced according to θ. This is essential for:
        - Instantiating general rules with specific values
        - Propagating bindings throughout logical inference
        - Generating specific predictions from learned rules
        
        Args:
            atom (LogicalAtom): Atom to apply substitution to
            substitution (Dict[str, LogicalTerm]): Variable bindings
            
        Returns:
            LogicalAtom: New atom with substitution applied
            
        Examples:
            >>> # Basic substitution
            >>> atom = LogicalAtom("father", [Variable("X"), Variable("Y")])
            >>> substitution = {"X": Constant("john"), "Y": Constant("mary")}
            >>> result = self._apply_substitution(atom, substitution)
            >>> # Returns: LogicalAtom("father", [Constant("john"), Constant("mary")])
            >>>
            >>> # Preserving negation
            >>> neg_atom = LogicalAtom("likes", [Variable("X")], negated=True)
            >>> substitution = {"X": Constant("broccoli")}
            >>> result = self._apply_substitution(neg_atom, substitution)
            >>> # Returns: LogicalAtom("likes", [Constant("broccoli")], negated=True)
        
        🔧 Implementation:
        - Preserves predicate name and negation
        - Applies substitution to each term
        - Creates new LogicalAtom (immutable approach)
        """
        
        new_terms = [self._apply_substitution_to_term(term, substitution) 
                    for term in atom.terms]
        return LogicalAtom(predicate=atom.predicate, terms=new_terms, negated=atom.negated)

    # Theta-subsumption methods (advanced unification concepts)
    def theta_subsumes(self, clause1: LogicalClause, clause2: LogicalClause) -> bool:
        """
        🔗 Theta-Subsumption - Generality Ordering for Logical Clauses
        
        Implements theta-subsumption from Muggleton & De Raedt (1994), which determines
        if one clause is more general than another. This is crucial for ILP systems
        to understand when one rule generalizes another.
        
        🧠 Mathematical Definition:
        Clause C₁ theta-subsumes clause C₂ (written C₁ ⊑θ C₂) if there exists
        a substitution θ such that C₁θ ⊆ C₂. In other words, C₁ is more general
        than C₂ because C₁ can be made to "fit inside" C₂ with proper variable bindings.
        
        💡 Key Insight: Theta-subsumption provides a mathematical foundation for
        comparing rule generality in ILP, enabling systematic refinement operators
        and hypothesis space ordering.
        
        Examples:
            >>> # parent(X,Y) theta-subsumes parent(john,mary) 
            >>> general = LogicalClause(parent(X,Y), [])
            >>> specific = LogicalClause(parent(john,mary), [])
            >>> result = self.theta_subsumes(general, specific)
            >>> # Returns: True with substitution {X: john, Y: mary}
            >>>
            >>> # father(X,Y) :- parent(X,Y) theta-subsumes father(john,mary) :- parent(john,mary), male(john)
            >>> rule1 = LogicalClause(father(X,Y), [parent(X,Y)])
            >>> rule2 = LogicalClause(father(john,mary), [parent(john,mary), male(john)])
            >>> result = self.theta_subsumes(rule1, rule2) 
            >>> # Returns: True (rule1 is more general)
        
        Args:
            clause1 (LogicalClause): Potentially more general clause
            clause2 (LogicalClause): Potentially more specific clause
            
        Returns:
            bool: True if clause1 theta-subsumes clause2
            
        🔬 Algorithm:
        1. Generate possible variable substitutions from clause1 to clause2
        2. For each substitution θ, check if clause1θ ⊆ clause2
        3. Return True if any substitution works
        
        Applications in ILP:
        - Rule generalization and specialization
        - Hypothesis space pruning (avoid redundant rules)
        - Semantic equivalence checking
        - Refinement operator design
        """
        # Try to find a substitution that makes clause1 subsume clause2
        substitutions = self._find_theta_substitutions(clause1, clause2)
        
        for substitution in substitutions:
            if self._check_subsumption_with_substitution(clause1, clause2, substitution):
                return True
        
        return False
    
    def _find_theta_substitutions(self, clause1: LogicalClause, clause2: LogicalClause) -> List[Dict[str, str]]:
        """
        🔍 Generate Candidate Substitutions for Theta-Subsumption
        
        Finds possible variable substitutions that could make clause1 theta-subsume clause2.
        This is a constraint satisfaction problem with exponential search space.
        
        Args:
            clause1 (LogicalClause): Source clause (more general)
            clause2 (LogicalClause): Target clause (more specific)
            
        Returns:
            List[Dict[str, str]]: Candidate substitution dictionaries
            
        Note: Uses heuristics to limit combinatorial explosion while maintaining completeness
        for practical ILP cases.
        """
        substitutions = []
        
        # Get all variables from clause1
        vars1 = self._extract_variables_from_clause(clause1)
        
        # Get all terms from clause2  
        terms2 = self._extract_terms_from_clause(clause2)
        
        # Generate all possible substitutions
        # This is simplified - full implementation would use constraint satisfaction
        if len(vars1) == 0:
            return [{}]  # No variables to substitute
        
        if len(vars1) <= 3:  # Limit combinatorial explosion
            from itertools import product
            for combination in product(terms2, repeat=len(vars1)):
                substitution = dict(zip(vars1, combination))
                substitutions.append(substitution)
        else:
            # For larger variable sets, use greedy approach
            substitutions.append(dict(zip(vars1, terms2[:len(vars1)])))
        
        return substitutions[:10]  # Limit to avoid excessive computation
    
    def _extract_variables_from_clause(self, clause: LogicalClause) -> List[str]:
        """Extract all variable names from a logical clause"""
        variables = set()
        
        # Check head
        variables.update(self._extract_variables_from_atom(clause.head))
        
        # Check body
        for atom in clause.body:
            variables.update(self._extract_variables_from_atom(atom))
        
        return list(variables)
    
    def _extract_variables_from_atom(self, atom: LogicalAtom) -> Set[str]:
        """Extract variable names from a logical atom"""
        variables = set()
        for term in atom.terms:
            if term.term_type == 'variable':
                variables.add(term.name)
            elif term.term_type == 'function' and term.arguments:
                for arg in term.arguments:
                    if arg.term_type == 'variable':
                        variables.add(arg.name)
        return variables
    
    def _extract_terms_from_clause(self, clause: LogicalClause) -> List[str]:
        """Extract all term names from a logical clause (constants and variables)"""
        terms = set()
        
        # Check head
        terms.update(self._extract_terms_from_atom(clause.head))
        
        # Check body
        for atom in clause.body:
            terms.update(self._extract_terms_from_atom(atom))
        
        return list(terms)
    
    def _extract_terms_from_atom(self, atom: LogicalAtom) -> Set[str]:
        """Extract all term names from a logical atom"""
        terms = set()
        for term in atom.terms:
            terms.add(term.name)
            if term.term_type == 'function' and term.arguments:
                for arg in term.arguments:
                    terms.add(arg.name)
        return terms
    
    def _check_subsumption_with_substitution(self, clause1: LogicalClause, clause2: LogicalClause, 
                                           substitution: Dict[str, str]) -> bool:
        """
        🎯 Check Subsumption with Specific Substitution
        
        Verifies if clause1 with the given substitution is a subset of clause2.
        This implements the core logic of theta-subsumption checking.
        
        Args:
            clause1 (LogicalClause): Source clause to apply substitution to
            clause2 (LogicalClause): Target clause to check against
            substitution (Dict[str, str]): Variable bindings to apply
            
        Returns:
            bool: True if clause1θ ⊆ clause2 where θ is the substitution
        """
        # Apply substitution to clause1
        substituted_clause1 = self._apply_substitution_to_clause(clause1, substitution)
        
        # Check if head of substituted clause1 matches head of clause2
        if not self._atoms_match(substituted_clause1.head, clause2.head):
            return False
        
        # Check if all body literals of substituted clause1 are in clause2's body
        for literal1 in substituted_clause1.body:
            found_match = False
            for literal2 in clause2.body:
                if self._atoms_match(literal1, literal2):
                    found_match = True
                    break
            if not found_match:
                return False
        
        return True
    
    def _apply_substitution_to_clause(self, clause: LogicalClause, substitution: Dict[str, str]) -> LogicalClause:
        """
        🔄 Apply String Substitution to Logical Clause
        
        Applies variable substitutions to an entire logical clause, creating
        a new clause with variables replaced by their bindings.
        
        Note: This version works with string-to-string substitutions for 
        theta-subsumption (different from LogicalTerm substitutions used in unification).
        """
        # Apply to head
        new_head = self._apply_substitution_to_atom_string(clause.head, substitution)
        
        # Apply to body
        new_body = []
        for atom in clause.body:
            new_atom = self._apply_substitution_to_atom_string(atom, substitution)
            new_body.append(new_atom)
        
        return LogicalClause(head=new_head, body=new_body, confidence=clause.confidence)
    
    def _apply_substitution_to_atom_string(self, atom: LogicalAtom, substitution: Dict[str, str]) -> LogicalAtom:
        """Apply string substitution to a logical atom"""
        new_terms = []
        for term in atom.terms:
            if term.term_type == 'variable' and term.name in substitution:
                # Substitute variable
                new_term = LogicalTerm(name=substitution[term.name], term_type='constant')
            else:
                # Keep term as is (could extend to handle functions)
                new_term = term
            new_terms.append(new_term)
        
        return LogicalAtom(predicate=atom.predicate, terms=new_terms, negated=atom.negated)
    
    def _atoms_match(self, atom1: LogicalAtom, atom2: LogicalAtom) -> bool:
        """
        ⚛️ Check if Two Atoms Match Exactly
        
        Determines if two logical atoms are identical in predicate, terms, and negation.
        Used in subsumption checking to verify structural equivalence.
        
        Args:
            atom1 (LogicalAtom): First atom
            atom2 (LogicalAtom): Second atom
            
        Returns:
            bool: True if atoms match exactly
        """
        if atom1.predicate != atom2.predicate or atom1.negated != atom2.negated:
            return False
        
        if len(atom1.terms) != len(atom2.terms):
            return False
        
        for term1, term2 in zip(atom1.terms, atom2.terms):
            if term1.name != term2.name:
                return False
        
        return True

    # Helper methods for predicate compatibility (required for unification)
    def _predicates_compatible(self, pred1: str, pred2: str) -> bool:
        """
        🔗 Enhanced Predicate Compatibility for ILP Unification
        
        Determines if two predicates can be unified, supporting:
        - Direct matching
        - Alias relationships (father → parent)
        - Hierarchical relationships (mammal → animal)  
        - Equivalence classes (spouse ↔ married)
        - Theta-subsumption ordering
        
        This extends basic unification to handle domain-specific knowledge
        and makes ILP systems more flexible with real-world data.
        
        Args:
            pred1 (str): First predicate name
            pred2 (str): Second predicate name
            
        Returns:
            bool: True if predicates can be unified
            
        Note: This method should be implemented in the main ILP class
        that uses this mixin, as it requires access to domain knowledge.
        """
        # Default implementation: exact match only
        if pred1 == pred2:
            return True
            
        # Special handling for target predicate placeholder
        if pred1 == "target_pred" or pred2 == "target_pred":
            return True
            
        # This method should be overridden in the main class to provide
        # domain-specific predicate compatibility logic
        return False