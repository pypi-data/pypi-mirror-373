"""
lib.py

This module provides the Lib class and utility functions for mass spectrometry compound library
management and feature annotation. It contains core functionality for compound library management,
target identification, adduct handling, and various analytical operations.

Key Features:
- **Lib Class**: Main class for managing compound libraries and annotations
- **Compound Libraries**: Load and manage compound databases with metadata
- **Adduct Calculations**: Handle various ionization adducts and charge states
- **Mass Calculations**: Precise mass calculations with adduct corrections
- **Target Matching**: Match detected features against compound libraries
- **Polarity Handling**: Support for positive and negative ionization modes
- **Database Integration**: Interface with various compound database formats

Dependencies:
- `pyopenms`: For mass spectrometry algorithms and data structures
- `polars` and `pandas`: For efficient data manipulation and analysis
- `numpy`: For numerical computations and array operations
- `tqdm`: For progress tracking during batch operations

Classes:
- `Lib`: Main class for compound library management and annotation

Functions:
- `lib_load()`: Load compound libraries from CSV files (legacy)
- `load_lib()`: Alias for lib_load function (legacy)
- Various utility functions for mass calculations and library management

Supported Adducts:
- Positive mode: [M+H]+, [M+Na]+, [M+K]+, [M+NH4]+, [M-H2O+H]+
- Negative mode: [M-H]-, [M+CH3COO]-, [M+HCOO]-, [M+Cl]-

Example Usage:
```python
from masster.sample.lib import Lib

# Create library instance
lib = Lib()

# Import compounds from CSV
lib.import_csv("compounds.csv", polarity="positive")

# Access library data
print(f"Loaded {len(lib.lib_df)} compounds")
print(lib.lib_df.head())
```

See Also:
- `parameters._lib_parameters`: For library-specific parameter configuration
- `sample.py`: For applying library matching to detected features

"""

import os
import re

import numpy as np
import pandas as pd
import polars as pl
import pyopenms as oms

from tqdm import tqdm

from masster.chromatogram import Chromatogram
# Parameters removed - using hardcoded defaults


def load_lib(self, *args, **kwargs):
    lib_load(self, *args, **kwargs)


