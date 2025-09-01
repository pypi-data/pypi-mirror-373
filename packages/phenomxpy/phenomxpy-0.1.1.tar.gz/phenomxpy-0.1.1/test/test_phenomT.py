# Copyright (C) 2023  Cecilio García Quirós
import sys

import numpy as np
import pytest

import phenomxpy

try:
    import cupy as cp
except ImportError:
    cp = None

# Run gpu test if possible
try:
    gpu_count = cp.cuda.runtime.getDeviceCount()
    if gpu_count > 0:
        print("GPU is available")
        cuda_available = True
    else:
        print("GPU is not available")
        cuda_available = False
except:
    print("GPU is not available")
    cuda_available = False
    pass
# The current CI cannot run gpu jobs
# cuda_available = False

# Tolerances for unit tests
rtol = 1e-13  # local
rtol = 1e-9  # online

# Waveform arguments
wf_params = dict(delta_t=1 / 4096, inclination=1.4, phi_ref=0, total_mass=60, f_min=10, eta=0.13, s1=[0.7, -0.1, 0.1], s2=[-0.5, 0.2, -0.3], f_ref=15)


def get_amp_phase(h):
    amp = np.abs(h)
    phase = np.unwrap(np.angle(h))
    return amp, phase


def sum_sqr_diff(x, y):
    return np.sqrt(np.sum((x - y) ** 2))


def gen_test_data(approximant="", **kwargs):
    """
    Compute amplitude and phase sumed square difference between the TD strain of two cases with different inclination and phi_ref.

    Return:
    -------
    2 floats, difference in amplitude and phase
    """

    phen = getattr(phenomxpy, approximant)(**wf_params, **kwargs)
    hp1, hc1, _ = phen.compute_polarizations()

    wf_params2 = wf_params.copy()
    wf_params2["inclination"] *= 1.5
    wf_params2["phi_ref"] = 2.3
    phen2 = getattr(phenomxpy, approximant)(**wf_params2, **kwargs)
    hp2, hc2, _ = phen2.compute_polarizations()

    strain1 = hp1 - 1j * hc1
    strain2 = hp2 - 1j * hc2

    if phen.xp == cp and cuda_available:
        strain1 = strain1.get()
        strain2 = strain2.get()

    h1_amp, h1_phase = get_amp_phase(strain1)
    h2_amp, h2_phase = get_amp_phase(strain2)

    h_amp_diff = sum_sqr_diff(h1_amp, h2_amp)
    h_phase_diff = np.mod(sum_sqr_diff(h1_phase, h2_phase), 2 * np.pi)

    return h_amp_diff, h_phase_diff


def gen_test_data_fd(approximant="", **kwargs):
    """
    Compute amplitude and phase sumed square difference between the FD strain of two cases with different inclination and phi_ref.

    Return:
    -------
    2 floats, difference in amplitude and phase
    """

    phen = getattr(phenomxpy, approximant)(**wf_params, condition=True, **kwargs)
    hp1, hc1, _ = phen.compute_fd_polarizations()

    wf_params2 = wf_params.copy()
    wf_params2["inclination"] *= 1.5
    wf_params2["phi_ref"] = 2.3
    phen = getattr(phenomxpy, approximant)(**wf_params2, condition=True, **kwargs)
    hp2, hc2, _ = phen.compute_fd_polarizations()

    strain1 = hp1 - 1j * hc1
    strain2 = hp2 - 1j * hc2

    if phen.xp == cp and cuda_available:
        strain1 = strain1.get()
        strain2 = strain2.get()

    h1_amp, h1_phase = get_amp_phase(strain1)
    h2_amp, h2_phase = get_amp_phase(strain2)

    h_amp_diff = sum_sqr_diff(h1_amp, h2_amp)
    h_phase_diff = np.mod(sum_sqr_diff(h1_phase, h2_phase), 2 * np.pi)

    return h_amp_diff, h_phase_diff


#################################
#   Tests for each approximant  #
#################################


