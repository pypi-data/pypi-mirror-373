'''
Created on 30 Aug 2023

@author: jacklok
'''
from trexconf import conf
import os, logging, csv
from trexlib.utils.common.common_util import sort_dict_list
from trexconf.conf import DEFAULT_CURRENCY_CODE, DEFAULT_CURRENCY_DISPLAY,\
    DEFAULT_CURRENCY_LABEL, DEFAULT_CURRENCY_FLOATING_POINT,\
    DEFAULT_CURRENCY_DECIMAL_SEPARATOR, DEFAULT_CURRENCY_THOUSAND_SEPARATOR

logger = logging.getLogger('util')

COUNTRY_CODE_FILEPATH                       = os.path.abspath(os.path.dirname(conf.__file__)) + '/data/countries.csv'
CURRENCY_CODE_FILEPATH                      = os.path.abspath(os.path.dirname(conf.__file__)) + '/data/currency.csv' 

ADMIN_PERMISSION_CODE_FILEPATH              = os.path.abspath(os.path.dirname(conf.__file__)) + '/data/admin_permission.csv'

MERCHANT_PERMISSION_CODE_FILEPATH           = os.path.abspath(os.path.dirname(conf.__file__)) + '/data/merchant_permission.csv'

REWARD_BASE_CODE_FILEPATH                   = os.path.abspath(os.path.dirname(conf.__file__)) + '/data/reward_base.csv'
REWARD_FORMAT_CODE_FILEPATH                 = os.path.abspath(os.path.dirname(conf.__file__)) + '/data/reward_format.csv'
REWARD_BASE_AND_FORMAT_MAPPING_FILEPATH     = os.path.abspath(os.path.dirname(conf.__file__)) + '/data/reward_base_and_reward_format_mapping.csv'
PROGRAM_STATUS_FILEPATH                     = os.path.abspath(os.path.dirname(conf.__file__)) + '/data/program_status.csv'
MERCHANT_NEWS_STATUS_FILEPATH               = os.path.abspath(os.path.dirname(conf.__file__)) + '/data/merchant_news_status.csv'

VOUCHER_STATUS_FILEPATH                     = os.path.abspath(os.path.dirname(conf.__file__)) + '/data/voucher_status.csv'
VOUCHER_TYPE_FILEPATH                       = os.path.abspath(os.path.dirname(conf.__file__)) + '/data/voucher_type.csv'

REDEMPTION_CATALOGUE_STATUS_FILEPATH        = os.path.abspath(os.path.dirname(conf.__file__)) + '/data/redemption_catalogue_status.csv'

REDEEM_LIMIT_TYPE_FILEPATH                  = os.path.abspath(os.path.dirname(conf.__file__)) + '/data/redeem_limit_type.csv'

REWARD_EFFECTIVE_TYPE_FILEPATH              = os.path.abspath(os.path.dirname(conf.__file__)) + '/data/reward_effective_type.csv'
REWARD_EXPIRATION_TYPE_FILEPATH             = os.path.abspath(os.path.dirname(conf.__file__)) + '/data/reward_expiration_type.csv'

REWARD_USE_CONDITION_FILEPATH               = os.path.abspath(os.path.dirname(conf.__file__)) + '/data/reward_use_condition.csv'
WEEKDAY_FILEPATH                            = os.path.abspath(os.path.dirname(conf.__file__)) + '/data/weekday.csv'

MEMBERSHIP_EXPIRATION_TYPE_FILEPATH         = os.path.abspath(os.path.dirname(conf.__file__)) + '/data/membership_expiration_type.csv'

MEMBERSHIP_ENTITLE_QUALIFICATION_TYPE_FILEPATH      = os.path.abspath(os.path.dirname(conf.__file__)) + '/data/membership_entitle_qualification_type.csv'  
MEMBERSHIP_UPGRADE_EXPIRY_TYPE_FILEPATH             = os.path.abspath(os.path.dirname(conf.__file__)) + '/data/membership_upgrade_expiry_type.csv'

