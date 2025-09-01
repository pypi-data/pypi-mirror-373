# Copyright (C) 2023  Cecilio García Quirós
"""
Parent class
------------

.. autoclass:: phenomxpy.phenomt.phenomt._PhenomT
    :members:
    :private-members:
    :undoc-members:
    :show-inheritance:
    :noindex:

IMRPhenomT
----------

.. autoclass:: phenomxpy.phenomt.phenomt.IMRPhenomT
    :members:
    :private-members:
    :undoc-members:
    :show-inheritance:
    :noindex:

IMRPhenomTHM
------------

.. autoclass:: phenomxpy.phenomt.phenomt.IMRPhenomTHM
    :members:
    :private-members:
    :undoc-members:
    :show-inheritance:
    :noindex:
"""

import numpy as np

try:
    import cupy as cp
except ImportError:
    cp = None

from .internals import pAmp, pPhase, pWFHM, Cache
from .numba_ansatze import combine_amp_phase
from phenomxpy.utils import (
    check_equal_blackholes,
    AmpNRtoSI,
    ModeToString,
    SpinWeightedSphericalHarmonic,
    MasstoSecond,
    SecondtoMass,
    logger,
    move_to_front,
    remove_duplicates,
    rotate_by_polarization_angle,
)
from phenomxpy.fft import FFT_polarizations, time_array_condition_stage1, time_array_condition_stage2, resize_timeseries, check_pow_of_2


class _PhenomT:
    """
    Parent class with common methods for the IMRPhenomT family: ``IMRPhenomT``, ``IMRPhenomTHM``, ``IMRPhenomTP``, ``IMRPhenomTPHM``.
    """

    def condition_polarizations(self, hp, hc):
        """
        Condition time domain polarizations for proper FFT Fourier Transform.

        Two stages conditioning:

            1. Apply tappering at the beginning and a high-pass filter.
            2. Tappering at the end and one cycle at low frequency.

        Then resize the series to match the input ``delta_f`` if specified or adjust to a power of 2 length.

        Parameters
        ----------
        hp, hc:
            1D arrays with the time series of the polarizations.
        resize_series: bool
            If ``True``, resize the series to match the input delta_f or adjust to a power of 2 length.
        high_pass_filter_lal: bool
            If ``True``, apply a high-pass filter using the LALSuite wrapper.

        Returns
        -------
        Tuple of 2 1D ndarrays
            hp(t), hc(t) conditioned polarizations.
        """

        delta_t = self.pWF.delta_t_sec
        delta_f = self.pWF.delta_f
        cparams = self.pWF.cparams

        # Conditioning stage 1
        hp, hc = time_array_condition_stage1(
            hp,
            hc,
            self.pWF.delta_t_sec,
            cparams["extra_time_fraction"] * cparams["tchirp"] + cparams["textra"],
            cparams["original_f_min"],
            xp=self.xp,
            high_pass_filter_lal=self.pWF.extra_options.get("high_pass_filter_lal", False),
        )

        # Conditioning stage 2
        hp, hc = time_array_condition_stage2(hp, hc, self.pWF.delta_t_sec, cparams["f_min0"], cparams["fisco"], xp=self.xp)

        # Resize time series
        if self.pWF.extra_options.get("resize_series", False):
            f_nyquist = 0.5 / delta_t
            N = len(hp)

            if delta_f == 0 or delta_f is None:
                chirplen = N
                _, chirplen_exp = check_pow_of_2(chirplen)
                chirplen = 2 ** (chirplen_exp)
                delta_f = 1.0 / (chirplen * delta_t)
            else:
                chirplen = 2 * f_nyquist / delta_f
                if chirplen < N:
                    logger.warning(
                        f"Specified frequency interval of {delta_f} Hz is too large "
                        f"for a chirp of duration {N * delta_t} s with Nyquist frequency {f_nyquist} Hz. "
                        f"The inspiral will be truncated."
                    )
            chirplen = int(np.round(chirplen))

            hp, times = resize_timeseries(hp, delta_t, N - chirplen, chirplen, xp=self.xp)
            hc, _ = resize_timeseries(hc, delta_t, N - chirplen, chirplen, xp=self.xp)

            # Update epoch and delta_f after resizing
            self.epoch = times[0]
            self.pWF.delta_f = delta_f
        else:
            times = MasstoSecond(self.set_time_array(), self.pWF.total_mass)

        return hp, hc, times

    def compute_fd_polarizations(self, f_min_fd=None):
        """
        Compute FFT Fourier ransform of the time domain conditioned polarizations hp, hc.

        Return only the positive frequencies spectrum since for real time series h(-f)=h*(f).

        By default the frequency series starts at 0, but can be changed with the ``f_min`` argument.

        Return
        ------
        Tuple of 3 1D ndarrays
            hp(f), hc(f), frequencies
        """

        if self.pWF.condition:
            self.pWF.extra_options["resize_series"] = True
            hp, hc, _ = self.compute_polarizations()
            hp, hc, frequencies = FFT_polarizations(hp, hc, self.pWF.delta_t_sec, self.pWF.delta_f, f_min_fd=f_min_fd)
            return hp, hc, frequencies
        else:
            raise ValueError("condtion must be True to use compute_fd_polarizations")

    def set_time_array(self, times=None):
        """
        Set time array where to compute hlms and polarizations.

        If ``times`` is ``None`` and ``delta_t`` >0, compute an internal equispaced time array and stores it as ``self.times``.
        """

        if times is not None:
            # Case times have astropy units
            if hasattr(times, "unit"):
                if str(getattr(times, "unit")) == "s":
                    if self.pWF.total_mass == 0:
                        raise ValueError("Need to provide total_mass>0 when times have units of second.")
                    return SecondtoMass(times.value, self.pWF.total_mass)
                else:
                    return times.value
            # Case times does not have units
            if self.pWF.total_mass > 0:
                times = SecondtoMass(times, self.pWF.total_mass)
            return times
        elif getattr(self, "times", None) is not None:
            return self.times
        elif self.pWF.delta_t_sec > 0:
            # Compute the internal time array
            self.times = self.xp.concatenate(
                (self.xp.flip(-self.xp.arange(1, self.pWF.len_neg + 1) * self.pWF.delta_t), self.xp.arange(self.pWF.len_pos) * self.pWF.delta_t)
            )
            self.epoch = MasstoSecond(self.times[0], self.pWF.total_mass) if self.pWF.total_mass is not None else self.times[0]
            return self.times
        else:
            raise ValueError("delta_t must be set > 0 to compute internal equispaced time array.")


