"""Main module."""

import json
import re
import sys

import traceback
from typing import Dict, List


from pydantic import ValidationError

from agptools.containers import exclude_dict, walk, flatten, Walk, build_paths, rebuild
from agptools.helpers import build_uri, DATE, FLOAT, NOTNULL, parse_uri, match_any
from agptools.web import html2text
from agptools.logs import logger

from syncmodels.definitions import KIND_KEY
from syncmodels.exceptions import NonRecoverable, NonRecoverableAuth, BadData
from syncmodels.model.schema_org import definitions


log = logger(__name__)


def parse_line(line, patterns):
    data = {}
    for _topic, (pattern, casting) in patterns.items():
        if m := re.search(pattern, line, re.I):
            d = m.groupdict()
            for _ in set(d).intersection(casting):
                d[_] = casting[_](d[_])
            data.update(d)
    return data


class XPathAnalyzer:
    """Handle Data"""

    REGEXP_PRICES = {
        "euro": [
            r"(?P<price>\d+([\.\,\s]\d+)?)\s*(?P<currency>€|\$)?",
            {
                "price": FLOAT,
            },
        ],
    }
    REGEXP_QPRICES = {
        "euro": [
            r"(?P<uprice>\d+([\.\,]\d+)?)\s*(?P<ucurrency>€|\$)?\s+/\s+(?P<uquantity>\d+)\s+(?P<uunit>\w+)",
            {
                "uprice": FLOAT,
                "quantity": FLOAT,
            },
        ],
    }
    REGEXP_QUANTITY = {
        "euro": [
            r"(?P<quantity>\d+([\.\,]\d+)?)\s+(?P<unit>(ml|g))",
            {
                "quantity": FLOAT,
            },
        ],
    }
    REGEXP_AVAILABLE = {
        "not_available": [
            r"(?i)(?P<not_available>(sin\s+unidades|agotado|no\sdisponible))",
            {
                "not_available": NOTNULL,
            },
        ],
        "availability": [
            r"(?i)(?P<availability>(Disponible|En\s+Stock|Comprar))",
            {
                "availability": NOTNULL,
            },
        ],
        "available_units": [
            r"(?i)(?P<availability>\d+)",
            {
                "availability": NOTNULL,
            },
        ],
    }

    DROP = {
        ".*": "None",
    }

    def _analyze_re(self, line, ctx) -> bool:
        info = ctx["info"]
        item = ctx["item"]
        found = False
        for _key, pattern in ctx["info"].get("regexp", {}).items():
            d = re.match(r"(?P<logic>\~)?(?P<key>\w+)", _key).groupdict()
            if isinstance(pattern, str):
                pattern = [pattern]
            for patt in pattern:
                # due yaml restructions on ESC chars
                patt = patt.replace("\\\\", "\\")

                if m := re.search(patt, line, re.I):
                    groups = m.groups()
                    if groups:
                        for value in m.groups():
                            if info.get("strip"):
                                value = re.sub(r"\s{1,}", " ", value)
                            item[d["key"]] = value
                    else:
                        item[d["key"]] = d["logic"] is None

                    d = m.groupdict()
                    if info.get("strip"):
                        d = {k: re.sub(r"\s{1,}", " ", v) for k, v in d.items()}
                    item.update(d)
                    found = True
        return found

    def _analyze_text(self, line, ctx) -> bool:
        line = line.strip()
        line = html2text(line)

        item = ctx["item"]
        info = ctx["info"]
        key = info.get("keyword", ctx["step"])
        if ctx["info"].get("append") and item.get(key):
            item[key] = "\n".join([item[key], line])
        else:
            item[key] = line

        if not info.get("strip"):
            pass
        else:
            item[key] = item[key].strip()

        return len(line) > 0

    def _analyze_json(self, line, ctx) -> bool:
        line = line.strip()
        line = html2text(line)
        try:
            data = json.loads(line)

            item = ctx["item"]
            info = ctx["info"]
            key = info.get("keyword", ctx["step"])
            if ctx["info"].get("append") and (holder := item.get(key)):
                if isinstance(holder, list):
                    holder.append(data)
                else:
                    item[key] = [holder, data]
            else:
                item[key] = data
            return True
        except Exception:
            pass
        return False

    def _analyze_table(self, line, ctx) -> bool:
        """
        ['Volumen (ML)\nfalse',
        'Efecto cabello\n\nAnti Encrespamiento, Hidratado, Reconstituyente',
        'Formato\n\nMascarilla',
        'Formulación\n\nVegano',
        'Ingrediente estrella\n\nÁcido Hialurónico, Coenzima Q10, Queratina',
        'Textura\n\nCremosa',
        'Tipo de cabello\n\nEncrespado',
        'Unidades\n\n1 ud.']

        """

        item = ctx["item"]
        info = ctx["info"]
        key = info.get("keyword", ctx["step"])

        line = line.strip()
        tokens = [_.strip() for _ in line.splitlines()]
        raw = "\n".join(tokens)

        idx = -1
        for idx, row in enumerate(raw.split("\n" * 4)):
            fields = row.split("\n" * 2)
            line = ": ".join(fields)

            if ctx["info"].get("append") and item.get(key):
                item[key] = "\n".join([item[key], line])
            else:
                item[key] = line

        return idx >= 0

    def _analyze_table_map(self, line, ctx) -> bool:
        """
        ['Volumen (ML)\nfalse',
        'Efecto cabello\n\nAnti Encrespamiento, Hidratado, Reconstituyente',
        'Formato\n\nMascarilla',
        'Formulación\n\nVegano',
        'Ingrediente estrella\n\nÁcido Hialurónico, Coenzima Q10, Queratina',
        'Textura\n\nCremosa',
        'Tipo de cabello\n\nEncrespado',
        'Unidades\n\n1 ud.']

        """

        item = ctx["item"]
        info = ctx["info"]
        key = info.get("keyword", ctx["step"])
        mapping = info.get("mapping", {})

        raw = line.strip()
        # tokens = [_.strip() for _ in line.splitlines()]
        # raw = "\n".join(tokens)

        idx = -1
        n = 0
        for idx, row in enumerate(raw.splitlines()):
            fields = row.split("\t")
            for pattern, key in mapping.items():
                if _m := re.search(pattern, fields[0]):
                    line = " ".join(fields[1:])
                    if ctx["info"].get("append") and item.get(key):
                        item[key] = "\n".join([item[key], line])
                    else:
                        item[key] = line
                    n += 1
                    break

        return n > 0

    def _analyze_attribute(self, line, ctx) -> bool:
        item = ctx["item"]
        info = ctx["info"]
        attributes = item["attributes"]

        found = 0
        rules = info.get("keyword", {})

        if isinstance(rules, list):
            for skey, pattern in rules:
                value = str(attributes.get(skey, ""))
                if m := re.match(pattern, value, re.I):
                    d = m.groupdict()
                    item.update(d)
                    found += len(d)
        elif isinstance(rules, dict):
            for tkey, skey in rules.items():
                item[tkey] = attributes.get(skey)
                found += 1

        return found > 0

    def _analyze_meta(self, line, ctx) -> bool:
        # TODO: tampodary skip meta info
        return False

    def _analyze_meta_old(self, line, ctx) -> bool:
        keyword = ctx.get("keyword") or {"name", "itemprop"}
        item = ctx["item"]
        info = ctx["info"]
        attributes = item["attributes"]
        found = 0
        if content := attributes.get("content"):
            if info.get("strip", True):
                content = content.strip()
            for name in keyword.intersection(attributes):
                # item[attributes[name]] = content
                item.setdefault(attributes[name], content)
                found += 1
        return found > 0

    def _analyze_price(self, line, ctx) -> bool:
        data = parse_line(line, self.REGEXP_PRICES)
        ctx["item"].update(data)
        return len(data) > 0

    def _analyze_uprice(self, line, ctx) -> bool:
        data = parse_line(line, self.REGEXP_QPRICES)
        ctx["item"].update(data)
        return len(data) > 0

    def _analyze_quantity(self, line, ctx) -> bool:
        data = parse_line(line, self.REGEXP_QUANTITY)
        ctx["item"].update(data)
        return len(data) > 0

    def _analyze_availability(self, line, ctx) -> bool:
        data = parse_line(line, self.REGEXP_AVAILABLE)
        if "not_available" in data:
            ctx["item"]["availability"] = "https://schema.org/OutOfStock"
        elif "availability" in data:
            ctx["item"]["availability"] = "https://schema.org/InStock"

        return len(data) > 0

    def _analyze_brand(self, line, ctx) -> bool:
        return self._analyze_text(line, ctx)

    def _analyze_ldjson_hide(self, line, ctx) -> bool:
        # TODO: this funcion has been temporary disabled
        return False

    def _analyze_ldjson(self, line, ctx) -> bool:
        # TODO: helper for loading json
        line = line.strip()
        line = html2text(line)
        try:
            data = json.loads(line)

            patterns = {
                r"gs\d+:(.*)": r"\1",
            }
            wdata = Walk(data)
            wdata.drop_empty()
            wdata.rewrite(patterns)
            stream = wdata.rebuild()
            if not isinstance(stream, list):
                stream = [stream]

            for data in stream:
                data = self._process_ldjson(data)
                if not data:
                    continue

                item = ctx["item"]
                info = ctx["info"]
                key = info.get("keyword") or data.get(KIND_KEY) or ctx["step"]
                if ctx["info"].get("append") and (holder := item.get(key)):
                    if isinstance(holder, list):
                        holder.append(data)
                    else:
                        item[key] = [holder, data]
                else:
                    item[key] = data
            return True
        except Exception as why:
            log.error(why)
            log.error("".join(traceback.format_exception(*sys.exc_info())))

        return False

    def _process_ldjson(self, data):
        if _type := data.get("@type"):
            # create a pydantic item from data
            model = definitions.load_model(_type)
            definitions.install_models(_type)

            if not model:
                error = {
                    "type": "missing",
                    "info": _type,
                }
                raise BadData(error)

            try:
                item = model(**data)
            except ValidationError as why:
                if _type in ("Product",):
                    # quarantine for pydantic improvements/investigation
                    error = {
                        "type": "quarantine",
                        "info": _type,
                    }
                    raise BadData(error)
                # ignore pydantic errors from other classes
                return

            _data = item.model_dump()
            _data = exclude_dict(_data, self.DROP)
            # check both model matches ... # TODO: agp: remove
            walk1 = dict(walk(data))
            walk2 = dict(walk(_data))

            for k1, v1 in walk1.items():
                if k1 and k1[-1] in ("@type", "@context", "@id"):
                    continue
                v2 = walk2.get(k1)
                if isinstance(v2, (int, float)):
                    if float(v1) != float(v2):
                        print(f"{k1}: {v1}, {v2}")
                        foo = 1
                    pass
                else:
                    if v1 != v2:
                        print(f"{k1}: {v1}, {v2}")
                        foo = 1

            if func := getattr(
                self,
                f"_ldjson_{_type.strip().lower()}",
                self._ldjson__default,
            ):
                _data = func(_data)

            _data[KIND_KEY] = _type
            return _data

    def _ldjson__default(self, data: Dict) -> Dict:
        return data

    def _ldjson_website(self, data: Dict) -> Dict:
        return data

    def _ldjson_product(self, data: Dict) -> Dict:
        return data
