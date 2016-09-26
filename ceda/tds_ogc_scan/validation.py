"""OGC services validation for TDS catalogue content
"""
__author__ = "P J Kershaw"
__date__ = "23/09/16"
__copyright__ = "(C) 2016 Science and Technology Facilities Council"
__license__ = """BSD - See LICENSE file in top-level directory"""
__contact__ = "Philip.Kershaw@stfc.ac.uk"
__revision__ = '$Id$'
import os
from urllib.parse import urlparse, urlunparse
import xml.etree.ElementTree as ET
import csv

import requests
import logging

log = logging.getLogger(__name__)


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
    
    @classmethod
    def create_report(cls, uri, report_filepath=None):
    
        if report_filepath is None:
            report_filepath = cls.REPORT_FILEPATH
    
        with open(report_filepath, 'w', newline=os.linesep) as report_file:
            report_writer = csv.writer(report_file, quoting=csv.QUOTE_MINIMAL,
                                       delimiter='$')
    
            cls.check(uri, report_writer=report_writer)
    
        report_file.close()
    
    @classmethod
    def check(cls, uri, report_writer=None):
    
        parsed_uri = urlparse(uri)
        thredds_prefix = urlunparse(
                        [parsed_uri.scheme, parsed_uri.netloc, 
                        os.path.dirname(parsed_uri.path), '', '', ''])
        base_prefix = urlunparse(
                        [parsed_uri.scheme, parsed_uri.netloc, '', '', '', ''])
    
        req = requests.get(uri)
        root = ET.fromstring(req.text)
    
        catalog_ref_elems = root.findall('{http://www.unidata.ucar.edu/'
                                         'namespaces/thredds/InvCatalog/v1.0}'
                                         'catalogRef')
    
        n_wms_uris_tested = 0
    
        for catalog_ref_elem in catalog_ref_elems:
            catalog_ref_uri_path = catalog_ref_elem.attrib[
                                        '{http://www.w3.org/1999/xlink}href']
            catalog_ref_uri = "{}/{}".format(thredds_prefix, 
                                             catalog_ref_uri_path)
    
            wms_uri = cls.get_wms_uri_from_catalog(base_prefix, catalog_ref_uri)
            wms_get_capabilities_uri = "{}{}".format(wms_uri, 
                                        cls.WMS_GET_CAPABILITIES_QUERY_ARGS)
    
            layer_names = cls.check_wms_get_capabilities_resp(
                                                    wms_get_capabilities_uri)

            if len(layer_names) > 0:
                wms_get_map_uri = "{}{}".format(wms_uri, 
                            cls.WMS_GET_MAP_QUERY_ARGS.format(layer_names[0]))

                cls.check_wms_get_map_resp(wms_get_map_uri)
                
#             if report_writer is not None:
#                 report_writer.writerow([wms_get_capabilities_uri, 
#                                         get_capabilities_resp.status_code,
#                                         get_capabilities_stripped_resp])
    
            n_wms_uris_tested += 1

    
        log.info('{} WMS endpoints tested'.format(n_wms_uris_tested))

    @classmethod
    def get_wms_uri_from_catalog(cls, base_prefix, catalog_uri):
        '''Get catalogue from given URI and extract the first WMS endpoint
        '''
        catalog_ref_resp = requests.get(catalog_uri)
        catalog_elem = ET.fromstring(catalog_ref_resp.text)
        
        wms_service_elem = catalog_elem.findall(
            "{http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/"
            "v1.0}service[@serviceType='WMS']")
        
        wms_base_path = wms_service_elem[0].attrib['base']
        wms_base_uri = "{}{}".format(base_prefix, wms_base_path)

        # Find WMS endpoint in catalogue
        wms_uri_elems = catalog_elem.findall(
            "{http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/"
            "v1.0}dataset/{http://www.unidata.ucar.edu/namespaces/thredds/"
            "InvCatalog/v1.0}dataset/{http://www.unidata.ucar.edu/"
            "namespaces/thredds/InvCatalog/v1.0}access[@serviceName='wms']")

        wms_uri_path = wms_uri_elems[0].attrib['urlPath']
        wms_uri = "{}{}".format(wms_base_uri, wms_uri_path)
        
        return wms_uri
        
    @classmethod
    def check_wms_get_capabilities_resp(cls, wms_get_capabilities_uri):
        '''Perform sanity checks on GetCapabilities response from WMS
        endpoint
        '''
        get_capabilities_resp = requests.get(wms_get_capabilities_uri)
        
        if get_capabilities_resp.ok:
            log.info('GetCapabilities OK for: {}'.format(
                                                wms_get_capabilities_uri))
        else:
            get_capabilities_stripped_resp = get_capabilities_resp.text.replace(
                                                                    '\r\n', '')
            log.error('GetCapabilities failed for: {}: status code={}, '
                      'message={}'.format(wms_get_capabilities_uri,
                      get_capabilities_resp.status_code, 
                      get_capabilities_stripped_resp))
                
        try:
            get_capabilities_elem = ET.fromstring(get_capabilities_resp.text)

        except ET.ParseError:
            log.exception("GetCapabilities call failed for {}".format(
                          wms_get_capabilities_uri))
            return []
        
        # Check for layer names
        layer_name_elems = get_capabilities_elem.findall(
                                    '{http://www.opengis.net/wms}Capability/'
                                    '{http://www.opengis.net/wms}Layer/'
                                    '{http://www.opengis.net/wms}Layer/'
                                    '{http://www.opengis.net/wms}Layer/'
                                    '{http://www.opengis.net/wms}Name')
        if len(layer_name_elems) == 0:
            log.error('GetCapabilities yielded no layer names for {}'.format(
                                                    wms_get_capabilities_uri))
            return []
        else:
            layer_names = [layer_name_elem.text 
                           for layer_name_elem in layer_name_elems]
            return layer_names
    
    @classmethod
    def check_wms_get_map_resp(cls, wms_get_map_uri):
        '''Perform sanity checks on GetMap response from WMS
        endpoint
        '''
        get_map_resp = requests.get(wms_get_map_uri)
        if get_map_resp.ok:
            log.info('GetMap OK for: {}'.format(wms_get_map_uri))
        else:
            get_map_stripped_resp = get_map_resp.text.replace('\r\n', '')
            log.error('GetMap failed for: {}: status code={}, '
                      'message={}'.format(wms_get_map_uri,
                                          get_map_resp.status_code, 
                                          get_map_stripped_resp))    
                  

