'''
Created on 2 Mar 2025

@author: jacklok
'''
from google.cloud import ndb
from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel
from trexconf import conf

class PromotionCode(BaseNModel, DictModel):    
    label   = ndb.StringProperty(required=True)
    desc    = ndb.StringProperty(required=False)
    created_datetime    = ndb.DateTimeProperty(required=True, auto_now_add=True)
    
    dict_properties = ['label', 'desc', 'created_datetime']
    
    @classmethod
    def create_code(cls,parent=None, label=None, desc=None):
        created_code = cls(
                            parent  = parent,
                            label   = label,
                            desc    = desc,
                            )
        
        created_code.put()
        
        return created_code
    
    @classmethod
    def get_by_label(cls, parent, label):
        return cls.query(ndb.AND(cls.label==label), ancestor=parent).fetch(limit=1)
    
class MerchantPromotionCode(PromotionCode):    
    
    @staticmethod
    def create(merchant_acct, label=None, desc=None):
        return MerchantPromotionCode.create_code(parent=merchant_acct.create_ndb_key(), label=label, desc=desc)
    
    def update(self, label=None, desc=None):
        self.label  = label
        self.desc   = desc
        self.put()
        
    @staticmethod
    def list_by_merchant_account(merchant_acct):
        return MerchantPromotionCode.query(ancestor = merchant_acct.create_ndb_key()).fetch(limit = conf.MAX_FETCH_RECORD)
    
    @staticmethod
    def get_by_merchant_label(merchant_acct, label):
        return MerchantPromotionCode.get_by_label(merchant_acct.create_ndb_key(), label)         
