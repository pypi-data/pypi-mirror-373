'''
Created on 26 Jan 2021

@author: jacklok
'''
from trexconf.conf import UPSTREAM_UPDATED_DATETIME_FIELD_NAME, MERCHANT_DATASET, SYSTEM_DATASET
import uuid, logging  
from trexmodel.models.datastore.analytic_models import UpstreamData
from trexanalytics.bigquery_table_template_config import REGISTERED_CUSTOMER_TEMPLATE, REGISTERED_MERCHANT_TEMPLATE, MERCHANT_REGISTERED_CUSTOMER_TEMPLATE,\
    CUSTOMER_TRANSACTION_TEMPLATE, MERCHANT_CUSTOMER_REWARD_TEMPLATE,\
    MERCHANT_CUSTOMER_REDEMPTION_TEMPLATE, MERCHANT_CUSTOMER_PREPAID_TEMPLATE,\
    CUSTOMER_MEMBERSHIP_TEMPLATE, USER_VOUCHER_ENTITLED_TEMPLATE,\
    USER_VOUCHER_REDEEMED_TEMPLATE, USER_VOUCHER_REMOVED_TEMPLATE,\
    USER_VOUCHER_ENTITLED_REVERTED_TEMPLATE,\
    USER_VOUCHER_REDEEMED_REVERTED_TEMPLATE,\
    PARTNERSHIP_REWARD_TRANSACTION_TEMPLATE, SALES_TRANSACTION_TEMPLATE,\
    TESTING_TEMPLATE 
from trexlib.utils.google.bigquery_util import default_serializable
from datetime import datetime
from trexmodel.models.datastore.transaction_models import CustomerTransactionWithRewardDetails,\
    CustomerTransactionWithPrepaidDetails
from trexmodel.models.datastore.ndb_models import convert_to_serializable_value
from trexmodel import program_conf 
from trexlib.utils.log_util import get_tracelog

__REGISTERED_MERCHANT_TEMPLATE_UPSTREAM_SCHEMA = { 
                                                'MerchantKey'           : 'key_in_str',
                                                'CompanyName'           : 'company_name',
                                                'RegisteredDateTime'    : 'registered_datetime',
                                            }

__REGISTERED_CUSTOMER_TEMPLATE_UPSTREAM_SCHEMA = {
                                                'UserKey'           : 'registered_user_acct_key',
                                                'CustomerKey'       : 'key_in_str',
                                                'MerchantKey'       : 'registered_merchant_acct_key',
                                                'DOB'               : 'birth_date',
                                                'Gender'            : 'gender',
                                                'MobilePhone'       : 'mobile_phone',
                                                'Email'             : 'email',
                                                'MobileAppInstall'  : 'mobile_app_installed',
                                                'RegisteredDateTime': 'registered_datetime',
                                                'RegisteredOutlet'  : 'registered_outlet_key',
                                                }

__CUSTOMER_MEMBERSHIP_TEMPLATE_UPSTREAM_SCHEMA = {
                                                'CustomerKey'       : 'customer_key',
                                                'MembershipKey'     : 'merchant_membership_key',
                                                'EntitledDateTime'  : 'entitled_datetime',
                                                'ExpiredDate'       : 'expiry_date',
                                                }

__MERCHANT_REGISTERED_CUSTOMER_TEMPLATE_UPSTREAM_SCHEMA = {
                                                        'UserKey'           : 'registered_user_acct_key',
                                                        'CustomerKey'       : 'key_in_str',
                                                        'DOB'               : 'birth_date',
                                                        'Gender'            : 'gender',
                                                        'MobilePhone'       : 'mobile_phone',
                                                        'Email'             : 'email',
                                                        'MobileAppInstall'  : 'mobile_app_installed',
                                                        'RegisteredDateTime': 'registered_datetime',
                                                        'RegisteredOutlet'  : 'registered_outlet_key',
                                                        }


__CUSTOMER_TRANSACTION_DATA_TEMPLATE_UPSTREAM_SCHEMA = {
                                            "UserKey"               : 'transact_by_user_acct_key',
                                            "CustomerKey"           : 'transact_customer_key',
                                            "MerchantKey"           : 'transact_merchant_acct_key',
                                            "TransactOutlet"        : 'transact_outlet_key',
                                            "TransactionId"         : 'transaction_id',
                                            "InvoiceId"             : 'invoice_id',
                                            "TransactAmount"        : 'transact_amount',
                                            "TransactDateTime"      : 'transact_datetime',
                                            "IsSalesTransaction"    : 'is_sales_transaction',
                                            "Reverted"              : 'is_revert',
                                            "RevertedDateTime"      : 'reverted_datetime',
                                            }

