'''
Created on 25 Nov 2024

@author: jacklok
'''

from flask import Blueprint
import logging
from trexanalytics.controllers.bigquery.query_base_routes import QueryBaseResource
from flask_restful import Api
from trexconf.conf import MERCHANT_DATASET
from trexconf import conf
from trexanalytics.bigquery_table_template_config import USER_VOUCHER_ENTITLED_TEMPLATE,\
    USER_VOUCHER_ENTITLED_REVERTED_TEMPLATE, USER_VOUCHER_REMOVED_TEMPLATE,\
    USER_VOUCHER_REDEEMED_TEMPLATE
from datetime import datetime
from trexlib.utils.common.date_util import date_str_to_bigquery_qualified_datetime_str



voucher_analytics_data_bp = Blueprint('voucher_analytics_data_bp', __name__,
                                 template_folder='templates',
                                 static_folder='static',
                                 url_prefix='/analytics/voucher')

logger = logging.getLogger('analytics')

voucher_analytics_data_api = Api(voucher_analytics_data_bp)

@voucher_analytics_data_bp.route('/index')
def query_voucher_index(): 
    return 'ping', 200


def process_reward_result_into_fieldname_and_value(job_result_rows):
    row_list = []
    for row in job_result_rows:
        #logger.debug(row)
        column_dict = {}
        column_dict['voucher_key']          = row.get('voucher_key')
        column_dict['date']                 = row.get('date')
        column_dict['entitled_total']       = row.get('entitled_total')
        column_dict['removed_total']        = row.get('removed_total')
        column_dict['redeemed_total']       = row.get('redeemed_total')
        
        row_list.append(column_dict)
    
    return row_list

class QueryMerchantVoucherDataByDateRangeBaseResource(QueryBaseResource):
    
    def prepare_query(self, **kwrgs):
        account_code            = kwrgs.get('account_code')
        date_range_from_str     = kwrgs.get('date_range_from')#yyyymmdd
        date_range_to_str       = kwrgs.get('date_range_to')#yyyymmdd
        
        account_code = account_code.replace('-','')
        
        logger.info('account_code=%s', account_code)
        logger.info('date_range_from_str=%s', date_range_from_str)
        logger.info('date_range_to_str=%s', date_range_to_str)
        
        #date_range_from = datetime.strptime(date_range_from_str, '%Y%m%d')
        #date_range_to   = datetime.strptime(date_range_to_str, '%Y%m%d')
        
        #year_month_date_from         = date_range_from.strftime('%Y%m%d')
        #year_month_date_to           = date_range_from.strftime('%Y%m%d')
        
        condition = ''
        
        if date_range_from_str and date_range_to_str:
            date_range_from    = date_str_to_bigquery_qualified_datetime_str(date_range_from_str)
            date_range_to      = date_str_to_bigquery_qualified_datetime_str(date_range_to_str)
            
            condition = "WHERE PartitionDateTime BETWEEN DATETIME('{date_range_from}') and DATETIME('{date_range_to}') ".format(date_range_from=date_range_from,date_range_to=date_range_to, )
        
        return self.prepare_query_with_condition(account_code, condition, date_range_from=date_range_from, date_range_to=date_range_to)
    
    def prepare_query_with_condition(self, account_code, condition):
        pass   
    
