# Heart Tissue Tensor Analysis Streamtube Visualization

This repository contains code for visualizing tensor analysis of heart tissue using streamtubes. The visualization uses Fractional Anisotropy (FA) values as a color scale to represent the degree of anisotropy in the tissue.

## Overview

The code reads:
- A pickle file containing a DataFrame with eigenvalues, eigenvectors, and FA values
- A multiframe TIFF file with the original 3D image data

And produces 3D streamtube visualizations where:
- Streamtubes follow the principal eigenvector directions
- Colors represent FA values (typically 0-1 range)
- Multiple visualization backends are supported (PyVista and Plotly)

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Data Format

### Pickle File (DataFrame)
The pickle file should contain a pandas DataFrame with the following columns:
- Coordinates: `x`, `y`, `z` (or `i`, `j`, `k`)
- Principal eigenvector components: `evec1_x`, `evec1_y`, `evec1_z`
- FA values: `FA` (or column containing "fractional" or "fa")

### TIFF File
A multiframe TIFF file containing the 3D image stack.

## Quick Start (Heart Tissue Dataset)

For the tomo (44B-T2)-256-cropped dataset, use the dedicated quick-start script:

```bash
# Interactive mode - choose visualization method
python visualize_heart_tissue.py

# Direct PyVista visualization
python visualize_heart_tissue.py --pyvista

# Direct Plotly visualization
python visualize_heart_tissue.py --plotly
```

**Note**: Update the file paths at the top of `visualize_heart_tissue.py` if your files are in different locations.

### Inspect Your Data

To examine the structure of your pickle file before visualization:

```bash
python inspect_pickle_data.py '/Users/asvetlove/Downloads/tomo (44B-T2)-256-cropped_df.pkl'
```

This will show you all column names, data types, and help identify any issues.

## Usage

### Command Line

```bash
# Using PyVista (recommended for high-quality visualization)
python streamtube_visualization.py tensor_data.pkl image_data.tif --method pyvista

# Using Plotly (interactive web-based)
python streamtube_visualization.py tensor_data.pkl image_data.tif --method plotly

# Using Plotly cone glyphs (alternative visualization)
python streamtube_visualization.py tensor_data.pkl image_data.tif --method plotly-cone

# With subsampling for better performance
python streamtube_visualization.py tensor_data.pkl image_data.tif --subsample 2 --method pyvista

# Adjust visualization parameters
python streamtube_visualization.py tensor_data.pkl image_data.tif \
    --method pyvista \
    --streamline-length 30.0 \
    --tube-radius 0.8
```

### Python API

```python
from streamtube_visualization import (
    load_data,
    prepare_streamtube_data,
    visualize_with_pyvista,
    visualize_with_plotly
)

# Load data
df, image_3d = load_data('tensor_data.pkl', 'image_data.tif')

# Prepare for visualization
points, vectors, fa_values = prepare_streamtube_data(df, subsample=2)

# Visualize with PyVista
visualize_with_pyvista(
    points, vectors, fa_values,
    streamline_length=25.0,
    tube_radius=0.5
)

# Or visualize with Plotly
visualize_with_plotly(
    points, vectors, fa_values,
    streamline_length=20.0
)
```

### Testing with Synthetic Data

If you want to test the visualization without real data:

```bash
python example_usage.py
```

This will create synthetic tensor data and visualize it.

## Visualization Methods

### PyVista
- **Pros**: High-quality rendering, smooth streamtubes, volume rendering support
- **Cons**: Requires VTK, desktop application
- **Best for**: Final publication-quality visualizations

### Plotly
- **Pros**: Interactive, web-based, easy sharing
- **Cons**: Can be slower with many streamlines
- **Best for**: Exploratory analysis, presentations

### Plotly Cone Glyphs
- **Pros**: Fast, shows vector field directly
- **Cons**: Not as smooth as streamtubes
- **Best for**: Quick overview of tensor field

## Parameters

### Subsampling
Use `--subsample N` to visualize every Nth voxel. This significantly improves performance for large datasets:
- `subsample=1`: All data (slowest, highest detail)
- `subsample=2`: Every other voxel (recommended starting point)
- `subsample=5`: Every 5th voxel (faster, less detail)

### Streamline Length
Controls how far streamlines propagate from seed points (default: 20.0)

### Tube Radius
Controls the thickness of streamtubes in PyVista visualization (default: 0.5)

## Color Scale

The color scale represents Fractional Anisotropy (FA):
- **Red/Hot colors**: High FA (high anisotropy, strong directional coherence)
- **Blue/Cold colors**: Low FA (more isotropic, less directional coherence)
- **Range**: Typically 0.0 to 1.0

## Troubleshooting

### "Could not find coordinate columns"
Make sure your DataFrame has columns named `x`, `y`, `z` or `i`, `j`, `k`.

### "Could not find FA column"
Ensure your DataFrame has a column with "FA" in the name.

### "Could not find eigenvector columns"
The DataFrame should have columns like `evec1_x`, `evec1_y`, `evec1_z` for the principal eigenvector.

### Performance Issues
- Increase the `--subsample` parameter
- Reduce `--streamline-length`
- Use fewer seed points in the Plotly visualization

## Example Output

The visualization will show:
1. 3D streamtubes following the principal eigenvector field
2. Color-coded by FA values
3. Interactive controls (rotation, zoom, pan)
4. Color bar showing the FA scale

## Citation

If you use this code in your research, please cite your tensor analysis methods and the visualization libraries used (PyVista, Plotly).
