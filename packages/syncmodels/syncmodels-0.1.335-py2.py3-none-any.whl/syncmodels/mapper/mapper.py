"""
Mappers transform plain dict to another dict
converting key and values.

Classes definition are inspired on pydantic

"""

import re
import sys
import traceback
import inspect
import itertools
from typing import Dict, List, Union, _GenericAlias

from math import isnan
from datetime import timedelta
from dateutil.parser import parse

from glom import glom, T, Coalesce, SKIP
from pydantic import ValidationError

# ------------------------------------------------
# Converter functions
# ------------------------------------------------
from agptools.helpers import (
    BOOL,
    DATE,
    DURATION,
    FLOAT,
    I,
    INT,
    STRIP,
    TEXT,
    STR,
)

# ---------------------------------------------------------
# Loggers
# ---------------------------------------------------------

from agptools.logs import logger


# ------------------------------------------------
# model support
# ------------------------------------------------
from ..model.model import *


log = logger(__name__)

# =========================================================
# Mappers Support
# =========================================================


def BASIC_ID(x):
    if isinstance(x, str):
        return x.split(":")[-1]
    return x


def VALID(x):
    try:
        if isnan(x):
            return False
    except Exception:
        pass
    return True


ANNOTATION_FACTORY = {
    "List": list,
    "Dict": dict,
}


def lambda_csv(x: List):
    result = []
    x.sort(key=lambda y: y[1])

    for m, key, value in x:
        if value is not None:
            value = str(value).strip()
            value = ",".join(re.findall(r"\w+", value))
            result.append(str(value).strip())

    return ",".join(result)


