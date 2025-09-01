"""
Helpers for loading, saving, merging, expand and condense config files.

- [ ] create a config file asking some questions to user.
- [ ] helpers to automatic guess some config values: app name, etc.
- [ ] load / save files in many formats: yaml, json, pickle, ini

Future:

- [ ] get a list of candidate names based on non-standard
    modules found in the stack.
"""

import os
import re
import time
import yaml
import json
import inspect

from collections import deque

import glom


from colorama import Fore

from .files import expandpath, fileiter, file_lookup
from .containers import (
    soft,
    sitems,
    merge,
    Dom,
    register_container,
    rebuild,
    walk,
    convert_container,
)


# ------------------------------------------------------
# Creating config file for 1st time
# ------------------------------------------------------


def populate_default_context(ctx):
    app_name = guess_app_name()
    ctx.setdefault("app_name", app_name)

    # gather all $APP related ENV
    for k, v in os.environ.items():
        if re.search(app_name, k, re.I):
            ctx[k] = v

    app_home = os.environ.get(f"{app_name.upper()}_HOME", f"~/workspace/{app_name}")
    app_home = expandpath(app_home)
    ctx.setdefault("home", app_home)
    # ctx.setdefault("config_file", guess_configfile_name())
    ctx.setdefault("config_file", "{home}/config.yml".format_map(ctx))
    ctx.setdefault("logs_folder", "logs".format_map(ctx))
    ctx.setdefault("xlogs_folder", expandpath("{home}/logs".format_map(ctx)))

    return ctx


def get_app_fqname():
    """Try o guess ythe fqname."""
    for stack in inspect.stack():
        frame, path, line, func_name, code_lines, _ = stack
        app = frame.f_locals.get("app")
        if app:
            return app.__module__.split(".")[0]


def guess_app_name():
    """Try to guess application name from calling module info.

    Example:

    Calling from a function in 'atlas.controllers.historical' module
    it yields:

    'atlas'

    TODO: get a list of candidate names based on non-standard
    modules found in the stack.

    """
    name = os.environ.get("APP")
    if not name:
        fqname = get_app_fqname()
        if fqname:
            name = fqname.split(".")[0]
    return name


def guess_configfile_name():
    """Guess a config file name based on the calling module to the function

    Example:

    Calling from a function in 'atlas.controllers.historical' module
    it yields:

    '~/.config/atlas/historical.yaml'

    """
    fqname = get_app_fqname()
    if fqname:
        mod = fqname.split(".")
        if len(mod) > 1:
            return f"~/.config/{mod[0]}/{mod[-1]}.yaml"

        return f"~/.config/{mod[0]}.yaml"


def dict_sp(item):
    """convert a ':' separate string into dict.

    key:value

    """
    items = [t.strip().split(":") for t in item.split(",")]

    result = {}
    for k, v in items:
        result.setdefault(k, list()).append(v)

    return result


