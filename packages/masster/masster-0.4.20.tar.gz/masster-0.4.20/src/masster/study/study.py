"""
study.py

This module provides tools for multi-sample mass spectrometry data analysis and cross-sample feature alignment.
It defines the `study` class, which manages collections of DDA files, performs feature alignment across samples,
generates consensus features, and provides study-level visualization and reporting capabilities.

Key Features:
- **Multi-Sample Management**: Handle collections of mass spectrometry files with metadata.
- **Feature Alignment**: Align features across multiple samples using retention time and m/z tolerances.
- **Consensus Features**: Generate consensus feature tables from aligned data.
- **Batch Processing**: Automated processing of entire studies with configurable parameters.
- **Study Visualization**: Generate comparative plots and alignment visualizations.
- **Export Capabilities**: Export study results in various formats for downstream analysis.

Dependencies:
- `pyopenms`: For mass spectrometry data handling and algorithms.
- `polars` and `pandas`: For efficient data manipulation and analysis.
- `bokeh`, `holoviews`, `panel`: For interactive visualizations and dashboards.
- `numpy`: For numerical computations and array operations.

Classes:
- `study`: Main class for multi-sample study management, providing methods for file loading,
  feature alignment, consensus generation, and study-level analysis.

Example Usage:
```python
from study import study

# Create study from multiple files
study_obj = study()
study_obj.load_files(["sample1.mzML", "sample2.mzML", "sample3.mzML"])
study_obj.process_all()
study_obj.align()
study_obj.plot_alignment_bokeh()
study_obj.export_consensus()
```

See Also:
- `single.py`: For individual file processing before study-level analysis.
- `parameters.study_parameters`: For study-specific parameter configuration.


"""

from __future__ import annotations

import importlib
import os
import sys

import polars as pl

# Study-specific imports
from masster.study.h5 import _load_study5
from masster.study.h5 import _save_study5
from masster.study.h5 import _save_study5_compressed
from masster.study.helpers import _get_consensus_uids
from masster.study.helpers import _get_feature_uids
from masster.study.helpers import _get_sample_uids
from masster.study.helpers import _ensure_features_df_schema_order
from masster.study.helpers import compress
from masster.study.helpers import compress_features
from masster.study.helpers import compress_ms2
from masster.study.helpers import compress_chrom
from masster.study.helpers import restore_features
from masster.study.helpers import restore_chrom
from masster.study.helpers import restore_ms2
from masster.study.helpers import decompress
from masster.study.helpers import fill_reset
from masster.study.helpers import get_chrom
from masster.study.helpers import get_sample
from masster.study.helpers import get_consensus
from masster.study.helpers import get_consensus_matches
from masster.study.helpers import get_consensus_matrix
from masster.study.helpers import get_orphans
from masster.study.helpers import get_gaps_matrix
from masster.study.helpers import get_gaps_stats
from masster.study.helpers import align_reset
from masster.study.helpers import set_folder
from masster.study.helpers import set_source
from masster.study.helpers import sample_color
from masster.study.helpers import sample_color_reset
from masster.study.helpers import sample_name_replace
from masster.study.helpers import sample_name_reset
from masster.study.helpers import samples_select
from masster.study.helpers import samples_delete
from masster.study.helpers import features_select
from masster.study.helpers import features_filter
from masster.study.helpers import features_delete
from masster.study.helpers import consensus_select
from masster.study.helpers import consensus_filter
from masster.study.helpers import consensus_delete
from masster.study.load import add
from masster.study.load import add_sample
from masster.study.load import _add_samples_batch
from masster.study.load import _add_sample_optimized
from masster.study.load import _add_sample_standard
from masster.study.load import _sample_color_reset_optimized
from masster.study.load import fill_single
from masster.study.load import fill
from masster.study.load import _process_sample_for_parallel_fill
from masster.study.load import _get_missing_consensus_sample_combinations
from masster.study.load import load
from masster.study.load import _load_consensusXML
from masster.study.load import load_features
from masster.study.load import sanitize
from masster.study.plot import plot_alignment
from masster.study.plot import plot_consensus_2d
from masster.study.plot import plot_samples_2d
from masster.study.plot import plot_consensus_stats
from masster.study.plot import plot_chrom
from masster.study.plot import plot_pca
from masster.study.plot import plot_bpc
from masster.study.plot import plot_tic
from masster.study.plot import plot_eic
from masster.study.plot import plot_rt_correction
from masster.study.processing import align
from masster.study.merge import merge
from masster.study.merge import _reset_consensus_data
from masster.study.merge import _extract_consensus_features
from masster.study.merge import _perform_adduct_grouping
from masster.study.merge import _consensus_cleanup
from masster.study.merge import _identify_adduct_by_mass_shift
from masster.study.merge import _finalize_merge
from masster.study.merge import _count_tight_clusters
from masster.study.processing import integrate
from masster.study.processing import find_ms2
from masster.study.parameters import store_history
from masster.study.parameters import get_parameters
from masster.study.parameters import update_parameters
from masster.study.parameters import get_parameters_property
from masster.study.parameters import set_parameters_property
from masster.study.save import save, save_consensus, _save_consensusXML, save_samples
from masster.study.export import (
    export_mgf,
    export_mztab,
    export_xlsx,
    export_parquet,
    _get_mgf_df,
)
from masster.study.id import lib_load, identify, get_id, id_reset, lib_reset
from masster.study.id import (
    _get_adducts,
    _calculate_formula_mass_shift,
    _format_adduct_name,
    _parse_element_counts,
)

