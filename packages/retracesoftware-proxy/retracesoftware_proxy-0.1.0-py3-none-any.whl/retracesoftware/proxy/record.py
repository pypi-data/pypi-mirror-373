import retracesoftware.functional as functional
import retracesoftware_utils as utils

from retracesoftware.proxy.proxytype import dynamic_proxytype, superdict, is_descriptor, extending_proxytype, dynamic_int_proxytype, make_extensible
from retracesoftware.proxy.gateway import gateway_pair
from retracesoftware.proxy.proxysystem import ProxySystem

import sys

class ExtendedProxy:
    __slots__ = []

class ProxyRef:
    def __init__(self, module, name):
        self.module = module
        self.name = name

    def resolve(self):
        return getattr(sys.modules[self.module], self.name)

class ProxySpec(ProxyRef):
    def __init__(self, module, name, methods, members):
        super().__init__(module, name)
        self.methods = methods
        self.members = members

    def __str__(self):
        return f'ProxySpec(module = {self.module}, name = {self.name}, methods = {self.methods}, members = {self.members})'
    
def keys_where_value(pred, dict):
    for key,value in dict.items():
        if pred(value): yield key

def resolveable(obj):
    try:
        return getattr(sys.modules[obj.__module__], obj.__name__) is obj
    except:
        return False
    
class ExtProxytype:

    def __init__(self, gateway, extended_types, writer):
        self.gateway = gateway
        self.writer = writer
        self.extended_types = extended_types

    def __call__(self, cls):
        assert isinstance(cls, type)

        if cls in self.extended_types:
            return functional.side_effect(lambda obj: utils.set_type(obj, self.extended_types[cls]))
        else:
            if resolveable(cls):
                ref = self.writer.handle(ProxyRef(name = cls.__name__, module = cls.__module__))
            else:
                blacklist = ['__getattribute__']
                descriptors = {k: v for k,v in superdict(cls).items() if k not in blacklist and is_descriptor(v) }

                methods = [k for k, v in descriptors.items() if utils.is_method_descriptor(v)]
                members = [k for k, v in descriptors.items() if not utils.is_method_descriptor(v)]

                ref = self.writer.handle(ProxySpec(name = cls.__name__, 
                                                module = cls.__module__,
                                                methods = methods,
                                                members = members))
            
            proxytype = dynamic_proxytype(handler = self.gateway, cls = cls)

            self.writer.type_serializer[proxytype] = functional.constantly(ref)
            return proxytype
        

# when 
class RecordProxySystem(ProxySystem):
    
    def __init__(self, thread_state, immutable_types, tracer, writer):
        super().__init__(thread_state = thread_state)

        self.immutable_types = immutable_types

        self.extended_types = {}
        self.writer = writer
        self.bind = writer.placeholder

        # on_ext_result = writer.handle('RESULT')
        on_ext_result = functional.if_then_else(
            functional.isinstanceof(str), writer.handle('RESULT'), writer)

        def int_proxytype(gateway):
            return lambda cls: dynamic_int_proxytype(handler = gateway, cls = cls, bind = self.bind)
        
        def ext_proxytype(gateway):
            return ExtProxytype(gateway = gateway, writer = writer, extended_types = self.extended_types)
    
        error = writer.handle('ERROR')

        def write_error(cls, val, traceback):
            error(cls, val)

        self.ext_handler, self.int_handler = gateway_pair(
            thread_state,
            tracer,
            immutable_types = immutable_types,
            int_proxytype = int_proxytype,
            ext_proxytype = ext_proxytype,
            on_int_call = writer.handle('CALL'),
            on_ext_result = functional.side_effect(on_ext_result),
            on_ext_error = write_error)

    def extend_type(self, base):

        if base in self.extended_types:
            return self.extended_types[base]

        # self.tracer.log('proxy.ext.new.extended', f'{base.__module__}.{base.__name__}')

        extended = extending_proxytype(
            cls = base,
            thread_state = self.thread_state, 
            ext_handler = self.ext_handler,
            int_handler = self.int_handler,
            on_subclass_new = self.bind,
            is_stub = False)
        
        ref = self.writer.handle(ProxyRef(name = base.__name__, module = base.__module__,))
        self.writer.type_serializer[extended] = functional.constantly(ref)
        
        # make_extensible(cls = extended, handler = self.int_handler, on_new = self.writer.placeholder)

        self.immutable_types.add(extended)
        self.extended_types[base] = extended 

        return extended