def lib_load(self, csvfile=None, polarity="positive"):
    delta_m = {
        "[M+H]+": 1.007276,
        "[M+Na]+": 22.989218,
        "[M+K]+": 39.962383,
        "[M+NH4]+": 18.033823,
        "[M-H2O+H]+": -17.00329,
        "[M-H]-": -1.007276,
        "[M+CH3COO]-": -59.013852,
        "[M+HCOO]-": -45.998203,
        "[M+Cl]-": -34.968853,
    }
    delta_z = {
        "[M+H]+": 1,
        "[M+Na]+": 1,
        "[M+K]+": 1,
        "[M+NH4]+": 1,
        "[M-H2O+H]+": 1,
        "[M+CH3COO]-": -1,
        "[M-H]-": -1,
        "[M+HCOO]-": -1,
        "[M+Cl]-": -1,
    }
    """
    Load target compounds from a CSV file.
    This method reads a CSV file containing target compounds and their properties, such as m/z, retention time (RT),
    and adducts. It filters the targets based on the specified adducts and returns a DataFrame of the targets.
    Parameters:
        csvfile (str): The path to the CSV file containing target compounds.
        adducts (list, optional): A list of adducts to filter the targets. Default is ['[M+H]+', '[M+Na]+', '[M+K]+'].
    Returns:
        pd.DataFrame: A DataFrame containing the filtered target compounds with columns 'mz', 'rt', 'adduct'.
    """
    self.lib = None
    df = pd.read_csv(csvfile)
    # filter targets by adducts
    # iterate over all rows in df
    # find index of column in df named "Name" or "name" or "Compound"
    df_cols = df.columns
    if "Name" in df_cols:
        name_col = "Name"
    elif "name" in df_cols:
        name_col = "name"
    elif "Compound" in df_cols:
        name_col = "Compound"
    elif "compound" in df_cols:
        name_col = "compound"
    else:
        raise ValueError(
            "No column named 'Name', 'name', or 'Compound' found in the CSV file.",
        )
    if "Formula" in df_cols:
        formula_col = "Formula"
    elif "formula" in df_cols:
        formula_col = "formula"
    else:
        raise ValueError(
            "No column named 'Formula' or 'formula' found in the CSV file.",
        )
    if "SMILES" in df_cols:
        smiles_col = "SMILES"
    elif "smiles" in df_cols:
        smiles_col = "smiles"
    else:
        raise ValueError("No column named 'SMILES' or 'smiles' found in the CSV file.")
    if "rt" in df_cols:
        rt_col = "rt"
    elif "RT" in df_cols:
        rt_col = "RT"
    else:
        rt_col = None
    if "rt2" in df_cols:
        rt_col2 = "rt2"
    elif "RT2" in df_cols:
        rt_col2 = "RT2"
    else:
        rt_col2 = None
    if "id" in df_cols:
        id_col = "id"
    elif "ID" in df_cols:
        id_col = "ID"
    else:
        id_col = name_col
    if "set" in df_cols:
        set_col = "set"
    elif "Set" in df_cols:
        set_col = "Set"
    else:
        set_col = None
        print(
            "No column named 'set' or 'Set' found in the CSV file. Using all targets.",
        )

    targets = []
    c = 0
    for _index, row in df.iterrows():
        # calculate accurate mass for row[formula_col]
        m = oms.EmpiricalFormula(row[formula_col])
        try:
            accurate_mass = m.getMonoWeight()
        except Exception as e:
            print(f"Error calculating accurate mass for {row[formula_col]}: {e}")
            continue

        rt = row[rt_col] if rt_col is not None else None
        for adduct in delta_m:
            new_target = {
                "libid": c,
                "set": row[set_col] if set_col is not None else None,
                "name": row[name_col],
                "id": row[id_col],
                "smiles": row[smiles_col],
                "formula": row[formula_col],
                "adduct": adduct,
                "m": accurate_mass + delta_m[adduct],
                "z": delta_z[adduct],
                "mz": (accurate_mass + delta_m[adduct]) / delta_z[adduct],
                "rt": rt,
                "MS2spec": None,
            }
            targets.append(new_target)
        if rt_col2 is not None:
            rt = row[rt_col2]
            for adduct in delta_m:
                new_target = {
                    "libid": c,
                    "set": row[set_col] if set_col is not None else None,
                    "name": row[name_col] + " II",
                    "id": row[id_col],
                    "smiles": row[smiles_col],
                    "formula": row[formula_col],
                    "adduct": adduct,
                    "m": accurate_mass + delta_m[adduct],
                    "z": delta_z[adduct],
                    "mz": (accurate_mass + delta_m[adduct]) / delta_z[adduct],
                    "rt": rt,
                    "MS2spec": None,
                }
                targets.append(new_target)
        c += 1

    # convert targets to DataFrame
    self.lib = pd.DataFrame(targets)
    # ensure that mz is . use the abs()
    self.lib["mz"] = self.lib["mz"].abs()
    # convert all np.nan to None
    self.lib = self.lib.where(pd.notnull(self.lib), None)
    # find all elements == nan and replace them with None
    self.lib = self.lib.replace({np.nan: None})
    if polarity is not None:
        if polarity.lower() == "positive":
            self.lib = self.lib[self.lib["z"] > 0]
        elif polarity.lower() == "negative":
            self.lib = self.lib[self.lib["z"] < 0]
        else:
            raise ValueError("Polarity must be 'positive' or 'negative'.")


def link_lib(self, *args, **kwargs):
    self.lib_link(*args, **kwargs)


