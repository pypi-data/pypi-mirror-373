'''
Created on 12 May 2023

@author: jacklok
'''
import logging
from trexconf import program_conf
import trexmodel.conf as model_conf
from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel
from google.cloud import ndb
from trexmodel.models.datastore.merchant_models import MerchantUser,\
    MerchantAcct, Outlet
from trexlib.utils.string_util import is_not_empty, random_string, is_empty
from datetime import datetime, timedelta
import random
from trexlib.utils.common.common_util import sort_dict_list
from trexmodel.models.datastore.customer_models import Customer
from collections import Counter
from trexmodel.models.datastore.voucher_models import MerchantVoucher

logger = logging.getLogger('model')
#logger = logging.getLogger('debug')

class LuckyDrawBase(BaseNModel, DictModel):
    '''
    Merchant Acct as ancestor
    
    '''
    
    label                   = ndb.StringProperty(required=True)
    desc                    = ndb.StringProperty(required=False)
    start_date              = ndb.DateProperty(required=True)
    end_date                = ndb.DateProperty(required=True)
    
    completed_status        = ndb.StringProperty(required=True, default=program_conf.PROGRAM_STATUS_PROGRAM_BASE, choices=set(program_conf.LUCKY_DRAW_PROGRAM_STATUS))
    
    archived                = ndb.BooleanProperty(default=False)
    enabled                 = ndb.BooleanProperty(default=True)
    
    created_datetime        = ndb.DateTimeProperty(required=True, auto_now_add=True)
    modified_datetime       = ndb.DateTimeProperty(required=True, auto_now=True)
    archived_datetime       = ndb.DateTimeProperty(required=False)
    
    created_by              = ndb.KeyProperty(name="created_by", kind=MerchantUser)
    created_by_username     = ndb.StringProperty(required=False)
    
    modified_by             = ndb.KeyProperty(name="modified_by", kind=MerchantUser)
    modified_by_username    = ndb.StringProperty(required=False)
    
