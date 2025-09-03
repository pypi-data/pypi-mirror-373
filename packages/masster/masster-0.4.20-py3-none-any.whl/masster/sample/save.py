"""
_export.py

This module provides data export functionality for mass spectrometry analysis results.
It handles saving processed data in various formats for downstream analysis, sharing,
and archival purposes, including spectrum files, feature tables, and custom formats.

Key Features:
- **Multi-Format Export**: Save data as MGF, mzML, CSV, FeatureXML, and custom formats.
- **Spectrum Export**: Export MS/MS spectra for database searching and identification.
- **Feature Export**: Save detected features with quantitative information.
- **Custom Formats**: Support for compressed pickle formats (mzpkl) for fast storage.
- **Metadata Preservation**: Maintain acquisition parameters and processing history.
- **Batch Export**: Export multiple samples or studies simultaneously.

Dependencies:
- `pyopenms`: For standard mass spectrometry file format export.
- `polars` and `pandas`: For tabular data export and manipulation.
- `numpy`: For numerical array operations.
- `pickle` and `bz2`: For custom format compression and serialization.
- `loguru`: For logging export operations and error handling.

Functions:
- `save()`: Main export function with format detection.
- `save_mzpkl()`: Export to compressed pickle format for fast loading.
- `save_featureXML()`: Export features in OpenMS FeatureXML format.
- `export_mgf()`: Export MS/MS spectra in MGF format for database searching.
- `export_csv()`: Export features and metadata in CSV format.

Supported Export Formats:
- MGF (Mascot Generic Format) for MS/MS spectra
- mzML (open standard format) for spectral data
- CSV for tabular feature data
- FeatureXML (OpenMS format) for feature data
- mzpkl (custom compressed format) for complete analysis results

Example Usage:
```python
from _export import save, export_mgf

# Save complete analysis in custom format
save(self, filename="analysis_results.mzpkl")

# Export MS/MS spectra for database searching
export_mgf(self, filename="ms2_spectra.mgf", export_type="all")

# Export feature table
export_csv(self, filename="features.csv", data_type="features")
```

See Also:
- `parameters._export_parameters`: For export-specific parameter configuration.
- `_import.py`: For data import functionality.
- `single.py`: For using export methods with ddafile class.

"""

import os

from datetime import datetime

import numpy as np
import pandas as pd
import polars as pl
import pyopenms as oms

from tqdm import tqdm

# Parameters removed - using hardcoded defaults
from masster.spectrum import combine_peaks


def save(self, filename=None):
    """
    Save the current object to a file in the '.sample5' format.

    If `filename` is not provided, the method attempts to use `self.file_path` as the base name,
    replacing its extension with '.sample5'. If neither `filename` nor `self.file_path` is available,
    a ValueError is raised.

    If `filename` is provided and `self.file_path` is an absolute path, the extension of `filename`
    is replaced with '.sample5'. Otherwise, if `self.file_path` is available, its extension is replaced
    with '.sample5'. If neither is available, a ValueError is raised.

    Parameters:
        filename (str, optional): The name of the file to save to. If not provided, uses `self.file_path`.

    Returns:
        None
    """
    if filename is None:
        # save to default file name
        if self.file_path is not None:
            filename = os.path.splitext(self.file_path)[0] + ".sample5"
        else:
            raise ValueError("either filename or file_path must be provided")
    else:
        # check if filename includes an absolute path
        if os.path.isabs(self.file_path):
            filename = os.path.splitext(filename)[0] + ".sample5"
        elif self.file_path is not None:
            filename = os.path.splitext(self.file_path)[0] + ".sample5"
        else:
            raise ValueError("either filename or file_path must be provided")
    self._save_sample5(filename=filename)
    self.file_path = filename


def _save_featureXML(self, filename="features.featureXML"):
    if self._oms_features_map is None:
        self.logger.warning("No features found.")
        return
    fh = oms.FeatureXMLFile()
    fh.store(filename, self._oms_features_map)
    self.logger.debug(f"Features Map saved to {filename}")


