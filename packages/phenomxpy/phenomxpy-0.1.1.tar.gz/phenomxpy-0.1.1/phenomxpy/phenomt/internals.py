# Copyright (C) 2023  Cecilio García Quirós
import numpy as np

try:
    import cupy as cp
except ImportError:
    cp = None

from scipy.optimize import brentq

from phenomxpy.fft import ConditioningParams, check_pow_of_2
from .fits import *
from .numba_ansatze import *
from phenomxpy.utils import HztoMf, ModeToString, SecondtoMass, chi_eff, qofeta, logger


class Cache:
    """
    Auxiliary class to store quantities that will be recycled (e.g. imr_phase22)
    It transform kwargs into attributes of the object.
    """

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class pWF:
    r"""
    Structure storing common waveform quantities and options for all the modes.

    Parameters
    ----------
    eta: float
        Symmetric mass ratio [0, 0.25].
    s1, s2: floats or (3,) ndarrays
        Spinz components or cartesian spin vectors.
        s1 corresponds to the most massive object
    total_mass: float
        Total mass in solar masses.
    f_min: float
        Minimum frequency. In Hz if ``total_mass`` is provided, if not in units of mass.
    f_ref: float
        Reference frequency. In Hz if ``total_mass`` is provided, if not in units of mass.
    delta_t: float
        Time spacing. In seconds if ``total_mass`` is provided, if not in units of mass.
    delta_f: float
        Frequency spacing for Fourier transform  in Hz.
        Only used for conditioning (``condition`` = ``True``).
    eccentricity: float
        Initial eccentricity defined at ``f_ref``. [0, 1]
    mean_anomaly: float
    inclination: float
        Inclination angle in radians. [0, :math:`\pi`]
    phi_ref: float
        Azimuthal angle in radians for Ylms defined as :math:`\pi/2` - ``phi_ref``.
    polarization_angle: float
        Polarization angle in radians.
    distance: float
        Distance in Megaparsecs.
    cuda: bool
        If True, use cupy if installed to run on the GPU.
    numba_ansatze: bool
        When evaluating the ansatze in the full time array, use the numba version.
        Deactivated when using cuda.
    condition: bool
        Compute conditioning parameters and generated conditioned waveforms when evaluated.
    rtol, atol: float
        Tolerances used for the solver computing ``tmin`` from ``f_min`` and ``tref`` from ``f_ref``.
    **kwargs:
        Not used arguments inherited from other class calls
    """

    def __init__(
        self,
        eta=None,
        s1=None,
        s2=None,
        f_min=None,
        f_ref=None,
        total_mass=0,
        delta_t=0,
        delta_f=0,
        eccentricity=0,
        mean_anomaly=0,
        inclination=0,
        phi_ref=0,
        polarization_angle=0,
        distance=0,
        f_max=None,
        cuda=False,
        numba_ansatze=True,
        condition=False,
        rtol=1e-12,
        atol=1e-12,
        tlow_fit=True,
        **kwargs,
    ):
        # Check for required arguments
        self.eta = eta
        self.s1 = s1
        self.s2 = s2
        self.f_min = f_min
        for var in ["eta", "s1", "s2", "f_min"]:
            if getattr(self, var) is None:
                raise ValueError(f"{var} cannot be None, need to provide a value")

        # Sanity checks
        if eta > 0.25:
            logger.warning(f"Rounding {eta} to 0.25.")
            eta = 0.25
        if eta < 0 or eta > 0.25:
            raise ValueError(f"eta must be between [0, 0.25], got {eta}")
        if np.linalg.norm(np.array(s1)) > 1:
            raise ValueError("s1 norm must be betwen [0, 1]")
        if np.linalg.norm(np.array(s1)) > 1:
            raise ValueError("s2 norm must be betwen [0, 1]")
        if f_min <= 0:
            raise ValueError("f_min must be > 0")
        if total_mass < 0:
            raise ValueError("total_mass must be > 0")
        if delta_f < 0:
            raise ValueError("delta_f must be >= 0")

        # Set required arguments
        self.eta = eta
        self.s1 = np.array(s1)
        self.s2 = np.array(s2)
        self.f_min = f_min

        # End the waveform 500M after peak time
        self.tEnd = 500

        # Set options
        self.condition = condition
        self.rtol = rtol
        self.atol = atol
        self.tlow_fit = tlow_fit
        self.cuda = cuda
        self.numba_ansatze = numba_ansatze if self.cuda is False else False
        self.extra_options = kwargs

        # Set optional parameters
        self.total_mass = total_mass
        self.f_ref = f_min if f_ref is None or f_ref == 0 else f_ref
        self.inclination = inclination
        self.phi_ref = phi_ref
        self.polarization_angle = polarization_angle
        self.distance = distance
        self.eccentricity = eccentricity
        self.mean_anomaly = mean_anomaly
        self.delta_t = delta_t
        self.delta_t_sec = delta_t
        self.delta_f = delta_f

        # f_max and delta_t_sec cannot be given at the same time
        if f_max is not None and self.delta_t_sec is not None:
            raise ValueError(
                "Cannot provide f_max and delta_t_sec at the same time. f_max is understood as 0.5 / delta_t. \n"
                "If f_max is provided then delta_t is modified so that f_max = 0.5 / delta_t."
            )

        # Set f_max and recompute delta_t_sec if needed
        self.f_max = f_max
        if f_max is not None:
            self.delta_t_sec = 0.5 / f_max
        elif self.delta_t_sec > 0:
            self.f_max = 0.5 / self.delta_t_sec

        # Sanity check on f_max
        if self.f_max is not None and self.f_max <= self.f_min:
            raise ValueError("f_max must be > f_min. Got {self.f_max:.2e} <= {self.f_min:.2e}")

        # Set derived quantities
        self.s1z = s1[2] if isinstance(s1, list) else s1
        self.s2z = s2[2] if isinstance(s2, list) else s2
        self.q = qofeta(eta)
        self.eta = eta
        self.delta = np.sqrt(1 - 4 * eta)
        # Component masses if sum is 1
        self.m1 = m1ofeta(eta)
        self.m2 = m2ofeta(eta)
        self.M = self.m1 + self.m2
        self.m1_2 = self.m1 * self.m1
        self.m2_2 = self.m2 * self.m2
        # Component masses if sum is total_mass
        self.mass1 = m1ofeta(eta, total_mass=total_mass) if total_mass > 0 else None
        self.mass2 = m2ofeta(eta, total_mass=total_mass) if total_mass > 0 else None
        # Auxiliary spin values
        self.s1_dim = self.s1 * self.m1_2
        self.s2_dim = self.s2 * self.m2_2
        self.chis = 0.5 * (self.s1z + self.s2z)
        self.chia = 0.5 * (self.s1z - self.s2z)
        self.sTotR = sTotR(self.eta, self.s1z, self.s2z)
        self.chi_eff = chi_eff(self.eta, self.s1z, self.s2z)
        self.dchi = self.s1z - self.s2z
        # Final remnant quantities
        self.afinal = IMRPhenomX_FinalSpin2017(self.eta, self.s1z, self.s2z)
        self.afinal_prec = self.afinal
        self.Mfinal = IMRPhenomX_FinalMass2017(self.eta, self.s1z, self.s2z)

        # Check if tref and tmin are provided as input arguments
        if "tref" in kwargs:
            self.tref = kwargs["tref"]
            if self.tref > 0:
                raise ValueError(f"Input tref must be <=0, got {self.tref}.")
        if "tmin" in kwargs:
            self.tmin = kwargs["tmin"]
            if self.tmin > 0:
                raise ValueError(f"Input tmin must be <=0, got {self.tmin}.")

        # Conditioning parameters
        if self.condition:
            if total_mass == 0:
                raise ValueError("Need to provide total_mass to use conditioning routines.")
            self.cparams = ConditioningParams(self.f_min, self.mass1, self.mass2, self.s1z, self.s2z)
            # Updated f_min
            self.f_min = self.cparams["f_min"]
            # This is the input f_min in ConditioningParams
            self.original_f_min = self.cparams["original_f_min"]
            f_nyquist = self.f_max
            if self.delta_f > 0:
                n = np.round(f_nyquist / self.delta_f)
                truth, exponent = check_pow_of_2(n)
                if not truth:
                    f_nyquist = 2 ** (exponent) * self.delta_f
            # Modified dt for even powers of 2.
            # LAL computes this when calling FD, not for TD conditioned.
            self.delta_t_sec = 0.5 / f_nyquist

        # Mass independent quantities
        self.Mfmin = HztoMf(self.f_min, total_mass) if total_mass > 0 else self.f_min
        self.Mfref = HztoMf(self.f_ref, total_mass) if total_mass > 0 else self.f_ref
        self.delta_t = SecondtoMass(self.delta_t_sec, total_mass) if total_mass > 0 else self.delta_t


