from __future__ import annotations

from datetime import datetime
from typing import Any

import holoviews as hv
import numpy as np
import panel
import polars as pl
from tqdm import tqdm

hv.extension("bokeh")


# Replace any unaliased import that could be shadowed:
# from bokeh.layouts import row
from bokeh.layouts import row as bokeh_row


def _isolated_save_plot(plot_object, filename, abs_filename, logger, plot_title="Plot"):
    """
    Save a plot using isolated file saving that doesn't affect global Bokeh state.
    This prevents browser opening issues when mixing file and notebook outputs.
    """
    if filename.endswith(".html"):
        # Use isolated file saving that doesn't affect global output state
        from bokeh.resources import Resources
        from bokeh.embed import file_html

        # Create HTML content without affecting global state
        resources = Resources(mode='cdn')
        html = file_html(plot_object, resources, title=plot_title)

        # Write directly to file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)

        logger.info(f"Plot saved to: {abs_filename}")

    elif filename.endswith(".png"):
        try:
            from bokeh.io.export import export_png
            export_png(plot_object, filename=filename)
            logger.info(f"Plot saved to: {abs_filename}")
        except Exception:
            # Fall back to HTML if PNG export not available
            html_filename = filename.replace('.png', '.html')
            from bokeh.resources import Resources
            from bokeh.embed import file_html

            resources = Resources(mode='cdn')
            html = file_html(plot_object, resources, title=plot_title)

            with open(html_filename, 'w', encoding='utf-8') as f:
                f.write(html)

            logger.warning(f"PNG export not available, saved as HTML instead: {html_filename}")
    elif filename.endswith(".pdf"):
        # Try to save as PDF, fall back to HTML if not available
        try:
            from bokeh.io.export import export_pdf
            export_pdf(plot_object, filename=filename)
            logger.info(f"Plot saved to: {abs_filename}")
        except ImportError:
            # Fall back to HTML if PDF export not available
            html_filename = filename.replace('.pdf', '.html')
            from bokeh.resources import Resources
            from bokeh.embed import file_html

            resources = Resources(mode='cdn')
            html = file_html(plot_object, resources, title=plot_title)

            with open(html_filename, 'w', encoding='utf-8') as f:
                f.write(html)

            logger.warning(f"PDF export not available, saved as HTML instead: {html_filename}")
    else:
        # Default to HTML for unknown extensions using isolated approach
        from bokeh.resources import Resources
        from bokeh.embed import file_html

        resources = Resources(mode='cdn')
        html = file_html(plot_object, resources, title=plot_title)

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)

        logger.info(f"Plot saved to: {abs_filename}")


def _isolated_show_notebook(plot_object):
    """
    Show a plot in notebook using isolated display that resets Bokeh state.
    This prevents browser opening issues when mixing file and notebook outputs.
    """
    from bokeh.io import reset_output, output_notebook, show
    import holoviews as hv
    import warnings
    import logging

    # Suppress both warnings and logging messages for the specific Bokeh callback warnings
    # that occur when Panel components with Python callbacks are converted to standalone Bokeh
    bokeh_logger = logging.getLogger('bokeh.embed.util')
    original_level = bokeh_logger.level
    bokeh_logger.setLevel(logging.ERROR)  # Suppress WARNING level messages

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message=".*standalone HTML/JS output.*", category=UserWarning)
        warnings.filterwarnings("ignore", message=".*real Python callbacks.*", category=UserWarning)

        try:
            # First clear all output state
            reset_output()

            # Set notebook mode
            output_notebook(hide_banner=True)

            # Reset Holoviews to notebook mode
            hv.extension('bokeh', logo=False)
            hv.output(backend='bokeh', mode='jupyter')

            # Show in notebook
            show(plot_object)
        finally:
            # Restore original logging level
            bokeh_logger.setLevel(original_level)


def _isolated_save_panel_plot(panel_obj, filename, abs_filename, logger, plot_title):
    """
    Save a Panel plot using isolated approach that doesn't affect global Bokeh state.

    Args:
        panel_obj: Panel object to save
        filename: Target filename
        abs_filename: Absolute path for logging
        logger: Logger instance
        plot_title: Title for logging
    """
    import os  # Import os for path operations

    if filename.endswith(".html"):
        # Panel save method should be isolated but let's be sure
        try:
            # Save directly without affecting global Bokeh state
            panel_obj.save(filename, embed=True)
            logger.info(f"{plot_title} saved to: {abs_filename}")
        except Exception as e:
            logger.error(f"Failed to save {plot_title}: {e}")

    elif filename.endswith(".png"):
        try:
            from panel.io.save import save_png
            # Convert Panel to Bokeh models before saving
            bokeh_layout = panel_obj.get_root()
            save_png(bokeh_layout, filename=filename)
            logger.info(f"{plot_title} saved to: {abs_filename}")
        except Exception:
            # Fall back to HTML if PNG export not available
            html_filename = filename.replace('.png', '.html')
            abs_html_filename = os.path.abspath(html_filename)
            try:
                panel_obj.save(html_filename, embed=True)
                logger.warning(f"PNG export not available, saved as HTML instead: {abs_html_filename}")
            except Exception as e:
                logger.error(f"Failed to save {plot_title} as HTML fallback: {e}")

    elif filename.endswith(".pdf"):
        # Try to save as PDF, fall back to HTML if not available
        try:
            from bokeh.io.export import export_pdf
            bokeh_layout = panel_obj.get_root()
            export_pdf(bokeh_layout, filename=filename)
            logger.info(f"{plot_title} saved to: {abs_filename}")
        except ImportError:
            # Fall back to HTML if PDF export not available
            html_filename = filename.replace('.pdf', '.html')
            abs_html_filename = os.path.abspath(html_filename)
            try:
                panel_obj.save(html_filename, embed=True)
                logger.warning(f"PDF export not available, saved as HTML instead: {abs_html_filename}")
            except Exception as e:
                logger.error(f"Failed to save {plot_title} as HTML fallback: {e}")
    else:
        # Default to HTML for unknown extensions
        try:
            panel_obj.save(filename, embed=True)
            logger.info(f"{plot_title} saved to: {abs_filename}")
        except Exception as e:
            logger.error(f"Failed to save {plot_title}: {e}")


def _isolated_show_panel_notebook(panel_obj):
    """
    Show a Panel plot in notebook with state isolation to prevent browser opening.

    Args:
        panel_obj: Panel object to display
    """
    # Reset Bokeh state completely to prevent browser opening if output_file was called before
    from bokeh.io import reset_output, output_notebook
    import holoviews as hv

    # First clear all output state
    reset_output()

    # Set notebook mode
    output_notebook(hide_banner=True)

    # Reset Holoviews to notebook mode
    hv.extension('bokeh', logo=False)
    hv.output(backend='bokeh', mode='jupyter')

    # For Panel objects in notebooks, use on.extension and display inline
    import panel as on
    try:
        # Configure Panel for notebook display
        on.extension('bokeh', inline=True, comms='vscode')
        # Use IPython display to show inline instead of show()
        from IPython.display import display
        display(panel_obj)
    except Exception:
        # Fallback to regular Panel show
        panel_obj.show()


