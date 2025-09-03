"""
Wizard module for automated processing of mass spectrometry studies.

This module provides the Wizard class for fully automated processing of MS data
from raw files to final study results, including batch conversion, assembly,
alignment, merging, plotting, and export.

Key Features:
- Automated discovery and batch conversion of raw data files
- Intelligent resume capability for interrupted processes
- Parallel processing optimization for large datasets
- Adaptive study format based on study size
- Comprehensive logging and progress tracking
- Optimized memory management for large studies

Classes:
- Wizard: Main class for automated study processing
- wizard_def: Default parameters configuration class

Example Usage:
```python
from masster import Wizard, wizard_def

# Create wizard with default parameters
wizard = Wizard(
    data_source="./raw_data",
    study_folder="./processed_study",
    polarity="positive",
    num_cores=4
)

# Run complete processing pipeline
wizard.run_full_pipeline()

# Or run individual steps
wizard.convert_to_sample5()
wizard.assemble_study()
wizard.align_and_merge()
wizard.generate_plots()
wizard.export_results()
```
"""

from __future__ import annotations

import os
import sys
import time
import importlib
import multiprocessing
from pathlib import Path
from typing import Optional, Any, Dict, List
from dataclasses import dataclass, field
import concurrent.futures
from datetime import datetime

# Import masster modules - use delayed import to avoid circular dependencies
from masster.logger import MassterLogger
from masster.study.defaults.study_def import study_defaults
from masster.study.defaults.align_def import align_defaults
from masster.study.defaults.merge_def import merge_defaults


@dataclass
class wizard_def:
    """
    Default parameters for the Wizard automated processing system.
    
    This class provides comprehensive configuration for all stages of automated
    mass spectrometry data processing from raw files to final results.
    
    Attributes:
        # Core Configuration
        data_source (str): Path to directory containing raw data files
        study_folder (str): Output directory for processed study
        polarity (str): Ion polarity mode ("positive" or "negative")
        num_cores (int): Number of CPU cores to use for parallel processing
        
        # File Discovery
        file_extensions (List[str]): File extensions to search for
        search_subfolders (bool): Whether to search subdirectories
        skip_patterns (List[str]): Filename patterns to skip
        
        # Processing Parameters
        adducts (List[str]): Adduct specifications for given polarity
        batch_size (int): Number of files to process per batch
        memory_limit_gb (float): Memory limit for processing (GB)
        
        # Resume & Recovery
        resume_enabled (bool): Enable automatic resume capability
        force_reprocess (bool): Force reprocessing of existing files
        backup_enabled (bool): Create backups of intermediate results
        
        # Output & Export
        generate_plots (bool): Generate visualization plots
        export_formats (List[str]): Output formats to generate
        compress_output (bool): Compress final study file
        
        # Logging
        log_level (str): Logging detail level
        log_to_file (bool): Save logs to file
        progress_interval (int): Progress update interval (seconds)
    """
    
    # === Core Configuration ===
    data_source: str = ""
    study_folder: str = ""  
    polarity: str = "positive"
    num_cores: int = 4
    
    # === File Discovery ===
    file_extensions: List[str] = field(default_factory=lambda: [".wiff", ".raw", ".mzML", ".d"])
    search_subfolders: bool = True
    skip_patterns: List[str] = field(default_factory=lambda: ["blank", "QC", "test"])
    
    # === Processing Parameters ===
    adducts: List[str] = field(default_factory=list)  # Will be set based on polarity
    batch_size: int = 8
    memory_limit_gb: float = 16.0
    max_file_size_gb: float = 4.0
    
    # === Resume & Recovery ===
    resume_enabled: bool = True
    force_reprocess: bool = False
    backup_enabled: bool = True
    checkpoint_interval: int = 10  # Save progress every N files
    
    # === Study Assembly ===
    min_samples_for_merge: int = 2
    rt_tolerance: float = 1.5
    mz_max_diff: float = 0.01
    alignment_algorithm: str = "kd"
    merge_method: str = "chunked"
    
    # === Feature Detection ===
    chrom_fwhm: float = 0.5
    noise_threshold: float = 200.0
    chrom_peak_snr: float = 5.0
    tol_ppm: float = 10.0
    detector_type: str = "unknown"  # Detected detector type ("orbitrap", "quadrupole", "unknown")
    
    # === Output & Export ===
    generate_plots: bool = True
    generate_interactive: bool = True
    export_formats: List[str] = field(default_factory=lambda: ["csv", "mgf", "xlsx"])
    compress_output: bool = True
    adaptive_compression: bool = True  # Adapt based on study size
    
    # === Logging ===
    log_level: str = "INFO"
    log_to_file: bool = True
    progress_interval: int = 30  # seconds
    verbose_progress: bool = True
    
    # === Advanced Options ===
    use_process_pool: bool = True  # vs ThreadPoolExecutor
    optimize_memory: bool = True
    cleanup_temp_files: bool = True
    validate_outputs: bool = True
    
    _param_metadata: dict[str, dict[str, Any]] = field(
        default_factory=lambda: {
            "data_source": {
                "dtype": str,
                "description": "Path to directory containing raw data files",
                "required": True,
            },
            "study_folder": {
                "dtype": str, 
                "description": "Output directory for processed study",
                "required": True,
            },
            "polarity": {
                "dtype": str,
                "description": "Ion polarity mode",
                "default": "positive",
                "allowed_values": ["positive", "negative", "pos", "neg"],
            },
            "num_cores": {
                "dtype": int,
                "description": "Number of CPU cores to use",
                "default": 4,
                "min_value": 1,
                "max_value": multiprocessing.cpu_count(),
            },
            "batch_size": {
                "dtype": int,
                "description": "Number of files to process per batch",
                "default": 8,
                "min_value": 1,
                "max_value": 32,
            },
            "memory_limit_gb": {
                "dtype": float,
                "description": "Memory limit for processing (GB)",
                "default": 16.0,
                "min_value": 1.0,
                "max_value": 128.0,
            },
        },
        repr=False,
    )
    
    def __post_init__(self):
        """Set polarity-specific defaults after initialization."""
        # Set default adducts based on polarity if not provided
        if not self.adducts:
            if self.polarity.lower() in ["positive", "pos"]:
                self.adducts = ["H:+:0.8", "Na:+:0.1", "NH4:+:0.1"]
            elif self.polarity.lower() in ["negative", "neg"]: 
                self.adducts = ["H-1:-:1.0", "CH2O2:0:0.5"]
            else:
                # Default to positive
                self.adducts = ["H:+:0.8", "Na:+:0.1", "NH4:+:0.1"]
        
        # Validate num_cores
        max_cores = multiprocessing.cpu_count()
        if self.num_cores <= 0:
            self.num_cores = max_cores
        elif self.num_cores > max_cores:
            self.num_cores = max_cores
            
        # Ensure paths are absolute
        if self.data_source:
            self.data_source = os.path.abspath(self.data_source)
        if self.study_folder:
            self.study_folder = os.path.abspath(self.study_folder)


