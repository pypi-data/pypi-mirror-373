# Copyright (C) 2023  Cecilio García Quirós
import pickle
import numpy as np
from numba import njit

try:
    import cupy as cp
except ImportError:
    cp = None

try:
    from lalsimulation.gwsignal.core.parameter_conventions import default_dict
    import astropy.units as units
except ImportError:
    pass


# FIXME place to store constants
MTSUN_SI = 4.925490947641267e-06
PC_SI = 3.085677581491367e16
MRSUN_SI = 1476.6250380501247

import logging

logger = logging.getLogger("phenomxpy")


@njit
def qofeta(eta):
    """
    Compute mass ratio from symmetric mass ratio.
    q >= 1
    """
    return (1 + np.sqrt(1 - 4 * eta)) / (1 - np.sqrt(1 - 4 * eta))


@njit
def etaofq(q):
    """
    Compute symmetric mass ratio from mass ratio.
    """
    return q / (1 + q) ** 2


@njit
def m1ofq(q, total_mass=1):
    """
    Compute component mass1 from mass ratio and total mass.
    If q > 1 then m1 > m2.
    """
    return q / (1 + q) * total_mass


@njit
def m2ofq(q, total_mass=1):
    """
    Compute component mass2 from mass ratio and total mass.
    If q > 1 then m1 > m2.
    """
    return (1.0 / (1.0 + q)) * total_mass


@njit
def m1ofeta(eta, total_mass=1):
    """
    Compute component mass1 from symmetric mass ratio (eta) and total mass.
    Assumes m1 >= m2.
    """
    return 0.5 * (1 + np.sqrt(1 - 4.0 * eta)) * total_mass


@njit
def m2ofeta(eta, total_mass=1):
    """
    Compute component mass2 from symmetric mass ratio (eta) and total mass.
    Assumes m1 >= m2.
    """
    return 0.5 * (1 - np.sqrt(1 - 4.0 * eta)) * total_mass


@njit
def sTotR(eta, s1, s2):
    """
    sTotR spin from symmetric mass ratio and spin-z components.

    sTotR = :math:`\\frac{m_1^2 s1 + m_2^2 s2}{m_1^2 + m_2^2}`.
    """
    m1 = m1ofeta(eta)
    m2 = m2ofeta(eta)
    m1_2 = m1 * m1
    m2_2 = m2 * m2

    return (m1_2 * s1 + m2_2 * s2) / (m1_2 + m2_2)


@njit
def chi_eff(eta, s1, s2):
    """
    chi_effective spin from symmetric mass ratio and spin-z components.

    chi_effective = m1 s1 + m2 s2
    """
    m1 = m1ofeta(eta)
    m2 = m2ofeta(eta)

    return m1 * s1 + m2 * s2


@njit
def PolarToCartesian(norm, theta, phi):
    """
    Transform polar coordinates to cartesian.

    Parameters
    ----------
    norm: float
        vector norm
    theta: float
        polar angle (rad).
    phi: float
        azimuthal angle (rad).

    Returns
    -------
    (3,) ndarray
        Vector in cartesian coordinates
    """
    x = norm * np.sin(theta) * np.cos(phi)
    y = norm * np.sin(theta) * np.sin(phi)
    z = norm * np.cos(theta)
    return [x, y, z]


def SecondtoMass(seconds, total_mass):
    """
    Transform time in seconds to time in mass.

    Parameters
    ----------
    seconds: float or 1D ndarray
        time in seconds
    total_mass: float
        mass in solar masses

    Returns
    -------
    float or 1D ndarray
        time in units of mass
    """
    return seconds / (total_mass * MTSUN_SI)


def MasstoSecond(mass, total_mass=1):
    """
    Transform (NR) time in masses to seconds.

    Parameters
    ----------
    mass: float or 1D ndarray
        time in units of mass
    total_mass: float
        mass in solar masses

    Returns
    -------
    float or 1D ndarray
        time in seconds
    """
    return mass * (total_mass * MTSUN_SI)


def DistanceToSeconds(dMpc):
    """
    Transform distance in megaparsecs to seconds.

    Parameters
    ----------
    dMpc: float or 1D ndarray
        distance in megaparsecs

    Returns
    -------
    float or 1D ndarray
        distance in seconds
    """
    distance_si = dMpc * 1e6 * PC_SI
    return distance_si * MTSUN_SI / MRSUN_SI


def AmpNRtoSI(ampNR, distance, total_mass):
    """
    Transform amplitude from NR units to SI units.

    Parameters
    ----------
    ampNR: float or 1D ndarray
        amplitude value in NR units.
    distance: float
        distance in megaparsecs.
    total_mass: float
        total mass in solar masses.

    Returns
    -------
    float or 1D ndarray
        amplitude in SI units.
    """
    ampfac = MasstoSecond(total_mass) / DistanceToSeconds(distance)
    return ampNR * ampfac


def AmpSItoNR(ampSI, distance, total_mass):
    """
    Transform amplitude from SI units to NR units.

    Parameters
    ----------
    ampSI: float or 1D ndarray
        amplitude value in SI units.
    distance: float
        distance in megaparsecs.
    total_mass: float
        total mass in solar masses.

    Returns
    -------
    float or 1D ndarray
        amplitude in NR units.
    """
    ampfac = MasstoSecond(total_mass) / DistanceToSeconds(distance)
    return ampSI / ampfac


