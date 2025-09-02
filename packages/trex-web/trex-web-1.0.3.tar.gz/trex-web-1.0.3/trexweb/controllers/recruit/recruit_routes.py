'''
Created on 6 Mar 2024

@author: jacklok
'''


from flask import Blueprint, render_template, request, current_app
import logging
from trexweb.conf import is_local_development
from trexweb.controllers.system.system_routes import verify_recaptcha_token
from trexmodel.utils.model.model_util import create_db_client
from trexlib.utils.string_util import is_not_empty, boolify
from trexmail.email_helper import is_valid_email 
from trexmail.conf import DEFAULT_SENDER, DEFAULT_RECIPIENT_EMAIL
from trexweb.forms.system_forms import DemoRequestForm
from trexmodel.models.datastore.system_models import DemoRequest
from trexmail.flask_mail import send_email
from trexlib.utils.log_util import get_tracelog
from flask_babel import gettext
from trexweb.libs.http import create_rest_message, StatusCode
from werkzeug.utils import redirect
from flask.helpers import url_for
from trexweb.forms.recruit_forms import CoFounderForm
from trexmodel.models.datastore.recruit_models import CoFounderRecruit


recruit_bp = Blueprint('recruit_bp', __name__,
                             template_folder    = 'templates',
                             static_folder      = '/recruit',
                             url_prefix         = '/recruit'
                     )

logger = logging.getLogger('controller')

'''
Blueprint settings here
'''
@recruit_bp.context_processor
def core_founder_recruit_bp_inject_settings():
    return dict(
                
                )

@recruit_bp.route('/co-founder')
def co_founder_recruit(): 
    return render_template("recruit/co_founder/co_founder_recruit.html")

@recruit_bp.route('/thank-you')
def thank_you_for_submission(): 
    return render_template("recruit/thank_you_for_submission_page.html")



@recruit_bp.route('/co-founder', methods=["post"])
def co_founder_recruit_post(): 
    recruit_data = request.form

    logger.info('recruit_data=%s', recruit_data)
    
    recruit_form = CoFounderForm(recruit_data)
    
    
    try:
        if recruit_form.validate():
            
            verify_token    = recruit_form.verify_token.data
            valid_token     = False
            
            logger.info('verify_token=%s', verify_token)
            
            valid_token= verify_recaptcha_token(verify_token)
            
            logger.info('valid_token=%s', valid_token)
            
            if valid_token:
            
                db_client       = create_db_client(caller_info="co_founder_recruit_post")
                to_send         = False
                email           = recruit_form.email.data
                mobile_phone    = recruit_form.mobile_phone.data
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
                        email                   = recruit_form.email.data
                        name                    = recruit_form.name.data
                        mobile_phone            = recruit_form.mobile_phone.data
                        address                 = recruit_form.address.data
                        involved_in_founding    = boolify(recruit_form.involved_in_founding.data)
                        founding_details        = recruit_form.founding_details.data
                        employment_time         = recruit_form.employment_time.data
                        skill                   = recruit_form.skill.data
                        other_skill             = recruit_form.other_skill.data
                        linkedin_profile        = recruit_form.linkedin_profile.data
                        
                        try:
                            
                            CoFounderRecruit.create(name                = name, 
                                                    mobile_phone        = mobile_phone, 
                                                    email               = email, 
                                                    address             = address, 
                                                    involved_in_founding= involved_in_founding, 
                                                    founding_details    = founding_details, 
                                                    employment_time     = employment_time, 
                                                    skill               = skill, 
                                                    other_skill         = other_skill,
                                                    linkedin_profile    = linkedin_profile
                                                    )
                            
                            
                            email_subject = 'Augmigo Co-Founder Recruit: %s from %s' % (email, name)
                            
                            message = '\n\nName:\n%s' % name
                            message += '\n\nEmail:\n%s' % email
                            message += '\n\nMobile:\n%s' % mobile_phone
                            message += '\n\nAddress:\n%s' % address
                            message += '\n\n' 
                            
                            message += '\n\nFounding Before:\n%s' % involved_in_founding
                            message += '\n\nFounding Details:\n%s' % founding_details
                            message += '\n\nEmployment time:\n%s' % employment_time
                            message += '\n\nSkill:\n%s' % skill
                            message += '\n\nOther Skill:\n%s' % other_skill
                            message += '\n\nLinkedIn Profile:\n%s' % linkedin_profile
                            
                            logger.debug('message=%s', message)
                            
                            
                            send_email(
                                       sender       = DEFAULT_SENDER, 
                                       to_address   = [DEFAULT_RECIPIENT_EMAIL], 
                                       subject      = email_subject, 
                                       body         = message,
                                       app          = current_app,
                                       )
                            
                            #is_sent = True
                        
                        except:
                            logging.error('Failed to create contact to us due to %s', get_tracelog())
                
                if to_send:
                    return create_rest_message(gettext('Thank you, we will contact you shortly'), 
                                               status_code=StatusCode.OK,
                                               next_page = url_for('recruit_bp.thank_you_for_submission')
                                               )
                else:
                    return create_rest_message(status_code=StatusCode.BAD_REQUEST)
                    
            else:
                return create_rest_message('Please fill verify ReCaptcha!', status_code=StatusCode.BAD_REQUEST)
        else:
            error_message = recruit_form.create_rest_return_error_message()
            logger.error('error_message=%s', error_message)
            return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    except:
        logging.error('Fail to join as partner due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)