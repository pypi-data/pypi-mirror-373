'''
Created on 10 Jun 2020

@author: jacklok
'''
import os, json
from flask import Blueprint, render_template, request, current_app, jsonify
from trexlib.utils.log_util import get_tracelog
from trexlib.utils.string_util import is_not_empty
import logging
from flask.helpers import url_for
from trexmodel.utils.model.model_util import create_db_client
from trexmodel.models.datastore.merchant_models import MerchantSentEmail


mailjet_service_bp = Blueprint('mailjet_service_bp', __name__,
                                     template_folder    = 'templates',
                                     static_folder      = 'static',
                                     url_prefix         = '/system/mailjet-service'
                                     )


logger = logging.getLogger('application:mail_service_routes')

@mailjet_service_bp.after_request
def set_system_response_headers(response):
    return response

@mailjet_service_bp.route('/mail-sent-status', methods=['PUT','POST'])
def update_mail_sent_status():
    json_params  = request.json
    
    logger.debug('json_params=%s', json_params)
    
    if json_params:
        db_client = create_db_client(info=current_app.config['database_config'], caller_info="update_mail_sent_status")
        
        with db_client.context():
            if isinstance(json_params, (tuple, list)):
                status_message_list = json_params
                for sm in status_message_list:
                    message_id  = str(sm.get('MessageID'))
                    email       = sm.get('email')
                    if is_not_empty(email):
                        MerchantSentEmail.update_sent_status_by_email_id(message_id)
            else:
                message_id  = str(json_params.get('MessageID'))
                email       = json_params.get('email')
                if is_not_empty(email):
                    MerchantSentEmail.update_sent_status_by_email_id(message_id)
            
    
    output = {'success':True}
    if json_params:
        output['json'] = json_params
    
    return jsonify(output), 200, {'ContentType':'application/json'}

@mailjet_service_bp.route('/mail-opened-status', methods=['PUT','POST'])
def update_mail_opened_status():
    json_params  = request.json
    
    logger.debug('json_params=%s', json_params)
    
    if json_params:
        db_client = create_db_client(info=current_app.config['database_config'], caller_info="update_mail_opened_status")
        
        with db_client.context():
            if isinstance(json_params, (tuple, list)):
                status_message_list = json_params
                for sm in status_message_list:
                    message_id  = str(sm.get('MessageID'))
                    email       = sm.get('email')
                    if is_not_empty(email):
                        MerchantSentEmail.update_open_status_by_email_id(message_id)
            else:
                message_id  = str(json_params.get('MessageID'))
                email       = json_params.get('email')
                if is_not_empty(email):
                    MerchantSentEmail.update_open_status_by_email_id(message_id)
            
    
    output = {'success':True}
    if json_params:
        output['json'] = json_params
    
    return jsonify(output), 200, {'ContentType':'application/json'}

@mailjet_service_bp.route('/mail-clicked-status', methods=['PUT','POST'])
def update_mail_clicked_status():
    json_params  = request.json
    
    logger.debug('json_params=%s', json_params)
    
    if json_params:
        db_client = create_db_client(info=current_app.config['database_config'], caller_info="update_mail_clicked_status")
        
        with db_client.context():
            if isinstance(json_params, (tuple, list)):
                status_message_list = json_params
                for sm in status_message_list:
                    message_id  = str(sm.get('MessageID'))
                    email       = sm.get('email')
                    if is_not_empty(email):
                        MerchantSentEmail.update_click_status_by_email_id(message_id)
            else:
                message_id  = str(json_params.get('MessageID'))
                email       = json_params.get('email')
                if is_not_empty(email):
                    MerchantSentEmail.update_click_status_by_email_id(message_id)
            
    
    output = {'success':True}
    if json_params:
        output['json'] = json_params
    
    return jsonify(output), 200, {'ContentType':'application/json'}

