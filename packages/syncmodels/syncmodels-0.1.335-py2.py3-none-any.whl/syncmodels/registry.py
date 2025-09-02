"""
Self Auto-Register classes
"""

import hashlib
import re
import sys

from typing import Callable, List, Dict
from agptools.helpers import (
    best_of,
    parse_xuri,
    parse_uri,
    build_uri,
)

# from agptools.containers import walk, rebuild
import pickle


def names(klass):
    "return a list of names for a class"
    yield klass.__name__
    yield klass.__module__ + "." + klass.__name__


def match_score(item):
    "score by counting how many groups have matched"
    info, m, d = item
    sc = len(m.groups())
    return sc, info


class Record:
    factory: Callable
    args: List
    kwargs: Dict


def blueprint(obj):
    """Get a blueprint of an object.
    mainly designed for code hashing"""
    string = getattr(obj, "__code__", str(id(obj)).encode("utf-8"))
    return hashlib.sha1(string=string, usedforsecurity=True).hexdigest()


class iRegistry:
    "a registry of objects"

    REGISTRY = {}
    MOD_REGISTERED = {}

    @classmethod
    def register_info(cls, patterns, *args, **kwargs):
        "register a class in the registry"
        __key__ = kwargs.pop("__key__", None)
        __factory__ = kwargs.pop("__factory__", None)
        __blueprint__ = blueprint(__factory__)
        if __factory__:
            factory_name = __factory__.__name__
        else:
            factory_name = __factory__
        if isinstance(patterns, str):
            patterns = [patterns]
        for pattern in patterns:
            cls.REGISTRY.setdefault(pattern, {}).setdefault(factory_name, {})[
                __key__
            ] = (
                __blueprint__,
                __factory__,
                args,
                kwargs,
            )

    @classmethod
    def register_itself(cls, patterns, *args, **kwargs):
        "register a class in the registry"

        # kwargs["__klass__"] = cls
        # args = cls, *args
        cls.register_info(patterns, __factory__=cls, *args, **kwargs)

    @classmethod
    def search(cls, uri, __klass__=None, __key__=None):
        """try to locate some info in the registry
        thing: pattern

        candidates: list of options
        options: dict of:
          - 'factory' (name or callable) : { key: info}
          - re.match
        info: callable factory, *args, **kw

        candidates = [
          (
            {'BookingMapper':
              {
                None: (
                   <class 'module.BookingMapper'>,
                   (),
                   {})
                   }
            },
            <re.Match object; span=(0, 7), match='Booking'>
          ),
        ]

        """
        candidates = []

        def check_mro(factory, pattern):
            mro = getattr(factory, "mro", None)
            for parent in mro():
                if re.match(pattern, parent.__name__):
                    return True
            return False

        if not isinstance(__klass__, (list, tuple, set, dict)):
            __klass__ = [__klass__]

        for klass in __klass__:
            for pattern, info in cls.REGISTRY.items():
                # Note: search(uri pattern) + match(uri when used will provide)
                if m := re.search(pattern, uri) or re.match(uri, pattern):
                    candidate = {}
                    for factory, options in info.items():
                        for key, data in options.items():
                            # filter any key when __key__ is provided
                            if __key__ is not None and key != __key__:
                                continue
                            # guess if this data must be considered
                            # 1. klass is not provided
                            c0 = not klass

                            # 2. klass is a regexp (string, not compiled)
                            call = data[1]
                            c1 = (
                                not c0
                                and isinstance(klass, str)
                                and (
                                    isinstance(factory, str)
                                    and check_mro(call, __klass__)
                                )
                            )
                            # 3. klass is a subclass
                            c2 = (
                                not c1
                                and not klass  # TODO: and c0 ?
                                or (
                                    factory
                                    and not isinstance(klass, str)
                                    and issubclass(call, klass)
                                )
                            )
                            if any([c0, c1, c2]):
                                candidate.setdefault(factory, {})[key] = data

                    if candidate:
                        candidates.append((candidate, m, m.groupdict()))

        return candidates

    @classmethod
    def locate(cls, uri, __klass__=None, __key__=None, score=None):
        """try to locate some info in the registry"""
        # Note: candidates has been filtered by __key__ if provided
        candidates = cls.search(uri, __klass__=__klass__, __key__=__key__)

        # get the best option from candidates
        score = score or match_score
        _, options = best_of(candidates, score)
        return options

    @classmethod
    def get_factory(cls, pattern, __klass__=None, __key__=None, score=None, **context):
        "Get factory and parameters from the registry"
        options = cls.locate(pattern, __klass__=__klass__, __key__=__key__, score=score)
        if options:
            # we have a 'complex' stucture so we need to use __key__
            # when is provided, otherwise, any option will satisfy
            # the provided criteria
            if isinstance(options, tuple):
                assert (
                    len(options) == 3
                ), "best_of should return a single item of 3 values: options, m, **extra"
                options, m, kw = options
                context.update(kw)

            if isinstance(options, dict):
                assert len(options) == 1, "best_of should return a single value"
                _factory, final = options.popitem()
                final = pickle.loads(pickle.dumps(final))
                __key__ = __key__ if __key__ in final else list(final).pop()
            elif isinstance(options, tuple):
                pass
            final[__key__][-1].update(context)
            return final[__key__]

        return None, None, None, None

    @classmethod
    def get_(cls, name):
        "get a class from the registry by name"
        for _name in names(cls):
            if (obj := cls.REGISTRY.get(_name).get(name)) is not None:
                break
        return obj

    @classmethod
    def search_(cls, name):
        "do a full search of a class by name in the whole registry database"
        for values in cls.REGISTRY.values():
            if (obj := values.get(name)) is not None:
                break
        return obj

    # --------------------------------------------
    # automaticmod_name.startswith("agptools."):
    # --------------------------------------------
    @classmethod
    def automatic_registering(cls, klasses=None, force=False, *args, **kwargs):
        """Register all classes that are subclasses of a given one"""
        klasses = klasses or cls
        if not hasattr(klasses, "__len__"):
            klasses = [klasses]
        klasses = tuple(klasses)
        if force:
            cls.MOD_REGISTERED.pop(klasses, None)

        universe = cls.MOD_REGISTERED.setdefault(klasses, set())

        for mod_name in universe.symmetric_difference(sys.modules):
            mod = sys.modules.get(mod_name)
            for obj_name, obj in mod.__dict__.items():
                try:
                    if issubclass(obj, klasses):
                        patterns = f"{mod_name}.{obj_name}"
                        # obj.register_itself(patterns=patterns, *args, **kwargs)
                        cls.register_info(patterns, __factory__=obj, *args, **kwargs)
                except TypeError:
                    continue

            universe.add(mod_name)
