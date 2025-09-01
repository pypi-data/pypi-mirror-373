# Copyright (C) 2023  Cecilio García Quirós
"""
Print reference values that go in test_coefficients.py.
"""

from test_phenomT import gen_test_data, gen_test_data_fd

kwargs = {
    "test_IMRPhenomT": dict(approximant="IMRPhenomT"),
    "test_IMRPhenomT condition": dict(approximant="IMRPhenomT", condition=1),
    "test_IMRPhenomTHM": dict(approximant="IMRPhenomTHM"),
    "test_IMRPhenomTP_NNLO": dict(approximant="IMRPhenomTP", prec_version="nnlo"),
    "test_IMRPhenomTPHM_NNLO": dict(approximant="IMRPhenomTPHM", prec_version="nnlo"),
    "test_IMRPhenomTP_MSA": dict(approximant="IMRPhenomTP", prec_version="msa"),
    "test_IMRPhenomTPHM_MSA": dict(approximant="IMRPhenomTPHM", prec_version="msa"),
    "test_IMRPhenomTPHM_ST": dict(approximant="IMRPhenomTPHM", prec_version="numerical"),
    "test_IMRPhenomTPHM_ST_FS2": dict(approximant="IMRPhenomTPHM", prec_version="numerical", final_spin_version=2),
}

for test in kwargs:
    print()
    print(test)
    print(gen_test_data(**kwargs[test]))

print()
for test in kwargs:
    if test != "test_IMRPhenomT condition":
        print()
        print(test)
        print(gen_test_data_fd(**kwargs[test]))
