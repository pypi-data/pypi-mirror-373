"""
_import.py

This module provides data import functionality for mass spectrometry files.
It handles loading and processing of various mass spectrometry file formats
including mzML, vendor formats (WIFF, RAW).

Key Features:
- **Multi-Format Support**: Load mzML, WIFF (SCIEX), and RAW (Thermo) files.
- **File Validation**: Check file existence and format compatibility.
- **Memory Management**: Support for on-disk and in-memory data handling.
- **Metadata Extraction**: Extract acquisition parameters and instrument information.
- **Error Handling**: Comprehensive error reporting for file loading issues.
- **Raw Data Processing**: Handle centroided and profile data with signal smoothing.

Dependencies:
- `pyopenms`: For standard mass spectrometry file format support.
- `polars` and `pandas`: For efficient data handling and manipulation.
- `numpy`: For numerical array operations.

Functions:
- `load()`: Main file loading function with format detection.
- `_load_mzML()`: Specialized mzML file loader.
- `_load_wiff()`: SCIEX WIFF file loader.
- `_load_raw()`: Thermo RAW file loader.

Supported File Formats:
- mzML (open standard format)
- WIFF (SCIEX vendor format)
- RAW (Thermo proprietary format)

See Also:
- `parameters._import_parameters`: For import-specific parameter configuration.
- `_export.py`: For data export functionality.
- `single.py`: For using imported data with ddafile class.

"""

import os
import warnings
from datetime import datetime

import numpy as np
import pandas as pd
import polars as pl
from tqdm import tqdm

from masster.chromatogram import Chromatogram
from masster.spectrum import Spectrum

# Import pyopenms with suppressed warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", message="Warning: OPENMS_DATA_PATH environment variable already exists.*", category=UserWarning)
    import pyopenms as oms


def load(
    self,
    filename=None,
    ondisk=False,
    type=None,
    label=None,
):
    """
    Load file content from a specified filename.
    Parameters:
        filename (str): The path to the file to load. The file must exist and have one of the following extensions:
                        .mzML, .wiff, or .raw.
        ondisk (bool, optional): Indicates whether the file should be treated as on disk. Defaults to False.
        type (str, optional): Specifies the type of file. If provided and set to 'ztscan' (case-insensitive), the file_type
                                attribute will be adjusted accordingly. Defaults to None.
        label (Any, optional): An optional label to associate with the loaded file. Defaults to None.
    Raises:
        FileNotFoundError: If the file specified by filename does not exist.
        ValueError: If the file extension is not one of the supported types (.mzML, .wiff, or .raw).
    Notes:
        The function determines the appropriate internal loading mechanism based on the file extension:
            - ".mzml": Calls _load_mzML(filename)
            - ".wiff": Calls _load_wiff(filename)
            - ".raw": Calls _load_raw(filename)
        After loading, the file_type attribute is set to 'dda', unless the optional 'type' parameter is provided as 'ztscan',
        in which case it is updated to 'ztscan'. The label attribute is updated if a label is provided.
    """

    if filename is None:
        filename = self.file_path
    filename = os.path.abspath(filename)
    if not os.path.exists(filename):
        raise FileNotFoundError("Filename not valid. Provide a valid file path.")
    self.ondisk = ondisk

    # check if file is mzML
    if filename.lower().endswith(".mzml"):
        self._load_mzML(filename)
    elif filename.lower().endswith(".wiff") or filename.lower().endswith(".wiff2"):
        self._load_wiff(filename)
    elif filename.lower().endswith(".raw"):
        self._load_raw(filename)
    elif filename.lower().endswith(".sample5"):
        self._load_sample5(filename)
    # elif filename.lower().endswith(".h5"):
    #    self._load_h5(filename)
    else:
        raise ValueError("File must be .mzML, .wiff, *.raw, or .sample5")

    self.file_type = "dda"
    if type is not None and type.lower() in ["ztscan"]:
        self.file_type = "ztscan"

    if label is not None:
        self.label = label


def load_noms1(
    self,
    filename=None,
    ondisk=False,
    type=None,
    label=None,
):
    """
    Optimized load method that skips loading ms1_df for better performance.

    This method is identical to load() but uses _load_sample5_study() for .sample5 files,
    which skips reading the potentially large ms1_df dataset to improve throughput when
    adding samples to studies or when MS1 spectral data is not needed.

    Args:
        filename (str, optional): The path to the file to load. If None, uses self.file_path.
        ondisk (bool, optional): Whether to load on-disk or in-memory. Defaults to False.
        type (str, optional): Override file type detection. Can be "ztscan". Defaults to None.
        label (str, optional): Override sample label. Defaults to None.

    Raises:
        FileNotFoundError: If the specified file doesn't exist.
        ValueError: If the file format is not supported.

    Notes:
        - Only affects .sample5 files (uses _load_sample5_study instead of _load_sample5)
        - Other file formats (.mzML, .wiff, .raw) are loaded normally
        - Sets ms1_df = None for .sample5 files to save memory and loading time
        - Recommended when MS1 spectral data is not needed (e.g., study workflows, feature-only analysis)
    """
    if filename is None:
        filename = self.file_path
    filename = os.path.abspath(filename)
    if not os.path.exists(filename):
        raise FileNotFoundError("Filename not valid. Provide a valid file path.")
    self.ondisk = ondisk

    # check if file is mzML
    if filename.lower().endswith(".mzml"):
        self._load_mzML(filename)
    elif filename.lower().endswith(".wiff") or filename.lower().endswith(".wiff2"):
        self._load_wiff(filename)
    elif filename.lower().endswith(".raw"):
        self._load_raw(filename)
    elif filename.lower().endswith(".sample5"):
        self._load_sample5_study(filename)  # Use optimized version for study loading
    else:
        raise ValueError("File must be .mzML, .wiff, *.raw, or .sample5")

    self.file_type = "dda"
    if type is not None and type.lower() in ["ztscan"]:
        self.file_type = "ztscan"

    if label is not None:
        self.label = label


