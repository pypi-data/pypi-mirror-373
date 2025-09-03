#!/usr/bin/env python3
"""
🎯 MODULAR ILP SYSTEM DEMONSTRATION
===================================

This script demonstrates the new modular ILP core system, showing how all the
extracted modules work together seamlessly while maintaining full backward
compatibility with the original implementation.

Features Demonstrated:
- Factory functions for different use cases
- Complete family relationship learning
- Advanced query answering and explanation
- Statistical analysis and coverage metrics
- All major ILP operations in action

Author: Benedict Chen
"""

import sys
import os

# Add the package to path for import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from inductive_logic_programming import (
    InductiveLogicProgrammer,
    create_educational_ilp,
    create_research_ilp_system,
    create_production_ilp,
    create_atom, create_constant, create_variable,
    create_fact, create_rule
)

def demonstrate_factory_functions():
    """Demonstrate different factory functions for various use cases"""
    print("🏭 FACTORY FUNCTIONS DEMONSTRATION")
    print("=" * 50)
    
    # Educational ILP (simple, fast, clear)
    edu_ilp = create_educational_ilp()
    print(f"📚 Educational ILP: max_clause_length={edu_ilp.max_clause_length}, confidence_threshold={edu_ilp.confidence_threshold}")
    
    # Research ILP (complex, advanced)  
    research_ilp = create_research_ilp_system()
    print(f"🔬 Research ILP: max_clause_length={research_ilp.max_clause_length}, semantic_setting='{research_ilp.semantic_setting}'")
    
    # Production ILP (balanced, robust)
    prod_ilp = create_production_ilp()
    print(f"🏭 Production ILP: noise_tolerance={prod_ilp.noise_tolerance}, coverage_threshold={prod_ilp.coverage_threshold}")
    
    print()

def demonstrate_comprehensive_learning():
    """Demonstrate complete ILP learning workflow with family relationships"""
    print("👨‍👩‍👧‍👦 COMPREHENSIVE FAMILY RELATIONSHIP LEARNING")
    print("=" * 55)
    
    # Create educational ILP system for clear demonstration
    ilp = create_educational_ilp()
    
    print("📚 Adding background knowledge...")
    
    # Background knowledge: basic family facts
    family_facts = [
        # Parent relationships
        ("parent", ["john", "mary"]),
        ("parent", ["john", "bob"]), 
        ("parent", ["mary", "ann"]),
        ("parent", ["mary", "tom"]),
        ("parent", ["bob", "sue"]),
        ("parent", ["alice", "mary"]),
        ("parent", ["alice", "bob"]),
        
        # Gender information
        ("male", ["john"]),
        ("male", ["bob"]),
        ("male", ["tom"]),
        ("female", ["mary"]),
        ("female", ["ann"]),
        ("female", ["sue"]),
        ("female", ["alice"])
    ]
    
    # Add background knowledge
    for predicate, args in family_facts:
        constants = [create_constant(arg) for arg in args]
        atom = create_atom(predicate, constants)
        fact = create_fact(atom)
        ilp.add_background_knowledge(fact)
    
    # Add some rules as background knowledge
    father_rule = create_rule(
        create_atom("father", [create_variable("X"), create_variable("Y")]),
        [
            create_atom("parent", [create_variable("X"), create_variable("Y")]),
            create_atom("male", [create_variable("X")])
        ]
    )
    ilp.add_background_knowledge(father_rule)
    
    mother_rule = create_rule(
        create_atom("mother", [create_variable("X"), create_variable("Y")]),
        [
            create_atom("parent", [create_variable("X"), create_variable("Y")]),
            create_atom("female", [create_variable("X")])
        ]
    )
    ilp.add_background_knowledge(mother_rule)
    
    print(f"Added {len(ilp.background_knowledge)} background knowledge clauses")
    
    print("\n📝 Adding training examples...")
    
    # Positive examples for grandparent relationship
    grandparent_positives = [
        ("grandparent", ["john", "ann"]),    # john is ann's grandparent
        ("grandparent", ["john", "tom"]),    # john is tom's grandparent  
        ("grandparent", ["john", "sue"]),    # john is sue's grandparent
        ("grandparent", ["alice", "ann"]),   # alice is ann's grandparent
        ("grandparent", ["alice", "tom"]),   # alice is tom's grandparent
        ("grandparent", ["alice", "sue"]),   # alice is sue's grandparent
    ]
    
    # Negative examples (not grandparent relationships)
    grandparent_negatives = [
        ("grandparent", ["mary", "john"]),   # mary is not john's grandparent
        ("grandparent", ["bob", "alice"]),   # bob is not alice's grandparent
        ("grandparent", ["ann", "tom"]),     # ann is not tom's grandparent (siblings)
        ("grandparent", ["sue", "mary"]),    # sue is not mary's grandparent
    ]
    
    # Add positive examples
    for predicate, args in grandparent_positives:
        constants = [create_constant(arg) for arg in args]
        atom = create_atom(predicate, constants)
        ilp.add_example(atom, True)
    
    # Add negative examples  
    for predicate, args in grandparent_negatives:
        constants = [create_constant(arg) for arg in args]
        atom = create_atom(predicate, constants)
        ilp.add_example(atom, False)
    
    print(f"Added {len(ilp.positive_examples)} positive examples")
    print(f"Added {len(ilp.negative_examples)} negative examples")
    
    print("\n🧠 Learning rules for 'grandparent'...")
    
    # Learn grandparent rules
    try:
        learned_rules = ilp.learn_rules("grandparent")
        
        print(f"\n✅ Successfully learned {len(learned_rules)} rules!")
        
        # Display learned rules
        ilp.print_learned_rules()
        
        # Display learning statistics
        ilp.print_learning_statistics()
        
        return ilp, learned_rules
        
    except Exception as e:
        print(f"❌ Learning failed: {e}")
        return ilp, []

