'''
Created on 14 Aug 2025

@author: jacklok
'''

from flask import Blueprint, render_template, request, current_app
import logging 
from werkzeug.utils import redirect
from flask.helpers import url_for


merchant_customization_bp = Blueprint('merchant_customization_bp', __name__,
                     template_folder    = 'templates',
                     static_folder      = '/merchant/custom/static',
                     url_prefix         = '/merchant/custom'
                     )

logger = logging.getLogger('controller')

@merchant_customization_bp.route('/vietly/privacy-policy')
def presentation_bp_index(): 
    brand_name          = 'Vietly'
    effective_date      = '14 Aug 2025'
    last_updated_date   = '14 Aug 2025'
    page_email          = 'support [at] augmigo [dot] com'
    obfuscated_email    = '\u0073\u0075\u0070\u0070\u006f\u0072\u0074\u0040\u0061\u0075\u0067\u006d\u0069\u0067\u006f\u002e\u0063\u006f\u006d'
    return render_template(
                "merchants/sample/merchant_sample_privacy_policy.html",
                brand_name          = brand_name,
                effective_date      = effective_date,
                last_updated_date   = last_updated_date,
                page_email          = page_email,
                obfuscated_email    = obfuscated_email,
                )