def merge_user_config(
    qst, ctx=None, prompt=None, save=True, automatic=False, prefix="", show_config=True
):
    """Ask user a list of questions for configure the app.

    - qst: { key: text } the questions and where to place in config.
    - defaults: default values for any key (if provided or required)
    - prompt: the mecanism for asking questions: console input by default.
    - save: boolean for writing the config in a YAML format.

    """

    def place(holder, keys, value):
        # root = holder # just debug
        _keys = keys.split(":")
        last_key = _keys.pop()
        klass = dict
        # try:
        # idx = int(last_key)
        # klass = list
        # except ValueError:
        # klass = dict

        # last_holder = holder
        for i, key in enumerate(_keys):
            if i == 0 and key in ("",):
                continue  # ignore 'absolute' key referencing
            # last_holder = holder
            new_holder = holder.get(key)
            if new_holder in (
                None,
                "None",
            ):  # fix when holder[key] exists and is None
                new_holder = holder[key] = klass()
            holder = new_holder

        # if not isinstance(holder, klass):
        # assert len(last_holder[key]) == 0
        # holder = last_holder[key] = klass()

        if isinstance(holder, dict):
            holder[last_key] = value
        elif isinstance(holder, list):
            holder.append(value)
        elif isinstance(holder, set):
            holder.add(value)
        else:
            raise RuntimeError(
                f"don't know how to add '{keys}' value into '{holder.__class__}' instance"
            )

    def myinput(text):
        print(text)
        result = input()
        return result

    def accept(text):
        m = re.search(r"\[([^\]]+)\]", text)
        answer = "Y"
        if m:
            answer = m.group(1)

        if answer.lower().strip() == "y/n":
            answer = "Y"

        print(f"{text} {Fore.MAGENTA}{answer}{Fore.RESET}")
        return answer

    if ctx is None:
        ctx = {}
    populate_default_context(ctx)

    # try to load and merge the config
    current = {}
    try:
        current = (
            yaml.load(open(expandpath(ctx["config_file"]), "rt"), Loader=yaml.Loader)
            or current
        )
        soft(ctx, **current)
    except Exception as why:
        foo = 1

    # start the user *interrogatory* :P
    wide = 2 + max(len(expand_config(key, ctx)) for key in qst)

    # default value must be enclosed by [...] in order to detect
    # when user anwer with ENTER accepting the shown value.
    template = "{key:wide}: [{default}] ?".replace("wide", str(wide))

    if automatic:
        prompt = accept
    else:
        prompt = prompt or input  # myinput # input

    def ask_user(prefix, questions):
        nonlocal ctx
        delated = []

        print(Fore.GREEN)
        print("-" * 60)
        print(f"Section: {prefix.replace(':', '/')}")
        print("-" * 60)
        print(Fore.RESET, end="")
        foo = 1
        for key, value in questions.items():
            ctx = expand_config(ctx)
            key = expand_config(key, ctx)
            if isinstance(value, tuple):
                value, klasses = value
            elif isinstance(value, dict):
                delated.append((f"{prefix}:{key}", value))
                continue
            else:
                klasses = str

            default = expand_config(value, ctx)
            text = template.format(**locals())

            # TODO user more sofisciacated promps (e.g. cement.utils.shell.Prompt)
            response = prompt(text)
            response = response or accept(text)  # use default value shown to user
            response = convert_container(response or default, klasses)

            # now we need to convert default in case it would be used
            place(current, f"{prefix}:{key}", response)
            place(ctx, key, response)
        # now we process all delayed pending questions
        for params in delated:
            ask_user(*params)
        foo = 1

    ask_user(prefix, qst)

    # check if we must save the config file.
    if save:
        # raw = yaml.dump(subset, default_flow_style=False)
        template = "{key:wide}: {value}".replace("wide", str(wide))
        if show_config:
            print(Fore.GREEN + "-" * 60)
            print(yaml.dump(current))
            print(Fore.RESET)
            # for key, value in current.items():
            # raw = template.format(**locals())
            # print(f"{Fore.GREEN}{raw}{Fore.RESET}")

            print()
        file = ctx.get("config_file")
        response = prompt(f"Save {file} file? [y/N] ") or "N"
        if response.upper() == "Y":
            save_config(current, file, condense=False)

    return current


# ------------------------------------------------------
# Automatic guessing some config values: app name, etc.
# ------------------------------------------------------