__SALES_TRANSACTION_DATA_TEMPLATE_UPSTREAM_SCHEMA = {
                                            "MerchantKey"           : 'transact_merchant_acct_key',
                                            "TransactOutlet"        : 'transact_outlet_key',
                                            "TransactionId"         : 'transaction_id',
                                            "InvoiceId"             : 'invoice_id',
                                            "TransactAmount"        : 'transact_amount',
                                            "TransactDateTime"      : 'transact_datetime',
                                            "Reverted"              : 'is_revert',
                                            "RevertedDateTime"      : 'reverted_datetime',
                                            }

__CUSTOMER_REWARD_DATA_TEMPLATE_UPSTREAM_SCHEMA = {
                                            "CustomerKey"           : 'transact_customer_key',
                                            "MerchantKey"           : 'transact_merchant_acct_key',
                                            "TransactOutlet"        : 'transact_outlet_key',
                                            "TransactionId"         : 'transaction_id',
                                            "TransactAmount"        : 'transact_amount',
                                            "TransactDateTime"      : 'transact_datetime',
                                            "RewardFormat"          : 'reward_format',
                                            "RewardAmount"          : 'reward_amount',
                                            "ExpiryDate"            : 'expiry_date',
                                            "RewardFormatKey"       : 'reward_format_key',
                                            "RewardedDateTime"      : 'rewarded_datetime',
                                            "Reverted"              : 'is_revert',
                                            "RevertedDateTime"      : 'reverted_datetime',
                                            }

__CUSTOMER_PREPAID_DATA_TEMPLATE_UPSTREAM_SCHEMA = {
                                            "CustomerKey"           : 'transact_customer_key',
                                            "MerchantKey"           : 'transact_merchant_acct_key',
                                            "TransactOutlet"        : 'transact_outlet_key',
                                            "TransactionId"         : 'transaction_id',
                                            "TransactAmount"        : 'transact_amount',
                                            "TransactDateTime"      : 'transact_datetime',
                                            "TopupAmount"           : 'topup_amount',
                                            "PrepaidAmount"         : 'prepaid_amount',
                                            "TopupDateTime"         : 'topup_datetime',
                                            "Reverted"              : 'is_revert',
                                            "RevertedDateTime"      : 'reverted_datetime',
                                            }

__CUSTOMER_REDEMPTION_DATA_TEMPLATE_UPSTREAM_SCHEMA = {
                                            "CustomerKey"           : 'customer_key',
                                            "MerchantKey"           : 'merchant_key',
                                            "RedeemedOutlet"        : 'redeemed_outlet_key',
                                            "TransactionId"         : 'transaction_id',
                                            "RedeemedAmount"        : 'redeemed_amount',
                                            "RewardFormat"          : 'reward_format',
                                            "VoucherKey"            : 'voucher_key',
                                            "RedeemedDateTime"      : 'redeemed_datetime',
                                            "Reverted"              : 'is_revert',
                                            "RevertedDateTime"      : 'reverted_datetime',
                                            }

__USER_VOUCHER_ENTITLED_DATA_TEMPLATE_UPSTREAM_SCHEMA = {
                                            "UserKey"               : 'user_key',
                                            "MerchantKey"           : 'merchant_key',
                                            "ProgramKey"            : 'program_key',
                                            "VoucherKey"            : 'voucher_key',
                                            "VoucherCode"           : 'voucher_code',
                                            "EntitledDatetime"      : 'entitled_datetime',
                                            "ExpiredDate"           : 'expired_date',
                                            }

__USER_VOUCHER_ENTITLED_REVERTED_DATA_TEMPLATE_UPSTREAM_SCHEMA = {
                                            "UserKey"               : 'user_key',
                                            "MerchantKey"           : 'merchant_key',
                                            "ProgramKey"            : 'program_key',
                                            "VoucherKey"            : 'voucher_key',
                                            "VoucherCode"           : 'voucher_code',
                                            "EntitledDatetime"      : 'entitled_datetime',
                                            "RevertedDatetime"      : 'reverted_datetime',
                                            "ExpiredDate"           : 'expired_date',
                                            }

__USER_VOUCHER_REDEEMED_DATA_TEMPLATE_UPSTREAM_SCHEMA = {
                                            "UserKey"               : 'user_key',
                                            "MerchantKey"           : 'merchant_key',
                                            "ProgramKey"            : 'program_key',
                                            "VoucherKey"            : 'voucher_key',
                                            "VoucherCode"           : 'voucher_code',
                                            "EntitledDatetime"      : 'entitled_datetime',
                                            'RedeemedDatetime'      : 'redeemed_datetime',
                                            "ExpiredDate"           : 'expired_date',
                                            'RedeemedOutletKey'     : 'redeemed_outlet_key',
                                            }

