"""
SurrealDB helpers
"""

import atexit
import base64
import re
import os
import signal
import sys
import time


from subprocess import Popen, PIPE, TimeoutExpired

from glom import glom, Iter
from agptools.containers import flatten
from agptools.files import fileiter
from agptools.helpers import tf

from ..crud import parse_duri, DEFAULT_DATABASE, DEFAULT_NAMESPACE

from ..storage import Surrealist
from ..definitions import MONOTONIC_KEY

# from ..syncmodels import SyncModel


def to64(x):
    x = f"{x}"
    x = bytes(x, "utf-8")
    x = base64.b64encode(x)
    x = x.decode("utf-8")
    x = x.replace("=", "_")

    # y = from64(x)
    return x


def from64(x):
    x = x.replace("_", "=")
    x = base64.b64decode(x)
    x = x.decode("utf-8")
    return x


# ----------------------------------------------------------
# Surreal Server
# ----------------------------------------------------------
class SurrealServer:
    """A helper to launch a local surrealDB server"""

    REG_VERSION = r"(?P<version>(?P<a>\d+)(\.(?P<b>\d+))?(\.(?P<c>\d+))?)"
    SURREAL_PID = ".surreal.pid"

    def __init__(
        self,
        path,
        bind="0.0.0.0:9000",
        user="root",
        password="root",
        daemon=False,
        version="",
    ):
        self.path = path
        self.bind = bind
        self.user = user
        self.password = password
        self.daemon = daemon
        self.proc = None
        self.pid = None
        self.version = version
        if m := re.match(self.REG_VERSION, version):
            self._version = m.groupdict()
        else:
            self._version = {}

    def find_executable(self):
        shortcuts = [
            "/usr/local/bin",
            "/usr/bin",
            ".",
            "~",
            "/",
        ]
        for top in shortcuts:
            for path, d in fileiter(
                top=top,
                regexp=r"surreal([-_\.\d]+)?$",
                followlinks=False,
            ):
                print(path)

                self.proc = Popen(
                    [path, "--version"],
                    stdout=PIPE,
                    stderr=PIPE,
                )
                try:
                    stdout, stderr = self.proc.communicate(timeout=1.5)
                    if m := re.search(
                        r"SurrealDB.*server\s+" + self.REG_VERSION,
                        stdout.decode("utf-8"),
                        re.I,
                    ):
                        version = m.groupdict()
                        for k in ["a", "b", "c"]:
                            if self._version[k] not in (version[k], None):
                                print(f"exit: {version}")
                                break
                        else:
                            self._version = version
                            return path

                except TimeoutExpired:
                    pass
                self.proc.kill()

    def cmd(self):
        if self.version:
            executable = self.find_executable()
        else:
            executable = "surreal"

        path = os.path.abspath(self.path)

        if self._version.get("a") in ("2",):
            return [
                executable,
                "start",
                "--allow-all",
                "--bind",
                f"{self.bind}",
                "-u",
                f"{self.user}",
                "-p",
                f"{self.password}",
                "--log",
                "debug",
                "--changefeed-gc-interval",
                "600s",
                f"rocksdb://{path}",
            ]
        else:
            return [
                executable,
                "start",
                "--allow-all",
                "--bind",
                f"{self.bind}",
                "-u",
                f"{self.user}",
                "-p",
                f"{self.password}",
                f"file://{path}",
            ]

    def start(self):
        """starts surreal process and register a callback is anything goes wrong"""
        os.makedirs(self.path, exist_ok=True)

        extra = {}
        self.pid = os.getpid()

        def launch():
            # launch server
            self.proc = Popen(
                self.cmd(),
                stdout=PIPE,
                stderr=PIPE,
                **extra,
            )
            # give sometime to communicate with process
            # so server will be ready or we get some error feedback
            try:
                stdout, stderr = self.proc.communicate(timeout=2)
                print(stdout)
                print(stderr)
                # open("/tmp/kk.log", "a").write(f"{stderr}\n")
                return False
                # raise RuntimeError()  # something was wrong

            except TimeoutExpired:
                open(self.SURREAL_PID, "w").write(f"{self.proc.pid}")
                pass

            # print(f"Server pid: {self.pid}")
            if self.daemon:
                # with open(f"{self.url}/pid", "w", encoding="utf-8") as f:
                # f.write(f"{self.pid}")
                pass
            else:
                # stop process when parent process may die
                atexit.register(self.stop)

            return True

        result = False
        if self.daemon:
            try:
                print("forking process ...")
                pid = os.fork()
                self.pid = os.getpid()
                if pid:
                    result = True
                else:
                    print(f"child launch server")
                    result = launch()
                    # detach
                    print(f"child detach fds")
                    sys.stdin.close()
                    sys.stdout.close()
                    sys.stderr.close()
            except OSError as why:
                print(why)
                os._exit(1)
        else:
            result = launch()

        return result

    def stop(self):
        """stops child process and unregister callback"""
        if self.daemon:
            # try to use las pid
            try:
                pid = open(self.SURREAL_PID, "rt").read()
                pid = int(pid)
                print(f"Trying to stop found pid: {pid}")
                os.kill(int(pid), signal.SIGTERM)
                return True
            except ProcessLookupError:
                pass

            except Exception as why:
                pass
            finally:
                os.unlink(self.SURREAL_PID)

            # find process that match the launching arguments
            cmd = "\0".join(self.cmd())
            for root, folders, _ in os.walk("/proc"):
                for pid in folders:
                    if re.match(r"\d+", pid):
                        try:
                            cmdline = open(
                                f"{root}/{pid}/cmdline",
                                "r",
                                encoding="utf-8",
                            ).read()
                            if cmd in cmdline:
                                print(f"Stopping: {pid} : {' '.join(self.cmd())}")
                                os.kill(int(pid), signal.SIGTERM)
                                return True
                        except Exception:
                            pass
            else:
                cmd = " ".join(self.cmd())
                print(f"can't find a surreal server such: '{cmd}'")
                return False
        else:
            self.proc.terminate()
            atexit.unregister(self.stop)
        return True

    @property
    def url(self):
        url = f"http://localhost:{self.bind.split(':')[-1]}"
        return url


