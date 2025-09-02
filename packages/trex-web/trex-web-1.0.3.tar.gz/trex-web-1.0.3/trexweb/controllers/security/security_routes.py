'''
Created on 15 Apr 2020

@author: jacklok
'''

from flask import Blueprint, render_template, request, current_app, redirect, url_for, session
from trexlib.utils.log_util import get_tracelog
from flask_login import login_user, logout_user, current_user
from trexweb.libs.oauth_signin import OAuthSignIn
from trexmodel.models.datastore.user_models import User 
from trexmodel.utils.model.model_util import create_db_client
from datetime import datetime
from trexweb.libs.http import StatusCode, create_rest_message
from trexweb.forms.user_forms import RegistrationForm, SignInForm
from trexlib.utils.security_util import hash_password
import logging

security_bp = Blueprint('security_bp', __name__,
                     template_folder    = 'templates',
                     static_folder      = 'static',
                     url_prefix         = '/sec'
                     )




@security_bp.route('/signin', methods=['GET'])
def signin_page():
    
    logged_in_user_id = session.get('logged_in_user_id')
    
    logging.debug('logged_in_user_id=%s', logged_in_user_id)
    
    if logged_in_user_id:
        return redirect(url_for('main_bp.dashboard_page'))
    else:
        return render_template("security/signin_page.html", navigation_type='signin')
    
@security_bp.route('/signin-content', methods=['GET'])
def signin_content():
    
    logged_in_user_id = session.get('logged_in_user_id')
    
    logging.debug('logged_in_user_id=%s', logged_in_user_id)
    
    if logged_in_user_id:
        return redirect(url_for('main_bp.dashboard_page'))
    else:
        return render_template("security/signin_lazy_load_page.html")    

@security_bp.route('/signin', methods=['post'])
def signin():
    logging.debug('--- submit signin data ---')
    signin_data = request.form
    
    logging.debug('signin_data=%s', signin_data)
    
    signin_form = SignInForm(signin_data)
    
    try:
        if signin_form.validate():
        
            
            db_client = create_db_client(info=current_app.config['database_config'], caller_info="signin")
            with db_client.context():
                email = signin_form.signin_email.data
                checked_user_by_email = User.get_by_email(email)
                
                logging.debug('checked_user_by_email=%s', checked_user_by_email)
                
                invalid_signin_message = "Invalid signin email or password"
                
                if checked_user_by_email is None:
                    return create_rest_message(invalid_signin_message, status_code=StatusCode.UNAUTHORIZED)
                else:
                    sigin_password = signin_form.password.data
                    
                    hashed_signin_password = hash_password(checked_user_by_email.user_id, sigin_password)
                    
                    logging.debug('sigin_password=%s', sigin_password)
                    logging.debug('hashed_signin_password=%s', hashed_signin_password)
                    logging.debug('checked_user_by_email.password=%s', checked_user_by_email.password)
                    is_signin_password_valid = hashed_signin_password == checked_user_by_email.password
                    
                    logging.debug('is_signin_password_valid=%s', is_signin_password_valid)
                    
                    if is_signin_password_valid:
                    
                        login_user(checked_user_by_email, True)
                        #session['logged_in_user']       = checked_user_by_email
                        session['logged_in_user_id']        = checked_user_by_email.user_id
                        session['was_once_logged_in']       = True
                        session['logged_in_user_activated'] = checked_user_by_email.active
                        return create_rest_message(status_code=StatusCode.OK)
                    else:
                        return create_rest_message(invalid_signin_message, status_code=StatusCode.UNAUTHORIZED)
                    
            
            return create_rest_message(status_code=StatusCode.BAD_REQUEST)
        else:
            logging.warn('Invalid signin request')
            error_message = signin_form.create_rest_return_error_message()
            
            return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    except:
        logging.error('Fail to signin in account due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)
    
    return create_rest_message(status_code=StatusCode.BAD_REQUEST)


@security_bp.route('/signup', methods=['GET'])
def signup_page():
    logging.debug('--- show signup page ---')
    #countries_list = get_country_list()
    
    return render_template("security/signup_page.html", navigation_type='signin')



@security_bp.route('/signup', methods=['post'])
def signup():
    logging.debug('--- submit signup data ---')
    signup_data = request.form
    
    logging.debug('signup_data=%s', signup_data)
    
    signup_form = RegistrationForm(signup_data)
    
    
    try:
        if signup_form.validate():
        
            
            db_client = create_db_client(info=current_app.config['database_config'], caller_info="signup")
            with db_client.context():
                email = signup_form.email.data
                checked_user_by_email = User.get_by_email(email)
                
                logging.debug('checked_user_by_email=%s', checked_user_by_email)
                if checked_user_by_email is None:
                
                    try:
                        new_signup_user = User.create(
                                                    name        = signup_form.fullname.data, 
                                                    email       = email, 
                                                    city        = signup_form.city.data, 
                                                    country     = signup_form.country.data,
                                                    password    = signup_form.password.data,
                                                    gender      = signup_form.gender.data,
                                                    )
                        
                        login_user(new_signup_user, True)
                        session['logged_in_user_id']    = new_signup_user.user_id
                        session['was_once_logged_in']   = True
                        
                        return create_rest_message('User account have been registered successfully', status_code=StatusCode.OK)
                    
                    except:
                        logging.error('Failed to create user due to %s', get_tracelog())
                        return create_rest_message(status_code=StatusCode.BAD_REQUEST)
                else:
                    return create_rest_message('User email have been used, please use other email address', status_code=StatusCode.BAD_REQUEST)
            
            return create_rest_message(status_code=StatusCode.BAD_REQUEST)
        else:
            error_message = signup_form.create_rest_return_error_message()
            
            return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    except:
        logging.error('Fail to register account due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)
        

@security_bp.route('/signout', methods=['GET'])
def signout():
    
    logout_user()
    if session.get('was_once_logged_in') and session.get('logged_in_user_id'):
        # prevent flashing automatically logged out message
        del session['was_once_logged_in']
        del session['logged_in_user_id']
    
    return redirect(url_for('main_bp.home_page'))
    

@security_bp.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        #return redirect('/home')
        session['logged_in_user_id'] = current_user.user_id
        return redirect(url_for('main_bp.dashboard_page'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()

@security_bp.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect('/home')
    oauth                       = OAuthSignIn.get_provider(provider)
    social_id, username, email  = oauth.callback()
    if social_id is None:
        #flash('Authentication failed.')
        return redirect('/home')
    
    db_client = create_db_client(info=current_app.config['database_config'], caller_info="oauth_callback")

    with db_client.context():
        user = User.get_by_social_id(social_id)
        if not user:
            user = User.create(social_id=social_id, name=username, email=email, provider=provider)
        else:
            user.last_login_datetime = datetime.now()
            user.name = username
            user.email = email
            user.put()
        
        login_user(user, True)
        session['was_once_logged_in'] = True
    
    logging.debug('Going redirect to dashboard')
            
    return redirect(url_for('main_bp.dashboard_page'))