def MftoHz(Mf, total_mass):
    """
    Transform frequency in NR units to SI (Hz) units.

    Parameters
    ----------
    Mf: float or 1D ndarray
        frequency in NR units.
    total_mass: float
        total mass in solar masses.

    Returns
    -------
    float or 1D ndarray
        frequency in Hz.
    """
    return Mf / (total_mass * MTSUN_SI)


def HztoMf(Hz, total_mass):
    """
    Transform frequency in Hz to NR units.

    Parameters
    ----------
    Hz: float or 1D ndarray
        frequency in Hz.
    total_mass: float
        total mass in solar masses.

    Returns
    -------
    float or 1D ndarray
        frequency in NR units.
    """
    return Hz * total_mass * MTSUN_SI


def SpinWeightedSphericalHarmonic(theta, phi, l, m, s=-2):
    """
    Computes the :math:`{}_{-2}Y_{lm}` spin-weighted spherical harmonic.

    Implements Equations (II.9)-(II.13) of
    D. A. Brown, S. Fairhurst, B. Krishnan, R. A. Mercer, R. K. Kopparapu,
    L. Santamaria, and J. T. Whelan,
    "Data formats for numerical relativity waves",
    arXiv:0709.0093v1 (2007).
    Currently only supports s=-2, l=2,3,4,5 modes.

    Adapted from `XLALSpinWeightedSphericalHarmonic <https://git.ligo.org/lscsoft/lalsuite/-/blob/master/lal/lib/utilities/SphericalHarmonics.c#L42>`_.

    Parameters
    ----------
    theta: float
        polar angle (rad).
    phi: float
        azimuthal angle (rad).
    l, m: int
        spherical harmonic indices.
    s: int
        spin value.

    Returns
    -------
    complex value
        Ylm(theta, phi)

    """

    LAL_PI = np.pi

    if l < abs(s):
        raise ValueError("l < |s| not valid")
    if l < abs(m):
        raise ValueError("l < |m| not valid")

    if s == -2:
        if l == 2:
            if m == -2:
                fac = np.sqrt(5.0 / (64.0 * LAL_PI)) * (1.0 - np.cos(theta)) * (1.0 - np.cos(theta))
            elif m == -1:
                fac = np.sqrt(5.0 / (16.0 * LAL_PI)) * np.sin(theta) * (1.0 - np.cos(theta))
            elif m == 0:
                fac = np.sqrt(15.0 / (32.0 * LAL_PI)) * np.sin(theta) * np.sin(theta)
            elif m == 1:
                fac = np.sqrt(5.0 / (16.0 * LAL_PI)) * np.sin(theta) * (1.0 + np.cos(theta))
            elif m == 2:
                fac = np.sqrt(5.0 / (64.0 * LAL_PI)) * (1.0 + np.cos(theta)) * (1.0 + np.cos(theta))
            else:
                raise ValueError("Value of (l,m) not valid")
        elif l == 3:
            if m == -3:
                fac = np.sqrt(21.0 / (2.0 * LAL_PI)) * np.cos(theta / 2.0) * np.power(np.sin(theta / 2.0), 5.0)
            elif m == -2:
                fac = np.sqrt(7.0 / (4.0 * LAL_PI)) * (2.0 + 3.0 * np.cos(theta)) * np.power(np.sin(theta / 2.0), 4.0)
            elif m == -1:
                fac = np.sqrt(35.0 / (2.0 * LAL_PI)) * (np.sin(theta) + 4.0 * np.sin(2.0 * theta) - 3.0 * np.sin(3.0 * theta)) / 32.0
            elif m == 0:
                fac = (np.sqrt(105.0 / (2.0 * LAL_PI)) * np.cos(theta) * np.power(np.sin(theta), 2.0)) / 4.0
            elif m == 1:
                fac = -np.sqrt(35.0 / (2.0 * LAL_PI)) * (np.sin(theta) - 4.0 * np.sin(2.0 * theta) - 3.0 * np.sin(3.0 * theta)) / 32.0
            elif m == 2:
                fac = np.sqrt(7.0 / LAL_PI) * np.power(np.cos(theta / 2.0), 4.0) * (-2.0 + 3.0 * np.cos(theta)) / 2.0
            elif m == 3:
                fac = -np.sqrt(21.0 / (2.0 * LAL_PI)) * np.power(np.cos(theta / 2.0), 5.0) * np.sin(theta / 2.0)
            else:
                raise ValueError("Value of (l,m) not valid")
        elif l == 4:
            if m == -4:
                fac = 3.0 * np.sqrt(7.0 / LAL_PI) * np.power(np.cos(theta / 2.0), 2.0) * np.power(np.sin(theta / 2.0), 6.0)
            elif m == -3:
                fac = 3.0 * np.sqrt(7.0 / (2.0 * LAL_PI)) * np.cos(theta / 2.0) * (1.0 + 2.0 * np.cos(theta)) * np.power(np.sin(theta / 2.0), 5.0)
            elif m == -2:
                fac = (3.0 * (9.0 + 14.0 * np.cos(theta) + 7.0 * np.cos(2.0 * theta)) * np.power(np.sin(theta / 2.0), 4.0)) / (4.0 * np.sqrt(LAL_PI))
            elif m == -1:
                fac = (3.0 * (3.0 * np.sin(theta) + 2.0 * np.sin(2.0 * theta) + 7.0 * np.sin(3.0 * theta) - 7.0 * np.sin(4.0 * theta))) / (
                    32.0 * np.sqrt(2.0 * LAL_PI)
                )
            elif m == 0:
                fac = (3.0 * np.sqrt(5.0 / (2.0 * LAL_PI)) * (5.0 + 7.0 * np.cos(2.0 * theta)) * np.power(np.sin(theta), 2.0)) / 16.0
            elif m == 1:
                fac = (3.0 * (3.0 * np.sin(theta) - 2.0 * np.sin(2.0 * theta) + 7.0 * np.sin(3.0 * theta) + 7.0 * np.sin(4.0 * theta))) / (
                    32.0 * np.sqrt(2.0 * LAL_PI)
                )
            elif m == 2:
                fac = (3.0 * np.power(np.cos(theta / 2.0), 4.0) * (9.0 - 14.0 * np.cos(theta) + 7.0 * np.cos(2.0 * theta))) / (4.0 * np.sqrt(LAL_PI))
            elif m == 3:
                fac = -3.0 * np.sqrt(7.0 / (2.0 * LAL_PI)) * np.power(np.cos(theta / 2.0), 5.0) * (-1.0 + 2.0 * np.cos(theta)) * np.sin(theta / 2.0)
            elif m == 4:
                fac = 3.0 * np.sqrt(7.0 / LAL_PI) * np.power(np.cos(theta / 2.0), 6.0) * np.power(np.sin(theta / 2.0), 2.0)
            else:
                raise ValueError("Value of (l,m) not valid")
        elif l == 5:
            if m == -5:
                fac = np.sqrt(330.0 / LAL_PI) * np.power(np.cos(theta / 2.0), 3.0) * np.power(np.sin(theta / 2.0), 7.0)
            elif m == -4:
                fac = np.sqrt(33.0 / LAL_PI) * np.power(np.cos(theta / 2.0), 2.0) * (2.0 + 5.0 * np.cos(theta)) * np.power(np.sin(theta / 2.0), 6.0)
            elif m == -3:
                fac = (
                    np.sqrt(33.0 / (2.0 * LAL_PI))
                    * np.cos(theta / 2.0)
                    * (17.0 + 24.0 * np.cos(theta) + 15.0 * np.cos(2.0 * theta))
                    * np.power(np.sin(theta / 2.0), 5.0)
                ) / 4.0
            elif m == -2:
                fac = (
                    np.sqrt(11.0 / LAL_PI)
                    * (32.0 + 57.0 * np.cos(theta) + 36.0 * np.cos(2.0 * theta) + 15.0 * np.cos(3.0 * theta))
                    * np.power(np.sin(theta / 2.0), 4.0)
                ) / 8.0
            elif m == -1:
                fac = (
                    np.sqrt(77.0 / LAL_PI)
                    * (
                        2.0 * np.sin(theta)
                        + 8.0 * np.sin(2.0 * theta)
                        + 3.0 * np.sin(3.0 * theta)
                        + 12.0 * np.sin(4.0 * theta)
                        - 15.0 * np.sin(5.0 * theta)
                    )
                ) / 256.0
            elif m == 0:
                fac = (np.sqrt(1155.0 / (2.0 * LAL_PI)) * (5.0 * np.cos(theta) + 3.0 * np.cos(3.0 * theta)) * np.power(np.sin(theta), 2.0)) / 32.0
            elif m == 1:
                fac = (
                    np.sqrt(77.0 / LAL_PI)
                    * (
                        -2.0 * np.sin(theta)
                        + 8.0 * np.sin(2.0 * theta)
                        - 3.0 * np.sin(3.0 * theta)
                        + 12.0 * np.sin(4.0 * theta)
                        + 15.0 * np.sin(5.0 * theta)
                    )
                    / 256.0
                )
            elif m == 2:
                fac = (
                    np.sqrt(11.0 / LAL_PI)
                    * np.power(np.cos(theta / 2.0), 4.0)
                    * (-32.0 + 57.0 * np.cos(theta) - 36.0 * np.cos(2.0 * theta) + 15.0 * np.cos(3.0 * theta))
                    / 8.0
                )
            elif m == 3:
                fac = (
                    -np.sqrt(33.0 / (2.0 * LAL_PI))
                    * np.power(np.cos(theta / 2.0), 5.0)
                    * (17.0 - 24.0 * np.cos(theta) + 15.0 * np.cos(2.0 * theta))
                    * np.sin(theta / 2.0)
                    / 4.0
                )
            elif m == 4:
                fac = np.sqrt(33.0 / LAL_PI) * np.power(np.cos(theta / 2.0), 6.0) * (-2.0 + 5.0 * np.cos(theta)) * np.power(np.sin(theta / 2.0), 2.0)
            elif m == 5:
                fac = -np.sqrt(330.0 / LAL_PI) * np.power(np.cos(theta / 2.0), 7.0) * np.power(np.sin(theta / 2.0), 3.0)
            else:
                raise ValueError("Value of (l,m) not valid")
    else:
        raise ValueError("Value of s not valid")

    return fac * np.exp(1j * m * phi)


