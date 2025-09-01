# Copyright (C) 2023  Cecilio García Quirós
"""
Utility functions involving quaternions.
"""

import numpy as np
from numba import njit, prange
from quaternion import as_quat_array
from phenomxpy.utils import custom_swsh


def from_euler_angles(alpha, cosbeta, gamma, xp=np, minus_beta=False):
    """
    Adapted from `quaternion package <https://github.com/moble/quaternion>`_ of Michael Boyle

    We use cosbeta instead of beta to speed-up calculations.

    Assumes the Euler angles correspond to the quaternion R via

        R = exp(alpha*z/2) * exp(beta*y/2) * exp(gamma*z/2)

    The angles naturally must be in radians for this to make any sense.

    We assume beta [0, pi] => sin(beta/2) >= 0, since this is mostly the case.
    A minus sign is introduced in q1, q2 if minus_beta=True

    Parameters
    ----------
    alpha : float or array of floats
    cosbeta : float, or array of floats
    gamma : float, or array of floats

    Returns
    -------
    R : quaternion array
    """

    # Set up the output array
    R = xp.empty(xp.broadcast(alpha, cosbeta, gamma).shape + (4,), dtype=xp.double)

    cos_beta_half = xp.sqrt((1 + cosbeta) * 0.5)
    sin_beta_half = xp.sqrt((1 - cosbeta) * 0.5)

    # Flip sin(beta/2) if beta < 0
    if minus_beta:
        sin_beta_half = -sin_beta_half

    alpha_p_gamma_half = (alpha + gamma) * 0.5
    alpha_m_gamma_half = (alpha - gamma) * 0.5

    # Compute the actual values of the quaternion components
    R[..., 0] = cos_beta_half * xp.cos(alpha_p_gamma_half)  # scalar quaternion components
    R[..., 1] = -sin_beta_half * xp.sin(alpha_m_gamma_half)  # x quaternion components
    R[..., 2] = sin_beta_half * xp.cos(alpha_m_gamma_half)  # y quaternion components
    R[..., 3] = cos_beta_half * xp.sin(alpha_p_gamma_half)  # z quaternion components

    # Return array of quaternions if in CPU
    if xp == np:
        return as_quat_array(R)
    else:
        return R


def as_euler_angles(q, xp=np):
    """
    Get Euler angles from normalized quaternions.

    Adapted from M. Boyle to return cosbeta

    Returns alpha, cosbeta, gamma
    """
    n = 1
    arctan1 = xp.arctan2(q[..., 3], q[..., 0])
    arctan2 = xp.arctan2(-q[..., 1], q[..., 2])
    alpha = arctan1 + arctan2
    cosbeta = 2 * (q[..., 0] ** 2 + q[..., 3] ** 2) / n - 1
    gamma = arctan1 - arctan2

    return alpha, cosbeta, gamma


@njit
def ell_prefactor(l: int):
    return np.sqrt((2 * l + 1) / (4 * np.pi))


def wigner_from_quaternions(R, mode_array, xp=np):
    """
    Compute WignerD matrices from quaternions for a custom mode_array with format [[2,2], [2,-1], ...].

    `Derivation Matematica notebook <https://gitlab.com/imrphenom-dev/reviews/qc-phenomt/-/blob/main/theory_notebooks/WignerDquaternions.nb?ref_type=heads>`_.

    Return array where each row corresponds to one mode, same order as the mode_array.
    """

    wD = xp.empty((len(mode_array), len(R)), dtype=xp.complex128)

    Ra = R[:, 0] + 1j * R[:, 3]
    Rb = R[:, 2] + 1j * R[:, 1]

    Rab = Ra * Rb

    Ra2 = Ra * Ra
    Ra4 = Ra2 * Ra2
    Ra6 = Ra4 * Ra2

    Rb2 = Rb * Rb
    Rb4 = Rb2 * Rb2
    Rb6 = Rb4 * Rb2

    Ra_conj = R[:, 0] - 1j * R[:, 3]
    Rb_conj = R[:, 2] - 1j * R[:, 1]

    Ra_conj2 = Ra_conj * Ra_conj
    Rb_conj2 = Rb_conj * Rb_conj

    fac_l2 = ell_prefactor(2)

    for idx, [l, m] in enumerate(mode_array):
        mode = str(l) + str(m)

        if "22" in mode:
            wD[idx] = Ra4 * fac_l2
        if "21" in mode:
            wD[idx] = 2 * Rab * Ra2 * fac_l2
        if "20" in mode:
            wD[idx] = np.sqrt(6) * Rb2 * Ra2 * fac_l2
        if "2-1" in mode:
            wD[idx] = 2 * Rb2 * Rab * fac_l2
        if "2-2" in mode:
            wD[idx] = Rb4 * fac_l2

        fac_l3 = ell_prefactor(3)

        if "33" in mode:
            wD[idx] = -np.sqrt(6) * Rb_conj * Ra * Ra4 * fac_l3
        if "32" in mode:
            Ra_norm = Ra * Ra_conj
            Rb_norm = Rb * Rb_conj
            quotient = Rb_norm / Ra_norm
            wD[idx] = (1 - 5 * quotient) * Ra_norm * Ra4 * fac_l3
        if "3-2" in mode:
            wD[idx] = Rb4 * (5 - quotient) * Ra_norm * fac_l3
        if "3-3" in mode:
            wD[idx] = np.sqrt(6) * Rb4 * Rb * Ra_conj * fac_l3

        fac_l4 = ell_prefactor(4)

        if "44" in mode:
            wD[idx] = 2 * np.sqrt(7) * Rb_conj * Rb_conj * Ra6 * fac_l4
        if "4-4" in mode:
            wD[idx] = 2 * np.sqrt(7) * Rb6 * Ra_conj * Ra_conj * fac_l4

        fac_l5 = ell_prefactor(5)

        if "55" in mode:
            wD[idx] = -2 * np.sqrt(30) * Rb_conj * Rb_conj2 * Ra * Ra6 * fac_l5
        if "5-5" in mode:
            wD[idx] = 2 * np.sqrt(30) * Rb6 * Rb * Ra_conj * Ra_conj2 * fac_l5

    return wD


