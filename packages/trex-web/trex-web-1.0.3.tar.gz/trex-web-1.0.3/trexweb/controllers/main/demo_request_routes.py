'''
Created on 14 Feb 2024

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


demo_request_bp = Blueprint('demo_request_bp', __name__,
                     template_folder    = 'templates',
                     static_folder      = 'static',
                     url_prefix         = '/demo-request'
                     )

logger = logging.getLogger('controller')

'''
Blueprint settings here
'''
@demo_request_bp.context_processor
def demo_request_bp_inject_settings():
    return dict(
                
                )

@demo_request_bp.route('/')
def demo_request(): 
    return render_template("main/demo_request/demo_request.html")

@demo_request_bp.route('/', methods=["post"])
def demo_request_post(): 
    demo_request_data = request.form
    
    logger.info('demo_request_data=%s', demo_request_data)
    
    demo_request_form = DemoRequestForm(demo_request_data)
    
    
    try:
        if demo_request_form.validate():
            
            verify_token    = demo_request_form.verify_token.data
            valid_token     = False
            
            logger.info('verify_token=%s', verify_token)
            
            valid_token= verify_recaptcha_token(verify_token)
            
            logger.info('valid_token=%s', valid_token)
            
            if valid_token:
            
                db_client   = create_db_client(caller_info="demo_request_post")
                to_send     = False
                email       = demo_request_form.email.data
                mobile_phone = demo_request_form.mobile_phone.data
                logger.info('email=%s', email)
                logger.info('mobile_phone=%s', mobile_phone)
                
                valid_email = False
                if is_not_empty(email):
                    valid_email = is_valid_email(email)
                
                logger.info('valid_email=%s', valid_email)
                
                if valid_email:
                    to_send = True
                
                if to_send:
                    with db_client.context():
                        from_email  = demo_request_form.email.data
                        from_name   = demo_request_form.name.data
                        try:
                            DemoRequest.create(
                                            company_name        = demo_request_form.company_name.data,
                                            name                = from_name,
                                            email               = from_email,
                                            mobile_phone        = demo_request_form.mobile_phone.data,
                                            message             = demo_request_form.message.data
                                            )
                            
                            email_subject = 'Augmigo Demo Request: %s from %s' % (demo_request_form.email.data, demo_request_form.name.data)
                            
                            message = 'Purpose:\n%s' % demo_request_form.purpose.data
                            message += '\n\nMessage:\n%s' % demo_request_form.message.data
                            
                            message += '\n\nFrom %s <%s>' % (from_name, from_email, )
                            
                            
                            
                            send_email(
                                       sender       = DEFAULT_SENDER, 
                                       to_address   = [DEFAULT_RECIPIENT_EMAIL], 
                                       subject      = email_subject, 
                                       body         = message,
                                       app          = current_app,
                                       )
                            
                            
                        
                        except:
                            logging.error('Failed to create demo request due to %s', get_tracelog())
                
                if to_send:
                    return create_rest_message(gettext('Thank you, we will contact you shortly'), status_code=StatusCode.OK)
                else:
                    return create_rest_message(status_code=StatusCode.BAD_REQUEST)
                    
            else:
                return create_rest_message('Please fill verify ReCaptcha!', status_code=StatusCode.BAD_REQUEST)
        else:
            error_message = demo_request_form.create_rest_return_error_message()
            
            return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    except:
        logging.error('Fail to join as partner due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)