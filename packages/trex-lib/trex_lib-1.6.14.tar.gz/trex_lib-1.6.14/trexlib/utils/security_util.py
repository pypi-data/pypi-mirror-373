import hashlib, hmac, time, uuid, json
from trexconf import conf
import logging
from basicauth import encode as basic_encode, decode as basic_decode

logger = logging.getLogger('lib')

#-----------------------------------------------------------------
# Password Hashing & Blending
# DO NOT CHANGE AFTER DEPLOYED TO PRODUCTION
#-----------------------------------------------------------------
def hash_password(unique_id, password):
    # sha512 hashing with custom algorithm
    hashed_password = ""
    
    if password and unique_id:
        #password = password.decode('utf-8')
        logger.debug('unique_id=%s', unique_id)
        logger.debug('password=%s', password)
        logger.debug('conf.MAX_PASSWORD_LENGTH=%s', conf.MAX_PASSWORD_LENGTH)
        
        blended_password = blend_password(unique_id, password)
        logger.debug('blended_password=%s', blended_password)
        
        
        password_salt = conf.SECRET_KEY 
        
        logger.debug('password_salt=%s', password_salt)
        
        hash_512 = hashlib.sha512()
        hash_512.update(('%s%s' % (password_salt, password)).encode('utf-8'))
        hashed_password = hash_512.hexdigest()
        
        logger.debug('hashed_password=%s', hashed_password)
        
        final_hashed_password =   hashed_password[0: int(conf.MAX_PASSWORD_LENGTH,10)]
        
        logger.debug('final_hashed_password=%s', final_hashed_password)
        
        return final_hashed_password 

def blend_password(unique_id, password):
    return unique_id + '!7' + password
#-----------------------------------------------------------------

#-----------------------------------------------------------------
# User ID generation
#-----------------------------------------------------------------

def generate_user_id ():
    user_id=generate_unique_random_characters()
    #return user_id[ len(user_id)-12:len(user_id) ]
    return user_id
    
#-----------------------------------------------------------------



#-----------------------------------------------------------------
# <<<<< Others >>>>>
#-----------------------------------------------------------------
def generate_unique_random_characters(limit=conf.MAX_CHAR_RANDOM_UUID4):
    return str( uuid.uuid4() )[:limit]

def get_issued_time():
    return int(time.time())

def is_time_expired (issued_time, expiration_miliseconds):
    return issued_time < (time.time() - expiration_miliseconds)
#-----------------------------------------------------------------


def create_basic_authentication(username, password):
    return basic_encode(username, password)

def verfiy_basic_authentication(authentication_token, username, password):
    (decoded_username, decoded_password)  = basic_decode(authentication_token)
    
    logger.debug('decoded_username')
    logger.debug('decoded_password')
    
    return decoded_username==username and decoded_password==password


def __ascii2Int(value):
    if value:
        int_keys = []
        for a in value:
            int_keys.append(ord(a))

        return int_keys


def __int2ascii(value):
    if value:
        ascii_keys = ''
        for a in value:
            ascii_keys+=chr(a)

        return ascii_keys
    