def test_IMRPhenomT():

    expected_result = np.array([1.6134477966611247, 1.2420775340151593])
    new_result = np.array(gen_test_data("IMRPhenomT", cuda=False))
    np.testing.assert_allclose(new_result, expected_result, rtol=rtol, err_msg="IMRPhenomT CPU test failed")

    new_result = np.array(gen_test_data("IMRPhenomT", cuda=False, numba_ansatze=False))
    np.testing.assert_allclose(new_result, expected_result, rtol=rtol, err_msg="IMRPhenomT CPU numba=false test failed")

    if cuda_available:
        new_result = gen_test_data("IMRPhenomT", cuda=True)
        np.testing.assert_allclose(new_result, expected_result, rtol=rtol, err_msg="IMRPhenomT GPU test failed")

    # Conditioned
    expected_result = np.array([1.7259677613679751, 5.062338993337605])
    new_result = np.array(gen_test_data("IMRPhenomT", cuda=False, condition=True))
    np.testing.assert_allclose(new_result, expected_result, rtol=rtol, err_msg="IMRPhenomT CPU test failed")

    new_result = np.array(gen_test_data("IMRPhenomT", cuda=False, numba_ansatze=False, condition=True))
    np.testing.assert_allclose(new_result, expected_result, rtol=rtol, err_msg="IMRPhenomT CPU numba=false test failed")

    if cuda_available:
        new_result = gen_test_data("IMRPhenomT", cuda=True, condition=True)
        np.testing.assert_allclose(new_result, expected_result, rtol=1e-6, err_msg="IMRPhenomT GPU test failed")

    # Fourier domain
    expected_result = np.array([0.16377385387203905, 0.4831520365810533])
    new_result = np.array(gen_test_data_fd("IMRPhenomT", cuda=False))
    np.testing.assert_allclose(new_result, expected_result, rtol=1e-7, err_msg="IMRPhenomT_FD CPU test failed")

    new_result = np.array(gen_test_data_fd("IMRPhenomT", cuda=False, numba_ansatze=False))
    np.testing.assert_allclose(new_result, expected_result, rtol=1e-7, err_msg="IMRPhenomT_FD CPU numba=false test failed")

    if cuda_available:
        new_result = gen_test_data_fd("IMRPhenomT", cuda=True)
        np.testing.assert_allclose(new_result, expected_result, rtol=1e-6, err_msg="IMRPhenomT_FD GPU test failed")


def test_IMRPhenomTHM():

    expected_result = np.array([1.6488293570243722, 1.770969082966083])
    new_result = np.array(gen_test_data("IMRPhenomTHM"))
    np.testing.assert_allclose(new_result, expected_result, rtol=rtol, err_msg="IMRPhenomTHM CPU test failed")

    new_result = np.array(gen_test_data("IMRPhenomTHM", numba_ansatze=False))
    np.testing.assert_allclose(new_result, expected_result, rtol=rtol, err_msg="IMRPhenomTHM CPU numba=false test failed")

    if cuda_available:
        new_result = gen_test_data("IMRPhenomTHM", cuda=True)
        np.testing.assert_allclose(new_result, expected_result, rtol=rtol, err_msg="IMRPhenomTHM GPU test failed")


def test_IMRPhenomTP_NNLO():

    expected_result = np.array([1.4468887094826826, 2.7390969436781702])
    new_result = np.array(gen_test_data("IMRPhenomTP", prec_version="nnlo"))
    np.testing.assert_allclose(new_result, expected_result, rtol=rtol, err_msg="IMRPhenomTP NNLO CPU test failed")

    new_result = np.array(gen_test_data("IMRPhenomTP", prec_version="nnlo", polarizations_from="L0modes"))
    np.testing.assert_allclose(new_result, expected_result, rtol=rtol, err_msg="IMRPhenomTP NNLO CPU L0modes test failed")

    new_result = np.array(gen_test_data("IMRPhenomTP", prec_version="nnlo", use_wigner_from_quaternions=False))
    np.testing.assert_allclose(new_result, expected_result, rtol=rtol, err_msg="IMRPhenomTP NNLO CPU wigner from Euler test failed")

    if cuda_available:
        new_result = gen_test_data("IMRPhenomTP", prec_version="nnlo", cuda=True)
        np.testing.assert_allclose(new_result, expected_result, rtol=rtol, err_msg="IMRPhenomTP NNLO GPU test failed")

        new_result = np.array(gen_test_data("IMRPhenomTP", prec_version="nnlo", cuda=True, use_wigner_from_quaternions=False))
        np.testing.assert_allclose(new_result, expected_result, rtol=rtol, err_msg="IMRPhenomTP NNLO CPU wigner from Euler test failed")


