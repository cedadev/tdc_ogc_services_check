"""OGC services validation for TDS catalogue content
"""
__author__ = "P J Kershaw"
__date__ = "23/09/16"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = """BSD - See LICENSE file in top-level directory"""
__contact__ = "Philip.Kershaw@stfc.ac.uk"
__revision__ = '$Id$'
import os
import random
from six.moves.urllib.parse import urlparse, urlunparse
import xml.etree.ElementTree as ET
import csv

import requests
import logging

log = logging.getLogger(__name__)


def get_base_uri(uri):
    '''Extract protocol scheme + DNS name from a URI'''
    parsed_uri = urlparse(uri)
    return urlunparse([parsed_uri.scheme, parsed_uri.netloc, '', '', '', ''])


class OgcTdsValidationConfigError(Exception):
    """Error with input configuration"""


class OgcTdsValidation:
    '''Check TDS catalogue and carry out validation steps on OGC endpoints
    published
    '''
    REPORT_FILEPATH = 'wms-error-report.csv'

    WMS_GET_CAPABILITIES_QUERY_ARGS = (
        '?service=WMS&version=1.3.0&request=GetCapabilities'
    )

    WMS_GET_MAP_QUERY_ARGS = (
        '?service=WMS&version=1.3.0&request=GetMap&BBOX=-180,-90,180,90&'
        'LAYERS={}&CRS=CRS:84&WIDTH=256&HEIGHT=256&STYLES=&'
        'FORMAT=image/png&COLORSCALERANGE=auto'
    )

    WCS_GET_CAPABILITIES_QUERY_ARGS = (
        '?service=WCS&version=1.0.0&request=GetCapabilities'
    )

    WCS_DESCRIBE_COVERAGE_QUERY_ARGS = (
        '?service=WCS&version=1.0.0&request=DescribeCoverage'
    )

    WCS_GET_COVERAGE_QUERY_ARGS = (
        '?service=WCS&version=1.0.0&request=GetCoverage&BBOX=-180,-90,180,90&'
        '&CRS=CRS:84&FORMAT=netcdf'
    )

    @classmethod
    def create_report(cls, uri, report_filepath=None):

        if report_filepath is None:
            report_filepath = cls.REPORT_FILEPATH

        with open(report_filepath, 'w', newline=os.linesep) as report_file:
            report_writer = csv.writer(report_file, quoting=csv.QUOTE_MINIMAL,
                                       delimiter='$')

            cls.check(uri, report_writer=report_writer)

        report_file.close()

    @staticmethod
    def parse_thredds_catalog(uri):
        '''Parse thredds Catalogue XML given by input URI and return list
        Catalogue Reference entries as ElementTree elements
        '''
        resp = requests.get(uri)
        root = ET.fromstring(resp.text)

        catalog_ref_elems = root.findall('{http://www.unidata.ucar.edu/'
                                         'namespaces/thredds/InvCatalog/v1.0}'
                                         'catalogRef')

        return catalog_ref_elems

    @classmethod
    def get_catalog_ref_uris(cls, uri):
        catalog_ref_elems = cls.parse_thredds_catalog(uri)

        parsed_uri = urlparse(uri)
        thredds_prefix = urlunparse(
                        [parsed_uri.scheme, parsed_uri.netloc,
                         os.path.dirname(parsed_uri.path), '', '', ''])

        for catalog_ref_elem in catalog_ref_elems:
            catalog_ref_uri_path = catalog_ref_elem.attrib[
                                        '{http://www.w3.org/1999/xlink}href']
            catalog_ref_uri = "{}/{}".format(thredds_prefix,
                                             catalog_ref_uri_path)

            yield catalog_ref_uri

    @classmethod
    def check(cls, uri, catalog_entries_filter=None, rand_sample=None,
              report_writer=None):
        """Iterate through a THREDDS catalogue (given by uri) and test all
        WMS endpoints

        :param uri: THREDDS Catalogue XML HTTP endpoint
        :param catalog_entries_filter: filter individual catalogue entries
        based on this list.  Entries not included will not be tested
        :rand_sample: set to an integer number of sample catalogue elements to
        try out.  The element indices are selected at random.  The number of
        elements picked out is normalised so that is at least one less than the
        total number of elements found in the catalogue.
        """
        catalog_ref_uris = tuple(cls.get_catalog_ref_uris(uri))

        # Initialise stats
        n_wms_get_capabilities_uris_tested = 0
        n_wms_get_capabilities_ok = 0
        n_wms_get_map_uris_tested = 0
        n_wms_get_map_ok = 0

        n_wcs_get_capabilities_uris_tested = 0
        n_wcs_get_capabilities_ok = 0
        n_wcs_describe_coverage_uris_tested = 0
        n_wcs_describe_coverage_ok = 0

        if catalog_entries_filter is not None:
            log.info("Specific catalogue reference elements selected for "
                     "testing: %s", '", "'.join(catalog_entries_filter))

        # Choose whether to iterate over catalogue elements or pick a random
        # sample
        n_catalog_ref_uris = len(catalog_ref_uris)
        if rand_sample is None:
            catalog_ref_indices = range(n_catalog_ref_uris)
        else:
            if catalog_entries_filter is not None:
                raise OgcTdsValidationConfigError("rand_sample and "
                                                  "catalog_entries_filter"
                                                  " keywords can't be set "
                                                  "together")

            n_sample_elems = min(rand_sample, n_catalog_ref_uris)
            catalog_ref_indices = random.sample(range(n_catalog_ref_uris),
                                                n_sample_elems)
            log.info("%d randomly selected elements chosen for testing",
                     n_sample_elems)

        for i in catalog_ref_indices:
            catalog_ref_uri = catalog_ref_uris[i]

            # If filter is set, then only process entries contained in filter
            # list
            if (catalog_entries_filter is not None and
                catalog_ref_uri not in catalog_entries_filter):
                continue

            log.info("+"*46)
            log.info("Testing catalogue reference URI "
                     "{}".format(catalog_ref_uri))

            wms_uri = cls.get_wms_uri_from_catalog(catalog_ref_uri)
            wms_get_capabilities_uri = "{}{}".format(wms_uri,
                                        cls.WMS_GET_CAPABILITIES_QUERY_ARGS)

            (wms_get_capabilities_resp_ok,
             layer_names) = cls.check_wms_get_capabilities_resp(
                                                    wms_get_capabilities_uri)
            if wms_get_capabilities_resp_ok:
                n_wms_get_capabilities_ok += 1

            n_wms_get_capabilities_uris_tested += 1

            if len(layer_names) > 0:
                n_wms_get_map_uris_tested += 1
                wms_get_map_uri = "{}{}".format(wms_uri,
                            cls.WMS_GET_MAP_QUERY_ARGS.format(layer_names[0]))

                wms_get_map_resp_ok = cls.check_wms_get_map_resp(
                                                            wms_get_map_uri)

                if wms_get_map_resp_ok:
                    n_wms_get_map_ok += 1

                n_wms_get_map_uris_tested += 1

            wcs_uri = cls.get_wcs_uri_from_catalog(catalog_ref_uri)
            wcs_get_capabilities_uri = "{}{}".format(wcs_uri,
                                        cls.WCS_GET_CAPABILITIES_QUERY_ARGS)

            (wcs_get_capabilities_resp_ok,
             layer_names) = cls.check_wcs_get_capabilities_resp(
                                                    wcs_get_capabilities_uri)
            if wcs_get_capabilities_resp_ok:
                n_wcs_get_capabilities_ok += 1

            n_wcs_get_capabilities_uris_tested += 1

            wcs_describe_coverage_uri = "{}{}".format(wcs_uri,
                                        cls.WCS_DESCRIBE_COVERAGE_QUERY_ARGS)

            (wcs_describe_coverage_resp_ok,
             layer_names) = cls.check_wcs_describe_coverage_resp(
                                         wcs_describe_coverage_uri)
            if wcs_describe_coverage_resp_ok:
                n_wcs_describe_coverage_ok += 1

            n_wcs_describe_coverage_uris_tested += 1

        # Log stats
        log.info('{} WMS endpoints tested'.format(
            n_wms_get_capabilities_uris_tested))
        log.info('{} WMS GetCapabilities calls succeeded'.format(
                            n_wms_get_capabilities_ok))
        log.info('{} WMS GetCapabilities calls failed'.format(
            n_wms_get_capabilities_uris_tested - n_wms_get_capabilities_ok))
        log.info('{} WMS GetMap endpoints tested'.format(
            n_wms_get_map_uris_tested))
        log.info('{} WMS GetMap calls succeeded'.format(n_wms_get_map_ok))
        log.info('{} WMS GetMap calls failed'.format(
                            n_wms_get_map_uris_tested - n_wms_get_map_ok))

        log.info('{} WCS GetCapabilities endpoints tested'.format(
            n_wcs_get_capabilities_uris_tested))
        log.info('{} WCS GetCapabilities calls succeeded'.format(
            n_wcs_get_capabilities_ok))
        log.info('{} WCS GetCapabilities calls failed'.format(
            n_wcs_get_capabilities_uris_tested - n_wcs_get_capabilities_ok))

        log.info('{} WCS DescribeCoverage endpoints tested'.format(
                 n_wcs_describe_coverage_uris_tested))
        log.info('{} WCS DescribeCoverage calls succeeded'.format(
                            n_wcs_describe_coverage_ok))
        log.info('{} WCS DescribeCoverage calls failed'.format(
            n_wcs_describe_coverage_uris_tested - n_wcs_describe_coverage_ok))

    @classmethod
    def get_wms_uri_from_catalog(cls, catalog_uri):
        '''Get catalogue from given URI and extract the first WMS endpoint
        '''
        base_prefix = get_base_uri(catalog_uri)

        catalog_ref_resp = requests.get(catalog_uri)
        catalog_elem = ET.fromstring(catalog_ref_resp.text)

        wms_service_elem = catalog_elem.findall(
            "{http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/"
            "v1.0}service[@serviceType='WMS']")

        wms_base_path = wms_service_elem[0].attrib['base']
        wms_base_uri = base_prefix + wms_base_path

        # Find WMS endpoint in catalogue
        wms_uri_elems = catalog_elem.findall(
            "{http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/"
            "v1.0}dataset/{http://www.unidata.ucar.edu/namespaces/thredds/"
            "InvCatalog/v1.0}dataset/{http://www.unidata.ucar.edu/"
            "namespaces/thredds/InvCatalog/v1.0}access[@serviceName='wms']")

        wms_uri_path = wms_uri_elems[0].attrib['urlPath']
        wms_uri = wms_base_uri + wms_uri_path

        return wms_uri

    @classmethod
    def check_wms_get_capabilities_resp(cls, wms_get_capabilities_uri):
        '''Perform sanity checks on GetCapabilities response from WMS
        endpoint
        '''
        get_capabilities_resp = requests.get(wms_get_capabilities_uri)

        if get_capabilities_resp.ok:
            log.info('WMS GetCapabilities OK for: {}'.format(
                                                wms_get_capabilities_uri))
        else:
            get_capabilities_stripped_resp = get_capabilities_resp.text.replace(
                                                                    '\r\n', '')
            log.error('WMS GetCapabilities failed for: {}: status code={}, '
                      'message={}'.format(wms_get_capabilities_uri,
                      get_capabilities_resp.status_code,
                      get_capabilities_stripped_resp))

            return get_capabilities_resp.ok, []

        try:
            get_capabilities_elem = ET.fromstring(get_capabilities_resp.text)

        except ET.ParseError:
            log.exception("WMS GetCapabilities call failed for {}".format(
                          wms_get_capabilities_uri))
            return get_capabilities_resp.ok, []

        # Check for layer names
        layer_name_elems = get_capabilities_elem.findall(
                                    '{http://www.opengis.net/wms}Capability/'
                                    '{http://www.opengis.net/wms}Layer/'
                                    '{http://www.opengis.net/wms}Layer/'
                                    '{http://www.opengis.net/wms}Layer/'
                                    '{http://www.opengis.net/wms}Name')
        if len(layer_name_elems) == 0:
            log.error('WMS GetCapabilities yielded no layer names for '
                      '{}'.format(wms_get_capabilities_uri))
            return get_capabilities_resp.ok, []
        else:
            layer_names = [layer_name_elem.text
                           for layer_name_elem in layer_name_elems]
            return get_capabilities_resp.ok, layer_names

    @classmethod
    def check_wms_get_map_resp(cls, wms_get_map_uri):
        '''Perform sanity checks on GetMap response from WMS
        endpoint
        '''
        get_map_resp = requests.get(wms_get_map_uri)
        if get_map_resp.ok:
            log.info('WMS GetMap OK for: {}'.format(wms_get_map_uri))
        else:
            get_map_stripped_resp = get_map_resp.text.replace('\r\n', '')
            log.error('WMS GetMap failed for: {}: status code={}, '
                      'message={}'.format(wms_get_map_uri,
                                          get_map_resp.status_code,
                                          get_map_stripped_resp))

        return get_map_resp.ok

    @classmethod
    def get_wcs_uri_from_catalog(cls, catalog_uri):
        '''Get catalogue from given URI and extract the first WCS endpoint
        '''
        base_prefix = get_base_uri(catalog_uri)

        catalog_ref_resp = requests.get(catalog_uri)
        catalog_elem = ET.fromstring(catalog_ref_resp.text)

        wcs_service_elem = catalog_elem.findall(
            "{http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/"
            "v1.0}service[@serviceType='WCS']")

        wcs_base_path = wcs_service_elem[0].attrib['base']
        wcs_base_uri = "{}{}".format(base_prefix, wcs_base_path)

        # Find WCS endpoint in catalogue
        wcs_uri_elems = catalog_elem.findall(
            "{http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/"
            "v1.0}dataset/{http://www.unidata.ucar.edu/namespaces/thredds/"
            "InvCatalog/v1.0}dataset/{http://www.unidata.ucar.edu/"
            "namespaces/thredds/InvCatalog/v1.0}access[@serviceName='wcs']")

        wcs_uri_path = wcs_uri_elems[0].attrib['urlPath']
        wcs_uri = "{}{}".format(wcs_base_uri, wcs_uri_path)

        return wcs_uri

    @classmethod
    def check_wcs_get_capabilities_resp(cls, wcs_get_capabilities_uri):
        '''Perform sanity checks on GetCapabilities response from WCS
        endpoint
        '''
        get_capabilities_resp = requests.get(wcs_get_capabilities_uri)

        if get_capabilities_resp.ok:
            log.info('WCS GetCapabilities OK for: {}'.format(
                                                wcs_get_capabilities_uri))
        else:
            get_capabilities_stripped_resp = get_capabilities_resp.text.replace(
                                                                    '\r\n', '')
            log.error('WCS GetCapabilities failed for: {}: status code={}, '
                      'message={}'.format(wcs_get_capabilities_uri,
                      get_capabilities_resp.status_code,
                      get_capabilities_stripped_resp))

            return get_capabilities_resp.ok, []

        try:
            get_capabilities_elem = ET.fromstring(get_capabilities_resp.text)

        except ET.ParseError:
            log.exception("WCS GetCapabilities call failed for {}".format(
                          wcs_get_capabilities_uri))
            return get_capabilities_resp.ok, []

        return get_capabilities_resp.ok, []

    @classmethod
    def check_wcs_describe_coverage_resp(cls, wcs_describe_coverage_uri):
        '''Perform sanity checks on DescribeCoverage response from WCS
        endpoint
        '''
        wcs_describe_coverage_resp = requests.get(wcs_describe_coverage_uri)

        if wcs_describe_coverage_resp.ok:
            log.info('WCS DescribeCoverage OK for: {}'.format(
                                                wcs_describe_coverage_uri))
        else:
            wcs_describe_coverage_stripped_resp = \
                wcs_describe_coverage_resp.text.replace('\r\n', '')
            log.error('WCS GetCapabilities failed for: {}: status code={}, '
                      'message={}'.format(wcs_describe_coverage_uri,
                      wcs_describe_coverage_resp.status_code,
                      wcs_describe_coverage_stripped_resp))

            return wcs_describe_coverage_resp.ok, []

        try:
            wcs_describe_coverage_elem = ET.fromstring(
                                              wcs_describe_coverage_resp.text)

        except ET.ParseError:
            log.exception("WCS DescribeCoverage call failed for {}".format(
                          wcs_describe_coverage_uri))
            return wcs_describe_coverage_resp.ok, []

        return wcs_describe_coverage_resp.ok, []