__USER_VOUCHER_REDEEMED_REVERTED_DATA_TEMPLATE_UPSTREAM_SCHEMA = {
                                            "UserKey"               : 'user_key',
                                            "MerchantKey"           : 'merchant_key',
                                            "ProgramKey"            : 'program_key',
                                            "VoucherKey"            : 'voucher_key',
                                            "VoucherCode"           : 'voucher_code',
                                            "EntitledDatetime"      : 'entitled_datetime',
                                            'RedeemedDatetime'      : 'redeemed_datetime',
                                            'RevertedDatetime'      : 'reverted_datetime',
                                            "ExpiredDate"           : 'expired_date',
                                            'RedeemedOutletKey'     : 'redeemed_outlet_key',
                                            }

__USER_VOUCHER_REMOVED_DATA_TEMPLATE_UPSTREAM_SCHEMA = {
                                            "UserKey"               : 'user_key',
                                            "MerchantKey"           : 'merchant_key',
                                            "ProgramKey"            : 'program_key',
                                            "VoucherKey"            : 'voucher_key',
                                            "VoucherCode"           : 'voucher_code',
                                            "EntitledDatetime"      : 'entitled_datetime',
                                            'RemovedDatetime'       : 'removed_datetime',
                                            "ExpiredDate"           : 'expired_date',
                                            }

__PARTNERSHIP_REWARD_TRANSACTION_DATA_TEMPLATE_UPSTREAM_SCHEMA = {
                                            "MerchantKey"                           : 'merchant_key',
                                            "PartnerMerchantKey"                    : 'partner_merchant_key',
                                            "TransactPointAmount"                   : 'transact_point_amount',
                                            "TransactDatetime"                      : 'transact_datetime',
                                            "TransactionId"                         : 'transaction_id',
                                            "MerchantPointWorthValueInCurrency"     : 'merchant_point_worth_value_in_currency',
                                            "PartnertPointWorthValueInCurrency"     : 'partner_point_worth_value_in_currency',
                                            }

__TESTING_TEMPLATE_UPSTREAM_SCHEMA = {
                                            "TestKey"                               : 'test_key',
                                            "TestValue"                             : 'test_value',
                                            "UpdatedDateTime"                       : 'updated_datetime',
                                            }



upstream_schema_config = {
                            REGISTERED_MERCHANT_TEMPLATE            : __REGISTERED_MERCHANT_TEMPLATE_UPSTREAM_SCHEMA,
                            REGISTERED_CUSTOMER_TEMPLATE            : __REGISTERED_CUSTOMER_TEMPLATE_UPSTREAM_SCHEMA,
                            MERCHANT_REGISTERED_CUSTOMER_TEMPLATE   : __MERCHANT_REGISTERED_CUSTOMER_TEMPLATE_UPSTREAM_SCHEMA,
                            CUSTOMER_MEMBERSHIP_TEMPLATE            : __CUSTOMER_MEMBERSHIP_TEMPLATE_UPSTREAM_SCHEMA,
                            CUSTOMER_TRANSACTION_TEMPLATE           : __CUSTOMER_TRANSACTION_DATA_TEMPLATE_UPSTREAM_SCHEMA,
                            SALES_TRANSACTION_TEMPLATE              : __SALES_TRANSACTION_DATA_TEMPLATE_UPSTREAM_SCHEMA,
                            MERCHANT_CUSTOMER_REWARD_TEMPLATE       : __CUSTOMER_REWARD_DATA_TEMPLATE_UPSTREAM_SCHEMA,
                            MERCHANT_CUSTOMER_PREPAID_TEMPLATE      : __CUSTOMER_PREPAID_DATA_TEMPLATE_UPSTREAM_SCHEMA,
                            MERCHANT_CUSTOMER_REDEMPTION_TEMPLATE   : __CUSTOMER_REDEMPTION_DATA_TEMPLATE_UPSTREAM_SCHEMA,
                            USER_VOUCHER_ENTITLED_TEMPLATE          : __USER_VOUCHER_ENTITLED_DATA_TEMPLATE_UPSTREAM_SCHEMA,
                            USER_VOUCHER_REDEEMED_TEMPLATE          : __USER_VOUCHER_REDEEMED_DATA_TEMPLATE_UPSTREAM_SCHEMA,
                            USER_VOUCHER_REMOVED_TEMPLATE           : __USER_VOUCHER_REMOVED_DATA_TEMPLATE_UPSTREAM_SCHEMA,
                            USER_VOUCHER_ENTITLED_REVERTED_TEMPLATE : __USER_VOUCHER_ENTITLED_REVERTED_DATA_TEMPLATE_UPSTREAM_SCHEMA,
                            USER_VOUCHER_REDEEMED_REVERTED_TEMPLATE : __USER_VOUCHER_REDEEMED_REVERTED_DATA_TEMPLATE_UPSTREAM_SCHEMA,
                            PARTNERSHIP_REWARD_TRANSACTION_TEMPLATE : __PARTNERSHIP_REWARD_TRANSACTION_DATA_TEMPLATE_UPSTREAM_SCHEMA,
                            TESTING_TEMPLATE                        : __TESTING_TEMPLATE_UPSTREAM_SCHEMA,
                            }

