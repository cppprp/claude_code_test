"""
Heart Tissue Tensor Analysis Visualization
Visualizes streamtubes from eigenvector data with FA color mapping

This script reads tensor analysis data (eigenvalues, eigenvectors, FA values)
from a pickle file and the original 3D image data from a multiframe TIFF,
then creates streamtube visualizations.
"""

import numpy as np
import pandas as pd
import pickle
from pathlib import Path
from typing import Tuple, Optional
import tifffile


def load_data(pickle_path: str, tiff_path: str) -> Tuple[pd.DataFrame, np.ndarray]:
    """
    Load tensor analysis data and original 3D image.

    Parameters
    ----------
    pickle_path : str
        Path to pickle file containing DataFrame with eigenvalues, eigenvectors, and FA
    tiff_path : str
        Path to multiframe TIFF file with 3D image data

    Returns
    -------
    df : pd.DataFrame
        DataFrame with tensor analysis results
    image_3d : np.ndarray
        3D image data from TIFF
    """
    # Load pickle file
    with open(pickle_path, 'rb') as f:
        df = pickle.load(f)

    # Load multiframe TIFF
    image_3d = tifffile.imread(tiff_path)

    print(f"Loaded DataFrame with {len(df)} voxels")
    print(f"DataFrame columns: {df.columns.tolist()}")
    print(f"Image shape: {image_3d.shape}")

    return df, image_3d


