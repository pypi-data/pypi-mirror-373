# BubbleBarrier

[![PyPI version](https://badge.fury.io/py/bubblebarrier.svg)](https://badge.fury.io/py/bubblebarrier)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/SOYONAOC/BubbleBarrier/main.yml?branch=main)](https://github.com/SOYONAOC/BubbleBarrier/actions)

A Python package for barrier calculations in cosmic reionization models, providing essential tools for modeling the physics of ionized bubbles in the early universe.

## Overview

The `BubbleBarrier` package provides a framework for calculating the density barrier (δ_v) required for cosmic structure formation within ionized regions during the Epoch of Reionization. It implements self-consistent models for ionization balance, halo mass functions, and feedback mechanisms.

This tool is designed for researchers and students in cosmology and astrophysics studying the 21cm signal, reionization simulations, and the interplay between galaxies and the intergalactic medium.

## Core Features

- **Barrier Function Calculation**: Computes the critical density barrier `δ_v` for different halo masses.
- **Ionization Modeling**: Self-consistent calculation of ionizing photon production (`N_ion`).
- **Minihalo Effects**: Includes options to model the impact of X-ray heating from minihalos.
- **Custom Power Spectrum**: Utilizes `camb` for cosmological calculations and allows for custom power spectrum models.
- **Efficient & Cached**: Caches intermediate results to disk (`.npy` files) for significantly faster subsequent calculations.

## Installation

Install the package directly from PyPI:

```bash
pip install bubblebarrier
```

## Quick Start

Here is a simple example of how to calculate the barrier height for a given halo mass.

```python
import numpy as np
from bubblebarrier import Barrier

# 1. Initialize the barrier model for a specific redshift
#    (fesc, qion, etc., have default values but can be specified)
barrier_model = Barrier(z_v=10.0)

# 2. Define a halo mass in solar masses
halo_mass = 1e15  # M_sun

# 3. Calculate the barrier height
delta_v = barrier_model.Calcul_deltaVM(halo_mass)
print(f"For a halo of {halo_mass:.1e} M_sun at z={barrier_model.z:.1f}, the barrier height is δ_v = {delta_v:.3f}")

# 4. Calculate the barrier including effects from minihalo X-ray heating
delta_v_minihalo = barrier_model.Calcul_deltaVM_Minihalo(halo_mass)
print(f"Including minihalo effects, the barrier is δ_v = {delta_v_minihalo:.3f}")
```

## Dependencies

This package relies on a standard scientific Python stack:

- `numpy`
- `scipy`
- `astropy`
- `matplotlib`
- `pandas`
- `filelock`
- `camb`: For cosmological power spectra.
- `massfunc`: For halo mass function calculations.

## Citation

If you use `BubbleBarrier` in your research, please cite the repository.

```bibtex
@misc{bubblebarrier2025,
  author = {Hajime Hinata},
  title = {BubbleBarrier: A Python package for reionization bubble modeling},
  year = {2025},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/SOYONAOC/BubbleBarrier}}
}
```

## Contributing

Contributions are welcome! Please feel free to fork the repository, create a feature branch, and open a Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.