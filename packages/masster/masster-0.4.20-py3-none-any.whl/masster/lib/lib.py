"""
lib.py

This module provides the Lib class for mass spectrometry compound library 
management and feature annotation.

The Lib class supports annotation of sample.features_df and study.consensus_df 
based on MS1 (rt, m/z, possibly isotopes) and MS2 data.

Key Features:
- **Lib Class**: Main class for managing compound libraries and annotations
- **Compound Libraries**: Load and manage compound databases with metadata
- **Adduct Calculations**: Handle various ionization adducts and charge states
- **Mass Calculations**: Precise mass calculations with adduct corrections
- **Target Matching**: Match detected features against compound libraries
- **Polarity Handling**: Support for positive and negative ionization modes
- **CSV Import**: Import compound data from CSV files with automatic adduct generation

Dependencies:
- `pyopenms`: For mass spectrometry algorithms and data structures
- `polars`: For efficient data manipulation and analysis
- `numpy`: For numerical computations and array operations
- `uuid`: For generating unique identifiers

Supported Adducts:
- Positive mode: [M+H]+, [M+Na]+, [M+K]+, [M+NH4]+, [M-H2O+H]+
- Negative mode: [M-H]-, [M+CH3COO]-, [M+HCOO]-, [M+Cl]-

Example Usage:
```python
from masster.lib import Lib

# Create library instance
lib = Lib()

# Import compounds from CSV
lib.import_csv("compounds.csv", polarity="positive")

# Access library data
print(f"Loaded {len(lib.lib_df)} compounds")
print(lib.lib_df.head())

# Annotate sample features
annotations = lib.annotate_features(sample.features_df)
```
"""

import os
import uuid
from typing import Optional, Union, List, Dict, Any, TYPE_CHECKING
import warnings

import numpy as np
import polars as pl
import pyopenms as oms

if TYPE_CHECKING:
    import pandas as pd


