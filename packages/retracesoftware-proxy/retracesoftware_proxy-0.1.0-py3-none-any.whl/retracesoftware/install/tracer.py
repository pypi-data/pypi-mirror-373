import retracesoftware.functional as functional
import retracesoftware_utils as utils
from retracesoftware.proxy.proxytype import Proxy

import types
import os

def format_kwargs(kwargs):
    result = []
    for k, v in kwargs.items():
        result.extend([f"{k} = ", v])

    return tuple(result)

class Tracer:
    def __init__(self, config, writer):
        self.config = config
        serialize = functional.walker(self.serialize)
        self.writer = functional.mapargs(transform = serialize, function = writer)

    def serialize(self, obj):
        try:
            if obj is None: return None

            cls = functional.typeof(obj)

            if issubclass(cls, (int, str)):
                return obj

            else:
                return 'FOO!!!!'
            
            if issubclass(cls, Proxy):
                return f'<Proxy>'

            if issubclass(cls, types.TracebackType):
                return '<traceback>'
            
            elif issubclass(cls, utils.wrapped_function):
                return utils.unwrap(obj).__name__
            
            elif hasattr(obj, '__module__') and hasattr(obj, '__name__'):
                return f'{obj.__module__}.{obj.__name__}'
            # elif isinstance(obj, type):
            #     return f'{obj.__module__}.{obj.__name__}'
            else:
                return '<other>'
                # return f'instance type: {str(self.serialize(type(obj)))}'
        except:
            print("ERROR in tracer serialize!!!!")
            os._exit(1)

    def log(self, name, message):
        if name in self.config:
            self.writer(name, message)
         
    def __call__(self, name, func = None):
        if name in self.config:
            if name.endswith('.call'):
                def write_call(*args, **kwargs):
                    self.writer(name, args[0].__name__, args[1:], kwargs)
            
                return functional.firstof(write_call, func) if func else write_call
            
            elif name.endswith('.result'):
                def write_result(obj):
                    self.writer(name, obj)
                    return obj
                
                return functional.sequence(func, write_result) if func else write_result
            
            elif name.endswith('.error'):
                def write_error(*args):
                    self.writer(name, args)
            
                return functional.firstof(write_error, func) if func else write_error

            elif name.endswith('.event'):
                def write_event(*args, **kwargs):
                    self.writer(name)

                return functional.firstof(write_event, func) if func else write_event
        
            elif name.endswith('.wrap'):
                def wrapper(*args, **kwargs):
                    self.writer(name, 'enter')
                    try:
                        return func(*args, **kwargs)
                    finally:
                        self.writer(name, 'exit')

                return wrapper
            
            elif name.endswith('.stack'):
                def write_event(*args, **kwargs):
                    self.writer(name, utils.stacktrace())

                return functional.firstof(write_event, func) if func else write_event


        return func


    def write(self, name):
        if name in self.config:
            return functional.partial(self.writer, name)

    def write_call(self, name, func = None):

        def writer(*args, **kwargs):
            self.writer(name, *(args + format_kwargs(kwargs)))

        if name in self.config:
            return functional.firstof(writer, func) if func else writer
        else:
            return func

    def write_result(self, name, func):
        
        writer = functional.partial(self.writer, name)
            
        if name in self.config:
            return functional.compose(func, functional.side_effect(writer))
        else:
            return func

    def event(self, name):
        return functional.always(lambda: self.writer(name))

    def event_before(self, name, func = None):
        if name in self.config:
            # def foo(*args, **kwargs):
            #     print("GRRRRR!!!!!")

            # return functional.firstof(foo, func)
            return functional.firstof(self.event(name), func)
        else:
            return func

    def event_after(self, name, func):
        if name in self.config:
            return functional.compose(func, functional.side_effect(self.event(name)))
        else:
            return func
