__author__ = 'jacklok'
 
def format_float(float_value, decimal_number=2):
    if float_value is not None:
        format_pattern = '{0:.%df}'%decimal_number
        return float(format_pattern.format(float_value))
    else:
        raise Exception('float value to be formatted is required')