# ------------------------------------------------------
# Expand / Condense config values.
# ------------------------------------------------------
def expand_config(config, context=None, **env):
    """Expand a configuration against a context.

    Example:

    {'done': '{repository}/__done__',
    'inbox': ['{repository}/__inbox__'],
    'repository': '{workspace}/repository',
    'workspace': '~/workspace'}

    will returns:

    {'done': '~/workspace/repository/__done__',
    'inbox': ['~/workspace/repository/__inbox__'],
    'repository': '~/workspace/repository',
    'workspace': '~/workspace'}

    """
    if context is None:
        if isinstance(config, dict):
            context = config
        else:
            context = {}

    env.update(context)
    if isinstance(config, str):
        config = os.path.expandvars(config)
        try:
            config = config.format(**env)
        except:
            foo = 1
        return config

    if isinstance(config, dict):
        result = dict()
        for k, item in config.items():
            last = None
            while last != item:
                last = item
                item = expand_config(item, env)
            result[k] = item
        return result

    if isinstance(config, list):
        result = list()
        for item in config:
            last = None
            while last != item:
                last = item
                item = expand_config(item, env)
            result.append(item)
        return result

    return config
    # raise RuntimeError(f"can expand {config}")


def condense_config(config, context=None):
    """Inverse operation of expand_config.

    Example:

    {'done': '~/workspace/repository/__done__',
    'inbox': ['~/workspace/repository/__inbox__'],
    'repository': '~/workspace/repository',
    'workspace': '~/workspace'}

    will returns:

     {'done': '{repository}/__done__',
    'inbox': ['{repository}/__inbox__'],
    'repository': '{workspace}/repository',
    'workspace': '~/workspace'}

    """
    if context is None:
        context = config

    if isinstance(config, str):
        k_best, v_best = None, ""
        for k, v in context.items():
            if isinstance(v, str):
                if v in config and len(v) > len(v_best):
                    k_best, v_best = k, v
        if v_best:
            return config.replace(v_best, "{%s}" % k_best)
        return config

    if isinstance(config, dict):
        result = dict()
        for k, item in config.items():
            last = None
            while last != item:
                last = item
                ctx = dict(context)
                ctx.pop(k, None)
                item = condense_config(item, ctx)
            result[k] = item
        return result

    if isinstance(config, list):
        result = list()
        for item in config:
            last = None
            while last != item:
                last = item
                item = condense_config(item, context)
            result.append(item)
        return result

    if isinstance(config, (bool, int, float)):  # not 'condensables'
        return config

    if hasattr(config, "__str__"):
        return config.__str__()

    raise RuntimeError(f"can not condense {config}")


def merge_config(pattern, srcfile=None, appname=""):
    """Merge config files using the same lookup pattern"""
    conf = dict()
    debug = os.environ.get("DEBUG", False)
    for path in file_lookup(pattern, srcfile, appname=appname):
        debug and print(f"loading: {path}")
        c = yaml.load(open(path), Loader=yaml.FullLoader)
        if c is None:
            continue
        # merge with existing values
        if debug:
            for name in c.get("loggers", {}):
                print(f" - {name}")

        for section, values in c.items():
            if isinstance(values, dict):
                org = conf.setdefault(section, dict())
                org.update(values)
            else:
                conf[section] = values
    return conf


# ------------------------------------------------------
# Load / Save / Process configuration files
# ------------------------------------------------------


def load_config(path, **kw):
    """Load a config file based on extension format.
    - .yaml
    - .json
    - .conf : bash unix style
    - .ini

    by default use 'yaml' format.
    """

    #: ext: funcion, default params
    loader = {
        "yaml": [
            yaml.load,
            {
                "Loader": yaml.FullLoader,
            },
        ],
        "json": [json.load, {}],
        "conf": [load_config_bash, {}],
    }

    config = dict()
    path = expandpath(path)
    if path and os.path.exists(path):
        ext = os.path.splitext(path)[-1][1:]
        if ext not in loader:
            ext = "yaml"
        loader, kwargs = loader[ext]
        kwargs = dict(kwargs)
        kwargs.update(kw)
        with open(path, "r", encoding="utf-8") as f:
            config = loader(f, **kwargs) or config
    return config