def compute_ylms(qTot, mode_array, use_wigner_from_quaternions, numba_rotation, xp, lmax):
    """
    Compute Ylms time series from quaternions for a list of modes.

    Used for ``computing polarizations_from`` = 'CPmodes'.

    Parameters
    ----------
    qTot: (N, 4) ndarray
        Array of quaternions (as float array).
    mode_array: list
        List of modes in format [[l,m],[],...] to compute the Ylms for.
    use_wigner_from_quaternions: bool
        Compute WignerD matrices (Ylms) directly from quaternions instead of from Euler angles.
    numba_rotation: string or bool
        Use numba functions to perform the twisting-up rotation of modes.

            - `'default_modes'` or ``True``: use numba for the default_mode_array defined in phenomt.py.
            - `'custom_modes'`: use numba for a custom mode_array. It is slower than default_modes because of all the if statements.
            - ``False``: do not use numba.
    xp: np/cp
        Module to use for computations on the cpu/gpu.
    lmax: int
        Maximum l value for the Ylms to compute (only used for ``use_wigner_from_quaternions`` = ``False``).

    Returns
    -------
    Tuple with ndarray and float
        Ylm: multidimensional array of Ylms time series. Each row corresponds to a mode in mode_array (same order).
        gammaTot: float. Global phase factor to correct the strain if ``use_wigner_from_quaternions`` = ``False``.

    """

    # Dummy value for the case use_wigner_from_quaternions=True
    gammaTot = None

    # Compute Ylm
    if use_wigner_from_quaternions is True:
        # This is the M. Boyle method (fastest, default)
        if numba_rotation == "default_modes" or numba_rotation is True:
            Ylm = numba_wigner_from_quaternions_default_modes(qTot)
        elif numba_rotation == "custom_modes":
            Ylm = numba_wigner_from_quaternions_custom_modes(qTot, np.array(mode_array))
        elif numba_rotation is False:
            Ylm = wigner_from_quaternions(qTot, mode_array, xp=xp)
        else:
            raise ValueError(f"numba_rotation {numba_rotation} not supported. Options are: default_modes, custom_modes, False")
    else:
        # This is the method in seobnrv5 by H. Estellés
        alphaTot, betaTot, gammaTot = as_euler_angles(qTot, xp=xp)

        Ylm = custom_swsh(betaTot, alphaTot, mode_array, lmax, xp=xp)

    return Ylm, gammaTot


