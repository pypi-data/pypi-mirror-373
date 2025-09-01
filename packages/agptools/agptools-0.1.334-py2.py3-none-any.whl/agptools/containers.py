"""Helpers for dealing with containers.

Container Operations
-----------------------

- [x] smart context updating.


Special Containers
-----------------------

- [x] sets that can delete object across all same containers.

"""

import asyncio
import pickle
import os
import types
import time
import re
import json
import yaml
from enum import Enum
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Iterable, Union, Dict, Any, List
from weakref import WeakValueDictionary
import xml.etree.ElementTree as ET

from lxml import etree

from glom import glom, assign, T
from glom.core import TType

# import pandas as pd
# import numpy as np

# from csv import QUOTE_MINIMAL, QUOTE_NONNUMERIC, QUOTE_ALL

# ----------------------------------
# Container Operations
# ----------------------------------


TYPES = []
for k in types.__all__:
    klass = getattr(types, k)
    try:
        if isinstance(TYPES, klass):
            pass
        TYPES.append(klass)
    except Exception as why:
        pass
TYPES = tuple(TYPES)


def update_context(context, *args, **kw):
    """Update several data into a *holder* context.
    args can be anything that we can obtain a *dict* alike object.
    """
    __avoid_nulls__ = kw.pop("__avoid_nulls__", True)

    if __avoid_nulls__:
        for k, v in kw.items():
            if v is not None:
                context[k] = v
    else:
        context.update(kw)

    for item in args:
        if isinstance(item, dict):
            d = item
        elif hasattr(item, "as_dict"):
            d = item.as_dict()
        elif hasattr(item, "__dict__"):
            d = item.__dict__
        elif hasattr(item, "__getstate__"):
            d = item.__getstate__()
        else:
            d = dict()
            for k in dir(item):
                if k.startswith("_"):
                    continue
                v = getattr(item, k)
                if v.__class__.__name__ == "type" or isinstance(
                    v, TYPES
                ):  # (types.FunctionType, types.MethodType, types.MethodWrapperType, types.BuiltinFunctionType)):
                    continue
                d[k] = v

        if __avoid_nulls__:
            for k, v in d.items():
                if v is not None:
                    context[k] = v
        else:
            context.update(d)


def extract_params(data, specs):
    r"""Extract {key: values} pairs in a data structure following
    some specs

    Example:

    specs = [
        {
            'value': ['(?is)value$', '(.*?\s+)?(?P<value>.*)\s*$'],
            'key': ['(?is).*name$', '(.*?\s+)?(?P<value>.*)\s*$'],
        },
    ]

    info
    {'language': 'es-ES',
     'category': 'Met',
     'event': 'Aviso de tormentas de nivel amarillo',
     'urgency': 'Future',
     'severity': 'Moderate',
     'certainty': 'Likely',
     'eventCode': {'valueName': 'AEMET-Meteoalerta fenomeno',
                   'value': 'TO;Tormentas'},
     'effective': '2024-09-07T11:57:13+02:00',
     'senderName': 'AEMET. Agencia Estatal de Meteorología',
     'headline': 'Aviso de tormentas de nivel amarillo. Ronda',
     'description': 'Rachas muy fuertes como fenómeno más significativo.',
     'web': 'https://www.aemet.es/es/eltiempo/prediccion/avisos',
     'parameter': [{'valueName': 'AEMET-Meteoalerta nivel', 'value': 'amarillo'},
                   {'valueName': 'AEMET-Meteoalerta parametro',
                    'value': 'TO;Tormentas;'},
                   {'valueName': 'AEMET-Meteoalerta probabilidad',
                    'value': '40%-70%'}],
     'area': {'areaDesc': 'Ronda',
              'polygon': '36.5,-5.56 36.51,-5.6 36.54,-5.61 36.55,-5.57 '
                         '36.53,-5.52 36.59,-5.46 36.62,-5.45 36.61,-5.44 '
                         '36.63,-5.38 36.68,-5.33 36.72,-5.32 36.78,-5.29 '
                         '36.79,-5.32 36.82,-5.34 36.87,-5.3 36.88,-5.28 '
                         '36.86,-5.23 36.84,-5.22 36.82,-5.17 36.84,-5.13 '
                         '36.92,-5.09 36.89,-5.05 36.88,-4.98 36.93,-4.88 '
                         '36.94,-4.83 36.92,-4.77 36.86,-4.78 36.87,-4.82 '
                         '36.85,-4.89 36.81,-4.88 36.77,-4.9 36.76,-4.95 '
                         '36.73,-4.99 36.67,-5.03 36.61,-5.06 36.54,-5.14 '
                         '36.54,-5.16 36.48,-5.21 36.52,-5.23 36.52,-5.27 '
                         '36.49,-5.29 36.43,-5.35 36.47,-5.39 36.53,-5.43 '
                         '36.54,-5.49 36.5,-5.52 36.5,-5.56',
              'area_code': {'valueName': 'AEMET-Meteoalerta zona',
                          'value': '612902'}}}


    get_params(info, specs)
    {'fenomeno': 'TO;Tormentas',
     'nivel': 'amarillo',
     'parametro': 'TO;Tormentas;',
     'probabilidad': '40%-70%',
     'zona': '612902'}

    """
    result = {}
    partial = {}
    for key, value in walk(data):
        # allocate partial definition in a holder
        if len(key) < 2:
            continue
        pkey, pname = key[:-1], key[-1]
        if not isinstance(pname, str):
            continue

        for spec in specs:
            for what, [pattern, extractor] in spec.items():
                if re.match(pattern, pname):
                    if m := re.match(extractor, value):
                        value = m.groupdict().get("value", value)

                        holder = partial.setdefault(pkey, {})
                        holder[what] = value
                        if len(holder) == len(spec):  # is completed
                            result[holder["key"]] = holder["value"]
                            partial.pop(pkey)

    return result


def collect(item, selectors, max_item=-1, flat=False, cast=None):
    for patt in selectors:
        if isinstance(patt, str):
            for key in patt.split("|"):
                done = False
                selectors = [
                    key,
                    f"*.{key}",
                    f"*.*.{key}",
                ]
                for selector in selectors:
                    try:
                        values = glom(item, selector)
                        if isinstance(values, list):
                            values = values
                        elif isinstance(values, dict):
                            values = [values]
                        else:
                            values = [values]

                        for value in values:
                            if flat and isinstance(value, (list, dict, tuple)):
                                _values = list(flatten(value))
                            else:
                                _values = [value]
                            for _value in _values:
                                if cast:
                                    _value = cast(_value)

                                yield patt, key, _value
                                # result.append((key, _value))
                            done = True
                        if done:
                            max_item -= 1
                            break
                    except Exception as why:
                        pass
        else:
            raise NotImplemented()
            # try:
            #     yield from glom(item, patt)
            #     max_item -= 1
            #     break
            # except Exception as why:
            #     pass
        if max_item == 0:
            break


def filter_list(universe: List[str], patterns: List[str]):
    # apply filtering
    # assert isinstance(patterns, list)
    if patterns:
        for value in universe:
            raw = str(value)
            for pat in patterns:
                if re.search(pat, raw, re.M | re.DOTALL):
                    yield value
                    break
    else:
        yield from universe


def exclude_dict(data, patterns):

    stream = []

    if isinstance(patterns, str):
        patterns = [patterns]

    if isinstance(patterns, list):
        for key, value in walk(data):
            _key = str(key)
            _value = str(value)

            for patt in patterns:
                if re.match(patt, _key) or re.match(patt, _value):
                    break
            else:
                # new[key] = value
                stream.append((key, value))

    elif isinstance(patterns, dict):
        for key, value in walk(data):
            _key = str(key)
            _value = str(value)
            for kpatt, vpatt in patterns.items():
                if re.match(kpatt, _key):
                    if re.match(vpatt, _value):
                        break
            else:
                stream.append((key, value))

    new = rebuild(stream)
    return new


def exclude_dict_old(data, patterns):

    if isinstance(patterns, str):
        patterns = [patterns]

    if isinstance(patterns, list):
        new = {}
        for key, value in data.items():
            _value = str(value)

            for patt in patterns:
                if re.match(patt, key) or re.match(patt, _value):
                    break
            else:
                new[key] = value

    elif isinstance(patterns, dict):
        new = {}
        for key, value in data.items():
            _value = str(value)
            for kpatt, vpatt in patterns.items():
                if re.match(kpatt, key):
                    if re.match(vpatt, _value):
                        break
            else:
                new[key] = value

    return new


def filter_dict(universe: List[Dict], patterns: Union[List[str], Dict[str, str]]):
    # apply filtering
    if isinstance(patterns, dict):
        for data in universe:
            for _key, _value in patterns.items():
                value = data.get(_key, "")
                if re.search(_value, value, re.M | re.DOTALL | re.I):
                    break
            else:
                # ignore this task
                continue
            yield data
    elif isinstance(patterns, (list, tuple)):

        patterns = patterns or []
        for data in universe:
            all_values = "\n".join([str(_) for _ in data.values()])
            for pat in patterns:
                if m := re.match(r"(?P<key>[^\s:]+)\s*:\s*(?P<value>.*)$", pat):
                    key_patterm, value_pattern = m.groups()
                    _values = [
                        str(data[_key])
                        for _key in data
                        if re.match(key_patterm, _key, re.I)
                    ]
                    values = [
                        _value for _value in _values if re.search(value_pattern, _value)
                    ]
                    if values:
                        break
                else:
                    if re.search(pat, all_values, re.M | re.DOTALL | re.I):
                        break
            else:
                # ignore this task
                continue

            yield data


def json_compatible(data):
    result = {}
    for k, v in data.items():
        # check that any task can se json serializable
        # so it can be stored as json in the DB
        try:
            _ = json.dumps({k: v})
        except Exception as why:
            continue
        result[k] = v
    return result


def json_compatible_old(data, **kw):
    result = []
    for row in walk(data, **kw):
        try:
            _ = json.dumps(row[1])
        except Exception as why:
            continue
        result.append(row)
    result = rebuild(result)
    return result


