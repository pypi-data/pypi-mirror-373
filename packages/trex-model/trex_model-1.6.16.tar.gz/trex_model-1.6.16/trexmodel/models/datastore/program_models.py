'''
Created on 19 Feb 2021

@author: jacklok
'''
from google.cloud import ndb
from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel
import trexmodel.conf as model_conf
from trexlib.utils.string_util import is_not_empty, random_string
from trexmodel.models.datastore.merchant_models import MerchantAcct,MerchantUser
import logging
from trexconf import conf, program_conf
from datetime import datetime
from trexmodel.models.datastore.model_decorators import model_transactional
from trexlib.utils.common.common_util import sort_list, sort_dict_list
from _datetime import timedelta
    


#logger = logging.getLogger('model')
logger = logging.getLogger('debug')

def create_schedule_program(merchant_acct, program):
    if program.reward_base in (program_conf.SCHEDULE_BASED_PROGRAM):
        
        if program.reward_base == program_conf.REWARD_BASE_ON_BIRTHDAY:
            if program.giveaway_reward_when == program_conf.PROGRAM_SCHEDULE_TYPE_MONTH_START:
                MerchantScheduleProgram.create_first_day_of_month_schedule_program(merchant_acct, program)
            
            elif program.giveaway_reward_when == program_conf.ADVANCE_IN_DAY:
                MerchantScheduleProgram.create_daily_schedule_program(merchant_acct, program)
                
        elif program.reward_base == program_conf.REWARD_BASE_ON_GIVEAWAY:
            if program.giveaway_system_condition == program_conf.GIVEAWAY_SYSTEM_CONDITION_MEMBERSHIP_YEAR:
                MerchantScheduleProgram.create_daily_schedule_program(merchant_acct, program)
                        
    

def remove_schedule_program(program):
    if program.reward_base in (program_conf.SCHEDULE_BASED_PROGRAM):
        MerchantScheduleProgram.remove_by_merchant_program(program)

