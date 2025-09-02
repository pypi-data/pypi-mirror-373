'''
Created on 11 Jan 2021

@author: jacklok
'''
from google.cloud import bigquery


__REGISTERED_USER_SCHEMA = {
                        
                            #customer key
                            bigquery.SchemaField('Key', 'STRING'),
                            bigquery.SchemaField('UserKey', 'STRING'),
                            bigquery.SchemaField('DOB', 'DATE'),
                            bigquery.SchemaField('Gender', 'STRING'),
                            bigquery.SchemaField('MobilePhone', 'STRING'),
                            bigquery.SchemaField('Email', 'STRING'),
                            bigquery.SchemaField('MobileAppDownload', 'BOOLEAN'),
                            bigquery.SchemaField('RegisteredDateTime', 'DATETIME'),
                            bigquery.SchemaField('UpdatedDateTime', 'DATETIME'),
                            bigquery.SchemaField('PartitionDateTime', 'DATETIME'),
                            }

__REGISTERED_CUSTOMER_SCHEMA = {
                        
                            #customer key
                            bigquery.SchemaField('Key', 'STRING'),
                            bigquery.SchemaField('UserKey', 'STRING'),
                            bigquery.SchemaField('CustomerKey', 'STRING'),
                            bigquery.SchemaField('MerchantKey', 'STRING'),
                            bigquery.SchemaField('DOB', 'DATE'),
                            bigquery.SchemaField('Gender', 'STRING'),
                            bigquery.SchemaField('MobilePhone', 'STRING'),
                            bigquery.SchemaField('Email', 'STRING'),
                            bigquery.SchemaField('MobileAppInstall', 'BOOLEAN'),
                            bigquery.SchemaField('RegisteredDateTime', 'DATETIME'),
                            bigquery.SchemaField('RegisteredOutlet', 'STRING'),
                            bigquery.SchemaField('UpdatedDateTime', 'DATETIME'),
                            bigquery.SchemaField('PartitionDateTime', 'DATETIME'),
                            }

__CUSTOMER_TAG_SCHEMA = {
                        
                            #customer key
                            bigquery.SchemaField('Key', 'STRING'),
                            bigquery.SchemaField('CustomerKey', 'STRING'),
                            bigquery.SchemaField('MerchantKey', 'STRING'),
                            bigquery.SchemaField('tag', 'STRING'),
                            bigquery.SchemaField('UpdatedDateTime', 'DATETIME'),
                            bigquery.SchemaField('PartitionDateTime', 'DATETIME'),
                            }

__MERCHANT_REGISTERED_CUSTOMER_SCHEMA = {
                        
                            #customer key
                            bigquery.SchemaField('Key', 'STRING'),
                            bigquery.SchemaField('UserKey', 'STRING'),
                            bigquery.SchemaField('CustomerKey', 'STRING'),
                            bigquery.SchemaField('DOB', 'DATE'),
                            bigquery.SchemaField('Gender', 'STRING'),
                            bigquery.SchemaField('MobilePhone', 'STRING'),
                            bigquery.SchemaField('Email', 'STRING'),
                            bigquery.SchemaField('MobileAppInstall', 'BOOLEAN'),
                            bigquery.SchemaField('RegisteredDateTime', 'DATETIME'),
                            bigquery.SchemaField('RegisteredOutlet', 'STRING'),
                            bigquery.SchemaField('UpdatedDateTime', 'DATETIME'),
                            bigquery.SchemaField('PartitionDateTime', 'DATETIME'),
                            }

__CUSTOMER_MEMBERSHIP_SCHEMA = {
                            bigquery.SchemaField('Key', 'STRING'),
                            bigquery.SchemaField('CustomerKey', 'STRING'),
                            bigquery.SchemaField('MembershipKey', 'STRING'),
                            bigquery.SchemaField('EntitledDateTime', 'DATETIME'),
                            bigquery.SchemaField('ExpiredDate', 'DATE'),
                            bigquery.SchemaField('UpdatedDateTime', 'DATETIME'),
                            bigquery.SchemaField('PartitionDateTime', 'DATETIME'),
                            }

