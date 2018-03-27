THREDDS Data Server OGC Services check
======================================
Utility to test OGC endpoints from a target THREDDS Data server catalogue 
developed to support work for the ESA CCI Open Data Portal

Releases
--------
 * 0.3.1
   * Fix wms_test nagios test script
 * 0.3.0
   * Added unit tests for WMS and WCS - takes a catalogue URI as input and
    creates tests for each endpoint found
 * 0.2.4
   * Fix for GetCapabilities check - don't try to parse response if gives 500
    error 
 * 0.2.3
   * added additional summary stats
 * 0.2.2
   * cleaned up, removed CSV output option, made pip installable
 * 0.1.0
   * initial release.  Checks WMS endpoints only, may be extended at a later 
   date to include WCS also.
  
Prerequisites
-------------
This has been developed and tested for Python 3.5.

Installation
------------
Installation can be performed using pip.