def custom_swsh(cosbeta, gamma, mode_array, lmax, xp=np):
    """
    Function to compute the spin-weighted spherical harmonics necessary to
    compute the polarizations in the inertial frame from the co-precessing
    frame modes [(2,|2|),(2,|1|),(3,|3|),(3,|2|),(4,|4|),(4,|3|),(5,|5|)].

    Parameters
    ----------
    beta: float, 1D ndarray
        Euler angle beta between the co-precessing frame and the inertial frame
    gamma: float, 1D ndarray
        Euler angle gamma between the co-precessing frame and the inertial frame
    lmax: int
        Maximum ell to use

    Returns
    -------
    dict
        Dictionary containing the Ylm (for v5 method) for each spin-weighted spherical harmonic
    """

    cBH = xp.sqrt((cosbeta + 1) * 0.5)

    cBH2 = cBH * cBH
    cBH4 = cBH2 * cBH2

    sBH2 = 1 - cBH2
    sBH = xp.sqrt(sBH2)
    sBH4 = sBH2 * sBH2

    hsB = sBH * cBH
    hsB2 = hsB * hsB

    expGamma = xp.exp(1j * gamma)
    expGamma2 = expGamma * expGamma

    swsh = xp.empty((len(mode_array), len(gamma)), dtype=complex)

    if lmax > 2:
        cB = cBH2 - sBH2
        expGamma3 = expGamma2 * expGamma

    if lmax > 3:
        expGamma4 = expGamma3 * expGamma

    if lmax > 4:
        hsB3 = hsB2 * hsB
        expGamma5 = expGamma4 * expGamma

    for idx, [l, m] in enumerate(mode_array):

        if l == 2 and m == 2:
            swsh[idx] = 0.5 * xp.sqrt(5.0 / xp.pi) * cBH4 * expGamma2
            continue
        if l == 2 and m == -2:
            swsh[idx] = 0.5 * xp.sqrt(5.0 / xp.pi) * sBH4 / expGamma2
            continue
        if l == 2 and m == 1:
            swsh[idx] = xp.sqrt(5.0 / xp.pi) * cBH2 * hsB * expGamma
            continue
        if l == 2 and m == -1:
            swsh[idx] = xp.sqrt(5.0 / xp.pi) * sBH2 * hsB / expGamma
            continue
        if l == 2 and m == 0:
            swsh[idx] = xp.sqrt(15 / (2 * np.pi)) * hsB
            continue

        if l == 3 and m == 3:
            swsh[idx] = -xp.sqrt(10.5 / xp.pi) * cBH4 * hsB * expGamma3
            continue
        if l == 3 and m == -3:
            swsh[idx] = xp.sqrt(10.5 / xp.pi) * sBH4 * hsB / expGamma3
            continue
        if l == 3 and m == 2:
            swsh[idx] = 0.25 * xp.sqrt(7.0 / xp.pi) * cBH4 * (6.0 * cB - 4.0) * expGamma2
            continue
        if l == 3 and m == -2:
            swsh[idx] = 0.25 * xp.sqrt(7.0 / xp.pi) * sBH4 * (6.0 * cB + 4.0) / expGamma2
            continue

        if l == 4 and m == 4:
            swsh[idx] = 3.0 * xp.sqrt(7.0 / xp.pi) * cBH4 * hsB2 * expGamma4
            continue
        if l == 4 and m == -4:
            swsh[idx] = 3.0 * xp.sqrt(7.0 / xp.pi) * sBH4 * hsB2 / expGamma4
            continue
        if l == 4 and m == 3:
            swsh[idx] = -0.75 * xp.sqrt(3.5 / xp.pi) * cBH4 * hsB * (8.0 * cB - 4.0) * expGamma3
            continue
        if l == 4 and m == -3:
            swsh[idx] = 0.75 * xp.sqrt(3.5 / xp.pi) * sBH4 * hsB * (8.0 * cB + 4.0) / expGamma3
            continue

        if l == 5 and m == 5:
            swsh[idx] = -xp.sqrt(330.0 / xp.pi) * cBH4 * hsB3 * expGamma5
            continue
        if l == 5 and m == -5:
            swsh[idx] = xp.sqrt(330.0 / xp.pi) * sBH4 * hsB3 / expGamma5
            continue

    return swsh


