'''
Created on 19 Jan 2021

@author: jacklok
'''
import unittest
from main import app


class Test(unittest.TestCase):


    def test_ping(self):
        response = app.test_client().get('/ping')

        assert response.status_code == 200
        assert response.data == b'ping'



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_hello']
    unittest.main()