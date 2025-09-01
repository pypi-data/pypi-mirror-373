'''
Created on 15 May 2020

@author: jacklok
'''

from google.cloud import ndb
from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel, FullTextSearchable
from trexmodel.models.datastore.system_models import SentEmail
from trexmodel.models.datastore.user_models import UserMin
import trexmodel.conf as model_conf
from trexlib.utils.security_util import generate_user_id, hash_password
from trexlib.utils.string_util import random_number, is_empty, is_not_empty,\
    split_by_length, random_string
import logging
from datetime import datetime, timedelta
from trexconf import conf, program_conf
from trexmodel.models.datastore.system_models import Tagging
from trexmodel.models.datastore.model_decorators import model_transactional
from trexmodel.program_conf import LOYALTY_PACKAGE_LITE, LOYALTY_PRODUCT,\
    POS_PACKAGE_LITE
import pytz
from trexlib.utils.common.cache_util import deleteFromCache, getFromCache,\
    setCache

#logger = logging.getLogger('model')
logger = logging.getLogger('target_debug')

class BusinessEntity(BaseNModel, DictModel):
    company_name                = ndb.StringProperty(required=False)
    brand_name                  = ndb.StringProperty(required=False)
    business_reg_no             = ndb.StringProperty(required=False)
    
class MerchantMin(BusinessEntity, FullTextSearchable):
    
    contact_name                = ndb.StringProperty(required=False)
    address                     = ndb.StringProperty(required=False)
    office_phone                = ndb.StringProperty(required=False)
    mobile_phone                = ndb.StringProperty(required=False)
    fax_phone                   = ndb.StringProperty(required=False)
    email                       = ndb.StringProperty(required=False)
    website                     = ndb.StringProperty(required=False)
    country                     = ndb.StringProperty(required=False, default='my')
    status                      = ndb.StringProperty(required=False)
    
    modified_datetime           = ndb.DateTimeProperty(required=True, auto_now=True)
    registered_datetime         = ndb.DateTimeProperty(required=True, auto_now_add=True)
    plan_start_date             = ndb.DateProperty(required=True)
    plan_end_date               = ndb.DateProperty(required=True)
    
    fulltextsearch_field_name   = 'company_name'
    
    
    @property
    def gmt_hour(self):
        return conf.DEFAULT_GMT_HOURS
    

