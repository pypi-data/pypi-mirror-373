#!/usr/bin/env python3
"""
🧪 Test Script for Semantic Evaluation Module
==============================================

This script demonstrates and tests the semantic evaluation functionality
extracted into the semantic_evaluation.py module.
"""

from inductive_logic_programming.ilp_modules import (
    LogicalTerm, LogicalAtom, LogicalClause, Example,
    SemanticEvaluationMixin, evaluate_semantic_quality, compare_semantic_settings
)


def create_test_data():
    """Create test hypothesis and examples"""
    
    # Create hypothesis: father(X, Y) :- parent(X, Y), male(X)
    hypothesis = LogicalClause(
        head=LogicalAtom("father", [
            LogicalTerm("X", "variable"),
            LogicalTerm("Y", "variable")
        ]),
        body=[
            LogicalAtom("parent", [
                LogicalTerm("X", "variable"),
                LogicalTerm("Y", "variable")
            ]),
            LogicalAtom("male", [
                LogicalTerm("X", "variable")
            ])
        ]
    )
    
    # Create positive examples
    positive_examples = [
        Example(LogicalAtom("father", [
            LogicalTerm("john", "constant"),
            LogicalTerm("mary", "constant")
        ]), is_positive=True),
        Example(LogicalAtom("father", [
            LogicalTerm("bob", "constant"),
            LogicalTerm("alice", "constant")
        ]), is_positive=True)
    ]
    
    # Create negative examples
    negative_examples = [
        Example(LogicalAtom("father", [
            LogicalTerm("mary", "constant"),
            LogicalTerm("john", "constant")
        ]), is_positive=False),
        Example(LogicalAtom("father", [
            LogicalTerm("alice", "constant"),
            LogicalTerm("bob", "constant")
        ]), is_positive=False)
    ]
    
    return hypothesis, positive_examples, negative_examples


def test_standalone_evaluation():
    """Test standalone semantic evaluation"""
    print("🔍 Testing Standalone Semantic Evaluation")
    print("=" * 50)
    
    hypothesis, pos_examples, neg_examples = create_test_data()
    
    # Test each semantic setting
    for setting in ['normal', 'definite', 'nonmonotonic']:
        print(f"\n📊 {setting.upper()} Semantics:")
        
        result = evaluate_semantic_quality(
            hypothesis, pos_examples, neg_examples,
            semantic_setting=setting,
            coverage_threshold=0.7,
            noise_tolerance=0.1
        )
        
        print(f"   Semantic Valid: {result['semantic_valid']}")
        print(f"   Positive Coverage: {result['positive_coverage']}")
        print(f"   Negative Coverage: {result['negative_coverage']}")
        print(f"   Coverage Ratio: {result['coverage_ratio']:.2f}")
        print(f"   Precision: {result['precision']:.2f}")
        print(f"   Semantic Score: {result['semantic_score']:.2f}")


def test_comparison():
    """Test semantic setting comparison"""
    print("\n🔬 Testing Semantic Settings Comparison")
    print("=" * 50)
    
    hypothesis, pos_examples, neg_examples = create_test_data()
    
    comparison = compare_semantic_settings(hypothesis, pos_examples, neg_examples)
    
    print(f"\nComparison Results for: {hypothesis}")
    print("-" * 60)
    
    for setting, results in comparison.items():
        print(f"{setting.upper():>12}: Valid={results['semantic_valid']:>5}, "
              f"Score={results['semantic_score']:>5.2f}, "
              f"Precision={results['precision']:>5.2f}")


class TestSemanticILP(SemanticEvaluationMixin):
    """Test implementation of semantic-aware ILP system"""
    
    def __init__(self, semantic_setting='normal'):
        self.semantic_setting = semantic_setting
        self.coverage_threshold = 0.7
        self.noise_tolerance = 0.1
        self.confidence_threshold = 0.8
        self.max_clause_length = 5
        self.max_variables = 4
        self.background_knowledge = []
        
    def _specialize_clause(self, clause, negative_examples):
        """Dummy implementation for testing"""
        return []
        
    def _generalize_clause(self, clause, positive_examples):
        """Dummy implementation for testing"""
        return []
        
    def _unify_atoms(self, atom1, atom2, substitution):
        """Simplified unification for testing"""
        return atom1.predicate == atom2.predicate
        
    def _entails_example(self, hypothesis, example):
        """Simplified entailment for testing"""
        return hypothesis.head.predicate == example.atom.predicate


