"""
Example usage of streamtube visualization for heart tissue tensor analysis.
"""

import numpy as np
import pandas as pd
import pickle
import tifffile
from streamtube_visualization import (
    load_data,
    prepare_streamtube_data,
    visualize_with_pyvista,
    visualize_with_plotly,
    visualize_with_plotly_cone
)


def example_pyvista():
    """
    Example using PyVista for high-quality streamtube visualization.
    """
    # Load your data
    pickle_path = 'path/to/your/tensor_data.pkl'
    tiff_path = 'path/to/your/image_data.tif'

    # Load the data
    df, image_3d = load_data(pickle_path, tiff_path)

    # Prepare for visualization (subsample for performance if needed)
    points, vectors, fa_values = prepare_streamtube_data(df, subsample=2)

    # Create visualization
    visualize_with_pyvista(
        points, vectors, fa_values,
        image_3d=None,  # Set to image_3d to include volume
        streamline_length=25.0,
        tube_radius=0.5,
        integration_step=0.5
    )


def example_plotly():
    """
    Example using Plotly for interactive web-based visualization.
    """
    pickle_path = 'path/to/your/tensor_data.pkl'
    tiff_path = 'path/to/your/image_data.tif'

    df, image_3d = load_data(pickle_path, tiff_path)
    points, vectors, fa_values = prepare_streamtube_data(df, subsample=5)

    # Plotly streamtubes
    visualize_with_plotly(
        points, vectors, fa_values,
        streamline_length=20.0,
        num_steps=50
    )


def example_plotly_cones():
    """
    Example using Plotly cone glyphs as an alternative visualization.
    """
    pickle_path = 'path/to/your/tensor_data.pkl'
    tiff_path = 'path/to/your/image_data.tif'

    df, image_3d = load_data(pickle_path, tiff_path)
    points, vectors, fa_values = prepare_streamtube_data(df, subsample=3)

    # Cone glyph visualization
    visualize_with_plotly_cone(points, vectors, fa_values, subsample=10)


def create_synthetic_example():
    """
    Create a synthetic example for testing if you don't have real data yet.
    """
    # Create synthetic tensor field
    nx, ny, nz = 50, 50, 50
    x, y, z = np.meshgrid(np.arange(nx), np.arange(ny), np.arange(nz), indexing='ij')

    # Flatten coordinates
    coords = np.stack([x.flatten(), y.flatten(), z.flatten()], axis=1)

    # Create synthetic principal eigenvectors (spiral pattern)
    center = np.array([nx/2, ny/2, nz/2])
    rel_coords = coords - center

    # Create a synthetic vector field
    theta = np.arctan2(rel_coords[:, 1], rel_coords[:, 0])
    evec1_x = -np.sin(theta)
    evec1_y = np.cos(theta)
    evec1_z = np.tanh((rel_coords[:, 2] - nz/2) / 10)

    evecs = np.stack([evec1_x, evec1_y, evec1_z], axis=1)
    evecs = evecs / (np.linalg.norm(evecs, axis=1, keepdims=True) + 1e-10)

    # Create synthetic FA values (higher near center)
    distances = np.linalg.norm(rel_coords, axis=1)
    fa_values = np.exp(-distances / 20) * 0.8 + 0.2

    # Create DataFrame
    df = pd.DataFrame({
        'x': coords[:, 0],
        'y': coords[:, 1],
        'z': coords[:, 2],
        'evec1_x': evecs[:, 0],
        'evec1_y': evecs[:, 1],
        'evec1_z': evecs[:, 2],
        'FA': fa_values
    })

    # Save to pickle
    with open('synthetic_tensor_data.pkl', 'wb') as f:
        pickle.dump(df, f)

    # Create synthetic 3D image
    image_3d = np.random.randn(nx, ny, nz) * 50 + 200
    image_3d = np.clip(image_3d, 0, 255).astype(np.uint8)
    tifffile.imwrite('synthetic_image.tif', image_3d)

    print("Created synthetic_tensor_data.pkl and synthetic_image.tif")

    # Now visualize
    points, vectors, fa_vals = prepare_streamtube_data(df, subsample=2)

    print("\nVisualizing with PyVista...")
    visualize_with_pyvista(points, vectors, fa_vals, streamline_length=15.0, tube_radius=0.3)


if __name__ == '__main__':
    # Uncomment the example you want to run:

    # For real data:
    # example_pyvista()
    # example_plotly()
    # example_plotly_cones()

    # For testing with synthetic data:
    create_synthetic_example()
