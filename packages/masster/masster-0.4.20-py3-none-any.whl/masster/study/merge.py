"""
Unified merge module for the Study class.
Supports multiple merge methods: 'kd', 'qt', 'kd-nowarp', 'kd_chunked', 'qt_chunked'
"""

import time
import numpy as np
from collections import defaultdict
from datetime import datetime
from tqdm import tqdm
import pyopenms as oms
import polars as pl
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from concurrent.futures.process import BrokenProcessPool
from masster.study.defaults import merge_defaults


def _process_kd_chunk_parallel(chunk_data):
    """
    Process a single KD chunk in parallel by reconstructing FeatureMaps from features_df slice.
    
    Args:
        chunk_data: Dictionary containing chunk processing parameters
        
    Returns:
        Tuple of (chunk_start_idx, serialized_consensus_features)
    """
    import pyopenms as oms
    
    chunk_start_idx = chunk_data['chunk_start_idx']
    chunk_features_data = chunk_data['chunk_features_data']  # List of feature dicts
    chunk_samples_data = chunk_data['chunk_samples_data']    # List of sample dicts
    params_dict = chunk_data['params']
    
    # Reconstruct FeatureMaps from features data for each sample in the chunk
    chunk_maps = []
    
    for sample_data in chunk_samples_data:
        sample_uid = sample_data['sample_uid']
        
        # Filter features for this specific sample
        sample_features = [f for f in chunk_features_data if f['sample_uid'] == sample_uid]
        
        # Create FeatureMap for this sample
        feature_map = oms.FeatureMap()
        
        # Add each feature to the map
        for feature_dict in sample_features:
            feature = oms.Feature()
            feature.setRT(float(feature_dict['rt']))
            feature.setMZ(float(feature_dict['mz']))
            feature.setIntensity(float(feature_dict['inty']))
            feature.setCharge(int(feature_dict.get('charge', 0)))
            
            # Set unique ID using feature_id for mapping back
            feature.setUniqueId(int(feature_dict['feature_id']))
            
            feature_map.push_back(feature)
        
        chunk_maps.append(feature_map)
    
    # Create the chunk consensus map
    chunk_consensus_map = oms.ConsensusMap()
    
    # Set up file descriptions for chunk
    file_descriptions = chunk_consensus_map.getColumnHeaders()
    for j, (feature_map, sample_data) in enumerate(zip(chunk_maps, chunk_samples_data)):
        file_description = file_descriptions.get(j, oms.ColumnHeader())
        file_description.filename = sample_data['sample_name']
        file_description.size = feature_map.size()
        file_description.unique_id = feature_map.getUniqueId()
        file_descriptions[j] = file_description
    
    chunk_consensus_map.setColumnHeaders(file_descriptions)
    
    # Use KD algorithm for chunk
    grouper = oms.FeatureGroupingAlgorithmKD()
    chunk_params = grouper.getParameters()
    chunk_params.setValue("mz_unit", "Da")
    chunk_params.setValue("nr_partitions", params_dict['nr_partitions'])
    chunk_params.setValue("warp:enabled", "true")
    chunk_params.setValue("warp:rt_tol", params_dict['rt_tol'])
    chunk_params.setValue("warp:mz_tol", params_dict['mz_tol'])
    chunk_params.setValue("link:rt_tol", params_dict['rt_tol'])
    chunk_params.setValue("link:mz_tol", params_dict['mz_tol'])
    chunk_params.setValue("link:min_rel_cc_size", params_dict['min_rel_cc_size'])
    chunk_params.setValue("link:max_pairwise_log_fc", params_dict['max_pairwise_log_fc'])
    chunk_params.setValue("link:max_nr_conflicts", params_dict['max_nr_conflicts'])
    
    grouper.setParameters(chunk_params)
    grouper.group(chunk_maps, chunk_consensus_map)
    
    # Serialize the consensus map result for cross-process communication
    consensus_features = []
    for consensus_feature in chunk_consensus_map:
        feature_data = {
            'rt': consensus_feature.getRT(),
            'mz': consensus_feature.getMZ(),
            'intensity': consensus_feature.getIntensity(),
            'quality': consensus_feature.getQuality(),
            'unique_id': str(consensus_feature.getUniqueId()),
            'features': []
        }
        
        # Get constituent features
        for feature_handle in consensus_feature.getFeatureList():
            feature_handle_data = {
                'unique_id': str(feature_handle.getUniqueId()),
                'map_index': feature_handle.getMapIndex()
            }
            feature_data['features'].append(feature_handle_data)
        
        consensus_features.append(feature_data)
    
    return chunk_start_idx, consensus_features


def _deserialize_consensus_features(consensus_features):
    """
    Deserialize consensus features back into an OpenMS ConsensusMap.
    
    Args:
        consensus_features: List of serialized consensus feature dictionaries
        
    Returns:
        OpenMS ConsensusMap object
    """
    import pyopenms as oms
    
    consensus_map = oms.ConsensusMap()
    
    for feature_data in consensus_features:
        consensus_feature = oms.ConsensusFeature()
        consensus_feature.setRT(float(feature_data['rt']))
        consensus_feature.setMZ(float(feature_data['mz']))
        consensus_feature.setIntensity(float(feature_data['intensity']))
        consensus_feature.setQuality(float(feature_data['quality']))
        consensus_feature.setUniqueId(int(feature_data['unique_id']))
        
        # Reconstruct feature handles (simplified approach)
        feature_handles = []
        for handle_data in feature_data['features']:
            feature_handle = oms.FeatureHandle()
            feature_handle.setUniqueId(int(handle_data['unique_id']))
            feature_handle.setMapIndex(int(handle_data['map_index']))
            feature_handles.append(feature_handle)
        
        # Set the feature list - properly add feature handles back to consensus feature
        if feature_handles:
            # Add each feature handle to the consensus feature using the correct OpenMS API
            for feature_handle in feature_handles:
                consensus_feature.getFeatureList().append(feature_handle)
        
        consensus_map.push_back(consensus_feature)
    
    return consensus_map


def _process_qt_chunk_parallel(chunk_data):
    """
    Process a single QT chunk in parallel by reconstructing FeatureMaps from features_df slice.
    
    Args:
        chunk_data: Dictionary containing chunk processing parameters
        
    Returns:
        Tuple of (chunk_start_idx, serialized_consensus_features)
    """
    import pyopenms as oms
    
    chunk_start_idx = chunk_data['chunk_start_idx']
    chunk_features_data = chunk_data['chunk_features_data']  # List of feature dicts
    chunk_samples_data = chunk_data['chunk_samples_data']    # List of sample dicts
    params_dict = chunk_data['params']
    
    # Reconstruct FeatureMaps from features data for each sample in the chunk
    chunk_maps = []
    
    for sample_data in chunk_samples_data:
        sample_uid = sample_data['sample_uid']
        
        # Filter features for this specific sample
        sample_features = [f for f in chunk_features_data if f['sample_uid'] == sample_uid]
        
        # Create FeatureMap for this sample
        feature_map = oms.FeatureMap()
        
        # Add each feature to the map
        for feature_dict in sample_features:
            feature = oms.Feature()
            feature.setRT(float(feature_dict['rt']))
            feature.setMZ(float(feature_dict['mz']))
            feature.setIntensity(float(feature_dict['inty']))
            feature.setCharge(int(feature_dict.get('charge', 0)))
            
            # Set unique ID using feature_id for mapping back
            feature.setUniqueId(int(feature_dict['feature_id']))
            
            feature_map.push_back(feature)
        
        chunk_maps.append(feature_map)
    
    # Create the chunk consensus map
    chunk_consensus_map = oms.ConsensusMap()
    
    # Set up file descriptions for chunk
    file_descriptions = chunk_consensus_map.getColumnHeaders()
    for j, (feature_map, sample_data) in enumerate(zip(chunk_maps, chunk_samples_data)):
        file_description = file_descriptions.get(j, oms.ColumnHeader())
        file_description.filename = sample_data['sample_name']
        file_description.size = feature_map.size()
        file_description.unique_id = feature_map.getUniqueId()
        file_descriptions[j] = file_description
    
    chunk_consensus_map.setColumnHeaders(file_descriptions)
    
    # Use QT algorithm for chunk
    grouper = oms.FeatureGroupingAlgorithmQT()
    chunk_params = grouper.getParameters()
    chunk_params.setValue("distance_RT:max_difference", params_dict['rt_tol'])
    chunk_params.setValue("distance_MZ:max_difference", params_dict['mz_tol'])
    chunk_params.setValue("distance_MZ:unit", "Da")
    chunk_params.setValue("ignore_charge", "true")
    chunk_params.setValue("nr_partitions", params_dict['nr_partitions'])
    
    grouper.setParameters(chunk_params)
    grouper.group(chunk_maps, chunk_consensus_map)
    
    # Serialize the consensus map result for cross-process communication
    consensus_features = []
    for consensus_feature in chunk_consensus_map:
        feature_data = {
            'rt': consensus_feature.getRT(),
            'mz': consensus_feature.getMZ(),
            'intensity': consensus_feature.getIntensity(),
            'quality': consensus_feature.getQuality(),
            'unique_id': str(consensus_feature.getUniqueId()),
            'features': []
        }
        
        # Get constituent features
        for feature_handle in consensus_feature.getFeatureList():
            feature_handle_data = {
                'unique_id': str(feature_handle.getUniqueId()),
                'map_index': feature_handle.getMapIndex()
            }
            feature_data['features'].append(feature_handle_data)
        
        consensus_features.append(feature_data)
    
    return chunk_start_idx, consensus_features


def _serialize_feature_map(feature_map):
    """
    Serialize a FeatureMap to a list of dictionaries for multiprocessing.
    
    Args:
        feature_map: OpenMS FeatureMap object
        
    Returns:
        List of feature dictionaries
    """
    features_data = []
    for feature in feature_map:
        feature_data = {
            'rt': feature.getRT(),
            'mz': feature.getMZ(), 
            'intensity': feature.getIntensity(),
            'charge': feature.getCharge(),
            'unique_id': feature.getUniqueId()
        }
        features_data.append(feature_data)
    return features_data


def merge(self, **kwargs) -> None:
    """
    Group features across samples into consensus features using various algorithms.

    This function provides a unified interface to multiple feature grouping algorithms,
    each optimized for different dataset sizes and analysis requirements.

    Parameters
    ----------
    **kwargs : dict
        Parameters from merge_defaults class:
        - method : str, default 'quality'
          Merge algorithm: 'sensitivity', 'qt', 'nowarp', 'kd_chunked', 'qt_chunked', 'quality'
        - min_samples : int, default 10  
          Minimum number of samples for consensus feature
        - rt_tol : float, default 2.0
          RT tolerance in seconds
        - mz_tol : float, default 0.01
          m/z tolerance in Da (Daltons) for all methods
        - chunk_size : int, default 500
          Chunk size for 'chunked' method
        - threads : int, default 1
          Number of parallel processes for chunked methods (kd_chunked, qt_chunked)
        - nr_partitions : int, default 500
          Number of partitions in m/z dimension for KD algorithms
        - min_rel_cc_size : float, default 0.3
          Minimum relative connected component size for conflict resolution
        - max_pairwise_log_fc : float, default 0.5
          Maximum pairwise log fold change for conflict resolution
        - max_nr_conflicts : int, default 0
          Maximum number of conflicts allowed in consensus feature
        - link_ms2 : bool, default True
          Whether to link MS2 spectra to consensus features

    Algorithm Guidelines
    -------------------
    - Quality: KD with post-processing quality control to reduce oversegmentation (RECOMMENDED DEFAULT)
      Includes RT tolerance optimization, secondary clustering, and quality filtering
    - Sensitivity: Best raw sensitivity, O(n log n), maximum feature detection
    - QT: Thorough but slow O(n²), good for <1000 samples  
    - NoWarp: Memory efficient KD without RT warping for large datasets
    - KD-Chunked: Memory-optimized KD algorithm for very large datasets (>5000 samples)
      Uses optimized partitioning for better memory management while maintaining
      full cross-sample consensus feature detection. Supports parallel processing.
    - QT-Chunked: Memory-optimized QT algorithm for very large datasets (>5000 samples)
      Uses QT clustering in first stage with optimized cross-chunk consensus building.
      Supports parallel processing.

    Parallel Processing
    ------------------
    For kd_chunked and qt_chunked methods, use threads > 1 to enable parallel processing
    of chunk alignments. This can significantly reduce processing time for large datasets
    by processing multiple chunks simultaneously in separate processes.
    
    Example:
        study.merge(method='kd_chunked', threads=4, chunk_size=200)
    """
    start_time = time.time()
    
    # Initialize with defaults and override with kwargs
    params = merge_defaults()
    
    # Filter and apply only valid parameters
    valid_params = set(params.list_parameters())
    for key, value in kwargs.items():
        if key in valid_params:
            setattr(params, key, value)
        else:
            self.logger.warning(f"Unknown parameter '{key}' ignored")
    
    # Backward compatibility: Map old method names to new names
    method_mapping = {
        'kd': 'sensitivity',
        'kd-nowarp': 'nowarp', 
        'kd_nowarp': 'nowarp',
        'kd-strict': 'quality',
        'kd_strict': 'quality',
        'kdstrict': 'quality',
        'chunked': 'kd_chunked',  # Map old 'chunked' to 'kd_chunked'
        'qtchunked': 'qt_chunked',  # QT chunked variants
        'qt-chunked': 'qt_chunked',
        'kdchunked': 'kd_chunked',  # KD chunked variants 
        'kd-chunked': 'kd_chunked'
    }
    
    if params.method in method_mapping:
        old_method = params.method
        params.method = method_mapping[old_method]
        self.logger.info(f"Method '{old_method}' is deprecated. Using '{params.method}' instead.")
    
    # Validate method
    if params.method not in ['sensitivity', 'qt', 'nowarp', 'kd_chunked', 'qt_chunked', 'quality']:
        raise ValueError(f"Invalid method '{params.method}'. Must be one of: ['sensitivity', 'qt', 'nowarp', 'kd_chunked', 'qt_chunked', 'quality']")
    
    # Check if chunked method is advisable for large datasets
    num_samples = len(self.samples_df) if hasattr(self, 'samples_df') and self.samples_df is not None else 0
    if num_samples > 500:
        chunked_methods = {'kd_chunked', 'qt_chunked'}
        if params.method not in chunked_methods:
            self.logger.warning(
                f"Large dataset detected ({num_samples} samples > 500). "
                f"For better performance and memory efficiency, consider using a chunked method: "
                f"'kd_chunked' or 'qt_chunked' instead of '{params.method}'"
            )
    
    # Persist last used params for diagnostics
    try:
        self._merge_params_last = params.to_dict()
    except Exception:
        self._merge_params_last = {}
    
    # Store merge parameters in history
    try:
        if hasattr(self, 'store_history'):
            self.store_history(['merge'], params.to_dict())
        else:
            self.logger.warning("History storage not available - parameters not saved to history")
    except Exception as e:
        self.logger.warning(f"Failed to store merge parameters in history: {e}")
    
    # Ensure feature maps are available for merging (regenerate if needed)
    if len(self.features_maps) < len(self.samples_df):
        self.features_maps = []
        # Feature maps will be generated on-demand within each merge method
    
    self.logger.info(
        f"Merge: {params.method}, samples={params.min_samples}, rt_tol={params.rt_tol}s, mz_tol={params.mz_tol}Da, min_rel_cc_size={params.min_rel_cc_size}, max_pairwise_log_fc={params.max_pairwise_log_fc}, max_nr_conflicts={params.max_nr_conflicts}"
    )
    
    # Initialize
    self._reset_consensus_data()

    # Cache adducts for performance (avoid repeated _get_adducts() calls)
    cached_adducts_df = None
    cached_valid_adducts = None
    try:
        cached_adducts_df = self._get_adducts()
        if not cached_adducts_df.is_empty():
            cached_valid_adducts = set(cached_adducts_df["name"].to_list())
        else:
            cached_valid_adducts = set()
    except Exception as e:
        self.logger.warning(f"Could not retrieve study adducts: {e}")
        cached_valid_adducts = set()
    
    # Always allow '?' adducts
    cached_valid_adducts.add("?")
    
    # Route to algorithm implementation  
    if params.method == 'sensitivity':
        consensus_map = _merge_kd(self, params)
        # Extract consensus features
        self._extract_consensus_features(consensus_map, params.min_samples, cached_adducts_df, cached_valid_adducts)
    elif params.method == 'qt':
        consensus_map = _merge_qt(self, params)
        # Extract consensus features
        self._extract_consensus_features(consensus_map, params.min_samples, cached_adducts_df, cached_valid_adducts)
    elif params.method == 'nowarp':
        consensus_map = _merge_kd_nowarp(self, params)
        # Extract consensus features
        self._extract_consensus_features(consensus_map, params.min_samples, cached_adducts_df, cached_valid_adducts)
    elif params.method == 'quality':
        consensus_map = _merge_kd_strict(self, params)
        # Note: _merge_kd_strict handles both consensus_df and consensus_mapping_df directly
    elif params.method == 'kd_chunked':
        consensus_map = _merge_kd_chunked(self, params, cached_adducts_df, cached_valid_adducts)
        # Note: _merge_kd_chunked populates consensus_df directly, no need to extract
    elif params.method == 'qt_chunked':
        consensus_map = _merge_qt_chunked(self, params, cached_adducts_df, cached_valid_adducts)
        # Note: _merge_qt_chunked populates consensus_df directly, no need to extract
    
    # Enhanced post-clustering to merge over-segmented features (for qt and kd methods)
    if params.method in ['qt', 'sensitivity', 'qt_chunked', 'kd_chunked']:
        self._consensus_cleanup(params.rt_tol, params.mz_tol)
    
    # Perform adduct grouping
    self._perform_adduct_grouping(params.rt_tol, params.mz_tol)
    
    # Identify coeluting consensus features by mass shifts and update adduct information
    self._identify_adduct_by_mass_shift(params.rt_tol, cached_adducts_df)
    
    # Link MS2 if requested
    if params.link_ms2:
        self._finalize_merge(params.link_ms2, params.min_samples)
    
    # Log completion without the misleading feature count
    elapsed = time.time() - start_time
    self.logger.debug(f"Merge process completed in {elapsed:.1f}s")


