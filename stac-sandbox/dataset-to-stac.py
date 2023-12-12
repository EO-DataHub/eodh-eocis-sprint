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

import xarray as xr
import cf_xarray as cfxr

sys.path.append(".")
from dset_stac_configs import configs
DEFAULTS = configs["DEFAULTS"]

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
 

def get_asset_dict(fpath, bbox, level, config=None):
    d = {
        "href": f"{SERVICE_URL}{fpath}",
        "size": os.path.getsize(fpath),
        "area": bbox,
        "time": time_from_fname(fpath),
        "level": level
    }  

    if config is None:
        config = config_from_path(fpath)
    d.update(config["defaults"]["asset"])
    return d


def floats(seq):
    return [float(x) for x in seq]

def proj_from_path(fpath, return_config=False):
    for proj, content in configs.items():
        if proj == "DEFAULTS": continue
        if fpath.startswith(content["base_dir"]): 
            if return_config:
                return configs[proj]
            return proj

    raise KeyError(f"No project matched for: {fpath}") 

def config_from_path(fpath):
    return proj_from_path(fpath, return_config=True)


class NCFileInspector:
    def __init__(self, fpath, var_id, config=None):
        self.config = config if config else config_from_path(fpath)
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
        lt = self.ds.cf["latitude"]
        ln = self.ds.cf["longitude"]
        return floats([ln.min(), lt.min(), ln.max(), lt.max()])
         
    def get_level(self):
        try:
            levels = self.ds.cf["Z"].values
            return floats([levels[0], levels[-1]])
        except Exception as exc:
            return None


def dir_to_dset_id(dr):
    config = config_from_path(dr)
    return config.get("dset_id_prefix", "") + \
           dr.replace(config["base_dir"], "").strip("/").replace("/", ".") + \
           config.get("dset_id_suffix", "")

def get_a_or_b(key, a, b):
    "Get item from `key` in dict `a`, or `b`."
    return a.get(key, b[key])


def get_access_control(config):
    ac = "access_control"
    dfac = DEFAULTS[ac]
    dsac = config.get(ac, dfac)

    return {   # because the same for all Assets in this Item
      "rule": get_a_or_b("rule", dsac, dfac),
      "roles": get_a_or_b("roles", dsac, dfac)
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
      

def get_item_dict(spec):
    if os.path.isdir(spec):
        dr = spec
        fnames = sorted(os.listdir(dr))
        fpaths = [os.path.join(dr, fname) for fname in fnames]
    else:
        fpaths = sorted(glob.glob(spec))
        fnames = [os.path.basename(fpath) for fpath in fpaths]
        dr = os.path.commonprefix(fpaths).rstrip("/")
        while not os.path.isdir(dr): dr = os.path.dirname(dr)
 
    config = config_from_path(dr)
#    var_id = "analysed_sst" # var_from_dir(dr, config)
    var_id = var_from_dir(dr, config)
    dset_id = dir_to_dset_id(dr)

    # ff and fl are file:first and file:last
    ff, fl = [NCFileInspector(fpath, var_id) for fpath in [fpaths[0], fpaths[-1]]]

    # Get bbox and level first so that we can insert them into the assets
    bbox = ff.get_bbox()
    level = ff.get_level()

    # Build asset list - start with kerchunk asset
    assets = get_kerchunk_asset(dset_id, dr, config)
    # Add normal file assets
    assets.update( {os.path.basename(fpath): get_asset_dict(fpath, bbox, level) for fpath in fpaths} )

    start = ff.get_datetime(0)
    end = fl.get_datetime(-1)

    d = {
        "properties": ff.get_properties(),
        "bbox": bbox,
        "start_datetime": start,
        "end_datetime": end,
        "level": level,
        "file_count": len(assets), 
        "total_size": sum([asset["size"] for asset in assets.values()]),
        "version": version_from_dir(dr),
        "access_control": get_access_control(config),
        "assets": assets
    }

    # Add dataset ID
    d["properties"][config["dset_id_name"]] = dset_id

    # Add templated properties
    for prop, tmpl in config["templated_properties"].items():
        d["properties"][prop] = tmpl.format(**vars())

    return dset_id, d

def var_from_dir(dr, config):
    return dr.strip("/").split("/")[config["var_id_index_in_dset_id"]]


def version_from_dir(dr):
    return dr.strip("/").split("/")[-1]


def main(spec):
    dset_id, item = get_item_dict(spec)
    dset_item_file = f"{OUTPUTS_DIR}/{dset_id}.json"
    
    with open(dset_item_file, "w") as writer:
        json.dump(item, writer, indent=4, sort_keys=False)

    print(f"Wrote STAC Item file to: {dset_item_file}")
    return item 

class Netcdf2Stac:

    def __init__(self, input_path, config_path, output_path):
        self.input_path = input_path
        self.config_path = config_path
        self.output_path = output_path

        with open(self.config_path) as f:
            self.config = json.loads(f.read())

    def run(self):

        if os.path.isdir(self.input_path):
            fnames = sorted(os.listdir(self.input_path))
            fpaths = [os.path.join(self, fname) for fname in fnames]
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

        d = {
            "properties": ff.get_properties(),
            "bbox": bbox,
            "start_datetime": ff.get_datetime(0),
            "end_datetime": fl.get_datetime(-1),
            "level": level,
            "file_count": len(assets),
            "total_size": sum([asset["size"] for asset in assets.values()]),
            "version": version_from_dir(self.input_path),
            "access_control": get_access_control(self.config),
            "assets": assets
        }

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
    parser.add_argument("config_path", help="path to JSON configuration file")
    parser.add_argument("output_path", help="path to output stac file")

    args = parser.parse_args()
    converter = Netcdf2Stac(args.input_path, args.config_path, args.output_path)
    converter.run()

if __name__ == "__main__":


    if len(sys.argv) > 1:
        # if arguments provided, call netcdf2stac to consume them
        netcdf2stac()
    else:

        import pprint, time
        spec1 = "/home/dev/data/regrid/analysed_sst/2022/01/01/"
        spec1 = "/badc/ukcp18/data/land-rcm/uk/12km/rcp85/01/tasmax/day/v20190731/tasmax_rcp85_land-rcm_uk_12km_01_day_*.nc"

        for spec in (spec1,):
            print(f"[INFO] Running with spec: {spec}")
            resp = main(spec)
            pprint.pprint(resp)

            print("Pausing for...: ", end="")
            for sleep in range(10, -1, -1):
                print(f"{sleep}", end=" ")
                sys.stdout.flush()
                time.sleep(1)

            print()