@mailjet_service_bp.route('/mail-read-status', methods=['PUT','POST'])
def update_mail_read_status():
    json_params  = request.json
    
    logger.debug('json_params=%s', json_params)
    
    if json_params:
        db_client = create_db_client(info=current_app.config['database_config'], caller_info="update_mail_read_status")
        
        with db_client.context():
            if isinstance(json_params, (tuple, list)):
                status_message_list = json_params
                for sm in status_message_list:
                    message_id  = str(sm.get('MessageID'))
                    email       = sm.get('email')
                    if is_not_empty(email):
                        MerchantSentEmail.update_read_status_by_email_id(message_id)
            else:
                message_id  = str(json_params.get('MessageID'))
                email       = json_params.get('email')
                if is_not_empty(email):
                    MerchantSentEmail.update_read_status_by_email_id(message_id)
            
    
    output = {'success':True}
    if json_params:
        output['json'] = json_params
    
    return jsonify(output), 200, {'ContentType':'application/json'}

@mailjet_service_bp.route('/mail-bounce-status', methods=['PUT','POST'])
def update_mail_bounce_status():
    json_params  = request.json
    
    logger.debug('json_params=%s', json_params)
    
    if json_params:
        db_client = create_db_client(info=current_app.config['database_config'], caller_info="update_mail_bounce_status")
        
        with db_client.context():
            if isinstance(json_params, (tuple, list)):
                status_message_list = json_params
                for sm in status_message_list:
                    message_id  = str(sm.get('MessageID'))
                    email       = sm.get('email')
                    if is_not_empty(email):
                        MerchantSentEmail.update_bounce_status_by_email_id(message_id)
            else:
                message_id  = str(json_params.get('MessageID'))
                email       = json_params.get('email')
                if is_not_empty(email):
                    MerchantSentEmail.update_bounce_status_by_email_id(message_id)
            
    
    output = {'success':True}
    if json_params:
        output['json'] = json_params
    
    return jsonify(output), 200, {'ContentType':'application/json'}

@mailjet_service_bp.route('/mail-spammed-status', methods=['PUT','POST'])
def update_mail_spam_status():
    json_params  = request.json
    
    logger.debug('json_params=%s', json_params)
    
    if json_params:
        db_client = create_db_client(info=current_app.config['database_config'], caller_info="update_mail_spam_status")
        
        with db_client.context():
            if isinstance(json_params, (tuple, list)):
                status_message_list = json_params
                for sm in status_message_list:
                    message_id  = str(sm.get('MessageID'))
                    email       = sm.get('email')
                    if is_not_empty(email):
                        MerchantSentEmail.update_spam_status_by_email_id(message_id)
            else:
                message_id  = str(json_params.get('MessageID'))
                email       = json_params.get('email')
                if is_not_empty(email):
                    MerchantSentEmail.update_spam_status_by_email_id(message_id)
            
    
    output = {'success':True}
    if json_params:
        output['json'] = json_params
    
    return jsonify(output), 200, {'ContentType':'application/json'}

@mailjet_service_bp.route('/mail-blocked-status', methods=['PUT','POST'])
def update_mail_blocked_status():
    json_params  = request.json
    
    logger.debug('json_params=%s', json_params)
    
    if json_params:
        db_client = create_db_client(info=current_app.config['database_config'], caller_info="update_mail_blocked_status")
        
        with db_client.context():
            if isinstance(json_params, (tuple, list)):
                status_message_list = json_params
                for sm in status_message_list:
                    message_id  = str(sm.get('MessageID'))
                    email       = sm.get('email')
                    if is_not_empty(email):
                        MerchantSentEmail.update_block_status_by_email_id(message_id)
            else:
                message_id  = str(json_params.get('MessageID'))
                email       = json_params.get('email')
                if is_not_empty(email):
                    MerchantSentEmail.update_block_status_by_email_id(message_id)
            
    
    output = {'success':True}
    if json_params:
        output['json'] = json_params
    
    return jsonify(output), 200, {'ContentType':'application/json'}


    
