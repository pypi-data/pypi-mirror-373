
'''
Created on 18 Jan 2021

@author: jacklok
'''
import dateutil.relativedelta
from datetime import datetime
from trexlib.utils.common.common_util import sort_list

def generate_month_before(number_of_months, start_datetime=None):
    if number_of_months and isinstance(number_of_months, int):
        if start_datetime is None:
            start_datetime = datetime.now()
        
            
        
        return sorted([ (start_datetime + dateutil.relativedelta.relativedelta(months=-n)).month for n in range(number_of_months)])
