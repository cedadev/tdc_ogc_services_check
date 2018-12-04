#!/usr/bin/env python
"""OGC services validation for TDS catalogue content
"""
__author__ = "P J Kershaw"
__date__ = "26/10/12"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = """BSD - See LICENSE file in top-level directory"""
__contact__ = "Philip.Kershaw@stfc.ac.uk"
__revision__ = '$Id$'
import sys
import os
import logging

from ceda.tds_ogc_scan.validation import OgcTdsValidation


def main():
    logging.basicConfig(level=logging.INFO)

    # Suppress requests logging
    requests_logger = logging.getLogger(
                                    'requests.packages.urllib3.connectionpool')
    requests_logger.setLevel(logging.WARNING)

    if len(sys.argv) < 2:
        raise SystemExit('Usage: {} <URI to TDS catalogue path to scan> '
                         '(<list of catalogue entries to test>|'
                         '<test n random sample of entries from the '
                         'catalogue>)'.format(os.path.basename(sys.argv[0])))
    else:
        uri = sys.argv[1]

    if len(sys.argv) > 2:
        if sys.argv[2].isdigit():
            rand_sample = int(sys.argv[2])
            catalog_entries_filter = None
        else:
            rand_sample = None
            catalog_entries_filter = sys.argv[2:]
    else:
        catalog_entries_filter = None
        rand_sample = None

    status = OgcTdsValidation.check(uri,
                             catalog_entries_filter=catalog_entries_filter,
                             rand_sample=rand_sample)
    sys.exit(status)


if __name__ == '__main__':
    main()

