'''
Created on 7 Apr 2021

@author: jacklok
'''

from google.cloud import ndb
from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel
import trexmodel.conf as model_conf
from trexlib.utils.string_util import is_not_empty, random_string
from trexmodel.models.datastore.merchant_models import MerchantAcct, \
    MerchantUser
import logging
from dateutil.relativedelta import relativedelta

from datetime import datetime
from trexconf import program_conf

logger = logging.getLogger('model')

class MembershipBase(BaseNModel, DictModel):
    '''
    Merchant Acct as ancestor
    
    '''
    
    label                   = ndb.StringProperty(required=True)
    desc                    = ndb.StringProperty(required=False)
    terms_and_conditions    = ndb.StringProperty(required=False)
    
    expiration_type         = ndb.StringProperty(required=True)
    expiration_value        = ndb.IntegerProperty(required=False)
    
    archived                = ndb.BooleanProperty(default=False)
    
    discount_rate           = ndb.IntegerProperty(default=0)
    
    image_storage_filename  = ndb.StringProperty(required=False)
    image_public_url        = ndb.StringProperty(required=False)
    
    created_datetime        = ndb.DateTimeProperty(required=True, auto_now_add=True)
    modified_datetime       = ndb.DateTimeProperty(required=True, auto_now=True)
    archived_datetime       = ndb.DateTimeProperty(required=False)
    
    created_by              = ndb.KeyProperty(name="created_by", kind=MerchantUser)
    created_by_username     = ndb.StringProperty(required=False)
    
    modified_by             = ndb.KeyProperty(name="modified_by", kind=MerchantUser)
    modified_by_username    = ndb.StringProperty(required=False)

    dict_properties         = ['label', 'desc', 'terms_and_conditions', 'expiration_type', 
                               'expiration_value', 'created_datetime', 'modified_datetime',
                               'discount_rate', 'image_public_url',]
    
    @property
    def merchant_acct(self):
        return MerchantAcct.fetch(self.key.parent().urlsafe())
    
    @property
    def membership_card_image(self):
        if self.image_public_url:
            return self.image_public_url 
        else:
            return self.merchant_acct.logo_public_url
    
    @classmethod
    def list_by_merchant_acct(cls, merchant_acct, is_archived=False):
        return cls.query(ndb.AND(MerchantMembership.archived == is_archived), ancestor=merchant_acct.create_ndb_key()).fetch(limit=model_conf.MAX_FETCH_RECORD)
    
    def calc_expiry_date(self, start_date=None, number_of_year=None):
        
        if start_date is None:
            start_date = datetime.utcnow()
        
        logger.debug('start_date=%s', start_date)
        logger.debug('self.expiration_type=%s', self.expiration_type)
        if is_not_empty(number_of_year) and isinstance(number_of_year, int):
            return start_date + relativedelta(years=number_of_year)
        else:   
            if self.expiration_type == program_conf.MEMBERSHIP_EXPIRATION_TYPE_AFTER_YEAR:
                return start_date + relativedelta(years=self.expiration_value)
             
            elif self.expiration_type == program_conf.MEMBERSHIP_EXPIRATION_TYPE_AFTER_MONTH:
                return start_date + relativedelta(months=self.expiration_value)
            
            elif self.expiration_type == program_conf.MEMBERSHIP_EXPIRATION_TYPE_AFTER_WEEK:
                return start_date + relativedelta(weeks=self.expiration_value)
            
            elif self.expiration_type == program_conf.MEMBERSHIP_EXPIRATION_TYPE_AFTER_DAY:
                return start_date + relativedelta(days=self.expiration_value)
            
            else:
                #for no expiration
                return datetime.max
    
    @classmethod
    def upload_membership_card_image(cls, membership, uploading_file, merchant_acct, bucket, modified_by=None):
        file_prefix                         = random_string(8)
        image_storage_filename              = 'merchant/'+merchant_acct.key_in_str+'/membership/'+file_prefix+'-'+uploading_file.filename
        blob                                = bucket.blob(image_storage_filename)
        
        logger.debug('image_storage_filename=%s', image_storage_filename)
        
        blob.upload_from_string(
                uploading_file.read(),
                content_type=uploading_file.content_type
            )
        
        image_public_url        = blob.public_url
        
        
        modified_by_username = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        if is_not_empty(membership.image_storage_filename):
            old_image_blob = bucket.get_blob(membership.image_storage_filename) 
            if old_image_blob:
                old_image_blob.delete()
        
        membership.image_public_url       = image_public_url
        membership.image_storage_filename = image_storage_filename
        
        membership.modified_by            = modified_by.create_ndb_key()
        membership.modified_by_username   = modified_by_username
        
        membership.put() 
        
        