class pWFHM(pWF):
    """
    Subclass to add mode specific quantities to an input pWF

    If no pWF is given, then a new pWF is created.
    """

    def __init__(self, mode=[2, 2], pWF_input=None, **kwargs):
        if pWF_input is not None and isinstance(pWF_input, pWF):
            # Copy all properties from the Parent instance
            self.__dict__.update(vars(pWF_input))
        else:
            super().__init__(**kwargs)

        self.mode = int(ModeToString(mode))
        self.ell, self.emm = int(mode[0]), int(mode[1])
        # ringdown and damping frequencies for fundamental mode
        self.fring = IMRPhenomT_fringfit(self.afinal, self.mode) / self.Mfinal
        self.fdamp = IMRPhenomT_fdampfit(self.afinal, self.mode) / self.Mfinal
        # damping frequency second overtone
        self.fdampn2 = IMRPhenomT_fdampn2fit(self.afinal, self.mode) / self.Mfinal
        # ringdown and damping frequencies for the precessing final spin
        self.fring_prec = IMRPhenomT_fringfit(self.afinal_prec, self.mode) / self.Mfinal
        self.fdamp_prec = IMRPhenomT_fdampfit(self.afinal_prec, self.mode) / self.Mfinal
        self.fdampn2_prec = IMRPhenomT_fdampn2fit(self.afinal_prec, self.mode) / self.Mfinal


