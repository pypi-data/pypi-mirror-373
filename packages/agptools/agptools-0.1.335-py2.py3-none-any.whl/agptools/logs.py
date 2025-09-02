"""Logs support"""

import os
import re
import tempfile
import time
import gzip

# import zlib
import threading
import random

import lzma as xz
from datetime import datetime, timedelta


from .colors import *

from .configurations import merge_config


class iLog:
    """Interface for logging into console."""

    def __init__(self):
        self.colorize = True
        self.styles = {
            "ok": GREEN,
            "banner": GREEN,
            "bright": PURPLE,
            "ok": GREEN,
            "debug": GRAY,
            "warn": YELLOW,
            "error": RED,
            "result": CYAN,
            "show": CYAN,
            "default": RESET,
        }
        self.indent = 0
        self.current_style = None

    def set_style(self, _style_=None):
        self.current_style = _style_

    def _line(self, pattern, _max_=100, **data):
        try:
            line = pattern.format(**data)
        except KeyError:
            line = pattern

        if len(line) > _max_:
            line = line[: _max_ - 3] + "..."

        return line

    def log(self, pattern, _style_="bright", **data):
        line = self._line(pattern, **data)
        if self.colorize:
            style = self.styles.get(
                _style_ or self.current_style, self.styles["default"]
            )
            line = f"{style}{line}{RESET}"
        print(f"{'  ' * self.indent}{line}")

    def show(self, pattern, **data):
        self.log(pattern, _style_="show", **data)

    def debug(self, pattern, **data):
        self.log(pattern, _style_="debug", **data)

    def ok(self, pattern, **data):
        line = self._line(pattern, **data)
        self.log(f"ok, {line}", _style_="ok", **data)

    def warn(self, pattern, **data):
        line = self._line(pattern, **data)
        self.log(f"{line}", _style_="warn", **data)

    def error(self, pattern, _raise_=RuntimeError, **data):
        line = self._line(pattern, **data)
        self.log(f"** ERROR: {line} **", _style_="error", **data)
        if _raise_:
            raise _raise_(line)

    def banner(self, line, _style_="banner"):
        sep = "=" * 70
        self.log(f"{sep}", _style_=_style_)
        self.log(line, _style_=_style_)
        self.log(f"{sep}", _style_=_style_)

    def _inc_indent(self):
        self.indent += 1

    def _dec_indent(self):
        self.indent -= 1

    def __enter__(self):
        self._inc_indent()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            foo = 1
        self._dec_indent()


# -------------------------------------------------------------
# loggers
# -------------------------------------------------------------

import logging
import logging.config
import yaml
import sys
import re
import os.path
import traceback

from logging.handlers import TimedRotatingFileHandler, MemoryHandler

# from uswarm.tools import expandpath, get_calling_function
# from uswarm.tools import merge_config

exclude = re.compile(r"(self|_.*)", re.DOTALL)
include = re.compile(r"(.*)", re.DOTALL)
# exclude = re.compile(r"(_.*)", re.DOTALL)


def addLoggingLevel(levelName, levelNum, methodName=None):
    """
    Comprehensively adds a new logging level to the `logging` module and the
    currently configured logging class.

    `levelName` becomes an attribute of the `logging` module with the value
    `levelNum`. `methodName` becomes a convenience method for both `logging`
    itself and the class returned by `logging.getLoggerClass()` (usually just
    `logging.Logger`). If `methodName` is not specified, `levelName.lower()` is
    used.

    To avoid accidental clobberings of existing attributes, this method will
    raise an `AttributeError` if the level name is already an attribute of the
    `logging` module or if the method name is already present

    Example
    -------
    >>> addLoggingLevel('TRACE', logging.DEBUG - 5)
    >>> logging.getLogger(__name__).setLevel("TRACE")
    >>> logging.getLogger(__name__).trace('that worked')
    >>> logging.trace('so did this')
    >>> logging.TRACE
    5

    """
    if not methodName:
        methodName = levelName.lower()

    if hasattr(logging, levelName):
        pass
        # raise AttributeError("{} already defined in logging module".format(levelName))
    if hasattr(logging, methodName):
        pass
        # raise AttributeError("{} already defined in logging module".format(methodName))
    if hasattr(logging.getLoggerClass(), methodName):
        pass
        # raise AttributeError("{} already defined in logger class".format(methodName))

    # This method was inspired by the answers to Stack Overflow post
    # http://stackoverflow.com/q/2183233/2988730, especially
    # http://stackoverflow.com/a/13638084/2988730
    def logForLevel(self, message, *args, **kwargs):
        if self.isEnabledFor(levelNum):
            self._log(levelNum, message, args, **kwargs)

    def logToRoot(message, *args, **kwargs):
        logging.log(levelNum, message, *args, **kwargs)

    logging.addLevelName(levelNum, levelName)
    setattr(logging, levelName, levelNum)
    setattr(logging.getLoggerClass(), methodName, logForLevel)
    setattr(logging, methodName, logToRoot)


