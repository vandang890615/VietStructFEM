# -*- coding: utf-8 -*-
"""
Smoke Test Script for VietStructFEM v1.0.0
Tests all 11 modules for basic functionality
"""

import sys
import traceback

def test_module(module_name, test_func):
    """Test a module and report result"""
    print(f"\n{'='*60}")
    print(f"Testing: {module_name}")
    print(f"{'='*60}")
    try:
        test_func()
        print(f"✅ {module_name}: PASSED")
        return True
    except Exception as e:
        print(f"❌ {module_name}: FAILED")
        print(f"Error: {str(e)}")
        print(traceback.format_exc())
        return False

def test_steel_deck():
    """Test Steel Deck Module"""
    from steeldeckfem.ui.modules.steel_deck_module import SteelDeckModule
    module = SteelDeckModule()
    assert module is not None
    print("  - Module instantiated successfully")

def test_rc_column():
    """Test RC Column Module"""
    from steeldeckfem.ui.modules.rc_column_module import RCColumnModule
    module = RCColumnModule()
    assert module is not None
    print("  - Module instantiated successfully")

def test_frame_analysis():
    """Test Frame Analysis Module"""
    from steeldeckfem.ui.modules.frame_analysis_module import FrameAnalysisModule
    module = FrameAnalysisModule()
    assert module is not None
    print("  - Module instantiated successfully")

def test_opensees():
    """Test OpenSees Module"""
    from steeldeckfem.ui.modules.opensees_module import OpenSeesModule
    module = OpenSeesModule()
    assert module is not None
    print("  - Module instantiated successfully")

def test_load_combo():
    """Test Load Combination Module"""
    from steeldeckfem.ui.widgets.load_combo_wizard import LoadCombinationWizard
    module = LoadCombinationWizard()
    assert module is not None
    print("  - Module instantiated successfully")

def test_rc_beam():
    """Test RC Beam Module"""
    from steeldeckfem.ui.modules.rc_beam_module import RCBeamModule
    module = RCBeamModule()
    assert module is not None
    print("  - Module instantiated successfully")

def test_foundation():
    """Test Foundation Module"""
    from steeldeckfem.ui.modules.foundation_module import FoundationModule
    module = FoundationModule()
    assert module is not None
    print("  - Module instantiated successfully")

def test_steel_members():
    """Test Steel Members Module"""
    from steeldeckfem.ui.modules.steel_module import SteelMemberModule
    module = SteelMemberModule()
    assert module is not None
    print("  - Module instantiated successfully")
    
def test_connections():
    """Test Steel Connections Module"""
    from steeldeckfem.ui.modules.connection_module import ConnectionModule
    module = ConnectionModule()
    assert module is not None
    print("  - Module instantiated successfully")

def test_deflection():
    """Test Deflection Check Module"""
    from steeldeckfem.ui.modules.deflection_module import DeflectionModule
    module = DeflectionModule()
    assert module is not None
    print("  - Module instantiated successfully")

def test_utilities():
    """Test Utilities Module"""
    from steeldeckfem.ui.modules.utility_modules import UtilityModulesWidget
    module = UtilityModulesWidget()
    assert module is not None
    print("  - Module instantiated successfully")

def test_core_engines():
    """Test Core Calculation Engines"""
    print("\nTesting Core Engines:")
    
    # VN Standards Loader
    from steeldeckfem.core.vn_standards_loader import get_vn_standards
    vn_std = get_vn_standards()
    print("  ✅ VN Standards Loader")
    
    # RC Beam Designer
    from steeldeckfem.core.rc_beam_designer import RCBeamDesigner
    beam = RCBeamDesigner(300, 500, 6.0)
    print("  ✅ RC Beam Designer")
    
    # Foundation Designer
    from steeldeckfem.core.foundation_designer import IsolatedFootingDesigner
    footing = IsolatedFootingDesigner()
    print("  ✅ Foundation Designer")
    
    # Steel Designer
    from steeldeckfem.core.steel_designer import SteelSectionDatabase
    sections = SteelSectionDatabase.get_all_h_beams()
    print(f"  ✅ Steel Designer ({len(sections)} sections)")
    
    # Connection Designer
    from steeldeckfem.core.connection_designer import ConnectionDesigner
    result = ConnectionDesigner.check_bolted_connection(4, 20, 'A325', 50)
    print("  ✅ Connection Designer")
    
    # Deflection Utility
    from steeldeckfem.core.deflection_utility import DeflectionCalculator
    defl = DeflectionCalculator()
    print("  ✅ Deflection Calculator")

def main():
    """Run all smoke tests"""
    print("\n" + "="*60)
    print("VietStructFEM v1.0.0 - SMOKE TEST")
    print("="*60)
    
    modules = [
        ("Steel Deck Module", test_steel_deck),
        ("RC Column Module", test_rc_column),
        ("Frame Analysis Module", test_frame_analysis),
        ("OpenSees Module", test_opensees),
        ("Load Combination Module", test_load_combo),
        ("RC Beam Module", test_rc_beam),
        ("Foundation Module", test_foundation),
        ("Steel Members Module", test_steel_members),
        ("Steel Connections Module", test_connections),
        ("Deflection Check Module", test_deflection),
        ("Utilities Module", test_utilities),
    ]
    
    results = []
    for name, test_func in modules:
        results.append(test_module(name, test_func))
    
    # Test core engines
    print(f"\n{'='*60}")
    print("Testing: Core Calculation Engines")
    print(f"{'='*60}")
    try:
        test_core_engines()
        results.append(True)
        print("✅ Core Engines: PASSED")
    except Exception as e:
        print(f"❌ Core Engines: FAILED - {str(e)}")
        results.append(False)
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    print(f"Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        return 0
    else:
        print(f"\n⚠️ {total - passed} TESTS FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