# Backward compatibility alias
def load_study(
    self,
    filename=None,
    ondisk=False,
    type=None,
    label=None,
):
    """
    Backward compatibility alias for load_noms1().

    This method is deprecated. Use load_noms1() instead.
    """
    return self.load_noms1(filename=filename, ondisk=ondisk, type=type, label=label)


def _load_mzML(
    self,
    filename=None,
):
    """
    Load an mzML file and process its spectra.
    This method loads an mzML file (if a filename is provided, it will update the internal file path) using either an on-disk or in-memory MS experiment depending on the object's "ondisk" flag. It then iterates over all the spectra in the experiment:
        - For MS level 1 spectra, it increments a cycle counter and creates a polars DataFrame containing the retention time, m/z values, and intensity values.
        - For higher MS level spectra, it processes precursor-related information such as precursor m/z, isolation window offsets, intensity, and activation energy.
    Each spectrum is further processed by computing its baseline, denoising based on the baseline, and extracting various scan properties (such as TIC, minimum/maximum intensity, m/z bounds, etc.). This scan information is appended to a list.
    After processing all spectra, the method consolidates the collected scan data into a polars DataFrame with an explicit schema. It also assigns the on-disk/in-memory experiment object and corresponding file interface to instance attributes. The method sets a label based on the file basename, and, unless the scan type is 'ztscan', calls an additional analysis routine (analyze_dda).
    Parameters:
        filename (str, optional): The path to the mzML file to load. If None, the existing file path attribute is used.
    Returns:
        None
    Side Effects:
        - Updates self.file_path if a new filename is provided.
        - Loads and stores the MS experiment in self.file_obj.
        - Sets self.file_interface to the string 'oms'.
        - Stores the processed scan data in self.scans_df.
        - Maintains MS1-specific data in self.ms1_df.
        - Updates the instance label based on the loaded file's basename.
        - Invokes the analyze_dda method if the scan type is not 'ztscan'.
    """
    # check if filename exists
    if filename is None:
        raise ValueError("Filename must be provided.")

    filename = os.path.abspath(filename)
    # check if it exists
    if not os.path.exists(filename):
        raise FileNotFoundError(f"File {filename} not found.")
    if filename is not None:
        self.file_path = filename
        self.file_source = filename

    self.logger.info(f"Loading {filename}")

    omsexp: oms.OnDiscMSExperiment | oms.MSExperiment
    if self.ondisk:
        omsexp = oms.OnDiscMSExperiment()
        self.file_obj = omsexp
    else:
        omsexp = oms.MSExperiment()
        oms.MzMLFile().load(self.file_path, omsexp)
        self.file_obj = omsexp

    scans = []
    cycle = 0
    schema = {
        "cycle": pl.Int32,
        "scan_uid": pl.Int64,
        "rt": pl.Float64,
        "mz": pl.Float64,
        "inty": pl.Float64,
    }
    # create a polars DataFrame with explicit schema: cycle: int, rt: float, mz: float, intensity: float
    ms1_df = pl.DataFrame(
        {"cycle": [], "scan_uid": [], "rt": [], "mz": [], "inty": []},
        schema=schema,
    )

    tdqm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]
    # iterate over all spectra
    for i, s in tqdm(
        enumerate(omsexp.getSpectra()),  # type: ignore[union-attr]
        total=omsexp.getNrSpectra(),
        desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Scans",
        disable=tdqm_disable,
    ):
        # create a dict
        if s.getMSLevel() == 1:
            cycle += 1
            prec_mz = None
            precursorIsolationWindowLowerMZ = None
            precursorIsolationWindowUpperMZ = None
            prec_intyensity = None
            energy = None
        else:
            prec_mz = s.getPrecursors()[0].getMZ()
            precursorIsolationWindowLowerMZ = s.getPrecursors()[
                0
            ].getIsolationWindowLowerOffset()
            precursorIsolationWindowUpperMZ = s.getPrecursors()[
                0
            ].getIsolationWindowUpperOffset()
            prec_intyensity = s.getPrecursors()[0].getIntensity()
            # Try to get collision energy from meta values first, fallback to getActivationEnergy()
            try:
                energy = s.getPrecursors()[0].getMetaValue("collision energy")
                if energy is None or energy == 0.0:
                    energy = s.getPrecursors()[0].getActivationEnergy()
            except Exception:
                energy = s.getPrecursors()[0].getActivationEnergy()

        peaks = s.get_peaks()
        spect = Spectrum(mz=peaks[0], inty=peaks[1], ms_level=s.getMSLevel())

        bl = spect.baseline()
        spect = spect.denoise(threshold=bl)

        if spect.ms_level == 1:
            mz = np.array(spect.mz)
            median_diff = np.median(np.diff(np.sort(mz))) if mz.size > 1 else None

            if median_diff is not None and median_diff < 0.01:
                spect = spect.centroid(
                    tolerance=self.parameters.mz_tol_ms1_da,
                    ppm=self.parameters.mz_tol_ms1_ppm,
                    min_points=self.parameters.centroid_min_points_ms1,
                )

        newscan = {
            "scan_uid": i,
            "cycle": cycle,
            "ms_level": int(s.getMSLevel()),
            "rt": s.getRT(),
            "inty_tot": spect.tic(),
            "inty_min": spect.inty_min(),
            "inty_max": spect.inty_max(),
            "bl": bl,
            "mz_min": spect.mz_min(),
            "mz_max": spect.mz_max(),
            "comment": s.getComment(),
            "name": s.getName(),
            "id": s.getNativeID(),
            "prec_mz": prec_mz,
            "prec_mz_min": precursorIsolationWindowLowerMZ,
            "prec_mz_max": precursorIsolationWindowUpperMZ,
            "prec_inty": prec_intyensity,
            "energy": energy,
            "feature_uid": -1,
        }

        scans.append(newscan)

        if s.getMSLevel() == 1 and len(peaks) > 0:
            newms1_df = pl.DataFrame(
                {
                    "cycle": cycle,
                    "scan_uid": i,
                    "rt": s.getRT(),
                    "mz": spect.mz,
                    "inty": spect.inty,
                },
                schema=schema,
            )
            ms1_df = pl.concat([ms1_df, newms1_df])

    # convert to polars DataFrame with explicit schema and store in self.scans_df
    self.scans_df = pl.DataFrame(
        scans,
        schema={
            "scan_uid": pl.Int64,
            "cycle": pl.Int64,
            "ms_level": pl.Int64,
            "rt": pl.Float64,
            "inty_tot": pl.Float64,
            "inty_min": pl.Float64,
            "inty_max": pl.Float64,
            "bl": pl.Float64,
            "mz_min": pl.Float64,
            "mz_max": pl.Float64,
            "comment": pl.Utf8,
            "name": pl.Utf8,
            "id": pl.Utf8,
            "prec_mz": pl.Float64,
            "prec_mz_min": pl.Float64,
            "prec_mz_max": pl.Float64,
            "prec_inty": pl.Float64,
            "energy": pl.Float64,
            "feature_uid": pl.Int64,
        },
        infer_schema_length=None,
    )
    self.file_interface = "oms"
    self.ms1_df = ms1_df
    self.label = os.path.basename(filename)
    if self.file_type != "ztscan":
        self.analyze_dda()


