'''
Created on 30 Dec 2022

@author: jacklok
'''

from google.cloud import ndb
from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel
from trexmodel.models.datastore.merchant_models import Outlet
from trexlib.utils.string_util import random_number
import logging
from trexconf import conf
from datetime import datetime
#from google.api_core.operations_v1.operations_client_config import config

logger = logging.getLogger('debug')


class LoyaltyDeviceSetting(BaseNModel,DictModel):
    '''
    merchant_acct as ancestor
    '''
    device_name                     = ndb.StringProperty(required=True)
    activation_code                 = ndb.StringProperty(required=True)
    device_id                       = ndb.StringProperty(required=False)
    enable_lock_screen              = ndb.BooleanProperty(required=True, default=False)
    lock_screen_code                = ndb.StringProperty(required=False, default='')
    lock_screen_length_in_second    = ndb.IntegerProperty(required=False, default=30)
    activated                       = ndb.BooleanProperty(required=True, default=False)
    assigned_outlet                 = ndb.KeyProperty(name="assigned_outlet", kind=Outlet)
    created_datetime                = ndb.DateTimeProperty(required=True, auto_now_add=True)
    activated_datetime              = ndb.DateTimeProperty(required=False)
    testing                         = ndb.BooleanProperty(required=False, default=False)
    device_details                  = ndb.JsonProperty()
    
    dict_properties = ['device_name', 'activation_code', 'device_id', 'activated', 'assigned_outlet_key', 
                       'activated_datetime', 'created_datetime', 'device_details',
                       'enable_lock_screen', 'lock_screen_code', 'lock_screen_length_in_second'
                       ]
    
    @property
    def device_tokens_list(self):
        _tokens_list = []
        
        if self.device_details:
            
            for k,v in self.device_details.items():
                for dd in v:
                    _tokens_list.append(dd.get('device_token'))
        return _tokens_list
    
    @property
    def is_test_setting(self):
        return self.testing
    
    @property
    def assigned_outlet_key(self):
        return self.assigned_outlet.urlsafe().decode('utf-8')
    
    @property
    def assigned_outlet_entity(self):
        return Outlet.fetch(self.assigned_outlet_key)
    
    @property
    def merchant_acct_entity(self):
        return self.assigned_outlet_entity.merchant_acct_entity
    
    @staticmethod
    def create(device_name, merchant_acct, assign_outlet,
               enable_lock_screen,
               lock_screen_code,
               lock_screen_length_in_second,
               ):
        activation_code = random_number(16)
        checking_activation_device_setting = LoyaltyDeviceSetting.get_by_activation_code(activation_code)
        regenerate_activation_code = False
        
        if checking_activation_device_setting:
            regenerate_activation_code = True
        
        while(regenerate_activation_code):
            activation_code = random_number(16)
            checking_activation_device_setting = LoyaltyDeviceSetting.get_by_activation_code(activation_code)
            if checking_activation_device_setting==None:
                regenerate_activation_code = False
            
        
        device_setting = LoyaltyDeviceSetting(
                                parent                          = merchant_acct.create_ndb_key(),
                                device_name                     = device_name,
                                activation_code                 = activation_code,
                                assigned_outlet                 = assign_outlet.create_ndb_key(),
                                enable_lock_screen              = enable_lock_screen,
                                lock_screen_code                = lock_screen_code,
                                lock_screen_length_in_second    = lock_screen_length_in_second,
                                
                                )
        
        device_setting.put()
        return device_setting
    
    @staticmethod
    def update(pos_setting_key, device_name, assigned_outlet,
               enable_lock_screen,
               lock_screen_code,
               lock_screen_length_in_second,
               ):
        checking_device_setting                                 = LoyaltyDeviceSetting.fetch(pos_setting_key)
        checking_device_setting.device_name                     = device_name
        checking_device_setting.assigned_outlet                 = assigned_outlet.create_ndb_key()
        checking_device_setting.enable_lock_screen              = enable_lock_screen
        checking_device_setting.lock_screen_code                = lock_screen_code
        checking_device_setting.lock_screen_length_in_second    = lock_screen_length_in_second
        checking_device_setting.put()
        
        return checking_device_setting
    
    @staticmethod
    def get_by_activation_code(activation_code):
        return LoyaltyDeviceSetting.query(LoyaltyDeviceSetting.activation_code ==activation_code).get()
        
    
    @staticmethod
    def list_by_merchant_account(merchant_acct, offset=0, limit=conf.PAGINATION_SIZE, start_cursor=None, return_with_cursor=False):
        query = LoyaltyDeviceSetting.query(ancestor=merchant_acct.create_ndb_key())
        
        return LoyaltyDeviceSetting.list_all_with_condition_query(query, offset=offset, limit=limit, start_cursor=start_cursor, return_with_cursor=return_with_cursor)
    
    @staticmethod
    def count_by_merchant_acct(merchant_acct):
        if merchant_acct:
            query = LoyaltyDeviceSetting.query(ancestor=merchant_acct.create_ndb_key())
        else:
            query = LoyaltyDeviceSetting.query()
        
        return LoyaltyDeviceSetting.count_with_condition_query(query)
    
    @staticmethod
    def list_by_merchant_account_and_assigned_outlet(merchant_acct, assigned_outlet, offset=0, limit=conf.PAGINATION_SIZE, start_cursor=None, return_with_cursor=False):
        query = LoyaltyDeviceSetting.query(ndb.AND(
                        LoyaltyDeviceSetting.assigned_outlet==assigned_outlet.create_ndb_key()
                        ),ancestor=merchant_acct.create_ndb_key())
        
        return LoyaltyDeviceSetting.list_all_with_condition_query(query, offset=offset, limit=limit, start_cursor=start_cursor, return_with_cursor=return_with_cursor)
    
    @staticmethod
    def count_by_merchant_account_and_assigned_outlet(merchant_acct, assigned_outlet):
        query = LoyaltyDeviceSetting.query(ndb.AND(
                        LoyaltyDeviceSetting.assigned_outlet==assigned_outlet.create_ndb_key()
                        ),ancestor=merchant_acct.create_ndb_key())
        
        return LoyaltyDeviceSetting.count_with_condition_query(query)
        
    def activate(self, device_id, activated=True):
        self.device_id          = device_id
        self.activated          = activated
        self.activated_datetime = datetime.utcnow()
        self.put()
        
        
    @staticmethod
    def remove_by_activation_code(activation_code):
        checking_device_setting = LoyaltyDeviceSetting.get_by_activation_code(activation_code)
        if checking_device_setting:
            checking_device_setting.delete()
            return True
        else:
            return False
        
    def update_device_details(self, platform, device_token):
        if self.device_details:
            found_device_details_list_by_platform = self.device_details.get(platform)
            if found_device_details_list_by_platform:
                self.device_details[platform] = {
                                                'device_token'              : device_token,
                                                'last_updated_datetime'     : datetime.utcnow().strftime("%d-%m-%Y %H:%M:%S"),
                                                }
                                                        
                
                '''
                is_found = False
                
                for device_details_by_platform in  found_device_details_list_by_platform:
                    device_token_by_platform = device_details_by_platform.get('device_token')
                    if device_token_by_platform:
                        device_details_by_platform['last_updated_datetime'] = datetime.utcnow().strftime("%d-%m-%Y %H:%M:%S")
                        is_found = True
                        break
                
                if is_found == False:
                    found_device_details_list_by_platform.append(
                                                                {
                                                                'device_token'              : device_token,
                                                                'last_updated_datetime'     : datetime.utcnow().strftime("%d-%m-%Y %H:%M:%S"),
                                                                }
                                                            )
                        
                '''    
            else:
                self.device_details[platform] = {
                                                'device_token'              : device_token,
                                                'last_updated_datetime'     : datetime.utcnow().strftime("%d-%m-%Y %H:%M:%S"),
                                                }
        else:
            self.device_details = {
                                    platform :  {
                                                    'device_token'              : device_token,
                                                    'last_updated_datetime'     : datetime.utcnow().strftime("%d-%m-%Y %H:%M:%S"),
                                                    }
                                                
                                }
        self.put()    
