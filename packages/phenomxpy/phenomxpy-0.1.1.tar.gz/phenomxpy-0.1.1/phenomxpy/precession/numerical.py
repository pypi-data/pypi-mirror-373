# Copyright (C) 2023  Cecilio García Quirós
"""
Spin-Taylor numerical Euler angles.
"""

import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import CubicSpline

from phenomxpy.phenomt.fits import IMRPhenomX_FinalSpin2017

try:
    import cupy as cp
except ImportError:
    cp = None

from numba import njit

LAL_PI = np.pi
LAL_GAMMA = np.euler_gamma


# Functions for setting up SpinTaylor T4
# Adapted from https://git.ligo.org/lscsoft/lalsuite/-/blob/master/lalsimulation/lib/LALSimInspiralPNCoefficients.c
def pn_energy_7pn_so(mByM):
    return (
        -75.0 / 4.0
        + 27.0 / (4.0 * mByM)
        + 53.0 * mByM / 2.0
        + 67 * mByM * mByM / 6.0
        + 17.0 * mByM * mByM * mByM / 12.0
        - mByM * mByM * mByM * mByM / 12.0
    )


def pn_energy_5pn_so(mByM):
    return 5.0 / 3.0 + 3.0 / mByM + 29.0 * mByM / 9.0 + mByM * mByM / 9.0


def pn_energy_4pn_s1s2(eta):
    return 1.0 / eta


def pn_energy_4pn_s1os2o(eta):
    return -3.0 / eta


def pn_energy_4PN_qm_s1s1(mByM):
    return 0.5 / mByM / mByM


def pn_energy_4PN_qm_s1os1o(mByM):
    return -1.5 / mByM / mByM


def pn_energy_3pn_so(mByM):
    return 2.0 / 3.0 + 2.0 / mByM


def spin_dot_7pn(mByM):
    return (
        mByM * mByM * mByM * mByM * mByM * mByM / 48.0
        - 3.0 / 8.0 * mByM * mByM * mByM * mByM * mByM
        - 3.9 / 1.6 * mByM * mByM * mByM * mByM
        - 23.0 / 6.0 * mByM * mByM * mByM
        + 18.1 / 1.6 * mByM * mByM
        - 51.0 / 8.0 * mByM
        + 2.7 / 1.6
    )


def spin_dot_5pn(mByM):
    return 9.0 / 8.0 - mByM / 2.0 + 7.0 * mByM * mByM / 12.0 - 7.0 * mByM * mByM * mByM / 6.0 - mByM * mByM * mByM * mByM / 24.0


def spin_dot_4pn_s2():
    return 0.5


def spin_dot_4pn_s2o():
    return -1.5


def spin_dot_4pn_qm_so(mByM):
    return 1.5 * (1.0 - 1.0 / mByM)


def spin_dot_3pn(mByM):
    return 3.0 / 2.0 - mByM - mByM * mByM / 2.0


# First suggested by J. Valencia to speedup spin derivatives.
@njit(inline="always")
def manual_cross(a, b):
    """
    Cross product of two 3D vectors.
    """
    return np.array([a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]])


