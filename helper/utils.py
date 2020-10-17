import ast
import collections
import logging
import keyword
import datetime
import pathlib
import shutil
import time
from typing import Tuple
import yaml
import itertools
import os
import cProfile
import pstats
import io

log = logging.getLogger(__name__)


class _Constant:
    pass


CONST = _Constant()
CONST.BASE_PATH = pathlib.Path(__file__).parents[2]
CONST.CONF_PATH = pathlib.Path(CONST.BASE_PATH,"immoproject", "config", "conf_yml")
CONST.DATETIME_FORMAT = "%Y-%m-%d"


def parse_params(params):
    custom_cfg = collections.defaultdict(dict)
    for key, value in params.items():
        try:
            try:
                if not keyword.iskeyword(str(value)):
                    value = ast.literal_eval(value)
            except:
                log.debug(
                    "'{}' cannot be intepreted as a litteral, will be used as string".format(
                        value
                    )
                )
            cats = key.split(".")[:-1]
            param = key.split(".")[-1]
            param = int(param) if param.isdigit() else param
            section = custom_cfg
            for cat in cats:
                if not section.get(cat):
                    section[cat] = {}
                section = section[cat]
            log.debug(
                "Setting {}.{} = {} ({})".format(
                    ".".join(cats), param, value, type(value)
                )
            )
            section[param] = value
        except Exception:
            log.exception(f"Failed to parse param: {key}:{value}")
            raise
    return custom_cfg


def get_timestamp():
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S")


def json_serial(obj):
    """
    JSON serializer for objects not serializable by default json code
    """
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


def get_versioned_log_path(
    cwd: pathlib.Path, scenario_name: str, timestamp: str
) -> Tuple[str, str]:
    log_dir_path = pathlib.Path(cwd, "log")
    pathlib.Path(log_dir_path).mkdir(parents=True, exist_ok=True)

    fname_base = "_".join([scenario_name, timestamp])
    log_path = pathlib.Path(log_dir_path, f"{fname_base}.log")
    old_path = ""
    if log_path.exists():
        old_path = f"{str(log_path)}.{str(time.time_ns())}"
        shutil.copy(log_path, old_path)
    return str(log_path), str(old_path)


def read_yaml_config(path):
    """
    Reads a yaml config file

    Parameters
    ----------
    path: str
        The full path to the config file

    Returns
    -------
    config: dict
        The config file parsed as a multi-level dictionary
    """
    if not pathlib.Path(path).exists():
        raise Exception(
            "Path '{}' to configuration file folder doesn't exist.".format(path)
        )

    with open(path, "r") as f:
        config = yaml.load(f)

    return config


def grid(**kwargs):
    """
    Takes a dict of param lists as input and creates their cartesian product as a list of param dicts

    Parameters
    ----------
    kwargs: Dict[List]
        Dict of lists with params and their possible values, eg. {"param1": [1, 2], "param2": ["abc", "def"]}

    Returns
    -------
    List[Dict]
        List of dicts containing all possible combinations of lists passed as inputs,
        eg. [{"param1": 1, "param2: "abc"}, {"param1": 1, "param2: "def"},
        {"param1": 2, "param2: "abc"}, {"param1": 2, "param2: "def"}]

    """
    keys = kwargs.keys()
    vals = kwargs.values()
    for instance in itertools.product(*vals):
        yield dict(zip(keys, instance))


def get_latest_in_directory(path, file_start=None, extension=None):
    """
    Returns the latest file from a datalake directory

    Parameters
    ----------
    path: str,
        The path to the directory

    file_start: str, optional, default=None
        start of file

    extension: str, optional, default=None
        Extension of file

    walk: bool, optional, default=True
        Flag to indicate if needed to search in inner directories

    Returns
    -------
    latest: str
        The file_name

    """
    latest = None
    items = list(os.listdir(path))
    filtered_items = items

    # Check if extension is right
    if extension is not None:
        filtered_items = [i for i in items if os.path.basename(i).endswith(extension)]

    # Check if filename starts with file start
    if file_start is not None:
        filtered_items = [
            i for i in filtered_items if os.path.basename(i).startswith(file_start)
        ]
    sorted_filtered_items = sorted(filtered_items)

    if sorted_filtered_items:
        latest = sorted_filtered_items[-1]

    return latest


def profileit(func):
    def wrapper(*args, **kwargs):
        datafn = func.__name__ + ".profile"  # Name the data file sensibly
        prof = cProfile.Profile()
        retval = prof.runcall(func, *args, **kwargs)
        s = io.StringIO()
        sortby = "cumulative"
        ps = pstats.Stats(prof, stream=s).sort_stats(sortby)
        ps.print_stats()
        with open(datafn, "w") as perf_file:
            perf_file.write(s.getvalue())
        return retval

    return wrapper
