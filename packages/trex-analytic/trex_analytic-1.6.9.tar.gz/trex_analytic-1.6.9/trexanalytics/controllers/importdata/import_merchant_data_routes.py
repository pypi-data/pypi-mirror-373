'''
Created on 12 Jan 2021

@author: jacklok
'''

from flask import Blueprint
import logging, uuid
from trexlib.utils.google.bigquery_util import create_bigquery_client, stream_data_by_datetime_partition
from trexconf import conf as analytics_conf
from trexanalytics.bigquery_table_template_config import REGISTERED_MERCHANT_TEMPLATE
from trexmodel.models.datastore.merchant_models import MerchantAcct

from trexmodel.utils.model.model_util import create_db_client 
from trexconf.conf import MAX_FETCH_RECORD
from datetime import datetime
from trexlib.utils.log_util import get_tracelog
from trexanalytics.controllers.importdata.import_data_base_routes import TriggerImportDataBaseResource, InitImportDataBaseResource, ImportDataBaseResource
from flask_restful import Api
from trexanalytics.bigquery_table_template_config import TABLE_SCHEME_TEMPLATE


import_merchant_data_bp = Blueprint('import_merchant_data_bp', __name__,
                     template_folder='templates',
                     static_folder='static',
                     url_prefix='/analytics/import-merchant-data')



logger = logging.getLogger('import')

import_merchant_data_api = Api(import_merchant_data_bp)

class TriggerPing(TriggerImportDataBaseResource):
    
    def get_task_url(self):
        return '/import-merchant-data/init-ping'
    
    def get_task_queue(self):
        return 'common'
    
class InitPing(InitImportDataBaseResource):
    pass    


class TriggerImportMerchantAcct(TriggerImportDataBaseResource):
    
    def get_task_url(self):
        return '/import-merchant-data/init-import-merchant-acct'
    
    def get_task_queue(self):
        return 'import-merchant'
    
    
    
    
class InitImportMerchantAcct(InitImportDataBaseResource):
    def get_import_data_count(self, **kwargs):
        count       = count_registered_merchant_function()
        return count
    
    def get_import_data_page_size(self):
        return analytics_conf.STREAM_DATA_PAGE_SIZE
    
    def get_task_url(self):
        return '/import-merchant-data/import-merchant-acct'
    
    def get_task_queue(self):
        return 'import-merchant'
    


class ImportMerchantAcct(ImportDataBaseResource): 
    def import_data(self, offset, limit, **kwargs):
        logger.debug('Going to import data now')
        logger.debug('offset=%d limit=%d', offset, limit)
        
        partition_month = datetime.now()
        try:
            start_cursor    = kwargs.get('start_cursor')
            batch_id        = kwargs.get('batch_id')
            
            logger.debug('ImportMerchantAcct: start_cursor=%s', start_cursor)
            logger.debug('ImportMerchantAcct: batch_id=%s', batch_id)
            
            next_cursor     = import_registered_merchant_function(dataset_name='system',  
                                                                      limit=limit, start_cursor=start_cursor, batch_id=batch_id)
            
            logger.debug('ImportAllRegisteredCustomer: next_cursor=%s', next_cursor)
            
            return next_cursor
        except:
            logger.debug('Failed due to %s', get_tracelog())
        
    
    def get_task_url(self):
        return '/import-merchant-data/import-merchant-acct'
    
    def get_task_queue(self):
        return 'import-merchant'

    
def import_registered_merchant_function(dataset_name='system', limit=analytics_conf.STREAM_DATA_PAGE_SIZE, start_cursor=None, batch_id=None):     
    
    bg_client       = create_bigquery_client(credential_filepath=analytics_conf.BIGQUERY_SERVICE_CREDENTIAL_PATH, project_id=analytics_conf.BIGQUERY_GCLOUD_PROJECT_ID)
    db_client = create_db_client(caller_info="import_registered_merchant")
    merchant_acct_dict_list = []
    import_datetime         = datetime.now()
    with db_client.context():
        (merchant_acct_list, next_cursor) = MerchantAcct.list_all(limit = limit, start_cursor=start_cursor, return_with_cursor=True)
        
        
        for m in merchant_acct_list:
            merchant_acct_dict_list.append({
                                            'Key'                   : uuid.uuid1().hex,
                                            'MerchantKey'           : m.key_in_str,
                                            'CompanyName'           : m.company_name,
                                            'RegisteredDateTime'    : m.registered_datetime,
                                            'UpdatedDateTime'       : import_datetime,
                                            })
        
    
    merchant_data_dict_to_stream = {'':merchant_acct_dict_list}
    logger.debug('################################ batch_id= %s ############################################', batch_id)
    logger.debug(merchant_data_dict_to_stream)
    logger.debug('#####################################################################################################')
    
    errors = stream_data_by_datetime_partition(bg_client, dataset_name, REGISTERED_MERCHANT_TEMPLATE, 
                                               TABLE_SCHEME_TEMPLATE.get(REGISTERED_MERCHANT_TEMPLATE), merchant_data_dict_to_stream, 
                                               column_name_used_to_partition = 'RegisteredDateTime',
                                               partition_year=True
                         )
    
    bg_client.close()
    
    if errors==[]:
        logger.debug("New rows have been added")
    else:
        logger.debug("Encountered errors while inserting rows: {}".format(errors))
        
    return next_cursor

def count_registered_merchant_function():
    db_client = create_db_client(caller_info="count_registered_merchant_function")
    with db_client.context():
        count = MerchantAcct.count(limit = MAX_FETCH_RECORD)
        
    return count

@import_merchant_data_bp.route('/count-merchant-acct')
def count_registered_customer():
    count = count_registered_merchant_function()
    return count, 200


import_merchant_data_api.add_resource(TriggerImportMerchantAcct,   '/trigger-import-merchant-acct')
import_merchant_data_api.add_resource(InitImportMerchantAcct,      '/init-import-merchant-acct')
import_merchant_data_api.add_resource(ImportMerchantAcct,          '/import-merchant-acct')

import_merchant_data_api.add_resource(TriggerPing,          '/trigger-ping')
import_merchant_data_api.add_resource(InitPing,          '/init-ping')