addLoggingLevel("VERBOSE", logging.DEBUG - 5)
addLoggingLevel("TRACE", logging.DEBUG + 5)


def logger(name, path=None, config="logging.yaml"):
    """Get a logger from logger system.
    The config file and handlers are loaded just once
    avoiding to truncate log files when loggers are
    required and returned.

    default folders to find logging yaml configuration file are:

    ~/
    ~/.config/
    <module_path>/
    /etc/

    and all the levels from current path until '/' is reached

    Aplication merges configuration in reverse order like class hierarchy

    """

    # name = ".".join(name.split(".")[-2:])
    # name = ".".join(name.split("."))

    # try to get a good name for logger
    # 1. split name by '.'
    # 2. search until last token is repeated (i.e. uswarm.uswarm.xxxx)
    # 3. or lenght > 4
    goodname, last = [], None
    for i, token in enumerate(reversed(name.split("."))):
        if i > 4 or token == last:
            break
        last = token
        goodname.insert(0, token)
    name = ".".join(goodname)

    log = logging.getLogger(name)

    if not log.handlers:
        lock_file = f"{config}.lock"
        # it seems like logging is not configured already
        # let's try to load a config file and / or update logging.yaml config file
        while True:
            content = f"{os.getpid()}:{random.random()}"
            try:
                mtime = os.stat(lock_file).st_mtime
                if time.time() - mtime > 10:
                    os.unlink(lock_file)
                else:
                    time.sleep(1 + random.random())
                    continue
            except FileNotFoundError as why:
                pass
            try:
                open(lock_file, "w").write(content)
                existing = open(lock_file).read()
                if existing == content:
                    break

            except Exception as why:
                print(f"exception trying to lock: {lock_file}")
            print(f"waiting to lock {lock_file}")

            time.sleep(1 + random.random())

        if os.access(config, os.F_OK):
            # load local config file
            try:
                conf = yaml.load(open(config, "rt"), Loader=yaml.Loader)
            except Exception as why:  # TODO: ParseError
                conf = {}
        else:
            # search other user config files as default templates
            conf = merge_config(config, path)

        # print(f">> Looking for logger: '{name}' path={path} {'-'*40}")
        if not conf:
            # create a initial config file
            text = """
formatters:
  simple:
    format: '{asctime} {levelname:>5} {message}'
    style: '{'
  trace:
    format: '{asctime} {name:15} {levelname:8} {message}'
    style: '{'
  traffic:
    format: '{asctime} {name:3} {message}'
    style: '{'
handlers:
  console:
    class: logging.StreamHandler
    formatter: simple
    level: INFO
    stream: ext://sys.stdout

loggers:
  .:
    handlers: []
    level: DEBUG
    propagate: false

root:
  handlers:
  - console
  level: INFO
version: 1
"""
            open(config, "w", encoding="utf-8").write(text)
            conf = yaml.load(open(config, "rt"), Loader=yaml.Loader)

        if conf:
            try:
                logging.config.dictConfig(conf)
            except Exception as why:
                log.warning("can not configure logger using:")
                log.warning(f"{conf}")
                log.warning("trying to continue ...")
            log = logging.getLogger(name)
            if not log.handlers:
                # print(f"** Logger: '{name}' is not defined in {config}")

                # add the logger with a default configuration
                if name not in conf["loggers"]:
                    l = conf["loggers"][name] = {}
                    l.update(
                        {
                            "level": "DEBUG",
                            "propagate": False,
                            "handlers": [f"{name}.xz", "console"],
                        }
                    )
                # add handler
                # sub = '.logs'
                sub = os.path.splitext(
                    __file__.replace("/", ".").split(__package__)[-1]
                )[0]

                h = conf["handlers"].setdefault(f"{name}.xz", {})
                h.update(
                    {
                        "class": f"{__package__}{sub}.ZTimedRotatingFileHandler",
                        "level": "DEBUG",
                        "formatter": "simple",
                        "filename": f"logs/{name}.log",
                        "when": "H",
                        "interval": 1,
                        "max_days": 14,
                        "max_size_mb": 500,
                        "backupCount": 15,
                        "extension": ".xz",
                    }
                )
                try:
                    yaml.dump(conf, open(config, "wt"), default_flow_style=False)
                except PermissionError:
                    # print(f"can't save: {config} config file, continue")
                    pass

                logging.config.dictConfig(conf)
                log = logging.getLogger(name)
                assert log.handlers, "something was wrong adding new loggers!?"

        else:
            # print(f"  ** can not find a '{config}' file in your system!")
            pass

        try:
            os.unlink(lock_file)
        except FileNotFoundError as _why:
            pass

    return log


