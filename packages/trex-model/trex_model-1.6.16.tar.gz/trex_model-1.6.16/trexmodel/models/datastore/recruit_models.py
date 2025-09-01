'''
Created on 27 Mar 2024

@author: jacklok
'''

from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel
from google.cloud import ndb
import logging
from builtins import staticmethod

logger = logging.getLogger('model')

class RecruitBase(BaseNModel, DictModel):
    name                        = ndb.StringProperty(required=True)
    mobile_phone                = ndb.StringProperty(required=True)
    email                       = ndb.StringProperty(required=True)
    address                     = ndb.TextProperty(required=False)
    submitted_datetime          = ndb.DateTimeProperty(required=True, auto_now=True)

class CoFounderRecruit(RecruitBase):
    involved_in_founding        = ndb.BooleanProperty(required=True)
    founding_details            = ndb.TextProperty(required=False)
    employment_time             = ndb.TextProperty(required=True)
    skill                       = ndb.TextProperty(required=True)
    other_skill                 = ndb.TextProperty(required=True)
    linkedin_profile            = ndb.TextProperty(required=True)
    
    
    @staticmethod
    def create(name=None, mobile_phone=None, email=None, address=None, involved_in_founding=False,
               founding_details=None, employment_time=None, skill=None, other_skill=None, linkedin_profile=None):
        CoFounderRecruit(
            name                    = name,
            mobile_phone            = mobile_phone,
            email                   = email,
            address                 = address,
            involved_in_founding    = involved_in_founding,
            founding_details        = founding_details,
            employment_time         = employment_time,
            skill                   = skill,
            other_skill             = other_skill,
            linkedin_profile        = linkedin_profile,
            ).put()
    