'''
Created on 18 Oct 2024

@author: jacklok
'''
from trexconf.conf import BIGQUERY_GCLOUD_PROJECT_ID, MERCHANT_DATASET,\
    BIGQUERY_SERVICE_CREDENTIAL_PATH
import logging
from trexlib.utils.google.bigquery_util import create_bigquery_client,\
    execute_query
from trexlib.utils.log_util import get_tracelog
from datetime import datetime
from dateutil.relativedelta import relativedelta
from trexconf import conf
from trexanalytics.bigquery_table_template_config import USER_VOUCHER_ENTITLED_TEMPLATE,\
    USER_VOUCHER_ENTITLED_REVERTED_TEMPLATE, USER_VOUCHER_REMOVED_TEMPLATE,\
    USER_VOUCHER_REDEEMED_TEMPLATE
from trexlib.utils.string_util import is_not_empty
from trexlib.utils.common.date_util import date_to_bigquery_qualified_datetime_str,\
    date_str_to_bigquery_qualified_datetime_str

#logger = logging.getLogger('analytics')
logger = logging.getLogger('target_debug')


def fetch_top_spender_data(date_range_from, date_range_to, limit=10, account_code=None, outlet_key=None,
                           min_total_spending_amount=.0, 
                           min_total_visit_amount = 0,
                           ):
    query = __prepare_top_spender_query(
                date_range_from, 
                date_range_to,
                limit                       = limit,
                account_code                = account_code,
                outlet_key                  = outlet_key,
                min_total_spending_amount   = min_total_spending_amount,
                min_total_visit_amount      = min_total_visit_amount,
                )
    bg_client       = create_bigquery_client(credential_filepath=BIGQUERY_SERVICE_CREDENTIAL_PATH)
    
    if bg_client is not None:
            logger.info('BigQuery Client is not none, thus going to execute query')
        
    try:
        job_result_rows = execute_query(bg_client, query)
        
        bg_client.close()
    except:
        job_result_rows = []
        logger.error('Failed to execute query due to %s', get_tracelog())
    
    row_list = []
    if job_result_rows:
        
        for row in job_result_rows:
            #logger.debug(row)
            column_dict = {}
            column_dict['customerKey']              = row.CustomerKey
            column_dict['totalTransactAmount']      = row.totalTransactAmount
            column_dict['transactionCount']         = row.transactionCount
            
            row_list.append(column_dict)
    
    return row_list

def fetch_merchant_voucher_performance_data(
                            start_date, end_date, account_code=None, 
                            voucher_key=None,
                           ):
    query = __prepare_merchant_voucher_performance_query(
                start_date, 
                end_date,
                account_code                = account_code,
                voucher_key                 = voucher_key,
                )
    logger.debug('query=%s', query)
    bg_client       = create_bigquery_client(credential_filepath=BIGQUERY_SERVICE_CREDENTIAL_PATH)
    
    if bg_client is not None:
            logger.info('BigQuery Client is not none, thus going to execute query')
        
    try:
        job_result_rows = execute_query(bg_client, query)
        
        bg_client.close()
    except:
        job_result_rows = []
        logger.error('Failed to execute query due to %s', get_tracelog())
    
    row_list = []
    for row in job_result_rows:
        #logger.debug(row)
        column_dict = {}
        column_dict['voucher_key']          = row.voucher_key
        column_dict['date']                 = row.date
        column_dict['entitled_total']       = row.entitled_total
        column_dict['removed_total']        = row.removed_total
        column_dict['redeemed_total']       = row.redeemed_total
        
        row_list.append(column_dict)
    
    return row_list
    