@njit
def numba_wigner_from_quaternions_default_modes_i(wD, R):
    """
    Compute WignerD matrices from quaternions for default modes: 22, 21, 33, 44, 55 and negatives

    `Derivation Mathematica notebook <https://gitlab.com/imrphenom-dev/reviews/qc-phenomt/-/blob/main/theory_notebooks/WignerDquaternions.nb?ref_type=heads>`_.

    Modifies the 1D array wD where each element corresponds to one mode, same order as the default mode array
    """

    Ra = R[0] + 1j * R[3]
    Rb = R[2] + 1j * R[1]

    Rab = Ra * Rb

    Ra2 = Ra * Ra
    Ra4 = Ra2 * Ra2
    Ra6 = Ra4 * Ra2

    Rb2 = Rb * Rb
    Rb4 = Rb2 * Rb2
    Rb6 = Rb4 * Rb2

    Ra_conj = R[0] - 1j * R[3]
    Rb_conj = R[2] - 1j * R[1]

    Ra_conj2 = Ra_conj * Ra_conj
    Rb_conj2 = Rb_conj * Rb_conj

    fac_l2 = ell_prefactor(2)
    fac_l3 = ell_prefactor(3)
    fac_l4 = ell_prefactor(4)
    fac_l5 = ell_prefactor(5)

    # 22
    wD[0] = Ra4 * fac_l2
    # 21
    wD[1] = 2 * Rab * Ra2 * fac_l2
    # 33
    wD[2] = -np.sqrt(6) * Rb_conj * Ra * Ra4 * fac_l3
    # 44
    wD[3] = 2 * np.sqrt(7) * Rb_conj * Rb_conj * Ra6 * fac_l4
    # 55
    wD[4] = -2 * np.sqrt(30) * Rb_conj * Rb_conj2 * Ra * Ra6 * fac_l5

    # 2-2
    wD[5] = Rb4 * fac_l2
    # 2-1
    wD[6] = 2 * Rb2 * Rab * fac_l2
    # 3-3
    wD[7] = np.sqrt(6) * Rb4 * Rb * Ra_conj * fac_l3
    # 4-4
    wD[8] = 2 * np.sqrt(7) * Rb6 * Ra_conj * Ra_conj * fac_l4
    # 5-5
    wD[9] = 2 * np.sqrt(30) * Rb6 * Rb * Ra_conj * Ra_conj2 * fac_l5


@njit
def numba_wigner_from_quaternions_custom_modes_i(wD, R, mode_array):
    """
    Compute WignerD matrices from quaternions for a custom mode_array in format [[2,2], [2,-1], ...].

    `Derivation Mathematica notebook <https://gitlab.com/imrphenom-dev/reviews/qc-phenomt/-/blob/main/theory_notebooks/WignerDquaternions.nb?ref_type=heads>`_.

    Modifies input 1D array wD where each element corresponds to one mode, same order as the mode_array
    """

    Ra = R[0] + 1j * R[3]
    Rb = R[2] + 1j * R[1]

    Rab = Ra * Rb

    Ra2 = Ra * Ra
    Ra4 = Ra2 * Ra2
    Ra6 = Ra4 * Ra2

    Rb2 = Rb * Rb
    Rb4 = Rb2 * Rb2
    Rb6 = Rb4 * Rb2

    Ra_conj = R[0] - 1j * R[3]
    Rb_conj = R[2] - 1j * R[1]

    Ra_conj2 = Ra_conj * Ra_conj
    Rb_conj2 = Rb_conj * Rb_conj

    for idx, [l, m] in enumerate(mode_array):
        fac_l2 = ell_prefactor(2)

        if l == 2 and m == 2:
            wD[idx] = Ra4 * fac_l2
        if l == 2 and m == 1:
            wD[idx] = 2 * Rab * Ra2 * fac_l2
        if l == 2 and m == 0:
            wD[idx] = np.sqrt(6) * Rb2 * Ra2 * fac_l2
        if l == 2 and m == -1:
            wD[idx] = 2 * Rb2 * Rab * fac_l2
        if l == 2 and m == -2:
            wD[idx] = Rb4 * fac_l2

        fac_l3 = ell_prefactor(3)

        if l == 3 and m == 3:
            wD[idx] = -np.sqrt(6) * Rb_conj * Ra * Ra4 * fac_l3
        if l == 3 and m == 2:
            Ra_norm = Ra * Ra_conj
            Rb_norm = Rb * Rb_conj
            quotient = Rb_norm / Ra_norm
            wD[idx] = (1 - 5 * quotient) * Ra_norm * Ra4 * fac_l3
        if l == 3 and m == -2:
            wD[idx] = Rb4 * (5 - quotient) * Ra_norm * fac_l3
        if l == 3 and m == -3:
            wD[idx] = np.sqrt(6) * Rb4 * Rb * Ra_conj * fac_l3

        fac_l4 = ell_prefactor(4)

        if l == 4 and m == 4:
            wD[idx] = 2 * np.sqrt(7) * Rb_conj * Rb_conj * Ra6 * fac_l4
        if l == 4 and m == -4:
            wD[idx] = 2 * np.sqrt(7) * Rb6 * Ra_conj * Ra_conj * fac_l4

        fac_l5 = ell_prefactor(5)

        if l == 5 and m == 5:
            wD[idx] = -2 * np.sqrt(30) * Rb_conj * Rb_conj2 * Ra * Ra6 * fac_l5
        if l == 5 and m == -5:
            wD[idx] = 2 * np.sqrt(30) * Rb6 * Rb * Ra_conj * Ra_conj2 * fac_l5

    return wD


