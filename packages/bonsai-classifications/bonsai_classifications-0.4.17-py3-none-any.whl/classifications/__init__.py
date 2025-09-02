import sys

from ._pint_units import get_unit_registry
from ._utils import convert_currency, create_conc, get_concordance
from .core import (
    activitytype,
    dataquality,
    flow,
    flowobject,
    location,
    time,
    uncertainty,
    unit_magnitude,
    unit_monetary,
    unit_physical,
)

# NOTE: Do not edit from here downward
# Create package version number from git tag
if sys.version_info[:2] >= (3, 8):
    from importlib.metadata import PackageNotFoundError, version
else:
    from importlib_metadata import PackageNotFoundError, version

# Change package version if project is renamed
try:
    dist_name = __name__
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError, dist_name, sys
