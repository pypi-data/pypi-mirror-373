'''
Created on 7 Apr 2020

@author: jacklok
'''
import logging, os

APPLICATION_NAME                            = os.environ.get('APPLICATION_NAME')
BRANDING                                    = os.environ.get('BRANDING')
APPLICATION_TITLE                           = os.environ.get('APPLICATION_TITLE')
APPLICATION_DESC                            = os.environ.get('APPLICATION_DESC')
APPLICATION_HREF                            = os.environ.get('APPLICATION_HREF')
APP_SEARCH_KEYWORDS                         = os.environ.get('APP_SEARCH_KEYWORDS')
BACKOFFICE_SIGNIN_URL                       = os.environ.get('BACKOFFICE_SIGNIN_URL')
APP_LOGO_PATH                               = os.environ.get('APP_LOGO_PATH')
APP_ABOUT_IMAGE_PATH                        = os.environ.get('APP_ABOUT_IMAGE_PATH')
APP_LOADING_PATH                            = os.environ.get('APP_LOADING_PATH') 
APP_ICO_PATH                                = os.environ.get('APP_ICO_PATH')
SUPPORT_EMAIL                               = os.environ.get('SUPPORT_EMAIL')
PAGE_EMAIL                                  = os.environ.get('PAGE_EMAIL')
OBFUSCATED_EMAIL                            = os.environ.get('OBFUSCATED_EMAIL')

CONTACT_EMAIL                               = os.environ.get('CONTACT_EMAIL')
OBFUSCATED_CONTACT_EMAIL                    = os.environ.get('OBFUSCATED_CONTACT_EMAIL')

GOOGLE_APP_INSTALL_IMG                      = os.environ.get('GOOGLE_APP_INSTALL_IMG')
IOS_APP_INSTALL_IMG                         = os.environ.get('IOS_APP_INSTALL_IMG')
HUAWEI_APP_INSTALL_IMG                      = os.environ.get('HUAWEI_APP_INSTALL_IMG')

GOOGLE_APP_INSTALL_URL                      = os.environ.get('GOOGLE_APP_INSTALL_URL')
IOS_APP_INSTALL_URL                         = os.environ.get('IOS_APP_INSTALL_URL')
HUAWEI_APP_INSTALL_URL                      = os.environ.get('HUAWEI_APP_INSTALL_URL')

RECAPTCHA_SECRET_KEY                        = os.environ.get('RECAPTCHA_SECRET_KEY')

APPLICATION_SHOW_DASHBOARD_MESSAGE          = False
APPLICATION_SHOW_DASHBOARD_NOTIFICATION     = False


PRODUCTION_MODE                             = "PROD"
DEMO_MODE                                   = "DEMO"
LOCAL_MODE                                  = "LOCAL"


#DEPLOYMENT_MODE                             = PRODUCTION_MODE
#DEPLOYMENT_MODE                             = DEMO_MODE
DEPLOYMENT_MODE                             = os.environ.get('DEPLOYMENT_MODE')

PAYMENT_GATEWAY_APP_KEY                     = ''
PAYMENT_GATEWAY_SECRET_KEY                  = ''

STRIPE_PAYMENT_GATEWAY_APP_KEY              = ''
STRIPE_PAYMENT_GATEWAY_SECRET_KEY           = ''


STRIPE_PAYMENT_GATEWAY_APP_KEY_FOR_LIVE     = 'pk_live_WEshxo5PrfcOyFxSgKskK5pw'
STRIPE_PAYMENT_GATEWAY_SECRET_KEY_FOR_LIVE  = 'sk_live_PEhkanjtcFRsjp7BE1O0mquC00hrYv1gWB'

STRIPE_PAYMENT_GATEWAY_APP_KEY_FOR_TEST     = 'sk_live_uj6BfYx5zQe5zN64A3w48RWJ00U39cP95h'
STRIPE_PAYMENT_GATEWAY_SECRET_KEY_FOR_TEST  = 'sk_test_vLw1amMu58RNWLOvFZMjMl7J00vvGnutd0' 

DEFAULT_CURRENCY_CODE                               = 'myr'
STRIPE_DEFAULT_PAYMENT_METHOD_TYPES                 = ['card','fpx']

FIREBASE_CERT_KEY_FILEPATH                          = None

DATASTORE_SERVICE_ACCOUNT_KEY_FILEPATH              = None

PROJECT_ID                                          = 'penefit-payment-dev'

CSRF_ENABLED                                        = True

CONTENT_WITH_JAVASCRIPT_LINK                        = True
 
