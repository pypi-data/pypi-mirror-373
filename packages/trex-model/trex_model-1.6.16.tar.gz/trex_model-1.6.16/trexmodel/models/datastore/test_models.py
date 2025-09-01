'''
Created on 16 May 2021

@author: jacklok
'''

from google.cloud import ndb
from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel
import logging


logger = logging.getLogger('model')

class TestModelBase(BaseNModel, DictModel):
    id                      = ndb.IntegerProperty(required=True, default=1)
    value                   = ndb.StringProperty(required=True)
    modified_datetime       = ndb.DateTimeProperty(required=True, auto_now=True)
    
    @classmethod
    def create(cls, id=1, value='1'):
        test_model = cls(id=id, value=value)
        test_model.put()

    @classmethod
    def get_by_id(cls, id):
        return cls.query(cls.id==id).get()

class TestModelA(TestModelBase):
    pass

        
class TestModelB(TestModelBase):
    pass      