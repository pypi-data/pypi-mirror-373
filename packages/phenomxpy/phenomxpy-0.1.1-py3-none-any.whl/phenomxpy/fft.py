# Copyright (C) 2023  Cecilio García Quirós
"""
Utilities for Fourier transform.
"""

import numpy as np
from scipy.signal import butter as butter_cpu, sosfiltfilt as sosfiltfilt_cpu

try:
    import cupy as cp
    from cupyx.scipy.signal import butter as butter_gpu, sosfiltfilt as sosfiltfilt_gpu
except:
    cp = None

from phenomxpy.utils import logger
from math import frexp

# FIXME better place for constants?
LAL_G_SI = 6.67430e-11
LAL_C_SI = 299792458
LAL_MSUN_SI = 1.988409870698050731911960804878414216e30
LAL_MRSUN_SI = 1.476625038050124729627979840144936351e3
LAL_MTSUN_SI = 4.925490947641266978197229498498379006e-6
LAL_PI = np.pi


def high_pass_time_series(time_series, dt, fmin, attenuation, N, xp=np):
    """
    Adapted from `gwsignal <https://git.ligo.org/lscsoft/lalsuite/-/blob/master/lalsimulation/python/lalsimulation/gwsignal/core/conditioning_subroutines.py>`_.

    High-pass filter a time series.

    Parameters
    ----------
    time_series: 1D ndarray
        Time series to filter
    dt: float
        Time spacing of input time series
    fmin : float
        Minimum frequency for high-pass
    attenuation : float
        Attenuation value at low-freq cut-off
    N : `float`
        Order of butterworth filter
    xp : np/cp
        Module to use for cpu/gpu

    Returns
    -------
    1D ndarray
        filtered time series

    """

    # Following butterworth filters as applied to LAL:
    # See : https://lscsoft.docs.ligo.org/lalsuite/lal/group___butterworth_time_series__c.html

    fs = 1.0 / dt  # Sampling frequency
    a1 = attenuation  # Attenuation at the low-freq cut-off

    w1 = np.tan(np.pi * fmin * dt)  # Transformed frequency variable at f_min
    wc = w1 * (1.0 / a1**0.5 - 1) ** (1.0 / (2.0 * N))  # Cut-off freq. from attenuation
    fc = fs * np.arctan(wc) / np.pi  # For use in butterworth filter

    # Construct the filter and then forward - backward filter the time-series
    if xp == np:
        sos = butter_cpu(N, fc, btype="highpass", output="sos", fs=fs)
        output = sosfiltfilt_cpu(sos, time_series)
    else:
        # This introduces a small difference O(10^-12) respect to the cpu version
        sos = butter_gpu(N, fc, btype="highpass", output="sos", fs=fs)
        output = sosfiltfilt_gpu(sos, time_series)

    return output


def time_array_condition_stage1(hp, hc, dt, t_extra, fmin, xp=np, high_pass_filter_lal=False):
    """
    Adapted from `gwsignal <https://git.ligo.org/lscsoft/lalsuite/-/blob/master/lalsimulation/python/lalsimulation/gwsignal/core/conditioning_subroutines.py>`_.

    Stage 1 of time-series conditioning - add taper and high-pass the time-series.

    Parameters
    ----------
    hp : `TimeSeries`
        GwPy TimeSeries object
    hc : `TimeSeries`
        GwPy TimeSeries object
    dt : `float`
        Sampling value of time series
    t_extra : `float`
        Initial extra time for conditioning
    fmin : `float`
        Minimum frequency for high-pass

    Return
    ------
    1D ndarray
        Stage1 conditioned time series

    """

    # Set the propoer module np/cp for cpu/gpu
    xp = cp.get_array_module(hp) if cp is not None else np

    # Generate the cos taper
    Ntaper = int(xp.round(t_extra / dt))
    if Ntaper > len(hp):
        Ntaper = len(hp)
    taper_array = xp.arange(Ntaper)
    w = 0.5 - 0.5 * xp.cos(taper_array * np.pi / Ntaper)
    hp[:Ntaper] *= w
    hc[:Ntaper] *= w

    # High pass filter the time series.
    if high_pass_filter_lal is False:
        # Replicate filter used in LAL. Machine precission is not always achieved.
        hp = high_pass_time_series(hp, dt, fmin, 0.99, 8.0, xp=xp)
        hc = high_pass_time_series(hc, dt, fmin, 0.99, 8.0, xp=xp)
    else:
        # Explicitly use the LAL filter to achieve machine precision when comparing to LAL
        import lal

        hp_lal = lal.CreateREAL8TimeSeries(name="hp", epoch=0, f0=0, deltaT=dt, sampleUnits=lal.StrainUnit, length=len(hp))
        hc_lal = lal.CreateREAL8TimeSeries(name="hc", epoch=0, f0=0, deltaT=dt, sampleUnits=lal.StrainUnit, length=len(hc))
        hp_lal.data.data = hp
        hc_lal.data.data = hc

        lal.HighPassREAL8TimeSeries(hp_lal, fmin, 0.99, 8)
        lal.HighPassREAL8TimeSeries(hc_lal, fmin, 0.99, 8)
        hp = hp_lal.data.data
        hc = hc_lal.data.data

    # Remove trailing zeroes from array
    xp.trim_zeros(hp, trim="b")
    xp.trim_zeros(hc, trim="b")

    return hp, hc


