from __future__ import annotations

import polars as pl


# Parameters removed - using hardcoded defaults


def _estimate_memory_usage(self):
    """
    Estimate the memory usage of all dataframes in the Sample object.

    Returns:
        dict: A dictionary containing memory usage estimates for each dataframe
              and the total memory usage in bytes and MB.
    """
    memory_usage = {}
    total_bytes = 0

    # Check features_df
    if self.features_df is not None and len(self.features_df) > 0:
        features_bytes = self.features_df.estimated_size()
        memory_usage["features_df"] = {
            "rows": len(self.features_df),
            "columns": len(self.features_df.columns),
            "bytes": features_bytes,
            "mb": features_bytes / (1024 * 1024),
        }
        total_bytes += features_bytes
    else:
        memory_usage["features_df"] = {"rows": 0, "columns": 0, "bytes": 0, "mb": 0}

    # Check scans_df
    if self.scans_df is not None and len(self.scans_df) > 0:
        scans_bytes = self.scans_df.estimated_size()
        memory_usage["scans_df"] = {
            "rows": len(self.scans_df),
            "columns": len(self.scans_df.columns),
            "bytes": scans_bytes,
            "mb": scans_bytes / (1024 * 1024),
        }
        total_bytes += scans_bytes
    else:
        memory_usage["scans_df"] = {"rows": 0, "columns": 0, "bytes": 0, "mb": 0}

    # Check ms1_df
    if self.ms1_df is not None and len(self.ms1_df) > 0:
        ms1_bytes = self.ms1_df.estimated_size()
        memory_usage["ms1_df"] = {
            "rows": len(self.ms1_df),
            "columns": len(self.ms1_df.columns),
            "bytes": ms1_bytes,
            "mb": ms1_bytes / (1024 * 1024),
        }
        total_bytes += ms1_bytes
    else:
        memory_usage["ms1_df"] = {"rows": 0, "columns": 0, "bytes": 0, "mb": 0}

    # Check chrom_df
    if self.chrom_df is not None and len(self.chrom_df) > 0:
        chrom_bytes = self.chrom_df.estimated_size()
        memory_usage["chrom_df"] = {
            "rows": len(self.chrom_df),
            "columns": len(self.chrom_df.columns),
            "bytes": chrom_bytes,
            "mb": chrom_bytes / (1024 * 1024),
        }
        total_bytes += chrom_bytes
    else:
        memory_usage["chrom_df"] = {"rows": 0, "columns": 0, "bytes": 0, "mb": 0}

    # Add total memory usage
    memory_usage["total"] = {
        "bytes": total_bytes,
        "mb": total_bytes / (1024 * 1024),
        "gb": total_bytes / (1024 * 1024 * 1024),
    }

    # Log the memory usage summary
    if hasattr(self, "logger"):
        self.logger.debug(
            f"Total DataFrame memory usage: {memory_usage['total']['mb']:.2f} MB",
        )
        for df_name, stats in memory_usage.items():
            if df_name != "total" and stats["bytes"] > 0:
                self.logger.debug(
                    f"{df_name}: {stats['rows']} rows, {stats['mb']:.2f} MB",
                )

    return memory_usage["total"]["mb"]


def get_dda_stats(self):
    # filter self.scans_df with mslevel 1
    ms1 = self.scans_df.filter(pl.col("ms_level") == 1)
    return ms1


def get_feature(self, feature_uid):
    # get the feature with feature_uid == feature_uid
    feature = self.features_df.filter(pl.col("feature_uid") == feature_uid)
    if len(feature) == 0:
        self.logger.warning(f"Feature {feature_uid} not found.")
        return None
    else:
        return feature.row(0, named=True)


def _get_scan_uids(self, scans=None, verbose=True):
    scans_uids = []
    if scans is None:
        # fromuids scan all get_dfans
        scans_uids = self.scans_df.get_column("scan_uid").to_list()
    elif isinstance(scans, list):
        # if scans is a list, ensure all elements are valid scan_uids
        scans_uids = [
            s for s in scans if s in self.scans_df.get_column("scan_uid").to_list()
        ]
        if verbose and not scans_uids:
            self.logger.error("No valid scan_uids provided.")

    return scans_uids