def convert_container(item, *klasses):
    """Try to convert a text into more fine grain object:

    when klass is provided, tries as much to convert to klass

    - list
    - dict
    - boolean
    - integer
    - etc

    # TODO: improve with regexp and dict of candidates.
    """
    klasses = list(klasses)
    while klasses:
        klass = klasses.pop(0)
        if isinstance(klass, (list, tuple)):
            klasses = [k for k in klass] + klasses
            continue

        if klass in (list,):
            item = [convert_container(t.strip(), *klasses) for t in item.split(",")]

        if klass in (dict,):
            item = [convert_container(t.strip(), *klasses) for t in item.split(",")]

        if klass:
            item = klass(item)

    return item


def list_of(thing, *klasses):
    if not isinstance(thing, list):
        thing = [thing]

    thing = [item for item in thing if isinstance(item, klasses)]
    return thing


# Pandas Reading Engines
# (from )
# _engines: Mapping[str, Any] = {
# "xlrd": XlrdReader,
# "openpyxl": OpenpyxlReader,
# "odf": ODFReader,
# "pyxlsb": PyxlsbReader,
# }

DF_KEYWORDS = {
    ".ods": {"engine": "odf", "format": "excel"},
    ".xls": {"engine": "xlrd", "format": "excel"},
    ".xlsx": {"engine": "openpyxl", "format": "excel"},
    ".csv": {"format": "csv"},
    ".pickle": {"format": "pickle"},
}
# ---------------------------------------------
# Loaders
# ---------------------------------------------
# opener = {
# ".xls": pd.read_excel,
# ".xlsx": pd.read_excel,
# ".csv": pd.read_csv,
# ".pickle": pd.read_pickle,
# }

SEP = r"//"


def build_paths(data):
    # return {"/".join([str(_) for _ in key]): str(value) for (key, value) in walk(data)}
    return {SEP.join([str(_) for _ in key]): value for (key, value) in walk(data)}


def retrieve(
    key,
    builder=None,
    *args,
    _storage_=".storage",
    _force_=False,
    _save_=True,
    _csv_review=True,
    **ctx,
):
    # TODO: remove if not used due `pandas` dependency
    path = f"{_storage_}/{key}.pickle"
    if _force_ or not os.path.exists(path):
        assert builder is not None, "you must set a builder when data is missing"
        response = builder(*args, **ctx)
        if _save_:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            pickle.dump(response, open(path, "wb"))
            if _csv_review:
                if isinstance(response, (pd.DataFrame, pd.Series)):
                    path = f"{_storage_}/{key}.csv"
                    response.to_csv(path)
                elif isinstance(response, dict):
                    for k, value in response.items():
                        if isinstance(value, (pd.DataFrame, pd.Series)):
                            path = f"{_storage_}/{key}-{k}.csv"
                            value.to_csv(path)
                        else:
                            path = f"{_storage_}/{key}-{k}.yml"
                            yaml.dump(
                                value,
                                open(path, "w"),
                                default_flow_style=False,
                            )
                else:
                    path = f"{_storage_}/{key}.yml"
                    yaml.dump(response, open(path, "w"), default_flow_style=False)
    else:
        response = pickle.load(open(path, "rb"))

    ctx[key] = response
    return response


DF_REGEXP = r"(?P<format>\.(?P<ext>(csv|pickle|xls|xlsx|ods)))(\.(?P<cmp>xz))?$"


def opendf(path, **kw):
    if os.path.exists(path):
        m = re.search(DF_REGEXP, path)
        if m:
            d = m.groupdict()

            soft(kw, **DF_KEYWORDS.get(d["format"]))
            fmt = kw.pop("format")
            loader = getattr(pd, f"read_{fmt}", None)
            if loader:
                t0 = time.time()
                try:
                    df = loader(path, **kw)
                except:
                    df = None
                t1 = time.time()
                elapsed = t1 - t0

                # print(f"read {path}: {elapsed:0.3f} secs")
                return df


def savedf(df, path, ext=None):
    _base, _ext = os.path.splitext(path)
    ext = ext or _ext
    path = "".join([_base, ext])

    default = {"format": ext[1:]}
    kw = DF_KEYWORDS.get(ext) or default
    saver = getattr(df, f"to_{kw['format']}", None)
    if saver:
        kw = dict(kw)
        kw.pop("format")
        t0 = time.time()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        df = saver(path, **kw)
        t1 = time.time()
        elapsed = t1 - t0

        print(f"save {path}: {elapsed:0.3f} secs")
        return df


def dataframe_iter(
    top,
    regexp,
    sanitize=[],
    sanitize_folder="sanitized",
    out_format=".pickle",
    dtypes=None,
    **kw,
):
    top = expandpath(top)
    sanitize_folder = expandpath(sanitize_folder)
    dtypes = dtypes or str

    for path, d in fileiter(top, ".", info="s", relative=False):
        m = re.search(regexp, path, re.I | re.DOTALL)
        if not m:
            continue

        d.update(m.groupdict())

        if os.path.splitext(path)[-1] == out_format:
            sane_path = path
        else:
            sane_name = sanitize_folder + "".join(path.split(top)[1:])
            sane_name = os.path.splitext(sane_name)[0]
            sane_path = sane_name + out_format

        updated = (
            os.path.exists(sane_path)
            and (os.stat(sane_path).st_size > 0)
            and os.stat(sane_path).st_mtime
            or 0
        )
        # select which one we need to load
        if updated < d["mtime"]:
            df = opendf(path)
            if df is None:
                continue
            for func in sanitize:
                print(f"{str(df.shape):12}: {func.__name__:20} : {path}")
                df = func(df, **kw)
                # if result is not None:
                # for name, partial in result.items():
                # pickle.dump(partial, open(os.path.join(normalized, name + '.pickle'), 'wb'))

            # write csv (human inspection) and fast pickle format
            formats = set([out_format, ".csv"])
            for ext in formats:
                writer = getattr(df, f"to{ext.replace('.', '_')}", None)
                if writer:
                    aux = list(os.path.splitext(sane_path))
                    aux[-1] = ext
                    aux = "".join(aux)
                    os.makedirs(os.path.dirname(aux), exist_ok=True)
                    writer(aux)
                else:
                    raise RuntimeError(
                        f"Don't know how to write '{out_format}' dataframes"
                    )
        else:
            df = opendf(sane_path)

        soft(d, sane_path=sane_path, path=path)
        df.attrs = d  # the right place to store metadata
        yield df
    pass


def load_data(
    regexp,
    normalize_func=[],
    top=".",
    inputs="inputs",
    outputs="",
    normalized=".storage",
    out_format=".pickle",
    **kw,
):
    """Load a set of (normalized) dataframes.

    - search dataframes from 'inputs' folder.
    - locate if a normalized version exists and is not outdated.
    - create a normalized version is needed.

    """
    data = {}
    inputs = os.path.join(top, inputs)
    normalized = os.path.join(top, normalized)

    for path, d in fileiter(inputs, regexp=regexp, info="s", relative=False):
        if re.search(r"lock.*#$", path):
            continue  #: excel / libreoffice lock

        # print(f"IN : {path:60}: {d['mtime']}")
        relpath = path.split(inputs)[-1].strip("/")
        # relpath = path.split(inputs)
        # relpath.pop(0)
        # relpath = "".join(relpath)

        norm_path = os.path.join(normalized, relpath)
        base, ext = os.path.splitext(norm_path)
        norm_path = "".join([base, out_format])
        updated = (
            os.path.exists(norm_path)
            and (os.stat(norm_path).st_size > 0)
            and os.stat(norm_path).st_mtime
            or 0
        )
        # print(f"OUT: {norm_path:60}: {updated}")

        if updated < d["mtime"]:
            df = opendf(path)
            if df is None:
                continue
            for func in normalize_func:
                print(f"{str(df.shape):12}: {func.__name__:20} : {path}")
                df = func(df, **kw)
                # if result is not None:
                # for name, partial in result.items():
                # pickle.dump(partial, open(os.path.join(normalized, name + '.pickle'), 'wb'))

            writer = getattr(df, f"to{out_format.replace('.', '_')}", None)
            if writer:
                os.makedirs(os.path.dirname(norm_path), exist_ok=True)
                writer(norm_path, quoting=QUOTE_ALL)
            else:
                raise RuntimeError(f"Don't know how to write '{out_format}' dataframes")
        else:
            df = opendf(norm_path)

        key = os.path.splitext(relpath)[0]
        data[key] = df
    return data


def join(dfs, drop_empy=False, drop_duplicates=False):
    """Join many dataframes in a single one"""
    df = pd.concat(dfs)
    drop_duplicates and df.drop_duplicates(inplace=True)
    drop_empy and df.replace("", np.nan, inplace=True)
    drop_empy and df.dropna(inplace=True)
    return df


def rename_columns(data, mapping):
    # delete target columns if they exists
    drop_columns(data, mapping.values())
    # rename (safe placeholder)
    knife = set(mapping)
    for key, df in data.items():
        map_ = {k: mapping[k] for k in knife.intersection(df.columns)}
        df.rename(columns=map_, inplace=True)


def drop_columns(data, columns):
    knife = set(columns)
    for key, df in data.items():
        df.drop(columns=knife.intersection(df.columns), inplace=True)


def keep_columns(data, columns):
    knife = set(columns)
    for key, df in data.items():
        df.drop(columns=df.columns.difference(knife), inplace=True)


def load_dataframes(kind, folder="", top=".", relative=False):
    """Load a set of dataframes from a folder."""

    used = set()
    data = {}
    regexp = f"(?P<kind>{kind})" + r"(?P<ext>\.[^.]+)$"
    for path, d in fileiter(os.path.join(top, folder), regexp=regexp, info="d"):
        abspath = os.path.abspath(path)
        if abspath in used:
            continue
        used.add(abspath)

        df = opendf(path)
        if relative:
            path = path.split(top)[-1]
        data[path] = df
        data[os.path.basename(d["kind"])] = df
    return data


TRX_MAP = {
    "á": "a",
    "é": "e",
    "í": "i",
    "ó": "o",
    "ú": "u",
    "Á": "A",
    "É": "E",
    "Í": "I",
    "Ó": "O",
    "Ú": "U",
}

TRX_TABLE = str.maketrans(TRX_MAP)


def rename_columns_old(names, mapping=None):
    """Rename columns:

    - covert to lower case
    - replace '.' by '_'
    - remove [es_ES] tails
    - covert to lower case

    """
    map_ = {}
    mapping = mapping or {}

    for org in names:
        key = org.translate(TRX_TABLE).lower().replace(" ", "_")
        name = mapping.get(key, org)
        name = re.sub(r"\[es_ES\]$", "", name)
        name = re.sub(r"\.", "_", name)
        name = re.sub(r"\s", "_", name)
        name = name.translate(TRX_TABLE).lower()
        map_[org] = name

    return map_


