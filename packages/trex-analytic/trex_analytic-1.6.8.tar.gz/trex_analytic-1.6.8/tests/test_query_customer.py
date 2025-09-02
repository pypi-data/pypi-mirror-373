'''
Created on 19 Jan 2021

@author: jacklok
'''
import unittest, logging, sys
from main import app

logger = logging.getLogger('unittest')

system_dataset_name = 'system'

class QueryCustomerUnitTestCase(unittest.TestCase):
    def test_query_registered_customer_blueprint_index(self):
        response = app.test_client().get('/biqquery/customer/index')

        assert response.status_code == 200
        assert response.data == b'ping'
       
    def test_query_registered_customer_by_year_month(self):
        response = app.test_client().get('/biqquery/customer/registered-customer-by-year-month', json={'date_range_from': 202101, 'date_range_to': 202112})
        
        logger.debug('response=%s', response)

        assert response.status_code == 200
        #assert response.data == b'ping'    
        
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()