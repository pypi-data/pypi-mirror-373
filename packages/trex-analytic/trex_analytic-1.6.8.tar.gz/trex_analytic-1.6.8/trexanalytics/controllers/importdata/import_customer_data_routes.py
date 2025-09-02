'''
Created on 13 Jan 2021

@author: jacklok
'''

from flask import Blueprint, render_template, session, abort, redirect, url_for, request
import logging, json, uuid
from flask.globals import current_app
from trexlib.utils.google.bigquery_util import create_bigquery_client, stream_data_by_datetime_partition
from trexconf import conf as analytics_conf
from trexanalytics.bigquery_table_template_config import REGISTERED_CUSTOMER_TEMPLATE, MERCHANT_REGISTERED_CUSTOMER_TEMPLATE
from trexmodel.models.datastore.merchant_models import MerchantAcct
from trexmodel.models.datastore.customer_models import Customer
from trexmodel.utils.model.model_util import create_db_client 
from datetime import datetime
from trexlib.utils.log_util import get_tracelog
from trexanalytics.controllers.importdata.import_data_base_routes import TriggerImportDataBaseResource, InitImportDataBaseResource, ImportDataBaseResource
from flask_restful import Api
from trexlib.utils.string_util import is_not_empty, random_string
from trexanalytics.bigquery_table_template_config import TABLE_SCHEME_TEMPLATE


import_customer_data_bp = Blueprint('import_customer_data_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/analytics/import-customer-data')

logger = logging.getLogger('import')

import_customer_data_api = Api(import_customer_data_bp)


class TriggerImportAllRegisteredCustomer(TriggerImportDataBaseResource):
    
    def get_task_url(self):
        return '/import-customer-data/init-import-all-registered-customer'
    
    def get_task_queue(self):
        return 'import-customer'
    
    
    
    
class InitImportAllRegisteredCustomer(InitImportDataBaseResource):
    def get_import_data_count(self, **kwargs):
        count       = count_import_all_registered_customer_function()
        #count = 1
        return count
    
    def get_import_data_page_size(self):
        return analytics_conf.STREAM_DATA_PAGE_SIZE
    
    def get_task_url(self):
        return '/import-customer-data/import-all-registered-customer'
    
    def get_task_queue(self):
        return 'import-customer'
    


class ImportAllRegisteredCustomer(ImportDataBaseResource): 
    def import_data(self, offset, limit, **kwargs):
        logger.debug('Going to import data now')
        logger.debug('offset=%d limit=%d', offset, limit)
        
        
        try:
            start_cursor    = kwargs.get('start_cursor')
            batch_id        = kwargs.get('batch_id')
            
            logger.debug('ImportAllRegisteredCustomer: start_cursor=%s', start_cursor)
            
            next_cursor     = import_all_registered_customer_function(dataset_name='system', limit=limit, start_cursor=start_cursor, batch_id=batch_id)
            
            logger.debug('ImportAllRegisteredCustomer: next_cursor=%s', next_cursor)
            
            return next_cursor
        except:
            logger.debug('Failed due to %s', get_tracelog())
        
    
    def get_task_url(self):
        return '/import-customer-data/import-all-registered-customer'
    
    def get_task_queue(self):
        return 'import-customer'
    
def count_import_all_registered_customer_function():     
    
    credential_info = current_app.config['credential_config']
        
    db_client = create_db_client(info=credential_info, caller_info="count_import_all_registered_customer_function")
    with db_client.context():
        count = Customer.count()
        
    return count

