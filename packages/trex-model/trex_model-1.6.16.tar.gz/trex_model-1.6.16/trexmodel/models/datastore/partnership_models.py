'''
Created on 6 May 2025

@author: jacklok
'''

from google.cloud import ndb
from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel
import logging
from trexmodel.models.datastore.merchant_models import MerchantAcct,\
    MerchantUser
from trexconf import program_conf, conf
from datetime import datetime, timedelta
from trexlib.utils.string_util import is_not_empty
from trexmodel.models.datastore.redemption_catalogue_models import RedemptionCatalogue
from trexmodel.models.merchant_helpers import convert_points_between_merchants
from trexmodel.models.datastore.user_models import User
from trexlib.utils.common.cache_util import setCache, getFromCache,\
    deleteFromCache
from trexlib.utils.common.date_util import convert_date_to_datetime



logger = logging.getLogger('target_debug')

class PartnershipSettings(BaseNModel, DictModel):
    '''
    Merchant account as ancestor
    '''
    point_worth_value_in_currency   = ndb.FloatProperty(required=True, default=.0)
    is_enabled                      = ndb.BooleanProperty(default=False)
    modified_datetime               = ndb.DateTimeProperty(auto_now=True)
    
    dict_properties = ['point_worth_value_in_currency', 'is_enabled', ]
    
    @staticmethod
    def create(merchant_acct, is_enabled=False, point_worth_value_in_currency=.0):
        
        partnership_settings = PartnershipSettings.get_by_merchant_acct(merchant_acct)
        if partnership_settings:
            partnership_settings.point_worth_value_in_currency  = point_worth_value_in_currency
            partnership_settings.is_enabled                     = is_enabled
            
            deleteFromCache('PartnershipSettings-%s'%merchant_acct.key_in_str)
            
        else:
            partnership_settings = PartnershipSettings(
                                    parent                          = merchant_acct.create_ndb_key(),
                                    point_worth_value_in_currency   = point_worth_value_in_currency,
                                    is_enabled                      = is_enabled,
                                    )
        partnership_settings.put()
        
        setCache('PartnershipSettings-%s'%merchant_acct.key_in_str, partnership_settings, timeout=3000)
        return partnership_settings
    
    @staticmethod    
    def get_by_merchant_acct(merchant_acct):
        result_from_cache = getFromCache('PartnershipSettings-%s'%merchant_acct.key_in_str)
        if result_from_cache is None:
            result = PartnershipSettings.query(ancestor=merchant_acct.create_ndb_key()).get()
            logger.debug('PartnershipSettings.get_by_merchant_acct debug: result=%s', result)
            return result
        else:
            return result_from_cache
    
