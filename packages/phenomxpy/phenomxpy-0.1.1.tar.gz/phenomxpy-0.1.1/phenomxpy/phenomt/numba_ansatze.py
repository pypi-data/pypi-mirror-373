# Copyright (C) 2023  Cecilio García Quirós
"""
Rewrite amplitude, phase ansatze to use numba

There are functions for evaluation in one single point and
in a time array, which is parallelize with prange.

Unfortunately this requires some code duplication respect to
the ansatze defined in internals.py.
"""

import numpy as np
from numba import njit, prange

LAL_PI = np.pi


# Build waveform A * exp(-i phase)
@njit(parallel=True)
def combine_amp_phase(amp, phase):
    out = np.empty(len(amp), np.cdouble)
    for idx in prange(len(amp)):
        out[idx] = amp[idx] * np.exp(-1j * phase[idx])
    return out


#########################################
#          AMPLITUDE ANSATZE
#########################################


@njit
def numba_inspiral_ansatz_amplitude(x, fac0, pn_real_coeffs, pn_imag_coeffs, pseudo_pn_coeffs):
    xhalf = np.sqrt(x)
    x1half = x * xhalf
    x2 = x * x
    x2half = x2 * xhalf
    x3 = x2 * x
    x3half = x3 * xhalf
    x4 = x2 * x2
    x4half = x4 * xhalf
    x5 = x3 * x2

    ampreal = (
        pn_real_coeffs[0]
        + pn_real_coeffs[1] * xhalf
        + pn_real_coeffs[2] * x
        + pn_real_coeffs[3] * x1half
        + pn_real_coeffs[4] * x2
        + pn_real_coeffs[5] * x2half
        + pn_real_coeffs[6] * x3
        + pn_real_coeffs[7] * x3half
        + pn_real_coeffs[8] * np.log(16 * x) * x3
    )
    ampimag = (
        pn_imag_coeffs[0] * xhalf
        + pn_imag_coeffs[1] * x
        + pn_imag_coeffs[2] * x1half
        + pn_imag_coeffs[3] * x2
        + pn_imag_coeffs[4] * x2half
        + pn_imag_coeffs[5] * x3
        + pn_imag_coeffs[6] * x3half
    )
    ampreal += pseudo_pn_coeffs[0] * x4 + pseudo_pn_coeffs[1] * x4half + pseudo_pn_coeffs[2] * x5

    return fac0 * x * (ampreal + 1j * ampimag)


@njit(parallel=True)
def numba_inspiral_ansatz_amplitude_array(x, fac0, pn_real_coeffs, pn_imag_coeffs, pseudo_pn_coeffs):
    out = np.zeros(len(x), np.cdouble)
    for idx in prange(len(x)):
        out[idx] = numba_inspiral_ansatz_amplitude(x[idx], fac0, pn_real_coeffs, pn_imag_coeffs, pseudo_pn_coeffs)
    return out


@njit
def numba_intermediate_ansatz_amplitude(time, alpha1RD, mergerC1, mergerC2, mergerC3, mergerC4, tshift):
    sech1 = 1 / np.cosh(alpha1RD * (time - tshift))
    sech2 = 1 / np.cosh(2 * alpha1RD * (time - tshift))

    return mergerC1 + mergerC2 * sech1 + mergerC3 * np.power(sech2, 1 / 7) + mergerC4 * (time - tshift) * (time - tshift)


@njit(parallel=True)
def numba_intermediate_ansatz_amplitude_array(times, alpha1RD, mergerC1, mergerC2, mergerC3, mergerC4, tshift):
    out = np.zeros(len(times))
    for idx in prange(len(times)):
        out[idx] = numba_intermediate_ansatz_amplitude(times[idx], alpha1RD, mergerC1, mergerC2, mergerC3, mergerC4, tshift)
    return out


@njit
def numba_ringdown_ansatz_amplitude(time, c1_prec, c2_prec, c3, c4_prec, alpha1RD_prec, tshift):
    tanh = np.tanh(c2_prec * (time - tshift) + c3)
    expAlpha = np.exp(-alpha1RD_prec * (time - tshift))

    return expAlpha * (c1_prec * tanh + c4_prec)


