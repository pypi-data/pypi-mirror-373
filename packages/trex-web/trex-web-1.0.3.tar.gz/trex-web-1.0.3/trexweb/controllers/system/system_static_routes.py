'''
Created on 1 Jul 2020

@author: jacklok
'''

import csv, os, json
from flask import Blueprint, render_template, request, current_app
from trexlib.utils.log_util import get_tracelog
from trexweb.utils.common.http_response_util import MINE_TYPE_JAVASCRIPT
import logging

system_static_bp = Blueprint('system_static_bp', __name__,
                     template_folder    = 'templates',
                     static_folder      = 'static',
                     url_prefix         = '/system/static'
                     )


COUNTRY_CODE_FILEPATH = os.path.abspath(os.path.dirname(__file__)) + '/data/countries.csv'  


@system_static_bp.after_request
def set_system_response_headers(response):
    request_url = request.url
    logging.debug('request_url=%s', request_url)
    
    if request_url.endswith('.js'):
        response.headers['Content-Type'] = MINE_TYPE_JAVASCRIPT
    
    response.charset= 'utf-8'    
    
    logging.debug('---set_system_response_headers---')
    
    return response