@njit
def numba_wigner_from_quaternions_default_modes(R):
    wD = np.empty((10, len(R)), dtype=np.complex128)
    for i in prange(len(R)):
        numba_wigner_from_quaternions_default_modes_i(wD[:, i], R[i])
    return wD


@njit
def numba_wigner_from_quaternions_custom_modes(R, mode_array):
    wD = np.empty((len(mode_array), len(R)), dtype=np.complex128)
    for i in prange(len(R)):
        numba_wigner_from_quaternions_custom_modes_i(wD[:, i], R[i], mode_array)
    return wD


def from_frame(X, Y, Z, xp=np):
    """
    Compute quaternions from frame.
    """
    R = xp.stack((X.T, Y.T, Z.T), axis=-1)
    return from_rotation_matrix(R, nonorthogonal=False, xp=xp)


def from_rotation_matrix(rot, nonorthogonal=True, xp=np):
    """
    Adapted from `M. Boyle quaternion <https://github.com/moble/quaternion>`_.

    Convert input 3x3 rotation matrix to unit quaternion.

    For any orthogonal matrix `rot`, this function returns a quaternion `q` such
    that, for every pure-vector quaternion `v`, we have

        q * v * q.conjugate() == rot @ v.vec

    Here, `@` is the standard python matrix multiplication operator and `v.vec` is
    the 3-vector part of the quaternion `v`.  If `rot` is not orthogonal the
    "closest" orthogonal matrix is used; see Notes below.

    Parameters
    ----------
    rot : (..., N, 3, 3) float array
        Each 3x3 matrix represents a rotation by multiplying (from the left) a
        column vector to produce a rotated column vector.  Note that this input may
        actually have ndims>3; it is just assumed that the last two dimensions have
        size 3, representing the matrix.
    nonorthogonal : bool, optional
        If scipy.linalg is available, use the more robust algorithm of Bar-Itzhack.
        Default value is True.

    Returns
    -------
    q : array of quaternions
        Unit quaternions resulting in rotations corresponding to input rotations.
        Output shape is rot.shape[:-2].

    Raises
    ------
    LinAlgError
        If any of the eigenvalue solutions does not converge

    Notes
    -----
    By default, if scipy.linalg is available, this function uses Bar-Itzhack's
    algorithm to allow for non-orthogonal matrices.  [J. Guidance, Vol. 23, No. 6,
    p. 1085 <http://dx.doi.org/10.2514/2.4654>] This will almost certainly be quite
    a bit slower than simpler versions, though it will be more robust to numerical
    errors in the rotation matrix.  Also note that Bar-Itzhack uses some pretty
    weird conventions.  The last component of the quaternion appears to represent
    the scalar, and the quaternion itself is conjugated relative to the convention
    used throughout this module.

    If scipy.linalg is not available or if the optional `nonorthogonal` parameter
    is set to `False`, this function falls back to the possibly faster, but less
    robust, algorithm of Markley [J. Guidance, Vol. 31, No. 2, p. 440
    <http://dx.doi.org/10.2514/1.31730>].

    """
    try:
        from scipy import linalg
    except ImportError:
        linalg = False

    rot = xp.asarray(rot)
    shape = rot.shape[:-2]

    if linalg and nonorthogonal:
        from operator import mul
        from functools import reduce

        K3 = xp.empty(shape + (4, 4))
        K3[..., 0, 0] = (rot[..., 0, 0] - rot[..., 1, 1] - rot[..., 2, 2]) / 3.0
        K3[..., 0, 1] = (rot[..., 1, 0] + rot[..., 0, 1]) / 3.0
        K3[..., 0, 2] = (rot[..., 2, 0] + rot[..., 0, 2]) / 3.0
        K3[..., 0, 3] = (rot[..., 1, 2] - rot[..., 2, 1]) / 3.0
        K3[..., 1, 0] = K3[..., 0, 1]
        K3[..., 1, 1] = (rot[..., 1, 1] - rot[..., 0, 0] - rot[..., 2, 2]) / 3.0
        K3[..., 1, 2] = (rot[..., 2, 1] + rot[..., 1, 2]) / 3.0
        K3[..., 1, 3] = (rot[..., 2, 0] - rot[..., 0, 2]) / 3.0
        K3[..., 2, 0] = K3[..., 0, 2]
        K3[..., 2, 1] = K3[..., 1, 2]
        K3[..., 2, 2] = (rot[..., 2, 2] - rot[..., 0, 0] - rot[..., 1, 1]) / 3.0
        K3[..., 2, 3] = (rot[..., 0, 1] - rot[..., 1, 0]) / 3.0
        K3[..., 3, 0] = K3[..., 0, 3]
        K3[..., 3, 1] = K3[..., 1, 3]
        K3[..., 3, 2] = K3[..., 2, 3]
        K3[..., 3, 3] = (rot[..., 0, 0] + rot[..., 1, 1] + rot[..., 2, 2]) / 3.0

        if not shape:
            q = zero.copy()
            eigvals, eigvecs = linalg.eigh(K3.T, subset_by_index=(3, 3))
            q.components[0] = eigvecs[-1, 0]
            q.components[1:] = -eigvecs[:-1].flatten()
            return q
        else:
            q = xp.empty(shape + (4,), dtype=xp.float64)
            for flat_index in range(reduce(mul, shape)):
                multi_index = xp.unravel_index(flat_index, shape)
                eigvals, eigvecs = linalg.eigh(K3[multi_index], subset_by_index=(3, 3))
                q[multi_index + (0,)] = eigvecs[-1, 0]
                q[multi_index + (slice(1, None),)] = -eigvecs[:-1].flatten()
            return as_quat_array(q)

    else:  # No scipy.linalg or not `nonorthogonal`
        diagonals = xp.empty(shape + (4,))
        diagonals[..., 0] = rot[..., 0, 0]
        diagonals[..., 1] = rot[..., 1, 1]
        diagonals[..., 2] = rot[..., 2, 2]
        diagonals[..., 3] = rot[..., 0, 0] + rot[..., 1, 1] + rot[..., 2, 2]

        indices = xp.argmax(diagonals, axis=-1)

        q = diagonals  # reuse storage space
        indices_i = indices == 0
        if xp.any(indices_i):
            if indices_i.shape == ():
                indices_i = Ellipsis
            rot_i = rot[indices_i, :, :]
            q[indices_i, 0] = rot_i[..., 2, 1] - rot_i[..., 1, 2]
            q[indices_i, 1] = 1 + rot_i[..., 0, 0] - rot_i[..., 1, 1] - rot_i[..., 2, 2]
            q[indices_i, 2] = rot_i[..., 0, 1] + rot_i[..., 1, 0]
            q[indices_i, 3] = rot_i[..., 0, 2] + rot_i[..., 2, 0]
        indices_i = indices == 1
        if xp.any(indices_i):
            if indices_i.shape == ():
                indices_i = Ellipsis
            rot_i = rot[indices_i, :, :]
            q[indices_i, 0] = rot_i[..., 0, 2] - rot_i[..., 2, 0]
            q[indices_i, 1] = rot_i[..., 1, 0] + rot_i[..., 0, 1]
            q[indices_i, 2] = 1 - rot_i[..., 0, 0] + rot_i[..., 1, 1] - rot_i[..., 2, 2]
            q[indices_i, 3] = rot_i[..., 1, 2] + rot_i[..., 2, 1]
        indices_i = indices == 2
        if xp.any(indices_i):
            if indices_i.shape == ():
                indices_i = Ellipsis
            rot_i = rot[indices_i, :, :]
            q[indices_i, 0] = rot_i[..., 1, 0] - rot_i[..., 0, 1]
            q[indices_i, 1] = rot_i[..., 2, 0] + rot_i[..., 0, 2]
            q[indices_i, 2] = rot_i[..., 2, 1] + rot_i[..., 1, 2]
            q[indices_i, 3] = 1 - rot_i[..., 0, 0] - rot_i[..., 1, 1] + rot_i[..., 2, 2]
        indices_i = indices == 3
        if xp.any(indices_i):
            if indices_i.shape == ():
                indices_i = Ellipsis
            rot_i = rot[indices_i, :, :]
            q[indices_i, 0] = 1 + rot_i[..., 0, 0] + rot_i[..., 1, 1] + rot_i[..., 2, 2]
            q[indices_i, 1] = rot_i[..., 2, 1] - rot_i[..., 1, 2]
            q[indices_i, 2] = rot_i[..., 0, 2] - rot_i[..., 2, 0]
            q[indices_i, 3] = rot_i[..., 1, 0] - rot_i[..., 0, 1]

        q /= xp.linalg.norm(q, axis=-1)[..., xp.newaxis]

        if xp == np:
            return as_quat_array(q)
        else:
            return q