class MerchantAcct(MerchantMin):
    account_code                            = ndb.StringProperty(required=False)
    logo_public_url                         = ndb.StringProperty(required=False)
    logo_storage_filename                   = ndb.StringProperty(required=False)
    dashboard_stat_figure                   = ndb.JsonProperty()
    currency_code                           = ndb.StringProperty(required=False, default='MYR')
    locale                                  = ndb.StringProperty(required=False, default='en_MY')
    timezone                                = ndb.StringProperty(required=False, default='Asia/Kuala_Lumpur')
    api_key                                 = ndb.StringProperty(required=False)
    
    account_plan                            = ndb.JsonProperty()
    setup_progress                          = ndb.JsonProperty()
    outlet_count                            = ndb.IntegerProperty(default=0)
    
    industry                                = ndb.StringProperty(required=False, default='fb')
    
    published_program_configuration                 = ndb.JsonProperty()
    published_referral_program_configuration        = ndb.JsonProperty()
    published_voucher_configuration                 = ndb.JsonProperty()
    published_redemption_catalogue_configuration    = ndb.JsonProperty()
    partner_redemption_catalogue_configuration      = ndb.JsonProperty()
    published_news_configuration                    = ndb.JsonProperty()
    published_tier_program_configuration            = ndb.JsonProperty()
    
    approved_partner_merchant_configuration         = ndb.JsonProperty()
    partner_merchant_history_configuration          = ndb.JsonProperty()
    
    membership_configuration                        = ndb.JsonProperty()
    tier_membership_configuration                   = ndb.JsonProperty()
    
    reward_naming_configuration                     = ndb.JsonProperty()
    
    prepaid_configuration                           = ndb.JsonProperty()
    
    lucky_draw_configuration                        = ndb.JsonProperty(required=False)
    
    product_modifier_configuration                  = ndb.JsonProperty()
    
    program_settings                                = ndb.JsonProperty(default={
                                                                                'days_of_return_policy'                 : 3,
                                                                                'days_of_repeat_purchase_measurement'   : 7,
                                                                                'membership_renew_advance_day'          : 7,
                                                                                'membership_renew_late_day'             : 30,
                                                                                'rating_review'                         : False,
                                                                                }
                                                                        )
    
    stat_figure_update_interval_in_minutes          = conf.MERCHANT_STAT_FIGURE_UPDATE_INTERVAL_IN_MINUTES
    stat_figure_update_datetime_format              = '%d-%m-%Y %H:%M:%S'
    
    dict_properties = ['company_name', 'brand_name', 'contact_name', 'business_reg_no', 'mobile_phone', 
                       'office_phone', 'fax_phone', 'email', 'account_code', 'country', 'industry',
                       'registered_datetime', 'modified_datetime', 'plan_start_date', 'plan_end_date', 'currency_code', 
                       'timezone', 'effective_referral_program_count', 'gmt_hour',
                       'published_program_configuration', 'published_tier_program_configuration', 'published_referral_program_configuration', 
                       'published_voucher_configuration', 'published_news_configuration', 'membership_configuration', 
                       'tier_membership_configuration', 'prepaid_configuration', 'lucky_draw_configuration', 'product_modifier_configuration',
                       'dashboard_stat_figure', 'program_settings', 'is_tier_membership_configured', 'website', 
                       'product_package', 'loyalty_package','pos_package', 'account_plan','outlet_count', 'outlet_limit',
                       'published_redemption_catalogue_configuration', 'partner_redemption_catalogue_configuration',
                       'approved_partner_merchant_configuration', 'partner_merchant_history_configuration',
                       'logo_public_url'
                       ]
    
    
    @property
    def gmt_hour(self):
        if self.timezone:
            now             = datetime.utcnow()
            timezone        = pytz.timezone(self.timezone)
            #timezone_time   = now.astimezone(self.timezone)
            return timezone.utcoffset(now).total_seconds() / 3600
        return conf.DEFAULT_GMT_HOURS
    
    def upload_logo(self, uploading_file, bucket, logo_file_type=None):
        file_prefix                         = random_string(8)
        logo_file_storage_filename          = 'merchant/'+self.key_in_str+'/logo/'+file_prefix+'-'+uploading_file.filename
        blob                                = bucket.blob(logo_file_storage_filename)
        
        logger.debug('logo_file_storage_filename=%s', logo_file_storage_filename)
        
        blob.upload_from_string(
                uploading_file.read(),
                content_type=uploading_file.content_type
            )
        
        uploaded_url        = blob.public_url
        
        logger.debug('uploaded_url=%s', uploaded_url)
        logger.debug('logo_file_type=%s', logo_file_type)
        
        if is_not_empty(self.logo_storage_filename):
            old_logo_blob = bucket.get_blob(self.logo_storage_filename) 
            if old_logo_blob:
                old_logo_blob.delete()
        
        self.logo_public_url        = uploaded_url
        self.logo_storage_filename  = logo_file_storage_filename 
        self.put()
        deleteFromCache(self.key_in_str)
    
    def update_setup_progress(self, setup_step):
        if self.setup_progress is None:
            self.setup_progress = {
                }
        elif self.setup_progress.get(setup_step) is None:
            self.setup_progress[setup_step] = True
    
    def to_login_dict(self):
        return {
                'account_code'      : self.account_code,
                'plan_end_date'     : self.plan_end_date,
                'currency_code'     : self.currency_code,
                'country'           : self.country,
                'account_plan'      : self.account_plan,
                'gmt_hour'          : self.gmt_hour,
                'account_plan'      : self.account_plan,
                }
        
    @property
    def product_package(self):
        if self.account_plan:
            if self.account_plan.get('product_package'):
                return self.account_plan.get('product_package')
        
        return [LOYALTY_PRODUCT]
    
    @property
    def loyalty_package(self):
        if self.account_plan:
            if self.account_plan.get('loyalty_package'):
                return self.account_plan.get('loyalty_package')
        
        return LOYALTY_PACKAGE_LITE
    
    @property
    def pos_package(self):
        if self.account_plan:
            if self.account_plan.get('pos_package'):
                return self.account_plan.get('pos_package')
        
        return POS_PACKAGE_LITE
    
    @property
    def effective_referral_program_count(self):
        if self.published_referral_program_configuration:
            program_count = self.published_referral_program_configuration.get('count',0)
            if program_count>0:
                check_effective_count = 0
                program_list = self.published_referral_program_configuration.get('programs');
                today_date = datetime.today()
                for program_details in program_list:
                    start_date_str = program_details.get('start_date')
                    start_date = datetime.strptime(start_date_str, '%d-%m-%Y')
                    
                    end_date_str = program_details.get('end_date')
                    end_date = datetime.strptime(end_date_str, '%d-%m-%Y')
                    
                    if start_date<=today_date and today_date<=end_date:
                        check_effective_count+=1
                
                return check_effective_count
                    
            else:
                return program_count
                
        return 0
    
    @property
    def outlet_limit(self):
        if self.account_plan:
            if self.account_plan.get('outlet_limit'):
                return self.account_plan.get('outlet_limit')
        
        return 1
    
    @property
    def program_configuration_list(self):
        if is_not_empty(self.published_program_configuration):
            return  self.published_program_configuration.get('programs')
        else:
            return []
    
    
    @property
    def is_tier_membership_configured(self):
        return is_not_empty(self.tier_membership_configuration)
    
    @property
    def image_default_base_url(self):
        return program_conf.IMAGE_BASE_URL
    
    @property
    def days_of_return_policy(self):
        return self.program_settings.get('days_of_return_policy') or MerchantAcct.default_program_settings().get('days_of_return_policy')
    
    @property
    def days_of_repeat_purchase_measurement(self):
        return self.program_settings.get('days_of_repeat_purchase_measurement') or MerchantAcct.default_program_settings().get('days_of_repeat_purchase_measurement')
    
    @property
    def membership_renew_advance_day(self):
        return self.program_settings.get('membership_renew_advance_day') or MerchantAcct.default_program_settings().get('membership_renew_advance_day')
    
    @property
    def membership_renew_late_day(self):
        return self.program_settings.get('membership_renew_late_day') or MerchantAcct.default_program_settings().get('membership_renew_late_day')
    
    
    
    @property
    def lucky_draw_program_count(self):
        if self.lucky_draw_configuration:
            if self.lucky_draw_configuration.get('count'):
                return self.lucky_draw_configuration.get('count')
        return 0
    
    @property
    def lucky_draw_ticket_is_recurring_scheme(self):
        if self.lucky_draw_configuration.get('settings')  and self.lucky_draw_configuration.get('settings').get('is_recurring_scheme'):
            return self.lucky_draw_configuration.get('settings').get('is_recurring_scheme')
        else:
            return False
            
    @property
    def lucky_draw_ticket_spending_currency(self):
        if self.lucky_draw_configuration.get('settings') and self.lucky_draw_configuration.get('settings').get('spending_currency'):
            return self.lucky_draw_configuration.get('settings').get('spending_currency')
        else:
            return 0
    
    @property
    def lucky_draw_ticket_limit_type(self):
        if self.lucky_draw_configuration.get('settings'):
            return self.lucky_draw_configuration.get('settings').get('ticket_limit_type') or program_conf.REWARD_LIMIT_TYPE_NO_LIMIT
        else:
            return program_conf.REWARD_LIMIT_TYPE_NO_LIMIT
            
    
    @property
    def lucky_draw_ticket_limit_amount(self):
        if self.lucky_draw_configuration.get('settings'):
            return self.lucky_draw_configuration.get('settings').get('ticket_limit_amount')
        
        return 0
    
    @property
    def lucky_draw_ticket_expiry_date_length_in_day(self):
        if self.lucky_draw_configuration.get('settings'):
            return self.lucky_draw_configuration.get('settings').get('ticket_expiry_date_length_in_day')
        
        return 0
    
    @property
    def lucky_draw_ticket_image_url(self):
        if self.lucky_draw_configuration.get('settings'):
            return self.lucky_draw_configuration['settings']['ticket_image_url']
    
    @property
    def referrer_promote_title(self):
        if is_not_empty(self.program_settings):
            if self.program_settings.get('referral_program'):
                return self.program_settings.get('referral_program').get('referrer_promote_title', '')
        return ''
        
    @property
    def referee_promote_title(self):
        if is_not_empty(self.program_settings):
            if self.program_settings.get('referral_program'):
                return self.program_settings.get('referral_program').get('referee_promote_title', '')      
        return ''
        
    @property
    def referrer_promote_desc(self):
        if is_not_empty(self.program_settings):
            if self.program_settings.get('referral_program'):
                return self.program_settings.get('referral_program').get('referrer_promote_desc', '')
        return ''
            
    @property
    def referee_promote_desc(self):
        if is_not_empty(self.program_settings):
            if self.program_settings.get('referral_program'):
                return self.program_settings.get('referral_program').get('referee_promote_desc', '')            
        return ''
        
    @property
    def referrer_promote_image(self):
        if is_not_empty(self.program_settings):
            if self.program_settings.get('referral_program'):
                return self.program_settings.get('referral_program').get('referrer_promote_image')
            
    @property
    def referee_promote_image(self):
        if is_not_empty(self.program_settings):
            if self.program_settings.get('referral_program'):
                return self.program_settings.get('referral_program').get('referee_promote_image')        
        
    
    @property
    def is_rating_review_enabled(self):
        return self.program_settings.get('rating_review', False)
    
    @staticmethod
    def default_program_settings():
        return {
                'days_of_return_policy'                 : 3,
                'days_of_repeat_purchase_measurement'   : 7,
                'membership_renew_advance_day'          : 7,
                'membership_renew_late_day'             : 30,
                'rating_review'                         : False,
                }
    
    def update_referrer_program_promote_text(self, 
                                             promote_title=None, 
                                             promote_desc=None,
                                             modified_by=None):
        modified_by_username = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        if is_empty(self.program_settings):
            self.program_settings = {
                                    'referral_program':{}
                                    }
        else:
            if is_empty(self.program_settings.get('referral_program')):
                self.program_settings['referral_program'] = {}
        
        self.modified_by            = modified_by.create_ndb_key()
        self.modified_by_username   = modified_by_username
            
        self.program_settings['referral_program']['referrer_promote_title'] =  promote_title
        self.program_settings['referral_program']['referrer_promote_desc']  =  promote_desc
        self.put() 
        deleteFromCache(self.key_in_str)
        
    def update_referee_program_promote_text(self, 
                                             promote_title=None, 
                                             promote_desc=None, 
                                             modified_by=None):
        modified_by_username = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        if is_empty(self.program_settings):
            self.program_settings = {
                                    'referral_program':{}
                                    }
        else:
            if is_empty(self.program_settings.get('referral_program')):
                self.program_settings['referral_program'] = {}
        
        self.modified_by            = modified_by.create_ndb_key()
        self.modified_by_username   = modified_by_username
            
        self.program_settings['referral_program']['referee_promote_title'] =  promote_title
        self.program_settings['referral_program']['referee_promote_desc']  =  promote_desc
        self.put()  
        deleteFromCache(self.key_in_str)     
        
    def upload_referrer_program_promote_image(self, image_public_url=None, image_storage_filename=None, modified_by=None):
        
        modified_by_username = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        if is_empty(self.program_settings):
            self.program_settings = {
                                    'referral_program':{}
                                    }
        else:
            if is_empty(self.program_settings.get('referral_program')):
                self.program_settings['referral_program'] = {}
        
        self.program_settings['referral_program']['referrer_promote_image']             = image_public_url
        self.program_settings['referral_program']['referrer_promote_image_filename']    = image_storage_filename
        
        self.modified_by            = modified_by.create_ndb_key()
        self.modified_by_username   = modified_by_username
        
        self.put()
        deleteFromCache(self.key_in_str)
        
    def upload_referee_program_promote_image(self, image_public_url=None, image_storage_filename=None, modified_by=None):
        
        modified_by_username = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        if is_empty(self.program_settings):
            self.program_settings = {
                                    'referral_program':{}
                                    }
        else:
            if is_empty(self.program_settings.get('referral_program')):
                self.program_settings['referral_program'] = {}
        
        self.program_settings['referral_program']['referee_promote_image']          = image_public_url
        self.program_settings['referral_program']['referee_promote_image_filename'] = image_storage_filename
        
        self.modified_by            = modified_by.create_ndb_key()
        self.modified_by_username   = modified_by_username
        
        self.put()      
        deleteFromCache(self.key_in_str)  
    
    @staticmethod
    def update_details(merchant_acct, company_name=None, brand_name=None, business_reg_no=None, contact_name=None, 
                       email=None, mobile_phone=None, office_phone=None, currency_code=None, industry='fb',
                       country=None, timezone=None, website=None):
        
        
        
        merchant_acct.company_name      = company_name
        merchant_acct.brand_name        = brand_name
        merchant_acct.business_reg_no   = business_reg_no
        merchant_acct.contact_name      = contact_name
        merchant_acct.email             = email
        merchant_acct.mobile_phone      = mobile_phone
        merchant_acct.office_phone      = office_phone
        merchant_acct.currency_code     = currency_code
        merchant_acct.country           = country
        merchant_acct.timezone          = timezone
        merchant_acct.website           = website
        merchant_acct.industry          = industry
        
        merchant_acct.put()
        
        deleteFromCache(merchant_acct.key_in_str)
    
    @staticmethod
    def format_account_code(account_code):
        if is_not_empty(account_code):
            if len(account_code) == 16:
                account_code = '-'.join(split_by_length(account_code,4))
        return account_code    
    
    @staticmethod
    def search_merchant_account(company_name=None, account_code=None,
                                 offset=0, start_cursor=None, limit=model_conf.MAX_FETCH_RECORD):
        
        search_text_list = None
        query = MerchantAcct.query()
        
        if is_not_empty(company_name):
            search_text_list = company_name.split(' ')
            
        elif is_not_empty(account_code):
            query = query.filter(MerchantAcct.account_code==account_code)
            
        
        
        total_count                         = MerchantAcct.full_text_count(search_text_list, query, conf.MAX_FETCH_RECORD_FULL_TEXT_SEARCH)
        
        (search_results, next_cursor)       = MerchantAcct.full_text_search(search_text_list, query, offset=offset, 
                                                                   start_cursor=start_cursor, return_with_cursor=True, 
                                                                   limit=limit)
        
        return (search_results, total_count, next_cursor)
    
    @property
    def manual_giveaway_reward_program_list(self):
        published_program_configuration = self.published_program_configuration
        program_list = []
        
        for program in published_program_configuration.get('programs'):
            if program.get('reward_base') == program_conf.REWARD_BASE_ON_GIVEAWAY:
                if program.get('giveaway_method') == program_conf.PROGRAM_REWARD_GIVEAWAY_METHOD_MANUAL:
                    program_list.append(program)
        
        
        return program_list
    
    def update_api_key(self):
        api_key = random_string(24)
        logger.debug('api_key=%s', api_key)
        self.api_key = api_key
        self.put()
        deleteFromCache(self.key_in_str)
        
        return api_key
    
    def flush_dirty_program_configuration(self):
        if self.published_program_configuration and len(self.published_program_configuration)>0:
            existing_programs_list  = self.published_program_configuration.get('programs')
            new_programs_list       = []
            for p in existing_programs_list:
                try:
                    program = ndb.Key(urlsafe=p.get('program_key')).get()
                    if program.archived is False:
                        new_programs_list.append(p)
                except:
                    pass
            
            self.published_program_configuration['programs']    = new_programs_list
            self.published_program_configuration['count']       = len(new_programs_list)
        else:
            self.published_program_configuration = {'programs':[], 'count':0}
            
        self.put()
        
    
    def flush_dirty_membership_configuration(self):    
        if self.membership_configuration and len(self.membership_configuration.get('memberships'))>0:
            existing_memberships_list  = self.membership_configuration.get('memberships')
            new_memberships_list       = []
            for p in existing_memberships_list:
                try:
                    membership = ndb.Key(urlsafe=p.get('membership_key')).get()
                    if membership.archived is False:
                        new_memberships_list.append(p)
                except:
                    pass
            
            self.membership_configuration['memberships'] = new_memberships_list
            self.membership_configuration['count']       = len(new_memberships_list)
            
        else:
            self.membership_configuration = {'memberships':[], 'count':0}
        
        self.put()
        
    def flush_dirty_tier_membership_configuration(self):    
        if self.tier_membership_configuration and len(self.tier_membership_configuration.get('memberships'))>0:
            existing_memberships_list  = self.tier_membership_configuration.get('memberships')
            new_memberships_list       = []
            for p in existing_memberships_list:
                try:
                    membership = ndb.Key(urlsafe=p.get('membership_key')).get()
                    if membership.archived is False:
                        new_memberships_list.append(p)
                except:
                    pass
            
            self.tier_membership_configuration['memberships'] = new_memberships_list
            self.tier_membership_configuration['count']       = len(new_memberships_list)
            
        else:
            self.tier_membership_configuration = {'memberships':[], 'count':0}
        
        self.put()
        
    def flush_and_update_membership_configuration(self, memberships_list):    
        
        logger.debug('flush_and_update_membership_configuration: memberships_list count=%d ', len(memberships_list))
        
        membership_configuration_list = []
        
        for m in memberships_list:
            membership_configuration_list.append(m.to_configuration())
            
        self.membership_configuration = {'memberships':membership_configuration_list, 'count':len(membership_configuration_list)}
        
        self.put()
        
    def flush_and_update_tier_membership_configuration(self, memberships_list):
        
        logger.debug('flush_and_update_tier_membership_configuration: memberships_list count=%d ', len(memberships_list))  
        
        membership_configuration_list = []
        
        for m in memberships_list:
            membership_configuration_list.append(m.to_configuration())
            
        self.tier_membership_configuration = {'memberships':membership_configuration_list, 'count':len(membership_configuration_list)}
        
        self.put()                
        
    def update_published_program(self, program_configuration):
        if is_empty(self.published_program_configuration):
            self.published_program_configuration = {
                                                'programs'  :[program_configuration],
                                                'count'     : 1,
                                                } 
                                            
        else:
            self.flush_dirty_program_configuration()
            existing_programs_list  = self.published_program_configuration.get('programs')
            
            program_key = program_configuration.get('program_key')
            index = 0
            for p in existing_programs_list:
                if p.get('program_key') == program_key:
                    existing_programs_list.pop(index)
                
                index = index+1
            
            existing_programs_list.append(program_configuration)
            
            self.published_program_configuration['programs']    = existing_programs_list
            self.published_program_configuration['count']       = len(existing_programs_list) 
            
        self.put()
        
    def update_published_tier_program(self, program_configuration):
        if is_empty(self.published_tier_program_configuration):
            self.published_program_configuration = {
                                                'programs'  :[program_configuration],
                                                'count'     : 1,
                                                } 
                                            
        else:
            self.flush_dirty_program_configuration()
            existing_programs_list  = self.published_tier_program_configuration.get('programs')
            
            program_key = program_configuration.get('program_key')
            index = 0
            for p in existing_programs_list:
                if p.get('program_key') == program_key:
                    existing_programs_list.pop(index)
                
                index = index+1
            
            existing_programs_list.append(program_configuration)
            
            self.published_tier_program_configuration['programs']    = existing_programs_list
            self.published_tier_program_configuration['count']       = len(existing_programs_list) 
            
        self.put()    
        deleteFromCache(self.key_in_str)
        
    def update_published_referral_program(self, program_configuration):
        if is_empty(self.published_referral_program_configuration):
            self.published_referral_program_configuration = {
                                                'programs'  :[program_configuration],
                                                'count'     : 1,
                                                } 
                                            
        else:
            self.flush_dirty_program_configuration()
            existing_programs_list  = self.published_referral_program_configuration.get('programs')
            
            program_key = program_configuration.get('program_key')
            index = 0
            for p in existing_programs_list:
                if p.get('program_key') == program_key:
                    existing_programs_list.pop(index)
                
                index = index+1
            
            existing_programs_list.append(program_configuration)
            
            self.published_referral_program_configuration['programs']    = existing_programs_list
            self.published_referral_program_configuration['count']       = len(existing_programs_list) 
            
        self.put()   
        deleteFromCache(self.key_in_str) 
        
    def add_voucher(self, voucher_configuration):
        if is_empty(self.published_voucher_configuration):
            self.published_voucher_configuration = {
                                                'vouchers'  :[voucher_configuration],
                                                'count'     : 1,
                                                } 
                                            
        else:
            existing_vouchers_list  = self.published_voucher_configuration.get('vouchers')
            
            voucher_key = voucher_configuration.get('voucher_key')
            
            index = 0
            for v in existing_vouchers_list:
                if v.get('voucher_key') == voucher_key:
                    existing_vouchers_list.pop(index)
                
                index = index+1
            
            existing_vouchers_list.append(voucher_configuration)
            
            self.published_voucher_configuration['vouchers']    = existing_vouchers_list
            self.published_voucher_configuration['count']       = len(existing_vouchers_list) 
            
        self.put() 
        deleteFromCache(self.key_in_str)
        
    def remove_voucher(self, voucher_key):
        existing_vouchers_list = self.published_voucher_configuration['vouchers']
        
        new_vouchers_list = []
        for voucher in existing_vouchers_list:
            if voucher.get('voucher_key') != voucher_key:
                new_vouchers_list.append(voucher)
            
        
        self.published_voucher_configuration['vouchers']    = new_vouchers_list
        self.published_voucher_configuration['count']       = len(new_vouchers_list)
            
        self.put()  
        deleteFromCache(self.key_in_str)
        
    def add_merchant_news(self, merchant_news_configuration):
        if is_empty(self.published_news_configuration):
            self.published_news_configuration = {
                                                'news'  :[merchant_news_configuration],
                                                'count'     : 1,
                                                } 
                                            
        else:
            existing_merchant_news_list  = self.published_news_configuration.get('news')
            
            merchant_news_key = merchant_news_configuration.get('merchant_news_key')
            
            if len(existing_merchant_news_list)>0:
                index = 0
                for v in existing_merchant_news_list:
                    if v.get('merchant_news_key') == merchant_news_key:
                        existing_merchant_news_list.pop(index)
                    
                    index = index+1
            
            existing_merchant_news_list.append(merchant_news_configuration)
            
            self.published_news_configuration['news']    = existing_merchant_news_list
            self.published_news_configuration['count']   = len(existing_merchant_news_list) 
            
        self.put() 
        deleteFromCache(self.key_in_str)
        
    def remove_merchant_news(self, merchant_news_key):
        existing_merchant_news_list = self.published_news_configuration['news']
        
        latest_news_list = []
        #now = datetime.now()
        for merchant_news in existing_merchant_news_list:
            if merchant_news.get('merchant_news_key') != merchant_news_key:
                #end_datetime = datetime.strptime('%d-%m-%Y %H:%m:%S', merchant_news.ge('end_datetime'))
                #if end_datetime >
                latest_news_list.append(merchant_news)
            
        
        self.published_news_configuration['news']    = latest_news_list
        self.published_news_configuration['count']   = len(latest_news_list)
            
        self.put()  
        deleteFromCache(self.key_in_str)      
        
    def update_prepaid_program(self, prepaid_configuration):
        if self.prepaid_configuration is None or len(self.prepaid_configuration)==0:
            self.prepaid_configuration = {
                                                'programs'  :[prepaid_configuration],
                                                'count'     : 1,
                                                } 
                                            
        else:
            existing_prepaid_program_list  = self.prepaid_configuration.get('programs')
            
            prepaid_program_key = prepaid_configuration.get('program_key')
            
            index = 0
            for v in existing_prepaid_program_list:
                if v.get('program_key') == prepaid_program_key:
                    existing_prepaid_program_list.pop(index)
                
                index = index+1
            
            existing_prepaid_program_list.append(prepaid_configuration)
            
            self.prepaid_configuration['programs']        = existing_prepaid_program_list
            self.prepaid_configuration['count']           = len(existing_prepaid_program_list) 
            
        self.put()
        deleteFromCache(self.key_in_str)
        
    def update_lucky_draw_program(self, lucky_draw_configuration):
        logger.debug('update_lucky_draw_program debug: lucky_draw_configuration = %s', lucky_draw_configuration)
        if self.lucky_draw_configuration is None or len(self.lucky_draw_configuration)==0:
            self.lucky_draw_configuration = {
                                                'programs'  :[lucky_draw_configuration],
                                                'count'     : 1,
                                                } 
                                                
        existing_lucky_draw_list  = self.lucky_draw_configuration.get('programs')
        
        program_key = lucky_draw_configuration.get('program_key')
        
        index = 0
        for v in existing_lucky_draw_list:
            if v.get('program_key') == program_key:
                existing_lucky_draw_list.pop(index)
            
            index = index+1
        
        existing_lucky_draw_list.append(lucky_draw_configuration)
        
        self.lucky_draw_configuration['programs']        = existing_lucky_draw_list
        self.lucky_draw_configuration['count']           = len(existing_lucky_draw_list) 
            
        self.put()  
        deleteFromCache(self.key_in_str)
    
    def update_published_redemption_catalogue(self, catalogue_configuration):
        if is_empty(self.published_redemption_catalogue_configuration):
            self.published_redemption_catalogue_configuration = {
                                                'catalogues'    :[catalogue_configuration],
                                                'count'         : 1,
                                                } 
                                            
        else:
            existing_catalogue_list  = self.published_redemption_catalogue_configuration.get('catalogues')
            
            catalogue_key = catalogue_configuration.get('catalogue_key')
            
            index = 0
            for v in existing_catalogue_list:
                if v.get('catalogue_key') == catalogue_key:
                    existing_catalogue_list.pop(index)
                
                index = index+1
            
            existing_catalogue_list.append(catalogue_configuration)
            
            self.published_redemption_catalogue_configuration['catalogues']  = existing_catalogue_list
            self.published_redemption_catalogue_configuration['count']       = len(existing_catalogue_list) 
            
        self.put()  
        deleteFromCache(self.key_in_str) 
    
    @property
    def partner_configuration(self):
        merchant_acct_key = self.key_in_str
        account_settings        = {
                                'account_code'  : self.account_code,
                                'currency'      : self.currency_code,
                                'locale'        : self.locale,    
                                }
        
        
        return {
                'key'                               : merchant_acct_key,
                'merchant_acct_key'                 : merchant_acct_key,
                'account_id'                        : self.account_code,
                'company_name'                      : self.company_name,
                'brand_name'                        : self.brand_name,
                'logo_image_url'                    : self.logo_public_url,
                'website'                           : self.website,
                'account_settings'                  : account_settings,
                'published_voucher_configuration'   : self.published_voucher_configuration,
            }
        
    def update_partner_merchant_configuration(self, partner_merchant_configuration):
        merchant_acct_key = partner_merchant_configuration.get('merchant_acct_key')
        
        if is_empty(self.partner_merchant_history_configuration):
            self.partner_merchant_history_configuration = {
                                                                'partners':{},
                                                                'count':0
                                                                }
        
        if is_empty(self.approved_partner_merchant_configuration):
            self.approved_partner_merchant_configuration = {
                                                'partners'              :{
                                                                            merchant_acct_key  : partner_merchant_configuration,
                                                                            },
                                                'count'               : 1,
                                                } 
            
            self.partner_merchant_history_configuration = {
                                                'partners'              :{
                                                                            merchant_acct_key  : partner_merchant_configuration,
                                                                            },
                                                'count'               : 1,
                                                } 
                                            
        else:
            
            existing_partner_merchant_dict  = self.approved_partner_merchant_configuration.get('partners')
            partner_merchant_history_dict   = self.partner_merchant_history_configuration.get('partners')
            partner_merchant_details        = existing_partner_merchant_dict.get(merchant_acct_key)
            
            if partner_merchant_details:
                existing_partner_merchant_dict[merchant_acct_key] = partner_merchant_configuration
            else:
                existing_partner_merchant_dict[merchant_acct_key] = partner_merchant_configuration
                self.approved_partner_merchant_configuration['count']+=self.approved_partner_merchant_configuration['count']
            
            partner_merchant_details        = partner_merchant_history_dict.get(merchant_acct_key) 
            if partner_merchant_details:
                partner_merchant_history_dict[merchant_acct_key] = partner_merchant_configuration
            else:
                partner_merchant_history_dict[merchant_acct_key] = partner_merchant_configuration
            
            self.partner_merchant_history_configuration['count']=len(self.partner_merchant_history_configuration['partners'])
                
        self.put()  
        deleteFromCache(self.key_in_str)     
    
    def remove_partner_merchant_configuration(self, partner_merchant_acct_key):
        if self.approved_partner_merchant_configuration is not None:
            existing_partner_merchant_dict = self.approved_partner_merchant_configuration.get('partners')
            
            logger.debug('existing_partner_merchant_dict=%s', existing_partner_merchant_dict)
            
            if existing_partner_merchant_dict:# and existing_partner_merchant_dict.get(existing_partner_merchant_dict):
                for key in existing_partner_merchant_dict.keys():
                    logger.debug('key=%s', key)
                if partner_merchant_acct_key in existing_partner_merchant_dict:
                    #existing_partner_merchant_dict.pop(partner_merchant_acct_key)
                    del existing_partner_merchant_dict[partner_merchant_acct_key]
                    self.approved_partner_merchant_configuration['count']-=1
                else:
                    logger.debug('%s not found', partner_merchant_acct_key)
        
        
    def update_approved_partner_redemption_catalogue(self, catalogue_configuration):
        if is_empty(self.partner_redemption_catalogue_configuration):
            self.partner_redemption_catalogue_configuration = {
                                                'catalogues'    :[catalogue_configuration],
                                                'count'         : 1,
                                                } 
                                            
        else:
            existing_catalogue_list  = self.partner_redemption_catalogue_configuration.get('catalogues')
            
            catalogue_key = catalogue_configuration.get('catalogue_key')
            
            index = 0
            for v in existing_catalogue_list:
                if v.get('catalogue_key') == catalogue_key:
                    existing_catalogue_list.pop(index)
                
                index = index+1
            
            existing_catalogue_list.append(catalogue_configuration)
            
            self.partner_redemption_catalogue_configuration['catalogues']  = existing_catalogue_list
            self.partner_redemption_catalogue_configuration['count']       = len(existing_catalogue_list) 
            
        self.put()  
        deleteFromCache(self.key_in_str)     
        
    def update_lucky_draw_program_settings(self, lucky_draw_program_settings):
        logger.debug('update_lucky_draw_program_settings debug: lucky_draw_program_settings = %s', lucky_draw_program_settings)
        if self.lucky_draw_configuration is None or len(self.lucky_draw_configuration)==0:
            self.lucky_draw_configuration = {'settings':{}}
            
        self.lucky_draw_configuration['settings'] = lucky_draw_program_settings
        self.put()
        deleteFromCache(self.key_in_str)
        
    def update_lucky_draw_ticket_image(self, ticket_image_url):
        if self.lucky_draw_configuration is None or len(self.lucky_draw_configuration)==0:
            self.lucky_draw_configuration = {'settings':{}}
            
        self.lucky_draw_configuration['settings']['ticket_image_url'] = ticket_image_url
        self.put()   
        deleteFromCache(self.key_in_str) 
        
        
    def update_product_modifier(self, product_modifier_configuration):
        if self.product_modifier_configuration is None or len(self.product_modifier_configuration)==0:
            self.product_modifier_configuration = {
                                                'modifiers'  :[product_modifier_configuration],
                                                'count'     : 1,
                                                } 
                                            
        else:
            existing_product_modifiers_list  = self.product_modifier_configuration.get('modifiers')
            
            modifier_key = product_modifier_configuration.get('modifier_key')
            
            index = 0
            for v in existing_product_modifiers_list:
                if v.get('modifier_key') == modifier_key:
                    existing_product_modifiers_list.pop(index)
                
                index = index+1
            
            existing_product_modifiers_list.append(product_modifier_configuration)
            
            self.product_modifier_configuration['modifiers']        = existing_product_modifiers_list
            self.product_modifier_configuration['count']            = len(existing_product_modifiers_list) 
            
        self.put()  
        deleteFromCache(self.key_in_str)       
        
    def add_membership(self, membership_configuration):
        if is_empty(self.membership_configuration):
            self.membership_configuration = {
                                                'memberships'  :[membership_configuration],
                                                'count'     : 1,
                                                } 
                                            
        else:
            self.flush_dirty_membership_configuration()
            existing_memberships_list  = self.membership_configuration.get('memberships')
            existing_memberships_list.append(membership_configuration)
            
            self.membership_configuration['memberships']     = existing_memberships_list
            self.membership_configuration['count']           = len(existing_memberships_list) 
            
        self.put()
        deleteFromCache(self.key_in_str)
        
    def update_membership(self, membership_configuration):
        if is_empty(self.membership_configuration):
            self.membership_configuration = {
                                                'memberships'  :[membership_configuration],
                                                'count'     : 1,
                                                } 
                                            
        else:
            self.flush_dirty_membership_configuration()
            existing_memberships_list  = self.membership_configuration.get('memberships')
            
            for idx, em in enumerate(existing_memberships_list):
                if em.get('membership_key') == membership_configuration.get('membership_key'):
                    existing_memberships_list[idx] = membership_configuration
                    break
            
            self.membership_configuration['memberships']     = existing_memberships_list 
            
        self.put() 
        deleteFromCache(self.key_in_str)    
        
    def add_tier_membership(self, membership_configuration):
        if is_empty(self.tier_membership_configuration):
            self.tier_membership_configuration = {
                                                'memberships'   :[membership_configuration],
                                                'count'         : 1,
                                                } 
                                            
        else:
            self.flush_dirty_tier_membership_configuration()
            existing_memberships_list  = self.tier_membership_configuration.get('memberships')
            existing_memberships_list.append(membership_configuration)
            
            self.tier_membership_configuration['memberships']     = existing_memberships_list
            self.tier_membership_configuration['count']           = len(existing_memberships_list) 
            
        self.put()
        deleteFromCache(self.key_in_str)
        
    def update_tier_membership(self, membership_configuration):
        if is_empty(self.tier_membership_configuration):
            self.tier_membership_configuration = {
                                                'memberships'   :[membership_configuration],
                                                'count'         : 1,
                                                } 
                                            
        else:
            self.flush_dirty_tier_membership_configuration()
            existing_memberships_list  = self.tier_membership_configuration.get('memberships')
            
            for idx, em in enumerate(existing_memberships_list):
                if em.get('membership_key') == membership_configuration.get('membership_key'):
                    existing_memberships_list[idx] = membership_configuration
                    break
            
            self.tier_membership_configuration['memberships']     = existing_memberships_list
            
        self.put() 
        deleteFromCache(self.key_in_str)               
        
    def remove_program_from_published_program_configuration(self, program_key_to_remove):
        
        logger.debug('remove_program_from_published_program_configuration: program_key_to_remove=%s', program_key_to_remove)
        
        #self.flush_dirty_program_configuration()
        existing_programs_list  = self.published_program_configuration['programs']
        program_count           = len(existing_programs_list)
        
        logger.debug('program_count before remove=%s', program_count)
        
        index = 0
        
        for program in existing_programs_list:
            
            logger.debug('program_key=%s', program.get('program_key'))
            
            is_same_program_key = program.get('program_key') == program_key_to_remove
            
            logger.debug('is_same_program_key=%s', is_same_program_key)
            
            if is_same_program_key:
                existing_programs_list.pop(index)
                
                logger.debug('Found program to be remove')
                
            index = index+1
        
        program_count = len(existing_programs_list)
        
        logger.debug('program_count after remove=%s', program_count)
        
        self.published_program_configuration['programs']    = existing_programs_list
        self.published_program_configuration['count']       = program_count
            
        self.put() 
        deleteFromCache(self.key_in_str)
    
    def remove_tier_program_from_published_tier_program_configuration(self, program_key_to_remove):
        
        logger.debug('remove_tier_program_from_published_tier_program_configuration: program_key_to_remove=%s', program_key_to_remove)
        
        #self.flush_dirty_program_configuration()
        if self.published_tier_program_configuration:
            existing_programs_list  = self.published_tier_program_configuration['programs']
            program_count           = len(existing_programs_list)
            
        else:
            self.published_tier_program_configuration = {}
            existing_programs_list  = []
            program_count           = 0
            
        
        logger.debug('program_count before remove=%s', program_count)
        
        index = 0
        
        for program in existing_programs_list:
            
            logger.debug('program_key=%s', program.get('program_key'))
            
            is_same_program_key = program.get('program_key') == program_key_to_remove
            
            logger.debug('is_same_program_key=%s', is_same_program_key)
            
            if is_same_program_key:
                existing_programs_list.pop(index)
                
                logger.debug('Found program to be remove')
                
            index = index+1
        
        program_count = len(existing_programs_list)
        
        logger.debug('program_count after remove=%s', program_count)
        
        self.published_tier_program_configuration['programs']    = existing_programs_list
        self.published_tier_program_configuration['count']       = program_count
            
        self.put() 
        deleteFromCache(self.key_in_str)
        
    def remove_program_from_published_referral_program_configuration(self, program_key_to_remove):
        
        logger.debug('remove_program_from_published_referral_program_configuration: program_key_to_remove=%s', program_key_to_remove)
        
        #self.flush_dirty_program_configuration()
        existing_programs_list  = self.published_referral_program_configuration['programs']
        program_count           = len(existing_programs_list)
        
        logger.debug('program_count before remove=%s', program_count)
        
        index = 0
        
        for program in existing_programs_list:
            
            logger.debug('program_key=%s', program.get('program_key'))
            
            is_same_program_key = program.get('program_key') == program_key_to_remove
            
            logger.debug('is_same_program_key=%s', is_same_program_key)
            
            if is_same_program_key:
                existing_programs_list.pop(index)
                
                logger.debug('Found program to be remove')
                
            index = index+1
        
        program_count = len(existing_programs_list)
        
        logger.debug('program_count after remove=%s', program_count)
        
        self.published_referral_program_configuration['programs']    = existing_programs_list
        self.published_referral_program_configuration['count']       = program_count
            
        self.put()     
        deleteFromCache(self.key_in_str)
    
        
    def remove_redeption_catalogue(self, catalogue_key):
        existing_catalogues_list = self.published_redemption_catalogue_configuration['catalogues']
        
        new_catalogues_list = []
        for catalogue in existing_catalogues_list:
            if catalogue.get('catalogue_key') != catalogue_key:
                new_catalogues_list.append(catalogue)
            
        
        self.published_redemption_catalogue_configuration['catalogues']      = new_catalogues_list
        self.published_redemption_catalogue_configuration['count']           = len(new_catalogues_list)
            
        self.put()
        deleteFromCache(self.key_in_str)
        
    def remove_partner_redeption_catalogue(self, catalogue_key):
        if self.partner_redemption_catalogue_configuration:
            existing_catalogues_list = self.partner_redemption_catalogue_configuration.get('catalogues', [])
            if existing_catalogues_list:
                new_catalogues_list = []
                for catalogue in existing_catalogues_list:
                    if catalogue.get('catalogue_key') != catalogue_key:
                        new_catalogues_list.append(catalogue)
                    
                
                self.partner_redemption_catalogue_configuration['catalogues']      = new_catalogues_list
                self.partner_redemption_catalogue_configuration['count']           = len(new_catalogues_list)
                    
                self.put()
                deleteFromCache(self.key_in_str)
            else:
                logger.debug('catalogue not found from partner redemption catalogue configuration') 
        else:
            logger.debug('partner redemption catalogue configuration is empty')
            
    def remove_archieve_redemption_catalogue(self, archieve_redemption_catalogue_key):
        existing_catalogues_list = self.published_redemption_catalogue_configuration['catalogues']
        
        new_catalogues_list = []
        for catalogue in existing_catalogues_list:
            if catalogue.get('catalogue_key') != archieve_redemption_catalogue_key:
                new_catalogues_list.append(catalogue)
            
        
        self.published_redemption_catalogue_configuration['catalogues']  = new_catalogues_list
        self.published_redemption_catalogue_configuration['count']       = len(new_catalogues_list)
            
        self.put()
        deleteFromCache(self.key_in_str)
        
    def remove_archieve_basic_membership(self, archieve_membership_key):
        self.flush_dirty_membership_configuration()
        existing_memberships_list = self.membership_configuration['memberships']
        
        index = 0
        
        for m in existing_memberships_list:
            if m.get('membership_key') == archieve_membership_key:
                existing_memberships_list.pop(index)
            index = index+1
        
        self.membership_configuration['memberships']    = existing_memberships_list
        self.membership_configuration['count']       = len(existing_memberships_list)
            
        self.put()
        deleteFromCache(self.key_in_str)
        
    def remove_archieve_tier_membership(self, archieve_membership_key):
        self.flush_dirty_tier_membership_configuration()
        existing_memberships_list = self.tier_membership_configuration['memberships']
        
        index = 0
        
        for m in existing_memberships_list:
            if m.get('membership_key') == archieve_membership_key:
                existing_memberships_list.pop(index)
            index = index+1
        
        self.tier_membership_configuration['memberships']  = existing_memberships_list
        self.tier_membership_configuration['count']             = len(existing_memberships_list)
            
        self.put()
        deleteFromCache(self.key_in_str)
        
    def remove_prepaid_program_configuration(self, program_key_to_remove):
        
        logger.debug('remove_prepaid_program_configuration: program_key_to_remove=%s', program_key_to_remove)
        if self.prepaid_configuration and self.prepaid_configuration.get('programs'):
            existing_programs_list  = self.prepaid_configuration['programs']
            program_count           = len(existing_programs_list)
            
            logger.debug('program_count before remove=%s', program_count)
            
            index = 0
            
            for program in existing_programs_list:
                
                logger.debug('program_key=%s', program.get('program_key'))
                
                is_same_program_key = program.get('program_key') == program_key_to_remove
                
                logger.debug('is_same_program_key=%s', is_same_program_key)
                
                if is_same_program_key:
                    existing_programs_list.pop(index)
                    
                    logger.debug('Found program to be remove')
                    
                index = index+1
            
            program_count = len(existing_programs_list)
            
            logger.debug('program_count after remove=%s', program_count)
            
            self.prepaid_configuration['programs']    = existing_programs_list
            self.prepaid_configuration['count']       = program_count
                
            self.put()
            deleteFromCache(self.key_in_str)
            
    def remove_lucky_draw_program_configuration(self, program_key_to_remove):
        
        logger.debug('remove_prepaid_program_configuration: program_key_to_remove=%s', program_key_to_remove)
        if self.lucky_draw_configuration and self.lucky_draw_configuration.get('programs'):
            existing_programs_list  = self.lucky_draw_configuration['programs']
            program_count           = len(existing_programs_list)
            
            logger.debug('program_count before remove=%s', program_count)
            
            index = 0
            found = False
            
            for program in existing_programs_list:
                
                logger.debug('program_key=%s', program.get('program_key'))
                
                is_same_program_key = program.get('program_key') == program_key_to_remove
                
                logger.debug('is_same_program_key=%s', is_same_program_key)
                
                if is_same_program_key:
                    existing_programs_list.pop(index)
                    found = True
                    logger.debug('Found program to be remove')
                    
                index = index+1
            
            if found:
                program_count = len(existing_programs_list)
                
                logger.debug('program_count after remove=%s', program_count)
                
                self.lucky_draw_configuration['programs']    = existing_programs_list
                self.lucky_draw_configuration['count']       = program_count
                    
                self.put()
                deleteFromCache(self.key_in_str)  
            
    def remove_product_modifier_configuration(self, modifier_key_to_remove):
        
        logger.debug('remove_product_modifier_configuration: modifier_key_to_remove=%s', modifier_key_to_remove)
        if self.product_modifier_configuration and self.product_modifier_configuration.get('modifiers'):
            existing_product_modifiers_list     = self.product_modifier_configuration['modifiers']
            modifiers_count                     = len(existing_product_modifiers_list)
            
            logger.debug('modifiers_count before remove=%s', modifiers_count)
            
            index = 0
            
            for modifier in existing_product_modifiers_list:
                
                logger.debug('modifier_key=%s', modifier.get('modifier_key'))
                
                is_same_modifier_key = modifier.get('modifier_key') == modifier_key_to_remove
                
                logger.debug('is_same_modifier_key=%s', is_same_modifier_key)
                
                if is_same_modifier_key:
                    existing_product_modifiers_list.pop(index)
                    
                    logger.debug('Found modifier to be remove')
                    
                index = index+1
            
            modifiers_count = len(existing_product_modifiers_list)
            
            logger.debug('modifiers_count after remove=%s', modifiers_count)
            
            self.product_modifier_configuration['modifiers']     = existing_product_modifiers_list
            self.product_modifier_configuration['count']         = modifiers_count
                
            self.put()
            deleteFromCache(self.key_in_str)
    
    def update_stat_details(self, stat_dict):
        dashboard_stat_figure = self.dashboard_stat_figure
        logger.debug('update_stat_figure: dashboard_stat_figure=%s', dashboard_stat_figure)
        
        next_updated_datetime = datetime.now() + timedelta(minutes=int(self.stat_figure_update_interval_in_minutes))
        
        logger.debug('update_stat_figure: next_updated_datetime=%s', next_updated_datetime)
        
        dashboard_stat_figure = {
                                'next_updated_datetime' : next_updated_datetime.strftime(self.stat_figure_update_datetime_format),
                                'stat_details'          : stat_dict,
                             }
            
        self.dashboard_stat_figure = dashboard_stat_figure
        self.put()
        deleteFromCache(self.key_in_str)
    
    def get_stat_details(self):
        dashboard_stat_figure = self.dashboard_stat_figure
        
        logger.debug('get_stat_figure: dashboard_stat_figure=%s', dashboard_stat_figure)
        
        if dashboard_stat_figure is not None and dashboard_stat_figure.get('next_updated_datetime'):
            next_updated_datetime = dashboard_stat_figure.get('next_updated_datetime')
            
            logger.debug('get_stat_figure: next_updated_datetime=%s', next_updated_datetime)
            
            if next_updated_datetime:
                next_updated_datetime = datetime.strptime(next_updated_datetime, self.stat_figure_update_datetime_format)
                now = datetime.now()
                if now > next_updated_datetime:
                    return None
                else:
                    return dashboard_stat_figure.get('stat_details')
        
        return None
    
    @staticmethod
    def create(company_name=None, brand_name=None, contact_name=None, email=None, mobile_phone=None, office_phone=None, 
               plan_start_date=None, plan_end_date=None, industry='fb', 
               account_code=None, currency_code=None, country=None, timezone=None, website=None,
               product_package=None,loyalty_package=None, pos_package=None, outlet_limit=1
               ):
        
        if account_code is None:
            account_code    = "%s-%s-%s-%s" % (random_number(4),random_number(4),random_number(4),random_number(4))
        
        account_plan = {
                        'product_package'   : product_package.split(','),
                        'loyalty_package'   : loyalty_package,
                        'pos_package'       : pos_package,
                        'outlet_limit'      : outlet_limit,
                        }
            
        merchant_acct   = MerchantAcct(
                                       company_name     = company_name,
                                       brand_name       = brand_name,     
                                       contact_name     = contact_name,
                                       email            = email,
                                       mobile_phone     = mobile_phone,
                                       office_phone     = office_phone,
                                       account_plan     = account_plan,
                                       plan_start_date  = plan_start_date, 
                                       plan_end_date    = plan_end_date,
                                       currency_code    = currency_code,
                                       country          = country, 
                                       timezone         = timezone,   
                                       website          = website,
                                       api_key          = random_string(24),
                                       industry         = industry,
                                       program_settings = MerchantAcct.default_program_settings(),
                                       
                                       
                                       )
        
        logging.debug('account_code=%s', account_code)
        
        merchant_acct.account_code = account_code
        
        merchant_acct.put()
        
        return merchant_acct
    
    @staticmethod
    def update(merchant_acct, company_name=None, brand_name=None, contact_name=None, email=None, mobile_phone=None, office_phone=None, 
               plan_start_date=None, plan_end_date=None,  
               currency_code=None, country=None, timezone=None, website=None,
               product_package=None,loyalty_package=None, pos_package=None, outlet_limit=1,
               ):
        
        account_plan = {
                        'product_package'   : product_package.split(','),
                        'loyalty_package'   : loyalty_package,
                        'pos_package'       : pos_package,
                        'outlet_limit'      : outlet_limit, 
                        }
        
        merchant_acct.company_name     = company_name
        merchant_acct.brand_name       = brand_name    
        merchant_acct.contact_name     = contact_name
        merchant_acct.email            = email
        merchant_acct.mobile_phone     = mobile_phone
        merchant_acct.office_phone     = office_phone
        merchant_acct.plan_start_date  = plan_start_date 
        merchant_acct.plan_end_date    = plan_end_date
        merchant_acct.currency_code    = currency_code
        merchant_acct.country          = country
        merchant_acct.timezone         = timezone
        merchant_acct.website          = website
        merchant_acct.account_plan     = account_plan
        
        
        merchant_acct.put()
        deleteFromCache(merchant_acct.key_in_str)
        return merchant_acct
    
    
    @staticmethod
    def get_by_account_code(account_code):
        result = getFromCache(account_code)
        if result is None:
            result =  MerchantAcct.query(ndb.AND(MerchantAcct.account_code==account_code)).get()
            setCache(account_code, result, timeout=300)
        
        return result
    
    @staticmethod
    def get_by_api_key(api_key):
        return MerchantAcct.query(ndb.AND(MerchantAcct.api_key==api_key)).get()
        
    
    @staticmethod
    def list(offset=None, start_cursor=None, return_with_cursor=False, limit = model_conf.MAX_FETCH_RECORD):
        if return_with_cursor:
            query = MerchantAcct.query()
            (result, next_cursor) = MerchantAcct.list_all_with_condition_query(query, start_cursor=start_cursor, return_with_cursor=True, limit=limit)
        
            return (result, next_cursor)
        else:
            return MerchantAcct.query().order(-MerchantAcct.registered_datetime).fetch(offset=offset, limit=limit)
    
    def delete_and_related(self):
        
        @ndb.transactional()
        def start_transaction(merchant_acct):
            merchant_user_key_list = MerchantUser.list_by_merchant_account(merchant_acct, keys_only=True)
            if merchant_user_key_list:
                ndb.delete_multi(merchant_user_key_list)
            
            merchant_acct.delete()
            logger.debug('after deleted merchant acct and merchant user')
            
        
        start_transaction(self)
        deleteFromCache(self.key_in_str)
    
    def _list_data_import_giveaway_programs(self, target_reward_format):
        published_program_configuration = self.published_program_configuration
        
        data_import_giveaway_programs = []
        
        for program in published_program_configuration.get('programs'):
            if program.get('giveaway_method') == program_conf.PROGRAM_REWARD_GIVEAWAY_METHOD_SYSTEM:
                if program.get('program_settings').get('giveaway_system_settings') and program.get('program_settings').get('giveaway_system_settings').get('giveaway_system_condition'):
                    logger.debug('giveaway system condition=%s', program.get('program_settings').get('giveaway_system_settings').get('giveaway_system_condition'))
                    if program.get('program_settings').get('giveaway_system_settings').get('giveaway_system_condition') == program_conf.GIVEAWAY_SYSTEM_CONDITION_DATA_IMPORT:
                        logger.debug('giveaway reward_format=%s', program.get('reward_format'))
                        if program.get('reward_format') == target_reward_format:
                            data_import_giveaway_programs.append({
                                                                'program_key'   : program.get('program_key'),
                                                                'label'         : program.get('label'),
                                                                })
                    
        return data_import_giveaway_programs
    
    def list_data_import_giveaway_prepaid_programs(self):
        return self._list_data_import_giveaway_programs(program_conf.REWARD_FORMAT_PREPAID)
    
    def list_data_import_giveaway_point_programs(self):
        return self._list_data_import_giveaway_programs(program_conf.REWARD_FORMAT_POINT)
    
    def list_data_import_giveaway_stamp_programs(self):
        return self._list_data_import_giveaway_programs(program_conf.REWARD_FORMAT_STAMP)
        
        