class Lib:
    """
    A class for managing compound libraries and feature annotation in mass spectrometry data.
    
    The Lib class provides functionality to:
    - Load compound libraries from CSV files
    - Generate adduct variants for compounds
    - Annotate MS1 features based on mass and retention time
    - Support both positive and negative ionization modes
    - Manage compound metadata (SMILES, InChI, formulas, etc.)
    
    Attributes:
        lib_df (pl.DataFrame): Polars DataFrame containing the library data with columns:
            - lib_uid: Unique identifier for each library entry
            - name: Compound name
            - smiles: SMILES notation
            - inchi: InChI identifier
            - inchikey: InChI key
            - formula: Molecular formula
            - adduct: Adduct type
            - m: Mass with adduct
            - z: Charge state
            - mz: Mass-to-charge ratio
            - rt: Retention time (if available)
    
    Example:
        >>> lib = Lib()
        >>> lib.import_csv("compounds.csv", polarity="positive")
        >>> print(f"Loaded {len(lib.lib_df)} library entries")
    """
    
    # Define supported adducts and their properties
    ADDUCT_DEFINITIONS = {
        # Positive mode adducts
        "[M+H]1+": {"delta_m": 1.007276, "delta_z": 1, "polarity": "positive"},
        "[M+Na]1+": {"delta_m": 22.989218, "delta_z": 1, "polarity": "positive"},
        "[M+K]1+": {"delta_m": 38.962383, "delta_z": 1, "polarity": "positive"},
        "[M+NH4]1+": {"delta_m": 18.033823, "delta_z": 1, "polarity": "positive"},
        "[M+H-H2O]1+": {"delta_m": -17.00329, "delta_z": 1, "polarity": "positive"},
        "[M+2H]2+": {"delta_m": 2.014552, "delta_z": 2, "polarity": "positive"},
        
        # Negative mode adducts
        "[M-H]1-": {"delta_m": -1.007276, "delta_z": -1, "polarity": "negative"},
        "[M+CH3COO]1-": {"delta_m": 59.013852, "delta_z": -1, "polarity": "negative"},
        "[M+HCOO]1-": {"delta_m": 44.998203, "delta_z": -1, "polarity": "negative"},
        "[M+Cl]1-": {"delta_m": 34.968853, "delta_z": -1, "polarity": "negative"},
        "[M-2H]2-": {"delta_m": -2.014552, "delta_z": -2, "polarity": "negative"},
    }
    
    def __init__(self):
        """Initialize an empty Lib instance."""
        self.lib_df = None
        self._initialize_empty_dataframe()
    
    def _initialize_empty_dataframe(self):
        """Initialize an empty DataFrame with the required schema."""
        self.lib_df = pl.DataFrame({
            "lib_uid": pl.Series([], dtype=pl.Int64),
            "cmpd_uid": pl.Series([], dtype=pl.Int64),
            "source_id": pl.Series([], dtype=pl.Utf8),
            "name": pl.Series([], dtype=pl.Utf8),
            "smiles": pl.Series([], dtype=pl.Utf8),
            "inchi": pl.Series([], dtype=pl.Utf8),
            "inchikey": pl.Series([], dtype=pl.Utf8),
            "formula": pl.Series([], dtype=pl.Utf8),
            "adduct": pl.Series([], dtype=pl.Utf8),
            "m": pl.Series([], dtype=pl.Float64),
            "z": pl.Series([], dtype=pl.Int8),
            "mz": pl.Series([], dtype=pl.Float64),
            "rt": pl.Series([], dtype=pl.Float64),
            "db_id": pl.Series([], dtype=pl.Utf8),
            "db": pl.Series([], dtype=pl.Utf8),
        })
    
    def _calculate_accurate_mass(self, formula: str) -> Optional[float]:
        """
        Calculate the accurate mass for a molecular formula using PyOpenMS.
        
        Args:
            formula: Molecular formula string
            
        Returns:
            Accurate mass as float, or None if calculation fails
        """
        # Skip obviously invalid formulas
        if not formula or not isinstance(formula, str):
            return None
        
        # Clean up whitespace
        formula = formula.strip()
        
        # Skip formulas that are obviously invalid
        invalid_patterns = [
            # Contains parentheses with multipliers like (C12H19NO19S3)nH2O
            lambda f: '(' in f and ')' in f and any(c.isalpha() and not c.isupper() for c in f.split(')')[1:]),
            # Contains words instead of chemical symbols
            lambda f: any(word in f.lower() for word in ['and', 'or', 'not', 'with', 'without']),
            # Contains lowercase letters at the start (element symbols should be uppercase)
            lambda f: f and f[0].islower(),
            # Contains unusual characters that shouldn't be in formulas
            lambda f: any(char in f for char in ['@', '#', '$', '%', '^', '&', '*', '=', '+', '?', '/', '\\', '|']),
            # Empty or very short non-standard formulas
            lambda f: len(f) < 2 and not f.isupper(),
        ]
        
        for pattern_check in invalid_patterns:
            try:
                if pattern_check(formula):
                    warnings.warn(f"Skipping obviously invalid formula: '{formula}'")
                    return None
            except Exception:
                # If pattern checking fails, continue to PyOpenMS parsing
                pass
        
        try:
            empirical_formula = oms.EmpiricalFormula(formula)
            return empirical_formula.getMonoWeight()
        except Exception as e:
            warnings.warn(f"Error calculating accurate mass for formula '{formula}': {e}")
            return None
    
    def _generate_adduct_variants(self, 
                                compound_data: Dict[str, Any], 
                                adducts: Optional[List[str]] = None,
                                polarity: Optional[str] = None,
                                lib_id_counter: Optional[int] = None) -> tuple[List[Dict[str, Any]], int]:
        """
        Generate adduct variants for a given compound.
        
        Args:
            compound_data: Dictionary containing compound information
            adducts: List of specific adducts to generate. If None, uses all adducts for polarity
            polarity: Ionization polarity ("positive", "negative", or None for both)
            lib_id_counter: Counter for generating unique lib_uid values
            
        Returns:
            Tuple of (list of dictionaries representing adduct variants, updated counter)
        """
        variants = []
        counter = lib_id_counter or 1
        
        # Calculate base accurate mass
        accurate_mass = self._calculate_accurate_mass(compound_data["formula"])
        if accurate_mass is None:
            return variants, counter
        
        # Determine which adducts to use
        if adducts is None:
            if polarity is None:
                # Use all adducts
                selected_adducts = list(self.ADDUCT_DEFINITIONS.keys())
            else:
                # Filter by polarity
                selected_adducts = [
                    adduct for adduct, props in self.ADDUCT_DEFINITIONS.items()
                    if props["polarity"] == polarity.lower()
                ]
        else:
            selected_adducts = adducts
        
        # Generate variants for each adduct
        for adduct in selected_adducts:
            if adduct not in self.ADDUCT_DEFINITIONS:
                warnings.warn(f"Unknown adduct: {adduct}")
                continue
                
            adduct_props = self.ADDUCT_DEFINITIONS[adduct]
            
            # Skip if polarity doesn't match
            if polarity is not None and adduct_props["polarity"] != polarity.lower():
                continue
            
            # Calculate adducted mass and m/z
            adducted_mass = accurate_mass + adduct_props["delta_m"]
            charge = adduct_props["delta_z"]
            mz = abs(adducted_mass / charge) if charge != 0 else adducted_mass
            
            # Create variant entry
            variant = {
                "lib_uid": counter,
                "cmpd_uid": compound_data.get("cmpd_uid", None),
                "source_id": compound_data.get("source_id", None),
                "name": compound_data.get("name", ""),
                "smiles": compound_data.get("smiles", ""),
                "inchi": compound_data.get("inchi", ""),
                "inchikey": compound_data.get("inchikey", ""),
                "formula": compound_data["formula"],
                "adduct": adduct,
                "m": adducted_mass,
                "z": charge,
                "mz": mz,
                "rt": compound_data.get("rt", None),
                "db_id": compound_data.get("db_id", None),
                "db": compound_data.get("db", None),
            }
            variants.append(variant)
            counter += 1
        
        return variants, counter
    
    def import_csv(self, 
                  csvfile: str, 
                  polarity: Optional[str] = None,
                  adducts: Optional[List[str]] = None) -> None:
        """
        Import compound library from a CSV file.
        
        This method reads a CSV file and generates adduct variants for each compound.
        Missing columns will be filled with appropriate default values.
        
        Args:
            csvfile: Path to the CSV file
            polarity: Ionization polarity ("positive", "negative", or None for both)
            adducts: Specific adducts to generate. If None, generates all for the polarity
            
        Expected CSV columns (case-insensitive):
            - Required: Formula (or formula)
            - Optional: Name/name/Compound/compound, SMILES/smiles, InChI/inchi, 
                      InChIKey/inchikey, RT/rt, RT2/rt2
        
        Raises:
            FileNotFoundError: If CSV file doesn't exist
            ValueError: If required columns are missing
        """
        if not os.path.exists(csvfile):
            raise FileNotFoundError(f"CSV file not found: {csvfile}")
        
        # Read CSV file with robust error handling
        try:
            df = pl.read_csv(csvfile, truncate_ragged_lines=True, ignore_errors=True)
        except Exception as e:
            raise ValueError(f"Error reading CSV file: {e}") from e
        
        # Find column mappings (case-insensitive)
        column_mapping = self._map_csv_columns(df.columns)
        
        # Validate required columns
        if "formula" not in column_mapping:
            raise ValueError("Required column 'Formula' (or 'formula') not found in CSV file")
        
        # Process each compound
        all_variants = []
        cmpd_id_counter = 1
        lib_id_counter = 1
        total_compounds = 0
        skipped_compounds = 0
        
        for row in df.iter_rows(named=True):
            total_compounds += 1
            
            # Extract compound data
            # assign a compound-level uid so all adducts share the same cmpd_uid
            compound_level_uid = cmpd_id_counter
            cmpd_id_counter += 1

            compound_data = {
                "name": row.get(column_mapping.get("name", ""), ""),
                "smiles": row.get(column_mapping.get("smiles", ""), ""),
                "inchi": row.get(column_mapping.get("inchi", ""), ""),
                "inchikey": row.get(column_mapping.get("inchikey", ""), ""),
                "formula": row[column_mapping["formula"]],
                "rt": self._safe_float_conversion(row.get(column_mapping.get("rt", ""), None)),
                "db_id": row.get(column_mapping.get("db_id", ""), None),
                "db": row.get(column_mapping.get("db", ""), None),
                "cmpd_uid": compound_level_uid,
            }
            
            # Generate adduct variants
            variants, lib_id_counter = self._generate_adduct_variants(
                compound_data, adducts=adducts, polarity=polarity, lib_id_counter=lib_id_counter
            )
            all_variants.extend(variants)
            
            # Track if compound was skipped due to invalid formula
            if len(variants) == 0:
                skipped_compounds += 1
            
            # Handle RT2 column if present
            if "rt2" in column_mapping and len(variants) > 0:  # Only if main variants were created
                rt2_value = self._safe_float_conversion(row.get(column_mapping["rt2"], None))
                if rt2_value is not None:
                    # Create additional variants with RT2
                    compound_data_rt2 = compound_data.copy()
                    compound_data_rt2["rt"] = rt2_value
                    compound_data_rt2["name"] = compound_data["name"] + " II"
                    
                    variants_rt2, lib_id_counter = self._generate_adduct_variants(
                        compound_data_rt2, adducts=adducts, polarity=polarity, lib_id_counter=lib_id_counter
                    )
                    all_variants.extend(variants_rt2)
        
        # Convert to DataFrame and store
        if all_variants:
            new_lib_df = pl.DataFrame(all_variants)
            
            # Combine with existing data if any
            if self.lib_df is not None and len(self.lib_df) > 0:
                self.lib_df = pl.concat([self.lib_df, new_lib_df])
            else:
                self.lib_df = new_lib_df
                
            #successful_compounds = total_compounds - skipped_compounds
            print(f"Imported {len(all_variants)} library entries from {csvfile}")
            #print(f"Processed {total_compounds} compounds: {successful_compounds} successful, {skipped_compounds} skipped due to invalid formulas")
        else:
            print(f"No valid compounds found in {csvfile}")
            if skipped_compounds > 0:
                print(f"All {total_compounds} compounds were skipped due to invalid formulas")
    
    def _map_csv_columns(self, columns: List[str]) -> Dict[str, str]:
        """
        Map CSV column names to standardized internal names (case-insensitive).
        
        Args:
            columns: List of column names from CSV
            
        Returns:
            Dictionary mapping internal names to actual column names
        """
        mapping = {}
        columns_lower = [col.lower() for col in columns]
        
        # Name mapping
        for name_variant in ["name", "compound"]:
            if name_variant in columns_lower:
                mapping["name"] = columns[columns_lower.index(name_variant)]
                break
        
        # Formula mapping
        for formula_variant in ["formula"]:
            if formula_variant in columns_lower:
                mapping["formula"] = columns[columns_lower.index(formula_variant)]
                break
        
        # SMILES mapping
        for smiles_variant in ["smiles"]:
            if smiles_variant in columns_lower:
                mapping["smiles"] = columns[columns_lower.index(smiles_variant)]
                break
        
        # InChI mapping
        for inchi_variant in ["inchi"]:
            if inchi_variant in columns_lower:
                mapping["inchi"] = columns[columns_lower.index(inchi_variant)]
                break
        
        # InChIKey mapping
        for inchikey_variant in ["inchikey", "inchi_key"]:
            if inchikey_variant in columns_lower:
                mapping["inchikey"] = columns[columns_lower.index(inchikey_variant)]
                break
        
        # RT mapping
        for rt_variant in ["rt", "retention_time", "retentiontime"]:
            if rt_variant in columns_lower:
                mapping["rt"] = columns[columns_lower.index(rt_variant)]
                break
        
        # RT2 mapping
        for rt2_variant in ["rt2", "retention_time2", "retentiontime2"]:
            if rt2_variant in columns_lower:
                mapping["rt2"] = columns[columns_lower.index(rt2_variant)]
                break
        
        # Database ID mapping
        for db_id_variant in ["db_id", "database_id", "dbid"]:
            if db_id_variant in columns_lower:
                mapping["db_id"] = columns[columns_lower.index(db_id_variant)]
                break
        
        # Database mapping
        for db_variant in ["db", "database"]:
            if db_variant in columns_lower:
                mapping["db"] = columns[columns_lower.index(db_variant)]
                break
        
        return mapping
    
    def _safe_float_conversion(self, value: Any) -> Optional[float]:
        """
        Safely convert a value to float, returning None if conversion fails.
        
        Args:
            value: Value to convert
            
        Returns:
            Float value or None
        """
        if value is None or value == "":
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def annotate_features(self, 
                         features_df: Union[pl.DataFrame, "pd.DataFrame"],
                         mz_tolerance: float = 0.01,
                         rt_tolerance: Optional[float] = None) -> pl.DataFrame:
        """
        Annotate features based on library matches using m/z and retention time.
        
        Args:
            features_df: DataFrame containing features with 'mz' and optionally 'rt' columns
            mz_tolerance: Mass tolerance in Da for matching
            rt_tolerance: Retention time tolerance in minutes for matching (if None, RT not used)
            
        Returns:
            DataFrame with annotation results
        """
        if self.lib_df is None or len(self.lib_df) == 0:
            raise ValueError("Library is empty. Import compounds first.")
        
        # Convert pandas DataFrame to Polars if needed
        if hasattr(features_df, 'to_pandas'):  # It's already a Polars DataFrame
            features_pl = features_df
        elif hasattr(features_df, 'values'):  # It's likely a pandas DataFrame
            try:
                import pandas as pd
                if isinstance(features_df, pd.DataFrame):
                    features_pl = pl.from_pandas(features_df)
                else:
                    features_pl = features_df
            except ImportError:
                features_pl = features_df
        else:
            features_pl = features_df
        
        annotations = []
        
        for feature_row in features_pl.iter_rows(named=True):
            feature_mz = feature_row.get("mz")
            feature_rt = feature_row.get("rt")
            
            if feature_mz is None:
                continue
            
            # Find matching library entries
            mz_matches = self.lib_df.filter(
                (pl.col("mz") >= feature_mz - mz_tolerance) &
                (pl.col("mz") <= feature_mz + mz_tolerance)
            )
            
            # Apply RT filter if both RT tolerance and feature RT are available
            if rt_tolerance is not None and feature_rt is not None:
                # Filter library entries that have RT values
                rt_matches = mz_matches.filter(
                    pl.col("rt").is_not_null() &
                    (pl.col("rt") >= feature_rt - rt_tolerance) &
                    (pl.col("rt") <= feature_rt + rt_tolerance)
                )
                if len(rt_matches) > 0:
                    matches = rt_matches
                else:
                    matches = mz_matches  # Fall back to m/z-only matches
            else:
                matches = mz_matches
            
            # Create annotation entries
            for match_row in matches.iter_rows(named=True):
                annotation = {
                    "feature_mz": feature_mz,
                    "feature_rt": feature_rt,
                    "lib_uid": match_row["lib_uid"],
                    "cmpd_uid": match_row.get("cmpd_uid"),
                    "source_id": match_row.get("source_id"),
                    "name": match_row["name"],
                    "formula": match_row["formula"],
                    "adduct": match_row["adduct"],
                    "smiles": match_row["smiles"],
                    "inchi": match_row["inchi"],
                    "inchikey": match_row["inchikey"],
                    "lib_mz": match_row["mz"],
                    "lib_rt": match_row["rt"],
                    "delta_mz": abs(feature_mz - match_row["mz"]),
                    "delta_rt": abs(feature_rt - match_row["rt"]) if feature_rt is not None and match_row["rt"] is not None else None,
                }
                annotations.append(annotation)
        
        return pl.DataFrame(annotations) if annotations else pl.DataFrame()
    
    def get_adducts_for_polarity(self, polarity: str) -> List[str]:
        """
        Get list of supported adducts for a given polarity.
        
        Args:
            polarity: "positive" or "negative"
            
        Returns:
            List of adduct names
        """
        return [
            adduct for adduct, props in self.ADDUCT_DEFINITIONS.items()
            if props["polarity"] == polarity.lower()
        ]
    
    def __len__(self) -> int:
        """Return number of library entries."""
        return len(self.lib_df) if self.lib_df is not None else 0
    
    def _reload(self):
        """
        Reloads all masster modules to pick up any changes to their source code,
        and updates the instance's class reference to the newly reloaded class version.
        This ensures that the instance uses the latest implementation without restarting the interpreter.
        """
        import importlib
        import sys

        # Get the base module name (masster)
        base_modname = self.__class__.__module__.split(".")[0]
        current_module = self.__class__.__module__

        # Dynamically find all lib submodules
        lib_modules = []
        lib_module_prefix = f"{base_modname}.lib."

        # Get all currently loaded modules that are part of the lib package
        for module_name in sys.modules:
            if module_name.startswith(lib_module_prefix) and module_name != current_module:
                lib_modules.append(module_name)

        # Add core masster modules
        core_modules = [
            f"{base_modname}._version",
            f"{base_modname}.chromatogram",
            f"{base_modname}.spectrum",
            f"{base_modname}.logger",
        ]

        '''# Add study submodules (for cross-dependencies)
        study_modules = []
        study_module_prefix = f"{base_modname}.study."
        for module_name in sys.modules:
            if module_name.startswith(study_module_prefix) and module_name != current_module:
                study_modules.append(module_name)'''

        '''# Add sample submodules (for cross-dependencies)
        sample_modules = []
        sample_module_prefix = f"{base_modname}.sample."
        for module_name in sys.modules:
            if module_name.startswith(sample_module_prefix) and module_name != current_module:
                sample_modules.append(module_name)'''

        all_modules_to_reload = core_modules + lib_modules # sample_modules + study_modules + 

        # Reload all discovered modules
        for full_module_name in all_modules_to_reload:
            try:
                if full_module_name in sys.modules:
                    mod = sys.modules[full_module_name]
                    importlib.reload(mod)
                    # Note: Lib class doesn't have a logger by default, so we just print or use warnings
                    #print(f"Reloaded module: {full_module_name}")
            except Exception as e:
                print(f"Warning: Failed to reload module {full_module_name}: {e}")

        # Finally, reload the current module (lib.py)
        try:
            mod = __import__(current_module, fromlist=[current_module.split(".")[0]])
            importlib.reload(mod)

            # Get the updated class reference from the reloaded module
            new = getattr(mod, self.__class__.__name__)
            # Update the class reference of the instance
            self.__class__ = new

            print("Lib module reload completed")
        except Exception as e:
            print(f"Error: Failed to reload current module {current_module}: {e}")
    
    def __str__(self) -> str:
        """String representation of the library."""
        if self.lib_df is None or len(self.lib_df) == 0:
            return "Empty Lib instance"
        
        unique_compounds = self.lib_df.select("name").unique().height
        unique_adducts = self.lib_df.select("adduct").unique().height
        
        return f"Lib instance with {len(self)} entries ({unique_compounds} unique compounds, {unique_adducts} adduct types)"