def _load_raw(
    self,
    filename=None,
):
    """
    Load and process raw spectral data from the given file.
    This method reads a Thermo raw file (with '.raw' extension) by utilizing the ThermoRawData class from
    the alpharaw.thermo module. It validates the filename, checks for file existence, and then imports and processes
    the raw data. The method performs the following tasks:
        - Converts retention times (rt) from minutes to seconds and rounds them to 4 decimal places.
        - Iterates over each spectrum in the raw data and constructs a list of scan dictionaries.
        - For MS level 1 scans, performs centroiding if peaks with intensities > 0 after denoising.
        - Creates a Polars DataFrame for all scans (self.scans_df) with detailed spectrum information.
        - Aggregates MS1 spectrum peak data into a separate Polars DataFrame (self.ms1_df).
        - Sets additional attributes such as file path, raw data object, interface label, and file label.
        - Calls the analyze_dda method for further processed data analysis.
    Parameters:
        filename (str): The path to the raw data file. Must end with ".raw".
    Raises:
        ValueError: If the provided filename does not end with ".raw".
        FileNotFoundError: If the file specified by filename does not exist.
    Side Effects:
        - Populates self.scans_df with scan data in a Polars DataFrame.
        - Populates self.ms1_df with MS1 scan data.
        - Updates instance attributes including self.file_path, self.file_obj, self.file_interface, and self.label.
        - Initiates further analysis by invoking analyze_dda().
    """
    from alpharaw.thermo import ThermoRawData

    if not filename:
        raise ValueError("Filename must be provided.")

    filename = os.path.abspath(filename)
    # check if it exists
    if not os.path.exists(filename):
        raise FileNotFoundError(f"File {filename} not found.")

    raw_data = ThermoRawData(centroided=False)
    raw_data.keep_k_peaks_per_spec = self.parameters.max_points_per_spectrum
    # check thatupdat filename ends with .raw
    if not filename.endswith(".raw"):
        raise ValueError("filename must end with .raw")
    # check that the file exists
    if not os.path.exists(filename):
        raise FileNotFoundError(f"File {filename} not found.")
    self.logger.info(f"Loading {filename}")
    raw_data.import_raw(filename)
    specs = raw_data.spectrum_df
    # convert rt from minutes to seconds, round to 4 decimal places
    specs.rt = specs.rt * 60
    # TODO this should be an external param
    specs.rt = specs.rt.round(4)

    scans = []
    cycle = 0
    schema = {
        "cycle": pl.Int32,
        "scan_uid": pl.Int64,
        "rt": pl.Float64,
        "mz": pl.Float64,
        "inty": pl.Float64,
    }
    # create a polars DataFrame with explicit schema: cycle: int, rt: float, mz: float, intensity: float
    ms1_df = pl.DataFrame(
        {"cycle": [], "scan_uid": [], "rt": [], "mz": [], "inty": []},
        schema=schema,
    )
    # iterate over rows of specs
    tdqm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]
    for i, s in tqdm(
        specs.iterrows(),
        total=len(specs),
        desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Scans",
        disable=tdqm_disable,
    ):
        # create a dict
        if s["ms_level"] == 1:
            cycle += 1
            prec_mz = None
            precursorIsolationWindowLowerMZ = None
            precursorIsolationWindowUpperMZ = None
            prec_intyensity = None
            energy = None
        else:
            prec_mz = s["precursor_mz"]
            precursorIsolationWindowLowerMZ = s["isolation_lower_mz"]
            precursorIsolationWindowUpperMZ = s["isolation_upper_mz"]
            prec_intyensity = None
            energy = s["nce"]

        peak_start_idx = s["peak_start_idx"]
        peak_stop_idx = s["peak_stop_idx"]
        peaks = raw_data.peak_df.loc[peak_start_idx : peak_stop_idx - 1]
        spect = Spectrum(
            mz=peaks.mz.values,
            inty=peaks.intensity.values,
            ms_level=s["ms_level"],
        )
        # remove peaks with intensity <= 0

        bl = spect.baseline()
        spect = spect.denoise(threshold=bl)

        if spect.ms_level == 1:
            # Use the same logic as mzML loading
            mz = np.array(spect.mz)
            median_diff = np.median(np.diff(np.sort(mz))) if mz.size > 1 else None

            if median_diff is not None and median_diff < 0.01:
                spect = spect.centroid(
                    tolerance=self.parameters.mz_tol_ms1_da,
                    ppm=self.parameters.mz_tol_ms1_ppm,
                    min_points=self.parameters.centroid_min_points_ms1,
                )
        newscan = {
            "scan_uid": i,
            "cycle": cycle,
            "ms_level": int(s["ms_level"]),
            "rt": s["rt"],
            "inty_tot": spect.tic(),
            "inty_min": spect.inty_min(),
            "inty_max": spect.inty_max(),
            "bl": bl,
            "mz_min": spect.mz_min(),
            "mz_max": spect.mz_max(),
            "comment": "",
            "name": "",
            "id": "",
            "prec_mz": prec_mz,
            "prec_mz_min": precursorIsolationWindowLowerMZ,
            "prec_mz_max": precursorIsolationWindowUpperMZ,
            "prec_inty": prec_intyensity,
            "energy": energy,
            "feature_uid": -1,
        }

        scans.append(newscan)

        if s["ms_level"] == 1 and len(peaks) > 0:
            newms1_df = pl.DataFrame(
                {
                    "cycle": cycle,
                    "scan_uid": i,
                    "rt": s["rt"],
                    "mz": spect.mz,
                    "inty": spect.inty,
                },
                schema=schema,
            )
            ms1_df = pl.concat([ms1_df, newms1_df])

    # convert to polars DataFrame with explicit schema and store in self.scans_df
    self.scans_df = pl.DataFrame(
        scans,
        schema={
            "scan_uid": pl.Int64,
            "cycle": pl.Int64,
            "ms_level": pl.Int64,
            "rt": pl.Float64,
            "inty_tot": pl.Float64,
            "inty_min": pl.Float64,
            "inty_max": pl.Float64,
            "bl": pl.Float64,
            "mz_min": pl.Float64,
            "mz_max": pl.Float64,
            "comment": pl.Utf8,
            "name": pl.Utf8,
            "id": pl.Utf8,
            "prec_mz": pl.Float64,
            "prec_mz_min": pl.Float64,
            "prec_mz_max": pl.Float64,
            "prec_inty": pl.Float64,
            "energy": pl.Float64,
            "feature_uid": pl.Int64,
        },
        infer_schema_length=None,
    )
    self.file_path = filename
    self.file_source = filename
    self.file_obj = raw_data
    self.file_interface = "alpharaw"
    self.label = os.path.basename(filename)
    self.ms1_df = ms1_df
    self.analyze_dda()


