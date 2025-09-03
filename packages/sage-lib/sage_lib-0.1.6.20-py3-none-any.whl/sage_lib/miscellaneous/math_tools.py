import numpy as np

def normalize_matrix_to_doubly_stochastic(matrix: np.ndarray, tol: float = 1e-9, max_iter: int = 1000) -> np.ndarray:
    """
    Normalize a matrix so that each row and column sums to 1 using the Sinkhorn-Knopp algorithm.

    Args:
        matrix (np.ndarray): The input non-negative matrix to be normalized.
        tol (float): Tolerance for convergence.

    Returns:
        np.ndarray: The normalized doubly stochastic matrix.
    """

    # Ensure matrix is non-negative
    if np.any(matrix < 0):
        raise ValueError(" Sinkhorn-Knopp algorithm : Matrix must have non-negative elements for normalization.")

    # Convert the matrix to float for division operations
    mat = matrix.astype(np.float64)

    # Iteratively scale rows and columns
    for _ in range(max_iter):
        # Normalize rows
        mat /= mat.sum(axis=1, keepdims=True)

        # Normalize columns
        mat /= mat.sum(axis=0, keepdims=True)

        # Check for convergence
        if np.all(np.abs(mat.sum(axis=1) - 1) < tol) and np.all(np.abs(mat.sum(axis=0) - 1) < tol):
            break

    return mat


def efficient_vectorized_permutations(X, n_permutations):
    """
    Perform a specified number of element swaps within a matrix in a vectorized and efficient manner.

    This function carries out multiple pairwise permutations of elements within a 2D numpy array.
    Each permutation consists of swapping two elements, and these swaps are executed in a single vectorized operation.

    Parameters:
    - X (np.ndarray): A 2D numpy array whose elements are to be permuted.
    - n_permutations (int): The number of element swaps to perform.

    Returns:
    - np.ndarray: The modified array with the specified number of elements permuted.
    
    Mathematical Details:
    - Let X be a matrix with dimensions rows x cols.
    - The number of elements in X is rows * cols.
    - The function randomly selects 2 * n_permutations indices from this range, ensuring that each pair can be swapped.
    - The selected indices are converted from a flat index to a 2D index (row, column) to identify exact positions in X for swapping.
    """

    # Get the dimensions of the matrix
    rows, cols = X.shape
    n_elements = rows * cols  # Total number of elements in the matrix

    # Generate a flat array of randomly permuted indices and select the first 2 * n_permutations indices
    indices = np.random.permutation(n_elements)[:np.min([n_elements, 2*n_permutations])].reshape(-1, 2)

    # Extract pairs of indices to be swapped
    idx1, idx2 = indices[:, 0], indices[:, 1]

    # Convert flat indices to 2D indices using the matrix dimensions
    r1, c1 = np.unravel_index(idx1, (rows, cols))
    r2, c2 = np.unravel_index(idx2, (rows, cols))

    # Perform the swap operation in a vectorized manner without looping
    X[r1, c1], X[r2, c2] = X[r2, c2].copy(), X[r1, c1].copy()

    return X