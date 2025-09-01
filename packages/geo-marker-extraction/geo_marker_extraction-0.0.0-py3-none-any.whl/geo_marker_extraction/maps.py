from __future__ import annotations

from typing import NamedTuple

import cv2
import numpy as np
import optuna
from locache import persist
from optuna import Trial, create_study
from optuna.samplers import TPESampler
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import PolynomialFeatures

optuna.logging.set_verbosity(optuna.logging.WARNING)


class Transform(NamedTuple):
    x: int
    y: int
    angle: float
    scale: float

    def apply_to_image(self, image: np.ndarray) -> np.ndarray:
        # offset
        image = np.roll(image, (self.x, self.y), axis=(0, 1))

        # rotate, scale
        center = tuple(np.array(image.shape) / 2)
        image = cv2.warpAffine(
            image,
            cv2.getRotationMatrix2D(center, self.angle, self.scale),
            image.shape[::-1],
        )

        return image

    def apply_to_points(
        self, points: np.ndarray, center: tuple[int, int]
    ) -> np.ndarray:
        # offset
        points = points + np.array([self.x, self.y])

        # rotate
        angle = np.deg2rad(self.angle)
        rotation_matrix = np.array(
            [[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]]
        )
        points = (points - center) @ rotation_matrix + center

        # scale
        points = points * self.scale

        return points


@persist
def get_transformation(reference_map, processed_map) -> Transform:
    """
    Use bayesian optimization provided by optuna to find the
    optimal transformation to align the processed_map with
    the reference_map
    """

    def target(a, b):
        """
        target function to optimize

        is at a minimum (0) when b is identical to a,
        and increases as the maps become more different
        """
        return 1 - (a * b).sum() / a.sum()

    def objective(trial: Trial):
        x = trial.suggest_int("x", -30, 30)
        y = trial.suggest_int("y", -30, 30)
        angle = trial.suggest_float("angle", -2, 2)
        scale = trial.suggest_float("scale", 0.99, 1.01)
        transform = Transform(x, y, angle, scale)
        transformed = transform.apply_to_image(processed_map)
        return target(reference_map, transformed)

    study = create_study(sampler=TPESampler(seed=5))
    study.optimize(objective, n_trials=50, show_progress_bar=False)
    return Transform(**study.best_params)


def optimally_align_all_maps(
    reference_map: np.ndarray,
    maps: list[np.ndarray],
) -> tuple[list[Transform], list[np.ndarray]]:
    # 1. pad all maps to the same size
    sizes = np.array([map.shape for map in maps] + [reference_map.shape])
    w, h = sizes.max(axis=0)
    resized_maps = [
        np.pad(
            map,
            ((0, w - map.shape[0]), (0, h - map.shape[1])),
            "constant",
            constant_values=0,
        )
        for map in maps
    ]
    reference_map = np.pad(
        reference_map,
        ((0, w - reference_map.shape[0]), (0, h - reference_map.shape[1])),
        "constant",
        constant_values=0,
    )

    # 2. dilate all maps: makes the markings thicker and easier to align
    def dilate(map):
        return cv2.dilate(map, np.ones((3, 3)))

    reference_map = dilate(reference_map)
    resized_maps = [dilate(map) for map in resized_maps]

    # 3. find the optimal transformation for each map
    transformations = [
        get_transformation(reference_map, map) for map in resized_maps
    ]
    aligned_maps = [
        transform.apply_to_image(map)
        for map, transform in zip(resized_maps, transformations, strict=True)
    ]
    return transformations, aligned_maps


def pixel_to_lat_lon_model(
    xy: np.ndarray,
    latlon: np.ndarray,
) -> Pipeline:
    model = make_pipeline(PolynomialFeatures(3), LinearRegression())
    model.fit(xy, latlon)
    return model
