'''
Created on 19 Feb 2021

@author: jacklok
'''
#from orderedset import OrderedSet
#from trexlib.utils.common.common_util import OrderedSet

import os

IMAGE_BASE_URL                              = os.environ.get('IMAGE_BASE_URL')

POS_PRODUCT                                 = 'point_of_sales'
LOYALTY_PRODUCT                             = 'loyalty'

PRODUCT_TYPES                               = (POS_PRODUCT, LOYALTY_PRODUCT)

POS_PACKAGE_DEFAULT                         = 'lite'
POS_PACKAGE_STANDARD                        = 'standard'
POS_PACKAGE_SCALE                           = 'scale'


LOYALTY_PACKAGE_LITE                        = 'lite'
LOYALTY_PACKAGE_STANDARD                    = 'standard'
LOYALTY_PACKAGE_SCALE                       = 'scale'

FEATURE_CODE_POINT_REWARD_FORMAT            = 'point'
FEATURE_CODE_STAMP_REWARD_FORMAT            = 'stamp'
FEATURE_CODE_VOUCHER_REWARD_FORMAT          = 'voucher'
FEATURE_CODE_PREPAID_REWARD_FORMAT          = 'prepaid'

FEATURE_CODE_SPENDING_REWARD_BASE           = 'spending'
FEATURE_CODE_GIVEAWAY_REWARD_BASE           = 'giveaway'
FEATURE_CODE_BIRTHDAY_REWARD_BASE           = 'birthday'
FEATURE_CODE_REFER_REWARD_BASE              = 'refer'
FEATURE_CODE_PROMOTION_SPENDING_REWARD_BASE = 'promotion_spending'

FEATURE_CODE_BASIC_MEMBERSHIP               = 'basic_membership'
FEATURE_CODE_TIER_MEMBERSHIP                = 'tier_membership'


FEATURE_CODE_TIER_REWARD_PROGRAM            = 'tier_reward'

FEATURE_CODE_REWARDING_PROGRAM              = 'rewarding'
FEATURE_CODE_REDEMPTION_PROGRAM             = 'redemption'
FEATURE_CODE_LUCKY_DRAW_PROGRAM             = 'lucky_draw'
FEATURE_CODE_REFERRAL_PROGRAM               = 'referral'

PRODUCT_CODE_POINT_OF_SALES                 = 'pos'
PRODUCT_CODE_LOYALTY                        = 'loyalty'


REWARD_PROGRAM_DATE_FORMAT                  = '%d-%m-%Y'

PACKAGE_FEATURE_REWARD_FORMAT_MAP = {
                                       LOYALTY_PACKAGE_LITE:[
                                                FEATURE_CODE_POINT_REWARD_FORMAT,
                                                FEATURE_CODE_STAMP_REWARD_FORMAT,
                                                
                                                
                                                ],
                                       
                                       LOYALTY_PACKAGE_STANDARD:[
                                                FEATURE_CODE_POINT_REWARD_FORMAT,
                                                FEATURE_CODE_STAMP_REWARD_FORMAT,
                                                FEATURE_CODE_VOUCHER_REWARD_FORMAT,
                                                
                                                ],
                                       
                                       LOYALTY_PACKAGE_SCALE:[
                                                FEATURE_CODE_POINT_REWARD_FORMAT,
                                                FEATURE_CODE_STAMP_REWARD_FORMAT,
                                                FEATURE_CODE_VOUCHER_REWARD_FORMAT,
                                                FEATURE_CODE_PREPAID_REWARD_FORMAT,
                                                
                                                
                                                ],
                                       }

PACKAGE_FEATURE_REWARD_BASE_MAP = {
                                       LOYALTY_PACKAGE_LITE:[
                                                FEATURE_CODE_SPENDING_REWARD_BASE,
                                                
                                                ],
                                       
                                       LOYALTY_PACKAGE_STANDARD:[
                                                FEATURE_CODE_SPENDING_REWARD_BASE,
                                                FEATURE_CODE_BIRTHDAY_REWARD_BASE,
                                                FEATURE_CODE_PROMOTION_SPENDING_REWARD_BASE,
                                                #FEATURE_CODE_GIVEAWAY_REWARD_BASE,
                                                
                                                ],
                                       
                                       LOYALTY_PACKAGE_SCALE:[
                                                FEATURE_CODE_SPENDING_REWARD_BASE,
                                                FEATURE_CODE_BIRTHDAY_REWARD_BASE,
                                                FEATURE_CODE_PROMOTION_SPENDING_REWARD_BASE,
                                                FEATURE_CODE_GIVEAWAY_REWARD_BASE,
                                                
                                                
                                                
                                                ],
                                       
                                       }

