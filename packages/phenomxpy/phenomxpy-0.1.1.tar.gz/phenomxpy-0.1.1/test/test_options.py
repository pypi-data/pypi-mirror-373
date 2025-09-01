# Copyright (C) 2023  Cecilio García Quirós
import numpy as np
import phenomxpy
from phenomxpy.common import GeneratePolarizations
import astropy.units as u
import sys
import pytest
from phenomxpy.utils import HztoMf, SecondtoMass, AmpSItoNR

# Waveform arguments
params = {
    "mass1": 30 * u.solMass,
    "mass2": 20 * u.solMass,
    "spin1x": -0.2891445 * u.dimensionless_unscaled,
    "spin1y": 0.37878766 * u.dimensionless_unscaled,
    "spin1z": -0.40825443 * u.dimensionless_unscaled,
    "spin2x": -0.04963701 * u.dimensionless_unscaled,
    "spin2y": 0.04123381 * u.dimensionless_unscaled,
    "spin2z": -0.13151325 * u.dimensionless_unscaled,
    "distance": 10516.03124442 * u.Mpc,
    "inclination": 0.88956637 * u.rad,
    "phi_ref": 1.09531516 * u.rad,
    "deltaT": 1 / 4096 * u.s,
    "f22_start": 10 * u.Hz,
    "f22_ref": 20 * u.Hz,
    "deltaF": 0 * u.Hz,  # Need deltaF key for gwsignal and pyseobnr
    "condition": 0,
    # "v_function": "imr_omega"
}

appxs = ["PyIMRPhenomT", "PyIMRPhenomTHM", "PyIMRPhenomTPHM", "PyIMRPhenomTPHM_NNLO", "PyIMRPhenomTPHM_MSA"]


def test_minimum_frequencies():
    tolerance = 1e-12
    for appx in appxs:
        # Test mimimum frequencies
        params2 = params.copy()

        hp1, hc1 = GeneratePolarizations(params2, approximant=appx, domain="TD")

        params2["f22_start"] = 20 * u.Hz
        hp2, hc2 = GeneratePolarizations(params2, approximant=appx, domain="TD")

        strain1 = hp1 - 1j * hc1
        strain2 = hp2 - 1j * hc2

        strain1 = strain1[-len(strain2) :]

        error = np.abs(1 - strain1 / strain2).value

        np.testing.assert_(np.max(error) < tolerance, msg=f"Relative error > {tolerance} for {appx}.")


approximants = ["IMRPhenomT", "IMRPhenomT", "IMRPhenomT", "IMRPhenomTPHM"]


def test_input_different_units():
    # Waveform arguments
    total_mass = 60
    wf_params_si = dict(
        delta_t=1 / 4096,
        inclination=1.4,
        phi_ref=0,
        total_mass=total_mass,
        distance=2000,
        f_min=10,
        f_ref=20,
        eta=0.13,
        s1=[0.7, -0.1, 0.1],
        s2=[-0.5, 0.2, -0.3],
    )
    wf_params_mass = wf_params_si.copy()
    wf_params_mass.pop("total_mass")
    wf_params_mass["delta_t"] = SecondtoMass(wf_params_si["delta_t"], total_mass)
    wf_params_mass["f_min"] = HztoMf(wf_params_si["f_min"], total_mass)
    wf_params_mass["f_ref"] = HztoMf(wf_params_si["f_ref"], total_mass)

    for appx in approximants:
        phen1 = getattr(phenomxpy, appx)(**wf_params_si)
        hp, hc, times1 = phen1.compute_polarizations()
        strain1 = hp - 1j * hc

        phen2 = getattr(phenomxpy, appx)(**wf_params_mass)
        hp, hc, times2 = phen2.compute_polarizations()
        strain2 = hp - 1j * hc

        strain1 = AmpSItoNR(strain1, wf_params_si["distance"], total_mass)
        times1 = SecondtoMass(times1, total_mass)

        error = np.abs(1 - strain1 / strain2)

        np.testing.assert_(np.max(error) < 1e-13, msg=f"Strain relative error {np.max(error):.3e} > {1e-13} for {appx}.")

        error = np.abs(times1 - times2)

        np.testing.assert_(np.max(error) < 1e-11, msg=f"Times relative error {np.max(error):.3e}> {1e-11} for {appx}.")


