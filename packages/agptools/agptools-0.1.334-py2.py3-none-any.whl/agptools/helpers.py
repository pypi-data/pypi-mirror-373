from datetime import timedelta, datetime, timezone
import os
import re
import string
import hashlib
import sys
from collections import namedtuple
from time import time_ns

from typing import Any, Callable, List
from urllib import parse
import pytz

# import uuid
import yaml

from dateutil import parser
from glom import glom, assign

from .containers import soft

FloatWhen = namedtuple("FloatWhen", ["value", "datetime"])


LOCAL_TZ = pytz.timezone("Europe/Madrid")
UTC_TZ = pytz.timezone("UTC")


def generate_blueprint(data, bluekeys=None):
    # bluekeys = ["url", "name"]
    bluekeys = bluekeys or [
        "url",
    ]
    if isinstance(bluekeys, str):
        bluekeys = bluekeys.split(",")
    if isinstance(data, dict):
        bluekeys = [_ for _ in bluekeys if _ in data]
        blueprint = "|".join([str(data[_]) for _ in bluekeys])
    else:
        bluekeys = [_ for _ in bluekeys if hasattr(data, _)]
        blueprint = "|".join([str(getattr(data, _)) for _ in bluekeys])

    if blueprint:
        blue = hashlib.md5(blueprint.encode("utf-8")).hexdigest()
        return blue


def camel_case_split(text):
    return re.findall(r"[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))", text)


def wrap_text(text, wide=80, prefix=""):
    result = []
    stream = text.split()

    line = []
    length = 0
    while stream:
        word = stream.pop(0)
        lw = len(word) + 1
        if length + lw > wide:
            result.append(" ".join(line))
            line = [prefix]
            length = 0
        line.append(word)
        length += lw
    result.append(" ".join(line))

    result = "\n".join(result)

    return result


# ------------------------------------------------
# Weekdays
# ------------------------------------------------
WEEK_OFFSET = {
    0: r"(?i)(domingo|sunday)",
    1: r"(?i)(lunes|monday)",
    2: r"(?i)(martes|tuesday)",
    3: r"(?i)(mi.rcoles|wednesday)",
    4: r"(?i)(jueves|thursday)",
    5: r"(?i)(viernes|friday)",
    6: r"(?i)(s.bado|satruday)",
}


def get_wday(text):
    if text and isinstance(text, str):
        for wday, pattern in WEEK_OFFSET.items():
            if re.match(pattern, text):
                return wday


# ------------------------------------------------
# Reg Helpers
# ------------------------------------------------
def match_any(string, *regexp):
    for pattern in regexp:
        if m := re.match(pattern, string):
            return m


# ------------------------------------------------
# Select the best of a serie using a score function
# ------------------------------------------------
def argmax(mask, *values):
    m = max(mask)
    for idx in mask:
        if mask[idx] == m:
            if values:
                return values[idx]
            else:
                return idx


def best_of(candidates: List[Any], func: Callable, *args, **kw) -> List:
    """
    Select the best of a series using a score function

    Callable may return a score or (score, item) to be saved

    If only score is returned, then current item will be saved
    as best candidate
    """
    best_score, best_result = -sys.float_info.max, None
    for item in candidates:
        result = func(item, *args, **kw)
        if isinstance(result, (tuple, list)) and len(result) == 2:
            score, result = result
        else:
            score, result = result, item

        if best_score < score:
            best_score, best_result = score, result
    return best_score, best_result


# ------------------------------------------------
# File and config helpers
# ------------------------------------------------
def expandpath(path):
    if path:
        path = os.path.expanduser(path)
        path = os.path.expandvars(path)
        path = os.path.abspath(path)
        while path[-1] == "/":
            path = path[:-1]
    return path


