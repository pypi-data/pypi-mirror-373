
from google.cloud import ndb
from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel
from trexmodel.models.datastore.merchant_models import Outlet
from trexlib.utils.string_util import random_number, is_not_empty
import logging
from trexconf import conf
from datetime import datetime
from trexmodel.models.datastore.product_models import ProductCatalogue
from trexmodel.models.datastore.model_decorators import model_transactional
from google.api_core.operations_v1.operations_client_config import config

logger = logging.getLogger('debug')


class POSSetting(BaseNModel,DictModel):
    '''
    merchant_acct as ancestor
    '''
    device_name                     = ndb.StringProperty(required=True)
    activation_code                 = ndb.StringProperty(required=True)
    device_id                       = ndb.StringProperty(required=False)
    enable_lock_screen              = ndb.BooleanProperty(required=True, default=False)
    lock_screen_code                = ndb.StringProperty(required=False, default='')
    lock_screen_length_in_second    = ndb.IntegerProperty(required=False, default=30)
    activated                       = ndb.BooleanProperty(required=True, default=False)
    assigned_outlet                 = ndb.KeyProperty(name="assigned_outlet", kind=Outlet)
    #assigned_catalogue      = ndb.KeyProperty(name="assigned_outlet", kind=ProductCatalogue)
    created_datetime                = ndb.DateTimeProperty(required=True, auto_now_add=True)
    activated_datetime              = ndb.DateTimeProperty(required=False)
    testing                         = ndb.BooleanProperty(required=False, default=False)
    device_details                  = ndb.JsonProperty()
    
    dict_properties = ['device_name', 'activation_code', 'device_id', 'activated', 'assigned_outlet_key', 
                       'enable_lock_screen', 'lock_screen_code', 'lock_screen_length_in_second', 
                       'device_details', 'activated_datetime', 'created_datetime']
    
    @property
    def device_tokens_list(self):
        _tokens_list = []
        
        if self.device_details:
            
            for k,v in self.device_details.items():
                for dd in v:
                    _tokens_list.append(dd.get('device_token'))
        return _tokens_list
    
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
        return self.assigned_outlet_entity.merchant_acct_entity
    
    @staticmethod
    def create(device_name, merchant_acct, assign_outlet):
        activation_code = random_number(16)
        checking_activation_pos_setting = POSSetting.get_by_activation_code(activation_code)
        regenerate_activation_code = False
        
        if checking_activation_pos_setting:
            regenerate_activation_code = True
        
        while(regenerate_activation_code):
            activation_code = random_number(16)
            checking_activation_pos_setting = POSSetting.get_by_activation_code(activation_code)
            if checking_activation_pos_setting==None:
                regenerate_activation_code = False
            
        
        pos_setting = POSSetting(
                                parent                  = merchant_acct.create_ndb_key(),
                                device_name             = device_name,
                                activation_code         = activation_code,
                                assigned_outlet         = assign_outlet.create_ndb_key(),
                                
                                )
        
        pos_setting.put()
        return pos_setting
    
    @staticmethod
    def update(pos_setting_key, device_name, assigned_outlet):
        pos_setting                         = POSSetting.fetch(pos_setting_key)
        pos_setting.device_name             = device_name
        pos_setting.assigned_outlet         = assigned_outlet.create_ndb_key()
        
        pos_setting.put()
        
        return pos_setting
    
    def update_device_details(self, platform, device_token):
        if self.device_details:
            found_device_details_list_by_platform = self.device_details.get(platform)
            if found_device_details_list_by_platform:
                self.device_details[platform] = {
                                                'device_token'              : device_token,
                                                'last_updated_datetime'     : datetime.utcnow().strftime("%d-%m-%Y %H:%M:%S"),
                                                }
                                                        
                
                    
            else:
                self.device_details[platform] = {
                                                'device_token'              : device_token,
                                                'last_updated_datetime'     : datetime.utcnow().strftime("%d-%m-%Y %H:%M:%S"),
                                                }
        else:
            self.device_details = {
                                    platform :  {
                                                    'device_token'              : device_token,
                                                    'last_updated_datetime'     : datetime.utcnow().strftime("%d-%m-%Y %H:%M:%S"),
                                                    }
                                                
                                }
        self.put() 
    
    @staticmethod
    def get_by_activation_code(activation_code):
        pos_setting = POSSetting.query(POSSetting.activation_code ==activation_code).get()
        return pos_setting
    
    @staticmethod
    def list_by_merchant_account(merchant_acct, offset=0, limit=conf.PAGINATION_SIZE, start_cursor=None, return_with_cursor=False):
        query = POSSetting.query(ancestor=merchant_acct.create_ndb_key())
        
        return POSSetting.list_all_with_condition_query(query, offset=offset, limit=limit, start_cursor=start_cursor, return_with_cursor=return_with_cursor)
    
    @staticmethod
    def count_by_merchant_acct(merchant_acct):
        if merchant_acct:
            query = POSSetting.query(ancestor=merchant_acct.create_ndb_key())
        else:
            query = POSSetting.query()
        
        return POSSetting.count_with_condition_query(query)
    
    @staticmethod
    def list_by_merchant_account_and_assigned_outlet(merchant_acct, assigned_outlet, offset=0, limit=conf.PAGINATION_SIZE, start_cursor=None, return_with_cursor=False):
        query = POSSetting.query(ndb.AND(
                        POSSetting.assigned_outlet==assigned_outlet.create_ndb_key()
                        ),ancestor=merchant_acct.create_ndb_key())
        
        return POSSetting.list_all_with_condition_query(query, offset=offset, limit=limit, start_cursor=start_cursor, return_with_cursor=return_with_cursor)
    
    @staticmethod
    def count_by_merchant_account_and_assigned_outlet(merchant_acct, assigned_outlet):
        query = POSSetting.query(ndb.AND(
                        POSSetting.assigned_outlet==assigned_outlet.create_ndb_key()
                        ),ancestor=merchant_acct.create_ndb_key())
        
        return POSSetting.count_with_condition_query(query)
        
    def activate(self, device_id):
        self.device_id          = device_id
        self.activated          = True
        self.activated_datetime = datetime.utcnow()
        self.put()
        
        
    @staticmethod
    def remove_by_activation_code(activation_code):
        checking_pos_setting = POSSetting.get_by_activation_code(activation_code)
        if checking_pos_setting:
            checking_pos_setting.delete()
            return True
        else:
            return False
    '''    
    @property
    def setting(self):
        merchant_acct           = MerchantAcct.fetch(self.parent_key)
        invoice_no_generation   = InvoiceNoGeneration.getByMerchantAcct(merchant_acct)
        account_settings        = merchant_acct.account_settings
        rounding_setup          = RoundingSetup.get_by_merchant_acct(merchant_acct)
        receipt_setup           = ReceiptSetup.get_by_merchant_acct(merchant_acct)
        outlet                  = self.assigned_outlet_entity
        dinning_option_json     = []
        dinning_option_list     = DinningOption.list_by_merchant_acct(merchant_acct)
        
        if dinning_option_list:
            for d in dinning_option_list:
                dinning_option_json.append({
                                            'option_key'                : d.key_in_str,
                                            'option_name'               : d.name,
                                            'option_prefix'             : d.prefix,
                                            'is_default'                : d.is_default,
                                            'is_dinning_input'          : d.is_dinning_input,
                                            'dinning_table_is_required' : d.dinning_table_is_required,
                                            'assign_queue'              : d.assign_queue,
                                            })
        
        
        account_settings['dinning_option_list'] = dinning_option_json
        account_settings['invoice_settings']    = {
                                                     'invoice_no_generators'    : invoice_no_generation.generators_list,
                                                                     
                                                    }
        
        if receipt_setup:
            account_settings['receipt_settings'] = {
                                                    'header_data_list': receipt_setup.receipt_header_settings,
                                                    'footer_data_list': receipt_setup.receipt_footer_settings,
                                                    }
        
        if rounding_setup:
            account_settings['rounding_settings']     = {
                                                        'rounding_interval' : rounding_setup.rounding_interval,
                                                        'rounding_rule'     : rounding_setup.rounding_rule,
                                                        }
        pos_payment_method_json = []
        pos_payment_method_list = PosPaymentMethod.list_by_merchant_acct(merchant_acct)
        
        if pos_payment_method_list:
            for d in pos_payment_method_list:
                pos_payment_method_json.append({
                                            'code'                  : d.code,
                                            'key'                   : d.key_in_str,
                                            'label'                 : d.label,
                                            'is_default'            : d.is_default,
                                            'is_rounding_required'  : d.is_rounding_required,
                                            })
        
        account_settings['assigned_service_charge_setup']   = outlet.service_charge_settings
        account_settings['assigned_tax_setup']              = outlet.assigned_tax_setup
        account_settings['dinning_table_list']              = outlet.assigned_dinning_table_list
        account_settings['payment_methods']                 = pos_payment_method_json
        
        outlet_details = {
                        'key'                        : self.assigned_outlet_key,
                        'id'                         : outlet.id,
                        'company_name'               : outlet.company_name,
                        'business_reg_no'            : outlet.business_reg_no,
                        'address'                    : outlet.address,
                        'email'                      : outlet.email,
                        'phone'                      : outlet.office_phone,
                        'website'                    : merchant_acct.website or '',  
                        'outlet_name'                : outlet.name,    
                        }
        
        return {
                'activation_code'                   : self.activation_code,
                'device_name'                       : self.device_name,
                'company_name'                      : merchant_acct.company_name,
                'website'                           : merchant_acct.website,
                'account_id'                        : self.parent_key,
                'api_key'                           : merchant_acct.api_key,
                'logo_image_url'                    : merchant_acct.logo_public_url,
                'account_settings'                  : account_settings,
                'outlet_details'                    : outlet_details,
                }
    '''    
        
