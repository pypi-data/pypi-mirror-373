#!/usr/bin/env python3
"""
Version management script for laneful.

Usage:
    python scripts/bump_version.py --dev               # Set to dev version for TestPyPI
    python scripts/bump_version.py --release 1.0.0     # Set release version for PyPI
    python scripts/bump_version.py --show              # Show current version
"""

import argparse
import re
import sys
from pathlib import Path

def get_pyproject_path():
    """Get path to pyproject.toml."""
    return Path(__file__).parent.parent / "pyproject.toml"

def get_current_version():
    """Get current version from pyproject.toml."""
    pyproject_path = get_pyproject_path()
    content = pyproject_path.read_text()
    
    match = re.search(r'^version = "([^"]+)"', content, re.MULTILINE)
    if not match:
        raise ValueError("Could not find version in pyproject.toml")
    
    return match.group(1)

def set_version(new_version):
    """Set version in pyproject.toml."""
    pyproject_path = get_pyproject_path()
    content = pyproject_path.read_text()
    
    # Update version
    content = re.sub(
        r'^version = "[^"]+"',
        f'version = "{new_version}"',
        content,
        flags=re.MULTILINE
    )
    
    pyproject_path.write_text(content)
    print(f"✓ Updated version to {new_version}")

def make_dev_version(base_version=None):
    """Create a dev version for TestPyPI."""
    if base_version is None:
        current = get_current_version()
        # Remove .dev suffix if present
        base_version = re.sub(r'\.dev\d*$', '', current)
    
    # Get git commit count for unique dev versions
    import subprocess
    try:
        result = subprocess.run(
            ['git', 'rev-list', '--count', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        commit_count = result.stdout.strip()
        dev_version = f"{base_version}.dev{commit_count}"
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback if git is not available
        dev_version = f"{base_version}.dev0"
    
    return dev_version

def main():
    parser = argparse.ArgumentParser(description="Manage package version")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dev", action="store_true", help="Set to dev version")
    group.add_argument("--release", metavar="VERSION", help="Set release version")
    group.add_argument("--show", action="store_true", help="Show current version")
    
    args = parser.parse_args()
    
    try:
        if args.show:
            current = get_current_version()
            print(f"Current version: {current}")
            
            if ".dev" in current:
                print("📦 Development version (suitable for TestPyPI)")
            else:
                print("🚀 Release version (suitable for PyPI)")
        
        elif args.dev:
            dev_version = make_dev_version()
            set_version(dev_version)
            print(f"📦 Set development version: {dev_version}")
            print("   This version will be published to TestPyPI on next push to main")
        
        elif args.release:
            version = args.release
            # Validate version format
            if not re.match(r'^\d+\.\d+\.\d+$', version):
                print("❌ Version must be in format x.y.z (e.g., 1.0.0)")
                sys.exit(1)
            
            set_version(version)
            print(f"🚀 Set release version: {version}")
            print(f"   Create a tag with 'git tag v{version}' to publish to PyPI")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
