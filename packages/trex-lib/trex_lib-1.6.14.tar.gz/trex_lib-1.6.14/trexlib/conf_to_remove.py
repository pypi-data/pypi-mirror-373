'''
Created on 4 Sep 2020

@author: jacklok
'''


import os, config_path

PRODUCTION_MODE                                     = "PROD"
DEMO_MODE                                           = "DEMO"
LOCAL_MODE                                          = "LOCAL"

DEPLOYMENT_MODE                                     = os.environ.get('DEPLOYMENT_MODE')

SECRET_KEY                                          = os.environ.get('SECRET_KEY')
MAX_PASSWORD_LENGTH                                 = os.environ.get('MAX_PASSWORD_LENGTH')

SYSTEM_TASK_GCLOUD_PROJECT_ID                       = os.environ.get('SYSTEM_TASK_GCLOUD_PROJECT_ID')
SYSTEM_TASK_GCLOUD_LOCATION                         = os.environ.get('SYSTEM_TASK_GCLOUD_LOCATION')
SYSTEM_TASK_SERVICE_ACCOUNT_KEY                     = os.environ.get('SYSTEM_TASK_SERVICE_ACCOUNT_KEY')
SYSTEM_TASK_SERVICE_CREDENTIAL_PATH                 = os.path.abspath(os.path.dirname(config_path.__file__)) + '/' + SYSTEM_TASK_SERVICE_ACCOUNT_KEY
SYSTEM_TASK_SERVICE_ACCOUNT_EMAIL                   = os.environ.get('SYSTEM_TASK_SERVICE_ACCOUNT_EMAIL')

SYSTEM_BASE_URL                                     = os.environ.get('SYSTEM_BASE_URL')


STORAGE_SERVICE_ACCOUNT_KEY_FILEPATH                = os.environ['CLOUD_STORAGE_SERVICE_ACCOUNT_KEY']
STORAGE_CREDENTIAL_PATH                             = os.path.abspath(os.path.dirname(__file__)) + '/../' + STORAGE_SERVICE_ACCOUNT_KEY_FILEPATH

CLOUD_STORAGE_BUCKET                                = os.environ.get('CLOUD_STORAGE_BUCKET')
CLOUD_STORAGE_PROJECT_ID                            = os.environ.get('CLOUD_STORAGE_PROJECT_ID')


SMS_GATEWAY_PATH                                    = os.environ.get('SMS_GATEWAY_PATH')
SMS_GATEWAY_URL                                     = os.environ.get('SMS_GATEWAY_URL')

SMS_GATEWAY_USERNAME                                = os.environ.get('SMS_GATEWAY_USERNAME')
SMS_GATEWAY_PASSWORD                                = os.environ.get('SMS_GATEWAY_PASSWORD')
SMS_GATEWAY_SENDER                                  = os.environ.get('SMS_GATEWAY_SENDER')

WHATSAPP_TOKEN                                      = os.environ.get('WHATSAPP_TOKEN')
WHATSAPP_PHONE_NUMBER_ID                            = os.environ.get('WHATSAPP_PHONE_NUMBER_ID')
WHATSAPP_VERIFY_TOKEN                               = os.environ.get('WHATSAPP_VERIFY_TOKEN')
FACEBOOK_API_VERSION                                = os.environ.get('FACEBOOK_API_VERSION')



def task_url(path):
    return '{}{}'.format(SYSTEM_BASE_URL, path)

CHECK_CUSTOMER_ENTITLE_REWARD_TASK_URL              = task_url('/rewarding/check-entitle-reward')
SEND_EMAIL_TASK_URL                                 = task_url('/system/send-email')


CRYPTO_SECRET_KEY                                   = os.environ.get('CRYPTO_SECRET_KEY')

DEFAULT_COUNTRY_CODE                                = 'my'
DEFAULT_GMT                                         = 8


DEFAULT_DATETIME_FORMAT                             = '%d/%m/%Y %H:%M:%S'
DEFAULT_DATE_FORMAT                                 = '%d/%m/%Y'
DEFAULT_TIME_FORMAT                                 = '%H:%M:%S'


DEFAULT_ETAG_VALUE                              = '68964759a96a7c876b7e'

MODEL_CACHE_ENABLED                             = False

INTERNAL_MAX_FETCH_RECORD                       = 9999
MAX_FETCH_RECORD_FULL_TEXT_SEARCH               = 1000
MAX_FETCH_RECORD_FULL_TEXT_SEARCH_PER_PAGE      = 10
MAX_FETCH_RECORD                                = 99999999
MAX_FETCH_IMAGE_RECORD                          = 100
MAX_CHAR_RANDOM_UUID4                           = 20
PAGINATION_SIZE                                 = 10
VISIBLE_PAGE_COUNT                              = 10

GENDER_MALE_CODE                                = 'm'
GENDER_FEMALE_CODE                              = 'f'



APPLICATION_ACCOUNT_PROVIDER                    = 'app'

SUPPORT_LANGUAGES                               = ['en','zh']

#-----------------------------------------------------------------
# Web Beacon settings
#-----------------------------------------------------------------
WEB_BEACON_TRACK_EMAIL_OPEN   = 'eo'

#-----------------------------------------------------------------
# Miliseconds settings
#-----------------------------------------------------------------
MILLISECONDS_ONE_MINUTES    = 60
MILLISECONDS_FIVE_MINUTES   = 300
MILLISECONDS_TEN_MINUTES    = 600
MILLISECONDS_TWENTY_MINUTES = 1200
MILLISECONDS_THIRTY_MINUTES = 1800
MILLISECONDS_ONE_HOUR       = 3600
MILLISECONDS_TWO_HOUR       = 7200
MILLISECONDS_FOUR_HOUR      = 14400
MILLISECONDS_EIGHT_HOUR     = 28800
MILLISECONDS_TEN_HOUR       = 36000
MILLISECONDS_TWELVE_HOUR    = 43200
MILLISECONDS_TWENTY_HOUR    = 72000
MILLISECONDS_ONE_WEEK       = 604800
MILLISECONDS_ONE_DAY        = 86400
MILLISECONDS_HALF_DAY       = 43200
MILLISECONDS_ONE_HOUR       = 3600
MILLISECONDS_TWO_HOUR       = 7200
MILLISECONDS_HALF_AN_HOUR   = 1800
MILLISECONDS_QUATER_AN_HOUR = 900 

#-----------------------------------------------------------------
# Cache settings
#-----------------------------------------------------------------
AGE_TIME_FIVE_MINUTE    = 60*5
AGE_TIME_QUATER_HOUR    = AGE_TIME_FIVE_MINUTE * 3
AGE_TIME_HALF_HOUR      = AGE_TIME_QUATER_HOUR * 2
AGE_TIME_ONE_HOUR       = AGE_TIME_HALF_HOUR * 2
AGE_TIME_TWO_HOUR       = AGE_TIME_ONE_HOUR * 2
AGE_TIME_SIX_HOUR       = AGE_TIME_ONE_HOUR * 6
AGE_TIME_ONE_DAY        = AGE_TIME_ONE_HOUR * 24
   
    
    
