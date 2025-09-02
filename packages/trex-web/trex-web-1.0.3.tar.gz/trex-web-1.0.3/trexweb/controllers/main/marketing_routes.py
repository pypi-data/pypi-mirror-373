'''
Created on 26 Dec 2024

@author: jacklok
'''

from flask import Blueprint, render_template, request, current_app
import logging
from trexweb.conf import is_local_development, SUPPORT_LANGUAGES
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
from flask.helpers import url_for
from werkzeug.utils import redirect


marketing_bp = Blueprint('marketing_bp', __name__,
                     template_folder    = 'templates',
                     static_folder      = 'static',
                     url_prefix         = '/marketing'
                     )

logger = logging.getLogger('controller')

'''
Blueprint settings here
'''
@marketing_bp.context_processor
def marketing_bp_inject_settings():
    return dict(
                
                )

@marketing_bp.route('/')
def marketing_index(): 
    supported_languages = SUPPORT_LANGUAGES
    lang = request.accept_languages.best_match(supported_languages)
    logger.info('preferred supported language=%s', lang)
    if lang:
        return redirect(url_for('marketing_bp.know_your_customer_%s' % lang))
    else:
        return redirect(url_for('marketing_bp.know_your_customer_en'))
    #return render_template("marketing/marketing_index.html")

@marketing_bp.route('/know-your-customers')
@marketing_bp.route('/know-your-customers/')
@marketing_bp.route('/know-your-customers/en')
def know_your_customer_en(): 
    return render_template(
                "marketing/know-your-customer/know_your_customers_en.html",
                content_image_url = url_for('static', filename='app/assets/img/marketing/know-your-customer-en.png')
                
                )
    
@marketing_bp.route('/know-your-customers/zh')
def know_your_customer_zh(): 
    return render_template(
                "marketing/know-your-customer/know_your_customers_zh.html",
                content_image_url = url_for('static', filename='app/assets/img/marketing/know-your-customer-zh.png')
                
                )    