def _merge_kd(self, params: merge_defaults) -> oms.ConsensusMap:
    """KD-tree based merge (fast, recommended)"""
    
    # Generate temporary feature maps on-demand from features_df
    temp_feature_maps = _generate_feature_maps_on_demand(self)
    
    consensus_map = oms.ConsensusMap()
    file_descriptions = consensus_map.getColumnHeaders()
    
    for i, feature_map in enumerate(temp_feature_maps):
        file_description = file_descriptions.get(i, oms.ColumnHeader())
        file_description.filename = self.samples_df.row(i, named=True)["sample_name"]
        file_description.size = feature_map.size()
        file_description.unique_id = feature_map.getUniqueId()
        file_descriptions[i] = file_description
    
    consensus_map.setColumnHeaders(file_descriptions)
    
    # Configure KD algorithm
    grouper = oms.FeatureGroupingAlgorithmKD()
    params_oms = grouper.getParameters()
    
    params_oms.setValue("mz_unit", "Da")
    params_oms.setValue("nr_partitions", params.nr_partitions)
    params_oms.setValue("warp:enabled", "true")
    params_oms.setValue("warp:rt_tol", params.rt_tol)
    params_oms.setValue("warp:mz_tol", params.mz_tol)
    params_oms.setValue("link:rt_tol", params.rt_tol)
    params_oms.setValue("link:mz_tol", params.mz_tol)
    #params_oms.setValue("link:min_rel_cc_size", params.min_rel_cc_size)
    #params_oms.setValue("link:max_pairwise_log_fc", params.max_pairwise_log_fc)
    #params_oms.setValue("link:max_nr_conflicts", params.max_nr_conflicts)
    #params_oms.setValue("link:charge_merging", "With_charge_zero") THIS LEADS TO A CRASH
    
    grouper.setParameters(params_oms)
    grouper.group(temp_feature_maps, consensus_map)
    
    return consensus_map


def _generate_feature_maps_on_demand(study):
    """
    Generate feature maps on-demand from study.features_df for merge operations.
    Returns temporary feature maps that are not cached in the study.
    
    Args:
        study: Study object containing features_df and samples_df
    
    Returns:
        list: List of temporary FeatureMap objects
    """
    import polars as pl
    import pyopenms as oms
    import numpy as np
    
    if study.features_df is None or len(study.features_df) == 0:
        study.logger.error("No features_df available for generating feature maps")
        return []
    
    temp_feature_maps = []
    n_samples = len(study.samples_df)
    n_features = len(study.features_df)
    
    # Performance optimization: use efficient polars groupby for large datasets
    use_groupby_optimization = n_features > 5000
    if use_groupby_optimization:
        study.logger.debug(f"Using polars groupby optimization for {n_features} features across {n_samples} samples")
        
        # Pre-group features by sample_uid - this is much more efficient than repeated filtering
        features_by_sample = study.features_df.group_by("sample_uid").agg([
            pl.col("feature_id"),
            pl.col("mz"), 
            pl.col("rt"),
            pl.col("inty"),
            pl.col("quality").fill_null(1.0),
            pl.col("charge").fill_null(0)
        ])
        
        # Convert to dictionary for fast lookups
        sample_feature_dict = {}
        for row in features_by_sample.iter_rows(named=True):
            sample_uid = row["sample_uid"]
            # Convert lists to numpy arrays for vectorized operations
            sample_feature_dict[sample_uid] = {
                "feature_id": np.array(row["feature_id"]),
                "mz": np.array(row["mz"]),
                "rt": np.array(row["rt"]),
                "inty": np.array(row["inty"]),
                "quality": np.array(row["quality"]),
                "charge": np.array(row["charge"])
            }
    
    # Process each sample in order
    for sample_index, row_dict in enumerate(study.samples_df.iter_rows(named=True)):
        sample_uid = row_dict["sample_uid"]
        
        if use_groupby_optimization:
            # Use pre-grouped data with vectorized operations
            if sample_uid not in sample_feature_dict:
                feature_map = oms.FeatureMap()
                temp_feature_maps.append(feature_map)
                continue
                
            sample_data = sample_feature_dict[sample_uid]
            n_sample_features = len(sample_data["feature_id"])
            
            if n_sample_features == 0:
                feature_map = oms.FeatureMap()
                temp_feature_maps.append(feature_map)
                continue
            
            # Create new FeatureMap
            feature_map = oms.FeatureMap()
            
            # Use vectorized data directly (no conversion needed)
            for i in range(n_sample_features):
                try:
                    feature = oms.Feature()
                    feature.setUniqueId(int(sample_data["feature_id"][i]))
                    feature.setMZ(float(sample_data["mz"][i]))
                    feature.setRT(float(sample_data["rt"][i]))
                    feature.setIntensity(float(sample_data["inty"][i]))
                    feature.setOverallQuality(float(sample_data["quality"][i]))
                    feature.setCharge(int(sample_data["charge"][i]))
                    feature_map.push_back(feature)
                except (ValueError, TypeError) as e:
                    study.logger.warning(f"Skipping feature due to conversion error: {e}")
                    continue
        else:
            # Use original polars-based approach for smaller datasets
            sample_features = study.features_df.filter(pl.col("sample_uid") == sample_uid)
            
            # Create new FeatureMap
            feature_map = oms.FeatureMap()
            
            # Convert DataFrame features to OpenMS Features
            for feature_row in sample_features.iter_rows(named=True):
                feature = oms.Feature()
                
                # Set properties from DataFrame (handle missing values gracefully)
                try:
                    feature.setUniqueId(int(feature_row["feature_id"]))
                    feature.setMZ(float(feature_row["mz"]))
                    feature.setRT(float(feature_row["rt"]))
                    feature.setIntensity(float(feature_row["inty"]))
                    feature.setOverallQuality(float(feature_row["quality"]))
                    feature.setCharge(int(feature_row["charge"]))
                    
                    # Add to feature map
                    feature_map.push_back(feature)
                except (ValueError, TypeError) as e:
                    study.logger.warning(f"Skipping feature due to conversion error: {e}")
                    continue
        
        temp_feature_maps.append(feature_map)
    
    study.logger.debug(f"Generated {len(temp_feature_maps)} temporary feature maps from features_df")
    return temp_feature_maps


def _merge_qt(self, params: merge_defaults) -> oms.ConsensusMap:
    """QT (Quality Threshold) based merge"""
    
    # Generate temporary feature maps on-demand from features_df
    temp_feature_maps = _generate_feature_maps_on_demand(self)
    
    n_samples = len(temp_feature_maps)
    if n_samples > 1000:
        self.logger.warning(f"QT with {n_samples} samples may be slow [O(n²)]. Consider KD [O(n log n)]")
    
    consensus_map = oms.ConsensusMap()
    file_descriptions = consensus_map.getColumnHeaders()
    
    for i, feature_map in enumerate(temp_feature_maps):
        file_description = file_descriptions.get(i, oms.ColumnHeader())
        file_description.filename = self.samples_df.row(i, named=True)["sample_name"]
        file_description.size = feature_map.size()
        file_description.unique_id = feature_map.getUniqueId()
        file_descriptions[i] = file_description
    
    consensus_map.setColumnHeaders(file_descriptions)
    
    # Configure QT algorithm
    grouper = oms.FeatureGroupingAlgorithmQT()
    params_oms = grouper.getParameters()
    
    params_oms.setValue("distance_RT:max_difference", params.rt_tol)
    params_oms.setValue("distance_MZ:max_difference", params.mz_tol)
    params_oms.setValue("distance_MZ:unit", "Da")  # QT now uses Da like all other methods
    params_oms.setValue("ignore_charge", "true")
    #params_oms.setValue("min_rel_cc_size", params.min_rel_cc_size)
    #params_oms.setValue("max_pairwise_log_fc", params.max_pairwise_log_fc)
    #params_oms.setValue("max_nr_conflicts", params.max_nr_conflicts)
    params_oms.setValue("nr_partitions", params.nr_partitions)

    grouper.setParameters(params_oms)
    grouper.group(temp_feature_maps, consensus_map)
    
    return consensus_map


def _merge_kd_strict(self, params: merge_defaults) -> oms.ConsensusMap:
    """
    Quality merge: Standard KD algorithm with post-processing quality control.
    
    This method combines the sensitivity of KD clustering with post-processing steps
    to reduce oversegmentation while maintaining high-quality consensus features.
    This is the recommended default method.
    
    Post-processing features:
    1. RT tolerance optimization (optional)
    2. Secondary clustering for close features
    3. Sample overlap validation
    4. RT spread quality filtering
    5. Chromatographic coherence validation
    
    Additional parameters supported in params:
    - optimize_rt_tol: bool - Enable RT tolerance optimization
    - rt_tol_range: tuple - RT tolerance range for optimization (min, max)
    - secondary_merge_rt_tol: float - Secondary merge RT tolerance (default: 0.5s)
    - secondary_merge_mz_tol: float - Secondary merge m/z tolerance (default: 0.005)
    - min_sample_overlap: float - Minimum sample overlap for merging (0.0-1.0, default: 0.8)
    - max_rt_spread: float - Maximum RT spread allowed (default: 2x rt_tol)
    - min_coherence: float - Minimum chromatographic coherence (default: 0.0, disabled)
    """
    
    # Check for RT tolerance optimization
    optimize_rt_tol = getattr(params, 'optimize_rt_tol', False)
    
    if optimize_rt_tol:
        # Optimize RT tolerance first
        optimal_rt_tol = _optimize_rt_tolerance(self, params)
        self.logger.info(f"RT tolerance optimization: {params.rt_tol}s → {optimal_rt_tol}s")
        # Create modified params with optimal RT tolerance
        import copy
        optimized_params = copy.deepcopy(params)
        optimized_params.rt_tol = optimal_rt_tol
    else:
        optimized_params = params
    
    # Phase 1: Standard KD clustering
    self.logger.info("Initial KD clustering")
    consensus_map = _merge_kd(self, optimized_params)
    
    # Phase 2: Post-processing quality control
    self.logger.info("Post-processing quality control")
    consensus_map = _apply_kd_strict_postprocessing(self, consensus_map, optimized_params)
    
    return consensus_map


def _optimize_rt_tolerance(self, params: merge_defaults) -> float:
    """
    Optimize RT tolerance by testing different values and measuring oversegmentation.
    
    Args:
        self: Study object
        params: Merge parameters
        
    Returns:
        Optimal RT tolerance value
    """
    rt_tol_range = getattr(params, 'rt_tol_range', (0.8, 2.0))
    rt_tol_steps = getattr(params, 'rt_tol_steps', 5)
    
    self.logger.info(f"Optimizing RT tolerance in range {rt_tol_range} with {rt_tol_steps} steps")
    
    # Generate test values
    test_rt_tols = [rt_tol_range[0] + i * (rt_tol_range[1] - rt_tol_range[0]) / (rt_tol_steps - 1) 
                    for i in range(rt_tol_steps)]
    
    best_rt_tol = params.rt_tol
    best_score = float('inf')
    
    # Store original features for restoration
    original_consensus_df = getattr(self, 'consensus_df', pl.DataFrame())
    original_consensus_mapping_df = getattr(self, 'consensus_mapping_df', pl.DataFrame())
    
    for test_rt_tol in test_rt_tols:
        try:
            # Create test parameters
            import copy
            test_params = copy.deepcopy(params)
            test_params.rt_tol = test_rt_tol
            
            # Run KD merge with test parameters
            test_consensus_map = _merge_kd(self, test_params)
            
            # Extract consensus features temporarily for analysis
            self._extract_consensus_features(test_consensus_map, test_params.min_samples)
            
            if len(self.consensus_df) == 0:
                continue
            
            # Calculate oversegmentation metrics
            oversegmentation_score = _calculate_oversegmentation_score(self, test_rt_tol)
            
            self.logger.debug(f"RT tol {test_rt_tol:.1f}s: {len(self.consensus_df)} features, score: {oversegmentation_score:.3f}")
            
            # Lower score is better (less oversegmentation)
            if oversegmentation_score < best_score:
                best_score = oversegmentation_score
                best_rt_tol = test_rt_tol
                
        except Exception as e:
            self.logger.warning(f"RT tolerance optimization failed for {test_rt_tol}s: {e}")
            continue
    
    # Restore original consensus data
    self.consensus_df = original_consensus_df
    self.consensus_mapping_df = original_consensus_mapping_df
    
    self.logger.info(f"Optimal RT tolerance: {best_rt_tol:.1f}s (score: {best_score:.3f})")
    return best_rt_tol


def _calculate_oversegmentation_score(self, rt_tol: float) -> float:
    """
    Calculate oversegmentation score based on feature density and RT spread metrics.
    Lower scores indicate less oversegmentation.
    
    Args:
        self: Study object
        rt_tol: RT tolerance used
        
    Returns:
        Oversegmentation score (lower = better)
    """
    if len(self.consensus_df) == 0:
        return float('inf')
    
    # Metric 1: Feature density (features per RT second)
    rt_range = self.consensus_df['rt'].max() - self.consensus_df['rt'].min()
    if rt_range <= 0:
        return float('inf')
    
    feature_density = len(self.consensus_df) / rt_range
    
    # Metric 2: Average RT spread relative to tolerance
    rt_spreads = (self.consensus_df['rt_max'] - self.consensus_df['rt_min'])
    avg_rt_spread_ratio = rt_spreads.mean() / rt_tol if rt_tol > 0 else float('inf')
    
    # Metric 3: Proportion of features with low sample counts (indicates fragmentation)
    low_sample_features = len(self.consensus_df.filter(pl.col('number_samples') <= 5))
    low_sample_ratio = low_sample_features / len(self.consensus_df)
    
    # Metric 4: Number of features with excessive RT spread
    excessive_spread_features = len(rt_spreads.filter(rt_spreads > rt_tol * 2))
    excessive_spread_ratio = excessive_spread_features / len(self.consensus_df)
    
    # Combined score (weighted combination)
    oversegmentation_score = (
        0.4 * (feature_density / 10.0) +  # Normalize to reasonable scale
        0.3 * avg_rt_spread_ratio +
        0.2 * low_sample_ratio +
        0.1 * excessive_spread_ratio
    )
    
    return oversegmentation_score


def _apply_kd_strict_postprocessing(self, consensus_map: oms.ConsensusMap, params: merge_defaults) -> oms.ConsensusMap:
    """
    Apply post-processing quality control to KD consensus map.
    
    Args:
        consensus_map: Initial consensus map from KD
        params: Merge parameters with kd-strict options
        
    Returns:
        Processed consensus map with reduced oversegmentation
    """
    if consensus_map.size() == 0:
        self.logger.warning("Empty consensus map provided to post-processing")
        return consensus_map
    
    self.logger.debug(f"Post-processing {consensus_map.size()} initial consensus features")
    
    # Step 1: Extract initial consensus features
    original_min_samples = params.min_samples
    params.min_samples = 1  # Extract all features initially
    
    self._extract_consensus_features(consensus_map, params.min_samples)
    initial_feature_count = len(self.consensus_df)
    
    if initial_feature_count == 0:
        self.logger.warning("No consensus features extracted for post-processing")
        params.min_samples = original_min_samples
        return consensus_map
    
    # Step 2: Secondary clustering for close features
    secondary_merge_rt_tol = getattr(params, 'secondary_merge_rt_tol', 0.5)
    secondary_merge_mz_tol = getattr(params, 'secondary_merge_mz_tol', 0.005)
    
    self.logger.debug(f"Secondary clustering with RT≤{secondary_merge_rt_tol}s, m/z≤{secondary_merge_mz_tol}")
    merged_features = _perform_secondary_clustering(self, secondary_merge_rt_tol, secondary_merge_mz_tol)
    
    # Step 3: Sample overlap validation
    min_sample_overlap = getattr(params, 'min_sample_overlap', 0.8)
    if min_sample_overlap > 0:
        self.logger.debug(f"Sample overlap validation (threshold: {min_sample_overlap})")
        merged_features = _validate_sample_overlap(self, merged_features, min_sample_overlap)
    
    # Step 4: RT spread quality filtering
    if params.rt_tol is not None:
        max_rt_spread = getattr(params, 'max_rt_spread', params.rt_tol * 2)
        if max_rt_spread is not None:
            self.logger.debug(f"RT spread filtering (max: {max_rt_spread:.1f}s)")
            merged_features = _filter_rt_spread(self, merged_features, max_rt_spread)
        else:
            self.logger.debug("Skipping RT spread filtering - max_rt_spread is None")
    else:
        self.logger.debug("Skipping RT spread filtering - rt_tol is None")
    
    # Step 5: Chromatographic coherence filtering (optional)
    min_coherence = getattr(params, 'min_coherence', 0.0)
    if min_coherence > 0:
        self.logger.debug(f"Chromatographic coherence filtering (min: {min_coherence})")
        merged_features = _filter_coherence(self, merged_features, min_coherence)
    
    # Step 6: Rebuild consensus_df with filtered features and preserve mapping
    original_mapping_df = self.consensus_mapping_df.clone()  # Save original mapping
    self.consensus_df = pl.DataFrame(merged_features, strict=False)
    
    # Step 7: Apply original min_samples filter
    params.min_samples = original_min_samples
    if params.min_samples > 1:
        l1 = len(self.consensus_df)
        self.consensus_df = self.consensus_df.filter(
            pl.col("number_samples") >= params.min_samples
        )
        filtered_count = l1 - len(self.consensus_df)
        if filtered_count > 0:
            self.logger.debug(f"Filtered {filtered_count} features below min_samples threshold ({params.min_samples})")
    
    # Step 8: Update consensus_mapping_df to match final consensus_df
    if len(self.consensus_df) > 0 and len(original_mapping_df) > 0:
        valid_consensus_ids = set(self.consensus_df['consensus_uid'].to_list())
        self.consensus_mapping_df = original_mapping_df.filter(
            pl.col('consensus_uid').is_in(list(valid_consensus_ids))
        )
    else:
        self.consensus_mapping_df = pl.DataFrame()
    
    final_feature_count = len(self.consensus_df)
    reduction_pct = ((initial_feature_count - final_feature_count) / initial_feature_count * 100) if initial_feature_count > 0 else 0
    
    self.logger.info(f"Post-processing complete: {initial_feature_count} → {final_feature_count} features ({reduction_pct:.1f}% reduction)")
    
    # Create a new consensus map for compatibility (the processed data is in consensus_df)
    processed_consensus_map = oms.ConsensusMap()
    return processed_consensus_map


