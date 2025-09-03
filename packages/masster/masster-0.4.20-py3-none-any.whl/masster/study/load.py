from __future__ import annotations

import os
import concurrent.futures
from datetime import datetime

import numpy as np
import polars as pl
import pyopenms as oms

from tqdm import tqdm

from masster.chromatogram import Chromatogram
from masster.study.defaults import fill_defaults
from masster.sample.sample import Sample
from masster.spectrum import Spectrum


# Pre-import heavy modules to avoid repeated loading in add_sample()
try:
    import alpharaw.sciex

    ALPHARAW_AVAILABLE = True
except ImportError:
    ALPHARAW_AVAILABLE = False

try:
    import pythonnet

    PYTHONNET_AVAILABLE = True
except ImportError:
    PYTHONNET_AVAILABLE = False

import glob


def add(
    self,
    folder=None,
    reset=False,
    adducts=None,
    max_files=None,
    fast=True,
):
    """Add samples from a folder to the study.

    Args:
        folder (str, optional): Path to folder containing sample files.
            Defaults to study folder or current working directory.
        reset (bool, optional): Whether to reset the study before adding samples.
            Defaults to False.
        adducts (optional): Adducts to use for sample loading. Defaults to None.
        max_files (int, optional): Maximum number of files to process.
            Defaults to None (no limit).
        fast (bool, optional): Whether to use optimized loading that skips ms1_df
            for better performance. Defaults to True.
    """
    if folder is None:
        if self.folder is not None:
            folder = self.folder
        else:
            folder = os.getcwd()

    self.logger.debug(f"Adding files from: {folder}")

    # Define file extensions to search for in order of priority
    extensions = [".sample5", ".wiff", ".raw", ".mzML"]

    # Check if folder contains glob patterns
    if not any(char in folder for char in ["*", "?", "[", "]"]):
        search_folder = folder
    else:
        search_folder = os.path.dirname(folder) if os.path.dirname(folder) else folder

    # Blacklist to track filenames without extensions that have already been processed
    blacklist = set()
    counter = 0
    not_zero = False
    tdqm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]

    # Search for files in order of priority
    for ext in extensions:
        if max_files is not None and counter >= max_files:
            break

        # Build search pattern
        if any(char in folder for char in ["*", "?", "[", "]"]):
            # If folder already contains glob patterns, use it as-is
            pattern = folder
        else:
            pattern = os.path.join(search_folder, "**", f"*{ext}")

        files = glob.glob(pattern, recursive=True)

        if len(files) > 0:
            # Limit files if max_files is specified
            remaining_slots = (
                max_files - counter if max_files is not None else len(files)
            )
            files = files[:remaining_slots]

            self.logger.debug(f"Found {len(files)} {ext} files")

            # Filter files not already processed and respect max_files limit
            files_to_process = []
            for file in files:
                if max_files is not None and counter >= max_files:
                    break

                # Get filename without extension for blacklist check
                basename = os.path.basename(file)
                filename_no_ext = os.path.splitext(basename)[0]

                # Check if this filename (without extension) is already in blacklist
                if filename_no_ext not in blacklist:
                    files_to_process.append(file)
                    if len(files_to_process) + counter >= (max_files or float("inf")):
                        break

            # Batch process all files of this extension using ultra-optimized method
            if files_to_process:
                self.logger.debug(
                    f"Batch processing {len(files_to_process)} {ext} files",
                )
                successful = self._add_samples_batch(
                    files_to_process,
                    reset=reset,
                    adducts=adducts,
                    blacklist=blacklist,
                    fast=fast,
                )
                counter += successful
                if successful > 0:
                    not_zero = True

    if max_files is not None and counter >= max_files:
        self.logger.debug(
            f"Reached maximum number of files to add: {max_files}. Stopping further additions.",
        )

    if not not_zero:
        self.logger.warning(
            f"No files found in {folder}. Please check the folder path or file patterns.",
        )
    else:
        self.logger.debug(f"Successfully added {counter} samples to the study.")

    # Return a simple summary to suppress marimo's automatic object display
    return f"Added {counter} samples to study"


# TODO type is not used
def add_sample(self, file, type=None, reset=False, adducts=None, fast=True):
    """
    Add a single sample to the study.

    Args:
        file (str): Path to the sample file
        type (str, optional): File type to force. Defaults to None (auto-detect).
        reset (bool, optional): Whether to reset the study. Defaults to False.
        adducts (optional): Adducts to use for sample loading. Defaults to None.
        fast (bool, optional): Whether to use optimized loading that skips ms1_df
            for better performance. Defaults to True.

    Returns:
        bool: True if successful, False otherwise.
    """
    if fast:
        # Use optimized method for better performance
        success = self._add_sample_optimized(
            file,
            type=type,
            reset=reset,
            adducts=adducts,
            skip_color_reset=False,  # Do color reset for individual calls
            skip_schema_check=True,  # Skip schema check for performance (safe with diagonal concat)
        )
    else:
        # Use standard method with full ms1_df loading
        success = self._add_sample_standard(
            file,
            type=type,
            reset=reset,
            adducts=adducts,
            skip_color_reset=False,  # Do color reset for individual calls
            skip_schema_check=True,  # Skip schema check for performance
        )

    return success


def load(self, filename=None):
    """
    Load a study from an HDF5 file.

    Args:
        study: The study object to load into
        filename (str, optional): The path to the HDF5 file to load the study from.
    """

    # Handle default filename
    if filename is None:
        if self.folder is not None:
            # search for *.study5 in folder
            study5_files = glob.glob(os.path.join(self.folder, "*.study5"))
            if study5_files:
                filename = study5_files[-1]
            else:
                self.logger.error("No .study5 files found in folder")
                return
        else:
            self.logger.error("Either filename or folder must be provided")
            return

    # self.logger.info(f"Loading study from {filename}")
    self._load_study5(filename)
    
    # After loading the study, check if we have consensus features before loading consensus XML
    if (self.consensus_df is not None and not self.consensus_df.is_empty()):
        consensus_xml_path = filename.replace(".study5", ".consensusXML")
        if os.path.exists(consensus_xml_path):
            self._load_consensusXML(filename=consensus_xml_path)
            # self.logger.info(f"Automatically loaded consensus from {consensus_xml_path}")
        else:
            self.logger.warning(f"No consensus XML file found at {consensus_xml_path}")
    else:
        self.logger.debug("No consensus features found, skipping consensusXML loading")
    
    self.filename = filename