def load_config(env):
    """Merge config files"""
    if env is None:
        return
    if isinstance(env, dict):
        cfg = env
    else:
        cfg = env.__dict__
    for path in reversed(cfg.get("config_files", ["config.yaml"])):
        try:
            data = yaml.load(open(path, "rt", encoding="utf-8"), Loader=yaml.Loader)
            # merge(cfg, data, inplace=True) # use any deep merge library or ...
            cfg.update(data)

        except FileNotFoundError:
            pass

    # env.folders = {expandpath(p): None for p in env.folders}


def save_config(env):
    os.makedirs(os.path.dirname(env.config_file), exist_ok=True)
    yaml.dump(env.__dict__, open(env.config_file, "wt"))


def build_fstring(*tokens, sep=""):
    tokens = ["{" + token + "}" for token in tokens]
    return sep.join(tokens)


# -----------------------------------------------------------
# URI handling
# -----------------------------------------------------------
reg_uri = re.compile(
    r"""(?imsx)
    (?P<fservice>
        (
            (?P<fscheme>
                (?P<direction>[<|>])?(?P<scheme>[^:/]*))
                ://
        )?
        (?P<xhost>
           (
                (?P<auth>
                   (?P<user>[^:@/]*?)
                   (:(?P<password>[^@/]*?))?
                )
            @)?
           (?P<host>[^@:/?]*)
           (:(?P<port>\d+))?
        )
    )?
    (?P<path>/[^?]*)?
    (\?(?P<query>[^#]*))?
    (\#(?P<fragment>.*))?
    """
)


def parse_uri(uri, bind=None, drop_nones=False, default=None, **kw):
    """Extended version for parsing uris:

    Return includes:

    - *query_*: dict with all query parameters splited

    If `bind` is passed, *localhost* will be replace by argument.

    """

    m = reg_uri.match(uri)
    if m:
        d = m.groupdict(default=default)
        # for k, v in d.items():
        #     if k not in kw or v is not None:
        #         kw[k] = v

        if bind:
            kw["host"] = d["host"].replace("localhost", bind)
        else:
            kw["host"] = d["host"]

        if d["port"]:
            kw["port"] = int(d["port"])
            kw["address"] = tuple([kw["host"], kw["port"]])
        if d["query"]:
            kw["query"] = d["query"]
            kw["query_"] = dict(parse.parse_qsl(d["query"]))
        else:
            kw["query_"] = {}

        kw["uri"] = uri

    soft(kw, d)
    if drop_nones:
        kw = {k: v for k, v in kw.items() if v is not None}
    return kw


# -----------------------------------------------------------
# Extended URI handling
# -----------------------------------------------------------
reg_xuri_old = re.compile(
    r"""(?isx)
((?P<fscheme>.*?)
:/
  (/
    (?P<xhost>[^/]+)
  )
)?
(?P<xpath>/[^?#]*?(/(?P<basename>[^?#]+))?)?
(\?(?P<query>[^#]*))?
(\#(?P<fragment>.*))?
$
"""
)

reg_xuri = re.compile(
    r"""(?imsx)
^
((?P<fscheme>.*?)(://))?
  (
    (?P<xhost>[^/]+)
  )?
(?P<xpath>/[^?#]*?(/?(?P<basename>[^/?#]+))?)?
(\?(?P<query>[^#]*))?
(\#(?P<fragment>.*))?
$
"""
)
REG_XURI = re.compile(
    r"""(?imsx)
^
(
  (?P<fscheme>.*?)
    (://)
)?
(
  (?P<xhost>
    (?P<host>[^/:]+)
      (:(?P<port>\d+))?
    )
)?
(?P<xpath>(?P<path>/?
  (?P<_path>[^?#]*?
    (/?
      (?P<basename>
        (?P<table>[^/:?]+)(:(?P<id>[^/?#]+))?
      )
    )?
  )
)?
(\?(?P<query>[^#]*))?
(\#(?P<fragment>.*))?
)
$
"""
)
HIE_REG_XURI = re.compile(
    r"""(?imsx)
(
  (?P<xhost>
    (?P<host>[^/:]+)
      (:(?P<port>\d+))?
    )
)?
(?P<xpath>/?
  (?P<_path>[^?#]*?
    (/?
      (?P<basename>
        (?P<table>[^/:?]+)(:(?P<id>[^/?#]+))?
      )
    )?
  )
)?
(\?(?P<query>[^#]*))?
(\#(?P<fragment>.*))?
$
"""
)

