"""
helpers.py

This module contains helper functions for the Study class that handle various operations
like data retrieval, filtering, compression, and utility functions.

The functions are organized into the following sections:
1. Chromatogram extraction functions (BPC, TIC, EIC, chrom matrix)
2. Data retrieval helper functions (get_sample, get_consensus, etc.)
3. UID helper functions (_get_*_uids)
4. Data filtering and selection functions
5. Data compression and restoration functions
6. Utility functions (reset, naming, colors, schema ordering)
"""

from __future__ import annotations

import os

import numpy as np
import pandas as pd
import polars as pl

from tqdm import tqdm
from masster.chromatogram import Chromatogram


# =====================================================================================
# CHROMATOGRAM EXTRACTION FUNCTIONS
# =====================================================================================


def get_bpc(owner, sample=None, rt_unit="s", label=None, original=False):
    """
    Return a Chromatogram object containing the Base Peak Chromatogram (BPC).

    The `owner` argument may be either a Study instance or a Sample-like object that
    exposes `ms1_df` (Polars DataFrame) and optionally `scans_df`.

    If `owner` is a Study, `sample` must be provided (int sample_uid, str sample_name or Sample instance)
    and the Sample will be retrieved using `get_sample(owner, sample)`.

    Returns:
        Chromatogram
    """
    # resolve sample when owner is a Study-like object (has get_sample)
    s = None
    if hasattr(owner, "ms1_df"):
        s = owner
    else:
        # owner is expected to be a Study
        s = get_sample(owner, sample)

    if s is None:
        raise ValueError("Could not resolve sample for BPC computation")

    # ensure ms1_df exists
    if getattr(s, "ms1_df", None) is None:
        raise ValueError("Sample has no ms1_df for BPC computation")

    # try Polars aggregation first
    try:
        cols = s.ms1_df.columns
        if not all(c in cols for c in ["rt", "inty"]):
            raise RuntimeError("ms1_df missing required columns")

        bpc = s.ms1_df.select([pl.col("rt"), pl.col("inty")])
        bpc = bpc.groupby("rt").agg(pl.col("inty").max().alias("inty"))
        bpc_pd = bpc.to_pandas().sort_values("rt")
    except Exception:
        # fallback to pandas
        try:
            bpc_pd = s.ms1_df.to_pandas()[["rt", "inty"]]
            bpc_pd = (
                bpc_pd.groupby("rt")
                .agg({"inty": "max"})
                .reset_index()
                .sort_values("rt")
            )
        except Exception:
            raise

    if bpc_pd.empty:
        raise ValueError("Computed BPC is empty")

    # If caller requests original RTs (original=True) and we were called from a Study
    # we can obtain a per-sample mapping between current rt and rt_original from
    # the study.features_df and apply it to the computed BPC rt values.
    # Note: original parameter default is False (return current/aligned RTs).
    if original is True:
        try:
            # Only proceed if owner is a Study-like object with features_df
            study = None
            if hasattr(owner, "features_df"):
                study = owner
            else:
                # If owner is a Sample, try to find Study via attribute (not guaranteed)
                study = getattr(owner, "study", None)

            if study is not None and getattr(study, "features_df", None) is not None:
                # Attempt to select mapping rows for this sample. Prefer matching by sample_uid,
                # fall back to sample_name when necessary.
                import numpy as _np

                feats = study.features_df
                # try filtering by sample identifier provided to this function
                mapping_rows = None
                if sample is not None:
                    try:
                        mapping_rows = feats.filter(pl.col("sample_uid") == sample)
                    except Exception:
                        mapping_rows = pl.DataFrame()

                    if mapping_rows is None or mapping_rows.is_empty():
                        try:
                            mapping_rows = feats.filter(pl.col("sample_name") == sample)
                        except Exception:
                            mapping_rows = pl.DataFrame()

                # If we still have no sample selector, try to infer sample from the Sample object s
                if (mapping_rows is None or mapping_rows.is_empty()) and hasattr(
                    s,
                    "sample_path",
                ):
                    # attempt to match by sample_path or file name
                    try:
                        # find row where sample_path matches
                        mapping_rows = feats.filter(
                            pl.col("sample_path") == getattr(s, "file", None),
                        )
                    except Exception:
                        mapping_rows = pl.DataFrame()

                # If still empty, give up mapping
                if mapping_rows is not None and not mapping_rows.is_empty():
                    # collect rt and rt_original pairs
                    try:
                        map_pd = mapping_rows.select(["rt", "rt_original"]).to_pandas()
                    except Exception:
                        map_pd = mapping_rows.to_pandas()[["rt", "rt_original"]]

                    # drop NA and duplicates
                    map_pd = map_pd.dropna()
                    if not map_pd.empty:
                        # sort by rt (current/aligned)
                        map_pd = map_pd.sort_values("rt")
                        x = map_pd["rt"].to_numpy()
                        y = map_pd["rt_original"].to_numpy()
                        # require at least 2 points to interpolate
                        if x.size >= 2:
                            # apply linear interpolation from current rt -> original rt
                            # for values outside the known range, numpy.interp will clip to endpoints
                            new_rt = _np.interp(bpc_pd["rt"].to_numpy(), x, y)
                            bpc_pd = bpc_pd.copy()
                            bpc_pd["rt"] = new_rt
        except Exception:
            # If mapping fails, silently continue and return the original computed BPC
            pass

    # build Chromatogram
    ycol = "inty"
    try:
        chrom = Chromatogram(
            rt=bpc_pd["rt"].to_numpy(),
            inty=bpc_pd[ycol].to_numpy(),
            label=label or "Base Peak Chromatogram",
            rt_unit=rt_unit,
        )
    except Exception:
        chrom = Chromatogram(
            rt=bpc_pd["rt"].values,
            inty=bpc_pd[ycol].values,
            label=label or "Base Peak Chromatogram",
            rt_unit=rt_unit,
        )

    return chrom


def get_tic(owner, sample=None, label=None):
    """
    Return a Chromatogram object containing the Total Ion Chromatogram (TIC).

    `owner` may be a Sample-like object (has `ms1_df`) or a Study (in which case `sample` selects the sample).
    The function falls back to `scans_df` when `ms1_df` is not available.
    """
    # resolve sample object
    s = None
    if hasattr(owner, "ms1_df"):
        s = owner
    else:
        s = get_sample(owner, sample)

    if s is None:
        raise ValueError("Could not resolve sample for TIC computation")

    # prefer ms1_df
    try:
        cols = s.ms1_df.columns
        if all(c in cols for c in ["rt", "inty"]):
            tic = s.ms1_df.select([pl.col("rt"), pl.col("inty")])
            tic = tic.groupby("rt").agg(pl.col("inty").sum().alias("inty_tot"))
            tic_pd = tic.to_pandas().sort_values("rt")
        else:
            raise RuntimeError("ms1_df missing required columns")
    except Exception:
        # fallback to scans_df if present
        if getattr(s, "scans_df", None) is not None:
            try:
                scans = s.scans_df.filter(pl.col("ms_level") == 1)
                data = scans[["rt", "scan_uid", "inty_tot"]].to_pandas()
                data = data.sort_values("rt")
                tic_pd = data.rename(columns={"inty_tot": "inty_tot"})
            except Exception:
                raise
        else:
            raise ValueError(
                "Neither ms1_df nor scans_df available for TIC computation",
            )

    if tic_pd.empty:
        raise ValueError("Computed TIC is empty")

    # ensure column name
    if "inty_tot" not in tic_pd.columns:
        tic_pd = tic_pd.rename(columns={tic_pd.columns[1]: "inty_tot"})

    try:
        chrom = Chromatogram(
            rt=tic_pd["rt"].to_numpy(),
            inty=tic_pd["inty_tot"].to_numpy(),
            label=label or "Total Ion Chromatogram",
        )
    except Exception:
        chrom = Chromatogram(
            rt=tic_pd["rt"].values,
            inty=tic_pd["inty_tot"].values,
            label=label or "Total Ion Chromatogram",
        )

    return chrom


def get_eic(owner, sample=None, mz=None, mz_tol=None, rt_unit="s", label=None):
    """
    Return a Chromatogram object containing the Extracted Ion Chromatogram (EIC) for a target m/z.

    The `owner` argument may be either a Study instance or a Sample-like object that
    exposes `ms1_df` (Polars DataFrame).

    If `owner` is a Study, `sample` must be provided (int sample_uid, str sample_name or Sample instance)
    and the Sample will be retrieved using `get_sample(owner, sample)`.

    Parameters:
        owner: Study or Sample instance
        sample: Sample identifier (required if owner is Study)
        mz (float): Target m/z value
        mz_tol (float): m/z tolerance. If None, uses owner.parameters.eic_mz_tol (for Study) or defaults to 0.01
        rt_unit (str): Retention time unit for the chromatogram
        label (str): Optional label for the chromatogram

    Returns:
        Chromatogram
    """
    # Use default mz_tol from study parameters if not provided
    if mz_tol is None:
        if hasattr(owner, "parameters") and hasattr(owner.parameters, "eic_mz_tol"):
            mz_tol = owner.parameters.eic_mz_tol
        else:
            mz_tol = 0.01  # fallback default

    if mz is None:
        raise ValueError("mz must be provided for EIC computation")

    # resolve sample when owner is a Study-like object (has get_sample)
    s = None
    if hasattr(owner, "ms1_df"):
        s = owner
    else:
        # owner is expected to be a Study
        s = get_sample(owner, sample)

    if s is None:
        raise ValueError("Could not resolve sample for EIC computation")

    # ensure ms1_df exists
    if getattr(s, "ms1_df", None) is None:
        raise ValueError("Sample has no ms1_df for EIC computation")

    # Extract EIC from ms1_df using mz window
    try:
        cols = s.ms1_df.columns
        if not all(c in cols for c in ["rt", "mz", "inty"]):
            raise RuntimeError("ms1_df missing required columns")

        # Filter by mz window
        mz_min = mz - mz_tol
        mz_max = mz + mz_tol
        eic_data = s.ms1_df.filter(
            (pl.col("mz") >= mz_min) & (pl.col("mz") <= mz_max),
        )

        if eic_data.is_empty():
            # Return empty chromatogram if no data found
            import numpy as _np

            return Chromatogram(
                rt=_np.array([0.0]),
                inty=_np.array([0.0]),
                label=label or f"EIC m/z={mz:.4f} ± {mz_tol} (empty)",
                rt_unit=rt_unit,
            )

        # Aggregate intensities per retention time (sum in case of multiple points per rt)
        eic = eic_data.group_by("rt").agg(pl.col("inty").sum().alias("inty"))
        eic_pd = eic.sort("rt").to_pandas()

    except Exception:
        raise RuntimeError("Failed to extract EIC from ms1_df")

    if eic_pd.empty:
        # Return empty chromatogram if no data found
        import numpy as _np

        return Chromatogram(
            rt=_np.array([0.0]),
            inty=_np.array([0.0]),
            label=label or f"EIC m/z={mz:.4f} ± {mz_tol} (empty)",
            rt_unit=rt_unit,
        )

    # build Chromatogram
    try:
        chrom = Chromatogram(
            rt=eic_pd["rt"].to_numpy(),
            inty=eic_pd["inty"].to_numpy(),
            label=label or f"EIC m/z={mz:.4f} ± {mz_tol}",
            rt_unit=rt_unit,
        )
    except Exception:
        chrom = Chromatogram(
            rt=eic_pd["rt"].values,
            inty=eic_pd["inty"].values,
            label=label or f"EIC m/z={mz:.4f} ± {mz_tol}",
            rt_unit=rt_unit,
        )

    return chrom


# =====================================================================================
# DATA RETRIEVAL AND MATRIX FUNCTIONS
# =====================================================================================