def rotate_by_polarization_angle(hp, hc, polarization_angle):
    """
    Rotate hp, hc by polarization_angle.

    Eq. 36 :cite:`nrinfrastructure`.

    hp' = hp cos(2 psi) - hc sin(2 psi)
    hc' = hp sin(2 psi) + hc cos(2 psi)

    Return
    ------
    Tuple with 2 1D ndarrays
        Rotated hp', hc'
    """

    cos2pol = np.cos(2 * polarization_angle)
    sin2pol = np.sin(2 * polarization_angle)
    hp_tmp = hp * cos2pol - hc * sin2pol
    hc_tmp = hp * sin2pol + hc * cos2pol

    return hp_tmp, hc_tmp


def ModeToString(mode):
    """
    Convert mode [l,m] to string "lm"
    """
    return str(mode[0]) + str(mode[1])


def save_pickle(obj, filename):
    """
    Save object into pickle file
    """
    with open(filename, "wb") as outp:  # Overwrites any existing file.
        pickle.dump(obj, outp, pickle.HIGHEST_PROTOCOL)


def read_pickle(filename):
    """
    Read pickle file
    """
    with open(filename, "rb") as inp:
        obj = pickle.load(inp)
    return obj


def ModeListToString(mode_array):
    """
    Transform mode_array in format [[l,m], [l2,m2], ...]
    to a string "lm l2m2 ..."
    """
    if mode_array is None:
        return "None"
    string = ""
    for mode in mode_array:
        string += ModeToString(mode) + " "
    return string