logger = logging.getLogger('target_debug')

def create_test_upstream_data(upstream_entity, schema):
    upstream_json = {}
    for upstrem_field_name, attr_name in schema.items():
        if isinstance(upstream_entity, dict):
            if upstream_entity.get(attr_name):
                upstream_json[upstrem_field_name] = default_serializable(upstream_entity[attr_name])
        else:
            if getattr(upstream_entity, attr_name):
                upstream_json[upstrem_field_name] = default_serializable(getattr(upstream_entity, attr_name))
    return upstream_json

def create_upstream_data(upstream_entity, schema, streamed_datetime=None, **kwargs):
    upstream_json = {}
    try:
        for upstrem_field_name, attr_name in schema.items():
            if isinstance(upstream_entity, dict):
                upstream_json[upstrem_field_name] = default_serializable(upstream_entity[attr_name])
            else:
                upstream_json[upstrem_field_name] = default_serializable(getattr(upstream_entity, attr_name))
        
        logger.debug('upstream_entity classname=%s', upstream_entity.__class__.__name__)
        if streamed_datetime is None:
            streamed_datetime = datetime.utcnow()
                
        upstream_json['Key'] = uuid.uuid1().hex
        
        if (UPSTREAM_UPDATED_DATETIME_FIELD_NAME in upstream_json) == False:
            upstream_json[UPSTREAM_UPDATED_DATETIME_FIELD_NAME] = default_serializable(streamed_datetime)
            
        
        for key, value in kwargs.items():
            upstream_json[key] = convert_to_serializable_value(value, datetime_format='%Y-%m-%d %H:%M:%S', date_format='%Y-%m-%d', time_format='%H:%M:%S')
    except:
        logger.error('Failed due to %s', get_tracelog())
    
    return upstream_json
    
    
def __create_upstream(upstream_entity, merchant_acct, upstream_template, dataset_name, table_name, streamed_datetime=None, **kwargs):
    
    upstream_json = {}
    logger.debug('upstream_template=%s', upstream_template)
    if upstream_entity:
        schema = upstream_schema_config.get(upstream_template)
        upstream_json = create_upstream_data(upstream_entity, schema, streamed_datetime=streamed_datetime, **kwargs)
        '''
        schema = upstream_schema_config.get(upstream_template)
        logger.debug('schema=%s', schema)
        try:
            for upstrem_field_name, attr_name in schema.items():
                if isinstance(upstream_entity, dict):
                    upstream_json[upstrem_field_name] = default_serializable(upstream_entity[attr_name])
                else:
                    upstream_json[upstrem_field_name] = default_serializable(getattr(upstream_entity, attr_name))
            
            logger.debug('upstream_entity classname=%s', upstream_entity.__class__.__name__)
        except:
            logger.error('Failed due to %s', get_tracelog())
            
        '''
    '''    
    if streamed_datetime is None:
        streamed_datetime = datetime.utcnow()
            
    upstream_json['Key'] = uuid.uuid1().hex
    
    if (UPSTREAM_UPDATED_DATETIME_FIELD_NAME in upstream_json) == False:
        upstream_json[UPSTREAM_UPDATED_DATETIME_FIELD_NAME] = default_serializable(streamed_datetime)
    '''
    #year = update_datetime.yeaar
    
    #dataset_with_year_prefix = '{year}_{dataset}'.format(year=year, dataset=dataset_name)
    try:
        '''
        for key, value in kwargs.items():
            upstream_json[key] = convert_to_serializable_value(value, datetime_format='%Y-%m-%d %H:%M:%S', date_format='%Y-%m-%d', time_format='%H:%M:%S')
        '''
        logger.debug('-------------------------------------------------')
        logger.debug('dataset_name=%s', dataset_name)
        logger.debug('table_name=%s', table_name)
        logger.debug('upstream_template=%s', upstream_template)
        logger.debug('upstream_json=%s', upstream_json)
        logger.debug('-------------------------------------------------')
        UpstreamData.create(merchant_acct, dataset_name, table_name, upstream_template, [upstream_json], partition_datetime=streamed_datetime)
    except:
        logger.error('Failed due to %s', get_tracelog())
    

