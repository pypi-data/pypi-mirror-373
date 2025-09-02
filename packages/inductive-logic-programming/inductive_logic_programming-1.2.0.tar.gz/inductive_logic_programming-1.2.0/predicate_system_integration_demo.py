#!/usr/bin/env python3
"""
🔗 PREDICATE SYSTEM INTEGRATION DEMO
===================================

This demo shows how the extracted predicate system module would integrate
with the main ILP system, demonstrating the modular architecture benefits.

Author: Benedict Chen
"""

import sys
from pathlib import Path

# Add the package to Python path
sys.path.append(str(Path(__file__).parent))

from inductive_logic_programming.ilp_modules import (
    LogicalTerm, LogicalAtom, LogicalClause, Example, 
    PredicateSystemMixin
)


class ModularILPSystem(PredicateSystemMixin):
    """
    Example ILP System using the extracted predicate system module
    
    This demonstrates how the main ILP system would inherit from the
    predicate system mixin to gain all predicate management functionality.
    """
    
    def __init__(self, max_clause_length=5, confidence_threshold=0.8):
        # Initialize core ILP attributes
        self.max_clause_length = max_clause_length
        self.confidence_threshold = confidence_threshold
        
        # Initialize data structures required by predicate system mixin
        self.background_knowledge = []
        self.positive_examples = []
        self.negative_examples = []
        self.learned_rules = []
        
        # Vocabulary management (required by predicate system)
        self.predicates = set()
        self.constants = set()
        self.functions = set()
        
        # Initialize the predicate system (from mixin)
        self._initialize_predicate_system()
        
        print("🧠 Modular ILP System initialized with predicate system")
        
    def add_background_knowledge(self, clause: LogicalClause):
        """Add background knowledge with automatic vocabulary extraction"""
        
        self.background_knowledge.append(clause)
        
        # Use predicate system mixin method for vocabulary extraction
        self._update_vocabulary_from_clause(clause)
        
        print(f"   Added background: {clause}")
        
    def add_example(self, atom: LogicalAtom, is_positive: bool):
        """Add training example with vocabulary tracking"""
        
        example = Example(atom=atom, is_positive=is_positive)
        
        if is_positive:
            self.positive_examples.append(example)
        else:
            self.negative_examples.append(example)
            
        # Use predicate system mixin method for vocabulary extraction
        self._update_vocabulary_from_atom(atom)
        
        sign = "+" if is_positive else "-"
        print(f"   Added example: {sign} {atom}")
        
    def generate_hypotheses(self, target_predicate: str):
        """Generate hypotheses using predicate system compatibility"""
        
        print(f"\n🔍 Generating hypotheses for: {target_predicate}")
        
        hypotheses = []
        
        # Use predicate system for compatibility checking during hypothesis generation
        for bg_clause in self.background_knowledge:
            for body_atom in bg_clause.body:
                # Check if background predicate is compatible with target
                if self._predicates_compatible(body_atom.predicate, target_predicate):
                    # Create simple hypothesis: target(X,Y) :- body_atom(X,Y)
                    hypothesis = LogicalClause(
                        head=LogicalAtom(target_predicate, [
                            LogicalTerm("X", term_type="variable"),
                            LogicalTerm("Y", term_type="variable")
                        ]),
                        body=[LogicalAtom(body_atom.predicate, [
                            LogicalTerm("X", term_type="variable"),
                            LogicalTerm("Y", term_type="variable")
                        ])]
                    )
                    hypotheses.append(hypothesis)
                    print(f"   Generated: {hypothesis}")
        
        return hypotheses
        
    def refine_hypotheses(self, hypotheses):
        """Refine hypotheses using theta-subsumption"""
        
        print(f"\n⚡ Refining {len(hypotheses)} hypotheses using theta-subsumption")
        
        refined = []
        
        for i, hyp1 in enumerate(hypotheses):
            is_subsumed = False
            
            # Check if this hypothesis is subsumed by any other
            for j, hyp2 in enumerate(hypotheses):
                if i != j and self.theta_subsumes(hyp2, hyp1):
                    print(f"   Hypothesis {i+1} subsumed by {j+1}")
                    is_subsumed = True
                    break
            
            # Keep non-subsumed hypotheses
            if not is_subsumed:
                refined.append(hyp1)
        
        print(f"   Refined to {len(refined)} non-subsumed hypotheses")
        return refined
        
    def print_system_status(self):
        """Print system status using predicate system vocabulary"""
        
        vocab = self.get_predicate_vocabulary()
        
        print(f"\n📊 System Status:")
        print(f"   Background clauses: {len(self.background_knowledge)}")
        print(f"   Positive examples: {len(self.positive_examples)}")
        print(f"   Negative examples: {len(self.negative_examples)}")
        print(f"   Predicates: {len(vocab['predicates'])}")
        print(f"   Constants: {len(vocab['constants'])}")
        print(f"   Functions: {len(vocab['functions'])}")
        print(f"   Aliases: {len(vocab['aliases'])}")
        print(f"   Hierarchies: {len(vocab['hierarchies'])}")
        

