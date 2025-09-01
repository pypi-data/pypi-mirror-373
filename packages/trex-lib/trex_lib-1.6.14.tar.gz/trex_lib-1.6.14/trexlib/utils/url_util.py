'''
Created on Jul 3, 2012

@author: sglok
'''
import base64,logging, hashlib
from trexlib.utils.log_util import get_tracelog
from binascii import unhexlify, b2a_base64
from urllib.parse import urlencode
from urllib.request import urlopen 
 
def base64_url_decode(data):
    data = data.encode(u'utf-8')
    data += '=' * (4 - (len(data) % 4))
    try:
        decoded_url = base64.urlsafe_b64decode(data)
        return decoded_url
    except:
        logging.error("Failed to decode url due to %s", get_tracelog())
        return data

def base64_url_encode(data):
    try:
        return base64.urlsafe_b64encode(data).rstrip('=')
    except:
        logging.debug('%s', get_tracelog())
        return base64.urlsafe_b64encode(data.encode('utf-8')).rstrip('=')
    
def urlencode_utf8(params):
    return urlencode(dict([k.encode('utf-8'), str(v).encode('utf-8')] for k,v in params.items()))

def create_tiny_url(long_url):
    apiurl = "http://tinyurl.com/api-create.php?url="
    tinyurl = urlopen(apiurl + long_url).read()
    return tinyurl

def hex_2_ascii(hex_string):
    if hex_string:
        return b2a_base64(unhexlify(hex_string)).replace('\n','')
    return hex_string

def base64_sha1(input):
    return base64.b64encode(hashlib.sha1(input).digest())





    