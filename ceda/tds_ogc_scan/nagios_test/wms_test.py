#!/usr/bin/env python
"""Nagios script to test CCI Open Data Portal WMS service
"""
__author__ = "P J Kershaw"
__date__ = "07/12/17"
__copyright__ = "(C) 2017 Science and Technology Facilities Council"
__license__ = """BSD - See LICENSE file in top-level directory"""
__contact__ = "Philip.Kershaw@stfc.ac.uk"
__revision__ = '$Id$'
from ceda.unittest_nagios_wrapper.script import nagios_script
from ceda.tds_ogc_scan.test.test_wms import tds_wms_testcase_factory
import ceda.tds_ogc_scan.test.test_wms


def main():
    '''Entry point for script - use standard nagios script'''

    # These options can be overridden by the CLI options
    SLACK_CHANNEL = 'cci-odp-ops-logging'
    SLACK_USER = 'cci-ops-test'

    import os
    catalog_uri = (os.getenv('CEDA_TDS_OGC_SCAN_CATALOG_URI') or
        'https://cci-odp-data.cems.rl.ac.uk/thredds/catalog.xml'
    )
    TdsWmsTestCase = tds_wms_testcase_factory(catalog_uri)
    
    nagios_script(TdsWmsTestCase, check_name='CCI_WMS_TEST',
                  slack_channel=SLACK_CHANNEL, slack_user=SLACK_USER)


if __name__ == '__main__':
    main()