def _fill_chrom_single_impl(
    self,
    uids=None,
    mz_tol: float = 0.010,
    rt_tol: float = 10.0,
    min_samples_rel: float = 0.0,
    min_samples_abs: int = 2,
):
    """Fill missing chromatograms by extracting from raw data.

    Simplified version that loads one sample at a time without preloading or batching.

    Args:
        uids: Consensus UIDs to process (default: all)
        mz_tol: m/z tolerance for extraction (default: 0.010 Da)
        rt_tol: RT tolerance for extraction (default: 10.0 seconds)
        min_samples_rel: Relative minimum sample threshold (default: 0.0)
        min_samples_abs: Absolute minimum sample threshold (default: 2)
    """
    uids = self._get_consensus_uids(uids)

    self.logger.info("Gap filling...")
    self.logger.debug(
        f"Parameters: mz_tol={mz_tol}, rt_tol={rt_tol}, min_samples_rel={min_samples_rel}, min_samples_abs={min_samples_abs}",
    )

    # Apply minimum sample filters
    min_number_rel = 1
    min_number_abs = 1
    if isinstance(min_samples_rel, float) and min_samples_rel > 0:
        min_number_rel = int(min_samples_rel * len(self.samples_df))
    if isinstance(min_samples_abs, int) and min_samples_abs > 0:
        min_number_abs = int(min_samples_abs)
    min_number = max(min_number_rel, min_number_abs)
    self.logger.debug(f"Threshold for gap filling: number_samples>={min_number}")

    if min_number > 0:
        original_count = len(uids)
        uids = self.consensus_df.filter(
            (pl.col("number_samples") >= min_number)
            & (pl.col("consensus_uid").is_in(uids)),
        )["consensus_uid"].to_list()
        self.logger.debug(
            f"Features to fill: {original_count} -> {len(uids)}",
        )
    self.logger.debug("Identifying missing features...")
    # Instead of building full chromatogram matrix, identify missing consensus/sample combinations directly
    missing_combinations = self._get_missing_consensus_sample_combinations(uids)
    if not missing_combinations:
        self.logger.info("No missing features found to fill.")
        return

    # Build lookup dictionaries
    self.logger.debug("Building lookup dictionaries...")
    consensus_info = {}
    consensus_subset = self.consensus_df.select(
        [
            "consensus_uid",
            "rt_start_mean",
            "rt_end_mean",
            "mz",
            "rt",
        ],
    ).filter(pl.col("consensus_uid").is_in(uids))

    for row in consensus_subset.iter_rows(named=True):
        consensus_info[row["consensus_uid"]] = {
            "rt_start_mean": row["rt_start_mean"],
            "rt_end_mean": row["rt_end_mean"],
            "mz": row["mz"],
            "rt": row["rt"],
        }

    # Process each sample individually
    # Group missing combinations by sample for efficient processing
    missing_by_sample = {}
    for consensus_uid, sample_uid, sample_name, sample_path in missing_combinations:
        if sample_name not in missing_by_sample:
            missing_by_sample[sample_name] = {
                "sample_uid": sample_uid,
                "sample_path": sample_path,
                "missing_consensus_uids": [],
            }
        missing_by_sample[sample_name]["missing_consensus_uids"].append(consensus_uid)

    new_features: list[dict] = []
    new_mapping: list[dict] = []
    counter = 0

    self.logger.debug(
        f"Missing features: {len(missing_combinations)} in {len(missing_by_sample)} samples...",
    )

    tdqm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]

    for sample_name, sample_info in tqdm(
        missing_by_sample.items(),
        desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}File",
        disable=tdqm_disable,
    ):
        # Load this sample
        sample_uid = sample_info["sample_uid"]
        sample_path = sample_info["sample_path"]
        missing_consensus_uids = sample_info["missing_consensus_uids"]

        try:
            # self.logger.debug(f"Loading sample: {sample_path}")
            file = Sample()
            file.logger_update("WARNING")
            file.load(sample_path)
        except Exception as e:
            self.logger.warning(f"Failed to load sample {sample_name}: {e}")
            continue

        self.logger.debug(
            f"Sample {sample_name}: Processing {len(missing_consensus_uids)} missing features",
        )

        # Process each missing feature
        for consensus_uid in missing_consensus_uids:
            cons = consensus_info[consensus_uid]
            mz = cons["mz"]
            rt = cons["rt"]
            rt_start_mean = cons["rt_start_mean"]
            rt_end_mean = cons["rt_end_mean"]

            # Filter MS1 data for this feature
            if hasattr(file, "ms1_df") and not file.ms1_df.is_empty():
                d = file.ms1_df.filter(
                    (pl.col("mz") >= mz - mz_tol)
                    & (pl.col("mz") <= mz + mz_tol)
                    & (pl.col("rt") >= rt_start_mean - rt_tol)
                    & (pl.col("rt") <= rt_end_mean + rt_tol),
                )
            else:
                d = pl.DataFrame()

            # Create chromatogram
            if d.is_empty():
                self.logger.debug(
                    f"Feature {consensus_uid}: No MS1 data found, creating empty chromatogram",
                )
                eic = Chromatogram(
                    rt=np.array([rt_start_mean, rt_end_mean]),
                    inty=np.array([0.0, 0.0]),
                    label=f"EIC mz={mz:.4f}",
                    file=sample_path,
                    mz=mz,
                    mz_tol=mz_tol,
                    feature_start=rt_start_mean,
                    feature_end=rt_end_mean,
                    feature_apex=rt,
                )
                max_inty = 0.0
                area = 0.0
            else:
                self.logger.debug(
                    f"Feature {consensus_uid}: Found {len(d)} MS1 points, creating EIC",
                )
                eic_rt = d.group_by("rt").agg(pl.col("inty").max()).sort("rt")

                if len(eic_rt) > 4:
                    eic = Chromatogram(
                        eic_rt["rt"].to_numpy(),
                        eic_rt["inty"].to_numpy(),
                        label=f"EIC mz={mz:.4f}",
                        file=sample_path,
                        mz=mz,
                        mz_tol=mz_tol,
                        feature_start=rt_start_mean,
                        feature_end=rt_end_mean,
                        feature_apex=rt,
                    ).find_peaks()
                    max_inty = np.max(eic.inty)
                    area = eic.feature_area
                else:
                    eic = Chromatogram(
                        eic_rt["rt"].to_numpy(),
                        eic_rt["inty"].to_numpy(),
                        label=f"EIC mz={mz:.4f}",
                        file=sample_path,
                        mz=mz,
                        mz_tol=mz_tol,
                        feature_start=rt_start_mean,
                        feature_end=rt_end_mean,
                        feature_apex=rt,
                    )
                    max_inty = 0.0
                    area = 0.0

            # Generate feature UID
            feature_uid = (
                self.features_df["feature_uid"].max() + len(new_features) + 1
                if not self.features_df.is_empty()
                else len(new_features) + 1
            )

            # Create new feature entry
            new_feature = {
                "sample_uid": sample_uid,
                "feature_uid": feature_uid,
                "feature_id": None,
                "mz": mz,
                "rt": rt,
                "rt_original": None,
                "rt_start": rt_start_mean,
                "rt_end": rt_end_mean,
                "rt_delta": rt_end_mean - rt_start_mean,
                "mz_start": None,
                "mz_end": None,
                "inty": max_inty,
                "quality": None,
                "charge": None,
                "iso": None,
                "iso_of": None,
                "adduct": None,
                "adduct_mass": None,
                "adduct_group": None,
                "chrom": eic,
                "chrom_coherence": None,
                "chrom_prominence": None,
                "chrom_prominence_scaled": None,
                "chrom_height_scaled": None,
                "ms2_scans": None,
                "ms2_specs": None,
                "filled": True,
                "chrom_area": area,
            }

            new_features.append(new_feature)
            new_mapping.append(
                {
                    "consensus_uid": consensus_uid,
                    "sample_uid": sample_uid,
                    "feature_uid": feature_uid,
                },
            )
            counter += 1

    # Add new features to DataFrames
    self.logger.debug(f"Adding {len(new_features)} new features to DataFrame...")
    if new_features:
        # Create properly formatted rows
        rows_to_add = []
        for feature_dict in new_features:
            new_row = {}
            for col in self.features_df.columns:
                if col in feature_dict:
                    new_row[col] = feature_dict[col]
                else:
                    new_row[col] = None
            rows_to_add.append(new_row)

        # Create and add new DataFrame
        if rows_to_add:
            # Ensure consistent data types by explicitly casting problematic columns
            for row in rows_to_add:
                # Cast numeric columns to ensure consistency
                for key, value in row.items():
                    if (
                        key in ["mz", "rt", "intensity", "area", "height"]
                        and value is not None
                    ):
                        row[key] = float(value)
                    elif key in ["sample_id", "feature_id"] and value is not None:
                        row[key] = int(value)

            new_df = pl.from_dicts(rows_to_add, infer_schema_length=len(rows_to_add))
        else:
            # Handle empty case - create empty DataFrame with proper schema
            new_df = pl.DataFrame(schema=self.features_df.schema)

        # Cast columns to match existing schema
        cast_exprs = []
        for col in self.features_df.columns:
            existing_dtype = self.features_df[col].dtype
            cast_exprs.append(pl.col(col).cast(existing_dtype, strict=False))

        new_df = new_df.with_columns(cast_exprs)
        self.features_df = self.features_df.vstack(new_df)

        # Add consensus mapping
        new_mapping_df = pl.DataFrame(new_mapping)
        self.consensus_mapping_df = pl.concat(
            [self.consensus_mapping_df, new_mapping_df],
            how="diagonal",
        )

    self.logger.info(f"Filled {counter} chromatograms from raw data.")