class POSCatalogue(BaseNModel,DictModel):
    '''
    merchant_acct as ancestor
    '''
    assigned_catalogue      = ndb.KeyProperty(name="assigned_catalogue", kind=ProductCatalogue)        
    assigned_outlet_list    = ndb.JsonProperty()
    
    is_publish              = ndb.BooleanProperty(default=False)
    
    created_datetime        = ndb.DateTimeProperty(required=True, auto_now_add=True)
    modified_datetime       = ndb.DateTimeProperty(required=False, auto_now=True)
    
    dict_properties = ['assigned_catalogue_key', 'assigned_outlet_list', 'is_publish']
    
    @property
    def assigned_catalogue_key(self):
        return self.assigned_catalogue.urlsafe().decode('utf-8')
    
    @staticmethod
    def list_by_merchant_acct(merchant_acct):
        return POSCatalogue.query(ancestor = merchant_acct.create_ndb_key()).fetch(limit=conf.MAX_FETCH_RECORD)
    
    @staticmethod
    @model_transactional(desc='POSCatalogue.create')
    def create(assigned_catalogue_key, merchant_acct, assigned_outlet_key_list=[]):
        if assigned_outlet_key_list:
            
            
            assigned_catalogue = ProductCatalogue.fetch(assigned_catalogue_key)
            if assigned_catalogue: 
                
                outlet_catalogue = POSCatalogue(
                                                                parent                  = merchant_acct.create_ndb_key(),
                                                                assigned_catalogue      = assigned_catalogue.create_ndb_key(),
                                                                assigned_outlet_list    = assigned_outlet_key_list,
                                                                )
                
                outlet_catalogue.put()
                
                return outlet_catalogue
                
            else:
                raise Exception('Invalid catalogue data')
                
                
        else:
            raise Exception('Missing assign outlet')    
        
    
    @staticmethod
    @model_transactional(desc='POSCatalogue.udpate')
    def update(pos_assigned_outlet_key, assigned_catalogue_key, assigned_outlet_key_list=[]):
        if is_not_empty(pos_assigned_outlet_key):
            outlet_catalogue = POSCatalogue.fetch(pos_assigned_outlet_key)
            if outlet_catalogue:
                assigned_catalogue = ProductCatalogue.fetch(assigned_catalogue_key)
                if assigned_catalogue:
                    outlet_catalogue.assigned_catalogue    = assigned_catalogue.create_ndb_key()
                    outlet_catalogue.assigned_outlet_list  = assigned_outlet_key_list
                    
                    outlet_catalogue.put()
                    
                    
                else:
                    raise Exception('Invalid catalogue data')
            else:
                raise Exception('Invalid pos assign catalogue data')
        else:
            raise Exception('POS assign catalogue key is empty')
    
    @model_transactional(desc='POSCatalogue.publish')   
    def publish(self):
        self.is_publish          = True
        assigned_catalogue_key  = self.assigned_catalogue.urlsafe().decode('utf-8')
        
        for outlet_key in self.assigned_outlet_list:
            Outlet.assign_catalogue_to_outlet(outlet_key, assigned_catalogue_key)
        
        self.put()
        
    @model_transactional(desc='POSAssignedCatalogue.unpublish')    
    def unpublish(self):
        self.is_publish          = False
        
        for outlet_key in self.assigned_outlet_list:
            Outlet.remove_catalogue_from_outlet(outlet_key)
        
        self.put()
        
