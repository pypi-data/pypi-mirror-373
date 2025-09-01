import asyncio
import queue
import random
import sys
import time
import traceback


from agptools.progress import Progress
from agptools.logs import logger
from syncmodels.crud import parse_duri

from .definitions import CALLABLE_KEY, FUNC_KEY
from .timequeue import TimeQueue
from .model.model import IntEnum

log = logger(__name__)

monotonic = time.time


class FailurePolicy(IntEnum):
    STOP = 0
    RAISE = 1
    RETRY = 5


class iRunner:
    "The minimal interface for something that runs autonomously"

    STATS_DISPATCH = "dispatch"
    STATS_IDLE = "idle"

    FAILURE_POLICY = FailurePolicy.RAISE

    def __init__(
        self,
        *,
        uri="",
        name="",
        bootstrap=None,
        output_queue=None,
        stop_when_empty=True,
        **kw,
    ):
        self.uri = uri
        if uri:
            self._uri = parse_duri(uri)
            self.uid = self._uri["id"]
        else:
            # self.uid = f"uid-{random.randint(1, 1000)}"
            self._uri = {}
            self.uid = ""

        name = name or self.uid
        self.name = name
        self.bootstrap = bootstrap
        self.progress = Progress(label=self.name or str(self))
        self.running = False
        self.input_queue = TimeQueue()
        self.output_queue = output_queue
        self.t0 = 0
        self.t1 = 0
        self.nice = 600
        self.clock = 0

        self.hooks = []
        self.stop_when_empty = stop_when_empty

        self._wip = []

        self.stats = {}
        self._last_announce = 0

    def __str__(self):  # pragma: nocover
        return f"<{self.__class__.__name__}>:{self.name}"

    def __repr__(self):  # pragma: nocover
        return str(self)

    async def run(self) -> bool:
        "main loop of a single `fiber` in pool"
        # TODO: replace as "run"
        log.debug(">> [%s] entering run()", self.name)

        # Create a worker pool with a specified number of 'fibers'
        self.t0 = time.time()
        self.t1 = self.t0 + self.nice

        self.running = True
        await self.start()
        while self.running:
            try:
                _, task = await self.get_task()
                if task is None:
                    if self.stop_when_empty:
                        break  # Break the loop
                    await self.idle()
                else:
                    self._wip.append(1)
                    await self.dispatch(task)
                self._stats(self.STATS_DISPATCH)
            except asyncio.exceptions.TimeoutError:
                await self.idle()
                self._stats(self.STATS_IDLE)
            except Exception as why:  # pragma: nocover
                log.error(why)
                msg = "".join(traceback.format_exception(*sys.exc_info()))
                log.error(msg)
                field = str(why)
                self._stats(field)
                if self.FAILURE_POLICY == FailurePolicy.STOP:
                    self.running = False
                elif self.FAILURE_POLICY == FailurePolicy.RAISE:
                    raise RuntimeError(msg)
                else:
                    # add same task to be executed later on
                    # using a scheduled queue, not just a simple queue
                    self.input_queue.push(task, monotonic() + self.FAILURE_POLICY.value)
                    await self.idle()
            finally:
                self._wip and self._wip.pop()

        await self.stop()
        log.debug("<< [%s] exit run()", self.name)

    def _stats(self, field: str, value=1):
        "update the stats"
        if field in self.stats:
            self.stats[field] += value
        else:
            self.stats[field] = value

    def add_task(self, task, expire=0):
        "add a new pending task to be executed by this iAgent"
        self.input_queue.push(task, expire)
        return True

    def remain_tasks(self):
        "compute how many pending tasks still remains"
        return len(self._wip) + self.input_queue.qsize()

    async def get_task(self, timeout=2) -> dict:
        "get the next task or raise a timeout exception"
        queue = self.input_queue
        while True:
            delay = queue.deadline()
            if delay is None:
                await asyncio.sleep(timeout)
                if not queue.deadline():
                    raise asyncio.exceptions.TimeoutError(
                        f"timeout: {timeout} in empty queue"
                    )
            elif delay <= 0:
                return queue.pop()
            else:
                await asyncio.sleep(min(delay, timeout))

    async def dispatch(self, task):
        "task executor to be implemented by sub-classes"
        func = task.pop(CALLABLE_KEY, None)
        if not func:
            func = getattr(self, task[FUNC_KEY])  # let fail with AttributeError
        await func(**task)
        self.clock += 1
        for hook in self.hooks:
            await hook(**task)

    async def idle(self):
        "default implementation when loop has nothing to do"
        asyncio.sleep(0.1)

    async def start(self):
        "start runner"
        await self._create_resources()

    async def stop(self):
        "stop runner"
        await self._stop_resources()

    async def _create_resources(self):
        "create/start the agent's resources needed before starting"

    async def _stop_resources(self):
        "stop/release the agent's resources on exit"