__MERCHANT_CUSTOMER_TRANSACTION_SCHEMA = {
                        
                            #customer key
                            bigquery.SchemaField('Key', 'STRING'),
                            bigquery.SchemaField('UserKey', 'STRING'),
                            bigquery.SchemaField('CustomerKey', 'STRING'),
                            bigquery.SchemaField('MerchantKey', 'STRING'),
                            bigquery.SchemaField('TransactOutlet', 'STRING'),
                            bigquery.SchemaField('TransactionId', 'STRING'),
                            bigquery.SchemaField('InvoiceId', 'STRING'),
                            bigquery.SchemaField('TransactAmount', 'FLOAT64'),
                            bigquery.SchemaField('TransactDateTime', 'DATETIME'),
                            bigquery.SchemaField('IsSalesTransaction', 'BOOLEAN'),
                            bigquery.SchemaField('Reverted', 'BOOLEAN'),
                            bigquery.SchemaField('RevertedDateTime', 'DATETIME'),
                            bigquery.SchemaField('UpdatedDateTime', 'DATETIME'),
                            bigquery.SchemaField('PartitionDateTime', 'DATETIME'),
                            }

__MERCHANT_SALES_TRANSACTION_SCHEMA = {
                        
                            bigquery.SchemaField('Key', 'STRING'),
                            bigquery.SchemaField('MerchantKey', 'STRING'),
                            bigquery.SchemaField('TransactOutlet', 'STRING'),
                            bigquery.SchemaField('TransactionId', 'STRING'),
                            bigquery.SchemaField('InvoiceId', 'STRING'),
                            bigquery.SchemaField('TransactAmount', 'FLOAT64'),
                            bigquery.SchemaField('TransactDateTime', 'DATETIME'),
                            bigquery.SchemaField('Reverted', 'BOOLEAN'),
                            bigquery.SchemaField('RevertedDateTime', 'DATETIME'),
                            bigquery.SchemaField('UpdatedDateTime', 'DATETIME'),
                            bigquery.SchemaField('PartitionDateTime', 'DATETIME'),
                            }

__MERCHANT_CUSTOMER_REWARD_SCHEMA = {
                        
                            bigquery.SchemaField('Key', 'STRING'),
                            bigquery.SchemaField('CustomerKey', 'STRING'),
                            bigquery.SchemaField('MerchantKey', 'STRING'),
                            bigquery.SchemaField('TransactOutlet', 'STRING'),
                            bigquery.SchemaField('TransactionId', 'STRING'),
                            bigquery.SchemaField('TransactAmount', 'FLOAT64'),
                            bigquery.SchemaField('TransactDateTime', 'DATETIME'),
                            bigquery.SchemaField('RewardFormat', 'STRING'),
                            bigquery.SchemaField('RewardAmount', 'FLOAT64'),
                            bigquery.SchemaField('ExpiryDate', 'DATE'),
                            bigquery.SchemaField('RewardFormatKey', 'STRING'),
                            bigquery.SchemaField('RewardedDateTime', 'DATETIME'),
                            bigquery.SchemaField('Reverted', 'BOOLEAN'),
                            bigquery.SchemaField('RevertedDateTime', 'DATETIME'),
                            bigquery.SchemaField('UpdatedDateTime', 'DATETIME'),
                            bigquery.SchemaField('PartitionDateTime', 'DATETIME'),
                            }

__MERCHANT_CUSTOMER_PREPAID_SCHEMA = {
                        
                            bigquery.SchemaField('Key', 'STRING'),
                            bigquery.SchemaField('CustomerKey', 'STRING'),
                            bigquery.SchemaField('MerchantKey', 'STRING'),
                            bigquery.SchemaField('TransactOutlet', 'STRING'),
                            bigquery.SchemaField('TransactionId', 'STRING'),
                            bigquery.SchemaField('TransactAmount', 'FLOAT64'),
                            bigquery.SchemaField('TransactDateTime', 'DATETIME'),
                            bigquery.SchemaField('TopupAmount', 'FLOAT64'),
                            bigquery.SchemaField('PrepaidAmount', 'FLOAT64'),
                            bigquery.SchemaField('TopupDateTime', 'DATETIME'),
                            bigquery.SchemaField('Reverted', 'BOOLEAN'),
                            bigquery.SchemaField('RevertedDateTime', 'DATETIME'),
                            bigquery.SchemaField('UpdatedDateTime', 'DATETIME'),
                            bigquery.SchemaField('PartitionDateTime', 'DATETIME'),
                            }

