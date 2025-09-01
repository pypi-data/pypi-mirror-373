'''
Created on 19 May 2020

@author: jacklok
'''
 
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from trexconf import conf
import pytz


def parse_generic_date(date_str):
    # List of possible formats to try (in order of priority)
    formats = ["%d-%m-%Y", "%d/%m/%Y"]
    
    for fmt in formats:
        try:
            # Attempt to parse with current format
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue  # Try next format if parsing fails
    
    # Return None if none of the formats work
    return None

def parse_date(date_value, date_separator='/', full_year_date_format='%d/%m/%Y', short_year_date_format='%d/%m/%y'):
    if date_value is not None:
        #logging.info('parse_date: date_value=%s', date_value)
        _d_array = date_value.split(date_separator)
        if len(_d_array)==3:
            if len(_d_array[2])==4:
                _datetime = datetime.strptime(date_value, full_year_date_format)
                return _datetime.date()
            elif len(_d_array[2])==2:
                _datetime = datetime.strptime(date_value, short_year_date_format)
                return _datetime.date()
    return None

def parse_datetime(date_value, parse_format='%d-%m-%Y %H:%M:%S'):
    if date_value:
        return datetime.strptime(date_value, parse_format)
    return None

def convert_date_to_datetime(date_value):
    return datetime.combine(date_value, datetime.min.time())

def get_gmt_datetime_from_gmt(gmt):
    now = datetime.now()
    return now + timedelta(hours=gmt)

def convert_datetime_from_gmt_hours(gmt_hours, datetime_value):
    return datetime_value + timedelta(hours=gmt_hours)


def decrease_date(origin_date, year=0, month=0, day=0, hour=0, minute=0, second=0, millisecond=0):
    if year or month or day or hour or minute or second or millisecond:
        origin_date = origin_date - relativedelta(years=year, months=month, days=day, hours=hour,
                                                  minutes=minute, seconds=second)

        if millisecond:
            origin_date = origin_date - timedelta(milliseconds=millisecond)

        return origin_date
    else:
        return origin_date

def increase_date(origin_date, year=0, month=0, day=0, hour=0, minute=0, second=0, millisecond=0):
    if year or month or day or hour or minute or second:
        

        #logging.info('increase_date b4 increase: origin_date=%s', origin_date)
        origin_date = origin_date + relativedelta(years=year, months=month, days=day, hours=hour,
                                                  minutes=minute, seconds=second)

        if millisecond:
            origin_date = origin_date + timedelta(milliseconds=millisecond)

        #logging.info('increase_date after increased: origin_date=%s', origin_date)

        return origin_date
    else:
        return origin_date
    
def last_day_of_month(date):
    if date.month == 12:
        return date.replace(day=31)
    return date.replace(month=date.month+1, day=1) - timedelta(days=1)

def to_day_of_year(datetime_input):
    return datetime_input.timetuple().tm_yday

def from_utc_datetime_to_local_datetime(datetime_value, country_code=conf.DEFAULT_COUNTRY_CODE, datetime_format=None):
    
    if datetime_format is None:
        datetime_format = '%d/%m/%Y %H:%M:%S'
        
    if isinstance(datetime_value, str):
        datetime_value = datetime.strptime(datetime_value, datetime_format)
        
    utc_datetime = datetime(datetime_value.year, 
                            datetime_value.month, 
                            datetime_value.day, 
                            datetime_value.hour, 
                            datetime_value.minute, 
                            datetime_value.second, 
                            tzinfo=pytz.utc)
    
    country_code        = country_code.upper()
    country_timezones   = pytz.country_timezones[country_code]
    country_timezone    = pytz.timezone(country_timezones[0])
    
    local_datetime = utc_datetime.astimezone(country_timezone)
    
    return local_datetime
    
def get_next_midnight_datetime():
    next_day_datetime = datetime.utcnow() + timedelta(days=1)
    next_midnight = next_day_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
    return next_midnight

def date_str_to_bigquery_qualified_datetime_str(datetime_in_str, date_str_format='%Y%m%d'):
    datetime_value    = datetime.strptime(datetime_in_str, date_str_format)
    return datetime.strftime(datetime_value, '%Y-%m-%d %H:%M:%S')

def date_to_bigquery_qualified_datetime_str(datetime_value):
    return datetime.strftime(datetime_value, '%Y-%m-%d %H:%M:%S')


