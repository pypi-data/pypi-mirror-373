"""
_study_h5.py

This module provides HDF5-based save/load functionality for the Study class.
It handles serialization and deserialization of Polars DataFrames with complex objects
It handles serialization and deserialization of Polars DataFrames with complex objects
It handles serialization and deserialization of Polars DataFrames with complex objects
like Chromatogram and Spectrum instances.

Key Features:
- **HDF5 Storage**: Efficient compressed storage using HDF5 format
- **Complex Object Serialization**: JSON-based serialization for Chromatogram and Spectrum objects
- **Schema-based loading**: Uses study5_schema.json for proper type handling
- **Error Handling**: Robust error handling and logging

Dependencies:
- `h5py`: For HDF5 file operations
- `polars`: For DataFrame handling
- `json`: For complex object serialization
- `numpy`: For numerical array operations

Functions:
- `_save_study5()`: Save study to .study5 HDF5 file (new format)
- `_load_study5()`: Load study from .study5 HDF5 file (new format)
- `_save_h5()`: Save study to .h5 file (legacy format)
- `_load_h5()`: Load study from .h5 file (legacy format)
"""

import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import h5py
import polars as pl
from tqdm import tqdm

from masster.chromatogram import Chromatogram
from masster.spectrum import Spectrum


# Helper functions for HDF5 operations
def _load_schema(schema_path: str) -> dict:
    """Load schema from JSON file with error handling."""
    try:
        with open(schema_path) as f:
            return json.load(f)  # type: ignore
    except FileNotFoundError:
        return {}


def _decode_bytes_attr(attr_value):
    """Decode metadata attribute, handling both bytes and string types."""
    if isinstance(attr_value, bytes):
        return attr_value.decode("utf-8")
    return str(attr_value) if attr_value is not None else ""


def _create_empty_dataframe_from_schema(df_name: str, schema: dict) -> pl.DataFrame:
    """Create an empty DataFrame with the correct schema based on study5_schema.json."""
    if df_name not in schema:
        # Fallback to basic empty DataFrame if schema not found
        return pl.DataFrame()
    
    df_schema = schema[df_name]["columns"]
    empty_data = {}
    polars_schema = {}
    
    for col_name, col_info in df_schema.items():
        dtype_str = col_info["dtype"]
        # Convert string representation to actual Polars dtype
        if dtype_str == "pl.Int64":
            polars_dtype = pl.Int64
        elif dtype_str == "pl.Int32":
            polars_dtype = pl.Int32  
        elif dtype_str == "pl.Float64":
            polars_dtype = pl.Float64
        elif dtype_str == "pl.Utf8":
            polars_dtype = pl.Utf8
        elif dtype_str == "pl.String":
            polars_dtype = pl.String
        elif dtype_str == "pl.Boolean":
            polars_dtype = pl.Boolean
        elif dtype_str == "pl.Object":
            polars_dtype = pl.Object
        elif dtype_str == "pl.Null":
            polars_dtype = pl.Null
        else:
            # Fallback to string if unknown type
            polars_dtype = pl.String
            
        empty_data[col_name] = []
        polars_schema[col_name] = polars_dtype
    
    return pl.DataFrame(empty_data, schema=polars_schema)


def _save_dataframe_optimized(df, group, schema, df_name, logger, chunk_size=10000):
    """
    Save an entire DataFrame to HDF5 with optimized batch processing and memory efficiency.

    This function replaces individual column processing with batch operations for much
    better performance on large datasets (300+ samples).

    Args:
        df: Polars DataFrame to save
        group: HDF5 group to save to
        schema: Schema for column ordering
        df_name: Name of the DataFrame for schema lookup
        logger: Logger instance
        chunk_size: Number of rows to process at once for memory efficiency
    """
    if df is None or df.is_empty():
        return

    try:
        # Reorder columns according to schema
        df_ordered = _reorder_columns_by_schema(df.clone(), schema, df_name)
        total_rows = len(df_ordered)

        # Group columns by processing type for batch optimization
        numeric_cols = []
        string_cols = []
        object_cols = []

        for col in df_ordered.columns:
            dtype = str(df_ordered[col].dtype).lower()
            if dtype == "object":
                object_cols.append(col)
            elif dtype in ["string", "utf8"]:
                string_cols.append(col)
            else:
                numeric_cols.append(col)

        logger.debug(
            f"Saving {df_name}: {total_rows} rows, {len(numeric_cols)} numeric, {len(string_cols)} string, {len(object_cols)} object columns",
        )

        # Process numeric columns in batch (most efficient)
        if numeric_cols:
            for col in numeric_cols:
                _save_numeric_column_fast(group, col, df_ordered[col], logger)

        # Process string columns in batch
        if string_cols:
            for col in string_cols:
                _save_string_column_fast(group, col, df_ordered[col], logger)

        # Process object columns with optimized serialization
        if object_cols:
            _save_object_columns_optimized(
                group,
                df_ordered,
                object_cols,
                logger,
                chunk_size,
            )

    except Exception as e:
        logger.error(f"Failed to save DataFrame {df_name}: {e}")
        # Fallback to old method for safety
        _save_dataframe_column_legacy(df, group, schema, df_name, logger)


def _save_numeric_column_fast(group, col, data_series, logger):
    """Fast numeric column saving with optimal compression."""
    try:
        import numpy as np

        # Get compression settings based on column name
        if col in ["consensus_uid", "feature_uid", "scan_id", "rt", "mz", "intensity"]:
            compression_kwargs = {"compression": "lzf", "shuffle": True}
        else:
            compression_kwargs = {"compression": "lzf"}

        # Convert to numpy array efficiently
        try:
            data_array = data_series.to_numpy()
        except Exception:
            # Fallback for complex data types
            data_array = np.array(data_series.to_list())

        # Handle None/null values efficiently
        if data_array.dtype == object:
            # Check if this is actually a list/array column that should be treated as object
            sample_value = None
            for val in data_array:
                if val is not None:
                    sample_value = val
                    break

            # If sample value is a list/array, treat as object column
            if isinstance(sample_value, (list, tuple, np.ndarray)):
                logger.debug(
                    f"Column '{col}' contains array-like data, treating as object",
                )
                _save_dataframe_column_legacy_single(
                    group,
                    col,
                    data_series.to_list(),
                    "object",
                    logger,
                )
                return

            # Otherwise, convert None values to -123 sentinel for mixed-type numeric columns
            try:
                data_array = np.array(
                    [(-123 if x is None else float(x)) for x in data_array],
                )
            except (ValueError, TypeError):
                # If conversion fails, this is not a numeric column
                logger.debug(f"Column '{col}' is not numeric, treating as object")
                _save_dataframe_column_legacy_single(
                    group,
                    col,
                    data_series.to_list(),
                    "object",
                    logger,
                )
                return

        group.create_dataset(col, data=data_array, **compression_kwargs)

    except Exception as e:
        logger.warning(f"Failed to save numeric column '{col}' efficiently: {e}")
        # Fallback to old method
        _save_dataframe_column_legacy_single(
            group,
            col,
            data_series.to_list(),
            str(data_series.dtype),
            logger,
        )


def _save_string_column_fast(group, col, data_series, logger):
    """Fast string column saving with optimal compression."""
    try:
        # Convert to string array efficiently
        string_data = ["None" if x is None else str(x) for x in data_series.to_list()]

        compression_kwargs = {"compression": "gzip", "compression_opts": 6}
        group.create_dataset(col, data=string_data, **compression_kwargs)

    except Exception as e:
        logger.warning(f"Failed to save string column '{col}' efficiently: {e}")
        # Fallback to old method
        _save_dataframe_column_legacy_single(
            group,
            col,
            data_series.to_list(),
            "string",
            logger,
        )