def _get_feature_uids(self, features=None, verbose=True):
    """
    Get feature UIDs from various input types.

    Parameters:
        features: Can be one of the following:
            - None: Returns all feature UIDs from self.features_df
            - list: Returns the list if all elements are valid feature UIDs
            - polars.DataFrame: Extracts unique values from 'feature_uid' or 'feature_id' column
            - pandas.DataFrame: Extracts unique values from 'feature_uid' or 'feature_id' column
        verbose (bool): Whether to log errors for invalid inputs

    Returns:
        list: List of feature UIDs
    """
    if features is None:
        # Get all feature UIDs from self.features_df
        if self.features_df is None:
            if verbose:
                self.logger.warning("No features_df available.")
            return []
        feature_uids = self.features_df.get_column("feature_uid").to_list()
    elif isinstance(features, list):
        # If features is a list, ensure all elements are valid feature_uids
        if self.features_df is None:
            if verbose:
                self.logger.warning(
                    "No features_df available to validate feature UIDs.",
                )
            return []

        valid_feature_uids = self.features_df.get_column("feature_uid").to_list()
        feature_uids = [f for f in features if f in valid_feature_uids]
        if verbose and not feature_uids:
            self.logger.error("No valid feature_uids provided.")
    else:
        # Handle polars and pandas DataFrames
        try:
            # Check if it's a polars DataFrame
            if hasattr(features, "columns") and hasattr(features, "get_column"):
                # Polars DataFrame
                feature_column = None
                if "feature_uid" in features.columns:
                    feature_column = "feature_uid"
                elif "feature_id" in features.columns:
                    feature_column = "feature_id"

                if feature_column is None:
                    if verbose:
                        self.logger.error(
                            "No 'feature_uid' or 'feature_id' column found in polars DataFrame.",
                        )
                    return []

                # Get unique values from the column
                feature_uids = features.get_column(feature_column).unique().to_list()

            # Check if it's a pandas DataFrame
            elif hasattr(features, "columns") and hasattr(features, "iloc"):
                # Pandas DataFrame
                import pandas as pd

                if not isinstance(features, pd.DataFrame):
                    if verbose:
                        self.logger.error(
                            "Invalid input type. Expected None, list, polars DataFrame, or pandas DataFrame.",
                        )
                    return []

                feature_column = None
                if "feature_uid" in features.columns:
                    feature_column = "feature_uid"
                elif "feature_id" in features.columns:
                    feature_column = "feature_id"

                if feature_column is None:
                    if verbose:
                        self.logger.error(
                            "No 'feature_uid' or 'feature_id' column found in pandas DataFrame.",
                        )
                    return []

                # Get unique values from the column
                feature_uids = features[feature_column].unique().tolist()

            else:
                if verbose:
                    self.logger.error(
                        "Invalid input type. Expected None, list, polars DataFrame, or pandas DataFrame.",
                    )
                return []

        except Exception as e:
            if verbose:
                self.logger.error(f"Error processing DataFrame input: {e}")
            return []

    return feature_uids


def get_scan(self, scans: list | None = None, verbose=True):
    scan_uids = self._get_scan_uids(scans, verbose=False)
    if not scan_uids:
        if verbose:
            self.logger.warning("No valid scan_uids provided.")
        return None

    scan = self.scans_df.filter(pl.col("scan_uid").is_in(scan_uids))
    return scan


def select_closest_scan(
    self,
    rt,
    prec_mz=None,
    mz_tol=0.01,
):
    """
    Select the closest scan based on retention time (rt), applying additional filtering on precursor m/z (prec_mz) if provided.
    Parameters:
        rt (float): The target retention time to find the closest scan.
        prec_mz (float, optional): The precursor m/z value used to filter scans. If given, only scans with ms_level 2 are considered
                                    and filtered to include only those within mz_tol of prec_mz.
        mz_tol (float, optional): The tolerance to apply when filtering scans by precursor m/z. Defaults to 0.01.
    Returns:
        polars.DataFrame or None: A DataFrame slice containing the closest scan if a matching scan is found;
                                  otherwise, returns None.
    Notes:
        - If the scans_df attribute is None, the function prints an error message and returns None.
        - When prec_mz is provided, it filters scans where ms_level equals 2 and the precursor m/z is within the given mz_tol range.
        - If prec_mz is not provided, scans with ms_level equal to 1 are considered.
        - The function calculates the absolute difference between each scan's rt and the given rt, sorting the scans by this difference.
        - If no scans match the criteria, an error message is printed before returning None.
    """
    # check if scans_df is None
    if self.scans_df is None:
        self.logger.warning("No scans found.")
        return None
    if prec_mz is not None:
        ms_level = 2
        scans = self.scans_df.filter(pl.col("ms_level") == ms_level)
        # find all scans with prec_mz within mz_tol of prec_mz
        scans = scans.filter(pl.col("prec_mz") > prec_mz - mz_tol)
        scans = scans.filter(pl.col("prec_mz") < prec_mz + mz_tol)
        # sort by distance to rt
        scans = scans.with_columns((pl.col("rt") - rt).abs().alias("rt_diff"))
        scans = scans.sort("rt_diff")
        # return the closest scan
        if len(scans) > 0:
            scan = scans.slice(0, 1)
        else:
            self.logger.warning(
                f"No scans found with prec_mz {prec_mz} within {mz_tol} of rt {rt}.",
            )
            return None
    else:
        mslevel = 1
        scans = self.scans_df.filter(pl.col("ms_level") == mslevel)
        # sort by distance to rt
        scans = scans.with_columns((pl.col("rt") - rt).abs().alias("rt_diff"))
        scans = scans.sort("rt_diff")
        # return the closest scan
        if len(scans) > 0:
            scan = scans.slice(0, 1)
        else:
            self.logger.warning(
                f"No scans found with ms_level {mslevel} within {mz_tol} of rt {rt}.",
            )
            return None
    # return scans_df slice

    return scan