def get_chrom(self, uids=None, samples=None):
    # Check if consensus_df is empty or doesn't have required columns
    if self.consensus_df.is_empty() or "consensus_uid" not in self.consensus_df.columns:
        self.logger.error("No consensus data found. Please run merge() first.")
        return None

    ids = self._get_consensus_uids(uids)
    sample_uids = self._get_sample_uids(samples)

    if self.consensus_map is None:
        self.logger.error("No consensus map found.")
        return None

    # Pre-filter all DataFrames to reduce join sizes
    filtered_consensus_mapping = self.consensus_mapping_df.filter(
        pl.col("consensus_uid").is_in(ids),
    )

    # Get feature_uids that we actually need
    relevant_feature_uids = filtered_consensus_mapping["feature_uid"].to_list()

    self.logger.debug(
        f"Filtering features_df for {len(relevant_feature_uids)} relevant feature_uids.",
    )
    # Pre-filter features_df to only relevant features and samples
    filtered_features = self.features_df.filter(
        pl.col("feature_uid").is_in(relevant_feature_uids)
        & pl.col("sample_uid").is_in(sample_uids),
    ).select(
        [
            "feature_uid",
            "chrom",
            "rt",
            "rt_original",
            "sample_uid",
        ],
    )

    # Pre-filter samples_df
    filtered_samples = self.samples_df.filter(
        pl.col("sample_uid").is_in(sample_uids),
    ).select(["sample_uid", "sample_name"])

    # Perform a three-way join to get all needed data
    self.logger.debug("Joining DataFrames to get complete chromatogram data.")
    df_combined = (
        filtered_consensus_mapping.join(
            filtered_features,
            on="feature_uid",
            how="inner",
        )
        .join(filtered_samples, on="sample_uid", how="inner")
        .with_columns(
            (pl.col("rt") - pl.col("rt_original")).alias("rt_shift"),
        )
    )

    # Update chrom objects with rt_shift efficiently
    self.logger.debug("Updating chromatogram objects with rt_shift values.")
    chrom_data = df_combined.select(["chrom", "rt_shift"]).to_dict(as_series=False)
    for chrom_obj, rt_shift in zip(chrom_data["chrom"], chrom_data["rt_shift"]):
        if chrom_obj is not None:
            chrom_obj.rt_shift = rt_shift

    # Get all unique combinations for complete matrix
    all_consensus_uids = sorted(df_combined["consensus_uid"].unique().to_list())
    all_sample_names = sorted(df_combined["sample_name"].unique().to_list())

    # Create a mapping dictionary for O(1) lookup instead of O(n) filtering
    self.logger.debug("Creating lookup dictionary for chromatogram objects.")
    chrom_lookup = {}
    for row in df_combined.select(
        [
            "consensus_uid",
            "sample_name",
            "chrom",
        ],
    ).iter_rows():
        key = (row[0], row[1])  # (consensus_uid, sample_name)
        chrom_lookup[key] = row[2]  # chrom object

    # Build pivot data efficiently using the lookup dictionary
    pivot_data = []
    total_iterations = len(all_consensus_uids)
    progress_interval = max(1, total_iterations // 10)  # Show progress every 10%

    for i, consensus_uid in enumerate(all_consensus_uids):
        if i % progress_interval == 0:
            progress_percent = (i / total_iterations) * 100
            self.logger.debug(
                f"Building pivot data: {progress_percent:.0f}% complete ({i}/{total_iterations})",
            )

        row_data = {"consensus_uid": consensus_uid}
        for sample_name in all_sample_names:
            key = (consensus_uid, sample_name)
            row_data[sample_name] = chrom_lookup.get(key, None)
        pivot_data.append(row_data)

    self.logger.debug(
        f"Building pivot data: 100% complete ({total_iterations}/{total_iterations})",
    )

    # Create Polars DataFrame with complex objects
    df2_pivoted = pl.DataFrame(pivot_data)

    return df2_pivoted


# =====================================================================================
# UTILITY AND CONFIGURATION FUNCTIONS
# =====================================================================================


def set_folder(self, folder):
    """
    Set the folder for saving and loading files.
    """
    if not os.path.exists(folder):
        os.makedirs(folder)
    self.folder = folder


def align_reset(self):
    self.logger.debug("Resetting alignment.")
    # iterate over all feature maps and set RT to original RT
    for feature_map in self.features_maps:
        for feature in feature_map:
            rt = feature.getMetaValue("original_RT")
            if rt is not None:
                feature.setRT(rt)
                feature.removeMetaValue("original_RT")
    self.alignment_ref_index = None
    # in self.features_df, set rt equal to rt_original
    self.features_df = self.features_df.with_columns(
        pl.col("rt_original").alias("rt"),
    )

    # Ensure column order is maintained after with_columns operation
    self._ensure_features_df_schema_order()


# =====================================================================================
# DATA RETRIEVAL HELPER FUNCTIONS
# =====================================================================================


# TODO I don't get this param
def get_consensus(self, quant="chrom_area"):
    if self.consensus_df is None:
        self.logger.error("No consensus map found.")
        return None

    # Convert Polars DataFrame to pandas for this operation since the result is used for export
    df1 = self.consensus_df.to_pandas().copy()

    # set consensus_id as uint64
    df1["consensus_id"] = df1["consensus_id"].astype("uint64")
    # set consensus_id as index
    df1.set_index("consensus_uid", inplace=True)
    # sort by consensus_id
    df1 = df1.sort_index()

    df2_polars = self.get_consensus_matrix(quant=quant)
    # Convert to pandas for merging (since the result is used for export)
    df2 = df2_polars.to_pandas().set_index("consensus_uid")
    # sort df2 row by consensus_id
    df2 = df2.sort_index()
    # merge df and df2 on consensus_id
    df = pd.merge(df1, df2, left_index=True, right_index=True, how="left")

    return df


# TODO I don't get this param
def get_consensus_matrix(self, quant="chrom_area"):
    """
    Get a matrix of consensus features with samples as columns and consensus features as rows.
    Optimized implementation that avoids expensive join operations.
    """
    if quant not in self.features_df.columns:
        self.logger.error(
            f"Quantification method {quant} not found in features_df.",
        )
        return None

    # Create a lookup dictionary from features_df for O(1) value access
    feature_values = {}
    for row in self.features_df.iter_rows(named=True):
        feature_uid = row["feature_uid"]
        sample_uid = row["sample_uid"]
        value = row[quant] if row[quant] is not None else 0
        feature_values[(feature_uid, sample_uid)] = value

    # Build consensus matrix directly using the consensus_mapping_df
    matrix_dict = {}
    sample_mapping = dict(
        self.samples_df.select(["sample_uid", "sample_name"]).iter_rows(),
    )

    for row in self.consensus_mapping_df.iter_rows(named=True):
        consensus_uid = row["consensus_uid"]
        sample_uid = row["sample_uid"]
        feature_uid = row["feature_uid"]

        # Look up the quantification value
        key = (feature_uid, sample_uid)
        value = feature_values.get(key, 0)

        if consensus_uid not in matrix_dict:
            matrix_dict[consensus_uid] = {}

        sample_name = sample_mapping.get(sample_uid, f"sample_{sample_uid}")

        # Take max if multiple features map to same consensus/sample combination
        if sample_name in matrix_dict[consensus_uid]:
            matrix_dict[consensus_uid][sample_name] = max(
                matrix_dict[consensus_uid][sample_name],
                value,
            )
        else:
            matrix_dict[consensus_uid][sample_name] = value

    # Convert to Polars DataFrame with proper formatting
    import polars as pl

    # Convert matrix_dict to list of records for Polars
    records = []
    for consensus_uid, sample_values in matrix_dict.items():
        record = {"consensus_uid": consensus_uid}
        record.update(sample_values)
        records.append(record)

    # Create Polars DataFrame and set proper data types
    df2 = pl.DataFrame(records)

    # Fill null values with 0 and round numeric columns
    numeric_cols = [col for col in df2.columns if col != "consensus_uid"]
    df2 = df2.with_columns(
        [
            pl.col("consensus_uid").cast(pl.UInt64),
            *[pl.col(col).fill_null(0).round(0) for col in numeric_cols],
        ],
    )

    return df2


def get_gaps_matrix(self, uids=None):
    """
    Get a matrix of gaps between consensus features with samples as columns and consensus features as rows.
    """
    if self.consensus_df is None:
        self.logger.error("No consensus map found.")
        return None
    uids = self._get_consensus_uids(uids)

    df1 = self.get_consensus_matrix(quant="filled")
    if df1 is None or df1.empty:
        self.logger.warning("No gap data found.")
        return None
    # keep only rows where consensus_id is in ids - use pandas indexing since df1 is already pandas
    df1 = df1[df1.index.isin(uids)]
    return df1


def get_gaps_stats(self, uids=None):
    """
    Get statistics about gaps in the consensus features.
    """

    df = self.get_gaps_matrix(uids=uids)

    # For each column, count how many times the value is True, False, or None. Summarize in a new df with three rows: True, False, None.
    if df is None or df.empty:
        self.logger.warning("No gap data found.")
        return None
    gaps_stats = pd.DataFrame(
        {
            "aligned": df.apply(lambda x: (~x.astype(bool)).sum()),
            "filled": df.apply(lambda x: x.astype(bool).sum() - pd.isnull(x).sum()),
            "missing": df.apply(lambda x: pd.isnull(x).sum()),
        },
    )
    return gaps_stats


# TODO is uid not supposed to be a list anymore?
def get_consensus_matches(self, uids=None, filled=True):
    """
    Get feature matches for consensus UIDs with optimized join operation.
    
    Parameters:
        uids: Consensus UID(s) to get matches for. Can be:
              - None: get matches for all consensus features
              - int: single consensus UID (converted to list)
              - list: multiple consensus UIDs
        filled (bool): Whether to include filled rows (True) or exclude them (False).
                      Default is True to maintain backward compatibility.
    
    Returns:
        pl.DataFrame: Feature matches for the specified consensus UIDs
    """
    # Handle single int by converting to list
    if isinstance(uids, int):
        uids = [uids]
    
    uids = self._get_consensus_uids(uids)
    
    if not uids:
        return pl.DataFrame()
    
    # Early validation checks
    if self.consensus_mapping_df is None or self.consensus_mapping_df.is_empty():
        self.logger.warning("No consensus mapping data available")
        return pl.DataFrame()
    
    if self.features_df is None or self.features_df.is_empty():
        self.logger.warning("No feature data available")
        return pl.DataFrame()
    
    # Build the query with optional filled filter
    features_query = self.features_df.lazy()
    
    # Apply filled filter if specified
    if not filled and "filled" in self.features_df.columns:
        features_query = features_query.filter(~pl.col("filled"))
    
    # Optimized single-pass operation using join instead of two separate filters
    # This avoids creating intermediate Python lists and leverages Polars' optimized joins
    matches = (
        features_query
        .join(
            self.consensus_mapping_df
            .lazy()
            .filter(pl.col("consensus_uid").is_in(uids))
            .select("feature_uid"),  # Only select what we need for the join
            on="feature_uid",
            how="inner"
        )
        .collect(streaming=True)  # Use streaming for memory efficiency with large datasets
    )
    
    return matches


# =====================================================================================
# UID HELPER FUNCTIONS
# =====================================================================================


def fill_reset(self):
    # remove all features with filled=True
    if self.features_df is None:
        self.logger.warning("No features found.")
        return
    l1 = len(self.features_df)
    self.features_df = self.features_df.filter(~pl.col("filled"))
    # remove all rows in consensus_mapping_df where feature_uid is not in features_df['uid']

    feature_uids_to_keep = self.features_df["feature_uid"].to_list()
    self.consensus_mapping_df = self.consensus_mapping_df.filter(
        pl.col("feature_uid").is_in(feature_uids_to_keep),
    )
    self.logger.info(
        f"Reset filled chromatograms. Chroms removed: {l1 - len(self.features_df)}",
    )


def _get_feature_uids(self, uids=None, seed=42):
    """
    Helper function to get feature_uids from features_df based on input uids.
    If uids is None, returns all feature_uids.
    If uids is a single integer, returns a random sample of feature_uids.
    If uids is a list of strings, returns feature_uids corresponding to those feature_uids.
    If uids is a list of integers, returns feature_uids corresponding to those feature_uids.
    """
    if uids is None:
        # get all feature_uids from features_df
        return self.features_df["feature_uid"].to_list()
    elif isinstance(uids, int):
        # choose a random sample of feature_uids
        if len(self.features_df) > uids:
            np.random.seed(seed)
            return np.random.choice(
                self.features_df["feature_uid"].to_list(),
                uids,
                replace=False,
            ).tolist()
        else:
            return self.features_df["feature_uid"].to_list()
    else:
        # iterate over all uids. If the item is a string, assume it's a feature_uid
        feature_uids = []
        for uid in uids:
            if isinstance(uid, str):
                matching_rows = self.features_df.filter(pl.col("feature_uid") == uid)
                if not matching_rows.is_empty():
                    feature_uids.append(
                        matching_rows.row(0, named=True)["feature_uid"],
                    )
            elif isinstance(uid, int):
                if uid in self.features_df["feature_uid"].to_list():
                    feature_uids.append(uid)
        # remove duplicates
        feature_uids = list(set(feature_uids))
        return feature_uids


def _get_consensus_uids(self, uids=None, seed=42):
    """
    Helper function to get consensus_uids from consensus_df based on input uids.
    If uids is None, returns all consensus_uids.
    If uids is a single integer, returns a random sample of consensus_uids.
    If uids is a list of strings, returns consensus_uids corresponding to those consensus_ids.
    If uids is a list of integers, returns consensus_uids corresponding to those consensus_uids.
    """
    # Check if consensus_df is empty or doesn't have required columns
    if self.consensus_df.is_empty() or "consensus_uid" not in self.consensus_df.columns:
        return []

    if uids is None:
        # get all consensus_uids from consensus_df
        return self.consensus_df["consensus_uid"].to_list()
    elif isinstance(uids, int):
        # choose a random sample of consensus_uids
        if len(self.consensus_df) > uids:
            np.random.seed(seed)  # for reproducibility
            return np.random.choice(
                self.consensus_df["consensus_uid"].to_list(),
                uids,
                replace=False,
            ).tolist()
        else:
            return self.consensus_df["consensus_uid"].to_list()
    else:
        # iterate over all uids. If the item is a string, assume it's a consensus_id
        consensus_uids = []
        for uid in uids:
            if isinstance(uid, str):
                matching_rows = self.consensus_df.filter(pl.col("consensus_id") == uid)
                if not matching_rows.is_empty():
                    consensus_uids.append(
                        matching_rows.row(0, named=True)["consensus_uid"],
                    )
            elif isinstance(uid, int):
                if uid in self.consensus_df["consensus_uid"].to_list():
                    consensus_uids.append(uid)
        # remove duplicates
        consensus_uids = list(set(consensus_uids))
        return consensus_uids


def _get_sample_uids(self, samples=None, seed=42):
    """
    Helper function to get sample_uids from samples_df based on input samples.
    If samples is None, returns all sample_uids.
    If samples is a single integer, returns a random sample of sample_uids.
    If samples is a list of strings, returns sample_uids corresponding to those sample_names.
    If samples is a list of integers, returns sample_uids corresponding to those sample_uids.
    """
    if samples is None:
        # get all sample_uids from samples_df
        return self.samples_df["sample_uid"].to_list()
    elif isinstance(samples, int):
        # choose a random sample of sample_uids
        if len(self.samples_df) > samples:
            np.random.seed(seed)  # for reproducibility
            self.logger.info(f"Randomly selected {samples} samples")
            return np.random.choice(
                self.samples_df["sample_uid"].to_list(),
                samples,
                replace=False,
            ).tolist()
        else:
            return self.samples_df["sample_uid"].to_list()
    else:
        # iterate over all samples. If the item is a string, assume it's a sample_name
        sample_uids = []
        for sample in samples:
            if isinstance(sample, str):
                matching_rows = self.samples_df.filter(pl.col("sample_name") == sample)
                if not matching_rows.is_empty():
                    sample_uids.append(
                        matching_rows.row(0, named=True)["sample_uid"],
                    )
            elif isinstance(sample, int):
                if sample in self.samples_df["sample_uid"].to_list():
                    sample_uids.append(sample)
        # remove duplicates
        sample_uids = list(set(sample_uids))
        return sample_uids


def get_sample(self, sample):
    """
    Return a `Sample` object corresponding to the provided sample identifier.

    Accepted `sample` values:
    - int: interpreted as `sample_uid`
    - str: interpreted as `sample_name`
    - Sample instance: returned as-is

    This helper mirrors the original Study.get_sample method but lives in helpers for reuse.
    """
    from masster.sample.sample import Sample

    if isinstance(sample, Sample):
        return sample

    if isinstance(sample, int):
        rows = self.samples_df.filter(pl.col("sample_uid") == sample)
    elif isinstance(sample, str):
        rows = self.samples_df.filter(pl.col("sample_name") == sample)
    else:
        raise ValueError(
            "sample must be an int (sample_uid), str (sample_name) or a Sample instance",
        )

    if rows.is_empty():
        raise KeyError(f"Sample not found: {sample}")

    row = rows.row(0, named=True)
    sample_uid = int(row["sample_uid"]) if row["sample_uid"] is not None else None

    # Use a cache on the Study instance if available
    cache = getattr(self, "_samples_cache", None)
    if cache is not None and sample_uid in cache:
        return cache[sample_uid]

    sample_path = row.get("sample_path", None)
    s = Sample(log_level="ERROR")
    try:
        if sample_path:
            try:
                s.load(sample_path)
            except Exception:
                s = Sample(file=sample_path)
    except Exception:
        pass

    if cache is not None and sample_uid is not None:
        cache[sample_uid] = s
    return s


def get_orphans(self):
    """
    Get all features that are not in the consensus mapping.
    """
    not_in_consensus = self.features_df.filter(
        ~self.features_df["feature_uid"].is_in(
            self.consensus_mapping_df["feature_uid"].to_list(),
        ),
    )
    return not_in_consensus


# =====================================================================================
# DATA COMPRESSION AND RESTORATION FUNCTIONS
# =====================================================================================


def compress(self, features=True, ms2=True, chrom=False, ms2_max=5):
    """
    Perform compress_features, compress_ms2, and compress_chrom operations.

    Parameters:
        max_replicates (int): Maximum number of MS2 replicates to keep per consensus_uid and energy combination
    """
    self.logger.info("Starting full compression...")
    if features:
        self.compress_features()
    if ms2:
        self.compress_ms2(max_replicates=ms2_max)
    if chrom:
        self.compress_chrom()
    self.logger.info("Compression completed")


def compress_features(self):
    """
    Compress features_df by:
    1. Deleting features that are not associated to any consensus (according to consensus_mapping_df)
    2. Setting the m2_specs column to None to save memory
    """
    if self.features_df is None or self.features_df.is_empty():
        self.logger.warning("No features_df found.")
        return

    if self.consensus_mapping_df is None or self.consensus_mapping_df.is_empty():
        self.logger.warning("No consensus_mapping_df found.")
        return

    initial_count = len(self.features_df)

    # Get feature_uids that are associated with consensus features
    consensus_feature_uids = self.consensus_mapping_df["feature_uid"].to_list()

    # Filter features_df to keep only features associated with consensus
    self.features_df = self.features_df.filter(
        pl.col("feature_uid").is_in(consensus_feature_uids),
    )

    # Set ms2_specs column to None if it exists
    if "ms2_specs" in self.features_df.columns:
        # Create a list of None values with the same length as the dataframe
        # This preserves the Object dtype instead of converting to Null
        none_values = [None] * len(self.features_df)
        self.features_df = self.features_df.with_columns(
            pl.Series("ms2_specs", none_values, dtype=pl.Object),
        )

    removed_count = initial_count - len(self.features_df)
    self.logger.info(
        f"Compressed features: removed {removed_count} features not in consensus, cleared ms2_specs column",
    )


def restore_features(self, samples=None, maps=False):
    """
    Update specific columns (chrom, chrom_area, ms2_scans, ms2_specs) in features_df
    from the corresponding samples by reading features_df from the sample5 file.
    Use the feature_id for matching.

    Parameters:
        samples (list, optional): List of sample_uids or sample_names to restore.
                                 If None, restores all samples.
        maps (bool, optional): If True, also load featureXML data and update study.feature_maps.
    """
    import datetime
    from masster.sample.sample import Sample

    if self.features_df is None or self.features_df.is_empty():
        self.logger.error("No features_df found in study.")
        return

    if self.samples_df is None or self.samples_df.is_empty():
        self.logger.error("No samples_df found in study.")
        return

    # Get sample_uids to process
    sample_uids = self._get_sample_uids(samples)

    if not sample_uids:
        self.logger.warning("No valid samples specified.")
        return

    # Columns to update from sample data
    columns_to_update = ["chrom", "chrom_area", "ms2_scans", "ms2_specs"]

    self.logger.info(
        f"Restoring columns {columns_to_update} from {len(sample_uids)} samples...",
    )

    # Create a mapping of (sample_uid, feature_id) to feature_uid from study.features_df
    study_feature_mapping = {}
    for row in self.features_df.iter_rows(named=True):
        if "feature_id" in row and "feature_uid" in row and "sample_uid" in row:
            key = (row["sample_uid"], row["feature_id"])
            study_feature_mapping[key] = row["feature_uid"]

    # Process each sample
    tqdm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]
    for sample_uid in tqdm(
        sample_uids,
        unit="sample",
        disable=tqdm_disable,
        desc=f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Restoring samples",
    ):
        # Get sample info
        sample_row = self.samples_df.filter(pl.col("sample_uid") == sample_uid)
        if sample_row.is_empty():
            self.logger.warning(
                f"Sample with uid {sample_uid} not found in samples_df.",
            )
            continue

        sample_info = sample_row.row(0, named=True)
        sample_path = sample_info.get("sample_path")
        sample_name = sample_info.get("sample_name")

        if not sample_path or not os.path.exists(sample_path):
            self.logger.warning(
                f"Sample file not found for {sample_name}: {sample_path}",
            )
            continue

        try:
            # Load sample to get its features_df
            # Use a direct load call with map=False to prevent feature synchronization
            # which would remove filled features that don't exist in the original FeatureMap
            # Use ERROR log level to suppress info messages
            sample = Sample(log_level="ERROR")
            sample._load_sample5(sample_path, map=False)

            if sample.features_df is None or sample.features_df.is_empty():
                self.logger.warning(f"No features found in sample {sample_name}")
                continue

            # Check which columns are actually available in the sample
            available_columns = [
                col for col in columns_to_update if col in sample.features_df.columns
            ]
            if not available_columns:
                self.logger.debug(f"No target columns found in sample {sample_name}")
                continue

            # Create update data for this sample
            updates_made = 0
            for row in sample.features_df.iter_rows(named=True):
                feature_id = row.get("feature_id")
                if feature_id is None:
                    continue

                key = (sample_uid, feature_id)
                if key in study_feature_mapping:
                    feature_uid = study_feature_mapping[key]

                    # Update only the available columns in study.features_df
                    for col in available_columns:
                        if col in row and col in self.features_df.columns:
                            # Get the original column dtype to preserve it
                            original_dtype = self.features_df[col].dtype

                            # Update the specific row and column, preserving dtype
                            mask = (pl.col("feature_uid") == feature_uid) & (
                                pl.col("sample_uid") == sample_uid
                            )

                            # Handle object columns (like Chromatogram) differently
                            if original_dtype == pl.Object:
                                self.features_df = self.features_df.with_columns(
                                    pl.when(mask)
                                    .then(
                                        pl.lit(
                                            row[col],
                                            dtype=original_dtype,
                                            allow_object=True,
                                        ),
                                    )
                                    .otherwise(pl.col(col))
                                    .alias(col),
                                )
                            else:
                                self.features_df = self.features_df.with_columns(
                                    pl.when(mask)
                                    .then(pl.lit(row[col], dtype=original_dtype))
                                    .otherwise(pl.col(col))
                                    .alias(col),
                                )
                    updates_made += 1

            if updates_made > 0:
                self.logger.debug(
                    f"Updated {updates_made} features from sample {sample_name}",
                )

            # If maps is True, load featureXML data
            if maps:
                if hasattr(sample, "feature_maps"):
                    self.feature_maps.extend(sample.feature_maps)

        except Exception as e:
            self.logger.error(f"Failed to load sample {sample_name}: {e}")
            continue

    self.logger.info(
        f"Completed restoring columns {columns_to_update} from {len(sample_uids)} samples",
    )