class DinningTableSetup(BaseNModel,DictModel):
    name                    = ndb.StringProperty(required=True)
    table_list              = ndb.StringProperty(required=True)
    assigned_outlet_list    = ndb.JsonProperty()
    is_publish              = ndb.BooleanProperty(default=False)
    show_occupied           = ndb.BooleanProperty(default=False)
    modified_datetime       = ndb.DateTimeProperty(auto_now=True)
    
    
    dict_properties = ['name', 'table_list', 'assigned_outlet_list', 'is_publish', 'show_occupied']
    
    @staticmethod
    def create(name, table_list, assigned_outlet_key_list, merchant_acct, show_occupied=False):
        dinning_table_setup = DinningTableSetup(
                                        parent                  = merchant_acct.create_ndb_key(),
                                        name                    = name, 
                                        is_publish              = False,
                                        table_list              = table_list,
                                        show_occupied           = show_occupied,
                                        assigned_outlet_list    = assigned_outlet_key_list,
                                        )
        dinning_table_setup.put()
        return dinning_table_setup
    
    @staticmethod
    def update(dinning_table_setup, name, table_list, assigned_outlet_key_list, show_occupied=False):
        dinning_table_setup.name                    = name
        dinning_table_setup.table_list              = table_list
        dinning_table_setup.assigned_outlet_list    = assigned_outlet_key_list
        dinning_table_setup.is_publish              = False
        dinning_table_setup.show_occupied           = show_occupied
        dinning_table_setup.put()
    
    @staticmethod    
    def remove(dinning_table_setup):
        dinning_table_setup.delete()
        
    @model_transactional(desc='DinningTableSetup.publish')   
    def publish(self):
        self.is_publish          = True  
          
        for outlet_key in self.assigned_outlet_list:
            Outlet.assign_dinning_table_setup_to_outlet(outlet_key, self.table_list)
            Outlet.assign_dinning_table_control_to_outlet(outlet_key, self.show_occupied)
        
        self.put()
            
    @model_transactional(desc='DinningTableSetup.unpublish')   
    def unpublish(self):
        self.is_publish          = False  
          
        for outlet_key in self.assigned_outlet_list:
            Outlet.remove_dinning_table_setup_from_outlet(outlet_key)
            Outlet.assign_dinning_table_control_to_outlet(outlet_key, False)
            
        self.put()         
        
    @staticmethod
    def list_by_merchant_acct(merchant_acct):
        return DinningTableSetup.query(ancestor = merchant_acct.create_ndb_key()).fetch(limit=conf.MAX_FETCH_RECORD)
    
    def generate_weblink_details_list(self, outlet_key, dinning_option, weblink_url_format):
        table_list_in_list = self.table_list.split(',')
        table_weblink_details_list = []
        for table in table_list_in_list:
            web_link = weblink_url_format.format(outlet_key=outlet_key, dinning_option=dinning_option, table=table)
            table_weblink_details_list.append({
                                            'table'             : table,
                                            'dinning_option'    : dinning_option,
                                            'web_link'          :  web_link,  
                                             
                                            })
        
        return table_weblink_details_list
        