def get_eic(self, mz, mz_tol=None):
    """
    Extract an extracted ion chromatogram (EIC) from `ms1_df` for a target m/z ± mz_tol.

    The function filters `self.ms1_df` for rows with `mz` within the tolerance, aggregates
    intensities per retention time (summing intensities for the same `rt`), sorts by `rt`,
    stores the resulting chromatogram in `self.chrom_df` and returns it.

    Parameters:
        mz (float): target m/z value
        mz_tol (float): tolerance around mz. If None, uses self.parameters.eic_mz_tol or defaults to 0.01

    Returns:
        polars.DataFrame or None: chromatogram with columns ['rt', 'inty'] or None if not available
    """
    # Use default mz_tol from sample parameters if not provided
    if mz_tol is None:
        if hasattr(self, "parameters") and hasattr(self.parameters, "eic_mz_tol"):
            mz_tol = self.parameters.eic_mz_tol
        else:
            mz_tol = 0.01  # fallback default

    # Validate ms1_df
    if not hasattr(self, "ms1_df") or self.ms1_df is None:
        if hasattr(self, "logger"):
            self.logger.warning("No ms1_df available to build EIC.")
        return None

    try:
        # Filter by mz window
        mz_min = mz - mz_tol
        mz_max = mz + mz_tol
        matches = self.ms1_df.filter(
            (pl.col("mz") >= mz_min) & (pl.col("mz") <= mz_max),
        )

        if len(matches) == 0:
            if hasattr(self, "logger"):
                self.logger.debug(f"No ms1 points found for mz={mz} ± {mz_tol}.")
            # ensure chrom_df is None when nothing found
            self.chrom_df = None
            return None

        # Aggregate intensities per retention time. Use sum in case multiple points per rt.
        chrom = (
            matches.group_by("rt").agg([pl.col("inty").sum().alias("inty")]).sort("rt")
        )

        # Attach to Sample
        self.chrom_df = chrom

        if hasattr(self, "logger"):
            self.logger.debug(f"Built EIC for mz={mz} ± {mz_tol}: {len(chrom)} points.")

        return chrom

    except Exception as e:
        if hasattr(self, "logger"):
            self.logger.error(f"Error building EIC for mz={mz}: {e}")
        return None