def save_config(config, srcfile, condense=True):
    """Save a configuration file and try to condense
    if required.


    """

    if condense:
        config = condense_config(config)

    # create parent folders
    srcfile = expandpath(srcfile)
    root, path = os.path.split(srcfile)
    os.makedirs(root, exist_ok=True)

    # and get the dumper

    library = {
        ".yaml": [
            yaml.dump,
            {
                "default_flow_style": False,
            },
        ],
        ".json": [json.dump, {}],
        # "conf": [None, {}],  # TODO: implement bash config format
    }

    aliases = {".yml": ".yaml"}

    ext = os.path.splitext(path)[-1]
    ext = aliases.get(ext, ext)
    dumper, kwargs = library.get(ext) or library[".yaml"]

    # save the file
    dumper(config, open(srcfile, "w", encoding="utf-8"), **kwargs)
    return config  # return the (condensed) configuration


def process_config(path, mode="add", **ctx):
    """process some special fields to enhance the current config:

    Some additional features are:

    - include other files
    - xxx


    """
    config = load_config(path, **ctx)
    config = expand_config(config, **ctx)
    # 1, include other files
    for pattern in config.get("include", []):
        for filename, d in fileiter(".", regexp=pattern):
            cfg = process_config(filename, **ctx)
            config = merge(cfg, config, mode=mode)

    config = Config(config)
    config.rebuild()
    return config


def build_config(root, pattern, base=None):
    base = {} if base is None else base
    base = Config(base)
    for path, s in fileiter(root, regexp=pattern, info="s"):
        cfg = load_config(path)
        base.mount(cfg)
    return cfg