def plot_alignment(
    self,
    samples=50,
    filename: str | None = None,
    width: int = 450,
    height: int = 450,
    markersize: int = 3,
):
    """Visualize retention time alignment using two synchronized Bokeh scatter plots.

    Uses ``features_df`` to create side-by-side plots showing Original RT (left) 
    and Current/Aligned RT (right). If no alignment has been performed yet, 
    both plots show the current RT values.

    Parameters:
    - samples: List of sample identifiers (sample_uids or sample_names), or single int for random selection, or None for all samples.
    - filename: optional HTML file path to save the plot.
    - width/height: pixel size of each subplot.
    - markersize: base marker size.

    Returns:
    - Bokeh layout (row) containing the two synchronized plots.
    """
    # Local imports so the module can be used even if bokeh isn't needed elsewhere
    from bokeh.models import ColumnDataSource, HoverTool
    from bokeh.plotting import figure
    import pandas as pd

    # Check if features_df exists
    if self.features_df is None or self.features_df.is_empty():
        self.logger.error("No features_df found. Load features first.")
        return

    # Check required columns
    required_cols = ["rt", "mz", "inty"]
    missing = [c for c in required_cols if c not in self.features_df.columns]
    if missing:
        self.logger.error(f"Missing required columns in features_df: {missing}")
        return

    # Check if alignment has been performed
    has_alignment = "rt_original" in self.features_df.columns
    if not has_alignment:
        self.logger.warning("Column 'rt_original' not found - alignment has not been performed yet.")
        self.logger.info("Showing current RT values for both plots. Run align() first to see alignment comparison.")

    # Get sample_uids to filter by if specified
    sample_uids = self._get_sample_uids(samples) if samples is not None else None

    # Start with full features_df
    features_df = self.features_df

    # Filter by selected samples if specified
    if sample_uids is not None:
        features_df = features_df.filter(pl.col("sample_uid").is_in(sample_uids))
        if features_df.is_empty():
            self.logger.error("No features found for the selected samples.")
            return

    # Determine sample column
    sample_col = "sample_uid" if "sample_uid" in features_df.columns else "sample_name"
    if sample_col not in features_df.columns:
        self.logger.error("No sample identifier column found in features_df.")
        return

    # Get unique samples
    samples_list = features_df.select(pl.col(sample_col)).unique().to_series().to_list()

    # Build plotting data
    before_data: list[dict[str, Any]] = []
    after_data: list[dict[str, Any]] = []

    for sample_idx, sample in enumerate(samples_list):
        # Filter sample data
        sample_data = features_df.filter(pl.col(sample_col) == sample)
        
        # Sample data if too large for performance
        max_points_per_sample = 10000
        if sample_data.height > max_points_per_sample:
            self.logger.info(f"Sample {sample}: Sampling {max_points_per_sample} points from {sample_data.height} features for performance")
            sample_data = sample_data.sample(n=max_points_per_sample, seed=42)

        # Calculate max intensity for alpha scaling
        max_inty = sample_data.select(pl.col("inty").max()).item() or 1

        # Get sample information
        sample_uid = sample if sample_col == "sample_uid" else sample_data.select(pl.col("sample_uid")).item() if "sample_uid" in sample_data.columns else sample
        
        # Try to get actual sample name from samples_df if available
        sample_name = str(sample)  # fallback
        if hasattr(self, "samples_df") and self.samples_df is not None and sample_uid is not None:
            try:
                sample_name_result = (
                    self.samples_df.filter(pl.col("sample_uid") == sample_uid)
                    .select("sample_name")
                    .to_series()
                )
                if len(sample_name_result) > 0 and sample_name_result[0] is not None:
                    sample_name = str(sample_name_result[0])
            except Exception:
                # Keep the fallback value
                pass

        # Select columns to process
        cols_to_select = ["rt", "mz", "inty"]
        if has_alignment:
            cols_to_select.append("rt_original")
        
        sample_dict = sample_data.select(cols_to_select).to_dicts()

        for row_dict in sample_dict:
            rt_original = row_dict.get("rt_original", row_dict["rt"]) if has_alignment else row_dict["rt"]
            rt_current = row_dict["rt"]
            mz = row_dict["mz"]
            inty = row_dict["inty"]
            alpha = inty / max_inty
            size = markersize + 2 if sample_idx == 0 else markersize

            before_data.append({
                "rt": rt_original,
                "mz": mz,
                "inty": inty,
                "alpha": alpha,
                "sample_idx": sample_idx,
                "sample_name": sample_name,
                "sample_uid": sample_uid,
                "size": size,
            })
            after_data.append({
                "rt": rt_current,
                "mz": mz,
                "inty": inty,
                "alpha": alpha,
                "sample_idx": sample_idx,
                "sample_name": sample_name,
                "sample_uid": sample_uid,
                "size": size,
            })

    # Check if we have any data to plot
    if not before_data:
        self.logger.error("No data to plot.")
        return

    # Get sample colors from samples_df
    sample_idx_to_uid = {}
    for item in before_data:
        if item["sample_idx"] not in sample_idx_to_uid:
            sample_idx_to_uid[item["sample_idx"]] = item["sample_uid"]

    # Get colors from samples_df if available
    sample_uids_list = list(sample_idx_to_uid.values())
    color_map: dict[int, str] = {}
    
    if sample_uids_list and hasattr(self, "samples_df") and self.samples_df is not None:
        try:
            sample_colors = (
                self.samples_df.filter(pl.col("sample_uid").is_in(sample_uids_list))
                .select(["sample_uid", "sample_color"])
                .to_dict(as_series=False)
            )
            uid_to_color = dict(zip(sample_colors["sample_uid"], sample_colors["sample_color"]))
            
            for sample_idx, sample_uid in sample_idx_to_uid.items():
                color_map[sample_idx] = uid_to_color.get(sample_uid, "#1f77b4")
        except Exception:
            # Fallback to default colors if sample colors not available
            for sample_idx in sample_idx_to_uid.keys():
                color_map[sample_idx] = "#1f77b4"
    else:
        # Default colors
        for sample_idx in sample_idx_to_uid.keys():
            color_map[sample_idx] = "#1f77b4"

    # Add sample_color to data
    for item in before_data + after_data:
        item["sample_color"] = color_map.get(item["sample_idx"], "#1f77b4")

    # Create DataFrames
    before_df = pd.DataFrame(before_data)
    after_df = pd.DataFrame(after_data)

    # Create Bokeh figures
    title_before = "Original RT" if has_alignment else "Current RT (No Alignment)"
    title_after = "Aligned RT" if has_alignment else "Current RT (Copy)"
    
    p1 = figure(
        width=width,
        height=height,
        title=title_before,
        x_axis_label="Retention Time (s)",
        y_axis_label="m/z",
        tools="pan,wheel_zoom,box_zoom,reset,save",
    )
    p1.outline_line_color = None
    p1.background_fill_color = "white"
    p1.border_fill_color = "white"
    p1.min_border = 0

    p2 = figure(
        width=width,
        height=height,
        title=title_after,
        x_axis_label="Retention Time (s)",
        y_axis_label="m/z",
        tools="pan,wheel_zoom,box_zoom,reset,save",
        x_range=p1.x_range,
        y_range=p1.y_range,
    )
    p2.outline_line_color = None
    p2.background_fill_color = "white"
    p2.border_fill_color = "white"
    p2.min_border = 0

    # Plot data by sample
    unique_samples = sorted(list({item["sample_idx"] for item in before_data}))
    renderers_before = []
    renderers_after = []

    for sample_idx in unique_samples:
        sb = before_df[before_df["sample_idx"] == sample_idx]
        sa = after_df[after_df["sample_idx"] == sample_idx]
        color = color_map.get(sample_idx, "#1f77b4")

        if not sb.empty:
            src = ColumnDataSource(sb)
            r = p1.scatter("rt", "mz", size="size", color=color, alpha="alpha", source=src)
            renderers_before.append(r)

        if not sa.empty:
            src = ColumnDataSource(sa)
            r = p2.scatter("rt", "mz", size="size", color=color, alpha="alpha", source=src)
            renderers_after.append(r)

    # Add hover tools
    hover1 = HoverTool(
        tooltips=[
            ("Sample UID", "@sample_uid"),
            ("Sample Name", "@sample_name"),
            ("Sample Color", "$color[swatch]:sample_color"),
            ("RT", "@rt{0.00}"),
            ("m/z", "@mz{0.0000}"),
            ("Intensity", "@inty{0.0e0}"),
        ],
        renderers=renderers_before,
    )
    p1.add_tools(hover1)

    hover2 = HoverTool(
        tooltips=[
            ("Sample UID", "@sample_uid"),
            ("Sample Name", "@sample_name"),
            ("Sample Color", "$color[swatch]:sample_color"),
            ("RT", "@rt{0.00}"),
            ("m/z", "@mz{0.0000}"),
            ("Intensity", "@inty{0.0e0}"),
        ],
        renderers=renderers_after,
    )
    p2.add_tools(hover2)

    # Create layout
    layout = bokeh_row(p1, p2, sizing_mode="fixed", width=width, height=height)

    # Apply consistent save/display behavior
    if filename is not None:
        # Convert relative paths to absolute paths using study folder as base
        import os
        if not os.path.isabs(filename):
            filename = os.path.join(self.folder, filename)

        # Convert to absolute path for logging
        abs_filename = os.path.abspath(filename)

        # Use isolated file saving
        _isolated_save_plot(layout, filename, abs_filename, self.logger, "Alignment Plot")
    else:
        # Show in notebook when no filename provided
        _isolated_show_notebook(layout)

    return layout