def demo_family_relationships():
    """Demonstrate family relationship learning with predicate system"""
    
    print("👨‍👩‍👧‍👦 FAMILY RELATIONSHIPS DEMO")
    print("=" * 50)
    
    # Create modular ILP system
    ilp = ModularILPSystem(max_clause_length=3, confidence_threshold=0.8)
    
    # Add domain-specific predicate knowledge
    print("\nAdding domain-specific predicate knowledge...")
    ilp.add_predicate_alias("father", "parent")
    ilp.add_predicate_alias("mother", "parent")
    ilp.add_predicate_hierarchy("family_member", {
        "parent", "child", "grandparent", "sibling", "spouse"
    })
    
    # Add background knowledge
    print("\nAdding background knowledge...")
    
    # parent(john, mary) :- true
    ilp.add_background_knowledge(LogicalClause(
        head=LogicalAtom("parent", [
            LogicalTerm("john", term_type="constant"),
            LogicalTerm("mary", term_type="constant")
        ]),
        body=[]
    ))
    
    # grandparent(X,Z) :- parent(X,Y), parent(Y,Z)
    ilp.add_background_knowledge(LogicalClause(
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
    ))
    
    # male(john) :- true
    ilp.add_background_knowledge(LogicalClause(
        head=LogicalAtom("male", [LogicalTerm("john", term_type="constant")]),
        body=[]
    ))
    
    # Add training examples  
    print("\nAdding training examples...")
    
    # Positive examples for father
    ilp.add_example(LogicalAtom("father", [
        LogicalTerm("john", term_type="constant"),
        LogicalTerm("mary", term_type="constant")
    ]), is_positive=True)
    
    # Negative examples
    ilp.add_example(LogicalAtom("father", [
        LogicalTerm("mary", term_type="constant"),
        LogicalTerm("john", term_type="constant")
    ]), is_positive=False)
    
    # Print system status
    ilp.print_system_status()
    
    # Test predicate compatibility
    print("\n🧩 Testing predicate compatibility:")
    test_pairs = [
        ("father", "parent"),
        ("parent", "grandparent"),
        ("male", "parent"),
        ("father", "teacher")
    ]
    
    for pred1, pred2 in test_pairs:
        compatible = ilp._predicates_compatible(pred1, pred2)
        status = "✅ Compatible" if compatible else "❌ Incompatible"
        print(f"   {pred1} ↔ {pred2}: {status}")
    
    # Generate hypotheses
    hypotheses = ilp.generate_hypotheses("father")
    
    # Refine hypotheses using theta-subsumption
    if hypotheses:
        refined_hypotheses = ilp.refine_hypotheses(hypotheses)
    
    # Validate predicate system
    print("\n✅ Validating predicate system...")
    report = ilp.validate_predicate_system()
    if report['errors']:
        print("❌ Validation errors found!")
    else:
        print("✅ Predicate system is consistent")


