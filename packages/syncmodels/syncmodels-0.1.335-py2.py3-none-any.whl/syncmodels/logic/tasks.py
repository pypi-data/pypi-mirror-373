import asyncio

# import re
import os
import sys
import time
import re
import traceback
import random
import pickle
import yaml

from datetime import datetime, timezone
from typing import List, Optional, Dict

from pydantic import BaseModel, Field, field_validator

from agptools.logs import logger
from agptools.containers import soft, overlap, filter_dict, filter_list
from agptools.loaders import ModuleLoader

# from syncmodels.crawler import iAsyncCrawler
from syncmodels.definitions import (
    ORG_KEY,
    WAVE_INFO_KEY,
    WHERE_KEY,
    KIND_KEY,
    UID_TYPE,
)

# from syncmodels.mapper import Mapper, I, DATE, FLOAT
# from syncmodels.model import BaseModel, Datetime
# from syncmodels.session.http import HTTPSession
# from syncmodels.crud import DEFAULT_DATABASE

from syncmodels.storage import SurrealistStorage, WaveStorage
from syncmodels.syncmodels import SyncModel
from syncmodels.wave import TUBE_SNAPSHOT
from syncmodels.crawler import iAsyncCrawler
from syncmodels.model import Datetime

# from kraken.helpers import *
# from kraken.cli.main import main, CONTEXT_SETTINGS
# from kraken.cli.config import config


class Boostrap(BaseModel):
    kind__: str = Field(
        None,
        # alias=KIND_KEY,
        description="kind used for crawler mapper",
        examples=[
            "parking/status",
            "/departures/traffictype/",
            "vuelos-llegada",
            "raw_waterconsumption",
            "HOTEL_OCCUPATION",
        ],
    )
    method__: str = Field(
        "get",
        # alias=METHOD_KEY,
        description="Session method to be used (default: get)",
        examples=[
            "get",
            "post",
        ],
    )
    prefix__: str | None = Field(
        None,
        # alias=PREFIX_KEY,
        description="Prefix used for storing the data, default None and use crawler built-in DEFAULT_PREFIX",
        examples=[
            None,
            "transport://adif/trains:{{ id }}",
            f"centesimal://centesimal/{{{KIND_KEY}}}" ":{{ id }}",
            "stats://ine/dti/flows/{COD}:{Fecha}",
        ],
    )
    path__: Optional[str] = Field(
        None,
        # alias=PATH_KEY,
        description="path for calling EndPoint",
        examples=[
            "/ftp/CPTEXP.TXT",
        ],
    )
    limit_value__: Optional[int] = Field(
        None,
        # alias=PATH_KEY,
        description="limit of number of item on every cycle",
        examples=[
            1000,
        ],
    )
    grace__: Optional[int] = Field(
        24 * 3600,
        # alias=PATH_KEY,
        description="grace period to protect same data duplication based on wave (seconds)",
        examples=[
            86400,
        ],
    )


class Task(BaseModel):
    """A Kraken Task model
    TODO: update in coockiecutter template
    """

    id: Optional[UID_TYPE] = Field(
        # "101_item",
        description="Item unique identifier",
        examples=[
            "e81265d0ac1a5a4fb32fa2ab5a5bd930067b9153",
            "fdfe1b7f64bbdb380661c60ed4bff1ae7692a1f1",
            "c123576d726ab9973390e562d28c0f619fada79b",
            "65aaa94497ce4474dd526c35e26dfcbe1b787fb0",
            "17ccd7ba28b3b920217c215a18099d610de135de",
        ],
    )
    name: Optional[str] | None = Field(
        # "kraken no name",
        description="kraken name",
        examples=[
            "nice-item",
        ],
    )
    description: Optional[str] | None = Field(
        # "a nice kraken object",
        description="kraken human more descriptive name",
        examples=[
            "A Nice Item",
        ],
    )

    unit: Optional[str] = Field(
        description="name/regexp to identify unit component",
        examples=[
            "smassa",
            "aena",
            "ine",
            "adif",
        ],
    )
    crawler: Optional[str] = Field(
        ".",
        description="name/regexp to identify Crawler Factory",
        examples=[
            "smassa",
            "aena",
            "ine",
            "adif",
        ],
    )
    storage_url: Optional[str] | None = Field(
        None,
        description="url for storage server. Using None by default will use config file vaule",
        examples=[
            None,
            "ws://localhost:12080",
        ],
    )
    fibers: Optional[int | None] = Field(
        1,
        description="num of fibers for crawler",
        examples=[
            1,
            2,
        ],
    )
    restart: Optional[int | None] = Field(
        60,
        description="seconds to wait to restart the crawling process",
        examples=[
            60,
        ],
    )
    cycles: Optional[int | None] = Field(
        None,
        description="how many cycles the crawler must execute until task if finished (-1 means infinite)",
        examples=[-1, 1, 5, 10],
    )
    cache_timeout: Optional[int | None] = Field(
        60,
        description="period in which same url+params requests will be ignored if it have been executed before",
        examples=[60, 600],
    )
    bootstrap: List[Boostrap] | None = Field(
        None,
        description="a list of Bootstrap items to be used in crawler. Ommiting this parameter will use cralwer default_bootstrap() method",
    )
    # time
    updated: Optional[Datetime] = Field(
        None,
        description="Task Update",
        # pattern=r"\d+\-\d+\-\d+T\d+:\d+:\d+",  # is already a datetime
    )
    paused: Optional[bool] = Field(
        False,
        description="determine if a task must be paused or not",
        examples=[False, True],
    )

    @field_validator("id")
    def convert_id(cls, value):
        if not isinstance(value, UID_TYPE):
            value = UID_TYPE(value)
        # TODO: make some validations here
        return value