PACKAGE_FEATURE_PROGRAM_MAP = {
                                       LOYALTY_PACKAGE_LITE:[
                                                FEATURE_CODE_REWARDING_PROGRAM,
                                                FEATURE_CODE_REDEMPTION_PROGRAM,
                                                ],
                                       
                                       LOYALTY_PACKAGE_STANDARD:[
                                                FEATURE_CODE_REWARDING_PROGRAM,
                                                FEATURE_CODE_REDEMPTION_PROGRAM,
                                                ],
                                       
                                       LOYALTY_PACKAGE_SCALE:[
                                                FEATURE_CODE_REWARDING_PROGRAM,
                                                FEATURE_CODE_REDEMPTION_PROGRAM,
                                                FEATURE_CODE_LUCKY_DRAW_PROGRAM,
                                                FEATURE_CODE_REFERRAL_PROGRAM,
                                                ],
                                       
                                       }

PACKAGE_FEATURE_MEMBERSHIP_MAP = {
                                       LOYALTY_PACKAGE_LITE:[
                                                FEATURE_CODE_BASIC_MEMBERSHIP,
                                                
                                                ],
                                       
                                       LOYALTY_PACKAGE_STANDARD:[
                                                FEATURE_CODE_BASIC_MEMBERSHIP,
                                                #FEATURE_CODE_TIER_MEMBERSHIP,
                                                ],
                                       
                                       LOYALTY_PACKAGE_SCALE:[
                                                FEATURE_CODE_BASIC_MEMBERSHIP,
                                                FEATURE_CODE_TIER_MEMBERSHIP,
                                                
                                                
                                                
                                                ],
                                       
                                       }



REWARD_BASE_ON_SPENDING                 = 'spending'
REWARD_BASE_ON_PROMOTION_SPENDING       = 'promotion_spending'
REWARD_BASE_ON_REFER                    = 'refer'
REWARD_BASE_ON_GIVEAWAY                 = 'giveaway'
REWARD_BASE_ON_BIRTHDAY                 = 'birthday'
REWARD_BASE_ON_TIER                     = 'tier'

REWARD_BASE_SET                         = (REWARD_BASE_ON_SPENDING, REWARD_BASE_ON_PROMOTION_SPENDING, REWARD_BASE_ON_GIVEAWAY, REWARD_BASE_ON_BIRTHDAY, REWARD_BASE_ON_REFER, REWARD_BASE_ON_TIER)

IMPORT_STATUS_NEW                       = 'new'
IMPORT_STATUS_READY                     = 'ready'
IMPORT_STATUS_COMPLETED                 = 'completed'
IMPORT_STATUS_FAILED                    = 'failed'

IMPORT_STATUS_SET                       = (IMPORT_STATUS_NEW,IMPORT_STATUS_READY,IMPORT_STATUS_COMPLETED)

FREQUENCY_AND_TIME_BASED_PROGRAM        = (REWARD_BASE_ON_SPENDING, REWARD_BASE_ON_PROMOTION_SPENDING)
SPENDING_BASED_PROGRAM                  = (REWARD_BASE_ON_SPENDING, REWARD_BASE_ON_PROMOTION_SPENDING)
SCHEME_BASED_PROGRAM                    = (REWARD_BASE_ON_SPENDING, REWARD_BASE_ON_PROMOTION_SPENDING)
SCHEDULE_BASED_PROGRAM                  = (REWARD_BASE_ON_GIVEAWAY, REWARD_BASE_ON_BIRTHDAY)

REWARD_FORMAT_POINT                     = 'point'
REWARD_FORMAT_STAMP                     = 'stamp'
REWARD_FORMAT_VOUCHER                   = 'voucher'
REWARD_FORMAT_DISCOUNT                  = 'discount'
REWARD_FORMAT_PREPAID                   = 'prepaid'
REWARD_FORMAT_MESSAGE                   = 'message'

REDEEM_REWARD_FORMAT_GROUP              = (REWARD_FORMAT_POINT, REWARD_FORMAT_STAMP)

REWARD_FORMAT_MAP = {
                REWARD_FORMAT_POINT: 'points',
                REWARD_FORMAT_STAMP: 'stamp',
                REWARD_FORMAT_PREPAID: 'prepaid',
    }

SALES_AMOUNT                            = 'sales_amount'

REWARD_FORMAT_SET                       = (REWARD_FORMAT_POINT, REWARD_FORMAT_STAMP, REWARD_FORMAT_VOUCHER, REWARD_FORMAT_PREPAID)
BASIC_TYPE_REWARD_FORMAT                = (REWARD_FORMAT_POINT, REWARD_FORMAT_STAMP, REWARD_FORMAT_VOUCHER)

SUPPORT_TIER_REWARD_PROGRAM_CONDITION_REWARD_FORMAT = (REWARD_FORMAT_POINT, REWARD_FORMAT_STAMP)

ENTITLE_REWARD_CONDITION_ACCUMULATE_POINT           = 'acc_point'
ENTITLE_REWARD_CONDITION_ACCUMULATE_STAMP           = 'acc_stamp'
ENTITLE_REWARD_CONDITION_ACCUMULATE_SALES_AMOUNT    = 'acc_sales'

