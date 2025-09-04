from retracesoftware.proxy import *

import retracesoftware.functional as functional
import retracesoftware_utils as utils
import retracesoftware.stream as stream
from retracesoftware.install.tracer import Tracer
from retracesoftware.install import globals

import os, json, re, glob, weakref
from pathlib import Path
from datetime import datetime

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



def thread_aware_reader(reader):
    def on_thread_switch():
        ...

    return utils.threadawareproxy(on_thread_switch = on_thread_switch, target = reader)


def replay_system(thread_state, immutable_types, config):

    recording_path = Path(latest_from_pattern(config['recording_path']))

    print(f"replay running against path: {recording_path}")

    globals.recording_path = globals.RecordingPath(recording_path)

    assert recording_path.exists()
    assert recording_path.is_dir()

    with open(recording_path / "env", "r", encoding="utf-8") as f:
        os.environ.update(json.load(f))

    with open(recording_path / "tracing_config.json", "r", encoding="utf-8") as f:
        tracing_config = json.load(f)

    handler = None

    # def create_stub_type(proxyspec):
    #     if isinstance(proxyspec, ExtendingProxySpec):
    #         mod = sys.modules[proxyspec.module]
    #         resolved = getattr(mod, proxyspec.name) 
    #         assert issubclass(resolved, ExtendingProxy)

    #         return resolved
    #         # unproxied = resolved.__base__            
    #         # print(f'base: {unproxied} has_generic_new: {utils.has_generic_new(unproxied)}')
    #         # print(f'base: {unproxied} has_generic_alloc: {utils.has_generic_alloc(unproxied)}')
    #         # utils.create_stub_object(resolved)
    #         # os._exit(1)
    #         # return resolved

    #     elif isinstance(proxyspec, WrappingProxySpec):            
    #         nonlocal handler
    #         return proxyspec.create_type(handler)
    #     else:
    #         print(f'In create_stub_type!!!! {proxyspec}')
    #         os._exit(1)

    # deserializer = functional.compose(pickle.loads, functional.when_instanceof(ProxySpec, create_stub_type))

    reader = thread_aware_reader(stream.reader(path = recording_path / 'trace.bin'))

    # reader = utils.threadawareproxy(on_thread_switch = ..., target = reader)

    def readnext():
        return reader()
        # print(f'read: {obj}')
        # return obj

    lookup = weakref.WeakKeyDictionary()
    
    # debug = debug_level(config)

    # int_refs = {}
        
    def checkpoint(replay):
        ...

    def read_required(required):
        obj = readnext()
        if obj != required:
            print(f'Expected: {required} but got: {obj}')
            for i in range(5):
                readnext()

            utils.sigtrap(None)
            os._exit(1)
            raise Exception(f'Expected: {required} but got: {obj}')

    def trace_writer(name, *args):
        print(f'Trace: {name} {args}')
        
        read_required('TRACE')
        read_required(name)

        for arg in args:
            read_required(arg)

    tracer = Tracer(tracing_config, writer = trace_writer)

    factory = ReplayProxySystem(thread_state = thread_state, 
                                immutable_types = immutable_types,
                                tracer = tracer,
                                reader = reader)
    
    # factory = replaying_proxy_factory(thread_state = thread_state, 
    #                                   is_immutable_type = is_immutable_type,
    #                                   tracer = tracer,
    #                                   bind = reader.supply,
    #                                   next = next_result, 
    #                                   checkpoint = checkpoint)
    
    factory.tracer = tracer

    def read_sync(): read_required('SYNC')

    factory.sync = lambda function: functional.observer(on_call = functional.always(read_sync), function = function)

    # factory.set_thread_number = writer.thread_number

    factory.log = lambda message: checkpoint({'type': 'log_message', 'message': message})

    return factory