def _perform_secondary_clustering(self, rt_tol: float, mz_tol: float) -> list:
    """
    Perform secondary clustering to merge very close features.
    
    Args:
        rt_tol: RT tolerance for secondary clustering
        mz_tol: m/z tolerance for secondary clustering
        
    Returns:
        List of merged consensus feature dictionaries
    """
    if len(self.consensus_df) == 0:
        return []
    
    # Convert consensus_df to list of dictionaries for clustering
    consensus_features = []
    for i, row in enumerate(self.consensus_df.iter_rows(named=True)):
        consensus_features.append(dict(row))
    
    # Use Union-Find for efficient clustering
    class UnionFind:
        def __init__(self, n):
            self.parent = list(range(n))
            self.rank = [0] * n
        
        def find(self, x):
            if self.parent[x] != x:
                self.parent[x] = self.find(self.parent[x])
            return self.parent[x]
        
        def union(self, x, y):
            px, py = self.find(x), self.find(y)
            if px == py:
                return
            if self.rank[px] < self.rank[py]:
                px, py = py, px
            self.parent[py] = px
            if self.rank[px] == self.rank[py]:
                self.rank[px] += 1
    
    n_features = len(consensus_features)
    uf = UnionFind(n_features)
    
    # Find features to merge based on proximity
    merge_count = 0
    for i in range(n_features):
        for j in range(i + 1, n_features):
            feat_i = consensus_features[i]
            feat_j = consensus_features[j]
            
            rt_diff = abs(feat_i['rt'] - feat_j['rt'])
            mz_diff = abs(feat_i['mz'] - feat_j['mz'])
            
            if rt_diff <= rt_tol and mz_diff <= mz_tol:
                uf.union(i, j)
                merge_count += 1
    
    # Group features by their root
    groups_by_root = defaultdict(list)
    for i in range(n_features):
        root = uf.find(i)
        groups_by_root[root].append(consensus_features[i])
    
    # Merge features within each group
    merged_features = []
    for group in groups_by_root.values():
        if len(group) == 1:
            # Single feature - keep as is
            merged_features.append(group[0])
        else:
            # Multiple features - merge them
            merged_feature = _merge_feature_group(group)
            merged_features.append(merged_feature)
    
    self.logger.debug(f"Secondary clustering: {n_features} → {len(merged_features)} features ({n_features - len(merged_features)} merged)")
    return merged_features


def _merge_feature_group(feature_group: list) -> dict:
    """
    Merge a group of similar consensus features into one.
    
    Args:
        feature_group: List of consensus feature dictionaries to merge
        
    Returns:
        Merged consensus feature dictionary
    """
    if not feature_group:
        return {}
    
    if len(feature_group) == 1:
        return feature_group[0]
    
    # Use the feature with highest sample count as base
    base_feature = max(feature_group, key=lambda f: f.get('number_samples', 0))
    merged = base_feature.copy()
    
    # Aggregate numeric statistics
    rt_values = [f['rt'] for f in feature_group if f.get('rt') is not None]
    mz_values = [f['mz'] for f in feature_group if f.get('mz') is not None]
    sample_counts = [f.get('number_samples', 0) for f in feature_group]
    intensities = [f.get('inty_mean', 0) for f in feature_group if f.get('inty_mean') is not None]
    
    # Update merged feature statistics
    if rt_values:
        merged['rt'] = float(np.mean(rt_values))
        merged['rt_min'] = min([f.get('rt_min', f['rt']) for f in feature_group])
        merged['rt_max'] = max([f.get('rt_max', f['rt']) for f in feature_group])
        merged['rt_mean'] = float(np.mean(rt_values))
    
    if mz_values:
        merged['mz'] = float(np.mean(mz_values))
        merged['mz_min'] = min([f.get('mz_min', f['mz']) for f in feature_group])
        merged['mz_max'] = max([f.get('mz_max', f['mz']) for f in feature_group])
        merged['mz_mean'] = float(np.mean(mz_values))
    
    # Use maximum sample count (features might be detected in overlapping but different samples)
    merged['number_samples'] = max(sample_counts)
    
    # Use weighted average intensity (by sample count)
    if intensities and sample_counts:
        total_weight = sum(sample_counts)
        if total_weight > 0:
            weighted_intensity = sum(inty * count for inty, count in zip(intensities, sample_counts)) / total_weight
            merged['inty_mean'] = float(weighted_intensity)
    
    # Aggregate chromatographic quality metrics if available
    coherence_values = [f.get('chrom_coherence_mean', 0) for f in feature_group if f.get('chrom_coherence_mean') is not None]
    prominence_values = [f.get('chrom_prominence_mean', 0) for f in feature_group if f.get('chrom_prominence_mean') is not None]
    
    if coherence_values:
        merged['chrom_coherence_mean'] = float(np.mean(coherence_values))
    if prominence_values:
        merged['chrom_prominence_mean'] = float(np.mean(prominence_values))
    
    # Merge MS2 counts
    ms2_counts = [f.get('number_ms2', 0) for f in feature_group]
    merged['number_ms2'] = sum(ms2_counts)
    
    # Keep the best quality score
    quality_scores = [f.get('quality', 1.0) for f in feature_group if f.get('quality') is not None]
    if quality_scores:
        merged['quality'] = max(quality_scores)
    
    return merged


def _validate_sample_overlap(self, features: list, min_overlap: float) -> list:
    """
    Validate that merged features have sufficient sample overlap.
    
    Args:
        features: List of consensus feature dictionaries
        min_overlap: Minimum sample overlap ratio (0.0-1.0)
        
    Returns:
        List of validated features
    """
    # This is a placeholder for sample overlap validation
    # Implementation would require access to which samples each feature appears in
    # For now, we'll use a simple heuristic based on feature statistics
    
    validated_features = []
    for feature in features:
        # Simple validation based on RT spread and sample count ratio
        rt_spread = feature.get('rt_max', feature['rt']) - feature.get('rt_min', feature['rt'])
        sample_count = feature.get('number_samples', 1)
        
        # Features with very tight RT spread and high sample counts are more reliable
        if rt_spread <= 2.0 or sample_count >= 10:  # More permissive validation
            validated_features.append(feature)
        else:
            # Could implement more sophisticated sample overlap checking here
            validated_features.append(feature)  # Keep for now
    
    return validated_features


def _filter_rt_spread(self, features: list, max_rt_spread: float) -> list:
    """
    Filter out features with excessive RT spread.
    
    Args:
        features: List of consensus feature dictionaries
        max_rt_spread: Maximum allowed RT spread in seconds
        
    Returns:
        List of filtered features
    """
    filtered_features = []
    filtered_count = 0
    
    for feature in features:
        rt_min = feature.get('rt_min', feature['rt'])
        rt_max = feature.get('rt_max', feature['rt'])
        rt_spread = rt_max - rt_min
        
        if rt_spread <= max_rt_spread:
            filtered_features.append(feature)
        else:
            filtered_count += 1
    
    if filtered_count > 0:
        self.logger.debug(f"Filtered {filtered_count} features with excessive RT spread (>{max_rt_spread:.1f}s)")
    
    return filtered_features


def _filter_coherence(self, features: list, min_coherence: float) -> list:
    """
    Filter out features with low chromatographic coherence.
    
    Args:
        features: List of consensus feature dictionaries
        min_coherence: Minimum chromatographic coherence score
        
    Returns:
        List of filtered features
    """
    filtered_features = []
    filtered_count = 0
    
    for feature in features:
        coherence = feature.get('chrom_coherence_mean', 1.0)  # Default to high coherence if missing
        
        if coherence >= min_coherence:
            filtered_features.append(feature)
        else:
            filtered_count += 1
    
    if filtered_count > 0:
        self.logger.debug(f"Filtered {filtered_count} features with low coherence (<{min_coherence})")
    
    return filtered_features


def _merge_kd_nowarp(self, params: merge_defaults) -> oms.ConsensusMap:
    """KD-tree based merge without RT warping"""
    
    # Generate temporary feature maps on-demand from features_df
    temp_feature_maps = _generate_feature_maps_on_demand(self)
    
    consensus_map = oms.ConsensusMap()
    file_descriptions = consensus_map.getColumnHeaders()
    
    for i, feature_map in enumerate(temp_feature_maps):
        file_description = file_descriptions.get(i, oms.ColumnHeader())
        file_description.filename = self.samples_df.row(i, named=True)["sample_name"]
        file_description.size = feature_map.size()
        file_description.unique_id = feature_map.getUniqueId()
        file_descriptions[i] = file_description
    
    consensus_map.setColumnHeaders(file_descriptions)
    
    # Configure KD algorithm with warping disabled for memory efficiency
    grouper = oms.FeatureGroupingAlgorithmKD()
    params_oms = grouper.getParameters()
    
    params_oms.setValue("mz_unit", "Da")
    params_oms.setValue("nr_partitions", params.nr_partitions)
    params_oms.setValue("warp:enabled", "false")  # Disabled for memory efficiency
    params_oms.setValue("link:rt_tol", params.rt_tol)
    params_oms.setValue("link:mz_tol", params.mz_tol)
    params_oms.setValue("link:min_rel_cc_size", params.min_rel_cc_size)
    params_oms.setValue("link:max_pairwise_log_fc", params.max_pairwise_log_fc)
    params_oms.setValue("link:max_nr_conflicts", params.max_nr_conflicts)
    #params_oms.setValue("link:charge_merging", "Any")
    
    grouper.setParameters(params_oms)
    grouper.group(temp_feature_maps, consensus_map)
    
    return consensus_map


