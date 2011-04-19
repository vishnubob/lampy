import math
from UserString import MutableString 

class String(MutableString):
    def __init__(self, *args):
        value = str.join('', map(str, args))
        super(String, self).__init__(value)
            
    def __cmp__(self, other):
        if type(other) in (int, float):
            raise TypeError
        return cmp(str(self.lower()), str(other.lower()))

    def __add__(self, other):
        return String(str(self) + other)

class Int(int):
    _Type = int

    def __neg__(self):
        return self.__class__(- self._Type(self))
    def __div__(self, other):
        return self.__class__(div(self, other))
    def __mod__(self, other):
        return self.__class__(mod(self, other))
    def __eq__(self, other):
        if type(other) not in (self.__class__, self._Type):
            return False
        return self._Type(self) == self._Type(other)
    def __ne__(self, other):
        return not self.__eq__(other)
    def __cmp__(self, other):
        if type(other) not in (self.__class__, self._Type):
            raise TypeError
        return cmp(self._Type(self), self._Type(other))

class Float(float):
    _Type = float

    def __neg__(self):
        return self.__class__(- self._Type(self))
    def __div__(self, other):
        return self.__class__(div(self, other))
    def __mod__(self, other):
        return self.__class__(mod(self, other))
    def __eq__(self, other):
        if type(other) not in (self.__class__, self._Type):
            return False
        return self._Type(self) == self._Type(other)
    def __ne__(self, other):
        return not self.__eq__(other)
    def __cmp__(self, other):
        if type(other) not in (self.__class__, self._Type):
            raise TypeError
        return cmp(self._Type(self), self._Type(other))

class Object(object):
    def __init__(self, obj):
        self.obj = int(obj)
    def __cmp__(self, other):
        if type(other) not in (Object,):
            raise TypeError
        return cmp(self.obj, other.obj)

def div(x, y):
    int_flag = False
    if type(x) == int and type(y) == int:
        int_flag = True
    res = float(x) / float(y)
    if int_flag:
        res = int(res)
    return res

def mod(x, y):
    int_flag = False
    if type(x) == int and type(y) == int:
        int_flag = True
    res = math.fmod(x, y)
    if int_flag:
        res = int(res)
    return res

def equality(x, y):
    if type(x) != type(y):
        return False
    if type(x) in (str, Mstr):
        # case insenitive
        return x.lower() == y.lower()
    elif type(x) in (list, tuple):
        if len(x) != len(y):
            return False
        for xE, yE in zip(x, y):
            if not equality(xE, yE):
                return False
        return True
    else:
        return x == y

def inequality(x, y):
    return not equality(x, y)

def index(haystack, needle, cs=False):
    needle = str(needle)
    haystack = str(haystack)
    if not cs:
        needle = needle.lower()
        haystack = haystack.lower()
    if needle in haystack:
        return haystack.index(needle) + 1
    return 0
    
