#!/bin/bash
# Script to package Lambda function with dependencies

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/../backend"
BUILD_DIR="$BACKEND_DIR/build"
LAMBDA_ZIP="$BUILD_DIR/lambda.zip"

echo "🔨 Building Lambda package..."

# Clean previous build
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR/package"

# Install dependencies to package directory
echo "📦 Installing dependencies..."
pip install -r "$BACKEND_DIR/requirements.txt" -t "$BUILD_DIR/package" --quiet

# Copy app code
echo "📂 Copying application code..."
cp -r "$BACKEND_DIR/app" "$BUILD_DIR/package/"

# Create zip
echo "🗜️  Creating Lambda zip..."
cd "$BUILD_DIR/package"
zip -r "$LAMBDA_ZIP" . -q

echo "✅ Lambda package created: $LAMBDA_ZIP"
echo "📊 Package size: $(du -h "$LAMBDA_ZIP" | cut -f1)"
