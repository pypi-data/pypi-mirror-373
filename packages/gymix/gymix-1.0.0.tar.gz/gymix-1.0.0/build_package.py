#!/usr/bin/env python3
"""
Build script for Gymix Python SDK.

This script helps with building and publishing the package to PyPI.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*50}")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"ERROR: {description} failed!")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        return False
    else:
        print(f"SUCCESS: {description} completed!")
        if result.stdout:
            print("Output:", result.stdout)
        return True


def main():
    """Main build process."""
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print("Gymix Python SDK Build Script")
    print("============================")
    
    # 1. Clean previous builds
    if not run_command("make clean", "Cleaning previous builds"):
        sys.exit(1)
    
    # 2. Run tests
    if not run_command("python -m pytest tests/", "Running tests"):
        print("\nWarning: Tests failed. Continue anyway? (y/N)")
        response = input().lower().strip()
        if response != 'y':
            sys.exit(1)
    
    # 3. Check code formatting
    if not run_command("python -m black --check gymix tests example.py", "Checking code format"):
        print("Code formatting issues found. Run 'make format' to fix them.")
        sys.exit(1)
    
    # 4. Run linting  
    if not run_command("python -m flake8 gymix tests", "Running linting"):
        print("Linting issues found. Please fix them before building.")
        sys.exit(1)
    
    # 5. Run type checking
    if not run_command("python -m mypy gymix", "Running type checks"):
        print("\nWarning: Type checking failed. Continue anyway? (y/N)")
        response = input().lower().strip()
        if response != 'y':
            sys.exit(1)
    
    # 6. Build package
    if not run_command("python -m build", "Building package"):
        sys.exit(1)
    
    print("\n" + "="*60)
    print("BUILD SUCCESSFUL!")
    print("="*60)
    print("\nPackage built successfully. Files created:")
    
    dist_dir = Path("dist")
    if dist_dir.exists():
        for file in dist_dir.iterdir():
            print(f"  - {file}")
    
    print("\nNext steps:")
    print("1. Test on TestPyPI: python -m twine upload --repository testpypi dist/*")
    print("2. Install from TestPyPI: pip install --index-url https://test.pypi.org/simple/ gymix")
    print("3. Test the installation")
    print("4. Upload to PyPI: python -m twine upload dist/*")
    print("\nOr use the Makefile commands:")
    print("  make upload-test  # Upload to TestPyPI")
    print("  make upload       # Upload to PyPI")


if __name__ == "__main__":
    main()