@njit(parallel=True)
def numba_ringdown_ansatz_amplitude_array(times, c1_prec, c2_prec, c3, c4_prec, alpha1RD_prec, tshift):
    out = np.empty(len(times))
    for idx in prange(len(times)):
        out[idx] = numba_ringdown_ansatz_amplitude(times[idx], c1_prec, c2_prec, c3, c4_prec, alpha1RD_prec, tshift)
    return out


#########################################
#           OMEGA ANSATZE
#########################################


@njit
def numba_pn_ansatz_omega(theta, coefficients):
    theta2 = theta * theta
    theta3 = theta2 * theta
    theta4 = theta2 * theta2
    theta5 = theta3 * theta2
    theta6 = theta3 * theta3
    theta7 = theta4 * theta3
    logterm = 107 * np.log(theta) / 280
    fac = theta3 / 4

    return fac * (
        1
        + coefficients[0] * theta2
        + coefficients[1] * theta3
        + coefficients[2] * theta4
        + coefficients[3] * theta5
        + coefficients[4] * theta6
        + logterm * theta6
        + coefficients[5] * theta7
    )


@njit(parallel=True)
def numba_pn_ansatz_omega_array(theta, coefficients):
    out = np.empty(len(theta))
    for idx in prange(len(theta)):
        out[idx] = numba_pn_ansatz_omega(theta[idx], coefficients)

    return out


@njit
def numba_inspiral_ansatz_omega(time, eta, pn_coefficients, coefficients):

    theta = np.power(-eta * time / 5, -1 / 8)

    # taylort3 = numba_pn_ansatz_omega(theta, pn_coefficients)

    theta2 = theta * theta
    theta3 = theta * theta2
    theta4 = theta * theta3
    theta5 = theta * theta4
    theta6 = theta * theta5
    theta7 = theta * theta6
    theta8 = theta4 * theta4
    theta9 = theta8 * theta
    theta10 = theta9 * theta
    theta11 = theta10 * theta
    theta12 = theta11 * theta
    theta13 = theta12 * theta
    logterm = 107 * np.log(theta) / 280

    fac = theta3 / 4

    taylort3 = (
        1
        + pn_coefficients[0] * theta2
        + pn_coefficients[1] * theta3
        + pn_coefficients[2] * theta4
        + pn_coefficients[3] * theta5
        + pn_coefficients[4] * theta6
        + logterm * theta6
        + pn_coefficients[5] * theta7
    )

    out = (
        coefficients[0] * theta8
        + coefficients[1] * theta9
        + coefficients[2] * theta10
        + coefficients[3] * theta11
        + coefficients[4] * theta12
        + coefficients[5] * theta13
    )
    omega = fac * (taylort3 + out)

    # omega = fac * out + taylort3

    return omega


@njit(parallel=True)
def numba_inspiral_ansatz_omega_array(times, eta, pn_coefficients, pseudo_coefficients):
    out = np.empty(len(times))
    for idx in prange(len(times)):
        out[idx] = numba_inspiral_ansatz_omega(times[idx], eta, pn_coefficients, pseudo_coefficients)
    return out


@njit
def numba_inspiral_ansatz_domega(time, eta, pn_coefficients, coefficients):

    theta = np.power(-eta * time / 5, -1.0 / 8)

    theta2 = theta * theta
    theta3 = theta * theta2
    theta4 = theta * theta3
    theta5 = theta * theta4
    theta6 = theta * theta5
    theta7 = theta * theta6
    theta8 = theta4 * theta4
    theta9 = theta8 * theta
    theta10 = theta9 * theta
    theta11 = theta10 * theta
    theta12 = theta11 * theta
    theta13 = theta12 * theta
    logterm = np.log(theta)

    der_omega = (
        0.25
        * theta2
        * (
            3
            + 5 * pn_coefficients[0] * theta2
            + 6 * pn_coefficients[1] * theta3
            + 7 * pn_coefficients[2] * theta4
            + 8 * pn_coefficients[3] * theta5
            + 107.0 / 280 * theta6
            + 9 * pn_coefficients[4] * theta6
            + 10 * pn_coefficients[5] * theta7
            + 11 * coefficients[0] * theta8
            + 12 * coefficients[1] * theta9
            + 13 * coefficients[2] * theta10
            + 14 * coefficients[3] * theta11
            + 15 * coefficients[4] * theta12
            + 16 * coefficients[5] * theta13
        )
        + 963 * theta8 * logterm / 1120
    )

    der_theta = 0.125 * np.power(5 / eta, 1.0 / 8) * np.power(-time, -9.0 / 8)

    return der_theta * der_omega


