"""
💾 Data Utility Functions
========================

This module provides utilities for saving, loading, and converting data
in the holographic memory system, including state serialization and format conversion.

Author: Benedict Chen (benedict@benedictchen.com)
"""

import numpy as np
import json
import pickle
import gzip
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
import warnings


def save_memory_state(state: Dict[str, Any], 
                     filepath: Union[str, Path],
                     format: str = 'numpy',
                     compress: bool = False) -> bool:
    """
    Save holographic memory state to file.
    
    Parameters
    ----------
    state : Dict[str, Any]
        Memory state dictionary
    filepath : str or Path
        Output file path
    format : str, default='numpy'
        Save format ('numpy', 'json', 'pickle')
    compress : bool, default=False
        Whether to compress the file
        
    Returns
    -------
    bool
        True if saved successfully
    """
    filepath = Path(filepath)
    
    try:
        if format == 'numpy':
            if compress:
                # Save as compressed .npz
                filepath = filepath.with_suffix('.npz')
                np.savez_compressed(filepath, **state)
            else:
                # Save as uncompressed .npy
                filepath = filepath.with_suffix('.npy')
                np.save(filepath, state)
        
        elif format == 'json':
            # Convert numpy arrays to lists for JSON serialization
            json_state = _convert_numpy_to_json(state)
            filepath = filepath.with_suffix('.json')
            
            if compress:
                with gzip.open(filepath.with_suffix('.json.gz'), 'wt') as f:
                    json.dump(json_state, f, indent=2)
                filepath = filepath.with_suffix('.json.gz')
            else:
                with open(filepath, 'w') as f:
                    json.dump(json_state, f, indent=2)
        
        elif format == 'pickle':
            filepath = filepath.with_suffix('.pkl')
            
            if compress:
                with gzip.open(filepath.with_suffix('.pkl.gz'), 'wb') as f:
                    pickle.dump(state, f, protocol=pickle.HIGHEST_PROTOCOL)
                filepath = filepath.with_suffix('.pkl.gz')
            else:
                with open(filepath, 'wb') as f:
                    pickle.dump(state, f, protocol=pickle.HIGHEST_PROTOCOL)
        
        else:
            raise ValueError(f"Unknown format: {format}")
        
        return True
        
    except Exception as e:
        warnings.warn(f"Failed to save state: {e}")
        return False