def _merge_kd_chunked(self, params: merge_defaults, cached_adducts_df=None, cached_valid_adducts=None) -> oms.ConsensusMap:
    """KD-based chunked merge with proper cross-chunk consensus building and optional parallel processing"""
    
    # Generate temporary feature maps on-demand from features_df
    temp_feature_maps = _generate_feature_maps_on_demand(self)
    
    n_samples = len(temp_feature_maps)
    if n_samples <= params.chunk_size:
        self.logger.info(f"Dataset size ({n_samples}) ≤ chunk_size, using KD merge")
        consensus_map = _merge_kd(self, params)
        # Extract consensus features to populate consensus_df for chunked method consistency
        self._extract_consensus_features(consensus_map, params.min_samples, cached_adducts_df, cached_valid_adducts)
        return consensus_map
    
    # Process in chunks
    chunks = []
    for i in range(0, n_samples, params.chunk_size):
        chunk_end = min(i + params.chunk_size, n_samples)
        chunks.append((i, temp_feature_maps[i:chunk_end]))
    
    self.logger.debug(f"Processing {len(chunks)} chunks of max {params.chunk_size} samples using {params.threads or 'sequential'} thread(s)")
    
    # Process each chunk to create chunk consensus maps
    chunk_consensus_maps = []
    
    if params.threads is None:
        # Sequential processing (original behavior)
        for chunk_idx, (chunk_start_idx, chunk_maps) in enumerate(tqdm(chunks, desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}KD Chunk", disable=self.log_level not in ["TRACE", "DEBUG", "INFO"])):
            chunk_consensus_map = oms.ConsensusMap()
            
            # Set up file descriptions for chunk
            file_descriptions = chunk_consensus_map.getColumnHeaders()
            for j, feature_map in enumerate(chunk_maps):
                file_description = file_descriptions.get(j, oms.ColumnHeader())
                file_description.filename = self.samples_df.row(chunk_start_idx + j, named=True)["sample_name"]
                file_description.size = feature_map.size()
                file_description.unique_id = feature_map.getUniqueId()
                file_descriptions[j] = file_description
            
            chunk_consensus_map.setColumnHeaders(file_descriptions)
            
            # Use KD algorithm for chunk
            grouper = oms.FeatureGroupingAlgorithmKD()
            chunk_params = grouper.getParameters()
            chunk_params.setValue("mz_unit", "Da")
            chunk_params.setValue("nr_partitions", params.nr_partitions)
            chunk_params.setValue("warp:enabled", "true")
            chunk_params.setValue("warp:rt_tol", params.rt_tol)
            chunk_params.setValue("warp:mz_tol", params.mz_tol)
            chunk_params.setValue("link:rt_tol", params.rt_tol)
            chunk_params.setValue("link:mz_tol", params.mz_tol)
            chunk_params.setValue("link:min_rel_cc_size", params.min_rel_cc_size)
            chunk_params.setValue("link:max_pairwise_log_fc", params.max_pairwise_log_fc)
            chunk_params.setValue("link:max_nr_conflicts", params.max_nr_conflicts)
            
            grouper.setParameters(chunk_params)
            grouper.group(chunk_maps, chunk_consensus_map)
            
            chunk_consensus_maps.append((chunk_start_idx, chunk_consensus_map))
    
    else:
        # Parallel processing
        self.logger.info(f"Processing chunks in parallel using {params.threads} processes")
        
        # Prepare chunk data for parallel processing using features_df slices
        chunk_data_list = []
        for chunk_idx, (chunk_start_idx, chunk_maps) in enumerate(chunks):
            # Get the sample UIDs for this chunk
            chunk_sample_uids = []
            chunk_samples_df_rows = []
            for j in range(len(chunk_maps)):
                sample_row = self.samples_df.row(chunk_start_idx + j, named=True)
                chunk_sample_uids.append(sample_row['sample_uid'])
                chunk_samples_df_rows.append(sample_row)
            
            # Create a DataFrame for this chunk's samples
            chunk_samples_df = pl.DataFrame(chunk_samples_df_rows)
            
            # Filter features_df for this chunk's samples and select only necessary columns
            chunk_features_df = self.features_df.filter(
                pl.col('sample_uid').is_in(chunk_sample_uids)
            ).select([
                'sample_uid', 'rt', 'mz', 'inty', 'charge', 'feature_id'
            ])
            
            # Convert DataFrames to serializable format (lists of dicts)
            chunk_features_data = chunk_features_df.to_dicts()
            chunk_samples_data = chunk_samples_df.to_dicts()
            
            chunk_data = {
                'chunk_start_idx': chunk_start_idx,
                'chunk_features_data': chunk_features_data,  # List of dicts instead of DataFrame
                'chunk_samples_data': chunk_samples_data,    # List of dicts instead of DataFrame
                'params': {
                    'nr_partitions': params.nr_partitions,
                    'rt_tol': params.rt_tol,
                    'mz_tol': params.mz_tol,
                    'min_rel_cc_size': params.min_rel_cc_size,
                    'max_pairwise_log_fc': params.max_pairwise_log_fc,
                    'max_nr_conflicts': params.max_nr_conflicts
                }
            }
            chunk_data_list.append(chunk_data)
        
        # Process chunks in parallel - try ProcessPoolExecutor first, fallback to ThreadPoolExecutor on Windows
        try:
            with ProcessPoolExecutor(max_workers=params.threads) as executor:
                # Submit all chunk processing tasks
                future_to_chunk = {executor.submit(_process_kd_chunk_parallel, chunk_data): i 
                                 for i, chunk_data in enumerate(chunk_data_list)}
                
                # Collect results with progress tracking
                completed_chunks = 0
                total_chunks = len(chunk_data_list)
                serialized_chunk_results = []
                
                for future in as_completed(future_to_chunk):
                    chunk_idx = future_to_chunk[future]
                    try:
                        chunk_start_idx, consensus_features = future.result()
                        serialized_chunk_results.append((chunk_start_idx, consensus_features))
                        completed_chunks += 1
                        n_samples_in_chunk = len(chunk_data_list[chunk_idx]['chunk_samples_data'])
                        self.logger.info(f"Completed chunk {completed_chunks}/{total_chunks} (samples {chunk_start_idx + 1}-{chunk_start_idx + n_samples_in_chunk})")
                    except Exception as exc:
                        # Check if this is a BrokenProcessPool exception from Windows multiprocessing issues
                        if isinstance(exc, BrokenProcessPool) or "process pool" in str(exc).lower():
                            # Convert to RuntimeError so outer except block can catch it for fallback
                            raise RuntimeError(f"Windows multiprocessing failure: {exc}")
                        else:
                            self.logger.error(f"Chunk {chunk_idx} generated an exception: {exc}")
                            raise exc
                        
        except (RuntimeError, OSError, BrokenProcessPool) as e:
            # Handle Windows multiprocessing issues - fallback to ThreadPoolExecutor
            if ("freeze_support" in str(e) or "spawn" in str(e) or "bootstrapping" in str(e) or 
                "process pool" in str(e).lower() or "Windows multiprocessing failure" in str(e)):
                self.logger.warning(f"ProcessPoolExecutor failed (likely Windows multiprocessing issue): {e}")
                self.logger.info(f"Falling back to ThreadPoolExecutor with {params.threads} threads")
                
                with ThreadPoolExecutor(max_workers=params.threads) as executor:
                    # Submit all chunk processing tasks
                    future_to_chunk = {executor.submit(_process_kd_chunk_parallel, chunk_data): i 
                                     for i, chunk_data in enumerate(chunk_data_list)}
                    
                    # Collect results with progress tracking
                    completed_chunks = 0
                    total_chunks = len(chunk_data_list)
                    serialized_chunk_results = []
                    
                    for future in as_completed(future_to_chunk):
                        chunk_idx = future_to_chunk[future]
                        try:
                            chunk_start_idx, consensus_features = future.result()
                            serialized_chunk_results.append((chunk_start_idx, consensus_features))
                            completed_chunks += 1
                            n_samples_in_chunk = len(chunk_data_list[chunk_idx]['chunk_samples_data'])
                            self.logger.info(f"Completed chunk {completed_chunks}/{total_chunks} (samples {chunk_start_idx + 1}-{chunk_start_idx + n_samples_in_chunk})")
                        except Exception as exc:
                            self.logger.error(f"Chunk {chunk_idx} generated an exception: {exc}")
                            raise exc
            else:
                # Re-raise other exceptions
                raise
        
        # Store serialized results for _merge_chunk_results to handle directly  
        chunk_consensus_maps = []
        for chunk_start_idx, consensus_features in sorted(serialized_chunk_results):
            # Store serialized data directly for _merge_chunk_results to handle
            chunk_consensus_maps.append((chunk_start_idx, consensus_features))
    
    # Merge chunk results with proper cross-chunk consensus building  
    # _merge_chunk_results now handles both ConsensusMap objects (sequential) and serialized data (parallel)
    _merge_chunk_results(self, chunk_consensus_maps, params, cached_adducts_df, cached_valid_adducts)
    
    # Return a dummy consensus map for compatibility (consensus features are stored in self.consensus_df)
    consensus_map = oms.ConsensusMap()
    return consensus_map


def _merge_qt_chunked(self, params: merge_defaults, cached_adducts_df=None, cached_valid_adducts=None) -> oms.ConsensusMap:
    """QT-based chunked merge with proper cross-chunk consensus building and optional parallel processing"""
    
    # Generate temporary feature maps on-demand from features_df
    temp_feature_maps = _generate_feature_maps_on_demand(self)
    
    n_samples = len(temp_feature_maps)
    if n_samples <= params.chunk_size:
        self.logger.info(f"Dataset size ({n_samples}) ≤ chunk_size, using QT merge")
        consensus_map = _merge_qt(self, params)
        # Extract consensus features to populate consensus_df for chunked method consistency
        self._extract_consensus_features(consensus_map, params.min_samples, cached_adducts_df, cached_valid_adducts)
        return consensus_map
    
    # Process in chunks
    chunks = []
    for i in range(0, n_samples, params.chunk_size):
        chunk_end = min(i + params.chunk_size, n_samples)
        chunks.append((i, temp_feature_maps[i:chunk_end]))
    
    self.logger.debug(f"Processing {len(chunks)} chunks of max {params.chunk_size} samples using {params.threads or 'sequential'} thread(s)")
    
    # Process each chunk to create chunk consensus maps
    chunk_consensus_maps = []
    
    if params.threads is None:
        # Sequential processing (original behavior)
        for chunk_idx, (chunk_start_idx, chunk_maps) in enumerate(tqdm(chunks, desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}QT Chunk", disable=self.log_level not in ["TRACE", "DEBUG", "INFO"])):
            chunk_consensus_map = oms.ConsensusMap()
            
            # Set up file descriptions for chunk
            file_descriptions = chunk_consensus_map.getColumnHeaders()
            for j, feature_map in enumerate(chunk_maps):
                file_description = file_descriptions.get(j, oms.ColumnHeader())
                file_description.filename = self.samples_df.row(chunk_start_idx + j, named=True)["sample_name"]
                file_description.size = feature_map.size()
                file_description.unique_id = feature_map.getUniqueId()
                file_descriptions[j] = file_description
            
            chunk_consensus_map.setColumnHeaders(file_descriptions)
            
            # Use QT algorithm for chunk (main difference from KD chunked)
            grouper = oms.FeatureGroupingAlgorithmQT()
            chunk_params = grouper.getParameters()
            chunk_params.setValue("distance_RT:max_difference", params.rt_tol)
            chunk_params.setValue("distance_MZ:max_difference", params.mz_tol)
            chunk_params.setValue("distance_MZ:unit", "Da")
            chunk_params.setValue("ignore_charge", "true")
            chunk_params.setValue("nr_partitions", params.nr_partitions)
            
            grouper.setParameters(chunk_params)
            grouper.group(chunk_maps, chunk_consensus_map)
            
            chunk_consensus_maps.append((chunk_start_idx, chunk_consensus_map))
    
    else:
        # Parallel processing
        self.logger.info(f"Processing chunks in parallel using {params.threads} processes")
        
        # Prepare chunk data for parallel processing using features_df slices
        chunk_data_list = []
        for chunk_idx, (chunk_start_idx, chunk_maps) in enumerate(chunks):
            # Get the sample UIDs for this chunk
            chunk_sample_uids = []
            chunk_samples_df_rows = []
            for j in range(len(chunk_maps)):
                sample_row = self.samples_df.row(chunk_start_idx + j, named=True)
                chunk_sample_uids.append(sample_row['sample_uid'])
                chunk_samples_df_rows.append(sample_row)
            
            # Create a DataFrame for this chunk's samples
            chunk_samples_df = pl.DataFrame(chunk_samples_df_rows)
            
            # Filter features_df for this chunk's samples and select only necessary columns
            chunk_features_df = self.features_df.filter(
                pl.col('sample_uid').is_in(chunk_sample_uids)
            ).select([
                'sample_uid', 'rt', 'mz', 'inty', 'charge', 'feature_id'
            ])
            
            # Convert DataFrames to serializable format (lists of dicts)
            chunk_features_data = chunk_features_df.to_dicts()
            chunk_samples_data = chunk_samples_df.to_dicts()
            
            chunk_data = {
                'chunk_start_idx': chunk_start_idx,
                'chunk_features_data': chunk_features_data,  # List of dicts instead of DataFrame
                'chunk_samples_data': chunk_samples_data,    # List of dicts instead of DataFrame
                'params': {
                    'nr_partitions': params.nr_partitions,
                    'rt_tol': params.rt_tol,
                    'mz_tol': params.mz_tol,
                }
            }
            chunk_data_list.append(chunk_data)
        
        # Process chunks in parallel - try ProcessPoolExecutor first, fallback to ThreadPoolExecutor on Windows
        executor_class = ProcessPoolExecutor
        executor_name = "processes"
        
        try:
            with ProcessPoolExecutor(max_workers=params.threads) as executor:
                # Submit all chunk processing tasks
                future_to_chunk = {executor.submit(_process_qt_chunk_parallel, chunk_data): i 
                                 for i, chunk_data in enumerate(chunk_data_list)}
                
                # Collect results with progress tracking
                completed_chunks = 0
                total_chunks = len(chunk_data_list)
                serialized_chunk_results = []
                
                for future in as_completed(future_to_chunk):
                    chunk_idx = future_to_chunk[future]
                    try:
                        chunk_start_idx, consensus_features = future.result()
                        serialized_chunk_results.append((chunk_start_idx, consensus_features))
                        completed_chunks += 1
                        n_samples_in_chunk = len(chunk_data_list[chunk_idx]['chunk_samples_data'])
                        self.logger.info(f"Completed chunk {completed_chunks}/{total_chunks} (samples {chunk_start_idx + 1}-{chunk_start_idx + n_samples_in_chunk})")
                    except Exception as exc:
                        # Check if this is a BrokenProcessPool exception from Windows multiprocessing issues
                        if isinstance(exc, BrokenProcessPool) or "process pool" in str(exc).lower():
                            # Convert to RuntimeError so outer except block can catch it for fallback
                            raise RuntimeError(f"Windows multiprocessing failure: {exc}")
                        else:
                            self.logger.error(f"Chunk {chunk_idx} generated an exception: {exc}")
                            raise exc
                        
        except (RuntimeError, OSError, BrokenProcessPool) as e:
            # Handle Windows multiprocessing issues - fallback to ThreadPoolExecutor
            if ("freeze_support" in str(e) or "spawn" in str(e) or "bootstrapping" in str(e) or 
                "process pool" in str(e).lower() or "Windows multiprocessing failure" in str(e)):
                self.logger.warning(f"ProcessPoolExecutor failed (likely Windows multiprocessing issue): {e}")
                self.logger.info(f"Falling back to ThreadPoolExecutor with {params.threads} threads")
                
                with ThreadPoolExecutor(max_workers=params.threads) as executor:
                    # Submit all chunk processing tasks
                    future_to_chunk = {executor.submit(_process_qt_chunk_parallel, chunk_data): i 
                                     for i, chunk_data in enumerate(chunk_data_list)}
                    
                    # Collect results with progress tracking
                    completed_chunks = 0
                    total_chunks = len(chunk_data_list)
                    serialized_chunk_results = []
                    
                    for future in as_completed(future_to_chunk):
                        chunk_idx = future_to_chunk[future]
                        try:
                            chunk_start_idx, consensus_features = future.result()
                            serialized_chunk_results.append((chunk_start_idx, consensus_features))
                            completed_chunks += 1
                            n_samples_in_chunk = len(chunk_data_list[chunk_idx]['chunk_samples_data'])
                            self.logger.info(f"Completed chunk {completed_chunks}/{total_chunks} (samples {chunk_start_idx + 1}-{chunk_start_idx + n_samples_in_chunk})")
                        except Exception as exc:
                            self.logger.error(f"Chunk {chunk_idx} generated an exception: {exc}")
                            raise exc
            else:
                # Re-raise other exceptions
                raise
        
        # Store serialized results for _merge_chunk_results to handle directly  
        chunk_consensus_maps = []
        for chunk_start_idx, consensus_features in sorted(serialized_chunk_results):
            # Store serialized data directly for _merge_chunk_results to handle
            chunk_consensus_maps.append((chunk_start_idx, consensus_features))
    
    # Merge chunk results with proper cross-chunk consensus building  
    # _merge_chunk_results now handles both ConsensusMap objects (sequential) and serialized data (parallel)
    _merge_chunk_results(self, chunk_consensus_maps, params, cached_adducts_df, cached_valid_adducts)
    
    # Return a dummy consensus map for compatibility (consensus features are stored in self.consensus_df)
    consensus_map = oms.ConsensusMap()
    return consensus_map


def _merge_chunk_results(self, chunk_consensus_maps: list, params: merge_defaults, cached_adducts_df=None, cached_valid_adducts=None) -> None:
    """
    Scalable aggregation of chunk consensus maps into final consensus_df.
    
    This function implements cross-chunk consensus building by:
    1. Extracting feature_uids from each chunk consensus map
    2. Aggregating features close in RT/m/z across chunks
    3. Building consensus_df and consensus_mapping_df directly
    """
    
    if len(chunk_consensus_maps) == 1:
        # Single chunk case - just extract using the true global min_samples.
        # No need for permissive threshold because we are not discarding singletons pre-aggregation.
        self._extract_consensus_features(
            chunk_consensus_maps[0][1],
            params.min_samples,
            cached_adducts_df,
            cached_valid_adducts,
        )
        return
    
    # Build feature_uid to feature_data lookup for fast access
    feature_uid_map = {
        row["feature_id"]: row["feature_uid"]
        for row in self.features_df.iter_rows(named=True)
    }
    
    features_lookup = _optimized_feature_lookup(self, self.features_df)
    
    # Extract all consensus features from chunks with their feature_uids
    all_chunk_consensus = []
    consensus_id_counter = 0
    
    for chunk_idx, (chunk_start_idx, chunk_data) in enumerate(chunk_consensus_maps):
        # Handle both ConsensusMap objects (sequential) and serialized data (parallel)
        if isinstance(chunk_data, list):
            # Parallel processing: chunk_data is a list of serialized consensus feature dictionaries
            consensus_features_data = chunk_data
        else:
            # Sequential processing: chunk_data is a ConsensusMap object
            chunk_consensus_map = chunk_data
            consensus_features_data = []
            
            # Extract data from ConsensusMap and convert to serialized format
            for consensus_feature in chunk_consensus_map:
                # Extract feature_uids from this consensus feature
                feature_uids = []
                feature_data_list = []
                sample_uids = []
                
                for feature_handle in consensus_feature.getFeatureList():
                    fuid = str(feature_handle.getUniqueId())
                    if fuid not in feature_uid_map:
                        continue
                        
                    feature_uid = feature_uid_map[fuid]
                    feature_data = features_lookup.get(feature_uid)
                    if feature_data:
                        feature_uids.append(feature_uid)
                        feature_data_list.append(feature_data)
                        sample_uids.append(chunk_start_idx + feature_handle.getMapIndex() + 1)

                if not feature_data_list:
                    # No retrievable feature metadata (possible stale map reference) -> skip
                    continue
                    
                # Convert ConsensusFeature to serialized format
                consensus_feature_data = {
                    'rt': consensus_feature.getRT(),
                    'mz': consensus_feature.getMZ(),
                    'intensity': consensus_feature.getIntensity(),
                    'quality': consensus_feature.getQuality(),
                    'feature_uids': feature_uids,
                    'feature_data_list': feature_data_list,
                    'sample_uids': sample_uids
                }
                consensus_features_data.append(consensus_feature_data)
        
        # Process the consensus features (now all in serialized format)
        for consensus_feature_data in consensus_features_data:
            # ACCEPT ALL consensus features (size >=1) here.
            # Reason: A feature that is globally present in many samples can still
            # appear only once inside a given sample chunk. Early filtering at
            # size>=2 causes irreversible loss and underestimates the final
            # consensus count (observed ~296 vs 950 for KD). We defer filtering
            # strictly to the final global min_samples.
            
            # For parallel processing, feature data is already extracted
            if isinstance(chunk_data, list):
                # Extract feature_uids and data from serialized format for parallel processing
                feature_uids = []
                feature_data_list = []
                sample_uids = []
                
                for handle_data in consensus_feature_data['features']:
                    fuid = str(handle_data['unique_id'])
                    if fuid not in feature_uid_map:
                        continue
                        
                    feature_uid = feature_uid_map[fuid]
                    feature_data = features_lookup.get(feature_uid)
                    if feature_data:
                        feature_uids.append(feature_uid)
                        feature_data_list.append(feature_data)
                        sample_uids.append(chunk_start_idx + handle_data['map_index'] + 1)
                
                if not feature_data_list:
                    continue
                    
                # Get RT/MZ from consensus feature data
                consensus_rt = consensus_feature_data['rt']
                consensus_mz = consensus_feature_data['mz']
                consensus_intensity = consensus_feature_data['intensity']
                consensus_quality = consensus_feature_data['quality']
            else:
                # Sequential processing: data is already extracted above
                feature_uids = consensus_feature_data['feature_uids']
                feature_data_list = consensus_feature_data['feature_data_list'] 
                sample_uids = consensus_feature_data['sample_uids']
                consensus_rt = consensus_feature_data['rt']
                consensus_mz = consensus_feature_data['mz']
                consensus_intensity = consensus_feature_data['intensity']
                consensus_quality = consensus_feature_data['quality']

            if not feature_data_list:
                # No retrievable feature metadata (possible stale map reference) -> skip
                continue
                
            # Derive RT / m/z ranges from underlying features (used for robust cross-chunk stitching)
            rt_vals_local = [fd.get("rt") for fd in feature_data_list if fd.get("rt") is not None]
            mz_vals_local = [fd.get("mz") for fd in feature_data_list if fd.get("mz") is not None]
            if rt_vals_local:
                rt_min_local = min(rt_vals_local)
                rt_max_local = max(rt_vals_local)
            else:
                rt_min_local = rt_max_local = consensus_rt
            if mz_vals_local:
                mz_min_local = min(mz_vals_local)
                mz_max_local = max(mz_vals_local)
            else:
                mz_min_local = mz_max_local = consensus_mz
                
            # Store chunk consensus with feature tracking
            chunk_consensus_data = {
                'consensus_id': consensus_id_counter,
                'chunk_idx': chunk_idx,
                'chunk_start_idx': chunk_start_idx,
                'mz': consensus_mz,
                'rt': consensus_rt,
                'mz_min': mz_min_local,
                'mz_max': mz_max_local,
                'rt_min': rt_min_local,
                'rt_max': rt_max_local,
                'intensity': consensus_intensity,
                'quality': consensus_quality,
                'feature_uids': feature_uids,
                'feature_data_list': feature_data_list,
                'sample_uids': sample_uids,
                'sample_count': len(feature_data_list)
            }
            
            all_chunk_consensus.append(chunk_consensus_data)
            consensus_id_counter += 1

    if not all_chunk_consensus:
        # No valid consensus features found
        self.consensus_df = pl.DataFrame()
        self.consensus_mapping_df = pl.DataFrame()
        return
    
    # Perform cross-chunk clustering using optimized spatial indexing
    def _cluster_chunk_consensus(chunk_consensus_list: list, rt_tol: float, mz_tol: float) -> list:
        """Cluster chunk consensus features using interval overlap (no over-relaxation).

        A union is formed if either centroids are within tolerance OR their RT / m/z
        intervals (expanded by tolerance) overlap, and they originate from different chunks.
        """
        if not chunk_consensus_list:
            return []

        n_features = len(chunk_consensus_list)

        # Spatial bins using strict tolerances (improves candidate reduction without recall loss)
        rt_bin_size = rt_tol if rt_tol > 0 else 1.0
        mz_bin_size = mz_tol if mz_tol > 0 else 0.01
        features_by_bin = defaultdict(list)

        for i, cf in enumerate(chunk_consensus_list):
            rt_bin = int(cf['rt'] / rt_bin_size)
            mz_bin = int(cf['mz'] / mz_bin_size)
            features_by_bin[(rt_bin, mz_bin)].append(i)

        class UF:
            def __init__(self, n):
                self.p = list(range(n))
                self.r = [0]*n
            def find(self, x):
                if self.p[x] != x:
                    self.p[x] = self.find(self.p[x])
                return self.p[x]
            def union(self, a,b):
                pa, pb = self.find(a), self.find(b)
                if pa == pb:
                    return
                if self.r[pa] < self.r[pb]:
                    pa, pb = pb, pa
                self.p[pb] = pa
                if self.r[pa] == self.r[pb]:
                    self.r[pa] += 1

        uf = UF(n_features)
        checked = set()
        for (rtb, mzb), idxs in features_by_bin.items():
            for dr in (-1,0,1):
                for dm in (-1,0,1):
                    neigh = (rtb+dr, mzb+dm)
                    if neigh not in features_by_bin:
                        continue
                    for i in idxs:
                        for j in features_by_bin[neigh]:
                            if i >= j:
                                continue
                            pair = (i,j)
                            if pair in checked:
                                continue
                            checked.add(pair)
                            a = chunk_consensus_list[i]
                            b = chunk_consensus_list[j]
                            if a['chunk_idx'] == b['chunk_idx']:
                                continue
                            
                            # Primary check: centroid distance (strict)
                            centroid_close = (abs(a['rt']-b['rt']) <= rt_tol and abs(a['mz']-b['mz']) <= mz_tol)
                            
                            # Secondary check: interval overlap (more conservative)
                            # Only allow interval overlap if centroids are reasonably close (within 2x tolerance)
                            centroids_reasonable = (abs(a['rt']-b['rt']) <= 2 * rt_tol and abs(a['mz']-b['mz']) <= 2 * mz_tol)
                            if centroids_reasonable:
                                rt_overlap = (a['rt_min'] - rt_tol/2) <= (b['rt_max'] + rt_tol/2) and (b['rt_min'] - rt_tol/2) <= (a['rt_max'] + rt_tol/2)
                                mz_overlap = (a['mz_min'] - mz_tol/2) <= (b['mz_max'] + mz_tol/2) and (b['mz_min'] - mz_tol/2) <= (a['mz_max'] + mz_tol/2)
                            else:
                                rt_overlap = mz_overlap = False
                            
                            if centroid_close or (rt_overlap and mz_overlap):
                                uf.union(i,j)

        groups_by_root = defaultdict(list)
        for i in range(n_features):
            groups_by_root[uf.find(i)].append(chunk_consensus_list[i])
        return list(groups_by_root.values())
    # (Obsolete relaxed + centroid stitching code removed.)

    # --- Stage 1: initial cross-chunk clustering of chunk consensus features ---
    initial_groups = _cluster_chunk_consensus(all_chunk_consensus, params.rt_tol, params.mz_tol)

    # --- Stage 2: centroid refinement (lightweight second pass) ---
    def _refine_groups(groups: list, rt_tol: float, mz_tol: float) -> list:
        """Refine groups by clustering group centroids (single-link) under same tolerances.

        This reconciles borderline splits left after interval-overlap clustering without
        re-introducing broad over-merging. Works on group centroids only (low cost).
        """
        if len(groups) <= 1:
            return groups
        # Build centroid list
        centroids = []  # (idx, rt, mz)
        for gi, g in enumerate(groups):
            if not g:
                continue
            rt_vals = [cf['rt'] for cf in g]
            mz_vals = [cf['mz'] for cf in g]
            if not rt_vals or not mz_vals:
                continue
            centroids.append((gi, float(np.mean(rt_vals)), float(np.mean(mz_vals))))
        if len(centroids) <= 1:
            return groups

        # Spatial binning for centroid clustering
        rt_bin = rt_tol if rt_tol > 0 else 1.0
        mz_bin = mz_tol if mz_tol > 0 else 0.01
        bins = defaultdict(list)
        for idx, rt_c, mz_c in centroids:
            bins[(int(rt_c/rt_bin), int(mz_c/mz_bin))].append((idx, rt_c, mz_c))

        # Union-Find over group indices
        parent = list(range(len(groups)))
        rank = [0]*len(groups)
        def find(x):
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]
        def union(a,b):
            pa, pb = find(a), find(b)
            if pa == pb:
                return
            if rank[pa] < rank[pb]:
                pa, pb = pb, pa
            parent[pb] = pa
            if rank[pa] == rank[pb]:
                rank[pa] += 1

        checked = set()
        for (rb, mb), items in bins.items():
            for dr in (-1,0,1):
                for dm in (-1,0,1):
                    neigh_key = (rb+dr, mb+dm)
                    if neigh_key not in bins:
                        continue
                    for (gi, rt_i, mz_i) in items:
                        for (gj, rt_j, mz_j) in bins[neigh_key]:
                            if gi >= gj:
                                continue
                            pair = (gi, gj)
                            if pair in checked:
                                continue
                            checked.add(pair)
                            if abs(rt_i-rt_j) <= rt_tol and abs(mz_i-mz_j) <= mz_tol:
                                union(gi, gj)

        merged = defaultdict(list)
        for gi, g in enumerate(groups):
            merged[find(gi)].extend(g)
        return list(merged.values())

    refined_groups = _refine_groups(initial_groups, params.rt_tol, params.mz_tol)

    # --- Stage 3: build final consensus feature metadata and mapping ---
    consensus_metadata = []
    consensus_mapping_list = []
    consensus_uid_counter = 0

    for group in refined_groups:
        if not group:
            continue
        
        # Aggregate underlying feature data (deduplicated by feature_uid)
        feature_data_acc = {}
        sample_uids_acc = set()
        rt_values_chunk = []  # use chunk-level centroids for statistic helper
        mz_values_chunk = []
        intensity_values_chunk = []
        quality_values_chunk = []

        for cf in group:
            rt_values_chunk.append(cf['rt'])
            mz_values_chunk.append(cf['mz'])
            intensity_values_chunk.append(cf.get('intensity', 0.0) or 0.0)
            quality_values_chunk.append(cf.get('quality', 1.0) or 1.0)
            
            for fd, samp_uid in zip(cf['feature_data_list'], cf['sample_uids']):
                fid = fd.get('feature_uid') or fd.get('uid') or fd.get('feature_id')
                # feature_uid expected in fd under 'feature_uid'; fallback attempts just in case
                if fid is None:
                    continue
                if fid not in feature_data_acc:
                    feature_data_acc[fid] = fd
                sample_uids_acc.add(samp_uid)
                
        if not feature_data_acc:
            continue

        number_samples = len(sample_uids_acc)
        
        # NOTE: Don't filter by min_samples here - let _finalize_merge handle it
        # This allows proper cross-chunk consensus building before final filtering

        metadata = _calculate_consensus_statistics(
            self,
            consensus_uid_counter,
            list(feature_data_acc.values()),
            rt_values_chunk,
            mz_values_chunk,
            intensity_values_chunk,
            quality_values_chunk,
            number_features=len(feature_data_acc),
            number_samples=number_samples,
            cached_adducts_df=cached_adducts_df,
            cached_valid_adducts=cached_valid_adducts,
        )
        
        # Validate RT spread doesn't exceed tolerance (with some flexibility for chunked merge)
        rt_spread = metadata.get('rt_max', 0) - metadata.get('rt_min', 0)
        max_allowed_spread = params.rt_tol * 2  # Allow 2x tolerance for chunked method
        
        if rt_spread > max_allowed_spread:
            # Skip consensus features with excessive RT spread
            self.logger.debug(f"Skipping consensus feature {consensus_uid_counter} with RT spread {rt_spread:.3f}s > {max_allowed_spread:.3f}s")
            consensus_uid_counter += 1
            continue
            
        consensus_metadata.append(metadata)

        # Build mapping rows (deduplicated)
        for fid, fd in feature_data_acc.items():
            samp_uid = fd.get('sample_uid') or fd.get('sample_id') or fd.get('sample')
            # If absent we attempt to derive from original group sample_uids pairing
            # but most feature_data rows should include sample_uid already.
            if samp_uid is None:
                # fallback: search for cf containing this fid
                for cf in group:
                    for fd2, samp2 in zip(cf['feature_data_list'], cf['sample_uids']):
                        f2id = fd2.get('feature_uid') or fd2.get('uid') or fd2.get('feature_id')
                        if f2id == fid:
                            samp_uid = samp2
                            break
                    if samp_uid is not None:
                        break
            if samp_uid is None:
                continue
            consensus_mapping_list.append({
                'consensus_uid': consensus_uid_counter,
                'sample_uid': samp_uid,
                'feature_uid': fid,
            })

        consensus_uid_counter += 1

    # Assign DataFrames
    self.consensus_df = pl.DataFrame(consensus_metadata, strict=False)
    self.consensus_mapping_df = pl.DataFrame(consensus_mapping_list, strict=False)

    # Ensure mapping only contains features from retained consensus_df
    if len(self.consensus_df) > 0:
        valid_consensus_ids = set(self.consensus_df['consensus_uid'].to_list())
        self.consensus_mapping_df = self.consensus_mapping_df.filter(
            pl.col('consensus_uid').is_in(list(valid_consensus_ids))
        )
    else:
        self.consensus_mapping_df = pl.DataFrame()

    # Attach empty consensus_map placeholder for downstream compatibility
    self.consensus_map = oms.ConsensusMap()
    return


def _calculate_consensus_statistics(study_obj, consensus_uid: int, feature_data_list: list, 
                                  rt_values: list, mz_values: list, 
                                  intensity_values: list, quality_values: list,
                                  number_features: int = None, number_samples: int = None,
                                  cached_adducts_df=None, cached_valid_adducts=None) -> dict:
    """
    Calculate comprehensive statistics for a consensus feature from aggregated feature data.
    
    Args:
        consensus_uid: Unique ID for this consensus feature
        feature_data_list: List of individual feature dictionaries
        rt_values: RT values from chunk consensus features
        mz_values: m/z values from chunk consensus features  
        intensity_values: Intensity values from chunk consensus features
        quality_values: Quality values from chunk consensus features
        
    Returns:
        Dictionary with consensus feature metadata
    """
    if not feature_data_list:
        return {}
    
    # Convert feature data to numpy arrays for vectorized computation
    rt_feat_values = np.array([fd.get("rt", 0) for fd in feature_data_list if fd.get("rt") is not None])
    mz_feat_values = np.array([fd.get("mz", 0) for fd in feature_data_list if fd.get("mz") is not None])
    rt_start_values = np.array([fd.get("rt_start", 0) for fd in feature_data_list if fd.get("rt_start") is not None])
    rt_end_values = np.array([fd.get("rt_end", 0) for fd in feature_data_list if fd.get("rt_end") is not None])
    rt_delta_values = np.array([fd.get("rt_delta", 0) for fd in feature_data_list if fd.get("rt_delta") is not None])
    mz_start_values = np.array([fd.get("mz_start", 0) for fd in feature_data_list if fd.get("mz_start") is not None])
    mz_end_values = np.array([fd.get("mz_end", 0) for fd in feature_data_list if fd.get("mz_end") is not None])
    inty_values = np.array([fd.get("inty", 0) for fd in feature_data_list if fd.get("inty") is not None])
    coherence_values = np.array([fd.get("chrom_coherence", 0) for fd in feature_data_list if fd.get("chrom_coherence") is not None])
    prominence_values = np.array([fd.get("chrom_prominence", 0) for fd in feature_data_list if fd.get("chrom_prominence") is not None])
    prominence_scaled_values = np.array([fd.get("chrom_height_scaled", 0) for fd in feature_data_list if fd.get("chrom_height_scaled") is not None])
    height_scaled_values = np.array([fd.get("chrom_prominence_scaled", 0) for fd in feature_data_list if fd.get("chrom_prominence_scaled") is not None])
    iso_values = np.array([fd.get("iso", 0) for fd in feature_data_list if fd.get("iso") is not None])
    charge_values = np.array([fd.get("charge", 0) for fd in feature_data_list if fd.get("charge") is not None])
    
    # Process adducts with cached validation
    all_adducts = []
    valid_adducts = cached_valid_adducts if cached_valid_adducts is not None else set()
    valid_adducts.add("?")  # Always allow '?' adducts
    
    for fd in feature_data_list:
        adduct = fd.get("adduct")
        if adduct is not None:
            # Only include adducts that are valid (from cached study adducts or contain '?')
            if adduct in valid_adducts or "?" in adduct:
                all_adducts.append(adduct)
    
    # Calculate adduct consensus
    adduct_values = []
    adduct_top = None
    adduct_charge_top = None
    adduct_mass_neutral_top = None
    adduct_mass_shift_top = None
    
    if all_adducts:
        adduct_counts = {adduct: all_adducts.count(adduct) for adduct in set(all_adducts)}
        total_count = sum(adduct_counts.values())
        for adduct, count in adduct_counts.items():
            percentage = (count / total_count) * 100 if total_count > 0 else 0
            adduct_values.append([str(adduct), int(count), float(round(percentage, 2))])
        
        adduct_values.sort(key=lambda x: x[1], reverse=True)
        
        if adduct_values:
            adduct_top = adduct_values[0][0]
            # Try to get charge and mass shift from cached study adducts
            adduct_found = False
            if cached_adducts_df is not None and not cached_adducts_df.is_empty():
                matching_adduct = cached_adducts_df.filter(
                    pl.col("name") == adduct_top,
                )
                if not matching_adduct.is_empty():
                    adduct_row = matching_adduct.row(0, named=True)
                    adduct_charge_top = adduct_row["charge"]
                    adduct_mass_shift_top = adduct_row["mass_shift"]
                    adduct_found = True
            
            if not adduct_found:
                # Set default charge and mass shift for top adduct
                adduct_charge_top = 1
                adduct_mass_shift_top = 1.007825
    else:
        # Default adduct based on study polarity
        study_polarity = getattr(study_obj, "polarity", "positive")
        if study_polarity in ["negative", "neg"]:
            adduct_top = "[M-?]1-"
            adduct_charge_top = -1
            adduct_mass_shift_top = -1.007825
        else:
            adduct_top = "[M+?]1+"
            adduct_charge_top = 1
            adduct_mass_shift_top = 1.007825
        
        adduct_values = [[adduct_top, 1, 100.0]]
    
    # Calculate neutral mass
    consensus_mz = round(float(np.mean(mz_values)), 4) if len(mz_values) > 0 else 0.0
    if adduct_charge_top and adduct_mass_shift_top is not None:
        adduct_mass_neutral_top = consensus_mz * abs(adduct_charge_top) - adduct_mass_shift_top
    
    # Calculate MS2 count
    ms2_count = 0
    for fd in feature_data_list:
        ms2_scans = fd.get("ms2_scans")
        if ms2_scans is not None:
            ms2_count += len(ms2_scans)
    
    # Build consensus metadata
    return {
        "consensus_uid": int(consensus_uid),
        "consensus_id": str(consensus_uid),  # Use simple string ID
        "quality": round(float(np.mean(quality_values)), 3) if len(quality_values) > 0 else 1.0,
        "number_samples": number_samples if number_samples is not None else len(feature_data_list),
        "rt": round(float(np.mean(rt_values)), 4) if len(rt_values) > 0 else 0.0,
        "mz": consensus_mz,
        "rt_min": round(float(np.min(rt_feat_values)), 3) if len(rt_feat_values) > 0 else 0.0,
        "rt_max": round(float(np.max(rt_feat_values)), 3) if len(rt_feat_values) > 0 else 0.0,
        "rt_mean": round(float(np.mean(rt_feat_values)), 3) if len(rt_feat_values) > 0 else 0.0,
        "rt_start_mean": round(float(np.mean(rt_start_values)), 3) if len(rt_start_values) > 0 else 0.0,
        "rt_end_mean": round(float(np.mean(rt_end_values)), 3) if len(rt_end_values) > 0 else 0.0,
        "rt_delta_mean": round(float(np.mean(rt_delta_values)), 3) if len(rt_delta_values) > 0 else 0.0,
        "mz_min": round(float(np.min(mz_feat_values)), 4) if len(mz_feat_values) > 0 else 0.0,
        "mz_max": round(float(np.max(mz_feat_values)), 4) if len(mz_feat_values) > 0 else 0.0,
        "mz_mean": round(float(np.mean(mz_feat_values)), 4) if len(mz_feat_values) > 0 else 0.0,
        "mz_start_mean": round(float(np.mean(mz_start_values)), 4) if len(mz_start_values) > 0 else 0.0,
        "mz_end_mean": round(float(np.mean(mz_end_values)), 4) if len(mz_end_values) > 0 else 0.0,
        "inty_mean": round(float(np.mean(inty_values)), 0) if len(inty_values) > 0 else 0.0,
        "bl": -1.0,
        "chrom_coherence_mean": round(float(np.mean(coherence_values)), 3) if len(coherence_values) > 0 else 0.0,
        "chrom_prominence_mean": round(float(np.mean(prominence_values)), 0) if len(prominence_values) > 0 else 0.0,
        "chrom_prominence_scaled_mean": round(float(np.mean(prominence_scaled_values)), 3) if len(prominence_scaled_values) > 0 else 0.0,
        "chrom_height_scaled_mean": round(float(np.mean(height_scaled_values)), 3) if len(height_scaled_values) > 0 else 0.0,
        "iso_mean": round(float(np.mean(iso_values)), 2) if len(iso_values) > 0 else 0.0,
        "charge_mean": round(float(np.mean(charge_values)), 2) if len(charge_values) > 0 else 0.0,
        "number_ms2": int(ms2_count),
        "adducts": adduct_values,
        "adduct_top": adduct_top,
        "adduct_charge_top": adduct_charge_top,
        "adduct_mass_neutral_top": round(adduct_mass_neutral_top, 6) if adduct_mass_neutral_top is not None else None,
        "adduct_mass_shift_top": round(adduct_mass_shift_top, 6) if adduct_mass_shift_top is not None else None,
        "id_top_name": None,
        "id_top_class": None,
        "id_top_adduct": None,
        "id_top_score": None,
    }


def _cluster_consensus_features(features: list, rt_tol: float, mz_tol: float) -> list:
    """
    Cluster consensus features from different chunks based on RT and m/z similarity.
    
    Args:
        features: List of feature dictionaries with 'mz', 'rt', 'id' keys
        rt_tol: RT tolerance in seconds
        mz_tol: m/z tolerance in Da
        
    Returns:
        List of groups, where each group is a list of feature dictionaries
    """
    if not features:
        return []
    
    # Use Union-Find for efficient clustering
    class UnionFind:
        def __init__(self, n):
            self.parent = list(range(n))
            self.rank = [0] * n
        
        def find(self, x):
            if self.parent[x] != x:
                self.parent[x] = self.find(self.parent[x])
            return self.parent[x]
        
        def union(self, x, y):
            px, py = self.find(x), self.find(y)
            if px == py:
                return
            if self.rank[px] < self.rank[py]:
                px, py = py, px
            self.parent[py] = px
            if self.rank[px] == self.rank[py]:
                self.rank[px] += 1
    
    n_features = len(features)
    uf = UnionFind(n_features)
    
    # Build distance matrix and cluster features within tolerance
    for i in range(n_features):
        for j in range(i + 1, n_features):
            feat_i = features[i]
            feat_j = features[j]
            
            # Skip if features are from the same chunk (they're already processed)
            if feat_i['chunk_idx'] == feat_j['chunk_idx']:
                continue
            
            mz_diff = abs(feat_i['mz'] - feat_j['mz'])
            rt_diff = abs(feat_i['rt'] - feat_j['rt'])
            
            # Cluster if within tolerance
            if mz_diff <= mz_tol and rt_diff <= rt_tol:
                uf.union(i, j)
    
    # Extract groups
    groups_by_root = {}
    for i in range(n_features):
        root = uf.find(i)
        if root not in groups_by_root:
            groups_by_root[root] = []
        groups_by_root[root].append(features[i])
    
    return list(groups_by_root.values())


def _reset_consensus_data(self):
    """Reset consensus-related DataFrames at the start of merge."""
    self.consensus_df = pl.DataFrame()
    self.consensus_ms2 = pl.DataFrame()
    self.consensus_mapping_df = pl.DataFrame()


def _extract_consensus_features(self, consensus_map, min_samples, cached_adducts_df=None, cached_valid_adducts=None):
    """Extract consensus features and build metadata."""
    # create a dict to map uid to feature_uid using self.features_df
    feature_uid_map = {
        row["feature_id"]: row["feature_uid"]
        for row in self.features_df.iter_rows(named=True)
    }
    imax = consensus_map.size()

    self.logger.debug(f"Found {imax} feature groups by clustering.")

    # Pre-build fast lookup tables for features_df data using optimized approach
    features_lookup = _optimized_feature_lookup(self, self.features_df)

    # create a list to store the consensus mapping
    consensus_mapping = []
    metadata_list = []

    tqdm_disable = self.log_level not in ["TRACE", "DEBUG"]

    for i, feature in enumerate(
        tqdm(
            consensus_map,
            total=imax,
            disable=tqdm_disable,
            desc=f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} | INFO     | {self.log_label}Extract metadata",
        ),
    ):
        # get all features in the feature map with the same unique id as the consensus feature
        features_list = feature.getFeatureList()
        uids = []
        feature_data_list = []

        for _j, f in enumerate(features_list):
            fuid = str(f.getUniqueId())
            if fuid not in feature_uid_map:
                # this is a feature that was removed but is still in the feature maps
                continue
            fuid = feature_uid_map[fuid]
            consensus_mapping.append(
                {
                    "consensus_uid": i,
                    "sample_uid": f.getMapIndex() + 1,
                    "feature_uid": fuid,
                },
            )
            uids.append(fuid)

            # Get feature data from lookup instead of DataFrame filtering
            feature_data = features_lookup.get(fuid)
            if feature_data:
                feature_data_list.append(feature_data)

        if not feature_data_list:
            # Skip this consensus feature if no valid features found
            continue

        # Compute statistics using vectorized operations on collected data
        # Convert to numpy arrays for faster computation
        rt_values = np.array(
            [fd.get("rt", 0) for fd in feature_data_list if fd.get("rt") is not None],
        )
        mz_values = np.array(
            [fd.get("mz", 0) for fd in feature_data_list if fd.get("mz") is not None],
        )
        rt_start_values = np.array(
            [
                fd.get("rt_start", 0)
                for fd in feature_data_list
                if fd.get("rt_start") is not None
            ],
        )
        rt_end_values = np.array(
            [
                fd.get("rt_end", 0)
                for fd in feature_data_list
                if fd.get("rt_end") is not None
            ],
        )
        rt_delta_values = np.array(
            [
                fd.get("rt_delta", 0)
                for fd in feature_data_list
                if fd.get("rt_delta") is not None
            ],
        )
        mz_start_values = np.array(
            [
                fd.get("mz_start", 0)
                for fd in feature_data_list
                if fd.get("mz_start") is not None
            ],
        )
        mz_end_values = np.array(
            [
                fd.get("mz_end", 0)
                for fd in feature_data_list
                if fd.get("mz_end") is not None
            ],
        )
        inty_values = np.array(
            [
                fd.get("inty", 0)
                for fd in feature_data_list
                if fd.get("inty") is not None
            ],
        )
        coherence_values = np.array(
            [
                fd.get("chrom_coherence", 0)
                for fd in feature_data_list
                if fd.get("chrom_coherence") is not None
            ],
        )
        prominence_values = np.array(
            [
                fd.get("chrom_prominence", 0)
                for fd in feature_data_list
                if fd.get("chrom_prominence") is not None
            ],
        )
        prominence_scaled_values = np.array(
            [
                fd.get("chrom_height_scaled", 0)
                for fd in feature_data_list
                if fd.get("chrom_height_scaled") is not None
            ],
        )
        height_scaled_values = np.array(
            [
                fd.get("chrom_prominence_scaled", 0)
                for fd in feature_data_list
                if fd.get("chrom_prominence_scaled") is not None
            ],
        )
        iso_values = np.array(
            [fd.get("iso", 0) for fd in feature_data_list if fd.get("iso") is not None],
        )
        charge_values = np.array(
            [
                fd.get("charge", 0)
                for fd in feature_data_list
                if fd.get("charge") is not None
            ],
        )

        # adduct_values
        # Collect all adducts from feature_data_list to create consensus adduct information
        # Only consider adducts that are in study._get_adducts() plus items with '?'
        all_adducts = []
        adduct_masses = {}

        # Get valid adducts from cached result (avoid repeated _get_adducts() calls)
        valid_adducts = cached_valid_adducts if cached_valid_adducts is not None else set()
        valid_adducts.add("?")  # Always allow '?' adducts

        for fd in feature_data_list:
            # Get individual adduct and mass from each feature data (fd)
            adduct = fd.get("adduct")
            adduct_mass = fd.get("adduct_mass")

            if adduct is not None:
                # Only include adducts that are valid (from study._get_adducts() or contain '?')
                if adduct in valid_adducts or "?" in adduct:
                    all_adducts.append(adduct)
                    if adduct_mass is not None:
                        adduct_masses[adduct] = adduct_mass

        # Calculate adduct_values for the consensus feature
        adduct_values = []
        if all_adducts:
            adduct_counts = {
                adduct: all_adducts.count(adduct) for adduct in set(all_adducts)
            }
            total_count = sum(adduct_counts.values())
            for adduct, count in adduct_counts.items():
                percentage = (count / total_count) * 100 if total_count > 0 else 0
                # Store as list with [name, num, %] format for the adducts column
                adduct_values.append(
                    [
                        str(adduct),
                        int(count),
                        float(round(percentage, 2)),
                    ],
                )

        # Sort adduct_values by count in descending order
        adduct_values.sort(key=lambda x: x[1], reverse=True)  # Sort by count (index 1)
        # Store adduct_values for use in metadata
        consensus_adduct_values = adduct_values

        # Extract top adduct information for new columns
        adduct_top = None
        adduct_charge_top = None
        adduct_mass_neutral_top = None
        adduct_mass_shift_top = None

        if consensus_adduct_values:
            top_adduct_name = consensus_adduct_values[0][0]  # Get top adduct name
            adduct_top = top_adduct_name

            # Parse adduct information to extract charge and mass shift
            # Handle "?" as "H" and parse common adduct formats
            if top_adduct_name == "?" or top_adduct_name == "[M+?]+":
                adduct_charge_top = 1
                adduct_mass_shift_top = 1.007825  # H mass
            elif top_adduct_name == "[M+?]-":
                adduct_charge_top = -1
                adduct_mass_shift_top = -1.007825  # -H mass
            else:
                # Try to get charge and mass shift from cached study adducts
                adduct_found = False
                if cached_adducts_df is not None and not cached_adducts_df.is_empty():
                    # Look for exact match in study adducts
                    matching_adduct = cached_adducts_df.filter(
                        pl.col("name") == top_adduct_name,
                    )
                    if not matching_adduct.is_empty():
                        adduct_row = matching_adduct.row(0, named=True)
                        adduct_charge_top = adduct_row["charge"]
                        adduct_mass_shift_top = adduct_row["mass_shift"]
                        adduct_found = True

                if not adduct_found:
                    # Fallback to regex parsing
                    import re

                    # Pattern for adducts like [M+H]+, [M-H]-, [M+Na]+, etc.
                    pattern = r"\[M([+\-])([A-Za-z0-9]+)\]([0-9]*)([+\-])"
                    match = re.match(pattern, top_adduct_name)

                    if match:
                        sign = match.group(1)
                        element = match.group(2)
                        multiplier_str = match.group(3)
                        charge_sign = match.group(4)

                        multiplier = int(multiplier_str) if multiplier_str else 1
                        charge = multiplier if charge_sign == "+" else -multiplier
                        adduct_charge_top = charge

                        # Calculate mass shift based on element
                        element_masses = {
                            "H": 1.007825,
                            "Na": 22.989769,
                            "K": 38.963708,
                            "NH4": 18.033823,
                            "Li": 7.016930,
                            "Cl": 34.969401,
                            "Br": 78.918885,
                            "HCOO": 44.998201,
                            "CH3COO": 59.013851,
                            "H2O": 18.010565,
                        }

                        base_mass = element_masses.get(
                            element,
                            1.007825,
                        )  # Default to H if unknown
                        mass_shift = (
                            base_mass * multiplier
                            if sign == "+"
                            else -base_mass * multiplier
                        )
                        adduct_mass_shift_top = mass_shift
                    else:
                        # Default fallback
                        adduct_charge_top = 1
                        adduct_mass_shift_top = 1.007825
        else:
            # No valid adducts found - assign default based on study polarity
            study_polarity = getattr(self, "polarity", "positive")
            if study_polarity in ["negative", "neg"]:
                # Negative mode default
                adduct_top = "[M-?]1-"
                adduct_charge_top = -1
                adduct_mass_shift_top = -1.007825  # -H mass (loss of proton)
            else:
                # Positive mode default (includes 'positive', 'pos', or any other value)
                adduct_top = "[M+?]1+"
                adduct_charge_top = 1
                adduct_mass_shift_top = 1.007825  # H mass (gain of proton)

            # Create a single default adduct entry in the adducts list for consistency
            consensus_adduct_values = [[adduct_top, 1, 100.0]]

        # Calculate neutral mass from consensus mz (for both cases)
        consensus_mz = (
            round(float(np.mean(mz_values)), 4) if len(mz_values) > 0 else 0.0
        )
        if adduct_charge_top and adduct_mass_shift_top is not None:
            adduct_mass_neutral_top = (
                consensus_mz * abs(adduct_charge_top) - adduct_mass_shift_top
            )

        # Calculate number of MS2 spectra
        ms2_count = 0
        for fd in feature_data_list:
            ms2_scans = fd.get("ms2_scans")
            if ms2_scans is not None:
                ms2_count += len(ms2_scans)

        metadata_list.append(
            {
                "consensus_uid": int(i),  # "consensus_id": i,
                "consensus_id": str(feature.getUniqueId()),
                "quality": round(float(feature.getQuality()), 3),
                "number_samples": len(feature_data_list),
                # "number_ext": int(len(features_list)),
                "rt": round(float(np.mean(rt_values)), 4)
                if len(rt_values) > 0
                else 0.0,
                "mz": round(float(np.mean(mz_values)), 4)
                if len(mz_values) > 0
                else 0.0,
                "rt_min": round(float(np.min(rt_values)), 3)
                if len(rt_values) > 0
                else 0.0,
                "rt_max": round(float(np.max(rt_values)), 3)
                if len(rt_values) > 0
                else 0.0,
                "rt_mean": round(float(np.mean(rt_values)), 3)
                if len(rt_values) > 0
                else 0.0,
                "rt_start_mean": round(float(np.mean(rt_start_values)), 3)
                if len(rt_start_values) > 0
                else 0.0,
                "rt_end_mean": round(float(np.mean(rt_end_values)), 3)
                if len(rt_end_values) > 0
                else 0.0,
                "rt_delta_mean": round(float(np.ptp(rt_delta_values)), 3)
                if len(rt_delta_values) > 0
                else 0.0,
                "mz_min": round(float(np.min(mz_values)), 4)
                if len(mz_values) > 0
                else 0.0,
                "mz_max": round(float(np.max(mz_values)), 4)
                if len(mz_values) > 0
                else 0.0,
                "mz_mean": round(float(np.mean(mz_values)), 4)
                if len(mz_values) > 0
                else 0.0,
                "mz_start_mean": round(float(np.mean(mz_start_values)), 4)
                if len(mz_start_values) > 0
                else 0.0,
                "mz_end_mean": round(float(np.mean(mz_end_values)), 4)
                if len(mz_end_values) > 0
                else 0.0,
                "inty_mean": round(float(np.mean(inty_values)), 0)
                if len(inty_values) > 0
                else 0.0,
                "bl": -1.0,
                "chrom_coherence_mean": round(float(np.mean(coherence_values)), 3)
                if len(coherence_values) > 0
                else 0.0,
                "chrom_prominence_mean": round(float(np.mean(prominence_values)), 0)
                if len(prominence_values) > 0
                else 0.0,
                "chrom_prominence_scaled_mean": round(
                    float(np.mean(prominence_scaled_values)),
                    3,
                )
                if len(prominence_scaled_values) > 0
                else 0.0,
                "chrom_height_scaled_mean": round(
                    float(np.mean(height_scaled_values)),
                    3,
                )
                if len(height_scaled_values) > 0
                else 0.0,
                "iso_mean": round(float(np.mean(iso_values)), 2)
                if len(iso_values) > 0
                else 0.0,
                "charge_mean": round(float(np.mean(charge_values)), 2)
                if len(charge_values) > 0
                else 0.0,
                "number_ms2": int(ms2_count),
                "adducts": consensus_adduct_values
                if consensus_adduct_values
                else [],  # Ensure it's always a list
                # New columns for top-ranked adduct information
                "adduct_top": adduct_top,
                "adduct_charge_top": adduct_charge_top,
                "adduct_mass_neutral_top": round(adduct_mass_neutral_top, 6)
                if adduct_mass_neutral_top is not None
                else None,
                "adduct_mass_shift_top": round(adduct_mass_shift_top, 6)
                if adduct_mass_shift_top is not None
                else None,
                # New columns for top-scoring identification results
                "id_top_name": None,
                "id_top_class": None,
                "id_top_adduct": None,
                "id_top_score": None,
            },
        )

    consensus_mapping_df = pl.DataFrame(consensus_mapping)
    # remove all rows in consensus_mapping_df where consensus_id is not in self.featured_df['uid']
    l1 = len(consensus_mapping_df)
    consensus_mapping_df = consensus_mapping_df.filter(
        pl.col("feature_uid").is_in(self.features_df["feature_uid"].to_list()),
    )
    self.logger.debug(
        f"Filtered {l1 - len(consensus_mapping_df)} orphan features from maps.",
    )
    self.consensus_mapping_df = consensus_mapping_df
    self.consensus_df = pl.DataFrame(metadata_list, strict=False)

    if min_samples is None:
        min_samples = 1
    if min_samples < 1:
        min_samples = int(min_samples * len(self.samples_df))

    # Validate that min_samples doesn't exceed the number of samples
    if min_samples > len(self.samples_df):
        self.logger.warning(
            f"min_samples ({min_samples}) exceeds the number of samples ({len(self.samples_df)}). "
            f"Setting min_samples to {len(self.samples_df)}.",
        )
        min_samples = len(self.samples_df)

    # filter out consensus features with less than min_samples features
    l1 = len(self.consensus_df)
    self.consensus_df = self.consensus_df.filter(
        pl.col("number_samples") >= min_samples,
    )
    self.logger.debug(
        f"Filtered {l1 - len(self.consensus_df)} consensus features with less than {min_samples} samples.",
    )
    # filter out consensus mapping with less than min_samples features
    self.consensus_mapping_df = self.consensus_mapping_df.filter(
        pl.col("consensus_uid").is_in(self.consensus_df["consensus_uid"].to_list()),
    )

    self.consensus_map = consensus_map


