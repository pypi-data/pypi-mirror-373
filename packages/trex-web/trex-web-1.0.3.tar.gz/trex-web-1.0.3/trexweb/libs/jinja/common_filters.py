'''
Created on 19 May 2020

@author: jacklok
'''
import conf, logging
from utils.common.date_util import increase_date
from utils.common.date_util import parse_date, parse_datetime

def gmt_datetime(datetime_value, gmt=conf.DEFAULT_GMT):
    if datetime_value:
        new_gmt_datetime = increase_date(datetime_value, hour=gmt)

        return new_gmt_datetime
        
    else:
        return ''

def pretty_datetime_filter(context, datetime_str):
    logging.debug('pretty_datetime_filter: datetime_str=%s', datetime_str)
     
    if datetime_str:
        datetime_value = parse_datetime(datetime_str, conf.DEFAULT_DATETIME_FORMAT)
        if datetime_value:
            return datetime_value.strftime('%d %b %Y %H:%M:%S')
    return ''

def pretty_date_filter(context, date_str):
    
    logging.debug('pretty_date_filter: date_str=%s', date_str)
    if date_str:
        datetime_value = parse_datetime(date_str, conf.DEFAULT_DATETIME_FORMAT)
        if datetime_value:
            return datetime_value.strftime('%d %b %Y')
    return ''
