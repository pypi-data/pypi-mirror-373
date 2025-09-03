from __future__ import annotations


from datetime import datetime
import numpy as np
import polars as pl
import pyopenms as oms

from tqdm import tqdm

from masster.spectrum import Spectrum
from .defaults.find_features_def import find_features_defaults
from .defaults.find_ms2_def import find_ms2_defaults
from .defaults.get_spectrum_def import get_spectrum_defaults


from masster.chromatogram import Chromatogram


def get_spectrum(self, scan, **kwargs):
    """Retrieve a single spectrum and optionally post-process it.

    The function locates the requested scan in ``self.scans_df`` and returns a
    :class:`Spectrum` object. Processing steps (centroiding, deisotoping,
    trimming and optional DIA statistics) are controlled by parameters defined
    in :class:`get_spectrum_defaults`. Pass an instance of that class via
    ``**kwargs`` or override individual parameters (they will be validated
    against the defaults class).

    Main parameters (from ``get_spectrum_defaults``):

    - scan (list[int]): Scan id(s) to retrieve. A single integer or a list is accepted.
    - precursor_trim (int): m/z window used to trim precursor region for MS2 (default: -10).
    - max_peaks (int | None): Maximum number of peaks to keep; ``None`` keeps all.
    - centroid (bool): Whether to centroid the spectrum (default: True).
    - deisotope (bool): Whether to apply deisotoping (default: True).
    - dia_stats (bool | None): Collect DIA/ztscan statistics when applicable (default: False).
    - feature (int | None): Optional feature id used for computing DIA statistics.
    - label (str | None): Optional label to assign to the returned Spectrum.
    - centroid_algo (str | None): Centroiding algorithm to use (allowed: 'lmp', 'cwt', 'gaussian').

    Returns:
        Spectrum or None: Processed spectrum object (may be an empty Spectrum if
        the scan is missing or on error).

    Notes:
        This wrapper validates provided parameters against ``get_spectrum_defaults``.
        Use the defaults class to discover parameter constraints and allowed values.
    """

    # parameters initialization
    params = get_spectrum_defaults(scan=scan)
    for key, value in kwargs.items():
        if isinstance(value, get_spectrum_defaults):
            params = value
            self.logger.debug("Using provided get_spectrum_defaults parameters")
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

    # Extract parameter values
    scan = params.get("scan")
    precursor_trim = params.get("precursor_trim")
    max_peaks = params.get("max_peaks")
    centroid = params.get("centroid")
    deisotope = params.get("deisotope")
    dia_stats = params.get("dia_stats")
    feature_uid = params.get("feature")
    label = params.get("label")
    centroid_algo = params.get("centroid_algo")

    # get energy, ms_level, rt from scans_df
    scan_uid = scan  # Preserve original scan ID
    scan_info = self.scans_df.filter(pl.col("scan_uid") == scan_uid)
    if len(scan_info) == 0:
        self.logger.warning(f"Scan {scan_uid} not found.")
        return None
    scan_info = scan_info[0]
    energy = scan_info["energy"][0]
    ms_level = scan_info["ms_level"][0]
    rt = scan_info["rt"][0]
    if label is None:
        if ms_level == 1:
            name = f"MS1, rt {rt:.2f} s, scan {scan_uid}"
        else:
            name = f"MS2 of mz {scan_info['prec_mz'][0]:0.1f}, rt {rt:.2f} s, scan {scan_uid}"
    else:
        name = label

    if centroid_algo is None:
        if "centroid_algo" in self.parameters:
            centroid_algo = self.parameters.get("centroid_algo")
        else:
            # this is for backward compatibility. This is the old default
            self.parameters.centroid_algo = "lmp"
        centroid_algo = self.parameters.get("centroid_algo")

    spec0 = Spectrum(mz=np.array([]), inty=np.array([]))
    if self.file_interface == "oms":
        # if check that file_obj is not None
        if self.file_obj is None:
            self.logger.error("Please load a file first.")
            return
        try:
            spect = self.file_obj.getSpectrum(scan_uid).get_peaks()
        except Exception as e:
            self.logger.error(f"Error: {e}")
            return spec0
        if len(spect[0]) == 0:
            return spec0
        elif len(spect[0]) == 1:
            mz = np.array([spect[0][0]])
            inty = np.array([spect[1][0]])
        else:
            mz = np.array(spect[0])
            inty = np.array(spect[1])
        if ms_level == 1:
            spect = Spectrum(
                mz=mz,
                inty=inty,
                ms_level=ms_level,
                rt=rt,
                energy=None,
                precursor_mz=None,
                label=name,
            )
        else:
            spect = Spectrum(
                mz=mz,
                inty=inty,
                ms_level=ms_level,
                rt=rt,
                energy=energy,
                precursor_mz=scan_info["prec_mz"][0],
                label=name,
            )
        if centroid and not spect.centroided:
            spect = spect.denoise()
            if spect.ms_level == 1:
                spect = spect.centroid(
                    algo=centroid_algo,
                    tolerance=self.parameters.get("mz_tol_ms1_da"),
                    ppm=self.parameters.get("mz_tol_ms1_ppm"),
                    min_points=self.parameters.get("centroid_min_points_ms1"),
                    smooth=self.parameters.get("centroid_smooth"),
                    prominence=self.parameters.get("centroid_prominence"),
                    refine=self.parameters.get("centroid_refine"),
                )
            elif spect.ms_level == 2:
                spect = spect.centroid(
                    algo=centroid_algo,
                    tolerance=self.parameters.get("mz_tol_ms2_da"),
                    ppm=self.parameters.get("mz_tol_ms2_ppm"),
                    min_points=self.parameters.get("centroid_min_points_ms2"),
                    smooth=self.parameters.get("centroid_smooth"),
                    prominence=self.parameters.get("centroid_prominence"),
                    refine=self.parameters.get("centroid_refine"),
                )

    elif self.file_interface == "alpharaw":
        spec_df = self.file_obj.spectrum_df
        spect = (
            spec_df.filter(pl.col("scan_id") == scan_uid).row(0, named=True)
            if isinstance(spec_df, pl.DataFrame)
            else spec_df.loc[scan_uid]
        )
        peak_stop_idx = spect["peak_stop_idx"]
        peak_start_idx = spect["peak_start_idx"]

        if isinstance(self.file_obj.peak_df, pl.DataFrame):
            peaks = self.file_obj.peak_df.slice(
                peak_start_idx,
                peak_stop_idx - peak_start_idx,
            )
            mz_values = peaks.select("mz").to_numpy().flatten()
            intensity_values = peaks.select("intensity").to_numpy().flatten()
        else:
            peaks = self.file_obj.peak_df.loc[peak_start_idx : peak_stop_idx - 1]
            mz_values = peaks.mz.values
            intensity_values = peaks.intensity.values

        if spect["ms_level"] > 1:
            spect = Spectrum(
                mz=np.asarray(mz_values, dtype=np.float64),
                inty=np.asarray(intensity_values, dtype=np.float64),
                ms_level=ms_level,
                centroided=False,
                precursor_mz=spect["precursor_mz"],
                energy=energy,
                rt=rt,
                label=name,
            )
        else:
            spect = Spectrum(
                mz=np.asarray(mz_values, dtype=np.float64),
                inty=np.asarray(intensity_values, dtype=np.float64),
                ms_level=ms_level,
                centroided=False,
                precursor_mz=None,
                energy=None,
                rt=rt,
                label=name,
            )

        if len(spect) and centroid and not spect.centroided:
            spect = spect.denoise()
            if spect.ms_level == 1:
                spect = spect.centroid(
                    algo=centroid_algo,
                    tolerance=self.parameters.get("mz_tol_ms1_da"),
                    ppm=self.parameters.get("mz_tol_ms1_ppm"),
                    min_points=self.parameters.get("centroid_min_points_ms1"),
                    smooth=self.parameters.get("centroid_smooth"),
                    prominence=self.parameters.get("centroid_prominence"),
                    refine=self.parameters.get("centroid_refine"),
                )
            elif spect.ms_level == 2:
                spect = spect.centroid(
                    algo=centroid_algo,
                    tolerance=self.parameters.get("mz_tol_ms2_da"),
                    ppm=self.parameters.get("mz_tol_ms2_ppm"),
                    min_points=self.parameters.get("centroid_min_points_ms2"),
                    smooth=self.parameters.get("centroid_smooth"),
                    prominence=self.parameters.get("centroid_prominence"),
                    refine=self.parameters.get("centroid_refine"),
                )

    else:
        self.logger.error(
            f"File interface {self.file_interface} not supported. Reload data.",
        )
        return spec0

    if precursor_trim is not None and spect.ms_level > 1:
        spect = spect.trim(mz_min=None, mz_max=spect.precursor_mz - precursor_trim)  # type: ignore[attr-defined]
    if deisotope:
        spect = spect.deisotope()

    if max_peaks is not None:
        spect = spect.keep_top(max_peaks)

    if dia_stats:
        if self.file_type in ["ztscan", "dia"]:
            spect = self._get_ztscan_stats(
                spec=spect,
                scan_uid=scan_uid,
                feature_uid=scan_info["feature_uid"][0]
                if "feature_uid" in scan_info
                and scan_info["feature_uid"][0] is not None
                else feature_uid,
                q1_step=2,
                deisotope=deisotope,
                centroid=centroid,
            )
    return spect