def export_features(self, filename="features.csv"):
    """
    Export the features DataFrame to a CSV or Excel file.

    This method clones the internal features DataFrame, adds a boolean column 'has_ms2' indicating
    whether the 'ms2_scans' column is not null, and exports the resulting DataFrame to the specified file.
    Columns with data types 'List' or 'Object' are excluded from the export.

    Parameters:
        filename (str): The path to the output file. If the filename ends with '.xls' or '.xlsx',
                        the data is exported in Excel format; otherwise, it is exported as CSV.
                        Defaults to 'features.csv'.

    Side Effects:
        Writes the exported data to the specified file and logs the export operation.
    """
    # clone df
    clean_df = self.features_df.clone()
    filename = os.path.abspath(filename)
    # add a column has_ms2=True if column ms2_scans is not None
    if "ms2_scans" in clean_df.columns:
        clean_df = clean_df.with_columns(
            (pl.col("ms2_scans").is_not_null()).alias("has_ms2"),
        )
    clean_df = self.features_df.select(
        [
            col
            for col in self.features_df.columns
            if self.features_df[col].dtype not in (pl.List, pl.Object)
        ],
    )
    if filename.lower().endswith((".xls", ".xlsx")):
        clean_df.to_pandas().to_excel(filename, index=False)
        self.logger.info(f"Features exported to {filename} (Excel format)")
    else:
        clean_df.write_csv(filename)
        self.logger.info(f"Features exported to {filename}")


