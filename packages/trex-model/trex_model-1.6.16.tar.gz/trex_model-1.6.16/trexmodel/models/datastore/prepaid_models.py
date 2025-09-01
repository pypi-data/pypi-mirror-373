'''
Created on 24 Aug 2021

@author: jacklok
'''
from google.cloud import ndb
from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel
from trexmodel.models.datastore.user_models import User
from trexmodel.models.datastore.merchant_models import MerchantAcct, Outlet, MerchantUser
import logging
from trexconf import conf, program_conf
from trexlib.utils.string_util import random_number, is_not_empty
from datetime import datetime
from trexlib.utils.common.common_util import sort_dict_list
from dateutil.relativedelta import relativedelta
from trexmodel.program_conf import PRODUCT_TYPES, LOYALTY_PRODUCT
from trexlib.utils.crypto_util import encrypt

logger = logging.getLogger('model')

class PrepaidSettings(BaseNModel,DictModel):
    '''
    Merchant acct as ancestor
    '''
    label                               = ndb.StringProperty(required=True)
    
    start_date                          = ndb.DateProperty(required=True)
    end_date                            = ndb.DateProperty(required=True)
    
    enabled                             = ndb.BooleanProperty(required=True, default=True)
    archived                            = ndb.BooleanProperty(required=False, default=False)
    
    created_datetime                    = ndb.DateTimeProperty(required=True, auto_now_add=True)
    modified_datetime                   = ndb.DateTimeProperty(required=True, auto_now=True)
    
    created_by                          = ndb.KeyProperty(name="created_by", kind=MerchantUser)
    created_by_username                 = ndb.StringProperty(required=False)
    modified_by                         = ndb.KeyProperty(name="modified_by", kind=MerchantUser)
    modified_by_username                = ndb.StringProperty(required=False)
    
    
    is_multi_tier_prepaid               = ndb.BooleanProperty(default=False)
    is_lump_sum_prepaid                 = ndb.BooleanProperty(default=True)
    
    lump_sum_settings                   = ndb.JsonProperty(required=False)
    multitier_settings                  = ndb.JsonProperty(required=False)
    
    created_datetime                    = ndb.DateTimeProperty(required=True, auto_now_add=True)
    modified_datetime                   = ndb.DateTimeProperty(required=True, auto_now=True)
    
    created_by                          = ndb.KeyProperty(name="created_by", kind=MerchantUser)
    created_by_username                 = ndb.StringProperty(required=False)
    modified_by                         = ndb.KeyProperty(name="modified_by", kind=MerchantUser)
    modified_by_username                = ndb.StringProperty(required=False)
    
    dict_properties = ["label", "start_date", "end_date", "enabled", "created_datetime", "modified_datetime", "enabled", "is_disabled",
                       "is_multi_tier_prepaid","is_lump_sum_prepaid", "lump_sum_settings", "multitier_settings", "multitier_settings_list"]
    
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
    def merchant_acct_entity(self):
        return MerchantAcct.fetch(self.key.parent().urlsafe())
    
    @property
    def multitier_settings_list(self):
        multitier_settings = self.multitier_settings
        return_list = []
        if multitier_settings:
            for v in multitier_settings.values():
                return_list.append(v)
        return return_list
    
    @property
    def is_expiration_date_type(self):
        return self.expiration_type == program_conf.REWARD_EXPIRATION_TYPE_SPECIFIC_DATE
    
    def to_configuration(self):
        prepaid_program_configuration =  {
                                                'program_key'   : self.key_in_str,
                                                'label'         : self.label,
                                                }
        if self.is_lump_sum_prepaid:
            prepaid_program_configuration['lump_sum_settings'] = self.lump_sum_settings
        
        if self.is_multi_tier_prepaid:
            prepaid_program_configuration['multitier_settings'] = self.multitier_settings
        
        logger.debug('prepaid_program_configuration=%s', prepaid_program_configuration)
        
        return prepaid_program_configuration
    
    @staticmethod
    def list_by_merchant_acct(merchant_acct):
        result = PrepaidSettings.query(ancestor=merchant_acct.create_ndb_key()).fetch(limit=conf.MAX_FETCH_RECORD)
        not_archive_program_list = []
        for r in result:
            if r.archived != True:
                not_archive_program_list.append(r)
        return not_archive_program_list
    
    def update_merchant_account_prepaid_configuration(self):
        merchant_acct = self.merchant_acct_entity    
        merchant_acct.update_prepaid_program(self.to_configuration())
        merchant_acct.put()
        
        
    
    @staticmethod
    def create(merchant_acct, label, start_date, end_date, is_multi_tier_prepaid=False, is_lump_sum_prepaid=True, lump_sum_settings=None, multitier_settings=None, created_by=None):
        prepaid_settings = PrepaidSettings(
                                parent                  = merchant_acct.create_ndb_key(),
                                label                   = label,
                                start_date              = start_date,
                                end_date                = end_date,
                                is_multi_tier_prepaid   = is_multi_tier_prepaid,
                                is_lump_sum_prepaid     = is_lump_sum_prepaid,
                                
                                lump_sum_settings       = lump_sum_settings,
                                multitier_settings      = multitier_settings,
                                
                                created_by              = created_by.create_ndb_key(),
                                created_by_username     = created_by.username,
                                )
        
        prepaid_settings.put()
        
        if prepaid_settings.enable:
            prepaid_settings.update_merchant_account_prepaid_configuration()
        
        return prepaid_settings
        
    @staticmethod
    def update(prepaid_settings, label, start_date, end_date, is_multi_tier_prepaid=False, is_lump_sum_prepaid=True, lump_sum_settings=None, multitier_settings=None, modified_by=None):
        
        prepaid_settings.label                  = label
        prepaid_settings.start_date             = start_date
        prepaid_settings.end_date               = end_date
        prepaid_settings.is_multi_tier_prepaid  = is_multi_tier_prepaid
        prepaid_settings.is_lump_sum_prepaid    = is_lump_sum_prepaid
        prepaid_settings.lump_sum_settings      = lump_sum_settings
        prepaid_settings.multitier_settings     = multitier_settings
        prepaid_settings.modified_by            = modified_by.create_ndb_key()
        prepaid_settings.modified_by_username   = modified_by.username
        prepaid_settings.put()    
    
        if prepaid_settings.enable:
            prepaid_settings.update_merchant_account_prepaid_configuration()
    
    
        return prepaid_settings
    
    @staticmethod
    def enable(prepaid_settings):
        prepaid_settings.enabled = True
        prepaid_settings.put()
        
        prepaid_settings.update_merchant_account_prepaid_configuration()
        
    @staticmethod
    def disable(prepaid_settings):
        prepaid_settings.enabled = False
        prepaid_settings.put() 
        
        merchant_acct = prepaid_settings.merchant_acct_entity    
        merchant_acct.remove_prepaid_program_configuration(prepaid_settings.key_in_str)
        merchant_acct.put()
        
    @staticmethod
    def archive(prepaid_settings):
        prepaid_settings.archived = True
        prepaid_settings.put() 
        
        merchant_acct = prepaid_settings.merchant_acct_entity    
        merchant_acct.remove_prepaid_program_configuration(prepaid_settings.key_in_str)
        merchant_acct.put()    

