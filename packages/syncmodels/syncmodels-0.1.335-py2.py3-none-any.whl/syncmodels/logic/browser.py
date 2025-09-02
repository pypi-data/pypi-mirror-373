import asyncio
import re
import math
from random import uniform
import time
from weakref import WeakKeyDictionary
import sys
import traceback
import random
import os
import requests
import yaml
from collections import Counter
from pprint import pformat
from datetime import datetime

import json

from lxml import etree

import nltk
from nltk.corpus import words
from nltk.stem import WordNetLemmatizer
from jinja2 import Template
import lzma as xz
from playwright import async_api as plw


from agptools.containers import flatten, overlap
from agptools.logs import logger
from agptools.helpers import (
    generate_blueprint,
    parse_uri,
    build_uri,
    parse_uri,
    replace,
    tf,
)
from agptools.files import fileiter

from syncmodels.http import CONTENT_TYPE, APPLICATION_PYTHON
from syncmodels.requests import iResponse
from syncmodels.crud import parse_duri

from ..definitions import TASK_KEY, KIND_KEY, ORG_URL, DURI, ID_KEY, VOL_DATA
from ..session import iSession
from ..crawler import iBot
from ..crawler import MetaExtractPlugin, PutPlugin, SetURIPlugin, SortPlugin

from .swarm import SwarmBot, SwarmCrawler, SWARM_REGISTER, SWARM_TASKS
from .analyzer import XPathAnalyzer

# ---------------------------------------------------------
# Loggers
# ---------------------------------------------------------
log = logger(__name__)


class Magic:

    CACHE = WeakKeyDictionary()
    PAUSE = 0.1

    def __init__(self, target, root=None, last=None):
        self._target_ = target
        self._root_ = root or target
        self._last__ = last

    def __getattr__(self, name):
        _next_ = getattr(self._target_, name)
        if isinstance(
            _next_,
            (
                int,
                float,
                str,
                bytes,
                dict,
                list,
                tuple,
            ),
        ):
            return _next_
        return self.__class__(_next_, self._root_)

    async def __call__(self, *args, **kw):
        return await self._target_(*args, **kw)

    async def unique(self, name, validator=None, timeout=100000):
        saved = self.CACHE.setdefault(self, {})
        t0 = time.time()
        t2 = t0 + timeout / 1000
        pause = self.PAUSE
        tries = 0
        while (t1 := time.time()) < t2:
            tries += 1
            pause *= 1.5

            try:
                new = self.__getattr__(name)
                if validator:
                    if m := re.search(validator, str(new)):
                        new = new, m.groupdict()
                    else:
                        new = new, None
                        print(f"[{tries}] pause: {pause}")
                        await asyncio.sleep(pause)
                        continue
                if name in saved:
                    last = saved[name]
                    if (validator and last[-1] == new[-1]) or (
                        not validator and last == new
                    ):
                        print(f"[{tries}] pause: {pause}")
                        await asyncio.sleep(pause)
                        continue

                # if tries > 2:
                #     self.PAUSE = 0.5 * self.PAUSE + 0.5 * pause
                # else:
                #     self.PAUSE *= 0.9

                elapsed = time.time() - t0
                print(f"elapse: {elapsed}")
                # NOTE: (0.8 + 0.1) < 1.0, so will try to reduce time when possible
                self.PAUSE = 0.8 * self.PAUSE + 0.1 * elapsed
                return new
            except Exception as why:
                print(why)

            finally:
                saved[name] = new


class Page(Magic):

    # WAIT_STATES =  ['commit', 'load', 'domcontentloaded', 'networkidle']
    # WAIT_STATES = ["domcontentloaded", "networkidle"]
    WAIT_STATES = []
    WAIT_FUNCTIONS = set(["goto"])

    async def __call__(self, *args, **kw):
        try:
            result = await self._target_(*args, **kw)
            if self._target_.__func__.__name__ in self.WAIT_FUNCTIONS:
                await self._wait_page()
            else:
                _foo = 2
            return result
        except TypeError as why:
            result = self._target_(*args, **kw)
            return result

        except Exception as why:
            print(why)
            raise

        finally:
            pass

    # async def goto(self, *args, **kw):
    #     pass

    async def _wait_page(self):
        page = self._root_
        await page.wait_for_timeout(500)

        # states = ['networkidle']
        # states = ['commit', 'load', 'domcontentloaded', 'networkidle']
        for state in self.WAIT_STATES:
            await page.wait_for_load_state(state)


# Download required datasets (run once)
nltk.download("words")
nltk.download("wordnet")

word_list = set(words.words())
lemmatizer = WordNetLemmatizer()


def is_common_word(word):
    # Lemmatize the word to its base form
    base_word = lemmatizer.lemmatize(word.lower(), pos="n")  # 'n' for noun
    if base_word in word_list:
        return base_word


def is_random_word(universe):
    if not isinstance(universe, list):
        universe = [universe]

    universe = " ".join(universe)
    tokens = re.findall(r"\w+", universe)
    tokens = [is_common_word(_) for _ in tokens if len(_) > 3]
    return not all(tokens)


# Define vowels (simple lowercase set)
VOWELS = "aeiou"


def calculate_shannon_entropy(text):
    """Calculates the Shannon entropy of a string."""
    if not text:
        return 0.0
    text = text.lower()  # Ensure case-insensitivity for entropy calc
    length = len(text)
    counts = Counter(text)
    entropy = 0.0
    for char_count in counts.values():
        probability = char_count / length
        # Avoid math domain error for probability 0 (though Counter shouldn't yield 0 counts)
        if probability > 0:
            entropy -= probability * math.log2(probability)
    return entropy


def looks_like_random_word(
    word,
    entropy_threshold=3.0,
    max_consonant_threshold=4,
    max_vowel_threshold=3,
    min_length=4,
):
    """
    Detects if a word looks random based on entropy and C/V patterns.

    Args:
        word (str): The word to check.
        entropy_threshold (float): Minimum Shannon entropy to be considered potentially random.
                                   Needs tuning based on typical word lengths and language.
                                   Higher value means less sensitive.
        max_consonant_threshold (int): Max allowed consecutive consonants.
        max_vowel_threshold (int): Max allowed consecutive vowels.
        min_length (int): Minimum word length to apply checks.

    Returns:
        bool: True if the word appears random, False otherwise.
    """
    if not isinstance(word, str) or not word or len(word) < min_length:
        return False

    word_lower = word.lower()

    # 1. Check Shannon Entropy
    # Entropy tends to increase with length, making a fixed threshold tricky.
    # Common English words often have entropy between 2.0 and 3.0. Random strings higher.
    entropy = calculate_shannon_entropy(word_lower)
    if entropy > entropy_threshold:
        # Consider adding logging here if needed:
        # log.debug(f"Word '{word}' flagged as random by entropy: {entropy:.2f} > {entropy_threshold}")
        return True

    # 2. Check Consonant/Vowel Patterns (only for alphabetic words)
    if word_lower.isalpha():
        cv_pattern = "".join(["V" if c in VOWELS else "C" for c in word_lower])

        # Find max consecutive consonants
        max_consecutive_consonants = 0
        matches = re.findall(r"C+", cv_pattern)
        if matches:
            max_consecutive_consonants = max(len(m) for m in matches)

        if max_consecutive_consonants > max_consonant_threshold:
            # log.debug(f"Word '{word}' flagged as random by consonants: {max_consecutive_consonants} > {max_consonant_threshold}")
            return True

        # Find max consecutive vowels
        max_consecutive_vowels = 0
        matches = re.findall(r"V+", cv_pattern)
        if matches:
            max_consecutive_vowels = max(len(m) for m in matches)

        if max_consecutive_vowels > max_vowel_threshold:
            # log.debug(f"Word '{word}' flagged as random by vowels: {max_consecutive_vowels} > {max_vowel_threshold}")
            return True

    # If neither check flagged it, assume it's not random
    return False


def tokens(value):
    """Extracts unique alphabetical tokens from a string, sorted alphabetically.

    Args:
        value: The input value (will be converted to string).

    Returns:
        A sorted list of unique alphabetical tokens found in the string.
    """
    value = str(value)
    values = list(set([_ for _ in re.findall(r"(?iu)[^\W_]+", value)]))
    values.sort()
    return values


def ltokens(value):
    return [_.lower() for _ in tokens(value)]


def integers(value):
    value = str(value)
    values = list(set([_.lower() for _ in re.findall(r"(?i)\d+", value)]))
    values.sort()
    return values