def plot_consensus_2d(
    self,
    filename=None,
    colorby="number_samples",
    cmap=None,
    markersize=8,
    sizeby="inty_mean",
    scaling="static",
    alpha=0.7,
    width=600,
    height=450,
    mz_range=None,
    rt_range=None,
):
    """
    Plot consensus features in a 2D scatter plot with retention time vs m/z.

    Parameters:
        filename (str, optional): Path to save the plot
        colorby (str): Column name to use for color mapping (default: "number_samples")
        sizeby (str): Column name to use for size mapping (default: "inty_mean")
        markersize (int): Base marker size (default: 6)
        scaling (str): Controls whether points scale with zoom. Options:
                   'dynamic' - points use circle() and scale with zoom
                   'static' - points use scatter() and maintain fixed pixel size
        alpha (float): Transparency level (default: 0.7)
        cmap (str, optional): Color map name
        width (int): Plot width in pixels (default: 900)
        height (int): Plot height in pixels (default: 900)
        mz_range (tuple, optional): m/z range for filtering consensus features (min_mz, max_mz)
        rt_range (tuple, optional): Retention time range for filtering consensus features (min_rt, max_rt)
    """
    if self.consensus_df is None:
        self.logger.error("No consensus map found.")
        return
    data = self.consensus_df.clone()

    # Filter by mz_range and rt_range if provided
    if mz_range is not None:
        data = data.filter((pl.col("mz") >= mz_range[0]) & (pl.col("mz") <= mz_range[1]))
    if rt_range is not None:
        data = data.filter((pl.col("rt") >= rt_range[0]) & (pl.col("rt") <= rt_range[1]))

    if colorby not in data.columns:
        self.logger.error(f"Column {colorby} not found in consensus_df.")
        return
    if sizeby is not None and sizeby not in data.columns:
        self.logger.warning(f"Column {sizeby} not found in consensus_df.")
        sizeby = None
    # if sizeby is not None, set markersize to sizeby
    if sizeby is not None:
        # set markersize to sizeby
        if sizeby in ["inty_mean"]:
            # use log10 of sizeby
            # Filter out empty or all-NA entries before applying np.log10
            data = data.with_columns([
                pl.when(
                    (pl.col(sizeby).is_not_null()) & (pl.col(sizeby).is_finite()) & (pl.col(sizeby) > 0),
                )
                .then((pl.col(sizeby).log10() * markersize / 12).pow(2))
                .otherwise(markersize)
                .alias("markersize"),
            ])
        else:
            max_size = data[sizeby].max()
            data = data.with_columns([
                (pl.col(sizeby) / max_size * markersize).alias("markersize"),
            ])
    else:
        data = data.with_columns([pl.lit(markersize).alias("markersize")])
    # sort by ascending colorby
    data = data.sort(colorby)
    # convert consensus_id to string - check if column exists
    if "consensus_id" in data.columns:
        # Handle Object dtype by converting to string first
        data = data.with_columns([
            pl.col("consensus_id")
            .map_elements(
                lambda x: str(x) if x is not None else None,
                return_dtype=pl.Utf8,
            )
            .alias("consensus_id"),
        ])
    elif "consensus_uid" in data.columns:
        data = data.with_columns([
            pl.col("consensus_uid").cast(pl.Utf8).alias("consensus_id"),
        ])

    if cmap is None:
        cmap = "viridis"
    elif cmap == "grey":
        cmap = "Greys256"

    # plot with bokeh
    import bokeh.plotting as bp

    from bokeh.models import BasicTicker
    from bokeh.models import ColumnDataSource
    from bokeh.models import HoverTool
    from bokeh.models import LinearColorMapper
    from bokeh.io.export import export_png

    try:
        from bokeh.models import ColorBar  # type: ignore[attr-defined]
    except ImportError:
        from bokeh.models.annotations import ColorBar
    from bokeh.palettes import viridis

    # Import cmap for colormap handling
    from cmap import Colormap

    # Convert Polars DataFrame to pandas for Bokeh compatibility
    data_pd = data.to_pandas()
    source = ColumnDataSource(data_pd)

    # Handle colormap using cmap.Colormap
    try:
        # Get colormap palette using cmap
        if isinstance(cmap, str):
            colormap = Colormap(cmap)
            # Generate 256 colors and convert to hex
            import numpy as np
            import matplotlib.colors as mcolors

            colors = colormap(np.linspace(0, 1, 256))
            palette = [mcolors.rgb2hex(color) for color in colors]
        else:
            colormap = cmap
            # Try to use to_bokeh() method first
            try:
                palette = colormap.to_bokeh()
                # Ensure we got a color palette, not another mapper
                if not isinstance(palette, (list, tuple)):
                    # Fall back to generating colors manually
                    import numpy as np
                    import matplotlib.colors as mcolors

                    colors = colormap(np.linspace(0, 1, 256))
                    palette = [mcolors.rgb2hex(color) for color in colors]
            except AttributeError:
                # Fall back to generating colors manually
                import numpy as np
                import matplotlib.colors as mcolors

                colors = colormap(np.linspace(0, 1, 256))
                palette = [mcolors.rgb2hex(color) for color in colors]
    except (AttributeError, ValueError, TypeError) as e:
        # Fallback to viridis if cmap interpretation fails
        self.logger.warning(f"Could not interpret colormap '{cmap}': {e}, falling back to viridis")
        palette = viridis(256)

    color_mapper = LinearColorMapper(
        palette=palette,
        low=data[colorby].min(),
        high=data[colorby].max(),
    )
    # scatter plot rt vs mz
    p = bp.figure(
        width=width,
        height=height,
        title="Consensus map",
    )
    p.xaxis.axis_label = "Retention Time (min)"
    p.yaxis.axis_label = "m/z"
    scatter_renderer: Any = None
    if scaling.lower() in ["dyn", "dynamic"]:
        # Calculate appropriate radius for dynamic scaling based on data range
        rt_range = data["rt"].max() - data["rt"].min()
        mz_range = data["mz"].max() - data["mz"].min()
        # Use a fraction of the smaller dimension for radius, similar to sample plotting
        dynamic_radius = min(rt_range, mz_range) * 0.0005 * markersize
        
        scatter_renderer = p.circle(
            x="rt",
            y="mz",
            radius=dynamic_radius,
            fill_color={"field": colorby, "transform": color_mapper},
            line_color=None,
            alpha=alpha,
            source=source,
        )
    else:
        scatter_renderer = p.scatter(
            x="rt",
            y="mz",
            size="markersize",
            fill_color={"field": colorby, "transform": color_mapper},
            line_color=None,
            alpha=alpha,
            source=source,
        )
    # add hover tool
    # Start with base tooltips
    tooltips = [
        ("consensus_uid", "@consensus_uid"),
        ("consensus_id", "@consensus_id"),
        ("number_samples", "@number_samples"),
        ("number_ms2", "@number_ms2"),
        ("rt", "@rt"),
        ("mz", "@mz"),
        ("inty_mean", "@inty_mean"),
        ("iso_mean", "@iso_mean"),
        ("coherence_mean", "@chrom_coherence_mean"),
        ("prominence_scaled_mean", "@chrom_prominence_scaled_mean"),
    ]
    
    # Add id_top_* columns if they exist and have non-null values
    id_top_columns = ["id_top_name", "id_top_class", "id_top_adduct", "id_top_score"]
    for col in id_top_columns:
        if col in data.columns:
            # Check if the column has any non-null values
            if data.filter(pl.col(col).is_not_null()).height > 0:
                # Format score column with decimal places, others as strings
                if col == "id_top_score":
                    tooltips.append((col.replace("id_top_", "id_"), f"@{col}{{0.0000}}"))
                else:
                    tooltips.append((col.replace("id_top_", "id_"), f"@{col}"))
    
    hover = HoverTool(
        tooltips=tooltips,
        renderers=[scatter_renderer],
    )
    p.add_tools(hover)

    # add colorbar
    color_bar = ColorBar(
        color_mapper=color_mapper,
        label_standoff=12,
        location=(0, 0),
        title=colorby,
        ticker=BasicTicker(desired_num_ticks=8),
    )
    p.add_layout(color_bar, "right")

    if filename is not None:
        # Convert relative paths to absolute paths using study folder as base
        import os
        if not os.path.isabs(filename):
            filename = os.path.join(self.folder, filename)

        # Convert to absolute path for logging
        abs_filename = os.path.abspath(filename)

        # Use isolated file saving
        _isolated_save_plot(p, filename, abs_filename, self.logger, "Consensus 2D Plot")
    else:
        # Show in notebook when no filename provided
        _isolated_show_notebook(p)
    return p


