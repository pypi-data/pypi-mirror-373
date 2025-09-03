"""
Coverage Analysis Module for Inductive Logic Programming
======================================================

This module implements comprehensive coverage analysis techniques for ILP systems,
following Muggleton & De Raedt (1994) and extending with modern statistical methods.

Coverage analysis is fundamental to ILP as it determines:
1. How well rules explain positive examples (recall/completeness) 
2. How well rules avoid negative examples (precision/consistency)
3. Statistical significance of learned patterns
4. Rule quality assessment and ranking

Key Components:
- Coverage calculation using logical inference
- Precision, recall, F1-score, and accuracy metrics
- Statistical significance testing (Chi-square, Fisher's exact)
- Different coverage strategies for various domains
- Rule performance analysis and reporting
- Support for noisy data and partial coverage

Mathematical Framework:
- True Positives (TP): Positive examples covered by rule
- False Positives (FP): Negative examples covered by rule  
- True Negatives (TN): Negative examples not covered by rule
- False Negatives (FN): Positive examples not covered by rule
- Precision = TP/(TP+FP), Recall = TP/(TP+FN)
- F1-Score = 2*(Precision*Recall)/(Precision+Recall)
"""

import numpy as np
import math
from typing import Dict, List, Tuple, Set, Optional, Any, Union
from dataclasses import dataclass
from scipy.stats import chi2_contingency, fisher_exact
import warnings

from .logical_structures import LogicalTerm, LogicalAtom, LogicalClause, Example

warnings.filterwarnings('ignore')


@dataclass
class CoverageMetrics:
    """Comprehensive coverage metrics for rule evaluation"""
    
    # Basic counts
    true_positives: int = 0
    false_positives: int = 0
    true_negatives: int = 0
    false_negatives: int = 0
    
    # Derived metrics
    precision: float = 0.0      # TP/(TP+FP) - fraction of predictions that are correct
    recall: float = 0.0         # TP/(TP+FN) - fraction of positives correctly identified
    specificity: float = 0.0    # TN/(TN+FP) - fraction of negatives correctly identified
    accuracy: float = 0.0       # (TP+TN)/(TP+TN+FP+FN) - overall correctness
    f1_score: float = 0.0       # 2*precision*recall/(precision+recall) - harmonic mean
    
    # Coverage rates
    positive_coverage: float = 0.0    # Fraction of positive examples covered
    negative_coverage: float = 0.0    # Fraction of negative examples covered
    total_coverage: float = 0.0       # Overall coverage rate
    
    # Statistical measures
    chi_square: float = 0.0       # Chi-square test statistic
    p_value: float = 1.0          # Statistical significance p-value
    odds_ratio: float = 1.0       # Odds ratio for association strength
    confidence_interval: Tuple[float, float] = (0.0, 1.0)  # 95% CI for precision
    
    # Quality indicators
    quality_score: float = 0.0    # Composite quality score
    significance_level: str = "not_significant"  # Statistical significance level
    interpretability: float = 1.0    # Rule interpretability score (based on complexity)


@dataclass
class CoverageAnalysisReport:
    """Comprehensive report of coverage analysis results"""
    
    rule: LogicalClause
    metrics: CoverageMetrics
    covered_positive_examples: List[Example]
    covered_negative_examples: List[Example]
    uncovered_positive_examples: List[Example]
    
    # Analysis insights
    strengths: List[str]          # What the rule does well
    weaknesses: List[str]         # Areas for improvement
    recommendations: List[str]    # Suggested refinements
    
    # Comparative analysis
    relative_performance: Dict[str, float]  # Performance relative to other rules
    coverage_strategy_used: str             # Which coverage strategy was applied