def _perform_adduct_grouping(self, rt_tol, mz_tol):
    """Perform adduct grouping on consensus features."""
    import polars as pl
    
    # Add adduct grouping and adduct_of assignment
    if len(self.consensus_df) > 0:
        # Get relevant columns for grouping
        consensus_data = []
        for row in self.consensus_df.iter_rows(named=True):
            consensus_data.append(
                {
                    "consensus_uid": row["consensus_uid"],
                    "rt": row["rt"],
                    "adduct_mass_neutral_top": row.get("adduct_mass_neutral_top"),
                    "adduct_top": row.get("adduct_top"),
                    "inty_mean": row.get("inty_mean", 0),
                },
            )

        # Use optimized adduct grouping
        adduct_group_list, adduct_of_list = _optimized_adduct_grouping(
            self, consensus_data, rt_tol, mz_tol
        )

        # Add the new columns to consensus_df
        self.consensus_df = self.consensus_df.with_columns(
            [
                pl.Series("adduct_group", adduct_group_list, dtype=pl.Int64),
                pl.Series("adduct_of", adduct_of_list, dtype=pl.Int64),
            ],
        )


def _count_tight_clusters(self, mz_tol: float = 0.04, rt_tol: float = 0.3) -> int:
    """
    Count consensus features grouped in tight clusters.
    
    Args:
        mz_tol: m/z tolerance in Daltons for cluster detection
        rt_tol: RT tolerance in seconds for cluster detection
        
    Returns:
        Number of tight clusters found
    """
    if len(self.consensus_df) < 2:
        return 0
    
    # Extract consensus feature data
    consensus_data = []
    for row in self.consensus_df.iter_rows(named=True):
        consensus_data.append({
            'consensus_uid': row['consensus_uid'],
            'mz': row['mz'], 
            'rt': row['rt']
        })
    
    # Build spatial index using bins
    rt_bin_size = rt_tol / 2
    mz_bin_size = mz_tol / 2
    
    bins = defaultdict(list)
    for feature in consensus_data:
        rt_bin = int(feature['rt'] / rt_bin_size)
        mz_bin = int(feature['mz'] / mz_bin_size)
        bins[(rt_bin, mz_bin)].append(feature)
    
    processed_features = set()
    tight_clusters_count = 0
    
    for bin_key, bin_features in bins.items():
        if len(bin_features) < 2:
            continue
            
        # Check neighboring bins for additional features
        rt_bin, mz_bin = bin_key
        all_nearby_features = list(bin_features)
        
        # Check 8 neighboring bins
        for drt in [-1, 0, 1]:
            for dmz in [-1, 0, 1]:
                if drt == 0 and dmz == 0:
                    continue
                neighbor_key = (rt_bin + drt, mz_bin + dmz)
                if neighbor_key in bins:
                    all_nearby_features.extend(bins[neighbor_key])
        
        # Filter to features within actual tolerances and not yet processed
        valid_cluster_features = []
        for feature in all_nearby_features:
            if feature['consensus_uid'] in processed_features:
                continue
                
            # Check if this feature is within tolerances of any bin feature
            for bin_feature in bin_features:
                rt_diff = abs(feature['rt'] - bin_feature['rt'])
                mz_diff = abs(feature['mz'] - bin_feature['mz'])
                
                if rt_diff <= rt_tol and mz_diff <= mz_tol:
                    valid_cluster_features.append(feature)
                    break
        
        # Count as tight cluster if we have multiple features
        if len(valid_cluster_features) >= 2:
            tight_clusters_count += 1
            for feature in valid_cluster_features:
                processed_features.add(feature['consensus_uid'])
    
    return tight_clusters_count


