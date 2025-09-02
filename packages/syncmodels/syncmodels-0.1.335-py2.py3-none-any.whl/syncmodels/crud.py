from typing import List, Dict
import random
import re
import sys
import traceback
from datetime import datetime

from agptools.logs import logger
from agptools.helpers import build_uri, parse_xuri, tf
from agptools.containers import overlap


from .definitions import (
    URI,
    JSON,
    QUERY,
    REG_SPLIT_PATH,
    REG_SPLIT_ID,
    # ORDER_KEY,
    # DIRECTION_KEY,
    # MONOTONIC_SINCE_KEY,
    # MONOTONIC_SINCE_VALUE,
    # MONOTONIC_SINCE_OPERATOR,
    # WHERE_KEY,
)
from .http import STATUS_OK

log = logger(__name__)

# ---------------------------------------------------------
# Default URI handling
# ---------------------------------------------------------

DEFAULT_NAMESPACE = "test"
DEFAULT_DATABASE = "test"
DEFAULT_URI_PARAMS = {
    "fscheme": DEFAULT_DATABASE,
    "host": DEFAULT_DATABASE,
    "xhost": DEFAULT_DATABASE,
}


MAX_HARD_URIS = 200
MAX_SOFT_URIS = 150
last_uris = {}


def esc(uid):
    #  surreal donen't allow integers as id
    # if isinstance(uid, str):
    #     try:
    #         uid = int(uid)
    #     except:
    #         pass
    if isinstance(uid, str):
        uid = uid.strip("_")
        uid = uid.strip("/")
    if uid in (None,):
        return uid
    else:
        uid = str(uid)
    return uid


def parse_duri(uri: URI | QUERY, _ignore_cache_=True, _normalize_=None, **kw) -> QUERY:
    global last_uris
    if isinstance(uri, URI.__supertype__):  # URI
        if _ignore_cache_ or not (_uri := last_uris.get(uri)):

            # try to parse using multiple strategies
            # simple fuid: table:uid
            m = REG_SPLIT_PATH.match(uri)
            if m:
                _uri = m.groupdict()
            else:
                # default strategy
                _uri = parse_xuri(uri)
            # get thing
            m = REG_SPLIT_ID.match(_uri["path"].strip("/"))
            if m:
                _uri.update(m.groupdict())
            if len(last_uris) > MAX_HARD_URIS:
                keys = list(last_uris)
                while n := len(keys) > MAX_SOFT_URIS:
                    last_uris.pop(keys.pop(random.randint(0, n - 1)))
            overlap(_uri, DEFAULT_URI_PARAMS)
            last_uris[uri] = _uri
    elif isinstance(uri, QUERY.__supertype__):
        _uri = uri
        overlap(_uri, DEFAULT_URI_PARAMS)
    else:
        raise RuntimeError(f"uri: {uri} type: {uri.__class__} is not supported")

    overlap(_uri, kw)

    if "_path" not in _uri:
        _uri["_path"] = ""

    if _uri["path"]:
        if _uri["path"][0] != "/":
            _uri["path"] = f"/{_uri['path']}"

        if _uri.get("basename") is None:
            _uri["basename"] = _uri["table"] = _uri["_path"]

    #     if _uri.setdefault("path", "/")[:1] != "/":
    #         _uri["path"] = f"/{_uri['path']}"
    #
    #     if _uri.setdefault("xpath", "/")[:1] != "/":
    #         _uri["xpath"] = f"/{_uri['xpath']}"

    if _normalize_ and isinstance(_normalize_, str):
        _normalize_ = [_normalize_]

    for pattern in _normalize_ or []:
        for _ in _uri:
            if re.match(pattern, _):
                _uri[_] = tf(_uri[_])

    return _uri


def complete_duri(uri: URI | QUERY, _ignore_cache_=False, **kw) -> QUERY:
    _uri = parse_duri(uri, _ignore_cache_=_ignore_cache_)
    uri = build_uri(**_uri)
    return uri


# ---------------------------------------------------------
# Basic iCRUD proposal
# ---------------------------------------------------------
class iConnection:
    def create(self, thing, data, record_id=None):
        log.warning(
            "create(%s) is not implemented yet for: [%s]",
            thing,
            self,
        )
        return []

    def update(self, thing, data, record_id=None):
        log.warning(
            "update(%s) is not implemented yet for: [%s]",
            thing,
            self,
        )
        return []

    def query(self, thing, data, record_id=None):
        log.warning(
            "query(%s) is not implemented yet for: [%s]",
            thing,
            self,
        )
        return []

    def select(self, thing, data, record_id=None):
        log.warning(
            "select(%s) is not implemented yet for: [%s]",
            thing,
            self,
        )
        return []

    def use(self, namespace, database):
        log.warning(
            "use(%s) is not implemented yet for: [%s]",
            namespace,
            self,
        )