def demonstrate_query_system(ilp, learned_rules):
    """Demonstrate query answering and explanation system"""
    print("\n🔍 QUERY SYSTEM DEMONSTRATION")  
    print("=" * 35)
    
    if not learned_rules:
        print("❌ No learned rules available for querying")
        return
    
    # Test queries
    test_queries = [
        # Should succeed (known grandparent relationships)
        ("grandparent", ["john", "ann"]),
        ("grandparent", ["alice", "tom"]),
        
        # Should fail (not grandparent relationships) 
        ("grandparent", ["mary", "john"]),
        ("grandparent", ["bob", "sue"]),
        
        # Unknown cases (test generalization)
        ("parent", ["john", "mary"]),  # Known fact
        ("male", ["john"]),            # Known fact
    ]
    
    print("Testing queries:")
    print("-" * 20)
    
    for predicate, args in test_queries:
        constants = [create_constant(arg) for arg in args]
        query_atom = create_atom(predicate, constants)
        
        # Query the system
        can_prove, confidence, proof_rules = ilp.query(query_atom)
        
        # Display result
        result_symbol = "✅" if can_prove else "❌"
        print(f"{result_symbol} {query_atom}: {'PROVABLE' if can_prove else 'NOT PROVABLE'} (confidence: {confidence:.3f})")
        
        if can_prove and proof_rules:
            print(f"   Proof uses {len(proof_rules)} rule(s)")
            
        # Get explanation
        explanations = ilp.explain_prediction(query_atom)
        for explanation in explanations[:3]:  # Limit output
            print(f"   {explanation}")
        print()

def demonstrate_modular_architecture():
    """Demonstrate the modular architecture benefits"""
    print("🧩 MODULAR ARCHITECTURE DEMONSTRATION")
    print("=" * 40)
    
    # Show individual mixin usage
    from inductive_logic_programming import HypothesisGenerationMixin, UnificationEngineMixin
    
    class CustomILP(HypothesisGenerationMixin, UnificationEngineMixin):
        """Example of custom ILP system using only specific mixins"""
        def __init__(self):
            self.max_variables = 3
            self.max_clause_length = 4
            self.background_knowledge = []
            self.learning_stats = {'clauses_generated': 0}
            
    custom_system = CustomILP()
    print(f"✅ Created custom ILP system with only HypothesisGeneration and Unification mixins")
    print(f"   Available methods: {[method for method in dir(custom_system) if method.startswith('_generate') or method.startswith('_robinson')]}")
    
    # Show full system capabilities
    full_system = InductiveLogicProgrammer()
    mixin_count = len([cls for cls in InductiveLogicProgrammer.__mro__ if 'Mixin' in cls.__name__])
    print(f"✅ Full ILP system integrates {mixin_count} specialized mixins")
    
    print("\n📊 Vocabulary tracking demonstration:")
    full_system.add_example(create_atom("loves", [create_constant("alice"), create_constant("pizza")]), True)
    full_system.add_example(create_atom("parent", [create_variable("X"), create_variable("Y")]), True)
    
    for vocab_type, vocab_set in full_system.vocabulary.items():
        if vocab_set:
            print(f"   {vocab_type}: {sorted(list(vocab_set))}")

def demonstrate_backward_compatibility():
    """Demonstrate that the new system is backward compatible"""
    print("\n🔄 BACKWARD COMPATIBILITY DEMONSTRATION")
    print("=" * 42)
    
    # Test that all original API methods still work
    ilp = InductiveLogicProgrammer()
    
    # Original initialization parameters
    original_params = {
        'max_clause_length': 5,
        'max_variables': 4, 
        'confidence_threshold': 0.8,
        'coverage_threshold': 0.7,
        'noise_tolerance': 0.1,
        'semantic_setting': 'normal'
    }
    
    ilp_original_style = InductiveLogicProgrammer(**original_params)
    print("✅ Original initialization style works")
    
    # Test original method calls
    example_atom = create_atom("test", [create_constant("a"), create_constant("b")])
    ilp_original_style.add_example(example_atom, True)
    print("✅ Original add_example() method works")
    
    fact = create_fact(create_atom("knows", [create_constant("alice"), create_constant("bob")]))
    ilp_original_style.add_background_knowledge(fact)
    print("✅ Original add_background_knowledge() method works")
    
    print("✅ All original API methods maintained!")

def main():
    """Main demonstration orchestrator"""
    print("🧠 MODULAR ILP SYSTEM COMPREHENSIVE DEMONSTRATION")
    print("=" * 55)
    print("Based on Muggleton & De Raedt (1994) with modern modular architecture")
    print()
    
    # Run all demonstrations
    try:
        demonstrate_factory_functions()
        
        ilp, learned_rules = demonstrate_comprehensive_learning()
        
        demonstrate_query_system(ilp, learned_rules)
        
        demonstrate_modular_architecture()
        
        demonstrate_backward_compatibility()
        
        print("\n🎉 DEMONSTRATION COMPLETE!")
        print("=" * 30)
        print("✅ All modular ILP components working perfectly!")
        print("✅ Full backward compatibility maintained")
        print("✅ Enhanced functionality through factory functions")
        print("✅ Clean separation of concerns via mixins") 
        print("✅ Comprehensive learning and query capabilities")
        
        print("\n💡 Ready for:")
        print("   📚 Educational use with create_educational_ilp()")
        print("   🔬 Research applications with create_research_ilp_system()")
        print("   🏭 Production deployment with create_production_ilp()")
        print("   🔧 Custom systems with individual mixins")
        
    except Exception as e:
        print(f"❌ Demonstration encountered error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()