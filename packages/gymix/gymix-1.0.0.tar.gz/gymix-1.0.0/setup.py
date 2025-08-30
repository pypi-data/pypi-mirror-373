#!/usr/bin/env python3
"""Setup configuration for gymix package."""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="gymix",
    version="1.0.0",
    author="Gymix Team",
    author_email="support@gymix.ir",
    description="Official Python SDK for Gymix API - Gym management and backup services",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mrssd/gymix-python-sdk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Office/Business",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "typing-extensions>=4.0.0;python_version<'3.8'",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.900",
            "twine>=3.0",
        ],
    },
    keywords="gymix api sdk gym management backup",
    project_urls={
        "Bug Reports": "https://github.com/mrssd/gymix-python-sdk/issues",
        "Source": "https://github.com/mrssd/gymix-python-sdk",
        "Documentation": "https://docs.gymix.ir/python-sdk",
    },
)
