# Copyright (C) 2023  Cecilio García Quirós
"""
Define pPrec class and useful function for precession
"""

import numpy as np

try:
    import cupy as cp
except ImportError:
    cp = None

from phenomxpy.phenomt.fits import IMRPhenomT_fringfit, IMRPhenomX_FinalSpin2017, IMRPhenomX_PrecessingFinalSpin2017
from phenomxpy.utils import logger

from .msa import MSA
from .nnlo import NNLO
from .numerical import Numerical

LAL_PI = np.pi

from numba import njit, prange


class pPrec:
    r"""
    Class for precessing utilities.

    Parameters
    ----------
    pwf: pWF
        pWF object with waveform arguments

    prec_version: {'numerical', 'msa', 'nnlo'}
        Choose the precessing prescription.

    final_spin_version: int
        Options for computing the final spin (0, 1, 2, 3, 4).

        When ``prec_version`` is 'numerical', ``final_spin_version`` uses 4. 'msa' uses 3. 'nnlo' uses 0.

            - 0: :math:`\bar{\chi}_p = \chi_p`  (Eq. 4.7-4.9 :cite:`phenomxphm`).
            - 1: :math:`\bar{\chi}_p = \chi_{1x}`
            - 2: :math:`\bar{\chi}_p = \chi_\perp` (related to in-plane spin components, Eq. 4.24, 4.28 :cite:`phenomxphm`).
            For the options above, :math:`\bar{\chi}_p` is then plugged into Eq. 4.25 :cite:`phenomxphm` to obtain the final spin.

            - 3: For MSA angles, uses spin averaged quantities (Eq. 4.23, 4.29 :cite:`phenomxphm`).
            - 4: Numerically evolved (this is done outside the pPrec class).

    afinal_prec: float
        Numerical value for the final precessing spin. Skips its internal calculation if not ``None``.

    add_20_mode: bool
        Include 20 mode in co-precessing modes

    numba_rotation: {'default_modes', 'custom_modes'} or bool
        Use numba functions to perform the twisting-up rotation of modes.

            - `'default_modes'` or ``True``: use numba for the default_mode_array defined in phenomt.py
            - `'custom_modes'`: use custom mode_array
            - ``False``: do not use numba.

    store_arrays: bool
        Store internal arrays like evolved LN, S1/2 for numerical angles or Euler angles.

    fall_back_msa_to_nnlo: bool
        Fall back to NNLO angles if MSA initialization fails.

    use_final_spin_sign: bool
        Use sign of final spin from MSA or assume positive.

    rtol, atol: float
        Relative and absolute tolerances for the ODE solver.

    use_closest_time_to_tref: bool
        Use closest point in the time array to tref to define there the initial condition for the ODE solver. It only supports equispaced time arrays.

    v_function : {'interpolant', 'imr_omega'}
        Function for v used in the ODE solver.

            - `'interpolant'`: compute an interpolant of v.
            - `'imr_omega'`: use the pPhase.imr_omega so it is independent of the time array as the interpolant and more accurate.

    cubic_interpolation_for_ode: bool
        The ODE solution is interpolated using CubicSpline and evaluated on the cpu, then transferred to the gpu if needed.
        If False, the interpolation is linear and is done directly on the gpu if requested.

    numba_derivatives: bool
        Use numba functions for the right-hand-side of the ODE solver.

    interpolate: {'ode_solution', 'euler_angles'} or ``None``.
            - `'ode_solution'`: the ODE solution is interpolated from the internal solver points to the requested time array
            - `'euler_angles'`: the Euler angles are interpolated from the internal solver points to the requested time array
            - ``None``: the ODE solution is evaluated in the requested time array

    quaternions_from: {'frame', 'euler_angles'}
        Strategy to compute the quaternions transforming from co-precessing to inertial frame.

            - `'frame'`: use the evolved frame Z=LNhatev, X=E1, Y=ZxX to get the quaternions already satisfying the minimal rotation condition. The evolution of E1 is done so it satisfies minimal rotation condition. Avoid computational cost of Euler angles and loss of accuracy due to the use of cubic splines for gamma integration.
            - `'euler_angles'`: from the evolution of LNhatev, computes Euler angles alpha, cosbeta, numerically integrate gamma according to minimal rotation condition and then transform to quaternions.

    gamma_integration_method: {'piecewise_integral', 'boole', 'antiderivative'}
        Strategy for the integration of gamma following minimal rotation condition.

            - `'piecewise_integral'`: analytical integral in each time interval of the 5th order "spline" resulting from the multiplication of two cubic splines: CS.derivative() * CS.
            - `'boole'`: use Boole's rule, assumes equispaced grid. This is the only one supported for cuda=True and in this case it uses linear interpolation instead of cubic spline.
            - `'antiderivative'`: use .antiderivative() method of CubicSpline. This spline is built after evaluating the alpha.derivative() and cosbeta() CubicSplines. It loses accuracy since higher order from the multiplication of alpha_der * cosbeta are discarded.

    analytical_RD_gamma: bool
        The ringdown attachment for gamma angles has an analytical form in terms of alpha and beta,
        which is used for NNLO and MSA but that was not used for the numerical angles in the lalsuite implementation.

    """

    def __init__(
        self,
        pwf,
        prec_version="numerical",
        final_spin_version=None,
        afinal_prec=None,
        add_20_mode=False,
        numba_rotation="default_modes",
        store_arrays=False,
        **kwargs,
    ):
        # Set options settings
        self.xp = cp if pwf.cuda and cp is not None else np
        self.add_20_mode = add_20_mode
        self._pWF = pwf
        self.numba_rotation = numba_rotation if pwf.cuda is False else False
        self.store_arrays = store_arrays
        self.input_afinal_prec = afinal_prec
        # Set spin quantities
        self.chiL = (1 + pwf.q) * (pwf.chi_eff / pwf.q)
        self.S1 = self._pWF.s1 * self._pWF.m1_2
        self.S2 = self._pWF.s2 * self._pWF.m2_2
        self.chip = self.get_chip()
        self.Sperp = self.chip * self._pWF.m1_2
        self.STot_perp = np.linalg.norm(self.S1[:2] + self.S2[:2])
        self.chiTot_perp = self.STot_perp * self._pWF.M * self._pWF.M / self._pWF.m1_2
        self.SL = pwf.s1z * pwf.m1_2 + pwf.s2z * pwf.m2_2
        self.alphaOff = np.arctan2(self.S1[1] + self.S2[1], self.S1[0] + self.S2[0]) - np.pi
        # Euler angles options
        self.prec_version = prec_version.lower()
        if self.prec_version in ["numerical", "num", "spintaylor", "st"]:
            self.prec_version = "numerical"
        # Set constant sqrt values
        self.set_sqrt()
        # Set quantities at fref
        self.omegaRef = self._pWF.Mfref * 2 * np.pi

        # Add specific methods for each Euler angles prescription: NNLO, MSA, Numerical and initialize coefficients
        # set_angular_momentum_coefficients depends on prec_version so it needs to be evaluated after checking ->
        # if MSA has failed and fallen back to NNLO

        # NNLO angles
        if self.prec_version == "nnlo":
            self._load_from(NNLO)
            self.save_omega = kwargs.get("save_omega", True)
            self.set_angular_momentum_coefficients()
            self.set_initial_quantities()
            self.set_NNLO_angles_coefficients()

        # MSA angles
        elif self.prec_version == "msa":
            self._load_from(MSA)
            self.save_omega = kwargs.get("save_omega", True)
            self.fall_back_msa_to_nnlo = kwargs.get("fall_back_msa_to_nnlo", True)
            try:
                self.Initialize_MSA()
                self.use_final_spin_sign = kwargs.get("use_final_spin_sign", True)
                self.set_angular_momentum_coefficients()
                self.set_initial_quantities()
            except:
                if self.fall_back_msa_to_nnlo is True:
                    logger.warning("Failed initializing MSA, falling back to NNLO.")
                    self.prec_version = "nnlo"
                    self._load_from(NNLO)
                    self.set_angular_momentum_coefficients()
                    self.set_initial_quantities()
                    self.set_NNLO_angles_coefficients()
                else:
                    raise RuntimeError("Failed initializing MSA. To fall back to NNLO set fall_back_msa_to_nnlo=True.")
        # Numerical angles
        elif self.prec_version == "numerical":
            self._load_from(Numerical)
            self.save_omega = False  # save_omega is only used for NNLO and MSA if compute_CPmodes_at_once is True
            self.rtol = kwargs.get("rtol", 1e-12)
            self.atol = kwargs.get("atol", 1e-12)
            self.use_closest_time_to_tref = kwargs.get("use_closest_time_to_tref", False)
            if self.use_closest_time_to_tref and self._pWF.delta_t == 0:
                raise ValueError("use_closest_time_to_tref=True requires equispaced time grids. Set delta_t > 0.")
            self.v_function = kwargs.get("v_function", "interpolant")  # interpolant, imr_omega
            self.cubic_interpolation_for_ode = kwargs.get(
                "cubic_interpolation_for_ode", True
            )  # cuda=True will still run on the cpu. Used only for interpolate=ode_solution
            self.numba_derivatives = kwargs.get("numba_derivatives", True) if pwf.cuda is False else False
            self.interpolate = kwargs.get("interpolate", "ode_solution")  # None, ode_solution, euler_angles
            self.quaternions_from = kwargs.get("quaternions_from", "frame")  # frame, euler_angles
            self.gamma_integration_method = kwargs.get("gamma_integration_method", "piecewise_integral")  # boole, antiderivative, piecewise_integral
            self.analytical_RD_gamma = kwargs.get("analytical_RD_gamma", True)

            if self.quaternions_from == "frame" and self.interpolate == "euler_angles":
                raise ValueError("Cannot use quaternions_from=frame and interpolate=euler_angles at the same time")
            if self._pWF.cuda and self.quaternions_from == "euler_angles" and self.gamma_integration_method != "boole":
                raise ValueError("cuda option for numerical angles only supports gamma_integration_method=boole")
            self.set_angular_momentum_coefficients()
            self.set_initial_quantities()

        # Final spin option. Default to 0 for NNLO, 3 for MSA and 4 for Numerical
        self.final_spin_version = final_spin_version
        if final_spin_version is None:
            self.final_spin_version = 0
            if self.prec_version == "msa":
                self.final_spin_version = 3
            elif self.prec_version == "numerical":
                self.final_spin_version = 4

        # Compute final spin (analytical options)
        if afinal_prec is None:
            self.set_final_spin(self.final_spin_version)
        else:
            self._pWF.afinal_prec = afinal_prec

        # Compute slope for the ringdown attachment
        self.EulerRDslope = self.get_euler_slope(self._pWF.afinal_prec, self._pWF.Mfinal)
        # For final_spin_version=4 these two quantities are recomputed later

        # Compute alpha_ref from initial condition
        LNhat_ref = self.rotate_z(-self.phiJ_Sf, [0, 0, 1])
        LNhat_ref = self.rotate_y(-self.thetaJ_Sf, LNhat_ref)
        LNhat_ref = self.rotate_z(-self.kappa, LNhat_ref)
        self.alpha_ref = self.xp.arctan2(LNhat_ref[1], LNhat_ref[0])

    def _load_from(self, source_class):
        """Add specific methods from an input class (NNLO, MSA, Numerical) to the pPrec class"""

        for attr_name in dir(source_class):
            # Skip special/private attributes
            if attr_name.startswith("_"):
                continue
            # Get attribute
            attr_value = getattr(source_class, attr_name)
            # Check if it is a method and bind it to this instance
            if callable(attr_value):
                setattr(self, attr_name, attr_value.__get__(self, self.__class__))

    def set_initial_quantities(self):
        """Angles and vectors at fref"""

        self.J0x_Sf = self.S1[0] + self.S2[0]
        self.J0y_Sf = self.S1[1] + self.S2[1]
        self.J0z_Sf = self.S1[2] + self.S2[2] + self.LRef
        self.J0 = np.linalg.norm([self.J0x_Sf, self.J0y_Sf, self.J0z_Sf])

        self.thetaJ_Sf = 0 if self.J0 < 1e-10 else np.arccos(self.J0z_Sf / self.J0)

        MAX_TOL_ATAN = 1e-15
        if np.abs(self.J0x_Sf) < MAX_TOL_ATAN and np.abs(self.J0y_Sf) < MAX_TOL_ATAN:
            self.phiJ_Sf = 0
        else:
            self.phiJ_Sf = np.arctan2(self.J0y_Sf, self.J0x_Sf)

        self.Nx_Sf = np.sin(self._pWF.inclination) * np.cos(np.pi / 2 - self._pWF.phi_ref)
        self.Ny_Sf = np.sin(self._pWF.inclination) * np.sin(np.pi / 2 - self._pWF.phi_ref)
        self.Nz_Sf = np.cos(self._pWF.inclination)

        tmp = self.rotate_z(-self.phiJ_Sf, [self.Nx_Sf, self.Ny_Sf, self.Nz_Sf])
        tmp = self.rotate_y(-self.thetaJ_Sf, tmp)

        if np.abs(tmp[1]) < MAX_TOL_ATAN and np.abs(tmp[0]) < MAX_TOL_ATAN:
            self.kappa = 0
        else:
            self.kappa = np.arctan2(tmp[1], tmp[0])

    def set_final_spin(self, final_spin_version):
        r"""
        Set final spin according to the final_spin_version

        - 0: :math:`\bar{\chi}_p = \chi_p`  (Eq. 4.7-4.9 :cite:`phenomxphm`).
        - 1: :math:`\bar{\chi}_p = \chi_{1x}`
        - 2: :math:`\bar{\chi}_p = \chi_\perp` (related to in-plane spin components, Eq. 4.24, 4.28 :cite:`phenomxphm`).
        For the options above, :math:`\bar{\chi}_p` is then plugged into Eq. 4.25 :cite:`phenomxphm` to obtain the final spin.

        - 3: For MSA angles, uses spin averaged quantities (Eq. 4.23, 4.29 :cite:`phenomxphm`).
        - 4: Numerically evolved (this is done outside the pPrec class).
        """

        if final_spin_version == 0:
            self._pWF.afinal_prec = IMRPhenomX_PrecessingFinalSpin2017(self._pWF.eta, self._pWF.s1z, self._pWF.s2z, self.chip)
        elif final_spin_version == 1:
            self._pWF.afinal_prec = IMRPhenomX_PrecessingFinalSpin2017(self._pWF.eta, self._pWF.s1z, self._pWF.s2z, self._pWF.s1[0])
        elif final_spin_version == 2:
            self._pWF.afinal_prec = IMRPhenomX_PrecessingFinalSpin2017(self._pWF.eta, self._pWF.s1z, self._pWF.s2z, self.chiTot_perp)
        elif final_spin_version == 3:
            if getattr(self, "SAv2", 0) == 0:
                # If not MSA version, default to final spin version = 0 FIXME: add logging warning?
                self.set_final_spin(0)
            else:
                M = 1
                self.af_parallel = IMRPhenomX_FinalSpin2017(self._pWF.eta, self._pWF.s1z, self._pWF.s2z)
                Lfinal = M * M * self.af_parallel - self._pWF.s1_dim[2] - self._pWF.s2_dim[2]
                sign = np.copysign(1, self.af_parallel) if self.use_final_spin_sign else 1
                self._pWF.afinal_prec = sign * np.sqrt(self.SAv2 + Lfinal * Lfinal + 2.0 * Lfinal * (self.S1L_pav + self.S2L_pav)) / (M * M)
        return self._pWF.afinal_prec

    def get_chip(self):
        r"""
        Compute :math:`\chi_p`. Originally in Eq.3.3-3.4 :cite:`Schmidt_2015`.
        """

        m1, m2 = [self._pWF.m1, self._pWF.m2]
        s1, s2 = [self._pWF.s1, self._pWF.s2]
        m1_2 = self._pWF.m1_2
        m2_2 = self._pWF.m2_2
        chi1x, chi1y = s1[0:2]
        chi2x, chi2y = s2[0:2]
        S1_perp = (m1_2) * np.sqrt(chi1x * chi1x + chi1y * chi1y)
        S2_perp = (m2_2) * np.sqrt(chi2x * chi2x + chi2y * chi2y)
        A1 = 2.0 + (3.0 * m2) / (2.0 * m1)
        A2 = 2.0 + (3.0 * m1) / (2.0 * m2)
        ASp1 = A1 * S1_perp
        ASp2 = A2 * S2_perp
        num = ASp2 if (ASp2 > ASp1) else ASp1
        den = A2 * m2_2 if (m2 > m1) else A1 * m1_2

        return num / den

    def set_angular_momentum_coefficients(self):
        """
        Set coefficients for the PN angular momenum L.

        Eqs. G10 :cite:`phenomxphm`.

        Angular momemtum at fref. Eq. 4.13 arxiv:2004.06503
        """

        eta, chi1L, chi2L, delta = [self._pWF.eta, self._pWF.s1z, self._pWF.s2z, self._pWF.delta]

        self.L0 = 1.0
        self.L1 = 0.0
        self.L2 = 3.0 / 2.0 + eta / 6.0

        if self.prec_version != "msa":
            self.L3 = (5 * (chi1L * (-2 - 2 * delta + eta) + chi2L * (-2 + 2 * delta + eta))) / 6.0
            self.L5 = (
                -7
                * (chi1L * (72 + delta * (72 - 31 * eta) + eta * (-121 + 2 * eta)) + chi2L * (72 + eta * (-121 + 2 * eta) + delta * (-72 + 31 * eta)))
            ) / 144.0
        else:
            self.L3 = (-7 * (chi1L + chi2L + chi1L * delta - chi2L * delta) + 5 * (chi1L + chi2L) * eta) / 6.0
            self.L5 = (
                -1650 * (chi1L + chi2L + chi1L * delta - chi2L * delta)
                + 1336 * (chi1L + chi2L) * eta
                + 511 * (chi1L - chi2L) * delta * eta
                + 28 * (chi1L + chi2L) * eta * eta
            ) / 600.0

        self.L4 = (81 + (-57 + eta) * eta) / 24.0
        self.L6 = (10935 + eta * (-62001 + eta * (1674 + 7 * eta) + 2214 * LAL_PI * LAL_PI)) / 1296.0
        self.L7 = 0.0
        self.L8 = 0.0

        # This is the log(x) term
        self.L8L = 0.0

        self.LRef = np.float64(self.compute_angular_momentum(np.cbrt(self.omegaRef * 0.5)))

    def compute_angular_momentum(self, v):
        """
        Compute orbital angular momentum up to 4PN approximantion.

        Eq. 4.13 :cite:`phenomxphm`.
        """

        x = v * v
        x2 = x * x
        x3 = x * x2
        x4 = x * x3
        sqx = self.xp.sqrt(x)

        return (
            self._pWF.eta
            / v
            * (
                self.L0
                + self.L1 * sqx
                + self.L2 * x
                + self.L3 * (x * sqx)
                + self.L4 * x2
                + self.L5 * (x2 * sqx)
                + self.L6 * x3
                + self.L7 * (x3 * sqx)
                + self.L8 * x4
                + self.L8L * x4 * self.xp.log(x)
            )
        )

    def set_sqrt(self):
        """
        Set useful values of square roots used in the Wigner-d matrices.
        """

        self.sqrt2 = np.sqrt(2)
        self.sqrt2half = np.sqrt(2.5)
        self.sqrt3 = np.sqrt(3)
        self.sqrt5 = np.sqrt(5)
        self.sqrt6 = np.sqrt(6)
        self.sqrt7 = np.sqrt(7)
        self.sqrt10 = np.sqrt(10)
        self.sqrt14 = np.sqrt(14)
        self.sqrt15 = np.sqrt(15)
        self.sqrt21 = np.sqrt(21)
        self.sqrt30 = np.sqrt(30)
        self.sqrt35 = np.sqrt(35)
        self.sqrt70 = np.sqrt(70)
        self.sqrt210 = np.sqrt(210)

    def WignerdMatrix(self, cosBeta, sign=1, lmax=2, global_rotation=False):
        """
        Compute Wigner-d matrices coefficients from cosbeta.

        Appendix A :cite:`phenomxphm`.

        Used only for L0/Jmodes, not the default CPmodes.

        Coefficients for each l are stored in `self.wignerdLi` with i = {2, 3, 4, 5}.

        global_rotation=True refers to the constant in time rotation from J to L0 frame. This rotation includes all the l=l modes
        """

        # This initialization is needed for the numba rotation when not all the modes are twisted-up
        if np.isscalar(cosBeta):
            self.wignerdL2 = self.xp.zeros((5, 5))
            self.wignerdL3 = self.xp.zeros((7, 7))
            self.wignerdL4 = self.xp.zeros((9, 9))
            self.wignerdL5 = self.xp.zeros((11, 11))
        else:
            self.wignerdL2 = self.xp.zeros((5, 5, len(cosBeta)))
            self.wignerdL3 = self.xp.zeros((7, 7, len(cosBeta)))
            self.wignerdL4 = self.xp.zeros((9, 9, len(cosBeta)))
            self.wignerdL5 = self.xp.zeros((11, 11, len(cosBeta)))

        cBetah = self.xp.sqrt(0.5 * self.xp.abs(1 + cosBeta))  # the abs should be redundant if -1 < cosBeta < 1
        sBetah = sign * self.xp.sqrt(0.5 * self.xp.abs(1 - cosBeta))
        cBetah2 = cBetah * cBetah
        cBetah3 = cBetah * cBetah2
        cBetah4 = cBetah * cBetah3
        sBetah2 = sBetah * sBetah
        sBetah3 = sBetah * sBetah2
        sBetah4 = sBetah * sBetah3

        d22 = self.xp.array([sBetah4, 2.0 * cBetah * sBetah3, self.sqrt6 * sBetah2 * cBetah2, 2.0 * cBetah3 * sBetah, cBetah4])
        d2m2 = self.xp.array([d22[4], -d22[3], d22[2], -d22[1], d22[0]])
        d21 = self.xp.array(
            [
                2.0 * cBetah * sBetah3,
                3.0 * cBetah2 * sBetah2 - sBetah4,
                self.sqrt6 * (cBetah3 * sBetah - cBetah * sBetah3),
                cBetah2 * (cBetah2 - 3.0 * sBetah2),
                -2.0 * cBetah3 * sBetah,
            ]
        )
        d2m1 = self.xp.array([-d21[4], d21[3], -d21[2], d21[1], -d21[0]])

        if global_rotation is True or self.add_20_mode is True:
            C2mS2 = cBetah2 - sBetah2
            d20 = self.xp.array(
                [
                    self.sqrt6 * cBetah2 * sBetah2,
                    self.sqrt6 * cBetah * sBetah * C2mS2,
                    0.25 * (1 + 3 * (-4 * cBetah2 * sBetah2 + C2mS2 * C2mS2)),
                    -self.sqrt6 * cBetah * sBetah * C2mS2,
                    self.sqrt6 * cBetah2 * sBetah2,
                ]
            )
        else:
            d20 = self.xp.zeros(d22.shape)

        self.wignerdL2 = self.xp.array([d2m2, d2m1, d20, d21, d22])

        if lmax >= 3:
            cBetah5 = cBetah * cBetah4
            cBetah6 = cBetah * cBetah5
            sBetah5 = sBetah * sBetah4
            sBetah6 = sBetah * sBetah5

            d33 = self.xp.array(
                [
                    sBetah6,
                    self.sqrt6 * cBetah * sBetah5,
                    self.sqrt15 * cBetah2 * sBetah4,
                    2.0 * self.sqrt5 * cBetah3 * sBetah3,
                    self.sqrt15 * cBetah4 * sBetah2,
                    self.sqrt6 * cBetah5 * sBetah,
                    cBetah6,
                ]
            )
            d3m3 = self.xp.array([d33[6], -d33[5], d33[4], -d33[3], d33[2], -d33[1], d33[0]])

            d32 = self.xp.empty(d33.shape)
            d31 = self.xp.empty(d33.shape)
            d30 = self.xp.empty(d33.shape)
            d3m1 = self.xp.empty(d33.shape)
            d3m2 = self.xp.empty(d33.shape)

            if global_rotation is True:
                sinBeta = sign * self.xp.sqrt(self.xp.abs(1.0 - cosBeta * cosBeta))
                cos2Beta = cosBeta * cosBeta - sinBeta * sinBeta
                cos3Beta = cosBeta * (2.0 * cos2Beta - 1.0)

                d32 = self.xp.array(
                    [
                        self.sqrt6 * cBetah * sBetah5,
                        sBetah4 * (5.0 * cBetah2 - sBetah2),
                        self.sqrt10 * sBetah3 * (2.0 * cBetah3 - cBetah * sBetah2),
                        self.sqrt30 * cBetah2 * (cBetah2 - sBetah2) * sBetah2,
                        self.sqrt10 * cBetah3 * (cBetah2 * sBetah - 2.0 * sBetah3),
                        cBetah4 * (cBetah2 - 5.0 * sBetah2),
                        -self.sqrt6 * cBetah5 * sBetah,
                    ]
                )
                d3m2 = self.xp.array([-d32[6], d32[5], -d32[4], d32[3], -d32[2], d32[1], -d32[0]])

                d31 = self.xp.array(
                    [
                        self.sqrt15 * cBetah2 * sBetah4,
                        self.sqrt2half * cBetah * sBetah3 * (1 + 3.0 * C2mS2),
                        0.125 * sBetah2 * (13.0 + 20.0 * C2mS2 + 15.0 * (C2mS2 * C2mS2 - 4.0 * cBetah2 * sBetah2)),
                        0.25 * self.sqrt3 * cBetah * sBetah * (3.0 + 5.0 * (C2mS2 * C2mS2 - 4.0 * cBetah2 * sBetah2)),
                        0.125 * cBetah2 * (13.0 - 20.0 * C2mS2 + 15.0 * (C2mS2 * C2mS2 - 4.0 * cBetah2 * sBetah2)),
                        -self.sqrt2half * cBetah3 * sBetah * (-1.0 + 3.0 * C2mS2),
                        self.sqrt15 * cBetah4 * sBetah2,
                    ]
                )
                d3m1 = self.xp.array([d31[6], -d31[5], d31[4], -d31[3], d31[2], -d31[1], d31[0]])

                d30 = self.xp.array(
                    [
                        2.0 * self.sqrt5 * cBetah3 * sBetah3,
                        self.sqrt30 * cBetah2 * sBetah2 * C2mS2,
                        0.25 * self.sqrt3 * cBetah * sBetah * (3.0 + 5.0 * (C2mS2 * C2mS2 - 4.0 * cBetah2 * sBetah2)),
                        0.125 * (5.0 * cos3Beta + 3 * C2mS2),
                        -0.25 * self.sqrt3 * cBetah * sBetah * (3.0 + 5.0 * (C2mS2 * C2mS2 - 4.0 * cBetah2 * sBetah2)),
                        self.sqrt30 * cBetah2 * sBetah2 * C2mS2,
                        -2.0 * self.sqrt5 * cBetah3 * sBetah3,
                    ]
                )

            self.wignerdL3 = self.xp.array([d3m3, d3m2, d3m1, d30, d31, d32, d33])

        if lmax >= 4:
            cBetah7 = cBetah * cBetah6
            cBetah8 = cBetah * cBetah7
            sBetah7 = sBetah * sBetah6
            sBetah8 = sBetah * sBetah7

            d44 = self.xp.array(
                [
                    sBetah8,
                    2.0 * self.sqrt2 * cBetah * sBetah7,
                    2.0 * self.sqrt7 * cBetah2 * sBetah6,
                    2.0 * self.sqrt14 * cBetah3 * sBetah5,
                    self.sqrt70 * cBetah4 * sBetah4,
                    2.0 * self.sqrt14 * cBetah5 * sBetah3,
                    2.0 * self.sqrt7 * cBetah6 * sBetah2,
                    2.0 * self.sqrt2 * cBetah7 * sBetah,
                    cBetah8,
                ]
            )
            d4m4 = self.xp.array([d44[8], -d44[7], d44[6], -d44[5], d44[4], -d44[3], d44[2], -d44[1], d44[0]])

            d43 = self.xp.empty(d44.shape)
            d42 = self.xp.empty(d44.shape)
            d41 = self.xp.empty(d44.shape)
            d40 = self.xp.empty(d44.shape)
            d4m1 = self.xp.empty(d44.shape)
            d4m2 = self.xp.empty(d44.shape)
            d4m3 = self.xp.empty(d44.shape)

            if global_rotation is True:
                cos4Beta = self.xp.power(sinBeta, 4) + self.xp.power(cosBeta, 4) - 6.0 * sinBeta * sinBeta * cosBeta * cosBeta

                d43 = self.xp.array(
                    [
                        2 * self.sqrt2 * cBetah * sBetah7,
                        7 * cBetah2 * sBetah6 - sBetah8,
                        self.sqrt14 * (3 * cBetah3 * sBetah5 - cBetah * sBetah7),
                        self.sqrt7 * (5 * cBetah4 * sBetah4 - 3 * cBetah2 * sBetah6),
                        2 * 5.916079783099616 * (cBetah5 * sBetah3 - cBetah3 * sBetah5),
                        self.sqrt7 * (3 * cBetah6 * sBetah2 - 5 * cBetah4 * sBetah4),
                        self.sqrt14 * (cBetah7 * sBetah - 3 * cBetah5 * sBetah3),
                        cBetah8 - 7 * cBetah6 * sBetah2,
                        -2.0 * self.sqrt2 * cBetah7 * sBetah,
                    ]
                )
                d4m3 = self.xp.array([-d43[8], d43[7], -d43[6], d43[5], -d43[4], d43[3], -d43[2], d43[1], -d43[0]])

                d42 = self.xp.array(
                    [
                        2 * self.sqrt7 * cBetah2 * sBetah6,
                        self.sqrt14 * cBetah * sBetah5 * (1.0 + 2.0 * C2mS2),
                        sBetah4 * (1.0 + 7.0 * C2mS2 + 7.0 * C2mS2 * C2mS2),
                        0.5 * self.sqrt2 * cBetah * sBetah3 * (6.0 + 7.0 * cos2Beta + 7.0 * C2mS2),
                        0.5 * self.sqrt2half * cBetah2 * (5.0 + 7.0 * cos2Beta) * sBetah2,
                        0.5 * self.sqrt2 * cBetah3 * sBetah * (6.0 + 7.0 * cos2Beta - 7.0 * C2mS2),
                        cBetah4 * (1.0 - 7.0 * C2mS2 + 7.0 * C2mS2 * C2mS2),
                        -self.sqrt14 * cBetah5 * sBetah * (-1.0 + 2.0 * C2mS2),
                        2 * self.sqrt7 * cBetah6 * sBetah2,
                    ]
                )
                d4m2 = self.xp.array([d42[8], -d42[7], d42[6], -d42[5], d42[4], -d42[3], d42[2], -d42[1], d42[0]])

                d41 = self.xp.array(
                    [
                        2 * self.sqrt14 * cBetah3 * sBetah5,
                        self.sqrt7 * cBetah2 * sBetah4 * (1.0 + 4.0 * C2mS2),
                        0.5 * self.sqrt2 * cBetah * sBetah3 * (6.0 + 7.0 * cos2Beta + 7.0 * C2mS2),
                        0.125 * sBetah2 * (15.0 + 21.0 * cos2Beta + 14.0 * cos3Beta + 30.0 * C2mS2),
                        0.125 * self.sqrt5 * cBetah * sBetah * (7.0 * cos3Beta + 9.0 * C2mS2),
                        0.125 * cBetah2 * (-15.0 + 30 * cosBeta - 21.0 * cos2Beta + 14.0 * cos3Beta),
                        0.5 * self.sqrt2 * cBetah3 * sBetah * (-6.0 - 7.0 * cos2Beta + 7.0 * C2mS2),
                        self.sqrt7 * cBetah4 * sBetah2 * (-1.0 + 4.0 * C2mS2),
                        -2 * self.sqrt14 * cBetah5 * sBetah3,
                    ]
                )
                d4m1 = self.xp.array([-d41[8], d41[7], -d41[6], d41[5], -d41[4], d41[3], -d41[2], d41[1], -d41[0]])

                d40 = self.xp.array(
                    [
                        self.sqrt70 * cBetah4 * sBetah4,
                        2 * self.sqrt35 * cBetah3 * sBetah3 * C2mS2,
                        0.5 * self.sqrt2half * cBetah2 * (5.0 + 7.0 * cos2Beta) * sBetah2,
                        0.125 * self.sqrt5 * cBetah * sBetah * (7.0 * cos3Beta + 9.0 * C2mS2),
                        0.015625 * (9 + 20.0 * cos2Beta + 35.0 * cos4Beta),
                        -0.125 * self.sqrt5 * cBetah * sBetah * (7.0 * cos3Beta + 9.0 * C2mS2),
                        0.5 * self.sqrt2half * cBetah2 * (5.0 + 7.0 * cos2Beta) * sBetah2,
                        -2.0 * self.sqrt35 * cBetah3 * sBetah3 * C2mS2,
                        self.sqrt70 * cBetah4 * sBetah4,
                    ]
                )

            self.wignerdL4 = self.xp.array([d4m4, d4m3, d4m2, d4m1, d40, d41, d42, d43, d44])

        if lmax >= 5:
            cBetah9 = cBetah * cBetah8
            cBetah10 = cBetah * cBetah9
            sBetah9 = sBetah * sBetah8
            sBetah10 = sBetah * sBetah9

            d55 = self.xp.array(
                [
                    sBetah10,
                    self.sqrt10 * cBetah * sBetah9,
                    3 * self.sqrt5 * cBetah2 * sBetah8,
                    2 * self.sqrt30 * cBetah3 * sBetah7,
                    self.sqrt210 * cBetah4 * sBetah6,
                    6.0 * self.sqrt7 * cBetah5 * sBetah5,
                    self.sqrt210 * cBetah6 * sBetah4,
                    2 * self.sqrt30 * cBetah7 * sBetah3,
                    3 * self.sqrt5 * cBetah8 * sBetah2,
                    self.sqrt10 * cBetah9 * sBetah,
                    cBetah10,
                ]
            )
            d5m5 = self.xp.array([d55[10], -d55[9], d55[8], -d55[7], d55[6], -d55[5], d55[4], -d55[3], d55[2], -d55[1], d55[0]])

            d54 = self.xp.empty(d55.shape)
            d53 = self.xp.empty(d55.shape)
            d52 = self.xp.empty(d55.shape)
            d51 = self.xp.empty(d55.shape)
            d50 = self.xp.empty(d55.shape)
            d5m1 = self.xp.empty(d55.shape)
            d5m2 = self.xp.empty(d55.shape)
            d5m3 = self.xp.empty(d55.shape)
            d5m4 = self.xp.empty(d55.shape)

            if global_rotation is True:
                d54 = self.xp.array(
                    [
                        self.sqrt10 * cBetah * sBetah9,
                        sBetah8 * (4.0 + 5.0 * C2mS2),
                        (3.0 / self.sqrt2) * cBetah * sBetah7 * (3.0 + 5.0 * C2mS2),
                        2.0 * self.sqrt3 * cBetah2 * sBetah6 * (2.0 + 5.0 * C2mS2),
                        self.sqrt21 * cBetah3 * sBetah5 * (1.0 + 5.0 * C2mS2),
                        3.0 * self.sqrt70 * cBetah4 * sBetah4 * C2mS2,
                        self.sqrt21 * cBetah5 * sBetah3 * (-1.0 + 5.0 * C2mS2),
                        2.0 * self.sqrt3 * cBetah6 * sBetah2 * (-2.0 + 5.0 * C2mS2),
                        (3.0 / self.sqrt2) * cBetah7 * sBetah * (-3.0 + 5.0 * C2mS2),
                        cBetah8 * (-4.0 + 5.0 * C2mS2),
                        -self.sqrt10 * cBetah9 * sBetah,
                    ]
                )
                d5m4 = self.xp.array([-d54[10], d54[9], -d54[8], d54[7], -d54[6], d54[5], -d54[4], d54[3], -d54[2], d54[1], -d54[0]])

                d53 = self.xp.array(
                    [
                        3.0 * self.sqrt5 * cBetah2 * sBetah8,
                        (3.0 / self.sqrt2) * cBetah * sBetah7 * (3.0 + 5.0 * C2mS2),
                        0.25 * (13.0 + 54.0 * C2mS2 + 45.0 * C2mS2 * C2mS2) * sBetah6,
                        np.sqrt(1.5) * (1.0 + 12.0 * C2mS2 + 15.0 * C2mS2 * C2mS2) * cBetah * sBetah5,
                        0.5 * np.sqrt(10.5) * (-1.0 + 6.0 * C2mS2 + 15.0 * C2mS2 * C2mS2) * cBetah2 * sBetah4,
                        0.25 * self.sqrt35 * (7.0 + 9.0 * cos2Beta) * cBetah3 * sBetah3,
                        0.5 * np.sqrt(10.5) * (-1.0 - 6.0 * C2mS2 + 15.0 * C2mS2 * C2mS2) * cBetah4 * sBetah2,
                        np.sqrt(1.5) * (1.0 - 12.0 * C2mS2 + 15.0 * C2mS2 * C2mS2) * cBetah5 * sBetah,
                        0.25 * (13.0 - 54.0 * C2mS2 + 45.0 * C2mS2 * C2mS2) * cBetah6,
                        (3.0 / self.sqrt2) * cBetah7 * sBetah * (3.0 - 5.0 * C2mS2),
                        3.0 * self.sqrt5 * cBetah8 * sBetah2,
                    ]
                )
                d5m3 = self.xp.array([d53[10], -d53[9], d53[8], -d53[7], d53[6], -d53[5], d53[4], -d53[3], d53[2], -d53[1], d53[0]])

                d52 = self.xp.array(
                    [
                        2 * self.sqrt30 * cBetah3 * sBetah7,
                        2.0 * self.sqrt3 * (2.0 + 5.0 * C2mS2) * cBetah2 * sBetah6,
                        np.sqrt(1.5) * (1.0 + 12.0 * C2mS2 + 15.0 * C2mS2 * C2mS2) * cBetah * sBetah5,
                        (-1.0 + 3.0 * C2mS2 + 18.0 * C2mS2 * C2mS2 + 15.0 * C2mS2 * C2mS2 * C2mS2) * sBetah4,
                        0.5 * self.sqrt7 * (-1.0 - 3.0 * C2mS2 + 9.0 * C2mS2 * C2mS2 + 15.0 * C2mS2 * C2mS2 * C2mS2) * cBetah * sBetah3,
                        0.5 * np.sqrt(52.5) * C2mS2 * cBetah2 * sBetah2 * (1.0 + 3.0 * cos2Beta),
                        0.5 * self.sqrt7 * (1.0 - 3.0 * C2mS2 - 9.0 * C2mS2 * C2mS2 + 15.0 * C2mS2 * C2mS2 * C2mS2) * cBetah3 * sBetah,
                        (1.0 + 3.0 * C2mS2 - 18.0 * C2mS2 * C2mS2 + 15.0 * C2mS2 * C2mS2 * C2mS2) * cBetah4,
                        -np.sqrt(1.5) * (1.0 - 12.0 * C2mS2 + 15.0 * C2mS2 * C2mS2) * cBetah5 * sBetah,
                        2.0 * self.sqrt3 * (-2.0 + 5.0 * C2mS2) * cBetah6 * sBetah2,
                        -2 * self.sqrt30 * cBetah7 * sBetah3,
                    ]
                )
                d5m2 = self.xp.array([-d52[10], d52[9], -d52[8], d52[7], -d52[6], d52[5], -d52[4], d52[3], -d52[2], d52[1], -d52[0]])

                d51 = self.xp.array(
                    [
                        self.sqrt210 * cBetah4 * sBetah6,
                        self.sqrt21 * (1.0 + 5.0 * C2mS2) * cBetah3 * sBetah5,
                        0.5 * np.sqrt(10.5) * (-1.0 + 6.0 * C2mS2 + 15.0 * C2mS2 * C2mS2) * cBetah2 * sBetah4,
                        0.5 * self.sqrt7 * (-1.0 - 3.0 * C2mS2 + 9.0 * C2mS2 * C2mS2 + 15.0 * C2mS2 * C2mS2 * C2mS2) * cBetah * sBetah3,
                        0.125
                        * (1.0 - 28.0 * C2mS2 - 42.0 * C2mS2 * C2mS2 + 84.0 * C2mS2 * C2mS2 * C2mS2 + 105.0 * C2mS2 * C2mS2 * C2mS2 * C2mS2)
                        * sBetah2,
                        np.sqrt(7.5) / 32.0 * cBetah * sBetah * (15.0 + 28.0 * cos2Beta + 21.0 * cos4Beta),
                        0.125
                        * (1.0 + 28.0 * C2mS2 - 42.0 * C2mS2 * C2mS2 - 84.0 * C2mS2 * C2mS2 * C2mS2 + 105.0 * C2mS2 * C2mS2 * C2mS2 * C2mS2)
                        * cBetah2,
                        -0.5 * self.sqrt7 * (1.0 - 3.0 * C2mS2 - 9.0 * C2mS2 * C2mS2 + 15.0 * C2mS2 * C2mS2 * C2mS2) * cBetah3 * sBetah,
                        0.5 * np.sqrt(10.5) * (-1.0 - 6.0 * C2mS2 + 15.0 * C2mS2 * C2mS2) * cBetah4 * sBetah2,
                        -self.sqrt21 * (-1.0 + 5.0 * C2mS2) * cBetah5 * sBetah3,
                        self.sqrt210 * cBetah6 * sBetah4,
                    ]
                )
                d5m1 = self.xp.array([d51[10], -d51[9], d51[8], -d51[7], d51[6], -d51[5], d51[4], -d51[3], d51[2], -d51[1], d51[0]])

                d50 = self.xp.array(
                    [
                        6.0 * self.sqrt7 * cBetah5 * sBetah5,
                        3.0 * self.sqrt70 * C2mS2 * cBetah4 * sBetah4,
                        0.25 * self.sqrt35 * cBetah3 * sBetah3 * (7.0 + 9.0 * cos2Beta),
                        0.5 * np.sqrt(52.5) * C2mS2 * cBetah2 * sBetah2 * (1.0 + 3.0 * cos2Beta),
                        np.sqrt(7.5) / 32.0 * cBetah * sBetah * (15.0 + 28.0 * cos2Beta + 21.0 * cos4Beta),
                        0.125 * C2mS2 * (15.0 - 70.0 * C2mS2 * C2mS2 + 63.0 * C2mS2 * C2mS2 * C2mS2 * C2mS2),
                        -np.sqrt(7.5) / 32.0 * cBetah * sBetah * (15.0 + 28.0 * cos2Beta + 21.0 * cos4Beta),
                        0.5 * np.sqrt(52.5) * C2mS2 * cBetah2 * sBetah2 * (1.0 + 3.0 * cos2Beta),
                        -0.25 * self.sqrt35 * cBetah3 * sBetah3 * (7.0 + 9.0 * cos2Beta),
                        3.0 * self.sqrt70 * C2mS2 * cBetah4 * sBetah4,
                        -6.0 * self.sqrt7 * cBetah5 * sBetah5,
                    ]
                )

            self.wignerdL5 = self.xp.array([d5m5, d5m4, d5m3, d5m2, d5m1, d50, d51, d52, d53, d54, d55])

    def WignerDMatrix(self, l, mp, m):
        """
        Compute Wigner-D matrix.
        """

        if l == 2:
            wignerd = self.wignerdL2[2 + mp][2 + m]
        elif l == 3:
            wignerd = self.wignerdL3[3 + mp][3 + m]
        elif l == 4:
            wignerd = self.wignerdL4[4 + mp][4 + m]
        elif l == 5:
            wignerd = self.wignerdL5[5 + mp][5 + m]
        else:
            raise SyntaxError("l = {0} not supported.".format(l))

        WignerD = self.expAlphaPowers[mp + 5] * wignerd * self.expGammaPowers[m + 5]

        return WignerD

    def set_exp_angle_powers(self, alpha, gamma):
        """
        Set complex exponential values needed for Wigner-D matrices.
        """

        if isinstance(alpha, self.xp.ndarray):
            self.expAlphaPowers = self.xp.zeros((11, len(alpha)), dtype=self.xp.cdouble)
            self.expGammaPowers = self.xp.zeros((11, len(gamma)), dtype=self.xp.cdouble)
        else:
            self.expAlphaPowers = self.xp.zeros(11, dtype=self.xp.cdouble)
            self.expGammaPowers = self.xp.zeros(11, dtype=self.xp.cdouble)

        expAlpha = self.xp.exp(1j * alpha)
        expAlpham = self.xp.conj(expAlpha)
        self.expAlphaPowers[4] = expAlpha
        self.expAlphaPowers[3] = expAlpha * expAlpha
        self.expAlphaPowers[2] = expAlpha * self.expAlphaPowers[3]
        self.expAlphaPowers[1] = expAlpha * self.expAlphaPowers[2]
        self.expAlphaPowers[0] = expAlpha * self.expAlphaPowers[1]
        self.expAlphaPowers[5] = 1.0
        self.expAlphaPowers[6] = expAlpham
        self.expAlphaPowers[7] = expAlpham * expAlpham
        self.expAlphaPowers[8] = expAlpham * self.expAlphaPowers[7]
        self.expAlphaPowers[9] = expAlpham * self.expAlphaPowers[8]
        self.expAlphaPowers[10] = expAlpham * self.expAlphaPowers[9]

        expGamma = self.xp.exp(1j * gamma)
        expGammam = self.xp.conj(expGamma)
        self.expGammaPowers[4] = expGamma
        self.expGammaPowers[3] = expGamma * expGamma
        self.expGammaPowers[2] = expGamma * self.expGammaPowers[3]
        self.expGammaPowers[1] = expGamma * self.expGammaPowers[2]
        self.expGammaPowers[0] = expGamma * self.expGammaPowers[1]
        self.expGammaPowers[5] = 1.0
        self.expGammaPowers[6] = expGammam
        self.expGammaPowers[7] = expGammam * expGammam
        self.expGammaPowers[8] = expGammam * self.expGammaPowers[7]
        self.expGammaPowers[9] = expGammam * self.expGammaPowers[8]
        self.expGammaPowers[10] = expGammam * self.expGammaPowers[9]

    def rotate_z(self, angle, old):
        """
        Rotate vector around z-axis.
        """

        cosangle = np.cos(angle)
        sinangle = np.sin(angle)

        newx = old[0] * cosangle - old[1] * sinangle
        newy = old[0] * sinangle + old[1] * cosangle

        return [newx, newy, old[2]]

    def rotate_y(self, angle, old):
        """
        Rotate vector around y-axis.
        """

        cosangle = np.cos(angle)
        sinangle = np.sin(angle)

        newx = old[0] * cosangle + old[2] * sinangle
        newz = -old[0] * sinangle + old[2] * cosangle

        return [newx, old[1], newz]

    def get_euler_slope(self, af, mf):
        """
        Slope for the alpha angle in the ringdown attachment.
        """

        slope = 2 * np.pi / mf * (IMRPhenomT_fringfit(af, 22) - IMRPhenomT_fringfit(af, 21))
        if af < 0:
            slope = -slope
        return slope