def select(
    self,
    mz=None,
    rt=None,
    coherence=None,
    inty=None,
    rt_delta=None,
    iso=None,
    iso_of=None,
    has_MS2=None,
    prominence_scaled=None,
    height_scaled=None,
    prominence=None,
    height=None,
):
    """
    Select features based on specified criteria and return the filtered DataFrame.

    Parameters:
        mz: m/z range filter (tuple for range, single value for minimum)
        rt: retention time range filter (tuple for range, single value for minimum)
        coherence: chromatogram coherence filter (tuple for range, single value for minimum)
        inty: intensity filter (tuple for range, single value for minimum)
        rt_delta: retention time delta filter (tuple for range, single value for minimum)
        iso: isotope number filter (tuple for range, single value for exact match)
        iso_of: isotope parent filter (tuple for range, single value for exact match)
        has_MS2: filter for features with/without MS2 spectra (bool)
        prominence_scaled: scaled prominence filter (tuple for range, single value for minimum)
        height_scaled: scaled height filter (tuple for range, single value for minimum)
        prominence: prominence filter (tuple for range, single value for minimum)
        height: height filter (tuple for range, single value for minimum)

    Returns:
        polars.DataFrame: Filtered features DataFrame
    """
    # remove all features with coherence < coherence
    if self.features_df is None:
        # self.logger.info("No features found. R")
        return
    feats = self.features_df.clone()
    if coherence is not None:
        has_coherence = "chrom_coherence" in self.features_df.columns
        if not has_coherence:
            self.logger.warning("No coherence data found in features.")
        else:
            # record len for logging
            feats_len_before_filter = len(feats)
            if isinstance(coherence, tuple) and len(coherence) == 2:
                min_coherence, max_coherence = coherence
                feats = feats.filter(
                    (pl.col("chrom_coherence") >= min_coherence)
                    & (pl.col("chrom_coherence") <= max_coherence),
                )
            else:
                feats = feats.filter(pl.col("chrom_coherence") >= coherence)
            self.logger.debug(
                f"Selected features by coherence. Features removed: {feats_len_before_filter - len(feats)}",
            )

    if mz is not None:
        feats_len_before_filter = len(feats)
        if isinstance(mz, tuple) and len(mz) == 2:
            min_mz, max_mz = mz
            feats = feats.filter((pl.col("mz") >= min_mz) & (pl.col("mz") <= max_mz))
        else:
            feats = feats.filter(pl.col("mz") >= mz)
        self.logger.debug(
            f"Selected features by mz. Features removed: {feats_len_before_filter - len(feats)}",
        )

    if rt is not None:
        feats_len_before_filter = len(feats)
        if isinstance(rt, tuple) and len(rt) == 2:
            min_rt, max_rt = rt
            feats = feats.filter((pl.col("rt") >= min_rt) & (pl.col("rt") <= max_rt))
        else:
            feats = feats.filter(pl.col("rt") >= rt)
        self.logger.debug(
            f"Selected features by rt. Features removed: {feats_len_before_filter - len(feats)}",
        )

    if inty is not None:
        feats_len_before_filter = len(feats)
        if isinstance(inty, tuple) and len(inty) == 2:
            min_inty, max_inty = inty
            feats = feats.filter(
                (pl.col("inty") >= min_inty) & (pl.col("inty") <= max_inty),
            )
        else:
            feats = feats.filter(pl.col("inty") >= inty)
        self.logger.debug(
            f"Selected features by intensity. Features removed: {feats_len_before_filter - len(feats)}",
        )

    if rt_delta is not None:
        feats_len_before_filter = len(feats)
        if "rt_delta" not in feats.columns:
            self.logger.warning("No rt_delta data found in features.")
            return
        if isinstance(rt_delta, tuple) and len(rt_delta) == 2:
            min_rt_delta, max_rt_delta = rt_delta
            feats = feats.filter(
                (pl.col("rt_delta") >= min_rt_delta)
                & (pl.col("rt_delta") <= max_rt_delta),
            )
        else:
            feats = feats.filter(pl.col("rt_delta") >= rt_delta)
        self.logger.debug(
            f"Selected features by rt_delta. Features removed: {feats_len_before_filter - len(feats)}",
        )

    if iso is not None:
        feats_len_before_filter = len(feats)
        if isinstance(iso, tuple) and len(iso) == 2:
            min_iso, max_iso = iso
            feats = feats.filter(
                (pl.col("iso") >= min_iso) & (pl.col("iso") <= max_iso),
            )
        else:
            feats = feats.filter(pl.col("iso") == iso)
        self.logger.debug(
            f"Selected features by iso. Features removed: {feats_len_before_filter - len(feats)}",
        )

    if iso_of is not None:
        feats_len_before_filter = len(feats)
        if isinstance(iso_of, tuple) and len(iso_of) == 2:
            min_iso_of, max_iso_of = iso_of
            feats = feats.filter(
                (pl.col("iso_of") >= min_iso_of) & (pl.col("iso_of") <= max_iso_of),
            )
        else:
            feats = feats.filter(pl.col("iso_of") == iso_of)
        self.logger.debug(
            f"Selected features by iso_of. Features removed: {feats_len_before_filter - len(feats)}",
        )

    if has_MS2 is not None:
        feats_len_before_filter = len(feats)
        if has_MS2:
            feats = feats.filter(pl.col("ms2_scans").is_not_null())
        else:
            feats = feats.filter(pl.col("ms2_scans").is_null())
        self.logger.debug(
            f"Selected features by MS2 presence. Features removed: {feats_len_before_filter - len(feats)}",
        )

    if prominence_scaled is not None:
        feats_len_before_filter = len(feats)
        if isinstance(prominence_scaled, tuple) and len(prominence_scaled) == 2:
            min_prominence_scaled, max_prominence_scaled = prominence_scaled
            feats = feats.filter(
                (pl.col("chrom_prominence_scaled") >= min_prominence_scaled)
                & (pl.col("chrom_prominence_scaled") <= max_prominence_scaled),
            )
        else:
            feats = feats.filter(pl.col("chrom_prominence_scaled") >= prominence_scaled)
        self.logger.debug(
            f"Selected features by prominence_scaled. Features removed: {feats_len_before_filter - len(feats)}",
        )

    if height_scaled is not None:
        feats_len_before_filter = len(feats)
        if isinstance(height_scaled, tuple) and len(height_scaled) == 2:
            min_height_scaled, max_height_scaled = height_scaled
            feats = feats.filter(
                (pl.col("chrom_height_scaled") >= min_height_scaled)
                & (pl.col("chrom_height_scaled") <= max_height_scaled),
            )
        else:
            feats = feats.filter(pl.col("chrom_height_scaled") >= height_scaled)
        self.logger.debug(
            f"Selected features by height_scaled. Features removed: {feats_len_before_filter - len(feats)}",
        )

    if prominence is not None:
        feats_len_before_filter = len(feats)
        if isinstance(prominence, tuple) and len(prominence) == 2:
            min_prominence, max_prominence = prominence
            feats = feats.filter(
                (pl.col("chrom_prominence") >= min_prominence)
                & (pl.col("chrom_prominence") <= max_prominence),
            )
        else:
            feats = feats.filter(pl.col("chrom_prominence") >= prominence)
        self.logger.debug(
            f"Selected features by prominence. Features removed: {feats_len_before_filter - len(feats)}",
        )

    if height is not None:
        feats_len_before_filter = len(feats)
        # Check if chrom_height column exists, if not use chrom_height_scaled
        height_col = (
            "chrom_height" if "chrom_height" in feats.columns else "chrom_height_scaled"
        )
        if isinstance(height, tuple) and len(height) == 2:
            min_height, max_height = height
            feats = feats.filter(
                (pl.col(height_col) >= min_height) & (pl.col(height_col) <= max_height),
            )
        else:
            feats = feats.filter(pl.col(height_col) >= height)
        self.logger.debug(
            f"Selected features by {height_col}. Features removed: {feats_len_before_filter - len(feats)}",
        )
    if len(feats) == 0:
        self.logger.warning("No features remaining after applying selection criteria.")
    else:
        self.logger.info(f"Selected features. Features remaining: {len(feats)}")
    return feats


