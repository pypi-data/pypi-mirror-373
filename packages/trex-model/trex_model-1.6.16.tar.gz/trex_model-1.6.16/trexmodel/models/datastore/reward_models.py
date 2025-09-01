'''
Created on 22 Apr 2021

@author: jacklok
'''
from google.cloud import ndb
from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel,\
    convert_to_serializable_value
from trexmodel.models.datastore.user_models import User
from trexmodel.models.datastore.merchant_models import MerchantAcct, Outlet, MerchantUser
from trexmodel.models.datastore.program_models import MerchantProgram,\
    MerchantTierRewardProgram
from trexmodel.models.datastore.voucher_models import MerchantVoucher
from trexlib.utils.string_util import is_empty, is_not_empty
import logging
from trexconf import conf, program_conf
from trexlib.utils.string_util import random_string
from datetime import datetime, timedelta
from trexmodel.utils.model.model_util import generate_transaction_id,\
    string_to_key_property 
from six import string_types
from flask_babel import gettext
from trexmodel.models.datastore.customer_models import Customer

logger = logging.getLogger('model')


class RewardEntitlement(BaseNModel, DictModel):
    effective_date              = ndb.DateProperty(required=True)
    expiry_date                 = ndb.DateProperty(required=True)
    
    transaction_id              = ndb.StringProperty(required=True)
    
    invoice_id                  = ndb.StringProperty(required=False)
    
    rewarded_datetime           = ndb.DateTimeProperty(required=True, auto_now_add=True)
    rewarded_by                 = ndb.KeyProperty(name="rewarded_by", kind=MerchantUser)
    rewarded_by_username        = ndb.StringProperty(required=False)
    
    reward_datetime_provided    = ndb.BooleanProperty(required=False, default=False)
    
    status                      = ndb.StringProperty(required=False, default=program_conf.REWARD_STATUS_VALID)
    
    reverted_datetime           = ndb.DateTimeProperty(required=False)
    reverted_by                 = ndb.KeyProperty(name="reverted_by", kind=MerchantUser)
    reverted_by_username        = ndb.StringProperty(required=False)
    
    @classmethod
    def list_by_transaction_id(cls, transaction_id):
        return cls.query(cls.transaction_id==transaction_id).fetch(limit=conf.MAX_FETCH_RECORD)
    
    @property
    def is_valid(self):
        return self.status == program_conf.REWARD_STATUS_VALID
    
    @property
    def is_redeemed(self):
        return self.status == program_conf.REWARD_STATUS_REDEEMED
    
    @property
    def is_removed(self):
        return self.status == program_conf.REWARD_STATUS_REMOVED
    
    @property
    def is_reverted(self):
        return self.status == program_conf.REWARD_STATUS_REVERTED
    
    
    
