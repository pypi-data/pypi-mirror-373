# Copyright (C) 2023  Cecilio García Quirós
import phenomxpy
import numpy as np

try:
    from bilby.gw.conversion import bilby_to_lalsimulation_spins
except:
    pass
try:
    import lalsimulation as lalsim
    import lal
    import lalsimulation.gwsignal as gws
    from importlib import import_module
except:
    pass

from phenomxpy.utils import (
    lookup_mass1,
    lookup_mass2,
    SecondtoMass,
    extra_options_from_string,
    ToComponentMassesCartesianSpins,
    convert_params_from_gwsignal,
)
from gwpy.timeseries import TimeSeries
from gwpy.frequencyseries import FrequencySeries
import astropy.units as u


def GeneratePolarizations(parameters={}, approximant="IMRPhenomT", domain="TD", return_generator=False):
    """
    Wrapper function to generate hp, hc in time or frequency domain from different interfaces:

        - LALSuite C interface: use swiglal python wrappers
        - LALSuite gwsignal interface: the lalsuite python interface. Can call phenomxpy, FIXME pyseobnr
        - phenomxpy: use phenomxpy directly.

    Parameters
    ----------
    parameters: astropy dict
        Waveform parameters with astropy units and extra options
    approximant: str
        Approximant name
    domain: {"TD", "FD"}
        Polarizations in time or frequency domain. Will perform an FFT if using a time domain approximant.
    return_generator: bool
        Return the class object for the python generator.

    Returns
    -------
    Tuple with 2 gwpy Time(Frequency)Series.
        hp, hc: polarizations in time or frequency domain.
    Optionally also return the python generator object.
    """

    params = parameters.copy()

    # Parse extra options from approximant name (not if approximant=NR_hdf5)
    if approximant == "NR_hdf5":
        params["interface"] = "c"
    else:
        wf_approximant, extra_options = extra_options_from_string(approximant)

        # Insert extra options into params dictionary
        params.update({k: v for k, v in extra_options.items() if k not in params})
        params.pop("nrfile", None)

    timeslal = params.pop("timeslal", None)
    if timeslal is True:
        lal_params = params.copy()
        lal_params["interface"] = "c"
        lal_params["lalsuite"] = True
        lal_params["use_exact_epoch"] = True
        hp_lal, _ = GeneratePolarizations(parameters=lal_params, approximant=wf_approximant, domain="TD")
        total_mass = (lookup_mass1(lal_params) + lookup_mass2(lal_params)).to(u.Msun).value
        params["times"] = SecondtoMass(np.array(hp_lal.times), total_mass)
        return GeneratePolarizations(parameters=params, approximant=wf_approximant, domain=domain)

    interface = params.pop("interface", None)
    lalsuite = params.pop("lalsuite", None)
    use_exact_epoch = params.pop("use_exact_epoch", None)

    if "condition" not in params:
        params["condition"] = 0 if domain == "TD" else 1
    elif domain == "FD":
        params["condition"] = 1

    # Use C interface of lalsuite
    if interface == "c":
        # Translate prec_version and final_spin_version to laldict options
        if "prec_version" in params:
            prec_version = params["prec_version"].lower()
            if "TP" in approximant and prec_version != "numerical":
                params["PrecVersion"] = {"nnlo": 10210, "msa": 22310}[prec_version]
            if "XP" in approximant and prec_version != "msa":
                params["PrecVersion"] = {"nnlo": 102, "numerical": 320}[prec_version]
            params.pop("prec_version")
        if "final_spin_version" in params:
            params["FinalSpinMod"] = params.pop("final_spin_version")

        # Convert the input arguments into a lal dictionary.
        lalparams = gws.core.utils.to_lal_dict(params)

        # Get lalsim.approximant
        if approximant == "NR_hdf5" and "nrfile" in params:
            lal_approx = lalsim.SimInspiralGetApproximantFromString("NR_hdf5")
            lalsim.SimInspiralWaveformParamsInsertNumRelData(lalparams, params["nrfile"])
        else:
            lal_approx = lalsim.SimInspiralGetApproximantFromString(wf_approximant)

        # Generate waveforms in TD or FD
        if domain == "TD":
            generator = lalsim.SimInspiralChooseGenerator(lal_approx, lalparams)
            hp, hc = lalsim.SimInspiralGenerateTDWaveform(lalparams, generator)
            if use_exact_epoch:
                shift = hp.f0
            else:
                shift = hp.epoch.gpsSeconds + hp.epoch.gpsNanoSeconds / 1e9
            times = np.arange(len(hp.data.data)) * hp.deltaT + shift
            # Retrun gwpy series
            return (
                TimeSeries(hp.data.data, times=times, name="hp", unit="strain"),
                TimeSeries(hc.data.data, times=times, name="hc", unit="strain"),
            )
        elif domain == "FD":
            # GenerateFDWaveform does not support TD approximants yet
            # hp, hc = lalsim.SimInspiralGenerateFDWaveform(lalparams, generator)
            (
                m1,
                m2,
                s1x,
                s1y,
                s1z,
                s2x,
                s2y,
                s2z,
                distance,
                inclination,
                phiRef,
                longAscNodes,
                eccentricity,
                meanPerAno,
                deltaF,
                f_min,
                f_max,
                f_ref,
            ) = lalsim.SimInspiralParseDictionaryToChooseFDWaveform(lalparams)
            if f_max == 0:
                if lal.DictContains(lalparams, "deltaT") == 0:
                    raise SyntaxError("Need to provide f_max or deltaT")
                else:
                    f_max = 0.5 / lal.DictLookupREAL8Value(lalparams, "deltaT")
            hp, hc = lalsim.SimInspiralFD(
                m1=m1,
                m2=m2,
                S1x=s1x,
                S1y=s1y,
                S1z=s1z,
                S2x=s2x,
                S2y=s2y,
                S2z=s2z,
                distance=distance,
                inclination=inclination,
                LALparams=lalparams,
                phiRef=phiRef,
                f_ref=f_ref,
                deltaF=deltaF,
                f_min=f_min,
                f_max=f_max,
                longAscNodes=longAscNodes,
                eccentricity=eccentricity,
                meanPerAno=meanPerAno,
                approximant=lal_approx,
            )
            frequencies = np.arange(len(hp.data.data)) * hp.deltaF
            # Retrun gwpy series
            return (
                FrequencySeries(hp.data.data, frequencies=frequencies, name="hp", unit=u.Unit("strain") * u.s, epoch=hp.epoch),
                FrequencySeries(hc.data.data, frequencies=frequencies, name="hc", unit=u.Unit("strain") * u.s, epoch=hp.epoch),
            )
        else:
            raise SyntaxError(f"domain {domain} not valid, options are TD or FD.")

    # Use gwsignal interface
    elif interface == "gwsignal":
        # FIXME gwsignal does not support flexible input parameters
        params = ToComponentMassesCartesianSpins(params, use_spin_vectors=False)

        if lalsuite is True:
            # Use lal approximant through gwsignal
            generator = gws.gwsignal_get_waveform_generator(wf_approximant)
        else:
            # Use phenomxpy through gwsignal
            generator = getattr(import_module("phenomxpy.gwsignal_wrapper"), "Py" + wf_approximant)()

        if domain == "TD":
            hp, hc = gws.core.waveform.GenerateTDWaveform(params, generator)
            hp.override_unit("strain")
            hc.override_unit("strain")
        elif domain == "FD":
            hp, hc = gws.core.waveform.GenerateFDWaveform(params, generator)
            hp.override_unit(u.Unit("strain") * u.s)
            hc.override_unit(u.Unit("strain") * u.s)

        if return_generator:
            return hp, hc, generator

        return hp, hc

    # Use phenomxpy interface
    elif interface == "phenomxpy":
        # Convert from gwsignal to phenomxpy paramters
        params = convert_params_from_gwsignal(params)

        # Choose and initialize class with parameters
        phen = getattr(phenomxpy, wf_approximant)(**params)

        # Evaluate polarizations in time/frequency array. Return gwpy series
        if domain == "TD":
            hp, hc, times = phen.compute_polarizations(times=params.get("times", None))

            hp = TimeSeries(hp, times=times, name="hp", unit="strain")
            hc = TimeSeries(hc, times=times, name="hc", unit="strain")

        elif domain == "FD":
            hp, hc, frequencies = phen.compute_fd_polarizations(**params)

            hp = FrequencySeries(hp, frequencies=frequencies, name="hp", unit=u.Unit("strain") * u.s, epoch=phen.epoch)
            hc = FrequencySeries(hc, frequencies=frequencies, name="hc", unit=u.Unit("strain") * u.s, epoch=phen.epoch)

        if return_generator:
            return hp, hc, phen

        return hp, hc