def mass_ratio_from_chirp_mass_component_mass2(chirp_mass, component_mass):
    """
    Compute mass ratio from chirp mass and component mass2.
    """
    return 1 / mass_ratio_from_chirp_mass_component_mass1(chirp_mass, component_mass)


def mass_ratio_from_chirp_mass_component_mass1(chirp_mass, component_mass):
    """
    Compute mass ratio from chirp mass and component mass1.
    """
    c = np.power(chirp_mass / component_mass, 5)
    x = 1.5 * np.sqrt(3 / c)
    if x < 1:
        mass_ratio = 3 * np.cos(np.arccos(x) / 3) / x
    else:
        mass_ratio = 3 * np.cosh(np.arccosh(x) / 3) / x
    return mass_ratio


def lookup_mass1(params):
    """
    Compute mass1 from any possible combination of 2 mass parameters inserted in the LALDict.
    If the combination does not allow to distinguish the largest object then it assumes m1 > m2.
    mass_ratio is defined as q = m2/m1 and mass_difference as m1 - m2.

    Adapted from `XLALSimInspiralWaveformParamsLookupMass1 <https://git.ligo.org/lscsoft/lalsuite/-/blob/master/lalsimulation/lib/LALSimInspiralWaveformParams.c#L470>`_

    Parameters
    ----------
    params: dict
        Waveform parameters

    Returns
    -------
    float
        Component mass1
    """

    if "mass1" in params:
        return params["mass1"]

    if "mass2" in params:
        mass2 = params["mass2"]
        if "mass_difference" in params:
            return mass2 + params["mass_difference"]
        elif "total_mass" in params:
            return params["total_mass"] - mass2
        elif "reduced_mass" in params:
            return params["reduced_mass"] * mass2 / (mass2 - params["reduced_mass"])
        if "mass_ratio" in params:
            mass_ratio = params["mass_ratio"]
        elif "sym_mass_ratio" in params:
            eta = params["sym_mass_ratio"]
            mass_ratio = qofeta(eta)
        elif "chirp_mass" in params:
            mass_ratio = mass_ratio_from_chirp_mass_component_mass2(params["chirp_mass"], mass2)
        return mass2 / mass_ratio

    elif "total_mass" in params:
        total_mass = params["total_mass"]
        if "mass_difference" in params:
            return 0.5 * (total_mass + params["mass_difference"])
        elif "reduced_mass" in params:
            reduced_mass = params["reduced_mass"]
            if total_mass < 4 * reduced_mass:
                raise ValueError("Invalid combination of total_mass and reduced_mass given")
            x = total_mass * (total_mass - 4.0 * reduced_mass)
            mass_difference = np.sqrt(x)
            return total_mass - 0.5 * (total_mass - mass_difference)
        if "mass_ratio" in params:
            mass_ratio = params["mass_ratio"]
        elif "sym_mass_ratio" in params:
            eta = params["sym_mass_ratio"]
            mass_ratio = qofeta(eta)
        elif "chirp_mass" in params:
            chirp_mass = params["chirp_mass"]
            eta = np.power(chirp_mass / total_mass, 5 / 3)
            mass_ratio = qofeta(eta)
        return total_mass / (1 + mass_ratio)

    elif "reduced_mass" in params:
        reduced_mass = params["reduced_mass"]
        if "mass_difference" in params:
            mass_difference = params["mass_difference"]
            x = 4 * reduced_mass**2 + mass_difference**2
            return reduced_mass + 0.5 * mass_difference + 0.5 * np.sqrt(x)
        if "chirp_mass" in params:
            chirp_mass = params["chirp_mass"]
            total_mass = np.sqrt(np.power(chirp_mass, 5) / np.power(reduced_mass, 3))
            x = total_mass * (total_mass - 4 * reduced_mass)
            if x >= 0:
                mass_difference = np.sqrt(x)
                return total_mass - 0.5 * (total_mass - mass_difference)
            else:
                raise ValueError("Invalid combination of reduced_mass and chirp_mass given")
        if "mass_ratio" in params:
            mass_ratio = params["mass_ratio"]
        elif "sym_mass_ratio" in params:
            eta = params["sym_mass_ratio"]
            mass_ratio = qofeta(eta)
        return (1 + mass_ratio) * reduced_mass / mass_ratio

    elif "mass_difference" in params:
        mass_difference = params["mass_difference"]
        if "mass_ratio" in params:
            mass_ratio = params["mass_ratio"]
        elif "sym_mass_ratio" in params:
            eta = params["sym_mass_ratio"]
            mass_ratio = qofeta(eta)
            if mass_difference < 0:
                mass_ratio = 1 / mass_ratio
        return mass_difference / (1 - mass_ratio)

    elif "chirp_mass" in params:
        chirp_mass = params["chirp_mass"]
        if "mass_ratio" in params:
            mass_ratio = params["mass_ratio"]
            eta = etaofq(mass_ratio)
        elif "sym_mass_ratio" in params:
            eta = params["sym_mass_ratio"]

        total_mass = chirp_mass / np.power(eta, 3 / 5)
        return total_mass / (1 + mass_ratio)


