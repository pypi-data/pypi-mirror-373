'''
Created on 21 Apr 2020

@author: jacklok
'''

import json, logging
from math import log
import string
import random

import itertools
import typing

T = typing.TypeVar("T")


logger = logging.getLogger('common_util')

UNIT_LIST = zip(['bytes', 'kB', 'MB', 'GB', 'TB', 'PB'], [0, 0, 1, 2, 2, 2])


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


def str2int(str, default_value=0):
    if str:
        try:
            return int(str)
        except:
            return default_value
    else:
        return default_value
    
def str2float(str, default_value=0):
    if str:
        try:
            return float(str)
        except:
            return float(default_value)
    else:
        return float(default_value)
    
    
def list_exist_in_list(list1=[], list2=[]):
    for i in list1:
        if i in list2:
            return True
    
    return False

def generateEAN13CheckDigit(prefix, first9digits):

    final_digits = '%s%s' % (prefix, first9digits)
    charList = [char for char in final_digits]
    ean13 = [1,3]
    total = 0
    for order, char in enumerate(charList):
        total += int(char) * ean13[order % 2]

    checkDigit = 10 - total % 10
    if (checkDigit == 10):
        return 0

    return checkDigit

def sort_dict_by_value(original_dict):
    if original_dict:
        from collections import OrderedDict
        d_sorted_by_value = OrderedDict(sorted(original_dict.items(), key=lambda x: x[1]))
        return d_sorted_by_value
    else:
        return original_dict

def sort_list(sorting_list, sort_attr_name=None, reverse_order=False, default_value=None):
    if sorting_list:
        logging.debug('sort_attr_name=%s', sort_attr_name)
        new_list = sort_list_by_condition(sorting_list, 
                                          condition=lambda x: (hasattr(x, sort_attr_name), getattr(x, sort_attr_name, default_value) if hasattr(x, sort_attr_name) else default_value), 
                                          reverse_order=reverse_order)
        return new_list
    else:
        return []

def sort_dict_list(sorting_list, sort_attr_name=None, reverse_order=False, default_value=None):
    if sorting_list:
        logging.debug('sort_attr_name=%s', sort_attr_name)
        new_list = sort_list_by_condition(sorting_list, 
                                          condition=lambda x: (hasattr(x, sort_attr_name), getattr(x, sort_attr_name, default_value) if hasattr(x, sort_attr_name) else default_value), 
                                          reverse_order=reverse_order)
        return new_list
    else:
        return []


def sort_list_by_condition(list, condition=None, reverse_order=False, ):
    if list:
        new_list = sorted(list, key=condition, reverse=reverse_order)
        return new_list
    else:
        return []


def sizeof_fmt(num):
    """Human friendly file size"""
    if isinstance(num, str):
        num = float(num)

    if num > 1:
        exponent = min(int(log(num, 1024)), len(UNIT_LIST) - 1)
        quotient = float(num) / 1024**exponent
        unit, num_decimals = UNIT_LIST[exponent]
        format_string = '{:.%sf} {}' % (num_decimals)
        return format_string.format(quotient, unit)
    if num == 0:
        return '0 bytes'
    if num == 1:
        return '1 byte'
    
def lookahead(iterable):
    """Pass through all values from the given iterable, augmented by the
    information if there are more values to come after the current one
    (True), or if it is the last value (False).
    """
    # Get an iterator and pull the first value.
    it = iter(iterable)
    last = next(it)
    # Run the iterator to exhaustion (starting from the second value).
    for val in it:
        # Report the *previous* value (more to come).
        yield last, True
        last = val
    # Report the last value.
    yield last, False    
    

class OrderedSet(typing.MutableSet[T]):
    """A set that preserves insertion order by internally using a dict."""

    def __init__(self, iterable: typing.Iterator[T]):
        self._d = dict.fromkeys(iterable)

    def add(self, x: T) -> None:
        self._d[x] = None

    def discard(self, x: T) -> None:
        self._d.pop(x, None)

    def __contains__(self, x: object) -> bool:
        return self._d.__contains__(x)

    def __len__(self) -> int:
        return self._d.__len__()

    def __iter__(self) -> typing.Iterator[T]:
        return self._d.__iter__()

    def __str__(self):
        return f"{{{', '.join(str(i) for i in self)}}}"

    def __repr__(self):
        return f"<OrderedSet {self}>"
    
    

        
    






