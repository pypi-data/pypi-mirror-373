# `geo-marker-extraction`

This repo contains:
- [source code](src/geo_marker_extraction) for identifying and geo-referencing markers from images of maps
- a [case study](case-study/README.md) of this method applied to a large collection of maps of Africa containing ~150k unique markers

## Installation

To install this Python package, run:

```bash
pip install geo-marker-extraction
```

To run the notebooks in the [case study](case-study/README.md), install with the `demo` extra:

```bash
pip install geo-marker-extraction[demo]
```

## Quick Start

Here's a basic example of how to use the package to extract markers from a map:

```python
import numpy as np
from geo_marker_extraction import maps, markers, separation, viz

# Load your map image (assuming it's a numpy array)
map_image = np.load("your_map.npy")  # or use cv2.imread() for image files

# Separate markers from the map background
marker_mask = separation.threshold(map_image, amount=0.3, keep="below")

# Extract individual marker shapes and their locations
shapes, centers = markers.locate_isolated_shapes(
    marker_mask, 
    min_size=50, 
    padding=2
)

# Visualize the extracted markers
viz.show_shapes(shapes[:16], cmap="Greys", w=4)
```

## Documentation

`geo-marker-extraction` exports several modules:

- `maps`: containing functions for aligning a collection of images of maps to a common reference frame
- `markers` : containing functions for identifying, separating, and locating collections of markers
- `viz`: containing functions for visualizing the results of the marker extraction process
- `clustering`: containing functions for clustering markers into groups
- `separation`: containing functions for separating markers from the map

Below, important functions are documented. For a practical example of how to use this package, see the [case study](case-study/README.md).

### Maps Module (`maps`)

The maps module provides functionality for aligning multiple map images to a common reference frame.

#### `Transform` Class

A named tuple representing an affine transformation with:
- `x`, `y`: Translation offsets in pixels
- `angle`: Rotation angle in degrees
- `scale`: Scale factor

```python
from geo_marker_extraction.maps import Transform

# Create a transformation
transform = Transform(x=10, y=-5, angle=1.5, scale=1.02)

# Apply to an image
transformed_image = transform.apply_to_image(original_image)

# Apply to coordinate points
transformed_points = transform.apply_to_points(points, center=(100, 100))
```

#### `get_transformation(reference_map, processed_map) -> Transform`

Uses Bayesian optimization to find the optimal transformation to align `processed_map` with `reference_map`.

```python
from geo_marker_extraction.maps import get_transformation

# Find transformation to align a map to reference
transform = get_transformation(reference_map, map_to_align)
aligned_map = transform.apply_to_image(map_to_align)
```

#### `optimally_align_all_maps(reference_map, maps) -> tuple[list[Transform], list[np.ndarray]]`

Aligns all maps in a collection to a common reference frame.

```python
from geo_marker_extraction.maps import optimally_align_all_maps

# Align multiple maps to reference
transforms, aligned_maps = optimally_align_all_maps(reference_map, map_collection)
```

### Markers Module (`markers`)

The markers module handles the extraction, analysis, and processing of individual marker shapes.

#### `locate_isolated_shapes(image, min_size=50, padding=1, min_aspect_ratio=3)`

Extracts isolated shapes from a binary image and returns cropped versions with their centers.

**Parameters:**
- `image`: Binary image (H, W) where True/1 indicates marker pixels
- `min_size`: Minimum pixel count for a shape to be considered
- `padding`: Pixels to add around each extracted shape
- `min_aspect_ratio`: Minimum aspect ratio for line-like shapes

**Returns:**
- `shapes`: List of cropped shape arrays
- `centers`: Array of shape center coordinates

```python
from geo_marker_extraction.markers import locate_isolated_shapes

# Extract shapes from marker mask
shapes, centers = locate_isolated_shapes(
    marker_mask, 
    min_size=100, 
    padding=3
)
```

#### `Component` Class

Represents a marker component with shape, center, and bounding box information.

```python
from geo_marker_extraction.markers import Component

# Create component from shape and center
component = Component(shape=marker_shape, center=(x, y))
print(f"Component at {component.center} with area {component.area}")
```

#### `extract_markers_from_image(image, min_size=50, padding=1)`

High-level function to extract all markers from an image.

```python
from geo_marker_extraction.markers import extract_markers_from_image

# Extract all markers from image
markers = extract_markers_from_image(image, min_size=50, padding=2)
```

#### `extract_components(compound_marker, base_center=None, rdp_epsilon=1.0, min_marker_size=20)`

Extracts atomic components from a compound marker by analyzing its contour and identifying connected sub-components.

**Parameters:**
- `compound_marker`: 2D image array of a compound marker (must be 2D)
- `base_center`: Center coordinates of the compound marker (defaults to image center)
- `rdp_epsilon`: Epsilon parameter for the Ramer-Douglas-Peucker line simplification algorithm
- `min_marker_size`: Minimum pixel count for a component to be considered valid

**Returns:**
- List of `Component` objects representing the extracted atomic components

**Algorithm:**
1. Finds the single contour of the compound marker
2. Simplifies the outline using RDP algorithm
3. Identifies pinch points (concave points) in the simplified contour
4. Generates a graph representation of the compound marker
5. Extracts connected components as cycles in the graph
6. Filters out components that are too small or too close to others

```python
from geo_marker_extraction.markers import extract_components

# Extract individual components from a compound marker
components = extract_components(
    compound_marker_image,
    base_center=(100, 150),
    rdp_epsilon=1.5,
    min_marker_size=30
)

# Each component has shape and center attributes
for component in components:
    print(f"Component at {component.center} with area {component.shape.sum()}")
```

