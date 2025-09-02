'''
Created on 15 Jan 2021

@author: jacklok
'''
import unittest, logging, sys
from trexanalytics.util.bigquery_util import detele_dataset

logger = logging.getLogger('unittest')

class DeleteBigqueryDatasetUnitTestCase(unittest.TestCase):
    def setUp(self):
        pass

        
    def tearDown(self):
        pass
    
    
    
    def test_delete_dataset(self):
        dataset_name    = 'unitest'
        deleted_dataset = detele_dataset(dataset_name)
        
        assert deleted_dataset is not None    
        
        
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)