def export_mgf(
    self,
    filename: str = "features.mgf",
    use_cache=True,
    selection="best",
    split_energy=True,
    merge=False,
    mz_start=None,
    mz_end=None,
    rt_start=None,
    rt_end=None,
    include_all_ms1=False,
    full_ms1=False,
    centroid=True,
    inty_min=float("-inf"),
    q1_ratio_min=None,
    q1_ratio_max=None,
    eic_corr_min=None,
    deisotope=True,
    precursor_trim=10.0,
    centroid_algo=None,
):
    """
    Export features as an MGF file with MS1 and MS2 spectra.

    Iterates over all features in `self.features_df` (or `self._oms_features_map` if the former is None),
    retrieves the corresponding MS1 and MS2 spectra, applies peak filtering, and writes them in MGF format.

    Args:
        filename (str, optional): Output MGF file name. Defaults to "features.mgf".
        use_cache (bool, optional): Use cached MS2 spectra from the features DataFrame. Defaults to False.
        selection (str, optional): "best" for first scan, "all" for every scan. Defaults to "best".
        split_energy (bool, optional): Process MS2 scans by unique energy. Defaults to False.
        merge (bool, optional): If selection="all", merge MS2 scans into one spectrum. Defaults to False.
        mz_start (float, optional): Minimum m/z for feature selection.
        mz_end (float, optional): Maximum m/z for feature selection.
        rt_start (float, optional): Minimum RT for feature selection.
        rt_end (float, optional): Maximum RT for feature selection.
        include_all_ms1 (bool, optional): Include MS1 spectra even if no MS2 scan. Defaults to False.
        full_ms1 (bool, optional): Export full MS1 spectrum or trim around precursor. Defaults to False.
        centroid (bool, optional): Centroid the spectrum. Defaults to True.
        inty_min (float, optional): Minimum intensity threshold for peaks.
        q1_ratio_min (float, optional): Minimum q1_ratio for peaks.
        q1_ratio_max (float, optional): Maximum q1_ratio for peaks.
        eic_corr_min (float, optional): Minimum EIC correlation for peaks.
        deisotope (bool, optional): Perform deisotoping. Defaults to True.
        verbose (bool, optional): Print summary after export. Defaults to False.
        precursor_trim (int, optional): Trimming parameter for precursor peaks. Defaults to -10.
        centroid_algo (str, optional): Centroiding algorithm to use.

    Returns:
        None

    Notes:
        - If neither `self.features_df` nor `self._oms_features_map` are available, the method logs a warning and returns.
        - Uses internal helpers for peak filtering and MGF formatting.
        - For each feature, writes MS1 spectrum first, then MS2 spectra if available.
    """

    if self.features_df is None:
        if self._oms_features_map is None:
            self.logger.warning("Please find features first.")
            return
        else:
            self.features_df = self._oms_features_map.get_df()

    # Apply filtering at DataFrame level for better performance
    features = self.features_df
    if mz_start is not None:
        features = features.filter(pl.col("mz") >= mz_start)
    if mz_end is not None:
        features = features.filter(pl.col("mz") <= mz_end)
    if rt_start is not None:
        features = features.filter(pl.col("rt") >= rt_start)
    if rt_end is not None:
        features = features.filter(pl.col("rt") <= rt_end)
    if not include_all_ms1:
        features = features.filter(pl.col("ms2_scans").is_not_null())

    # Convert to list of dictionaries for faster iteration
    features_list = features.to_dicts()

    def filter_peaks(spec, inty_min=None, q1_min=None, eic_min=None, q1_max=None):
        # create a copy of the spectrum
        spec = spec.copy()
        spec_len = len(spec.mz)
        mask = [True] * spec_len
        if inty_min is not None and inty_min > 0:
            mask = np.array(mask) & (spec.inty >= inty_min)
        # check if q1_ratio is an attribute of spec
        if q1_min is not None and hasattr(spec, "q1_ratio"):
            mask = mask & (spec.q1_ratio >= q1_min)
        # check if eic_corr is an attribute of spec
        if q1_max is not None and hasattr(spec, "q1_ratio"):
            mask = mask & (spec.q1_ratio <= q1_max)
        # check if eic_corr is an attribute of spec
        if eic_min is not None and hasattr(spec, "eic_corr"):
            mask = mask & (spec.eic_corr >= eic_min)
        # apply mask to all attributes of spec with the same length as mz
        for attr in spec.__dict__:
            # check it attr is a list or an array:
            if isinstance(getattr(spec, attr), list) or isinstance(
                getattr(spec, attr),
                np.ndarray,
            ):
                # check if attr has attribute 0 and its length is equal to spec_len:
                if hasattr(getattr(spec, attr), "__len__"):
                    if len(getattr(spec, attr)) == spec_len:
                        setattr(spec, attr, getattr(spec, attr)[mask])
        return spec

    def write_ion(f, title, fid, mz, rt, charge, spect):
        if spect is None:
            return
        f.write(f"BEGIN IONS\nTITLE={title}\n")
        f.write(f"FEATURE_ID={fid}\n")
        f.write(f"CHARGE={charge}\nPEPMASS={mz}\nRTINSECONDS={rt}\n")
        if spect.ms_level is None:
            f.write("MSLEVEL=1\n")
        else:
            f.write(f"MSLEVEL={spect.ms_level}\n")
        if spect.ms_level is not None:
            if spect.ms_level > 1 and hasattr(spect, "energy"):
                f.write(f"ENERGY={spect.energy}\n")
        # Use list comprehension for better performance
        peak_lines = [
            f"{mz_val:.5f} {inty_val:.0f}\n"
            for mz_val, inty_val in zip(spect.mz, spect.inty, strict=False)
        ]
        f.writelines(peak_lines)
        f.write("END IONS\n\n")

    if centroid_algo is None:
        if hasattr(self.parameters, "centroid_algo"):
            centroid_algo = self.parameters.centroid_algo
        else:
            centroid_algo = "cr"

    # count how many features have charge < 0
    if (
        self.features_df.filter(pl.col("charge") < 0).shape[0]
        - self.features_df.filter(pl.col("charge") > 0).shape[0]
        > 0
    ):
        preferred_charge = -1
    else:
        preferred_charge = 1

    c = 0
    skip = 0
    # check if features is empty
    if len(features_list) == 0:
        self.logger.warning("No features found.")
        return
    filename = os.path.abspath(filename)
    with open(filename, "w", encoding="utf-8") as f:
        tdqm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]
        for row in tqdm(
            features_list,
            total=len(features_list),
            desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Export MGF",
            disable=tdqm_disable,
        ):
            # Pre-calculate common values
            feature_uid = row["feature_uid"]
            mz = row["mz"]
            rt = row["rt"]
            rt_str = f"{rt:.2f}"
            mz_str = f"{mz:.4f}"

            # Filtering is now done at DataFrame level, so we can skip these checks
            if row["ms2_scans"] is None and not include_all_ms1:
                skip = skip + 1
                continue

            # write MS1 spectrum
            ms1_scan_uid = self.select_closest_scan(rt=rt)["scan_uid"][0]
            spect = self.get_spectrum(
                ms1_scan_uid,
                centroid=centroid,
                deisotope=deisotope,
                centroid_algo=centroid_algo,
            )

            spect = filter_peaks(spect, inty_min=inty_min)

            if not full_ms1:
                # trim spectrum to region around the precursor, it's wide to potentially identify adducts
                spect = spect.trim(
                    mz_min=mz - 50,
                    mz_max=mz + 50,
                )

            charge = preferred_charge
            if row["charge"] is not None and row["charge"] != 0:
                charge = row["charge"]

            write_ion(
                f,
                f"feature_uid:{feature_uid}, rt:{rt_str}, mz:{mz_str}",
                feature_uid,
                mz,
                rt,
                charge,
                spect,
            )

            if row["ms2_scans"] is None:
                continue
            elif use_cache:
                spect = row["ms2_specs"]
                if spect is None:
                    # No cached spectra, fall through to fetch from scan_uid
                    use_cache = False
                else:
                    # check if spec is a list of spectra
                    if isinstance(spect, list):
                        if selection == "best":
                            s = spect[0]
                            scan_uid = row["ms2_scans"][0]
                            s.energy = self.get_spectrum(scan_uid).energy
                            spect = [s]
                            scan_uids = [scan_uid]
                        else:
                            scan_uids = row["ms2_scans"]

                        for i, s in enumerate(spect):
                            if s is None:
                                print(
                                    f"No MS2 spectrum for feature {feature_uid} is cached.",
                                )
                                continue
                            # check if s is a spectrum
                            if type(s).__name__ == "Spectrum":
                                s = filter_peaks(
                                    s,
                                    inty_min=inty_min,
                                    q1_min=q1_ratio_min,
                                    eic_min=eic_corr_min,
                                    q1_max=q1_ratio_max,
                                )
                                # Get the corresponding scan_uid from the list
                                current_scan_uid = (
                                    scan_uids[i] if i < len(scan_uids) else "unknown"
                                )
                                write_ion(
                                    f,
                                    f"fid:{feature_uid}, rt:{rt_str}, mz:{mz_str}, scan_uid:{current_scan_uid}",
                                    feature_uid,
                                    mz,
                                    rt,
                                    charge,
                                    s,
                                )
                                c += 1
                        continue  # Skip the rest of the processing for this feature

            # If we reach here, either use_cache=False or no cached spectra were available
            if split_energy:
                # get energy of all scans with scan_uid in ms2_scans by fetching them
                ms2_scan_uids = row["ms2_scans"]
                if isinstance(ms2_scan_uids, list) and len(ms2_scan_uids) > 0:
                    # Fetch spectra to get energy information
                    spectra_with_energy = []
                    for scan_uid in ms2_scan_uids:
                        spec = self.get_spectrum(scan_uid)
                        if spec is not None:
                            spectra_with_energy.append(
                                (
                                    scan_uid,
                                    spec.energy if hasattr(spec, "energy") else 0,
                                ),
                            )

                    # Group by energy
                    energy_groups: dict[float, list[int]] = {}
                    for scan_uid, energy in spectra_with_energy:
                        if energy not in energy_groups:
                            energy_groups[energy] = []
                        energy_groups[energy].append(scan_uid)

                    for energy, scan_uids_for_energy in energy_groups.items():
                        if selection == "best":
                            # Keep only the first scan for this energy
                            scan_uids_for_energy = [scan_uids_for_energy[0]]

                        for scan_uid in scan_uids_for_energy:
                            spect = self.get_spectrum(
                                scan_uid,
                                centroid=centroid,
                                deisotope=deisotope,
                                precursor_trim=precursor_trim,
                                centroid_algo=centroid_algo,
                            )
                            spect = filter_peaks(
                                spect,
                                inty_min=inty_min,
                                q1_min=q1_ratio_min,
                                eic_min=eic_corr_min,
                                q1_max=q1_ratio_max,
                            )
                            write_ion(
                                f,
                                f"fid:{feature_uid}, rt:{rt_str}, mz:{mz_str}, scan_uid:{scan_uid}, energy:{energy}",
                                feature_uid,
                                mz,
                                rt,
                                charge,
                                spect,
                            )
                            c += 1
            else:
                if selection == "best":
                    ms2_scans = row["ms2_scans"][0]
                    spect = self.get_spectrum(
                        ms2_scans,
                        centroid=centroid,
                        deisotope=deisotope,
                        precursor_trim=precursor_trim,
                        centroid_algo=centroid_algo,
                    )
                    spect = filter_peaks(
                        spect,
                        inty_min=inty_min,
                        q1_min=q1_ratio_min,
                        eic_min=eic_corr_min,
                        q1_max=q1_ratio_max,
                    )
                    write_ion(
                        f,
                        f"fid:{feature_uid}, rt:{rt_str}, mz:{mz_str}, scan_uid:{ms2_scans}",
                        feature_uid,
                        mz,
                        rt,
                        charge,
                        spect,
                    )
                    c += 1
                elif selection == "all":
                    if merge:
                        specs = []
                        for ms2_scans in row["ms2_scans"]:
                            specs.append(
                                self.get_spectrum(
                                    ms2_scans,
                                    centroid=centroid,
                                    deisotope=deisotope,
                                    precursor_trim=precursor_trim,
                                ),
                            )
                        spect = combine_peaks(specs)
                        if centroid:
                            spect = spect.denoise()
                            if spect.ms_level == 1:
                                spect = spect.centroid(
                                    tolerance=self.parameters["mz_tol_ms1_da"],
                                    ppm=self.parameters["mz_tol_ms1_ppm"],
                                    min_points=self.parameters[
                                        "centroid_min_points_ms1"
                                    ],
                                    algo=centroid_algo,
                                )
                            elif spect.ms_level == 2:
                                spect = spect.centroid(
                                    tolerance=self.parameters["mz_tol_ms2_da"],
                                    ppm=self.parameters["mz_tol_ms2_ppm"],
                                    min_points=self.parameters[
                                        "centroid_min_points_ms2"
                                    ],
                                    algo=centroid_algo,
                                )
                        if deisotope:
                            spect = spect.deisotope()
                        title = f"fid:{feature_uid}, rt:{rt_str}, mz:{mz_str}, merged"
                        spect = filter_peaks(
                            spect,
                            inty_min=inty_min,
                            q1_min=q1_ratio_min,
                            eic_min=eic_corr_min,
                            q1_max=q1_ratio_max,
                        )
                        write_ion(
                            f,
                            title,
                            feature_uid,
                            mz,
                            rt,
                            charge,
                            spect,
                        )
                        c += 1
                    else:
                        for ms2_scans in row["ms2_scans"]:
                            spect = self.get_spectrum(
                                ms2_scans,
                                centroid=centroid,
                                deisotope=deisotope,
                                precursor_trim=precursor_trim,
                                centroid_algo=centroid_algo,
                            )
                            spect = filter_peaks(
                                spect,
                                inty_min=inty_min,
                                q1_min=q1_ratio_min,
                                eic_min=eic_corr_min,
                                q1_max=q1_ratio_max,
                            )
                            write_ion(
                                f,
                                f"fid:{feature_uid}, rt:{rt_str}, mz:{mz_str}, scan_uid:{ms2_scans}",
                                feature_uid,
                                mz,
                                rt,
                                charge,
                                spect,
                            )
                            c += 1

    self.logger.info(f"Exported {c} features to {filename}")

    # Handle None values in logging
    inty_min_str = f"{inty_min:.3f}" if inty_min != float("-inf") else "None"
    q1_ratio_min_str = f"{q1_ratio_min:.3f}" if q1_ratio_min is not None else "None"
    eic_corr_min_str = f"{eic_corr_min:.3f}" if eic_corr_min is not None else "None"

    self.logger.debug(
        f"MGF created with int>{inty_min_str}, q1_ratio>{q1_ratio_min_str}, eic_corr>{eic_corr_min_str}",
    )
    self.logger.debug(
        f"- Exported {c} MS2 spectra for {len(features_list) - skip} precursors. Average spectra/feature is {c / (len(features_list) - skip + 0.000000001):.0f}",
    )
    self.logger.debug(
        f"- Skipped {skip} features because no MS2 scans were available.",
    )


