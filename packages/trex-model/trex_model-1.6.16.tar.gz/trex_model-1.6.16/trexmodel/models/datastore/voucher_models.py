'''
Created on 10 Mar 2021

@author: jacklok
'''
from google.cloud import ndb
from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel
import trexmodel.conf as model_conf
from trexlib.utils.string_util import is_not_empty
from trexmodel.models.datastore.merchant_models import MerchantAcct, \
    MerchantUser
import logging
from trexconf import program_conf
from datetime import datetime
from trexmodel.program_conf import VOUCHER_REWARD_TYPE,\
    VOUCHER_REWARD_MAX_QUANTITY,\
    VOUCHER_REWARD_PRICE, VOUCHER_REWARD_BRAND,\
    VOUCHER_REWARD_MIN_SALES_AMOUNT,\
    VOUCHER_REWARD_DISCOUNT_RATE,\
    VOUCHER_REWARD_TYPE_DISCOUNT,\
    VOUCHER_REWARD_PRODUCT_SKU,\
    VOUCHER_REWARD_PRODUCT_CATEGORY, VOUCHER_REWARD_CASH,\
    VOUCHER_REWARD_TYPE_CASH,\
    VOUCHER_REWARD_ACTION_DATA,\
    VOUCHER_REWARD_TYPE_PRODUCT, VOUCHER_REWARD_TYPE
from google.auth._default import default

logger = logging.getLogger('model')

class VoucherBase(BaseNModel, DictModel):
    label                   = ndb.StringProperty(required=True)
    desc                    = ndb.StringProperty(required=False)
    terms_and_conditions    = ndb.TextProperty(required=False)
    voucher_type            = ndb.StringProperty(required=True, choices=set(program_conf.VOUCHER_TYPE))
    completed_status        = ndb.StringProperty(required=True, choices=set(program_conf.VOUCHER_STATUS))
    configuration           = ndb.JsonProperty(required=False, default={})
    
    created_datetime        = ndb.DateTimeProperty(required=True, auto_now_add=True)
    modified_datetime       = ndb.DateTimeProperty(required=True, auto_now=True)
    published_datetime      = ndb.DateTimeProperty(required=False)
    archived_datetime       = ndb.DateTimeProperty(required=False)
    
    created_by              = ndb.KeyProperty(name="created_by", kind=MerchantUser)
    created_by_username     = ndb.StringProperty(required=False)
    
    modified_by             = ndb.KeyProperty(name="modified_by", kind=MerchantUser)
    modified_by_username    = ndb.StringProperty(required=False)
    
    archived                = ndb.BooleanProperty(default=False)
    enabled                 = ndb.BooleanProperty(default=True)
    image_storage_filename  = ndb.StringProperty(required=False)
    image_public_url        = ndb.StringProperty(required=False)
    
    redeem_limit_type       = ndb.StringProperty(required=False, default=program_conf.REDEEM_LIMIT_TYPE_PER_RECEIPT)
    redeem_limit_count      = ndb.IntegerProperty(required=False, default=1)
    
    dict_properties         = ['label', 'voucher_type', 'desc', 'terms_and_conditions', 'configuration', 'created_datetime', 'modified_datetime', 'completed_status', 
                               'created_by_username', 'modified_by_username', 'is_published', 'is_archived', 'is_enabled',
                               'redeem_limit_type', 'redeem_limit_count',  
                               'image_public_url','image_storage_filename']
    
    @property
    def is_archived(self):
        return self.archived
    
    @property
    def is_enabled(self):
        return self.enabled
    
    @property
    def is_published(self):
        return self.completed_status == program_conf.VOUCHER_STATUS_PUBLISH
    