def test_IMRPhenomTPHM_NNLO():

    expected_result = np.array([1.488393499978703, 1.533522171850926])
    new_result = np.array(gen_test_data("IMRPhenomTPHM", prec_version="nnlo"))
    np.testing.assert_allclose(new_result, expected_result, rtol=rtol, err_msg="IMRPhenomTPHM NNLO angles CPU test failed")

    new_result = np.array(gen_test_data("IMRPhenomTPHM", prec_version="nnlo", polarizations_from="L0modes"))
    np.testing.assert_allclose(new_result, expected_result, rtol=rtol, err_msg="IMRPhenomTPHM NNLO angles CPU L0 modes test failed")

    if cuda_available:
        new_result = gen_test_data("IMRPhenomTPHM", prec_version="nnlo", cuda=True)
        np.testing.assert_allclose(new_result, expected_result, rtol=rtol, err_msg="IMRPhenomTPHM NNLO angles GPU test failed")


def test_IMRPhenomTP_MSA():

    expected_result = np.array([1.4619373912754237, 0.8260169046345993])
    new_result = np.array(gen_test_data("IMRPhenomTP", prec_version="msa"))
    np.testing.assert_allclose(new_result, expected_result, rtol=rtol, err_msg="IMRPhenomTP MSA angles CPU test failed")

    new_result = np.array(gen_test_data("IMRPhenomTP", prec_version="msa", polarizations_from="L0modes"))
    np.testing.assert_allclose(new_result, expected_result, rtol=rtol, err_msg="IMRPhenomTP MSA angles CPU L0 modes test failed")

    if cuda_available:
        new_result = gen_test_data("IMRPhenomTP", prec_version="msa", cuda=True)
        np.testing.assert_allclose(new_result, expected_result, rtol=rtol, err_msg="IMRPhenomTP MSA angles GPU test failed")


def test_IMRPhenomTPHM_MSA():

    expected_result = np.array([1.5190798239607697, 5.3206165141959545])
    new_result = np.array(gen_test_data("IMRPhenomTPHM", prec_version="msa"))
    np.testing.assert_allclose(new_result, expected_result, rtol=rtol, err_msg="IMRPhenomTPHM MSA angles CPU test failed")

    new_result = np.array(gen_test_data("IMRPhenomTPHM", prec_version="msa", polarizations_from="L0modes"))
    np.testing.assert_allclose(new_result, expected_result, rtol=rtol, err_msg="IMRPhenomTPHM MSA angles CPU L0 modes test failed")

    if cuda_available:
        new_result = gen_test_data("IMRPhenomTPHM", prec_version="msa", cuda=True)
        np.testing.assert_allclose(new_result, expected_result, rtol=rtol, err_msg="IMRPhenomTPHM MSA angles GPU test failed")


def test_IMRPhenomTPHM_ST():

    # Numerical angles
    expected_result = np.array([1.5118192511392472, 6.068479285892714])
    new_result = np.array(gen_test_data("IMRPhenomTPHM", prec_version="numerical"))
    np.testing.assert_allclose(new_result, expected_result, rtol=rtol, err_msg="IMRPhenomTPHM Num angles FS-4 CPU test failed")

    new_result = np.array(gen_test_data("IMRPhenomTPHM", prec_version="numerical", polarizations_from="L0modes"))
    np.testing.assert_allclose(new_result, expected_result, rtol=1e-8, err_msg="IMRPhenomTPHM Num angles FS-4 CPU L0modes test failed")

    if cuda_available:
        new_result = gen_test_data("IMRPhenomTPHM", prec_version="numerical", cuda=True)
        np.testing.assert_allclose(new_result, expected_result, rtol=rtol, err_msg="IMRPhenomTPHM Num angles GPU test failed")

    expected_result = np.array([1.5117859428512992, 0.2977753588451222])
    new_result = np.array(gen_test_data("IMRPhenomTPHM", prec_version="numerical", final_spin_version=2))
    np.testing.assert_allclose(new_result, expected_result, rtol=rtol, err_msg="IMRPhenomTPHM Num angles FS-2 CPU test failed")

    new_result = np.array(gen_test_data("IMRPhenomTPHM", prec_version="numerical", final_spin_version=2, polarizations_from="L0modes"))
    np.testing.assert_allclose(new_result, expected_result, rtol=1e-7, err_msg="IMRPhenomTPHM Num angles FS-2 CPU Numba-rot L0modes test failed")

    if cuda_available:
        new_result = gen_test_data("IMRPhenomTPHM", prec_version="numerical", final_spin_version=2, cuda=True)
        np.testing.assert_allclose(new_result, expected_result, rtol=rtol, err_msg="IMRPhenomTPHM Num angles FS-2 GPU test failed")


if __name__ == "__main__":
    args = sys.argv[1:] or ["-v", "-rs"]
    sys.exit(pytest.main(args=[__file__] + args))