def _get_ztscan_stats(
    self,
    spec,
    scan_uid=None,
    feature_uid=None,
    q1_step=2,
    mz_tol=0.005,
    # TODO check this
    # deisotope=SpectrumParameters().deisotope,
    deisotope=False,
    # TODO there is no `centroid_algo`?
    centroid=True,
):
    spec.size = spec.mz.size
    # spec.ms_entropy = spec.entropy()

    if self.scans_df is None:
        self.logger.warning("No scans found.")
        return spec
    scan = self.scans_df.filter(pl.col("scan_uid") == scan_uid)
    if len(scan) == 0:
        self.logger.warning(f"Scan {scan_uid} not found.")
        return spec
    scan = scan[0]
    if scan["ms_level"][0] != 2:
        self.logger.warning(f"Scan {scan_uid} is not a MS2 scan.")
    # Q1
    lscan = self.scans_df.filter(pl.col("scan_uid") == scan_uid - q1_step)
    if len(lscan) == 0:
        self.logger.warning(f"Scan {scan_uid - q1_step} not found.")
        return spec
    lscan = lscan[0]
    # check that lscan['ms_level'] == 2 and lscan['cycle'] == scan['cycle']
    if lscan["ms_level"][0] != 2:
        self.logger.warning(f"Scan {scan_uid - q1_step} is not a MS2 scan.")
        return spec
    if lscan["cycle"][0] != scan["cycle"][0]:
        self.logger.warning(
            f"Scan {scan_uid - q1_step} is not in the same cycle as scan {scan_uid}.",
        )
        return spec
    rscan = self.scans_df.filter(pl.col("scan_uid") == scan_uid + q1_step)
    if len(rscan) == 0:
        self.logger.warning(f"Scan {scan_uid + q1_step} not found.")
        return spec
    rscan = rscan[0]
    # check that rscan['ms_level'] == 2 and rscan['cycle'] == scan['cycle']
    if rscan["ms_level"][0] != 2:
        self.logger.warning(f"Scan {scan_uid + q1_step} is not a MS2 scan.")
        return spec
    if rscan["cycle"][0] != scan["cycle"][0]:
        self.logger.warning(
            f"Scan {scan_uid + q1_step} is not in the same cycle as scan {scan_uid}.",
        )
        return spec
    intymat = self._spec_to_mat(
        scan_uids=[scan_uid - q1_step, scan_uid, scan_uid + q1_step],
        mz_ref=spec.mz,
        mz_tol=mz_tol,
        deisotope=deisotope,
        centroid=centroid,
    )
    # pick only mzs that are close to spec.mz
    if intymat is None:
        return spec
    if intymat.shape[1] < 3:
        self.logger.warning(f"Not enough data points for scan {scan_uid}.")
        return spec
    q1_ratio = (2 * intymat[:, 1] + 0.01) / (intymat[:, 0] + intymat[:, 2] + 0.01)
    spec.q1_ratio = np.log2(q1_ratio)
    # where intymat[:, 0] + intymat[:, 2]==0, set q1_ratio to -1
    spec.q1_ratio[np.isclose(intymat[:, 0] + intymat[:, 2], 0)] = -10

    # EIC correlation
    # find rt_start and rt_end of the feature_uid
    if self.features_df is None:
        self.logger.warning("No features found.")
        return spec
    if feature_uid is None:
        return spec
    # spec.precursor_mz = feature['mz']
    feature = self.features_df.filter(pl.col("feature_uid") == feature_uid)
    if len(feature) == 0:
        self.logger.warning(f"Feature {feature_uid} not found.")
        return spec
    feature = feature.row(0, named=True)
    rt_start = feature["rt_start"]
    rt_end = feature["rt_end"]
    # get the cycle at rt_start and the cycle at rt_end from the closest scan with ms_level == 1
    scans = self.scans_df.filter(pl.col("ms_level") == 1)
    scans = scans.filter(pl.col("rt") > rt_start)
    scans = scans.filter(pl.col("rt") < rt_end)
    if len(scans) == 0:
        self.logger.warning(f"No scans found between {rt_start} and {rt_end}.")
        return spec
    scan_uids = scans["scan_uid"].to_list()
    eic_prec = self._spec_to_mat(
        scan_uids=scan_uids,
        mz_ref=feature["mz"],
        mz_tol=mz_tol,
        deisotope=deisotope,
        centroid=centroid,
    )
    # find width at half maximum of the eic_prec
    # hm = np.max(eic_prec[0, :]) / 3
    # find index of maximum
    # eic_prec_max_idx = np.argmax(eic_prec[0, :])
    # find index of the closest point to half maximum
    # idx = np.argmin(np.abs(eic_prec[0, :] - hm))
    # eic_fwhm_prec = abs(eic_prec_max_idx - idx)

    # get all unique cycles from scans
    cycles = scans["cycle"].unique()
    scandids = []
    # iterate over all cycles and get the scan_uid of scan with ms_level == 2 and closest precursor_mz to spec.precursor_mz
    for cycle in cycles:
        scans = self.scans_df.filter(pl.col("cycle") == cycle)
        scans = scans.filter(pl.col("ms_level") == 2)
        scans = scans.filter(pl.col("prec_mz") > feature["mz"] - 4)
        scans = scans.filter(pl.col("prec_mz") < feature["mz"] + 4)
        if len(scans) == 0:
            self.logger.warning(f"No scans found for cycle {cycle}.")
            continue
        scan = scans[(scans["prec_mz"] - feature["mz"]).abs().arg_sort()[:1]]
        scandids.append(scan["scan_uid"][0])

    eic_prod = self._spec_to_mat(
        scandids,
        mz_ref=spec.mz,
        mz_tol=mz_tol,
        deisotope=deisotope,
        centroid=centroid,
    )
    # eic_prod = eic_prod.T
    # eic_prec = eic_prec.T
    # calculate correlation between eic_prec and all columns of eic_prod, column by column
    eic_corr = np.zeros(eic_prod.shape[0])
    # eic_width_ratio = np.zeros(eic_prod.shape[0])
    for i in range(eic_prod.shape[0]):
        try:
            with np.errstate(divide="ignore", invalid="ignore"):
                eic_corr[i] = np.corrcoef(eic_prod[i, :], eic_prec[0, :])[0, 1]
        except:
            pass

    spec.eic_corr = eic_corr
    return spec


