# Wizard Class Documentation

The `Wizard` class provides comprehensive automation for mass spectrometry data processing, from raw files to final study results. It handles the complete workflow with minimal user intervention while providing intelligent resume capabilities, parallel processing optimization, and adaptive output formats.

## Quick Start

### Basic Usage

```python
from masster import Wizard

# Create wizard with minimal configuration
wizard = Wizard(
    data_source="./raw_data",      # Directory with raw files
    study_folder="./processed",    # Output directory  
    polarity="positive",           # or "negative"
    num_cores=4                    # CPU cores to use
)

# Run complete pipeline
success = wizard.run_full_pipeline()

if success:
    wizard.info()  # Print summary
```

### Advanced Configuration

```python
from masster import Wizard, wizard_def

# Create custom parameters
params = wizard_def(
    data_source="./raw_data",
    study_folder="./processed_advanced",
    polarity="negative",
    num_cores=8,
    
    # File discovery
    file_extensions=[".wiff", ".raw", ".mzML"],
    search_subfolders=True,
    skip_patterns=["blank", "QC", "test"],
    
    # Processing parameters
    adducts=["H-1:-:0.95", "Cl:-:0.05", "CH2O2:0:0.2"],
    chrom_fwhm=0.15,
    noise_threshold=5e4,
    
    # Study assembly
    rt_tolerance=1.0,
    mz_tolerance=0.008,
    min_samples_for_merge=30,
    
    # Output options
    export_formats=["csv", "xlsx", "mgf", "parquet"],
    generate_plots=True,
    compress_output=True,
)

wizard = Wizard(params=params)
wizard.run_full_pipeline()
```

## Key Features

### 🔄 Automated Pipeline
- **Raw Data Discovery**: Automatically finds and validates raw MS files
- **Batch Conversion**: Parallel conversion to sample5 format with optimized parameters
- **Study Assembly**: Creates study from processed samples with quality filtering
- **Feature Alignment**: Cross-sample alignment using configurable algorithms
- **Consensus Generation**: Merges aligned features with statistical validation
- **Results Export**: Multiple output formats for downstream analysis

### 💾 Intelligent Resume
- **Checkpoint System**: Automatically saves progress at key points
- **File Tracking**: Remembers which files have been processed successfully  
- **Smart Recovery**: Resumes from last successful step after interruption
- **Validation**: Verifies existing outputs before skipping

### ⚡ Performance Optimization
- **Parallel Processing**: Utilizes multiple CPU cores efficiently
- **Memory Management**: Adaptive batch sizing based on available memory
- **Process Isolation**: Prevents memory leaks in long-running jobs
- **Adaptive Compression**: Optimizes output format based on study size

### 📊 Comprehensive Logging
- **Progress Tracking**: Real-time status updates with time estimates
- **Detailed Logs**: Complete processing history saved to files
- **Error Reporting**: Clear error messages with recovery suggestions
- **Performance Metrics**: Processing times and resource usage statistics

## Pipeline Steps

### 1. File Discovery
- Searches for raw MS files (`.wiff`, `.raw`, `.mzML`, `.d`)
- Applies skip patterns to exclude unwanted files
- Validates file integrity and accessibility
- Reports file sizes and estimates processing time

### 2. Sample5 Conversion
- **Feature Detection**: Two-pass algorithm with configurable parameters
- **Adduct Detection**: Automated adduct grouping based on polarity
- **MS2 Linking**: Associates fragmentation spectra with features
- **Quality Control**: Validates outputs and reports statistics
- **Parallel Processing**: Utilizes multiple CPU cores with batch optimization

### 3. Study Assembly
- **Sample Loading**: Imports all processed sample5 files
- **Quality Filtering**: Removes low-quality features based on coherence/prominence
- **Metadata Organization**: Organizes sample information and experimental design
- **Memory Optimization**: Efficient data structures for large studies

### 4. Feature Alignment
- **RT Alignment**: Corrects retention time shifts between samples
- **Mass Alignment**: Accounts for mass calibration differences  
- **Algorithm Selection**: Supports KD-tree, QT-clustering, and chunked methods
- **Validation**: Reports alignment statistics and quality metrics

### 5. Consensus Generation
- **Feature Merging**: Groups aligned features into consensus features
- **Statistical Validation**: Applies minimum sample requirements
- **Gap Filling**: Extracts chromatograms for missing values
- **MS2 Integration**: Links consensus features to MS2 spectra

