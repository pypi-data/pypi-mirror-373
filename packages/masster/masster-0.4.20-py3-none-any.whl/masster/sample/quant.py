# a module for the reproducible quantification of EIC traces.
# it takes a study and a list of features indicated either as MS1 or MRM features
import os

import pandas as pd

# from .parameters import QuantParameters
# Parameters removed - using hardcoded defaults


def chrom_from_csv(
    self,
    filename=None,
):
    """
    Load MRM transitions from a file.
    :param filename: Path to the file containing MRM transitions.
    :return: List of MRM transitions
    """

    # if filename exists and ends with csv, read it as a CSV file
    if filename and filename.endswith(".csv"):
        df = pd.read_csv(filename, comment="#")
        # possible columns are name, class, q1, q3, rt, istd. Make sure to handle upper and lower case.
        df.columns = [col.lower() for col in df.columns]
        if "name" not in df.columns:
            raise ValueError("CSV file must contain a 'name' column.")
        if "q1" in df.columns:
            col_q1 = "q1"
        elif "precursor" in df.columns:
            col_q1 = "precursor"
        elif "precursor_mz" in df.columns:
            col_q1 = "precursor_mz"
        else:
            raise ValueError("CSV file must contain a 'q1' column or equivalent.")
        if "q3" in df.columns:
            col_q3 = "q3"
        elif "product" in df.columns:
            col_q3 = "product"
        elif "product_mz" in df.columns:
            col_q3 = "product_mz"
        else:
            col_q3 = None
        col_rt = "rt" if "rt" in df.columns else None
        col_istd = "istd" if "istd" in df.columns else None
        col_class = "class" if "class" in df.columns else None
        col_adduct = "adduct" if "adduct" in df.columns else None
        col_qid = "qid" if "qid" in df.columns else None
        col_group = "group" if "group" in df.columns else None
        col_formula = "formula" if "formula" in df.columns else None
        col_inchikey = "inchikey" if "inchikey" in df.columns else None
        col_smiles = "smiles" if "smiles" in df.columns else None

        traces = []
        for _, row in df.iterrows():
            traces.append({
                "chid": row[col_qid],
                "type": "mrm",
                "name": row["name"],
                "group": row[col_group],
                "prec_mz": row[col_q1],
                "prod_mz": row[col_q3] if col_q3 else None,
                "rt": row[col_rt],
                "rt_start": None,
                "rt_end": None,
                "istd": row[col_istd] if col_istd else None,
                "adduct": row[col_adduct] if col_adduct else None,
                "class": row[col_class] if col_class else None,
                "formula": row[col_formula] if col_formula else None,
                "inchikey": row[col_inchikey] if col_inchikey else None,
                "smiles": row[col_smiles] if col_smiles else None,
            })
        self.chrom_df = pd.DataFrame(traces)
        return


def chrom_from_oracle(
    self,
    oracle_folder=None,
    classes=None,
    level=None,
):
    if level is None:
        level = [2]
    if oracle_folder is None:
        return
    # try to read the annotationfile as a csv file and add it to feats
    try:
        oracle_data = pd.read_csv(
            os.path.join(oracle_folder, "diag", "annotation_full.csv"),
        )
    except:
        print(f"Could not read {oracle_folder}/diag/annotation_full.csv")
        return

    # if classes is not None, filter the oracle_data by classe
    traces = []

    cols_to_keep = [
        "mz",
        "rt",
        "level",
        "formula",
        "ion",
        "name",
        "hg",
        "ms2_matched",
        "ms2_missed",
    ]

    qid = 0
    oracle_data = oracle_data[cols_to_keep]
    # keep only MS2 features
    oracle_data["lib_frags"] = None
    for i, row in oracle_data.iterrows():
        if row["level"] in level:
            if classes is not None and row["hg"] not in classes:
                continue
        if row["level"] == 2:
            frags = {}
            if row["ms2_matched"] is not None:
                if isinstance(row["ms2_matched"], str):
                    # split the ms2_matched column by semicolon
                    tokens = row["ms2_matched"].split("  ")
                    for token in tokens:
                        if token.strip():
                            frag = token.split("|")
                            if len(frag) > 1:
                                # add to dictionary with frag[2] as key and frag[1] as value
                                frags[frag[1]] = float(frag[0])
            if row["ms2_missed"] is not None:
                if isinstance(row["ms2_missed"], str):  # frag[0]
                    tokens = row["ms2_missed"].split("  ")
                    for token in tokens:
                        if token.strip():
                            frag = token.split("|")
                            if len(frag) > 1:
                                # add to dictionary with frag[2] as key and frag[1] as value
                                frags[frag[1]] = float(frag[0])
            if len(frags) > 0:
                oracle_data.at[i, "lib_frags"] = frags
                for _key, value in frags.items():
                    # add the fragment to the row
                    traces.append({
                        "chid": qid,
                        "type": "mrm",
                        "name": row["name"] + " " + row["ion"],
                        "group": row["name"] + " " + row["ion"],
                        "prec_mz": row["mz"],
                        "prod_mz": value,
                        "rt": row["rt"],
                        "rt_start": None,
                        "rt_end": None,
                        "istd": None,
                        "adduct": row["ion"],
                        "class": row["hg"],
                        "formula": row["formula"],
                        "inchikey": None,
                        "smiles": None,
                    })
                    qid += 1
    self.chrom_df = pd.DataFrame(traces)
    return


def chrom_from_features(
    self,
    feature_uid=None,
):
    """
    Create a chromatogram from features.
    :param feature_uid: Feature UID to create the chromatogram for. If None, create chromatograms for all features.
    :return: None
    """
    traces = []
    chid = 0

    if feature_uid is None:
        feature_uid = self.features_df["feature_uid"].unique()
    else:
        # ensure feature_uid is a list
        if not isinstance(feature_uid, list | tuple):
            feature_uid = [feature_uid]

    for _i, row in self.features_df.iterrows():
        if row["feature_uid"] not in feature_uid:
            continue

        traces.append({
            "chid": chid,
            "type": "ms1",
            "name": f"MS1 fid:{row['feature_uid']} ({row['mz']:.4f})",
            "group": f"fid:{row['feature_uid']}",
            "prec_mz": row["mz"],
            "prod_mz": None,
            "rt": row["rt"],
            "rt_start": row["rt_start"],
            "rt_end": row["rt_end"],
            "istd": None,
            "adduct": None,
            "class": None,
            "formula": None,
            "inchikey": None,
            "smiles": None,
        })
        chid += 1

    self.chrom_df = pd.DataFrame(traces)
    return
