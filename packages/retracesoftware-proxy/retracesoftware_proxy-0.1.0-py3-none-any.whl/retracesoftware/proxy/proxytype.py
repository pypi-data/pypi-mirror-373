import retracesoftware_utils as utils
import retracesoftware.functional as functional

import types

class Proxy:
    __slots__ = []

class Stub(Proxy):
    __slots__ = []

class DynamicProxy(Proxy):
    __slots__ = []

class ExtendingProxy(Proxy):
    __slots__ = []

class InternalProxy:
    __slots__ = []

def superdict(cls):
    result = {}
    for cls in list(reversed(cls.__mro__))[1:]:
        result.update(cls.__dict__)
    
    return result

def is_method_descriptor(obj):
    return isinstance(obj, types.FunctionType) or \
           (isinstance(obj, (types.WrapperDescriptorType, types.MethodDescriptorType)) and obj.__objclass__ != object)

def proxy_method_descriptors(cls, handler):
    for name, target in cls.__dict__.items():
        if is_method_descriptor(target):
            proxied = utils.wrapped_function(handler = handler, target = target)
            setattr(cls, name, proxied)

def methods(cls):
    for name,value in superdict(cls).items():
        if is_descriptor(value) and is_method_descriptor(value):
            yield name

def is_descriptor(obj):
    return hasattr(obj, '__get__') or hasattr(obj, '__set__') or hasattr(obj, '__delete__')

class Named:
    def __init__(self, name):
        self.__name__ = name

class DescriptorStub:

    __slots__ = ['handler', 'name']

    def __init__(self, handler, name):
        self.handler = handler
        self.name = name

    def __get__(self, instance, owner):
        return self.handler(Named('getattr'), self.name)

    def __set__(self, instance, value):
        return self.handler(Named('setattr'), self.name, value)

    def __delete__(self, instance):
        return self.handler(Named('delattr'), self.name)
    
def stubtype_from_spec(handler, module, name, methods, members):

    spec = {
        '__module__': module,        
    }

    for method in methods:
        spec[method] = utils.wrapped_function(
            handler = handler, target = Named(method))

    for member in members:
        spec[member] = DescriptorStub(handler = handler, name = member)

    return type(name, (Stub, DynamicProxy,), spec)

    # stubtype.__new__ = thread_state.dispatch(disabled__new__, internal = stub.__new__, external = stub.__new__)
    # stub.__retrace_unproxied__ = cls

def dynamic_stubtype(handler, cls):

    assert not issubclass(cls, BaseException)

    blacklist = ['__getattribute__', '__hash__', '__del__', '__init__', '__call__']

    to_proxy = [m for m in methods(cls) if m not in blacklist]

    def wrap(name): return utils.wrapped_function(handler = handler, 
                                                  target = Named(name))
    
    spec = { name: wrap(name) for name in to_proxy }

    spec['__getattr__'] = wrap('__getattr__')
    spec['__setattr__'] = wrap('__setattr__')
    
    if utils.yields_callable_instances(cls):
        spec['__call__'] = handler

    spec['__retrace_target_class__'] = cls
    spec['__class__'] = property(functional.repeatedly(cls))

    name = f'retrace.proxied.{cls.__module__}.{cls.__name__}'

    return type(name, (Stub, DynamicProxy), spec)

def dynamic_proxytype(handler, cls):

    assert not issubclass(cls, BaseException)

    blacklist = ['__getattribute__', '__hash__', '__del__', '__init__', '__call__']

    to_proxy = [m for m in methods(cls) if m not in blacklist]

    def wrap(target): return utils.wrapped_function(handler = handler, target = target)
    
    spec = { name: wrap(getattr(cls, name)) for name in to_proxy }

    spec['__getattr__'] = wrap(getattr)
    spec['__setattr__'] = wrap(setattr)
    
    if utils.yields_callable_instances(cls):
        spec['__call__'] = handler

    spec['__retrace_target_class__'] = cls

    target_type = functional.compose(utils.unwrap, functional.typeof)
    spec['__class__'] = property(target_type)

    name = f'retrace.proxied.{cls.__module__}.{cls.__name__}'

    return type(name, (utils.Wrapped, DynamicProxy), spec)

def dynamic_int_proxytype(handler, cls, bind):
    proxytype = dynamic_proxytype(handler = handler, cls = cls)
    proxytype.__new__ = functional.sequence(proxytype.__new__, functional.side_effect(bind))
    return proxytype
                                    
