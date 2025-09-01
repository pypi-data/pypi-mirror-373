# Copyright (C) 2023  Cecilio García Quirós
"""
Generate reference values for test_coefficients.py

Get coefficient values from pWF, pAmp, pPhase for each mode and each approximant.
Also get values for pPrec.

Values are saved in pickle files stored in the reference_values folder.
"""

from phenomxpy.phenomt import PhenomT, PhenomTHM
from phenomxpy.phenomtp import PhenomTPHM
from phenomxaux.utils import save_pickle

# Folder where to save the pickle files
folder = "reference_values/"


def get_numeric_attributes(object):
    """
    Get the class attributes that store numeric values.

    Pameters:
    ---------
    - object: class object to get attributes from.

    Return:
    -------
    dictionary, attribute name and its value

    """
    return {k: v for k, v in vars(object).items() if isinstance(v, (int, float)) and not isinstance(v, bool)}


# Waveform arguments
kwargs = {
    "eta": 0.13,
    "s1": [0.8, -0.1, 0.1],
    "s2": [0.8, 0.4, -0.3],
    "f_lower": 20,
    "f_ref": 25,
    "total_mass": 60,
    "delta_t_sec": 1 / 4096.0,
    "inclination": 1.4,
    "phiRef": 0.5,
    "distance": 2000,
}


# PhenomT
phen = PhenomT(**kwargs)

py_phase_coeffs = phen.pPhase
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

pWF = get_numeric_attributes(phen.pWF)
pAmp = get_numeric_attributes(phen.pAmp)
pPhase = get_numeric_attributes(py_phase_coeffs)

save_pickle(pWF, folder + "phenT.pWF.pkl")
save_pickle(pAmp, folder + "phenT.pAmp.pkl")
save_pickle(pPhase, folder + "phenT.pPhase.pkl")

# PhenomTHM
phen = PhenomTHM(**kwargs)

pWF, pAmp, pPhase = {}, {}, {}

for mode in phen.phenT_classes:
    py_phase_coeffs = phen.phenT_classes[mode].pPhase
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

    pWF[mode] = get_numeric_attributes(phen.phenT_classes[mode].pWF)
    pAmp[mode] = get_numeric_attributes(phen.phenT_classes[mode].pAmp)
    pPhase[mode] = get_numeric_attributes(py_phase_coeffs)

save_pickle(pWF, folder + "phenTHM.pWF.pkl")
save_pickle(pAmp, folder + "phenTHM.pAmp.pkl")
save_pickle(pPhase, folder + "phenTHM.pPhase.pkl")

# PhenomTPHM_NNLO
phen = PhenomTPHM(**kwargs, prec_version="nnlo")

pPrec = get_numeric_attributes(phen.pPrec)
pWF_top = get_numeric_attributes(phen.pWF)

pWF, pAmp, pPhase = {}, {}, {}

for mode in phen.phenTHM.phenT_classes:
    py_phase_coeffs = phen.phenTHM.phenT_classes[mode].pPhase
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

    pWF[mode] = get_numeric_attributes(phen.phenTHM.phenT_classes[mode].pWF)
    pAmp[mode] = get_numeric_attributes(phen.phenTHM.phenT_classes[mode].pAmp)
    pPhase[mode] = get_numeric_attributes(py_phase_coeffs)

save_pickle(pPrec, folder + "phenTPHM_NNLO.pPrec.pkl")
save_pickle(pWF_top, folder + "phenTPHM_NNLO.pWF_top.pkl")
save_pickle(pWF, folder + "phenTPHM_NNLO.pWF.pkl")
save_pickle(pAmp, folder + "phenTPHM_NNLO.pAmp.pkl")
save_pickle(pPhase, folder + "phenTPHM_NNLO.pPhase.pkl")

# PhenomTPHM_MSA
phen = PhenomTPHM(**kwargs, prec_version="msa")

pPrec = get_numeric_attributes(phen.pPrec)
pWF_top = get_numeric_attributes(phen.pWF)

pWF, pAmp, pPhase = {}, {}, {}

for mode in phen.phenTHM.phenT_classes:
    py_phase_coeffs = phen.phenTHM.phenT_classes[mode].pPhase
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

    pWF[mode] = get_numeric_attributes(phen.phenTHM.phenT_classes[mode].pWF)
    pAmp[mode] = get_numeric_attributes(phen.phenTHM.phenT_classes[mode].pAmp)
    pPhase[mode] = get_numeric_attributes(py_phase_coeffs)

save_pickle(pPrec, folder + "phenTPHM_MSA.pPrec.pkl")
save_pickle(pWF_top, folder + "phenTPHM_MSA.pWF_top.pkl")
save_pickle(pWF, folder + "phenTPHM_MSA.pWF.pkl")
save_pickle(pAmp, folder + "phenTPHM_MSA.pAmp.pkl")
save_pickle(pPhase, folder + "phenTPHM_MSA.pPhase.pkl")

# PhenomTPHM_Numerical
phen = PhenomTPHM(**kwargs, prec_version="numerical")

pPrec = get_numeric_attributes(phen.pPrec)
pWF_top = get_numeric_attributes(phen.pWF)

pWF, pAmp, pPhase = {}, {}, {}

for mode in phen.phenTHM.phenT_classes:
    py_phase_coeffs = phen.phenTHM.phenT_classes[mode].pPhase
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

    pWF[mode] = get_numeric_attributes(phen.phenTHM.phenT_classes[mode].pWF)
    pAmp[mode] = get_numeric_attributes(phen.phenTHM.phenT_classes[mode].pAmp)
    pPhase[mode] = get_numeric_attributes(py_phase_coeffs)

save_pickle(pPrec, folder + "phenTPHM.pPrec.pkl")
save_pickle(pWF_top, folder + "phenTPHM.pWF_top.pkl")
save_pickle(pWF, folder + "phenTPHM.pWF.pkl")
save_pickle(pAmp, folder + "phenTPHM.pAmp.pkl")
save_pickle(pPhase, folder + "phenTPHM.pPhase.pkl")
