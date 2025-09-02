import random
from typing import Dict, List

from agptools.helpers import build_uri, parse_xuri, tf
from agptools.containers import json_compatible
from agptools.logs import logger

from .definitions import (
    UID,
    WAVE,
    JSON,
    MONOTONIC_KEY,
    URI,
    ORDER_KEY,
    DIRECTION_KEY,
    DIRECTION_DESC,
    PREFIX_KEY,
    WAVE_INFO_KEY,
    KIND_KEY,
    PREFIX_URL,
    ID_KEY,
)
from .crud import iStorage, parse_duri

# TODO: check https://pypi.org/project/speedict/
# TODO: check https://github.com/speedb-io/python-speedb
# TODO: check https://github.com/grantjenks/python-diskcache/tree/master
# TODO: check https://github.com/unum-cloud/ustore

#  system
TUBE_NS = "system"
TUBE_DB = "swarmtube"
TUBE_META = "TubeMeta"
SYSTEM_NS = set([TUBE_NS])

# other
TUBE_WAVE = "TubeWave"
TUBE_SYNC = "TubeSync"
TUBE_SNAPSHOT = "TubeSnap"
TUBE_TABLES = set([TUBE_META, TUBE_WAVE, TUBE_SYNC, TUBE_SNAPSHOT])


log = logger(__name__)


def get_tube_name(klass):
    if isinstance(klass, str):
        tube_name = klass.split(":")[-1]
    else:
        tube_name = f"{klass.__module__.replace('.', '_')}_{klass.__name__}"
    return tube_name


class iWaves:
    """Swarm Flows / Waves storage.
    Base implementation is for Surreal, but can be
    overridden by sub-classing
    """

    MODE_SNAPSHOT = "snap"
    MODE_TUBE = "tube"

    MAX_HARD_CACHE = 120
    MAX_SOFT_CACHE = 100

    TUBE_SYNC_WAVES = {}
    #
    #     AVOID_KEYS = (
    #         PREFIX_KEY,
    #         MONOTONIC_KEY,
    #         CRAWLER_KEY,
    #         BOT_KEY,
    #     )

    def __init__(self, storage: iStorage, *args, **kw):
        super().__init__(*args, **kw)
        self.cache = {}
        self.storage = storage

    async def last_wave(self, task: Dict) -> WAVE:
        """Returns all objects that belongs
        to the last wave within the prefix: ns/db
        """
        prefix = task[PREFIX_KEY]
        prefix = prefix.render(task)
        _prefix = parse_duri(prefix)
        namespace = _prefix["fscheme"]
        database = _prefix["host"]
        # use tr(target) instead letting storage use a PK
        # and adding a column with id (more space)
        # thing = tf(target)
        # query = (
        #     f'{namespace}://{database}/{TUBE_WAVE}?id={TUBE_WAVE}:{thing}'
        # )
        query = f"{namespace}://{database}/{TUBE_WAVE}"

        wave_keys = set(task.get(WAVE_INFO_KEY, []))
        wave_keys.update(
            [
                KIND_KEY,
            ]
        )
        # wave_keys.update([KIND_KEY, PREFIX_URL]) #TODO: fix and include PREFIX_URL

        wave = {k: task[k] for k in wave_keys}
        params = {
            ORDER_KEY: MONOTONIC_KEY,
            DIRECTION_KEY: DIRECTION_DESC,
        }

        found_waves = await self.storage.query(query, **wave, **params)
        if len(found_waves) > 1:
            log.error(
                "[%s] has (%s) records for [%s], but must have only 0..1 waves",
                TUBE_WAVE,
                len(found_waves),
                wave,
            )
            log.error("delete and fixing table ...")
            for record in found_waves[1:]:
                uri = record[ID_KEY].split(":")[1]
                uri = f"{query}:{uri}"
                await self.storage.delete(uri)

            found_waves = found_waves[:1]

        # return all objects that belongs to this *last* wave
        waves = []
        assert len(found_waves) <= 1, "multiple wave for same crawler fource?"
        for w in found_waves:
            query = f"{namespace}://{database}/{TUBE_SNAPSHOT}"
            wave = {MONOTONIC_KEY: w[MONOTONIC_KEY]}
            items = await self.storage.query(query, **wave)
            waves.append({"wave": w, "items": items})

        return waves

    async def update_sync_wave(
        self, prefix: URI, sources: List[URI], target: URI, waves: List[WAVE]
    ):
        """Update the synchronization wave
        of some sources for a particular target
        """
        _prefix = parse_duri(prefix)
        namespace = _prefix["fscheme"]
        database = _prefix["host"]

        results = []
        # query = f'{namespace}://{database}/{TUBE_WAVE}'
        query = f"{namespace}://{database}/{TUBE_SYNC}"
        for source in set(sources).intersection(waves):
            # query = f'{TUBE_NS}://{TUBE_DB}/{TUBE_SYNC}?source={source}&target={target}'
            # Note that record hasn't `id`, we need to find if the
            # record already exist or is new one
            params = {
                "source": source,
                "target": target,
            }
            _results = await self.storage.query(query, **params)
            if _results:
                record = _results[0]
                if record[MONOTONIC_KEY] > waves[source]:
                    log.error("Wave info goes back in time ?")
                    log.error("sources: [%s]", sources)
                    log.error("target: [%s]", target)
                    log.error("waves: [%s]", waves)
                    log.error("record: [%s]", record)
                    continue
                record[MONOTONIC_KEY] = waves[source]
                result = await self.storage.update(query, record)
            else:
                # use params as record for efficiency
                params[MONOTONIC_KEY] = waves[source]
                result = await self.storage.put(query, params)

            results.append(result)
        return all(results)

    async def last_waves(
        self, prefix: URI, sources: List[URI], target: URI
    ) -> Dict[URI, WAVE]:
        "return the last wave of an object"
        _prefix = parse_duri(prefix)
        namespace = _prefix["fscheme"]
        database = _prefix["host"]

        # _uri = parse_duri(target)
        # just for clarity
        # namespace = _uri["fscheme"]
        # database = _uri["host"]

        waves = {}
        query = f"{namespace}://{database}/{TUBE_SYNC}"
        for source in sources:
            # query = f'{namespace}://{database}/{TUBE_SYNC}?source={source}&target={target}'
            params = {
                "source": source,
                "target": target,
            }
            result = await self.storage.query(query, **params)
            if result:
                waves[source] = result[0][MONOTONIC_KEY]
            else:
                waves[source] = 0
        return waves

    def _has_change(self, uri: UID, **data: JSON):
        # TODO: ask to TUBE_WAVE instead (direct check by id)
        _uri = parse_duri(uri)
        if data:
            root = self.cache
            for key in _uri["_path"].split("/"):
                root = root.setdefault(key, {})
            current = root.get(uid := _uri["id"])
            if current != data:
                # check cache size
                if len(root) > self.MAX_HARD_CACHE:
                    keys = list(root.keys())
                    while (l := len(keys)) > self.MAX_SOFT_CACHE:
                        k = random.randint(0, l - 1)
                        root.pop(keys.pop(k))

                root[uid] = data
                return True
        return False

    async def start(self):
        "any action related to start storage operations"

    async def stop(self):
        "any action related to stop storage operations"

    async def update_meta(self, tube, meta, merge=True):
        """Update the tube metadata.
        If merge is True, meta-data will me merge
        If merge is False, meta-data will be replace
        """

    async def find_meta(self, tube, meta):
        """Find tubes that match the specified meta"""
        return []

    async def save(self, nice=False, wait=False):
        return await self.storage.save(nice=nice, wait=wait)
