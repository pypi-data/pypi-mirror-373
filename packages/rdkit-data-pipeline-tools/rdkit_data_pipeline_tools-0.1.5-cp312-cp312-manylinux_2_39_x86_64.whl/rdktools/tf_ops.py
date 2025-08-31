"""
TensorFlow custom operations for RDK-Tools.

This module provides TensorFlow custom operations for use in TF data pipelines.
These operations can be used to process molecular data efficiently within
TensorFlow graphs and tf.data pipelines.
"""

import os
import tensorflow as tf
from typing import Optional


def _load_tf_ops():
    """Load the TensorFlow custom ops library."""
    try:
        # Get the directory where this module is located
        module_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Look for the shared library
        lib_path = os.path.join(module_dir, 'rdktools_tf_ops.so')
        
        if not os.path.exists(lib_path):
            raise ImportError(f"TensorFlow ops library not found at {lib_path}")
        
        # Load the custom ops
        tf_ops_module = tf.load_op_library(lib_path)
        return tf_ops_module
        
    except Exception as e:
        raise ImportError(f"Failed to load TensorFlow custom ops: {e}")


# Load the ops module
try:
    _tf_ops_module = _load_tf_ops()
    _TF_OPS_AVAILABLE = True
except ImportError as e:
    _tf_ops_module = None
    _TF_OPS_AVAILABLE = False
    _import_error = e


def _check_tf_ops():
    """Check if TensorFlow custom ops are available."""
    if not _TF_OPS_AVAILABLE:
        raise ImportError(
            f"RDK-Tools TensorFlow ops not available: {_import_error}. "
            "Please ensure TensorFlow is installed and the library was built with TensorFlow support."
        )


def string_process(input_strings: tf.Tensor, name: Optional[str] = None) -> tf.Tensor:
    """
    Process SMILES string tensors through RDKit for randomized SMILES generation.
    
    This operation takes SMILES strings as input and returns randomized SMILES strings 
    as output using RDKit's molecular parsing and canonical SMILES generation. Each 
    valid input SMILES is parsed by RDKit and converted to a randomized canonical form.
    Invalid SMILES strings are returned as empty strings.
    
    The randomization ensures that the same molecule can be represented with different
    atom orderings while maintaining chemical equivalence, which is useful for data
    augmentation in machine learning pipelines.
    
    Args:
        input_strings: A string tensor containing SMILES strings to process.
        name: Optional name for the operation.
        
    Returns:
        A string tensor with the same shape as the input, containing randomized
        SMILES strings. Invalid SMILES are returned as empty strings.
        
    Raises:
        ImportError: If TensorFlow custom ops are not available.
        
    Example:
        >>> import tensorflow as tf
        >>> from rdktools.tf_ops import string_process
        >>> 
        >>> # Create a dataset with SMILES strings
        >>> smiles = tf.constant(["CCO", "c1ccccc1", "CC(=O)O", "invalid"])
        >>> randomized = string_process(smiles)
        >>> print(randomized.numpy())
        # Output will be randomized SMILES like [b'OCC' b'c1ccccc1' b'CC(=O)O' b'']
        
        # Use in a tf.data pipeline for data augmentation
        >>> dataset = tf.data.Dataset.from_tensor_slices(["CCO", "c1ccccc1"])
        >>> dataset = dataset.map(lambda x: string_process(tf.expand_dims(x, 0))[0])
        >>> for item in dataset:
        ...     print(item.numpy().decode())  # Will show randomized SMILES
    """
    _check_tf_ops()
    
    return _tf_ops_module.string_process(input_strings, name=name)

# Export public API
__all__ = [
    "string_process",
]


# Utility function to check if TensorFlow ops are available
def is_tf_ops_available() -> bool:
    """Check if TensorFlow custom ops are available."""
    return _TF_OPS_AVAILABLE