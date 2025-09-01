from __future__ import annotations

from collections import namedtuple
from dataclasses import dataclass

import cv2
import networkx as nx
import numpy as np
from jaxtyping import Float, Int
from numpy.typing import NDArray
from rdp import rdp
from scipy.spatial.distance import pdist, squareform


def locate_isolated_shapes(
    image: Float[np.ndarray, "H W"],
    min_size: int = 50,
    padding: int = 1,
    min_aspect_ratio: float = 3,
) -> tuple[list[np.ndarray], np.ndarray]:
    """
    Extract a cropped version of each isolated shape in a
    black and white image (of shape (H, W)), together with
    its center location in the original image.

    Parameters
    ----------
    image
        black and white image of shape (H, W)
    min_size
        minimum size of a shape (in pixel count)
    padding
        padding to add around each shape
    min_aspect_ratio
        minimum aspect ratio of a shape

    Returns
    -------
    shapes
        list of cropped shapes
    centers
        list of centers of the shapes
    """
    contours = cv2.findContours(
        image.astype(np.uint8) * 255,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE,
    )[0]

    shapes = []
    centers = []

    for c in contours:
        x, y = c[:, 0, 0], c[:, 0, 1]
        xmin, xmax = x.min(), x.max()
        ymin, ymax = y.min(), y.max()

        xmin, xmax = (
            max(0, xmin - padding),
            min(image.shape[1], xmax + padding),
        )
        ymin, ymax = (
            max(0, ymin - padding),
            min(image.shape[0], ymax + padding),
        )
        box = image[ymin:ymax, xmin:xmax]

        poly = np.zeros_like(box, dtype=np.uint8)
        cv2.fillPoly(poly, [c - [[xmin, ymin]]], 1)  # type: ignore
        poly = poly.astype(bool)

        shape = box * poly
        w, h = shape.shape
        aspect_ratio = max(w, h) / min(w, h)
        if shape.sum() < min_size and aspect_ratio < min_aspect_ratio:
            continue  # remove very small shapes that aren't lines

        shapes.append(shape)
        centers.append(((xmin + xmax) / 2, (ymin + ymax) / 2))

    centers = np.array(centers)

    return shapes, centers


class BoundingBox:
    def __init__(self, x_lo, y_lo, x_hi, y_hi):
        self.x_lo = x_lo
        self.y_lo = y_lo
        self.x_hi = x_hi
        self.y_hi = y_hi

    def __contains__(self, point: tuple[int, int]) -> bool:
        x, y = point
        return self.x_lo <= x <= self.x_hi and self.y_lo <= y <= self.y_hi

    @property
    def width(self) -> int:
        return self.x_hi - self.x_lo + 1

    @property
    def height(self) -> int:
        return self.y_hi - self.y_lo + 1

    @property
    def center(self) -> Float[NDArray, "2"]:
        return np.array(
            [(self.x_lo + self.x_hi) / 2, (self.y_lo + self.y_hi) / 2]
        )

    @property
    def top_left(self) -> Float[NDArray, "2"]:
        return np.array([self.x_lo, self.y_lo])

    @property
    def bottom_right(self) -> Float[NDArray, "2"]:
        return np.array([self.x_hi, self.y_hi])

    def contains_other(self, other: BoundingBox) -> bool:
        return (
            self.x_lo <= other.x_lo
            and self.x_hi >= other.x_hi
            and self.y_lo <= other.y_lo
            and self.y_hi >= other.y_hi
        )

    @classmethod
    def from_points(cls, points: Float[NDArray, "N 2"]) -> BoundingBox:
        """
        Get the bounding box that contains all the points, assuming
        that each `point` is in the order (x, y)

        Parameters
        ----------
        points
            array of (x, y) tuples

        Returns
        -------
        BoundingBox
            bounding box that contains all the points
        """
        (x_lo, y_lo), (x_hi, y_hi) = [
            np.min(points, axis=0),
            np.max(points, axis=0),
        ]

        return cls(x_lo, y_lo, x_hi, y_hi)

    def index_image(
        self, image: Float[NDArray, "H W ..."]
    ) -> Float[NDArray, "H W ..."]:
        return image[self.y_lo : self.y_hi + 1, self.x_lo : self.x_hi + 1]

    def __repr__(self):
        return f"[[{self.x_lo}, {self.y_lo}],\n [{self.x_hi}, {self.y_hi}]]"


