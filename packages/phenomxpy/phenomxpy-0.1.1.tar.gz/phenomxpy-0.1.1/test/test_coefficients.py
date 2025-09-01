# Copyright (C) 2023  Cecilio García Quirós
import os
import sys

import numpy as np
import pandas as pd
import pytest

from phenomxpy.phenomt.phenomt import IMRPhenomT, IMRPhenomTHM
from phenomxpy.phenomt.phenomtp import IMRPhenomTPHM
from phenomxpy.utils import read_pickle

# Folder where reference values are stored
reference_values = os.path.join(os.path.dirname(__file__), "reference_values/")

# Tolerance for unit test
rtol = 1e-11

# Waveform arguments
kwargs = {
    "eta": 0.13,
    "s1": [0.8, -0.1, 0.1],
    "s2": [0.8, 0.4, -0.3],
    "f_min": 20,
    "f_ref": 25,
    "total_mass": 60,
    "delta_t": 1 / 4096.0,
    "inclination": 1.4,
    "phi_ref": 0.5,
    "distance": 2000,
}


def compare_coeffs(ref_coeffs, py_coeffs):
    """
    Combine two set of coefficients into a pandas data frame

    Parameters:
    -----------
    - ref_coeffs: dictionary with reference coefficients
    - py_coeffs: dictionary with new coefficients

    Return:
    -------
    df pandas dataframe with two columns: ref, new, for the reference values and the ones.
    Each row is a different coefficient.
    """

    data = {}
    for key in ref_coeffs.keys():
        ref_value = ref_coeffs[key]
        try:
            py_value = getattr(py_coeffs, key)
            data[key] = [ref_value, py_value]
        except:
            pass

    data = pd.DataFrame.from_dict(data, orient="index", columns=["ref", "new"])

    return data


#################################
#   Tests for each approximant  #
#################################
# Compare coefficients computed after the initialization of each class.


def test_phenT_coefficients():

    phenT = IMRPhenomT(**kwargs)

    py_phase_coeffs = phenT.pPhase
    (
        py_phase_coeffs.thetapoints1,
        py_phase_coeffs.thetapoints2,
        py_phase_coeffs.thetapoints3,
        py_phase_coeffs.thetapoints4,
        py_phase_coeffs.thetapoints5,
        py_phase_coeffs.thetapoints6,
    ) = py_phase_coeffs.inspiral_collocation_points[:, 0]
    (
        py_phase_coeffs.omegaInspCP1,
        py_phase_coeffs.omegaInspCP2,
        py_phase_coeffs.omegaInspCP3,
        py_phase_coeffs.omegaInspCP4,
        py_phase_coeffs.omegaInspCP5,
        py_phase_coeffs.omegaInspCP6,
    ) = py_phase_coeffs.inspiral_collocation_points[:, 1]

    pWF_reference = read_pickle(reference_values + "phenT.pWF.pkl")
    pAmp_reference = read_pickle(reference_values + "phenT.pAmp.pkl")
    pPhase_reference = read_pickle(reference_values + "phenT.pPhase.pkl")

    d = compare_coeffs(pWF_reference, phenT.pWF)
    np.testing.assert_allclose(d["ref"], d["new"], rtol=rtol, err_msg="phenT.pWF coefficients not equal")

    d = compare_coeffs(pAmp_reference, phenT.pAmp)
    np.testing.assert_allclose(d["ref"], d["new"], rtol=rtol, err_msg="phenT.pAmp coefficients not equal")

    d = compare_coeffs(pPhase_reference, py_phase_coeffs)
    np.testing.assert_allclose(d["ref"], d["new"], rtol=rtol, err_msg="phenT.pPhase coefficients not equal")


def test_phenTHM_coefficients():

    phenTHM = IMRPhenomTHM(**kwargs)

    pWF_reference = read_pickle(reference_values + "phenTHM.pWF.pkl")
    pAmp_reference = read_pickle(reference_values + "phenTHM.pAmp.pkl")
    pPhase_reference = read_pickle(reference_values + "phenTHM.pPhase.pkl")

    for mode in phenTHM.phenT_classes:
        phenT = phenTHM.phenT_classes[mode]

        py_phase_coeffs = phenT.pPhase
        (
            py_phase_coeffs.thetapoints1,
            py_phase_coeffs.thetapoints2,
            py_phase_coeffs.thetapoints3,
            py_phase_coeffs.thetapoints4,
            py_phase_coeffs.thetapoints5,
            py_phase_coeffs.thetapoints6,
        ) = py_phase_coeffs.inspiral_collocation_points[:, 0]
        (
            py_phase_coeffs.omegaInspCP1,
            py_phase_coeffs.omegaInspCP2,
            py_phase_coeffs.omegaInspCP3,
            py_phase_coeffs.omegaInspCP4,
            py_phase_coeffs.omegaInspCP5,
            py_phase_coeffs.omegaInspCP6,
        ) = py_phase_coeffs.inspiral_collocation_points[:, 1]

        d = compare_coeffs(pWF_reference[mode], phenT.pWF)
        np.testing.assert_allclose(d["ref"], d["new"], rtol=rtol, err_msg="phenTHM.phenT_classes[%s].pWF coefficients not equal" % mode)

        d = compare_coeffs(pAmp_reference[mode], phenT.pAmp)
        np.testing.assert_allclose(d["ref"], d["new"], rtol=rtol, err_msg="phenTHM.phenT_classes[%s].pAmp coefficients not equal" % mode)

        d = compare_coeffs(pPhase_reference[mode], py_phase_coeffs)
        np.testing.assert_allclose(d["ref"], d["new"], rtol=rtol, err_msg="phenTHM.phenT_classes[%s].pPhase coefficients not equal" % mode)


