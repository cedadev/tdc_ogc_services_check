#!/usr/bin/env python
"""OGC services validation for TDS catalogue content
"""
__author__ = "P J Kershaw"
__date__ = "26/10/12"
__copyright__ = "(C) 2016 Science and Technology Facilities Council"
__license__ = """BSD - See LICENSE file in top-level directory"""
__contact__ = "Philip.Kershaw@stfc.ac.uk"
__revision__ = '$Id$'
import logging

from ceda.tds_ogc_scan.validation import OgcTdsValidation


def main():
    OgcTdsValidation.check(uri)
 
   
if __name__ == '__main__':
    import sys
    import os

    logging.basicConfig(level=logging.INFO)
    
    # Suppress requests logging
    requests_logger = logging.getLogger(
                                    'requests.packages.urllib3.connectionpool')
    requests_logger.setLevel(logging.WARNING)
    
    if len(sys.argv) < 2:
        raise SystemExit('Usage: {} <URI to TDS catalogue path to scan>'.format(
                                                    os.path.basename(__file__)))
    else:
        uri = sys.argv[1]

    main()