AUTHORIZATION_BASE_URL                              = "/sec/oauth2/authorize"
TOKEN_URL                                           = "/sec/oauth2/token"
USERINFO_URL                                        = "/sec/oauth2/userinfo"

DEBUG_MODE                                          = True

#FACEBOOK_ACCOUNT_ID                                 = os.environ['FACEBOOK_ID']
#FACEBOOK_SECRET_KEY                                 = os.environ['FACEBOOK_SECRET_KEY']

APPLICATION_VERSION_NO                              = "1.0.0"

#LOGIN_CONTENT_URL_FOR_PATH                          = 'security_bp.signin_content'



DAILY_REPORT_RECEIPIENTS                            = ['sglok@augmigo.com']


if DEPLOYMENT_MODE==PRODUCTION_MODE:
    DEBUG_MODE       = False
    #DEBUG_MODE       = True

    #LOGGING_LEVEL    = logging.DEBUG
    #LOGGING_LEVEL    = logging.WARN
    LOGGING_LEVEL    = logging.INFO
    #LOGGING_LEVEL    = logging.ERROR
    
    PAYMENT_GATEWAY_APP_KEY                 = STRIPE_PAYMENT_GATEWAY_APP_KEY_FOR_LIVE
    PAYMENT_GATEWAY_SECRET_KEY              = STRIPE_PAYMENT_GATEWAY_SECRET_KEY_FOR_LIVE
    
    
    
elif DEPLOYMENT_MODE==DEMO_MODE:
    DEBUG_MODE       = True
    #DEBUG_MODE       = False
    
    LOGGING_LEVEL    = logging.DEBUG
    #LOGGING_LEVEL    = logging.INFO
    
    PAYMENT_GATEWAY_APP_KEY                 = STRIPE_PAYMENT_GATEWAY_APP_KEY_FOR_TEST
    PAYMENT_GATEWAY_SECRET_KEY              = STRIPE_PAYMENT_GATEWAY_SECRET_KEY_FOR_TEST
    
elif DEPLOYMENT_MODE==LOCAL_MODE:
    DEBUG_MODE       = True

    LOGGING_LEVEL    = logging.DEBUG
    #LOGGING_LEVEL    = logging.INFO
    


DEFAULT_ETAG_VALUE                              = '68964759a96a7c876b7e'

DEFAULT_COUNTRY_CODE                            = 'my'

MODEL_CACHE_ENABLED                             = False

INTERNAL_MAX_FETCH_RECORD                       = 9999
MAX_FETCH_RECORD_FULL_TEXT_SEARCH               = 1000
MAX_FETCH_RECORD_FULL_TEXT_SEARCH_PER_PAGE      = 10
MAX_FETCH_RECORD                                = 99999999
MAX_FETCH_IMAGE_RECORD                          = 100
MAX_CHAR_RANDOM_UUID4                           = 20
PAGINATION_SIZE                                 = 2
VISIBLE_PAGE_COUNT                              = 10

GENDER_MALE_CODE                                = 'm'
GENDER_FEMALE_CODE                              = 'f'

API_VERSION                                     = '1.0.0'

APPLICATION_ACCOUNT_PROVIDER                    = 'app'

SUPPORT_LANGUAGES                               = ['en','zh']

PLAYSTORE_URL_MEMBERASIA                        = 'https://play.google.com/store/apps/details?id=com.augmigo.memberasia'
APPLESTORE_URL_MEMBERASIA                       = 'https://apps.apple.com/my/app/memberasia/id6469048463'
HUAWEI_GALLERY_URL_MEMBERASIA                   = 'https://appgallery.huawei.com/app/C109444793'
WEB_URL_MEMBERASIA                              = 'https://memberasia.augmigo.com'
DOWNLOAD_URL_MEMBERASIA                         = 'https://www.augmigo.com/memberasia/download'


PLAYSTORE_URL_MEMBERLA                          = 'https://play.google.com/store/apps/details?id=com.augmigo.memberla'
APPLESTORE_URL_MEMBERLA                         = 'https://apps.apple.com/my/app/memberla/id6469686696'
HUAWEI_GALLERY_URL_MEMBERLA                     = 'https://appgallery.huawei.com/app/C109439485'


#-----------------------------------------------------------------
# Web Beacon settings
#-----------------------------------------------------------------
WEB_BEACON_TRACK_EMAIL_OPEN   = 'eo'

def is_local_development():
    return DEPLOYMENT_MODE==LOCAL_MODE 

    