SUB_PATTERNS = {
    "xhost": re.compile(
        r"""(?imsx)
(
  (?P<auth>
   (?P<user>[^:@/]*?)
   (:(?P<password>[^@/]*?))?
  )
@)?
(?P<host>[^@:?]*)
(:(?P<port>\d+))?
"""
    ),
    #     'xpath_old': re.compile(
    #         """
    # (?imsx)
    # (?P<path>
    # /?
    # (?P<_path>[^:]+)
    # (:
    # (?P<id>[^:]+)
    # )?
    # )
    # """
    #     ),
    "xpath": re.compile(
        r"""(?imsx)
^
(?P<xpath>
 (?P<path>
 /?
  (?P<_path>
    [^:]+?
    (
    /
      (?P<basename>
        (?P<table>[^/:?]+)
      )
    )?
  )
  (
      [:]
      (?P<id>[^/:?#]*)
  )?
 )
)
(
  \?
  (?P<query>[^#]*)
)?
(\#(?P<fragment>.*))?
$
"""
    ),
}


def parse_xuri(uri, bind=None, drop_nones=False, default=None, **kw):
    """Extended version for parsing uris:

    Return includes:

    - *query_*: dict with all query parameters splited

    If `bind` is passed, *localhost* will be replace by argument.

    """
    m = REG_XURI.match(uri)
    if m:
        d = m.groupdict(default=default)
        if not d["fscheme"] and not d["xpath"] and uri and not uri.startswith("/"):
            m = REG_XURI.match(f"/{uri}")
            d = m.groupdict(default=default)

        for k, v in d.items():
            if k not in kw or v is not None:
                kw[k] = v

        # parse more complex sub-elements
        for key, regexp in SUB_PATTERNS.items():
            if value := kw.get(key):
                m = regexp.match(value)
                if m:
                    # soft(kw, m.groupdict())
                    kw.update(m.groupdict())
                    # overlap(kw, m.groupdict())

        if bind:
            kw["host"] = kw["host"].replace("localhost", bind)
        if port := kw.get("port"):
            kw["port"] = int(port)
            kw["address"] = tuple([kw["host"], kw["port"]])
        if query := kw.get("query"):
            kw["query_"] = dict(parse.parse_qsl(query))
        else:
            kw["query_"] = {}

    kw["uri"] = uri
    if uri == kw["_path"]:
        assert kw["id"] is None
        kw["id"] = uri

    if drop_nones:
        kw = {k: v for k, v in kw.items() if v is not None}
    return kw


REG_SPLIT_PATH = re.compile(
    """(?imsx)
    ^
    (?P<head>.*?)(:(?P<id>[^:]+))$
    """
)


def clean_uri(uri):
    _uri = parse_uri(uri)
    _uri["query_"] = _uri["query"] = None
    uri = build_uri(**_uri).strip("/")
    return uri


def build_uri(
    fscheme="",
    direction="",
    scheme="",
    xhost="",
    host="",
    port="",
    path="",
    query="",
    fragment="",
    query_={},
    id="",
    **kw,
):
    """Generate a URI based on individual parameters"""
    uri = ""
    if fscheme:
        uri += fscheme or ""
    else:
        if not direction:
            uri += scheme or ""
        else:
            uri += f"{direction}{scheme or ''}"
    if uri:
        uri += "://"

    if xhost:
        uri += xhost
    # else:
    # host = host or f"{uuid.getnode():x}"
    # uri += host
    # if port:
    # uri += f":{port}"

    if path:
        uri += f"{path}"

    if id:
        m = REG_SPLIT_PATH.match(path or "")
        if m:
            pass
            # assert id == m.groupdict()['id']
        else:
            uri += f":{id}"

    if query_ and not isinstance(query, str):
        # query_ overrides query if both are provided
        query = "&".join([f"{k}={v}" for k, v in query_.items()])

    elif isinstance(query, dict):
        query = "&".join([f"{k}={v}" for k, v in query.items()])

    if query:
        uri += f"?{query}"
    if fragment:
        uri += f"#{fragment}"

    return uri


