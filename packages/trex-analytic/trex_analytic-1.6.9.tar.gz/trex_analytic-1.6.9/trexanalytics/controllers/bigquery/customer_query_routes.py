'''
Created on 18 Jan 2021

@author: jacklok
'''
from flask import Blueprint
import logging
from trexlib.utils.google.bigquery_util import process_job_result_into_category_and_count, execute_query
from trexanalytics.controllers.bigquery.query_base_routes import CategoryAndCountQueryBaseResource,\
    CachedQueryBaseResource,\
    QueryBaseResource, BaseResource
from flask_restful import Api
from trexconf.conf import BIGQUERY_GCLOUD_PROJECT_ID, SYSTEM_DATASET, MERCHANT_DATASET
from datetime import datetime
from trexlib.libs.flask_wtf.request_wrapper import request_values
from trexlib.utils.common.cache_util import cache
from trexlib.utils.common.date_util import date_str_to_bigquery_qualified_datetime_str,\
    date_to_bigquery_qualified_datetime_str


customer_analytics_data_bp = Blueprint('customer_analytics_data_bp', __name__,
                                 template_folder='templates',
                                 static_folder='static',
                                 url_prefix='/analytics/cust')

logger = logging.getLogger('analytics')

query_customer_data_api = Api(customer_analytics_data_bp)

@customer_analytics_data_bp.route('/index')
def query_customer_index(): 
    return 'ping', 200


class QueryAllCustomerGrowthByYearMonth(CategoryAndCountQueryBaseResource):
    def prepare_query(self, **kwrgs):
        
        date_range_from   = kwrgs.get('date_range_from')
        date_range_to     = kwrgs.get('date_range_to')
        
        logger.debug('QueryAllCustomerGrowthByYearMonth debug: date_range_from=%s',  date_range_from)
        logger.debug('QueryAllCustomerGrowthByYearMonth debug: date_range_to=%s',  date_range_to)
        
        where_condition  = ''
        
        if date_range_from and date_range_to:
            
            date_range_from    = date_str_to_bigquery_qualified_datetime_str(date_range_from)
            date_range_to      = date_str_to_bigquery_qualified_datetime_str(date_range_to)
            
            where_condition = "WHERE PartitionDateTime BETWEEN DATETIME('{date_range_from}') and DATETIME('{date_range_to}') ".format(date_range_from=date_range_from,date_range_to=date_range_to, )
            
        query = '''
            SELECT FORMAT_DATETIME('%Y-%m', RegisteredDateTime) as year_month, sum(count_by_date) as count
            FROM (
            SELECT RegisteredDateTime, count(*) as count_by_date FROM
                (
                        SELECT CustomerKey, RegisteredDateTime
                        FROM `{project_id}.{dataset_name}.registered_customer_*`
                        {where_condition}
                        GROUP BY CustomerKey, RegisteredDateTime
                ) GROUP BY RegisteredDateTime       
            ) GROUP BY year_month            
            '''.format(project_id=BIGQUERY_GCLOUD_PROJECT_ID, dataset_name=SYSTEM_DATASET, where_condition=where_condition)    
            
        logger.debug('execute_all_registered_customer_by_year_month: query=%s', query)
    
        return query 

class QueryMerchantCategoryDataByDateRangeBaseResource(CategoryAndCountQueryBaseResource):
    
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
            date_range_from    = date_str_to_bigquery_qualified_datetime_str(date_range_from)
            date_range_to      = date_str_to_bigquery_qualified_datetime_str(date_range_to)
            
            condition = "WHERE PartitionDateTime BETWEEN DATETIME('{date_range_from}') and DATETIME('{date_range_to}') ".format(date_range_from=date_range_from,date_range_to=date_range_to, )
            
        return self.prepare_query_with_condition(account_code, condition)
    
    def prepare_query_with_condition(self, account_code, condition):
        pass
    
class QueryMerchantCustomDataByDateRangeBaseResource(CachedQueryBaseResource):
    
    def is_cached(self):
        return True
    
    def get_timeout_amount(self):
        return 60
    
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
    