def _spec_to_mat(
    self,
    scan_uids,
    mz_ref=None,
    mz_tol=0.01,
    # TODO check this
    # deisotope=SpectrumParameters().deisotope,
    deisotope=False,
    # TODO there is no `centroid_algo`?
    # TODO there is no `dia_stats`?
    # TODO unused (see below)
    centroid=True,
    # TODO check this
    # precursor_trim=SpectrumParameters().precursor_trim,
    # TODO unused (see below)
    precursor_trim=None,
):
    # get all spectra in scan_uids

    if mz_ref is None:
        return None

    if not isinstance(mz_ref, np.ndarray):
        if isinstance(mz_ref, list):
            mz_ref = np.array(mz_ref)
        else:
            mz_ref = np.array([mz_ref])

    def align_mzs(ar1, ar2, tol):
        closest_indices = []
        # find the closest pair between each element in ar1 and ar2, within a maximum tolerance of tol
        for i, val1 in enumerate(ar1):
            closest_index = np.argmin(np.abs(ar2 - val1))
            closest_indices.append((i, closest_index))
        # filter out pairs that are not within the specified tolerance
        closest_indices = [
            (i, j) for i, j in closest_indices if np.abs(ar1[i] - ar2[j]) <= tol
        ]
        # remove duplicates from the list of indices
        closest_indices = list(set(closest_indices))
        # sort the list of indices by the first element (i) in ascending order
        closest_indices = sorted(closest_indices, key=lambda x: x[0])

        # Convert the list of indices into an array for easier indexing in subsequent operations
        return np.array(closest_indices)

    specs = []
    for scan_uid in scan_uids:
        spec = self.get_spectrum(
            scan_uid=scan_uid,
            centroid=True,
            dia_stats=False,
            precursor_trim=5,
        )
        if deisotope:
            spec = spec.deisotope()
        # align to reference spectrum
        if spec.mz.size == 0:
            continue
        if mz_ref.size == 0:
            continue
        closest_indices = align_mzs(spec.mz, mz_ref, mz_tol)
        # store the aligned spectrum in the list
        aligned_inty = np.zeros(len(mz_ref))
        for i, j in closest_indices:
            if abs(spec.mz[i] - mz_ref[j]) <= mz_tol:
                if aligned_inty[j] < spec.inty[i]:
                    aligned_inty[j] = spec.inty[i]
        specs.append(aligned_inty)

    if len(specs) == 0:
        return None
    # create a matrix with the aligned spectra. Each spec goes into a column
    mat = np.column_stack(specs)

    return mat