def time_array_condition_stage2(hp, hc, dt, fmin, fmax, xp=np):
    """
    Adapted from `gwsignal <https://git.ligo.org/lscsoft/lalsuite/-/blob/master/lalsimulation/python/lalsimulation/gwsignal/core/conditioning_subroutines.py>`_.

    Stage 2 of time-series conditioning - taper end of waveform based off maximum frequency

    Parameters
    ----------
    hp : `TimeSeries`
        GwPy TimeSeries object
    hc : `TimeSeries`
        GwPy TimeSeries object
    dt : `float`
        Sampling value of time series
    fmin : `float`
        Minimum frequency for high-pass
    fmax : `float`
        Minimum frequency for high-pass

    Return
    ------
    1D ndarray
        Stage2 conditioned time series
    """

    # Following XLALSimInspiralTDConditionStage2
    min_taper_samples = 4.0
    if len(hp) < 2 * min_taper_samples:
        logger.warning(f"Current waveform has less than {2 * min_taper_samples} samples: No Final tapering will be applied")
        return 0

    # taper end of waveform: 1 cycle at f_max; at least min_taper_samples
    # note: this tapering is done so the waveform goes to zero at the next
    # point beyond the end of the data
    ntaper = int(np.round(1.0 / (fmax * dt)))
    ntaper = np.max([ntaper, min_taper_samples])

    # Taper end of waveform
    taper_array = xp.arange(1, ntaper)
    w = 0.5 - 0.5 * xp.cos(taper_array * np.pi / ntaper)
    Nsize = len(hp)
    w_ones = xp.ones(Nsize)
    w_ones[int(Nsize - ntaper + 1) :] *= w[::-1]
    hp *= w_ones
    hc *= w_ones

    # Taper off one cycle at low frequency
    ntaper = np.round(1.0 / (fmin * dt))
    ntaper = np.max([ntaper, min_taper_samples])

    # Taper end of waveform
    taper_array = xp.arange(ntaper)
    w = 0.5 - 0.5 * xp.cos(taper_array * np.pi / ntaper)
    w_ones = xp.ones(Nsize)
    w_ones[: int(ntaper)] *= w
    hp *= w_ones
    hc *= w_ones

    return hp, hc


def resize_timeseries(h, dt, start_id, new_length, xp=np):
    """
    Adapted from `gwsignal <https://git.ligo.org/lscsoft/lalsuite/-/blob/master/lalsimulation/python/lalsimulation/gwsignal/core/conditioning_subroutines.py>`_.

    Resize a given gwpy TimeSeries which has a given length and starts at a point specified by start_id. If start_id
    is negative, the timeseries will be padded on the left with that amount.

    Parameters
    ----------
    h : numpy(cupy) array
       Time series that needs to be resized

    start_id : int
       If positive, index at which TimeSeries will now start from. If negative, TimeSeries will be zero padded with
       that length on the left.

    new_length : int
        Final length of output array. This will be done by clippling the end of the TimeSeries, if new_length is
        larger than len(hp[start_id:]); otherwise zero_pad on right

    Returns
    -------
    h : numpy(cupy) array
        Resized time series object.

    """

    # Do the left padding / cutting
    if start_id < 0:
        zeros = xp.zeros(int(abs(start_id)))
        h = xp.concatenate([zeros, h])
    elif start_id >= 0:
        h = h[int(start_id) :]

    # Right padding / cutting
    end_id = int(len(h) - new_length)
    if end_id < 0:
        zeros = xp.zeros(int(abs(end_id)))
        h = xp.concatenate([h, zeros])
    elif end_id > 0:
        h = h[:-end_id]

    times_new = xp.arange(0, new_length) * dt
    times_new = times_new - times_new[xp.argmax(h)]  # FIXME

    return h, times_new