def create_entitled_customer_voucher_upstream_for_merchant(customer_entitled_voucher, ):
    table_name              = USER_VOUCHER_ENTITLED_TEMPLATE
    
    user_key                = customer_entitled_voucher.entitled_user_key
    merchant_key            = customer_entitled_voucher.merchant_acct_key
    program_key             = customer_entitled_voucher.reward_program_key
    voucher_key             = customer_entitled_voucher.entitled_voucher_key
    voucher_code            = customer_entitled_voucher.redeem_code 
    entitled_datetime       = customer_entitled_voucher.rewarded_datetime
    expiry_date             = customer_entitled_voucher.expiry_date
    
    streamed_datetime       = entitled_datetime
    merchant_acct           = customer_entitled_voucher.rewarded_by_merchant_acct_entity
    account_code            = merchant_acct.account_code.replace('-','')
    #final_table_name        = '{}_{}'.format(table_name, streamed_datetime.strftime('%Y%m%d'))
    #final_table_name        = table_name
    '''
    if stream_date_is_data_date:
        final_table_name        = '{}_{}'.format(table_name, entitled_datetime.strftime('%Y%m%d'))
    else:
        final_table_name        = '{}_{}'.format(table_name, streamed_datetime.strftime('%Y%m%d'))
    '''
    data_json = {
                'user_key'          : user_key,
                'merchant_key'      : merchant_key,
                'program_key'       : program_key,
                'voucher_key'       : voucher_key,
                'voucher_code'      : voucher_code,
                'entitled_datetime' : entitled_datetime,
                'expired_date'      : expiry_date,
                
                }
    dataset = '%s_%s' % (MERCHANT_DATASET,account_code)
    __create_upstream(data_json, merchant_acct, USER_VOUCHER_ENTITLED_TEMPLATE, dataset, table_name, streamed_datetime=streamed_datetime)
    
def create_revert_entitled_customer_voucher_upstream_for_merchant(customer_entitled_voucher, ):
    
    user_key                = customer_entitled_voucher.entitled_user_key
    merchant_key            = customer_entitled_voucher.merchant_acct_key
    program_key             = customer_entitled_voucher.reward_program_key
    voucher_key             = customer_entitled_voucher.entitled_voucher_key
    voucher_code            = customer_entitled_voucher.redeem_code 
    entitled_datetime       = customer_entitled_voucher.rewarded_datetime
    reverted_datetime       = customer_entitled_voucher.reverted_datetime
    expiry_date             = customer_entitled_voucher.expiry_date
    
    streamed_datetime       = reverted_datetime
    
    table_name              = USER_VOUCHER_ENTITLED_REVERTED_TEMPLATE
    merchant_acct           = customer_entitled_voucher.rewarded_by_merchant_acct_entity
    account_code            = merchant_acct.account_code.replace('-','')
    #final_table_name        = '{}_{}'.format(table_name, streamed_datetime.strftime('%Y%m%d'))
    #final_table_name        = table_name
    
    
    '''
    if stream_date_is_data_date:
        final_table_name        = '{}_{}'.format(table_name, entitled_datetime.strftime('%Y%m%d'))
    else:
        final_table_name        = '{}_{}'.format(table_name, streamed_datetime.strftime('%Y%m%d'))
    '''
    
    data_json = {
                'user_key'          : user_key,
                'merchant_key'      : merchant_key,
                'program_key'       : program_key,
                'voucher_key'       : voucher_key,
                'voucher_code'      : voucher_code,
                'entitled_datetime' : entitled_datetime,
                'reverted_datetime' : reverted_datetime,
                'expired_date'      : expiry_date,
                
                }
    dataset = '%s_%s' % (MERCHANT_DATASET,account_code)
    __create_upstream(data_json, merchant_acct, USER_VOUCHER_ENTITLED_REVERTED_TEMPLATE, dataset, table_name, streamed_datetime=streamed_datetime)    


def create_removed_customer_voucher_to_upstream_for_merchant(customer_entitled_voucher, ):
    
    
    table_name              = USER_VOUCHER_REMOVED_TEMPLATE
    merchant_acct           = customer_entitled_voucher.rewarded_by_merchant_acct_entity
    account_code            = merchant_acct.account_code.replace('-','')
    #final_table_name        = '{}_{}'.format(table_name, streamed_datetime.strftime('%Y%m%d'))
    
    user_key                = customer_entitled_voucher.entitled_user_key
    merchant_key            = customer_entitled_voucher.merchant_acct_key
    program_key             = customer_entitled_voucher.reward_program_key
    voucher_key             = customer_entitled_voucher.entitled_voucher_key
    voucher_code            = customer_entitled_voucher.redeem_code 
    entitled_datetime       = customer_entitled_voucher.rewarded_datetime
    removed_datetime        = customer_entitled_voucher.removed_datetime
    expiry_date             = customer_entitled_voucher.expiry_date
    
    streamed_datetime = removed_datetime
    
    '''
    if stream_date_is_data_date:
        final_table_name        = '{}_{}'.format(table_name, removed_datetime.strftime('%Y%m%d'))
    else:
        final_table_name        = '{}_{}'.format(table_name, streamed_datetime.strftime('%Y%m%d'))
    ''' 
    data_json = {
                'user_key'          : user_key,
                'merchant_key'      : merchant_key,
                'program_key'       : program_key,
                'voucher_key'       : voucher_key,
                'voucher_code'      : voucher_code,
                'entitled_datetime' : entitled_datetime,
                'removed_datetime'  : removed_datetime,
                'expired_date'      : expiry_date,
                
                }
    dataset = '%s_%s' % (MERCHANT_DATASET,account_code)
    __create_upstream(data_json, merchant_acct, USER_VOUCHER_REMOVED_TEMPLATE, dataset, table_name, streamed_datetime=streamed_datetime)


