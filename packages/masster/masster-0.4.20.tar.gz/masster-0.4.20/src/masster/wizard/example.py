#!/usr/bin/env python3
"""
Example script demonstrating the Wizard class for automated study processing.

This script shows how to use the Wizard class to automatically process
mass spectrometry data from raw files to final study results.
"""

from pathlib import Path
from masster import Wizard, wizard_def

def main():
    """Main example function."""
    
    # =================================================================
    # EXAMPLE 1: Basic Usage with Minimal Configuration
    # =================================================================
    print("=== Example 1: Basic Wizard Usage ===\n")
    
    # Set up paths (adjust these for your data)
    data_source = r"D:\Data\raw_files"  # Directory with .wiff, .raw, .mzML files
    study_folder = r"D:\Data\processed_study"  # Output directory
    
    # Create wizard with basic settings
    wizard = Wizard(
        data_source=data_source,
        study_folder=study_folder,
        polarity="positive",  # or "negative"
        num_cores=4
    )
    
    # Run the complete pipeline
    success = wizard.run_full_pipeline()
    
    if success:
        print("✅ Processing completed successfully!")
        wizard.info()  # Print status summary
    else:
        print("❌ Processing failed. Check logs for details.")
    
    print("\n" + "="*60 + "\n")
    
    # =================================================================
    # EXAMPLE 2: Advanced Configuration with Custom Parameters
    # =================================================================
    print("=== Example 2: Advanced Wizard Configuration ===\n")
    
    # Create custom parameters
    params = wizard_def(
        # Core settings
        data_source=data_source,
        study_folder=study_folder + "_advanced",
        polarity="negative",
        num_cores=8,
        
        # File discovery settings
        file_extensions=[".wiff", ".raw", ".mzML"],
        search_subfolders=True,
        skip_patterns=["blank", "QC", "test", "solvent"],
        
        # Processing parameters
        adducts=["H-1:-:0.95", "Cl:-:0.05", "CH2O2:0:0.2"],
        batch_size=4,  # Process 4 files at once
        memory_limit_gb=32.0,
        
        # Feature detection parameters
        chrom_fwhm=0.15,  # Narrower peaks for UHPLC
        noise_threshold=5e4,  # Lower noise threshold
        chrom_peak_snr=7.0,  # Higher S/N requirement
        tol_ppm=8.0,  # Tighter mass tolerance
        
        # Study assembly parameters
        rt_tolerance=1.0,  # Tighter RT tolerance
        mz_tolerance=0.008,  # Tighter m/z tolerance
        min_samples_for_merge=30,  # Require feature in at least 30 samples
        merge_method="chunked",  # Memory-efficient merging
        
        # Output options
        generate_plots=True,
        generate_interactive=True,
        export_formats=["csv", "xlsx", "mgf", "parquet"],
        compress_output=True,
        adaptive_compression=True,
        
        # Advanced options
        resume_enabled=True,  # Can resume if interrupted
        force_reprocess=False,  # Skip already processed files
        backup_enabled=True,
        cleanup_temp_files=True,
        log_level="INFO",
        verbose_progress=True,
    )
    
    # Create wizard with custom parameters
    wizard_advanced = Wizard(params=params)
    
    # You can also run individual steps for more control
    print("Running step-by-step processing...")
    
    # Step 1: Discover files
    files = wizard_advanced.discover_files()
    print(f"Found {len(files)} files for processing")
    
    # Step 2: Convert to sample5 (can be resumed if interrupted)
    if wizard_advanced.convert_to_sample5():
        print("✅ Sample5 conversion completed")
        
        # Step 3: Assemble study
        if wizard_advanced.assemble_study():
            print("✅ Study assembly completed")
            
            # Step 4: Align and merge
            if wizard_advanced.align_and_merge():
                print("✅ Alignment and merging completed")
                
                # Step 5: Generate plots
                if wizard_advanced.generate_plots():
                    print("✅ Plot generation completed")
                
                # Step 6: Export results
                if wizard_advanced.export_results():
                    print("✅ Results exported")
                
                # Step 7: Save final study
                if wizard_advanced.save_study():
                    print("✅ Study saved")
                    
                    # Optional cleanup
                    wizard_advanced.cleanup_temp_files()
                    print("✅ Cleanup completed")
    
    # Print final status
    wizard_advanced.info()
    
    print("\n" + "="*60 + "\n")
    
    # =================================================================
    # EXAMPLE 3: Resume Interrupted Processing
    # =================================================================
    print("=== Example 3: Resume Capability ===\n")
    
    # If processing was interrupted, you can resume by creating a new wizard
    # with the same parameters. It will automatically detect and skip
    # already processed files.
    
    resume_wizard = Wizard(
        data_source=data_source,
        study_folder=study_folder + "_resume",
        polarity="positive",
        num_cores=4,
        resume_enabled=True  # This is the default
    )
    
    # The wizard will automatically load checkpoint and continue from where it left off
    print("Status after loading checkpoint:")
    resume_wizard.info()
    
    print("\n" + "="*60 + "\n")
    
    # =================================================================
    # EXAMPLE 4: Monitoring and Status
    # =================================================================
    print("=== Example 4: Status Monitoring ===\n")
    
    # You can check wizard status at any time
    status = wizard.get_status()
    print("Wizard Status:")
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    # The wizard maintains comprehensive logs
    log_file = Path(study_folder) / "wizard.log"
    if log_file.exists():
        print(f"\nDetailed logs available at: {log_file}")
    
    processing_log = Path(study_folder) / "processing.log" 
    if processing_log.exists():
        print(f"Processing summary at: {processing_log}")


def example_batch_different_polarities():
    """Example of processing positive and negative mode data separately."""
    
    print("=== Processing Both Polarities ===\n")
    
    base_data_source = r"D:\Data\raw_files"
    base_output = r"D:\Data\processed_studies"
    
    # Process positive mode
    pos_wizard = Wizard(
        data_source=base_data_source + r"\positive",
        study_folder=base_output + r"\positive_study",
        polarity="positive",
        adducts=["H:+:0.8", "Na:+:0.1", "NH4:+:0.1"],
        num_cores=6
    )
    
    print("Processing positive mode data...")
    pos_success = pos_wizard.run_full_pipeline()
    
    # Process negative mode  
    neg_wizard = Wizard(
        data_source=base_data_source + r"\negative", 
        study_folder=base_output + r"\negative_study",
        polarity="negative",
        adducts=["H-1:-:0.95", "Cl:-:0.05"],
        num_cores=6
    )
    
    print("Processing negative mode data...")
    neg_success = neg_wizard.run_full_pipeline()
    
    print("\nResults:")
    print(f"Positive mode: {'✅ Success' if pos_success else '❌ Failed'}")
    print(f"Negative mode: {'✅ Success' if neg_success else '❌ Failed'}")


if __name__ == "__main__":
    # Run basic examples
    main()
    
    # Uncomment to run polarity-specific processing
    # example_batch_different_polarities()