from ..definitions import (
    TASK_THING,
)


# ---------------------------------------------------------
# Loggers
# ---------------------------------------------------------


log = logger(__name__)

# ---------------------------------------------------------
# launch
# ---------------------------------------------------------


def launch(
    task: Dict,
    config_path: str | None = None,
    pattern: List = None,
):
    # for config_path in env.config_files:
    #     if os.access(config_path, os.F_OK):
    #         break
    # else:
    #     config_path = None
    #
    # setup the syncmodel that holds all data
    # url = env.surreal_url

    if config_path:
        cfg = yaml.load(open(config_path, "t", encoding="utf-8"), Loader=yaml.Loader)
    else:
        cfg = {}

    if isinstance(task, Dict):
        dtask = task
    else:
        dtask = task.model_dump()

    soft(
        dtask,
        {
            "task_filters": pattern,
        },
    )
    url = dtask.get("storage_url") or cfg.get("storage_url")
    surreal = SurrealistStorage(url)
    storage = WaveStorage(storage=surreal)
    syncmodel = SyncModel(
        config_path=config_path,
        storage=[
            storage,
            # yaml_wave,
        ],
    )

    loader = ModuleLoader("unit")  # could be a module or a folder name
    # available = loader.available_modules()

    # loader = ModuleLoader(CRAWLER_UNITS_LOCATION)
    # available = loader.available_modules()

    crawler = dtask.get("crawler") or [".*"]
    wanted = loader.available_modules([dtask.get("unit") or ".*"])
    if len(wanted) > 1:
        log.warning(
            "Too many (%s) units found using: `%s` pattern",
            len(wanted),
            dtask.get("unit"),
        )
        for name in wanted:
            log.info(" - %s", name)
        log.info(
            "try to use a closer filter to get the template unit, i.e. `%s`",
            name,
        )
    else:
        for i, mod in enumerate(loader.load_modules(wanted)):
            # make introspection of the module
            if not (inventory := getattr(mod, "inventory")):
                log.error("Unit: %s has not `inventory` !!")
                log.error("Review unit and provide the required initialization entry")
                continue

            try:

                log.debug("module: [%s] inventory", mod.inventory)
                _crawlers = mod.inventory[iAsyncCrawler.__name__]
                log.info("found: [%s] crawler factories", len(_crawlers))
                if _crawlers:
                    for _, (name, factory) in enumerate(_crawlers.items()):
                        log.info("- name: [%s] : factory: [%s]", name, factory)
                        if loader.match_any_regexp(factory.__name__, [crawler], re.I):
                            mod.default_setup()
                            # instance = factory(
                            #     config_path=config_path,
                            #     syncmodel=syncmodel,
                            #     restart=task.restart,
                            #     cycles=task.cycles,
                            #     cache_timeout=task.cache_timeout,
                            # )
                            instance = factory(
                                config_path=config_path,
                                syncmodel=syncmodel,
                                **dtask,
                                # restart=task.restart,
                                # cycles=task.cycles,
                                # cache_timeout=task.cache_timeout,
                            )
                            # add bootstrap from task of let use the
                            # default_bootstrap() (instance.bootstrap=None)
                            if dtask.get("bootstrap"):
                                # check that bootstrap looks complete based
                                # on default_bootstrap
                                default_bootstrap = list(instance.default_bootstrap())

                                # default_bootstrap can have multiple options with a
                                # combination  of kind__, path__, etc  so I try to get
                                # the best match and complement the missing information
                                def best_boot(boot):
                                    keys = set(boot)
                                    best = {}
                                    for candidate in default_bootstrap:
                                        if candidate.get(KIND_KEY) != boot.get(
                                            KIND_KEY
                                        ):
                                            # can merge only with same keys
                                            continue
                                        if len(keys.intersection(candidate)) > len(
                                            best
                                        ):
                                            best = candidate
                                    return best

                                bootstrap = []
                                for boot in dtask["bootstrap"]:
                                    best = best_boot(boot)
                                    # complement missing data from bootstrap
                                    overlap(boot, best)
                                    bootstrap.append(boot)
                                instance.bootstrap = bootstrap

                            # asyncio.run(instance.run())
                            yield instance

                else:
                    log.error("No crawlers match [`%s`] name", crawler)
                    log.error("Candidates:")
                    for idx, (name, factory) in enumerate(_crawlers.items()):
                        log.error("[%s] %s : %s", idx, name, factory)

                    log.error(
                        "You must set a name/regexp that match any of these names"
                    )

            except Exception as why:
                log.error("%s", why)
                log.error("Ignoring this module!!")

    foo = 1


