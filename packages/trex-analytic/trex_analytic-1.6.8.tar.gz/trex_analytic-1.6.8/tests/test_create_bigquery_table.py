'''
Created on 11 Jan 2021

@author: jacklok
'''

import unittest, logging, sys
from trexlib.utils.google.bigquery_util import create_bigquery_client, create_table_from_template, list_all_table_full_id_from_dataset, detele_table_from_dataset, is_dataset_exist, detele_dataset
from trexanalytics.bigquery_table_template_config import REGISTERED_CUSTOMER_TEMPLATE, REGISTERED_MERCHANT_TEMPLATE, REGISTERED_USER_TEMPLATE, TABLE_SCHEME_TEMPLATE
from trexconf.conf import BIGQUERY_SERVICE_CREDENTIAL_PATH
logger = logging.getLogger('unittest')

dataset_name    = 'unittest'

class CreateBigqueryTableUnitTestCase(unittest.TestCase):
    def setUp(self):
        self.bq_client = create_bigquery_client(credential_filepath=BIGQUERY_SERVICE_CREDENTIAL_PATH)

        
    def tearDown(self):
        pass
    
    
    def test_create_registred_customer_table(self):
        table_name      = REGISTERED_CUSTOMER_TEMPLATE
        
        created_table = create_table_from_template(dataset_name, table_name, TABLE_SCHEME_TEMPLATE.get(REGISTERED_CUSTOMER_TEMPLATE), bigquery_client=self.bq_client)
        
        assert created_table is not None
        
    def test_create_registred_merchant_table(self):
        table_name      = REGISTERED_MERCHANT_TEMPLATE
        
        created_table = create_table_from_template(dataset_name, table_name, TABLE_SCHEME_TEMPLATE.get(REGISTERED_MERCHANT_TEMPLATE), bigquery_client=self.bq_client)
        
        assert created_table is not None
        
    def test_create_registred_user_table(self):
        table_name      = REGISTERED_USER_TEMPLATE
        
        created_table = create_table_from_template(dataset_name, table_name, TABLE_SCHEME_TEMPLATE.get(REGISTERED_USER_TEMPLATE), bigquery_client=self.bq_client)
        
        assert created_table is not None   
        
    
    def test_list_all_table(self):
        tables_list = list_all_table_full_id_from_dataset(dataset_name, bigquery_client=self.bq_client)
        
        assert tables_list is not None           
        assert len(tables_list) == 3
        
        logger.debug('tables_list=%s', tables_list)
        
        #test delete all tables
        
    '''
    def test_delete_registred_customer_table(self):
        dataset_name    = 'unitest'
        table_name      = REGISTERED_CUSTOMER_TEMPLATE
        
        deleted_table = detele_table_from_dataset(dataset_name, table_name)
        
        assert deleted_table is not None    
    '''
        
    
    '''
    
    def test_check_dataset_is_exist(self):
        #bq_client = create_bigquery_client(credential_filepath=BIGQUERY_SERVICE_CREDENTIAL_PATH)
        is_exist = is_dataset_exist(dataset_name, bigquery_client=self.bq_client)
        
        assert is_exist is True
    '''
        
    '''
    def test_delete_dataset(self):
        dataset_name    = 'unitest'
        deleted_dataset = detele_dataset(dataset_name)
        
        assert deleted_dataset is not None    
    '''    
        
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)        
