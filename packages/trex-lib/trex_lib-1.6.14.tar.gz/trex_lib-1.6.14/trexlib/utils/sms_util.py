'''
Created on 16 Aug 2023

@author: jacklok
'''

import logging, time
import phonenumbers
from phonenumbers import carrier
from phonenumbers.phonenumberutil import number_type
from trexconf import conf
from trexlib.utils.log_util import get_tracelog
from six.moves import http_client
from six.moves.urllib.parse import urlencode
from trexlib.utils.string_util import four_digit_escape, is_ascii, random_string
from datetime import datetime

logger = logging.getLogger('util')

class SMSGatewayProvider(object):
    
    def send_sms(self, body=None, to_number=None, from_number=None):
        pass
    

class SilverStreetSMSGatewayProvider(SMSGatewayProvider):

    def __init__(self, sms_gateway_sender=None):
        self.sms_gateway_sender = sms_gateway_sender
    
    def send_sms(self, body=None, to_number=None, reference=None, batch_id=0):
        logger.info('SilverStreetSMSGatewayProvider.send_sms: to_number=%s', to_number)
        logger.info('SilverStreetSMSGatewayProvider.send_sms: body=%s', body)

        normalized_number_list = []

        if isinstance(to_number, (tuple,list)):
            logging.info('SilverStreetSMSGatewayProvider.send_sms: list of phone number')
            for n in to_number:
                if is_mobile_phone(n):
                    logging.info('SilverStreetSMSGatewayProvider.send_sms: %s is mobile phone number', n)
                    __normalized_mobile_phone = normalized_mobile_phone(n)
                    if __normalized_mobile_phone:
                        logging.info('SilverStreetSMSGatewayProvider.send_sms: normalised mobile phone=%s', __normalized_mobile_phone)
                        normalized_number_list.append(__normalized_mobile_phone)
                else:
                    logging.info('SilverStreetSMSGatewayProvider.send_sms: %s is not mobile phone number', n)
        elif is_mobile_phone(to_number):
            logging.info('SilverStreetSMSGatewayProvider.send_sms: is mobile phone')
            __normalized_mobile_phone = normalized_mobile_phone(to_number)
            logging.info('SilverStreetSMSGatewayProvider.send_sms: normalised mobile phone=%s', __normalized_mobile_phone)
            normalized_number_list.append(__normalized_mobile_phone)
        else:
            logging.info('SilverStreetSMSGatewayProvider.send_sms: no mobile phone found')
            

        logging.info('SilverStreetSMSGatewayProvider.send_sms: normalized_number_list=%s', normalized_number_list)

        if normalized_number_list:
            try:
                encoded_body = body
                bodytype = 1
                if not is_ascii(body):
                    
                    bodytype = 4
                    encoded_body = four_digit_escape(encoded_body)
                #else:
                    #encoded_body = body[0:149]

                logging.info('bodytype=%s', bodytype)
                logging.info('encoded_body=%s', encoded_body)
                
                username    = conf.SMS_GATEWAY_USERNAME
                password    = conf.SMS_GATEWAY_PASSWORD
                sender      = conf.SMS_GATEWAY_SENDER
                
                

                params = {
                    'username'      : username,
                    'password'      : password,
                    'sender'        : sender,
                    'body'          : encoded_body,
                    'bodytype'      : bodytype,
                    'destination'   : self.__format_destination_number(normalized_number_list)
                }

                if reference:
                    params['reference'] = '%s-%s-%s'%(reference, batch_id, conf.DEPLOYMENT_MODE)
                    params['service']   = reference
                    params['dlr']       = 1

                encoded_params = urlencode(params)

                #logging.debug('params=%s', params)
                logger.debug('encoded_params=%s', encoded_params)

                headers = {"Content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                       "Accept": "text/plain"}
                
                logger.info('customization_conf.SMS_GATEWAY_PATH=%s', conf.SMS_GATEWAY_PATH)
                
                conn = http_client.HTTPConnection(conf.SMS_GATEWAY_PATH)
                
                #response = requests.post(customization_conf.SMS_GATEWAY_URL, data=encoded_params, headers=headers)

                conn.request("POST", "/send.php", encoded_params, headers)
                
                
                response = conn.getresponse()

                logger.debug('response=%s', response)
                logger.info('params=%s', params)
                logger.info('response.status=%s', response.status)
                logger.info('response.msg=%s', response.msg)
                logger.info('response.reason=%s', response.reason)
                logger.info('response.read=%s', response.read())
                
                return True
            except:
                logging.error('Failed to send sms message via SilverStreet SMS Gateway, where %s', get_tracelog())
                return False
        else:
            logging.debug('invalid mobile phone =%s', to_number)
        
    def __format_destination_number(self, destination_no):
        if isinstance(destination_no, str):
            final_destination_no = destination_no
            if destination_no and destination_no.startswith('+'):
                final_destination_no = final_destination_no[1:]
            
            if final_destination_no:
                final_destination_no = final_destination_no.replace(' ','')
                final_destination_no = final_destination_no.replace('-','')
            return final_destination_no
        elif isinstance(destination_no, (list, tuple)):
            final_destination_no = []
            for _dest_no in destination_no:
                formatted_desti_no = self.__format_destination_number(_dest_no)
                if not formatted_desti_no in final_destination_no:
                    final_destination_no.append(formatted_desti_no)
            
            return ",".join(final_destination_no)

def send_sms(to_number=None, body=None, reference=None, batch_id=0):
    logging.debug('-----------------------------send_sms---------------------------------')
    logging.debug('to_number=%s', to_number)
    logging.debug('body=%s', body)

    if reference is None:
        now = datetime.now()
        reference = '%s.%s'  %(int(time.mktime(now.timetuple())), random_string(6))

    sms_provider = SilverStreetSMSGatewayProvider()
    #sms_provider = MockSMSGatewayProvider()
    return sms_provider.send_sms(to_number=to_number,  
                                 body=body, 
                                 reference=reference, batch_id=batch_id)
        
def is_mobile_phone(phone_no, default_country_code=conf.DEFAULT_COUNTRY_CODE.upper()):
    if phone_no:
        try:
            logger.info('checking %s', phone_no)
            phone_no_obj = phonenumbers.parse(phone_no, region=default_country_code, _check_region=False)
            logger.info('phone_no_obj=%s', phone_no_obj)
            ntype = number_type(phone_no_obj)
            logger.info('ntype=%s', ntype)
            is_mobile =  carrier._is_mobile(ntype)
            
            logger.info('is_mobile=%s', is_mobile)
            
            return is_mobile
        except:
            logging.warn('Failed to parse due to %s', get_tracelog())
            return False
    else:
        return False

def normalized_mobile_phone(phone_no, default_country_code=conf.DEFAULT_COUNTRY_CODE.upper()):
    if is_mobile_phone(phone_no):
        try:
            parsed_mobile_phone = phonenumbers.parse(phone_no, region=default_country_code)
            return '+%s%s' % (parsed_mobile_phone.country_code, parsed_mobile_phone.national_number)
        except:
            return None
    return None

def format_mobile_phone(phone_no, default_country_code=conf.DEFAULT_COUNTRY_CODE.upper()):
    parsed_mobile_phone = phonenumbers.parse(phone_no, region=default_country_code)
    return '+%s%s' % (parsed_mobile_phone.country_code, parsed_mobile_phone.national_number)        
