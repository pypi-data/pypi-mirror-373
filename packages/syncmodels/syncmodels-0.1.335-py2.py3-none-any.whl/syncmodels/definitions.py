import re
import time
from typing import NewType

# from .models import (
#     BudgetTypeEnum,
#     TravelPartyCompositionEnum,
# )

DEFAULT_LANGUAGE = "es"

MODEL_TABLE = "model"

UID_TYPE = str

# TODO: reallocate
UID = NewType("UID", str)
QUERY = NewType("QUERY", dict)

URI = NewType("URI", str)
DURI = NewType("DURI", dict)
TAG = NewType("TAG", str)
EDGE = NewType("EDGE", dict)

WAVE = NewType("WAVE", int)
JSON = NewType("JSON", dict)

REGEXP = NewType("REGEXP", str)


# ----------------------------------------------------------
# geo location
# ----------------------------------------------------------
GEO_NS = "geo"
GEO_BOUNDARIES_DB = "boundaries"
GEO_GRID_THING = "grid"
GEO_REGION_THING = "region"
GEO_CONFIG_THING = "config"
GEO_DEFAULT_GRID = "default_grid"
GEO_DEFAULT_REGION = "default_region"
GEO_THING = "geo"

# ----------------------------------------------------------
# common keys
# ----------------------------------------------------------
# crawler factory keys
APP_URL = "app_url"

# bootstrap keys
ENUM_KEY = "enum__"
KIND_KEY = "kind__"
MODEL_KEY = "model__"
TASK_KEY = "task__"
WAVE_INFO_KEY = "wave_info__"
STREAM_KEY = "stream__"
METHOD_KEY = "method__"
PREFIX_URL = "prefix_uri__"
PREFIX_KEY = "prefix__"
PARAMS_KEY = "params__"
ACTIVITY_LOG_KEY = "activity_log__"


# other call_kw | data keys

GRACE_PERIOD_KEY = "grace__"
# DEFAULT_GRACE_PERIOD = sys.float_info.max
# DEFAULT_GRACE_PERIOD = 24 * 3600 * 7 * 2  # 2 weeks (seconds)
DEFAULT_GRACE_PERIOD = 24 * 3600 * 1 * 1  # 1 day (seconds)
ORDER_KEY = "order__"
LIMIT_KEY = "limit__"
LIMIT_KEY_VALUE = "limit_value__"
DIRECTION_KEY = "direction__"
DIRECTION_ASC = "ASC"
DIRECTION_DESC = "DESC"
MAX_ROWS = "max_rows__"
BODY_FORMAT = "body_format__"

WHERE_KEY = "where__"
TABLE_KEY = "table__"
TOPIC_LIST_KEY = "topic_list__"
TOPIC_KEY = "topic__"
BODY_KEY = "body"
PATH_KEY = "path__"
MAPPER_KEY = "mapper__"
NS_KEY = "ns__"
CALLER_DATA_KEY = "caller_data__"

WAVE_RESUMING_KEY = "wave_resuming__"
WAVE_RESUMING_SOURCES = "wave_resuming_sources__"
WAVE_RESUMING_INFO_KEY = "wave_resuming_info__"
WAVE_FIRST_KEY = "wave_first__"
WAVE_LAST_KEY = "wave_last__"
EXTRA_ENV_KEY = "extra_env__"
GEOQUERY_KEY = "geoquery__"
GEOQUERY_COMPILED_KEY = "geoquery_comp__"

GEOMETRY_SHAPE_KEY = "_geometry"
GEOMETRY_KEY = "geometry"
GEOMETRY_COMP_KEY = "geometry__"
GEOJSON_KEY = "geojson"
GEOLINK_KEY = "geolink"

COMPARISON_PATTERNS = "compare__"

GEOSPECS_KEYS = [GEOMETRY_KEY, GEOMETRY_SHAPE_KEY, GEOJSON_KEY]

UBICATION_KEY = "ubication"

# reserved and private keys
SORT_KEY = "sort__"
REVERSE_SORT_KEY = "reverse_sort__"

FUNC_KEY = "func__"
META_KEY = "meta__"
DOMESTIC_KEY = "domestic__"
CALLABLE_KEY = "call__"
FILTERS_KEY = "filters__"

CRAWLER_KEY = "crawler__"
BOT_KEY = "bot__"

MONOTONIC_KEY = "wave__"
monotonic_wave = time.time_ns

MONOTONIC_SINCE = "since__"
MONOTONIC_SINCE_KEY = "since_key__"
MONOTONIC_SINCE_VALUE = "since_value__"
MONOTONIC_SINCE_OPERATOR = "since_operator__"

DATETIME_KEY = "datetime"
DATETIME_LAST_KEY = "last"
ID_KEY = "id"
PUSHED = "pushed__"
FQUID_KEY = "fquid"
ORG_KEY = "id__"
ORG_URL = "url__"
FORCED_URL = "_url__"
THINK_KEY = "thing"
FORCE_SAVE = "__save"
REG_PRIVATE_KEY = r".*__$"

# ----------------------------------------------------------
# Volumes
# ----------------------------------------------------------
VOL_DATA = "data"


# ----------------------------------------------------------
# Namespaces and Tables
# ----------------------------------------------------------
TEST_NS = "test"
TEST_DB = "test"
SYS_NS = "system"
SYS_DB = "system"


TASK_THING = "tasks"
PARTICLE_THING = "particle"


# ----------------------------------------------------------
# fqid helpers
# ----------------------------------------------------------

# split table:uid from fqid
# TODO: get until ":"
REG_FQID = r"((?P<table>\w+):)?(?P<uid>\w+)$"

REG_SPLIT_ID = re.compile(
    """(?imsx)
    ^
    (?P<thing>[^:]+)(:(?P<id>.+))?$
    """
)
REG_SPLIT_PATH2 = re.compile(
    """(?imsx)
    ^
    (?P<head>.*?)(:(?P<id>[^:]+))$
    """
)
REG_SPLIT_PATH = re.compile(
    r"""(?imsx)
^
(?P<xpath>
 (?P<path>
  (?P<_path>
    (?P<basename>
      (?P<table>[^/:]+)
      [/:]
      (?P<id>[^/:?#]*)
    )
  )
 )
)
(
  \?
  (?P<query>[^#]*)
)?
  (\#(?P<fragment>.*))?
$
"""
)


def build_fqid(fqid, table=""):
    m = re.match(REG_FQID, str(fqid))
    if m:
        d = m.groupdict(default=table)
        return "{table}:{uid}".format_map(d)
    # return table, fqid
    return fqid


def extract_wave(data):
    """Extract wave from tube id: i.e. table:wave
    Example:

    data
    {'air_temperature': 22.2,
     'id': 'meteorological_stations:1726569064209590207',
     'id__': 'weather://aemet/meteorological_stations:6156X',
     'ts': 1726641608058.1094,
     'type': 'test'}

     'id': 'meteorological_stations:1726569064209590207'

    """
    fquid = data[ID_KEY]
    m = REG_SPLIT_ID.match(fquid)
    if m:
        id_ = m.groupdict()["id"]
        if id_ is not None:
            return int(m.groupdict()["id"])
    return 0


def filter_4_compare(data, table=""):
    """Filter data to be used for comparison"""
    if data:
        result = {
            key: value
            for key, value in data.items()
            if not re.match(REG_PRIVATE_KEY, key)
        }
        # check id:
        uid = result.get("id")
        if uid is not None:
            result["id"] = build_fqid(str(uid))
    else:
        result = {}

    return result