# --------------------------------------------------
#  Convert Base
# --------------------------------------------------

# CHAR_LOOKUP = list(string.digits + string.ascii_letters)

#  avoid use of numbers (so can be used as regular attribute names with ".")
CHAR_LOOKUP = list(string.ascii_letters)
INV_LOOKUP = {c: i for i, c in enumerate(CHAR_LOOKUP)}


def convert_base(number, base, padding=-1, lookup=CHAR_LOOKUP) -> str:
    """Coding a number into a string in base 'base'

    results will be padded with '0' until minimal 'padding'
    length is reached.

    lookup is the char map available for coding.
    """
    if base < 2 or base > len(lookup):
        raise RuntimeError(f"base: {base} > coding map length: {len(lookup)}")
    mods = []
    while number > 0:
        mods.append(lookup[number % base])
        number //= base

    while len(mods) < padding:
        mods.append(lookup[0])

    mods.reverse()
    return "".join(mods)


def from_base(key, base, inv_lookup=INV_LOOKUP):
    """Convert a coded number in base 'base' to an integer."""
    number = 0
    keys = list(key)
    keys.reverse()
    w = 1
    for c in keys:
        number += INV_LOOKUP[c] * w
        w *= base
    return number


# def new_uid(base=50):
# number = uuid.uuid1()
# return convert_base(number.int, base)
SEED = 12345


def next_uid(base=50):
    global SEED
    SEED += 1
    return convert_base(SEED, base)


def new_uid():
    raw = str(time_ns())
    uid = hashlib.md5(raw.encode("utf-8")).hexdigest()
    return uid


# ------------------------------------------------
# File and config helpers
# ------------------------------------------------
def slug(text):
    text = text.strip()
    text = re.sub(r"\W", "_", text).lower()
    text = replace(text)
    last = ""
    while last != text:
        text, last = text.replace("__", "_"), text

    text = text.strip("_")
    return text


def replace(text, lower=True):
    text = str(text)
    if lower:
        text = text.lower()
    text = text.replace("á", "a")
    text = text.replace("é", "e")
    text = text.replace("í", "i")
    text = text.replace("ó", "o")
    text = text.replace("ú", "u")
    text = text.replace("à", "a")
    text = text.replace("è", "e")
    text = text.replace("ì", "i")
    text = text.replace("ò", "o")
    text = text.replace("ù", "u")

    text = text.replace("ä", "a")
    text = text.replace("ë", "e")
    text = text.replace("ï", "i")
    text = text.replace("ö", "o")
    text = text.replace("ü", "u")

    return text


# from xml.sax.saxutils import escape
# ------------------------------------------------
# jinja2 filters
# ------------------------------------------------
def escape(text: str):
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = text.replace('"', "&quot;")
    text = text.replace("'", "&apos;")
    return text


def fmt(value, fmt=">40"):
    fmt = "{:" + fmt + "}"
    try:
        value = fmt.format(value)
    except:
        pass
    return value


# ------------------------------------------------
# glom extensions
# ------------------------------------------------
def setdefault(obj, path, val, missing=dict):
    current = glom(obj, path, default=None)
    if current is None:
        assign(obj, path, val, missing=missing)
        return val
    return current


# ------------------------------------------------
# Converter functions
# ------------------------------------------------


def I(x):
    return x


