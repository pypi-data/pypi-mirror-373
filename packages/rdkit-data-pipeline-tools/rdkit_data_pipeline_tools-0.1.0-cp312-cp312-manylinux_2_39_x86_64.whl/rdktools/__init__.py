"""
RDK-Tools: High-performance molecular operations using RDKit's C++ core through nanobind bindings.

This module provides fast molecular descriptor calculations, SMILES validation, and fingerprint
generation by exposing RDKit's optimized C++ implementation with native numpy array support.
"""

from typing import Dict

import numpy as np

# Import the compiled C++ extension
try:
    from . import _rdktools_core

    _EXTENSION_AVAILABLE = True
except ImportError as e:
    _EXTENSION_AVAILABLE = False
    _import_error = e


def _check_extension():
    """Check if the C++ extension is available."""
    if not _EXTENSION_AVAILABLE:
        raise ImportError(
            f"RDK-Tools C++ extension not available: {_import_error}. "
            "Please build the extension first using: uv run python -m pip install -e ."
        )


def _validate_smiles_input(smiles) -> np.ndarray:
    """Convert and validate SMILES input to numpy string array."""
    if isinstance(smiles, (list, tuple)):
        smiles = np.array(smiles, dtype=str)
    elif isinstance(smiles, str):
        smiles = np.array([smiles], dtype=str)
    elif isinstance(smiles, np.ndarray):
        smiles = smiles.astype(str)
    else:
        raise TypeError("SMILES input must be string, list, or numpy array")

    return smiles


# Core descriptor functions
def molecular_weights(smiles) -> np.ndarray:
    """
    Calculate molecular weights for an array of SMILES strings.

    Args:
        smiles: Array-like of SMILES strings

    Returns:
        numpy array of molecular weights (float64). Invalid SMILES return NaN.
    """
    _check_extension()
    smiles = _validate_smiles_input(smiles)
    return _rdktools_core.calculate_molecular_weights(smiles)


def logp(smiles) -> np.ndarray:
    """
    Calculate LogP values for an array of SMILES strings.

    Args:
        smiles: Array-like of SMILES strings

    Returns:
        numpy array of LogP values (float64). Invalid SMILES return NaN.
    """
    _check_extension()
    smiles = _validate_smiles_input(smiles)
    return _rdktools_core.calculate_logp(smiles)


def tpsa(smiles) -> np.ndarray:
    """
    Calculate TPSA (Topological Polar Surface Area) for an array of SMILES strings.

    Args:
        smiles: Array-like of SMILES strings

    Returns:
        numpy array of TPSA values (float64). Invalid SMILES return NaN.
    """
    _check_extension()
    smiles = _validate_smiles_input(smiles)
    return _rdktools_core.calculate_tpsa(smiles)


# Validation functions
def is_valid(smiles) -> np.ndarray:
    """
    Check if SMILES strings are valid.

    Args:
        smiles: Array-like of SMILES strings

    Returns:
        numpy array of boolean values indicating validity.
    """
    _check_extension()
    smiles = _validate_smiles_input(smiles)
    return _rdktools_core.validate_smiles(smiles)


def canonical_smiles(smiles) -> np.ndarray:
    """
    Convert SMILES to canonical form.

    Args:
        smiles: Array-like of SMILES strings

    Returns:
        numpy array of canonical SMILES strings. Invalid SMILES return empty strings.
    """
    _check_extension()
    smiles = _validate_smiles_input(smiles)
    return _rdktools_core.canonicalize_smiles(smiles)


# Batch processing functions
def descriptors(smiles) -> Dict[str, np.ndarray]:
    """
    Calculate multiple descriptors efficiently in one pass.

    Args:
        smiles: Array-like of SMILES strings

    Returns:
        Dictionary with keys: 'molecular_weight', 'logp', 'tpsa'
        Each value is a numpy array. Invalid SMILES have NaN values.
    """
    _check_extension()
    smiles = _validate_smiles_input(smiles)
    return _rdktools_core.calculate_multiple_descriptors(smiles)


def morgan_fingerprints(smiles, radius: int = 2, nbits: int = 2048) -> np.ndarray:
    """
    Calculate Morgan fingerprints for an array of SMILES strings.

    Args:
        smiles: Array-like of SMILES strings
        radius: Fingerprint radius (default: 2)
        nbits: Number of bits in fingerprint (default: 2048)

    Returns:
        2D numpy array of shape (n_molecules, nbits) with uint8 values (0 or 1).
        Invalid SMILES have all-zero fingerprints.
    """
    _check_extension()
    smiles = _validate_smiles_input(smiles)
    return _rdktools_core.calculate_morgan_fingerprints(smiles, radius, nbits)


# Convenience functions
def filter_valid(smiles) -> np.ndarray:
    """
    Filter array to only valid SMILES strings.

    Args:
        smiles: Array-like of SMILES strings

    Returns:
        numpy array containing only valid SMILES strings.
    """
    smiles = _validate_smiles_input(smiles)
    valid_mask = is_valid(smiles)
    return smiles[valid_mask]


def batch_process(
    smiles,
    batch_size: int = 1000,
    include_descriptors: bool = True,
    include_fingerprints: bool = False,
    radius: int = 2,
    nbits: int = 2048,
) -> Dict[str, np.ndarray]:
    """
    Process large datasets in batches for memory efficiency.

    Args:
        smiles: Array-like of SMILES strings
        batch_size: Number of molecules per batch
        include_descriptors: Whether to calculate molecular descriptors
        include_fingerprints: Whether to calculate fingerprints
        radius: Fingerprint radius (if calculating fingerprints)
        nbits: Fingerprint size (if calculating fingerprints)

    Returns:
        Dictionary with results. Always includes 'valid' boolean array.
        If include_descriptors: adds 'molecular_weight', 'logp', 'tpsa'
        If include_fingerprints: adds 'fingerprints' 2D array
    """
    smiles = _validate_smiles_input(smiles)
    n_molecules = len(smiles)

    # Initialize result arrays
    results = {"valid": np.zeros(n_molecules, dtype=bool)}

    if include_descriptors:
        results.update(
            {
                "molecular_weight": np.full(n_molecules, np.nan),
                "logp": np.full(n_molecules, np.nan),
                "tpsa": np.full(n_molecules, np.nan),
            }
        )

    if include_fingerprints:
        results["fingerprints"] = np.zeros((n_molecules, nbits), dtype=np.uint8)

    # Process in batches
    for i in range(0, n_molecules, batch_size):
        end_idx = min(i + batch_size, n_molecules)
        batch_smiles = smiles[i:end_idx]

        # Validation
        batch_valid = is_valid(batch_smiles)
        results["valid"][i:end_idx] = batch_valid

        if include_descriptors:
            batch_desc = descriptors(batch_smiles)
            results["molecular_weight"][i:end_idx] = batch_desc["molecular_weight"]
            results["logp"][i:end_idx] = batch_desc["logp"]
            results["tpsa"][i:end_idx] = batch_desc["tpsa"]

        if include_fingerprints:
            batch_fps = morgan_fingerprints(batch_smiles, radius, nbits)
            results["fingerprints"][i:end_idx] = batch_fps

    return results


# Version and metadata
__version__ = "0.1.0"
__all__ = [
    "molecular_weights",
    "logp",
    "tpsa",
    "is_valid",
    "canonical_smiles",
    "descriptors",
    "morgan_fingerprints",
    "filter_valid",
    "batch_process",
]