class iCRUD:
    async def get(self, uri: URI):
        "Get an object from URI"
        raise NotImplementedError()

    async def put(self, uri: URI, data: JSON = None, context={}, **kw) -> bool:
        "Put an object from URI"
        raise NotImplementedError()

    async def update(self, uri: URI, data: JSON = None, **kw) -> bool:
        "Update an object from URI"
        raise NotImplementedError()

    async def delete(self, uri: URI):
        "Delete an object from URI"
        raise NotImplementedError()

    async def query(self, query: URI | QUERY, **params) -> List[JSON]:
        "Make a query to the system based on URI (pattern)"
        log.warning(
            "query(%s) is not implemented yet for: [%s]",
            query,
            self,
        )
        return []


class iConnectionPool:
    "manage multiples connection based on URI"

    def __init__(self, url):
        super().__init__()
        self.url = url

        # self.connection = None
        self.connections = {}
        self.last_connection = None

    def close(self):
        "close connection pool"

    async def prepare_call(self, uri):
        _uri = parse_duri(uri)
        # mapping to surreal
        namespace = tf(_uri.get("fscheme", DEFAULT_NAMESPACE))
        database = tf(_uri.get("host", DEFAULT_DATABASE))
        thing = tf(_uri["thing"])
        # surreal special chars: ⟨ ⟩
        # tube mode
        key = namespace, database
        connection = self.connections.get(key) or await self._connect(*key)
        assert connection, f"{self} get connection has failed"

        return connection, thing, _uri

    async def _connect(self, *key) -> iConnection:
        raise NotImplementedError()


class iPolicy:
    "base of criteria / policies"

    DISCARD = "discard"
    STORE = "store"

    def __init__(self, storage):
        self.storage = storage

    async def action(self, mode, thing, data):
        return self.STORE