class SpinTaylor:
    """
    Class to setup SpinTaylorT4 quantities and compute spin derivatives.
    """

    def __init__(self, eta, m1M, m2M):
        self.eta = eta
        self.m1M = m1M
        self.m2M = m2M
        self.spin0 = -1
        self.phase0 = -1
        self.energy_spin_derivative_setup()

    def energy_spin_derivative_setup(self, quadparam1=0, quadparam2=0):
        """
        Setup energy and spin derivative coefficients.

        Adapted from `XLALSimSpinTaylorEnergySpinDerivativeSetup <https://git.ligo.org/lscsoft/lalsuite/-/blob/master/lalsimulation/lib/LALSimInspiralSpinTaylor.c#L253>`_.
        """

        eta = self.eta
        m1M = self.m1M
        m2M = self.m2M

        self.Ecoeff = np.zeros(8)
        self.Ecoeff[7] = 0
        self.Ecoeff[6] = -(67.5 / 6.4 - (344.45 / 5.76 - 20.5 / 9.6 * LAL_PI * LAL_PI) * eta + 15.5 / 9.6 * eta * eta + 3.5 / 518.4 * eta * eta * eta)
        self.Ecoeff[5] = 0
        self.Ecoeff[4] = -(27.0 / 8.0 - 19.0 / 8.0 * eta + 1.0 / 24.0 * eta * eta)
        self.Ecoeff[3] = 0
        self.Ecoeff[2] = -(0.75 + eta / 12.0)
        self.Ecoeff[1] = 0
        self.Ecoeff[0] = 1

        # 3PN order
        # Energy coefficients
        self.E7S1O = pn_energy_7pn_so(m1M)  # Coefficient of S1.LN
        self.E7S2O = pn_energy_7pn_so(m2M)  # Coefficient of S2.LN
        # Sdot coefficients
        self.S1dot7S2 = spin_dot_7pn(m1M)  # Coefficient of S2 x S1
        self.S2dot7S1 = spin_dot_7pn(m2M)  # Coefficient of S1 x S2

        # 2.5PN order
        self.E5S10 = pn_energy_5pn_so(m1M)
        self.E5S20 = pn_energy_5pn_so(m2M)
        self.S1dot5 = spin_dot_5pn(m1M)
        self.S2dot5 = spin_dot_5pn(m2M)

        # 2PN order
        # 2PN spin-spin averaged terms
        self.E4S1S2Avg = pn_energy_4pn_s1s2(eta)
        self.E4S1OS2OAvg = pn_energy_4pn_s1os2o(eta)
        # 2PN quadrupole-monopole averaged self-spin terms
        self.E4QMS1S1Avg = quadparam1 * pn_energy_4PN_qm_s1s1(m1M)
        self.E4QMS1OS1OAvg = quadparam1 * pn_energy_4PN_qm_s1os1o(m1M)
        self.E4QMS2S2Avg = quadparam2 * pn_energy_4PN_qm_s1s1(m2M)
        self.E4QMS2OS2OAvg = quadparam2 * pn_energy_4PN_qm_s1os1o(m2M)
        # Spin derivative
        self.S1dot4S2Avg = spin_dot_4pn_s2()
        self.S1dot4S2OAvg = spin_dot_4pn_s2o()
        self.S1dot4QMS1OAvg = quadparam1 * spin_dot_4pn_qm_so(m1M)
        self.S2dot4QMS2OAvg = quadparam2 * spin_dot_4pn_qm_so(m2M)

        # 1.5PN order
        self.E3S10 = pn_energy_3pn_so(m1M)
        self.E3S20 = pn_energy_3pn_so(m2M)
        self.S1dot3 = spin_dot_3pn(m1M)
        self.S2dot3 = spin_dot_3pn(m2M)

    def spin_derivatives_avg(self, v, LNh, E1, S1, S2):
        """
        No numba wrapper for the spin derivatives function.
        """

        return _spin_derivatives_avg(
            v,
            LNh,
            E1,
            S1,
            S2,
            self.eta,
            self.S1dot3,
            self.S2dot3,
            self.S1dot4S2Avg,
            self.S1dot4S2OAvg,
            self.S1dot5,
            self.S2dot5,
            self.S1dot7S2,
            self.S2dot7S1,
        )


def _spin_derivatives_avg(
    v,
    LNh,
    E1,
    S1,
    S2,
    eta,
    S1dot3,
    S2dot3,
    S1dot4S2Avg,
    S1dot4S2OAvg,
    S1dot5,
    S2dot5,
    S1dot7S2,
    S2dot7S1,
):
    r"""
    Compute right-hand side of ODE.

    We call it spin derivatives but it also includes the derivatives of LNh and E1.

    Special case of the original function in `lalsuite <https://git.ligo.org/lscsoft/lalsuite/-/blob/master/lalsimulation/lib/LALSimInspiralSpinTaylor.c#L483>`_.

    Parameters
    ----------
    v : float
        :math:`\sqrt[3]{\omega / 2}`
    LNh : ndarray (3,)
        The angular momentum unit vector.
    E1 : ndarray (3,)
        The X axis vector.
    S1 : ndarray (3,)
        The spin vector of the first object.
    S2 : ndarray (3,)
        The spin vector of the second object.
    S1/2dot...: float
        Spin coefficients.

    Returns
    -------
    1D ndarray
        A 1D array with the derivatives of LNh, E1, S1, S2. 12 elements since each vector has 3 components.
    """

    LNhdotS1 = np.dot(LNh, S1)
    LNhdotS2 = np.dot(LNh, S2)

    LN0mag = eta / v

    v2 = v * v
    v5 = v2 * v2 * v

    S1_a0 = S1dot3
    S2_a0 = S2dot3
    S1_a1 = S1dot4S2OAvg * LNhdotS2
    S2_a1 = S1dot4S2OAvg * LNhdotS1
    S1_a2 = S1dot5
    S2_a2 = S2dot5
    S1_a3 = S1dot7S2
    S2_a3 = S2dot7S1

    dS1 = v5 * ((S1_a0 + v * (S1_a1 + v * (S1_a2 + v2 * S1_a3))) * LNh + v * S1dot4S2Avg * S2)
    dS2 = v5 * ((S2_a0 + v * (S2_a1 + v * (S2_a2 + v2 * S2_a3))) * LNh + v * S1dot4S2Avg * S1)

    dS1 = manual_cross(dS1, S1)
    dS2 = manual_cross(dS2, S2)

    L1PN = 1.5 + eta / 6.0
    L2PN = 27.0 / 8.0 - 19.0 / 8.0 * eta + eta * eta / 24.0

    LNmag = LN0mag * (1 + v2 * (L1PN + v2 * L2PN))

    dLNhat = -(dS1 + dS2) / LNmag

    Om = manual_cross(LNh, dLNhat)
    # Is this one really needed?
    dLNh = manual_cross(Om, LNh)
    # With this definition, E1 satisfies the minimal rotation condition.
    dE1 = manual_cross(Om, E1)

    # Equivalent formulas up to num error. No speed gain.
    # dLNh[:] = dLNhat - np.dot(LNh, dLNhat) * LNh
    # dE1[:] = -np.dot(dLNh, E1) * LNh

    return np.array([dLNh[0], dLNh[1], dLNh[2], dE1[0], dE1[1], dE1[2], dS1[0], dS1[1], dS1[2], dS2[0], dS2[1], dS2[2]])