class LuckyDrawProgram(LuckyDrawBase):
    condition_settings      = ndb.JsonProperty(required=False)
    exclusivity_settings    = ndb.JsonProperty(required=False)
    prize_settings          = ndb.JsonProperty(required=False)
    test_result             = ndb.JsonProperty(required=False)
    image_storage_filename  = ndb.StringProperty(required=False)
    image_public_url        = ndb.StringProperty(required=False)
    
    dict_properties                     = ['label', 'desc', 'start_date', 'end_date', 'archived', 'is_recurring_scheme',
                                           'created_datetime', 'modified_datetime','archived_datetime', 'completed_status',
                                           'condition_settings', 'exclusivity_settings', 'prize_settings',
                                           'exclusive_tags_list', 'exclusive_memberships_list', 'exclusive_tier_memberships_list',  
                                           'created_by_username', 'modified_by_username', 'completed_progress_in_percentage',
                                           'is_published', 'is_enabled','is_disabled', 'totalPrizePossibility',
                                           'image_storage_filename', 'image_public_url', 'test_result', 'is_expired',
                                           ]
    
    
    def to_configuration(self):
        program_configuration = {
                                'merchant_acct_key'                 : self.parent_key,
                                'program_key'                       : self.key_in_str,
                                'label'                             : self.label,
                                'desc'                              : self.desc,
                                'start_date'                        : self.start_date.strftime('%d-%m-%Y'),
                                'end_date'                          : self.end_date.strftime('%d-%m-%Y'),    
                                'program_settings'                  : {
                                                                        'condition_settings'    : self.condition_settings,
                                                                        'exclusivity_settings'  : self.exclusivity_settings,
                                                                        'prize_settings'        : self.prize_settings,
                                                                        'ticket_image_url'      : self.image_public_url,
                                                                        },
                                'is_published'                      : self.is_published,  
                                }
        
        return program_configuration
    
    @property
    def merchant_acct_entity(self):
        return MerchantAcct.fetch(self.key.parent().urlsafe())
    
    @property
    def is_enabled(self):
        return self.enabled
    
    @property
    def is_disabled(self):
        return self.enabled==False
    
    @property
    def is_expired(self):
        return self.end_date<datetime.now().date()
    
    @property
    def is_archived(self):
        return self.archived
    
    @property
    def is_published(self):
        return self.completed_status == program_conf.PROGRAM_STATUS_PUBLISH
    
    @property
    def exclusive_tags_list(self):
        if self.exclusivity_settings and self.exclusivity_settings.get('tags'):
            return ','.join(self.exclusivity_settings.get('tags')) or ''
        
    @property
    def exclusive_memberships_list(self):
        if self.exclusivity_settings and self.exclusivity_settings.get('memberships'):
            return ','.join(self.exclusivity_settings.get('memberships')) or ''
        
    @property
    def exclusive_tier_memberships_list(self):
        if self.exclusivity_settings and self.exclusivity_settings.get('tier_memberships'):
            return ','.join(self.exclusivity_settings.get('tier_memberships')) or ''
    
    @property
    def completed_progress_in_percentage(self):
        return program_conf.lucky_draw_program_completed_progress_percentage(self.completed_status)
    
    @property
    def is_recurring_scheme(self):
        if self.condition_settings:
            return self.condition_settings.get('is_recurring_scheme') or False
        return False
    
    @property
    def totalPrizePossibility(self):
        total = 0
        if self.prize_settings.get('prizes'):
            for prize_details in self.prize_settings.get('prizes'):
                if prize_details.get('possibility'):
                    total +=prize_details.get('possibility')
        
        return total
    
    @staticmethod
    def create(merchant_acct, label=None, desc=None, start_date=None, end_date=None, exclusivity_settings={}, prize_settings={}, 
               created_by=None):
        
        created_by_username = None
        if is_not_empty(created_by):
            if isinstance(created_by, MerchantUser):
                created_by_username = created_by.username
                
        lucky_draw_program = LuckyDrawProgram(
                                parent                  = merchant_acct.create_ndb_key(),
                                label                   = label,
                                desc                    = desc,
                                start_date              = start_date,
                                end_date                = end_date,
                                exclusivity_settings    = exclusivity_settings,
                                prize_settings          = prize_settings,
                                created_by              = created_by.create_ndb_key(),
                                created_by_username     = created_by_username,
                                )
        lucky_draw_program.put()
        
        return lucky_draw_program
        
    @staticmethod
    def update(lucky_draw_program, label=None, desc=None, start_date=None, end_date=None, 
               modified_by=None):
        
        modified_by_username = None
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        lucky_draw_program.label                = label
        lucky_draw_program.desc                 = desc
        lucky_draw_program.start_date           = start_date
        lucky_draw_program.end_date             = end_date
        
        lucky_draw_program.modified_by = modified_by.create_ndb_key()
        lucky_draw_program.modified_by_username = modified_by_username
                
        
        lucky_draw_program.put()   
        
    @staticmethod
    def list_by_merchant_acct(merchant_acct):
        return LuckyDrawProgram.query(ndb.AND(LuckyDrawProgram.archived!=True), ancestor=merchant_acct.create_ndb_key()).fetch(limit=model_conf.MAX_FETCH_RECORD)
    
    @staticmethod
    def list_archived_by_merchant_acct(merchant_acct):
        return LuckyDrawProgram.query(ndb.AND(LuckyDrawProgram.archived==True), ancestor=merchant_acct.create_ndb_key()).fetch(limit=model_conf.MAX_FETCH_RECORD)
    
    def add_program_prize(self, prize_configuration, modified_by=None):
        
        modified_by_username        = None
        
        prize_configurations_list   = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        if self.prize_settings is None:
            prize_configurations_list   = []
            prize_settings              = {}
            
        else:
            prize_settings              = self.prize_settings
            prize_configurations_list   = prize_settings.get('prizes') or []
        
        if self.exclusivity_settings is None:
            self.exclusivity_settings = {}   
        
        prize_configurations_list.append(prize_configuration)
        prize_settings['prizes']    = prize_configurations_list
        
        self.modified_by            = modified_by.create_ndb_key()
        self.modified_by_username   = modified_by_username
        self.prize_settings         = prize_settings
        
        self.put()
        
    def remove_program_prize(self, prize_index, modified_by=None):    
        
        modified_by_username        = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        prizes_listing              = self.prize_settings.get('prizes')
        latest_prizes_listing = []
        
        for p in prizes_listing:
            if p.get('prize_index') != prize_index:
                latest_prizes_listing.append(p)
    
        self.prize_settings['prizes'] = latest_prizes_listing        
        
        self.modified_by            = modified_by.create_ndb_key()
        self.modified_by_username   = modified_by_username
        
        
        self.put()    
    
    def completed_program_prize_status(self, modified_by=None):
        modified_by_username    = None              
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username

          
        self.modified_by            = modified_by.create_ndb_key()
        self.modified_by_username   = modified_by_username
        self.completed_status       = program_conf.PROGRAM_STATUS_DEFINE_PRIZE
        self.put()
        
    def archive(self, modified_by=None):
        modified_by_username    = None              
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username

          
        self.modified_by            = modified_by.create_ndb_key()
        self.modified_by_username   = modified_by_username
        self.archived               = True
        self.archived_datetime      = datetime.utcnow()
        self.put() 
        
        merchant_acct = self.merchant_acct_entity
        merchant_acct.remove_lucky_draw_program_configuration(self.to_configuration())
        
        
    def enable(self, modified_by=None):
        modified_by_username    = None              
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username

          
        self.modified_by            = modified_by.create_ndb_key()
        self.modified_by_username   = modified_by_username
        self.enabled               = True
        self.put()
        
        logger.debug('enable debug: is published : %s', self.is_published)
        
        if self.is_published:
            logger.debug('enable debug: going to update merchant account ')
            merchant_acct = self.merchant_acct_entity
            merchant_acct.update_lucky_draw_program(self.to_configuration())
        
    def disable(self, modified_by=None):
        modified_by_username    = None              
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username

          
        self.modified_by            = modified_by.create_ndb_key()
        self.modified_by_username   = modified_by_username
        self.enabled               = False
        self.put()
        
        logger.debug('disable debug: is published : %s', self.is_published)
        
        if self.is_published:
            logger.debug('disable debug: going to update merchant account ')
            merchant_acct = self.merchant_acct_entity
            merchant_acct.remove_lucky_draw_program_configuration(self.to_configuration())            
        
    def update_program_condition(self, program_condition_data, modified_by=None):
        modified_by_username    = None              
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username

          
        logger.debug('program_condition_data=%s', program_condition_data)
        
        self.condition_settings     = program_condition_data
        self.modified_by            = modified_by.create_ndb_key()
        self.modified_by_username   = modified_by_username
        self.completed_status       = program_conf.PROGRAM_STATUS_DEFINE_CONDITION
        self.put()
        
    def update_program_prize_possibility(self, program_prize_possibility_data, modified_by=None):
        prize_settings          = self.prize_settings
        modified_by_username    = None              
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username

          
        logger.debug('prize_settings=%s', prize_settings)
        
        total_possibility = .0
        
        for ps in prize_settings.get('prizes'):
            prize_index = ps.get('prize_index')
            possibility = float(program_prize_possibility_data.get(prize_index))
            ps['possibility'] = possibility
            logger.debug('prize_index=%s, possibility=%s', prize_index, possibility)
            total_possibility+= possibility
        
        total_possibility = int(round(total_possibility))
        
        if total_possibility>100 or total_possibility<100:
            raise Exception('Total possibility must be 100')
        
        
        if self.exclusivity_settings is None:
            self.exclusivity_settings = {}
        
        self.modified_by            = modified_by.create_ndb_key()
        self.modified_by_username   = modified_by_username
        self.completed_status       = program_conf.PROGRAM_STATUS_DEFINE_PRIZE_POSSIBILITY
        self.put()  
        
    def test_program_prize_possibility(self, program_prize_possibility_data, test_count=100):
        prize_settings          = self.prize_settings

        total_possibility = .0
        
        for ps in prize_settings.get('prizes'):
            prize_index = ps.get('prize_index')
            possibility = float(program_prize_possibility_data.get(prize_index))
            ps['possibility'] = possibility
            logger.debug('prize_index=%s, possibility=%s', prize_index, possibility)
            total_possibility+= possibility
        
        total_possibility = int(round(total_possibility))
        
        if total_possibility>100 or total_possibility<100:
            raise Exception('Total possibility must be 100')
        
        prize_details_list = prize_settings.get('prizes')
        prizes_to_draw  = {}
        prizes          = []
        weights         = []
        accum_weights   = []
        accum_weight    = 0
        for p in prize_details_list:
            prizes_to_draw[p.get('prize_index')] = p.get('possibility')
            prizes.append(p.get('prize_index'))
            weights.append(p.get('possibility'))
            accum_weight+=p.get('possibility')
            accum_weights.append(accum_weight)
            
        logger.debug('prizes=%s', prizes)
        logger.debug('weights=%s', weights)
        
        logger.debug('accum_weights=%s', accum_weights)
        
        
        win_prize_index_list        = random.choices(prizes, cum_weights=accum_weights, k=test_count)    
        win_prize_details_counter   = Counter(win_prize_index_list)
        win_prize_details_dict      = {}
        logger.debug('win_prize_details_counter=%s', win_prize_details_counter)
            
        for win_prize_index, count in win_prize_details_counter.items():    
            win_prize_details = None
            if win_prize_index:
                for p in prize_details_list:
                    if p.get('prize_index') == win_prize_index:
                        win_prize_details = p
                        break
            if win_prize_details is not None:
                win_prize_details_dict[win_prize_index] = {
                                                            'count'         : count,
                                                            'prize_details' : win_prize_details,
                                                            }
        
        self.test_result = win_prize_details_dict
        self.put()
                
        
    def update_program_exclusivity(self, exclusivity_settings, modified_by=None):    
        modified_by_username    = None              
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        self.exclusivity_settings   = exclusivity_settings
        self.modified_by            = modified_by.create_ndb_key()
        self.modified_by_username   = modified_by_username
        self.completed_status       = program_conf.PROGRAM_STATUS_EXCLUSIVITY
        self.put()
    
    def update_ticket_image(self, image_public_url=None, image_storage_filename=None, modified_by=None):
        
        modified_by_username = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        self.image_public_url       = image_public_url
        self.image_storage_filename = image_storage_filename
        
        self.modified_by            = modified_by.create_ndb_key()
        self.modified_by_username   = modified_by_username
        
        self.completed_status       = program_conf.PROGRAM_STATUS_UPLOAD_TICKET_IMAGE
        self.put()
        
    def completed_program_ticket_image_status(self, modified_by=None, default_ticket_image=None):
        modified_by_username    = None              
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username

        
        if is_empty(self.image_public_url):
            self.image_public_url = default_ticket_image
          
        self.modified_by            = modified_by.create_ndb_key()
        self.modified_by_username   = modified_by_username
        self.completed_status       = program_conf.PROGRAM_STATUS_UPLOAD_TICKET_IMAGE
        self.put()    
        
    def publish_program(self, modified_by=None):
        modified_by_username    = None              
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username

          
        self.modified_by            = modified_by.create_ndb_key()
        self.modified_by_username   = modified_by_username
        self.completed_status       = program_conf.PROGRAM_STATUS_PUBLISH
        self.put()  
        
        merchant_acct = self.merchant_acct_entity
        merchant_acct.update_lucky_draw_program(self.to_configuration())
          
