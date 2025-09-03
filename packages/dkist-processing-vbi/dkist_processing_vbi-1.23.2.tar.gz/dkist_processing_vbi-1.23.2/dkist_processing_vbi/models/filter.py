"""VBI filter list and tooling."""

import astropy.units as u
from dkist_processing_common.models.wavelength import WavelengthRange


class Filter(WavelengthRange):
    """
    VBI filter data structure.

    Parameters
    ----------
    name
        The name of the filter
    """

    name: str


VBI_FILTERS = [
    Filter(name="VBI-Blue Ca II K", min=393.276 * u.nm, max=393.378 * u.nm),
    Filter(name="VBI-Blue G-Band", min=430.301 * u.nm, max=430.789 * u.nm),
    Filter(name="VBI-Blue Continuum", min=450.084 * u.nm, max=450.490 * u.nm),
    Filter(name="VBI-Blue H-Beta", min=486.116 * u.nm, max=486.162 * u.nm),
    Filter(name="VBI-Red H-alpha", min=656.258 * u.nm, max=656.306 * u.nm),
    Filter(name="VBI-Red Continuum", min=668.202 * u.nm, max=668.644 * u.nm),
    Filter(name="VBI-Red Ti O", min=705.545 * u.nm, max=706.133 * u.nm),
    Filter(name="VBI-Red Fe IX", min=789.168 * u.nm, max=789.204 * u.nm),
]


def find_associated_filter(wavelength: u.Quantity) -> Filter:
    """
    Given a wavelength, find the Filter that contains that wavelength between its wavemin/wavemax.

    Parameters
    ----------
    wavelength
        The wavelength to use in the search

    Returns
    -------
    A Filter object that contains the wavelength
    """
    matching_filters = [f for f in VBI_FILTERS if f.min <= wavelength <= f.max]
    if len(matching_filters) == 1:
        return matching_filters[0]
    raise ValueError(f"Found {len(matching_filters)} matching filters when 1 was expected.")
