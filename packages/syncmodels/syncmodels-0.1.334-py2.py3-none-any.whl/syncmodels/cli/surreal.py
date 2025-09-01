import asyncio
import random
import time
import click

from agptools.logs import logger

# from bigplanner.helpers import *
from bigplanner.cli.main import main, CONTEXT_SETTINGS
from bigplanner.cli.config import config

# from bigplanner.definitions import DEFAULT_LANGUAGE, UID_TYPE

# TODO: include any logic from module core
# Examples
# from bigplanner.models import *
# from bigplanner.logic import Tagger
# from syncmodels.storage import Storage

# Import local inventory models
# from bigplanner.models.task import PlannerTask as Item
# from bigplanner.models.task import PlannerTaskRequest as Request
# from bigplanner.models.task import PlannerTaskResponse as Response

from bigplanner.helpers.surreal import SurrealServer
from bigplanner.helpers.faker import fake

from surrealist import Surreal

# ---------------------------------------------------------
# Dynamic Loading Interface / EP Exposure
# ---------------------------------------------------------
TAG = "SURREAL"
DESCRIPTION = "SurrealDB CLI API"
API_ORDER = 10

# ---------------------------------------------------------
# Loggers
# ---------------------------------------------------------

log = logger(__name__)


# ---------------------------------------------------------
# Task CLI port implementation
# ---------------------------------------------------------
@main.group(context_settings=CONTEXT_SETTINGS)
@click.pass_obj
def surreal(env):
    """subcommands for manage tasks for bigplanner"""
    # banner("User", env.__dict__)


submodule = surreal


@submodule.command()
@click.option("--path", default=None)
@click.pass_obj
def start(env, path):
    """Create a new task for bigplanner"""
    # force config loading
    config.callback()

    db_path = env.db_url
    server = SurrealServer(url=db_path, daemon=True)
    server.start()
    log.info(f"Surreal Server running: {server.bind}")
    log.info(f"Press CRTL+C to quit")


@submodule.command()
@click.pass_obj
def stop(env):
    """Find and list existing tasks for bigplanner"""
    # force config loading
    config.callback()

    # config.callback()

    db_path = env.db_url
    server = SurrealServer(url=db_path, daemon=True)
    server.stop()


@submodule.command()
@click.option("--rate", default=2.0)
@click.option("--events", default=10000)
@click.pass_obj
def publish(env, rate, events):
    """Find and list existing tasks for bigplanner"""
    # force config loading
    config.callback()

    db_path = env.db_url
    server = SurrealServer(url=db_path, daemon=True)

    url = f"http://localhost:{server.bind.split(':')[-1]}"

    surreal = Surreal(
        # "http://localhost:9000",
        url,
        namespace="test",
        database="test",
        credentials=("root", "root"),
        use_http=False,
        timeout=10,
        log_level="ERROR",
    )
    print(surreal.is_ready())  # prints True if server up and running on that url
    print(surreal.version())  # prints server version

    with surreal.connect() as db:
        t0 = time.time()
        t2 = 0
        i = 0
        name = fake.name()
        surname = fake.name()
        while events != 0:

            phone = fake.phone_number()
            surname = fake.name()
            name = fake.name()

            data = {
                "name": f"{name}-{i}",
                "surname": f"{surname}-{i}",
                "phone": phone,
            }
            db.create("person", data)
            events -= 1
            i += 1

            if t2 < (t1 := time.time()):
                query = """
                SELECT COUNT() FROM person GROUP ALL;
                """
                res = db.query(query)
                log.info(f"{res.result}")
                # res = db.select("person")
                # elapsed = time.time() - t1
                # log.info(f"elapsed: {elapsed} / {len(res.result)}")

                t2 = t1 + 2
                log.info(f"+ [{i}] {data}")
                speed = i / (t1 - t0)
                log.info(f"speed: {speed} rows / sec")

            if rate > 0:
                time.sleep(rate)

        speed = events / (t1 - t0)
        log.info(f"> Speed: {speed} rows / sec")


@submodule.command()
@click.option("--events", default=1000)
@click.pass_obj
def subscribe(env, events):
    """Find and list existing tasks for bigplanner"""
    # force config loading
    config.callback()

    db_path = env.db_url
    server = SurrealServer(url=db_path, daemon=True)

    url = f"http://localhost:{server.bind.split(':')[-1]}"

    surreal = Surreal(
        # "http://localhost:9000",
        url,
        namespace="test",
        database="test",
        credentials=("root", "root"),
        use_http=False,
        timeout=10,
        log_level="ERROR",
    )
    print(surreal.is_ready())  # prints True if server up and running on that url
    print(surreal.version())  # prints server version

    received = 0

    def call_back(response: dict) -> None:
        nonlocal received
        received += 1
        print(f"[{received}] : {response}")

    with surreal.connect() as db:
        log.info(f"Creating LQ")
        res = db.live("person", callback=call_back)

        log.info(f"Listening events ...")
        while received < events:
            time.sleep(0.5)

        log.info(f"Stop LQ")
        live_id = res.result  # live_id is a LQ id, we need it to kill a query
        db.kill(live_id)  # we kill LQ, no more events to come


