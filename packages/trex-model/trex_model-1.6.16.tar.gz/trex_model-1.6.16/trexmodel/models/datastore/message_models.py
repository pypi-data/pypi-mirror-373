'''
Created on 9 Nov 2023

@author: jacklok
'''

from google.cloud import ndb
from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel
from trexmodel.models.datastore.user_models import User
from datetime import datetime
import logging
from trexconf import conf
from trexmodel.models.datastore.transaction_models import CustomerTransaction
from trexmodel.models.datastore.redeem_models import RedemptionCatalogueTransaction,\
    CustomerRedemption
from trexmodel.models.datastore.merchant_models import MerchantAcct


logger = logging.getLogger('model')

'''

message content is json like below format
{
content_type=[html]
content_body=[text in html]

}

'''

class Message(BaseNModel, DictModel):
    '''
    User as ancestor
    '''
    message_to              = ndb.KeyProperty(name="message_to", kind=User)
    source_key              = ndb.StringProperty(required=False)
    title                   = ndb.StringProperty(required=True)
    message_category        = ndb.StringProperty(required=True, default=conf.MESSAGE_CATEGORY_SYSTEM, choices=conf.MESSAGE_CATEGORIES)
    message_content         = ndb.JsonProperty(required=True, indexed=False)
    message_data            = ndb.JsonProperty(required=True, indexed=False)
    message_from            = ndb.StringProperty(required=False)
    status                  = ndb.StringProperty(required=True, default=conf.MESSAGE_STATUS_NEW, choices=conf.MESSAGE_STATUS_SET)    
    created_datetime        = ndb.DateTimeProperty(required=True, auto_now_add=True)
    read_datetime           = ndb.DateTimeProperty(required=False)
    email_sent_datetime     = ndb.DateTimeProperty(required=False)

    dict_properties = [
                        'source_key', 'message_to', 'title', 'message_category', 'message_content', 'message_data', 'status', 'created_datetime'
                    ]

    @property
    def user_acct_entity(self):
        return User.fetch(self.message_to.urlsafe())
    
    
    @property
    def customer_transaction_entity(self):
        customer_transaction_key = self.message_data.get('reward_transaction_key')
        if customer_transaction_key:
            return  CustomerTransaction.fetch(customer_transaction_key)
        
    @property
    def customer_redemption_catalogue_entity(self):
        customer_redemption_key = self.message_data.get('redemption_catalogue_transaction_key')
        if customer_redemption_key:
            return  RedemptionCatalogueTransaction.fetch(customer_redemption_key)
        
    @property
    def customer_redemption_entity(self):
        customer_redemption_key = self.message_data.get('redemption_transaction_key')
        if customer_redemption_key:
            return  CustomerRedemption.fetch(customer_redemption_key)
        
    
    @staticmethod
    def create(user_acct, source_key=None, message_to=None, title=None, message_type=conf.MESSAGE_CATEGORY_ANNOUNCEMENT, message_content={}):
        Message(
            parent          = user_acct.create_ndb_key(),
            source_key      = source_key,
            message_to      = message_to.create_ndb_key(),
            title           = title,
            message_type    = message_type,
            message_content = message_content,
            created_datetime= datetime.utcnow(),
            ).put()
    
    @staticmethod        
    def update_read(message_key):
        message = Message.fetch(message_key)
        if message:
            user_acct = message.user_acct_entity
            logger.debug('found message title=%s', message.title)
            message.status = conf.MESSAGE_STATUS_READ
            message.read_datetime = datetime.utcnow()
            message.put()
            '''
            user_acct.new_message_count-=1
            if user_acct.new_message_count<0:
                user_acct.new_message_count=0

            user_acct.put()
            '''
            
    @staticmethod        
    def update_delete(message_key):
        message = Message.fetch(message_key)
        
        if message:
            logger.debug('found message title=%s', message.title)
            message.delete()   
            
    @staticmethod
    def list_paginated_by_user_account(user_acct, limit=conf.MAX_FETCH_RECORD, start_cursor=None):
        #query = Message.query(ancestor=user_acct.create_ndb_key()).order(-Message.created_datetime)
        query = Message.query(ndb.AND(Message.message_to==user_acct.create_ndb_key())).order(-Message.created_datetime)     
        
        return Message.list_all_with_condition_query(query, limit=limit, start_cursor=start_cursor, return_with_cursor=True, keys_only=False)
    
    
    @staticmethod
    def count_new_message(user_acct):
        return Message.count_by_status(user_acct, status=conf.MESSAGE_STATUS_NEW)
    
    @staticmethod
    def count_by_status(user_acct, status=conf.MESSAGE_STATUS_NEW):
        query = Message.query(ndb.AND(Message.status==status), ancestor=user_acct.create_ndb_key()).order(-Message.created_datetime)     
        
        return Message.count_with_condition_query(query, limit=conf.MAX_FETCH_RECORD)


    @staticmethod
    def get_by_source_key(source_key):
        return  Message.query(ndb.AND(Message.source_key==source_key)).get()
    

class MerchantMessage(BaseNModel, DictModel):
    title                   = ndb.StringProperty(required=True)
    message_category        = ndb.StringProperty(required=True, default=conf.MESSAGE_CATEGORY_SYSTEM, choices=conf.MESSAGE_CATEGORIES)
    message_content         = ndb.JsonProperty(required=True, indexed=False)
    message_data            = ndb.JsonProperty(required=True, indexed=False)
    status                  = ndb.StringProperty(required=True, default=conf.MESSAGE_STATUS_NEW, choices=conf.MESSAGE_STATUS_SET)    
    created_datetime        = ndb.DateTimeProperty(required=True, auto_now_add=True)
    read_datetime           = ndb.DateTimeProperty(required=False)
    
    dict_properties = [
                        'message_to', 'title', 'message_category', 'message_content', 'message_data', 'status', 
                        'created_datetime', 
                    ]


    @staticmethod
    def create(merchant_account, title=None, message_category=conf.MESSAGE_CATEGORY_SYSTEM, 
               message_content=None, message_data={}, status=conf.MESSAGE_STATUS_NEW, ):
        message = MerchantMessage(
                        parent              = merchant_account.create_ndb_key(),
                        title               = title,
                        message_category    = message_category,
                        message_content     = message_content,
                        message_data        = message_data,
                        status              = status
                        )
        message.put()
        return message

    @staticmethod
    def list_unread_by_merchant_account(merchant_account, limit=conf.MAX_FETCH_RECORD, start_cursor=None):
        #query = Message.query(ancestor=user_acct.create_ndb_key()).order(-Message.created_datetime)
        query = MerchantMessage.query(ancestor=merchant_account.create_ndb_key()).order(-MerchantMessage.created_datetime)     
        
        return MerchantMessage.list_all_with_condition_query(query, limit=limit, start_cursor=start_cursor, return_with_cursor=False, keys_only=False)
    
    
    
    
    