def SimInspiralChirpTimeBound(fstart, m1, m2, s1z, s2z):
    """
    Adapted from `XLALSimInspiralChirpTimeBound <https://git.ligo.org/lscsoft/lalsuite/-/blob/master/lalsimulation/lib/LALSimInspiral.c#L4999>`_.

    Routine to compute an overestimate of the inspiral time from a given frequency.

    This routine estimates the time it will take for point-particle inspiral from a
    specified frequency to infinite frequency.  The estimate is intended to be an
    over-estimate, so that the true inspiral time is always smaller than the time this
    routine returns.  To obtain this estimate, the 2PN chirp time is used where all
    negative contributions are discarded.

    Parameters
    ----------
    fstart: float
        The starting frequency in Hz.
    m1: float
        The mass of the first component in kg.
    m2: float
        The mass of the second component in kg.
    s1: float
        The dimensionless spin of the first component.
    s2: float
        The dimensionless spin of the second component.

    Returns
    -------
    float
        Upper bound on chirp time of post-Newtonian inspiral in seconds

    """

    M = m1 + m2
    mu = m1 * m2 / M
    eta = mu / M
    chi = abs(s1z if abs(s1z) > abs(s2z) else s2z)

    total_mass = M * LAL_G_SI / np.power(LAL_C_SI, 3.0)
    c0 = abs(-5 * total_mass / (256.0 * eta))
    c2 = 7.43 / 2.52 + 11.0 / 3.0 * eta
    c3 = 226.0 / 15 * chi
    c4 = 30.58673 / 5.08032 + 54.29 / 5.04 * eta + 61.7 / 7.2 * eta * eta
    v = np.cbrt(np.pi * LAL_G_SI * M * fstart) / LAL_C_SI
    return c0 * np.power(v, -8) * (1 + (c2 + (c3 + c4 * v) * v) * v * v)


def SimInspiralFinalBlackHoleSpinBound(s1z, s2z):
    """ "
    Adapted from `XLALSimInspiralFinalBlackHoleSpinBound <https://git.ligo.org/lscsoft/lalsuite/-/blob/master/lalsimulation/lib/LALSimInspiral.c#L5097>`_.

    Routine to compute an overestimate of a final black hole dimensionless spin.

    This routine provides an upper bound on the dimensionless spin of a black
    hole produced in a compact binary merger.  Uses the formula in Tichy and
    Marronetti, Physical Review D 78 081501 (2008), Eq. (1) and Table 1, for
    equal mass black holes, or the larger of the two spins (which covers the
    extreme mass case).  If the result is larger than a maximum realistic
    black hole spin, truncate at this maximum value.

    See Tichy and Marronetti, Physical Review D 78 081501 (2008).
    TODO: It has been suggested that Barausse, Rezzolla (arXiv: 0904.2577) is
    more accurate.


    Parameters
    ----------
    s1z: float
        The z-component of the dimensionless spin of body 1.
    s2z: float
        The z-component of the dimensionless spin of body 2.

    Returns
    -------
    float
        Upper bound on final black hole dimensionless spin.

    """

    maximum_black_hole_spin = 0.998
    s = 0.686 + 0.15 * (s1z + s2z)
    if s < abs(s1z):
        s = abs(s1z)
    if s < abs(s2z):
        s = abs(s2z)
    if s > maximum_black_hole_spin:
        s = maximum_black_hole_spin
    return s


def SimInspiralMergeTimeBound(m1, m2):
    """
    Adapted from `XLALSimInspiralMergeTimeBound <https://git.ligo.org/lscsoft/lalsuite/-/blob/master/lalsimulation/lib/LALSimInspiral.c#L5038>`_.

    Routine to compute an overestimate of the merger time.

    This routine provides an upper bound on the time it will take for compact
    binaries to plunge and merge at the end of the quasi-stationary inspiral.
    This is quite vague since the notion of a innermost stable circular orbit
    is ill-defined except in a test mass limit. Nevertheless, this routine
    assumes (i) that the innermost stable circular orbit occurs at v = c / 3,
    or r = 9 G M / c^3 (in Boyer-Lindquist coordinates), which is roughly right
    for an extreme Kerr black hole counter-rotating with a test particle,
    and (ii) the plunge lasts for a shorter period than one cycle at this
    innermost stable circular orbit.

    Parameters
    ----------
    m1: float
        The mass of the first component in kg.
    m2: float
        The mass of the second component in kg.

    Returns
    -------
    float
        Upper bound on the merger time in seconds.

    """

    M = m1 + m2
    norbits = 1
    r = 9 * M * LAL_MRSUN_SI / LAL_MSUN_SI
    v = LAL_C_SI / 3
    return norbits * (2 * np.pi * r / v)