class MerchantVoucher(VoucherBase):
    
    dict_properties         = ['label', 'voucher_type', 'desc', 'terms_and_conditions', 'configuration', 'created_datetime', 'modified_datetime', 'completed_status', 
                               'created_by_username', 'modified_by_username', 'is_published', 'is_archived', 'is_enabled', 
                               'image_public_url','image_storage_filename', 
                               'redeem_limit_type', 'redeem_limit_count',
                               'cash_amount', 'discount_rate', 'product_category', 'product_sku', 'min_sales_amount', 'applicable_product_category', 
                               'applicable_product_brand', 'product_price', 'max_quantity',
                               ]
    
    @property
    def cash_amount(self):
        if self.configuration and VOUCHER_REWARD_CASH in self.configuration[VOUCHER_REWARD_ACTION_DATA].keys():
            if VOUCHER_REWARD_TYPE_CASH == self.configuration[VOUCHER_REWARD_TYPE]:
                return self.configuration[VOUCHER_REWARD_ACTION_DATA][VOUCHER_REWARD_CASH]
        else:
            return .0        
    @property
    def discount_rate(self):
        if self.configuration:
            if VOUCHER_REWARD_TYPE_DISCOUNT == self.configuration[VOUCHER_REWARD_TYPE] and VOUCHER_REWARD_DISCOUNT_RATE in self.configuration[VOUCHER_REWARD_ACTION_DATA].keys():
                return self.configuration[VOUCHER_REWARD_ACTION_DATA][VOUCHER_REWARD_DISCOUNT_RATE]
        
        return .0             
    
    @property
    def product_category(self):
        if self.configuration and VOUCHER_REWARD_PRODUCT_CATEGORY in self.configuration[VOUCHER_REWARD_ACTION_DATA].keys():
            if VOUCHER_REWARD_TYPE_PRODUCT == self.configuration[VOUCHER_REWARD_TYPE]:
                return self.configuration[VOUCHER_REWARD_ACTION_DATA][VOUCHER_REWARD_PRODUCT_CATEGORY]
            
    @property
    def product_sku(self):
        if self.configuration and VOUCHER_REWARD_PRODUCT_SKU in self.configuration[VOUCHER_REWARD_ACTION_DATA].keys():
            if VOUCHER_REWARD_TYPE_PRODUCT == self.configuration[VOUCHER_REWARD_TYPE]:
                return self.configuration[VOUCHER_REWARD_ACTION_DATA][VOUCHER_REWARD_PRODUCT_SKU]                    
            
    
    @property
    def min_sales_amount(self):
        if self.configuration and VOUCHER_REWARD_MIN_SALES_AMOUNT in self.configuration[VOUCHER_REWARD_ACTION_DATA].keys():
            return self.configuration[VOUCHER_REWARD_ACTION_DATA][VOUCHER_REWARD_MIN_SALES_AMOUNT]
        else:
            return .0
        
    @property
    def max_quantity(self):
        if self.configuration and VOUCHER_REWARD_MAX_QUANTITY in self.configuration[VOUCHER_REWARD_ACTION_DATA].keys():
            return self.configuration[VOUCHER_REWARD_ACTION_DATA][VOUCHER_REWARD_MAX_QUANTITY]    
        else:
            return 1
        
    @property
    def product_price(self):
        if self.configuration:
            if VOUCHER_REWARD_TYPE_PRODUCT == self.configuration[VOUCHER_REWARD_TYPE] and VOUCHER_REWARD_PRICE in self.configuration[VOUCHER_REWARD_ACTION_DATA].keys():
                return self.configuration[VOUCHER_REWARD_ACTION_DATA][VOUCHER_REWARD_PRICE]    
            
        return .0        
        
    @property
    def applicable_product_category(self):
        if self.configuration:
            return self.configuration[VOUCHER_REWARD_ACTION_DATA][VOUCHER_REWARD_PRODUCT_CATEGORY]
        
    @property
    def applicable_product_brand(self):
        if self.configuration:
            return self.configuration[VOUCHER_REWARD_ACTION_DATA][VOUCHER_REWARD_BRAND]        
    
    @property
    def rebuild_configuration(self):
        new_configuration = self.configuration
        if new_configuration:
            if VOUCHER_REWARD_TYPE_DISCOUNT == new_configuration[VOUCHER_REWARD_TYPE]:
                new_configuration[VOUCHER_REWARD_ACTION_DATA][VOUCHER_REWARD_MAX_QUANTITY] = 1
            elif VOUCHER_REWARD_TYPE_CASH == new_configuration[VOUCHER_REWARD_TYPE]:
                new_configuration[VOUCHER_REWARD_ACTION_DATA][VOUCHER_REWARD_MAX_QUANTITY] = self.max_quantity
            elif VOUCHER_REWARD_TYPE_PRODUCT == new_configuration[VOUCHER_REWARD_TYPE]:
                new_configuration[VOUCHER_REWARD_ACTION_DATA][VOUCHER_REWARD_MAX_QUANTITY] = self.max_quantity
        
        return new_configuration
    
    @staticmethod
    def construct_cash_voucher_configuration(amount, category=None, brand=None, min_sales_amount=.0, max_quantity=1):
        return {
                VOUCHER_REWARD_TYPE         : VOUCHER_REWARD_TYPE_CASH,
                VOUCHER_REWARD_ACTION_DATA  : {
                                                VOUCHER_REWARD_CASH             : amount,
                                                VOUCHER_REWARD_MIN_SALES_AMOUNT : min_sales_amount,
                                                VOUCHER_REWARD_PRODUCT_CATEGORY : category,
                                                VOUCHER_REWARD_BRAND            : brand,
                                                VOUCHER_REWARD_MAX_QUANTITY     : max_quantity,    
                                                },
                }
    
    @staticmethod
    def construct_discount_voucher_configuration(discount_rate, category=None, brand=None, min_sales_amount=.0):
        return {
                VOUCHER_REWARD_TYPE         : VOUCHER_REWARD_TYPE_DISCOUNT,
                VOUCHER_REWARD_ACTION_DATA  : {
                                                
                                                VOUCHER_REWARD_DISCOUNT_RATE    : discount_rate,
                                                VOUCHER_REWARD_MIN_SALES_AMOUNT : min_sales_amount,
                                                VOUCHER_REWARD_PRODUCT_CATEGORY : category,
                                                VOUCHER_REWARD_BRAND            : brand, 
                                                VOUCHER_REWARD_MAX_QUANTITY     : 1,    
                                                },
                }
        
    @staticmethod
    def construct_product_voucher_configuration(product_sku, category=None, brand=None, min_sales_amount=.0, price=.0, max_quantity=1):
        return {
                VOUCHER_REWARD_TYPE         : VOUCHER_REWARD_TYPE_PRODUCT,
                VOUCHER_REWARD_ACTION_DATA  : {
                                                
                                                VOUCHER_REWARD_PRODUCT_SKU      : product_sku,
                                                VOUCHER_REWARD_MIN_SALES_AMOUNT : min_sales_amount,
                                                VOUCHER_REWARD_PRODUCT_CATEGORY : category,
                                                VOUCHER_REWARD_BRAND            : brand,
                                                VOUCHER_REWARD_PRICE            : price,  
                                                VOUCHER_REWARD_MAX_QUANTITY     : max_quantity,     
                                                },
                }    
    
    @property
    def merchant_acct(self):
        return MerchantAcct.fetch(self.key.parent().urlsafe())
    
    def to_voucher_configuration(self):
        voucher_configuration = {
                                'label'                 : self.label,
                                'voucher_key'           : self.key_in_str,
                                'voucher_configuration' : self.configuration,
                                'desc'                  : self.desc,
                                'terms_and_conditions'  : self.terms_and_conditions,
                                'image_url'             : self.image_public_url,
                                }
        
        return voucher_configuration
    
    
    
    @staticmethod
    def create(merchant_acct, label=None, voucher_type=None, desc=None, terms_and_conditions=None, 
               voucher_image_url=None, created_by=None, redeem_limit_type='day', redeem_limit_count=1):
        
        created_by_username = None
        if is_not_empty(created_by):
            if isinstance(created_by, MerchantUser):
                created_by_username = created_by.username
        
        
        merchant_voucher =  MerchantVoucher(
                                        parent                  = merchant_acct.create_ndb_key(),
                                        label                   = label,
                                        voucher_type            = voucher_type,
                                        desc                    = desc,
                                        terms_and_conditions    = terms_and_conditions,
                                        redeem_limit_type       = redeem_limit_type,
                                        redeem_limit_count      = redeem_limit_count,
                                        created_by              = created_by.create_ndb_key(),
                                        created_by_username     = created_by_username,
                                        configuration           = {},
                                        completed_status        = program_conf.VOUCHER_STATUS_BASE,
                                        image_public_url        = voucher_image_url,
                                        )
        
        merchant_voucher.put()
        return merchant_voucher
    
    @staticmethod
    def update_voucher_base_data(merchant_voucher, label=None, voucher_type=None, desc=None, 
                                 terms_and_conditions=None, modified_by=None, 
                                 redeem_limit_type='day', redeem_limit_count=1):
        
        modified_by_username = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        merchant_voucher.label                  = label
        merchant_voucher.voucher_type           = voucher_type
        merchant_voucher.desc                   = desc
        merchant_voucher.terms_and_conditions   = terms_and_conditions
        merchant_voucher.redeem_limit_type      = redeem_limit_type
        merchant_voucher.redeem_limit_count     = redeem_limit_count
        
        merchant_voucher.modified_by            = modified_by.create_ndb_key()
        merchant_voucher.modified_by_username   = modified_by_username
        
        if merchant_voucher.completed_status!=program_conf.VOUCHER_STATUS_BASE:
            merchant_voucher.completed_status       = program_conf.VOUCHER_STATUS_PUBLISH
        
        merchant_voucher.put()
        
        return merchant_voucher
    
    @staticmethod
    def update_voucher_configuration_data(merchant_voucher, configuration=None, modified_by=None, image_public_url=None):
        
        modified_by_username = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        merchant_voucher.configuration          = configuration
        merchant_voucher.completed_status       = program_conf.VOUCHER_STATUS_CONFIGURATION
        merchant_voucher.modified_by            = modified_by.create_ndb_key()
        merchant_voucher.modified_by_username   = modified_by_username
        if image_public_url:
            merchant_voucher.image_public_url   = image_public_url
        
        merchant_voucher.put()
        
        return merchant_voucher
    
    @staticmethod
    def update_voucher_material(merchant_voucher, image_public_url=None, image_storage_filename=None, modified_by=None):
        
        modified_by_username = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        merchant_voucher.image_public_url       = image_public_url
        merchant_voucher.image_storage_filename = image_storage_filename
        
        if merchant_voucher.completed_status!=program_conf.VOUCHER_STATUS_PUBLISH:
            merchant_voucher.completed_status       = program_conf.VOUCHER_STATUS_UPLOAD_MATERIAL 
        
        merchant_voucher.modified_by            = modified_by.create_ndb_key()
        merchant_voucher.modified_by_username   = modified_by_username
        
        merchant_voucher.put()
        
        return merchant_voucher
    
    @staticmethod
    def update_voucher_material_uploaded(merchant_voucher, modified_by=None):
        
        modified_by_username = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        merchant_voucher.completed_status       = program_conf.VOUCHER_STATUS_UPLOAD_MATERIAL
        merchant_voucher.modified_by            = modified_by.create_ndb_key()
        merchant_voucher.modified_by_username   = modified_by_username
        
        merchant_voucher.put()
        
        return merchant_voucher
    
    @staticmethod
    def publish_voucher(voucher):
        voucher.completed_status    = program_conf.VOUCHER_STATUS_PUBLISH
        voucher.apublished_datetime = datetime.now()
        voucher.put()
        
        merchant_acct = voucher.merchant_acct
        merchant_acct.add_voucher(voucher.to_voucher_configuration())    
        
    @staticmethod
    def archive_voucher(voucher):
        voucher.archived = True
        voucher.archived_datetime = datetime.now()
        voucher.put()
        
        merchant_acct = voucher.merchant_acct
        merchant_acct.remove_voucher(voucher.key_in_str)
        
        
    @staticmethod
    def disable_voucher(voucher):
        voucher.enabled = False
        voucher.put()
        
        merchant_acct = voucher.merchant_acct
        merchant_acct.remove_voucher(voucher.key_in_str)
        
        
    @staticmethod
    def enable_voucher(voucher):
        voucher.enabled = True
        voucher.put()
        
        merchant_acct = voucher.merchant_acct
        merchant_acct.add_voucher(voucher.to_voucher_configuration())     
    
    @staticmethod    
    def list_by_voucher_key_list(voucher_key_list):
        ndb_keys_list = []
        for k in voucher_key_list:
            ndb_keys_list.append(ndb.Key(urlsafe=k))
        
        return MerchantVoucher.fetch_multi(ndb_keys_list)        
    
    @staticmethod
    def list_all_by_merchant_account(merchant_acct):
        return MerchantVoucher.query(ancestor=merchant_acct.create_ndb_key()).fetch(limit=model_conf.MAX_FETCH_RECORD)
    
    @staticmethod
    def list_by_merchant_account(merchant_acct):
        vouchers_list = MerchantVoucher.query(ndb.AND(MerchantVoucher.completed_status==program_conf.VOUCHER_STATUS_PUBLISH), ancestor=merchant_acct.create_ndb_key()).fetch(limit=model_conf.MAX_FETCH_RECORD)
        final_list = []
        for v in vouchers_list:
            if v.archived==False:
                final_list.append(v)
        return final_list
    
    @staticmethod
    def list_latest_by_merchant_account(merchant_acct):
        vouchers_list = MerchantVoucher.query(ndb.AND(MerchantVoucher.archived==False), ancestor=merchant_acct.create_ndb_key()).fetch(limit=model_conf.MAX_FETCH_RECORD)
        final_list = []
        for v in vouchers_list:
            final_list.append(v)
        return final_list
    
    @staticmethod
    def list_archived_by_merchant_account(merchant_acct):
        return MerchantVoucher.query(ndb.AND(MerchantVoucher.archived==True), ancestor=merchant_acct.create_ndb_key()).fetch(limit=model_conf.MAX_FETCH_RECORD)
    
    @staticmethod
    def list_published_by_merchant_account(merchant_acct):
        return MerchantVoucher.query(ndb.AND(MerchantVoucher.completed_status==program_conf.VOUCHER_STATUS_PUBLISH), ancestor=merchant_acct.create_ndb_key()).fetch(limit=model_conf.MAX_FETCH_RECORD)
    
    
        
class BrandVouhcer(VoucherBase):
    #merchant_acct           = ndb.KeyProperty(name="merchant_acct", kind=MerchantAcct)
    pass
