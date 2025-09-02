'''
Created on 12 Jan 2021

@author: jacklok
'''
import unittest, logging, sys
from trexanalytics.controllers.importdata.import_merchant_data_routes import import_registered_merchant_function
from trexmodel.utils.model.model_util import read_service_account_file
from trexanalytics import conf as analytics_conf
from trexmodel import conf as model_conf


logger = logging.getLogger('unittest')

#dataset_name = 'system_analytics'
dataset_name = 'unittest'

class TestImportMerchantData(unittest.TestCase):
    
    def setUp(self):
        datastore_credential_filepath                           = model_conf.DATASTORE_SERVICE_ACCOUNT_KEY_FILEPATH
        (credential_config, data)                               = read_service_account_file(credential_filepath=datastore_credential_filepath)
        self.credential_config                                  = credential_config
        
    def tearDown(self):
        pass

    def test_import_registered_merchant_data(self):
        
        import_count = import_registered_merchant_function(credential_info=self.credential_config, dataset_name=dataset_name)
        logger.debug('import_count=%d', import_count)

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()