def lib_link(
    self,
    mz_tol=0.01,
    mz_tol_factor_lib=0.5,
    rt_tol=6.0,
    rt_tol_factor_lib=0.5,
    level=1,
):
    """
    Find all features that match the mz and rt is not None. Add all feature_uids of the feature to the lib_ms1 DataFrame.
    """

    lib_matches = []
    mz_tol_lib = mz_tol * mz_tol_factor_lib
    rt_tol_lib = rt_tol * rt_tol_factor_lib

    for _index, row in self.lib.iterrows():
        # find all features that match the mz and rt is not None
        mask = (self.features_df["mz"] >= row["mz"] - mz_tol_lib) & (self.features_df["mz"] <= row["mz"] + mz_tol_lib)
        if row["rt"] is not None and rt_tol_lib is not np.nan:
            mask &= (self.features_df["rt"] >= row["rt"] - rt_tol_lib) & (
                self.features_df["rt"] <= row["rt"] + rt_tol_lib
            )
        if level == 1:
            # get the feature_uids of the features that match the mask
            feature_uids = self.features_df[mask]["feature_uid"].to_list()
            for feature_uid in feature_uids:
                # create a new df with id, name, formula, adduct, delta_mz, delta_rt, scan_uid,
                f = self.features_df[self.features_df["feature_uid"] == feature_uid]
                new_match = {
                    "libid": row["libid"],
                    "set": row["set"],
                    "name": row["name"],
                    "id": row["id"],
                    "formula": row["formula"],
                    "adduct": row["adduct"],
                    "smiles": row["smiles"],
                    "z": row["z"],
                    "match_level": 1,
                    "feature_uid": feature_uid,
                    "inty": f["inty"].values[0],
                    "quality": f["quality"].values[0],
                    "mz": f["mz"].values[0],
                    "delta_mz": row["mz"] - f["mz"].values[0],
                    "rt": f["rt"].values[0],
                    "delta_rt": row["rt"] - f["rt"].values[0] if row["rt"] is not None else None,
                    "ms2_scans": f["ms2_scans"].values[0] if "ms2_scans" in self.features_df.columns else None,
                    "eic": None,
                }
                lib_matches.append(new_match)

    # convert lib_matches to DataFrame
    self.lib_match = pd.DataFrame(lib_matches)
    self.lib_eic(mz_tol=mz_tol, rt_tol=rt_tol)


def lib_eic(
    self,
    mz_tol=0.01,
    rt_tol=6.0,
):
    # for each matched feature, extract the EIC and add it to the lib_match DataFrame
    if self.lib_match is None:
        print("Please load and match the library first.")
        return
    if len(self.lib_match) == 0:
        print("No matches found.")
        return
    for index, row in self.lib_match.iterrows():
        # find the feature with feature_uid == row["feature_uid"]
        f = self.features_df[self.features_df["feature_uid"] == row["feature_uid"]]
        if f.empty:
            continue
        f = f.iloc[0]
        rt_start = f["rt_start"] - rt_tol
        rt_end = f["rt_end"] + rt_tol
        # find all ms1 data in the retention time range. self.ms1_df is a polars DataFrame
        d = self.ms1_df.filter(
            (pl.col("rt") >= rt_start)
            & (pl.col("rt") <= rt_end)
            & (pl.col("mz") >= f["mz"] - mz_tol)
            & (pl.col("mz") <= f["mz"] + mz_tol),
        )
        # for all unique rt values, find the maximum inty
        eic_rt = d.group_by("rt").agg(pl.col("inty").max())
        eic = Chromatogram(
            eic_rt["rt"].to_numpy(),
            eic_rt["inty"].to_numpy(),
            label=f"EIC mz={f['mz']:.4f}; {row['name']} {row['adduct']}",
            feature_start=f["rt_start"],
            feature_end=f["rt_end"],
            lib_rt=row["rt"],
        )
        self.lib_match.loc[index, "eic"] = eic


