# -*- coding: utf-8 -*-
"""Quick Test - No Emojis for Windows"""

print("\n" + "="*60)
print("VietStructFEM v1.0.0 - IMPORT TEST")
print("="*60)

passed = 0
failed = 0

# Core modules
print("\n[CORE ENGINES]")
try:
    from steeldeckfem.core.vn_standards_loader import get_vn_standards
    print("  [OK] vn_standards_loader")
    passed += 1
except Exception as e:
    print(f"  [FAIL] vn_standards_loader: {e}")
    failed += 1

try:
    from steeldeckfem.core.rc_beam_designer import RCBeamDesigner
    print("  [OK] rc_beam_designer")
    passed += 1
except Exception as e:
    print(f"  [FAIL] rc_beam_designer: {e}")
    failed += 1

try:
    from steeldeckfem.core.foundation_designer import IsolatedFootingDesigner
    print("  [OK] foundation_designer")
    passed += 1
except Exception as e:
    print(f"  [FAIL] foundation_designer: {e}")
    failed += 1

try:
    from steeldeckfem.core.steel_designer import SteelSectionDatabase
    print("  [OK] steel_designer")
    passed += 1
except Exception as e:
    print(f"  [FAIL] steel_designer: {e}")
    failed += 1

try:
    from steeldeckfem.core.connection_designer import ConnectionDesigner
    print("  [OK] connection_designer")
    passed += 1
except Exception as e:
    print(f"  [FAIL] connection_designer: {e}")
    failed += 1

try:
    from steeldeckfem.core.deflection_utility import DeflectionCalculator
    print("  [OK] deflection_utility")
    passed += 1
except Exception as e:
    print(f"  [FAIL] deflection_utility: {e}")
    failed += 1

# UI modules
print("\n[UI MODULES]")
modules_to_test = [
    ("steel_deck_module", "SteelDeckModule"),
    ("rc_column_module", "RCColumnModule"),
    ("frame_analysis_module", "FrameAnalysisModule"),
    ("opensees_module", "OpenSeesModule"),
    ("rc_beam_module", "RCBeamModule"),
    ("foundation_module", "FoundationModule"),
    ("steel_module", "SteelMemberModule"),
    ("connection_module", "ConnectionModule"),
    ("deflection_module", "DeflectionModule"),
    ("utility_modules", "UtilityModulesWidget"),
]

for module_name, class_name in modules_to_test:
    try:
        exec(f"from steeldeckfem.ui.modules.{module_name} import {class_name}")
        print(f"  [OK] {module_name}")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] {module_name}: {e}")
        failed += 1

# Load combo widget
try:
    from steeldeckfem.ui.widgets.load_combo_wizard import LoadCombinationWizard
    print("  [OK] load_combo_wizard")
    passed += 1
except Exception as e:
    print(f"  [FAIL] load_combo_wizard: {e}")
    failed += 1

# TCVN Data
print("\n[TCVN DATABASE]")
try:
    from steeldeckfem.core.vn_standards_loader import get_vn_standards
    vn = get_vn_standards()
    h_beams = vn.get_all_h_beams()
    box_sections = vn.get_all_box_sections()
    print(f"  [OK] H-beams: {len(h_beams)} sections")
    print(f"  [OK] Box sections: {len(box_sections)} sections")
    passed += 2
except Exception as e:
    print(f"  [FAIL] TCVN data: {e}")
    failed += 2

# Summary
print("\n" + "="*60)
print("RESULTS")
print("="*60)
print(f"Passed: {passed}")
print(f"Failed: {failed}")
print(f"Total: {passed + failed}")
print(f"Success Rate: {passed/(passed+failed)*100:.1f}%")

if failed == 0:
    print("\n*** ALL TESTS PASSED ***")
    exit(0)
else:
    print(f"\n*** {failed} TEST(S) FAILED ***")
    exit(1)
