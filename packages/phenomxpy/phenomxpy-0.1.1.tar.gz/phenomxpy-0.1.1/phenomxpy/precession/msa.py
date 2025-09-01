# Copyright (C) 2023  Cecilio García Quirós
"""
Multi-Scale-Analyis Euler angles
"""

import numpy as np
from scipy.special import ellipj, ellipkinc
from phenomxpy.utils import replace_instances_with_value


class MSA:
    """
    Class with extra methods for the MSA angles to be added to ``pPrec``.

    Only ``PrecVersion`` = 223 version is supported.

    The methods are adapted from `PhenomX lalsuite <https://git.ligo.org/lscsoft/lalsuite/-/blob/master/lalsimulation/lib/LALSimIMRPhenomX_precession.c>`_.
    """

    def compute_msa_angles(self, omega, **kwargs):
        r"""
        Compute MSA angles alpha, cosbeta, gamma.

        Parameters
        ----------
        omega: float, 1D ndarray
            frequency evolution taken from the aligned-spin model.

        Returns
        -------
        Tuple with 3 1D ndarrays
            :math:`\alpha`, :math:`\cos \beta`, :math:`\gamma`
        """

        # Determine if single value or array case
        if np.isscalar(omega):
            xp = np
            array = False
        else:
            xp = self.xp
            array = True

        v = xp.cbrt(omega * 0.5)
        v2 = v * v
        invv = 1.0 / v
        invv2 = invv * invv

        # FIXME why LAL doesn't use L_norm3Pn here?
        L_norm = self._pWF.eta / v
        J_norm = self.JNorm_MSA(L_norm)

        self.S32, self.Smi2, self.Spl2 = self.Roots_MSA(L_norm, J_norm)

        self.Spl2mSmi2 = self.Spl2 - self.Smi2
        self.Spl2pSmi2 = self.Spl2 + self.Smi2
        self.Spl = xp.sqrt(self.Spl2)
        self.Smi = xp.sqrt(self.Smi2)

        SNorm = self.SNorm_MSA(v, v2, **kwargs)
        self.S_norm = SNorm
        self.S_norm_2 = SNorm * SNorm

        x = self.phiz_MSA(v, invv, invv2, J_norm)
        y = self.zeta_MSA(v, v2, invv, invv2)

        if array is False:
            if xp.abs(self.Smi2 - self.Spl2) > 1e-5:
                vMSA = self.MSA_Corrections(v, v2, L_norm, J_norm, self.Spl, self.Spl2, self.Smi2, self.S32)
                x += vMSA[0]
                y += vMSA[1]
        else:
            mask = xp.abs(self.Smi2 - self.Spl2) > 1e-5
            if xp.any(mask):
                vMSA = xp.zeros((3, len(v)))
                vMSA[:, mask] = self.MSA_Corrections(
                    v[mask], v2[mask], L_norm[mask], J_norm[mask], self.Spl[mask], self.Spl2[mask], self.Smi2[mask], self.S32[mask]
                )
                x += vMSA[0]
                y += vMSA[1]

        # FIXME In LAL we use now 3PN norm for L and J. But that is not consistent with the alpha and gamma computed before
        L_norm = self.Lnorm_3PN_of_v(v, v2, L_norm)
        J_norm = self.JNorm_MSA(L_norm)

        z = self.costhetaLJ(L_norm, J_norm, SNorm, **kwargs)

        alpha = x + self.alphaOff
        gamma = -(y + self.alphaOff)
        cosbeta = z

        return alpha, cosbeta, gamma

    def JNorm_MSA(self, L_norm):
        """
        Get norm of J using Eq 41 :cite:`Katerina_2017`.
        """
        xp = np if np.isscalar(L_norm) else self.xp
        return xp.sqrt(L_norm * L_norm + (2 * L_norm * self.c1_over_eta) + self.SAv2)

    def Lnorm_3PN_of_v(self, v, v2, L_norm):
        return L_norm * (
            1.0
            + v2 * (self.constants_L[0] + v * self.constants_L[1] + v2 * (self.constants_L[2] + v * self.constants_L[3] + v2 * (self.constants_L[4])))
        )

    def SNorm_MSA(self, v, v2):
        """
        Get norm of S, see :cite:`Katerina_2017`.
        """

        # Determine if single value or array case
        if np.isscalar(v):
            xp = np
            array = False
        else:
            xp = self.xp
            array = True

        # sn, cn are Jacobi elliptic functions
        # psi is the phase and m a parameter entering the Jacobi elliptic functions

        # Equation 25 of Chatziioannou et al, PRD 95, 104004, (2017), arXiv:1703.03967
        m = (self.Smi2 - self.Spl2) / (self.S32 - self.Spl2)
        psi = self.psiofv(v, v2, self.psi0, self.psi1, self.psi2)

        # Evaluate the Jacobi elliptic function
        sn, _, _, _ = ellipj(psi, m)  # Can also run on cupy arrays

        # If spin norms ~ cancel then we do not need to evaluate the Jacobi elliptic function.
        if array:
            sn = replace_instances_with_value(sn, xp.abs(self.Smi2 - self.Spl2) < 1e-5, 0, xp)
        elif abs(self.Smi2 - self.Spl2) < 1e-5:
            sn = 0

        # Equation 23 of Chatziioannou et al, PRD 95, 104004, (2017), arXiv:1703.03967
        SNorm2 = self.Spl2 + (self.Smi2 - self.Spl2) * sn * sn

        return xp.sqrt(SNorm2)

    def psiofv(self, v, v2, psi0, psi1, psi2):
        """
        Equation 51 :cite:`Katerina_2017`.
        """
        return psi0 - 0.75 * self.g0 * self.delta_qq * (1 + psi1 * v + psi2 * v2) / (v2 * v)

    def phiz_MSA(self, v, invv, invv2, JNorm):
        r"""
        Get :math:`$\phi_z` using Eq 66 :cite:`Katerina_2017`.
        The coefficients are given in Appendix D (D15 - D26).
        """

        # Determine if single value or array case
        if np.isscalar(v):
            xp = np
            array = False
        else:
            xp = self.xp
            array = True

        LNewt = self._pWF.eta / v

        c1 = self.c1
        c12 = c1 * c1

        SAv2 = self.SAv2
        SAv = self.SAv
        invSAv = self.invSAv
        invSAv2 = self.invSAv2

        # These are log functions defined in Eq. D27 and D28 of Chatziioannou et al, PRD 95, 104004, (2017), arXiv:1703.03967
        log1 = xp.log(xp.abs(c1 + JNorm * self._pWF.eta + self._pWF.eta * LNewt))
        log2 = xp.log(xp.abs(c1 + JNorm * SAv * v + SAv2 * v))

        # Eq. D22 of Chatziioannou et al, PRD 95, 104004, (2017), arXiv:1703.03967
        phiz_0_coeff = (JNorm * self.inveta4) * (0.5 * c12 - c1 * self.eta2 * invv / 6.0 - SAv2 * self.eta2 / 3.0 - self.eta4 * invv2 / 3.0) - (
            c1 * 0.5 * self.inveta
        ) * (c12 * self.inveta4 - SAv2 * self.inveta2) * log1

        # Eq. D23 of Chatziioannou et al, PRD 95, 104004, (2017), arXiv:1703.03967
        # Note the factor of c12 in the second term
        phiz_1_coeff = -0.5 * JNorm * self.inveta2 * (c1 + self.eta * LNewt) + 0.5 * self.inveta3 * (c12 - self.eta2 * SAv2) * log1

        # Eq. D24 of Chatziioannou et al, PRD 95, 104004, (2017), arXiv:1703.03967
        phiz_2_coeff = -JNorm + SAv * log2 - c1 * log1 * self.inveta

        # Eq. D25 of Chatziioannou et al, PRD 95, 104004, (2017), arXiv:1703.03967
        phiz_3_coeff = JNorm * v - self.eta * log1 + c1 * log2 * self.invSAv

        # Eq. D26 of Chatziioannou et al, PRD 95, 104004, (2017), arXiv:1703.03967
        phiz_4_coeff = (0.5 * JNorm * invSAv2 * v) * (c1 + v * SAv2) - (0.5 * invSAv2 * invSAv) * (c12 - self.eta2 * SAv2) * log2

        # Eq. D27 of Chatziioannou et al, PRD 95, 104004, (2017), arXiv:1703.03967
        phiz_5_coeff = (
            -JNorm * v * ((0.5 * c12 * invSAv2 * invSAv2) - (c1 * v * invSAv2 / 6.0) - v * v / 3.0 - self.eta2 * invSAv2 / 3.0)
            + (0.5 * c1 * invSAv2 * invSAv2 * invSAv) * (c12 - self.eta2 * SAv2) * log2
        )

        # Eq. 66 of Chatziioannou et al, PRD 95, 104004, (2017), arXiv:1703.03967
        # \phi_{z,-1} = \sum^5_{n=0} <\Omega_z>^(n) \phi_z^(n) + \phi_{z,-1}^0
        # Note that the <\Omega_z>^(n) are given by self.Omegazn_coeff's as in Eqs. D15-D20

        phiz_out = (
            phiz_0_coeff * self.Omegaz0_coeff
            + phiz_1_coeff * self.Omegaz1_coeff
            + phiz_2_coeff * self.Omegaz2_coeff
            + phiz_3_coeff * self.Omegaz3_coeff
            + phiz_4_coeff * self.Omegaz4_coeff
            + phiz_5_coeff * self.Omegaz5_coeff
            + self.phiz_0
        )

        # Check for NaNs and replace with zero
        if array:
            phiz_out = replace_instances_with_value(phiz_out, xp.isnan(phiz_out), 0, xp)
        elif np.isnan(phiz_out):
            phiz_out = 0

        return phiz_out

    def zeta_MSA(self, v, v2, invv, invv2):
        r"""
        Eq. F5 :cite:`Katerina_2017`.
        :math:`\zeta_{z,-1} = \eta v^{-3} \sum^5_{n=0} <\Omega_{\zeta}>^n v^n + \zeta_{-1}^0`.
        Note that the :math:`<\Omega_{\eta}>^n` are given by ``self.Omegazeta(n)_coeff``'s as in Eqs. F6-F11.
        """

        # Determine if single value or array case
        if np.isscalar(v):
            xp = np
            array = False
        else:
            xp = self.xp
            array = True

        invv3 = invv * invv2
        logv = xp.log(v)

        # Note factor of log(v) as per LALSimInspiralFDPrecAngles_internals.c, https:#git.ligo.org/lscsoft/lalsuite/-/blob/master/lalsimulation/lib/LALSimInspiralFDPrecAngles_internals.c#L718
        zeta_out = (
            self.eta
            * (
                self.Omegazeta0_coeff * invv3
                + self.Omegazeta1_coeff * invv2
                + self.Omegazeta2_coeff * invv
                + self.Omegazeta3_coeff * logv
                + self.Omegazeta4_coeff * v
                + self.Omegazeta5_coeff * v2
            )
            + self.zeta_0
        )

        # Check for NaNs and replace with zero
        if array:
            zeta_out = replace_instances_with_value(zeta_out, xp.isnan(zeta_out), 0, xp)
        elif np.isnan(zeta_out):
            zeta_out = 0

        return zeta_out

    def costhetaLJ(self, L_norm, J_norm, S_norm):
        """
        Calculate (L dot J).
        """

        costhetaLJ = 0.5 * (J_norm * J_norm + L_norm * L_norm - S_norm * S_norm) / (L_norm * J_norm)

        if np.isscalar(L_norm):
            if costhetaLJ > 1.0:
                costhetaLJ = +1.0
            if costhetaLJ < -1.0:
                costhetaLJ = -1.0
        else:
            costhetaLJ[costhetaLJ > 1] = 1
            costhetaLJ[costhetaLJ < -1] = -1

        return costhetaLJ

    def MSA_Corrections(self, v, v2, LNorm, JNorm, Spl, Spl2, Smi2, S32):
        r"""
        Get MSA corrections to :math:`\zeta` and :math:`\phi_z` using Eq. F19 in Appendix F and Eq. 67 :cite:`Katerina_2017`. respectively.
        """

        # Determine if single value or array case
        if np.isscalar(LNorm):
            xp = np
            array = False
        else:
            xp = self.xp
            array = True

        # Precessing flag
        pflag = self.PrecVersion

        # Initialize arrays
        if array is False:
            vMSA = [0.0, 0.0, 0.0]
        else:
            vMSA = self.xp.zeros((3, len(v)))

        # Sets c0, c2 and c4 in pPrec as per Eq. B6-B8 of Chatziioannou et al, PRD 95, 104004, (2017), arXiv:1703.03967
        c_vec = self.Constants_c_MSA(v, v2, JNorm, Spl2, Smi2)

        # Sets d0, d2 and d4 in pPrec as per Eq. B9-B11 of Chatziioannou et al, PRD 95, 104004, (2017), arXiv:1703.03967
        d_vec = self.Constants_d_MSA(LNorm, JNorm, Spl, Spl2, Smi2)

        c0, c2, c4 = c_vec

        d0, d2, d4 = d_vec

        # Pre-cache a bunch of useful variables
        two_d0 = 2.0 * d0

        # Eq. B20 of Chatziioannou et al, PRD 95, 104004, (2017), arXiv:1703.03967
        sd = xp.sqrt(xp.abs(d2 * d2 - 4.0 * d0 * d4))

        # Eq. F20 of Chatziioannou et al, PRD 95, 104004, (2017), arXiv:1703.03967
        A_theta_L = 0.5 * ((JNorm / LNorm) + (LNorm / JNorm) - (Spl2 / (JNorm * LNorm)))

        # Eq. F21 of Chatziioannou et al, PRD 95, 104004, (2017), arXiv:1703.03967
        B_theta_L = 0.5 * (Spl2 - Smi2) / (JNorm * LNorm)

        # Coefficients for B16
        nc_num = 2.0 * (d0 + d2 + d4)
        nc_denom = two_d0 + d2 + sd

        # Equations B16 and B17 respectively
        nc = nc_num / nc_denom
        nd = nc_denom / two_d0

        sqrt_nc = xp.sqrt(xp.abs(nc))
        sqrt_nd = xp.sqrt(xp.abs(nd))

        # Get phase and phase evolution of S
        psi = self.Psi_MSA(v, v2) + self.psi0
        psi_dot = self.Psi_dot_MSA(v, v2, Spl2, S32)

        # Trigonometric calls are expensive, pre-cache them
        # Note: arctan(tan(x)) = 0 if and only if x \in (−pi/2,pi/2).
        tan_psi = xp.tan(psi)
        atan_psi = xp.arctan(tan_psi)

        # Eq. B18
        C1 = -0.5 * (c0 / d0 - 2.0 * (c0 + c2 + c4) / nc_num)

        # Eq. B19
        C2num = c0 * (-2.0 * d0 * d4 + d2 * d2 + d2 * d4) - c2 * d0 * (d2 + 2.0 * d4) + c4 * d0 * (two_d0 + d2)
        C2den = 2.0 * d0 * sd * (d0 + d2 + d4)
        C2 = C2num / C2den

        # These are defined in Appendix B, B14 and B15 respectively
        Cphi = C1 + C2
        Dphi = C1 - C2

        # Calculate C_phi term in Eq. 67
        if pflag == 222 or pflag == 223:
            # As implemented in LALSimInspiralFDPrecAngles.c, c.f. https:#git.ligo.org/lscsoft/lalsuite/-/blob/master/lalsimulation/lib/LALSimInspiralFDPrecAngles_internals.c#L772
            phiz_0_MSA_Cphi_term = (
                xp.abs((c4 * d0 * ((2 * d0 + d2) + sd) - c2 * d0 * ((d2 + 2.0 * d4) - sd) - c0 * ((2 * d0 * d4) - (d2 + d4) * (d2 - sd))) / (C2den))
                * (sqrt_nc / (nc - 1.0) * (atan_psi - xp.arctan(sqrt_nc * tan_psi)))
                / psi_dot
            )
        else:
            # First term in Eq. 67
            phiz_0_MSA_Cphi_term = ((Cphi / psi_dot) * sqrt_nc / (nc - 1.0)) * xp.arctan(
                ((1.0 - sqrt_nc) * tan_psi) / (1.0 + (sqrt_nc * tan_psi * tan_psi))
            )

        # Limit implied by Eq. 67
        if array is True:
            phiz_0_MSA_Cphi_term = replace_instances_with_value(phiz_0_MSA_Cphi_term, nc == 1.0, 0, xp)
        elif nc == 1.0:
            phiz_0_MSA_Cphi_term = 0

        # Calculate D_phi term in Eq. 67
        if pflag == 222 or pflag == 223:
            # As implemented in LALSimInspiralFDPrecAngles.c, c.f. https:#git.ligo.org/lscsoft/lalsuite/-/blob/master/lalsimulation/lib/LALSimInspiralFDPrecAngles_internals.c#L779
            phiz_0_MSA_Dphi_term = (
                xp.abs((-c4 * d0 * ((2 * d0 + d2) - sd) + c2 * d0 * ((d2 + 2.0 * d4) + sd) - c0 * (-(2 * d0 * d4) + (d2 + d4) * (d2 + sd))))
                / (C2den)
                * (sqrt_nd / (nd - 1.0) * (atan_psi - xp.arctan(sqrt_nd * tan_psi)))
                / psi_dot
            )
        else:
            # Second term in Eq. 67
            phiz_0_MSA_Dphi_term = ((Dphi / psi_dot) * sqrt_nd / (nd - 1.0)) * xp.arctan(
                ((1.0 - sqrt_nd) * tan_psi) / (1.0 + (sqrt_nd * tan_psi * tan_psi))
            )

        # Limit implied by Eq. 67
        if array is True:
            phiz_0_MSA_Dphi_term = replace_instances_with_value(phiz_0_MSA_Dphi_term, nd == 1.0, 0, xp)
        elif nd == 1.0:
            phiz_0_MSA_Dphi_term = 0.0

        # Eq. 67
        vMSA[0] = phiz_0_MSA_Cphi_term + phiz_0_MSA_Dphi_term

        #  The first MSA correction to \zeta as given in Eq. F19
        if pflag == 222 or pflag == 223 or pflag == 224:
            # As implemented in LALSimInspiralFDPrecAngles.c, c.f. https:#git.ligo.org/lscsoft/lalsuite/-/blob/master/lalsimulation/lib/LALSimInspiralFDPrecAngles_internals.c#L786
            # Note that Cphi and Dphi are *not* used but phiz_0_MSA_Cphi_term and phiz_0_MSA_Dphi_term are
            vMSA[1] = A_theta_L * vMSA[0] + 2.0 * B_theta_L * d0 * (phiz_0_MSA_Cphi_term / (sd - d2) - phiz_0_MSA_Dphi_term / (sd + d2))
        else:
            # Eq. F19 as in arXiv:1703.03967
            vMSA[1] = ((A_theta_L * (Cphi + Dphi)) + (2.0 * d0 * B_theta_L) * ((Cphi / (sd - d2)) - (Dphi / (sd + d2)))) / psi_dot

        # Return 0 if the angles are NaNs
        if array:
            vMSA[0] = replace_instances_with_value(vMSA[0], xp.isnan(vMSA[0]), 0, xp)
            vMSA[1] = replace_instances_with_value(vMSA[1], xp.isnan(vMSA[1]), 0, xp)
        else:
            vMSA[0] = 0 if np.isnan(vMSA[0]) else vMSA[0]
            vMSA[1] = 0 if np.isnan(vMSA[1]) else vMSA[1]

        return vMSA

    def Constants_c_MSA(self, v, v2, JNorm, Spl2, Smi2):
        """
        Get c constants from Appendix B (B6, B7, B8) :cite:`Katerina_2017`.
        """

        v3 = v * v2
        v4 = v2 * v2
        v6 = v3 * v3

        JNorm2 = JNorm * JNorm

        vout = [0.0, 0.0, 0.0]

        Seff = self.Seff

        if self.PrecVersion != 220:
            # Equation B6 of Chatziioannou et al, PRD 95, 104004, (2017)
            vout[0] = JNorm * (
                0.75
                * (1.0 - Seff * v)
                * v2
                * (
                    self.eta3
                    + 4.0 * self.eta3 * Seff * v
                    - 2.0 * self.eta * (JNorm2 - Spl2 + 2.0 * (self.S1_norm_2 - self.S2_norm_2) * self.delta_qq) * v2
                    - 4.0 * self.eta * Seff * (JNorm2 - Spl2) * v3
                    + (JNorm2 - Spl2) * (JNorm2 - Spl2) * v4 * self.inveta
                )
            )

            # Equation B7 of Chatziioannou et al, PRD 95, 104004, (2017)
            vout[1] = JNorm * (-1.5 * self.eta * (Spl2 - Smi2) * (1.0 + 2.0 * Seff * v - (JNorm2 - Spl2) * v2 * self.inveta2) * (1.0 - Seff * v) * v4)

            # Equation B8 of Chatziioannou et al, PRD 95, 104004, (2017)
            vout[2] = JNorm * (0.75 * self.inveta * (Spl2 - Smi2) * (Spl2 - Smi2) * (1.0 - Seff * v) * v6)
        else:
            # This is as implemented in LALSimInspiralFDPrecAngles, should be equivalent to above code.
            #   c.f. https:#git.ligo.org/lscsoft/lalsuite/-/blob/master/lalsimulation/lib/LALSimInspiralFDPrecAngles_internals.c#L578
            J_norm = JNorm
            delta = self.delta_qq
            eta = self.eta
            eta_2 = eta * eta

            vout[0] = (
                -0.75
                * (
                    (JNorm2 - Spl2) * (JNorm2 - Spl2) * v4 / (self.eta)
                    - 4.0 * (self.eta) * (self.Seff) * (JNorm2 - Spl2) * v3
                    - 2.0 * (JNorm2 - self.Spl2 + 2 * ((self.S1_norm_2) - (self.S2_norm_2)) * (delta)) * (self.eta) * v2
                    + (4.0 * (self.Seff) * v + 1) * (self.eta) * (eta_2)
                )
                * J_norm
                * v2
                * ((self.Seff) * v - 1.0)
            )
            vout[1] = (
                1.5
                * (Smi2 - Spl2)
                * J_norm
                * ((JNorm2 - Spl2) / (self.eta) * v2 - 2.0 * (self.eta) * (self.Seff) * v - (self.eta))
                * ((self.Seff) * v - 1.0)
                * v4
            )
            vout[2] = -0.75 * J_norm * ((self.Seff) * v - 1.0) * (Spl2 - Smi2) * (Spl2 - Smi2) * v6 / (self.eta)

        return vout

    def Constants_d_MSA(self, LNorm, JNorm, Spl, Spl2, Smi2):
        """
        Get d constants from Appendix B (B9, B10, B11) :cite:`Katerina_2017`.
        """

        LNorm2 = LNorm * LNorm
        JNorm2 = JNorm * JNorm

        vout = [0.0, 0.0, 0.0]

        vout[0] = -(JNorm2 - (LNorm + Spl) * (LNorm + Spl)) * ((JNorm2 - (LNorm - Spl) * (LNorm - Spl)))
        vout[1] = -2.0 * (Spl2 - Smi2) * (JNorm2 + LNorm2 - Spl2)
        vout[2] = -(Spl2 - Smi2) * (Spl2 - Smi2)

        return vout

    def Psi_MSA(self, v, v2):
        r"""
        Get :math:`\psi` using Eq 51 :cite:`Katerina_2017`.
        - Here :math:`\psi` is the phase of S as in Eq 23.
        - Note that the coefficients are defined in Appendix C (C1 and C2).
        """
        return -0.75 * self.g0 * self.delta_qq * (1.0 + self.psi1 * v + self.psi2 * v2) / (v2 * v)

    def Psi_dot_MSA(self, v, v2, Spl2, S32):
        r"""
        Get :math:`\dot{\psi}` using Eq 24 :cite:`Katerina_2017`.
        :math:`\frac{d \psi}{d t} = \frac{A}{2} \sqrt{S_+^2 - S_3^2}`.
        """
        xp = np if np.isscalar(v) else self.xp
        A_coeff = -1.5 * (v2 * v2 * v2) * (1.0 - v * self.Seff) * self.sqrt_inveta
        psi_dot = 0.5 * A_coeff * xp.sqrt(Spl2 - S32)

        return psi_dot

    def Initialize_MSA(self, ExpansionOrder=5):
        """
        Initialize all the core variables for the MSA system. This will be called first.
        """

        self.PrecVersion = 223

        self.eta = self._pWF.eta
        self.eta2 = self.eta * self.eta
        self.eta3 = self.eta * self.eta2
        self.eta4 = self.eta * self.eta3
        self.inveta = 1 / self.eta
        self.inveta2 = self.inveta * self.inveta
        self.inveta3 = self.inveta * self.inveta2
        self.inveta4 = self.inveta * self.inveta3
        self.sqrt_inveta = 1 / np.sqrt(self.eta)

        pflag = self.PrecVersion
        if pflag != 220 and pflag != 221 and pflag != 222 and pflag != 223 and pflag != 224:
            raise SyntaxError("MSA system requires PrecVersion 220, 221, 222, 223 or 224.\n")

        # First initialize the system of variables needed for Chatziioannou et al, PRD, 88, 063011, (2013), arXiv:1307.4418:
        #     - Racine et al, PRD, 80, 044010, (2009), arXiv:0812.4413
        #     - Favata, PRD, 80, 024002, (2009), arXiv:0812.0069
        #     - Blanchet et al, PRD, 84, 064041, (2011), arXiv:1104.5659
        #     - Bohe et al, CQG, 30, 135009, (2013), arXiv:1303.7412

        eta = self.eta
        eta2 = self.eta2
        eta3 = self.eta3
        eta4 = self.eta4

        m1 = self._pWF.m1
        m2 = self._pWF.m2

        LAL_PI = np.pi
        LAL_GAMMA = np.euler_gamma
        LAL_LN2 = np.log(2)
        LAL_G_SI = 6.6743e-11
        LAL_C_SI = 299792458.0
        LAL_MSUN_SI = 1.9884098706980507e30

        self.piGM = LAL_PI * self._pWF.total_mass * LAL_MSUN_SI * (LAL_G_SI / LAL_C_SI) / (LAL_C_SI * LAL_C_SI)

        # PN Coefficients for d \omega / d t as per LALSimInspiralFDPrecAngles_internals.c
        domegadt_constants_NS = [
            96.0 / 5.0,
            -1486.0 / 35.0,
            -264.0 / 5.0,
            384.0 * LAL_PI / 5.0,
            34103.0 / 945.0,
            13661.0 / 105.0,
            944.0 / 15.0,
            LAL_PI * (-4159.0 / 35.0),
            LAL_PI * (-2268.0 / 5.0),
            (16447322263.0 / 7276500.0 + LAL_PI * LAL_PI * 512.0 / 5.0 - LAL_LN2 * 109568.0 / 175.0 - LAL_GAMMA * 54784.0 / 175.0),
            (-56198689.0 / 11340.0 + LAL_PI * LAL_PI * 902.0 / 5.0),
            1623.0 / 140.0,
            -1121.0 / 27.0,
            -54784.0 / 525.0,
            -LAL_PI * 883.0 / 42.0,
            LAL_PI * 71735.0 / 63.0,
            LAL_PI * 73196.0 / 63.0,
        ]
        domegadt_constants_SO = [
            -904.0 / 5.0,
            -120.0,
            -62638.0 / 105.0,
            4636.0 / 5.0,
            -6472.0 / 35.0,
            3372.0 / 5.0,
            -LAL_PI * 720.0,
            -LAL_PI * 2416.0 / 5.0,
            -208520.0 / 63.0,
            796069.0 / 105.0,
            -100019.0 / 45.0,
            -1195759.0 / 945.0,
            514046.0 / 105.0,
            -8709.0 / 5.0,
            -LAL_PI * 307708.0 / 105.0,
            LAL_PI * 44011.0 / 7.0,
            -LAL_PI * 7992.0 / 7.0,
            LAL_PI * 151449.0 / 35.0,
        ]
        domegadt_constants_SS = [-494.0 / 5.0, -1442.0 / 5.0, -233.0 / 5.0, -719.0 / 5.0]

        L_csts_nonspin = [
            3.0 / 2.0,
            1.0 / 6.0,
            27.0 / 8.0,
            -19.0 / 8.0,
            1.0 / 24.0,
            135.0 / 16.0,
            -6889 / 144.0 + 41.0 / 24.0 * LAL_PI * LAL_PI,
            31.0 / 24.0,
            7.0 / 1296.0,
        ]
        L_csts_spinorbit = [-14.0 / 6.0, -3.0 / 2.0, -11.0 / 2.0, 133.0 / 72.0, -33.0 / 8.0, 7.0 / 4.0]

        # Note that Chatziioannou et al use q = m2/m1, where m1 > m2 and therefore q < 1
        # IMRPhenomX assumes m1 > m2 and q > 1. For the internal MSA code, flip q and
        # dump this to self.qq, where qq explicitly dentoes that this is 0 < q < 1.

        q = m2 / m1  # m2 / m1, q < 1, m1 > m2
        invq = 1.0 / q  # m2 / m1, q < 1, m1 > m2
        self.qq = q
        self.invqq = invq
        mu = (m1 * m2) / (m1 + m2)

        # \delta and powers of \delta in terms of q < 1, should just be m1 - m2
        self.delta_qq = (1.0 - self.qq) / (1.0 + self.qq)
        self.delta2_qq = self.delta_qq * self.delta_qq
        self.delta3_qq = self.delta_qq * self.delta2_qq
        self.delta4_qq = self.delta_qq * self.delta3_qq

        # Define source frame such that \hat{L} = {0,0,1} with L_z pointing along \hat{z}.
        Lhat = np.array([0.0, 0.0, 1.0])

        # Set LHat variables - these are fixed.
        self.Lhat_cos_theta = 1.0  # Cosine of Polar angle of orbital angular momentum
        self.Lhat_phi = 0.0  # Azimuthal angle of orbital angular momentum
        self.Lhat_theta = 0.0  # Polar angle of orbital angular momentum

        # Dimensionful spin vectors, note eta = m1 * m2 and q = m2/m1
        S1v = self._pWF.s1_dim  # eta / q = m1^2  # FIXME check
        S2v = self._pWF.s2_dim  # eta * q = m2^2

        S1_0_norm = np.linalg.norm(S1v)
        S2_0_norm = np.linalg.norm(S2v)

        self.S1_norm = S1_0_norm
        self.S2_norm = S2_0_norm
        self.S1_norm_2 = self.S1_norm * self.S1_norm
        self.S2_norm_2 = self.S2_norm * self.S2_norm

        # Initial dimensionful spin vectors at reference frequency
        self.S1_0 = S1v
        self.S2_0 = S2v

        # Reference velocity v and v^2
        # self.v_0 = np.cbrt(self.piGM * self._pWF.f_ref)
        self.v_0 = np.cbrt(np.pi * self._pWF.Mfref)
        self.v_0_2 = self.v_0 * self.v_0

        # Reference orbital angular momenta
        L_0 = self.eta / self.v_0 * Lhat
        self.L_0 = L_0

        # Inner products used in MSA system
        dotS1L = np.dot(S1v, Lhat)
        dotS2L = np.dot(S2v, Lhat)
        dotS1S2 = np.dot(S1v, S2v)
        dotS1Ln = dotS1L / S1_0_norm
        dotS2Ln = dotS2L / S2_0_norm

        # Add dot products to struct
        self.dotS1L = dotS1L
        self.dotS2L = dotS2L
        self.dotS1S2 = dotS1S2
        self.dotS1Ln = dotS1Ln
        self.dotS2Ln = dotS2Ln

        # Coeffcients for PN orbital angular momentum at 3PN, as per LALSimInspiralFDPrecAngles_internals.c
        self.constants_L = np.zeros(5)
        self.constants_L[0] = L_csts_nonspin[0] + eta * L_csts_nonspin[1]
        self.constants_L[1] = self.Get_PN_beta(L_csts_spinorbit[0], L_csts_spinorbit[1])
        self.constants_L[2] = L_csts_nonspin[2] + eta * L_csts_nonspin[3] + eta * eta * L_csts_nonspin[4]
        self.constants_L[3] = self.Get_PN_beta((L_csts_spinorbit[2] + L_csts_spinorbit[3] * eta), (L_csts_spinorbit[4] + L_csts_spinorbit[5] * eta))
        self.constants_L[4] = L_csts_nonspin[5] + L_csts_nonspin[6] * eta + L_csts_nonspin[7] * eta * eta + L_csts_nonspin[8] * eta * eta * eta

        # Effective total spin
        Seff = (1.0 + q) * self.dotS1L + (1 + (1.0 / q)) * self.dotS2L
        Seff2 = Seff * Seff

        self.Seff = Seff
        self.Seff2 = Seff2

        # Initial total spin, S = S1 + S2
        S0 = S1v + S2v

        # Cache total spin in the precession struct
        self.S_0 = S0

        # Initial total angular momentum, J = L + S1 + S2
        self.J_0 = self.L_0 + self.S_0

        # Norm of total initial spin
        self.S_0_norm = np.linalg.norm(S0)
        self.S_0_norm_2 = self.S_0_norm * self.S_0_norm

        # Norm of orbital and total angular momenta
        self.L_0_norm = np.linalg.norm(self.L_0)
        self.J_0_norm = np.linalg.norm(self.J_0)

        L0norm = self.L_0_norm
        J0norm = self.J_0_norm

        # Useful powers
        self.S_0_norm_2 = self.S_0_norm * self.S_0_norm
        self.J_0_norm_2 = self.J_0_norm * self.J_0_norm
        self.L_0_norm_2 = self.L_0_norm * self.L_0_norm

        #  Get roots to S^2 equation : S^2_+, S^2_-, S^2_3
        #         vroots.x = A1 = S_{3}^2
        #         vroots.y = A2 = S_{-}^2
        #         vroots.z = A3 = S_{+}^2

        self.S32, self.Smi2, self.Spl2 = self.Roots_MSA(self.L_0_norm, self.J_0_norm)

        # S^2_+ + S^2_-
        self.Spl2pSmi2 = self.Spl2 + self.Smi2

        # S^2_+ - S^2_-
        self.Spl2mSmi2 = self.Spl2 - self.Smi2

        # S_+ and S_-
        self.Spl = np.sqrt(self.Spl2)
        self.Smi = np.sqrt(self.Smi2)

        # Eq. 45 of PRD 95, 104004, (2017), arXiv:1703.03967, set from initial conditions
        self.SAv2 = 0.5 * self.Spl2pSmi2
        self.SAv = np.sqrt(self.SAv2)
        self.invSAv2 = 1.0 / self.SAv2
        self.invSAv = 1.0 / self.SAv

        # c_1 is determined by Eq. 41 of PRD, 95, 104004, (2017), arXiv:1703.03967
        c_1 = 0.5 * (J0norm * J0norm - L0norm * L0norm - self.SAv2) / self.L_0_norm * eta
        c1_2 = c_1 * c_1

        # Useful powers and combinations of c_1
        self.c1 = c_1
        self.c12 = c_1 * c_1
        self.c1_over_eta = c_1 / eta

        # Average spin couplings over one precession cycle: A9 - A14 of arXiv:1703.03967
        omqsq = (1.0 - q) * (1.0 - q) + 1e-16
        omq2 = (1.0 - q * q) + 1e-16

        # Precession averaged spin couplings, Eq. A9 - A14 of arXiv:1703.03967, note that we only use the initial values
        self.S1L_pav = (c_1 * (1.0 + q) - q * eta * Seff) / (eta * omq2)
        self.S2L_pav = -q * (c_1 * (1.0 + q) - eta * Seff) / (eta * omq2)
        self.S1S2_pav = 0.5 * self.SAv2 - 0.5 * (self.S1_norm_2 + self.S2_norm_2)
        self.S1Lsq_pav = (self.S1L_pav * self.S1L_pav) + ((self.Spl2mSmi2) * (self.Spl2mSmi2) * self.v_0_2) / (32.0 * eta2 * omqsq)
        self.S2Lsq_pav = (self.S2L_pav * self.S2L_pav) + (q * q * (self.Spl2mSmi2) * (self.Spl2mSmi2) * self.v_0_2) / (32.0 * eta2 * omqsq)
        self.S1LS2L_pav = self.S1L_pav * self.S2L_pav - q * (self.Spl2mSmi2) * (self.Spl2mSmi2) * self.v_0_2 / (32.0 * eta2 * omqsq)

        # Spin couplings in arXiv:1703.03967
        self.beta3 = ((113.0 / 12.0) + (25.0 / 4.0) * (m2 / m1)) * self.S1L_pav + ((113.0 / 12.0) + (25.0 / 4.0) * (m1 / m2)) * self.S2L_pav

        self.beta5 = (((31319.0 / 1008.0) - (1159.0 / 24.0) * eta) + (m2 / m1) * ((809.0 / 84) - (281.0 / 8.0) * eta)) * self.S1L_pav + (
            ((31319.0 / 1008.0) - (1159.0 / 24.0) * eta) + (m1 / m2) * ((809.0 / 84) - (281.0 / 8.0) * eta)
        ) * self.S2L_pav

        self.beta6 = LAL_PI * (((75.0 / 2.0) + (151.0 / 6.0) * (m2 / m1)) * self.S1L_pav + ((75.0 / 2.0) + (151.0 / 6.0) * (m1 / m2)) * self.S2L_pav)

        self.beta7 = (
            ((130325.0 / 756) - (796069.0 / 2016) * eta + (100019.0 / 864.0) * eta2)
            + (m2 / m1) * ((1195759.0 / 18144) - (257023.0 / 1008.0) * eta + (2903 / 32.0) * eta2) * self.S1L_pav
            + ((130325.0 / 756) - (796069.0 / 2016) * eta + (100019.0 / 864.0) * eta2)
            + (m1 / m2) * ((1195759.0 / 18144) - (257023.0 / 1008.0) * eta + (2903 / 32.0) * eta2) * self.S2L_pav
        )

        self.sigma4 = (
            (1.0 / mu) * ((247.0 / 48.0) * self.S1S2_pav - (721.0 / 48.0) * self.S1L_pav * self.S2L_pav)
            + (1.0 / (m1 * m1)) * ((233.0 / 96.0) * self.S1_norm_2 - (719.0 / 96.0) * self.S1Lsq_pav)
            + (1.0 / (m2 * m2)) * ((233.0 / 96.0) * self.S2_norm_2 - (719.0 / 96.0) * self.S2Lsq_pav)
        )

        # Compute PN coefficients using precession-averaged spin couplings
        self.a0 = 96.0 * eta / 5.0

        # These are all normalized by a factor of a0
        self.a2 = -(743.0 / 336.0) - (11.0 / 4.0) * eta
        self.a3 = 4.0 * LAL_PI - self.beta3
        self.a4 = (34103.0 / 18144.0) + (13661.0 / 2016.0) * eta + (59.0 / 18.0) * eta2 - self.sigma4
        self.a5 = -(4159.0 / 672.0) * LAL_PI - (189.0 / 8.0) * LAL_PI * eta - self.beta5
        self.a6 = (
            (16447322263.0 / 139708800.0)
            + (16.0 / 3.0) * LAL_PI * LAL_PI
            - (856.0 / 105) * np.log(16.0)
            - (1712.0 / 105.0) * LAL_GAMMA
            - self.beta6
            + eta * ((451.0 / 48) * LAL_PI * LAL_PI - (56198689.0 / 217728.0))
            + eta2 * (541.0 / 896.0)
            - eta3 * (5605.0 / 2592.0)
        )
        self.a7 = -(4415.0 / 4032.0) * LAL_PI + (358675.0 / 6048.0) * LAL_PI * eta + (91495.0 / 1512.0) * LAL_PI * eta2 - self.beta7

        # Coefficients are weighted by an additional factor of a_0
        self.a2 *= self.a0
        self.a3 *= self.a0
        self.a4 *= self.a0
        self.a5 *= self.a0
        self.a6 *= self.a0
        self.a7 *= self.a0

        # For versions 222 and 223, we compute PN coefficients using initial spin couplings, as per LALSimInspiralFDPrecAngles_internals.c
        if pflag == 222 or pflag == 223:
            self.a0 = eta * domegadt_constants_NS[0]
            self.a2 = eta * (domegadt_constants_NS[1] + eta * (domegadt_constants_NS[2]))
            self.a3 = eta * (domegadt_constants_NS[3] + self.Get_PN_beta(domegadt_constants_SO[0], domegadt_constants_SO[1]))
            self.a4 = eta * (
                domegadt_constants_NS[4]
                + eta * (domegadt_constants_NS[5] + eta * (domegadt_constants_NS[6]))
                + self.Get_PN_sigma(domegadt_constants_SS[0], domegadt_constants_SS[1])
                + self.Get_PN_tau(domegadt_constants_SS[2], domegadt_constants_SS[3])
            )
            self.a5 = eta * (
                domegadt_constants_NS[7]
                + eta * (domegadt_constants_NS[8])
                + self.Get_PN_beta(
                    (domegadt_constants_SO[2] + eta * (domegadt_constants_SO[3])), (domegadt_constants_SO[4] + eta * (domegadt_constants_SO[5]))
                )
            )

        # Useful powers of a_0
        self.a0_2 = self.a0 * self.a0
        self.a0_3 = self.a0_2 * self.a0
        self.a2_2 = self.a2 * self.a2

        # Calculate g coefficients as in Appendix A of Chatziioannou et al, PRD, 95, 104004, (2017), arXiv:1703.03967.
        # These constants are used in TaylorT2 where domega/dt is expressed as an inverse polynomial

        self.g0 = 1.0 / self.a0

        # Eq. A2 (1703.03967)
        self.g2 = -(self.a2 / self.a0_2)

        # Eq. A3 (1703.03967)
        self.g3 = -(self.a3 / self.a0_2)

        # Eq.A4 (1703.03967)
        self.g4 = -(self.a4 * self.a0 - self.a2_2) / self.a0_3

        # Eq. A5 (1703.03967)
        self.g5 = -(self.a5 * self.a0 - 2.0 * self.a3 * self.a2) / self.a0_3

        # Useful powers of delta
        delta = self.delta_qq
        delta2 = delta * delta
        delta3 = delta * delta2
        delta4 = delta * delta3

        # These are the phase coefficients of Eq. 51 of PRD, 95, 104004, (2017), arXiv:1703.03967
        self.psi0 = 0.0
        self.psi1 = 0.0
        self.psi2 = 0.0

        # \psi_1 is defined in Eq. C1 of Appendix C in PRD, 95, 104004, (2017), arXiv:1703.03967
        self.psi1 = 3.0 * (2.0 * eta2 * Seff - c_1) / (eta * delta2)

        c_1_over_nu = self.c1_over_eta
        c_1_over_nu_2 = c_1_over_nu * c_1_over_nu
        one_p_q_sq = (1.0 + q) * (1.0 + q)
        Seff_2 = Seff * Seff
        q_2 = q * q
        one_m_q_sq = (1.0 - q) * (1.0 - q)
        one_m_q2_2 = (1.0 - q_2) * (1.0 - q_2)
        one_m_q_4 = one_m_q_sq * one_m_q_sq

        #  This implements the Delta term as in LALSimInspiralFDPrecAngles.c
        #    c.f. https:#git.ligo.org/lscsoft/lalsuite/-/blob/master/lalsimulation/lib/LALSimInspiralFDPrecAngles_internals.c#L145

        if pflag == 222 or pflag == 223:
            Del1 = 4.0 * c_1_over_nu_2 * one_p_q_sq
            Del2 = 8.0 * c_1_over_nu * q * (1.0 + q) * Seff
            Del3 = 4.0 * (one_m_q2_2 * self.S1_norm_2 - q_2 * Seff_2)
            Del4 = 4.0 * c_1_over_nu_2 * q_2 * one_p_q_sq
            Del5 = 8.0 * c_1_over_nu * q_2 * (1.0 + q) * Seff
            Del6 = 4.0 * (one_m_q2_2 * self.S2_norm_2 - q_2 * Seff_2)
            self.Delta = np.sqrt(abs((Del1 - Del2 - Del3) * (Del4 - Del5 - Del6)))
        else:
            # Coefficients of \Delta as defined in Eq. C3 of Appendix C in PRD, 95, 104004, (2017), arXiv:1703.03967.
            term1 = c1_2 * eta / (q * delta4)
            term2 = -2.0 * c_1 * eta3 * (1.0 + q) * Seff / (q * delta4)
            term3 = -eta2 * (delta2 * self.S1_norm_2 - eta2 * Seff2) / delta4
            # Is this 1) (c1_2 * q * eta / delta4) or 2) c1_2*eta2/delta4?
            #     - In paper.pdf, the expression 1) is used.
            # Using eta^2 leads to higher frequency oscillations, use q * eta
            term4 = c1_2 * eta * q / delta4
            term5 = -2.0 * c_1 * eta3 * (1.0 + q) * Seff / delta4
            term6 = -eta2 * (delta2 * self.S2_norm_2 - eta2 * Seff2) / delta4

            # \Delta as in Eq. C3 of Appendix C in PRD, 95, 104004, (2017)
            self.Delta = np.sqrt(np.abs((term1 + term2 + term3) * (term4 + term5 + term6)))

        #  This implements the Delta term as in LALSimInspiralFDPrecAngles.c
        #    c.f. https:#git.ligo.org/lscsoft/lalsuite/-/blob/master/lalsimulation/lib/LALSimInspiralFDPrecAngles_internals.c#L160

        if pflag == 222 or pflag == 223:
            u1 = 3.0 * self.g2 / self.g0
            u2 = 0.75 * one_p_q_sq / one_m_q_4
            u3 = -20.0 * c_1_over_nu_2 * q_2 * one_p_q_sq
            u4 = 2.0 * one_m_q2_2 * (q * (2.0 + q) * self.S1_norm_2 + (1.0 + 2.0 * q) * self.S2_norm_2 - 2.0 * q * self.SAv2)
            u5 = 2.0 * q_2 * (7.0 + 6.0 * q + 7.0 * q_2) * 2.0 * c_1_over_nu * Seff
            u6 = 2.0 * q_2 * (3.0 + 4.0 * q + 3.0 * q_2) * Seff_2
            u7 = q * self.Delta

            # Eq. C2 (1703.03967)
            self.psi2 = u1 + u2 * (u3 + u4 + u5 - u6 + u7)
        else:
            # \psi_2 is defined in Eq. C2 of Appendix C in PRD, 95, 104004, (2017). Here we implement system of equations as in paper.pdf
            term1 = 3.0 * self.g2 / self.g0

            # q^2 or no q^2 in term2? Consensus on retaining q^2 term: https:#git.ligo.org/waveforms/reviews/phenompv3hm/issues/7
            term2 = 3.0 * q * q / (2.0 * eta3)
            term3 = 2.0 * self.Delta
            term4 = -2.0 * eta2 * self.SAv2 / delta2
            term5 = -10.0 * eta * c1_2 / delta4
            term6 = 2.0 * eta2 * (7.0 + 6.0 * q + 7.0 * q * q) * c_1 * Seff / (omqsq * delta2)
            term7 = -eta3 * (3.0 + 4.0 * q + 3.0 * q * q) * Seff2 / (omqsq * delta2)
            term8 = eta * (q * (2.0 + q) * self.S1_norm_2 + (1.0 + 2.0 * q) * self.S2_norm_2) / (omqsq)

            # \psi_2, C2 of Appendix C of PRD, 95, 104004, (2017)
            self.psi2 = term1 + term2 * (term3 + term4 + term5 + term6 + term7 + term8)

        # Eq. D1 of PRD, 95, 104004, (2017), arXiv:1703.03967
        Rm = self.Spl2 - self.Smi2
        Rm_2 = Rm * Rm

        # Eq. D2 and D3 Appendix D of PRD, 95, 104004, (2017), arXiv:1703.03967
        cp_v = self.Spl2 * eta2 - c1_2
        cm = self.Smi2 * eta2 - c1_2

        # Check if cm goes negative, this is likely pathological. If so, set MSA_ERROR to 1, so that waveform generator can handle the error approriately
        # if(cm < 0.0)
        # {
        #   self.MSA_ERROR = 1
        #   XLAL_PRINT_ERROR("Error, coefficient cm = %.16f, which is negative and likely to be pathological. Triggering MSA failure.\n",cm)
        # }

        # fabs is here to help enforce positive definite cpcm
        cpcm = np.abs(cp_v * cm)
        sqrt_cpcm = np.sqrt(cpcm)

        # Eq. D4 in PRD, 95, 104004, (2017), arXiv:1703.03967  Note difference to published version.
        a1dD = 0.5 + 0.75 / eta

        # Eq. D5 in PRD, 95, 104004, (2017), arXiv:1703.03967
        a2dD = -0.75 * Seff / eta

        # Eq. E3 in PRD, 95, 104004, (2017), arXiv:1703.03967  Note that this is Rm * D2
        D2RmSq = (cp_v - sqrt_cpcm) / eta2

        # Eq. E4 in PRD, 95, 104004, (2017), arXiv:1703.03967  Note that this is Rm^2 * D4
        D4RmSq = -0.5 * Rm * sqrt_cpcm / eta2 - cp_v / eta4 * (sqrt_cpcm - cp_v)

        S0m = self.S1_norm_2 - self.S2_norm_2

        # Difference of spin norms squared, as used in Eq. D6 of PRD, 95, 104004, (2017), arXiv:1703.03967
        aw = -3.0 * (1.0 + q) / q * (2.0 * (1.0 + q) * eta2 * Seff * c_1 - (1.0 + q) * c1_2 + (1.0 - q) * eta2 * S0m)
        cw = 3.0 / 32.0 / eta * Rm_2
        dw = 4.0 * cp_v - 4.0 * D2RmSq * eta2
        hw = -2.0 * (2.0 * D2RmSq - Rm) * c_1
        fw = Rm * D2RmSq - D4RmSq - 0.25 * Rm_2

        adD = aw / dw
        hdD = hw / dw
        cdD = cw / dw
        fdD = fw / dw

        gw = 3.0 / 16.0 / eta2 / eta * Rm_2 * (c_1 - eta2 * Seff)
        gdD = gw / dw

        # Useful powers of the coefficients
        hdD_2 = hdD * hdD
        adDfdD = adD * fdD
        adDfdDhdD = adDfdD * hdD
        adDhdD_2 = adD * hdD_2

        # Eq. D10 in PRD, 95, 104004, (2017), arXiv:1703.03967
        self.Omegaz0 = a1dD + adD

        # Eq. D11 in PRD, 95, 104004, (2017), arXiv:1703.03967
        self.Omegaz1 = a2dD - adD * Seff - adD * hdD

        # Eq. D12 in PRD, 95, 104004, (2017), arXiv:1703.03967
        self.Omegaz2 = adD * hdD * Seff + cdD - adD * fdD + adD * hdD_2

        # Eq. D13 in PRD, 95, 104004, (2017), arXiv:1703.03967
        self.Omegaz3 = (adDfdD - cdD - adDhdD_2) * (Seff + hdD) + adDfdDhdD

        # Eq. D14 in PRD, 95, 104004, (2017), arXiv:1703.03967
        self.Omegaz4 = (cdD + adDhdD_2 - 2.0 * adDfdD) * (hdD * Seff + hdD_2 - fdD) - adD * fdD * fdD

        # Eq. D15 in PRD, 95, 104004, (2017), arXiv:1703.03967
        self.Omegaz5 = (
            (cdD - adDfdD + adDhdD_2) * fdD * (Seff + 2.0 * hdD) - (cdD + adDhdD_2 - 2.0 * adDfdD) * hdD_2 * (Seff + hdD) - adDfdD * fdD * hdD
        )

        # If Omegaz5 > 1000, this is larger than we expect and the system may be pathological.
        # - Set MSA_ERROR = 1 to trigger an error
        if np.abs(self.Omegaz5) > 1000.0:
            self.MSA_ERROR = 1
            raise RuntimeError(
                "Warning, |Omegaz5| = {self.Omegaz:%.16f}, which is larger than expected and may be pathological. Triggering MSA failure."
            )

        g0 = self.g0

        # Coefficients of Eq. 65, as defined in Equations D16 - D21 of PRD, 95, 104004, (2017), arXiv:1703.03967
        self.Omegaz0_coeff = 3.0 * g0 * self.Omegaz0
        self.Omegaz1_coeff = 3.0 * g0 * self.Omegaz1
        self.Omegaz2_coeff = 3.0 * (g0 * self.Omegaz2 + self.g2 * self.Omegaz0)
        self.Omegaz3_coeff = 3.0 * (g0 * self.Omegaz3 + self.g2 * self.Omegaz1 + self.g3 * self.Omegaz0)
        self.Omegaz4_coeff = 3.0 * (g0 * self.Omegaz4 + self.g2 * self.Omegaz2 + self.g3 * self.Omegaz1 + self.g4 * self.Omegaz0)
        self.Omegaz5_coeff = 3.0 * (
            g0 * self.Omegaz5 + self.g2 * self.Omegaz3 + self.g3 * self.Omegaz2 + self.g4 * self.Omegaz1 + self.g5 * self.Omegaz0
        )

        # Coefficients of zeta: in Appendix E of PRD, 95, 104004, (2017), arXiv:1703.03967
        c1oveta2 = c_1 / eta2
        self.Omegazeta0 = self.Omegaz0
        self.Omegazeta1 = self.Omegaz1 + self.Omegaz0 * c1oveta2
        self.Omegazeta2 = self.Omegaz2 + self.Omegaz1 * c1oveta2
        self.Omegazeta3 = self.Omegaz3 + self.Omegaz2 * c1oveta2 + gdD
        self.Omegazeta4 = self.Omegaz4 + self.Omegaz3 * c1oveta2 - gdD * Seff - gdD * hdD
        self.Omegazeta5 = self.Omegaz5 + self.Omegaz4 * c1oveta2 + gdD * hdD * Seff + gdD * (hdD_2 - fdD)

        self.Omegazeta0_coeff = -self.g0 * self.Omegazeta0
        self.Omegazeta1_coeff = -1.5 * self.g0 * self.Omegazeta1
        self.Omegazeta2_coeff = -3.0 * (self.g0 * self.Omegazeta2 + self.g2 * self.Omegazeta0)
        self.Omegazeta3_coeff = 3.0 * (self.g0 * self.Omegazeta3 + self.g2 * self.Omegazeta1 + self.g3 * self.Omegazeta0)
        self.Omegazeta4_coeff = 3.0 * (self.g0 * self.Omegazeta4 + self.g2 * self.Omegazeta2 + self.g3 * self.Omegazeta1 + self.g4 * self.Omegazeta0)
        self.Omegazeta5_coeff = 1.5 * (
            self.g0 * self.Omegazeta5 + self.g2 * self.Omegazeta3 + self.g3 * self.Omegazeta2 + self.g4 * self.Omegazeta1 + self.g5 * self.Omegazeta0
        )

        # Expansion order of corrections to retain
        # Generate all orders
        if ExpansionOrder == -1:
            pass
        elif ExpansionOrder == 1:
            self.Omegaz1_coeff = 0.0
            self.Omegazeta1_coeff = 0.0
        elif ExpansionOrder == 2:
            self.Omegaz2_coeff = 0.0
            self.Omegazeta2_coeff = 0.0
        elif ExpansionOrder == 3:
            self.Omegaz3_coeff = 0.0
            self.Omegazeta3_coeff = 0.0
        elif ExpansionOrder == 4:
            self.Omegaz4_coeff = 0.0
            self.Omegazeta4_coeff = 0.0
        elif ExpansionOrder == 5:
            self.Omegaz5_coeff = 0.0
            self.Omegazeta5_coeff = 0.0
        else:
            raise SyntaxError(
                f"Expansion order for MSA corrections = {ExpansionOrder} not recognized. Default is 5. Allowed values are: [-1,1,2,3,4,5]."
            )

        # Get psi0 term
        psi_of_v0 = 0.0
        mm = 0.0
        tmpB = 0.0
        volume_element = 0.0
        vol_sign = 0.0

        # Tolerance chosen to be consistent with implementation in LALSimInspiralFDPrecAngles
        if abs(self.Smi2 - self.Spl2) < 1.0e-5:
            self.psi0 = 0.0
        else:
            # mm      = np.sqrt( (self.Smi2 - self.Spl2) / (self.S32 - self.Spl2) ) # The ellipkinc and gsl functions difer in the m(=k^2) definition
            mm = (self.Smi2 - self.Spl2) / (self.S32 - self.Spl2)
            tmpB = (self.S_0_norm * self.S_0_norm - self.Spl2) / (self.Smi2 - self.Spl2)

            volume_element = np.dot(np.cross(L_0, S1v), S2v)
            # vol_sign        = (volume_element > 0) - (volume_element < 0)
            vol_sign = np.copysign(1, volume_element)  # equivalent as long as volume_element !=0

            psi_of_v0 = self.psiofv(self.v_0, self.v_0_2, 0.0, self.psi1, self.psi2)

            if tmpB < 0.0 or tmpB > 1.0:
                if tmpB > 1.0 and (tmpB - 1.0) < 0.00001:
                    # self.psi0 = gsl_sf_ellint_F(np.arcsin(vol_sign) , mm, GSL_PREC_DOUBLE ) - psi_of_v0
                    self.psi0 = ellipkinc(np.arcsin(vol_sign), mm) - psi_of_v0
                if tmpB < 0.0 and tmpB > -0.00001:
                    self.psi0 = ellipkinc(0.0, mm) - psi_of_v0
            else:
                self.psi0 = ellipkinc(np.arcsin(vol_sign * np.sqrt(tmpB)), mm) - psi_of_v0

        vMSA = [0.0, 0.0, 0.0]

        if abs(self.Spl2 - self.Smi2) > 1.0e-5:
            vMSA = self.MSA_Corrections(self.v_0, self.v_0 * self.v_0, self.L_0_norm, self.J_0_norm, self.Spl, self.Spl2, self.Smi2, self.S32)

        # Initial \phi_z
        self.phiz_0 = 0.0
        phiz_0 = self.phiz_MSA(self.v_0, 1 / self.v_0, 1 / self.v_0_2, self.J_0_norm)

        # Initial \zeta
        self.zeta_0 = 0.0
        zeta_0 = self.zeta_MSA(self.v_0, self.v_0_2, 1 / self.v_0, 1 / self.v_0_2)

        self.phiz_0 = -phiz_0 - vMSA[0]
        self.zeta_0 = -zeta_0 - vMSA[1]

    def Get_PN_beta(self, a, b):
        """
        Compute PN spin-orbit couplings.
        """
        return self.dotS1L * (a + b * self.qq) + self.dotS2L * (a + b / self.qq)

    def Get_PN_sigma(self, a, b):
        """
        Compute PN spin-spin couplings.
        """
        return self.inveta * (a * self.dotS1S2 - b * self.dotS1L * self.dotS2L)

    def Get_PN_tau(self, a, b):
        """
        Compute PN spin-spin couplings.
        """
        return (
            self.qq * ((self.S1_norm_2 * a) - b * self.dotS1L * self.dotS1L) + (a * self.S2_norm_2 - b * self.dotS2L * self.dotS2L) / self.qq
        ) / self.eta

    def Roots_MSA(self, LNorm, JNorm):
        r"""
        Solve for the roots of Eq 21 :cite:`Katerina_2017`.

        Roots for :math:`\frac{d S^2}{d t^2} = -A^2 (S^2 -S_+^2)(S^2 - S_-^2)(S^2 - S_3^2)`.

        Returns
        -------
        Tuple with 3 floats or 3 1D ndarrays
            :math:`S_+^2`, :math:`S_-^2` and :math:`S_3^2`.

        """

        # Determine if single value or array case
        if np.isscalar(LNorm):
            xp = np
            array = False
        else:
            xp = self.xp
            array = True

        tmp1 = 0.0
        tmp2 = 0.0
        tmp3 = 0.0
        tmp4 = 0.0
        tmp5 = 0.0
        tmp6 = 0.0

        B, C, D = self.Spin_Evolution_Coefficients_MSA(LNorm, JNorm)

        S1Norm2 = self.S1_norm_2
        S2Norm2 = self.S2_norm_2

        S0Norm2 = self.S_0_norm_2

        B2 = B * B
        B3 = B2 * B
        BC = B * C

        p = C - B2 / 3
        qc = (2.0 / 27.0) * B3 - BC / 3.0 + D

        sqrtarg = xp.sqrt(-p / 3.0)
        acosarg = 1.5 * qc / p / sqrtarg

        # Make sure that acosarg is appropriately bounded
        if array:
            acosarg[acosarg < -1] = -1
            acosarg[acosarg > 1] = 1
        else:
            if acosarg < -1:
                acosarg = -1
            if acosarg > 1:
                acosarg = +1
        theta = xp.arccos(acosarg) / 3.0
        cos_theta = xp.cos(theta)

        dotS1Ln = self.dotS1Ln
        dotS2Ln = self.dotS2Ln

        # Check for bad values
        # Array case
        if array:
            if (dotS1Ln == 1) or (dotS2Ln == 1) or (dotS1Ln == -1) or (dotS2Ln == -1) or (S1Norm2 == 1) or (S2Norm2 == 0):
                S32 = xp.zeros_like(theta)
                Smi2 = xp.full(len(theta), S0Norm2)
                # Add a numerical perturbation to prevent azimuthal precession angle from diverging.
                Spl2 = Smi2 + 1e-9
                return S32, Smi2, Spl2

            # Get positions in array with NaNs
            mask = xp.isnan(theta) | xp.isnan(sqrtarg)

        # Single value case
        elif (
            xp.isnan(theta)
            or xp.isnan(sqrtarg)
            or (dotS1Ln == 1)
            or (dotS2Ln == 1)
            or (dotS1Ln == -1)
            or (dotS2Ln == -1)
            or (S1Norm2 == 1)
            or (S2Norm2 == 0)
        ):
            S32 = 0.0
            Smi2 = S0Norm2
            Spl2 = Smi2 + 1e-9
            return S32, Smi2, Spl2

        LAL_TWOPI = 2 * np.pi
        # E.g. see discussion on elliptic functions in arXiv:0711.4064
        tmp1 = 2.0 * sqrtarg * np.cos(theta - 2.0 * LAL_TWOPI / 3.0) - B / 3.0
        tmp2 = 2.0 * sqrtarg * np.cos(theta - LAL_TWOPI / 3.0) - B / 3.0
        tmp3 = 2.0 * sqrtarg * cos_theta - B / 3.0

        # tmp4 will be the maximum of tmp1, tmp2, tmp3
        # tmp5 will be the minimum of tmp1, tmp2, tmp3
        # tmp6 will be the remaining root
        roots = xp.array([tmp1, tmp2, tmp3])
        pos_max = xp.argmax(roots, axis=0)
        pos_min = xp.argmin(roots, axis=0)
        pos_3 = xp.abs(pos_max + pos_min - 3)

        if array is True:
            column_index = xp.arange(len(pos_max))
            tmp4 = roots[pos_max, column_index]
            tmp5 = roots[pos_min, column_index]
            tmp6 = roots[pos_3, column_index]
        else:
            tmp4 = roots[pos_max]
            tmp5 = roots[pos_min]
            tmp6 = roots[pos_3]

        # When Spl2 ~ 0 to numerical roundoff then Smi2 can sometimes be ~ negative causing NaN's.
        # This occurs in a very limited portion of the parameter space where spins are ~ 0 to numerical roundoff.
        # We can circumvent by enforcing +ve definite behaviour when tmp4 ~ 0. Note that S32 can often be negative, this is fine.
        tmp4 = xp.abs(tmp4)
        tmp6 = xp.abs(tmp6)

        # Return the roots
        Spl2 = tmp4
        S32 = tmp5
        Smi2 = tmp6

        # Replace NaN cases for array case
        if array:
            S32 = replace_instances_with_value(S32, mask, 0, xp)
            Smi2 = replace_instances_with_value(Smi2, mask, S0Norm2, xp)
            # Add a numerical perturbation to prevent azimuthal precession angle from diverging.
            Spl2 = replace_instances_with_value(Spl2, mask, Smi2 + 1e-9, xp)

        return S32, Smi2, Spl2

    def Spin_Evolution_Coefficients_MSA(self, LNorm, JNorm):
        """
        Get coefficients for Eq 21 :cite:`Katerina_2017`.
        """

        # Total angular momenta: J = L + S1 + S2
        JNorm2 = JNorm * JNorm

        # Orbital angular momenta
        LNorm2 = LNorm * LNorm

        # Dimensionfull spin angular momenta
        S1Norm2 = self.S1_norm_2
        S2Norm2 = self.S2_norm_2

        q = self.qq
        eta = self.eta

        J2mL2 = JNorm2 - LNorm2
        J2mL2Sq = J2mL2 * J2mL2

        delta = self.delta_qq
        deltaSq = delta * delta

        # Note:
        # S_{eff} \equiv \xi = (1 + q)(S1.L) + (1 + 1/q)(S2.L)
        Seff = self.Seff

        # Note that we do not evaluate Eq. B1 here as it is v dependent whereas B, C and D are not

        # Set Eq. B2, B_coeff
        x = (LNorm2 + S1Norm2) * q + 2.0 * LNorm * Seff - 2.0 * JNorm2 - S1Norm2 - S2Norm2 + (LNorm2 + S2Norm2) / q

        # Set Eq. B3, C_coeff
        y = (
            J2mL2Sq
            - 2.0 * LNorm * Seff * J2mL2
            - 2.0 * ((1.0 - q) / q) * LNorm2 * (S1Norm2 - q * S2Norm2)
            + 4.0 * eta * LNorm2 * Seff * Seff
            - 2.0 * delta * (S1Norm2 - S2Norm2) * Seff * LNorm
            + 2.0 * ((1.0 - q) / q) * (q * S1Norm2 - S2Norm2) * JNorm2
        )

        # Set Eq. B4, D_coeff
        z = (
            ((1.0 - q) / q) * (S2Norm2 - q * S1Norm2) * J2mL2Sq
            + deltaSq * (S1Norm2 - S2Norm2) * (S1Norm2 - S2Norm2) * LNorm2 / eta
            + 2.0 * delta * LNorm * Seff * (S1Norm2 - S2Norm2) * J2mL2
        )

        return x, y, z
