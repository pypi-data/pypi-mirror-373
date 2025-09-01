'''
Created on 3 Sep 2020

@author: jacklok
'''
import phonenumbers
from phonenumbers import carrier
from phonenumbers.phonenumberutil import number_type
import logging 
from trexlib.utils.log_util import get_tracelog

logger = logging.getLogger('phone_util')

def is_mobile_phone(phone_no):
    if phone_no:
        try:
            phone_no_obj = phonenumbers.parse(phone_no, _check_region=False)
            logger.debug('phone_no_obj=%s', phone_no_obj)
            ntype = number_type(phone_no_obj)
            logger.debug('ntype=%s', ntype)
            return carrier._is_mobile(ntype)
        except:
            logger.error('Failed to parse phone no (%s) due to %s', phone_no, get_tracelog())
            return False
    else:
        return False

def normalized_mobile_phone(phone_no):
    if is_mobile_phone(phone_no):
        try:
            parsed_mobile_phone = phonenumbers.parse(phone_no, _check_region=False)
            return '+%s%s' % (parsed_mobile_phone.country_code, parsed_mobile_phone.national_number)
        except:
            return None
    return None