class Mapper:
    PYDANTIC = None
    _MAPPING = {}
    _REVERSE = {}
    _LAMBDAS = {
        "csv": lambda_csv,
    }

    @classmethod
    def _populate(cls):
        MAP = cls._MAPPING.get(cls)
        if MAP is None:
            MAP = cls._MAPPING[cls] = {}
            REVERSE = cls._REVERSE[cls] = {}
            # explore subclasses
            klasses = cls.mro()[:-1]
            for klass in reversed(klasses):
                for key in dir(klass):
                    value = getattr(klass, key)
                    if isinstance(value, tuple):
                        l = len(value)
                        if l == 2:
                            # is an attribute
                            MAP[key] = *value, None
                        elif l == 3:
                            MAP[key] = value

                        t_name = value[0]
                        if isinstance(t_name, str):
                            REVERSE[key] = t_name
                        elif t_name in (I,):
                            # inverse function of I -> I
                            REVERSE[key] = key
                        else:
                            log.warning("inverse of t_name: %s is unknown", t_name)

        return MAP

    @classmethod
    def _schemes(cls):
        base = {
            "id": "https://portal.ccoc-mlg.spec-cibernos.com/api/schema/{{ normalized.kind }}/latest",
            "ref": "aemet.observation",
            "type": "object",
            "ccoc-label": {"default": "Observación Estación Metereológica AEMET"},
            "properties": {
                "id": {"type": "string", "ccoc-label": {"default": "Id"}},
                "type": {
                    "type": "string",
                    "ccoc-label": {"default": "Type"},
                },
                # extra properties comes here
            },
            "ccoc-extraInformation": {
                "ccoc-defaultDisplayedAttributes": [],
                "ccoc-defaultMapMarkerIcon": {
                    "iconUrl": "",
                    "legendLabel": "",
                },
            },
        }

        MAP = cls._MAPPING.get(cls)
        if MAP is None:
            pass

    @classmethod
    def mapping(cls, org: Dict, only_defined=True, **kw):
        assert isinstance(org, dict)
        result = {} if only_defined else dict(org)
        MAP = cls._populate()

        def parse(value, t_value, t_default):
            if VALID(value):
                if inspect.isfunction(t_value):
                    value = t_value(value)
                # is a fstring?
                elif isinstance(t_value, str):
                    value = t_value.format_map(org)
                # is a typing anotation?
                elif isinstance(t_value, _GenericAlias):
                    if t_value._name in ANNOTATION_FACTORY:
                        # example
                        # data = (r"Data", List[StatisticData], )
                        new_value = {
                            klass: [parse(v, klass, t_default) for v in value]
                            for klass in t_value.__args__
                        }
                        # create the value from Generic specification
                        factory = ANNOTATION_FACTORY[t_value._name]
                        value = factory(
                            itertools.zip_longest(
                                new_value.values(),
                                fillvalue=None,
                            )
                        )
                        value = value[0][0]  # TODO: review
                    else:
                        raise f"don't know how to deal with `{t_value}` typing yet!"
                elif inspect.isclass(t_value) and issubclass(t_value, Mapper):
                    # is another mapper?
                    value = t_value.pydantic(value)
                else:
                    value = t_value(value)
            else:
                value = t_default
            return value

        try:
            org = {
                **org,
                **kw,
            }
            # we need to process larget patterns before shorter ones
            org_keys = list(org)
            org_keys.sort(key=lambda x: len(x.split("_")) * 20 + len(x), reverse=True)

            # loop
            for key, (t_name, t_value, t_default) in MAP.items():
                # try to use a glom specification
                if isinstance(t_name, str):
                    try:
                        value = glom(org, t_name)
                        value = parse(value, t_value, t_default)
                        result.setdefault(key, t_name)
                        continue
                    except Exception as why:
                        pass
                elif isinstance(t_name, (list, tuple)):
                    values = [org[k] for k in t_name]
                    value = t_value(*values)
                    result.setdefault(key, ".".join(t_name))
                    continue
                # try to use a direct regexp match or a function to get the name
                name = None
                if isinstance(t_name, str):
                    for k in org_keys:
                        v = org[k]
                        if m := re.match(f"{t_name}$", k, re.I):
                            # name = m.group(0)
                            name = k  # take the key not the match
                            break
                else:
                    name = t_name(key)

                # if name:  # name in org
                # value = org.get(name, t_default)
                # value = parse(value, t_value, t_default)
                # result.setdefault(key, value)
                result[name] = key

        except Exception as why:  # pragma: nocover
            log.error(why)
            log.error("".join(traceback.format_exception(*sys.exc_info())))
            log.error(f"key: {key} : value: {value}")

        #         # post-actions
        #         for pattern, holder, action in getattr(cls, "COMBINE", []):
        #             values = []
        #             for key, value in list(result.items()):
        #                 if m := re.match(pattern, key):
        #                     values.append([m, key, value])
        #
        #             # result[holder] = cls._LAMBDAS[action](values)
        #             result.setdefault(holder, cls._LAMBDAS[action](values))

        return result

    @classmethod
    def transform(cls, org: Dict, only_defined=False, **kw):
        assert isinstance(org, dict)
        result = {} if only_defined else dict(org)
        MAP = cls._populate()

        def parse(value, t_value, t_default):
            if VALID(value):
                if inspect.isfunction(t_value):
                    value = t_value(value)
                # is a fstring?
                elif isinstance(t_value, str):
                    value = t_value.format_map(org)
                # is a typing anotation?
                elif isinstance(t_value, _GenericAlias):
                    if t_value._name in ANNOTATION_FACTORY:
                        # example
                        # data = (r"Data", List[StatisticData], )
                        new_value = {
                            klass: [parse(v, klass, t_default) for v in value]
                            for klass in t_value.__args__
                        }
                        # create the value from Generic specification
                        factory = ANNOTATION_FACTORY[t_value._name]
                        value = factory(
                            itertools.zip_longest(
                                new_value.values(),
                                fillvalue=None,
                            )
                        )
                        value = value[0][0]  # TODO: review
                    else:
                        raise f"don't know how to deal with `{t_value}` typing yet!"
                elif inspect.isclass(t_value) and issubclass(t_value, Mapper):
                    # is another mapper?
                    value = t_value.pydantic(value)
                else:
                    value = t_value(value)
            else:
                value = t_default
            return value

        try:
            org = {
                **org,
                **kw,
            }
            # we need to process larget patterns before shorter ones
            org_keys = list(org)
            org_keys.sort(key=lambda x: len(x.split("_")) * 20 + len(x), reverse=True)

            # loop
            for key, (t_name, t_value, t_default) in MAP.items():
                # try to use a glom specification
                if isinstance(t_name, (str, list)):
                    try:
                        value = glom(org, t_name)
                        value = parse(value, t_value, t_default)
                        result.setdefault(key, value)
                        continue
                    except Exception as why:
                        pass
                elif isinstance(t_name, tuple):
                    values = [org[k] for k in t_name]
                    value = t_value(*values)
                    result.setdefault(key, value)
                    continue
                # try to use a direct regexp match or a function to get the name
                name = None
                if isinstance(t_name, str):
                    for k in org_keys:
                        v = org[k]
                        if m := re.match(f"{t_name}$", k, re.I):
                            # name = m.group(0)
                            name = k  # take the key not the match
                            break
                else:
                    name = t_name(key)

                # if name:  # name in org
                value = org.get(name, t_default)
                value = parse(value, t_value, t_default)
                result.setdefault(key, value)

        except Exception as why:  # pragma: nocover
            log.error(why)
            log.error("".join(traceback.format_exception(*sys.exc_info())))
            log.error(f"key: {key} : value: {value}")

        # post-actions
        for pattern, holder, action in getattr(cls, "COMBINE", []):
            values = []
            for key, value in list(result.items()):
                if m := re.match(pattern, key):
                    values.append([m, key, value])

            # result[holder] = cls._LAMBDAS[action](values)
            result.setdefault(holder, cls._LAMBDAS[action](values))

        return result

    @classmethod
    def remap(cls, org: Dict, only_defined=False, **kw):
        mapping = cls.mapping_keys(org, only_defined=only_defined, **kw)

        if only_defined:
            result = {}
            for old in set(mapping).intersection(org):
                new = mapping[old]
                result[new] = org[old]
        else:
            result = org.__class__(org)
            for old in set(mapping).intersection(org):
                new = mapping[old]
                result[new] = result.pop(old)

        return result

    @classmethod
    def mapping_keys(cls, org: Dict, only_defined=False, **kw):
        assert isinstance(org, dict)
        result = {}  # if only_defined else dict(org)
        MAP = cls._populate()

        def parse(value, t_value, t_default):
            if VALID(value):
                if inspect.isfunction(t_value):
                    value = t_value(value)
                # is a fstring?
                elif isinstance(t_value, str):
                    value = t_value.format_map(org)
                # is a typing anotation?
                elif isinstance(t_value, _GenericAlias):
                    if t_value._name in ANNOTATION_FACTORY:
                        # example
                        # data = (r"Data", List[StatisticData], )
                        new_value = {
                            klass: [parse(v, klass, t_default) for v in value]
                            for klass in t_value.__args__
                        }
                        # create the value from Generic specification
                        factory = ANNOTATION_FACTORY[t_value._name]
                        value = factory(
                            itertools.zip_longest(
                                new_value.values(),
                                fillvalue=None,
                            )
                        )
                        value = value[0][0]  # TODO: review
                    else:
                        raise f"don't know how to deal with `{t_value}` typing yet!"
                elif inspect.isclass(t_value) and issubclass(t_value, Mapper):
                    # is another mapper?
                    value = t_value.pydantic(value)
                else:
                    value = t_value(value)
            else:
                value = t_default
            return value

        try:
            org = {
                **org,
                **kw,
            }
            for key, (t_name, t_value, t_default) in MAP.items():
                # try to use a glom specification
                if isinstance(t_name, (str, list)):
                    try:
                        result[t_name] = key
                        continue
                    except Exception as why:
                        pass
                elif isinstance(t_name, tuple):
                    values = [org[k] for k in t_name]
                    value = t_value(*values)
                    result[value] = key
                    continue
                # try to use a direct regexp match or a function to get the name
                name = None
                if isinstance(t_name, str):
                    for k, v in org.items():
                        if m := re.match(t_name, k, re.I):
                            # name = m.group(0)
                            name = k  # take the key not the match
                            break
                else:
                    name = t_name(key)

                result[name or t_name] = key

        except Exception as why:  # pragma: nocover
            log.error(why)
            log.error("".join(traceback.format_exception(*sys.exc_info())))
            log.error(f"key: {key} : value: {value}")

        return result

    @classmethod
    def item(cls, org, **extra):
        """Create a pydantic object as well. `source` is already transformed"""
        klass = getattr(cls, "PYDANTIC", None)
        if klass:
            if klass != IgnoreMapper:
                org.update(extra)
                try:
                    # if uid := org.get("id"):
                    #     if isinstance(uid, str):
                    #         org["id"] = uid.split(":")[-1]
                    item = klass(**org)
                except ValidationError as why:
                    log.debug(
                        "FAILED Pydatic Validation: klass: [%s] : [%s]",
                        klass,
                        org,
                    )
                    log.debug(f"{why}")
                    item = None
                return item

        else:
            log.warning("[%s] has not defined a PYDANTIC class", cls)

    @classmethod
    def pydantic(cls, org, **extra):
        """Create a pydantic object as well. `source` is not yet transformed"""
        return cls.item(cls.transform(org, **extra), **extra)


class IgnoreMapper(Mapper):
    """A specific mapper to indicate we don't want to
    create any pydantic class explicity
    (it not forgotten or a mistake)
    """