def purge(holder, older=None, max_len=None):
    """Purge a dict by age or max length."""
    if isinstance(older, datetime):
        older = older.timestamp()

    # delete by date
    for key in list(holder.keys()):
        if isinstance(key, datetime):
            k = key.timestamp()
        else:
            k = key
        if k < older:
            holder.pop(key)

    # delete by size
    keys = list(holder.keys())
    keys.sort()
    for key in keys[max_len:]:
        holder.pop(key)


def sitems(d, exclude=None):
    exclude = exclude or []
    keys = list(d)
    keys.sort()
    for k in keys:
        for pattern in exclude:
            if re.match(pattern, k):
                break
        else:
            yield k, d[k]


# -----------------------------------------------------------
# Base Item class
# -----------------------------------------------------------


class Item:
    """Just a container to Store data"""

    __hash_exclude__ = []

    def __getkeys__(self):
        keys = []
        for klass in self.__class__.__mro__:
            keys.extend(getattr(klass, "__slots__", []))
        return keys

    def __getstate__(self):
        state = dict([(k, getattr(self, k, None)) for k in self.__getkeys__()])
        state["<klass>"] = self.__class__.__name__
        return state

    def __setstate__(self, state):
        klass = state.pop("<klass>", None)
        assert klass in (self.__class__.__name__, None)
        for k, v in state.items():
            setattr(self, k, v)

    def __str__(self):
        keys = self.__getkeys__()
        fields = ", ".join([f"{key}: {getattr(self, key, None)}" for key in keys])
        return f"{self.__class__.__name__}: {fields}"

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, key):
        return getattr(self, self.__getkeys__()[key])

    def __setitem__(self, key, value):
        return setattr(self, self.__getkeys__()[key], value)

    def aslist(self, string=True):
        keys = self.__getkeys__()
        if string:
            return [f"{getattr(self, key, None)}" for key in keys]
        return [getattr(self, key, None) for key in keys]

    def asdict(self, string=True):
        keys = self.__getkeys__()
        if string:
            return dict([(key, f"{getattr(self, key, None)}") for key in keys])
        return dict([(key, getattr(self, key, None)) for key in keys])

    def soft(self, **kw):
        for k, v in kw.items():
            if getattr(self, k, None) is None:
                setattr(self, k, v)

    def hash(self):
        state = self.__getstate__()
        for k in self.__hash_exclude__:
            state.pop(k)
        m = hashlib.md5(bytes(str(state), "utf-8"))
        return m.hexdigest()

    def clone(self, **kw):
        """Clone the object allowing an update"""
        new = self.__class__()  # default constructor must be defined
        for k in self.__getkeys__():
            setattr(new, k, kw.get(k, getattr(self, k)))
        return new


# ----------------------------------
# Type definitions
# ----------------------------------

BASIC_TYPES = tuple(
    [
        type(None),
        int,
        float,
        str,
        bytes,
    ]
)
DATETIME_TYPES = tuple([datetime, relativedelta])
CONTAINERS_TYPES = tuple([dict, list, tuple, set])

BASIC_TYPES_EXT = tuple(
    list(BASIC_TYPES) + list(CONTAINERS_TYPES) + list(DATETIME_TYPES) + [Item]
)
ITERATOR_TYPES = tuple(
    [type({}.keys()), type({}.values()), type({}.items())] + list(CONTAINERS_TYPES)
)
GENERATOR_TYPES = tuple(
    [
        types.GeneratorType,
    ]
)
ITERATOR_TYPES_EXT = tuple(list(ITERATOR_TYPES) + list(GENERATOR_TYPES))
CALLEABLE_TYPES = tuple([types.MethodType, types.FunctionType, types.LambdaType])


def index(stream, value):
    try:
        idx = stream.index(value)
        return idx
    except IndexError:
        pass
    for idx, v in stream:
        if re.match(value, v):
            return idx


def soft(target, source):
    """Update only when target key does not exits."""
    for k, v in source.items():
        target.setdefault(k, v)
    return target


def overlap(target, source, overwrite=False):
    """Update target when source has meaninful data"""
    for k, v in source.items():
        if (overwrite or target.get(k) in (None, "")) and v not in (
            None,
            "",
        ):
            target[k] = v
            # target.setdefault(k, v)
    return target


def complete_on(holder, key, values, where="begin"):
    original = holder.get(key) or []
    holder[key] = complete(original, values, where)


def complete(target, values, where="begin"):
    if isinstance(target, str):
        # target = re.findall(r"\w+", target) # don't use, will break regexp i.e. \d+
        target = [_.strip() for _ in target.split(",")]

    if where in ("begin", "middle"):
        stream = reversed(values)
    else:
        stream = values

    for _ in stream:
        if _ not in target:
            if where in ("begin,"):
                target.insert(0, _)
            elif where in ("middle",):
                pos = (len(target) + 1) // 2
                target.insert(pos, _)
            elif where in ("end",):
                target.append(_)
            else:
                target.append(_)
    return target


def compose(target, source, overwrite=False):
    """Update target when source has meaningful data"""
    target = dict(target)
    for k, v in source.items():
        if (overwrite or target.get(k) in (None, "")) and v not in (
            None,
            "",
        ):
            target[k] = v
            # target.setdefault(k, v)
    return target


def combine_uri(*uris):
    """Update target when source has meaningful data"""
    target = dict(uris[0])
    for source in uris[1:]:
        for k, v0 in target.items():
            v1 = source.get(k)
            if k in ("_path", "path", "xpath", "query") and v0 is not None:
                v1 = v1 or ""
                if v0:
                    v1 = v1.split(v0)[-1]
                v0 += v1
            elif k in ("_path",) and v1:
                v0 = f"{v0}/{v1}"
            # elif k in ("query_",):
            #     v0.update(v1 or {})
            elif k in ("id", "basename", "table", "fragment") and v1:
                v0 = v1
            elif not v0:
                v0 = v1

            # try to render when is a string
            if isinstance(v0, str):
                try:
                    v0 = v0.format_map(source)
                except KeyError:
                    pass
                except Exception as why:  # pragma: nocover
                    print(f"Error combine_uri: {why}")
                    raise
            target[k] = v0

    return target


# ----------------------------------
# Expansions
# ----------------------------------
REG_EXPAND_EXPRESSION = r"""(?imsx)
(?P<bound>\{
  (?P<exp>.*?)
 \}
)
(?P<tail>.*)$
"""


def expand_expression(data, expression):
    "TBD"
    # use 2 stages to avoid infinite recursion expression hack
    # i.e an expression that will render another expression
    # that evaluated give the 1st one
    results = {}
    string = expression
    m = True
    while m:
        m = re.search(REG_EXPAND_EXPRESSION, string)
        if m:
            d = m.groupdict()
            try:
                res = glom(data, d["exp"])
                results[d["bound"]] = res
                string = d["tail"]
            except Exception as why:  # pragma: nocover
                pass
    for bound, exp in results.items():
        expression = expression.replace(bound, exp)

    return expression


# ----------------------------------
# Special Containers
# ----------------------------------


class xset(set):
    """Smart Set that keep connection with other xset for
    manage same objects placed inside the xset *mesh*.
    """

    universe = WeakValueDictionary()

    def __init__(self, iterator=None, register=False):
        super().__init__(iterator)
        if register:
            # register xset container
            self.universe[id(self)] = self

    def difference_update(self, *args):
        """Remove items from ALL registered xset containers"""
        for container in self.universe.values():
            foo = container.intersection(*args)
            if foo:
                foo = foo
            set.difference_update(container, *args)

    def add(self, *args):
        """Replace an instance by other in ALL registered groups.
        When an object class object with the same attribute <key>
        is found, then is replaced by the new one (id() must be different)
        """
        key = "uri"

        def _replace_in(container, item):
            id1 = id(item)
            key1 = getattr(item, key, None)

            for current in list(container):
                if id(current) == id1:
                    continue
                key2 = getattr(current, key, None)
                if not key2:
                    continue
                if key1 == key2:  # replace object
                    container.remove(current)
                    set.add(container, item)
                    return True
            set.add(container, item)
            return False

        for item in args:
            if _replace_in(self, item):
                for container in self.universe.values():
                    _replace_in(container, item)

    @staticmethod
    def _explore(node, visited=None):
        """Iterate for xset containeres across parent nested structure"""
        visited = list() if visited is None else visited
        # extr = ('__iter__', '__dict__', 'items')
        extr = "node.__dict__.values()"
        items = [
            item
            for item in node.__dict__.values()
            if isinstance(item, xset) and item not in visited
        ]

        print(f"= {node}{'='*40}")
        for item in items:
            if isinstance(item, xset):
                print(f" - {item}")
                visited.append(item)
                xset._explore(item, visited)

        return visited


def build_set(iterator=None):
    "Build a Set from object or object iterators"
    if isinstance(iterator, set):
        return iterator

    if (
        not hasattr(iterator, "__len__")
        or isinstance(iterator, str)
        or isinstance(iterator, type)
    ):
        if iterator:
            iterator = [iterator]
        else:
            iterator = []
    return set(iterator)


def build_xset(iterator=None, register=False, linear=False):
    "Build a xset from object or object iterators"
    if isinstance(iterator, set):
        return iterator

    if not hasattr(iterator, "__len__") or isinstance(iterator, str):
        if iterator:
            iterator = [iterator]
        else:
            iterator = []
    if linear:
        iterator = linear_containers(iterator)
    return xset(iterator, register)


def build_dict(data, keys):
    result = {}
    for key in keys or []:
        if key in data:
            result[key] = data[key]
        else:
            # TODO: REVIEW: geojson doesn't share sort_keys
            # log.warning(
            #     "sort key [%s] is not present in data? (looks like human set by hand",
            #     key,
            # )
            pass
    return result


def linear_containers(*iterable):
    """Join all elements from iterables.
    TODO: use itertools.
    """
    remain = list(iterable)
    while remain:
        item = remain.pop(0)
        if isinstance(item, (dict, list, tuple, set)):
            remain.extend(item)
        else:
            yield item


# -------------------------------------
# Container Iterators
# -------------------------------------
def myget(data, keys):
    for key in keys:
        data = data[key]
    return data