# ---------------------------------------------------------
# run_tasks
# ---------------------------------------------------------


async def update_task(task):

    APP_NS = os.getenv("APP_NS", "myapp_ns")
    APP_DB = os.getenv("APP_DB", "myapp_db")

    cfg = dict(env.__dict__)
    try:
        url = cfg["surreal_url"]
        config_path = cfg.get("config_path", "config.yaml")
        surreal = SurrealistStorage(url)
        storage = WaveStorage(storage=surreal)
        syncmodel = SyncModel(
            config_path=config_path,
            storage=[
                storage,
            ],
        )

        org_id = task.id
        fqid = f"{APP_NS}://{APP_DB}/{TASK_THING}:{org_id}"
        task.id = fqid
        task.updated = datetime.now(tz=timezone.utc)

        dtask = task.model_dump()

        wave_info = {
            WAVE_INFO_KEY: ["bootstrap"],
            **dtask,
        }
        result = await syncmodel.put(task, **wave_info)
        if result:
            query = f"{APP_NS}://{APP_DB}/{TUBE_SNAPSHOT}"
            params = {
                ORG_KEY: fqid,
            }
            result = await syncmodel.query(query, **params)
            for fqid, data in result.items():
                stored_task = Task(**data)
                # returns the task saved in storage as confirmation
                return stored_task

            msg = f"Saved task: {org_id} can't be retrieved back for checking"
        else:
            msg = f"Task {org_id} hasn't been saved in storage"
        # return failed response
        raise RuntimeError(msg)

    except Exception as e:
        log.error(e)
        msg = "".join(traceback.format_exception(*sys.exc_info()))
        log.error(msg)
        raise RuntimeError(msg) from e