def test_custom_time_array():
    from phenomxpy.utils import MasstoSecond

    # Waveform arguments
    wf_params_si = dict(
        delta_t=1 / 4096,
        inclination=1.4,
        phi_ref=0,
        total_mass=60,
        distance=2000,
        f_min=10,
        f_ref=20,
        eta=0.13,
        s1=[0.7, -0.1, 0.1],
        s2=[-0.5, 0.2, -0.3],
        v_function="imr_omega",
    )

    for appx in approximants:
        phen = getattr(phenomxpy, appx)(**wf_params_si)
        full_grid = MasstoSecond(phen.set_time_array(times=None), phen.pWF.total_mass)

        hp, hc, _ = phen.compute_polarizations(times=full_grid)
        strain = hp - 1j * hc

        # Split waveform into even and odd time samples
        even_hp, even_hc, _ = phen.compute_polarizations(times=full_grid[::2])
        odd_hp, odd_hc, _ = phen.compute_polarizations(times=full_grid[1::2])
        even = even_hp - 1j * even_hc
        odd = odd_hp - 1j * odd_hc

        # Recombine the even and odd samples
        recombined = np.empty_like(strain)
        recombined[::2] = even
        recombined[1::2] = odd

        error = np.abs(1 - strain / recombined)

        np.testing.assert_(np.max(error) < 1e-15, msg=f"Strain relative error {np.max(error):.3e} > {1e-15} for {appx}.")


def test_numba_ansatze():
    tolerance = 1e-13

    params2 = params.copy()
    params2["numba_ansatze"] = False

    for appx in appxs:
        hp1, hc1 = GeneratePolarizations(params, approximant=appx, domain="TD")
        strain1 = hp1 - 1j * hc1

        hp2, hc2 = GeneratePolarizations(params2, approximant=appx, domain="TD")
        strain2 = hp2 - 1j * hc2

        error = np.abs(1 - strain1 / strain2)

        np.testing.assert_(np.max(error) < tolerance, msg=f"Relative error {np.max(error):.3e} > {tolerance} for {appx}.")


def test_compute_modes_at_once():
    tolerance = 1e-15

    params2 = params.copy()
    params2["compute_hlms_at_once"] = True
    params2["compute_CPmodes_at_once"] = True

    for appx in ["PyIMRPhenomTPHM", "PyIMRPhenomTPHM_NNLO", "PyIMRPhenomTPHM_MSA"]:
        hp1, hc1 = GeneratePolarizations(params, approximant=appx, domain="TD")
        strain1 = hp1 - 1j * hc1

        hp2, hc2 = GeneratePolarizations(params2, approximant=appx, domain="TD")
        strain2 = hp2 - 1j * hc2

        error = np.abs(1 - strain1 / strain2)

        np.testing.assert_(np.max(error) < tolerance, msg=f"Relative error {np.max(error):.3e} > {tolerance} for {appx}.")


def test_compute_ylms_at_once():
    tolerance = 1e-15

    params2 = params.copy()
    params2["compute_ylms_at_once"] = True

    for appx in appxs:
        hp1, hc1 = GeneratePolarizations(params, approximant=appx, domain="TD")
        strain1 = hp1 - 1j * hc1

        hp2, hc2 = GeneratePolarizations(params2, approximant=appx, domain="TD")
        strain2 = hp2 - 1j * hc2

        error = np.abs(1 - strain1 / strain2)

        np.testing.assert_(np.max(error) < tolerance, msg=f"Relative error {np.max(error):.3e} > {tolerance} for {appx}.")


def test_polarizations_from_different_frames():
    params2 = params.copy()
    params2["quaternions_from"] = "euler_angles"

    for appx in ["PyIMRPhenomTPHM", "PyIMRPhenomTPHM_NNLO", "PyIMRPhenomTPHM_MSA"]:
        hp1, hc1 = GeneratePolarizations(params2, approximant=appx, domain="TD")
        strain1 = hp1 - 1j * hc1

        for polarizations_from in ["CPmodes", "Jmodes", "L0modes"]:
            params2["polarizations_from"] = polarizations_from
            hp2, hc2 = GeneratePolarizations(params2, approximant=appx, domain="TD")
            strain2 = hp2 - 1j * hc2

            error = np.abs(1 - strain1 / strain2)

            np.testing.assert_(
                np.max(error) < 1e-14, msg=f"Relative error {np.max(error):.3e} > {1e-14} for {appx} and polarizations_from={polarizations_from}."
            )


def test_numba_for_twist_up_rotation():
    params2 = params.copy()

    for appx in ["PyIMRPhenomTPHM", "PyIMRPhenomTPHM_NNLO", "PyIMRPhenomTPHM_MSA"]:
        for polarizations_from in ["CPmodes", "Jmodes", "L0modes"]:
            params2["polarizations_from"] = polarizations_from

            hp1, hc1 = GeneratePolarizations(params2, approximant=appx, domain="TD")
            strain1 = hp1 - 1j * hc1

            params3 = params.copy()
            params3["numba_rotation"] = False
            hp2, hc2 = GeneratePolarizations(params2, approximant=appx, domain="TD")
            strain2 = hp2 - 1j * hc2

            error = np.abs(1 - strain1 / strain2)

            np.testing.assert_(
                np.max(error) < 1e-14, msg=f"Relative error {np.max(error):.3e} > {1e-14} for {appx} and polarizations_from={polarizations_from}."
            )