ENTITLE_REWARD_CONDITION_ACCUMULATE_TYPES           = (ENTITLE_REWARD_CONDITION_ACCUMULATE_POINT, ENTITLE_REWARD_CONDITION_ACCUMULATE_STAMP, ENTITLE_REWARD_CONDITION_ACCUMULATE_SALES_AMOUNT)

PROGRAM_STATUS_PROGRAM_BASE             = 'program_base'
PROGRAM_STATUS_REWARD_SCHEME            = 'reward_scheme'
PROGRAM_STATUS_REWARD_DETAILS           = 'reward_details'
PROGRAM_STATUS_DEFINE_TIER              = 'define_program_tier'
PROGRAM_STATUS_DEFINE_REWARD            = 'define_reward'
PROGRAM_STATUS_DEFINE_CONDITION         = 'define_condition'
PROGRAM_STATUS_UPLOAD_TICKET_IMAGE      = 'upload_material'
PROGRAM_STATUS_UPLOAD_MATERIAL          = 'upload_material'
PROGRAM_STATUS_DEFINE_PRIZE             = 'define_prize'
PROGRAM_STATUS_DEFINE_PRIZE_POSSIBILITY = 'define_prize_possibility'
PROGRAM_STATUS_EXCLUSIVITY              = 'exclusivity'
PROGRAM_STATUS_REVIEW                   = 'review'
PROGRAM_STATUS_PUBLISH                  = 'published'
PROGRAM_STATUS_DEFINE_ITEM              = 'define_item'
PROGRAM_STATUS_DEFINE_PROMOTE_TEXT      = 'define_promote_text'

PROGRAM_STATUS_DEFINE_REFERRER_REWARD   = 'define_program_referrer_reward'
PROGRAM_STATUS_DEFINE_REFEREE_REWARD    = 'define_program_referee_reward'

ACTION_AFTER_UNLOCK_TIER_NO_ACTION          = 'no_action'
ACTION_AFTER_UNLOCK_TIER_CONSUME_REWARD     = 'consume_reward'


PROGRAM_REWARD_GIVEAWAY_METHOD_AUTO         = 'auto'
PROGRAM_REWARD_GIVEAWAY_METHOD_MANUAL       = 'manual'
PROGRAM_REWARD_GIVEAWAY_METHOD_SYSTEM       = 'system'
PROGRAM_REWARD_GIVEAWAY_METHOD_TIER         = 'tier'
PROGRAM_REWARD_GIVEAWAY_METHOD_REDEEM       = 'redeem'
PROGRAM_REWARD_GIVEAWAY_METHOD_REFERRAL     = 'referral'
PROGRAM_REWARD_GIVEAWAY_METHOD_PARTNERSHIP  = 'partnership'

GIVEAWAY_SYSTEM_CONDITION_NEW_MEMBERSHIP        = 'new_membership'
GIVEAWAY_SYSTEM_CONDITION_RENEW_MEMBERSHIP      = 'renew_membership'
GIVEAWAY_SYSTEM_CONDITION_MEMBERSHIP_YEAR       = 'membership_year'
GIVEAWAY_SYSTEM_CONDITION_DATA_IMPORT           = 'data_import'

GIVEAWAY_SYSTEM_CONDITION_FOR_MEMBERSHIP        = (GIVEAWAY_SYSTEM_CONDITION_NEW_MEMBERSHIP, GIVEAWAY_SYSTEM_CONDITION_RENEW_MEMBERSHIP)

MERCHANT_PARTNERSHIP_STATUS_LINKED              = 'linked'
MERCHANT_PARTNERSHIP_STATUS_REDEEM_CONFIGURED   = 'redeem_configured'
MERCHANT_PARTNERSHIP_STATUS_LIMIT_CONFIGURED    = 'limit_configured'
MERCHANT_PARTNERSHIP_STATUS_REVIEWED            = 'reviewed'
MERCHANT_PARTNERSHIP_STATUS_REQUESTED           = 'requested'
MERCHANT_PARTNERSHIP_STATUS_APPROVED            = 'approved'
MERCHANT_PARTNERSHIP_STATUS_DISABLED            = 'disabled'

'''
BASIC_REWARD_PROGRAM_STATUS                          = OrderedSet([PROGRAM_STATUS_PROGRAM_BASE, 
                                                                  PROGRAM_STATUS_REWARD_SCHEME, 
                                                                  PROGRAM_STATUS_EXCLUSIVITY,
                                                                  PROGRAM_STATUS_PUBLISH
                                                                  ])

TIER_REWARD_PROGRAM_STATUS                          = OrderedSet([PROGRAM_STATUS_PROGRAM_BASE, 
                                                                  PROGRAM_STATUS_DEFINE_TIER, 
                                                                  PROGRAM_STATUS_DEFINE_REWARD,
                                                                  PROGRAM_STATUS_EXCLUSIVITY,
                                                                  PROGRAM_STATUS_PUBLISH,
                                                                  ])
'''