def fill_single(self, **kwargs):
    """Fill missing chromatograms by extracting from raw data.

    Simplified version that loads one sample at a time without preloading or batching.

    Parameters:
        **kwargs: Keyword arguments for fill_single parameters. Can include:
            - A fill_defaults instance to set all parameters at once
            - Individual parameter names and values (see fill_defaults for details)

    Key Parameters:
        uids: Consensus UIDs to process (default: all)
        mz_tol: m/z tolerance for extraction (default: 0.010 Da)
        rt_tol: RT tolerance for extraction (default: 10.0 seconds)
        min_samples_rel: Relative minimum sample threshold (default: 0.0)
        min_samples_abs: Absolute minimum sample threshold (default: 2)
    """
    # parameters initialization
    from masster.study.defaults import fill_defaults

    params = fill_defaults()

    for key, value in kwargs.items():
        if isinstance(value, fill_defaults):
            params = value
            self.logger.debug("Using provided fill_defaults parameters")
        else:
            if hasattr(params, key):
                if params.set(key, value, validate=True):
                    self.logger.debug(f"Updated parameter {key} = {value}")
                else:
                    self.logger.warning(
                        f"Failed to set parameter {key} = {value} (validation failed)",
                    )
            else:
                self.logger.debug(f"Unknown parameter {key} ignored")
    # end of parameter initialization

    # Store parameters in the Study object
    self.store_history(["fill_single"], params.to_dict())
    self.logger.debug("Parameters stored to fill_single")

    # Call the original fill_chrom_single function with extracted parameters
    return _fill_chrom_single_impl(
        self,
        uids=params.get("uids"),
        mz_tol=params.get("mz_tol"),
        rt_tol=params.get("rt_tol"),
        min_samples_rel=params.get("min_samples_rel"),
        min_samples_abs=params.get("min_samples_abs"),
    )


def _process_sample_for_parallel_fill(
    self,
    sample_info,
    consensus_info,
    uids,
    mz_tol,
    rt_tol,
    missing_combinations_df,
    features_df_max_uid,
):
    """Process a single sample for parallel gap filling."""
    sample_uid = sample_info["sample_uid"]
    sample_path = sample_info["sample_path"]

    new_features: list[dict] = []
    new_mapping: list[dict] = []
    counter = 0

    try:
        # Load this sample
        file = Sample()
        file.logger_update(level="WARNING")
        file.load(sample_path)
    except Exception:
        # Skip this sample if loading fails
        return new_features, new_mapping, counter

    # Find missing features for this sample from precomputed combinations
    sample_missing = missing_combinations_df.filter(
        pl.col("sample_uid") == sample_uid,
    )["consensus_uid"].to_list()

    if not sample_missing:
        return new_features, new_mapping, counter

    # Process each missing feature
    for consensus_uid in sample_missing:
        cons = consensus_info[consensus_uid]
        mz = cons["mz"]
        rt = cons["rt"]
        rt_start_mean = cons["rt_start_mean"]
        rt_end_mean = cons["rt_end_mean"]

        # Filter MS1 data for this feature
        if hasattr(file, "ms1_df") and not file.ms1_df.is_empty():
            d = file.ms1_df.filter(
                (pl.col("mz") >= mz - mz_tol)
                & (pl.col("mz") <= mz + mz_tol)
                & (pl.col("rt") >= rt_start_mean - rt_tol)
                & (pl.col("rt") <= rt_end_mean + rt_tol),
            )
        else:
            d = pl.DataFrame()

        # Create chromatogram
        if d.is_empty():
            eic = Chromatogram(
                rt=np.array([rt_start_mean, rt_end_mean]),
                inty=np.array([0.0, 0.0]),
                label=f"EIC mz={mz:.4f}",
                file=sample_path,
                mz=mz,
                mz_tol=mz_tol,
                feature_start=rt_start_mean,
                feature_end=rt_end_mean,
                feature_apex=rt,
            )
            max_inty = 0.0
            area = 0.0
        else:
            eic_rt = d.group_by("rt").agg(pl.col("inty").max()).sort("rt")

            if len(eic_rt) > 4:
                eic = Chromatogram(
                    eic_rt["rt"].to_numpy(),
                    eic_rt["inty"].to_numpy(),
                    label=f"EIC mz={mz:.4f}",
                    file=sample_path,
                    mz=mz,
                    mz_tol=mz_tol,
                    feature_start=rt_start_mean,
                    feature_end=rt_end_mean,
                    feature_apex=rt,
                ).find_peaks()
                max_inty = np.max(eic.inty)
                area = eic.feature_area
            else:
                eic = Chromatogram(
                    eic_rt["rt"].to_numpy(),
                    eic_rt["inty"].to_numpy(),
                    label=f"EIC mz={mz:.4f}",
                    file=sample_path,
                    mz=mz,
                    mz_tol=mz_tol,
                    feature_start=rt_start_mean,
                    feature_end=rt_end_mean,
                    feature_apex=rt,
                )
                max_inty = 0.0
                area = 0.0

        # Generate feature UID (will be adjusted later to ensure global uniqueness)
        feature_uid = features_df_max_uid + len(new_features) + 1

        # Create new feature entry
        new_feature = {
            "sample_uid": sample_uid,
            "feature_uid": feature_uid,
            "feature_id": None,
            "mz": mz,
            "rt": rt,
            "rt_original": None,
            "rt_start": rt_start_mean,
            "rt_end": rt_end_mean,
            "rt_delta": rt_end_mean - rt_start_mean,
            "mz_start": None,
            "mz_end": None,
            "inty": max_inty,
            "quality": None,
            "charge": None,
            "iso": None,
            "iso_of": None,
            "adduct": None,
            "adduct_mass": None,
            "adduct_group": None,
            "chrom": eic,
            "filled": True,
            "chrom_area": area,
            "chrom_coherence": None,
            "chrom_prominence": None,
            "chrom_prominence_scaled": None,
            "chrom_height_scaled": None,
            "ms2_scans": None,
            "ms2_specs": None,
        }

        new_features.append(new_feature)
        new_mapping.append(
            {
                "consensus_uid": consensus_uid,
                "sample_uid": sample_uid,
                "feature_uid": feature_uid,
            },
        )
        counter += 1

    return new_features, new_mapping, counter


