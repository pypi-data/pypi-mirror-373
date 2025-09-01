'''
Created on 10 Apr 2020

@author: jacklok
'''
 
import traceback, sys

def get_tracelog():
    return ''.join(traceback.format_exception(*sys.exc_info()))

