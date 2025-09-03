"""
🔧 Inductive Logic Programming Configuration System
=================================================

Configuration system for selecting between multiple ILP algorithms and methods.
Enables users to choose the most appropriate approach for their specific use case.

Author: Benedict Chen
Based on: Quinlan (1990), Muggleton & De Raedt (1994), Robinson (1965)
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import numpy as np


class SpecializationMethod(Enum):
    """
    Available clause specialization methods with research citations
    """
    # Quinlan (1990) - FOIL algorithm specialization
    FOIL_ORIGINAL = "foil_original"
    
    # Constraint-based literal addition
    CONSTRAINT_LITERALS = "constraint_literals"
    
    # Variable refinement approaches
    VARIABLE_REFINEMENT = "variable_refinement"
    
    # Hybrid specialization combining methods
    HYBRID_SPECIALIZATION = "hybrid_specialization"


class GeneralizationMethod(Enum):
    """
    Available clause generalization methods for ILP
    """
    # Basic literal removal (Muggleton & De Raedt 1994)
    REMOVE_LITERALS = "remove_literals"
    
    # Variable generalization by substitution
    VARIABLE_GENERALIZATION = "variable_generalization"
    
    # Predicate abstraction and hierarchy climbing
    PREDICATE_ABSTRACTION = "predicate_abstraction"
    
    # Hybrid generalization approach
    HYBRID_GENERALIZATION = "hybrid_generalization"


class UnificationMethod(Enum):
    """
    Available unification algorithms for clause matching
    """
    # Robinson (1965) - Original unification algorithm
    ROBINSON_BASIC = "robinson_basic"
    
    # Robinson with occurs check for infinite structure prevention
    ROBINSON_OCCURS_CHECK = "robinson_occurs_check"
    
    # Type-aware unification with type constraints
    TYPE_AWARE = "type_aware"
    
    # Hybrid unification with multiple strategies
    HYBRID_UNIFICATION = "hybrid_unification"


class EvaluationMetric(Enum):
    """
    Evaluation metrics for clause quality assessment
    """
    ACCURACY = "accuracy"
    PRECISION = "precision"
    RECALL = "recall"
    F1_SCORE = "f1_score"
    INFORMATION_GAIN = "information_gain"
    MDL_LENGTH = "mdl_length"


@dataclass
class ILPConfig:
    """
    Comprehensive configuration for Inductive Logic Programming operations
    
    This configuration system allows users to select from multiple research-backed
    implementations and fine-tune parameters for their specific learning task.
    
    Example:
        # Basic FOIL specialization (Quinlan 1990)
        config = ILPConfig(
            specialization_method=SpecializationMethod.FOIL_ORIGINAL,
            generalization_method=GeneralizationMethod.REMOVE_LITERALS,
            unification_method=UnificationMethod.ROBINSON_BASIC
        )
        
        # Advanced hybrid approach
        config = ILPConfig(
            specialization_method=SpecializationMethod.HYBRID_SPECIALIZATION,
            generalization_method=GeneralizationMethod.HYBRID_GENERALIZATION,
            unification_method=UnificationMethod.TYPE_AWARE,
            use_occurs_check=True,
            max_clause_length=10
        )
        
        # Research-accurate Robinson unification (1965)
        config = ILPConfig(
            unification_method=UnificationMethod.ROBINSON_OCCURS_CHECK,
            occurs_check_depth=5,
            type_constraints=True
        )
    """
    
    # === CORE ALGORITHM SELECTION ===
    specialization_method: SpecializationMethod = SpecializationMethod.FOIL_ORIGINAL
    generalization_method: GeneralizationMethod = GeneralizationMethod.REMOVE_LITERALS
    unification_method: UnificationMethod = UnificationMethod.ROBINSON_BASIC
    
    # === CLAUSE STRUCTURE CONSTRAINTS ===
    max_clause_length: int = 20
    min_clause_length: int = 1
    max_variables_per_clause: int = 10
    allow_recursive_clauses: bool = True
    
    # === FOIL SPECIALIZATION SPECIFIC (Quinlan 1990) ===
    foil_gain_threshold: float = 0.1
    foil_significance_threshold: float = 0.01
    foil_max_literals: int = 10
    use_foil_pruning: bool = True
    
    # === CONSTRAINT-BASED SPECIALIZATION ===
    constraint_types: List[str] = None  # ['numerical', 'categorical', 'temporal']
    max_constraints_per_literal: int = 3
    constraint_satisfaction_threshold: float = 0.8
    
    # === VARIABLE REFINEMENT ===
    variable_binding_strength: float = 0.7
    allow_variable_introduction: bool = True
    variable_type_checking: bool = False
    
    # === GENERALIZATION CONTROL ===
    generalization_beam_width: int = 5
    max_generalization_steps: int = 10
    min_coverage_threshold: float = 0.1
    
    # === ROBINSON UNIFICATION SPECIFIC (Robinson 1965) ===
    use_occurs_check: bool = False
    occurs_check_depth: int = 100
    unification_timeout: float = 1.0  # seconds
    
    # === TYPE-AWARE UNIFICATION ===
    type_constraints: bool = False
    strict_type_matching: bool = False
    allow_type_coercion: bool = True
    
    # === EVALUATION AND SEARCH ===
    evaluation_metric: EvaluationMetric = EvaluationMetric.ACCURACY
    beam_search_width: int = 10
    max_search_depth: int = 15
    early_stopping_patience: int = 5
    
    # === PERFORMANCE OPTIMIZATION ===
    use_caching: bool = True
    parallel_evaluation: bool = False
    memory_limit_mb: int = 1000
    
    # === VALIDATION AND DEBUGGING ===
    validate_clauses: bool = True
    verbose_logging: bool = False
    debug_unification: bool = False
    
    def __post_init__(self):
        """Validate configuration and set dependent parameters"""
        # Set default constraint types if None
        if self.constraint_types is None:
            self.constraint_types = ['numerical', 'categorical']
            
        # Validate combinations
        if self.unification_method == UnificationMethod.ROBINSON_OCCURS_CHECK:
            if not self.use_occurs_check:
                self.use_occurs_check = True
                if self.verbose_logging:
                    print("Auto-enabling occurs check for Robinson occurs check unification")
                    
        if self.unification_method == UnificationMethod.TYPE_AWARE:
            if not self.type_constraints:
                self.type_constraints = True
                if self.verbose_logging:
                    print("Auto-enabling type constraints for type-aware unification")
                    
        # Set optimal defaults based on method combinations
        if self.specialization_method == SpecializationMethod.FOIL_ORIGINAL:
            if self.evaluation_metric != EvaluationMetric.INFORMATION_GAIN:
                self.evaluation_metric = EvaluationMetric.INFORMATION_GAIN
                
    def get_algorithm_description(self) -> str:
        """Get human-readable description of selected algorithms"""
        descriptions = {
            SpecializationMethod.FOIL_ORIGINAL: "Quinlan (1990) FOIL - Information gain specialization",
            SpecializationMethod.CONSTRAINT_LITERALS: "Constraint-based literal addition",
            SpecializationMethod.VARIABLE_REFINEMENT: "Variable refinement with binding constraints",
            SpecializationMethod.HYBRID_SPECIALIZATION: "Hybrid specialization combining multiple methods",
            
            GeneralizationMethod.REMOVE_LITERALS: "Muggleton (1994) Literal removal generalization",
            GeneralizationMethod.VARIABLE_GENERALIZATION: "Variable substitution generalization",
            GeneralizationMethod.PREDICATE_ABSTRACTION: "Predicate hierarchy abstraction",
            GeneralizationMethod.HYBRID_GENERALIZATION: "Hybrid multi-strategy generalization",
            
            UnificationMethod.ROBINSON_BASIC: "Robinson (1965) Basic unification algorithm",
            UnificationMethod.ROBINSON_OCCURS_CHECK: "Robinson (1965) with occurs check",
            UnificationMethod.TYPE_AWARE: "Type-aware unification with constraints",
            UnificationMethod.HYBRID_UNIFICATION: "Hybrid unification with multiple strategies"
        }
        
        spec_desc = descriptions.get(self.specialization_method, "Unknown specialization")
        gen_desc = descriptions.get(self.generalization_method, "Unknown generalization")
        unif_desc = descriptions.get(self.unification_method, "Unknown unification")
        
        return f"{spec_desc} + {gen_desc} + {unif_desc}"
    
    def estimate_computational_complexity(self, num_clauses: int = 100, avg_clause_length: int = 5) -> Dict[str, str]:
        """Estimate computational complexity for different configurations"""
        complexity = {}
        
        # Specialization complexity
        if self.specialization_method == SpecializationMethod.FOIL_ORIGINAL:
            complexity['specialization'] = f"O(n²m) where n={num_clauses}, m={avg_clause_length}"
        elif self.specialization_method == SpecializationMethod.CONSTRAINT_LITERALS:
            complexity['specialization'] = f"O(n³m) with constraint checking overhead"
        else:
            complexity['specialization'] = f"O(n²m) to O(n³m) depending on method"
            
        # Generalization complexity  
        if self.generalization_method == GeneralizationMethod.REMOVE_LITERALS:
            complexity['generalization'] = f"O(nm) for literal removal"
        elif self.generalization_method == GeneralizationMethod.PREDICATE_ABSTRACTION:
            complexity['generalization'] = f"O(n²m) for predicate hierarchy traversal"
        else:
            complexity['generalization'] = f"O(nm) to O(n²m) depending on method"
            
        # Unification complexity
        if self.unification_method == UnificationMethod.ROBINSON_BASIC:
            complexity['unification'] = f"O(n) per unification attempt"
        elif self.unification_method == UnificationMethod.ROBINSON_OCCURS_CHECK:
            complexity['unification'] = f"O(n²) per unification with occurs check"
        elif self.unification_method == UnificationMethod.TYPE_AWARE:
            complexity['unification'] = f"O(n log n) per unification with type checking"
        else:
            complexity['unification'] = f"O(n) to O(n²) depending on method"
            
        return complexity


# Preset configurations for common ILP scenarios
class PresetConfigs:
    """
    Preset configurations for common Inductive Logic Programming scenarios
    """
    
    @staticmethod
    def quinlan_foil_original() -> ILPConfig:
        """Original Quinlan (1990) FOIL algorithm configuration"""
        return ILPConfig(
            specialization_method=SpecializationMethod.FOIL_ORIGINAL,
            generalization_method=GeneralizationMethod.REMOVE_LITERALS,
            unification_method=UnificationMethod.ROBINSON_BASIC,
            foil_gain_threshold=0.1,
            evaluation_metric=EvaluationMetric.INFORMATION_GAIN,
            use_foil_pruning=True
        )
    
    @staticmethod  
    def muggleton_progol() -> ILPConfig:
        """Muggleton & De Raedt (1994) Progol-style configuration"""
        return ILPConfig(
            specialization_method=SpecializationMethod.CONSTRAINT_LITERALS,
            generalization_method=GeneralizationMethod.VARIABLE_GENERALIZATION,
            unification_method=UnificationMethod.ROBINSON_OCCURS_CHECK,
            use_occurs_check=True,
            constraint_satisfaction_threshold=0.9,
            max_clause_length=15
        )
    
    @staticmethod
    def robinson_unification_research() -> ILPConfig:
        """Robinson (1965) research-accurate unification"""
        return ILPConfig(
            specialization_method=SpecializationMethod.FOIL_ORIGINAL,
            generalization_method=GeneralizationMethod.REMOVE_LITERALS,
            unification_method=UnificationMethod.ROBINSON_OCCURS_CHECK,
            use_occurs_check=True,
            occurs_check_depth=100,
            unification_timeout=5.0,
            debug_unification=True
        )
    
    @staticmethod
    def performance_optimized() -> ILPConfig:
        """High-performance configuration for large datasets"""
        return ILPConfig(
            specialization_method=SpecializationMethod.FOIL_ORIGINAL,
            generalization_method=GeneralizationMethod.REMOVE_LITERALS,
            unification_method=UnificationMethod.ROBINSON_BASIC,
            use_caching=True,
            parallel_evaluation=True,
            beam_search_width=20,
            early_stopping_patience=3
        )
    
    @staticmethod
    def research_comprehensive() -> ILPConfig:
        """Comprehensive configuration combining all research methods"""
        return ILPConfig(
            specialization_method=SpecializationMethod.HYBRID_SPECIALIZATION,
            generalization_method=GeneralizationMethod.HYBRID_GENERALIZATION,
            unification_method=UnificationMethod.HYBRID_UNIFICATION,
            use_occurs_check=True,
            type_constraints=True,
            constraint_types=['numerical', 'categorical', 'temporal'],
            max_clause_length=25,
            verbose_logging=True
        )
    
    @staticmethod
    def type_aware_modern() -> ILPConfig:
        """Modern type-aware ILP configuration"""
        return ILPConfig(
            specialization_method=SpecializationMethod.VARIABLE_REFINEMENT,
            generalization_method=GeneralizationMethod.PREDICATE_ABSTRACTION,
            unification_method=UnificationMethod.TYPE_AWARE,
            type_constraints=True,
            strict_type_matching=True,
            variable_type_checking=True,
            evaluation_metric=EvaluationMetric.F1_SCORE
        )


# Export key components
__all__ = [
    'SpecializationMethod',
    'GeneralizationMethod', 
    'UnificationMethod',
    'EvaluationMetric',
    'ILPConfig',
    'PresetConfigs'
]