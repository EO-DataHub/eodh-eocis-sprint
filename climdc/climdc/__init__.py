import pandas as pd
import xarray as xr
from copy import deepcopy

datasets = {
"ukcp-land-rcm-12km-uk-mon":
{
  "path": "/badc/ukcp18/data/land-rcm/uk/12km/rcp85/01/{variable}/mon/latest/*.nc",
  "vars": ["tas", "pr"],
  "time": ["1980-01-01", "2080-12-30"],
  "x": [-210000, 762000], "y": [-102000, 1230000]
},
"ukcp-land-rcm-12km-uk-day":
{
  "path": "/badc/ukcp18/data/land-rcm/uk/12km/rcp85/01/tas/day/latest",
  "time": ["1980-01-01", "2080-12-30"],
  "x": [-210000, 762000], "y": [-102000, 1230000]
},
"CMIP6.CMIP.MOHC.UKESM1-0-LL.1pctCO2.r1i1p1f2.Amon.tas.gn.latest": 
{
  "path": "/badc/cmip6/data/CMIP6/CMIP/MOHC/UKESM1-0-LL/1pctCO2/r1i1p1f2/Amon/tas/gn/latest",
  "time": ["1850-01-01", "1999-01-01"],
  "x": [0.9375, 359.0625], "y": [-89.375, 89.375]
}
}


products = {

"ukcp": {
"datasets": [
"ukcp-land-rcm-12km-uk-mon",
"ukcp-land-rcm-12km-uk-day",
"ukcp-land-cpm-5km-uk-mon",
"ukcp-land-cpm-5km-uk-day"
],
"description": "UKCP datasets", 
"license": "OGL",
"default_crs": "OSGB",
"default_resolution": "12km"},

"cmip6": {
"datasets": [
"CMIP6.CMIP.MOHC.UKESM1-0-LL.1pctCO2.r1i1p1f2.Amon.tas.gn.latest"],
"description": "CMIP6 UKESM1-0-LL 1pctCO2",
"license": "open",
"default_crs": None,
"default_resolution": None} 
}


prods_no_dsets = deepcopy(products)
for key in prods_no_dsets.keys():
  del prods_no_dsets[key]["datasets"]


def list_products():
  products = pd.DataFrame(data=prods_no_dsets).T
  return products


def find_datasets(product, x=None, y=None, time=None):
  return products[product]["datasets"]


def load(dataset, measurements, time, x, y, output_crs=None, resolution=None):
  dataset = datasets[dataset]
  dsets = []

  for measurement in measurements:
    dsets.append(
      xr.open_mfdataset(dataset['path'].format(variable=measurement)).sel(time=slice(*time), projection_y_coordinate=slice(*y), projection_x_coordinate=slice(*x))
    )
  return xr.merge(dsets) 



  
       


