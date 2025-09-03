"""
🧮 Mathematical Utilities for Tensor Product Binding
====================================================

This module provides mathematical utility functions used throughout
the tensor product binding system. It includes numerical operations,
statistical functions, and mathematical transformations.
"""

import numpy as np
from typing import Tuple, Optional, Union
import warnings


def soft_threshold(x: np.ndarray, threshold: float) -> np.ndarray:
    """
    Apply soft thresholding operation.
    
    Soft thresholding: sign(x) * max(0, |x| - threshold)
    
    Parameters
    ----------
    x : np.ndarray
        Input array
    threshold : float
        Threshold value
        
    Returns
    -------
    np.ndarray
        Soft thresholded array
    """
    return np.sign(x) * np.maximum(0, np.abs(x) - threshold)


def gaussian_noise(shape: Union[int, Tuple[int, ...]], 
                  scale: float = 1.0,
                  random_state: Optional[int] = None) -> np.ndarray:
    """
    Generate Gaussian noise with specified scale.
    
    Parameters
    ----------
    shape : int or tuple
        Shape of noise array
    scale : float, default=1.0
        Standard deviation of noise
    random_state : int, optional
        Random seed
        
    Returns
    -------
    np.ndarray
        Gaussian noise array
    """
    if random_state is not None:
        np.random.seed(random_state)
    
    if isinstance(shape, int):
        shape = (shape,)
    
    return np.random.normal(0, scale, shape)


def outer_product_flatten(vec1: np.ndarray, vec2: np.ndarray) -> np.ndarray:
    """
    Compute outer product and flatten to vector.
    
    Parameters
    ----------
    vec1, vec2 : np.ndarray
        Input vectors
        
    Returns
    -------
    np.ndarray
        Flattened outer product
    """
    return np.outer(vec1, vec2).flatten()


def matrix_to_vector(matrix: np.ndarray, order: str = 'C') -> np.ndarray:
    """
    Flatten matrix to vector with specified order.
    
    Parameters
    ----------
    matrix : np.ndarray
        Input matrix
    order : str, default='C'
        Flattening order ('C' for row-major, 'F' for column-major)
        
    Returns
    -------
    np.ndarray
        Flattened vector
    """
    return matrix.flatten(order=order)


def vector_to_matrix(vector: np.ndarray, shape: Tuple[int, int]) -> np.ndarray:
    """
    Reshape vector to matrix with specified shape.
    
    Parameters
    ----------
    vector : np.ndarray
        Input vector
    shape : Tuple[int, int]
        Target matrix shape
        
    Returns
    -------
    np.ndarray
        Reshaped matrix
        
    Raises
    ------
    ValueError
        If vector size doesn't match target shape
    """
    if len(vector) != shape[0] * shape[1]:
        raise ValueError(f"Vector size {len(vector)} doesn't match shape {shape}")
    
    return vector.reshape(shape)


def safe_divide(numerator: np.ndarray, 
               denominator: np.ndarray, 
               eps: float = 1e-12,
               default_value: float = 0.0) -> np.ndarray:
    """
    Safe division with numerical stability.
    
    Parameters
    ----------
    numerator : np.ndarray
        Numerator array
    denominator : np.ndarray
        Denominator array
    eps : float, default=1e-12
        Small epsilon to prevent division by zero
    default_value : float, default=0.0
        Default value when denominator is zero
        
    Returns
    -------
    np.ndarray
        Division result with safe handling of zeros
    """
    # Create mask for small denominators
    small_mask = np.abs(denominator) < eps
    
    # Replace small denominators with eps (or 1 for default_value=0)
    safe_denominator = np.where(small_mask, 
                               1.0 if default_value == 0.0 else eps,
                               denominator)
    
    # Perform division
    result = numerator / safe_denominator
    
    # Apply default value where denominator was small
    result = np.where(small_mask, default_value, result)
    
    return result


def entropy(probabilities: np.ndarray, base: float = 2.0) -> float:
    """
    Calculate entropy of probability distribution.
    
    Parameters
    ----------
    probabilities : np.ndarray
        Probability distribution (should sum to 1)
    base : float, default=2.0
        Logarithm base (2 for bits, e for nats)
        
    Returns
    -------
    float
        Entropy value
    """
    # Remove zero probabilities to avoid log(0)
    p_nonzero = probabilities[probabilities > 0]
    
    if len(p_nonzero) == 0:
        return 0.0
    
    # Calculate entropy
    if base == 2.0:
        log_p = np.log2(p_nonzero)
    elif base == np.e:
        log_p = np.log(p_nonzero)
    else:
        log_p = np.log(p_nonzero) / np.log(base)
    
    return -np.sum(p_nonzero * log_p)


