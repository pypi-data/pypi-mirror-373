'''
Created on 30 Aug 2023

@author: jacklok
'''
import logging, os, csv

logger = logging.getLogger('util')

def read_config(config_file):
    properties = {}

    with open(config_file, 'r') as file:
        for line in file:
            if line.strip() != "":
                key, value = line.strip().split('=')
                
                #logger.debug('key=%s, value=%s', key, value)
                if value.strip().startswith("'") or value.strip().startswith('"'):
                    properties[key.strip()] = value.strip()[1:-1]
                    #logger.debug('It is string value')
                elif value.strip() in ('True', 'False', 'true', 'false', 'yes', 'no'):
                    properties[key.strip()] = bool(value.strip())
                    #logger.debug('It is bool value')
                else:
                    properties[key.strip()] = int(value.strip())
                    #logger.debug('It is integer value')
            
    return properties


    