def _load_wiff(
    self,
    filename=None,
):
    try:
        # Use masster's own implementation first
        from masster.sample.sciex import SciexWiffData as MassterSciexWiffData

        SciexWiffDataClass = MassterSciexWiffData
    except ImportError:
        # Fallback to alpharaw if masster implementation fails
        from alpharaw.sciex import SciexWiffData as AlpharawSciexWiffData

        SciexWiffDataClass = AlpharawSciexWiffData

    if not filename:
        raise ValueError("Filename must be provided.")

    filename = os.path.abspath(filename)
    # check if it exists
    if not os.path.exists(filename):
        raise FileNotFoundError(f"File {filename} not found.")

    raw_data = SciexWiffDataClass(centroided=False)
    raw_data.keep_k_peaks_per_spec = self.parameters.max_points_per_spectrum

    if not filename.endswith(".wiff"):
        raise ValueError("filename must end with .wiff")
    if not os.path.exists(filename):
        raise FileNotFoundError(f"File {filename} not found.")

    self.logger.info(f"Loading {filename}")
    raw_data.import_raw(filename)

    specs = raw_data.spectrum_df
    specs.rt = specs.rt * 60
    specs.rt = specs.rt.round(4)

    algo = self.parameters.centroid_algo

    scans = []
    ms1_df_records = []
    cycle = 0
    schema = {
        "cycle": pl.Int32,
        "scan_uid": pl.Int64,
        "rt": pl.Float64,
        "mz": pl.Float64,
        "inty": pl.Float64,
    }

    # iterate over rows of specs
    tdqm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]
    for i, s in tqdm(
        specs.iterrows(),
        total=len(specs),
        desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Scans",
        disable=tdqm_disable,
    ):
        ms_level = s["ms_level"]
        if ms_level == 1:
            cycle += 1
            prec_mz = None
            precursorIsolationWindowLowerMZ = None
            precursorIsolationWindowUpperMZ = None
            prec_intyensity = None
            energy = None
        else:
            prec_mz = s["precursor_mz"]
            precursorIsolationWindowLowerMZ = s["isolation_lower_mz"]
            precursorIsolationWindowUpperMZ = s["isolation_upper_mz"]
            prec_intyensity = None
            energy = s["nce"]

        peak_start_idx = s["peak_start_idx"]
        peak_stop_idx = s["peak_stop_idx"]
        peaks = raw_data.peak_df.loc[peak_start_idx : peak_stop_idx - 1]
        spect = Spectrum(
            mz=peaks.mz.values,
            inty=peaks.intensity.values,
            ms_level=ms_level,
        )
        bl = spect.baseline()
        spect = spect.denoise(threshold=bl)
        if ms_level == 1:
            spect = spect.centroid(
                algo=algo,
                tolerance=self.parameters.mz_tol_ms1_da,
                ppm=self.parameters.mz_tol_ms1_ppm,
                min_points=self.parameters.centroid_min_points_ms1,
            )
        scans.append(
            {
                "scan_uid": i,
                "cycle": cycle,
                "ms_level": int(ms_level),
                "rt": s["rt"],
                "inty_tot": spect.tic(),
                "inty_min": spect.inty_min(),
                "inty_max": spect.inty_max(),
                "bl": bl,
                "mz_min": spect.mz_min(),
                "mz_max": spect.mz_max(),
                "comment": "",
                "name": "",
                "id": "",
                "prec_mz": prec_mz,
                "prec_mz_min": precursorIsolationWindowLowerMZ,
                "prec_mz_max": precursorIsolationWindowUpperMZ,
                "prec_inty": prec_intyensity,
                "energy": energy,
                "feature_uid": -1,
            },
        )

        if ms_level == 1 and len(peaks) > 0:
            # Use extend for all mz/int pairs at once
            ms1_df_records.extend(
                [
                    {
                        "cycle": cycle,
                        "scan_uid": i,
                        "rt": s["rt"],
                        "mz": mz,
                        "inty": inty,
                    }
                    for mz, inty in zip(spect.mz, spect.inty, strict=False)
                ],
            )

    # Create DataFrames in one go
    self.scans_df = pl.DataFrame(
        scans,
        schema={
            "scan_uid": pl.Int64,
            "cycle": pl.Int64,
            "ms_level": pl.Int64,
            "rt": pl.Float64,
            "inty_tot": pl.Float64,
            "inty_min": pl.Float64,
            "inty_max": pl.Float64,
            "bl": pl.Float64,
            "mz_min": pl.Float64,
            "mz_max": pl.Float64,
            "comment": pl.Utf8,
            "name": pl.Utf8,
            "id": pl.Utf8,
            "prec_mz": pl.Float64,
            "prec_mz_min": pl.Float64,
            "prec_mz_max": pl.Float64,
            "prec_inty": pl.Float64,
            "energy": pl.Float64,
            "feature_uid": pl.Int64,
        },
        infer_schema_length=None,
    )
    self.file_path = filename
    self.file_source = filename
    self.file_obj = raw_data
    self.file_interface = "alpharaw"
    self.label = os.path.basename(filename)
    self.ms1_df = pl.DataFrame(ms1_df_records, schema=schema)
    if self.file_type != "ztscan":
        self.analyze_dda()


