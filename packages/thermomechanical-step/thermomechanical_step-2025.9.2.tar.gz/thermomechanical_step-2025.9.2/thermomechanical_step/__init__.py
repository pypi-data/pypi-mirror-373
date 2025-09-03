# -*- coding: utf-8 -*-

"""
thermomechanical_step
A SEAMM plug-in for calculating thermomechanical properties
"""

# Bring up the classes so that they appear to be directly in
# the thermomechanical_step package.

from .thermomechanical import Thermomechanical  # noqa: F401, E501
from .thermomechanical_parameters import ThermomechanicalParameters  # noqa: F401, E501
from .thermomechanical_step import ThermomechanicalStep  # noqa: F401, E501
from .tk_thermomechanical import TkThermomechanical  # noqa: F401, E501

from .metadata import metadata  # noqa: F401

# Handle versioneer
from ._version import get_versions

__author__ = "Paul Saxe"
__email__ = "psaxe@molssi.org"
versions = get_versions()
__version__ = versions["version"]
__git_revision__ = versions["full-revisionid"]
del get_versions, versions
