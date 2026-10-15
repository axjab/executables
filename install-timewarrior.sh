#!/bin/bash

set -e

echo "=== Timewarrior Auto-Installer for PikaOS ==="

# Check required tools
echo "Checking for cmake, make, asciidoctor..."
for tool in cmake make asciidoctor; do
    if ! command -v "$tool" &> /dev/null; then
        echo "Installing $tool..."
        pikman install "$tool"
    fi
done

# Download and build
VERSION="1.10.0"
FILENAME="timew-${VERSION}.tar.gz"
URL="https://github.com/GothenburgBitFactory/timewarrior/releases/download/v${VERSION}/${FILENAME}"

echo "Downloading $FILENAME..."
wget "$URL" || curl -O "$URL"

echo "Extracting..."
tar xzf "$FILENAME"
cd "timew-${VERSION}"

echo "Building..."
cmake .
make -j$(nproc)
sudo make install

echo "Cleaning up..."
cd ..
rm -rf "timew-${VERSION}"

echo "✓ Timewarrior installed successfully!"
timew --version
