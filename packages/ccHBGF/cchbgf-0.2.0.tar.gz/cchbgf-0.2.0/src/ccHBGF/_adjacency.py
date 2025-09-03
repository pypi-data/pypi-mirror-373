import numpy as np
from numpy.typing import NDArray
from numba import njit

from scipy.sparse import csc_matrix

def _construct_adj_matrix(matrix: NDArray
                          ) -> csc_matrix:
    """
    Construct a sparse adjacency matrix from a clustering matrix.

    This function constructs a sparse adjacency matrix from a clustering matrix, where each column represents
    a clustering solution, and each row represents an element being clustered. It converts each clustering
    solution into a binary matrix and concatenates them horizontally to form the adjacency matrix.

    Parameters
    ----------
    matrix : ndarray
        A 2D array where each column represents a clustering solution, and each row represents an element being clustered.

    Returns
    -------
    csc_matrix
        A sparse adjacency matrix in Compressed Sparse Column (CSC) format.
    """
    
    n, m = matrix.shape
    encoded = np.empty_like(matrix, dtype=np.int64)
    
    #TODO NaN values?
    
    offset = 0
    for i in range(m):
        solution = matrix[:, i]
        unique_labels, encoded_col = np.unique(solution, return_inverse=True)
        encoded[:, i] = encoded_col + offset
        offset += len(unique_labels)
        
    A_rows, A_cols, A_data = _compute_adjacency_coords(encoded)

    A = csc_matrix((A_data, (A_rows, A_cols)),
                   shape=(n, offset),
                   dtype=np.bool_)
    
    return A

    
@njit
def _compute_adjacency_coords(matrix):
    n, m = matrix.shape
    nnz = n * m

    rows = np.empty(nnz, dtype=np.int64)
    cols = np.empty(nnz, dtype=np.int64)
    data = np.ones(nnz, dtype=np.bool_)

    idx = 0
    for j in range(m):
        sol = matrix[:, j]
        for i in range(n):
            rows[idx] = i
            cols[idx] = sol[i]
            idx += 1

    return rows, cols, data


# Legacy Version (Numba independant)
# binary_matrices = []
# for solution in matrix.T:
#     clusters = np.unique(solution)
#     binary_matrix = (solution[:, np.newaxis] == clusters).astype(bool)
#     binary_matrices.append(csc_matrix(binary_matrix, dtype=bool))

# return hstack(binary_matrices, format='csc', dtype=bool)