# Define njit version of spin_derivatives function
spin_derivatives_avg_numba = njit(_spin_derivatives_avg)


@njit(inline="always")
def eval_cubic_spline(x, x_breaks, coefs):
    """
    Evaluate a cubic spline in a single point with numba.
    """
    # Find which segment x belongs to
    i = np.searchsorted(x_breaks, x, side="left") - 1

    # Handle edge cases
    if i < 0:
        i = 0
    elif i >= x_breaks.shape[0] - 1:
        i = x_breaks.shape[0] - 2

    dx = x - x_breaks[i]
    c = coefs[:, i]  # coefficients for segment i, e.g. shape (4,)

    # Evaluate cubic: Horner's method (matches C order)
    return ((c[0] * dx + c[1]) * dx + c[2]) * dx + c[3]


@njit(inline="always")
def eval_cubic_spline_array(x_array, x_breaks, coefs):
    """
    Evaluate a cubic spline in an array with numba.
    """
    result = np.empty_like(x_array)

    for j in range(x_array.shape[0]):
        result[j] = eval_cubic_spline(x_array[j], x_breaks, coefs)

    return result


@njit
def unpack(y):
    """
    Unpack the state vector y into its components LNh, E1, S1, S2.
    """
    return y[0:3], y[3:6], y[6:9], y[9:12]


def tphm_spin_derivatives(t, y, v_interpolant, spin_taylor_t4):
    """
    Spin derivatives using a v_interpolant without numba.
    """

    LNh, E1, S1, S2 = unpack(y)

    v = v_interpolant(t)

    return spin_taylor_t4.spin_derivatives_avg(v, LNh, E1, S1, S2)


@njit()
def tphm_spin_derivatives_numba(
    t,
    y,
    t_breaks,
    coeffs,
    eta,
    S1dot3,
    S2dot3,
    S1dot4S2Avg,
    S1dot4S2OAvg,
    S1dot5,
    S2dot5,
    S1dot7S2,
    S2dot7S1,
):
    """
    Spin derivatives using a v_interpolant with numba.
    """

    LNh, E1, S1, S2 = unpack(y)

    v = eval_cubic_spline(t, t_breaks, coeffs)

    return spin_derivatives_avg_numba(
        v,
        LNh,
        E1,
        S1,
        S2,
        eta,
        S1dot3,
        S2dot3,
        S1dot4S2Avg,
        S1dot4S2OAvg,
        S1dot5,
        S2dot5,
        S1dot7S2,
        S2dot7S1,
    )


#####################################
#  Spin derivatives with imr_omega  #
#####################################
# Using imr_omega instead of the interpolant is more precise and independent of the time array
# hwoever, it is significantly slower.


@njit
def v_of_omega(omega):
    """
    Compute v from a single value of omega.
    """
    return np.cbrt(0.5 * omega)


def tphm_spin_derivatives_imr_omega(t, y, pPhase22, spin_taylor_t4):
    """
    Spin derivatives using imr_omega without numba.
    """

    LNh, E1, S1, S2 = unpack(y)

    v = v_of_omega(pPhase22.imr_omega(t))

    return spin_taylor_t4.spin_derivatives_avg(v, LNh, E1, S1, S2)


