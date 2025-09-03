"""
chrom.py

This module provides tools for processing and analyzing chromatographic data.
It defines the `chrom` class for handling retention time and intensity profiles,
including peak detection, chromatographic feature extraction, and visualization.

Key Features:
- **Chromatogram Processing**: Handle retention time and intensity data arrays.
- **Peak Detection**: Advanced chromatographic peak picking with customizable parameters.
- **Feature Extraction**: Extract chromatographic features including peak areas, widths, and shapes.
- **Baseline Correction**: Remove baseline contributions from chromatographic data.
- **Visualization**: Plot chromatograms with peak annotations and feature highlighting.
- **Quality Metrics**: Calculate peak quality metrics and chromatographic statistics.

Dependencies:
- `numpy`: For numerical array operations and mathematical computations.
- `polars`: For structured data handling and tabulation.
- `scipy.signal`: For signal processing, peak detection, and chromatographic algorithms.

Classes:
- `chrom`: Main class for chromatographic data processing, providing methods for
  peak detection, feature extraction, and analysis.

Example Usage:
```python
from chrom import chrom
import numpy as np

# Create chromatogram from retention time and intensity arrays
rt = np.linspace(0, 300, 1000)  # 5 minutes in seconds
intensity = np.random.normal(1000, 100, 1000)  # Baseline noise
# Add a peak
peak_center = 150
peak_intensity = np.exp(-((rt - peak_center) ** 2) / (2 * 10**2)) * 10000
intensity += peak_intensity

chromatogram = chrom(rt=rt, inty=intensity, label="Sample 1")
chromatogram.find_peaks()
chromatogram.plot()
```

See Also:
- `single.py`: For complete mass spectrometry file processing including chromatograms.
- `parameters.chrom_parameters`: For chromatography-specific parameter configuration.

"""

import importlib

from dataclasses import dataclass

import numpy as np
import polars

from scipy.signal import find_peaks
from scipy.signal import peak_prominences