class PrepaidRedeemSettings(BaseNModel,DictModel):
    '''
    Merchant acct as ancestor
    '''
    label                               = ndb.StringProperty(required=True)
    device_activation_code              = ndb.StringProperty(required=True)
    device_type                         = ndb.StringProperty(required=False, default=LOYALTY_PRODUCT, choices=set(PRODUCT_TYPES))
    assigned_outlet                     = ndb.KeyProperty(name="assigned_outlet", kind=Outlet)
    testing                             = ndb.BooleanProperty(required=False, default=False)
    
    redeem_code                         = ndb.StringProperty(required=True)
    
    created_datetime                    = ndb.DateTimeProperty(required=True, auto_now_add=True)
    modified_datetime                   = ndb.DateTimeProperty(required=True, auto_now=True)
    
    created_by                          = ndb.KeyProperty(name="created_by", kind=MerchantUser)
    created_by_username                 = ndb.StringProperty(required=False)
    modified_by                         = ndb.KeyProperty(name="modified_by", kind=MerchantUser)
    modified_by_username                = ndb.StringProperty(required=False)
    
    
    dict_properties = [
                        'label', 'redeem_code', 'redeem_url', 'device_activation_code', 'device_type', 'assigned_outlet_key', 'created_datetime', 'modified_datetime',
                    ]
    
    @property
    def is_test_setting(self):
        return self.testing
    
    @property
    def assigned_outlet_key(self):
        return self.assigned_outlet.urlsafe().decode('utf-8')
    
    @property
    def assigned_outlet_entity(self):
        return Outlet.fetch(self.assigned_outlet_key)
    
    @property
    def merchant_acct_entity(self):
        return MerchantAcct.fetch(self.key.parent().urlsafe())
    
    @property
    def redeem_url(self):
        encrypted_redeem_code = encrypt(self.redeem_code)
        return conf.PREPAID_REDEEM_URL.format(code=encrypted_redeem_code)
    
    @property
    def is_loyalty_device(self):
        if self.device_type == program_conf.LOYALTY_PRODUCT:
            return True
        return False
    
    @staticmethod
    def create(merchant_acct, label, assigned_outlet, device_activation_code=None, testing=False, 
               created_by=None
               ):
        
        created_by_username = None
        if is_not_empty(created_by):
            if isinstance(created_by, MerchantUser):
                created_by_username = created_by.username
        
        redeem_code = random_number(24)
        checking_redeem_setting = PrepaidRedeemSettings.get_by_redeem_code(redeem_code)
        regenerate_redeem_code = False
        
        if checking_redeem_setting:
            regenerate_redeem_code = True
        
        while(regenerate_redeem_code):
            redeem_code = random_number(24)
            checking_redeem_setting = PrepaidRedeemSettings.get_by_redeem_code(redeem_code)
            if checking_redeem_setting==None:
                regenerate_redeem_code = False
                
        prepaid_redeem_settings = PrepaidRedeemSettings(
                                        parent                  = merchant_acct.create_ndb_key(),
                                        assigned_outlet         = assigned_outlet.create_ndb_key(),
                                        label                   = label,
                                        redeem_code             = redeem_code,
                                        testing                 = testing, 
                                        device_activation_code  = device_activation_code,
                                        
                                        created_by              = created_by.create_ndb_key(),
                                        created_by_username     = created_by_username,   
                                    )
        
        prepaid_redeem_settings.put()
        
        return prepaid_redeem_settings
        
    @staticmethod
    def update(prepaid_redeem_settings_key, label, assigned_outlet, device_activation_code=None, 
               modified_by=None
               ):
        
        modified_by_username = None
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        prepaid_redeem_settings = PrepaidRedeemSettings.fetch(prepaid_redeem_settings_key)
        
        prepaid_redeem_settings.label                   = label
        prepaid_redeem_settings.device_activation_code  = device_activation_code
        prepaid_redeem_settings.assigned_outlet         = assigned_outlet.create_ndb_key()
        prepaid_redeem_settings.modified_by             = modified_by.create_ndb_key()
        prepaid_redeem_settings.modified_by_username    = modified_by_username
        
        prepaid_redeem_settings.put()
        
        return prepaid_redeem_settings    
    
    @staticmethod
    def remove(prepaid_redeem_settings_key):
        prepaid_redeem_settings = PrepaidRedeemSettings.fetch(prepaid_redeem_settings_key)
        if prepaid_redeem_settings:
            prepaid_redeem_settings.delete()
    
    @staticmethod
    def get_by_redeem_code(redeem_code):
        return PrepaidRedeemSettings.query(PrepaidRedeemSettings.redeem_code ==redeem_code).get()
    
    @staticmethod
    def list_by_merchant_account_and_assigned_outlet(merchant_acct, assigned_outlet, offset=0, limit=conf.PAGINATION_SIZE, start_cursor=None, return_with_cursor=False):
        query = PrepaidRedeemSettings.query(ndb.AND(
                        PrepaidRedeemSettings.assigned_outlet==assigned_outlet.create_ndb_key()
                        ),ancestor=merchant_acct.create_ndb_key())
        
        return PrepaidRedeemSettings.list_all_with_condition_query(query, offset=offset, limit=limit, start_cursor=start_cursor, return_with_cursor=return_with_cursor)
    
    @staticmethod
    def count_by_merchant_account_and_assigned_outlet(merchant_acct, assigned_outlet):
        query = PrepaidRedeemSettings.query(ndb.AND(
                        PrepaidRedeemSettings.assigned_outlet==assigned_outlet.create_ndb_key()
                        ),ancestor=merchant_acct.create_ndb_key())
        
        return PrepaidRedeemSettings.count_with_condition_query(query)
    
    @staticmethod
    def list_by_merchant_account(merchant_acct, offset=0, limit=conf.PAGINATION_SIZE, start_cursor=None, return_with_cursor=False):
        query = PrepaidRedeemSettings.query(ancestor=merchant_acct.create_ndb_key())
        
        return PrepaidRedeemSettings.list_all_with_condition_query(query, offset=offset, limit=limit, start_cursor=start_cursor, return_with_cursor=return_with_cursor)
    
    @staticmethod
    def count_by_merchant_acct(merchant_acct):
        if merchant_acct:
            query = PrepaidRedeemSettings.query(ancestor=merchant_acct.create_ndb_key())
        else:
            query = PrepaidRedeemSettings.query()
        
        return PrepaidRedeemSettings.count_with_condition_query(query)
    
