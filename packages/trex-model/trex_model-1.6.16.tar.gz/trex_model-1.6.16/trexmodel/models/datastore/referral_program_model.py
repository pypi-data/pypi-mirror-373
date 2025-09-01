'''
Created on 8 Apr 2024

@author: jacklok
'''

from google.cloud import ndb
from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel
import trexmodel.conf as model_conf
from trexlib.utils.string_util import is_not_empty
from trexmodel.models.datastore.merchant_models import MerchantAcct, MerchantUser
import logging
from trexconf import conf, program_conf
from datetime import datetime
from trexmodel.models.datastore.model_decorators import model_transactional
from builtins import staticmethod
    


#logger = logging.getLogger('model')
logger = logging.getLogger('debug')

class BaseProgram(BaseNModel, DictModel):
    completed_status                    = ndb.StringProperty(required=True, choices=set(program_conf.REFERRAL_PROGRAM_STATUS))
    #reward_format                       = ndb.StringProperty(required=False, choices=set(program_conf.REWARD_FORMAT_SET))
    start_date                          = ndb.DateProperty(required=True)
    end_date                            = ndb.DateProperty(required=True)
    
    label                               = ndb.StringProperty(required=False)
    desc                                = ndb.StringProperty(required=False)
    
    promote_title                       = ndb.StringProperty(required=False)
    promote_desc                        = ndb.StringProperty(required=False)
    
    program_settings                    = ndb.JsonProperty(required=True)
    created_datetime                    = ndb.DateTimeProperty(required=True, auto_now_add=True)
    modified_datetime                   = ndb.DateTimeProperty(required=True, auto_now=True)
    published_datetime                  = ndb.DateTimeProperty(required=False)
    archived_datetime                   = ndb.DateTimeProperty(required=False)
    remarks                             = ndb.StringProperty(required=False)
    
    created_by                          = ndb.KeyProperty(name="created_by", kind=MerchantUser)
    created_by_username                 = ndb.StringProperty(required=False)
    modified_by                         = ndb.KeyProperty(name="modified_by", kind=MerchantUser)
    modified_by_username                = ndb.StringProperty(required=False)
    
    enabled                             = ndb.BooleanProperty(default=True)
    archived                            = ndb.BooleanProperty(default=False)
    
    image_storage_filename              = ndb.StringProperty(required=False)
    image_public_url                    = ndb.StringProperty(required=False)
    
    program_code                        = ndb.StringProperty(required=False)
    
    loyalty_package                     = ndb.StringProperty(required=False, default=program_conf.LOYALTY_PACKAGE_SCALE)
    
    @property
    def is_enabled(self):
        return self.enabled
    
    @property
    def is_disabled(self):
        return self.enabled==False
    
    @property
    def is_archived(self):
        return self.archived
    
    @property
    def is_published(self):
        return self.completed_status == program_conf.PROGRAM_STATUS_PUBLISH
    
    @property
    def is_review_state(self):
        return program_conf.is_existing_referral_program_status_final_state(self.completed_status)
    
    @classmethod
    @model_transactional(desc="publish_program")
    def publish_program(cls, program):
        program.completed_status = program_conf.PROGRAM_STATUS_PUBLISH
        program.published_datetime = datetime.now()
        program.put()
        
        merchant_acct = program.merchant_acct_entity
        merchant_acct.update_published_referral_program(program.to_configuration())
        
    @classmethod
    @model_transactional(desc="archive_program")
    def archive_program(cls, program):
        program.archived = True
        program.archived_datetime = datetime.now()
        program.put()
        
        merchant_acct = program.merchant_acct_entity
        merchant_acct.remove_program_from_published_referral_program_configuration(program.key_in_str) 
        
    
    @classmethod
    @model_transactional(desc="enable program")
    def enable(cls, program, modified_by=None):
        program.enabled = True
        
        modified_by_username = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        program.modified_by            = modified_by.create_ndb_key()
        program.modified_by_username   = modified_by_username
        
        if program.is_published:
            merchant_acct = program.merchant_acct_entity
            merchant_acct.update_published_referral_program(program.to_configuration())
        
        program.put()
            
    @classmethod
    @model_transactional(desc="disable program")
    def disable(cls, program, modified_by=None):
        program.enabled = False
        
        modified_by_username = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
                program.modified_by            = modified_by.create_ndb_key()
                
        program.modified_by_username   = modified_by_username
        
        program.put()  
        
        if program.is_published:
            merchant_acct = program.merchant_acct_entity
            merchant_acct.remove_program_from_published_referral_program_configuration(program.key_in_str)
        
    @property
    def merchant_acct_entity(self):
        return MerchantAcct.fetch(self.key.parent().urlsafe())    
        
    def to_configuration(self):
        program_configuration = {
                                'merchant_acct_key'                 : self.parent_key,
                                'program_key'                       : self.key_in_str,
                                'label'                             : self.label,
                                'desc'                              : self.desc,
                                'start_date'                        : self.start_date.strftime('%d-%m-%Y'),
                                'end_date'                          : self.end_date.strftime('%d-%m-%Y'),
                                'promote_title'                     : self.promote_title,
                                'promote_desc'                      : self.promote_desc,
                                'promote_image_link'                : self.image_public_url,    
                                'program_settings'                  : self.program_settings,
                                'is_published'                      : self.is_published,  
                                }
        
        return program_configuration