def find_features(self, **kwargs):
    """Detect features from MS1 data (mass-trace detection, peak deconvolution, feature assembly).

    The method converts internal MS1 data into an MSExperiment (one MSSpectrum per cycle), runs mass-trace
    detection, deconvolutes mass traces to find chromatographic peaks, and assembles features. Results are
    cleaned, optionally deisotoped, assigned unique IDs and stored in ``self.features`` / ``self.features_df``.

    Parameters:
        **kwargs: Keyword overrides for any parameter available in :class:`find_features_defaults`.
            You may pass a full ``find_features_defaults`` instance or individual parameter values.

    Main parameters (what they mean, units and tuning guidance):

    - chrom_fwhm (float, seconds):
        Expected chromatographic peak full-width at half-maximum (FWHM) in seconds. This guides smoothing,
        peak-finding window sizes and RT-based tolerances. Choose a value that matches your LC peak widths:
        small values (e.g. 0.2–0.8 s) for sharp/fast separations, larger values (several seconds) for broad peaks.
        Default: 1.0 s.

    - noise (float, intensity units):
        Intensity threshold used to ignore background points before mass-trace and peak detection. Raising
        ``noise`` reduces false positives from baseline fluctuations but may discard low-abundance true signals;
        lowering it increases sensitivity but raises the false-positive rate. Set this to a conservative estimate of
        your instrument baseline (default: 200.0, instrument-dependent).

    - chrom_peak_snr (float, unitless):
        Minimum signal-to-noise ratio required to accept an elution peak during peak deconvolution. SNR is usually
        computed as peak height divided by a local noise estimate. Higher values make detection stricter (fewer
        low-quality peaks), lower values make it more permissive. Typical tuning range: ~3 (relaxed) to >10
        (stringent). Default: 10.0.

    - isotope_filtering_model (str):
        Isotope filtering model ('metabolites (2% RMS)', 'metabolites (5% RMS)', 'peptides', 'none').
        Default: 'metabolites (5% RMS)'.

    Tuning recommendation: first set ``chrom_fwhm`` to match your LC peak shape, then set ``noise`` to a baseline
    intensity filter for your data, and finally adjust ``chrom_peak_snr`` to reach the desired balance between
    sensitivity and specificity.

    Attributes set:
        self.features: OpenMS FeatureMap produced by the routine (after ensureUniqueId).
        self.features_df: cleaned polars DataFrame of detected features (zero-quality peaks removed).

    Notes:
        The implementation relies on OpenMS components (MassTraceDetection, ElutionPeakDetection,
        FeatureFindingMetabo). See ``find_features_defaults`` for the full list of adjustable parameters.
    """
    if self.ms1_df is None:
        self.logger.error("No MS1 data found. Please load a file first.")
        return
    if len(self.ms1_df) == 0:
        self.logger.error("MS1 data is empty. Please load a file first.")
        return
    # parameters initialization
    params = find_features_defaults()
    for key, value in kwargs.items():
        if isinstance(value, find_features_defaults):
            # set
            params = value
            self.logger.debug("Using provided find_features_defaults parameters")
        else:
            if hasattr(params, key):
                if params.set(key, value, validate=True):
                    self.logger.debug(f"Updated parameter {key} = {value}")
                else:
                    self.logger.warning(
                        f"Failed to set parameter {key} = {value} (validation failed)",
                    )
            else:
                self.logger.warning(f"Unknown parameter {key} ignored")

    # Set global parameters
    if hasattr(params, "threads") and params.threads is not None:
        try:
            # Try setting via OpenMP environment variable first (newer approach)
            import os

            os.environ["OMP_NUM_THREADS"] = str(params.threads)
            self.logger.debug(
                f"Set thread count to {params.threads} via OMP_NUM_THREADS",
            )
        except Exception:
            self.logger.warning(
                f"Could not set thread count to {params.threads} - using default",
            )

    # Set debug mode if enabled
    if hasattr(params, "debug") and params.debug:
        self.logger.debug("Debug mode enabled")
    elif hasattr(params, "no_progress") and params.no_progress:
        self.logger.debug("No progress mode enabled")

    self.logger.info("Starting feature detection...")
    self.logger.debug(
        f"Parameters: chrom_fwhm={params.get('chrom_fwhm')}, noise={params.get('noise')}, tol_ppm={params.get('tol_ppm')}, isotope_filtering_model={params.get('isotope_filtering_model')}",
    )

    exp = oms.MSExperiment()
    # find max number of cycles in self.ms1_df
    max_cycle = self.ms1_df["cycle"].max()
    # iterate over all cycles, find rows with 1 cycle and append to exp2
    for cycle in range(1, max_cycle + 1):
        cycle_df = self.ms1_df.filter(pl.col("cycle") == cycle)
        # check if len(cycle_df) > 0
        if len(cycle_df) > 0:
            spectrum = oms.MSSpectrum()
            spectrum.setRT(cycle_df[0]["rt"].item())
            spectrum.setMSLevel(1)  # MS1
            mz = cycle_df["mz"]
            inty = cycle_df["inty"]
            spectrum.set_peaks([mz, inty])  # type: ignore[attr-defined]
            spectrum.sortByPosition()
            exp.addSpectrum(spectrum)

    # exp.sortSpectra(True)
    # mass trace detection
    mass_traces: list = []
    mtd = oms.MassTraceDetection()
    mtd_par = mtd.getDefaults()

    # Apply MTD parameters
    mtd_par.setValue("mass_error_ppm", float(params.get("tol_ppm")))
    mtd_par.setValue("noise_threshold_int", float(params.get("noise")))
    mtd_par.setValue(
        "min_trace_length",
        float(params.get("min_trace_length_multiplier"))
        * float(params.get("chrom_fwhm_min")),
    )
    mtd_par.setValue(
        "trace_termination_outliers",
        int(params.get("trace_termination_outliers")),
    )
    mtd_par.setValue("chrom_peak_snr", float(params.get("chrom_peak_snr")))

    # Additional MTD parameters
    mtd_par.setValue("min_sample_rate", float(params.get("min_sample_rate")))
    mtd_par.setValue("min_trace_length", float(params.get("min_trace_length")))
    mtd_par.setValue(
        "trace_termination_criterion",
        params.get("trace_termination_criterion"),
    )
    mtd_par.setValue(
        "reestimate_mt_sd",
        "true" if params.get("reestimate_mt_sd") else "false",
    )
    mtd_par.setValue("quant_method", params.get("quant_method"))

    mtd.setParameters(mtd_par)  # set the new parameters
    mtd.run(exp, mass_traces, 0)  # run mass trace detection

    # elution peak detection
    mass_traces_deconvol: list = []
    epd = oms.ElutionPeakDetection()
    epd_par = epd.getDefaults()

    # Apply EPD parameters using our parameter class
    epd_par.setValue("width_filtering", params.get("width_filtering"))
    epd_par.setValue("min_fwhm", float(params.get("chrom_fwhm_min")))
    epd_par.setValue("max_fwhm", float(params.get("chrom_fwhm_max")))
    epd_par.setValue("chrom_fwhm", float(params.get("chrom_fwhm")))
    epd_par.setValue("chrom_peak_snr", float(params.get("chrom_peak_snr")))
    if params.get("masstrace_snr_filtering"):
        epd_par.setValue("masstrace_snr_filtering", "true")
    if params.get("mz_scoring_13C"):
        epd_par.setValue("mz_scoring_13C", "true")

    epd.setParameters(epd_par)
    epd.detectPeaks(mass_traces, mass_traces_deconvol)

    # feature detection
    feature_map = oms.FeatureMap()  # output features
    chrom_out: list = []  # output chromatograms
    ffm = oms.FeatureFindingMetabo()
    ffm_par = ffm.getDefaults()

    # Apply FFM parameters using our parameter class
    ffm_par.setValue(
        "remove_single_traces",
        "true" if params.get("remove_single_traces") else "false",
    )
    ffm_par.setValue(
        "report_convex_hulls",
        "true" if params.get("report_convex_hulls") else "false",
    )
    ffm_par.setValue(
        "report_summed_ints",
        "true" if params.get("report_summed_ints") else "false",
    )
    ffm_par.setValue(
        "report_chromatograms",
        "true" if params.get("report_chromatograms") else "false",
    )
    ffm_par.setValue(
        "report_smoothed_intensities",
        "true" if params.get("report_smoothed_intensities") else "false",
    )
    # Additional FFM parameters
    ffm_par.setValue("local_rt_range", float(params.get("local_rt_range")))
    ffm_par.setValue("local_mz_range", float(params.get("local_mz_range")))
    ffm_par.setValue("charge_lower_bound", int(params.get("charge_lower_bound")))
    ffm_par.setValue("charge_upper_bound", int(params.get("charge_upper_bound")))
    ffm_par.setValue("isotope_filtering_model", params.get("isotope_filtering_model"))

    ffm.setParameters(ffm_par)

    self.logger.debug("Running feature finding with parameters:")
    self.logger.debug(ffm_par)
    ffm.run(mass_traces_deconvol, feature_map, chrom_out)
    # Assigns a new, valid unique id per feature
    feature_map.ensureUniqueId()
    df = feature_map.get_df(export_peptide_identifications=False)  # type: ignore[attr-defined]
    # Sets the file path to the primary MS run (usually the mzML file)
    feature_map.setPrimaryMSRunPath([self.file_path.encode()])

    # Store feature map in both attributes for compatibility
    self.features = feature_map
    self._oms_features_map = feature_map
    # remove peaks with quality == 0
    df = self._clean_features_df(df)

    # desotope features
    df = self._features_deisotope(
        df,
        mz_tol=params.get("deisotope_mz_tol"),
        rt_tol=params.get("chrom_fwhm") * params.get("deisotope_rt_tol_factor"),
    )
    if params.get("deisotope"):
        # record size before deisotoping
        size_before_deisotope = len(df)
        df = df.filter(pl.col("iso") == 0)
        self.logger.debug(
            f"Deisotoping features: {size_before_deisotope - len(df)} features removed.",
        )

    # update eic - create lists to collect results
    chroms: list[Chromatogram] = []
    coherences: list[float] = []
    prominences: list[float] = []
    prominence_scaleds: list[float] = []
    height_scaleds: list[float] = []

    mz_tol = self.parameters.get("eic_mz_tol")
    rt_tol = self.parameters.get("eic_rt_tol")

    # iterate over all rows in df using polars iteration
    self.logger.debug("Extracting EICs...")
    for row in df.iter_rows(named=True):
        # select data in ms1_df with mz in range [mz_start - mz_tol, mz_end + mz_tol] and rt in range [rt_start - rt_tol, rt_end + rt_tol]
        d = self.ms1_df.filter(
            (pl.col("rt") >= row["rt_start"] - rt_tol)
            & (pl.col("rt") <= row["rt_end"] + rt_tol)
            & (pl.col("mz") >= row["mz"] - mz_tol)
            & (pl.col("mz") <= row["mz"] + mz_tol),
        )
        # for all unique rt values, find the maximum inty
        eic_rt = d.group_by("rt").agg(pl.col("inty").max())
        if len(eic_rt) < 4:
            chroms.append(None)
            coherences.append(None)
            prominences.append(None)
            prominence_scaleds.append(None)
            height_scaleds.append(None)
            continue

        eic = Chromatogram(
            eic_rt["rt"].to_numpy(),
            eic_rt["inty"].to_numpy(),
            label=f"EIC mz={row['mz']:.4f}",
            file=self.file_path,
            mz=row["mz"],
            mz_tol=mz_tol,
            feature_start=row["rt_start"],
            feature_end=row["rt_end"],
            feature_apex=row["rt"],
        ).find_peaks()

        # collect results
        chroms.append(eic)
        if len(eic.peak_widths) > 0:
            coherences.append(round(eic.feature_coherence, 3))
            prominences.append(round(eic.peak_prominences[0], 3))
            prominence_scaleds.append(
                round(eic.peak_prominences[0] / (np.mean(eic.inty) + 1e-10), 3),
            )
            height_scaleds.append(
                round(eic.peak_heights[0] / (np.mean(eic.inty) + 1e-10), 3),
            )
        else:
            coherences.append(None)
            prominences.append(None)
            prominence_scaleds.append(None)
            height_scaleds.append(None)

    # Add the computed columns to the dataframe
    df = df.with_columns(
        [
            pl.Series("chrom", chroms, dtype=pl.Object),
            pl.Series("chrom_coherence", coherences, dtype=pl.Float64),
            pl.Series("chrom_prominence", prominences, dtype=pl.Float64),
            pl.Series("chrom_prominence_scaled", prominence_scaleds, dtype=pl.Float64),
            pl.Series("chrom_height_scaled", height_scaleds, dtype=pl.Float64),
        ],
    )

    self.features_df = df
    self._features_sync()
    self.logger.info(f"Feature detection completed. Total features: {len(df)}")

    # store params
    self.store_history(["find_features"], params.to_dict())
    self.logger.debug(
        "Parameters stored to find_features",
    )
    keys_to_remove = ["find_adducts", "find_ms2"]
    for key in keys_to_remove:
        if key in self.history:
            del self.history[key]
            self.logger.debug(f"Removed {key} from history")