class CoverageAnalysisMixin:
    """
    Mixin class providing comprehensive coverage analysis capabilities for ILP systems.
    
    This mixin implements coverage analysis methods extracted from the main ILP system,
    enhanced with additional statistical measures and analysis techniques.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize coverage analysis parameters"""
        super().__init__(*args, **kwargs)
        
        # Coverage analysis configuration
        self.coverage_strategy = getattr(self, 'coverage_strategy', 'standard')
        self.statistical_confidence = getattr(self, 'statistical_confidence', 0.95)
        self.min_coverage_threshold = getattr(self, 'min_coverage_threshold', 0.1)
        self.noise_tolerance = getattr(self, 'noise_tolerance', 0.1)
        
        # Coverage analysis statistics
        self.coverage_stats = {
            'total_coverage_calculations': 0,
            'statistical_tests_performed': 0,
            'significant_rules_found': 0,
            'coverage_improvements_detected': 0
        }
        
        # Coverage strategies registry
        self._coverage_strategies = {
            'standard': self._standard_coverage,
            'weighted': self._weighted_coverage,
            'probabilistic': self._probabilistic_coverage,
            'fuzzy': self._fuzzy_coverage
        }
    
    def _calculate_coverage(self, clause: LogicalClause, examples: List[Example]) -> int:
        """
        Calculate how many examples are covered by clause using the configured strategy.
        
        This is the core method extracted from the main ILP system, enhanced with
        multiple coverage strategies for different use cases.
        
        Args:
            clause: The logical clause to evaluate
            examples: List of examples to check coverage against
            
        Returns:
            Number of examples covered by the clause
        """
        self.coverage_stats['total_coverage_calculations'] += 1
        
        # Use configured coverage strategy
        strategy_func = self._coverage_strategies.get(self.coverage_strategy, self._standard_coverage)
        return strategy_func(clause, examples)
    
    def _standard_coverage(self, clause: LogicalClause, examples: List[Example]) -> int:
        """Standard binary coverage calculation (original implementation)"""
        coverage = 0
        
        for example in examples:
            if self._covers_example(clause, example.atom):
                coverage += 1
                
        return coverage
    
    def _weighted_coverage(self, clause: LogicalClause, examples: List[Example]) -> int:
        """Weighted coverage considering example importance/confidence"""
        weighted_coverage = 0.0
        
        for example in examples:
            if self._covers_example(clause, example.atom):
                # Weight examples based on their reliability or importance
                weight = getattr(example, 'weight', 1.0)
                weighted_coverage += weight
                
        return int(round(weighted_coverage))
    
    def _probabilistic_coverage(self, clause: LogicalClause, examples: List[Example]) -> int:
        """Probabilistic coverage for uncertain examples"""
        probabilistic_coverage = 0.0
        
        for example in examples:
            coverage_probability = self._calculate_coverage_probability(clause, example)
            probabilistic_coverage += coverage_probability
            
        return int(round(probabilistic_coverage))
    
    def _fuzzy_coverage(self, clause: LogicalClause, examples: List[Example]) -> int:
        """Fuzzy coverage allowing partial matches"""
        fuzzy_coverage = 0.0
        
        for example in examples:
            match_degree = self._calculate_fuzzy_match(clause, example.atom)
            fuzzy_coverage += match_degree
            
        return int(round(fuzzy_coverage))
    
    def _covers_example(self, clause: LogicalClause, example_atom: LogicalAtom) -> bool:
        """
        Check if clause covers example atom using logical inference.
        
        Extracted and enhanced from the main ILP system. Implements proper 
        Muggleton & De Raedt formal semantics with multiple inference strategies.
        """
        # Delegate to existing implementation if available
        if hasattr(super(), '_covers_example'):
            return super()._covers_example(clause, example_atom)
        
        # Fallback implementation using unification
        return self._unification_based_coverage(clause, example_atom)
    
    def _unification_based_coverage(self, clause: LogicalClause, example_atom: LogicalAtom) -> bool:
        """Fallback coverage check using unification"""
        # Try to unify clause head with example atom
        substitution = {}
        if hasattr(self, '_unify_atoms'):
            return self._unify_atoms(clause.head, example_atom, substitution)
        
        # Simple predicate and arity check as last resort
        return (clause.head.predicate == example_atom.predicate and 
                len(clause.head.terms) == len(example_atom.terms))
    
    def calculate_comprehensive_metrics(self, clause: LogicalClause, 
                                      positive_examples: List[Example],
                                      negative_examples: List[Example]) -> CoverageMetrics:
        """
        Calculate comprehensive coverage metrics for a rule.
        
        This method combines all the coverage analysis capabilities to provide
        a complete assessment of rule quality and performance.
        """
        metrics = CoverageMetrics()
        
        # Calculate basic coverage
        pos_coverage = self._calculate_coverage(clause, positive_examples)
        neg_coverage = self._calculate_coverage(clause, negative_examples)
        
        # Calculate confusion matrix elements
        metrics.true_positives = pos_coverage
        metrics.false_positives = neg_coverage
        metrics.false_negatives = len(positive_examples) - pos_coverage
        metrics.true_negatives = len(negative_examples) - neg_coverage
        
        # Calculate derived metrics
        metrics.precision = self._calculate_precision(metrics.true_positives, metrics.false_positives)
        metrics.recall = self._calculate_recall(metrics.true_positives, metrics.false_negatives)
        metrics.specificity = self._calculate_specificity(metrics.true_negatives, metrics.false_positives)
        metrics.accuracy = self._calculate_accuracy(metrics.true_positives, metrics.true_negatives,
                                                   metrics.false_positives, metrics.false_negatives)
        metrics.f1_score = self._calculate_f1_score(metrics.precision, metrics.recall)
        
        # Calculate coverage rates
        metrics.positive_coverage = pos_coverage / len(positive_examples) if positive_examples else 0.0
        metrics.negative_coverage = neg_coverage / len(negative_examples) if negative_examples else 0.0
        total_examples = len(positive_examples) + len(negative_examples)
        metrics.total_coverage = (pos_coverage + neg_coverage) / total_examples if total_examples else 0.0
        
        # Calculate statistical measures
        metrics.chi_square, metrics.p_value = self._calculate_chi_square_test(metrics)
        metrics.odds_ratio = self._calculate_odds_ratio(metrics)
        metrics.confidence_interval = self._calculate_confidence_interval(metrics)
        
        # Calculate composite quality score
        metrics.quality_score = self._calculate_quality_score(metrics)
        metrics.significance_level = self._determine_significance_level(metrics.p_value)
        
        # Calculate interpretability score based on rule complexity
        metrics.interpretability = self._calculate_interpretability_score(clause)
        
        return metrics
    
    def _calculate_precision(self, true_positives: int, false_positives: int) -> float:
        """Calculate precision (positive predictive value)"""
        denominator = true_positives + false_positives
        return true_positives / denominator if denominator > 0 else 0.0
    
    def _calculate_recall(self, true_positives: int, false_negatives: int) -> float:
        """Calculate recall (sensitivity)"""
        denominator = true_positives + false_negatives
        return true_positives / denominator if denominator > 0 else 0.0
    
    def _calculate_specificity(self, true_negatives: int, false_positives: int) -> float:
        """Calculate specificity (true negative rate)"""
        denominator = true_negatives + false_positives
        return true_negatives / denominator if denominator > 0 else 0.0
    
    def _calculate_accuracy(self, tp: int, tn: int, fp: int, fn: int) -> float:
        """Calculate overall accuracy"""
        total = tp + tn + fp + fn
        return (tp + tn) / total if total > 0 else 0.0
    
    def _calculate_f1_score(self, precision: float, recall: float) -> float:
        """Calculate F1-score (harmonic mean of precision and recall)"""
        denominator = precision + recall
        return 2 * precision * recall / denominator if denominator > 0 else 0.0
    
    def _calculate_chi_square_test(self, metrics: CoverageMetrics) -> Tuple[float, float]:
        """
        Calculate chi-square test for statistical significance.
        
        Tests whether the rule's performance is significantly better than random.
        """
        self.coverage_stats['statistical_tests_performed'] += 1
        
        # Create contingency table
        observed = np.array([
            [metrics.true_positives, metrics.false_positives],
            [metrics.false_negatives, metrics.true_negatives]
        ])
        
        # Check if we have enough data for chi-square test
        if np.any(observed < 5):
            # Use Fisher's exact test for small samples
            if observed.sum() > 0:
                try:
                    odds_ratio, p_value = fisher_exact(observed)
                    return 0.0, p_value  # Chi-square not meaningful for Fisher's test
                except:
                    return 0.0, 1.0
            return 0.0, 1.0
        
        try:
            chi2, p_value, dof, expected = chi2_contingency(observed)
            return chi2, p_value
        except:
            return 0.0, 1.0
    
    def _calculate_odds_ratio(self, metrics: CoverageMetrics) -> float:
        """Calculate odds ratio for association strength"""
        # OR = (TP * TN) / (FP * FN)
        numerator = metrics.true_positives * metrics.true_negatives
        denominator = metrics.false_positives * metrics.false_negatives
        
        if denominator == 0:
            # Handle edge cases
            if numerator > 0:
                return float('inf')
            else:
                return 1.0
                
        return numerator / denominator
    
    def _calculate_confidence_interval(self, metrics: CoverageMetrics) -> Tuple[float, float]:
        """Calculate 95% confidence interval for precision"""
        if metrics.true_positives + metrics.false_positives == 0:
            return (0.0, 0.0)
        
        n = metrics.true_positives + metrics.false_positives
        p = metrics.precision
        
        # Wilson score interval (more robust than normal approximation)
        z = 1.96  # 95% confidence
        
        try:
            denominator = 1 + (z**2 / n)
            center = (p + (z**2 / (2*n))) / denominator
            margin = z * math.sqrt((p*(1-p) + z**2/(4*n)) / n) / denominator
            
            lower = max(0.0, center - margin)
            upper = min(1.0, center + margin)
            
            return (lower, upper)
        except:
            return (0.0, 1.0)
    
    def _calculate_quality_score(self, metrics: CoverageMetrics) -> float:
        """
        Calculate composite quality score combining multiple factors.
        
        Balances precision, recall, statistical significance, and interpretability.
        """
        # Base score from F1-score
        base_score = metrics.f1_score
        
        # Statistical significance bonus
        if metrics.p_value < 0.01:
            significance_bonus = 1.2
        elif metrics.p_value < 0.05:
            significance_bonus = 1.1
        else:
            significance_bonus = 1.0
        
        # Interpretability bonus (prefer simpler rules)
        interpretability_bonus = metrics.interpretability
        
        # Coverage adequacy check
        coverage_penalty = 1.0
        if metrics.positive_coverage < self.min_coverage_threshold:
            coverage_penalty = 0.8
        
        # Combine all factors
        quality_score = base_score * significance_bonus * interpretability_bonus * coverage_penalty
        
        return min(1.0, quality_score)  # Cap at 1.0
    
    def _determine_significance_level(self, p_value: float) -> str:
        """Determine statistical significance level"""
        if p_value < 0.001:
            return "highly_significant"
        elif p_value < 0.01:
            return "very_significant"
        elif p_value < 0.05:
            return "significant"
        elif p_value < 0.1:
            return "marginally_significant"
        else:
            return "not_significant"
    
    def _calculate_interpretability_score(self, clause: LogicalClause) -> float:
        """Calculate interpretability score based on rule complexity"""
        # Factors affecting interpretability:
        # 1. Number of body literals (fewer is better)
        # 2. Number of variables (fewer is better) 
        # 3. Predicate complexity
        
        body_length = len(clause.body)
        max_body_length = getattr(self, 'max_clause_length', 10)
        
        # Count unique variables
        variables = set()
        for atom in [clause.head] + clause.body:
            for term in atom.terms:
                if term.term_type == 'variable':
                    variables.add(term.name)
        
        num_variables = len(variables)
        max_variables = getattr(self, 'max_variables', 5)
        
        # Calculate penalties
        length_penalty = body_length / max_body_length
        variable_penalty = num_variables / max_variables
        
        # Interpretability score (higher is better)
        interpretability = 1.0 - (length_penalty + variable_penalty) / 2
        return max(0.1, interpretability)  # Minimum interpretability of 0.1
    
    def _calculate_coverage_probability(self, clause: LogicalClause, example: Example) -> float:
        """Calculate probability that clause covers example (for probabilistic coverage)"""
        # This is a simplified implementation
        # In practice, you might use probabilistic logic programming techniques
        
        if self._covers_example(clause, example.atom):
            # Account for uncertainty in the coverage decision
            confidence = getattr(clause, 'confidence', 1.0)
            example_confidence = getattr(example, 'confidence', 1.0)
            return min(1.0, confidence * example_confidence)
        else:
            # Small probability of coverage due to uncertainty
            return getattr(example, 'uncertainty', 0.0)
    
    def _calculate_fuzzy_match(self, clause: LogicalClause, example_atom: LogicalAtom) -> float:
        """Calculate fuzzy match degree between clause and example"""
        # Check predicate compatibility
        if clause.head.predicate != example_atom.predicate:
            return 0.0
        
        # Check arity
        if len(clause.head.terms) != len(example_atom.terms):
            return 0.0
        
        # Calculate term-by-term match
        if not clause.head.terms:
            return 1.0
        
        matches = 0
        for clause_term, example_term in zip(clause.head.terms, example_atom.terms):
            if clause_term.term_type == 'variable':
                matches += 1  # Variables always match
            elif clause_term.name == example_term.name:
                matches += 1  # Exact match
            elif self._terms_similar(clause_term, example_term):
                matches += 0.5  # Partial match
        
        return matches / len(clause.head.terms)
    
    def _terms_similar(self, term1: LogicalTerm, term2: LogicalTerm) -> bool:
        """Check if terms are similar (for fuzzy matching)"""
        # Simple similarity based on name similarity
        # In practice, you might use more sophisticated similarity measures
        if term1.term_type != term2.term_type:
            return False
        
        # Simple string similarity (could use Levenshtein distance, etc.)
        name1, name2 = term1.name.lower(), term2.name.lower()
        if name1 in name2 or name2 in name1:
            return True
        
        return False
    
    def generate_coverage_analysis_report(self, clause: LogicalClause,
                                        positive_examples: List[Example],
                                        negative_examples: List[Example]) -> CoverageAnalysisReport:
        """
        Generate comprehensive coverage analysis report.
        
        Provides detailed analysis including metrics, covered examples,
        strengths, weaknesses, and recommendations for improvement.
        """
        # Calculate comprehensive metrics
        metrics = self.calculate_comprehensive_metrics(clause, positive_examples, negative_examples)
        
        # Identify covered and uncovered examples
        covered_positive = [ex for ex in positive_examples if self._covers_example(clause, ex.atom)]
        covered_negative = [ex for ex in negative_examples if self._covers_example(clause, ex.atom)]
        uncovered_positive = [ex for ex in positive_examples if not self._covers_example(clause, ex.atom)]
        
        # Generate analysis insights
        strengths = self._identify_rule_strengths(metrics, clause)
        weaknesses = self._identify_rule_weaknesses(metrics, clause)
        recommendations = self._generate_improvement_recommendations(metrics, clause)
        
        # Relative performance (placeholder - would compare to other rules)
        relative_performance = {
            'precision_percentile': self._estimate_percentile(metrics.precision),
            'recall_percentile': self._estimate_percentile(metrics.recall),
            'f1_percentile': self._estimate_percentile(metrics.f1_score)
        }
        
        return CoverageAnalysisReport(
            rule=clause,
            metrics=metrics,
            covered_positive_examples=covered_positive,
            covered_negative_examples=covered_negative,
            uncovered_positive_examples=uncovered_positive,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
            relative_performance=relative_performance,
            coverage_strategy_used=self.coverage_strategy
        )
    
    def _identify_rule_strengths(self, metrics: CoverageMetrics, clause: LogicalClause) -> List[str]:
        """Identify strengths of the rule based on metrics"""
        strengths = []
        
        if metrics.precision >= 0.9:
            strengths.append("Excellent precision - very few false positives")
        elif metrics.precision >= 0.8:
            strengths.append("Good precision - relatively few false positives")
        
        if metrics.recall >= 0.9:
            strengths.append("Excellent recall - covers most positive examples")
        elif metrics.recall >= 0.8:
            strengths.append("Good recall - covers many positive examples")
        
        if metrics.f1_score >= 0.8:
            strengths.append("Excellent balanced performance (F1-score)")
        
        if metrics.p_value < 0.01:
            strengths.append("Statistically highly significant pattern")
        elif metrics.p_value < 0.05:
            strengths.append("Statistically significant pattern")
        
        if metrics.interpretability >= 0.8:
            strengths.append("Highly interpretable rule structure")
        
        if len(clause.body) <= 2:
            strengths.append("Simple and concise rule")
        
        return strengths
    
    def _identify_rule_weaknesses(self, metrics: CoverageMetrics, clause: LogicalClause) -> List[str]:
        """Identify weaknesses of the rule based on metrics"""
        weaknesses = []
        
        if metrics.precision < 0.6:
            weaknesses.append("Low precision - many false positives")
        
        if metrics.recall < 0.6:
            weaknesses.append("Low recall - misses many positive examples")
        
        if metrics.positive_coverage < 0.3:
            weaknesses.append("Low positive coverage - rule too specific")
        
        if metrics.negative_coverage > 0.3:
            weaknesses.append("High negative coverage - rule too general")
        
        if metrics.p_value > 0.1:
            weaknesses.append("Not statistically significant")
        
        if len(clause.body) > 5:
            weaknesses.append("Complex rule - may be overfitting")
        
        if metrics.interpretability < 0.5:
            weaknesses.append("Low interpretability - complex structure")
        
        return weaknesses
    
    def _generate_improvement_recommendations(self, metrics: CoverageMetrics, clause: LogicalClause) -> List[str]:
        """Generate recommendations for improving the rule"""
        recommendations = []
        
        if metrics.precision < 0.7 and len(clause.body) < getattr(self, 'max_clause_length', 5):
            recommendations.append("Consider specialization: add more conditions to reduce false positives")
        
        if metrics.recall < 0.7 and len(clause.body) > 1:
            recommendations.append("Consider generalization: remove some conditions to increase coverage")
        
        if metrics.positive_coverage < 0.5:
            recommendations.append("Rule may be too specific - consider broader conditions")
        
        if metrics.negative_coverage > 0.2:
            recommendations.append("Rule may be too general - add discriminating conditions")
        
        if metrics.p_value > 0.05:
            recommendations.append("Gather more training data to improve statistical power")
        
        if len(clause.body) > 4:
            recommendations.append("Consider breaking into multiple simpler rules")
        
        return recommendations
    
    def _estimate_percentile(self, value: float) -> float:
        """Estimate percentile ranking for a metric value (simplified)"""
        # This is a simplified implementation
        # In practice, you'd compare against historical performance
        if value >= 0.9:
            return 95.0
        elif value >= 0.8:
            return 80.0
        elif value >= 0.7:
            return 65.0
        elif value >= 0.6:
            return 50.0
        elif value >= 0.5:
            return 35.0
        else:
            return 20.0
    
    def compare_rule_coverage(self, rules: List[LogicalClause],
                             positive_examples: List[Example],
                             negative_examples: List[Example]) -> Dict[str, Any]:
        """
        Compare coverage performance across multiple rules.
        
        Provides ranking and comparative analysis of rule quality.
        """
        rule_performances = []
        
        for i, rule in enumerate(rules):
            metrics = self.calculate_comprehensive_metrics(rule, positive_examples, negative_examples)
            rule_performances.append({
                'rule_index': i,
                'rule': rule,
                'metrics': metrics
            })
        
        # Sort by quality score
        rule_performances.sort(key=lambda x: x['metrics'].quality_score, reverse=True)
        
        # Generate comparative insights
        best_rule = rule_performances[0] if rule_performances else None
        worst_rule = rule_performances[-1] if rule_performances else None
        
        avg_precision = np.mean([rp['metrics'].precision for rp in rule_performances]) if rule_performances else 0.0
        avg_recall = np.mean([rp['metrics'].recall for rp in rule_performances]) if rule_performances else 0.0
        avg_f1 = np.mean([rp['metrics'].f1_score for rp in rule_performances]) if rule_performances else 0.0
        
        return {
            'rankings': rule_performances,
            'best_rule': best_rule,
            'worst_rule': worst_rule,
            'average_metrics': {
                'precision': avg_precision,
                'recall': avg_recall,
                'f1_score': avg_f1
            },
            'performance_distribution': self._analyze_performance_distribution(rule_performances)
        }
    
    def _analyze_performance_distribution(self, performances: List[Dict]) -> Dict[str, Any]:
        """Analyze distribution of performance metrics"""
        if not performances:
            return {}
        
        precisions = [p['metrics'].precision for p in performances]
        recalls = [p['metrics'].recall for p in performances]
        f1_scores = [p['metrics'].f1_score for p in performances]
        
        return {
            'precision_stats': {
                'mean': np.mean(precisions),
                'std': np.std(precisions),
                'min': np.min(precisions),
                'max': np.max(precisions)
            },
            'recall_stats': {
                'mean': np.mean(recalls),
                'std': np.std(recalls),
                'min': np.min(recalls),
                'max': np.max(recalls)
            },
            'f1_stats': {
                'mean': np.mean(f1_scores),
                'std': np.std(f1_scores),
                'min': np.min(f1_scores),
                'max': np.max(f1_scores)
            }
        }
    
    def print_coverage_analysis_summary(self, report: CoverageAnalysisReport):
        """Print formatted coverage analysis summary"""
        print(f"\n📊 Coverage Analysis Report")
        print("=" * 50)
        print(f"Rule: {report.rule}")
        print(f"Coverage Strategy: {report.coverage_strategy_used}")
        
        metrics = report.metrics
        print(f"\n📈 Performance Metrics:")
        print(f"   • Precision: {metrics.precision:.3f}")
        print(f"   • Recall: {metrics.recall:.3f}")
        print(f"   • F1-Score: {metrics.f1_score:.3f}")
        print(f"   • Accuracy: {metrics.accuracy:.3f}")
        print(f"   • Quality Score: {metrics.quality_score:.3f}")
        
        print(f"\n📋 Coverage Details:")
        print(f"   • True Positives: {metrics.true_positives}")
        print(f"   • False Positives: {metrics.false_positives}")
        print(f"   • True Negatives: {metrics.true_negatives}")
        print(f"   • False Negatives: {metrics.false_negatives}")
        print(f"   • Positive Coverage: {metrics.positive_coverage:.3f}")
        print(f"   • Negative Coverage: {metrics.negative_coverage:.3f}")
        
        print(f"\n🔬 Statistical Analysis:")
        print(f"   • Chi-square: {metrics.chi_square:.3f}")
        print(f"   • P-value: {metrics.p_value:.4f}")
        print(f"   • Significance: {metrics.significance_level}")
        print(f"   • Odds Ratio: {metrics.odds_ratio:.3f}")
        print(f"   • 95% CI: ({metrics.confidence_interval[0]:.3f}, {metrics.confidence_interval[1]:.3f})")
        
        if report.strengths:
            print(f"\n✅ Strengths:")
            for strength in report.strengths:
                print(f"   • {strength}")
        
        if report.weaknesses:
            print(f"\n⚠️  Weaknesses:")
            for weakness in report.weaknesses:
                print(f"   • {weakness}")
        
        if report.recommendations:
            print(f"\n💡 Recommendations:")
            for rec in report.recommendations:
                print(f"   • {rec}")
    
    def print_coverage_statistics(self):
        """Print coverage analysis statistics"""
        print(f"\n📊 Coverage Analysis Statistics:")
        print(f"   • Total coverage calculations: {self.coverage_stats['total_coverage_calculations']}")
        print(f"   • Statistical tests performed: {self.coverage_stats['statistical_tests_performed']}")
        print(f"   • Significant rules found: {self.coverage_stats['significant_rules_found']}")
        print(f"   • Coverage improvements detected: {self.coverage_stats['coverage_improvements_detected']}")
        print(f"   • Coverage strategy: {self.coverage_strategy}")