# Twising-up rotation functions written in numba to speed-up evaluation.
# By default polarizations_from='CPmodes' and these are not used.
# Used in compute_L0modes and compute_Jmodes
@njit(parallel=True)
def numba_global_rotation(lmax, L0modes, Jmodes, wignerdL2, wignerdL3, wignerdL4, wignerdL5, expAlphaPowers, expGammaPowers):

    L0list = []
    for l in range(2, lmax + 1):
        for m in range(-l, l + 1):
            L0list.append([l, m])

    for L0mode in prange(len(L0list)):
        l, m = L0list[L0mode]
        lmodes = (l - 1) * (l - 1) + 2 * (l - 1 - 2) + 1 if l > 2 else 0
        for mp in range(-l, l + 1):
            Jmode = lmodes + mp + l
            if l == 2:
                wignerd = wignerdL2[l + mp][l + m]
            elif l == 3:
                wignerd = wignerdL3[l + mp][l + m]
            elif l == 4:
                wignerd = wignerdL4[l + mp][l + m]
            elif l == 5:
                wignerd = wignerdL5[l + mp][l + m]

            WignerD = expAlphaPowers[mp + 5] * wignerd * expGammaPowers[m + 5]

            for idx in range(len(L0modes[L0mode])):
                L0modes[L0mode][idx] = L0modes[L0mode][idx] + WignerD * Jmodes[Jmode][idx]

    return L0modes


