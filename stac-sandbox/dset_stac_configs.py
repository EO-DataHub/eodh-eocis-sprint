configs = {

  "ukcp": {
    "base_dir": "/badc/ukcp18/data",
    "dset_id_name": "dataset_id",
    "var_id_index_in_dset_id": -3,
    "dset_id_prefix": "ukcp.",
    "defaults": {
      "item": {
        "latest": True
      },
      "asset": {
        "checksum": None,
        "checksum_type": None,
        "type": "application/netcdf",
        "roles": ["data"]
      },
    },
    "global_attrs": ['collection', 'domain', 'frequency', 'institution', 
                     'institution_id', 'project', 'references', 'resolution', 'scenario', 
                     'version', 'Conventions'],
    "global_attr_map": {},
    "templated_properties": {}
  },

  "cmip6": {
    "base_dir": "/badc/cmip6/data",
    "metadata_dir": "/badc/cmip6/metadata",
    "dset_id_name": "instance_id",
    "var_id_index_in_dset_id": -3,
    "kerchunk": {
      "dir_depth": {
        "by_dset": 6
      },
    },
    "defaults": {
      "item": {
        "access": ["HTTPServer"],
        "index_node": None,
        "latest": True,
        "pid": None,
        "replica": False,
        "retracted": False
      },
      "asset": {
        "checksum": None,
        "checksum_type": None,
        "type": "application/netcdf",
        "roles": ["data"]
      },
    },
    "global_attrs": ["activity_id", "data_specs_version", "experiment_id", "experiment", "frequency", "further_info_url",
                     "grid", "grid_label", "institution_id", "mip_era", "nominal_resolution", "source_id", "source_type",
                     "sub_experiment_id", "table_id", "variable_id", "variant_label"],
    "global_attr_map": {
      "experiment": "experiment_title"
    },
    "templated_properties": {
      "citation_url": "http://cera-www.dkrz.de/WDCC/meta/CMIP6/{dset_id}.json"
    }
  },

  "cordex": {
    "base_dir": "/badc/cordex/data",
    "dset_id_name": "instance_id",
    "var_id_index_in_dset_id": -2,
    "defaults": {
      "item": {
        "access": ["HTTPServer"],
        "index_node": None,
        "latest": True,
        "pid": None,
        "replica": False,
        "retracted": False
      },
      "asset": {
        "checksum": None,
        "checksum_type": None,
        "type": "application/netcdf",
        "roles": ["data"]
      },
    },
    "global_attrs": ['CORDEX_domain', 'driving_model_id', 'driving_model_ensemble_member', 'experiment_id', 'experiment_familys', 
                     'institute_id', 'product', 'project_id', 'rcm_version_id', 'frequency',
                     'driving_experiment_name', 'model_id'],
    "global_attr_map": {
      "CORDEX_domain": "domain",
      "driving_model_id": "driving_model",
      "frequency": "time_frequency",
      "rcm_version_id": "rcm_version",
      "experiment_id": "experiment",
      "project_id": "project",
      "institute_id": "institute",
      "driving_model_ensemble_member": "ensemble",
      "model_id": "rcm_name"
    },
    "templated_properties": {}
  }
}

