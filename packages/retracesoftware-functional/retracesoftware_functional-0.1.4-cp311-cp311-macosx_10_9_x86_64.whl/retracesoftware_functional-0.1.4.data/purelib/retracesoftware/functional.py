import retracesoftware_functional as _functional
from retracesoftware_functional import *

def when_not(test, then):
    return _functional.if_then_else(test, None, then)

def when(test, then):
    return _functional.if_then_else(test, then, None)

def when_instanceof(cls, then):
    return when(_functional.isinstanceof(cls), then)

repeatedly = always

# TODO, compose is wrong order at the moment
sequence = compose