# --------------------------------------------------
# Config
# --------------------------------------------------
class Config(Dom):
    """A base class for configuration"""

    def assign(self, spec, value):
        # glom.assign(self, spec, value) # do not modify 'inplace'
        holder = self
        keys = re.findall(r"[a-z0-9_-]+", spec)
        for k in keys[:-1]:
            if not k:
                continue
            holder = holder.setdefault(k, dict())
        holder[keys[-1]] = value

    def sg(self, spec, default={}):
        "safe get alike"
        holder = self
        keys = re.findall(r"[a-z0-9_-]+", spec)
        for k in keys:
            if not k:
                continue
            if k in holder:
                holder = holder[k]
            else:
                return default
        return holder

    def sd(self, spec, value, default=None):
        "setdefault alike"
        holder = self
        keys = re.findall(r"[a-z0-9_-]+", spec)
        for k in keys[:-1]:
            if not k:
                continue
            holder = holder.setdefault(k, dict())

        return holder.setdefault(keys[-1], value)

    def merge(self, spec, data, overwrite=False):
        try:
            holder = glom.glom(self, spec)
        except KeyError:
            holder = self
            for k in re.findall(r"[a-z0-9_-]+", spec):
                holder = holder.setdefault(k, dict())

        if overwrite:
            holder.update(data)
        else:
            soft(holder, **data)

    def mount(self, cfg: Dom, path=""):
        cfg = Config(cfg)
        path = path or cfg.pop("_mount_")
        defaults = re.sub(r"(.+)/[^/]+$", r"\1/_default_", path)
        defaults = self.g(defaults)
        soft(cfg, **defaults)

        self.patch("/", path, cfg)
        # return self
        return self.g(path)

    def reload(self):
        for path, info in self.get("include", {}).items():
            mtime = os.access(path, os.F_OK) and os.stat(path).st_mtime
            if mtime > (loaded := info.get("loaded", 0)):
                cfg = load_config(path)
                merge(self, cfg)
                info["loaded"] = time.time()

    def priority(self, root, dep_key="after", exclude=[r"_.*_$"]):
        """Get a ordered list of element keys that have priority dependences among them.

        Consider the following example:

        runlevel:
            device:
                _default_:
                    description: ''
                    documentation: ''
                broadcast:
                    description: the broadcast channel device
                    documentation: Phasellus urna lorem ...
                hearbeat.dev:
                    description: the hearbeat device
                    documentation: Share alive information with peers
            service:
                _default_:
                    description: ''
                    documentation: ''
                bar:
                    description: ''
                    documentation: Nunc in dui condimentum ...
                buzz:
                    after:
                        - bar
                        - foo
                    description: unit mounted by hand
                    documentation: Vivamus congue libero ...
                foo:
                    after: bar
                    description: a wornderful 'foo' unit
                    documentation: Lorem ipsum dolor sit amet ...
                    params:
                        accounts: DU.*
                        client_id: 666
                    uri: tws://localhost:10000
                hearbeat.srv:
                    description: a hearbeat agnt that publish alive info
                    documentation: Cras condimentum consequat quam ...
                    params:
                        details: full
                        freq: 5s
                    uri: hearbeat://localhost
                webui:
                    description: we need a Web console for showing data
                    documentation: Nulla porta sem tincidunt ...
                    params:
                        passwd: '1234'
                        user: agp
                    uri: http://localhost:8080

        >>> result = example.priority('runlevel')
        >>> assert result == [
            "device/broadcast",
            "device/hearbeat",
            "service/bar",
            "service/foo",
            "service/hearbeat",
            "service/webui",
            "service/buzz",
            ]

        This function will:

        - ignores all "_xxxxx_" keys (such as '_default_') by default.
        - resolver order by grouping for 1st sorted keys from root node ('device', 'service')
        - use 2nd key to combie a relative path from root node:
            ['device/broadcast', 'service/hearbeat', ...]
        - same name can be used in multiple sections as section name is used as prefix:
            ['device/hearbeat', 'service/hearbeat', ...]
        - depedencies are got by *dep_key* parameter (used 'after' by default).
        - detect dependencies that can not be satisfied (i.e cycles)

        """
        top = self.g(root)
        result = []
        used = {}

        def inside(after):
            nonlocal result
            for pattern in result:
                if re.match(after, pattern, re.DOTALL):
                    return True
            return False

        for level, data in sitems(top, exclude=exclude):
            remain = deque(sitems(data, exclude=exclude))
            n = len(remain)
            while remain:
                name, info = remain[0]
                name = f"{root}/{level}/{name}"
                deps = info.get(dep_key, [])
                if isinstance(deps, str):
                    deps = [deps]
                for after in deps:
                    if inside(f"{root}/{level}/{after}"):
                        continue
                    remain.rotate(-1)
                    n -= 1
                    if n < 0:
                        raise RuntimeError(f"dependency order can not be satisfied")
                    break
                else:
                    if name in used:
                        raise RuntimeError(
                            f"same key '{name}' is already used in '{used[name]}' and '{level}' sections"
                        )
                    used[name] = level
                    result.append(name)
                    remain.popleft()
                    n = len(remain)
        return result

    def rebuild(self):
        clone = rebuild(walk(self), converters={dict: self.__class__})
        self.update(clone)


register_container(Config)
# ------------------------------------------------------
# Non-Standar Specific formats
# ------------------------------------------------------


def load_config_bash(path):
    """*Parse a UNIX bash style config file.*
    Example:

    #REMOTE="vorange:/media/backup/ vmountain:/mnt/backup/"
    REMOTE="vorange:/media/backup/"
    FOLDERS="/home/agp/Documents/me/"
    SSHKEY=/home/agp/.ssh/id_rsa
    BWLIMIT=100
    PAUSE=3600
    CONSOLE=true

    """
    config = dict()
    reg = re.compile(r'^(?P<key>\w+)\s*="?(?P<value>.*?)"?$')
    reg2 = re.compile(r"([^\s]+)\s*")

    if isinstance(path, str):
        os.path.isfile(path)
        path = expandpath(path)
        if os.path.exists(path):
            file = open(path, "rt")
    elif isinstance(path, io.IOBase):
        file = path
    else:
        raise RuntimeError(f"Can not handle {path} for parsing file")

    for line in file:
        m = reg.match(line)
        if m:
            key, value = m.groups()
            value2 = [x.group() for x in reg2.finditer(value)]
            if len(value2) > 1:
                value = value2
            config[key] = value

    return config