def trace(
    message="",
    context=None,
    name=None,
    log=None,
    exclude=exclude,
    include=include,
    level=logging.INFO,
    frames=1,
):
    parent = sys._getframe(frames)
    name = name or parent.f_code.co_name

    if context == None:
        context = parent.f_locals

    self = context.get("self")

    if not isinstance(exclude, re.Pattern):
        exclude = re.compile(exclude, re.DOTALL)
    if not isinstance(include, re.Pattern):
        include = re.compile(include, re.DOTALL)

    ctx = (
        dict(
            [
                (k, v)
                for k, v in context.items()
                if include.match(k) and not exclude.match(k)
            ]
        )
        or ""
    )

    if not log:
        mod = parent.f_globals
        log = mod.get("log") or logger(mod["__name__"])

    if self:
        label = str(self)
        log.log(level, f"{label:>12}.{name}(): {message} {ctx}")
    else:
        log.log(level, f"{name}(): {message} {ctx}")


def _debug(*args, **kw):
    return trace(level=logging.DEBUG, frames=2, *args, **kw)


def _error(*args, **kw):
    return trace(level=logging.ERROR, frames=2, *args, **kw)


def _warn(*args, **kw):
    return trace(level=logging.WARN, frames=2, *args, **kw)


def _info(*args, **kw):
    return trace(level=logging.INFO, frames=2, *args, **kw)


def debug(*args, **kw):
    kw["context"] = {}
    return trace(level=logging.DEBUG, frames=2, *args, **kw)


def info(*args, **kw):
    kw["context"] = {}
    return trace(level=logging.INFO, frames=2, *args, **kw)


def warn(*args, **kw):
    kw["context"] = {}
    return trace(level=logging.WARN, frames=2, *args, **kw)


def error(*args, **kw):
    kw["context"] = {}
    return trace(level=logging.ERROR, frames=2, *args, **kw)


def exception(*args, **kw):
    # trace(level=logging.ERROR, frames=2, *args, **kw)
    exc_type, exc_value, exc_tb = sys.exc_info()
    tb = traceback.format_exception(exc_type, exc_value, exc_tb)
    tb = "".join(tb)
    trace(message=tb, level=logging.ERROR, frames=2)
    print(tb)
    foo = 1


# ----------------------------------------------------------
# Custom rotation files
# ----------------------------------------------------------