__MERCHANT_CUSTOMER_REDEMPTION_SCHEMA = {
                        
                            bigquery.SchemaField('Key', 'STRING'),
                            bigquery.SchemaField('CustomerKey', 'STRING'),
                            bigquery.SchemaField('MerchantKey', 'STRING'),
                            bigquery.SchemaField('RedeemedOutlet', 'STRING'),
                            bigquery.SchemaField('TransactionId', 'STRING'),
                            bigquery.SchemaField('RedeemedAmount', 'FLOAT64'),
                            bigquery.SchemaField('RewardFormat', 'STRING'),
                            bigquery.SchemaField('VoucherKey', 'STRING'),
                            bigquery.SchemaField('RedeemedDateTime', 'DATETIME'),
                            bigquery.SchemaField('Reverted', 'BOOLEAN'),
                            bigquery.SchemaField('RevertedDateTime', 'DATETIME'),
                            bigquery.SchemaField('UpdatedDateTime', 'DATETIME'),
                            bigquery.SchemaField('PartitionDateTime', 'DATETIME'),
                            }


__REGISTERED_MERCHANT_SCHEMA = {
                        
                            #customer key
                            bigquery.SchemaField('Key', 'STRING'),
                            bigquery.SchemaField('MerchantKey', 'STRING'),
                            bigquery.SchemaField('CompanyName', 'STRING'),
                            bigquery.SchemaField('RegisteredDateTime', 'DATETIME'),
                            bigquery.SchemaField('UpdatedDateTime', 'DATETIME'),
                            bigquery.SchemaField('PartitionDateTime', 'DATETIME'),
                            }
    

_USER_ENTITLED_VOUCHER_SCHEMA = (
                            bigquery.SchemaField('Key', 'STRING'),
                            bigquery.SchemaField('UserKey', 'STRING'),
                            bigquery.SchemaField('MerchantKey', 'STRING'),
                            bigquery.SchemaField('ProgramKey', 'STRING'),
                            bigquery.SchemaField('VoucherKey', 'STRING'),
                            bigquery.SchemaField('VoucherCode', 'STRING'),
                            bigquery.SchemaField('EntitledDatetime', 'DATETIME'),
                            bigquery.SchemaField('ExpiredDate', 'DATE'),
                            bigquery.SchemaField('UpdatedDateTime', 'DATETIME'),
                            bigquery.SchemaField('PartnerMerchantKey', 'STRING'),
                            bigquery.SchemaField('PartitionDateTime', 'DATETIME'),
                            
            )

_USER_REDEEMED_VOUCHER_SCHEMA = (
                            bigquery.SchemaField('Key', 'STRING'),
                            bigquery.SchemaField('UserKey', 'STRING'),
                            bigquery.SchemaField('MerchantKey', 'STRING'),
                            bigquery.SchemaField('ProgramKey', 'STRING'),
                            bigquery.SchemaField('VoucherKey', 'STRING'),
                            bigquery.SchemaField('VoucherCode', 'STRING'),
                            bigquery.SchemaField('EntitledDatetime', 'DATETIME'),
                            bigquery.SchemaField('RedeemedDatetime', 'DATETIME'),
                            bigquery.SchemaField('ExpiredDate', 'DATE'),
                            bigquery.SchemaField('RedeemedOutletKey', 'STRING'),
                            bigquery.SchemaField('UpdatedDateTime', 'DATETIME'),
                            bigquery.SchemaField('PartitionDateTime', 'DATETIME'),
            )

