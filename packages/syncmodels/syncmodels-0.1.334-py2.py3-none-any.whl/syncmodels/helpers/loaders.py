"""
A basic dynamic module loader
"""

import importlib
import re
import os
import traceback
import sys
from typing import List
import yaml

from agptools.helpers import best_of

# ---------------------------------------------------------
# Loggers
# ---------------------------------------------------------

# from agptools.logs import logger

# log = logger(__name__)

# subloger = logger(f'{__name__}.subloger')
# import jmespath


# ----------------------------------------------------------
# Dynamic Loaders
# ----------------------------------------------------------
class ModuleLoader:
    """A minimal module loader class"""

    ACTIVE_PORT_KEY = "active_ports"

    @classmethod
    def get_project_root(cls):
        """
        obtain the root of project, so imports such:
        - <module>.a.b.c may possible.
        """

        def score(path: str, file: List):
            item = path.split(os.path.sep)
            for r, value in enumerate(file):
                if r >= len(item) or item[r] != value:
                    break
            r -= 1
            return r, os.path.sep.join(item[:r])

        file = __file__.split(os.path.sep)
        score, item = best_of(sys.path, score, file)
        return item

    def __init__(self, top):
        self.root = self.get_project_root()

        if not isinstance(top, str):
            # should be a module
            top = os.path.dirname(top.__file__)
        if os.path.isfile(top):
            top = os.path.dirname(top)
        self.top = top
        self.active_ports = [".*"]
        self.load_config()

    def load_config(self, path="config.yaml"):
        for _path in self.find(type_="f", name=path):
            try:
                cfg = yaml.load(open(_path, encoding="utf-8"), Loader=yaml.Loader)
                self.active_ports = cfg.get(self.ACTIVE_PORT_KEY, self.active_ports)
            except Exception as why:  # pragma: nocover
                print(f"ERROR loading {_path}: {why}")
            break
        return self.active_ports

    @staticmethod
    def match_any_regexp(name, active_ports) -> bool:
        for regex in active_ports:
            if re.match(regex, name):
                return True
        return False

    def available_modules(self, active_ports=None) -> List[str]:
        names = []

        active_ports = active_ports or self.active_ports

        top = self.top
        for _root, _folders, _files in os.walk(top):
            for _name in _files:
                _name, _ext = os.path.splitext(_name)
                if _ext not in (".py",) or _name.startswith("__"):
                    continue
                _path = os.path.join(_root, _name)
                _path = _path.split(top)[-1].split(os.path.sep)[1:]
                _path = ".".join(_path)
                if self.match_any_regexp(_path, active_ports):
                    names.append(_path)

        names.sort()
        return names

    def load_modules(self, names):

        top = self.top
        # old = list(sys.path)
        # sys.path.insert(0, top)
        modules = []
        for name in names:
            name = f"{top}.{name}"
            name = name.split(self.root)[1][1:].replace("/", ".")
            try:
                print(f"Loading: {name}")
                mod = importlib.import_module(name)
                # mod = __import__(name)
                modules.append(mod)
            except ImportError as why:
                print(f"ERROR importing: {name}")
                print(why)
                info = traceback.format_exception(*sys.exc_info())
                print("".join(info))
        # sys.path = old
        return modules

    def find(self, type_=tuple(["d", "f"]), name=".*", top=None):
        "mimic unix `find` command"
        if not isinstance(type_, list):
            type_ = list(type_)

        top = top or self.root
        if isinstance(top, str):
            top = [top]

        for _top in top:
            for root, folders, files in os.walk(_top):
                candidates = {
                    "d": folders,
                    "f": files,
                }
                for t in type_:
                    for _name in candidates.get(t, []):
                        if re.match(name, _name):
                            yield os.path.join(root, _name)
