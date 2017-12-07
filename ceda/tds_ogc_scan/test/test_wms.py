"""Module for factory class used to generate unittest case class to test
WMS endpoints from a THREDDS catalogue
"""
__author__ = "P J Kershaw"
__date__ = "06/12/17"
__copyright__ = "(C) 2017 Science and Technology Facilities Council"
__license__ = """BSD - See LICENSE file in top-level directory"""
__contact__ = "Philip.Kershaw@stfc.ac.uk"
import six

from ceda.tds_ogc_scan.validation import OgcTdsValidation
from ceda.tds_ogc_scan.test.factory import ThreddsCatalogUnittestCaseFactory


class WmsGetCapabilitiesUnittestMethodFactory:
    '''Factory class in order to maintain start with WMS URIs'''
    def __init__(self, catalog_ref_uri):
        self.catalog_ref_uri = catalog_ref_uri

    def __call__(self):
        '''This becomes a test method in newly generated unittest case class'''
        assert isinstance(self.catalog_ref_uri, six.string_types)

        wms_uri = OgcTdsValidation.get_wms_uri_from_catalog(
                                                        self.catalog_ref_uri)

        wms_get_capabilities_uri = "{}{}".format(wms_uri,
                OgcTdsValidation.WMS_GET_CAPABILITIES_QUERY_ARGS)

        (
            wms_get_capabilities_resp_ok,
            layer_names
        ) = OgcTdsValidation.check_wms_get_capabilities_resp(
                                                wms_get_capabilities_uri)
        assert wms_get_capabilities_resp_ok

        if len(layer_names) > 0:
            query_args = OgcTdsValidation.WMS_GET_MAP_QUERY_ARGS.format(
                                                                layer_names[0])
            wms_get_map_uri = "{}{}".format(self.wms_uri, query_args)

            wms_get_map_resp_ok = OgcTdsValidation.check_wms_get_map_resp(
                                                            wms_get_map_uri)
            assert wms_get_map_resp_ok

        print('Tested {}'.format(wms_get_capabilities_uri))

import os
catalog_uri = os.getenv('CEDA_TDS_OGC_SCAN_CATALOG_URI')
if catalog_uri is None:
    raise ImportError('CEDA_TDS_OGC_SCAN_CATALOG_URI must be set to target '
                      'THREDDS catalogue URI')

unittest_case_factory = ThreddsCatalogUnittestCaseFactory(
                                    catalog_uri,
                                    WmsGetCapabilitiesUnittestMethodFactory)

TdsOgcServicesCheckWmsTestCase = unittest_case_factory()