.. phenomxpy documentation master file, created by
   sphinx-quickstart on Sun Jul 20 14:45:01 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to phenomxpy documentation!
===================================

Python implementation of the IMRPhenomT family of waveform models :cite:`phenomt, phenomthm, phenomtphm`.

Available both for CPU and GPU hardware. 

The CPU version is accelerated with ``numba`` by default, the GPU version with ``cupy``.

The parallelization happens at the level of the time array since each time point is independent.

.. toctree::
   :maxdepth: 1
   :caption: Getting started

   getting_started

.. toctree::
   :maxdepth: 1
   :caption: Approximants

   approximants

.. toctree::
   :maxdepth: 1
   :caption: Precession

   precession

.. toctree::
   :maxdepth: 1
   :caption: Interfaces

   interfaces

.. toctree::
   :maxdepth: 1
   :caption: Auxiliary modules

   auxiliary

.. toctree::
   :maxdepth: 1
   :caption: Examples

   examples/gwsignal

.. toctree::
   :maxdepth: 1
   :caption: Lalsuite differences

   lal_differences


.. toctree::
   :maxdepth: 2
   :caption: Others

   license
   bibliography
   Gitlab project <https://gitlab.com/imrphenom-dev/phenomxpy>


..    :maxdepth: 2
..    :caption: Contents:

..    phenomxpy