def _consensus_cleanup(self, rt_tol, mz_tol):
    """
    Consensus cleanup to merge over-segmented consensus features and remove isotopic features.
    
    This function:
    1. Identifies and merges consensus features that are likely over-segmented 
       (too many features in very tight m/z and RT windows)
    2. Performs deisotoping to remove +1 and +2 isotopic features
    """
    if len(self.consensus_df) == 0:
        return
    
    initial_count = len(self.consensus_df)
    
    # Only perform enhanced post-clustering if there are many features
    if initial_count < 50:
        return
    
    self.logger.debug(f"Enhanced post-clustering: processing {initial_count} consensus features")
    
    # Find tight clusters using spatial binning
    consensus_data = []
    for row in self.consensus_df.iter_rows(named=True):
        consensus_data.append({
            'consensus_uid': row['consensus_uid'],
            'mz': row['mz'], 
            'rt': row['rt'],
            'inty_mean': row.get('inty_mean', 0),
            'number_samples': row.get('number_samples', 0)
        })
    
    # Parameters for tight clustering detection - more lenient for effective merging
    tight_rt_tol = min(0.5, rt_tol * 0.5)  # More lenient RT tolerance (max 0.5s)
    tight_mz_tol = min(0.05, max(0.03, mz_tol * 2.0))  # More lenient m/z tolerance (min 30 mDa, max 50 mDa)
    
    # Build spatial index using smaller RT and m/z bins for better coverage
    rt_bin_size = tight_rt_tol / 4  # Smaller bins to ensure nearby features are captured
    mz_bin_size = tight_mz_tol / 4  # Smaller bins to ensure nearby features are captured
    
    bins = defaultdict(list)
    for feature in consensus_data:
        rt_bin = int(feature['rt'] / rt_bin_size)
        mz_bin = int(feature['mz'] / mz_bin_size)
        bins[(rt_bin, mz_bin)].append(feature)
    
    # Find clusters that need merging
    merge_groups = []
    processed_uids = set()
    
    for bin_key, bin_features in bins.items():
        # Check current bin and extended neighboring bins for complete cluster
        rt_bin, mz_bin = bin_key
        cluster_features = list(bin_features)
        
        # Check a larger neighborhood (±2 bins) to ensure we capture all nearby features
        for dr in [-2, -1, 0, 1, 2]:
            for dm in [-2, -1, 0, 1, 2]:
                if dr == 0 and dm == 0:
                    continue
                neighbor_key = (rt_bin + dr, mz_bin + dm)
                if neighbor_key in bins:
                    cluster_features.extend(bins[neighbor_key])
        
        # Remove duplicates
        seen_uids = set()
        unique_features = []
        for f in cluster_features:
            if f['consensus_uid'] not in seen_uids:
                unique_features.append(f)
                seen_uids.add(f['consensus_uid'])
        
        # Only proceed if we have at least 2 features after including neighbors
        if len(unique_features) < 2:
            continue
            
        # Calculate cluster bounds
        mzs = [f['mz'] for f in unique_features]
        rts = [f['rt'] for f in unique_features]
        
        mz_spread = max(mzs) - min(mzs)
        rt_spread = max(rts) - min(rts)
        
        # Only merge if features are tightly clustered
        if mz_spread <= tight_mz_tol and rt_spread <= tight_rt_tol:
            # Filter out features that were already processed
            uids_in_cluster = {f['consensus_uid'] for f in unique_features}
            unprocessed_features = [f for f in unique_features if f['consensus_uid'] not in processed_uids]
            
            # Only proceed if we have at least 2 unprocessed features that still form a tight cluster
            if len(unprocessed_features) >= 2:
                # Recalculate bounds for unprocessed features only
                unprocessed_mzs = [f['mz'] for f in unprocessed_features]
                unprocessed_rts = [f['rt'] for f in unprocessed_features]
                
                unprocessed_mz_spread = max(unprocessed_mzs) - min(unprocessed_mzs)
                unprocessed_rt_spread = max(unprocessed_rts) - min(unprocessed_rts)
                
                # Check if unprocessed features still meet tight clustering criteria
                if unprocessed_mz_spread <= tight_mz_tol and unprocessed_rt_spread <= tight_rt_tol:
                    merge_groups.append(unprocessed_features)
                    processed_uids.update({f['consensus_uid'] for f in unprocessed_features})
    
    if not merge_groups:
        return
    
    self.logger.debug(f"Found {len(merge_groups)} over-segmented clusters to merge")
    
    # Merge clusters by keeping the most representative feature
    uids_to_remove = set()
    
    for group in merge_groups:
        if len(group) < 2:
            continue
            
        # Find the most representative feature (highest intensity and sample count)
        best_feature = max(group, key=lambda x: (x['number_samples'], x['inty_mean']))
        
        # Mark other features for removal
        for f in group:
            if f['consensus_uid'] != best_feature['consensus_uid']:
                uids_to_remove.add(f['consensus_uid'])
    
    if uids_to_remove:
        # Remove merged features from consensus_df
        self.consensus_df = self.consensus_df.filter(
            ~pl.col('consensus_uid').is_in(list(uids_to_remove))
        )
        
        # Also update consensus_mapping_df if it exists
        if hasattr(self, 'consensus_mapping_df') and not self.consensus_mapping_df.is_empty():
            self.consensus_mapping_df = self.consensus_mapping_df.filter(
                ~pl.col('consensus_uid').is_in(list(uids_to_remove))
            )
        
        final_count = len(self.consensus_df)
        reduction = initial_count - final_count
        reduction_pct = (reduction / initial_count) * 100
        
        if reduction > 0:
            self.logger.debug(f"Enhanced post-clustering: {initial_count} → {final_count} features ({reduction_pct:.1f}% reduction)")
    
    # Step 2: Deisotoping - Remove +1 and +2 isotopic consensus features
    pre_deisotoping_count = len(self.consensus_df)
    isotope_uids_to_remove = set()
    
    # Use strict tolerances for deisotoping (same as declustering)
    deisotope_rt_tol = min(0.3, rt_tol * 0.3)  # Strict RT tolerance for isotope detection
    deisotope_mz_tol = min(0.01, mz_tol * 0.5)  # Strict m/z tolerance for isotope detection
    
    # Get current consensus data for isotope detection
    current_consensus_data = []
    for row in self.consensus_df.iter_rows(named=True):
        current_consensus_data.append({
            'consensus_uid': row['consensus_uid'],
            'mz': row['mz'], 
            'rt': row['rt'],
            'number_samples': row.get('number_samples', 0)
        })
    
    # Sort by m/z for efficient searching
    current_consensus_data.sort(key=lambda x: x['mz'])
    n_current = len(current_consensus_data)
    
    for i in range(n_current):
        feature_i = current_consensus_data[i]
        
        # Skip if already marked for removal
        if feature_i['consensus_uid'] in isotope_uids_to_remove:
            continue
            
        # Look for potential +1 and +2 isotopes (higher m/z)
        for j in range(i + 1, n_current):
            feature_j = current_consensus_data[j]
            
            # Skip if already marked for removal
            if feature_j['consensus_uid'] in isotope_uids_to_remove:
                continue
                
            mz_diff = feature_j['mz'] - feature_i['mz']
            
            # Break if m/z difference is too large (features are sorted by m/z)
            if mz_diff > 2.1:  # Beyond +2 isotope range
                break
                
            rt_diff = abs(feature_j['rt'] - feature_i['rt'])
            
            # Check for +1 isotope (C13 mass difference ≈ 1.003354 Da)
            if (0.995 <= mz_diff <= 1.011) and rt_diff <= deisotope_rt_tol:
                # Potential +1 isotope - should have fewer samples than main feature
                if feature_j['number_samples'] < feature_i['number_samples']:
                    isotope_uids_to_remove.add(feature_j['consensus_uid'])
                    continue
            
            # Check for +2 isotope (2 * C13 mass difference ≈ 2.006708 Da) 
            if (1.995 <= mz_diff <= 2.018) and rt_diff <= deisotope_rt_tol:
                # Potential +2 isotope - should have fewer samples than main feature
                if feature_j['number_samples'] < feature_i['number_samples']:
                    isotope_uids_to_remove.add(feature_j['consensus_uid'])
                    continue
    
    # Remove isotopic features
    if isotope_uids_to_remove:
        self.consensus_df = self.consensus_df.filter(
            ~pl.col('consensus_uid').is_in(list(isotope_uids_to_remove))
        )
        
        # Also update consensus_mapping_df if it exists
        if hasattr(self, 'consensus_mapping_df') and not self.consensus_mapping_df.is_empty():
            self.consensus_mapping_df = self.consensus_mapping_df.filter(
                ~pl.col('consensus_uid').is_in(list(isotope_uids_to_remove))
            )
        
        post_deisotoping_count = len(self.consensus_df)
        isotope_reduction = pre_deisotoping_count - post_deisotoping_count
        
        if isotope_reduction > 0:
            self.logger.debug(f"Deisotoping: {pre_deisotoping_count} → {post_deisotoping_count} features ({isotope_reduction} isotopic features removed)")
    
    # Final summary
    final_count = len(self.consensus_df)
    total_reduction = initial_count - final_count
    if total_reduction > 0:
        total_reduction_pct = (total_reduction / initial_count) * 100
        self.logger.debug(f"Consensus cleanup complete: {initial_count} → {final_count} features ({total_reduction_pct:.1f}% total reduction)")