class BaseProgram(BaseNModel, DictModel):
    reward_base                         = ndb.StringProperty(required=True, choices=set(program_conf.REWARD_BASE_SET))
    reward_format                       = ndb.StringProperty(required=False, choices=set(program_conf.REWARD_FORMAT_SET))
    completed_status                    = ndb.StringProperty(required=True, choices=set(program_conf.ALL_PROGRAM_STATUS))
    giveaway_method                     = ndb.StringProperty(required=True, default=program_conf.PROGRAM_REWARD_GIVEAWAY_METHOD_SYSTEM)
    start_date                          = ndb.DateProperty(required=True)
    end_date                            = ndb.DateProperty(required=True)
    label                               = ndb.StringProperty(required=False)
    desc                                = ndb.StringProperty(required=False)
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
        return program_conf.is_existing_program_status_final_state(self.completed_status)
    
    @property
    def exclusive_tags_list(self):
        if self.program_settings.get('exclusivity') and self.program_settings.get('exclusivity').get('tags'):
            return ','.join(self.program_settings.get('exclusivity').get('tags')) or ''
    
    @property
    def exclusive_promotion_codes_list(self):
        if self.program_settings.get('exclusivity') and self.program_settings.get('exclusivity').get('promotion_codes'):
            return ','.join(self.program_settings.get('exclusivity').get('promotion_codes')) or ''
        
    @property
    def exclusive_memberships_list(self):
        if self.program_settings.get('exclusivity') and self.program_settings.get('exclusivity').get('memberships'):
            return ','.join(self.program_settings.get('exclusivity').get('memberships')) or ''
        
    @property
    def exclusive_tier_memberships_list(self):
        if self.program_settings.get('exclusivity') and self.program_settings.get('exclusivity').get('tier_memberships'):
            return ','.join(self.program_settings.get('exclusivity').get('tier_memberships')) or ''  
    
    @property
    def spending_currency(self):
        return self.program_settings.get('scheme').get('spending_currency')
    
    @property
    def reward_amount(self):
        return self.program_settings.get('scheme').get('reward_amount')
    
    @property
    def reward_limit_type(self):
        if self.program_settings and self.program_settings.get('scheme'):
            return self.program_settings.get('scheme').get('reward_limit_type')
        
    @property
    def reward_limit_amount(self):
        if self.program_settings and self.program_settings.get('scheme'):
            return self.program_settings.get('scheme').get('reward_limit_amount')
    
    @property
    def is_reward_amount_required(self):
        return self.reward_format in (program_conf.REWARD_FORMAT_POINT, program_conf.REWARD_FORMAT_STAMP)
    
    @property
    def is_recurring_scheme(self):
        if self.program_settings and self.program_settings.get('scheme'):
            return self.program_settings.get('scheme').get('is_recurring_scheme')
        return False
    
    @property
    def limit_to_specific_day(self):
        try:
            if self.program_settings and self.program_settings.get('scheme'):
                return self.program_settings.get('scheme').get('limit_to_specific_day')
        except:
            pass
        return False
    
    @property
    def limit_to_specific_date_of_month(self):
        try:
            if self.program_settings and self.program_settings.get('scheme'):
                return self.program_settings.get('scheme').get('limit_to_specific_date_of_month')
        except:
            pass
        return False
    
    @property
    def specified_days_list(self):
        try:
            if self.program_settings and self.program_settings.get('scheme'):
                return self.program_settings.get('scheme').get('specified_days_list')
        except:
            pass
        return []
    
    @property
    def specified_dates_of_month_list(self):
        try:
            if self.program_settings and self.program_settings.get('scheme'):
                return self.program_settings.get('scheme').get('specified_dates_of_month_list')
        except:
            pass
        return []
        
    @property
    def giveaway_system_condition(self):
        if self.program_settings and self.program_settings.get('giveaway_system_settings'):
            return self.program_settings.get('giveaway_system_settings').get('giveaway_system_condition')
        
    @property
    def expiration_type(self):
        if self.program_settings and self.program_settings.get('scheme'):
            return self.program_settings.get('scheme').get('expiration_type')    
        
    @property
    def is_expiration_date_type(self):
        if self.program_settings and self.program_settings.get('scheme'):
            return self.program_settings.get('scheme').get('expiration_type') == program_conf.REWARD_EXPIRATION_TYPE_SPECIFIC_DATE    
        
    @property
    def expiration_date(self):
        if self.program_settings and self.program_settings.get('scheme'):
            return self.program_settings.get('scheme').get('expiration_date')
        
    @property
    def expiration_value(self):
        if self.program_settings and self.program_settings.get('scheme'):
            return self.program_settings.get('scheme').get('expiration_value')                
    
    @property
    def giveaway_reward_when(self):
        if self.program_settings.get('scheme') and self.program_settings.get('scheme').get('giveaway_when'):
            return self.program_settings.get('scheme').get('giveaway_when')
        
    @property
    def giveaway_reward_advance_in_day(self):
        if self.program_settings.get('scheme') and self.program_settings.get('scheme').get('advance_in_day'):
            return self.program_settings.get('scheme').get('advance_in_day')
        else:
            return 0 
    
    @classmethod
    def update_prorgram_exclusivity_data(cls, program, exclusivity_configuration={}, modified_by=None):
        modified_by_username = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        program_settings = program.program_settings
        program_settings['exclusivity'] = exclusivity_configuration
            
        program.modified_by            = modified_by.create_ndb_key()
        program.modified_by_username   = modified_by_username
        program.completed_status       = program_conf.PROGRAM_STATUS_EXCLUSIVITY
        program.program_settings       = program_settings
        
        program.put()
        
        return program
    '''
    @classmethod
    def create_schedule_program(cls, merchant_acct, program):
        if program.reward_base in (program_conf.SCHEDULE_BASED_PROGRAM):
            
            if program.reward_base == program_conf.REWARD_BASE_ON_BIRTHDAY:
                if program.giveaway_reward_when == program_conf.PROGRAM_SCHEDULE_TYPE_MONTH_START:
                    MerchantScheduleProgram.create_first_day_of_month_schedule_program(merchant_acct, program)
                
                elif program.giveaway_reward_when == program_conf.ADVANCE_IN_DAY:
                    MerchantScheduleProgram.create_daily_schedule_program(merchant_acct, program)
                    
            elif program.reward_base == program_conf.REWARD_BASE_ON_GIVEAWAY:
                if program.giveaway_system_condition == program_conf.GIVEAWAY_SYSTEM_CONDITION_MEMBERSHIP_YEAR:
                    MerchantScheduleProgram.create_daily_schedule_program(merchant_acct, program)
                        
    
    @classmethod
    def remove_schedule_program(cls, program):
        if program.reward_base in (program_conf.SCHEDULE_BASED_PROGRAM):
            MerchantScheduleProgram.remove_by_merchant_program(program)
    '''
        
    @classmethod
    @model_transactional(desc="publish_program")
    def publish_program(cls, program):
        program.completed_status = program_conf.PROGRAM_STATUS_PUBLISH
        program.published_datetime = datetime.now()
        program.put()
        
        merchant_acct = program.merchant_acct
        merchant_acct.update_published_program(program.to_configuration())
        
        create_schedule_program(merchant_acct, program)
        
    @classmethod
    @model_transactional(desc="archive_program")
    def archive_program(cls, program):
        program.archived = True
        program.archived_datetime = datetime.now()
        program.put()
        
        merchant_acct = program.merchant_acct
        merchant_acct.remove_program_from_published_program_configuration(program.key_in_str) 
        
        remove_schedule_program(program)
        
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
        
        program.put()
        
        if program.is_published:
            merchant_acct = program.merchant_acct
            merchant_acct.update_published_program(program.to_configuration())
            
            create_schedule_program(merchant_acct, program)
            
        
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
            merchant_acct = program.merchant_acct
            merchant_acct.remove_program_from_published_program_configuration(program.key_in_str)
            
            remove_schedule_program(program)
        
    def to_configuration(self):
        program_configuration = {
                                'merchant_acct_key'                 : self.parent_key,
                                'program_key'                       : self.key_in_str,
                                'label'                             : self.label,
                                'desc'                              : self.desc,
                                'reward_base'                       : self.reward_base,
                                'reward_format'                     : self.reward_format,
                                'giveaway_method'                   : self.giveaway_method,
                                'start_date'                        : self.start_date.strftime('%d-%m-%Y'),
                                'end_date'                          : self.end_date.strftime('%d-%m-%Y'),    
                                'program_settings'                  : self.program_settings,
                                'is_published'                      : self.is_published,  
                                'remarks'                           : self.remarks, 
                                }
        
        return program_configuration
    