def _features_sync(self):
    """
    Synchronizes the cached FeatureMap with features_df.

    This ensures that the cached FeatureMap (_oms_features_map) contains only features
    that exist in both the FeatureMap and the features_df. This is important
    after operations that modify features_df but not the FeatureMap (like filtering).

    Side Effects:
        Updates self._oms_features_map and self.features_df to contain only common features.
        Logs information about removed features.
    """
    if self.features_df is None or len(self.features_df) == 0:
        self.logger.debug("No features_df to synchronize")
        if hasattr(self, "_oms_features_map"):
            self._oms_features_map = None
        return

    # Check if we have a cached feature map
    if not hasattr(self, "_oms_features_map") or self._oms_features_map is None:
        self.logger.debug("No cached feature map to synchronize")
        return

    try:
        import pyopenms as oms
    except ImportError:
        self.logger.warning("PyOpenMS not available, cannot sync FeatureMap")
        return

    try:
        # Get feature IDs from both sources
        if "feature_id" in self.features_df.columns:
            df_feature_ids = set(
                self.features_df.get_column("feature_id").cast(str).to_list(),
            )
        else:
            self.logger.warning(
                "No feature_id column in features_df, cannot synchronize",
            )
            return

        # Get feature IDs from FeatureMap
        feature_map_ids = set()
        for i in range(self._oms_features_map.size()):
            feature = self._oms_features_map[i]
            unique_id = str(
                feature.getUniqueId(),
            )  # Convert to string to match DataFrame
            feature_map_ids.add(unique_id)

        # Find features that exist in both
        common_feature_ids = df_feature_ids & feature_map_ids

        # Safety check: log error and exit if no features are matching
        if not common_feature_ids:
            self.logger.error(
                f"No matching features found between FeatureMap and features_df. "
                f"FeatureMap has {len(feature_map_ids)} features, "
                f"features_df has {len(df_feature_ids)} features. "
                f"Cannot synchronize - this indicates a data inconsistency. Exiting without changes.",
            )
            return

        # Create new synchronized FeatureMap with only common features
        synced_feature_map = oms.FeatureMap()
        for i in range(self._oms_features_map.size()):
            feature = self._oms_features_map[i]
            unique_id = str(feature.getUniqueId())
            if unique_id in common_feature_ids:
                synced_feature_map.push_back(feature)

        # Filter features_df to only include features that exist in FeatureMap
        synced_features_df = self.features_df.filter(
            pl.col("feature_id").is_in(list(common_feature_ids)),
        )

        # Update the objects
        original_map_size = self._oms_features_map.size()
        original_df_size = len(self.features_df)

        self._oms_features_map = synced_feature_map
        self.features_df = synced_features_df

        # Log the synchronization results
        map_removed = original_map_size - self._oms_features_map.size()
        df_removed = original_df_size - len(self.features_df)

        # only log if features were removed
        if map_removed > 0 or df_removed > 0:
            self.logger.debug(
                f"Features synchronized. FeatureMap: {original_map_size} -> {self._oms_features_map.size()} "
                f"({map_removed} removed), DataFrame: {original_df_size} -> {len(self.features_df)} "
                f"({df_removed} removed)",
            )
        else:
            self.logger.debug(
                f"Features synchronized. FeatureMap: {original_map_size} -> {self._oms_features_map.size()} "
                f"({map_removed} removed), DataFrame: {original_df_size} -> {len(self.features_df)} "
                f"({df_removed} removed)",
            )

    except ImportError:
        self.logger.warning("PyOpenMS not available, cannot sync FeatureMap")
    except Exception as e:
        self.logger.error(f"Error during feature synchronization: {e}")