def create_redeemed_customer_voucher_to_upstream_for_merchant(customer_entitled_voucher, ):
    
    
    table_name              = USER_VOUCHER_REDEEMED_TEMPLATE
    merchant_acct           = customer_entitled_voucher.rewarded_by_merchant_acct_entity
    account_code            = merchant_acct.account_code.replace('-','')
    
    user_key                = customer_entitled_voucher.entitled_user_key
    merchant_key            = customer_entitled_voucher.merchant_acct_key
    program_key             = customer_entitled_voucher.reward_program_key
    voucher_key             = customer_entitled_voucher.entitled_voucher_key
    voucher_code            = customer_entitled_voucher.redeem_code 
    entitled_datetime       = customer_entitled_voucher.rewarded_datetime
    redeemed_datetime       = customer_entitled_voucher.redeemed_datetime
    redeemed_outlet_key     = customer_entitled_voucher.redeemed_by_outlet_key
    expiry_date             = customer_entitled_voucher.expiry_date
    
    streamed_datetime       = redeemed_datetime
    
    data_json = {
                'user_key'              : user_key,
                'merchant_key'          : merchant_key,
                'program_key'           : program_key,
                'voucher_key'           : voucher_key,
                'voucher_code'          : voucher_code,
                'entitled_datetime'     : entitled_datetime,
                'redeemed_datetime'     : redeemed_datetime,
                'redeemed_outlet_key'   : redeemed_outlet_key,
                'expired_date'          : expiry_date,
                
                }
    dataset = '%s_%s' % (MERCHANT_DATASET,account_code)
    __create_upstream(data_json, merchant_acct, USER_VOUCHER_REDEEMED_TEMPLATE, dataset, table_name, streamed_datetime=streamed_datetime)
    
def create_revert_redeemed_customer_voucher_to_upstream_for_merchant(customer_entitled_voucher, ):
    #streamed_datetime = datetime.utcnow()
    
    table_name              = USER_VOUCHER_REDEEMED_REVERTED_TEMPLATE
    merchant_acct           = customer_entitled_voucher.rewarded_by_merchant_acct_entity
    account_code            = merchant_acct.account_code.replace('-','')
    #final_table_name        = '{}_{}'.format(table_name, streamed_datetime.strftime('%Y%m%d'))
    
    user_key                = customer_entitled_voucher.entitled_user_key
    merchant_key            = customer_entitled_voucher.merchant_acct_key
    program_key             = customer_entitled_voucher.reward_program_key
    voucher_key             = customer_entitled_voucher.entitled_voucher_key
    voucher_code            = customer_entitled_voucher.redeem_code 
    entitled_datetime       = customer_entitled_voucher.rewarded_datetime
    redeemed_datetime       = customer_entitled_voucher.redeemed_datetime
    redeemed_outlet_key     = customer_entitled_voucher.redeemed_by_outlet_key
    expiry_date             = customer_entitled_voucher.expiry_date
    
    streamed_datetime       = entitled_datetime
    
    '''
    if stream_date_is_data_date:
        final_table_name        = '{}_{}'.format(table_name, redeemed_datetime.strftime('%Y%m%d'))
    else:
        final_table_name        = '{}_{}'.format(table_name, streamed_datetime.strftime('%Y%m%d'))
    ''' 
    data_json = {
                'user_key'              : user_key,
                'merchant_key'          : merchant_key,
                'program_key'           : program_key,
                'voucher_key'           : voucher_key,
                'voucher_code'          : voucher_code,
                'entitled_datetime'     : entitled_datetime,
                'redeemed_datetime'     : redeemed_datetime,
                'reverted_datetime'     : streamed_datetime,
                'redeemed_outlet_key'   : redeemed_outlet_key,
                'expired_date'          : expiry_date,
                
                }
    dataset = '%s_%s' % (MERCHANT_DATASET,account_code)
    __create_upstream(data_json, merchant_acct, USER_VOUCHER_REDEEMED_REVERTED_TEMPLATE, dataset, table_name, streamed_datetime=streamed_datetime)    

