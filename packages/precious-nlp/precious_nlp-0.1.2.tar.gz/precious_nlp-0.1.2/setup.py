#!/usr/bin/env python3
"""
Setup script for the Precious package.
A tokenizer-free NLP library with T-FREE, CANINE, and byte-level approaches.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

# Get version
def get_version():
    version_file = os.path.join("src", "precious", "__init__.py")
    with open(version_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")
    return "0.1.0"

setup(
    name="precious-nlp",
    version=get_version(),
    author="bimri",
    author_email="bimri@outlook.com",
    description="A tokenizer-free NLP library with T-FREE, CANINE, and byte-level approaches",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/bimri/precious",
    project_urls={
        "Bug Reports": "https://github.com/bimri/precious/issues",
        "Source": "https://github.com/bimri/precious",
        "Documentation": "https://github.com/bimri/precious/blob/main/docs/API_REFERENCE.md",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
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
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.8",
    install_requires=[
        "torch>=1.9.0",
        "numpy>=1.19.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=22.0",
            "isort>=5.0",
            "flake8>=4.0",
        ],
        "benchmarks": ["psutil>=5.8.0"],
        "docs": ["sphinx>=4.0", "sphinx-rtd-theme>=1.0"],
        "all": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=22.0",
            "isort>=5.0",
            "flake8>=4.0",
            "psutil>=5.8.0",
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "tokenization",
        "nlp",
        "transformers",
        "tokenizer-free",
        "canine",
        "tfree",
        "byte-level",
        "natural-language-processing",
        "deep-learning",
        "pytorch",
    ],
)
