# Reading SST Level 4 data via Kerchunk

Install library and env:

```
git clone https://github.com/cedadev/kerchunk-tools
cd kerchunk-tools/

# Create 
conda create --name kerchunk-tools --file spec-file.txt
conda activate kerchunk-tools

pip install -e . --no-deps
```

Read with `kerchunk-tools`:

```
import kerchunk_tools.xarray_wrapper as wrap_xr

index_uri = "https://gws-access.jasmin.ac.uk/public/cmip6_prep/eodh-eocis/esacci-sst-l4.json.zst"
ds = wrap_xr.wrap_xr_open(index_uri, compression="infer", scheme="http")

mx = ds.analysed_sst.isel(time=slice(0,3), lat=slice(100, 300), lon=slice(100,300)).max()
print(float(mx))
```

Or read with `xarray` only:

```
import xarray as xr
import fsspec

index_uri = "https://gws-access.jasmin.ac.uk/public/cmip6_prep/eodh-eocis/esacci-sst-l4.json.zst"
mapper = fsspec.get_mapper("reference://", fo=index_uri, target_options={"compression": "zstd"})
ds = xr.open_zarr(mapper, consolidated=False)

mx = ds.analysed_sst.isel(time=slice(0,3), lat=slice(100, 300), lon=slice(100,300)).max()
print(float(mx))
```