def _load_featureXML(
    self,
    filename="features.featureXML",
):
    """
    Load feature data from a FeatureXML file.

    This method reads a FeatureXML file (defaulting to "features.featureXML") using the
    OMS library's FeatureXMLFile and FeatureMap objects. The loaded feature data is stored
    in the instance variable 'features'. The method then converts the feature data into a
    DataFrame, optionally excluding peptide identification data, and cleans it using the
    '__oms_clean_df' method, saving the cleaned DataFrame into 'features_df'.

    Parameters:
        filename (str): The path to the FeatureXML file to load. Defaults to "features.featureXML".

    Returns:
        None
    """
    fh = oms.FeatureXMLFile()
    fm = oms.FeatureMap()
    fh.load(filename, fm)
    self._oms_features_map = fm
    """if self.features_df is None:
        df = self._oms_features_map.get_df(export_peptide_identifications=False)
        df = self._clean_features_df(df)

        # desotope features
        df = self._features_deisotope(df, mz_tol=0.02, rt_tol=0.5)

        # update eic
        df["chrom"] = None
        mz_tol = 0.01
        rt_tol = 10
        # iterate over all rows in df
        for i, row in df.iterrows():
            # select data in ms1_df with mz in range [mz_start - mz_tol, mz_end + mz_tol] and rt in range [rt_start - rt_tol, rt_end + rt_tol]
            d = self.ms1_df.filter(
                (pl.col("rt") >= row["rt_start"] - rt_tol)
                & (pl.col("rt") <= row["rt_end"] + rt_tol)
                & (pl.col("mz") >= row["mz"] - mz_tol)
                & (pl.col("mz") <= row["mz"] + mz_tol)
            )
            # for all unique rt values, find the maximum inty
            eic_rt = d.group_by("rt").agg(pl.col("inty").max())
            if len(eic_rt) < 4:
                continue
            eic = Chromatogram(
                eic_rt["rt"].to_numpy(),
                eic_rt["inty"].to_numpy(),
                label=f"EIC mz={row['mz']:.4f}",
                feature_start=row["rt_start"],
                feature_end=row["rt_end"],
                feature_apex=row["rt"],
            ).find_peaks()
            # set eic in df
            df.at[i, "chrom"] = eic
            if len(eic.peak_widths) > 0:
                df.at[i, "chrom_coherence"] = round(eic.feature_coherence, 3)
                df.at[i, "chrom_prominence"] = round(
                    eic.peak_prominences[0], 3
                )  # eic.peak_prominences[0]
                df.at[i, "chrom_prominence_scaled"] = round(
                    eic.peak_prominences[0] / (np.mean(eic.inty) + 1e-10), 3
                )
                df.at[i, "chrom_height_scaled"] = round(
                    eic.peak_heights[0] / (np.mean(eic.inty) + 1e-10), 3
                )

        self.features_df = df"""


'''
def _load_mzpkl(
    self,
    filename="sample.mzpkl",
    ondisk=False,
):
    """
    Load the mzpkl data file, initialize the experiment attributes, and set up the file object.
    Parameters:
        filename (str, optional): The path to the .mzpkl file to be loaded. Defaults to "data.mzpkl".
        ondisk (bool, optional): A flag indicating whether the data should be loaded for on-disk usage.
                                    If True, self.ondisk is set to True and an OnDiscMSExperiment is used.
                                    Otherwise, an MSExperiment is used.
    Side Effects:
        - Decompresses and unpickles the specified file.
        - Sets attributes on self for each key in the loaded data dictionary, except for keys named 'format'.
        - Renames the attribute 'spectra_df' to 'scans_df' if present.
        - Initializes self.file_obj as either an OnDiscMSExperiment or MSExperiment based on the ondisk flag.
        - Checks for an associated featureXML file (with the same base name as the input file) and loads it if found.
    """

    if ondisk is True:
        self.ondisk = True

    with bz2.BZ2File(filename, "rb") as f:
        data = pickle.load(f)

    for k, v in data.items():
        if k in ["format"]:
            continue
        if k == "spectra_df":
            k = "scans_df"
        setattr(self, k, v)

    self.sanitize()

    if self.ondisk:
        self.file_obj = oms.OnDiscMSExperiment()
    else:
        self.file_obj = oms.MSExperiment()

    # check if *.featureXML exists
    featureXML = filename.replace(".mzpkl", ".featureXML")
    if os.path.exists(featureXML):
        self._load_featureXML(featureXML)

'''


