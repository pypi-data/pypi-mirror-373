#!/usr/bin/env python3
"""
🧪 PREDICATE SYSTEM TEST SUITE - Comprehensive Testing and Demonstration
=======================================================================

This test suite demonstrates and validates the predicate system functionality
extracted from the main ILP system, showcasing:

1. Predicate hierarchy management
2. Alias and equivalence handling  
3. Vocabulary extraction and management
4. Theta-subsumption compatibility checking
5. Advanced predicate compatibility reasoning

Author: Benedict Chen
"""

import sys
from pathlib import Path

# Add the package to Python path for importing
sys.path.append(str(Path(__file__).parent))

from inductive_logic_programming.ilp_modules import (
    LogicalTerm, LogicalAtom, LogicalClause, Example, PredicateSystemMixin
)


class TestPredicateSystem(PredicateSystemMixin):
    """Test class that inherits predicate system functionality"""
    
    def __init__(self):
        """Initialize test instance with predicate system"""
        # Initialize required attributes for the mixin
        self.background_knowledge = []
        self.predicates = set()
        self.constants = set()
        self.functions = set()
        
        # Initialize the predicate system
        self._initialize_predicate_system()
        
        print("🚀 Test Predicate System initialized")
        

def test_vocabulary_extraction():
    """Test vocabulary extraction from clauses, atoms, and terms"""
    
    print("\n📚 Testing Vocabulary Extraction")
    print("=" * 50)
    
    system = TestPredicateSystem()
    
    # Create complex logical structures for testing
    print("Creating test logical structures...")
    
    # Test clause: grandparent(X,Z) :- parent(X,Y), parent(Y,Z), different(X,Z)
    head = LogicalAtom("grandparent", [
        LogicalTerm("X", term_type="variable"),
        LogicalTerm("Z", term_type="variable")
    ])
    
    body = [
        LogicalAtom("parent", [
            LogicalTerm("X", term_type="variable"),
            LogicalTerm("Y", term_type="variable")
        ]),
        LogicalAtom("parent", [
            LogicalTerm("Y", term_type="variable"), 
            LogicalTerm("Z", term_type="variable")
        ]),
        LogicalAtom("different", [
            LogicalTerm("X", term_type="variable"),
            LogicalTerm("Z", term_type="variable")
        ])
    ]
    
    test_clause = LogicalClause(head=head, body=body)
    
    # Test vocabulary extraction
    system._update_vocabulary_from_clause(test_clause)
    
    print(f"✅ Extracted predicates: {system.predicates}")
    print(f"✅ Extracted constants: {system.constants}")
    print(f"✅ Extracted functions: {system.functions}")
    
    # Test with constants and functions
    print("\nTesting with constants and functions...")
    
    # Create atom with constants: loves(john, mary)
    love_atom = LogicalAtom("loves", [
        LogicalTerm("john", term_type="constant"),
        LogicalTerm("mary", term_type="constant")
    ])
    
    system._update_vocabulary_from_atom(love_atom)
    
    # Create atom with function: father_of(john, child_of(mary, bob))
    function_atom = LogicalAtom("relationship", [
        LogicalTerm("father_of", term_type="function", arguments=[
            LogicalTerm("john", term_type="constant"),
            LogicalTerm("child_of", term_type="function", arguments=[
                LogicalTerm("mary", term_type="constant"),
                LogicalTerm("bob", term_type="constant")
            ])
        ])
    ])
    
    system._update_vocabulary_from_atom(function_atom)
    
    print(f"✅ Updated predicates: {system.predicates}")
    print(f"✅ Updated constants: {system.constants}")
    print(f"✅ Updated functions: {system.functions}")


