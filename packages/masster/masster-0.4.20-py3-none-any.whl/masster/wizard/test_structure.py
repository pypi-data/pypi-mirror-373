#!/usr/bin/env python3
"""
Simple test to verify the wizard module structure works correctly.
"""

def test_wizard_module_import():
    """Test that the wizard module can be imported."""
    try:
        # Test direct wizard module import
        import sys
        from pathlib import Path
        
        # Add the masster directory to path
        masster_path = Path(__file__).parent.parent
        sys.path.insert(0, str(masster_path))
        
        # Import wizard directly from its module
        from wizard import Wizard, wizard_def
        
        print("✅ Successfully imported Wizard from wizard module")
        print(f"✅ wizard_def class available: {wizard_def}")
        print(f"✅ Wizard class available: {Wizard}")
        
        # Test creating wizard_def instance
        defaults = wizard_def(
            data_source="/test/data",
            study_folder="/test/output",
            polarity="positive"
        )
        
        print(f"✅ Created wizard_def instance with polarity: {defaults.polarity}")
        print(f"✅ Default adducts: {defaults.adducts}")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_wizard_module_import()
    print("\n" + "="*50)
    if success:
        print("🎉 WIZARD MODULE STRUCTURE TEST PASSED!")
    else:
        print("❌ WIZARD MODULE STRUCTURE TEST FAILED!")
    print("="*50)