def plot_samples_2d(
    self,
    samples=100,
    filename=None,
    markersize=2,
    size="dynamic",
    alpha_max=0.8,
    alpha="inty",
    max_features=50000,
    width=600,
    height=600,
    mz_range=None,
    rt_range=None,
):
    """
    Plot all feature maps for sample_uid in parameter uids in an overlaid scatter plot.
    Each sample is a different color. Alpha scales with intensity.
    OPTIMIZED VERSION: Uses vectorized operations and batch processing.

    Parameters:
        samples: Sample UIDs to plot
        filename (str, optional): Path to save the plot
        markersize (int): Base marker size (default: 2)
        size (str): Controls whether points scale with zoom. Options:
                   'dynamic' or 'dyn' - points use circle() and scale with zoom
                   'const', 'static' or other - points use scatter() and maintain fixed pixel size
        alpha_max (float): Maximum transparency level (default: 0.8)
        alpha (str): Column name to use for alpha mapping (default: "inty")
        cmap (str): Color map name (default: "Turbo256")
        max_features (int): Maximum number of features to plot (default: 50000)
        width (int): Plot width in pixels (default: 900)
        height (int): Plot height in pixels (default: 900)
        mz_range (tuple, optional): m/z range for filtering features (min_mz, max_mz)
        rt_range (tuple, optional): Retention time range for filtering features (min_rt, max_rt)
    """

    # Local bokeh imports to avoid heavy top-level dependency
    from bokeh.plotting import figure, show, output_file
    from bokeh.io.export import export_png
    from bokeh.models import ColumnDataSource, HoverTool

    sample_uids = self._get_sample_uids(samples)

    if not sample_uids:
        self.logger.error("No valid sample_uids provided.")
        return

    # Get sample colors from samples_df
    sample_colors = (
        self.samples_df.filter(pl.col("sample_uid").is_in(sample_uids))
        .select(["sample_uid", "sample_color"])
        .to_dict(as_series=False)
    )
    color_map = dict(zip(sample_colors["sample_uid"], sample_colors["sample_color"]))

    p = figure(
        width=width,
        height=height,
        title="Sample Features",
    )
    p.xaxis.axis_label = "Retention Time (RT)"
    p.yaxis.axis_label = "m/z"

    # OPTIMIZATION 1: Batch filter all features for selected samples at once
    features_batch = self.features_df.filter(pl.col("sample_uid").is_in(sample_uids))

    # Filter by mz_range and rt_range if provided
    if mz_range is not None:
        features_batch = features_batch.filter((pl.col("mz") >= mz_range[0]) & (pl.col("mz") <= mz_range[1]))
    if rt_range is not None:
        features_batch = features_batch.filter((pl.col("rt") >= rt_range[0]) & (pl.col("rt") <= rt_range[1]))

    if features_batch.is_empty():
        self.logger.error("No features found for the selected samples.")
        return

    # OPTIMIZATION 8: Fast sampling for very large datasets to maintain interactivity
    max_features_per_plot = max_features  # Limit for interactive performance
    total_features = len(features_batch)

    if total_features > max_features_per_plot:
        # OPTIMIZED: Much faster random sampling without groupby operations
        sample_ratio = max_features_per_plot / total_features
        self.logger.info(
            f"Large dataset detected ({total_features:,} features). "
            f"Sampling {sample_ratio:.1%} for visualization performance.",
        )

        # FAST: Use simple random sampling instead of expensive stratified sampling
        n_samples = min(max_features_per_plot, total_features)
        features_batch = features_batch.sample(n=n_samples, seed=42)

    # OPTIMIZATION 2: Join with samples_df to get sample names in one operation
    samples_info = self.samples_df.filter(pl.col("sample_uid").is_in(sample_uids))
    features_with_names = features_batch.join(
        samples_info.select(["sample_uid", "sample_name"]),
        on="sample_uid",
        how="left",
    )

    # OPTIMIZATION 4: Fast pre-calculation of alpha values for all features
    if alpha == "inty":
        # OPTIMIZED: Use efficient Polars operations instead of pandas groupby transform
        # Calculate max intensity per sample in Polars (much faster)
        max_inty_per_sample = features_with_names.group_by("sample_uid").agg(
            pl.col("inty").max().alias("max_inty"),
        )

        # Join back and calculate alpha efficiently
        features_batch = (
            features_with_names.join(
                max_inty_per_sample,
                on="sample_uid",
                how="left",
            )
            .with_columns(
                (pl.col("inty") / pl.col("max_inty") * alpha_max).alias("alpha"),
            )
            .drop("max_inty")
        )

        # Convert to pandas once after all Polars operations
        features_pd = features_batch.to_pandas()
    else:
        # Convert to pandas and add constant alpha
        features_pd = features_with_names.to_pandas()
        features_pd["alpha"] = alpha_max

    # OPTIMIZATION 9: NEW - Batch create all ColumnDataSources at once
    # Group all data by sample_uid and create sources efficiently
    sources = {}
    renderers: list[Any] = []

    # Pre-compute color mapping to avoid repeated lookups
    color_values = {}
    sample_names = {}

    # Decide whether to show tqdm based on log level (show for INFO/DEBUG/TRACE)
    tqdm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]

    for uid in tqdm(sample_uids, desc="Plotting BPCs", disable=tqdm_disable):
        sample_data = features_pd[features_pd["sample_uid"] == uid]
        if sample_data.empty:
            continue

        sample_name = sample_data["sample_name"].iloc[0]
        sample_names[uid] = sample_name
        color_values[uid] = color_map[uid]

    # OPTIMIZATION 10: Batch renderer creation with pre-computed values
    for uid in sample_uids:
        sample_data = features_pd[features_pd["sample_uid"] == uid]
        if sample_data.empty:
            continue

        sample_name = sample_names[uid]
        color_values[uid]

        # OPTIMIZATION 11: Direct numpy array access for better performance
        source = ColumnDataSource(
            data={
                "rt": sample_data["rt"].values,
                "mz": sample_data["mz"].values,
                "inty": sample_data["inty"].values,
                "alpha": sample_data["alpha"].values,
                "sample": np.full(len(sample_data), sample_name, dtype=object),
                "sample_color": np.full(len(sample_data), color_values[uid], dtype=object),
            },
        )

        sources[uid] = source

        # OPTIMIZATION 12: Use pre-computed color value
        # Create renderer with pre-computed values
        renderer: Any
        if size.lower() in ["dyn", "dynamic"]:
            renderer = p.circle(
                x="rt",
                y="mz",
                radius=markersize / 10,
                color=color_values[uid],
                alpha="alpha",
                legend_label=sample_name,
                source=source,
            )
        else:
            renderer = p.scatter(
                x="rt",
                y="mz",
                size=markersize,
                color=color_values[uid],
                alpha="alpha",
                legend_label=sample_name,
                source=source,
            )
        renderers.append(renderer)

    # OPTIMIZATION 13: Simplified hover tool for better performance with many samples
    if renderers:
        hover = HoverTool(
            tooltips=[
                ("sample", "@sample"),
                ("sample_color", "$color[swatch]:sample_color"),
                ("rt", "@rt{0.00}"),
                ("mz", "@mz{0.0000}"),
                ("intensity", "@inty{0.0e+0}"),
            ],
            renderers=renderers,
        )
        p.add_tools(hover)

    # Remove legend from plot
    # Only set legend properties if a legend was actually created to avoid Bokeh warnings
    if getattr(p, "legend", None) and len(p.legend) > 0:
        p.legend.visible = False

    # Apply consistent save/display behavior
    if filename is not None:
        # Convert relative paths to absolute paths using study folder as base
        import os
        if not os.path.isabs(filename):
            filename = os.path.join(self.folder, filename)

        # Convert to absolute path for logging
        abs_filename = os.path.abspath(filename)

        # Use isolated file saving
        _isolated_save_plot(p, filename, abs_filename, self.logger, "Samples 2D Plot")
    else:
        # Show in notebook when no filename provided
        _isolated_show_notebook(p)
    return


def plot_bpc(
    self,
    samples=100,
    title: str | None = None,
    filename: str | None = None,
    width: int = 1000,
    height: int = 300,
    original: bool = False,
):
    """
    Plot Base Peak Chromatograms (BPC) for selected samples overlaid using Bokeh.

    This collects per-sample BPCs via `get_bpc(self, sample=uid)` and overlays them.
    Colors are mapped per-sample using the same Turbo256 palette as `plot_samples_2d`.
    Parameters:
        original (bool): If True, attempt to map RTs back to original RTs using `features_df`.
                         If False (default), return current/aligned RTs.
    """
    # Local imports to avoid heavy top-level deps / circular imports
    from bokeh.plotting import figure, show, output_file
    from bokeh.models import ColumnDataSource, HoverTool
    from bokeh.io.export import export_png
    from masster.study.helpers import get_bpc

    sample_uids = self._get_sample_uids(samples)
    if not sample_uids:
        self.logger.error("No valid sample_uids provided for BPC plotting.")
        return

    # Debug: show which sample_uids we will process
    self.logger.debug(f"plot_bpc: sample_uids={sample_uids}")

    # Get sample colors from samples_df
    sample_colors = (
        self.samples_df.filter(pl.col("sample_uid").is_in(sample_uids))
        .select(["sample_uid", "sample_color"])
        .to_dict(as_series=False)
    )
    color_map = dict(zip(sample_colors["sample_uid"], sample_colors["sample_color"]))

    # If plotting original (uncorrected) RTs, use the requested title.
    if original:
        plot_title = "Base Peak Chromatogarms (uncorrected)"
    else:
        plot_title = title or "Base Peak Chromatograms"

    # Get rt_unit from the first chromatogram, default to "s" if not available
    rt_unit = "s"
    for uid in sample_uids:
        try:
            first_chrom = get_bpc(self, sample=uid, label=None, original=original)
            if hasattr(first_chrom, "rt_unit"):
                rt_unit = first_chrom.rt_unit
                break
        except Exception:
            continue

    p = figure(width=width, height=height, title=plot_title, tools="pan,wheel_zoom,box_zoom,reset,save")
    p.xaxis.axis_label = f"Retention Time ({rt_unit})"
    p.yaxis.axis_label = "Intensity"

    renderers = []

    # Build sample name mapping once
    samples_info = None
    if hasattr(self, "samples_df") and self.samples_df is not None:
        try:
            samples_info = self.samples_df.to_pandas()
        except Exception:
            samples_info = None

    for uid in sample_uids:
        try:
            chrom = get_bpc(self, sample=uid, label=None, original=original)
        except Exception as e:
            # log and skip samples we can't compute BPC for
            self.logger.debug(f"Skipping sample {uid} for BPC: {e}")
            continue

        # extract arrays
        try:
            # prefer Chromatogram API
            chrom_dict = (
                chrom.to_dict()
                if hasattr(chrom, "to_dict")
                else {"rt": getattr(chrom, "rt"), "inty": getattr(chrom, "inty")}
            )
            rt = chrom_dict.get("rt")
            inty = chrom_dict.get("inty")
        except Exception:
            try:
                rt = chrom.rt
                inty = chrom.inty
            except Exception as e:
                self.logger.debug(f"Invalid chromatogram for sample {uid}: {e}")
                continue

        if rt is None or inty is None:
            continue

        # Ensure numpy arrays
        import numpy as _np

        rt = _np.asarray(rt)
        inty = _np.asarray(inty)
        if rt.size == 0 or inty.size == 0:
            continue

        # Sort by rt
        idx = _np.argsort(rt)
        rt = rt[idx]
        inty = inty[idx]

        sample_name = str(uid)
        if samples_info is not None:
            try:
                row = samples_info[samples_info["sample_uid"] == uid]
                if not row.empty:
                    sample_name = row.iloc[0].get("sample_name", sample_name)
            except Exception:
                pass
        # Determine color for this sample early so we can log it
        color = color_map.get(uid, "#000000")

        # Debug: log sample processing details
        self.logger.debug(
            f"Processing BPC for sample_uid={uid}, sample_name={sample_name}, rt_len={rt.size}, color={color}",
        )

        data = {"rt": rt, "inty": inty, "sample": [sample_name] * len(rt), "sample_color": [color] * len(rt)}
        src = ColumnDataSource(data)

        r_line = p.line("rt", "inty", source=src, line_width=1, color=color, legend_label=str(sample_name))
        r_points = p.scatter("rt", "inty", source=src, size=2, color=color, alpha=0.6)
        renderers.append(r_line)

    if not renderers:
        self.logger.warning("No BPC curves to plot for the selected samples.")
        return

    hover = HoverTool(
        tooltips=[
            ("sample", "@sample"),
            ("sample_color", "$color[swatch]:sample_color"),
            ("rt", "@rt{0.00}"),
            ("inty", "@inty{0.00e0}"),
        ],
        renderers=renderers,
    )
    p.add_tools(hover)

    # Only set legend properties if a legend was actually created to avoid Bokeh warnings
    if getattr(p, "legend", None) and len(p.legend) > 0:
        p.legend.visible = False

    # Apply consistent save/display behavior
    if filename is not None:
        # Convert relative paths to absolute paths using study folder as base
        import os
        if not os.path.isabs(filename):
            filename = os.path.join(self.folder, filename)

        # Convert to absolute path for logging
        abs_filename = os.path.abspath(filename)

        # Use isolated file saving
        _isolated_save_plot(p, filename, abs_filename, self.logger, "BPC Plot")
    else:
        # Show in notebook when no filename provided
        _isolated_show_notebook(p)

    return p