# ---------------------------------------------------------
# LogicLoader
# ---------------------------------------------------------


def sanitice_json(text):
    SANITIZE_JSON = {r"\"\s*\+\s*\"": ""}
    for pattern, repl in SANITIZE_JSON.items():
        text = re.sub(pattern, repl, text)

    return text


def save_json_xz(url, html_content):
    # get ldjson
    tree = etree.HTML(html_content)
    sel = """//script[@type="application/ld+json"]"""
    elements = tree.xpath(sel)
    queue = []

    last_sanitizers = [None, lambda x: x.replace("\t", "")]

    for element in elements:
        try:
            text = element.text
            if not text:
                continue
            text = sanitice_json(text)
            for method in last_sanitizers:
                if method:
                    text = method(text)
                try:
                    data = json.loads(text)
                except:
                    continue
                if isinstance(data, list):
                    queue.extend(data)
                else:
                    queue.append(data)
                break

        except Exception as why:
            print(why)
            info = traceback.format_exception(*sys.exc_info())
            print("".join(info))

    # choose a path to save the raw content
    _url = parse_uri(url)
    uid = generate_blueprint(_url)
    _url["path"] = uid  # = hashlib.md5(url.encode("utf-8")).hexdigest()
    today = datetime.now().strftime("%Y-%m-%d")
    path = "{host}/{path}".format_map(_url)
    path = path.lower()
    if not path.endswith(".json"):
        path = f"{path}.json"
    path = f"{VOL_DATA}/{today}/{path}.xz"
    os.makedirs(os.path.dirname(path), exist_ok=True)

    if isinstance(html_content, bytes):
        html_content = html_content.decode("utf-8")
    # prepare payload
    payload = {
        "html_content": html_content,
        "url": url,
        "ldjson": queue,
        "uid": uid,
    }
    # raw = pickle.dumps(payload)
    raw = json.dumps(payload)
    with open(path, "wb") as file:
        file.write(xz.compress(raw.encode("utf-8")))


def load_json_xz(path):
    with open(path, "rb") as file:
        raw = xz.decompress(file.read())
        raw = raw.decode("utf-8")
        payload = json.loads(raw)
        return payload


def camel_to_kebab_case(camel_str):
    # Use a regex to insert a hyphen before uppercase letters and convert to lowercase
    return re.sub(r"([a-z])([A-Z])", r"\1-\2", camel_str).lower()


def rgb_to_hex(color):
    rgb = [hex(int(number))[2:] for number in re.findall(r"\d+", color)]
    if rgb:
        color = "".join(rgb)
    return color


class StyleConverter:
    @classmethod
    def convert(cls, styles):
        result = {camel_to_kebab_case(key): value for key, value in styles.items()}

        # convert some items
        if color := result.get("color"):
            result["color"] = rgb_to_hex(color)

        return result


class LogicLoader:
    CACHE = {}

    def __init__(self, tops=[]):
        if isinstance(tops, str):
            tops = [tops]
        self.tops = [_ if os.path.isdir(_) else os.path.dirname(_) for _ in tops]
        for _ in [".", os.path.dirname(os.path.splitext(__file__)[0])]:
            if _ not in self.tops:
                self.tops.append(_)

    def load(self, page, realm=""):
        info = self.CACHE.setdefault(realm, {}).get(page)
        if info:
            path, ts, logic = info
            if ts < os.stat(path).st_mtime:
                info = None

        if not info:
            pattern = [
                f"{realm}.*{page}.yaml",
            ]
            pattern = r"|".join(pattern)

            def search():
                for top in self.tops:
                    for path, info in fileiter(top, regexp=pattern):
                        print(path)
                        if re.search(pattern, path):
                            yield path

            for path in search():
                log.debug("OK  found logic file: [%s]", path)
                logic = yaml.load(open(path, "r", encoding="utf-8"), Loader=yaml.Loader)
                info = path, os.stat(path).st_mtime, logic
                self.CACHE[realm][page] = info
                break
            else:
                log.debug("NOT found logic file: [%s]", page)
                return None

        return info[-1]


class BrowserBot(Magic):
    """A bot that controls a browser and provide basic helpers"""

    async def new_page(self):
        page = await self._target_.new_page()
        page = Page(page)
        return page

    async def get_lat_long(self, addresses):

        try:
            ctx = {
                "timeout": 1000,
            }

            page = await self.new_page()

            # Open Google Maps
            await page.goto("https://www.google.es/maps")

            # check if "Accept" condition button appears
            try:
                await page.click("button[aria-label='Aceptar todo']", **ctx)
            except plw.TimeoutError as why:
                _foo = 2

            # Setup map event listener
            # await setup_map_event_listener(page)
            # await human_like_mouse_move(page, 0, 0, 500, 500)

            t0 = time.time()
            result = {
                address: await get_lat_long(page, address) for address in addresses
            }
            elapsed = time.time() - t0
            print(f"elapsed: {elapsed}")
            return result
        except Exception as why:
            print(why)
        finally:
            # Close the page
            pass

    async def search(self, query):
        page = await self.new_page()
        q = query.keywords.replace(" ", "+")
        url = f"https://www.duckduckgo.com/{q}"
        await page.goto(url)

        await page.close()
        foo = 1


# Helpers


async def human_like_mouse_move(
    page, start_x, start_y, end_x, end_y, duration=2, steps=30
):
    # Calculate the distance to move
    distance_x = end_x - start_x
    distance_y = end_y - start_y

    mouse = page.mouse

    # Move in small steps
    dt = duration / steps
    t2 = time.time() + duration
    for step in range(steps):
        # Calculate intermediate position
        x = step / steps * 4 / math.pi
        x = math.sin(x)

        intermediate_x = start_x + distance_x * x + uniform(-5, 5)
        intermediate_y = start_y + distance_y * x + uniform(-5, 5)

        # Move the mouse to the intermediate position
        print(f"{x}: {intermediate_x}, {intermediate_y}")

        await mouse.move(intermediate_x, intermediate_y)

        # Wait a little to simulate human speed (varying delay between steps)
        remain = min(t2 - time.time(), dt)

        # await asyncio.sleep(uniform(0.0, remain))  # Add random short pauses

    # Finally move to the exact end position
    await mouse.move(end_x, end_y)


async def get_lat_long(page: Page, address):
    # Launch the browser
    # browser = p.chromium.launch(headless=False)
    # browser = await p.firefox.launch(headless=False)
    ctx = {
        "timeout": 1000,
    }

    # # page = await browser.new_page()

    await page.fill("input[id='searchboxinput']", address, **ctx)
    await page.keyboard.press("Enter")

    regexp = r"@(?P<latitude>-?\d+\.\d+),(?P<longitude>-?\d+\.\d+)"
    old = page.url
    # old = await page.unique("url", validator=regexp)

    # Extra wait to ensure the marker appears
    # await page.wait_for_load_state('networkidle')
    # await page.wait_for_timeout(500)
    # await page.reload(wait_until='domcontentloaded')
    # await page.wait_for_load_state('networkidle')
    # await page.wait_for_timeout(1500)

    if False:
        await page.wait_for_timeout(1000)

        # Find the red marker and click on it
        # The red marker usually has a specific class name.
        # We can inspect it using the browser's Developer Tools.
        # try:
        #     # Click on the red marker (Google Maps uses aria-label 'Location' for the marker)
        #     page.click(f"button[title='{address}']")
        #     # Wait a moment for the marker details to show up
        #     page.wait_for_timeout(1000)
        # except:
        #     print("Could not find or click the red marker.")
        #
        #
        # Simulate a click at the center of the map (where the marker is usually positioned)
        # Adjust the coordinates if necessary, depending on the zoom level
        map_width, map_height = (
            page.viewport_size["width"],
            page.viewport_size["height"],
        )
        # Click at the center of the map
        x0, y0 = uniform(0, map_width), uniform(0, map_height)
        x1, y1 = map_width // 2, map_height // 2
        x2, y2 = x1 * uniform(0.8, 0.9), y1 * uniform(0.8, 0.9)

        # await human_like_mouse_move(page, x0, y0, x2, y2)
        # await human_like_mouse_move(page, x2, y2, x1, y1)
        # await human_like_mouse_move(page, x1, y1, x0, y0)

        await page.mouse.click(x1, y1, button="right")
        await page.wait_for_timeout(1000)
        # page.keyboard.press('ArrowDown')
        # page.keyboard.press('ArrowUp')

        focused_element = await page.evaluate_handle(
            "document.activeElement"
        )  # Get the active (focused) element
        box = await focused_element.bounding_box()

        # Now use the mouse click on the element based on its bounding box (left-click)
        x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
        # page.mouse.click(x,y)
        await page.mouse.move(x, y)
        await page.mouse.click(x, y)
        # focused_element.click()

        page.keyboard.press("Enter")

        # get the content from clipboard
        text = await page.evaluate("navigator.clipboard.readText().then(text => text);")
        print(text)

        # text = await page.evaluate(
        #     "navigator.clipboard.readText().then(text => text);"
        # )
        # print(text)

        # 48.8583701, 2.2944812999999997
        # 48.85866656635026, 2.2945885883611203
        # 37.393301554385886, -6.074174555819438
        # 37.3931396, -6.0742281999999985
        # 37.39247473095943, -6.073230418241575
        # Get the current URL

        #  48.858638331535424, 2.2945027576722237
        # diference
        # url  : 37.3931396       , -6.0742282,
        # click: 37.39327598266401, -6.0742496576722225

    # await page.wait_for_load_state('networkidle')
    # await page.reload(wait_until='domcontentloaded')
    # await page.wait_for_load_state('networkidle')
    # await page.wait_for_timeout(1000)

    # await page.reload(wait_until='domcontentloaded')
    # await page.wait_for_timeout(500)

    regexp = r"@(?P<latitude>-?\d+\.\d+),(?P<longitude>-?\d+\.\d+)"
    new = None

    while True:
        # url, geo = await page.unique("url", validator=regexp)
        if page.url != old:
            break
        await page.wait_for_timeout(500)

    url, geo = await page.unique("url", validator=regexp)

    # Use a regex pattern to extract latitude and longitude from the URL
    if geo:
        geo = {k: float(v) for k, v in geo.items()}
    print(f"{address}: {geo}")
    return geo


