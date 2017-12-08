"""Module for factory class used to generate unittest case classes for testing
service endpoints from a THREDDS catalogue
"""
__author__ = "P J Kershaw"
__date__ = "06/12/17"
__copyright__ = "(C) 2017 Science and Technology Facilities Council"
__license__ = """BSD - See LICENSE file in top-level directory"""
__contact__ = "Philip.Kershaw@stfc.ac.uk"
import unittest

from ceda.tds_ogc_scan.validation import OgcTdsValidation


class ThreddsCatalogUnittestCaseFactory:
    '''Create a unittest case class for testing endpoints from a THREDDS
    catalogue
    '''
    def __init__(self, catalog_uri, unittest_method_factory):
        '''Provide the URI to the THREDDS catalogue + a class factory which
        generates the tests needed
        '''
        self.catalog_uri = catalog_uri
        self.unittest_method_factory = unittest_method_factory

    def _gen_unittest_method_factories(self):
        '''Make a list of unittest methods based contents of a THREDDS catalogue
        '''
        catalog_ref_uris = OgcTdsValidation.get_catalog_ref_uris(
                                                            self.catalog_uri)
        for catalog_ref_uri in catalog_ref_uris:
            unittest_method_factory = self.unittest_method_factory(
                                                                catalog_ref_uri)

            yield unittest_method_factory

    def  __call__(self):
        '''Generate new unittest case class from a list of unittest methods
        generated from unittest_method_factory'''
        _attr = {}
        method_factories = self._gen_unittest_method_factories()
        for i, unittest_method_factory in enumerate(method_factories, start=1):
            def _test_method(self):
                '''Wrapper to satisfy
                unittest.defaultTestLoader.loadTestsFromName which expects
                unittest methods to be of type types.FunctionType

                It also enables passing an instance of the unittest case class
                to the test method - 'self' variable
                '''
                unittest_method_factory(self)

            _attr['test_{:03d}'.format(i)] = _test_method

        TdsCatalogServiceTestCase = type('TdsCatalogServiceTestCase',
                                         (unittest.TestCase, ), _attr)
        return TdsCatalogServiceTestCase
