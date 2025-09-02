'''
Created on 21 Jan 2021

@author: jacklok
'''
import unittest, logging, sys
from trexlib.utils.google.cloud_tasks_util import create_task

logger = logging.getLogger('unittest')

class TestCryptoUtil(unittest.TestCase):
    
    def test_create_task(self):
        task_url = 'https://trex-analytics-dev.df.r.appspot.com/ping'
        queue_name = 'common'
        create_task(task_url, queue_name, in_seconds=1, http_method = 'GET')
        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()        
