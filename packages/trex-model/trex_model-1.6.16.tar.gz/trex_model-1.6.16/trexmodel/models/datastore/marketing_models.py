'''
Created on 8 Jan 2024

@author: jacklok
'''
from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel
from google.cloud import ndb
from trexmodel.models.datastore.merchant_models import MerchantUser,\
    MerchantAcct
from trexlib.utils.string_util import is_not_empty, random_string
from datetime import datetime
from trexconf import conf, program_conf
import trexmodel.conf as model_conf
import logging
from _datetime import timedelta
from trexconf.program_conf import MERCHANT_NEWS_STATUS_PUBLISH
from trexconf.conf import MERCHANT_NEWS_BASE_URL
from trexlib.utils.common.common_util import sort_list

logger = logging.getLogger('model')

class PushNotificationSetup(BaseNModel, DictModel):
    '''
    Merchant Acct as ancestor
    
    '''
    
    title                   = ndb.StringProperty(required=True)
    desc                    = ndb.StringProperty(required=True)
    send_mode               = ndb.StringProperty(required=True, default="send_now", choices=set(['send_now','send_schedule']))
    schedule_datetime       = ndb.DateTimeProperty(required=False)
    
    content_settings        = ndb.JsonProperty()
    
    is_archived             = ndb.BooleanProperty(required=True)
    
    created_datetime        = ndb.DateTimeProperty(required=True, auto_now_add=True)
    archived_datetime       = ndb.DateTimeProperty(required=False)
    
    created_by              = ndb.KeyProperty(name="created_by", kind=MerchantUser)
    created_by_username     = ndb.StringProperty(required=False)
    
    archived_by             = ndb.KeyProperty(name="created_by", kind=MerchantUser)
    archived_by_username    = ndb.StringProperty(required=False)
    
    send                    = ndb.BooleanProperty(required=True, default=False)
    sent_datetime           = ndb.DateTimeProperty(required=False)
    
    dict_properties = [
                        'title', 'desc', 'send_mode', 'schedule_datetime', 
                        'content_type', 'content_value', 'content_settings', 
                        'created_datetime', 'send', 'sent_datetime',
                    ]
    
    @property
    def merchant_acct_entity(self):
        return MerchantAcct.fetch(self.key.parent().urlsafe())
    
    @property
    def content_type(self):
        if self.content_settings:
            return self.content_settings.get('content_type')
    
    @property
    def content_value(self):
        if self.content_settings:
            return self.content_settings.get('content_value')
        
    @property
    def image_url(self):
        if self.content_settings:
            if self.content_settings.get('content_type')=='image':
                return self.content_settings.get('content_value')
            
    @property
    def text_data(self):
        if self.content_settings:
            if self.content_settings.get('content_type')=='text':
                return self.content_settings.get('content_value')
            
    @property
    def action_link(self):
        if self.content_settings:
            if self.content_settings.get('content_type')=='action_link':
                return self.content_settings.get('content_value')                    
            
    @staticmethod
    def create(merchant_acct, title=None, desc=None, send_mode=None, schedule_datetime=None, content_settings={},
               created_by=None):
        
        created_by_username = None
        if is_not_empty(created_by):
            if isinstance(created_by, MerchantUser):
                created_by_username = created_by.username
        
                
        push_notification_setup = PushNotificationSetup(
                                                parent                  = merchant_acct.create_ndb_key(),
                                                title                   = title,
                                                desc                    = desc,
                                                send_mode               = send_mode,
                                                schedule_datetime       = schedule_datetime,
                                                content_settings        = content_settings,
                                                is_archived             = False,
                                                created_by              = created_by.create_ndb_key(),
                                                created_by_username     = created_by_username,
                                                )
        push_notification_setup.put()
        
        return push_notification_setup
    
    
    def to_configuration(self):
        return {
                
                }
    
    def archived(self, archived_by=None):
        
        archived_by_username = None
        if is_not_empty(archived_by):
            if isinstance(archived_by, MerchantUser):
                archived_by_username = archived_by.username
        
        self.is_archived                = True
        self.archived_datetime          = datetime.utcnow()
        self.archived_by                = archived_by.create_ndb_key()
        self.archived_by_username       = archived_by_username
        self.put()
        
    def update_as_send(self):
        self.send = True
        self.sent_datetime = datetime.utcnow()
        self.put()
        
    @staticmethod
    def list_by_merchant_acct(merchant_acct):
        return PushNotificationSetup.query(ndb.AND(PushNotificationSetup.is_archived!=True), ancestor=merchant_acct.create_ndb_key()).fetch(limit=model_conf.MAX_FETCH_RECORD)
    
    @staticmethod
    def list_archived_by_merchant_acct(merchant_acct):
        return PushNotificationSetup.query(ndb.AND(PushNotificationSetup.is_archived==True), ancestor=merchant_acct.create_ndb_key()).fetch(limit=model_conf.MAX_FETCH_RECORD)
    
    @staticmethod
    def list(start_datetime=datetime.utcnow(), end_datetime=datetime.utcnow(), send=False):
        if send==False:
            result = PushNotificationSetup.query(
                    ndb.AND(
                            PushNotificationSetup.send==False, 
                            PushNotificationSetup.schedule_datetime>start_datetime,
                            PushNotificationSetup.schedule_datetime<=end_datetime,
                            )
                    ).fetch(offset=0, limit=conf.MAX_FETCH_RECORD)
        else:
            result = PushNotificationSetup.query(
                    ndb.AND(
                            PushNotificationSetup.schedule_datetime>start_datetime,
                            PushNotificationSetup.schedule_datetime<=end_datetime,
                            )
                    ).fetch(offset=0, limit=conf.MAX_FETCH_RECORD)
        return result
    
    @staticmethod
    def cound(start_datetime=datetime.utcnow(), end_datetime=datetime.utcnow(), send=False):
        if send==False:
            result = PushNotificationSetup.query(
                    ndb.AND(
                            PushNotificationSetup.send==False, 
                            PushNotificationSetup.schedule_datetime>start_datetime,
                            PushNotificationSetup.schedule_datetime<=end_datetime,
                            )
                    ).fetch(offset=0, limit=conf.MAX_FETCH_RECORD)
        else:
            result = PushNotificationSetup.query(
                    ndb.AND(
                            PushNotificationSetup.schedule_datetime>start_datetime,
                            PushNotificationSetup.schedule_datetime<=end_datetime,
                            )
                    ).fetch(offset=0, limit=conf.MAX_FETCH_RECORD)
        return result
    
