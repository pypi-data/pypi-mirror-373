"""
FOIL Comprehensive Configuration System
======================================

Author: Benedict Chen (benedict@benedictchen.com)

This module provides comprehensive configuration options for ALL FIXME solutions
identified in the FOIL implementation, allowing users to pick and choose from
research-accurate alternatives.

Based on: Quinlan (1990) "Learning logical definitions from relations"
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Callable
from enum import Enum
import numpy as np


class InformationGainMethod(Enum):
    """Information gain calculation methods with research basis."""
    QUINLAN_ORIGINAL = "quinlan_original"  # Exact Quinlan (1990) formula with variable bindings
    EXAMPLE_BASED_APPROXIMATION = "example_approximation"  # Current fake implementation
    BINDING_WEIGHTED = "binding_weighted"  # Weighted by binding multiplicity
    LAPLACE_CORRECTED = "laplace_corrected"  # With Laplace smoothing
    
    
class BindingGenerationMethod(Enum):
    """Variable binding generation strategies."""
    EXHAUSTIVE_ENUMERATION = "exhaustive"  # Enumerate all possible variable instantiations
    CONSTRAINT_GUIDED = "constraint_guided"  # Use mode declarations and constraints
    SAMPLING_BASED = "sampling"  # Sample from binding space
    HYBRID_ENUMERATION = "hybrid"  # Combine exhaustive + constraint-guided


class LiteralGenerationStrategy(Enum):
    """Literal generation approaches from research."""
    MODE_DECLARATIONS = "mode_declarations"  # Quinlan's mode-based generation
    BACKGROUND_GUIDED = "background_guided"  # Use background knowledge structure
    TYPE_CONSTRAINED = "type_constrained"  # Type-based constraints
    DETERMINATE_LITERALS = "determinate"  # Focus on determinate literals


class CoverageTestingMethod(Enum):
    """Coverage testing implementations."""
    SLD_RESOLUTION = "sld_resolution"  # Proper theorem proving with SLD resolution
    UNIFICATION_BASED = "unification"  # Unification-based coverage testing  
    EXAMPLE_MATCHING = "example_matching"  # Current oversimplified method
    BACKGROUND_INTEGRATED = "background_integrated"  # Include background knowledge


class PruningStrategy(Enum):
    """Pruning and complexity control methods."""
    MDL_PRINCIPLE = "mdl"  # Minimum Description Length principle
    SIGNIFICANCE_TESTING = "significance"  # Statistical significance testing
    CROSS_VALIDATION = "cross_validation"  # Cross-validation based pruning
    CLAUSE_SUBSUMPTION = "subsumption"  # Subsumption-based redundancy removal


class NoiseHandlingApproach(Enum):
    """Noise handling strategies from Quinlan (1990)."""
    CHI_SQUARE_TEST = "chi_square"  # χ² test for literal significance
    CONFIDENCE_INTERVALS = "confidence"  # Statistical confidence measures
    LAPLACE_CORRECTION = "laplace"  # Laplace correction for probability estimates
    EXCEPTION_HANDLING = "exceptions"  # Explicit noise tolerance parameters


@dataclass
class FOILComprehensiveConfig:
    """
    MASTER CONFIGURATION for ALL FOIL FIXME solutions.
    
    Allows users to pick and choose from all research-based implementations
    identified in the comprehensive code review.
    """
    
    # ============================================================================
    # INFORMATION GAIN CALCULATION SOLUTIONS
    # ============================================================================
    
    # Method Selection
    information_gain_method: InformationGainMethod = InformationGainMethod.QUINLAN_ORIGINAL
    
    # Quinlan Original Parameters (Research-Accurate)
    use_variable_bindings: bool = True  # Use bindings instead of examples
    binding_enumeration_limit: int = 10000  # Prevent combinatorial explosion
    t_parameter_calculation: str = "positive_bindings"  # "positive_bindings", "all_bindings", "weighted"
    
    # Laplace Correction Settings
    laplace_alpha: float = 1.0  # Laplace smoothing parameter
    use_laplace_correction: bool = True  # Apply Laplace correction
    
    # Logarithmic Base and Smoothing
    logarithm_base: str = "natural"  # "natural", "base2", "base10" 
    smoothing_epsilon: float = 1e-8  # Numerical stability
    handle_zero_probabilities: bool = True  # Systematic zero handling
    
    # ============================================================================
    # VARIABLE BINDING MECHANISM SOLUTIONS
    # ============================================================================
    
    # Binding Generation Method
    binding_generation_method: BindingGenerationMethod = BindingGenerationMethod.CONSTRAINT_GUIDED
    
    # Theta-Subsumption Parameters
    enable_theta_subsumption: bool = True  # Proper generality testing
    subsumption_timeout: float = 1.0  # Seconds before timeout
    max_unification_depth: int = 50  # Prevent infinite recursion
    
    # Variable Instantiation Control
    max_variables_per_clause: int = 6  # Limit variable explosion
    variable_sharing_constraints: bool = True  # Enforce shared variables
    binding_consistency_checking: bool = True  # Check binding consistency
    
    # ============================================================================
    # LITERAL GENERATION STRATEGY SOLUTIONS
    # ============================================================================
    
    # Generation Strategy
    literal_generation_strategy: LiteralGenerationStrategy = LiteralGenerationStrategy.MODE_DECLARATIONS
    
    # Mode Declaration Support
    require_mode_declarations: bool = True  # Require explicit modes
    default_mode_for_unknown: str = "+type"  # Default mode if not specified
    
    # Mode Types (Quinlan's Original)
    input_mode_symbol: str = "+"  # Input argument (+type)
    output_mode_symbol: str = "-"  # Output argument (-type) 
    constant_mode_symbol: str = "#"  # Constant argument (#type)
    
    # Determinate Literal Detection
    detect_determinate_literals: bool = True  # Find functional dependencies
    determinate_literal_priority: float = 2.0  # Priority boost for determinate literals
    
    # Background Knowledge Integration
    use_background_structure: bool = True  # Guide generation with background
    background_relevance_threshold: float = 0.1  # Relevance threshold
    
    # ============================================================================
    # COVERAGE TESTING SOLUTIONS
    # ============================================================================
    
    # Coverage Method
    coverage_testing_method: CoverageTestingMethod = CoverageTestingMethod.SLD_RESOLUTION
    
    # SLD Resolution Parameters  
    sld_resolution_max_steps: int = 100  # Prevent infinite loops
    sld_selection_rule: str = "leftmost"  # "leftmost", "random", "heuristic"
    enable_occurs_check: bool = True  # Unification occurs check
    
    # Background Knowledge Integration
    integrate_background_knowledge: bool = True  # Use background in coverage
    background_indexing: bool = True  # Index background for efficiency
    closed_world_assumption: bool = True  # Negation as failure
    
    # ============================================================================
    # PRUNING AND COMPLEXITY CONTROL SOLUTIONS  
    # ============================================================================
    
    # Pruning Strategy
    pruning_strategy: PruningStrategy = PruningStrategy.MDL_PRINCIPLE
    
    # Minimum Description Length Parameters
    hypothesis_encoding_cost: float = 1.0  # Cost per literal in hypothesis
    data_encoding_cost: float = 1.0  # Cost per uncovered example
    mdl_optimization: bool = True  # Optimize for total encoding length
    
    # Significance Testing Parameters
    significance_level: float = 0.05  # α level for statistical tests
    chi_square_threshold: float = 3.84  # χ² threshold (α=0.05, df=1)
    min_sample_size_for_test: int = 30  # Minimum samples for valid test
    
    # Cross-Validation Settings
    cv_folds: int = 5  # Number of cross-validation folds
    cv_random_seed: int = 42  # Reproducible CV splits
    validation_metric: str = "accuracy"  # "accuracy", "f1", "precision", "recall"
    
    # Subsumption-Based Pruning
    enable_clause_subsumption: bool = True  # Remove subsumed clauses
    subsumption_check_timeout: float = 0.5  # Timeout for subsumption checks
    
    # ============================================================================
    # NOISE HANDLING SOLUTIONS
    # ============================================================================
    
    # Noise Handling Method
    noise_handling_approach: NoiseHandlingApproach = NoiseHandlingApproach.CHI_SQUARE_TEST
    
    # Statistical Validation Parameters
    perform_chi_square_tests: bool = True  # χ² test for literal significance
    confidence_interval_method: str = "bootstrap"  # "bootstrap", "normal", "t_distribution"
    confidence_level: float = 0.95  # Confidence level for intervals
    
    # Noise Tolerance Settings
    noise_tolerance_level: float = 0.1  # Accept some inconsistent examples
    handle_inconsistent_examples: bool = True  # Explicit inconsistency handling
    exception_handling_threshold: int = 5  # Max exceptions per clause
    
    # Bootstrap Confidence Intervals
    bootstrap_samples: int = 1000  # Number of bootstrap samples
    bootstrap_random_seed: int = 42  # Reproducible bootstrap
    
    # ============================================================================
    # PERFORMANCE AND DEBUGGING OPTIONS
    # ============================================================================
    
    # Performance Settings
    enable_parallel_processing: bool = False  # Parallel literal evaluation
    max_parallel_workers: int = 4  # CPU cores to use
    cache_coverage_tests: bool = True  # Cache expensive coverage computations
    
    # Debugging and Validation
    validate_against_quinlan_paper: bool = False  # Runtime validation against paper
    log_binding_generation: bool = False  # Log binding enumeration process
    log_information_gain_details: bool = False  # Detailed gain calculation logs
    trace_sld_resolution: bool = False  # Trace theorem proving steps
    
    # Output Control
    verbose_output: bool = True  # Detailed learning progress
    save_intermediate_results: bool = False  # Save clauses and statistics
    output_format: str = "human_readable"  # "human_readable", "json", "xml"


def create_research_accurate_config() -> FOILComprehensiveConfig:
    """
    Create configuration that exactly matches Quinlan (1990) FOIL paper.
    
    Returns:
        FOILComprehensiveConfig: Research-accurate configuration
    """
    return FOILComprehensiveConfig(
        # Exact Quinlan formulation
        information_gain_method=InformationGainMethod.QUINLAN_ORIGINAL,
        use_variable_bindings=True,
        logarithm_base="natural",  # Quinlan used natural log in some formulations
        
        # Proper binding mechanism
        binding_generation_method=BindingGenerationMethod.CONSTRAINT_GUIDED,
        enable_theta_subsumption=True,
        
        # Mode-based literal generation as in paper
        literal_generation_strategy=LiteralGenerationStrategy.MODE_DECLARATIONS,
        require_mode_declarations=True,
        detect_determinate_literals=True,
        
        # Proper coverage testing
        coverage_testing_method=CoverageTestingMethod.SLD_RESOLUTION,
        integrate_background_knowledge=True,
        
        # MDL-based pruning as discussed in paper
        pruning_strategy=PruningStrategy.MDL_PRINCIPLE,
        
        # Statistical significance testing as in paper
        noise_handling_approach=NoiseHandlingApproach.CHI_SQUARE_TEST,
        perform_chi_square_tests=True,
        
        # Research validation
        validate_against_quinlan_paper=True
    )


def create_performance_optimized_config() -> FOILComprehensiveConfig:
    """
    Create configuration optimized for speed over research accuracy.
    
    Returns:
        FOILComprehensiveConfig: Performance-optimized configuration  
    """
    return FOILComprehensiveConfig(
        # Use faster approximations
        information_gain_method=InformationGainMethod.EXAMPLE_BASED_APPROXIMATION,
        use_variable_bindings=False,  # Skip expensive binding enumeration
        
        # Sampling-based binding generation
        binding_generation_method=BindingGenerationMethod.SAMPLING_BASED,
        binding_enumeration_limit=1000,  # Limit search space
        
        # Simpler literal generation
        literal_generation_strategy=LiteralGenerationStrategy.BACKGROUND_GUIDED,
        require_mode_declarations=False,
        
        # Faster coverage testing
        coverage_testing_method=CoverageTestingMethod.UNIFICATION_BASED,
        sld_resolution_max_steps=20,  # Shorter timeout
        
        # Simple pruning
        pruning_strategy=PruningStrategy.SIGNIFICANCE_TESTING,
        
        # Minimal noise handling
        noise_handling_approach=NoiseHandlingApproach.LAPLACE_CORRECTION,
        
        # Performance optimizations
        enable_parallel_processing=True,
        cache_coverage_tests=True,
        verbose_output=False
    )


def create_debugging_config() -> FOILComprehensiveConfig:
    """
    Create configuration with maximum debugging and validation features.
    
    Returns:
        FOILComprehensiveConfig: Debug-focused configuration
    """
    return FOILComprehensiveConfig(
        # Research-accurate methods for validation
        information_gain_method=InformationGainMethod.QUINLAN_ORIGINAL,
        coverage_testing_method=CoverageTestingMethod.SLD_RESOLUTION,
        
        # Maximum validation
        validate_against_quinlan_paper=True,
        log_binding_generation=True,
        log_information_gain_details=True,
        trace_sld_resolution=True,
        
        # Conservative settings
        binding_enumeration_limit=5000,  # Reasonable limit for debugging
        sld_resolution_max_steps=50,
        
        # Comprehensive pruning and noise handling
        pruning_strategy=PruningStrategy.MDL_PRINCIPLE,
        noise_handling_approach=NoiseHandlingApproach.CHI_SQUARE_TEST,
        
        # Detailed output
        verbose_output=True,
        save_intermediate_results=True,
        output_format="json"  # Machine-readable for analysis
    )


def get_available_foil_solutions() -> Dict[str, List[str]]:
    """
    Get all available FOIL solution options organized by category.
    
    Returns:
        Dict[str, List[str]]: All available solution methods
    """
    return {
        "Information Gain Methods": [method.value for method in InformationGainMethod],
        "Binding Generation Methods": [method.value for method in BindingGenerationMethod],
        "Literal Generation Strategies": [strategy.value for strategy in LiteralGenerationStrategy],
        "Coverage Testing Methods": [method.value for method in CoverageTestingMethod],
        "Pruning Strategies": [strategy.value for strategy in PruningStrategy],
        "Noise Handling Approaches": [approach.value for approach in NoiseHandlingApproach],
        
        "Configuration Presets": [
            "research_accurate",
            "performance_optimized", 
            "debugging_focused"
        ],
        
        "Research Papers Implemented": [
            "Quinlan (1990) 'Learning logical definitions from relations'",
            "Muggleton & Feng (1990) 'Efficient induction of logic programs'", 
            "Cohen (1995) 'Fast effective rule induction'",
            "Lavrač & Džeroski (1994) 'Inductive Logic Programming'"
        ]
    }


def validate_foil_config(config: FOILComprehensiveConfig) -> List[str]:
    """
    Validate FOIL configuration and return warnings/issues.
    
    Args:
        config: Configuration to validate
        
    Returns:
        List[str]: Validation warnings and issues
    """
    warnings = []
    
    # Check for research accuracy vs performance trade-offs
    if not config.use_variable_bindings:
        warnings.append("⚠️  Using example-based approximation instead of Quinlan's variable bindings")
    
    if config.coverage_testing_method == CoverageTestingMethod.EXAMPLE_MATCHING:
        warnings.append("🚨 CRITICAL: Using fake coverage testing - results will be inaccurate")
    
    if config.information_gain_method == InformationGainMethod.EXAMPLE_BASED_APPROXIMATION:
        warnings.append("🚨 CRITICAL: Using fake information gain - not research accurate")
    
    # Check for parameter consistency
    if config.binding_enumeration_limit < 100:
        warnings.append("⚠️  Very low binding enumeration limit may miss important patterns")
    
    if config.significance_level <= 0 or config.significance_level >= 1:
        warnings.append("❌ Invalid significance level - must be between 0 and 1")
    
    # Check for computational feasibility
    if (config.binding_generation_method == BindingGenerationMethod.EXHAUSTIVE_ENUMERATION and 
        config.binding_enumeration_limit > 50000):
        warnings.append("⚠️  Exhaustive enumeration with high limit may be very slow")
    
    # Check research validation settings
    if (config.validate_against_quinlan_paper and 
        config.information_gain_method != InformationGainMethod.QUINLAN_ORIGINAL):
        warnings.append("💡 Consider using Quinlan original method for paper validation")
    
    return warnings


def print_foil_solutions_summary():
    """Print comprehensive summary of all implemented FOIL solutions."""
    
    print("🔧 FOIL COMPREHENSIVE SOLUTIONS SUMMARY")
    print("=" * 80)
    print()
    
    solutions = get_available_foil_solutions()
    
    for category, items in solutions.items():
        print(f"📂 {category}:")
        for item in items:
            print(f"   ✅ {item}")
        print()
    
    print("🎯 USAGE EXAMPLES:")
    print("   # Research-accurate configuration (Quinlan 1990)")
    print("   config = create_research_accurate_config()")
    print()
    print("   # Performance-optimized configuration")
    print("   config = create_performance_optimized_config()")
    print()  
    print("   # Custom configuration")
    print("   config = FOILComprehensiveConfig(")
    print("       information_gain_method=InformationGainMethod.QUINLAN_ORIGINAL,")
    print("       binding_generation_method=BindingGenerationMethod.CONSTRAINT_GUIDED,")
    print("       coverage_testing_method=CoverageTestingMethod.SLD_RESOLUTION")
    print("   )")
    print()
    print("🔍 VALIDATE YOUR CONFIG:")
    print("   warnings = validate_foil_config(config)")
    print("   if warnings:")
    print("       for warning in warnings:")
    print("           print(warning)")


if __name__ == "__main__":
    print_foil_solutions_summary()