class ZTimedRotatingFileHandler(TimedRotatingFileHandler):
    """

    self.suffix:       '%Y-%m-%d_%H-%M-%S'
    self.baseFilename: '/home/agp/workspace/atlas/compressed.log'

    self.rotation_filename()
    self.getFilesToDelete()

    """

    library = {
        ".gz": [gzip.compress, {}],
        ".xz": [xz.compress, {}],
    }

    aliases = {".gzip": ".gz"}

    def __init__(
        self,
        filename,
        max_days: int = 14,
        max_size_mb=500,
        extension=".gz",
        folder="xz",
        threaded=True,
        *args,
        **kw,
    ):
        parent = os.path.dirname(filename)
        try:
            os.makedirs(parent, exist_ok=True)
        except PermissionError as why:
            print(f"Error: {filename} : {why}")
            tmp = tempfile.gettempdir()  # /tmp or c:/temp
            filename = os.path.join(tmp, os.path.basename(filename))
            print(f"replacing by: {filename}")

        super().__init__(filename=filename, *args, **kw)
        self.extension = extension
        self.max_size = max_size_mb * 1024 * 1024
        self.max_days = max_days
        self.folder = folder
        self.threaded = threaded
        self.rotator = self._rotator

    # name the compressed file
    def namer(self, name):
        return name + self.extension

    # read the data from source, compress it, write it to dest and delete source
    def _rotator(self, source, dest):
        def folding(path):
            return os.path.join(
                os.path.dirname(path), self.folder, os.path.basename(path)
            )

        self.t0 = time.time()
        temp = source + ".tmp"
        temp = folding(temp)
        os.renames(source, temp)
        source = temp
        if not dest.endswith(self.extension):
            dest += self.extension

        dest = folding(dest)

        def comp():
            try:
                self.s0 = os.path.getsize(source)
                _, ext = os.path.splitext(dest)
                ext = self.aliases.get(ext, ext)
                compressor, kw = self.library[self.extension]
                with open(source, "rb") as sf:
                    with open(dest, "wb") as df:
                        df.write(compressor(sf.read(), **kw))
                os.remove(source)
            except Exception as why:
                print(f"{why}")

            self.elapsed = time.time() - self.t0
            self.s1 = os.path.getsize(dest)
            self.ratio = self.s1 / (self.s0 or 1)
            # print(
            # f"compression time: {os.path.basename(dest)} {self.elapsed:.4} secs: ratio: {self.ratio:.2%}"
            # )

        if self.threaded:
            threading.Thread(target=comp).start()
        else:
            comp()

    def getFilesToDelete(self):
        """
        Determine the files to delete when rolling over.
        Return files order that deadline
        Return more older files until disk size is under control.

        """

        top, base_name = os.path.split(self.baseFilename)
        pattern, ext = os.path.splitext(base_name)
        pattern = base_name + "(?P<date>.*)\\" + self.extension

        result = []
        remain = []
        total_size = 0
        last_day = datetime.today() - timedelta(days=self.max_days)
        last_day = last_day.timestamp()
        for root, folders, files in os.walk(top):
            for name in files:
                if re.search(pattern, name):
                    filename = os.path.join(root, name)
                    stats = os.stat(filename)
                    if stats.st_mtime < last_day:
                        result.append(filename)
                    else:
                        remain.append((stats.st_mtime, filename, stats.st_size))
                        total_size += stats.st_size

        # strip older files until disk size is under control
        remain.sort(key=lambda x: x[0])

        max_logs = len(remain)
        for mtime, filename, size in remain:
            if total_size < self.max_size and max_logs < self.backupCount:
                break
            result.append(filename)
            total_size -= size
            max_logs -= 1

        return result


class ReportHandler(MemoryHandler):
    """
    A handler class that keep logs in memory to create a report.
    """

    def __init__(
        self,
        capacity,
        flushLevel=logging.ERROR,
        target=None,
        flushOnClose=True,
    ):
        super().__init__(capacity, flushLevel, target, flushOnClose)


# ----------------------------------------------------------
# Log array
# ----------------------------------------------------------
def log_container(log, container, fmt=None, lines=4, level=logging.DEBUG):
    pair = False
    line_fmt = "[{i:3}] {raw}"
    if isinstance(container, (list, tuple)):
        gen = enumerate(container)
    elif isinstance(container, dict):
        gen = enumerate(container.items())
        pair = True
        if container:
            m = str(max([len(str(k)) for k in container]) + 2)
        else:
            m = "2"
        line_fmt = "[{i:3}] {key:" + m + "} : {raw}"

    else:
        raise RuntimeError(f"Not a valid container: {container.__class__}")

    l = len(container) - lines
    for i, data in gen:
        if i < lines or i > l:
            if pair:
                key, data = data

            if isinstance(data, dict) and fmt:
                raw = fmt.format_map(data)
            else:
                raw = str(data)

            line = line_fmt.format(**locals())  # f"[{i}] {key:50} : {raw}"

            # if pair:
            # else:
            # line = f"[{i}] {raw}"

            log.log(level, line)
        elif i == lines:
            log.log(level, "." * 20)

    log.log(level, f"{len(container)} items")
    foo = 1
