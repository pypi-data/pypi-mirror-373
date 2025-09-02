import sys
import re
from typing import NewType, List
from pydantic import AnyUrl

from agptools.loaders import ModuleLoader
from agptools.containers import flatten

# type definitions
Text = NewType("Text", str)
URL = NewType("URL", str)
TextObject = NewType("TextObject", str)
PropertyValue = NewType("PropertyValue", str)
Event = NewType("Event", str)
InteractionCounter = NewType("InteractionCounter", str)
Date = NewType("Date", str)
Grant = NewType("Grant", str)
GenderType = NewType("GenderType", str)
DefinedTerm = NewType("DefinedTerm", str)
Integer = NewType("Integer", int)
DateTime = NewType("DateTime", str)
Number = NewType("Number", float)
Boolean = NewType("Boolean", bool)
Time = NewType("Time", str)
BusinessEntityType = NewType("BusinessEntityType", str)
AdultOrientedEnumeration = NewType("AdultOrientedEnumeration", str)
CssSelectorType = NewType("CssSelectorType", str)
XPathType = NewType("XPathType", str)
ItemListOrderType = NewType("ItemListOrderType", str)


# --------------------------------------------------
# Dynamically class loader
# --------------------------------------------------
RESERVED_MAP = {"class": "class_", "yield": "yield_"}


def fileof(name):
    name = name.strip().lower()
    return RESERVED_MAP.get(name, name)


DEFERRED_LOADS = set()


def lazy_load(*names):
    flat = flatten(names)
    DEFERRED_LOADS.update(flat)


loader = ModuleLoader(__file__)


def load_model(name):
    # tokens = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', name)
    # tokens =[ _.title() for _ in tokens]
    # name = "".join(tokens)
    mod_name = fileof(name)
    if not (model := MODEL_REGISTRY.get(mod_name)):
        for mod in loader.load_modules([mod_name]):
            pass
            # return getattr(mod, name)
    model = MODEL_REGISTRY.get(mod_name)
    return model


def load_models(frame=None, builtins=False):
    frame = frame or sys._getframe(1)
    frame_locals = frame.f_locals

    while DEFERRED_LOADS:
        name = DEFERRED_LOADS.pop()
        if model := load_model(name):
            # model.update_forward_refs()  # Resolve the forward reference
            frame_locals[model.__name__] = model
            if builtins:
                __builtins__[model.__name__] = model


def install_models(*names, builtins=False):
    frame = sys._getframe(1)
    frame_locals = frame.f_locals

    if names:
        pending = set(names)
        final = set()
        while pending:
            name = pending.pop()
            final.add(name)
            deps = MODEL_DEPENDENCES.get(name, [])
            pending.update(set(deps).difference(final))
            # print(f"pending: {len(pending)}")

    else:
        final = set(MODEL_REGISTRY)

    lazy_load(*names)
    load_models(builtins=builtins)  # any mising unloaded model

    for key in final:
        if key.islower():
            continue
        if model := MODEL_REGISTRY.get(key):
            frame_locals[key] = model

    foo = 1


# --------------------------------------------------
# Model Dependences
# --------------------------------------------------

MODEL_DEPENDENCES = {}


def model_dependence(name, *names):
    flat = flatten(names)
    MODEL_DEPENDENCES.setdefault(name, set()).update(flat)
    lazy_load(*names)


# --------------------------------------------------
# Central registry
# --------------------------------------------------

MODEL_REGISTRY = {}


def register_model(cls):
    name = cls.__name__
    MODEL_REGISTRY[cls.__name__] = cls
    MODEL_REGISTRY[fileof(name)] = cls
    return cls


def rebuild_models():
    frame = sys._getframe(1)
    frame_locals = frame.f_locals
    for model in MODEL_REGISTRY.values():
        frame_locals[model.__name__] = model
