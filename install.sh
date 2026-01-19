#!/bin/bash
# MyClip Installer
# Downloads and installs MyClip, bypassing Gatekeeper

set -e

APP_NAME="MyClip"
INSTALL_DIR="/Applications"
REPO="antonpetrovmain/myclip"

echo "Installing $APP_NAME..."

# Create temp directory
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

# Get latest release info
echo "Finding latest release..."
RELEASE_JSON=$(curl -s "https://api.github.com/repos/$REPO/releases/latest")
VERSION=$(echo "$RELEASE_JSON" | grep '"tag_name"' | cut -d '"' -f 4)
RELEASE_URL=$(echo "$RELEASE_JSON" | grep "browser_download_url.*macos-arm64.zip" | cut -d '"' -f 4)

if [ -z "$RELEASE_URL" ]; then
    echo "Error: Could not find latest release"
    exit 1
fi

# Download latest release
echo "Downloading $APP_NAME $VERSION..."
curl -L -o myclip.zip "$RELEASE_URL"

# Extract
echo "Extracting..."
unzip -q myclip.zip

# Remove old version if exists
if [ -d "$INSTALL_DIR/$APP_NAME.app" ]; then
    echo "Removing old version..."
    rm -rf "$INSTALL_DIR/$APP_NAME.app"
fi

# Move to Applications
echo "Installing to $INSTALL_DIR..."
mv "$APP_NAME.app" "$INSTALL_DIR/"

# Remove quarantine attribute (bypasses Gatekeeper)
echo "Removing quarantine..."
xattr -cr "$INSTALL_DIR/$APP_NAME.app"

# Cleanup
rm -rf "$TEMP_DIR"

echo ""
echo "Done! $APP_NAME $VERSION installed to $INSTALL_DIR/$APP_NAME.app"
echo ""
echo "NOTE: You need to grant Accessibility permission:"
echo "  System Settings > Privacy & Security > Accessibility > Add MyClip"
echo ""
echo "Run with: open /Applications/MyClip.app"