class MarketingImage(BaseNModel, DictModel):
    '''
    Merchant Account as ancestor
    '''
    image_label                     = ndb.StringProperty(required=True)
    image_file_type                 = ndb.StringProperty(required=True)
    image_file_public_url           = ndb.StringProperty(required=True)
    image_file_storage_filename     = ndb.StringProperty(required=True)
    created_datetime                = ndb.DateTimeProperty(required=False, auto_now=True, default=datetime.min)
    
    dict_properties = ['image_label', 'image_file_public_url', 'image_file_storage_filename', 'image_file_type']
    
    @staticmethod
    def list_by_merchant_acct(merchant_acct):
        result = MarketingImage.query(ancestor=merchant_acct.create_ndb_key()).fetch(limit=conf.MAX_FETCH_RECORD)
        sorted_result = sort_list(result,'created_datetime', reverse_order=True, default_value=datetime.min)
        return sorted_result
    
    @staticmethod
    def upload_file(uploading_file, image_label, merchant_acct, bucket, image_file_type=None):
        file_prefix                         = random_string(8)
        image_file_storage_filename         = 'merchant/'+merchant_acct.key_in_str+'/marketing/'+file_prefix+'-'+uploading_file.filename
        blob                                = bucket.blob(image_file_storage_filename)
        
        logger.debug('image_label=%s', image_label)
        logger.debug('image_file_storage_filename=%s', image_file_storage_filename)
        
        blob.upload_from_string(
                uploading_file.read(),
                content_type=uploading_file.content_type
            )
        
        uploaded_url        = blob.public_url
        
        logger.debug('image_file_type=%s', image_file_type)
        
        image_file = MarketingImage(
                            parent                              = merchant_acct.create_ndb_key(),
                            image_label                         = image_label,
                            image_file_public_url               = uploaded_url,
                            image_file_storage_filename         = image_file_storage_filename,
                            image_file_type                     = image_file_type,
                            )
        
        image_file.put()
        
        return image_file
    
    @staticmethod
    def create_upload_file(image_label, image_file_storage_filename, public_url, merchant_acct, image_file_type=None):
        logger.debug('image_file_type=%s', image_file_type)
        
        image_file = MarketingImage(
                            parent                              = merchant_acct.create_ndb_key(),
                            image_label                         = image_label,
                            image_file_public_url               = public_url,
                            image_file_storage_filename         = image_file_storage_filename,
                            image_file_type                     = image_file_type,
                            )
        
        image_file.put()
        
        return image_file
    
    @staticmethod
    def remove_file(image_file, bucket):
        
        old_logo_blob = bucket.get_blob(image_file.image_file_storage_filename) 
        if old_logo_blob:
            old_logo_blob.delete()
            image_file.delete()      