def _wiff_to_dict(
    filename=None,
):
    from alpharaw.raw_access.pysciexwifffilereader import WillFileReader

    file_reader = WillFileReader(filename)
    number_of_samples = len(file_reader.sample_names)
    metadata = []
    for si in range(number_of_samples):
        sample_reader = file_reader._wiff_file.GetSample(si)
        number_of_exps = sample_reader.MassSpectrometerSample.ExperimentCount
        for ei in range(number_of_exps):
            exp_reader = sample_reader.MassSpectrometerSample.GetMSExperiment(ei)

            exp_info = exp_reader.GetMassSpectrumInfo(ei)

            # get the details of the experiment
            exp_name = exp_reader.Details.get_ExperimentName()
            exp_type = exp_reader.Details.get_ExperimentType()

            IDA_type = exp_reader.Details.get_IDAType()
            has_MRM_Pro_Data = exp_reader.Details.get_HasMRMProData()
            has_SMRM_Data = exp_reader.Details.get_HasSMRMData()
            is_swath = exp_reader.Details.get_IsSwath()
            has_dyn_fill_time = exp_reader.Details.get_HasDynamicFillTime()
            method_fill_time = exp_reader.Details.get_MethodFillTime()
            default_resolution = exp_reader.Details.get_DefaultResolution()
            parameters = exp_reader.Details.get_Parameters()
            targeted_compound_info = exp_reader.Details.get_TargetedCompoundInfo()
            source_type = exp_reader.Details.get_SourceType()
            raw_data_type = exp_reader.Details.get_RawDataType()

            number_of_scans = exp_reader.Details.get_NumberOfScans()
            scan_group = exp_reader.Details.get_ScanGroup()
            spectrum_type = exp_reader.Details.get_SpectrumType()
            saturatrion_threshold = exp_reader.Details.get_SaturationThreshold()
            polarity = exp_reader.Details.get_Polarity()
            mass_range_info = exp_reader.Details.get_MassRangeInfo()
            start_mass = exp_reader.Details.get_StartMass()
            end_mass = exp_reader.Details.get_EndMass()

            mslevel = exp_info.MSLevel
            if mslevel > 1:
                # get the precursor information
                parent_mz = exp_info.ParentMZ
                collision_energy = exp_info.CollisionEnergy
                parent_charge_state = exp_info.ParentChargeState
            else:
                parent_mz = None
                collision_energy = None
                parent_charge_state = None

            # create a dict with the details
            exp_dict = {
                "instrument_name": sample_reader.MassSpectrometerSample.get_InstrumentName(),
                "sample_id": si,
                "experiment_id": ei,
                "experiment_name": exp_name,
                "experiment_type": exp_type,
                "IDA_type": IDA_type,
                "has_MRM_Pro_Data": has_MRM_Pro_Data,
                "has_SMRM_Data": has_SMRM_Data,
                "is_swath": is_swath,
                "has_dyn_fill_time": has_dyn_fill_time,
                "method_fill_time": method_fill_time,
                "default_resolution": default_resolution,
                "parameters": parameters,
                "targeted_compound_info": targeted_compound_info,
                "source_type": source_type,
                "raw_data_type": raw_data_type,
                "number_of_scans": number_of_scans,
                "scan_group": scan_group,
                "spectrum_type": spectrum_type,
                "saturatrion_threshold": saturatrion_threshold,
                "polarity": polarity,
                "mass_range_info": mass_range_info,
                "start_mass": start_mass,
                "end_mass": end_mass,
                "mslevel": mslevel,
                "parent_mz": parent_mz,
                "collision_energy": collision_energy,
                "parent_charge_state": parent_charge_state,
            }
            metadata.append(exp_dict)
    # convert to pandas DataFrame
    metadata = pd.DataFrame(metadata)

    return metadata


def sanitize(self):
    # iterate over all rows in self.features_df
    if self.features_df is None:
        return
    for _i, row in self.features_df.iterrows():
        # check if chrom is not None
        if row["chrom"] is not None and not isinstance(row["chrom"], Chromatogram):
            # update chrom to a Chromatogram
            new_chrom = Chromatogram(rt=np.array([]), inty=np.array([]))
            new_chrom.from_dict(row["chrom"].__dict__)
            self.features_df.at[_i, "chrom"] = new_chrom
        if row["ms2_specs"] is not None:
            if isinstance(row["ms2_specs"], list):
                for _j, ms2_specs in enumerate(row["ms2_specs"]):
                    if not isinstance(ms2_specs, Spectrum):
                        new_ms2_specs = Spectrum(mz=np.array([0]), inty=np.array([0]))
                        new_ms2_specs.from_dict(ms2_specs.__dict__)
                        self.features_df.at[_i, "ms2_specs"][_j] = new_ms2_specs


def index_file(self):
    """
    Reload raw data from a file based on its extension.

    This method checks whether the file at self.file_path exists and determines
    the appropriate way to load it depending on its extension:
    - If the file ends with ".wiff", it uses the SciexWiffData class for import.
    - If the file ends with ".raw", it uses the ThermoRawData class for import.
    - If the file ends with ".mzml", it uses the MzMLFile loader with either
        an on-disk or in-memory MSExperiment based on the self.ondisk flag.

    It also sets the file interface and file object on the instance after successful
    import. Additionally, the number of peaks per spectrum is configured using the
    'max_points_per_spectrum' parameter from self.parameters.

    Raises:
            FileNotFoundError: If the file does not exist or has an unsupported extension.
    """
    # check if file_path exists and ends with .wiff
    if os.path.exists(self.file_source) and self.file_source.lower().endswith(".wiff"):
        self.file_interface = "alpharaw"
        try:
            from alpharaw.sciex import SciexWiffData
        except ImportError:
            # Fallback to masster's own implementation
            from masster.sample.sciex import SciexWiffData

        raw_data = SciexWiffData(centroided=False)
        raw_data.keep_k_peaks_per_spec = self.parameters.max_points_per_spectrum
        self.logger.info("Index raw data...")
        raw_data.import_raw(self.file_source)
        self.file_obj = raw_data
    elif os.path.exists(self.file_source) and self.file_source.lower().endswith(".raw"):
        self.file_interface = "alpharaw"
        from alpharaw.thermo import ThermoRawData

        raw_data = ThermoRawData(centroided=False)
        raw_data.keep_k_peaks_per_spec = self.parameters.get("max_points_per_spectrum")
        self.logger.info("Index raw data...")
        raw_data.import_raw(self.file_source)
        self.file_obj = raw_data
    elif os.path.exists(self.file_source) and self.file_source.lower().endswith(
        ".mzml",
    ):
        self.file_interface = "oms"
        omsexp: oms.OnDiscMSExperiment | oms.MSExperiment
        if self.ondisk:
            omsexp = oms.OnDiscMSExperiment()
            self.file_obj = omsexp
        else:
            omsexp = oms.MSExperiment()
            oms.MzMLFile().load(self.file_source, omsexp)
            self.file_obj = omsexp
    elif os.path.exists(self.file_source) and self.file_source.lower().endswith(
        ".sample5",
    ):
        # this is an old save, try to see if
        if os.path.exists(self.file_source.replace(".sample5", ".wiff")):
            self.set_source(self.file_source.replace(".sample5", ".wiff"))
        elif os.path.exists(self.file_source.replace(".sample5", ".raw")):
            self.set_source(self.file_source.replace(".sample5", ".raw"))
        elif os.path.exists(self.file_source.replace(".sample5", ".mzml")):
            self.set_source(self.file_source.replace(".sample5", ".mzml"))
        else:
            raise FileNotFoundError(
                f"File {self.file_source} not found. Did the path change? Consider running source().",
            )
        self.index_file()
    else:
        raise FileNotFoundError(
            f"File {self.file_source} not found. Did the path change? Consider running source().",
        )