def bilby_frequency_phenomt(
    frequency_array,
    mass_1,
    mass_2,
    luminosity_distance,
    theta_jn,
    phase,
    a_1=0.0,
    a_2=0.0,
    tilt_1=0.0,
    tilt_2=0.0,
    phi_12=0.0,
    phi_jl=0.0,
    **waveform_kwargs,
):
    """
    frequency_domain_model for bilby waveform generator.
    """

    reference_frequency = waveform_kwargs["reference_frequency"]
    minimum_frequency = waveform_kwargs["minimum_frequency"]
    maximum_frequency = frequency_array[-1]
    approximant = waveform_kwargs["approximant"]

    delta_f = frequency_array[1] - frequency_array[0]
    npoints = int(2 * maximum_frequency / delta_f)
    delta_t = 0.5 / maximum_frequency

    frequency_bounds = (frequency_array >= minimum_frequency) * (frequency_array <= maximum_frequency)

    iota, spin_1x, spin_1y, spin_1z, spin_2x, spin_2y, spin_2z = bilby_to_lalsimulation_spins(
        theta_jn=theta_jn,
        phi_jl=phi_jl,
        tilt_1=tilt_1,
        tilt_2=tilt_2,
        phi_12=phi_12,
        a_1=a_1,
        a_2=a_2,
        mass_1=mass_1,
        mass_2=mass_2,
        reference_frequency=reference_frequency,
        phase=phase,
    )

    params = {
        "total_mass": mass_1 + mass_2,
        "eta": mass_1 * mass_2 / (mass_1 + mass_2) ** 2,
        "s1": [spin_1x, spin_1y, spin_1z],
        "s2": [spin_2x, spin_2y, spin_2z],
        "inclination": iota,
        "distance": luminosity_distance,
        "phi_ef": phase,
        "f_min": minimum_frequency,
        "f_ref": reference_frequency,
        "delta_t": delta_t,
        "delta_f": delta_f,
        "condition": 1,
    }

    phen = getattr(phenomxpy, approximant)(**params)
    h_plus, h_cross, _ = phen.compute_fd_polarizations()

    diff_points = npoints - len(h_plus)
    if diff_points > 0:
        h_plus = np.pad(h_plus, (0, diff_points))
        h_cross = np.pad(h_cross, (0, diff_points))
    elif diff_points < 0:
        h_plus = h_plus[:npoints]
        h_cross = h_cross[:npoints]

    h_plus = h_plus[: len(frequency_array)]
    h_cross = h_cross[: len(frequency_array)]

    h_plus *= frequency_bounds
    h_cross *= frequency_bounds

    dt = 1 / delta_f + phen.epoch
    time_shift = np.exp(-1j * 2 * np.pi * dt * frequency_array[frequency_bounds])
    h_plus[frequency_bounds] *= time_shift
    h_cross[frequency_bounds] *= time_shift

    return dict(plus=h_plus, cross=h_cross)