from masster.logger import MassterLogger
from masster.study.defaults.study_def import study_defaults
from masster.study.defaults.align_def import align_defaults
from masster.study.defaults.export_def import export_mgf_defaults
from masster.study.defaults.fill_chrom_def import fill_chrom_defaults
from masster.study.defaults.fill_def import fill_defaults
from masster.study.defaults.find_ms2_def import find_ms2_defaults
from masster.study.defaults.integrate_chrom_def import integrate_chrom_defaults
from masster.study.defaults.integrate_def import integrate_defaults
from masster.study.defaults.merge_def import merge_defaults

# Import sample defaults
from masster.sample.defaults.sample_def import sample_defaults
from masster.sample.defaults.find_features_def import find_features_defaults
from masster.sample.defaults.find_adducts_def import find_adducts_defaults
from masster.sample.defaults.get_spectrum_def import get_spectrum_defaults

# Warning symbols for info display
_WARNING_SYMBOL = "⚠️"  # Yellow warning triangle
_CRITICAL_SYMBOL = "❗️"  # Red exclamation mark


class Study:
    """
    A class for managing and analyzing multi-sample mass spectrometry studies.

    The `study` class provides comprehensive tools for handling collections of DDA
    (Data-Dependent Acquisition) mass spectrometry files, performing cross-sample
    feature alignment, generating consensus features, and conducting study-level
    analysis and visualization.

    Attributes:
        folder (str): Default directory for study files and outputs.
        ddafiles (dict): Dictionary containing loaded ddafile objects keyed by sample names.
        features_df (pl.DataFrame): Combined features from all samples in the study.
        consensus_df (pl.DataFrame): Consensus features generated from alignment.
        metadata_df (pl.DataFrame): Sample metadata and experimental information.

    Key Methods:
        - `add_folder()`: Load all files from a directory into the study.
        - `add_sample()`: Add individual sample files to the study.
        - `process_all()`: Batch process all samples with feature detection.
        - `align()`: Perform cross-sample feature alignment.
        - `plot_alignment_bokeh()`: Visualize alignment results.
        - `export_consensus()`: Export consensus features for downstream analysis.

    Example Usage:
        >>> from masster import Study
        >>> study_obj = Study(folder="./data")
        >>> study_obj.load_folder("./mzml_files")
        >>> study_obj.process_all()
        >>> study_obj.align()
        >>> study_obj.plot_alignment_bokeh()
        >>> study_obj.export_consensus("consensus_features.csv")

    See Also:
        - `ddafile`: For individual sample processing before study-level analysis.
        - `StudyParameters`: For configuring study-specific parameters.
    """

    # Defaults class attributes
    study_defaults = study_defaults
    sample_defaults = sample_defaults
    find_features_defaults = find_features_defaults
    find_adducts_defaults = find_adducts_defaults
    find_ms2_defaults = find_ms2_defaults
    get_spectrum_defaults = get_spectrum_defaults
    export_mgf_defaults = export_mgf_defaults
    align_defaults = align_defaults
    merge_defaults = merge_defaults
    integrate_defaults = integrate_defaults
    integrate_chrom_defaults = integrate_chrom_defaults

    def __init__(
        self,
        filename=None,
        **kwargs,
    ):
        """
        Initialize a Study instance for multi-sample mass spectrometry analysis.

        This constructor initializes various attributes related to file handling,
        data storage, and processing parameters used for study-level analysis.

        Parameters:
            filename (str, optional): Path to a .study5 file to load automatically.
                                    If provided, the folder will be set to the
                                    directory containing this file, and the study will
                                    be loaded automatically.
            **kwargs: Keyword arguments for setting study parameters. Can include:
                     - A study_defaults instance to set all parameters at once (pass as params=study_defaults(...))
                     - Individual parameter names and values (see study_defaults for available parameters)

                     Core initialization parameters:
                     - folder (str, optional): Default directory for study files and outputs
                     - label (str, optional): An optional label to identify the study
                     - log_level (str): The logging level to be set for the logger. Defaults to 'INFO'
                     - log_label (str, optional): Optional label for the logger
                     - log_sink (str): Output sink for logging. Default is "sys.stdout"

                     For backward compatibility, original signature is supported:
                     Study(folder=..., label=..., log_level=..., log_label=..., log_sink=...)
        """
        # Initialize default parameters

        # Handle filename parameter for automatic loading
        auto_load_filename = None
        if filename is not None:
            if not filename.endswith(".study5"):
                raise ValueError("filename must be a .study5 file")
            if not os.path.exists(filename):
                raise FileNotFoundError(f"Study file not found: {filename}")

            # Set folder to the directory containing the file if not already specified
            if "folder" not in kwargs:
                kwargs["folder"] = os.path.dirname(os.path.abspath(filename))

            auto_load_filename = filename

        # Check if a study_defaults instance was passed
        if "params" in kwargs and isinstance(kwargs["params"], study_defaults):
            params = kwargs.pop("params")
        else:
            # Create default parameters and update with provided values
            params = study_defaults()

            # Update with any provided parameters
            for key, value in kwargs.items():
                if hasattr(params, key):
                    params.set(key, value, validate=True)

        # Keeps a pointer to study5 whenever it's saved or loaded
        self.filename = None

        # Store parameter instance for method access
        self.parameters = params
        self.history = {}
        self.store_history(["study"], params.to_dict())

        # Set instance attributes (ensure proper string values for logger)
        self.folder = params.folder
        self.label = params.label
        self.polarity = (
            params.polarity
            if params.polarity in ["positive", "negative", "pos", "neg"]
            else "positive"
        )
        self.log_level = params.log_level.upper() if params.log_level else "INFO"
        self.log_label = params.log_label + " | " if params.log_label else ""
        self.log_sink = params.log_sink

        if self.folder is not None and not os.path.exists(self.folder):
            # create the folder if it does not exist
            os.makedirs(self.folder)

        self.samples_df = pl.DataFrame(
            {
                "sample_uid": [],
                "sample_name": [],
                "sample_path": [],
                "sample_type": [],
                "map_id": [],
                "sample_source": [],
                "sample_color": [],
                "sample_group": [],
                "sample_batch": [],
                "sample_sequence": [],
                "num_features": [],
                "num_ms1": [],
                "num_ms2": [],
            },
            schema={
                "sample_uid": pl.Int64,
                "sample_name": pl.Utf8,
                "sample_path": pl.Utf8,
                "sample_type": pl.Utf8,
                "map_id": pl.Int64,
                "sample_source": pl.Utf8,
                "sample_color": pl.Utf8,
                "sample_group": pl.Utf8,
                "sample_batch": pl.Int64,
                "sample_sequence": pl.Int64,
                "num_features": pl.Int64,
                "num_ms1": pl.Int64,
                "num_ms2": pl.Int64,
            },
        )
        self.features_maps = []
        self.features_df = pl.DataFrame()
        self.consensus_ms2 = pl.DataFrame()
        self.consensus_df = pl.DataFrame()
        self.consensus_map = None
        self.consensus_mapping_df = pl.DataFrame()
        self.alignment_ref_index = None

        # Library DataFrame (populated by lib_load)
        self.lib_df = pl.DataFrame()

        # Identification results DataFrame (populated by identify)
        self.id_df = pl.DataFrame()

        # Initialize independent logger
        self.logger = MassterLogger(
            instance_type="study",
            level=self.log_level.upper(),
            label=self.log_label,
            sink=self.log_sink,
        )
        self.logger.debug(f"Study folder: {self.folder}")
        self.logger.debug(f"Polarity: {self.polarity}")

        # Auto-load study file if filename was provided
        if auto_load_filename is not None:
            self.load(filename=auto_load_filename)

        # cache for Sample instances created/loaded by this Study
        self._samples_cache = {}

    # ===== ATTACH MODULE FUNCTIONS AS CLASS METHODS =====
    
    # === File I/O Operations ===
    load = load
    save = save
    save_consensus = save_consensus
    save_samples = save_samples
    sanitize = sanitize
    set_folder = set_folder
    
    # === Sample Management ===
    add = add
    add_folder = add  # backward compatibility alias
    add_sample = add_sample
    
    # === Core Processing Operations ===
    align = align
    merge = merge
    find_consensus = merge  # Backward compatibility alias
    find_ms2 = find_ms2
    integrate = integrate
    integrate_chrom = integrate  # Backward compatibility alias
    fill = fill
    fill_chrom = fill  # Backward compatibility alias
    fill_single = fill_single
    fill_chrom_single = fill_single  # Backward compatibility alias
    # === Data Retrieval and Access ===
    get_consensus = get_consensus
    get_chrom = get_chrom
    get_sample = get_sample
    get_consensus_matches = get_consensus_matches
    get_consensus_matrix = get_consensus_matrix
    get_gaps_matrix = get_gaps_matrix
    get_gaps_stats = get_gaps_stats
    get_orphans = get_orphans
    
    # === Data Selection and Filtering ===
    samples_select = samples_select
    samples_delete = samples_delete
    features_select = features_select
    features_filter = features_filter
    features_delete = features_delete
    consensus_select = consensus_select
    consensus_filter = consensus_filter
    consensus_delete = consensus_delete
    # Backward compatibility aliases
    filter_consensus = consensus_filter
    select_consensus = consensus_select
    filter_features = features_filter
    select_features = features_select
    consensus_find = merge
    
    # === Sample Metadata and Styling ===
    set_source = set_source
    sample_color = sample_color
    sample_color_reset = sample_color_reset
    name_replace = sample_name_replace
    name_reset = sample_name_reset
    
    # === Data Compression and Storage ===
    compress = compress
    compress_features = compress_features
    compress_ms2 = compress_ms2
    compress_chrom = compress_chrom
    restore_features = restore_features
    restore_chrom = restore_chrom
    restore_ms2 = restore_ms2
    decompress = decompress
    
    # === Reset Operations ===
    fill_reset = fill_reset
    align_reset = align_reset
    
    # === Plotting and Visualization ===
    plot_alignment = plot_alignment
    plot_chrom = plot_chrom
    plot_consensus_2d = plot_consensus_2d
    plot_consensus_stats = plot_consensus_stats
    plot_pca = plot_pca
    plot_samples_2d = plot_samples_2d
    plot_bpc = plot_bpc
    plot_rt_correction = plot_rt_correction
    plot_tic = plot_tic
    plot_eic = plot_eic
    
    # === Export Operations ===
    export_mgf = export_mgf
    export_mztab = export_mztab
    export_xlsx = export_xlsx
    export_parquet = export_parquet
    
    # === Identification and Library Matching ===
    lib_load = lib_load
    identify = identify
    get_id = get_id
    id_reset = id_reset
    lib_reset = lib_reset
    
    # === Parameter Management ===
    store_history = store_history
    get_parameters = get_parameters
    update_parameters = update_parameters
    get_parameters_property = get_parameters_property
    set_parameters_property = set_parameters_property
    
    # === Private/Internal Methods ===
    _add_samples_batch = _add_samples_batch
    _add_sample_optimized = _add_sample_optimized
    _add_sample_standard = _add_sample_standard
    _sample_color_reset_optimized = _sample_color_reset_optimized
    _load_study5 = _load_study5
    _save_study5 = _save_study5
    _save_study5_compressed = _save_study5_compressed
    _get_consensus_uids = _get_consensus_uids
    _get_feature_uids = _get_feature_uids
    _get_sample_uids = _get_sample_uids
    _ensure_features_df_schema_order = _ensure_features_df_schema_order
    _process_sample_for_parallel_fill = _process_sample_for_parallel_fill
    _get_missing_consensus_sample_combinations = (
        _get_missing_consensus_sample_combinations
    )
    _load_consensusXML = _load_consensusXML
    load_features = load_features
    _save_consensusXML = _save_consensusXML
    _get_mgf_df = _get_mgf_df
    _get_adducts = _get_adducts
    _calculate_formula_mass_shift = _calculate_formula_mass_shift
    _format_adduct_name = _format_adduct_name
    _parse_element_counts = _parse_element_counts
    
    # === Merge Helper Methods ===
    _reset_consensus_data = _reset_consensus_data
    _extract_consensus_features = _extract_consensus_features
    _perform_adduct_grouping = _perform_adduct_grouping
    _consensus_cleanup = _consensus_cleanup
    _identify_adduct_by_mass_shift = _identify_adduct_by_mass_shift
    _finalize_merge = _finalize_merge
    
    # === Default Parameters ===
    study_defaults = study_defaults
    align_defaults = align_defaults
    export_mgf_defaults = export_mgf_defaults
    fill_chrom_defaults = fill_chrom_defaults
    fill_defaults = fill_defaults
    find_ms2_defaults = find_ms2_defaults
    integrate_chrom_defaults = integrate_chrom_defaults
    integrate_defaults = integrate_defaults
    merge_defaults = merge_defaults

    def _reload(self):
        """
        Reloads all masster modules to pick up any changes to their source code,
        and updates the instance's class reference to the newly reloaded class version.
        This ensures that the instance uses the latest implementation without restarting the interpreter.
        """
        # Reset logger configuration flags to allow proper reconfiguration after reload
        """        try:
            import masster.sample.logger as logger_module

            if hasattr(logger_module, "_STUDY_LOGGER_CONFIGURED"):
                logger_module._STUDY_LOGGER_CONFIGURED = False
        except Exception:
            pass"""

        # Get the base module name (masster)
        base_modname = self.__class__.__module__.split(".")[0]
        current_module = self.__class__.__module__

        # Dynamically find all study submodules
        study_modules = []
        study_module_prefix = f"{base_modname}.study."

        # Get all currently loaded modules that are part of the study package
        for module_name in sys.modules:
            if (
                module_name.startswith(study_module_prefix)
                and module_name != current_module
            ):
                study_modules.append(module_name)

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

        # Add lib submodules
        lib_modules = []
        lib_module_prefix = f"{base_modname}.lib."
        for module_name in sys.modules:
            if (
                module_name.startswith(lib_module_prefix)
                and module_name != current_module
            ):
                lib_modules.append(module_name)

        all_modules_to_reload = core_modules + sample_modules + study_modules + lib_modules

        # Reload all discovered modules
        for full_module_name in all_modules_to_reload:
            try:
                if full_module_name in sys.modules:
                    mod = sys.modules[full_module_name]
                    importlib.reload(mod)
                    self.logger.debug(f"Reloaded module: {full_module_name}")
            except Exception as e:
                self.logger.warning(f"Failed to reload module {full_module_name}: {e}")

        # Finally, reload the current module (sample.py)
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

    def __dir__(self):
        """
        Custom __dir__ implementation to hide internal methods starting with '_' 
        and backward compatibility aliases from tab completion and dir() calls, 
        while keeping them accessible to class methods.
        
        Returns:
            list: List of public attribute and method names (excluding internal and deprecated methods)
        """
        # Define backward compatibility aliases to hide
        backward_compatibility_aliases = {
            'add_folder',           # alias for add
            'find_consensus',       # alias for merge  
            'integrate_chrom',      # alias for integrate
            'fill_chrom',           # alias for fill
            'fill_chrom_single',    # alias for fill_single
            'filter_consensus',     # alias for consensus_filter
            'select_consensus',     # alias for consensus_select
            'filter_features',      # alias for features_filter
            'select_features',      # alias for features_select
            'consensus_find',       # alias for merge
        }
        
        # Get all attributes from the class
        all_attrs = set()
        
        # Add attributes from the class and all its bases
        for cls in self.__class__.__mro__:
            all_attrs.update(cls.__dict__.keys())
        
        # Add instance attributes
        all_attrs.update(self.__dict__.keys())
        
        # Filter out attributes starting with '_' (but keep special methods like __init__, __str__, etc.)
        # Also filter out backward compatibility aliases
        public_attrs = [
            attr for attr in all_attrs 
            if not attr.startswith('_') or attr.startswith('__') and attr.endswith('__')
        ]
        
        # Remove backward compatibility aliases from the public attributes
        public_attrs = [attr for attr in public_attrs if attr not in backward_compatibility_aliases]
        
        return sorted(public_attrs)

    def __str__(self):
        """
        Returns a string representation of the study.

        Returns:
            str: A summary string of the study.
        """
        return ""

    def logger_update(
        self,
        level: str | None = None,
        label: str | None = None,
        sink: str | None = None,
    ):
        """Update the logging configuration for this Study instance.

        Args:
            level: New logging level ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
            label: New label for log messages
            sink: New output sink (file path, file object, or "sys.stdout")
        """
        if level is not None:
            self.log_level = level.upper()
            self.logger.update_level(level)

        if label is not None:
            self.log_label = label + " | " if len(label) > 0 else ""
            self.logger.update_label(self.log_label)

        if sink is not None:
            if sink == "sys.stdout":
                self.log_sink = sys.stdout
            else:
                self.log_sink = sink
            self.logger.update_sink(self.log_sink)

    def info(self):
        """
        Display study information with optimized performance.

        Returns a summary string of the study including folder, features count,
        samples count, and various statistics. Shows warning symbols for values
        that are out of normal range.
        """
        if self.consensus_df is None or self.consensus_df.is_empty():
            self.consensus_df = pl.DataFrame()
            consensus_df_len = 0
        else:
            consensus_df_len = len(self.consensus_df)

        samples_df_len = len(self.samples_df) if (self.samples_df is not None and not self.samples_df.is_empty()) else 0

        # Calculate consensus statistics only if consensus_df exists and has data
        if consensus_df_len > 0:
            # Execute the aggregation once
            stats_result = self.consensus_df.select(
                [
                    pl.col("number_samples").min().alias("min_samples"),
                    pl.col("number_samples").mean().alias("mean_samples"),
                    pl.col("number_samples").max().alias("max_samples"),
                ],
            ).row(0)

            min_samples = stats_result[0] if stats_result[0] is not None else 0
            mean_samples = stats_result[1] if stats_result[1] is not None else 0
            max_samples = stats_result[2] if stats_result[2] is not None else 0
        else:
            min_samples = 0
            mean_samples = 0
            max_samples = 0

        # Count only features where 'filled' == False
        if (self.features_df is not None and not self.features_df.is_empty() and 
            "filled" in self.features_df.columns):
            unfilled_features_count = self.features_df.filter(
                ~self.features_df["filled"],
            ).height
        else:
            unfilled_features_count = 0

        # Calculate features in consensus vs not in consensus (only for unfilled features)
        if (self.features_df is not None and not self.features_df.is_empty() and 
            self.consensus_mapping_df is not None and not self.consensus_mapping_df.is_empty()):
            # Get unfilled features only
            unfilled_features = (
                self.features_df.filter(~self.features_df["filled"])
                if "filled" in self.features_df.columns
                else self.features_df
            )

            # Ensure the column and list have matching data types
            consensus_feature_uids = self.consensus_mapping_df["feature_uid"].to_list()

            # Check if we need to cast either side to match types
            unfilled_dtype = unfilled_features["feature_uid"].dtype
            consensus_dtype = self.consensus_mapping_df["feature_uid"].dtype

            if unfilled_dtype != consensus_dtype:
                # Cast both to Int64 if possible, otherwise keep as string
                try:
                    unfilled_features = unfilled_features.with_columns(
                        pl.col("feature_uid").cast(pl.Int64),
                    )
                    consensus_feature_uids = [
                        int(uid) for uid in consensus_feature_uids
                    ]
                except Exception:
                    # If casting fails, ensure both are strings
                    unfilled_features = unfilled_features.with_columns(
                        pl.col("feature_uid").cast(pl.Utf8),
                    )
                    consensus_feature_uids = [
                        str(uid) for uid in consensus_feature_uids
                    ]

            # Count unfilled features that are in consensus
            in_consensus_count = unfilled_features.filter(
                pl.col("feature_uid").is_in(consensus_feature_uids),
            ).height

            # Calculate ratios that sum to 100%
            total_unfilled = unfilled_features.height
            ratio_in_consensus_to_total = (
                (in_consensus_count / total_unfilled * 100) if total_unfilled > 0 else 0
            )
            ratio_not_in_consensus_to_total = (
                100 - ratio_in_consensus_to_total if total_unfilled > 0 else 0
            )
        else:
            ratio_in_consensus_to_total = 0
            ratio_not_in_consensus_to_total = 0

        # Optimize chrom completeness calculation
        if (
            consensus_df_len > 0
            and samples_df_len > 0
            and self.features_df is not None
            and not self.features_df.is_empty()
        ):
            # Ensure matching data types for join keys
            features_dtype = self.features_df["feature_uid"].dtype
            consensus_dtype = self.consensus_mapping_df["feature_uid"].dtype

            if features_dtype != consensus_dtype:
                # Try to cast both to Int64, fallback to string if needed
                try:
                    self.features_df = self.features_df.with_columns(
                        pl.col("feature_uid").cast(pl.Int64),
                    )
                    self.consensus_mapping_df = self.consensus_mapping_df.with_columns(
                        pl.col("feature_uid").cast(pl.Int64),
                    )
                except Exception:
                    # If casting to Int64 fails, cast both to string
                    self.features_df = self.features_df.with_columns(
                        pl.col("feature_uid").cast(pl.Utf8),
                    )
                    self.consensus_mapping_df = self.consensus_mapping_df.with_columns(
                        pl.col("feature_uid").cast(pl.Utf8),
                    )

            # Use more efficient counting - count non-null chroms only for features in consensus mapping
            if (self.consensus_mapping_df is not None and 
                not self.consensus_mapping_df.is_empty()):
                non_null_chroms = (
                    self.features_df.join(
                        self.consensus_mapping_df.select("feature_uid"),
                        on="feature_uid",
                        how="inner",
                    )
                    .select(
                        pl.col("chrom").is_not_null().sum().alias("count"),
                    )
                    .item()
                )
            else:
                non_null_chroms = 0
            total_possible = samples_df_len * consensus_df_len
            chrom_completeness = (
                non_null_chroms / total_possible if total_possible > 0 else 0
            )
        else:
            chrom_completeness = 0

        # Calculate consensus features with MS2 (count unique consensus_uids with MS2)
        if self.consensus_ms2 is not None and not self.consensus_ms2.is_empty():
            consensus_with_ms2_count = self.consensus_ms2["consensus_uid"].n_unique()
        else:
            consensus_with_ms2_count = 0

        if self.consensus_df is not None and not self.consensus_df.is_empty():
            # Compute RT spread using only consensus rows with number_samples >= half the number of samples
            threshold = (
                self.consensus_df.select(pl.col("number_samples").max()).item() / 2
                if (self.samples_df is not None and not self.samples_df.is_empty())
                else 0
            )
            filtered = self.consensus_df.filter(pl.col("number_samples") >= threshold)
            if filtered.is_empty():
                rt_spread = -1.0
            else:
                rt_spread_row = filtered.select(
                    (pl.col("rt_max") - pl.col("rt_min")).mean(),
                ).row(0)
                rt_spread = (
                    float(rt_spread_row[0])
                    if rt_spread_row and rt_spread_row[0] is not None
                    else 0.0
                )
        else:
            rt_spread = -1.0

        # Calculate percentage of consensus features with MS2
        consensus_with_ms2_percentage = (
            (consensus_with_ms2_count / consensus_df_len * 100)
            if consensus_df_len > 0
            else 0
        )

        # Total MS2 spectra count
        total_ms2_count = (
            len(self.consensus_ms2) if (self.consensus_ms2 is not None and not self.consensus_ms2.is_empty()) else 0
        )

        # Estimate memory usage
        memory_usage = (
            (self.samples_df.estimated_size() if self.samples_df is not None else 0)
            + (self.features_df.estimated_size() if self.features_df is not None else 0)
            + (self.consensus_df.estimated_size() if self.consensus_df is not None else 0)
            + (self.consensus_ms2.estimated_size() if self.consensus_ms2 is not None else 0)
            + (self.consensus_mapping_df.estimated_size() if self.consensus_mapping_df is not None else 0)
        )

        # Calculate tight clusters count
        tight_clusters_count = 0
        if consensus_df_len > 0:
            try:
                tight_clusters_count = _count_tight_clusters(self, mz_tol=0.04, rt_tol=0.3)
            except Exception as e:
                # If tight clusters calculation fails, just use 0
                tight_clusters_count = 0

        # Add warning symbols for out-of-range values
        consensus_warning = f" {_WARNING_SYMBOL}" if consensus_df_len < 50 else ""

        rt_spread_text = "N/A" if rt_spread < 0 else f"{rt_spread:.3f}s"
        rt_spread_warning = (
            f" {_WARNING_SYMBOL}"
            if rt_spread >= 0 and (rt_spread > 5 or rt_spread < 0.1)
            else ""
        )

        chrom_completeness_pct = chrom_completeness * 100
        chrom_warning = (
            f" {_WARNING_SYMBOL}"
            if chrom_completeness_pct < 10 and chrom_completeness_pct >= 0
            else ""
        )

        max_samples_warning = ""
        if (
            isinstance(max_samples, (int, float))
            and samples_df_len > 0
            and max_samples > 0
        ):
            if max_samples < samples_df_len / 3.0:
                max_samples_warning = f" {_WARNING_SYMBOL}"
            elif max_samples < samples_df_len * 0.8:
                max_samples_warning = f" {_WARNING_SYMBOL}"

        # Add warning for tight clusters
        tight_clusters_warning = f" {_WARNING_SYMBOL}" if tight_clusters_count > 10 else ""

        summary = (
            f"Study folder:           {self.folder}\n"
            f"Last save:              {self.filename}\n"
            f"Samples:                {samples_df_len}\n"
            f"Features:               {unfilled_features_count}\n"
            f"- in consensus:         {ratio_in_consensus_to_total:.0f}%\n"
            f"- not in consensus:     {ratio_not_in_consensus_to_total:.0f}%\n"
            f"Consensus:              {consensus_df_len}{consensus_warning}\n"
            f"- RT spread:            {rt_spread_text}{rt_spread_warning}\n"
            f"- Tight clusters:       {tight_clusters_count}{tight_clusters_warning}\n"
            f"- Min samples count:    {min_samples:.0f}\n"
            f"- Mean samples count:   {mean_samples:.0f}\n"
            f"- Max samples count:    {max_samples:.0f}{max_samples_warning}\n"
            f"- with MS2:             {consensus_with_ms2_percentage:.0f}%\n"
            f"- total MS2:            {total_ms2_count}\n"
            f"Chrom completeness:     {chrom_completeness_pct:.0f}%{chrom_warning}\n"
            f"Memory usage:           {memory_usage / (1024**2):.2f} MB\n"
        )

        print(summary)


if __name__ == "__main__":
    # This block is executed when the script is run directly
    pass
