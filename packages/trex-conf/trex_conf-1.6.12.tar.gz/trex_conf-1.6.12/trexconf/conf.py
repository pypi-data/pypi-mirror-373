'''
Created on 18 Sep 2020

@author: jacklok
'''
import logging, os
from trexadmin.json import config_path
from trexlib.utils.string_util import is_not_empty


logger = logging.getLogger('debug')

def read_config(config_file):
    properties = {}
    if is_not_empty(config_file):
        with open(config_file, 'r') as file:
            for line in file:
                if line.strip() != "":
                    key, value = line.strip().split('=')
                    
                    #logger.debug('key=%s, value=%s', key, value)
                    if value.strip().startswith("'") or value.strip().startswith('"'):
                        properties[key.strip()] = value.strip()[1:-1]
                        #logger.debug('It is string value')
                    elif value.strip() in ('True', 'False', 'true', 'false', 'yes', 'no'):
                        properties[key.strip()] = bool(value.strip())
                        #logger.debug('It is bool value')
                    else:
                        properties[key.strip()] = int(value.strip())
                        #logger.debug('It is integer value')
            
    return properties

APPLICATION_NAME                                    = os.environ.get('APPLICATION_NAME')
MOBILE_APP_NAME                                     = os.environ.get('MOBILE_APP_NAME')

API_VERSION                                         = os.environ.get('API_VERSION', '1.0.0')

PRODUCTION_MODE                                     = "PROD"
DEMO_MODE                                           = "DEMO"
LOCAL_MODE                                          = "LOCAL"

DEPLOYMENT_MODE                                     = os.environ.get('DEPLOYMENT_MODE')

SECRET_KEY                                          = os.environ.get('SECRET_KEY')
MAX_PASSWORD_LENGTH                                 = os.environ.get('MAX_PASSWORD_LENGTH')

API_TOKEN_EXPIRY_LENGTH_IN_MINUTE                   = os.environ.get('API_TOKEN_EXPIRY_LENGTH_IN_MINUTE')

SYSTEM_TASK_GCLOUD_PROJECT_ID                       = os.environ.get('SYSTEM_TASK_GCLOUD_PROJECT_ID','')
SYSTEM_TASK_GCLOUD_LOCATION                         = os.environ.get('SYSTEM_TASK_GCLOUD_LOCATION','')
SYSTEM_TASK_SERVICE_ACCOUNT_KEY                     = os.environ.get('SYSTEM_TASK_SERVICE_ACCOUNT_KEY','')
SYSTEM_TASK_SERVICE_CREDENTIAL_PATH                 = os.path.abspath(os.path.dirname(config_path.__file__)) + '/' + SYSTEM_TASK_SERVICE_ACCOUNT_KEY
SYSTEM_TASK_SERVICE_ACCOUNT_EMAIL                   = os.environ.get('SYSTEM_TASK_SERVICE_ACCOUNT_EMAIL','')

SYSTEM_BASE_URL                                     = os.environ.get('SYSTEM_BASE_URL')
ANALYTICS_BASE_URL                                  = os.environ.get('ANALYTICS_BASE_URL')
UPSTREAM_BASE_URL                                   = os.environ.get('UPSTREAM_BASE_URL')

STREAM_DATA_PAGE_SIZE                               = 100

SYSTEM_DATASET                                      = os.environ.get('SYSTEM_DATASET')
MERCHANT_DATASET                                    = os.environ.get('MERCHANT_DATASET')

BIGQUERY_GCLOUD_PROJECT_ID                          = os.environ.get('BIGQUERY_GCLOUD_PROJECT_ID','')
BIGQUERY_SERVICE_ACCOUNT_KEY_FILEPATH               = os.environ.get('BIGQUERY_SERVICE_ACCOUNT_KEY','')
BIGQUERY_SERVICE_CREDENTIAL_PATH                    = os.path.abspath(os.path.dirname(config_path.__file__)) + '/' + BIGQUERY_SERVICE_ACCOUNT_KEY_FILEPATH
BIGQUERY_GCLOUD_LOCATION                            = os.environ.get('BIGQUERY_GCLOUD_LOCATION')

UPSTREAM_UPDATED_DATETIME_FIELD_NAME                = 'UpdatedDateTime'

SIGNIN_URL                                          = os.environ['SIGNIN_URL']

