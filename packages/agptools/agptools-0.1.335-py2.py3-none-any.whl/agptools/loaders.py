"""
A basic dynamic module loader
"""

import importlib
import inspect
import re
import os
import traceback
import sys
from typing import List
import yaml
import pickle
import hashlib

# ---------------------------------------------------------
# Loggers
# ---------------------------------------------------------

from .helpers import BASEOF, NAMEOF

from agptools.logs import logger

log = logger(__name__)

# subloger = logger(f'{__name__}.subloger')
# import jmespath


def load_yaml(path):
    if os.path.exists(path):
        return yaml.load(open(path, encoding="utf-8"), Loader=yaml.Loader)
    return {}


def save_yaml(data, path, force=True):  # TODO: force=False
    if force or not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        yaml.dump(data, open(path, "wt", encoding="utf-8"), Dumper=yaml.Dumper)
    return yaml.load(open(path, encoding="utf-8"), Loader=yaml.Loader)


# ----------------------------------------------------------
# Dynamic Loaders
# ----------------------------------------------------------


class Finder:
    CACHE = {}
    HANDLERS = {}
    SKIP = set(
        [
            "ctypes",
        ]
    )

    @staticmethod
    def blueprint(meta):
        """Create a blueprint for a meta search criteria"""
        keys = list(meta.keys())
        keys.sort()
        data = [(k, meta[k]) for k in keys]
        blue = pickle.dumps(data)
        blue = hashlib.md5(blue).hexdigest()
        return blue

    @staticmethod
    def mach(item, meta) -> bool:

        for key, value in meta.items():
            function = Finder.HANDLERS.get(key)
            if function:
                try:
                    if not function(item, value):
                        return False
                except Exception:
                    return False

        return True

    @classmethod
    def find_in_memory(cls, modules: List | str, force=False, flags=re.I, **meta):
        if not force:
            blueprint = cls.blueprint(meta)
            result = cls.CACHE.get(blueprint)
            if result:
                return result

        result = []
        visited = set()
        if isinstance(modules, str):
            modules = [modules]
        while missing := visited.symmetric_difference(sys.modules):
            for module_fqid in missing:
                if module_fqid in visited:
                    continue
                visited.add(module_fqid)
                # print(f"? {module_fqid}")
                if module_fqid in cls.SKIP:
                    continue
                for pattern in modules:
                    if re.match(pattern, module_fqid, flags):
                        break
                else:
                    continue

                # print(f"--> OK: {module_fqid}")

                module = sys.modules.get(module_fqid)
                if not module:
                    continue

                for name in dir(module):
                    try:
                        item = getattr(module, name)
                    except Exception:
                        continue

                    if cls.mach(item, meta):
                        # not sure we can use set() instead list()
                        if item not in result:
                            result.append(item)
                break  # rebuilt missing

        cls.CACHE[blueprint] = result

        return result


# Populate handlers
Finder.HANDLERS["name"] = NAMEOF
# Finder.HANDLERS["klass"] = lambda item, value: isinstance(item, value)
Finder.HANDLERS["klass"] = BASEOF


def mro(item, value):
    if isinstance(value, str):
        for layer in item.mro():
            if value in str(layer):
                return True
        return False
    return value in item.mro()


Finder.HANDLERS["mro"] = mro


