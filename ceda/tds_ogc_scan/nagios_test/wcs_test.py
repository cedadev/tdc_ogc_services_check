#!/usr/bin/env python
"""Nagios script to test CCI Open Data Portal WCS service
"""
__author__ = "P J Kershaw"
__date__ = "08/12/17"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = """BSD - See LICENSE file in top-level directory"""
__contact__ = "Philip.Kershaw@stfc.ac.uk"
import os

from ceda.unittest_nagios_wrapper.script import nagios_script
from ceda.tds_ogc_scan.test.test_wcs import tds_wcs_testcase_factory


def main():
    '''Entry point for script - use standard nagios script'''

    # These options can be overridden by the CLI options
    SLACK_CHANNEL = 'cci-odp-ops-logging'
    SLACK_USER = 'cci-ops-test'

    catalog_uri = (os.getenv('CEDA_TDS_OGC_SCAN_CATALOG_URI') or
        'https://cci-odp-data.cems.rl.ac.uk/thredds/catalog.xml'
    )
    TdsWcsTestCase = tds_wcs_testcase_factory(catalog_uri)
    
    nagios_script(TdsWcsTestCase, check_name='CCI_WCS_TEST',
                  slack_channel=SLACK_CHANNEL, slack_user=SLACK_USER)


if __name__ == '__main__':
    main()