def _save_object_columns_optimized(group, df, object_cols, logger, chunk_size):
    """Optimized object column processing with chunking and parallel serialization."""
    import json

    def serialize_chunk(col_name, chunk_data):
        """Serialize a chunk of object data."""
        serialized_chunk = []

        if col_name == "chrom":
            # Handle Chromatogram objects
            for item in chunk_data:
                if item is not None:
                    serialized_chunk.append(item.to_json())
                else:
                    serialized_chunk.append("None")
        elif col_name == "ms2_scans":
            # Handle MS2 scan lists
            for item in chunk_data:
                if item is not None:
                    serialized_chunk.append(json.dumps(list(item)))
                else:
                    serialized_chunk.append("None")
        elif col_name == "ms2_specs":
            # Handle MS2 spectrum lists
            for item in chunk_data:
                if item is not None:
                    json_strings = []
                    for spectrum in item:
                        if spectrum is not None:
                            json_strings.append(spectrum.to_json())
                        else:
                            json_strings.append("None")
                    serialized_chunk.append(json.dumps(json_strings))
                else:
                    serialized_chunk.append(json.dumps(["None"]))
        elif col_name in ["adducts", "adduct_values"]:
            # Handle lists
            for item in chunk_data:
                if item is not None:
                    serialized_chunk.append(json.dumps(item))
                else:
                    serialized_chunk.append("[]")
        elif col_name == "spec":
            # Handle single Spectrum objects
            for item in chunk_data:
                if item is not None:
                    serialized_chunk.append(item.to_json())
                else:
                    serialized_chunk.append("None")
        else:
            logger.warning(
                f"Unknown object column '{col_name}', using default serialization",
            )
            for item in chunk_data:
                serialized_chunk.append(str(item) if item is not None else "None")

        return serialized_chunk

    # Process each object column
    for col in object_cols:
        try:
            data_list = df[col].to_list()
            total_items = len(data_list)

            if total_items == 0:
                group.create_dataset(
                    col,
                    data=[],
                    compression="gzip",
                    compression_opts=6,
                )
                continue

            # For small datasets, process directly
            if total_items <= chunk_size:
                serialized_data = serialize_chunk(col, data_list)
                group.create_dataset(
                    col,
                    data=serialized_data,
                    compression="gzip",
                    compression_opts=6,
                )
            else:
                # For large datasets, use chunked processing with parallel serialization
                logger.debug(
                    f"Processing large object column '{col}' with {total_items} items in chunks",
                )

                all_serialized = []
                num_chunks = (total_items + chunk_size - 1) // chunk_size

                # Use thread pool for parallel serialization of chunks
                with ThreadPoolExecutor(max_workers=min(4, num_chunks)) as executor:
                    futures = {}

                    for i in range(0, total_items, chunk_size):
                        chunk = data_list[i : i + chunk_size]
                        future = executor.submit(serialize_chunk, col, chunk)
                        futures[future] = i

                    # Collect results in order
                    results = {}
                    for future in as_completed(futures):
                        chunk_start = futures[future]
                        try:
                            chunk_result = future.result()
                            results[chunk_start] = chunk_result
                        except Exception as e:
                            logger.warning(
                                f"Failed to serialize chunk starting at {chunk_start} for column '{col}': {e}",
                            )
                            # Fallback to simple string conversion for this chunk
                            chunk = data_list[chunk_start : chunk_start + chunk_size]
                            results[chunk_start] = [
                                str(item) if item is not None else "None"
                                for item in chunk
                            ]

                    # Reassemble in correct order
                    for i in range(0, total_items, chunk_size):
                        if i in results:
                            all_serialized.extend(results[i])

                group.create_dataset(
                    col,
                    data=all_serialized,
                    compression="gzip",
                    compression_opts=6,
                )

        except Exception as e:
            logger.warning(
                f"Failed to save object column '{col}' with optimization: {e}",
            )
            # Fallback to old method
            _save_dataframe_column_legacy_single(
                group,
                col,
                df[col].to_list(),
                "object",
                logger,
            )


def _save_dataframe_column_legacy_single(
    group,
    col: str,
    data,
    dtype: str,
    logger,
    compression="gzip",
):
    """Legacy single column save method for fallback."""
    # This is the original _save_dataframe_column method for compatibility
    return _save_dataframe_column_legacy(group, col, data, dtype, logger, compression)


def _save_dataframe_column_legacy(
    group,
    col: str,
    data,
    dtype: str,
    logger,
    compression="gzip",
):
    """
    Save a single DataFrame column to an HDF5 group with optimized compression.

    This optimized version uses context-aware compression strategies for better
    performance and smaller file sizes. Different compression algorithms are
    selected based on data type and column name patterns.

    Args:
        group: HDF5 group to save to
        col: Column name
        data: Column data
        dtype: Data type string
        logger: Logger instance
        compression: Default compression (used for compatibility, but overridden by optimization)

    Compression Strategy:
        - LZF + shuffle: Fast access data (consensus_uid, rt, mz, intensity, scan_id)
        - GZIP level 6: JSON objects (chromatograms, spectra) and string data
        - GZIP level 9: Bulk storage data (large collections)
        - LZF: Standard numeric arrays
    """

    # Optimized compression configuration
    COMPRESSION_CONFIG = {
        "fast_access": {
            "compression": "lzf",
            "shuffle": True,
        },  # Fast I/O for IDs, rt, mz
        "numeric": {"compression": "lzf"},  # Standard numeric data
        "string": {"compression": "gzip", "compression_opts": 6},  # String data
        "json": {"compression": "gzip", "compression_opts": 6},  # JSON objects
        "bulk": {"compression": "gzip", "compression_opts": 9},  # Large bulk data
    }

    def get_optimal_compression(column_name, data_type, data_size=None):
        """Get optimal compression settings based on column type and usage pattern."""
        # Fast access columns (frequently read IDs and coordinates)
        if column_name in [
            "consensus_uid",
            "feature_uid",
            "scan_id",
            "rt",
            "mz",
            "intensity",
            "rt_original",
            "mz_original",
        ]:
            return COMPRESSION_CONFIG["fast_access"]

        # JSON object columns (complex serialized data)
        elif column_name in [
            "spectrum",
            "chromatogram",
            "chromatograms",
            "ms2_specs",
            "chrom",
        ]:
            return COMPRESSION_CONFIG["json"]

        # String/text columns
        elif data_type in ["string", "object"] and column_name in [
            "sample_name",
            "file_path",
            "label",
            "file_type",
        ]:
            return COMPRESSION_CONFIG["string"]

        # Large bulk numeric data
        elif data_size and data_size > 100000:
            return COMPRESSION_CONFIG["bulk"]

        # Standard numeric data
        else:
            return COMPRESSION_CONFIG["numeric"]

    # Get data size for optimization decisions
    data_size = len(data) if hasattr(data, "__len__") else None

    # Get optimal compression settings
    optimal_compression = get_optimal_compression(col, dtype, data_size)
    if dtype == "object" or dtype.startswith("list"):
        if col == "chrom":
            # Handle Chromatogram objects
            data_as_str = []
            for item in data:
                if item is not None:
                    data_as_str.append(item.to_json())
                else:
                    data_as_str.append("None")
            group.create_dataset(col, data=data_as_str, compression=compression)
        elif col == "ms2_scans":
            # Handle MS2 scan lists
            data_as_json_strings = []
            for item in data:
                if item is not None:
                    data_as_json_strings.append(json.dumps(list(item)))
                else:
                    data_as_json_strings.append("None")
            group.create_dataset(col, data=data_as_json_strings, **optimal_compression)
        elif col == "ms2_specs":
            # Handle MS2 spectrum lists
            data_as_lists_of_strings = []
            for item in data:
                if item is not None:
                    json_strings = []
                    for spectrum in item:
                        if spectrum is not None:
                            json_strings.append(spectrum.to_json())
                        else:
                            json_strings.append("None")
                    data_as_lists_of_strings.append(json_strings)
                else:
                    data_as_lists_of_strings.append(["None"])
            # Convert to serialized data
            serialized_data = [json.dumps(item) for item in data_as_lists_of_strings]
            group.create_dataset(col, data=serialized_data, **optimal_compression)
        elif col == "adducts":
            # Handle adducts lists (List(String))
            data_as_json_strings = []
            for item in data:
                if item is not None:
                    data_as_json_strings.append(json.dumps(item))
                else:
                    data_as_json_strings.append("[]")
            group.create_dataset(col, data=data_as_json_strings, **optimal_compression)
        elif col == "adduct_values":
            # Handle adduct_values lists (List(Struct))
            data_as_json_strings = []
            for item in data:
                if item is not None:
                    data_as_json_strings.append(json.dumps(item))
                else:
                    data_as_json_strings.append("[]")
            group.create_dataset(col, data=data_as_json_strings, **optimal_compression)
        elif col == "spec":
            # Handle single Spectrum objects
            data_as_str = []
            for item in data:
                if item is not None:
                    data_as_str.append(item.to_json())
                else:
                    data_as_str.append("None")
            group.create_dataset(col, data=data_as_str, compression=compression)
        else:
            logger.warning(
                f"Unexpectedly, column '{col}' has dtype '{dtype}'. Implement serialization for this column.",
            )
    elif dtype == "string":
        # Handle string columns
        string_data = ["None" if x is None else str(x) for x in data]
        group.create_dataset(col, data=string_data, **optimal_compression)
    else:
        # Handle numeric columns
        try:
            # Convert None values to -123 sentinel value for numeric columns
            import numpy as np

            data_array = np.array(data)

            # Check if it's a numeric dtype that might have None/null values
            if data_array.dtype == object:
                # Convert None values to -123 for numeric columns with mixed types
                processed_data = []
                for item in data:
                    if item is None:
                        processed_data.append(-123)
                    else:
                        try:
                            # Try to convert to float to check if it's numeric
                            processed_data.append(int(float(item)))
                        except (ValueError, TypeError):
                            # If conversion fails, keep original value (might be string)
                            processed_data.append(item)
                data_array = np.array(processed_data)

            group.create_dataset(col, data=data_array, **optimal_compression)
        except Exception as e:
            logger.warning(f"Failed to save column '{col}': {e}")