def lookup_mass2(params):
    """
    Compute mass2 from any possible combination of 2 mass parameters inserted in the LALDict.
    If the combination does not allow to distinguish the largest object then it assumes m1 > m2.
    mass_ratio is defined as q = m2/m1 and mass_difference as m1 - m2.

    Adapted from `XLALSimInspiralWaveformParamsLookupMass2 <https://git.ligo.org/lscsoft/lalsuite/-/blob/master/lalsimulation/lib/LALSimInspiralWaveformParams.c#L651>`_

    Parameters
    ----------
    params: dict
        Waveform parameters

    Returns
    -------
    float
        Component mass2
    """

    if "mass2" in params:
        return params["mass2"]

    if "mass1" in params:
        mass1 = params["mass1"]
        if "mass_difference" in params:
            return mass1 - params["mass_difference"]
        elif "total_mass" in params:
            return params["total_mass"] - mass1
        elif "reduced_mass" in params:
            return params["reduced_mass"] * mass1 / (mass1 - params["reduced_mass"])
        if "mass_ratio" in params:
            mass_ratio = params["mass_ratio"]
        elif "sym_mass_ratio" in params:
            eta = params["sym_mass_ratio"]
            mass_ratio = qofeta(eta)
        elif "chirp_mass" in params:
            mass_ratio = mass_ratio_from_chirp_mass_component_mass1(params["chirp_mass"], mass1)
        return mass1 * mass_ratio

    elif "total_mass" in params:
        total_mass = params["total_mass"]
        if "mass_difference" in params:
            return 0.5 * (total_mass - params["mass_difference"])
        elif "reduced_mass" in params:
            reduced_mass = params["reduced_mass"]
            if total_mass < 4 * reduced_mass:
                raise ValueError("Invalid combination of total_mass and reduced_mass given")
            x = total_mass * (total_mass - 4.0 * reduced_mass)
            mass_difference = np.sqrt(x)
            return 0.5 * (total_mass - mass_difference)
        if "mass_ratio" in params:
            mass_ratio = params["mass_ratio"]
        elif "sym_mass_ratio" in params:
            eta = params["sym_mass_ratio"]
            mass_ratio = qofeta(eta)
        elif "chirp_mass" in params:
            chirp_mass = params["chirp_mass"]
            eta = np.power(chirp_mass / total_mass, 5 / 3)
            mass_ratio = qofeta(eta)
        return total_mass / (1 + mass_ratio) * mass_ratio

    elif "reduced_mass" in params:
        reduced_mass = params["reduced_mass"]
        if "mass_difference" in params:
            mass_difference = params["mass_difference"]
            x = 4 * reduced_mass**2 + mass_difference**2
            return reduced_mass + 0.5 * mass_difference + 0.5 * np.sqrt(x) - mass_difference
        if "chirp_mass" in params:
            chirp_mass = params["chirp_mass"]
            total_mass = np.sqrt(np.power(chirp_mass, 5) / np.power(reduced_mass, 3))
            x = total_mass * (total_mass - 4 * reduced_mass)
            if x >= 0:
                mass_difference = np.sqrt(x)
                return 0.5 * (total_mass - mass_difference)
            else:
                raise ValueError("Invalid combination of reduced_mass and chirp_mass given")
        if "mass_ratio" in params:
            mass_ratio = params["mass_ratio"]
        elif "sym_mass_ratio" in params:
            eta = params["sym_mass_ratio"]
            mass_ratio = qofeta(eta)
        return (1 + mass_ratio) * reduced_mass

    elif "mass_difference" in params:
        mass_difference = params["mass_difference"]
        if "mass_ratio" in params:
            mass_ratio = params["mass_ratio"]
        elif "sym_mass_ratio" in params:
            eta = params["sym_mass_ratio"]
            mass_ratio = qofeta(eta)
            if mass_difference < 0:
                mass_ratio = 1 / mass_ratio
        return mass_ratio * mass_difference / (1 - mass_ratio)

    elif "chirp_mass" in params:
        chirp_mass = params["chirp_mass"]
        if "mass_ratio" in params:
            mass_ratio = params["mass_ratio"]
            eta = etaofq(mass_ratio)
        elif "sym_mass_ratio" in params:
            eta = params["sym_mass_ratio"]

        total_mass = chirp_mass / np.power(eta, 3 / 5)
        return total_mass / (1 + mass_ratio) * mass_ratio