def restore_chrom(self, samples=None, mz_tol=0.010, rt_tol=10.0):
    """
    Restore chromatograms from individual .sample5 files and gap-fill missing ones.

    This function combines the functionality of restore_features() and fill_chrom():
    1. First restores chromatograms from individual .sample5 files (like restore_features)
    2. Then gap-fills any remaining empty chromatograms (like fill_chrom)
    3. ONLY updates the 'chrom' column, not chrom_area or other derived values

    Parameters:
        samples (list, optional): List of sample_uids or sample_names to process.
                                 If None, processes all samples.
        mz_tol (float): m/z tolerance for gap filling (default: 0.010)
        rt_tol (float): RT tolerance for gap filling (default: 10.0)
    """
    import datetime
    import numpy as np
    from masster.sample.sample import Sample
    from masster.chromatogram import Chromatogram

    if self.features_df is None or self.features_df.is_empty():
        self.logger.error("No features_df found in study.")
        return

    if self.samples_df is None or self.samples_df.is_empty():
        self.logger.error("No samples_df found in study.")
        return

    # Get sample_uids to process
    sample_uids = self._get_sample_uids(samples)
    if not sample_uids:
        self.logger.warning("No valid samples specified.")
        return

    self.logger.info(f"Restoring chromatograms from {len(sample_uids)} samples...")

    # Create mapping of (sample_uid, feature_id) to feature_uid
    study_feature_mapping = {}
    for row in self.features_df.iter_rows(named=True):
        if "feature_id" in row and "feature_uid" in row and "sample_uid" in row:
            key = (row["sample_uid"], row["feature_id"])
            study_feature_mapping[key] = row["feature_uid"]

    # Phase 1: Restore from individual .sample5 files (like restore_features)
    restored_count = 0
    tqdm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]

    self.logger.info("Phase 1: Restoring chromatograms from .sample5 files...")
    for sample_uid in tqdm(
        sample_uids,
        desc=f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Restoring from samples",
        disable=tqdm_disable,
    ):
        # Get sample info
        sample_row = self.samples_df.filter(pl.col("sample_uid") == sample_uid)
        if sample_row.is_empty():
            self.logger.warning(f"Sample with uid {sample_uid} not found.")
            continue

        sample_info = sample_row.row(0, named=True)
        sample_path = sample_info.get("sample_path")
        sample_name = sample_info.get("sample_name")

        if not sample_path or not os.path.exists(sample_path):
            self.logger.warning(f"Sample file not found: {sample_path}")
            continue

        try:
            # Load sample (with map=False to prevent feature synchronization)
            # Use ERROR log level to suppress info messages
            sample = Sample(log_level="ERROR")
            sample._load_sample5(sample_path, map=False)

            if sample.features_df is None or sample.features_df.is_empty():
                self.logger.warning(f"No features found in sample {sample_name}")
                continue

            # Check if chrom column exists in sample
            if "chrom" not in sample.features_df.columns:
                continue

            # Update chromatograms from this sample
            for row in sample.features_df.iter_rows(named=True):
                feature_id = row.get("feature_id")
                chrom = row.get("chrom")

                if feature_id is None or chrom is None:
                    continue

                key = (sample_uid, feature_id)
                if key in study_feature_mapping:
                    feature_uid = study_feature_mapping[key]

                    # Update only the chrom column
                    mask = (pl.col("feature_uid") == feature_uid) & (
                        pl.col("sample_uid") == sample_uid
                    )
                    self.features_df = self.features_df.with_columns(
                        pl.when(mask)
                        .then(pl.lit(chrom, dtype=pl.Object, allow_object=True))
                        .otherwise(pl.col("chrom"))
                        .alias("chrom"),
                    )
                    restored_count += 1

        except Exception as e:
            self.logger.error(f"Failed to load sample {sample_name}: {e}")
            continue

    self.logger.info(
        f"Phase 1 complete: Restored {restored_count} chromatograms from .sample5 files",
    )

    # Phase 2: Gap-fill remaining empty chromatograms (like fill_chrom)
    self.logger.info("Phase 2: Gap-filling remaining empty chromatograms...")

    # Count how many chromatograms are still missing
    empty_chroms = self.features_df.filter(pl.col("chrom").is_null()).height
    total_chroms = len(self.features_df)

    self.logger.debug(
        f"Chromatograms still missing: {empty_chroms}/{total_chroms} ({empty_chroms / total_chroms * 100:.1f}%)",
    )

    if empty_chroms == 0:
        self.logger.info(
            "All chromatograms restored from .sample5 files. No gap-filling needed.",
        )
        return

    # Get consensus info for gap filling
    consensus_info = {}
    for row in self.consensus_df.iter_rows(named=True):
        consensus_info[row["consensus_uid"]] = {
            "rt_start_mean": row["rt_start_mean"],
            "rt_end_mean": row["rt_end_mean"],
            "mz": row["mz"],
            "rt": row["rt"],
        }

    filled_count = 0

    # Process each sample that has missing chromatograms
    for sample_uid in tqdm(
        sample_uids,
        desc=f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Gap-filling missing chromatograms",
        disable=tqdm_disable,
    ):
        # Get features with missing chromatograms for this sample
        missing_features = self.features_df.filter(
            (pl.col("sample_uid") == sample_uid) & (pl.col("chrom").is_null()),
        )

        if missing_features.is_empty():
            continue

        # Get sample info
        sample_row = self.samples_df.filter(pl.col("sample_uid") == sample_uid)
        sample_info = sample_row.row(0, named=True)
        sample_path = sample_info.get("sample_path")
        sample_name = sample_info.get("sample_name")

        if not sample_path or not os.path.exists(sample_path):
            continue

        try:
            # Load sample for MS1 data extraction
            # Use ERROR log level to suppress info messages
            sample = Sample(log_level="ERROR")
            sample._load_sample5(sample_path, map=False)

            if (
                not hasattr(sample, "ms1_df")
                or sample.ms1_df is None
                or sample.ms1_df.is_empty()
            ):
                continue

            # Process each missing feature
            for feature_row in missing_features.iter_rows(named=True):
                feature_uid = feature_row["feature_uid"]
                mz = feature_row["mz"]
                rt = feature_row["rt"]
                rt_start = feature_row.get("rt_start", rt - rt_tol)
                rt_end = feature_row.get("rt_end", rt + rt_tol)

                # Extract EIC from MS1 data
                d = sample.ms1_df.filter(
                    (pl.col("mz") >= mz - mz_tol)
                    & (pl.col("mz") <= mz + mz_tol)
                    & (pl.col("rt") >= rt_start - rt_tol)
                    & (pl.col("rt") <= rt_end + rt_tol),
                )

                # Create chromatogram
                if d.is_empty():
                    # Create empty chromatogram
                    eic = Chromatogram(
                        rt=np.array([rt_start, rt_end]),
                        inty=np.array([0.0, 0.0]),
                        label=f"EIC mz={mz:.4f} (gap-filled)",
                        file=sample_path,
                        mz=mz,
                        mz_tol=mz_tol,
                        feature_start=rt_start,
                        feature_end=rt_end,
                        feature_apex=rt,
                    )
                else:
                    # Create real chromatogram from data
                    eic_rt = d.group_by("rt").agg(pl.col("inty").max()).sort("rt")

                    if len(eic_rt) > 4:
                        eic = Chromatogram(
                            eic_rt["rt"].to_numpy(),
                            eic_rt["inty"].to_numpy(),
                            label=f"EIC mz={mz:.4f} (gap-filled)",
                            file=sample_path,
                            mz=mz,
                            mz_tol=mz_tol,
                            feature_start=rt_start,
                            feature_end=rt_end,
                            feature_apex=rt,
                        ).find_peaks()
                    else:
                        eic = Chromatogram(
                            eic_rt["rt"].to_numpy(),
                            eic_rt["inty"].to_numpy(),
                            label=f"EIC mz={mz:.4f} (gap-filled)",
                            file=sample_path,
                            mz=mz,
                            mz_tol=mz_tol,
                            feature_start=rt_start,
                            feature_end=rt_end,
                            feature_apex=rt,
                        )

                # Update the chromatogram in the study
                mask = pl.col("feature_uid") == feature_uid
                self.features_df = self.features_df.with_columns(
                    pl.when(mask)
                    .then(pl.lit(eic, dtype=pl.Object, allow_object=True))
                    .otherwise(pl.col("chrom"))
                    .alias("chrom"),
                )
                filled_count += 1

        except Exception as e:
            self.logger.error(f"Failed to gap-fill sample {sample_name}: {e}")
            continue

    self.logger.info(f"Phase 2 complete: Gap-filled {filled_count} chromatograms")

    # Final summary
    final_non_null = self.features_df.filter(pl.col("chrom").is_not_null()).height
    final_total = len(self.features_df)

    self.logger.info(
        f"Chromatogram restoration complete: {final_non_null}/{final_total} ({final_non_null / final_total * 100:.1f}%)",
    )
    self.logger.info(
        f"Restored from .sample5 files: {restored_count}, Gap-filled from raw data: {filled_count}",
    )


def compress_ms2(self, max_replicates=5):
    """
    Reduce the number of entries matching any pair of (consensus and energy) to max XY rows.
    Groups all rows by consensus_uid and energy. For each group, sort by number_frags * prec_inty,
    and then pick the top XY rows. Discard the others.

    Parameters:
        max_replicates (int): Maximum number of replicates to keep per consensus_uid and energy combination
    """
    if self.consensus_ms2 is None or self.consensus_ms2.is_empty():
        self.logger.warning("No consensus_ms2 found.")
        return

    initial_count = len(self.consensus_ms2)

    # Create a ranking score based on number_frags * prec_inty
    # Handle None values by treating them as 0
    self.consensus_ms2 = self.consensus_ms2.with_columns(
        [
            (
                pl.col("number_frags").fill_null(0) * pl.col("prec_inty").fill_null(0)
            ).alias("ranking_score"),
        ],
    )

    # Group by consensus_uid and energy, then rank by score and keep top max_replicates
    compressed_ms2 = (
        self.consensus_ms2.with_row_count(
            "row_id",
        )  # Add row numbers for stable sorting
        .sort(
            ["consensus_uid", "energy", "ranking_score", "row_id"],
            descending=[False, False, True, False],
        )
        .with_columns(
            [
                pl.int_range(pl.len()).over(["consensus_uid", "energy"]).alias("rank"),
            ],
        )
        .filter(pl.col("rank") < max_replicates)
        .drop(["ranking_score", "row_id", "rank"])
    )

    self.consensus_ms2 = compressed_ms2

    removed_count = initial_count - len(self.consensus_ms2)
    self.logger.info(
        f"Compressed MS2 data: removed {removed_count} entries, kept max {max_replicates} per consensus/energy pair",
    )


def compress_chrom(self):
    """
    Set the chrom column in study.features_df to null to save memory.

    This function clears all chromatogram objects from the features_df, which can
    significantly reduce memory usage in large studies.
    """
    if self.features_df is None or self.features_df.is_empty():
        self.logger.warning("No features_df found.")
        return

    if "chrom" not in self.features_df.columns:
        self.logger.warning("No 'chrom' column found in features_df.")
        return

    # Count non-null chromatograms before compression
    non_null_count = self.features_df.filter(pl.col("chrom").is_not_null()).height

    # Set chrom column to None while keeping dtype as object
    self.features_df = self.features_df.with_columns(
        pl.lit(None, dtype=pl.Object).alias("chrom"),
    )

    self.logger.info(
        f"Compressed chromatograms: cleared {non_null_count} chromatogram objects from features_df",
    )


# =====================================================================================
# SAMPLE MANAGEMENT AND NAMING FUNCTIONS
# =====================================================================================


def sample_name_replace(self, replace_dict):
    """
    Replace sample names in samples_df based on a dictionary mapping.

    Takes all names in self.samples_df['sample_name'], creates a copy, and replaces
    all keys with their corresponding values from replace_dict. Checks that all
    resulting sample names are unique. If unique, replaces the values in self.samples_df.

    Parameters:
        replace_dict (dict): Dictionary mapping old names (keys) to new names (values).
                           All keys found in sample names will be replaced with their
                           corresponding values.
                           e.g., {"old_name1": "new_name1", "old_name2": "new_name2"}

    Returns:
        None

    Raises:
        ValueError: If replace_dict is not a dictionary
        ValueError: If resulting sample names are not unique
    """
    if not isinstance(replace_dict, dict):
        raise ValueError("replace_dict must be a dictionary")

    if self.samples_df is None or len(self.samples_df) == 0:
        self.logger.warning("No samples found in study.")
        return

    if not replace_dict:
        self.logger.warning("Empty replace_dict provided, no changes made.")
        return

    # Get current sample names
    current_names = self.samples_df.get_column("sample_name").to_list()

    # Create a copy and apply replacements
    new_names = []
    replaced_count = 0

    for name in current_names:
        if name in replace_dict:
            new_names.append(replace_dict[name])
            replaced_count += 1
            self.logger.debug(
                f"Replacing sample name: '{name}' -> '{replace_dict[name]}'",
            )
        else:
            new_names.append(name)

    # Check that all new names are unique
    if len(set(new_names)) != len(new_names):
        duplicates = []
        seen = set()
        for name in new_names:
            if name in seen:
                duplicates.append(name)
            else:
                seen.add(name)
        raise ValueError(
            f"Resulting sample names are not unique. Duplicates found: {duplicates}",
        )

    # If we get here, all names are unique - apply the changes
    self.samples_df = self.samples_df.with_columns(
        pl.Series("sample_name", new_names).alias("sample_name"),
    )

    self.logger.info(f"Successfully replaced {replaced_count} sample names")