def _identify_adduct_by_mass_shift(self, rt_tol, cached_adducts_df=None):
    """
    Identify coeluting consensus features by characteristic mass shifts between adducts
    and update their adduct information accordingly.
    
    This function:
    1. Generates a catalogue of mass shifts between adducts using _get_adducts()
    2. Searches for pairs of consensus features with same RT (within strict RT tolerance)
       and matching m/z shifts (±0.005 Da)
    3. Updates adduct_* columns based on identified relationships
    
    Args:
        rt_tol: RT tolerance in seconds (strict tolerance for coelution detection)
        cached_adducts_df: Pre-computed adducts DataFrame for performance
    """
    import polars as pl
    import numpy as np
    from collections import defaultdict
    
    # Check if consensus_df exists and has features
    if len(self.consensus_df) == 0:
        self.logger.debug("No consensus features for adduct identification by mass shift")
        return
    
    self.logger.info(f"Identifying coeluting adducts by mass shifts in {len(self.consensus_df)} consensus features...")
    
    # Get adducts DataFrame if not provided
    if cached_adducts_df is None or cached_adducts_df.is_empty():
        try:
            # Use lower min_probability for better adduct coverage in mass shift identification
            cached_adducts_df = self._get_adducts(min_probability=0.01)
        except Exception as e:
            self.logger.warning(f"Could not retrieve adducts for mass shift identification: {e}")
            return
    
    if cached_adducts_df.is_empty():
        self.logger.debug("No adducts available for mass shift identification")
        return
    
    # Build catalogue of mass shifts between adducts
    mass_shift_catalog = {}
    adduct_info = {}
    
    # Extract adduct information
    adducts_data = cached_adducts_df.select(["name", "charge", "mass_shift"]).to_dicts()
    
    for adduct in adducts_data:
        name = adduct["name"]
        charge = adduct["charge"] 
        mass_shift = adduct["mass_shift"]
        
        adduct_info[name] = {
            "charge": charge,
            "mass_shift": mass_shift
        }
    
    # Generate pairwise mass differences for catalog
    for adduct1 in adducts_data:
        for adduct2 in adducts_data:
            if adduct1["name"] == adduct2["name"]:
                continue
                
            name1, charge1, ms1 = adduct1["name"], adduct1["charge"], adduct1["mass_shift"]
            name2, charge2, ms2 = adduct2["name"], adduct2["charge"], adduct2["mass_shift"]
            
            # Only consider shifts between adducts that have the same charge (same ionization state)
            if charge1 != charge2:
                continue
            
            # Calculate expected m/z difference
            if charge1 != 0 and charge2 != 0:
                mz_diff = (ms1 - ms2) / abs(charge1)
            else:
                continue  # Skip neutral adducts for this analysis
            
            # Store the mass shift relationship
            shift_key = round(mz_diff, 4)  # Round to 4 decimal places for matching
            if shift_key not in mass_shift_catalog:
                mass_shift_catalog[shift_key] = []
            mass_shift_catalog[shift_key].append({
                "from_adduct": name1,
                "to_adduct": name2, 
                "mz_shift": mz_diff,
                "from_charge": charge1,
                "to_charge": charge2
            })
    
    self.logger.debug(f"Generated mass shift catalog with {len(mass_shift_catalog)} unique shifts")
    
    # Get consensus features data
    consensus_data = []
    for i, row in enumerate(self.consensus_df.iter_rows(named=True)):
        consensus_data.append({
            "index": i,
            "consensus_uid": row["consensus_uid"],
            "rt": row["rt"], 
            "mz": row["mz"],
            "adduct_top": row.get("adduct_top", "[M+?]1+"),
            "adduct_charge_top": row.get("adduct_charge_top", 1),
            "adduct_mass_neutral_top": row.get("adduct_mass_neutral_top"),
            "adduct_mass_shift_top": row.get("adduct_mass_shift_top"),
            "inty_mean": row.get("inty_mean", 0)
        })
    
    # Sort by RT for efficient searching
    consensus_data.sort(key=lambda x: x["rt"])
    n_features = len(consensus_data)
    
    # Track updates to make
    adduct_updates = {}  # consensus_uid -> new_adduct_info
    
    # Strict RT tolerance for coelution (convert to minutes)
    rt_tol_strict = rt_tol * 0.5  # Use half the merge tolerance for strict coelution
    mz_tol_shift = 0.005  # ±5 mDa tolerance for mass shift matching
    
    # Search for coeluting pairs with characteristic mass shifts
    updated_count = 0
    
    for i in range(n_features):
        feature1 = consensus_data[i]
        rt1 = feature1["rt"]
        mz1 = feature1["mz"]
        adduct1 = feature1["adduct_top"]
        
        # Skip if already has identified adduct (not [M+?]) - DISABLED to allow re-evaluation
        # if adduct1 and "?" not in adduct1:
        #     continue
            
        # Search for coeluting features within strict RT tolerance
        for j in range(i + 1, n_features):
            feature2 = consensus_data[j]
            rt2 = feature2["rt"]
            
            # Break if RT difference exceeds tolerance (sorted by RT)
            if abs(rt2 - rt1) > rt_tol_strict:
                break
                
            mz2 = feature2["mz"]
            adduct2 = feature2["adduct_top"]
            
            # Skip if already has identified adduct (not [M+?]) - DISABLED to allow re-evaluation
            # if adduct2 and "?" not in adduct2:
            #     continue
            
            # Calculate observed m/z difference
            mz_diff = mz2 - mz1
            shift_key = round(mz_diff, 4)
            
            # Check if this mass shift matches any known adduct relationships
            for catalog_shift, relationships in mass_shift_catalog.items():
                if abs(shift_key - catalog_shift) <= mz_tol_shift:
                    # Found a matching mass shift!
                    
                    # Choose the best relationship based on common adducts
                    best_rel = None
                    best_score = 0
                    
                    for rel in relationships:
                        # Prioritize common adducts ([M+H]+, [M+Na]+, [M+NH4]+)
                        score = 0
                        if "H]" in rel["from_adduct"]: score += 3
                        if "Na]" in rel["from_adduct"]: score += 2  
                        if "NH4]" in rel["from_adduct"]: score += 2
                        if "H]" in rel["to_adduct"]: score += 3
                        if "Na]" in rel["to_adduct"]: score += 2
                        if "NH4]" in rel["to_adduct"]: score += 2
                        
                        if score > best_score:
                            best_score = score
                            best_rel = rel
                    
                    if best_rel:
                        # Determine which feature gets which adduct based on intensity
                        inty1 = feature1["inty_mean"]
                        inty2 = feature2["inty_mean"] 
                        
                        # Assign higher intensity to [M+H]+ if possible
                        if "H]" in best_rel["from_adduct"] and inty1 >= inty2:
                            # Feature 1 = from_adduct, Feature 2 = to_adduct
                            from_feature = feature1
                            to_feature = feature2
                            from_adduct_name = best_rel["from_adduct"]
                            to_adduct_name = best_rel["to_adduct"]
                        elif "H]" in best_rel["to_adduct"] and inty2 >= inty1:
                            # Feature 2 = to_adduct (reverse), Feature 1 = from_adduct
                            from_feature = feature2
                            to_feature = feature1
                            from_adduct_name = best_rel["to_adduct"]
                            to_adduct_name = best_rel["from_adduct"]
                        else:
                            # Assignment based on mass shift direction
                            # catalog_shift = (ms1 - ms2) / abs(charge1) where ms1 = from_adduct mass shift, ms2 = to_adduct mass shift
                            # If catalog_shift > 0: from_adduct has higher m/z than to_adduct
                            # If catalog_shift < 0: from_adduct has lower m/z than to_adduct
                            # observed mz_diff = mz2 - mz1
                            # If mz_diff matches catalog_shift: feature2 should get to_adduct, feature1 should get from_adduct
                            # If mz_diff matches -catalog_shift: assignments are swapped
                            
                            if abs(mz_diff - catalog_shift) <= abs(mz_diff - (-catalog_shift)):
                                # mz_diff matches catalog_shift direction
                                from_feature = feature1
                                to_feature = feature2
                                from_adduct_name = best_rel["from_adduct"]
                                to_adduct_name = best_rel["to_adduct"]
                            else:
                                # mz_diff matches reverse direction of catalog_shift
                                from_feature = feature2
                                to_feature = feature1
                                from_adduct_name = best_rel["to_adduct"] 
                                to_adduct_name = best_rel["from_adduct"]
                        
                        # Get adduct details from catalog
                        from_adduct_info = adduct_info.get(from_adduct_name, {})
                        to_adduct_info = adduct_info.get(to_adduct_name, {})
                        
                        # Calculate neutral masses
                        from_charge = from_adduct_info.get("charge", 1)
                        to_charge = to_adduct_info.get("charge", 1)
                        from_mass_shift = from_adduct_info.get("mass_shift", 1.007825)
                        to_mass_shift = to_adduct_info.get("mass_shift", 1.007825)
                        
                        from_neutral_mass = from_feature["mz"] * abs(from_charge) - from_mass_shift
                        to_neutral_mass = to_feature["mz"] * abs(to_charge) - to_mass_shift
                        
                        # Store updates
                        adduct_updates[from_feature["consensus_uid"]] = {
                            "adduct_top": from_adduct_name,
                            "adduct_charge_top": from_charge,
                            "adduct_mass_neutral_top": from_neutral_mass,
                            "adduct_mass_shift_top": from_mass_shift
                        }
                        
                        adduct_updates[to_feature["consensus_uid"]] = {
                            "adduct_top": to_adduct_name,
                            "adduct_charge_top": to_charge,
                            "adduct_mass_neutral_top": to_neutral_mass,
                            "adduct_mass_shift_top": to_mass_shift
                        }
                        
                        updated_count += 2
                        self.logger.debug(
                            f"Identified adduct pair: {from_adduct_name} (m/z {from_feature['mz']:.4f}) "
                            f"<-> {to_adduct_name} (m/z {to_feature['mz']:.4f}), "
                            f"RT {rt1:.2f}s, Δm/z {mz_diff:.4f}"
                        )
                        break  # Found match, no need to check other relationships
    
    # Apply updates to consensus_df
    if adduct_updates:
        # Prepare update data
        consensus_uids = self.consensus_df["consensus_uid"].to_list()
        
        new_adduct_top = []
        new_adduct_charge_top = []
        new_adduct_mass_neutral_top = []
        new_adduct_mass_shift_top = []
        
        for uid in consensus_uids:
            if uid in adduct_updates:
                update = adduct_updates[uid]
                new_adduct_top.append(update["adduct_top"])
                new_adduct_charge_top.append(update["adduct_charge_top"])
                new_adduct_mass_neutral_top.append(update["adduct_mass_neutral_top"])
                new_adduct_mass_shift_top.append(update["adduct_mass_shift_top"])
            else:
                # Keep existing values
                row_idx = consensus_uids.index(uid)
                row = self.consensus_df.row(row_idx, named=True)
                new_adduct_top.append(row.get("adduct_top"))
                new_adduct_charge_top.append(row.get("adduct_charge_top"))
                new_adduct_mass_neutral_top.append(row.get("adduct_mass_neutral_top"))
                new_adduct_mass_shift_top.append(row.get("adduct_mass_shift_top"))
        
        # Update the DataFrame
        self.consensus_df = self.consensus_df.with_columns([
            pl.Series("adduct_top", new_adduct_top),
            pl.Series("adduct_charge_top", new_adduct_charge_top), 
            pl.Series("adduct_mass_neutral_top", new_adduct_mass_neutral_top),
            pl.Series("adduct_mass_shift_top", new_adduct_mass_shift_top)
        ])
        
        self.logger.info(f"Updated adduct assignments for {updated_count} consensus features based on mass shifts")
    else:
        self.logger.debug("No consensus features updated based on mass shift analysis")