BASIC_REWARD_PROGRAM_STATUS                          = [PROGRAM_STATUS_PROGRAM_BASE, 
                                                                  PROGRAM_STATUS_REWARD_SCHEME, 
                                                                  PROGRAM_STATUS_EXCLUSIVITY,
                                                                  PROGRAM_STATUS_REVIEW,
                                                                  PROGRAM_STATUS_PUBLISH
                                                                  ]

REFERRAL_REWARD_PROGRAM_STATUS                          = [PROGRAM_STATUS_PROGRAM_BASE, 
                                                                  PROGRAM_STATUS_DEFINE_REFERRER_REWARD, 
                                                                  PROGRAM_STATUS_DEFINE_REFEREE_REWARD,
                                                                  PROGRAM_STATUS_REVIEW,
                                                                  PROGRAM_STATUS_PUBLISH
                                                                  ]


LITE_BASIC_REWARD_PROGRAM_STATUS                     = [PROGRAM_STATUS_PROGRAM_BASE, 
                                                                  PROGRAM_STATUS_REWARD_SCHEME, 
                                                                  PROGRAM_STATUS_REVIEW,
                                                                  PROGRAM_STATUS_PUBLISH
                                                                  ]

TIER_REWARD_PROGRAM_STATUS                          = [PROGRAM_STATUS_PROGRAM_BASE, 
                                                                  PROGRAM_STATUS_DEFINE_TIER, 
                                                                  PROGRAM_STATUS_DEFINE_REWARD,
                                                                  PROGRAM_STATUS_EXCLUSIVITY,
                                                                  PROGRAM_STATUS_REVIEW,
                                                                  PROGRAM_STATUS_PUBLISH,
                                                                  ]

LUCKY_DRAW_PROGRAM_STATUS                          = [
                                                                  PROGRAM_STATUS_PROGRAM_BASE, 
                                                                  #PROGRAM_STATUS_DEFINE_CONDITION,
                                                                  PROGRAM_STATUS_DEFINE_PRIZE,
                                                                  PROGRAM_STATUS_DEFINE_PRIZE_POSSIBILITY,
                                                                  PROGRAM_STATUS_EXCLUSIVITY,
                                                                  PROGRAM_STATUS_UPLOAD_TICKET_IMAGE,  
                                                                  PROGRAM_STATUS_PUBLISH,
                                                                  ]

REFERRAL_PROGRAM_STATUS                            = [PROGRAM_STATUS_PROGRAM_BASE, 
                                                                  PROGRAM_STATUS_DEFINE_REFERRER_REWARD, 
                                                                  PROGRAM_STATUS_DEFINE_REFEREE_REWARD,
                                                                  #PROGRAM_STATUS_DEFINE_PROMOTE_TEXT,
                                                                  #PROGRAM_STATUS_UPLOAD_MATERIAL,
                                                                  #PROGRAM_STATUS_REVIEW,
                                                                  PROGRAM_STATUS_PUBLISH,
                                                                  ]

MERCHANT_PARTNERSHIP_STATUS                          = [MERCHANT_PARTNERSHIP_STATUS_LINKED, 
                                                                  MERCHANT_PARTNERSHIP_STATUS_REDEEM_CONFIGURED,
                                                                  MERCHANT_PARTNERSHIP_STATUS_LIMIT_CONFIGURED,
                                                                  MERCHANT_PARTNERSHIP_STATUS_REVIEWED,
                                                                  MERCHANT_PARTNERSHIP_STATUS_REQUESTED,
                                                                  MERCHANT_PARTNERSHIP_STATUS_APPROVED,
                                                                  ]

ALL_PROGRAM_STATUS                            = (PROGRAM_STATUS_PROGRAM_BASE,
                                                 PROGRAM_STATUS_REWARD_SCHEME,
                                                 PROGRAM_STATUS_DEFINE_TIER,
                                                 PROGRAM_STATUS_DEFINE_REWARD,
                                                 PROGRAM_STATUS_EXCLUSIVITY,
                                                 PROGRAM_STATUS_REVIEW,
                                                 PROGRAM_STATUS_PUBLISH,
                                                 )

REDEMPTION_CATALOGUE_STATUS_NEW                     = 'new'
REDEMPTION_CATALOGUE_STATUS_DEFINED_CATALOGUE       = 'define_catalogue'
REDEMPTION_CATALOGUE_STATUS_DEFINE_ITEM             = 'define_item'
REDEMPTION_CATALOGUE_STATUS_UPLOAD_MATERIAL         = 'upload_material'
REDEMPTION_CATALOGUE_STATUS_DEFINE_EXCLUSIVITY      = 'define_exclusivity'
REDEMPTION_CATALOGUE_STATUS_REVIEW                  = 'review'
REDEMPTION_CATALOGUE_STATUS_PUBLISH                 = 'published'


