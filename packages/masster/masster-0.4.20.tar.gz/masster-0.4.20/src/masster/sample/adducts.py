"""
Adduct Detection and Processing Module

This module contains all adduct-related functionality for mass spectrometry data processing.
It provides comprehensive adduct detection, combination generation, and relationship analysis
with improved algorithms based on OpenMS MetaboliteFeatureDeconvolution but with fixes
for RT filtering and mass tolerance issues.

Functions:
- find_adducts: Main function for adduct detection and processing (standalone)
- _get_adducts: Generate comprehensive adduct specifications
- Helper functions for mass calculations, probability scoring, and combination generation
"""

import numpy as np
import polars as pl
from typing import List, Dict
from itertools import combinations

# Import defaults class for external use
from masster.sample.defaults.find_adducts_def import find_adducts_defaults


def _get_adducts(self, adducts_list: list = None, **kwargs):
    """
    Generate comprehensive adduct specifications including multiply charged species and combinations.

    This method consolidates all adduct generation logic into a single optimized helper
    that produces a polars DataFrame with all possible adduct combinations, properly
    formatted names like [M+H]1+ or [M-H2O+2H]2+, and respecting charge constraints.

    Uses parameters from find_adducts_defaults() by default, which can be overridden
    by providing keyword arguments.

    Parameters
    ----------
    adducts_list : List[str], optional
        List of base adduct specifications in format "+H:1:0.6" or "-H:-1:0.8"
        If None, uses self.find_adducts_defaults().get_openms_adducts()
    **kwargs : dict
        Override parameters from find_adducts_defaults, including:
        - charge_min: Minimum charge to consider (default from find_adducts_defaults)
        - charge_max: Maximum charge to consider (default from find_adducts_defaults)
        - max_combinations: Maximum number of adduct components to combine (default 4)

    Returns
    -------
    pl.DataFrame
        DataFrame with columns:
        - name: Formatted adduct name like "[M+H]1+" or "[M-H2O+2H]2+"
        - charge: Total charge of the adduct
        - mass_shift: Total mass shift in Da
        - probability: Combined probability score
        - complexity: Number of adduct components (1-4)
        - components: List of component adduct dictionaries
    """
    # Get default parameters from find_adducts_defaults
    defaults = self.find_adducts_defaults()

    # Use provided parameters or defaults
    if adducts_list is None:
        adducts_list = defaults.get_openms_adducts()

    charge_min = kwargs.get("charge_min", defaults.charge_min)
    charge_max = kwargs.get("charge_max", defaults.charge_max)
    max_combinations = kwargs.get("max_combinations", 4)

    # Parse base adduct specifications
    base_specs = []

    for adduct_str in adducts_list:
        if not isinstance(adduct_str, str) or ":" not in adduct_str:
            continue

        try:
            parts = adduct_str.split(":")
            if len(parts) != 3:
                continue

            formula_part = parts[0]
            charge = int(parts[1])
            probability = float(parts[2])

            # Calculate mass shift from formula
            mass_shift = _calculate_formula_mass_shift(formula_part)

            base_specs.append(
                {
                    "formula": formula_part,
                    "charge": charge,
                    "mass_shift": mass_shift,
                    "probability": probability,
                    "raw_string": adduct_str,
                },
            )

        except (ValueError, IndexError):
            continue

    # Generate all valid combinations
    combinations_list = []

    # Separate specs by charge type
    positive_specs = [spec for spec in base_specs if spec["charge"] > 0]
    negative_specs = [spec for spec in base_specs if spec["charge"] < 0]
    neutral_specs = [spec for spec in base_specs if spec["charge"] == 0]

    # 1. Single adducts
    for spec in base_specs:
        if charge_min <= spec["charge"] <= charge_max:
            formatted_name = _format_adduct_name([spec])
            combinations_list.append(
                {
                    "components": [spec],
                    "formatted_name": formatted_name,
                    "total_mass_shift": spec["mass_shift"],
                    "total_charge": spec["charge"],
                    "combined_probability": spec["probability"],
                    "complexity": 1,
                },
            )

    # 2. Generate multiply charged versions (2H+, 3H+, etc.)
    for spec in positive_specs + negative_specs:
        base_charge = spec["charge"]
        for multiplier in range(2, min(max_combinations + 1, 5)):
            total_charge = base_charge * multiplier
            if charge_min <= total_charge <= charge_max:
                components = [spec] * multiplier
                formatted_name = _format_adduct_name(components)

                combinations_list.append(
                    {
                        "components": components,
                        "formatted_name": formatted_name,
                        "total_mass_shift": spec["mass_shift"] * multiplier,
                        "total_charge": total_charge,
                        "combined_probability": spec["probability"] ** multiplier,
                        "complexity": multiplier,
                    },
                )

    # 3. Mixed combinations (2-component)
    if max_combinations >= 2:
        # Positive + Neutral
        for pos_spec in positive_specs:
            for neut_spec in neutral_specs:
                total_charge = pos_spec["charge"] + neut_spec["charge"]
                if charge_min <= total_charge <= charge_max:
                    components = [pos_spec, neut_spec]
                    formatted_name = _format_adduct_name(components)
                    combinations_list.append(
                        {
                            "components": components,
                            "formatted_name": formatted_name,
                            "total_mass_shift": pos_spec["mass_shift"]
                            + neut_spec["mass_shift"],
                            "total_charge": total_charge,
                            "combined_probability": pos_spec["probability"]
                            * neut_spec["probability"],
                            "complexity": 2,
                        },
                    )

        # Different charged species
        for combo in combinations(positive_specs, 2):
            if combo[0]["formula"] != combo[1]["formula"]:
                total_charge = combo[0]["charge"] + combo[1]["charge"]
                if charge_min <= total_charge <= charge_max:
                    components = list(combo)
                    formatted_name = _format_adduct_name(components)
                    combinations_list.append(
                        {
                            "components": components,
                            "formatted_name": formatted_name,
                            "total_mass_shift": combo[0]["mass_shift"]
                            + combo[1]["mass_shift"],
                            "total_charge": total_charge,
                            "combined_probability": combo[0]["probability"]
                            * combo[1]["probability"],
                            "complexity": 2,
                        },
                    )

    # 4. 3-component combinations (limited for performance)
    if max_combinations >= 3:
        for pos_spec in positive_specs[:2]:
            for neut_combo in combinations(neutral_specs[:2], 2):
                components = [pos_spec] + list(neut_combo)
                total_charge = sum(spec["charge"] for spec in components)

                if charge_min <= total_charge <= charge_max:
                    formatted_name = _format_adduct_name(components)
                    total_mass_shift = sum(spec["mass_shift"] for spec in components)
                    combined_prob = np.prod(
                        [spec["probability"] for spec in components],
                    )

                    combinations_list.append(
                        {
                            "components": components,
                            "formatted_name": formatted_name,
                            "total_mass_shift": total_mass_shift,
                            "total_charge": total_charge,
                            "combined_probability": combined_prob,
                            "complexity": 3,
                        },
                    )

    # Convert to polars DataFrame
    if combinations_list:
        combinations_list.sort(
            key=lambda x: (-x["combined_probability"], x["complexity"]),
        )

        adducts_df = pl.DataFrame(
            [
                {
                    "name": combo["formatted_name"],
                    "charge": combo["total_charge"],
                    "mass_shift": combo["total_mass_shift"],
                    "probability": combo["combined_probability"],
                    "complexity": combo["complexity"],
                    "components": combo["components"],
                }
                for combo in combinations_list
            ],
        )
    else:
        # Return empty DataFrame with correct schema
        adducts_df = pl.DataFrame(
            {
                "name": [],
                "charge": [],
                "mass_shift": [],
                "probability": [],
                "complexity": [],
                "components": [],
            },
        )

    return adducts_df


