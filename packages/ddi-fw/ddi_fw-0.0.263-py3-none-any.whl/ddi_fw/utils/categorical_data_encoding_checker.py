import numpy as np

def to_one_hot_encode(arr):
    """
    Convert a multi-dimensional array (1D, 2D, or 3D) into a one-hot encoded array.
    
    Parameters:
    arr (numpy.ndarray): An array where each element or row (or slice) contains class indices or class probabilities.
    
    Returns:
    numpy.ndarray: One-hot encoded array.
    """
    # Check if the input is a numpy array
    if not isinstance(arr, np.ndarray):
        raise ValueError("Input must be a numpy array")

    # Get the shape of the input
    shape = arr.shape
    
    # If the array is 1D, treat it as a list of class indices
    if arr.ndim == 1:
        num_classes = np.max(arr) + 1
        one_hot = np.zeros((shape[0], num_classes))
        one_hot[np.arange(shape[0]), arr] = 1

    # If the array is 2D, treat each row as a list of class indices
    elif arr.ndim == 2:
        num_classes = shape[1]
        one_hot = np.zeros((shape[0], num_classes))
        # Handle one-hot encoding for each row (max index for each row)
        max_indices = np.argmax(arr, axis=1)
        one_hot[np.arange(shape[0]), max_indices] = 1

    # If the array is 3D or higher, iterate over the first axis and apply one-hot encoding for each slice
    elif arr.ndim >= 3:
        num_classes = shape[-1]
        # Initialize the output array for one-hot encoding with the same shape as input, but the last dimension is num_classes
        one_hot = np.zeros_like(arr, dtype=int)
        
        # Iterate through the first axis (the batch dimension)
        for i in range(shape[0]):
            # Get the max indices along the second dimension for each slice
            max_indices = np.argmax(arr[i], axis=1)
            # Set the corresponding one-hot vectors in the slice
            one_hot[i, np.arange(shape[1]), max_indices] = 1

    return one_hot


def is_one_hot_encoded(arr):
    # Check if the array is one-hot encoded
    # Ensure the input is a numpy ndarray and is 2D
    if not isinstance(arr, np.ndarray):
        raise ValueError("Input must be a NumPy ndarray.")
    if not np.all(np.isin(arr, [0, 1])):
        return False
    # Check if each row (or column) has exactly one "1"
    return np.all(np.sum(arr, axis=1) == 1)  # For row-wise checking


def is_binary_encoded(arr):
    # Ensure the input is a numpy ndarray and is 2D
    if not isinstance(arr, np.ndarray):
        raise ValueError("Input must be a NumPy ndarray.")
    if arr.ndim != 2:
        raise ValueError("Input must be a 2D array.")

    # Check if all elements are either 0 or 1
    return np.all(np.isin(arr, [0, 1]))


def is_binary_vector(arr):
    # Ensure the input is a numpy ndarray and is 1D
    if not isinstance(arr, np.ndarray):
        raise ValueError("Input must be a NumPy ndarray.")
    if arr.ndim != 1:
        raise ValueError("Input must be a 1D array.")
    return arr.ndim == 1 and np.all(np.isin(arr, [0, 1]))


def is_label_encoded(arr):
    # Check if the array is label encoded
    # Ensure the input is a numpy ndarray and is 1D
    if not isinstance(arr, np.ndarray):
        raise ValueError("Input must be a NumPy ndarray.")
    if arr.ndim != 1:
        raise ValueError("Input must be a 1D array.")
    
    # Check if all values are non-negative integers (possible class labels)
    return np.issubdtype(arr.dtype, np.integer) and np.all(arr >= 0)