class MerchantSentEmail(SentEmail):
    '''
    Merchant account as Ancestor
    '''
    pass

class Outlet(BusinessEntity, FullTextSearchable):
    '''
    Merchant account as Ancestor
    '''
    
    merchant_acct                   = ndb.KeyProperty(name="merchant_acct", kind=MerchantAcct)
    id                              = ndb.StringProperty(required=False)
    name                            = ndb.StringProperty(required=True)
    address                         = ndb.StringProperty(required=False)
    office_phone                    = ndb.StringProperty(required=False)
    fax_phone                       = ndb.StringProperty(required=False)
    email                           = ndb.StringProperty(required=False)
    business_hour                   = ndb.StringProperty(required=False)
    
    is_physical_store               = ndb.BooleanProperty(required=False, default=True)
    geo_location                    = ndb.GeoPtProperty(required=False)
    created_datetime                = ndb.DateTimeProperty(required=True, auto_now_add=True)
    modified_datetime               = ndb.DateTimeProperty(auto_now=True)
    
    assigned_tax_setup              = ndb.JsonProperty()
    receipt_settings                = ndb.JsonProperty()
    service_charge_settings         = ndb.JsonProperty()
    
    assigned_catalogue_key          = ndb.StringProperty(required=False)
    assigned_dinning_table_list     = ndb.JsonProperty()
    
    is_headquarter                  = ndb.BooleanProperty(required=False, default=False)
    
    show_dinning_table_occupied     = ndb.BooleanProperty(required=False, default=False)    
    
    fulltextsearch_field_name   = 'name'
    
    dict_properties         = ['key', 'id', 'company_name', 'business_reg_no', 'name', 'address', 'office_phone', 
                                'fax_phone', 'email', 'business_hour', 'is_physical_store', 'assigned_catalogue_key', 'assigned_dinning_table_list',
                                'service_charge_settings', 'assigned_tax_setup', 'is_headquarter',
                                'geo_location', 'created_datetime']
    
    @property
    def merchant_acct_entity(self):
        #return MerchantAcct.fetch(self.key.parent().urlsafe())
        return self.key.parent().get()
    
    @property
    def merchant_acct_key(self):
        return self.key.parent().urlsafe().decode('utf-8')
    
    @property
    def outlet_key(self):
        return self.key.urlsafe()
    
    @staticmethod
    def get_head_quarter_outlet(merchant_acct):
        outlet_list = Outlet.list_all_by_merchant_account(merchant_acct)
        for outlet in outlet_list:
            if outlet.is_headquarter:
                return outlet
    
    @staticmethod
    def assign_catalogue_to_outlet(outlet_key, catalogue_key):
        outlet = Outlet.fetch(outlet_key)
        if outlet:
            outlet.assigned_catalogue_key = catalogue_key
            outlet.put()
            
    @staticmethod
    def remove_catalogue_from_outlet(outlet_key):
        outlet = Outlet.fetch(outlet_key)
        if outlet:
            outlet.assigned_catalogue_key = None
            outlet.put()
    
    @staticmethod
    def add_tax_setup(outlet_key, tax_setup):
        outlet = Outlet.fetch(outlet_key)
        if outlet:
            
            if outlet.assigned_tax_setup:
                outlet.assigned_tax_setup[tax_setup.get('tax_reg_id')] = tax_setup
            else:
            
                assigned_tax_setup={
                                tax_setup.get('tax_reg_id'): tax_setup
                                }
                outlet.assigned_tax_setup = assigned_tax_setup
            
            outlet.put()
                
    @staticmethod
    def remove_tax_setup(outlet_key, tax_reg_id):
        outlet = Outlet.fetch(outlet_key)
        if outlet:
            logger.debug('Going to remove tax setup from %s', outlet.name)
            
            if outlet.assigned_tax_setup:
                del outlet.assigned_tax_setup[tax_reg_id]
            else:
                outlet.assigned_tax_setup = {}
            
            outlet.put()
            
    @staticmethod
    def set_receipt_settings(outlet_key, receipt_settings):
        outlet = Outlet.fetch(outlet_key)
        if outlet:
            outlet.receipt_settings = receipt_settings
            outlet.put()
                
    @staticmethod
    def remove_receipt_settings(outlet_key):
        outlet = Outlet.fetch(outlet_key)
        if outlet:
            outlet.receipt_settings = {}
            outlet.put()        
            
    @staticmethod
    def assign_dinning_table_setup_to_outlet(outlet_key, table_list):
        outlet = Outlet.fetch(outlet_key)
        if outlet:
            outlet.assigned_dinning_table_list = table_list.split(',')
            outlet.put()
    
    @staticmethod
    def remove_dinning_table_setup_from_outlet(outlet_key):
        outlet = Outlet.fetch(outlet_key)
        if outlet:
            outlet.assigned_dinning_table_list = []
            outlet.put()
            
    @staticmethod
    def assign_dinning_table_control_to_outlet(outlet_key, show_dinning_table_occupied):
        outlet = Outlet.fetch(outlet_key)
        if outlet:
            outlet.show_dinning_table_occupied = show_dinning_table_occupied
            outlet.put()                        
    
    @staticmethod
    def create(merchant_acct=None,name=None, company_name=None, business_reg_no=None, address=None, email=None, fax_phone=None, 
               office_phone=None, business_hour=None, geo_location=None, is_physical_store=True, id=None, 
               is_headquarter=False,
               ):
        logger.info('is_headquarter=%s', is_headquarter)
        outlet_limit = merchant_acct.outlet_limit
        
        total_count = Outlet.count_by_merchant_account(merchant_acct)
        
        if outlet_limit<=total_count:
            raise Exception('Exceeded outlet limit')
        
        if is_headquarter:
            outlets_list = Outlet.list_all_by_merchant_account(merchant_acct)
            for outlet in outlets_list:
                if outlet.is_headquarter:
                    outlet.is_headquarter=False
                    outlet.put()
                    break
        else:
            outlets_list = Outlet.list_all_by_merchant_account(merchant_acct)
            found_hq_outlet = False
            for outlet in outlets_list:
                if outlet.is_headquarter:
                    found_hq_outlet = True
                    break
            if found_hq_outlet==False:
                raise Exception('Head Quarter outlet must created first')    
        
        outlet   = Outlet(
                            parent              = merchant_acct.create_ndb_key(),
                            name                = name,
                            id                  = id,
                            company_name        = company_name,  
                            business_reg_no     = business_reg_no,
                            address             = address,
                            email               = email,
                            fax_phone           = fax_phone,
                            office_phone        = office_phone,
                            business_hour       = business_hour,
                            geo_location        = geo_location,
                            is_physical_store   = is_physical_store,
                            is_headquarter      = is_headquarter,
                            )
        
        outlet.put()
        
        
        
        merchant_acct.outlet_count= total_count + 1
        merchant_acct.put()
        
        return outlet
    
    @staticmethod
    def update(outlet, name=None, company_name=None, business_reg_no=None, address=None, email=None, fax_phone=None, 
               office_phone=None, business_hour=None, geo_location=None, is_physical_store=True, id=None, 
               is_headquarter=False):
        
        merchant_acct = outlet.merchant_acct_entity
        
        if is_headquarter:
            merchant_acct = outlet.merchant_acct_entity
            outlets_list = Outlet.list_all_by_merchant_account(merchant_acct)
            
            for checking_outlet in outlets_list:
                if checking_outlet.is_headquarter:
                    if outlet.key_in_str !=checking_outlet.key_in_str:
                        checking_outlet.is_headquarter=False
                        checking_outlet.put()
                        break
        else:
            outlets_list = Outlet.list_all_by_merchant_account(merchant_acct)
            found_hq_outlet = False
            for checking_outlet in outlets_list:
                if checking_outlet.is_headquarter:
                    if outlet.key_in_str !=checking_outlet.key_in_str:
                        found_hq_outlet = True
                        break
            if found_hq_outlet==False:
                raise Exception('The Headquarter outlet must be created first.') 
            
        outlet.name                 = name
        outlet.id                   = id
        outlet.company_name         = company_name
        outlet.business_reg_no      = business_reg_no
        outlet.email                = email
        outlet.address              = address
        outlet.office_phone         = office_phone
        outlet.fax_phone            = fax_phone
        outlet.business_hour        = business_hour
        outlet.geo_location         = geo_location
        outlet.is_physical_store    = is_physical_store
        outlet.is_headquarter       = is_headquarter
        outlet.put()
    
    def to_brief_dict(self):
        return {
                'outlet_name'       : self.name,
                'company_name'      : self.company_name,
                'business_reg_no'   : self.business_reg_no,
                'address'           : self.address,
                'email'             : self.email,
                'office_phone'      : self.office_phone,
                }
    
    @staticmethod
    def list_by_merchant_acct(merchant_acct):
        return Outlet.query(ancestor = merchant_acct.create_ndb_key()).fetch(limit=model_conf.MAX_FETCH_RECORD)
    
    @staticmethod
    def list_all_by_merchant_account(merchant_acct, offset=None, start_cursor=None, return_with_cursor=False, keys_only=False, limit = model_conf.MAX_FETCH_RECORD):
        #condition_query =  Outlet.query(ancestor = merchant_acct.create_ndb_key()).order(-Outlet.created_datetime)
        condition_query =  Outlet.query(ancestor = merchant_acct.create_ndb_key())
        return Outlet.list_all_with_condition_query(
                                        condition_query, 
                                        offset=offset, 
                                        start_cursor=start_cursor, 
                                        return_with_cursor=return_with_cursor, 
                                        keys_only=keys_only, 
                                        limit=limit)
    
    @staticmethod
    def count_by_merchant_account(merchant_acct):
        condition_query = Outlet.query(ancestor = merchant_acct.create_ndb_key())
        return Outlet.count_with_condition_query(condition_query, limit=model_conf.MAX_FETCH_RECORD)
    
    @staticmethod
    def search_by_merchant_account(name=None, 
                                 offset=0, start_cursor=None, limit=model_conf.MAX_FETCH_RECORD):
        
        search_text_list = None
        query = Outlet.query()
        
        if is_not_empty(name):
            search_text_list = name.split(' ')
            
        total_count                         = Outlet.full_text_count(search_text_list, query, conf.MAX_FETCH_RECORD_FULL_TEXT_SEARCH)
        
        (search_results, next_cursor)       = Outlet.full_text_search(search_text_list, query, offset=offset, 
                                                                   start_cursor=start_cursor, return_with_cursor=True, 
                                                                   limit=limit)
        
        return (search_results, total_count, next_cursor)