class CustomerEntitledReward(RewardEntitlement):
    '''
    Customer as ancestor
    '''
    
    merchant_acct               = ndb.KeyProperty(name="merchant_acct", kind=MerchantAcct)
    user_acct                   = ndb.KeyProperty(name="user_acct", kind=User)
    transact_outlet             = ndb.KeyProperty(name="transact_outlet", kind=Outlet)
    reward_program              = ndb.KeyProperty(name="reward_program")
    
    @property
    def entitled_customer_key(self):
        return self.key.parent().urlsafe().decode('utf-8')
    
    @property
    def entitled_user_key(self):
        return self.user_acct.urlsafe().decode('utf-8')
    
    @property
    def merchant_acct_key(self):
        return self.merchant_acct.urlsafe().decode('utf-8')
    
    @property
    def entitled_customer_acct(self):
        return Customer.fetch(self.key.parent().urlsafe())
    
    @property
    def reward_program_key(self):
        if self.reward_program:
            return self.reward_program.urlsafe().decode('utf-8')
        else:
            return ''
    
    @property
    def rewarded_by_merchant_acct_entity(self):
        return MerchantAcct.fetch(self.merchant_acct.urlsafe())
    
    @property
    def reward_format(self):
        pass
    
    @property
    def reward_format_key(self):
        pass
    
    @property
    def reward_format_label(self):
        pass
    
    @property
    def rewarded_datetime_with_gmt(self):
        gmt_hour = self.rewarded_by_merchant_acct_entity.gmt_hour
        
        return self.rewarded_datetime + timedelta(hours=gmt_hour)
    
    @property
    def is_used(self):
        pass
    
    def revert(self, reverted_by, reverted_datetime=None):
        self.status = program_conf.REWARD_STATUS_REVERTED
        if reverted_datetime is None:
            reverted_datetime = datetime.now()
        
        self.reverted_datetime      = reverted_datetime
        self.reverted_by            = reverted_by.create_ndb_key()
        self.reverted_by_username   = reverted_by.username
        self.put()
    
    @classmethod
    def list_by_customer(cls, customer, status=program_conf.REWARD_STATUS_VALID, limit = conf.MAX_FETCH_RECORD):
        return cls.query(ndb.AND(cls.status==status), ancestor=customer.create_ndb_key()).fetch(limit=limit)
        
    @classmethod
    def list_all_by_customer(cls, customer, offset=0, limit = conf.MAX_FETCH_RECORD):
        return cls.query(ancestor=customer.create_ndb_key()).fetch(offset=offset, limit=limit)
    
    @classmethod
    def list_all_by_user_acct(cls, user_acct, limit = conf.MAX_FETCH_RECORD):
        return cls.query(ndb.AND(cls.user_acct==user_acct.create_ndb_key())).fetch(limit=limit)
    
    @classmethod
    def delete_all_by_customer(cls, customer):
        query = cls.query(ancestor=customer.create_ndb_key())
        cls.delete_multiples(query)    
    
    @staticmethod
    def count_by_merchant_acct(cls, merchant_acct, datetime_ranage_start=None, datetime_range_end=None):
        if datetime_ranage_start and datetime_range_end:
            result = cls.query(ndb.AND(
                        cls.merchant_acct==merchant_acct.create_ndb_key(),
                        cls.rewarded_datetime>=datetime_ranage_start,
                        cls.rewarded_datetime<datetime_range_end,
                        )).count(limit=conf.MAX_FETCH_RECORD)
        else:
            result = cls.query(ndb.AND(
                        cls.merchant_acct==merchant_acct.create_ndb_key(),
                        )).count(limit=conf.MAX_FETCH_RECORD)
    
        
        return result
    
    @classmethod
    def list_by_merchant_acct(cls, merchant_acct, datetime_range_start=None, datetime_range_end=None, offset=0, limit=50, start_cursor=None, return_with_cursor=True):
        if is_not_empty(datetime_range_start) and is_not_empty(datetime_range_end):
            query = cls.query(ndb.AND(
                    cls.merchant_acct==merchant_acct.create_ndb_key(),
                    cls.rewarded_datetime>=datetime_range_start,
                    cls.rewarded_datetime<datetime_range_end,
                    ))
        else:
            query = cls.query(ndb.AND(
                    cls.merchant_acct==merchant_acct.create_ndb_key(),
                    ))
        return cls.list_all_with_condition_query(query, start_cursor=start_cursor, return_with_cursor=return_with_cursor, offset=offset, limit=limit)
        

class CustomerCountableReward(CustomerEntitledReward):
    reward_amount               = ndb.FloatProperty(required=True, default=0)
    used_reward_amount          = ndb.FloatProperty(required=True, default=0)
    
    dict_properties     = [
                            'reward_amount', 'used_reward_amount', 'transaction_id', 'rewarded_datetime', 
                            'status',
                           ]
    
    def __repr__(self):
        return 'transaction_id=%s, rewarded_datetime=%s, reward_balance=%s'% (self.transaction_id, self.rewarded_datetime, self.reward_balance)
    
    @property
    def is_reach_reward_limit(self):
        return self.status == program_conf.REWARD_STATUS_REACH_LIMIT
    
    @property
    def reward_balance(self):
        return self.reward_amount - self.used_reward_amount
    
    def update_used_reward_amount(self, used_reward_amount):
        self.used_reward_amount += used_reward_amount
        
        logger.debug('CustomerCountableReward: reward_balance=%s', self.reward_balance)
        
        if self.reward_balance ==0:
            self.status = program_conf.REWARD_STATUS_REDEEMED
        
        self.put()
    
    @classmethod
    def list_by_valid_with_cursor(cls, customer, limit=50, start_cursor=None, start_datetime=None, end_datetime=None, expiry_date=None):
        if start_datetime is not None and end_datetime is not None:
            query = cls.query(ndb.AND(cls.status==program_conf.REWARD_STATUS_VALID,
                                      cls.rewarded_datetime>=start_datetime,
                                      cls.rewarded_datetime<end_datetime,
            ), ancestor=customer.create_ndb_key()).order(cls.rewarded_datetime)
            
        elif expiry_date is not None:
            query = cls.query(ndb.AND(cls.status==program_conf.REWARD_STATUS_VALID,
                                      cls.expiry_date>expiry_date
            ), ancestor=customer.create_ndb_key()).order(cls.expiry_date)
            
        
        else:
            query = cls.query(ndb.AND(cls.status==program_conf.REWARD_STATUS_VALID
                ), ancestor=customer.create_ndb_key()).order(cls.expiry_date)
                
        
        (result, next_cursor) = cls.list_all_with_condition_query(query, start_cursor=start_cursor, return_with_cursor=True, limit=limit)
        
        return (result, next_cursor)
    
    
    
    @classmethod
    def list_valid(cls, customer, limit=50):
        query = cls.query(ndb.AND(cls.status==program_conf.REWARD_STATUS_VALID
            ), ancestor=customer.create_ndb_key()).order(cls.expiry_date)
            
        return cls.list_all_with_condition_query(query, limit=limit)
         
    
    @property
    def is_used(self):
        return self.used_reward_amount>0
    
    @property
    def reward_brief(self):
        if self.is_reach_reward_limit:
            return gettext('Not entitle any reward due to reach rewward limit')
        else:
            return gettext('Entitle {reward_amount} {reward_format}').format(reward_amount=self.reward_amount, reward_format=self.reward_format_label)
    
    def to_reward_summary(self):
        return {
                'reward_format'         : self.reward_format, 
                'amount'                : self.reward_amount,
                'used_amount'           : self.used_reward_amount,
                'expiry_date'           : self.expiry_date.strftime('%d-%m-%Y'),
                'rewarded_date'         : self.rewarded_datetime.strftime('%d-%m-%Y'),
                'program_key'           : self.reward_program_key,
                'is_reach_reward_limit' : self.is_reach_reward_limit,
                }
    
    @classmethod
    def create(cls, reward_amount, customer_acct, transact_outlet,
               effective_date=None, expiry_date=None, 
               transaction_id=None, invoice_id=None,
               rewarded_by=None, program_key=None, used_reward_amount=.0,
               rewarded_datetime = None, status=program_conf.REWARD_STATUS_VALID
               ):
        
        if is_empty(transaction_id):
            transaction_id = generate_transaction_id()
            
        if effective_date is None:
            effective_date = datetime.today()
            
        if expiry_date is None:
            expiry_date = (datetime.today() + timedelta(days=1)).date()
        
        if is_not_empty(program_key):
            reward_program          = string_to_key_property(program_key)
        else:
            reward_program = None
        
        customer_reward = cls(
                                            parent                  = customer_acct.create_ndb_key(),
                                            reward_amount           = reward_amount,
                                            used_reward_amount      = used_reward_amount,
                                            transaction_id          = transaction_id,
                                            invoice_id              = invoice_id,
                                            
                                            merchant_acct           = customer_acct.merchant_acct,
                                            transact_outlet         = transact_outlet.create_ndb_key() if transact_outlet else None,
                                            
                                            effective_date          = effective_date,
                                            expiry_date             = expiry_date,
                                            
                                            rewarded_by             = rewarded_by.create_ndb_key() if rewarded_by else None,
                                            rewarded_by_username    = rewarded_by.username if rewarded_by else None,
                                            
                                            reward_program          = reward_program,
                                            rewarded_datetime       = rewarded_datetime,
                                            
                                            status                  = status,
                                            
                                            )
        
        customer_reward.put()
        
        return customer_reward
    
