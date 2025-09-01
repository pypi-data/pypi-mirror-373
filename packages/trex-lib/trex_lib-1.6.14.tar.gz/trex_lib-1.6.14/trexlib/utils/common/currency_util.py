'''
Created on 4 Mar 2021

@author: jacklok
'''
from trexlib.utils.common.format_util import format_with_commas
import logging
from trexlib.utils.string_util import is_not_empty

logger = logging.getLogger('utils')

def format_currency(value_2_format=0, currency_label='$', floating_point=2, decimal_separator='.', thousand_separator=',', 
                    show_thousand_separator=True, show_currency_label=False):
    pattern             = u'%.' + str(floating_point)+'f'

    if not show_thousand_separator:
        thousand_separator = ''

    if show_currency_label:
        return '%s %s' % (currency_label, format_with_commas(pattern, value_2_format, thousand_separator, decimal_separator))
    else:
        return format_with_commas(pattern, value_2_format, thousand_separator, decimal_separator)
    
    
def currency_amount_based_on_currency(currency=None, value_2_format=.0):
    if is_not_empty(value_2_format):
        logger.debug('value_2_format is not empty')
        if isinstance(value_2_format, float):
            if currency is not None:
                floating_no         = currency.get('floating_point')
                pattern             = u'%.' + str(floating_no)+'f'

                logger.debug('pattern=%s', pattern)

                value_2_format    = pattern % value_2_format

                return float(value_2_format)
            else:
                raise Exception('Currency is required')
        else:
            return value_2_format
    else:
        logger.warn('value_2_format is empty')
        return float(0)    

    
