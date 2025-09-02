'''
Created on 30 Nov 2020

@author: jacklok
'''

from flask import Blueprint, render_template, make_response
import logging


custom_bp = Blueprint('custom_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/custom')

@custom_bp.route('/custom_style.css')
def custom_style(): 
    resp = make_response(render_template('shared/css/custom_style.css'))
    resp.headers['Content-type'] = 'text/css; charset=utf-8'
    return resp