class IMRPhenomTHM(_PhenomT):
    """
    Class for the IMRPhenomTHM model :cite:`phenomthm`, aligned-spin with subdominant harmonics.

    Initialize an ``IMRPhenomT`` class for each (l,m) harmonic.

    Parameters
    ----------
    mode_array: None, list
        List with the modes to be computed in format [[l,m], [,], ...]. If ``None`` use default array (22, 21, 33, 44, 55 and negative moes).
    add_20_mode: bool
        Add the 20 mode to the list of modes.
    cuda: bool
        If ``True``, use GPU and cupy, if not use CPU and numpy.
    pWF_input: pWF
        pWF object with common waveform quantities for all the modes.

    Attributes
    ----------
    phenT_classes: dict
        Dictionary with initialiazed ``IMRPhenomT`` classes for each harmonic. E.g. {'22':phen22, '21':phen21, ...}. Keys only show positive modes since the class is the same for the negative ones.
    pWF: pWF
        pWF object with common quantities for all modes
    mode_array: list
        List with the modes to be computed in format [[l,m], [,], ...]. For equal black holes cases, odd modes are removed from ``mode_array``.
    lmax: int
        maximum l in the mode_array
    times: 1D ndarray
        Internally computed equispaced time array if input time array is ``None``. Only set if one the evaluation methods is called.
    """

    @staticmethod
    def metadata():
        metadata = {
            "type": "aligned_spin",
            "f_ref_spin": True,
            "modes": True,
            "polarizations": True,
            "implemented_domain": "time",
            "approximant": "IMRPhenomTHM",
            "implementation": "",
            "conditioning_routines": "",
        }
        return metadata

    def __init__(self, mode_array=None, add_20_mode=False, cuda=False, pWF_input=None, **kwargs):

        # Set proper module for cpu/gpu
        self.xp = cp if cuda and cp is not None else np

        # Set up mode array
        # NOTE Be careful changing the default array. This mode order is assumed by numba_wigner_from_quaternions_default_modes_i
        self.default_mode_array = [[2, 2], [2, 1], [3, 3], [4, 4], [5, 5], [2, -2], [2, -1], [3, -3], [4, -4], [5, -5]]
        if mode_array is None:
            self.mode_array = self.default_mode_array
            if add_20_mode is True:
                self.mode_array.append([2, 0])
        else:
            self.mode_array = mode_array
            # Put the 22 mode the first one to recycle quantities
            if [2, -2] in self.mode_array:
                self.mode_array = move_to_front(self.mode_array, [2, -2])
            if [2, 2] in self.mode_array:
                self.mode_array = move_to_front(self.mode_array, [2, 2])
            # Remove duplicated modes
            self.mode_array = remove_duplicates(self.mode_array)
            # Remove non-supported modes
            for mode in self.mode_array:
                if mode not in self.default_mode_array:
                    self.mode_array.remove(mode)
                    logger.warning(f"Mode {mode} not supported, removing from mode_array")
        self.lmax = np.max(np.array(self.mode_array)[:, 0])

        # Dictionary storing IMRPhenomT objects for each mode
        self.phenT_classes = {}

        # Compute first the 22
        mode22 = IMRPhenomT(**kwargs, mode=[2, 2], cuda=cuda, pWF_input=pWF_input)
        self.phenT_classes["22"] = mode22
        self.pWF = mode22.pWF

        # Remove odd modes for equal black holes since they are zero
        if check_equal_blackholes(self.pWF):
            logger.warning("Equal black holes, skipping odd modes")
            self.mode_array = [mode for mode in self.mode_array if abs(mode[1]) % 2 == 0]
            if self.mode_array == []:
                raise ValueError("No non-zero modes requested for this case")

        # Compute the IMRPhenomT classes for each HM subdominant mode
        for mode in self.mode_array:
            pos_mode = [mode[0], abs(mode[1])]
            if (mode[1] < 0 and pos_mode in self.mode_array) or ModeToString(pos_mode) == "22":
                continue
            self.phenT_classes[ModeToString(pos_mode)] = IMRPhenomT(**kwargs, cuda=cuda, mode=pos_mode, mode22=mode22, pWF_input=mode22.pWF)

    def compute_hlms(self, times=None):
        """
        Compute all the hlms modes in a time array.

        Parameters
        ----------
        times: 1D ndarray
            Time array where to evaluate the polarizations. If None, use the internal one self.times.

        Return
        ------
        dict
            hlms(t). Each element contains the hlm array for each mode. The keys are the mode strings, e.g. '22', '21', '2-2', etc.
        """

        # Dictionary with the harmonics
        hlms = {}

        # This stores quantities computed in the time array for the 22 that are recycled for the higher modes
        cache = None

        # Loop over modes
        keys = {}
        for idx, mode in enumerate(self.mode_array):
            l = mode[0]
            m = mode[1]
            key = str(l) + str(abs(m))
            if key in keys:
                # Recycle mode if it has been already computed for the opposite mode
                hlm = hlms[key]
            else:
                # Compute hlm
                keys[key] = idx
                phen = getattr(self, "phenT_classes")[key]
                # Cache quantities from the 22 mode
                if key == "22":
                    hlm, times, cache = phen.compute_hlm(times=times, return_cache=True)
                else:
                    hlm, times = phen.compute_hlm(times=times, cache=cache)

            # Use equatorial symmetry for the negative modes
            if m < 0:
                hlm = (-1) ** l * self.xp.conj(hlm)

            hlms[ModeToString(mode)] = hlm

        return hlms, times

    def compute_polarizations(self, times=None):
        """
        Compute hp, hc in a time array.

        Parameters
        ----------
        times: 1D ndarray
            Time array where to evaluate the polarizations. If ``None``, use the internal one ``self.times``.
        compute_hlms_at_once: bool
            If ``True``, compute all hlms at once and build strain. If ``False``, compute hlms individually in a loop to save memory.

        Return
        ------
        Tuple of 2 1D ndarrays
            hp(t), hc(t)
        """

        # Compute all hlms at once and build strain
        if self.pWF.extra_options.get("compute_hlms_at_once", False):
            # Compute hlms if needed
            hlms, times = self.compute_hlms(times=times)

            # Sum all the modes as += hlm * Ylm
            strain = 0
            for mode in self.mode_array:
                l = mode[0]
                m = mode[1]
                Ylm = SpinWeightedSphericalHarmonic(self.pWF.inclination, np.pi / 2 - self.pWF.phi_ref, l, m)
                hlm = hlms[ModeToString(mode)]
                strain += hlm * Ylm

        # Compute hlms individually in loop to save memory (default)
        else:
            # Sum all the modes as += hlm * Ylm
            strain = 0
            cache = None

            modes_already_computed = []
            for mode in self.mode_array:
                add_opposite_mode = False
                l = mode[0]
                m = mode[1]
                if [l, m] not in modes_already_computed:
                    if [l, -m] in self.mode_array:
                        add_opposite_mode = True if m != 0 else False
                        modes_already_computed.append([l, -m])

                    key = str(l) + str(abs(m))
                    phen = getattr(self, "phenT_classes")[key]
                    # Cache quantities from the 22 mode
                    if key == "22":
                        hlm, times, cache = phen.compute_hlm(times=times, return_cache=True)
                    else:
                        hlm, times = phen.compute_hlm(times=times, cache=cache)

                    # Apply equatorial symmetry for negative modes
                    if m < 0:
                        hlm = (-1) ** l * self.xp.conj(hlm)

                    Ylm = SpinWeightedSphericalHarmonic(self.pWF.inclination, np.pi / 2 - self.pWF.phi_ref, l, m)
                    strain += hlm * Ylm

                    if add_opposite_mode:
                        Ylmm = SpinWeightedSphericalHarmonic(self.pWF.inclination, np.pi / 2 - self.pWF.phi_ref, l, -m)
                        strain += (-1) ** l * self.xp.conj(hlm) * Ylmm

        # Polarizations from strain
        hp = self.xp.real(strain)
        hc = -self.xp.imag(strain)

        # Rotate polarizations by polarization_angle
        if self.pWF.polarization_angle != 0:
            hp, hc = rotate_by_polarization_angle(hp, hc, self.pWF.polarization_angle)

        # Condition polarizations
        if self.pWF.condition:
            hp, hc, times = self.condition_polarizations(hp, hc)

        return hp, hc, times