class MerchantUser(UserMin, FullTextSearchable):
    
    '''
    parent is MerchantAcct
    '''
    username                        = ndb.StringProperty(required=True)
    granted_outlets_search_list     = ndb.StringProperty(required=False, default="")
    permission                      = ndb.JsonProperty()
    is_admin                        = ndb.BooleanProperty(required=True, default=False)
    basic_auth_token                = ndb.StringProperty(required=False)
    
    dict_properties         = ['user_id', 'name', 'username', 'permission', 'granted_outlet', 'granted_access',
                                'created_datetime', 'active', 'is_admin', 'basic_auth_token', 
                                'is_super_user', 'is_admin_user', 'is_merchant_user', 'merchant_acct_key']
    
    fulltextsearch_field_name           = 'name'
    fulltextsearch_field_to_lowercase   = True
    
    def to_login_dict(self):
        return {
                'key'                   : self.key_in_str,
                'user_id'               : self.user_id,
                'username'              : self.username,
                'name'                  : self.name,
                'permission'            : self.permission,
                'granted_outlet'        : self.granted_outlet,
                'granted_access'        : self.granted_access,
                'active'                : self.active,
                'is_admin'              : self.is_admin,
                'is_admin_user'         : self.is_admin_user,
                'is_merchant_user'      : self.is_merchant_user,
                'merchant_acct_key'     : self.merchant_acct_key,
                
                }
    
    @property
    def is_super_user(self):
        return False
    
    @property
    def is_admin_user(self):
        return self.is_admin
    
    @property
    def is_merchant_user(self):
        return True
    
    @property
    def merchant_acct(self):
        return MerchantAcct.fetch(self.key.parent().urlsafe())
    
    @property
    def merchant_acct_key(self):
        return self.key.parent().urlsafe().decode('utf-8')
    
    @property
    def granted_outlet(self):
        if self.is_admin:
            logger.debug('is admin merchant user')
            g_outlets_list = []
            all_outlet_list = Outlet.list_by_merchant_acct(self.merchant_acct)
            
            logger.debug('all_outlet_list=%s', all_outlet_list)
            
            for o in all_outlet_list:
                g_outlets_list.append(o.key_in_str)
                
            return g_outlets_list
            
        else:
            if self.permission:
                return self.permission.get('granted_outlet')
            else:
                return []
        
    @property
    def granted_outlet_details_list(self):
        g_outlets_list = []
        
        if self.is_admin:
            logger.debug('is admin merchant user')
            
            all_outlet_list = Outlet.list_by_merchant_acct(self.merchant_acct)
            
            for o in all_outlet_list:
                g_outlets_list.append({
                                        'outlet_key'    : o.key_in_str,
                                        'name'          : o.name,
                                        })
                
            return g_outlets_list
            
        else:
            outlet_key_list =  self.permission.get('granted_outlet')
            
            for o in  outlet_key_list:
                outlet_details = Outlet.fetch(o)
                g_outlets_list.append({
                                        'outlet-key'    : 0,
                                        'name'          : outlet_details.name,
                                        })
        return g_outlets_list
    
    @property
    def granted_access(self):
        if self.permission:
            return self.permission.get('granted_access')
        else:
            return []
        
    @staticmethod
    def update_permission(merchant_user, access_permission, outlet_permission, is_admin=False):
        if access_permission is None:
            access_permission = []
            
        if outlet_permission is None:
            outlet_permission = []
            
        merchant_user.is_admin = is_admin
        merchant_user.permission = {'granted_access': access_permission, 'granted_outlet': outlet_permission}
        merchant_user.granted_outlets_search_list =' '.join(outlet_permission)
        
        merchant_user.put()
    
    @staticmethod
    def create(merchant_acct=None, name=None, 
               username=None,
               password=None):
        
        check_unique_merchant_user = MerchantUser.get_by_username(username)
        
        if check_unique_merchant_user is None:
            user_id = generate_user_id()
            created_user = MerchantUser(
                                parent      = merchant_acct.create_ndb_key(),
                                user_id     = user_id, 
                                name        = name, 
                                username    = username,
                                #country     = merchant_acct.country,
                                )
            
            hashed_password = hash_password(user_id, password)
            created_user.password = hashed_password
                
            created_user.put()
            
            return created_user
        else:
            raise Exception('Username have been used')
    
    @staticmethod
    def count_by_merchant_account(merchant_acct):
        condition_query = MerchantUser.query(ancestor = merchant_acct.create_ndb_key())
        return MerchantUser.count_with_condition_query(condition_query, limit=model_conf.MAX_FETCH_RECORD)  
    
    @staticmethod
    def list_by_merchant_account(merchant_acct, keys_only=False):
        return MerchantUser.query(ancestor = merchant_acct.create_ndb_key()).order(-MerchantUser.created_datetime).fetch(limit=model_conf.MAX_FETCH_RECORD, keys_only=keys_only)
    
    @staticmethod
    def list_all_by_merchant_account(merchant_acct, offset=None, start_cursor=None, return_with_cursor=False, keys_only=False, limit = model_conf.MAX_FETCH_RECORD):
        condition_query =  MerchantUser.query(ancestor = merchant_acct.create_ndb_key()).order(-MerchantUser.created_datetime)
        return MerchantUser.list_all_with_condition_query(
                                        condition_query, 
                                        offset=offset, 
                                        start_cursor=start_cursor, 
                                        return_with_cursor=return_with_cursor, 
                                        keys_only=keys_only, 
                                        limit=limit)
    
    @staticmethod
    def get_by_username(username):
        return MerchantUser.query(ndb.AND(MerchantUser.username==username)).get()
    
    
    @staticmethod
    def get_merchant_acct_by_merchant_user(merchant_user):
        return MerchantUser.fetch(merchant_user.key.parent().urlsafe())
    
    
    @staticmethod
    def search_by_merchant_account(merchant_acct, name=None, username=None, assigned_outlet=None, 
                                 offset=0, start_cursor=None, limit=model_conf.MAX_FETCH_RECORD):
        
        
        query = MerchantUser.query(ancestor=merchant_acct.create_ndb_key())
        
        if is_not_empty(name):
            search_text_list = name.split(' ')
            
            total_count                         = MerchantUser.full_text_count(search_text_list, query, conf.MAX_FETCH_RECORD_FULL_TEXT_SEARCH)
        
            (search_results, next_cursor)       = MerchantUser.full_text_search(search_text_list, query, offset=offset, 
                                                                       start_cursor=start_cursor, return_with_cursor=True, 
                                                                       limit=limit)
            
            return (search_results, total_count, next_cursor)
        
        
        elif is_not_empty(username):
            query = query.filter(MerchantUser.username==username)
            
            
            total_count                         = MerchantUser.count_with_condition_query(
                                                                    query, 
                                                                    limit=limit)
        
            (search_results, next_cursor)       = MerchantUser.list_all_with_condition_query(
                                                                    query, 
                                                                    offset=offset, 
                                                                    start_cursor=start_cursor, 
                                                                    return_with_cursor=True, 
                                                                    limit=limit)
            
            return (search_results, total_count, next_cursor)
            
        elif is_not_empty(assigned_outlet):
            #query = query.filter(MerchantUser.granted_outlets_search_list==assigned_outlet)
            query = MerchantUser.query(
                                    
                                        MerchantUser.granted_outlets_search_list==assigned_outlet,
                                    )
            
            
            
        
            total_count                         = MerchantUser.count_with_condition_query(
                                                                    query, 
                                                                    limit=limit)
        
            (search_results, next_cursor)       = MerchantUser.list_all_with_condition_query(
                                                                    query, 
                                                                    offset=offset, 
                                                                    start_cursor=start_cursor, 
                                                                    return_with_cursor=True, 
                                                                    limit=limit)
            
            return (search_results, total_count, next_cursor)   
        
        '''    
        total_count                         = MerchantUser.full_text_count(search_text_list, query, conf.MAX_FETCH_RECORD_FULL_TEXT_SEARCH)
        
        (search_results, next_cursor)       = MerchantUser.full_text_search(search_text_list, query, offset=offset, 
                                                                   start_cursor=start_cursor, return_with_cursor=True, 
                                                                   limit=limit)
        
        return (search_results, total_count, next_cursor)
        '''
         
            
    
    