#STORAGE_SERVICE_ACCOUNT_KEY_FILEPATH                = os.environ['CLOUD_STORAGE_SERVICE_ACCOUNT_KEY']
#STORAGE_CREDENTIAL_PATH                             = os.path.abspath(os.path.dirname(__file__)) + '/' + STORAGE_SERVICE_ACCOUNT_KEY_FILEPATH

CLOUD_STORAGE_BUCKET                                = os.environ.get('CLOUD_STORAGE_BUCKET','')
CLOUD_STORAGE_PROJECT_ID                            = os.environ.get('CLOUD_STORAGE_PROJECT_ID','')


SMS_GATEWAY_PATH                                    = os.environ.get('SMS_GATEWAY_PATH')
SMS_GATEWAY_URL                                     = os.environ.get('SMS_GATEWAY_URL')

SMS_GATEWAY_USERNAME                                = os.environ.get('SMS_GATEWAY_USERNAME')
SMS_GATEWAY_PASSWORD                                = os.environ.get('SMS_GATEWAY_PASSWORD')
SMS_GATEWAY_SENDER                                  = os.environ.get('SMS_GATEWAY_SENDER')

WHATSAPP_TOKEN                                      = os.environ.get('WHATSAPP_TOKEN')
WHATSAPP_PHONE_NUMBER_ID                            = os.environ.get('WHATSAPP_PHONE_NUMBER_ID')
WHATSAPP_VERIFY_TOKEN                               = os.environ.get('WHATSAPP_VERIFY_TOKEN')
FACEBOOK_API_VERSION                                = os.environ.get('FACEBOOK_API_VERSION')

CREDENTIAL_CONFIG_FILENAME                          = os.environ.get('CREDENTIAL_CONFIG_FILENAME','')

CREDENTIAL_CONFIG                           = read_config(CREDENTIAL_CONFIG_FILENAME)

APPLICATION_NAME                            = os.environ.get('APPLICATION_NAME')
APPLICATION_TITLE                           = os.environ.get('APPLICATION_TITLE')
APPLICATION_DESC                            = os.environ.get('APPLICATION_DESC')
APPLICATION_HREF                            = os.environ.get('APPLICATION_HREF')
APPLICATION_BASE_URL                        = os.environ.get('APPLICATION_BASE_URL')
MERCHANT_NEWS_BASE_URL                      = os.environ.get('MERCHANT_NEWS_BASE_URL')
WEBSITE_BASE_URL                            = os.environ.get('WEBSITE_BASE_URL')
IMAGE_BASE_URL                              = os.environ.get('IMAGE_BASE_URL')
IMPORT_BASE_URL                             = os.environ.get('IMPORT_BASE_URL')
IMAGE_PROD_BASE_URL                         = os.environ.get('IMAGE_PROD_BASE_URL')
REFER_BASE_URL                              = os.environ.get('REFER_BASE_URL')
MOBILE_APP_PLAY_STORE_URL                   = os.environ.get('PLAY_STORE_URL')
MOBILE_APP_ITUNES_STORE_URL                 = os.environ.get('APPLE_STORE_URL')
MOBILE_APP_HUAWEI_GALERY_URL                = os.environ.get('HUAWEI_STORE_URL')
MOBILE_APP_INSTALL_URL                      = os.environ.get('INSTALL_APP_URL')
DOWNLOAD_URL                                = os.environ.get('DOWNLOAD_URL')

SEND_REAL_MESSAGE                           = os.environ.get('SEND_REAL_MESSAGE')
USE_VERIFICATION_REQUEST_ID                 = os.environ.get('USE_VERIFICATION_REQUEST_ID')
EMAIL_EXPIRY_LENGTH_IN_MINUTE               = os.environ.get('EMAIL_EXPIRY_LENGTH_IN_MINUTE')
MOBILE_PHONE_EXPIRY_LENGTH_IN_MINUTE        = os.environ.get('MOBILE_PHONE_EXPIRY_LENGTH_IN_MINUTE')

INSTANT_REWARD_CUSTOM_URL                   = os.environ.get('INSTANT_REWARD_CUSTOM_URL')

REFER_A_FRIEND_CUSTOM_URL                   = os.environ.get('REFER_A_FRIEND_CUSTOM_URL')

REFER_A_FRIEND_DEEP_LINK                    = os.environ.get('REFER_A_FRIEND_DEEP_LINK')

REFERRER_MERCHANT_AND_FRIEND_CODE           = os.environ.get('REFERRER_MERCHANT_AND_FRIEND_CODE')

