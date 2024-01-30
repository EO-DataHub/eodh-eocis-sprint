"""
Script to demonstrate pulling ITEM and ASSET content from files in the CEDA Archive:

FOR CMIP and CORDEX, SEE GOOGLE SHEET:

https://docs.google.com/spreadsheets/d/1eGB09gkLRM0OQw6trAKkVC0SaVE4EgJt-z_T1DM-X18/edit#gid=523321045

Dependencies:

- xarray
- cf_xarray

"""

import sys
import os
import glob
import hashlib
import json
import uuid

import xarray as xr

sys.path.append(".")

SERVICE_URL = "https://dap.ceda.ac.uk"
KERCHUNK_URL = "https://dap.ceda.ac.uk"
OUTPUTS_DIR = "./outputs"

def expand_timestring(t, end=False):
    tmpl = "00001231235959" if end else "00000101000000"
    return t + tmpl[len(t):]
   
        
def time_from_fname(fname):
    # TODO: Need a check to handle files with no time component
    t_comps = fname.split(".")[-2].split("_")[-1].split("-")
    time_comps = [expand_timestring(t_comps[0])]
    if len(t_comps) > 1:
        time_comps.append(expand_timestring(t_comps[1], end=True))
         
    time_comps = [f"{t[:4]}-{t[4:6]}-{t[6:8]}T{t[8:10]}:{t[10:12]}:{t[12:14]}" for t in time_comps]
    return "/".join(time_comps)
 

def get_asset_dict(fpath, bbox, level, config):
    d = {
        "href": f"{SERVICE_URL}{fpath}",
        "size": os.path.getsize(fpath),
        "area": bbox,
        "time": time_from_fname(fpath),
        "level": level
    }  

    d.update(config["defaults"]["asset"])
    return d


def floats(seq):
    return [float(x) for x in seq]

class NCFileInspector:
    def __init__(self, fpath, var_id, config):
        self.config = config
        self.ds = xr.open_dataset(fpath)
        self.var_id = var_id
        self.var = self.ds[var_id]

    def global_attr(self, key):
        return self.ds.attrs.get(key, None)

    def get_var_props(self):
        attrs = self.var.attrs
        vprops = {
            "variable_id": self.var_id,
            "variable_long_name": attrs.get("long_name", None),
            "variable_units": attrs.get("units", None), 
            "cf_standard_name": attrs.get("standard_name", None) 
        }
        return vprops

    def get_properties(self):
        props = {}
        for key in self.config["global_attrs"]:
            value = self.global_attr(key)
            key = self.config["global_attr_map"].get(key, key)

            if isinstance(value, str) and value.lower() in ("null", "none"):
                value = None

            props[key] = value

        props.update(self.config["defaults"]["item"])

        var_props = self.get_var_props()
        props.update(var_props)
        return props 

    def get_datetime(self, index):
        try:
            return self.ds.time.values[index].isoformat()
        except Exception as exc:
            try: 
                # For np.datetime64 objects
                return str(self.ds.time.values[index]).split(".")[0]
            except Exception as exc2:
                pass

        return None 
  
    def get_bbox(self):
        # use the geopspatial min/max metdata if present
        geospatial_lat_min = self.ds.attrs.get("geospatial_lat_min", None)
        geospatial_lat_max = self.ds.attrs.get("geospatial_lat_max", None)
        geospatial_lon_min = self.ds.attrs.get("geospatial_lon_min", None)
        geospatial_lon_max = self.ds.attrs.get("geospatial_lon_max", None)
        metadata_valid = True
        for v in [geospatial_lat_min, geospatial_lon_min, geospatial_lat_max, geospatial_lon_max]:
            if v is None:
                metadata_valid = False
        if metadata_valid:
            return floats([geospatial_lon_min, geospatial_lat_min, geospatial_lon_max, geospatial_lat_max])
        # otherwise, extract from the data
        lt = self.ds.cf["latitude"]
        ln = self.ds.cf["longitude"]
        return floats([ln.min(), lt.min(), ln.max(), lt.max()])
         
    def get_level(self):
        try:
            levels = self.ds.cf["Z"].values
            return floats([levels[0], levels[-1]])
        except Exception as exc:
            return None


def get_access_control(config):
    dsac = config["access_control"]

    return {   # because the same for all Assets in this Item
      "rule": dsac["rule"],
      "roles": dsac["roles"]
    }


def sha256(fpath):
    # fake hack to not fail if file doesn't exist
    content = open(fpath, "rb").read() if os.path.isfile(fpath) else fpath.encode("utf-8")
    return hashlib.sha256(content).hexdigest()