def _fill_chrom_impl(
    self,
    uids=None,
    mz_tol: float = 0.010,
    rt_tol: float = 10.0,
    min_samples_rel: float = 0.0,
    min_samples_abs: int = 2,
    num_workers=4,
):
    """Fill missing chromatograms by extracting from raw data using parallel processing.

    Args:
        uids: Consensus UIDs to process (default: all)
        mz_tol: m/z tolerance for extraction (default: 0.010 Da)
        rt_tol: RT tolerance for extraction (default: 10.0 seconds)
        min_samples_rel: Relative minimum sample threshold (default: 0.0)
        min_samples_abs: Absolute minimum sample threshold (default: 2)
        num_workers: Number of parallel workers (default: 4)
    """
    uids = self._get_consensus_uids(uids)

    self.logger.info(f"Gap filling with {num_workers} workers...")
    self.logger.debug(
        f"Parameters: mz_tol={mz_tol}, rt_tol={rt_tol}, min_samples_rel={min_samples_rel}, min_samples_abs={min_samples_abs}, num_workers={num_workers}",
    )

    # Apply minimum sample filters
    min_number_rel = 1
    min_number_abs = 1
    if isinstance(min_samples_rel, float) and min_samples_rel > 0:
        min_number_rel = int(min_samples_rel * len(self.samples_df))
    if isinstance(min_samples_abs, int) and min_samples_abs > 0:
        min_number_abs = int(min_samples_abs)
    min_number = max(min_number_rel, min_number_abs)

    self.logger.debug(f"Threshold for gap filling: number_samples>={min_number}")

    if min_number > 0:
        original_count = len(uids)
        uids = self.consensus_df.filter(
            (pl.col("number_samples") >= min_number)
            & (pl.col("consensus_uid").is_in(uids)),
        )["consensus_uid"].to_list()
        self.logger.debug(f"Features to fill: {original_count} -> {len(uids)}")

    # Get missing consensus/sample combinations using the optimized method
    self.logger.debug("Identifying missing features...")
    missing_combinations = self._get_missing_consensus_sample_combinations(uids)

    if not missing_combinations or len(missing_combinations) == 0:
        self.logger.info("No missing features found to fill.")
        return

    # Convert to DataFrame for easier processing
    missing_combinations_df = pl.DataFrame(
        missing_combinations,
        schema={
            "consensus_uid": pl.Int64,
            "sample_uid": pl.Int64,
            "sample_name": pl.Utf8,
            "sample_path": pl.Utf8,
        },
        orient="row",
    )

    # Build lookup dictionaries
    self.logger.debug("Building lookup dictionaries...")
    consensus_info = {}
    consensus_subset = self.consensus_df.select(
        [
            "consensus_uid",
            "rt_start_mean",
            "rt_end_mean",
            "mz",
            "rt",
        ],
    ).filter(pl.col("consensus_uid").is_in(uids))

    for row in consensus_subset.iter_rows(named=True):
        consensus_info[row["consensus_uid"]] = {
            "rt_start_mean": row["rt_start_mean"],
            "rt_end_mean": row["rt_end_mean"],
            "mz": row["mz"],
            "rt": row["rt"],
        }

    # Get sample info for all samples that need processing
    samples_to_process = []
    unique_sample_uids = missing_combinations_df["sample_uid"].unique().to_list()

    for row in self.samples_df.filter(
        pl.col("sample_uid").is_in(unique_sample_uids),
    ).iter_rows(named=True):
        samples_to_process.append(
            {
                "sample_name": row["sample_name"],
                "sample_uid": row["sample_uid"],
                "sample_path": row["sample_path"],
            },
        )

    total_missing = len(missing_combinations_df)
    self.logger.debug(
        f"Gap filling for {total_missing} missing features...",
    )

    # Calculate current max feature_uid to avoid conflicts
    features_df_max_uid = (
        self.features_df["feature_uid"].max() if not self.features_df.is_empty() else 0
    )

    # Process samples in parallel
    all_new_features: list[dict] = []
    all_new_mapping: list[dict] = []
    total_counter = 0

    tdqm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        # Submit all samples for processing
        future_to_sample = {}
        for sample_info in samples_to_process:
            future = executor.submit(
                self._process_sample_for_parallel_fill,
                sample_info,
                consensus_info,
                uids,
                mz_tol,
                rt_tol,
                missing_combinations_df,
                features_df_max_uid,
            )
            future_to_sample[future] = sample_info

        # Collect results with progress bar
        with tqdm(
            total=len(samples_to_process),
            desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Processing samples",
            disable=tdqm_disable,
        ) as pbar:
            for future in concurrent.futures.as_completed(future_to_sample):
                try:
                    new_features, new_mapping, counter = future.result()

                    # Adjust feature UIDs to ensure global uniqueness
                    uid_offset = features_df_max_uid + len(all_new_features)
                    for i, feature in enumerate(new_features):
                        feature["feature_uid"] = uid_offset + i + 1
                    for i, mapping in enumerate(new_mapping):
                        mapping["feature_uid"] = uid_offset + i + 1

                    all_new_features.extend(new_features)
                    all_new_mapping.extend(new_mapping)
                    total_counter += counter

                except Exception as e:
                    sample_info = future_to_sample[future]
                    self.logger.warning(
                        f"Sample {sample_info['sample_name']} failed: {e}",
                    )

                pbar.update(1)

    # Add new features to DataFrames
    self.logger.debug(f"Adding {len(all_new_features)} new features to DataFrame...")
    if all_new_features:
        # Create properly formatted rows
        rows_to_add = []
        for feature_dict in all_new_features:
            new_row = {}
            for col in self.features_df.columns:
                if col in feature_dict:
                    new_row[col] = feature_dict[col]
                else:
                    new_row[col] = None
            rows_to_add.append(new_row)

        # Create and add new DataFrame
        if rows_to_add:
            # Ensure consistent data types by explicitly casting problematic columns
            for row in rows_to_add:
                # Cast numeric columns to ensure consistency
                for key, value in row.items():
                    if (
                        key in ["mz", "rt", "intensity", "area", "height"]
                        and value is not None
                    ):
                        row[key] = float(value)
                    elif key in ["sample_id", "feature_id"] and value is not None:
                        row[key] = int(value)

            new_df = pl.from_dicts(rows_to_add, infer_schema_length=len(rows_to_add))
        else:
            # Handle empty case - create empty DataFrame with proper schema
            new_df = pl.DataFrame(schema=self.features_df.schema)

        # Cast columns to match existing schema
        cast_exprs = []
        for col in self.features_df.columns:
            existing_dtype = self.features_df[col].dtype
            cast_exprs.append(pl.col(col).cast(existing_dtype, strict=False))

        new_df = new_df.with_columns(cast_exprs)
        self.features_df = self.features_df.vstack(new_df)

        # Add consensus mapping
        new_mapping_df = pl.DataFrame(all_new_mapping)
        self.consensus_mapping_df = pl.concat(
            [self.consensus_mapping_df, new_mapping_df],
            how="diagonal",
        )

    self.logger.info(
        f"Filled {total_counter} chromatograms from raw data using {num_workers} parallel workers.",
    )