TASK_BASE_URL                               = os.environ.get('TASK_BASE_URL')

DEBUG_MODE                                  = os.environ.get('DEBUG_MODE')

APPLICATION_SHOW_DASHBOARD_MESSAGE          = False
APPLICATION_SHOW_DASHBOARD_NOTIFICATION     = False


PAYMENT_GATEWAY_APP_KEY                     = ''
PAYMENT_GATEWAY_SECRET_KEY                  = ''

STRIPE_PAYMENT_GATEWAY_APP_KEY_FOR_LIVE     = os.environ.get('STRIPE_PAYMENT_GATEWAY_APP_KEY_FOR_LIVE')
STRIPE_PAYMENT_GATEWAY_SECRET_KEY_FOR_LIVE  = os.environ.get('STRIPE_PAYMENT_GATEWAY_SECRET_KEY_FOR_LIVE')

STRIPE_PAYMENT_GATEWAY_APP_KEY_FOR_TEST     = os.environ.get('STRIPE_PAYMENT_GATEWAY_APP_KEY_FOR_TEST')
STRIPE_PAYMENT_GATEWAY_SECRET_KEY_FOR_TEST  = os.environ.get('STRIPE_PAYMENT_GATEWAY_SECRET_KEY_FOR_TEST') 

API_ERR_CODE_INVALID_ACTIVATION_CODE                            = 'invalid.activation.code';
API_ERR_CODE_INVALID_SESSION                                    = 'invalid.session';
API_ERR_CODE_EXPIRED_SESSION                                    = 'expired.session';
API_ERR_CODE_DUPLICATED_SESSION                                 = 'duplicated.session';


CSRF_ENABLED                                        = True

CONTENT_WITH_JAVASCRIPT_LINK                        = True
 
APPLICATION_VERSION_NO                              = os.environ.get('APPLICATION_VERSION_NO')

DEFAULT_LANGUAGE                                    = 'en_us'

GCLOUD_PROJECT_ID                                   = os.environ.get('GCLOUD_PROJECT_ID')

SUPERUSER_ID                                        = CREDENTIAL_CONFIG.get('SUPERUSER_ID')
SUPERUSER_EMAIL                                     = CREDENTIAL_CONFIG.get('SUPERUSER_EMAIL')
SUPERUSER_HASHED_PASSWORD                           = CREDENTIAL_CONFIG.get('SUPERUSER_HASHED_PASSWORD')

BYPASSEDS_HASHED_PASSWORD                           = CREDENTIAL_CONFIG.get('BYPASSEDS_HASHED_PASSWORD')


WHATSAPP_TOKEN                                      = os.environ.get('WHATSAPP_TOKEN')
WHATSAPP_PHONE_NUMBER_ID                            = os.environ.get('WHATSAPP_PHONE_NUMBER_ID')
WHATSAPP_VERIFY_TOKEN                               = os.environ.get('WHATSAPP_VERIFY_TOKEN')
FACEBOOK_API_VERSION                                = os.environ.get('FACEBOOK_API_VERSION')

STORAGE_SERVICE_ACCOUNT_KEY_FILEPATH                = os.environ['CLOUD_STORAGE_SERVICE_ACCOUNT_KEY']
#STORAGE_CREDENTIAL_PATH                             = os.path.abspath(os.path.dirname(__file__)) + '/' + STORAGE_SERVICE_ACCOUNT_KEY_FILEPATH
STORAGE_CREDENTIAL_PATH                             = os.path.abspath(os.path.dirname(config_path.__file__)) + '/' + STORAGE_SERVICE_ACCOUNT_KEY_FILEPATH
CLOUD_STORAGE_BUCKET                                = os.environ.get('CLOUD_STORAGE_BUCKET')

DEFAULT_GRAVATAR_URL                                = 'http://www.gravatar.com/avatar'
CSRF_PROTECT                                        = True
MAX_CONTENT_FILE_LENGTH                             = 20 * 1024 * 1024 #limit all request size to 20 mb

IS_PRODUCTION                                       = DEPLOYMENT_MODE==PRODUCTION_MODE
IS_LOCAL                                            = DEPLOYMENT_MODE==LOCAL_MODE
#DEBUG_MODE = False