class QueryMerchantCustomerGrowthByYearMonth(QueryMerchantCustomDataByDateRangeBaseResource):
    
    def prepare_query_with_condition(self, account_code, condition):
        dataset = '%s_%s' % (MERCHANT_DATASET,account_code)
        query = '''
            SELECT FORMAT_DATETIME('%Y-%m', RegisteredDateTime) as year_month, sum(count_by_date) as count
            FROM (
            SELECT RegisteredDateTime, count(*) as count_by_date FROM
                (
                        SELECT CustomerKey, RegisteredDateTime
                        FROM `{project_id}.{dataset_name}.merchant_registered_customer`
                        {where_condition}
                        GROUP BY CustomerKey, RegisteredDateTime
                ) GROUP BY RegisteredDateTime       
            ) GROUP BY year_month            
            '''.format(project_id=BIGQUERY_GCLOUD_PROJECT_ID, dataset_name=dataset, where_condition=condition, account_code=account_code)    
            
        return query 
    
    
    def process_query_result(self, job_result_rows):
        row_list = []
        for row in job_result_rows:
            #logger.debug(row)
            column_dict = {}
            
            column_dict['category']  = row.get('year_month')
            column_dict['count']     = row.get('count')
            
            row_list.append(column_dict)
        
        return row_list 
    
class QueryMerchantCustomerCountByDateRange(QueryMerchantCustomDataByDateRangeBaseResource):
    
    def prepare_query_with_condition(self, account_code, condition):
        dataset = '%s_%s' % (MERCHANT_DATASET,account_code)
        query = '''
            SELECT count(*) as customerCount FROM
                (
                        SELECT CustomerKey, RegisteredDateTime
                        FROM `{project_id}.{dataset_name}.merchant_registered_customer`
                        {where_condition}
                        GROUP BY CustomerKey, RegisteredDateTime
                )       
                        
            '''.format(project_id=BIGQUERY_GCLOUD_PROJECT_ID, dataset_name=dataset, where_condition=condition, account_code=account_code)    
            
        return query 
    
    def process_query_result(self, job_result_rows):
        row_list = []
        for row in job_result_rows:
            #logger.debug(row)
            column_dict = {}
            column_dict['amount']        = row.get('customerCount')
            
            row_list.append(column_dict)
        
        return row_list 
    
class QueryMerchantCustomerDateAndCountByDateRange(QueryMerchantCustomDataByDateRangeBaseResource):
    
    def prepare_query_with_condition(self, account_code, condition):
        dataset = '%s_%s' % (MERCHANT_DATASET,account_code)
        query = '''
            SELECT FORMAT_DATETIME('%d/%m/%Y', RegisteredDateTime) AS RegisteredDate, count(*) as customerCount FROM
                (
                        SELECT CustomerKey, RegisteredDateTime
                        FROM `{project_id}.{dataset_name}.merchant_registered_customer`
                        {where_condition}
                        GROUP BY CustomerKey, RegisteredDateTime
                )
            group by RegisteredDate
                        
            '''.format(project_id=BIGQUERY_GCLOUD_PROJECT_ID, dataset_name=dataset, where_condition=condition, account_code=account_code)    
            
        return query 
    
    def process_query_result(self, job_result_rows):
        row_list = []
        for row in job_result_rows:
            #logger.debug(row)
            column_dict = {}
            #column_dict['registeredDate']        = row.get('RegisteredDate')
            #column_dict['customerCount']        = row.get('customerCount')
            column_dict['amount']               = row.get('customerCount')
            
            row_list.append(column_dict)
        
        return row_list     
    
class QueryMerchantCustomerGenderByDateRange(QueryMerchantCustomDataByDateRangeBaseResource):
    def prepare_query_with_condition(self, account_code, condition):
        dataset = '%s_%s' % (MERCHANT_DATASET,account_code)
        query = '''
            SELECT coalesce(Gender,'u') as gender, count(*) as genderCount FROM
                (
                
                SELECT
                  DISTINCT checking.Key, checking.CustomerKey, checking.UpdatedDateTime, checking.Gender as gender
                FROM
                  (
                  SELECT
                     CustomerKey, MAX(UpdatedDateTime) AS latestUpdatedDateTime
                   FROM
                    `{project_id}.{dataset_name}.merchant_registered_customer`
                    {where_condition}
                    
                  GROUP BY
                 CustomerKey
                 ) 
                 AS latest_customers
            INNER JOIN 
            (
              SELECT 
              Key, CustomerKey, UpdatedDateTime, Gender
              FROM
              `{project_id}.{dataset_name}.merchant_registered_customer`
              {where_condition} 
                 
            ) as checking
            ON
              checking.CustomerKey = latest_customers.CustomerKey
              AND
              checking.UpdatedDateTime=latest_customers.latestUpdatedDateTime
            ) group by gender      
                        
            '''.format(project_id=BIGQUERY_GCLOUD_PROJECT_ID, dataset_name=dataset, where_condition=condition, account_code=account_code)    
            
        return query 
    
    def process_query_result(self, job_result_rows):
        row_list = []
        for row in job_result_rows:
            #logger.debug(row)
            column_dict = {}
            column_dict['gender']           = row.get('gender')
            column_dict['count']            = row.get('genderCount')
            
            row_list.append(column_dict)
        
        return row_list 
    