def _clean_features_df(self, df):
    """Clean and standardize features DataFrame."""
    # Convert pandas DataFrame to polars if needed
    if hasattr(df, "index"):  # pandas DataFrame
        df = df.copy()
        df["feature_id"] = df.index

    if hasattr(df, "columns") and not isinstance(df, pl.DataFrame):
        df_pl = pl.from_pandas(df)
    else:
        df_pl = df

    # Filter out rows with quality == 0
    df2 = df_pl.filter(pl.col("quality") != 0)

    # Create new dataframe with required columns and transformations
    df_result = df2.select(
        [
            pl.int_range(pl.len()).alias("feature_uid"),
            pl.col("feature_id").cast(pl.String).alias("feature_id"),
            pl.col("mz").round(5),
            pl.col("RT").round(3).alias("rt"),
            pl.col("RT").round(3).alias("rt_original"),
            pl.col("RTstart").round(3).alias("rt_start"),
            pl.col("RTend").round(3).alias("rt_end"),
            (pl.col("RTend") - pl.col("RTstart")).round(3).alias("rt_delta"),
            pl.col("MZstart").round(5).alias("mz_start"),
            pl.col("MZend").round(5).alias("mz_end"),
            pl.col("intensity").alias("inty"),
            pl.col("quality"),
            pl.col("charge"),
            pl.lit(0).alias("iso"),
            pl.lit(None, dtype=pl.Int64).alias("iso_of"),
            pl.lit(None, dtype=pl.Utf8).alias("adduct"),
            pl.lit(None, dtype=pl.Float64).alias("adduct_charge"),
            pl.lit(None, dtype=pl.Float64).alias("adduct_mass_shift"),
            pl.lit(None, dtype=pl.Float64).alias("adduct_mass_neutral"),
            pl.lit(None, dtype=pl.Int64).alias("adduct_group"),
            pl.lit(None, dtype=pl.Object).alias("chrom"),
            pl.lit(None, dtype=pl.Float64).alias("chrom_coherence"),
            pl.lit(None, dtype=pl.Float64).alias("chrom_prominence"),
            pl.lit(None, dtype=pl.Float64).alias("chrom_prominence_scaled"),
            pl.lit(None, dtype=pl.Float64).alias("chrom_height_scaled"),
            pl.lit(None, dtype=pl.Object).alias("ms2_scans"),
            pl.lit(None, dtype=pl.Object).alias("ms2_specs"),
        ],
    )

    return df_result