class CustomerPrepaidReward(BaseNModel,DictModel):
    '''
    Customer acct as ancestor
    '''
    merchant_acct                       = ndb.KeyProperty(name="merchant_acct", kind=MerchantAcct)
    topup_outlet                        = ndb.KeyProperty(name="topup_outlet", kind=Outlet)
    
    topup_amount                        = ndb.FloatProperty(required=True, default=.0)
    topup_unit                          = ndb.IntegerProperty(required=True, default=.1)
    topup_prepaid_rate                  = ndb.FloatProperty(required=True, default=.0)
    prepaid_amount                      = ndb.FloatProperty(required=True, default=.0)
    
    used_prepaid_amount                 = ndb.FloatProperty(required=False, default=.0)
    
    status                              = ndb.StringProperty(required=False, default=program_conf.REWARD_STATUS_VALID)
    
    transaction_id                      = ndb.StringProperty(required=True)
    invoice_id                          = ndb.StringProperty(required=False)
    
    #store prepaid program key, topup_amount, prepaid_amount scheme
    prepaid_scheme_details              = ndb.JsonProperty(required=False)
    
    topup_datetime                      = ndb.DateTimeProperty(required=True, auto_now_add=True)
    topup_by                            = ndb.KeyProperty(name="topup_by", kind=MerchantUser)
    topup_by_username                   = ndb.StringProperty(required=False)
    
    reverted_datetime                   = ndb.DateTimeProperty(required=False)
    reverted_by                         = ndb.KeyProperty(name="reverted_by", kind=MerchantUser)
    reverted_by_username                = ndb.StringProperty(required=False)
    
    dict_properties         = ['transaction_id', 'invoice_id', 'topup_amount', 'topup_unit', 'topup_prepaid_rate',
                               'prepaid_amount', 'used_prepaid_amount', 'status', 'prepaid_scheme_details',
                               'topup_datetime', 'topup_by', 'reverted_datetime', 'reverted_by_username',
                               'status'
                               ]
    
    @property
    def is_valid(self):
        return self.status == program_conf.REWARD_STATUS_VALID
    
    @property
    def is_redeemed(self):
        return self.status == program_conf.REWARD_STATUS_REDEEMED
    
    @property
    def is_used(self):
        return self.used_prepaid_amount>0
    
    @property
    def prepaid_balance(self):
        return self.prepaid_amount - self.used_prepaid_amount
    
    @property
    def expiry_date(self):
        return (self.topup_datetime + relativedelta(years=100)).date()
    
    @property
    def reward_format_key(self):
        return None
    
    @property
    def rewarded_datetime(self):
        return self.topup_datetime
    
    @property
    def reward_amount(self):
        return self.prepaid_amount
    
    def update_used_reward_amount(self, used_prepaid_amount):
        self.used_prepaid_amount    += used_prepaid_amount
        prepaid_balance              = self.prepaid_balance
        
        if prepaid_balance<0:
            prepaid_balance = 0
        
        logger.debug('CustomerCountableReward: prepaid_balance=%s', prepaid_balance)
        
        if prepaid_balance ==0:
            self.status = program_conf.REWARD_STATUS_REDEEMED
        else:
            self.status = program_conf.REWARD_STATUS_VALID
            
        self.put()
    
    @property
    def reward_format(self):
        return program_conf.REWARD_FORMAT_PREPAID
    
    @staticmethod
    def __calculate_topup_unit(topup_amount, prepaid_scheme_details):
        return int(topup_amount/prepaid_scheme_details.get('topup_amount'))
    
    @staticmethod
    def __calculate_prepaid_amount(topup_unit, prepaid_scheme_details):
        return topup_unit * prepaid_scheme_details.get('prepaid_amount')
    
    @staticmethod
    def __calculate_topup_prepaid_rate(prepaid_scheme_details):
        return float(prepaid_scheme_details.get('topup_amount')/prepaid_scheme_details.get('prepaid_amount'))
    
    def to_prepaid_summary(self):
        prepaid_summary =  {
                            'amount'                : self.prepaid_amount,
                            'used_amount'           : self.used_prepaid_amount,  
                               
                            }
        
        return prepaid_summary
    
    def to_reward_summary(self):
        return self.to_prepaid_summary()
    
    @property
    def is_reach_reward_limit(self):
        return self.status == program_conf.REWARD_STATUS_REACH_LIMIT
    
    @property
    def reward_balance(self):
        return self.prepaid_amount - self.used_prepaid_amount
    
    @property
    def reward_format_label(self):
        return 'prepaid'
    
    @property
    def reward_brief(self):
        return 'Entitle {reward_amount} {reward_format}'.format(reward_amount=self.prepaid_amount, reward_format=self.reward_format_label)
    
    @classmethod
    def list_by_valid_with_cursor(cls, customer, limit=50, start_cursor=None):
        query = cls.query(ndb.AND(cls.status==program_conf.REWARD_STATUS_VALID
            ), ancestor=customer.create_ndb_key()).order(cls.topup_datetime)
            
        (result, next_cursor) = cls.list_all_with_condition_query(query, start_cursor=start_cursor, return_with_cursor=True, limit=limit)
        
        return (result, next_cursor) 
    
    @staticmethod
    def list_by_customer(customer, status=program_conf.REWARD_STATUS_VALID, limit = conf.MAX_FETCH_RECORD):
        return CustomerPrepaidReward.query(ndb.AND(CustomerPrepaidReward.status==status), ancestor=customer.create_ndb_key()).fetch(limit=limit)
    
    @staticmethod
    def list_all_by_customer(customer, limit = conf.MAX_FETCH_RECORD, offset=0):
        return CustomerPrepaidReward.query(ancestor=customer.create_ndb_key()).fetch(offset=offset, limit=limit)
    
    @staticmethod
    def list_by_transaction_id(transaction_id):
        return CustomerPrepaidReward.query(CustomerPrepaidReward.transaction_id==transaction_id).fetch(limit=conf.MAX_FETCH_RECORD)
    
    @staticmethod
    def list_by_customer_acct(customer_acct):
        return CustomerPrepaidReward.query(ndb.AND(CustomerPrepaidReward.status==program_conf.REDEEM_STATUS_VALID),ancestor=customer_acct.create_ndb_key()).fetch(limit=conf.MAX_FETCH_RECORD)
        
    @staticmethod
    def topup(customer_acct, topup_amount, prepaid_program, invoice_id=None, topup_outlet=None, topup_by=None, transaction_id=None, topup_datetime=None):
        prepaid_scheme_details      = {
                                        }
        found_match_scheme          = None
        
        if prepaid_program:
            is_lump_sum_prepaid     = prepaid_program.is_lump_sum_prepaid
            is_multi_tier_prepaid   = prepaid_program.is_multi_tier_prepaid
            
            sorted_tier_scheme      = None
            
            prepaid_scheme_details  = {
                                        'program_key'   : prepaid_program.key_in_str
                                        }
            
            tier_prepaid_scheme      = None
            
            
            logger.debug('is_multi_tier_prepaid=%s', is_multi_tier_prepaid)
            
            if is_multi_tier_prepaid:
                sorted_tier_scheme = sort_dict_list(prepaid_program.multitier_settings.values(), 'min_topup_amount')
                
                logger.debug('Get topup scheme from topup amount(%s)', topup_amount)
                
                #look for higheest min topup amount scheme
                for scheme in sorted_tier_scheme:
                    if topup_amount>= scheme.get('min_topup_amount'):
                        tier_prepaid_scheme = {
                                                'topup_amount'  : scheme.get('topup_amount'),
                                                'prepaid_amount': scheme.get('prepaid_amount'),
                                                'prepaid_rate'  : scheme.get('prepaid_amount')/scheme.get('topup_amount'),
                                                'scheme_type'   : 'tier',
                                                }
                        logger.debug('Found topup scheme for min topup amount(%s)', scheme.get('min_topup_amount'))
            
            logger.debug('tier_prepaid_scheme=%s', tier_prepaid_scheme)
            
            #if topup amount is less than smallest prepaid tier minimum topup amount, thus goto lump sum scheme    
            if tier_prepaid_scheme is None and is_lump_sum_prepaid:
                logger.debug('going to create scheme from lump sum setting')
                prepaid_scheme = prepaid_program.lump_sum_settings
                found_match_scheme = {
                                                'topup_amount'  : prepaid_scheme.get('topup_amount'),
                                                'prepaid_amount': prepaid_scheme.get('prepaid_amount'),
                                                'prepaid_rate'  : prepaid_scheme.get('prepaid_amount')/prepaid_scheme.get('topup_amount'),
                                                'scheme_type'   : 'lump_sum',
                                                }  
            
            else:
                found_match_scheme = tier_prepaid_scheme
             
        if found_match_scheme is None:
            logger.debug('going to create scheme default scheme')
            
            found_match_scheme = {
                                            'topup_amount'  : 1,
                                            'prepaid_amount': 1,
                                            'prepaid_rate'  : 1,
                                            'scheme_type'   : 'auto',
                                            }
            
        logger.debug('create found_match_scheme=%s', found_match_scheme)
        
        prepaid_scheme_details.update(found_match_scheme)
        
        logger.debug('prepaid_scheme_details=%s', prepaid_scheme_details)
            
        topup_unit          = CustomerPrepaidReward.__calculate_topup_unit(topup_amount, prepaid_scheme_details)
        prepaid_amount      = CustomerPrepaidReward.__calculate_prepaid_amount(topup_unit, prepaid_scheme_details)
        topup_prepaid_rate  = CustomerPrepaidReward.__calculate_topup_prepaid_rate(prepaid_scheme_details)
        
        topup_by_key = None
        topup_by_username = None
        
        if topup_by:
            topup_by_key = topup_by.create_ndb_key()
            topup_by_username = topup_by.username
            
        if topup_datetime is None:
            topup_datetime = datetime.utcnow()
            
        merchant_acct               = customer_acct.registered_merchant_acct
        prepaid_topup_reward        = CustomerPrepaidReward(
                                                            parent                  = customer_acct.create_ndb_key(),
                                                            merchant_acct           = merchant_acct.create_ndb_key(),
                                                            topup_outlet            = topup_outlet.create_ndb_key() if topup_outlet else None,
                                                            topup_amount            = topup_amount,
                                                            topup_unit              = topup_unit,
                                                            prepaid_amount          = prepaid_amount,
                                                            topup_prepaid_rate      = topup_prepaid_rate,
                                                            used_prepaid_amount     = .0,
                                                            prepaid_scheme_details  = prepaid_scheme_details,
                                                            
                                                            transaction_id          = transaction_id,
                                                            invoice_id              = invoice_id,
                                                            
                                                            topup_by                = topup_by_key,
                                                            topup_by_username       = topup_by_username, 
                                                            topup_datetime          = topup_datetime,    
                                                            )
        
        prepaid_topup_reward.put()
        
        return prepaid_topup_reward
    
    @staticmethod
    def create(customer_acct, topup_outlet, 
               topup_amount=0, topup_unit=0, topup_prepaid_rate = 1, 
               prepaid_amount=.0, prepaid_scheme_details={}, 
               topup_datetime=None, topup_by=None,
               transaction_id=None, invoice_id=None,
               ):
        
        merchant_acct  = customer_acct.registered_merchant_acct
        
        topup_by_key = None
        topup_by_username = None
        
        if topup_by:
            topup_by_key = topup_by.create_ndb_key()
            topup_by_username = topup_by.username
            
        CustomerPrepaidReward(
            parent                  = customer_acct.create_ndb_key(),
            merchant_acct           = merchant_acct.create_ndb_key(),
            topup_outlet            = topup_outlet.create_ndb_key() if topup_outlet else None,
            topup_amount            = topup_amount,
            topup_unit              = topup_unit,
            prepaid_amount          = prepaid_amount,
            topup_prepaid_rate      = topup_prepaid_rate,
            used_prepaid_amount     = .0,
            prepaid_scheme_details  = prepaid_scheme_details,
            
            transaction_id          = transaction_id,
            invoice_id              = invoice_id,
            
            topup_by                = topup_by_key,
            topup_by_username       = topup_by_username, 
            topup_datetime          = topup_datetime,   
             
            )
    
    @staticmethod
    def delete_all_by_customer(customer):
        query = CustomerPrepaidReward.query(ancestor=customer.create_ndb_key())
        CustomerPrepaidReward.delete_multiples(query)
        
    @staticmethod
    def list_by_merchant_acct(merchant_acct, datetime_range_start=None, datetime_range_end=None, offset=0, limit=50, start_cursor=None, return_with_cursor=True):
        if is_not_empty(datetime_range_start) and is_not_empty(datetime_range_end):
            query = CustomerPrepaidReward.query(ndb.AND(
                    CustomerPrepaidReward.merchant_acct==merchant_acct.create_ndb_key(),
                    CustomerPrepaidReward.topup_datetime>=datetime_range_start,
                    CustomerPrepaidReward.topup_datetime<datetime_range_end,
                    ))
        else:
            query = CustomerPrepaidReward.query(ndb.AND(
                    CustomerPrepaidReward.merchant_acct==merchant_acct.create_ndb_key(),
                    ))
            
        return CustomerPrepaidReward.list_all_with_condition_query(query, start_cursor=start_cursor, return_with_cursor=return_with_cursor, offset=offset, limit=limit)
    
    @staticmethod
    def count_by_merchant_acct(merchant_acct, datetime_range_start=None, datetime_range_end=None, limit=conf.MAX_FETCH_RECORD,):
        if is_not_empty(datetime_range_start) and is_not_empty(datetime_range_end):
            query = CustomerPrepaidReward.query(ndb.AND(
                    CustomerPrepaidReward.merchant_acct==merchant_acct.create_ndb_key(),
                    CustomerPrepaidReward.topup_datetime>=datetime_range_start,
                    CustomerPrepaidReward.topup_datetime<datetime_range_end,
                    ))
        else:
            query = CustomerPrepaidReward.query(ndb.AND(
                    CustomerPrepaidReward.merchant_acct==merchant_acct.create_ndb_key(),
                    ))
            
        return CustomerPrepaidReward.count_with_condition_query(query, limit)    
    