def plot_eic(
    self,
    mz,
    mz_tol=None,
    samples=100,
    title: str | None = None,
    filename: str | None = None,
    width: int = 1000,
    height: int = 300,
    original: bool = False,
):
    """
    Plot Extracted Ion Chromatograms (EIC) for a target m/z (± mz_tol) for selected samples.

    Parameters mirror `plot_bpc` with additional `mz` and `mz_tol` arguments. The function
    retrieves a Sample object for each sample UID, calls `sample.get_eic(mz, mz_tol)`, and
    overlays the resulting chromatograms.

    Args:
        mz_tol: m/z tolerance in Da. If None, uses study.parameters.eic_mz_tol as default.
    """
    # Local imports to avoid heavy top-level deps / circular imports
    from bokeh.plotting import figure, show, output_file
    from bokeh.models import ColumnDataSource, HoverTool
    from bokeh.io.export import export_png
    from masster.study.helpers import get_eic

    # Use study's eic_mz_tol parameter as default if not provided
    if mz_tol is None:
        mz_tol = self.parameters.eic_mz_tol

    if mz is None:
        self.logger.error("mz must be provided for EIC plotting")
        return

    sample_uids = self._get_sample_uids(samples)
    if not sample_uids:
        self.logger.error("No valid sample_uids provided for EIC plotting.")
        return

    # Get sample colors from samples_df
    sample_colors = (
        self.samples_df.filter(pl.col("sample_uid").is_in(sample_uids))
        .select(["sample_uid", "sample_color"])
        .to_dict(as_series=False)
    )
    color_map = dict(zip(sample_colors["sample_uid"], sample_colors["sample_color"]))

    plot_title = title or f"Extracted Ion Chromatograms (m/z={mz:.4f} ± {mz_tol})"

    # Get rt_unit from the first chromatogram, default to "s" if not available
    rt_unit = "s"
    for uid in sample_uids:
        try:
            first_chrom = get_eic(self, sample=uid, mz=mz, mz_tol=mz_tol, label=None)
            if hasattr(first_chrom, "rt_unit"):
                rt_unit = first_chrom.rt_unit
                break
        except Exception:
            continue

    p = figure(width=width, height=height, title=plot_title, tools="pan,wheel_zoom,box_zoom,reset,save")
    p.xaxis.axis_label = f"Retention Time ({rt_unit})"
    p.yaxis.axis_label = "Intensity"

    renderers = []

    # Build sample name mapping once
    samples_info = None
    if hasattr(self, "samples_df") and self.samples_df is not None:
        try:
            samples_info = self.samples_df.to_pandas()
        except Exception:
            samples_info = None

    for uid in sample_uids:
        try:
            chrom = get_eic(self, sample=uid, mz=mz, mz_tol=mz_tol, label=None)
        except Exception as e:
            # log and skip samples we can't compute EIC for
            self.logger.debug(f"Skipping sample {uid} for EIC: {e}")
            continue

        # extract arrays
        try:
            # prefer Chromatogram API
            chrom_dict = (
                chrom.to_dict()
                if hasattr(chrom, "to_dict")
                else {"rt": getattr(chrom, "rt"), "inty": getattr(chrom, "inty")}
            )
            rt = chrom_dict.get("rt")
            inty = chrom_dict.get("inty")
        except Exception:
            try:
                rt = chrom.rt
                inty = chrom.inty
            except Exception as e:
                self.logger.debug(f"Invalid chromatogram for sample {uid}: {e}")
                continue

        if rt is None or inty is None:
            continue

        import numpy as _np

        rt = _np.asarray(rt)
        inty = _np.asarray(inty)
        if rt.size == 0 or inty.size == 0:
            continue

        # Sort by rt
        idx = _np.argsort(rt)
        rt = rt[idx]
        inty = inty[idx]

        sample_name = str(uid)
        if samples_info is not None:
            try:
                row = samples_info[samples_info["sample_uid"] == uid]
                if not row.empty:
                    sample_name = row.iloc[0].get("sample_name", sample_name)
            except Exception:
                pass

        color = color_map.get(uid, "#000000")

        data = {"rt": rt, "inty": inty, "sample": [sample_name] * len(rt), "sample_color": [color] * len(rt)}
        src = ColumnDataSource(data)

        r_line = p.line("rt", "inty", source=src, line_width=1, color=color, legend_label=str(sample_name))
        p.scatter("rt", "inty", source=src, size=2, color=color, alpha=0.6)
        renderers.append(r_line)

    if not renderers:
        self.logger.warning("No EIC curves to plot for the selected samples.")
        return

    hover = HoverTool(
        tooltips=[
            ("sample", "@sample"),
            ("sample_color", "$color[swatch]:sample_color"),
            ("rt", "@rt{0.00}"),
            ("inty", "@inty{0.0e0}"),
        ],
        renderers=renderers,
    )
    p.add_tools(hover)

    if getattr(p, "legend", None) and len(p.legend) > 0:
        p.legend.visible = False

    # Apply consistent save/display behavior
    if filename is not None:
        # Convert relative paths to absolute paths using study folder as base
        import os
        if not os.path.isabs(filename):
            filename = os.path.join(self.folder, filename)

        # Convert to absolute path for logging
        abs_filename = os.path.abspath(filename)

        # Use isolated file saving
        _isolated_save_plot(p, filename, abs_filename, self.logger, "EIC Plot")
    else:
        # Show in notebook when no filename provided
        _isolated_show_notebook(p)

    return p


def plot_rt_correction(
    self,
    samples=200,
    title: str | None = None,
    filename: str | None = None,
    width: int = 1000,
    height: int = 300,
):
    """
    Plot RT correction per sample: (rt - rt_original) vs rt overlaid for selected samples.

    This uses the same color mapping as `plot_bpc` so curves for the same samples match.
    """
    from bokeh.plotting import figure, show, output_file
    from bokeh.models import ColumnDataSource, HoverTool
    import numpy as _np

    # Validate features dataframe
    if self.features_df is None or self.features_df.is_empty():
        self.logger.error("No features_df found. Load features first.")
        return

    if "rt_original" not in self.features_df.columns:
        self.logger.error("Column 'rt_original' not found in features_df. Alignment/backup RTs missing.")
        return

    sample_uids = self._get_sample_uids(samples)
    if not sample_uids:
        self.logger.error("No valid sample_uids provided for RT correction plotting.")
        return

    # Get sample colors from samples_df
    sample_colors = (
        self.samples_df.filter(pl.col("sample_uid").is_in(sample_uids))
        .select(["sample_uid", "sample_color"])
        .to_dict(as_series=False)
    )
    color_map = dict(zip(sample_colors["sample_uid"], sample_colors["sample_color"]))

    # For RT correction plots, default to "s" since we're working with features_df directly
    rt_unit = "s"

    p = figure(width=width, height=height, title=title or "RT correction", tools="pan,wheel_zoom,box_zoom,reset,save")
    p.xaxis.axis_label = f"Retention Time ({rt_unit})"
    p.yaxis.axis_label = "RT - RT_original (s)"

    samples_info = None
    if hasattr(self, "samples_df") and self.samples_df is not None:
        try:
            samples_info = self.samples_df.to_pandas()
        except Exception:
            samples_info = None

    renderers = []

    # Iterate samples and build curves
    for uid in sample_uids:
        # Select features belonging to this sample
        try:
            if "sample_uid" in self.features_df.columns:
                sample_feats = self.features_df.filter(pl.col("sample_uid") == uid)
            elif "sample_name" in self.features_df.columns:
                sample_feats = self.features_df.filter(pl.col("sample_name") == uid)
            else:
                self.logger.debug("No sample identifier column in features_df; skipping sample filtering")
                continue
        except Exception as e:
            self.logger.debug(f"Error filtering features for sample {uid}: {e}")
            continue

        if sample_feats.is_empty():
            continue

        # Convert to pandas for easy numeric handling
        try:
            df = sample_feats.to_pandas()
        except Exception:
            continue

        # Need both rt and rt_original
        if "rt" not in df.columns or "rt_original" not in df.columns:
            continue

        # Drop NA and ensure numeric arrays
        df = df.dropna(subset=["rt", "rt_original"]).copy()
        if df.empty:
            continue

        rt = _np.asarray(df["rt"], dtype=float)
        rt_orig = _np.asarray(df["rt_original"], dtype=float)
        delta = rt - rt_orig

        # sort by rt
        idx = _np.argsort(rt)
        rt = rt[idx]
        delta = delta[idx]

        sample_name = str(uid)
        if samples_info is not None:
            try:
                row = samples_info[samples_info["sample_uid"] == uid]
                if not row.empty:
                    sample_name = row.iloc[0].get("sample_name", sample_name)
            except Exception:
                pass

        color = color_map.get(uid, "#000000")

        data = {"rt": rt, "delta": delta, "sample": [sample_name] * len(rt), "sample_color": [color] * len(rt)}
        src = ColumnDataSource(data)

        r_line = p.line("rt", "delta", source=src, line_width=1, color=color)
        p.scatter("rt", "delta", source=src, size=2, color=color, alpha=0.6)
        renderers.append(r_line)

    if not renderers:
        self.logger.warning("No RT correction curves to plot for the selected samples.")
        return

    hover = HoverTool(
        tooltips=[
            ("sample", "@sample"),
            ("sample_color", "$color[swatch]:sample_color"),
            ("rt", "@rt{0.00}"),
            ("rt - rt_original", "@delta{0.00}"),
        ],
        renderers=renderers,
    )
    p.add_tools(hover)

    # Only set legend properties if a legend was actually created to avoid Bokeh warnings
    if getattr(p, "legend", None) and len(p.legend) > 0:
        p.legend.visible = False

    # Apply consistent save/display behavior
    if filename is not None:
        # Convert relative paths to absolute paths using study folder as base
        import os
        if not os.path.isabs(filename):
            filename = os.path.join(self.folder, filename)

        # Convert to absolute path for logging
        abs_filename = os.path.abspath(filename)

        # Use isolated file saving
        _isolated_save_plot(p, filename, abs_filename, self.logger, "RT Correction Plot")
    else:
        # Show in notebook when no filename provided
        _isolated_show_notebook(p)

    return p


