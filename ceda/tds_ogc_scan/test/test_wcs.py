"""Module for factory class used to generate unittest case class to test
WCS endpoints from a THREDDS catalogue
"""
__author__ = "P J Kershaw"
__date__ = "06/12/17"
__copyright__ = "(C) 2017 Science and Technology Facilities Council"
__license__ = """BSD - See LICENSE file in top-level directory"""
__contact__ = "Philip.Kershaw@stfc.ac.uk"
import six

from ceda.tds_ogc_scan.validation import OgcTdsValidation
from ceda.tds_ogc_scan.test.factory import ThreddsCatalogUnittestCaseFactory


class WcsGetCapabilitiesUnittestMethodFactory:
    '''Factory class in order to maintain start with WCS URIs'''
    def __init__(self, catalog_ref_uri):
        self.catalog_ref_uri = catalog_ref_uri

    def __call__(self):
        '''This becomes a test method in newly generated unittest case class'''
        assert isinstance(self.catalog_ref_uri, six.string_types)

        wcs_uri = OgcTdsValidation.get_wcs_uri_from_catalog(
                                                        self.catalog_ref_uri)

        wcs_get_capabilities_uri = "{}{}".format(wcs_uri,
                OgcTdsValidation.WCS_GET_CAPABILITIES_QUERY_ARGS)

        if wcs_get_capabilities_uri == ('https://cci-odp-data.cems.rl.ac.uk/'
                                        'thredds/wcs/esacci.OC.8-days.L3S.IOP.'
                                        'multi-sensor.multi-platform.MERGED.'
                                        '2-0.r1.v20170120?service=WCS&'
                                        'version=1.0.0&'
                                        'request=GetCapabilities'):
            pass

        (
            wcs_get_capabilities_resp_ok,
            layer_names
        ) = OgcTdsValidation.check_wcs_get_capabilities_resp(
                                                wcs_get_capabilities_uri)
        assert wcs_get_capabilities_resp_ok

        wcs_describe_coverage_uri = "{}{}".format(wcs_uri,
                            OgcTdsValidation.WCS_DESCRIBE_COVERAGE_QUERY_ARGS)

        (
            wcs_describe_coverage_resp_ok,
            layer_names
        ) = OgcTdsValidation.check_wcs_describe_coverage_resp(
                                                    wcs_describe_coverage_uri)
        assert wcs_describe_coverage_resp_ok

        print('Tested {}'.format(self.catalog_ref_uri))


import os
catalog_uri = (os.getenv('CEDA_TDS_OGC_SCAN_CATALOG_URI') or
    'http://cci-odp-data.cems.rl.ac.uk/thredds/catalog.xml'
)

unittest_case_factory = ThreddsCatalogUnittestCaseFactory(
                                    catalog_uri,
                                    WcsGetCapabilitiesUnittestMethodFactory)

TdsOgcServicesCheckWcsTestCase = unittest_case_factory()