class DescriptorProxy:

    __slots__ = ['handler', 'proxytype', 'name']

    def __init__(self, proxytype, handler, name):
        self.proxytype = proxytype
        self.handler = handler
        self.name = name

    def __get__(self, instance, owner):
        inst = owner if instance is None else instance
        getter = functional.partial(getattr, super(self.proxytype, inst))
        return self.handler(getter, self.name)

    def __set__(self, instance, value):
        setter = functional.partial(setattr, super(self.proxytype, instance))
        return self.handler(setter, self.name, value)

    def __delete__(self, instance):
        deleter = functional.partial(delattr, super(self.proxytype, instance))
        return self.handler(deleter, self.name)


blacklist = ['__getattribute__', '__hash__', '__del__']

# if the type can be patched, thats better, all new instances must be of correct type

def extending_proxytype(cls, thread_state, ext_handler, int_handler, on_subclass_new, is_stub = False):

    assert not issubclass(cls, BaseException)

    def init_subclass(subclass, **kwargs):
        print(f'In init_subclass: {subclass} {kwargs}')
        # subclass.__retrace_unproxied__ = create_unproxied_type(subclass)

        proxy_method_descriptors(cls = subclass, handler = int_handler)

        if not issubclass(subclass, InternalProxy):
            subclass.__new__ = functional.compose(subclass.__new__, functional.side_effect(on_subclass_new))
            subclass.__bases__ = subclass.__bases__ + (InternalProxy,)

    slots = { "__slots__": (), "__init_subclass__": init_subclass }

    def wrap(target): return utils.wrapped_function(handler = ext_handler, target = target)

    descriptors = []

    for name,value in superdict(cls).items():
        if name not in blacklist:
            if is_method_descriptor(value):
                slots[name] = wrap(getattr(cls, name))
            elif is_descriptor(value):
                descriptors.append(name)

    name = f'retrace.extended.{cls.__module__}.{cls.__name__}'

    extended = type(name, (cls, ExtendingProxy), slots)

    for name in descriptors:
        proxy = DescriptorProxy(handler = ext_handler, name = name, proxytype = extended)
        setattr(extended, name, proxy)

    # def disabled__new__(subcls, *args, **kwargs):
    #     print('IN Diabled new!!!')
        
    #     instance = cls.__new__(subcls.__retrace_unproxied__, *args, **kwargs)
    #     instance.__init__(*args, **kwargs)
    #     return instance

    # __new__ = functional.compose(cls.__new__, functional.side_effect(on_new))
    if is_stub:
        def __new__(cls, *args, **kwargs):
            instance = utils.create_stub_object(cls)
            # print(instance is None)
            # utils.sigtrap(None)
            return instance
        
        extended.__new__ = thread_state.dispatch(cls.__new__, internal = __new__, external = __new__)
    
    # extended.__retrace_unproxied__ = cls

    return extended


def stubtype(cls, result, thread_state, handler):
    
    name = f'retrace.stub.{cls.__module__}.{cls.__name__}'

    slots = {}

    def wrap(name):
        return utils.wrapped_function(
            handler = handler, 
            target = StubMethodDescriptor(name = name, result = result))

    for name,value in superdict(cls).items():
        if name not in blacklist:
            if is_method_descriptor(value):
                slots[name] = wrap(name)
            elif is_descriptor(value):
                slots[name] = DescriptorStub(handler = handler, name = name)

    def disabled__new__(subcls, *args, **kwargs):
        instance = cls.__new__(subcls.__retrace_unproxied__, *args, **kwargs)
        instance.__init__(*args, **kwargs)
        return instance

    stub = type(name, (Stub,), slots)

    stub.__new__ = thread_state.dispatch(disabled__new__, internal = stub.__new__, external = stub.__new__)

    stub.__retrace_unproxied__ = cls

    return stub

def create_unproxied_type(cls):
    name = f'{cls.__module__}.{cls.__name__}'

    def unproxy_type(cls):
        return cls.__retrace_unproxied__ if issubclass(cls, ExtendingProxy) else cls

    return type(name, tuple(map(unproxy_type, cls.__bases__)), dict(cls.__dict__))

def make_extensible(cls, handler, on_new):

    cls.__retrace_unproxied__ = cls.__base__

    def init_subclass(*args, **kwargs):
        print(f'In init_subclass: {args} {kwargs}')
        # subclass.__retrace_unproxied__ = create_unproxied_type(subclass)

        # proxy_method_descriptors(cls = subclass, handler = handler)

        # if not issubclass(subclass, InternalProxy):
        #     cls.__new__ = functional.compose(cls.__new__, functional.side_effect(on_new))
        #     cls.__bases__ = cls.__bases__ + (InternalProxy,)

    cls.__init_subclass__ = init_subclass
