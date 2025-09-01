'''
Created on 13 Jan 2021

@author: jacklok
'''
from google.cloud import tasks_v2
from trexconf import conf as lib_conf 
import logging, json
from datetime import datetime, timedelta
from google.oauth2 import service_account 
from google.protobuf import timestamp_pb2
from trexlib.utils.security_util import create_basic_authentication, verfiy_basic_authentication
from trexlib.utils.string_util import random_string
from trexconf.conf import SYSTEM_TASK_SERVICE_CREDENTIAL_PATH
from trexlib.conf_to_remove import SYSTEM_TASK_GCLOUD_PROJECT_ID,\
    SYSTEM_TASK_GCLOUD_LOCATION, SYSTEM_TASK_SERVICE_ACCOUNT_EMAIL

logger = logging.getLogger('utils-debug')

def create_task(task_url, queue_name, payload={}, in_seconds=1, http_method='get', headers=None, 
                credential_path=SYSTEM_TASK_SERVICE_CREDENTIAL_PATH, 
                project_id=SYSTEM_TASK_GCLOUD_PROJECT_ID, 
                location=SYSTEM_TASK_GCLOUD_LOCATION, 
                service_email=SYSTEM_TASK_SERVICE_ACCOUNT_EMAIL
                ): 
    
    cred = service_account.Credentials.from_service_account_file(
                                                            credential_path,
                                                            scopes=["https://www.googleapis.com/auth/cloud-platform", 
                                                                    "https://www.googleapis.com/auth/cloud-tasks"
                                                                    ]
                                                            )
    
    task_id = random_string(12)
    
    client = tasks_v2.CloudTasksClient(credentials=cred)
        
    parent = client.queue_path(project_id, location, queue_name)
    
    logger.info(">>>>>>>>>>>>>>>>create_task: task_url=%s", task_url)
    logger.info(">>>>>>>>>>>>>>>>create_task: credential_path=%s", credential_path)
    logger.info(">>>>>>>>>>>>>>>>create_task: project_id=%s", project_id)
    logger.info(">>>>>>>>>>>>>>>>create_task: location=%s", location)
    logger.info(">>>>>>>>>>>>>>>>create_task: service_email=%s", service_email)
    
    task = {
        "http_request": {  # Specify the type of request.
                         "http_method"  : tasks_v2.HttpMethod.POST if http_method.lower()=='post' or payload is not None else tasks_v2.HttpMethod.GET,
                         "url"          : task_url,  
                         "oidc_token"   : {"service_account_email": service_email},
                        }
        }
    
    if payload is not None:
        if isinstance(payload, dict):
            # Convert dict to JSON string
            payload = json.dumps(payload)
            # specify http content-type to application/json
            task["http_request"]["headers"] = {"Content-type": "application/json"}
        else:
            task["http_request"]["headers"] = {"Content-type": "application/x-www-form-urlencoded"}
            
        # The API expects a payload of type bytes.
        converted_payload = payload.encode()
        
        logger.debug('create_task: converted_payload=%s', converted_payload)
    
        # Add the payload to the request.
        task["http_request"]["body"] = converted_payload
    else:
        task["http_request"]["headers"] = {"Content-type": "application/x-www-form-urlencoded"}
        
    
    if headers is not None:
        for k,v in headers.items():
            task["http_request"]["headers"][k]=v
            
    
    task["http_request"]["headers"]['X-task-id']        = task_id
    task["http_request"]["headers"]['X-task-token']     = create_task_authenticated_token(task_id)
        
    if in_seconds is not None:
        # Convert "seconds from now" into an rfc3339 datetime string.
        d = datetime.utcnow() + timedelta(seconds=in_seconds)
    
        # Create Timestamp protobuf.
        timestamp = timestamp_pb2.Timestamp()
        timestamp.FromDatetime(d)
    
        # Add the timestamp to the tasks.
        task["schedule_time"] = timestamp    
    
    logger.info('task["http_request"]["headers"]=%s', task["http_request"].get("headers"))
    
    response = client.create_task(request={"parent": parent, "task": task})
    
    logger.info('response=%s', response)
    
    return response


def create_task_authenticated_token(id):
    return create_basic_authentication(id, lib_conf.SECRET_KEY)

def check_is_task_authenticated_token_valid(token, id):
    return verfiy_basic_authentication(token, id, lib_conf.SECRET_KEY)



