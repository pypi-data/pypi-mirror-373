'''
Created on 6 Mar 2024

@author: jacklok
'''


from flask import Blueprint, render_template, request, current_app
import logging 
from werkzeug.utils import redirect
from flask.helpers import url_for


presentation_bp = Blueprint('merchant_presentation_bp', __name__,
                     template_folder    = 'templates',
                     static_folder      = '/presentation/static',
                     url_prefix         = '/presentation'
                     )

logger = logging.getLogger('controller')

'''
Blueprint settings here
'''
@presentation_bp.context_processor
def merchant_presentation_bp_inject_settings():
    return dict(
                
                )

@presentation_bp.route('/')
def presentation_bp_index(): 
    return render_template("presentation/presentation_index.html")

@presentation_bp.route('/html')
def presentation_in_html(): 
    return redirect(url_for('static', filename='presentation/pv2024.html'))

@presentation_bp.route('/pdf')
def presentation_in_pdf(): 
    return redirect(url_for('static', filename='presentation/pv2024.pdf'))