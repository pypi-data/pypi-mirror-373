'''
Created on 29 Apr 2020

@author: jacklok
'''
import hashlib
import logging
from six.moves.urllib.parse import urlencode, quote_plus
 
logger = logging.getLogger('lib') 
 
def get_gravatar_url(email):
    
    #default = "https://www.example.com/default.jpg"
    size = 40
    
    email = email.encode('utf-8')
    
    logger.debug('email=%s', email)
    # construct the url
    hashed_email = hashlib.md5(email.lower()).hexdigest()
    logger.debug('hashed_email=%s', hashed_email)
    gravatar_url = "https://www.gravatar.com/avatar/" + hashlib.md5(email.lower()).hexdigest() + "?"
    #gravatar_url += urlencode({'d':default, 's':str(size)}, quote_via=quote_plus)
    gravatar_url += urlencode({'s':str(size)}, quote_via=quote_plus)
    
    logger.debug('gravatar_url=%s', gravatar_url)
    
    return gravatar_url
