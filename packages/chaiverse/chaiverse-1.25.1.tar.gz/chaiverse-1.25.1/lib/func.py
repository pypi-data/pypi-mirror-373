from base64 import b64encode, b64decode
import dill


def serialize_function(function):
    # Pickle the function (use dill as usual
    # pickle doesn't work on locals/lambdas
    function = dill.dumps(function)
    # Convert to JSON-serialisable byte string
    function = b64encode(function)
    # Convert to plain string
    function = function.decode("utf-8")
    return function


def deserialize_function(function):
    function = b64decode(function)
    function = dill.loads(function)
    return function


def dedupe_list(values):
    '''
    This dedupe list function preserves order that ensure deterministic outcome, so
     1. test result will not be dependent on the run
     2. fewer edge cases
    '''
    return list(dict.fromkeys(values))


def is_base_64(string):
    if type(string) != bytes:
        string = string.encode()
    try:
        is_base_64 = b64encode(b64decode(string)) == string
    except:
        is_base_64 = False
    return is_base_64


class class_property(property):
    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)
