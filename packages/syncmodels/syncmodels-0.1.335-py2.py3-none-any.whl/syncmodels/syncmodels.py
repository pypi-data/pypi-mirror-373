"""Main module."""

# library modules
# import asyncio
import os

# import pickle
import re
import time
from typing import List, Dict

# import time

# import uvloop

# import ryaml
import yaml

# library partial
# from time import sleep


# 3rd party libraries
# ---------------------------------------------------------
# helpers
# ---------------------------------------------------------
from agptools.containers import walk, rebuild, SEP, list_of, myassign, exclude_dict
from agptools.logs import logger
from syncmodels.definitions import UID_TYPE

# ---------------------------------------------------------
# storage
# ---------------------------------------------------------

# local imports
from .definitions import MONOTONIC_KEY, monotonic_wave, URI, QUERY, JSON
from .helpers import expandpath
from .storage import SurrealistStorage
from .wave import iWaves

# from .parallel import  AsyncParallel
from .crud import iCRUD
from .storage import Storage, WaveStorage
from .model.model import BaseModel

# ---------------------------------------------------------
# Loggers
# ---------------------------------------------------------


log = logger(__name__)

# subloger = logger(f'{__name__}.subloger')


# =========================================================
# syncmodels
# =========================================================


class COPY:
    pass


# =========================================================
# Transformer
# =========================================================
# TODO: agp: used?
class Transformer:
    # governance data
    MAPPERS = {}
    RESTRUCT_DATA = {}
    RETAG_DATA = {}
    REFERENCE_MATCHES = []
    KINDS_UID = {}

    REG_KIND = r"(?P<parent>[^-]*)(-(?P<sub>.*))?$"

    def convert_into_references(self, data: Dict):
        """
        Search for nested objects in `value` and convert them into references
        """
        if self.REFERENCE_MATCHES:
            id_keys = list(
                walk(
                    data,
                    keys_included=self.REFERENCE_MATCHES,
                    include_struct=False,
                )
            )
            for idkey, idval in id_keys:
                # myassign(value, myget(value, idkey), idkey[:-1])
                myassign(data, idval, idkey[:-1])

        return data

    def new(self, kind: str, data: Dict):
        """Try to create / update an item of `type_` class from raw data

        - convert nested data into references
        - convert data to suit pydantic schema
        - get the pydantic item

        """
        data2 = self.convert_into_references(data)
        d = re.match(self.REG_KIND, kind).groupdict()
        real_kind = d["parent"]
        klass = self.MAPPERS.get(real_kind)
        if not klass:
            # TODO: remove debug
            log.warning("missing MAPPERS[%s] class!", kind)
            return

        item = klass.pydantic(data2)
        return item

    def _restruct(self, kind: str, data: Dict, reveal: Dict):
        """
        Restructure internal data according to `RESTRUCT_DATA` structure info.
        Finally the result is the overlay of the original `data` and the
        restructured one.
        """
        restruct = {}
        info = self.RESTRUCT_DATA.get("default", {})
        info.update(self.RESTRUCT_DATA.get(kind, {}))
        for path, value in reveal.items():
            for pattern, (new_path, new_value) in info.items():
                m = re.match(pattern, path)
                if m:
                    d = m.groupdict()
                    d["value"] = value
                    key = tuple(new_path.format_map(d).split(SEP))
                    _value = value if new_value == COPY else new_value.format_map(d)
                    restruct[key] = _value

        # build the restructured data
        restruct = rebuild(restruct, result={})
        # create the overlay of both data to be used (possibly) by pydantic
        data = {**data, **restruct}

        return data

    def _transform(self, kind: str, data: Dict):
        return data


# =========================================================
# syncmodel Namespace and Surreal Storage Support
# =========================================================


def apply_fqui(item: BaseModel, force=False):
    # TODO: glbot wiki uses base64, so review use of this function
    # TODO: use tf() method to unify uid generation
    if hasattr(item, "id"):
        if isinstance(item.id, str):
            # if _ := re.match(r"(?P<table>[^:]+):(?P<uid>[^:]+)$", item.id):
            return item.id
        klass = item.__class__
        kind = f"{klass.__module__.replace('.', '_')}_{klass.__name__}"

        uid = str(item.id).replace("/", "_").replace(".", "_")
        if ":" in uid:
            # TODO: escape special uid chars
            log.warning("uid [%s] must be escaped to be inserted into surreal", uid)
        fqid = f"{kind}:{uid}"
        item.id = fqid
    else:
        klass = item.__class__
        kind = f"{klass.__module__.replace('.', '_')}_{klass.__name__}"
        if force:
            uid = monotonic_wave()
            fqid = f"{kind}:{uid}"
        else:
            fqid = kind
    return fqid