# Keep the original function as _save_dataframe_column for backward compatibility
_save_dataframe_column = _save_dataframe_column_legacy


def _reconstruct_object_column(data_col, col_name: str):
    """Reconstruct object columns from serialized HDF5 data."""
    reconstructed_data: list = []

    for item in data_col:
        if isinstance(item, bytes):
            item = item.decode("utf-8")

        # Handle non-string data (e.g., float32 NaN from corrupted compression)
        if not isinstance(item, str):
            import numpy as np

            if isinstance(item, (float, np.floating)) and np.isnan(item):
                reconstructed_data.append(None)
                continue
            else:
                reconstructed_data.append(None)
                continue

        if item == "None" or item == "":
            reconstructed_data.append(None)
            continue

        try:
            if col_name == "chrom":
                reconstructed_data.append(Chromatogram.from_json(item))
            elif col_name == "ms2_scans":
                scan_list = json.loads(item)
                reconstructed_data.append(scan_list)
            elif col_name == "ms2_specs":
                json_list = json.loads(item)
                if json_list == ["None"]:
                    reconstructed_data.append(None)
                else:
                    spectrum_list: list = []
                    for json_str in json_list:
                        if json_str == "None":
                            spectrum_list.append(None)
                        else:
                            spectrum_list.append(Spectrum.from_json(json_str))
                    reconstructed_data.append(spectrum_list)
            elif col_name == "spec":
                reconstructed_data.append(Spectrum.from_json(item))
            elif col_name == "adducts":
                # Handle adducts lists (List(Struct)) - convert to proper dict structure
                adducts_list = json.loads(item)
                converted_adducts = []
                for adduct_row in adducts_list:
                    if len(adduct_row) >= 3:
                        # Convert from [adduct, count, percentage] to dict structure
                        converted_adducts.append(
                            {
                                "adduct": str(adduct_row[0]),
                                "count": int(float(adduct_row[1])),
                                "percentage": float(adduct_row[2]),
                                "mass": float(adduct_row[3])
                                if len(adduct_row) > 3
                                else 0.0,
                            },
                        )
                reconstructed_data.append(converted_adducts)
            else:
                # Unknown object column
                reconstructed_data.append(None)
        except (json.JSONDecodeError, ValueError):
            reconstructed_data.append(None)

    return reconstructed_data


def _clean_string_nulls(df: pl.DataFrame) -> pl.DataFrame:
    """Convert string null representations to proper nulls."""
    for col in df.columns:
        if df[col].dtype == pl.Utf8:
            df = df.with_columns(
                [
                    pl.when(pl.col(col).is_in(["None", "", "null", "NULL"]))
                    .then(None)
                    .otherwise(pl.col(col))
                    .alias(col),
                ],
            )
    return df


def _apply_schema_casting(df: pl.DataFrame, schema: dict, df_name: str) -> pl.DataFrame:
    """Apply schema-based type casting to DataFrame columns."""
    if df_name not in schema or "columns" not in schema[df_name]:
        return df

    schema_columns = schema[df_name]["columns"]
    cast_exprs = []

    for col in df.columns:
        if col in schema_columns:
            dtype_str = schema_columns[col]["dtype"]
            # Convert string representation to actual Polars type
            if dtype_str == "pl.Object":
                cast_exprs.append(pl.col(col))  # Keep Object type as is
            elif dtype_str == "pl.Int64":
                cast_exprs.append(pl.col(col).cast(pl.Int64, strict=False))
            elif dtype_str == "pl.Float64":
                cast_exprs.append(pl.col(col).cast(pl.Float64, strict=False))
            elif dtype_str == "pl.Utf8":
                cast_exprs.append(pl.col(col).cast(pl.Utf8, strict=False))
            elif dtype_str == "pl.Int32":
                cast_exprs.append(pl.col(col).cast(pl.Int32, strict=False))
            elif dtype_str == "pl.Boolean":
                cast_exprs.append(pl.col(col).cast(pl.Boolean, strict=False))
            elif dtype_str == "pl.Null":
                cast_exprs.append(pl.col(col).cast(pl.Null, strict=False))
            else:
                cast_exprs.append(pl.col(col))  # Keep original type
        else:
            cast_exprs.append(pl.col(col))  # Keep original type

    if cast_exprs:
        df = df.with_columns(cast_exprs)

    return df


def _reorder_columns_by_schema(
    df: pl.DataFrame,
    schema: dict,
    df_name: str,
) -> pl.DataFrame:
    """Reorder DataFrame columns to match schema order."""
    if df_name not in schema or "columns" not in schema[df_name]:
        return df

    schema_columns = list(schema[df_name]["columns"].keys())
    # Only reorder columns that exist in both schema and DataFrame
    existing_columns = [col for col in schema_columns if col in df.columns]
    # Add any extra columns not in schema at the end
    extra_columns = [col for col in df.columns if col not in schema_columns]
    final_column_order = existing_columns + extra_columns

    return df.select(final_column_order)


