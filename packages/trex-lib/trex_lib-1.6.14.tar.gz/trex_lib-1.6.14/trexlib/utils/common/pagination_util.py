'''
Created on 3 Sep 2020

@author: jacklok
'''
from trexconf import conf
import logging 
from six import string_types

logger = logging.getLogger('pagination_util')


def get_offset_by_page_no(page_no, limit=conf.PAGINATION_SIZE):
    logger.debug('---get_offset_by_page_no---')
    
    if page_no is not None:
        if isinstance(page_no, string_types):
            try:
                page_no = int(page_no, 10)
                
            except:
                logging.warn('invalid value of page_no')
                page_no = 0
        
        logging.debug('page_no=%d', page_no)
        
        if limit is not None:
            if isinstance(limit, string_types):
                try:
                    limit = int(limit, 10)
                    
                except:
                    logging.warn('invalid value of limit')
                    limit = conf.PAGINATION_SIZE
        else:
            limit = conf.PAGINATION_SIZE 
        
        if page_no>0:
            return (page_no-1) * limit
        else:
            return 0
    else:
        return 0
