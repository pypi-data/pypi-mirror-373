'''
Created on 25 Sep 2023

@author: jacklok
'''
import logging
from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel
from google.cloud import ndb
from datetime import datetime
from trexconf import program_conf, conf as model_conf
from trexmodel.models.datastore.merchant_models import MerchantUser,\
    MerchantAcct
from trexlib.utils.string_util import is_not_empty, is_empty
from trexmodel.models.datastore.model_decorators import model_transactional
from trexconf.program_conf import REDEMPTION_CATALOGUE_STATUS_DEFINED_CATALOGUE,\
    REDEMPTION_CATALOGUE_STATUS_NEW, REDEMPTION_CATALOGUE_STATUS_PUBLISH
from trexlib.utils.common.common_util import sort_list
from audioop import reverse

logger = logging.getLogger('model')

class RedemptionCatalogue(BaseNModel, DictModel):
    #merchant_acct                       = ndb.KeyProperty(name="merchant_acct", kind=MerchantAcct)
    label                               = ndb.StringProperty(required=True)
    desc                                = ndb.StringProperty(required=False)
    redeem_reward_format                = ndb.StringProperty(required=True, choices=set(program_conf.REDEEM_REWARD_FORMAT_GROUP))
    completed_status                    = ndb.StringProperty(required=True, choices=set(program_conf.REDEMPTION_CATALOGUE_STATUS))
    start_date                          = ndb.DateProperty(required=True)
    end_date                            = ndb.DateProperty(required=True)
    created_datetime                    = ndb.DateTimeProperty(required=True, auto_now_add=True)
    modified_datetime                   = ndb.DateTimeProperty(required=True, auto_now=True)
    
    published_datetime                  = ndb.DateTimeProperty(required=False)
    archived_datetime                   = ndb.DateTimeProperty(required=False)
    
    catalogue_settings                  = ndb.JsonProperty(required=True)
    
    created_by                          = ndb.KeyProperty(name="created_by", kind=MerchantUser)
    created_by_username                 = ndb.StringProperty(required=False)
    modified_by                         = ndb.KeyProperty(name="modified_by", kind=MerchantUser)
    modified_by_username                = ndb.StringProperty(required=False)
    
    enabled                             = ndb.BooleanProperty(required=True, default=True)
    archived                            = ndb.BooleanProperty(required=True, default=False)
    
    image_storage_filename              = ndb.StringProperty(required=False)
    image_public_url                    = ndb.StringProperty(required=False)
    
    loyalty_package                    = ndb.StringProperty(required=False, default=program_conf.LOYALTY_PACKAGE_SCALE)
    
    dict_properties = [
                        "label","desc","completed_status","start_date","end_date","created_datetime",
                        "redeem_reward_format","catalogue_settings", "image_storage_filename", "image_public_url",
                        "exclusive_tags_list", "exclusive_memberships_list", "exclusive_tier_memberships_list", 'partner_exclusive',
                        "completed_progress_in_percentage","completed_status_index", "catalogue_items",
                        "is_enabled", "is_disabled", "is_archived", "is_published", "loyalty_package", "is_expired",
                        ]
    
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
    def is_expired(self):
        return self.end_date<datetime.today().date()
    
    @property
    def is_effectived(self):
        return self.start_date<=datetime.today().date()
    
    @property
    def is_published(self):
        return self.completed_status == program_conf.PROGRAM_STATUS_PUBLISH
    
    @property
    def merchant_acct(self):
        return MerchantAcct.fetch(self.key.parent().urlsafe())
    
    @property
    def partner_exclusive(self):
        if self.catalogue_settings.get('exclusivity') and self.catalogue_settings.get('exclusivity').get('partner_exclusive'):
            return True
        else:
            return False
        
    
    @property
    def exclusive_tags_list(self):
        if self.catalogue_settings.get('exclusivity') and self.catalogue_settings.get('exclusivity').get('tags'):
            return self.catalogue_settings.get('exclusivity').get('tags') or []
        else:
            return []
        
    @property
    def exclusive_memberships_list(self):
        if self.catalogue_settings.get('exclusivity') and self.catalogue_settings.get('exclusivity').get('memberships'):
            return self.catalogue_settings.get('exclusivity').get('memberships') or []
        else:
            return []
        
    @property
    def exclusive_tier_memberships_list(self):
        if self.catalogue_settings.get('exclusivity') and self.catalogue_settings.get('exclusivity').get('tier_memberships'):
            return self.catalogue_settings.get('exclusivity').get('tier_memberships') or []
        else:
            return []
    
    @property
    def catalogue_items(self):
        return self.catalogue_settings.get('items') or []
    
    @property
    def completed_progress_in_percentage(self):
        return program_conf.redemption_catalogue_completed_progress_percentage(self.completed_status, self.loyalty_package)
    
    @property
    def completed_status_index(self):
        return program_conf.get_redemption_catalogue_completed_status_index(self.completed_status)
    
    @property
    def merchant_account_entity(self):
        return self.key.parent().get()
    
    @staticmethod
    def create(merchant_acct, label=None, desc=None, start_date=None, end_date=None, redeem_reward_format=None, 
               created_by=None, loyalty_package=program_conf.LOYALTY_PACKAGE_SCALE):
        
        created_by_username = None
        if is_not_empty(created_by):
            if isinstance(created_by, MerchantUser):
                created_by_username = created_by.username
                
        redemption_catalogue = RedemptionCatalogue(
                                parent              = merchant_acct.create_ndb_key(),
                                label               = label,
                                desc                = desc,
                                start_date          = start_date,
                                end_date            = end_date,
                                redeem_reward_format= redeem_reward_format,
                                created_by          = created_by.create_ndb_key(),
                                created_by_username = created_by_username,
                                completed_status    = program_conf.REDEMPTION_CATALOGUE_STATUS_DEFINED_CATALOGUE,
                                catalogue_settings  = {},
                                loyalty_package     = loyalty_package,
                                )
        
        redemption_catalogue.put()
        
        return redemption_catalogue
    
    @staticmethod
    def update(redemption_catalogue, label=None, desc=None, start_date=None, end_date=None, 
               redeem_reward_format=None, modified_by=None, loyalty_package=program_conf.LOYALTY_PACKAGE_SCALE):
        
        modified_by_username = None
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
                
        redemption_catalogue.label                  = label
        redemption_catalogue.desc                   = desc
        redemption_catalogue.start_date             = start_date
        redemption_catalogue.end_date               = end_date
        redemption_catalogue.redeem_reward_format   = redeem_reward_format
        redemption_catalogue.completed_status       = program_conf.REDEMPTION_CATALOGUE_STATUS_DEFINED_CATALOGUE
        
        redemption_catalogue.modified_by            = modified_by.create_ndb_key()
        redemption_catalogue.modified_by_username   = modified_by_username
        redemption_catalogue.loyalty_package        = loyalty_package
        
        redemption_catalogue.put()
        
        return redemption_catalogue
    
    
    def clone(self, created_by=None, **overrides):
        created_datetime = datetime.utcnow();
        overrides.setdefault('created_datetime', created_datetime)
        overrides.setdefault('modified_datetime', created_datetime)
        overrides.setdefault('published_datetime', None)
        overrides.setdefault('archived_datetime', None)
        overrides.setdefault('completed_status', REDEMPTION_CATALOGUE_STATUS_NEW)
        
        created_by_username = None
        if is_not_empty(created_by):
            if isinstance(created_by, MerchantUser):
                created_by_username = created_by.username
                
        overrides.setdefault('created_by', created_by.create_ndb_key())        
        overrides.setdefault('created_by_username', created_by_username)        
        
        new_cloned = super().clone(parent=self.key.parent(), **overrides)
        return new_cloned
    
    def remove_redemption_catalogue_item(self, voucher_index, modified_by=None):
        modified_by_username = None
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
                
        
        catalogue_settings = self.catalogue_settings
        
        items = catalogue_settings.get('items')
        if is_not_empty(items):
            items = [item for item in items if item.get('voucher_index') != voucher_index]
            
        catalogue_settings['items'] = items
        
        self.catalogue_settings     = catalogue_settings
        
        self.modified_by            = modified_by.create_ndb_key()
        self.modified_by_username   = modified_by_username
        
        self.put()
    
    def update_redemption_catalogue_image(self, image_public_url=None, image_storage_filename=None, modified_by=None):
        
        modified_by_username = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        self.image_public_url       = image_public_url
        self.image_storage_filename = image_storage_filename
        
        self.modified_by            = modified_by.create_ndb_key()
        self.modified_by_username   = modified_by_username
        
        self.completed_status       = program_conf.REDEMPTION_CATALOGUE_STATUS_UPLOAD_MATERIAL
        self.put()
        
    def completed_redemption_catalogue_image_status(self, modified_by=None, default_redemption_catalogue_image=None):
        modified_by_username    = None              
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username

        
        if is_empty(self.image_public_url):
            self.image_public_url = default_redemption_catalogue_image
          
        self.modified_by            = modified_by.create_ndb_key()
        self.modified_by_username   = modified_by_username
        self.completed_status       = program_conf.REDEMPTION_CATALOGUE_STATUS_UPLOAD_MATERIAL
        self.put()      
    
    def add_redemption_catalogue_item(self, item_settings, modified_by=None):
        modified_by_username = None
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
                
        
        catalogue_settings = self.catalogue_settings
        
        items = catalogue_settings.get('items')
        if items is None:
            items = []
        
        items.append(item_settings)
        
        catalogue_settings['items'] = items
        
        self.catalogue_settings     = catalogue_settings
        
        self.modified_by            = modified_by.create_ndb_key()
        self.modified_by_username   = modified_by_username
        
        self.put()
    
    @model_transactional(desc="update_redemption_catalogue_exclusivity")    
    def update_redemption_catalogue_exclusivity(self, exclusivity_configuration, modified_by=None):
        modified_by_username = None
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
                
        
        catalogue_settings = self.catalogue_settings
        catalogue_settings['exclusivity'] = exclusivity_configuration
        
        self.catalogue_settings     = catalogue_settings
        
        self.modified_by            = modified_by.create_ndb_key()
        self.modified_by_username   = modified_by_username
        
        self.completed_status       = program_conf.REDEMPTION_CATALOGUE_STATUS_DEFINE_EXCLUSIVITY
        
        self.put()    
        
    
    @model_transactional(desc="complete_adding_redemption_catalogue_item")
    def complete_adding_redemption_catalogue_item(self, modified_by=None):
        modified_by_username = None
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        self.completed_status = program_conf.REDEMPTION_CATALOGUE_STATUS_DEFINE_ITEM
        self.modified_by            = modified_by.create_ndb_key()
        self.modified_by_username   = modified_by_username
        
        self.put()
    
    
    @model_transactional(desc="publish_redemption_catalogue")
    def publish_redemption_catalogue(self, modified_by=None):
        modified_by_username = None
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
            self.modified_by            = modified_by.create_ndb_key()
        
        self.completed_status       = program_conf.REDEMPTION_CATALOGUE_STATUS_PUBLISH
        self.published_datetime     = datetime.utcnow()
        
        self.modified_by_username   = modified_by_username
        self.put()
        
        catalogue_configuration = self.to_configuration()
        
        logger.debug('catalogue_configuration=%s', catalogue_configuration)

        if self.partner_exclusive == False:
            merchant_acct = self.merchant_acct
            merchant_acct.update_published_redemption_catalogue(catalogue_configuration)
    
    @model_transactional(desc="enable redemption catalogue")
    def enable(self, modified_by=None):
        self.enabled = True
        
        modified_by_username = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        self.modified_by            = modified_by.create_ndb_key()
        self.modified_by_username   = modified_by_username
        
        self.put()
        
        if self.is_published:
            if self.partner_exclusive == False:
                merchant_acct = self.merchant_acct
                merchant_acct.update_published_redemption_catalogue(self.to_configuration())
            
            
            
        
    @model_transactional(desc="disable redemption catalogue")
    def disable(self, modified_by=None):
        self.enabled = False
        
        modified_by_username = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
                self.modified_by            = modified_by.create_ndb_key()
                
        self.modified_by_username   = modified_by_username
        
        self.put()  

        if self.partner_exclusive == False:
            merchant_acct = self.merchant_acct
            merchant_acct.remove_redeption_catalogue(self.key_in_str)
        
    @model_transactional(desc="archive redemption catal0gue")
    def archive(self, modified_by=None):
        self.archived = True
        
        modified_by_username = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
                self.modified_by            = modified_by.create_ndb_key()
                
        self.modified_by_username   = modified_by_username
        self.archived_datetime      = datetime.utcnow()
        self.put()  
        
        if self.partner_exclusive == False:
            merchant_acct = self.merchant_acct
            merchant_acct.remove_redeption_catalogue(self.key_in_str)    
        
    def to_configuration(self):
        catalogue_configuration = {
                                'merchant_acct_key'                 : self.parent_key,
                                'catalogue_key'                     : self.key_in_str,
                                'label'                             : self.label,
                                'desc'                              : self.desc,
                                'image_url'                         : self.image_public_url,
                                'redeem_reward_format'              : self.redeem_reward_format,
                                'start_date'                        : self.start_date.strftime('%d-%m-%Y'),
                                'end_date'                          : self.end_date.strftime('%d-%m-%Y'),    
                                'items'                             : self.catalogue_settings.get('items'),
                                'exclusivity'                       : {
                                                                        'tags'              : self.exclusive_tags_list,
                                                                        'memberships'       : self.exclusive_memberships_list,
                                                                        'tier_memberships'  : self.exclusive_tier_memberships_list,
                                                                        'partner_exclusive' : self.partner_exclusive,
                                                                        },
                                }
        
        return catalogue_configuration    
        
    @staticmethod
    @model_transactional(desc="archive_redemption_catalogue")
    def archive_redemption_catalogue(redemption_catalogue):
        redemption_catalogue.archived = True
        redemption_catalogue.archived_datetime = datetime.now()
        redemption_catalogue.put()
        
        if redemption_catalogue.partner_exclusive == False:
            merchant_acct = redemption_catalogue.merchant_acct
            merchant_acct.remove_archieve_redemption_catalogue(redemption_catalogue.key_in_str) 
        
    @staticmethod
    def list_by_merchant_account(merchant_acct):
        result = RedemptionCatalogue.query(ndb.AND(RedemptionCatalogue.archived!=True), ancestor=merchant_acct.create_ndb_key()).fetch(limit=model_conf.MAX_FETCH_RECORD)

        sorted_result = sort_list(result, 'modified_datetime', reverse_order=True)
        return sorted_result
    
    @staticmethod
    def list_archived_by_merchant_account(merchant_acct):
        result = RedemptionCatalogue.query(ndb.AND(RedemptionCatalogue.archived==True), ancestor=merchant_acct.create_ndb_key()).fetch(limit=model_conf.MAX_FETCH_RECORD)    

        sorted_result = sort_list(result, 'modified_datetime', reverse_order=True)
        return sorted_result
    
    @staticmethod
    def list_published_by_merchant_account(merchant_acct):
        result = RedemptionCatalogue.query(ndb.AND(RedemptionCatalogue.completed_status==REDEMPTION_CATALOGUE_STATUS_PUBLISH), ancestor=merchant_acct.create_ndb_key()).fetch(limit=model_conf.MAX_FETCH_RECORD)

        sorted_result = sort_list(result, 'modified_datetime', reverse_order=True)
        return sorted_result
    
    @staticmethod
    def list_published_partner_exclusive_by_merchant_account(merchant_acct):
        result = RedemptionCatalogue.query(ndb.AND(RedemptionCatalogue.completed_status==REDEMPTION_CATALOGUE_STATUS_PUBLISH), ancestor=merchant_acct.create_ndb_key()).fetch(limit=model_conf.MAX_FETCH_RECORD)
        partner_exclusive_list = []
        for r in result:
            if r.partner_exclusive:
                partner_exclusive_list.append(r)
        return partner_exclusive_list
        #sorted_result = sort_list(partner_exclusive_list, 'modified_datetime', reverse_order=True)
        #return sorted_result
