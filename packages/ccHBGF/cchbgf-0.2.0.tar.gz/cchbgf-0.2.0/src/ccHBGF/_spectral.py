from typing import Literal

import numpy as np
from numpy.typing import NDArray

from sklearn.cluster import KMeans, kmeans_plusplus
from scipy.sparse import diags, linalg

from ._orthogonal import _orthogonalize_centers

from .config import logger

def _spectral_partitioning(adj: NDArray,
                           k: int,
                           tol: float = 0.1,
                           init: Literal['orthogonal', 'kmeans++'] = 'kmeans++',
                           random_state: int | np.random.RandomState | np.random.Generator | None = None
                           ) -> NDArray:
    """
    Perform spectral partitioning of a graph.

    This function performs spectral partitioning of a graph represented by an adjacency matrix.
    It calculates the Laplacian matrix from the adjacency matrix, performs Singular Value
    Decomposition (SVD) of the Laplacian, normalizes the left (U) and right (V) singular vectors to unit
    length, initializes cluster centers using the KMeans++ or orthogonal method, merges the
    singular vector representation of the bipartite graph, and partitions it using KMeans.

    Parameters
    ----------
    adj : ndarray
        Adjacency matrix of the graph.
    k : int
        Number of clusters.
    tol : float, optional
        Tolerance for Singular Value Decomposition (SVD). Default is 0.1.
    init : Literal['orthogonal', 'kmeans++'], optional
        Initialization method for cluster centers. Options are 'orthogonal' or 'kmeans++'. Default is 'kmeans++'.
    random_state : {None, int, numpy.random.Generator, numpy.random.RandomState}, optional
        Random state for reproducibility. Default is None.

    Returns
    -------
    ndarray
        Cluster membership labels.
    """

    # Calculate Laplacian Matrix (L) from A
    D = diags(np.sqrt(adj.sum(axis=0)).A1).tocsc()
    L = adj.dot(linalg.inv(D))

    logger.info(f'Transformed A to Laplacian Matrix (L) of shape {L.shape}')

    # Perform Singular Value Decomposition (SVD)
    U, _, V = linalg.svds(L, min(min(L.shape)-1, k), tol=tol, random_state=random_state)

    logger.info('Decomposed L into Singular Values (SVs)')

    # Normalize left (U) and right (V) SVs to unit vectors
    U = U / np.linalg.norm(U, axis=1, keepdims=True)
    V = V / np.linalg.norm(V, axis=0, keepdims=True)

    logger.info('Normalized SVs')

    if init == 'kmeans++':
        centers, _ = kmeans_plusplus(U, n_clusters=k, random_state=random_state)
        
        logger.info('Initialized Centers')
        
    elif init == 'orthogonal':
        centers, _ = kmeans_plusplus(U, n_clusters=k, random_state=random_state)
        
        logger.info('Initialized Centers')
        
        centers = _orthogonalize_centers(centers)
        
        logger.info('Orthogonalized Centers')


    # Merge SV representation of Bipartite Graph
    n = U.shape[0]
    UVt = np.vstack([U, V.T])

    # KMeans partitioning of Bipartite Graph
    kmeans = KMeans(n_clusters=k, init=centers, random_state=random_state)
    kmeans.fit(UVt)

    logger.info('KMeans model fitted to UVt')

    # Cluster Elements (U)
    membership = kmeans.predict(UVt[:n])

    return membership