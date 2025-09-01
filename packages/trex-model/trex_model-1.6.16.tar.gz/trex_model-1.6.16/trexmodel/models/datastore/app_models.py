'''
Created on 23 May 2023

@author: jacklok
'''

import logging
from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel
from google.cloud import ndb
from datetime import datetime
import trexmodel.conf as model_conf

logger = logging.getLogger('model')

class AppMessageBase(BaseNModel, DictModel):
    title                   = ndb.StringProperty(required=True)
    content                 = ndb.StringProperty(required=False)
    start_date              = ndb.DateProperty(required=True)
    end_date                = ndb.DateProperty(required=True)
    archived                = ndb.BooleanProperty(default=False)
    
    created_datetime        = ndb.DateTimeProperty(required=True, auto_now_add=True)
    modified_datetime       = ndb.DateTimeProperty(required=True, auto_now=True)
    archived_datetime       = ndb.DateTimeProperty(required=False)
    
    @classmethod
    def create(cls, title, content=None, start_date=None, end_date=None):
        message = cls(
                        title       = title, 
                        content     = content,
                        start_date  = start_date,
                        end_date    = end_date,
                        )
        message.put()
        return message
    
    @classmethod
    def update(cls, message, title=None, content=None, start_date=None, end_date=None):
        message.title         = title
        message.content       = content
        message.start_date    = start_date
        message.end_date      = end_date
        message.put()
        
    def archive(self):
        self.archived = True
        self.archived_datetime = datetime.now()
        self.put()    
        
    @classmethod
    def list(cls, is_archived=False):
        return cls.query(ndb.AND(cls.archived == is_archived)).fetch(limit=model_conf.MAX_FETCH_RECORD)
    
    @classmethod
    def list_active(cls):
        now = datetime.now().date()
        return cls.query(ndb.AND(cls.archived == False, cls.start_date>=now, cls.end_date<now)).fetch(limit=model_conf.MAX_FETCH_RECORD)

class AppMessage(AppMessageBase):
    pass
    

class AppPromotion(AppMessageBase):
    image_file_type                = ndb.StringProperty(required=False)
    image_file_public_url          = ndb.StringProperty(required=False)
    image_file_storage_filename    = ndb.StringProperty(required=False)
    
    
    
    
        