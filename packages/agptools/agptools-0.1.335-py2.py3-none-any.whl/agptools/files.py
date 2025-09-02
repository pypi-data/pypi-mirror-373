import fnmatch
import inspect
import os
import re
import types
import json

import lzma as xz
import bz2
import gzip
import magic
import ctypes

import tarfile
import zipfile
import io

from typing import List
from .containers import xml_text_to_dict


class ContentIterator:
    def __init__(self, name, raw, skip: List = None):
        self.name = name
        self.raw = raw

        self.ACTIONS = {
            r"gzip\scompressed\sdata": self.gzip,
            r"POSIX\star\sarchive\s": self.tar,
            r"zip": self.zip,
            r"XML.*.document": self.xml,
            r"JSON\s+data": self.json,
        }
        self.skip = skip or []

    def __iter__(self):
        yield from self._expand(self.name, self.raw)

    def _skip(self, type_):
        for pattern in self.skip:
            if re.match(pattern, type_, re.I):
                return True
        return False

    def _expand(self, name, raw):
        try:
            type_ = magic.from_buffer(raw)
            for pattern, action in self.ACTIONS.items():
                if re.match(pattern, type_, re.I) and not self._skip(type_):
                    for thing in action(name, raw):
                        yield from self._expand(**thing)
                    break
            else:
                yield {"name": name, "raw": raw}
        except ctypes.ArgumentError:
            yield {"name": name, "raw": raw}

    def gzip(self, name, raw):
        yield {"name": name, "raw": gzip.decompress(raw)}

    def xml(self, name, raw):
        yield {
            "name": name,
            "raw": xml_text_to_dict(raw, include_root=False),
        }

    def json(self, name, raw):
        yield {
            "name": name,
            "raw": json.loads(raw),
        }

    def tar(self, name, raw):
        # Use 'r:'
        with tarfile.open(fileobj=io.BytesIO(raw), mode="r:") as container:
            for i, item in enumerate(container):
                # print(item.name)  # Print the name of the file in the archive
                # Extract each file
                file = container.extractfile(item)
                yield {"name": item.name, "raw": file.read()}

    def zip(self, name, raw):
        with zipfile.ZipFile(io.BytesIO(raw), "r") as container:
            for i, item in enumerate(container.infolist()):
                with container.open(item) as file:
                    yield {"name": item.filename, "raw": file.read()}


def expandpath(path):
    if path:
        path = os.path.expanduser(path)
        path = os.path.expandvars(path)
        path = os.path.abspath(path)
        while path and path[-1] == "/":
            path = path[:-1]
    return path


def fileiter(
    top,
    regexp=None,
    wildcard=None,
    info="d",
    relative=False,
    exclude=None,
    neg_reg=None,
    stats=False,
    followlinks=True,
):
    """Iterate over files
    info == 'd'   : returns filename, regexp.groupdict()
    info == 's'   : same, but including mtime and file size
    info == 'g'   : returns filename, regexp.groups()
    info == None: : returns filename

    Allow single expressions or iterator as regexp or wildcard params
    """
    neg_reg = _prepare_test_regext(neg_reg, None)

    include = _prepare_test_regext(regexp, wildcard)
    exclude = _prepare_test_regext(exclude, None)

    if neg_reg and not include:
        include = _prepare_test_regext(".*", None)

    def do(filename, info):
        if info in ("s",):
            try:
                st = os.stat(filename)
            except:
                return
            stats = {
                "mtime": st.st_mtime,
                "size": st.st_size,
                "blocks": st.st_blocks,
            }
        else:
            stats = {}

        if relative:
            filename = filename.split(top)[-1][1:]

        m3 = _find_match(filename, exclude)
        if m3:
            return

        m4 = _find_match(filename, neg_reg)
        if m4:
            return

        m1 = _find_match(filename, include)
        m2 = _find_match(filename, exclude)

        if m1 and not m2:
            m1 = _return_matched_info(m1, info)
            if m1 is not None:
                m1.update(stats)
                return filename, m1
            else:
                return filename
        elif m2 and not m1:
            m2 = _return_matched_info(m2, info)
            if m2 is not None:
                m2.update(stats)
                return filename, m2
            else:
                return filename

    for root, _, files in os.walk(top, followlinks=followlinks):
        for name in files:
            filename = os.path.join(root, name)
            if os.path.sep != "/":
                filename = filename.replace(os.path.sep, "/")
            # print(filename)
            if res := do(filename, info):
                yield res