def features_delete(self, features: list | None = None):
    """
    Delete features from both self.features_df and self._oms_features_map based on a list of feature UIDs.

    Parameters:
        features (list, optional): List of feature UIDs to delete. If None, all features will be deleted.

    Returns:
        None

    Side Effects:
        Updates self.features_df by removing specified features.
        Updates self._oms_features_map (OpenMS FeatureMap) by creating a new FeatureMap with only the remaining features.
        Updates self.scans_df by removing feature_uid associations for deleted features.

    Note:
        The function preserves all OpenMS FeatureMap information by creating a new FeatureMap
        containing only the features that should remain after deletion.
    """
    if self.features_df is None:
        self.logger.warning("No features found.")
        return

    # Get the feature UIDs to delete
    feature_uids_to_delete = self._get_feature_uids(features=features, verbose=True)

    if not feature_uids_to_delete:
        self.logger.warning("No valid feature UIDs provided for deletion.")
        return

    original_count = len(self.features_df)

    # Update features_df by filtering out the features to delete
    self.features_df = self.features_df.filter(
        ~pl.col("feature_uid").is_in(feature_uids_to_delete),
    )

    # Update the OpenMS FeatureMap by creating a new one with only features to keep
    if hasattr(self, "_oms_features_map") and self._oms_features_map is not None:
        try:
            # Import pyopenms
            import pyopenms as oms

            # Create new FeatureMap with only features to keep
            filtered_map = oms.FeatureMap()

            # Get the feature UIDs that should remain after deletion
            remaining_feature_uids = self.features_df.get_column(
                "feature_uid",
            ).to_list()

            # Iterate through existing features and keep only those not in deletion list
            for i in range(self._oms_features_map.size()):
                feature = self._oms_features_map[i]
                # Since feature UIDs in DataFrame are sequential (0, 1, 2, ...) and correspond to indices
                # we can check if the current index is in the remaining UIDs
                if i in remaining_feature_uids:
                    filtered_map.push_back(feature)

            # Replace the original FeatureMap with the filtered one
            self._oms_features_map = filtered_map
            self.logger.debug(
                f"OpenMS FeatureMap updated with {filtered_map.size()} remaining features.",
            )

        except ImportError:
            self.logger.warning("PyOpenMS not available, only updating features_df")
        except Exception as e:
            self.logger.warning(
                f"Could not update OpenMS FeatureMap: {e}. FeatureMap may be out of sync.",
            )

    # Update scans_df to remove feature_uid associations for deleted features
    if hasattr(self, "scans_df") and self.scans_df is not None:
        self.scans_df = self.scans_df.with_columns(
            pl.when(pl.col("feature_uid").is_in(feature_uids_to_delete))
            .then(None)
            .otherwise(pl.col("feature_uid"))
            .alias("feature_uid"),
        )

    deleted_count = original_count - len(self.features_df)
    self.logger.info(
        f"Deleted {deleted_count} features. Remaining features: {len(self.features_df)}",
    )


