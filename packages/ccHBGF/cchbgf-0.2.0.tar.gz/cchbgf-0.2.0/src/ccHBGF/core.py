from typing import Literal

import numpy as np
from numpy.typing import NDArray

from ._adjacency import _construct_adj_matrix
from ._spectral import _spectral_partitioning

from .config import logger

def find_consensus(clustering_matrix: NDArray,
           n_clusters: int | None = None,
           tol: float = 0.1,
           init: Literal['orthogonal', 'kmeans++'] = 'orthogonal',
           random_state: int | np.random.RandomState | np.random.Generator | None = None,
           verbose: bool = False # deprecated, kept for backwards compatability
           ) -> NDArray:
    """
    Perform consensus clustering using Hybrid Bipartite Graph Formulation (HBGF).

    This function performs consensus clustering on a `clustering_matrix`, which is a 2D array where each column
    represents a clustering solution and each row represents an element being clustered. It constructs a bipartite
    graph with vertices representing the clusters and elements, and then partitions the graph using spectral
    partitioning to generate final cluster labels.

    Parameters
    ----------
    clustering_matrix : ndarray
        A 2D array where each column represents a clustering solution, and each row represents an element being clustered.

    n_clusters : int, optional
        The number of clusters. If not provided, the function automatically detects the number of clusters.

    tol : float, optional
        The tolerance for scipy.sparse.linalg.svds(), where `0` is machine precision.

    init : {'orthogonal', 'kmeans++'}, optional
        Method for initializing KMeans centers. Default is 'orthogonal'.

    random_state : {int, numpy.random.Generator, numpy.random.RandomState}, optional
        Controls the randomness of the algorithm for reproducibility. Default is None.

    Returns
    -------
    ndarray
        A 1D array of consensus clustering labels for the elements.
    """

    # Check Input Parameters
    assert init in ['orthogonal', 'kmeans++'], f"No center initialization method: {init}.\nAvailable methods:\n\t- 'orthogonal'\n\t- 'kmeans++'"

    # Define expected number of clusters, if not given
    if not n_clusters:
        n_clusters = int(np.max(np.apply_along_axis(lambda x: np.unique(x).size, 0, clustering_matrix)))
        if n_clusters == 1:
            logger.info('Only 1 cluster detected.')
            return np.zeros(shape=clustering_matrix.shape[0])

    logger.info(f'Detected {n_clusters} clusters.')

    if n_clusters > 500:
        logger.warning(f'Large numbers of clusters detected ({n_clusters}!). This may take a while.')

    # Construct graph adjacency matrix (A)
    A = _construct_adj_matrix(clustering_matrix)

    logger.info(f'Graph adjacency matrix (A) constructed with shape {A.shape}')

    # Derive cluster labels using spectral partitioning of graph
    cluster_labels = _spectral_partitioning(A, n_clusters, tol, init, random_state)

    logger.info('Consensus Labels Found')

    return cluster_labels

ccHBGF = find_consensus