@dataclass
class Chromatogram:
    """
    A class for processing and analyzing chromatographic data.

    The `chrom` class provides comprehensive tools for handling chromatographic profiles,
    including retention time and intensity data processing, peak detection, feature
    extraction, and quality assessment. It supports various chromatographic data types
    and provides methods for baseline correction and peak characterization.

    Attributes:
        rt (np.ndarray): Retention time values (typically in seconds).
        inty (np.ndarray): Intensity values corresponding to retention times.
        label (str, optional): Text label for the chromatogram.
        rt_unit (str, optional): Unit for retention time ("sec" or "min").
        history (str): Processing history log.
        bl (np.ndarray, optional): Baseline values for baseline correction.
        feature_start (float, optional): Start retention time of detected feature.
        feature_end (float, optional): End retention time of detected feature.
        feature_apex (float, optional): Apex retention time of detected feature.
        feature_area (float, optional): Integrated area of detected feature.

    Key Methods:
        - `find_peaks()`: Detect chromatographic peaks with customizable parameters.
        - `calculate_area()`: Integrate peak areas for quantification.
        - `baseline_correct()`: Remove baseline contributions.
        - `plot()`: Visualize chromatographic data with annotations.
        - `get_statistics()`: Calculate chromatographic quality metrics.

    Example Usage:
        >>> import numpy as np
        >>> from masster import Chromatogram
        >>> rt = np.linspace(0, 300, 1000)
        >>> intensity = np.random.normal(1000, 100, 1000)
        >>> chromatogram = Chromatogram(rt=rt, inty=intensity, label="EIC m/z 150")
        >>> chromatogram.find_peaks()
        >>> chromatogram.calculate_area()

    See Also:
        - `ddafile`: For complete mass spectrometry data including chromatograms.
        - `ChromParameters`: For chromatography-specific parameter configuration.
    """

    def __init__(
        self,
        rt: np.ndarray | None = None,
        inty: np.ndarray | None = None,
        label: str | None = None,
        rt_unit: str | None = None,
        **kwargs,
    ):
        # Handle case where rt and inty might be in kwargs (from from_dict/from_json)
        if rt is None and "rt" in kwargs:
            rt = kwargs.pop("rt")
        if inty is None and "inty" in kwargs:
            inty = kwargs.pop("inty")

        # Ensure rt and inty are provided
        if rt is None or inty is None:
            raise ValueError("rt and inty arrays are required")

        self.label = label
        self.rt = np.asarray(rt, dtype=np.float64)
        # if all rt are less than 60, assume minutes
        if rt_unit is None:
            if np.all(self.rt < 60):
                self.rt_unit = "sec"
            else:
                self.rt_unit = "sec"
        else:
            self.rt_unit = rt_unit
        self.inty = np.asarray(inty, dtype=np.float64)
        self.history = ""
        self.bl: float | None = None
        self.feature_start: float | None = None
        self.feature_end: float | None = None
        self.feature_apex: float | None = None
        self.feature_area: float | None = None
        self.lib_rt: float | None = None  # Library retention time for reference
        self.__dict__.update(kwargs)
        # sort rt and inty by rt
        if len(self.rt) > 0:
            sorted_indices = np.argsort(self.rt)
            self.rt = self.rt[sorted_indices]
            self.inty = self.inty[sorted_indices]
        self.__post_init__()

    # a spectrum is defined by mz and intensity values. It can also have ms_level, centroided, and label. If additional arguments are provided, they are added to the dictionary.

    def __post_init__(self):
        """Validate and ensure arrays are numpy arrays."""
        self.rt = np.asarray(self.rt)
        self.inty = np.asarray(self.inty)
        if self.rt.shape != self.inty.shape:
            raise ValueError("rt and intensity arrays must have the same shape")

    def __len__(self):
        """Return the number of points in the chromatogram."""
        return len(self.rt)

    def reload(self):
        """
        Reloads the module and updates the class reference of the instance.
        """
        # Get the name of the module containing the class
        modname = self.__class__.__module__
        # Import the module
        mod = __import__(modname, fromlist=[modname.split(".")[0]])
        # Reload the module
        importlib.reload(mod)
        # Get the updated class reference from the reloaded module
        new = getattr(mod, self.__class__.__name__)
        # Update the class reference of the instance
        self.__class__ = new

    def to_dict(self):
        # return a dictionary representation of the chromatogram. include all the attributes
        # Create a copy to avoid modifying the original object
        result = {}

        # Handle numpy arrays by creating copies and converting to lists
        for key, value in self.__dict__.items():
            if isinstance(value, np.ndarray):
                result[key] = value.copy().tolist()
            elif isinstance(value, (list, dict)):
                # Create copies of mutable objects
                import copy

                result[key] = copy.deepcopy(value)
            else:
                # Immutable objects can be copied directly
                result[key] = value

        # Sort rt and inty in the result (not the original object)
        if "rt" in result and "inty" in result and len(result["rt"]) > 0:
            rt_array = np.array(result["rt"])
            inty_array = np.array(result["inty"])
            sorted_indices = np.argsort(rt_array)
            result["rt"] = np.round(rt_array[sorted_indices], 3).tolist()
            result["inty"] = np.round(inty_array[sorted_indices], 3).tolist()

        return result

    @classmethod
    def from_dict(cls, data):
        """
        Create a Chromatogram instance from a dictionary of attributes.
        Args:
            data (dict): Dictionary containing chromatogram attributes.
        Returns:
            Chromatogram: New instance with attributes set from the dictionary.
        """
        # Create instance directly from data dictionary
        return cls(**data)

    def to_json(self):
        """
        Serialize the chromatogram to a JSON string.

        Returns:
            str: JSON string representation of the chromatogram.
        """
        import json

        data = self.to_dict()
        return json.dumps(data, indent=2)

    @classmethod
    def from_json(cls, json_str):
        """
        Create a Chromatogram instance from a JSON string.

        Args:
            json_str (str): JSON string containing chromatogram data.

        Returns:
            Chromatogram: New instance with attributes set from the JSON data.
        """
        import json

        data = json.loads(json_str)
        return cls.from_dict(data)

    def copy(self):
        """
        Create a copy of the chromatogram instance.
        Returns:
            A new instance of the chromatogram with the same data.
        """
        return Chromatogram(
            rt=self.rt.copy(),
            inty=self.inty.copy(),
            label=self.label,
            rt_unit=self.rt_unit,
            **{k: v.copy() for k, v in self.__dict__.items() if isinstance(v, np.ndarray)},
        )

    def pandalize(self):
        """
        Convert the spectrum to a pandas DataFrame.
        This is an alias for to_df.
        """
        return self.to_df()

    def to_df(self):
        """
        Convert the spectrum to a pandas dataframe. include all the attributes that have the same length as mz
        find all attributes that are numpy arrays and have the same length as mz
        """
        data = {
            key: val for key, val in self.__dict__.items() if isinstance(val, np.ndarray) and val.size == self.rt.size
        }
        return polars.DataFrame(data)

    def plot(self, ax=None, width=800, height=300, **kwargs):
        """
        Plot the chromatogram using bokeh
        """
        import bokeh.plotting as bp

        from bokeh.models import ColumnDataSource
        from bokeh.models import HoverTool

        # Import Span with fallback - use type: ignore to avoid mypy issues with different Bokeh versions
        try:
            from bokeh.models import Span  # type: ignore
        except ImportError:
            from bokeh.models import VSpan as Span

        if ax is None:
            p = bp.figure(
                title=self.label,
                width=width,
                height=height,
            )
            p.xaxis.axis_label = f"rt ({self.rt_unit})"
            p.yaxis.axis_label = "inty"
        else:
            p = ax

        # sort by rt
        sorted_indices = np.argsort(self.rt)
        self.rt = self.rt[sorted_indices]
        self.inty = self.inty[sorted_indices]

        source = ColumnDataSource(data={"rt": self.rt, "inty": self.inty})

        line = p.line("rt", "inty", source=source, **kwargs)

        # Add hover tool for the chromatogram line
        hover = HoverTool(
            tooltips=[
                ("rt", "@rt"),
                ("inty", "@inty"),
            ],
            renderers=[line],
        )
        p.add_tools(hover)

        # Add spans and hover tools for them
        span_renderers = []
        if "feature_start" in self.__dict__:
            feature_start = self.feature_start
            feature_end = self.feature_end
            # Create spans - may fail with different Bokeh versions but we handle it
            span_start = Span(
                location=feature_start,
                dimension="height",
                line_color="green",
                line_width=1,
                line_dash="dashed",
            )
            span_end = Span(
                location=feature_end,
                dimension="height",
                line_color="green",
                line_width=1,
                line_dash="dashed",
            )
            p.add_layout(span_start)
            p.add_layout(span_end)
            span_renderers.extend([span_start, span_end])
        if "feature_apex" in self.__dict__:
            feature_apex = self.feature_apex
            span_apex = Span(
                location=feature_apex,
                dimension="height",
                line_color="green",
                line_width=1,
            )
            p.add_layout(span_apex)
            span_renderers.append(span_apex)
        if "lib_rt" in self.__dict__:
            lib_rt = self.lib_rt
            span_lib = Span(
                location=lib_rt,
                dimension="height",
                line_color="red",
                line_width=1,
            )
            p.add_layout(span_lib)
            span_renderers.append(span_lib)

        # Add hover tool for spans (using a dummy invisible renderer, since Span is not a glyph)
        # Workaround: add invisible vbar glyphs at the span locations for hover
        vbar_data: dict[str, list] = {"rt": [], "top": [], "bottom": []}
        vbar_tooltips = []
        if "feature_start" in self.__dict__:
            vbar_data["rt"].append(self.feature_start)
            vbar_data["top"].append(np.max(self.inty))
            vbar_data["bottom"].append(np.min(self.inty))
            vbar_tooltips.append(("feature_start", str(self.feature_start)))
        if "feature_end" in self.__dict__:
            vbar_data["rt"].append(self.feature_end)
            vbar_data["top"].append(np.max(self.inty))
            vbar_data["bottom"].append(np.min(self.inty))
            vbar_tooltips.append(("feature_end", str(self.feature_end)))
        if "lib_rt" in self.__dict__:
            vbar_data["rt"].append(self.lib_rt)
            vbar_data["top"].append(np.max(self.inty))
            vbar_data["bottom"].append(np.min(self.inty))
            vbar_tooltips.append(("lib_rt", str(self.lib_rt)))
        if "feature_apex" in self.__dict__:
            vbar_data["rt"].append(self.feature_apex)
            vbar_data["top"].append(np.max(self.inty))
            vbar_data["bottom"].append(np.min(self.inty))
            vbar_tooltips.append(("feature_apex", str(self.feature_apex)))
        if vbar_data["rt"]:
            vbar_source = ColumnDataSource(data=vbar_data)
            vbars = p.vbar(
                x="rt",
                top="top",
                bottom="bottom",
                width=0.01,
                alpha=0,
                source=vbar_source,
            )
            hover_span = HoverTool(tooltips=[("rt", "@rt")], renderers=[vbars])
            p.add_tools(hover_span)

        bp.show(p)

    def find_peaks(self, order_by="prominences"):
        sinty = self.inty
        p = []
        if len(sinty) > 5:
            # smooth
            # sinty = savgol_filter(sinty, window_length=7, polyorder=2)
            p, props = find_peaks(
                sinty,
                prominence=(None, None),
                height=(None, None),
                width=(None, None),
            )

        # TODO Instance attributes defined outside __init__
        if len(p) == 0:
            self.feature_apex = None
            self.feature_coherence = 0.0
            self.peak_rts = np.array([])
            self.peak_heights = np.array([])
            self.peak_prominences = np.array([])
            self.peak_widths = np.array([])
            self.peak_left_bases = np.array([])
            self.peak_right_bases = np.array([])
        else:
            prt = self.rt[p]
            # remove prt with prt < c['feature_start'] or prt > c['feature_end']
            mask = (prt >= self.feature_start) & (prt <= self.feature_end)
            # apply mask to all arrays in props
            if mask.any():
                for key in props:
                    if isinstance(props[key], np.ndarray):
                        props[key] = props[key][mask]
                # order peaks by the specified order
                p = p[mask]
                prt = prt[mask]
            if order_by in props:
                # descending order
                order = np.argsort(props[order_by])[::-1]
            else:
                order = np.arange(len(prt))

            # add to self
            self.feature_apex = prt[order[0]]
            self.feature_coherence = 0.0
            self.peak_rts = prt[order]
            self.peak_heights = self.inty[p][order]
            self.peak_prominences = peak_prominences(self.inty, p)[0][order]
            self.peak_widths = props["widths"][order]
            self.peak_left_bases = self.rt[props["left_bases"][order]]
            self.peak_right_bases = self.rt[props["right_bases"][order]]
            self.feature_start = self.peak_left_bases[0]
            self.feature_end = self.peak_right_bases[0]

            # select inty for rt between feature_start and feature_end
            mask = (
                (self.rt >= self.feature_start)
                & (self.rt <= self.feature_end)
                & (self.rt >= self.feature_apex - 4)
                & (self.rt <= self.feature_apex + 4)
            )

            sinty = sinty[mask]
            # calculate how many times the derivative of self.inty crosses zero
            if len(sinty) > 3:
                self.feature_coherence = 1 - np.sum(
                    np.diff(np.sign(np.diff(sinty))) != 0,
                ) / (len(sinty) - 3)
        return self

    def integrate(self):
        """
        Integrate the chromatogram between feature_start and feature_end.
        """
        if self.feature_start is None or self.feature_end is None:
            raise ValueError(
                "feature_start and feature_end must be set before integration",
            )

        # At this point, mypy knows feature_start and feature_end are not None
        mask = (self.rt >= self.feature_start) & (self.rt <= self.feature_end)
        area_result = np.trapezoid(self.inty[mask], self.rt[mask])
        self.feature_area = float(area_result)
        if self.bl is not None:
            # subtract baseline
            self.feature_area -= self.bl * (self.feature_end - self.feature_start)
        if self.feature_area < 0:
            self.feature_area = 0.0

    def get_area(self):
        """
        Get the area of the chromatogram between feature_start and feature_end.
        If the area is not calculated, it will be calculated first.
        """
        if self.feature_area is None:
            self.integrate()
        return self.feature_area