class iStorage(iCRUD):

    connection_pool: iConnectionPool

    def __init__(self, url, policy=iPolicy):
        super().__init__()
        self.url = url
        self.policy = policy(storage=self)
        self.connection_pool = None
        self._index_2_create = {}
        self._table_metadata = {}

    def register_index(self, fquid: str, keys: List[str]):
        _uri = parse_xuri(fquid)
        if _uri.pop("id", None):
            _uri["path"] = (
                f"/{_uri['_path']}"  # force remove "id" and give back compability
            )
            table = build_uri(**_uri)
            self._index_2_create.setdefault(table, set()).update(keys)

    async def build_indexes(self):
        "build the registered indexes"

    def register_metadata(self, fquid: str, meta: Dict):
        _uri = parse_xuri(fquid)
        if _uri.pop("id", None):
            _uri["path"] = (
                f"/{_uri['_path']}"  # force remove "id" and give back compability
            )
            table = build_uri(**_uri)
            self._table_metadata[table] = meta

    async def build_meta(self):
        "build the registered indexes"

    async def start(self):
        "any action related to start storage operations"

    async def stop(self):
        "any action related to stop storage operations"

    async def live(self, uri: URI) -> JSON:
        "Make a live query to the system based on URI (pattern)"
        raise NotImplementedError()

    def running(self):
        return 0

    async def save(self, nice=False, wait=False):
        "TBD"
        raise NotImplementedError()

    async def merge(self, uri: URI, data: JSON = None, **kw) -> bool:
        if data is None:
            data = kw
        else:
            data.update(kw)

        try:
            connection, thing, _uri = await self.connection_pool.prepare_call(uri)
            # better use uri["id"] as has been converted to str
            # due surreal restrictions (can't use int as 'id')
            record_id = _uri["id"] or data.get("id", None)

            # we need to check if uri['thing'] and
            # data['id'] contains the same info about 'thing'
            # in order not duplicate (and add) the same info

            def update(record_id):
                # _uri2 = parse_duri(record_id)
                m = REG_SPLIT_ID.match(record_id)
                if m:
                    d = m.groupdict()
                    if _uri["thing"] in d["thing"] and d["id"]:
                        return d["id"]
                record_id = tf(record_id)
                record_id = esc(record_id)
                return record_id

            now = str(datetime.utcnow())
            data["datetime"] = data.get("datetime") or now

            if record_id:
                record_id = update(record_id)
                # update record
                _data = {k: v for k, v in data.items() if v is not None}
                _data.pop(
                    "id", None
                )  # can't use record_id and data['id]. It'll fail in silence
                result = connection.merge(thing, _data, record_id=record_id)
                # result = connection.update(thing, data, record_id=record_id)
                if result.status == "OK" and result.result is None:
                    data["created"] = data.get("created") or now
                    result = connection.upsert(thing, data, record_id=record_id)

            else:
                # create a new one
                result = connection.create(thing, data)

            return result.result and result.status in (
                "OK",
                STATUS_OK,
            )  # True|False

        except Exception as why:  # pragma: nocover
            log.error(why)
            log.error("".join(traceback.format_exception(*sys.exc_info())))

    async def put(self, uri: URI, data: JSON = None, context={}, **kw) -> bool:
        if data is None:
            data = kw
        # else:
        #     data = {**data, **kw}

        try:
            connection, thing, _uri = await self.connection_pool.prepare_call(uri)
            # better use uri["id"] as has been converted to str
            # due surreal restrictions (can't use int as 'id')
            record_id = _uri["id"] or data.get("id", None)

            # we need to check if uri['thing'] and
            # data['id'] contains the same info about 'thing'
            # in order not duplicate (and add) the same info

            def update(record_id):
                # _uri2 = parse_duri(record_id)
                m = REG_SPLIT_ID.match(record_id)
                if m:
                    d = m.groupdict()
                    if _uri["thing"] in d["thing"] and d["id"]:
                        return d["id"]
                record_id = tf(record_id)
                record_id = esc(record_id)
                return record_id

            if record_id:
                record_id = update(record_id)
                data.pop(
                    "id", None
                )  # can't use record_id and data['id]. It'll fail in silence
                result = connection.upsert(thing, data, record_id=record_id)
                # result = connection.update(thing, data, record_id=record_id)
            else:
                # create a new one
                result = connection.create(thing, data)

            return result.result and result.status in (
                "OK",
                STATUS_OK,
            )  # True|False

        except Exception as why:  # pragma: nocover
            log.error(why)
            log.error("".join(traceback.format_exception(*sys.exc_info())))

    async def update(self, query: URI | QUERY, data: JSON = None, **kw) -> List[JSON]:
        "Update object from URI"
        if data is None:
            data = kw
        else:
            data.update(kw)

        # TODO: REVIEW!
        record_id = data.get("id", -1)
        if record_id is not None:
            if record_id != -1:
                # update single record
                pool = self.connection_pool
                conn, table, _uri = await pool.prepare_call(query)
                record_id = esc(record_id)
                _data = {**data}
                _data.pop("id")
                result = conn.upsert(table, _data, record_id=record_id)
            else:
                # update many as record_id is not provided
                stream = await self.query(query)
                pool = self.connection_pool
                conn = pool.last_connection  # reuse exact same connection
                if stream:
                    for _data in stream:
                        _data.update(data)
                        m = REG_SPLIT_PATH.match(_data["id"])
                        d = m.groupdict()
                        table = d["_path"]
                        result = conn.update(table, _data)
                else:
                    return False
        else:
            # insert a single record getting a fresh record_id
            _uri = parse_duri(query)
            table = _uri["_path"]
            data.pop("id", None)
            result = conn.insert(table, data)

        return result.result and result.status in ("OK",)  # True|False

    async def get(self, uri: URI, cache=True) -> JSON:
        try:
            pool = self.connection_pool
            conn, table, _uri = await pool.prepare_call(uri)
            record_id = _uri["id"]
            record_id = esc(record_id)
            res = conn.select(table, record_id)
            result = res.result
            if result:
                data = result[0]
                return data
        except Exception as why:  # pragma: nocover
            log.warning(why)  # pragma: nocover

    async def delete(self, uri: URI):
        "Delete an object from URI"
        try:
            pool = self.connection_pool
            conn, table, _uri = await pool.prepare_call(uri)
            record_id = _uri["id"]
            record_id = esc(record_id)
            res = conn.delete(table, record_id)
            data = res.result
            return data
        except Exception as why:  # pragma: nocover
            log.warning(why)  # pragma: nocover

    async def query(self, query: URI | QUERY, **params) -> List[JSON]:
        _uri = parse_duri(query)
        # mapping to surreal
        namespace = tf(_uri.get("fscheme", DEFAULT_NAMESPACE))
        database = tf(_uri.get("host", DEFAULT_DATABASE))
        # path = tf(_uri.get("path", "/"))
        key = namespace, database

        pool = self.connection_pool
        connection = pool.connections.get(key) or await pool._connect(*key)
        assert connection, f"connection from {pool} has failed"

        thing = _uri["thing"]  # must exists
        thing = tf(thing)
        data = _uri.get("query_", {})
        data.update(params)

        res = connection.query(thing, data)
        self.last_connection = connection
        return res.result