class RevertedCustomerCountableReward(CustomerCountableReward):
    reverted_datetime           = ndb.DateTimeProperty(required=True, auto_now_add=True)
    reverted_by                 = ndb.KeyProperty(name="reverted_by", kind=MerchantUser)
    reverted_by_username        = ndb.StringProperty(required=False)
    
    @classmethod
    def create(cls, customer_reward, reverted_by):
        reverted_customer_reward = cls(
                            parent                  = customer_reward.key.parent(),
                            reward_amount           = customer_reward.reward_amount,
                            transaction_id          = customer_reward.transaction_id,
                            invoice_id              = customer_reward.invoice_id,
                            
                            merchant_acct           = customer_reward.merchant_acct,
                            transact_outlet         = customer_reward.transact_outlet,
                            
                            effective_date          = customer_reward.effective_date,
                            expiry_date             = customer_reward.expiry_date,
                            
                            rewarded_by             = customer_reward.rewarded_by,
                            rewarded_by_username    = customer_reward.rewarded_by_username,
                            
                            reverted_by             = reverted_by.create_ndb_key(),
                            reverted_by_username    = reverted_by.username,
                            
                            )
        
        reverted_customer_reward.put()
        
class CustomerPointReward(CustomerCountableReward):
    
    @property
    def reward_format(self):
        return program_conf.REWARD_FORMAT_POINT
    
    @property
    def reward_format_label(self):
        return 'point(s)'

class CustomerStampReward(CustomerCountableReward):
    
    @property
    def reward_format(self):
        return program_conf.REWARD_FORMAT_STAMP
    
    @property
    def reward_format_label(self):
        return 'stamp(s)'
    

class RevertedCustomerPointReward(RevertedCustomerCountableReward):
    pass

class RevertedCustomerStampReward(RevertedCustomerCountableReward):
    pass
    