def fill(self, **kwargs):
    """Fill missing chromatograms by extracting from raw data using parallel processing.

    Parameters:
        **kwargs: Keyword arguments for fill parameters. Can include:
            - A fill_defaults instance to set all parameters at once
            - Individual parameter names and values (see fill_defaults for details)

    Key Parameters:
        uids: Consensus UIDs to process (default: all)
        mz_tol: m/z tolerance for extraction (default: 0.010 Da)
        rt_tol: RT tolerance for extraction (default: 10.0 seconds)
        min_samples_rel: Relative minimum sample threshold (default: 0.05)
        min_samples_abs: Absolute minimum sample threshold (default: 5)
        num_workers: Number of parallel workers (default: 4)
    """
    # parameters initialization
    params = fill_defaults()
    num_workers = kwargs.get(
        "num_workers",
        4,
    )  # Default parameter not in defaults class

    for key, value in kwargs.items():
        if isinstance(value, fill_defaults):
            params = value
            self.logger.debug("Using provided fill_defaults parameters")
        else:
            if hasattr(params, key):
                if params.set(key, value, validate=True):
                    self.logger.debug(f"Updated parameter {key} = {value}")
                else:
                    self.logger.warning(
                        f"Failed to set parameter {key} = {value} (validation failed)",
                    )
            elif key != "num_workers":  # Allow num_workers as valid parameter
                self.logger.debug(f"Unknown parameter {key} ignored")
    # end of parameter initialization

    # Store parameters in the Study object
    self.store_history(["fill"], params.to_dict())
    self.logger.debug("Parameters stored to fill")

    # Call the original fill_chrom function with extracted parameters
    return _fill_chrom_impl(
        self,
        uids=params.get("uids"),
        mz_tol=params.get("mz_tol"),
        rt_tol=params.get("rt_tol"),
        min_samples_rel=params.get("min_samples_rel"),
        min_samples_abs=params.get("min_samples_abs"),
        num_workers=num_workers,
    )


# Backward compatibility alias
fill_chrom = fill


def _get_missing_consensus_sample_combinations(self, uids):
    """
    Efficiently identify which consensus_uid/sample combinations are missing.
    Returns a list of tuples: (consensus_uid, sample_uid, sample_name, sample_path)

    Optimized for common scenarios:
    - Early termination for fully-filled studies
    - Efficient dictionary lookups instead of expensive DataFrame joins
    - Smart handling of sparse vs dense missing data patterns
    """
    if not uids:
        return []

    n_consensus = len(uids)
    n_samples = len(self.samples_df)
    total_possible = n_consensus * n_samples

    # Quick early termination check for fully/nearly filled studies
    # This handles the common case where fill() is run on an already-filled study
    consensus_counts = (
        self.consensus_mapping_df.filter(pl.col("consensus_uid").is_in(uids))
        .group_by("consensus_uid")
        .agg(pl.count("feature_uid").alias("count"))
    )

    total_existing = (
        consensus_counts["count"].sum() if not consensus_counts.is_empty() else 0
    )

    # If >95% filled, likely no gaps (common case)
    if total_existing >= total_possible * 0.95:
        self.logger.debug(
            f"Study appears {total_existing / total_possible * 100:.1f}% filled, using sparse optimization",
        )

        # For sparse missing data, check each consensus feature individually
        missing_combinations = []
        uids_set = set(uids)

        # Build efficient lookups
        feature_to_sample = dict(
            self.features_df.select(["feature_uid", "sample_uid"]).iter_rows(),
        )

        # Get existing combinations for target UIDs only
        existing_by_consensus = {}
        for consensus_uid, feature_uid in self.consensus_mapping_df.select(
            [
                "consensus_uid",
                "feature_uid",
            ],
        ).iter_rows():
            if consensus_uid in uids_set and feature_uid in feature_to_sample:
                if consensus_uid not in existing_by_consensus:
                    existing_by_consensus[consensus_uid] = set()
                existing_by_consensus[consensus_uid].add(feature_to_sample[feature_uid])

        # Get sample info once
        all_samples = list(
            self.samples_df.select(
                ["sample_uid", "sample_name", "sample_path"],
            ).iter_rows(),
        )

        # Check for missing combinations
        for consensus_uid in uids:
            existing_samples = existing_by_consensus.get(consensus_uid, set())
            for sample_uid, sample_name, sample_path in all_samples:
                if sample_uid not in existing_samples:
                    missing_combinations.append(
                        (consensus_uid, sample_uid, sample_name, sample_path),
                    )

        return missing_combinations

    else:
        # For studies with many gaps, use bulk operations
        self.logger.debug(
            f"Study {total_existing / total_possible * 100:.1f}% filled, using bulk optimization",
        )

        # Build efficient lookups
        uids_set = set(uids)
        feature_to_sample = dict(
            self.features_df.select(["feature_uid", "sample_uid"]).iter_rows(),
        )

        # Build existing combinations set
        existing_combinations = {
            (consensus_uid, feature_to_sample[feature_uid])
            for consensus_uid, feature_uid in self.consensus_mapping_df.select(
                [
                    "consensus_uid",
                    "feature_uid",
                ],
            ).iter_rows()
            if consensus_uid in uids_set and feature_uid in feature_to_sample
        }

        # Get all sample info
        all_samples = list(
            self.samples_df.select(
                ["sample_uid", "sample_name", "sample_path"],
            ).iter_rows(),
        )

        # Generate all missing combinations
        missing_combinations = [
            (consensus_uid, sample_uid, sample_name, sample_path)
            for consensus_uid in uids
            for sample_uid, sample_name, sample_path in all_samples
            if (consensus_uid, sample_uid) not in existing_combinations
        ]

        return missing_combinations


def sanitize(self):
    """
    Sanitize features DataFrame to ensure all complex objects are properly typed.
    Convert serialized objects back to their proper types (Chromatogram, Spectrum).
    """
    if self.features_df is None or self.features_df.is_empty():
        return

    self.logger.debug(
        "Sanitizing features DataFrame to ensure all complex objects are properly typed.",
    )
    tdqm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]

    # Check if we have object columns that need sanitization
    has_chrom = "chrom" in self.features_df.columns
    has_ms2_specs = "ms2_specs" in self.features_df.columns

    if not has_chrom and not has_ms2_specs:
        self.logger.debug("No object columns found that need sanitization.")
        return

    # Convert to list of dictionaries for easier manipulation
    rows_data = []

    for row_dict in tqdm(
        self.features_df.iter_rows(named=True),
        total=len(self.features_df),
        desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     |{self.log_label}Sanitize features",
        disable=tdqm_disable,
    ):
        row_data = dict(row_dict)

        # Sanitize chrom column
        if has_chrom and row_data["chrom"] is not None:
            if not isinstance(row_data["chrom"], Chromatogram):
                try:
                    # Create new Chromatogram and populate from dict if needed
                    new_chrom = Chromatogram(rt=np.array([]), inty=np.array([]))
                    if hasattr(row_data["chrom"], "__dict__"):
                        new_chrom.from_dict(row_data["chrom"].__dict__)
                    else:
                        # If it's already a dict
                        new_chrom.from_dict(row_data["chrom"])
                    row_data["chrom"] = new_chrom
                except Exception as e:
                    self.logger.warning(f"Failed to sanitize chrom object: {e}")
                    row_data["chrom"] = None

        # Sanitize ms2_specs column
        if has_ms2_specs and row_data["ms2_specs"] is not None:
            if isinstance(row_data["ms2_specs"], list):
                sanitized_specs = []
                for ms2_specs in row_data["ms2_specs"]:
                    if not isinstance(ms2_specs, Spectrum):
                        try:
                            new_ms2_specs = Spectrum(
                                mz=np.array([0]),
                                inty=np.array([0]),
                            )
                            if hasattr(ms2_specs, "__dict__"):
                                new_ms2_specs.from_dict(ms2_specs.__dict__)
                            else:
                                new_ms2_specs.from_dict(ms2_specs)
                            sanitized_specs.append(new_ms2_specs)
                        except Exception as e:
                            self.logger.warning(
                                f"Failed to sanitize ms2_specs object: {e}",
                            )
                            sanitized_specs.append(None)
                    else:
                        sanitized_specs.append(ms2_specs)
                row_data["ms2_specs"] = sanitized_specs
            elif not isinstance(row_data["ms2_specs"], Spectrum):
                try:
                    new_ms2_specs = Spectrum(mz=np.array([0]), inty=np.array([0]))
                    if hasattr(row_data["ms2_specs"], "__dict__"):
                        new_ms2_specs.from_dict(row_data["ms2_specs"].__dict__)
                    else:
                        new_ms2_specs.from_dict(row_data["ms2_specs"])
                    row_data["ms2_specs"] = new_ms2_specs
                except Exception as e:
                    self.logger.warning(f"Failed to sanitize ms2_specs object: {e}")
                    row_data["ms2_specs"] = None

        rows_data.append(row_data)

    # Recreate the DataFrame with sanitized data
    try:
        self.features_df = pl.DataFrame(rows_data)
        self.logger.success("Features DataFrame sanitization completed successfully.")
    except Exception as e:
        self.logger.error(f"Failed to recreate sanitized DataFrame: {e}")


