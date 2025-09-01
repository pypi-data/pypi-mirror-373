'''
Created on 4 Apr 2024

@author: jacklok
'''
import requests, logging
from trexconf.conf import WHATSAPP_TOKEN, WHATSAPP_PHONE_NUMBER_ID,FACEBOOK_API_VERSION

logger = logging.getLogger('utils')
    
def _construct_whatasapp_message_header():
    return {
                "Authorization": f"Bearer %s" % WHATSAPP_TOKEN,
                "Content-Type": "application/json",
            }
    
def _construct_whatsapp_message_url():
    return "https://graph.facebook.com/%s/%s/messages" % (FACEBOOK_API_VERSION, WHATSAPP_PHONE_NUMBER_ID)

def __send_whatsapp_template_message(to_number, template_name, components, language='en'):
    if '+' ==  to_number[0]:
        to_number = to_number[1:]
    
    data = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "template",
        "template": {
                    "name": template_name,
                    "language": {
                                 "code": language
                                },
                    "components":components
                    },
    }
    
    logger.info(data)
    
    whatsapp_target_url = _construct_whatsapp_message_url()
    logger.info('whatsapp_target_url=%s', whatsapp_target_url)
    
    response = requests.post(
                whatsapp_target_url, 
                json=data, headers=_construct_whatasapp_message_header()
                )
    logger.debug('whatsapp message response: %s', response.json())    
    
    response.raise_for_status()

def send_whatsapp_text_message(to_number, text_message):
    if '+' ==  to_number[0]:
        to_number = to_number[1:]
        
    data = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": text_message},
    }
    response = requests.post(
                _construct_whatsapp_message_url(), 
                json=data, headers=_construct_whatasapp_message_header()
                )
    logger.debug('whatsapp message response: %s', response.json())

def send_whatsapp_verification_message(to_number, verification_code, request_id=None, language='en', ):
    
    request_id_n_verification_code = '%s - %s' % (request_id, verification_code)
    
    components = [
         {
              "type": "body",
              "parameters": [
                {
                  "type": "text",
                  "text": request_id_n_verification_code
                },
                 ]
            },
            {
            "type": "button",
            "sub_type": "url",
            "index": 0,
            "parameters": [
              {
                "type": "text",
                "text": verification_code
              }
            ]
          }

        ]
    __send_whatsapp_template_message(to_number, 'mobile_phone_verification', components, language=language)
    