def _load_ms2data(
    self,
    scans=None,
):
    # reads all ms2 data from the file object and returns a polars DataFrame

    # check if file_obj is set
    if self.file_obj is None:
        return
    # check if scan_uid is set
    if scans is None:
        scans = self.scans_df["scan_uid"].to_list()
    if len(scans) == 0:
        scans = self.scans_df["scan_uid"].to_list()

    # check the file interface
    if self.file_interface == "oms":
        _load_ms2data(self, scans=scans)
    elif self.file_interface == "alpharaw":
        _load_ms2data_alpharaw(self, scan_uid=scans)

    return


def _load_ms2data_alpharaw(
    self,
    scan_uid=None,
):
    # reads all ms data from the file object and returns a polars DataFrame

    # TODO not used
    ms2data = None
    scan_uid = self.scans_df["scan_uid"].to_list() if scan_uid is None else scan_uid
    self.logger.info(f"Loading MS2 data for {len(scan_uid)} scans...")
    # keep only scans with ms_level == 2
    if self.file_obj is None:
        return

    raw_data = self.file_obj
    scans = raw_data.spectrum_df
    # scans.rt = scans.rt * 60
    scans.rt = scans.rt.round(4)

    schema = {
        "scan_uid": pl.Int64,
        "rt": pl.Float64,
        "prec_mz": pl.Float64,
        "mz": pl.Float64,
        "inty": pl.Float64,
    }
    # create a polars DataFrame with explicit schema: cycle: int, rt: float, mz: float, intensity: float
    ms2data = pl.DataFrame(
        {"scan_uid": [], "rt": [], "prec_mz": [], "mz": [], "inty": []},
        schema=schema,
    )
    # iterate over rows of specs
    tdqm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]
    for i, s in tqdm(
        scans.iterrows(),
        total=len(scans),
        desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Centroid",
        disable=tdqm_disable,
    ):
        # create a dict
        if s["ms_level"] == 2:
            prec_mz = s["precursor_mz"]
            peak_start_idx = s["peak_start_idx"]
            peak_stop_idx = s["peak_stop_idx"]
            peaks = raw_data.peak_df.loc[peak_start_idx : peak_stop_idx - 1]
            spect = Spectrum(
                mz=peaks.mz.values,
                inty=peaks.intensity.values,
                ms_level=s["ms_level"],
                centroided=False,
            )
            # remove peaks with intensity <= 0
            bl = spect.baseline()
            spect = spect.denoise(threshold=bl)

            if len(peaks) > 0:
                newms2data = pl.DataFrame(
                    {
                        "scan_uid": i,
                        "rt": s["rt"],
                        "prec_mz": prec_mz,
                        "mz": spect.mz,
                        "inty": spect.inty,
                    },
                    schema=schema,
                )
                ms2data = pl.concat([ms2data, newms2data])
    self.ms2data = ms2data


