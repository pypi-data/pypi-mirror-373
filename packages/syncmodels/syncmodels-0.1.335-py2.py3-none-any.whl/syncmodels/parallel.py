import asyncio
import aiohttp
import os
import re
import random
import sys
import traceback
from typing import List, Dict, Any, Callable
import yaml
from pprint import pformat

from asyncio.queues import Queue

# ---------------------------------------------------------
# concurrent data gathering
import concurrent.futures
import threading
import multiprocessing
import queue
import time

# ---------------------------------------------------------


from .helpers import expandpath
from .syncmodels import SyncModel, COPY

# ---------------------------------------------------------
# Loggers
# ---------------------------------------------------------
from agptools.containers import walk, myassign, rebuild, SEP, list_of
from agptools.logs import logger
from agptools.progress import Progress

log = logger(__name__)


def nop(*args, **kw):
    pass


async def anop(*args, **kw):
    yield None


class Parallel:
    def __init__(self, num_threads=3, dispatch=None):
        self.num_threads = num_threads
        self.task_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self._wip = []
        self.show_stats = True
        self.dispatch = dispatch or nop

        self.workers = []
        self.pool = None

    def bootstrap(self):
        self.pool = multiprocessing.Pool(processes=self.num_threads)

    def _create_executor_pool(self):
        if True:
            self.workers = [
                threading.Thread(target=self.worker) for _ in range(self.num_threads)
            ]

            for worker in self.workers:
                worker.start()

        else:
            self.worker = multiprocessing.Pool(processes=self.num_threads)

    def _stop_executor_pool(self):
        # Add sentinel values to signal worker threads to exit
        for _ in range(self.num_threads):
            self.task_queue.put(None)

        # Wait for all worker threads to complete
        for worker in self.workers:
            worker.join()

    def run(self):
        self.t0 = time.time()
        self.elapsed = 0.0

        # Create a thread pool with a specified number of threads
        self._create_executor_pool()
        # Start worker threads

        # wait until all work is done
        shows = 0
        while remain := self.remain_tasks():
            try:
                result = self.result_queue.get(timeout=1)
                self.dispatch(*result)
            except queue.Empty as why:
                foo = 1

            shows -= 1
            if self.show_stats and shows <= 0:
                log.warning(f"remain tasks: {remain} : {self.num_threads} threads")
                shows = 50
            # time.sleep(0.25)
            self.elapsed = time.time() - self.t0

        self._stop_executor_pool()

    def add_task(self, func, *args, **kw):
        self.task_queue.put_nowait((func, args, kw))

    def remain_tasks(self):
        return (
            len(self._wip) + len(self.task_queue.queue) + len(self.result_queue.queue)
        )

    def worker(self):
        while True:
            try:
                # Get a task from the queue
                task = self.task_queue.get(block=True, timeout=1)
                if task is None:
                    break  # Break the loop
                self._wip.append(1)
                func, args, kwargs = task
                # print(f">> Processing task: {func}")
                result = func(*args, **kwargs)
                item = task, result
                self.result_queue.put(item)
                self._wip.pop()
                # print(f"<< Processing task: {func}")
            except queue.Empty:
                pass


class AsyncParallel:
    def __init__(self, num_threads=3, dispatch=None):
        self.num_threads = num_threads
        self.task_queue = asyncio.queues.Queue()
        self.result_queue = asyncio.queues.Queue()
        self._wip = []
        self.show_stats = True
        self.dispatch = dispatch or anop

        self.workers = []  # tasks
        # self.pool = None
        self.loop = None

    def bootstrap(self):
        "Provide the initial tasks to ignite the process"
        # self.pool = multiprocessing.Pool(processes=self.num_threads)

    async def _create_executor_pool(self):

        self.workers = [
            self.loop.create_task(self.worker(), name=f"worker-{n}")
            for n in range(self.num_threads)
        ]

    async def _stop_executor_pool(self):
        # Add sentinel values to signal worker threads to exit
        for _ in range(self.num_threads):
            self.task_queue.put_nowait(None)

        # Wait for all worker threads to complete
        # for worker in self.workers:
        # worker.join()

    async def run(self):
        self.t0 = time.time()
        self.elapsed = 0.0
        self.loop = asyncio.get_running_loop()

        # Create a worker pool with a specified number of 'fibers'
        await self._create_executor_pool()

        # wait until all work is done
        last = 0
        while remain := self.remain_tasks():
            try:
                # result = await asyncio.wait_for(self.result_queue.get(), timeout=2)
                result = await self.result_queue.get()
                await self.dispatch(*result)
            except queue.Empty as why:
                foo = 1
            except asyncio.exceptions.TimeoutError as why:
                foo = 1

            t1 = time.time()
            self.elapsed = t1 - self.t0
            # print("foo")
            if self.show_stats and t1 - last > 10:
                log.info(f"remain tasks: {remain} : {self.num_threads} fibers")
                last = t1
            # time.sleep(0.25)

        await self._stop_executor_pool()

    def add_task(self, func, *args, **kw):
        self.task_queue.put_nowait((func, args, kw))

    def remain_tasks(self):
        return len(self._wip) + self.task_queue.qsize() + self.result_queue.qsize()

    async def worker(self):
        while True:
            try:
                # Get a task from the queue
                while remaining := self.remain_tasks() < 1000:
                    print(f"Pause worker due too much remainin task: {remaining}")
                    await asyncio.sleep(1)
                    foo = 1
                task = await asyncio.wait_for(self.task_queue.get(), timeout=2)
                if task is None:
                    break  # Break the loop
                self._wip.append(1)
                func, args, kwargs = task
                # print(f">> Processing task: {args}: {kwargs}")
                result = await func(*args, **kwargs)
                item = task, result
                self.result_queue.put_nowait(item)
                self._wip.pop()
                # print(f"<< Processing task: {func}")
            except queue.Empty:
                foo = 1
            except asyncio.exceptions.TimeoutError as why:
                foo = 1
            except Exception as why:
                log.error(why)
                log.error("".join(traceback.format_exception(*sys.exc_info())))
                foo = 1
                print(tb)
                foo = 1