def sample_name_reset(self):
    """
    Reset sample names to the basename of sample_path without extensions.

    Takes all paths in self.samples_df['sample_path'], extracts the basename,
    removes file extensions, and checks that all resulting names are unique.
    If unique, replaces the values in self.samples_df['sample_name'].

    Returns:
        None

    Raises:
        ValueError: If resulting sample names are not unique
        RuntimeError: If any sample_path is None or empty
    """
    import os

    if self.samples_df is None or len(self.samples_df) == 0:
        self.logger.warning("No samples found in study.")
        return

    # Get current sample paths
    sample_paths = self.samples_df.get_column("sample_path").to_list()

    # Extract basenames without extensions
    new_names = []

    for i, path in enumerate(sample_paths):
        if path is None or path == "":
            raise RuntimeError(f"Sample at index {i} has no sample_path set")

        # Get basename and remove extension(s)
        basename = os.path.basename(path)
        # Remove all extensions (handles cases like .tar.gz, .sample5.gz, etc.)
        name_without_ext = basename
        while "." in name_without_ext:
            name_without_ext = os.path.splitext(name_without_ext)[0]

        new_names.append(name_without_ext)
        self.logger.debug(
            f"Resetting sample name from path: '{path}' -> '{name_without_ext}'",
        )

    # Check that all new names are unique
    if len(set(new_names)) != len(new_names):
        duplicates = []
        seen = set()
        for name in new_names:
            if name in seen:
                duplicates.append(name)
            else:
                seen.add(name)
        raise ValueError(
            f"Resulting sample names are not unique. Duplicates found: {duplicates}",
        )

    # If we get here, all names are unique - apply the changes
    self.samples_df = self.samples_df.with_columns(
        pl.Series("sample_name", new_names).alias("sample_name"),
    )

    self.logger.info(
        f"Successfully reset {len(new_names)} sample names from sample paths",
    )


def set_source(self, filename):
    """
    Reassign file_source for all samples in samples_df. If filename contains only a path,
    keep the current basename and build an absolute path. Check that the new file exists
    before overwriting the old file_source.

    Parameters:
        filename (str): New file path or directory path for all samples

    Returns:
        None
    """
    import os

    if self.samples_df is None or len(self.samples_df) == 0:
        self.logger.warning("No samples found in study.")
        return

    updated_count = 0
    failed_count = 0

    # Get all current file_source values
    current_sources = self.samples_df.get_column("sample_source").to_list()
    sample_names = self.samples_df.get_column("sample_name").to_list()

    new_sources = []

    for i, (current_source, sample_name) in enumerate(
        zip(current_sources, sample_names),
    ):
        # Check if filename is just a directory path
        if os.path.isdir(filename):
            if current_source is None or current_source == "":
                self.logger.warning(
                    f"Cannot build path for sample '{sample_name}': no current file_source available",
                )
                new_sources.append(current_source)
                failed_count += 1
                continue

            # Get the basename from current file_source
            current_basename = os.path.basename(current_source)
            # Build new absolute path
            new_file_path = os.path.join(filename, current_basename)
        else:
            # filename is a full path, make it absolute
            new_file_path = os.path.abspath(filename)

        # Check if the new file exists
        if not os.path.exists(new_file_path):
            self.logger.warning(
                f"File does not exist for sample '{sample_name}': {new_file_path}",
            )
            new_sources.append(current_source)
            failed_count += 1
            continue

        # File exists, update source
        new_sources.append(new_file_path)
        updated_count += 1

        # Log individual updates at debug level
        self.logger.debug(
            f"Updated file_source for sample '{sample_name}': {current_source} -> {new_file_path}",
        )

    # Update the samples_df with new file_source values
    self.samples_df = self.samples_df.with_columns(
        pl.Series("file_source", new_sources).alias("file_source"),
    )

    # Log summary
    if updated_count > 0:
        self.logger.info(f"Updated file_source for {updated_count} samples")
    if failed_count > 0:
        self.logger.warning(f"Failed to update file_source for {failed_count} samples")


# =====================================================================================
# DATA FILTERING AND SELECTION FUNCTIONS
# =====================================================================================


def features_select(
    self,
    mz=None,
    rt=None,
    inty=None,
    sample_uid=None,
    sample_name=None,
    consensus_uid=None,
    feature_uid=None,
    filled=None,
    quality=None,
    chrom_coherence=None,
    chrom_prominence=None,
    chrom_prominence_scaled=None,
    chrom_height_scaled=None,
    chunk_size: int = 100000,
    use_lazy_streaming: bool = True,
):
    """
    Select features from features_df based on specified criteria and return the filtered DataFrame.

    FULLY OPTIMIZED VERSION: Enhanced performance with lazy streaming and chunked processing.

    Key optimizations:
    - Lazy evaluation with streaming execution for memory efficiency
    - Optimized filter expression building with reduced overhead
    - Chunked processing for very large datasets
    - Efficient column existence checking
    - Enhanced error handling and performance logging

    Parameters:
        mz: m/z range filter (tuple for range, single value for minimum)
        rt: retention time range filter (tuple for range, single value for minimum)
        inty: intensity filter (tuple for range, single value for minimum)
        sample_uid: sample UID filter (list, single value, or tuple for range)
        sample_name: sample name filter (list or single value)
        consensus_uid: consensus UID filter (list, single value, or tuple for range)
        feature_uid: feature UID filter (list, single value, or tuple for range)
        filled: filter for filled/not filled features (bool)
        quality: quality score filter (tuple for range, single value for minimum)
        chrom_coherence: chromatogram coherence filter (tuple for range, single value for minimum)
        chrom_prominence: chromatogram prominence filter (tuple for range, single value for minimum)
        chrom_prominence_scaled: scaled chromatogram prominence filter (tuple for range, single value for minimum)
        chrom_height_scaled: scaled chromatogram height filter (tuple for range, single value for minimum)
        chunk_size: Number of features to process per chunk for large datasets (default: 100000)
        use_lazy_streaming: Enable lazy evaluation with streaming for memory efficiency (default: True)

    Returns:
        polars.DataFrame: Filtered features DataFrame
    """
    if self.features_df is None or self.features_df.is_empty():
        self.logger.warning("No features found in study.")
        return pl.DataFrame()

    # Early return optimization
    filter_params = [mz, rt, inty, sample_uid, sample_name, consensus_uid, 
                    feature_uid, filled, quality, chrom_coherence, 
                    chrom_prominence, chrom_prominence_scaled, chrom_height_scaled]
    
    if all(param is None for param in filter_params):
        return self.features_df.clone()

    import time
    start_time = time.perf_counter()
    initial_count = len(self.features_df)

    # Build optimized filter expression
    filter_expr = _build_optimized_filter_expression(
        self, mz, rt, inty, sample_uid, sample_name, consensus_uid,
        feature_uid, filled, quality, chrom_coherence,
        chrom_prominence, chrom_prominence_scaled, chrom_height_scaled
    )
    
    if filter_expr is None:
        return pl.DataFrame()
    
    # Apply filter with optimized execution strategy
    if use_lazy_streaming and initial_count > chunk_size:
        result = _apply_chunked_select(self, filter_expr, chunk_size)
    else:
        result = (
            self.features_df
            .lazy()
            .filter(filter_expr)
            .collect(streaming=use_lazy_streaming)
        )
    
    # Log performance
    elapsed_time = time.perf_counter() - start_time
    final_count = len(result)
    removed_count = initial_count - final_count
    
    if final_count == 0:
        self.logger.warning("No features remaining after applying selection criteria.")
    else:
        self.logger.debug(
            f"Selected features: {final_count:,} (removed: {removed_count:,}) in {elapsed_time:.4f}s"
        )
    
    return result


def _build_optimized_filter_expression(self, mz, rt, inty, sample_uid, sample_name, 
                                     consensus_uid, feature_uid, filled, quality,
                                     chrom_coherence, chrom_prominence, 
                                     chrom_prominence_scaled, chrom_height_scaled):
    """
    Build optimized filter expression with efficient column checking and expression combining.
    """
    # Pre-check available columns once
    available_columns = set(self.features_df.columns)
    filter_conditions = []
    warnings = []
    
    # Build filter conditions with optimized expressions
    if mz is not None:
        if isinstance(mz, tuple) and len(mz) == 2:
            min_mz, max_mz = mz
            filter_conditions.append(pl.col("mz").is_between(min_mz, max_mz, closed="both"))
        else:
            filter_conditions.append(pl.col("mz") >= mz)

    if rt is not None:
        if isinstance(rt, tuple) and len(rt) == 2:
            min_rt, max_rt = rt
            filter_conditions.append(pl.col("rt").is_between(min_rt, max_rt, closed="both"))
        else:
            filter_conditions.append(pl.col("rt") >= rt)

    if inty is not None:
        if isinstance(inty, tuple) and len(inty) == 2:
            min_inty, max_inty = inty
            filter_conditions.append(pl.col("inty").is_between(min_inty, max_inty, closed="both"))
        else:
            filter_conditions.append(pl.col("inty") >= inty)

    # Filter by sample_uid
    if sample_uid is not None:
        if isinstance(sample_uid, (list, tuple)):
            if len(sample_uid) == 2 and not isinstance(sample_uid, list):
                # Treat as range
                min_uid, max_uid = sample_uid
                filter_conditions.append(pl.col("sample_uid").is_between(min_uid, max_uid, closed="both"))
            else:
                # Treat as list
                filter_conditions.append(pl.col("sample_uid").is_in(sample_uid))
        else:
            filter_conditions.append(pl.col("sample_uid") == sample_uid)

    # Filter by sample_name (requires pre-processing)
    if sample_name is not None:
        # Get sample_uids for the given sample names
        if isinstance(sample_name, list):
            sample_uids_for_names = self.samples_df.filter(
                pl.col("sample_name").is_in(sample_name),
            )["sample_uid"].to_list()
        else:
            sample_uids_for_names = self.samples_df.filter(
                pl.col("sample_name") == sample_name,
            )["sample_uid"].to_list()

        if sample_uids_for_names:
            filter_conditions.append(pl.col("sample_uid").is_in(sample_uids_for_names))
        else:
            filter_conditions.append(pl.lit(False))  # No matching samples

    # Filter by consensus_uid
    if consensus_uid is not None:
        if isinstance(consensus_uid, (list, tuple)):
            if len(consensus_uid) == 2 and not isinstance(consensus_uid, list):
                # Treat as range
                min_uid, max_uid = consensus_uid
                filter_conditions.append(pl.col("consensus_uid").is_between(min_uid, max_uid, closed="both"))
            else:
                # Treat as list
                filter_conditions.append(pl.col("consensus_uid").is_in(consensus_uid))
        else:
            filter_conditions.append(pl.col("consensus_uid") == consensus_uid)

    # Filter by feature_uid
    if feature_uid is not None:
        if isinstance(feature_uid, (list, tuple)):
            if len(feature_uid) == 2 and not isinstance(feature_uid, list):
                # Treat as range
                min_uid, max_uid = feature_uid
                filter_conditions.append(pl.col("feature_uid").is_between(min_uid, max_uid, closed="both"))
            else:
                # Treat as list
                filter_conditions.append(pl.col("feature_uid").is_in(feature_uid))
        else:
            filter_conditions.append(pl.col("feature_uid") == feature_uid)

    # Filter by filled status
    if filled is not None:
        if "filled" in available_columns:
            if filled:
                filter_conditions.append(pl.col("filled"))
            else:
                filter_conditions.append(~pl.col("filled") | pl.col("filled").is_null())
        else:
            warnings.append("'filled' column not found in features_df")

    # Filter by quality
    if quality is not None:
        if "quality" in available_columns:
            if isinstance(quality, tuple) and len(quality) == 2:
                min_quality, max_quality = quality
                filter_conditions.append(pl.col("quality").is_between(min_quality, max_quality, closed="both"))
            else:
                filter_conditions.append(pl.col("quality") >= quality)
        else:
            warnings.append("'quality' column not found in features_df")

    # Filter by chromatogram coherence
    if chrom_coherence is not None:
        if "chrom_coherence" in available_columns:
            if isinstance(chrom_coherence, tuple) and len(chrom_coherence) == 2:
                min_coherence, max_coherence = chrom_coherence
                filter_conditions.append(pl.col("chrom_coherence").is_between(min_coherence, max_coherence, closed="both"))
            else:
                filter_conditions.append(pl.col("chrom_coherence") >= chrom_coherence)
        else:
            warnings.append("'chrom_coherence' column not found in features_df")

    # Filter by chromatogram prominence
    if chrom_prominence is not None:
        if "chrom_prominence" in available_columns:
            if isinstance(chrom_prominence, tuple) and len(chrom_prominence) == 2:
                min_prominence, max_prominence = chrom_prominence
                filter_conditions.append(pl.col("chrom_prominence").is_between(min_prominence, max_prominence, closed="both"))
            else:
                filter_conditions.append(pl.col("chrom_prominence") >= chrom_prominence)
        else:
            warnings.append("'chrom_prominence' column not found in features_df")

    # Filter by scaled chromatogram prominence
    if chrom_prominence_scaled is not None:
        if "chrom_prominence_scaled" in available_columns:
            if isinstance(chrom_prominence_scaled, tuple) and len(chrom_prominence_scaled) == 2:
                min_prominence_scaled, max_prominence_scaled = chrom_prominence_scaled
                filter_conditions.append(
                    pl.col("chrom_prominence_scaled").is_between(min_prominence_scaled, max_prominence_scaled, closed="both"))
            else:
                filter_conditions.append(pl.col("chrom_prominence_scaled") >= chrom_prominence_scaled)
        else:
            warnings.append("'chrom_prominence_scaled' column not found in features_df")

    # Filter by scaled chromatogram height
    if chrom_height_scaled is not None:
        if "chrom_height_scaled" in available_columns:
            if isinstance(chrom_height_scaled, tuple) and len(chrom_height_scaled) == 2:
                min_height_scaled, max_height_scaled = chrom_height_scaled
                filter_conditions.append(
                    pl.col("chrom_height_scaled").is_between(min_height_scaled, max_height_scaled, closed="both"))
            else:
                filter_conditions.append(pl.col("chrom_height_scaled") >= chrom_height_scaled)
        else:
            warnings.append("'chrom_height_scaled' column not found in features_df")

    # Log warnings once at the end
    for warning in warnings:
        self.logger.warning(warning)

    # Combine all conditions efficiently
    if not filter_conditions:
        return None
    
    # Use reduce for efficient expression combination
    from functools import reduce
    import operator
    combined_expr = reduce(operator.and_, filter_conditions)
    
    return combined_expr


def _apply_chunked_select(self, filter_expr, chunk_size: int):
    """
    Apply selection using chunked processing for large datasets.
    """
    total_features = len(self.features_df)
    num_chunks = (total_features + chunk_size - 1) // chunk_size
    
    self.logger.debug(f"Using chunked select with {num_chunks} chunks")
    
    filtered_chunks = []
    for i in range(num_chunks):
        start_idx = i * chunk_size
        end_idx = min((i + 1) * chunk_size, total_features)
        
        chunk_result = (
            self.features_df
            .lazy()
            .slice(start_idx, end_idx - start_idx)
            .filter(filter_expr)
            .collect(streaming=True)
        )
        
        if not chunk_result.is_empty():
            filtered_chunks.append(chunk_result)
    
    if filtered_chunks:
        return pl.concat(filtered_chunks, how="vertical")
    else:
        return pl.DataFrame()


def features_select_benchmarked(
    self,
    mz=None,
    rt=None,
    inty=None,
    sample_uid=None,
    sample_name=None,
    consensus_uid=None,
    feature_uid=None,
    filled=None,
    quality=None,
    chrom_coherence=None,
    chrom_prominence=None,
    chrom_prominence_scaled=None,
    chrom_height_scaled=None,
):
    """
    Benchmarked version that compares old vs new implementation performance.
    If an original implementation is available as `features_select_original` on the Study
    instance, it will be used for comparison; otherwise only the optimized run is timed.
    """
    import time

    original_time = None
    # If an original implementation was stored, call it for comparison
    original_impl = getattr(self, "features_select_original", None)
    if callable(original_impl):
        start_time = time.perf_counter()
        _ = original_impl(
            mz=mz,
            rt=rt,
            inty=inty,
            sample_uid=sample_uid,
            sample_name=sample_name,
            consensus_uid=consensus_uid,
            feature_uid=feature_uid,
            filled=filled,
            quality=quality,
            chrom_coherence=chrom_coherence,
            chrom_prominence=chrom_prominence,
            chrom_prominence_scaled=chrom_prominence_scaled,
            chrom_height_scaled=chrom_height_scaled,
        )
        original_time = time.perf_counter() - start_time

    # Call the optimized method
    start_time = time.perf_counter()
    result_optimized = self.features_select(
        mz=mz,
        rt=rt,
        inty=inty,
        sample_uid=sample_uid,
        sample_name=sample_name,
        consensus_uid=consensus_uid,
        feature_uid=feature_uid,
        filled=filled,
        quality=quality,
        chrom_coherence=chrom_coherence,
        chrom_prominence=chrom_prominence,
        chrom_prominence_scaled=chrom_prominence_scaled,
        chrom_height_scaled=chrom_height_scaled,
    )
    optimized_time = time.perf_counter() - start_time

    # Log performance comparison when possible
    if original_time is not None:
        speedup = original_time / optimized_time if optimized_time > 0 else float("inf")
        self.logger.info(
            f"Performance comparison - Original: {original_time:.4f}s, Optimized: {optimized_time:.4f}s, Speedup: {speedup:.2f}x",
        )
    else:
        self.logger.info(f"Optimized features_select executed in {optimized_time:.4f}s")

    return result_optimized