### 6. Visualization & Export
- **Interactive Plots**: 2D feature maps, PCA plots, alignment visualizations
- **Multiple Formats**: CSV, Excel, MGF, Parquet exports
- **Study Archival**: Compressed study5 format for long-term storage
- **Metadata Export**: Complete processing parameters and statistics

## Configuration Options

### Core Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data_source` | str | **required** | Directory containing raw data files |
| `study_folder` | str | **required** | Output directory for processed study |
| `polarity` | str | `"positive"` | Ion polarity mode (`"positive"` or `"negative"`) |
| `num_cores` | int | `4` | Number of CPU cores for parallel processing |
| `adducts` | List[str] | auto-set | Adduct specifications (set based on polarity) |

### File Discovery

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `file_extensions` | List[str] | `[".wiff", ".raw", ".mzML", ".d"]` | File types to search for |
| `search_subfolders` | bool | `True` | Search subdirectories recursively |
| `skip_patterns` | List[str] | `["blank", "QC", "test"]` | Filename patterns to skip |
| `max_file_size_gb` | float | `4.0` | Maximum file size warning threshold |

### Processing Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `batch_size` | int | `8` | Files processed per batch |
| `memory_limit_gb` | float | `16.0` | Memory usage limit |
| `chrom_fwhm` | float | `0.2` | Expected chromatographic peak width (s) |
| `noise_threshold` | float | `1e5` | Intensity threshold for peak detection |
| `chrom_peak_snr` | float | `5.0` | Signal-to-noise ratio requirement |
| `tol_ppm` | float | `10.0` | Mass tolerance (ppm) |

### Study Assembly

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `rt_tolerance` | float | `1.5` | RT tolerance for alignment (seconds) |
| `mz_tolerance` | float | `0.01` | m/z tolerance for alignment (Da) |
| `alignment_algorithm` | str | `"kd"` | Alignment algorithm (`"kd"`, `"qt"`, `"chunked"`) |
| `merge_method` | str | `"chunked"` | Merge algorithm for consensus generation |
| `min_samples_for_merge` | int | `50` | Minimum samples required for consensus |

### Output & Logging

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `generate_plots` | bool | `True` | Generate visualization plots |
| `export_formats` | List[str] | `["csv", "mgf", "xlsx"]` | Output formats to generate |
| `compress_output` | bool | `True` | Compress final study file |
| `adaptive_compression` | bool | `True` | Adapt compression based on study size |
| `log_level` | str | `"INFO"` | Logging detail level |
| `log_to_file` | bool | `True` | Save logs to file |

### Resume & Recovery

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `resume_enabled` | bool | `True` | Enable automatic resume capability |
| `force_reprocess` | bool | `False` | Force reprocessing of existing files |
| `backup_enabled` | bool | `True` | Create backups of intermediate results |
| `checkpoint_interval` | int | `10` | Save progress every N files |
| `cleanup_temp_files` | bool | `True` | Remove temporary files after completion |

## Methods

### Pipeline Control

#### `run_full_pipeline() -> bool`
Executes the complete processing pipeline in sequence. Returns `True` if successful.

#### Individual Steps
- `discover_files() -> List[Path]` - Find raw data files
- `convert_to_sample5(file_list=None) -> bool` - Convert to sample5 format
- `assemble_study() -> bool` - Create study from sample5 files
- `align_and_merge() -> bool` - Perform feature alignment and merging
- `generate_plots() -> bool` - Create visualization plots
- `export_results() -> bool` - Export in requested formats
- `save_study() -> bool` - Save final study file
- `cleanup_temp_files() -> bool` - Remove temporary files

### Status & Information

#### `info()`
Prints comprehensive wizard status including progress, timings, and results.

#### `get_status() -> Dict[str, Any]`
Returns detailed status dictionary with current step, processed files, timing, and parameters.

## Error Handling & Recovery

### Common Issues and Solutions

**Memory Errors**
- Reduce `batch_size` parameter
- Increase `memory_limit_gb` if available
- Use `merge_method="chunked"` for large studies
- Enable `cleanup_temp_files=True`

**File Access Errors**
- Check file permissions on source and destination folders
- Verify network connectivity for remote file systems
- Ensure sufficient disk space in output directory
- Close any applications that might lock files