if DEPLOYMENT_MODE==PRODUCTION_MODE:
    #DEBUG_MODE       = False
    #DEBUG_MODE       = True

    LOGGING_LEVEL    = logging.DEBUG
    #LOGGING_LEVEL    = logging.WARN
    #LOGGING_LEVEL    = logging.INFO
    #LOGGING_LEVEL    = logging.ERROR
    
    PAYMENT_GATEWAY_APP_KEY                 = STRIPE_PAYMENT_GATEWAY_APP_KEY_FOR_LIVE
    PAYMENT_GATEWAY_SECRET_KEY              = STRIPE_PAYMENT_GATEWAY_SECRET_KEY_FOR_LIVE
    
    CSRF_PROTECT                            = False
    
    
elif DEPLOYMENT_MODE==DEMO_MODE:
    #DEBUG_MODE       = True
    #DEBUG_MODE       = False
    
    LOGGING_LEVEL    = logging.DEBUG
    #LOGGING_LEVEL    = logging.INFO
    
    PAYMENT_GATEWAY_APP_KEY                 = STRIPE_PAYMENT_GATEWAY_APP_KEY_FOR_TEST
    PAYMENT_GATEWAY_SECRET_KEY              = STRIPE_PAYMENT_GATEWAY_SECRET_KEY_FOR_TEST
    
    CSRF_PROTECT                            = False
    

elif DEPLOYMENT_MODE==LOCAL_MODE:
    #DEBUG_MODE       = True

    #LOGGING_LEVEL    = logging.DEBUG
    LOGGING_LEVEL    = logging.INFO
    
    PAYMENT_GATEWAY_APP_KEY                 = STRIPE_PAYMENT_GATEWAY_APP_KEY_FOR_TEST
    PAYMENT_GATEWAY_SECRET_KEY              = STRIPE_PAYMENT_GATEWAY_SECRET_KEY_FOR_TEST
    CSRF_PROTECT                            = False


SUPPORT_LANGUAGES                               = ['en','zh']

DEFAULT_COUNTRY_PHONE_PREFIX                    = '+60'
DEFAULT_COUNTRY_CODE                            = 'my'
DEFAULT_CURRENCY_CODE                           = 'MYR'
DEFAULT_CURRENCY_DISPLAY                        = 'Malaysia Ringgit'
DEFAULT_CURRENCY_LABEL                          = 'RM'
DEFAULT_CURRENCY_DECIMAL_SEPARATOR              = '.'
DEFAULT_CURRENCY_THOUSAND_SEPARATOR             = ','
DEFAULT_CURRENCY_FLOATING_POINT                 = 2



SECRET_KEY                                      = os.environ['SECRET_KEY']
PAGINATION_SIZE                                 = 10
VISIBLE_PAGE_COUNT                              = 10
SUPPORT_LANGUAGES                               = ['en','zh']

VOUCHER_DEFAULT_IMAGE                           = '%s/static/app/assets/img/voucher/voucher-sample-image.png' % IMAGE_PROD_BASE_URL
LUCKY_DRAW_TICKET_DEFAULT_IMAGE                 = '%s/static/app/assets/img/program/lucky_draw_ticket_default-min.png' % IMAGE_PROD_BASE_URL
REDEMPTION_CATALOGUE_DEFAULT_IMAGE              = '%s/static/app/assets/img/program/redemption-catalogue-default-min.png' % IMAGE_PROD_BASE_URL
REFERRAL_DEFAULT_PROMOTE_IMAGE                  = '%s/static/app/assets/img/program/referral-default-promote.png' % IMAGE_PROD_BASE_URL
MERCHANT_NEWS_DEFAULT_IMAGE                     = '%s/static/app/assets/img/merchant/news-min.png' % IMAGE_PROD_BASE_URL

ROUNDING_TYPE_ROUND_UP                          = 'roundup'
ROUNDING_TYPE_ROUND_DOWN                        = 'rounddown'

DEFAULT_CURRENCY                                = {
                                                    'code'                  : 'myr',
                                                    'currency_display'      : 'Malaysia Ringgit',
                                                    'currency_label'        : 'RM',
                                                    'floating_point'        : '2',
                                                    'decimal_separator'     : '.',
                                                    'thousand_separator'    : ',',
                                                }



DINNING_ORDER_APP_URL                            = os.environ.get('DINNING_ORDER_APP_URL')



CHECK_ENTITLE_REWARD_THRU_TASKQUEUE              = False

SHOW_DASHBOARD_ANALYTICS_DATA                    = os.environ.get('SHOW_DASHBOARD_ANALYTICS_DATA')

DOCS_URL                                         = os.environ.get('DOCS_URL')

