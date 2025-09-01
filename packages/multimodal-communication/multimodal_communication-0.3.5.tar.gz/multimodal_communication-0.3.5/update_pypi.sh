#!/usr/bin/env bash
set -e  # Exit immediately on error

# Check if version argument is provided
if [ -z "$1" ]; then
  echo "Usage: ./release.sh <new_version>"
  exit 1
fi

NEW_VERSION=$1

# Update version in pyproject.toml
echo "Updating version to $NEW_VERSION..."
sed -i.bak "s/^version = .*/version = \"$NEW_VERSION\"/" pyproject.toml
rm -f pyproject.toml.bak

# Clean old build artifacts
echo "Cleaning old builds..."
rm -rf dist/ build/ *.egg-info

# Build new distribution
echo "Building distribution..."
uv run python -m build

# Upload to PyPI
echo "Uploading to PyPI..."
uv run twine upload dist/*

echo "✅ Release $NEW_VERSION complete!"
