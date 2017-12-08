#!/usr/bin/env python
"""Nagios script to test CCI Open Data Portal WCS service
"""
__author__ = "P J Kershaw"
__date__ = "08/12/17"
__copyright__ = "(C) 2017 Science and Technology Facilities Council"
__license__ = """BSD - See LICENSE file in top-level directory"""
__contact__ = "Philip.Kershaw@stfc.ac.uk"
__revision__ = '$Id$'
from ceda.unittest_nagios_wrapper.script import nagios_script
from ceda.tds_ogc_scan.test.test_wcs import TdsCatalogServiceTestCase
import ceda.tds_ogc_scan.test.test_wcs


def main():
    '''Entry point for script - use standard nagios script'''

    # These options can be overridden by the CLI options
    SLACK_CHANNEL = 'cci-odp-ops-logging'
    SLACK_USER = 'cci-ops-test'

    nagios_script(TdsCatalogServiceTestCase, check_name='CCI_WCS_TEST',
                  unittest_module=ceda.tds_ogc_scan.test.test_wcs,
                  slack_channel=SLACK_CHANNEL, slack_user=SLACK_USER)


if __name__ == '__main__':
    main()