def test_phenTPHM_NNLO_coefficients():

    phen = IMRPhenomTPHM(**kwargs, prec_version="nnlo")

    pPrec_reference = read_pickle(reference_values + "phenTPHM_NNLO.pPrec.pkl")
    d = compare_coeffs(pPrec_reference, phen.pPrec)
    np.testing.assert_allclose(d["ref"], d["new"], rtol=rtol, err_msg="phen.pPrec coefficients not equal")

    pWF_top_reference = read_pickle(reference_values + "phenTPHM_NNLO.pWF_top.pkl")
    d = compare_coeffs(pWF_top_reference, phen.pWF)
    np.testing.assert_allclose(d["ref"], d["new"], rtol=rtol, err_msg="phen.pWF_top coefficients not equal")

    pWF_reference = read_pickle(reference_values + "phenTPHM_NNLO.pWF.pkl")
    pAmp_reference = read_pickle(reference_values + "phenTPHM_NNLO.pAmp.pkl")
    pPhase_reference = read_pickle(reference_values + "phenTPHM_NNLO.pPhase.pkl")

    for mode in phen.phenTHM.phenT_classes:
        phenT = phen.phenTHM.phenT_classes[mode]

        py_phase_coeffs = phenT.pPhase
        (
            py_phase_coeffs.thetapoints1,
            py_phase_coeffs.thetapoints2,
            py_phase_coeffs.thetapoints3,
            py_phase_coeffs.thetapoints4,
            py_phase_coeffs.thetapoints5,
            py_phase_coeffs.thetapoints6,
        ) = py_phase_coeffs.inspiral_collocation_points[:, 0]
        (
            py_phase_coeffs.omegaInspCP1,
            py_phase_coeffs.omegaInspCP2,
            py_phase_coeffs.omegaInspCP3,
            py_phase_coeffs.omegaInspCP4,
            py_phase_coeffs.omegaInspCP5,
            py_phase_coeffs.omegaInspCP6,
        ) = py_phase_coeffs.inspiral_collocation_points[:, 1]

        d = compare_coeffs(pWF_reference[mode], phenT.pWF)
        np.testing.assert_allclose(d["ref"], d["new"], rtol=rtol, err_msg="phen.phenTHM.phenT_classes[%s].pWF coefficients not equal" % mode)

        d = compare_coeffs(pAmp_reference[mode], phenT.pAmp)
        np.testing.assert_allclose(d["ref"], d["new"], rtol=rtol, err_msg="phen.phenTHM.phenT_classes[%s].pAmp coefficients not equal" % mode)

        d = compare_coeffs(pPhase_reference[mode], py_phase_coeffs)
        np.testing.assert_allclose(d["ref"], d["new"], rtol=rtol, err_msg="phen.phenTHM.phenT_classes[%s].pPhase coefficients not equal" % mode)


