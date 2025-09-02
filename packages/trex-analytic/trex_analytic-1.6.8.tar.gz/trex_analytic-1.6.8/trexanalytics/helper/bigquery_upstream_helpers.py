from trexmodel.models.datastore.transaction_models import CustomerTransaction
from trexmodel.models.datastore.reward_models import CustomerPointReward,\
    CustomerStampReward, CustomerEntitledVoucher
from trexmodel.models.datastore.prepaid_models import CustomerPrepaidReward
from trexanalytics.bigquery_upstream_data_config import create_merchant_customer_reward_upstream_for_merchant,\
    create_merchant_customer_redemption_upstream_for_merchant,\
    create_merchant_customer_redemption_reverted_upstream_for_merchant,\
    create_entitled_customer_voucher_upstream_for_merchant,\
    create_merchant_customer_prepaid_upstream_for_merchant,\
    create_revert_entitled_customer_voucher_upstream_for_merchant,\
    create_removed_customer_voucher_to_upstream_for_merchant,\
    create_redeemed_customer_voucher_to_upstream_for_merchant
from trexlib.utils.string_util import is_not_empty
import logging    
    
    
logger = logging.getLogger('debug')
    
def create_transction_reward_upstream(transaction_details):        
    
    rewards_list = list_transction_reward(transaction_details)
    
    if rewards_list and is_not_empty(rewards_list):
        for r in rewards_list:
            if isinstance(r, CustomerEntitledVoucher):
                is_redeemed = r.is_redeemed
                is_removed  = r.is_removed
                is_reverted = r.is_reverted
                
                
                if is_reverted:
                    create_revert_entitled_customer_voucher_upstream_for_merchant(r)
                    logger.debug('going to create upstream for reverted voucher')    
                elif is_removed:
                    create_removed_customer_voucher_to_upstream_for_merchant(r)
                    logger.debug('going to create upstream for removed voucher')
                    
                elif is_redeemed:
                    create_redeemed_customer_voucher_to_upstream_for_merchant(r)
                    logger.debug('going to create upstream for redeemed voucher')
                
                create_entitled_customer_voucher_upstream_for_merchant(r)
                logger.debug('going to create upstream for entitled voucher')
                
              
            elif isinstance(r, CustomerPrepaidReward):
                
                create_merchant_customer_prepaid_upstream_for_merchant(transaction_details, r)
                if transaction_details.is_revert:
                    create_merchant_customer_prepaid_upstream_for_merchant(transaction_details, r, transaction_details.reverted_datetime, Reverted=True)
                
            else:
                create_merchant_customer_reward_upstream_for_merchant(transaction_details, r)
            
                if transaction_details.is_revert:
                    create_merchant_customer_reward_upstream_for_merchant(transaction_details, r, Reverted=True)
            
def list_transction_reward(transaction_details):
    all_rewards_list = []
            
    if isinstance(transaction_details, CustomerTransaction):
        transaction_id = transaction_details.transaction_id
        
        logger.debug('transaction_id=%s', transaction_id)
        
        if transaction_details.is_point_reward_entitled:
            logger.debug('it is point reward')
            rewards_list = CustomerPointReward.list_by_transaction_id(transaction_id)
            
            logger.debug('rewards_list=%s', rewards_list)
            
            if rewards_list and is_not_empty(rewards_list):
                all_rewards_list.extend(rewards_list)
        
        if transaction_details.is_stamp_reward_entitled:
            logger.debug('it is stamp reward')
            rewards_list = CustomerStampReward.list_by_transaction_id(transaction_id)
            
            logger.debug('rewards_list=%s', rewards_list)
            
            if rewards_list and is_not_empty(rewards_list):
                all_rewards_list.extend(rewards_list)
        
        if transaction_details.is_voucher_reward_entitled:
            logger.debug('it is voucher reward')
            rewards_list = CustomerEntitledVoucher.list_by_transaction_id(transaction_id)
            
            logger.debug('rewards_list=%s', rewards_list)
            
            if rewards_list and is_not_empty(rewards_list):
                all_rewards_list.extend(rewards_list)
        
        if transaction_details.is_prepaid_reward_entitled:
            logger.debug('it is prepaid reward')
            rewards_list = CustomerPrepaidReward.list_by_transaction_id(transaction_id)
            
            logger.debug('rewards_list=%s', rewards_list)
            
            if rewards_list and is_not_empty(rewards_list):
                all_rewards_list.extend(rewards_list) 
                
    return all_rewards_list                  
        
def create_redemption_upstream(redemption_details):        
    
    create_merchant_customer_redemption_upstream_for_merchant(redemption_details)
            
    if redemption_details.is_revert:
        create_merchant_customer_redemption_reverted_upstream_for_merchant(redemption_details)
                