def _features_deisotope(
    self,
    df,
    mz_tol=None,
    rt_tol=None,
):
    """Perform isotope detection and assignment on features."""
    if mz_tol is None:
        mz_tol = 0.02
    if rt_tol is None:
        rt_tol = 0.2

    # Convert to polars if needed
    if not isinstance(df, pl.DataFrame):
        df = pl.from_pandas(df)

    # Initialize new columns
    df = df.with_columns(
        [
            pl.lit(0).alias("iso"),
            pl.col("feature_uid").alias("iso_of"),
        ],
    )

    # Sort by 'mz'
    df = df.sort("mz")

    # Get arrays for efficient processing
    rt_arr = df["rt"].to_numpy()
    mz_arr = df["mz"].to_numpy()
    intensity_arr = df["inty"].to_numpy()
    feature_uid_arr = df["feature_uid"].to_numpy()
    n = len(df)
    mz_diff = 1.003355

    # Create arrays to track isotope assignments
    iso_arr = np.zeros(n, dtype=int)
    iso_of_arr = feature_uid_arr.copy()

    for i in range(n):
        base_rt = rt_arr[i]
        base_mz = mz_arr[i]
        base_int = intensity_arr[i]
        base_feature_uid = feature_uid_arr[i]

        # Search for isotope candidates
        for isotope_offset in [1, 2, 3]:
            offset_mz = isotope_offset * mz_diff
            tolerance_factor = 1.0 if isotope_offset == 1 else 1.5

            t_lower = base_mz + offset_mz - tolerance_factor * mz_tol
            t_upper = base_mz + offset_mz + tolerance_factor * mz_tol

            li = np.searchsorted(mz_arr, t_lower, side="left")
            ri = np.searchsorted(mz_arr, t_upper, side="right")

            if li < ri:
                cand_idx = np.arange(li, ri)
                mask = (
                    (rt_arr[cand_idx] > base_rt - rt_tol)
                    & (rt_arr[cand_idx] < base_rt + rt_tol)
                    & (intensity_arr[cand_idx] < 2 * base_int)
                )
                valid_cand = cand_idx[mask]

                for cand in valid_cand:
                    if cand != i and iso_of_arr[cand] == feature_uid_arr[cand]:
                        iso_arr[cand] = iso_arr[i] + isotope_offset
                        iso_of_arr[cand] = base_feature_uid

    # Update the dataframe with isotope assignments
    df = df.with_columns(
        [
            pl.Series("iso", iso_arr),
            pl.Series("iso_of", iso_of_arr),
        ],
    )

    return df