def plot_chrom(
    self,
    uids=None,
    samples=100,
    filename=None,
    aligned=True,
    width=800,
    height=300,
):
    cons_uids = self._get_consensus_uids(uids)
    sample_uids = self._get_sample_uids(samples)

    chroms = self.get_chrom(uids=cons_uids, samples=sample_uids)

    if chroms is None or chroms.is_empty():
        self.logger.error("No chromatogram data found.")
        return

    # Get sample colors for alignment plots
    # Need to map sample names to colors since chromatogram data uses sample names as columns
    sample_names = [col for col in chroms.columns if col not in ["consensus_uid"]]
    if not sample_names:
        self.logger.error("No sample names found in chromatogram data.")
        return

    # Create color mapping by getting sample_color for each sample_name
    samples_info = self.samples_df.select(["sample_name", "sample_color", "sample_uid"]).to_dict(as_series=False)
    sample_name_to_color = dict(zip(samples_info["sample_name"], samples_info["sample_color"]))
    sample_name_to_uid = dict(zip(samples_info["sample_name"], samples_info["sample_uid"]))
    color_map = {name: sample_name_to_color.get(name, "#1f77b4") for name in sample_names}  # fallback to blue

    plots = []
    self.logger.info(f"Plotting {chroms.shape[0]} chromatograms...")
    tqdm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]
    for row in tqdm(
        chroms.iter_rows(named=True),
        total=chroms.shape[0],
        desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Plot chromatograms",
        disable=tqdm_disable,
    ):
        consensus_uid = row["consensus_uid"]  # Get consensus_uid from the row
        consensus_id = consensus_uid  # Use the same value for consensus_id
        curves = []
        rt_min = np.inf
        rt_max = 0
        for sample in sample_names:
            chrom = row[sample]
            if chrom is not None:
                # check if chrom is nan
                if isinstance(chrom, float) and np.isnan(chrom):
                    continue

                chrom = chrom.to_dict()
                rt = chrom["rt"].copy()
                if len(rt) == 0:
                    continue
                if aligned and "rt_shift" in chrom:
                    rt_shift = chrom["rt_shift"]
                    if rt_shift is not None:
                        # Convert to numpy array if it's a list, then add scalar
                        if isinstance(rt, list):
                            rt = np.array(rt)
                        rt = rt + rt_shift  # Add scalar to array

                # update rt_min and rt_max
                if rt[0] < rt_min:
                    rt_min = rt[0]
                if rt[-1] > rt_max:
                    rt_max = rt[-1]

                inty = chrom["inty"]

                # Convert both rt and inty to numpy arrays if they're lists
                if isinstance(rt, list):
                    rt = np.array(rt)
                if isinstance(inty, list):
                    inty = np.array(inty)

                # Ensure both rt and inty are arrays and have the same length and are not empty
                if rt.size > 0 and inty.size > 0 and rt.shape == inty.shape:
                    # sort rt and inty by rt
                    sorted_indices = np.argsort(rt)
                    rt = rt[sorted_indices]
                    inty = inty[sorted_indices]

                    # Get sample uid for this sample name
                    sample_uid = sample_name_to_uid.get(sample, None)
                    sample_color = color_map.get(sample, "#1f77b4")

                    # Create arrays with sample information for hover tooltips
                    sample_names_array = [sample] * len(rt)
                    sample_uids_array = [sample_uid] * len(rt)
                    sample_colors_array = [sample_color] * len(rt)

                    curve = hv.Curve(
                        (rt, inty, sample_names_array, sample_uids_array, sample_colors_array),
                        kdims=["RT"],
                        vdims=["inty", "sample_name", "sample_uid", "sample_color"]
                    ).opts(
                        color=color_map[sample],
                        line_width=1,
                        tools=["hover"],
                        hover_tooltips=[
                            ("RT", "@RT{0.00}"),
                            ("Intensity", "@inty{0,0}"),
                            ("Sample Name", "@sample_name"),
                            ("Sample UID", "@sample_uid"),
                            ("Sample Color", "$color[swatch]:sample_color")
                        ]
                    )
                    curves.append(curve)

                    if "feature_start" in chrom and "feature_end" in chrom:
                        # Add vertical lines for feature start and end
                        feature_start = chrom["feature_start"]
                        feature_end = chrom["feature_end"]
                        if aligned and "rt_shift" in chrom:
                            rt_shift = chrom["rt_shift"]
                            if rt_shift is not None:
                                feature_start += rt_shift
                                feature_end += rt_shift
                        if feature_start < rt_min:
                            rt_min = feature_start
                        if feature_end > rt_max:
                            rt_max = feature_end
                        # Add vertical lines to the curves
                        curves.append(
                            hv.VLine(feature_start).opts(
                                color=color_map[sample],
                                line_dash="dotted",
                                line_width=1,
                            ),
                        )
                        curves.append(
                            hv.VLine(feature_end).opts(
                                color=color_map[sample],
                                line_dash="dotted",
                                line_width=1,
                            ),
                        )
        if curves:
            # find row in consensus_df with consensus_id
            consensus_row = self.consensus_df.filter(
                pl.col("consensus_uid") == consensus_id,
            )
            rt_start_mean = consensus_row["rt_start_mean"][0]
            rt_end_mean = consensus_row["rt_end_mean"][0]
            # Add vertical lines to overlay
            curves.append(hv.VLine(rt_start_mean).opts(color="black", line_width=2))
            curves.append(hv.VLine(rt_end_mean).opts(color="black", line_width=2))

            overlay = hv.Overlay(curves).opts(
                height=height,
                width=width,
                title=f"Consensus UID: {consensus_id}, mz: {consensus_row['mz'][0]:.4f}, rt: {consensus_row['rt'][0]:.2f}{' (aligned)' if aligned else ''}",
                xlim=(rt_min, rt_max),
                shared_axes=False,
            )
            plots.append(overlay)

    if not plots:
        self.logger.warning("No valid chromatogram curves to plot.")
        return

    # stack vertically.
    # Stack all plots vertically in a Panel column
    layout = panel.Column(*[panel.panel(plot) for plot in plots])

    # Apply consistent save/display behavior
    if filename is not None:
        # Convert relative paths to absolute paths using study folder as base
        import os
        if not os.path.isabs(filename):
            filename = os.path.join(self.folder, filename)

        # Convert to absolute path for logging
        abs_filename = os.path.abspath(filename)

        # Use isolated Panel saving
        _isolated_save_panel_plot(panel.panel(layout), filename, abs_filename, self.logger, "Chromatogram Plot")
    else:
        # Show in notebook when no filename provided
        # Convert Panel layout to Bokeh layout for consistent isolated display
        try:
            panel_obj = panel.panel(layout)
            bokeh_layout = panel_obj.get_root()
            # Use the regular isolated show method for Bokeh objects
            _isolated_show_notebook(bokeh_layout)
        except Exception:
            # Fallback to Panel display if conversion fails
            _isolated_show_panel_notebook(panel.panel(layout))


