"""Module for factory class used to generate unittest case class to test
WCS endpoints from a THREDDS catalogue
"""
__author__ = "P J Kershaw"
__date__ = "06/12/17"
__copyright__ = "(C) 2017 Science and Technology Facilities Council"
__license__ = """BSD - See LICENSE file in top-level directory"""
__contact__ = "Philip.Kershaw@stfc.ac.uk"
import unittest
import logging

import six

from ceda.tds_ogc_scan.validation import OgcTdsValidation
from ceda.tds_ogc_scan.test.factory import ThreddsCatalogUnittestCaseFactory

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class TdsWcsUnittestMethodFactory:
    '''Factory class in order to maintain start with WCS URIs'''
    def __init__(self, catalog_ref_uri):
        self.catalog_ref_uri = catalog_ref_uri

    def __call__(self):
        '''This becomes a test method in newly generated unittest case class'''
        log.info('+'*80) 
        log.info('Testing WCS endpoints from {!r}'.format(
                self.catalog_ref_uri))

        if not isinstance(self.catalog_ref_uri, six.string_types):
            raise AssertionError("Expecting string type for THREDDS "
                                "Catalogue URI {!r}; got {} type".format(
                                self.catalog_ref_uri, 
                                type(self.catalog_ref_uri)))

        wcs_uri = OgcTdsValidation.get_wcs_uri_from_catalog(
                                                        self.catalog_ref_uri)

        wcs_get_capabilities_uri = "{}{}".format(wcs_uri,
                OgcTdsValidation.WCS_GET_CAPABILITIES_QUERY_ARGS)

        (
            wcs_get_capabilities_resp_ok,
            layer_names
        ) = OgcTdsValidation.check_wcs_get_capabilities_resp(
                                                wcs_get_capabilities_uri)
        if not wcs_get_capabilities_resp_ok:
            raise AssertionError("WCS GetCapabilities call failed for "
                                 "{!r}".format(wcs_get_capabilities_uri))

        wcs_describe_coverage_uri = "{}{}".format(wcs_uri,
                            OgcTdsValidation.WCS_DESCRIBE_COVERAGE_QUERY_ARGS)

        (
            wcs_describe_coverage_resp_ok,
            layer_names
        ) = OgcTdsValidation.check_wcs_describe_coverage_resp(
                                                    wcs_describe_coverage_uri)
        if not wcs_describe_coverage_resp_ok:
            raise AssertionError("WCS DescribeCoverage call failed for "
                                 "{!r}".format(wcs_describe_coverage_uri))

        log.info('WCS tests passed for {!r}'.format(self.catalog_ref_uri))


def tds_wcs_testcase_factory(catalog_uri):
    '''Create TDS WCS TestCase class'''
    unittest_case_factory = ThreddsCatalogUnittestCaseFactory(
                                        catalog_uri,
                                        TdsWcsUnittestMethodFactory)
    return unittest_case_factory()
    
        
if __name__ == '__main__':
    import os
    catalog_uri = (os.getenv('CEDA_TDS_OGC_SCAN_CATALOG_URI') or
        'https://cci-odp-data.cems.rl.ac.uk/thredds/catalog.xml'
    )

    TdsWcsTestCase = tds_wcs_testcase_factory()
    unittest.main()