'''
Created on 19 Feb 2021

@author: jacklok
'''
from google.cloud import ndb
from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel, FullTextSearchable
import logging


logger = logging.getLogger('model')

class CorporateBase(BaseNModel, DictModel, FullTextSearchable):
    
    company_name            = ndb.StringProperty(required=True)
    contact_name            = ndb.StringProperty(required=False)
    address                 = ndb.StringProperty(required=False)
    office_phone            = ndb.StringProperty(required=False)
    mobile_phone            = ndb.StringProperty(required=False)
    fax_phone               = ndb.StringProperty(required=False)
    email                   = ndb.StringProperty(required=False)
    country                 = ndb.StringProperty(required=False, default='my')
    status                  = ndb.StringProperty(required=False)
    
    modified_datetime       = ndb.DateTimeProperty(required=True, auto_now=True)
    registered_datetime     = ndb.DateTimeProperty(required=True, auto_now_add=True)
    plan_start_date         = ndb.DateProperty(required=True)
    plan_end_date           = ndb.DateProperty(required=True)
    
    fulltextsearch_field_name   = 'company_name'
    
    

class CorporateAcct(CorporateBase):
    account_code                = ndb.StringProperty(required=False)
    logo_public_url             = ndb.StringProperty(required=False)
    logo_storage_filename       = ndb.StringProperty(required=False)
    dashboard_stat_figure       = ndb.JsonProperty()
    currency_code               = ndb.StringProperty(required=False, default='myr')
    
    
    