def import_all_registered_customer_function(credential_info=None, dataset_name='system_dataset', 
                                            limit=analytics_conf.STREAM_DATA_PAGE_SIZE, start_cursor=None, batch_id=None):     
    
    bg_client       = create_bigquery_client(credential_filepath=analytics_conf.BIGQUERY_SERVICE_CREDENTIAL_PATH, project_id=analytics_conf.BIGQUERY_GCLOUD_PROJECT_ID)
    
    if credential_info is None:
        credential_info = current_app.config['credential_config']
        
    db_client = create_db_client(info=credential_info, caller_info="import_registered_customer_function")
    customer_dict_list = []
    import_datetime         = datetime.now()
    
    logger.debug('import_all_registered_customer_function (%s): start_cursor=%s', batch_id, start_cursor)
    
    with db_client.context():
        (customer_list, next_cursor) = Customer.list_all(limit = limit, start_cursor=start_cursor, return_with_cursor=True)
        import_count  = len(customer_list)
        
        for c in customer_list:
            customer_dict_list.append({
                                            "Key"                   : uuid.uuid1().hex,
                                            "UserKey"               : c.registered_user_acct_key,
                                            "CustomerKey"           : c.key_in_str,
                                            "MerchantKey"           : c.registered_merchant_acct_key,
                                            "DOB"                   : c.birth_date,
                                            "Gender"                : c.gender,
                                            "MobilePhone"           : c.mobile_phone,
                                            "Email"                 : c.email,
                                            "MobileAppInstall"      : c.mobile_app_installed,
                                            "RegisteredDateTime"    : c.registered_datetime,
                                            "RegisteredOutlet"      : c.registered_outlet_key,
                                            "UpdatedDateTime"       : import_datetime,
                                            })
    
    customer_data_dict_to_stream = {'':customer_dict_list}
    
    logger.debug('################################ batch_id= %s ############################################', batch_id)
    logger.debug(customer_data_dict_to_stream)
    logger.debug('#####################################################################################################')
    
    errors = stream_data_by_datetime_partition(bg_client, dataset_name, REGISTERED_CUSTOMER_TEMPLATE, 
                                               TABLE_SCHEME_TEMPLATE.get(REGISTERED_CUSTOMER_TEMPLATE), customer_data_dict_to_stream, 
                                               column_name_used_to_partition='RegisteredDateTime', 
                                               partition_date=True,
                                               )
    
    bg_client.close()
    
    if errors==[]:
        logger.debug("New rows have been added")
    else:
        logger.debug("Encountered errors while inserting rows: {}".format(errors))
    
    logger.debug('import_count=%d', import_count)
    
    return next_cursor

class TriggerImportMerchantRegisteredCustomer(TriggerImportDataBaseResource):
    
    def get_task_url(self):
        return '/import-customer-data/init-import-merchant-registered-customer'
    
    def get_task_queue(self):
        return 'import-customer'
    
    def get_data_payload(self):
        merchant_acct_key = request.args.get('merchant_acct_key')
        return {
                'merchant_acct_key': merchant_acct_key
                }
    
    
class InitImportMerchantRegisteredCustomer(InitImportDataBaseResource):
    def get_import_data_count(self, **kwargs):
        
        merchant_acct_key = kwargs.get('merchant_acct_key')
        
        logger.debug('InitImportMerchantRegisteredCustomer: merchant_acct_key=%s', merchant_acct_key)
        
        count       = count_import_merchant_registered_customer_function(merchant_acct_key)
        return count
    
    def get_import_data_page_size(self):
        return analytics_conf.STREAM_DATA_PAGE_SIZE
    
    def get_task_url(self):
        return '/import-customer-data/import-merchant-registered-customer'
    
    def get_task_queue(self):
        return 'import-customer'
    
    def get_data_payload(self):
        content             = request.args.to_dict() or request.json or {}
        merchant_acct_key   = content.get('merchant_acct_key')
        
        return {
                'merchant_acct_key': merchant_acct_key
                }


class ImportMerchantRegisteredCustomer(ImportDataBaseResource): 
    def import_data(self, offset, limit, **kwargs):
        logger.debug('Going to import data now')
        logger.debug('offset=%d limit=%d', offset, limit)
        
        try:
            merchant_acct_key       = kwargs.get('merchant_acct_key')
            start_cursor            = kwargs.get('start_cursor')
            batch_id                = kwargs.get('batch_id')
            (errors, next_cursor)   = import_merchant_registered_customer_function(dataset_name='merchant', merchant_acct_key=merchant_acct_key,  
                                                         limit=limit, 
                                                         start_cursor=start_cursor, batch_id=batch_id)
        except:
            logger.debug('Failed due to %s', get_tracelog())
        
        return next_cursor
    
    def get_task_url(self):
        return '/import-customer-data/import-merchant-registered-customer'
    
    def get_task_queue(self):
        return 'import-customer'
    
    def get_data_payload(self):
        content             = request.args.to_dict() or request.json or {}
        merchant_acct_key   = content.get('merchant_acct_key')
        
        return {
                'merchant_acct_key': merchant_acct_key
                }