REDEMPTION_CATALOGUE_STATUS                   = (
                                                 REDEMPTION_CATALOGUE_STATUS_NEW,
                                                 REDEMPTION_CATALOGUE_STATUS_DEFINED_CATALOGUE,
                                                 REDEMPTION_CATALOGUE_STATUS_DEFINE_ITEM,
                                                 REDEMPTION_CATALOGUE_STATUS_UPLOAD_MATERIAL,
                                                 REDEMPTION_CATALOGUE_STATUS_DEFINE_EXCLUSIVITY,
                                                 REDEMPTION_CATALOGUE_STATUS_REVIEW,
                                                 REDEMPTION_CATALOGUE_STATUS_PUBLISH
                                                 )

LITE_REDEMPTION_CATALOGUE_STATUS                   = (
                                                 REDEMPTION_CATALOGUE_STATUS_DEFINED_CATALOGUE,
                                                 REDEMPTION_CATALOGUE_STATUS_DEFINE_ITEM,
                                                 REDEMPTION_CATALOGUE_STATUS_UPLOAD_MATERIAL,
                                                 REDEMPTION_CATALOGUE_STATUS_REVIEW,
                                                 REDEMPTION_CATALOGUE_STATUS_PUBLISH
                                                 )



PROGRAM_SCHEDULE_TYPE_DAILY             = 'daily'
PROGRAM_SCHEDULE_TYPE_MONTH_START       = 'month_start'
PROGRAM_SCHEDULE_TYPE_WEEKEND           = 'weekend'
PROGRAM_SCHEDULE_TYPE_FRIDAY            = 'friday'
PROGRAM_SCHEDULE_TYPE_MONDAY            = 'monday'

PROGRAM_SCHEDULE_TYPE_GROUP             = (PROGRAM_SCHEDULE_TYPE_DAILY, PROGRAM_SCHEDULE_TYPE_MONTH_START, PROGRAM_SCHEDULE_TYPE_WEEKEND, PROGRAM_SCHEDULE_TYPE_FRIDAY, PROGRAM_SCHEDULE_TYPE_MONDAY)

VOUCHER_STATUS_BASE                     = 'voucher_base'
VOUCHER_STATUS_CONFIGURATION            = 'voucher_configuration'
VOUCHER_STATUS_UPLOAD_MATERIAL          = 'upload_material'
VOUCHER_STATUS_PUBLISH                  = 'published'

MERCHANT_NEWS_STATUS_BASE                     = 'news_base'
MERCHANT_NEWS_STATUS_UPLOAD_MATERIAL          = 'upload_material'
MERCHANT_NEWS_STATUS_PUBLISH                  = 'published'

VOUCHER_STATUS                          = [VOUCHER_STATUS_BASE, 
                                              VOUCHER_STATUS_CONFIGURATION,
                                              VOUCHER_STATUS_UPLOAD_MATERIAL, 
                                              VOUCHER_STATUS_PUBLISH
                                              ]

MERCHANT_NEWS_STATUS                          = [MERCHANT_NEWS_STATUS_BASE, 
                                              MERCHANT_NEWS_STATUS_UPLOAD_MATERIAL, 
                                              MERCHANT_NEWS_STATUS_PUBLISH
                                              ]

VOUCHER_REWARD_TYPE                          = 'type'
VOUCHER_REWARD_ACTION_DATA                   = 'action_data'
VOUCHER_REWARD_CASH                          = 'cash'
VOUCHER_REWARD_PRODUCT_CATEGORY              = 'category'
VOUCHER_REWARD_PRODUCT_SKU                   = 'SKU'
VOUCHER_REWARD_MIN_SALES_AMOUNT              = 'min_sales_amount'
VOUCHER_REWARD_DISCOUNT_RATE                 = 'discount_rate'
VOUCHER_REWARD_BRAND                         = 'brand'
VOUCHER_REWARD_PRICE                         = 'price'
VOUCHER_REWARD_MAX_QUANTITY                  = 'max_quantity'

VOUCHER_REWARD_TYPE_CASH                     = 'cash' 
VOUCHER_REWARD_TYPE_PRODUCT                  = 'product'
VOUCHER_REWARD_TYPE_DISCOUNT                 = 'discount'
   
VOUCHER_TYPE                                 = [
                                                VOUCHER_REWARD_TYPE_CASH,
                                                VOUCHER_REWARD_TYPE_PRODUCT,
                                                VOUCHER_REWARD_TYPE_DISCOUNT,
                                                ]

PRORRAM_NEXT_STEP_AND_COMPLELTED_STATUS_MAPPING = {
                                                    PROGRAM_STATUS_PROGRAM_BASE: 2
                                                    }