class SyncModel(iCRUD):
    # MAPPERS = {}
    # RESTRUCT_DATA = {}
    # RETAG_DATA = {}
    # REFERENCE_MATCHES = []
    # KINDS_UID = {}
    # MODEL = None  # callable to create a Model instance

    def __init__(
        self,
        config_path=None,
        storage: List[iCRUD] = None,
        surreal_url=None,
        alt_storage: iCRUD = None,
        mode=iWaves.MODE_SNAPSHOT,
        exclude="None",
        *args,
        **kw,
    ):
        if not config_path:
            config_path = "config.yaml"
        config_path = expandpath(config_path)
        self.root = os.path.dirname(config_path)
        self.stats_path = os.path.join(self.root, "stats.yaml")
        self.mode = mode

        self.cfg = {}
        try:
            with open(config_path, "rt", encoding="utf-8") as f:
                self.cfg = yaml.load(f, Loader=yaml.Loader)
        except Exception as why:  # pragma: nocover
            log.warning(why)  # pragma: nocover

        self.model = {}
        self.exclude = exclude
        # storage
        if storage is None:
            surreal_url = surreal_url or self.cfg.get(
                "surreal_url", "http://localhost:9000"
            )
            # storage = SurrealStorage(url=surreal_url)
            sur = SurrealistStorage(url=surreal_url)
            storage = [
                sur,
            ]

        self.storage = list_of(storage, Storage, WaveStorage)
        self.alt_storage = list_of(alt_storage, Storage, WaveStorage)
        if alt_storage:
            self.storage.extend(self.alt_storage)

    async def get(self, uri: URI):
        "Get an object from URI"
        results = {}
        for storage in self.storage:
            data = await storage.get(uri)
            fqui = data.get("id")
            results[fqui] = data

        return results

    async def query(self, query: URI | QUERY, **params) -> Dict[UID_TYPE, JSON]:
        "Make a query to the system based on URI (pattern)"

        results = {}
        for storage in self.storage:
            for data in await storage.query(query, **params):
                fqui = data.get("id__", data.get("id"))  # TODO: use KEY_xxxx
                results.setdefault(fqui, data)

        return results

        # log.warning(
        #     "query(%s) is not implemented yet for: [%s]",
        #     query,
        #     self,
        # )
        # return []

    async def put(self, item: BaseModel, context={}, **kw) -> bool:
        """Try to create / update an item of `type_` class from raw data

        - get the pydantic item
        - save it to storage in case it have changed

        Returns:
        - bool: True if the item has been saved, False otherwise

        """
        results = []
        if item:
            data = item.model_dump(mode="json")
            if self.exclude:
                data = exclude_dict(data, self.exclude)

            assert MONOTONIC_KEY not in data

            # Finally I choose to bless any record with 'wave'
            # information, so it will be possible to use the value
            # for synchronization purposes despite it was not
            # intended at first.

            # Add a MONOTONIC_KEY to the record to be saved in DB
            # pydantic will ignore it on object reconstruction
            # when data is retrieved from DB, but can be used for
            # swarmtube or any other synchronization problems

            # Note: this MONOTONIC_KEY will be the same across all storages
            data[MONOTONIC_KEY] = kw.get(MONOTONIC_KEY) or monotonic_wave()

            fqid = apply_fqui(item, force=True)
            # create/update save data into all storages
            kw["uri"] = fqid
            kw["data"] = data
            for storage in self.storage:
                result = await storage.put(context=context, **kw)
                results.append(result)

        return all(results)

    async def build_indexes(self):
        for storage in self.storage:
            await storage.build_indexes()

    async def build_meta(self):
        for storage in self.storage:
            await storage.build_meta()

    async def update_meta(self, tube, meta: Dict, merge=True) -> bool:
        """Update tube metadata, using an item as reference"""
        assert isinstance(tube, str), "update_meta need a tube as string"
        results = []
        #         fqid = apply_fqui(item, force=True)
        #
        #         tube = fqid.split(":")[0]
        # create/update meta-data into all storages
        for storage in self.storage:
            if isinstance(storage, WaveStorage):
                result = await storage.update_meta(tube, meta, merge=merge)
                results.append(result)

        return all(results)

    async def find_meta(self, tube, **meta):
        """Find tubes that match the specified meta"""
        result = {}
        for storage in self.storage:
            if isinstance(storage, WaveStorage):
                result[storage] = await storage.find_meta(tube, meta)
        return result

    async def save(self, nice=False, wait=False):
        """TBD"""
        results = []
        for storage in self.storage:
            result = await storage.save(nice=nice, wait=wait)
            results.append(result)

        return all(results)

    def running(self):
        return sum([storage.running() for storage in self.storage])
