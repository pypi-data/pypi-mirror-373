'''
Created on 30 Apr 2021

@author: jacklok
'''
from flask import Blueprint, render_template, session, abort, redirect, url_for, request
import logging, json, uuid
from flask.globals import current_app
from trexlib.utils.google.bigquery_util import create_bigquery_client, stream_data_by_datetime_partition
from trexconf import conf as analytics_conf
from trexanalytics.bigquery_table_template_config import CUSTOMER_TRANSACTION_TEMPLATE
from trexmodel.models.datastore.merchant_models import MerchantAcct
from trexmodel.models.datastore.customer_models import Customer
from trexmodel.utils.model.model_util import create_db_client 
from datetime import datetime
from trexlib.utils.log_util import get_tracelog
from trexanalytics.controllers.importdata.import_data_base_routes import TriggerImportDataBaseResource, InitImportDataBaseResource, ImportDataBaseResource
from flask_restful import Api
from trexlib.utils.string_util import is_not_empty, random_string
from trexanalytics.bigquery_table_template_config import TABLE_SCHEME_TEMPLATE
from trexmodel.models.datastore.transaction_models import CustomerTransaction
from trexconf.conf import MERCHANT_DATASET


import_customer_transaction_data_bp = Blueprint('import_customer_transaction_data_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/analytics/import-customer-transaction-data')

logger = logging.getLogger('import')

import_customer_transaction_data_api = Api(import_customer_transaction_data_bp)

class TriggerImportAllCustomerTransaction(TriggerImportDataBaseResource):
    
    def get_task_url(self):
        return '/import-customer-transaction-data/init-import-all-customer-transaction'
    
    def get_task_queue(self):
        return 'import-customer'
    
    
class InitImportAllCustomerTransaction(InitImportDataBaseResource):
    def get_import_data_count(self, **kwargs):
        count       = count_import_all_customer_transaction_function()
        #count = 1
        return count
    
    def get_import_data_page_size(self):
        return analytics_conf.STREAM_DATA_PAGE_SIZE
    
    def get_task_url(self):
        return '/import-customer-transaction-data/import-all-customer-transaction'
    
    def get_task_queue(self):
        return 'import-customer'
    


class ImportAllCustomerTransaction(ImportDataBaseResource): 
    def import_data(self, offset, limit, **kwargs):
        logger.debug('Going to import data now')
        logger.debug('offset=%d limit=%d', offset, limit)
        
        
        try:
            start_cursor    = kwargs.get('start_cursor')
            batch_id        = kwargs.get('batch_id')
            
            logger.debug('ImportAllCustomerTransaction: start_cursor=%s', start_cursor)
            
            next_cursor     = import_all_customer_transaction_function(dataset_name=MERCHANT_DATASET, limit=limit, start_cursor=start_cursor, batch_id=batch_id)
            
            logger.debug('ImportAllCustomerTransaction: next_cursor=%s', next_cursor)
            
            return next_cursor
        except:
            logger.debug('Failed due to %s', get_tracelog())
        
    
    def get_task_url(self):
        return '/import-customer-transaction-data/import-all-customer-transaction'
    
    def get_task_queue(self):
        return 'import-customer'
    
def count_import_all_customer_transaction_function():     
    
    credential_info = current_app.config['credential_config']
        
    db_client = create_db_client(info=credential_info, caller_info="count_import_all_customer_transaction_function")
    with db_client.context():
        count = CustomerTransaction.count()
        
    return count

def import_all_customer_transaction_function(credential_info=None, dataset_name=MERCHANT_DATASET, 
                                            limit=analytics_conf.STREAM_DATA_PAGE_SIZE, start_cursor=None, batch_id=None):     
    
    bg_client       = create_bigquery_client(credential_filepath=analytics_conf.BIGQUERY_SERVICE_CREDENTIAL_PATH, project_id=analytics_conf.BIGQUERY_GCLOUD_PROJECT_ID)
    
    if credential_info is None:
        credential_info = current_app.config['credential_config']
        
    db_client                                   = create_db_client(info=credential_info, caller_info="import_all_customer_transaction_function")
    customer_transaction_data_dict_to_stream    = {}
    import_datetime                             = datetime.now()
    
    logger.debug('import_all_customer_transaction_function (%s): start_cursor=%s', batch_id, start_cursor)
    
    with db_client.context():
        (customer_transaction_list, next_cursor) = CustomerTransaction.list_all(limit = limit, start_cursor=start_cursor, return_with_cursor=True)
        import_count  = len(customer_transaction_list)
        
        for ct in customer_transaction_list:
            merchant_acct           = ct.transact_merchant_acct
            merchant_account_code   = merchant_acct.account_code.replace('-','')
            
            customer_transaction_dict_list = customer_transaction_data_dict_to_stream.get(merchant_account_code)
            
            if customer_transaction_dict_list is None:
                customer_transaction_dict_list = []
            
            customer_transaction_dict_list.append({
                                            "Key"                   : uuid.uuid1().hex,
                                            "UserKey"               : ct.transact_user_acct_key,
                                            "CustomerKey"           : ct.transact_customer_key,
                                            "MerchantKey"           : ct.transact_merchant_acct_key,
                                            "TransactOutlet"        : ct.transact_outlet_key,
                                            "TransactionId"         : ct.transaction_id,
                                            "InvoiceId"             : ct.invoice_id,
                                            "TransactAmount"        : ct.transact_amount,
                                            "TransactDateTime"      : ct.transact_datetime,
                                            'Reverted'              : False,
                                            'RevertedDateTime'      : None,
                                            "UpdatedDateTime"       : import_datetime,
                                            })
            
            
    
    
    
            customer_transaction_data_dict_to_stream = {merchant_account_code : customer_transaction_dict_list}
    
    logger.debug('################################ batch_id= %s ############################################', batch_id)
    logger.debug(customer_transaction_data_dict_to_stream)
    logger.debug('#####################################################################################################')
    
    errors = stream_data_by_datetime_partition(bg_client, dataset_name, CUSTOMER_TRANSACTION_TEMPLATE, 
                                               TABLE_SCHEME_TEMPLATE.get(CUSTOMER_TRANSACTION_TEMPLATE), customer_transaction_data_dict_to_stream, 
                                               column_name_used_to_partition='TransactDateTime', 
                                               partition_date=True,
                                               )
    
    bg_client.close()
    
    if errors==[]:
        logger.debug("New rows have been added")
    else:
        logger.debug("Encountered errors while inserting rows: {}".format(errors))
    
    logger.debug('import_count=%d', import_count)
    
    return next_cursor

@import_customer_transaction_data_bp.route('/count-all-customer-transaction')
def count_customer_transaction():
    count = count_import_all_customer_transaction_function()
    return 'Total count=%s'% count


import_customer_transaction_data_api.add_resource(TriggerImportAllCustomerTransaction,   '/trigger-import-all-customer-transaction')
import_customer_transaction_data_api.add_resource(InitImportAllCustomerTransaction,   '/init-import-all-customer-transaction')
import_customer_transaction_data_api.add_resource(ImportAllCustomerTransaction,       '/import-all-customer-transaction')

