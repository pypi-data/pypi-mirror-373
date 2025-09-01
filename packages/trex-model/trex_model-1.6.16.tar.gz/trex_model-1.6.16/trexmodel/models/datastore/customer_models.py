'''
Created on 5 Jan 2021

@author: jacklok
'''
from google.cloud import ndb
from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel, FullTextSearchable
from trexmodel.models.datastore.user_models import User
from trexmodel.models.datastore.merchant_models import MerchantAcct, Outlet,\
    MerchantUser
import trexmodel.conf as model_conf
from trexlib.utils.string_util import is_not_empty, is_empty
import logging
from trexlib.utils.common.date_util import convert_date_to_datetime,\
    to_day_of_year
from trexconf import conf, program_conf
from six import string_types
from datetime import datetime, timedelta
from trexmodel.models.datastore.membership_models import MerchantTierMembership,\
    MerchantMembership
from trexmodel.models.datastore.customer_model_helpers import update_customer_entiteld_voucher_summary_after_removed_voucher,\
    update_customer_entiteld_voucher_summary_with_customer_new_voucher,\
    update_customer_entiteld_voucher_summary_after_removed_voucher_by_redeem_code
    

logger = logging.getLogger('model')


class Customer(BaseNModel, DictModel, FullTextSearchable):
    
    #user_acct                   = ndb.KeyProperty(name="user_acct", kind=User)
    merchant_acct               = ndb.KeyProperty(name="merchant_acct", kind=MerchantAcct)
    outlet                      = ndb.KeyProperty(name="outlet", kind=Outlet)
    merchant_reference_code     = ndb.StringProperty(name="merchant_reference_code", required=False)
    registered_datetime         = ndb.DateTimeProperty(required=False, auto_now_add=True)
    modified_datetime           = ndb.DateTimeProperty(required=False, auto_now=True)
    
    #---------------------------------------------------------------------------
    # User denormalize fields
    #---------------------------------------------------------------------------
    name                        = ndb.StringProperty(required=False)
    mobile_phone                = ndb.StringProperty(required=False)
    email                       = ndb.StringProperty(required=False)
    
    birth_date                  = ndb.DateProperty(required=False, indexed=False)
    birth_date_date_str         = ndb.StringProperty(required=False) 
    birth_day_in_year           = ndb.IntegerProperty(required=False)
    gender                      = ndb.StringProperty(required=False)
    reference_code              = ndb.StringProperty(required=True)
    referral_code               = ndb.StringProperty(required=False)
    
    mobile_app_installed        = ndb.BooleanProperty(required=False, default=False)
    
    tags_list                   = ndb.StringProperty(repeated=True, write_empty_list=True)
    
    memberships_list            = ndb.StringProperty(repeated=True, write_empty_list=True)
    
    last_transact_datetime      = ndb.DateTimeProperty(required=False)
    previous_transact_datetime  = ndb.DateTimeProperty(required=False)
    
    last_redeemed_datetime      = ndb.DateTimeProperty(required=False)
    
    tier_membership             = ndb.KeyProperty(name="tier_membership", kind=MerchantTierMembership)
    previous_tier_membership    = ndb.KeyProperty(name="previous_tier_membership", kind=MerchantTierMembership)
    
    reward_summary                              = ndb.JsonProperty()
    prepaid_summary                             = ndb.JsonProperty()
    entitled_voucher_summary                    = ndb.JsonProperty()
    entitled_birthday_reward_summary            = ndb.JsonProperty()
    entitled_membership_reward_summary          = ndb.JsonProperty()
    entitled_lucky_draw_ticket_summary          = ndb.JsonProperty(required=False)
    
    referrer_code                               = ndb.StringProperty(required=False)
    
    kpi_summary                                 = ndb.JsonProperty()
    
    device_details                              = ndb.JsonProperty()
    
    fulltextsearch_field_name           = 'name'
    
    dict_properties     = ['name', 'mobile_phone', 'email', 'gender', 'birth_date', 'reference_code', 'merchant_reference_code',  
                           'tags_list', 'memberships_list', 'registered_merchant_acct', 'entitled_membership_reward_summary',
                           'reward_summary', 'entitled_voucher_summary', 'prepaid_summary', 'kpi_summary', 'entitled_lucky_draw_ticket_summary',
                           'entitled_birthday_reward_summary', 'tier_membership_key',
                           'registered_outlet_key', 'merchant_account_key', 
                           'registered_datetime', 'modified_datetime',
                           'registered_user_acct','referral_code', 'is_referred_by_friend',
                           
                           ]
    
    @property
    def customer_key(self):
        return self.key_in_str
    
    @property
    def is_any_entitled_voucher_active(self):
        
        today = datetime.utcnow().date()
        
        for voucher_key, voucher_info in self.entitled_voucher_summary:
            latest_expiry_date_str = voucher_info.get('latest_expiry_date')
            latest_expiry_date = datetime.strftime(latest_expiry_date_str, '%d-%m-%Y')
            if latest_expiry_date >= today:
                return True
        
        return False
    
    @property
    def registered_user_acct(self):
        #return User.fetch(self.user_acct.urlsafe())
        return User.get_by_reference_code(self.reference_code)
    
    @property
    def registered_user_acct_key(self):
        return self.key.parent().urlsafe().decode("utf-8")
    
    @property
    def registered_merchant_acct(self):
        #return MerchantAcct.fetch(self.merchant_acct.urlsafe())
        return self.merchant_acct.get()
    
    @property
    def registered_merchant_acct_key(self):
        if self.merchant_acct:
            return self.merchant_acct.urlsafe().decode("utf-8")
        
    @property
    def merchant_account_key(self):
        if self.merchant_acct:
            return self.merchant_acct.urlsafe().decode("utf-8")    
    
    @property
    def registered_outlet(self):
        if self.outlet:
            return Outlet.fetch(self.outlet.urlsafe())
    
    @property
    def registered_outlet_key(self):
        if self.outlet:
            return self.outlet.urlsafe().decode("utf-8")
    
    @property
    def merchant_memberships_list(self):
        _memberships_list = []
        for key in self.memberships_list:
            merchant_membership = MerchantMembership.fetch(key)
            _memberships_list.append(merchant_membership)
        
        return _memberships_list
    
    @property
    def tier_membership_key(self):
        if self.tier_membership:
            return self.tier_membership.urlsafe().decode("utf-8")
        
    @property
    def tier_membership_entity(self):
        if self.tier_membership:
            return MerchantTierMembership.fetch(self.tier_membership.urlsafe())    
    
    @property
    def is_referred_by_friend(self):
        return self.referrer_code is not None and is_not_empty(self.referrer_code)
    
    @staticmethod    
    def update_KPI(customer_acct, tags_list=None, memberships_list=None, tier_membership_key=None):
        if isinstance(tags_list, string_types):
            if is_not_empty(tags_list):
                tags_list = tags_list.split(',')
            else:
                tags_list = []
                
        if memberships_list is not None and isinstance(memberships_list, string_types):
            if is_not_empty(memberships_list):
                memberships_list = memberships_list.split(',')
            else:
                memberships_list = []
            
            customer_acct.memberships_list  = memberships_list
        
        tier_membership = None
        
        if tier_membership_key:
            tier_membership = MerchantTierMembership.fetch(tier_membership_key)        
            
            customer_acct.tier_membership   = tier_membership
            
        customer_acct.tags_list         = tags_list
        customer_acct.put()
        
    @staticmethod    
    def update_membership(customer_acct, memberships_list):
        if isinstance(memberships_list, string_types):
            if is_not_empty(memberships_list):
                memberships_list = memberships_list.split(',')
            else:
                memberships_list = []
        
        customer_acct.memberships_list  = memberships_list
        customer_acct.put()
        
    @staticmethod    
    def update_tier_membership(customer_acct, new_tier_membership):
        if customer_acct.tier_membership is not None:
            customer_acct.previous_tier_membership  = customer_acct.tier_membership
        
        customer_acct.tier_membership           = new_tier_membership.create_ndb_key()
        customer_acct.put()        
    
    @staticmethod
    def add_new_tickets_list_into_lucky_draw_ticket_summary(customer_acct, new_entitled_draw_tickets_list):
        
        logger.debug('new_entitled_draw_tickets_list=%s', new_entitled_draw_tickets_list)
        
        entitled_lucky_draw_ticket_summary = {}
        if customer_acct.entitled_lucky_draw_ticket_summary:
            entitled_lucky_draw_ticket_summary = customer_acct.entitled_lucky_draw_ticket_summary
        
        entitled_tickets_list = entitled_lucky_draw_ticket_summary.get('tickets') or []
        
        tickets_to_update_list = []
        
        #check before add
        for new_ticket in new_entitled_draw_tickets_list:
            check_ticket = next((obj for obj in entitled_tickets_list if obj.get('ticket_key') == new_ticket.get('ticket_key')), None)
            if check_ticket is None:
                logger.debug('Cannot find ticket, thus going to add ticket')
                tickets_to_update_list.append(new_ticket)
            else:
                logger.debug('Found ticket, thus ignore to avoid duplicated ticket')
                continue
        
        entitled_tickets_list.extend(tickets_to_update_list)
        
        entitled_lucky_draw_ticket_summary['tickets']    = entitled_tickets_list
        entitled_lucky_draw_ticket_summary['count']      = len(entitled_tickets_list)
        
        customer_acct.entitled_lucky_draw_ticket_summary = entitled_lucky_draw_ticket_summary
         
        
        customer_acct.put()
        
    @staticmethod
    def update_ticket_into_lucky_draw_ticket_summary(customer_acct, updated_draw_ticket):
        entitled_lucky_draw_ticket_summary = {}
        if customer_acct.entitled_lucky_draw_ticket_summary:
            entitled_lucky_draw_ticket_summary = customer_acct.entitled_lucky_draw_ticket_summary
        
        draw_tickets_list = entitled_lucky_draw_ticket_summary.get('tickets') or []
        
        new_tickets_list = []
        
        for ticket in draw_tickets_list:
            if ticket.get('ticket_key')!=updated_draw_ticket.get('ticket_key'):
                new_tickets_list.append(ticket)
            else:
                new_tickets_list.append(updated_draw_ticket)
                
        customer_acct.entitled_lucky_draw_ticket_summary['tickets'] = new_tickets_list
        customer_acct.put()
        
    @staticmethod
    def remove_ticket_from_lucky_draw_ticket_summary(customer_acct, removed_draw_ticket):
        logger.debug('removed_draw_ticket=%s', removed_draw_ticket)
        entitled_lucky_draw_ticket_summary = {}
        
        if customer_acct.entitled_lucky_draw_ticket_summary:
            entitled_lucky_draw_ticket_summary = customer_acct.entitled_lucky_draw_ticket_summary
        
        draw_tickets_list = entitled_lucky_draw_ticket_summary.get('tickets') or []
        
        new_tickets_list = []
        
        for ticket in draw_tickets_list:
            if ticket.get('ticket_key')!=removed_draw_ticket.get('ticket_key'):
                new_tickets_list.append(ticket)
            else:
                logger.debug('Found ticket to remove')
                
        customer_acct.entitled_lucky_draw_ticket_summary['tickets'] = new_tickets_list
        customer_acct.entitled_lucky_draw_ticket_summary['count']   = len(new_tickets_list)
        customer_acct.put()    
        
    @staticmethod
    def update_tickets_list_into_lucky_draw_ticket_summary(customer_acct, tickets_list):
        for ticket in tickets_list:
            ticket.patch_prize_image_base_url()
            Customer.update_ticket_into_lucky_draw_ticket_summary(customer_acct, ticket.to_configuration())
    
    @staticmethod    
    def list_by_customer_key_list(customer_keys_list):
        ndb_keys_list = []
        for k in customer_keys_list:
            ndb_keys_list.append(ndb.Key(urlsafe=k))
        
        return Customer.fetch_multi(ndb_keys_list)
    
    @classmethod
    def get_by_reference_code(cls, reference_code, merchant_acct):
        return cls.query(ndb.AND(cls.reference_code==reference_code, cls.merchant_acct==merchant_acct.create_ndb_key())).get()
    
    @classmethod
    def get_by_merchant_reference_code(cls, merchant_reference_code, merchant_acct):
        return cls.query(ndb.AND(cls.merchant_reference_code==merchant_reference_code, cls.merchant_acct==merchant_acct.create_ndb_key())).get()
    
    @classmethod
    def get_by_email(cls, email, merchant_acct=None):
        if merchant_acct:
            return cls.query(ndb.AND(cls.email==email, cls.merchant_acct==merchant_acct.create_ndb_key())).get()
        else:
            return cls.query(cls.email==email).get()
    
    @classmethod
    def get_by_mobile_phone(cls, mobile_phone, merchant_acct=None):
        
        if merchant_acct:
            return cls.query(ndb.AND(cls.mobile_phone==mobile_phone, cls.merchant_acct==merchant_acct.create_ndb_key())).get()
        else:
            return cls.query(cls.mobile_phone==mobile_phone).get()
    
    @classmethod
    def create(cls, outlet=None, name=None, email=None, mobile_phone=None, 
               merchant_reference_code=None, gender=None, birth_date=None,
               password=None, reference_code=None,
               is_email_verified=False, is_mobile_phone_verified=False):
        
        if is_not_empty(email):
            checking_user = User.get_by_email(email)
        elif is_not_empty(mobile_phone):
            checking_user = User.get_by_email(mobile_phone)
        
        if checking_user is not None:
            created_user = checking_user
            created_user.name           = name
            created_user.email          = email
            created_user.mobile_phone   = mobile_phone
            created_user.gender         = gender
            created_user.password       = password
            created_user.birth_date     = birth_date
        else:
            created_user = User.create(name=name, email=email, mobile_phone=mobile_phone, 
                                   gender=gender, birth_date=birth_date, 
                                   password=password, reference_code=reference_code,
                                   is_email_verified=is_email_verified, 
                                   is_mobile_phone_verified=is_mobile_phone_verified)
        
        created_user.put()
        created_customer = cls.create_from_user(outlet, created_user)
        created_customer.merchant_reference_code = merchant_reference_code
        created_customer.put()
        
        return created_customer
    
    @classmethod
    def update(cls, customer=None, outlet=None, **kwargs):
        if outlet:
            customer.outlet = outlet.create_ndb_key()
        
        logger.debug('**kwargs=%s', kwargs)
        
        mobile_phone    = kwargs.get('mobile_phone')
        
        if mobile_phone:
            mobile_phone = mobile_phone.replace(" ", "")
        
        kwargs['mobile_phone'] = mobile_phone
        
        for key, value in kwargs.items():
            setattr(customer, key, value)
            
        user_acct = customer.registered_user_acct
        
        User.update(user_acct=user_acct, **kwargs)
        '''
        user_acct.name                   = customer.name
        user_acct.email                  = customer.email
        user_acct.mobile_phone           = customer.mobile_phone
        user_acct.birth_date             = customer.birth_date
        user_acct.birth_date_date_str    = customer.birth_date_date_str
        user_acct.gender                 = customer.gender
        
        user_acct.put()
        '''
        customer.put()
        
    @classmethod
    def create_from_user(cls, outlet, user_acct, merchant_reference_code=None, merchant_acct=None, referrer_code=None):
        registered_merchant_acct       = outlet.merchant_acct_entity if merchant_acct is None else merchant_acct
        created_customer    = cls(
                               parent=user_acct.create_ndb_key(),
                               #user_acct                = user_acct.create_ndb_key(),  
                               outlet                   = outlet.create_ndb_key(), 
                               name                     = user_acct.name, 
                               email                    = user_acct.email, 
                               mobile_phone             = user_acct.mobile_phone, 
                               gender                   = user_acct.gender, 
                               reference_code           = user_acct.reference_code, 
                               referral_code            = user_acct.referral_code,
                               birth_date               = user_acct.birth_date, 
                               birth_date_date_str      = user_acct.birth_date_date_str, 
                               birth_day_in_year        = user_acct.birth_day_in_year,
                               merchant_reference_code  = merchant_reference_code,
                               referrer_code            = referrer_code,
                               merchant_acct            = registered_merchant_acct.create_ndb_key()
                           )
        
        created_customer.put()
        
        return created_customer
    
    @classmethod
    def list_last_active_customer_by_range(cls, merchant_acct,  last_active_date_since, last_active_date_end, 
                                          offset=0, limit=conf.MAX_FETCH_RECORD, start_cursor=None, return_with_cursor=False):
        query = cls.query(ndb.AND(
                            cls.merchant_acct==merchant_acct.create_ndb_key(),
                            cls.last_transact_datetime>=last_active_date_since,
                            cls.last_transact_datetime<last_active_date_end,
                            
                            )).order(-cls.last_transact_datetime)
        
        return cls.list_all_with_condition_query(query, offset=offset, limit=limit, start_cursor=start_cursor, return_with_cursor=return_with_cursor)
    
    @classmethod
    def count_last_active_customer_by_range(cls, merchant_acct,  last_active_date_since, last_active_date_end, limit=conf.MAX_FETCH_RECORD,):
        query = cls.query(ndb.AND(
                            cls.merchant_acct==merchant_acct.create_ndb_key(),
                            cls.last_transact_datetime>=last_active_date_since,
                            cls.last_transact_datetime<=last_active_date_end,
                            
                            ))
        
        return cls.count_with_condition_query(query)
    
    @classmethod
    def list(cls, offset=0, limit=conf.MAX_FETCH_RECORD, start_cursor=None, return_with_cursor=False, keys_only=False):
        query = cls.query()
        
        return cls.list_all_with_condition_query(query, offset=offset, limit=limit, start_cursor=start_cursor, return_with_cursor=return_with_cursor, keys_only=keys_only)
    
    @classmethod
    def list_merchant_customer_by_date_of_birth(cls, merchant_acct, date_of_birth, offset=0, limit=conf.MAX_FETCH_RECORD, start_cursor=None, return_with_cursor=False, keys_only=False):
        query = cls.query(ndb.AND(cls.merchant_acct==merchant_acct.create_ndb_key(), cls.birth_date_date_str==date_of_birth))
        
        return cls.list_all_with_condition_query(query, offset=offset, limit=limit, start_cursor=start_cursor, return_with_cursor=return_with_cursor, keys_only=keys_only)
    
    @classmethod
    def list_merchant_customer_by_date_of_birth_thru_date_range(cls, merchant_acct, date_range_start=None, date_range_end=None, offset=0, limit=conf.MAX_FETCH_RECORD, start_cursor=None, return_with_cursor=False, keys_only=False):
        date_range_start_day_in_year    = to_day_of_year(date_range_start)
        date_range_end_day_in_year      = to_day_of_year(date_range_end)
        
        query = cls.query(ndb.AND(cls.merchant_acct==merchant_acct.create_ndb_key(), cls.birth_day_in_year>=date_range_start_day_in_year, cls.birth_day_in_year<=date_range_end_day_in_year))
        
        return cls.list_all_with_condition_query(query, offset=offset, limit=limit, start_cursor=start_cursor, return_with_cursor=return_with_cursor, keys_only=keys_only)
    
    @classmethod
    def count_merchant_customer_by_date_of_birth(cls, merchant_acct, date_of_birth, limit=conf.MAX_FETCH_RECORD):
        query = cls.query(ndb.AND(cls.merchant_acct==merchant_acct.create_ndb_key(), cls.birth_date_date_str==date_of_birth))
        
        return cls.count_with_condition_query(query, limit=limit)
    
    @classmethod
    def list_merchant_customer(cls, merchant_acct, offset=0, limit=conf.PAGINATION_SIZE, start_cursor=None, return_with_cursor=False):
        query = cls.query(ndb.AND(cls.merchant_acct==merchant_acct.create_ndb_key()))
        
        return cls.list_all_with_condition_query(query, offset=offset, limit=limit, start_cursor=start_cursor, return_with_cursor=return_with_cursor)
    
    @classmethod
    def list_by_user_account(cls, user_acct):
        return cls.query(ancestor=user_acct.create_ndb_key()).fetch(limit=conf.MAX_FETCH_RECORD)
    
    @classmethod
    def list_paginated_by_user_account(cls, user_acct, limit=conf.MAX_FETCH_RECORD, start_cursor=None):
        query = cls.query(ancestor=user_acct.create_ndb_key())
        
        return cls.list_all_with_condition_query(query, limit=limit, start_cursor=start_cursor, return_with_cursor=True, keys_only=False)
    
    @classmethod
    def count_merchant_customer(cls, merchant_acct):
        if merchant_acct:
            query = cls.query(ndb.AND(cls.merchant_acct==merchant_acct.create_ndb_key()))
        else:
            query = cls.query()
        
        return cls.count_with_condition_query(query)
    
    @classmethod
    def search_merchant_customer(cls, merchant_acct, name=None, email=None, mobile_phone=None, 
                                 reference_code=None, merchant_reference_code=None, merchant_tagging=None,
                                 registered_date_start=None, registered_date_end=None,
                                 offset=0, start_cursor=None, limit=model_conf.MAX_FETCH_RECORD):
        
        search_text_list = None
        query = cls.query(ndb.AND(cls.merchant_acct==merchant_acct.create_ndb_key()))
        
        if is_not_empty(email):
            query = query.filter(cls.email==email)
            
        elif is_not_empty(mobile_phone):
            query = query.filter(cls.mobile_phone==mobile_phone)
            
        elif is_not_empty(reference_code):
            query = query.filter(cls.reference_code==reference_code)
            
        elif is_not_empty(merchant_reference_code):
            query = query.filter(cls.merchant_reference_code==merchant_reference_code)
                    
        elif is_not_empty(merchant_tagging):
            query = query.filter(cls.tags_list==merchant_tagging)
        
        elif is_not_empty(name):
            search_text_list = name.split(' ')
        
        elif is_not_empty(registered_date_start) or is_not_empty(registered_date_end):
            
            if is_not_empty(registered_date_start):
                registered_datetime_start = convert_date_to_datetime(registered_date_start)
                
                query = query.filter(cls.registered_datetime>=registered_datetime_start)
            
            if is_not_empty(registered_date_end):
                registered_datetime_end = convert_date_to_datetime(registered_date_end)
            
                query = query.filter(cls.registered_datetime<registered_datetime_end)
        
        total_count                         = cls.full_text_count(search_text_list, query, conf.MAX_FETCH_RECORD_FULL_TEXT_SEARCH)
        
        (search_results, next_cursor)       = cls.full_text_search(search_text_list, query, offset=offset, 
                                                                   start_cursor=start_cursor, return_with_cursor=True, 
                                                                   limit=limit)
        
        return (search_results, total_count, next_cursor)
    
    @staticmethod
    def update_all_from_user_acct(user_acct):
        customers_list  = Customer.list_by_user_account(user_acct)
        if customers_list:
            logger.info('Found customer %d account', len(customers_list))
            for c in customers_list:
                c.update_from_user_acct(user_acct)
        
    
    def update_from_user_acct(self, user_acct):
        
        self.name                   = user_acct.name
        self.email                  = user_acct.email
        self.mobile_phone           = user_acct.mobile_phone
        self.birth_date             = user_acct.birth_date
        self.birth_date_date_str    = user_acct.birth_date_date_str
        self.birth_day_in_year      = user_acct.birth_day_in_year
        self.gender                 = user_acct.gender
        self.put()
    
    @staticmethod
    def count_by_last_transact_date(merchant_acct, last_transact_in_day=7):
        checking_date = datetime.now().date() - timedelta(days=last_transact_in_day)
        
        logger.debug('count_by_last_transact_date: checking_date=%s', checking_date)
        
        query = Customer.query(ndb.AND(
                                                    Customer.merchant_acct==merchant_acct.create_ndb_key(),
                                                    Customer.last_transact_date >= checking_date   
                                        ))
        
        return Customer.count_with_condition_query(query)
    
    
                
    
    @staticmethod
    def check_birthday_reward_have_entitled_before(customer_acct, year, program_key):
        entitled_birthday_reward_summary = customer_acct.entitled_birthday_reward_summary
        year_str = str(year)
        logger.info('entitled_birthday_reward_summary=%s', entitled_birthday_reward_summary)
        
        if is_not_empty(entitled_birthday_reward_summary):
            if is_not_empty(entitled_birthday_reward_summary.get(year_str)):
                this_year_entitled_birthday_programs_list = entitled_birthday_reward_summary.get(year_str).get('programs')
                
                logger.debug('this_year_entitled_birthday_programs_list=%s', this_year_entitled_birthday_programs_list)
                is_entitled_before = False
                if is_not_empty(this_year_entitled_birthday_programs_list):
                    for k in this_year_entitled_birthday_programs_list:
                        if k == program_key:
                            is_entitled_before =  True
                            break
                    
                    logger.debug('is_entitled_before=%s', is_entitled_before)
                    return is_entitled_before
                else:
                    logger.debug('Program list is empty')
            else:
                logger.debug('Not found for year (%s)', year)
        else:
            logger.debug('entitled_birthday_reward_summary is empty')            
        
        return False
    
    @staticmethod
    def update_customer_entitled_birthday_reward_summary(customer_acct, merchant_program_key, transact_datetime=None):
        
        logger.debug('---update_customer_entitled_birthday_reward_summary---')
        
        if transact_datetime is None:
            today       = datetime.today().date()
            this_year   = today.year
        else:
            today       = transact_datetime.date()
            this_year   = transact_datetime.year
        
        year_str = str(this_year)
        entitled_birthday_reward_summary            = customer_acct.entitled_birthday_reward_summary
        this_year_entitled_birthday_reward_summary  = None    
        
        if entitled_birthday_reward_summary:
            this_year_entitled_birthday_reward_summary  = entitled_birthday_reward_summary.get(year_str)
        else:
            entitled_birthday_reward_summary = {}
        
        if this_year_entitled_birthday_reward_summary is None:
            this_year_entitled_birthday_reward_summary = {}
            
        
        is_birthday_reward_has_been_given = False
        if this_year_entitled_birthday_reward_summary.get('programs'):
            if merchant_program_key in this_year_entitled_birthday_reward_summary.get('programs'):
                is_birthday_reward_has_been_given = True
                logger.debug('Found %s in programs list', merchant_program_key)
            else:
                logger.debug('going to add entitled program(%s)', merchant_program_key)
                this_year_entitled_birthday_reward_summary['programs'].append(merchant_program_key)
                is_birthday_reward_has_been_given = False
                
        else:
            this_year_entitled_birthday_reward_summary = {'programs': [merchant_program_key]}
            is_birthday_reward_has_been_given = False
            
        if is_birthday_reward_has_been_given==False:
            entitled_birthday_reward_summary[year_str]     = this_year_entitled_birthday_reward_summary
            customer_acct.entitled_birthday_reward_summary  = entitled_birthday_reward_summary
            customer_acct.put()
    
    @staticmethod
    def check_membership_year_reward_have_entitled_before(customer_acct, year, program_key):
        entitled_membership_reward_summary = customer_acct.entitled_membership_reward_summary
        year_str = str(year)
        logger.info('entitled_membership_reward_summary=%s', entitled_membership_reward_summary)
        
        if is_not_empty(entitled_membership_reward_summary):
            entitled_membership_yearly_reward_summary = entitled_membership_reward_summary.get('yearly')
            if is_not_empty(entitled_membership_yearly_reward_summary):
                if is_not_empty(entitled_membership_yearly_reward_summary.get(year_str)):
                    this_year_entitled_membership_programs_list = entitled_membership_yearly_reward_summary.get(year_str).get('programs')
                    
                    logger.debug('this_year_entitled_membership_programs_list=%s', this_year_entitled_membership_programs_list)
                    is_entitled_before = False
                    if is_not_empty(this_year_entitled_membership_programs_list):
                        for k in this_year_entitled_membership_programs_list:
                            if k == program_key:
                                is_entitled_before =  True
                                break
                        
                        logger.debug('is_entitled_before=%s', is_entitled_before)
                        return is_entitled_before
                    else:
                        logger.debug('Program list is empty')
                else:
                    logger.debug('Not found for year (%s)', year)
            else:
                logger.debug('Not found for yearly reward suammry')        
        else:
            logger.debug('entitled_membership_reward_summary is empty')            
        
        return False
    
    @staticmethod
    def revert_customer_entitled_membership_reward_summary(customer_acct, program_key, transact_year=None):
        
        if program_key in customer_acct.entitled_membership_reward_summary['yearly'][transact_year]['programs']:
            customer_acct.entitled_membership_reward_summary['yearly'][transact_year]['programs'].remove(program_key)
            customer_acct.put()
    
    @staticmethod
    def update_customer_entitled_membership_reward_summary(customer_acct, merchant_program_key, transact_datetime=None):
        
        logger.debug('---update_customer_entitled_membership_reward_summary---')
        
        if transact_datetime is None:
            today       = datetime.today().date()
            this_year   = today.year
        else:
            today       = transact_datetime.date()
            this_year   = transact_datetime.year
        
        year_str = str(this_year)
        entitled_membership_reward_summary              = customer_acct.entitled_membership_reward_summary
        is_membership_reward_has_been_given             = False
        
        if is_empty(entitled_membership_reward_summary):
            entitled_membership_reward_summary = {
                                                'yearly': {
                                                        year_str: {
                                                                'programs':[
                                                                            merchant_program_key,
                                                                            ]
                                                            }
                                                    }
                                                }
                                                    
                
        else:
            entitled_membership_yearly_reward_summary       = entitled_membership_reward_summary.get('yearly')
            
            
            if is_empty(entitled_membership_yearly_reward_summary):
                entitled_membership_yearly_reward_summary = {
                                                                    year_str: {
                                                                            'programs':[
                                                                                        merchant_program_key,
                                                                                        ]
                                                                        }
                                                                }
                entitled_membership_reward_summary['yearly']        = entitled_membership_yearly_reward_summary
                
            else:
                
                this_year_entitled_membership_reward_summary    = entitled_membership_yearly_reward_summary.get(year_str)
                 
                if is_empty(this_year_entitled_membership_reward_summary):
                    this_year_entitled_membership_reward_summary = {
                                                                year_str: {
                                                                            'programs':[
                                                                                        merchant_program_key,
                                                                                        ]
                                                                        }
                                                                }
                    entitled_membership_yearly_reward_summary[year_str] = this_year_entitled_membership_reward_summary
                    entitled_membership_reward_summary['yearly']        = entitled_membership_yearly_reward_summary
                    
                else:
                    
                    if this_year_entitled_membership_reward_summary.get('programs'):
                        if merchant_program_key in this_year_entitled_membership_reward_summary.get('programs'):
                            is_membership_reward_has_been_given = True
                            logger.debug('Found %s in programs list', merchant_program_key)
                        else:
                            logger.debug('going to add entitled program(%s)', merchant_program_key)
                            this_year_entitled_membership_reward_summary['programs'].append(merchant_program_key)
                            
                            entitled_membership_yearly_reward_summary[year_str] = this_year_entitled_membership_reward_summary
                            entitled_membership_reward_summary['yearly']        = entitled_membership_yearly_reward_summary   
                            
                    else:
                        this_year_entitled_membership_reward_summary = {'programs': [merchant_program_key]}
                    
                        entitled_membership_yearly_reward_summary[year_str] = this_year_entitled_membership_reward_summary
                        entitled_membership_reward_summary['yearly']        = entitled_membership_yearly_reward_summary    
                    
        if is_membership_reward_has_been_given==False:
            customer_acct.entitled_membership_reward_summary  = entitled_membership_reward_summary
            customer_acct.put()
    
    def update_after_removed_voucher(self, removed_voucher):
        entitled_voucher_summary = self.entitled_voucher_summary
        update_customer_entiteld_voucher_summary_after_removed_voucher(entitled_voucher_summary, removed_voucher)
        self.put()
        
    def update_after_removed_voucher_by_redeem_code(self, redeem_code):
        self.entitled_voucher_summary = update_customer_entiteld_voucher_summary_after_removed_voucher_by_redeem_code(self.entitled_voucher_summary, redeem_code)
        self.put()    
        
    def update_after_added_voucher(self, added_voucher):
        entitled_voucher_summary = self.entitled_voucher_summary
        update_customer_entiteld_voucher_summary_with_customer_new_voucher(entitled_voucher_summary, added_voucher)
        self.put()
    
