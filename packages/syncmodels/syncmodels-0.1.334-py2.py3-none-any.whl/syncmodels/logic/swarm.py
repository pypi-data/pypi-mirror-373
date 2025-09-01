import asyncio
import random
import time
import pickle
import hashlib
from collections import deque
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional, Union

from agptools.helpers import build_uri, DATE, parse_uri
from agptools.logs import logger
from agptools.containers import flatten, json_compatible

from syncmodels.definitions import (
    ID_KEY,
    ORG_KEY,
    DATETIME_KEY,
    ORDER_KEY,
    WHERE_KEY,
    DIRECTION_ASC,
    DIRECTION_KEY,
    LIMIT_KEY,
    KIND_KEY,
    FUNC_KEY,
    MAPPER_KEY,
    DOMESTIC_KEY,
    FQUID_KEY,
    DATETIME_LAST_KEY,
)
from syncmodels.crud import parse_duri
from syncmodels.model import Enum
from syncmodels.storage import Storage
from syncmodels.crawler import iAsyncCrawler, iBot

from ..model.swarm import SwarmTask

# from syncmodels.logic.swarm import SwarmTask

# from ..definitions import URI_BOT_PRESENCE, URI_BQUEUE_CRAWLER

# ---------------------------------------------------------
# Loggers
# ---------------------------------------------------------


log = logger(__name__)


SWARM_REGISTER = "swarm_register"
SWARM_TASKS = "swarm_tasks"

URI_BOT_PRESENCE = "swarm://swarm/presence"
URI_BOT_QUEUE = "swarm://swarm/queue"


class SwarmActionsEnum(Enum):
    """Price Kinds
    TBD
    """

    # weather_warnings = "weather_warnings"
    NOP = {
        MAPPER_KEY: None,
        KIND_KEY: "nop",
        FUNC_KEY: "nop",
        DOMESTIC_KEY: True,
    }
    SWARM_REGISTER = {
        MAPPER_KEY: None,
        KIND_KEY: SWARM_REGISTER,
        FUNC_KEY: SWARM_REGISTER,
        DOMESTIC_KEY: True,
    }
    SWARM_TASKS = {
        MAPPER_KEY: None,
        KIND_KEY: SWARM_TASKS,
        FUNC_KEY: SWARM_TASKS,
        DOMESTIC_KEY: True,
    }


