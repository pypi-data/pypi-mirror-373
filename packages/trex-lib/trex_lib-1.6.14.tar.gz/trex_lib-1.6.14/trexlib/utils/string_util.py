'''
Created on Jul 3, 2012

@author: sglok
'''
import random, re, string, logging
import hmac
from datetime import datetime

WHITESPACE_PATTERN  = re.compile(r'\s')
DASH_PATTERN        = re.compile(r'-')

ALPHANUMERIC_CHARS  = string.ascii_lowercase + string.ascii_uppercase + string.digits
NUMERIC_CHARS       = string.digits

HUMAN_SAFE_ALPHANUMERIC_CHARS     = 'abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ123456789'



def safe_str_cmp(a: str, b: str) -> bool:
    """This function compares strings in somewhat constant time. This
    requires that the length of at least one string is known in advance.

    Returns `True` if the two strings are equal, or `False` if they are not.
    """

    if isinstance(a, str):
        a = a.encode("utf-8")  # type: ignore

    if isinstance(b, str):
        b = b.encode("utf-8")  # type: ignore

    return hmac.compare_digest(a, b)

def random_string(number_character, is_human_mistake_safe=False):
    random.seed(datetime.now().timestamp())
    if is_human_mistake_safe:
        if number_character and type(number_character) is int and number_character>=0:
            return ''.join(random.sample(HUMAN_SAFE_ALPHANUMERIC_CHARS, number_character))
        else:
            return ''

    else:
        if number_character and type(number_character) is int and number_character>=0:
            return ''.join(random.sample(ALPHANUMERIC_CHARS, number_character))
        else:
            return ''

def random_number(number_character):
    if number_character and type(number_character) is int and number_character>=0:
        return ''.join([random.choice(NUMERIC_CHARS) for _ in range(number_character)])
    else:
        return ''

def is_ascii(s):
    return all(ord(c) < 128 for c in s)

def str_to_bool(value):
    if value:
        if "on"==value.lower() or "true"==value.lower() or "yes"==value.lower() or "y"==value.lower():
            return True
    return False
    
def remove_whitespace(value=None, replacement='_'):
    if value is not None and len(value.strip())>0:
        modified = re.sub(WHITESPACE_PATTERN, replacement, value)
        return modified
    else:
        raise ValueError('Illegal argument exception, where restaurant name is required.')

def remove_dash(value=None, replacement=''):
    if value is not None and len(value.strip())>0:
        modified = re.sub(DASH_PATTERN, replacement, value)
        return modified
    else:
        raise ValueError('Illegal argument exception, where restaurant name is required.')
    
def boolify(val, default=False):
    if (isinstance(val, str) and bool(val)):
        return not val in ('False', '0', 'false', 'no', 'No', 'n')
    else:
        if val:
            return bool(val)
        else:
            return default
    
def to_hex(value):
    res = ""
    for c in value:
        res += "%04X" % ord(c) #at least 2 hex digits, can be more
    return res

def four_digit_escape(string):
    try:
        decoded_string = string.decode('utf-8')
        #return u''.join(char if 32 <= ord(char) <= 126 else u'%04x' % ord(char) for char in decoded_string)
        return u''.join(u'%04x' % ord(char) for char in decoded_string)
    except:
        #return u''.join(char if 32 <= ord(char) <= 126 else u'%04x' % ord(char) for char in string)
        return u''.join(u'%04x' % ord(char) for char in string)

def unicode_(msg):
    new_msg = []
    for char in msg:
        try:
            char = chr(int(char, 16))
        except ValueError:
            char = '?'
        new_msg.append(char)
    return ''.join(new_msg)

def is_match(regex, val):
    logging.debug('is_match')
    if val:
        if re.match(regex, val):
            return True
        return False
    else:
        return True

def random_int_str(range_from, range_to, zero_padding):
    from random import randint
    i = randint(range_from, range_to)
    if zero_padding:
        return str(i).zfill(zero_padding)
    else:
        return str(i)

def is_empty(value):
    if isinstance(value, str):
        if value is None or value.strip()=='' or value.strip()=='null' or value.strip()=='None':
            return True
        
    elif isinstance(value,(dict,list)):
        if len(value)==0:
            return True
          
    else:
        return value is None
    
    return False

def is_not_empty(value):
    return is_empty(value)==False

def truncate_if_max_length(value, max_length):
    if value:
        return value[:max_length]

def truncate_string(original_string, max_length):
    if len(original_string) <= max_length:
        return original_string
    else:
        truncated_string = original_string[:max_length]
        return truncated_string

def resolve_unicode_value(unicode_value):
    if unicode_value:
        unicode_value = unicode_value.decode('utf-8')
        return unicode_value
    else:
        return unicode_value


def base64Encode(value):
    import base64
    return base64.b64encode(bytes(value, 'utf-8'))

def split_by_length(str_value, length):
    def _f(str_value, length):
        while str_value:
            yield str_value[:length]
            str_value = str_value[length:]
    return list(_f(str_value, length))
