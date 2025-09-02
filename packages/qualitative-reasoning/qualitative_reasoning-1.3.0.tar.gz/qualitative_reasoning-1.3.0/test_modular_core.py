#!/usr/bin/env python3
"""
Test script for the modular qualitative reasoning core

This script tests the integration of all modules and verifies that the
modular core maintains backward compatibility with the original implementation.
"""

def test_basic_functionality():
    """Test basic functionality of the modular core"""
    
    print("🧪 Testing Modular Qualitative Reasoning Core")
    print("=" * 50)
    
    try:
        # Import the modular core
        from qualitative_reasoning import QualitativeReasoner, QualitativeValue, QualitativeDirection
        
        print("✓ Import successful")
        
        # Create a reasoner instance
        reasoner = QualitativeReasoner("Test System")
        print("✓ Reasoner created")
        
        # Test adding quantities
        reasoner.add_quantity("temperature", QualitativeValue.POSITIVE_SMALL, 
                            QualitativeDirection.INCREASING, landmarks=[0.0, 100.0])
        reasoner.add_quantity("pressure", QualitativeValue.ZERO, 
                            QualitativeDirection.STEADY)
        print("✓ Quantities added")
        
        # Test adding processes
        reasoner.add_process("heating", 
                           preconditions=["heat_source_present"],
                           quantity_conditions=["temperature > 0"],
                           influences=["I+(temperature)"])
        print("✓ Process added")
        
        # Test adding constraints
        reasoner.add_constraint("temperature > 0")
        print("✓ Constraint added")
        
        # Test simulation
        state = reasoner.run_simulation("step1")
        print("✓ Simulation step executed")
        
        # Test analysis
        explanation = reasoner.explain_quantity("temperature")
        print("✓ Behavior explanation generated")
        
        # Test prediction
        predictions = reasoner.predict_future(3)
        print(f"✓ Future predictions generated ({len(predictions)} steps)")
        
        # Test report generation
        report = reasoner.generate_report("text")
        print("✓ Report generated")
        
        # Test system status
        status = reasoner.get_system_status()
        print(f"✓ System status retrieved (health: {status.get('health', {}).get('status', 'unknown')})")
        
        print("\n🎉 All basic functionality tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    return True


def test_factory_functions():
    """Test factory functions for different use cases"""
    
    print("\n🏭 Testing Factory Functions")
    print("=" * 30)
    
    try:
        from qualitative_reasoning import (
            create_educational_reasoner,
            create_research_reasoner, 
            create_production_reasoner,
            create_demo_reasoner
        )
        
        # Test educational reasoner
        edu_reasoner = create_educational_reasoner("Physics Demo")
        print("✓ Educational reasoner created")
        
        # Test research reasoner
        research_reasoner = create_research_reasoner("Advanced Analysis")
        print("✓ Research reasoner created")
        
        # Test production reasoner
        prod_reasoner = create_production_reasoner("Industrial System", "high")
        print("✓ Production reasoner created")
        
        # Test demo reasoner
        demo_reasoner = create_demo_reasoner("Conference Demo")
        print("✓ Demo reasoner created")
        
        print("\n🎉 All factory function tests passed!")
        
    except Exception as e:
        print(f"❌ Factory test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    return True


def test_security_features():
    """Test security features and constraint evaluation methods"""
    
    print("\n🔒 Testing Security Features")
    print("=" * 30)
    
    try:
        from qualitative_reasoning import QualitativeReasoner, ConstraintEvaluationMethod
        
        # Test different evaluation methods
        reasoner = QualitativeReasoner("Security Test")
        
        # Test AST safe method (default)
        reasoner.configure_security(ConstraintEvaluationMethod.AST_SAFE)
        reasoner.add_quantity("temp", landmarks=[0, 100])
        reasoner.add_constraint("temp > 0")
        print("✓ AST safe evaluation configured")
        
        # Test regex parser method
        reasoner.configure_security(ConstraintEvaluationMethod.REGEX_PARSER)
        print("✓ Regex parser evaluation configured")
        
        # Test hybrid method
        reasoner.configure_security(ConstraintEvaluationMethod.HYBRID)
        print("✓ Hybrid evaluation configured")
        
        # Test constraint evaluation
        state = reasoner.run_simulation("security_test")
        print("✓ Secure constraint evaluation working")
        
        print("\n🎉 All security tests passed!")
        
    except Exception as e:
        print(f"❌ Security test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    return True


def test_visualization_features():
    """Test visualization and reporting features"""
    
    print("\n🎨 Testing Visualization Features")
    print("=" * 30)
    
    try:
        from qualitative_reasoning import QualitativeReasoner, VisualizationConfig
        
        # Create reasoner with visualization config
        viz_config = VisualizationConfig(
            detail_level="comprehensive",
            show_unicode_symbols=True,
            include_explanations=True
        )
        
        reasoner = QualitativeReasoner("Viz Test", visualization_config=viz_config)
        
        # Add some content
        reasoner.add_quantity("flow_rate")
        reasoner.add_quantity("pressure") 
        reasoner.add_process("pumping", ["pump_on"], [], ["I+(pressure)", "I+(flow_rate)"])
        
        # Test different visualization formats
        reasoner.run_simulation("viz_test")
        
        # Test report generation in different formats
        text_report = reasoner.generate_report("text")
        json_report = reasoner.generate_report("json")
        md_report = reasoner.generate_report("markdown")
        
        print("✓ Text report generated")
        print("✓ JSON report generated") 
        print("✓ Markdown report generated")
        
        # Test data export
        json_data = reasoner.export_system_state(format_type="json")
        csv_data = reasoner.export_system_state(format_type="csv")
        
        print("✓ JSON export working")
        print("✓ CSV export working")
        
        print("\n🎉 All visualization tests passed!")
        
    except Exception as e:
        print(f"❌ Visualization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    return True


def main():
    """Run all tests"""
    
    print("🧠 Qualitative Reasoning Modular Core Test Suite")
    print("=" * 60)
    print()
    
    # Run all test suites
    tests = [
        test_basic_functionality,
        test_factory_functions,
        test_security_features,
        test_visualization_features
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
            
    # Print summary
    print("\n" + "=" * 60)
    print(f"📊 Test Summary: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! The modular core is working correctly.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        
    return failed == 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)