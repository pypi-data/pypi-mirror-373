"""
Setup script for mizuio package.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements from requirements.txt
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(requirements_path):
        with open(requirements_path, "r", encoding="utf-8") as fh:
            return [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    return []

setup(
    name="mizuio",
    version="0.1.0",
    author="Mert Sakızcı",
    author_email="mertskzc@gmail.com",
    description="A comprehensive Python data processing tool for cleaning, visualization, and analysis",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/mertskzc/mizu",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
            "sphinx-autodoc-typehints>=1.12",
        ],
    },
    entry_points={
        "console_scripts": [
            "mizu=mizu.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "data-science",
        "data-analysis",
        "data-cleaning",
        "data-visualization",
        "pandas",
        "numpy",
        "matplotlib",
        "seaborn",
        "machine-learning",
        "data-processing",
    ],
    project_urls={
        "Bug Reports": "https://github.com/mertskzc/mizu-io/issues",
        "Source": "https://github.com/mertskzc/mizu-io"     
    },
)
