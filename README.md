# ImmoProject

Copyright © 2020 by Rata Jacquemart and Thomas Besnard. All rights reserved



Applications for agency fee comparison four real estate sellers



## Installation

To run things locally, create and activate the conda environment
`conda env create -f environment.yml`
`conda activate immoproject`

Then install the pre-commit hooks to ensure proper code formatting
`pre-commit install`

To leverage docker-compose, you have to pass in your SSH key in order to fetch private repositories:

`docker-compose build --build-arg SSH_KEY="$(cat ~/.ssh/id_rsa)"`
`docker-compose up`



## Entry points

The tool has several entry points through CLI depending on the flow one wants to run. All are structured around a `Routine` object and accept the same arguments. The generic command is the following:

```
python -m <module> 
	--cwd <cwd> 
	[--routine/-r <routine>] 
	[--params <params>] 
	[--logging_level <logging_level>] 
	[--timestamp <timestamp>] 
	[--cache_to_prod] 
	[--cache_from_prod] 
	[--local_cache_root <local_cache_root>]
```

where:

- `<module>` corresponds to the module one wants to run a routine from (cf. section below for more details). It must be one of:
  - `data` to refresh ETLs and save the pre-processed data to cache
  - `prediction` to access all routines linked to the predictor
  - `flow` to access routines linked to scenario generation and evaluation
  - `optim` to run the optimizer
- `<cwd>` is the folder in which one wants to write the outputs
- `<routine>` is the name of the routine to run. Each module may have several routines. A default routine is always specified for each module *(optional)*
- `<params>` is a list of parameters that will overwrite the default parameters set in the YAML files. Nesting is represented by `.`, name and values should be separated by `:` and entries should be separated by white spaces ` `. For instance: `--params predictor.xgb.pred_col:pred_xbg` *(optional)*
- `<logging level>` will set the logging level (default is `INFO`). Must be one of `DEBUG`, `INFO`, `ERROR`, etc. *(optional)*
- `<timestamp>` will set the timestamp for the run. By default, timestamp is set to current time *(optional)*
- `--cache_to_prod` indicates that one wants to update the production cache *(optional)*
- `--cache_from_prod` indicates that one wants to only read from production cache (i.e. ignore local cache, cf. section on caching system below) *(optional)*
- `<local_cache_root>` is the path where one wants local cache to be written relative to `$HOME` folder (default is `pep_cache`) *(optional)*

For each run, the `Routine` object will create an output folder in the working directory named according to the run timestamp, and configuration and logging will be automatically saved there.



### ETL

To update the ETLs and cache the results, run:

```
python -m data ...
```
