# Copyright (C) 2023  Cecilio García Quirós
"""
IMRPhenomTP
-----------

.. autoclass:: phenomxpy.phenomt.phenomtp.IMRPhenomTP
    :members:
    :private-members:
    :undoc-members:
    :show-inheritance:
    :noindex:

IMRPhenomTPHM
-------------

.. autoclass:: phenomxpy.phenomt.phenomtp.IMRPhenomTPHM
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
import math
from scipy.spatial.transform import Rotation

from .internals import pWFHM, pPhase
from .phenomt import _PhenomT, IMRPhenomTHM
from phenomxpy.utils import SpinWeightedSphericalHarmonic, rotate_by_polarization_angle, MasstoSecond
from phenomxpy.precession.precession import pPrec, numba_rotation, numba_global_rotation

import_error_quaternions = False
try:
    from quaternion import as_float_array
    from phenomxpy.precession.quaternion import from_euler_angles, from_frame, as_euler_angles, compute_ylms
except ImportError:
    import_error_quaternions = True
import_error_quaternions_gpu = False
try:
    import torch
    from pytorch3d.transforms import quaternion_invert, quaternion_multiply
except ImportError:
    import_error_quaternions_gpu = True


class IMRPhenomTPHM(_PhenomT):
    """
    Class for the IMRPhenomTPHM model :cite:`phenomtphm`.

    Precessing with subdominant modes in the co-precessing frame
    """

    @staticmethod
    def metadata():
        metadata = {
            "type": "precessing",
            "f_ref_spin": True,
            "modes": True,
            "polarizations": True,
            "implemented_domain": "time",
            "approximant": "IMRPhenomTPHM",
            "implementation": "",
            "conditioning_routines": "",
        }
        return metadata

    def __init__(self, **kwargs):

        # Set pWF struct
        self.pWF = pWFHM(mode=[2, 2], **kwargs)

        # Set pPrec struct.
        # This updates pWF.afinal_prec according to the final_spin_version, except for version 4 which is done next
        self.pPrec = pPrec(self.pWF, **kwargs)

        # Copy module for easier use
        self.xp = self.pPrec.xp

        # ONLY for NUMERICAL ANGLES
        if self.pPrec.prec_version == "numerical" and self.pPrec.final_spin_version == 4 and self.pPrec.input_afinal_prec is None:
            # Solve PN spin equations to obtain the final spin, recycle the evolved quantities later to compute the Euler angles

            pPhase22 = pPhase(self.pWF)  # Also computes tmin, tref
            self.pPrec._pPhase22 = pPhase22
            times = self.set_time_array(times=kwargs.get("times", None))

            # Forward Integration: from tref to t=0
            self.pPrec.forward_integration(times=times)

            # Compute final spin from last point (t=0) in the evolution
            self.pPrec.evolved_final_spin(self.pPrec.LNhatev, self.pPrec.S1ev, self.pPrec.S2ev)

        # Initialize co-precessing class
        self.phenTHM = IMRPhenomTHM(pWF_input=self.pWF, **kwargs)

        # Populate global pWF with values computed in co-precessing
        key = "22"
        if hasattr(self.pWF, "tmin") is False:
            self.pWF.tmin = self.phenTHM.phenT_classes[key].pWF.tmin
        if hasattr(self.pWF, "tref") is False:
            self.pWF.tref = self.phenTHM.phenT_classes[key].pWF.tref

        if self.pWF.delta_t > 0:
            # Set equispaced time array lengths
            if hasattr(self.pWF, "length") is False:
                self.pWF.length = self.phenTHM.phenT_classes[key].pWF.length
            if hasattr(self.pWF, "len_neg") is False:
                self.pWF.len_neg = self.phenTHM.phenT_classes[key].pWF.len_neg
            if hasattr(self.pWF, "len_pos") is False:
                self.pWF.len_pos = self.phenTHM.phenT_classes[key].pWF.len_pos

        # Check consistency time array with co-precessing
        if math.isclose(self.pWF.tmin, self.phenTHM.phenT_classes[key].pWF.tmin, rel_tol=1e-15) is False:
            raise AssertionError(f"Inconsistent tmin with co-precessing {self.pWF.tmin}!={self.phenTHM.phenT_classes[key].pWF.tmin}")
        if math.isclose(self.pWF.tref, self.phenTHM.phenT_classes[key].pWF.tref, rel_tol=1e-15) is False:
            raise AssertionError(f"Inconsistent tref with co-precessing {self.pWF.tref}!={self.phenTHM.phenT_classes[key].pWF.tref}")
        if self.pWF.delta_t > 0 and math.isclose(self.pWF.length, self.phenTHM.phenT_classes[key].pWF.length, rel_tol=1e-15) is False:
            raise AssertionError(f"Inconsistent length with co-precessing {self.pWF.length}!={self.phenTHM.phenT_classes[key].pWF.length}")

    def compute_euler_angles(self, times=None):
        r"""
        Compute Euler angles alpha, cosbeta, gamma for a time array.

        3 prescriptions supported:
            - NNLO
            - MSA
            - Numerical/SpinTaylor (default)

        Parameters
        ----------
        times: 1D ndarray
            Time array where to evaluate the angles. If ``None``, use equispaced grid ``self.times``.

        Returns
        -------
        Tuple with 3 1D ndarrays
            :math:`\\alpha(t)`, :math:`\cos(\\beta(t))`, :math:`\\gamma(t)`,
        """

        # Variable to decide if we need to evolve the orbit in the new time array (numerical angles only)
        new_times = True if times is not None else False

        # Set time array
        times = self.set_time_array(times=times)

        # Compute omega(t) in the time array
        omega = self.phenTHM.phenT_classes["22"].pPhase.imr_omega(times[times <= 0])

        ##########################
        #    NNLO - MSA ANGLES   #
        ##########################
        if self.pPrec.prec_version in ["nnlo", "msa"]:

            # Choose proper function to evaluate the angles: compute_nnlo_angles or compute_msa_angles
            euler_function = getattr(self.pPrec, "compute_" + self.pPrec.prec_version + "_angles")

            # Compute angles in time array up to mergeer t<=0
            alpha, cosbeta, gamma = euler_function(omega)

            # Values at t=0 for the ringdown attachment
            self.pPrec.omegaPeak = self.phenTHM.phenT_classes["22"].pPhase.omegaPeak
            self.pPrec.alphaRD0, self.pPrec.cosbetaRD0, self.pPrec.gammaRD0 = euler_function(self.pPrec.omegaPeak)

            # Angles for global rotation from J to L0
            self.pPrec.alphaJtoL0, self.pPrec.cosbetaJtoL0, self.pPrec.gammaJtoL0 = euler_function(self.pPrec.omegaRef)

            # Ringdown part
            alphaRD = self.pPrec.alphaRD0 + self.pPrec.EulerRDslope * times[times > 0]
            cosbetaRD = self.xp.full(len(times[times > 0]), self.pPrec.cosbetaRD0)
            gammaRD = self.pPrec.gammaRD0 - alphaRD * cosbetaRD + self.pPrec.alphaRD0 * self.pPrec.cosbetaRD0

            # Attach ringdown
            alpha = self.xp.concatenate((alpha, alphaRD))
            cosbeta = self.xp.concatenate((cosbeta, cosbetaRD))
            gamma = self.xp.concatenate((gamma, gammaRD))

        ##########################
        #    NUMERICAL ANGLES    #
        ##########################
        else:
            ###############################################
            #     FORWARD INTEGRATION: from tref to t=0   #
            ###############################################
            # The PN spin equations have not been yet evolved in the initialization of the class if final_spin_version = 4,
            # or a input_afinal_prec is given.
            # If that is not the case, we evolve them now from tref to merger (t=0)
            if self.pPrec.final_spin_version != 4 or self.pPrec.input_afinal_prec is not None or new_times:
                # Set pPhase22 if not already set
                if getattr(self, "_pPhase22", None) is None:
                    self.pPrec._pPhase22 = self.phenTHM.phenT_classes["22"].pPhase

                self.pPrec.forward_integration(times)

            #################################################
            #     BACKWARD INTEGRATION: from tref to tmin   #
            #################################################
            if self.pWF.tmin < self.pWF.tref:
                LNhatev, _ = self.pPrec.backward_integration(times)
            else:
                LNhatev = self.pPrec.LNhatev

            # Compute angles in the full time array (PN evolved + Ringdown attachment)
            alpha, cosbeta, gamma = self.pPrec.compute_numerical_angles(LNhatev, times)

        # Optionally store arrays.
        if self.pPrec.store_arrays is True:
            self.alpha, self.cosbeta, self.gamma = alpha, cosbeta, gamma

        return alpha, cosbeta, gamma

    def compute_quaternions(self, times=None):
        """
        Compute quaternions in time array to transform from L to L0 frame and align with the line-of-sight.

        For the NNLO and MSA prescriptions, the quaternions are computed from the Euler angles.

        For the numerical angles, the default option is to compute them directly from the evolution of the L frame (Z=LNhatev, X=E1ev, Y=ZxX).
        There is also the option to compute them from the Euler angles. But this involves more computations steps and potential losses of accuracy.

        Parameters
        ----------
        times: 1D ndarray
            Time array to compute quaternions for. If ``None``, use internal equispaced grid ``self.times``.
        torch_single_precision: bool
            If ``True``, use single precision for ``torch`` tensors, slightly faster.

        Returns
        -------
        (N, 4) ndarray
            Quaternions evaluated in time array.
        """

        torch_single_precision = self.pWF.extra_options.get("torch_single_precision", False)

        # Quaternion corresponding to the alignment with the line-of-sight
        qL02I0 = from_euler_angles((np.pi / 2 - self.pWF.phi_ref), np.cos(self.pWF.inclination), 0.0, xp=self.xp)

        ################################
        #     Quaternions from frame   #
        ################################
        # Only for numerical angles.
        # Skips euler angles computation, calculating the quaternions directly from L, E1 evolution
        if self.pPrec.prec_version == "numerical" and self.pPrec.quaternions_from == "frame":
            # Variable to decide if we need to evolve the orbit in the new time array (numerical angles only)
            new_times = True if times is not None else False

            # Set time array
            times = self.set_time_array(times=times)

            #################################################
            #     FORWARD INTEGRATION: from tref to t=0     #
            #################################################
            # PN spin equations have not been yet evolved if final_spin_version != 4,
            # or if the final spin is provided through input_afinal_prec. Do forward integration
            if self.pPrec.final_spin_version != 4 or self.pPrec.input_afinal_prec is not None or new_times:
                # Set pPhase22 if not already set
                if getattr(self, "_pPhase22", None) is None:
                    self.pPrec._pPhase22 = self.phenTHM.phenT_classes["22"].pPhase

                self.pPrec.forward_integration(times)

            #################################################
            #     BACKWARD INTEGRATION: from tref to tmin   #
            #################################################
            if self.pWF.tmin < self.pWF.tref:
                LNhatev, E1ev = self.pPrec.backward_integration(times)
            else:
                LNhatev = self.pPrec.LNhatev
                E1ev = self.pPrec.E1ev

            # Set axis of evolved frame
            X = E1ev
            Z = LNhatev
            Y = self.xp.cross(Z, X, axis=0)

            # Compute quaternions from evolved frame
            qtwist = from_frame(X, Y, Z, xp=self.xp)

            # Ringdown attachment
            # Need to transform to the J-frame where the Euler angles for the attachment are defined
            qL0toJ = from_euler_angles(-self.pPrec.kappa, np.cos(-self.pPrec.thetaJ_Sf), -self.pPrec.phiJ_Sf, minus_beta=True, xp=self.xp)

            if self.xp == np:
                alphaRD0, cosbetaRD0, gammaRD0 = as_euler_angles(as_float_array(qL0toJ * qtwist[-1]))
            else:
                dtype_torch = torch.float32 if torch_single_precision is True else torch.float64
                q1 = torch.tensor(qL0toJ, dtype=dtype_torch)
                q2 = torch.tensor(qtwist[-1], dtype=dtype_torch)
                alphaRD0, cosbetaRD0, gammaRD0 = as_euler_angles(cp.asarray(quaternion_multiply(q1, q2)))

            # Remove t=0 if it was added in forward_integration
            if self.pPrec.t0_added_to_array:
                qtwist = qtwist[:-1]

            RDtimes = times[times > 0]
            alphaRD = alphaRD0 + self.pPrec.EulerRDslope * RDtimes
            cosbetaRD = self.xp.full(len(alphaRD), cosbetaRD0)
            gammaRD = gammaRD0 - self.pPrec.EulerRDslope * cosbetaRD0 * RDtimes
            # These values will not coincide with the method from Euler angles, but the final rotation is consistent
            self.pPrec.alphaRD0 = alphaRD0
            self.pPrec.cosbetaRD0 = cosbetaRD0
            self.pPrec.gammaRD0 = gammaRD0

            if self.xp == np:
                # Quaternions from Euler angles in the RD attachment and convert them to L->L0
                qtwistRD = ~from_euler_angles(alphaRD, cosbetaRD, gammaRD) * qL0toJ

                # Attach RD part
                qtwist = np.append(~qtwist, qtwistRD)

                # Final quaternion
                qTot = as_float_array(qtwist * qL02I0)

            else:
                # Quaternions from Euler angles in the RD attachment and convert them to L->L0
                q1 = quaternion_invert(torch.tensor(from_euler_angles(alphaRD, cosbetaRD, gammaRD, xp=self.xp), dtype=dtype_torch))
                q2 = torch.tensor(qL0toJ, dtype=dtype_torch)
                qtwistRD = quaternion_multiply(q1, q2)

                # Attach RD part
                q1 = quaternion_invert(torch.tensor(qtwist, dtype=dtype_torch))
                qtwist = torch.cat((q1, qtwistRD), dim=0)

                # Final quaternion
                q2 = torch.tensor(qL02I0, dtype=dtype_torch)
                qTot = quaternion_multiply(qtwist, q2)
                qTot = cp.from_dlpack(torch.utils.dlpack.to_dlpack(qTot))

        ######################################
        #    Quaternions from Euler angles   #
        ######################################
        else:
            # Compute Euler angles
            alpha, cosbeta, gamma = self.compute_euler_angles(times=times)

            # Compute quaternions from Euler angles for each rotation
            qP2J = from_euler_angles(alpha, cosbeta, gamma, xp=self.xp)
            qJ2L0 = from_euler_angles(self.pPrec.alphaJtoL0, self.pPrec.cosbetaJtoL0, self.pPrec.gammaJtoL0, xp=self.xp)

            # Final quaternion
            # In CPU, quaternion is faster than pytorch. pytorch only for GPU
            if self.xp == np:
                qTot = as_float_array(~qP2J * qJ2L0 * qL02I0)
                self.qTot = qTot
            else:
                dtype_torch = torch.float32 if torch_single_precision is True else torch.float64
                qP2Jb = quaternion_invert(torch.tensor(qP2J, dtype=dtype_torch))
                qJ2L0b = torch.tensor(qJ2L0, dtype=dtype_torch)
                qL02I0b = torch.tensor(qL02I0, dtype=dtype_torch)
                qTot = quaternion_multiply(qP2Jb, quaternion_multiply(qJ2L0b, qL02I0b))
                qTot = cp.from_dlpack(torch.utils.dlpack.to_dlpack(qTot))

        return qTot

    def compute_CPmodes(self, times=None):
        """
        Compute co-precessing modes in a time array

        Return dictionary with the co-precessing hlms(t).

        """

        CPmodes, times = self.phenTHM.compute_hlms(times=times)

        if self.pPrec.store_arrays is True:
            self.CPmodes = CPmodes

        return CPmodes, times

    def compute_Jmodes(self, times=None):
        """
        Compute hlms(t) in the J-frame

        Return dictionary/array with the modes, depending if numba_rotation=False/True.

        """

        # Compute Euler angles
        alpha, cosbeta, gamma = self.compute_euler_angles(times=times)

        # Compute CPmodes
        CPmodes, times = self.compute_CPmodes(times=times)

        # Initialize Jmodes dictionary to zero
        Jmodes = {}
        n_inertial_modes = 0
        for l in range(2, self.phenTHM.lmax + 1):
            for m in range(-l, l + 1):
                n_inertial_modes = n_inertial_modes + 1
                mode_string = str(l) + str(m)
                Jmodes[mode_string] = self.xp.zeros(len(alpha), dtype=self.xp.cdouble)

        # Compute Wigner-d matrices for Euler angle rotations
        self.pPrec.set_exp_angle_powers(gamma, alpha)
        self.pPrec.WignerdMatrix(cosbeta, sign=1, lmax=self.phenTHM.lmax)

        # Rotation from CP to J frame
        # Rotation without numba: can use a dictionary to store the modes
        if self.pPrec.numba_rotation is False:
            for l in range(2, self.phenTHM.lmax + 1):
                for m in range(-l, l + 1):
                    Jmode = str(l) + str(m)
                    for mp in range(-l, l + 1):
                        comode = str(l) + str(mp)
                        if comode in CPmodes:
                            WignerD = self.pPrec.WignerDMatrix(l, mp, m)
                            Jmodes[Jmode] += WignerD * CPmodes[comode]

        # Rotation with numba: cannot handle dictionaries, use arrays
        else:
            CPmodes = self.xp.array(list(CPmodes.values()))
            Jmodes = self.xp.zeros((n_inertial_modes, len(alpha)), dtype=self.xp.cdouble)
            Jmodes = numba_rotation(
                self.phenTHM.lmax,
                Jmodes,
                CPmodes,
                self.pPrec.wignerdL2,
                self.pPrec.wignerdL3,
                self.pPrec.wignerdL4,
                self.pPrec.wignerdL5,
                self.pPrec.expAlphaPowers,
                self.pPrec.expGammaPowers,
                np.array(self.phenTHM.mode_array),
            )

        return Jmodes, times

    def compute_L0modes(self, times=None):
        """
        Compute hlms(t) in the L0-frame

        Return dictionary/array with the modes, depending if numba_rotation=False/True.

        """

        # Compute Jmodes
        Jmodes, times = self.compute_Jmodes(times=times)

        # Compute Wigner-d matrices for Euler angle rotation
        self.pPrec.set_exp_angle_powers(-self.pPrec.alphaJtoL0, -self.pPrec.gammaJtoL0)
        self.pPrec.WignerdMatrix(self.pPrec.cosbetaJtoL0, sign=-1, global_rotation=True, lmax=self.phenTHM.lmax)

        # Rotation from J to L0 frame
        # Rotation without numba: can use a dictionary to store the modes
        if self.pPrec.numba_rotation is False:
            # Get length of first value from the dict
            N = len(next(iter(Jmodes.values())))
            # Initialize L0modes to zero
            L0modes = {}
            for l in range(2, self.phenTHM.lmax + 1):
                for m in range(-l, l + 1):
                    mode_string = str(l) + str(m)
                    L0modes[mode_string] = self.xp.zeros(N, dtype=self.xp.cdouble)
            # Modes rotation
            for l in range(2, self.phenTHM.lmax + 1):
                for m in range(-l, l + 1):
                    L0mode = str(l) + str(m)
                    for mp in range(-l, l + 1):
                        Jmode = str(l) + str(mp)
                        WignerD = self.pPrec.WignerDMatrix(l, mp, m)
                        L0modes[L0mode] += WignerD * Jmodes[Jmode]

        # Rotation with numba: cannot handle dictionaries, use arrays
        else:
            L0modes = self.xp.zeros(Jmodes.shape, dtype=self.xp.cdouble)
            L0modes = numba_global_rotation(
                self.phenTHM.lmax,
                L0modes,
                Jmodes,
                self.pPrec.wignerdL2,
                self.pPrec.wignerdL3,
                self.pPrec.wignerdL4,
                self.pPrec.wignerdL5,
                self.pPrec.expAlphaPowers,
                self.pPrec.expGammaPowers,
            )

        return L0modes, times

    def compute_polarizations(self, times=None):
        """
        Compute polarizations hp(t), hc(t) in given time array. Equispaced one if ``times`` is ``None``.

        Parameters
        ----------
        times: 1D ndarray
            Time array where to evaluate the polarizations
        polarizations_from: {'L0modes', 'Jmodes', 'CPmodes'}
            Strategy to compute the polarizations that should return the same output.

                - LOmodes: method employed in LAL involving two rotations: CP->J, J->L0
                - Jmodes:  similar to PhenomX, rotate modes from CP->J and compute polarizations using theta_JN instead of inclination
                - CPmodes (default): use efficient method with quaternions from M. Boyle, Appendix B of :cite:`boyle2014`.

        use_wigner_from_quaternions: bool
            If ``False``, then use the method of seobnrv5.
        compute_CPmodes_at_once: bool
            Compute all the co-precessing modes at once, this is simpler but uses more memory.
            If False, compute one mode and add its contribution to the polarizations in a loop over modes
        compute_ylms_at_once: bool
            Same as for the CPmodes but for the Ylms time series.

        Returns
        -------
        Tuple with 2 1D ndarrays
            hp(t), hc(t) real arrays

        """

        # Read extra options
        polarizations_from = self.pWF.extra_options.get("polarizations_from", "CPmodes")
        compute_CPmodes_at_once = self.pWF.extra_options.get("compute_CPmodes_at_once", False)
        compute_ylms_at_once = self.pWF.extra_options.get("compute_ylms_at_once", True)
        use_wigner_from_quaternions = self.pWF.extra_options.get("use_wigner_from_quaternions", True)

        ####################################
        #    polarizations_from L0modes    #
        ####################################
        if polarizations_from == "L0modes":

            # Compute L0modes
            hlms, times = self.compute_L0modes(times=times)

            # Angles for the Ylms
            polar, azimuthal = self.pWF.inclination, np.pi / 2 - self.pWF.phi_ref

        ####################################
        #    polarizations_from Jmodes    #
        ####################################
        elif polarizations_from == "Jmodes":

            # Compute Jmodes
            hlms, times = self.compute_Jmodes(times=times)

            # Compute polar angles for Ylms
            N = [
                np.sin(self.pWF.inclination) * np.cos(np.pi / 2 - self.pWF.phi_ref),
                np.sin(self.pWF.inclination) * np.sin(np.pi / 2 - self.pWF.phi_ref),
                np.cos(self.pWF.inclination),
            ]
            r = Rotation.from_euler("zyz", [self.pPrec.gammaJtoL0, np.arccos(self.pPrec.cosbetaJtoL0), self.pPrec.alphaJtoL0], degrees=False)
            N_Jf = r.apply(N)
            polar, azimuthal = np.arccos(N_Jf[2]), np.arctan2(N_Jf[1], N_Jf[0])

            self.pPrec.J0x_Sf = self.pPrec._pWF.m1_2 * self.pPrec._pWF.s1[0] + self.pPrec._pWF.m2_2 * self.pPrec._pWF.s2[0]
            self.pPrec.J0y_Sf = self.pPrec._pWF.m1_2 * self.pPrec._pWF.s1[1] + self.pPrec._pWF.m2_2 * self.pPrec._pWF.s2[1]
            self.pPrec.J0z_Sf = self.pPrec._pWF.m1_2 * self.pPrec._pWF.s1[2] + self.pPrec._pWF.m2_2 * self.pPrec._pWF.s2[2] + self.pPrec.LRef
            J0 = [self.pPrec.J0x_Sf, self.pPrec.J0y_Sf, self.pPrec.J0z_Sf]
            J0_norm = np.linalg.norm(J0)

            J_L0 = r.inv().apply([0, 0, J0_norm])

            yN = np.cross(np.array([0, 0, 1]), N)
            yN /= np.linalg.norm(yN)
            xN = np.cross(yN, N)
            xN /= np.linalg.norm(xN)

            yNp = np.cross(J_L0, N)
            yNp /= np.linalg.norm(yNp)
            xNp = np.cross(yNp, N)
            xNp /= np.linalg.norm(xNp)

            # Eq. C22 arxiv:2004.06503
            self.pPrec.zeta = np.arctan2(np.dot(xN, yNp), np.dot(xN, xNp))

        ####################################
        #    polarizations_from CPmodes    #
        ####################################
        elif polarizations_from == "CPmodes":

            # This method requires the quaternions package to be installed
            if import_error_quaternions is True:
                raise ImportError("Error importing quaternions packages. Cannot use polarizations_from='CPmodes'")
            if self.xp == cp and import_error_quaternions_gpu is True:
                raise ImportError("Error importing quaternions packages for GPU version. Cannot use polarizations_from='CPmodes'")

            ############################
            #    Compute quaternions   #
            ############################
            qTot = self.compute_quaternions(times=times)

            ############################
            #   Ylms from quaternions  #
            ############################
            if compute_ylms_at_once:
                # If mode_array is not the default, then use custom_modes numba_rotation function
                if self.phenTHM.mode_array != self.phenTHM.default_mode_array and (self.pPrec.numba_rotation in ["default_modes", True]):
                    self.pPrec.numba_rotation = "custom_modes"

                Ylm, gammaTot = compute_ylms(
                    qTot, self.phenTHM.mode_array, use_wigner_from_quaternions, self.pPrec.numba_rotation, self.xp, self.phenTHM.lmax
                )

            ##################################
            #   Compute strain from CPmodes  #
            ##################################

            # Intialize strain
            strain = self.xp.zeros(len(qTot), dtype=complex)

            # Compute all CPmodes at once. Simple way, uses more memory
            if compute_CPmodes_at_once:
                # Compute co-precessing modes
                CPmodes, times = self.compute_CPmodes(times=times)

                # Loop over modes and add strain contribution
                for i, [l, m] in enumerate(self.phenTHM.mode_array):
                    mode = str(l) + str(m)
                    # Build strain
                    strain += Ylm[i] * CPmodes[mode]

            # Another option is to generate hlms one by one to save memory (default)
            else:
                cache = None
                modes_already_computed = []
                for idx, [l, m] in enumerate(self.phenTHM.mode_array):
                    if [l, m] not in modes_already_computed:
                        mode = str(l) + str(m)

                        # NOTE only valid for equatorial symmetry
                        # Skip the evaluation of the opposite mode by using symmetry
                        # marray_ylms is to compute the Ylms one by one to save memory
                        if m != 0 and [l, -m] in self.phenTHM.mode_array:
                            add_opposite_mode = True
                            marray_ylms = [[l, m], [l, -m]]
                        else:
                            add_opposite_mode = False
                            marray_ylms = [[l, m]]

                        modes_already_computed.append([l, -m])

                        # Compute hlm
                        key = str(l) + str(abs(m))
                        phen = self.phenTHM.phenT_classes[key]
                        if key == "22":
                            hlm, times, cache = phen.compute_hlm(times=times, return_cache=True)
                        else:
                            hlm, times = phen.compute_hlm(times=times, cache=cache)

                        # Apply equatorial symmetry for negative modes
                        if m < 0:
                            hlm = (-1) ** l * self.xp.conj(hlm)

                        # Compute Ylm if not computed all at once (this saves memory but it is slower)
                        if compute_ylms_at_once is False:
                            Ylm, gammaTot = compute_ylms(
                                qTot, marray_ylms, use_wigner_from_quaternions, self.pPrec.numba_rotation, self.xp, self.phenTHM.lmax
                            )
                            i, i_opposite = 0, 1

                        # All Ylms are already computed. Get proper indeces
                        else:
                            i = idx
                            # Find index in custom mode array for the opposite mode
                            if add_opposite_mode:
                                matches = np.all(np.array(self.phenTHM.mode_array) == [l, -m], axis=1)
                                i_opposite = np.where(matches)[0][0]

                        # Add mode contribution to strain
                        strain += Ylm[i] * hlm

                        # Add opposite mode. NOTE only valid for equatorial symmetry
                        if add_opposite_mode:
                            strain += Ylm[i_opposite] * (-1) ** l * self.xp.conj(hlm)

            # Correction needed for the seobnrv5 method. Eq.28 arxiv:2303.18046
            if use_wigner_from_quaternions is False:
                strain *= self.xp.exp(2j * gammaTot)

        # Option not supported for polarizations_from
        else:
            raise ValueError(
                f"polarizations_from={polarizations_from} not supported. Available options are CPmodes (default), L0modes (LAL) or Jmodes (PhenomX)"
            )

        ########################################
        #  Compute strain for Jmodes, L0modes  #
        ########################################
        # hlms is a dictionary or array depending if numba_rotation=False/True
        if polarizations_from != "CPmodes":
            # Use arrays for numba_rotation
            if self.pPrec.numba_rotation:
                L0list = []
                for l in range(2, self.phenTHM.lmax + 1):
                    for m in range(-l, l + 1):
                        L0list.append([l, m])
                strain = self.xp.zeros(len(hlms[0]), dtype=self.xp.cdouble)
                for idx in range(len(L0list)):
                    ell, emm = L0list[idx]
                    hlm = hlms[idx]
                    Ylm = SpinWeightedSphericalHarmonic(polar, azimuthal, ell, emm)
                    strain += hlm * Ylm

            # numba_rotation=False: use dictionaries
            else:
                keys = list(hlms.keys())
                strain = self.xp.zeros(len(hlms[keys[0]]), dtype=self.xp.cdouble)
                for key, hlm in hlms.items():
                    ell = int(key[0])
                    emm = int(key[1:])
                    Ylm = SpinWeightedSphericalHarmonic(polar, azimuthal, ell, emm)
                    strain += hlm * Ylm

            # Zeta correction for Jmodes. Eqs. D6-D7 arxiv:2004.06503
            if polarizations_from == "Jmodes":
                strain *= self.xp.exp(1j * self.pPrec.zeta * 2)

        ####################################
        #   Get polarizations from strain  #
        ####################################
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


class IMRPhenomTP(IMRPhenomTPHM):
    """
    Class for the IMRPhenomTP model :cite:`phenomtphm`.

    Precessing model with only the 22 mode in the co-precessing frame.

    Wrapper to the ``IMRPhenomTPHM`` class called with only the 22, 2-2 modes.
    """

    @staticmethod
    def metadata():
        metadata = {
            "type": "precessing",
            "f_ref_spin": True,
            "modes": True,
            "polarizations": True,
            "implemented_domain": "time",
            "approximant": "IMRPhenomTP",
            "implementation": "",
            "conditioning_routines": "",
        }
        return metadata

    def __init__(self, **kwargs):
        super().__init__(**kwargs, mode_array=[[2, 2], [2, -2]])
