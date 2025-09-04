import retracesoftware.functional as functional
import retracesoftware_utils as utils

# from retracesoftware.proxy.proxytype import ExtendingProxy

unproxy_execute = functional.mapargs(starting = 1, 
                                     transform = functional.walker(utils.try_unwrap), 
                                     function = functional.apply)

def adapter(proxy_input,
            proxy_output,
            function,
            on_call = None,
            on_result = None,
            on_error = None):

    # function = functional.apply

    if on_call: function = functional.observer(on_call = on_call, function = function)

    function = functional.mapargs(starting = 1, transform = proxy_input, function = function)

    function = functional.compose(function, proxy_output)

    if on_result or on_error:
        function = functional.observer(on_result = on_result, on_error = on_error, function = function)

    return function

def adapter_pair(proxy_int, 
                 proxy_ext,
                 int_apply,
                 ext_apply,
                 tracer, 
                 on_int_call,
                 on_ext_result,
                 on_ext_error):
    return (
        adapter(
            function = ext_apply,
            proxy_input = proxy_int,
            proxy_output = proxy_ext,
            on_call = tracer('proxy.ext.call'),
            on_result = on_ext_result,
            on_error = on_ext_error),
            # on_result = tracer('proxy.ext.result', on_ext_result),
            # on_error = tracer('proxy.ext.error', on_ext_error)),
        adapter(
            function = int_apply,
            proxy_input = proxy_ext,
            proxy_output = proxy_int,
            on_call = tracer('proxy.int.call', on_int_call),
            on_result = tracer('proxy.int.result'),
            on_error = tracer('proxy.int.error')))
    
def proxy(proxytype):
    return functional.selfapply(functional.compose(functional.typeof, proxytype))

def maybe_proxy(proxytype):
    return functional.if_then_else(
            functional.isinstanceof(utils.Wrapped),
            utils.unwrap,
            proxy(functional.memoize_one_arg(proxytype)))

def gateway_pair(thread_state,
                 tracer,
                 immutable_types,
                 int_proxytype,
                 ext_proxytype,
                 int_apply = functional.apply,
                 ext_apply = functional.apply,
                 on_int_call = None,
                 on_ext_result = None,
                 on_ext_error = None):

    def is_immutable_type(cls):
        return issubclass(cls, tuple(immutable_types))

    is_immutable = functional.sequence(functional.typeof, functional.memoize_one_arg(is_immutable_type))

    def create_proxier(proxytype):
        return functional.walker(functional.when_not(is_immutable, maybe_proxy(proxytype)))
    
    int_to_ext_dispatch = thread_state.dispatch(tracer('proxy.int.disabled.event', unproxy_execute))
    ext_to_int_dispatch = thread_state.dispatch(tracer('proxy.ext.disabled.event', unproxy_execute))

    int_to_ext, ext_to_int = adapter_pair(
        proxy_int = create_proxier(int_proxytype(ext_to_int_dispatch)),
        proxy_ext = create_proxier(ext_proxytype(int_to_ext_dispatch)),
        int_apply = thread_state.wrap(desired_state = 'internal', function = int_apply),
        ext_apply = thread_state.wrap(desired_state = 'external', function = ext_apply),
        tracer = tracer,
        on_int_call = on_int_call,
        on_ext_result = on_ext_result,
        on_ext_error = on_ext_error)

    thread_state.set_dispatch(int_to_ext_dispatch, external = functional.apply, internal = tracer('proxy.int_to_ext.stack', int_to_ext))
    thread_state.set_dispatch(ext_to_int_dispatch, internal = functional.apply, external = tracer('proxy.ext_to_int.wrap', ext_to_int))
    
    return (int_to_ext_dispatch, ext_to_int_dispatch)
