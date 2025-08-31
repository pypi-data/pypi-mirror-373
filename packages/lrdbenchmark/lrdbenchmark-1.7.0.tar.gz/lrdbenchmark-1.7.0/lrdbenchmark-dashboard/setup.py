#!/usr/bin/env python3
"""
Setup script for LRDBenchmark Dashboard
A comprehensive web dashboard for long-range dependence analysis
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "LRDBenchmark Dashboard - Interactive web interface for long-range dependence analysis"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="lrdbenchmark-dashboard",
    version="1.0.0",
    author="Davian R. Chin",
    author_email="d.r.chin@pgr.reading.ac.uk",
    description="Interactive web dashboard for LRDBenchmark - Long-range dependence analysis",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/dave2k77/LRDBenchmark",
    project_urls={
        "Bug Tracker": "https://github.com/dave2k77/LRDBenchmark/issues",
        "Documentation": "https://github.com/dave2k77/LRDBenchmark/tree/master/documentation",
        "Live Dashboard": "https://lrdbenchmark-dev.streamlit.app/",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Mathematics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "deploy": [
            "streamlit>=1.28.0",
            "plotly>=5.15.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "lrdbenchmark-dashboard=lrdbenchmark_dashboard.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "lrdbenchmark_dashboard": [
            "*.py",
            "*.md",
            "*.txt",
            ".streamlit/*",
        ],
    },
    keywords=[
        "long-range dependence",
        "hurst parameter",
        "time series analysis",
        "fractional brownian motion",
        "wavelet analysis",
        "streamlit",
        "dashboard",
        "data science",
        "statistics",
        "research",
    ],
    platforms=["any"],
    license="MIT",
    zip_safe=False,
)