class ModuleLoader:
    """A minimal and improved module loader class"""

    ACTIVE_PORT_KEY = "active_ports"
    ACTIVE_UNIT_KEY = "active_units"

    def __init__(self, top):
        self.root = self.get_project_root(use_sys_only=True)
        self.home = self.get_project_root(use_sys_only=False)

        #         tokens = root.split(os.path.sep)
        #         self.home = os.path.sep.join(tokens)
        #
        #         if tokens[-2] == tokens[-1]:
        #             self.root = os.path.sep.join(tokens[:-1])
        #         else:
        #             self.root = self.home

        self.top = self._resolve_top(top)

        if os.path.split(self.root)[-1] == os.path.split(self.home)[-1]:
            if self.home not in sys.path:
                # sys.path.insert(0, self.home)
                sys.path.append(self.home)

        self.active_ports = [".*"]
        self.load_config()

    @classmethod
    def get_project_root(cls, use_sys_only=False, exclude=".*/(tests|debugpy)"):
        """
        Obtain the root of the project, enabling imports such as <module>.a.b.c
        """

        def get_candidate(file, package):
            sep = os.path.sep
            path = file.split(sep)[:-1]
            tokens = package.split(".")[1:]
            for name in reversed(tokens):
                if name == path[-1]:
                    path.pop()
                else:
                    break
            return sep.join(path)

        def get_common(filename, path):
            bits = filename.split(path)
            if len(bits) > 1:
                return path

        candidates = []
        python_version = re.match(r"\d\.\d+", sys.version).group(0)

        frame = sys._getframe(0)
        rexgexp = f"{python_version}|{exclude}"
        sys_paths = [_ for _ in sys.path if not re.search(rexgexp, _)]
        while frame := frame.f_back:
            module = inspect.getmodule(frame)
            filename = frame.f_code.co_filename
            if python_version in filename or not (module and module.__package__):
                continue

            for path in sys_paths:
                if m := re.match(r"(?P<root>.*)/.venv/bin", path):
                    candidate = m.group(1)
                    if candidate not in candidates:
                        candidates.append(candidate)

                if candidate := get_common(filename, path):
                    if candidate not in candidates:
                        candidates.append(candidate)

            if not use_sys_only and (
                candidate := get_candidate(filename, module.__package__)
            ):
                if candidate not in candidates:
                    if not re.search(rexgexp, candidate):
                        candidates.append(candidate)

        # returns the top in the stack call
        return candidates[-1]

    def _resolve_top(self, top):
        """
        Resolve the `top` directory, ensuring it's valid.
        """
        if hasattr(top, "__file__"):  # `top` is a module
            if top.__file__:
                top = os.path.dirname(top.__file__)
            else:
                top = os.path.join(self.root, top.__package__)
        elif isinstance(top, str):
            top = os.path.join(self.home, top)
        return os.path.dirname(top) if os.path.isfile(top) else top

    def load_config(self, path="config.yaml"):
        """
        Load configuration from a YAML file to determine active ports.
        """
        for _path in self.find(type_="f", name=path):
            _path = os.path.abspath(_path)
            try:
                with open(_path, encoding="utf-8") as file:
                    cfg = yaml.load(file, Loader=yaml.Loader)
                self.active_ports = cfg.get(self.ACTIVE_PORT_KEY, self.active_ports)
                log.info(f"Loaded config from {_path}")
            except Exception as e:
                log.error(f"Error loading {_path}: {e}")
            break

    def match_any_regexp(self, name, active_ports, flags=0) -> bool:
        """
        Check if a name matches any regular expression in the active ports list.
        """
        _top = self.top.split(os.path.sep) + [name]
        for regex in active_ports:
            if re.search(regex, name, flags):
                return True
            _regexp = regex.split(".")
            if _top[-len(_regexp) :] == _regexp:
                return True
        return False

    def available_modules(self, active_ports=None) -> List[str]:
        """
        Discover all available modules that match the active ports.
        """
        names = []
        active_ports = active_ports or self.active_ports
        if not isinstance(active_ports, (list, set, tuple)):
            active_ports = [active_ports]

        for root, _, files in os.walk(self.top):
            for file in files:
                name, ext = os.path.splitext(file)
                if ext != ".py" or name.startswith("__"):
                    continue
                path = (
                    os.path.join(root, name).split(self.top)[-1].split(os.path.sep)[1:]
                )
                module_name = ".".join(path)
                if self.match_any_regexp(module_name, active_ports):
                    names.append(module_name)

        return sorted(names)

    def load_modules(self, names):
        """
        Dynamically load the specified modules.
        """
        # sys.path.insert(0, self.root)
        modules = []

        def module_exists(fqpath):
            return any(os.access(f"{fqpath}{ext}", os.F_OK) for ext in [".py", ".pyc"])

        def load(fqname):
            a, b = os.path.splitext(fqname)
            fqpath = a + b.replace(".", "/")
            for parent in sys.path:
                if not parent:
                    continue
                if os.path.isabs(fqpath):
                    split = fqpath.split(parent)
                    if len(split) > 1 and module_exists(fqpath):
                        name = "/".join(split[1:]).replace("/", ".")[1:]
                    else:
                        continue
                else:
                    name = fqname

                try:
                    if mod := sys.modules.get(name):
                        log.debug("Already loaded: [%s]", name)
                    else:
                        # log.info("Loading: [%s]", name)
                        mod = importlib.import_module(name)
                        log.info("Loading: [%s] OK", name)

                    modules.append(mod)
                    return True
                except ModuleNotFoundError:
                    log.info("Loading: [%s], not found", name)
                except Exception:
                    log.error(f"Error importing module: [{name}]")
                    log.error("".join(traceback.format_exception(*sys.exc_info())))
                    break
            return False

        for name in names:
            candidates = [f"{self.top}.{name}", name]
            for fqname in candidates:
                if load(fqname):
                    break

        return modules

    def find(self, type_=("d", "f"), name=".*", top=None):
        """
        Mimic the Unix `find` command to locate files or directories.
        """
        if isinstance(type_, str):
            type_ = [type_]

        top = top or [".", self.root]
        if isinstance(top, str):
            top = [top]

        for _top in top:
            for root, folders, files in os.walk(_top):
                candidates = {"d": folders, "f": files}
                for t in type_:
                    for item in candidates.get(t, []):
                        if re.match(name, item):
                            yield os.path.join(root, item)
