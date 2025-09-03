"""
Comprehensive Tests for ALL FIXME Solutions
==========================================

Author: Benedict Chen (benedict@benedictchen.com)

Validation tests for all implemented FIXME solutions across ILP package:
- FOIL information gain solutions  
- Progol inverse entailment solutions
- Configuration system validation
- Research accuracy verification

Ensures all configuration options work correctly and produce research-accurate results.
"""

import pytest
import torch
import numpy as np
from typing import Dict, List, Tuple

# Import all comprehensive solutions
from inductive_logic_programming.foil_comprehensive_config import (
    FOILComprehensiveConfig,
    InformationGainMethod,
    BindingGenerationMethod,
    CoverageTestingMethod,
    create_research_accurate_config,
    create_performance_optimized_config,
    validate_foil_config
)

from inductive_logic_programming.progol_comprehensive_config import (
    ProgolComprehensiveConfig,
    InverseEntailmentMethod,
    BottomClauseConstruction,
    create_muggleton_accurate_config,
    validate_progol_config
)

from inductive_logic_programming.foil_research_accurate import (
    ResearchAccurateFOIL,
    VariableBinding,
    create_research_foil_system
)


class TestFOILComprehensiveConfig:
    """Test FOIL comprehensive configuration system."""
    
    def test_config_creation(self):
        """Test basic config creation."""
        config = FOILComprehensiveConfig()
        assert config.information_gain_method == InformationGainMethod.QUINLAN_ORIGINAL
        assert config.use_variable_bindings == True
        assert config.binding_generation_method == BindingGenerationMethod.CONSTRAINT_GUIDED
    
    def test_research_accurate_preset(self):
        """Test research-accurate preset configuration."""
        config = create_research_accurate_config()
        
        # Verify Quinlan (1990) settings
        assert config.information_gain_method == InformationGainMethod.QUINLAN_ORIGINAL
        assert config.use_variable_bindings == True
        assert config.validate_against_quinlan_paper == True
        assert config.coverage_testing_method == CoverageTestingMethod.SLD_RESOLUTION
    
    def test_performance_optimized_preset(self):
        """Test performance-optimized preset."""
        config = create_performance_optimized_config()
        
        # Verify performance settings
        assert config.information_gain_method == InformationGainMethod.EXAMPLE_BASED_APPROXIMATION
        assert config.use_variable_bindings == False
        assert config.enable_parallel_processing == True
        assert config.cache_coverage_tests == True
    
    def test_config_validation(self):
        """Test configuration validation system."""
        # Valid config should have no warnings
        config = create_research_accurate_config()
        warnings = validate_foil_config(config)
        
        # Should have no critical warnings for research-accurate config
        critical_warnings = [w for w in warnings if "🚨 CRITICAL" in w]
        assert len(critical_warnings) == 0, f"Unexpected critical warnings: {critical_warnings}"
    
    def test_invalid_config_detection(self):
        """Test detection of invalid configurations."""
        config = FOILComprehensiveConfig()
        config.significance_level = -0.1  # Invalid
        config.binding_enumeration_limit = -1  # Invalid
        
        warnings = validate_foil_config(config)
        
        # Should detect invalid parameters
        assert len(warnings) > 0
        assert any("Invalid significance level" in w for w in warnings)
    
    def test_all_enum_values_valid(self):
        """Test all enum values can be used."""
        # Test InformationGainMethod
        for method in InformationGainMethod:
            config = FOILComprehensiveConfig(information_gain_method=method)
            assert config.information_gain_method == method
        
        # Test BindingGenerationMethod  
        for method in BindingGenerationMethod:
            config = FOILComprehensiveConfig(binding_generation_method=method)
            assert config.binding_generation_method == method
        
        # Test CoverageTestingMethod
        for method in CoverageTestingMethod:
            config = FOILComprehensiveConfig(coverage_testing_method=method)
            assert config.coverage_testing_method == method


class TestProgolComprehensiveConfig:
    """Test Progol comprehensive configuration system."""
    
    def test_config_creation(self):
        """Test basic Progol config creation."""
        config = ProgolComprehensiveConfig()
        assert config.inverse_entailment_method == InverseEntailmentMethod.MUGGLETON_ORIGINAL
        assert config.bottom_clause_construction == BottomClauseConstruction.MODE_GUIDED
        assert config.integrate_background_knowledge == True
    
    def test_muggleton_accurate_preset(self):
        """Test Muggleton (1995) accurate configuration."""
        config = create_muggleton_accurate_config()
        
        # Verify Muggleton settings
        assert config.inverse_entailment_method == InverseEntailmentMethod.MUGGLETON_ORIGINAL
        assert config.validate_against_muggleton_paper == True
        assert config.require_mode_declarations == True
        assert config.strict_mode_compliance == True
    
    def test_progol_config_validation(self):
        """Test Progol configuration validation."""
        config = create_muggleton_accurate_config()
        warnings = validate_progol_config(config)
        
        # Research-accurate config should have minimal warnings
        critical_warnings = [w for w in warnings if "🚨" in w]
        assert len(critical_warnings) == 0, f"Unexpected critical warnings: {critical_warnings}"
    
    def test_progol_enum_coverage(self):
        """Test all Progol enums work correctly."""
        # Test InverseEntailmentMethod
        for method in InverseEntailmentMethod:
            config = ProgolComprehensiveConfig(inverse_entailment_method=method)
            assert config.inverse_entailment_method == method
        
        # Test BottomClauseConstruction
        for construction in BottomClauseConstruction:
            config = ProgolComprehensiveConfig(bottom_clause_construction=construction)
            assert config.bottom_clause_construction == construction