_USER_REDEEMED_REVERTED_VOUCHER_SCHEMA = (
                            bigquery.SchemaField('Key', 'STRING'),
                            bigquery.SchemaField('UserKey', 'STRING'),
                            bigquery.SchemaField('MerchantKey', 'STRING'),
                            bigquery.SchemaField('ProgramKey', 'STRING'),
                            bigquery.SchemaField('VoucherKey', 'STRING'),
                            bigquery.SchemaField('VoucherCode', 'STRING'),
                            bigquery.SchemaField('EntitledDatetime', 'DATETIME'),
                            bigquery.SchemaField('RedeemedDatetime', 'DATETIME'),
                            bigquery.SchemaField('RevertedDatetime', 'DATETIME'),
                            bigquery.SchemaField('ExpiredDate', 'DATE'),
                            bigquery.SchemaField('RedeemedOutletKey', 'STRING'),
                            bigquery.SchemaField('UpdatedDateTime', 'DATETIME'),
                            bigquery.SchemaField('PartitionDateTime', 'DATETIME'),
            )

_USER_REMOVED_VOUCHER_SCHEMA = (
                            bigquery.SchemaField('Key', 'STRING'),
                            bigquery.SchemaField('UserKey', 'STRING'),
                            bigquery.SchemaField('MerchantKey', 'STRING'),
                            bigquery.SchemaField('ProgramKey', 'STRING'),
                            bigquery.SchemaField('VoucherKey', 'STRING'),
                            bigquery.SchemaField('VoucherCode', 'STRING'),
                            bigquery.SchemaField('EntitledDatetime', 'DATETIME'),
                            bigquery.SchemaField('RemovedDatetime', 'DATETIME'),
                            bigquery.SchemaField('ExpiredDate', 'DATE'),
                            bigquery.SchemaField('UpdatedDateTime', 'DATETIME'),
                            bigquery.SchemaField('PartitionDateTime', 'DATETIME'),
                            
            )

_USER_REVERTED_VOUCHER_SCHEMA = (
                            bigquery.SchemaField('Key', 'STRING'),
                            bigquery.SchemaField('UserKey', 'STRING'),
                            bigquery.SchemaField('MerchantKey', 'STRING'),
                            bigquery.SchemaField('ProgramKey', 'STRING'),
                            bigquery.SchemaField('VoucherKey', 'STRING'),
                            bigquery.SchemaField('VoucherCode', 'STRING'),
                            bigquery.SchemaField('EntitledDatetime', 'DATETIME'),
                            bigquery.SchemaField('RevertedDatetime', 'DATETIME'),
                            bigquery.SchemaField('ExpiredDate', 'DATE'),
                            bigquery.SchemaField('UpdatedDateTime', 'DATETIME'),
                            bigquery.SchemaField('PartitionDateTime', 'DATETIME'),
                            
            )

_PARTNERSHIP_REWARD_TRANSACTION_SCHEMA = (
                            bigquery.SchemaField('Key', 'STRING'),
                            bigquery.SchemaField('MerchantKey', 'STRING'),
                            bigquery.SchemaField('PartnerMerchantKey', 'STRING'),
                            bigquery.SchemaField('TransactPointAmount', 'FLOAT64'),
                            bigquery.SchemaField('TransactDatetime', 'DATETIME'),
                            bigquery.SchemaField('TransactionId', 'STRING'),
                            bigquery.SchemaField('MerchantPointWorthValueInCurrency', 'FLOAT64'),
                            bigquery.SchemaField('PartnertPointWorthValueInCurrency', 'FLOAT64'),
                            bigquery.SchemaField('UpdatedDateTime', 'DATETIME'),
                            bigquery.SchemaField('PartitionDateTime', 'DATETIME'),
                            
            )

_TESTING_SCHEMA = (
                            bigquery.SchemaField('TestKey', 'STRING'),
                            bigquery.SchemaField('TestValue', 'STRING'),
                            bigquery.SchemaField('UpdatedDateTime', 'DATETIME'),
                            
                            
            )