REWARD_EFFECTIVE_TYPE_IMMEDIATE         = 'immediate'
REWARD_EFFECTIVE_TYPE_SPECIFIC_DATE     = 'date'
REWARD_EFFECTIVE_TYPE_AFTER_MONTH       = 'month'
REWARD_EFFECTIVE_TYPE_AFTER_WEEK        = 'week'
REWARD_EFFECTIVE_TYPE_AFTER_DAY         = 'day'


REWARD_EXPIRATION_TYPE_SPECIFIC_DATE     = 'date'
REWARD_EXPIRATION_TYPE_AFTER_YEAR        = 'year'
REWARD_EXPIRATION_TYPE_AFTER_MONTH       = 'month'
REWARD_EXPIRATION_TYPE_AFTER_WEEK        = 'week'
REWARD_EXPIRATION_TYPE_AFTER_DAY         = 'day'
REWARD_EXPIRATION_TYPE_END_OF_MONTH      = 'eom'

FIRST_DAY_OF_MONTH                       = 'month_start'
ON_DOB_DATE                              = 'dob_date'
ADVANCE_IN_DAY                           = 'advance_in_day'

REWARD_LIMIT_TYPE_NO_LIMIT                  = 'no_limit'
REWARD_LIMIT_TYPE_BY_MONTH                  = 'limit_by_month'
REWARD_LIMIT_TYPE_BY_WEEK                   = 'limit_by_week'
REWARD_LIMIT_TYPE_BY_DAY                    = 'limit_by_day'
REWARD_LIMIT_TYPE_BY_TRANSACTION            = 'limit_by_transaction'

MEMBERSHIP_EXPIRATION_TYPE_AFTER_YEAR       = 'year'
MEMBERSHIP_EXPIRATION_TYPE_AFTER_MONTH      = 'month'
MEMBERSHIP_EXPIRATION_TYPE_AFTER_WEEK       = 'week'
MEMBERSHIP_EXPIRATION_TYPE_AFTER_DAY        = 'day'
MEMBERSHIP_EXPIRATION_TYPE_SPECIFIC_DATE    = 'date'
MEMBERSHIP_EXPIRATION_TYPE_NO_EXPIRY        = 'no_expiry'

MEMBERSHIP_EFFECTIVE_TYPE_IMMEDIATE         = 'immediate'
MEMBERSHIP_EFFECTIVE_TYPE_SPECIFIC_DATE     = 'date'
MEMBERSHIP_EFFECTIVE_TYPE_AFTER_DAY         = 'day'

MEMBERSHIP_ENTITLE_QUALIFICATION_TYPE_AUTO_ASSIGN                    = 'auto'
MEMBERSHIP_ENTITLE_QUALIFICATION_TYPE_ACCUMULATED_SPENDING_AMOUNT    = 'acc_spending'
MEMBERSHIP_ENTITLE_QUALIFICATION_TYPE_ACCUMULATED_POINT_AMOUNT       = 'acc_point'
MEMBERSHIP_ENTITLE_QUALIFICATION_TYPE_ACCUMULATED_STAMP_AMOUNT       = 'acc_stamp'
MEMBERSHIP_ENTITLE_QUALIFICATION_TYPE_ACCUMULATED_PREPAID_AMOUNT     = 'acc_prepaid'
MEMBERSHIP_ENTITLE_QUALIFICATION_TYPE_EXCEED_SPENDING_AMOUNT         = 'exceed_spending'
MEMBERSHIP_ENTITLE_QUALIFICATION_TYPE_EXCEED_PREPAID_AMOUNT          = 'exceed_prepaid'

MEMBERSHIP_REQUIRED_ENTITLE_QUALIFICATION_VALUE = (
                                                    MEMBERSHIP_ENTITLE_QUALIFICATION_TYPE_ACCUMULATED_SPENDING_AMOUNT, 
                                                    MEMBERSHIP_ENTITLE_QUALIFICATION_TYPE_ACCUMULATED_POINT_AMOUNT,
                                                    MEMBERSHIP_ENTITLE_QUALIFICATION_TYPE_ACCUMULATED_STAMP_AMOUNT,
                                                    MEMBERSHIP_ENTITLE_QUALIFICATION_TYPE_ACCUMULATED_PREPAID_AMOUNT,
                                                    MEMBERSHIP_ENTITLE_QUALIFICATION_TYPE_EXCEED_SPENDING_AMOUNT,
                                                    MEMBERSHIP_ENTITLE_QUALIFICATION_TYPE_EXCEED_PREPAID_AMOUNT
                                                   )


MEMBERSHIP_UPGRADE_EXPIRY_TYPE_CONTINUE_EXPIRY                      = 'cont_expiry'
MEMBERSHIP_UPGRADE_EXPIRY_TYPE_NEW_EXPIRY                           = 'new_expiry'


GIVEAWAY_ON_FIRST_DAY_OF_MONTH  = 'month_start'
GIVEAWAY_ON_DOB                 = 'dob_date'
GIVEAWAY_IN_ADVANCE             = 'advance_in_day'