def __prepare_top_spender_query(date_range_from, date_range_to, 
                             limit=10, account_code=None, outlet_key=None,
                             min_total_spending_amount=.0, 
                             min_total_visit_amount = 0,
                             ):
    
        
    account_code = account_code.replace('-','')
    
    where_condition  = ''
    
    where_final_condition  = 'WHERE'
    
    if date_range_from and date_range_to:
        date_range_from    = date_str_to_bigquery_qualified_datetime_str(date_range_from)
        date_range_to      = date_str_to_bigquery_qualified_datetime_str(date_range_to)
        
        if outlet_key:
            where_condition = "WHERE PartitionDateTime BETWEEN DATETIME('{date_range_from}') and DATETIME('{date_range_to}')and TransactOutlet='{outlet_key}' and  ".format(date_range_from=date_range_from,date_range_to=date_range_to, outlet_key=outlet_key)
        else:
            where_condition = "WHERE PartitionDateTime BETWEEN DATETIME('{date_range_from}') and DATETIME('{date_range_to}')and  ".format(date_range_from=date_range_from,date_range_to=date_range_to, )
    else:
        if outlet_key:
            where_condition = "WHERE TransactOutlet='{outlet_key}' and ".format(outlet_key=outlet_key)
        else:
            where_condition = "WHERE "
    
    if min_total_spending_amount>0:
        where_final_condition  = '%s totalTransactAmount>=%s' % (where_final_condition, min_total_spending_amount)
        
        if min_total_visit_amount>0:
            where_final_condition  = '%s and transactionCount>=%s' % (where_final_condition, min_total_visit_amount)
    else:
        if min_total_visit_amount>0:
            where_final_condition  = '%s transactionCount>=%s' % (where_final_condition, min_total_visit_amount)
        else:
            where_final_condition = ''
    
    dataset = '%s_%s' % (MERCHANT_DATASET,account_code)
            
    query = '''
            SELECT CustomerKey, totalTransactAmount, transactionCount
                FROM (
                    SELECT CustomerKey, SUM(TransactAmount) as totalTransactAmount, count(*) as transactionCount
                    FROM (
                        
                        SELECT
                            CustomerKey,
                            TransactAmount, 
                            Reverted
                            
                          FROM
                               `{project_id}.{dataset_name}.customer_transaction`
                                
                                {where_condition}
                                IsSalesTransaction=true
                    )
                    WHERE Reverted=False
                    GROUP BY CustomerKey
                )
                {where_final_condition}       
                    order by totalTransactAmount desc
                    LIMIT {limit}
                    
                 
               
        '''.format(project_id=BIGQUERY_GCLOUD_PROJECT_ID, dataset_name=dataset, 
                   where_condition=where_condition,
                   where_final_condition=where_final_condition,
                   limit=limit,
                   account_code=account_code)    
        
    logger.debug('QueryMerchantOutletCustomerTopSpendingAmountByDateRange: query=%s', query)

    return query  