def _calculate_formula_mass_shift(formula: str) -> float:
    """
    Calculate mass shift from formula string like "+H", "-H2O", "+Na-H", etc.

    Parameters
    ----------
    formula : str
        Formula string (e.g., "+H", "-H2O", "+Na-H")

    Returns
    -------
    float
        Mass shift in Daltons
    """
    # Standard atomic masses
    atomic_masses = {
        "H": 1.007825,
        "C": 12.0,
        "N": 14.003074,
        "O": 15.994915,
        "Na": 22.989769,
        "K": 38.963707,
        "Li": 7.016003,
        "Ca": 39.962591,
        "Mg": 23.985042,
        "Fe": 55.934938,
        "Cl": 34.968853,
        "Br": 78.918336,
        "I": 126.904473,
        "P": 30.973762,
        "S": 31.972071,
    }

    total_mass = 0.0

    # Parse formula by splitting on + and - while preserving the operators
    parts = []
    current_part = ""
    current_sign = 1

    for char in formula:
        if char == "+":
            if current_part:
                parts.append((current_sign, current_part))
            current_part = ""
            current_sign = 1
        elif char == "-":
            if current_part:
                parts.append((current_sign, current_part))
            current_part = ""
            current_sign = -1
        else:
            current_part += char

    if current_part:
        parts.append((current_sign, current_part))

    # Process each part
    for sign, part in parts:
        if not part:
            continue

        # Parse element and count (e.g., "H2O" -> H:2, O:1)
        elements = _parse_element_counts(part)

        for element, count in elements.items():
            if element in atomic_masses:
                total_mass += sign * atomic_masses[element] * count

    return total_mass