# TODO this should go to chrom?
def chrom_extract(
    self,
    rt_tol=6.0,
    mz_tol=0.005,
):
    """
    Extracts MRM (Multiple Reaction Monitoring) and EIC (Extracted Ion Chromatogram) data from the file object.

    This method processes the `chrom_df` DataFrame, identifying relevant scans in `scans_df` and extracting chromatograms
    for MS1, MRM, and MS2 traces. It updates `chrom_df` with scan IDs and extracted chromatogram objects.

    Parameters:
        rt_tol (float, optional): Retention time tolerance for scan selection. Defaults to RtParameters().rt_tol.
        mz_tol (float, optional): m/z tolerance for scan selection. Defaults to MzParameters().mz_tol_ms1_da.

    Returns:
        None: Updates self.chrom_df in place with extracted chromatogram data.
    """
    if self.file_obj is None:
        return

    if self.chrom_df is None:
        return

    # check if mrm_df is dict, if so convert to DataFrame
    chrom_df = self.chrom_df

    chrom_df["scan_uid"] = None
    chrom_df["chrom"] = None
    scan_uid = []

    # iterate over all mrms and identidy the scans
    for i, trace in chrom_df.iterrows():
        if trace["type"] in ["ms1"]:
            rt = trace["rt"]
            rt_start = trace["rt_start"]
            if rt_start is None:
                rt_start = rt - 3
            rt_end = trace["rt_end"]
            if rt_end is None:
                rt_end = rt + 3
            # TODO not used
            q1 = trace["prec_mz"]
            # find all rows in self.scans_df that have rt between rt_start-rt_tol and rt_end+rt_tol and mz between q1-mz_tol and q1+mz_tol
            mask = (
                (self.scans_df["rt"] >= rt_start - rt_tol)
                & (self.scans_df["rt"] <= rt_end + rt_tol)
                & (self.scans_df["ms_level"] == 1)
            )
            scans_df = self.scans_df.filter(mask)
            scan_ids = scans_df["scan_uid"].to_list()
            scan_uid.extend(scan_ids)
            chrom_df.at[i, "scan_uid"] = scan_ids

        elif trace["type"] in ["mrm", "ms2"]:
            rt = trace["rt"]
            rt_start = trace["rt_start"]
            if rt_start is None:
                rt_start = rt - 3
            rt_end = trace["rt_end"]
            if rt_end is None:
                rt_end = rt + 3
            q1 = trace["prec_mz"]
            # find all rows in self.scans_df that have rt between rt_start-rt_tol and rt_end+rt_tol and mz between q1-mz_tol and q1+mz_tol
            mask = (
                (self.scans_df["rt"] >= rt_start - rt_tol)
                & (self.scans_df["rt"] <= rt_end + rt_tol)
                & (self.scans_df["ms_level"] == 2)
                & (self.scans_df["prec_mz"] >= q1 - 5)
                & (self.scans_df["prec_mz"] <= q1 + 5)
            )
            scans_df = self.scans_df.filter(mask)
            # find the closes prec_mz to q1
            if scans_df.is_empty():
                continue
            # find the closest prec_mz to q1
            # sort by abs(prec_mz - q1) and take the first row
            # this is the closest precursor m/z to q1
            closest_prec_mz = scans_df.sort(abs(pl.col("prec_mz") - q1)).select(
                pl.col("prec_mz").first(),
            )
            # keep only the scans with prec_mz within mz_tol of closest_prec_mz
            scans_df = scans_df.filter(
                (pl.col("prec_mz") >= closest_prec_mz["prec_mz"][0] - 0.2)
                & (pl.col("prec_mz") <= closest_prec_mz["prec_mz"][0] + 0.2),
            )

            scan_ids = scans_df["scan_uid"].to_list()
            scan_uid.extend(scan_ids)
            chrom_df.at[i, "scan_uid"] = scan_ids

    # get the ms2data
    _load_ms2data(self, scans=list(set(scan_uid)) if scan_uid else None)
    tdqm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]

    for i, trace in tqdm(
        chrom_df.iterrows(),
        total=len(chrom_df),
        desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Extract EICs",
        disable=tdqm_disable,
    ):
        if trace["type"] in ["ms1"]:
            q1 = trace["prec_mz"]
            name = trace["name"]
            scan_uid = trace["scan_uid"]
            # find all ms1 data with scan_uid and mz between q1-mz_tol and q1+mz_tol
            d = self.ms1_df.filter(
                (pl.col("scan_uid").is_in(scan_uid))
                & (pl.col("mz") >= q1 - mz_tol)
                & (pl.col("mz") <= q1 + mz_tol),
            )
            # for all unique rt values, find the maximum inty
            eic_rt = d.group_by("rt").agg(pl.col("inty").max())
            eic = Chromatogram(
                eic_rt["rt"].to_numpy(),
                inty=eic_rt["inty"].to_numpy(),
                label=f"MS1 {name} ({q1:0.3f})",
                lib_rt=trace["rt"],
            )
            chrom_df.at[i, "chrom"] = eic

        elif trace["type"] in ["mrm", "ms2"]:
            q1 = trace["prec_mz"]
            q3 = trace["prod_mz"]
            name = trace["name"]
            scan_uid = trace["scan_uid"]
            # find all ms2 data with scan_uid and mz between q3-mz_tol and q3+mz_tol
            d = self.ms2data.filter(
                (pl.col("scan_uid").is_in(scan_uid))
                & (pl.col("mz") >= q3 - mz_tol)
                & (pl.col("mz") <= q3 + mz_tol),
            )
            # for all unique rt values, find the maximum inty
            eic_rt = d.group_by("rt").agg(pl.col("inty").max())
            eic = Chromatogram(
                eic_rt["rt"].to_numpy(),
                inty=eic_rt["inty"].to_numpy(),
                label=f"MRM {name} ({q1:0.3f}>{q3:0.3f})",
                lib_rt=trace["rt"],
            )
            chrom_df.at[i, "chrom"] = eic

    self.chrom_df = chrom_df


# TODO no self?
def _oms_clean_df(self, df):
    df2 = df[df["quality"] != 0]
    # change columns and order
    df = pd.DataFrame(
        columns=[
            "feature_uid",
            "uid",
            "mz",
            "rt",
            "rt_start",
            "rt_end",
            "rt_delta",
            "mz_start",
            "mz_end",
            "inty",
            "quality",
            "charge",
            "iso",
            "iso_of",
            "chrom",
            "chrom_coherence",
            "chrom_prominence",
            "chrom_prominence_scaled",
            "chrom_height_scaled",
            "ms2_scans",
            "ms2_specs",
        ],
    )

    # set values of fid to 0:len(df)
    df["uid"] = df2.index.to_list()
    df["mz"] = (df2["mz"]).round(5)
    df["rt"] = (df2["RT"]).round(3)
    df["rt_start"] = (df2["RTstart"]).round(3)
    df["rt_end"] = (df2["RTend"]).round(3)
    df["rt_delta"] = (df2["RTend"] - df2["RTstart"]).round(3)
    df["mz_start"] = (df2["MZstart"]).round(5)
    df["mz_end"] = (df2["MZend"]).round(5)  # df2["MZend"]
    df["inty"] = df2["intensity"]
    df["quality"] = df2["quality"]
    df["charge"] = df2["charge"]
    df["iso"] = 0
    df["iso_of"] = None
    df["chrom"] = None
    df["chrom_coherence"] = None
    df["chrom_prominence"] = None
    df["chrom_prominence_scaled"] = None
    df["chrom_height_scaled"] = None
    df["ms2_scans"] = None
    df["ms2_specs"] = None
    df["feature_uid"] = range(1, len(df) + 1)
    # df.set_index('fid', inplace=True)
    # rests index
    # df.reset_index(drop=True, inplace=True)

    return df
