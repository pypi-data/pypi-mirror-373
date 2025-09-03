"""
💾 Data Utilities for Tensor Product Binding
============================================

This module provides utilities for saving, loading, and converting
data in the tensor product binding system. It includes serialization,
file I/O, and data format conversion functions.
"""

import json
import pickle
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import numpy as np
import warnings

from ..config.config_classes import TensorBindingConfig
from ..core.binding_operations import TPBVector


def save_binding_state(vectors: Dict[str, Any],
                      filepath: Union[str, Path],
                      format: str = 'npz') -> bool:
    """
    Save binding state (vectors and metadata) to file.
    
    Parameters
    ----------
    vectors : Dict[str, Any]
        Dictionary containing vectors and metadata
    filepath : str or Path
        Output file path
    format : str, default='npz'
        Save format ('npz', 'pickle', 'json')
        
    Returns
    -------
    bool
        True if successful
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        if format == 'npz':
            # Convert TPBVector objects to arrays for npz
            arrays_dict = {}
            metadata_dict = {}
            
            for name, vector in vectors.items():
                if isinstance(vector, TPBVector):
                    arrays_dict[f"{name}_data"] = vector.data
                    metadata_dict[name] = {
                        'role': vector.role,
                        'filler': vector.filler,
                        'is_bound': vector.is_bound,
                        'binding_info': vector.binding_info
                    }
                elif isinstance(vector, np.ndarray):
                    arrays_dict[name] = vector
                else:
                    metadata_dict[name] = vector
            
            # Save arrays and metadata separately
            np.savez_compressed(filepath.with_suffix('.npz'), **arrays_dict)
            
            if metadata_dict:
                with open(filepath.with_suffix('.json'), 'w') as f:
                    json.dump(metadata_dict, f, indent=2, default=str)
        
        elif format == 'pickle':
            with open(filepath.with_suffix('.pkl'), 'wb') as f:
                pickle.dump(vectors, f, protocol=pickle.HIGHEST_PROTOCOL)
        
        elif format == 'json':
            # Convert numpy arrays to lists for JSON
            json_dict = {}
            for name, vector in vectors.items():
                if isinstance(vector, TPBVector):
                    json_dict[name] = {
                        'data': vector.data.tolist(),
                        'role': vector.role,
                        'filler': vector.filler,
                        'is_bound': vector.is_bound,
                        'binding_info': vector.binding_info
                    }
                elif isinstance(vector, np.ndarray):
                    json_dict[name] = vector.tolist()
                else:
                    json_dict[name] = vector
            
            with open(filepath.with_suffix('.json'), 'w') as f:
                json.dump(json_dict, f, indent=2, default=str)
        
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        return True
        
    except Exception as e:
        warnings.warn(f"Failed to save binding state: {e}")
        return False


def load_binding_state(filepath: Union[str, Path],
                      format: str = 'auto') -> Optional[Dict[str, Any]]:
    """
    Load binding state from file.
    
    Parameters
    ----------
    filepath : str or Path
        Input file path
    format : str, default='auto'
        Load format ('npz', 'pickle', 'json', 'auto')
        
    Returns
    -------
    Dict[str, Any] or None
        Loaded vectors and metadata, or None if failed
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        warnings.warn(f"File not found: {filepath}")
        return None
    
    # Auto-detect format from extension
    if format == 'auto':
        ext = filepath.suffix.lower()
        if ext == '.npz':
            format = 'npz'
        elif ext == '.pkl':
            format = 'pickle'
        elif ext == '.json':
            format = 'json'
        else:
            warnings.warn(f"Unknown file extension: {ext}")
            return None
    
    try:
        if format == 'npz':
            result = {}
            
            # Load arrays
            with np.load(filepath) as data:
                for name in data.files:
                    result[name] = data[name]
            
            # Load metadata if exists
            metadata_file = filepath.with_suffix('.json')
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                
                # Reconstruct TPBVector objects
                for name, meta in metadata.items():
                    if isinstance(meta, dict) and 'role' in meta:
                        data_key = f"{name}_data"
                        if data_key in result:
                            result[name] = TPBVector(
                                data=result[data_key],
                                role=meta.get('role'),
                                filler=meta.get('filler'),
                                is_bound=meta.get('is_bound', False),
                                binding_info=meta.get('binding_info', {})
                            )
                            del result[data_key]  # Remove raw data
                    else:
                        result[name] = meta
        
        elif format == 'pickle':
            with open(filepath, 'rb') as f:
                result = pickle.load(f)
        
        elif format == 'json':
            with open(filepath, 'r') as f:
                json_dict = json.load(f)
            
            result = {}
            for name, value in json_dict.items():
                if isinstance(value, dict) and 'data' in value:
                    # Reconstruct TPBVector
                    result[name] = TPBVector(
                        data=np.array(value['data']),
                        role=value.get('role'),
                        filler=value.get('filler'),
                        is_bound=value.get('is_bound', False),
                        binding_info=value.get('binding_info', {})
                    )
                elif isinstance(value, list):
                    result[name] = np.array(value)
                else:
                    result[name] = value
        
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        return result
        
    except Exception as e:
        warnings.warn(f"Failed to load binding state: {e}")
        return None


