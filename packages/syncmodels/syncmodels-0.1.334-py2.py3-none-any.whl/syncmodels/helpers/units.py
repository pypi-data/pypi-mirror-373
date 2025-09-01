import sys
import traceback

from pydantic import BaseModel

from agptools.logs import logger

from syncmodels.crawler import iPlugin, iAsyncCrawler
from syncmodels.geofactory import GeoFactory
from syncmodels.mapper import Mapper
from syncmodels.model import Enum
from syncmodels.model.geofilters import GeoFilterDefinition
from syncmodels.session import iSession
from syncmodels.registry import iRegistry

# ---------------------------------------------------------
# Loggers
# ---------------------------------------------------------
log = logger(__name__)


class UnitInventory(dict):
    """Helper class to build inventory of classes from a `unit` module"""

    DEFAULT_CATEGORIES = [
        BaseModel,
        Enum,
        iSession,
        Mapper,
        iPlugin,
        iAsyncCrawler,
        iRegistry,
        GeoFilterDefinition,
        GeoFactory,
    ]

    def build_all(self, name, **kw):
        """Build the whole inventory"""
        self.build_inventory(name, **kw)
        self.bootstrap(**kw)

    def build_inventory(self, name, local=True, final=True, categories=None, **_):
        """Build an inventory of some categories classes"""
        mod = sys.modules[name]
        inventory = self
        categories = self.DEFAULT_CATEGORIES if categories is None else categories
        for key, item in mod.__dict__.items():
            # print(f"{key}: {item}")
            for klass in categories:
                try:
                    if item == klass:
                        # skip category classes itself
                        continue
                    if local and item.__module__ != name:
                        # skip outside definitions
                        break

                    # check by name
                    if isinstance(klass, str):
                        candidates = [str(item)]
                        try:
                            for _ in item.mro():
                                candidates.append(_.__name__)
                        except Exception as why:
                            pass
                        if klass in candidates:
                            inventory.setdefault(klass, {})[key] = item
                        continue

                    # fallback (may raise an Exception)
                    # check subclass
                    if issubclass(item, klass):
                        inventory.setdefault(klass.__name__, {})[key] = item
                except AttributeError:
                    pass
                except TypeError:
                    pass
                except Exception as why:
                    log.error(why)
                    msg = "".join(traceback.format_exception(*sys.exc_info()))
                    log.exception(msg)

        if final:
            # try to remove any intermediate class
            for options in inventory.values():
                for parent_name, parent_klass in list(options.items()):
                    for child_name, child_klass in options.items():
                        if child_name != parent_name and issubclass(
                            child_klass, parent_klass
                        ):
                            options.pop(parent_name)
                            break

        return inventory

    def bootstrap(self, **_):
        """Get all bootstrap initial setup"""
        bootstrap = {}

        for name, klass in self.get(iAsyncCrawler.__name__, {}).items():
            crawler = klass()
            bootstrap[name] = list(crawler.default_bootstrap())

        return bootstrap
