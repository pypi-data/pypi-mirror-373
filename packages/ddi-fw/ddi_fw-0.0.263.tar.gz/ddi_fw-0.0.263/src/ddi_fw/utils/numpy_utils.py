import numpy as np

def adjust_array_dims(arr, final_ndim=2):
    # Add axes if array has fewer dimensions than final_ndim
    while arr.ndim < final_ndim:
        arr = arr[:, np.newaxis]  # Add a new axis
        
    # Drop axes if array has more dimensions than final_ndim
    while arr.ndim > final_ndim:
        arr = np.squeeze(arr, axis=-1)  # Remove the last axis
    
    return arr



# # Example usage
# arr_1d = np.array([1, 2, 3, 4, 5])

# # Convert to a 3D array (iteratively adds axes)
# arr_3d = adjust_array_dims(arr_1d, final_ndim=3)
# print(arr_3d)
# print("Shape of arr_3d:", arr_3d.shape)

# # Convert to a 2D array (iteratively drops axes)
# arr_2d = adjust_array_dims(arr_3d, final_ndim=2)
# print(arr_2d)
# print("Shape of arr_2d:", arr_2d.shape)