def convert_params(params):
    """
    Transform input dictionary to (eta, total_mass) and spins in cartesian coordintaes.
    """

    converted_params = params.copy()

    # Get component masses from any combination of mass arguments
    mass1 = lookup_mass1(params)
    mass2 = lookup_mass2(params)

    # Compute symmetric_mass_ratio and total_mass
    converted_params["eta"] = etaofq(mass1 / mass2)
    converted_params["total_mass"] = mass1 + mass2

    # Transform spins to cartesian coordinates if needed. The format will be s1,2=[3 components]
    for idx in ["1", "2"]:
        spin_key = "s{}".format(idx)
        if spin_key not in params:
            list1 = [f"spin{idx}x", f"spin{idx}y", f"spin{idx}z"]
            list2 = [f"spin{idx}_norm", f"spin{idx}_tilt", f"spin{idx}_phi"]
            list3 = ["spin2_norm", "spin2_tilt", "phi12", "spin1_phi"]
            if all(key in params for key in list1):
                converted_params[spin_key] = [params[list1[0]], params[list1[1]], params[list1[2]]]
                [converted_params.pop(key) for key in list1]
            elif all(key in params for key in list2):
                converted_params[spin_key] = PolarToCartesian(params[list2[0]], params[list2[1]], params[list2[2]])
                [converted_params.pop(key) for key in list2]
            elif idx == "2" and all(key in params for key in list3):
                norm, tilt, phi12, phi1 = params[list3[0]], params[list3[1]], params[list3[2]], params[list3[3]]
                converted_params[spin_key] = [
                    norm * np.sin(tilt) * np.cos(phi1 + phi12),
                    norm * np.sin(tilt) * np.sin(phi1 + phi12),
                    norm * np.cos(tilt),
                ]
                [converted_params.pop(key) for key in list3[:3]]
            elif f"spin{idx}z" in params:
                converted_params[f"s{idx}"] = [0, 0, params[f"spin{idx}z"]]
                converted_params.pop(f"spin{idx}z")
            else:
                raise RuntimeError(f"Cannot determine s{idx}")

    if mass1 < mass2:
        tmp = converted_params["s1"]
        converted_params["s1"] = converted_params["s2"]
        converted_params["s2"] = tmp

    # If delta_t_sec not provided, assume f_max is the Nyquist frequency
    if "delta_t" not in params:  # FIXME already handled in pWF
        if "f_max" in params:
            converted_params["delta_t"] = 0.5 / params["f_max"]
        else:
            raise SyntaxError("Need to specify either delta_t or f_max")

    return converted_params


def strip_units(waveform_dict):
    """
    Remove units from astropy dictionary.
    """

    new_dc = {}
    for key in waveform_dict.keys():
        new_dc[key] = waveform_dict[key].value if isinstance(waveform_dict[key], units.Quantity) else waveform_dict[key]

    return new_dc


def convert_params_from_gwsignal(input_params):
    """
    Convert gwsignal (astropy dictionary) to phenomxpy.

    Parameters are transformed to the units in the default_dict of gwsignal.

    Units are removed.

    Parameters
    ----------
    input_params: gwsiganl dictionary
        parameters with astropy units.

    Returns
    -------
    dict
        Parameters in phenomxpy format without units.
    """

    # Deep copy to not modify the original dictionary
    params = input_params.copy()

    # Conversion to units used in phenomxpy. It uses the same units as defined in gwsignal.core.parameter_conventions.default_dict
    for key in params:
        if key in default_dict:
            params[key] = params[key].to(default_dict[key].unit)

    # Renaming some keys
    for old_key, new_key in {"f22_start": "f_min", "f22_ref": "f_ref", "deltaT": "delta_t", "deltaF": "delta_f"}.items():
        if old_key in params:
            params[new_key] = params.pop(old_key)

    return convert_params(strip_units(params))


def parse_options_from_approximant_name(params_dict):
    """
    Update input dictionary with extra options taken from the approximant name.

    Some options can be indicated in the approximant name, e.g. IMRPhenomTPHM_NNLO_FS2 will
    add ``prec_version`` = 'nnlo' and ``final_spin_version`` = 2 to the input dictionary.

    Parameters
    ----------
    params_dict: dictionary, it includes the approximant name with extra options

    Returns
    -------
    string
        Clean approximant name, e.g. IMRPhenomTPHM.
    """

    approximant = params_dict["approximant"].split("_")

    if len(approximant) > 1:
        for option in approximant[1:]:
            if option.lower() in ["nnlo", "msa", "numerical", "num", "st", "spintaylor"]:
                params_dict["prec_version"] = option.lower()
            elif "fs" in option.lower():
                params_dict["final_spin_version"] = int(option[2:])
            else:
                raise KeyError(f"Option {option} not supported in approximant name")

    # Return approximant name without options
    return approximant[0]


def move_to_front(array, target):
    """
    Find element in an array and put it at the beginning of the array.

    Parameters
    ----------
    array: list
        input array to modify
    target: same as array
        Element to move

    Returns
    -------
    list
        Array with target in the first position.
    """

    if target in array:
        array.remove(target)
        array.insert(0, target)
    return array


def remove_duplicates(lst):
    """
    Remove duplicates from a list with format [[l,m], [,], ...]
    """
    seen = set()
    result = []
    for item in lst:
        t = tuple(item)  # convert to tuple so it's hashable
        if t not in seen:
            seen.add(t)
            result.append(item)
    return result


def replace_instances_with_value(array, mask, value, xp):
    """
    Replace instances in an array with a given value.

    Basically it does `array[mask]`, but this is very slow for cupy arrays,
    so for that case we use cp.where.

    Parameters
    ----------
    array: ndarray
        array to modify.
    mask: array of booleans
        Array where the instances happen.
    value: value or array to replace the instances with.
    xp: np/cp
        module for the cpu/gpu

    Returns
    -------
    array
        With instances replaced.
    """
    if mask.any():
        if xp == np:
            array[mask] = value
        else:
            array = xp.where(mask, value, array)
    return array


def check_equal_blackholes(pWF):
    """
    Check if the black holes are equal by checking if eta is 0.25 and s1z == s2z.

    Parameters
    ----------
    pWF: pWFHM
        pWFHM object with the parameters of the waveform.

    Returns
    -------
    bool
        ``True`` if black holes are equal, ``False`` otherwise
    """

    if pWF.eta == 0.25 and pWF.s1z == pWF.s2z:
        return True
    return False