class MerchantReferralProgram(BaseProgram):
    dict_properties                     = [
                                           'completed_status', 'start_date', 'end_date', 'label','desc', 
                                           'program_settings', 
                                           'created_datetime', 'modified_datetime',  'enabled',
                                           'archived_datetime',
                                           'is_enabled', 'is_disabled', 'is_review_state', 
                                           'is_published', 'archived', 'completed_progress_in_percentage', 
                                           'completed_status_index',
                                           'promote_title', 'promote_desc', 'promote_image_link',
                                           'remarks', 'loyalty_package', 'image_storage_filename', 'image_public_url',
                                           'created_by_username', 'modified_by_username']
    
    
    @property
    def promote_image_link(self):
        return self.image_public_url
    
    @property
    def completed_progress_in_percentage(self):
        return program_conf.referral_program_completed_progress_percentage(self.completed_status)
    
    @property
    def completed_status_index(self):
        return program_conf.get_referral_program_completed_status_index(self.completed_status)
    
    @staticmethod
    def create(merchant_acct, label=None, 
               desc=None, start_date=None, end_date=None, created_by=None,
               default_promote_image = None,
               loyalty_package = program_conf.LOYALTY_PACKAGE_SCALE,
               ):
        
        created_by_username = None
        if is_not_empty(created_by):
            if isinstance(created_by, MerchantUser):
                created_by_username = created_by.username
        
        program_settings = {
                            }
        
        
        
        merchant_program =  MerchantReferralProgram(
                                        parent                = merchant_acct.create_ndb_key(),
                                        label                 = label,
                                        #reward_format         = reward_format,
                                        desc                  = desc,
                                        start_date            = start_date,
                                        end_date              = end_date,
                                        created_by            = created_by.create_ndb_key(),
                                        created_by_username   = created_by_username,
                                        completed_status      = program_conf.PROGRAM_STATUS_PROGRAM_BASE,
                                        program_settings      = program_settings,
                                        loyalty_package       = loyalty_package,
                                        image_public_url      = default_promote_image,
                                        )
        
        merchant_program.put()
        return merchant_program
    
    @staticmethod
    def update_program_base_data(program, label=None,   
                                 desc=None,start_date=None, end_date=None, modified_by=None, 
                                 default_promote_image = None, 
                                 loyalty_package=program_conf.LOYALTY_PACKAGE_LITE,
                                 ):
        
        modified_by_username = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        program_settings = program.program_settings or {}
        
        
        program.label                   = label
        program.desc                    = desc
        #program.reward_format           = reward_format
        program.start_date              = start_date
        program.end_date                = end_date
        program.modified_by             = modified_by.create_ndb_key()
        program.modified_by_username    = modified_by_username
        program.completed_status        = program_conf.PROGRAM_STATUS_PROGRAM_BASE 
        program.program_settings        = program_settings
        program.loyalty_package         = loyalty_package
        program.image_public_url        = default_promote_image
        
        
        program.put()
        
        return program
    
    @staticmethod
    def define_referrer_reward(program, modified_by=None):
        
        modified_by_username = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        program.modified_by             = modified_by.create_ndb_key()
        program.modified_by_username    = modified_by_username
        program.completed_status        = program_conf.PROGRAM_STATUS_DEFINE_REFERRER_REWARD 
        
        
        program.put()
        
        return program
    
    @staticmethod
    def define_referee_reward(program, modified_by=None):
        
        modified_by_username = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        program.modified_by             = modified_by.create_ndb_key()
        program.modified_by_username    = modified_by_username
        program.completed_status        = program_conf.PROGRAM_STATUS_DEFINE_REFEREE_REWARD 
        
        
        program.put()
        
        return program
    
    @staticmethod
    def __add_program_reward(program, point_configuration, modified_by=None, target_reward_items_naming='referrer_reward_items'):
        modified_by_username = None
        
        rewards_list = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        if program.program_settings is None:
            rewards_list       = []
            program_settings    = {}
            
        else:
            program_settings    = program.program_settings
            rewards_list       = program_settings.get(target_reward_items_naming) or []
            
        
        rewards_list.append(point_configuration)
        logger.debug('rewards_list=%s', rewards_list)
        program_settings[target_reward_items_naming]    = rewards_list
        
        program.modified_by            = modified_by.create_ndb_key()
        program.modified_by_username   = modified_by_username
        program.program_settings       = program_settings
        
        program.put()
        
        return program
    
    @staticmethod
    def __remove_program_reward(program, voucher_index, modified_by=None, target_reward_items_naming='referrer_reward_items'):
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        program_settings            = program.program_settings
        existing_rewards_list      = program_settings.get(target_reward_items_naming) or []
        new_rewards_list = []
        for reward in existing_rewards_list:
            if reward.get('reward_index') !=voucher_index:
                new_rewards_list.append(reward)
        
        program_settings[target_reward_items_naming]    = new_rewards_list
        
        program.modified_by            = modified_by.create_ndb_key()
        program.modified_by_username   = modified_by_username
        program.program_settings       = program_settings
        
        program.put()
    
    @staticmethod
    def add_referrer_program_reward(program, reward_configuration, modified_by=None):
        return MerchantReferralProgram.__add_program_reward(program, reward_configuration, modified_by=modified_by, target_reward_items_naming='referrer_reward_items')
    
    @staticmethod
    def add_referee_program_reward(program, reward_configuration, modified_by=None):
        return MerchantReferralProgram.__add_program_reward(program, reward_configuration, modified_by=modified_by, target_reward_items_naming='referee_reward_items')
    
    @staticmethod
    def remove_referrer_program_reward(program, reward_index, modified_by=None):
        MerchantReferralProgram.__remove_program_reward(program, reward_index, modified_by=modified_by, target_reward_items_naming='referrer_reward_items')
        
    @staticmethod
    def remove_referee_program_reward(program, reward_index, modified_by=None):
        MerchantReferralProgram.__remove_program_reward(program, reward_index, modified_by=modified_by, target_reward_items_naming='referee_reward_items')        
    
    @staticmethod
    def list_by_merchant_account(merchant_acct):
        return MerchantReferralProgram.query(ndb.AND(MerchantReferralProgram.archived!=True), ancestor=merchant_acct.create_ndb_key()).fetch(limit=model_conf.MAX_FETCH_RECORD)
    
    @staticmethod
    def list_archived_by_merchant_account(merchant_acct):
        return MerchantReferralProgram.query(ndb.AND(MerchantReferralProgram.archived==True), ancestor=merchant_acct.create_ndb_key()).fetch(limit=model_conf.MAX_FETCH_RECORD)
    
    
    
    