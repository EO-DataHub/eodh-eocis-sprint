# Instructions for Kerchunk and STAC records for UK Climate Projections (UKCP)

## General rules

- 1 Kerchunk record == 1 STAC Item

## 12km regional climate model simulations

For the 12km data, there are (12 * 15 =) 180 STAC Items/Kerchunk files.

Here are the relevant facets:
- sub_collection: land-rcm
- domain: uk
- frequency: day
- resolution: 12km
- scenario: rcp85
- version: v20190731
- ensemble_member(s) \[x12]: 01, 04, 05, 06, 07, 08, 09, 10, 11, 12, 13, 15
- variable_id(s) \[x15]: clt, hurs, huss, pr, prsn, psl, rls, rss, sfcWind, snw, tas, tasmax, tasmin, uas, vas

The files to scan for these are:

`/badc/ukcp18/data/land-rcm/uk/12km/rcp85/{ensemble_member}/{variable_id}/{frequency}/{version}/*.nc`

E.g.:

`/badc/ukcp18/data/land-rcm/uk/12km/rcp85/01/tasmax/day/v20190731/*.nc`

Dataset ID scheme:
- example: `ukcp.land-rcm.uk.12km.rcp85.01.tasmax.day.v20190731`
- `ukcp.{sub_collection}.{domain}.{resolution}.{scenario}.{ensemble_member}.{variable_id}.{frequency}.{version}`

## 5km "local" climate model simulations

For the 5km data, there are 2 STAC Items/Kerchunk files. Each represents a different 20-year period:

- 1980-2000
- 2020-2040
- 2060-2080

Here are the relevant facets:
- sub_collection: land-cpm
- domain: uk
- frequency: day
- resolution: 5km
- scenario: rcp85
- version: v20210615
- ensemble_member(s): 01
- variable_id(s): tas
- time_period(s) \[x 3]:  1980-2000, 2020-2040, 2060-2080

The files to scan for these are:

`/badc/ukcp18/data/land-cpm/uk/5km/rcp85/{ensemble_member}/{variable_id}/{frequency}/{version}/*_{time_specifier}.nc`
- see time specifier below

E.g. for 2020-2040:

`/badc/ukcp18/data/land-cpm/uk/5km/rcp85/01/tas/day/v20210615/*_20[23]0*.nc`

Dataset ID scheme (DIFFERENT TO the 12km data):
- example: `ukcp.land-cpm.uk.5km.rcp85.01.tasmax.day.2060-2080.v20190731`
- `ukcp.{sub_collection}.{domain}.{resolution}.{scenario}.{ensemble_member}.{variable_id}.{frequency}.{time_period}.{version}`

## Notes

- I have renamed the global attribute "collection" to "sub_collection" for UKCP:
  - to avoid getting mixed up with the STAC collection