def simplify_line(
    points: Float[NDArray, "N 2"],
    epsilon: float = 1.0,
) -> Float[NDArray, "M 2"]:
    """
    Use the Ramer-Douglas-Peucker algorithm to simplify a list of points,
    reducing the number of points while preserving the shape of the line.

    Parameters
    ----------
    points
        list of (x, y) tuples
    epsilon
        maximum distance between the original line and the simplified line
    """
    return rdp(points, epsilon)  # type: ignore


# TODO: vectorize this function
def sign(value):
    """
    Return the sign of the value:
    * -1 if value is negative
    * 1 if positive
    * 0 if zero
    """
    if value < 0:
        return -1
    elif value > 0:
        return 1
    else:
        return 0


def vector_cross_product(v1, v2):
    """
    Return the 2D cross product of two vectors.
    """
    return v1[0] * v2[1] - v1[1] * v2[0]


def extract_concave_points(
    points: Float[NDArray, "N 2"],
) -> tuple[Float[NDArray, "M 2"], Int[NDArray, "M"]]:
    """
    Extract concave points from a closed contour defined by `points`.

    Parameters
    ----------
    points
        array of (x, y) tuples

    Returns
    -------
    concave_points
        array of (x, y) tuples
    concave_indices
        array of indices of the concave points in the original array
    """
    M = len(points)
    orientation = []
    net_orient = 0

    for i in range(M):
        pcor_i = points[i]
        pcor_i_minus_1 = points[i - 1] if i > 0 else points[-1]
        pcor_i_plus_1 = points[i + 1] if i < M - 1 else points[0]

        Vi = pcor_i - pcor_i_minus_1
        Vi_plus_1 = pcor_i_plus_1 - pcor_i

        orient = sign(vector_cross_product(Vi, Vi_plus_1))
        orientation.append(orient)
        net_orient += orient

    net_orient = sign(net_orient)
    Cconcave = []
    idxs = []
    for i in range(M):
        if orientation[i] != net_orient:
            Cconcave.append(points[i])
            idxs.append(i)

    return np.array(Cconcave), np.array(idxs)


