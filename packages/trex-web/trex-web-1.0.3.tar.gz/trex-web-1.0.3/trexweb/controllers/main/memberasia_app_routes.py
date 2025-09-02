'''
Created on 19 Jul 2023

@author: jacklok
'''

from flask import Blueprint, render_template, request
import logging
from trexweb.libs import http
from werkzeug.utils import redirect
from trexweb import conf


memberasia_app_bp = Blueprint('memberasia_app_bp', __name__,
                     template_folder    = 'templates',
                     static_folder      = 'static',
                     url_prefix         = '/memberasia'
                     )

logger = logging.getLogger('controller')

'''
Blueprint settings here
'''
@memberasia_app_bp.context_processor
def mobile_app_bp_inject_settings():
    return dict(
                )

@memberasia_app_bp.route('/install', methods=['GET'])
def install_memberasia_app():
    
    redirect_url = None
    if http.is_huawei(request):
        redirect_url = conf.HUAWEI_GALLERY_URL_MEMBERASIA
    elif http.is_android(request):
        redirect_url = conf.PLAYSTORE_URL_MEMBERASIA
    elif http.is_ios(request):
        redirect_url = conf.APPLESTORE_URL_MEMBERASIA
    else:
        redirect_url = conf.DOWNLOAD_URL_MEMBERASIA

    return redirect(redirect_url)
    
@memberasia_app_bp.route('/google-play-store', methods=['GET'])
def google_play_store():
    return render_template("product/memberasia/install_store.html", 
                           store_name = 'Google Play Store',
                           browser_user_agent=http.browser_user_agent(request),
                           )
    
@memberasia_app_bp.route('/apple-store', methods=['GET'])
def apple_store():
    return render_template("product/memberasia/install_store.html", 
                           store_name = 'Apple Store',
                           browser_user_agent=http.browser_user_agent(request),
                           )
    
@memberasia_app_bp.route('/huawei-gallery', methods=['GET'])
def huawei_gallary():
    return render_template("product/memberasia/install_store.html", 
                           store_name = 'Huawei Gallery',
                           browser_user_agent=http.browser_user_agent(request),
                           )
    
@memberasia_app_bp.route('/download', methods=['GET'])
def download():
    return render_template("product/memberasia/download_app.html", 
                           browser_user_agent   = http.browser_user_agent(request),
                           play_store_url       = conf.PLAYSTORE_URL_MEMBERASIA,
                           huawei_store_url     = conf.HUAWEI_GALLERY_URL_MEMBERASIA,
                           apple_store_url      = conf.APPLESTORE_URL_MEMBERASIA,
                           )         
          