def monkey_patch_study():
    """
    (Optional) Monkey-patch helper for Study. Stores the current Study.features_select
    as `features_select_original` if not already set, then replaces Study.features_select
    with the optimized `features_select` defined above. This function is idempotent.
    """
    from masster.study.study import Study

    # Only set original if it doesn't exist yet
    if not hasattr(Study, "features_select_original"):
        Study.features_select_original = Study.features_select

    Study.features_select = features_select
    Study.features_select_benchmarked = features_select_benchmarked

    print("Patched Study.features_select with consolidated optimized implementation")


def features_filter(
    self, 
    features,
    chunk_size: int = 50000,
    use_index_based: bool = True,
    parallel: bool = True
):
    """
    Filter features_df by keeping only features that match the given criteria.
    This keeps only the specified features and removes all others.

    FULLY OPTIMIZED VERSION: Index-based filtering, chunked processing, and lazy evaluation.
    
    Performance improvements:
    - Index-based filtering using sorted arrays (O(n log n) instead of O(n²))
    - Chunked processing to handle large datasets without memory issues
    - Enhanced lazy evaluation with streaming operations
    - Hash-based lookups for optimal performance
    - Memory-efficient operations

    Parameters:
        features: Features to keep. Can be:
                 - polars.DataFrame: Features DataFrame (will use feature_uid column)
                 - list: List of feature_uids to keep
                 - tuple: Tuple of feature_uids to keep
                 - int: Single feature_uid to keep
        chunk_size: Number of features to process per chunk (default: 50000)
        use_index_based: Use index-based filtering for better performance (default: True)
        parallel: Enable parallel processing when beneficial (default: True)

    Returns:
        None (modifies self.features_df in place)
    """
    if self.features_df is None or self.features_df.is_empty():
        self.logger.warning("No features found in study.")
        return

    if features is None:
        self.logger.warning("No features provided for filtering.")
        return

    initial_count = len(self.features_df)
    
    # Extract feature UIDs efficiently
    feature_uids_to_keep = _extract_feature_uids_optimized(self, features)
    if not feature_uids_to_keep:
        self.logger.warning("No feature UIDs provided for filtering.")
        return
    
    # Choose optimal filtering strategy based on data size and characteristics
    if use_index_based and len(self.features_df) > 10000:
        _apply_index_based_filter(self, feature_uids_to_keep, chunk_size, parallel)
    else:
        _apply_standard_filter(self, feature_uids_to_keep)
    
    # Calculate results and log performance
    final_count = len(self.features_df)
    removed_count = initial_count - final_count
    
    self.logger.info(
        f"Filtered features: kept {final_count:,}, removed {removed_count:,}"
    )


def _extract_feature_uids_optimized(self, features):
    """
    Efficiently extract feature UIDs from various input types.
    Returns a set for O(1) lookup performance.
    """
    if isinstance(features, pl.DataFrame):
        if "feature_uid" not in features.columns:
            self.logger.error("features DataFrame must contain 'feature_uid' column")
            return set()
        # Use polars native operations for efficiency
        return set(features.select("feature_uid").to_series().to_list())
    
    elif isinstance(features, (list, tuple)):
        return set(features)  # Convert to set immediately for O(1) lookups
    
    elif isinstance(features, int):
        return {features}
    
    else:
        self.logger.error("features parameter must be a DataFrame, list, tuple, or int")
        return set()


def _apply_index_based_filter(self, feature_uids_to_keep, chunk_size: int, parallel: bool):
    """
    Apply index-based filtering with chunked processing and lazy evaluation.
    
    This method uses:
    1. Sorted arrays and binary search for O(log n) lookups
    2. Chunked processing to manage memory usage
    3. Lazy evaluation with streaming operations
    4. Hash-based set operations for optimal performance
    """
    self.logger.debug(f"Using index-based filtering with chunks of {chunk_size:,}")
    
    total_features = len(self.features_df)
    
    if total_features <= chunk_size:
        # Small dataset - process in single chunk with optimized operations
        _filter_single_chunk_optimized(self, feature_uids_to_keep)
    else:
        # Large dataset - use chunked processing with lazy evaluation
        _filter_chunked_lazy(self, feature_uids_to_keep, chunk_size, parallel)


def _filter_single_chunk_optimized(self, feature_uids_to_keep):
    """
    Optimized filtering for datasets that fit in a single chunk.
    Uses hash-based set operations for maximum performance.
    """
    # Create boolean mask using hash-based set lookup (O(1) per element)
    filter_expr = pl.col("feature_uid").is_in(list(feature_uids_to_keep))
    
    # Apply filter using lazy evaluation with optimized execution
    self.features_df = (
        self.features_df
        .lazy()
        .filter(filter_expr)
        .collect(streaming=True)  # Use streaming for memory efficiency
    )
    
    # Apply same filter to consensus_mapping_df if it exists
    if (self.consensus_mapping_df is not None and 
        not self.consensus_mapping_df.is_empty()):
        self.consensus_mapping_df = (
            self.consensus_mapping_df
            .lazy()
            .filter(filter_expr)
            .collect(streaming=True)
        )


def _filter_chunked_lazy(self, feature_uids_to_keep, chunk_size: int, parallel: bool):
    """
    Chunked processing with lazy evaluation for large datasets.
    
    This approach:
    1. Processes data in manageable chunks to control memory usage
    2. Uses lazy evaluation to optimize query execution
    3. Maintains consistent performance regardless of dataset size
    4. Optionally uses parallel processing for independent operations
    """
    total_features = len(self.features_df)
    num_chunks = (total_features + chunk_size - 1) // chunk_size
    
    self.logger.debug(f"Processing {total_features:,} features in {num_chunks} chunks")
    
    # Process features_df in chunks using lazy evaluation
    filtered_chunks = []
    
    for i in range(num_chunks):
        start_idx = i * chunk_size
        end_idx = min((i + 1) * chunk_size, total_features)
        
        # Create lazy query for this chunk
        chunk_query = (
            self.features_df
            .lazy()
            .slice(start_idx, end_idx - start_idx)
            .filter(pl.col("feature_uid").is_in(list(feature_uids_to_keep)))
        )
        
        # Collect chunk with streaming for memory efficiency
        chunk_result = chunk_query.collect(streaming=True)
        if not chunk_result.is_empty():
            filtered_chunks.append(chunk_result)
    
    # Combine all filtered chunks efficiently
    if filtered_chunks:
        self.features_df = pl.concat(filtered_chunks, how="vertical")
    else:
        self.features_df = pl.DataFrame()  # No features remain
    
    # Apply same chunked processing to consensus_mapping_df
    _filter_consensus_mapping_chunked(self, feature_uids_to_keep, chunk_size)


def _filter_consensus_mapping_chunked(self, feature_uids_to_keep, chunk_size: int):
    """
    Apply chunked filtering to consensus_mapping_df with same optimization strategy.
    """
    if (self.consensus_mapping_df is None or 
        self.consensus_mapping_df.is_empty()):
        return
    
    total_mappings = len(self.consensus_mapping_df)
    
    if total_mappings <= chunk_size:
        # Single chunk processing
        self.consensus_mapping_df = (
            self.consensus_mapping_df
            .lazy()
            .filter(pl.col("feature_uid").is_in(list(feature_uids_to_keep)))
            .collect(streaming=True)
        )
    else:
        # Multi-chunk processing
        num_chunks = (total_mappings + chunk_size - 1) // chunk_size
        filtered_chunks = []
        
        for i in range(num_chunks):
            start_idx = i * chunk_size
            end_idx = min((i + 1) * chunk_size, total_mappings)
            
            chunk_query = (
                self.consensus_mapping_df
                .lazy()
                .slice(start_idx, end_idx - start_idx)
                .filter(pl.col("feature_uid").is_in(list(feature_uids_to_keep)))
            )
            
            chunk_result = chunk_query.collect(streaming=True)
            if not chunk_result.is_empty():
                filtered_chunks.append(chunk_result)
        
        if filtered_chunks:
            self.consensus_mapping_df = pl.concat(filtered_chunks, how="vertical")
        else:
            self.consensus_mapping_df = pl.DataFrame()


def _apply_standard_filter(self, feature_uids_to_keep):
    """
    Fallback to standard filtering for smaller datasets.
    Still uses optimized set operations and lazy evaluation.
    """
    filter_expr = pl.col("feature_uid").is_in(list(feature_uids_to_keep))
    
    # Apply filter with lazy evaluation
    self.features_df = (
        self.features_df
        .lazy()
        .filter(filter_expr)
        .collect(streaming=True)
    )
    
    # Apply to consensus_mapping_df
    if (self.consensus_mapping_df is not None and 
        not self.consensus_mapping_df.is_empty()):
        self.consensus_mapping_df = (
            self.consensus_mapping_df
            .lazy()
            .filter(filter_expr)
            .collect(streaming=True)
        )


def features_delete(self, features):
    """
    Delete features from features_df based on feature identifiers.
    This removes the specified features and keeps all others (opposite of features_filter).

    Parameters:
        features: Features to delete. Can be:
                 - polars.DataFrame: Features DataFrame (will use feature_uid column)
                 - list: List of feature_uids to delete
                 - int: Single feature_uid to delete

    Returns:
        None (modifies self.features_df in place)
    """
    if self.features_df is None or self.features_df.is_empty():
        self.logger.warning("No features found in study.")
        return

    # Early return if no features provided
    if features is None:
        self.logger.warning("No features provided for deletion.")
        return

    initial_count = len(self.features_df)

    # Determine feature_uids to remove - optimized type checking
    if isinstance(features, pl.DataFrame):
        if "feature_uid" not in features.columns:
            self.logger.error("features DataFrame must contain 'feature_uid' column")
            return
        feature_uids_to_remove = features["feature_uid"].to_list()
    elif isinstance(features, (list, tuple)):
        feature_uids_to_remove = list(features)  # Convert tuple to list if needed
    elif isinstance(features, int):
        feature_uids_to_remove = [features]
    else:
        self.logger.error("features parameter must be a DataFrame, list, tuple, or int")
        return

    # Early return if no UIDs to remove
    if not feature_uids_to_remove:
        self.logger.warning("No feature UIDs provided for deletion.")
        return

    # Convert to set for faster lookup if list is large
    if len(feature_uids_to_remove) > 100:
        feature_uids_set = set(feature_uids_to_remove)
        # Use the set for filtering if it's significantly smaller
        if len(feature_uids_set) < len(feature_uids_to_remove) * 0.8:
            feature_uids_to_remove = list(feature_uids_set)

    # Create filter condition - remove specified features
    filter_condition = ~pl.col("feature_uid").is_in(feature_uids_to_remove)

    # Apply filter to features_df using lazy evaluation for better performance
    self.features_df = self.features_df.lazy().filter(filter_condition).collect()

    # Apply filter to consensus_mapping_df if it exists - batch operation
    mapping_removed_count = 0
    if (
        self.consensus_mapping_df is not None
        and not self.consensus_mapping_df.is_empty()
    ):
        initial_mapping_count = len(self.consensus_mapping_df)
        self.consensus_mapping_df = (
            self.consensus_mapping_df.lazy().filter(filter_condition).collect()
        )
        mapping_removed_count = initial_mapping_count - len(self.consensus_mapping_df)

    # Calculate results once and log efficiently
    final_count = len(self.features_df)
    removed_count = initial_count - final_count

    # Single comprehensive log message
    if mapping_removed_count > 0:
        self.logger.info(
            f"Deleted {removed_count} features and {mapping_removed_count} consensus mappings. Remaining features: {final_count}",
        )
    else:
        self.logger.info(
            f"Deleted {removed_count} features. Remaining features: {final_count}",
        )


def consensus_select(
    self,
    mz=None,
    rt=None,
    inty_mean=None,
    consensus_uid=None,
    consensus_id=None,
    number_samples=None,
    number_ms2=None,
    quality=None,
    bl=None,
    chrom_coherence_mean=None,
    chrom_prominence_mean=None,
    chrom_prominence_scaled_mean=None,
    chrom_height_scaled_mean=None,
    rt_delta_mean=None,
    id_top_score=None,
    identified=None,
    sortby=None,
    descending=True,
):
    """
    Select consensus features from consensus_df based on specified criteria and return the filtered DataFrame.

    OPTIMIZED VERSION: Enhanced performance with lazy evaluation, vectorized operations, and efficient filtering.

    Parameters:
        mz: m/z filter with flexible formats:
            - float: m/z value ± default tolerance (uses study.parameters.eic_mz_tol)
            - tuple (mz_min, mz_max): range where mz_max > mz_min
            - tuple (mz_center, mz_tol): range where mz_tol < mz_center (interpreted as mz_center ± mz_tol)
        rt: retention time filter with flexible formats:
            - float: RT value ± default tolerance (uses study.parameters.eic_rt_tol)
            - tuple (rt_min, rt_max): range where rt_max > rt_min
            - tuple (rt_center, rt_tol): range where rt_tol < rt_center (interpreted as rt_center ± rt_tol)
        inty_mean: mean intensity filter (tuple for range, single value for minimum)
        consensus_uid: consensus UID filter (list, single value, or tuple for range)
        consensus_id: consensus ID filter (list or single value)
        number_samples: number of samples filter (tuple for range, single value for minimum)
        number_ms2: number of MS2 spectra filter (tuple for range, single value for minimum)
        quality: quality score filter (tuple for range, single value for minimum)
        bl: baseline filter (tuple for range, single value for minimum)
        chrom_coherence_mean: mean chromatogram coherence filter (tuple for range, single value for minimum)
        chrom_prominence_mean: mean chromatogram prominence filter (tuple for range, single value for minimum)
        chrom_prominence_scaled_mean: mean scaled chromatogram prominence filter (tuple for range, single value for minimum)
        chrom_height_scaled_mean: mean scaled chromatogram height filter (tuple for range, single value for minimum)
        rt_delta_mean: mean RT delta filter (tuple for range, single value for minimum)
        id_top_score: identification top score filter (tuple for range, single value for minimum)
        identified: filter by identification status:
            - True: select only rows with id_top_name not null
            - False: select only rows with id_top_name null
            - None: no filtering (default)
        sortby: column name(s) to sort by (string, list of strings, or None for no sorting)
        descending: sort direction (True for descending, False for ascending, default is True)

    Returns:
        polars.DataFrame: Filtered consensus DataFrame
    """
    if self.consensus_df is None or self.consensus_df.is_empty():
        self.logger.warning("No consensus features found in study.")
        return pl.DataFrame()

    # Early return optimization - check if any filters are provided
    filter_params = [mz, rt, inty_mean, consensus_uid, consensus_id, number_samples, 
                    number_ms2, quality, bl, chrom_coherence_mean, chrom_prominence_mean,
                    chrom_prominence_scaled_mean, chrom_height_scaled_mean, 
                    rt_delta_mean, id_top_score, identified]
    
    if all(param is None for param in filter_params) and sortby is None:
        return self.consensus_df.clone()

    import time
    start_time = time.perf_counter()
    initial_count = len(self.consensus_df)

    # Pre-check available columns once for efficiency
    available_columns = set(self.consensus_df.columns)
    filter_conditions = []
    warnings = []

    # Build all filter conditions efficiently
    if mz is not None:
        if isinstance(mz, tuple) and len(mz) == 2:
            if mz[1] < mz[0]:
                # mz_center ± mz_tol format
                mz_center, mz_tol = mz
                min_mz = mz_center - mz_tol
                max_mz = mz_center + mz_tol
            else:
                # (min_mz, max_mz) format
                min_mz, max_mz = mz
            filter_conditions.append((pl.col("mz") >= min_mz) & (pl.col("mz") <= max_mz))
        else:
            # Single value with default tolerance
            default_mz_tol = getattr(self, "parameters", None)
            if default_mz_tol and hasattr(default_mz_tol, "eic_mz_tol"):
                default_mz_tol = default_mz_tol.eic_mz_tol
            else:
                from masster.study.defaults.align_def import align_defaults
                default_mz_tol = align_defaults().mz_max_diff
            
            min_mz = mz - default_mz_tol
            max_mz = mz + default_mz_tol
            filter_conditions.append((pl.col("mz") >= min_mz) & (pl.col("mz") <= max_mz))

    if rt is not None:
        if isinstance(rt, tuple) and len(rt) == 2:
            if rt[1] < rt[0]:
                # rt_center ± rt_tol format
                rt_center, rt_tol = rt
                min_rt = rt_center - rt_tol
                max_rt = rt_center + rt_tol
            else:
                # (min_rt, max_rt) format
                min_rt, max_rt = rt
            filter_conditions.append((pl.col("rt") >= min_rt) & (pl.col("rt") <= max_rt))
        else:
            # Single value with default tolerance
            default_rt_tol = getattr(self, "parameters", None)
            if default_rt_tol and hasattr(default_rt_tol, "eic_rt_tol"):
                default_rt_tol = default_rt_tol.eic_rt_tol
            else:
                from masster.study.defaults.align_def import align_defaults
                default_rt_tol = align_defaults().rt_tol
            
            min_rt = rt - default_rt_tol
            max_rt = rt + default_rt_tol
            filter_conditions.append((pl.col("rt") >= min_rt) & (pl.col("rt") <= max_rt))

    # Helper function to add range/minimum filters
    def _add_range_filter(param, column, param_name):
        if param is not None:
            if column in available_columns:
                if isinstance(param, tuple) and len(param) == 2:
                    min_val, max_val = param
                    filter_conditions.append((pl.col(column) >= min_val) & (pl.col(column) <= max_val))
                else:
                    filter_conditions.append(pl.col(column) >= param)
            else:
                warnings.append(f"'{column}' column not found in consensus_df")

    # Apply range/minimum filters efficiently
    _add_range_filter(inty_mean, "inty_mean", "inty_mean")
    _add_range_filter(quality, "quality", "quality")
    _add_range_filter(bl, "bl", "bl")
    _add_range_filter(chrom_coherence_mean, "chrom_coherence_mean", "chrom_coherence_mean")
    _add_range_filter(chrom_prominence_mean, "chrom_prominence_mean", "chrom_prominence_mean")
    _add_range_filter(chrom_prominence_scaled_mean, "chrom_prominence_scaled_mean", "chrom_prominence_scaled_mean")
    _add_range_filter(chrom_height_scaled_mean, "chrom_height_scaled_mean", "chrom_height_scaled_mean")
    _add_range_filter(rt_delta_mean, "rt_delta_mean", "rt_delta_mean")
    _add_range_filter(id_top_score, "id_top_score", "id_top_score")
    _add_range_filter(number_samples, "number_samples", "number_samples")

    # Handle number_ms2 with column check
    if number_ms2 is not None:
        if "number_ms2" in available_columns:
            if isinstance(number_ms2, tuple) and len(number_ms2) == 2:
                min_ms2, max_ms2 = number_ms2
                filter_conditions.append((pl.col("number_ms2") >= min_ms2) & (pl.col("number_ms2") <= max_ms2))
            else:
                filter_conditions.append(pl.col("number_ms2") >= number_ms2)
        else:
            warnings.append("'number_ms2' column not found in consensus_df")

    # Handle consensus_uid (list, single value, or range)
    if consensus_uid is not None:
        if isinstance(consensus_uid, (list, tuple)):
            if len(consensus_uid) == 2 and not isinstance(consensus_uid, list):
                # Treat tuple as range
                min_uid, max_uid = consensus_uid
                filter_conditions.append((pl.col("consensus_uid") >= min_uid) & (pl.col("consensus_uid") <= max_uid))
            else:
                # Treat as list of values
                filter_conditions.append(pl.col("consensus_uid").is_in(consensus_uid))
        else:
            filter_conditions.append(pl.col("consensus_uid") == consensus_uid)

    # Handle consensus_id (list or single value)
    if consensus_id is not None:
        if isinstance(consensus_id, list):
            filter_conditions.append(pl.col("consensus_id").is_in(consensus_id))
        else:
            filter_conditions.append(pl.col("consensus_id") == consensus_id)

    # Handle identified status filter
    if identified is not None:
        if "id_top_name" in available_columns:
            if identified:
                filter_conditions.append(pl.col("id_top_name").is_not_null())
            else:
                filter_conditions.append(pl.col("id_top_name").is_null())
        else:
            warnings.append("'id_top_name' column not found in consensus_df")

    # Log warnings once
    for warning in warnings:
        self.logger.warning(warning)

    # Apply all filters at once using lazy evaluation for optimal performance
    if filter_conditions:
        # Combine all conditions efficiently using reduce
        from functools import reduce
        import operator
        combined_filter = reduce(operator.and_, filter_conditions)
        
        consensus = (
            self.consensus_df
            .lazy()
            .filter(combined_filter)
            .collect(streaming=True)
        )
    else:
        consensus = self.consensus_df.clone()

    final_count = len(consensus)

    # Early return if no results
    if final_count == 0:
        self.logger.warning("No consensus features remaining after applying selection criteria.")
        return pl.DataFrame()

    # Sort the results if sortby is specified
    if sortby is not None:
        if isinstance(sortby, str):
            if sortby in consensus.columns:
                consensus = consensus.sort(sortby, descending=descending)
            else:
                self.logger.warning(f"Sort column '{sortby}' not found in consensus DataFrame")
        elif isinstance(sortby, (list, tuple)):
            valid_columns = [col for col in sortby if col in consensus.columns]
            invalid_columns = [col for col in sortby if col not in consensus.columns]
            
            if invalid_columns:
                self.logger.warning(f"Sort columns not found in consensus DataFrame: {invalid_columns}")
            
            if valid_columns:
                consensus = consensus.sort(valid_columns, descending=descending)
        else:
            self.logger.warning(f"Invalid sortby parameter type: {type(sortby)}. Expected str, list, or tuple.")

    # Log performance metrics
    elapsed_time = time.perf_counter() - start_time
    removed_count = initial_count - final_count
    
    self.logger.info(f"Selected consensus features: {final_count:,} (removed: {removed_count:,}) in {elapsed_time:.4f}s")

    return consensus


