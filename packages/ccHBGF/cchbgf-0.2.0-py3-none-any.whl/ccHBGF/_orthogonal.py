import numpy as np
from numpy.typing import NDArray

def _orthogonalize_centers(vectors: NDArray
                           ) -> NDArray:
    """
    Perform Modified Gram-Schmidt (MGS) orthogonalization on a set of input vectors.

    MGS is a variant of the Gram-Schmidt process used to orthogonalize a set of vectors.
    Unlike the classical Gram-Schmidt process, MGS calculates all projections before subtracting them,
    which improves numerical stability and reduces round-off errors.

    Parameters
    ----------
    vectors : ndarray
        Input array of shape (m, n), where m is the number of samples (vectors)
        and n is the dimensionality of each vector. Each row represents a vector to be orthogonalized.

    Returns
    -------
    ndarray
        Orthogonalized vectors of the same shape as the input array.
        Each row of the returned array represents an orthogonal vector corresponding to the input vectors.

    Notes
    -----
    The Modified Gram-Schmidt algorithm works by iteratively orthogonalizing the input vectors.
    It subtracts the projections of each vector onto previously orthogonalized vectors.
    The resulting orthogonal vectors are normalized to unit length.
    """
    
    ortho_vectors = np.copy(vectors)
    for i in range(ortho_vectors.shape[0]):
        for j in range(i):
            projection = np.dot(ortho_vectors[i, :], ortho_vectors[j, :])
            ortho_vectors[i, :] -= projection * ortho_vectors[j, :]
        norm = np.linalg.norm(ortho_vectors[i, :])
        if norm != 0:
            ortho_vectors[i, :] /= norm
    return ortho_vectors