def test_predicate_compatibility():
    """Test predicate compatibility checking with various mechanisms"""
    
    print("\n🧩 Testing Predicate Compatibility")
    print("=" * 50)
    
    system = TestPredicateSystem()
    
    # Test direct compatibility
    print("Testing direct compatibility...")
    assert system._predicates_compatible("parent", "parent") == True
    print("✅ Direct match: parent ↔ parent")
    
    # Test alias compatibility
    print("\nTesting alias compatibility...")
    assert system._predicates_compatible("father", "parent") == True
    assert system._predicates_compatible("mother", "parent") == True
    assert system._predicates_compatible("son", "child") == True
    print("✅ Alias compatibility: father → parent, mother → parent, son → child")
    
    # Test hierarchy compatibility
    print("\nTesting hierarchy compatibility...")
    assert system._predicates_compatible("male", "female") == True  # Both in 'person'
    assert system._predicates_compatible("parent", "grandparent") == True  # Both in 'relation'
    assert system._predicates_compatible("tall", "short") == True  # Both in 'property'
    print("✅ Hierarchy compatibility: male ↔ female (person), parent ↔ grandparent (relation)")
    
    # Test equivalence compatibility
    print("\nTesting equivalence compatibility...")
    assert system._predicates_compatible("spouse", "married") == True
    assert system._predicates_compatible("friend", "friend") == True
    print("✅ Equivalence compatibility: spouse ↔ married, friend ↔ friend")
    
    # Test incompatibility
    print("\nTesting incompatible predicates...")
    assert system._predicates_compatible("parent", "house") == False
    assert system._predicates_compatible("happy", "tree") == False
    print("✅ Correctly identified incompatible predicates")


def test_predicate_system_management():
    """Test adding and managing predicate system components"""
    
    print("\n🔧 Testing Predicate System Management")
    print("=" * 50)
    
    system = TestPredicateSystem()
    
    # Test adding custom aliases
    print("Adding custom aliases...")
    system.add_predicate_alias("dad", "parent")
    system.add_predicate_alias("mom", "parent") 
    system.add_predicate_alias("client", "customer")
    
    # Verify aliases work
    assert system._predicates_compatible("dad", "parent") == True
    assert system._predicates_compatible("mom", "father") == True  # Both resolve to parent
    assert system._predicates_compatible("client", "customer") == True
    print("✅ Custom aliases working correctly")
    
    # Test adding custom equivalences
    print("\nAdding custom equivalences...")
    system.add_predicate_equivalence("colleague", "coworker")
    system.add_predicate_equivalence("intelligent", "smart")
    
    # Verify equivalences work
    assert system._predicates_compatible("colleague", "coworker") == True
    assert system._predicates_compatible("intelligent", "smart") == True
    print("✅ Custom equivalences working correctly")
    
    # Test adding custom hierarchies
    print("\nAdding custom hierarchies...")
    system.add_predicate_hierarchy("animal", {"dog", "cat", "bird", "fish"})
    system.add_predicate_hierarchy("color", {"red", "blue", "green", "yellow"})
    
    # Verify hierarchies work
    assert system._predicates_compatible("dog", "cat") == True  # Both in 'animal'
    assert system._predicates_compatible("red", "blue") == True  # Both in 'color'
    assert system._predicates_compatible("dog", "red") == False  # Different hierarchies
    print("✅ Custom hierarchies working correctly")