def connect_the_dots(
    contour: Float[NDArray, "N 2"],
    pinch_points: Int[NDArray, "M"],
    max_chord_length: float = 20.0,
    min_loop_length: float = 25.0,
    max_loop_length: float = 200.0,
    ratio_weight: float = 1.0,
    pinch_weight: float = 0.7,
    cost_threshold: float = 1.5,
) -> nx.Graph:
    """
    Split the outline of a compound marker into a connected graph
    where each chordless cycle represents our best guess at an
    atomic component shape.

    Use a cost-function approach to decide which pairs of points
    to connect.

    Parameters
    ----------
    contour
        array of (x, y) tuples representing points along the outline
        of a compound marker
    pinch_points
        array of indices of the pinch points in the original array
    max_chord_length
        maximum length of a chord
    min_loop_length
        minimum length of a loop
    max_loop_length
        maximum length of a loop
    ratio_weight
        weight of the ratio of the chord length to the loop length
    pinch_weight
        weight of the pinch points
    cost_threshold
        maximum cost of an edge

    Returns
    -------
    nx.Graph
        networkx graph representing the compound marker
    """
    G = nx.Graph()

    def is_chord_inside(a: int, b: int) -> bool:
        # Get the midpoint of the chord
        midpoint = (contour[a] + contour[b]) / 2

        # Ray casting algorithm to check if the midpoint is inside the contour
        inside = False
        n = len(contour)
        for i in range(n):
            j = (i + 1) % n
            if (
                (contour[i][1] > midpoint[1]) != (contour[j][1] > midpoint[1])
            ) and (
                midpoint[0]
                < (contour[j][0] - contour[i][0])
                * (midpoint[1] - contour[i][1])
                / (contour[j][1] - contour[i][1])
                + contour[i][0]
            ):
                inside = not inside
        return inside

    def add_edge(a: int, b: int):
        a = a % len(contour)
        b = b % len(contour)
        dist = np.linalg.norm(contour[a] - contour[b])
        G.add_edge(a, b, weight=dist)

    # Add nodes with their positions
    for i, (x, y) in enumerate(contour):
        G.add_node(i, pos=(x, y))
        add_edge(i, i + 1)

    for n in G.nodes:
        G.nodes[n]["pinch"] = False
        G.nodes[n]["usage_count"] = 0
    for n in pinch_points:
        G.nodes[n]["pinch"] = True

    allowed_idxs = list(pinch_points)
    euclidean_distances = squareform(pdist(contour[allowed_idxs]))
    np.fill_diagonal(euclidean_distances, np.inf)

    steps = 0
    MAX_STEPS = 200
    while len(allowed_idxs) > 1 and steps < MAX_STEPS:
        steps += 1
        path_distances = np.zeros_like(euclidean_distances)
        for i, node in enumerate(allowed_idxs):
            for j, node2 in enumerate(allowed_idxs):
                if i != j:
                    path_distances[i, j] = nx.shortest_path_length(
                        G, source=node, target=node2, weight="weight"
                    )

        ratios = euclidean_distances / path_distances

        costs = np.ones_like(ratios) * np.inf
        for i in range(len(allowed_idxs)):
            for j in range(i + 1, len(allowed_idxs)):
                a, b = allowed_idxs[i], allowed_idxs[j]
                ratio = ratios[i, j]
                ratio_cost = ratio_weight * ratios[i, j]
                pinch_cost = pinch_weight * (
                    G.nodes[a]["usage_count"] + G.nodes[b]["usage_count"]
                )

                # set hard rules by keeping costs as inf
                # 1. don't connect adjacent pinch points
                if ratio == 1:
                    continue
                # 2. don't connect pinch points that are not chords
                if not is_chord_inside(a, b):
                    continue
                # 3. don't connect pinch points that are already connected
                if (
                    G.nodes[a]["usage_count"] >= 2
                    or G.nodes[b]["usage_count"] >= 2
                ):
                    continue
                # 4. don't connect pinch points that are too far apart/near
                if not (
                    min_loop_length < path_distances[i, j] < max_loop_length
                ):
                    continue
                # 5. don't connect pinch points that are too far apart
                if euclidean_distances[i, j] > max_chord_length:
                    continue

                costs[i, j] = ratio_cost + pinch_cost

        min_cost = np.min(costs)
        if min_cost > cost_threshold:
            break  # Stop if the minimum cost is above the threshold

        i, j = np.unravel_index(np.argmin(costs), costs.shape)
        a, b = allowed_idxs[i], allowed_idxs[j]

        add_edge(a, b)
        G.nodes[a]["usage_count"] += 1
        G.nodes[b]["usage_count"] += 1

        if G.nodes[a]["usage_count"] >= 2 and a in allowed_idxs:
            i = allowed_idxs.index(a)
            allowed_idxs.remove(a)
            euclidean_distances = np.delete(
                np.delete(euclidean_distances, i, axis=0), i, axis=1
            )
        if G.nodes[b]["usage_count"] >= 2 and b in allowed_idxs:
            j = allowed_idxs.index(b)
            allowed_idxs.remove(b)
            euclidean_distances = np.delete(
                np.delete(euclidean_distances, j, axis=0), j, axis=1
            )

    return G


@dataclass
class Shape:
    bbox: BoundingBox
    pixels: Float[NDArray, "N 2"]
    top_left: Float[NDArray, "2"]


def create_mask(shape, cycle_points):
    mask = np.zeros(shape, dtype=np.uint8)
    cv2.fillPoly(mask, [cycle_points.astype(np.int32)], 255)  # type: ignore
    return mask


Component = namedtuple("Component", ["shape", "center"])


