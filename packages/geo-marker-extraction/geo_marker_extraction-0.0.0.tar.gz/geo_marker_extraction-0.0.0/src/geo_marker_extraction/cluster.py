import cv2
import numpy as np
from sklearn.cluster import HDBSCAN  # type: ignore
from sklearn.decomposition import PCA

from .markers import Component


def resize_shape(shape, n=64):
    """
    1. pad shape with zeros to be square
        (with zeros spaced evenly around the edges)
    2. if smaller than nxn, pad around the edges to be nxn
         otherwise, resize to nxn
    """
    h, w = shape.shape

    if h > w:
        pad = (h - w) // 2
        shape = np.pad(shape, ((0, 0), (pad, pad)))  # type: ignore
    elif w > h:
        pad = (w - h) // 2
        shape = np.pad(shape, ((pad, pad), (0, 0)))  # type: ignore

    # shape is now ~square
    d = shape.shape[0]
    if d < n:
        pad = (n - d) // 2
        shape = np.pad(shape, ((pad, pad), (pad, pad)))

    shape = cv2.resize(shape.astype(np.uint8), (n, n)).astype(bool)

    return shape


def cluster_markers(
    markers: list[Component],
    side_length: int = 40,
    pca_components: int = 10,
) -> tuple[list[np.ndarray], np.ndarray, PCA, np.ndarray]:
    # 1. resize
    resized_markers = [
        resize_shape(marker.shape, side_length) for marker in markers
    ]

    # 2. flatten
    flattened = np.array([marker.flatten() for marker in resized_markers])

    # 3. PCA
    pca = PCA(n_components=50)
    pca_emb = pca.fit_transform(flattened)

    # 4. clustering
    clusterer = HDBSCAN(
        min_cluster_size=30,
        min_samples=10,
        store_centers="both",
        cluster_selection_epsilon=0.4,
    )
    clusterer.fit(pca_emb[:, :pca_components])

    return (resized_markers, pca_emb, pca, clusterer.labels_)