class MerchantTagging(Tagging):    
    
    @staticmethod
    def create(merchant_acct, label=None, desc=None):
        return MerchantTagging.create_tag(parent=merchant_acct.create_ndb_key(), label=label, desc=desc)
    
    def update(self, label=None, desc=None):
        self.label  = label
        self.desc   = desc
        self.put()
        
    @staticmethod
    def list_by_merchant_account(merchant_acct):
        return MerchantTagging.query(ancestor = merchant_acct.create_ndb_key()).fetch(limit = conf.MAX_FETCH_RECORD)
    
    @staticmethod
    def get_by_merchant_label(merchant_acct, label):
        return MerchantTagging.get_by_label(merchant_acct.create_ndb_key(), label)
    

class ReceiptSetup(BaseNModel,DictModel):
    receipt_header_settings = ndb.JsonProperty()
    receipt_footer_settings = ndb.JsonProperty()
    modified_datetime       = ndb.DateTimeProperty(auto_now=True)
    
    
    dict_properties = ['receipt_header_settings', 'receipt_footer_settings']
    
    @staticmethod
    def create(merchant_acct, receipt_header_settings={}, receipt_footer_settings={}):
        receipt_setup = ReceiptSetup(
                                        parent                  = merchant_acct.create_ndb_key(),
                                        receipt_header_settings = receipt_header_settings,    
                                        receipt_footer_settings = receipt_footer_settings,
                                        )
        receipt_setup.put() 
        
        return receipt_setup
    
    @staticmethod
    def update(receipt_setup, receipt_header_settings={}, receipt_footer_settings={}):
        receipt_setup.receipt_header_settings      = receipt_header_settings
        receipt_setup.receipt_footer_settings      = receipt_footer_settings
            
        receipt_setup.put() 
        
        return receipt_setup   
    
    @staticmethod    
    def remove(receipt_setup):
        receipt_setup.delete()
        
    @staticmethod
    def get_by_merchant_acct(merchant_acct):
        return ReceiptSetup.query(ancestor = merchant_acct.create_ndb_key()).get()   
    
