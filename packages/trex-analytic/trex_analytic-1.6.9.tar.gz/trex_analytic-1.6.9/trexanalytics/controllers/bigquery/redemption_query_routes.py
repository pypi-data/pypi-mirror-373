'''
Created on 29 Jun 2021

@author: jacklok
'''

from flask import Blueprint
import logging
from trexanalytics.controllers.bigquery.query_base_routes import QueryBaseResource
from flask_restful import Api
from trexconf.conf import BIGQUERY_GCLOUD_PROJECT_ID, MERCHANT_DATASET
from trexlib.utils.common.date_util import date_str_to_bigquery_qualified_datetime_str


redemption_analytics_data_bp = Blueprint('redemption_analytics_data_bp', __name__,
                                 template_folder='templates',
                                 static_folder='static',
                                 url_prefix='/analytics/redemption')

logger = logging.getLogger('analytics')

query_redemption_data_api = Api(redemption_analytics_data_bp)

@redemption_analytics_data_bp.route('/index')
def query_redemption_index(): 
    return 'ping', 200


def process_redemption_result_into_fieldname_and_value(job_result_rows):
    row_list = []
    for row in job_result_rows:
        #logger.debug(row)
        column_dict = {}
        column_dict['date_range']           = row.get('date_range')
        column_dict['RewardFormat']         = row.get('RewardFormat')
        column_dict['sumRedeemedAmount']    = row.get('sumRewardAmount')
        column_dict['transactionCount']     = row.get('transactionCount')
        
        row_list.append(column_dict)
    
    return row_list

class OutletRedemptionQueryBase(QueryBaseResource):
    def process_query_result(self, job_result_rows):
        return process_redemption_result_into_fieldname_and_value(job_result_rows)




class QueryMerchantRedemptionByDateRange(OutletRedemptionQueryBase):
    def prepare_query(self, **kwrgs):
        account_code      = kwrgs.get('account_code')
        date_range_from   = kwrgs.get('date_range_from')
        date_range_to     = kwrgs.get('date_range_to')
        
        account_code = account_code.replace('-','')
        
        where_condition  = ''
        
        if date_range_from and date_range_to:
            date_range_from    = date_str_to_bigquery_qualified_datetime_str(date_range_from)
            date_range_to      = date_str_to_bigquery_qualified_datetime_str(date_range_to)
            
            where_condition = "WHERE PartitionDateTime BETWEEN DATETIME('{date_range_from}') and DATETIME('{date_range_to}') ".format(date_range_from=date_range_from,date_range_to=date_range_to, )
        
        query = '''
            SELECT FORMAT_DATETIME('%Y-%m-%d', RedeemedDateTime) as date_range, RewardFormat, sum(TotalRedeemedAmount) as sumRedeemedAmount, count(transactionId) as transactionCount
            FROM (
            
                SELECT transactionId, RedeemedDateTime, RewardFormat, RewardFormatKey, SUM(RedeemedAmount) as TotalRedeemedAmount
                        FROM (
                            
                            SELECT
                                checking_transaction.RedeemedDateTime as RedeemedDateTime, 
                                checking_transaction.TransactionId as TransactionId, 
                                checking_transaction.UpdatedDateTime, 
                                checking_transaction.RewardFormat as RewardFormat,
                                checking_transaction.RedeemedAmount as RedeemedAmount,
                                checking_transaction.Reverted as Reverted
                                
                              FROM
                                (
                                SELECT
                                   TransactionId, MAX(UpdatedDateTime) AS latestUpdatedDateTime
                                 FROM
                                   `{project_id}.{dataset_name}.customer_redemption_{account_code}_*`
                                    
                                    {where_condition}
                            
                                 GROUP BY
                                   TransactionId
                                   ) 
                                   AS latest_transaction
                              INNER JOIN
                              (
                                SELECT 
                                RedeemedDateTime, TransactionId, UpdatedDateTime, RewardFormat, RedeemedAmount, Reverted
                                FROM
                                `{project_id}.{dataset_name}.customer_redemption_{account_code}_*`
                                  
                                  {where_condition}
                            
                              ) as checking_transaction
                            
                            ON
                            
                            checking_transaction.TransactionId = latest_transaction.TransactionId
                            AND
                            checking_transaction.UpdatedDateTime=latest_transaction.latestUpdatedDateTime
                            
                    )
                    WHERE Reverted=False
                    GROUP BY transactionId, RewardedDateTime, RewardFormat
            )
            GROUP BY date_range, RewardFormat    
            order by date_range        
            '''.format(project_id=BIGQUERY_GCLOUD_PROJECT_ID, dataset_name=MERCHANT_DATASET, where_condition=where_condition, account_code=account_code)    
            
        logger.debug('QueryMerchantRedemptionByDateRange: query=%s', query)
    
        return query
    
    
query_redemption_data_api.add_resource(QueryMerchantRedemptionByDateRange,   '/merchant-redemption-by-date-range')