# -------------------------------------------------------------------
# BrowserLogicBot
# -------------------------------------------------------------------


class BrowserLogicBot(SwarmBot):
    "Basic Web-Browser Bot"

    MAX_RETRIES = 1
    RETRY_DELAY = 0.0

    ALLOWED_KIND = set(
        [
            SWARM_REGISTER,
            SWARM_TASKS,
        ]
    )

    ALLOWED_TYPES = set(
        flatten(
            [
                SwarmBot.ALLOWED_TYPES,
                # "foo" # TODO: new types for this boot
            ]
        )
    )
    ALLOWED_PARAMS = iBot.ALLOWED_PARAMS + [
        # add any private parameter that you want to be included
        # when call _build_params()
    ]

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.headless = self.context.get("headless", True)

        # self.headers = {
        #     # USER_AGENT: f"python-{self.__class__.__name__.lower()}/{__version__}",
        #     USER_AGENT: "Mozilla/5.0 (X11; Linux i686; rv:125.0) Gecko/20100101 Firefox/125.0",
        #     CONTENT_TYPE: APPLICATION_JSON,
        #     # "Authorization": f"Bearer {personal_access_token}",
        # }
        self.operational.update(
            {
                "find_missing_search": {
                    # "max_files": [10000, 1000, 0.99],
                    # "max_task": [100, 10, 0.99],
                    "lapse": [60, 300, 1.01],
                },
            }
        )

    def _add_plugins(self):
        # super()._add_plugins()
        # self.plugins.clear()

        # self.add_plugin(HashStreamPlugin())
        self.add_plugin(MetaExtractPlugin(geojson=False))
        self.add_plugin(PutPlugin())
        self.add_plugin(SetURIPlugin())
        # self.add_plugin(SortPlugin())

        # self.add_plugin(RenameKeys())
        # self.add_plugin(UnwrapResponse())
        # self.add_plugin(RegExtractor())
        # self.add_plugin(Cleaner())
        # self.add_plugin(FQIUD())
        # self.add_plugin(DeepSearch())
        # self.add_plugin(SimplePagination())

        # mine
        # self.add_plugin(UpdateTaskStatus())

    def _prepare_task(self, **_task):
        raise NotImplementedError()

    async def _get_session(self, url, **context) -> iSession:
        self._sessions.clear()
        return await super()._get_session(url, **context)

    async def _swarm_get_tasks(self):
        """
                universe
        {'www.notino.es': [{'bot': '0',
                            'datetime': '2025-07-12 10:22:37.128127+00:00',
                            'fquid': 'pricemon://crawler/queue:ff97c78fc536e13407b60fab27054f2a',
                            'id': 'queue:ff97c78fc536e13407b60fab27054f2a',
                            'kind__': 'prices',
                            'last': '2025-07-12 10:07:37.128127',
                            'payload': None,
                            'url': 'https://www.notino.es/ardell/remover-producto-para-quitar-las-pestanas-postizas/p-16258869/'}]}
        """
        universe = {}
        if True:
            _task = {
                "bot": "wip",
                "datetime": "2025-01-18 11:46:18.241069+00:00",
                "id": "queue:00a401e322d3a3b43e8687cf5d4c10bd",
                "kind__": "prices",
                "url": "https://makeup.es/product/600657/",
                # "url": "https://wells.pt/total-plex-bond-reconstruction-shampoo-7932859.html",
                # "url": "https://www.maquillalia.com/ardell-kit-de-pestanas-postizas-seamless-naked-p-84985.html",
                # "url": "https://www.douglas.es/es/p/5010993205",
                # "url": "https://www.amazon.es/gp/offer-listing/B00LM8CW6Y",
                # "url": "https://www.mystyle-beauty.com/marcas/the-cosmetic-republic/the-cosmetic-republic-keratin-hair-fibers-negro-125grs",
                # "url": "https://www.fruugo.es/ardell-pack-deluxe-pestana-110-negro/p-89720505-187184651",
                # "url": "https://www.atida.com/es-es/kativa-champu-aceite-de-argan-250-ml",
                # "url": "https://www.caretobeauty.com/es/kativa-coconut-conditioner-355ml",
                # "url": "https://www.holaprincesa.es/products/mascarilla-con-manteca-de-karite-aceite-de-coco-y-marula-300-ml-kativa",
            }
            # _task.setdefault("type", "ldjson")
            host = parse_uri(_task.get("url")).get("host")
            universe.setdefault(host, []).append(_task)

        else:
            universe.update(await super()._swarm_get_tasks())

        return universe

    def can_handle(self, task):
        "return if the function can be handled by this iBot"
        if super().can_handle(task):
            return True

        # check for task subtype
        type_ = task.get(TASK_KEY, {}).get("type")
        if type_ is None:
            return True

        if type_ in self.ALLOWED_TYPES:  # ldjson, logic, ...
            return True
        return False


class BrowserCrawler(SwarmCrawler):
    "Base of all BrowerCrawlers"

    SESSIONS = set(
        flatten(
            [
                SwarmCrawler.SESSIONS,
            ]
        )
    )
    # ORCHESTRATOR_FACTORY = SwarmOrchestrator
    ACTIONS = list(
        flatten(
            [
                SwarmCrawler.ACTIONS,
            ]
        )
    )

    def __init__(
        self,
        *args,
        **kw,
    ):
        kw.setdefault("headless", True)
        kw.setdefault("logic_path", __file__)
        super().__init__(
            *args,
            **kw,
        )
        self.headless = kw.get("headless")
        self.logic_path = kw.get("logic_path")