def myholder(data: dict, *keys):
    _keys = list(deep_chain(keys))

    for key in _keys[:-1]:
        ## "thread-safe way"
        # while (new := data.get(key)) is None:
        # data.setdefault(key, {})

        # need to to this way because lists doesn't have 'get' method
        if isinstance(data, list):
            data = data[key]  # must exists (can't create items in lists)
        else:
            data = data.setdefault(key, {})

    return data, _keys[-1]


def myassign(data, value, keys):
    data, key = myholder(data, keys)
    data[key] = value


def winsert(ordered: List, key, value):
    common = key[:-1]
    for idx, (k, v) in enumerate(ordered):
        if k[:-1] > common:
            break
    ordered.insert(idx, (key, value))


class CWalk(dict):
    def __init__(self, map: Dict, include: List[str] = [], exclude: List[str] = []):
        for k, v in walk(map):
            string = "/".join([str(_) for _ in k])
            for pattern in exclude:
                if re.match(pattern, string):
                    break
            else:
                for pattern in include:
                    if re.match(pattern, string):
                        self[k] = v


class Walk(dict):
    def __init__(self, map: Dict = None):
        if map is None:
            self.ordered = []
        else:
            self.ordered = list(walk(map))
            self.ordered.sort()
        super().__init__({k: v for k, v in self.ordered})

    def convert_key(self, key):
        _key = tuple([int(_) if re.match(r"\d+$", _) else _ for _ in key])

        if _key in self:
            return _key
        return key

    def winsert(self, key, value, use_ordered=True):
        if isinstance(key, str):
            key = tuple([key])

        if use_ordered:
            skey = tuple([str(_) for _ in key])
            ordered = self.ordered
            # ordered.sort()
            for idx, (k, v) in enumerate(ordered):
                if k == key:
                    break
                sk = tuple([str(_) for _ in k])
                if sk > skey:
                    ordered.insert(idx, (key, value))
                    break

        self[key] = value

    def wmove(self, source, target):

        if isinstance(source, str):
            source = tuple([tuple(), source])

        if isinstance(target, str):
            source = tuple([tuple(), target])

        if source == target:
            return

        l = len(source)
        for key in list(self):
            if len(key) >= l:
                if key[:l] == source:
                    suffix = key[l:]
                    t = tuple(list(target) + list(suffix))
                    self[t] = self.pop(key)

    def wdrop(self, source):

        if isinstance(source, str):
            source = tuple([tuple(), source])

        pattern = "/".join([str(_) for _ in source])

        for key in list(self):
            skey = "/".join([str(_) for _ in key])
            if re.match(pattern, skey):
                self.pop(key)
                if key in self.ordered:
                    self.ordered.remove(key)

    def wget(self, key, extract=True):
        if isinstance(key, tuple):
            keys = set(flatten(key))
            direct_key = key
        elif isinstance(key, (list, dict)):
            keys = set(key)
            direct_key = tuple(key)
        else:
            keys = set([key])
            direct_key = tuple([key])

        struct = {
            tuple(): "<dict>",
        }
        for k, v in self.ordered:
            if keys.intersection(k) or k in keys:
                struct[k] = v

        if extract:
            while len(struct) > 1:
                if direct_key in struct:
                    item = self.rebuild(struct)
                    return item[key]

                struct = {k[1:]: v for k, v in struct.items()}
            foo = 1

        item = self.rebuild(struct)
        return item

    def wpop(self, key, default=None):
        if isinstance(key, tuple):
            keys = set(flatten(key))
            direct_key = key
        elif isinstance(key, (list, dict)):
            keys = set(key)
            direct_key = tuple(key)
        else:
            keys = set([key])
            direct_key = tuple([key])

        struct = {
            tuple(): "<dict>",
        }
        for idx, (k, v) in enumerate(self.ordered):
            if keys.intersection(k) or k in keys:
                self.ordered.pop(idx)
                v2 = self.pop(k)
                assert v == v2
                return v

        return default

    def rget(self, filters, simplify=False, search=re.search):
        struct = {
            tuple(): "<dict>",
        }
        if isinstance(filters, str):
            filters = [filters]
        if isinstance(filters, list):
            filters = {_: ".*" for _ in filters}
        for k, v in self.ordered:
            sk = ".".join([str(_) for _ in k])
            sv = str(v)
            for kpatt, vpatt in filters.items():
                if search(kpatt, sk):
                    if search(vpatt, sv):
                        struct[k] = v

        if simplify:
            struct2 = None
            # try to simplify the struct to move data to 1st depth level
            while len(struct) > 1:
                struct2 = {}
                drop = set()
                for k, v in struct.items():
                    if len(k) > 1:
                        struct2[k[1:]] = v
                        drop.add(tuple([k[0]]))
                    else:
                        struct2[k] = v

                for _ in drop:
                    struct2.pop(_)
                if len(struct) == len(struct2):
                    break
                struct = struct2
            foo = 1

        item = self.rebuild(struct)
        return item

    def copy(self):
        new = Walk()
        new.update(self)
        new.ordered = list(self.ordered)
        return new

    def wupdate(self, wdata):
        if isinstance(wdata, Walk):
            wdata = wdata.copy()
        elif isinstance(wdata, dict):
            wdata = Walk(wdata)

        for key in set(self).difference(wdata):
            value = self[key]
            wdata.winsert(key, value)

        self.ordered = wdata.ordered
        self.update(wdata)
        foo = 1

    def rebuild(self, struct=None, use_ordered=True):
        if isinstance(struct, dict):
            struct = list(struct.items())
            struct.sort()
        if not use_ordered:
            struct = list(self.items())
            try:
                struct.sort()
            except Exception:
                pass
        if struct is None:
            struct = self.ordered
        item = rebuild(struct)
        return item

    def restruct(self, info: Dict, drop=True):
        new = {}
        for kpatt, kval in info.items():
            key = self.rget(kpatt, search=re.match)
            value = self.rget(kval, search=re.match)
            if key and value:
                assert len(key) == 1
                assert len(value) == 1

                dk, k = key.popitem()
                dv, v = value.popitem()
                self.winsert(k, v)
                new[k] = v
                if drop:
                    self.wpop(dk)
                    self.wpop(dv)

        return new

    def rewrite(self, patterns):
        stream = list(self.items())
        stream.sort()

        def replace(text, patterns):
            if isinstance(text, str):
                for pattern, repl in patterns.items():
                    text = re.sub(pattern, repl, text)
            return text

        new_ord, new_dict = [], {}
        for key, value in stream:
            key = tuple([replace(text, patterns) for text in key])
            value = replace(value, patterns)

            new_ord.append((key, value))
            new_dict[key] = value

        self.ordered = new_ord
        self.clear()
        self.update(new_dict)

    def drop_empty(self):
        stream = list(self.items())
        stream.sort()

        while True:
            new_ord, new_dict = [], {}
            last = stream.pop(0)
            stream.append(((None,), None))
            for current in stream:
                attr, value = current[0][:-1], current[1]
                if last[-1] in ("<list>", "<dict>"):
                    if attr != last[0]:
                        last = current
                        continue
                if value in ("",):
                    continue

                new_ord.append(last)
                new_dict[last[0]] = last[1]
                last = current

            if len(stream) == len(new_ord):
                break
            stream = new_ord
        self.ordered = new_ord
        self.clear()
        self.update(new_dict)


def walk(
    container,
    root=tuple(),
    includes={},
    excludes={},
    keys_included=[],
    keys_excluded=[],
    include_struct=True,
):
    """Recursive Walk down for any arbitrary container."""
    keys_included = [
        re.compile(reg) if isinstance(reg, str) else reg for reg in keys_included
    ]
    keys_excluded = [
        re.compile(reg) if isinstance(reg, str) else reg for reg in keys_excluded
    ]

    def ignore(*path):
        tmp = list()
        for k in deep_chain(path):
            tmp.append(str(k))
        path = f"/{'/'.join(tmp)}"
        # ---------------------------------------
        # check key filters
        # ---------------------------------------
        for reg in keys_excluded:
            if reg.match(path):
                return True  # ignore this key

        if keys_included:
            ign = True
            for reg in keys_included:
                if reg.match(path):
                    ign = False  # accept this key
                    break
        else:
            ign = False
        return ign

    def buid_key(*keys):
        "creare a key using the right factory"

        # if factory in (tuple, ):
        # keys = list(flatten(keys))
        # return factory(keys)
        # elif factory in (str, ):
        # return '/'.join([factory(k) for k in keys])
        # else:
        # raise RuntimeError('Unknown factory type')
        results = list(keys[0])
        results.extend(keys[1:])
        return tuple(results)

    # TODO: review
    # if ignore(root):
    # return

    if isinstance(container, dict):
        # yield '{}/'.format(root, ), '<{}>'.format(container.__class__.__name__)
        func = container.items
        key = buid_key(
            root,
        )
        if not ignore(key):
            yield key, "<{}>".format(container.__class__.__name__)
    elif isinstance(container, (list, tuple, set)):

        def func():
            return enumerate(container)

        key = buid_key(
            root,
        )
        if not ignore(key):

            yield key, "<{}>".format(container.__class__.__name__)

    # infinite recursion!!
    # elif hasattr(container, '__getstate__'):
    ## is an object with __getstate__ method
    # yield buid_key(root, ), '<{}>'.format(container.__class__.__name__)
    # container = container.__getstate__()
    # func = container.items
    elif (
        hasattr(container, "__slots__")
        and "__pydantic_fields_set__" not in container.__slots__
    ):
        # is an object with __slots__
        container = dict(
            [(k, getattr(container, k, None)) for k in container.__slots__]
        )
        func = container.items
        key = buid_key(
            root,
        )
        if not ignore(key):
            yield key, "<{}>".format(container.__class__.__name__)

    elif hasattr(container, "__dict__"):
        # is an object
        container = container.__dict__
        func = container.items
        key = buid_key(
            root,
        )
        if not ignore(key):
            yield key, "<{}>".format(container.__class__.__name__)

    else:
        # TODO: apply includes/excludes
        if not ignore(root):
            yield root, container  # container is a single item or object
            return

    # EXCLUDES
    recursive, match, same_klass = 0, 0, 0
    to_exclude = set()
    valid_items = dict()
    for key, item in func():
        # if ignore(root, key):
        # continue

        valid_items[key] = item
        # ---------------------------------------
        # continue
        # ---------------------------------------
        for klass, info in excludes.items():
            if not isinstance(item, klass):
                continue
            same_klass += 1
            for attr, filters in info.items():
                value = getattr(item, attr)
                if isinstance(value, CONTAINERS_TYPES):
                    recursive += 1
                    continue
                results = [f(value) for f in filters]
                if any(match):
                    match += 1
                    to_exclude.add(key)
                match += any(results)

    if recursive == 0 and match == 1 and same_klass == 1:
        # discard the whole container because there is 1 single element
        # that match the excludes and the rest of element are related with
        # different klasses (e.g. a tuple containing related information)
        return

    # TODO: coding 'includes' filters

    # RECURSIVE exploring
    for key, item in valid_items.items():
        if key in to_exclude:
            continue

        # dealing with enums and other classes
        if isinstance(key, (Enum,)):
            # <TaskDependenceGroup.HARD: 0>
            # key = repr(key)
            # '<TaskDependenceGroup.HARD>'
            # (preserve name instead name+value for maintenance)
            key = f"<{str(key)}>"

        if isinstance(item, (Enum,)):
            # item = repr(item)
            item = f"<{str(item)}>"

        new_key = buid_key(root, key)

        if (
            isinstance(item, CONTAINERS_TYPES)
            or hasattr(item, "__slots__")
            or hasattr(item, "__dict__")
        ):
            yield from walk(
                item,
                new_key,
                includes,
                excludes,
                keys_included,
                keys_excluded,
            )
        # infinite recursion!!
        # elif item.__class__ is not type.__class__ and hasattr(item, '__getstate__'):
        # yield from walk(item, new_key, includes, excludes, keys_included, keys_excluded)
        # cpu 100% !!
        # elif hasattr(item, '__slots__') or hasattr(item, '__dict__'):
        # yield from walk(item, new_key, includes, excludes, keys_included, keys_excluded)
        else:
            if not ignore(new_key):
                yield new_key, item


