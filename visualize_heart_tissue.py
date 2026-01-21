"""
Quick-start script for visualizing the heart tissue tensor analysis data.
Configured for the tomo (44B-T2)-256-cropped dataset.
"""

from streamtube_visualization import (
    load_data,
    prepare_streamtube_data,
    visualize_with_pyvista,
    visualize_with_plotly,
    visualize_with_plotly_cone
)


# Update these paths to match your file locations
PICKLE_FILE = '/Users/asvetlove/Downloads/tomo (44B-T2)-256-cropped_df.pkl'
TIFF_FILE = '/Users/asvetlove/Downloads/tomo_(44B-T2)-256-cropped.tif'


def main():
    """
    Main visualization function for heart tissue data.
    """
    print("=" * 80)
    print("Heart Tissue Tensor Analysis Visualization")
    print("=" * 80)

    # Step 1: Load data
    print("\n[1/3] Loading data...")
    try:
        df, image_3d = load_data(PICKLE_FILE, TIFF_FILE)
        print(f"✓ Loaded DataFrame with {len(df):,} voxels")
        print(f"✓ Loaded 3D image with shape {image_3d.shape}")
    except FileNotFoundError as e:
        print(f"\n❌ Error: Could not find file")
        print(f"    {e}")
        print("\nPlease update the file paths at the top of this script:")
        print(f"    PICKLE_FILE = '{PICKLE_FILE}'")
        print(f"    TIFF_FILE = '{TIFF_FILE}'")
        return
    except Exception as e:
        print(f"\n❌ Error loading data: {e}")
        print("\nTry running: python inspect_pickle_data.py '{PICKLE_FILE}'")
        print("This will show the DataFrame structure and help identify the issue.")
        return

    print(f"\nDataFrame columns: {df.columns.tolist()}")

    # Step 2: Prepare streamtube data
    print("\n[2/3] Preparing streamtube data...")
    try:
        # Start with subsampling for performance
        # Adjust subsample value: 1=all data (slow), 2=every other voxel, 5=every 5th voxel (fast)
        subsample = 2
        points, vectors, fa_values = prepare_streamtube_data(df, subsample=subsample)

        print(f"✓ Prepared {len(points):,} streamtube seed points")
        print(f"  FA value range: [{fa_values.min():.4f}, {fa_values.max():.4f}]")
        print(f"  FA value mean: {fa_values.mean():.4f}")
        print(f"  Subsample factor: {subsample}")

    except Exception as e:
        print(f"\n❌ Error preparing data: {e}")
        print("\nThis usually means the DataFrame columns don't match expected names.")
        print("Run the inspection script to see the actual column names:")
        print(f"    python inspect_pickle_data.py '{PICKLE_FILE}'")
        return

    # Step 3: Visualize
    print("\n[3/3] Creating visualization...")
    print("\nChoose visualization method:")
    print("  1. PyVista (high-quality, desktop, recommended)")
    print("  2. Plotly streamtubes (interactive, web-based)")
    print("  3. Plotly cone glyphs (fast preview)")

    try:
        choice = input("\nEnter choice (1-3) [default: 1]: ").strip() or "1"

        if choice == "1":
            print("\nLaunching PyVista visualization...")
            print("Tip: Use mouse to rotate, scroll to zoom")
            visualize_with_pyvista(
                points, vectors, fa_values,
                image_3d=None,  # Change to image_3d to include volume rendering
                streamline_length=20.0,
                tube_radius=0.5,
                integration_step=0.5
            )

        elif choice == "2":
            print("\nLaunching Plotly streamtubes visualization...")
            print("This will open in your web browser")
            visualize_with_plotly(
                points, vectors, fa_values,
                streamline_length=20.0,
                num_steps=50
            )

        elif choice == "3":
            print("\nLaunching Plotly cone glyphs visualization...")
            print("This will open in your web browser")
            visualize_with_plotly_cone(
                points, vectors, fa_values,
                subsample=5
            )

        else:
            print(f"Invalid choice: {choice}")
            return

        print("\n✓ Visualization complete!")

    except KeyboardInterrupt:
        print("\n\nVisualization cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error during visualization: {e}")
        import traceback
        traceback.print_exc()


def quick_pyvista():
    """
    Quick visualization with PyVista (no prompts).
    """
    print("Loading data and creating PyVista visualization...")
    df, image_3d = load_data(PICKLE_FILE, TIFF_FILE)
    points, vectors, fa_values = prepare_streamtube_data(df, subsample=2)

    visualize_with_pyvista(
        points, vectors, fa_values,
        streamline_length=20.0,
        tube_radius=0.5
    )


def quick_plotly():
    """
    Quick visualization with Plotly (no prompts).
    """
    print("Loading data and creating Plotly visualization...")
    df, image_3d = load_data(PICKLE_FILE, TIFF_FILE)
    points, vectors, fa_values = prepare_streamtube_data(df, subsample=3)

    visualize_with_plotly(
        points, vectors, fa_values,
        streamline_length=20.0
    )


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == '--pyvista':
            quick_pyvista()
        elif sys.argv[1] == '--plotly':
            quick_plotly()
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Usage:")
            print("  python visualize_heart_tissue.py           # Interactive mode")
            print("  python visualize_heart_tissue.py --pyvista # Direct PyVista")
            print("  python visualize_heart_tissue.py --plotly  # Direct Plotly")
    else:
        main()