def SimInspiralRingdownTimeBound(M, s):
    """
    Adapted from `XLALSimInspiralRingdownTimeBound <https://git.ligo.org/lscsoft/lalsuite/-/blob/master/lalsimulation/lib/LALSimInspiral.c#L5063>`_.

    Routine to compute an overestimate of the ringdown time.

    This routine provides an upper bound on the time it will take for a
    black hole produced by compact binary merger to ring down through
    quasinormal mode radiation.  An approximate formula for the frequency
    and quality of the longest-lived fundamental (n=0) dominant (l=m=2)
    quasinormal mode * is given by Eqs. (E1) and (E2) along with Table VIII
    of Berti, Cardoso, and Will, Physical Review D (2006) 064030.
    Waveform generators produce 10 e-folds of ringdown radiation, so
    this routine goes up to 11 to provide an over-estimate of the ringdown time.

    See Emanuele Berti, Vitor Cardoso, and Clifford M. Will, Physical Review D 73, 064030 (2006) DOI: 10.1103/PhysRevD.73.064030

    Parameters
    ----------
    M: float
        The mass of the final black hole in kg.
    s: float
        The dimensionless spin of the final black hole.

    Returns
    -------
    float
        Upper bound on the merger time in seconds.

    """

    nefolds = 11
    f1 = +1.5251
    f2 = -1.1568
    f3 = +0.1292
    q1 = +0.7000
    q2 = +1.4187
    q3 = -0.4990
    omega = (f1 + f2 * np.power(1.0 - s, f3)) / (M * LAL_MTSUN_SI / LAL_MSUN_SI)
    Q = q1 + q2 * np.power(1.0 - s, q3)
    tau = 2.0 * Q / omega
    return nefolds * tau


def SimInspiralChirpStartFrequencyBound(tchirp, m1, m2):
    """
    Adapted from `XLALSimInspiralChirpStartFrequencyBound <https://git.ligo.org/lscsoft/lalsuite/-/blob/master/lalsimulation/lib/LALSimInspiral.c#L5134>`_.

    Routine to compute an underestimate of the starting frequency for a given chirp time.

    This routine estimates a start frequency for a binary inspiral from which the
    actual inspiral chirp time will be shorter than the specified chirp time.
    To obtain this estimate, only the leading order Newtonian coefficient is used.
    The frequency returned by this routine is guaranteed to be less than the frequency
    passed to XLALSimInspiralChirpTimeBound() if the returned value of that routine
    is passed to this routine as tchirp.

    Parameters
    ----------
    tchirp: float
        The chirp time of post-Newtonian inspiral s.
    m1: float
        The mass of the first component in kg.
    m2: float
        The mass of the second component in kg.

    Returns
    -------
    float
        Lower bound on the starting frequency of a post-Newtonian inspiral in Hz.
    """

    M = m1 + m2
    mu = m1 * m2 / M
    eta = mu / M
    totalmass = M * LAL_G_SI / np.power(LAL_C_SI, 3.0)
    c0 = 1.0 / (8.0 * LAL_PI * totalmass)
    return c0 * np.power(5.0 * M * (LAL_MTSUN_SI / LAL_MSUN_SI) / (eta * tchirp), 3.0 / 8.0)