def load_features(self):
    """
    Load features by reconstructing FeatureMaps from the processed features_df data.

    This ensures that the loaded FeatureMaps contain the same processed features
    as stored in features_df, rather than loading raw features from .featureXML files
    which may not match the processed data after filtering, alignment, etc.
    """
    import polars as pl
    import pyopenms as oms
    from tqdm import tqdm
    from datetime import datetime

    self.features_maps = []

    # Check if features_df exists and is not empty
    if self.features_df is None:
        self.logger.warning("features_df is None. Falling back to XML loading.")
        self._load_features_from_xml()
        return

    if len(self.features_df) == 0:
        self.logger.warning("features_df is empty. Falling back to XML loading.")
        self._load_features_from_xml()
        return

    # If we get here, we should use the new method
    self.logger.debug("Reconstructing FeatureMaps from features_df.")

    tdqm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]

    # Process each sample in order
    for sample_index, row_dict in tqdm(
        enumerate(self.samples_df.iter_rows(named=True)),
        total=len(self.samples_df),
        desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Reconstruct FeatureMaps from DataFrame",
        disable=tdqm_disable,
    ):
        sample_uid = row_dict["sample_uid"]
        sample_name = row_dict["sample_name"]

        # Get features for this sample from features_df
        sample_features = self.features_df.filter(pl.col("sample_uid") == sample_uid)

        # Create new FeatureMap
        feature_map = oms.FeatureMap()

        # Convert DataFrame features to OpenMS Features
        for feature_row in sample_features.iter_rows(named=True):
            feature = oms.Feature()

            # Set properties from DataFrame (handle missing values gracefully)
            try:
                feature.setUniqueId(int(feature_row["feature_id"]))
                feature.setMZ(float(feature_row["mz"]))
                feature.setRT(float(feature_row["rt"]))
                feature.setIntensity(float(feature_row["inty"]))
                feature.setOverallQuality(float(feature_row["quality"]))
                feature.setCharge(int(feature_row["charge"]))

                # Add to feature map
                feature_map.push_back(feature)
            except (ValueError, TypeError) as e:
                self.logger.warning(f"Skipping feature due to conversion error: {e}")
                continue

        self.features_maps.append(feature_map)

    self.logger.debug(
        f"Successfully reconstructed {len(self.features_maps)} FeatureMaps from features_df.",
    )


def _load_features_from_xml(self):
    """
    Original load_features method that loads from .featureXML files.
    Used as fallback when features_df is not available.
    """
    self.features_maps = []
    self.logger.debug("Loading features from featureXML files.")
    tdqm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]
    for _index, row_dict in tqdm(
        enumerate(self.samples_df.iter_rows(named=True)),
        total=len(self.samples_df),
        desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Load feature maps from XML",
        disable=tdqm_disable,
    ):
        if self.folder is not None:
            filename = os.path.join(
                self.folder,
                row_dict["sample_name"] + ".featureXML",
            )
        else:
            filename = os.path.join(
                os.getcwd(),
                row_dict["sample_name"] + ".featureXML",
            )
        # check if file exists
        if not os.path.exists(filename):
            filename = row_dict["sample_path"].replace(".sample5", ".featureXML")

        if not os.path.exists(filename):
            self.features_maps.append(None)
            continue

        fh = oms.FeatureXMLFile()
        fm = oms.FeatureMap()
        fh.load(filename, fm)
        self.features_maps.append(fm)
    self.logger.debug("Features loaded successfully.")


def _load_consensusXML(self, filename="alignment.consensusXML"):
    """
    Load a consensus map from a file.
    """
    if not os.path.exists(filename):
        self.logger.error(f"File {filename} does not exist.")
        return
    fh = oms.ConsensusXMLFile()
    self.consensus_map = oms.ConsensusMap()
    fh.load(filename, self.consensus_map)
    self.logger.debug(f"Loaded consensus map from {filename}.")


def _add_samples_batch(
    self,
    files,
    reset=False,
    adducts=None,
    blacklist=None,
    fast=True,
):
    """
    Optimized batch addition of samples.

    Args:
        files (list): List of file paths to process
        reset (bool): Whether to reset features before processing
        adducts: Adducts to use for sample loading
        blacklist (set): Set of filenames already processed
        fast (bool): Whether to use optimized loading (skips ms1_df) or standard loading

    Performance optimizations:
    1. No per-sample color reset
    2. No schema enforcement during addition
    3. Simplified DataFrame operations
    4. Batch progress reporting
    """
    if not files:
        return 0

    if blacklist is None:
        blacklist = set()

    self.logger.debug(
        f"Starting batch addition of {len(files)} samples (skip_ms1={fast})...",
    )

    successful_additions = 0
    failed_additions = 0

    # Progress reporting setup
    tqdm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]

    for i, file in enumerate(
        tqdm(
            files,
            total=len(files),
            desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Add samples",
            disable=tqdm_disable,
        ),
    ):
        try:
            # Choose between optimized and standard loading
            if fast:
                success = self._add_sample_optimized(
                    file,
                    reset=reset,
                    adducts=adducts,
                    skip_color_reset=True,  # Skip color reset during batch
                    skip_schema_check=True,  # Skip schema enforcement
                )
            else:
                success = self._add_sample_standard(
                    file,
                    reset=reset,
                    adducts=adducts,
                    skip_color_reset=True,  # Skip color reset during batch
                    skip_schema_check=True,  # Skip schema enforcement
                )

            if success:
                # Add to blacklist for filename tracking
                basename = os.path.basename(file)
                filename_no_ext = os.path.splitext(basename)[0]
                blacklist.add(filename_no_ext)
                successful_additions += 1

        except Exception as e:
            self.logger.warning(f"Failed to add sample {file}: {e}")
            failed_additions += 1
            continue

    # Final cleanup operations done once at the end
    if successful_additions > 0:
        self.logger.debug("Performing final batch cleanup...")

        # Optional: Only do schema enforcement if specifically needed (usually not required)
        # self._ensure_features_df_schema_order()

        # Color assignment done once for all samples
        self._sample_color_reset_optimized()

        self.logger.debug(
            f"Add samples complete: {successful_additions} successful, {failed_additions} failed",
        )

    return successful_additions