def _parse_element_counts(formula_part: str) -> Dict[str, int]:
    """Parse element counts from a formula part like 'H2O' -> {'H': 2, 'O': 1}"""
    elements = {}
    i = 0

    while i < len(formula_part):
        # Get element (uppercase letter, possibly followed by lowercase)
        element = formula_part[i]
        i += 1

        while i < len(formula_part) and formula_part[i].islower():
            element += formula_part[i]
            i += 1

        # Get count (digits following element)
        count_str = ""
        while i < len(formula_part) and formula_part[i].isdigit():
            count_str += formula_part[i]
            i += 1

        count = int(count_str) if count_str else 1
        elements[element] = elements.get(element, 0) + count

    return elements


def _format_adduct_name(components: List[Dict]) -> str:
    """Format adduct name from components like [M+H]1+ or [M+2H]2+ or [M+2(H+Na)]3+"""
    if not components:
        return "[M]"

    # Count occurrences of each formula
    from collections import Counter

    formula_counts = Counter(comp["formula"] for comp in components)
    total_charge = sum(comp["charge"] for comp in components)

    # Build formula part with proper multipliers
    formula_parts = []
    for formula, count in sorted(
        formula_counts.items(),
    ):  # Sort for consistent ordering
        if count == 1:
            formula_parts.append(formula)
        else:
            # For multiple occurrences, use count prefix (e.g., 2H, 3Na)
            # Handle special case where formula might already start with + or -
            if formula.startswith(("+", "-")):
                sign = formula[0]
                base_formula = formula[1:]
                formula_parts.append(f"{sign}{count}{base_formula}")
            else:
                formula_parts.append(f"{count}{formula}")

    # Combine formula parts
    formula = "".join(formula_parts)

    # Format charge
    if total_charge == 0:
        charge_str = ""
    elif abs(total_charge) == 1:
        charge_str = "1+" if total_charge > 0 else "1-"
    else:
        charge_str = (
            f"{abs(total_charge)}+" if total_charge > 0 else f"{abs(total_charge)}-"
        )

    return f"[M{formula}]{charge_str}"


