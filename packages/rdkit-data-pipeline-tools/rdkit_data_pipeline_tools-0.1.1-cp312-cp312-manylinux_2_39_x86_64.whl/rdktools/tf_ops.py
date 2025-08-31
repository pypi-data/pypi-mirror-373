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
    Process string tensors through a custom C++ operation.
    
    This operation can be used in TensorFlow data pipelines to perform
    custom string processing operations. Currently implemented as a 
    pass-through operation that returns the input unchanged, but can be
    extended to perform custom molecular string processing.
    
    Args:
        input_strings: A string tensor to process.
        name: Optional name for the operation.
        
    Returns:
        A string tensor with the same shape as the input.
        
    Raises:
        ImportError: If TensorFlow custom ops are not available.
        
    Example:
        >>> import tensorflow as tf
        >>> from rdktools.tf_ops import string_process
        >>> 
        >>> # Create a dataset with SMILES strings
        >>> smiles = tf.constant(["CCO", "c1ccccc1", "CC(=O)O"])
        >>> processed = string_process(smiles)
        >>> print(processed.numpy())
        [b'CCO' b'c1ccccc1' b'CC(=O)O']
        
        # Use in a tf.data pipeline
        >>> dataset = tf.data.Dataset.from_tensor_slices(["CCO", "c1ccccc1"])
        >>> dataset = dataset.map(lambda x: string_process(x))
    """
    _check_tf_ops()
    
    return _tf_ops_module.string_process(input_strings, name=name)


def create_tf_dataset_op(smiles_list, batch_size: int = 32):
    """
    Create a TensorFlow dataset with custom string processing.
    
    This is a convenience function that demonstrates how to use the custom
    string processing operation in a tf.data pipeline.
    
    Args:
        smiles_list: List of SMILES strings or tensor.
        batch_size: Batch size for the dataset.
        
    Returns:
        A tf.data.Dataset with batched, processed strings.
        
    Example:
        >>> smiles = ["CCO", "c1ccccc1", "CC(=O)O", "CCC"]
        >>> dataset = create_tf_dataset_op(smiles, batch_size=2)
        >>> for batch in dataset:
        ...     print(batch.numpy())
    """
    _check_tf_ops()
    
    # Create dataset from the input
    if isinstance(smiles_list, (list, tuple)):
        dataset = tf.data.Dataset.from_tensor_slices(smiles_list)
    else:
        dataset = tf.data.Dataset.from_tensor_slices(smiles_list)
    
    # Apply custom string processing
    dataset = dataset.map(
        lambda x: string_process(x),
        num_parallel_calls=tf.data.AUTOTUNE
    )
    
    # Batch the data
    dataset = dataset.batch(batch_size)
    
    # Prefetch for performance
    dataset = dataset.prefetch(tf.data.AUTOTUNE)
    
    return dataset


# Export public API
__all__ = [
    "string_process",
    "create_tf_dataset_op",
]


# Utility function to check if TensorFlow ops are available
def is_tf_ops_available() -> bool:
    """Check if TensorFlow custom ops are available."""
    return _TF_OPS_AVAILABLE