def ConditioningParams(f_min=10.0, mass1=30.0, mass2=20.0, s1z=0, s2z=0):
    """
    Compute the conditioning parameters.

    The most important one is the new minimum frequency to start the waveform at.
    - original_f_min: this is the input f_min
    - f_min0: f_min if it is lower than a fisco frequency, otherwise set to fisco.
    It is used in time_array_condition_stage2.
    - f_min: the new f_min to start the waveform after adding extra cycles and time.
    - fisco: the frequency at which the innermost stable circular orbit occurs.
    - extra_time_fraction: the fraction of the total chirp time to add as extra time.
    - extra_cycles: the number of extra cycles to add.
    - tchirp: bound to chirp time.
    - s: the final spin of the black hole.
    - tmerge: bound to merger time.
    - textra: the extra time added.

    Parameters
    ----------
    f_min: float
        The lower frequency bound in Hz.
    mass1: float
        The mass of the first component in solar masses.
    mass2: float
        The mass of the second component in solar masses.
    s1z: float
        The z-component of the dimensionless spin of body 1.
    s2z: float
        The z-component of the dimensionless spin of body 2.

    Returns
    -------
    dict
        Containing the conditioning parameters.
    """

    cparams = {}

    cparams["original_f_min"] = f_min

    m1 = mass1 * LAL_MSUN_SI
    m2 = mass2 * LAL_MSUN_SI
    extra_time_fraction = 0.1
    extra_cycles = 3.0
    fisco = 1.0 / ((9**1.5) * np.pi * (mass1 + mass2) * LAL_MTSUN_SI)
    if f_min > fisco:
        f_min = fisco
    cparams["f_min0"] = f_min

    tchirp = SimInspiralChirpTimeBound(f_min, m1, m2, s1z, s2z)
    s = SimInspiralFinalBlackHoleSpinBound(s1z, s2z)
    tmerge = SimInspiralMergeTimeBound(m1, m2) + SimInspiralRingdownTimeBound(m1 + m2, s)
    textra = extra_cycles / f_min
    cparams["f_min"] = SimInspiralChirpStartFrequencyBound((1.0 + extra_time_fraction) * tchirp + tmerge + textra, m1, m2)

    cparams["fisco"] = 1.0 / (np.power(6, 3 / 2.0) * np.pi * (mass1 + mass2) * LAL_MTSUN_SI)
    cparams["extra_time_fraction"] = extra_time_fraction
    cparams["extra_cycles"] = extra_cycles
    cparams["tchirp"] = tchirp
    cparams["s"] = s
    cparams["tmerge"] = tmerge
    cparams["textra"] = textra

    return cparams


def check_pow_of_2(n):
    """
    Return the next highest power of 2 given number n.
    For example: if n = 7; exponent will be 3 (2**3=8)
    """

    nv = int(n)
    out = False
    if (nv & (nv - 1) == 0) and n != 0:
        out = True
    _, exponent = frexp(n)

    return out, exponent


def FFT(h, delta_t, delta_f=0, f_min_fd=None, real=True):
    """
    Compute the Fast Fourier Transform (FFT) of a complex or real time series.

    Parameters
    ----------
    h: 1D ndarray
        complex/real time series. It should be properly conditioned to produce sensible results.
    delta_t: float
        Time spacing of input time series.
    delta_f: float
        Frequency spacing of output frequency series.
    f_min: float
        Starting frequency of frequency series.
    real: boal
        If time series is real or complex.

    Return
    ------
    Tuple with 2 1D ndarrays
        h(f), f: Frequency series y and x values.
        For complex time series the frequencies will spand also the negative frequency range,
        while real series only return positive frequencies since h(-f)=h*(f).

    """

    # Set the propoer module np/cp for cpu/gpu
    xp = cp.get_array_module(h) if cp is not None else np

    # Set normalization value
    N = len(h)
    norm = N * delta_f

    if real:
        # Real FFT
        hf = xp.fft.rfft(h) / norm
        freqs = xp.fft.rfftfreq(N, d=delta_t)
    else:
        # Complex FFT
        hf = xp.fft.fft(h) / norm
        freqs = xp.fft.fftfreq(N, d=delta_t)

    if f_min_fd is not None:
        # Select frequencies above f_min
        mask = freqs >= f_min_fd
        hf = hf[mask]
        freqs = freqs[mask]

    return hf, freqs


def FFT_polarizations(hp, hc, delta_t, delta_f=0, f_min_fd=None):
    """
    Compute the Fast Fourier Transform (FFT) of the two (real) time domain polarizations.

    Parameters
    ----------
    hp, hc: 1D ndarrays
        Real time series for the two polarizations. The should be properly conditioned to produce sensible results.
    delta_t: float
        Time spacing of input time series.
    delta_f: float
        Frequency spacing of output frequency series.
    f_min: float
        Starting frequency of frequency series.

    Returns
    -------
    Tuple with 3 1D arrays
        hp(f), hc(f), f: Polarizations in Fourier domain and frequency array.
        Since the time series are real, the output frequencies only span the positive range, h(-f)=h*(f).

    """

    # Set the propoer module np/cp for cpu/gpu
    xp = cp.get_array_module(hp) if cp is not None else np

    # Set normalization value
    N = len(hp)
    norm = N * delta_f

    # Real FFT
    hpf = xp.fft.rfft(hp) / norm
    hcf = xp.fft.rfft(hc) / norm
    freqs = xp.fft.rfftfreq(N, d=delta_t)

    if f_min_fd is not None:
        # Select frequencies above f_min
        mask = freqs >= f_min_fd
        hpf = hpf[mask]
        hcf = hcf[mask]
        freqs = freqs[mask]

    return hpf, hcf, freqs