def test_phenTPHM_MSA_coefficients():

    phen = IMRPhenomTPHM(**kwargs, prec_version="msa")

    pPrec_reference = read_pickle(reference_values + "phenTPHM_MSA.pPrec.pkl")
    d = compare_coeffs(pPrec_reference, phen.pPrec)
    np.testing.assert_allclose(d["ref"], d["new"], rtol=rtol, err_msg="phen.pPrec coefficients not equal")

    pWF_top_reference = read_pickle(reference_values + "phenTPHM_MSA.pWF_top.pkl")
    d = compare_coeffs(pWF_top_reference, phen.pWF)
    np.testing.assert_allclose(d["ref"], d["new"], rtol=rtol, err_msg="phen.pWF_top coefficients not equal")

    pWF_reference = read_pickle(reference_values + "phenTPHM_MSA.pWF.pkl")
    pAmp_reference = read_pickle(reference_values + "phenTPHM_MSA.pAmp.pkl")
    pPhase_reference = read_pickle(reference_values + "phenTPHM_MSA.pPhase.pkl")

    for mode in phen.phenTHM.phenT_classes:
        phenT = phen.phenTHM.phenT_classes[mode]

        py_phase_coeffs = phenT.pPhase
        (
            py_phase_coeffs.thetapoints1,
            py_phase_coeffs.thetapoints2,
            py_phase_coeffs.thetapoints3,
            py_phase_coeffs.thetapoints4,
            py_phase_coeffs.thetapoints5,
            py_phase_coeffs.thetapoints6,
        ) = py_phase_coeffs.inspiral_collocation_points[:, 0]
        (
            py_phase_coeffs.omegaInspCP1,
            py_phase_coeffs.omegaInspCP2,
            py_phase_coeffs.omegaInspCP3,
            py_phase_coeffs.omegaInspCP4,
            py_phase_coeffs.omegaInspCP5,
            py_phase_coeffs.omegaInspCP6,
        ) = py_phase_coeffs.inspiral_collocation_points[:, 1]

        d = compare_coeffs(pWF_reference[mode], phenT.pWF)
        np.testing.assert_allclose(d["ref"], d["new"], rtol=rtol, err_msg="phen.phenTHM.phenT_classes[%s].pWF coefficients not equal" % mode)

        d = compare_coeffs(pAmp_reference[mode], phenT.pAmp)
        np.testing.assert_allclose(d["ref"], d["new"], rtol=rtol, err_msg="phen.phenTHM.phenT_classes[%s].pAmp coefficients not equal" % mode)

        d = compare_coeffs(pPhase_reference[mode], py_phase_coeffs)
        np.testing.assert_allclose(d["ref"], d["new"], rtol=rtol, err_msg="phen.phenTHM.phenT_classes[%s].pPhase coefficients not equal" % mode)


def test_phenTPHM_Numerical_coefficients():

    phen = IMRPhenomTPHM(**kwargs, prec_version="numerical")

    pPrec_reference = read_pickle(reference_values + "phenTPHM.pPrec.pkl")
    d = compare_coeffs(pPrec_reference, phen.pPrec)
    np.testing.assert_allclose(d["ref"], d["new"], rtol=rtol, err_msg="phen.pPrec coefficients not equal")

    pWF_top_reference = read_pickle(reference_values + "phenTPHM.pWF_top.pkl")
    d = compare_coeffs(pWF_top_reference, phen.pWF)
    np.testing.assert_allclose(d["ref"], d["new"], rtol=rtol, err_msg="phen.pWF_top coefficients not equal")

    pWF_reference = read_pickle(reference_values + "phenTPHM.pWF.pkl")
    pAmp_reference = read_pickle(reference_values + "phenTPHM.pAmp.pkl")
    pPhase_reference = read_pickle(reference_values + "phenTPHM.pPhase.pkl")

    for mode in phen.phenTHM.phenT_classes:
        phenT = phen.phenTHM.phenT_classes[mode]

        py_phase_coeffs = phenT.pPhase
        (
            py_phase_coeffs.thetapoints1,
            py_phase_coeffs.thetapoints2,
            py_phase_coeffs.thetapoints3,
            py_phase_coeffs.thetapoints4,
            py_phase_coeffs.thetapoints5,
            py_phase_coeffs.thetapoints6,
        ) = py_phase_coeffs.inspiral_collocation_points[:, 0]
        (
            py_phase_coeffs.omegaInspCP1,
            py_phase_coeffs.omegaInspCP2,
            py_phase_coeffs.omegaInspCP3,
            py_phase_coeffs.omegaInspCP4,
            py_phase_coeffs.omegaInspCP5,
            py_phase_coeffs.omegaInspCP6,
        ) = py_phase_coeffs.inspiral_collocation_points[:, 1]

        d = compare_coeffs(pWF_reference[mode], phenT.pWF)
        np.testing.assert_allclose(d["ref"], d["new"], rtol=rtol, err_msg="phen.phenTHM.phenT_classes[%s].pWF coefficients not equal" % mode)

        d = compare_coeffs(pAmp_reference[mode], phenT.pAmp)
        np.testing.assert_allclose(d["ref"], d["new"], rtol=rtol, err_msg="phen.phenTHM.phenT_classes[%s].pAmp coefficients not equal" % mode)

        d = compare_coeffs(pPhase_reference[mode], py_phase_coeffs)
        np.testing.assert_allclose(d["ref"], d["new"], rtol=rtol, err_msg="phen.phenTHM.phenT_classes[%s].pPhase coefficients not equal" % mode)


if __name__ == "__main__":
    args = sys.argv[1:] or ["-v", "-rs"]
    sys.exit(pytest.main(args=[__file__] + args))
