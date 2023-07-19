#!/usr/bin/env python

import xarray as xr
import sys

var_id = sys.argv[1]
files = sys.argv[2:]

ds = xr.open_mfdataset(files, use_cftime=True, combine="by_coords", decode_timedelta=False)
v = ds[var_id]

t = v.time.values
print(f"""
        "temporal":{{"interval":[["{t[0].isoformat()}", "{t[-1].isoformat()}"]]}}
""")

lat = v.latitude.values
lon = v.longitude.values

print(f"[{lon.min()}, {lat.min()}, {lon.max()}, {lat.max()}]")

for attr in ds.attrs:
    print(f'        "{attr}": "{ds.attrs[attr]}",')


