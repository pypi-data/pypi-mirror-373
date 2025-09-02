'''
Created on 6 Mar 2024

@author: jacklok
'''


from flask import Blueprint, render_template, request, current_app
import logging
from trexweb.conf import is_local_development
from trexweb.controllers.system.system_routes import verify_recaptcha_token
from trexmodel.utils.model.model_util import create_db_client
from trexlib.utils.string_util import is_not_empty
from trexmail.email_helper import is_valid_email 
from trexmail.conf import DEFAULT_SENDER, DEFAULT_RECIPIENT_EMAIL
from trexweb.forms.system_forms import DemoRequestForm
from trexmodel.models.datastore.system_models import DemoRequest
from trexmail.flask_mail import send_email
from trexlib.utils.log_util import get_tracelog
from flask_babel import gettext
from trexweb.libs.http import create_rest_message, StatusCode


merchant_demo_tour_bp = Blueprint('merchant_demo_tour_bp', __name__,
                     template_folder    = 'templates',
                     static_folder      = 'static',
                     url_prefix         = '/demo/merchant'
                     )

logger = logging.getLogger('controller')

'''
Blueprint settings here
'''
@merchant_demo_tour_bp.context_processor
def merchant_demo_tour_bp_inject_settings():
    return dict(
                
                )

@merchant_demo_tour_bp.route('/')
def merchant_demo_tour_bp_index(): 
    return render_template("demo/merchant/merchant_demo_tour_index.html")

