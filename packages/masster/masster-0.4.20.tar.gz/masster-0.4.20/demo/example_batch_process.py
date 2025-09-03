#!/usr/bin/env python3
"""
Module: batch_process.py
This module processes mass spectrometry data using the massistant package. It supports
both single file and directory processing, and is capable of recursive searches for supported
file extensions (.wiff, .mzml, .raw, .mzpkl). The script also configures macOS-specific settings
for massistant when running on a Darwin platform, ensuring Mono compatibility via pythonnet.
Functions:
    process_file(file_path: Path, output_dir: Optional[Path], chrom_peak_snr: float,
                 noise: int, chrom_fwhm: float, mgf_export: str, centroid: bool) -> None:
        Processes a single mass spectrometry data file. Depending on whether an output directory
        is specified, the function determines the directory in which to save the processed results.
        It loads existing intermediate results if available, otherwise processes the file by detecting
        features, linking MS2 spectra, and exporting various plots and statistical summaries.
    parse_args() -> argparse.Namespace:
        Configures and parses command-line arguments. The parser accepts an input file or directory,
        optional destination directory, threshold parameters for feature detection (chrom_peak_snr, noise,
        chrom_fwhm), MGF export mode, and a flag to disable centroiding. It returns an argparse.Namespace
        object containing the parsed arguments.
    main() -> None:
        Serves as the main entry point of the script. It validates the input path, determines whether it
        is a single file or a directory, and then invokes the processing routine accordingly. For directories,
        it aggregates supported files (with optional recursive search) and processes each file sequentially.
Usage Example:
    To process a specific file:
        python batch_process.py /path/to/datafile.mzML
    To process an entire directory recursively and specify a destination folder:
        python batch_process.py /path/to/directory --recursive --dest /path/to/output
"""

import argparse
import os
import platform
import sys

from pathlib import Path


# Ensure massistant is in the path
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, ".."))
sys.path.insert(0, parent_dir)
from massistant.sample import Sample  # noqa: E402


# === macOS Mono Setup (for massistant via pythonnet) ===
if platform.system() == "Darwin":  # Only for macOS
    os.environ["PYTHONNET_RUNTIME"] = "mono"
    ## brew version not working for ARM, need the default universal one since the whole package is package via Rosetta, so defaulting to the classical /Library/Frameworks/Mono.framework
    # os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = "/opt/homebrew/lib"
    # os.environ["PATH"] = "/opt/homebrew/bin:" + os.environ.get("PATH", "")


# === Core Processing Function ===
def process_file(
    file_path: Path,
    output_dir: Path | None,
    chrom_peak_snr: float,
    chrom_fwhm: float,
    noise: float,
    window_size: float,
    mgf_export: str,
    centroid: bool,
):
    print(f"📄 Processing: {file_path.name}")

    base_name = file_path.stem
    out_dir = output_dir or file_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    mzpkl_path = out_dir / f"{base_name}.mzpkl"

    if mzpkl_path.exists():
        print(f"🔁 Using existing mzpkl: {mzpkl_path}")
        ddaobj = Sample(str(mzpkl_path))
    else:
        ddaobj = Sample(str(file_path))
        ddaobj.find_features_oms(
            chrom_peak_snr=chrom_peak_snr, noise=noise, chrom_fwhm=chrom_fwhm
        )

    # Link MS2
    ddaobj.find_ms2(mz_tol=window_size, centroid=centroid)

    # Save output files
    ddaobj.plot_2d(filename=str(out_dir / f"{base_name}_2d.html"))
    ddaobj.plot_dda_stats(filename=str(out_dir / f"{base_name}_stats.html"))
    ## COMMENT AR: Not working
    # ddaobj.plot_feature_stats(filename=str(out_dir / f"{base_name}_feature_stats.html"))
    ## COMMENT AR: Not working
    # ddaobj.save(filename=str(mzpkl_path)) ## not working anymore
    ddaobj.save_features(filename=str(out_dir / f"{base_name}.csv"))
    ddaobj.save_mgf(
        filename=str(out_dir / f"{base_name}.mgf"),
        selection=mgf_export,
        centroid=centroid,
    )
    ddaobj.save_dda_stats(filename=str(out_dir / f"{base_name}_stats.csv"))

    print(f"✅ Done: {file_path.name} -> {out_dir}\n")


# === Argument Parser ===
def parse_args():
    parser = argparse.ArgumentParser(
        description="🧬 Process mass spectrometry data using ms12"
    )
    parser.add_argument("input_path", type=Path, help="Input file or directory")
    parser.add_argument(
        "--dest",
        type=Path,
        default=None,
        help="Destination directory (default: same as source)",
    )
    parser.add_argument(
        "--chrom_peak_snr",
        type=float,
        default=10.0,
        help="Chrom peak SNR threshold (default: 10.0)",
    )
    parser.add_argument(
        "--chrom_fwhm", type=float, default=4.0, help="Chrom peak width (default: 4.0)"
    )
    parser.add_argument(
        "--noise", type=float, default=500.0, help="Noise threshold (default: 500.0)"
    )
    parser.add_argument(
        "--window_size", type=float, default=0.3, help="Window size (default: 0.3)"
    )
    parser.add_argument(
        "--mgf_export",
        choices=["best", "all"],
        default="all",
        help="MGF export mode ('best' or 'all')",
    )
    parser.add_argument("--recursive", action="store_true", help="Search in subfolders")
    parser.add_argument(
        "--no-centroid",
        dest="centroid",
        action="store_false",
        help="Disable centroiding",
    )
    return parser.parse_args()


# === Entry Point ===
def main():
    args = parse_args()

    if not args.input_path.exists():
        print(f"❌ Input not found: {args.input_path}")
        sys.exit(1)

    if args.input_path.is_dir():
        print(f"📁 Processing directory: {args.input_path}\n")
        supported_exts = {".wiff", ".mzml", ".raw", ".mzpkl"}

        files = list(args.input_path.glob("**/*.mzML" if args.recursive else "*.mzML"))
        files += list(args.input_path.glob("**/*.wiff" if args.recursive else "*.wiff"))
        files = [f for f in files if f.suffix.lower() in supported_exts]

        for file_path in files:
            process_file(
                file_path,
                args.dest,
                args.chrom_peak_snr,
                args.chrom_fwhm,
                args.noise,
                args.window_size,
                args.mgf_export,
                args.centroid,
            )

    elif args.input_path.is_file():
        process_file(
            args.input_path,
            args.dest,
            args.chrom_peak_snr,
            args.chrom_fwhm,
            args.noise,
            args.window_size,
            args.mgf_export,
            args.centroid,
        )
    else:
        print("❗ Error: Input must be a file or directory.")
        sys.exit(1)


if __name__ == "__main__":
    main()