def extract_components(
    compound_marker: Float[NDArray, "H W"],
    base_center: Float[NDArray, "2"] | None = None,
    rdp_epsilon: float = 1.0,
    min_marker_size: int = 20,
) -> list[Component]:
    """
    Extract atomic components from a compound marker.

    Parameters
    ----------
    compound_marker
        image of a compound marker
    base_center
        center of the compound marker
    rdp_epsilon
        epsilon for the RDP algorithm

    Returns
    -------
    list of atomic components
    """
    if compound_marker.ndim != 2:
        raise ValueError("Compound marker must be 2D")

    h, w = compound_marker.shape
    if base_center is None:
        base_center = np.array([w, h]) / 2

    _temp = np.dstack([compound_marker, compound_marker, compound_marker]) * 255

    # 1. find the single contour
    contours, _ = cv2.findContours(
        cv2.cvtColor(_temp, cv2.COLOR_BGR2GRAY),  # type: ignore
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE,
    )
    assert len(contours) == 1
    contour = contours[0].squeeze()

    # 2. simplify the outline, and find the pinch points
    simple_contour = simplify_line(contour, epsilon=rdp_epsilon)
    _, pinch_idxs = extract_concave_points(simple_contour)

    # 3. generate a graph representing the compound marker
    connected_graph = connect_the_dots(
        simple_contour,
        pinch_idxs,
        cost_threshold=1.9,
    )

    # 4. extract all the connected components
    cycles = list(nx.chordless_cycles(connected_graph))  # type: ignore
    shapes: list[Shape] = []
    for cycle in cycles:
        subgraph = connected_graph.subgraph(cycle)
        pos = np.array(list(nx.get_node_attributes(subgraph, "pos").values()))

        bbox = BoundingBox.from_points(pos)

        # Create a mask for the cycle
        cycle_points = pos - bbox.top_left
        mask = create_mask((bbox.height, bbox.width), cycle_points)
        # import matplotlib.pyplot as plt

        # plt.imshow(mask)
        # plt.show()

        # Extract and mask the pixels
        pixels = bbox.index_image(compound_marker).copy()
        pixels[mask == 0] = 0  # Set pixels outside the cycle to white

        if (pixels != 0).sum() < min_marker_size:
            continue

        shapes.append(Shape(bbox, pixels, bbox.top_left))

    # Remove larger bounding boxes that completely encompass another
    shapes_to_keep: list[Shape] = []
    for i, shape in enumerate(shapes):
        is_encompassing = False
        is_too_close = False

        for j, other_shape in enumerate(shapes):
            if i != j and shape.bbox.contains_other(other_shape.bbox):
                is_encompassing = True
                break

        for other_shape in shapes_to_keep:
            if np.linalg.norm(shape.bbox.center - other_shape.bbox.center) < 10:
                is_too_close = True
                break

        if not is_encompassing and not is_too_close:
            shapes_to_keep.append(shape)

    top_left = base_center - np.array([w, h]) / 2

    return [
        Component(
            shape=255 * shape.pixels,
            center=top_left + shape.bbox.center,
        )
        for shape in shapes_to_keep
    ]


def show_graph(G):
    import matplotlib.pyplot as plt

    pos = nx.get_node_attributes(G, "pos")
    nx.draw(G, pos, edge_color="red", node_size=10)
    plt.show()


def resize(img: np.ndarray, n: int = 64) -> np.ndarray:
    """
    1. pad shape with zeros to be square
        (with zeros spaced evenly around the edges)
    2. if smaller than nxn, pad around the edges to be nxn
         otherwise, resize to nxn
    """
    if img.ndim != 2:
        raise ValueError("Image must be 2D")

    h, w = img.shape

    if h > w:
        pad = (h - w) // 2
        img = np.pad(img, ((0, 0), (pad, pad)))  # type: ignore
    elif w > h:
        pad = (w - h) // 2
        img = np.pad(img, ((pad, pad), (0, 0)))  # type: ignore

    # shape is now ~square
    d = img.shape[0]
    if d < n:
        pad = (n - d) // 2
        img = np.pad(img, ((pad, pad), (pad, pad)))

    img = cv2.resize(img.astype(np.uint8), (n, n)).astype(bool)

    return img
