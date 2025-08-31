#!/usr/bin/env python3
"""
Pytest tests to verify HDF5 loading works with h5py.
"""

import os
import pytest
import numpy as np

# Skip all tests if h5py is not available
try:
    import h5py
    H5PY_AVAILABLE = True
except ImportError:
    H5PY_AVAILABLE = False

@pytest.fixture
def sample_data():
    """Fixture providing sample data for testing."""
    return {
        'month': np.array([1, 2, 3, 4, 5]),
        'day_of_month': np.array([1, 15, 20, 25, 30]),
        'ArrDelay': np.array([10, -5, 15, -2, 8]),
        'Year': np.array([2015, 2015, 2015, 2015, 2015])
    }

@pytest.fixture
def advanced_data():
    """Fixture providing advanced test data with different types."""
    return {
        'integers': np.array([1, 2, 3, 4, 5], dtype=np.int32),
        'floats': np.array([1.1, 2.2, 3.3, 4.4, 5.5], dtype=np.float64),
        'strings': np.array(['a', 'b', 'c', 'd', 'e'], dtype='S1'),
        'booleans': np.array([True, False, True, False, True], dtype=np.bool_)
    }

@pytest.fixture
def temp_h5_file():
    """Fixture providing a temporary HDF5 file path."""
    return "test_data.h5"

@pytest.fixture
def temp_advanced_h5_file():
    """Fixture providing a temporary advanced HDF5 file path."""
    return "test_advanced.h5"

@pytest.mark.skipif(not H5PY_AVAILABLE, reason="h5py is not available")
def test_h5py_import():
    """Test that h5py can be imported."""
    import h5py
    assert h5py is not None

@pytest.mark.skipif(not H5PY_AVAILABLE, reason="h5py is not available")
def test_basic_h5py_creation_and_loading(sample_data, temp_h5_file):
    """Test basic h5py file creation and loading."""
    # Create HDF5 file
    with h5py.File(temp_h5_file, 'w') as f:
        for key, value in sample_data.items():
            f.create_dataset(key, data=value)
    
    # Verify file was created
    assert os.path.exists(temp_h5_file)
    
    # Load data from HDF5 file
    with h5py.File(temp_h5_file, 'r') as f:
        columns = list(f.keys())
        data_arrays = {}
        for col in columns:
            data_arrays[col] = f[col][:]
    
    # Verify all data was loaded correctly
    for key, expected_data in sample_data.items():
        assert key in data_arrays
        assert np.array_equal(data_arrays[key], expected_data)
    
    # Clean up
    os.remove(temp_h5_file)

@pytest.mark.skipif(not H5PY_AVAILABLE, reason="h5py is not available")
def test_data_processing_logic(sample_data, temp_h5_file):
    """Test the data processing logic used in the original code."""
    # Create HDF5 file
    with h5py.File(temp_h5_file, 'w') as f:
        for key, value in sample_data.items():
            f.create_dataset(key, data=value)
    
    # Load data
    with h5py.File(temp_h5_file, 'r') as f:
        columns = list(f.keys())
        data_arrays = {}
        for col in columns:
            data_arrays[col] = f[col][:]
    
    # Apply the data processing logic
    if "Year" in data_arrays:
        del data_arrays["Year"]
    
    Yall = data_arrays.pop("ArrDelay").reshape(-1, 1)
    remaining_cols = list(data_arrays.keys())
    Xall = np.column_stack([data_arrays[col] for col in remaining_cols])
    
    # Verify the results
    assert Xall.shape == (5, 2)  # 5 rows, 2 columns (month, day_of_month)
    assert Yall.shape == (5, 1)  # 5 rows, 1 column (ArrDelay)
    assert "Year" not in data_arrays
    assert "ArrDelay" not in data_arrays
    assert len(remaining_cols) == 2
    assert "month" in remaining_cols
    assert "day_of_month" in remaining_cols
    
    # Clean up
    os.remove(temp_h5_file)

@pytest.mark.skipif(not H5PY_AVAILABLE, reason="h5py is not available")
def test_advanced_h5py_features(advanced_data, temp_advanced_h5_file):
    """Test advanced h5py features like groups and attributes."""
    # Create advanced HDF5 file with groups and attributes
    with h5py.File(temp_advanced_h5_file, 'w') as f:
        # Create a group
        group = f.create_group('data')
        
        # Add datasets to the group
        for key, value in advanced_data.items():
            dataset = group.create_dataset(key, data=value)
            # Add attributes to the dataset
            dataset.attrs['description'] = f'Dataset containing {key}'
            dataset.attrs['shape'] = value.shape
            dataset.attrs['dtype'] = str(value.dtype)
        
        # Add global attributes
        f.attrs['created_by'] = 'test_h5py_advanced_features'
        f.attrs['version'] = '1.0'
    
    # Verify file was created
    assert os.path.exists(temp_advanced_h5_file)
    
    # Load and verify the data
    with h5py.File(temp_advanced_h5_file, 'r') as f:
        # Check global attributes
        assert f.attrs['created_by'] == 'test_h5py_advanced_features'
        assert f.attrs['version'] == '1.0'
        
        # Access the group
        group = f['data']
        
        # Load and verify each dataset
        for key, expected_data in advanced_data.items():
            dataset = group[key]
            loaded_data = dataset[:]
            
            # Check data
            assert np.array_equal(loaded_data, expected_data)
            
            # Check attributes
            assert dataset.attrs['description'] == f'Dataset containing {key}'
            assert dataset.attrs['shape'] == expected_data.shape
            assert dataset.attrs['dtype'] == str(expected_data.dtype)
    
    # Clean up
    os.remove(temp_advanced_h5_file)

@pytest.mark.skipif(not H5PY_AVAILABLE, reason="h5py is not available")
def test_h5py_file_structure(sample_data, temp_h5_file):
    """Test HDF5 file structure and metadata."""
    # Create HDF5 file
    with h5py.File(temp_h5_file, 'w') as f:
        for key, value in sample_data.items():
            f.create_dataset(key, data=value)
    
    # Check file structure
    with h5py.File(temp_h5_file, 'r') as f:
        # Check that all expected datasets exist
        for key in sample_data.keys():
            assert key in f
            assert isinstance(f[key], h5py.Dataset)
        
        # Check dataset properties
        for key, expected_data in sample_data.items():
            dataset = f[key]
            assert dataset.shape == expected_data.shape
            assert dataset.dtype == expected_data.dtype
            assert dataset.size == expected_data.size
    
    # Clean up
    os.remove(temp_h5_file)

@pytest.mark.skipif(not H5PY_AVAILABLE, reason="h5py is not available")
def test_h5py_version():
    """Test that h5py version is available and reasonable."""
    import h5py
    version = h5py.version.version
    assert version is not None
    assert isinstance(version, str)
    # Version should be in format like "3.8.0" or "3.9.0"
    assert len(version.split('.')) >= 2

@pytest.mark.skipif(not H5PY_AVAILABLE, reason="h5py is not available")
def test_h5py_hdf5_version():
    """Test that HDF5 version information is available."""
    import h5py
    hdf5_version = h5py.version.hdf5_version
    assert hdf5_version is not None
    assert isinstance(hdf5_version, str)
    # HDF5 version should be in format like "1.12.2" or "1.13.0"
    assert len(hdf5_version.split('.')) >= 2

if __name__ == "__main__":
    # Allow running as script for backward compatibility
    pytest.main([__file__, "-v"]) 