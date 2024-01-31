# dataset-to-stac

A utility to convert the metadata in a netcdf4 data file to a STAC item JSON file, and add assets

## summary

Map netcdf4 files to STAC items, guided by one or more configuration files

## dependencies

Requires xarray and netcdf4 python libraries

Suggested environment:

```
conda create -n stac_env python=3.10
conda activate stac_env
conda install xarray cf_xarray netcdf4 pystac
```

## running

Download the dataset-to-stac.py script and any required configuration files from the config folder

```
python /home/dev/github/eodh-eocis-sprint/stac-sandbox/dataset-to-stac.py --help
usage: dataset-to-stac.py [-h] --config-path CONFIG_PATH [CONFIG_PATH ...] [--id ID] input_path output_path

positional arguments:
  input_path            path to netcdf4 file or folder
  output_path           path to output stac file

optional arguments:
  -h, --help            show this help message and exit
  --config-path CONFIG_PATH [CONFIG_PATH ...]
                        path to JSON configuration file(s)
  --id ID               supply an id for the STAC item

```

### example - convert EOCIS/ESACCI SST CDRv3 file, using two configuration files

```
python dataset-to-stac.py 20220101120000-C3S-L4_GHRSST-SSTdepth-OSTIA-GLOB_ICDR3.0-v02.0-fv01.0.nc 20220101120000-C3S-L4_GHRSST-SSTdepth-OSTIA-GLOB_ICDR3.0-v02.0-fv01.0.json --config-path configs/defaults.json configs/sst.json 
```

note that if multiple configuration files are supplied, they are merged, with later ones taking precedence over earlier ones

### configuration file format

Each configuration file is a JSON formatted dictionary, with the following keys (incomplete)

| key                 | purpose                                                                                                                                   |
|---------------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| file_id_attribute   | global attribute in each input file that provides a file-unique identifier string                                                         |
| global_attrs        | a list of global attributes to copy into the STAC item properties                                                                         |
| global_attr_map    | a dictionary mapping dataset global attribute names to STAC item property names                                                           |
| service_url         | root URL for serving files, to which the filenames are appended <br/> {year}, {month} and {day} are expanded using python's format method |
| kerchunk_url        | root URL for kerchunk                                                                                                                     |
| variable            | a reference variable that can be used to obtain the spatial and temporal extent                                                           |
| dataset_id          | the name of the dataset                                                                                                                   |
 | defaults=>item      | a dictionary containing metatdata to add to each STAC item properties                                                                     |
 | kerchunk           | dictionary describing kerchunk configuration (TBC)                                                                                        |



