"""Helpers for dealing calls, parameters adaptations, etc.

Smart calls
-----------------

- [x] *scall*: pass only matching arguments before call function.

Strategy Calls
-----------------

- [x]: search for data/functions in the stack that can supply arguments calls.
- [x] *strategy*: cache where there parameters are located for future calls.

"""

import sys
import types
import asyncio
import traceback
import inspect

from .metrics import likelyhood4
from .containers import update_context
from .colors import *

# ----------------------------------------------------------------------
# introspective and async calls
# ----------------------------------------------------------------------


def scall(func, *args, **kw):
    """Smart-Call that prepares arguments before calling the function."""
    if func is None:
        return

    # 1. try to execute directly
    if len(args) == 1:
        if isinstance(args[0], dict):
            args[0].update(kw)
            args, kw = [], args[0]
        elif isinstance(args[0], (list, tuple)):
            args = args[0]

    try:
        args2, kw2 = prepare_call(func, *args, **kw)
        return func(*args2, **kw2)
    except Exception as why:  # TODO: which is the right exception here? (missing args)
        #  TypeError
        traceback.print_exc()

        print(f"{YELLOW}ERROR: scall({func}) -> {BLUE}{why}{RED}")
        traceback.print_exc(file=sys.stdout)
        # exc_info = sys.exc_info()
        # tb = exc_info[-1]
        # tb.tb_next
        # frame = tb.tb_next.tb_frame

        # print(traceback.print_exception(*exc_info))
        print(f"{RESET}")
        # del exc_info
        foo = 1

    # 2. try to find calling arguments from passed dict as env
    # TODO: include default **converters as well?

    strategy = strategy_call(func, kw)
    kw2 = execute_strategy(strategy, kw)
    try:
        return func(**kw2)
    except Exception as why:  # TODO: which is the right exception here? (missing args)
        pass


def async_call(func, *args, **kw):
    "asyncio adapter for scall."
    main = scall(func, *args, **kw)
    assert asyncio.iscoroutine(main)
    asyncio.run(main)


def prepare_call(func, *args, **kw):
    """Collect available variables from stack in order to
    create a context for calling the function.
    """
    #
    __max_frames_back__ = kw.pop("__max_frames_back__", 1)
    frame = sys._getframe(1)
    frameN = sys._getframe(__max_frames_back__)
    _locals = list()
    while __max_frames_back__ > 0 and frame:
        _locals.append(frame.f_locals)
        __max_frames_back__ -= 1
        frame = frame.f_back
    _locals.reverse()

    # build a parameter database kw0 from
    # data gathered from stack
    kw0 = dict()
    for st in _locals:
        for item in st.values():
            update_context(kw0, item)
        update_context(kw0, st)
    kw0.update(kw)

    # try to match function calling args
    info = inspect.getfullargspec(func)
    if info.varkw:
        kw2 = kw0
    else:
        kw2 = dict()

    args = list(args)
    callargs = list(info.args)
    defaults = list(info.defaults or [])

    # remove self for MethodType, and __init__
    if (
        isinstance(func, types.MethodType)
        or func.__name__ in ("__init__",)
        or func.__class__.__name__ in ("type",)
    ):  # klass.__call__
        if callargs[0] == "self":  # is a convenience criteria
            callargs.pop(0)
            kw0.pop("self", None)

    # simple solution for adjusting default values
    while len(defaults) < len(callargs):
        defaults.insert(0, None)

    # allocate passed args into final output dict
    while args:
        attr = callargs.pop(0)
        value = args.pop(0)
        dvalue = defaults.pop(0)
        kw2[attr] = value

    # allocate unmatched defaul values (if possible)
    while callargs:
        attr = callargs.pop(0)
        dvalue = defaults.pop(0)
        kw2[attr] = dvalue

    # while callargs:
    # attr = callargs.pop(0)
    # value = defaults.pop(0)
    # if attr in kw0:
    # value = kw0.pop(attr)
    # if args:
    # if id(value) == id(args[0]):
    # args.pop(0)
    # elif args:
    # value = args.pop(0)
    # kw2[attr] = value

    if not info.varargs:
        if len(args) > 0:
            raise RuntimeError(
                "too many positional args ({}) for calling {}(...)".format(
                    args, func.__name__
                )
            )

    # if isinstance(func, types.MethodType):
    # bound = info.args[0]
    # assert bound == 'self'   # is a convenience criteria
    # kw2.pop(bound)
    return [], kw2


# ----------------------------------------------------------------------
# gather params from stack and save informaion as a
# strategy for future calls
# ----------------------------------------------------------------------