class SwarmOrchestrator(object):
    """TBD"""

    PRESENCE_URI = URI_BOT_PRESENCE
    QUEUE_URI = URI_BOT_QUEUE
    DEAD = 60
    PAUSE = 2
    DELAY = 3600 * 2

    def __init__(
        self,
        storage: Storage,
        *args,
        **kw,
    ):
        self.uri = kw.get("uri") or self.PRESENCE_URI
        if self.uri:
            self._uri = parse_duri(self.uri)
        self.uid = kw.get("uid")

        try:
            super().__init__(*args, **kw)
        except TypeError:
            pass

        self.storage = storage
        self.next_presence = 0

    async def presence(self):
        # get some unassigned tasks
        storage = self.storage
        now = datetime.utcnow()
        presence = {
            # ID_KEY: f"{self.uid}",
            ORG_KEY: self.uri,
            DATETIME_KEY: str(now),
        }
        idx = 0
        uri = self.PRESENCE_URI
        while not self.uid:
            # uri is not set, we find the next available name
            fquid = f"{uri}:{idx}"
            if not await storage.get(fquid):
                probe = now + timedelta(microseconds=random.randint(0, 10**6))
                presence[DATETIME_KEY] = str(probe)
                res = await storage.update(uri, id=idx, **presence)

                await asyncio.sleep(1 + random.random())
                current = await storage.get(fquid)
                if current[DATETIME_KEY] == presence[DATETIME_KEY]:
                    # I win, so I'll take the ownership
                    self._uri["id"] = self.uid = str(idx)
                    self.uri = build_uri(**self._uri)
            idx += 1
            await asyncio.sleep(random.random() * 0.25)

        # save presence in storage
        now = datetime.utcnow()
        presence[DATETIME_KEY] = str(now)
        uri = f"{uri}:{self._uri['id']}"
        res = await storage.put(uri, **presence)
        log.info("Swarm presence: [%s]", self.uri)
        return res

    async def purge(self):
        # get some unassigned tasks
        uri = self.PRESENCE_URI
        storage = self.storage
        now = datetime.utcnow()
        # basename = self._uri["basename"]
        # uri is not set, so we're going to reuse and old one
        # when = now - timedelta(seconds=self.DEAD)
        dead = str(now - 5 * timedelta(seconds=self.DEAD))

        params = {
            WHERE_KEY: f"{DATETIME_KEY} < '{dead}'",
            # ORDER_KEY: DATETIME_KEY,
            # DIRECTION_KEY: DIRECTION_ASC,
            # LIMIT_KEY: len(bots),
        }
        # pattern = f"{basename}:(?P<num>.*)$"
        res = await storage.query(uri, **params)
        for bot in res:
            uid = bot.get(ID_KEY)
            _uri = parse_duri(uid)
            fquid = f"{uri}:{_uri['id']}"
            await storage.delete(fquid)

    async def assign(self):
        # get some unassigned tasks
        storage = self.storage
        presence = await storage.query(self.PRESENCE_URI)
        running = {bot[ID_KEY].split(":")[-1] for bot in presence}
        uri = self.QUEUE_URI
        uid = self._uri["id"]

        now = datetime.utcnow()
        # warn = str(now - 2 * timedelta(seconds=self.DEAD))
        when = str(now + 2 * timedelta(seconds=self.DEAD))
        free = str(now + 7 * timedelta(seconds=self.DEAD))

        N = len(running)
        f = 1 / (max(N, 1))

        params = {
            WHERE_KEY: f"{DATETIME_KEY} < '{free}' AND bot != '{uid}' ",
            ORDER_KEY: DATETIME_KEY,
            DIRECTION_KEY: DIRECTION_ASC,
            # LIMIT_KEY: 3 * N,
        }

        now = str(datetime.utcnow())
        stream = await storage.query(uri, **params)
        for _task in stream:
            bot_uid = _task.get("bot")
            bot_date = _task.get(DATETIME_KEY, "")
            r = random.random()
            if r < f:  # only with this probability (1/N bots)
                if (True or bot_date > when) or bot_uid not in running:
                    # 1st check:
                    # free bar, anyone can steal other's tasks.
                    # that way when there are a lot of task assiged
                    # to a bots that is running for a long time
                    # new bots can release pressure to the old ones

                    # 2nd check
                    # when is near to execution, we try not to
                    # steal tasks that has been assigned but
                    # the assigned bot is dead
                    _task["bot"] = self._uri["id"]
                    _task[DATETIME_KEY] = now  # TODO: when to execute the task
                    res = await storage.update(uri, **_task)
                    foo = 1
            # await asyncio.sleep(r)
        foo = 1

    async def get_tasks(self, limit=1):
        # get some unassigned tasks
        storage = self.storage
        uri = self.QUEUE_URI
        uid = self._uri["id"]

        # now = datetime.utcnow()
        params = {
            # WHERE_KEY: f"{DATETIME_KEY} < '{now}' AND bot = '{uid}' ",
            # WHERE_KEY: f"bot = '{uid}' ",
            WHERE_KEY: f"bot = '{uid}'",
            ORDER_KEY: DATETIME_KEY,
            DIRECTION_KEY: DIRECTION_ASC,
            LIMIT_KEY: limit,
        }
        stream = await storage.query(uri, **params)
        for task in stream:
            bot_uid = task.get("bot")
            assert bot_uid == uid
            # simulate task execution
            # ...

            # move the task a little bit forward to avoid "echos"
            when = DATE(task[DATETIME_KEY]) or datetime.now(tz=timezone.utc)
            when += timedelta(seconds=900)
            task[DATETIME_LAST_KEY] = task[DATETIME_KEY]
            task[DATETIME_KEY] = f"{when}"
            # task["bot"] = "wip"

            res = await storage.update(uri, task)
            foo = 1

        return stream

    async def search_tasks(self, where):
        storage = self.storage
        uri = self.QUEUE_URI

        stream = await storage.query(uri, **where)
        return stream

    async def reset_tasks(self, where, patch):
        storage = self.storage
        uri = self.QUEUE_URI

        stream = await self.search_tasks(where)
        for task in stream:
            task.update(patch)
            res = await storage.update(uri, task)

    async def reschedule(self, task, delay=None, framed=True):
        delay = delay or self.DELAY
        storage = self.storage
        uri = self.QUEUE_URI
        # uid = self._uri["id"]

        uid = task["id"].split(":")[-1]
        # 'queue:00a401e322d3a3b43e8687cf5d4c10bd'
        uri = f"{self.QUEUE_URI}:{uid}"

        if current := await storage.get(uri):
            pass
        else:
            current = task

        if framed:
            # add a tiny time delay, for debugging so queue
            # can be sorted in surreal
            t1 = time.time()
            t0 = (t1 // delay) * delay
            t2 = t0 + delay
            t2 += (t1 - t0) / delay * 300  #  [0..1]*5 min
            when = DATE(t2)
        else:
            when = DATE(current[DATETIME_KEY])
            when += timedelta(seconds=delay)

        current[DATETIME_KEY] = f"{when}"
        current["bot"] = None  # free to be assigned

        res = await storage.update(uri, current)
        return res

    async def create_task(self, task, **extra):
        storage = self.storage

        if uri := task.get(ID_KEY):
            _uri = parse_duri(uri)
            if not _uri.get(ID_KEY):
                blueprint = json_compatible(task)
                blueprint = pickle.dumps(blueprint)
                blueprint = hashlib.md5(blueprint).hexdigest()
                task[ID_KEY] = blueprint
                # task["fquid"] = fquid = f"{self.QUEUE_URI}:{blueprint}"

        check = SwarmTask(**task)
        task.update(check.model_dump())
        new = {
            **task,
            **extra,
        }
        new = json_compatible(new)

        fquid = task.get(ID_KEY) or extra.get(FQUID_KEY) or f"{self.QUEUE_URI}"
        res = await storage.put(fquid, new)
        return res

    async def update_task(self, task, **extra):
        storage = self.storage
        if uid := task.get(ID_KEY):
            _uri = parse_duri(uid)
            if _uri.get("id"):
                uri = uid
            else:
                uri = self.QUEUE_URI
                uid = uid.split(":")[-1]
                uri = f"{self.QUEUE_URI}:{uid}"
        else:
            uri = self.QUEUE_URI
            # uid = self._uri["id"]
        new = {
            **task,
            **extra,
        }
        res = await storage.update(uri, new)
        return res

    async def delete_task(self, task, **extra):
        storage = self.storage
        if uid := task.get(ID_KEY):
            _uri = parse_duri(uid)
            if _id := _uri.get("id"):
                uri = f"{self.QUEUE_URI}:{_id}"
            else:
                uid = uid.split(":")[-1]
                uri = f"{self.QUEUE_URI}:{uid}"
        else:
            uri = self.QUEUE_URI
            # uid = self._uri["id"]
        res = await storage.delete(uri)
        return res

    async def by_id(self, uid):
        storage = self.storage
        _uri = parse_duri(uid)
        if _uri.get(ID_KEY):
            uri = uid
        else:
            uri = self.QUEUE_URI
            uid = uid.split(":")[-1]
            uri = f"{self.QUEUE_URI}:{uid}"

        task = await storage.get(uri)
        return task

    async def domestics(self):
        await self.presence()
        await self.purge()
        await self.assign()

        t0 = time.time()
        r = random.random()
        self.next_presence = t0 + self.DEAD - self.PAUSE - r

    async def idle(self):
        "default implementation when loop has nothing to do"
        t0 = time.time()
        r = random.random()
        if t0 >= self.next_presence or r < 0.15:
            await self.domestics()


class SwarmBot(iBot):
    MAX_QUEUE_TASK = 10
    ALLOWED_TYPES = set()
    RESCHEDULE = 3600 * 4

    ALLOWED_KIND = set(
        [
            SWARM_REGISTER,
            SWARM_TASKS,
        ]
    )

    def __init__(self, *args, **kw):
        kw.setdefault("stop_when_empty", False)
        super().__init__(*args, **kw)
        # self.headless = self.context.get("headless", True)
        self.operational = {}

    def can_handle(self, task):
        "return if the function can be handled by this iBot"
        if super().can_handle(task):
            return True
        return task.get(KIND_KEY) in self.ALLOWED_KIND

    async def nop(self, **task):
        self.add_task(task, expire=5)
        print("nop")
        foo = 1

    def update_operational(self, name):
        result = {}
        info = self.operational.get(name, {})
        for key, params in info.items():
            current, limit, factor = params
            if factor > 1.0:
                current = min(limit, current * factor)
            else:
                current = max(limit, current * factor)

            params[0] = current
            result[key] = current

        return result

    async def swarm_register(self, **task):
        """
        Give extra chances to execute swarm.idle()

        TODO: can be ignored if SwarmCrawler.idle()
        is executed with regularity.
        """
        # log.info("swarm_register!:")
        swarm = self.parent.swarm
        await swarm.idle()
        self.add_task(task, expire=swarm.DEAD / 2)

    async def _swarm_get_tasks(self):
        swarm = self.parent.swarm
        universe = {}
        limit = 2 - (self.input_queue.qsize() - 2)  # 2 domestic tasks
        limit = min(4, limit)
        # NOTE: when a task is got, it's has been moved a little bit
        # NOTE: forward in order to be appart from the current edge
        # NOTE: only when the task is added, then is moved again and
        # NOTE: fully rescheduled
        for _task in await swarm.get_tasks(limit=limit):
            if url := _task.get("url"):
                if host := parse_duri(url).get("host"):
                    universe.setdefault(host, []).append(_task)
                    continue
            await swarm.delete_task(_task)
        return universe

    async def swarm_tasks(self, **task):

        # check how may task are pending
        swarm = self.parent.swarm
        if (n := self.parent.remain_tasks()) < self.MAX_QUEUE_TASK:
            if swarm.uid:
                # collect a bunch of tasks
                universe = await self._swarm_get_tasks()

                # order to try to delay the largets period
                # to the same host in 2 consecutive request

                def milk(universe):
                    keys = deque(universe.keys())
                    while keys:
                        key = keys[0]
                        if candidates := universe.get(key, []):
                            item = candidates.pop(0)
                            yield item
                            keys.rotate()
                        else:
                            keys.remove(key)

                for _task in milk(universe):
                    log.info(" + Task: [%s]", _task)

                    new_task = self._prepare_task(**_task)
                    self.add_task(new_task)
                    # reschedule the task in the future just in case
                    # something will fail
                    await swarm.reschedule(_task, delay=self.RESCHEDULE)
            else:
                log.info("Waiting for a Swarm ID ...")
        else:
            log.info(
                "[%s] queue has [%s] task, ignoring add more tasks by now", swarm.uri, n
            )
        self.add_task(task, expire=2)
        foo = 1

    def _prepare_task(self, **_task):
        # new_task = {
        #     # **MyTaskKindEnum.PRICES.value,
        #     ORG_URL: _task["url"],
        #     TASK_KEY: _task,
        #     # PREFIX_KEY: "pricemon://crawler/historical:{{ id }}",
        # }
        if payload := _task.get("payload"):
            _task.update(payload)

        # _task[FORCED_URL] = _task.get("url")
        return _task


class SwarmCrawler(iAsyncCrawler):
    "Base of all BrowerCrawlers"

    SESSIONS = set(
        flatten(
            [
                iAsyncCrawler.SESSIONS,
            ]
        )
    )
    ORCHESTRATOR_FACTORY = SwarmOrchestrator
    ACTIONS: List[Enum] = [SwarmActionsEnum]

    def __init__(
        self,
        *args,
        **kw,
    ):
        super().__init__(
            *args,
            **kw,
        )
        self.swarm: SwarmOrchestrator = None

    def default_bootstrap(self):
        """
        Provide the default actions for this crawler
        """
        yield from super().default_bootstrap()

        for enum in flatten(self.ACTIONS):
            task = {
                **enum.value,
            }
            if task.get(DOMESTIC_KEY):
                yield task

    async def start(self):
        "start runner"
        for wstorage in self._storages():
            storage = wstorage.storage
            self.swarm = self.ORCHESTRATOR_FACTORY(uri=self.uri, storage=storage)
            log.info("Swarm using storage: [%s]", storage.url)
            break
        else:
            log.error("crawler has not storage?")
        await super().start()

    async def idle(self):
        "default implementation when loop has nothing to do"
        await self.swarm.idle()
        await super().idle()