def _create_dataframe_with_objects(data: dict, object_columns: list) -> pl.DataFrame:
    """Create DataFrame handling Object columns properly."""
    object_data = {k: v for k, v in data.items() if k in object_columns}
    regular_data = {k: v for k, v in data.items() if k not in object_columns}

    # Determine expected length from regular data or first object column
    expected_length = None
    if regular_data:
        for values in regular_data.values():
            if values is not None and hasattr(values, "__len__"):
                expected_length = len(values)
                break

    if expected_length is None and object_data:
        for values in object_data.values():
            if values is not None and hasattr(values, "__len__"):
                expected_length = len(values)
                break

    if expected_length is None:
        expected_length = 0

    # Fix any object columns that have None or empty values
    for col in object_columns:
        if col in object_data:
            values = object_data[col]
            if values is None or (hasattr(values, "__len__") and len(values) == 0):
                object_data[col] = [None] * expected_length
                # print(f"DEBUG: Fixed object column '{col}' to have length {expected_length}")

    # Create DataFrame with regular columns first
    if regular_data:
        df = pl.DataFrame(regular_data)
        # print(f"DEBUG: Created DataFrame with regular columns, shape: {df.shape}")
        # Add Object columns one by one
        for col, values in object_data.items():
            # print(f"DEBUG: Adding object column '{col}', type: {type(values)}, length: {len(values) if values is not None else 'None'}")
            if col == "adducts":
                # Handle adducts as List(Struct) - now contains dicts
                df = df.with_columns(
                    [
                        pl.Series(
                            col,
                            values,
                            dtype=pl.List(
                                pl.Struct(
                                    [
                                        pl.Field("adduct", pl.Utf8),
                                        pl.Field("count", pl.Int64),
                                        pl.Field("percentage", pl.Float64),
                                        pl.Field("mass", pl.Float64),
                                    ],
                                ),
                            ),
                        ),
                    ],
                )
            else:
                # Other object columns stay as Object
                df = df.with_columns([pl.Series(col, values, dtype=pl.Object)])
    else:
        # Only Object columns
        df = pl.DataFrame()
        for col, values in object_data.items():
            # print(f"DEBUG: Creating object column '{col}', type: {type(values)}, length: {len(values) if values is not None else 'None'}")
            if col == "adducts":
                # Handle adducts as List(Struct) - now contains dicts
                df = df.with_columns(
                    [
                        pl.Series(
                            col,
                            values,
                            dtype=pl.List(
                                pl.Struct(
                                    [
                                        pl.Field("adduct", pl.Utf8),
                                        pl.Field("count", pl.Int64),
                                        pl.Field("percentage", pl.Float64),
                                        pl.Field("mass", pl.Float64),
                                    ],
                                ),
                            ),
                        ),
                    ],
                )
            else:
                # Other object columns stay as Object
                df = df.with_columns([pl.Series(col, values, dtype=pl.Object)])

    return df


def _load_dataframe_from_group(
    group,
    schema: dict,
    df_name: str,
    logger,
    object_columns: list | None = None,
) -> pl.DataFrame:
    """Load a DataFrame from HDF5 group using schema."""
    if object_columns is None:
        object_columns = []

    data: dict = {}
    missing_columns = []

    # Iterate through schema columns in order to maintain column ordering
    logger.debug(
        f"Loading {df_name} - schema type: {type(schema)}, content: {schema.keys() if isinstance(schema, dict) else 'Not a dict'}",
    )
    schema_section = schema.get(df_name, {}) if isinstance(schema, dict) else {}
    logger.debug(f"Schema section for {df_name}: {schema_section}")
    schema_columns = (
        schema_section.get("columns", []) if isinstance(schema_section, dict) else []
    )
    logger.debug(f"Schema columns for {df_name}: {schema_columns}")
    if schema_columns is None:
        schema_columns = []

    # Get available columns from HDF5 file
    hdf5_columns = list(group.keys())
    logger.debug(f"HDF5 columns available: {hdf5_columns}")

    # Handle column name migrations for backward compatibility first
    if df_name == "samples_df":
        # Migrate old column names to new names
        column_migrations = {
            "size": "num_features",
            "file_source": "sample_source",
            "ms1": "num_ms1",
            "ms2": "num_ms2",
        }

        # Create a mapping of what's actually available after migrations
        effective_columns = hdf5_columns.copy()
        for old_name, new_name in column_migrations.items():
            if old_name in effective_columns:
                logger.info(
                    f"Will migrate column '{old_name}' to '{new_name}' for backward compatibility",
                )
                # Add the new name to effective columns and optionally remove old name
                effective_columns.append(new_name)

    # First pass: load all existing columns (including migrated ones)
    for col in schema_columns or []:
        source_col = col

        # Check if we need to load from a migrated column name
        if df_name == "samples_df":
            column_migrations = {
                "size": "num_features",
                "file_source": "sample_source",
                "ms1": "num_ms1",
                "ms2": "num_ms2",
            }
            # Reverse lookup - find old name for new name
            reverse_migrations = {v: k for k, v in column_migrations.items()}
            if col in reverse_migrations:
                old_name = reverse_migrations[col]
                if old_name in group:
                    source_col = old_name
                    logger.info(f"Loading '{col}' from old column name '{old_name}'")

        if source_col not in group:
            missing_columns.append(col)
            continue

        dtype = schema[df_name]["columns"][col].get("dtype", "native")
        if dtype == "pl.Object" or col in object_columns:
            # Handle object columns specially
            data[col] = _reconstruct_object_column(group[source_col][:], col)
        else:
            # Regular columns
            column_data = group[source_col][:]

            # Convert -123 sentinel values back to None for numeric columns
            if len(column_data) > 0:
                # Check if it's a numeric column that might contain sentinel values
                try:
                    import numpy as np

                    data_array = np.array(column_data)
                    if data_array.dtype in [np.float32, np.float64, np.int32, np.int64]:
                        # Replace -123 sentinel values with None
                        processed_data: list = []
                        for item in column_data:
                            if item == -123:
                                processed_data.append(None)
                            else:
                                processed_data.append(item)
                        data[col] = processed_data
                    else:
                        data[col] = column_data
                except Exception:
                    # If any error occurs, use original data
                    data[col] = column_data
            else:
                data[col] = column_data

    # Determine expected DataFrame length from loaded columns
    expected_length = None
    for col, values in data.items():
        if values is not None and hasattr(values, "__len__"):
            expected_length = len(values)
            logger.debug(
                f"Determined expected_length={expected_length} from loaded column '{col}'",
            )
            break

    # If no data loaded yet, try HDF5 columns directly
    if expected_length is None:
        hdf5_columns = list(group.keys())
        for col in hdf5_columns:
            col_data = group[col][:]
            if expected_length is None:
                expected_length = len(col_data)
                logger.debug(
                    f"Determined expected_length={expected_length} from HDF5 column '{col}'",
                )
                break

    # Default to 0 if no data found
    if expected_length is None:
        expected_length = 0
        logger.debug("No columns found, setting expected_length=0")

    # Second pass: handle missing columns
    for col in missing_columns:
        logger.warning(f"Column '{col}' not found in {df_name}.")
        # For missing columns, create appropriately sized array with appropriate defaults
        if col in object_columns:
            data[col] = [None] * expected_length
            logger.debug(
                f"Created missing object column '{col}' with length {expected_length}",
            )
        else:
            # Provide specific default values for new columns for backward compatibility
            if df_name == "samples_df":
                if col == "sample_group":
                    data[col] = [""] * expected_length  # Empty string default
                    logger.debug(
                        f"Created missing column '{col}' with empty string defaults",
                    )
                elif col == "sample_batch":
                    data[col] = [1] * expected_length  # Batch 1 default
                    logger.debug(
                        f"Created missing column '{col}' with batch 1 defaults",
                    )
                elif col == "sample_sequence":
                    # Create increasing sequence numbers
                    data[col] = list(range(1, expected_length + 1))
                    logger.debug(
                        f"Created missing column '{col}' with sequence 1-{expected_length}",
                    )
                else:
                    data[col] = [None] * expected_length
                    logger.debug(
                        f"Created missing regular column '{col}' with length {expected_length}",
                    )
            else:
                data[col] = [None] * expected_length
                logger.debug(
                    f"Created missing regular column '{col}' with length {expected_length}",
                )

    # Check for columns in HDF5 file that are not in schema (for backward compatibility)
    # But skip the old column names we already migrated
    migrated_old_names = set()
    if df_name == "samples_df":
        column_migrations = {
            "size": "num_features",
            "file_source": "sample_source",
            "ms1": "num_ms1",
            "ms2": "num_ms2",
        }
        migrated_old_names = set(column_migrations.keys())

    extra_columns = [
        col
        for col in hdf5_columns
        if col not in (schema_columns or []) and col not in migrated_old_names
    ]

    for col in extra_columns:
        logger.info(f"Loading extra column '{col}' not in schema for {df_name}")
        column_data = group[col][:]

        # Try to determine if this should be treated as an object column
        # by checking if the data looks like JSON strings
        if len(column_data) > 0 and isinstance(column_data[0], bytes):
            try:
                # Check if it looks like JSON
                test_decode = column_data[0].decode("utf-8")
                if test_decode.startswith("[") or test_decode.startswith("{"):
                    # Looks like JSON, treat as object column
                    data[col] = _reconstruct_object_column(column_data, col)
                    if col not in object_columns:
                        object_columns.append(col)
                else:
                    # Regular string data
                    data[col] = [
                        item.decode("utf-8") if isinstance(item, bytes) else item
                        for item in column_data
                    ]
            except Exception:
                # If decoding fails, treat as regular data
                data[col] = column_data
        else:
            data[col] = column_data

    if not data:
        return pl.DataFrame()

    # Handle byte string conversion for non-object columns
    # Only convert to strings for columns that should actually be strings
    for col, values in data.items():
        if (
            col not in object_columns
            and values is not None
            and len(values) > 0
            and isinstance(values[0], bytes)
        ):
            # Check schema to see if this should be a string column
            should_be_string = False
            if (
                df_name in schema
                and "columns" in schema[df_name]
                and col in schema[df_name]["columns"]
            ):
                dtype_str = schema[df_name]["columns"][col]["dtype"]
                should_be_string = dtype_str == "pl.Utf8"

            if should_be_string:
                processed_values = []
                for val in values:
                    if isinstance(val, bytes):
                        val = val.decode("utf-8")
                    processed_values.append(val)
                data[col] = processed_values
            # If not a string column, leave as original data type (will be cast by schema)

    # Create DataFrame with Object columns handled properly
    if object_columns:
        logger.debug(f"Creating DataFrame with object columns: {object_columns}")
        for col in object_columns:
            if col in data:
                logger.debug(
                    f"Object column '{col}': length={len(data[col]) if data[col] is not None else 'None'}",
                )
        df = _create_dataframe_with_objects(data, object_columns)
    else:
        df = pl.DataFrame(data)

    # Clean null values and apply schema
    df = _clean_string_nulls(df)
    df = _apply_schema_casting(df, schema, df_name)
    df = _reorder_columns_by_schema(df, schema, df_name)

    return df