def export_vectors_csv(vectors: Dict[str, np.ndarray],
                      filepath: Union[str, Path],
                      include_metadata: bool = True) -> bool:
    """
    Export vectors to CSV format.
    
    Parameters
    ----------
    vectors : Dict[str, np.ndarray]
        Dictionary of named vectors
    filepath : str or Path
        Output CSV file path
    include_metadata : bool, default=True
        Include vector metadata as additional columns
        
    Returns
    -------
    bool
        True if successful
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Determine maximum vector dimension
            max_dim = max(len(vec) if isinstance(vec, np.ndarray) else len(vec.data) 
                         for vec in vectors.values())
            
            # Write header
            header = ['name']
            if include_metadata:
                header.extend(['dimension', 'norm', 'type'])
            header.extend([f'dim_{i}' for i in range(max_dim)])
            writer.writerow(header)
            
            # Write vectors
            for name, vector in vectors.items():
                if isinstance(vector, TPBVector):
                    data = vector.data
                    vector_type = 'TPBVector'
                elif isinstance(vector, np.ndarray):
                    data = vector
                    vector_type = 'ndarray'
                else:
                    continue  # Skip non-vector data
                
                row = [name]
                
                if include_metadata:
                    row.extend([len(data), np.linalg.norm(data), vector_type])
                
                # Pad or truncate to max_dim
                padded_data = np.zeros(max_dim)
                padded_data[:len(data)] = data
                row.extend(padded_data.tolist())
                
                writer.writerow(row)
        
        return True
        
    except Exception as e:
        warnings.warn(f"Failed to export vectors to CSV: {e}")
        return False


def import_vectors_csv(filepath: Union[str, Path]) -> Optional[Dict[str, np.ndarray]]:
    """
    Import vectors from CSV format.
    
    Parameters
    ----------
    filepath : str or Path
        Input CSV file path
        
    Returns
    -------
    Dict[str, np.ndarray] or None
        Dictionary of imported vectors, or None if failed
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        warnings.warn(f"File not found: {filepath}")
        return None
    
    try:
        vectors = {}
        
        with open(filepath, 'r') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)
            
            # Find data columns (start after metadata)
            data_start_idx = 1
            if 'dimension' in header:
                data_start_idx = header.index('dimension') + 3  # name, dim, norm, type
            
            for row in reader:
                name = row[0]
                
                # Extract vector data
                data = [float(x) for x in row[data_start_idx:]]
                vector = np.array(data)
                
                # Remove padding zeros if dimension info available
                if 'dimension' in header:
                    actual_dim = int(row[1])
                    vector = vector[:actual_dim]
                
                vectors[name] = vector
        
        return vectors
        
    except Exception as e:
        warnings.warn(f"Failed to import vectors from CSV: {e}")
        return None