def dive(container, key, stop_before=0, default_container=dict, create=False):
    """Dive into a container and return parent container and key."""
    if not key:
        return container, key

    keys = list(key)
    if stop_before > 0:
        rkey = keys[-stop_before]
        keys = keys[:-stop_before]

    if not keys:
        key = key[-1]

    while keys:
        key = keys.pop(0)
        if key in container or create:
            container = container.setdefault(key, default_container())
        else:
            break

    assert len(keys) == 0
    if stop_before > 0:
        return container, rkey
    return container, key


def marshall(item):
    _item = {}
    for key, value in walk(item):
        if re.match(r"\<\w+\>", value):
            continue
        key = ".".join([str(_) for _ in key])
        _item[key] = value
    return _item


def marshall_iter(item):
    for key, value in walk(item):
        if re.match(r"\<\w+\>", value):
            continue
        key = ".".join([str(_) for _ in key])
        yield key, value


def deep_search(item, patterns, result=None):
    """Explore deeply elements hierchachy searching items from
    certain classes.
    """
    if result is None:
        result = dict()

    remain = [item]

    # TODO: avoid circular references
    used = set()
    while remain:
        item = remain.pop(0)
        idx = id(item)
        if idx in used:
            # print('remain[{}] : {} : <{}> : {}'.format(len(remain), klass, holder, idx))
            continue
        used.add(idx)

        klass = item.__class__.__name__
        holder, idx = patterns.get(klass, (None, None))

        # print('remain[{}] : {} : <{}> : {}'.format(len(remain), klass, holder, idx))
        if idx:
            # found an item of interest.
            holder = holder or klass
            key = getattr(item, idx)
            if key is not None:
                result.setdefault(holder, dict())[key] = item
                # print('>> [{}][{}] = {}'.format(holder, key, klass))
                foo = 1

        if isinstance(item, dict):
            # remain.extend(item.keys())
            remain.extend(item.values())
        elif isinstance(item, (list, tuple, set)):
            remain.extend(item)
        elif hasattr(item, "__dict__"):
            remain.append(item.__dict__)
        elif hasattr(item, "__slots__"):
            remain.append(dict([(k, getattr(item, k, None)) for k in item.__slots__]))
        else:
            foo = 1  # discard item, we don't know how to go deeper

    return result


AVAILABLE_CONTAINERS = {
    "dict": dict,
    "list": list,
    "set": set,
    "tuple": tuple,
}


def register_container(klass, name=None):
    name = name or klass.__name__
    AVAILABLE_CONTAINERS[name] = klass


def new_container(item, default_container=dict):
    """Try to get the container described in the item string:
    <list> : return the list class
    <dict> : return the dict class
    """

    if isinstance(item, str) and (m := re.match(r"<(?P<klass>.{2,})>", item)):
        klass = m.group(1)  # the klass name
        klass = AVAILABLE_CONTAINERS.get(klass, default_container)
        return klass


def ichop(stream, root=""):
    sep = "|"
    cut = -1
    if isinstance(root, (list, tuple, dict, set)):
        root = sep.join(root)

    if isinstance(stream, dict):
        stream = stream.items()
    for key, value in stream:
        _key = sep.join([str(_) for _ in key])
        if not (root and _key.startswith(root)):
            root = _key
            cut = len(key)
        tail = key[cut:]
        if key and not tail:
            continue
        yield tail, value


def chop(container, root=""):
    result = rebuild(walk_iterator=ichop(walk(container), root), result={})
    return result


def bspec(*keys):
    def ravel(iterator):
        for x in iterator:
            if isinstance(x, (list, dict, tuple)):
                yield from ravel(x)
            else:
                yield x

    keys = [p for p in ravel(keys) if p not in ("", None)]
    result = T
    once = False
    while keys:
        p = keys.pop(0)
        if isinstance(p, TType):
            assert not once, "you can't merge 2 T types!"
            once = True
            result = p
            continue
        result = result[p]

    return result


def tspec(*keys):
    result = []

    def ravel(iterator):
        for x in iterator:
            if isinstance(x, (list, dict, tuple)):
                yield from ravel(x)
            else:
                yield x

    for p in ravel(keys):
        if p:
            result.append(p)

    return tuple(result)


def cut(stream, level=0):
    for k, v in stream:
        yield k[level:], v


def search(target, blueprint, center=[], flat=True):
    result = xoverlap(target, blueprint, center)
    if flat:
        return result
    output = {}

    # for kk in chop(result.items()):
    # print(kk)

    # output = rebuild(result.items(), result=output)
    output = rebuild(result.items(), result=output)

    return output


def option_match(pattern, *options):
    for candidate in options:
        if re.match(pattern, candidate) or re.match(candidate, pattern):
            return candidate


def gather_values(target, *root, **specs):
    results = {}
    spec = tspec(root) or ("",)
    for key, value in specs.items():
        patt = ".".join(spec + ("*", key.lstrip(".")))
        blueprint = {}  # get sure only 1 key is got
        blueprint[patt] = value or ".*"
        subset = search(target, blueprint, flat=False)
        subset = simplify(subset)
        # results.update(subset)
        merge(results, subset, inplace=True)

    return results


def simplify(container, up=0):
    # find the largst key that is contained in all other
    sep = "|"
    items = [(k, v) for k, v in walk(container)]

    def find_best():
        b_cut = ""
        b_len = -1
        keys = [sep.join([str(_) for _ in k]) for k, v in items]
        keys.sort(key=lambda x: len(x.split(sep)))
        foo = 1
        for i, a in enumerate(keys):
            for b in keys[i + 1 :]:
                if not b.startswith(a):
                    return b_cut, b_len
            else:
                l = len(a.split(sep))
                if l >= b_len:
                    b_cut = a
                    b_len = l
                    # print(f"best: {b_cut}")
        # this points means dict has a single element
        # so we need to return one level back
        return b_cut, b_len - 1

    b_cut, b_len = find_best()
    if b_cut:
        result = rebuild(cut(items, b_len - up))
        return result
    return container  # we can't simplify, is a plain dict


def deindent(container, level=1):
    items = [(k, v) for k, v in walk(container)]
    result = rebuild(cut(items, level))
    return result


def deindent_by(container, key):
    return deindent(container, level=len(key))


def rebuild(
    walk_iterator,
    default_converter=None,
    default_container=dict,
    key_converters={},
    container_converters={},
    converters={},
    result=None,
    merge=True,
):
    """rebuild a tree structure from previous walk result

    - rebuild structure tree
    - track special holders such lists, tuples, sets
    - treats everything as dicts
    - finally convert back all special holders
    """
    # if factory in (str, ):
    # key_converters = dict([re.compile(k, re.I | re.DOTALL), v] for k, v in key_converters.items())

    # merge = False if result is None else True

    def new_container(item):
        """Try to get the container described in the item string:
        <list> : return the list class
        <dict> : return the dict class
        """

        if isinstance(item, str) and (m := re.match(r"<(?P<klass>.{2,})>", item)):
            klass = m.group(1)  # the klass name
            if "<" in klass:
                pass  # text can't containt "<" or ">" as there are special delimiters
            else:
                klass = AVAILABLE_CONTAINERS.get(klass, default_container)
                return klass

    convert = dict()
    if isinstance(walk_iterator, dict):
        walk_iterator = walk_iterator.items()
    for key, item in walk_iterator:
        klass = new_container(item)  # try to guess if is a container

        if klass is not None and not issubclass(klass, dict):
            convert[key] = klass  # for later converting the container
            klass = default_container  # as default building container for non-dict alike containers

            if key:
                parent, parent_key = dive(result, key, 1, create=True)
                assert parent_key == key[-1]
                if isinstance(
                    parent.setdefault(parent_key, default_container()),
                    (tuple, list),
                ):
                    parent[parent_key] = {
                        i: v for i, v in enumerate(parent[parent_key])
                    }

        if klass:
            item = klass()

        conv = converters.get(item.__class__, default_converter)
        if conv:
            item = conv(item)

        if not key:
            if result is None:
                result = item
            continue

        assert result is not None, "root element must be found before any other"
        # print((key, item, merge))
        divepush(result, key, item, merge)
    # we need to convert some nodes from botton-up to preserve
    # indexing with keys as str, not integers in case of list/tuples
    convert_keys = list(convert.keys())
    convert_keys.sort(key=len, reverse=True)

    for key in convert_keys:
        klass = convert[key]
        if key:
            parent_container, parent_key = dive(result, key, 1)
            container = parent_container[parent_key]
        else:
            container = result
        keys = list(container.keys())

        if issubclass(klass, (list, tuple)):
            # if you have an error here, probably you're
            # trying to merge dict and lists in the same
            # 'path'
            keys.sort(key=lambda x: int(x))  # TODO: review
            # keys.sort(key=lambda x: str(x))  # TODO: review
        else:
            keys.sort()

        values = [container[k] for k in keys]
        item = klass(values)
        # chain converters
        for conv in container_converters.get(klass, []):
            item = conv(key, item)

        if key:
            parent_container[parent_key] = item
        else:
            result = item

    return result


