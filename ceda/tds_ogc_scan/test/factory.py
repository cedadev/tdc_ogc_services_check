"""Module for factory class used to generate unittest case classes for testing
service endpoints from a THREDDS catalogue
"""
__author__ = "P J Kershaw"
__date__ = "06/12/17"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = """BSD - See LICENSE file in top-level directory"""
__contact__ = "Philip.Kershaw@stfc.ac.uk"
import unittest

from ceda.tds_ogc_scan.validation import OgcTdsValidation


class ThreddsCatalogUnittestCaseFactory:
    '''Create a unittest case class for testing endpoints from a THREDDS
    catalogue
    '''
    def __init__(self, catalog_uri, unittest_method_factory):
        '''Provide the URI to the THREDDS catalogue + a unit test method
        factory which generates the tests needed
        '''
        self.catalog_uri = catalog_uri
        self.unittest_method_factory = unittest_method_factory

    def _gen_unittest_methods(self):
        '''Make a list of unittest methods based on contents of a THREDDS 
        catalogue
        '''
        catalog_ref_uris = OgcTdsValidation.get_catalog_ref_uris(
                                                            self.catalog_uri)
        for catalog_ref_uri in catalog_ref_uris:
            unittest_method = self.unittest_method_factory(catalog_ref_uri)

            yield unittest_method

    def  __call__(self):
        '''Generate new unittest case class from a list of unittest methods
        generated from unittest_method_factory'''
        _attr = {}
        method_factories = self._gen_unittest_methods()
        for i, unittest_method in enumerate(method_factories, start=1):
            _attr['test_{:03d}'.format(i)] = unittest_method

        TdsCatalogServiceTestCase = type('TdsCatalogServiceTestCase',
                                         (unittest.TestCase, ), _attr)
        return TdsCatalogServiceTestCase
