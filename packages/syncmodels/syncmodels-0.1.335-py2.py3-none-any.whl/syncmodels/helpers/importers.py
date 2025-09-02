import os
import re
from typing import Dict, Any
from datetime import datetime
import pandas as pd


from agptools.files import fileiter
from agptools.helpers import DATE
from agptools.containers import overlap, rebuild, walk


class JSONVerter:
    @classmethod
    def to_json(cls, params: Dict) -> Dict:
        _env = rebuild([(k, cls._to_json(v)) for k, v in walk(params)])
        return _env

    @classmethod
    def from_json(cls, params: Dict) -> Dict:
        _env = rebuild([(k, cls._from_json(v)) for k, v in walk(params)])
        return _env

    @classmethod
    def _to_json(cls, value: Any) -> Any:
        if isinstance(value, datetime):
            value = value.strftime("%FT%T.%f%Z")
        return value

    @classmethod
    def _from_json(cls, value: Any) -> Any:
        for func in [
            DATE,
        ]:
            _value = func(value)
            if _value != value:
                value = _value
                break
        return value


class ExcelImporter:
    def __init__(self):
        pass

    @classmethod
    def load(
        cls,
        path=".",
        file_pattern=None,
        col_pattern=None,
        value_pattern=None,
    ):

        file_pattern = file_pattern or [r"(?P<name>.*)(?P<ext>\.(csv|xls|xlsx))$"]

        if isinstance(path, str):
            path = [path]

        if isinstance(file_pattern, str):
            file_pattern = [file_pattern]

        col_pattern = col_pattern or [r"(?P<name>id)"]
        if isinstance(col_pattern, str):
            col_pattern = [col_pattern]

        value_pattern = value_pattern or []
        if isinstance(value_pattern, str):
            value_pattern = [value_pattern]

        def find_idx(df):
            _col = df.columns
            for _, row in df.iterrows():
                for _idx, _pattern in enumerate(col_pattern):
                    name = _col[_idx]
                    if re.match(_pattern, name):
                        return _idx, name
                break
            return -1, ""

        def find_idx_from(data):
            for key, value in data.items():
                _value = str(value).strip()
                # TODO: remove hack due data sour error
                _value = _value.replace("IKBS", "IBKS")
                for _pattern in value_pattern:
                    if re.match(_pattern, _value):
                        return key, value
            return -1, ""

        db = {}
        N = 0
        for top in path:
            top = os.path.abspath(top)
            for pat in file_pattern:
                for path, info in fileiter(
                    top=top, regexp=pat, info="d", relative=True
                ):
                    df = pd.read_excel(path)
                    df = df.fillna("")
                    # find the columns that match the index pattern
                    idx, idx_name = find_idx(df)

                    _col = df.columns
                    n = 0
                    for _idx, row in df.iterrows():
                        data = {k: row[k] for k in _col}
                        if not idx_name:
                            _key, uid = find_idx_from(data)
                        else:
                            uid = data[idx_name]

                        if uid:
                            # TODO: remove
                            uid = uid.replace("IKBS", "IBKS")
                            n += 1
                            # data.setdefault('uid', uid)
                            current = db.setdefault(uid, {})
                            overlap(current, data, overwrite=True)

                        else:
                            print(f"warning: can't find uid in {data}")
                            foo = 1
                    print(f"Importing [{n:3}] beacons from {path}")
                    N += n
        assert db
        print(f"Total: {len(db)} beacons found")
        return db