def _delete_ms2(self):
    """
    Unlinks MS2 spectra from features in the dataset.
    This method removes the association between MS2 spectra and features in the features dataframe by setting
    the 'ms2_scans' and 'ms2_specs' columns to None. It also updates the scans dataframe to remove the feature
    id (feature_uid) association for the linked MS2 spectra.
    Parameters:
    Returns:
        None
    Side Effects:
        Updates self.features_df by setting 'ms2_scans' and 'ms2_specs' columns to None. Also, updates self.scans_df
        by resetting the 'feature_uid' column for linked MS2 spectra.
    """
    if self.features_df is None:
        # self.logger.warning("No features found.")
        return

    self.logger.debug("Unlinking MS2 spectra from features...")

    # Set ms2_scans and ms2_specs to None using Polars syntax
    self.features_df = self.features_df.with_columns(
        [
            pl.lit(None).alias("ms2_scans"),
            pl.lit(None).alias("ms2_specs"),
        ],
    )

    # Update scans_df to remove feature_uid association for linked MS2 spectra
    self.scans_df = self.scans_df.with_columns(
        pl.when(pl.col("ms_level") == 2)
        .then(None)
        .otherwise(pl.col("feature_uid"))
        .alias("feature_uid"),
    )
    self.logger.info("MS2 spectra unlinked from features.")


def features_filter(self, features):
    """
    Keep only the specified features and delete all others. This is the opposite of features_delete().

    Parameters:
        features: Can be one of the following:
            - list: List of feature UIDs to keep
            - polars.DataFrame: DataFrame with 'feature_uid' or 'feature_id' column - extracts unique values to keep
            - pandas.DataFrame: DataFrame with 'feature_uid' or 'feature_id' column - extracts unique values to keep

    Returns:
        None

    Side Effects:
        Updates self.features_df by keeping only the specified features.
        Updates self._oms_features_map (OpenMS FeatureMap) by creating a new FeatureMap with only the specified features.
        Updates self.scans_df by removing feature_uid associations for deleted features.

    Note:
        The function preserves all OpenMS FeatureMap information by creating a new FeatureMap
        containing only the features that should be kept.
    """
    if self.features_df is None:
        self.logger.warning("No features found.")
        return

    if features is None:
        self.logger.warning(
            "No features specified to keep. Use features_delete() to delete all features.",
        )
        return

    # Get the feature UIDs to keep
    feature_uids_to_keep = self._get_feature_uids(features=features, verbose=True)

    if not feature_uids_to_keep:
        self.logger.warning("No valid feature UIDs provided to keep.")
        return

    original_count = len(self.features_df)

    # Update features_df by keeping only the specified features
    self.features_df = self.features_df.filter(
        pl.col("feature_uid").is_in(feature_uids_to_keep),
    )

    # Calculate which features were deleted (all except the ones to keep)
    all_feature_uids = set(range(original_count))  # Assuming sequential UIDs
    feature_uids_to_delete = list(all_feature_uids - set(feature_uids_to_keep))

    # Update the OpenMS FeatureMap by creating a new one with only features to keep
    if hasattr(self, "_oms_features_map") and self._oms_features_map is not None:
        try:
            # Import pyopenms
            import pyopenms as oms

            # Create new FeatureMap with only features to keep
            filtered_map = oms.FeatureMap()

            # Iterate through existing features and keep only those in the keep list
            for i in range(self._oms_features_map.size()):
                feature = self._oms_features_map[i]
                # Since feature UIDs in DataFrame are sequential (0, 1, 2, ...) and correspond to indices
                # we can check if the current index is in the keep UIDs
                if i in feature_uids_to_keep:
                    filtered_map.push_back(feature)

            # Replace the original FeatureMap with the filtered one
            self._oms_features_map = filtered_map
            self.logger.debug(
                f"OpenMS FeatureMap updated with {filtered_map.size()} remaining features.",
            )

        except ImportError:
            self.logger.warning("PyOpenMS not available, only updating features_df")
        except Exception as e:
            self.logger.warning(
                f"Could not update OpenMS FeatureMap: {e}. FeatureMap may be out of sync.",
            )

    # Update scans_df to remove feature_uid associations for deleted features
    if (
        hasattr(self, "scans_df")
        and self.scans_df is not None
        and feature_uids_to_delete
    ):
        self.scans_df = self.scans_df.with_columns(
            pl.when(pl.col("feature_uid").is_in(feature_uids_to_delete))
            .then(None)
            .otherwise(pl.col("feature_uid"))
            .alias("feature_uid"),
        )

    kept_count = len(self.features_df)
    deleted_count = original_count - kept_count
    self.logger.info(
        f"Kept {kept_count} features, deleted {deleted_count} features. Remaining features: {kept_count}",
    )


