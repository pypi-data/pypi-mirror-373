import asyncio
from datetime import datetime
import re
import sys
import traceback
from typing import Dict, List
import aiohttp
import requests
from glom import glom

from agptools.helpers import DATE, camel_case_split, match_any, replace, tf
from agptools.logs import logger

from syncmodels.crud import parse_duri
from syncmodels.definitions import (
    ORG_KEY,
    REG_PRIVATE_KEY,
    ID_KEY,
    MONOTONIC_KEY,
    GEOJSON_KEY,
    DATETIME_KEY,
    extract_wave,
)
from syncmodels.http import (
    CONTENT_TYPE,
    USER_AGENT,
    APPLICATION_JSON,
    TEXT_HTML,
    guess_content_type,
)
from syncmodels.helpers.crawler import SortKeyFinder, GeojsonManager
from syncmodels import __version__

log = logger(__file__)


class OrionInjector:
    """
    Inject data into Orion using async http.
    """

    TARGET_URL = "https://orion.example.com:1026"

    MAPPER = None
    EXCLUDE = set(["id", "type"])
    HEADER_KEYS = set(["fiware-service", "fiware-servicepath"])
    FULL_EXCLUDE = EXCLUDE.union(HEADER_KEYS)
    EXCLUDE_ALL = [".*"]

    ALLOWED_KEYS = set([MONOTONIC_KEY])

    # Automatic types conversion
    TYPES = {
        "ts": "timestamp",
        "date": "timestamp",
        "datetime": "timestamp",
        "location": "geo:point",
        "entity_location": "geo:point",
        "geojson": "geo:point",
        # TODO: add Point as "geo:point" as well and some conversion
        str: "string",
        float: "float",
        int: "integer",
        type(None): "null",
    }
    TIMEOUT_INFO = aiohttp.ClientTimeout(
        total=None,
        # total timeout (time consists connection establishment for a new connection
        # or waiting for a free connection from a pool if pool connection limits are exceeded)
        # default value is 5 minutes, set to `None` or `0` for unlimited timeout
        sock_connect=15,
        # Maximal number of seconds for connecting to a peer for a new connection,
        # not given from a pool. See also connect.
        sock_read=15,
        # Maximal number of seconds for reading a portion of data from a peer
    )
    RETRY = 15

    HEADERS = {
        # CONTENT_TYPE: "application/json",
        USER_AGENT: f"OrionInjector/{__version__}",
        # "Accept": "*/*",
        # "Accept-Encoding": "gzip, deflate, br",
        # additional headers for the FIWARE item
        # "fiware-service": "fs_ccoc",
        # "fiware-servicepath": "/beacons/traces",
    }

    # TARGET_URL = "https://orion.ccoc.spec-cibernos.com/v2/entities"
    SERVICE_PATH = (
        ""  # Need to be overridden by the user or use default pattern generation
    )

    ORION_WAVES = {}

    REG_FORBIDDEN_CHARS = re.compile("|".join([f"\\{_}" for _ in """<>()"'=;"""]))

    def __init__(
        self,
        target_url,
        service,
        service_path,
        push_method="update",
        check_orion_wave=True,
        use_sync=True,
    ):
        self.target_url = target_url
        self.service = service
        self.service_path = service_path
        self.use_sync = use_sync

        # resposability-chain for pushing an object into Orion
        self.methods = [
            (
                # 1. try to update an existing object
                [
                    "put",
                    self.target_url
                    # + "/v2/entities/{id}/attrs?options=append,keyValues",
                    + "/v2/entities/{id}/attrs?type={type}",
                    self.FULL_EXCLUDE,
                ],
            ),
            (
                # 2. try to create a non-existing object
                [
                    "post",
                    # self.target_url  + "/v2/entities?options=keyValues",
                    self.target_url + "/v2/entities",
                    [],
                ],
            ),
            (
                # 3. try to delete and create the object again
                [
                    "delete",
                    self.target_url
                    # + "/v2/entities/{id}/attrs?options=append,keyValues",
                    + "/v2/entities/{id}",
                    # + "/v2/entities/{id}?type={type}", # TODO: avoid posibly 409 if id is used in other fs_pathservice
                    # self.EXCLUDE_ALL,
                    self.FULL_EXCLUDE,
                ],
                [
                    "post",
                    # self.target_url  + "/v2/entities?options=keyValues",
                    self.target_url + "/v2/entities",
                    [],
                ],
            ),
        ]
        # TODO: REMOVE debug
        # self.methods.insert(0, self.methods.pop())
        self.push_method = push_method
        self.check_orion_wave = check_orion_wave
        if self.push_method in ("delete",):
            # just use delete + put method
            self.methods[:] = self.methods[2:]

    async def get_orion_wave(self, headers, snap):
        """
        {'Content-Type': 'application/json',
        'User-Agent': 'OrionInjector/0.1.131',
        'fiware-service': None,  # <--------------
        'fiware-servicepath': '/climate/observations'}

        snap
        {'air_dew_point': {'value': 22.1, 'type': 'float'},
         'air_humidity': {'value': 57.0, 'type': 'float'},
         'air_temperature': {'value': 20.9, 'type': 'float'},
         'air_temperature_max': {'value': 21.4, 'type': 'float'},
         'air_temperature_min': {'value': 20.9, 'type': 'float'},
         'altitude': {'value': 760.0, 'type': 'float'},
         'datetime': {'value': '2024-09-16T22:00:00Z', 'type': 'timestamp'},
         'ground_temperature': {'value': 29.3, 'type': 'float'},
         'ground_temperature_20': {'value': None, 'type': 'string'},
         'ground_temperature_5': {'value': None, 'type': 'string'},
         'id': '6032X',
         'insolation': {'value': 26.0, 'type': 'float'},
         'precipitation': {'value': 0.0, 'type': 'float'},
         'precipitation_disdrometer': {'value': None, 'type': 'string'},
         'pressure': {'value': 1012.2, 'type': 'float'},
         'pressure_sea': {'value': 1012.5, 'type': 'float'},
         'snow': {'value': None, 'type': 'string'},
         'ubication': {'value': 'RONDA  IES', 'type': 'string'},
         'visibility': {'value': None, 'type': 'string'},
         'wind_direction': {'value': 93.0, 'type': 'float'},
         'wind_direction_deviation': {'value': 23.0, 'type': 'float'},
         'wind_direction_deviation_ultrasonic': {'value': None, 'type': 'string'},
         'wind_direction_max': {'value': 335.0, 'type': 'float'},
         'wind_direction_max_ultrasonic': {'value': None, 'type': 'string'},
         'wind_direction_ultrasonic': {'value': None, 'type': 'string'},
         'wind_distance': {'value': 187.0, 'type': 'float'},
         'wind_speed': {'value': 1.1, 'type': 'float'},
         'wind_speed_average_ultrasonic': {'value': None, 'type': 'string'},
         'wind_speed_deviation': {'value': 0.8, 'type': 'float'},
         'wind_speed_deviation_ultrasonic': {'value': None, 'type': 'string'},
         'wind_speed_max': {'value': 2.4, 'type': 'float'},
         'wind_speed_max_ultrasonic': {'value': None, 'type': 'string'},
         'type': 'climate.observations',
         'ts': {'type': 'timestamp', 'value': '2024-09-17 12:31:04'}}


         # TODO: WRONG, use tf() + fiware-servicepath ?
         # TODO: or isn't neccessary?
         url: 'https://orion.ccoc.spec-cibernos.com/v2/entities/6032X'


        """
        key = (
            f"{headers['fiware-service']}:{headers['fiware-servicepath']}/{snap['id']}"
        )
        orion_wave = self.ORION_WAVES.get(key, 0)
        if not orion_wave:
            for _ in range(10):
                try:
                    url = self.target_url + "/v2/entities/{id}".format_map(snap)

                    if self.use_sync:
                        response = requests.get(url, headers=headers)
                        if response.status_code < 300:
                            orion_item = response.json()
                        else:
                            log.warning(
                                "It seems that [%s] doesn't exist in Orion (is a new entity for Orion)",
                                url,
                            )
                            break
                    else:
                        async with aiohttp.ClientSession() as session:
                            response = await session.get(url, headers=headers)
                            if response.status < 300:
                                orion_item = await response.json()
                            else:
                                log.warning(
                                    "It seems that [%s] doesn't exitis in Orion (is a new entity for Orion)",
                                    url,
                                )
                                break
                    orion_wave = orion_item.get(MONOTONIC_KEY, {}).get("value")
                    self.ORION_WAVES[key] = orion_wave
                    break  # continue in outher loop
                except aiohttp.ClientError as why:
                    log.error(why)
                    log.error("".join(traceback.format_exception(*sys.exc_info())))
                    asyncio.sleep(1)
                except Exception as why:
                    log.error(why)
                    log.error("".join(traceback.format_exception(*sys.exc_info())))
                    asyncio.sleep(1)

        return orion_wave

    def update_orion_wave(self, headers, snap, orion_wave):
        key = (
            f"{headers['fiware-service']}:{headers['fiware-servicepath']}/{snap['id']}"
        )
        self.ORION_WAVES[key] = orion_wave

    def get_service_path(self):
        "Generate service path from class name, removing common prefixes"
        name = self.service_path or self.__class__.__name__

        for ban in "Orion", "Particle", "Sync", "Tube":
            name = name.replace(ban, "")

        tokens = [""] + camel_case_split(name)
        name = "/".join(tokens).lower()

        # TODO: generalize to use a single class / improve
        # TODO: returns "/injector" right now
        return name

    def _guess_type(self, key, value):
        "Guess type of a key-value pair based on its value"
        type_ = self.TYPES.get(key)
        if type_ is None:
            if isinstance(value, str):
                x = DATE(value)
                if isinstance(x, datetime):
                    return "timestamp"
            # return default value of 'string'
            type_ = self.TYPES.get(value.__class__, "string")
        return type_

    def _to_snap(self, data):
        "check is data is in 'tube' mode and transform into snapshot"
        meta = {}
        snap = {}
        for key, value in data.items():
            if re.match(REG_PRIVATE_KEY, key):
                meta[key] = value
            else:
                snap[key] = value
        if meta:
            fquid = meta.get(ORG_KEY)
            if fquid:
                # _fquid = parse_duri(fquid)
                # # TODO: agp: use a define for "_path"
                # snap[ID_KEY] = _fquid[ID_KEY] or  _fquid["_path"]
                fquid = "_".join(re.findall("\w+", fquid))
                snap[ID_KEY] = fquid

            wave = meta.get(MONOTONIC_KEY) or extract_wave(data)
            if wave:
                # snap["ts"] = DATE(wave)
                snap[MONOTONIC_KEY] = wave
                # TODO: replace any 'sort_key' based on datetime if name doesn't match?
                snap.setdefault(DATETIME_KEY, str(DATE(wave)))

        return meta, snap

    def _to_fiware(self, snap: Dict):
        """Create a json for Orion based on given data
        Note: all attribute but 'id', 'type' must be converted to
        a json format unless keyValues is used with orion
        (including ALLOWED_KEYS).

        This means parameters such 'wave__' can be sent, but as
        any other ordinary parameter.

        TODO: evaluate the option of using keyValues and let wave__
        to live in orion.mongodb, but doesn't be present in platform's
        time serie database (i.e. cratedb, timescale, ...)

        Note: we can sent ANY extra data to Orion such:
        { 'foo':
             {'type': 'string', 'value': None, 'metadata': {}},
        }
        and this will not be present in crateDB if it was not defined
        in its schema manager, so we can extend the objects that Orion
        will store/retrieve for us with no interferences with crateDB

        i.e. to store 'wave__' info

        Note: NEC/crateSink add 'entity_ts' to database (similar concept
        to wave__) but this info is not accesible from Orion, to 3rd
        party injetors can't benefict from this.

        """

        # "type" --> entity_type: i.e. beacons.traces
        data = dict(snap)
        _id = data.get(ID_KEY)
        if not _id:
            fquid = data.get(ORG_KEY) or data["_path"]

            _uri = parse_duri(fquid)
            entity_id = _uri[ID_KEY]

            # entity_id = tf(entity_id)
            # entity_id = esc(entity_id)
            data["id"] = entity_id

        # geojson
        try:
            geojson = data.pop(GEOJSON_KEY)
            if geojson:
                centroid = GeojsonManager.centroid(geojson)
                # Note reverse order: lng, lat --> lat, lng
                geopoint = "{1}, {0}".format(*centroid.coordinates)
                # data["entity_location"] = geopoint
                data["location"] = geopoint
        except KeyError:
            log.warning("geolocation can not be computed for %s", data["id"])

        data.setdefault("type", self.get_service_path().replace("/", "_")[1:])
        # datetime
        # crateSkin stamp a 'ts' based on time received
        # ts = data.get(DATETIME_KEY, data.get(MONOTONIC_KEY))
        # ts = DATE(ts)
        # data["entity_ts"] = ts.timestamp() * 1000

        # check if a validation MAPPER is defined
        # TODO: MAPPER must be located in Particle, not in Injector (generic)
        if self.MAPPER:
            item = self.MAPPER.pydantic(data)
            if item:
                data = item.model_dump(mode="json")
                # include any extra alloed key directly
                for key in self.ALLOWED_KEYS:
                    data[key] = snap[key]
        else:
            # filter any private key when pydantic models are
            # not helping us, so if we need to publish a private
            # key, create a pydantic model that contains the key
            # and this purge will not be executed
            for key, value in list(data.items()):

                # remove any private key, but allowed ones
                if (
                    re.match(REG_PRIVATE_KEY, key) and key not in self.ALLOWED_KEYS
                ):  # or value in (None,):
                    data.pop(key)

                # replace not-allowed values in string
                # Example:
                # response.status
                # 400
                # reason
                # {'error': 'BadRequest', 'description': 'Invalid characters in attribute value'}
                # data['ubication']
                # {'value': 'COIN (AUTOMATICA)', 'type': 'string'}
                # https://fiware-orion.readthedocs.io/en/2.4.0/user/forbidden_characters/index.html
                # https://telefonicaid.github.io/fiware-orion/archive/api/v2/

                if isinstance(value, str):
                    if self.REG_FORBIDDEN_CHARS.search(value):
                        _value = self.REG_FORBIDDEN_CHARS.sub("", value)
                        data[key] = replace(_value, lower=False)
                        log.warning(
                            "[%s] replacing illegal characters in %s: %s -> %s",
                            data["id"],
                            key,
                            value,
                            data[key],
                        )

                        foo = 1

        # get headers
        headers = {
            **self.HEADERS,
            "fiware-service": data.pop("fiware-service", self.service),
            "fiware-servicepath": data.pop("fiware-servicepath", self.service_path),
        }

        assert headers["fiware-service"], "can't be Empty"
        assert headers["fiware-servicepath"], "can't be Empty"
        # try to translate all regular existing fields
        for key in set(data.keys()).difference(self.FULL_EXCLUDE):
            value = data[key]

            if isinstance(value, dict) and not set(value.keys()).difference(
                ["value", "type"]
            ):
                pass
            else:
                data[key] = {
                    "value": value,
                    "type": self._guess_type(key, value),
                }

        for key, value in list(data.items()):

            # remove any private key, but allowed ones
            if (
                re.match(REG_PRIVATE_KEY, key) and key not in self.ALLOWED_KEYS
            ):  # or value in (None,):
                data.pop(key)

            # replace not-allowed values in string
            # Example:
            # response.status
            # 400
            # reason
            # {'error': 'BadRequest', 'description': 'Invalid characters in attribute value'}
            # data['ubication']
            # {'value': 'COIN (AUTOMATICA)', 'type': 'string'}
            # https://fiware-orion.readthedocs.io/en/2.4.0/user/forbidden_characters/index.html
            # https://telefonicaid.github.io/fiware-orion/archive/api/v2/
            if isinstance(value, str):

                if self.REG_FORBIDDEN_CHARS.search(value):
                    data[key] = self.REG_FORBIDDEN_CHARS.sub("", value)
                    log.warning(
                        "[%s] replacing illegal characters in %s: %s -> %s",
                        data["id"],
                        key,
                        value,
                        data[key],
                    )
                    foo = 1
                else:
                    data[key] = value = replace(value)

        return headers, data

    async def _push(self, session, data, headers):
        """
        # Update an entity
        # https://fiware-orion.readthedocs.io/en/1.10.0/user/update_action_types/index.html#update

        201: POST
        204: POST

        400: POST
        # 'type': 'beacons/trace'
        {'error': 'BadRequest', 'description': 'Invalid characters in entity type'}


        400: PATCH
        {'error': 'BadRequest', 'description': 'entity id specified in payload'}
        {'error': 'BadRequest', 'description': 'entity type specified in payload'}
        {'error': 'BadRequest', 'description': 'attribute must be a JSON object, unless keyValues option is used'}
        {'error': 'BadRequest', 'description': 'empty payload'}

        400: DELETE
        {'error': 'BadRequest', 'description': 'Orion accepts no payload for GET/DELETE requests. HTTP header Content-Type is thus forbidden'}


        404: PATCH
        {'error': 'NotFound',  'description': 'The requested entity has not been found. Check type and id'}
        {'error': 'BadRequest','description': 'Service not found. Check your URL as probably it is wrong.'}

        {'orionError': {'code': '400',
                'reasonPhrase': 'Bad Request',
                'details': 'Service not found. Check your URL as probably it '
                           'is wrong.'}}

        422: POST
        {'error': 'Unprocessable', 'description': 'Already Exists'}
        {'error': 'Unprocessable', 'description': 'one or more of the attributes in the request do not exist: ['plate ]'}

        Example of headers

        headers = {
            "Content-Type": "application/json",
            "fiware-service": "fs_ccoc",
            "fiware-servicepath": "/test",
        }
        """
        response = None
        for operations in self.methods:
            results = []
            for name, url, exclude in operations:
                method = getattr(session, name)
                url = url.format_map(data)  # TODO: jinja2 ?

                if name in ("delete",):
                    call_kw = {
                        "url": url,
                        "headers": {**headers},
                    }
                else:
                    _data = {
                        k: v for k, v in data.items() if not match_any(k, *exclude)
                    }
                    call_kw = {
                        "url": url,
                        "headers": {
                            **headers,
                            **{
                                CONTENT_TYPE: "application/json",
                            },
                        },
                        "json": _data,
                    }
                for _ in range(0, 15):
                    try:
                        # TODO: check why async is not working right now!
                        if self.use_sync:
                            func = getattr(requests, name)
                            response = func(**call_kw)

                            if response.status_code < 300:
                                results.append(response)
                            if int(response.headers.get("Content-Length", 0)) > 0:
                                if content_type := guess_content_type(response.headers):
                                    if content_type in APPLICATION_JSON:
                                        reason = response.json()
                                    else:
                                        reason = response.text

                                if reason and reason.get("error") in ("NotFound",):
                                    log.debug(
                                        "Orion [%s] [%s]: %s, trying next method",
                                        name,
                                        response.status_code,
                                        reason,
                                    )
                                else:
                                    log.error(
                                        "Orion [%s]: %s", response.status_code, reason
                                    )

                        else:
                            async with method(**call_kw) as response:
                                if response.status < 300:
                                    results.append(response)
                                if response.headers.get("Content-Length"):
                                    if content_type := guess_content_type(
                                        response.headers
                                    ):
                                        if content_type in APPLICATION_JSON:
                                            reason = await response.json()
                                        else:
                                            reason = await response.text()

                                    if reason and reason.get("error") in ("NotFound",):
                                        log.debug(
                                            "Orion [%s] [%s]: %s, trying next method",
                                            name,
                                            response.status,
                                            reason,
                                        )
                                    else:
                                        log.error(
                                            "Orion [%s]: %s", response.status, reason
                                        )

                        break
                    except Exception as why:
                        log.error(why)
                        await asyncio.sleep(2)
                        foo = 1
            if results:
                # let response be returned
                break
            else:
                response = None

        else:
            log.error(
                "Orion: Unable to push object using [%s] methods: %s",
                list(self.methods),
                data,
            )

        return response

    def _push_sync(self, session, data, headers):
        """
        # Update an entity
        # https://fiware-orion.readthedocs.io/en/1.10.0/user/update_action_types/index.html#update

        201: POST
        204: POST

        400: POST
        # 'type': 'beacons/trace'
        {'error': 'BadRequest', 'description': 'Invalid characters in entity type'}


        400: PATCH
        {'error': 'BadRequest', 'description': 'entity id specified in payload'}
        {'error': 'BadRequest', 'description': 'entity type specified in payload'}
        {'error': 'BadRequest', 'description': 'attribute must be a JSON object, unless keyValues option is used'}
        {'error': 'BadRequest', 'description': 'empty payload'}

        400: DELETE
        {'error': 'BadRequest', 'description': 'Orion accepts no payload for GET/DELETE requests. HTTP header Content-Type is thus forbidden'}


        404: PATCH
        {'error': 'NotFound',  'description': 'The requested entity has not been found. Check type and id'}
        {'error': 'BadRequest','description': 'Service not found. Check your URL as probably it is wrong.'}

        {'orionError': {'code': '400',
                'reasonPhrase': 'Bad Request',
                'details': 'Service not found. Check your URL as probably it '
                           'is wrong.'}}

        422: POST
        {'error': 'Unprocessable', 'description': 'Already Exists'}
        {'error': 'Unprocessable', 'description': 'one or more of the attributes in the request do not exist: ['plate ]'}

        Example of headers

        headers = {
            "Content-Type": "application/json",
            "fiware-service": "fs_ccoc",
            "fiware-servicepath": "/test",
        }
        """
        for operations in self.methods:
            results = []
            for method, url, exclude in operations:
                method = getattr(session, method)
                url = url.format_map(data)
                _data = {k: v for k, v in data.items() if k not in exclude}

                response = method(url, json=_data, headers=headers)
                response.status = response.status_code  # hack meanwhile

                if response.status < 300:
                    results.append(response)
                elif response.headers.get("Content-Length"):
                    reason = response.json()
                    log.info("Orion [%s]: %s", response.status, reason)

            if results:
                break
        return response

    async def _compute(self, edge, ekeys):
        """
        # TODO: looks like is a batch insertion! <-----

        Example
        {
        "actionType": "APPEND",
        "entities": [
            {
                "id": "TL1",
                "type": "totem.views",
                "ts": {
                    "value": "2024-03-06 09:43:11",
                    "type": "timestamp"
                },
                "conteo": {
                    "value": 9,
                    "type": "integer"
                },
                "component": {
                    "value": "C11 - TOTEMS",
                    "type": "string"
                },
                "place": {
                    "value": "LUCENTUM",
                    "type": "string"
                },
                "geojson": {
                    "type": "geo:point",
                    "value": "38.365156979723906,-0.438225677848391"
                }
            }
        ]
        }
        """
        assert (
            len(ekeys) == 1
        ), f"{self.__class__.__name__} must have just 1 input tube "
        "it just syncronize, doesn't compute anything and the advance "
        "of the mark is associate to a single value, not multiples at once "
        "just in case something fails, only affect to a single synchronization."

        # returning None means that no data is really needed for synchronization
        # just advance the TubeSync wave mark
        for tube_name in ekeys:
            data = edge[tube_name]
            return await self.push(data)

    async def push(self, data, **context):
        """try to push data to Orion"""
        response = None

        # sort_keys = SortKeyFinder.find_sort_key([data])

        # TODO: MAPPER must appply here or applied in Particle before sent data
        meta, snap = self._to_snap(data)
        headers, snap = self._to_fiware(snap)

        swarm_wave = data.get(MONOTONIC_KEY) or extract_wave(data)
        if self.check_orion_wave:
            orion_wave = await self.get_orion_wave(headers, snap)
            if orion_wave:

                # convert them to datetime to avoid nanosecods round errors
                # orion_wave: 1726715149029566720
                # swarm_wave: 1726715149029566739
                # -19 nanosecods !
                # maybe due an aritmetic precission with Orion
                # orion_wave, swarm_wave = DATE(orion_wave), DATE(swarm_wave)
                # (orion_wave // 1000) == (swarm_wave // 1000)

                if orion_wave >= swarm_wave:
                    log.debug(
                        """Orion has newer or equal wave than the data that we're trying to push, SKIPPING!
                        orion_wave: [%s]
                        swarm_wave: [%s]
                        (other process are updating the same entities?)
                        """,
                        orion_wave,
                        swarm_wave,
                    )
                    return

        # check 1st time if there is sync problem with orion
        # due SwarmTube's external causes (3rd party situations)
        # update with context
        for key in self.HEADER_KEYS.intersection(context).difference(headers):
            headers[key] = context[key]
        if snap:
            for tries in range(0, self.RETRY):
                try:
                    async with aiohttp.ClientSession() as session:
                        response = await self._push(session, snap, headers)
                        self.update_orion_wave(headers, snap, swarm_wave)
                        return response

                except aiohttp.ClientError as why:
                    log.error(why)
                    log.error("".join(traceback.format_exception(*sys.exc_info())))
                log.warning("retry: %s: %s", tries, data)
                await asyncio.sleep(2.5)
            return response
