'''
Created on 18 Jan 2021

@author: jacklok
'''
import unittest, logging
from trexanalytics.util.chart_util import generate_month_before
from datetime import datetime, date
logger = logging.getLogger('unittest')

class TestChartUtil(unittest.TestCase):
    

    def test_generate_month_before(self):
        start_datetime=date(2020,11,30)
        expected_result = generate_month_before(6, start_datetime=start_datetime)
        assert expected_result == [6,7,8,9,10,11]
        
        expected_result = generate_month_before(3, start_datetime=start_datetime)
        assert expected_result == [9,10,11]
        
        expected_result = generate_month_before(1, start_datetime=start_datetime)
        assert expected_result == [11]
        
        expected_result = generate_month_before(0, start_datetime=start_datetime)
        assert expected_result is None
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()