def _finalize_merge(self, link_ms2, min_samples):
    """Complete the merge process with final calculations and cleanup."""
    import polars as pl
    
    # Check if consensus_df is empty or missing required columns
    if len(self.consensus_df) == 0 or "number_samples" not in self.consensus_df.columns:
        self.logger.debug("No consensus features found or consensus_df is empty. Skipping finalize merge.")
        return
    
    # Validate min_samples parameter
    if min_samples is None:
        min_samples = 1
    if min_samples < 1:
        min_samples = int(min_samples * len(self.samples_df))

    # Validate that min_samples doesn't exceed the number of samples
    if min_samples > len(self.samples_df):
        self.logger.warning(
            f"min_samples ({min_samples}) exceeds the number of samples ({len(self.samples_df)}). "
            f"Setting min_samples to {len(self.samples_df)}.",
        )
        min_samples = len(self.samples_df)

    # Filter out consensus features with less than min_samples features
    l1 = len(self.consensus_df)
    self.consensus_df = self.consensus_df.filter(
        pl.col("number_samples") >= min_samples,
    )
    self.logger.debug(
        f"Filtered {l1 - len(self.consensus_df)} consensus features with less than {min_samples} samples.",
    )
    
    # Filter out consensus mapping with less than min_samples features
    self.consensus_mapping_df = self.consensus_mapping_df.filter(
        pl.col("consensus_uid").is_in(self.consensus_df["consensus_uid"].to_list()),
    )

    # Calculate the completeness of the consensus map
    # Log completion with tight cluster metrics
    if len(self.consensus_df) > 0 and len(self.samples_df) > 0:
        c = (
            len(self.consensus_mapping_df)
            / len(self.consensus_df)
            / len(self.samples_df)
        )
        
        # Count tight clusters with specified thresholds
        tight_clusters = _count_tight_clusters(self,mz_tol=0.04, rt_tol=0.3)
        
        self.logger.info(
            f"Merging completed. Consensus features: {len(self.consensus_df)}. "
            f"Completeness: {c:.2f}. Tight clusters left: {tight_clusters}.",
        )
    else:
        self.logger.warning(
            f"Merging completed with empty result. Consensus features: {len(self.consensus_df)}. "
            f"This may be due to min_samples ({min_samples}) being too high for the available data.",
        )
    
    if link_ms2:
        self.find_ms2()


def _optimized_feature_lookup(study_obj, features_df):
    """
    Optimized feature lookup creation using Polars operations.
    """
    study_obj.logger.debug("Creating optimized feature lookup...")
    start_time = time.time()
    
    # Use Polars select for faster conversion
    feature_columns = [
        "feature_uid", "rt", "mz", "rt_start", "rt_end", "rt_delta", 
        "mz_start", "mz_end", "inty", "chrom_coherence", "chrom_prominence", 
        "chrom_prominence_scaled", "chrom_height_scaled", "iso", "charge", 
        "ms2_scans", "adduct", "adduct_mass"
    ]
    
    # Filter to only existing columns
    existing_columns = [col for col in feature_columns if col in features_df.columns]
    
    # Convert to dictionary more efficiently
    selected_df = features_df.select(existing_columns)
    
    features_lookup = {}
    for row in selected_df.iter_rows(named=True):
        feature_uid = row["feature_uid"]
        # Keep feature_uid in the dictionary for chunked merge compatibility
        features_lookup[feature_uid] = {k: v for k, v in row.items()}
    
    lookup_time = time.time() - start_time
    if len(features_lookup) > 50000:
        study_obj.logger.debug(f"Feature lookup created in {lookup_time:.2f}s for {len(features_lookup)} features")
    return features_lookup


def _optimized_adduct_grouping(study_obj, consensus_data, rt_tol, mz_tol):
    """
    Optimized O(n log n) adduct grouping using spatial indexing.
    
    Args:
        study_obj: Study object with logger
        consensus_data: List of consensus feature dictionaries
        rt_tol: RT tolerance in minutes
        mz_tol: m/z tolerance in Da
        
    Returns:
        Tuple of (adduct_group_list, adduct_of_list)
    """
    if not consensus_data:
        return [], []
    
    n_features = len(consensus_data)
    if n_features > 10000:
        study_obj.logger.info(f"Adduct grouping for {n_features} consensus features...")
    else:
        study_obj.logger.debug(f"Adduct grouping for {n_features} consensus features...")
    
    # Build spatial index using RT and neutral mass as coordinates
    features_by_mass = defaultdict(list)
    mass_bin_size = mz_tol * 2  # 2x tolerance for conservative binning
    
    valid_features = []
    for feature in consensus_data:
        consensus_uid = feature["consensus_uid"]
        rt = feature["rt"]
        neutral_mass = feature.get("adduct_mass_neutral_top")
        intensity = feature.get("inty_mean", 0)
        adduct = feature.get("adduct_top", "")
        
        if neutral_mass is not None:
            mass_bin = int(neutral_mass / mass_bin_size)
            features_by_mass[mass_bin].append((consensus_uid, rt, neutral_mass, intensity, adduct))
            valid_features.append((consensus_uid, rt, neutral_mass, intensity, adduct, mass_bin))
    
    # Union-Find for efficient grouping
    class UnionFind:
        def __init__(self, n):
            self.parent = list(range(n))
            self.rank = [0] * n
        
        def find(self, x):
            if self.parent[x] != x:
                self.parent[x] = self.find(self.parent[x])
            return self.parent[x]
        
        def union(self, x, y):
            px, py = self.find(x), self.find(y)
            if px == py:
                return
            if self.rank[px] < self.rank[py]:
                px, py = py, px
            self.parent[py] = px
            if self.rank[px] == self.rank[py]:
                self.rank[px] += 1
    
    uid_to_idx = {feature[0]: i for i, feature in enumerate(valid_features)}
    uf = UnionFind(len(valid_features))
    
    # Find groups using spatial index
    checked_pairs = set()
    for i, (uid1, rt1, mass1, inty1, adduct1, bin1) in enumerate(valid_features):
        for bin_offset in [-1, 0, 1]:
            check_bin = bin1 + bin_offset
            if check_bin not in features_by_mass:
                continue
                
            for uid2, rt2, mass2, inty2, adduct2 in features_by_mass[check_bin]:
                if uid1 >= uid2:
                    continue
                
                pair = (min(uid1, uid2), max(uid1, uid2))
                if pair in checked_pairs:
                    continue
                checked_pairs.add(pair)
                
                mass_diff = abs(mass1 - mass2)
                rt_diff = abs(rt1 - rt2) / 60.0  # Convert to minutes
                
                if mass_diff <= mz_tol and rt_diff <= rt_tol:
                    j = uid_to_idx[uid2]
                    uf.union(i, j)
    
    # Extract groups
    groups_by_root = defaultdict(list)
    for i, (uid, rt, mass, inty, adduct, _) in enumerate(valid_features):
        root = uf.find(i)
        groups_by_root[root].append((uid, rt, mass, inty, adduct))
    
    groups = {}
    group_id = 1
    assigned_groups = {}
    
    for group_members in groups_by_root.values():
        member_uids = [uid for uid, _, _, _, _ in group_members]
        
        for uid in member_uids:
            assigned_groups[uid] = group_id
        groups[group_id] = member_uids
        group_id += 1
    
    # Handle features without neutral mass
    for feature in consensus_data:
        uid = feature["consensus_uid"]
        if uid not in assigned_groups:
            assigned_groups[uid] = group_id
            groups[group_id] = [uid]
            group_id += 1
    
    # Determine adduct_of for each group
    group_adduct_of = {}
    for grp_id, member_uids in groups.items():
        best_uid = None
        best_priority = -1
        best_intensity = 0
        
        for uid in member_uids:
            feature_data = next((f for f in consensus_data if f["consensus_uid"] == uid), None)
            if not feature_data:
                continue
                
            adduct = feature_data.get("adduct_top", "")
            intensity = feature_data.get("inty_mean", 0)
            
            priority = 0
            if adduct and ("[M+H]" in adduct or adduct == "H" or adduct == "?"):
                priority = 3
            elif adduct and "[M-H]" in adduct:
                priority = 2
            elif adduct and "M" in adduct:
                priority = 1
            
            if priority > best_priority or (priority == best_priority and intensity > best_intensity):
                best_uid = uid
                best_priority = priority
                best_intensity = intensity
        
        group_adduct_of[grp_id] = best_uid if best_uid else member_uids[0]
    
    # Build final lists in same order as consensus_data
    adduct_group_list = []
    adduct_of_list = []
    
    for feature in consensus_data:
        uid = feature["consensus_uid"]
        group = assigned_groups.get(uid, 0)
        adduct_of = group_adduct_of.get(group, uid)
        
        adduct_group_list.append(group)
        adduct_of_list.append(adduct_of)
    
    if n_features > 10000:
        study_obj.logger.info("Adduct grouping completed.")
    else:
        study_obj.logger.debug("Adduct grouping completed.")

    return adduct_group_list, adduct_of_list