class ServiceTaxSetup(BaseNModel,DictModel):
    tax_reg_id              = ndb.StringProperty(required=True)
    tax_name                = ndb.StringProperty(required=True)
    tax_label               = ndb.StringProperty(required=True)
    tax_apply_type          = ndb.StringProperty(required=True)
    tax_pct_amount          = ndb.FloatProperty(required=True)
    assigned_outlet_list    = ndb.JsonProperty()
    is_publish              = ndb.BooleanProperty(default=False)
    modified_datetime       = ndb.DateTimeProperty(auto_now=True)
    
    
    dict_properties = ['tax_reg_id', 'tax_name', 'tax_label', 'tax_apply_type', 'tax_pct_amount', 'assigned_outlet_list', 'is_publish']
    
    @staticmethod
    def create(tax_reg_id, tax_name, tax_label, tax_apply_type, tax_pct_amount, assigned_outlet_key_list, merchant_acct):
        service_tax_setup = ServiceTaxSetup(
                                        parent                  = merchant_acct.create_ndb_key(),
                                        tax_reg_id              = tax_reg_id,    
                                        tax_name                = tax_name,
                                        tax_label               = tax_label,  
                                        tax_apply_type          = tax_apply_type,    
                                        tax_pct_amount          = tax_pct_amount,
                                        is_publish              = False,
                                        assigned_outlet_list    = assigned_outlet_key_list,
                                        )
        service_tax_setup.put()
        return service_tax_setup
    
    @staticmethod
    def update(service_tax_setup, tax_reg_id, tax_name, tax_label, tax_apply_type, tax_pct_amount, assigned_outlet_key_list):
        service_tax_setup.tax_reg_id            = tax_reg_id
        service_tax_setup.tax_name              = tax_name
        service_tax_setup.tax_label             = tax_label
        service_tax_setup.tax_apply_type        = tax_apply_type
        service_tax_setup.tax_pct_amount        = tax_pct_amount
        service_tax_setup.assigned_outlet_list  = assigned_outlet_key_list
        service_tax_setup.is_publish            = False
        service_tax_setup.put()
    
    @staticmethod    
    def remove(service_tax_setup):
        service_tax_setup.delete()
        
    @model_transactional(desc='ServiceTaxSetup.publish')   
    def publish(self):
        self.is_publish          = True  
          
        for outlet_key in self.assigned_outlet_list:
            Outlet.add_tax_setup(outlet_key,
                                    {
                                     'tax_reg_id'       : self.tax_reg_id,
                                     'tax_label'        : self.tax_label,
                                     'tax_apply_type'   : self.tax_apply_type,
                                     'tax_pct_amount'   : self.tax_pct_amount,   
                                    })
            
        
        self.put()
            
    @model_transactional(desc='ServiceTaxSetup.unpublish')   
    def unpublish(self):
        self.is_publish          = False  
          
        for outlet_key in self.assigned_outlet_list:
            Outlet.remove_tax_setup(outlet_key, self.tax_reg_id)
            
        
        self.put()        
        
    @staticmethod
    def list_by_merchant_acct(merchant_acct):
        return ServiceTaxSetup.query(ancestor = merchant_acct.create_ndb_key()).fetch(limit=conf.MAX_FETCH_RECORD)