**Processing Failures** 
- Check individual file integrity
- Review `skip_patterns` to exclude problematic files
- Examine detailed logs in `wizard.log` and `processing.log`
- Try processing failed files individually for debugging

**Resume Issues**
- Delete `wizard_checkpoint.json` to force fresh start
- Verify output directory permissions
- Check for corrupted intermediate files

### Validation and Quality Control

The Wizard includes built-in validation at each step:

- **File Validation**: Checks file accessibility and format compatibility
- **Processing Validation**: Verifies sample5 outputs can be loaded
- **Study Validation**: Ensures study assembly completed successfully  
- **Alignment Validation**: Reports alignment statistics and warnings
- **Export Validation**: Confirms all requested outputs were created

## Performance Guidelines

### System Requirements
- **Minimum**: 4 CPU cores, 8 GB RAM
- **Recommended**: 8+ CPU cores, 16+ GB RAM  
- **Large Studies**: 16+ CPU cores, 32+ GB RAM
- **Storage**: SSD recommended, ~2-3x raw data size free space

### Optimization Tips

**For Small Studies (< 50 samples)**
- Use `num_cores = 4-6`
- Set `batch_size = 4-8`  
- Use `merge_method = "kd"`
- Enable all export formats

**For Large Studies (100+ samples)**
- Use `num_cores = 8-16`
- Set `batch_size = 16-32`
- Use `merge_method = "chunked"`
- Enable `adaptive_compression = True`
- Consider processing in polarity-specific batches

**For Very Large Studies (500+ samples)**
- Process positive/negative modes separately
- Use `memory_limit_gb = 64+`
- Set `checkpoint_interval = 50`
- Enable `cleanup_temp_files = True`
- Consider cluster/cloud processing

## Integration Examples

### With Existing Workflows

```python
# Integration with custom preprocessing
wizard = Wizard(data_source="./preprocessed", ...)

# Skip conversion if already done
if not wizard.study_folder_path.glob("*.sample5"):
    wizard.convert_to_sample5()

# Continue with study-level processing
wizard.assemble_study()
wizard.align_and_merge() 
wizard.export_results()
```

### Batch Processing Multiple Studies

```python
studies = [
    {"source": "./batch1", "output": "./results/batch1", "polarity": "pos"},
    {"source": "./batch2", "output": "./results/batch2", "polarity": "neg"},
]

for study_config in studies:
    wizard = Wizard(**study_config, num_cores=8)
    success = wizard.run_full_pipeline()
    
    if success:
        print(f"✅ {study_config['output']} completed")
    else:
        print(f"❌ {study_config['output']} failed")
```

### Custom Processing Steps

```python
wizard = Wizard(...)

# Standard conversion
wizard.convert_to_sample5()

# Custom study assembly with specific parameters
wizard.assemble_study()

# Custom filtering before alignment
if hasattr(wizard.study, 'features_filter'):
    selection = wizard.study.features_select(
        chrom_coherence=0.5,  # Higher quality threshold
        chrom_prominence_scaled=2.0
    )
    wizard.study.features_filter(selection)

# Continue with standard pipeline  
wizard.align_and_merge()
wizard.generate_plots()
```

## Output Files

The Wizard generates several types of output files:

### Primary Results
- `final_study.study5` - Complete study in masster native format
- `consensus_features.csv` - Feature table with RT, m/z, intensity data
- `study_results.xlsx` - Multi-sheet Excel workbook with results and metadata
- `consensus_ms2.mgf` - MS2 spectra for database searching

### Visualizations
- `alignment_plot.html` - Interactive alignment visualization
- `consensus_2d.html` - 2D feature map of consensus features
- `pca_plot.html` - Principal component analysis plot
- `consensus_stats.html` - Study statistics and quality metrics

### Processing Logs
- `wizard.log` - Detailed processing log with debug information
- `processing.log` - Simple progress log with timestamps
- `study_metadata.txt` - Study summary with parameters and statistics

### Individual Sample Outputs (if enabled)
- `sample_name.sample5` - Processed sample in masster format
- `sample_name.features.csv` - Individual sample feature table
- `sample_name.mgf` - Individual sample MS2 spectra
- `sample_name_2d.html` - Individual sample 2D plot

The Wizard provides a complete, automated solution for mass spectrometry data processing while maintaining flexibility for custom workflows and providing robust error handling and recovery capabilities.
