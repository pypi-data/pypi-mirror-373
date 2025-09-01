'''
Created on 23 Oct 2020

@author: jacklok
'''

from google.cloud import ndb
from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel

from datetime import datetime

class FacebookSubscriber(BaseNModel, DictModel):
    subscriber_fb_id        = ndb.StringProperty(required=True)
    name                    = ndb.StringProperty(required=False)
    email                   = ndb.StringProperty(required=False)
    last_engaged_datetime   = ndb.DateTimeProperty(required=True, auto_now_add=True)
    
    @staticmethod
    def create(subscriber_fb_id, name=None, email=None): 
        fb_subscriber = FacebookSubscriber.get_by_subscriber_id(subscriber_fb_id)
        if fb_subscriber is None:
            fb_subscriber = FacebookSubscriber(subscriber_fb_id=subscriber_fb_id, name=name, email=email)
        else:
            fb_subscriber.last_engaged_datetime = datetime.now()
            fb_subscriber.name  = name
            fb_subscriber.email = email
        
        fb_subscriber.put()
        
        return fb_subscriber
        
        
    @staticmethod
    def get_by_subscriber_id(subscriber_fb_id): 
        return FacebookSubscriber.query(ndb.AND(FacebookSubscriber.subscribe_fb_id==subscriber_fb_id)).get()    

class FacebookSubscriberMessage(BaseNModel, DictModel):
    subscriber_fb_id        = ndb.StringProperty(required=True)  
    conversation_id         = ndb.StringProperty(required=True)
    
    
          
