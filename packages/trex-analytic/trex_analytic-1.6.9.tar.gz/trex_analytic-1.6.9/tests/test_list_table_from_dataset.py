'''
Created on 15 Jan 2021

@author: jacklok
'''
import unittest, logging, sys
from trexanalytics.util.bigquery_util import list_all_table_from_dataset

logger = logging.getLogger('unittest')

class DeleteBigqueryDatasetUnitTestCase(unittest.TestCase):
    def setUp(self):
        pass

        
    def tearDown(self):
        pass
    
    
    
    def test_delete_dataset(self):
        dataset_name    = 'unittest'
        table_list = list_all_table_from_dataset(dataset_name)
        table_name_list = []
        
        for t in table_list:
            table_name_list.append(t.table_id)
        
        logger.debug('table_name_list=%s', table_name_list)    
        
        
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)