def INT(x):
    if x is not None:
        try:
            if isinstance(x, str):
                if m := re.match(r"[^\d]*(\d)+", x):
                    x = m.group(1)

            return int(x)
        except Exception:
            pass
    return x


def FLOAT(x):
    if x is not None:
        try:
            if isinstance(x, str):
                if m := re.match(r"[^\d]*(\d+(\D\d+)?)", x):
                    x = m.group(1)
                    x = re.sub(r"\D", ".", x)

            return float(x)
        except Exception:
            pass
    return x


def BOOL(x):
    if isinstance(x, str):
        return x.lower() in ("true", "yes")
    try:
        return bool(x)
    except Exception:
        return x


def NOTNULL(x):
    if x:
        return True
    return False


def TEXT(x):
    if x is not None:
        try:
            return x.text
        except Exception:
            pass
    return x


def STR(x):
    if x is not None:
        try:
            return str(x)
        except Exception:
            pass
    return x


def SAFE_STR(x):
    if x is not None:
        x = str(x)
        x = re.sub(r"""[\(\)\<\>\"\'\=\;]""", "", x)
    return x


def MAC(x):
    if isinstance(x, str):
        if re.match(r"(?:[0-9a-fA-F]:?){12}", x):
            x = x.replace(":", "").lower()
    return x


def STRIP(x):
    if x is not None:
        try:
            return x.strip()
        except Exception:
            pass
    return x


def URL_HOST(x):
    if isinstance(x, str):
        try:
            _uri = parse_uri(x)
            return _uri["xhost"]
        except Exception:
            pass
    return x


def milliseconds_to_datetime(milliseconds: int | str) -> datetime:
    """Converts a date from YYYYMMDD format to datetime"""

    return datetime.utcfromtimestamp(int(milliseconds) / 1000)


def seconds_to_datetime(seconds: int | str) -> datetime:
    """Converts a date from YYYYMMDD format to datetime"""
    return datetime.utcfromtimestamp(int(seconds))


def TO_NS(x):
    return int(DATE(x).timestamp() * (10**9))


def NOW():
    return datetime.now()


def UTCNOW():
    return datetime.now(tz=timezone.utc)


def DATE(x) -> datetime:  # TODO
    if x is not None:
        if isinstance(x, str):
            if re.match(r"\d{19}$", x):
                return milliseconds_to_datetime(int(x) / 1000000)
            elif re.match(r"\d{13}$", x):
                return milliseconds_to_datetime(int(x) / 1000)
            elif re.match(r"\d{10}$", x):
                return milliseconds_to_datetime(x)
            try:
                # parse() fails with '611101' -> (year=2061, month=11, day=1)
                if re.match(r"2\d{3}", x):
                    x = parser.parse(x)
                elif re.match(r"[\d|.]+$", x):
                    x = DATE(int(x))
                else:
                    x = parser.parse(x)

            except parser.ParserError:
                pass
            except Exception as why:  # dateutil.parser._parser.ParserError:
                pass
        elif isinstance(x, (int, float)):
            if x >= 10**16:
                x = milliseconds_to_datetime(x / 1000000)
            elif x >= 10**13:
                x = milliseconds_to_datetime(x / 1000)
            elif x >= 10**10:
                x = milliseconds_to_datetime(x)
            elif x >= 10**9:  # > year 2000
                x = seconds_to_datetime(x)
            else:
                # TODO: REVIEW: maybe is simply a number
                # x = seconds_to_datetime(x)
                pass

    if isinstance(x, datetime):
        if not x.tzinfo:
            # x = x.replace(tzinfo=timezone.utc)
            # x = x.replace(tzinfo=LOCAL_TZ)
            x = pytz.utc.localize(x)
            x = x.astimezone(UTC_TZ)

    return x


def SDATE(x):
    y = DATE(x)
    if isinstance(y, datetime):
        return y.strftime("%Y-%m-%dT%H:%M:%SZ")
    return x


MULTIPLIERS = {"days": 24 * 3600, "hours": 3600, "min": 60}