def plot_consensus_stats(
    self,
    filename=None,
    width=1200,
    height=1200,
    alpha=0.6,
    markersize=3,
):
    """
    Plot a scatter plot matrix (SPLOM) of consensus statistics using Bokeh.

    Parameters:
        filename (str, optional): Output filename for saving the plot
        width (int): Overall width of the plot (default: 1200)
        height (int): Overall height of the plot (default: 1200)
        alpha (float): Point transparency (default: 0.6)
        markersize (int): Size of points (default: 5)
    """
    from bokeh.layouts import gridplot
    from bokeh.models import ColumnDataSource, HoverTool
    from bokeh.plotting import figure, show, output_file

    # Check if consensus_df exists and has data
    if self.consensus_df is None or self.consensus_df.is_empty():
        self.logger.error("No consensus data available. Run merge/find_consensus first.")
        return

    # Define the columns to plot
    columns = [
        "rt",
        "mz",
        "number_samples",
        "log10_quality",
        "mz_delta_mean",
        "rt_delta_mean",
        "chrom_coherence_mean",
        "chrom_prominence_scaled_mean",
        "inty_mean",
        "number_ms2",
    ]

    # Check which columns exist in the dataframe and compute missing ones
    available_columns = self.consensus_df.columns
    data_df = self.consensus_df.clone()

    # Add log10_quality if quality exists
    if "quality" in available_columns and "log10_quality" not in available_columns:
        data_df = data_df.with_columns(
            pl.col("quality").log10().alias("log10_quality"),
        )

    # Filter columns that actually exist
    final_columns = [col for col in columns if col in data_df.columns]

    if len(final_columns) < 2:
        self.logger.error(f"Need at least 2 columns for SPLOM. Available: {final_columns}")
        return

    self.logger.debug(f"Creating SPLOM with columns: {final_columns}")

    # Add important ID columns for tooltips even if not plotting them
    tooltip_columns = []
    for id_col in ["consensus_uid", "consensus_id"]:
        if id_col in data_df.columns and id_col not in final_columns:
            tooltip_columns.append(id_col)

    # Select plotting columns plus tooltip columns
    all_columns = final_columns + tooltip_columns
    data_pd = data_df.select(all_columns).to_pandas()

    # Remove any infinite or NaN values
    data_pd = data_pd.replace([np.inf, -np.inf], np.nan).dropna()

    if data_pd.empty:
        self.logger.error("No valid data after removing NaN/infinite values.")
        return

    source = ColumnDataSource(data_pd)

    n_vars = len(final_columns)

    # Fixed dimensions - override user input to ensure consistent layout
    total_width = 1200
    total_height = 1200

    # Calculate plot sizes to ensure uniform inner plot areas
    # First column needs extra width for y-axis labels
    plot_width_first = 180  # Wider to account for y-axis labels
    plot_width_others = 120  # Standard width for other columns
    plot_height_normal = 120  # Standard height
    plot_height_last = 155  # Taller last row to accommodate x-axis labels while keeping inner plot area same size

    # Create grid of plots with variable outer sizes but equal inner areas
    plots = []

    for i, y_var in enumerate(final_columns):
        row = []
        for j, x_var in enumerate(final_columns):
            # Determine if this plot needs axis labels
            has_x_label = i == n_vars - 1  # bottom row
            has_y_label = j == 0  # left column

            # First column wider to accommodate y-axis labels, ensuring equal inner plot areas
            current_width = plot_width_first if has_y_label else plot_width_others
            current_height = plot_height_last if has_x_label else plot_height_normal

            p = figure(
                width=current_width,
                height=current_height,
                title=None,  # No title on any plot
                toolbar_location=None,
                # Adjusted borders - first column has more space, others minimal
                min_border_left=70 if has_y_label else 15,
                min_border_bottom=50 if has_x_label else 15,
                min_border_right=15,
                min_border_top=15,
            )

            # Ensure subplot background and border are explicitly white so the plot looks
            # correct in dark and light themes.
            p.outline_line_color = None
            p.border_fill_color = "white"
            p.border_fill_alpha = 1.0
            p.background_fill_color = "white"

            # Remove axis lines to eliminate black lines between plots
            p.xaxis.axis_line_color = None
            p.yaxis.axis_line_color = None

            # Keep subtle grid lines for data reference
            p.grid.visible = True
            p.grid.grid_line_color = "#E0E0E0"  # Light gray grid lines

            # Set axis labels and formatting
            if has_x_label:  # bottom row
                p.xaxis.axis_label = x_var
                p.xaxis.axis_label_text_font_size = "12pt"
                p.xaxis.major_label_text_font_size = "9pt"
                p.xaxis.axis_label_standoff = 15
            else:
                p.xaxis.major_label_text_font_size = "0pt"
                p.xaxis.minor_tick_line_color = None
                p.xaxis.major_tick_line_color = None

            if has_y_label:  # left column
                p.yaxis.axis_label = y_var
                p.yaxis.axis_label_text_font_size = "10pt"  # Smaller y-axis title
                p.yaxis.major_label_text_font_size = "8pt"
                p.yaxis.axis_label_standoff = 12
            else:
                p.yaxis.major_label_text_font_size = "0pt"
                p.yaxis.minor_tick_line_color = None
                p.yaxis.major_tick_line_color = None

            if i == j:
                # Diagonal: histogram
                hist, edges = np.histogram(data_pd[x_var], bins=30)
                p.quad(
                    top=hist,
                    bottom=0,
                    left=edges[:-1],
                    right=edges[1:],
                    fill_color="green",
                    line_color="white",
                    alpha=alpha,
                )
            else:
                # Off-diagonal: scatter plot
                scatter = p.scatter(
                    x=x_var,
                    y=y_var,
                    size=markersize,
                    alpha=alpha,
                    color="blue",
                    source=source,
                )

                # Add hover tool
                hover = HoverTool(
                    tooltips=[
                        (x_var, f"@{x_var}{{0.0000}}"),
                        (y_var, f"@{y_var}{{0.0000}}"),
                        (
                            "consensus_uid",
                            "@consensus_uid"
                            if "consensus_uid" in data_pd.columns
                            else "@consensus_id"
                            if "consensus_id" in data_pd.columns
                            else "N/A",
                        ),
                        ("rt", "@rt{0.00}" if "rt" in data_pd.columns else "N/A"),
                        ("mz", "@mz{0.0000}" if "mz" in data_pd.columns else "N/A"),
                    ],
                    renderers=[scatter],
                )
                p.add_tools(hover)

            row.append(p)
        plots.append(row)

    # Link axes for same variables
    for i in range(n_vars):
        for j in range(n_vars):
            if i != j:  # Don't link diagonal plots
                # Link x-axis to other plots in same column
                for k in range(n_vars):
                    if k != i and k != j:
                        plots[i][j].x_range = plots[k][j].x_range

                # Link y-axis to other plots in same row
                for k in range(n_vars):
                    if k != j and k != i:
                        plots[i][j].y_range = plots[i][k].y_range

    # Create grid layout and force overall background/border to white so the outer
    # container doesn't show dark UI colors in night mode.
    grid = gridplot(plots)

    # Set overall background and border to white when supported
    if hasattr(grid, "background_fill_color"):
        grid.background_fill_color = "white"
    if hasattr(grid, "border_fill_color"):
        grid.border_fill_color = "white"

    # Apply consistent save/display behavior
    if filename is not None:
        # Convert relative paths to absolute paths using study folder as base
        import os
        if not os.path.isabs(filename):
            filename = os.path.join(self.folder, filename)

        # Convert to absolute path for logging
        abs_filename = os.path.abspath(filename)

        # Use isolated file saving
        _isolated_save_plot(grid, filename, abs_filename, self.logger, "Consensus Stats Plot")
    else:
        # Show in notebook when no filename provided
        _isolated_show_notebook(grid)
    return grid