class ScheduledPushNotificationHistory(BaseNModel, DictModel):
    push_notification_setup = ndb.KeyProperty(name="push_notification_setup", kind=PushNotificationSetup)
    created_datetime        = ndb.DateTimeProperty(required=True, auto_now_add=True)
    send                    = ndb.BooleanProperty(required=True, default=False)
    scheduled_datetime      = ndb.DateTimeProperty(required=True)
    sent_datetime           = ndb.DateTimeProperty(required=False)    

    @staticmethod
    def create(push_notification_setup, scheduled_datetime=None):
        if scheduled_datetime is None:
            scheduled_datetime = datetime.utcnow()
        ScheduledPushNotificationHistory(
                                    push_notification_setup = push_notification_setup.create_ndb_key(),
                                    scheduled_datetime      = scheduled_datetime,
                                    ).put()
                                    
    
    @staticmethod
    def list(scheduled_datetime=datetime.utcnow(), send=False):
        if send==False:
            result = ScheduledPushNotificationHistory.query(
                    ndb.AND(
                            ScheduledPushNotificationHistory.send==False, 
                            ScheduledPushNotificationHistory.scheduled_datetime<=scheduled_datetime)).fetch(offset=0, limit=conf.MAX_FETCH_RECORD)
        else:
            result = ScheduledPushNotificationHistory.query(
                    ndb.AND(
                            ScheduledPushNotificationHistory.scheduled_datetime<=scheduled_datetime)).fetch(offset=0, limit=conf.MAX_FETCH_RECORD)
        return result
    
    @staticmethod
    def count(scheduled_datetime=datetime.utcnow(), send=False):
        if send==False:
            return ScheduledPushNotificationHistory.query(
                    ndb.AND(
                            ScheduledPushNotificationHistory.send==False, 
                            ScheduledPushNotificationHistory.scheduled_datetime<=scheduled_datetime)).count(limit=conf.MAX_FETCH_RECORD)
        else:
            return ScheduledPushNotificationHistory.query(
                    ndb.AND(
                            ScheduledPushNotificationHistory.scheduled_datetime<=scheduled_datetime)).count(limit=conf.MAX_FETCH_RECORD)
            
