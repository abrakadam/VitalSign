#!/bin/bash
echo "Building VitalSign AppImage..."
echo.

# Check if tools are installed
if ! command -v patchelf &> /dev/null; then
    echo "patchelf not found. Installing..."
    sudo apt update
    sudo apt install -y patchelf desktop-file-utils
fi

# Download appimagetool if not exists
if [ ! -f "appimagetool-x86_64.AppImage" ]; then
    echo "Downloading appimagetool..."
    wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
    chmod +x appimagetool-x86_64.AppImage
fi

# Create AppDir structure
echo "Creating AppDir..."
rm -rf VitalSign.AppDir
mkdir -p VitalSign.AppDir/usr/bin
mkdir -p VitalSign.AppDir/usr/share/applications
mkdir -p VitalSign.AppDir/usr/share/icons
mkdir -p VitalSign.AppDir/opt/vitalsign

# Copy files
echo "Copying files..."
cp -r * VitalSign.AppDir/opt/vitalsign/
cp scripts/run_gui.sh VitalSign.AppDir/usr/bin/vitalsign
chmod +x VitalSign.AppDir/usr/bin/vitalsign

# Copy icon if exists
if [ -f "resources/icon.png" ]; then
    cp resources/icon.png VitalSign.AppDir/usr/share/icons/vitalsign.png
fi

# Create .desktop file
echo "Creating .desktop file..."
cat > VitalSign.AppDir/vitalsign.desktop <<EOF
[Desktop Entry]
Name=VitalSign
Comment=Advanced System Monitor
Exec=vitalsign
Icon=vitalsign
Type=Application
Categories=System;Monitor;
Terminal=false
EOF

cp VitalSign.AppDir/vitalsign.desktop VitalSign.AppDir/usr/share/applications/

# Create AppRun
echo "Creating AppRun..."
cat > VitalSign.AppDir/AppRun <<'EOF'
#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin:${PATH}"
exec "${HERE}/usr/bin/vitalsign"
EOF
chmod +x VitalSign.AppDir/AppRun

# Build AppImage
echo "Building AppImage..."
./appimagetool-x86_64.AppImage VitalSign.AppDir

echo.
echo "AppImage build complete!"
echo "AppImage located in: VitalSign-x86_64.AppImage"
