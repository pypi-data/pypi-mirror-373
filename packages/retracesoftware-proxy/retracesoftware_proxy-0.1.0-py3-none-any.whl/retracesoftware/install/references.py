import gc
import sys
import pdb

def references(obj):
    refcnt = sys.getrefcount(obj) - 2
    
    if refcnt == 1:
        moddict = sys.modules[obj.__module__].__dict__

        if obj.__name__ in moddict and moddict[obj.__name__] is obj:
            return [moddict]
    else:
        refs = []

        for mod in list(sys.modules.values()):
            moddict = mod.__dict__
            if obj.__name__ in moddict and moddict[obj.__name__] is obj:
                refs.append(moddict)

        if len(refs) == refcnt:
            return refs

    return gc.get_referrers(obj)
    
def replace(container, old, new):
    if isinstance(container, dict):
        if old in container:
            elem = container.pop(old)
            container[new] = elem
            replace(container, old, new)
        else:
            for key,value in container.items():
                if value is old:
                    container[key] = new
                    
    elif isinstance(container, list):
        for i,value in enumerate(container):
            if value is old:
                container[i] = new

    elif isinstance(container, set):
        container.remove(old)
        container.add(new)

    # elif isinstance(container, tuple):
    #     pdb.set_trace()
    # else:
    #     pdb.set_trace()
    #     raise Exception('TODO')

def update(f, obj):
    new = f(obj)
    if new is not obj:
        refs = references(obj)
        for ref in refs:
            replace(ref, obj, new)

    return new

# import math
# import os
# print(references(math.sqrt))
# print(references(os.nice))
# print(references(os.open))
