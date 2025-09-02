'''
Created on 11 Jun 2020

@author: jacklok
'''
import os, json, conf
from flask import Blueprint, request, jsonify, current_app
from utils.log_util import get_tracelog
from utils.string_util import is_not_empty
import logging
from utils.model.model_util import create_db_client
from models.datastore.merchant_models import MerchantSentEmail


web_beacon_tracking_bp = Blueprint('web_beacon_tracking_bp', __name__,
                                     template_folder    = 'templates',
                                     static_folder      = 'static',
                                     url_prefix         = '/system/web-beacon'
                                     )


logger = logging.getLogger('web_beacon_tracking_routes')

@web_beacon_tracking_bp.route('/open', methods=['GET'])
def open_track_status():
    beacon_type = request.args.get('beacon_type')
    beacon_id   = request.args.get('beacon_id')
    
    logger.debug('beacon_type=%s', beacon_type)
    logger.debug('beacon_id=%s', beacon_id)
    
    if is_not_empty(beacon_type) and is_not_empty(beacon_id):
        
        
        db_client = create_db_client(info=current_app.config['database_config'], caller_info="open_track_status")
        
        with db_client.context():
            if conf.WEB_BEACON_TRACK_EMAIL_OPEN == beacon_type:
                MerchantSentEmail.update_open_status_by_email_id(beacon_id)
        
            
    
    output = {'success':True}
    
    return jsonify(output), 200, {'ContentType':'application/json'}