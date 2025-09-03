"""
Test configuration and fixtures for tensor_product_binding tests.
Following 2024 pytest best practices.
"""
import pytest
import numpy as np
from typing import Dict, List, Any

# Import the main classes we'll be testing
from src.tensor_product_binding import TensorProductBinding
# Note: create_tpb_system is not available in src module - using direct instantiation


@pytest.fixture(scope="session")
def random_state():
    """Fixed random state for reproducible tests."""
    return np.random.RandomState(42)


@pytest.fixture(scope="module")
def sample_vectors(random_state):
    """Sample vectors for testing binding operations."""
    return {
        'role_vector': random_state.randn(10),
        'filler_vector': random_state.randn(10),
        'context_vector': random_state.randn(10),
        'large_vector': random_state.randn(100),
    }


@pytest.fixture
def tpb_system():
    """Basic TensorProductBinding system for testing."""
    return TensorProductBinding(role_dim=10, filler_dim=10)


@pytest.fixture
def complex_tpb_system():
    """Complex TensorProductBinding system with higher dimensions."""
    return TensorProductBinding(role_dim=50, filler_dim=50)


@pytest.fixture(scope="class")
def binding_test_data():
    """Comprehensive test data for binding operations."""
    np.random.seed(42)  # For reproducibility
    return {
        'roles': {
            'subject': np.random.randn(10),
            'verb': np.random.randn(10), 
            'object': np.random.randn(10),
        },
        'fillers': {
            'john': np.random.randn(10),
            'loves': np.random.randn(10),
            'mary': np.random.randn(10),
        },
        'sentences': [
            {'subject': 'john', 'verb': 'loves', 'object': 'mary'},
            {'subject': 'mary', 'verb': 'loves', 'object': 'john'},
        ]
    }


@pytest.fixture(params=[5, 10, 20, 50])
def vector_dimensions(request):
    """Parametrized fixture for testing different vector dimensions."""
    return request.param


@pytest.fixture(params=[0.1, 0.5, 0.8, 1.0])
def binding_strengths(request):
    """Parametrized fixture for testing different binding strengths."""
    return request.param


@pytest.fixture
def performance_test_data():
    """Large-scale data for performance testing."""
    np.random.seed(42)
    return {
        'large_role_set': [np.random.randn(100) for _ in range(50)],
        'large_filler_set': [np.random.randn(100) for _ in range(50)],
        'batch_size': 1000,
    }


# Pytest hooks for custom test collection and reporting
def pytest_collection_modifyitems(config, items):
    """Add markers to tests based on their names and characteristics."""
    for item in items:
        # Mark slow tests
        if "performance" in item.name or "large" in item.name:
            item.add_marker(pytest.mark.slow)
        
        # Mark integration tests
        if "integration" in item.name or "end_to_end" in item.name:
            item.add_marker(pytest.mark.integration)
        else:
            item.add_marker(pytest.mark.unit)
        
        # Mark parametrized tests
        if hasattr(item, 'pytestmark'):
            for marker in item.pytestmark:
                if marker.name == 'parametrize':
                    item.add_marker(pytest.mark.parametrize)


def pytest_configure(config):
    """Configure pytest with custom settings."""
    # Register custom markers
    config.addinivalue_line(
        "markers", "research_aligned: mark test as validating research paper accuracy"
    )
    config.addinivalue_line(
        "markers", "mathematical: mark test as validating mathematical properties"
    )


@pytest.fixture(autouse=True)
def reset_numpy_state():
    """Automatically reset numpy random state for each test."""
    np.random.seed(None)  # Reset to unpredictable state
    yield
    # Cleanup after test if needed