class CustomerEntitledVoucher(CustomerEntitledReward):
    
    entitled_voucher            = ndb.KeyProperty(name='entitled_voucher', kind=MerchantVoucher)
    redeem_code                 = ndb.StringProperty(required=False)
    redeemed_datetime           = ndb.DateTimeProperty(required=False)
    
    redeemed_by_outlet          = ndb.KeyProperty(name='redeemed_by_outlet', required=False)
    redeemed_by                 = ndb.KeyProperty(name="redeemed_by", kind=MerchantUser)
    redeemed_by_username        = ndb.StringProperty(required=False)
    
    redeemed_transaction_id     = ndb.StringProperty(required=False)
    
    removed_datetime            = ndb.DateTimeProperty(required=False)
    removed_by_username         = ndb.StringProperty(required=False)
    
    use_online                  = ndb.BooleanProperty(required=False, default=False)
    use_in_store                = ndb.BooleanProperty(required=False, default=False)
    
    partner_merchant_acct       = ndb.KeyProperty(name='partner_merchant_acct', kind=MerchantAcct)
    
    dict_properties     = [
                            'redeem_code', 'configuration', 'rewarded_datetime', 'transaction_id', 
                            'status', 'is_reverted', 'is_used', 'partner_merchant_acct_key',
                           ]
    
    @property
    def redeemed_by_outlet_key(self):
        if self.redeemed_by_outlet:
            return self.redeemed_by_outlet.urlsafe().decode('utf-8')
    
    @property
    def partner_merchant_acct_key(self):
        if self.partner_merchant_acct:
            return self.partner_merchant_acct.urlsafe().decode('utf-8')
    
    
    @staticmethod
    def list_by_transaction_id(transaction_id):
        return CustomerEntitledVoucher.query(CustomerEntitledVoucher.transaction_id==transaction_id).fetch(limit=conf.MAX_FETCH_RECORD)
    
    @staticmethod
    def list_redeemed_by_merchant_voucher(customer, merchant_voucher, passed_day_count=1):
        
        now = datetime.utcnow()
        passed_datetime = now - timedelta(days = passed_day_count)
        
        result = CustomerEntitledVoucher.query(ndb.AND(
                    CustomerEntitledVoucher.entitled_voucher==merchant_voucher.create_ndb_key(),
                    CustomerEntitledVoucher.redeemed_datetime>=passed_datetime,
                    CustomerEntitledVoucher.status==program_conf.REWARD_STATUS_REDEEMED,
                    
                    ), ancestor=customer.create_ndb_key()).fetch(limit=conf.MAX_FETCH_RECORD)
    
        
        return result
    
    @staticmethod
    def list_by_merchant_voucher(merchant_voucher, entitled_datetime_start=None, entitled_datetime_end=None):
        if entitled_datetime_start and entitled_datetime_end:
            result = CustomerEntitledVoucher.query(ndb.AND(
                        CustomerEntitledVoucher.entitled_voucher==merchant_voucher.create_ndb_key(),
                        CustomerEntitledVoucher.rewarded_datetime>=entitled_datetime_start,
                        CustomerEntitledVoucher.rewarded_datetime<entitled_datetime_end,
                        )).fetch(limit=conf.MAX_FETCH_RECORD)
        else:
            result = CustomerEntitledVoucher.query(ndb.AND(
                        CustomerEntitledVoucher.entitled_voucher==merchant_voucher.create_ndb_key(),
                        )).fetch(limit=conf.MAX_FETCH_RECORD)
        
        return result
    
    @staticmethod
    def count_redeemed_by_merchant_voucher(customer, merchant_voucher, passed_day_count=1):
        
        now = datetime.utcnow()
        passed_datetime = now - timedelta(days = passed_day_count)
        
        result = CustomerEntitledVoucher.query(ndb.AND(
                    CustomerEntitledVoucher.entitled_voucher==merchant_voucher.create_ndb_key(),
                    CustomerEntitledVoucher.redeemed_datetime>=passed_datetime,
                    CustomerEntitledVoucher.status==program_conf.REWARD_STATUS_REDEEMED,
                    
                    ), ancestor=customer.create_ndb_key()).count(limit=conf.MAX_FETCH_RECORD)
    
        
        return result
    
    @staticmethod
    def count_by_merchant_acct(merchant_acct, datetime_ranage_start=None, datetime_range_end=None):
        if datetime_ranage_start and datetime_range_end:
            result = CustomerEntitledVoucher.query(ndb.AND(
                        CustomerEntitledVoucher.merchant_acct==merchant_acct.create_ndb_key(),
                        CustomerEntitledVoucher.rewarded_datetime>=datetime_ranage_start,
                        CustomerEntitledVoucher.rewarded_datetime<datetime_range_end,
                        )).count(limit=conf.MAX_FETCH_RECORD)
        else:
            result = CustomerEntitledVoucher.query(ndb.AND(
                        CustomerEntitledVoucher.merchant_acct==merchant_acct.create_ndb_key(),
                        )).count(limit=conf.MAX_FETCH_RECORD)
    
        
        return result
    '''
    @staticmethod
    def list_by_merchant_acct(merchant_acct, datetime_range_start=None, datetime_range_end=None, offset=0, limit=50,):
        if is_not_empty(datetime_range_start) and is_not_empty(datetime_range_end):
            query = CustomerEntitledVoucher.query(ndb.AND(
                    CustomerEntitledVoucher.merchant_acct==merchant_acct.create_ndb_key(),
                    CustomerEntitledVoucher.rewarded_datetime>=datetime_range_start,
                    CustomerEntitledVoucher.rewarded_datetime<datetime_range_end,
                    ))
        else:
            query = CustomerEntitledVoucher.query(ndb.AND(
                    CustomerEntitledVoucher.merchant_acct==merchant_acct.create_ndb_key(),
                    ))
        return CustomerEntitledVoucher.list_all_with_condition_query(query, offset=offset, limit=limit)
        
    
    @staticmethod
    def list_by_merchant_acct_with_cursor(merchant_acct, datetime_range_start=None, datetime_range_end=None, offset=0, limit=50, start_cursor=None, return_with_cursor=True):
        if is_not_empty(datetime_range_start) and is_not_empty(datetime_range_end):
            query = CustomerEntitledVoucher.query(ndb.AND(
                    CustomerEntitledVoucher.merchant_acct==merchant_acct.create_ndb_key(),
                    CustomerEntitledVoucher.rewarded_datetime>=datetime_range_start,
                    CustomerEntitledVoucher.rewarded_datetime<datetime_range_end,
                    ))
        else:
            query = CustomerEntitledVoucher.query(ndb.AND(
                    CustomerEntitledVoucher.merchant_acct==merchant_acct.create_ndb_key(),
                    ))
        (result, next_cursor) = CustomerEntitledVoucher.list_all_with_condition_query(query, start_cursor=start_cursor, return_with_cursor=return_with_cursor, offset=offset, limit=limit)
        
        return (result, next_cursor)
    '''
    @staticmethod
    def count_redeemed_by_merchant_voucher_and_passed_redeemed_datetime(customer, merchant_voucher, passed_redeemed_datetime):
        
        result = CustomerEntitledVoucher.query(ndb.AND(
                    CustomerEntitledVoucher.entitled_voucher==merchant_voucher.create_ndb_key(),
                    CustomerEntitledVoucher.redeemed_datetime>=passed_redeemed_datetime,
                    CustomerEntitledVoucher.status==program_conf.REWARD_STATUS_REDEEMED,
                    
                    ), ancestor=customer.create_ndb_key()).count(limit=conf.MAX_FETCH_RECORD)
    
        
        return result
    
    @staticmethod
    def count_merchant_voucher(merchant_voucher):
        
        result = CustomerEntitledVoucher.query(ndb.AND(
                    CustomerEntitledVoucher.entitled_voucher==merchant_voucher.create_ndb_key(),
                    )).count(limit=conf.MAX_FETCH_RECORD)
    
        
        return result
    
    def revert_from_redemption(self):
        self.status = program_conf.REDEEM_STATUS_VALID
        self.redeemed_datetime      = None
        self.redeemed_by            = None
        self.redeemed_by_username   = None
        self.put()
        
    
    def redeem(self, redeemed_by=None, redeemed_datetime=None, redeemed_outlet=None, transaction_id=None):
        self.status = program_conf.REWARD_STATUS_REDEEMED   
        
        if redeemed_datetime is None:
            redeemed_datetime = datetime.utcnow()
        
        redeemed_by_username = None
        if redeemed_by:
            redeemed_by_username = redeemed_by.username
        
        self.redeemed_datetime          = redeemed_datetime
        self.redeemed_by                = redeemed_by.create_ndb_key()
        self.redeemed_by_username       = redeemed_by_username
        self.redeemed_outlet            = redeemed_outlet.create_ndb_key()
        self.redeemed_transaction_id    = transaction_id
        self.put()
    
    def remove(self, removed_by=None, removed_datetime=None):
        self.status = program_conf.REWARD_STATUS_REMOVED   
        
        if removed_datetime is None:
            removed_datetime = datetime.utcnow()
        
        removed_by_username = None
        if removed_by:
            removed_by_username = removed_by.username
            
        self.removed_datetime      = removed_datetime
        self.removed_by_username   = removed_by_username
        self.put() 
        
    @property
    def entitled_customer_entity(self):
        return Customer.fetch(self.key.parent().urlsafe()) 
        
    @property
    def is_used(self):
        return self.status == program_conf.REWARD_STATUS_REDEEMED
    
    @property
    def is_valid_to_redeem(self):
        if self.status == program_conf.REWARD_STATUS_VALID:
            return True
        return False
    
    def is_effective_to_redeem(self, checking_datetime=None):
        if checking_datetime is None:
            checking_datetime = datetime.utcnow().date()
        if self.effective_date <= checking_datetime:
            return True
        return False
    
    def is_not_expired_to_redeem(self, checking_datetime=None):
        if checking_datetime is None:
            checking_datetime = datetime.utcnow().date()
        if self.expiry_date >= checking_datetime:
            return True
        return False
    
    @property
    def is_reverted(self):
        return self.status == program_conf.REWARD_STATUS_REVERTED
    
    @property
    def transact_outlet_summary(self):
        return Outlet.fetch(self.transact_outlet.urlsafe())
    
    @property
    def configuration(self):
        voucher = MerchantVoucher.fetch(self.entitled_voucher.urlsafe())
        if voucher:
            return voucher.configuration
    
    @property
    def entitled_voucher_key(self):
        return self.entitled_voucher.urlsafe().decode('utf-8')
    
    @property
    def entitled_voucher_entity(self):
        return MerchantVoucher.fetch(self.entitled_voucher.urlsafe())
    
    @property
    def merchant_voucher_entity(self):
        return MerchantVoucher.fetch(self.entitled_voucher.urlsafe())
    
    @property
    def merchant_voucher_key(self):
        return self.entitled_voucher.urlsafe().decode('utf-8')
    
    def redeem_limit_configuration(self):
        _redeem_limit_configuration = self.merchant_voucher_entity.redeem_limit_configuration
        
        return _redeem_limit_configuration
    
    def to_redeem_info(self):
        return {
                'redeem_code'       : self.redeem_code,
                'entitled_datetime' : self.rewarded_datetime.strftime('%d-%m-%Y %H:%M'),
                'effective_date'    : self.effective_date.strftime('%d-%m-%Y'),
                'expiry_date'       : self.expiry_date.strftime('%d-%m-%Y'),
                
                }
    
    @staticmethod
    def create(merchant_voucher, customer_acct, transact_outlet=None, 
               effective_date=None, expiry_date=None,
               transaction_id=None, invoice_id=None,
               rewarded_by=None, rewarded_datetime=None,
               program_key=None, partner_merchant_acct=None,
               ):
        logger.debug('program_key=%s', program_key)
        redeem_code = random_string(program_conf.REDEEM_CODE_LENGTH, is_human_mistake_safe=True)
        
        if is_empty(transaction_id):
            transaction_id = generate_transaction_id()
        
        customer_entiteld_voucher = CustomerEntitledVoucher(
                                            parent                  = customer_acct.create_ndb_key(),
                                            entitled_voucher        = merchant_voucher.create_ndb_key(),
                                            
                                            effective_date          = effective_date,
                                            expiry_date             = expiry_date,
                                            
                                            redeem_code             = redeem_code,
                                            transaction_id          = transaction_id,
                                            invoice_id              = invoice_id,
                                            
                                            merchant_acct           = customer_acct.merchant_acct,
                                            transact_outlet         = transact_outlet.create_ndb_key() if transact_outlet else None,
                                            
                                            rewarded_by             = rewarded_by.create_ndb_key() if rewarded_by else None,
                                            rewarded_by_username    = rewarded_by.username if rewarded_by else None,
                                            
                                            rewarded_datetime       = rewarded_datetime,
                                            
                                            user_acct               = customer_acct.registered_user_acct.create_ndb_key(),
                                            reward_program          = string_to_key_property(program_key) if program_key is not None else None,
                                            
                                            partner_merchant_acct   = partner_merchant_acct.create_ndb_key() if partner_merchant_acct is not None else None
                                            )
        
        customer_entiteld_voucher.put()
        
        #customer_acct.update_after_added_voucher(customer_entiteld_voucher)
        
        return customer_entiteld_voucher
        
        
    @staticmethod
    def get_by_redeem_code(redeem_code):
        return  CustomerEntitledVoucher.query(CustomerEntitledVoucher.redeem_code==redeem_code).get()
    
    @staticmethod
    def list_by_customer(customer, limit=conf.MAX_FETCH_RECORD, offset=0, voucher_status=program_conf.REWARD_STATUS_VALID):
        return CustomerEntitledVoucher.query(ndb.AND(CustomerEntitledVoucher.status==voucher_status),
                ancestor=customer.create_ndb_key()).fetch(limit=limit, offset=offset)
    
    '''
    @staticmethod
    def list_all_by_customer(customer, limit=conf.MAX_FETCH_RECORD, offset=0):
        return CustomerEntitledVoucher.query(ancestor=customer.create_ndb_key()).fetch(limit=limit, offset=offset)
    '''
        
    @staticmethod
    def update_customer_entiteld_voucher_summary(customer, voucher_status=program_conf.REWARD_STATUS_VALID):
        customers_vouchers_list = CustomerEntitledVoucher.list_by_customer(customer, voucher_status=voucher_status)
        entitled_voucher_summary   = {}
        if customers_vouchers_list:
            
            for customer_voucher in customers_vouchers_list:
                merchant_voucher        = customer_voucher.merchant_voucher_entity
                merchant_voucher_key    = customer_voucher.merchant_voucher_key
                voucher_summary         = entitled_voucher_summary.get(merchant_voucher_key)
                new_redeem_info         = {
                                            'redeem_code'       : customer_voucher.redeem_code,
                                            'effective_date'    : customer_voucher.effective_date.strftime('%d-%m-%Y'),
                                            'expiry_date'       : customer_voucher.expiry_date.strftime('%d-%m-%Y'),
                                            'is_redeem'         : False,
                                            }    
                if voucher_summary:
                    entitled_voucher_summary[merchant_voucher_key]['key']=merchant_voucher_key
                    entitled_voucher_summary[merchant_voucher_key]['redeem_info_list'].append(new_redeem_info)
                    
                else:
                    entitled_voucher_summary[merchant_voucher_key]={
                                                                    'key'               : merchant_voucher_key,
                                                                    'label'             : merchant_voucher.label,
                                                                    'image_url'         : merchant_voucher.image_public_url,
                                                                    'redeem_info_list'  : [new_redeem_info]
                                                                    }
        
        customer.entitled_voucher_summary = entitled_voucher_summary
        customer.put()