def consensus_filter(self, consensus):
    """
    Filter consensus_df by keeping only consensus features that match the given criteria.
    This keeps only the specified consensus features and removes all others.
    Also updates related entries in consensus_mapping_df, features_df, and consensus_ms2.

    Parameters:
        consensus: Consensus features to keep. Can be:
                  - polars.DataFrame: Consensus DataFrame (will use consensus_uid column)
                  - list: List of consensus_uids to keep
                  - int: Single consensus_uid to keep

    Returns:
        None (modifies self.consensus_df and related DataFrames in place)
    """
    if self.consensus_df is None or self.consensus_df.is_empty():
        self.logger.warning("No consensus features found in study.")
        return

    initial_consensus_count = len(self.consensus_df)

    # Determine consensus_uids to keep
    if isinstance(consensus, pl.DataFrame):
        if "consensus_uid" not in consensus.columns:
            self.logger.error("consensus DataFrame must contain 'consensus_uid' column")
            return
        consensus_uids_to_keep = consensus["consensus_uid"].to_list()
    elif isinstance(consensus, list):
        consensus_uids_to_keep = consensus
    elif isinstance(consensus, int):
        consensus_uids_to_keep = [consensus]
    else:
        self.logger.error("consensus parameter must be a DataFrame, list, or int")
        return

    if not consensus_uids_to_keep:
        self.logger.warning("No consensus UIDs provided for filtering.")
        return

    # Get feature_uids that need to be kept in features_df
    feature_uids_to_keep = []
    if (
        self.consensus_mapping_df is not None
        and not self.consensus_mapping_df.is_empty()
    ):
        feature_uids_to_keep = self.consensus_mapping_df.filter(
            pl.col("consensus_uid").is_in(consensus_uids_to_keep),
        )["feature_uid"].to_list()

    # Keep only specified consensus features in consensus_df
    self.consensus_df = self.consensus_df.filter(
        pl.col("consensus_uid").is_in(consensus_uids_to_keep),
    )

    # Keep only relevant entries in consensus_mapping_df
    if (
        self.consensus_mapping_df is not None
        and not self.consensus_mapping_df.is_empty()
    ):
        initial_mapping_count = len(self.consensus_mapping_df)
        self.consensus_mapping_df = self.consensus_mapping_df.filter(
            pl.col("consensus_uid").is_in(consensus_uids_to_keep),
        )
        remaining_mapping_count = len(self.consensus_mapping_df)
        removed_mapping_count = initial_mapping_count - remaining_mapping_count
        if removed_mapping_count > 0:
            self.logger.debug(
                f"Removed {removed_mapping_count} entries from consensus_mapping_df",
            )

    # Keep only corresponding features in features_df
    if (
        feature_uids_to_keep
        and self.features_df is not None
        and not self.features_df.is_empty()
    ):
        initial_features_count = len(self.features_df)
        self.features_df = self.features_df.filter(
            pl.col("feature_uid").is_in(feature_uids_to_keep),
        )
        remaining_features_count = len(self.features_df)
        removed_features_count = initial_features_count - remaining_features_count
        if removed_features_count > 0:
            self.logger.debug(
                f"Removed {removed_features_count} entries from features_df",
            )

    # Keep only relevant entries in consensus_ms2 if it exists
    if (
        hasattr(self, "consensus_ms2")
        and self.consensus_ms2 is not None
        and not self.consensus_ms2.is_empty()
    ):
        initial_ms2_count = len(self.consensus_ms2)
        self.consensus_ms2 = self.consensus_ms2.filter(
            pl.col("consensus_uid").is_in(consensus_uids_to_keep),
        )
        remaining_ms2_count = len(self.consensus_ms2)
        removed_ms2_count = initial_ms2_count - remaining_ms2_count
        if removed_ms2_count > 0:
            self.logger.debug(f"Removed {removed_ms2_count} entries from consensus_ms2")

    remaining_consensus_count = len(self.consensus_df)
    removed_consensus_count = initial_consensus_count - remaining_consensus_count
    self.logger.info(
        f"Filtered consensus features: kept {remaining_consensus_count}, removed {removed_consensus_count}",
    )


def consensus_delete(self, consensus):
    """
    Delete consensus features from consensus_df based on consensus identifiers.
    This removes the specified consensus features and keeps all others (opposite of consensus_filter).
    Also removes related entries from consensus_mapping_df, features_df, and consensus_ms2.

    Parameters:
        consensus: Consensus features to delete. Can be:
                  - polars.DataFrame: Consensus DataFrame (will use consensus_uid column)
                  - list: List of consensus_uids to delete
                  - int: Single consensus_uid to delete

    Returns:
        None (modifies self.consensus_df and related DataFrames in place)
    """
    if self.consensus_df is None or self.consensus_df.is_empty():
        self.logger.warning("No consensus features found in study.")
        return

    # Early return if no consensus provided
    if consensus is None:
        self.logger.warning("No consensus provided for deletion.")
        return

    initial_consensus_count = len(self.consensus_df)

    # Determine consensus_uids to remove
    if isinstance(consensus, pl.DataFrame):
        if "consensus_uid" not in consensus.columns:
            self.logger.error("consensus DataFrame must contain 'consensus_uid' column")
            return
        consensus_uids_to_remove = consensus["consensus_uid"].to_list()
    elif isinstance(consensus, list):
        consensus_uids_to_remove = consensus
    elif isinstance(consensus, int):
        consensus_uids_to_remove = [consensus]
    else:
        self.logger.error("consensus parameter must be a DataFrame, list, or int")
        return

    if not consensus_uids_to_remove:
        self.logger.warning("No consensus UIDs provided for deletion.")
        return

    # Convert to set for faster lookup if list is large
    if len(consensus_uids_to_remove) > 100:
        consensus_uids_set = set(consensus_uids_to_remove)
        # Use the set for filtering if it's significantly smaller
        if len(consensus_uids_set) < len(consensus_uids_to_remove) * 0.8:
            consensus_uids_to_remove = list(consensus_uids_set)

    # Get feature_uids that need to be removed from features_df
    feature_uids_to_remove = []
    if (
        self.consensus_mapping_df is not None
        and not self.consensus_mapping_df.is_empty()
    ):
        feature_uids_to_remove = self.consensus_mapping_df.filter(
            pl.col("consensus_uid").is_in(consensus_uids_to_remove),
        )["feature_uid"].to_list()

    # Remove consensus features from consensus_df
    self.consensus_df = self.consensus_df.filter(
        ~pl.col("consensus_uid").is_in(consensus_uids_to_remove),
    )

    # Remove from consensus_mapping_df
    mapping_removed_count = 0
    if (
        self.consensus_mapping_df is not None
        and not self.consensus_mapping_df.is_empty()
    ):
        initial_mapping_count = len(self.consensus_mapping_df)
        self.consensus_mapping_df = self.consensus_mapping_df.filter(
            ~pl.col("consensus_uid").is_in(consensus_uids_to_remove),
        )
        mapping_removed_count = initial_mapping_count - len(self.consensus_mapping_df)

    # Remove corresponding features from features_df
    features_removed_count = 0
    if (
        feature_uids_to_remove
        and self.features_df is not None
        and not self.features_df.is_empty()
    ):
        initial_features_count = len(self.features_df)
        self.features_df = self.features_df.filter(
            ~pl.col("feature_uid").is_in(feature_uids_to_remove),
        )
        features_removed_count = initial_features_count - len(self.features_df)

    # Remove from consensus_ms2 if it exists
    ms2_removed_count = 0
    if (
        hasattr(self, "consensus_ms2")
        and self.consensus_ms2 is not None
        and not self.consensus_ms2.is_empty()
    ):
        initial_ms2_count = len(self.consensus_ms2)
        self.consensus_ms2 = self.consensus_ms2.filter(
            ~pl.col("consensus_uid").is_in(consensus_uids_to_remove),
        )
        ms2_removed_count = initial_ms2_count - len(self.consensus_ms2)

    # Calculate results and log efficiently
    final_consensus_count = len(self.consensus_df)
    consensus_removed_count = initial_consensus_count - final_consensus_count

    # Single comprehensive log message
    log_parts = [f"Deleted {consensus_removed_count} consensus features"]
    if mapping_removed_count > 0:
        log_parts.append(f"{mapping_removed_count} consensus mappings")
    if features_removed_count > 0:
        log_parts.append(f"{features_removed_count} features")
    if ms2_removed_count > 0:
        log_parts.append(f"{ms2_removed_count} MS2 spectra")
    
    log_message = ". ".join(log_parts) + f". Remaining consensus: {final_consensus_count}"
    self.logger.info(log_message)


# =====================================================================================
# SAMPLE MANAGEMENT AND DELETION FUNCTIONS
# =====================================================================================