# ----------------------------------------------------------
class SurrealStats:
    def __init__(self, url):
        self.url = url
        self.inventory = {}

    def collect(
        self,
        include_ns=[],
        skip_ns=["system"],
    ):
        surreal = Surrealist(self.url)
        for _ in range(20):
            if surreal.is_ready():
                break
            time.sleep(0.1)

        con = surreal.connect()

        inventory = self.inventory
        namespaces = {}
        inventory["ns"] = namespaces

        if include_ns:
            NS = set(include_ns)
        else:
            inventory["root"] = root = con.root_info(structured=True).result
            NS = set(glom(root, "namespaces.*.name"))

        for ns in NS.difference(skip_ns):
            ns_holder = namespaces.setdefault(ns, {})
            con.use(ns, "")
            ns_info = con.ns_info(structured=True).result

            for db in glom(ns_info, "databases.*.name"):
                db_holder = ns_holder.setdefault(db, {})
                r = con.use(ns, db)
                db_info = con.db_info(structured=True).result
                for tb in glom(db_info, "tables.*.name"):
                    tb_holder = db_holder.setdefault(tb, {})
                    tb_info = con.table_info(tb, structured=True).result
                    tb_holder.update(tb_info)
                    tb_holder["count"] = con.count(tb).result

        # stats
        stats = inventory["stats"] = {}
        stats["ns"] = glom(inventory, ("ns", len))
        stats["db"] = glom(inventory, ("ns.*", Iter().flatten().all(), len))
        stats["tb"] = glom(inventory, ("ns.*.*", flatten, Iter().all(), len))
        stats["records"] = sum(glom(inventory, ("ns.*.*.*.count", flatten)))

        return self.inventory

    def samples(self, n=2):
        if not self.inventory:
            self.collect()

        surreal = Surrealist(self.url)
        con = surreal.connect()
        universe = self.inventory["ns"]
        samples = self.inventory["samples"] = {}
        tubes = self.inventory["tubes"] = []
        for ns, databases in universe.items():
            for db, tables in databases.items():
                con.use(ns, db)
                for table in tables:
                    sql = f"SELECT * FROM {table} ORDER BY id DESC LIMIT {n}"
                    res = con.query(sql)

                    tubename = f"{ns}://{db}/{table}"
                    tubes.append(tubename)
                    samples[tubename] = res.result

        tubes.sort()
        return samples

    def check(self, uri):
        _uri = parse_duri(uri)
        namespace = _uri["fscheme"]
        database = _uri["host"]
        table = _uri["table"]

        surreal = Surrealist(self.url, namespace, database)
        for _ in range(20):
            if surreal.is_ready():
                break
            time.sleep(0.1)
        con = surreal.connect()
        con.use(namespace, database)
        res = con.query(f"SELECT * from {table} ORDER BY {MONOTONIC_KEY}")
        for record in res.result:
            foo = 1
        foo = 1