class BasicRewardProgram(BaseProgram):
    
    @property
    def completed_progress_in_percentage(self):
        
        return program_conf.program_completed_progress_percentage(self.completed_status, self.loyalty_package)
    
    @property
    def completed_status_index(self):
        return program_conf.get_program_completed_status_index(self.completed_status)
    
        
    @classmethod
    def update_program_base_data(cls, program, label=None, reward_base=None, reward_format=None,  
                                 desc=None,start_date=None, end_date=None, modified_by=None, 
                                 loyalty_package=program_conf.LOYALTY_PACKAGE_LITE):
        
        modified_by_username = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        program_settings = program.program_settings or {}
        
        exclusivity_configuration = {
                                                    'tags'              : [],
                                                    'memberships'       : [],
                                                    'tier_memberships'  : [],
                                                    }
        
        program_settings['exclusivity'] = exclusivity_configuration
        program.label                   = label
        program.reward_base             = reward_base
        program.reward_format           = reward_format
        program.desc                    = desc
        program.start_date              = start_date
        program.end_date                = end_date
        program.modified_by             = modified_by.create_ndb_key()
        program.modified_by_username    = modified_by_username
        program.completed_status        = program_conf.PROGRAM_STATUS_PROGRAM_BASE 
        program.program_settings        = program_settings
        program.loyalty_package         = loyalty_package
        
        
        program.put()
        
        return program
    
    @classmethod
    def update_prorgram_reward_details_data(cls, program, 
                                            giveaway_method=None,
                                            giveaway_system_condition = None, 
                                            giveaway_system_condition_membership_key=None, 
                                            giveaway_system_condition_tier_membership_key=None,
                                            giveaway_system_condition_value=None,
                                            reward_scheme_configuration={}, modified_by=None,
                                            remarks=None):
        modified_by_username = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        if program.program_settings is None:
            program_settings = {
                            'scheme'                : [reward_scheme_configuration]
                            }
            
        else:
            program_settings = program.program_settings
            program_settings['scheme']              = reward_scheme_configuration
            
        if program_conf.REWARD_BASE_ON_GIVEAWAY == program.reward_base:  
            program.giveaway_method     = giveaway_method
            giveaway_system_settings    = program_settings.get('giveaway_system_settings')
            
            if giveaway_system_settings is None:        
                giveaway_system_settings = {
                                                    'giveaway_system_condition'         : giveaway_system_condition,
                                                    'giveaway_system_condition_value'   : giveaway_system_condition_value,
                                                }
            else:
                giveaway_system_settings['giveaway_system_condition']       = giveaway_system_condition
                giveaway_system_settings['giveaway_system_condition_value'] = giveaway_system_condition_value
                
            if is_not_empty(giveaway_system_condition_membership_key):
                giveaway_system_settings['giveaway_memberships'] = giveaway_system_condition_membership_key
            else:
                if giveaway_system_settings.get('giveaway_memberships'):
                    del giveaway_system_settings['giveaway_memberships']
            
            if is_not_empty(giveaway_system_condition_tier_membership_key):
                giveaway_system_settings['giveaway_tier_memberships'] = giveaway_system_condition_tier_membership_key
            else:
                if giveaway_system_settings.get('giveaway_tier_memberships'):
                    del giveaway_system_settings['giveaway_tier_memberships']
            
            logger.debug('######################## giveaway_system_settings=%s', giveaway_system_settings)
        
            program_settings['giveaway_system_settings'] = giveaway_system_settings    
        else:
            if program_settings.get('giveaway_system_settings'):
                del program_settings['giveaway_system_settings']
            
        if program_conf.REWARD_FORMAT_VOUCHER != program.reward_format:
            if program_settings.get('reward_items'):
                del program_settings['reward_items']
                        
        program.modified_by             = modified_by.create_ndb_key()
        program.modified_by_username    = modified_by_username
        program.completed_status        = program_conf.PROGRAM_STATUS_REWARD_SCHEME
        program.program_settings        = program_settings
        program.remarks                 = remarks
        
        logger.debug('program_settings=%s', program_settings)
        
        program.put()
        
        return program
    
    
    @classmethod
    def add_program_voucher(cls, program, voucher_configuration, modified_by=None):
        
        modified_by_username = None
        
        voucher_configuration_list = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        if program.program_settings is None:
            voucher_configuration_list  = []
            program_settings            = {}
            
        else:
            program_settings = program.program_settings
            voucher_configuration_list = program_settings.get('reward_items') or []
            
        
        voucher_configuration_list.append(voucher_configuration)
        program_settings['reward_items']    = voucher_configuration_list
        
        program.modified_by            = modified_by.create_ndb_key()
        program.modified_by_username   = modified_by_username
        program.program_settings       = program_settings
        
        program.put()
        
        return program
    
    @classmethod
    def add_program_tier_membership(cls, program, membership_configuration, modified_by=None):
        
        modified_by_username = None
        
        membership_configuration_list = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        if program.program_settings is None:
            membership_configuration_list  = []
            program_settings            = {}
            
        else:
            program_settings = program.program_settings
            membership_configuration_list = program_settings.get('tier_memberships') or []
            
        
        membership_configuration_list.append(membership_configuration)
        
        program_settings['tier_memberships']    = membership_configuration_list
        
        program.modified_by            = modified_by.create_ndb_key()
        program.modified_by_username   = modified_by_username
        program.program_settings       = program_settings
        
        
        program.put()
        
        return program
    
    @classmethod
    def add_program_membership(cls, program, membership_configuration, modified_by=None):
        
        modified_by_username = None
        
        membership_configuration_list = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        if program.program_settings is None:
            membership_configuration_list   = []
            program_settings                = {}
            
        else:
            program_settings = program.program_settings
            membership_configuration_list = program_settings.get('memberships') or []
            
        
        membership_configuration_list.append(membership_configuration)
        
        program_settings['memberships']    = membership_configuration_list
        
        program.modified_by            = modified_by.create_ndb_key()
        program.modified_by_username   = modified_by_username
        program.program_settings       = program_settings
        
        
        program.put()
        
        return program
    
    @property
    def reward_items(self):
        return self.program_settings.get('reward_items')
    
    @property
    def exclusivity_configuration(self):
        return self.program_settings.get('exclusivity')
    
    @classmethod
    def remove_program_voucher(cls, program, voucher_index, modified_by=None):
        modified_by_username = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        program_settings            = program.program_settings
        program_voucher_listing     = program_settings.get('reward_items')
        
        index = 0
        
        for voucher in program_voucher_listing:
            if voucher.get('voucher_index') == voucher_index:
                program_voucher_listing.pop(index)
                break
            
            index = index +1
    
        program_settings['reward_items']    = program_voucher_listing      
        program.program_settings            = program_settings
        program.modified_by                 = modified_by.create_ndb_key()
        program.modified_by_username        = modified_by_username
        program.put()
        
    @classmethod
    def remove_program_tier_membership(cls, program, membership_key, modified_by=None):
        modified_by_username = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        program_settings            = program.program_settings
        tier_membership_listing     = program_settings.get('tier_memberships')
        
        index = 0
        
        for membership in tier_membership_listing:
            if membership.get('membership_key') == membership_key:
                tier_membership_listing.pop(index)
                break
            
            index = index +1
    
        program_settings['tier_memberships']    = tier_membership_listing      
        program.program_settings                = program_settings
        program.modified_by                     = modified_by.create_ndb_key()
        program.modified_by_username            = modified_by_username
        program.put()    
    
    
    