def set_source(self, filename):
    """
    Reassign file_source. If filename contains only a path, keep the current basename
    and build an absolute path. Check that the new file exists before overwriting
    the old file_source.

    Parameters:
        filename (str): New file path or directory path

    Returns:
        None
    """
    import os

    # Store the old file_source for logging
    old_file_source = getattr(self, "file_source", None)

    # Check if filename is just a directory path
    if os.path.isdir(filename):
        if old_file_source is None:
            self.logger.error("Cannot build path: no current file_source available")
            return

        # Get the basename from current file_source
        current_basename = os.path.basename(old_file_source)
        # Build new absolute path
        new_file_path = os.path.join(filename, current_basename)
    else:
        # filename is a full path, make it absolute
        new_file_path = os.path.abspath(filename)

    # Check if the new file exists
    if not os.path.exists(new_file_path):
        self.logger.error(f"File does not exist: {new_file_path}")
        return

    # Update file_source
    self.file_source = new_file_path

    # Log the change
    if old_file_source is not None:
        self.logger.info(
            f"Updated file_source from {old_file_source} to {self.file_source}",
        )
    else:
        self.logger.info(f"Set file_source to {self.file_source}")


def _recreate_feature_map(self):
    """
    Recreate OpenMS FeatureMap from features_df.

    This helper function creates a new OpenMS FeatureMap using the data from features_df.
    This allows us to avoid storing and loading featureXML files by default, while still
    being able to recreate the feature map when needed for OpenMS operations like
    find_features() or saving to featureXML format.

    Returns:
        oms.FeatureMap: A new FeatureMap with features from features_df, or None if no features

    Side Effects:
        Caches the created feature map in self._oms_features_map for reuse
    """
    if self.features_df is None or len(self.features_df) == 0:
        self.logger.debug("No features_df available to recreate feature map")
        return None

    try:
        import pyopenms as oms
    except ImportError:
        self.logger.warning("PyOpenMS not available, cannot recreate feature map")
        return None

    # Create new FeatureMap
    feature_map = oms.FeatureMap()

    # Set the primary MS run path if available
    if hasattr(self, "file_path") and self.file_path:
        feature_map.setPrimaryMSRunPath([self.file_path.encode()])

    # Convert DataFrame features to OpenMS Features
    for i, feature_row in enumerate(self.features_df.iter_rows(named=True)):
        feature = oms.Feature()

        # Set basic properties from DataFrame (handle missing values gracefully)
        try:
            if feature_row.get("feature_id") is not None:
                feature.setUniqueId(int(feature_row["feature_id"]))
            else:
                feature.setUniqueId(i)  # Use index as fallback

            if feature_row.get("mz") is not None:
                feature.setMZ(float(feature_row["mz"]))
            if feature_row.get("rt") is not None:
                feature.setRT(float(feature_row["rt"]))
            if feature_row.get("inty") is not None:
                feature.setIntensity(float(feature_row["inty"]))
            if feature_row.get("quality") is not None:
                feature.setOverallQuality(float(feature_row["quality"]))
            if feature_row.get("charge") is not None:
                feature.setCharge(int(feature_row["charge"]))

            # Add to feature map
            feature_map.push_back(feature)

        except (ValueError, TypeError) as e:
            self.logger.warning(f"Skipping feature due to conversion error: {e}")
            continue

    # Ensure unique IDs
    feature_map.ensureUniqueId()

    # Cache the feature map
    self._oms_features_map = feature_map

    self.logger.debug(
        f"Recreated FeatureMap with {feature_map.size()} features from features_df",
    )
    return feature_map


def _get_feature_map(self):
    """
    Get the OpenMS FeatureMap, creating it from features_df if needed.

    This property-like method returns the cached feature map if available,
    or recreates it from features_df if not. This allows lazy loading of
    feature maps only when needed for OpenMS operations.

    Returns:
        oms.FeatureMap or None: The feature map, or None if not available
    """
    # Return cached feature map if available
    if hasattr(self, "_oms_features_map") and self._oms_features_map is not None:
        return self._oms_features_map

    # Otherwise recreate from features_df
    return self._recreate_feature_map()