class IMRPhenomT(_PhenomT):
    """
    Class for aligned-spin, single harmonic.

    Can initialize any harmonic, not only the 22.

    The 22 mode is described in :cite:`phenomt`, while the subdominant modes in :cite:`phenomthm`.

    Initialize ``pWF``, ``pAmp`` and ``pPhase`` objects for a specific harmonic.

    Parameters
    ----------
    mode: list [l,m]
        Indeces for the spherical harmonic to be initialized.
    mode22: IMRPhenomT
        Class with the 22 mode initialized. To be used by the subdominant harmonics.
    cuda: bool
        If ``True``, use GPU and cupy, if not use CPU and numpy.

    Attributes
    ----------
    pWF: pWF
        pWF object with common quantities for all modes
    pAmp: pAmp
        pAmp object for amplitude coefficients
    pPhase: pPhase
        pPhase object for phase coefficients

    pPhase22: pPhase
        pPhase object of the 22 mode to be used by higher modes
    mode20: phenomxpy.mode20
        Class for the 20 mode

    """

    @staticmethod
    def metadata():
        metadata = {
            "type": "aligned_spin",
            "f_ref_spin": True,
            "modes": True,
            "polarizations": True,
            "implemented_domain": "time",
            "approximant": "IMRPhenomT",
            "implementation": "",
            "conditioning_routines": "",
        }
        return metadata

    def __init__(self, mode=[2, 2], mode22=None, cuda=False, **kwargs):

        # Set proper module for cpu/gpu
        self.xp = cp if cuda and cp is not None else np

        # For a subdominant harmonic we need first the mode22 if not yet computed.
        if mode != [2, 2] and mode != [2, -2] and mode22 is None:
            mode22 = IMRPhenomT(**kwargs, cuda=cuda, mode=[2, 2])

        # Read the pPhase22 object from mode22 if already computed
        self.pPhase22 = mode22.pPhase if mode22 is not None else None

        # Set pWF structure for one specific mode
        # If pWF_input is in kwargs, it recycles it and adds the mode specific properties
        self.pWF = pWFHM(**kwargs, mode=mode, cuda=cuda)

        # Set amplitude and phase coefficients (pAmp, pPhase)

        # 22 mode
        if self.pWF.mode == 22:
            # For the 22 mode the phase coefficients need to be computed before the amplitude coefficients
            self.pPhase = pPhase(self.pWF)
            self.pAmp = pAmp(self.pWF, self.pPhase)

        # Higher modes
        elif self.pPhase22 is not None:
            if self.pWF.mode == 20:
                self.mode20 = mode20(self.pWF, self.pPhase22)
            else:
                # For the higher modes, the amplitude coefficients need to be computed before the phase coefficients
                self.pAmp = pAmp(self.pWF, self.pPhase22)
                self.pPhase = pPhase(self.pWF, pPhase22=self.pPhase22, omegaCutPNAMP=self.pAmp.omegaCutPNAMP, phiCutPNAMP=self.pAmp.phiCutPNAMP)
        else:
            raise SystemError("Need pPhase22 argument for higher modes")

    def compute_hlm(self, times=None, cache=None, return_cache=False):
        """
        Compute hlm mode in time array.

        Parameters
        ----------
        times: 1D ndarray
            Time array where to evaluate the hlm. If None, use the internal one self.times.
        cache: Cache
            Cache object with imr_22phase and x_insp, only used for the 22 mode.
        return_cache: bool
            If True, return hlm and cache object.

        Returns
        -------
        1D ndarray
            hlm(t)
        (Optionally for the 22 mode)
        1Dndarray, Cache:
            hlm(t), cache object with imr_22phase and x_insp if return_cache=True
        """

        # Set time array
        times = self.set_time_array(times=times)

        # The 20 mode is generated differently
        if self.pWF.mode == 20:
            hlm = self.mode20.mode20_mem_osc(times)

        # Non 20 modes: amp * exp(-I phase)
        else:
            # Compute amplitude in time array
            amplitude = self.pAmp.imr_amplitude(times, cache=cache)
            # Only for the 22 we take the absolute value
            amplitude = self.xp.abs(amplitude) if self.pWF.mode == 22 else amplitude

            # Compute phase in time array
            imr_phase = self.pPhase.imr_phase(times=times, cache=cache)
            phase = imr_phase - self.pPhase.phoff - self.pPhase.phiref0 * self.pWF.emm / 2.0

            # Build waveform hlm = amp * exp(-I phase)
            if self.pWF.numba_ansatze is False:
                hlm = amplitude * self.xp.exp(-1j * phase)
            else:
                hlm = combine_amp_phase(amplitude, phase)

        # Transform to SI units if required
        if self.pWF.distance > 0 and self.pWF.total_mass > 0:
            hlm = AmpNRtoSI(hlm, self.pWF.distance, self.pWF.total_mass)

        if self.pWF.total_mass > 0:
            times = MasstoSecond(times, self.pWF.total_mass)

        # If return_cache is True, return the hlm and the cache with imr_22phase and x_insp
        if return_cache:
            if self.pWF.mode != 22:
                raise ValueError("cache option is only valid for 22 mode")
            return hlm, times, Cache(imr_22phase=imr_phase, x_insp=self.pAmp.x_insp)

        return hlm, times

    def compute_polarizations(self, times=None):
        """
        Compute hp, hc for one mode and its negative counterpart.

        Parameters
        ----------
        times: 1D ndarray or ``None``
            Time array where to evaluate the polarizations. If ``None``, use the internal arry ``self.times``. If not ``None``, recompute the hlms in the new array.

        Return
        ------
        Tuple of 2 1D ndarrays
            hp(t), hc(t) contribution for one mode and its opposite one
        """

        # Compute one single mode
        hlm, times = self.compute_hlm(times=times)

        # Get opposite one by equatorial symmetry
        hlmm = (-1) ** self.pWF.ell * self.xp.conj(hlm)

        # Compute Ylms for both modes
        Ylm = SpinWeightedSphericalHarmonic(self.pWF.inclination, np.pi / 2 - self.pWF.phi_ref, self.pWF.ell, self.pWF.emm)
        Ylmm = SpinWeightedSphericalHarmonic(self.pWF.inclination, np.pi / 2 - self.pWF.phi_ref, self.pWF.ell, -self.pWF.emm)

        # Build strain for one mode with its opposite one
        strain = hlm * Ylm + hlmm * Ylmm

        # Polarizations from complex strain
        hp = self.xp.real(strain)
        hc = -self.xp.imag(strain)

        # Rotate polarizations by polarization_angle
        if self.pWF.polarization_angle != 0:
            hp, hc = rotate_by_polarization_angle(hp, hc, self.pWF.polarization_angle)

        # Condition polarizations
        if self.pWF.condition:
            hp, hc, times = self.condition_polarizations(hp, hc)

        return hp, hc, times
