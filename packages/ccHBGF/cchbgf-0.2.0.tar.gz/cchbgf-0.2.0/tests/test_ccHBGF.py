import numpy as np
import pytest

from ccHBGF import find_consensus

@pytest.fixture
def sample_clustering_matrix():
    """Fixture to provide a sample clustering matrix for testing."""
    return np.array([
        [0, 1, 2],
        [1, 1, 2],
        [0, 2, 1],
        [2, 0, 1],
        [1, 0, 0]
    ])

def test_default_parameters(sample_clustering_matrix):
    """Test ccHBGF with default parameters."""
    labels = find_consensus(sample_clustering_matrix)
    assert labels.ndim == 1, "Output should be a 1D array."
    assert labels.size == sample_clustering_matrix.shape[0], "Output size should match the number of rows in the clustering matrix."

def test_specified_n_clusters(sample_clustering_matrix):
    """Test ccHBGF with a specified number of clusters."""
    labels = find_consensus(sample_clustering_matrix, n_clusters=3)
    assert len(np.unique(labels)) == 3, "Output should have exactly 3 clusters."

def test_invalid_init_method(sample_clustering_matrix):
    """Test ccHBGF with an invalid init method."""
    with pytest.raises(AssertionError, match="No center initialization method"):
        find_consensus(sample_clustering_matrix, init='invalid_method')

def test_reproducibility(sample_clustering_matrix):
    """Test reproducibility of the clustering with a fixed random_state."""
    random_state = 42
    labels1 = find_consensus(sample_clustering_matrix, random_state=random_state)
    labels2 = find_consensus(sample_clustering_matrix, random_state=random_state)
    assert np.array_equal(labels1, labels2), "Clustering should be reproducible with the same random_state."

def test_single_cluster_detected():
    """Test ccHBGF behavior when only one cluster is detected."""
    clustering_matrix = np.ones((5, 3))  # All elements belong to one cluster
    labels = find_consensus(clustering_matrix)
    assert np.all(labels == 0), "All labels should be zero when only one cluster is detected."

def test_tolerance_effect(sample_clustering_matrix):
    """Test the effect of different tolerances on the output."""
    labels_low_tol = find_consensus(sample_clustering_matrix, tol=0.01)
    labels_high_tol = find_consensus(sample_clustering_matrix, tol=0.5)
    assert labels_low_tol.size == labels_high_tol.size, "Tolerance change should not affect the size of the output."

# def test_verbose_output(sample_clustering_matrix, capsys):
#     """Test verbose output."""
#     ccHBGF(sample_clustering_matrix, verbose=True)
#     captured = capsys.readouterr()
#     assert "Detected" in captured.out, "Verbose output should include information about the number of clusters."