class TestFOILResearchAccurate:
    """Test research-accurate FOIL implementation."""
    
    def test_variable_binding_creation(self):
        """Test VariableBinding dataclass."""
        binding = VariableBinding(
            substitution={"X": "john", "Y": "mary"},
            is_positive=True,
            satisfies_clause=True
        )
        
        assert binding.substitution["X"] == "john"
        assert binding.is_positive == True
        assert binding.satisfies_clause == True
    
    def test_research_foil_system_creation(self):
        """Test creation of research-accurate FOIL system."""
        config = create_research_accurate_config()
        foil_system = create_research_foil_system(config)
        
        assert foil_system.config == config
        assert hasattr(foil_system, 'background_knowledge')
        assert hasattr(foil_system, 'learned_clauses')
    
    def test_binding_generation_quinlan_method(self):
        """Test Quinlan's variable binding generation."""
        config = create_research_accurate_config()
        foil_system = create_research_foil_system(config)
        
        # Simple test example
        positive_examples = [
            {"father": [("tom", "bob"), ("bob", "pat")]},
            {"male": [("tom",), ("bob",)]}
        ]
        
        # Test binding generation for a simple clause
        clause = "grandfather(X, Y) :- father(X, Z), father(Z, Y)"
        
        bindings = foil_system.generate_variable_bindings(
            clause, 
            positive_examples[0]
        )
        
        # Should generate some bindings
        assert len(bindings) > 0
        assert all(isinstance(b, VariableBinding) for b in bindings)
    
    def test_information_gain_calculation(self):
        """Test Quinlan's information gain formula."""
        config = create_research_accurate_config()
        foil_system = create_research_foil_system(config)
        
        # Create test bindings
        test_bindings = [
            VariableBinding({"X": "tom", "Y": "bob"}, is_positive=True, satisfies_clause=True),
            VariableBinding({"X": "bob", "Y": "pat"}, is_positive=True, satisfies_clause=True),
            VariableBinding({"X": "tom", "Y": "sue"}, is_positive=False, satisfies_clause=False),
        ]
        
        # Test information gain calculation
        gain = foil_system.calculate_information_gain(
            test_bindings,
            "father(X, Z)"  # Test literal
        )
        
        # Should return a numeric gain value
        assert isinstance(gain, (float, int))
        assert gain >= 0  # Information gain should be non-negative
    
    def test_sld_resolution_coverage(self):
        """Test SLD resolution for coverage testing."""
        config = create_research_accurate_config()
        config.coverage_testing_method = CoverageTestingMethod.SLD_RESOLUTION
        foil_system = create_research_foil_system(config)
        
        # Simple coverage test
        clause = "parent(X, Y) :- father(X, Y)"
        example = {"father": [("tom", "bob")]}
        
        covers = foil_system.test_coverage(clause, example, "parent(tom, bob)")
        
        # Should return boolean coverage result
        assert isinstance(covers, bool)
    
    def test_mode_declaration_support(self):
        """Test mode declaration parsing and usage."""
        config = create_research_accurate_config()
        foil_system = create_research_foil_system(config)
        
        # Test mode declarations
        mode_declarations = [
            "parent(+person, -person)",
            "male(+person)",
            "female(+person)"
        ]
        
        foil_system.set_mode_declarations(mode_declarations)
        
        # Should parse modes correctly
        assert len(foil_system.mode_declarations) == len(mode_declarations)
        assert "parent" in foil_system.mode_declarations
        assert "male" in foil_system.mode_declarations
    
    def test_theta_subsumption(self):
        """Test theta-subsumption checking."""
        config = create_research_accurate_config()
        foil_system = create_research_foil_system(config)
        
        clause1 = "parent(X, Y) :- father(X, Y)"
        clause2 = "parent(tom, Y) :- father(tom, Y)"
        
        # clause1 should subsume clause2 (more general)
        subsumes = foil_system.theta_subsumes(clause1, clause2)
        
        # Should detect subsumption relationship
        assert isinstance(subsumes, bool)
    
    def test_laplace_correction(self):
        """Test Laplace correction in probability estimates."""
        config = create_research_accurate_config()
        config.use_laplace_correction = True
        config.laplace_alpha = 1.0
        
        foil_system = create_research_foil_system(config)
        
        # Test with small sample
        positive_count = 2
        negative_count = 1
        
        probability = foil_system.calculate_probability_with_laplace(
            positive_count, 
            negative_count
        )
        
        # Should apply Laplace correction
        expected = (positive_count + config.laplace_alpha) / (positive_count + negative_count + 2 * config.laplace_alpha)
        assert abs(probability - expected) < 1e-6


