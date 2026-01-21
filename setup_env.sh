#!/bin/bash
# Setup script for heart tissue tensor visualization environment
# Uses uv for fast package management

set -e  # Exit on error

echo "=========================================="
echo "Heart Tissue Tensor Visualization Setup"
echo "=========================================="
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed."
    echo ""
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo ""
    echo "✓ uv installed successfully"
    echo ""
    echo "⚠️  Please restart your shell or run:"
    echo "    source ~/.bashrc  # or ~/.zshrc"
    echo ""
    echo "Then run this setup script again."
    exit 0
fi

echo "✓ uv is installed ($(uv --version))"
echo ""

# Create virtual environment
echo "[1/3] Creating virtual environment..."
if [ -d ".venv" ]; then
    echo "  Virtual environment already exists, skipping creation"
else
    uv venv
    echo "  ✓ Virtual environment created in .venv/"
fi
echo ""

# Activate virtual environment
echo "[2/3] Activating virtual environment..."
source .venv/bin/activate
echo "  ✓ Virtual environment activated"
echo ""

# Install dependencies
echo "[3/3] Installing dependencies..."
uv pip install -r requirements.txt
echo "  ✓ All dependencies installed"
echo ""

echo "=========================================="
echo "✓ Setup complete!"
echo "=========================================="
echo ""
echo "To activate the environment in the future, run:"
echo "  source .venv/bin/activate"
echo ""
echo "Quick start:"
echo "  python visualize_heart_tissue.py"
echo ""
echo "Inspect your data:"
echo "  python inspect_pickle_data.py <path_to_pickle>"
echo ""
