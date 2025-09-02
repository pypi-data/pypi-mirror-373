'''
Created on 21 Feb 2024

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


blogs_bp = Blueprint('blogs_bp', __name__,
                     template_folder    = 'templates',
                     static_folder      = 'static',
                     url_prefix         = '/blogs'
                     )

logger = logging.getLogger('controller')

'''
Blueprint settings here
'''
@blogs_bp.context_processor
def blogs_bp_inject_settings():
    return dict(
                
                )

@blogs_bp.route('/')
def blogs_index(): 
    return render_template("blogs/blogs_index.html")

@blogs_bp.route('/latest-loyalty-programs')
def latest_customer_loyalty_programs(): 
    return render_template("blogs/latest-loyalty-programs/latest_loyalty_programs.html")

@blogs_bp.route('/know-your-customer')
def know_your_customer(): 
    return render_template("blogs/know-your-customer/know_your_customer.html")

@blogs_bp.route('/revenue-growth-thru-effective-membership-program')
def revenue_growth_thru_effective_membership_program():
    return render_template("blogs/revenue-growth/revenue_growth_thru_membership_program.html")