def get_kerchunk_asset(dset_id, dr, config):
    extra_dirs = "/".join(dset_id.split(".")[:config['kerchunk']['dir_depth']['by_dset']])
    kc_path = f"{config['metadata_dir']}/kerchunk/by_dset/{extra_dirs}/{dset_id}.zstd"
    kc_uri = f"{KERCHUNK_URL}{kc_path}"

    return {"reference_file":
       {"checksum": sha256(kc_path),
        "checksum_type": "SHA256",
        "href": kc_uri,
        "roles": ["reference"],
        "size": os.path.getsize(kc_path) if os.path.isfile(kc_path) else 248942,
        "type": "application/zstd",
        "open_zarr_kwargs": {"decode_times": True}
       }
    }
      
def get_geometry(bbox):
    lon_min = bbox[0]
    lat_min = bbox[1]
    lon_max = bbox[2]
    lat_max = bbox[3]
    return {
        "type": "Polygon",
        "coordinates": [
            [[lon_min, lat_min], [lon_max, lat_min], [lon_max, lat_max], [lon_min, lat_max], [lon_min, lat_min]]
        ]
    }


class Netcdf2Stac:

    def __init__(self, input_path, config_paths, output_path, item_id=None):
        self.input_path = input_path
        self.config_paths = config_paths
        self.output_path = output_path
        self.item_id = item_id


        def merge(d1, d2):
            # recursively merge configurations d1 and d2, give d2 priority
            if d2 is None:
                return d1
            if d1 is None:
                return d2
            if isinstance(d1,list) and isinstance(d2,list):
                return d1+d2
            if isinstance(d1,dict) and isinstance(d2,dict):
                all_keys = list(set(list(d1.keys())+list(d2.keys())))
                merged = {}
                for k in all_keys:
                    merged[k] = merge(d1.get(k,None),d2.get(k,None))
                return merged
            # fallback, ignore d1, return d2
            return d2

        self.config = {}
        for config_path in self.config_paths:
            with open(config_path) as f:
                self.config = merge(self.config,json.loads(f.read()))

    def run(self):

        if os.path.isdir(self.input_path):
            fpaths = []
            for root, folders, files in os.walk(self.input_path):
                for file in files:
                    if file.endswith(".nc"):
                        fpaths.append(os.path.join(root,file))
            fpaths = sorted(fpaths)
        else:
            fpaths = [self.input_path]

        var_id = self.config["variable"]
        dset_id = self.config["dataset_id"]

        # ff and fl are file:first and file:last
        ff, fl = [NCFileInspector(fpath, var_id, self.config) for fpath in [fpaths[0], fpaths[-1]]]

        # Get bbox and level first so that we can insert them into the assets
        bbox = ff.get_bbox()
        level = ff.get_level()

        # Build asset list - start with kerchunk asset
        assets = get_kerchunk_asset(dset_id, self.input_path, self.config)
        # Add normal file assets
        assets.update({os.path.basename(fpath): get_asset_dict(fpath, bbox, level, self.config) for fpath in fpaths})

        # work out the identifier for this STAC item
        item_id = self.item_id

        # if not passed explicitly...
        if self.item_id is None:
            if len(fpaths) == 1:
                # try to get id from the file
                if "file_id_attribute" in self.config:
                    item_id = ff.global_attr(self.config["file_id_attribute"])

        # fallback to creating a new id
        if item_id is None:
            # make up a new unique id
            item_id = str(uuid.uuid4())

        # define the top-level attributes of the item
        d = {
            "stac_version": "1.0.0",
            "stac_extensions": [],
            "type": "Feature",
            "properties": ff.get_properties(),
            "bbox": bbox,
            "geometry": get_geometry(bbox),
            "id": item_id
        }

        d["properties"].update(**{
            "start_datetime": ff.get_datetime(0),
            "end_datetime": fl.get_datetime(-1),
            "level": level,
            "file_count": len(assets),
            "total_size": sum([asset["size"] for asset in assets.values()]),
            "access_control": get_access_control(self.config),
            "assets": assets
        })

        # Add dataset ID
        d["properties"][self.config["dset_id_name"]] = dset_id

        # Add templated properties
        for prop, tmpl in self.config["templated_properties"].items():
            d["properties"][prop] = tmpl.format(**vars())

        with open(self.output_path,"w") as f:
            f.write(json.dumps(d))


def netcdf2stac():

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("input_path",help="path to netcdf4 file or folder")
    parser.add_argument("output_path", help="path to output stac file")

    parser.add_argument("--config-path", nargs="+", help="path to JSON configuration file(s)", required=True)
    parser.add_argument("--id", type=str, help="supply an id for the STAC item", required=False, default=None)

    args = parser.parse_args()
    converter = Netcdf2Stac(args.input_path, args.config_path, args.output_path, args.id)
    converter.run()

if __name__ == "__main__":
    netcdf2stac()