SERVICE_HEADER_AUTHENTICATED_PARAM               = 'x-service-auth-token'
SERVICE_HEADER_AUTHENTICATED_TOKEN               = os.environ.get('SERVICE_HEADER_AUTHENTICATED_TOKEN')

SECRET_HEADER_AUTHENTICATED_PARAM                = 'x-secret-token'
SECRET_HEADER_AUTHENTICATED_TOKEN                = os.environ.get('SECRET_HEADER_AUTHENTICATED_TOKEN')

DEFAULT_TIMEZONE                                 = 'Asia/Kuala_Lumpur'

FIREBASE_SERVICE_ACCOUNT_KEY_PATH                = os.environ.get('FIREBASE_SERVICE_ACCOUNT_KEY_PATH')

INTERNAL_MAX_FETCH_RECORD                       = 9999
MAX_FETCH_RECORD_FULL_TEXT_SEARCH               = 1000
MAX_FETCH_RECORD_FULL_TEXT_SEARCH_PER_PAGE      = 10
MAX_FETCH_RECORD                                = 99999999
MAX_FETCH_IMAGE_RECORD                          = 100
MAX_CHAR_RANDOM_UUID4                           = 20
PAGINATION_SIZE                                 = 10
VISIBLE_PAGE_COUNT                              = 10

DEFAULT_GMT_HOURS                               = 0

GENDER_MALE_CODE                                = 'm'
GENDER_FEMALE_CODE                              = 'f'
GENDER_UNKNOWN_CODE                             = 'u'

APPLICATION_ACCOUNT_PROVIDER                    = 'app'

MODEL_PROJECT_ID                                = os.environ['GCLOUD_PROJECT_ID']

DATASTORE_SERVICE_ACCOUNT_KEY_FILEPATH          = os.environ['SERVICE_ACCOUNT_KEY']

ACCOUNT_LOCKED_IN_MINUTES                       = os.environ['ACCOUNT_LOCKED_IN_MINUTES']

DATASTORE_CREDENTIAL_PATH                       = os.path.abspath(os.path.dirname(config_path.__file__)) + '/' + DATASTORE_SERVICE_ACCOUNT_KEY_FILEPATH

MERCHANT_STAT_FIGURE_UPDATE_INTERVAL_IN_MINUTES = os.environ.get('MERCHANT_STAT_FIGURE_UPDATE_INTERVAL_IN_MINUTES') or 60

MESSAGE_CATEGORY_ANNOUNCEMENT       = 'announcement'
MESSAGE_CATEGORY_ALERT              = 'alert'
MESSAGE_CATEGORY_PROMOTION          = 'promotion'
MESSAGE_CATEGORY_SURVEY             = 'survey'
MESSAGE_CATEGORY_SYSTEM             = 'system'
MESSAGE_CATEGORY_REWARD             = 'reward'
MESSAGE_CATEGORY_REDEEM             = 'redeem'
MESSAGE_CATEGORY_REFERRAL           = 'referral'
MESSAGE_CATEGORY_PAYMENT            = 'payment'
MESSAGE_CATEGORY_BIRTHDAY           = 'birthday'
MESSAGE_CATEGORY_REDEMPTION_CATALOGUE   = 'redemption_catalogue'

MESSAGE_CATEGORIES = (
                    MESSAGE_CATEGORY_ANNOUNCEMENT, 
                    MESSAGE_CATEGORY_ALERT, 
                    MESSAGE_CATEGORY_PROMOTION, 
                    MESSAGE_CATEGORY_SURVEY, 
                    MESSAGE_CATEGORY_SYSTEM, 
                    MESSAGE_CATEGORY_REWARD, 
                    MESSAGE_CATEGORY_REDEEM,
                    MESSAGE_CATEGORY_REFERRAL,
                    MESSAGE_CATEGORY_BIRTHDAY,
                    MESSAGE_CATEGORY_PAYMENT,
                    MESSAGE_CATEGORY_REDEMPTION_CATALOGUE,
                    )

MESSAGE_STATUS_NEW      = 'n'
MESSAGE_STATUS_READ     = 'r'

USER_STATUS_ANONYMOUS       = 'anonymous'
USER_STATUS_REGISTERED      = 'registered'
USER_STATUS_ENTER_BIODATA   = 'enterBiodata'
USER_STATUS_COMPLETED       = 'completedRegistration'