# TODO Should go in _export? (Almost the same method already there)
def save_lib_mgf(
    self,
    filename="lib_export.mgf",
    selection="best",
    split_energy=True,
    merge=False,
    centroid=True,
    inty_min=float("-inf"),
    q1_ratio_min=None,
    q1_ratio_max=None,
    eic_corr_min=None,
    deisotope=True,
    verbose=False,
    precursor_trim=-10.0,
    centroid_algo=None,
):
    if self.lib_match is None:
        print("Please load and match the library first.")
        return

    if len(self.lib_match) == 0:
        print("No matches found.")
        return

    # iterate over all features

    def filter_peaks(spec, inty_min=None, q1_min=None, eic_min=None, q1_max=None):
        # create a copy of the spectrum
        spec = spec.copy()
        l = len(spec.mz)
        mask = [True] * l
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
                # check if attr has attribute 0 and its length is equal to l:
                if hasattr(getattr(spec, attr), "__len__"):
                    if len(getattr(spec, attr)) == l:
                        setattr(spec, attr, getattr(spec, attr)[mask])
        return spec

    def write_ion(f, d, spec):
        if spec is None:
            return
        f.write("BEGIN IONS\n")
        # iterate through all d.keys()
        for key in d:
            f.write(f"{key.upper()}={d[key]}\n")
        for mz, inty in zip(spec.mz, spec.inty, strict=False):
            f.write(f"{mz:.5f} {inty:.0f}\n")
        f.write("END IONS\n\n")

    if centroid_algo is None:
        if "centroid_algo" in self.parameters:
            centroid_algo = self.parameters["centroid_algo"]
        else:
            centroid_algo = "cr"

    # c = 0
    skip = 0
    # check if features is empty
    with open(filename, "w", encoding="utf-8") as f:
        for _index, matchrow in tqdm(
            self.lib_match.iterrows(),
            total=len(self.lib_match),
            desc="Export MGF",
        ):
            # find the feature with feature_uid == matchrow["feature_uid"]
            row = self.features_df[self.features_df["feature_uid"] == matchrow["feature_uid"]].iloc[0]
            if row["ms2_scans"] is None:
                skip = skip + 1
                continue

            # write MS1 spectrum
            ms1_scan_uid = self.select_closest_scan(rt=row["rt"])["scan_uid"][0]
            spec = self.get_spectrum(
                ms1_scan_uid,
                centroid=centroid,
                deisotope=deisotope,
                centroid_algo=centroid_algo,
            )
            # trim spectrum 2 Da lower and 10 Da higher than precursor m/z
            spec = spec.mz_trim(mz_min=row["mz"] - 2.0, mz_max=row["mz"] + 10.0)

            file_basename: str = os.path.basename(self.file_path)
            mslevel = 1 if spec.ms_level is None else spec.ms_level
            activation = None
            energy = None
            kineticenergy = None
            if mslevel > 1:
                if "CID" in file_basename.upper() or "ZTS" in file_basename.upper():
                    if "EAD" in file_basename.upper():
                        activation = "CID-EAD"
                        # search ([0-9]*KE) in filename.upper() using regex
                        match = re.search(r"(\d+)KE", str(filename.upper()))
                        if match:
                            kineticenergy = int(match.group(1))
                        else:
                            match = re.search(r"(\d+)EV", filename.upper())
                            if match:
                                kineticenergy = int(match.group(1))
                    else:
                        activation = "CID"
                elif "EAD" in file_basename.upper():
                    activation = "EAD"
                    # search ([0-9]*KE) in filename.upper() using regex
                    match = re.search(r"(\d+)KE", file_basename.upper())
                    if match:
                        kineticenergy = int(match.group(1))
                    else:
                        match = re.search(r"(\d+)EV", file_basename.upper())
                        if match:
                            kineticenergy = int(match.group(1))
                energy = spec.energy if hasattr(spec, "energy") else None

            spec = filter_peaks(spec, inty_min=inty_min)
            d = {
                "PEPMASS": row["mz"],
                "RTINSECONDS": row["rt"],
                "IONMODE": "positive" if matchrow["adduct"][-1] == "+" else "negative",
                "CHARGE": "1" + matchrow["adduct"].split("]")[1],
                "NAME": f"{matchrow['name']}",
                "SMILES": matchrow["smiles"],
                "FORMULA": matchrow["formula"],
                "ADDUCT": matchrow["adduct"],
                "LIBID": matchrow["libid"],
                "ACTIVATION": activation,
                "COLLISIONENERGY": energy,
                "KINETICENERGY": kineticenergy,
                "FILENAME": filename,
                "SCANS": ms1_scan_uid,
                "FID": row["feature_uid"],
                "MSLEVEL": 1 if spec.ms_level is None else spec.ms_level,
            }
            write_ion(f, d, spec)

            if split_energy:
                # get energy of all scans with scan_uid in ms2_scans
                energy = [s.energy for s in row["ms2_specs"]]
                # find unique energies
                unique_energies = list(set(energy))
                for e in unique_energies:
                    ms2_scans = [s.scan_uid for s in row["ms2_specs"] if s.energy == e]
                    if selection == "best":
                        ms2_scans = ms2_scans[0]
                    for scan_uid in ms2_scans:
                        spec = self.get_spectrum(
                            scan_uid,
                            centroid=centroid,
                            deisotope=deisotope,
                            precursor_trim=precursor_trim,
                            centroid_algo=centroid_algo,
                        )
                        spec = filter_peaks(
                            spec,
                            inty_min=inty_min,
                            q1_min=q1_ratio_min,
                            eic_min=eic_corr_min,
                            q1_max=q1_ratio_max,
                        )
                        # TODO not used
                        mslevel = 1 if spec.ms_level is None else spec.ms_level
                        activation = None
                        energy = None
                        kineticenergy = None
                        if "CID" in filename.upper() or "ZTS" in filename.upper():
                            if "EAD" in filename.upper():
                                activation = "CID-EAD"
                                # search ([0-9]*KE) in filename.upper() using regex
                                match = re.search(r"(\d+)KE", filename.upper())
                                if match:
                                    kineticenergy = int(match.group(1))
                                else:
                                    match = re.search(r"(\d+)EV", filename.upper())
                                    if match:
                                        kineticenergy = int(match.group(1))
                            else:
                                activation = "CID"
                        elif "EAD" in file_basename.upper():
                            activation = "EAD"
                            # search ([0-9]*KE) in file_basename.upper() using regex
                            match = re.search(r"(\d+)KE", file_basename.upper())
                            if match:
                                kineticenergy = int(match.group(1))
                            else:
                                match = re.search(r"(\d+)EV", file_basename.upper())
                                if match:
                                    kineticenergy = int(match.group(1))
                            energy = spec.energy if hasattr(spec, "energy") else None

                        spec = filter_peaks(spec, inty_min=inty_min)
                        d = {
                            "PEPMASS": row["mz"],
                            "RTINSECONDS": row["rt"],
                            "IONMODE": "positive" if matchrow["adduct"][-1] == "+" else "negative",
                            "CHARGE": "1" + matchrow["adduct"].split("]")[1],
                            "NAME": f"{matchrow['name']}",
                            "SMILES": matchrow["smiles"],
                            "FORMULA": matchrow["formula"],
                            "ADDUCT": matchrow["adduct"],
                            "LIBID": matchrow["libid"],
                            "ACTIVATION": activation,
                            "COLLISIONENERGY": energy,
                            "KINETICENERGY": kineticenergy,
                            "FILENAME": file_basename,
                            "SCANS": ms1_scan_uid,
                            "FID": row["feature_uid"],
                            "MSLEVEL": 1 if spec.ms_level is None else spec.ms_level,
                        }

                        write_ion(f, d, spec)
            else:
                if selection == "best":
                    ms2_scans = row["ms2_scans"][0]
                    spec = self.get_spectrum(
                        ms2_scans,
                        centroid=centroid,
                        deisotope=deisotope,
                        precursor_trim=precursor_trim,
                        centroid_algo=centroid_algo,
                    )
                    spec = filter_peaks(
                        spec,
                        inty_min=inty_min,
                        q1_min=q1_ratio_min,
                        eic_min=eic_corr_min,
                        q1_max=q1_ratio_max,
                    )
                    mslevel = 1 if spec.ms_level is None else spec.ms_level
                    activation = None
                    energy = None
                    kineticenergy = None
                    if mslevel > 1:
                        if "CID" in filename.upper() or "ZTS" in filename.upper():
                            if "EAD" in filename.upper():
                                activation = "CID-EAD"
                                # search ([0-9]*KE) in filename.upper() using regex
                                match = re.search(r"(\d+)KE", filename.upper())
                                if match:
                                    kineticenergy = int(match.group(1))
                                else:
                                    match = re.search(r"(\d+)EV", filename.upper())
                                    if match:
                                        kineticenergy = int(match.group(1))
                            else:
                                activation = "CID"
                        elif "EAD" in filename.upper():
                            activation = "EAD"
                            # search ([0-9]*KE) in filename.upper() using regex
                            match = re.search(r"(\d+)KE", filename.upper())
                            if match:
                                kineticenergy = int(match.group(1))
                            else:
                                match = re.search(r"(\d+)EV", filename.upper())
                                if match:
                                    kineticenergy = int(match.group(1))
                        energy = spec.energy if hasattr(spec, "energy") else None

                    spec = filter_peaks(spec, inty_min=inty_min)
                    d = {
                        "PEPMASS": row["mz"],
                        "RTINSECONDS": row["rt"],
                        "IONMODE": "positive" if matchrow["adduct"][-1] == "+" else "negative",
                        "CHARGE": "1" + matchrow["adduct"].split("]")[1],
                        "NAME": f"{matchrow['name']}",
                        "SMILES": matchrow["smiles"],
                        "FORMULA": matchrow["formula"],
                        "ADDUCT": matchrow["adduct"],
                        "LIBID": matchrow["libid"],
                        "ACTIVATION": activation,
                        "COLLISIONENERGY": energy,
                        "KINETICENERGY": kineticenergy,
                        "FILENAME": filename,
                        "SCANS": ms1_scan_uid,
                        "FID": row["feature_uid"],
                        "MSLEVEL": 1 if spec.ms_level is None else spec.ms_level,
                    }
                    write_ion(f, d, spec)
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
                        spec = spec.merge_peaks(specs)
                        if centroid:
                            spec = spec.denoise()
                            if spec.ms_level == 1:
                                spec = spec.centroid(
                                    tolerance=self.parameters["mz_tol_ms1_da"],
                                    ppm=self.parameters["mz_tol_ms1_ppm"],
                                    min_points=self.parameters["centroid_min_points_ms1"],
                                    algo=centroid_algo,
                                )
                            elif spec.ms_level == 2:
                                spec = spec.centroid(
                                    tolerance=self.parameters["mz_tol_ms2_da"],
                                    ppm=self.parameters["mz_tol_ms2_ppm"],
                                    min_points=self.parameters["centroid_min_points_ms2"],
                                    algo=centroid_algo,
                                )
                        if deisotope:
                            spec = spec.deisotope()
                        spec = filter_peaks(
                            spec,
                            inty_min=inty_min,
                            q1_min=q1_ratio_min,
                            eic_min=eic_corr_min,
                            q1_max=q1_ratio_max,
                        )
                        mslevel = 1 if spec.ms_level is None else spec.ms_level
                        activation = None
                        energy = None
                        kineticenergy = None
                        if mslevel > 1:
                            if "CID" in filename.upper() or "ZTS" in filename.upper():
                                if "EAD" in filename.upper():
                                    activation = "CID-EAD"
                                    match = re.search(r"(\d+)KE", filename.upper())
                                    if match:
                                        kineticenergy = int(match.group(1))
                                    else:
                                        match = re.search(r"(\d+)EV", filename.upper())
                                        if match:
                                            kineticenergy = int(match.group(1))
                                else:
                                    activation = "CID"
                            energy = spec.energy if hasattr(spec, "energy") else None

                        spec = filter_peaks(spec, inty_min=inty_min)
                        d = {
                            "PEPMASS": row["mz"],
                            "RTINSECONDS": row["rt"],
                            "IONMODE": "positive" if matchrow["adduct"][-1] == "+" else "negative",
                            "CHARGE": "1" + matchrow["adduct"].split("]")[1],
                            "NAME": f"{matchrow['name']}",
                            "SMILES": matchrow["smiles"],
                            "FORMULA": matchrow["formula"],
                            "ADDUCT": matchrow["adduct"],
                            "LIBID": matchrow["libid"],
                            "ACTIVATION": activation,
                            "COLLISIONENERGY": energy,
                            "KINETICENERGY": kineticenergy,
                            "FILENAME": filename,
                            "SCANS": ms1_scan_uid,
                            "FID": row["feature_uid"],
                            "MSLEVEL": 1 if spec.ms_level is None else spec.ms_level,
                        }
                        write_ion(f, d, spec)
                    else:
                        for ms2_scans in row["ms2_scans"]:
                            spec = self.get_spectrum(
                                ms2_scans,
                                centroid=centroid,
                                deisotope=deisotope,
                                precursor_trim=precursor_trim,
                                centroid_algo=centroid_algo,
                            )
                            spec = filter_peaks(
                                spec,
                                inty_min=inty_min,
                                q1_min=q1_ratio_min,
                                eic_min=eic_corr_min,
                                q1_max=q1_ratio_max,
                            )
                            mslevel = 1 if spec.ms_level is None else spec.ms_level
                            activation = None
                            energy = None
                            kineticenergy = None
                            if mslevel > 1:
                                if (
                                    "CID" in filename.upper() or "ZTS" in filename.upper()
                                ) and "EAD" in filename.upper():
                                    activation = "CID-EAD"
                                    match = re.search(r"(\d+)KE", filename.upper())
                                    if match:
                                        kineticenergy = int(match.group(1))
                                    else:
                                        match = re.search(r"(\d+)EV", filename.upper())
                                        if match:
                                            kineticenergy = int(match.group(1))
                                        else:
                                            activation = "CID"
                                energy = spec.energy if hasattr(spec, "energy") else None

                            spec = filter_peaks(spec, inty_min=inty_min)
                            d = {
                                "PEPMASS": row["mz"],
                                "RTINSECONDS": row["rt"],
                                "IONMODE": "positive" if matchrow["adduct"][-1] == "+" else "negative",
                                "CHARGE": "1" + matchrow["adduct"].split("]")[1],
                                "NAME": f"{matchrow['name']}",
                                "SMILES": matchrow["smiles"],
                                "FORMULA": matchrow["formula"],
                                "ADDUCT": matchrow["adduct"],
                                "LIBID": matchrow["libid"],
                                "ACTIVATION": activation,
                                "COLLISIONENERGY": energy,
                                "KINETICENERGY": kineticenergy,
                                "FILENAME": filename,
                                "SCANS": ms1_scan_uid,
                                "FID": row["fid"],
                                "MSLEVEL": 1 if spec.ms_level is None else spec.ms_level,
                            }
                            write_ion(f, d, spec)

    if verbose:
        print(
            f"MGF created with int>{inty_min:.3f}, q1_ratio>{q1_ratio_min:.3f}, eic_corr>{eic_corr_min:.3f}",
        )
        # COMMENT `features` are missing
        # print(
        #     f"- Exported {c} MS2 features for {len(features) - skip} precursors. Average peaks/feature is {c / (len(features) - skip + 0.000000001):.0f}"
        # )
        print(
            f"- Skipped {skip} features because no MS2 peaks were left after filtering.",
        )
