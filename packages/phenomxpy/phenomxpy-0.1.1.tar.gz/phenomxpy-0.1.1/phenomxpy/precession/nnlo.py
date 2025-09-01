# Copyright (C) 2023  Cecilio García Quirós
"""
Next-to-next to leasing order Euler angles
"""

import numpy as np


class NNLO:
    """
    Class with extra methods for the NNLO angles to be added to ``pPrec``.
    """

    def set_NNLO_angles_coefficients(self):
        """
        Set PN coefficients for alpha and gamma.

        See Eqs. G9 :cite:`phenomxphm`.
        """

        m1, eta, delta = [self._pWF.m1, self._pWF.eta, self._pWF.delta]

        eta2 = eta * eta
        eta3 = eta * eta2
        eta4 = eta * eta3
        eta5 = eta * eta4
        eta6 = eta * eta5
        delta2 = delta * delta
        delta3 = delta * delta2

        m1_2 = m1 * m1
        m1_3 = m1 * m1_2
        m1_4 = m1 * m1_3
        m1_5 = m1 * m1_4
        m1_6 = m1 * m1_5
        m1_8 = m1_2 * m1_6

        chiL, chip = [self.chiL, self.chip]
        chip2 = chip * chip
        chiL2 = chiL * chiL

        # alpha coefficients Eq. G9a-e arxiv:2004.06503
        self.alpha1 = -35 / 192.0 + (5 * delta) / (64.0 * m1)

        self.alpha2 = ((15 * chiL * delta * m1) / 128.0 - (35 * chiL * m1_2) / 128.0) / eta

        self.alpha3 = (
            -5515 / 3072.0
            + eta * (-515 / 384.0 - (15 * delta2) / (256.0 * m1_2) + (175 * delta) / (256.0 * m1))
            + (4555 * delta) / (7168.0 * m1)
            + ((15 * chip2 * delta * m1_3) / 128.0 - (35 * chip2 * m1_4) / 128.0) / eta2
        )

        # This is the term proportional to log(w)
        self.alpha4L = (
            (5 * chiL * delta2) / 16.0
            - (5 * chiL * delta * m1) / 3.0
            + (2545 * chiL * m1_2) / 1152.0
            + ((-2035 * chiL * delta * m1) / 21504.0 + (2995 * chiL * m1_2) / 9216.0) / eta
            + ((5 * chiL * chip2 * delta * m1_5) / 128.0 - (35 * chiL * chip2 * m1_6) / 384.0) / eta3
            - (35 * np.pi) / 48.0
            + (5 * delta * np.pi) / (16.0 * m1)
        )

        self.alpha5 = (
            5
            * (
                -190512 * delta3 * eta6
                + 2268 * delta2 * eta3 * m1 * (eta2 * (323 + 784 * eta) + 336 * (25 * chiL2 + chip2) * m1_4)
                + 7
                * m1_3
                * (
                    8024297 * eta4
                    + 857412 * eta5
                    + 3080448 * eta6
                    + 143640 * chip2 * eta2 * m1_4
                    - 127008 * chip2 * (-4 * chiL2 + chip2) * m1_8
                    + 6048 * eta3 * ((2632 * chiL2 + 115 * chip2) * m1_4 - 672 * chiL * m1_2 * np.pi)
                )
                + 3
                * delta
                * m1_2
                * (
                    -5579177 * eta4
                    + 80136 * eta5
                    - 3845520 * eta6
                    + 146664 * chip2 * eta2 * m1_4
                    + 127008 * chip2 * (-4 * chiL2 + chip2) * m1_8
                    - 42336 * eta3 * ((726 * chiL2 + 29 * chip2) * m1_4 - 96 * chiL * m1_2 * np.pi)
                )
            )
        ) / (6.5028096e7 * eta4 * m1_3)

        self.alpha0 = np.pi - self.kappa
        self.alpha_offset = 0

        # Set PN coefficients for gamma=(-epsilon). Eq. G9f-j arxiv:2004.06503
        self.gamma1 = -(-35 / 192.0 + (5 * delta) / (64.0 * m1))

        self.gamma2 = -((15 * chiL * delta * m1) / 128.0 - (35 * chiL * m1_2) / 128.0) / eta

        self.gamma3 = -(
            -5515 / 3072.0 + eta * (-515 / 384.0 - (15 * delta2) / (256.0 * m1_2) + (175 * delta) / (256.0 * m1)) + (4555 * delta) / (7168.0 * m1)
        )

        # This term is proportional to log(w)
        self.gamma4L = -(
            (5 * chiL * delta2) / 16.0
            - (5 * chiL * delta * m1) / 3.0
            + (2545 * chiL * m1_2) / 1152.0
            + ((-2035 * chiL * delta * m1) / 21504.0 + (2995 * chiL * m1_2) / 9216.0) / eta
            - (35 * np.pi) / 48.0
            + (5 * delta * np.pi) / (16.0 * m1)
        )

        self.gamma5 = -(
            5
            * (
                -190512 * delta3 * eta3
                + 2268 * delta2 * m1 * (eta2 * (323 + 784 * eta) + 8400 * chiL2 * m1_4)
                - 3 * delta * m1_2 * (eta * (5579177 + 504 * eta * (-159 + 7630 * eta)) + 254016 * chiL * m1_2 * (121 * chiL * m1_2 - 16 * np.pi))
                + 7 * m1_3 * (eta * (8024297 + 36 * eta * (23817 + 85568 * eta)) + 338688 * chiL * m1_2 * (47 * chiL * m1_2 - 12 * np.pi))
            )
        ) / (6.5028096e7 * eta * m1_3)

        # Set angle offsets
        self.epsilon0 = self.phiJ_Sf - np.pi  # Same definition as alphaOff
        self.gamma_offset = 0

        self.alpha_offset, _, self.gamma_offset = self.compute_nnlo_angles(self.omegaRef)
        self.alpha_offset -= self.alphaOff
        self.gamma_offset += self.alphaOff

    def compute_nnlo_angles(self, omega, **kwargs):
        r"""
        Compute analytical NNLO angles alpha, cosbeta, gamma.

        Parameters
        ----------
        omega: float, 1D ndarray
            frequency evolution taken from the aligned-spin model.

        Returns
        -------
        Tuple with 3 1D ndarrays
            :math:`\alpha`, :math:`\cos \beta`, :math:`\gamma`
        """

        # Evaluate omega power series
        omega = 0.5 * omega
        omega_cbrt = self.xp.cbrt(omega)
        omega_cbrt2 = omega_cbrt * omega_cbrt
        logomega = self.xp.log(omega)

        # Evaluate alpha and gamma power series
        alpha = (
            self.alpha1 / omega
            + self.alpha2 / omega_cbrt2
            + self.alpha3 / omega_cbrt
            + self.alpha4L * logomega
            + self.alpha5 * omega_cbrt
            - self.alpha_offset
        )
        gamma = (
            self.gamma1 / omega
            + self.gamma2 / omega_cbrt2
            + self.gamma3 / omega_cbrt
            + self.gamma4L * logomega
            + self.gamma5 * omega_cbrt
            - self.gamma_offset
        )

        # Compute cosbeta from angular momentum and in-plane spin
        L = self.compute_angular_momentum(omega_cbrt)
        s = self.Sperp / (L + self.SL)
        s2 = s * s
        cosbeta = self.xp.copysign(1, L + self.SL) / (self.xp.sqrt(1 + s2))

        return alpha, cosbeta, gamma
