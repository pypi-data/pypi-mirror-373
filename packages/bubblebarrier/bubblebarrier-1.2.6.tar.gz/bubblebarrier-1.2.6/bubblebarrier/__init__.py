"""
BubbleBarrier: A Python package for calculating bubble barriers in cosmic reionization models.

This package provides tools for modeling ionized bubbles and barrier functions 
used in studies of the epoch of reionization.

Classes:
    Barrier: Computes barrier heights for ionization balance

Example:
    >>> from bubblebarrier import Barrier
    >>> barrier = Barrier(fesc=0.2, qion=20000.0, z_v=12.0)
    >>> N_ion = barrier.Nion(1e15, 0.1)
"""

from .barrier import Barrier
from . import PowerSpectrum

__version__ = "0.1.5"
__author__ = "Hajime Hinata"
__email__ = "onmyojiflow@gmail.com"
__license__ = "MIT"
__description__ = "Barrier calculations for cosmic reionization models"
__url__ = "https://github.com/SOYONAOC/BubbleBarrier"

# Define what gets imported with "from bubblebarrier import *"
__all__ = [
    "Barrier",
    "PowerSpectrum",
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "__description__",
    "__url__",
]

# Package metadata
__package_info__ = {
    "name": "bubblebarrier",
    "version": __version__,
    "author": __author__,
    "email": __email__,
    "description": __description__,
    "url": __url__,
    "license": __license__,
    "keywords": ["astrophysics", "cosmology", "reionization", "barrier", "halo", "ionization"],
    "classifiers": [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Astronomy",
        "Topic :: Scientific/Engineering :: Physics",
    ],
}

# Convenience function to get package information
def get_package_info():
    """Return package metadata as a dictionary."""
    return __package_info__.copy()

# Version checking utility
def check_version():
    """Print the current version of bubblebarrier."""
    print(f"bubblebarrier version {__version__}")
    return __version__