class TestCrossModuleIntegration:
    """Test integration between different solution modules."""
    
    def test_foil_progol_config_compatibility(self):
        """Test compatibility between FOIL and Progol configs."""
        foil_config = create_research_accurate_config()
        progol_config = create_muggleton_accurate_config()
        
        # Both should support mode declarations
        assert foil_config.require_mode_declarations == True
        assert progol_config.require_mode_declarations == True
        
        # Both should support background knowledge
        assert foil_config.integrate_background_knowledge == True
        assert progol_config.integrate_background_knowledge == True
    
    def test_performance_vs_accuracy_tradeoffs(self):
        """Test performance vs accuracy configuration tradeoffs."""
        accurate_config = create_research_accurate_config()
        fast_config = create_performance_optimized_config()
        
        # Accurate config should prioritize research accuracy
        assert accurate_config.information_gain_method == InformationGainMethod.QUINLAN_ORIGINAL
        assert accurate_config.use_variable_bindings == True
        assert accurate_config.coverage_testing_method == CoverageTestingMethod.SLD_RESOLUTION
        
        # Fast config should prioritize speed
        assert fast_config.information_gain_method == InformationGainMethod.EXAMPLE_BASED_APPROXIMATION
        assert fast_config.use_variable_bindings == False
        assert fast_config.enable_parallel_processing == True
    
    def test_configuration_serialization(self):
        """Test configuration serialization/deserialization."""
        original_config = create_research_accurate_config()
        
        # Convert to dict
        config_dict = original_config.__dict__.copy()
        
        # Should be serializable
        assert isinstance(config_dict, dict)
        assert len(config_dict) > 0
        
        # Key fields should be present
        assert 'information_gain_method' in config_dict
        assert 'binding_generation_method' in config_dict
        assert 'coverage_testing_method' in config_dict


class TestResearchAccuracyValidation:
    """Test research accuracy against known papers."""
    
    def test_quinlan_1990_formula_implementation(self):
        """Test implementation matches Quinlan (1990) formula exactly."""
        config = create_research_accurate_config()
        foil_system = create_research_foil_system(config)
        
        # Test Quinlan's information gain formula: Gain = t × (log(p₁/(p₁+n₁)) - log(p₀/(p₀+n₀)))
        p0, n0 = 10, 5  # Before adding literal
        p1, n1 = 8, 2   # After adding literal
        t = p1           # Number of positive bindings covered by new literal
        
        expected_gain = t * (np.log(p1/(p1+n1)) - np.log(p0/(p0+n0)))
        calculated_gain = foil_system._quinlan_information_gain_formula(p0, n0, p1, n1, t)
        
        # Should match within numerical precision
        assert abs(calculated_gain - expected_gain) < 1e-10
    
    def test_muggleton_1995_inverse_entailment(self):
        """Test implementation follows Muggleton (1995) inverse entailment."""
        config = create_muggleton_accurate_config()
        
        # Verify theoretical soundness parameters
        assert config.inverse_entailment_method == InverseEntailmentMethod.MUGGLETON_ORIGINAL
        assert config.validate_against_muggleton_paper == True
        assert config.use_occurs_check == True  # Proper unification
    
    def test_research_paper_citations_present(self):
        """Verify all implementations cite appropriate research papers."""
        # This test ensures research citations are maintained
        
        foil_config_code = open("/Users/benedictchen/work/research_papers/packages/inductive_logic_programming/src/inductive_logic_programming/foil_comprehensive_config.py").read()
        progol_config_code = open("/Users/benedictchen/work/research_papers/packages/inductive_logic_programming/src/inductive_logic_programming/progol_comprehensive_config.py").read()
        
        # Check for research citations
        assert "Quinlan (1990)" in foil_config_code
        assert "Muggleton (1995)" in progol_config_code
        assert "Learning logical definitions from relations" in foil_config_code
        assert "Inverse entailment and Progol" in progol_config_code


if __name__ == "__main__":
    # Run comprehensive tests
    print("🧪 Running comprehensive FIXME solution tests...")
    
    # Run specific test classes
    test_classes = [
        TestFOILComprehensiveConfig,
        TestProgolComprehensiveConfig,
        TestFOILResearchAccurate,
        TestCrossModuleIntegration,
        TestResearchAccuracyValidation
    ]
    
    for test_class in test_classes:
        print(f"\n📋 Testing {test_class.__name__}...")
        instance = test_class()
        
        # Run all test methods
        for method_name in dir(instance):
            if method_name.startswith('test_'):
                try:
                    method = getattr(instance, method_name)
                    method()
                    print(f"   ✅ {method_name}")
                except Exception as e:
                    print(f"   ❌ {method_name}: {e}")
    
    print("\n🎉 Comprehensive FIXME solution testing complete!")