def plot_pca(
    self,
    filename=None,
    width=500,
    height=450,
    alpha=0.8,
    markersize=6,
    n_components=2,
    colorby=None,
    title="PCA of Consensus Matrix",
):
    """
    Plot PCA (Principal Component Analysis) of the consensus matrix using Bokeh.

    Parameters:
        filename (str, optional): Output filename for saving the plot
        width (int): Plot width (default: 800)
        height (int): Plot height (default: 600)
        alpha (float): Point transparency (default: 0.8)
        markersize (int): Size of points (default: 8)
        n_components (int): Number of PCA components to compute (default: 2)
        color_by (str, optional): Column from samples_df to color points by
        title (str): Plot title (default: "PCA of Consensus Matrix")
    """
    from bokeh.models import ColumnDataSource, HoverTool, ColorBar, LinearColorMapper
    from bokeh.plotting import figure, show, output_file
    from bokeh.palettes import Category20, viridis
    from bokeh.transform import factor_cmap
    from bokeh.io.export import export_png
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
    import pandas as pd
    import numpy as np

    # Check if consensus matrix and samples_df exist
    try:
        consensus_matrix = self.get_consensus_matrix()
        samples_df = self.samples_df
    except Exception as e:
        self.logger.error(f"Error getting consensus matrix or samples_df: {e}")
        return

    if consensus_matrix is None or consensus_matrix.shape[0] == 0:
        self.logger.error("No consensus matrix available. Run merge/find_consensus first.")
        return

    if samples_df is None or samples_df.is_empty():
        self.logger.error("No samples dataframe available.")
        return

    self.logger.debug(f"Performing PCA on consensus matrix with shape: {consensus_matrix.shape}")

    # Extract only the sample columns (exclude consensus_uid column)
    sample_cols = [col for col in consensus_matrix.columns if col != "consensus_uid"]

    # Convert consensus matrix to numpy, excluding the consensus_uid column
    if hasattr(consensus_matrix, "select"):
        # Polars DataFrame
        matrix_data = consensus_matrix.select(sample_cols).to_numpy()
    else:
        # Pandas DataFrame or other - drop consensus_uid column
        matrix_sample_data = consensus_matrix.drop(columns=["consensus_uid"], errors="ignore")
        if hasattr(matrix_sample_data, "values"):
            matrix_data = matrix_sample_data.values
        elif hasattr(matrix_sample_data, "to_numpy"):
            matrix_data = matrix_sample_data.to_numpy()
        else:
            matrix_data = np.array(matrix_sample_data)

    # Transpose matrix so samples are rows and features are columns
    matrix_data = matrix_data.T

    # Handle missing values by replacing with 0
    matrix_data = np.nan_to_num(matrix_data, nan=0.0, posinf=0.0, neginf=0.0)

    # Standardize the data
    scaler = StandardScaler()
    matrix_scaled = scaler.fit_transform(matrix_data)

    # Perform PCA
    pca = PCA(n_components=n_components)
    pca_result = pca.fit_transform(matrix_scaled)

    # Get explained variance ratios
    explained_var = pca.explained_variance_ratio_

    self.logger.debug(f"PCA explained variance ratios: {explained_var}")

    # Convert samples_df to pandas for easier manipulation
    samples_pd = samples_df.to_pandas()

    # Create dataframe with PCA results and sample information
    pca_df = pd.DataFrame({
        "PC1": pca_result[:, 0],
        "PC2": pca_result[:, 1] if n_components > 1 else np.zeros(len(pca_result)),
    })

    # Add sample information to PCA dataframe
    if len(samples_pd) == len(pca_df):
        for col in samples_pd.columns:
            pca_df[col] = samples_pd[col].values
    else:
        self.logger.warning(
            f"Sample count mismatch: samples_df has {len(samples_pd)} rows, "
            f"but consensus matrix has {len(pca_df)} samples",
        )

    # Prepare color mapping
    color_column = None
    color_mapper = None

    if colorby and colorby in pca_df.columns:
        color_column = colorby
        unique_values = pca_df[colorby].unique()

        # Handle categorical vs numeric coloring
        if pca_df[colorby].dtype in ["object", "string", "category"]:
            # Categorical coloring
            if len(unique_values) <= 20:
                palette = Category20[min(20, max(3, len(unique_values)))]
            else:
                palette = viridis(min(256, len(unique_values)))
            color_mapper = factor_cmap(colorby, palette, unique_values)
        else:
            # Numeric coloring
            palette = viridis(256)
            color_mapper = LinearColorMapper(
                palette=palette,
                low=pca_df[colorby].min(),
                high=pca_df[colorby].max(),
            )

    # Create Bokeh plot
    p = figure(
        width=width,
        height=height,
        title=f"{title} (PC1: {explained_var[0]:.1%}, PC2: {explained_var[1]:.1%})",
        tools="pan,wheel_zoom,box_zoom,reset,save",
    )

    p.xaxis.axis_label = f"PC1 ({explained_var[0]:.1%} variance)"
    p.yaxis.axis_label = f"PC2 ({explained_var[1]:.1%} variance)"

    # Create data source
    source = ColumnDataSource(pca_df)

    # Create scatter plot
    if color_mapper:
        if isinstance(color_mapper, LinearColorMapper):
            scatter = p.scatter(
                "PC1",
                "PC2",
                size=markersize,
                alpha=alpha,
                color={"field": colorby, "transform": color_mapper},
                source=source,
            )
            # Add colorbar for numeric coloring
            color_bar = ColorBar(color_mapper=color_mapper, width=8, location=(0, 0))
            p.add_layout(color_bar, "right")
        else:
            scatter = p.scatter(
                "PC1",
                "PC2",
                size=markersize,
                alpha=alpha,
                color=color_mapper,
                source=source,
                legend_field=colorby,
            )
    else:
        # If no color_by provided, use sample_color column from samples_df
        if "sample_uid" in pca_df.columns or "sample_name" in pca_df.columns:
            # Choose the identifier to map colors by
            id_col = "sample_uid" if "sample_uid" in pca_df.columns else "sample_name"

            # Get colors from samples_df based on the identifier
            if id_col == "sample_uid":
                sample_colors = (
                    self.samples_df.filter(pl.col("sample_uid").is_in(pca_df[id_col].unique()))
                    .select(["sample_uid", "sample_color"])
                    .to_dict(as_series=False)
                )
                color_map = dict(zip(sample_colors["sample_uid"], sample_colors["sample_color"]))
            else:  # sample_name
                sample_colors = (
                    self.samples_df.filter(pl.col("sample_name").is_in(pca_df[id_col].unique()))
                    .select(["sample_name", "sample_color"])
                    .to_dict(as_series=False)
                )
                color_map = dict(zip(sample_colors["sample_name"], sample_colors["sample_color"]))

            # Map colors into dataframe
            pca_df["color"] = [color_map.get(x, "#1f77b4") for x in pca_df[id_col]]  # fallback to blue
            # Update the ColumnDataSource with new color column
            source = ColumnDataSource(pca_df)
            scatter = p.scatter(
                "PC1",
                "PC2",
                size=markersize,
                alpha=alpha,
                color="color",
                source=source,
            )
        else:
            scatter = p.scatter(
                "PC1",
                "PC2",
                size=markersize,
                alpha=alpha,
                color="blue",
                source=source,
            )

    # Create comprehensive hover tooltips with all sample information
    tooltip_list = []

    # Columns to exclude from tooltips (file paths and internal/plot fields)
    excluded_cols = {"file_source", "file_path", "sample_path", "map_id", "PC1", "PC2", "ms1", "ms2", "size"}

    # Add all sample dataframe columns to tooltips, skipping excluded ones
    for col in samples_pd.columns:
        if col in excluded_cols:
            continue
        if col in pca_df.columns:
            if col == "sample_color":
                # Display sample_color as a colored swatch
                tooltip_list.append(("color", "$color[swatch]:sample_color"))
            elif pca_df[col].dtype in ["float64", "float32"]:
                tooltip_list.append((col, f"@{col}{{0.00}}"))
            else:
                tooltip_list.append((col, f"@{col}"))

    hover = HoverTool(
        tooltips=tooltip_list,
        renderers=[scatter],
    )
    p.add_tools(hover)

    # Add legend if using categorical coloring
    if color_mapper and not isinstance(color_mapper, LinearColorMapper) and colorby:
        # Only set legend properties if legends exist (avoid Bokeh warning when none created)
        if getattr(p, "legend", None) and len(p.legend) > 0:
            p.legend.location = "top_left"
            p.legend.click_policy = "hide"

    # Apply consistent save/display behavior
    if filename is not None:
        # Convert relative paths to absolute paths using study folder as base
        import os
        if not os.path.isabs(filename):
            filename = os.path.join(self.folder, filename)

        # Convert to absolute path for logging
        abs_filename = os.path.abspath(filename)

        # Use isolated file saving
        _isolated_save_plot(p, filename, abs_filename, self.logger, "PCA Plot")
    else:
        # Show in notebook when no filename provided
        _isolated_show_notebook(p)
    return p


def plot_tic(
    self,
    samples=100,
    title: str | None = None,
    filename: str | None = None,
    width: int = 1000,
    height: int = 300,
    original: bool = False,
):
    """
    Plot Total Ion Chromatograms (TIC) for selected samples overlaid using Bokeh.

    Parameters and behavior mirror `plot_bpc` but use per-sample TICs (get_tic).
    """
    # Local imports to avoid heavy top-level deps / circular imports
    from bokeh.plotting import figure, show, output_file
    from bokeh.models import ColumnDataSource, HoverTool
    from bokeh.io.export import export_png
    from masster.study.helpers import get_tic

    sample_uids = self._get_sample_uids(samples)
    if not sample_uids:
        self.logger.error("No valid sample_uids provided for TIC plotting.")
        return

    # Get sample colors from samples_df
    sample_colors = (
        self.samples_df.filter(pl.col("sample_uid").is_in(sample_uids))
        .select(["sample_uid", "sample_color"])
        .to_dict(as_series=False)
    )
    color_map = dict(zip(sample_colors["sample_uid"], sample_colors["sample_color"]))

    plot_title = title or "Total Ion Chromatograms"

    # Get rt_unit from the first chromatogram, default to "s" if not available
    rt_unit = "s"
    for uid in sample_uids:
        try:
            first_chrom = get_tic(self, sample=uid, label=None)
            if hasattr(first_chrom, "rt_unit"):
                rt_unit = first_chrom.rt_unit
                break
        except Exception:
            continue

    p = figure(width=width, height=height, title=plot_title, tools="pan,wheel_zoom,box_zoom,reset,save")
    p.xaxis.axis_label = f"Retention Time ({rt_unit})"
    p.yaxis.axis_label = "Intensity"

    renderers = []

    # Build sample name mapping once
    samples_info = None
    if hasattr(self, "samples_df") and self.samples_df is not None:
        try:
            samples_info = self.samples_df.to_pandas()
        except Exception:
            samples_info = None

    for uid in sample_uids:
        try:
            chrom = get_tic(self, sample=uid, label=None)
        except Exception as e:
            self.logger.debug(f"Skipping sample {uid} for TIC: {e}")
            continue

        # extract arrays
        try:
            chrom_dict = (
                chrom.to_dict()
                if hasattr(chrom, "to_dict")
                else {"rt": getattr(chrom, "rt"), "inty": getattr(chrom, "inty")}
            )
            rt = chrom_dict.get("rt")
            inty = chrom_dict.get("inty")
        except Exception:
            try:
                rt = chrom.rt
                inty = chrom.inty
            except Exception as e:
                self.logger.debug(f"Invalid chromatogram for sample {uid}: {e}")
                continue

        if rt is None or inty is None:
            continue

        import numpy as _np

        rt = _np.asarray(rt)
        inty = _np.asarray(inty)
        if rt.size == 0 or inty.size == 0:
            continue

        # Sort by rt
        idx = _np.argsort(rt)
        rt = rt[idx]
        inty = inty[idx]

        sample_name = str(uid)
        if samples_info is not None:
            try:
                row = samples_info[samples_info["sample_uid"] == uid]
                if not row.empty:
                    sample_name = row.iloc[0].get("sample_name", sample_name)
            except Exception:
                pass

        color = color_map.get(uid, "#000000")

        data = {"rt": rt, "inty": inty, "sample": [sample_name] * len(rt), "sample_color": [color] * len(rt)}
        src = ColumnDataSource(data)

        r_line = p.line("rt", "inty", source=src, line_width=1, color=color, legend_label=str(sample_name))
        p.scatter("rt", "inty", source=src, size=2, color=color, alpha=0.6)
        renderers.append(r_line)

    if not renderers:
        self.logger.warning("No TIC curves to plot for the selected samples.")
        return

    hover = HoverTool(
        tooltips=[
            ("sample", "@sample"),
            ("sample_color", "$color[swatch]:sample_color"),
            ("rt", "@rt{0.00}"),
            ("inty", "@inty{0.00e0}"),
        ],
        renderers=renderers,
    )
    p.add_tools(hover)

    # Only set legend properties if a legend was actually created to avoid Bokeh warnings
    if getattr(p, "legend", None) and len(p.legend) > 0:
        p.legend.visible = False

    # Apply consistent save/display behavior
    if filename is not None:
        # Convert relative paths to absolute paths using study folder as base
        import os
        if not os.path.isabs(filename):
            filename = os.path.join(self.folder, filename)

        # Convert to absolute path for logging
        abs_filename = os.path.abspath(filename)

        # Use isolated file saving
        _isolated_save_plot(p, filename, abs_filename, self.logger, "TIC Plot")
    else:
        # Show in notebook when no filename provided
        _isolated_show_notebook(p)

    return p
