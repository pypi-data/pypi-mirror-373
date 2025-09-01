"""Crawler Helpers"""

import re
from datetime import datetime
from typing import List, Dict, Union

from agptools.helpers import DATE, build_uri
from agptools.containers import walk, flatten

from shapely.geometry import (
    shape,
    Point as _Point,
    Polygon as _Polygon,
    MultiPolygon as _MultiPolygon,
)

from ..definitions import ID_KEY, ORG_KEY
from ..crud import parse_duri
from ..model.geojson import BaseGeometry, Point


class SortKeyFinder:
    WANTED_TYPES = tuple([datetime])
    # DATE_KEYS = r"|".join(
    #     [
    #         ".*date",
    #         "time",
    #         "year",
    #         'ts',
    #         "sent",
    #         "rewiew",
    #         "update",
    #         # "entity_ts",
    #     ]
    # )
    DATE_KEYS = [
        # ".*date", # keys that does not belongs to Pydantic models
        "time",
        "year",
        "ts",
        "sent",
        "rewiew",
        "update",
        "entity_ts",
        "datetime",  # check that everything works fine adding this one
    ]

    DATE_REGEXP = re.compile(r"|".join(DATE_KEYS))

    # keys used in model to trace-back the resuming point
    # stored in WAVE_RESUMING_INFO_KEY
    MODEL_DESIRED_SORT_KEYS = set(
        [
            "datimeme",
            # "timestamp",
        ]
    )
    SORT_KEY_CACHE = {}

    @classmethod
    def register(cls, kind, sort_key):
        cls.SORT_KEY_CACHE[kind] = sort_key

    @classmethod
    def get(cls, kind):
        return cls.SORT_KEY_CACHE.get(kind)

    @classmethod
    def differentiable(cls, item):
        """return a convenience key for sorting element that can be sustracted"""
        _range = item[1]
        assert len(_range) == 2
        # x = _range[0] - 1 * (_range[1] - _range[0])
        x = _range[0]
        return x

    @classmethod
    def find_sort_key(cls, stream: List[Dict], kind=None):
        """
        Try to figure-out which is the best key for sortering data stream
        in order to feed the storage as close as possible to the order that
        events must appear in storage for real-time observation and KPI calculation
        """
        universe = {}
        assert isinstance(stream, List), "maybe find_sort_key( [data] ) instead?"

        def criteria(x: List):
            for value in flatten(x):
                break
            else:
                return 10**6

            for idx, pattern in enumerate(cls.DATE_KEYS):
                if re.match(pattern, value):
                    return idx
            return 10**6

        for key, value in walk(stream):
            _key = key[1:]
            if _key and cls.DATE_REGEXP.match(str(_key[-1])):
                value = DATE(value)
            if isinstance(value, cls.WANTED_TYPES):
                klass = value.__class__
                candidates = universe.setdefault(klass, {})
                candidates.setdefault(_key, []).append(value)

        # discard any non-fully-present keys
        for klass, candidates in list(universe.items()):
            for key, samples in list(candidates.items()):
                if len(samples) == len(stream):
                    candidates[key] = min(samples), max(samples)
                else:
                    candidates.pop(key)

            if candidates:
                candidates = list([k, v] for k, v in candidates.items())
                # candidates.sort(key=cls.differentiable)
                candidates.sort(key=criteria)  # select by order in DATE_KEYS
                universe[klass] = candidates[0]
            else:
                universe.pop(klass)
        for type_ in cls.WANTED_TYPES:
            candidates = universe.get(type_)
            if candidates:
                # candidates.sort(key=lambda x: len(x))
                sort_key = candidates[0]
                # example: sort_key = ('sent',)
                if isinstance(sort_key, str):
                    sort_key = tuple([sort_key])
                return sort_key
        return tuple([])


class GeojsonManager:
    @classmethod
    def geo_uri(cls, data):
        "returns the uri of a related object"
        for candidate in [ORG_KEY, ID_KEY]:
            if _sid := data.get(candidate):
                _sid = parse_duri(str(_sid))
                if _sid["fscheme"] != "test":

                    _sid["path"] = "/{thing}/geo".format_map(_sid)
                    fquid = build_uri(**_sid)
                    return fquid

    @classmethod
    def centroid(cls, geojson: Union[BaseGeometry, Dict]):
        """Generic Centroid calculation for any GeoJSON type"""
        if isinstance(geojson, BaseGeometry):
            geojson = geojson.model_dump()
        geom = shape(geojson)
        coords = list(geom.centroid.coords)
        centroid = Point(coordinates=coords[0])
        return centroid