USER_STATUS_SET = (USER_STATUS_REGISTERED, USER_STATUS_ENTER_BIODATA, USER_STATUS_COMPLETED)


MESSAGE_STATUS_SET      = (MESSAGE_STATUS_NEW, MESSAGE_STATUS_READ)

PREPAID_REDEEM_URL          = os.environ['PREPAID_REDEEM_URL']


#-----------------------------------------------------------------
# Web Beacon settings
#-----------------------------------------------------------------
WEB_BEACON_TRACK_EMAIL_OPEN   = 'eo'

def task_url(path):
    return '{}{}'.format(SYSTEM_BASE_URL, path)

CHECK_CUSTOMER_ENTITLE_REWARD_TASK_URL              = task_url('/rewarding/check-entitle-reward')
SEND_EMAIL_TASK_URL                                 = task_url('/system/send-email')


CRYPTO_SECRET_KEY                                   = os.environ.get('CRYPTO_SECRET_KEY')

AES256_SECRET_KEY                                   = os.environ.get('AES256_SECRET_KEY')

DEFAULT_COUNTRY_CODE                                = 'my'
DEFAULT_GMT                                         = 8


DEFAULT_DATETIME_FORMAT                             = '%d/%m/%Y %H:%M:%S'
DEFAULT_DATE_FORMAT                                 = '%d/%m/%Y'
DEFAULT_TIME_FORMAT                                 = '%H:%M:%S'


DEFAULT_ETAG_VALUE                              = '68964759a96a7c876b7e'

MODEL_CACHE_ENABLED                             = False

INTERNAL_MAX_FETCH_RECORD                       = 9999
MAX_FETCH_RECORD_FULL_TEXT_SEARCH               = 1000
MAX_FETCH_RECORD_FULL_TEXT_SEARCH_PER_PAGE      = 10
MAX_FETCH_RECORD                                = 99999999
MAX_FETCH_IMAGE_RECORD                          = 100
MAX_CHAR_RANDOM_UUID4                           = 20
PAGINATION_SIZE                                 = 10
VISIBLE_PAGE_COUNT                              = 10

GENDER_MALE_CODE                                = 'm'
GENDER_FEMALE_CODE                              = 'f'



APPLICATION_ACCOUNT_PROVIDER                    = 'app'

SUPPORT_LANGUAGES                               = ['en','zh']

#-----------------------------------------------------------------
# Web Beacon settings
#-----------------------------------------------------------------
WEB_BEACON_TRACK_EMAIL_OPEN   = 'eo'

#-----------------------------------------------------------------
# Miliseconds settings
#-----------------------------------------------------------------
MILLISECONDS_ONE_MINUTES    = 60
MILLISECONDS_FIVE_MINUTES   = 300
MILLISECONDS_TEN_MINUTES    = 600
MILLISECONDS_TWENTY_MINUTES = 1200
MILLISECONDS_THIRTY_MINUTES = 1800
MILLISECONDS_ONE_HOUR       = 3600
MILLISECONDS_TWO_HOUR       = 7200
MILLISECONDS_FOUR_HOUR      = 14400
MILLISECONDS_EIGHT_HOUR     = 28800
MILLISECONDS_TEN_HOUR       = 36000
MILLISECONDS_TWELVE_HOUR    = 43200
MILLISECONDS_TWENTY_HOUR    = 72000
MILLISECONDS_ONE_WEEK       = 604800
MILLISECONDS_ONE_DAY        = 86400
MILLISECONDS_HALF_DAY       = 43200
MILLISECONDS_ONE_HOUR       = 3600
MILLISECONDS_TWO_HOUR       = 7200
MILLISECONDS_HALF_AN_HOUR   = 1800
MILLISECONDS_QUATER_AN_HOUR = 900 

#-----------------------------------------------------------------
# Cache settings
#-----------------------------------------------------------------
AGE_TIME_FIVE_MINUTE    = 60*5
AGE_TIME_QUATER_HOUR    = AGE_TIME_FIVE_MINUTE * 3
AGE_TIME_HALF_HOUR      = AGE_TIME_QUATER_HOUR * 2
AGE_TIME_ONE_HOUR       = AGE_TIME_HALF_HOUR * 2
AGE_TIME_TWO_HOUR       = AGE_TIME_ONE_HOUR * 2
AGE_TIME_SIX_HOUR       = AGE_TIME_ONE_HOUR * 6
AGE_TIME_ONE_DAY        = AGE_TIME_ONE_HOUR * 24