class BannerFile(BaseNModel, DictModel):
    '''
    Merchant Account as ancestor
    '''
    banner_file_type                = ndb.StringProperty(required=True)
    banner_file_public_url          = ndb.StringProperty(required=True)
    banner_file_storage_filename    = ndb.StringProperty(required=True)
    sequence                        = ndb.IntegerProperty(required=False, default=0)
    
    dict_properties = ['banner_file_public_url', 'banner_file_storage_filename', 'banner_file_type', 'sequence']
    
    @staticmethod
    def list_by_merchant_acct(merchant_acct):
        result = BannerFile.query(ancestor=merchant_acct.create_ndb_key()).fetch(limit=conf.MAX_FETCH_RECORD)
        return result
    
    @staticmethod
    def upload_file(uploading_file, merchant_acct, bucket, banner_file_type=None):
        file_prefix                         = random_string(8)
        banner_file_storage_filename       = 'merchant/'+merchant_acct.key_in_str+'/banner/'+file_prefix+'-'+uploading_file.filename
        blob                                = bucket.blob(banner_file_storage_filename)
        
        logger.debug('banner_file_storage_filename=%s', banner_file_storage_filename)
        
        blob.upload_from_string(
                uploading_file.read(),
                content_type=uploading_file.content_type
            )
        
        uploaded_url        = blob.public_url
        
        logger.debug('banner_file_type=%s', uploaded_url)
        logger.debug('product_file_type=%s', banner_file_type)
        
        count = BannerFile.query(ancestor=merchant_acct.create_ndb_key()).count()
        
        banner_file = BannerFile(
                            parent = merchant_acct.create_ndb_key(),
                            banner_file_public_url              = uploaded_url,
                            banner_file_storage_filename        = banner_file_storage_filename,
                            banner_file_type                    = banner_file_type,
                            sequence                            = count+1,
                            )
        
        banner_file.put()
        
        return banner_file
    
    @staticmethod
    def remove_file(banner_file, bucket):
        
        old_logo_blob = bucket.get_blob(banner_file.banner_file_storage_filename) 
        if old_logo_blob:
            old_logo_blob.delete()
            banner_file.delete()   
            
             