class MerchantProgram(BasicRewardProgram):
    dict_properties                     = ['reward_base', 'giveaway_method', 'reward_format', 'completed_status', 'start_date', 'end_date', 'label','desc', 'program_settings', 
                                           'created_datetime', 'modified_datetime',  'enabled','completed_status','is_enabled', 'is_disabled', 'is_review_state', 
                                           'is_published', 'archived', 'is_reward_amount_required', 'completed_progress_in_percentage', 'completed_status_index',
                                           'exclusive_tags_list', 'exclusive_memberships_list', 'exclusive_tier_memberships_list',
                                           'is_recurring_scheme', 'limit_to_specific_day', 'specified_days_list',
                                           'limit_to_specific_date_of_month', 'specified_dates_of_month_list',
                                           'expiration_type', 'expiration_date', 'expiration_value', 'is_expiration_date_type',
                                           'giveaway_reward_when', 'giveaway_reward_advance_in_day',
                                           'giveaway_system_condition', 'giveaway_system_condition_memberships_list', 'giveaway_system_condition_tier_memberships_list',
                                           'remarks', 'loyalty_package', 'exclusive_promotion_codes_list',
                                           'created_by_username', 'modified_by_username']
    
    @property
    def giveaway_system_condition_memberships_list(self):
        if self.program_settings and self.program_settings.get('giveaway_system_settings'):
            
            giveaway_memberships = self.program_settings.get('giveaway_system_settings').get('giveaway_memberships')
            if is_not_empty(giveaway_memberships):
                if isinstance(giveaway_memberships, str):
                    return giveaway_memberships.split(',')
                else:
                    #check the value is value separated by comma
                    memberships_list = []
                    for m in giveaway_memberships:
                        memberships_list.extend(m.split(','))
                    return memberships_list
                    
    
    @property
    def giveaway_system_condition_tier_memberships_list(self):
        if self.program_settings and self.program_settings.get('giveaway_system_settings'):
            return self.program_settings.get('giveaway_system_settings').get('giveaway_tier_memberships')
    
    @staticmethod
    def create(merchant_acct, label=None, reward_base=None, reward_format=None, 
               desc=None, start_date=None, end_date=None, created_by=None,
               loyalty_package = program_conf.LOYALTY_PACKAGE_SCALE,
               ):
        
        created_by_username = None
        if is_not_empty(created_by):
            if isinstance(created_by, MerchantUser):
                created_by_username = created_by.username
        
        exclusivity_configuration = {
                                                    'tags'              : [],
                                                    'memberships'       : [],
                                                    'tier_memberships'  : [],
                                                    }
        
        program_settings = {
                            'exclusivity'               : exclusivity_configuration,
                            'scheme'                    : {
                                                            'is_recurring_scheme'   : True,
                                                            'limit_to_specific_day' : False,
                                                            'specified_days_list'   : [],
                                                        }
                            }
        
        
        
        merchant_program =  MerchantProgram(
                                        parent                              = merchant_acct.create_ndb_key(),
                                        label                               = label,
                                        reward_base                         = reward_base,
                                        reward_format                       = reward_format,
                                        desc                                = desc,
                                        start_date                          = start_date,
                                        end_date                            = end_date,
                                        created_by                          = created_by.create_ndb_key(),
                                        created_by_username                 = created_by_username,
                                        completed_status                    = program_conf.PROGRAM_STATUS_PROGRAM_BASE,
                                        program_settings                    = program_settings,
                                        loyalty_package                     = loyalty_package,
                                        )
        
        merchant_program.put()
        return merchant_program
    
    
    
    @property
    def merchant_acct(self):
        return MerchantAcct.fetch(self.key.parent().urlsafe())
    
      
    
    @staticmethod
    def list_by_merchant_account(merchant_acct):
        return MerchantProgram.query(ndb.AND(MerchantProgram.archived!=True), ancestor=merchant_acct.create_ndb_key()).fetch(limit=model_conf.MAX_FETCH_RECORD)
    
    @staticmethod
    def list_archived_by_merchant_account(merchant_acct):
        return MerchantProgram.query(ndb.AND(MerchantProgram.archived==True), ancestor=merchant_acct.create_ndb_key()).fetch(limit=model_conf.MAX_FETCH_RECORD)