def analyze_dda(self):
    # Preallocate variables
    cycle_records = []
    previous_rt = 0
    previous_level = 0
    ms1_index = None
    cyclestart = None
    ms2_n = 0
    ms1_duration = 0
    ms2_duration: list[float] = []

    for row in self.scans_df.iter_rows(named=True):
        if row["ms_level"] == 1:
            if previous_level == 2:
                ms2_to_ms2 = float(np.mean(ms2_duration)) if ms2_duration else -1.0
                d = {
                    "scan_uid": ms1_index,
                    "ms2_n": ms2_n,
                    "time_cycle": row["rt"] - cyclestart,
                    "time_ms1_to_ms1": -1.0,
                    "time_ms1_to_ms2": ms1_duration,
                    "time_ms2_to_ms2": ms2_to_ms2,
                    "time_ms2_to_ms1": row["rt"] - previous_rt,
                }
                cycle_records.append(d)
            elif previous_level == 1:
                d = {
                    "scan_uid": ms1_index,
                    "ms2_n": 0,
                    "time_cycle": row["rt"] - cyclestart,
                    "time_ms1_to_ms1": row["rt"] - cyclestart,
                    "time_ms1_to_ms2": -1.0,
                    "time_ms2_to_ms2": -1.0,
                    "time_ms2_to_ms1": -1.0,
                }
                cycle_records.append(d)

            ms1_index = row["scan_uid"]
            cyclestart = row["rt"]
            ms2_n = 0
            ms1_duration = 0
            ms2_duration = []
        elif previous_level == 2:
            ms2_n += 1
            ms2_duration.append(row["rt"] - previous_rt)
        elif previous_level == 1:
            ms1_duration = row["rt"] - cyclestart
            ms2_n += 1
        previous_level = row["ms_level"]
        previous_rt = row["rt"]

    # Create DataFrame once at the end
    if cycle_records:
        cycle_data = pl.DataFrame(cycle_records)
        self.scans_df = self.scans_df.join(cycle_data, on="scan_uid", how="left")
    else:
        self.scans_df = self.scans_df.with_columns(
            [
                pl.lit(None).alias("ms2_n"),
                pl.lit(None).alias("time_cycle"),
                pl.lit(None).alias("time_ms1_to_ms1"),
                pl.lit(None).alias("time_ms1_to_ms2"),
                pl.lit(None).alias("time_ms2_to_ms2"),
                pl.lit(None).alias("time_ms2_to_ms1"),
            ],
        )