def extra_options_from_string(approximant):
    """
    Parse extra options from approximant name. E.g. IMRPhenomTPHM_NNLO_FS2.

    Parameters
    ----------
    approximant: str
        Approximant name with extra options separated by underscores. E.g. IMRPhenomTPHM_NNLO_FS2.

    Returns
    -------
    Tuple with string and dict
        clean approximant name, dictionary with extra options
    """

    # Options are separated by underscore (except maybe a Py in front, e.g. PyIMRPhenomTPHM)
    split = approximant.split("_")

    # Clean approximant name (the Py in front PyIMRPhenomTPHM is removed later if needes)
    wf_approximant = split[0]

    parser = {
        # Options for the lal dictionary
        "AD": {"PhenomTAnalyticalDerivative": 1},
        "BPI": {"BugPI": 1},
        "BW5": {"BugWigner5": 1},
        "NRDT": {"NewRDtimes": 1},
        "BPN": {"BugPNAmp": 1},
        "NTA": {"NewTimeArray": 1},
        "RA": {"RefAngles": 1},
        "BGI": {"BugGammaIntegration": 1},
        "NT": {"NumericalTimes": 1},
        # Options for phenomxpy pacakge
        "CTR": {"use_closest_time_to_tref": True},
        "RL": {"recover_lal": True},
        "TL": {"timeslal": True},
        "EP": {"use_exact_epoch": True},
        "Jmodes": {"polarizations_from": "Jmodes"},
        "L0modes": {"polarizations_from": "L0modes"},
        "fast": {"numba_spline_for": "ode_solution", "use_frame_to_quaternions": True, "numba_derivatives": True},
        "fastv2": {"numba_spline_for": "ode_solution", "use_frame_to_quaternions": True, "numba_derivatives": True, "v_function": "full_omega"},
        "slow": {"numba_derivatives": False},
        # Options for interface
        "CI": {"interface": "c"},
        "GWS": {"interface": "gwsignal"},
    }

    # By default use lalsuite approximant and gwsignal interface. The interface can be specified by adding CI, GWS or Py(without GWS) to the approximant name
    #   - Nothing: call lalsuite approximant through gwsginal  IMRPhenomTPHM
    #   - CI: call lalsuite approximant through C interface    IMRPhenomTPHM_CI
    #   - Py: call phenomxpy directly                          PyIMRPhenomTPHM, IMRPhenomTPHM_python... (contains "py")
    #   - Py + GWS: call phenomxpy through gwsignal            PyIMRPhenomTPHM_gws, IMRPhenomTPHM_py_gws

    extra_options = {"lalsuite": True, "interface": "gwsignal"}
    if "py" in wf_approximant.lower():
        # extra_options["interface"] = "phenomxpy" By default use gwsignal
        extra_options["lalsuite"] = False

    # Remove remaining python option if needed.
    wf_approximant = wf_approximant.replace("py", "").replace("Py", "")

    # Loop over the extra options and add them to the dictionary
    if len(split) > 1:
        for option in split[1:]:
            if option.lower() in ["nnlo", "msa", "numerical", "num", "st", "spintaylor"]:
                extra_options["prec_version"] = option.lower()
            elif "fs" in option.lower():
                extra_options["final_spin_version"] = int(option[2:])
            elif option.upper() in parser:
                extra_options.update(parser[option.upper()])
            elif option in parser:
                extra_options.update(parser[option])
            elif "lal" in option.lower():
                extra_options["lalsuite"] = True
            elif "py" in option.lower():
                extra_options["lalsuite"] = False
            else:
                raise KeyError(f"Option {option} not supported in approximant name")

    # Return clean approximant name and dictionary with the extra options
    return wf_approximant, extra_options


def ToComponentMassesCartesianSpins(params, use_spin_vectors=True):
    new_params = params.copy()

    new_params["mass1"] = lookup_mass1(params)
    new_params["mass2"] = lookup_mass2(params)
    for key in ["total_mass", "mass_ratio", "chirp_mass", "mass_difference", "symetric_mass_ratio"]:
        if key in new_params:
            new_params.pop(key)

    if "s1z" in params and use_spin_vectors:
        del new_params["s1z"]
        new_params["s1"] = [0, 0, params["s1z"]]
    if "s2z" in params and use_spin_vectors:
        del new_params["s2z"]
        new_params["s2"] = [0, 0, params["s2z"]]

    if all(x in params for x in ["spin1_norm", "spin1_tilt", "spin1_phi"]):
        s1 = PolarToCartesian(params["spin1_norm"], params["spin1_tilt"], params["spin1_phi"])

        if use_spin_vectors is True:
            new_params["s1"] = s1
        else:
            new_params["spin1x"], new_params["spin1y"], new_params["spin1z"] = s1
        for key in ["spin1_norm", "spin1_tilt", "spin1_phi"]:
            del new_params[key]

    if all(x in params for x in ["spin2_norm", "spin2_tilt", "spin2_phi"]):
        s2 = PolarToCartesian(params["spin2_norm"], params["spin2_tilt"], params["spin2_phi"])

        if use_spin_vectors is True:
            new_params["s2"] = s2
        else:
            new_params["spin2x"], new_params["spin2y"], new_params["spin2z"] = s2
        for key in ["spin2_norm", "spin2_tilt", "spin2_phi"]:
            del new_params[key]

    return new_params