def _save_study5_compressed(self, filename):
    """
    Compressed save identical to _save_study5 but skips serialization of chrom and ms2_specs columns in features_df.

    This version maintains full compatibility with _load_study5() while providing performance benefits
    by skipping the serialization of heavy object columns (chrom and ms2_specs) in features_df.
    """

    # if no extension is given, add .study5
    if not filename.endswith(".study5"):
        filename += ".study5"

    self.logger.debug(f"Save study")

    # delete existing file if it exists
    if os.path.exists(filename):
        os.remove(filename)

    # Load schema for column ordering
    schema_path = os.path.join(os.path.dirname(__file__), "study5_schema.json")
    schema = _load_schema(schema_path)
    if not schema:
        self.logger.warning(f"Could not load schema from {schema_path}")

    with h5py.File(filename, "w") as f:
        # Count total DataFrames to save for progress tracking
        dataframes_to_save = []
        if self.samples_df is not None and not self.samples_df.is_empty():
            dataframes_to_save.append(("samples", len(self.samples_df)))
        if self.features_df is not None and not self.features_df.is_empty():
            dataframes_to_save.append(("features", len(self.features_df)))
        if self.consensus_df is not None and not self.consensus_df.is_empty():
            dataframes_to_save.append(("consensus", len(self.consensus_df)))
        if (
            self.consensus_mapping_df is not None
            and not self.consensus_mapping_df.is_empty()
        ):
            dataframes_to_save.append(
                ("consensus_mapping", len(self.consensus_mapping_df)),
            )
        if self.consensus_ms2 is not None and not self.consensus_ms2.is_empty():
            dataframes_to_save.append(("consensus_ms2", len(self.consensus_ms2)))
        if (
            hasattr(self, "lib_df")
            and self.lib_df is not None
            and not self.lib_df.is_empty()
        ):
            dataframes_to_save.append(("lib", len(self.lib_df)))
        if (
            hasattr(self, "id_df")
            and self.id_df is not None
            and not self.id_df.is_empty()
        ):
            dataframes_to_save.append(("id", len(self.id_df)))

        total_steps = len(dataframes_to_save) + 1  # +1 for metadata

        # Show progress for large saves
        tdqm_disable = (
            self.log_level not in ["TRACE", "DEBUG", "INFO"] or total_steps < 2
        )

        with tqdm(
            total=total_steps,
            desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {getattr(self, 'log_label', '')}Saving study ({sum(count for _, count in dataframes_to_save)} total rows)",
            disable=tdqm_disable,
        ) as pbar:
            # Create groups for organization
            metadata_group = f.create_group("metadata")
            features_group = f.create_group("features")
            consensus_group = f.create_group("consensus")
            consensus_mapping_group = f.create_group("consensus_mapping")
            consensus_ms2_group = f.create_group("consensus_ms2")
            lib_group = f.create_group("lib")
            id_group = f.create_group("id")

            # Store metadata
            metadata_group.attrs["format"] = "masster-study-1"
            metadata_group.attrs["folder"] = (
                str(self.folder) if self.folder is not None else ""
            )
            metadata_group.attrs["label"] = (
                str(self.label)
                if hasattr(self, "label") and self.label is not None
                else ""
            )

            # Store parameters as JSON
            if hasattr(self, "parameters") and self.history is not None:
                try:
                    parameters_json = json.dumps(self.history, indent=2)
                    metadata_group.create_dataset("parameters", data=parameters_json)
                except (TypeError, ValueError) as e:
                    self.logger.warning(f"Failed to serialize history: {e}")
                    metadata_group.create_dataset("parameters", data="")
            else:
                metadata_group.create_dataset("parameters", data="")

            pbar.update(1)
            pbar.set_description(
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {getattr(self, 'log_label', '')}Saving dataframes",
            )

            # Store samples_df - use optimized batch processing
            if self.samples_df is not None and not self.samples_df.is_empty():
                samples_group = f.create_group("samples")
                self.logger.debug(
                    f"Saving samples_df with {len(self.samples_df)} rows using optimized method",
                )
                _save_dataframe_optimized(
                    self.samples_df,
                    samples_group,
                    schema,
                    "samples_df",
                    self.logger,
                )
                pbar.update(1)

                # Store features_df - use fast method that skips chrom and ms2_specs columns
            if self.features_df is not None and not self.features_df.is_empty():
                pbar.set_description(
                    f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {getattr(self, 'log_label', '')}Saving features ({len(self.features_df)} rows, compressed)"
                )
                self.logger.debug(
                    f"Fast saving features_df with {len(self.features_df)} rows (skipping chrom and ms2_specs)",
                )
                _save_dataframe_optimized_fast(
                    self.features_df,
                    features_group,
                    schema,
                    "features_df",
                    self.logger,
                )
                pbar.update(1)

            # Store consensus_df - use optimized batch processing
            if self.consensus_df is not None and not self.consensus_df.is_empty():
                self.logger.debug(
                    f"Saving consensus_df with {len(self.consensus_df)} rows using optimized method",
                )
                _save_dataframe_optimized(
                    self.consensus_df,
                    consensus_group,
                    schema,
                    "consensus_df",
                    self.logger,
                )
                pbar.update(1)

            # Store consensus_mapping_df - keep existing fast method
            if (
                self.consensus_mapping_df is not None
                and not self.consensus_mapping_df.is_empty()
            ):
                consensus_mapping = self.consensus_mapping_df.clone()
                self.logger.debug(
                    f"Saving consensus_mapping_df with {len(consensus_mapping)} rows",
                )
                for col in consensus_mapping.columns:
                    try:
                        data = consensus_mapping[col].to_numpy()
                        # Use LZF compression for consensus mapping data
                        consensus_mapping_group.create_dataset(
                            col,
                            data=data,
                            compression="lzf",
                            shuffle=True,
                        )
                    except Exception as e:
                        self.logger.warning(
                            f"Failed to save column '{col}' in consensus_mapping_df: {e}",
                        )
                pbar.update(1)

            # Store consensus_ms2 - use optimized batch processing
            if self.consensus_ms2 is not None and not self.consensus_ms2.is_empty():
                self.logger.debug(
                    f"Saving consensus_ms2 with {len(self.consensus_ms2)} rows using optimized method",
                )
                _save_dataframe_optimized(
                    self.consensus_ms2,
                    consensus_ms2_group,
                    schema,
                    "consensus_ms2",
                    self.logger,
                )
                pbar.update(1)

            # Store lib_df - library data
            if (
                hasattr(self, "lib_df")
                and self.lib_df is not None
                and not self.lib_df.is_empty()
            ):
                self.logger.debug(
                    f"Saving lib_df with {len(self.lib_df)} rows using optimized method",
                )
                _save_dataframe_optimized(
                    self.lib_df,
                    lib_group,
                    schema,
                    "lib_df",
                    self.logger,
                )
                pbar.update(1)

            # Store id_df - identification results
            if (
                hasattr(self, "id_df")
                and self.id_df is not None
                and not self.id_df.is_empty()
            ):
                self.logger.debug(
                    f"Saving id_df with {len(self.id_df)} rows using optimized method",
                )
                _save_dataframe_optimized(
                    self.id_df,
                    id_group,
                    schema,
                    "id_df",
                    self.logger,
                )
                pbar.update(1)

    self.logger.debug(f"Fast save completed for {filename}")