GIVEAWAY_METHOD_FILEPATH                            = os.path.abspath(os.path.dirname(conf.__file__)) + '/data/giveaway_method.csv'
GIVEAWAY_SYSTEM_CONDITION_FILEPATH                  = os.path.abspath(os.path.dirname(conf.__file__)) + '/data/giveaway_system_condition.csv'

BARCODE_TYPE_FILEPATH                               = os.path.abspath(os.path.dirname(conf.__file__)) + '/data/barcode_type.csv'

BIRTHDAY_REWARD_GIVEAWAY_TYPE_FILEPATH              = os.path.abspath(os.path.dirname(conf.__file__)) + '/data/birthday_reward_giveaway_type.csv'

ENTITLE_REWARD_CONDITION_FILEPATH                   = os.path.abspath(os.path.dirname(conf.__file__)) + '/data/entitle_reward_condition.csv'

RUNNING_NO_GENERATOR_FILEPATH                       = os.path.abspath(os.path.dirname(conf.__file__)) + '/data/invoice_no_generator.csv'

RECEIPT_HEADER_DATA_TYPE_FILEPATH                   = os.path.abspath(os.path.dirname(conf.__file__)) + '/data/receipt_header_data_type.csv'

RECEIPT_FOOTER_DATA_TYPE_FILEPATH                   = os.path.abspath(os.path.dirname(conf.__file__)) + '/data/receipt_footer_data_type.csv'

PRODUCT_PACKAGE_FILEPATH                            = os.path.abspath(os.path.dirname(conf.__file__)) + '/data/product_package.csv'

LOYALTY_PACKAGE_FILEPATH                            = os.path.abspath(os.path.dirname(conf.__file__)) + '/data/loyalty_package.csv'

LOYALTY_PACKAGE_FEATURE_FILEPATH                    = os.path.abspath(os.path.dirname(conf.__file__)) + '/data/loyalty_package_feature.csv'

REDEEM_REWARD_FORMAT_CODE_FILEPATH                  = os.path.abspath(os.path.dirname(conf.__file__)) + '/data/redeem_reward_format.csv'

PUSH_NOTIFICATION_CONTENT_TYPE_CODE_FILEPATH        = os.path.abspath(os.path.dirname(conf.__file__)) + '/data/push_notification_content_type.csv'


DEFAULT_CURRENCY_JSON                           = {
                                                    "code": DEFAULT_CURRENCY_CODE,
                                                    "label": DEFAULT_CURRENCY_DISPLAY,
                                                    "currency_label": DEFAULT_CURRENCY_LABEL,
                                                    "floating_point": DEFAULT_CURRENCY_FLOATING_POINT,
                                                    "decimal_separator": DEFAULT_CURRENCY_DECIMAL_SEPARATOR,
                                                    "thousand_separator": DEFAULT_CURRENCY_THOUSAND_SEPARATOR,
                                                    }

def get_currency_json():
    data_list = []
    
    with open(CURRENCY_CODE_FILEPATH) as csv_file:
        logging.debug('Found currency data file')
        data        = csv.reader(csv_file, delimiter=',')
        first_line  = True
        
        
        
        for column in data:
            if not first_line:
                data_list.append({
                    "code": column[0],
                    "label": column[1],
                    "currency_label": column[2],
                    "floating_point": column[3],
                    "decimal_separator": column[4],
                    "thousand_separator": column[5],
                    })
            else:
                first_line = False
    
    return sort_dict_list(data_list, sort_attr_name='label')

def get_currency_config_by_currency_code(currency_code):
    currency_json_list = get_currency_json()
    
    logger.debug('currency_json_list=%s', currency_json_list)
    for currency_json in currency_json_list:
        if currency_json.get('code') == currency_code:
            return currency_json
    
    return DEFAULT_CURRENCY_JSON
