#!/usr/bin/env python3
"""
Coverage Analysis Module Demonstration
=====================================

This script demonstrates the comprehensive coverage analysis capabilities
extracted from the main ILP system and organized into a dedicated mixin class.
"""

import sys
import os

# Add the package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'inductive_logic_programming'))

from ilp_modules.coverage_analysis import CoverageAnalysisMixin, CoverageMetrics, CoverageAnalysisReport
from ilp_modules.logical_structures import LogicalTerm, LogicalAtom, LogicalClause, Example


class SimpleCoverageAnalyzer(CoverageAnalysisMixin):
    """Simple demonstration class using the coverage analysis mixin"""
    
    def __init__(self):
        # Initialize with configuration parameters
        self.coverage_strategy = 'standard'
        self.statistical_confidence = 0.95
        self.min_coverage_threshold = 0.1
        self.noise_tolerance = 0.1
        self.max_clause_length = 5
        self.max_variables = 4
        
        # Initialize the mixin
        super().__init__()
    
    def _covers_example(self, clause, example_atom):
        """Simple coverage check for demonstration"""
        # Basic predicate matching for demo purposes
        return (clause.head.predicate == example_atom.predicate and
                len(clause.head.terms) == len(example_atom.terms))


def create_sample_data():
    """Create sample logical clauses and examples for testing"""
    
    # Sample rule: father(X,Y) :- parent(X,Y), male(X)
    head = LogicalAtom('father', [
        LogicalTerm('X', 'variable'), 
        LogicalTerm('Y', 'variable')
    ])
    body = [
        LogicalAtom('parent', [LogicalTerm('X', 'variable'), LogicalTerm('Y', 'variable')]),
        LogicalAtom('male', [LogicalTerm('X', 'variable')])
    ]
    father_rule = LogicalClause(head=head, body=body)
    
    # Positive examples
    positive_examples = [
        Example(LogicalAtom('father', [LogicalTerm('john', 'constant'), LogicalTerm('mary', 'constant')]), True),
        Example(LogicalAtom('father', [LogicalTerm('bob', 'constant'), LogicalTerm('alice', 'constant')]), True),
        Example(LogicalAtom('father', [LogicalTerm('tom', 'constant'), LogicalTerm('ann', 'constant')]), True),
    ]
    
    # Negative examples
    negative_examples = [
        Example(LogicalAtom('father', [LogicalTerm('mary', 'constant'), LogicalTerm('john', 'constant')]), False),
        Example(LogicalAtom('father', [LogicalTerm('alice', 'constant'), LogicalTerm('bob', 'constant')]), False),
    ]
    
    return father_rule, positive_examples, negative_examples


def main():
    """Demonstrate coverage analysis capabilities"""
    
    print("🧠 Coverage Analysis Module Demonstration")
    print("=" * 50)
    
    # Create analyzer and sample data
    analyzer = SimpleCoverageAnalyzer()
    rule, pos_examples, neg_examples = create_sample_data()
    
    print(f"\n📝 Sample Rule: {rule}")
    print(f"📊 Examples: {len(pos_examples)} positive, {len(neg_examples)} negative")
    
    # Calculate comprehensive metrics
    print(f"\n🔍 Calculating coverage metrics...")
    metrics = analyzer.calculate_comprehensive_metrics(rule, pos_examples, neg_examples)
    
    print(f"\n📈 Coverage Metrics:")
    print(f"   • Precision: {metrics.precision:.3f}")
    print(f"   • Recall: {metrics.recall:.3f}")
    print(f"   • F1-Score: {metrics.f1_score:.3f}")
    print(f"   • Accuracy: {metrics.accuracy:.3f}")
    print(f"   • Quality Score: {metrics.quality_score:.3f}")
    print(f"   • Interpretability: {metrics.interpretability:.3f}")
    
    print(f"\n📋 Confusion Matrix:")
    print(f"   • True Positives: {metrics.true_positives}")
    print(f"   • False Positives: {metrics.false_positives}")
    print(f"   • True Negatives: {metrics.true_negatives}")
    print(f"   • False Negatives: {metrics.false_negatives}")
    
    print(f"\n🔬 Statistical Analysis:")
    print(f"   • Chi-square: {metrics.chi_square:.3f}")
    print(f"   • P-value: {metrics.p_value:.4f}")
    print(f"   • Significance: {metrics.significance_level}")
    print(f"   • Odds Ratio: {metrics.odds_ratio:.3f}")
    print(f"   • 95% CI: ({metrics.confidence_interval[0]:.3f}, {metrics.confidence_interval[1]:.3f})")
    
    # Generate comprehensive report
    print(f"\n📊 Generating comprehensive analysis report...")
    report = analyzer.generate_coverage_analysis_report(rule, pos_examples, neg_examples)
    
    # Print detailed report
    analyzer.print_coverage_analysis_summary(report)
    
    # Test different coverage strategies
    print(f"\n🔧 Testing Different Coverage Strategies:")
    strategies = ['standard', 'weighted', 'probabilistic', 'fuzzy']
    
    for strategy in strategies:
        analyzer.coverage_strategy = strategy
        coverage = analyzer._calculate_coverage(rule, pos_examples)
        print(f"   • {strategy.capitalize()}: {coverage} examples covered")
    
    # Print statistics
    analyzer.print_coverage_statistics()
    
    # Test rule comparison
    print(f"\n⚖️  Rule Comparison:")
    
    # Create a second rule for comparison
    head2 = LogicalAtom('father', [LogicalTerm('X', 'variable'), LogicalTerm('Y', 'variable')])
    simple_rule = LogicalClause(head=head2, body=[])
    
    comparison = analyzer.compare_rule_coverage([rule, simple_rule], pos_examples, neg_examples)
    
    print(f"   • Best rule: {comparison['best_rule']['rule'] if comparison['best_rule'] else 'None'}")
    print(f"   • Average F1-score: {comparison['average_metrics']['f1_score']:.3f}")
    
    print(f"\n✨ Key Features Demonstrated:")
    print(f"   • Comprehensive coverage metrics calculation")
    print(f"   • Statistical significance testing") 
    print(f"   • Multiple coverage strategies")
    print(f"   • Detailed analysis reporting")
    print(f"   • Rule comparison capabilities")
    print(f"   • Interpretability assessment")
    
    print(f"\n🎯 Coverage Analysis Module Successfully Extracted!")
    print(f"   Ready for integration into ILP systems for comprehensive rule evaluation.")


if __name__ == "__main__":
    main()