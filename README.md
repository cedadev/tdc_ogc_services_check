THREDDS Data Server OGC Services check
======================================
Utility to test OGC endpoints from a target THREDDS Data server catalogue 
developed to support work for the ESA CCI Open Data Portal

# Releases
 * 0.4.0
   * Rework to allow non-existent catalogue entries and entries with no WMS or
     WCS entries at all
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
  
# Prerequisites
This has been developed and tested for Python 3.5.

# Installation
Installation can be performed using pip:

```
pip install git+https://github.com/cedadev/ceda-unittest-nagios-wrapper git+https://github.com/cedadev/slack-logging-handler git+https://github.com/cedadev/tds_ogc_services_check
```
Nb. ordering for picking up other dependent packages from CEDA Github.

# Running
There are three different scripts that can be run.

## Scan TDS Catalogue and find and test WMS and WCS services
This script crawls the whole catalogue and carries out basic tests on all the 
WMS and WCS endpoints it finds.  It reports using `logging` and outputs a
summary of successes and failures at the end.
```
ceda_tds_ogc_scan <URI to TDS catalogue path to scan> (<list of catalogue entries to test>|<test n random sample of entries from the catalogue>)
```

Test all entries in a catalogue:
```
ceda_tds_ogc_scan http://my-thredds-data-server/catalog.xml
```

Test 5 entries at random:
```
ceda_tds_ogc_scan http://my-thredds-data-server/catalog.xml 5
```

Run tests on specific catalogue references
```
ceda_tds_ogc_scan http://my-thredds-data-server/catalog.xml http://my-thredds-data-server/catalogRef1.xml http://my-thredds-data-server/catalogRef2.xml
```

## Nagios + Slack scripts
There are two scripts written for running in Nagios.  They give an output
message and the appropriate Nagios exit code depending on the outcome of the
test.  These also have capability for writing to a Slack channel given the 
correct Slack API hooks.

Set the environment variable `CEDA_TDS_OGC_SCAN_CATALOG_URI` to configure the
THREDDS catalogue to be queried.

Test WMS endpoints:
```
cci_odp_wms_test
```

Test WCS endpoints:
```
cci_odp_wcs_test
```


