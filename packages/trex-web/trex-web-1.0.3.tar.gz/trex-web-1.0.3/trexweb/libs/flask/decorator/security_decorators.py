'''
Created on 6 May 2020

@author: jacklok
'''
from functools import wraps
from flask import session, abort, request, redirect, url_for, session, current_app
from trexweb.libs.flask.exceptions import RESTUnauthorized, Unauthorized
import logging
from trexmodel.utils.model.model_util import create_db_client
from trexmodel.models.datastore.user_models import User 

logger = logging.getLogger('decorator');

def superuser(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logged_in_user = session['logged_in_user']
        
        logging.debug('logged_in_user=%s', logged_in_user)
        if logged_in_user:
            if logged_in_user.is_super_user:
                return f(*args, **kwargs)
        
        abort(404)

    return decorated_function


def authorized_role(authorized_roles_list):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            logged_in_user = session['logged_in_user']
        
            logging.debug('logged_in_user=%s', logged_in_user)
            
            if logged_in_user:
                found_authorized_role = False
                for role in logged_in_user.roles:
                    if role in authorized_roles_list:
                        found_authorized_role = True
                        break
                if found_authorized_role:
                    return f(*args, **kwargs)
                        
            abort(403)
            
        return wrapper
    return decorator

def ignore_load_user(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        request_url = request.url
        logger.debug('request_url=%s', request_url)
        if not session.get('logged_in_user_id'):
            #return redirect(url_for(conf.LOGIN_URL_FOR_PATH, next=request.url))
            
            #return redirect(url_for(conf.LOGIN_CONTENT_URL_FOR_PATH, next=request_url))
            abort(401)
            #pass
        return f(*args, **kwargs)
    return decorated_function

def account_activated(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        
        logger.debug('---account_activated decorator---')
        
        if session.get('logged_in_user_id'):
            logger.debug('logged in user found')
            logged_in_user_id = session.get('logged_in_user_id')
            
            db_client = create_db_client(info=current_app.config['database_config'], caller_info="account_activated:load_user")
            with db_client.context():   
                logged_in_user =  User.get_by_user_id(logged_in_user_id)
            
            if not logged_in_user.active:
                abort(403)
            
        else:
            logger.debug('logged in user not found')
            abort(401)
        return f(*args, **kwargs)
    return decorated_function


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        
        logger.debug('---login_required decorator---')
        
        request_url = request.url
        logger.debug('request_url=%s', request_url)
        if not session.get('logged_in_user_id'):
            #return redirect(url_for(conf.LOGIN_URL_FOR_PATH, next=request.url))
            
            #return redirect(url_for(conf.LOGIN_CONTENT_URL_FOR_PATH, next=request_url))
            abort(401)
            #pass
        return f(*args, **kwargs)
    return decorated_function

def login_required_rest(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logger.debug('---login_required_rest decorator---')
        
        if not session.get('logged_in_user_id'):
            raise RESTUnauthorized()
            #abort(401)
        return f(*args, **kwargs)
    return decorated_function