def strategy_call(func, env, **converters):
    """Try to find matching calling arguments making a
    deep search in `**kw` arguments."""
    func_info = inspect.getfullargspec(func)
    callargs = list(func_info.args)
    defaults = list(func_info.defaults or [])
    annotations = func_info.annotations or {}
    strategy = dict()
    while callargs:
        attr = callargs.pop(0)
        klass = annotations.get(attr)
        # find a object that match attr
        best_name, best_score = None, 0
        for name, value in env.items():
            if name in strategy:
                continue
            # d1 = likelyhood(attr, name)
            # d2 = likelyhood2(attr, name)
            # print("<{}, {}> : {} {}".format(attr, name, d1, d2))
            score = (likelyhood4(attr, name) + (klass in (None, value.__class__))) / 2
            if 0.50 <= score > best_score:
                best_name, best_score = name, score
        if best_name:
            strategy[attr] = ("env", best_name)
            continue
        # otherwise we need to use converters
        # try to find the best converter possible
        # same or similar names, same return values is provided by signature
        best_name, best_score = None, 0
        for name, conv in converters.items():
            conv_info = inspect.getfullargspec(conv)
            ret = conv_info.annotations.get("return")
            if ret in (None, klass):
                score = likelyhood(attr, name)
                if score > best_score:
                    best_name, best_score = name, score
        if best_name:
            strategy[attr] = ("conv", best_name)

    if isinstance(func, types.MethodType):
        bound = func_info.args[0]
        assert bound == "self"  # is a convenience criteria
        strategy.pop(bound, None)

    # self._make_request_cache[request] = strategy
    return strategy


def execute_strategy(strategy, env, **converters):
    """Execute a precomputed strategy for getting the
    arguments faster next times."""
    kw2 = dict()
    for attr, (where, best) in strategy.items():
        if where in ("env"):
            value = env.get(best)
        elif where in ("conv"):
            conv = converters[best]
            args, kw = prepare_call(conv, **env)
            value = conv(*args, **kw)
        kw2[attr] = value
    return kw2


# ----------------------------------------------------------------------
# Helper: used only by Xingleton by now
# ----------------------------------------------------------------------


def prepare_call_args(func, *args, **kw):
    """Get all arguments needed for a call.
    Used by Xingleton."""

    args2, kw2 = prepare_call(func, *args, **kw)
    kw2.pop("self", None)
    info = inspect.getfullargspec(func)
    args2.extend([k for k in info.args if k in kw2])
    return tuple([kw2[k] for k in args2])


# ----------------------------------------------------------------------
# Helper: used only by Xingleton by now
# ----------------------------------------------------------------------


class IntrospCaller(object):
    """base class for instrospective calls and async calls.

    Requires a context where locate:
    - 'converters' dict for mapping arguments call with calleables or data
    - 'call_keys' set to extract the key used to store deferred calls

    Example:

    # context for automatic IntrospCaller
    converters = self.context.setdefault('converters', {})
    converters['reqId'] = self._next_rid
    converters['contract'] = self._get_contract

    self.context.setdefault('call_keys', set()).update(['reqId', ])

    for symbol in ('NQ', 'ES', 'DAX'):
            self.make_call(self.protocol.client.reqContractDetails)

    It will make 3 calls that will use 'reqId' parameter as key

    In order to drop the cache when request is done user must explicit invoke

        self._drop_call(kw)

    where kw contains the same parameter that has been used to make the call

    """

    def __init__(self, context=None):
        self.context = context if context is not None else dict()
        self._make_request_cache = dict()
        self._calls = dict()

    def make_call(self, func, **ctx):
        frame = inspect.currentframe().f_back
        env = dict(frame.f_locals)
        context = {}
        while frame and not context:
            # converters = frame.f_locals.get('kw', {}).get('__context__', {}).get('converters', {})
            for name in (
                "context",
                "ctx",
            ):
                context = frame.f_locals.get(name, {})
                if context:
                    break
            frame = frame.f_back
        converters = context.get("converters", {})

        # execute cached strategy
        strategy = self._get_strategy(func, env, converters)
        kw = execute_strategy(strategy, env, **converters)
        keys = self._set_call(func, kw)
        return func(**kw), keys

    def _get_strategy(self, func, env, converters):
        strategy = self._make_request_cache.get(func)
        if strategy is not None:
            return strategy

        strategy = strategy_call(func, env, **converters)
        self._make_request_cache[func] = strategy
        return strategy

    def _set_call(self, func, kw):
        # store call parameters for later use
        for key in self.context["call_keys"].intersection(kw):
            value = kw[key]
            self._calls[value] = func, value, kw

            # just 1 iteration, maybe more than one for advanced uses
            return func, value, kw

    def _drop_call(self, kw):
        result = []
        for key in self.context["call_keys"].intersection(kw):
            result.append(self._calls.pop(kw[key], None))
        return result