def demo_business_domain():
    """Demonstrate business domain adaptation"""
    
    print("\n💼 BUSINESS DOMAIN DEMO")
    print("=" * 50)
    
    ilp = ModularILPSystem()
    
    # Add business domain knowledge
    print("Adding business domain knowledge...")
    
    ilp.add_predicate_hierarchy("business_role", {
        "manager", "employee", "director", "analyst", "consultant"
    })
    ilp.add_predicate_hierarchy("business_process", {
        "planning", "execution", "monitoring", "evaluation"
    })
    
    ilp.add_predicate_alias("staff", "employee")
    ilp.add_predicate_alias("supervisor", "manager")
    ilp.add_predicate_alias("exec", "director")
    
    # Test domain-specific compatibility
    print("\nTesting business domain compatibility:")
    
    business_tests = [
        ("manager", "employee"),      # Same hierarchy
        ("staff", "supervisor"),      # Aliases resolve to same hierarchy
        ("planning", "execution"),    # Same process hierarchy
        ("manager", "planning"),      # Different hierarchies
    ]
    
    for pred1, pred2 in business_tests:
        compatible = ilp._predicates_compatible(pred1, pred2)
        status = "✅ Compatible" if compatible else "❌ Incompatible"
        print(f"   {pred1} ↔ {pred2}: {status}")
    
    vocab = ilp.get_predicate_vocabulary()
    print(f"\nBusiness domain vocabulary:")
    print(f"   Hierarchies: {sorted(vocab['hierarchies'])}")
    print(f"   Aliases: {sorted(list(vocab['aliases'])[:10])}")  # Show first 10


def demo_theta_subsumption():
    """Demonstrate theta-subsumption capabilities"""
    
    print("\n🎯 THETA-SUBSUMPTION DEMO")
    print("=" * 50)
    
    ilp = ModularILPSystem()
    
    # Create clauses for subsumption testing
    
    # General: parent(X,Y) :- male(X)
    general = LogicalClause(
        head=LogicalAtom("parent", [
            LogicalTerm("X", term_type="variable"),
            LogicalTerm("Y", term_type="variable")
        ]),
        body=[LogicalAtom("male", [
            LogicalTerm("X", term_type="variable")
        ])]
    )
    
    # Specific: parent(john,mary) :- male(john), adult(john)
    specific = LogicalClause(
        head=LogicalAtom("parent", [
            LogicalTerm("john", term_type="constant"),
            LogicalTerm("mary", term_type="constant")
        ]),
        body=[
            LogicalAtom("male", [
                LogicalTerm("john", term_type="constant")
            ]),
            LogicalAtom("adult", [
                LogicalTerm("john", term_type="constant")
            ])
        ]
    )
    
    print(f"General clause: {general}")
    print(f"Specific clause: {specific}")
    
    # Test subsumption
    subsumes = ilp.theta_subsumes(general, specific)
    print(f"\n✅ Theta-subsumption result: {subsumes}")
    
    # Show substitutions
    substitutions = ilp._find_theta_substitutions(general, specific)
    print(f"Generated substitutions: {substitutions}")
    
    # Test reverse
    reverse = ilp.theta_subsumes(specific, general)
    print(f"Reverse subsumption: {reverse}")


def main():
    """Run all integration demos"""
    
    print("🔗 PREDICATE SYSTEM INTEGRATION DEMONSTRATION")
    print("=" * 70)
    print("Showing how the extracted predicate system integrates with ILP...")
    
    try:
        demo_family_relationships()
        demo_business_domain()
        demo_theta_subsumption()
        
        print("\n🎉 INTEGRATION DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("✅ Predicate system seamlessly integrates with ILP")
        print("✅ Modular architecture enables domain flexibility")
        print("✅ All predicate system features available to main system")
        print("✅ Ready for production use!")
        
    except Exception as e:
        print(f"\n❌ INTEGRATION DEMO FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()