class QueryMerchantCustomerAgeGroupByDateRange(QueryMerchantCustomDataByDateRangeBaseResource):
    def prepare_query_with_condition(self, account_code, condition):
        dataset = '%s_%s' % (MERCHANT_DATASET,account_code)
        
        query = '''
            SELECT age_group, sum(group_count) as count  FROM (

                SELECT age_group, count(*) as group_count FROM (
                    SELECT CASE 
                       WHEN age >=  0 AND age < 20 THEN '0-19'
                       WHEN age >= 20 AND age < 30 THEN '20-29'
                       WHEN age >= 30 AND age < 40 THEN '30-39'
                       WHEN age >= 40 AND age < 50 THEN '40-49'
                       WHEN age >= 50 AND age < 60 THEN '50-59'
                       WHEN age >= 60 AND age < 70 THEN '60-69'
                       WHEN age >= 70 AND age < 80 THEN '70-79'
                       WHEN age >= 80              THEN '>=80'
                       ELSE 'unknown' END as age_group
            
                        FROM(
            
                            SELECT IFNULL(DATE_DIFF(CURRENT_DATE(),DOB, YEAR), -1) as age
                                FROM(
            
                                SELECT
                                  DISTINCT checking.Key, checking.CustomerKey, checking.UpdatedDateTime, checking.DOB as DOB
                                FROM
                                  (
                                  SELECT
                                     CustomerKey, MAX(UpdatedDateTime) AS latestUpdatedDateTime
                                   FROM
                                     `{project_id}.{dataset_name}.merchant_registered_customer`
                                     {where_condition} 
            
                                   GROUP BY
                                     CustomerKey
                                     ) 
                                     AS latest_customers
                                INNER JOIN
                                (
                                  SELECT 
                                  Key, CustomerKey, UpdatedDateTime, DOB
                                  FROM
                                  `{project_id}.{dataset_name}.merchant_registered_customer`
                                  {where_condition} 
            
                                ) as checking
                                
                                ON
                                    
                                checking.CustomerKey = latest_customers.CustomerKey
                                AND
                                checking.UpdatedDateTime=latest_customers.latestUpdatedDateTime
                            ) 
                        )                 
                ) group by age_group
            ) group by age_group
                        
            '''.format(project_id=BIGQUERY_GCLOUD_PROJECT_ID, dataset_name=dataset, where_condition=condition, account_code=account_code)    
            
        logger.debug('QueryMerchantCustomerCountByDateRange: query=%s', query)
    
        return query 
    
    def process_query_result(self, job_result_rows):
        row_list = []
        for row in job_result_rows:
            #logger.debug(row)
            column_dict = {}
            column_dict['age_group']    = row.get('age_group')
            column_dict['count']        = row.get('count')
            
            row_list.append(column_dict)
        
        return row_list                   
    

def execute_all_registered_customer_by_year_month(bg_client, project_id, dataset_name):
    
    query = '''
            SELECT FORMAT_DATETIME('%Y-%m-%d', RegisteredDateTime) as year_month, sum(count_by_date) as count
            FROM (
            SELECT RegisteredDateTime, count(*) as count_by_date
                        FROM `{project_id}.{dataset_name}.registered_customer`
                        GROUP BY RegisteredDateTime
            ) GROUP BY year_month            
            '''.format(project_id=project_id, dataset_name=dataset_name)
    
    logger.debug('execute_all_registered_customer_by_year_month: query=%s', query)
    
    return execute_query(bg_client, query)


def process_all_registered_customer_by_year_month(job_result_rows):
    return process_job_result_into_category_and_count(job_result_rows)


@customer_analytics_data_bp.route('/')
def customer_data_analytics():
    logger.debug('This is default path for this blueprint')
    return 'Customer Data Analytics', 200

query_customer_data_api.add_resource(QueryAllCustomerGrowthByYearMonth,             '/all-cust-growth-by-year-month')
query_customer_data_api.add_resource(QueryMerchantCustomerGrowthByYearMonth,        '/merchant-cust-growth-by-year-month')
query_customer_data_api.add_resource(QueryMerchantCustomerCountByDateRange,         '/merchant-cust-count-by-date-range')
query_customer_data_api.add_resource(QueryMerchantCustomerDateAndCountByDateRange,  '/merchant-cust-date-and-count-by-date-range')
query_customer_data_api.add_resource(QueryMerchantCustomerGenderByDateRange,        '/merchant-cust-gender-by-date-range')
query_customer_data_api.add_resource(QueryMerchantCustomerAgeGroupByDateRange,      '/merchant-cust-age-group-by-date-range')
query_customer_data_api.add_resource(BaseResource,  '/base')