class Wizard:
    """
    Automated processing wizard for mass spectrometry studies.
    
    The Wizard class provides end-to-end automation for processing collections
    of mass spectrometry files from raw data to final study results, including:
    
    1. Raw data discovery and batch conversion to sample5 format
    2. Automatic detector type detection and parameter optimization
    3. Study assembly with feature alignment and merging 
    4. Automated plot generation and result export
    5. Intelligent resume capability for interrupted processes
    6. Adaptive optimization based on study size and system resources
    
    The wizard automatically detects the type of MS detector using simplified rules:
    - .raw files: Assume Orbitrap (noise threshold = 1e5)
    - .wiff files: Assume Quadrupole (noise threshold = 200)
    - .mzML files: Check metadata for Orbitrap detection
    
    The wizard handles the complete workflow with minimal user intervention
    while providing comprehensive logging and progress tracking.
    """
    
    def __init__(
        self,
        data_source: str = "",
        study_folder: str = "",  
        polarity: str = "positive",
        adducts: Optional[List[str]] = None,
        num_cores: int = 4,
        **kwargs
    ):
        """
        Initialize the Wizard for automated study processing.
        
        Parameters:
            data_source: Directory containing raw data files
            study_folder: Output directory for processed study
            polarity: Ion polarity mode ("positive" or "negative")
            adducts: List of adduct specifications (auto-set if None)
            num_cores: Number of CPU cores for parallel processing
            **kwargs: Additional parameters (see wizard_def for full list)
        """
        
        # Auto-detect optimal number of cores (75% of total)
        if num_cores <= 0:
            num_cores = max(1, int(multiprocessing.cpu_count() * 0.75))
            
        # Create parameters instance
        if "params" in kwargs and isinstance(kwargs["params"], wizard_def):
            self.params = kwargs.pop("params")
        else:
            # Create default parameters and update with provided values
            self.params = wizard_def(
                data_source=data_source,
                study_folder=study_folder,
                polarity=polarity,
                num_cores=num_cores
            )
            
            if adducts is not None:
                self.params.adducts = adducts
            
            # Update with any additional parameters
            for key, value in kwargs.items():
                if hasattr(self.params, key):
                    setattr(self.params, key, value)
        
        # Validate required parameters
        if not self.params.data_source:
            raise ValueError("data_source is required")
        if not self.params.study_folder:
            raise ValueError("study_folder is required")
        
        # Create directories
        self.data_source_path = Path(self.params.data_source)
        self.study_folder_path = Path(self.params.study_folder) 
        self.study_folder_path.mkdir(parents=True, exist_ok=True)
        
        # Auto-infer polarity from the first file if not explicitly set by user
        if polarity == "positive" and "polarity" not in kwargs:
            inferred_polarity = self._infer_polarity_from_first_file()
            if inferred_polarity:
                self.params.polarity = inferred_polarity
                # Update adducts based on inferred polarity  
                self.params.__post_init__()
        
        # Setup logging
        self._setup_logging()
        
        # Initialize state tracking
        self.processed_files = []
        self.failed_files = []
        self.study = None
        self.start_time = None
        self.current_step = "initialized"
        
        # Create checkpoint file path
        self.checkpoint_file = self.study_folder_path / "wizard_checkpoint.json"
        
        self.logger.info(f"Wizard initialized for {self.polarity} mode")
        self.logger.info(f"Data source: {self.data_source_path}")
        self.logger.info(f"Study folder: {self.study_folder_path}")
        self.logger.info(f"Using {self.params.num_cores} CPU cores")
        
        # Load checkpoint if resuming
        if self.params.resume_enabled:
            self._load_checkpoint()
    
    def _infer_polarity_from_first_file(self) -> str:
        """
        Infer polarity from the first available raw data file.
        
        Returns:
            Inferred polarity string ("positive" or "negative") or None if detection fails
        """
        try:
            # Find first file
            for extension in ['.wiff', '.raw', '.mzML', '.d']:
                pattern = f"**/*{extension}" if True else f"*{extension}"  # search_subfolders=True
                files = list(self.data_source_path.rglob(pattern))
                if files:
                    first_file = files[0]
                    break
            else:
                return None
            
            # Only implement for .wiff files initially (most common format)
            if first_file.suffix.lower() == '.wiff':
                from masster.sample.load import _wiff_to_dict
                
                # Extract metadata from first file
                metadata_df = _wiff_to_dict(str(first_file))
                
                if not metadata_df.empty and 'polarity' in metadata_df.columns:
                    # Get polarity from first experiment  
                    first_polarity = metadata_df['polarity'].iloc[0]
                    
                    # Convert numeric polarity codes to string
                    if first_polarity == 1 or str(first_polarity).lower() in ['positive', 'pos', '+']:
                        return "positive"
                    elif first_polarity == -1 or str(first_polarity).lower() in ['negative', 'neg', '-']:
                        return "negative"
                    
        except Exception:
            # Silently fall back to default if inference fails
            pass
            
        return None
    
    @property
    def polarity(self) -> str:
        """Get the polarity setting."""
        return self.params.polarity
    
    @property 
    def adducts(self) -> List[str]:
        """Get the adducts list."""
        return self.params.adducts
    
    def _reload(self):
        """
        Reloads all masster modules to pick up any changes to their source code,
        and updates the instance's class reference to the newly reloaded class version.
        This ensures that the instance uses the latest implementation without restarting the interpreter.
        """
        # Reset logger configuration flags to allow proper reconfiguration after reload
        try:
            import masster.logger as logger_module

            if hasattr(logger_module, "_WIZARD_LOGGER_CONFIGURED"):
                logger_module._WIZARD_LOGGER_CONFIGURED = False
        except Exception:
            pass

        # Get the base module name (masster)
        base_modname = self.__class__.__module__.split(".")[0]
        current_module = self.__class__.__module__

        # Dynamically find all wizard submodules
        wizard_modules = []
        wizard_module_prefix = f"{base_modname}.wizard."

        # Get all currently loaded modules that are part of the wizard package
        for module_name in sys.modules:
            if (
                module_name.startswith(wizard_module_prefix)
                and module_name != current_module
            ):
                wizard_modules.append(module_name)

        # Add core masster modules
        core_modules = [
            f"{base_modname}._version",
            f"{base_modname}.chromatogram",
            f"{base_modname}.spectrum",
            f"{base_modname}.logger",
        ]

        # Add sample submodules
        sample_modules = []
        sample_module_prefix = f"{base_modname}.sample."
        for module_name in sys.modules:
            if (
                module_name.startswith(sample_module_prefix)
                and module_name != current_module
            ):
                sample_modules.append(module_name)

        # Add study submodules
        study_modules = []
        study_module_prefix = f"{base_modname}.study."
        for module_name in sys.modules:
            if (
                module_name.startswith(study_module_prefix)
                and module_name != current_module
            ):
                study_modules.append(module_name)

        all_modules_to_reload = (
            core_modules + wizard_modules + sample_modules + study_modules
        )

        # Reload all discovered modules
        for full_module_name in all_modules_to_reload:
            try:
                if full_module_name in sys.modules:
                    mod = sys.modules[full_module_name]
                    importlib.reload(mod)
                    self.logger.debug(f"Reloaded module: {full_module_name}")
            except Exception as e:
                self.logger.warning(f"Failed to reload module {full_module_name}: {e}")

        # Finally, reload the current module (wizard.py)
        try:
            mod = __import__(current_module, fromlist=[current_module.split(".")[0]])
            importlib.reload(mod)

            # Get the updated class reference from the reloaded module
            new = getattr(mod, self.__class__.__name__)
            # Update the class reference of the instance
            self.__class__ = new

            self.logger.debug("Module reload completed")
        except Exception as e:
            self.logger.error(f"Failed to reload current module {current_module}: {e}")
        
    def _setup_logging(self):
        """Setup comprehensive logging system."""
        # Create logger
        log_label = f"Wizard-{self.polarity}"
        
        if self.params.log_to_file:
            log_file = self.study_folder_path / "wizard.log"
            sink = str(log_file)
        else:
            sink = "sys.stdout"
            
        self.logger = MassterLogger(
            instance_type="wizard",
            level=self.params.log_level.upper(),
            label=log_label,
            sink=sink,
        )
        
        # Also create a simple file logger for critical info
        self.log_file = self.study_folder_path / "processing.log"
        
    def _log_progress(self, message: str, level: str = "INFO"):
        """Log progress message with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_message = f"[{timestamp}] {message}"
        
        # Log to masster logger
        getattr(self.logger, level.lower())(message)
        
        # Also write to simple log file
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"{full_message}\n")
            
        if self.params.verbose_progress and level in ["INFO", "WARNING", "ERROR"]:
            print(full_message)
    
    def _save_checkpoint(self):
        """Save processing checkpoint for resume capability."""
        if not self.params.resume_enabled:
            return
            
        import json
        checkpoint_data = {
            "timestamp": datetime.now().isoformat(),
            "current_step": self.current_step,
            "processed_files": self.processed_files,
            "failed_files": self.failed_files,
            "params": {
                "data_source": self.params.data_source,
                "study_folder": self.params.study_folder,
                "polarity": self.params.polarity,
                "adducts": self.params.adducts,
                "num_cores": self.params.num_cores,
            }
        }
        
        try:
            with open(self.checkpoint_file, "w") as f:
                json.dump(checkpoint_data, f, indent=2)
            self.logger.debug(f"Checkpoint saved: {len(self.processed_files)} files processed")
        except Exception as e:
            self.logger.warning(f"Failed to save checkpoint: {e}")
    
    def _load_checkpoint(self):
        """Load processing checkpoint for resume capability."""
        if not self.checkpoint_file.exists():
            return
            
        import json
        try:
            with open(self.checkpoint_file, "r") as f:
                checkpoint_data = json.load(f)
            
            self.processed_files = checkpoint_data.get("processed_files", [])
            self.failed_files = checkpoint_data.get("failed_files", [])
            self.current_step = checkpoint_data.get("current_step", "initialized")
            
            self.logger.info(f"Resuming from checkpoint: {len(self.processed_files)} files already processed")
            self.logger.info(f"Previous step: {self.current_step}")
            
        except Exception as e:
            self.logger.warning(f"Failed to load checkpoint: {e}")
            self.processed_files = []
            self.failed_files = []
    
    def discover_files(self) -> List[Path]:
        """
        Discover raw data files in the source directory.
        
        Returns:
            List of file paths found for processing
        """
        self._log_progress("Discovering raw data files...")
        self.current_step = "discovering_files"
        
        found_files = []
        
        for extension in self.params.file_extensions:
            if self.params.search_subfolders:
                pattern = f"**/*{extension}"
                files = list(self.data_source_path.rglob(pattern))
            else:
                pattern = f"*{extension}"
                files = list(self.data_source_path.glob(pattern))
            
            # Filter out files matching skip patterns
            filtered_files = []
            for file_path in files:
                skip_file = False
                for pattern in self.params.skip_patterns:
                    if pattern.lower() in file_path.name.lower():
                        skip_file = True
                        self.logger.debug(f"Skipping file (matches pattern '{pattern}'): {file_path.name}")
                        break
                
                if not skip_file:
                    # Check file size
                    try:
                        file_size_gb = file_path.stat().st_size / (1024**3)
                        if file_size_gb > self.params.max_file_size_gb:
                            self.logger.warning(f"Large file ({file_size_gb:.1f}GB): {file_path.name}")
                        filtered_files.append(file_path)
                    except Exception as e:
                        self.logger.warning(f"Could not check file size for {file_path}: {e}")
                        filtered_files.append(file_path)
            
            found_files.extend(filtered_files)
            self.logger.info(f"Found {len(filtered_files)} {extension} files")
        
        # Remove duplicates and sort
        found_files = sorted(list(set(found_files)))
        
        self._log_progress(f"Total files discovered: {len(found_files)}")
        
        return found_files
    
    def _process_single_file(self, file_path: Path, reset: bool = False) -> Optional[str]:
        """
        Process a single file to sample5 format.
        
        This method replicates the core processing from parallel_sample_processing.py
        but with wizard-specific configuration and error handling.
        
        Parameters:
            file_path: Path to the raw data file
            reset: Force reprocessing even if output exists
        
        Returns:
            Base filename of output on success, None on failure
        """
        import gc
        
        # Generate output filename
        file_out = file_path.stem + '.sample5'
        output_file = self.study_folder_path / file_out
        
        # Initialize masster Sample with delayed import
        import masster
        sample = masster.Sample(
            log_label=file_path.name,
            log_level='ERROR'  # Reduce logging overhead in parallel processing
        )
        
        # Check if file should be skipped
        skip = False
        if not reset and not self.params.force_reprocess and output_file.exists():
            try:
                # Attempt to load existing processed file to verify it's valid
                sample.load(str(output_file))
                skip = True
            except Exception:
                # If loading fails, file needs to be reprocessed
                skip = False
        
        if skip:
            self.logger.debug(f"Skipping {file_path.name} (already processed)")
            return output_file.stem
        
        self.logger.info(f"Processing {file_path.name}")
        
        try:
            # STEP 1: Load raw data
            sample.load(str(file_path))
            
            # STEP 2: Feature detection - First pass (strict parameters)
            sample.find_features(
                chrom_fwhm=self.params.chrom_fwhm,
                noise=self.params.noise_threshold,
                tol_ppm=self.params.tol_ppm,
                chrom_peak_snr=self.params.chrom_peak_snr,
                min_trace_length_multiplier=0.5,
                chrom_fwhm_min=self.params.chrom_fwhm
            )
            
            # STEP 3: Feature detection - Second pass (relaxed parameters)
            sample.find_features(
                chrom_peak_snr=self.params.chrom_peak_snr,
                noise=self.params.noise_threshold / 10,  # Lower noise threshold
                chrom_fwhm=2.0  # Wider peaks
            )
            
            # STEP 3.5: Validate feature detection results
            if not hasattr(sample, 'features_df') or sample.features_df is None or len(sample.features_df) == 0:
                self.logger.warning(f"No features detected in {file_path.name} - skipping additional processing")
                # Still save the sample5 file for record keeping
                sample.save(filename=str(output_file))
                return output_file.stem
            
            self.logger.info(f"Detected {len(sample.features_df)} features in {file_path.name}")
            
            # STEP 4: Adduct detection
            sample.find_adducts(adducts=self.adducts)
            
            # STEP 5: MS2 spectrum identification
            sample.find_ms2()
            
            # STEP 6: Save processed data
            sample.save(filename=str(output_file))
            
            # STEP 7: Generate additional outputs (only for samples with features)
            # Skip CSV export and individual MGF export as requested
            
            if self.params.generate_plots:
                plot_file = output_file.parent / (output_file.stem + "_2d.html")
                sample.plot_2d(filename=str(plot_file), markersize=4)
            
            # Memory cleanup
            result = output_file.stem
            del sample
            gc.collect()
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing {file_path.name}: {e}")
            # Cleanup on error
            gc.collect()
            return None
    
    def _process_batch(self, file_batch: List[Path]) -> List[str]:
        """Process a batch of files in a single worker."""
        results = []
        for file_path in file_batch:
            result = self._process_single_file(file_path)
            if result:
                results.append(result)
            else:
                results.append(None)
        return results
    
    def convert_to_sample5(self, file_list: Optional[List[Path]] = None) -> bool:
        """
        Convert raw data files to sample5 format in parallel.
        
        Parameters:
            file_list: List of files to process (None to discover automatically)
        
        Returns:
            True if conversion completed successfully
        """
        self._log_progress("=== Starting Sample5 Conversion ===")
        self.current_step = "converting_to_sample5"
        
        if file_list is None:
            file_list = self.discover_files()
        
        if not file_list:
            self.logger.warning("No files found for conversion")
            return False
        
        # Detect detector type and adjust parameters before processing
        detector_type = self._detect_detector_type()
        self._adjust_parameters_for_detector(detector_type)
        
        # Filter out already processed files if resuming
        if self.params.resume_enabled and self.processed_files:
            remaining_files = []
            for file_path in file_list:
                if str(file_path) not in self.processed_files:
                    remaining_files.append(file_path)
            file_list = remaining_files
            
            if not file_list:
                self._log_progress("All files already processed")
                return True
        
        self._log_progress(f"Converting {len(file_list)} files to sample5 format")
        
        conversion_start = time.time()
        successful_count = 0
        failed_count = 0
        
        if self.params.use_process_pool:
            # ProcessPoolExecutor approach - better for CPU-intensive work
            if len(file_list) <= self.params.batch_size:
                # Few files: process individually
                self.logger.info(f"Processing {len(file_list)} files individually with {self.params.num_cores} workers")
                
                with concurrent.futures.ProcessPoolExecutor(max_workers=self.params.num_cores) as executor:
                    futures = [
                        executor.submit(self._process_single_file, file_path)
                        for file_path in file_list
                    ]
                    
                    for i, future in enumerate(concurrent.futures.as_completed(futures)):
                        result = future.result()
                        if result:
                            successful_count += 1
                            self.processed_files.append(str(file_list[i]))
                        else:
                            failed_count += 1
                            self.failed_files.append(str(file_list[i]))
                        
                        # Progress update and checkpoint
                        if (successful_count + failed_count) % self.params.checkpoint_interval == 0:
                            progress = (successful_count + failed_count) / len(file_list) * 100
                            self._log_progress(f"Progress: {progress:.1f}% ({successful_count} successful, {failed_count} failed)")
                            self._save_checkpoint()
            
            else:
                # Many files: process in batches
                batches = [
                    file_list[i:i + self.params.batch_size]
                    for i in range(0, len(file_list), self.params.batch_size)
                ]
                
                self.logger.info(f"Processing {len(file_list)} files in {len(batches)} batches")
                
                with concurrent.futures.ProcessPoolExecutor(max_workers=self.params.num_cores) as executor:
                    futures = [executor.submit(self._process_batch, batch) for batch in batches]
                    
                    for batch_idx, future in enumerate(concurrent.futures.as_completed(futures)):
                        batch_results = future.result()
                        batch = batches[batch_idx]
                        
                        for i, result in enumerate(batch_results):
                            if result:
                                successful_count += 1
                                self.processed_files.append(str(batch[i]))
                            else:
                                failed_count += 1
                                self.failed_files.append(str(batch[i]))
                        
                        # Progress update
                        progress = (successful_count + failed_count) / len(file_list) * 100
                        self._log_progress(f"Batch {batch_idx + 1}/{len(batches)} complete. Progress: {progress:.1f}%")
                        self._save_checkpoint()
        
        else:
            # ThreadPoolExecutor approach
            self.logger.info(f"Processing {len(file_list)} files with {self.params.num_cores} threads")
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.params.num_cores) as executor:
                futures = [
                    executor.submit(self._process_single_file, file_path)
                    for file_path in file_list
                ]
                
                for i, future in enumerate(concurrent.futures.as_completed(futures)):
                    result = future.result()
                    if result:
                        successful_count += 1
                        self.processed_files.append(str(file_list[i]))
                    else:
                        failed_count += 1
                        self.failed_files.append(str(file_list[i]))
                    
                    if (successful_count + failed_count) % self.params.checkpoint_interval == 0:
                        progress = (successful_count + failed_count) / len(file_list) * 100
                        self._log_progress(f"Progress: {progress:.1f}%")
                        self._save_checkpoint()
        
        conversion_time = time.time() - conversion_start
        
        self._log_progress("=== Sample5 Conversion Complete ===")
        self._log_progress(f"Successful: {successful_count}")
        self._log_progress(f"Failed: {failed_count}")
        self._log_progress(f"Total time: {conversion_time:.1f} seconds")
        
        if failed_count > 0:
            self.logger.warning(f"{failed_count} files failed to process")
            for failed_file in self.failed_files[-failed_count:]:
                self.logger.warning(f"Failed: {failed_file}")
        
        self._save_checkpoint()
        return successful_count > 0
    
    def _detect_detector_type(self) -> str:
        """
        Detect the type of MS detector from the first available file.
        
        Simplified detection rules:
        - .raw files: Assume Orbitrap (Thermo instruments)
        - .wiff files: Assume Quadrupole (SCIEX instruments)  
        - .mzML files: Check metadata for Orbitrap detection
        
        Returns:
            String indicating detector type ("orbitrap", "quadrupole", "unknown")
        """
        try:
            # Find first raw file to analyze
            for extension in ['.raw', '.wiff', '.mzML', '.d']:
                if self.params.search_subfolders:
                    pattern = f"**/*{extension}"
                    files = list(self.data_source_path.rglob(pattern))
                else:
                    pattern = f"*{extension}"
                    files = list(self.data_source_path.glob(pattern))
                if files:
                    first_file = files[0]
                    break
            else:
                self.logger.warning("No raw files found for detector detection")
                return "unknown"
            
            self.logger.info(f"Detecting detector type from: {first_file.name}")
            
            # Simplified detection rules
            if first_file.suffix.lower() == '.raw':
                # RAW files are Thermo -> assume Orbitrap
                detector_type = "orbitrap"
                self.logger.info("Detected .raw file -> Thermo Orbitrap detector")
                return detector_type
                
            elif first_file.suffix.lower() in ['.wiff', '.wiff2']:
                # WIFF files are SCIEX -> assume Quadrupole
                detector_type = "quadrupole"
                self.logger.info("Detected .wiff file -> SCIEX Quadrupole detector")
                return detector_type
            
            elif first_file.suffix.lower() == '.mzml':
                # For mzML files, check metadata for Orbitrap detection
                try:
                    import warnings
                    with warnings.catch_warnings():
                        warnings.filterwarnings("ignore", message="Warning: OPENMS_DATA_PATH environment variable already exists.*", category=UserWarning)
                        import pyopenms as oms
                    
                    exp = oms.MSExperiment()
                    oms.MzMLFile().load(str(first_file), exp)
                    
                    # Check instrument metadata for Orbitrap keywords
                    instrument_info = []
                    if hasattr(exp, 'getExperimentalSettings'):
                        settings = exp.getExperimentalSettings()
                        if hasattr(settings, 'getInstrument'):
                            instrument = settings.getInstrument()
                            if hasattr(instrument, 'getName'):
                                name = instrument.getName().decode() if hasattr(instrument.getName(), 'decode') else str(instrument.getName())
                                instrument_info.append(name.lower())
                            if hasattr(instrument, 'getModel'):
                                model = instrument.getModel().decode() if hasattr(instrument.getModel(), 'decode') else str(instrument.getModel())
                                instrument_info.append(model.lower())
                    
                    # Check for Orbitrap keywords in instrument info
                    orbitrap_keywords = ['orbitrap', 'exactive', 'q-exactive', 'exploris', 'fusion', 'lumos', 'velos', 'elite']
                    instrument_text = ' '.join(instrument_info)
                    
                    if any(keyword in instrument_text for keyword in orbitrap_keywords):
                        detector_type = "orbitrap"
                        self.logger.info(f"Detected mzML with Orbitrap instrument: {instrument_text}")
                    else:
                        detector_type = "unknown"
                        self.logger.info(f"Detected mzML with unknown instrument: {instrument_text}")
                    
                    return detector_type
                        
                except Exception as e:
                    self.logger.warning(f"Failed to analyze mzML file for detector type: {e}")
                    return "unknown"
        
        except Exception as e:
            self.logger.warning(f"Detector type detection failed: {e}")
        
        return "unknown"
    
    def _adjust_parameters_for_detector(self, detector_type: str):
        """
        Adjust processing parameters based on detected detector type.
        
        Simplified rules:
        - "orbitrap": Use 1e5 noise threshold (high background noise)
        - "quadrupole": Use 200 noise threshold (default, lower noise)
        - "unknown": Use 200 noise threshold (default)
        
        Parameters:
            detector_type: Type of detector detected ("orbitrap", "quadrupole", "unknown")
        """
        original_noise = self.params.noise_threshold
        self.params.detector_type = detector_type  # Store the detected type
        
        if detector_type == "orbitrap":
            # Orbitraps have much higher background noise, use 1e5 threshold
            self.params.noise_threshold = 1e5
            self._log_progress(f"Detector: Orbitrap detected - adjusted noise threshold: {original_noise} -> {self.params.noise_threshold}")
            
        elif detector_type == "quadrupole":
            # Quadrupole instruments have lower noise, use default threshold
            self.params.noise_threshold = 200.0
            self._log_progress(f"Detector: Quadrupole detected - noise threshold: {self.params.noise_threshold}")
            
        else:
            # Unknown detector type, keep default
            self.params.noise_threshold = 200.0
            self._log_progress(f"Detector: Unknown type detected - using default noise threshold: {self.params.noise_threshold}")
    
    def assemble_study(self) -> bool:
        """
        Assemble processed sample5 files into a study.
        
        Returns:
            True if study assembly was successful
        """
        self._log_progress("=== Starting Study Assembly ===")
        self.current_step = "assembling_study"
        
        # Find all sample5 files
        sample5_files = list(self.study_folder_path.glob("*.sample5"))
        
        if not sample5_files:
            self.logger.error("No sample5 files found for study assembly")
            return False
        
        self._log_progress(f"Assembling study from {len(sample5_files)} sample5 files")
        
        try:
            # Detect detector type and adjust parameters if needed
            detector_type = self._detect_detector_type()
            self._adjust_parameters_for_detector(detector_type)
            
            # Create study with optimized settings
            import masster
            study_params = study_defaults(
                folder=str(self.study_folder_path),
                polarity=self.polarity,
                log_level="INFO",
                log_label=f"Study-{self.polarity}",
                adducts=self.adducts
            )
            
            self.study = masster.Study(params=study_params)
            
            # Add all sample5 files
            sample5_pattern = str(self.study_folder_path / "*.sample5")
            self.study.add(sample5_pattern)
            
            self._log_progress(f"Added {len(self.study.samples_df)} samples to study")
            
            # Filter features based on quality criteria
            if hasattr(self.study, 'features_filter'):
                initial_features = len(self.study.features_df) if hasattr(self.study, 'features_df') else 0
                
                # Apply feature filtering
                feature_selection = self.study.features_select(
                    chrom_coherence=0.3,
                    chrom_prominence_scaled=1
                )
                self.study.features_filter(feature_selection)
                
                final_features = len(self.study.features_df) if hasattr(self.study, 'features_df') else 0
                self._log_progress(f"Feature filtering: {initial_features} -> {final_features} features")
            
            self._save_checkpoint()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to assemble study: {e}")
            return False
    
    def align_and_merge(self) -> bool:
        """
        Perform feature alignment and merging.
        
        Returns:
            True if alignment and merging were successful
        """
        self._log_progress("=== Starting Feature Alignment and Merging ===")
        self.current_step = "aligning_and_merging"
        
        if self.study is None:
            self.logger.error("Study not assembled. Run assemble_study() first.")
            return False
        
        try:
            # Determine optimal algorithms based on study size
            num_samples = len(self.study.samples_df)
            
            if num_samples < 500:
                # For smaller studies: use qt for both alignment and merge
                alignment_algorithm = "qt"
                merge_method = "qt"
                self.logger.info(f"Small study ({num_samples} samples) - using qt algorithms")
            else:
                # For larger studies: use kd for alignment and qt-chunked for merge
                alignment_algorithm = "kd"
                merge_method = "qt-chunked"
                self.logger.info(f"Large study ({num_samples} samples) - using kd alignment and qt-chunked merge")
            
            # Align features across samples
            align_params = align_defaults(
                rt_tol=self.params.rt_tolerance,
                mz_max_diff=self.params.mz_max_diff,
                algorithm=alignment_algorithm
            )

            self.logger.info(f"Aligning features with RT tolerance {self.params.rt_tolerance}s, m/z max diff {self.params.mz_max_diff} Da, algorithm: {alignment_algorithm}")
            self.study.align(params=align_params)
            
            # Merge aligned features
            merge_params = merge_defaults(
                method=merge_method,
                rt_tol=self.params.rt_tolerance,
                mz_tol=self.params.mz_max_diff,
                min_samples=self.params.min_samples_for_merge
            )
            
            self.logger.info(f"Merging features using {merge_method} method")
            self.study.merge(params=merge_params)
            
            # Log results
            num_consensus = len(self.study.consensus_df) if hasattr(self.study, 'consensus_df') else 0
            self._log_progress(f"Generated {num_consensus} consensus features")
            
            # Get study info
            if hasattr(self.study, 'info'):
                self.study.info()
            
            self._save_checkpoint()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to align and merge: {e}")
            return False
    
    def generate_plots(self) -> bool:
        """
        Generate visualization plots for the study.
        
        Returns:
            True if plot generation was successful
        """
        if not self.params.generate_plots:
            self._log_progress("Plot generation disabled, skipping...")
            return True
            
        self._log_progress("=== Generating Visualization Plots ===")
        self.current_step = "generating_plots"
        
        if self.study is None:
            self.logger.error("Study not available. Complete previous steps first.")
            return False
        
        try:
            plots_generated = 0
            
            # Alignment plot
            if hasattr(self.study, 'plot_alignment'):
                alignment_plot = self.study_folder_path / "alignment_plot.html"
                self.study.plot_alignment(filename=str(alignment_plot))
                plots_generated += 1
                self.logger.info(f"Generated alignment plot: {alignment_plot}")
            
            # Consensus 2D plot
            if hasattr(self.study, 'plot_consensus_2d'):
                consensus_2d_plot = self.study_folder_path / "consensus_2d.html"
                self.study.plot_consensus_2d(filename=str(consensus_2d_plot))
                plots_generated += 1
                self.logger.info(f"Generated consensus 2D plot: {consensus_2d_plot}")
            
            # PCA plot
            if hasattr(self.study, 'plot_pca'):
                pca_plot = self.study_folder_path / "pca_plot.html"
                self.study.plot_pca(filename=str(pca_plot))
                plots_generated += 1
                self.logger.info(f"Generated PCA plot: {pca_plot}")
            
            # Consensus statistics
            if hasattr(self.study, 'plot_consensus_stats'):
                stats_plot = self.study_folder_path / "consensus_stats.html"
                self.study.plot_consensus_stats(filename=str(stats_plot))
                plots_generated += 1
                self.logger.info(f"Generated statistics plot: {stats_plot}")
            
            self._log_progress(f"Generated {plots_generated} visualization plots")
            self._save_checkpoint()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to generate plots: {e}")
            return False
    
    def export_results(self) -> bool:
        """
        Export study results in requested formats.
        
        Returns:
            True if export was successful
        """
        self._log_progress("=== Exporting Study Results ===")
        self.current_step = "exporting_results"
        
        if self.study is None:
            self.logger.error("Study not available. Complete previous steps first.")
            return False
        
        try:
            exports_completed = 0
            
            # Export consensus features as CSV
            if "csv" in self.params.export_formats:
                csv_file = self.study_folder_path / "consensus_features.csv"
                if hasattr(self.study.consensus_df, 'write_csv'):
                    self.study.consensus_df.write_csv(str(csv_file))
                exports_completed += 1
                self.logger.info(f"Exported CSV: {csv_file}")
            
            # Export as Excel
            if "xlsx" in self.params.export_formats and hasattr(self.study, 'export_xlsx'):
                xlsx_file = self.study_folder_path / "study_results.xlsx"
                self.study.export_xlsx(filename=str(xlsx_file))
                exports_completed += 1
                self.logger.info(f"Exported Excel: {xlsx_file}")
            
            # Export MGF for MS2 spectra
            if "mgf" in self.params.export_formats and hasattr(self.study, 'export_mgf'):
                mgf_file = self.study_folder_path / "consensus_ms2.mgf"
                self.study.export_mgf(filename=str(mgf_file))
                exports_completed += 1
                self.logger.info(f"Exported MGF: {mgf_file}")
            
            # Export as Parquet for efficient storage
            if "parquet" in self.params.export_formats and hasattr(self.study, 'export_parquet'):
                parquet_file = self.study_folder_path / "study_data.parquet"
                self.study.export_parquet(filename=str(parquet_file))
                exports_completed += 1
                self.logger.info(f"Exported Parquet: {parquet_file}")
            
            self._log_progress(f"Completed {exports_completed} exports")
            self._save_checkpoint()
            
            # Always perform additional export methods as requested
            self._export_additional_formats()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export results: {e}")
            return False
    
    def _export_additional_formats(self):
        """Export additional formats: xlsx, parquet, save, and mgf."""
        self.logger.info("=== Exporting Additional Formats ===")
        
        try:
            # Force export xlsx (study results in Excel format)
            xlsx_file = self.study_folder_path / "study_results.xlsx"
            if hasattr(self.study, 'export_xlsx'):
                self.study.export_xlsx(filename=str(xlsx_file))
                self.logger.info(f"Exported Excel: {xlsx_file}")
            
            # Force export parquet (efficient binary format)
            parquet_file = self.study_folder_path / "study_data.parquet" 
            if hasattr(self.study, 'export_parquet'):
                self.study.export_parquet(filename=str(parquet_file))
                self.logger.info(f"Exported Parquet: {parquet_file}")
            
            # Force save the study in study5 format
            study_file = self.study_folder_path / "final_study.study5"
            self.study.save(filename=str(study_file))
            self.logger.info(f"Saved study: {study_file}")
            
            # Force export MGF for MS2 spectra
            mgf_file = self.study_folder_path / "consensus_ms2.mgf"
            if hasattr(self.study, 'export_mgf'):
                self.study.export_mgf(filename=str(mgf_file))
                self.logger.info(f"Exported MGF: {mgf_file}")
            
        except Exception as e:
            self.logger.warning(f"Some additional exports failed: {e}")
    
    def save_study(self) -> bool:
        """
        Save the final study in optimized format.
        
        Returns:
            True if study was saved successfully
        """
        self._log_progress("=== Saving Final Study ===")
        self.current_step = "saving_study"
        
        if self.study is None:
            self.logger.error("Study not available. Complete previous steps first.")
            return False
        
        try:
            study_file = self.study_folder_path / "final_study.study5"
            
            # Determine optimal save format based on study size
            num_samples = len(self.study.samples_df)
            num_features = len(self.study.consensus_df) if hasattr(self.study, 'consensus_df') else 0
            
            if self.params.adaptive_compression:
                # Use compressed format for large studies
                if num_samples > 50 or num_features > 10000:
                    self.logger.info(f"Large study detected ({num_samples} samples, {num_features} features) - using compressed format")
                    self.params.compress_output = True
                else:
                    self.logger.info(f"Small study ({num_samples} samples, {num_features} features) - using standard format")
                    self.params.compress_output = False
            
            # Save study
            if self.params.compress_output and hasattr(self.study, 'save_compressed'):
                self.study.save_compressed(filename=str(study_file))
                self.logger.info(f"Saved compressed study: {study_file}")
            else:
                self.study.save(filename=str(study_file))
                self.logger.info(f"Saved study: {study_file}")
            
            # Save metadata summary
            metadata_file = self.study_folder_path / "study_metadata.txt"
            with open(metadata_file, "w") as f:
                f.write("Study Processing Summary\n")
                f.write("========================\n")
                f.write(f"Processing Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Polarity: {self.polarity}\n")
                f.write(f"Adducts: {', '.join(self.adducts)}\n")
                f.write(f"Number of Samples: {num_samples}\n")
                f.write(f"Number of Consensus Features: {num_features}\n")
                f.write(f"Successful Files: {len(self.processed_files)}\n")
                f.write(f"Failed Files: {len(self.failed_files)}\n")
                f.write(f"RT Tolerance: {self.params.rt_tolerance}s\n")
                f.write(f"m/z Max Diff: {self.params.mz_max_diff} Da\n")
                f.write(f"Merge Method: {self.params.merge_method}\n")
                f.write(f"Processing Time: {self._get_total_processing_time()}\n")
            
            self._log_progress(f"Saved study metadata: {metadata_file}")
            self._save_checkpoint()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save study: {e}")
            return False
    
    def cleanup_temp_files(self) -> bool:
        """
        Clean up temporary files if requested.
        
        Returns:
            True if cleanup was successful
        """
        if not self.params.cleanup_temp_files:
            return True
            
        self._log_progress("=== Cleaning Up Temporary Files ===")
        
        try:
            cleaned_count = 0
            
            # Remove individual sample plots if study plots were generated
            if self.params.generate_plots:
                temp_plots = list(self.study_folder_path.glob("*_2d.html"))
                for plot_file in temp_plots:
                    if plot_file.name not in ["alignment_plot.html", "consensus_2d.html", "pca_plot.html"]:
                        plot_file.unlink()
                        cleaned_count += 1
            
            # Remove checkpoint file
            if self.checkpoint_file.exists():
                self.checkpoint_file.unlink()
                cleaned_count += 1
            
            self._log_progress(f"Cleaned up {cleaned_count} temporary files")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup temp files: {e}")
            return False
    
    def run_full_pipeline(self) -> bool:
        """
        Run the complete automated processing pipeline.
        
        This method executes all processing steps in sequence:
        1. Convert raw files to sample5 format
        2. Assemble study from sample5 files
        3. Align and merge features
        4. Generate visualization plots
        5. Export results in requested formats
        6. Save final study
        7. Clean up temporary files
        
        Returns:
            True if the entire pipeline completed successfully
        """
        self._log_progress("=" * 60)
        self._log_progress("STARTING AUTOMATED STUDY PROCESSING PIPELINE")
        self._log_progress("=" * 60)
        
        self.start_time = time.time()
        pipeline_success = True
        
        try:
            # Step 1: Convert to sample5
            if not self.convert_to_sample5():
                self.logger.error("Sample5 conversion failed")
                return False
            
            # Step 2: Assemble study
            if not self.assemble_study():
                self.logger.error("Study assembly failed")
                return False
            
            # Step 3: Align and merge
            if not self.align_and_merge():
                self.logger.error("Feature alignment and merging failed")
                return False
            
            # Step 4: Generate plots
            if not self.generate_plots():
                self.logger.warning("Plot generation failed, continuing...")
                pipeline_success = False
            
            # Step 5: Export results
            if not self.export_results():
                self.logger.warning("Result export failed, continuing...")
                pipeline_success = False
            
            # Step 6: Save study
            if not self.save_study():
                self.logger.error("Study saving failed")
                return False
            
            # Step 7: Cleanup
            if not self.cleanup_temp_files():
                self.logger.warning("Cleanup failed, continuing...")
            
            # Final summary
            total_time = time.time() - self.start_time
            self._log_progress("=" * 60)
            self._log_progress("PIPELINE COMPLETED SUCCESSFULLY")
            self._log_progress(f"Total processing time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")
            self._log_progress(f"Files processed: {len(self.processed_files)}")
            self._log_progress(f"Files failed: {len(self.failed_files)}")
            if hasattr(self.study, 'consensus_df'):
                self._log_progress(f"Consensus features: {len(self.study.consensus_df)}")
            self._log_progress("=" * 60)
            
            return pipeline_success
            
        except KeyboardInterrupt:
            self.logger.info("Pipeline interrupted by user")
            self._save_checkpoint()
            return False
        except Exception as e:
            self.logger.error(f"Pipeline failed with unexpected error: {e}")
            self._save_checkpoint()
            return False
    
    def _get_total_processing_time(self) -> str:
        """Get formatted total processing time."""
        if self.start_time is None:
            return "Unknown"
        
        total_seconds = time.time() - self.start_time
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current processing status.
        
        Returns:
            Dictionary with current status information
        """
        return {
            "current_step": self.current_step,
            "processed_files": len(self.processed_files),
            "failed_files": len(self.failed_files),
            "study_loaded": self.study is not None,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "processing_time": self._get_total_processing_time(),
            "parameters": {
                "data_source": self.params.data_source,
                "study_folder": self.params.study_folder,
                "polarity": self.params.polarity,
                "num_cores": self.params.num_cores,
                "adducts": self.params.adducts,
            }
        }
    
    def execute(self) -> bool:
        """
        Execute the complete automated processing pipeline.
        
        This is a convenience method that runs the full pipeline with the wizard's
        current configuration. It performs standalone analysis of the samples/studies
        as proposed by the Wizard.
        
        Returns:
            True if execution completed successfully, False otherwise
        """
        self._log_progress("Executing Wizard automated processing...")
        return self.run_full_pipeline()
    
    def export_script(self, filename: str) -> bool:
        """
        Generate a Python script that replicates the wizard's processing steps.
        
        Creates a standalone Python script that can be executed independently
        to perform the same analysis as the wizard with the current configuration.
        The script will be saved in the study folder.
        
        This is useful for:
        - Creating reproducible analysis scripts
        - Customizing processing steps
        - Running analysis in different environments
        - Batch processing automation
        
        Parameters:
            filename: Filename for the script (should end with .py). Script will be saved in the study folder.
        
        Returns:
            True if script was generated successfully, False otherwise
        """
        self._log_progress("Generating analysis script...")
        
        try:
            # Ensure the filename is just a filename, not a full path
            script_filename = Path(filename).name
            if not script_filename.endswith('.py'):
                script_filename = script_filename.replace(Path(script_filename).suffix, '') + '.py'
            
            # Place the script in the study folder
            script_path = self.study_folder_path / script_filename
            
            # Generate the script content
            script_content = self._generate_script_content()
            
            # Write the script
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)

            self._log_progress(f"Analysis script saved: {os.path.abspath(script_path)}")
            self.logger.info(f"Generated standalone analysis script: {os.path.abspath(script_path)}")

            return True
            
        except Exception as e:
            self.logger.error(f"Failed to generate script: {e}")
            return False
    
    def to_script(self, filename: str) -> bool:
        """
        [DEPRECATED] Use export_script() instead.
        
        Backward compatibility alias for export_script().
        """
        return self.export_script(filename)
    
    def _generate_script_content(self) -> str:
        """
        Generate the content for the standalone analysis script.
        
        Returns:
            Complete Python script content as string
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create script header
        script_lines = [
            '#!/usr/bin/env python3',
            '"""',
            'Standalone Mass Spectrometry Analysis Script',
            f'Generated by masster.Wizard on {timestamp}',
            '',
            'This script replicates the automated processing pipeline configured',
            'in the Wizard with the following settings:',
            f'- Data Source: {self.params.data_source.replace(chr(92), chr(92)*2)}',
            f'- Study Folder: {self.params.study_folder.replace(chr(92), chr(92)*2)}',
            f'- Polarity: {self.params.polarity}',
            f'- Number of Cores: {self.params.num_cores}',
            f'- Adducts: {", ".join(self.params.adducts)}',
            f'- RT Tolerance: {self.params.rt_tolerance}s',
            f'- m/z Max Diff: {self.params.mz_max_diff} Da',
            f'- Merge Method: {self.params.merge_method}',
            '"""',
            '',
            'import os',
            'import sys',
            'import time',
            'import multiprocessing',
            'from pathlib import Path',
            'from typing import List, Optional',
            'import concurrent.futures',
            'from datetime import datetime',
            '',
            '# Add error handling for masster import',
            '# First, try to add the masster directory to the Python path',
            'try:',
            '    # Try to find masster by looking for it in common development locations',
            '    possible_paths = [',
            '        Path(__file__).parent.parent,  # Script is in masster subfolder',
            '        Path(__file__).parent.parent.parent,  # Script is in study folder', 
            '        Path(os.getcwd()),  # Current working directory',
            '        Path(os.getcwd()).parent,  # Parent of current directory',
            '        Path(r"D:\\SW\\massistant"),  # Specific development path',
            '        Path.home() / "massistant",  # Home directory',
            '        Path.home() / "SW" / "massistant",  # Common dev location',
            '    ]',
            '    ',
            '    masster_found = False',
            '    for possible_path in possible_paths:',
            '        masster_dir = possible_path / "masster"',
            '        if masster_dir.exists() and (masster_dir / "__init__.py").exists():',
            '            if str(possible_path) not in sys.path:',
            '                sys.path.insert(0, str(possible_path))',
            '            masster_found = True',
            '            print(f"Found masster at: {possible_path}")',
            '            break',
            '    ',
            '    if not masster_found:',
            '        # Try adding current directory to path as fallback',
            '        current_dir = Path(os.getcwd())',
            '        if str(current_dir) not in sys.path:',
            '            sys.path.insert(0, str(current_dir))',
            '    ',
            '    import masster',
            'except ImportError as e:',
            '    print(f"Error: masster library not found. {e}")',
            '    print("Please ensure masster is installed or run this script from the masster directory.")',
            '    print("You can install masster with: pip install -e .")',
            '    sys.exit(1)',
            '',
            '',
            'def infer_polarity_from_first_file():',
            '    """Infer polarity from the first available raw data file."""',
            '    try:',
            '        data_source_path = Path(DATA_SOURCE)',
            '        # Find first file',
            '        for extension in [\'.wiff\', \'.raw\', \'.mzML\', \'.d\']:',
            '            pattern = f"**/*{extension}"',
            '            files = list(data_source_path.rglob(pattern))',
            '            if files:',
            '                first_file = files[0]',
            '                break',
            '        else:',
            '            return None',
            '        ',
            '        # Only implement for .wiff files initially',
            '        if first_file.suffix.lower() == \'.wiff\':',
            '            from masster.sample.load import _wiff_to_dict',
            '            ',
            '            # Extract metadata from first file',
            '            metadata_df = _wiff_to_dict(str(first_file))',
            '            ',
            '            if not metadata_df.empty and \'polarity\' in metadata_df.columns:',
            '                # Get polarity from first experiment',
            '                first_polarity = metadata_df[\'polarity\'].iloc[0]',
            '                ',
            '                # Convert numeric polarity codes to string',
            '                if first_polarity == 1 or str(first_polarity).lower() in [\'positive\', \'pos\', \'+\']:',
            '                    return "positive"',
            '                elif first_polarity == -1 or str(first_polarity).lower() in [\'negative\', \'neg\', \'-\']:',
            '                    return "negative"',
            '    except Exception:',
            '        pass',
            '    return None',
            '',
            '',
            '# Configuration Parameters',
            f'DATA_SOURCE = r"{self.params.data_source}"',
            f'STUDY_FOLDER = r"{self.params.study_folder}"',
            '',
            '# Auto-infer polarity from first file, fall back to default',
            'detected_polarity = infer_polarity_from_first_file()',
            f'POLARITY = detected_polarity or "{self.params.polarity}"',
            'NUM_CORES = max(1, int(multiprocessing.cpu_count() * 0.75))  # Auto-detect 75% of cores',
            '',
            '# Set adducts based on detected polarity',
            'if POLARITY.lower() in ["positive", "pos"]:',
            '    ADDUCTS = ["H:+:0.8", "Na:+:0.1", "NH4:+:0.1"]',
            'elif POLARITY.lower() in ["negative", "neg"]:',
            '    ADDUCTS = ["H-1:-:1.0", "CH2O2:0:0.5"]',
            'else:',
            f'    ADDUCTS = {self.params.adducts!r}  # Fall back to original',
            f'RT_TOLERANCE = {self.params.rt_tolerance}',
            f'MZ_TOLERANCE = {self.params.mz_max_diff}',
            f'MERGE_METHOD = "{self.params.merge_method}"',
            f'BATCH_SIZE = {self.params.batch_size}',
            f'CHROM_FWHM = {self.params.chrom_fwhm}',
            f'NOISE_THRESHOLD = {self.params.noise_threshold}',
            f'CHROM_PEAK_SNR = {self.params.chrom_peak_snr}',
            f'TOL_PPM = {self.params.tol_ppm}',
            f'MIN_SAMPLES_FOR_MERGE = {self.params.min_samples_for_merge}',
            '',
            '# File discovery settings',
            "FILE_EXTENSIONS = ['.wiff', '.raw', '.mzML']",
            f'SEARCH_SUBFOLDERS = {self.params.search_subfolders}',
            "SKIP_PATTERNS = []",
            f'MAX_FILE_SIZE_GB = {self.params.max_file_size_gb}',
            '',
            '# Output settings',
            f'GENERATE_PLOTS = {self.params.generate_plots}',
            f'EXPORT_FORMATS = {self.params.export_formats!r}',
            f'COMPRESS_OUTPUT = {self.params.compress_output}',
            f'CLEANUP_TEMP_FILES = {self.params.cleanup_temp_files}',
            '',
            '',
            'def log_progress(message: str):',
            '    """Log progress message with timestamp."""',
            '    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")',
            '    print(f"[{timestamp}] {message}")',
            '',
            '',
            'def discover_files() -> List[Path]:',
            '    """Discover raw data files in the source directory."""',
            '    log_progress("Discovering raw data files...")',
            '    data_source_path = Path(DATA_SOURCE)',
            '    found_files = []',
            '    ',
            '    for extension in FILE_EXTENSIONS:',
            '        if SEARCH_SUBFOLDERS:',
            '            pattern = f"**/*{extension}"',
            '            files = list(data_source_path.rglob(pattern))',
            '        else:',
            '            pattern = f"*{extension}"',
            '            files = list(data_source_path.glob(pattern))',
            '        ',
            '        # Filter out files matching skip patterns',
            '        filtered_files = []',
            '        for file_path in files:',
            '            skip_file = False',
            '            for pattern in SKIP_PATTERNS:',
            '                if pattern.lower() in file_path.name.lower():',
            '                    skip_file = True',
            '                    print(f"Skipping file (matches pattern \'{pattern}\'): {file_path.name}")',
            '                    break',
            '            ',
            '            if not skip_file:',
            '                # Check file size',
            '                try:',
            '                    file_size_gb = file_path.stat().st_size / (1024**3)',
            '                    if file_size_gb > MAX_FILE_SIZE_GB:',
            '                        print(f"Large file ({file_size_gb:.1f}GB): {file_path.name}")',
            '                    filtered_files.append(file_path)',
            '                except Exception as e:',
            '                    print(f"Could not check file size for {file_path}: {e}")',
            '                    filtered_files.append(file_path)',
            '        ',
            '        found_files.extend(filtered_files)',
            '        log_progress(f"Found {len(filtered_files)} {extension} files")',
            '    ',
            '    # Remove duplicates and sort',
            '    found_files = sorted(list(set(found_files)))',
            '    log_progress(f"Total files discovered: {len(found_files)}")',
            '    return found_files',
            '',
            '',
            'def process_single_file(file_path: Path) -> Optional[str]:',
            '    """Process a single file to sample5 format."""',
            '    import gc',
            '    study_folder_path = Path(STUDY_FOLDER)',
            '    ',
            '    # Generate output filename',
            '    file_out = file_path.stem + ".sample5"',
            '    output_file = study_folder_path / file_out',
            '    ',
            '    # Check if file already exists',
            '    if output_file.exists():',
            '        try:',
            '            # Try to load existing file to verify it\'s valid',
            '            sample = masster.Sample(log_level="ERROR")',
            '            sample.load(str(output_file))',
            '            print(f"Skipping {file_path.name} (already processed)")',
            '            return output_file.stem',
            '        except Exception:',
            '            # If loading fails, file needs to be reprocessed',
            '            pass',
            '    ',
            '    print(f"Processing {file_path.name}")',
            '    ',
            '    try:',
            '        # Initialize sample',
            '        sample = masster.Sample(',
            '            log_label=file_path.name,',
            '            log_level="ERROR"  # Reduce logging overhead',
            '        )',
            '        ',
            '        # STEP 1: Load raw data',
            '        sample.load(str(file_path))',
            '        ',
            '        # STEP 2: Feature detection - First pass (strict parameters)',
            '        sample.find_features(',
            '            chrom_fwhm=CHROM_FWHM,',
            '            noise=NOISE_THRESHOLD,',
            '            tol_ppm=TOL_PPM,',
            '            chrom_peak_snr=CHROM_PEAK_SNR,',
            '            min_trace_length_multiplier=0.5,',
            '            chrom_fwhm_min=CHROM_FWHM',
            '        )',
            '        ',
            '        # STEP 3: Feature detection - Second pass (relaxed parameters)',
            '        sample.find_features(',
            '            chrom_peak_snr=CHROM_PEAK_SNR,',
            '            noise=NOISE_THRESHOLD / 10,  # Lower noise threshold',
            '            chrom_fwhm=2.0  # Wider peaks',
            '        )',
            '        ',
            '        # STEP 3.5: Validate feature detection results',
            '        if not hasattr(sample, "features_df") or sample.features_df is None or len(sample.features_df) == 0:',
            '            print(f"WARNING: No features detected in {file_path.name} - skipping additional processing")',
            '            # Still save the sample5 file for record keeping',
            '            sample.save(filename=str(output_file))',
            '            return output_file.stem',
            '        ',
            '        print(f"Detected {len(sample.features_df)} features in {file_path.name}")',
            '        ',
            '        # STEP 4: Adduct detection',
            '        sample.find_adducts(adducts=ADDUCTS)',
            '        ',
            '        # STEP 5: MS2 spectrum identification',
            '        sample.find_ms2()',
            '        ',
            '        # STEP 6: Save processed data',
            '        sample.save(filename=str(output_file))',
            '        ',
            '        # STEP 7: Generate additional outputs (only for samples with features)',
            '        # Skip CSV export and individual MGF export as requested',
            '        ',
            '        if GENERATE_PLOTS:',
            '            plot_file = output_file.parent / (output_file.stem + "_2d.html")',
            '            sample.plot_2d(filename=str(plot_file), markersize=4)',
            '        ',
            '        # Memory cleanup',
            '        result = output_file.stem',
            '        del sample',
            '        gc.collect()',
            '        return result',
            '        ',
            '    except Exception as e:',
            '        print(f"Error processing {file_path.name}: {e}")',
            '        gc.collect()',
            '        return None',
            '',
            '',
            'def convert_to_sample5(file_list: List[Path]) -> bool:',
            '    """Convert raw data files to sample5 format in parallel."""',
            '    log_progress("=== Starting Sample5 Conversion ===")',
            '    log_progress(f"Converting {len(file_list)} files to sample5 format")',
            '    ',
            '    conversion_start = time.time()',
            '    successful_count = 0',
            '    failed_count = 0',
            '    ',
            '    with concurrent.futures.ProcessPoolExecutor(max_workers=NUM_CORES) as executor:',
            '        futures = [executor.submit(process_single_file, file_path) for file_path in file_list]',
            '        ',
            '        for i, future in enumerate(concurrent.futures.as_completed(futures)):',
            '            result = future.result()',
            '            if result:',
            '                successful_count += 1',
            '            else:',
            '                failed_count += 1',
            '            ',
            '            # Progress update',
            '            if (successful_count + failed_count) % 10 == 0:',
            '                progress = (successful_count + failed_count) / len(file_list) * 100',
            '                log_progress(f"Progress: {progress:.1f}% ({successful_count} successful, {failed_count} failed)")',
            '    ',
            '    conversion_time = time.time() - conversion_start',
            '    log_progress("=== Sample5 Conversion Complete ===")',
            '    log_progress(f"Successful: {successful_count}")',
            '    log_progress(f"Failed: {failed_count}")',
            '    log_progress(f"Total time: {conversion_time:.1f} seconds")',
            '    ',
            '    return successful_count > 0',
            '',
            '',
            'def assemble_study() -> masster.Study:',
            '    """Assemble processed sample5 files into a study."""',
            '    log_progress("=== Starting Study Assembly ===")',
            '    study_folder_path = Path(STUDY_FOLDER)',
            '    ',
            '    # Find all sample5 files',
            '    sample5_files = list(study_folder_path.glob("*.sample5"))',
            '    if not sample5_files:',
            '        raise RuntimeError("No sample5 files found for study assembly")',
            '    ',
            '    log_progress(f"Assembling study from {len(sample5_files)} sample5 files")',
            '    ',
            '    # Create study with optimized settings',
            '    from masster.study.defaults.study_def import study_defaults',
            '    study_params = study_defaults(',
            '        folder=str(study_folder_path),',
            '        polarity=POLARITY,',
            '        log_level="INFO",',
            f'        log_label="Study-{self.params.polarity}",',
            '        adducts=ADDUCTS',
            '    )',
            '    ',
            '    study = masster.Study(params=study_params)',
            '    ',
            '    # Add all sample5 files',
            '    sample5_pattern = str(study_folder_path / "*.sample5")',
            '    study.add(sample5_pattern)',
            '    log_progress(f"Added {len(study.samples_df)} samples to study")',
            '    ',
            '    # Filter features based on quality criteria',
            '    if hasattr(study, "features_filter"):',
            '        initial_features = len(study.features_df) if hasattr(study, "features_df") else 0',
            '        feature_selection = study.features_select(',
            '            chrom_coherence=0.3,',
            '            chrom_prominence_scaled=1',
            '        )',
            '        study.features_filter(feature_selection)',
            '        final_features = len(study.features_df) if hasattr(study, "features_df") else 0',
            '        log_progress(f"Feature filtering: {initial_features} -> {final_features} features")',
            '    ',
            '    return study',
            '',
            '',
            'def align_and_merge(study: masster.Study) -> masster.Study:',
            '    """Perform feature alignment and merging."""',
            '    log_progress("=== Starting Feature Alignment and Merging ===")',
            '    ',
            '    # Import alignment and merge defaults',
            '    from masster.study.defaults.align_def import align_defaults',
            '    from masster.study.defaults.merge_def import merge_defaults',
            '    ',
            '    # Determine optimal algorithms based on study size',
            '    num_samples = len(study.samples_df)',
            '    ',
            '    if num_samples < 500:',
            '        # For smaller studies: use qt for both alignment and merge',
            '        alignment_algorithm = "qt"',
            '        merge_method = "qt"',
            '        log_progress(f"Small study ({num_samples} samples) - using qt algorithms")',
            '    else:',
            '        # For larger studies: use kd for alignment and qt-chunked for merge',
            '        alignment_algorithm = "kd"',
            '        merge_method = "qt-chunked"',
            '        log_progress(f"Large study ({num_samples} samples) - using kd alignment and qt-chunked merge")',
            '    ',
            '    # Align features across samples',
            '    align_params = align_defaults(',
            '        rt_tol=RT_TOLERANCE,',
            '        mz_max_diff=MZ_TOLERANCE,',
            '        algorithm=alignment_algorithm',
            '    )',
            '    ',
            '    log_progress(f"Aligning features with RT tolerance {RT_TOLERANCE}s, m/z tolerance {MZ_TOLERANCE} Da, algorithm: {alignment_algorithm}")',
            '    study.align(params=align_params)',
            '    ',
            '    # Merge aligned features',
            '    merge_params = merge_defaults(',
            '        method=merge_method,',
            '        rt_tol=RT_TOLERANCE,',
            '        mz_tol=MZ_TOLERANCE,',
            '        min_samples=MIN_SAMPLES_FOR_MERGE',
            '    )',
            '    ',
            '    log_progress(f"Merging features using {merge_method} method")',
            '    study.merge(params=merge_params)',
            '    ',
            '    # Log results',
            '    num_consensus = len(study.consensus_df) if hasattr(study, "consensus_df") else 0',
            '    log_progress(f"Generated {num_consensus} consensus features")',
            '    ',
            '    # Get study info',
            '    if hasattr(study, "info"):',
            '        study.info()',
            '    ',
            '    return study',
            '',
            '',
            'def generate_plots(study: masster.Study) -> bool:',
            '    """Generate visualization plots for the study."""',
            '    if not GENERATE_PLOTS:',
            '        log_progress("Plot generation disabled, skipping...")',
            '        return True',
            '    ',
            '    log_progress("=== Generating Visualization Plots ===")',
            '    study_folder_path = Path(STUDY_FOLDER)',
            '    plots_generated = 0',
            '    ',
            '    try:',
            '        # Alignment plot',
            '        if hasattr(study, "plot_alignment"):',
            '            alignment_plot = study_folder_path / "alignment_plot.html"',
            '            study.plot_alignment(filename=str(alignment_plot))',
            '            plots_generated += 1',
            '            log_progress(f"Generated alignment plot: {alignment_plot}")',
            '        ',
            '        # Consensus 2D plot',
            '        if hasattr(study, "plot_consensus_2d"):',
            '            consensus_2d_plot = study_folder_path / "consensus_2d.html"',
            '            study.plot_consensus_2d(filename=str(consensus_2d_plot))',
            '            plots_generated += 1',
            '            log_progress(f"Generated consensus 2D plot: {consensus_2d_plot}")',
            '        ',
            '        # PCA plot',
            '        if hasattr(study, "plot_pca"):',
            '            pca_plot = study_folder_path / "pca_plot.html"',
            '            study.plot_pca(filename=str(pca_plot))',
            '            plots_generated += 1',
            '            log_progress(f"Generated PCA plot: {pca_plot}")',
            '        ',
            '        # Consensus statistics',
            '        if hasattr(study, "plot_consensus_stats"):',
            '            stats_plot = study_folder_path / "consensus_stats.html"',
            '            study.plot_consensus_stats(filename=str(stats_plot))',
            '            plots_generated += 1',
            '            log_progress(f"Generated statistics plot: {stats_plot}")',
            '        ',
            '        log_progress(f"Generated {plots_generated} visualization plots")',
            '        return True',
            '        ',
            '    except Exception as e:',
            '        print(f"Failed to generate plots: {e}")',
            '        return False',
            '',
            '',
            'def export_results(study: masster.Study) -> bool:',
            '    """Export study results in requested formats."""',
            '    log_progress("=== Exporting Study Results ===")',
            '    study_folder_path = Path(STUDY_FOLDER)',
            '    exports_completed = 0',
            '    ',
            '    try:',
            '        # Skip CSV export as requested',
            '        ',
            '        # Export as Excel',
            '        if "xlsx" in EXPORT_FORMATS and hasattr(study, "export_xlsx"):',
            '            xlsx_file = study_folder_path / "study_results.xlsx"',
            '            study.export_xlsx(filename=str(xlsx_file))',
            '            exports_completed += 1',
            '            log_progress(f"Exported Excel: {xlsx_file}")',
            '        ',
            '        # Export MGF for MS2 spectra',
            '        if "mgf" in EXPORT_FORMATS and hasattr(study, "export_mgf"):',
            '            mgf_file = study_folder_path / "consensus_ms2.mgf"',
            '            study.export_mgf(filename=str(mgf_file))',
            '            exports_completed += 1',
            '            log_progress(f"Exported MGF: {mgf_file}")',
            '        ',
            '        # Export as Parquet for efficient storage',
            '        if "parquet" in EXPORT_FORMATS and hasattr(study, "export_parquet"):',
            '            parquet_file = study_folder_path / "study_data.parquet"',
            '            study.export_parquet(filename=str(parquet_file))',
            '            exports_completed += 1',
            '            log_progress(f"Exported Parquet: {parquet_file}")',
            '        ',
            '        log_progress(f"Completed {exports_completed} exports")',
            '        ',
            '        # Always perform additional exports as requested',
            '        log_progress("=== Exporting Additional Formats ===")',
            '        ',
            '        try:',
            '            # Force export xlsx (study results in Excel format)',
            '            xlsx_file = study_folder_path / "study_results.xlsx"',
            '            if hasattr(study, "export_xlsx"):',
            '                study.export_xlsx(filename=str(xlsx_file))',
            '                log_progress(f"Exported Excel: {xlsx_file}")',
            '            ',
            '            # Force export parquet (efficient binary format)',
            '            parquet_file = study_folder_path / "study_data.parquet"',
            '            if hasattr(study, "export_parquet"):',
            '                study.export_parquet(filename=str(parquet_file))',
            '                log_progress(f"Exported Parquet: {parquet_file}")',
            '            ',
            '            # Force save the study in study5 format',
            '            study_file = study_folder_path / "final_study.study5"',
            '            study.save(filename=str(study_file))',
            '            log_progress(f"Saved study: {study_file}")',
            '            ',
            '            # Force export MGF for MS2 spectra',
            '            mgf_file = study_folder_path / "consensus_ms2.mgf"',
            '            if hasattr(study, "export_mgf"):',
            '                study.export_mgf(filename=str(mgf_file))',
            '                log_progress(f"Exported MGF: {mgf_file}")',
            '        ',
            '        except Exception as e:',
            '            print(f"Some additional exports failed: {e}")',
            '        ',
            '        return True',
            '        ',
            '    except Exception as e:',
            '        print(f"Failed to export results: {e}")',
            '        return False',
            '',
            '',
            'def save_study(study: masster.Study) -> bool:',
            '    """Save the final study in optimized format."""',
            '    log_progress("=== Saving Final Study ===")',
            '    study_folder_path = Path(STUDY_FOLDER)',
            '    ',
            '    try:',
            '        study_file = study_folder_path / "final_study.study5"',
            '        ',
            '        # Determine optimal save format based on study size',
            '        num_samples = len(study.samples_df)',
            '        num_features = len(study.consensus_df) if hasattr(study, "consensus_df") else 0',
            '        ',
            '        if num_samples > 50 or num_features > 10000:',
            '            log_progress(f"Large study detected ({num_samples} samples, {num_features} features) - using compressed format")',
            '            compress_output = True',
            '        else:',
            '            log_progress(f"Small study ({num_samples} samples, {num_features} features) - using standard format")',
            '            compress_output = False',
            '        ',
            '        # Save study',
            '        if compress_output and hasattr(study, "save_compressed"):',
            '            study.save_compressed(filename=str(study_file))',
            '            log_progress(f"Saved compressed study: {study_file}")',
            '        else:',
            '            study.save(filename=str(study_file))',
            '            log_progress(f"Saved study: {study_file}")',
            '        ',
            '        # Save metadata summary',
            '        metadata_file = study_folder_path / "study_metadata.txt"',
            '        with open(metadata_file, "w") as f:',
            '            f.write("Study Processing Summary\\n")',
            '            f.write("========================\\n")',
            '            f.write(f"Processing Date: {datetime.now().strftime(\'%Y-%m-%d %H:%M:%S\')}\\n")',
            '            f.write(f"Polarity: {POLARITY}\\n")',
            '            f.write(f"Adducts: {\', \'.join(ADDUCTS)}\\n")',
            '            f.write(f"Number of Samples: {num_samples}\\n")',
            '            f.write(f"Number of Consensus Features: {num_features}\\n")',
            '            f.write(f"RT Tolerance: {RT_TOLERANCE}s\\n")',
            '            f.write(f"m/z Tolerance: {MZ_TOLERANCE} Da\\n")',
            '            f.write(f"Merge Method: {MERGE_METHOD}\\n")',
            '        ',
            '        log_progress(f"Saved study metadata: {metadata_file}")',
            '        return True',
            '        ',
            '    except Exception as e:',
            '        print(f"Failed to save study: {e}")',
            '        return False',
            '',
            '',
            'def cleanup_temp_files() -> bool:',
            '    """Clean up temporary files if requested."""',
            '    if not CLEANUP_TEMP_FILES:',
            '        return True',
            '    ',
            '    log_progress("=== Cleaning Up Temporary Files ===")',
            '    study_folder_path = Path(STUDY_FOLDER)',
            '    ',
            '    try:',
            '        cleaned_count = 0',
            '        ',
            '        # Remove individual sample plots if study plots were generated',
            '        if GENERATE_PLOTS:',
            '            temp_plots = list(study_folder_path.glob("*_2d.html"))',
            '            for plot_file in temp_plots:',
            '                if plot_file.name not in ["alignment_plot.html", "consensus_2d.html", "pca_plot.html"]:',
            '                    plot_file.unlink()',
            '                    cleaned_count += 1',
            '        ',
            '        log_progress(f"Cleaned up {cleaned_count} temporary files")',
            '        return True',
            '        ',
            '    except Exception as e:',
            '        print(f"Failed to cleanup temp files: {e}")',
            '        return False',
            '',
            '',
            'def main():',
            '    """Main execution function."""',
            '    print("=" * 70)',
            '    print("AUTOMATED MASS SPECTROMETRY ANALYSIS SCRIPT")',
            f'    print("Generated by masster.Wizard on {timestamp}")',
            '    print("=" * 70)',
            '    ',
            '    start_time = time.time()',
            '    ',
            '    try:',
            '        # Ensure output directory exists',
            '        Path(STUDY_FOLDER).mkdir(parents=True, exist_ok=True)',
            '        ',
            '        # Step 1: Discover files',
            '        file_list = discover_files()',
            '        if not file_list:',
            '            print("No files found for processing")',
            '            return False',
            '        ',
            '        # Step 2: Convert to sample5',
            '        if not convert_to_sample5(file_list):',
            '            print("Sample5 conversion failed")',
            '            return False',
            '        ',
            '        # Step 3: Assemble study',
            '        study = assemble_study()',
            '        ',
            '        # Step 4: Align and merge',
            '        study = align_and_merge(study)',
            '        ',
            '        # Step 5: Generate plots',
            '        generate_plots(study)',
            '        ',
            '        # Step 6: Export results',
            '        export_results(study)',
            '        ',
            '        # Step 7: Save study',
            '        save_study(study)',
            '        ',
            '        # Step 8: Cleanup',
            '        cleanup_temp_files()',
            '        ',
            '        # Final summary',
            '        total_time = time.time() - start_time',
            '        print("=" * 70)',
            '        print("ANALYSIS COMPLETED SUCCESSFULLY")',
            '        print(f"Total processing time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)")',
            '        if hasattr(study, "consensus_df"):',
            '            print(f"Consensus features generated: {len(study.consensus_df)}")',
            '        print("=" * 70)',
            '        ',
            '        return True',
            '        ',
            '    except KeyboardInterrupt:',
            '        print("\\nAnalysis interrupted by user")',
            '        return False',
            '    except Exception as e:',
            '        print(f"Analysis failed with error: {e}")',
            '        import traceback',
            '        traceback.print_exc()',
            '        return False',
            '',
            '',
            'if __name__ == "__main__":',
            '    success = main()',
            '    sys.exit(0 if success else 1)',
        ]
        
        return '\n'.join(script_lines)
    
    def info(self):
        """Print comprehensive wizard status information."""
        status = self.get_status()
        
        print("\n" + "=" * 50)
        print("WIZARD STATUS")
        print("=" * 50)
        print(f"Current Step: {status['current_step']}")
        print(f"Data Source: {self.params.data_source}")
        print(f"Study Folder: {self.params.study_folder}")
        print(f"Polarity: {status['parameters']['polarity']}")
        print(f"CPU Cores: {status['parameters']['num_cores']}")
        print(f"Adducts: {', '.join(status['parameters']['adducts'])}")
        print(f"Detector Type: {self.params.detector_type}")
        print(f"Noise Threshold: {self.params.noise_threshold}")
        print(f"Processing Time: {status['processing_time']}")
        print(f"Files Processed: {status['processed_files']}")
        print(f"Files Failed: {status['failed_files']}")
        print(f"Study Loaded: {status['study_loaded']}")
        
        if self.study is not None and hasattr(self.study, 'samples_df'):
            print(f"Samples in Study: {len(self.study.samples_df)}")
        
        if self.study is not None and hasattr(self.study, 'consensus_df'):
            print(f"Consensus Features: {len(self.study.consensus_df)}")
        
        print("=" * 50)