class QueryMerchantVoucherPerformanceByDateRange(QueryMerchantVoucherDataByDateRangeBaseResource):
    def prepare_query_with_condition(self, account_code, condition, date_range_from=None, date_range_to=None):
        
        dataset_name = MERCHANT_DATASET
        
        user_entitled_voucher_table_name            = '`{0}.{1}.{2}_{3}_*`'.format(conf.BIGQUERY_GCLOUD_PROJECT_ID, dataset_name, USER_VOUCHER_ENTITLED_TEMPLATE, account_code)
        user_entitled_voucher_reverted_table_name   = '`{0}.{1}.{2}_{3}_*`'.format(conf.BIGQUERY_GCLOUD_PROJECT_ID, dataset_name, USER_VOUCHER_ENTITLED_REVERTED_TEMPLATE, account_code)

        user_removed_voucher_table_name             = '`{0}.{1}.{2}_{3}_*`'.format(conf.BIGQUERY_GCLOUD_PROJECT_ID, dataset_name, USER_VOUCHER_REMOVED_TEMPLATE, account_code)
        user_redeemed_voucher_table_name            = '`{0}.{1}.{2}_{3}_*`'.format(conf.BIGQUERY_GCLOUD_PROJECT_ID, dataset_name, USER_VOUCHER_REDEEMED_TEMPLATE, account_code)
        
        
        
        query_params = {
            'user_entitled_voucher_table_name'              : user_entitled_voucher_table_name,
            'user_entitled_voucher_reverted_table_name'     : user_entitled_voucher_reverted_table_name,
            'user_removed_voucher_table_name'               : user_removed_voucher_table_name,
            'user_redeemed_voucher_table_name'              : user_redeemed_voucher_table_name,
            'voucher_datetime_format'                       : '%d-%m-%Y',
            'filter_by_voucher_condition'                   : condition,
        }
        
        query_params['date_range_from']    = date_range_from.strftime('%Y,%m,%d,0,0,0')
        query_params['date_range_to']      = date_range_to.strftime('%Y,%m,%d,23,59,59')
        
        
        query = '''
            SELECT 
                    COALESCE(entitled_list.VoucherKey, removed_list.VoucherKey, redeemed_list.VoucherKey) AS voucher_key,
                    COALESCE(entitled_list.entitled_date, removed_list.removed_date, redeemed_list.redeemed_date) AS date,
                    
                    entitled_total,
                    removed_total,
                    redeemed_total

                    FROM
                    (

                        SELECT entitled_date, VoucherKey, count(*) as entitled_total FROM (

                            SELECT entitled_date, VoucherKey, VoucherCode FROM (

                                SELECT FORMAT_DATETIME('{voucher_datetime_format}',EntitledDatetime) as entitled_date, VoucherKey, VoucherCode
                                FROM
                                  {user_entitled_voucher_table_name}

                                  where EntitledDatetime >= datetime({date_range_from})
                                  and EntitledDatetime <= datetime({date_range_to})
                                  and {filter_by_voucher_condition}

                            )
                            group by entitled_date, VoucherKey, VoucherCode

                        )
                        group by entitled_date, VoucherKey

                        UNION ALL

                        SELECT entitled_date, VoucherKey, -1*(count(*)) as entitled_total FROM (

                           SELECT entitled_date, VoucherKey, VoucherCode FROM (

                                SELECT FORMAT_DATETIME('{voucher_datetime_format}',RevertedDatetime) as entitled_date, VoucherKey, VoucherCode
                                FROM
                                  {user_entitled_voucher_reverted_table_name}

                                  where EntitledDatetime >= datetime({date_range_from})
                                  and EntitledDatetime <= datetime({date_range_to})
                                  and {filter_by_voucher_condition}
                           )
                           group by entitled_date, VoucherKey, VoucherCode

                        )
                        group by entitled_date, VoucherKey
                    ) as entitled_list

                    full join

                    (

                        SELECT removed_date, VoucherKey, count(*) as removed_total FROM (
                            SELECT removed_date, VoucherKey, VoucherCode FROM (

                                SELECT FORMAT_DATETIME('{voucher_datetime_format}',RemovedDatetime) as removed_date, VoucherKey, VoucherCode
                                FROM
                                  {user_removed_voucher_table_name}

                                  where
                                  VoucherCode NOT IN (SELECT VoucherCode FROM {user_redeemed_voucher_table_name}) and
                                  RemovedDatetime >= datetime({date_range_from})
                                  and RemovedDatetime <= datetime({date_range_to})
                                  and {filter_by_voucher_condition}

                            )
                            group by removed_date, VoucherKey, VoucherCode

                       )
                       group by removed_date, VoucherKey

                    ) as removed_list

                  on entitled_list.entitled_date = removed_list.removed_date and entitled_list.VoucherKey=removed_list.VoucherKey

                  full join

                    (
                        SELECT redeemed_date, VoucherKey, count(*) as redeemed_total FROM (
                            SELECT redeemed_date, VoucherKey, VoucherCode FROM (

                                SELECT FORMAT_DATETIME('{voucher_datetime_format}',RedeemedDatetime) as redeemed_date, VoucherKey, VoucherCode
                                FROM
                                  {user_redeemed_voucher_table_name}

                                  where RedeemedDatetime >= datetime({date_range_from})
                                  and RedeemedDatetime <= datetime({date_range_to})
                                  and {filter_by_voucher_condition}

                            )
                            group by redeemed_date, VoucherKey, VoucherCode
                        )
                        group by redeemed_date, VoucherKey
                    ) as redeemed_list

                  on 
                  COALESCE(entitled_list.entitled_date, removed_list.removed_date) = redeemed_list.redeemed_date and
                  COALESCE(entitled_list.VoucherKey, removed_list.VoucherKey) = redeemed_list.VoucherKey
                        
            '''.format(**query_params)    
            
        logger.debug('QueryMerchantCustomerCountByDateRange: query=%s', query)
    
        return query 
    
    def process_query_result(self, job_result_rows):
        return process_reward_result_into_fieldname_and_value(job_result_rows)    
    
voucher_analytics_data_api.add_resource(QueryMerchantVoucherPerformanceByDateRange,   '/performance-by-date-range')

       