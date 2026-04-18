#!/bin/bash
echo "Building VitalSign DEB package..."
echo.

# Check if checkinstall is installed
if ! command -v checkinstall &> /dev/null; then
    echo "checkinstall not found. Installing..."
    sudo apt update
    sudo apt install -y checkinstall
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Build DEB package
echo "Building DEB package..."
sudo checkinstall -D \
  --pkgname=vitalsign \
  --pkgversion=1.0 \
  --pkgrelease=1 \
  --maintainer="your@email.com" \
  --requires="python3,python3-pyqt6,python3-psutil,python3-matplotlib,python3-numpy,python3-gputil,python3-pycpuinfo" \
  --nodoc \
  --install=no \
  bash scripts/run_gui.sh

echo.
echo "DEB package build complete!"
echo "Package located in the current directory."