def prepare_streamtube_data(df: pd.DataFrame, subsample: Optional[int] = None) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Prepare data for streamtube visualization.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with columns for positions, eigenvectors, and FA values
    subsample : int, optional
        Subsample factor to reduce number of streamlines

    Returns
    -------
    points : np.ndarray
        Starting points for streamtubes (N x 3)
    vectors : np.ndarray
        Principal eigenvectors at each point (N x 3)
    fa_values : np.ndarray
        Fractional anisotropy values (N,)
    """
    # Extract spatial coordinates
    # Assumes columns like 'x', 'y', 'z' or 'i', 'j', 'k' or similar
    coord_cols = []
    for possible_cols in [['x', 'y', 'z'], ['i', 'j', 'k'], ['X', 'Y', 'Z']]:
        if all(col in df.columns for col in possible_cols):
            coord_cols = possible_cols
            break

    if not coord_cols:
        raise ValueError("Could not find coordinate columns in DataFrame")

    points = df[coord_cols].values

    # Extract FA values
    fa_cols = [col for col in df.columns if 'FA' in col.upper() or 'fractional' in col.lower()]
    if fa_cols:
        fa_values = df[fa_cols[0]].values
    else:
        raise ValueError("Could not find FA column in DataFrame")

    # Extract principal eigenvector (largest eigenvalue)
    # Look for eigenvector columns
    evec_cols = [col for col in df.columns if 'evec' in col.lower() or 'eigenvector' in col.lower()]

    if evec_cols:
        # Assume format like 'evec1_x', 'evec1_y', 'evec1_z' for principal eigenvector
        principal_evec_cols = []
        for suffix in ['x', 'y', 'z']:
            for col in evec_cols:
                if '1' in col and suffix in col.lower():
                    principal_evec_cols.append(col)
                    break

        if len(principal_evec_cols) == 3:
            vectors = df[principal_evec_cols].values
        else:
            raise ValueError("Could not find principal eigenvector columns")
    else:
        raise ValueError("Could not find eigenvector columns in DataFrame")

    # Subsample if requested
    if subsample and subsample > 1:
        indices = np.arange(0, len(points), subsample)
        points = points[indices]
        vectors = vectors[indices]
        fa_values = fa_values[indices]
        print(f"Subsampled to {len(points)} points")

    # Normalize vectors
    vectors = vectors / (np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-10)

    return points, vectors, fa_values


def visualize_with_pyvista(points: np.ndarray, vectors: np.ndarray, fa_values: np.ndarray,
                           image_3d: Optional[np.ndarray] = None,
                           streamline_length: float = 20.0,
                           tube_radius: float = 0.5,
                           integration_step: float = 0.5):
    """
    Create streamtube visualization using PyVista.

    Parameters
    ----------
    points : np.ndarray
        Starting points for streamtubes (N x 3)
    vectors : np.ndarray
        Direction vectors at each point (N x 3)
    fa_values : np.ndarray
        Fractional anisotropy values for coloring (N,)
    image_3d : np.ndarray, optional
        Original 3D image for context
    streamline_length : float
        Maximum length of streamlines
    tube_radius : float
        Radius of the tubes
    integration_step : float
        Step size for streamline integration
    """
    try:
        import pyvista as pv
    except ImportError:
        raise ImportError("PyVista not installed. Install with: uv pip install pyvista")

    # Create a PyVista plotter
    plotter = pv.Plotter()

    # Create vector field for streamline integration
    # We'll use a structured grid approach
    grid_shape = tuple(int(points[:, i].max() - points[:, i].min()) + 10 for i in range(3))
    origin = tuple(points[:, i].min() - 5 for i in range(3))

    # Create mesh for the vector field
    mesh = pv.ImageData(dimensions=grid_shape, spacing=(1, 1, 1), origin=origin)

    # Initialize vector field
    vector_field = np.zeros((mesh.n_points, 3))
    fa_field = np.zeros(mesh.n_points)

    # Map vectors to grid
    for i, (pt, vec, fa) in enumerate(zip(points, vectors, fa_values)):
        # Find nearest grid point
        idx = tuple(int(pt[j] - origin[j]) for j in range(3))
        if all(0 <= idx[j] < grid_shape[j] for j in range(3)):
            flat_idx = np.ravel_multi_index(idx, grid_shape, order='F')
            if flat_idx < len(vector_field):
                vector_field[flat_idx] = vec
                fa_field[flat_idx] = fa

    mesh['vectors'] = vector_field
    mesh['FA'] = fa_field

    # Generate streamlines
    streamlines = mesh.streamlines(
        vectors='vectors',
        source_center=points.mean(axis=0),
        source_radius=points.std(),
        n_points=min(200, len(points)),
        max_time=streamline_length,
        integration_direction='both',
        initial_step_length=integration_step,
        max_step_length=integration_step * 2
    )

    # Create tubes from streamlines
    tubes = streamlines.tube(radius=tube_radius)

    # Sample FA values onto tubes
    tubes = tubes.sample(mesh)

    # Add to plotter with FA color mapping
    plotter.add_mesh(
        tubes,
        scalars='FA',
        cmap='jet',
        scalar_bar_args={'title': 'Fractional Anisotropy'},
        clim=[0, 1]
    )

    # Optionally add volume rendering of original image
    if image_3d is not None:
        vol_mesh = pv.ImageData(dimensions=image_3d.shape)
        vol_mesh['values'] = image_3d.flatten(order='F')
        plotter.add_volume(vol_mesh, opacity='sigmoid', cmap='gray', opacity_unit_distance=2.0)

    plotter.add_axes()
    plotter.show_grid()
    plotter.show()


def visualize_with_plotly(points: np.ndarray, vectors: np.ndarray, fa_values: np.ndarray,
                          streamline_length: float = 20.0,
                          num_steps: int = 50):
    """
    Create streamtube visualization using Plotly.

    Parameters
    ----------
    points : np.ndarray
        Starting points for streamtubes (N x 3)
    vectors : np.ndarray
        Direction vectors at each point (N x 3)
    fa_values : np.ndarray
        Fractional anisotropy values for coloring (N,)
    streamline_length : float
        Maximum length of streamlines
    num_steps : int
        Number of integration steps per streamline
    """
    try:
        import plotly.graph_objects as go
    except ImportError:
        raise ImportError("Plotly not installed. Install with: uv pip install plotly")

    # Generate streamlines manually using simple Euler integration
    step_size = streamline_length / num_steps

    # We'll create multiple streamtubes
    # Subsample seed points for performance
    num_streamlines = min(100, len(points))
    seed_indices = np.linspace(0, len(points) - 1, num_streamlines, dtype=int)

    streamtubes = []

    for idx in seed_indices:
        seed = points[idx]
        direction = vectors[idx]
        seed_fa = fa_values[idx]

        # Integrate forward
        streamline_points = [seed]
        current_pos = seed.copy()
        current_dir = direction.copy()

        for step in range(num_steps):
            # Simple Euler integration
            current_pos = current_pos + current_dir * step_size

            # Find nearest neighbor to update direction
            distances = np.linalg.norm(points - current_pos, axis=1)
            nearest_idx = np.argmin(distances)

            if distances[nearest_idx] < 5.0:  # Within reasonable distance
                current_dir = vectors[nearest_idx]

            streamline_points.append(current_pos.copy())

        # Integrate backward
        current_pos = seed.copy()
        current_dir = -direction.copy()

        for step in range(num_steps):
            current_pos = current_pos + current_dir * step_size

            distances = np.linalg.norm(points - current_pos, axis=1)
            nearest_idx = np.argmin(distances)

            if distances[nearest_idx] < 5.0:
                current_dir = -vectors[nearest_idx]

            streamline_points.insert(0, current_pos.copy())

        streamline_points = np.array(streamline_points)

        # Create streamtube trace
        streamtubes.append(
            go.Streamtube(
                x=streamline_points[:, 0],
                y=streamline_points[:, 1],
                z=streamline_points[:, 2],
                u=np.full(len(streamline_points), current_dir[0]),
                v=np.full(len(streamline_points), current_dir[1]),
                w=np.full(len(streamline_points), current_dir[2]),
                colorscale='Jet',
                cmin=0,
                cmax=1,
                colorbar=dict(title='FA'),
                sizeref=0.3,
                showscale=(idx == seed_indices[0]),  # Only show colorbar once
                name=f'Streamtube {idx}'
            )
        )

    # Create figure
    fig = go.Figure(data=streamtubes)

    fig.update_layout(
        scene=dict(
            xaxis_title='X',
            yaxis_title='Y',
            zaxis_title='Z',
            aspectmode='data'
        ),
        title='Heart Tissue Tensor Streamtubes (FA colored)',
        showlegend=False
    )

    fig.show()


def visualize_with_plotly_cone(points: np.ndarray, vectors: np.ndarray, fa_values: np.ndarray,
                                subsample: int = 5):
    """
    Alternative Plotly visualization using cone glyphs.

    Parameters
    ----------
    points : np.ndarray
        Points in space (N x 3)
    vectors : np.ndarray
        Direction vectors (N x 3)
    fa_values : np.ndarray
        FA values for coloring (N,)
    subsample : int
        Subsampling factor for display
    """
    try:
        import plotly.graph_objects as go
    except ImportError:
        raise ImportError("Plotly not installed. Install with: uv pip install plotly")

    # Subsample for performance
    indices = np.arange(0, len(points), subsample)
    pts = points[indices]
    vecs = vectors[indices]
    fa = fa_values[indices]

    # Scale vectors by FA for visual effect
    scaled_vecs = vecs * fa[:, np.newaxis]

    fig = go.Figure(data=go.Cone(
        x=pts[:, 0],
        y=pts[:, 1],
        z=pts[:, 2],
        u=scaled_vecs[:, 0],
        v=scaled_vecs[:, 1],
        w=scaled_vecs[:, 2],
        colorscale='Jet',
        sizemode='absolute',
        sizeref=2,
        colorbar=dict(title='FA'),
        cmin=0,
        cmax=1,
        showscale=True
    ))

    fig.update_layout(
        scene=dict(
            xaxis_title='X',
            yaxis_title='Y',
            zaxis_title='Z',
            aspectmode='data'
        ),
        title='Heart Tissue Tensor Field (FA colored cones)'
    )

    fig.show()


def main():
    """
    Main function demonstrating usage.
    """
    import argparse

    parser = argparse.ArgumentParser(description='Visualize heart tissue tensor analysis')
    parser.add_argument('pickle_file', type=str, help='Path to pickle file with tensor data')
    parser.add_argument('tiff_file', type=str, help='Path to multiframe TIFF with 3D image')
    parser.add_argument('--method', type=str, choices=['pyvista', 'plotly', 'plotly-cone'],
                        default='pyvista', help='Visualization method')
    parser.add_argument('--subsample', type=int, default=None,
                        help='Subsample factor for data reduction')
    parser.add_argument('--streamline-length', type=float, default=20.0,
                        help='Maximum streamline length')
    parser.add_argument('--tube-radius', type=float, default=0.5,
                        help='Tube radius for PyVista')

    args = parser.parse_args()

    # Load data
    print("Loading data...")
    df, image_3d = load_data(args.pickle_file, args.tiff_file)

    # Prepare streamtube data
    print("Preparing streamtube data...")
    points, vectors, fa_values = prepare_streamtube_data(df, subsample=args.subsample)

    print(f"Number of streamtubes: {len(points)}")
    print(f"FA range: [{fa_values.min():.3f}, {fa_values.max():.3f}]")

    # Visualize
    print(f"Creating visualization with {args.method}...")
    if args.method == 'pyvista':
        visualize_with_pyvista(
            points, vectors, fa_values,
            image_3d=None,  # Set to image_3d to include volume rendering
            streamline_length=args.streamline_length,
            tube_radius=args.tube_radius
        )
    elif args.method == 'plotly':
        visualize_with_plotly(
            points, vectors, fa_values,
            streamline_length=args.streamline_length
        )
    elif args.method == 'plotly-cone':
        visualize_with_plotly_cone(points, vectors, fa_values)


if __name__ == '__main__':
    main()
