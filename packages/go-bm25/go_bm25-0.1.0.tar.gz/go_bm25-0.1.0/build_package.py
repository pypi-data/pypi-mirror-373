#!/usr/bin/env python3
"""
Build script for go-bm25 package.
This script helps build the Python package and can also trigger Go compilation.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def detect_python():
    """Detect the appropriate Python executable."""
    for cmd in ['python3', 'python', 'py']:
        try:
            result = subprocess.run([cmd, '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                return cmd
        except FileNotFoundError:
            continue
    return 'python3'  # fallback

def run_command(cmd, cwd=None, check=True):
    """Run a shell command."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error running command: {cmd}")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        sys.exit(1)
    return result

def clean_build():
    """Clean build artifacts."""
    print("Cleaning build artifacts...")
    dirs_to_clean = ["build", "dist", "*.egg-info", "__pycache__"]
    for pattern in dirs_to_clean:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"Removed {path}")
            else:
                path.unlink()
                print(f"Removed {path}")

def build_python_package():
    """Build the Python package."""
    python_cmd = detect_python()
    print(f"Building Python package using {python_cmd}...")
    
    # Clean previous builds
    clean_build()
    
    # Build the package
    run_command(f"{python_cmd} -m build")
    
    print("Python package built successfully!")

def install_package():
    """Install the package in development mode."""
    # Detect pip command
    pip_cmd = 'pip3' if detect_python() == 'python3' else 'pip'
    print(f"Installing package in development mode using {pip_cmd}...")
    run_command(f"{pip_cmd} install -e .")
    print("Package installed successfully!")

def build_go_bindings():
    """Build Go bindings if Go is available."""
    try:
        # Check if Go is available
        result = subprocess.run(["go", "version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("Go found, building bindings...")
            run_command("cd bm25 && make", check=False)
        else:
            print("Go not found, skipping Go bindings build")
    except FileNotFoundError:
        print("Go not found, skipping Go bindings build")

def main():
    """Main build function."""
    if len(sys.argv) < 2:
        print("Usage: python build_package.py [clean|build|install|go|all]")
        print("  clean  - Clean build artifacts")
        print("  build  - Build Python package")
        print("  install- Install package in development mode")
        print("  go     - Build Go bindings")
        print("  all    - Clean, build Go bindings, build Python package, and install")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "clean":
        clean_build()
    elif command == "build":
        build_python_package()
    elif command == "install":
        install_package()
    elif command == "go":
        build_go_bindings()
    elif command == "all":
        clean_build()
        build_go_bindings()
        build_python_package()
        install_package()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()

