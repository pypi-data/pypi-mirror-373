'''
Created on 19 Aug 2021

@author: jacklok
'''

from google.cloud import ndb
from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel
from trexmodel.models.datastore.merchant_models import MerchantUser
import logging

logger = logging.getLogger('model')


class ProductStock(BaseNModel,DictModel):
    '''
    Product as ancestor
    '''
    stock_code              = ndb.StringProperty(required=True)
    code_type               = ndb.StringProperty(required=False)
    quantity                = ndb.IntegerProperty(required=True, default=0)
    cost_price              = ndb.FloatProperty()
    created_by              = ndb.KeyProperty(name="created_by", kind=MerchantUser)
    created_datetime        = ndb.DateTimeProperty(required=True, auto_now_add=True)
    
    
    dict_properties = ['stock_code', 'code_type', 'parent_category_code', 'has_child']