class DinningOption(BaseNModel,DictModel):
    name                        = ndb.StringProperty(required=True)
    prefix                      = ndb.StringProperty(required=False)  
    is_default                  = ndb.BooleanProperty(default=False)
    is_dinning_input            = ndb.BooleanProperty(default=True)
    is_takeaway_input           = ndb.BooleanProperty(default=False)
    is_delivery_input           = ndb.BooleanProperty(default=False)
    is_self_order_input         = ndb.BooleanProperty(default=False)
    is_self_payment_mandatory   = ndb.BooleanProperty(default=False)
    is_archive                  = ndb.BooleanProperty(default=False)
    dinning_table_is_required   = ndb.BooleanProperty(default=False)
    assign_queue                = ndb.BooleanProperty(default=False) 
    modified_datetime           = ndb.DateTimeProperty(auto_now=True) 
    archived_datetime           = ndb.DateTimeProperty(required=False) 
    
    dict_properties = ['name','prefix', 'is_dinning_input', 'is_delivery_input', 'is_takeaway_input', 'is_self_order_input', 'is_self_payment_mandatory', 'is_archive', 'is_default', 'dinning_table_is_required', 'assign_queue']
    
    @staticmethod
    def create(name, prefix, merchant_acct, is_dinning_input=False, is_delivery_input=False, is_takeaway_input=False, is_self_order_input=False, is_self_payment_mandatory=False, is_default=False, dinning_table_is_required=False, assign_queue=False):
        dinning_option = DinningOption(
                                        parent                      = merchant_acct.create_ndb_key(),
                                        name                        = name,
                                        prefix                      = prefix,
                                        is_dinning_input            = is_dinning_input, 
                                        is_delivery_input           = is_delivery_input,   
                                        is_takeaway_input           = is_takeaway_input,
                                        is_self_order_input         = is_self_order_input,
                                        is_self_payment_mandatory   = is_self_payment_mandatory,    
                                        is_default                  = is_default,
                                        dinning_table_is_required   = dinning_table_is_required,
                                        assign_queue                = assign_queue,
                                        )
        dinning_option.put()
        return dinning_option
    
    @staticmethod
    def update(dinning_option, name, prefix, is_dinning_input=False, is_delivery_input=False, is_takeaway_input=False, is_self_order_input=False, is_self_payment_mandatory=False, is_default=False, dinning_table_is_required=False, assign_queue=False):
        dinning_option.name                         = name
        dinning_option.prefix                       = prefix
        dinning_option.is_default                   = is_default
        dinning_option.is_dinning_input             = is_dinning_input
        dinning_option.is_delivery_input            = is_delivery_input
        dinning_option.is_takeaway_input            = is_takeaway_input
        dinning_option.is_self_order_input          = is_self_order_input
        dinning_option.is_self_payment_mandatory    = is_self_payment_mandatory
        dinning_option.dinning_table_is_required    = dinning_table_is_required
        dinning_option.assign_queue                 = assign_queue
        dinning_option.put()
        
    @staticmethod
    def list_by_merchant_acct(merchant_acct):
        return DinningOption.query(ndb.AND(DinningOption.is_archive==False), ancestor = merchant_acct.create_ndb_key()).fetch(limit=conf.MAX_FETCH_RECORD)
    
    @staticmethod    
    def archive(dinning_option):
        dinning_option.is_archive = True
        dinning_option.archived_datetime = datetime.utcnow()
        dinning_option.put()   