def tphm_spin_derivatives_imr_omega_numba(
    t,
    y,
    pPhase22,
    eta,
    S1dot3,
    S2dot3,
    S1dot4S2Avg,
    S1dot4S2OAvg,
    S1dot5,
    S2dot5,
    S1dot7S2,
    S2dot7S1,
):
    """
    Spin derivatives using imr_omega with numba.
    """

    LNh, E1, S1, S2 = unpack(y)

    v = v_of_omega(pPhase22.imr_omega(t))

    return spin_derivatives_avg_numba(
        v,
        LNh,
        E1,
        S1,
        S2,
        eta,
        S1dot3,
        S2dot3,
        S1dot4S2Avg,
        S1dot4S2OAvg,
        S1dot5,
        S2dot5,
        S1dot7S2,
        S2dot7S1,
    )


class Numerical:
    """
    Class with extra methods for evolving spin equations and compute numerical angles added to ``pPrec``.
    """

    def evolve_orbit(self, tinit, tend, t_eval=None):
        """
        Solve PN spin equations from tinit to tend in a custom time array ``t_eval``.

        LNh is the Z axis of the rotating frame, while E1 is the X axis.

        The evolution of E1 is not needed for computing the Euler angles. 
        If removed, the solution is slightly different since the solver chooses different adaptive points and interpolation methods.
        E1 is evolved satisfying the minimal rotation condition. This is used to obtain the quaternions without computing the Euler \
            angles nor integrating gamma. 
        It also prevents the loss of precission due to building CubicSplines, derive them and then numerically integrate them.


        Returns
        -------
        Tuple with 4 (3, N)-ndarrays and one 1D ndarray
            LNh, E1, S1, S2, and the evaluated times t_eval.

        """

        # Set up SpinTaylorT4
        self.spin_taylor_t4 = SpinTaylor(self._pWF.eta, self._pWF.m1, self._pWF.m2)

        # Inital conditions
        LNh = np.array([0, 0, 1])
        E1 = np.array([1, 0, 0])
        S1 = self.S1
        S2 = self.S2
        yinit = np.array([LNh[0], LNh[1], LNh[2], E1[0], E1[1], E1[2], S1[0], S1[1], S1[2], S2[0], S2[1], S2[2]])

        # Set the arguments for the ODE solver
        # rhs: function computing the derivatives for each component
        # args: arguments passed rhs function
        if self.numba_derivatives is False:
            if self.v_function == "imr_omega":
                rhs = tphm_spin_derivatives_imr_omega
                args = [self._pPhase22, self.spin_taylor_t4]
            elif self.v_function == "interpolant":
                rhs = tphm_spin_derivatives
                args = [self.v_interpolant, self.spin_taylor_t4]
        else:
            # Pass also the outputs (derivatives) as arguments to avoid creation of arrays
            # at each evaluation of the solver
            if self.v_function == "imr_omega":
                rhs = tphm_spin_derivatives_imr_omega_numba
                args = [
                    self._pPhase22,
                    self.spin_taylor_t4.eta,
                    self.spin_taylor_t4.S1dot3,
                    self.spin_taylor_t4.S2dot3,
                    self.spin_taylor_t4.S1dot4S2Avg,
                    self.spin_taylor_t4.S1dot4S2OAvg,
                    self.spin_taylor_t4.S1dot5,
                    self.spin_taylor_t4.S2dot5,
                    self.spin_taylor_t4.S1dot7S2,
                    self.spin_taylor_t4.S2dot7S1,
                ]
            elif self.v_function == "interpolant":
                rhs = tphm_spin_derivatives_numba
                args = [
                    self.v_interpolant.x,
                    self.v_interpolant.c,
                    self.spin_taylor_t4.eta,
                    self.spin_taylor_t4.S1dot3,
                    self.spin_taylor_t4.S2dot3,
                    self.spin_taylor_t4.S1dot4S2Avg,
                    self.spin_taylor_t4.S1dot4S2OAvg,
                    self.spin_taylor_t4.S1dot5,
                    self.spin_taylor_t4.S2dot5,
                    self.spin_taylor_t4.S1dot7S2,
                    self.spin_taylor_t4.S2dot7S1,
                ]

        # Choose where to evaluate the solution. None will output the internal solver points.
        t_eval = t_eval.get() if self.xp == cp else t_eval  # t_eval must be on the cpu
        t_eval_solver = None if self.interpolate is not None else t_eval
        # Actual ODE solver execution (Runge-Kutta 45)
        res = solve_ivp(
            rhs,
            (tinit, tend),
            yinit,
            method="RK45",
            args=args,
            t_eval=t_eval_solver,
            rtol=self.rtol,
            atol=self.atol,
        )

        # Get solution in the proper format, interpolate if needed
        if self.interpolate == "ode_solution":
            if self.cubic_interpolation_for_ode:
                # Make CubicSplines of each of the evolved components and evaluate them fast with numba
                ysolution = np.empty((len(res.y), len(t_eval)))
                sign = np.copysign(1, res.t[1] - res.t[0])
                for i in range(len(res.y)):
                    spline = CubicSpline(sign * res.t, res.y[i])
                    # The custom spline might introduce small differences
                    ysolution[i] = eval_cubic_spline_array(sign * t_eval, spline.x, spline.c)
            else:
                ysolution = self.xp.empty((len(res.y), len(t_eval)))
                sign = np.copysign(1, res.t[1] - res.t[0])
                tt = self.xp.array(sign * res.t)
                for idx, ysol in enumerate(res.y):
                    ysolution[idx] = self.xp.interp(cp.ascontiguousarray(cp.array(sign * t_eval)), tt, self.xp.array(ysol))

        else:
            # interpolate = None or "euler_angles"
            ysolution = res.y
            if self.interpolate == "euler_angles":
                # Need to output the new t_eval where the solution is evaluated
                t_eval = res.t

        # Move to the GPU if cuda is demanded
        if self.xp == cp:
            ysolution = self.xp.array(ysolution)

        # Distribution solution in vectors
        LNh = self.xp.empty((3, len(ysolution[0])))
        E1 = self.xp.empty((3, len(ysolution[0])))
        S1 = self.xp.empty((3, len(ysolution[0])))
        S2 = self.xp.empty((3, len(ysolution[0])))
        LNh[0], LNh[1], LNh[2], E1[0], E1[1], E1[2], S1[0], S1[1], S1[2], S2[0], S2[1], S2[2] = ysolution

        S1 /= self._pWF.m1_2
        S2 /= self._pWF.m2_2

        return LNh, E1, S1, S2, t_eval

    def forward_integration(self, times=None):
        """
        Evolve orbit from tref to t=0.
        """

        # Build interpolant for v(t) used in the rhs of the ODE solver.
        # The other option is to use "imr_omega" function directly (that is more precise).
        if self.v_function == "interpolant":
            vorb = self.xp.cbrt(0.5 * self._pPhase22.imr_omega(times))

            # Define v_interpolant
            if self.xp == np:
                self.v_interpolant = CubicSpline(times, vorb)
            else:
                # v needs to be in the cpu for the ODE solver
                self.v_interpolant = CubicSpline(times.get(), vorb.get())

        # Set t_eval and t_span where to evaluate the ODE solution.
        # t_eval will be overriden to use the internal solver's point if interpolate != None
        if self.use_closest_time_to_tref:
            self.idx_tref = (
                int(np.round(np.abs(self._pWF.tref - self._pWF.tmin) / self._pWF.delta_t))
                if self._pWF.delta_t > 0
                else self.xp.argmin(self.xp.abs(times - self.pWF.tref))
            )
            self.tref_prime = times[self.idx_tref]

            t_eval = times[(times >= self.tref_prime) & (times <= 0)]
            tinit = self.tref_prime
        else:
            t_eval = times[(times >= self._pWF.tref) & (times <= 0)]
            tinit = self._pWF.tref

        # Include t=0 to get the values for the Ringdown attachment
        self.t0_added_to_array = False
        if t_eval[-1] != 0:
            t_eval = self.xp.append(t_eval, 0.0)
            self.t0_added_to_array = True

        # Evolve orbit from tref to t=0.
        self.LNhatev, self.E1ev, self.S1ev, self.S2ev, t_eval = self.evolve_orbit(tinit=tinit, tend=np.float64(0), t_eval=t_eval)
        if self.interpolate == "euler_angles":
            self.t_eval = self.xp.array(t_eval)

    def backward_integration(self, times=None):
        """
        Evolve orbit from tref to tmin.
        """

        # Choose between using the computed tref or the closest point in the time array
        if self.use_closest_time_to_tref:
            # Using closest point to tref
            if self.idx_tref == 0:
                # This means that tref_prime=tmin and there is not backward evolution
                # self.tref_prime is already set from the forward evolution
                pass
            self.tref_prime = times[self.idx_tref]
            t_eval = times[(times >= self._pWF.tmin) & (times < self.tref_prime)][::-1]
            tinit = self.tref_prime
        else:
            # Skip tref in t_eval to avoid point duplication with the forward integration
            t_eval = times[(times >= self._pWF.tmin) & (times < self._pWF.tref)][::-1]
            tinit = self._pWF.tref

        # Case with no backwards evolution
        if tinit == self._pWF.tmin:
            return self.LNhatev, self.E1ev

        # Evolve orbit from tref to tmin
        LNhatev, E1ev, S1ev, S2ev, t_eval = self.evolve_orbit(
            tinit=tinit,
            tend=self._pWF.tmin,
            t_eval=t_eval,
        )

        ###############################################
        #   Prepend the evolution from tref to tmin   #
        ###############################################
        if self.interpolate == "euler_angles":
            # Avoid tref duplication. In this case, the tinit in forward and backwards is the same
            t_eval = self.xp.flip(self.xp.array(t_eval[1:]))
            self.t_eval = self.xp.concatenate((t_eval, self.t_eval))
            LNhatev = LNhatev[:, 1:]
            E1ev = E1ev[:, 1:]

        LNhatev = self.xp.flip(LNhatev, 1)
        LNhatev = self.xp.concatenate((LNhatev, self.LNhatev), 1)

        E1ev = self.xp.flip(E1ev, 1)
        E1ev = self.xp.concatenate((E1ev, self.E1ev), 1)

        # Optionally store arrays
        if self.store_arrays is True:
            if self.interpolate == "euler_angles":
                # Skip duplicated point for tref
                S1ev = S1ev[:, 1:]
                S2ev = S2ev[:, 1:]

            S1ev = self.xp.flip(S1ev, 1)
            S2ev = self.xp.flip(S2ev, 1)

            self.LNhatev = LNhatev
            self.E1ev = E1ev
            self.S1ev = self.xp.concatenate((S1ev, self.S1ev), 1)
            self.S2ev = self.xp.concatenate((S2ev, self.S2ev), 1)

        return LNhatev, E1ev

    def evolved_final_spin(self, LNhat, S1, S2):
        """
        Compute the final spin from evolved quantities. Eq. 25 arxiv:2105.05872

        The aligned final spin contribution is also computed from the evolved quantities and its sign is copied to the precessing one

        Update self._pWF.afinal_prec and self.EulerRDslope
        """

        # Eq. 25 arxiv:2105.05872
        norm1, norm2 = self._pWF.m1_2, self._pWF.m2_2

        s1peak = norm1 * S1[:, -1]
        s2peak = norm2 * S2[:, -1]
        lnpeak = LNhat[:, -1]

        s1Lpeak = np.float64(np.inner(s1peak, lnpeak))
        s2Lpeak = np.float64(np.inner(s2peak, lnpeak))

        s1parallel = s1Lpeak * lnpeak
        s2parallel = s2Lpeak * lnpeak

        s1perp = s1peak - s1parallel
        s2perp = s2peak - s2parallel

        self.Sperp = np.float64(np.linalg.norm(s1perp + s2perp))
        self.af_nonprec = IMRPhenomX_FinalSpin2017(self._pWF.eta, s1Lpeak / norm1, s2Lpeak / norm2)

        Sf = np.copysign(1, self.af_nonprec) * np.sqrt(self.Sperp * self.Sperp + self.af_nonprec * self.af_nonprec)
        Sf = 1 if Sf > 1 else Sf
        Sf = -1 if Sf < -1 else Sf

        self.af_evolved = Sf

        # Update afinal_prec for version 4
        if self.final_spin_version == 4:
            self._pWF.afinal_prec = self.af_evolved

        # Compute slope for the ringdown attachment
        self.EulerRDslope = self.NumEulerRDslope = self.get_euler_slope(self._pWF.afinal_prec, self._pWF.Mfinal)

        return Sf

    def compute_numerical_angles(self, LNhat, times):
        r"""
        Compute numerical angles alpha, beta, gamma for a given LN evolution plus ringdown attachment.

        The input LNhat is the evolved, normalized one. It is transformed to the J-frame with the angles phiJ_Sf, thetaJ_Sf, kappa.

        Then the Euler angles from J to L are:

        .. math::
            \alpha = \operatorname{atan2}(L_{N,y}, L_{N,x})
            \cos(\beta) = L_{N,z}.

        :math:`\gamma` is numerically integrated according to the minimal rotation condition.


        if ``self.interpolate`` != "euler_angles":
            times corresponds to the points where LNhat is evaluated plus the points in the ringdown.

        if ``self.interpolate`` == "euler_angles":
            LNhat is evaluated in ``self.t_eval``, times can be any array and the Euler angles are evaluated with CubicSplines.

        Sets the angle offsets from J to L0: alphaJtoL0, cosbetaJtoL0, gammaJtoL0

        Returns
        -------
        Tuple with 3 1D ndarrays
            alpha, cosbeta, gamma
        """

        # Rotate LN vector to the J-frame. Eq. C13 arxiv:2004.06503
        LNhat = self.rotate_z(-self.phiJ_Sf, LNhat)
        LNhat = self.rotate_y(-self.thetaJ_Sf, LNhat)
        LNhat = self.rotate_z(-self.kappa, LNhat)

        # Get alpha and beta from LN
        alpha = self.xp.arctan2(LNhat[1], LNhat[0])
        cosbeta = LNhat[2]

        # Set offset for alpha
        self.num_alphaOff = self.alphaOff - self.alpha_ref
        alpha += self.num_alphaOff

        # Unwrap alpha angle
        alpha = self.xp.unwrap(alpha)

        # Build and evaluate splines for Euler angles in input times array.
        # If this option is selected the LNhat is evaluated in self.t_eval.
        if self.interpolate == "euler_angles":
            if self.xp == np:
                alpha_s = CubicSpline(self.t_eval, alpha)
                cosbeta_s = CubicSpline(self.t_eval, cosbeta)
                alpha = eval_cubic_spline_array(times[times <= 0], alpha_s.x, alpha_s.c)
                cosbeta = eval_cubic_spline_array(times[times <= 0], cosbeta_s.x, cosbeta_s.c)
            else:
                alpha = self.xp.interp(times[times <= 0], self.t_eval, alpha)
                cosbeta = self.xp.interp(times[times <= 0], self.t_eval, cosbeta)
            if self.store_arrays is False:
                del self.t_eval

        # Integrate gamma up to t=0
        if self.analytical_RD_gamma:
            gamma = self.gamma_integration(times, alpha, cosbeta)
            # Value of gamma at t=0 (t=0 is enforced in the last point of the evolution, disregarding tof he input time array.)
            self.gammaRD0 = gamma[-1]

        # Values at t=0. (t=0 is enforced in the last point of the evolution, disregarding of the input time array.)
        self.alphaRD0 = alpha[-1]
        self.cosbetaRD0 = cosbeta[-1]

        # Remove t=0 if it was added in forward_integration
        if self.t0_added_to_array:
            alpha = alpha[:-1]
            cosbeta = cosbeta[:-1]
            if self.analytical_RD_gamma:
                gamma = gamma[:-1]

        # Ringdown attachment for alpha, cosbeta
        alphaRD_attach = self.alphaRD0 + self.EulerRDslope * times[times > 0]
        alpha = self.xp.concatenate((alpha, alphaRD_attach))
        cosbetaRD_attach = self.xp.full(len(alphaRD_attach), self.cosbetaRD0)
        cosbeta = self.xp.concatenate((cosbeta, cosbetaRD_attach))

        # Analytical RD attachment for gamma.
        # Integral (-da/dt cos_beta) = Integral (-EulerRDslope * cosbetRD0) =
        # gammaRD0 + -EulerRDslope * cosbetaRD * t = gammaRD0 - cosbetaRD0 (alphaRD - alphaRD0)
        if self.analytical_RD_gamma:
            gammaRD_attach = self.gammaRD0 - self.cosbetaRD0 * (alphaRD_attach - self.alphaRD0)
            gamma = self.xp.concatenate((gamma, gammaRD_attach))

        # Gamma integration from alpha and beta including RD part
        if self.analytical_RD_gamma is False:
            gamma = self.gamma_integration(times, alpha, cosbeta)
            self.gammaRD0 = gamma[self.xp.argmin(self.xp.abs(times))]

        return alpha, cosbeta, gamma

    def gamma_integration(self, times, alpha, cosbeta):
        r"""
        Numerical integration of :math:`\dot{\gamma}` over the full time array to fulfill minimal rotation condition.

        :math:`\dot{\gamma} = - \dot{\alpha} \cos(\beta)`.
        Eq. 18 :cite:`Boyle_2011`.

        Different methods selected with option ``pPrec.gamma_integration_method``:

            - `'piecewise_integral'`: analytical integral in each time interval of the 5th order "spline" resulting from the multiplication of two cubic splines: CS.derivative() * CS.
            - `'boole'`: use Boole's rule, assumes equispaced grid. This is the only one supported for cuda=True and in this case it uses linear interpolation instead of cubic spline.
            - `'antiderivative'`: use .antiderivative() method of CubicSpline. This spline is built after evaluating the alpha.derivative() and cosbeta() CubicSplines. It loses accuracy since higher order from the multiplication of alpha_der * cosbeta are discarded.

        Returns
        -------
        1D ndarray
            Integrated :math:`\gamma` satisfying minimal rotation condition.
        """

        # For analytical_RD_gamma, integrate only up to t=0
        if self.analytical_RD_gamma:
            times_neg = times[times <= 0]
            if times_neg[-1] != 0:
                # Add t=0 to the times array if it is not present
                times_neg = self.xp.append(times_neg, 0.0)
            times = times_neg

        # Integrate gamma with different methods or set right-hand-side function for Boole's rule.
        # cpu version
        if self.xp == np:
            alpha_s = CubicSpline(times, alpha)
            cosbeta_s = CubicSpline(times, cosbeta)
            der_alpha_s = alpha_s.derivative()

            # Choose integration method
            if self.gamma_integration_method == "piecewise_integral":
                gamma = -integrate_product_cubic_splines_vectorized(der_alpha_s, cosbeta_s)
            elif self.gamma_integration_method == "antiderivative":
                gamma_s = CubicSpline(times, -der_alpha_s(times) * cosbeta).antiderivative()
                if self.interpolate == "euler_angles":
                    gamma = eval_cubic_spline_array(times, gamma_s.x, gamma_s.c)
                else:
                    gamma = gamma_s(times)
            elif self.gamma_integration_method == "boole":

                def rhs(t):
                    der_alpha = der_alpha_s(t)
                    new_cosbeta = cosbeta_s(t)
                    return -der_alpha * new_cosbeta

            else:
                raise NotImplementedError(
                    f"gamma_integration_method = {self.gamma_integration_method} not supported.\
                                          Options are:(boole, antiderivative, piecewise_integral) "
                )

        # For gpu version, only Boole's rule is available, use linear interpolant
        else:

            def rhs(t):
                new_alpha = self.xp.interp(t, times, alpha)
                der_alpha = self.xp.gradient(new_alpha, t)
                new_cosbeta = self.xp.interp(t, times, cosbeta)
                return -der_alpha * new_cosbeta

        # Integrate with Boole's Rule (https://en.wikipedia.org/wiki/Boole%27s_rule)
        if self.gamma_integration_method == "boole":
            # If analytical_RD_gamma: integrate only the PN part up to t=0.
            length = len(times)

            gamma = self.xp.zeros(length)
            gamma[0] = -alpha[0]
            t1 = times[: length - 1]
            t2 = times[1:length]
            h = self.xp.abs(times[1] - times[0]) / 4
            x0 = t1
            x1 = t1 + h
            x2 = t1 + 2 * h
            x3 = t1 + 3 * h
            x4 = t2
            integral = 2 * h / 45 * (7 * rhs(x0) + 32 * rhs(x1) + 12 * rhs(x2) + 32 * rhs(x3) + 7 * rhs(x4))
            gamma[1:] = integral
            gamma = self.xp.cumsum(gamma)

        # Angles from J to L0
        # Choose between evaluating the splines at tref or at the closest point in the array.
        if self.use_closest_time_to_tref:
            alpha_ref = alpha[self.idx_tref]
            cosbeta_ref = cosbeta[self.idx_tref]
            gamma_ref = gamma[self.idx_tref]
        else:
            if self.xp == np:
                alpha_ref = alpha_s(self._pWF.tref).item()
                cosbeta_ref = cosbeta_s(self._pWF.tref).item()
                if self.gamma_integration_method == "antiderivative":
                    gamma_ref = gamma_s(self._pWF.tref).item()
                else:
                    gamma_ref = CubicSpline(times, gamma)(self._pWF.tref).item()
            else:
                alpha_ref = self.xp.interp(self.xp.asarray([self._pWF.tref]), times, alpha)[0]
                cosbeta_ref = self.xp.interp(self.xp.asarray([self._pWF.tref]), times, cosbeta)[0]
                gamma_ref = self.xp.interp(self.xp.asarray([self._pWF.tref]), times, gamma)[0]

        self.alphaJtoL0 = alpha_ref
        self.cosbetaJtoL0 = cosbeta_ref
        self.gammaJtoL0 = -alpha_ref

        # Set up proper offset
        gamma += -gamma_ref - alpha_ref

        return gamma