class CustomerMembership(BaseNModel, DictModel):
    '''
    parent is Customer
    '''
    
    merchant_acct               = ndb.KeyProperty(name="merchant_acct", kind=MerchantAcct)
    merchant_membership         = ndb.KeyProperty(name="merchant_membership", kind=MerchantMembership)
    entitled_datetime           = ndb.DateTimeProperty(required=True, auto_now_add=True)
    entitled_date               = ndb.DateProperty(required=True, auto_now_add=True)
    expiry_date                 = ndb.DateProperty(required=True)
    previous_expiry_date        = ndb.DateProperty(required=False)
    renewed_datetime            = ndb.DateTimeProperty(required=False)
    renewed_date                = ndb.DateProperty(required=False)
    
    assigned_by                 = ndb.KeyProperty(name="assigned_by", kind=MerchantUser)
    assigned_by_username        = ndb.StringProperty(required=False)
    assigned_outlet             = ndb.KeyProperty(name="assigned_outlet", kind=Outlet)
    
    renewed_by                  = ndb.KeyProperty(name="renewed_by", kind=MerchantUser)
    renewed_by_username         = ndb.StringProperty(required=False)
    
    renewed_outlet              = ndb.KeyProperty(name="renewed_outlet", kind=Outlet)
    
    dict_properties     =[
                            'customer', 'merchant_membership_entity', 'entitled_date', 'expiry_date', 'merchant_membership_key'
                            ]
    
    @property
    def merchant_membership_key(self):
        return self.merchant_membership.urlsafe().decode('utf-8')
    
    @property
    def customer_key(self):
        return self.key.parent().urlsafe().decode('utf-8')
    
    @property
    def merchant_acct_entity(self):
        if self.merchant_acct:
            return MerchantAcct.fetch(self.merchant_acct.urlsafe())
    
    @property
    def merchant_membership_entity(self):
        return MerchantMembership.fetch(self.merchant_membership.urlsafe())
    
    @property
    def customer(self):
        return Customer.fetch(self.key.parent().urlsafe())
    
    def is_active(self, checking_date=None):
        if checking_date is None:
            checking_date = datetime.utcnow().date()
        return checking_date<= self.expiry_date
    
    def is_new_joined(self, purchased_datetime=None):
        if purchased_datetime is None:
            purchased_datetime = datetime.utcnow()
        
        time_difference = purchased_datetime -  self.entitled_datetime
        
        time_difference_in_second =  time_difference.total_seconds()
        
        logger.debug('time_difference_in_second=%s', time_difference_in_second)
        
        return time_difference_in_second<=3
    
    def is_valid(self, checking_date=None):
        if checking_date is None:
            checking_date = datetime.utcnow().date()
        
        return checking_date<=self.expiry_date
    
    @staticmethod
    def get_by_customer_and_merchant_membership(customer, merchant_membership):
        return CustomerMembership.query(
                                    ndb.AND(
                                        CustomerMembership.merchant_membership==merchant_membership.create_ndb_key()
                                        ), ancestor=customer.create_ndb_key()).get()
                                        
    
    @staticmethod
    def count_merchant_customer_membership(merchant_acct):
        if merchant_acct:
            query = CustomerMembership.query(ndb.AND(CustomerMembership.merchant_acct==merchant_acct.create_ndb_key()))
        else:
            query = CustomerMembership.query()
        
        return CustomerMembership.count_with_condition_query(query)
    
    @staticmethod
    def list_merchant_customer_membership(merchant_acct, limit=conf.MAX_FETCH_RECORD, start_cursor=None, return_with_cursor=False):
        if merchant_acct:
            query = CustomerMembership.query(ndb.AND(CustomerMembership.merchant_acct==merchant_acct.create_ndb_key()))
        else:
            query = CustomerMembership.query()
        
        return CustomerMembership.list_all_with_condition_query(query, limit=limit, start_cursor=start_cursor, return_with_cursor=return_with_cursor, keys_only=False)
    
    @staticmethod
    def list_all_by_customer(customer, limit = conf.MAX_FETCH_RECORD, offset=0, keys_only=False):
        return CustomerMembership.query(ancestor=customer.create_ndb_key()).fetch(offset=offset, limit=limit, keys_only=keys_only)
    
    @staticmethod
    def delete_all_by_customer(customer):
        query = CustomerMembership.query(ancestor=customer.create_ndb_key())
        CustomerMembership.delete_multiples(query)
    
    @staticmethod
    def list_active_by_customer(customer):
        memberships_list = CustomerMembership.list_all_by_customer(customer)
        today_date = datetime.today().date()
        valid_memberships_list = []
        for m in memberships_list:
            if m.is_valid(checking_date=today_date):
                valid_memberships_list.append(m)
                
        
        return valid_memberships_list
    
    @staticmethod
    def list_by_customer(customer):
        memberships_list = CustomerMembership.list_all_by_customer(customer)
        valid_memberships_list = []
        for m in memberships_list:
            valid_memberships_list.append(m)
                
        
        return valid_memberships_list        
                                    
    @staticmethod
    def list_merchant_membership_by_entitled_date(merchant_memberships_list, entitled_date, limit=conf.MAX_FETCH_RECORD, start_cursor=None, return_with_cursor=False):
        
        merchant_membership_key_list = []
        for m in merchant_memberships_list:
            merchant_membership_key_list.append(m.create_ndb_key())
        
        query = CustomerMembership.query(ndb.AND(
                                        CustomerMembership.merchant_membership.IN(merchant_membership_key_list),
                                        CustomerMembership.entitled_date==entitled_date,
                                        ),
                                    )
        return CustomerMembership.list_all_with_condition_query(query, limit=limit, start_cursor=start_cursor, return_with_cursor=return_with_cursor, keys_only=False)
    
    @staticmethod
    def list_active_merchant_membership_by_entitled_date(merchant_memberships_list, entitled_date, limit=conf.MAX_FETCH_RECORD, start_cursor=None, return_with_cursor=False):
        active_memberships_list     = []
        today_date                  = datetime.utcnow().date()
        next_cursor                 = None
        search_results              = []
        
        if return_with_cursor:
            (search_results, next_cursor) = CustomerMembership.list_merchant_membership_by_entitled_date(merchant_memberships_list, entitled_date, limit=limit, start_cursor=start_cursor, return_with_cursor=return_with_cursor)
            
        else:
            search_results = CustomerMembership.list_merchant_membership_by_entitled_date(merchant_memberships_list, entitled_date, limit=limit, start_cursor=start_cursor);
            
        for r in search_results:
            if r.is_active(checking_date=today_date):
                active_memberships_list.append(r)
                
        if return_with_cursor:
            return (active_memberships_list, next_cursor)
        else:
            return active_memberships_list
                    
            
    @staticmethod
    def create(customer, merchant_membership, entitled_datetime=None, assigned_outlet=None, assigned_by=None, number_of_year=None):
        if entitled_datetime is None:
            entitled_datetime = datetime.utcnow()
            
        expiry_date = merchant_membership.calc_expiry_date(start_date=entitled_datetime, number_of_year=number_of_year)
        logger.debug('expiry_date=%s', expiry_date)
        merchant_acct = merchant_membership.merchant_acct
        customer_membership = CustomerMembership(
                                parent                  = customer.create_ndb_key(),
                                merchant_membership     = merchant_membership.create_ndb_key(),
                                merchant_acct           = merchant_acct.create_ndb_key(),
                                entitled_datetime       = entitled_datetime,
                                entitled_date           = entitled_datetime.date(),
                                expiry_date             = expiry_date,    
                                assigned_outlet         = assigned_outlet.create_ndb_key(), 
                                assigned_by             = assigned_by.create_ndb_key(),
                                assigned_by_username    = assigned_by.username,
                                 
                                )
        customer_membership.put()
                            
        Customer.update_membership(customer, merchant_membership.key_in_str)
        
        return customer_membership
        
        
    @staticmethod
    def renew(customer, merchant_membership, renewed_datetime=None, renewed_outlet=None, renewed_by=None):
        
        customer_membership = CustomerMembership.get_by_customer_and_merchant_membership(customer, merchant_membership)
        if customer_membership is not None:
            if renewed_datetime is None:
                renewed_datetime = datetime.utcnow()
            
            merchant_acct   = merchant_membership.merchant_acct
            expiry_date     = customer_membership.expiry_date 
            renewed_date    = renewed_datetime.date()
            valid_to_renew  = False
            
            day_difference  = (expiry_date - renewed_date).days
            logger.debug('day_difference=%s', day_difference)
            if day_difference>=0:
                logger.debug('advance renew')
                if day_difference<merchant_acct.membership_renew_advance_day:
                    logger.debug('within configured advance renew')
                    valid_to_renew = True
                else: 
                    logger.debug('not within configured advance renew')
            else:
                logger.debug('late renew') 
                if abs(day_difference)<merchant_acct.membership_renew_late_day:
                    logger.debug('within configured late renew')
                    valid_to_renew = True
                else: 
                    logger.debug('not within configured late renew')
            
            if valid_to_renew:    
                customer_membership.renewed_datetime        = renewed_datetime
                customer_membership.renewed_date            = renewed_datetime.date()
                customer_membership.previous_expiry_date    = customer_membership.expiry_date
                customer_membership.expiry_date             = merchant_membership.calc_expiry_date(start_date=renewed_datetime)
                customer_membership.renewed_outlet          = renewed_outlet.create_ndb_key()
                customer_membership.renewed_by              = renewed_by.create_ndb_key()
                customer_membership.renewed_by_username     = renewed_by.username
                customer_membership.put()
                
                return customer_membership
            else:
                raise Exception('Renewal not within configured advance date or late date')
        else:
            raise Exception('Membership is not found')
        
    def revert_renewal(self):
        
        self.renewed_datetime        = None
        self.expiry_date             = self.previous_expiry_date
        self.put()   
        
