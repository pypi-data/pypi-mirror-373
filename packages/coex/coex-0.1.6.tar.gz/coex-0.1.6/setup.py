#!/usr/bin/env python3
"""
Setup script for the coex library.
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements from requirements.txt
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="coex",
    version="0.1.4",
    author="torchtorchkimtorch",
    author_email="torchtorchkimtorch@users.noreply.github.com",
    description="Execute code snippets in isolated Docker environments with multi-language support and security protection",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/torchtorchkimtorch/coex",
    project_urls={
        "Bug Reports": "https://github.com/torchtorchkimtorch/coex/issues",
        "Source": "https://github.com/torchtorchkimtorch/coex",
        "Documentation": "https://github.com/torchtorchkimtorch/coex#readme",
    },
    packages=find_packages(exclude=["tests*", "examples*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing",
        "Topic :: System :: Software Distribution",
        "Topic :: Education",
        "Topic :: Security",
    ],
    keywords="docker, code-execution, sandbox, security, multi-language, testing, validation",
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-xdist>=3.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "isort>=5.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    platforms=["any"],
)
