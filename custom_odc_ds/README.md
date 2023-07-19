# Custom Datasources for ODC

This code creates custom datareader/writer for a new format `NetCDFX`

This is based on copies of datacube code with a fix required to 
add EPSG:4326 as the CRS on the fly to SST netcdf files.  

To use this driver, set the format of a ODC dataset to `NetCDFX` instead of `NetCDF`

## Installation instructions

These drivers register themselves with opendatacube via python entrypoints - see setup.cfg.

To install run the following inside the datacube conda environment

```
pip install .
```