class CustomerEntitledTierRewardSummary(BaseNModel, DictModel):
    '''
    Customer as ancestor
    
    tier_summary consist of list of tier_details details
    
    where, tier_details is like below
    
    tier_details = {
                            'tier_index'                : ...,
                            'tier_label'                : ...,
                            'unlock_tier_message'       : ...,
                            'unlock_status'             : ...,
                            'unlock_condition'          : ...,
                            'unlock_condition_value'    : ..., 
                            }
    
    
    '''
    tier_reward_program     = ndb.KeyProperty(name='tier_reward_program', kind=MerchantTierRewardProgram)
    cycle_start_datetime    = ndb.DateTimeProperty(required=True, auto_now_add=True)
    cycle_end_datetime      = ndb.DateTimeProperty(required=False)
    program_end_date        = ndb.DateProperty(required=True)
    tier_summary            = ndb.JsonProperty()
    is_valid                = ndb.BooleanProperty(required=True, default=True)
    allow_recycle           = ndb.BooleanProperty(required=True, default=True)
    modified_datetime       = ndb.DateTimeProperty(required=True, auto_now=True)
    
    dict_properties     = [
                            'cycle_start_datetime', 'cycle_end_datetime', 'is_valid', 'program_end_date', 'tier_summary',
                            
                            ]
    
    @property
    def cycle_completed_datetime(self):
        return self.cycle_end_datetime
    
    @property
    def tier_reward_program_entity(self):
        return MerchantTierRewardProgram.fetch(self.tier_reward_program.urlsafe())
    
    @property
    def is_cycle_completed(self):
        is_completed = True
        if self.tier_summary:
            for tier_details in self.tier_summary.get('tiers'):
                if tier_details.get('unlock_status') == False:
                    is_completed = False
                    break
        return is_completed
    
    def to_program_tier_status_summary(self):
        tier_details_list           = self.tier_summary.get('tiers')
        tier_reward_program         = self.tier_reward_program_entity
        
        last_completed_unlock_condition_value   = 0
        found_incomplete_tier                   = False
        
        for tier_details in tier_details_list:
            if tier_details.get('unlock_status'):
                last_completed_unlock_condition_value   = int(tier_details.get('unlock_condition_value'))
                tier_details['completed_percentage']    = 100 
            else:
                tier_unlock_value           = int(tier_details.get('unlock_value')) or 0
                tier_unlock_condition_value = int(tier_details.get('unlock_condition_value'))
                if found_incomplete_tier:
                    tier_completed_percentage = '0'
                else:
                    if tier_unlock_value>0:
                        tier_completed_percentage = '%.2f' % (100*(tier_unlock_value-last_completed_unlock_condition_value)/(tier_unlock_condition_value-last_completed_unlock_condition_value))
                    else:
                        tier_completed_percentage = '%.2f' % (100*tier_unlock_value/tier_unlock_condition_value)
                
                tier_details['completed_percentage'] = tier_completed_percentage
                
                found_incomplete_tier = True
                
        return {
                'label'                 : tier_reward_program.label,
                'tiers'                 : tier_details_list,
                'cycle_start_datetime'  : convert_to_serializable_value(self.cycle_start_datetime),
                'end_date'              : convert_to_serializable_value(tier_reward_program.end_date),
                }
    
    @staticmethod
    def list_all_by_customer(customer, limit = conf.MAX_FETCH_RECORD, offset=0):
        return CustomerEntitledTierRewardSummary.query(ancestor=customer.create_ndb_key()).fetch(offset=offset, limit=limit)
    
    @staticmethod
    def delete_all_by_customer(customer):
        result = CustomerEntitledTierRewardSummary.query(ancestor=customer.create_ndb_key()).fetch(limit=conf.MAX_FETCH_RECORD)
        for r in result:
            r.delete()
        
    @staticmethod
    def list_tier_reward_summary_by_customer(customer_acct):
        today = datetime.utcnow().date()
        return CustomerEntitledTierRewardSummary.query(ndb.AND(
                                                            CustomerEntitledTierRewardSummary.is_valid==True, 
                                                            CustomerEntitledTierRewardSummary.program_end_date>=today
                                                            ),
                                                        ancestor = customer_acct.create_ndb_key()
                                                    ).fetch(limit=conf.MAX_FETCH_RECORD)
    
    @staticmethod
    def get_customer_tier_reward_program_summary(customer_acct, tier_reward_program):
        tier_reward_summary         = CustomerEntitledTierRewardSummary.query(
                                                                    ndb.AND(
                                                                        CustomerEntitledTierRewardSummary.tier_reward_program==tier_reward_program.create_ndb_key() 
                                                                        ),
                                                                    ancestor=customer_acct.create_ndb_key()).get()
    
        return tier_reward_summary
    
    @staticmethod
    def create(customer_acct, tier_reward_program, cycle_start_datetime=None):
        
        if cycle_start_datetime is None:
            cycle_start_datetime = datetime.utcnow()
        
        tier_setting_list = tier_reward_program.program_tiers
        tier_reward_summary_list = []
        for tier_setting in tier_setting_list:
            tier_summary = {
                            'tier_index'                : tier_setting.get('tier_index'),
                            'tier_label'                : tier_setting.get('tier_label'),
                            'unlock_tier_message'       : tier_setting.get('unlock_tier_message'),
                            'unlock_status'             : False,
                            'unlock_condition'          : tier_setting.get('unlock_tier_condition'),
                            'unlock_condition_value'    : tier_setting.get('unlock_tier_condition_value'), 
                            'unlock_value'              : .0,
                            'unlock_source_details'     : {},
                            }
            
            
              
            tier_reward_summary_list.append(tier_summary)  
            
        
        reward_summary = CustomerEntitledTierRewardSummary(
                                            parent                  = customer_acct.create_ndb_key(),
                                            tier_reward_program     = tier_reward_program.create_ndb_key(),
                                            program_end_date        = tier_reward_program.end_date,
                                            cycle_start_datetime    = cycle_start_datetime,
                                            tier_summary            = {'tiers': tier_reward_summary_list},
                                            allow_recycle           = tier_reward_program.is_tier_recycle,
                                            )
        
        reward_summary.put()
        
        return reward_summary
    
    @staticmethod
    def update(customer_tier_reward_summary, tier_summary_list=None, cycle_start_datetime=None, is_cycle_completed=False):
        if cycle_start_datetime:
            customer_tier_reward_summary.cycle_start_datetime = cycle_start_datetime
        
        if is_cycle_completed:
            customer_tier_reward_summary.cycle_end_datetime = datetime.utcnow()
        
        
        customer_tier_reward_summary.tier_summary = tier_summary_list
        
        logger.debug('update CustomerEntitledTierRewardSummary with customer_tier_reward_summary=%s', customer_tier_reward_summary)
        customer_tier_reward_summary.put()
        
    @staticmethod
    def restart_cycle(customer_tier_reward_summary, cycle_start_datetime=None):
        if cycle_start_datetime is None:
            customer_tier_reward_summary.cycle_start_datetime   = datetime.utcnow()
        else:
            customer_tier_reward_summary.cycle_start_datetime   = cycle_start_datetime
            
        customer_tier_reward_summary.cycle_end_datetime     = None
        
        tier_details_list = customer_tier_reward_summary.tier_summary.get('tiers')
        
        for tier_details in tier_details_list:
            tier_details['unlock_status']           = False
            tier_details['unlock_datetime']         = None
            tier_details['unlock_value']            = .0
            tier_details['unlock_source_details']   = {}
        
        logger.debug('tier_details_list=%s', tier_details_list)
            
        customer_tier_reward_summary.tier_summary['ties'] = tier_details_list
        
        customer_tier_reward_summary.put()    
        
        
    
class VoucherRewardDetailsForUpstreamData(object):    
    '''
    For Upstream purpose
    '''
    def __init__(self, voucher_key, reward_amount, expiry_date, rewarded_datetime, merchant_acct=None):
        self.merchant_acct      = merchant_acct
        self.voucher_key        = voucher_key
        self.reward_amount      = reward_amount
        if isinstance(expiry_date, string_types):
            self.expiry_date        = datetime.strptime(expiry_date, '%d-%m-%Y').date()
        else:
            self.expiry_date = expiry_date
        self.rewarded_datetime  = rewarded_datetime
        
    def __repr__(self, *args, **kwargs):
        return 'voucher_key=%s, reward_amount=%d, expiry_date=%s, rewarded_datetime=%s' % (self.voucher_key, self.reward_amount, self.expiry_date, self.rewarded_datetime)    
        
    @property
    def reward_format(self):
        return program_conf.REWARD_FORMAT_VOUCHER
    
    @property
    def reward_format_key(self):
        return self.voucher_key
    
    @property
    def rewarded_datetime_with_gmt(self):
        gmt_hour = self.merchant_acct.gmt_hour
        
        return self.rewarded_datetime + timedelta(hours=gmt_hour)
    