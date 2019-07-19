'''
Created on 27 Nov 2017

@author: philipkershaw
'''
import os
import unittest

import six

from ceda.tds_ogc_scan.validation import OgcTdsValidation


class TdsOgcServicesCheckTestCase(unittest.TestCase):
    TDS_CATALOG_URI = (
        os.getenv('CEDA_TDS_OGC_SCAN_CATALOG_URI') or
        'https://cci-odp-data.ceda.ac.uk/thredds/esacci/catalog.xml'
    )

    def test01_parse_thredds_catalog(self):
        validation = OgcTdsValidation()

        catalog_elems = validation.parse_thredds_catalog(
            self.__class__.TDS_CATALOG_URI)

        self.assertGreater(len(catalog_elems), 0,
                           msg="No elements found in THREDDS catalogue "
                               "{!r}".format(self.__class__.TDS_CATALOG_URI))

    def test02_get_catalog_ref_uris(self):
        for catalog_ref_uri in OgcTdsValidation.get_catalog_ref_uris(
                                            self.__class__.TDS_CATALOG_URI):
            self.assertIsInstance(catalog_ref_uri, six.string_types,
                                  'Expecting string type for catalogue '
                                  'reference URI, got '
                                  '{!r}'.format(catalog_ref_uri))


