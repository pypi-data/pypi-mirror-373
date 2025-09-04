import retracesoftware.functional as functional
import retracesoftware_utils as utils
                                                                 
from retracesoftware.proxy.proxytype import extending_proxytype, make_extensible

class ProxySystem:
    
    def __init__(self, thread_state):
        self.thread_state = thread_state

    def __call__(self, obj):
        assert not isinstance(obj, BaseException)

        if type(obj) == type and utils.is_extendable(obj):
            return self.extend_type(obj)
        elif callable(obj):
            return utils.wrapped_function(handler = self.ext_handler, target = obj)
        else:
            raise Exception(f'object {obj} was not proxied as its not a extensible type and is not callable')
    
