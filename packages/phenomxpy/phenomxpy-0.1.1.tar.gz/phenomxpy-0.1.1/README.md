![Pipeline Status](https://gitlab.com/imrphenom-dev/phenomxpy/badges/main/pipeline.svg)
[![Docs](https://img.shields.io/badge/docs-online-brightgreen)](https://phenomxpy.readthedocs.io/en/latest/)
[![coverage report](https://gitlab.com/imrphenom-dev/private/phenomxpy-private/badges/release-qc-phent/coverage.svg)](https://gitlab.com/imrphenom-dev/private/phenomxpy-private/-/commits/release-qc-phent)


# phenomxpy
Python implementation of the `IMRPhenomT` family of waveform models.

Available both for CPU and GPU. <br/>The CPU version is accelerated with `numba` by default, the GPU version with `cupy`. <br/>The parallelization happens at the level of the time array since each time point is independent.

## Installation

```bash
git clone https://gitlab.com/imrphenom-dev/phenomxpy.git
cd phenomxpy
pip install .
```

## Simple usage

```python
import phenomxpy

# Initialize approximant class
# Available approximants are: IMRPhenomT, IMRPhenomTHM, IMRPhenomTP, IMRPhenomTPHM
phen = IMRPhenomTHM(eta=..., total_mass=..., s1=...., s2=..., f_lower=..., option1=..., option2=...)

# Compute time domain polarizations
hp, hc = phen.compute_polarizations(times)

# Compute Fourier domain polarizations
hpf, hcf, frequencies = phen.compute_fd_polarizations(times)

# Compute individual modes (in time domain)
hlms = phen.compute_hlms(times)

# In the case of precessing approximants, can compute modes in different frames
hlms = phen.compute_CPmodes(times)
hlms = phen.compute_Jmodes(times)
hlms = phen.compute_L0modes(times)
```
The time array `times` can be a custom array. If `None`, then it computes an equispaced array with `delta_t` given in the class initialization.

If `total_mass` is not provided it assumes input arguments in NR units (i.e. f_lower, delta_t in mass units) and returns the waveform in NR units.

If `total_mass` and `distance` are provided, it returns the waveform in SI units.

**NOTE**: Fourier domain only support SI units.

## IMRPhenomT class details

An instance of the IMRPhenomT class initializes the amplitude and phase coefficients of the ansatzes. In this step there is no evaluation on any time array.

```python
phen = IMRPhenomT(waveform parameters and options)
```

One can generate the hlm mode and the polarizations in a custom time array as

```python
phen.compute_hlm(times)
phen.compute_polarizations(times)
```

In the initialization of PhenomT, the structures needed for the amplitude and phase coefficients are also initialized:

```python
IMRPhenomT
   - pWF
   - pPhase
   - pAmp
```

For the initialization of these clases, we employ "internal" methods denoted with an initial underscore, e.g. `_set_inspiral_coefficients()`. These methods are only employed in the initialization and only called by the `__init__` method.

These classes also define the ansatzes for each region, which can be evaluated in a custom time array. E.g.:
```python
pAmp.inspiral_ansatz(times)
pAmp.intermediate_ansatz(times)
pAmp.ringdown_ansatz(times)
```
and for the full imr region that is a piecewise function of the ansatzes above:
```python
pAmp.imr_amplitude(times)
```
For the phase and frequency we have e.g.:
```python
pPhase.inspiral_ansatz(times)
pPhase.inspiral_ansatz_omega(times)

pPhase.imr_phase(times)
pPhase.imr_omega(times)
```
If times=None, then an internally computed equispaced array is used.

The `pAmp.imr_amplitude` and `pPhase.imr_phase` are called when evaluating `phen.compute_hlm`.

## Manual docs built
 - sphinx-quickstart
 - sphinx-apidoc -o source/ ../phenomxpy
 - Add extensions and them to the generated conf.py
 - Add modules or other content to index.rst
 - make html

## Authors and acknowledgment
Cecilio García Quirós

If you use `phenomxpy` please cite

```
@misc{garcíaquirós2025gpuacceleratedlisaparameterestimation,
      title={GPU-accelerated LISA parameter estimation with full time domain response}, 
      author={Cecilio García-Quirós and Shubhanshu Tiwari and Stanislav Babak},
      year={2025},
      eprint={2501.08261},
      archivePrefix={arXiv},
      primaryClass={gr-qc},
      url={https://arxiv.org/abs/2501.08261}, 
}
```