class InvoiceNoGeneration(BaseNModel,DictModel):
    generators_list    = ndb.JsonProperty()
    
    dict_properties = ['generators_list']

    @staticmethod
    def create(generators_list, merchant_acct):
        invocie_no_generation = InvoiceNoGeneration.getByMerchantAcct(merchant_acct)
        if invocie_no_generation:
            invocie_no_generation.generators_list = generators_list
        else:    
            invocie_no_generation = InvoiceNoGeneration(
                                    parent = merchant_acct.create_ndb_key(),
                                    generators_list = generators_list,
                                )
    
        invocie_no_generation.put()
        
        return invocie_no_generation
    
    @staticmethod
    def update(invoice_no_generation, generators_list):
        invoice_no_generation.generators_list = generators_list
        invoice_no_generation.put()
        
    @staticmethod
    def getByMerchantAcct(merchant_acct):
        return InvoiceNoGeneration.query(ancestor=merchant_acct.create_ndb_key()).get()

class PosPaymentMethod(BaseNModel,DictModel):
    code                        = ndb.StringProperty(required=True)
    label                       = ndb.StringProperty(required=True)  
    is_default                  = ndb.BooleanProperty(default=False)
    is_rounding_required        = ndb.BooleanProperty(default=False)
    not_archivable              = ndb.BooleanProperty(default=False)
    is_archive                  = ndb.BooleanProperty(default=False)
    modified_datetime           = ndb.DateTimeProperty(auto_now=True) 
    archived_datetime           = ndb.DateTimeProperty(required=False) 
    
    dict_properties = ['code', 'label','is_archive', 'is_default', 'not_archivable', 'is_rounding_required']
    
    @staticmethod
    def create_cash_payment(merchant_acct):
        cash = PosPaymentMethod.query(ndb.AND(PosPaymentMethod.code=='cash'), ancestor=merchant_acct.create_ndb_key()).get()
        logger.debug('cash=%s', cash);
        if cash is None:
            cash = PosPaymentMethod(
                                    parent                  = merchant_acct.create_ndb_key(),
                                    code                    = 'cash',
                                    label                   = 'Cash',
                                    is_default              = True,
                                    not_archivable          = True,
                                    is_rounding_required    = True,
                                                      
                                )
            cash.put()
        return cash
    
    @staticmethod
    def create(label, merchant_acct, is_default=False, is_rounding_required=False):
        code = label.replace(' ', '_')
        payment_method = PosPaymentMethod(
                                        parent                      = merchant_acct.create_ndb_key(),
                                        code                        = code,
                                        label                       = label,
                                        is_default                  = is_default,
                                        is_rounding_required        = is_rounding_required,
                                        )
        payment_method.put()
        return payment_method
    
    @staticmethod
    def update(payment_method, label, is_default=False, is_rounding_required=False):
        code = 'cash'
        if payment_method.code!='cash':
            code = label.replace(' ', '_')
        
        payment_method.code                         = code
        payment_method.label                        = label
        payment_method.is_default                   = is_default
        payment_method.is_rounding_required         = is_rounding_required
        payment_method.put()
        
    @staticmethod
    def list_by_merchant_acct(merchant_acct):
        PosPaymentMethod.create_cash_payment(merchant_acct)
        payment_methods_list =  PosPaymentMethod.query(ndb.AND(PosPaymentMethod.is_archive==False), ancestor = merchant_acct.create_ndb_key()).fetch(limit=conf.MAX_FETCH_RECORD)
        
        return payment_methods_list
    
    @staticmethod    
    def archive(payment_method):
        payment_method.is_archive = True
        payment_method.archived_datetime = datetime.utcnow()
        payment_method.put()
        