class MerchantNewsFile(BaseNModel, DictModel):
    '''
    Merchant Account as ancestor
    '''
    label                         = ndb.StringProperty(required=True)
    desc                          = ndb.StringProperty(required=False)
    news_text                     = ndb.StringProperty(required=False)
    
    news_file_type                = ndb.StringProperty(required=False)
    news_file_public_url          = ndb.StringProperty(required=False)
    news_file_storage_filename    = ndb.StringProperty(required=False)
    
    completed_status                = ndb.StringProperty(required=True, choices=set(program_conf.MERCHANT_NEWS_STATUS))
    
    start_date                    = ndb.DateProperty(required=True)
    end_date                      = ndb.DateProperty(required=True)
    
    enabled                       = ndb.BooleanProperty(default=True)
    
    is_archived                   = ndb.BooleanProperty(default=False)
    
    created_datetime        = ndb.DateTimeProperty(required=True, auto_now_add=True)
    modified_datetime       = ndb.DateTimeProperty(required=False)
    published_datetime      = ndb.DateTimeProperty(required=False)
    archived_datetime       = ndb.DateTimeProperty(required=False)
    
    created_by              = ndb.KeyProperty(name="created_by", kind=MerchantUser)
    created_by_username     = ndb.StringProperty(required=False)
    
    modified_by              = ndb.KeyProperty(name="modified_by", kind=MerchantUser)
    modified_by_username     = ndb.StringProperty(required=False)
    
    published_by            = ndb.KeyProperty(name="published_by", kind=MerchantUser)
    published_by_username   = ndb.StringProperty(required=False)
    
    archived_by             = ndb.KeyProperty(name="archived_by", kind=MerchantUser)
    archived_by_username    = ndb.StringProperty(required=False)
    
    
    dict_properties = ['image_url', 'completed_progress_in_percentage','is_published', 'is_enabled',
                       'label', 'desc', 'news_text', 'start_date', 'end_date', 'enabled', 'is_archived',
                       'news_public_url', 
                       'completed_status']
    
    @property
    def merchant_acct(self):
        return MerchantAcct.fetch(self.key.parent().urlsafe())
    
    @property
    def image_url(self):
        if self.news_file_public_url:
            return self.news_file_public_url
        else:
            return conf.MERCHANT_NEWS_DEFAULT_IMAGE
        
    @property
    def news_public_url(self):
        return '%s/merchant/marketing/news/%s/show' % (MERCHANT_NEWS_BASE_URL, self.key_in_str)
    
    @property
    def completed_progress_in_percentage(self):
        
        return program_conf.merchant_news_completed_progress_percentage(self.completed_status)
    
    @property
    def is_published(self):
        return self.completed_status == MERCHANT_NEWS_STATUS_PUBLISH
    
    @property
    def is_enabled(self):
        return self.enabled
    
    @staticmethod
    def list_by_merchant_acct(merchant_acct):
        result = MerchantNewsFile.query(ndb.AND(MerchantNewsFile.is_archived==False), ancestor=merchant_acct.create_ndb_key()).fetch(limit=conf.MAX_FETCH_RECORD)
        return result
    
    @staticmethod
    def list_archived_by_merchant_acct(merchant_acct):
        return MerchantNewsFile.query(ndb.AND(MerchantNewsFile.is_archived==True), ancestor=merchant_acct.create_ndb_key()).fetch(limit=model_conf.MAX_FETCH_RECORD)
    
    @staticmethod
    def create(merchant_acct, label=None, desc=None, news_text=None, 
               start_date=None, end_date=None, created_by=None):
        
        created_by_username = None
        if is_not_empty(created_by):
            if isinstance(created_by, MerchantUser):
                created_by_username = created_by.username
                
        news_file = MerchantNewsFile(
                            parent                  = merchant_acct.create_ndb_key(),
                            label                   = label,
                            desc                    = desc,
                            news_text               = news_text,
                            start_date              = start_date,
                            end_date                = end_date,
                            created_by              = created_by.create_ndb_key(),
                            created_by_username     = created_by_username,
                            created_datetime        = datetime.utcnow(),
                            completed_status        = program_conf.MERCHANT_NEWS_STATUS_BASE,
                            )
        
        news_file.put()
        
        return news_file
    
    @staticmethod
    def update(merchant_news, label=None, desc=None, news_text=None, 
               start_date=None, end_date=None, modified_by=None):
        
        modified_by_username = None
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
                
        merchant_news.label                 = label
        merchant_news.desc                  = desc
        merchant_news.news_text             = news_text
        merchant_news.start_date            = start_date
        merchant_news.end_date              = end_date
        merchant_news.completed_status      = program_conf.MERCHANT_NEWS_STATUS_BASE
        merchant_news.modified_by           = modified_by.create_ndb_key()
        merchant_news.modified_by_username  = modified_by_username
        merchant_news.modified_datetime     = datetime.utcnow()
        
        
        merchant_news.put()
    
    @staticmethod
    def upload_file(merchant_news, uploading_file, merchant_acct, bucket, news_file_type=None):
        file_prefix                         = random_string(8)
        news_file_storage_filename          = 'merchant/'+merchant_acct.key_in_str+'/news/'+file_prefix+'-'+uploading_file.filename
        blob                                = bucket.blob(news_file_storage_filename)
        
        logger.debug('news_file_storage_filename=%s', news_file_storage_filename)
        
        blob.upload_from_string(
                uploading_file.read(),
                content_type=uploading_file.content_type
            )
        
        uploaded_url        = blob.public_url
        
        logger.debug('uploaded_url=%s', uploaded_url)
        logger.debug('news_file_type=%s', news_file_type)
        
        if is_not_empty(merchant_news.news_file_storage_filename):
            old_logo_blob = bucket.get_blob(merchant_news.news_file_storage_filename)
            if old_logo_blob:
                old_logo_blob.delete()
            
        
        merchant_news.news_file_public_url          = uploaded_url
        merchant_news.news_file_storage_filename    = news_file_storage_filename
        merchant_news.news_file_type                = news_file_type
        
        
        merchant_news.put()
        
        return merchant_news
    
    @staticmethod
    def update_news_material_uploaded(merchant_news, modified_by=None):
        
        modified_by_username = None
        
        if is_not_empty(modified_by):
            if isinstance(modified_by, MerchantUser):
                modified_by_username = modified_by.username
        
        merchant_news.completed_status          = program_conf.MERCHANT_NEWS_STATUS_UPLOAD_MATERIAL
        merchant_news.modified_by               = modified_by.create_ndb_key()
        merchant_news.modified_by_username      = modified_by_username
        merchant_news.modified_datetime         = datetime.utcnow()
        
        merchant_news.put()
        
        return merchant_news
    
    @staticmethod
    def remove_file(news_file, bucket):
        
        old_logo_blob = bucket.get_blob(news_file.news_file_storage_filename) 
        if old_logo_blob:
            old_logo_blob.delete()
            news_file.delete()    
            
    def archived(self, archived_by=None):
        
        archived_by_username = None
        if is_not_empty(archived_by):
            if isinstance(archived_by, MerchantUser):
                archived_by_username = archived_by.username
        
        self.is_archived                = True
        self.archived_datetime          = datetime.utcnow()
        self.archived_by                = archived_by.create_ndb_key()
        self.archived_by_username       = archived_by_username
        self.put()
        
        merchant_acct = self.merchant_acct
        merchant_acct.remove_merchant_news(self.key_in_str)
    
    def to_configuration(self):
        return {
                'merchant_news_key'     : self.key_in_str,
                'image_url'             : self.image_url,
                'label'                 : self.label,
                'content'               : self.news_text,
                'start_datetime'        : self.start_date.strftime('%d-%m-%Y %H:%M:%S'),
                'end_datetime'          : self.end_date.strftime('%d-%m-%Y %H:%M:%S'),
                'news_public_url'       : self.news_public_url,
                }
        
    def publish(self, published_by=None):
        
        published_by_username = None
        if is_not_empty(published_by):
            if isinstance(published_by, MerchantUser):
                published_by_username = published_by.username
        
        self.completed_status           = program_conf.MERCHANT_NEWS_STATUS_PUBLISH
        self.published_by               = published_by.create_ndb_key()
        self.published_by_username      = published_by_username
        self.published_datetime         = datetime.utcnow()
        self.put()    
        
        merchant_acct = self.merchant_acct
        merchant_acct.add_merchant_news(self.to_configuration())
        
    @staticmethod
    def disable_news(merchant_news):
        merchant_news.enabled = False
        merchant_news.put()
        
        merchant_acct = merchant_news.merchant_acct
        merchant_acct.remove_merchant_news(merchant_news.key_in_str)
        
        
    @staticmethod
    def enable_news(merchant_news):
        merchant_news.enabled = True
        merchant_news.put()
        
        merchant_acct = merchant_news.merchant_acct
        merchant_acct.add_merchant_news(merchant_news.to_configuration())        