def create_registered_customer_upstream_for_system(customer, ):
    table_name          = REGISTERED_CUSTOMER_TEMPLATE
    streamed_datetime   = customer.registered_datetime
    merchant_acct       = customer.registered_merchant_acct
    
    __create_upstream(customer, merchant_acct, REGISTERED_CUSTOMER_TEMPLATE, SYSTEM_DATASET, table_name, streamed_datetime=streamed_datetime)
    
def create_customer_membership_upstream_for_merchant(customer_membership, merchant_acct=None, ):
    
    table_name          = CUSTOMER_MEMBERSHIP_TEMPLATE
    streamed_datetime   = customer_membership.entitled_datetime
    
    if merchant_acct is None:
        merchant_acct       = customer_membership.merchant_acct_entity
    
    if merchant_acct is not None:
        account_code        = merchant_acct.account_code.replace('-','')
        dataset = '%s_%s' % (MERCHANT_DATASET,account_code)
        
        __create_upstream(customer_membership, merchant_acct, CUSTOMER_MEMBERSHIP_TEMPLATE, dataset, table_name, streamed_datetime=streamed_datetime)    

def create_merchant_registered_customer_upstream_for_merchant(customer, ):
    #streamed_datetime = datetime.utcnow()
    
    table_name          = MERCHANT_REGISTERED_CUSTOMER_TEMPLATE
    merchant_acct       = customer.registered_merchant_acct
    account_code        = merchant_acct.account_code.replace('-','')
    streamed_datetime   = customer.registered_datetime
    #final_table_name    = '{}_{}_{}'.format(table_name, account_code, streamed_datetime.strftime('%Y%m%d'))
    dataset = '%s_%s' % (MERCHANT_DATASET,account_code)
    __create_upstream(customer, merchant_acct, MERCHANT_REGISTERED_CUSTOMER_TEMPLATE, dataset, table_name, streamed_datetime=streamed_datetime)    
    
def create_merchant_sales_transaction_upstream_for_merchant(transaction_details, Reverted=False):
    
    streamed_datetime     = transaction_details.transact_datetime
    if Reverted:
        streamed_datetime     = transaction_details.reverted_datetime
        
    table_name          = SALES_TRANSACTION_TEMPLATE
    merchant_acct       = transaction_details.transact_merchant_acct
    account_code        = merchant_acct.account_code.replace('-','')
    
    dataset = '%s_%s' % (MERCHANT_DATASET,account_code)
    __create_upstream(transaction_details, merchant_acct, SALES_TRANSACTION_TEMPLATE, dataset, table_name, 
                      streamed_datetime=streamed_datetime, Reverted=Reverted, RevertedDateTime=None)
    
    


def create_merchant_customer_transaction_upstream_for_merchant(transaction_details, Reverted=False,):
    streamed_datetime   = transaction_details.transact_datetime
    updated_datetime    = transaction_details.transact_datetime
    reverted_datetime   = None
    if Reverted:
        streamed_datetime   = transaction_details.reverted_datetime
        reverted_datetime   = transaction_details.reverted_datetime
        updated_datetime    = transaction_details.reverted_datetime
        
    table_name          = CUSTOMER_TRANSACTION_TEMPLATE
    merchant_acct       = transaction_details.transact_merchant_acct
    account_code        = merchant_acct.account_code.replace('-','')
    
    dataset = '%s_%s' % (MERCHANT_DATASET,account_code)
    __create_upstream(transaction_details, merchant_acct, CUSTOMER_TRANSACTION_TEMPLATE, dataset, table_name, 
                      streamed_datetime=streamed_datetime, Reverted=Reverted, RevertedDateTime=reverted_datetime,
                      UpdatedDateTime=updated_datetime,)
    
def create_merchant_customer_reward_upstream_for_merchant(transaction_details, reward_details, Reverted=False):
    
    table_name          = MERCHANT_CUSTOMER_REWARD_TEMPLATE
    merchant_acct       = transaction_details.transact_merchant_acct
    account_code        = merchant_acct.account_code.replace('-','')
    #final_table_name    = '{}_{}_{}'.format(table_name, account_code, streamed_datetime.strftime('%Y%m%d'))
    
    streamed_datetime   = transaction_details.transact_datetime
    updated_datetime    = transaction_details.transact_datetime
    
    reverted_datetime = None
    if Reverted:
        reverted_datetime   = transaction_details.reverted_datetime
        updated_datetime    = transaction_details.reverted_datetime
        
    
    transaction_details_with_reward_details = CustomerTransactionWithRewardDetails(transaction_details, reward_details)
    
    if transaction_details_with_reward_details.reward_amount<=0:
        logger.debug('Ignore due to reward_amount is zero')
        return
    
    
    dataset = '%s_%s' % (MERCHANT_DATASET,account_code)
    __create_upstream(transaction_details_with_reward_details, merchant_acct, MERCHANT_CUSTOMER_REWARD_TEMPLATE, dataset, table_name, 
                      streamed_datetime=streamed_datetime, Reverted=Reverted, RevertedDateTime=reverted_datetime,
                      UpdatedDateTime=updated_datetime,
                      )