class iBrowserSession(iSession):
    """Session for browser-based crawling"""

    ACTIONS = {
        "text": {
            "xpath": "//textarea",
        },
    }

    HEADERS = {
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
        "Accept-Language": "en",
    }

    HIGHLIGHT = {
        None: "border: 1px dotted gray; background-color: rgba(0, 255, 255, 0.15);",
        0: "border: 3px solid red; background-color: rgba(0, 255, 255, 0.15);",
        1: "border: 3px solid blue; background-color: rgba(255, 255, 0, 0.15);",
        2: "border: 3px solid green; background-color: rgba(255, 0, 255, 0.15);",
    }

    PAUSE = {
        None: 1.50,
        "input": 0.15,
        "textarea": 0.15,
        "a": 0.0,
        "div": 0.0,
    }

    PROPERTY_ACCESSORS = {
        "tag": "(element) => element.tagName.toLowerCase()",
        "type": "(element) => element.getAttribute('type')",
        "href": "(element) => element.getAttribute('href')",
    }

    SEARCH = {
        # 'xpath': By.XPATH,
    }

    XPATH_SEARCH = "//textarea"

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self._browser = None
        self._session = None
        self.browser = None
        self.headless = self.bot.parent.headless
        self.page = {}
        self.page_stack = []
        self.ANALYZE = {}

        self._populate_analyze(target=self)

    def _populate_analyze(self, target):
        for func in dir(target):
            if m := re.match(r"_(?P<key>analyze|direct|handler)_(?P<name>.*)", func):
                key = m.groupdict()["key"]
                name = m.groupdict()["name"]
                self.ANALYZE.setdefault(key, {})[name] = getattr(target, func)

    def __enter__(self, *args, **kw):
        if self._session is None:
            self._session = plw.async_playwright()

        return self

    async def __aenter__(self, *args, **kw):
        if self._session is None:
            # self._session = await plw.async_playwright().start()
            self._session = plw.async_playwright()
        return self

    def __exit__(self, *exc):
        pass

    async def __aexit__(self, *exc):
        if self._session:
            # await self._session.stop()
            self._session = None
        return self.__exit__(*exc)

    async def _create_connection(self, uri: DURI, **_uri):
        # uri = parse_uri(url, **kw)
        # url = self._get_base_url()
        # return aiohttp.ClientSession(base_url=url)
        _browser = await self._session.chromium.launch(headless=self.headless)

        return _browser

    @property
    def current(self):
        return self.page_stack[-1]

    async def _render_value(self, action, context, expression=None):
        expression = expression or "{{{{ {cmd__} }}}}"
        ctx = dict(context)
        ctx.update(action)
        last, value = False, True
        while value != last:
            if m := re.search(r"\s\{\w+\}\s", expression):
                expression = expression.format_map(context)
            template = Template(expression)
            last, value = value, template.render(**ctx)
            expression = value
        return value

    async def _get_property(self, page, item, *names, force_dict=False):
        item_handle = await item.element_handle()
        if item_handle:
            result = {
                name: await page.evaluate(
                    self.PROPERTY_ACCESSORS[name],
                    item_handle,
                )
                for name in names
            }
            if len(result) == 1 and not force_dict:
                _, result = result.popitem()
            return result

    async def get(self, *args, **kw):
        """
        {'url': 'https://www.duckduckgo.com/kativa alisado',
        'headers': {},
        'params': {'kind__': 'prices',
                   'path__': '/kativa alisado',
                   'keywords': 'kativa alisado',
                   'type': 'shopping',
                   'region': 'es-es',
                   'shopping': 'True',
                   'links': 'True',
                   'func__': 'get_data',
                   'prefix_uri__': 'prices://duckduckgo/{{ kind__ }}:{{ id }}',
                   'url__': 'https://www.duckduckgo.com'}}

        """

        # TODO: where is used create_connection in base library?
        # url = kw['url']
        # browser = await self._create_connection(uri)
        while True:
            try:
                async with self._session as p:
                    # Launch the browser
                    self._browser = await p.chromium.launch(headless=self.headless)
                    self.browser = BrowserBot(self._browser)

                    # context = kw["params"] # Original line
                    context = kw.get("params", {})  # Use .get() for safety
                    context.setdefault("pagination", {})

                    kind = context.get(KIND_KEY, "main")
                    main, logic = await self.new_page(kind)

                    stages = logic["stages"]
                    sequence = logic["sequence"]

                    order = list(stages)
                    order.sort()
                    for _stage in order:
                        # maps = self.SCRIPT[_stage]
                        maps = stages[_stage]
                        for param in set(maps).intersection(context):
                            actions = maps[param]
                            for action in actions:
                                # for cmd in self.ACTION_SEQUENCE:
                                for cmd in sequence:
                                    if cmd not in action:
                                        continue
                                    handler = f"_handler_{cmd}"
                                    context["cmd__"] = cmd
                                    if func := getattr(self, handler, None):
                                        response = await func(main, action, context)
                                        if isinstance(response, plw.Response):
                                            if response.status < 300:
                                                log.debug("OK: %s", response.request)
                                                context["headers"] = headers = (
                                                    await response.all_headers()
                                                )
                                                content_length = headers.get(
                                                    "content-length"
                                                )
                                                if content_length:
                                                    content_type = headers.get(
                                                        "content-type"
                                                    )
                                                    try:

                                                        if re.search(
                                                            "text|html", content_type
                                                        ):
                                                            result = (
                                                                await response.body()
                                                            )
                                                        else:
                                                            result = (
                                                                await response.json()
                                                            )
                                                    except Exception as why:
                                                        result = None
                                                    context["result"] = result
                                            else:
                                                log.error(response.status_text)
                                                raise RuntimeError(response)
                                        elif isinstance(response, plw.Locator):
                                            log.debug(
                                                "OK: [%s] elements: %s",
                                                await response.count(),
                                                response,
                                            )
                                        else:
                                            log.debug("OK: %s", response)
                                            context["result"] = response
                                    else:
                                        log.error(
                                            "[%s] session has not method [%s(...)]",
                                            self,
                                            handler,
                                        )
                                        # TODO: raise or continue?
                                    # await main.wait_for_load_state("networkidle")
                                    # await main.wait_for_load_state("domcontentloaded")

                    # https://duckduckgo.com/?q=kativa&iax=shopping&ia=shopping
                    # await self.analyze(main)
                    headers = context.setdefault("headers", {})
                    body = context["result"]
                    if isinstance(
                        body,
                        (
                            list,
                            dict,
                            bool,
                        ),
                    ):
                        headers["Content-Type"] = APPLICATION_PYTHON

                    response = iResponse(
                        status=200,
                        headers=context.get("headers"),
                        links=None,
                        real_url=context.get("url__"),
                        body=body,
                    )
                    return response
            except asyncio.CancelledError as why:
                log.error("%s", why)
                log.error("retry in 5 secs")
                await asyncio.sleep(5)
            except Exception as why:
                log.error("%s", why)
                log.error("".join(traceback.format_exception(*sys.exc_info())))
                log.error("retry in 5 secs")
                await asyncio.sleep(5)
            finally:
                # TODO: can live self._browser outside `with` block?
                # self._browser = None
                # self.browser = None
                # main and main.close()
                # aux and aux.close()
                while self.page:
                    name, page = self.page.popitem()
                    await page.close()
                pass

    # ----------------------------------------------------------------
    # handlers
    # ----------------------------------------------------------------
    async def handle(self, item, value):
        # TODO: used?
        name = f"_handle_{item.tag_name}"
        handler = getattr(self, name, None)
        assert handler, f"missing function: {name}"
        self.sleep(item)
        try:
            result = handler(item, value)
        except Exception as why:
            print(why)
            result = False
        return result

    async def _handler_infinite_scroll(self, page, action, context):
        await page.wait_for_load_state("domcontentloaded")
        await page.wait_for_load_state("networkidle")
        timeout = context.get("timeout__", 60)
        decay = context.get("decay__", 1.05)
        last_height, curr_height, t1 = False, True, time.time() + timeout
        while last_height != curr_height and time.time() < t1:
            last_height = curr_height
            curr_height = await page.evaluate("(window.innerHeight + window.scrollY)")
            if curr_height > last_height:
                t1 = time.time() + timeout

            print(f"- curr_height: {curr_height}, decay: {decay}")
            # log.debug("height: %s, decay: %s", curr_height, decay)
            for _ in range(0, random.randint(1, 6)):
                await page.mouse.wheel(0, random.randint(15, 75))
                await asyncio.sleep(0.3 + random.random() * 0.5)

            await asyncio.sleep(0.205 + random.random() * decay)
            # decay *= 0.97
            decay = max(0.1, decay * 0.89)
            # break  # TODO: agp: REMOVE DEBUG
        return last_height

    async def _handler_input_text(self, page, action, context):
        """
        Try to typing a text into an input_text item.
        The value is rendered from context.
        """
        item = context["item__"]
        value = await self._render_value(action, context)
        await item.type(text=value)
        response = await item.input_value()

        if value == response:
            log.debug("OK: typed [%s]", response)
        else:
            log.warning("trying to select: [%s] but got [%s]", value, response)

        return response

    async def _handler_textarea(self, page, action, context):
        """
        Try to typing a text into an input_text item.
        The value is rendered from context.
        """
        return await self._handler_input_text(page, action, context)