def count_import_merchant_registered_customer_function(merchant_acct_key):     
    
    credential_info = current_app.config['credential_config']
        
    db_client = create_db_client(info=credential_info, caller_info="count_import_all_registered_customer_function")
    with db_client.context():
        merchant_acct = None
        if is_not_empty(merchant_acct_key):
            merchant_acct       = MerchantAcct.fetch(merchant_acct_key)
        count = Customer.count_merchant_customer(merchant_acct)
        
    return count


def import_merchant_registered_customer_function(credential_info=None, dataset_name='merchant', merchant_acct_key=None,
                                            partition_date = True, 
                                            limit=analytics_conf.STREAM_DATA_PAGE_SIZE, start_cursor=None, batch_id=None):     
    
    bg_client       = create_bigquery_client(credential_filepath=analytics_conf.BIGQUERY_SERVICE_CREDENTIAL_PATH, project_id=analytics_conf.BIGQUERY_GCLOUD_PROJECT_ID)
    
    if credential_info is None:
        credential_info = current_app.config['credential_config']
        
    db_client = create_db_client(info=credential_info, caller_info="import_registered_customer_function")
    customer_list_dict      = {}
    import_datetime         = datetime.now()
    
    logger.debug('import_merchant_registered_customer_function: merchant_acct_key=%s', merchant_acct_key)
    
    with db_client.context():
        if is_not_empty(merchant_acct_key):
            merchant_acct = MerchantAcct.fetch(merchant_acct_key)
            (customer_list, next_cursor) = Customer.list_merchant_customer(merchant_acct, limit = limit, 
                                                                           start_cursor=start_cursor, return_with_cursor=True)
        else:
            customer_list = Customer.list_all(limit = limit, start_cursor=start_cursor)
        
        import_count  = len(customer_list)
        
        for c in customer_list:
            
            merchant_acct   = c.registered_merchant_acct
            account_code    = merchant_acct.account_code
            account_code    = account_code.replace('-','')
            
            customer_list = customer_list_dict.get(account_code)
            if customer_list is None:
                customer_list = []
            
            customer_list.append({
                                            "Key"                   : uuid.uuid1().hex,
                                            "UserKey"               : c.registered_user_acct_key,
                                            "CustomerKey"           : c.key_in_str,
                                            "DOB"                   : c.birth_date,
                                            "Gender"                : c.gender,
                                            "MobilePhone"           : c.mobile_phone,
                                            "Email"                 : c.email,
                                            "MobileAppInstall"      : c.mobile_app_installed,
                                            "RegisteredDateTime"    : c.registered_datetime,
                                            "RegisteredOutlet"      : c.registered_outlet_key,
                                            "UpdatedDateTime"       : import_datetime,
                                            })
            
            customer_list_dict[account_code] = customer_list
            
    logger.debug('################################ batch_id= %s ############################################', batch_id)
    logger.debug(customer_list_dict)
    logger.debug('#####################################################################################################')        
    
    errors = stream_data_by_datetime_partition(bg_client, dataset_name, MERCHANT_REGISTERED_CUSTOMER_TEMPLATE, 
                                               TABLE_SCHEME_TEMPLATE.get(MERCHANT_REGISTERED_CUSTOMER_TEMPLATE), customer_list_dict, 
                                               column_name_used_to_partition='RegisteredDateTime',partition_date=partition_date
                             )
    
    bg_client.close()
    
    if errors==[]:
        logger.debug("New rows have been added")
    else:
        logger.debug("Encountered errors while inserting rows: {}".format(errors))
    
    logger.debug('import_count=%d', import_count)
    
    return (errors,next_cursor)

@import_customer_data_bp.route('/count-all-registered-customer')
def count_registered_customer():
    count = count_import_all_registered_customer_function()
    return count, 200

@import_customer_data_bp.route('/trigger-import-customer/<customer_key>')
def trigger_customer_changes(customer_key):
    
    import_merchant_customer_changes(customer_key)
    
    return 'Completed', 200
    