def serialize_config(config: TensorBindingConfig) -> str:
    """
    Serialize configuration to JSON string.
    
    Parameters
    ----------
    config : TensorBindingConfig
        Configuration to serialize
        
    Returns
    -------
    str
        JSON string representation
    """
    try:
        # Convert to dictionary
        config_dict = {
            'vector_dim': config.vector_dim,
            'binding_method': config.binding_method.value,
            'binding_operation': config.binding_operation.value,
            'unbinding_method': config.unbinding_method.value,
            'enable_binding_strength': config.enable_binding_strength,
            'default_binding_strength': config.default_binding_strength,
            'strength_decay_factor': config.strength_decay_factor,
            'normalize_bindings': config.normalize_bindings,
            'context_window_size': config.context_window_size,
            'context_sensitivity': config.context_sensitivity,
            'enable_role_ambiguity_resolution': config.enable_role_ambiguity_resolution,
            'max_recursion_depth': config.max_recursion_depth,
            'recursive_strength_decay': config.recursive_strength_decay,
            'enable_hierarchical_unbinding': config.enable_hierarchical_unbinding,
            'enable_variable_dimensions': config.enable_variable_dimensions,
            'role_dimension_map': config.role_dimension_map,
            'filler_dimension_map': config.filler_dimension_map,
            'max_unbinding_iterations': config.max_unbinding_iterations,
            'unbinding_tolerance': config.unbinding_tolerance,
            'enable_symbolic_reasoning': config.enable_symbolic_reasoning,
            'enable_compositional_semantics': config.enable_compositional_semantics,
            'enable_structure_preservation': config.enable_structure_preservation
        }
        
        return json.dumps(config_dict, indent=2)
        
    except Exception as e:
        warnings.warn(f"Failed to serialize config: {e}")
        return "{}"


def deserialize_config(json_str: str) -> Optional[TensorBindingConfig]:
    """
    Deserialize configuration from JSON string.
    
    Parameters
    ----------
    json_str : str
        JSON string representation
        
    Returns
    -------
    TensorBindingConfig or None
        Deserialized configuration, or None if failed
    """
    try:
        from ..config.enums import BindingMethod, BindingOperation, UnbindingMethod
        from ..config.config_classes import TensorBindingConfig
        
        config_dict = json.loads(json_str)
        
        # Convert enum strings back to enums
        if 'binding_method' in config_dict:
            config_dict['binding_method'] = BindingMethod(config_dict['binding_method'])
        
        if 'binding_operation' in config_dict:
            config_dict['binding_operation'] = BindingOperation(config_dict['binding_operation'])
        
        if 'unbinding_method' in config_dict:
            config_dict['unbinding_method'] = UnbindingMethod(config_dict['unbinding_method'])
        
        return TensorBindingConfig(**config_dict)
        
    except Exception as e:
        warnings.warn(f"Failed to deserialize config: {e}")
        return None


def create_backup(vectors: Dict[str, Any],
                 backup_dir: Union[str, Path] = "backups") -> Optional[Path]:
    """
    Create timestamped backup of binding state.
    
    Parameters
    ----------
    vectors : Dict[str, Any]
        Vectors to backup
    backup_dir : str or Path, default="backups"
        Backup directory
        
    Returns
    -------
    Path or None
        Path to backup file, or None if failed
    """
    import datetime
    
    backup_dir = Path(backup_dir)
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"tpb_backup_{timestamp}.npz"
    
    if save_binding_state(vectors, backup_file, format='npz'):
        return backup_file
    else:
        return None


def list_backups(backup_dir: Union[str, Path] = "backups") -> List[Path]:
    """
    List available backup files.
    
    Parameters
    ----------
    backup_dir : str or Path, default="backups"
        Backup directory
        
    Returns
    -------
    List[Path]
        List of backup file paths, sorted by modification time
    """
    backup_dir = Path(backup_dir)
    
    if not backup_dir.exists():
        return []
    
    backup_files = list(backup_dir.glob("tpb_backup_*.npz"))
    
    # Sort by modification time (newest first)
    backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    return backup_files