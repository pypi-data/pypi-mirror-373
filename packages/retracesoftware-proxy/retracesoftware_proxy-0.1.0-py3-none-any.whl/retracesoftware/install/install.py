from __future__ import annotations

import retracesoftware.functional as functional
import retracesoftware_utils as utils

# from retracesoftware_functional import mapargs, walker, first_arg, if_then_else, compose, observer, anyargs, memoize_one_arg, side_effect, partial, threadwatcher, firstof, notinstance_test, instance_test,typeof, isinstanceof, always
# from retracesoftware.proxy.proxy import ProxyFactory, InternalProxy, ProxySpec, WrappingProxySpec, ExtendingProxySpec, ExtendingProxy
from retracesoftware_proxy import thread_id
# from retracesoftware_stream import ObjectWriter, ObjectReader
import retracesoftware.stream as stream

# from retracesoftware_utils import visitor
from retracesoftware.install.tracer import Tracer
from retracesoftware.proxy.record import RecordProxySystem
from retracesoftware.proxy.replay import ReplayProxySystem
from datetime import datetime

import os
import sys
import json
import enum
import _thread
import pickle
import weakref
import types
from pathlib import Path
import glob, os
import re

# from retracesoftware_proxy import *
# from retracesoftware_utils import *
# from retracesoftware.proxy import references
from retracesoftware.install import patcher
from retracesoftware.install.config import load_config
# from retracesoftware.proxy.immutabletypes import ImmutableTypes
# from retracesoftware.proxy import edgecases
from retracesoftware.install import globals
# from retracesoftware.proxy.record import RecordProxyFactory


class DebugWriter:
    __slot__ = ['checkpoint']

    def __init__(self, checkpoint):
        self.checkpoint = checkpoint
 
    def write_call(self, func, *args, **kwargs):
        self.checkpoint({'type': 'call', 'func': ...})

    def write_result(self, res):
        self.checkpoint({'type': 'result', 'result': res})

    def write_error(self, *args):
        self.checkpoint({'type': 'error', 'error': tuple(args)})

class MethodDescriptor:
    def __init__(self, descriptor):
        self.cls = descriptor.__objclass__
        self.name = descriptor.name

def once(*args): return functional.memoize_one_arg(functional.compose(*args))

any = functional.firstof


def compose(*args):
    new_args = [item for item in args if item is not None]
    if len(new_args) == 0:
        raise Exception('TODO')
    elif len(new_args) == 1:
        return new_args[0]
    else:
        return functional.compose(*new_args)

class SerializedWrappedFunction:
    def __init__(self, func):
        if hasattr(func, '__objclass__'):
            self.cls = func.__objclass__
        elif hasattr(func, '__module__'):
            self.module = func.__module__
    
        if hasattr(func, '__name__'):
            self.name = func.__name__


def replaying_proxy_factory(thread_state, is_immutable_type, tracer, next, bind, checkpoint):

    # def on_new_ext_proxytype(proxytype):
    #     assert not issubclass(proxytype, DynamicProxy)
    #     bind(proxytype)
        # writer.add_type_serializer(cls = proxytype, serializer = functional.typeof)

    # bind_new_int_proxy = functional.if_then_else(functional.isinstanceof(InternalProxy), functional.memoize_one_arg(bind), None)
        
    # on_ext_call = utils.visitor(from_arg = 1, function = bind_new_int_proxy)

    def wrap_int_call(handler):
        return functional.observer(
            on_call = tracer('proxy.int.call'),
            on_result = tracer('proxy.int.result'),
            on_error = tracer('proxy.int.error'),
            function = handler)

    def foo(cls):
        print(f"IN FOO {cls}")
        inst = utils.create_stub_object(cls)
        print(f'FOO {cls} {type(inst)}')
        return inst
    
    # def is_stub_type(obj):
    #     return type(obj) == type and issubclass(obj, (WrappingProxy, ExtendingProxy))

    def is_stub_type(obj):
        return type(obj) == type

    create_stubs = functional.walker(functional.when(is_stub_type, foo))
    # create_stubs = functional.walker(functional.when(is_stub_type, utils.create_stub_object))

    def wrap_ext_call(handler):
        return functional.observer(
            on_call = tracer('proxy.ext.call'),
            on_result = tracer('proxy.ext.result'),
            on_error = tracer('proxy.ext.error'),
            function = functional.compose(functional.always(next), create_stubs))

    return ProxyFactory(thread_state = thread_state,
                        is_immutable_type = is_immutable_type,
                        tracer = tracer, 
                        on_new_int_proxy = bind,
                        # on_new_ext_proxytype = on_new_ext_proxytype,
                        wrap_int_call = wrap_int_call,
                        wrap_ext_call = wrap_ext_call)

def latest_from_pattern(pattern: str) -> str | None:
    """
    Given a strftime-style filename pattern (e.g. "recordings/%Y%m%d_%H%M%S_%f"),
    return the path to the most recent matching file, or None if no files exist.
    """
    # Turn strftime placeholders into '*' for globbing
    # (very simple replacement: %... -> *)
    glob_pattern = re.sub(r"%[a-zA-Z]", "*", pattern)

    # Find all matching files
    candidates = glob.glob(glob_pattern)
    if not candidates:
        return None

    # Derive the datetime format from the pattern (basename only)
    base_pattern = os.path.basename(pattern)

    def parse_time(path: str):
        name = os.path.basename(path)
        return datetime.strptime(name, base_pattern)

    # Find the latest by parsed timestamp
    latest = max(candidates, key=parse_time)
    return latest

# class Reader:

#     def __init__(self, objectreader):
#         self.objectreader = objectreader

#     self.objectreader()

def tracing_config(config):
    level = os.environ.get('RETRACE_DEBUG', config['default_tracing_level'])
    return config['tracing_levels'].get(level, {})


def install(create_system):
    return patcher.install(config = load_config('config.json'), create_system = create_system)