class pAmp:
    """
    Class for computing amplitude coefficients and define amplitude ansatze.

    Parameters
    ----------
    pWF: pWF
        pWF structure with waveform parameters
    pPhase22: pPhase
        pPhase structure for the 22 mode to be used by subdominant harmonics.
    """

    def __init__(self, pwf, pphase22):
        """Set coefficients needed for the amplitude ansatze"""
        self.xp = pphase22.xp
        self._pPhase = pphase22
        self._pWF = pwf
        self._set_inspiral_cut()
        self._set_ringdown_cut()
        self._set_pn_coefficients()
        self._set_inspiral_collocation_points()
        self._set_inspiral_coefficients()
        self._set_ringdown_coefficients()
        self._set_intermediate_coefficients()

    def _set_inspiral_cut(self):
        """
        Transition time between inspiral and intermediate region for the amplitude (t=-150M).
        """
        self.inspiral_cut = -150.0

    def _set_ringdown_cut(self):
        """
        Transition time between intermediate and ringdown region for the amplitude (from parameter space fits).
        """
        self.ringdown_cut = self.tshift = IMRPhenomT_tshift(self._pWF)

    def _set_pn_coefficients(self):
        """
        PN coefficients for complex amplitude

        3PN non-spinning Eq 9.4 :cite:`Blanchet_2008`.
        3.5PN non-spinning `Eq. 43 :cite:`Faye_2012`.
        1.5 PN spinning Eq 4.17 :cite:`Arun`.
        2 PN spinning `Eq. 4.27 :cite:`Buonanno`.

        Transformation to python code in `Mathematica <https://gitlab.com/imrphenom-dev/reviews/qc-phenomt/-/blob/main/theory_notebooks/PNCoefficients.nb>`__.

        There is a factor missing for each mode because they were rotated so that the real part is closer to the absolute value.
        The factors for each mode to recover the expressions in the paper are: 22 1, 21 i, 33 -i, 44 -1, 55 i.
        These factors are included through offsets in the phase, see pPhase._set_offsets.
        """

        eta, delta = [self._pWF.eta, self._pWF.delta]

        chis = self._pWF.chis
        chia = self._pWF.chia
        Sc = self._pWF.m1_2 * self._pWF.s1z + self._pWF.m2_2 * self._pWF.s2z
        Sigmac = self._pWF.m2 * self._pWF.s2z - self._pWF.m1 * self._pWF.s1z

        eta2 = eta * eta
        eta3 = eta * eta2

        self.fac0 = 2 * eta * np.sqrt(16 * np.pi / 5)

        if self._pWF.mode == 22:
            S0 = self._pWF.m1 * self._pWF.s1z + self._pWF.m2 * self._pWF.s2z
            self.ampN = 1
            self.amp0halfPNreal = 0
            self.amp0halfPNimag = 0
            self.amp1PNreal = -107 / 42 + (55 * eta) / 42
            self.amp1PNimag = 0
            self.amp1halfPNreal = (-4 * chis) / 3 - (4 * chia * delta) / 3 + (4 * chis * eta) / 3 + 2 * np.pi
            self.amp1halfPNimag = 0
            self.amp2PNreal = -2173 / 1512 - (1069 * eta) / 216 + (2047 * eta2) / 1512 + S0**2
            self.amp2PNimag = 0
            self.amp2halfPNreal = (-107 * np.pi) / 21 + (34 * eta * np.pi) / 21
            self.amp2halfPNimag = -24 * eta
            self.amp3PNreal = (
                27027409 / 646800
                - (278185 * eta) / 33264
                - (20261 * eta2) / 2772
                + (114635 * eta3) / 99792
                - (856 * np.euler_gamma) / 105
                + (2 * np.pi**2) / 3
                + (41 * eta * np.pi**2) / 96
            )
            self.amp3PNimag = (428 * np.pi) / 105
            self.amp3halfPNreal = (-2173 * np.pi) / 756 - (2495 * eta * np.pi) / 378 + (40 * eta2 * np.pi) / 27
            self.amp3halfPNimag = (14333 * eta) / 162 - (4066 * eta2) / 945
            self.amplog = -428 / 105
        elif self._pWF.mode == 21:
            self.ampN = 0
            self.amp0halfPNreal = delta / 3
            self.amp0halfPNimag = 0
            self.amp1PNreal = -1 / 2 * chia - (chis * delta) / 2
            self.amp1PNimag = 0
            self.amp1halfPNreal = (-17 * delta) / 84 + (5 * delta * eta) / 21
            self.amp1halfPNimag = 0
            self.amp2PNreal = (delta * np.pi) / 3 - (43 * delta * Sc) / 21 - (79 * Sigmac) / 42 + (139 * eta * Sigmac) / 42
            self.amp2PNimag = -1 / 6 * delta - (delta * np.log(16)) / 6
            self.amp2halfPNreal = (-43 * delta) / 378 - (509 * delta * eta) / 378 + (79 * delta * eta2) / 504
            self.amp2halfPNimag = 0
            self.amp3PNreal = (-17 * delta * np.pi) / 84 + (delta * eta * np.pi) / 14
            self.amp3PNimag = (17 * delta) / 168 - (353 * delta * eta) / 84 + (17 * delta * np.log(16)) / 168 - (delta * eta * np.log(4096)) / 84
            self.amp3halfPNreal = 0
            self.amp3halfPNimag = 0
            self.amplog = 0
        elif self._pWF.mode == 33:
            self.ampN = 0
            self.amp0halfPNreal = (3 * np.sqrt(15 / 14) * delta) / 4
            self.amp0halfPNimag = 0
            self.amp1PNreal = 0
            self.amp1PNimag = 0
            self.amp1halfPNreal = -3 * np.sqrt(15 / 14) * delta + (3 * np.sqrt(15 / 14) * delta * eta) / 2
            self.amp1halfPNimag = 0
            self.amp2PNreal = (
                (9 * np.sqrt(15 / 14) * delta * np.pi) / 4
                - (3 * np.sqrt(105 / 2) * delta * Sc) / 8
                - (9 * np.sqrt(15 / 14) * Sigmac) / 8
                + (27 * np.sqrt(15 / 14) * eta * Sigmac) / 8
            )
            self.amp2PNimag = (-9 * np.sqrt(21 / 10) * delta) / 4 + (9 * np.sqrt(15 / 14) * delta * np.log(3 / 2)) / 2
            self.amp2halfPNreal = (
                (369 * np.sqrt(3 / 70) * delta) / 88 - (919 * np.sqrt(3 / 70) * delta * eta) / 22 + (887 * np.sqrt(3 / 70) * delta * eta2) / 88
            )
            self.amp2halfPNimag = 0
            self.amp3PNreal = 0
            self.amp3PNimag = 0
            self.amp3halfPNreal = 0
            self.amp3halfPNimag = 0
            self.amplog = 0.0
        elif self._pWF.mode == 44:
            self.ampN = 0
            self.amp0halfPNreal = 0
            self.amp0halfPNimag = 0
            self.amp1PNreal = (8 * np.sqrt(5 / 7)) / 9 - (8 * np.sqrt(5 / 7) * eta) / 3
            self.amp1PNimag = 0
            self.amp1halfPNreal = 0
            self.amp1halfPNimag = 0
            self.amp2PNreal = -2372 / (99 * np.sqrt(35)) + (5092 * np.sqrt(5 / 7) * eta) / 297 - (100 * np.sqrt(35) * eta2) / 99
            self.amp2PNimag = 0
            self.amp2halfPNreal = (32 * np.sqrt(5 / 7) * np.pi) / 9 - (32 * np.sqrt(5 / 7) * eta * np.pi) / 3
            self.amp2halfPNimag = (
                (-16 * np.sqrt(7 / 5)) / 3
                + (1193 * eta) / (9 * np.sqrt(35))
                + (64 * np.sqrt(5 / 7) * np.log(2)) / 9
                - (64 * np.sqrt(5 / 7) * eta * np.log(2)) / 3
            )
            self.amp3PNreal = (
                1068671 / (45045 * np.sqrt(35))
                - (1088119 * eta) / (6435 * np.sqrt(35))
                + (293758 * eta2) / (1053 * np.sqrt(35))
                - (226097 * eta3) / (3861 * np.sqrt(35))
            )
            self.amp3PNimag = 0
            self.amp3halfPNreal = 0
            self.amp3halfPNimag = 0
            self.amplog = 0.0
        elif self._pWF.mode == 55:
            self.ampN = 0
            self.amp0halfPNreal = 0
            self.amp0halfPNimag = 0
            self.amp1PNreal = 0
            self.amp1PNimag = 0
            self.amp1halfPNreal = (625 * delta) / (96 * np.sqrt(66)) - (625 * delta * eta) / (48 * np.sqrt(66))
            self.amp1halfPNimag = 0
            self.amp2PNreal = 0
            self.amp2PNimag = 0
            self.amp2halfPNreal = (
                (-164375 * delta) / (3744 * np.sqrt(66)) + (26875 * delta * eta) / (234 * np.sqrt(66)) - (2500 * np.sqrt(2 / 33) * delta * eta2) / 117
            )
            self.amp2halfPNimag = 0
            self.amp3PNreal = (3125 * delta * np.pi) / (96 * np.sqrt(66)) - (3125 * delta * eta * np.pi) / (48 * np.sqrt(66))
            self.amp3PNimag = (
                (-113125 * delta) / (1344 * np.sqrt(66))
                + (17639 * delta * eta) / (80 * np.sqrt(66))
                + (3125 * delta * np.log(5 / 2)) / (48 * np.sqrt(66))
                - (3125 * delta * eta * np.log(5 / 2)) / (24 * np.sqrt(66))
            )
            self.amp3halfPNreal = 0
            self.amp3halfPNimag = 0
            self.amplog = 0.0
        self.pn_real_coeffs = np.array(
            [
                self.ampN,
                self.amp0halfPNreal,
                self.amp1PNreal,
                self.amp1halfPNreal,
                self.amp2PNreal,
                self.amp2halfPNreal,
                self.amp3PNreal,
                self.amp3halfPNreal,
                self.amplog,
            ]
        )
        self.pn_imag_coeffs = np.array(
            [self.amp0halfPNimag, self.amp1PNimag, self.amp1halfPNimag, self.amp2PNimag, self.amp2halfPNimag, self.amp3PNimag, self.amp3halfPNimag]
        )

    def _set_inspiral_collocation_points(self):
        """
        Define inspiral collocation points.
        Set times (-2000, -250, -150)M and read parameter space fits.
        Fits are for the full strain amplitude without any rescaling.
        """

        tinsppoints = np.array([-2000, -250, -150])
        ncoll_points = len(tinsppoints)
        ampInspCP = np.zeros(ncoll_points)
        for idx in range(ncoll_points):
            ampInspCP[idx] = IMRPhenomT_Inspiral_Amp_CP(self._pWF, 1 + idx)

        self.tinsp1, self.tinsp2, self.tinsp3 = tinsppoints
        self.ampInspCP1, self.ampInspCP2, self.ampInspCP3 = ampInspCP
        self.inspiral_collocation_points = np.vstack((tinsppoints, ampInspCP)).T

    def _set_inspiral_coefficients(self):
        """
        Compute coefficients of pseudo-PN terms by solving a system with collocation points.

        A c = B
        A is a matrix with the values of the powers of x at the times of the collocation points.
        B is a vector with the values of the collocation points: (collocation point fit - pn_ansatz) / fac0 / x
        c is the solution vector for the free coefficients.

        For 3 free coefficients the system is:
        c1 x1^4 + c2 x1^5 + c3 x1^6 = b1
        c1 x2^4 + c2 x2^5 + c3 x2^6 = b2
        c1 x3^4 + c2 x3^5 + c3 x3^6 = b3
        """

        # 3 coefficients to be computed
        self.inspC1 = 0
        self.inspC2 = 0
        self.inspC3 = 0
        self.pseudo_pn_coeffs = np.zeros(3)

        # Define system Ax = B. A is a matrix, x is the solution vector and B is the vector with indepent terms
        ncoll_points = len(self.inspiral_collocation_points)
        matrix = np.zeros((ncoll_points, ncoll_points))
        B = np.zeros(ncoll_points)

        # Define system matrix coefficients
        for idx in range(ncoll_points):
            time = self.inspiral_collocation_points[idx, 0]
            omega = self._pPhase.imr_omega(time)
            xx = np.power(0.5 * omega, 2.0 / 3)
            xxhalf = np.sqrt(xx)
            xx4 = xx * xx * xx * xx
            ampoffset = np.real(numba_inspiral_ansatz_amplitude(xx, self.fac0, self.pn_real_coeffs, self.pn_imag_coeffs, self.pseudo_pn_coeffs))
            B[idx] = (1 / self.fac0 / xx) * (self.inspiral_collocation_points[idx, 1] - ampoffset)

            xx_power = xx4
            for jdx in range(ncoll_points):
                matrix[idx, jdx] = xx_power
                xx_power *= xxhalf

        # Solve linear system
        solution = np.linalg.solve(matrix, B)
        self.inspC1, self.inspC2, self.inspC3 = solution
        self.pseudo_pn_coeffs = solution

    def _set_ringdown_coefficients(self):
        """
        Set coefficients for amplitude ringdown ansatz
        """
        self.alpha1RD = 2 * np.pi * self._pWF.fdamp
        self.alpha2RD = 2 * np.pi * self._pWF.fdampn2
        self.alpha21RD = 0.5 * (self.alpha2RD - self.alpha1RD)

        self.alpha1RD_prec = 2 * np.pi * self._pWF.fdamp_prec
        self.alpha2RD_prec = 2 * np.pi * self._pWF.fdampn2_prec
        self.alpha21RD_prec = 0.5 * (self.alpha2RD_prec - self.alpha1RD_prec)

        self.ampPeak = IMRPhenomT_PeakAmp(self._pWF)
        self.c3 = IMRPhenomT_Ringdown_Amp_C3(self._pWF)
        self.c2 = self.alpha21RD
        self.c2_prec = self.alpha21RD_prec

        coshc3 = np.cosh(self.c3)
        tanhc3 = np.tanh(self.c3)

        if self.c2 > np.abs(0.5 * self.alpha1RD / tanhc3):
            self.c2 = -0.5 * self.alpha1RD / tanhc3
        if self.c2_prec > np.abs(0.5 * self.alpha1RD_prec / tanhc3):
            self.c2_prec = -0.5 * self.alpha1RD_prec / tanhc3

        self.c1 = self.ampPeak * self.alpha1RD * coshc3 * coshc3 / self.c2
        self.c4 = self.ampPeak - self.c1 * tanhc3
        self.c1_prec = self.ampPeak * self.alpha1RD_prec * coshc3 * coshc3 / self.c2_prec
        self.c4_prec = self.ampPeak - self.c1_prec * tanhc3

    def _set_intermediate_coefficients(self):
        """
        Compute coefficients for amplitude intermediate ansatz by solving a system with collocation points.
        """

        # Set system
        matrix = np.zeros((4, 4))
        B = np.zeros(4)

        ampinsp_cplx = self.inspiral_ansatz_amplitude(self.inspiral_cut)
        ampinsp = ampinsp_cplx

        ampinsp = np.copysign(np.abs(ampinsp), np.real(ampinsp))
        self.ampinsp = ampinsp

        phi = self.alpha1RD * (self.inspiral_cut - self.tshift)
        phi2 = 2 * phi

        sech1 = 1 / np.cosh(phi)
        sech2 = 1 / np.cosh(phi2)

        matrix[0, 0] = 1
        matrix[0, 1] = sech1
        matrix[0, 2] = np.power(sech2, 1 / 7)
        matrix[0, 3] = (self.inspiral_cut - self.tshift) * (self.inspiral_cut - self.tshift)
        B[0] = ampinsp

        self.ampMergerCP1 = IMRPhenomT_Intermediate_Amp_CP1(self._pWF)
        self.tcpMerger = -25.0

        phib = self.alpha1RD * (self.tcpMerger - self.tshift)
        sech1b = 1 / np.cosh(phib)
        sech2b = 1 / np.cosh(2 * phib)

        matrix[1, 0] = 1
        matrix[1, 1] = sech1b
        matrix[1, 2] = np.power(sech2b, 1 / 7)
        matrix[1, 3] = (self.tcpMerger - self.tshift) * (self.tcpMerger - self.tshift)
        B[1] = self.ampMergerCP1

        matrix[2, 0] = 1
        matrix[2, 1] = 1
        matrix[2, 2] = 1
        matrix[2, 3] = 0
        B[2] = self.ampPeak

        amp2 = ampinsp_cplx
        dampMECO = np.copysign(1.0, np.real(amp2)) * self._der_complex_amp_orientation(self.inspiral_cut)
        self.dampMECO = dampMECO

        tanh = np.tanh(phi)
        sinh = np.sinh(phi2)

        aux1 = -self.alpha1RD * sech1 * tanh
        aux2 = (-2 / 7) * self.alpha1RD * sinh * np.power(sech2, 8 / 7)
        aux3 = 2 * (self.inspiral_cut - self.tshift)

        matrix[3, 0] = 0
        matrix[3, 1] = aux1
        matrix[3, 2] = aux2
        matrix[3, 3] = aux3
        B[3] = dampMECO

        # Solve linear system
        solution = np.linalg.solve(matrix, B)
        self.mergerC1, self.mergerC2, self.mergerC3, self.mergerC4 = solution

        self.intermediate_collocation_points = np.array(
            [[self.inspiral_cut, ampinsp], [self.tcpMerger, self.ampMergerCP1], [0, self.ampPeak], [self.inspiral_cut, dampMECO]]
        )

        self.omegaCutPNAMP = 0 if self._pWF.mode == 22 else -np.real(self._der_complex_amp_orientation(self.inspiral_cut, return_phase=True))
        if self._pWF.mode == 22:
            self.phiCutPNAMP = 0
        else:
            amp2 = self.inspiral_ansatz_amplitude(self.inspiral_cut)
            self.phiCutPNAMP = np.arctan2(np.imag(amp2), np.real(amp2))

        if np.copysign(1, np.real(amp2)) == -1:
            self.phiCutPNAMP += np.pi

    def _der_complex_amp_orientation(self, time, return_phase=False):
        """
        Compute derivative of complex inspiral amplitude.

        Can return the derivative of the absolute value or of the phase.

        Derivation in `Mathematica <https://gitlab.com/imrphenom-dev/reviews/qc-phenomt/-/blob/main/theory_notebooks/AnalyticalDerivatives.nb>`_.

        Parameters
        ----------
        time: float or 1D ndarray
            where to evaluate the derivative
        return_phase: bool
            - ``True``: return derivative of the phase of the complex amplitude.
            - ``False``: return derivative of the absolutie value

        Returns
        -------
        float
            Derivative complex amplitude.
        """

        omega = self._pPhase.imr_omega(time)
        x = np.power(omega * 0.5, 2 / 3)

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
            self.ampN
            + self.amp0halfPNreal * xhalf
            + self.amp1PNreal * x
            + self.amp1halfPNreal * x1half
            + self.amp2PNreal * x2
            + self.amp2halfPNreal * x2half
            + self.amp3PNreal * x3
            + self.amp3halfPNreal * x3half
            + self.amplog * np.log(16 * x) * x3
            + self.inspC1 * x4
            + self.inspC2 * x4half
            + self.inspC3 * x5
        )
        ampimag = (
            self.amp0halfPNimag * xhalf
            + self.amp1PNimag * x
            + self.amp1halfPNimag * x1half
            + self.amp2PNimag * x2
            + self.amp2halfPNimag * x2half
            + self.amp3PNimag * x3
            + self.amp3halfPNimag * x3half
        )

        dampreal = (
            0.5 * self.amp0halfPNreal / xhalf
            + self.amp1PNreal
            + 1.5 * self.amp1halfPNreal * xhalf
            + 2 * self.amp2PNreal * x
            + 2.5 * self.amp2halfPNreal * x1half
            + 3 * self.amp3PNreal * x2
            + 3.5 * self.amp3halfPNreal * x2half
            + self.amplog * x2 * (1 + 3 * np.log(16 * x))
            + 4 * self.inspC1 * x3
            + 4.5 * self.inspC2 * x3half
            + 5 * self.inspC3 * x4
        )
        dampimag = (
            0.5 * self.amp0halfPNimag / xhalf
            + self.amp1PNimag
            + 1.5 * self.amp1halfPNimag * xhalf
            + 2 * self.amp2PNimag * x
            + 2.5 * self.amp2halfPNimag * x1half
            + 3 * self.amp3PNimag * x2
            + 3.5 * self.amp3halfPNimag * x2half
        )

        der_x_per_omega = np.cbrt(2 / omega) / 3
        if time < self._pPhase.inspiral_cut:
            der_omega_per_t = numba_inspiral_ansatz_domega(
                time, self._pWF.eta, self._pPhase.omega_pn_coefficients, self._pPhase.omega_pseudo_pn_coefficients
            )
        else:
            arcsinh = np.arcsinh(self._pPhase.alpha1RD * time)
            der_omega_per_t = (
                -self._pPhase.omegaRING
                / np.sqrt(1 + (self._pPhase.alpha1RD * time) ** 2)
                * (
                    self._pPhase.domegaPeak
                    + self._pPhase.alpha1RD
                    * (
                        2 * self._pPhase.omegaMergerC1 * arcsinh
                        + 3 * self._pPhase.omegaMergerC2 * arcsinh * arcsinh
                        + 4 * self._pPhase.omegaMergerC3 * arcsinh**3
                    )
                )
            )

        amp = np.abs(ampreal + 1j * ampimag)

        if return_phase:
            return (dampimag * ampreal - dampreal * ampimag) / (amp * amp) * der_x_per_omega * der_omega_per_t

        else:
            return self.fac0 * (ampreal * (dampreal * x + ampreal) + ampimag * (dampimag * x + ampimag)) / amp * der_x_per_omega * der_omega_per_t

    ###############################
    #      Evaluation Methods     #
    ###############################
    # Methods for the ansatze to be evaluated in a time array

    def inspiral_ansatz_amplitude(self, times, cache=None):
        """
        Inspiral ansatz amplitude.
        PN augmented with 3 pseudo-PN terms. Eq. 14 :cite:`phenomthm`.

        The values for x can be read from cache for the subdominant harmonics.

        Parameters
        ----------
        times: float or 1D ndarray
            Times in NR units where to evaluate the ansatz
        cache: Cache
            Cache object storing x_insp for the subdominant modes

        Returns
        -------
        float or 1D ndarray
            Inspiral amplitude
        """

        # cache is only used when evaluating in time arrays, not in single values
        # cache stores the array for x computed first for the 22 mode
        if cache is not None:
            if len(times) != len(cache.x_insp):
                raise RuntimeError(f"Inconsistent lengths of times and cache_insp {len(times)}!={len(cache.x_insp)}")
            x = cache.x_insp

        # Compute omega and x if cache is not used
        else:
            omega = self._pPhase.imr_omega(times)
            x = self.xp.cbrt((omega * 0.5) ** 2)
            # The evaluation in the array should only be done for the 22 mode and then be recycled
            if self._pWF.mode != 22 and not np.isscalar(times):
                logger.warning(f"omega should only be computed once for the 22 mode, this is {self._pWF.mode}")

            # These are saved in the cache when calling PhenomT.compute_hlm()
            if hasattr(times, "__len__"):
                self.x_insp = x

        # Single value
        if np.isscalar(times):
            x = np.cbrt((omega * 0.5) ** 2)
            return numba_inspiral_ansatz_amplitude(x, self.fac0, self.pn_real_coeffs, self.pn_imag_coeffs, self.pseudo_pn_coeffs)

        # Array of values
        else:
            if self._pWF.numba_ansatze:
                return numba_inspiral_ansatz_amplitude_array(x, self.fac0, self.pn_real_coeffs, self.pn_imag_coeffs, self.pseudo_pn_coeffs)
            else:
                xhalf = self.xp.sqrt(x)
                x1half = x * xhalf
                x2 = x * x
                x2half = x2 * xhalf
                x3 = x2 * x
                x3half = x3 * xhalf
                x4 = x2 * x2
                x4half = x4 * xhalf
                x5 = x3 * x2
                ampreal = (
                    self.ampN
                    + self.amp0halfPNreal * xhalf
                    + self.amp1PNreal * x
                    + self.amp1halfPNreal * x1half
                    + self.amp2PNreal * x2
                    + self.amp2halfPNreal * x2half
                    + self.amp3PNreal * x3
                    + self.amp3halfPNreal * x3half
                    + self.amplog * self.xp.log(16 * x) * x3
                )
                ampimag = (
                    self.amp0halfPNimag * xhalf
                    + self.amp1PNimag * x
                    + self.amp1halfPNimag * x1half
                    + self.amp2PNimag * x2
                    + self.amp2halfPNimag * x2half
                    + self.amp3PNimag * x3
                    + self.amp3halfPNimag * x3half
                )
                ampreal += self.inspC1 * x4 + self.inspC2 * x4half + self.inspC3 * x5
                return self.fac0 * x * (ampreal + 1j * ampimag)

    def intermediate_ansatz_amplitude(self, times):
        """
        Intermediate ansatz amplitude.

        Eq. 30 :cite:`phenomthm`.

        Parameters
        ----------
        times: float or 1D ndarray
            Times in NR units where to evaluate the ansatz.

        Returns
        -------
        float or 1D ndarray
            Intermediate amplitude
        """

        # Single value
        if np.isscalar(times):
            return numba_intermediate_ansatz_amplitude(times, self.alpha1RD, self.mergerC1, self.mergerC2, self.mergerC3, self.mergerC4, self.tshift)

        # Array of values
        else:
            if self._pWF.numba_ansatze:
                return numba_intermediate_ansatz_amplitude_array(
                    times, self.alpha1RD, self.mergerC1, self.mergerC2, self.mergerC3, self.mergerC4, self.tshift
                )
            else:
                sech1 = 1 / self.xp.cosh(self.alpha1RD * (times - self.tshift))
                sech2 = 1 / self.xp.cosh(2 * self.alpha1RD * (times - self.tshift))
                return (
                    self.mergerC1
                    + self.mergerC2 * sech1
                    + self.mergerC3 * self.xp.power(sech2, 1 / 7)
                    + self.mergerC4 * (times - self.tshift) * (times - self.tshift)
                )

    def ringdown_ansatz_amplitude(self, times):
        """
        Ringdown ansatz amplitude.

        Eq. 26 :cite:`phenomthm` (the second line in the paper misses the :math:`e^{\\alpha t}` term).

        Parameters
        ----------
        times: float or 1D ndarray
            Times in NR units where to evaluate the ansatz.

        Returns
        -------
        float or 1D ndarray
            Ringdown amplitude.
        """

        # Single value
        if np.isscalar(times):
            return numba_ringdown_ansatz_amplitude(times, self.c1_prec, self.c2_prec, self.c3, self.c4_prec, self.alpha1RD_prec, self.tshift)

        # Array of values
        else:
            if self._pWF.numba_ansatze:
                return numba_ringdown_ansatz_amplitude_array(
                    times, self.c1_prec, self.c2_prec, self.c3, self.c4_prec, self.alpha1RD_prec, self.tshift
                )
            else:
                tanh = self.xp.tanh(self.c2_prec * (times - self.tshift) + self.c3)
                expAlpha = self.xp.exp(-self.alpha1RD_prec * (times - self.tshift))
                return expAlpha * (self.c1_prec * tanh + self.c4_prec)

    def imr_amplitude(self, times, cache=None):
        """
        Amplitude function for full IMR region.
        Piecewise of inspiral, intermediate and ringdown regions.

        Parameters
        ----------
        times: float or 1D ndarray
            Times in NR units where to evaluate the ansatz
        cache: Cache
            Cache object storing x_insp for the subdominant modes

        Return
        ------
        float or 1Darray
            IMR amplitude for one harmonic.
        """

        # Single vlue
        if np.isscalar(times):
            if times < self.inspiral_cut:
                return self.inspiral_ansatz_amplitude(times)
            elif times >= self.ringdown_cut:
                return self.ringdown_ansatz_amplitude(times)
            else:
                return self.intermediate_ansatz_amplitude(times)

        # Time array
        out = self.xp.empty(len(times), dtype=self.xp.cdouble)

        insp_mask = times < self.inspiral_cut
        inter_mask = (times >= self.inspiral_cut) & (times < self.ringdown_cut)
        ring_mask = times >= self.ringdown_cut

        out[insp_mask] = self.inspiral_ansatz_amplitude(times[insp_mask], cache=cache)
        out[inter_mask] = self.intermediate_ansatz_amplitude(times[inter_mask])
        out[ring_mask] = self.ringdown_ansatz_amplitude(times[ring_mask])

        return out


