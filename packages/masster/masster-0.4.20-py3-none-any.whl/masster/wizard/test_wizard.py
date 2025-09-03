#!/usr/bin/env python3
"""
Test script for the Wizard class.

This script tests the basic functionality of the Wizard class without
requiring actual raw data files.
"""

import tempfile
from pathlib import Path
import sys

# Add masster to path if needed
sys.path.insert(0, str(Path(__file__).parent.parent))

from masster import Wizard, wizard_def


def test_wizard_initialization():
    """Test wizard initialization and parameter handling."""
    print("Testing Wizard initialization...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        data_source = temp_path / "data"
        study_folder = temp_path / "study"
        
        # Create directories
        data_source.mkdir()
        
        # Test basic initialization
        wizard = Wizard(
            data_source=str(data_source),
            study_folder=str(study_folder),
            polarity="positive",
            num_cores=2
        )
        
        assert wizard.polarity == "positive"
        assert wizard.params.num_cores == 2
        assert len(wizard.adducts) > 0  # Should have default adducts
        assert study_folder.exists()  # Should create output directory
        
        print("✅ Basic initialization works")
        
        # Test parameter validation
        try:
            Wizard(
                data_source="",  # Empty data source should fail
                study_folder=str(study_folder)
            )
            assert False, "Should have failed with empty data_source"
        except ValueError:
            print("✅ Parameter validation works")
        
        # Test custom parameters
        custom_params = wizard_def(
            data_source=str(data_source),
            study_folder=str(study_folder / "custom"),
            polarity="negative",
            num_cores=4,
            adducts=["H-1:-:1.0", "Cl:-:0.1"],
            batch_size=2,
            generate_plots=False
        )
        
        custom_wizard = Wizard(params=custom_params)
        assert custom_wizard.polarity == "negative"
        assert custom_wizard.params.batch_size == 2
        assert not custom_wizard.params.generate_plots
        
        print("✅ Custom parameters work")


def test_file_discovery():
    """Test file discovery functionality."""
    print("\nTesting file discovery...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        data_source = temp_path / "data"
        study_folder = temp_path / "study"
        
        # Create test directory structure
        data_source.mkdir()
        (data_source / "subdir").mkdir()
        
        # Create mock files
        test_files = [
            "sample1.wiff",
            "sample2.raw", 
            "sample3.mzML",
            "blank.wiff",  # Should be skipped
            "QC_test.raw",  # Should be skipped
            "subdir/sample4.wiff",
        ]
        
        for filename in test_files:
            file_path = data_source / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text("mock file content")
        
        # Create wizard
        wizard = Wizard(
            data_source=str(data_source),
            study_folder=str(study_folder),
            polarity="positive"
        )
        
        # Test file discovery
        found_files = wizard.discover_files()
        found_names = [f.name for f in found_files]
        
        # Should find sample files but skip blanks and QC
        assert "sample1.wiff" in found_names
        assert "sample2.raw" in found_names
        assert "sample3.mzML" in found_names
        assert "sample4.wiff" in found_names  # From subdirectory
        assert "blank.wiff" not in found_names  # Should be skipped
        assert "QC_test.raw" not in found_names  # Should be skipped
        
        print(f"✅ Found {len(found_files)} files, correctly filtered")
        
        # Test without subdirectory search
        wizard.params.search_subfolders = False
        found_files_no_sub = wizard.discover_files()
        found_names_no_sub = [f.name for f in found_files_no_sub]
        
        assert "sample4.wiff" not in found_names_no_sub  # Should not find in subdir
        assert len(found_files_no_sub) < len(found_files)
        
        print("✅ Subdirectory search control works")


def test_wizard_status():
    """Test status monitoring and checkpointing."""
    print("\nTesting status monitoring...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        data_source = temp_path / "data"
        study_folder = temp_path / "study"
        
        data_source.mkdir()
        
        wizard = Wizard(
            data_source=str(data_source),
            study_folder=str(study_folder),
            polarity="positive"
        )
        
        # Test initial status
        status = wizard.get_status()
        assert status["current_step"] == "initialized"
        assert status["processed_files"] == 0
        assert not status["study_loaded"]
        
        print("✅ Initial status correct")
        
        # Test status update
        wizard.current_step = "converting_to_sample5"
        wizard.processed_files = ["file1.wiff", "file2.raw"]
        
        status = wizard.get_status()
        assert status["current_step"] == "converting_to_sample5"
        assert status["processed_files"] == 2
        
        print("✅ Status updates work")
        
        # Test checkpoint save/load
        wizard._save_checkpoint()
        checkpoint_file = wizard.checkpoint_file
        assert checkpoint_file.exists()
        
        print("✅ Checkpoint saving works")
        
        # Create new wizard and test checkpoint loading
        new_wizard = Wizard(
            data_source=str(data_source),
            study_folder=str(study_folder),
            polarity="positive",
            resume_enabled=True
        )
        
        # Should load from checkpoint
        assert len(new_wizard.processed_files) == 2
        assert new_wizard.current_step == "converting_to_sample5"
        
        print("✅ Checkpoint loading works")


def test_defaults_and_validation():
    """Test default parameter classes and validation."""
    print("\nTesting parameter defaults and validation...")
    
    # Test wizard_def defaults
    defaults = wizard_def()
    
    # Should set polarity-specific adducts
    assert len(defaults.adducts) > 0
    
    # Test polarity switching
    neg_defaults = wizard_def(polarity="negative")
    pos_defaults = wizard_def(polarity="positive")
    
    # Should have different adducts
    assert neg_defaults.adducts != pos_defaults.adducts
    
    print("✅ Polarity-specific defaults work")
    
    # Test parameter validation
    defaults = wizard_def(
        data_source="/test/path",
        study_folder="/test/output",
        num_cores=999  # Should be capped to available cores
    )
    
    import multiprocessing
    max_cores = multiprocessing.cpu_count()
    assert defaults.num_cores <= max_cores
    
    print("✅ Parameter validation works")


def test_logging_setup():
    """Test logging configuration."""
    print("\nTesting logging setup...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        data_source = temp_path / "data"
        study_folder = temp_path / "study"
        
        data_source.mkdir()
        
        wizard = Wizard(
            data_source=str(data_source),
            study_folder=str(study_folder),
            polarity="positive",
            log_to_file=True,
            log_level="DEBUG"
        )
        
        # Test logging
        wizard._log_progress("Test message")
        
        # Check log files exist
        assert wizard.log_file.exists()
        
        # Check log content
        log_content = wizard.log_file.read_text()
        assert "Test message" in log_content
        
        print("✅ Logging setup works")


def main():
    """Run all tests."""
    print("=" * 50)
    print("WIZARD CLASS TESTS")
    print("=" * 50)
    
    try:
        test_wizard_initialization()
        test_file_discovery()
        test_wizard_status()
        test_defaults_and_validation()
        test_logging_setup()
        
        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