@njit
def numba_intermediate_ansatz_omega(times, alpha1RD, omegaPeak, omegaRING, domegaPeak, omegaMergerC1, omegaMergerC2, omegaMergerC3):
    x = np.arcsinh(alpha1RD * times)
    w = 1 - omegaPeak / omegaRING + x * (domegaPeak / alpha1RD + x * (omegaMergerC1 + x * (omegaMergerC2 + x * omegaMergerC3)))
    return omegaRING * (1 - w)


@njit
def numba_intermediate_ansatz_omega_array(times, alpha1RD, omegaPeak, omegaRING, domegaPeak, omegaMergerC1, omegaMergerC2, omegaMergerC3):
    out = np.zeros(len(times))
    for idx in prange(len(times)):
        out[idx] = numba_intermediate_ansatz_omega(
            times[idx], alpha1RD, omegaPeak, omegaRING, domegaPeak, omegaMergerC1, omegaMergerC2, omegaMergerC3
        )
    return out


@njit
def numba_ringdown_ansatz_omega(times, c1, c2, c3, c4, omegaRING):
    expC = np.exp(-c2 * times)
    expC2 = expC * expC

    num = -c1 * c2 * (2 * c4 * expC2 + c3 * expC)
    den = 1 + c4 * expC2 + c3 * expC

    return num / den + omegaRING


@njit
def numba_ringdown_ansatz_omega_array(times, c1, c2, c3, c4, omegaRING):
    out = np.zeros(len(times))
    for idx in prange(len(times)):
        out[idx] = numba_ringdown_ansatz_omega(times[idx], c1, c2, c3, c4, omegaRING)
    return out


#########################################
#           PHASE ANSATZE
#########################################


@njit
def numba_pn_ansatz_22_phase(thetabar, eta, powers_of_5, pn_coefficients):
    thetabar = thetabar * powers_of_5[1]
    thetabar2 = thetabar * thetabar
    thetabar3 = thetabar * thetabar2
    thetabar4 = thetabar * thetabar3
    thetabar5 = thetabar * thetabar4
    thetabar6 = thetabar * thetabar5
    thetabar7 = thetabar * thetabar6
    logthetabar = np.log(thetabar)

    aux = (
        1
        / eta
        / thetabar5
        * (
            -168
            - 280 * pn_coefficients[0] * thetabar2
            - 420 * pn_coefficients[1] * thetabar3
            - 840 * pn_coefficients[2] * thetabar4
            + 840 * pn_coefficients[3] * (logthetabar - 0.125 * np.log(5)) * thetabar5
            - 321 * thetabar6
            + 840 * pn_coefficients[4] * thetabar6
            + 321 * logthetabar * thetabar6
            + 420 * pn_coefficients[5] * thetabar7
        )
    ) / 84.0

    return aux


@njit
def numba_inspiral_22_phase(time, eta, powers_of_5, pn_coefficients, pseudo_pn_coefficients, phOffInsp):
    thetabar = np.power(-eta * time, -1.0 / 8)
    thetabar2 = thetabar * thetabar
    thetabar3 = thetabar * thetabar2
    thetabar4 = thetabar * thetabar3
    thetabar5 = thetabar * thetabar4
    thetabar6 = thetabar * thetabar5
    thetabar7 = thetabar * thetabar6
    logmtime = np.log(-time)
    log_theta_bar = np.log(np.power(5, 0.125)) - 0.125 * (np.log(eta) + logmtime)

    aux = (
        -(
            1
            / powers_of_5[5]
            / (eta * eta)
            / time
            / thetabar7
            * (
                3 * (-107 + 280 * pn_coefficients[4]) * powers_of_5[6]
                + 321 * log_theta_bar * powers_of_5[6]
                + 420 * pn_coefficients[5] * thetabar * powers_of_5[7]
                + 56 * (25 * pseudo_pn_coefficients[0] + 3 * eta * time) * thetabar2
                + 1050 * pseudo_pn_coefficients[1] * powers_of_5[1] * thetabar3
                + 280 * (3 * pseudo_pn_coefficients[2] + eta * pn_coefficients[0] * time) * powers_of_5[2] * thetabar4
                + 140 * (5 * pseudo_pn_coefficients[3] + 3 * eta * pn_coefficients[1] * time) * powers_of_5[3] * thetabar5
                + 120 * (5 * pseudo_pn_coefficients[4] + 7 * eta * pn_coefficients[2] * time) * powers_of_5[4] * thetabar6
                + 525 * pseudo_pn_coefficients[5] * powers_of_5[5] * thetabar7
                + 105 * eta * pn_coefficients[3] * time * logmtime * powers_of_5[5] * thetabar7
            )
        )
        / 84.0
    )

    aux = aux + phOffInsp

    return aux