def find_ms2(self, **kwargs):
    """Link MS2 spectra to detected features.

    Matches MS2 scans from ``self.scans_df`` to features in ``self.features_df`` using
    retention time and precursor m/z criteria. Parameters are defined in
    :class:`find_ms2_defaults`; pass an instance via ``**kwargs`` or override
    individual parameters (they will be validated against the defaults class).

    Main parameters (from ``find_ms2_defaults``):

    - mz_tol (float):
        Precursor m/z tolerance used for matching. The effective tolerance may be
        adjusted by file type (the defaults class provides ``get_mz_tolerance(file_type)``).
        Default: 0.5 (ztscan/DIA defaults may be larger).

    - centroid (bool):
        If True, retrieved spectra will be centroided (default: True).

    - deisotope (bool):
        If True, spectra will be deisotoped before returning (default: False).

    - dia_stats (bool):
        Collect additional DIA/ztscan statistics when retrieving spectra (default: False).

    - features (int | list[int] | None):
        Specific feature uid or list of uids to process. Use ``None`` to process all
        features. An empty list is treated as ``None``.

    - mz_tol_ztscan (float):
        m/z tolerance used for ztscan/DIA file types (default: 4.0).

    Side effects:
        Updates ``self.features_df`` with columns ``ms2_scans`` and ``ms2_specs`` and
        updates ``self.scans_df`` to set the ``feature_uid`` for matched scans.

    Notes:
        The function is implemented to be efficient by vectorizing the matching
        and performing batch updates. Use ``find_ms2_defaults`` to inspect all
        available parameters and their canonical descriptions.
    """

    # parameters initialization
    params = find_ms2_defaults()
    for key, value in kwargs.items():
        if isinstance(value, find_ms2_defaults):
            params = value
            self.logger.debug("Using provided find_ms2_defaults parameters")
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

    # Extract parameter values
    features = params.get("features")
    mz_tol = params.get_mz_tolerance(self.file_type)
    centroid = params.get("centroid")
    deisotope = params.get("deisotope")
    dia_stats = params.get("dia_stats")

    self.logger.debug("Starting MS2 spectra linking...")
    self.logger.debug(
        f"Parameters: mz_tol={mz_tol}, centroid={centroid}, deisotope={deisotope}",
    )

    # Ensure features_df is loaded and has the MS2 columns
    if self.features_df is None:
        self.logger.error("Please find features first.")
        return
    if "ms2_scans" not in self.features_df.columns:
        self.features_df["ms2_scans"] = None
    if "ms2_specs" not in self.features_df.columns:
        self.features_df["ms2_specs"] = None

    feature_uid_list = []
    self.logger.debug("Building lookup lists")
    if features == []:
        features = None  # If empty list, treat as None
    feature_uid_list = self._get_feature_uids(features)

    if len(feature_uid_list) == 0:
        self.logger.warning("No features to process.")
        return

    ms2_df = self.scans_df.filter(pl.col("ms_level") == 2)
    if len(ms2_df) == 0:
        self.logger.warning("No MS2 spectra found in file.")
        return

    ms2_index_arr = ms2_df["scan_uid"].to_numpy()
    ms2_rt = ms2_df["rt"].to_numpy()
    ms2_precursor = ms2_df["prec_mz"].to_numpy()
    ms2_cycle = ms2_df["cycle"].to_numpy()

    features_df = self.features_df
    c = 0

    if self.file_interface is None:
        self.index_file()

    # Vectorize the entire operation for better performance
    features_subset = features_df.filter(pl.col("feature_uid").is_in(feature_uid_list))

    if len(features_subset) == 0:
        return

    # Convert to numpy arrays for vectorized operations
    feature_rt = features_subset.select("rt").to_numpy().flatten()
    feature_mz = features_subset.select("mz").to_numpy().flatten()
    feature_rt_start = features_subset.select("rt_start").to_numpy().flatten()
    feature_rt_end = features_subset.select("rt_end").to_numpy().flatten()
    feature_uids = features_subset.select("feature_uid").to_numpy().flatten()
    feature_indices = (
        features_subset.with_row_index().select("index").to_numpy().flatten()
    )

    # Pre-compute RT radius for all features
    rt_radius = np.minimum(feature_rt - feature_rt_start, feature_rt_end - feature_rt)

    # Batch process all features
    scan_uid_lists: list[list[int]] = []
    spec_lists: list[list[Spectrum]] = []
    updated_feature_uids = []
    updated_scan_uids = []

    tdqm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]

    for i, (rt_center, mz_center, radius, feature_uid, idx) in enumerate(
        tqdm(
            zip(
                feature_rt,
                feature_mz,
                rt_radius,
                feature_uids,
                feature_indices,
                strict=False,
            ),
            total=len(features_subset),
            desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Link MS2 spectra",
            disable=tdqm_disable,
        ),
    ):
        # Vectorized filtering
        rt_mask = np.abs(ms2_rt - rt_center) <= radius
        mz_mask = np.abs(ms2_precursor - mz_center) <= mz_tol
        valid_mask = rt_mask & mz_mask

        if not np.any(valid_mask):
            scan_uid_lists.append(None)
            spec_lists.append(None)
            continue

        valid_indices = np.nonzero(valid_mask)[0]
        rt_diffs = np.abs(ms2_rt[valid_indices] - rt_center)
        sorted_indices = valid_indices[np.argsort(rt_diffs)]

        # Get unique cycles and their first occurrences
        cycles = ms2_cycle[sorted_indices]
        _, first_idx = np.unique(cycles, return_index=True)
        final_indices = sorted_indices[first_idx]

        # Sort by RT difference again
        final_rt_diffs = np.abs(ms2_rt[final_indices] - rt_center)
        final_indices = final_indices[np.argsort(final_rt_diffs)]

        scan_uids = ms2_index_arr[final_indices].tolist()
        scan_uid_lists.append(scan_uids)
        spec_lists.append(
            [
                self.get_spectrum(
                    scan_uids[0],
                    centroid=centroid,
                    deisotope=deisotope,
                    dia_stats=dia_stats,
                    feature_uid=feature_uid,
                ),
            ],
        )

        # Collect updates for batch processing
        updated_feature_uids.extend([feature_uid] * len(final_indices))
        updated_scan_uids.extend(ms2_index_arr[final_indices])
        c += 1

    self.logger.debug("Update features.")
    # Convert to polars if needed and batch update features_df
    # Convert to polars if needed and batch update features_df
    if not isinstance(features_df, pl.DataFrame):
        features_df = pl.from_pandas(features_df)

    # Update the features_df
    update_df = pl.DataFrame(
        {
            "temp_idx": feature_indices,
            "ms2_scans": pl.Series("ms2_scans", scan_uid_lists, dtype=pl.Object),
            "ms2_specs": pl.Series("ms2_specs", spec_lists, dtype=pl.Object),
        },
    )

    # Join and update
    features_df = (
        features_df.with_row_index("temp_idx")
        .join(
            update_df,
            on="temp_idx",
            how="left",
            suffix="_new",
        )
        .with_columns(
            [
                pl.when(pl.col("ms2_scans_new").is_not_null())
                .then(pl.col("ms2_scans_new"))
                .otherwise(pl.col("ms2_scans"))
                .alias("ms2_scans"),
                pl.when(pl.col("ms2_specs_new").is_not_null())
                .then(pl.col("ms2_specs_new"))
                .otherwise(pl.col("ms2_specs"))
                .alias("ms2_specs"),
            ],
        )
        .drop(["temp_idx", "ms2_scans_new", "ms2_specs_new"])
    )

    # Batch update scans_df
    if updated_scan_uids:
        scan_feature_uid_updates = dict(
            zip(updated_scan_uids, updated_feature_uids, strict=True),
        )
        self.scans_df = (
            self.scans_df.with_columns(
                pl.col("scan_uid")
                .map_elements(
                    lambda x: scan_feature_uid_updates.get(x),
                    return_dtype=pl.Int64,
                )
                .alias("feature_uid_update"),
            )
            .with_columns(
                pl.when(pl.col("feature_uid_update").is_not_null())
                .then(pl.col("feature_uid_update"))
                .otherwise(pl.col("feature_uid"))
                .alias("feature_uid"),
            )
            .drop("feature_uid_update")
        )

    # Log completion
    self.logger.info(
        f"MS2 linking completed. Total features with MS2 data: {c}",
    )
    self.features_df = features_df

    # store params
    self.store_history(["find_ms2"], params.to_dict())
    self.logger.debug(
        "Parameters stored to find_ms2",
    )