def create_script(
    source: str, 
    study_folder: str, 
    filename: str, 
    polarity: str = "positive",
    adducts: Optional[List[str]] = None,
    params: Optional[wizard_def] = None,
    num_cores: int = 0,
    **kwargs
) -> bool:
    """
    Create a standalone analysis script without initializing a Wizard instance.
    
    This function generates a Python script that replicates automated processing
    steps with the specified configuration. The script can be executed independently
    to perform the same analysis.
    
    Parameters:
        source: Directory containing raw data files
        study_folder: Output directory for processed study  
        filename: Filename for the generated script (should end with .py)
        polarity: Ion polarity mode ("positive" or "negative")
        adducts: List of adduct specifications (auto-set if None)
        params: Custom wizard_def parameters (optional)
        num_cores: Number of CPU cores (0 = auto-detect)
        **kwargs: Additional parameters to override defaults
        
    Returns:
        True if script was generated successfully, False otherwise
        
    Example:
        >>> from masster.wizard import create_script
        >>> create_script(
        ...     source=r'D:\\Data\\raw_files',
        ...     study_folder=r'D:\\Data\\output', 
        ...     filename='run_masster.py',
        ...     polarity='positive'
        ... )
    """
    
    try:
        # Create parameters
        if params is not None:
            # Use provided params as base
            wizard_params = params
            # Update with provided values
            wizard_params.data_source = source
            wizard_params.study_folder = study_folder
            if polarity != "positive":  # Only override if explicitly different
                wizard_params.polarity = polarity
            if num_cores > 0:
                wizard_params.num_cores = num_cores
            if adducts is not None:
                wizard_params.adducts = adducts
        else:
            # Create new params with provided values
            wizard_params = wizard_def(
                data_source=source,
                study_folder=study_folder,
                polarity=polarity,
                num_cores=max(1, int(multiprocessing.cpu_count() * 0.75)) if num_cores <= 0 else num_cores
            )
            
            if adducts is not None:
                wizard_params.adducts = adducts
            
            # Apply any additional kwargs
            for key, value in kwargs.items():
                if hasattr(wizard_params, key):
                    setattr(wizard_params, key, value)
        
        # Ensure study folder exists
        study_path = Path(study_folder)
        study_path.mkdir(parents=True, exist_ok=True)
        
        # Create a temporary Wizard instance to generate the script
        temp_wizard = Wizard(params=wizard_params)
        
        # Generate the script using the existing method
        success = temp_wizard.export_script(filename)
        
        if success:
            script_path = study_path / Path(filename).name
            print(f"Analysis script created: {script_path.absolute()}")
            print(f"Run with: python \"{script_path}\"")
            
        return success
        
    except Exception as e:
        print(f"Failed to create script: {e}")
        import traceback
        traceback.print_exc()
        return False


# Export the main classes and functions
__all__ = ["Wizard", "wizard_def", "create_script"]