def file_lookup(pattern, path, appname=""):
    """Search for files in several folders using a strategy lookup.
    - pattern: relative or abspath
    - path: file or directory where to look until if reac
    """
    debug = os.environ.get("DEBUG", False)

    root, name = os.path.split(pattern)
    if root:
        pattern = expandpath(pattern)

    path = path or "."
    if os.path.isabs(pattern):
        candidates, pattern = os.path.split(pattern)
        candidates = [candidates]
    else:
        candidates = [f"/etc/{appname}"]
        # include all folders from stack modules in memory
        stack = inspect.stack()
        while stack:
            dirname = os.path.dirname(stack.pop(0)[0].f_code.co_filename)
            if dirname and dirname not in candidates:
                candidates.append(dirname)

        # include some special folders
        for _ in [
            os.path.dirname(__file__),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "data"),
            f"~/.config/{appname}",
            f"~/{appname}",
            path,
            ".",
        ]:
            if _ not in candidates:
                candidates.append(_)

        debug and print(f"CAND: {candidates}")

    # expand all parents for each candidate
    folders = []
    for path in candidates:
        head = tail = expandpath(path)
        ascend = list()
        while tail:
            ascend.append(head)
            head, tail = os.path.split(head)

        ascend.reverse()
        # add only new ones (is faster here that check twice later)
        for path in ascend:
            if path not in folders:
                debug and print(f"+ {path}")
                folders.append(path)

    debug and print(f"FOLD: {folders}")
    for root in folders:
        path = os.path.join(root, pattern)
        path = os.path.expanduser(path)
        path = os.path.expandvars(path)
        if not os.path.exists(path):
            # debug and print(f"not exist:  {path}? - no")
            continue
        debug and print(f"> exists: {path}? - yes")
        yield path


def parse_string(string, regexp=None, wildcard=None, info=None):
    test = _prepare_test_regext(regexp, wildcard)
    m = _find_match(string, test)
    if m:
        return _return_matched_info(m, info)
    return _return_unmatched(info)  # to return compatible values in upper stack


def _prepare_test_regext(regexp=None, wildcard=None, test=None):
    test = test or list()

    if isinstance(regexp, (list, tuple, set)):
        test.extend(regexp)
    else:
        test.append(regexp)

    if not isinstance(wildcard, (list, tuple)):
        wildcard = [wildcard]
    for wc in wildcard:
        if wc and isinstance(wc, str):
            wc = fnmatch.translate(wc)
            test.append(wc)

    test = [re.compile(m).search for m in test if m]

    return test  # you can compile a compiled expression


def _find_match(string, test):
    b_m, b_d = None, {}
    for reg in test:
        if isinstance(reg, types.BuiltinFunctionType):
            m = reg(string)
        else:
            m = reg.search(string)
        if m:
            candidate = m.groupdict()
            if len(candidate) > len(b_d):
                b_m, b_d = m, candidate
            if not candidate and not b_d:
                # print(f"warning: string match but no groups are defined.")
                b_m = m

    return b_m

    # if test:
    # for match in test:
    # m = match(string)
    # if m:
    # return m


def _return_matched_info(m, info):
    if info in ("d", "s"):
        return m.groupdict()
    elif info == "g":
        return m.groups()
    return None
    # return m.group(0)


def _return_unmatched(info):
    if info in ("d", "s"):
        return dict()
    elif info == "g":
        return list()