def __prepare_merchant_voucher_performance_query(
                                start_date, 
                                end_date, 
                                account_code    = None,
                                voucher_key     = None,
                             ):
    account_code = account_code.replace('-','')
    
    logger.info('account_code=%s', account_code)
    logger.info('start_date=%s', start_date)
    logger.info('end_date=%s', end_date)
    
    #date_range_from = datetime.strftime(start_date, '%Y%m%d')
    #date_range_to   = datetime.strftime(end_date, '%Y%m%d')
    
    date_range_from    = date_to_bigquery_qualified_datetime_str(start_date)
    date_range_to      = date_to_bigquery_qualified_datetime_str(end_date)
    
    condition = "PartitionDateTime BETWEEN DATETIME('{date_range_from}') and DATETIME('{date_range_to}') ".format(date_range_from=date_range_from,date_range_to=date_range_to, )
    
    if is_not_empty(voucher_key):
        condition += " and VoucherKey='%s'" % voucher_key
    
    dataset_name = '%s_%s' % (MERCHANT_DATASET,account_code)
        
    user_entitled_voucher_table_name            = '`{0}.{1}.{2}`'.format(conf.BIGQUERY_GCLOUD_PROJECT_ID, dataset_name, USER_VOUCHER_ENTITLED_TEMPLATE,)
    user_entitled_voucher_reverted_table_name   = '`{0}.{1}.{2}`'.format(conf.BIGQUERY_GCLOUD_PROJECT_ID, dataset_name, USER_VOUCHER_ENTITLED_REVERTED_TEMPLATE,)

    user_removed_voucher_table_name             = '`{0}.{1}.{2}`'.format(conf.BIGQUERY_GCLOUD_PROJECT_ID, dataset_name, USER_VOUCHER_REMOVED_TEMPLATE,)
    user_redeemed_voucher_table_name            = '`{0}.{1}.{2}`'.format(conf.BIGQUERY_GCLOUD_PROJECT_ID, dataset_name, USER_VOUCHER_REDEEMED_TEMPLATE,)
    
    
    
    query_params = {
        'user_entitled_voucher_table_name'              : user_entitled_voucher_table_name,
        'user_entitled_voucher_reverted_table_name'     : user_entitled_voucher_reverted_table_name,
        'user_removed_voucher_table_name'               : user_removed_voucher_table_name,
        'user_redeemed_voucher_table_name'              : user_redeemed_voucher_table_name,
        'voucher_datetime_format'                       : '%d-%m-%Y',
        'filter_by_voucher_condition'                   : condition,
    }
    
    query_params['date_range_from']    = start_date.strftime('%Y,%m,%d,0,0,0')
    query_params['date_range_to']      = end_date.strftime('%Y,%m,%d,23,59,59')
    
    query = '''
        SELECT 
                COALESCE(
                    entitled_list.VoucherKey, 
                    removed_list.VoucherKey, 
                    redeemed_list.VoucherKey) AS voucher_key,
                
                COALESCE(
                    entitled_list.entitled_date, 
                    removed_list.removed_date, 
                    redeemed_list.redeemed_date) AS date,
                
                entitled_total,
                removed_total,
                redeemed_total
                
                FROM (
                
                SELECT entitled_date, VoucherKey, SUM(entitled_total) as entitled_total 

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
    
                                SELECT FORMAT_DATETIME('{voucher_datetime_format}',EntitledDatetime) as entitled_date, VoucherKey, VoucherCode
                                FROM
                                  {user_entitled_voucher_reverted_table_name}
    
                                  where EntitledDatetime >= datetime({date_range_from})
                                  and EntitledDatetime <= datetime({date_range_to})
                                  and {filter_by_voucher_condition}
                           )
                           group by entitled_date, VoucherKey, VoucherCode
    
                        ) group by entitled_date, VoucherKey
                    ) group by entitled_date, VoucherKey
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
              
              ORDER BY date
                    
        '''.format(**query_params)    
        
    logger.debug('query=%s', query)
    
    
    
    return query

def __prepare_non_active_customer_query(
                                num_of_months, 
                                limit=10, account_code=None,
                                membership_key=None,
                                tier_membership_key=None,
                             ):
    
        
    account_code = account_code.replace('-','')
    
    where_final_condition  = 'WHERE'
    
    today = datetime.utcnow().date()
    
    from_date = today - relativedelta(months=num_of_months)
    
    date_range_from = datetime.strftime(from_date, '%Y%m%d')
    date_range_to   = datetime.strftime(today, '%Y%m%d')
    
    date_range_from    = date_str_to_bigquery_qualified_datetime_str(date_range_from)
    date_range_to      = date_str_to_bigquery_qualified_datetime_str(date_range_to)
    
    where_condition = "WHERE PartitionDateTime BETWEEN DATETIME('{date_range_from}') and DATETIME('{date_range_to}')".format(date_range_from=date_range_from,date_range_to=date_range_to)
    
    query = '''
            SELECT CustomerKey, TransactDateTime
                FROM (
                    SELECT
                        checking_transaction.TransactDateTime as TransactDateTime, 
                        checking_transaction.UpdatedDateTime, 
                        checking_transaction.Reverted as Reverted
                        
                      FROM
                        (
                        SELECT
                           MAX(TransactDateTime) AS LatestTransactDateTime
                         FROM
                           `{project_id}.{dataset_name}.customer_transaction_{account_code}_*`
                            
                            {where_condition}
                            IsSalesTransaction=true
                    
                         
                      
                )
                {where_final_condition}       
                    
                    
                 
               
        '''.format(project_id=BIGQUERY_GCLOUD_PROJECT_ID, dataset_name=MERCHANT_DATASET, 
                   where_condition=where_condition,
                   where_final_condition=where_final_condition,
                   limit=limit,
                   account_code=account_code)    
        
    logger.debug('QueryMerchantOutletCustomerTopSpendingAmountByDateRange: query=%s', query)

    return query   
    