def _save_dataframe_optimized_fast(
    df,
    group,
    schema,
    df_name,
    logger,
    chunk_size=10000,
):
    """
    Save DataFrame with optimized batch processing, but skip chrom and ms2_specs columns for features_df.

    This function is identical to _save_dataframe_optimized but excludes heavy object columns
    (chrom and ms2_specs) when saving features_df to improve performance.

    Args:
        df: Polars DataFrame to save
        group: HDF5 group to save to
        schema: Schema for column ordering
        df_name: Name of the DataFrame for schema lookup
        logger: Logger instance
        chunk_size: Number of rows to process at once for memory efficiency
    """
    if df is None or df.is_empty():
        return

    try:
        # Reorder columns according to schema
        df_ordered = _reorder_columns_by_schema(df.clone(), schema, df_name)

        # Skip chrom and ms2_specs columns for features_df
        if df_name == "features_df":
            skip_columns = ["chrom", "ms2_specs"]
            df_ordered = df_ordered.select(
                [col for col in df_ordered.columns if col not in skip_columns],
            )
            logger.debug(f"Fast save: skipping columns {skip_columns} for {df_name}")

        total_rows = len(df_ordered)

        # Group columns by processing type for batch optimization
        numeric_cols = []
        string_cols = []
        object_cols = []

        for col in df_ordered.columns:
            dtype = str(df_ordered[col].dtype).lower()
            if dtype == "object":
                object_cols.append(col)
            elif dtype in ["string", "utf8"]:
                string_cols.append(col)
            else:
                numeric_cols.append(col)

        logger.debug(
            f"Saving {df_name}: {total_rows} rows, {len(numeric_cols)} numeric, {len(string_cols)} string, {len(object_cols)} object columns",
        )

        # Process numeric columns in batch (most efficient)
        if numeric_cols:
            for col in numeric_cols:
                _save_numeric_column_fast(group, col, df_ordered[col], logger)

        # Process string columns in batch
        if string_cols:
            for col in string_cols:
                _save_string_column_fast(group, col, df_ordered[col], logger)

        # Process object columns with optimized serialization
        if object_cols:
            _save_object_columns_optimized(
                group,
                df_ordered,
                object_cols,
                logger,
                chunk_size,
            )

    except Exception as e:
        logger.error(f"Failed to save DataFrame {df_name}: {e}")
        # Fallback to old method for safety
        _save_dataframe_column_legacy(df, group, schema, df_name, logger)


