Installation
============

.. code-block:: bash

   git clone https://gitlab.com/imrphenom-dev/phenomxpy.git
   cd phenomxpy
   pip install .

Simple usage
============

.. code-block:: python
   
   import phenomxpy

   # Initialize approximant class
   # Available approximants are: IMRPhenomT, IMRPhenomTHM, IMRPhenomTP, IMRPhenomTPHM
   phen = IMRPhenomTHM(eta=..., total_mass=..., s1=...., s2=..., f_lower=..., option1=...)

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

The time array ``times`` can be a custom array. If ``None``, then it computes an equispaced array with ``delta_t`` given in the class initialization.

If ``total_mass`` is not provided it assumes input arguments in NR units (i.e. ``f_lower``, ``delta_t`` in mass units) and returns the waveform in NR units.

If ``total_mass`` and ``distance`` are provided, it returns the waveform in SI units.

.. note:: Fourier domain only support SI units.