class PartnerLinked(BaseNModel, DictModel):
    '''
    Merchant account as ancestor
    '''
    partner_merchant_acct           = ndb.KeyProperty(name="partner_merchant_acct", kind=MerchantAcct)
    partner_company_name            = ndb.StringProperty(required=False)
    partner_account_code            = ndb.StringProperty(required=False)
    desc                            = ndb.StringProperty(required=False)
    
    start_date                      = ndb.DateProperty(required=True)
    end_date                        = ndb.DateProperty(required=True)
    
    partnership_configuration       = ndb.JsonProperty()
    
    status                          = ndb.StringProperty(required=True)
    enabled                         = ndb.BooleanProperty(default=True)
    archived                        = ndb.BooleanProperty(default=False)
    created_datetime                = ndb.DateTimeProperty(required=True, auto_now_add=True)
    modified_datetime               = ndb.DateTimeProperty(auto_now=True)
    requested_datetime              = ndb.DateTimeProperty(required=False)
    approved_datetime               = ndb.DateTimeProperty(required=False)
    
    created_by                      = ndb.KeyProperty(name="created_by", kind=MerchantUser)
    created_by_username             = ndb.StringProperty(required=False)
    modified_by                     = ndb.KeyProperty(name="modified_by", kind=MerchantUser)
    modified_by_username            = ndb.StringProperty(required=False)
    requested_by                    = ndb.KeyProperty(name="requested_by", kind=MerchantUser)
    requested_by_username           = ndb.StringProperty(required=False)
    approved_by                     = ndb.KeyProperty(name="approved_by", kind=MerchantUser)
    approved_by_username            = ndb.StringProperty(required=False)
    
    dict_properties = ['partner_merchant_acct', 'partner_company_name', 'partner_account_code', 'partner_merchant_key',
                       'status', 'enabled', 'is_approved', 'is_requested', 'start_date', 'end_date', 'desc',
                       'partnership_configuration', 'partnership_key', 'redemption_catalogue_list',
                       'limit_redeem', 'requested_from_merchant_entity',
                       'created_datetime', 'modified_datetime', 'approved_datetime',
                       ]
    
    @property
    def is_approved(self):
        return self.status==program_conf.MERCHANT_PARTNERSHIP_STATUS_APPROVED;
    
    @property
    def is_requested(self):
        return self.status==program_conf.MERCHANT_PARTNERSHIP_STATUS_REQUESTED;
    
    @property
    def is_archived(self):
        return self.archived==True;
    
    @property
    def partnership_key(self):
        return self.key.urlsafe().decode('utf-8')
    
    @property
    def partner_merchant_key(self):
        return self.partner_merchant_acct.urlsafe().decode('utf-8')
    
    @property
    def merchant_key(self):
        return self.key.parent().urlsafe().decode('utf-8')
    
    @property
    def partner_merchant_entity(self):
        return self.partner_merchant_acct.get()
    
    @property
    def merchant_entity(self):
        return self.key.parent().get()
    
    @property
    def requested_from_merchant_entity(self):
        return self.key.parent().get()
    
    @property
    def redemption_catalogue_list(self):
        if self.partnership_configuration:
            return self.partnership_configuration.get('redemption_catalogue_list',[])
        else:
            return []
    
    @property
    def limit_redeem(self):
        if self.partnership_configuration:
            return self.partnership_configuration.get('limit_redeem',False)
        else:
            return False
    
    @property
    def limit_redeem_configuration_list(self):
        return self.partnership_configuration.get('limit_redeem_configuration_list',[])
    
    @staticmethod
    def create(merchant_acct, partner_merchant_acct, start_date, end_date, created_by=None, desc=None, status=program_conf.MERCHANT_PARTNERSHIP_STATUS_LINKED):
        created_by_username = None
        if is_not_empty(created_by):
            if isinstance(created_by, MerchantUser):
                created_by_username = created_by.username
                
        partnership_linked = PartnerLinked(
                                parent                          = merchant_acct.create_ndb_key(),
                                partner_merchant_acct           = partner_merchant_acct.create_ndb_key(),
                                partner_company_name            = partner_merchant_acct.company_name,
                                partner_account_code            = partner_merchant_acct.account_code,
                                enabled                         = True,
                                status                          = status,
                                desc                            = desc,
                                start_date                      = start_date,
                                end_date                        = end_date,
                                created_by                      = created_by.create_ndb_key(),
                                created_by_username             = created_by_username,
                                )
        partnership_linked.put()
        return partnership_linked
    
    @staticmethod
    def update(partnership, partner_merchant_acct, start_date, end_date, desc=None, modified_by=None,status=program_conf.MERCHANT_PARTNERSHIP_STATUS_LINKED):
        modified_by_username = None
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
                
        partnership.partner_merchant_acct   = partner_merchant_acct.create_ndb_key()
        partnership.partner_company_name    = partner_merchant_acct.company_name
        partnership.partner_account_code    = partner_merchant_acct.account_code
        partnership.status                  = status
        partnership.desc                    = desc
        partnership.start_date              = start_date
        partnership.end_date                = end_date
        partnership.modified_by             = modified_by.create_ndb_key()
        partnership.modified_by_username    = modified_by_username
        
        
        partnership.put()
        
    def update_configuration(self, redemption_catalogue_list, limit_redeem=False):
        self.status                  = program_conf.MERCHANT_PARTNERSHIP_STATUS_REDEEM_CONFIGURED
        self.partnership_configuration = {
                                                'redemption_catalogue_list' : redemption_catalogue_list,
                                                'limit_redeem'              : limit_redeem,
                                                }
        self.put()    
    
    @staticmethod
    def submit_request(partnership, requested_by=None):
        requested_by_username = None
        if is_not_empty(requested_by):
            if isinstance(requested_by, MerchantUser):
                requested_by_username = requested_by.username
                
        partnership.status                   = program_conf.MERCHANT_PARTNERSHIP_STATUS_REQUESTED
        partnership.requested_datetime       = datetime.utcnow()
        partnership.requested_by             = requested_by.create_ndb_key()
        partnership.requested_by_username    = requested_by_username
        partnership.put()
    
    @staticmethod    
    def approve_request(partnership, approved_by=None):
        approved_by_username = None
        if is_not_empty(approved_by):
            if isinstance(approved_by, MerchantUser):
                approved_by_username = approved_by.username
                
        partnership.status                  = program_conf.MERCHANT_PARTNERSHIP_STATUS_APPROVED
        partnership.approved_datetime       = datetime.utcnow()
        partnership.approved_by             = approved_by.create_ndb_key()
        partnership.approved_by_username    = approved_by_username
        partnership.put()    
        
        partner_merchant_account = partnership.partner_merchant_entity
        
        redemption_catalogue_configurations_list = partnership.create_redemption_catalogue_configurations_list()
        for configuration in redemption_catalogue_configurations_list:
            partner_merchant_account.update_approved_partner_redemption_catalogue(configuration)
        
    @staticmethod    
    def list_from_merchant_by_merchant_acct(merchant_acct, archived=False):
        result = PartnerLinked.query(ancestor=merchant_acct.create_ndb_key()).fetch()
        filtered_result = []
        for r in result:
            if r.archived==archived:
                filtered_result.append(r)
        return filtered_result
    
    @staticmethod    
    def list_from_partner_by_merchant_acct(merchant_acct, archived=False):
        result = PartnerLinked.query(ndb.AND(PartnerLinked.partner_merchant_acct==merchant_acct.create_ndb_key())).fetch()
        filtered_result = []
        for r in result:
            if r.archived==archived:
                filtered_result.append(r)
        return filtered_result
    
    def create_redemption_catalogue_configurations_list(self):
        partnership_redemption_catalogue_list = []
        catalogue_list  = RedemptionCatalogue.list_published_partner_exclusive_by_merchant_account(self.merchant_entity)
        for catalogue in catalogue_list:
            for c in self.redemption_catalogue_list:
                if catalogue.key_in_str == c:
                    partnership_redemption_catalogue_list.append(catalogue)
        
        partner_partnership_settings            = PartnershipSettings.get_by_merchant_acct(self.partner_merchant_entity)
        merchant_partnership_settings           = PartnershipSettings.get_by_merchant_acct(self.merchant_entity)
        
        logger.debug('partner_partnership_settings=%s', partner_partnership_settings)
        logger.debug('merchant_partnership_settings=%s', merchant_partnership_settings)
        
        catalogue_configurations_list = []
        
        if partner_partnership_settings:
        
            partner_point_worth_value_in_currency   = partner_partnership_settings.point_worth_value_in_currency
            merchant_point_worth_value_in_currency  = merchant_partnership_settings.point_worth_value_in_currency
            
            for catalogue in partnership_redemption_catalogue_list:
                configuration = catalogue.to_configuration()
                configuration['merchant_acct_key'] = self.merchant_key
                
                for catalogue_item  in configuration['items']:
                    redeem_reward_amount = catalogue_item['redeem_reward_amount']
                    catalogue_item['redeem_reward_amount'] = convert_points_between_merchants(redeem_reward_amount, merchant_point_worth_value_in_currency, partner_point_worth_value_in_currency)
                catalogue_configurations_list.append(configuration)
                
        return catalogue_configurations_list
    
    def disable(self):
        self.enabled = False
        logger.debug('going to remove partner program if found')
        partner_merchant_account = self.partner_merchant_entity
        if partner_merchant_account:
            logger.debug('partner company=%s', partner_merchant_account.company_name)
            
            partner_merchant_account.remove_partner_merchant_configuration(self.merchant_key)
            
            for catalogue_key in self.redemption_catalogue_list:
                partner_merchant_account.remove_partner_redeption_catalogue(catalogue_key)
        
        self.put()
        
    def enable(self):
        self.enabled = True
        logger.debug('going to add partner program')
        merchant_account            = self.merchant_entity
        partner_merchant_account    = self.partner_merchant_entity
        if partner_merchant_account:
            partner_merchant_account.update_partner_merchant_configuration(merchant_account.partner_configuration)
            partner_merchant_account.put()
            logger.debug('partner company=%s', partner_merchant_account.company_name)
            
            redemption_catalogue_configurations_list = self.create_redemption_catalogue_configurations_list()
            if redemption_catalogue_configurations_list:
                for configuration in redemption_catalogue_configurations_list:
                    partner_merchant_account.update_approved_partner_redemption_catalogue(configuration)
        
        self.put()    

