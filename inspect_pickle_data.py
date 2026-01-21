"""
Inspect the structure of a pickle file containing tensor analysis data.
Run this script locally to examine your data format.
"""

import pickle
import pandas as pd
import numpy as np


def inspect_pickle_file(pickle_path: str):
    """
    Inspect the contents of a pickle file and print detailed information.

    Parameters
    ----------
    pickle_path : str
        Path to the pickle file
    """
    print(f"Inspecting: {pickle_path}")
    print("=" * 80)

    # Load the pickle file
    with open(pickle_path, 'rb') as f:
        data = pickle.load(f)

    print(f"\nData type: {type(data)}")

    if isinstance(data, pd.DataFrame):
        print(f"\nDataFrame shape: {data.shape}")
        print(f"Number of rows: {len(data)}")
        print(f"Number of columns: {len(data.columns)}")

        print("\n" + "=" * 80)
        print("COLUMN NAMES:")
        print("=" * 80)
        for i, col in enumerate(data.columns, 1):
            print(f"{i:3d}. {col}")

        print("\n" + "=" * 80)
        print("COLUMN DETAILS:")
        print("=" * 80)
        print(data.dtypes)

        print("\n" + "=" * 80)
        print("FIRST FEW ROWS:")
        print("=" * 80)
        print(data.head())

        print("\n" + "=" * 80)
        print("STATISTICAL SUMMARY:")
        print("=" * 80)
        print(data.describe())

        print("\n" + "=" * 80)
        print("COLUMN SEARCH RESULTS:")
        print("=" * 80)

        # Search for coordinate columns
        coord_patterns = [['x', 'y', 'z'], ['i', 'j', 'k'], ['X', 'Y', 'Z']]
        print("\nCoordinate columns:")
        for pattern in coord_patterns:
            matches = [col for col in data.columns if any(p in col.lower() for p in pattern)]
            if matches:
                print(f"  Pattern {pattern}: {matches}")

        # Search for FA columns
        print("\nFractional Anisotropy (FA) columns:")
        fa_cols = [col for col in data.columns if 'fa' in col.lower() or 'fractional' in col.lower() or 'anisotropy' in col.lower()]
        if fa_cols:
            print(f"  Found: {fa_cols}")
            for col in fa_cols:
                print(f"    {col}: range [{data[col].min():.4f}, {data[col].max():.4f}], mean {data[col].mean():.4f}")
        else:
            print("  No FA columns found")

        # Search for eigenvector columns
        print("\nEigenvector columns:")
        evec_cols = [col for col in data.columns if 'evec' in col.lower() or 'eigenvector' in col.lower() or 'vector' in col.lower()]
        if evec_cols:
            print(f"  Found {len(evec_cols)} eigenvector-related columns:")
            for col in evec_cols:
                print(f"    {col}")
        else:
            print("  No eigenvector columns found")

        # Search for eigenvalue columns
        print("\nEigenvalue columns:")
        eval_cols = [col for col in data.columns if 'eval' in col.lower() or 'eigenvalue' in col.lower() or 'lambda' in col.lower()]
        if eval_cols:
            print(f"  Found {len(eval_cols)} eigenvalue-related columns:")
            for col in eval_cols:
                print(f"    {col}: range [{data[col].min():.4f}, {data[col].max():.4f}]")
        else:
            print("  No eigenvalue columns found")

        print("\n" + "=" * 80)
        print("RECOMMENDED USAGE:")
        print("=" * 80)

        # Try to infer the correct columns
        coord_cols = None
        for pattern in coord_patterns:
            matches = [col for col in data.columns if col.lower() in [p.lower() for p in pattern]]
            if len(matches) == 3:
                coord_cols = matches
                break

        if coord_cols:
            print(f"\nCoordinate columns: {coord_cols}")
        else:
            print("\n⚠️  Could not automatically identify coordinate columns")
            print("    Please manually specify which columns contain x, y, z coordinates")

        if fa_cols:
            print(f"FA column: {fa_cols[0]}")
        else:
            print("\n⚠️  Could not automatically identify FA column")

        # Try to find principal eigenvector
        principal_evec = []
        for suffix in ['x', 'y', 'z']:
            for col in data.columns:
                if 'evec' in col.lower() and '1' in col and suffix in col.lower():
                    principal_evec.append(col)
                    break

        if len(principal_evec) == 3:
            print(f"Principal eigenvector columns: {principal_evec}")
        else:
            print("\n⚠️  Could not automatically identify principal eigenvector columns")
            print("    Please manually specify which columns contain the principal eigenvector")

        # Check for any missing values
        print("\n" + "=" * 80)
        print("DATA QUALITY:")
        print("=" * 80)
        missing = data.isnull().sum()
        if missing.sum() > 0:
            print("\n⚠️  Missing values detected:")
            print(missing[missing > 0])
        else:
            print("\n✓ No missing values")

        # Check for infinite values
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        inf_count = 0
        for col in numeric_cols:
            inf_in_col = np.isinf(data[col]).sum()
            if inf_in_col > 0:
                print(f"⚠️  {col}: {inf_in_col} infinite values")
                inf_count += inf_in_col

        if inf_count == 0:
            print("✓ No infinite values")

    elif isinstance(data, dict):
        print("\nData is a dictionary")
        print(f"Keys: {list(data.keys())}")
        for key, value in data.items():
            print(f"\n{key}:")
            print(f"  Type: {type(value)}")
            if isinstance(value, np.ndarray):
                print(f"  Shape: {value.shape}")
                print(f"  Dtype: {value.dtype}")

    else:
        print("\nUnexpected data type!")
        print(f"Type: {type(data)}")
        if hasattr(data, 'shape'):
            print(f"Shape: {data.shape}")


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python inspect_pickle_data.py <path_to_pickle_file>")
        print("\nExample:")
        print("  python inspect_pickle_data.py '/Users/asvetlove/Downloads/tomo (44B-T2)-256-cropped_df.pkl'")
        sys.exit(1)

    pickle_path = sys.argv[1]
    inspect_pickle_file(pickle_path)