def flatten(iterator, klass=None):
    """Convert any iterator into key: value pair stream."""
    if not isinstance(iterator, Iterable):
        yield iterator
        return
    # from https://stackoverflow.com/questions/2158395/flatten-an-irregular-list-of-lists
    for item in iterator:
        if isinstance(item, Iterable) and not isinstance(item, (str, bytes)):
            yield from flatten(item)
        elif klass is None or isinstance(item, klass):
            yield item


def unflattern(iterator, keys, container=None):
    """Build a structure info from a iterator, using some keys that
    acts as indexes of the structure.

    The value is taken from item itself.
    """
    container = container or dict()
    for item in iterator:
        parent, children = None, container
        for key in keys:
            if isinstance(item, (list, tuple)):
                item = list(item)
                key = item.pop(key)
            elif isinstance(item, dict):
                item = dict(item)
                key = item.pop(key)
            else:
                key = getattr(item, key)
            parent, children = children, children.setdefault(key, dict())
        parent[key] = item
    return container


def join_level(container, level):
    """Convert the result of joining values from original container
    chooping the first (levels) parents
    """
    return rebuild(
        [(key[level:], value) for key, value in walk(container) if len(key) >= level]
    )


def flatdict(container):
    """Convert any structure in a flat dict that can be
    rebuilt later.

    flat = flatdict(container)
    copy = rebuild(flat.items())
    assert flat == copy
    """
    return dict([t for t in walk(container)])


def deep_chain(*iterable):
    """Return all elements in an arbitrary nested structure."""
    remain = list(iterable)
    # preserve order
    while remain:
        item = remain.pop(0)
        if isinstance(item, BASIC_TYPES):
            yield item
        elif isinstance(item, dict):
            remain = list(items.keys()) + remain
            # remain.extend(item.keys())
            # remain.extend(item.values())
        elif isinstance(item, (list, tuple, set)):
            # remain.extend(item)
            remain = list(item) + remain
        elif hasattr(item, "__dict__"):
            remain = list(items.__dict__) + remain
            # remain.append(item.__dict__)
        elif hasattr(item, "__slots__"):
            # remain.append(dict([(k, getattr(item, k, None)) for k in item.__slots__]))
            remain = [
                dict([(k, getattr(item, k, None)) for k in item.__slots__])
            ] + remain
        else:
            foo = 1  # discard item, we don't know how to go deeper


def diffdict(current, last):
    """Compare to versions of the same flatdict container, giving:

    - new items
    - changed items
    - deleted items

    """
    current_keys = set(current.keys())
    last_keys = set(last.keys())

    new_items = dict([(k, current[k]) for k in current_keys.difference(last_keys)])
    deleted_items = dict([(k, last[k]) for k in last_keys.difference(current_keys)])

    changed_items = dict()
    for k in current_keys.intersection(last_keys):
        c = current[k]
        l = last[k]
        if c != l:
            changed_items[k] = (c, l)

    return new_items, changed_items, deleted_items


# -------------------------------------
# Container Updating
# -------------------------------------
class DELETE_ITEM:
    """Item interpreted as REMOVE element"""


def xsearch(container, blueprint):
    for key, value in walk(container):
        key = ".".join(key)
        value = str(value)

        for kpattern, vpattern in blueprint.items():
            print(f"{kpattern}: {key}, {vpattern}: {value}")
            if re.search(kpattern, key) and re.search(vpattern, value):
                yield key, value
    foo = 1


def xmatch(container, blueprint):
    try:
        include = blueprint.get("include", {})
        exclude = blueprint.get("exclude", {})
        if not (include or exclude):
            include = blueprint

        def match(_key, _value):
            keys = [str(k) for k in _key]
            value = str(_value)
            # exclude filter
            for kpattern, vpattern in exclude.items():
                for k in keys:
                    if re.match(kpattern, k):
                        if re.match(vpattern, value):
                            return False

            # include filter
            if include:
                key = ".".join(keys)
                for kpattern, vpattern in include.items():
                    # print(f"{kpattern} : {vpattern}   --> {key} : {value}")
                    if re.match(kpattern, key):
                        if re.match(vpattern, value):
                            return True
                return False
            return True

        for _key, _value in walk(container):
            if match(_key, _value):
                yield _key, _value

    except Exception as why:  # pragma: nocover
        print(why)
    foo = 1


def xfind(container, keys):
    for key, value in walk(container):
        key = ".".join(key)
        value = str(value)
        print(f"{key}: {value}")

        for kpattern in keys:
            if re.match(kpattern, key):
                yield key, value


def xlocate(container, blueprint, center=[]):
    center = set(center)

    def distance(x):
        d = set(x[0]).difference(center)
        return len(d)

    candidates = []
    for pair in xmatch(container, blueprint):
        candidates.append(pair)

    candidates.sort(key=distance)
    return candidates


def xoverlap(container, blueprint, center=[]):
    result = {}
    for key, value in xlocate(container, blueprint):
        result.setdefault(key, value)
    return result


def xget(container, key, default=None):
    if isinstance(key, str):
        key = key.split(".")

    for k in key:
        if k in container:
            container = container[k]
        else:
            return default
    return container


def divepush2(container, seq, d, **kw):
    key = [d[k] for k in seq]
    return divepush(container, key, d, **kw)


def divepush(container, key, item, merge=True, default_container=dict):
    """Set an element in a nested container array"""
    parent = container
    for key in key:
        if container is None:
            return parent
        parent, container = container, container.setdefault(key, default_container())

    if item is not DELETE_ITEM:
        if key is not None:
            if merge == False:
                parent[key] = item
            elif isinstance(container, BASIC_TYPES):
                parent[key] = item
            elif len(container) == 0:
                parent[key] = item
            elif len(item) == 0:
                foo = 1
            else:
                parent[key] = item
    else:
        parent.pop(key, None)

    return parent


def update_structure(target, source):
    rebuild(walk(source), result=target)


def serializable_container(
    container,
    includes={},
    excludes={},
    keys_included=[],
    keys_excluded=[],
    ignore=True,
):
    def _filter(container):
        for path, v in walk(
            container,
            includes=includes,
            excludes=excludes,
            keys_included=keys_included,
            keys_excluded=keys_excluded,
        ):
            if v in ("<tuple>",):
                yield path, "<list>"
            elif v in (None, "<dict>", "<list>"):
                yield path, v
            elif v in ("<Config>",):
                yield path, "<dict>"
            # must be at the end
            elif isinstance(v, BASIC_TYPES_EXT):
                yield path, v
            # elif isinstance(v, Item):
            # yield path, v
            # func = item.__getstate__().items
            # yield buid_key(root, ), '<{}>'.format(container.__class__.__name__)
            elif ignore:
                # print(f"Ignoring: {path}: {v}")
                continue
            else:
                raise RuntimeError(
                    f"{RED}Don't know how to _filter{YELLOW} {path} = {v}{RESET}"
                )

    result = rebuild(_filter(container))
    return result


def update_container_value(container, value, *keys):
    """Try to change a value in a container tree of nested list and dict
    returning if tree has been changed or not.
    """

    def change(container, key, value):
        modified = False
        if isinstance(container, (list,)):
            assert isinstance(key, int)
            if value:
                if key not in container:
                    container.append(key)
                    modified = True
            else:
                if key in container:
                    container.remove(key)
                    modified = True
        else:
            old = container.get(key)
            if value != old:
                container[key] = value
                modified = True
        return modified

    for key in keys[:-1]:
        if isinstance(container, (list,)):
            key = int(key)
            while len(container) < key:
                container.append(None)
        elif isinstance(container, (dict,)):
            container = container.setdefault(key, dict())
        else:
            raise RuntimeError(
                f"Don't know how to handle {container.__class__} in container"
            )
    return change(container, keys[-1], value)


# -------------------------------------
# Merge functions
# -------------------------------------