class MerchantTierRewardProgram(MerchantProgram):
    '''
    Merchant acct as ancestor. Used for schedule program like birthday or push reward.
    '''
    
    is_tier_recycle                     = ndb.BooleanProperty(required=True, default=True)
    max_unlock_tier_count_per_trax      = ndb.IntegerProperty(required=False, default=999)
    is_show_progress                    = ndb.BooleanProperty(required=True, default=True)
    
    dict_properties                     = ['completed_status', 'start_date', 'end_date', 'label', 'desc', 'program_settings', 'reward_format',
                                           'created_datetime', 'modified_datetime',  'enabled','completed_status','is_enabled', 'is_disabled', 'is_review_state', 
                                           'is_published', 'archived', 'completed_progress_in_percentage', 'completed_status_index',
                                           'exclusive_tags_list', 'exclusive_memberships_list', 'exclusive_tier_memberships_list',
                                           'is_tier_recycle', 'is_show_progress', 'max_unlock_tier_count_per_trax',
                                           'created_by_username', 'modified_by_username', 'loyalty_package']
    
    @property
    def completed_progress_in_percentage(self):
        return program_conf.tier_reward_program_completed_progress_percentage(self.completed_status)
    
    @property
    def completed_status_index(self):
        return program_conf.get_tier_reward_program_completed_status_index(self.completed_status)
    
    @property
    def is_review_state(self):
        return program_conf.is_existing_tier_reward_program_status_final_state(self.completed_status)
    
    @property
    def program_tiers(self):
        tier_settings_list = self.program_settings.get('tiers')
        
        logger.debug('tier_settings_list=%s', tier_settings_list)
        
        return sort_dict_list(tier_settings_list, 'unlock_tier_condition_value')
        
    
    @property
    def program_rewards(self):
        tier_settings_list = self.program_settings.get('tiers') or []
        reward_settings_list = []
        for tier_setting in tier_settings_list:
            reward_items = tier_setting.get('reward_items')
            if reward_items:
                for reward_setting in reward_items:
                    reward_settings_list.append(reward_setting)
        
        return reward_settings_list
    
    @staticmethod
    @model_transactional(desc="publish_program")
    def publish_program(program):
        program.completed_status = program_conf.PROGRAM_STATUS_PUBLISH
        program.published_datetime = datetime.now()
        program.put()
        
        merchant_acct = program.merchant_acct
        merchant_acct.update_published_program(program.to_configuration())
        
        create_schedule_program(merchant_acct, program)
    
    @staticmethod
    @model_transactional(desc="archive_program")
    def archive_program(program):
        program.archived = True
        program.archived_datetime = datetime.now()
        program.put()
        
        merchant_acct = program.merchant_acct
        #merchant_acct.remove_tier_program_from_published_tier_program_configuration(program.key_in_str)
        merchant_acct.remove_program_from_published_program_configuration(program.key_in_str) 
        
        remove_schedule_program(program)
    
    @staticmethod
    @model_transactional(desc="enable program")
    def enable(program, modified_by=None):
        program.enabled = True
        
        modified_by_username = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        program.modified_by            = modified_by.create_ndb_key()
        program.modified_by_username   = modified_by_username
        
        program.put()
        
        if program.is_published:
            merchant_acct = program.merchant_acct
            #merchant_acct.update_published_tier_program(program.to_configuration())
            merchant_acct.update_published_program(program.to_configuration())
            
            create_schedule_program(merchant_acct, program)
            
        
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
            merchant_acct = program.merchant_acct
            #merchant_acct.remove_tier_program_from_published_tier_program_configuration(program.key_in_str)
            merchant_acct.remove_program_from_published_program_configuration(program.key_in_str)
            
            remove_schedule_program(program)
    
    @staticmethod
    def create(merchant_acct, label=None, is_tier_recycle=True, is_show_progress=True, reward_format=None,
               desc=None, start_date=None, end_date=None, created_by=None):
        
        created_by_username = None
        if is_not_empty(created_by):
            if isinstance(created_by, MerchantUser):
                created_by_username = created_by.username
        
        exclusivity_configuration = {
                                                    'tags'              : [],
                                                    'memberships'       : [],
                                                    'tier_memberships'  : [],
                                                    }
        
        program_settings = {
                            'exclusivity'               : exclusivity_configuration,
                            'giveaway_methd'            : program_conf.PROGRAM_REWARD_GIVEAWAY_METHOD_SYSTEM,
                            }
        
        
        
        tier_reward_program =  MerchantTierRewardProgram(
                                        parent                              = merchant_acct.create_ndb_key(),
                                        reward_base                         = program_conf.REWARD_BASE_ON_TIER,
                                        reward_format                       = reward_format,
                                        label                               = label,
                                        desc                                = desc,
                                        is_tier_recycle                     = is_tier_recycle,
                                        is_show_progress                    = is_show_progress,
                                        start_date                          = start_date,
                                        end_date                            = end_date,
                                        created_by                          = created_by.create_ndb_key(),
                                        created_by_username                 = created_by_username,
                                        completed_status                    = program_conf.PROGRAM_STATUS_PROGRAM_BASE,
                                        program_settings                    = program_settings,
                                        )
        
        tier_reward_program.put()
        
        return tier_reward_program
    
    @staticmethod
    def update(program, label=None, is_tier_recycle=True, is_show_progress=True, reward_format=None,
               desc=None, start_date=None, end_date=None, modified_by=None):
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                program.modified_by                          = modified_by.create_ndb_key()
                program.modified_by_username                 = modified_by.username
        
        program.reward_format                       = reward_format
        program.label                               = label
        program.desc                                = desc
        program.is_tier_recycle                     = is_tier_recycle
        program.is_show_progress                    = is_show_progress
        program.start_date                          = start_date
        program.end_date                            = end_date
        program.program_settings['giveaway_methd']  = program_conf.PROGRAM_REWARD_GIVEAWAY_METHOD_SYSTEM
        program.put()
        
        return program
    
    @staticmethod
    def remove_program_reward(program, reward_index, modified_by=None):
        program_tier_settings_list  = program.program_settings['tiers']
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                
                program.modified_by             = modified_by.create_ndb_key()
                program.modified_by_username    = modified_by.username
        
        if program_tier_settings_list:
            latest_tier_settings_list = []
            
            for tier_setting in program_tier_settings_list:
                reward_settings_list        = tier_setting.get('reward_items')
                if reward_settings_list:
                    latest_reward_setting_list  = []
                    
                    for reward_setting in reward_settings_list:
                        if reward_setting.get('reward_index') != reward_index:
                            latest_reward_setting_list.append(reward_setting)
                    
                    tier_setting['reward_items'] = latest_reward_setting_list
                
                
                latest_tier_settings_list.append(tier_setting)
        
        program.program_settings['tiers'] =  latest_tier_settings_list   
        program.put()
    
    @staticmethod
    def add_program_reward(program, tier_index=None, merchant_voucher_key=None, voucher_amount=1, use_online=True, use_in_store=True, 
                           effective_type=None, effective_value=None, effective_date=None,
                           expiration_type=None, expiration_value=None, expiration_date=None,
                           modified_by=None
                           ):
        program_tier_settings_list  = program.program_settings['tiers']
        reward_index                = random_string(12)
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                
                program.modified_by             = modified_by.create_ndb_key()
                program.modified_by_username    = modified_by.username
        
        if program_tier_settings_list:
            latest_tier_settings_list = []
            
            for tier_setting in program_tier_settings_list:
                if tier_setting.get('tier_index') == tier_index:
                    reward_settings_list = tier_setting.get('reward_items')
                    if not reward_settings_list:
                        reward_settings_list = []
                    
                    reward_settings_list.append({
                                                'tier_index'        : tier_index,
                                                'reward_index'      : reward_index,
                                                'voucher_key'       : merchant_voucher_key,
                                                'voucher_amount'    : voucher_amount,
                                                'use_online'        : use_online,
                                                'use_in_store'      : use_in_store,
                                                'effective_type'    : effective_type,
                                                'effective_value'   : effective_value,
                                                'effective_date'    : effective_date,
                                                'expiration_type'   : expiration_type,
                                                'expiration_value'  : expiration_value,
                                                'expiration_date'   : expiration_date,
                                                })
            
                    tier_setting['reward_items'] = reward_settings_list
                    
                latest_tier_settings_list.append(tier_setting)
                
                    
        #program.completed_status           = program_conf.PROGRAM_STATUS_DEFINE_REWARD
        program.program_settings['tiers'] =  latest_tier_settings_list   
        program.put()
        
        
        
        
    @staticmethod
    def add_program_tier(program, tier_label=None, unlock_tier_message=None, unlock_tier_condition=None, unlock_tier_condition_value=None, modified_by=None):
        tier_index = random_string(12)
        tier_settings = {
                        'tier_index'                    : tier_index,
                        'tier_label'                    : tier_label,
                        'unlock_tier_message'           : unlock_tier_message,
                        'unlock_tier_condition'         : unlock_tier_condition,
                        'unlock_tier_condition_value'   : unlock_tier_condition_value,
                        }
        
        program_settings = program.program_settings
        
        tier_list = program_settings.get('tiers')
        if tier_list:
            tier_list.append(tier_settings)
        else:
            tier_list = [tier_settings]
            
        modified_by_username = None
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username    
            
        program_settings['tiers']       = tier_list
        program.program_settings        = program_settings
        
        if modified_by:
            program.modified_by             = modified_by.create_ndb_key()
            program.modified_by_username    = modified_by_username
            
        program.put()
        
    @staticmethod
    def update_program_tier_settings(program, program_tier_settings_list, modified_by=None):
        modified_by_username = None
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username    
        
        existing_program_tier_settings_list = program.program_settings.get('tiers') or []
        
        for new_tier_settings in program_tier_settings_list:
            logger.debug('new_tier_settings=%s', new_tier_settings);
            for existing_tier_setting in existing_program_tier_settings_list:
                logger.debug('existing_tier_setting=%s', existing_tier_setting);
                if existing_tier_setting.get('reward_items'):
                    if existing_tier_setting.get('tier_index') == new_tier_settings.get('tier_index'):
                        new_tier_settings['reward_items'] = existing_tier_setting.get('reward_items')
                        break
                else:
                    continue
                     
        
        program.program_settings['tiers']  = program_tier_settings_list
        program.completed_status           = program_conf.PROGRAM_STATUS_DEFINE_TIER
        if modified_by:
            program.modified_by             = modified_by.create_ndb_key()
            program.modified_by_username    = modified_by_username
            
        program.put() 
    
    @staticmethod    
    def update_program_reward_settings(program, modified_by=None):
        modified_by_username = None
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username    
        
        program.completed_status           = program_conf.PROGRAM_STATUS_DEFINE_REWARD
        if modified_by:
            program.modified_by             = modified_by.create_ndb_key()
            program.modified_by_username    = modified_by_username
            
        program.put()        
    
    @staticmethod
    def remove_tier(program, tier_index, modified_by=None):
        
        program_settings = program.program_settings
        
        tier_list = program_settings.get('tiers')
        if tier_list:
            index_no = 0
            for tier_setting in tier_list:
                if tier_setting.get('tier_index') == tier_index:
                    del tier_list[index_no]
                    break
            
                index_no+=1
        
        modified_by_username = None
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
                
        program_settings['tiers']       = tier_list
        program.program_settings        = program_settings
        
        if modified_by:
            program.modified_by             = modified_by.create_ndb_key()
            program.modified_by_username    = modified_by_username
            
        program.put()
    
    @staticmethod
    def list_by_merchant_acct(merchant_acct):
        result =  MerchantTierRewardProgram.query(ancestor=merchant_acct.create_ndb_key()).fetch(limit=conf.MAX_FETCH_RECORD)
        if result:
            return sort_list(result, 'created_datetime', reverse_order=True)
        else:
            return []
    