def integrate_product_cubic_splines_vectorized(cs1, cs2, xp=np):
    """
    Vectorized integration of the product of two splines.

    Parameters
    ----------
    cs1: CubicSpline.derivative
        Derivative of the first cubic spline with CubicSpline.derivative()
    cs2: CubicSpline
        The second cubic spline

    Returns
    -------
    1D ndarray
        Indefinite integral of the product.
    """

    t = cs1.x
    h = t[1:] - t[:-1]  # shape (n_intervals,)

    # Coefficients: shape (4, n_intervals)
    a = cs1.c
    b = cs2.c

    # Compute all c0..c5 (shape: (7, n_intervals))
    c0 = a[2] * b[3]
    c1 = a[2] * b[2] + a[1] * b[3]
    c2 = a[2] * b[1] + a[1] * b[2] + a[0] * b[3]
    c3 = a[2] * b[0] + a[1] * b[1] + a[0] * b[2]
    c4 = a[1] * b[0] + a[0] * b[1]
    c5 = a[0] * b[0]

    delta_I = h * (c0 + h * (c1 / 2 + h * (c2 / 3 + h * (c3 / 4 + h * (c4 / 5 + h * c5 / 6)))))

    cumulative = xp.zeros(len(t))
    cumulative[1:] = xp.cumsum(delta_I)

    return cumulative
