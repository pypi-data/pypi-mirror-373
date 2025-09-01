from typing import Literal

import numpy as np


def threshold(
    image: np.ndarray,
    amount: float,
    keep: Literal["above", "below"],
    channel: int | None = None,
) -> np.ndarray:
    """
    Threshold the input image, of shape (H, W, 3),
    and return a binary mask of shape (H, W).

    If `channel` is provided, threshold the specified channel.
    Otherwise, threshold the mean of all channels.

    If the image is not normalized to [0, 1], it will be normalized
    before thresholding.
    """
    if not (0 <= amount <= 1):
        raise ValueError("`amount` must be between 0 and 1")
    if not image.ndim == 3:
        raise ValueError("`image` must be a 3D array")

    thing = image[:, :, channel] if channel is not None else image.mean(axis=2)
    if not (thing <= 1).all():
        thing = thing / 255

    if keep == "above":
        return thing > amount
    else:
        return thing < amount
