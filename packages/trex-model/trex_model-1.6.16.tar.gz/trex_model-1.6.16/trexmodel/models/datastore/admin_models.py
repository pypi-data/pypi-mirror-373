'''
Created on 8 May 2020

@author: jacklok
'''
from google.cloud import ndb
from trexmodel.models.datastore.user_models import UserMin
from trexlib.utils.security_util import generate_user_id, hash_password
from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel
from trexlib.utils.string_util import random_string
from trexlib.utils.common.common_util import logger
from trexconf import conf


class SuperUser(UserMin):
    email                           = ndb.StringProperty(required=False)
    created_datetime                = ndb.DateTimeProperty(required=False, auto_now_add=True)
    
    dict_properties         = ['user_id', 'name', 'email', 'gravatar_url', 'active', 'locked', 
                               'is_super_user', 'is_admin_user', 'is_merchant_user', 'created_datetime']
    
    @property
    def is_super_user(self):
        return True
    
    @property
    def is_admin_user(self):
        return False
    
    @property
    def is_merchant_user(self):
        return False
    
    @classmethod
    def new_super_user_id(cls):
        return 'superuser'
    
    @classmethod
    def create(cls, name=None, email=None, password=None, active=False):
        
        user_id = cls.new_super_user_id()
        created_user = cls(user_id=user_id, name=name, email=email, active=active)
        
        hashed_password         = hash_password(user_id, password)
        created_user.password   = hashed_password
            
        created_user.put()
        return created_user
    
    @classmethod
    def list(cls, offset=0, limit=10):
        return cls.query().order(-cls.joined_date).fetch(offset=offset, limit=limit)
    
    @classmethod
    def get_by_email(cls, email):
        return cls.query(ndb.AND(cls.email==email)).get()
    
class AdminUser(SuperUser):
    permission              = ndb.JsonProperty()
    is_superuser            = ndb.BooleanProperty(required=True, default=False)
    dict_properties         = ['user_id', 'name', 'email', 'gravatar_url', 'active', 'locked', 
                               'permission', 'is_superuser', 'is_super_user', 'is_admin_user', 'is_merchant_user', 'created_datetime']
    
    @classmethod
    def new_super_user_id(cls):
        return generate_user_id()
    
    @property
    def is_super_user(self):
        return self.is_superuser
    
    @property
    def is_admin_user(self):
        return True
    
    @property
    def is_merchant_user(self):
        return False
    
    @staticmethod
    def update_permission(admin_user, permission, is_superuser=False):
        admin_user.is_superuser = is_superuser
        admin_user.permission = {'granted_access': permission}
        admin_user.put()
        
class AppBannerFile(BaseNModel, DictModel):
    banner_file_type                = ndb.StringProperty(required=True)
    banner_file_public_url          = ndb.StringProperty(required=True)
    banner_file_storage_filename    = ndb.StringProperty(required=True)
    sequence                        = ndb.IntegerProperty(required=False, default=0)
    
    dict_properties = ['banner_file_public_url', 'banner_file_storage_filename', 'banner_file_type', 'sequence']
    
    @staticmethod
    def list():
        result = AppBannerFile.query().fetch(limit=conf.MAX_FETCH_RECORD)
        return result
    
    @staticmethod
    def upload_file(uploading_file, bucket, banner_file_type=None):
        file_prefix                         = random_string(8)
        banner_file_storage_filename       = 'app/banner/'+file_prefix+'-'+uploading_file.filename
        blob                                = bucket.blob(banner_file_storage_filename)
        
        logger.debug('banner_file_storage_filename=%s', banner_file_storage_filename)
        
        blob.upload_from_string(
                uploading_file.read(),
                content_type=uploading_file.content_type
            )
        
        uploaded_url        = blob.public_url
        
        logger.debug('banner_file_type=%s', uploaded_url)
        logger.debug('product_file_type=%s', banner_file_type)
        
        count = AppBannerFile.query().count()
        
        banner_file = AppBannerFile(
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

