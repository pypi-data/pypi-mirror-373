# Copyright (C) 2023  Cecilio García Quirós
"""
Define generators to interface with gwsignal.
"""

try:
    from lalsimulation.gwsignal.core.waveform import CompactBinaryCoalescenceGenerator
    import astropy.units as u
    from gwpy.timeseries import TimeSeries
    from gwpy.frequencyseries import FrequencySeries
except:
    raise ImportWarning("Cannot use gwsignal interface for phenomxpy.")

import phenomxpy
from phenomxpy.utils import convert_params_from_gwsignal, parse_options_from_approximant_name


class PyIMRPhenomT(CompactBinaryCoalescenceGenerator):
    """
    gwsignal generator wrapper for the IMRPhenomT model.

    This is the parent class from which all the other IMRPhenomT* models subclass.

    Example usage:

    .. code-block:: python

        from lalsimulation import gwsignal as gws

        gen = PyIMRPhenomT()
        hp, hc = gws.core.waveform.GenerateTDWaveform(params, gen)
    """

    def __init__(self, **kwargs):

        self._domain = "time"
        self._implemented_domain = "time"
        self._generation_domain = None
        self._approximant = "IMRPhenomT"
        # This imports the corresponding Phenom class but doesn't create the instance.
        # Instances are created inside the methods `generate_td_waveform`, etc.
        self._class = getattr(phenomxpy, self._approximant)

    @property
    def metadata(self):
        return self._class.metadata()

    def _evaluate_class(self, **parameters):
        """
        Create instance of the IMRPhenom class (initialization of coefficients).
        """

        # Convert from gwsiganl dictionary to phenomxpy dictionary
        self.waveform_dict = convert_params_from_gwsignal(parameters)

        return self._class(**self.waveform_dict)

    def generate_td_waveform(self, **parameters):
        """
        Compute time domain polarizations.
        """

        # Create instance of the class (initialization of coefficients)
        self.phen = self._evaluate_class(**parameters)

        # Compute polarizations (evaluation in time array)
        hp, hc, times = self.phen.compute_polarizations()

        # Return gwpy series
        return (
            TimeSeries(hp, times=times, name="hp", unit="strain"),
            TimeSeries(hc, times=times, name="hc", unit="strain"),
        )

    def generate_fd_waveform(self, **parameters):
        """
        Compute Fourier domain polarizations.
        """

        # Create instance of the class (initialization of coefficients)
        self.phen = self._evaluate_class(**parameters)

        # Compute polarizations in Fourier domain. Computes the conditioned TD polarizations and Fourier transform them
        hp, hc, frequencies = self.phen.compute_fd_polarizations()

        # Retrun gwpy series
        return (
            FrequencySeries(hp, frequencies=frequencies, name="hp", unit=u.Unit("strain") * u.s, epoch=self.phen.epoch),
            FrequencySeries(hc, frequencies=frequencies, name="hc", unit=u.Unit("strain") * u.s, epoch=self.phen.epoch),
        )


class PyIMRPhenomTHM(PyIMRPhenomT):
    """
    gwsignal generator wrapper for the IMRPhenomTHM model.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._approximant = "IMRPhenomTHM"
        self._class = getattr(phenomxpy, self._approximant)


class PyIMRPhenomTP(PyIMRPhenomT):
    """
    gwsignal generator wrapper for the IMRPhenomTP model.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._approximant = "IMRPhenomTP"
        self._class = getattr(phenomxpy, self._approximant)


class PyIMRPhenomTPHM(PyIMRPhenomT):
    """
    gwsignal generator wrapper for the IMRPhenomTPHM model.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._approximant = "IMRPhenomTPHM"
        self._class = getattr(phenomxpy, self._approximant)


class PyIMRPhenomTFamily(PyIMRPhenomT):
    """
    gwsignal generator wrapper for the IMRPhenomTFamily.

    This class permits to use all the models in the IMRPhenomT family with the same generator.
    One needs to specify the `approximant` name in the input parameters.

    Example usage:

    .. code-block:: python

        gen = PyIMRPhenomTFamily()

        params["approximant"] = "IMRPhenomTHM"
        hp, hc = gws.core.waveform.GenerateTDWaveform(params, gen)

        params["approximant"] = "IMRPhenomTPHM"
        hp, hc = gws.core.waveform.GenerateTDWaveform(params, gen)

    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._approximant = "IMRPhenomTFamily"

    @property
    def metadata(self):
        return {
            "type": "aligned_spin, precessing",
            "f_ref_spin": True,
            "modes": True,
            "polarizations": True,
            "implemented_domain": "time",
            "approximant": "IMRPhenomTFamily",
            "implementation": "",
            "conditioning_routines": "",
        }

    def _evaluate_class(self, **parameters):

        # Update parameters with options read from approximant name
        # Returns approximant name without options, i.e. IMRPhenomT, IMRPhenomTHM, ...
        approx_wo_options = parse_options_from_approximant_name(parameters)

        # Choose appropiate phenomxpy class from approximant name
        try:
            self._class = getattr(phenomxpy, approx_wo_options)
        except KeyError as e:
            raise KeyError(f"Using PyIMRPhenomTFamily needs to provide `approximant` key in `parameters`.") from e

        self.waveform_dict = convert_params_from_gwsignal(parameters)

        return self._class(**self.waveform_dict)