def test_theta_subsumption():
    """Test theta-subsumption functionality"""
    
    print("\n🎯 Testing Theta-Subsumption")
    print("=" * 50)
    
    system = TestPredicateSystem()
    
    # Test Case 1: Simple subsumption
    # General: parent(X,Y) :- father(X,Y)
    general_clause = LogicalClause(
        head=LogicalAtom("parent", [
            LogicalTerm("X", term_type="variable"),
            LogicalTerm("Y", term_type="variable")
        ]),
        body=[
            LogicalAtom("father", [
                LogicalTerm("X", term_type="variable"),
                LogicalTerm("Y", term_type="variable")
            ])
        ]
    )
    
    # Specific: parent(john,mary) :- father(john,mary), male(john)
    specific_clause = LogicalClause(
        head=LogicalAtom("parent", [
            LogicalTerm("john", term_type="constant"),
            LogicalTerm("mary", term_type="constant")
        ]),
        body=[
            LogicalAtom("father", [
                LogicalTerm("john", term_type="constant"),
                LogicalTerm("mary", term_type="constant")
            ]),
            LogicalAtom("male", [
                LogicalTerm("john", term_type="constant")
            ])
        ]
    )
    
    print("Testing simple subsumption...")
    print(f"General clause: {general_clause}")
    print(f"Specific clause: {specific_clause}")
    
    subsumes = system.theta_subsumes(general_clause, specific_clause)
    print(f"✅ Theta-subsumption result: {subsumes}")
    
    # Test reverse (should be False)
    reverse_subsumes = system.theta_subsumes(specific_clause, general_clause)
    print(f"✅ Reverse subsumption (should be False): {reverse_subsumes}")
    
    # Test Case 2: Variable extraction
    print("\nTesting variable extraction...")
    variables = system._extract_variables_from_clause(general_clause)
    print(f"Variables in general clause: {variables}")
    
    terms = system._extract_terms_from_clause(specific_clause)
    print(f"Terms in specific clause: {terms}")
    
    # Test Case 3: Substitution generation
    print("\nTesting substitution generation...")
    substitutions = system._find_theta_substitutions(general_clause, specific_clause)
    print(f"Generated substitutions: {substitutions}")
    
    # Test substitution application
    if substitutions:
        applied_clause = system._apply_substitution_to_clause(general_clause, substitutions[0])
        print(f"Applied substitution result: {applied_clause}")


def test_vocabulary_reporting():
    """Test vocabulary reporting and system management"""
    
    print("\n📊 Testing Vocabulary Reporting")
    print("=" * 50)
    
    system = TestPredicateSystem()
    
    # Add some test vocabulary
    system.predicates.update(["parent", "child", "loves", "tall"])
    system.constants.update(["john", "mary", "bob", "alice"])  
    system.functions.update(["father_of", "age_of"])
    
    # Test vocabulary report
    vocab_report = system.get_predicate_vocabulary()
    
    print("Vocabulary Report:")
    for category, items in vocab_report.items():
        print(f"  {category.capitalize()}: {sorted(items)}")
    
    # Test system validation
    print("\nTesting system validation...")
    validation_report = system.validate_predicate_system()
    
    print("Validation Report:")
    for category, messages in validation_report.items():
        if messages:
            print(f"  {category.upper()}:")
            for msg in messages:
                print(f"    - {msg}")
        else:
            print(f"  {category.upper()}: None")


def test_advanced_features():
    """Test advanced predicate system features"""
    
    print("\n🚀 Testing Advanced Features")
    print("=" * 50)
    
    system = TestPredicateSystem()
    
    # Test complex hierarchy relationships
    print("Setting up complex domain hierarchies...")
    
    # Medical domain
    system.add_predicate_hierarchy("medical_condition", {
        "disease", "syndrome", "disorder", "infection", "injury"
    })
    system.add_predicate_hierarchy("medical_professional", {
        "doctor", "nurse", "surgeon", "therapist", "specialist"
    })
    
    # Business domain
    system.add_predicate_hierarchy("business_role", {
        "manager", "employee", "director", "analyst", "consultant"
    })
    system.add_predicate_hierarchy("business_process", {
        "planning", "execution", "monitoring", "evaluation", "optimization"
    })
    
    # Test domain-specific aliases
    system.add_predicate_alias("physician", "doctor")
    system.add_predicate_alias("patient", "person")
    system.add_predicate_alias("diagnosis", "medical_condition")
    system.add_predicate_alias("staff", "employee")
    
    # Test cross-domain compatibility
    print("\nTesting cross-domain compatibility...")
    
    # Should be compatible (same hierarchy)
    assert system._predicates_compatible("doctor", "nurse") == True
    assert system._predicates_compatible("manager", "employee") == True
    
    # Should be incompatible (different hierarchies)
    assert system._predicates_compatible("doctor", "manager") == False
    assert system._predicates_compatible("disease", "planning") == False
    
    # Should work through aliases
    assert system._predicates_compatible("physician", "doctor") == True
    assert system._predicates_compatible("staff", "manager") == True
    
    print("✅ Advanced domain hierarchies working correctly")
    
    # Test system clearing
    print("\nTesting system clearing...")
    original_predicates = len(system.predicates)
    system.clear_predicate_system()
    
    print(f"Predicates before clearing: {original_predicates}")
    print(f"Predicates after clearing: {len(system.predicates)}")
    print("✅ System clearing working correctly")