class PartnershipRewardTransaction(BaseNModel, DictModel):
    '''
    This is used to record convert merchant point to partner merchant point
    '''
    merchant_acct                               = ndb.KeyProperty(name="merchant_acct", kind=MerchantAcct)
    partner_merchant_acct                       = ndb.KeyProperty(name="partner_merchant_acct", kind=MerchantAcct)
    
    merchant_point_worth_value_in_currency      = ndb.FloatProperty(required=True, default=.0)
    partner_point_worth_value_in_currency       = ndb.FloatProperty(required=True, default=.0)
    
    transact_point_amount                       = ndb.FloatProperty(required=True)
    transact_datetime                           = ndb.DateTimeProperty(required=True, auto_now_add=True)
    
    user_acct                                   = ndb.KeyProperty(name="user_acct", kind=User)
    transaction_id                              = ndb.StringProperty(required=True)
    reward_summary                              = ndb.JsonProperty()
    
    is_revert                                   = ndb.BooleanProperty(required=False, default=False)
    reverted_datetime                           = ndb.DateTimeProperty(required=False)
    reverted_by                                 = ndb.KeyProperty(name="reverted_by", kind=MerchantUser)
    reverted_by_username                        = ndb.StringProperty(required=False)
    
    dict_properties = [
                        'partner_merchant_acct_key', 'merchant_point_worth_value_in_currency', 'partner_point_worth_value_in_currency',
                        'transact_point_amount', 'transact_datetime', 'reward_summary', 'transaction_id',
                        ]
    
    @property
    def merchant_acct_key(self):
        return self.merchant_acct.urlsafe().decode('utf-8')
    
    @property
    def partner_merchant_acct_key(self):
        return self.partner_merchant_acct.urlsafe().decode('utf-8')
    
    @property
    def merchant_acct_entity(self):
        return self.merchant_acct.get()
    
    @property
    def partner_merchant_acct_entity(self):
        return self.partner_merchant_acct.get()
    
    @property
    def user_acct_entity(self):
        return self.user_acct.get()
    
    @property
    def user_acct_reference_code(self):
        return self.user_acct_entity.reference_code
    
    def convertion_rate(self)->float:
        return self.merchant_point_worth_value_in_currency/self.partner_point_worth_value_in_currency
    
    @staticmethod
    def create(merchant_acct, partner_merchant_acct, user_acct, transact_point_amount, reward_summary=None):
        merchant_artnership_settings = PartnershipSettings.get_by_merchant_acct(merchant_acct)
        partner_partnership_settings = PartnershipSettings.get_by_merchant_acct(partner_merchant_acct)
        
        if merchant_artnership_settings is not None and partner_partnership_settings is not None and merchant_artnership_settings.is_enabled and partner_partnership_settings.is_enabled: 
            merchant_point_worth_value_in_currency      = merchant_artnership_settings.point_worth_value_in_currency
            partner_point_worth_value_in_currency       = partner_partnership_settings.point_worth_value_in_currency
            partnership_reward_transaction = PartnershipRewardTransaction(
                                                merchant_acct           = merchant_acct.create_ndb_key(),
                                                partner_merchant_acct   = partner_merchant_acct.create_ndb_key(),
                                                
                                                merchant_point_worth_value_in_currency  = merchant_point_worth_value_in_currency,
                                                partner_point_worth_value_in_currency   = partner_point_worth_value_in_currency,
                                                
                                                transact_point_amount   = transact_point_amount,
                                                user_acct               = user_acct.create_ndb_key(),
                                                reward_summary          = {
                                                                            'entitled_voucher_summary': reward_summary.entitled_voucher_summary,
                                                                            },
                                                transaction_id          = reward_summary.transaction_id,
                                                )
            partnership_reward_transaction.put()
            return partnership_reward_transaction
        else:
            logger.error('Merchant (%s) or partner (%%) partnership settings is not enabled or created', merchant_artnership_settings, partner_partnership_settings)
            raise Exception('Merchant or partner partnership settings is not enabled or created')
    
    
    @staticmethod
    def list_transaction_by_date(enquiry_date, merchant_acct=None,  partner_merchant_acct=None, offset=0, limit=conf.PAGINATION_SIZE, return_with_cursor=False, start_cursor=None):
        start_datetime  = convert_date_to_datetime(enquiry_date)
        end_datetime    = start_datetime + timedelta(days=1)
        query = PartnershipRewardTransaction.query(
                        ndb.AND(
                            PartnershipRewardTransaction.merchant_acct==merchant_acct.create_ndb_key(),
                            PartnershipRewardTransaction.partner_merchant_acct==partner_merchant_acct.create_ndb_key(),
                            PartnershipRewardTransaction.transact_datetime>=start_datetime,
                            PartnershipRewardTransaction.transact_datetime<end_datetime,
                        ))
        if return_with_cursor:
            (result, next_cursor) = PartnershipRewardTransaction.list_all_with_condition_query(query, order_by=PartnershipRewardTransaction.transact_datetime, start_cursor=start_cursor, return_with_cursor=True, limit=limit)
        
            return (result, next_cursor)
        else:
            return query.order(PartnershipRewardTransaction.transact_datetime).fetch(offset=offset, limit=limit)
    
    
    @staticmethod
    def list_merchant_partnership_reward_transaction(merchant_acct, offset=0, limit=conf.PAGINATION_SIZE, start_cursor=None, return_with_cursor=False, reverse_order=True, keys_only=False):
        if keys_only:
            query = PartnershipRewardTransaction.query(ndb.AND(PartnershipRewardTransaction.merchant_acct==merchant_acct.create_ndb_key()))
            return PartnershipRewardTransaction.list_all_with_condition_query(query, offset=offset, limit=limit, keys_only=True)
        else:
            if reverse_order:
                query = PartnershipRewardTransaction.query(ndb.AND(PartnershipRewardTransaction.merchant_acct==merchant_acct.create_ndb_key())).order(-PartnershipRewardTransaction.transact_datetime)
            else:
                query = PartnershipRewardTransaction.query(ndb.AND(PartnershipRewardTransaction.merchant_acct==merchant_acct.create_ndb_key())).order(PartnershipRewardTransaction.transact_datetime)
            
            return PartnershipRewardTransaction.list_all_with_condition_query(query, offset=offset, limit=limit, start_cursor=start_cursor, return_with_cursor=return_with_cursor)
    
    @staticmethod
    def count_merchant_partnership_reward_transaction(merchant_acct, limit=conf.MAX_FETCH_RECORD):
        query = PartnershipRewardTransaction.query(ndb.AND(PartnershipRewardTransaction.merchant_acct==merchant_acct.create_ndb_key()))
        
        return   PartnershipRewardTransaction.count_with_condition_query(query, limit=limit)
    
    