@njit(parallel=True)
def njit_inspiral_22_phase(times, eta, powers_of_5, pn_coefficients, pseudo_pn_coefficients, phOffInsp):
    out = np.zeros(len(times))
    for idx in prange(len(times)):
        out[idx] = numba_inspiral_22_phase(times[idx], eta, powers_of_5, pn_coefficients, pseudo_pn_coefficients, phOffInsp)
    return out


@njit
def numba_intermediate_ansatz_phase(time, alpha1RD, omegaMergerC1, omegaMergerC2, omegaMergerC3, omegaPeak, domegaPeak, omegaRING, phOffMerger):

    x = np.arcsinh(alpha1RD * time)
    x2 = x * x
    x3 = x * x2
    x4 = x * x3
    term1 = np.sqrt(1 + (alpha1RD * alpha1RD) * time * time)

    aux = omegaRING * time * (
        1
        - (
            2 * omegaMergerC1
            + 24 * omegaMergerC3
            + (6 * omegaMergerC2 + domegaPeak / alpha1RD) * x
            + (1 - omegaPeak / omegaRING)
            + (omegaMergerC1 + 12 * omegaMergerC3) * x2
            + omegaMergerC2 * x3
            + omegaMergerC3 * x4
        )
    ) - (omegaRING / alpha1RD) * term1 * (
        -domegaPeak / alpha1RD - 6 * omegaMergerC2 - x * (2 * omegaMergerC1 + 24 * omegaMergerC3) - 3 * omegaMergerC2 * x2 - 4 * omegaMergerC3 * x3
    )

    return aux + phOffMerger


@njit(parallel=True)
def numba_intermediate_ansatz_phase_array(
    times, alpha1RD, omegaMergerC1, omegaMergerC2, omegaMergerC3, omegaPeak, domegaPeak, omegaRING, phOffMerger
):
    out = np.empty(len(times))
    for idx in prange(len(times)):
        out[idx] = numba_intermediate_ansatz_phase(
            times[idx], alpha1RD, omegaMergerC1, omegaMergerC2, omegaMergerC3, omegaPeak, domegaPeak, omegaRING, phOffMerger
        )
    return out


@njit
def numba_ringdown_ansatz_phase(time, c1_prec, c2, c3, c4, omegaRING_prec, phOffRD):
    expC = np.exp(-c2 * time)
    num = 1 + c3 * expC + c4 * expC * expC
    den = 1 + c3 + c4
    aux = np.log(num / den)

    return c1_prec * aux + omegaRING_prec * time + phOffRD


@njit(parallel=True)
def numba_ringdown_ansatz_phase_array(times, c1_prec, c2, c3, c4, omegaRING_prec, phOffRD):
    out = np.empty(len(times))
    for idx in prange(len(times)):
        out[idx] = numba_ringdown_ansatz_phase(times[idx], c1_prec, c2, c3, c4, omegaRING_prec, phOffRD)
    return out


@njit
def numba_ringdown_ansatz_domega(time, c1, c2, c3, c4):
    expC = np.exp(c2 * time)
    expC2 = expC * expC

    num = c1 * c2 * c2 * expC * (4 * c4 * expC + c3 * (c4 + expC2))
    den = c4 + expC * (c3 + expC)

    return num / (den * den)
