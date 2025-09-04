import retracesoftware.functional as functional
import retracesoftware_utils as utils

from retracesoftware.proxy.proxytype import dynamic_proxytype, dynamic_int_proxytype, extending_proxytype, make_extensible, dynamic_stubtype, stubtype_from_spec, Stub
from retracesoftware.proxy.gateway import gateway_pair

from retracesoftware.proxy.record import ProxyRef, ProxySpec
from retracesoftware.proxy.proxysystem import ProxySystem

import os

# we can have a dummy method descriptor, its has a __name__ and when called, returns the next element

# for types, we can patch the __new__ method
# do it from C and immutable types can be patched too
# patch the tp_new pointer?

class ReplayProxySystem(ProxySystem):
    
    def stubtype(self, cls):
        return dynamic_proxytype(handler = self.ext_handler, cls = cls)

    def stubtype_from_spec(self, spec):
        print (f'FOOO!!! {spec}')
        return stubtype_from_spec(
            handler = self.ext_handler,
            module = spec.module, 
            name = spec.name,
            methods = spec.methods,
            members = spec.members)

    @utils.striptraceback
    def next_result(self):
        while True:
            next = self.reader()

            if next == 'CALL':
                func = self.reader()
                args = self.reader()
                kwargs = self.reader()

                try:
                    func(*args, **kwargs)
                except:
                    pass

            elif next == 'RESULT':
                return self.reader()
            elif next == 'ERROR':
                err_type = self.reader()
                err_value = self.reader()
                utils.raise_exception(err_type, err_value)
            else:
                assert not isinstance(next, str)
                return next

    def __init__(self, thread_state, immutable_types, tracer, reader):
        # self.writer = writer
        super().__init__(thread_state = thread_state)
        self.immutable_types = immutable_types
        self.reader = reader
        self.bind = self.reader.supply

        add_stubtype = functional.side_effect(immutable_types.add)

        reader.type_deserializer[ProxyRef] = functional.sequence(lambda ref: ref.resolve(), self.stubtype, add_stubtype)
        reader.type_deserializer[ProxySpec] = functional.sequence(self.stubtype_from_spec, add_stubtype)

        # on_ext_result = functional.if_then_else(
        #     functional.is_instanceof(str), writer.handle('RESULT'), writer)

        def int_proxytype(gateway):
            return lambda cls: dynamic_int_proxytype(handler = gateway, cls = cls, bind = self.bind)

        def is_stub_type(obj):
            return functional.typeof(obj) is type and issubclass(obj, Stub)

        create_stubs = functional.walker(functional.when(is_stub_type, lambda cls: cls()))

        ext_apply = functional.repeatedly(functional.sequence(self.next_result, create_stubs))
                
        self.ext_handler, self.int_handler = gateway_pair(
            thread_state,
            tracer,
            immutable_types = immutable_types,
            ext_apply = ext_apply,
            int_proxytype = int_proxytype,
            ext_proxytype = functional.identity)

    def extend_type(self, base):
        
        # ok, how to provide __getattr__ style access, 

        extended = extending_proxytype(
            cls = base,
            thread_state = self.thread_state, 
            int_handler = self.int_handler,
            ext_handler = self.ext_handler,
            on_subclass_new = self.bind,
            is_stub = True)

        self.immutable_types.add(extended)
        # proxytype = extending_proxytype(base)

        # make_extensible(cls = extended, 
        #                 int_handler = self.int_handler, 
        #                 ext_handler = self.ext_handler,
        #                 on_new = self.reader.supply)

        return extended
