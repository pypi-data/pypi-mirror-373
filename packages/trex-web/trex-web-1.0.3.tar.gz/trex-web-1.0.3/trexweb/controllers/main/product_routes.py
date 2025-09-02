'''
Created on 31 Oct 2023

@author: jacklok
'''

from flask import Blueprint, render_template, abort
import logging
from trexweb import conf
from trexweb.conf import is_local_development, DEPLOYMENT_MODE


product_bp = Blueprint('product_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/product')


@product_bp.context_processor
def inject_settings():


    return dict(
            branding_text               = conf.APPLICATION_NAME,
            app_title                   = conf.APPLICATION_TITLE,
            PAGE_EMAIL                  = conf.PAGE_EMAIL,
            OBFUSCATED_EMAIL            = conf.OBFUSCATED_EMAIL,
            CONTACT_EMAIL               = conf.CONTACT_EMAIL,
            OBFUSCATED_CONTACT_EMAIL    = conf.OBFUSCATED_CONTACT_EMAIL,
            )

@product_bp.route('/memberla')
def memberla_page(): 
    return render_template('product/memberla/memberla_page.html',
                            PLAYSTORE_URL_MEMBERLA              = conf.PLAYSTORE_URL_MEMBERLA,
                            APPLESTORE_URL_MEMBERLA             = conf.APPLESTORE_URL_MEMBERLA,
                            HUAWEI_GALLERY_URL_MEMBERLA         = conf.HUAWEI_GALLERY_URL_MEMBERLA,
                            
                           )

@product_bp.route('/memberasia')
def memberasia_page(): 
    return render_template('product/memberasia/memberasia_page.html',
                           
                            PLAYSTORE_URL_MEMBERASIA            = conf.PLAYSTORE_URL_MEMBERASIA,
                            APPLESTORE_URL_MEMBERASIA           = conf.APPLESTORE_URL_MEMBERASIA,
                            HUAWEI_GALLERY_URL_MEMBERASIA       = conf.HUAWEI_GALLERY_URL_MEMBERASIA,
                            WEB_URL_MEMBERASIA                  = conf.WEB_URL_MEMBERASIA, 
                           )