def create_merchant_customer_prepaid_upstream_for_merchant(transaction_details, prepaid_details, Reverted=False):
    
    table_name          = MERCHANT_CUSTOMER_PREPAID_TEMPLATE
    merchant_acct       = transaction_details.transact_merchant_acct
    account_code        = merchant_acct.account_code.replace('-','')
    
    streamed_datetime   = transaction_details.transact_datetime
    updated_datetime    = transaction_details.transact_datetime
    
    reverted_datetime = None
    if Reverted:
        reverted_datetime   = transaction_details.reverted_datetime
        updated_datetime    = transaction_details.reverted_datetime
    
    transaction_details_with_prepaid_details = CustomerTransactionWithPrepaidDetails(transaction_details, prepaid_details)
    
    dataset = '%s_%s' % (MERCHANT_DATASET,account_code)
    
    __create_upstream(transaction_details_with_prepaid_details, merchant_acct, MERCHANT_CUSTOMER_PREPAID_TEMPLATE, dataset, table_name, 
                      streamed_datetime=streamed_datetime, Reverted=Reverted, RevertedDateTime=reverted_datetime,
                      UpdatedDateTime=updated_datetime,)    
    
def create_merchant_customer_redemption_upstream_for_merchant(customer_redemption, reverted=False ):
    logger.debug('customer_redemption key=%s', customer_redemption.key_in_str)
    
    table_name          = MERCHANT_CUSTOMER_REDEMPTION_TEMPLATE
    merchant_acct       = customer_redemption.redeemed_merchant_acct
    account_code        = merchant_acct.account_code.replace('-','')
    
    upstream_data_list = []
    
    dataset = '%s_%s' % (MERCHANT_DATASET,account_code)
    
    streamed_datetime   = customer_redemption.redeemed_datetime
    updated_datetime    = customer_redemption.redeemed_datetime
    
    reverted_datetime = None
    if reverted:
        reverted_datetime   = customer_redemption.reverted_datetime
        updated_datetime    = customer_redemption.reverted_datetime
    
    if customer_redemption.reward_format in (program_conf.REWARD_FORMAT_POINT, program_conf.REWARD_FORMAT_STAMP, program_conf.REWARD_FORMAT_PREPAID):
        upstream_data_list.append(customer_redemption.to_upstream_info())
    
    elif customer_redemption.reward_format == program_conf.REWARD_FORMAT_VOUCHER:
        upstream_data_list.extend(customer_redemption.to_voucher_upstream_info_list())
            
    for upstream_data in upstream_data_list:
        __create_upstream(upstream_data, merchant_acct, MERCHANT_CUSTOMER_REDEMPTION_TEMPLATE, dataset, table_name, 
                      streamed_datetime=streamed_datetime, Reverted=reverted, RevertedDateTime=reverted_datetime, 
                      UpdatedDateTime=updated_datetime
                      )
    
def create_merchant_customer_redemption_reverted_upstream_for_merchant(redemption_details):
    create_merchant_customer_redemption_upstream_for_merchant(redemption_details, 
                                                              reverted=True, )     


def create_partnership_transaction_upstream_for_merchant(transaction_details, ):
    try:
        table_name              = PARTNERSHIP_REWARD_TRANSACTION_TEMPLATE
        merchant_acct           = transaction_details.merchant_acct_entity
        account_code            = merchant_acct.account_code.replace('-','')
        transact_datetime       = transaction_details.transact_datetime
        dataset = '%s_%s' % (MERCHANT_DATASET,account_code)
        
        data_json = {
                    "merchant_key"                              : merchant_acct.key_in_str,
                    "partner_merchant_key"                      : transaction_details.partner_merchant_acct_key,
                    "transact_point_amount"                     : transaction_details.transact_point_amount,
                    "transact_datetime"                         : transact_datetime,
                    "transaction_id"                            : transaction_details.transaction_id,
                    "merchant_point_worth_value_in_currency"    : transaction_details.merchant_point_worth_value_in_currency,
                    "partner_point_worth_value_in_currency"     : transaction_details.partner_point_worth_value_in_currency,
            }
        logger.debug('data_json=%s', data_json)
        __create_upstream(data_json, merchant_acct, PARTNERSHIP_REWARD_TRANSACTION_TEMPLATE, dataset, table_name, 
                          streamed_datetime=transact_datetime, UpdatedDateTime=transact_datetime)
        
    except:
        logger.error('Failed due to %s', get_tracelog())
    