def _add_sample_optimized(
    self,
    file,
    type=None,
    reset=False,
    adducts=None,
    skip_color_reset=True,
    skip_schema_check=True,
):
    """
    Optimized add_sample with performance improvements integrated.

    Removes:
    - Schema enforcement (_ensure_features_df_schema_order)
    - Complex column alignment and type casting
    - Per-addition color reset
    - Unnecessary column reordering

    Returns True if successful, False otherwise.
    """
    self.logger.debug(f"Adding: {file}")

    # Basic validation
    basename = os.path.basename(file)
    sample_name = os.path.splitext(basename)[0]

    if sample_name in self.samples_df["sample_name"].to_list():
        self.logger.warning(f"Sample {sample_name} already exists. Skipping.")
        return False

    if not os.path.exists(file):
        self.logger.error(f"File {file} does not exist.")
        return False

    if not file.endswith((".sample5", ".wiff", ".raw", ".mzML")):
        self.logger.error(f"Unsupported file type: {file}")
        return False

    # Load sample
    ddaobj = Sample()
    ddaobj.logger_update(level="WARNING", label=os.path.basename(file))

    # Try optimized loading first (study-specific, skips ms1_df for better performance)

    if file.endswith(".sample5"):
        ddaobj.load_noms1(file)
        # restore _oms_features_map
        ddaobj._get_feature_map()
    else:
        try:
            ddaobj.load(file)
            ddaobj.find_features()
            ddaobj.find_adducts(adducts=adducts)
            ddaobj.find_ms2()
        except Exception as e:
            self.logger.warning(f"Failed to add sample {file}: {e}")
            return False

    # Check if features map was created successfully
    if ddaobj._oms_features_map is None:
        self.logger.warning(f"Failed to add sample {file}: No features map created")
        return False

    self.features_maps.append(ddaobj._oms_features_map)

    # Determine sample type
    sample_type = "sample" if type is None else type
    if "qc" in sample_name.lower():
        sample_type = "qc"
    if "blank" in sample_name.lower():
        sample_type = "blank"

    map_id_value = len(self.features_maps) - 1

    # Handle file paths
    if file.endswith(".sample5"):
        final_sample_path = file
        # self.logger.debug(f"Using existing .sample5 file: {final_sample_path}")
    else:
        if self.folder is not None:
            if not os.path.exists(self.folder):
                os.makedirs(self.folder)
            final_sample_path = os.path.join(self.folder, sample_name + ".sample5")
        else:
            final_sample_path = os.path.join(os.getcwd(), sample_name + ".sample5")
        ddaobj.save(final_sample_path)
        self.logger.debug(f"Saved converted sample: {final_sample_path}")

    # Efficient scan counting
    ms1_count = ms2_count = 0
    if (
        hasattr(ddaobj, "scans_df")
        and ddaobj.scans_df is not None
        and not ddaobj.scans_df.is_empty()
    ):
        scan_counts = (
            ddaobj.scans_df.group_by("ms_level").len().to_dict(as_series=False)
        )
        ms_levels = scan_counts.get("ms_level", [])
        counts = scan_counts.get("len", [])
        for level, count in zip(ms_levels, counts):
            if level == 1:
                ms1_count = count
            elif level == 2:
                ms2_count = count

    # Create sample entry
    next_sequence = len(self.samples_df) + 1 if not self.samples_df.is_empty() else 1
    new_sample = pl.DataFrame(
        {
            "sample_uid": [int(len(self.samples_df) + 1)],
            "sample_name": [sample_name],
            "sample_path": [final_sample_path],
            "sample_type": [sample_type],
            "map_id": [map_id_value],
            "sample_source": [getattr(ddaobj, "file_source", file)],
            "sample_color": [None],  # Will be set in batch at end
            "sample_group": [""],
            "sample_batch": [1],
            "sample_sequence": [next_sequence],
            "num_features": [int(ddaobj._oms_features_map.size())],
            "num_ms1": [ms1_count],
            "num_ms2": [ms2_count],
        },
    )

    self.samples_df = pl.concat([self.samples_df, new_sample])

    # SIMPLIFIED feature processing
    current_sample_uid = len(self.samples_df)

    # Add required columns with minimal operations
    columns_to_add = [
        pl.lit(current_sample_uid).alias("sample_uid"),
        pl.lit(False).alias("filled"),
        pl.lit(-1.0).alias("chrom_area"),
    ]

    # Only add rt_original if it doesn't exist
    if "rt_original" not in ddaobj.features_df.columns:
        columns_to_add.append(pl.col("rt").alias("rt_original"))

    f_df = ddaobj.features_df.with_columns(columns_to_add)

    if self.features_df.is_empty():
        # First sample
        self.features_df = f_df.with_columns(
            pl.int_range(pl.len()).add(1).alias("feature_uid"),
        )
    else:
        # Subsequent samples - minimal overhead
        offset = self.features_df["feature_uid"].max() + 1
        f_df = f_df.with_columns(
            pl.int_range(pl.len()).add(offset).alias("feature_uid"),
        )

        # OPTIMIZED: Use diagonal concatenation without any schema enforcement
        # This is the fastest concatenation method in Polars and handles type mismatches automatically
        self.features_df = pl.concat([self.features_df, f_df], how="diagonal")

    # REMOVED ALL EXPENSIVE OPERATIONS:
    # - No _ensure_features_df_schema_order()
    # - No complex column alignment
    # - No type casting loops
    # - No sample_color_reset()

    self.logger.debug(
        f"Added sample {sample_name} with {ddaobj._oms_features_map.size()} features (optimized)",
    )
    return True


