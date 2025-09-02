'''
Created on 20 Apr 2020

@author: jacklok
'''
import csv, os, json 
from flask import Blueprint, send_file, make_response, render_template
from trexweb.conf import APP_LOGO_PATH, APP_ICO_PATH, APP_LOADING_PATH
from trexweb import conf
import logging, custom

logger = logging.getLogger('root')

base_dir = os.path.abspath(os.path.dirname(custom.__file__))
    
templates_path      = os.path.join(base_dir, "templates")
static_path         = os.path.join(base_dir, "static")

custom_bp = Blueprint('custom_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/custom')


@custom_bp.route('/custom_style.css')
def custom_style(): 
    resp = make_response(render_template('shared/css/custom_style.css'))
    resp.headers['Content-type'] = 'text/css; charset=utf-8'
    return resp


@custom_bp.route('/app-logo.png', methods=['GET'])
def app_logo():
    #logger.debug('---application logo---')
    #logger.debug('APP_LOGO_PATH=%s', APP_LOGO_PATH)
    
    return send_file(static_path+'/'+APP_LOGO_PATH, mimetype='image/png')

@custom_bp.route('/loading.gif', methods=['GET'])
def loading_image():
    #logger.debug('---loading image---')
    #logger.debug('APP_LOADING_PATH=%s', APP_LOADING_PATH)
    
    return send_file(static_path+'/'+APP_LOADING_PATH, mimetype='image/gif')

@custom_bp.route('/app.ico', methods=['GET'])
def app_ico():
    #logger.debug('---application logo---')
    #logger.debug('APP_LOGO_PATH=%s', APP_LOGO_PATH)
    
    return send_file(static_path+'/'+APP_ICO_PATH, mimetype='image/x-icon')

 