REWARD_STATUS_VALID        = 'valid'
REWARD_STATUS_REACH_LIMIT  = 'limit'
REWARD_STATUS_REDEEMED     = 'redeemed'
REWARD_STATUS_REVERTED     = 'reverted'
REWARD_STATUS_REMOVED      = 'removed'

REDEEM_STATUS_VALID        = 'valid'
REDEEM_STATUS_REVERTED     = 'reverted'

TIER_MEMBERSHIP_STATUS_ACTIVE           = 'active'
TIER_MEMBERSHIP_STATUS_UPGRADED         = 'upgraded'

REDEEM_LIMIT_TYPE_PER_DAY       = 'day'
REDEEM_LIMIT_TYPE_PER_WEEK      = 'week'
REDEEM_LIMIT_TYPE_PER_MONTH     = 'month'
REDEEM_LIMIT_TYPE_PER_RECEIPT   = 'receipt'

REDEEM_CODE_LENGTH                                                  = 12

MAX_REWARD_AMOUNT           = 999999999

def get_program_completed_status_index(completed_status):
    return BASIC_REWARD_PROGRAM_STATUS.index(completed_status)

def get_voucher_completed_status_index(completed_status):
    return VOUCHER_STATUS.index(completed_status)

def get_merchant_news_completed_status_index(completed_status):
    return MERCHANT_NEWS_STATUS.index(completed_status) 

def get_tier_reward_program_completed_status_index(completed_status):
    return TIER_REWARD_PROGRAM_STATUS.index(completed_status)

def get_lucky_draw_program_completed_status_index(completed_status):
    return LUCKY_DRAW_PROGRAM_STATUS.index(completed_status)

def get_redemption_catalogue_completed_status_index(completed_status):
    return REDEMPTION_CATALOGUE_STATUS.index(completed_status)

def get_referral_program_completed_status_index(completed_status):
    return REFERRAL_PROGRAM_STATUS.index(completed_status)

def get_partnership_completed_status_index(completed_status):
    return MERCHANT_PARTNERSHIP_STATUS.index(completed_status)

def is_program_current_status_reach(checking_status, completed_status):
    completed_status_index  = get_program_completed_status_index(completed_status)
    checking_status_index   = get_program_completed_status_index(checking_status)
    
    print('completed_status_index=%s'%completed_status_index)
    print('checking_status_index=%s'%checking_status_index)
    
    return checking_status_index<=completed_status_index+1

def is_referral_program_current_status_reach(checking_status, completed_status):
    completed_status_index  = get_referral_program_completed_status_index(completed_status)
    checking_status_index   = get_referral_program_completed_status_index(checking_status)
    
    print('completed_status_index=%s'%completed_status_index)
    print('checking_status_index=%s'%checking_status_index)
    
    return checking_status_index<=completed_status_index+1

def is_voucher_current_status_reach(checking_status, completed_status):
    completed_status_index  = get_voucher_completed_status_index(completed_status)
    checking_status_index   = get_voucher_completed_status_index(checking_status)
    
    print('completed_status_index=%s'%completed_status_index)
    print('checking_status_index=%s'%checking_status_index)
    
    return checking_status_index<=completed_status_index+1

def is_tier_reward_program_current_status_reach(checking_status, completed_status):
    completed_status_index  = get_tier_reward_program_completed_status_index(completed_status)
    checking_status_index   = get_tier_reward_program_completed_status_index(checking_status)
    
    print('completed_status_index=%s'%completed_status_index)
    print('checking_status_index=%s'%checking_status_index)
    
    return checking_status_index<=completed_status_index+1

def is_lucky_draw_program_current_status_reach(checking_status, completed_status):
    completed_status_index  = get_lucky_draw_program_completed_status_index(completed_status)
    checking_status_index   = get_lucky_draw_program_completed_status_index(checking_status)
    
    print('completed_status_index=%s'%completed_status_index)
    print('checking_status_index=%s'%checking_status_index)
    
    return checking_status_index<=completed_status_index+1

def is_merchant_news_current_status_reach(checking_status, completed_status):
    completed_status_index  = get_merchant_news_completed_status_index(completed_status)
    checking_status_index   = get_merchant_news_completed_status_index(checking_status)
    
    print('completed_status_index=%s'%completed_status_index)
    print('checking_status_index=%s'%checking_status_index)
    
    return checking_status_index<=completed_status_index+1

def is_valid_to_update_program_status(checking_status, completed_status):
    completed_status_index  = get_program_completed_status_index(completed_status)
    checking_status_index   = get_program_completed_status_index(checking_status)
    
    return checking_status_index<=completed_status_index+1

def is_valid_to_update_referral_program_status(checking_status, completed_status):
    completed_status_index  = get_referral_program_completed_status_index(completed_status)
    checking_status_index   = get_referral_program_completed_status_index(checking_status)
    
    return checking_status_index<=completed_status_index+1