def load_memory_state(filepath: Union[str, Path],
                     format: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Load holographic memory state from file.
    
    Parameters
    ----------
    filepath : str or Path
        Input file path
    format : str, optional
        File format (auto-detected if None)
        
    Returns
    -------
    Dict[str, Any] or None
        Loaded state dictionary, or None if failed
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        warnings.warn(f"File not found: {filepath}")
        return None
    
    # Auto-detect format if not specified
    if format is None:
        suffix = filepath.suffix.lower()
        if suffix in ['.npy', '.npz']:
            format = 'numpy'
        elif suffix in ['.json', '.gz'] and '.json' in str(filepath):
            format = 'json'
        elif suffix in ['.pkl', '.pickle'] or '.pkl' in str(filepath):
            format = 'pickle'
        else:
            warnings.warn(f"Cannot auto-detect format from {filepath}")
            return None
    
    try:
        if format == 'numpy':
            if filepath.suffix == '.npz':
                # Load from compressed numpy file
                with np.load(filepath, allow_pickle=True) as data:
                    state = dict(data)
                    # Convert single-item arrays back to scalars/objects
                    for key, value in state.items():
                        if isinstance(value, np.ndarray) and value.ndim == 0:
                            state[key] = value.item()
            else:
                # Load from .npy file
                state = np.load(filepath, allow_pickle=True).item()
        
        elif format == 'json':
            if '.gz' in str(filepath):
                with gzip.open(filepath, 'rt') as f:
                    json_state = json.load(f)
            else:
                with open(filepath, 'r') as f:
                    json_state = json.load(f)
            
            # Convert lists back to numpy arrays
            state = _convert_json_to_numpy(json_state)
        
        elif format == 'pickle':
            if '.gz' in str(filepath):
                with gzip.open(filepath, 'rb') as f:
                    state = pickle.load(f)
            else:
                with open(filepath, 'rb') as f:
                    state = pickle.load(f)
        
        else:
            raise ValueError(f"Unknown format: {format}")
        
        return state
        
    except Exception as e:
        warnings.warn(f"Failed to load state: {e}")
        return None


def export_vectors(vectors: Dict[str, np.ndarray],
                  filepath: Union[str, Path],
                  format: str = 'csv',
                  include_metadata: bool = True) -> bool:
    """
    Export vectors to external format.
    
    Parameters
    ----------
    vectors : Dict[str, np.ndarray]
        Dictionary of named vectors
    filepath : str or Path
        Output file path
    format : str, default='csv'
        Export format ('csv', 'txt', 'hdf5')
    include_metadata : bool, default=True
        Whether to include metadata
        
    Returns
    -------
    bool
        True if exported successfully
    """
    filepath = Path(filepath)
    
    try:
        if format == 'csv':
            import pandas as pd
            
            # Create dataframe with vectors as columns
            max_len = max(len(v) for v in vectors.values()) if vectors else 0
            
            data = {}
            for name, vector in vectors.items():
                # Pad shorter vectors with NaN
                padded = np.full(max_len, np.nan)
                padded[:len(vector)] = vector
                data[name] = padded
            
            df = pd.DataFrame(data)
            df.to_csv(filepath.with_suffix('.csv'), index=False)
            
            if include_metadata:
                # Save metadata separately
                metadata = {
                    'n_vectors': len(vectors),
                    'vector_names': list(vectors.keys()),
                    'vector_lengths': {name: len(vec) for name, vec in vectors.items()},
                    'vector_stats': {
                        name: {
                            'mean': float(np.mean(vec)),
                            'std': float(np.std(vec)),
                            'min': float(np.min(vec)),
                            'max': float(np.max(vec))
                        } for name, vec in vectors.items()
                    }
                }
                
                with open(filepath.with_suffix('.json'), 'w') as f:
                    json.dump(metadata, f, indent=2)
        
        elif format == 'txt':
            # Simple text format: one vector per line
            with open(filepath.with_suffix('.txt'), 'w') as f:
                for name, vector in vectors.items():
                    f.write(f"# {name}\n")
                    f.write(" ".join(map(str, vector)) + "\n")
        
        elif format == 'hdf5':
            try:
                import h5py
                
                with h5py.File(filepath.with_suffix('.h5'), 'w') as f:
                    vectors_group = f.create_group('vectors')
                    
                    for name, vector in vectors.items():
                        vectors_group.create_dataset(name, data=vector)
                    
                    if include_metadata:
                        metadata_group = f.create_group('metadata')
                        metadata_group.attrs['n_vectors'] = len(vectors)
                        
                        for name, vector in vectors.items():
                            meta_group = metadata_group.create_group(name)
                            meta_group.attrs['length'] = len(vector)
                            meta_group.attrs['mean'] = np.mean(vector)
                            meta_group.attrs['std'] = np.std(vector)
                            meta_group.attrs['min'] = np.min(vector)
                            meta_group.attrs['max'] = np.max(vector)
            
            except ImportError:
                warnings.warn("h5py not available, cannot export to HDF5")
                return False
        
        else:
            raise ValueError(f"Unknown export format: {format}")
        
        return True
        
    except Exception as e:
        warnings.warn(f"Failed to export vectors: {e}")
        return False


def import_vectors(filepath: Union[str, Path],
                  format: Optional[str] = None) -> Optional[Dict[str, np.ndarray]]:
    """
    Import vectors from external format.
    
    Parameters
    ----------
    filepath : str or Path
        Input file path
    format : str, optional
        File format (auto-detected if None)
        
    Returns
    -------
    Dict[str, np.ndarray] or None
        Dictionary of imported vectors, or None if failed
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        warnings.warn(f"File not found: {filepath}")
        return None
    
    # Auto-detect format
    if format is None:
        suffix = filepath.suffix.lower()
        if suffix == '.csv':
            format = 'csv'
        elif suffix == '.txt':
            format = 'txt'
        elif suffix in ['.h5', '.hdf5']:
            format = 'hdf5'
        else:
            warnings.warn(f"Cannot auto-detect format from {filepath}")
            return None
    
    try:
        if format == 'csv':
            import pandas as pd
            
            df = pd.read_csv(filepath)
            vectors = {}
            
            for col in df.columns:
                # Remove NaN values (padding)
                vector = df[col].dropna().values
                vectors[col] = vector
        
        elif format == 'txt':
            vectors = {}
            current_name = None
            
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('#'):
                        current_name = line[1:].strip()
                    elif line and current_name:
                        vector = np.array([float(x) for x in line.split()])
                        vectors[current_name] = vector
                        current_name = None
        
        elif format == 'hdf5':
            try:
                import h5py
                
                vectors = {}
                with h5py.File(filepath, 'r') as f:
                    if 'vectors' in f:
                        vectors_group = f['vectors']
                        for name, dataset in vectors_group.items():
                            vectors[name] = dataset[:]
                    else:
                        # Assume all datasets are vectors
                        for name, dataset in f.items():
                            if isinstance(dataset, h5py.Dataset):
                                vectors[name] = dataset[:]
            
            except ImportError:
                warnings.warn("h5py not available, cannot import from HDF5")
                return None
        
        else:
            raise ValueError(f"Unknown import format: {format}")
        
        return vectors
        
    except Exception as e:
        warnings.warn(f"Failed to import vectors: {e}")
        return None


def convert_format(input_path: Union[str, Path],
                  output_path: Union[str, Path],
                  input_format: Optional[str] = None,
                  output_format: str = 'numpy') -> bool:
    """
    Convert data between formats.
    
    Parameters
    ----------
    input_path : str or Path
        Input file path
    output_path : str or Path
        Output file path
    input_format : str, optional
        Input format (auto-detected if None)
    output_format : str, default='numpy'
        Output format
        
    Returns
    -------
    bool
        True if converted successfully
    """
    # Load data in input format
    if output_format in ['csv', 'txt', 'hdf5']:
        # Vector export
        vectors = import_vectors(input_path, input_format)
        if vectors is None:
            return False
        return export_vectors(vectors, output_path, output_format)
    
    else:
        # State conversion
        state = load_memory_state(input_path, input_format)
        if state is None:
            return False
        return save_memory_state(state, output_path, output_format)


def compress_data(data: Any, method: str = 'gzip') -> bytes:
    """
    Compress data using specified method.
    
    Parameters
    ----------
    data : Any
        Data to compress
    method : str, default='gzip'
        Compression method
        
    Returns
    -------
    bytes
        Compressed data
    """
    # Serialize data first
    serialized = pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
    
    if method == 'gzip':
        return gzip.compress(serialized)
    else:
        raise ValueError(f"Unknown compression method: {method}")


def decompress_data(compressed_data: bytes, method: str = 'gzip') -> Any:
    """
    Decompress data using specified method.
    
    Parameters
    ----------
    compressed_data : bytes
        Compressed data
    method : str, default='gzip'
        Compression method
        
    Returns
    -------
    Any
        Decompressed data
    """
    if method == 'gzip':
        serialized = gzip.decompress(compressed_data)
    else:
        raise ValueError(f"Unknown compression method: {method}")
    
    return pickle.loads(serialized)


def _convert_numpy_to_json(obj: Any) -> Any:
    """Convert numpy arrays to JSON-serializable format."""
    if isinstance(obj, np.ndarray):
        return {
            '__numpy_array__': True,
            'data': obj.tolist(),
            'dtype': str(obj.dtype),
            'shape': obj.shape
        }
    elif isinstance(obj, np.number):
        return obj.item()
    elif isinstance(obj, dict):
        return {key: _convert_numpy_to_json(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [_convert_numpy_to_json(item) for item in obj]
    else:
        return obj


def _convert_json_to_numpy(obj: Any) -> Any:
    """Convert JSON format back to numpy arrays."""
    if isinstance(obj, dict):
        if obj.get('__numpy_array__'):
            return np.array(obj['data'], dtype=obj['dtype']).reshape(obj['shape'])
        else:
            return {key: _convert_json_to_numpy(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [_convert_json_to_numpy(item) for item in obj]
    else:
        return obj