@submodule.command()
# @click.option("--events", default=1000)
@click.pass_obj
def count(env):
    """Find and list existing tasks for bigplanner"""
    # force config loading
    config.callback()

    db_path = env.db_url
    server = SurrealServer(url=db_path, daemon=True)

    url = f"http://localhost:{server.bind.split(':')[-1]}"

    surreal = Surreal(
        # "http://localhost:9000",
        url,
        namespace="test",
        database="test",
        credentials=("root", "root"),
        use_http=False,
        timeout=10,
        log_level="ERROR",
    )
    print(surreal.is_ready())  # prints True if server up and running on that url
    print(surreal.version())  # prints server version

    with surreal.connect() as db:
        log.info(f"Selecting LQ")
        query = """
        SELECT COUNT() FROM person GROUP ALL;
        """
        res = db.query(query)
        log.info(f"{res.result}")


@submodule.command()
# @click.option("--events", default=1000)
@click.option("--cycles", default=-1)
@click.pass_obj
def swarmflow1(env, cycles):
    """Find and list existing tasks for bigplanner"""
    # force config loading
    config.callback()

    async def main():

        db_path = env.db_url
        server = SurrealServer(url=db_path, daemon=True)
        url = f"http://localhost:{server.bind.split(':')[-1]}"

        from ..logic.swarmflow import SurrealBroker, SurrealStorage, PlusOne

        broker = SurrealBroker(url)
        storage = SurrealStorage(url)

        uid = "random_plus_one"
        sources = ["clock"]

        particle = PlusOne(uid, sources, broker, storage)
        await particle.run()

    asyncio.run(main())


@submodule.command()
@click.option("--rate", default=2.0)
@click.option("--events", default=-1)
@click.option("--cycles", default=-1)
@click.pass_obj
def clock(env, rate, events, cycles):
    """Find and list existing tasks for bigplanner"""
    config.callback()

    db_path = env.db_url
    server = SurrealServer(url=db_path, daemon=True)

    url = f"http://localhost:{server.bind.split(':')[-1]}"

    surreal = Surreal(
        # "http://localhost:9000",
        url,
        namespace="test",
        database="test",
        credentials=("root", "root"),
        use_http=False,
        timeout=10,
        log_level="ERROR",
    )
    print(surreal.is_ready())  # prints True if server up and running on that url
    print(surreal.version())  # prints server version

    uid = "clock"
    with surreal.connect() as conn:
        while events != 0:
            t0 = time.time()
            data = {
                "_wave": t0,
                #'uid': uid,
                "payload": events,
            }
            conn.create(uid, data)
            log.info(f"{data}")
            time.sleep(rate)
            events -= 1


@submodule.command()
@click.option("--rate", default=2.0)
@click.option("--events", default=-1)
@click.option("--cycles", default=-1)
@click.pass_obj
def temperatures(env, rate, events, cycles):
    """Find and list existing tasks for bigplanner"""
    config.callback()

    db_path = env.db_url
    server = SurrealServer(url=db_path, daemon=True)

    url = f"http://localhost:{server.bind.split(':')[-1]}"

    surreal = Surreal(
        # "http://localhost:9000",
        url,
        namespace="test",
        database="test",
        credentials=("root", "root"),
        use_http=False,
        timeout=10,
        log_level="ERROR",
    )

    uids = "temp_in", "temp_out"
    temp0 = [22, 15]
    inertia = [1, 10]
    temps = [
        [21.0, 17.5],  # t
        [0.1, 0.3],  # t'
        [0, 0],  # t''
    ]

    def step():
        s = 0.1
        for i, zero in enumerate(temp0):
            d = zero - temps[0][i]
            a = d / inertia[i]
            temps[2][i] = a
            temps[1][i] += a * s
            temps[0][i] += temps[1][i] * s

    conn = surreal.connect()

    def publish(idx: int):
        uid = uids[idx]
        t0 = time.time()
        data = {
            "_wave": t0,
            "payload": temps[0][idx],
        }
        conn.create(uid, data)
        # log.info(f"+ [{idx}]: {data}")

    counter = list(inertia)
    while events > 0:
        time.sleep(rate)
        step()
        for i, value in enumerate(counter):
            value -= 1
            if value <= 0 and random.random() < 0.25:
                value = inertia[i]
                publish(i)
                events -= 1
            counter[i] = value


@submodule.command()
# @click.option("--events", default=1000)
@click.option("--cycles", default=-1)
@click.pass_obj
def swarmflow2(env, cycles):
    """Find and list existing tasks for bigplanner"""
    # force config loading
    config.callback()

    async def main():

        db_path = env.db_url
        server = SurrealServer(url=db_path, daemon=True)
        url = f"http://localhost:{server.bind.split(':')[-1]}"

        from ..logic.swarmflow import SurrealBroker, SurrealStorage, TempDiff

        broker = SurrealBroker(url)
        storage = SurrealStorage(url)

        uid = "temp_diff"
        sources = "temp_in", "temp_out"

        particle = TempDiff(uid, sources, broker, storage)
        await particle.run()

    asyncio.run(main())
