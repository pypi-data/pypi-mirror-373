'''
Created on 15 Jan 2021

@author: jacklok
'''

import unittest, logging, sys
from trexanalytics.controllers.importdata.import_customer_data_routes import import_merchant_registered_customer_function, import_merchant_customer_changes
from trexmodel.models.datastore.customer_models import Customer
from trexmodel.utils.model.model_util import read_service_account_file
from trexanalytics import conf as analytics_conf
from trexmodel import conf as model_conf
from datetime import datetime, date
from trexmodel.utils.model.model_util import create_db_client 

dataset_name = 'unittest'

class TestImportMerchantCustomerData(unittest.TestCase):
    
    def setUp(self):
        credential_filepath                         = model_conf.DATASTORE_SERVICE_ACCOUNT_KEY_FILEPATH
        (credential_config, data)                   = read_service_account_file(credential_filepath=credential_filepath)
        self.credential_config                      = credential_config
        
    def tearDown(self):
        pass
    
    
    def test_import_registered_customer_data(self):
        merchant_acct_key = 'ahBufnRyZXgtYWRtaW4tZGV2chkLEgxNZXJjaGFudEFjY3QYgICAmMX2ggoM'
        
        import_merchant_registered_customer_function(credential_info=self.credential_config, dataset_name=dataset_name,
                                                                    merchant_acct_key = merchant_acct_key, 
                                                                    partition_date=True, limit=10)
        
    def test_import_changed_customer_data(self):
        db_client = create_db_client(info=self.credential_config, caller_info="count_import_all_registered_customer_function")
        with db_client.context():
            customers = Customer.list_all(offset=0, limit=1)
        
        assert len(customers)>0
        customer = customers[0]
        
        customer.birth_date = date(1977,2,2)
        
        assert customer is not None
        errors = import_merchant_customer_changes(customer, credential_info=self.credential_config, dataset_name=dataset_name,
                                                                    )    
        assert len(errors)==0

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()