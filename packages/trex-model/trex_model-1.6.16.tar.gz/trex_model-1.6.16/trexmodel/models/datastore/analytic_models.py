'''
Created on 25 Jan 2021

@author: jacklok
'''
from trexconf import conf as model_conf
from google.cloud import ndb
from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel
from datetime import timedelta
from trexmodel.models.datastore.merchant_models import MerchantAcct

class UpstreamData(BaseNModel, DictModel):
    merchant_acct           = ndb.KeyProperty(name="merchant_acct", kind=MerchantAcct)
    table_template_name     = ndb.StringProperty(required=True)
    dataset_name            = ndb.StringProperty(required=True)
    table_name              = ndb.StringProperty(required=True)
    stream_content          = ndb.JsonProperty(required=True)
    is_sent                 = ndb.BooleanProperty(required=True, default=False)
    created_datetime        = ndb.DateTimeProperty(required=True, auto_now_add=True)
    partition_datetime      = ndb.DateTimeProperty(required=False)
    
    dict_properties = ['table_template_name', 'dataset_name', 'table_name', 'stream_content', 'is_sent', 'partition_datetime']
    
    @staticmethod
    def list_not_send(offset=0, limit=model_conf.MAX_FETCH_RECORD, start_cursor=None,return_with_cursor=False, keys_only=False):
        query = UpstreamData.query(ndb.AND(UpstreamData.is_sent==False))
        
        return UpstreamData.list_all_with_condition_query(query, offset=offset, start_cursor=start_cursor, return_with_cursor=return_with_cursor, keys_only=keys_only, limit=limit)


    @staticmethod
    def list_all(offset=0, limit=model_conf.MAX_FETCH_RECORD, start_cursor=None,return_with_cursor=False, keys_only=False):
        query = UpstreamData.query()
        
        return UpstreamData.list_all_with_condition_query(query, offset=offset, start_cursor=start_cursor, return_with_cursor=return_with_cursor, keys_only=keys_only, limit=limit)

    @staticmethod
    def list_by_date_range(datetime_start, datetime_end, offset=0, limit=model_conf.MAX_FETCH_RECORD, start_cursor=None,return_with_cursor=False, keys_only=False):
        
        datetime_end = datetime_end + timedelta(days=1)
        query = UpstreamData.query(ndb.AND(
                                            UpstreamData.created_datetime>=datetime_start,
                                            UpstreamData.created_datetime<datetime_end,
                                        ))
        
        return UpstreamData.list_all_with_condition_query(query, offset=offset, start_cursor=start_cursor, return_with_cursor=return_with_cursor, keys_only=keys_only, limit=limit)
    
    
    @staticmethod
    def count_not_sent(limit=model_conf.MAX_FETCH_RECORD):
        return UpstreamData.query(ndb.AND(UpstreamData.is_sent==False)).count(limit = limit)
    
    @staticmethod
    def count_all(limit=model_conf.MAX_FETCH_RECORD):
        return UpstreamData.query().count(limit = limit)
    
    @staticmethod
    def count_by_date_range(datetime_start, datetime_end, limit=model_conf.MAX_FETCH_RECORD):
        datetime_end = datetime_end + timedelta(days=1)
        
        return UpstreamData.query(ndb.AND(
                                    UpstreamData.created_datetime>=datetime_start,
                                    UpstreamData.created_datetime<datetime_end,
                                )).count(limit = limit)
    
    @staticmethod
    def create(merchant_acct, dataset_name, table_name, table_template_name, stream_content, partition_datetime=None):
        UpstreamData(
                    merchant_acct       = merchant_acct.create_ndb_key(), 
                    table_template_name = table_template_name,
                    dataset_name        = dataset_name,
                    table_name          = table_name,
                    stream_content      = stream_content,
                    partition_datetime  = partition_datetime,
                    ).put()
                    

    
    
                    
    
