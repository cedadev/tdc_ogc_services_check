#!/usr/bin/env python
"""Distribution Utilities setup program for CCI OGC TDS scanning Package
"""
__author__ = "P J Kershaw"
__date__ = "26/09/16"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = """BSD - See LICENSE file in top-level directory"""
__contact__ = "Philip.Kershaw@stfc.ac.uk"

# Bootstrap setuptools if necessary.
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages


setup(
    name =            	'tds_ogc_services_check',
    version =         	'0.4.0',
    description =     	'Check OGC endpoints from target TDS catalogue',
    long_description = 	'''Utility to test OGC endpoints from a target THREDDS
Data server catalogue
''',
    author =          	'Philip Kershaw',
    author_email =    	'Philip.Kershaw@stfc.ac.uk',
    maintainer =        'Philip Kershaw',
    maintainer_email =  'Philip.Kershaw@stfc.ac.uk',
    url =             	'https://github.com/cedadev/tds_ogc_services_check',
    platforms =         ['POSIX', 'Linux', 'Windows'],
    install_requires =  ['requests', 'six', 'ceda-unittest-nagios-wrapper',
                         'cedadev-slack-logging-handler'],
    license =           __license__,
    test_suite =        '',
    packages =          find_packages(),
    package_data={
        'ceda/tds_ogc_scan': [
            'LICENSE',
        ],
    },
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Security',
        'Topic :: Internet',
        'Topic :: Scientific/Engineering',
        'Topic :: System :: Distributed Computing',
        'Topic :: System :: Systems Administration :: Authentication/Directory',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    entry_points={
        'console_scripts': [
            'ceda_tds_ogc_scan = ceda.tds_ogc_scan.script:main',
            'cci_odp_wms_test = '
            'ceda.tds_ogc_scan.nagios_test.wms_test:main',
            'cci_odp_wcs_test = '
            'ceda.tds_ogc_scan.nagios_test.wcs_test:main',
            ],
        },
    zip_safe = False
)
