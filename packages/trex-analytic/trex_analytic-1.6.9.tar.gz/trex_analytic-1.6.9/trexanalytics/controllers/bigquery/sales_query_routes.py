'''
Created on 12 Jun 2025

@author: jacklok
'''

from flask import Blueprint
import logging
from trexlib.utils.google.bigquery_util import process_job_result_into_category_and_count
from trexanalytics.controllers.bigquery.query_base_routes import CachedQueryBaseResource
from flask_restful import Api
from trexconf.conf import BIGQUERY_GCLOUD_PROJECT_ID, SYSTEM_DATASET, MERCHANT_DATASET
from datetime import datetime
from trexlib.utils.string_util import is_empty, is_not_empty


sales_analytics_data_bp = Blueprint('sales_analytics_data_bp', __name__,
                                 template_folder='templates',
                                 static_folder='static',
                                 url_prefix='/analytics/sales')

logger = logging.getLogger('analytics')

query_sales_data_api = Api(sales_analytics_data_bp)

@sales_analytics_data_bp.route('/index')
def query_sales_index(): 
    return 'ping', 200

class QueryMerchantSalesDataByDateRangeBaseResource(CachedQueryBaseResource):
    
    def prepare_query(self, **kwrgs):
        account_code      = kwrgs.get('account_code')
        date_range_from   = kwrgs.get('date_range_from')
        date_range_to     = kwrgs.get('date_range_to')
        
        account_code = account_code.replace('-','')
        
        logger.info('account_code=%s', account_code)
        logger.info('date_range_from=%s', date_range_from)
        logger.info('date_range_to=%s', date_range_to)
        
        condition = ''
        
        if date_range_from and date_range_to:
            date_range_from = datetime.strptime(date_range_from, '%Y%m%d')
            date_range_from = datetime.strftime(date_range_from, '%Y-%m-%d %H:%M:%S')
            
            date_range_to = datetime.strptime(date_range_to, '%Y%m%d')
            date_range_to = datetime.strftime(date_range_to, '%Y-%m-%d %H:%M:%S')
            
            condition = "WHERE PartitionDateTime BETWEEN DATETIME('{date_range_from}') and DATETIME('{date_range_to}')".format(date_range_from=date_range_from,date_range_to=date_range_to)
        
        return self.prepare_query_with_condition(account_code, condition)
    
    def prepare_query_with_condition(self, account_code, condition):
        pass    

class QueryMerchantSalesAmountByDateRangeResource(QueryMerchantSalesDataByDateRangeBaseResource):
    
    
    
    def prepare_query_with_condition(self, account_code, where_condition):
        dataset = '%s_%s' % (MERCHANT_DATASET,account_code)
        query = '''
            SELECT sum(TransactAmount) as TotalSalesAmount
                FROM `{project_id}.{dataset_name}.sales_transaction`
                {where_condition}
                        
            '''.format(project_id=BIGQUERY_GCLOUD_PROJECT_ID, dataset_name=dataset, where_condition=where_condition, account_code=account_code)    
            
        query= '''
            
                SELECT sum(TransactAmount) as TotalSalesAmount
                    FROM (
                        SELECT
                          TransactDateTime,
                          TransactionId,
                          TransactAmount,
                          Reverted,
                          UpdatedDateTime
                        FROM (
                        
                        SELECT
                          TransactDateTime,
                          TransactionId,
                          TransactAmount,
                          Reverted,
                          UpdatedDateTime,
                          FIRST_VALUE(Reverted) OVER (PARTITION BY TransactionId ORDER BY UpdatedDateTime DESC) AS latest_status
                        FROM `{project_id}.{dataset_name}.sales_transaction`
                        {where_condition}
                        )
                        WHERE latest_status=False
                    )
        '''.format(project_id=BIGQUERY_GCLOUD_PROJECT_ID, dataset_name=dataset, where_condition=where_condition, account_code=account_code)
        
        return query 
    
    
    def process_query_result(self, job_result_rows):
        row_list = []
        if job_result_rows and is_not_empty(job_result_rows):
            for row in job_result_rows:
                #logger.debug(row)
                column_dict = {}
                column_dict['amount']  = row.get('TotalSalesAmount')
                row_list.append(column_dict)
        
        if is_empty(row_list):
            row_list.append({'amount':0})
            
        
        return row_list    
    
class QueryMerchantSalesAmountGroupByYearMonthByDateRangeResource(QueryMerchantSalesDataByDateRangeBaseResource):
    
    
    
    def prepare_query_with_condition(self, account_code, condition):
        dataset = '%s_%s' % (MERCHANT_DATASET,account_code)
        query = '''
            SELECT FORMAT_DATETIME('%Y-%m', TransactDateTime) as year_month, sum(TransactAmount) as TotalTransactAmount
            FROM (
                SELECT TransactDateTime, TransactAmount
                FROM `{project_id}.{dataset_name}.sales_transaction`
                {where_condition}
                
            ) GROUP BY year_month            
            '''.format(project_id=BIGQUERY_GCLOUD_PROJECT_ID, dataset_name=dataset, where_condition=condition, account_code=account_code)    
            
        return query 
    
    
    def process_query_result(self, job_result_rows):
        return process_job_result_into_category_and_count(job_result_rows)    

query_sales_data_api.add_resource(QueryMerchantSalesAmountByDateRangeResource,                      '/merchant-sales-amount-by-date-range')
query_sales_data_api.add_resource(QueryMerchantSalesAmountGroupByYearMonthByDateRangeResource,      '/merchant-sales-amount-group-by-year-month-by-date-range')