def find_adducts(self, **kwargs):
    """Detect adduct relationships among detected features using improved OpenMS-like algorithm.

    This method implements a corrected version of the OpenMS MetaboliteFeatureDeconvolution
    algorithm that properly enforces RT constraints and avoids the mass tolerance dominance
    issues present in the original C++ implementation.

    Key improvements over OpenMS:
    - Early RT filtering prevents expensive mass calculations for temporally incompatible features
    - Strict mass tolerance (0.01 Da default) prevents inappropriate mass relationships
    - RT constraints are properly enforced throughout the algorithm
    - Connected components analysis respects both mass AND RT constraints
    - Probability-based scoring for adduct assignment

    Main parameters (from ``find_adducts_defaults``):
    - adducts (list[str] | str | None): List of potential adduct strings or ionization mode ('pos'/'neg').
    - charge_min (int): Minimum allowed charge state (default: -4).
    - charge_max (int): Maximum allowed charge state (default: 4).
    - retention_max_diff (float): Maximum RT difference in seconds (default: 1.0).
    - mass_max_diff (float): Maximum mass tolerance (default: 0.01 Da).
    - unit (str): Mass tolerance unit 'Da' or 'ppm' (default: 'Da').
    - min_probability (float): Minimum probability threshold for adducts (default: 0.03).

    Side effects:
        Updates ``self.features_df`` with adduct information columns.
    """
    # Initialize parameters
    params = find_adducts_defaults()

    for key, value in kwargs.items():
        if isinstance(value, find_adducts_defaults):
            params = value
            self.logger.debug("Using provided find_adducts_defaults parameters")
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

    # Check if features_df exists and has data
    if not hasattr(self, "features_df") or len(self.features_df) == 0:
        self.logger.warning(
            "No features available for adduct detection. Run find_features() first.",
        )
        return

    self.logger.info("Adduct detection...")

    # Validate required columns
    required_cols = ["mz", "rt"]
    missing_cols = [col for col in required_cols if col not in self.features_df.columns]
    if missing_cols:
        self.logger.error(f"Required columns missing from features_df: {missing_cols}")
        return

    # Check if we have any features to process
    if len(self.features_df) == 0:
        self.logger.warning("No features available for adduct detection")
        return

    # Remove existing adduct columns if they exist
    columns_to_remove = ["adduct", "adduct_mass", "adduct_charge", "adduct_group"]
    for col in columns_to_remove:
        if col in self.features_df.columns:
            self.features_df = self.features_df.drop(col)

    # Get parameters
    adducts_list = params.get_openms_adducts()
    charge_min = params.get("charge_min")
    charge_max = params.get("charge_max")
    retention_max_diff = params.get("retention_max_diff")
    mass_max_diff = params.get("mass_max_diff")
    unit = params.get("unit")
    min_probability = params.get("min_probability")

    self.logger.debug(
        f"Processing {len(self.features_df)} features with {len(adducts_list)} base adducts",
    )
    self.logger.debug(
        f"RT tolerance: {retention_max_diff}s, Mass tolerance: {mass_max_diff} {unit}",
    )
    self.logger.debug(f"Min probability threshold: {min_probability}")

    # Generate comprehensive adduct specifications using the Sample method
    adducts_df = self._get_adducts(
        adducts_list=adducts_list,
        charge_min=charge_min,
        charge_max=charge_max,
        max_combinations=4,
    )

    self.logger.debug(f"Generated {len(adducts_df)} total adduct combinations")

    # Filter adducts by minimum probability threshold
    if min_probability > 0.0:
        adducts_before_filter = len(adducts_df)
        adducts_df = adducts_df.filter(pl.col("probability") >= min_probability)
        adducts_after_filter = len(adducts_df)
        filtered_count = adducts_before_filter - adducts_after_filter

        self.logger.debug(
            f"Filtered {filtered_count} low-probability adducts (< {min_probability})",
        )
        self.logger.debug(f"Remaining adducts for analysis: {adducts_after_filter}")

        if len(adducts_df) == 0:
            self.logger.warning(
                f"No adducts remaining after probability filtering (min_probability={min_probability})",
            )
            return

    # Implement the adduct detection algorithm directly here
    import numpy as np

    # Get parameters
    charge_max = params.get("charge_max")
    retention_max_diff = params.get("retention_max_diff")
    mass_max_diff = params.get("mass_max_diff")
    unit = params.get("unit")

    # Sort features by RT for efficient RT-sweep processing (OpenMS approach)
    # Store original row positions before sorting for correct index mapping
    features_with_positions = self.features_df.with_row_index("original_position")
    features_sorted = features_with_positions.sort("rt")
    n_features = len(features_sorted)

    # Extract arrays for fast processing
    feature_mzs = features_sorted.select("mz").to_numpy().flatten()
    feature_rts = features_sorted.select("rt").to_numpy().flatten()

    # Convert adducts to arrays for vectorized operations
    adduct_mass_shifts = adducts_df.select("mass_shift").to_numpy().flatten()
    adduct_charges = adducts_df.select("charge").to_numpy().flatten()
    adduct_names = adducts_df.select("name").to_series().to_list()
    adduct_probs = adducts_df.select("probability").to_numpy().flatten()

    self.logger.debug(
        f"RT-sweep processing: {n_features} features × {len(adducts_df)} adduct combinations",
    )

    # Phase 1: RT-sweep line algorithm with early RT filtering (fixes OpenMS flaw #1)
    candidate_edges = []

    for i_rt in range(n_features):
        mz1 = feature_mzs[i_rt]
        rt1 = feature_rts[i_rt]

        # RT-window sweep: only check features within RT tolerance (early filtering)
        for j_rt in range(i_rt + 1, n_features):
            rt2 = feature_rts[j_rt]
            rt_diff = rt2 - rt1

            # Early RT constraint check (fixes OpenMS issue where RT was checked too late)
            if rt_diff > retention_max_diff:
                break  # Features are RT-sorted, so no more valid pairs

            mz2 = feature_mzs[j_rt]

            # Phase 2: Check for valid mass relationships with strict tolerance (fixes OpenMS flaw #2)
            for adduct_idx, mass_shift in enumerate(adduct_mass_shifts):
                charge = adduct_charges[adduct_idx]

                # Calculate mass tolerance (per feature, as in OpenMS)
                if unit == "ppm":
                    tol1 = mass_max_diff * mz1 * 1e-6
                    tol2 = mass_max_diff * mz2 * 1e-6
                    combined_tolerance = tol1 + tol2
                else:  # Da
                    combined_tolerance = (
                        2 * mass_max_diff
                    )  # Combined tolerance for both features

                # Check both directions of mass relationship
                if charge != 0:
                    # For charged adducts: m/z relationship
                    mass_diff_12 = (mz2 * abs(charge)) - (mz1 * abs(charge))
                    expected_mass_diff = mass_shift

                    if abs(mass_diff_12 - expected_mass_diff) <= combined_tolerance:
                        # Valid mass relationship found
                        candidate_edges.append(
                            {
                                "i": i_rt,
                                "j": j_rt,
                                "rt_diff": rt_diff,
                                "mass_error": abs(mass_diff_12 - expected_mass_diff),
                                "adduct_idx": adduct_idx,
                                "charge1": charge if mass_diff_12 > 0 else -charge,
                                "charge2": -charge if mass_diff_12 > 0 else charge,
                                "probability": adduct_probs[adduct_idx],
                            },
                        )
                else:
                    # For neutral adducts: direct mass shift
                    mass_diff_12 = mz2 - mz1
                    if abs(mass_diff_12 - mass_shift) <= combined_tolerance:
                        candidate_edges.append(
                            {
                                "i": i_rt,
                                "j": j_rt,
                                "rt_diff": rt_diff,
                                "mass_error": abs(mass_diff_12 - mass_shift),
                                "adduct_idx": adduct_idx,
                                "charge1": 0,
                                "charge2": 0,
                                "probability": adduct_probs[adduct_idx],
                            },
                        )

    self.logger.debug(
        f"Found {len(candidate_edges)} candidate edges after RT+mass filtering",
    )

    if len(candidate_edges) == 0:
        self.logger.info("No adduct relationships found")
        return

    # Phase 3: Connected components analysis (respects both RT and mass constraints)
    # Build adjacency matrix from valid edges only
    adjacency = {}
    for i in range(n_features):
        adjacency[i] = []

    for edge in candidate_edges:
        i, j = edge["i"], edge["j"]
        adjacency[i].append(j)
        adjacency[j].append(i)

    # Find connected components using DFS
    visited = [False] * n_features
    components = []

    def dfs(node, component):
        visited[node] = True
        component.append(node)
        for neighbor in adjacency[node]:
            if not visited[neighbor]:
                dfs(neighbor, component)

    for i in range(n_features):
        if not visited[i] and len(adjacency[i]) > 0:
            component = []
            dfs(i, component)
            if len(component) > 1:  # Only multi-feature groups
                components.append(component)

    self.logger.debug(f"Found {len(components)} connected adduct groups")

    # Phase 4: Assign adduct identities with probability-based scoring
    adduct_assignments = [None] * n_features
    adduct_charges_assigned = [0] * n_features
    group_assignments = [0] * n_features
    mass_shift_assignments = [0.0] * n_features
    neutral_mass_assignments = [0.0] * n_features

    for group_id, component in enumerate(components, 1):
        # Find the most likely base ion (highest intensity or lowest m/z as proxy)
        component_mzs = [feature_mzs[idx] for idx in component]
        base_idx_in_component = np.argmin(component_mzs)  # Lowest m/z as base
        base_feature_idx = component[base_idx_in_component]
        base_mz = feature_mzs[base_feature_idx]

        # Assign base ion
        base_adduct = "[M+H]1+" if charge_max > 0 else "[M-H]1-"
        base_charge = 1 if charge_max > 0 else -1
        base_mass_shift = 1.007825 if charge_max > 0 else -1.007825  # H mass

        adduct_assignments[base_feature_idx] = base_adduct
        adduct_charges_assigned[base_feature_idx] = base_charge
        group_assignments[base_feature_idx] = group_id
        mass_shift_assignments[base_feature_idx] = base_mass_shift

        # Calculate neutral mass for base ion
        base_mz_measured = feature_mzs[base_feature_idx]
        neutral_mass_assignments[base_feature_idx] = (
            base_mz_measured * abs(base_charge) - base_mass_shift
        )

        # Assign other features based on their relationships to base
        for feature_idx in component:
            if feature_idx == base_feature_idx:
                continue

            group_assignments[feature_idx] = group_id

            # Find best adduct assignment based on mass difference and probability
            feature_mz = feature_mzs[feature_idx]
            best_score = -np.inf
            best_assignment = "[M+?]1+"
            best_charge = 1
            best_mass_shift = 1.007825  # Default to H mass shift for [M+?]1+

            # Check all possible adducts
            for adduct_idx, (mass_shift, charge, name, prob) in enumerate(
                zip(
                    adduct_mass_shifts,
                    adduct_charges,
                    adduct_names,
                    adduct_probs,
                ),
            ):
                if charge != 0:
                    expected_mz = base_mz + mass_shift / abs(charge)
                else:
                    expected_mz = base_mz + mass_shift

                mass_error = abs(expected_mz - feature_mz)

                # Combined score: probability + mass accuracy
                if mass_error < mass_max_diff * 2:  # Within tolerance
                    score = prob - mass_error * 0.1  # Weight mass accuracy
                    if score > best_score:
                        best_score = score
                        best_assignment = name
                        best_charge = charge
                        best_mass_shift = mass_shift

            adduct_assignments[feature_idx] = best_assignment
            adduct_charges_assigned[feature_idx] = best_charge
            mass_shift_assignments[feature_idx] = best_mass_shift

            # Calculate neutral mass
            neutral_mass_assignments[feature_idx] = (
                feature_mz * abs(best_charge) - best_mass_shift
            )

    # Assign fallback adduct for features not processed in connected components (isolated features)
    for i in range(n_features):
        if adduct_assignments[i] is None:
            fallback_charge = 1 if charge_max > 0 else -1
            fallback_mass_shift = 1.007825 if charge_max > 0 else -1.007825  # Assume H

            adduct_assignments[i] = "[M+?]1+"
            adduct_charges_assigned[i] = fallback_charge
            group_assignments[i] = 0  # No group assignment for isolated features
            mass_shift_assignments[i] = fallback_mass_shift

            # Calculate neutral mass for isolated features
            feature_mz = feature_mzs[i]
            neutral_mass_assignments[i] = (
                feature_mz * abs(fallback_charge) - fallback_mass_shift
            )

    # Map back to original feature order using stored positions
    original_indices = features_sorted.select("original_position").to_numpy().flatten()

    # Create final assignments in original order (same size as original DataFrame)
    final_adducts = [None] * len(self.features_df)
    final_charges = [0] * len(self.features_df)
    final_groups = [0] * len(self.features_df)
    final_mass_shifts = [0.0] * len(self.features_df)
    final_neutral_masses = [0.0] * len(self.features_df)

    for sorted_idx, orig_idx in enumerate(original_indices):
        final_adducts[orig_idx] = adduct_assignments[sorted_idx]
        final_charges[orig_idx] = adduct_charges_assigned[sorted_idx]
        final_groups[orig_idx] = group_assignments[sorted_idx]
        final_mass_shifts[orig_idx] = mass_shift_assignments[sorted_idx]
        final_neutral_masses[orig_idx] = neutral_mass_assignments[sorted_idx]

    # Update features DataFrame with correct column ordering
    # Insert adduct columns in the specified order after iso_of column

    # Get current columns
    current_columns = self.features_df.columns

    # Find the position of iso_of column
    try:
        iso_of_index = current_columns.index("iso_of")
        insert_position = iso_of_index + 1
    except ValueError:
        # If iso_of doesn't exist, append at the end
        insert_position = len(current_columns)
        self.logger.warning("iso_of column not found, adding adduct columns at the end")

    # Remove any existing adduct columns first
    adduct_column_names = [
        "adduct",
        "adduct_charge",
        "adduct_mass_shift",
        "adduct_mass_neutral",
        "adduct_group",
    ]
    df_without_adducts = self.features_df.select(
        [col for col in current_columns if col not in adduct_column_names],
    )

    # Split columns at insertion point
    columns_before = df_without_adducts.columns[:insert_position]
    columns_after = df_without_adducts.columns[insert_position:]

    # Create the new column order with adduct columns in the correct position
    new_column_order = list(columns_before) + adduct_column_names + list(columns_after)

    # Add adduct columns to the dataframe
    self.features_df = df_without_adducts.with_columns(
        [
            pl.Series("adduct", final_adducts),
            pl.Series("adduct_charge", final_charges),
            pl.Series("adduct_mass_shift", final_mass_shifts),
            pl.Series("adduct_mass_neutral", final_neutral_masses),
            pl.Series("adduct_group", final_groups),
        ],
    ).select(new_column_order)

    # Summary statistics
    total_with_adducts = sum(1 for x in final_adducts if x is not None)
    total_groups = max(final_groups) if final_groups else 0

    self.logger.info(
        f"Adduct detection completed: {total_with_adducts} features with adducts in {total_groups} groups",
    )

    # Store parameters including the actual processed adducts list
    history_params = params.to_dict()
    # Convert the filtered adducts dataframe to a list of adduct specifications for history
    history_params["adducts"] = adducts_df.select(
        ["name", "charge", "mass_shift", "probability"],
    ).to_dicts()

    self.store_history(["find_adducts"], history_params)
    self.logger.debug("Parameters stored successfully")