def run_tasks(
    cycles=-1,
    restart=60,
    active_units=None,
    active_crawlers=None,
    ignore_units=None,
    ignore_crawlers=None,
    **context,
):
    APP_NS = context.get("APP_NS", "kraken")
    APP_DB = context.get("APP_DB", "kraken")

    url = context.get("surreal_url")
    config_path = context.get("config_path")
    surreal = SurrealistStorage(url)
    storage = WaveStorage(storage=surreal)
    ctx = dict(storage=storage, dead=restart)

    async def iteration_main():

        syncmodel = SyncModel(
            config_path=config_path,
            storage=[
                storage,
            ],
        )

        query = f"{APP_NS}://{APP_DB}/{TASK_THING}"

        # params = request.params
        # if params:
        #     params = params.model_dump()
        # else:
        #     params = {
        #         MONOTONIC_KEY: 0,
        #     }

        context.setdefault("storage_url", context.get("surreal_url"))

        params = {
            # key: value
            # for key, value in params.items()
            # if value not in (None, "")
            WHERE_KEY: "crawler",  # object has crawler keyword defined
        }

        task_definition = await syncmodel.query(query, **params)
        last_task_definition = pickle.loads(pickle.dumps(task_definition))

        timeout = 10
        tasks = set()
        instances = {}
        launched_bootstraps = {}
        loop = asyncio.get_running_loop()
        t0 = loop.time()
        delay = 0
        restart = False

        for _, (fquid, data) in enumerate(task_definition.items()):
            data = overlap(data, context)
            task = Task(**data)
            _task = task.model_dump()
            # add any extra special parameter that is not in the Task Model definition
            extra = {k: v for k, v in data.items() if re.match(r".*__$", k)}
            _task.update(extra)

            if _paused := _task.get("paused"):
                log.info("Ignoring Task")
                continue

            exclude = list(
                filter_list(
                    universe=[_task.get("unit", "")], patterns=ignore_units or [r"(?!)"]
                )
            )
            if exclude:
                log.info("Ignoring task: %s due ignore_units=%s", _task, ignore_units)
                continue

            exclude = list(
                filter_list(
                    universe=[_task.get("crawler", "")],
                    patterns=ignore_crawlers or [r"(?!)"],
                )
            )
            if exclude:
                log.info(
                    "Ignoring task: %s due ignore_crawlers=%s", _task, ignore_crawlers
                )
                continue

            for _ in filter_dict(universe=[_task], patterns=active_units or (".",)):
                # check that there is not any redundant task
                samples = launched_bootstraps.setdefault(task.crawler, [])
                arguments = _task["bootstrap"]
                if arguments in samples:
                    log.error(
                        "[%s] A similar task has already launched",
                        task.crawler,
                    )
                    log.error("%s", arguments)
                    continue
                else:
                    samples.append(arguments)

                # ('[{"kind__": "parking/status", "method__": "get",
                # "prefix__": null, "path__": null}]'))

                # replace with the needed data only
                task_definition[fquid] = _task
                runners = list(launch(_task, pattern=active_crawlers or (".",)))
                # TODO: update bootstrap definition to the storage
                # TODO: so user can specify jus the crawler without
                # TODO: any data, but the default bootstrap parameters
                # TODO: will be saved back, so user can see current
                # TODO: bootstrap implementation
                delay += 1
                instances[fquid] = [runners, t0 + delay * timeout]

        while tasks or instances:
            # start all waiting instances
            now = loop.time()
            for fquid, info in list(instances.items()):
                if info[-1] < now:
                    crawlers = info[0]
                    if not crawlers:
                        log.warning("Unit found, but no crawler match criteria")
                    for crawler in info[0]:
                        coro = crawler.run()
                        task = loop.create_task(coro, name=fquid)
                        tasks.add(task)
                        log.info("Add a coro for task: %s", info)
                    info[-1] = float("inf")
                    instances.pop(fquid)

            # wait task to finish for a short period
            if not (tasks or instances):
                break

            foo = 2

            if not tasks:
                assert (
                    instances
                ), "we must be waiting for an instance that must be launched soon"
                log.info(
                    "no task to wait, but there's [%s] tasks that will be launched soon",
                    len(instances),
                )
                # timeout = 1 # TODO: hack for faster debugging
                await asyncio.sleep(timeout)
                continue
            done, tasks = await asyncio.wait(tasks, timeout=timeout)

            #  check if any task has been modified
            new_task_definition = await syncmodel.query(query, **params)

            # TODO: agp: restart only the affected tasks
            if last_task_definition != new_task_definition:
                log.info("Task definitions has change, restarting crawlers")
                for task in tasks:
                    frame = task.get_coro().cr_frame.f_locals
                    crawler = frame.get("self")
                    if isinstance(crawler, iAsyncCrawler):
                        # request crawler to stop inmediately
                        # crawler.running = False
                        # request crawler to stop on the next cycle
                        crawler.cycles = 0
                    else:
                        log.error("self [%s] isn't instance of iAsyncCrawler")
                restart = True
                tasks.clear()

            if done:
                # some stats
                log.info("[%s] tasks are still running", len(tasks))
                # evaluate what to do with done tasks
                for task in done:
                    fquid = task.get_name()
                    data = task_definition[fquid]
                    log.info(
                        "task: [%s] is finished: result: [%s]",
                        fquid,
                        task.result(),
                    )
                    for key, value in data.items():
                        log.info(
                            " - %s: %s",
                            key,
                            value,
                        )

                    data["cycles"] -= 1
                    if (
                        not restart and data["cycles"] != 0
                    ):  # TODO: set restarting POLICY
                        when = max(data["restart"], 60)
                        # a little shifted randomness that will spread the crawler load
                        when *= 0.975 + random.random() / 10
                        log.info(
                            "Daemon restart [%s] in [%s] secs: [%s]",
                            data["unit"],
                            when,
                            fquid,
                        )
                        instances[fquid][-1] = loop.time() + when
                    else:
                        # crawler is not restarted
                        instances.pop(fquid, None)

        foo = 1

    restart = max(restart, 15)
    while cycles != 0:

        asyncio.run(iteration_main())
        cycles -= 1
        if cycles:
            log.info(
                "waiting: [%s] secs before the next crawling iteration",
                restart,
            )
            time.sleep(restart)