def is_valid_to_update_voucher_status(checking_status, completed_status):
    completed_status_index  = get_voucher_completed_status_index(completed_status)
    checking_status_index   = get_voucher_completed_status_index(checking_status)
    
    return checking_status_index<=completed_status_index+1


def is_valid_to_update_tier_reward_program_status(checking_status, completed_status):
    completed_status_index  = get_tier_reward_program_completed_status_index(completed_status)
    checking_status_index   = get_tier_reward_program_completed_status_index(checking_status)
    
    return checking_status_index<=completed_status_index+1

def is_existing_program_status_higher_than_updating_status(checking_status, completed_status):
    completed_status_index  = get_program_completed_status_index(completed_status)
    checking_status_index   = get_program_completed_status_index(checking_status)
    
    return checking_status_index<completed_status_index

def is_existing_voucher_status_higher_than_updating_status(checking_status, completed_status):
    completed_status_index  = get_voucher_completed_status_index(completed_status)
    checking_status_index   = get_voucher_completed_status_index(checking_status)
    
    return checking_status_index<completed_status_index

def is_existing_program_status_final_state(completed_status):
    completed_status_index  = get_program_completed_status_index(completed_status)
    
    return completed_status_index==len(BASIC_REWARD_PROGRAM_STATUS)-1

def is_existing_referral_program_status_final_state(completed_status):
    completed_status_index  = get_referral_program_completed_status_index(completed_status)
    
    return completed_status_index==len(BASIC_REWARD_PROGRAM_STATUS)-1

def is_existing_tier_reward_program_status_final_state(completed_status):
    completed_status_index  = get_tier_reward_program_completed_status_index(completed_status)
    
    return completed_status_index==len(TIER_REWARD_PROGRAM_STATUS)-1

def is_existing_voucher_status_final_state(completed_status):
    completed_status_index  = get_voucher_completed_status_index(completed_status)
    
    return completed_status_index==len(BASIC_REWARD_PROGRAM_STATUS)-1

def program_completed_progress_percentage(completed_status, loyalty_package):
    completed_status_index  = get_program_completed_status_index(completed_status)
    print('program_completed_progress_percentage: completed_status_index(%s)=%s'% (completed_status,completed_status_index))
    if loyalty_package == LOYALTY_PACKAGE_LITE:
        return int((completed_status_index+1)/len(LITE_BASIC_REWARD_PROGRAM_STATUS) * 100)
    else:    
        return int((completed_status_index+1)/len(BASIC_REWARD_PROGRAM_STATUS) * 100)

def merchant_news_completed_progress_percentage(completed_status):
    completed_status_index  = get_merchant_news_completed_status_index(completed_status)
    print('merchant_news_completed_progress_percentage: completed_status_index(%s)=%s'% (completed_status,completed_status_index))
    return int((completed_status_index+1)/len(MERCHANT_NEWS_STATUS) * 100)

def tier_reward_program_completed_progress_percentage(completed_status):
    completed_status_index  = get_tier_reward_program_completed_status_index(completed_status)
    print('tier_reward_program_completed_progress_percentage: completed_status_index(%s)=%s'% (completed_status,completed_status_index))
    return int((completed_status_index+1)/len(TIER_REWARD_PROGRAM_STATUS) * 100)    

def lucky_draw_program_completed_progress_percentage(completed_status):
    completed_status_index  = get_lucky_draw_program_completed_status_index(completed_status)
    print('lucky_draw_program_completed_progress_percentage: completed_status_index(%s)=%s'% (completed_status,completed_status_index))
    return int((completed_status_index+1)/len(LUCKY_DRAW_PROGRAM_STATUS) * 100)
    
def redemption_catalogue_completed_progress_percentage(completed_status, loyalty_package):
    completed_status_index  = get_redemption_catalogue_completed_status_index(completed_status)
    print('redemption_catalogue_completed_progress_percentage: completed_status_index(%s)=%s'% (completed_status,completed_status_index))
    if loyalty_package == LOYALTY_PACKAGE_LITE:
        return int((completed_status_index+1)/len(LITE_REDEMPTION_CATALOGUE_STATUS) * 100)
    else:
        return int((completed_status_index+1)/len(REDEMPTION_CATALOGUE_STATUS) * 100)

def referral_program_completed_progress_percentage(completed_status):
    completed_status_index  = get_referral_program_completed_status_index(completed_status)
    print('referral_program_completed_progress_percentage: completed_status_index(%s)=%s'% (completed_status,completed_status_index))
    return int((completed_status_index+1)/len(REFERRAL_PROGRAM_STATUS) * 100)

def is_partnership_current_status_reach(checking_status, completed_status):
    completed_status_index  = get_partnership_completed_status_index(completed_status)
    checking_status_index   = get_partnership_completed_status_index(checking_status)
    
    print('completed_status_index=%s'%completed_status_index)
    print('checking_status_index=%s'%checking_status_index)
    
    return checking_status_index<completed_status_index+1