class MerchantScheduleProgram(BaseNModel, DictModel):
    '''
    Merchant acct as ancestor. Used for schedule program like birthday or push reward.
    '''
    merchant_program                    = ndb.KeyProperty(name="merchant_program", kind=MerchantProgram)
    program_configuration               = ndb.JsonProperty(required=True)
    schedule_type                       = ndb.StringProperty(required=True, choices=set(program_conf.PROGRAM_SCHEDULE_TYPE_GROUP))
    start_date                          = ndb.DateProperty(required=True)
    end_date                            = ndb.DateProperty(required=True)
    created_datetime                    = ndb.DateTimeProperty(required=True, auto_now_add=True)
    
    dict_properties                     = ['program_configuration', 'schedule_type', 'start_date', 'end_date']
    
    
    @property
    def merchant_acct_key(self):
        return self.parent_key
    
    @property
    def merchant_program_entity(self):
        return MerchantProgram.fetch(self.merchant_program.urlsafe())
    
    @property
    def merchant_program_desc(self):
        return self.merchant_program_entity.desc
    
    @staticmethod
    def __list_by_schedule_type(schedule_type):
        return MerchantScheduleProgram.query(MerchantScheduleProgram.schedule_type==schedule_type).fetch(limit=model_conf.MAX_FETCH_RECORD)
    
    @staticmethod
    def list_daily_schedule_program():
        return MerchantScheduleProgram.__list_by_schedule_type(program_conf.PROGRAM_SCHEDULE_TYPE_DAILY)
    
    @staticmethod
    def list_beginning_of_month_schedule_program():
        return MerchantScheduleProgram.__list_by_schedule_type(program_conf.PROGRAM_SCHEDULE_TYPE_MONTH_START)
    
    @staticmethod
    def list_beginning_of_week_schedule_program():
        return MerchantScheduleProgram.__list_by_schedule_type(program_conf.PROGRAM_SCHEDULE_TYPE_MONDAY)
    
    @staticmethod
    def list_friday_schedule_program():
        return MerchantScheduleProgram.__list_by_schedule_type(program_conf.PROGRAM_SCHEDULE_TYPE_FRIDAY)
    
    @staticmethod
    def get_by_merchant_program(merchant_program):
        return MerchantScheduleProgram.query(MerchantScheduleProgram.merchant_program == merchant_program.create_ndb_key()).get()
    
    @staticmethod
    def __create(merchant_acct, schedule_type, merchant_program):
        schedule_program    = MerchantScheduleProgram(
                                parent                  = merchant_acct.create_ndb_key(),
                                merchant_program        = merchant_program.create_ndb_key(),
                                schedule_type           = schedule_type,
                                program_configuration   = merchant_program.to_configuration(),
                                start_date              = merchant_program.start_date,
                                end_date                = merchant_program.end_date,
                                
                            )
        
        schedule_program.put()
        
        return schedule_program
        
    @staticmethod
    def create_daily_schedule_program(merchant_acct, merchant_program):
        return MerchantScheduleProgram.__create(merchant_acct, program_conf.PROGRAM_SCHEDULE_TYPE_DAILY, merchant_program)
    
    @staticmethod
    def create_first_day_of_month_schedule_program(merchant_acct, merchant_program):
        return MerchantScheduleProgram.__create(merchant_acct, program_conf.PROGRAM_SCHEDULE_TYPE_MONTH_START, merchant_program)
    
    @staticmethod
    def create_every_monday_schedule_program(merchant_acct, merchant_program):
        return MerchantScheduleProgram.__create(merchant_acct, program_conf.PROGRAM_SCHEDULE_TYPE_MONDAY, merchant_program)
    
    @staticmethod
    def create_every_friday_schedule_program(merchant_acct, merchant_program):
        return MerchantScheduleProgram.__create(merchant_acct, program_conf.PROGRAM_SCHEDULE_TYPE_FRIDAY, merchant_program)
    
    @staticmethod
    def create_weekend_schedule_program(merchant_acct, merchant_program):
        return MerchantScheduleProgram.__create(merchant_acct, program_conf.PROGRAM_SCHEDULE_TYPE_WEEKEND, merchant_program)    
        
    @staticmethod
    def remove_by_merchant_program(merchant_program):
        schedule_program = MerchantScheduleProgram.get_by_merchant_program(merchant_program)
        if schedule_program:
            logger.debug('Found schedule program')
            schedule_program.delete()
        else:
            logger.warn('Schedule program not found')
        
    


           