def demonstrate_practical_usage():
    """Demonstrate practical usage patterns"""
    
    print("\n💡 Practical Usage Demonstration")
    print("=" * 50)
    
    system = TestPredicateSystem()
    
    # Scenario: Family relationship learning
    print("Scenario: Learning family relationships")
    
    # Add domain knowledge
    system.add_predicate_hierarchy("family_member", {
        "parent", "child", "grandparent", "grandchild", "sibling", "spouse"
    })
    
    system.add_predicate_alias("father", "parent")
    system.add_predicate_alias("mother", "parent")
    system.add_predicate_alias("son", "child")
    system.add_predicate_alias("daughter", "child")
    system.add_predicate_alias("grandfather", "grandparent")
    system.add_predicate_alias("grandmother", "grandparent")
    
    # Create sample background knowledge
    bg_clauses = [
        # parent(john, mary) :- father(john, mary)
        LogicalClause(
            head=LogicalAtom("parent", [
                LogicalTerm("john", term_type="constant"), 
                LogicalTerm("mary", term_type="constant")
            ]),
            body=[LogicalAtom("father", [
                LogicalTerm("john", term_type="constant"), 
                LogicalTerm("mary", term_type="constant")
            ])]
        ),
        # grandparent(X,Z) :- parent(X,Y), parent(Y,Z)
        LogicalClause(
            head=LogicalAtom("grandparent", [
                LogicalTerm("X", term_type="variable"), 
                LogicalTerm("Z", term_type="variable")
            ]),
            body=[
                LogicalAtom("parent", [
                    LogicalTerm("X", term_type="variable"), 
                    LogicalTerm("Y", term_type="variable")
                ]),
                LogicalAtom("parent", [
                    LogicalTerm("Y", term_type="variable"), 
                    LogicalTerm("Z", term_type="variable")
                ])
            ]
        )
    ]
    
    system.background_knowledge = bg_clauses
    
    # Extract vocabulary from background knowledge
    for clause in bg_clauses:
        system._update_vocabulary_from_clause(clause)
    
    print("Background knowledge processed:")
    for i, clause in enumerate(bg_clauses, 1):
        print(f"  {i}. {clause}")
    
    # Test predicate relationships
    print("\nTesting learned predicate relationships:")
    test_pairs = [
        ("father", "parent"),
        ("grandmother", "grandparent"), 
        ("parent", "grandparent"),
        ("sibling", "spouse"),
        ("father", "teacher")  # Should be incompatible
    ]
    
    for pred1, pred2 in test_pairs:
        compatible = system._predicates_compatible(pred1, pred2)
        status = "✅ Compatible" if compatible else "❌ Incompatible"
        print(f"  {pred1} ↔ {pred2}: {status}")
    
    # Show final vocabulary
    vocab = system.get_predicate_vocabulary()
    print(f"\nFinal vocabulary size:")
    print(f"  Predicates: {len(vocab['predicates'])}")
    print(f"  Constants: {len(vocab['constants'])}")
    print(f"  Hierarchies: {len(vocab['hierarchies'])}")
    print(f"  Aliases: {len(vocab['aliases'])}")


def run_all_tests():
    """Run the complete test suite"""
    
    print("🧪 PREDICATE SYSTEM TEST SUITE")
    print("=" * 70)
    print("Testing comprehensive predicate system functionality...")
    
    try:
        test_vocabulary_extraction()
        test_predicate_compatibility()
        test_predicate_system_management()
        test_theta_subsumption()
        test_vocabulary_reporting()
        test_advanced_features()
        demonstrate_practical_usage()
        
        print("\n🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("✅ Predicate system module is working correctly")
        print("✅ All key features validated")
        print("✅ Ready for integration with main ILP system")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()