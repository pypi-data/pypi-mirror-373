from retracesoftware_functional import *
import re
import pdb
import weakref
from types import MappingProxyType

class RegexPredicate:
    __slots__ = ['regex']

    def __init__(self, regex):
        self.regex = re.compile(regex)

    def __hash__(self):
        return hash(self.regex)
    
    def __eq__(self, other):
        if not isinstance(other, RegexPredicate):
            return NotImplemented  # Allows Python to attempt `other.__eq__(self)`
        return self.regex == other.regex
    
    def __str__(self):
        return repr(self.regex.pattern)
    
    def __call__(self, obj):
        return bool(re.fullmatch(self.regex, str(obj)))

def canonical(spec):
    if isinstance(spec, str):
        return ('regex', spec)
    elif isinstance(spec, list):
        return ('or',) + tuple(map(canonical, spec))
    elif 'not' in spec:
        return ('not', canonical(spec['not']))
    elif 'and' in spec:
        return ('and',) + tuple(map(canonical, spec['and']))
    elif 'or' in spec:
        return ('or',) + tuple(map(canonical, spec['or']))
    else:
        pdb.set_trace()
        raise Exception()    

class PredicateBuilder:
    __slots__ = ['cache']

    def __init__(self):
        # self.cache = weakref.WeakKeyDictionary()
        self.cache = {}

    def build(self, spec):
        if spec in self.cache:
            return self.cache[spec]
    
        if spec[0] == 'regex':
            pred = RegexPredicate(spec[1])
        elif spec[0] == 'not':
            pred = not_predicate(self.build(spec[1]))
        elif spec[0] == 'and':
            pred = and_predicate(*map(self.build, spec[1:]))
        elif spec[0] == 'or':
            pred = or_predicate(*map(self.build, spec[1:]))
        else:
            raise Exception("TODO")
        
        self.cache[spec] = pred

        return pred
            
    def __call__(self, spec):
        return self.build(canonical(spec))

class ParamPredicate:
    __slots__ = ['pred', 'index', 'param']

    def __init__(self, signature, param, pred):
        # params = inspect.signature(target).parameters
        self.index = list(signature.keys()).index(param)
        self.param = param
        self.pred = pred

    def __str__(self):
        return f'ParamPredicate(pred = {self.pred}, index = {self.index}, param = {self.param})'
    
    def find_arg(self, *args, **kwargs):
        if self.param in kwargs:
            return kwargs[self.param]
        elif self.index < len(args):
            return args[self.index]
        else:
            raise Exception(f'Cant get arg: {self.param}')

    def __call__(self, *args, **kwargs):
        return self.pred(self.find_arg(*args, **kwargs))
