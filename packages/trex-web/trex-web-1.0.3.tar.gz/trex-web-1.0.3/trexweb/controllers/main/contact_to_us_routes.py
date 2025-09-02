'''
Created on 15 Feb 2024

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
from trexweb.forms.system_forms import JoinAsPartnerForm, ContactToUsForm
from trexmodel.models.datastore.system_models import JoinAsPartner, ContactToUs
from trexmail.flask_mail import send_email
from trexlib.utils.log_util import get_tracelog
from flask_babel import gettext
from trexweb.libs.http import create_rest_message, StatusCode

contact_to_us_bp = Blueprint('contact_to_us_bp', __name__,
                     template_folder    = 'templates',
                     static_folder      = 'static',
                     url_prefix         = '/contact-to-us'
                     )

logger = logging.getLogger('controller')

'''
Blueprint settings here
'''
@contact_to_us_bp.context_processor
def contact_to_us_bp_inject_settings():
    return dict(
                
                )

@contact_to_us_bp.route('/')
def contact_to_us(): 
    return render_template("main/contact_to_us/contact_to_us.html")

@contact_to_us_bp.route('/', methods=["post"])
def contact_to_us_post(): 
    contact_to_us_data = request.form
    
    logger.info('contact_to_us_data=%s', contact_to_us_data)
    
    contact_to_us_form = ContactToUsForm(contact_to_us_data)
    
    
    try:
        if contact_to_us_form.validate():
            
            verify_token    = contact_to_us_form.verify_token.data
            valid_token     = False
            
            logger.info('verify_token=%s', verify_token)
            
            valid_token= verify_recaptcha_token(verify_token)
            
            logger.info('valid_token=%s', valid_token)
            
            if valid_token:
            
                db_client   = create_db_client(caller_info="contact_to_us_post")
                to_send     = False
                email       = contact_to_us_form.email.data
                mobile_phone = contact_to_us_form.mobile_phone.data
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
                        from_email  = contact_to_us_form.email.data
                        from_name   = contact_to_us_form.name.data
                        try:
                            ContactToUs.create(
                                            company_name        = contact_to_us_form.company_name.data,
                                            name                = from_name,
                                            email               = from_email,
                                            mobile_phone        = contact_to_us_form.mobile_phone.data,
                                            message             = contact_to_us_form.message.data
                                            )
                            
                            email_subject = 'Augmigo Contact To Us: %s from %s' % (contact_to_us_form.email.data, contact_to_us_form.name.data)
                            
                            message = contact_to_us_form.message.data
                            
                            message = 'Purpose:\n%s' % contact_to_us_form.purpose.data
                            message += 'Message:\n%s' % contact_to_us_form.message.data
                            
                            message += '\n\nFrom %s<%s>' % (from_name, from_email, )
                            
                            
                            
                            send_email(
                                       sender       = DEFAULT_SENDER, 
                                       to_address   = [DEFAULT_RECIPIENT_EMAIL], 
                                       subject      = email_subject, 
                                       body         = message,
                                       #bcc_address  = [from_email],
                                       app          = current_app,
                                       )
                            
                            is_sent = True
                        
                        except:
                            logging.error('Failed to create contact to us due to %s', get_tracelog())
                
                if to_send:
                    return create_rest_message(gettext('Thank you, we will contact you shortly'), status_code=StatusCode.OK)
                else:
                    return create_rest_message(status_code=StatusCode.BAD_REQUEST)
                    
            else:
                return create_rest_message('Please fill verify ReCaptcha!', status_code=StatusCode.BAD_REQUEST)
        else:
            error_message = contact_to_us_form.create_rest_return_error_message()
            
            return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    except:
        logging.error('Fail to join as partner due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)