class pPhase:
    """
    Class for computing omega and phase coefficients and define the ansatze.

    Parameters
    ----------
    pWF: pWF
        pWF structure with waveform parameters
    pPhase22: pPhase
        pPhase object for the 22 mode to be used for the higher modes.
    omegaCutPNAMP: float
        Omega contribution from complex amplitude at transtion time ``pAmp.inspiral_cut``.
    phiCutPNAMP: float
        Phase contribution from complex amplitude at transtion time ``pAmp.inspiral_cut``.
    """

    def __init__(self, pwf, pPhase22=None, omegaCutPNAMP=0, phiCutPNAMP=0):
        self.xp = cp if pwf.cuda is True else np
        self._pWF = pwf
        self._set_powers_of_5()
        self._set_inspiral_cut()
        self._set_ringdown_cut()
        self.pPhase22 = pPhase22
        self.omegaCutPNAMP = omegaCutPNAMP
        self.phiCutPNAMP = phiCutPNAMP
        self._set_offsets()
        self._set_pn_coefficients()
        self._set_inspiral_collocation_points()
        self._set_inspiral_coefficients()
        self._set_ringdown_coefficients()
        self._set_intermediate_coefficients()
        self._set_phase_continuity()

        # Set tmin
        if hasattr(self._pWF, "tmin") is False:
            self._pWF.tmin = self._get_time_of_freq(self._pWF.Mfmin)
            self._pWF.tmin_original = self._pWF.tmin
        if self._pWF.tmin > 0:
            raise ValueError(f"tmin = {self._pWF.tmin:.2f} > 0 invalid. Try lowering f_min.")

        # Set wf length
        if hasattr(self._pWF, "length") is False:
            self._set_wf_length()

        # Set tref
        if hasattr(self._pWF, "tref") is False:
            if self._pWF.Mfmin == self._pWF.Mfref:
                self._pWF.tref = self._pWF.tmin_original
            else:
                self._pWF.tref = self._get_time_of_freq(self._pWF.Mfref)
        if self._pWF.tref > 0:
            raise ValueError(f"tref = {self._pWF.tref:.2f} > 0 invalid. Try lowering f_ref.")

        if self._pWF.mode == 22:
            self._pWF.omega_inspiral_cut = self.imr_omega(self.inspiral_cut)

        if self._pWF.mode == 22:
            self.phiref0 = self.imr_phase(self._pWF.tref)
        else:
            self.phiref0 = self.pPhase22.phiref0

    # Initialization methods
    def _set_powers_of_5(self):
        """
        Set useful powers of 5 for phase_inspiral_ansatz. Array stored in self.powers_of_5
        """

        base = np.power(5, 1 / 8)
        base2 = base * base
        base3 = base * base2
        base4 = base * base3
        base5 = base * base4
        base6 = base * base5
        base7 = base * base6
        self.powers_of_5 = np.array([1, base, base2, base3, base4, base5, base6, base7])

    def _set_inspiral_cut(self):
        """
        Transition time between inspiral and intermediate regions
        For the 22= -5/(eta * 0.81^8). For HM = -150.0
        """

        self.tCut = self.inspiral_cut = -26.982976386771437 / self._pWF.eta if self._pWF.mode == 22 else -150.0

    def _set_ringdown_cut(self):
        """
        Transition time between intermediate and ringdown regions.
        Set to zero (peak time of 22).
        """

        self.ringdown_cut = 0

    def _set_offsets(self):
        """
        The PN amplitude coefficients in pAmp._set_pn_coefficients have been multiplied by a factor so that the real part is dominant and positive, approximating the absolute value.
        The correct complex amplitudes are put back by accordingly correcting the phase. See Eq. 13 in arxiv:2012.11923

        E.g.: the complete 21 complex amplitude has a global factor with I. But the PN amplitude coefficient does not have it. An equivalent multiplication by I is achieved by adding pi/2 to the phase.
        """

        if self._pWF.mode == 22:
            self.phoff = 0
        elif self._pWF.mode == 21:
            self.phoff = np.pi * 0.5
        elif self._pWF.mode == 33:
            self.phoff = -np.pi * 0.5
        elif self._pWF.mode == 44:
            self.phoff = np.pi
        elif self._pWF.mode == 55:
            self.phoff = np.pi * 0.5
        elif self._pWF.mode == 20:
            self.phoff = 0
        else:
            raise NotImplementedError(f"Mode {self._pWF.mode} not supported")

    def _set_pn_coefficients(self):
        """
        Omega PN coefficients for TaylorT3.

        Eqs. A5 :cite:`phenomt`. Paper misses the term eta3 235925 / 1769472 at 3PN order.

        Transformation to python code in `Mathematica <https://gitlab.com/imrphenom-dev/reviews/qc-phenomt/-/blob/main/theory_notebooks/PNCoefficients.nb>`__.
        """

        eta, chi1, chi2, delta = [self._pWF.eta, self._pWF.s1z, self._pWF.s2z, self._pWF.delta]
        m1 = self._pWF.m1
        m2 = self._pWF.m2

        eta2 = eta * eta
        eta3 = eta * eta2

        chi12 = chi1 * chi1
        chi22 = chi2 * chi2
        chi23 = chi2 * chi22

        self.omega1PN = 743 / 2688 + (11 * eta) / 32
        self.omega1halfPN = (-19 * (chi1 + chi2) * eta) / 80 + (-113 * (-2 * chi1 * m1 - 2 * chi2 * m2) - 96 * np.pi) / 320
        self.omega2PN = (
            ((56975 + 61236 * chi12 - 119448 * chi1 * chi2 + 61236 * chi22) * eta) / 258048
            + (371 * eta2) / 2048
            + (1855099 - 3429216 * chi12 * m1 - 3429216 * chi22 * m2) / 14450688
        )
        self.omega2halfPN = (
            (-17 * (chi1 + chi2) * eta2) / 128
            + (-146597 * (-2 * chi1 * m1 - 2 * chi2 * m2) - 46374 * np.pi) / 129024
            + (eta * (-2 * (chi1 * (1213 - 63 * delta) + chi2 * (1213 + 63 * delta)) + 117 * np.pi)) / 2304
        )
        self.omega3PN = (
            -720817631400877 / 288412611379200
            - (16928263 * chi12) / 137625600
            - (16928263 * chi22) / 137625600
            - (16928263 * chi12 * delta) / 137625600
            + (16928263 * chi22 * delta) / 137625600
            + ((-2318475 + 18767224 * chi12 - 54663952 * chi1 * chi2 + 18767224 * chi22) * eta2) / 137625600
            + (235925 * eta3) / 1769472
            + (107 * np.euler_gamma) / 280
            - (6127 * chi1 * np.pi) / 12800
            - (6127 * chi2 * np.pi) / 12800
            - (6127 * chi1 * delta * np.pi) / 12800
            + (6127 * chi2 * delta * np.pi) / 12800
            + (
                eta
                * (
                    632550449425
                    + 35200873512 * chi12
                    - 28527282000 * chi1 * chi2
                    + 9605339856 * chi12 * delta
                    - 1512 * chi22 * (-23281001 + 6352738 * delta)
                    + 34172264448 * (chi1 + chi2) * np.pi
                    - 22912243200 * np.pi**2
                )
            )
            / 104044953600
            + (53 * np.pi**2) / 200
            + (107 * np.log(2)) / 280
        )
        self.omega3halfPN = (
            (-12029 * (chi1 + chi2) * eta3) / 92160
            + (
                eta2
                * (
                    507654 * chi1 * chi22
                    - 838782 * chi23
                    + chi2 * (-840149 + 507654 * chi12 - 870576 * delta)
                    + chi1 * (-840149 - 838782 * chi12 + 870576 * delta)
                    + 1701228 * np.pi
                )
            )
            / 15482880
            + (
                eta
                * (
                    -1134 * chi23 * (-206917 + 71931 * delta)
                    + chi1 * (-1496368361 - 429508815 * delta + 1134 * chi12 * (206917 + 71931 * delta))
                    - chi2 * (1496368361 - 429508815 * delta + 437064012 * chi12 * m1)
                    - 437064012 * chi1 * chi22 * m2
                    - 144 * (488825 + 923076 * chi12 - 1782648 * chi1 * chi2 + 923076 * chi22) * np.pi
                )
            )
            / 185794560
            + (
                -2 * chi1 * (-6579635551 + 535759434 * chi12) * m1
                + 13159271102 * chi2 * m2
                - 1071518868 * chi23 * m2
                + (-565550067 + 930460608 * chi12 * m1 + 930460608 * chi22 * m2) * np.pi
            )
            / 1300561920
        )

        # Intialize coefficients for pseudo-PN terms
        self.omegaInspC1 = 0
        self.omegaInspC2 = 0
        self.omegaInspC3 = 0
        self.omegaInspC4 = 0
        self.omegaInspC5 = 0
        self.omegaInspC6 = 0

        self.omega_pn_coefficients = np.array([self.omega1PN, self.omega1halfPN, self.omega2PN, self.omega2halfPN, self.omega3PN, self.omega3halfPN])

    def _set_inspiral_collocation_points(self):
        """
        Define the set of collocation points for omega inspiral
        See Eq. 11 :cite:`phenomthm`.
        """

        thetapoints = np.array([0.33, 0.45, 0.55, 0.65, 0.75, 0.82])
        ncoll_points = len(thetapoints)
        omegapoints = np.zeros(ncoll_points)
        self.tt0 = IMRPhenomT_Inspiral_TaylorT3_t0(self._pWF)
        self.tEarly = -5 / (self._pWF.eta * np.power(thetapoints[0], 8))
        thetaini = np.power(self._pWF.eta * (self.tt0 - self.tEarly) / 5, -0.125)
        omegapoints[0] = self.pn_ansatz_omega(thetaini)
        for idx in range(1, ncoll_points):
            omegapoints[idx] = IMRPhenomT_Inspiral_Freq_CP(self._pWF, idx)

        self.inspiral_collocation_points = np.vstack((thetapoints, omegapoints)).T

    def _set_inspiral_coefficients(self):
        """
        Compute the omega pseudo-PN terms coefficients by solving a system of equations with collocation points.
        See Eq. 15 :cite:`phenomthm`.
        """

        # Define system Ax = B. A is a matrix, x is the solution vector and B is the vector with indepent terms
        ncoll_points = len(self.inspiral_collocation_points)
        matrix = np.zeros((ncoll_points, ncoll_points))

        theta = self.inspiral_collocation_points[:, 0]
        theta_power = np.power(theta, 8)

        T3offset = np.array([self.pn_ansatz_omega(theta_i) for theta_i in theta])
        B = 4 / (theta * theta * theta) * (self.inspiral_collocation_points[:, 1] - T3offset)

        for jdx in range(ncoll_points):
            matrix[:, jdx] = theta_power
            theta_power *= theta

        # Solve system
        solution = np.linalg.solve(matrix, B)

        # Assign coefficients
        self.omegaInspC1, self.omegaInspC2, self.omegaInspC3, self.omegaInspC4, self.omegaInspC5, self.omegaInspC6 = solution
        self.omega_pseudo_pn_coefficients = solution

    def _set_ringdown_coefficients(self):
        """
        Coefficients for ringdown ansatz omega.
        See Eq. 25, 27a :cite:`phenomthm`.
        """

        self.omegaRING = 2 * np.pi * self._pWF.fring
        self.alpha1RD = 2 * np.pi * self._pWF.fdamp
        self.omegaRING_prec = 2 * np.pi * self._pWF.fring_prec

        self.omegaPeak = IMRPhenomT_PeakFrequency(self._pWF)

        self.c2 = IMRPhenomT_RD_Freq_D2(self._pWF)
        self.c3 = IMRPhenomT_RD_Freq_D3(self._pWF)
        self.c4 = 0
        self.c1 = (1 + self.c3 + self.c4) * (self.omegaRING - self.omegaPeak) / self.c2 / (self.c3 + 2 * self.c4)
        self.c1_prec = (1 + self.c3 + self.c4) * (self.omegaRING_prec - self.omegaPeak) / self.c2 / (self.c3 + 2 * self.c4)

    def _set_intermediate_coefficients(self):
        """
        Compute coefficients for intermediate ansatz omega by solving a system of equations with collocation points.
        See Eqs. 28, 29, 31 and surroundings :cite:`phenomthm`.
        """

        # Set up collocation points for intermediate region
        if self._pWF.mode == 22:
            self.omegaCut = self.inspiral_ansatz_omega(self.tCut)
            self.tcpMerger = -5 / (self._pWF.eta * np.power(0.95, 8))
        elif self.pPhase22 is not None:
            self.omegaCut = self._pWF.emm / 2.0 * self.pPhase22.imr_omega(self.tCut)
            self.tcpMerger = -25.0
        else:
            raise RuntimeError("Needs pPhase22 for higher modes")

        omegaMergerCP = 1 - IMRPhenomT_Intermediate_Freq_CP1(self._pWF) / self.omegaRING
        omegaCutBar = 1 - (self.omegaCut + self.omegaCutPNAMP) / self.omegaRING
        self.omegaMergerCP = omegaMergerCP
        self.omegaCutBar = omegaCutBar

        if self._pWF.mode == 22:
            self.domegaCut = (
                -numba_inspiral_ansatz_domega(self.tCut, self._pWF.eta, self.omega_pn_coefficients, self.omega_pseudo_pn_coefficients)
                / self.omegaRING
            )
        elif self.pPhase22 is not None:
            if self.tCut < self.pPhase22.tCut:
                self.domegaCut = numba_inspiral_ansatz_domega(
                    self.tCut, self._pWF.eta, self.pPhase22.omega_pn_coefficients, self.pPhase22.omega_pseudo_pn_coefficients
                )
            else:
                arcsinh = np.arcsinh(self.pPhase22.alpha1RD * self.tCut)
                self.domegaCut = (
                    -self.pPhase22.omegaRING
                    / np.sqrt(1 + (self.pPhase22.alpha1RD * self.tCut) ** 2)
                    * (
                        self.pPhase22.domegaPeak
                        + self.pPhase22.alpha1RD
                        * (
                            2 * self.pPhase22.omegaMergerC1 * arcsinh
                            + 3 * self.pPhase22.omegaMergerC2 * arcsinh * arcsinh
                            + 4 * self.pPhase22.omegaMergerC3 * arcsinh**3
                        )
                    )
                )
            self.domegaCut = -self._pWF.emm / 2.0 * self.domegaCut / self.omegaRING
        else:
            raise RuntimeError("Needs pPhase22 for higher modes")

        self.domegaPeak = -numba_ringdown_ansatz_domega(0, self.c1, self.c2, self.c3, self.c4) / self.omegaRING

        # Set up system of equations and solve
        n_coefficients = 3
        matrix = np.zeros((n_coefficients, n_coefficients))
        B = np.zeros(n_coefficients)

        ascut = np.arcsinh(self.alpha1RD * self.tCut)
        ascut2 = ascut * ascut
        ascut3 = ascut * ascut2
        ascut4 = ascut * ascut3

        B[0] = omegaCutBar - (1 - self.omegaPeak / self.omegaRING) - (self.domegaPeak / self.alpha1RD) * ascut
        matrix[0, 0] = ascut2
        matrix[0, 1] = ascut3
        matrix[0, 2] = ascut4

        bascut = np.arcsinh(self.alpha1RD * self.tcpMerger)
        bascut2 = bascut * bascut
        bascut3 = bascut * bascut2
        bascut4 = bascut * bascut3

        B[1] = omegaMergerCP - (1 - self.omegaPeak / self.omegaRING) - (self.domegaPeak / self.alpha1RD) * bascut
        matrix[1, 0] = bascut2
        matrix[1, 1] = bascut3
        matrix[1, 2] = bascut4

        dencut = np.sqrt(1 + self.tCut * self.tCut * self.alpha1RD * self.alpha1RD)

        B[2] = self.domegaCut - self.domegaPeak / dencut
        matrix[2, 0] = 2 * self.alpha1RD * ascut / dencut
        matrix[2, 1] = 3 * self.alpha1RD * ascut2 / dencut
        matrix[2, 2] = 4 * self.alpha1RD * ascut3 / dencut

        # Solve linear system
        solution = np.linalg.solve(matrix, B)
        self.omegaMergerC1, self.omegaMergerC2, self.omegaMergerC3 = solution

    def _set_phase_continuity(self):
        """
        The phase is the integration of the omega ansatz in each region. Setup the constants of integration so that the phase is continuous between regions.

        The intermediate and ringdown regions are shifted respect to the inspiral one.
        """

        self.phOffInsp = 0
        self.phOffMerger = 0
        if self._pWF.mode == 22:
            thetabarini = np.power(self._pWF.eta * (self.tt0 - self.tEarly), -1.0 / 8)
            self.phOffInsp = self.pn_ansatz_phase(thetabarini) - self.inspiral_ansatz_phase(self.tEarly)
            self.phOffMerger = self.inspiral_ansatz_phase(self.tCut) - self.intermediate_ansatz_phase(self.tCut)
        else:
            self.phMECOinsp = self._pWF.emm / 2.0 * self.pPhase22.imr_phase(self.tCut)
            self.phMECOmerger = self.intermediate_ansatz_phase(self.tCut)
            self.phOffMerger = self.phMECOinsp - self.phMECOmerger

        self.phOffRD = self.intermediate_ansatz_phase(0)

    def _get_time_of_freq(self, freq):
        """
        Find the time corresponding to an input frequency by numerically solve using imr_omega.
        """

        # tlow_test could not work if f_min is very low.
        tlow_test = -1e9

        # Use fit from reviews/qc-phent/other_tests/tlow_test.ipynb
        if self._pWF.tlow_fit:
            tlow_test = -0.012 * freq ** (-2.7)

        def time_of_freq(time, freq):
            if time < self.tEarly:
                omega = self.imr_omega(time - self.tt0)
            else:
                omega = self.imr_omega(time)
            return 2 * np.pi * freq - omega

        return brentq(time_of_freq, tlow_test, self._pWF.tEnd, args=(freq), maxiter=1000, rtol=self._pWF.rtol, xtol=self._pWF.atol)

    def _set_wf_length(self):
        """
        Set internal length of the waveform assuming that it is equispaced.
        """

        # The time array is built as tmin + i * dt. If we change fmin, the time array will be different
        # even for the common frequency range, so the same waveform in the same frequency range can be slightly different
        # because it is evaluated at slightly different times.
        # We can avoid that if we generate the array starting from t=0 and filling with i*dt to the left and to the right.
        # Therefore we update tmin so that we have an integer number of dts up to t=0. The original tmin from the solver is store in tmin_original
        if self._pWF.delta_t > 0:
            self._pWF.len_neg = int(np.round(np.abs(self._pWF.tmin / self._pWF.delta_t)))
            self._pWF.len_pos = int(np.round(np.abs(self._pWF.tEnd / self._pWF.delta_t)))
            self._pWF.length = self._pWF.len_pos + self._pWF.len_neg
            self._pWF.tmin = -self._pWF.len_neg * self._pWF.delta_t

    ############################
    #    Evaluation Methods    #
    ############################
    # Methods to be evaluated in a time array after the class has been initialized

    def pn_ansatz_omega(self, theta):
        r"""
        PN ansatz omega, TaylorT3 based.
        Eq. 6b :cite:`phenomthm`.

        Parameters
        ----------
        theta: float or 1D ndarray
            Where to evaluate the ansatz. :math:`\\theta = (-\eta * t / 5)^{-1/8}`.

        Returns
        -------
        float or 1D ndarray
            TaylorT3 omega.
        """

        if np.isscalar(theta):
            return numba_pn_ansatz_omega(theta, self.omega_pn_coefficients)
        else:
            if self._pWF.numba_ansatze:
                return numba_pn_ansatz_omega_array(theta, self.omega_pn_coefficients)
            else:
                theta2 = theta * theta
                theta3 = theta2 * theta
                theta4 = theta2 * theta2
                theta5 = theta3 * theta2
                theta6 = theta3 * theta3
                theta7 = theta4 * theta3
                logterm = 107 * self.xp.log(theta) / 280
                fac = theta3 / 4
                return fac * (
                    1
                    + self.omega1PN * theta2
                    + self.omega1halfPN * theta3
                    + self.omega2PN * theta4
                    + self.omega2halfPN * theta5
                    + self.omega3PN * theta6
                    + logterm * theta6
                    + self.omega3halfPN * theta7
                )

    def inspiral_ansatz_omega(self, times):
        """
        Inspiral ansatz omega
        PN ansatz augmented with 6 pseudo-PN terms.
        Eq. 6b, 7 :cite:`phenomthm`.

        Parameters
        ----------
        times: float or 1D ndarray
            Times in NR units where to evaluate the ansatz

        Returns
        -------
        float or 1D ndarray
            Inspiral omega.
        """

        # Single value always uses numba since it is faster
        if np.isscalar(times):
            return numba_inspiral_ansatz_omega(times, self._pWF.eta, self.omega_pn_coefficients, self.omega_pseudo_pn_coefficients)

        # Array of times. Can use numba in the CPU
        else:
            if self._pWF.numba_ansatze:
                return numba_inspiral_ansatz_omega_array(times, self._pWF.eta, self.omega_pn_coefficients, self.omega_pseudo_pn_coefficients)
            else:
                theta = self.xp.power(-self._pWF.eta * times / 5, -1 / 8)
                taylort3 = self.pn_ansatz_omega(theta)
                theta8 = self.xp.power(theta, 8)
                theta9 = theta8 * theta
                theta10 = theta9 * theta
                theta11 = theta10 * theta
                theta12 = theta11 * theta
                theta13 = theta12 * theta
                fac = theta * theta * theta / 8
                out = (
                    self.omegaInspC1 * theta8
                    + self.omegaInspC2 * theta9
                    + self.omegaInspC3 * theta10
                    + self.omegaInspC4 * theta11
                    + self.omegaInspC5 * theta12
                    + self.omegaInspC6 * theta13
                )
                return taylort3 + 2 * fac * out

    def intermediate_ansatz_omega(self, times):
        """
        Intermediate ansatz omega.
        Eq. 15 :cite:`phenomthm`.

        Parameters
        ----------
        times: float or 1D ndarray
            Times in NR units where to evaluate the ansatz

        Returns
        -------
        float or 1D ndarray
            Intermediate omega.
        """

        # Single value always uses numba
        if np.isscalar(times):
            return numba_intermediate_ansatz_omega(
                times, self.alpha1RD, self.omegaPeak, self.omegaRING, self.domegaPeak, self.omegaMergerC1, self.omegaMergerC2, self.omegaMergerC3
            )

        # Array of times. Can use numba in the CPU
        else:
            if self._pWF.numba_ansatze:
                return numba_intermediate_ansatz_omega_array(
                    times, self.alpha1RD, self.omegaPeak, self.omegaRING, self.domegaPeak, self.omegaMergerC1, self.omegaMergerC2, self.omegaMergerC3
                )
            else:
                x = self.xp.arcsinh(self.alpha1RD * times)
                w = (
                    1
                    - self.omegaPeak / self.omegaRING
                    + x * (self.domegaPeak / self.alpha1RD + x * (self.omegaMergerC1 + x * (self.omegaMergerC2 + x * self.omegaMergerC3)))
                )

                return self.omegaRING * (1 - w)

    def ringdown_ansatz_omega(self, times):
        """
        Ringdown ansatz omega.
        Eq. 25 :cite:`phenomthm`.

        Parameters
        ----------
        times: float or 1D ndarray
            Times in NR units where to evaluate the ansatz

        Returns
        -------
        float or 1D ndarray
            Ringdown omega.
        """

        # Single value always uses numba
        if np.isscalar(times):
            return numba_ringdown_ansatz_omega(times, self.c1, self.c2, self.c3, self.c4, self.omegaRING)

        # Array of times. Can use numba in the CPU
        else:
            if self._pWF.numba_ansatze:
                return numba_ringdown_ansatz_omega_array(times, self.c1, self.c2, self.c3, self.c4, self.omegaRING)
            else:
                expC = self.xp.exp(-self.c2 * times)
                expC2 = expC * expC
                num = -self.c1 * self.c2 * (2 * self.c4 * expC2 + self.c3 * expC)
                den = 1 + self.c4 * expC2 + self.c3 * expC

                return num / den + self.omegaRING

    def imr_omega(self, times, **kwargs):
        """
        Omega function for full IMR region.
        Piecewise of inspiral, intermediate and ringdown regions.

        Parameters
        ----------
        times: float or 1D ndarray
            Times in NR units where to evaluate the ansatz

        Returns
        -------
        float or 1D ndarray
            IMR omega.
        """

        # Single vlue
        if np.isscalar(times):
            if times < self.inspiral_cut:
                return self.inspiral_ansatz_omega(times)
            elif times >= self.ringdown_cut:
                return self.ringdown_ansatz_omega(times)
            else:
                return self.intermediate_ansatz_omega(times)

        # Case for array
        out = self.xp.empty(len(times), dtype=self.xp.double)

        insp_mask = times < self.inspiral_cut
        inter_mask = (times >= self.inspiral_cut) & (times < self.ringdown_cut)
        ring_mask = times >= self.ringdown_cut

        out[insp_mask] = self.inspiral_ansatz_omega(times[insp_mask], **kwargs)
        out[inter_mask] = self.intermediate_ansatz_omega(times[inter_mask])
        out[ring_mask] = self.ringdown_ansatz_omega(times[ring_mask])

        return out

    def pn_ansatz_phase(self, thetabar):
        """
        PN ansatz phase. Integration of omega ansatz.
        Only used to compute one value of thetabar needed for ``_set_phase_continuity``.
        """

        return numba_pn_ansatz_22_phase(thetabar, self._pWF.eta, self.powers_of_5, self.omega_pn_coefficients)

    def inspiral_ansatz_phase(self, times, cache=None):
        """
        Inspiral ansatz phase.
        Integration of omega ansatz.
        For the higher harmonics the 22 phase is rescaled by m/2

        Parameters
        ----------
        times: float or 1D ndarray
            Times in NR units where to evaluate the ansatz
        cache: Cache
            Cache struct storing 22 phase to be used by subdominant harmonics.

        Returns
        -------
        float or 1D ndarray
            Inspiral phase.
        """

        eta = self._pWF.eta

        if self._pWF.mode == 22:
            if np.isscalar(times):
                return numba_inspiral_22_phase(
                    times, eta, self.powers_of_5, self.omega_pn_coefficients, self.omega_pseudo_pn_coefficients, self.phOffInsp
                )
            else:
                if self._pWF.numba_ansatze:
                    return njit_inspiral_22_phase(
                        times, eta, self.powers_of_5, self.omega_pn_coefficients, self.omega_pseudo_pn_coefficients, self.phOffInsp
                    )
                else:
                    thetabar = self.xp.power(-eta * times, -1.0 / 8)
                    thetabar2 = thetabar * thetabar
                    thetabar3 = thetabar * thetabar2
                    thetabar4 = thetabar * thetabar3
                    thetabar5 = thetabar * thetabar4
                    thetabar6 = thetabar * thetabar5
                    thetabar7 = thetabar * thetabar6
                    logmtimes = self.xp.log(-times)
                    log_theta_bar = self.xp.log(np.power(5, 0.125)) - 0.125 * (self.xp.log(eta) + logmtimes)

                    aux = (
                        -(
                            1
                            / self.powers_of_5[5]
                            / (eta * eta)
                            / times
                            / thetabar7
                            * (
                                3 * (-107 + 280 * self.omega3PN) * self.powers_of_5[6]
                                + 321 * log_theta_bar * self.powers_of_5[6]
                                + 420 * self.omega3halfPN * thetabar * self.powers_of_5[7]
                                + 56 * (25 * self.omegaInspC1 + 3 * eta * times) * thetabar2
                                + 1050 * self.omegaInspC2 * self.powers_of_5[1] * thetabar3
                                + 280 * (3 * self.omegaInspC3 + eta * self.omega1PN * times) * self.powers_of_5[2] * thetabar4
                                + 140 * (5 * self.omegaInspC4 + 3 * eta * self.omega1halfPN * times) * self.powers_of_5[3] * thetabar5
                                + 120 * (5 * self.omegaInspC5 + 7 * eta * self.omega2PN * times) * self.powers_of_5[4] * thetabar6
                                + 525 * self.omegaInspC6 * self.powers_of_5[5] * thetabar7
                                + 105 * eta * self.omega2halfPN * times * logmtimes * self.powers_of_5[5] * thetabar7
                            )
                        )
                        / 84.0
                    )

                    return aux + self.phOffInsp

        # Higher Modes
        else:
            # Phase_lm = m/2 phase_22
            if np.isscalar(times) is False and cache is not None:
                aux = cache.imr_22phase[: len(times)]
            else:
                aux = self.pPhase22.imr_phase(times)

            # Rescale 22 phase
            return aux * (self._pWF.emm / 2.0)

    def intermediate_ansatz_phase(self, times):
        """
        Intermediate ansatz phase.
        Integration of omega ansatz.

        Parameters
        ----------
        times: float or 1D ndarray
            Times in NR units where to evaluate the ansatz

        Returns
        -------
        float or 1D ndarray
            Intermediate phase.
        """

        if np.isscalar(times):
            return numba_intermediate_ansatz_phase(
                times,
                self.alpha1RD,
                self.omegaMergerC1,
                self.omegaMergerC2,
                self.omegaMergerC3,
                self.omegaPeak,
                self.domegaPeak,
                self.omegaRING,
                self.phOffMerger,
            )
        else:
            if self._pWF.numba_ansatze:
                return numba_intermediate_ansatz_phase_array(
                    times,
                    self.alpha1RD,
                    self.omegaMergerC1,
                    self.omegaMergerC2,
                    self.omegaMergerC3,
                    self.omegaPeak,
                    self.domegaPeak,
                    self.omegaRING,
                    self.phOffMerger,
                )
            else:
                x = self.xp.arcsinh(self.alpha1RD * times)
                x2 = x * x
                x3 = x * x2
                x4 = x * x3
                term1 = self.xp.sqrt(1 + (self.alpha1RD * self.alpha1RD) * times * times)

                aux = self.omegaRING * times * (
                    1
                    - (
                        2 * self.omegaMergerC1
                        + 24 * self.omegaMergerC3
                        + (6 * self.omegaMergerC2 + self.domegaPeak / self.alpha1RD) * x
                        + (1 - self.omegaPeak / self.omegaRING)
                        + (self.omegaMergerC1 + 12 * self.omegaMergerC3) * x2
                        + self.omegaMergerC2 * x3
                        + self.omegaMergerC3 * x4
                    )
                ) - (self.omegaRING / self.alpha1RD) * term1 * (
                    -self.domegaPeak / self.alpha1RD
                    - 6 * self.omegaMergerC2
                    - x * (2 * self.omegaMergerC1 + 24 * self.omegaMergerC3)
                    - 3 * self.omegaMergerC2 * x2
                    - 4 * self.omegaMergerC3 * x3
                )

                return aux + self.phOffMerger

    def ringdown_ansatz_phase(self, times):
        """
        Ringdown ansatz phase.
        Integration of omega ansatz.

        Parameters
        ----------
        times: float or 1D ndarray
            Times in NR units where to evaluate the ansatz

        Returns
        -------
        float or 1D ndarray
            Ringdown phase.
        """

        if np.isscalar(times):
            return numba_ringdown_ansatz_phase(times, self.c1_prec, self.c2, self.c3, self.c4, self.omegaRING_prec, self.phOffRD)
        else:
            if self._pWF.numba_ansatze:
                return numba_ringdown_ansatz_phase_array(times, self.c1_prec, self.c2, self.c3, self.c4, self.omegaRING_prec, self.phOffRD)
            else:
                expC = self.xp.exp(-self.c2 * times)
                num = 1 + self.c3 * expC + self.c4 * expC * expC
                den = 1 + self.c3 + self.c4
                aux = self.xp.log(num / den)
                return self.c1_prec * aux + self.omegaRING_prec * times + self.phOffRD

    def imr_phase(self, times, cache=None):
        """
        Phase function for full IMR region.
        Piecewise of inspiral, intermediate and ringdown regions.

        Parameters
        ----------
        times: float or 1D ndarray
            Times in NR units where to evaluate the ansatz

        Returns
        -------
        float or 1D ndarray
            IMR phase.
        """

        # Single vlue
        if np.isscalar(times):
            if times < self.inspiral_cut:
                return self.inspiral_ansatz_phase(times)
            elif times >= self.ringdown_cut:
                return self.ringdown_ansatz_phase(times)
            else:
                return self.intermediate_ansatz_phase(times)

        # Case for array
        out = self.xp.empty(len(times), dtype=self.xp.double)

        insp_mask = times < self.inspiral_cut
        inter_mask = (times >= self.inspiral_cut) & (times < self.ringdown_cut)
        ring_mask = times >= self.ringdown_cut

        out[insp_mask] = self.inspiral_ansatz_phase(times[insp_mask], cache=cache)
        out[inter_mask] = self.intermediate_ansatz_phase(times[inter_mask]) - self.phiCutPNAMP
        out[ring_mask] = self.ringdown_ansatz_phase(times[ring_mask]) - self.phiCutPNAMP

        return out