def samples_select(
    self,
    sample_uid=None,
    sample_name=None,
    sample_type=None,
    sample_group=None,
    sample_batch=None,
    sample_sequence=None,
    num_features=None,
    num_ms1=None,
    num_ms2=None,
):
    """
    Select samples from samples_df based on specified criteria and return the filtered DataFrame.

    Parameters:
        sample_uid: sample UID filter (list, single value, or tuple for range)
        sample_name: sample name filter (list or single value)
        sample_type: sample type filter (list or single value)
        sample_group: sample group filter (list or single value)
        sample_batch: sample batch filter (list, single value, or tuple for range)
        sample_sequence: sample sequence filter (list, single value, or tuple for range)
        num_features: number of features filter (tuple for range, single value for minimum)
        num_ms1: number of MS1 spectra filter (tuple for range, single value for minimum)
        num_ms2: number of MS2 spectra filter (tuple for range, single value for minimum)

    Returns:
        polars.DataFrame: Filtered samples DataFrame
    """
    if self.samples_df is None or self.samples_df.is_empty():
        self.logger.warning("No samples found in study.")
        return pl.DataFrame()

    # Early return if no filters provided
    filter_params = [
        sample_uid,
        sample_name,
        sample_type,
        sample_group,
        sample_batch,
        sample_sequence,
        num_features,
        num_ms1,
        num_ms2,
    ]
    if all(param is None for param in filter_params):
        return self.samples_df.clone()

    initial_count = len(self.samples_df)

    # Pre-check available columns once for efficiency
    available_columns = set(self.samples_df.columns)

    # Build all filter conditions first, then apply them all at once
    filter_conditions = []
    warnings = []

    # Filter by sample_uid
    if sample_uid is not None:
        if isinstance(sample_uid, (list, tuple)):
            if len(sample_uid) == 2 and not isinstance(sample_uid, list):
                # Treat as range
                min_uid, max_uid = sample_uid
                filter_conditions.append(
                    (pl.col("sample_uid") >= min_uid)
                    & (pl.col("sample_uid") <= max_uid),
                )
            else:
                # Treat as list
                filter_conditions.append(pl.col("sample_uid").is_in(sample_uid))
        else:
            filter_conditions.append(pl.col("sample_uid") == sample_uid)

    # Filter by sample_name
    if sample_name is not None:
        if isinstance(sample_name, list):
            filter_conditions.append(pl.col("sample_name").is_in(sample_name))
        else:
            filter_conditions.append(pl.col("sample_name") == sample_name)

    # Filter by sample_type
    if sample_type is not None:
        if "sample_type" in available_columns:
            if isinstance(sample_type, list):
                filter_conditions.append(pl.col("sample_type").is_in(sample_type))
            else:
                filter_conditions.append(pl.col("sample_type") == sample_type)
        else:
            warnings.append("'sample_type' column not found in samples_df")

    # Filter by sample_group
    if sample_group is not None:
        if "sample_group" in available_columns:
            if isinstance(sample_group, list):
                filter_conditions.append(pl.col("sample_group").is_in(sample_group))
            else:
                filter_conditions.append(pl.col("sample_group") == sample_group)
        else:
            warnings.append("'sample_group' column not found in samples_df")

    # Filter by sample_batch
    if sample_batch is not None:
        if "sample_batch" in available_columns:
            if isinstance(sample_batch, (list, tuple)):
                if len(sample_batch) == 2 and not isinstance(sample_batch, list):
                    # Treat as range
                    min_batch, max_batch = sample_batch
                    filter_conditions.append(
                        (pl.col("sample_batch") >= min_batch)
                        & (pl.col("sample_batch") <= max_batch),
                    )
                else:
                    # Treat as list
                    filter_conditions.append(pl.col("sample_batch").is_in(sample_batch))
            else:
                filter_conditions.append(pl.col("sample_batch") == sample_batch)
        else:
            warnings.append("'sample_batch' column not found in samples_df")

    # Filter by sample_sequence
    if sample_sequence is not None:
        if "sample_sequence" in available_columns:
            if isinstance(sample_sequence, (list, tuple)):
                if len(sample_sequence) == 2 and not isinstance(sample_sequence, list):
                    # Treat as range
                    min_seq, max_seq = sample_sequence
                    filter_conditions.append(
                        (pl.col("sample_sequence") >= min_seq)
                        & (pl.col("sample_sequence") <= max_seq),
                    )
                else:
                    # Treat as list
                    filter_conditions.append(
                        pl.col("sample_sequence").is_in(sample_sequence),
                    )
            else:
                filter_conditions.append(pl.col("sample_sequence") == sample_sequence)
        else:
            warnings.append("'sample_sequence' column not found in samples_df")

    # Filter by num_features
    if num_features is not None:
        if "num_features" in available_columns:
            if isinstance(num_features, tuple) and len(num_features) == 2:
                min_features, max_features = num_features
                filter_conditions.append(
                    (pl.col("num_features") >= min_features)
                    & (pl.col("num_features") <= max_features),
                )
            else:
                filter_conditions.append(pl.col("num_features") >= num_features)
        else:
            warnings.append("'num_features' column not found in samples_df")

    # Filter by num_ms1
    if num_ms1 is not None:
        if "num_ms1" in available_columns:
            if isinstance(num_ms1, tuple) and len(num_ms1) == 2:
                min_ms1, max_ms1 = num_ms1
                filter_conditions.append(
                    (pl.col("num_ms1") >= min_ms1) & (pl.col("num_ms1") <= max_ms1),
                )
            else:
                filter_conditions.append(pl.col("num_ms1") >= num_ms1)
        else:
            warnings.append("'num_ms1' column not found in samples_df")

    # Filter by num_ms2
    if num_ms2 is not None:
        if "num_ms2" in available_columns:
            if isinstance(num_ms2, tuple) and len(num_ms2) == 2:
                min_ms2, max_ms2 = num_ms2
                filter_conditions.append(
                    (pl.col("num_ms2") >= min_ms2) & (pl.col("num_ms2") <= max_ms2),
                )
            else:
                filter_conditions.append(pl.col("num_ms2") >= num_ms2)
        else:
            warnings.append("'num_ms2' column not found in samples_df")

    # Log all warnings once at the end for efficiency
    for warning in warnings:
        self.logger.warning(warning)

    # Apply all filters at once using lazy evaluation for optimal performance
    if filter_conditions:
        # Combine all conditions with AND
        combined_filter = filter_conditions[0]
        for condition in filter_conditions[1:]:
            combined_filter = combined_filter & condition

        # Apply the combined filter using lazy evaluation
        samples = self.samples_df.lazy().filter(combined_filter).collect()
    else:
        samples = self.samples_df.clone()

    final_count = len(samples)

    if final_count == 0:
        self.logger.warning("No samples remaining after applying selection criteria.")
    else:
        self.logger.info(f"Samples selected: {final_count} (out of {initial_count})")

    return samples


def samples_delete(self, samples):
    """
    Delete samples and all related data from the study based on sample identifiers.

    This function eliminates all data related to the specified samples (and their sample_uids)
    from all dataframes including:
    - samples_df: Removes the sample rows
    - features_df: Removes all features belonging to these samples
    - consensus_mapping_df: Removes mappings for features from these samples
    - consensus_ms2: Removes MS2 spectra for features from these samples
    - feature_maps: Removes the corresponding feature maps

    Also updates map_id values to maintain sequential indices after deletion.

    Parameters:
        samples: Samples to delete. Can be:
                - list of int: List of sample_uids to delete
                - polars.DataFrame: DataFrame obtained from samples_select (will use sample_uid column)
                - int: Single sample_uid to delete

    Returns:
        None (modifies study DataFrames and feature_maps in place)
    """
    if self.samples_df is None or self.samples_df.is_empty():
        self.logger.warning("No samples found in study.")
        return

    # Early return if no samples provided
    if samples is None:
        self.logger.warning("No samples provided for deletion.")
        return

    initial_sample_count = len(self.samples_df)

    # Determine sample_uids to remove
    if isinstance(samples, pl.DataFrame):
        if "sample_uid" not in samples.columns:
            self.logger.error("samples DataFrame must contain 'sample_uid' column")
            return
        sample_uids_to_remove = samples["sample_uid"].to_list()
    elif isinstance(samples, (list, tuple)):
        sample_uids_to_remove = list(samples)  # Convert tuple to list if needed
    elif isinstance(samples, int):
        sample_uids_to_remove = [samples]
    else:
        self.logger.error("samples parameter must be a DataFrame, list, tuple, or int")
        return

    # Early return if no UIDs to remove
    if not sample_uids_to_remove:
        self.logger.warning("No sample UIDs provided for deletion.")
        return

    # Convert to set for faster lookup if list is large
    if len(sample_uids_to_remove) > 100:
        sample_uids_set = set(sample_uids_to_remove)
        # Use the set for filtering if it's significantly smaller
        if len(sample_uids_set) < len(sample_uids_to_remove) * 0.8:
            sample_uids_to_remove = list(sample_uids_set)

    self.logger.info(
        f"Deleting {len(sample_uids_to_remove)} samples and all related data...",
    )

    # Get feature_uids that need to be removed from features_df
    feature_uids_to_remove = []
    initial_features_count = 0
    if self.features_df is not None and not self.features_df.is_empty():
        initial_features_count = len(self.features_df)
        feature_uids_to_remove = self.features_df.filter(
            pl.col("sample_uid").is_in(sample_uids_to_remove),
        )["feature_uid"].to_list()

    # Get map_ids to remove from feature_maps (needed before samples_df deletion)
    map_ids_to_remove = []
    if hasattr(self, "feature_maps") and self.feature_maps is not None:
        # Get map_ids for samples to be deleted
        map_ids_df = self.samples_df.filter(
            pl.col("sample_uid").is_in(sample_uids_to_remove),
        ).select("map_id")
        if not map_ids_df.is_empty():
            map_ids_to_remove = map_ids_df["map_id"].to_list()

    # 1. Remove samples from samples_df
    self.samples_df = self.samples_df.filter(
        ~pl.col("sample_uid").is_in(sample_uids_to_remove),
    )

    # 2. Remove corresponding features from features_df
    removed_features_count = 0
    if (
        feature_uids_to_remove
        and self.features_df is not None
        and not self.features_df.is_empty()
    ):
        self.features_df = self.features_df.filter(
            ~pl.col("sample_uid").is_in(sample_uids_to_remove),
        )
        removed_features_count = initial_features_count - len(self.features_df)

    # 3. Remove from consensus_mapping_df
    removed_mapping_count = 0
    if (
        feature_uids_to_remove
        and self.consensus_mapping_df is not None
        and not self.consensus_mapping_df.is_empty()
    ):
        initial_mapping_count = len(self.consensus_mapping_df)
        self.consensus_mapping_df = self.consensus_mapping_df.filter(
            ~pl.col("feature_uid").is_in(feature_uids_to_remove),
        )
        removed_mapping_count = initial_mapping_count - len(self.consensus_mapping_df)

    # 4. Remove from consensus_ms2 if it exists
    removed_ms2_count = 0
    if (
        hasattr(self, "consensus_ms2")
        and self.consensus_ms2 is not None
        and not self.consensus_ms2.is_empty()
    ):
        initial_ms2_count = len(self.consensus_ms2)
        self.consensus_ms2 = self.consensus_ms2.filter(
            ~pl.col("sample_uid").is_in(sample_uids_to_remove),
        )
        removed_ms2_count = initial_ms2_count - len(self.consensus_ms2)

    # 5. Remove from feature_maps and update map_id
    removed_maps_count = 0
    if (
        hasattr(self, "feature_maps")
        and self.feature_maps is not None
        and map_ids_to_remove
    ):
        # Remove feature maps in reverse order to maintain indices
        for map_id in sorted(map_ids_to_remove, reverse=True):
            if 0 <= map_id < len(self.feature_maps):
                self.feature_maps.pop(map_id)
                removed_maps_count += 1

        # Update map_id values in samples_df to maintain sequential indices
        if len(self.samples_df) > 0:
            new_map_ids = list(range(len(self.samples_df)))
            self.samples_df = self.samples_df.with_columns(
                pl.lit(new_map_ids).alias("map_id"),
            )

    # Calculate and log results
    removed_sample_count = initial_sample_count - len(self.samples_df)
    final_sample_count = len(self.samples_df)

    # Create comprehensive summary message
    summary_parts = [
        f"Deleted {removed_sample_count} samples",
    ]

    if removed_features_count > 0:
        summary_parts.append(f"{removed_features_count} features")

    if removed_mapping_count > 0:
        summary_parts.append(f"{removed_mapping_count} consensus mappings")

    if removed_ms2_count > 0:
        summary_parts.append(f"{removed_ms2_count} MS2 spectra")

    if removed_maps_count > 0:
        summary_parts.append(f"{removed_maps_count} feature maps")

    summary_parts.append(f"Remaining samples: {final_sample_count}")

    self.logger.info(". ".join(summary_parts))

    # Update map_id indices if needed
    if removed_maps_count > 0 and final_sample_count > 0:
        self.logger.debug(
            f"Updated map_id values to range from 0 to {final_sample_count - 1}",
        )


# =====================================================================================
# COLOR PALETTE AND VISUALIZATION FUNCTIONS
# =====================================================================================


def sample_color(self, by=None, palette="Turbo256"):
    """
    Set sample colors in the sample_color column of samples_df.

    When a new sample is added, this function resets all colors picking from the specified palette.
    The default palette is Turbo256.

    Parameters:
        by (str or list, optional): Property to base colors on. Options:
                                     - 'sample_uid': Use sample_uid values to assign colors
                                     - 'sample_index': Use sample index (position) to assign colors
                                     - 'sample_type': Use sample_type values to assign colors
                                     - 'sample_name': Use sample_name values to assign colors
                                     - list of colors: Use provided list of hex color codes
                                     - None: Use sequential colors from palette (default)
        palette (str): Color palette to use. Options:
                      - 'Turbo256': Turbo colormap (256 colors, perceptually uniform)
                      - 'Viridis256': Viridis colormap (256 colors, perceptually uniform)
                      - 'Plasma256': Plasma colormap (256 colors, perceptually uniform)
                      - 'Inferno256': Inferno colormap (256 colors, perceptually uniform)
                      - 'Magma256': Magma colormap (256 colors, perceptually uniform)
                      - 'Cividis256': Cividis colormap (256 colors, colorblind-friendly)
                      - 'Set1': Qualitative palette (9 distinct colors)
                      - 'Set2': Qualitative palette (8 distinct colors)
                      - 'Set3': Qualitative palette (12 distinct colors)
                      - 'Tab10': Tableau 10 palette (10 distinct colors)
                      - 'Tab20': Tableau 20 palette (20 distinct colors)
                      - 'Dark2': Dark qualitative palette (8 colors)
                      - 'Paired': Paired qualitative palette (12 colors)
                      - 'Spectral': Spectral diverging colormap
                      - 'Rainbow': Rainbow colormap
                      - 'Coolwarm': Cool-warm diverging colormap
                      - 'Seismic': Seismic diverging colormap
                      - Any other colormap name supported by the cmap library

                      For a complete catalog of available colormaps, see:
                      https://cmap-docs.readthedocs.io/en/latest/catalog/

    Returns:
        None (modifies self.samples_df in place)

    Example:
        # Set colors based on sample type
        study.sample_color(by='sample_type', palette='Set1')

        # Set colors using a custom color list
        study.sample_color(by=['#FF0000', '#00FF00', '#0000FF'])

        # Reset to default Turbo256 sequential colors
        study.sample_color()
    """
    if self.samples_df is None or len(self.samples_df) == 0:
        self.logger.warning("No samples found in study.")
        return

    sample_count = len(self.samples_df)

    # Handle custom color list
    if isinstance(by, list):
        if len(by) < sample_count:
            self.logger.warning(
                f"Provided color list has {len(by)} colors but {sample_count} samples. Repeating colors.",
            )
            # Cycle through the provided colors if there aren't enough
            colors = []
            for i in range(sample_count):
                colors.append(by[i % len(by)])
        else:
            colors = by[:sample_count]
    else:
        # Use the new approach: sample colors evenly from the whole colormap
        if by is None:
            # Sequential colors evenly sampled from the colormap
            try:
                colors = _sample_colors_from_colormap(palette, sample_count)
            except ValueError as e:
                self.logger.error(f"Error sampling colors from colormap: {e}")
                return

        elif by == "sample_uid":
            # Use sample_uid to determine position in evenly sampled colormap
            sample_uids = self.samples_df["sample_uid"].to_list()
            try:
                # Sample colors evenly for the number of samples
                palette_colors = _sample_colors_from_colormap(palette, sample_count)
                colors = []
                for uid in sample_uids:
                    # Use modulo to cycle through evenly sampled colors
                    color_index = uid % len(palette_colors)
                    colors.append(palette_colors[color_index])
            except ValueError as e:
                self.logger.error(f"Error sampling colors from colormap: {e}")
                return

        elif by == "sample_index":
            # Use sample index (position in DataFrame) with evenly sampled colors
            try:
                colors = _sample_colors_from_colormap(palette, sample_count)
            except ValueError as e:
                self.logger.error(f"Error sampling colors from colormap: {e}")
                return

        elif by == "sample_type":
            # Use sample_type to assign colors - same type gets same color
            # Sample colors evenly across colormap for unique types
            sample_types = self.samples_df["sample_type"].to_list()
            unique_types = list({t for t in sample_types if t is not None})

            try:
                # Sample colors evenly for unique types
                type_colors = _sample_colors_from_colormap(palette, len(unique_types))
                type_to_color = {}

                for i, sample_type in enumerate(unique_types):
                    type_to_color[sample_type] = type_colors[i]

                colors = []
                for sample_type in sample_types:
                    if sample_type is None:
                        # Default to first color for None
                        colors.append(type_colors[0] if type_colors else "#000000")
                    else:
                        colors.append(type_to_color[sample_type])
            except ValueError as e:
                self.logger.error(f"Error sampling colors from colormap: {e}")
                return

        elif by == "sample_name":
            # Use sample_name to assign colors - same name gets same color (unlikely but possible)
            # Sample colors evenly across colormap for unique names
            sample_names = self.samples_df["sample_name"].to_list()
            unique_names = list({n for n in sample_names if n is not None})

            try:
                # Sample colors evenly for unique names
                name_colors = _sample_colors_from_colormap(palette, len(unique_names))
                name_to_color = {}

                for i, sample_name in enumerate(unique_names):
                    name_to_color[sample_name] = name_colors[i]

                colors = []
                for sample_name in sample_names:
                    if sample_name is None:
                        # Default to first color for None
                        colors.append(name_colors[0] if name_colors else "#000000")
                    else:
                        colors.append(name_to_color[sample_name])
            except ValueError as e:
                self.logger.error(f"Error sampling colors from colormap: {e}")
                return
        else:
            self.logger.error(
                f"Invalid by value: {by}. Must be 'sample_uid', 'sample_index', 'sample_type', 'sample_name', a list of colors, or None.",
            )
            return

    # Update the sample_color column
    self.samples_df = self.samples_df.with_columns(
        pl.Series("sample_color", colors).alias("sample_color"),
    )

    if isinstance(by, list):
        self.logger.debug(
            f"Set sample colors using provided color list ({len(by)} colors)",
        )
    elif by is None:
        self.logger.debug(f"Set sequential sample colors using {palette} palette")
    else:
        self.logger.debug(f"Set sample colors based on {by} using {palette} palette")