class MerchantMembership(MembershipBase):
    
    
    def to_configuration(self):
        membership_configuration = {
                                    'membership_key'                : self.key_in_str,
                                    'label'                         : self.label,
                                    'expiration_type'               : self.expiration_type,
                                    'expiration_value'              : self.expiration_value,
                                    'card_image'                    : self.membership_card_image,
                                    'is_tier'                       : False,
                                    }
        
        return membership_configuration
    
        
    @staticmethod
    def create(merchant_acct, label, desc=None, expiration_type=None, expiration_value=None, 
               created_by=None, discount_rate=0, terms_and_conditions=None):
        
        created_by_username = None
        if is_not_empty(created_by):
            if isinstance(created_by, MerchantUser):
                created_by_username = created_by.username
        
        merchant_membership = MerchantMembership(
                                                parent                  = merchant_acct.create_ndb_key(),
                                                label                   = label,
                                                desc                    = desc,
                                                discount_rate           = discount_rate,
                                                expiration_type         = expiration_type,
                                                expiration_value        = expiration_value,
                                                created_by              = created_by.create_ndb_key(),
                                                created_by_username     = created_by_username,
                                                terms_and_conditions    = terms_and_conditions,
                                                )
        
        merchant_membership.put()
        
        merchant_acct.add_membership(merchant_membership.to_configuration())
        
        return merchant_membership
    
    @staticmethod
    def update(merchant_membership, label, desc=None, expiration_type=None, expiration_value=None, 
               modified_by=None, discount_rate=0, terms_and_conditions=None):
        modified_by_username = None
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        merchant_membership.label                   = label
        merchant_membership.desc                    = desc
        merchant_membership.expiration_type         = expiration_type
        merchant_membership.expiration_value        = expiration_value
        merchant_membership.modified_by             = modified_by.create_ndb_key()
        merchant_membership.modified_by_username    = modified_by_username
        merchant_membership.discount_rate           = discount_rate
        merchant_membership.terms_and_conditions    = terms_and_conditions
        
        
        merchant_membership.put()
        
        merchant_acct = merchant_membership.merchant_acct
        merchant_acct.update_membership(merchant_membership.to_configuration())
    
    @classmethod
    def archive_membership(cls, membership):
        membership.archived = True
        membership.archived_datetime = datetime.now()
        membership.put()
        
        merchant_acct = membership.merchant_acct
        merchant_acct.remove_archieve_basic_membership(membership.key_in_str)    
    


class MerchantTierMembership(MembershipBase):        
    entitle_qualification_type          = ndb.StringProperty(required=True)
    entitle_qualification_value         = ndb.FloatProperty(required=False)
    upgrade_expiry_type                 = ndb.StringProperty(required=True)
    
    dict_properties         = ['label', 'desc', 'terms_and_conditions', 'expiration_type', 'expiration_value', 'entitle_qualification_type', 
                               'entitle_qualification_value', 'upgrade_expiry_type', 'created_datetime', 'modified_datetime',
                               'discount_rate', 'image_public_url',
                               ]
    
    
    def to_configuration(self):
        membership_configuration = {
                                    'membership_key'                : self.key_in_str,
                                    'label'                         : self.label,
                                    'expiration_type'               : self.expiration_type,
                                    'expiration_value'              : self.expiration_value,
                                    'entitle_qualification_type'    : self.entitle_qualification_type,
                                    'entitle_qualification_value'   : self.entitle_qualification_value,
                                    'upgrade_expiry_type'           : self.upgrade_expiry_type,
                                    'card_image'                    : self.membership_card_image,
                                    'is_tier'                       : True,
                                    }
        
        return membership_configuration
        
    @staticmethod
    def create(merchant_acct, label=None, desc=None, expiration_type=None, expiration_value=None, 
               entitle_qualification_type=None, entitle_qualification_value=None, upgrade_expiry_type=None,
               created_by=None, discount_rate=0, terms_and_conditions=None):
        
        created_by_username = None
        if is_not_empty(created_by):
            if isinstance(created_by, MerchantUser):
                created_by_username = created_by.username
        
        merchant_membership = MerchantTierMembership(
                                                parent                          = merchant_acct.create_ndb_key(),
                                                label                           = label,
                                                desc                            = desc,
                                                expiration_type                 = expiration_type,
                                                expiration_value                = expiration_value,
                                                entitle_qualification_type      = entitle_qualification_type,
                                                entitle_qualification_value     = entitle_qualification_value,
                                                upgrade_expiry_type             = upgrade_expiry_type,
                                                created_by                      = created_by.create_ndb_key(),
                                                created_by_username             = created_by_username,
                                                discount_rate                   = discount_rate,
                                                terms_and_conditions            = terms_and_conditions,
                                                )
        
        merchant_membership.put()
        
        membership_key = merchant_membership.key_in_str
        
        logger.debug('membership_key=%s', membership_key)
        
        merchant_acct.add_tier_membership(merchant_membership.to_configuration())
        
        return merchant_membership
    
    @staticmethod
    def update(merchant_membership, label=None, desc=None, expiration_type=None, expiration_value=None, 
               entitle_qualification_type=None, entitle_qualification_value=None, upgrade_expiry_type=None,
               modified_by=None, discount_rate=0, terms_and_conditions=None):
        
        modified_by_username = None
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        merchant_membership.label                           = label
        merchant_membership.desc                            = desc
        merchant_membership.expiration_type                 = expiration_type
        merchant_membership.expiration_value                = expiration_value
        merchant_membership.entitle_qualification_type      = entitle_qualification_type
        merchant_membership.entitle_qualification_value     = entitle_qualification_value
        merchant_membership.entitle_qualification_value     = entitle_qualification_value
        merchant_membership.upgrade_expiry_type             = upgrade_expiry_type
        merchant_membership.modified_by_username            = modified_by_username
        
        merchant_membership.discount_rate                   = discount_rate
        merchant_membership.terms_and_conditions            = terms_and_conditions
        
        merchant_membership.put()
        
        merchant_acct = merchant_membership.merchant_acct
        
        merchant_acct.update_tier_membership(merchant_membership.to_configuration())
        
        return merchant_membership
    
    @staticmethod
    def archive_membership(membership):
        membership.archived = True
        membership.archived_datetime = datetime.now()
        membership.put()
        
        merchant_acct = membership.merchant_acct
        merchant_acct.remove_archieve_tier_membership(membership.key_in_str)   


        