def import_merchant_customer_changes(customer_key, credential_info=None):
    bg_client       = create_bigquery_client(credential_filepath=analytics_conf.BIGQUERY_SERVICE_CREDENTIAL_PATH, project_id=analytics_conf.BIGQUERY_GCLOUD_PROJECT_ID)
    
    if credential_info is None:
        credential_info = current_app.config['credential_config']
    
    db_client = create_db_client(info=credential_info, caller_info="import_registered_customer_function")
    merchant_customer_list_dict     = {}
    registered_customer_list_dict   = {}
    import_datetime                 = datetime.now()
    
    with db_client.context():
        customer = Customer.fetch(customer_key)
        merchant_acct   = customer.registered_merchant_acct
        account_code    = merchant_acct.account_code
        account_code    = account_code.replace('-','')
        registered_customer_list_dict[""] = [{
                                            "Key"                   : uuid.uuid1().hex,
                                            "UserKey"               : customer.registered_user_acct_key,
                                            "CustomerKey"           : customer.key_in_str,
                                            "MerchantKey"           : customer.registered_merchant_acct_key,
                                            "DOB"                   : customer.birth_date,
                                            "Gender"                : customer.gender,
                                            "MobilePhone"           : customer.mobile_phone,
                                            "Email"                 : customer.email,
                                            "MobileAppInstall"      : customer.mobile_app_installed,
                                            "RegisteredDateTime"    : customer.registered_datetime,
                                            "RegisteredOutlet"      : customer.registered_outlet_key,
                                            "UpdatedDateTime"       : import_datetime,
                                            }]
        merchant_customer_list_dict[account_code] = [{
                                            "Key"                   : uuid.uuid1().hex,
                                            "UserKey"               : customer.registered_user_acct_key,
                                            "CustomerKey"           : customer.key_in_str,
                                            "DOB"                   : customer.birth_date,
                                            "Gender"                : customer.gender,
                                            "MobilePhone"           : customer.mobile_phone,
                                            "Email"                 : customer.email,
                                            "MobileAppInstall"      : customer.mobile_app_installed,
                                            "RegisteredDateTime"    : customer.registered_datetime,
                                            "RegisteredOutlet"      : customer.registered_outlet_key,
                                            "UpdatedDateTime"       : import_datetime,
                                            }]
            
        
    
    logger.debug('#####################################################################################################')
    logger.debug(merchant_customer_list_dict)
    logger.debug('#####################################################################################################')        
    errors = []
    
    errors1 = stream_data_by_datetime_partition(bg_client, 'merchant', MERCHANT_REGISTERED_CUSTOMER_TEMPLATE, 
                                               TABLE_SCHEME_TEMPLATE.get(MERCHANT_REGISTERED_CUSTOMER_TEMPLATE), merchant_customer_list_dict, 
                                               column_name_used_to_partition='RegisteredDateTime', partition_date=True
                                               )
    
    errors2 = stream_data_by_datetime_partition(bg_client, 'system', REGISTERED_CUSTOMER_TEMPLATE, 
                                               TABLE_SCHEME_TEMPLATE.get(REGISTERED_CUSTOMER_TEMPLATE), registered_customer_list_dict, 
                                               column_name_used_to_partition='RegisteredDateTime', partition_date=True
                                               )
    errors.extend(errors1)
    errors.extend(errors2)
    
    bg_client.close()
    
    if errors==[]:
        logger.debug("New rows have been added")
    else:
        logger.debug("Encountered errors while inserting rows: {}".format(errors))
    
    return errors


import_customer_data_api.add_resource(TriggerImportAllRegisteredCustomer,   '/trigger-import-all-registered-customer')
import_customer_data_api.add_resource(InitImportAllRegisteredCustomer,      '/init-import-all-registered-customer')
import_customer_data_api.add_resource(ImportAllRegisteredCustomer,          '/import-all-registered-customer')

import_customer_data_api.add_resource(TriggerImportMerchantRegisteredCustomer,   '/trigger-import-merchant-registered-customer')
import_customer_data_api.add_resource(InitImportMerchantRegisteredCustomer,      '/init-import-merchant-registered-customer')
import_customer_data_api.add_resource(ImportMerchantRegisteredCustomer,          '/import-merchant-registered-customer')