REGISTERED_USER_TEMPLATE                    = 'registered_user'
REGISTERED_CUSTOMER_TEMPLATE                = 'registered_customer'
SALES_TRANSACTION_TEMPLATE                  = 'sales_transaction'
CUSTOMER_TRANSACTION_TEMPLATE               = 'customer_transaction'
CUSTOMER_MEMBERSHIP_TEMPLATE                = 'customer_membership'
REGISTERED_MERCHANT_TEMPLATE                = 'registered_merchant'
MERCHANT_REGISTERED_CUSTOMER_TEMPLATE       = 'merchant_registered_customer'
MERCHANT_CUSTOMER_REWARD_TEMPLATE           = 'customer_reward'
MERCHANT_CUSTOMER_PREPAID_TEMPLATE          = 'customer_prepaid'
MERCHANT_CUSTOMER_REDEMPTION_TEMPLATE       = 'customer_redemption'
USER_VOUCHER_ENTITLED_TEMPLATE              = 'user_voucher_entitled'
USER_VOUCHER_REDEEMED_TEMPLATE              = 'user_voucher_redeemed'
USER_VOUCHER_REMOVED_TEMPLATE               = 'user_voucher_removed'
USER_VOUCHER_ENTITLED_REVERTED_TEMPLATE     = 'user_voucher_entitled_reverted'
USER_VOUCHER_REDEEMED_REVERTED_TEMPLATE     = 'user_voucher_redeemed_reverted'
PARTNERSHIP_REWARD_TRANSACTION_TEMPLATE     = 'partnership_reward_transaction'
TESTING_TEMPLATE                            = 'testing'
    

TABLE_SCHEME_TEMPLATE = {
                    REGISTERED_USER_TEMPLATE                : __REGISTERED_USER_SCHEMA,
                    REGISTERED_CUSTOMER_TEMPLATE            : __REGISTERED_CUSTOMER_SCHEMA,
                    REGISTERED_MERCHANT_TEMPLATE            : __REGISTERED_MERCHANT_SCHEMA,
                    MERCHANT_REGISTERED_CUSTOMER_TEMPLATE   : __MERCHANT_REGISTERED_CUSTOMER_SCHEMA,
                    CUSTOMER_MEMBERSHIP_TEMPLATE            : __CUSTOMER_MEMBERSHIP_SCHEMA,
                    CUSTOMER_TRANSACTION_TEMPLATE           : __MERCHANT_CUSTOMER_TRANSACTION_SCHEMA,
                    SALES_TRANSACTION_TEMPLATE              : __MERCHANT_SALES_TRANSACTION_SCHEMA,
                    MERCHANT_CUSTOMER_REWARD_TEMPLATE       : __MERCHANT_CUSTOMER_REWARD_SCHEMA,
                    MERCHANT_CUSTOMER_PREPAID_TEMPLATE      : __MERCHANT_CUSTOMER_PREPAID_SCHEMA,
                    MERCHANT_CUSTOMER_REDEMPTION_TEMPLATE   : __MERCHANT_CUSTOMER_REDEMPTION_SCHEMA,
                    USER_VOUCHER_ENTITLED_TEMPLATE          : _USER_ENTITLED_VOUCHER_SCHEMA,
                    USER_VOUCHER_REDEEMED_TEMPLATE          : _USER_REDEEMED_VOUCHER_SCHEMA,
                    USER_VOUCHER_REMOVED_TEMPLATE           : _USER_REMOVED_VOUCHER_SCHEMA,
                    USER_VOUCHER_ENTITLED_REVERTED_TEMPLATE : _USER_REVERTED_VOUCHER_SCHEMA,
                    USER_VOUCHER_REDEEMED_REVERTED_TEMPLATE : _USER_REDEEMED_REVERTED_VOUCHER_SCHEMA,
                    PARTNERSHIP_REWARD_TRANSACTION_TEMPLATE : _PARTNERSHIP_REWARD_TRANSACTION_SCHEMA,
                    TESTING_TEMPLATE                        : _TESTING_SCHEMA,
    }