class LuckyDrawTicket(BaseNModel, DictModel):
    '''
    Customer acct as acentos
    '''
    
    merchant_acct           = ndb.KeyProperty(name="merchant_acct", kind=MerchantAcct)
    transact_outlet         = ndb.KeyProperty(name="transact_outlet", kind=Outlet)
    ticket_key              = ndb.StringProperty(required=True)
    program_key             = ndb.StringProperty(required=False)
    created_datetime        = ndb.DateTimeProperty(required=True, auto_now_add=True)
    used_datetime           = ndb.DateTimeProperty(required=False)
    expiry_date             = ndb.DateProperty(required=True)
    used                    = ndb.BooleanProperty(default=False)
    drawed_details          = ndb.JsonProperty(required=False)
    removed                 = ndb.BooleanProperty(default=False)
    removed_datetime        = ndb.DateProperty(required=False)
    grabbed                 = ndb.BooleanProperty(default=False)
    grabbed_datetime        = ndb.DateProperty(required=False)
    #created_by              = ndb.KeyProperty(name="created_by", kind=MerchantUser)
    #created_by_username     = ndb.StringProperty(required=False)
    dict_properties                     = [
                                            'ticket_key', 'expiry_date', 'merchant_acct_key','used', 
                                            'drawed_details', 'used_datetime', 'grabbed', 'grabbed_datetime',
                                           ]
    
    @property
    def customer_acct_key(self):
        return self.key.parent().urlsafe().decode('utf-8')
    
    @property
    def customer_acct_entity(self):
        return Customer.fetch(self.key.parent().urlsafe())
    
    @property
    def merchant_acct_key(self):
        return self.merchant_acct.urlsafe().decode('utf-8')
    
    @property
    def merchant_acct_entity(self):
        return MerchantAcct.fetch(self.merchant_acct.urlsafe())
    
    @property
    def transact_outlet_entity(self):
        return Outlet.fetch(self.transact_outlet.urlsafe())
    
    
    def to_configuration(self):
        configuration =  {
                'ticket_key'        : self.ticket_key,
                'expiry_date'       : self.expiry_date.strftime("%d-%m-%Y"),
                'entitled_datetime' : self.created_datetime.strftime("%d-%m-%Y %H:%M"),
                'merchant_acct_key' : self.merchant_acct_key,
                'used'              : self.used,
                'grabbed'           : self.grabbed,
                'drawed_details'    : self.drawed_details,
                }
        if self.used_datetime:
            configuration['used_datetime'] = self.used_datetime.strftime("%d-%m-%Y %H:%M:%s")
            
        if self.grabbed_datetime:
            configuration['grabbed_datetime'] = self.grabbed_datetime.strftime("%d-%m-%Y %H:%M:%s")    
            
        return configuration
    
    @staticmethod
    def list_by_customer_acct(customer_acct):
        return LuckyDrawTicket.query(ndb.AND(LuckyDrawTicket.removed==False), ancestor=customer_acct.create_ndb_key()).fetch(limit=model_conf.MAX_FETCH_RECORD)
    
    @staticmethod
    def list_entiteld_by_customer_acct_by_date_range(customer_acct, start_datetime=None, end_datetime=None):
        return LuckyDrawTicket.query(ndb.AND(LuckyDrawTicket.created_datetime>=start_datetime, LuckyDrawTicket.created_datetime<end_datetime), ancestor=customer_acct.create_ndb_key()).fetch(limit=model_conf.MAX_FETCH_RECORD)
    
    @staticmethod
    def count_entiteld_by_customer_acct_by_date_range(customer_acct, start_datetime=None, end_datetime=None):
        return LuckyDrawTicket.query(ndb.AND(LuckyDrawTicket.created_datetime>=start_datetime, LuckyDrawTicket.created_datetime<end_datetime), ancestor=customer_acct.create_ndb_key()).count(limit=model_conf.MAX_FETCH_RECORD)
    
    @staticmethod
    def count_by_merchant_acct(merchant_acct):
        return LuckyDrawTicket.query(ndb.AND(LuckyDrawTicket.merchant_acct==merchant_acct.create_ndb_key())).count(limit=model_conf.MAX_FETCH_RECORD)
    
    @staticmethod
    def list_by_merchant_acct(merchant_acct, offset=0, limit=50, start_cursor=None, return_with_cursor=True):
        query = LuckyDrawTicket.query(ndb.AND(LuckyDrawTicket.merchant_acct==merchant_acct.create_ndb_key(),))
        return LuckyDrawTicket.list_all_with_condition_query(query, start_cursor=start_cursor, return_with_cursor=return_with_cursor, offset=offset, limit=limit)
        
        
    
    @staticmethod
    def create_for_customer_from_sales_amount(customer_acct, sales_amount=None, merchant_acct=None, transact_outlet=None):
        number_of_ticket = 0
        lucky_draw_ticket_spending_currency = merchant_acct.lucky_draw_ticket_spending_currency
        
        logger.debug('sales_amount=%s', sales_amount)
        logger.debug('lucky_draw_ticket_spending_currency=%s', lucky_draw_ticket_spending_currency)
        
        if lucky_draw_ticket_spending_currency>0:
            if sales_amount> merchant_acct.lucky_draw_ticket_spending_currency:
                logger.debug('going to calculate draw ticket count')
                logger.info('is recurring scheme=%s', merchant_acct.lucky_draw_ticket_is_recurring_scheme)
                
                if merchant_acct.lucky_draw_ticket_is_recurring_scheme:
                    logger.info('lucky draw ticket spending requirement=%s', lucky_draw_ticket_spending_currency)
                    number_of_ticket = int(sales_amount/lucky_draw_ticket_spending_currency)
                else:
                    number_of_ticket = 1
            else:
                number_of_ticket = 0
        tickets_list = []
        
        logger.info('number_of_ticket to create=%d', number_of_ticket)
        
        if number_of_ticket>0:
            logger.debug('going to check maximum limit of ticket per day')
            ticket_limit_amount_per_day = merchant_acct.lucky_draw_ticket_limit_amount
            now = datetime.utcnow()
            start_datetime = now - timedelta(days=1)
            end_datetime = now
            entitled_ticket_count = LuckyDrawTicket.count_entiteld_by_customer_acct_by_date_range(customer_acct, start_datetime=start_datetime, end_datetime=end_datetime)
            balance_of_entitled_limit = ticket_limit_amount_per_day - entitled_ticket_count
            
            logger.info('balance_of_entitled_limit=%d', balance_of_entitled_limit)
            
            if balance_of_entitled_limit>0:
                if number_of_ticket>balance_of_entitled_limit:
                    number_of_ticket = balance_of_entitled_limit
            else:
                number_of_ticket = balance_of_entitled_limit
            
        logger.info('number_of_ticket after checking entitled limit per day=%d', number_of_ticket)
        
        for num in range(1, number_of_ticket+1):
            ticket = LuckyDrawTicket.create(customer_acct, merchant_acct, transact_outlet)
            if ticket:
                tickets_list.append(ticket)
            else:
                logger.warn('Cannot create ticket')
        
        return tickets_list
    
    def patch_prize_image_base_url(self):
        drawed_details = self.drawed_details
        logger.debug('drawed_details=%s', drawed_details)
        for prize in drawed_details.get('prizes'):
            
            logger.debug('prize=%s', prize)
            
            if prize.get('prize_type') == 'voucher':
                
                if '/static' in prize.get('image_url'):
                    index = prize.get('image_url').index('/static')
                
                    if index>0:
                        prize['image_url'] = prize.get('image_url')[index:]
                        
        won_prize = drawed_details.get('won_prize')
        if won_prize:
            if won_prize.get('prize_type') == 'voucher':
                if '/static' in won_prize.get('image_url'):
                    index = won_prize.get('image_url').index('/static')
                    if index>0:
                        won_prize['image_url'] = won_prize.get('image_url')[index:]
                
        
        logger.info('drawed_details=%s', drawed_details)
        
        
        if '/static'in drawed_details.get('ticket_image_url'):
            index = drawed_details.get('ticket_image_url').index('/static')
            drawed_details['ticket_image_url'] = drawed_details['ticket_image_url'][index:]
                
        #drawed_details['won_prize'] = won_prize
        
    @staticmethod
    def create(customer_acct, merchant_acct, transact_outlet):
        '''
        created_by_username    = None              
        
        if is_not_empty(created_by):
            if isinstance(created_by, MerchantUser):
                created_by_username = created_by.username
        '''        
        lucky_draw_ticket_expiry_date_length_in_day = merchant_acct.lucky_draw_ticket_expiry_date_length_in_day
        
        now = datetime.utcnow()
        expiry_date = now + timedelta(days=lucky_draw_ticket_expiry_date_length_in_day)
        logger.debug('expiry_date=%s', expiry_date)
        
        program = LuckyDrawTicket.__get_lucky_draw_program(merchant_acct.lucky_draw_configuration, customer_acct=customer_acct)
        if program:            
            program_key = program.get('program_key')
            prize_details_list      = program.get('program_settings').get('prize_settings').get('prizes')
            ticket_image_url        = program.get('program_settings').get('ticket_image_url')
            archived_vouchers_list  = MerchantVoucher.list_archived_by_merchant_account(merchant_acct)
            for prize in prize_details_list:
                if prize.get('prize_type') == program_conf.REWARD_FORMAT_VOUCHER:
                    found_voucher = False
                    for voucher_details in merchant_acct.published_voucher_configuration.get('vouchers'):
                        if voucher_details.get('voucher_key') == prize.get('voucher_key'):
                            prize['image_url']  = voucher_details.get('image_url')
                            prize['label']      = voucher_details.get('label')
                            found_voucher = True
                    
                    if found_voucher==False:
                        logger.info('Some voucher may be archived')
                        
                        if archived_vouchers_list:
                            for voucher_details in archived_vouchers_list:
                                if voucher_details.key_in_str == prize.get('voucher_key'):
                                    prize['image_url']  = voucher_details.image_public_url
                                    prize['label']      = voucher_details.label
                                    found_voucher = True
                            
            
            drawed_details =  {
                                'prizes'            : prize_details_list,
                                'ticket_image_url'  : ticket_image_url,
                                }
            
            lucky_draw_ticket = LuckyDrawTicket(
                                parent              = customer_acct.create_ndb_key(),
                                merchant_acct       = merchant_acct.create_ndb_key(),
                                transact_outlet     = transact_outlet.create_ndb_key(),
                                expiry_date         = expiry_date.date(),
                                ticket_key          = random_string(16),
                                drawed_details      = drawed_details,
                                program_key         = program_key,
                                #created_by          = created_by.create_ndb_key(),
                                #created_by_username = created_by_username,
                            )
            lucky_draw_ticket.put()
            
            logger.debug('lucky_draw_ticket=%s', lucky_draw_ticket)
            
            return lucky_draw_ticket 
    
    @staticmethod
    def get_by_ticket_key(ticket_key):
        return LuckyDrawTicket.query(LuckyDrawTicket.ticket_key ==ticket_key).get()
    
    
    def remove(self, customer_acct=None):
        self.removed            = True
        self.removed_datetime   = datetime.utcnow() 
        self.put()
        
        if customer_acct is None:
            customer_acct = self.customer_acct_entity
        Customer.remove_ticket_from_lucky_draw_ticket_summary(customer_acct, self.to_configuration())
        
    def grab_the_prize(self, customer_acct=None):
        self.grabbed            = True
        self.grabbed_datetime   = datetime.utcnow() 
        
        self.put()   
        
        if customer_acct is None:
            customer_acct = self.customer_acct_entity
            
        Customer.remove_ticket_from_lucky_draw_ticket_summary(customer_acct, self.to_configuration())
        
    def draw_update_prize_sequence(self, selected_index=-1): 
        drawed_prize_sequence_indexes   = []
        
        prize_details_list = self.drawed_details.get('prizes')
        
        for p in prize_details_list:
            drawed_prize_sequence_indexes.append(p.get('prize_index'))
        
        won_prize_details = self.drawed_details['won_prize']
        self.drawed_details['selected_index']       = selected_index
        
        random.shuffle(drawed_prize_sequence_indexes)
                
        won_prize_sequence_index = drawed_prize_sequence_indexes.index(won_prize_details['prize_index'])
        
        temp = drawed_prize_sequence_indexes[selected_index]
        drawed_prize_sequence_indexes[selected_index] = won_prize_details['prize_index']
        drawed_prize_sequence_indexes[won_prize_sequence_index] = temp
        
        self.drawed_details['drawed_prize_sequence_indexes']    = drawed_prize_sequence_indexes
        self.put()

    def draw(self, selected_index=-1):

        now = datetime.utcnow()
        if self.expiry_date>=now.date():
            if self.used==False or self.drawed_details.get('won_prize') is None:
                prize_details_list = self.drawed_details.get('prizes')
                
                prizes_to_draw                  = {}
                prizes                          = []
                accum_weights                   = []
                accum_weight                    = 0
                drawed_prize_sequence_indexes   = []
                
                for p in prize_details_list:
                    prizes_to_draw[p.get('prize_index')] = p.get('possibility')
                    prizes.append(p.get('prize_index'))
                    accum_weight+=p.get('possibility')
                    accum_weights.append(accum_weight)
                    drawed_prize_sequence_indexes.append(p.get('prize_index'))
                    
                
                logger.debug('prizes=%s', prizes)
                logger.debug('accum_weights=%s', accum_weights)
                
                won_prize_index = random.choices(prizes, cum_weights=accum_weights, k=1)[0]    
                logger.debug('won_prize_index=%s', won_prize_index)
                    
                won_prize_details = None
                if won_prize_index:
                    for p in prize_details_list:
                        if p.get('prize_index') == won_prize_index:
                            won_prize_details = p
                            break
                
                self.drawed_details['won_prize']                        = won_prize_details
                self.drawed_details['selected_index']                   = selected_index
                
                random.shuffle(drawed_prize_sequence_indexes)
                
                won_prize_sequence_index = drawed_prize_sequence_indexes.index(won_prize_details['prize_index'])
                
                temp = drawed_prize_sequence_indexes[selected_index]
                drawed_prize_sequence_indexes[selected_index] = won_prize_details['prize_index']
                drawed_prize_sequence_indexes[won_prize_sequence_index] = temp
                
                
                self.drawed_details['drawed_prize_sequence_indexes']    = drawed_prize_sequence_indexes
                self.used               = True
                self.used_datetime      = now 
                self.put()
                
                customer_acct = self.customer_acct_entity
                Customer.update_ticket_into_lucky_draw_ticket_summary(customer_acct, self.to_configuration())
                
            
        
        else:
            raise Exception('Ticket is expired')
    
    @staticmethod
    def __get_lucky_draw_program(lucky_draw_configuration, customer_acct=None):
        logger.debug('---__get_lucky_draw_program---')
        programs            = lucky_draw_configuration.get('programs')
        #ordered_programs    = sort_dict_list(programs, 'start_date')
        count               = lucky_draw_configuration.get('count')
        
        #filter by check exclusivity
        
        if count>=1:
            return LuckyDrawTicket.__filter_by_exclusivity(programs, customer_acct=customer_acct)
        
            
        
    @staticmethod    
    def __filter_by_exclusivity(programs, customer_acct=None):
        logger.debug('--__filter_by_exclusivity--')
        no_exclusivity_program = None
        
        for program in programs:
            is_match = False
            if program.get('program_settings').get('exclusivity_settings'):
                exclusivity_settings = program.get('program_settings').get('exclusivity_settings')
                if exclusivity_settings:
                    exclusived_tags_list                = exclusivity_settings.get('tags')
                    exclusived_memberships_list         = exclusivity_settings.get('memberships')
                    exclusived_tier_memberships_list    = exclusivity_settings.get('tier_memberships')
                    
                    if isinstance(exclusived_tags_list, str) and is_empty(exclusived_tags_list):
                        exclusived_tags_list = []
                        
                    if isinstance(exclusived_memberships_list, str) and is_empty(exclusived_memberships_list):
                        exclusived_memberships_list = []
                        
                    if isinstance(exclusived_tier_memberships_list, str) and is_empty(exclusived_tier_memberships_list):
                        exclusived_tier_memberships_list = []        
                    
                    if no_exclusivity_program is None:
                        if is_empty(exclusived_tags_list) and is_empty(exclusived_memberships_list) and is_empty(exclusived_tier_memberships_list):
                            no_exclusivity_program = program
                        
                    if not is_match:
                        if is_not_empty(exclusived_tags_list) and LuckyDrawTicket.__is_customer_tagged_match(customer_acct, exclusived_tags_list):
                            logger.debug('__filter_by_exclusivity debug: Customer tag matched')
                            is_match = True
                        else:
                            logger.debug('__filter_by_exclusivity debug: Customer tag not match')
                    
                    if not is_match:
                        if is_not_empty(exclusived_memberships_list) and  LuckyDrawTicket.__is_customer_membership_match(customer_acct, exclusived_memberships_list):
                            logger.debug('__filter_by_exclusivity debug: Customer membership matched')
                            is_match = True
                        else:
                            logger.debug('__filter_by_exclusivity debug: Customer membership not match')
                        
                    if not is_match:
                        if is_not_empty(exclusived_tier_memberships_list) and  LuckyDrawTicket.__is_customer_tier_membership_match(customer_acct, exclusived_tier_memberships_list):
                            logger.debug('__filter_by_exclusivity debug: Customer tier membership matched')
                            is_match = True
                        else:
                            logger.debug('__filter_by_exclusivity debug: Customer tier membership not match')
                else:
                    logger.debug('__filter_by_exclusivity debug: no exclusivity in program thus matched')
                    is_match = True
                
                if is_match:
                    logger.debug('__filter_by_exclusivity debug: matched program=%s', program)
                    return program
            else:
                if no_exclusivity_program is None:
                    no_exclusivity_program = program
                    
        return no_exclusivity_program
        
    
    @staticmethod   
    def __is_customer_tagged_match(customer_details, exclusived_tags_list=None):
        if customer_details.tags_list:
            customer_tags_set   = set(customer_details.tags_list) 
            exclusived_tags_set = set(exclusived_tags_list)
            
            if customer_tags_set.intersection(exclusived_tags_set):
                return True
        
        return False
    
    @staticmethod   
    def __is_customer_membership_match(customer_details, exclusived_memberships_list=None):
        if customer_details.memberships_list:
            customer_memberships_set   = set(customer_details.memberships_list) 
            exclusived_memberships_set = set(exclusived_memberships_list)
            
            if customer_memberships_set.intersection(exclusived_memberships_set):
                return True
        
        return False
    
    @staticmethod   
    def __is_customer_tier_membership_match(customer_details, exclusived_tier_memberships_list=None):
        if customer_details.tier_membership:
            if customer_details.tier_membership in exclusived_tier_memberships_list:
                return True
        
        return False
    
    @staticmethod
    def delete_all_by_customer(customer_acct):
        query = LuckyDrawTicket.query(ancestor = customer_acct.create_ndb_key())
        LuckyDrawTicket.delete_multiples(query)
            
    