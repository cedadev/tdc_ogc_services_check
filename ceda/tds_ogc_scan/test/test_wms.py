"""Module for factory class used to generate unittest case class to test
WMS endpoints from a THREDDS catalogue
"""
import unittest
__author__ = "P J Kershaw"
__date__ = "06/12/17"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = """BSD - See LICENSE file in top-level directory"""
__contact__ = "Philip.Kershaw@stfc.ac.uk"
import six
import logging

from ceda.tds_ogc_scan.validation import OgcTdsValidation
from ceda.tds_ogc_scan.test.factory import ThreddsCatalogUnittestCaseFactory

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

        
class TdsWmsUnittestMethodFactory:
    '''Unit test method factory creates a test method for a WMS endpoint from 
    a given THREDDS Catalogue URI'''
    
    def __init__(self, catalog_ref_uri):
        self.catalog_ref_uri = catalog_ref_uri
        
        # Required for unittest.loader.TestLoader
        if not getattr(self, '__qualname__', None):
            self.__qualname__ = 'tds_wms_test'
 
    def __call__(self):
        '''This becomes a test method in newly generated unittest case class'''
        log.info('+'*80) 
        log.info('Testing WMS endpoints for {!r}'.format(
                self.catalog_ref_uri))

        if not isinstance(self.catalog_ref_uri, six.string_types):
            raise AssertionError(
                "Expecting string type for THREDDS Catalogue URI {!r}; got {}"
                " type".format(self.catalog_ref_uri, 
                               type(self.catalog_ref_uri)))
 
        wms_uri = OgcTdsValidation.get_wms_uri_from_catalog(
                                                        self.catalog_ref_uri)
        if wms_uri is None:
            # No WMS endpoint
            return
            
        wms_get_capabilities_uri = "{}{}".format(wms_uri,
                OgcTdsValidation.WMS_GET_CAPABILITIES_QUERY_ARGS)
 
        (
            wms_get_capabilities_resp_ok,
            layer_names
        ) = OgcTdsValidation.check_wms_get_capabilities_resp(
                                                wms_get_capabilities_uri)
        if not wms_get_capabilities_resp_ok:
            raise AssertionError("WMS GetCapabilities call failed for "
                                 "{!r}".format(wms_get_capabilities_uri))
        
        if len(layer_names) > 0:
            query_args = OgcTdsValidation.WMS_GET_MAP_QUERY_ARGS.format(
                                                            layer_names[0])
            wms_get_map_uri = "{}{}".format(wms_uri, query_args)
 
            wms_get_map_resp_ok = OgcTdsValidation.check_wms_get_map_resp(
                                                            wms_get_map_uri)
            if not wms_get_map_resp_ok:
                raise AssertionError("WMS GetMap call failed for {!r}".format(
                                         wms_get_map_uri))

        log.info('WMS tests passed for {!r}'.format(self.catalog_ref_uri))


def tds_wms_testcase_factory(catalog_uri):
    '''Create TDS WMS TestCase class'''
    unittest_case_factory = ThreddsCatalogUnittestCaseFactory(
                                                catalog_uri,
                                                TdsWmsUnittestMethodFactory)
    
    return unittest_case_factory()


if __name__ == '__main__':
    import os
    catalog_uri = (
        os.getenv('CEDA_TDS_OGC_SCAN_CATALOG_URI') or
        'https://cci-odp-data.ceda.ac.uk/thredds/esacci/catalog.xml'
    )
     
    TdsWmsTestCase = tds_wms_testcase_factory(catalog_uri)
    unittest.main()