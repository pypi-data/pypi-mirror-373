#!/usr/bin/env python3
"""
Setup script for go-bm25 package.
This file provides backward compatibility for older Python packaging tools.
The main configuration is in pyproject.toml.
"""

from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext
from setuptools.command.build_py import build_py
import os
import subprocess
import sys
import platform
from pathlib import Path

class GoExtension(Extension):
    """A setuptools Extension for Go shared libraries."""
    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)

class BuildGoExt(build_ext):
    """Custom build command to compile Go shared library."""
    
    def build_extension(self, ext):
        if not isinstance(ext, GoExtension):
            return super().build_extension(ext)
            
        # Check if Go is available
        try:
            subprocess.check_output(['go', 'version'])
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError("Go compiler not found. Please install Go 1.18 or later.")
        
        # Determine output filename based on platform
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        
        if platform.system() == "Darwin":
            lib_filename = "libbm25.dylib"
        elif platform.system() == "Windows":
            lib_filename = "libbm25.dll"
        else:  # Linux and others
            lib_filename = "libbm25.so"
        
        lib_path = os.path.join(extdir, "bm25", lib_filename)
        
        # Create output directory
        os.makedirs(os.path.dirname(lib_path), exist_ok=True)
        
        # Build Go shared library
        build_args = [
            'go', 'build',
            '-buildmode=c-shared',
            '-o', lib_path,
            'bm25.go', 'main.go'
        ]
        
        env = os.environ.copy()
        env['CGO_ENABLED'] = '1'
        env['CGO_CFLAGS'] = '-O3 -Wno-deprecated-declarations'
        
        print(f"Building Go shared library: {' '.join(build_args)}")
        subprocess.check_call(build_args, cwd=ext.sourcedir, env=env)
        print(f"Go shared library built: {lib_path}")

class BuildPyWithGo(build_py):
    """Custom build_py command that ensures Go library is built first."""
    
    def run(self):
        self.run_command('build_ext')
        super().run()

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="go-bm25",
    version="0.1.0",
    author="BM25 Contributors",
    description="High-performance BM25 ranking algorithm implementation with Go core and Python bindings",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/pentney/go-bm25",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.950",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    ext_modules=[GoExtension('go_bm25', sourcedir='.')],
    cmdclass={
        'build_ext': BuildGoExt,
        'build_py': BuildPyWithGo,
    },
    include_package_data=True,
    package_data={
        "bm25": ["*.so", "*.dll", "*.dylib"],
    },
    entry_points={
        "console_scripts": [
            "go-bm25=bm25.bm25:main",
        ],
    },
    zip_safe=False,
)
