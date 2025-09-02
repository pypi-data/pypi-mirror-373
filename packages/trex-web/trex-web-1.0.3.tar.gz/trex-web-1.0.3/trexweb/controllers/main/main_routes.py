'''
Created on 15 Apr 2020

@author: jacklok
'''

from flask import Blueprint, render_template, abort, redirect
import logging
#from trexweb import conf
from trexconf import conf
from trexweb.conf import is_local_development, DEPLOYMENT_MODE
from flask.helpers import url_for


main_bp = Blueprint('main_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/')


@main_bp.context_processor
def inject_settings():


    return dict(
            )

@main_bp.route('/test-home')
def test_home(): 
    #return render_template('main/home.html', navigation_type = 'home',)
    return render_template('test/test_home.html')


@main_bp.route('/')
@main_bp.route('/home')
def home_page(): 
    #return render_template('main/index.html', navigation_type='home')
    #return render_template('main/leon_index.html', navigation_type='home')

    return render_template('main/ai_index.html', navigation_type='home')

'''
@main_bp.route('/download')
def download_page(): 
    return render_template('landing/download_page.html')
'''

@main_bp.route('/api-docs')
def api_doc(): 
    return render_template('main/api_docs.html', 
                           navigation_type = 'api-docs',)
    
@main_bp.route('/pricing')
def pricing_page(): 
    return render_template('main/pricing/pricing_page.html', 
                           navigation_type = 'pricing',)
    
@main_bp.route('/service')
def service_page(): 
    return render_template('landing/service_section_page.html', 
                           navigation_type = 'service',)


@main_bp.route('/feature')
def feature_page(): 
    return render_template('landing/feature_section_page.html', 
                           navigation_type = 'feature',)
    
@main_bp.route('/about-us')
def about_us_page(): 
    return render_template('main/about-us/about_us.html', 
                           navigation_type = 'about_us',)                        

@main_bp.route('/read-more')
def read_more_page(): 
    return render_template('main/about_us.html', 
                           navigation_type = 'about_us',)
    
@main_bp.route('/api-integration')
def api_integration_page(): 
    return render_template('main/api_integration.html', 
                           navigation_type = 'about_us',)    

@main_bp.route('/contact-us')
def contact_us_page():
    return render_template(
            "main/contact_us.html",
            is_local_dev = is_local_development(),
            DEPLOYMENT_MODE = DEPLOYMENT_MODE,
            )

@main_bp.route('/thank-you-for-contact-us', methods=['GET'])
def thank_you_for_contact_us_page():
    return render_template("main/thank_you_for_contact_us.html")

@main_bp.route('/terms-and-conditions', methods=['GET'])
def terms_and_conditions_page():
    return render_template("main/terms_and_conditions.html")

@main_bp.route('/terms-and-conditions-content', methods=['GET'])
def terms_and_conditions_simple():
    return render_template("main/terms_and_conditions_simple.html")

@main_bp.route('/privacy-policy', methods=['GET'])
def privacy_policy_page():
    return render_template("main/privacy_policy.html")

@main_bp.route('/privacy-policy-content', methods=['GET'])
def privacy_policy_content():
    return render_template("main/privacy_policy_simple.html")

@main_bp.route('/privacy-promise', methods=['GET'])
def privacy_promise_page():
    return render_template("main/privacy_promise.html")

@main_bp.route('/terms-of-use', methods=['GET'])
def terms_of_use_page():
    return render_template("main/terms_of_use.html")

@main_bp.route('/product-membership-program')
def membership_program_page(): 
    return render_template("main/product_membership_program.html")

@main_bp.route('/product-point-of-sales')
def point_of_sales_page(): 
    return render_template("main/product_point_of_sales.html")

@main_bp.route('/download')
def download_page(): 
    return render_template("main/download.html")

@main_bp.route('/backoffice/user-guide')
def backoffice_user_guide(): 
    return redirect('https://storage.googleapis.com/augmigo-document/user-guide/augmigo-backoffice-user-guide-v1.2.pdf')

@main_bp.route('/memberasia/instant-reward-demo')
def scan_instant_reward_demo(): 
    return redirect('https://youtu.be/h1ZzgYdWjkg')

@main_bp.route('/products')
def products(): 
    return render_template("product/products_page.html")

@main_bp.route('/know-more')
def know_more(): 
    return render_template("marketing/know_more.html")


