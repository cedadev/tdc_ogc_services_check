"""OGC services validation for TDS catalogue content - CEDA namespace package
"""
__author__ = "P J Kershaw"
__date__ = "23/09/16"
__copyright__ = "(C) 2016 Science and Technology Facilities Council"
__license__ = """BSD - See LICENSE file in top-level directory"""
__contact__ = "Philip.Kershaw@stfc.ac.uk"
__revision__ = '$Id$'
try:
    import pkg_resources
    pkg_resources.declare_namespace(__name__)
except ImportError:
    # don't prevent use if pkg_resources isn't installed
    from pkgutil import extend_path
    __path__ = extend_path(__path__, __name__) 

import modulefinder
for p in __path__:
    modulefinder.AddPackagePath(__name__, p)