class BrowserLogicSession(iBrowserSession):
    """Session for browser-based crawling"""

    IMAGE_EXT = {"jpeg": "jpg"}

    VISITED_STYLE = "2px solid blue"
    FOUND_STYLE = "5px solid red"

    DEFAULTS = {
        "click": {
            "sleep": 0.5,
        },
        "ldjson": {
            "loop": "all",
            "append": True,
        },
        "meta": {
            "loop": "all",
            "append": True,
            "keyword": ["itemprop", "name"],
        },
    }

    def __init__(self, logic_path=".", *args, **kw):
        super().__init__(*args, **kw)

        self.logic = LogicLoader(tops=[logic_path, __file__])

        self.analyzer = XPathAnalyzer()
        target = self.analyzer
        self._populate_analyze(target)

        self._logic_handler = {
            "__default__": self._logic_handler_1,
            "browser-logic": self._logic_handler_2,
        }

    async def _logic_handler_1(self, page, logic, task, **context):
        final_url = page.url  # 301: redirect, etc
        ctx = {"url": final_url}
        ctx = await self.analyze(page, logic, **ctx)

        log.debug("Item: %s", ctx)

        uid = task.get(ID_KEY)
        _uid = parse_duri(uid)

        data = {
            **context,
            **ctx["item"],
            "datetime": datetime.utcnow(),
            "url": final_url,
            ID_KEY: _uid[ID_KEY],
        }
        response = iResponse(
            status=200,
            headers={
                **self.headers,
                CONTENT_TYPE: APPLICATION_PYTHON,
            },
            links=None,
            real_url=context.get(ORG_URL),
            body=[data],
        )
        return response

    async def _logic_handler_2(self, page, logic, task, **context):
        """
        async def get_de_base(self, *args, **kw):
        {'url': 'https://www.duckduckgo.com/kativa alisado',
        'headers': {},
        'params': {'kind__': 'prices',
                   'path__': '/kativa alisado',
                   'keywords': 'kativa alisado',
                   'type': 'shopping',
                   'region': 'es-es',
                   'shopping': 'True',
                   'links': 'True',
                   'func__': 'get_data',
                   'prefix_uri__': 'prices://duckduckgo/{{ kind__ }}:{{ id }}',
                   'url__': 'https://www.duckduckgo.com'}}
        """

        # TODO: where is used create_connection in base library?
        # url = kw['url']
        # browser = await self._create_connection(uri)
        try:
            # Launch the browser
            # self._browser = await p.chromium.launch(headless=self.headless)
            # self.browser = BrowserBot(self._browser)

            # context = kw["params"] # Original line
            # context = kw.get("params", {})  # Use .get() for safety
            # context.setdefault("pagination", {})

            stages = logic["stages"]  # stages to be processed in order
            sequence = logic["sequence"]  # action execution priority

            order = list(stages)
            order.sort()
            for _stage in order:
                # maps = self.SCRIPT[_stage]
                maps = stages[_stage]
                for param in set(maps).intersection(context):
                    actions = maps[param]
                    for action in actions:
                        # for cmd in self.ACTION_SEQUENCE:
                        for cmd in sequence:
                            if cmd not in action:
                                continue
                            handler = f"_handler_{cmd}"
                            context["cmd__"] = cmd
                            if func := getattr(self, handler, None):
                                response = await func(page, action, context)

                                # process response type
                                if isinstance(response, plw.Response):
                                    if response.status < 300:
                                        log.debug("OK: %s", response.request)
                                        context["headers"] = headers = (
                                            await response.all_headers()
                                        )
                                        content_length = headers.get("content-length")
                                        if content_length:
                                            content_type = headers.get("content-type")
                                            try:
                                                if re.search("text|html", content_type):
                                                    result = await response.body()
                                                else:
                                                    result = await response.json()
                                            except Exception as why:
                                                result = None
                                            context["result"] = result
                                    else:
                                        log.error(response.status_text)
                                        raise RuntimeError(response)
                                elif isinstance(response, plw.Locator):
                                    log.debug(
                                        "OK: [%s] elements: %s",
                                        await response.count(),
                                        response,
                                    )
                                else:
                                    log.debug("OK: %s", response)
                                    context["result"] = response
                            else:
                                log.error(
                                    "[%s] session has not method [%s(...)]",
                                    self,
                                    handler,
                                )
                                # TODO: raise or continue?
                            # await main.wait_for_load_state("networkidle")
                            # await main.wait_for_load_state("domcontentloaded")

            # https://duckduckgo.com/?q=kativa&iax=shopping&ia=shopping
            # await self.analyze(main)
            headers = context.setdefault("headers", {})
            body = context["result"]
            if isinstance(
                body,
                (
                    list,
                    dict,
                    bool,
                ),
            ):
                headers["Content-Type"] = APPLICATION_PYTHON

            response = iResponse(
                status=200,
                headers=context.get("headers"),
                links=None,
                real_url=context.get("url__"),
                body=body,
            )
            return response
        except asyncio.CancelledError as why:
            log.error("%s", why)
            log.error("retry in 5 secs")
            await asyncio.sleep(5)
        except Exception as why:
            log.error("%s", why)
            log.error("".join(traceback.format_exception(*sys.exc_info())))
            log.error("retry in 5 secs")
            await asyncio.sleep(5)
        finally:
            # TODO: can live self._browser outside `with` block?
            # self._browser = None
            # self.browser = None
            # main and main.close()
            # aux and aux.close()
            while self.page:
                name, page = self.page.popitem()
                await page.close()
            pass

    async def new_page(self, name="default"):
        logic = self.logic.load(name)
        if not (page := self.page.get(name)):
            page = await self.browser.new_page()
            self.page[name] = page
            self.page_stack.append(name)
            # x, y = 800, 10
            # await page.evaluate(f"window.moveTo({x}, {y});")

        return page, logic

    async def _save_raw(self, res):
        # choose a path to save the raw content
        url = self.context.get(TASK_KEY, {}).get("url")
        if url := url or self.context.get(ORG_URL):
            html_content = await res.body()
            save_json_xz(url, html_content)

    async def _get_xpath(self, element):
        xpath = await element.evaluate(
            """(element) => {
                    function getXPath(el) {
                        if (!el) return '';
                        if (el.tagName === 'HTML') return '/html';
                        const index = Array.from(el.parentNode.children)
                            .filter(e => e.tagName === el.tagName)
                            .indexOf(el) + 1;
                        const parentXPath = getXPath(el.parentNode);
                        return `${parentXPath}/${el.tagName.toLowerCase()}[${index}]`;
                    }
                    return getXPath(element);
                }""",
            element,
        )

        return xpath

    async def DELETE_browser_request(self, url, context, **kw):
        task = context.get(TASK_KEY, {})

        try:
            # return 404 by default
            data = []
            response = iResponse(
                status=404,
                headers={
                    **self.headers,
                    CONTENT_TYPE: APPLICATION_PYTHON,
                },
                links=None,
                real_url=context.get(ORG_URL),
                body=data,
                result=data,
            )
            main = aux = None
            async with self._session as p:
                # Launch the browser
                screen_width = 128 * 13
                screen_height = 128 * 11
                x, y = 2500, 50
                self._browser = await p.chromium.launch(
                    headless=self.headless,
                    # no_viewport=True,
                    args=[
                        f"--window-position={x},{y}",
                        f"--window-size={screen_width},{screen_height}",
                    ],
                )

                timeout = 20000
                self._context = await self._browser.new_context(
                    no_viewport=True,
                    viewport={"width": screen_width, "height": screen_height},
                )
                self._context.set_default_timeout(timeout)

                self.browser = BrowserBot(self._context)
                context = kw["params"]

                page, logic = await self.new_page("main")
                if url := kw.get("url") or context.get(ORG_URL):
                    # --------------------------------------------
                    # continue with browser
                    # --------------------------------------------
                    try:
                        res = await page.goto(url, timeout=25000, wait_until=None)
                        if res.status >= 400:
                            return response

                        await self._save_raw(res)

                        # # Get the entire DOM content
                        # dom_content = await page.content()
                        # with open("page.html", "w", encoding="utf-8") as file:
                        #     file.write(dom_content)
                        # foo = 1
                    except plw.TimeoutError:
                        log.debug(
                            "[%s] loading timeout [%s]: Page doesn't give me back control",
                            url,
                            timeout,
                        )
                        log.debug("Continue with normal process")
                        foo = 1

                    final_url = page.url  # 310: redirect, etc
                    _final_url = parse_uri(final_url)

                    host = _final_url["host"]
                    realm = context[KIND_KEY]
                    logic = self.logic.load(host, realm=realm) or []

                    # TODO: agp: analyze logic type and delegate in some logic handler

                    if logic:
                        ctx = {
                            "url": url,
                        }
                        ctx = await self.analyze(page, logic, **ctx)

                        log.debug("Item: %s", ctx)

                        uid = task.get(ID_KEY)
                        _uid = parse_duri(uid)

                        data = {
                            **context,
                            **ctx["item"],
                            "datetime": datetime.utcnow(),
                            "url": final_url,
                            ID_KEY: _uid[ID_KEY],
                        }
                        response = iResponse(
                            status=200,
                            headers={
                                **self.headers,
                                CONTENT_TYPE: APPLICATION_PYTHON,
                            },
                            links=None,
                            real_url=context.get(ORG_URL),
                            body=[data],
                        )
                    else:
                        msg = f"logic for [{host}] not found"
                        log.warning(msg)
                        data = {
                            **context,
                            "message": msg,
                            "datetime": datetime.utcnow(),
                            "url": final_url,
                        }
                        response = iResponse(
                            status=422,
                            headers={
                                **self.headers,
                                CONTENT_TYPE: APPLICATION_PYTHON,
                            },
                            links=None,
                            real_url=context.get(ORG_URL),
                            body=[data],
                        )
                        foo = 1

            return response

        except asyncio.CancelledError as why:
            log.error("%s", why)
            log.error("retry in 5 secs")
            await asyncio.sleep(5)
        except plw.TimeoutError as why:
            log.warn("%s", why)
            log.error("".join(traceback.format_exception(*sys.exc_info())))
        except plw.Error as why:
            log.error("%s", why)
            # log.error("".join(traceback.format_exception(*sys.exc_info())))
            await asyncio.sleep(1)
        except Exception as why:
            log.error("%s", why)
            log.error("".join(traceback.format_exception(*sys.exc_info())))
            log.error("retry in 5 secs")
            await asyncio.sleep(1)
        finally:
            # TODO: can live self._browser outside `with` block?
            self._browser = None
            self.browser = None
            page and await page.close()
            aux and await aux.close()
            return response

    async def get(self, url=None, *args, **kw):
        """
        kw ?
               {'url': 'https://www.duckduckgo.com/foo/2024-11-21T00:00:00UTC/bar/2024-11-23T00:00:00UTC',
        'headers': {},
        'params': {'kind__': 'prices',
                   'path__': '/foo/2024-11-21T00:00:00UTC/bar/2024-11-23T00:00:00UTC',
                   'func__': 'get_data',
                   'prefix_uri__': 'prices://duckduckgo/{{ kind__ }}:{{ id }}',
                   'url__': 'https://www.duckduckgo.com'}}

        kw <--- ok
        {'url': 'https://www.duckduckgo.com/kativa alisado',
        'headers': {},
        'params': {'kind__': 'prices',
                   'path__': '/kativa alisado',
                   'keywords': 'kativa alisado',
                   'type': 'shopping',
                   'region': 'es-es',
                   'shopping': 'True',
                   'links': 'True',
                   'func__': 'get_data',
                   'prefix_uri__': 'prices://duckduckgo/{{ kind__ }}:{{ id }}',
                   'url__': 'https://www.duckduckgo.com'}}

        # web example
        kw
        {'url': 'https://www.primor.eu/es_es/ardell-naked-extensions-pestanas-postizas-98446.html',
         'headers': {},
         'params': {'kind__': 'prices',
                    'url__': 'https://www.primor.eu/es_es/ardell-naked-extensions-pestanas-postizas-98446.html',
                    'func__': 'get_data',
                    'prefix_uri__': 'prices://duckduckgo/{{ kind__ }}:{{ id }}'}}


        """
        frame = sys._getframe(1)
        context = frame.f_locals.get("context")
        page = aux = None

        url = url or context.get(ORG_URL)
        if not url:
            return None

        task = context.get(TASK_KEY, {})
        try:
            # return 404 by default
            data = []
            response = iResponse(
                status=404,
                headers={
                    **self.headers,
                    CONTENT_TYPE: APPLICATION_PYTHON,
                },
                links=None,
                real_url=context.get(ORG_URL),
                body=data,
                result=data,
            )
            main = aux = None
            async with self._session as p:
                # Launch the browser
                screen_width = 128 * 13
                screen_height = 128 * 11
                x, y = 2500, 50
                self._browser = p.chromium  # firefox

                self._context = await self._browser.launch_persistent_context(
                    os.path.abspath("./browser_data"),
                    headless=self.headless,
                    # no_viewport=True,
                    viewport={"width": screen_width, "height": screen_height},
                    args=[
                        f"--window-position={x},{y}",
                        f"--window-size={screen_width},{screen_height}",
                    ],
                )

                timeout = 20000
                self._context.set_default_timeout(timeout)
                self.browser = BrowserBot(self._context)
                context = kw.get("params", {})  # Use .get() for safety
                context.setdefault("pagination", {})

                # open browser and goto initial url
                # url can contain 301 redirect
                page, logic = await self.new_page("main")
                if url := kw.get("url") or context.get(ORG_URL) or context.get("url"):
                    try:
                        res = await page.goto(url, timeout=25000, wait_until=None)
                        if res.status >= 400:
                            return response
                        await self._save_raw(res)  # save raw html

                        # # Get the entire DOM content
                        # dom_content = await page.content()
                        # with open("page.html", "w", encoding="utf-8") as file:
                        #     file.write(dom_content)
                        # foo = 1
                    except plw.TimeoutError:
                        log.debug(
                            "[%s] loading timeout [%s]: Page doesn't give me back control",
                            url,
                            timeout,
                        )
                        log.debug("Continue with normal process")
                        foo = 1

                    final_url = page.url  # 301: redirect, etc
                    _final_url = parse_uri(final_url)

                    # load the logic yaml file
                    host = _final_url["host"]
                    kind = context.get(KIND_KEY, "main")
                    logic = self.logic.load(host, realm=kind) or []

                    if logic:
                        # TODO: agp: analyze logic type and delegate in some logic handler
                        logic_kind = logic.get("kind")
                        if handler := self._logic_handler.get(
                            logic_kind
                        ) or self._logic_handler.get("__default__"):
                            response = await handler(page, logic, task, **context)

                    else:
                        msg = f"logic for [{host}] not found"
                        log.warning(msg)
                        data = {
                            **context,
                            "message": msg,
                            "datetime": datetime.utcnow(),
                            "url": final_url,
                        }
                        response = iResponse(
                            status=422,
                            headers={
                                **self.headers,
                                CONTENT_TYPE: APPLICATION_PYTHON,
                            },
                            links=None,
                            real_url=context.get(ORG_URL),
                            body=[data],
                        )
                        foo = 1
                else:
                    log.warning("NO url is provided!")
            return response

        except asyncio.CancelledError as why:
            log.error("%s", why)
            log.error("retry in 5 secs")
            await asyncio.sleep(5)
        except plw.TimeoutError as why:
            log.warn("%s", why)
            log.error("".join(traceback.format_exception(*sys.exc_info())))
        except plw.Error as why:
            log.error("%s", why)
            # log.error("".join(traceback.format_exception(*sys.exc_info())))
            await asyncio.sleep(1)
        except Exception as why:
            log.error("%s", why)
            log.error("".join(traceback.format_exception(*sys.exc_info())))
            log.error("retry in 5 secs")
            await asyncio.sleep(1)
        finally:
            # TODO: can live self._browser outside `with` block?
            self._browser = None
            self.browser = None
            page and await page.close()
            aux and await aux.close()
            return response

    async def analyze(self, page, logic, **ctx):
        """Analyze the page"""
        ctx["page"] = page
        ctx["item"] = {}
        if url := ctx.get("url"):
            ctx.update(parse_uri(url))

        keys = list(logic.keys())
        keys.sort()
        for ctx["step"] in keys:
            if re.match(r"__.*", ctx["step"]):
                continue
            ctx["info"] = info = logic[ctx["step"]]
            if not info:
                continue

            if handler := self.ANALYZE["direct"].get(info.get("type")):
                await handler(ctx)
                continue

            ctx["selector"] = info.get("selector")
            if selector := ctx["selector"]:
                if isinstance(selector, str):
                    selector = [selector]

                found = False
                for sel in selector:
                    ctx["current_selector"] = sel
                    # await asyncio.sleep(0.2)
                    _ctx = {**ctx}
                    _ctx.update(ctx["item"])

                    # sel = Template(sel).render(**ctx, **ctx["item"])
                    sel = Template(sel).render(**_ctx)
                    if elements := await self._locate(page, sel, ctx):
                        # TODO: review locator.wait_for() or page.wait_for_selector()
                        # n = await elements.count()
                        # foo = 1
                        for element in await elements.all():
                            # check CSS criteria
                            ctx["styles"] = await element.evaluate(
                                "el => window.getComputedStyle(el)"
                            )
                            await self._mark_element(element, self.VISITED_STYLE)

                            styles = StyleConverter.convert(ctx["styles"])
                            pattern_styles = info.get("styles", {})
                            skip = False
                            for key, pattern in pattern_styles.items():
                                if value := styles.get(key):
                                    pattern = pattern.replace(";", "")
                                    if not re.search(pattern, value):
                                        skip = True
                                        break
                            if skip:
                                continue

                            ctx["element"] = element
                            attributes = await self._get_attributes(element)
                            # attributes
                            # {'id': 'onetrust-accept-btn-handler',
                            #  'style': 'border: 2px solid blue;',
                            #  'tag': 'button',
                            #  'text': 'Sí, acepto todo'}

                            # print(attributes)
                            ctx["item"]["attributes"] = attributes

                            if _found := await self._resolve_element(element, ctx):
                                await self._mark_element(element, self.FOUND_STYLE)

                                # save common keywords related to this element to help AI
                                # finding the right XPATH based on typical attributes
                                # patterns used by other webs: i.e: class="foo current-price"
                                # Note: disable as AI discover module seems to need any help
                                # training = await self._save_step_training_attibutes(element, ctx)

                                if sleep := info.get("sleep"):
                                    await asyncio.sleep(sleep)
                                found |= _found
                                if not info.get("append"):
                                    break
                    if found and info.get("loop") not in ("all",):
                        break

            else:
                log.error("no selector")
                # log.error("sleeping for 20 secs...")
                await asyncio.sleep(1)
                foo = 1

        log.info("-" * len(ctx["url"]))
        log.info("%s", ctx["url"])
        item = ctx["item"]
        stream = [
            (key, value)
            for key, value in item.items()
            if not isinstance(value, (list, dict))
        ]
        stream.sort()
        for key, value in stream:
            log.info("- %s: %s", key, value)

        return ctx

    async def _locate(self, page, selector, ctx):
        elements = []
        # timeout = ctx["info"].get("timeout", 5)
        # num_selectors = len(ctx["info"]["selector"])
        # timeout = 1 + timeout // num_selectors
        timeout = 1.2
        t1 = time.time() + timeout
        while time.time() < t1:
            try:
                elements = await page.locator(selector)
                n = await elements.count()
                log.debug("selector: [%s] returns [%s] elements", selector, n)
                if n > 0:
                    return elements
                await asyncio.sleep(1)
            except plw.TimeoutError:
                log.debug("timeout: can't find [%s]", selector)
                await asyncio.sleep(1)
            except Exception as why:
                log.error("selector: %s -> %s", selector, why)
                foo = 1

    async def _mark_element(self, element, style):
        try:
            if await element.is_visible():
                await element.evaluate(f"el => el.style.border='{style}';")
                # await asyncio.sleep(1)
            # else:
            #     log.debug("element [%s] is not visible", element)
        except Exception as why:
            pass

    async def _get_attributes(self, element, *exclude):
        # Get all attributes
        # attributes = await element.evaluate(
        #     "element => Object.fromEntries([...element.attributes].map(attr => [attr.name, attr.value]))"
        # )
        try:
            # Get all attributes
            attributes = await element.evaluate(
                """(element) => {
                            const attrs = {};
                            for (let attr of element.attributes) {
                                attrs[attr.name] = attr.value;
                            }
                            return attrs;
                        }""",
                element,
            )
            tag = await element.evaluate("element => element.tagName", element)
            attributes["tag"] = tag.lower()

            text = await element.inner_text()
            attributes["text"] = text.strip()

            for pattern in exclude:
                for key in list(attributes):
                    if re.match(pattern, key):
                        attributes.pop(key, None)

            return attributes
        except Exception as why:
            pass

    async def _resolve_element(self, element, ctx):
        # get all single lines
        # lines = await element.all_inner_texts()
        # lines = "\n".join(lines)

        lines = ctx["item"]["attributes"]["text"]
        # lines = lines.splitlines()

        info = ctx["info"]

        # handle different actions
        if _type := info.get("handler"):
            info.update(self.DEFAULTS.get(_type, {}))
            if handler := self.ANALYZE["handler"].get(_type):
                return await handler(lines, ctx)
            else:
                log.error("can't find a handler function for [%s] type", _type)

        if _type := info.get("analyze"):
            info.update(self.DEFAULTS.get(_type, {}))
            if handler := self.ANALYZE["analyze"].get(_type):
                return handler(lines, ctx)
            else:
                log.error("can't find a analyze function for [%s] type", _type)

        if _type := info.get("direct"):
            info.update(self.DEFAULTS.get(_type, {}))
            if handler := self.ANALYZE["direct"].get(_type):
                return await handler(lines, ctx)
            else:
                log.error("can't find a direct for [%s] type", _type)

    # ----------------------------------------------------------------
    # handlers
    # ----------------------------------------------------------------

    async def _handler_a(self, page, action, context):
        return await self._handler_click(page, action, context)

    async def _handler_input_submit(self, page, action, context):
        item = context["item__"]
        value = await self._render_value(action, context)
        value = eval(value, {}, {})
        if value:
            await item.click()
        return value

    async def _handler_image(self, line, ctx) -> bool:
        item = ctx["item"]
        attributes = item["attributes"]

        found = False
        for src in "srcset", "src":
            if url := attributes.get(src):
                # url = https://assets.atida.com/transform/c26e1b1a-3608-470f-bd4c-741fa478b62c/Sendo-Champu-Calmante-250-ml?io=transform:extend,width:600,height:600
                if name := item.get("name"):
                    # fix wrong urls
                    # '//img2.miravia.es/g/fb/kf/E22713a693ed04ba891d0b473e8996110T.png_720x720q75.png_.webp'
                    _image_url = parse_uri(url)
                    _page_url = parse_uri(ctx["url"])

                    _image_url["path"].strip("/")
                    overlap(_image_url, _page_url)
                    url = build_uri(**_image_url)

                    response = requests.get(url)
                    if response.status_code == 200:
                        content_type = response.headers.get("Content-Type")
                        if m := re.match(r"image/(?P<type>.*)", content_type):
                            image_type = m.groupdict()["type"]
                            image_ext = self.IMAGE_EXT.get(image_type, image_type)

                            # TODO: use a jinja expression
                            path = f"/tmp/kapalua/{name}_{ctx['host']}.{image_ext}"
                            os.makedirs(os.path.dirname(path), exist_ok=True)
                            with open(path, "wb") as f:
                                f.write(response.content)
                            found = True
                            log.debug("Image saved as [%s]", path)
                            break
                        else:
                            log.warning(
                                "[%s] is not a valid image src / content-type",
                                content_type,
                            )
                    else:
                        log.error(
                            f"Failed to download image. Status code: {response.status_code}"
                        )
        else:
            log.warning(
                "default mechanism for storing image failed, using element screenshot"
            )
            # TODO: use a jinja expression
            image_ext = "png"
            name = item.get("name") or item["attributes"].get("alt")

            if not name:
                name = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

            name = tf(replace(name))

            path = f"/tmp/syncmodels/images/{name}_{ctx['host']}.{image_ext}"
            os.makedirs(os.path.dirname(path), exist_ok=True)

            element = ctx["element"]
            # style = await element.evaluate("el => window.getComputedStyle(el)")
            rs = await element.screenshot(path=path)
            found = rs is not None

        return found

    async def _handler_collect(self, page, action, context):
        # TODO: use many browser in parallel
        page_aux, _logic = await self.new_page("aux")
        await page_aux.set_default_timeout(20000)

        sites = {}
        stream = set()
        # aux._target_.WAIT_STATES = ['load', 'domcontentloaded', 'networkidle']
        elements = context.get("selector__")
        pattern = action.get("pattern", ".")
        exclude = action.get("exclude", r"$^")  # never matches!! :)
        if elements:
            universe = await elements.all()
            collected = set()
            for idx, item in enumerate(universe):
                href = await item.get_attribute("href")
                if href and re.search(pattern, href):
                    collected.add(href)

            collected = list(collected)
            random.shuffle(collected)
            N = len(collected)  # used later
            log.info("collect: [%s] urls", N)

            # TODO: this code will iterate and resolve some urls
            # TODO: better to resolve in parallel using multiples crawlers
            for idx, href in enumerate(collected):
                if href:
                    historial_links = [href]
                    try:
                        await page_aux.goto(href)
                    except plw.TimeoutError:
                        # better to try to add th url instead discard this entire web-site
                        # url = aux.url
                        log.warning("[%s]: TIMEOUT: %s", idx, url)
                        # _uri = parse_uri(url)
                        # sites.setdefault(_uri["host"], set()).add(url)
                        continue
                    except Exception as why:
                        log.error("[%s]: %s %s", idx, why)
                        continue

                    # we need to wait until all 301 redirects are done
                    for _ in range(300):
                        # await aux.wait_for_load_state("load")
                        url = page_aux.url

                        # DONE: agp:  check if we can get the same url using requests
                        # _headers = {'upgrade-insecure-requests': '1',
                        #             'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, '
                        #                           'like Gecko) Chrome/131.0.0.0 Safari/537.36',
                        #             'sec-ch-ua': '"Chromium";v="131", "Not_A Brand";v="24"',
                        #             'sec-ch-ua-mobile': '?0',
                        #             'sec-ch-ua-platform': '"Linux"'}
                        # response = requests.get(href, headers=_headers, allow_redirects=True)
                        # DONE: agp: doesn't work, 200, ddg -> bing, but we're missing the last jump
                        log.info("[%s/%s]: %s", idx, N, url)
                        historial_links.append(url)
                        if (
                            len(historial_links) > 2
                            and historial_links[0] != historial_links[-1]
                            and all([_ == url for _ in historial_links[-6:]])
                        ):
                            # sites.setdefault(_uri["host"], set()).add(url)
                            break
                        # await asyncio.sleep(0.05)
                        # don't work well, get stacked sometimes
                        # better simply check the urls
                        # await page_aux.wait_for_load_state("domcontentloaded")
                        try:
                            await page_aux.wait_for_load_state("networkidle")
                        except plw.TimeoutError:
                            log.warning("page stalled, continue")
                            break

                        except Exception as why:
                            break

                        await asyncio.sleep(0.99)

                    if url and re.search(exclude, url):
                        continue

                    historial_links.append(url)
                    # clean link
                    _uri = parse_uri(url)
                    for _ in "query", "query_", "fragment":
                        _uri.pop(_, None)

                    url = build_uri(**_uri)
                    stream.add(url)
                    sites.setdefault(_uri["host"], set()).add(url)
                    # TODO: IDEA: pushing this url into storage right now
                    # TODO: NO, we don't know why we want these urls for

                    for idx, (site, urls) in enumerate(sites.items()):
                        log.info("- #%s: %s: [%s] links", idx, site, len(urls))

                    # TODO: agp: REMOVE EDEBUG
                    if False and len(stream) > 3:
                        break

        stream = list(stream)
        context["collect__"] = stream
        return stream

    def direct_request(self, url):
        # --------------------------------------------
        # try to get the json-ld data using simple request
        # --------------------------------------------
        response = requests.get(url, headers=self.HEADERS)
        raw = response.content
        # with open("raw2.html", "wb") as file:
        #     file.write(raw)

        raw = raw.decode("utf-8")
        tree = etree.HTML(raw)
        sel = """//script[@type="application/ld+json"]"""
        results = tree.xpath(sel)

        stream = []
        for element in results:
            try:
                queue = []
                text = element.text
                data = json.loads(text)

                if isinstance(data, list):
                    queue.extend(data)
                else:
                    queue.append(data)

                for data in queue:
                    log.debug(pformat(data, indent=4))
                    _data = self.analyzer._process_ldjson(data)
                    stream.append(_data)

            except Exception as why:
                print(why)
                info = traceback.format_exception(*sys.exc_info())
                print("".join(info))
                foo = 1
        return stream

    async def _handler_select(self, page, action, context):
        item = context["item__"]
        value = await self._render_value(action, context)
        # log.debug("selecting: [%s] from [%s]", value, item)
        response = await item.select_option(value=value)
        if value in response:
            log.debug("OK: selected [%s]", response)
        else:
            log.warning("trying to select: [%s] but got [%s]", value, response)

        return response

    async def _handler_url(self, page, action, context):
        expression = "{{{{ url__ }}}}{{{{ {cmd__} }}}}"
        value = await self._render_value(action, context, expression)
        # response = await page.goto(value, wait_until="domcontentloaded")

        # check if url is relative or absolute
        _url = parse_uri(value)
        if not _url.get("xhost"):
            value = f"{page.url}/{value}"
            _url = parse_uri(value)
            while "//" in _url["path"]:
                _url["path"] = re.sub("//", "/", _url["path"])
            value = build_uri(**_url)

        response = await page.goto(value, timeout=15000)
        # await page.wait_for_load_state("networkidle", timeout=15000)
        return response

    async def _handler_value_old(self, page, action, context):
        elements = context["selector__"]
        interests = "tag", "type"
        for item in await elements.all():
            properties = await self._get_property(
                page, item, *interests, force_dict=True
            )
            context["item__"] = item
            context["properties__"] = properties
            for key, value in properties.items():
                context[f"{key}__"] = value

            handler = "_".join(
                [str(properties[key]) for key in interests if properties.get(key)]
            )
            handler = f"_handler_{handler}"
            _response = await getattr(self, handler)(page, action, context)

    async def _handler_value(self, page, action, context):
        """Handle items from last selector according to its properties"""
        response = []
        elements = context["selector__"]
        interests = "tag", "type"  # ordered, to build sub-handler name
        for item in await elements.all():
            # get the properties that the item may have
            # and we're interested in
            properties = await self._get_property(
                page, item, *interests, force_dict=True
            )
            # update the context
            context["item__"] = item
            context["properties__"] = properties
            for key, value in properties.items():
                context[f"{key}__"] = value

            # find the handler to deal with thii item
            handler = "_".join(
                [str(properties[key]) for key in interests if properties.get(key)]
            )
            handler = f"_handler_{handler}"
            if func := getattr(self, handler, None):
                log.debug("using: [%s]() for items: %s", handler, item)
                res = await func(page, action, context)
                response.append(res)
            else:
                log.warning(
                    "Ignoring Item: [%s] :[%s] session has not method [%s(...)]",
                    item,
                    self,
                    handler,
                )
        return response

    async def _handler_xpath_old(self, page, action, context):
        value = await self._render_value(action, context)

        for _ in range(30):
            await page.wait_for_load_state("networkidle")

            context["selector__"] = elements = await page.locator(value)
            n = await elements.count()
            if n > 0:
                break
            await page.wait_for_load_state("networkidle")
            await page.wait_for_load_state("domcontentloaded")

    async def _handler_xpath(self, page, action, context):
        """
        Select an item by xpath
        The value is got from context
        The key is taken from `cmd__` as usual
        """
        value = await self._render_value(action, context)

        for idx in range(30):
            log.debug("trying to get xpath: [%s] (%s attempt)", value, idx)
            await page.wait_for_load_state("networkidle")

            context["selector__"] = elements = await page.locator(value)
            n = await elements.count()
            if n > 0:
                log.debug("Ok: got [%s] elements", n)
                return elements
            await page.wait_for_load_state("networkidle")
            await page.wait_for_load_state("domcontentloaded")
        log.error("FAILED: to get [%s]", value)

    async def _direct_keyboard(self, ctx) -> bool:
        page = ctx["page"]
        info = ctx["info"]

        for key in info.get("keys", []):
            await page.keyboard.press(key)
            await asyncio.sleep(0.35 + random.random())
        foo = 1

    async def _handler_click(self, line, ctx) -> bool:
        element = ctx["element"]
        if await element.is_visible():  # element.is_visible():
            # time.sleep(0.5)

            page = ctx["page"]
            try:
                await element.click()
                # TODO: use a class method to control these events
                await page.wait_for_load_state("networkidle")
                await page.wait_for_load_state("domcontentloaded")
            except plw.TimeoutError:
                log.warning("timeout waiting for clicking on [%s]", element)
                return False
            except Exception:
                pass
            return True

        # else:
        #     log.debug("element: [%s] is not visible for clicking!", ctx["selector"])
        return False
