import asyncio
import sys
import traceback
import tarfile
import zipfile
import io
import json
import os
import gzip
import bz2
import lzma as xz
import time
import html

from datetime import datetime
from jinja2 import Template
import pandas as pd
from aiohttp import FormData
from agptools.helpers import build_uri, parse_xuri, parse_uri, tf
from agptools.containers import overlap
from agptools.logs import logger
from agptools.files import ContentIterator


from syncmodels.definitions import (
    BODY_KEY,
    MAX_ROWS,
    BODY_FORMAT,
    # KIND_KEY,
    METHOD_KEY,
    MONOTONIC_KEY,
    # MONOTONIC_SINCE,
    MONOTONIC_SINCE_KEY,
    MONOTONIC_SINCE_VALUE,
    URI,
    DURI,
    WAVE_LAST_KEY,
    WAVE_RESUMING_INFO_KEY,
    WAVE_RESUMING_SOURCES,
)
from syncmodels.mapper.mapper import Mapper
from syncmodels.auth import iAuthenticator

from syncmodels.http import (
    guess_content_type,
    APPLICATION_JSON,
    APPLICATION_ZIP,
    APPLICATION_GTAR,
    APPLICATION_MS_EXCEL,
    APPLICATION_OCTET_STREAM,
    TEXT_CSV,
    APPLICATION_PYTHON,
    TEXT_HTML,
)

from syncmodels.crawler import iRunner

from ..crud import parse_duri, DEFAULT_DATABASE, DEFAULT_NAMESPACE

from ..context import iContext
from ..schema import iSchema, StructShema
from ..registry import iRegistry
from ..requests import iResponse

log = logger(__name__)


