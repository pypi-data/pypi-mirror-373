import re, logging

__test__ = {}

re_digits_nondigits = re.compile(r'\d+|\D+')

__test__['re_digits_nondigits'] = r"""

    >>> re_digits_nondigits.findall('$1234.1234')
    ['$', '1234', '.', '1234']
    >>> re_digits_nondigits.findall('1234')
    ['1234']
    >>> re_digits_nondigits.findall('')
    []
    
"""

def format_with_commas(format, value, thousand_separator=',', decimal_separator='.'):
    """

    >>> format_with_commas('%.4f', .1234)
    '0.1234'
    >>> format_with_commas('%i', 100)
    '100'
    >>> format_with_commas('%.4f', 234.5678)
    '234.5678'
    >>> format_with_commas('$%.4f', 234.5678)
    '$234.5678'
    >>> format_with_commas('%i', 1000)
    '1,000'
    >>> format_with_commas('%.4f', 1234.5678)
    '1,234.5678'
    >>> format_with_commas('$%.4f', 1234.5678)
    '$1,234.5678'
    >>> format_with_commas('%i', 1000000)
    '1,000,000'
    >>> format_with_commas('%.4f', 1234567.5678)
    '1,234,567.5678'
    >>> format_with_commas('$%.4f', 1234567.5678)
    '$1,234,567.5678'
    >>> format_with_commas('%i', -100)
    '-100'
    >>> format_with_commas('%.4f', -234.5678)
    '-234.5678'
    >>> format_with_commas('$%.4f', -234.5678)
    '$-234.5678'
    >>> format_with_commas('%i', -1000)
    '-1,000'
    >>> format_with_commas('%.4f', -1234.5678)
    '-1,234.5678'
    >>> format_with_commas('$%.4f', -1234.5678)
    '$-1,234.5678'
    >>> format_with_commas('%i', -1000000)
    '-1,000,000'
    >>> format_with_commas('%.4f', -1234567.5678)
    '-1,234,567.5678'
    >>> format_with_commas('$%.4f', -1234567.5678)
    '$-1,234,567.5678'
    
    """
    #logging.debug('format_with_commas: value=%s',value)
    #logging.debug('format_with_commas: format=%s',format)

    if value is None or value=='':
        float_value = float(0)
    else:
        try:
            float_value = float(value)
        except ValueError:
            logging.warn('not a float value, value=%s', value)
            return value

    parts                   = re_digits_nondigits.findall(format % (float_value))
    format_commas_already   = False
    decimal_separator       = decimal_separator.strip()
    thousand_separator      = thousand_separator.strip()

    #logging.debug('format_with_commas: parts=%s',parts)
    #logging.debug('format_with_commas: decimal_separator=%s',decimal_separator)
    #logging.debug('format_with_commas: thousand_separator=%s',thousand_separator)

    for i in range(len(parts)):
        s = parts[i]
        #logging.debug('format_with_commas: s=%s, s.isdigit()=%s', s, s.isdigit())
        if s.isdigit() and format_commas_already==False :
            parts[i] = _commafy(s, thousand_separator)
            #logging.debug('format_with_commas: parts[i]=%s', parts[i])
            format_commas_already = True
        elif str(parts[i])=='.' and decimal_separator!='.':
            parts[i]=decimal_separator
            
    formatted_value = ''.join(parts)

    #logging.debug('format_with_commas: formatted_value=%s', formatted_value)

    return formatted_value
    
def _commafy(s, thousand_separator=','):

    r = []
    for i, c in enumerate(reversed(s)):
        if i and (not (i % 3)):
            r.insert(0, thousand_separator)
        r.insert(0, c)
    return ''.join(r)

def unittest():
    
    assert '0.1234' == format_with_commas('%.4f', .1234)
    assert '100' == format_with_commas('%i', 100)
    assert '234.5678' == format_with_commas('%.4f', 234.5678)
    assert '$234.5678' == format_with_commas('$%.4f', 234.5678)
    assert 'RM 234.57' == format_with_commas('RM %.2f', 234.5678)
    assert '-100' == format_with_commas('%i', -100)
    assert '1,234,567.5678' == format_with_commas('%.4f', 1234567.5678)
    assert '$-234.5678' == format_with_commas('$%.4f', -234.5678)
    assert '-1,234,567.5678' == format_with_commas('%.4f', -1234567.5678)
    assert 'Euro 1.234.567,57' == format_with_commas('Euro %.2f', 1234567.5678, '.', ',')
    assert 'Euro 1234567,57' == format_with_commas('Euro %.2f', 1234567.5678, '', ',')
    assert '1,001' == format_with_commas('%.0f', 1000.57)
    assert '1,000.6' == format_with_commas('%.1f', 1000.57)
    

if __name__ == "__main__":
    unittest()
    print("Unit Tests OK")