def _add_sample_standard(
    self,
    file,
    type=None,
    reset=False,
    adducts=None,
    skip_color_reset=True,
    skip_schema_check=True,
):
    """
    Standard add_sample method that uses full sample loading (includes ms1_df).

    This method uses the standard sample.load() method which loads all data
    including ms1_df, providing full functionality but potentially slower performance
    for large MS1 datasets.

    Returns True if successful, False otherwise.
    """
    self.logger.debug(f"Adding (standard): {file}")

    # Basic validation
    basename = os.path.basename(file)
    sample_name = os.path.splitext(basename)[0]

    if sample_name in self.samples_df["sample_name"].to_list():
        self.logger.warning(f"Sample {sample_name} already exists. Skipping.")
        return False

    if not os.path.exists(file):
        self.logger.error(f"File {file} does not exist.")
        return False

    if not file.endswith((".sample5", ".wiff", ".raw", ".mzML")):
        self.logger.error(f"Unsupported file type: {file}")
        return False

    # Load sample using standard method (includes ms1_df)
    ddaobj = Sample()
    ddaobj.logger_update(level="WARNING", label=os.path.basename(file))
    # Use standard loading method that loads all data including ms1_df

    if file.endswith(".sample5"):
        ddaobj.load(file)
        # restore _oms_features_map
        ddaobj._get_feature_map()
    else:
        try:
            ddaobj.load(file)
            ddaobj.find_features()
            ddaobj.find_adducts(adducts=adducts)
            ddaobj.find_ms2()
        except Exception as e:
            self.logger.warning(f"Failed to add sample {file}: {e}")
            return False

    # Check if features map was created successfully
    if ddaobj._oms_features_map is None:
        self.logger.warning(f"Failed to add sample {file}: No features map created")
        return False

    self.features_maps.append(ddaobj._oms_features_map)

    # Determine sample type
    sample_type = "sample" if type is None else type
    if "qc" in sample_name.lower():
        sample_type = "qc"
    if "blank" in sample_name.lower():
        sample_type = "blank"

    map_id_value = len(self.features_maps) - 1

    # Handle file paths
    if file.endswith(".sample5"):
        final_sample_path = file
        # self.logger.trace(f"Using existing .sample5 file: {final_sample_path}")
    else:
        if self.folder is not None:
            if not os.path.exists(self.folder):
                os.makedirs(self.folder)
            final_sample_path = os.path.join(self.folder, sample_name + ".sample5")
        else:
            final_sample_path = os.path.join(os.getcwd(), sample_name + ".sample5")
        ddaobj.save(final_sample_path)
        self.logger.debug(f"Saved converted sample: {final_sample_path}")

    # Efficient scan counting
    ms1_count = ms2_count = 0
    if (
        hasattr(ddaobj, "scans_df")
        and ddaobj.scans_df is not None
        and not ddaobj.scans_df.is_empty()
    ):
        scan_counts = (
            ddaobj.scans_df.group_by("ms_level").len().to_dict(as_series=False)
        )
        ms_levels = scan_counts.get("ms_level", [])
        counts = scan_counts.get("len", [])
        for level, count in zip(ms_levels, counts):
            if level == 1:
                ms1_count = count
            elif level == 2:
                ms2_count = count

    # Create sample entry
    next_sequence = len(self.samples_df) + 1 if not self.samples_df.is_empty() else 1
    new_sample = pl.DataFrame(
        {
            "sample_uid": [int(len(self.samples_df) + 1)],
            "sample_name": [sample_name],
            "sample_path": [final_sample_path],
            "sample_type": [sample_type],
            "map_id": [map_id_value],
            "sample_source": [getattr(ddaobj, "file_source", file)],
            "sample_color": [None],  # Will be set in batch at end
            "sample_group": [""],
            "sample_batch": [1],
            "sample_sequence": [next_sequence],
            "num_features": [int(ddaobj._oms_features_map.size())],
            "num_ms1": [ms1_count],
            "num_ms2": [ms2_count],
        },
    )

    self.samples_df = pl.concat([self.samples_df, new_sample])

    # SIMPLIFIED feature processing
    current_sample_uid = len(self.samples_df)

    # Add required columns with minimal operations
    columns_to_add = [
        pl.lit(current_sample_uid).alias("sample_uid"),
        pl.lit(False).alias("filled"),
        pl.lit(-1.0).alias("chrom_area"),
    ]

    # Only add rt_original if it doesn't exist
    if "rt_original" not in ddaobj.features_df.columns:
        columns_to_add.append(pl.col("rt").alias("rt_original"))

    f_df = ddaobj.features_df.with_columns(columns_to_add)

    if self.features_df.is_empty():
        # First sample
        self.features_df = f_df.with_columns(
            pl.int_range(pl.len()).add(1).alias("feature_uid"),
        )
    else:
        # Subsequent samples - minimal overhead
        offset = self.features_df["feature_uid"].max() + 1
        f_df = f_df.with_columns(
            pl.int_range(pl.len()).add(offset).alias("feature_uid"),
        )

        # Use diagonal concatenation for flexibility
        self.features_df = pl.concat([self.features_df, f_df], how="diagonal")

    self.logger.debug(
        f"Added sample {sample_name} with {ddaobj._oms_features_map.size()} features (standard)",
    )
    return True
    ## COMMENT AR: Is this intentional?
    # Use standard loading method that loads all data including ms1_df
    ddaobj.load(file)

    if ddaobj.features_df is None and not reset:
        ddaobj._oms_features_map = None

    if ddaobj._oms_features_map is None or reset:
        ddaobj.find_features()
        ddaobj.find_adducts(adducts=adducts)
        ddaobj.find_ms2()

    self.features_maps.append(ddaobj._oms_features_map)

    # Determine sample type
    sample_type = "sample" if type is None else type
    if "qc" in sample_name.lower():
        sample_type = "qc"
    if "blank" in sample_name.lower():
        sample_type = "blank"

    map_id_value = len(self.features_maps) - 1

    # Handle file paths
    if file.endswith(".sample5"):
        final_sample_path = file
        # self.logger.trace(f"Using existing .sample5 file: {final_sample_path}")
    else:
        if self.folder is not None:
            if not os.path.exists(self.folder):
                os.makedirs(self.folder)
            final_sample_path = os.path.join(self.folder, sample_name + ".sample5")
        else:
            final_sample_path = os.path.join(os.getcwd(), sample_name + ".sample5")
        ddaobj.save(final_sample_path)
        self.logger.debug(f"Saved converted sample: {final_sample_path}")

    # Efficient scan counting
    ms1_count = ms2_count = 0
    if (
        hasattr(ddaobj, "scans_df")
        and ddaobj.scans_df is not None
        and not ddaobj.scans_df.is_empty()
    ):
        scan_counts = (
            ddaobj.scans_df.group_by("ms_level").len().to_dict(as_series=False)
        )
        ms_levels = scan_counts.get("ms_level", [])
        counts = scan_counts.get("len", [])
        for level, count in zip(ms_levels, counts):
            if level == 1:
                ms1_count = count
            elif level == 2:
                ms2_count = count

    # Create sample entry
    next_sequence = len(self.samples_df) + 1 if not self.samples_df.is_empty() else 1
    new_sample = pl.DataFrame(
        {
            "sample_uid": [int(len(self.samples_df) + 1)],
            "sample_name": [sample_name],
            "sample_path": [final_sample_path],
            "sample_type": [sample_type],
            "map_id": [map_id_value],
            "sample_source": [getattr(ddaobj, "file_source", file)],
            "sample_color": [None],  # Will be set in batch at end
            "sample_group": [""],
            "sample_batch": [1],
            "sample_sequence": [next_sequence],
            "num_features": [int(ddaobj._oms_features_map.size())],
            "num_ms1": [ms1_count],
            "num_ms2": [ms2_count],
        },
    )

    self.samples_df = pl.concat([self.samples_df, new_sample])

    # SIMPLIFIED feature processing
    current_sample_uid = len(self.samples_df)

    # Add required columns with minimal operations
    columns_to_add = [
        pl.lit(current_sample_uid).alias("sample_uid"),
        pl.lit(False).alias("filled"),
        pl.lit(-1.0).alias("chrom_area"),
    ]

    # Only add rt_original if it doesn't exist
    if "rt_original" not in ddaobj.features_df.columns:
        columns_to_add.append(pl.col("rt").alias("rt_original"))

    f_df = ddaobj.features_df.with_columns(columns_to_add)

    if self.features_df.is_empty():
        # First sample
        self.features_df = f_df.with_columns(
            pl.int_range(pl.len()).add(1).alias("feature_uid"),
        )
    else:
        # Subsequent samples - minimal overhead
        offset = self.features_df["feature_uid"].max() + 1
        f_df = f_df.with_columns(
            pl.int_range(pl.len()).add(offset).alias("feature_uid"),
        )

        # Use diagonal concatenation for flexibility
        self.features_df = pl.concat([self.features_df, f_df], how="diagonal")

    self.logger.debug(
        f"Added sample {sample_name} with {ddaobj._oms_features_map.size()} features (standard)",
    )
    return True


def _sample_color_reset_optimized(self):
    """
    Optimized version of sample_color_reset that caches colormap initialization.
    """
    if self.samples_df is None or len(self.samples_df) == 0:
        self.logger.warning("No samples found in study.")
        return

    # Cache the colormap if not already cached
    if not hasattr(self, "_cached_colormap"):
        try:
            from cmap import Colormap

            self._cached_colormap = Colormap("turbo")
        except ImportError:
            self.logger.warning("cmap package not available, using default colors")
            return

    cm = self._cached_colormap
    n_samples = len(self.samples_df)

    # Pre-allocate colors list for better performance
    colors = [None] * n_samples

    # Vectorized color generation
    for i in range(n_samples):
        normalized_value = 0.1 + ((i + 0.5) / n_samples) * 0.8
        color_rgba = cm(normalized_value)

        if len(color_rgba) >= 3:
            r, g, b = color_rgba[:3]
            if max(color_rgba[:3]) <= 1.0:
                r, g, b = int(r * 255), int(g * 255), int(b * 255)
            colors[i] = f"#{r:02x}{g:02x}{b:02x}"

    # Update the sample_color column efficiently
    self.samples_df = self.samples_df.with_columns(
        pl.Series("sample_color", colors).alias("sample_color"),
    )

    self.logger.debug(f"Reset sample colors (cached) for {n_samples} samples")
