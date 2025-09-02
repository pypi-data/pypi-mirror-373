import re
from datetime import datetime


def most_common(sample):
    stats = {}
    for value in sample:
        stats[value] = stats.get(value, 0) + 1

    stats = [(v, k) for k, v in stats.items()]
    stats.sort(reverse=True)
    return stats


class iSchema:

    MONOTONIC_CANDIDATES = [
        r"ts",
        r"timestamp",
        r"date",
        r".*modified.*",
        r".*created.*",
        r"entity_ts",
    ]

    def guess_schema(self, names, data, **kw):
        """
        info
        ({'date': {'name': 'date',
                   'type': 'TEXT',
                   'notnull': 0,
                   'default': None,
                   'pk': 0,
                   'hidden': 0},
          'value': {'name': 'value',
                    'type': 'REAL',
                    'notnull': 0,
                    'default': None,
                    'pk': 0,
                    'hidden': 0}},
         [{'name': 'date',
           'type': 'TEXT',
           'notnull': 0,
           'default': None,
           'pk': 0,
           'hidden': 0},
          {'name': 'value',
           'type': 'REAL',
           'notnull': 0,
           'default': None,
           'pk': 0,
           'hidden': 0}],
         'date')

        """
        # T
        d_fields = {}
        for row in data:
            for i, value in enumerate(row):
                name = names[i]
                type_ = value.__class__
                d_fields.setdefault(name, []).append(type_)

        for key, sample in d_fields.items():
            d_fields[key] = most_common(sample)[0][1]

        types = [d_fields[key] for key in names]

        def best():
            # try to find a column that match any of the candidate patterns
            for pattern in self.MONOTONIC_CANDIDATES:
                for value in d_fields:
                    if re.match(pattern, value):
                        return value
            # direct search has failed
            # try to guess the column by value class
            for key, klass in d_fields.items():
                if issubclass(klass, (datetime,)):
                    return key

        monotonic_since_key = best()
        return names, types, d_fields, monotonic_since_key


class StructShema:
    def __init__(self, names, types, d_fields, monotonic_since_key, struct):
        self.names = names
        self.types = types
        self.d_fields = d_fields
        self.monotonic_since_key = monotonic_since_key
        self.struct = struct