def export_dda_stats(self, filename="stats.csv"):
    """
    Save DDA statistics into a CSV file.

    This method computes basic statistics from the DDA analysis, such as:
        - Total number of MS1 scans.
        - Total number of MS2 scans.
        - Total number of detected features.
        - Number of features linked with MS2 data.
        - Average cycle time (if available in the scans data).

    The resulting statistics are saved in CSV format.

    Parameters:
        filename (str): The name/path of the CSV file to be saved. Defaults to "stats.csv".

    Returns:
        None
    """
    # Compute counts from scans_df and features_df
    ms1_count = len(self.scans_df.filter(pl.col("ms_level") == 1))
    ms2_count = len(self.scans_df.filter(pl.col("ms_level") == 2))
    features_count = len(self.features_df) if self.features_df is not None else 0
    features_with_ms2 = (
        self.features_df.filter(pl.col("ms2_scans").is_not_null()).height
        if self.features_df is not None
        else 0
    )

    # Initialize a dictionary to hold statistics
    stats = {
        "MS1_scans": ms1_count,
        "MS2_scans": ms2_count,
        "Total_features": features_count,
        "Features_with_MS2": features_with_ms2,
    }

    # Calculate the average cycle time if available.
    if "time_cycle" in self.scans_df.columns:
        ms1_df = self.scans_df.filter(pl.col("ms_level") == 1)
        avg_cycle_time = ms1_df["time_cycle"].mean()
        stats["Average_cycle_time"] = (
            avg_cycle_time if avg_cycle_time is not None else ""
        )
    else:
        stats["Average_cycle_time"] = 0

    # Convert stats dict to a Pandas DataFrame and save as CSV.
    df_stats = pd.DataFrame(list(stats.items()), columns=["Metric", "Value"])
    df_stats.to_csv(filename, index=False)
    lines = []
    lines.append(f"Filename,{self.file_path}")
    lines.append(
        f"Number of cycles,{len(self.scans_df.filter(pl.col('ms_level') == 1))}",
    )
    lines.append(
        f"Number of MS2 scans,{len(self.scans_df.filter(pl.col('ms_level') == 2))}",
    )
    # retrieve scans with mslevel 1 from
    ms1 = self.scans_df.filter(pl.col("ms_level") == 1)
    lines.append(f"Maximal number of MS2 scans per cycle (N),{ms1['ms2_n'].max()}")
    # average number of MS2 scans per cycle, skip null values
    ms2n_mean = ms1.filter(pl.col("ms2_n") >= 0)["ms2_n"].mean()
    lines.append(f"Average number of MS2 scans per cycle,{ms2n_mean:.0f}")
    lines.append(f"Maximal cycle time,{ms1['time_cycle'].max():.3f}")
    # find spectra with ms2_n = 0
    ms1_ms2_0 = ms1.filter(pl.col("ms2_n") == 0)
    if len(ms1_ms2_0) > 0:
        lines.append(
            f"Average cycle time at MS1-only,{ms1_ms2_0['time_cycle'].mean():.3f}",
        )
    else:
        lines.append("Average cycle time at MS1-only,")
    # find spectra with ms2_n = 1
    ms1_ms2_1 = ms1.filter(pl.col("ms2_n") == 1)
    if len(ms1_ms2_1) > 0:
        lines.append(
            f"Average cycle time with 1 MS2,{ms1_ms2_1['time_cycle'].mean():.3f}",
        )
    else:
        lines.append("Average cycle time with 1 MS2,")
    # find spectra with ms2_n = 2
    ms1_ms2_2 = ms1.filter(pl.col("ms2_n") == 2)
    if len(ms1_ms2_2) > 0:
        lines.append(
            f"Average cycle time with 2 MS2,{ms1_ms2_2['time_cycle'].mean():.3f}",
        )
    else:
        lines.append("Average cycle time with 2 MS2,")
    # find spectra with ms2_n = 2
    ms1_ms2_3 = ms1.filter(pl.col("ms2_n") == 3)
    if len(ms1_ms2_3) > 0:
        lines.append(
            f"Average cycle time with 3 MS2,{ms1_ms2_3['time_cycle'].mean():.3f}",
        )
    else:
        lines.append("Average cycle time with 3 MS2,")
    max_ms2_n = ms1["ms2_n"].max()
    ms1_ms2_n1 = ms1.filter(pl.col("ms2_n") == max_ms2_n - 1)
    if len(ms1_ms2_n1) > 0:
        lines.append(
            f"Average cycle time with N-1 MS2,{ms1_ms2_n1['time_cycle'].mean():.3f}",
        )
    else:
        lines.append("Average cycle time with N-1 MS2,")
    # find specgtra with maximal ms2_n
    ms1_max_ms2_n = ms1.filter(pl.col("ms2_n") == max_ms2_n)
    lines.append(
        f"Average cycle time with N MS2,{ms1_max_ms2_n['time_cycle'].mean():.3f}",
    )
    # average time_MS1, skip null values
    a = ms1.filter(pl.col("time_ms1_to_ms1") >= 0)["time_ms1_to_ms1"].mean()
    if a is not None:
        lines.append(f"Average MS1-to-MS1 scan time,{a:.3f}")
    else:
        lines.append("Average MS1-to-MS1 scan time,")
    a = ms1.filter(pl.col("time_ms1_to_ms2") >= 0)["time_ms1_to_ms2"].mean()
    if a is not None:
        lines.append(f"Average MS1-to-MS2 scan time,{a:.3f}")
    else:
        lines.append("Average MS1-to-MS2 scan time,")
    ms2_mean = ms1.filter(pl.col("time_ms2_to_ms2") >= 0)["time_ms2_to_ms2"].mean()
    if ms2_mean is not None:
        lines.append(f"Average MS2-to-MS2 scan time,{ms2_mean:.3f}")
    else:
        lines.append("Average MS2-to-MS2 scan time,")
    a = ms1.filter(pl.col("time_ms2_to_ms1") >= 0)["time_ms2_to_ms1"].mean()
    if a is not None:
        lines.append(f"Average MS2-to-MS1 scan time,{a:.3f}")
    else:
        lines.append("Average MS2-to-MS1 scan time,")
    # number of features
    if self.features_df is not None:
        lines.append(f"Number of features,{self.features_df.height}")
        a = self.features_df.filter(pl.col("ms2_scans").is_not_null()).height
        lines.append(f"Number of features with MS2 data,{a}")
        b = self.scans_df.filter(pl.col("feature_uid") >= 0).height
        lines.append(f"Number of MS2 scans with features,{b}")
        if a > 0:
            lines.append(f"Redundancy of MS2 scans with features,{b / a:.3f}")
        else:
            lines.append("Redundancy of MS2 scans with features,")
    else:
        lines.append("Number of features,")
        lines.append("Number of features with MS2 data,")
        lines.append("Number of MS2 scans with features,")
        lines.append("Redundancy of MS2 scans with features,")

    # write to file
    with open(filename, "w") as f:
        for line in lines:
            f.write(line + "\n")

    self.logger.info(f"DDA statistics exported to {filename}")


def export_chrom(self, filename="chrom.csv"):
    # saves self.chrom_df to a csv file. Remove the scan_uid and chrom columns if the file already exists
    if self.chrom_df is None:
        self.logger.warning("No chromatogram definitions found.")
        return
    data = self.chrom_df.clone()
    # Convert to pandas for CSV export
    if hasattr(data, "to_pandas"):
        data = data.to_pandas()
    # remove scan_uid and chrom columns if they exist
    if "scan_uid" in data.columns:
        data = data.drop("scan_uid")
    if "chrom" in data.columns:
        data = data.drop("chrom")
    data.to_csv(filename, index=False)