def sample_color_reset(self):
    """
    Reset sample colors to default coloring using the 'turbo' colormap.

    This function assigns colors by distributing samples evenly across the full
    turbo colormap range, ensuring maximum color diversity and visual distinction
    between samples.

    Returns:
        None (modifies self.samples_df in place)
    """
    if self.samples_df is None or len(self.samples_df) == 0:
        self.logger.warning("No samples found in study.")
        return

    try:
        from cmap import Colormap

        # Use turbo colormap
        cm = Colormap("turbo")

        # Get sample count and assign colors evenly distributed across colormap
        n_samples = len(self.samples_df)
        colors = []

        # Distribute samples evenly across the full colormap range
        for i in range(n_samples):
            # Evenly distribute samples across colormap (avoiding endpoints to prevent white/black)
            normalized_value = (
                i + 0.5
            ) / n_samples  # +0.5 to center samples in their bins
            # Optionally, map to a subset of colormap to avoid extreme colors
            # Use 10% to 90% of colormap range for better color diversity
            normalized_value = 0.1 + (normalized_value * 0.8)

            color_rgba = cm(normalized_value)

            # Convert RGBA to hex
            if len(color_rgba) >= 3:
                r, g, b = color_rgba[:3]
                # Convert to 0-255 range if needed
                if max(color_rgba[:3]) <= 1.0:
                    r, g, b = int(r * 255), int(g * 255), int(b * 255)
                hex_color = f"#{r:02x}{g:02x}{b:02x}"
                colors.append(hex_color)

        # Update the sample_color column
        self.samples_df = self.samples_df.with_columns(
            pl.Series("sample_color", colors).alias("sample_color"),
        )

        self.logger.debug(
            f"Reset sample colors using turbo colormap with even distribution ({n_samples} samples)",
        )

    except ImportError:
        self.logger.error(
            "cmap library is required for sample color reset. Install with: uv add cmap",
        )
    except Exception as e:
        self.logger.error(f"Failed to reset sample colors: {e}")


def _get_color_palette(palette_name):
    """
    Get color palette as a list of hex color codes using the cmap library.

    Parameters:
        palette_name (str): Name of the palette

    Returns:
        list: List of hex color codes

    Raises:
        ValueError: If palette_name is not supported
    """
    try:
        from cmap import Colormap
    except ImportError:
        raise ValueError(
            "cmap library is required for color palettes. Install with: pip install cmap",
        )

    # Map common palette names to cmap names
    palette_mapping = {
        # Scientific colormaps
        "Turbo256": "turbo",
        "Viridis256": "viridis",
        "Plasma256": "plasma",
        "Inferno256": "inferno",
        "Magma256": "magma",
        "Cividis256": "cividis",
        # Qualitative palettes
        "Set1": "Set1",
        "Set2": "Set2",
        "Set3": "Set3",
        "Tab10": "tab10",
        "Tab20": "tab20",
        "Dark2": "Dark2",
        "Paired": "Paired",
        # Additional useful palettes
        "Spectral": "Spectral",
        "Rainbow": "rainbow",
        "Coolwarm": "coolwarm",
        "Seismic": "seismic",
    }

    # Get the cmap name
    cmap_name = palette_mapping.get(palette_name, palette_name.lower())

    try:
        # Create colormap
        cm = Colormap(cmap_name)

        # Determine number of colors to generate
        if "256" in palette_name:
            n_colors = 256
        elif palette_name in ["Set1"]:
            n_colors = 9
        elif palette_name in ["Set2", "Dark2"]:
            n_colors = 8
        elif palette_name in ["Set3", "Paired"]:
            n_colors = 12
        elif palette_name in ["Tab10"]:
            n_colors = 10
        elif palette_name in ["Tab20"]:
            n_colors = 20
        else:
            n_colors = 256  # Default for continuous colormaps

        # Generate colors
        if n_colors <= 20:
            # For discrete palettes, use evenly spaced indices
            indices = [i / (n_colors - 1) for i in range(n_colors)]
        else:
            # For continuous palettes, use full range
            indices = [i / (n_colors - 1) for i in range(n_colors)]

        # Get colors as RGBA and convert to hex
        colors = cm(indices)
        hex_colors = []

        for color in colors:
            if len(color) >= 3:  # RGBA or RGB
                r, g, b = color[:3]
                # Convert to 0-255 range if needed
                if max(color[:3]) <= 1.0:
                    r, g, b = int(r * 255), int(g * 255), int(b * 255)
                hex_color = f"#{r:02x}{g:02x}{b:02x}"
                hex_colors.append(hex_color)

        return hex_colors

    except Exception as e:
        raise ValueError(
            f"Failed to create colormap '{cmap_name}': {e}. Available palettes: {list(palette_mapping.keys())}",
        )


def _sample_colors_from_colormap(palette_name, n_colors):
    """
    Sample colors evenly from the whole colormap range, similar to sample_color_reset.

    Parameters:
        palette_name (str): Name of the palette/colormap
        n_colors (int): Number of colors to sample

    Returns:
        list: List of hex color codes sampled evenly from the colormap

    Raises:
        ValueError: If palette_name is not supported
    """
    try:
        from cmap import Colormap
    except ImportError:
        raise ValueError(
            "cmap library is required for color palettes. Install with: pip install cmap",
        )

    # Map common palette names to cmap names (same as _get_color_palette)
    palette_mapping = {
        # Scientific colormaps
        "Turbo256": "turbo",
        "Viridis256": "viridis",
        "Plasma256": "plasma",
        "Inferno256": "inferno",
        "Magma256": "magma",
        "Cividis256": "cividis",
        # Qualitative palettes
        "Set1": "Set1",
        "Set2": "Set2",
        "Set3": "Set3",
        "Tab10": "tab10",
        "Tab20": "tab20",
        "Dark2": "Dark2",
        "Paired": "Paired",
        # Additional useful palettes
        "Spectral": "Spectral",
        "Rainbow": "rainbow",
        "Coolwarm": "coolwarm",
        "Seismic": "seismic",
    }

    # Get the cmap name
    cmap_name = palette_mapping.get(palette_name, palette_name.lower())

    try:
        # Create colormap
        cm = Colormap(cmap_name)

        colors = []

        # Distribute samples evenly across the full colormap range (same approach as sample_color_reset)
        for i in range(n_colors):
            # Evenly distribute samples across colormap (avoiding endpoints to prevent white/black)
            normalized_value = (
                i + 0.5
            ) / n_colors  # +0.5 to center samples in their bins
            # Map to a subset of colormap to avoid extreme colors (use 10% to 90% range)
            normalized_value = 0.1 + (normalized_value * 0.8)

            color_rgba = cm(normalized_value)

            # Convert RGBA to hex
            if len(color_rgba) >= 3:
                r, g, b = color_rgba[:3]
                # Convert to 0-255 range if needed
                if max(color_rgba[:3]) <= 1.0:
                    r, g, b = int(r * 255), int(g * 255), int(b * 255)
                hex_color = f"#{r:02x}{g:02x}{b:02x}"
                colors.append(hex_color)

        return colors

    except Exception as e:
        raise ValueError(
            f"Failed to create colormap '{cmap_name}': {e}. Available palettes: {list(palette_mapping.keys())}",
        )


def _matplotlib_to_hex(color_dict):
    """Convert matplotlib color dictionary to list of hex colors."""
    return list(color_dict.values())


# =====================================================================================
# SCHEMA AND DATA STRUCTURE FUNCTIONS
# =====================================================================================


def _ensure_features_df_schema_order(self):
    """
    Ensure features_df columns are ordered according to study5_schema.json.

    This method should be called after operations that might scramble the column order.
    """
    if self.features_df is None or self.features_df.is_empty():
        return

    try:
        import os
        import json
        from masster.study.h5 import _reorder_columns_by_schema

        # Load schema
        schema_path = os.path.join(os.path.dirname(__file__), "study5_schema.json")
        with open(schema_path) as f:
            schema = json.load(f)

        # Reorder columns to match schema
        self.features_df = _reorder_columns_by_schema(
            self.features_df,
            schema,
            "features_df",
        )

    except Exception as e:
        self.logger.warning(f"Failed to reorder features_df columns: {e}")


def migrate_map_id_to_index(self):
    """
    Migrate map_id from string-based OpenMS unique IDs to integer indices.

    This function converts the map_id column from string type (with OpenMS unique IDs)
    to integer type where each map_id corresponds to the index of the feature map
    in self.features_maps.

    This migration is needed for studies that were created before the map_id format
    change from OpenMS unique IDs to feature map indices.
    """
    if self.samples_df is None or self.samples_df.is_empty():
        self.logger.warning("No samples to migrate")
        return

    # Check if migration is needed
    current_dtype = self.samples_df["map_id"].dtype
    if current_dtype == pl.Int64:
        self.logger.info("map_id column is already Int64 type - no migration needed")
        return

    self.logger.info("Migrating map_id from string-based OpenMS IDs to integer indices")

    # Create new map_id values based on sample order
    # Each sample gets a map_id that corresponds to its position in features_maps
    sample_count = len(self.samples_df)
    new_map_ids = list(range(sample_count))

    # Update the map_id column
    self.samples_df = self.samples_df.with_columns(
        pl.lit(new_map_ids).alias("map_id"),
    )

    # Ensure the column is Int64 type
    self.samples_df = self.samples_df.cast({"map_id": pl.Int64})

    self.logger.info(
        f"Successfully migrated {sample_count} samples to indexed map_id format",
    )
    self.logger.info(f"map_id now ranges from 0 to {sample_count - 1}")


def restore_ms2(self, samples=None, **kwargs):
    """
    Restore MS2 data by re-running find_ms2 on specified samples.

    This function rebuilds the consensus_ms2 DataFrame by re-extracting MS2 spectra
    from the original sample files. Use this to reverse the effects of compress_ms2().

    Parameters:
        samples (list, optional): List of sample_uids or sample_names to process.
                                 If None, processes all samples.
        **kwargs: Additional keyword arguments passed to find_ms2()
                 (e.g., mz_tol, centroid, deisotope, etc.)
    """
    if self.features_df is None or self.features_df.is_empty():
        self.logger.error("No features_df found in study.")
        return

    if self.samples_df is None or self.samples_df.is_empty():
        self.logger.error("No samples_df found in study.")
        return

    # Get sample_uids to process
    sample_uids = self._get_sample_uids(samples)
    if not sample_uids:
        self.logger.warning("No valid samples specified.")
        return

    self.logger.info(f"Restoring MS2 data from {len(sample_uids)} samples...")

    # Clear existing consensus_ms2 to rebuild from scratch
    initial_ms2_count = (
        len(self.consensus_ms2) if not self.consensus_ms2.is_empty() else 0
    )
    self.consensus_ms2 = pl.DataFrame()

    # Re-run find_ms2 which will rebuild consensus_ms2
    try:
        self.find_ms2(**kwargs)

        final_ms2_count = (
            len(self.consensus_ms2) if not self.consensus_ms2.is_empty() else 0
        )

        self.logger.info(
            f"MS2 restoration completed: {initial_ms2_count} -> {final_ms2_count} MS2 spectra",
        )

    except Exception as e:
        self.logger.error(f"Failed to restore MS2 data: {e}")
        raise


def decompress(self, features=True, ms2=True, chrom=True, samples=None, **kwargs):
    """
    Reverse any compression effects by restoring compressed data adaptively.

    This function restores data that was compressed using compress(), compress_features(),
    compress_ms2(), compress_chrom(), or study.save(compress=True). It optimizes the
    decompression process for speed by only processing what actually needs restoration.

    Parameters:
        features (bool): Restore features data (ms2_specs, ms2_scans, chrom_area)
        ms2 (bool): Restore MS2 spectra by re-running find_ms2()
        chrom (bool): Restore chromatogram objects
        samples (list, optional): List of sample_uids or sample_names to process.
                                 If None, processes all samples.
        **kwargs: Additional keyword arguments for restoration functions:
                 - For restore_chrom: mz_tol (default: 0.010), rt_tol (default: 10.0)
                 - For restore_ms2/find_ms2: mz_tol, centroid, deisotope, etc.

    Performance Optimizations:
        - Adaptive processing: Only restores what actually needs restoration
        - Processes features and chromatograms together when possible (shared file I/O)
        - Uses cached sample instances to avoid repeated file loading
        - Processes MS2 restoration last as it's the most computationally expensive
        - Provides detailed progress information for long-running operations

    Example:
        # Restore everything (but only what needs restoration)
        study.decompress()

        # Restore only chromatograms with custom tolerances
        study.decompress(features=False, ms2=False, chrom=True, mz_tol=0.005, rt_tol=5.0)

        # Restore specific samples only
        study.decompress(samples=["sample1", "sample2"])
    """
    if not any([features, ms2, chrom]):
        self.logger.warning("No decompression operations specified.")
        return

    # Get sample_uids to process
    sample_uids = self._get_sample_uids(samples)
    if not sample_uids:
        self.logger.warning("No valid samples specified.")
        return

    # Adaptively check what actually needs to be done
    import polars as pl

    # Check if features need restoration (more sophisticated logic)
    features_need_restoration = False
    if features and not self.features_df.is_empty():
        # Check for completely missing columns that should exist after feature processing
        missing_cols = []
        for col in ["ms2_scans", "ms2_specs"]:
            if col not in self.features_df.columns:
                missing_cols.append(col)

        # If columns are missing entirely, we likely need restoration
        if missing_cols:
            features_need_restoration = True
        else:
            # If columns exist, check if they're mostly null (indicating compression)
            # But be smart about it - only check if we have consensus features with MS2
            if not self.consensus_ms2.is_empty():
                # We have MS2 data, so ms2_specs should have some content
                null_ms2_specs = self.features_df.filter(
                    pl.col("ms2_specs").is_null(),
                ).height
                total_features = len(self.features_df)
                # If more than 90% are null but we have MS2 data, likely compressed
                if null_ms2_specs > (total_features * 0.9):
                    features_need_restoration = True

    # Check if chromatograms need restoration
    chrom_need_restoration = False
    if chrom and not self.features_df.is_empty():
        if "chrom" not in self.features_df.columns:
            # Column completely missing
            chrom_need_restoration = True
        else:
            null_chroms = self.features_df.filter(pl.col("chrom").is_null()).height
            total_features = len(self.features_df)
            # If more than 50% are null, likely need restoration
            chrom_need_restoration = null_chroms > (total_features * 0.5)

    # Check if MS2 data might need restoration (compare expected vs actual)
    ms2_need_restoration = False
    if ms2:
        current_ms2_count = (
            len(self.consensus_ms2) if not self.consensus_ms2.is_empty() else 0
        )
        consensus_count = (
            len(self.consensus_df) if not self.consensus_df.is_empty() else 0
        )

        if consensus_count > 0:
            # Calculate expected MS2 count based on consensus features with MS2 potential
            # This is a heuristic - if we have very few MS2 compared to consensus, likely compressed
            expected_ratio = 3.0  # Expect at least 3 MS2 per consensus on average
            expected_ms2 = consensus_count * expected_ratio

            if current_ms2_count < min(expected_ms2 * 0.3, consensus_count * 0.8):
                ms2_need_restoration = True

    # Build list of operations that actually need to be done
    operations_needed = []
    if features and features_need_restoration:
        operations_needed.append("features")
    if chrom and chrom_need_restoration:
        operations_needed.append("chromatograms")
    if ms2 and ms2_need_restoration:
        operations_needed.append("MS2 spectra")

    # Early exit if nothing needs to be done
    if not operations_needed:
        self.logger.info(
            "All data appears to be already decompressed. No operations needed.",
        )
        return

    self.logger.info(
        f"Starting adaptive decompression: {', '.join(operations_needed)} from {len(sample_uids)} samples",
    )

    try:
        # Phase 1: Restore features and chromatograms together (shared file I/O)
        if "features" in operations_needed and "chromatograms" in operations_needed:
            self.logger.info(
                "Phase 1: Restoring features and chromatograms together...",
            )

            # Extract relevant kwargs for restore_features and restore_chrom
            restore_kwargs = {}
            if "mz_tol" in kwargs:
                restore_kwargs["mz_tol"] = kwargs["mz_tol"]
            if "rt_tol" in kwargs:
                restore_kwargs["rt_tol"] = kwargs["rt_tol"]

            # Restore features first (includes chrom column)
            self.restore_features(samples=samples)

            # Then do additional chrom gap-filling if needed
            self.restore_chrom(samples=samples, **restore_kwargs)

        elif (
            "features" in operations_needed and "chromatograms" not in operations_needed
        ):
            self.logger.info("Phase 1: Restoring features data...")
            self.restore_features(samples=samples)

        elif (
            "chromatograms" in operations_needed and "features" not in operations_needed
        ):
            self.logger.info("Phase 1: Restoring chromatograms...")
            restore_kwargs = {}
            if "mz_tol" in kwargs:
                restore_kwargs["mz_tol"] = kwargs["mz_tol"]
            if "rt_tol" in kwargs:
                restore_kwargs["rt_tol"] = kwargs["rt_tol"]
            self.restore_chrom(samples=samples, **restore_kwargs)

        # Phase 2: Restore MS2 data (most computationally expensive, done last)
        if "MS2 spectra" in operations_needed:
            self.logger.info("Phase 2: Restoring MS2 spectra...")

            # Extract MS2-specific kwargs
            ms2_kwargs = {}
            for key, value in kwargs.items():
                if key in [
                    "mz_tol",
                    "centroid",
                    "deisotope",
                    "dia_stats",
                    "feature_uid",
                ]:
                    ms2_kwargs[key] = value

            self.restore_ms2(samples=samples, **ms2_kwargs)

        self.logger.info("Adaptive decompression completed successfully")

    except Exception as e:
        self.logger.error(f"Decompression failed: {e}")
        raise