def _save_study5(self, filename):
    """
    Save the Study instance data to a .study5 HDF5 file with optimized schema-based format.

    This method saves all Study DataFrames (samples_df, features_df, consensus_df,
    consensus_mapping_df, consensus_ms2) using the schema defined in study5_schema.json
    for proper Polars DataFrame type handling.

    Args:
        filename (str, optional): Target file name. If None, uses default based on folder.

    Stores:
        - metadata/format (str): Data format identifier ("masster-study-1")
        - metadata/folder (str): Study default folder path
        - metadata/label (str): Study label
        - metadata/parameters (str): JSON-serialized parameters dictionary
        - samples/: samples_df DataFrame data
        - features/: features_df DataFrame data with Chromatogram and Spectrum objects
        - consensus/: consensus_df DataFrame data
        - consensus_mapping/: consensus_mapping_df DataFrame data
        - consensus_ms2/: consensus_ms2 DataFrame data with Spectrum objects
        - lib/: lib_df DataFrame data with library/compound information
        - id/: id_df DataFrame data with identification results

    Notes:
        - Uses HDF5 format with compression for efficient storage.
        - Chromatogram objects are serialized as JSON for reconstruction.
        - MS2 scan lists and Spectrum objects are properly serialized.
        - Parameters dictionary (nested dicts) are JSON-serialized for storage.
        - Optimized for use with _load_study5() method.
    """

    # if no extension is given, add .study5
    if not filename.endswith(".study5"):
        filename += ".study5"

    self.logger.info("Save study...")

    # delete existing file if it exists
    if os.path.exists(filename):
        os.remove(filename)

    # Load schema for column ordering
    schema_path = os.path.join(os.path.dirname(__file__), "study5_schema.json")
    schema = _load_schema(schema_path)
    if not schema:
        self.logger.warning(f"Could not load schema from {schema_path}")

    with h5py.File(filename, "w") as f:
        # Count total DataFrames to save for progress tracking
        dataframes_to_save = []
        if self.samples_df is not None and not self.samples_df.is_empty():
            dataframes_to_save.append(("samples", len(self.samples_df)))
        if self.features_df is not None and not self.features_df.is_empty():
            dataframes_to_save.append(("features", len(self.features_df)))
        if self.consensus_df is not None and not self.consensus_df.is_empty():
            dataframes_to_save.append(("consensus", len(self.consensus_df)))
        if (
            self.consensus_mapping_df is not None
            and not self.consensus_mapping_df.is_empty()
        ):
            dataframes_to_save.append(
                ("consensus_mapping", len(self.consensus_mapping_df)),
            )
        if self.consensus_ms2 is not None and not self.consensus_ms2.is_empty():
            dataframes_to_save.append(("consensus_ms2", len(self.consensus_ms2)))
        if (
            hasattr(self, "lib_df")
            and self.lib_df is not None
            and not self.lib_df.is_empty()
        ):
            dataframes_to_save.append(("lib", len(self.lib_df)))
        if (
            hasattr(self, "id_df")
            and self.id_df is not None
            and not self.id_df.is_empty()
        ):
            dataframes_to_save.append(("id", len(self.id_df)))

        total_steps = len(dataframes_to_save) + 1  # +1 for metadata

        # Show progress for large saves
        tdqm_disable = (
            self.log_level not in ["TRACE", "DEBUG", "INFO"] or total_steps < 2
        )

        with tqdm(
            total=total_steps,
            desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {getattr(self, 'log_label', '')}Saving study ({sum(count for _, count in dataframes_to_save)} total rows)",
            disable=tdqm_disable,
        ) as pbar:
            # Create groups for organization
            metadata_group = f.create_group("metadata")
            features_group = f.create_group("features")
            consensus_group = f.create_group("consensus")
            consensus_mapping_group = f.create_group("consensus_mapping")
            consensus_ms2_group = f.create_group("consensus_ms2")
            lib_group = f.create_group("lib")
            id_group = f.create_group("id")

            # Store metadata
            metadata_group.attrs["format"] = "masster-study-1"
            metadata_group.attrs["folder"] = (
                str(self.folder) if self.folder is not None else ""
            )
            metadata_group.attrs["label"] = (
                str(self.label)
                if hasattr(self, "label") and self.label is not None
                else ""
            )

            # Store parameters as JSON
            if hasattr(self, "parameters") and self.history is not None:
                try:
                    parameters_json = json.dumps(self.history, indent=2)
                    metadata_group.create_dataset("parameters", data=parameters_json)
                except (TypeError, ValueError) as e:
                    self.logger.warning(f"Failed to serialize history: {e}")
                    metadata_group.create_dataset("parameters", data="")
            else:
                metadata_group.create_dataset("parameters", data="")

            pbar.update(1)

            # Store samples_df - use optimized batch processing
            if self.samples_df is not None and not self.samples_df.is_empty():
                pbar.set_description(
                    f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {getattr(self, 'log_label', '')}Saving samples ({len(self.samples_df)} rows)"
                )
                samples_group = f.create_group("samples")
                self.logger.debug(
                    f"Saving samples_df with {len(self.samples_df)} rows using optimized method",
                )
                _save_dataframe_optimized(
                    self.samples_df,
                    samples_group,
                    schema,
                    "samples_df",
                    self.logger,
                )
                pbar.update(1)

            # Store features_df - use optimized batch processing
            if self.features_df is not None and not self.features_df.is_empty():
                pbar.set_description(
                    f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {getattr(self, 'log_label', '')}Saving features ({len(self.features_df)} rows)"
                )
                self.logger.debug(
                    f"Saving features_df with {len(self.features_df)} rows using optimized method",
                )
                _save_dataframe_optimized(
                    self.features_df,
                    features_group,
                    schema,
                    "features_df",
                    self.logger,
                )
                pbar.update(1)

            # Store consensus_df - use optimized batch processing
            if self.consensus_df is not None and not self.consensus_df.is_empty():
                pbar.set_description(
                    f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {getattr(self, 'log_label', '')}Saving consensus ({len(self.consensus_df)} rows)"
                )
                self.logger.debug(
                    f"Saving consensus_df with {len(self.consensus_df)} rows using optimized method",
                )
                _save_dataframe_optimized(
                    self.consensus_df,
                    consensus_group,
                    schema,
                    "consensus_df",
                    self.logger,
                )
                pbar.update(1)

            # Store consensus_mapping_df - keep existing fast method
            if (
                self.consensus_mapping_df is not None
                and not self.consensus_mapping_df.is_empty()
            ):
                consensus_mapping = self.consensus_mapping_df.clone()
                self.logger.debug(
                    f"Saving consensus_mapping_df with {len(consensus_mapping)} rows",
                )
                for col in consensus_mapping.columns:
                    try:
                        data = consensus_mapping[col].to_numpy()
                        # Use LZF compression for consensus mapping data
                        consensus_mapping_group.create_dataset(
                            col,
                            data=data,
                            compression="lzf",
                            shuffle=True,
                        )
                    except Exception as e:
                        self.logger.warning(
                            f"Failed to save column '{col}' in consensus_mapping_df: {e}",
                        )
                pbar.update(1)

            # Store consensus_ms2 - use optimized batch processing
            if self.consensus_ms2 is not None and not self.consensus_ms2.is_empty():
                self.logger.debug(
                    f"Saving consensus_ms2 with {len(self.consensus_ms2)} rows using optimized method",
                )
                _save_dataframe_optimized(
                    self.consensus_ms2,
                    consensus_ms2_group,
                    schema,
                    "consensus_ms2",
                    self.logger,
                )
                pbar.update(1)

            # Store lib_df - library data
            if (
                hasattr(self, "lib_df")
                and self.lib_df is not None
                and not self.lib_df.is_empty()
            ):
                self.logger.debug(
                    f"Saving lib_df with {len(self.lib_df)} rows using optimized method",
                )
                _save_dataframe_optimized(
                    self.lib_df,
                    lib_group,
                    schema,
                    "lib_df",
                    self.logger,
                )
                pbar.update(1)

            # Store id_df - identification results
            if (
                hasattr(self, "id_df")
                and self.id_df is not None
                and not self.id_df.is_empty()
            ):
                self.logger.debug(
                    f"Saving id_df with {len(self.id_df)} rows using optimized method",
                )
                _save_dataframe_optimized(
                    self.id_df,
                    id_group,
                    schema,
                    "id_df",
                    self.logger,
                )
                pbar.update(1)

    self.logger.info(f"Study saved successfully to {filename}")
    self.logger.debug(f"Save completed for {filename}")
    self.logger.debug(f"Save completed for {filename}")