class ServiceChargeSetup(BaseNModel,DictModel):
    charge_name                     = ndb.StringProperty(required=True)
    charge_label                    = ndb.StringProperty(required=True)
    charge_pct_amount               = ndb.IntegerProperty(required=True)
    applyed_dinning_option_list     = ndb.JsonProperty()
    assigned_outlet_list            = ndb.JsonProperty()
    is_publish                      = ndb.BooleanProperty(default=False)
    modified_datetime               = ndb.DateTimeProperty(auto_now=True)
    
    
    dict_properties = ['charge_name', 'charge_label', 'charge_pct_amount', 'applyed_dinning_option_list', 'assigned_outlet_list', 'is_publish']
    
    @staticmethod
    def create(charge_name, charge_label, charge_pct_amount, applyed_dinning_option_list, assigned_outlet_key_list, merchant_acct):
        service_charge_setup = ServiceChargeSetup(
                                        parent                      = merchant_acct.create_ndb_key(),
                                        charge_name                 = charge_name,    
                                        charge_label                = charge_label,
                                        charge_pct_amount           = charge_pct_amount, 
                                        applyed_dinning_option_list = applyed_dinning_option_list,
                                        is_publish                  = False,
                                        assigned_outlet_list        = assigned_outlet_key_list,
                                        )
        service_charge_setup.put()
        return service_charge_setup
    
    @staticmethod
    def update(service_charge_setup, charge_name, charge_label, charge_pct_amount, applyed_dinning_option_list, assigned_outlet_key_list):
        service_charge_setup.charge_name                    = charge_name
        service_charge_setup.charge_label                   = charge_label
        service_charge_setup.charge_pct_amount              = charge_pct_amount
        service_charge_setup.applyed_dinning_option_list    = applyed_dinning_option_list
        service_charge_setup.assigned_outlet_list           = assigned_outlet_key_list
        service_charge_setup.is_publish                     = False
        service_charge_setup.put()
    
    @staticmethod    
    def remove(service_charge_setup):
        service_charge_setup.delete()
        
    @model_transactional(desc='ServiceChargeSetup.publish')   
    def publish(self):
        self.is_publish          = True  
          
        for outlet_key in self.assigned_outlet_list:
            outlet = Outlet.fetch(outlet_key)
            if outlet:
                service_charge_details = {
                                        'charge_key'                    : self.key_in_str,
                                        'charge_label'                  : self.charge_label,
                                        'charge_pct_amount'             : self.charge_pct_amount,
                                        'applied_dinning_option_list'   : self.applyed_dinning_option_list,
                                        }
                if outlet.service_charge_settings:
                    outlet.service_charge_settings[self.key_in_str] = service_charge_details
                else:
                    outlet.service_charge_settings = {
                                                        self.key_in_str: service_charge_details
                                                    }
                
                outlet.put()
        
        self.put()
            
    @model_transactional(desc='ServiceChargeSetup.unpublish')   
    def unpublish(self):
        self.is_publish          = False  
          
        for outlet_key in self.assigned_outlet_list:
            outlet = Outlet.fetch(outlet_key)
            if outlet:
                del outlet.service_charge_settings[self.key_in_str]
                outlet.put()
            
        self.put()         
        
    @staticmethod
    def list_by_merchant_acct(merchant_acct):
        return ServiceChargeSetup.query(ancestor = merchant_acct.create_ndb_key()).fetch(limit=conf.MAX_FETCH_RECORD)
    

class RoundingSetup(BaseNModel,DictModel):
    rounding_interval           = ndb.StringProperty(required=True)
    rounding_rule               = ndb.StringProperty(required=True, default='')  
    modified_datetime           = ndb.DateTimeProperty(auto_now=True)    
    
    dict_properties = ['rounding_interval', 'rounding_rule']
    
    @staticmethod
    def create(rounding_interval, rounding_rule, merchant_acct):
        rounding_setup = RoundingSetup(
                                parent                  = merchant_acct.create_ndb_key(),
                                rounding_interval       = rounding_interval, 
                                rounding_rule           = rounding_rule,
                            )
          
        rounding_setup.put()
        return rounding_setup
    
    @staticmethod
    def update(rounding_setup, rounding_interval, rounding_rule):
        rounding_setup.rounding_interval   = rounding_interval
        rounding_setup.rounding_rule       = rounding_rule
        rounding_setup.put()
        
    @staticmethod
    def get_by_merchant_acct(merchant_acct):
        return RoundingSetup.query(ancestor = merchant_acct.create_ndb_key()).get()
    
                  