async def amerge(base, new, mode="add", inplace=False, **kw):
    """Merge a base container with a new elements from other container."""

    def next_key_old(key):
        key = key.split("/")
        key[-1] = int(key[-1]) + 1
        return "/".join(key)

    def next_key(key):
        key = list(key)
        key[-1] += 1  # must be an integer
        return tuple(key)

    def _hide_score(item):
        """function for sorting item sequence.

        - shorter key length goes 1st.
        - 22 goes 1st than 1111111.

        compute a shortable alternative representation of key
        that match these criterias.

        """
        # combine lenght of individual elements in unwrapped item
        r = [f"{o}" for o in flatten(item)]
        r = [f"{'!'*len(o)}{o}" for o in r]

        # now combine the key length as well
        r = "!" * len(item[0]) + "".join(r)
        return r

    def score(item):
        """function for sorting item sequence.

        - shorter key length goes 1st.
        - 22 goes 1st than 1111111.

        compute a shortable alternative representation of key
        that match these criterias.

        """
        return item[0]

    async def _merge(base, new):
        """
        yield 'a' side or 'b' side depending on key ordering.

        singles values or dict {key, value} can merge without
        structural conflicts.

        structural conflicts comes when in the same *cursor* position
        we have different container structure.
        """
        base_ = list(walk(base))
        new_ = list(walk(new))

        base_.sort(key=score, reverse=False)
        new_.sort(key=score, reverse=False)

        # with open("/tmp/base.txt", "w") as f:
        # for item in base_:
        # f.write(f"{item}\n")

        # with open("/tmp/new.txt", "w") as f:
        # for item in new_:
        # f.write(f"{item}\n")

        last_container = []  # ?? None instead?
        last_container = None  # agp: + None
        last_parent = None
        last_key = None
        last_idx = 0

        a = b = None
        a0 = b0 = None

        t1 = 0

        while base_ or new_:
            t0 = time.time()
            if t0 > t1:
                t1 = t0 + 1
                await asyncio.sleep(0)

            # update next a or b value for take a decission
            if a is None and base_:
                a = base_.pop(0)
            if b is None and new_:
                b = new_.pop(0)

            # 0. when both are the same, we just yield the
            # (same) value and continue with the next case.
            if b == a:
                yield b
                a = b = a0 = b0 = None
                continue

            # 1. TODO: review... looks like "adding two lists" ?
            if a and a[1] in ("<list>",) or b and b[1] in ("<list>",):
                for b1 in last_container or []:  # agp: + or []
                    last_key = next_key(last_key)
                    yield (last_key, b1)

                last_container = list()
                last_parent = b and b[0]

            # 2. when a or b is mising, return 'a' or 'b'
            if a is None and b is not None:
                yield b
                b = b0 = None
                continue
            if b is None and a is not None:
                yield a
                a = a0 = None
                continue

            # 3. both a, b exists, we need to compare them
            # return just one, and continue asking a new
            # fresh value from missing *leg*.

            # using same sort rule that ordering base and new lists
            # to make comparissons possible
            a0 = a0 or score(a)
            b0 = b0 or score(b)

            if b0 < a0:  # flush 'b' side as comes first
                yield b
                b = b0 = None
            elif b0 > a0:  # flush 'a' side as comes first
                yield a
                a = a0 = None
            elif b0 == a0:
                # share the same key, but values differs
                assert a != b
                if mode in ("replace",):
                    yield b
                elif mode in ("add",):
                    # check if we have a list container
                    # in progress and concatenate them
                    if isinstance(last_container, list):
                        # TODO: REVIEW
                        last_key = a[0]
                        # we save the value in the WIP container
                        last_container.append(b[1])
                        yield a
                    else:
                        # Conflict: the keys can not be merged, so we
                        # replace with 'b' side
                        yield b
                a = b = a0 = b0 = None
            else:
                raise RuntimeError("???")

        foo = 1

    # >>> debug
    # data = list()
    # from pprint import pprint

    # for pair in _merge(base, new):
    # print("-" * 40)
    # print(f"{pair[0]}: {pair[1]}")
    ## data.append(pair)
    ## data = sort_iterable(data)
    ## try:
    ## result = rebuild(data)
    ## pprint(result)
    ## except:
    ## pass

    # foo = 1

    # <<< debug
    stream = list(await _merge(base, new))

    # key_converters = {'None': None, }
    # with open("/tmp/result.txt", "w") as f:
    # for item in result:
    # f.write(f"{item}\n")

    # self.reactor.ctx = sort_iterable(result)
    converters = {dict: base.__class__}
    # result = scall(
    # rebuild, walk_iterator=result, converters=converters, **kw
    # )
    result = rebuild(walk_iterator=stream, converters=converters, result={}, **kw)
    if inplace:
        base.clear()
        base.update(result)
    return result


def merge(base, new, mode="add", inplace=False, **kw):
    """Merge a base container with a new elements from other container."""

    def next_key_old(key):
        key = key.split("/")
        key[-1] = int(key[-1]) + 1
        return "/".join(key)

    def next_key(key):
        key = list(key)
        key[-1] += 1  # must be an integer
        return tuple(key)

    def _hide_score(item):
        """function for sorting item sequence.

        - shorter key length goes 1st.
        - 22 goes 1st than 1111111.

        compute a shortable alternative representation of key
        that match these criterias.

        """
        # combine lenght of individual elements in unwrapped item
        r = [f"{o}" for o in flatten(item)]
        r = [f"{'!'*len(o)}{o}" for o in r]

        # now combine the key length as well
        r = "!" * len(item[0]) + "".join(r)
        return r

    def score(item):
        """function for sorting item sequence.

        - shorter key length goes 1st.
        - 22 goes 1st than 1111111.

        compute a shortable alternative representation of key
        that match these criterias.

        """
        return item[0]

    def _merge(base, new):
        """
        yield 'a' side or 'b' side depending on key ordering.

        singles values or dict {key, value} can merge without
        structural conflicts.

        structural conflicts comes when in the same *cursor* position
        we have different container structure.
        """
        base_ = list(walk(base))
        new_ = list(walk(new))

        base_.sort(key=score, reverse=False)
        new_.sort(key=score, reverse=False)

        # with open("/tmp/base.txt", "w") as f:
        # for item in base_:
        # f.write(f"{item}\n")

        # with open("/tmp/new.txt", "w") as f:
        # for item in new_:
        # f.write(f"{item}\n")

        last_container = []  # ?? None instead?
        last_container = None  # agp: + None
        last_parent = None
        last_key = None
        last_idx = 0

        a = b = None
        a0 = b0 = None

        while base_ or new_ or a or b:
            # update next a or b value for take a decission
            if a is None and base_:
                a = base_.pop(0)
            if b is None and new_:
                b = new_.pop(0)

            # 0. when both are the same, we just yield the
            # (same) value and continue with the next case.
            if b == a:
                yield b
                a = b = a0 = b0 = None
                continue

            # 1. TODO: review... looks like "adding two lists" ?
            if a and a[1] in ("<list>",) or b and b[1] in ("<list>",):
                for b1 in last_container or []:  # agp: + or []
                    last_key = next_key(last_key)
                    yield (last_key, b1)

                last_container = list()
                last_parent = b and b[0]
            else:
                last_container = None

            # 2. when a or b is mising, return 'a' or 'b'
            if a is None and b is not None:
                yield b
                b = b0 = None
                continue
            if b is None and a is not None:
                yield a
                a = a0 = None
                continue

            # 3. both a, b exists, we need to compare them
            # return just one, and continue asking a new
            # fresh value from missing *leg*.

            # using same sort rule that ordering base and new lists
            # to make comparissons possible
            a0 = a0 or score(a)
            b0 = b0 or score(b)

            if b0 < a0:  # flush 'b' side as comes first
                yield b
                b = b0 = None
            elif b0 > a0:  # flush 'a' side as comes first
                yield a
                a = a0 = None
            elif b0 == a0:
                # share the same key, but values differs
                assert a != b
                if mode in ("replace",):
                    yield b
                elif mode in ("add",):
                    # check if we have a list container
                    # in progress and concatenate them
                    if isinstance(last_container, list):
                        # TODO: REVIEW
                        last_key = a[0]
                        # we save the value in the WIP container
                        last_container.append(b[1])
                        yield a
                    else:
                        # Conflict: the keys can not be merged, so we
                        # replace with 'b' side
                        yield b
                a = b = a0 = b0 = None
            else:
                raise RuntimeError("???")

        foo = 1

    stream = list(_merge(base, new))

    converters = {dict: base.__class__}
    # result = scall(
    # rebuild, walk_iterator=result, converters=converters, **kw
    # )
    result = rebuild(walk_iterator=stream, converters=converters, result={}, **kw)
    if inplace:
        base.clear()
        base.update(result)
    return result


def convert_container(item):
    container = new_container(item)
    if container is not None:
        return container()
    return item


def diff(new, old, mode="both", **kw):
    """Diff between 2 containers"""

    def _diff(new, old_):
        """
        yield 'a' side or 'b' side depending on key ordering.

        singles values or dict {key, value} can merge without
        structural conflicts.

        structural conflicts comes when in the same *cursor* position
        we have different container structure.
        """

        new_ = dict(walk(new))
        old_ = dict(walk(old_))

        cc = convert_container

        if mode in ("both", "list"):
            func = lambda o, n: [cc(o), cc(n)]
        elif mode in ("dict",):
            func = lambda o, n: {"old": cc(o), "new": cc(n)}
        else:
            func = lambda o, n: cc(n)

        for key, vnew in new_.items():
            vold = old_.get(key)
            if vnew != vold:
                yield key, func(vold, vnew)

    result = {}
    for k, v in _diff(new, old):
        spec = bspec(k)

        assign(result, spec, v, missing=dict)

    return result


def rediff(new, old, mode="both", **kw):
    """Diff between 2 containers using regexp"""

    def _diff(new, old_):
        """
        yield 'a' side or 'b' side depending on key ordering.

        singles values or dict {key, value} can merge without
        structural conflicts.

        structural conflicts comes when in the same *cursor* position
        we have different container structure.
        """
        FLAGS = re.DOTALL | re.IGNORECASE
        new_ = dict(walk(new))
        old_ = dict(walk(old_))

        new_.pop(tuple())
        old_.pop(tuple())

        key_map = {k: "/".join(k) for k in old_}

        cc = convert_container

        if mode in ("both", "list"):
            func = lambda o, n: [cc(o), cc(n)]
        elif mode in ("dict",):
            func = lambda o, n: {"old": cc(o), "new": cc(n)}
        else:
            func = lambda o, n: cc(n)

        for nkey, nvalue in new_.items():
            if nvalue in (None, "<dict>"):
                continue  # ignore

            rnkey = f"{'/'.join(nkey)}$"
            snvalue = str(nvalue)

            for okey, ovalue in old_.items():
                rokey = key_map.get(okey)

                if re.match(rnkey, rokey):
                    # check if they are the same
                    sovalue = str(ovalue)

                    # TODO: find a better solution that really the difference doesn't appears here
                    # exceptions:
                    # case (('var', 'pkg', 'pip', 'pycelium'), '<dict>', 'lastest'),
                    if "pkg" in rnkey:  #  and 'pip'
                        if re.match("lastest", snvalue):
                            if re.match("(<dict>)|(lasest)", sovalue):
                                break

                    if not (
                        ovalue == nvalue
                        or re.match(sovalue, snvalue, FLAGS)
                        or re.match(snvalue, sovalue, FLAGS)
                    ):
                        # yield nkey, func(ovalue, nvalue)
                        yield okey, func(ovalue, nvalue)
                    break
            else:
                value = func(None, nvalue)
                if any(value.values()):
                    yield nkey, value
                else:
                    foo = 1

            foo = 1

    result = {}
    for k, v in _diff(new, old):
        spec = bspec(k)
        assign(result, spec, v, missing=dict)

    return result


def get_deltas(container):
    pending = {}
    for key, value in walk(container):
        # if not key or value in ('<dict>',):
        # continue
        if key:
            parent, attr = key[:-1], key[-1]
            status = pending.setdefault(parent, {})
            status[attr] = value

            # check completness
            if "new" in status and "old" in status:
                yield parent, status["old"], status["new"]


