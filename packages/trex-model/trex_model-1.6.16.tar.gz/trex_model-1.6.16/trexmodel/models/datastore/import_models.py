'''
Created on 26 Sep 2023

@author: jacklok
'''

from google.cloud import ndb
from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel
from trexlib.utils.string_util import random_string
from trexmodel.models.datastore.merchant_models import MerchantAcct
import logging
import csv, io

from trexconf import program_conf

logger = logging.getLogger('model')

class ImportCustomerFile(BaseNModel, DictModel):
    merchant_acct               = ndb.KeyProperty(name="merchant_acct", kind=MerchantAcct)
    file_public_url             = ndb.StringProperty(required=True)
    file_storage_filename       = ndb.StringProperty(required=True)
    import_settings             = ndb.JsonProperty()
    
    dict_properties = ['file_public_url', 'file_storage_filename', 'import_settings', 'merchant_acct_key']
    
    @property
    def merchant_acct_key(self):
        return self.merchant_acct.urlsafe().decode('utf-8')
    
    @property
    def merchant_acct_entity(self):
        return MerchantAcct.fetch(self.merchant_acct.urlsafe())
    
    @staticmethod
    def get(merchant_acct):
        return ImportCustomerFile.query(ImportCustomerFile.merchant_acct==merchant_acct.create_ndb_key()).get()
    
    @staticmethod
    def upload_file(merchant_acct, uploading_file, bucket):
        file_prefix                         = random_string(8)
        file_storage_filename               = 'import/customer/'+merchant_acct.account_code+'/'+file_prefix+'-'+uploading_file.filename
        blob                                = bucket.blob(file_storage_filename)
        
        logger.debug('file_storage_filename=%s', file_storage_filename)
        
        blob.upload_from_string(
                uploading_file.read(),
                content_type=uploading_file.content_type
            )
        
        uploaded_url        = blob.public_url
        
        logger.debug('uploaded_url=%s', uploaded_url)
        
        import_customer_file = ImportCustomerFile.get(merchant_acct)
        
        if import_customer_file is None:
            import_customer_file = ImportCustomerFile(
                                    merchant_acct               = merchant_acct.create_ndb_key(),
                                    file_public_url             = uploaded_url,
                                    file_storage_filename       = file_storage_filename,
                                    import_settings             = {},
                                    
                                    )
        else:
            old_file_blob = bucket.get_blob(import_customer_file.file_storage_filename) 
            if old_file_blob:
                old_file_blob.delete()
            
            import_customer_file.file_public_url                = uploaded_url
            import_customer_file.file_storage_filename          = file_storage_filename
            import_customer_file.import_settings                = {}
            
            
            
        import_customer_file.put()
        
        return import_customer_file
    
    @staticmethod
    def read_file(merchant_acct, bucket, import_customer_file=None):
        
        if import_customer_file is None:
            import_customer_file = ImportCustomerFile.get(merchant_acct)
        rows = []
        
        if import_customer_file:
            
            logger.debug('file_storage_filename=%s', import_customer_file.file_storage_filename)
            file_path     = import_customer_file.file_storage_filename
            
            logger.debug('file_path=%s', file_path)
            
            blob = bucket.blob(file_path)
            
            content = blob.download_as_text()
            
            csv_file = io.StringIO(content)
            
            csv_reader = csv.DictReader(csv_file)
            
            
            
            for row in csv_reader:
                rows.append(row)
                
        
        return rows
    
    @staticmethod
    def define_account_settings(merchant_acct, registered_outlet=None, default_password='123456'): 
        import_customer_file = ImportCustomerFile.get(merchant_acct)   
        import_customer_file.import_settings['registered_outlet'] = registered_outlet
        import_customer_file.import_settings['default_password'] = default_password
        import_customer_file.put()
        
    @staticmethod
    def update_reward_program_settings(merchant_acct, reward_program_settings={}): 
        import_customer_file = ImportCustomerFile.get(merchant_acct)   
        import_customer_file.import_settings['reward_program_settings'] = reward_program_settings
        import_customer_file.put()
        
    @staticmethod
    def confirm_status(merchant_acct): 
        import_customer_file = ImportCustomerFile.get(merchant_acct)   
        return ConfirmedImportCustomerFile.create(import_customer_file)        
    
    @staticmethod
    def remove_file(import_customer_file, bucket):
        
        old_file_blob = bucket.get_blob(import_customer_file.file_storage_filename) 
        if old_file_blob:
            old_file_blob.delete()
            import_customer_file.delete()  
    

class ConfirmedImportCustomerFile(ImportCustomerFile):
    created_datetime            = ndb.DateTimeProperty(required=True, auto_now_add=True)
    imported_datetime           = ndb.DateTimeProperty(required=False)
    status                      = ndb.StringProperty(required=True, default=program_conf.IMPORT_STATUS_READY,  choices=set(program_conf.IMPORT_STATUS_SET))    
    
    @property
    def is_ready(self):
        return self.status == program_conf.IMPORT_STATUS_READY
        
    @staticmethod
    def create(import_customer_file):
        import_customer_file =  ConfirmedImportCustomerFile(
                                    merchant_acct           = import_customer_file.merchant_acct,
                                    file_public_url         = import_customer_file.file_public_url,
                                    file_storage_filename   = import_customer_file.file_storage_filename,
                                    import_settings         = import_customer_file.import_settings,
                                )
        import_customer_file.put()
        return import_customer_file
            
    def read_customer_data_rows(self, bucket):
        
        logger.debug('file_storage_filename=%s', self.file_storage_filename)
        file_path     = self.file_storage_filename
        
        logger.debug('file_path=%s', file_path)
        
        blob = bucket.blob(file_path)
        
        content = blob.download_as_text()
        
        csv_file = io.StringIO(content)
        
        csv_reader = csv.DictReader(csv_file)
        
        rows = []
        
        for row in csv_reader:
            rows.append(row)
                
        
        return rows
            
class ImportFailedCustomerData(BaseNModel, DictModel):
    merchant_acct               = ndb.KeyProperty(name="merchant_acct", kind=MerchantAcct)
    customer_data               = ndb.JsonProperty()
    failed_datetime             = ndb.DateTimeProperty(required=True, auto_now_add=True)
    
    dict_properties = ['customer_data', 'failed_datetime']
    
    @staticmethod
    def create(merchant_acct, customer_data):
        ImportFailedCustomerData(
                merchant_acct   = merchant_acct.create_ndb_key(),
                customer_data   = customer_data,
            ).put()
            
class ImportDuplicatedCustomerData(BaseNModel, DictModel):
    merchant_acct               = ndb.KeyProperty(name="merchant_acct", kind=MerchantAcct)
    customer_data               = ndb.JsonProperty()
    imported_datetime           = ndb.DateTimeProperty(required=True, auto_now_add=True)
    
    dict_properties = ['customer_data', 'failed_datetime']
    
    @staticmethod
    def create(merchant_acct, customer_data):
        ImportDuplicatedCustomerData(
                merchant_acct   = merchant_acct.create_ndb_key(),
                customer_data   = customer_data,
            ).put()            