class iSession(iContext, iSchema, iRegistry):  # , iAuthenticator):
    "The base for all 3rd party session accessors"

    DEFAULT_METHOD = "get"

    RESPONSE_META = ["headers", "links", "real_url"]

    CACHE = {}
    "some data to be cached and shared"

    QUERY_BODY_KEY = "json"
    PARAMS_KEY = "params"

    HEADERS = {}

    def __init__(self, bot, headers=None, **kw):
        self.bot = bot
        self.connection_pool = {}
        self.headers = headers or dict(self.HEADERS)
        self.context = kw

    async def _schema(self, uri: URI, data=None, **kw):
        schema = self.CACHE.get(uri)  # .get(_uri[KIND_KEY])
        if not schema:
            schema = await self._get_schema(uri, data, **kw)
        return schema

    async def _create_connection(self, uri: DURI, **_uri):
        raise NotImplementedError()

    def _get_base_url(self, **kw) -> URI:
        params = {
            key: kw.get(key) or self.context.get(key) for key in ["fscheme", "xhost"]
        }
        url = build_uri(**params)
        return url

    def _postprocess_df(self, df, context):
        df["row"] = range(len(df))
        last_row = (
            context.get("wave_last__")
            and context["wave_last__"][0].get("items")
            and context["wave_last__"][0]["items"][0].get("row")
        )
        if max_rows := context.get(MAX_ROWS):
            if last_row:
                df = df[df["row"] > last_row].head(max_rows)
            else:
                df = df.head(max_rows)
        return json.loads(df.to_json(orient="records"))

    def _parse_escaped_json_table(self, raw_html: bytes):
        try:
            unescaped = html.unescape(raw_html)
            normalized = (
                unescaped.replace("<br>", "\n")
                .replace(r"<br/>", "\n")
                .replace(r"<\/br>", "\n")
                .replace(r"<br />", "\n")
                .replace("\\/", "/")
                .replace(r"\n", "\\n")
            )

            table = json.loads(normalized)
            df = pd.DataFrame(table[1:], columns=table[0])

            cols_to_split = [col for col in df.columns if "\n" in col]
            for col in cols_to_split:
                new_cols = col.split("\n")
                df[new_cols] = df[col].astype(str).str.split("\n", expand=True)
                df.drop(columns=[col], inplace=True)

            for col in df.columns:
                df[col] = df[col].astype(str).str.replace("\n", " ").str.strip()

            return df
        except Exception as e:
            log.error("❌ Cannot parse HTML table: %s", e)
            return pd.DataFrame()

    async def _process_response(self, response):
        def expand(value):
            iterator = getattr(value, "items", None)
            if iterator:
                value = {k: expand(v) for k, v in iterator()}
            return value

        meta = {
            # k: expand(getattr(response, k, None))
            # for k in self.RESPONSE_META
            # if hasattr(response, k)
        }
        headers = getattr(response, "headers", {})
        meta.update(headers)
        content_type = guess_content_type(headers)

        t0 = time.time()  # TODO: used a timed context
        try:
            if content_type == APPLICATION_JSON:
                stream = await response.json()

            elif content_type in (
                APPLICATION_ZIP,
                APPLICATION_GTAR,
            ):
                raw = await response.read()  # bytes object
                # stream = []
                # for thing in ContentIterator(name='', raw=raw):
                #     stream.extend(thing)
                stream = [thing for thing in ContentIterator(name="", raw=raw)]

            elif content_type in (APPLICATION_MS_EXCEL,):
                raw = await response.read()  # bytes object
                df = pd.read_excel(io.BytesIO(raw))
                stream = json.loads(df.to_json(orient="records"))

            elif content_type in (APPLICATION_OCTET_STREAM, TEXT_CSV):
                raw = await response.read()
                try:
                    df = pd.read_csv(
                        io.StringIO(raw.decode("ISO-8859-1")),
                        sep=None,
                        engine="python",
                        decimal=",",
                    )
                    stream = self._postprocess_df(df, self.context)
                except Exception as why:
                    log.error("Error processing CSV [%s]", why)
                    log.error("content_type: %s", content_type)
                    log.error("response    : %s", response)
                    raise

            elif content_type in (APPLICATION_PYTHON,):
                stream = response.body  # is a internal python object

            elif content_type in (TEXT_HTML,):
                raw_html = await response.text()
                df = self._parse_escaped_json_table(raw_html)
                stream = (
                    self._postprocess_df(df, self.context)
                    if not df.empty
                    else [{"raw_html": raw_html}]
                )

            else:
                for enc in "utf-8", "iso-8859-1":
                    try:
                        stream = await response.text(encoding=enc)
                        assert isinstance(stream, str)
                        # stream = [{'data': block} for block in stream.splitlines()]
                        break
                    except UnicodeDecodeError as why:
                        pass  # use next encoding
                else:
                    stream = response._body
                    log.error("can't decode response: [%s]", stream)
                stream = [{"result": stream}]

        except Exception as why:
            log.error("why: [%s]", why)
            log.error("content_type : %s", content_type)
            log.error("response     : %s", response)
            # log.error("response.text: %s", response)
            log.error("".join(traceback.format_exception(*sys.exc_info())))

            raise
        finally:
            if (elapsed := time.time() - t0) > 10:
                log.warning(
                    "(%s sec) to get response payload!! from [%s]",
                    elapsed,
                    response.real_url,
                )

        return stream, meta

    def _get_connection_key(self, uri: DURI):
        namespace = tf(uri.get("fscheme", DEFAULT_NAMESPACE))
        database = tf(uri.get("host", DEFAULT_DATABASE))
        key = namespace, database
        return key

    async def _get_connection(self, uri: DURI, **kw):
        key = self._get_connection_key(uri)
        connection = self.connection_pool.get(key) or await self._create_connection(uri)
        return connection

    @classmethod
    async def new(cls, url, bot, __klass__=None, **context):
        def score(item):
            "score by counting how many uri values are not None"
            options, m, d = item
            _uri = parse_xuri(url)
            sc = 100 * len(m.groups()) + len(
                [_ for _ in _uri.values() if _ is not None]
            )
            return sc, options

        __klass__ = __klass__ or cls
        blue, factory, args, kw = cls.get_factory(url, __klass__=__klass__, score=score)
        if factory:
            context["uri"] = url
            uri = parse_uri(**context)
            try:
                context.update(kw)
                item = factory(bot=bot, *args, **uri)
                return item
            except Exception as why:  # pragma: nocover
                print(why)
                foo = 1

        # option = cls.locate(url, __klass__=cls, score=score)
        # if option:
        #     uri = parse_uri(url)
        #     factory, info = option
        #     for __key__, (args, kw) in info.items():
        #         try:
        #             context.update(kw)
        #             item = factory(bot=bot, *args, **uri, **context)
        #             return item
        #         except Exception as why:
        #             print(why)

        raise RuntimeError(f"Unable to create a {cls} for url: {url}")

    async def get(self, url, headers=None, params=None, **kw) -> iResponse:
        "Note: Returns is not properly a iResponse, but we mimic the same interface"
        headers = headers or {}
        params = params or {}
        connection = await self._get_connection(url, **headers, **params, **kw)
        return await connection.get(url, headers=headers, params=params, **kw)

    async def _get_schema(self, uri: URI, data=None, **kw):
        # uri = _uri["uri"]
        # kind = _uri[KIND_KEY]
        # schema = self.CACHE.setdefault(uri, {})[kind] = await self._inspect_schema(_uri, data)
        schema = self.CACHE.get(uri)
        if not schema:
            schema = await self._inspect_schema(uri, data, **kw)
            if schema.monotonic_since_key:
                self.CACHE[uri] = schema

        return schema

    async def _inspect_schema(self, uri: URI, data=None, **kw) -> StructShema:
        """performs an introspection to figure-out the schema
        for a particular kind object
        """
        schema = StructShema(
            names=[],
            types=[],
            d_fields={},
            monotonic_since_key="",
            struct={},
        )
        return schema

    def _prepare_body(self, body):
        if isinstance(body, dict):
            form = FormData()
            for key, value in body.items():
                form.add_field(key, value)
            return form
        return body

    async def update_params(self, url, params, context):
        """
        Last chance to modify params based on context for a specific iSession type

        context
        {'crawler__': <SQLiteCrawler>:dummy,
         'bot__': <HTTPBot>:httpbot-0,
         'wave_info__': [],
         'kind__': 'mysensor_stream',
         'func__': 'get_data',
         'meta__': {'foo': 'bar'},
         'prefix__': <Template memory:7c699f532200>,
         'prefix_uri__': 'test://test/mysensor_stream:TubeSnap:mysensor_stream_AINB50945878432336',
         'url__': 'sqlite:///tmp/kraken1727939402.3510203.592664656/db.sqlite',
         'wave_last__': [{'wave': {'id': 'TubeWave:6fwb9uiw3obw0dsijxm4',
                                   'kind__': 'mysensor_stream',
                                   'params__': {},
                                   'prefix_uri__': 'test://test/{{ kind__ }}:{{ id }}',
                                   'wave__': 1727939442812620427},
                          'items': [{'datetime': '2025-03-13T09:10:17Z',
                                     'id': 'TubeSnap:mysensor_stream_AINB50945878432336',
                                     'id__': 'test://test/mysensor_stream:AINB50945878432336',
                                     'value': 25.0,
                                     'wave__': 1727939442812620427}]}],
         'params__': {}}

         # we expect
         call_kw
         {'url': 'sqlite://test/tmp/kraken1727980024.3481097.245022830/db.sqlite',
          'headers': {},
          'params': {'since_key__': 'datetime', 'since_value__': '2025-03-27T20:27:07Z'}}


        """
        # try to convert from WAVE_LAST_KEY -> params that EndPoint
        # will understand

        # 1. get the schema that maps attributes
        # _uri = parse_uri(url, **context)
        # schema = await self._schema(url, **context)
        # monotonic_since_key = schema.monotonic_since_key

        # 2. iterate over waves info
        # TODO: agp: REVIEW if is necessary to do anything here
        # kind = context[KIND_KEY]
        # MAPPER = self.bot.parent.MAPPERS[kind]
        # MAPPER._populate()
        # REVERSE = Mapper._REVERSE.get(kind, {})

        for wave0 in context.get(WAVE_LAST_KEY, []):
            # 3. search these values in the items that belongs to the
            # last wave (from last insertion in the tube)
            # for item in wave0.get("items", []):
            #     # if monotonic_since_key in item:
            #     #     params[MONOTONIC_SINCE_KEY] = monotonic_since_key
            #     #     params[MONOTONIC_SINCE_VALUE] = item[monotonic_since_key]
            #     #     break
            #     if resuming_info := item.get(WAVE_RESUMING_INFO_KEY):
            #         assert (
            #             len(resuming_info) == 1
            #         ), "multiples resuming keys are not alloewd (review storage.put())"
            #         key, value = resuming_info.popitem()
            #         params[MONOTONIC_SINCE_KEY] = key
            #         params[MONOTONIC_SINCE_VALUE] = value
            #         break
            _wave = wave0.get("wave", {})
            if resuming_info := _wave.get(WAVE_RESUMING_INFO_KEY):
                assert (
                    len(resuming_info) == 1
                ), "multiples resuming keys are not alloewd (review storage.put())"
                key, value = resuming_info.popitem()
                params[MONOTONIC_SINCE_KEY] = key
                params[MONOTONIC_SINCE_VALUE] = value
                break
            break

        call_kw = {
            "url": url,
            "headers": self.headers,
        }
        if context.get(METHOD_KEY, "get").lower() in ("post", "put"):
            if body := context.get(BODY_KEY):
                if context.get(BODY_FORMAT) in ("form",):
                    call_kw[self.QUERY_BODY_KEY] = self._prepare_body(body)
                else:
                    call_kw[self.QUERY_BODY_KEY] = body
        else:
            call_kw[self.PARAMS_KEY] = params
        return call_kw


class iActiveSession(iSession, iRunner):  # TODO: agp: used?
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.running = False

    async def start(self):
        pass

    async def stop(self):
        pass

    async def run(self):
        while self.running:
            await asyncio.sleep(1)


if __name__ == "__main__":
    import pickle

    data = pickle.load(open("/tmp/xml.pickle", "rb"))

    stream = []
    for thing in ContentIterator(**data):
        stream.append(thing)