def test_gamma_integration_methods():
    params2 = params.copy()
    params2["quaternions_from"] = "euler_angles"
    appx = "PyIMRPhenomTPHM"

    hp1, hc1 = GeneratePolarizations(params2, approximant=appx, domain="TD")
    strain1 = hp1 - 1j * hc1

    rtols = [1e-15, 1e-10, 1e-6]
    rtols2 = [1e-5, 1e-5, 1e-2]
    for idx, gamma_integration_method in enumerate(["piecewise_integral", "boole", "antiderivative"]):
        params2["gamma_integration_method"] = gamma_integration_method
        hp2, hc2 = GeneratePolarizations(params2, approximant=appx, domain="TD")
        strain2 = hp2 - 1j * hc2

        error = np.abs(1 - strain1 / strain2).value

        np.testing.assert_(
            np.max(error) < rtols[idx],
            msg=f"Relative error {np.max(error):.3e} > {rtols[idx]} for gamma_integration_method={gamma_integration_method}.",
        )

        params3 = params2.copy()
        params3["analytical_RD_gamma"] = False
        hp2, hc2 = GeneratePolarizations(params3, approximant=appx, domain="TD")
        strain2 = hp2 - 1j * hc2

        error = np.abs(1 - strain1 / strain2).value

        np.testing.assert_(
            np.max(error) < rtols2[idx],
            msg=f"Relative error {np.max(error):.3e} > {rtols2[idx]} for gamma_integration_method={gamma_integration_method} and analytical_RD_gamma=False.",
        )


def test_ode_solver_right_hand_sides():
    params2 = params.copy()
    appx = "PyIMRPhenomTPHM"

    hp1, hc1 = GeneratePolarizations(params2, approximant=appx, domain="TD")
    strain1 = hp1 - 1j * hc1

    rtols = [1e-12, 1e-6]
    for idx, v_function in enumerate(["interpolant", "imr_omega"]):
        params2["v_function"] = v_function
        hp2, hc2 = GeneratePolarizations(params2, approximant=appx, domain="TD")
        strain2 = hp2 - 1j * hc2

        error = np.abs(1 - strain1 / strain2).value

        np.testing.assert_(np.max(error) < rtols[idx], msg=f"Relative error {np.max(error):.3e} > {rtols[idx]} for v_function={v_function}.")

        params3 = params2.copy()
        params3["numba_derivatives"] = False
        hp2, hc2 = GeneratePolarizations(params3, approximant=appx, domain="TD")
        strain2 = hp2 - 1j * hc2

        error = np.abs(1 - strain1 / strain2).value

        np.testing.assert_(
            np.max(error) < rtols[idx],
            msg=f"Relative error {np.max(error):.3e} > {rtols[idx]} for v_function={v_function} and numba_derivatives=False.",
        )


def test_interpolations():
    params2 = params.copy()
    appx = "PyIMRPhenomTPHM"

    hp1, hc1 = GeneratePolarizations(params2, approximant=appx, domain="TD")
    strain1 = hp1 - 1j * hc1

    rtols = [1e-15, 1e-7]
    for idx, interpolate in enumerate(["ode_solution", None]):
        params2["interpolate"] = interpolate
        hp2, hc2 = GeneratePolarizations(params2, approximant=appx, domain="TD")
        strain2 = hp2 - 1j * hc2

        error = np.abs(1 - strain1 / strain2).value

        np.testing.assert_(np.max(error) < rtols[idx], msg=f"Relative error {np.max(error):.3e} > {rtols[idx]} for interpolate={interpolate}.")

        if interpolate == "ode_solution":
            params2["cubic_interpolation_for_ode"] = True
            hp2, hc2 = GeneratePolarizations(params2, approximant=appx, domain="TD")
            strain2 = hp2 - 1j * hc2

            error = np.abs(1 - strain1 / strain2).value

            np.testing.assert_(np.max(error) < rtols[idx], msg=f"Relative error {np.max(error):.3e} > {rtols[idx]} for interpolate={interpolate}.")

    params2["quaternions_from"] = "euler_angles"
    hp1, hc1 = GeneratePolarizations(params2, approximant=appx, domain="TD")
    strain1 = hp1 - 1j * hc1

    rtols = [1e-8, 1e-8, 1e-15]
    for idx, interpolate in enumerate(["ode_solution", "euler_angles", None]):
        params2["interpolate"] = interpolate
        hp2, hc2 = GeneratePolarizations(params2, approximant=appx, domain="TD")
        strain2 = hp2 - 1j * hc2

        error = np.abs(1 - strain1 / strain2).value

        np.testing.assert_(np.max(error) < rtols[idx], msg=f"Relative error {np.max(error):.3e} > {rtols[idx]} for interpolate={interpolate}.")


if __name__ == "__main__":
    args = sys.argv[1:] or ["-v", "-rs", "--junit-xml=junit-phenomT.xml"]
    sys.exit(pytest.main(args=[__file__] + args))