def sort_iterable(iterable, key=0):
    "Specific function for sorting a iterable from a specific key position"
    result = list()
    iterable = list(iterable)
    while iterable:
        l = min([len(k[key]) if hasattr(k[key], "__len__") else 0 for k in iterable])
        subset = list()
        for i, k in reversed(list(enumerate(iterable))):
            if not hasattr(k[key], "__len__") or len(k[key]) == l:
                subset.append(k)
                iterable.pop(i)
        subset.sort(key=str, reverse=False)
        result.extend(subset)
    return result


# -------------------------------------
# Best Key of a dict
# -------------------------------------


def find_best(container, func):
    best_key, best_value = None, None
    for key, value in container.items():
        if best_key:
            if func(value, best_value):
                best_key, best_value = key, value
        else:
            best_key, best_value = key, value

    return best_key, best_value


def match(item: Union[Dict, Any], criteria: Dict) -> bool:
    """Determine if an item matches a criteria"""
    if hasattr(item, "dict"):
        universe = item.dict()
    elif isinstance(item, dict):
        universe = item
    else:
        raise RuntimeError(f"{item} is not a dict or have a dict() method")

    for key_pattern, value_pattern in criteria.items():
        for key, value in universe.items():
            if re.match(key_pattern, key, re.DOTALL | re.I) and (
                re.match(value_pattern, value, re.DOTALL | re.I)
                or value_pattern == value
            ):
                break
        else:
            return False
    return True


def text_to_xml(text):
    parser = etree.XMLParser(
        remove_blank_text=True,
        recover=True,
        ns_clean=True,
    )
    root = etree.XML(text, parser=parser)
    return root


def xml_to_dict(element):
    """
    Recursively converts an XML element and its children to a dictionary.
    """
    result = {}
    for child in element:
        child_result = xml_to_dict(child)
        tag = etree.QName(child).localname
        if tag in result:
            # Handle multiple elements with the same tag by creating a list
            if isinstance(result[tag], list):
                result[tag].append(child_result)
            else:
                result[tag] = [result[tag], child_result]
        else:
            result[tag] = child_result

    # Include attributes and text (if present)
    if element.attrib:
        result.update(("@" + k, v) for k, v in element.attrib.items())

    text = element.text.strip() if element.text else None
    if text:
        if result:
            result["#text"] = text
        else:
            result = text

    return result


def xml_text_to_dict(text, include_root=True):
    root = text_to_xml(text)
    result = xml_to_dict(root)
    if include_root:
        result = {etree.QName(root).localname: result}
    return result


# ------------------------------------------
# Generic Filters
# ------------------------------------------
class Dict(dict):
    """A specialized *dict* with some filters implemented."""

    ORDER_KEYS = "date", "last_trade_date"

    def copy(self):
        return self.__class__(self)

    def __getitem__(self, key):
        """Special"""
        if key not in self and isinstance(key, int):
            map_ = {}
            for k, v in self.items():
                for o in self.ORDER_KEYS:
                    if o in v:
                        map_[v[o]] = k, v
            keys = list(map_.keys())
            keys.sort()
            return map_[keys[0]]  # returns both k, v items

        return super().__getitem__(key)

    def over(self, key, value):
        """Filter items where key > value."""
        new = self.__class__()
        for k, item in self.items():
            if (key not in item) or (item[key] > value):
                new[k] = item
        return new

    def under(self, key, value):
        """Filter items where key < value."""
        new = self.__class__()
        for k, item in self.items():
            if (key not in item) or (item[key] < value):
                new[k] = item
        return new

    # def __getstate__(self):
    # return dict(self)

    # def __setstate__(self, item):
    # self.update(item)


class Dom(Dict):
    """A specialized *Dict* that acts like a Document Object Model (*DOM*).

    - xpath alike patching.
    - xpath alike get item.
    - find iterator similar to unix *find*.

    """

    re_param = re.compile(r"\{(?P<name>[^\}]*)\}")
    re_op = re.compile(r"(?P<op>[<>[=+*]+)(?P<name>[^/\]]*)")
    re_idx = re.compile(r"\[(?P<idx>(-|\w)+)\]")

    def _unroll(self, path, patch, dom, **env):
        """
        Get an elment from DOM

        - "{name}" : replace '{name}' by env replacement.
        - "={name}" : replace '{name}' by env replacement and don't split by '/' the result (urls typically)
        - ">name"  : replace 'dom' by dom[name] and insert in DOM
        - "<name"  : replace 'dom' by dom[name], breaking the descend, and doing nothing with DOM
        - "[name]" : index current dom (an items list) by item[key]

        Example: '/{path}/{symbol}/{local_symbol}/{timeframe}/>bars/[date]

        1. replace and go down using variable substitution: path, ..., timeframe.
        2. replace node by node['bars']. Next is a list of bars in this particular case.
        3. index each item in the current 'dom' (a list in this example) by its 'date' keyword value.

        Example: '/errors/{rid}/{date}'

        1. create 'errors' holder
        2. create a holder for 'rid' message/s.
        3. index by 'date'

        Note:

        - path and patch are join

        """
        # assert os.path.isabs(path)
        env.update(dom)
        env["path"] = path

        # expand path
        aux = os.path.join(path, patch)
        aux = aux.split("/")

        # break down all path sublevels
        result = []
        retire = set([])
        setters = []
        while aux:
            setter = None
            name = aux.pop(0)
            # TODO : recursive param expansion
            # 1. expand name
            m = isinstance(name, str) and self.re_param.match(name)
            if m:
                (key,) = m.groups()
                if key in dom:
                    retire.add(key)
                    name = dom[key]
                else:
                    name = name.format(**env)

            # 2. operations (when apply)
            m = isinstance(name, str) and self.re_op.match(name)
            if m:
                operation, name = m.groups()
                for op in operation:
                    if op == ">":
                        # replace dom by dom[name]
                        dom = dom[name]
                        setters.append(name)
                        # and insert name in recursive dive-down keys
                        aux.insert(0, name)

                    elif op == "<":
                        # replace dom by dom[name]
                        dom = dom[name]
                        setters.append(name)
                        # do nothing and break the descend
                        break

                    elif op == "[":
                        # index list with key 'name'
                        # check if is a number(pos) or string(key)
                        try:
                            name = eval(name, env)
                            if isinstance(name, int):
                                pass
                            else:
                                raise RuntimeError(f"[{name}] ???-???", name)
                        except Exception as why:  # pragma: nocover
                            foo = 1
                        setters.append(name)

                    elif op == "=":
                        # literal insertion
                        aux.insert(0, name)  # raw insert
                        name = None
                        break  # do not split '/' char
                    elif op == "+":
                        assert (
                            not name
                        ), "operator '+' takes no arguments, just append to the list"
                        if isinstance(l_v, dict) and not where:
                            where = l_v[l_k] = list()
                            where.append(dom)
                            assert (
                                not aux
                            ), "operator '+' should be the last one in xpath"
                            return

                    if name in setters:
                        continue

                    if isinstance(name, str):
                        spl = name.split("/")
                        if len(spl) > 1:
                            spl.extend(aux)
                            aux = spl
                            continue

            if name:
                result.append(name)

        return result, retire, setters

    def g(self, path, **env):
        """access to a item inside DOM.
        TODO.: cache and invalidate cache items.
        """
        result, retire, setter = self._unroll(path, patch="", dom={}, **env)

        for key in retire:
            dom.pop(key)

        holder = self
        for key in result:
            if isinstance(key, int) and isinstance(holder, dict):
                if holder:
                    keys = list(holder.keys())
                    keys.sort()  # TODO: review sorting keys before accessing
                    key = keys[key]
                else:
                    raise RuntimeError("Empty ??")
            holder = holder.setdefault(key, dict())
        return holder

    def patch(self, path, patch, dom, **env):
        """Update the dom with some data in somewhere
        pointed by patch.

        - "{name}" : replace '{name}' by env replacement.
        - "={name}" : replace '{name}' by env replacement and don't split by '/' the result (urls typically)
        - ">name"  : replace 'where' by dom[name]
        - "[name]" : index current dom (a list item) by item[key]
        - "+"      : replace current 'where' holder (dict) by list.
                     Following operation should be "append" not [index]

        Example: '/{path}/{symbol}/{local_symbol}/{timeframe}/>bars/[date]

        1. replace and go down using variable substitution: path, ..., timeframe
        2. replace dom by dom['bars']. Next is a list of bars
        3. index the 'dom' (a list) by 'date' key of each item.

        Example: '/errors/{rid}/{date}'

        1. create 'errors' holder
        2. create a holder for 'rid' message/s.
        3. index by 'date'

        """

        result, retire, setters = self._unroll(path, patch, dom, **env)
        # apply the keys that must be retired from dom
        # as they have been used.
        for key in retire:
            dom.pop(key, None)

        # create the down-path from '/' accross it-self.
        holder = self
        for key in result:
            holder = holder.setdefault(key, dict())

        # in case of having setters, we descend through dom but last key ...
        if setters:
            for key in setters[:-1]:
                dom = dom.get(key, dom)

            # ... and traslade the target dom element to this (holder)
            name = setters[-1]
            for item in dom:
                key = item.pop(name)
                holder[key] = item
        else:
            # otherwise, we simply update the this (holder) leaf with remaining dom.
            holder.update(dom)

    def find(self, key_patt, value_patt="."):
        # vpattern = kw.get('vpattern', '.')

        # meta = '|'.join(patterns)
        # meta = re.compile(meta)
        # vpattern = re.compile(vpattern)

        for root, container in walk(
            self,
        ):
            path = "/".join([str(x) for x in root])
            m = re.search(key_patt, path)
            if m:
                d = m.groupdict()
                aux = str(container)
                m = re.search(value_patt, aux)
                if m:
                    d.update(m.groupdict())
                    yield path, container, d

        foo = 1

    def subset(self, definition):
        res = self.__class__()
        for key_patt, patch in definition.items():
            for path, value, d in self.find(key_patt):
                dom = {}
                dom[d["key"]] = value
                res.patch("/", patch, dom, **d)

        return res

    # hooks / pub-sub
    def add_hook(self, hook, func, *args, **kw):
        # kw.setdefault("worker", self)
        if not hasattr(self, "_hooks"):
            self._hooks = {}

        self._hooks.setdefault(hook, list()).append(tuple([func, args, kw]))

    def _hook(self, hook, *args, **kw):
        for regexp, (func, args_, kw_) in self._hooks.items():
            if re.match(regexp, hook):
                _kw = dict(kw_)
                _kw.update(kw)
                _args = args or args_
                scall(func, *_args, **_kw)


register_container(Dict)
register_container(Dom)