### Separation Module (`separation`)

The separation module provides functions to separate markers from map backgrounds.

#### `threshold(image, amount, keep, channel=None)`

Thresholds an image to create a binary mask separating markers from background.

**Parameters:**
- `image`: Input image array (H, W, 3)
- `amount`: Threshold value (0-1)
- `keep`: Either "above" or "below" the threshold
- `channel`: Specific color channel to threshold (None for mean of all channels)

**Returns:**
- Binary mask where True indicates marker pixels

```python
from geo_marker_extraction.separation import threshold

# Separate dark markers from light background
marker_mask = threshold(image, amount=0.4, keep="below")

# Threshold specific color channel
red_markers = threshold(image, amount=0.6, keep="above", channel=0)
```

### Clustering Module (`cluster`)

The clustering module groups similar markers together using unsupervised learning.

#### `cluster_markers(markers, side_length=40, pca_components=10)`

Clusters markers based on shape similarity using PCA and HDBSCAN.

**Parameters:**
- `markers`: List of Component objects
- `side_length`: Size to resize shapes to for comparison
- `pca_components`: Number of PCA components to use for clustering

**Returns:**
- `resized_markers`: List of resized marker shapes
- `pca_embeddings`: PCA-transformed feature vectors
- `pca_model`: Fitted PCA model
- `cluster_labels`: Cluster assignments for each marker

```python
from geo_marker_extraction.cluster import cluster_markers

# Cluster markers by shape similarity
resized, embeddings, pca, labels = cluster_markers(markers, side_length=64)

# Analyze clusters
unique_labels = set(labels)
for label in unique_labels:
    if label != -1:  # -1 indicates noise points
        cluster_markers = [m for m, l in zip(markers, labels) if l == label]
        print(f"Cluster {label}: {len(cluster_markers)} markers")
```

### Visualization Module (`viz`)

The visualization module provides functions for displaying results and intermediate steps.

#### `show_shapes(shapes, cmap="Greys", cmaps=None, shared=False, w=None, shuffle=False)`

Displays a grid of marker shapes for visual inspection.

**Parameters:**
- `shapes`: List of shape arrays to display
- `cmap`: Colormap for all shapes
- `cmaps`: Individual colormaps for each shape
- `shared`: Whether to share axes between subplots
- `w`: Number of columns in the grid
- `shuffle`: Whether to randomize shape order

```python
from geo_marker_extraction.viz import show_shapes

# Display first 16 markers in a 4x4 grid
viz.show_shapes(shapes[:16], cmap="Greys", w=4)

# Display with different colormaps for each shape
viz.show_shapes(shapes, cmaps=["Reds", "Blues", "Greens"] * 10)
```

#### `show_image(image, ax=None, **kwargs)`

Displays a single image with proper axis formatting.

```python
from geo_marker_extraction.viz import show_image

# Display image
viz.show_image(marker_mask, cmap="gray")
```

#### `overlay_components(marker, components)`

Overlays colored component boundaries on a marker image.

```python
from geo_marker_extraction.viz import overlay_components

# Overlay detected components on marker
overlay_components(marker_image, detected_components)
plt.title("Marker with Component Overlay")
plt.show()
```

## Advanced Usage

### Complete Workflow Example

Here's a complete example of processing multiple maps:

```python
import numpy as np
from geo_marker_extraction import maps, markers, separation, cluster, viz

# 1. Load and align maps
reference_map = np.load("reference_map.npy")
map_images = [np.load(f"map_{i}.npy") for i in range(10)]

# Align all maps to reference
transforms, aligned_maps = maps.optimally_align_all_maps(reference_map, map_images)

# 2. Extract markers from each aligned map
all_markers = []
for aligned_map in aligned_maps:
    # Separate markers from background
    marker_mask = separation.threshold(aligned_map, amount=0.3, keep="below")
    
    # Extract individual markers
    shapes, centers = markers.locate_isolated_shapes(marker_mask, min_size=50)
    
    # Convert to Component objects
    map_markers = [markers.Component(shape=s, center=c) for s, c in zip(shapes, centers)]
    all_markers.extend(map_markers)

# 3. Cluster similar markers
resized, embeddings, pca, labels = cluster.cluster_markers(all_markers)

# 4. Analyze results
unique_labels = set(labels)
print(f"Found {len(unique_labels)} marker types:")
for label in unique_labels:
    if label != -1:
        count = sum(1 for l in labels if l == label)
        print(f"  Type {label}: {count} markers")

# 5. Visualize results
viz.show_shapes(resized[:25], w=5, cmap="Greys")
```

### Custom Thresholding Strategies

For different types of maps, you might need custom separation strategies:

```python
# Multi-channel thresholding
def custom_separator(image):
    # Separate by multiple criteria
    dark_mask = separation.threshold(image, 0.3, "below")
    red_mask = separation.threshold(image, 0.6, "above", channel=0)
    
    # Combine masks
    combined = dark_mask | red_mask
    
    # Clean up small noise
    from scipy import ndimage
    cleaned = ndimage.binary_opening(combined, structure=np.ones((3, 3)))
    
    return cleaned

# Use custom separator
marker_mask = custom_separator(map_image)
```


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use this package in your research, please cite:

```bibtex
@software{geo_marker_extraction,
  title={geo-marker-extraction: Extract markers from collections of geo-referenced images},
  author={John Gardner and Harri Ravenscroft},
  year={2024},
  url={https://github.com/jla-gardner/geo-marker-extraction}
}
```