def normalize_probabilities(values: np.ndarray, 
                          temperature: float = 1.0) -> np.ndarray:
    """
    Convert values to normalized probabilities using softmax.
    
    Parameters
    ----------
    values : np.ndarray
        Input values
    temperature : float, default=1.0
        Temperature parameter (lower = more peaked)
        
    Returns
    -------
    np.ndarray
        Normalized probabilities
    """
    if temperature <= 0:
        raise ValueError("Temperature must be positive")
    
    # Apply temperature scaling
    scaled_values = values / temperature
    
    # Numerical stability: subtract max value
    stable_values = scaled_values - np.max(scaled_values)
    
    # Compute softmax
    exp_values = np.exp(stable_values)
    return exp_values / np.sum(exp_values)


def circular_correlation(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """
    Compute circular correlation (inverse of circular convolution).
    
    Parameters
    ----------
    x, y : np.ndarray
        Input vectors (must be same length)
        
    Returns
    -------
    np.ndarray
        Circular correlation result
        
    Raises
    ------
    ValueError
        If vectors have different lengths
    """
    if len(x) != len(y):
        raise ValueError(f"Vector lengths must match: {len(x)} vs {len(y)}")
    
    # FFT-based circular correlation
    x_fft = np.fft.fft(x)
    y_fft = np.fft.fft(y)
    
    # Circular correlation = IFFT(conj(X) * Y)
    correlation_fft = np.conj(x_fft) * y_fft
    
    return np.fft.ifft(correlation_fft).real


def smooth_step(x: np.ndarray, 
               x_min: float = 0.0, 
               x_max: float = 1.0) -> np.ndarray:
    """
    Apply smooth step function (3x² - 2x³) between x_min and x_max.
    
    Parameters
    ----------
    x : np.ndarray
        Input values
    x_min : float, default=0.0
        Lower bound
    x_max : float, default=1.0
        Upper bound
        
    Returns
    -------
    np.ndarray
        Smoothed values between 0 and 1
    """
    if x_max <= x_min:
        raise ValueError("x_max must be greater than x_min")
    
    # Normalize to [0, 1]
    t = np.clip((x - x_min) / (x_max - x_min), 0.0, 1.0)
    
    # Apply smooth step function
    return t * t * (3.0 - 2.0 * t)


def logistic_sigmoid(x: np.ndarray, 
                    steepness: float = 1.0, 
                    midpoint: float = 0.0) -> np.ndarray:
    """
    Apply logistic sigmoid function.
    
    Parameters
    ----------
    x : np.ndarray
        Input values
    steepness : float, default=1.0
        Steepness parameter (higher = steeper)
    midpoint : float, default=0.0
        Midpoint of sigmoid
        
    Returns
    -------
    np.ndarray
        Sigmoid values between 0 and 1
    """
    # Prevent overflow for very negative values
    shifted_x = steepness * (x - midpoint)
    return 1.0 / (1.0 + np.exp(-np.clip(shifted_x, -500, 500)))


def mutual_information(x: np.ndarray, y: np.ndarray, bins: int = 10) -> float:
    """
    Estimate mutual information between two variables.
    
    Parameters
    ----------
    x, y : np.ndarray
        Input variables
    bins : int, default=10
        Number of histogram bins
        
    Returns
    -------
    float
        Mutual information estimate
    """
    # Create 2D histogram
    hist_2d, _, _ = np.histogram2d(x, y, bins=bins)
    
    # Convert to probabilities
    p_xy = hist_2d / np.sum(hist_2d)
    
    # Marginal probabilities
    p_x = np.sum(p_xy, axis=1)
    p_y = np.sum(p_xy, axis=0)
    
    # Calculate mutual information
    mi = 0.0
    for i in range(len(p_x)):
        for j in range(len(p_y)):
            if p_xy[i, j] > 0 and p_x[i] > 0 and p_y[j] > 0:
                mi += p_xy[i, j] * np.log2(p_xy[i, j] / (p_x[i] * p_y[j]))
    
    return mi


def robust_mean(x: np.ndarray, trim_percentage: float = 10.0) -> float:
    """
    Calculate robust mean by trimming outliers.
    
    Parameters
    ----------
    x : np.ndarray
        Input array
    trim_percentage : float, default=10.0
        Percentage of data to trim from each end
        
    Returns
    -------
    float
        Robust mean
    """
    if not 0 <= trim_percentage < 50:
        raise ValueError("trim_percentage must be between 0 and 50")
    
    if trim_percentage == 0:
        return np.mean(x)
    
    # Sort array
    sorted_x = np.sort(x)
    n = len(sorted_x)
    
    # Calculate trim indices
    trim_count = int(np.round(n * trim_percentage / 100))
    
    if trim_count >= n // 2:
        warnings.warn("Trim percentage too high, using median")
        return np.median(x)
    
    # Return mean of central portion
    if trim_count > 0:
        return np.mean(sorted_x[trim_count:-trim_count])
    else:
        return np.mean(sorted_x)