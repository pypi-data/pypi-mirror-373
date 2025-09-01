'''
Created on 28 Jul 2025

@author: jacklok
'''

from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel
from google.cloud import ndb
import logging

#logger = logging.getLogger('model')
logger = logging.getLogger('target_debug')

class SupportReportBase(BaseNModel, DictModel):
    activation_code                 = ndb.StringProperty(required=False)
    platform                        = ndb.StringProperty(required=True)
    error_message                   = ndb.TextProperty(required=False)
    stack_trace                     = ndb.TextProperty(required=False)
    reported_datetime               = ndb.DateTimeProperty(required=True, auto_now=True)
    
    
    
class ErrorReport(SupportReportBase):
    
    @staticmethod
    def create(platform, error_message, activation_code=None, stack_trace=None, ):
        ErrorReport(
            activation_code     = activation_code,
            platform            = platform,
            error_message       = error_message,
            stack_trace         = stack_trace, 
            ).put()