def _load_study5(self, filename=None):
    """
    Load Study instance data from a .study5 HDF5 file.

    Restores all Study DataFrames that were saved with _save_study5() method using the
    schema defined in study5_schema.json for proper Polars DataFrame reconstruction.

    Args:
        filename (str, optional): Path to the .study5 HDF5 file to load. If None, uses default.

    Returns:
        None (modifies self in place)

    Notes:
        - Restores DataFrames with proper schema typing from study5_schema.json
        - Handles Chromatogram and Spectrum object reconstruction
        - Properly handles MS2 scan lists and spectrum lists
        - Restores parameters dictionary from JSON serialization
    """

    self.logger.info(f"Loading study from {filename}")

    # Handle default filename
    if filename is None:
        if self.folder is not None:
            filename = os.path.join(self.folder, "study.study5")
        else:
            self.logger.error("Either filename or folder must be provided")
            return

    # Add .study5 extension if not provided
    if not filename.endswith(".study5"):
        filename += ".study5"

    if not os.path.exists(filename):
        self.logger.error(f"File {filename} does not exist")
        return

    # Load schema for proper DataFrame reconstruction
    schema_path = os.path.join(os.path.dirname(__file__), "study5_schema.json")
    schema = _load_schema(schema_path)
    if not schema:
        self.logger.warning(
            f"Schema file {schema_path} not found. Using default types.",
        )

    # Define loading steps for progress tracking
    loading_steps = [
        "metadata",
        "samples_df",
        "features_df",
        "consensus_df",
        "consensus_mapping_df",
        "consensus_ms2",
        "lib_df",
        "id_df",
    ]

    # Check if progress bar should be disabled based on log level
    tdqm_disable = self.log_level not in ["TRACE", "DEBUG", "INFO"]

    with h5py.File(filename, "r") as f:
        # Use progress bar to show loading progress
        with tqdm(
            total=len(loading_steps),
            desc="Loading study",
            disable=tdqm_disable,
            unit="step"
        ) as pbar:
            # Load metadata
            pbar.set_description(
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Loading metadata",
            )
            if "metadata" in f:
                metadata = f["metadata"]
                self.folder = _decode_bytes_attr(metadata.attrs.get("folder", ""))
                if hasattr(self, "label"):
                    self.label = _decode_bytes_attr(metadata.attrs.get("label", ""))

                # Load parameters from JSON
                if "parameters" in metadata:
                    try:
                        parameters_data = metadata["parameters"][()]
                        if isinstance(parameters_data, bytes):
                            parameters_data = parameters_data.decode("utf-8")

                        if parameters_data and parameters_data != "":
                            self.history = json.loads(parameters_data)
                        else:
                            self.history = {}
                    except (json.JSONDecodeError, ValueError, TypeError) as e:
                        self.logger.warning(f"Failed to deserialize parameters: {e}")
                        self.history = {}
                else:
                    self.history = {}

                # Reconstruct self.parameters from loaded history
                from masster.study.defaults.study_def import study_defaults

                # Always create a fresh study_defaults object to ensure we have all defaults
                self.parameters = study_defaults()

                # Update parameters from loaded history if available
                if self.history and "study" in self.history:
                    study_params = self.history["study"]
                    if isinstance(study_params, dict):
                        failed_params = self.parameters.set_from_dict(
                            study_params,
                            validate=False,
                        )
                        if failed_params:
                            self.logger.debug(
                                f"Could not set study parameters: {failed_params}",
                            )
                        else:
                            self.logger.debug(
                                "Successfully updated parameters from loaded history",
                            )
                    else:
                        self.logger.debug(
                            "Study parameters in history are not a valid dictionary",
                        )
                else:
                    self.logger.debug(
                        "No study parameters found in history, using defaults",
                    )

                # Synchronize instance attributes with parameters (similar to __init__)
                # Note: folder and label are already loaded from metadata attributes above
                # but we ensure they match the parameters for consistency
                if (
                    hasattr(self.parameters, "folder")
                    and self.parameters.folder is not None
                ):
                    self.folder = self.parameters.folder
                if (
                    hasattr(self.parameters, "label")
                    and self.parameters.label is not None
                ):
                    self.label = self.parameters.label
                if hasattr(self.parameters, "log_level"):
                    self.log_level = self.parameters.log_level
                if hasattr(self.parameters, "log_label"):
                    self.log_label = (
                        self.parameters.log_label
                        if self.parameters.log_label is not None
                        else ""
                    )
                if hasattr(self.parameters, "log_sink"):
                    self.log_sink = self.parameters.log_sink
            pbar.update(1)

            # Load samples_df
            pbar.set_description(
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Loading samples",
            )
            if "samples" in f and len(f["samples"].keys()) > 0:
                self.samples_df = _load_dataframe_from_group(
                    f["samples"],
                    schema,
                    "samples_df",
                    self.logger,
                )
            else:
                # Initialize empty samples_df with the correct schema if no data exists
                self.logger.debug(
                    "No samples data found in study5 file. Initializing empty samples_df.",
                )
                self.samples_df = _create_empty_dataframe_from_schema("samples_df", schema)
            pbar.update(1)

            # Load features_df
            pbar.set_description(
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Loading features",
            )
            if "features" in f and len(f["features"].keys()) > 0:
                object_columns = ["chrom", "ms2_scans", "ms2_specs"]
                self.features_df = _load_dataframe_from_group(
                    f["features"],
                    schema,
                    "features_df",
                    self.logger,
                    object_columns,
                )
            else:
                self.features_df = _create_empty_dataframe_from_schema("features_df", schema)
            pbar.update(1)

            # Load consensus_df
            pbar.set_description(
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Loading consensus",
            )
            if "consensus" in f and len(f["consensus"].keys()) > 0:
                # Only include adducts in object_columns if it actually exists in the file
                object_columns = []
                if "adducts" in f["consensus"]:
                    object_columns.append("adducts")

                self.consensus_df = _load_dataframe_from_group(
                    f["consensus"],
                    schema,
                    "consensus_df",
                    self.logger,
                    object_columns,
                )

                # Backward compatibility: If adducts column doesn't exist, initialize with empty lists
                if self.consensus_df is not None:
                    if (
                        "adducts" not in self.consensus_df.columns
                        or self.consensus_df["adducts"].dtype == pl.Null
                    ):
                        self.logger.info(
                            "Adding missing 'adducts' column for backward compatibility",
                        )
                        empty_adducts: list[list] = [
                            [] for _ in range(len(self.consensus_df))
                        ]

                        # If column exists but is Null, drop it first
                        if "adducts" in self.consensus_df.columns:
                            self.consensus_df = self.consensus_df.drop("adducts")

                        self.consensus_df = self.consensus_df.with_columns(
                            [
                                pl.Series(
                                    "adducts",
                                    empty_adducts,
                                    dtype=pl.List(
                                        pl.Struct(
                                            [
                                                pl.Field("adduct", pl.Utf8),
                                                pl.Field("count", pl.Int64),
                                                pl.Field("percentage", pl.Float64),
                                                pl.Field("mass", pl.Float64),
                                            ],
                                        ),
                                    ),
                                ),
                            ],
                        )
            else:
                self.consensus_df = _create_empty_dataframe_from_schema("consensus_df", schema)
            pbar.update(1)

            # Load consensus_mapping_df
            pbar.set_description(
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Loading consensus mapping",
            )
            if "consensus_mapping" in f and len(f["consensus_mapping"].keys()) > 0:
                self.consensus_mapping_df = _load_dataframe_from_group(
                    f["consensus_mapping"],
                    schema,
                    "consensus_mapping_df",
                    self.logger,
                )
            else:
                self.consensus_mapping_df = _create_empty_dataframe_from_schema("consensus_mapping_df", schema)
            pbar.update(1)

            # Load consensus_ms2
            pbar.set_description(
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Loading consensus MS2",
            )
            if "consensus_ms2" in f and len(f["consensus_ms2"].keys()) > 0:
                object_columns = ["spec"]
                self.consensus_ms2 = _load_dataframe_from_group(
                    f["consensus_ms2"],
                    schema,
                    "consensus_ms2",
                    self.logger,
                    object_columns,
                )
            else:
                self.consensus_ms2 = _create_empty_dataframe_from_schema("consensus_ms2", schema)
            pbar.update(1)

            # Load lib_df
            pbar.set_description(
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Loading library data",
            )
            if "lib" in f and len(f["lib"].keys()) > 0:
                self.lib_df = _load_dataframe_from_group(
                    f["lib"],
                    schema,
                    "lib_df",
                    self.logger,
                    [],
                )
            else:
                self.lib_df = _create_empty_dataframe_from_schema("lib_df", schema)
            pbar.update(1)

            # Load id_df
            pbar.set_description(
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Loading identification results",
            )
            if "id" in f and len(f["id"].keys()) > 0:
                self.id_df = _load_dataframe_from_group(
                    f["id"],
                    schema,
                    "id_df",
                    self.logger,
                    [],
                )
            else:
                self.id_df = _create_empty_dataframe_from_schema("id_df", schema)
            pbar.update(1)

    # Check and migrate old string-based map_id to integer indices
    if (
        self.samples_df is not None
        and not self.samples_df.is_empty()
        and self.samples_df["map_id"].dtype == pl.Utf8
    ):
        self.logger.info(
            "Detected old string-based map_id format, migrating to integer indices",
        )

        # Convert string-based map_id to integer indices
        sample_count = len(self.samples_df)
        new_map_ids = list(range(sample_count))

        self.samples_df = self.samples_df.with_columns(
            pl.lit(new_map_ids).alias("map_id"),
        )

        # Ensure the column is Int64 type
        self.samples_df = self.samples_df.cast({"map_id": pl.Int64})

        self.logger.info(
            f"Successfully migrated {sample_count} samples to indexed map_id format (0 to {sample_count - 1})",
        )

    self.logger.debug("Study loaded")