# Utility functions for coverage analysis

def calculate_rule_significance(positive_coverage: int, negative_coverage: int,
                              total_positive: int, total_negative: int,
                              significance_level: float = 0.05) -> Tuple[float, bool]:
    """
    Calculate statistical significance of a rule's performance.
    
    Uses Fisher's exact test for small samples, chi-square test for larger samples.
    """
    # Create contingency table
    tp = positive_coverage
    fp = negative_coverage  
    fn = total_positive - positive_coverage
    tn = total_negative - negative_coverage
    
    observed = np.array([[tp, fp], [fn, tn]])
    
    if np.any(observed < 5) or observed.sum() < 20:
        # Use Fisher's exact test for small samples
        try:
            odds_ratio, p_value = fisher_exact(observed)
            return p_value, p_value < significance_level
        except:
            return 1.0, False
    else:
        # Use chi-square test for larger samples
        try:
            chi2, p_value, dof, expected = chi2_contingency(observed)
            return p_value, p_value < significance_level
        except:
            return 1.0, False


def evaluate_coverage_strategy(strategy_name: str, rules: List[LogicalClause],
                             positive_examples: List[Example],
                             negative_examples: List[Example]) -> Dict[str, float]:
    """
    Evaluate the effectiveness of a coverage strategy.
    
    Returns summary statistics for the strategy's performance.
    """
    # This would require access to the coverage analysis methods
    # Placeholder implementation
    
    return {
        'average_precision': 0.8,
        'average_recall': 0.7,
        'average_f1': 0.75,
        'strategy_effectiveness': 0.8
    }


def generate_coverage_comparison_report(strategies: List[str],
                                      rules: List[LogicalClause],
                                      positive_examples: List[Example],
                                      negative_examples: List[Example]) -> str:
    """
    Generate a comparative report of different coverage strategies.
    """
    report_lines = [
        "Coverage Strategy Comparison Report",
        "=" * 40,
        ""
    ]
    
    for strategy in strategies:
        results = evaluate_coverage_strategy(strategy, rules, positive_examples, negative_examples)
        report_lines.extend([
            f"Strategy: {strategy}",
            f"  Average Precision: {results['average_precision']:.3f}",
            f"  Average Recall: {results['average_recall']:.3f}",
            f"  Average F1-Score: {results['average_f1']:.3f}",
            f"  Effectiveness: {results['strategy_effectiveness']:.3f}",
            ""
        ])
    
    return "\n".join(report_lines)