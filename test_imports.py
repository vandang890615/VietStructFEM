# -*- coding: utf-8 -*-
"""
Quick Import Test for VietStructFEM v1.0.0
Tests that all modules can be imported
"""

def test_imports():
    """Test all module imports"""
    print("\nTESTING MODULE IMPORTS...")
    print("="*60)
    
    tests = []
    
    # Test 1: Core Engines
    print("\n1. Core Calculation Engines:")
    try:
        from steeldeckfem.core.vn_standards_loader import get_vn_standards
        print("  ✅ vn_standards_loader")
        tests.append(True)
    except Exception as e:
        print(f"  ❌ vn_standards_loader: {e}")
        tests.append(False)
    
    try:
        from steeldeckfem.core.rc_beam_designer import RCBeamDesigner
        print("  ✅ rc_beam_designer")
        tests.append(True)
    except Exception as e:
        print(f"  ❌ rc_beam_designer: {e}")
        tests.append(False)
    
    try:
        from steeldeckfem.core.foundation_designer import IsolatedFootingDesigner
        print("  ✅ foundation_designer")
        tests.append(True)
    except Exception as e:
        print(f"  ❌ foundation_designer: {e}")
        tests.append(False)
    
    try:
        from steeldeckfem.core.steel_designer import SteelSectionDatabase
        print("  ✅ steel_designer")
        tests.append(True)
    except Exception as e:
        print(f"  ❌ steel_designer: {e}")
        tests.append(False)
    
    try:
        from steeldeckfem.core.connection_designer import ConnectionDesigner
        print("  ✅ connection_designer")
        tests.append(True)
    except Exception as e:
        print(f"  ❌ connection_designer: {e}")
        tests.append(False)
    
    try:
        from steeldeckfem.core.deflection_utility import DeflectionCalculator
        print("  ✅ deflection_utility")
        tests.append(True)
    except Exception as e:
        print(f"  ❌ deflection_utility: {e}")
        tests.append(False)
    
    # Test 2: UI Modules
    print("\n2. UI Modules:")
    try:
        from steeldeckfem.ui.modules.steel_deck_module import SteelDeckModule
        print("  ✅ steel_deck_module")
        tests.append(True)
    except Exception as e:
        print(f"  ❌ steel_deck_module: {e}")
        tests.append(False)
    
    try:
        from steeldeckfem.ui.modules.rc_column_module import RCColumnModule
        print("  ✅ rc_column_module")
        tests.append(True)
    except Exception as e:
        print(f"  ❌ rc_column_module: {e}")
        tests.append(False)
    
    try:
        from steeldeckfem.ui.modules.frame_analysis_module import FrameAnalysisModule
        print("  ✅ frame_analysis_module")
        tests.append(True)
    except Exception as e:
        print(f"  ❌ frame_analysis_module: {e}")
        tests.append(False)
    
    try:
        from steeldeckfem.ui.modules.opensees_module import OpenSeesModule
        print("  ✅ opensees_module")
        tests.append(True)
    except Exception as e:
        print(f"  ❌ opensees_module: {e}")
        tests.append(False)
    
    try:
        from steeldeckfem.ui.widgets.load_combo_wizard import LoadCombinationWizard
        print("  ✅ load_combo_wizard")
        tests.append(True)
    except Exception as e:
        print(f"  ❌ load_combo_wizard: {e}")
        tests.append(False)
    
    try:
        from steeldeckfem.ui.modules.rc_beam_module import RCBeamModule
        print("  ✅ rc_beam_module")
        tests.append(True)
    except Exception as e:
        print(f"  ❌ rc_beam_module: {e}")
        tests.append(False)
    
    try:
        from steeldeckfem.ui.modules.foundation_module import FoundationModule
        print("  ✅ foundation_module")
        tests.append(True)
    except Exception as e:
        print(f"  ❌ foundation_module: {e}")
        tests.append(False)
    
    try:
        from steeldeckfem.ui.modules.steel_module import SteelMemberModule
        print("  ✅ steel_module")
        tests.append(True)
    except Exception as e:
        print(f"  ❌ steel_module: {e}")
        tests.append(False)
    
    try:
        from steeldeckfem.ui.modules.connection_module import ConnectionModule
        print("  ✅ connection_module")
        tests.append(True)
    except Exception as e:
        print(f"  ❌ connection_module: {e}")
        tests.append(False)
    
    try:
        from steeldeckfem.ui.modules.deflection_module import DeflectionModule
        print("  ✅ deflection_module")
        tests.append(True)
    except Exception as e:
        print(f"  ❌ deflection_module: {e}")
        tests.append(False)
    
    try:
        from steeldeckfem.ui.modules.utility_modules import UtilityModulesWidget
        print("  ✅ utility_modules")
        tests.append(True)
    except Exception as e:
        print(f"  ❌ utility_modules: {e}")
        tests.append(False)
    
    # Test 3: TCVN Data
    print("\n3. TCVN Database:")
    try:
        from steeldeckfem.core.vn_standards_loader import get_vn_standards
        vn = get_vn_standards()
        
        # Test data access
        h_beams = vn.get_all_h_beams()
        print(f"  ✅ H-beams loaded: {len(h_beams)} sections")
        
        box_sections = vn.get_all_box_sections()
        print(f"  ✅ Box sections loaded: {len(box_sections)} sections")
        
        factors = vn.get_bearing_capacity_factors(30)
        print(f"  ✅ Bearing factors (φ=30°): Nc={factors['Nc']:.2f}")
        
        tests.append(True)
    except Exception as e:
        print(f"  ❌ TCVN data access failed: {e}")
        tests.append(False)
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    passed = sum(tests)
    total = len(tests)
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total-passed}/{total}")
    print(f"📊 Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL IMPORTS SUCCESSFUL! System is healthy.")
        return 0
    else:
        print(f"\n⚠️ {total-passed} import(s) failed. Review errors above.")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(test_imports())