def test_mixin_integration():
    """Test SemanticEvaluationMixin integration"""
    print("\n🏗️ Testing Mixin Integration")
    print("=" * 50)
    
    hypothesis, pos_examples, neg_examples = create_test_data()
    
    # Test each semantic setting
    for setting in ['normal', 'definite', 'nonmonotonic']:
        print(f"\n⚙️ Testing {setting} semantics integration:")
        
        ilp_system = TestSemanticILP(semantic_setting=setting)
        
        # Test hypothesis evaluation
        is_valid = ilp_system._evaluate_hypothesis_semantic(
            hypothesis, pos_examples, neg_examples
        )
        
        # Test semantic scoring
        score = ilp_system._calculate_semantic_score(
            hypothesis, pos_examples, neg_examples
        )
        
        # Test refinement methods
        specializations = ilp_system._specialize_clause_semantic(
            hypothesis, pos_examples, neg_examples
        )
        
        generalizations = ilp_system._generalize_clause_semantic(
            hypothesis, pos_examples, neg_examples
        )
        
        print(f"   Hypothesis Valid: {is_valid}")
        print(f"   Semantic Score: {score:.3f}")
        print(f"   Specializations: {len(specializations)}")
        print(f"   Generalizations: {len(generalizations)}")


def test_complex_hypothesis():
    """Test with a more complex hypothesis"""
    print("\n🧮 Testing Complex Hypothesis")
    print("=" * 50)
    
    # Create more complex hypothesis: ancestor(X, Z) :- parent(X, Y), ancestor(Y, Z)
    complex_hypothesis = LogicalClause(
        head=LogicalAtom("ancestor", [
            LogicalTerm("X", "variable"),
            LogicalTerm("Z", "variable")
        ]),
        body=[
            LogicalAtom("parent", [
                LogicalTerm("X", "variable"),
                LogicalTerm("Y", "variable")
            ]),
            LogicalAtom("ancestor", [
                LogicalTerm("Y", "variable"),
                LogicalTerm("Z", "variable")
            ])
        ]
    )
    
    # Create examples for ancestor relation
    ancestor_pos = [
        Example(LogicalAtom("ancestor", [
            LogicalTerm("john", "constant"),
            LogicalTerm("alice", "constant")
        ]), is_positive=True)
    ]
    
    ancestor_neg = [
        Example(LogicalAtom("ancestor", [
            LogicalTerm("alice", "constant"),
            LogicalTerm("john", "constant")
        ]), is_positive=False)
    ]
    
    print(f"Complex Hypothesis: {complex_hypothesis}")
    
    # Compare across semantic settings
    comparison = compare_semantic_settings(
        complex_hypothesis, ancestor_pos, ancestor_neg
    )
    
    for setting, results in comparison.items():
        print(f"{setting:>12}: Valid={results['semantic_valid']:>5}, "
              f"Score={results['semantic_score']:>5.2f}")


def main():
    """Run all tests"""
    print("🧪 Semantic Evaluation Module Test Suite")
    print("=" * 60)
    print("Testing the extracted semantic evaluation functionality")
    print("from Muggleton & De Raedt's ILP framework")
    
    try:
        test_standalone_evaluation()
        test_comparison()
        test_mixin_integration()
        test_complex_hypothesis()
        
        print("\n✅ All tests completed successfully!")
        print("\n💡 Key Insights:")
        print("   • Normal semantics focuses on consistency")
        print("   • Definite semantics emphasizes model correctness")
        print("   • Nonmonotonic semantics prioritizes minimality")
        print("   • Different semantics can yield different evaluations")
        print("   • Semantic constraints improve rule quality")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        raise


if __name__ == "__main__":
    main()