'''
Created on 24 Dec 2020

@author: jacklok
'''
import logging, json
from google.oauth2 import service_account
from google.cloud import storage
from trexconf import conf as lib_conf

logger = logging.getLogger('debug')


def create_cloud_storage_client(info=None, credential_filepath=None):
    if info:
        cred = service_account.Credentials.from_service_account_info(info)
        
    else:
        if credential_filepath:
            cred = service_account.Credentials.from_service_account_file(credential_filepath)
        else:
            cred = service_account.Credentials.from_service_account_file(
                                                            lib_conf.STORAGE_CREDENTIAL_PATH)
    
    
    logger.debug('admin_conf.STORAGE_CREDENTIAL_PATH=%s', lib_conf.STORAGE_CREDENTIAL_PATH)
    logger.debug('cred._project_id=%s', cred._project_id)
    logger.debug('cred.service_account_email=%s', cred.service_account_email)
    
    
    client = storage.Client(project=lib_conf.CLOUD_STORAGE_PROJECT_ID, credentials=cred)
    
    return client

def connect_to_bucket(info=None, credential_filepath=None):    
    client = create_cloud_storage_client(info=info, credential_filepath=credential_filepath)
    # Get the bucket that the file will be uploaded to.
    bucket = client.get_bucket(lib_conf.CLOUD_STORAGE_BUCKET)
    
    return bucket