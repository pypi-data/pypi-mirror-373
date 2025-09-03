#!/usr/bin/env python
"""
Version bump script for mcp-openvision.

This script helps developers bump the version in pyproject.toml
and updates the CHANGELOG.md file with a new entry.

Usage:
    python scripts/bump_version.py [major|minor|patch]

Example:
    python scripts/bump_version.py minor  # Bumps the minor version
"""

import argparse
import datetime
import os
import re
import sys
from pathlib import Path


def get_current_version():
    """Extract the current version from pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    
    if not pyproject_path.exists():
        print("Error: pyproject.toml not found")
        sys.exit(1)
        
    with open(pyproject_path, "r") as file:
        content = file.read()
        
    match = re.search(r'version\s*=\s*"([^"]+)"', content)
    if not match:
        print("Error: Could not find version in pyproject.toml")
        sys.exit(1)
        
    return match.group(1)


def bump_version(current_version, bump_type):
    """Bump the version according to the specified type."""
    major, minor, patch = map(int, current_version.split("."))
    
    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        print(f"Error: Invalid bump type '{bump_type}'")
        sys.exit(1)


def update_pyproject_toml(new_version):
    """Update the version in pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    
    with open(pyproject_path, "r") as file:
        content = file.read()
        
    updated_content = re.sub(r'(version\s*=\s*)"([^"]+)"', f'\\1"{new_version}"', content)
    
    with open(pyproject_path, "w") as file:
        file.write(updated_content)
        
    print(f"Updated pyproject.toml with version {new_version}")


def update_changelog(new_version):
    """Add a new entry to CHANGELOG.md."""
    changelog_path = Path("CHANGELOG.md")
    
    if not changelog_path.exists():
        print("Error: CHANGELOG.md not found")
        sys.exit(1)
        
    with open(changelog_path, "r") as file:
        content = file.readlines()
    
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    # Find where to insert the new version
    insert_index = 0
    for i, line in enumerate(content):
        if line.startswith("## ["):
            insert_index = i
            break
    
    # Create the new version block
    new_version_block = [
        f"## [{new_version}] - {today}\n",
        "\n",
        "### Added\n",
        "- \n",
        "\n",
        "### Changed\n",
        "- \n",
        "\n",
        "### Fixed\n",
        "- \n",
        "\n"
    ]
    
    # Insert the new version block
    content = content[:insert_index] + new_version_block + content[insert_index:]
    
    with open(changelog_path, "w") as file:
        file.writelines(content)
        
    print(f"Updated CHANGELOG.md with version {new_version}")
    print(f"Please fill in the details for version {new_version} in CHANGELOG.md")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Bump version in pyproject.toml and update CHANGELOG.md")
    parser.add_argument("bump_type", choices=["major", "minor", "patch"], 
                        help="Type of version bump to perform")
    
    args = parser.parse_args()
    
    # Create scripts directory if it doesn't exist
    os.makedirs("scripts", exist_ok=True)
    
    current_version = get_current_version()
    print(f"Current version: {current_version}")
    
    new_version = bump_version(current_version, args.bump_type)
    print(f"New version: {new_version}")
    
    update_pyproject_toml(new_version)
    update_changelog(new_version)
    
    print("\nNext steps:")
    print(f"1. Fill in the details for version {new_version} in CHANGELOG.md")
    print("2. Commit and push the changes")
    print("3. The GitHub Actions workflow will create a release and publish to PyPI")


if __name__ == "__main__":
    main() 