class CustomerTierMembership(BaseNModel, DictModel):
    '''
    parent is Customer
    '''
    
    merchant_acct               = ndb.KeyProperty(name="merchant_acct", kind=MerchantAcct)
    merchant_tier_membership    = ndb.KeyProperty(name="merchant_tier_membership", kind=MerchantTierMembership)
    entitled_datetime           = ndb.DateTimeProperty(required=True, auto_now_add=True)
    entitled_date               = ndb.DateProperty(required=True, auto_now_add=True)
    expiry_date                 = ndb.DateProperty(required=True)
    valid                       = ndb.BooleanProperty(required=True, default=True)
    
    dict_properties     =[
                            'customer', 'merchant_tier_membership_entity', 'entitled_date', 'expiry_date', 'valid', 'merchant_tier_membership_key',
                            ] 
    
    
    @property
    def merchant_tier_membership_key(self):
        return self.merchant_tier_membership.urlsafe().decode('utf-8')
    
    @property
    def merchant_tier_membership_entity(self):
        return MerchantTierMembership.fetch(self.merchant_tier_membership.urlsafe())
    
    @property
    def customer(self):
        return Customer.fetch(self.key.parent().urlsafe())
    
    def is_active(self, checking_date=None):
        if checking_date is None:
            checking_date = datetime.utcnow().date()
        return checking_date<= self.expiry_date
    
    def is_new_entitled(self, entitled_datetime=None):
        if entitled_datetime is None:
            entitled_datetime = datetime.utcnow()
        
        time_difference = entitled_datetime -  self.entitled_datetime
        
        time_difference_in_second =  time_difference.total_seconds()
        
        logger.debug('time_difference_in_second=%s', time_difference_in_second)
        
        return time_difference_in_second<=3
    
    def is_valid(self, checking_date=None):
        if checking_date is None:
            checking_date = datetime.utcnow().date()
        
        return checking_date<=self.expiry_date
    
    @staticmethod
    def list_all_by_customer(customer, limit = conf.MAX_FETCH_RECORD, offset=0, keys_only=False):
        return CustomerTierMembership.query(ancestor=customer.create_ndb_key()).fetch(offset=offset, limit=limit, keys_only=keys_only)
    
    @staticmethod
    def delete_all_by_customer(customer):
        query = CustomerTierMembership.query(ancestor=customer.create_ndb_key())
        CustomerTierMembership.delete_multiples(query)
    
    @staticmethod
    def get_by_customer_and_merchant_tier_membership(customer, merchant_tier_membership):
        return CustomerTierMembership.query(
                                    ndb.AND(
                                        CustomerTierMembership.merchant_tier_membership==merchant_tier_membership.create_ndb_key()
                                        ), ancestor=customer.create_ndb_key()).get()
                                        
                                        
                                        
    @staticmethod
    def list_by_customer(customer):
        return CustomerTierMembership.query(
                                    ancestor=customer.create_ndb_key()).fetch(limit=conf.MAX_FETCH_RECORD)
    
    @staticmethod
    def list_active_by_customer(customer):
        memberships_list = CustomerTierMembership.list_by_customer(customer)
        today_date = datetime.today().date()
        valid_memberships_list = []
        for m in memberships_list:
            if m.is_valid(checking_date=today_date):
                valid_memberships_list.append(m)
                
        
        return valid_memberships_list        
                                    
    @staticmethod
    def list_merchant_tier_membership_by_entitled_date(merchant_tier_memberships_list, entitled_date, limit=conf.MAX_FETCH_RECORD, start_cursor=None, return_with_cursor=False):
        
        merchant_tier_membership_key_list = []
        for m in merchant_tier_memberships_list:
            merchant_tier_membership_key_list.append(m.create_ndb_key())
        
        query = CustomerTierMembership.query(ndb.AND(
                                        CustomerTierMembership.merchant_tier_membership.IN(merchant_tier_membership_key_list),
                                        CustomerTierMembership.entitled_date==entitled_date,
                                        ),
                                    )
        return CustomerTierMembership.list_all_with_condition_query(query, limit=limit, start_cursor=start_cursor, return_with_cursor=return_with_cursor, keys_only=False)
    
    @staticmethod
    def list_active_merchant_tier_membership_by_entitled_date(merchant_memberships_list, entitled_date, limit=conf.MAX_FETCH_RECORD, start_cursor=None, return_with_cursor=False):
        active_memberships_list     = []
        today_date                  = datetime.utcnow().date()
        next_cursor                 = None
        search_results              = []
        
        if return_with_cursor:
            (search_results, next_cursor) = CustomerTierMembership.list_merchant_tier_membership_by_entitled_date(merchant_memberships_list, entitled_date, limit=limit, start_cursor=start_cursor, return_with_cursor=return_with_cursor)
            
        else:
            search_results = CustomerTierMembership.list_merchant_tier_membership_by_entitled_date(merchant_memberships_list, entitled_date, limit=limit, start_cursor=start_cursor);
            
        for r in search_results:
            if r.is_active(checking_date=today_date):
                active_memberships_list.append(r)
                
        if return_with_cursor:
            return (active_memberships_list, next_cursor)
        else:
            return active_memberships_list  
        
    @staticmethod
    def create(customer, merchant_tier_membership, transaction_details, entitled_datetime=None, ):
        if entitled_datetime is None:
            entitled_datetime = datetime.utcnow()
            
        expiry_date = merchant_tier_membership.calc_expiry_date(start_date=entitled_datetime)
        logger.debug('expiry_date=%s', expiry_date)
        
        customer_tier_membership = CustomerTierMembership(
                                parent                      = customer.create_ndb_key(),
                                merchant_tier_membership    = merchant_tier_membership.create_ndb_key(),
                                entitled_datetime           = entitled_datetime,
                                entitled_date               = entitled_datetime.date(),
                                expiry_date                 = expiry_date,    
                                 
                                )
        customer_tier_membership.put()
                            
        Customer.update_tier_membership(customer, merchant_tier_membership)
        
        transaction_details.is_tier_membership_upgraded = True
        transaction_details.upgraded_merchant_tier_membership = merchant_tier_membership.create_ndb_key()
        transaction_details.put()
        
        return customer_tier_membership 
    
    @staticmethod
    def change(customer, new_merchant_tier_membership, transaction_details, entitled_datetime=None, ):
        logger.debug('Customer tier membership changed in transaction_id=%s', transaction_details.transaction_id)
        existing_tier_membership            = customer.tier_membership_entity
        existing_customer_tier_membership   = CustomerTierMembership.get_by_customer_and_merchant_tier_membership(customer, existing_tier_membership)
        
        upgrade_expiry_type = new_merchant_tier_membership.upgrade_expiry_type
        new_expiry_date = None
        
        if upgrade_expiry_type == program_conf.MEMBERSHIP_UPGRADE_EXPIRY_TYPE_CONTINUE_EXPIRY:
            new_expiry_date = existing_customer_tier_membership.expiry_date
        elif upgrade_expiry_type == program_conf.MEMBERSHIP_UPGRADE_EXPIRY_TYPE_NEW_EXPIRY:
            new_expiry_date = new_merchant_tier_membership.calc_expiry_date()
        
        if entitled_datetime is None:
            entitled_datetime = datetime.utcnow()
            
        expiry_date = new_merchant_tier_membership.calc_expiry_date(start_date=entitled_datetime)
        logger.debug('expiry_date=%s', expiry_date)
        
        existing_customer_tier_membership.valid = False
        existing_customer_tier_membership.put()
        
        customer_tier_membership = CustomerTierMembership.get_by_customer_and_merchant_tier_membership(customer, new_merchant_tier_membership)
        if customer_tier_membership:
            customer_tier_membership.entitled_datetime  = entitled_datetime
            customer_tier_membership.entitled_date      = entitled_datetime.date()
            customer_tier_membership.expiry_date        = new_expiry_date
            customer_tier_membership.valid              = True
        else:
            customer_tier_membership = CustomerTierMembership(
                                parent                      = customer.create_ndb_key(),
                                merchant_tier_membership    = new_merchant_tier_membership.create_ndb_key(),
                                entitled_datetime           = entitled_datetime,
                                entitled_date               = entitled_datetime.date(),
                                expiry_date                 = new_expiry_date,    
                                 
                                )
        customer_tier_membership.put()
                            
        Customer.update_tier_membership(customer, new_merchant_tier_membership)
        logger.debug('Going to update there is merchant tier membership upgraded in the transaction where transaction_id=%s', transaction_details.transaction_id)
        transaction_details.is_tier_membership_upgraded = True
        transaction_details.upgraded_merchant_tier_membership = new_merchant_tier_membership.create_ndb_key()
        transaction_details.put()
        
        return customer_tier_membership         