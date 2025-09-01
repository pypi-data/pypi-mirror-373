'''
Created on 23 Jun 2025

@author: jacklok
'''
import logging
from datetime import datetime
from trexanalytics.bigquery_upstream_data_config import create_merchant_sales_transaction_upstream_for_merchant

#logger = logging.getLogger('helper')
logger = logging.getLogger('target_debug')

def revert_sales_transaction(transaction_details, reverted_by, reverted_datetime=None):
    
    if transaction_details.is_revert==False and transaction_details.allow_to_revert and transaction_details.used==False:
        logger.info('going to check for sales transaction revert')
        
        if reverted_datetime is None:
            reverted_datetime = datetime.utcnow()
        
        if reverted_by:
            transaction_details.reverted_by                = reverted_by.create_ndb_key()
            transaction_details.reverted_by_username       = reverted_by.username
        
        transaction_details.reverted_datetime   = reverted_datetime
        transaction_details.is_revert = True
        transaction_details.put()
        
        create_merchant_sales_transaction_upstream_for_merchant(transaction_details, Reverted=True)
        
    else:
        logger.error('Sales transaction is either reverted or not allow to revert or it has been claimed by customer')
        raise Exception('Sales transaction is either reverted or not allow to revert or it has been claimed by customer')
