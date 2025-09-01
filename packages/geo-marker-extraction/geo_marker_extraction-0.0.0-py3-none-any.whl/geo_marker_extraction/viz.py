from math import ceil, sqrt

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np


def max_extent(shape: np.ndarray) -> int:
    return max(*shape.shape)


def show_shapes(
    shapes: list[np.ndarray],
    cmap: str = "Greys",
    cmaps: list[str] | None = None,
    shared: bool = False,
    w: int | None = None,
    shuffle: bool = False,
):
    """
    Make a grid of images from a list of shapes

    Parameters
    ----------
    shapes
        list of shapes to display
    cmap
        colormap to use
    cmaps
        list of colormaps to use for each shape
    shared
        whether to share axes
    w
        number of columns
    shuffle
        whether to shuffle the shapes
    """
    if cmaps is None:
        cmaps = [cmap] * len(shapes)
    if w is None:
        w = ceil(sqrt(len(shapes)))
    if shuffle:
        idx = np.random.RandomState(0).permutation(len(shapes))
        shapes = [shapes[i] for i in idx]

    _, axes = plt.subplots(w, w, figsize=(4, 4), sharex=shared, sharey=shared)
    if w == 1:
        axes = np.array([axes])

    for shape, ax, cmap in zip(shapes, axes.ravel(), cmaps, strict=False):
        ax.imshow(shape, cmap=cmap)
    for ax in axes.flat:
        ax.axis("off")
        ax.set_aspect(1)


def show_image(image, ax=None, **kwargs):
    if ax is None:
        ax = plt.gca()
    ax.imshow(image, **kwargs)
    h, w = image.shape[:2]
    ax.axis((0, w, h, 0))
    ax.axis("off")


def transparent_cmap(color) -> mcolors.LinearSegmentedColormap:
    transparent = mcolors.to_rgba("white", alpha=0)  # type: ignore
    return mcolors.LinearSegmentedColormap.from_list("", [transparent, color])


def overlay_components(marker: np.ndarray, components):
    rand = np.random.RandomState(42)
    for component in components:
        rand_colour = rand.rand(3)
        h, w = component.shape.shape
        top_left = component.center - np.array([w, h]) // 2
        plt.imshow(
            component.shape,
            cmap=transparent_cmap(rand_colour),
            alpha=0.7,
            extent=[top_left[0], top_left[0] + w, top_left[1] + h, top_left[1]],  # type: ignore
        )
    plt.imshow(marker, cmap="gray_r", zorder=-1)

    plt.axis("off")