@njit(fastmath=True)
def isin(array, l, m):
    n, p = array.shape
    for i in range(n):
        if (array[i][0] == l) and (array[i][1] == m):
            return True
    return False


@njit(parallel=True)
def numba_rotation(lmax, Jmodes, CPmodes, wignerdL2, wignerdL3, wignerdL4, wignerdL5, expAlphaPowers, expGammaPowers, mode_array):

    Jlist = []
    for l in range(2, lmax + 1):
        for m in range(-l, l + 1):
            Jlist.append([l, m])

    for Jmode in prange(len(Jlist)):
        l, m = Jlist[Jmode]
        l_coprec_array = mode_array[mode_array[:, 0] == l]
        for mp in l_coprec_array[:, 1]:
            # comode = [l, mp]
            idx_comode = np.where((mode_array[:, 0] == l) & (mode_array[:, 1] == mp))[0][0]
            if l == 2:
                wignerd = wignerdL2[l + mp][l + m]
            elif l == 3:
                wignerd = wignerdL3[l + mp][l + m]
            elif l == 4:
                wignerd = wignerdL4[l + mp][l + m]
            elif l == 5:
                wignerd = wignerdL5[l + mp][l + m]
            WignerD = expAlphaPowers[mp + 5] * wignerd * expGammaPowers[m + 5]
            for idx in range(len(Jmodes[Jmode])):
                Jmodes[Jmode][idx] += WignerD[idx] * CPmodes[idx_comode][idx]

    return Jmodes
