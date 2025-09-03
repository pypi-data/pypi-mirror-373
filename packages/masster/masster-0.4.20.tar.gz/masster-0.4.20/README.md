# MASSter

**MASSter** is a comprehensive Python package for mass spectrometry data analysis, designed for metabolomics and LC-MS data processing. It provides tools for feature detection, alignment, consensus building, and interactive visualization of mass spectrometry datasets. It is designed to deal with DDA, and hides functionalities for DIA and ZTScan DIA data. 

This is a poorly documented, stable branch of the development codebase in use in the Zamboni lab. 

Some of the core processing functions are derived from OpenMS. We use the same nomenclature and refer to their documentation for an explanation of the parameters. To a large extent, however, you should be able to use the defaults (=no parameters) when calling processing steps.


## Installation

```bash
pip install masster
```

### Basic Workflow for analyzing LC-MS study with 2-... samples

```python
import masster

# Initialize the Study object with the default folder
study = masster.Study(default_folder=r'D:\...\mylcms')

# Load data from folder with raw data, here: WIFF
study.add(r'D:\...\...\...\*.wiff')

# Perform retention time correction
study.align(rt_max_diff=2.0)
study.plot_alignment()

# Find consensus features
study.merge(min_samples=3)
study.plot_consensus_2d()

# Retrieve missing data for quantification
study.fill()

# Integrate according to consensus metadata
study.integrate()

# export results
study.export_mgf()
study.export_mztab()
study.export_xlsx()
study.export_parquet()

# Save the study to .study5
study.save()
```

## Requirements

- Python ≥ 3.11
- Key dependencies: pandas, polars, numpy, scipy, matplotlib, bokeh, holoviews, panel
- See `pyproject.toml` for complete dependency list

## License

GNU Affero General Public License v3

## Citation

If you use Masster in your research, please cite this repository.