TYPES_MAP = {
    datetime: DATE,
    int: INT,
    float: FLOAT,
    bool: BOOL,
    str: TEXT,
}


def DURATION(x):  # TODO
    if x is not None:
        if isinstance(x, str):
            m = re.match(
                r"""(?imx)
                ((?P<days>\d+)\s*(day|d.a))?\.*?
                ((?P<hours>\d+)\s*(hour|hora)(s)?)?\.*?
                ((?P<min>\d+)\s*min)?
                """,
                x,
            )
            if m:
                secs = 0
                for key, value in m.groupdict(default=0).items():
                    secs += MULTIPLIERS[key] * float(value)

        return timedelta(seconds=secs)


def COLOR(x):
    """Task color
    Ignore when if a "black" or "blue" color and let GP
    use default ones next time.
    """
    if x not in ("#8cb6ce", "#000000"):
        return x
    return x  # TODO: remove, this hack will remove default colors


def PRIORITY(x):
    """GanttProject PRIORITY.... (have not sense :) )"""
    return {
        "3": -2,  #  Lowest
        "0": -1,  #  Low
        None: 0,  #  Normal (missing)
        "2": 1,  #  High
        "4": 2,  #  Highest
    }.get(x, 0)


c1 = lambda item, value: issubclass(item, value)
c2 = lambda item, value: isinstance(item, value)


def c3(item, value):
    if isinstance(value, str):
        string = str(item)
        return re.match(value, string, re.I) or re.search(
            f"\\.{value}(\\W|$)", string, re.I
        )  # "<class 'swarmtube.particles.fiware.OrionParticleSync'>"


c4 = lambda item, value: getattr(item, "__name__", None) == value


def c5(item, value):
    if isinstance(value, str):
        string = tf(str(item)).replace("_", "")
        value = tf(str(value)).replace("_", "")
        return re.match(value, string, re.I) or re.search(
            f"\\.{value}(\\W|$)", string, re.I
        )  # "<class 'swarmtube.particles.fiware.OrionParticleSync'>"


def BASEOF(item, value):
    result = False

    for call in c1, c2, c3:
        try:
            result = call(item, value)
            if result:
                break
        except Exception:
            pass
    return result


def NAMEOF(item, value):
    result = False

    for call in c4, c3, c5:
        try:
            result = call(item, value)
            if result:
                break
        except Exception:
            pass
    return result


# ---------------------------------------------------------
# transformation helpers
# ---------------------------------------------------------
def tf(name, sep="_"):
    if isinstance(name, str):
        return re.sub(r"\W", sep, name)
    return name


# ------------------------------------------------
# console
# ------------------------------------------------

GREEN = "\033[32;1;4m"
RESET = "\033[0m"


last_sepatator = 40


def banner(
    header,
    lines=None,
    spec=None,
    sort_by=None,
    sort_reverse=True,
    output=print,
    color=GREEN,
):
    global last_sepatator
    lines = lines or []
    # compute keys spaces
    m = 1 + max([len(k) for k in lines] or [0])
    if isinstance(lines, dict):
        if sort_by:
            idx = 0 if sort_by.lower().startswith("keys") else 1
            lines = dict(
                sorted(
                    lines.items(),
                    key=lambda item: item[idx],
                    reverse=sort_reverse,
                )
            )
        _lines = []
        for k, v in lines.items():
            if spec:
                try:
                    v = glom(v, spec)
                except:
                    v = getattr(v, spec)

            line = f"{k.ljust(m)}: {v}"
            _lines.append(line)
        lines = _lines

    if lines:
        m = max([len(l) for l in lines])
        last_sepatator = m
    elif last_sepatator:
        m = last_sepatator
    else:
        m = max([40, len(header)]) - len(header) + 1

    # m = max([len(l) for l in lines] or [40, len(header)]) - len(header) + 1
    output(f"{color}{header}{' ' * m}{RESET}")
    for line in lines:
        output(line)
