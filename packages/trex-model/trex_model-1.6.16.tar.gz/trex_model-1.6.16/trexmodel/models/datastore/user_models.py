'''
Created on 10 Apr 2020

@author: jacklok
'''
from google.cloud import ndb
from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel
from trexlib.utils.string_util import random_number, random_string,\
    is_empty, is_not_empty
from flask_login import UserMixin
import logging  
from trexlib.utils.security_util import generate_user_id, hash_password

from trexconf import conf as lib_conf
from trexconf import conf as model_conf, conf
from trexlib.utils.common.date_util import to_day_of_year
from datetime import datetime, timedelta
from trexmodel.conf import USER_STATUS_ANONYMOUS, ACCOUNT_LOCKED_IN_MINUTES

logger = logging.getLogger("model")
#logger = logging.getLogger("target_debug")

class UserMin(BaseNModel, DictModel, UserMixin):
    
    #system internal usage
    user_id                     = ndb.StringProperty(required=True)
    password                    = ndb.StringProperty(required=False)
    gravatar_url                = ndb.StringProperty(required=False)
    
    #---------------------------------------------------------------------------
    # User Personal Details
    #---------------------------------------------------------------------------
    name                        = ndb.StringProperty(required=False)
    reset_password_reminder     = ndb.BooleanProperty(required=False, default=False)
    
    created_datetime            = ndb.DateTimeProperty(required=False, auto_now_add=True)
    last_login_datetime         = ndb.DateTimeProperty(required=False)

    locked                      = ndb.BooleanProperty(required=False, default=False)
    lock_expiry_datetime        = ndb.DateTimeProperty(required=False)
    active                      = ndb.BooleanProperty(required=True, default=True) 
    try_count                   = ndb.IntegerProperty(required=False)
    demo_account                = ndb.BooleanProperty(required=False, default=False)
    deleted                     = ndb.BooleanProperty(required=False, default=False)
    signin_device_session       = ndb.JsonProperty()
    
    
    dict_properties             = ['user_id', 'name', 'email', 'signin_device_session', 'gravatar_url', 'active', 'locked', 'lock_expiry_datetime']
    
    @classmethod
    #@cache.memoize(timeout=60)
    def get_by_user_id(cls, user_id):
        logger.debug('UserMin.get_by_user_id: read from database')
        return cls.query(cls.user_id==user_id).get()
    
    def get_id(self):
        return self.user_id
    
    @property
    def is_super_user(self):
        return False
    
    @property
    def is_admin_user(self):
        return False
    
    @property
    def signin_device_id(self):
        if is_not_empty(self.signin_device_session):
            return self.signin_device_session.get('device_id')
    
    @property
    def signin_expiry_datetime(self):
        if is_not_empty(self.signin_device_session):
            expiry_datetime_str =  self.signin_device_session.get('expiry_datetime')
            if is_not_empty(expiry_datetime_str):
                return datetime.strptime(expiry_datetime_str, '%d-%m-%Y %H:%M:%S')
    
    def is_valid_password(self, checking_password):
        hashed_signin_password = hash_password(self.user_id, checking_password)
        
        logger.debug('is_valid_password: checking_password=%s', checking_password)
        logger.debug('is_valid_password: hashed_signin_password=%s', hashed_signin_password)
        logger.debug('is_valid_password: user password=%s', self.password)
        
        is_signin_password_valid = hashed_signin_password == self.password
        
        logger.debug('is_valid_password: is_signin_password_valid=%s', is_signin_password_valid)
        
        return is_signin_password_valid
    
    def set_reset_password_code(self, reset_password_code):
        self.reset_password_code = reset_password_code
        self.put()
    
    def change_password(self, new_password):
        hashed_new_password = hash_password(self.user_id, new_password)
        
        logger.debug('change_password: new_password=%s', new_password)
        logger.debug('change_password: hashed_new_password=%s', hashed_new_password)
        
        self.password = hashed_new_password 
        self.put()
        
    def request_to_delete(self):
        DeletedUser.create_from_user(self)    
        #self.delete()
        self.deleted = True
        self.put()
        
    def add_try_count(self):
        if self.try_count is None:
            self.try_count = 0
        
        self.try_count +=1
        if self.try_count>=5:
            self.locked = True
            self.try_count = 0
            self.lock_expiry_datetime = datetime.utcnow() + timedelta(minutes=int(ACCOUNT_LOCKED_IN_MINUTES))
        self.put()
    
    @property    
    def is_still_lock(self):
        if self.lock_expiry_datetime is not None and self.lock_expiry_datetime>datetime.utcnow():
            return True
        return False
    
    
class Role(BaseNModel):
    id              = ndb.StringProperty(required=True)
    name            = ndb.StringProperty(required=True)
    description     = ndb.TextProperty(required=False)


class UserBase(UserMin):
    #---------------------------------------------------------------------------
    # User System Generated fields
    #---------------------------------------------------------------------------
    reference_code              = ndb.StringProperty(required=True)
    referral_code               = ndb.StringProperty(required=True)
    
    #---------------------------------------------------------------------------
    # User Mutual Mandatory fields
    #---------------------------------------------------------------------------
    email                       = ndb.StringProperty(required=False)
    mobile_phone                = ndb.StringProperty(required=False)
    
    #---------------------------------------------------------------------------
    # User Personal Details
    #---------------------------------------------------------------------------
    birth_date                  = ndb.DateProperty(required=False, indexed=False) 
    birth_date_date_str         = ndb.StringProperty(required=False)
    birth_day_in_year           = ndb.IntegerProperty(required=False)
    gender                      = ndb.StringProperty(required=False, choices=set([
                                                                    model_conf.GENDER_MALE_CODE, 
                                                                    model_conf.GENDER_FEMALE_CODE,
                                                                    model_conf.GENDER_UNKNOWN_CODE
                                                                    ]))
    national_id                 = ndb.StringProperty(required=False, )
    
    #---------------------------------------------------------------------------
    # User Contact Details
    #---------------------------------------------------------------------------
    
    country                     = ndb.StringProperty(required=False, default=lib_conf.DEFAULT_COUNTRY_CODE)
    state                       = ndb.StringProperty(required=False)
    city                        = ndb.StringProperty(required=False, )
    postcode                    = ndb.StringProperty(required=False, )
    address                     = ndb.StringProperty(required=False, )
    
    is_test_account             = ndb.BooleanProperty(required=False, default=False)
    
    #---------------------------------------------------------------------------
    # User account activation required fields
    #---------------------------------------------------------------------------
    is_email_verified                   = ndb.BooleanProperty(required=False, default=False)
    is_mobile_phone_verified            = ndb.BooleanProperty(required=False, default=False)
    
    email_verified_datetime             = ndb.DateTimeProperty(required=False)
    mobile_phone_verified_datetime      = ndb.DateTimeProperty(required=False)
    
    email_vc                            = ndb.StringProperty(required=False)
    email_vc_expiry_datetime            = ndb.DateTimeProperty(required=False)
    
    mobile_phone_vc                     = ndb.StringProperty(required=False)
    mobile_phone_vc_expiry_datetime     = ndb.DateTimeProperty(required=False)
    
    modified_datetime                   = ndb.DateTimeProperty(required=True, auto_now=True)
    
    request_reset_password_datetime             = ndb.DateTimeProperty(required=False)
    request_reset_password_expiry_datetime      = ndb.DateTimeProperty(required=False)
    request_reset_password_token                = ndb.StringProperty(required=False)
    reset_password_updated_datetime             = ndb.DateTimeProperty(required=False)
    
    
    
    @property
    def age(self):
        if self.birth_date:
            from dateutil.relativedelta import relativedelta
            from datetime import date
            today   = date.today()
            __age   = relativedelta(today, self.birth_date)
            return __age.years
        else:
            return 0
    
    @classmethod
    def get_by_reference_code(cls, reference_code):
        return User.query(ndb.AND(User.reference_code==reference_code)).get()
    
    @classmethod
    def get_by_email(cls, email):
        return User.query(ndb.AND(User.email==email, User.deleted==False)).get()
    
    @classmethod
    def list_by_email(cls, email):
        return cls.query(ndb.AND(User.email==email)).fetch(limit=conf.MAX_FETCH_RECORD)
    
    @classmethod
    def get_by_mobile_phone(cls, mobile_phone):
        return User.query(ndb.AND(User.mobile_phone==mobile_phone, User.deleted==False)).get()
    
    @classmethod
    def get_by_referral_code(cls, referral_code):
        return User.query(ndb.AND(User.referral_code==referral_code)).get()
    
    @classmethod
    def get_by_reset_password_token(cls, request_reset_password_token):
        return User.query(ndb.AND(User.request_reset_password_token==request_reset_password_token)).get()
    
    @classmethod
    def count_all(cls):
        return cls.count(limit=conf.MAX_FETCH_RECORD)
    
    @classmethod
    def _generate_referral_code(cls):
        referral_code = random_string(8, is_human_mistake_safe=True)
        checking_user = cls.get_by_referral_code(referral_code)
        while checking_user is not None:
            referral_code = random_string(8, is_human_mistake_safe=True)
            checking_user = cls.get_by_referral_code(referral_code)
        return referral_code
    
    @classmethod
    def create(cls, name=None, email=None, mobile_phone=None, 
               gender=None, birth_date=None, 
               password=None, is_email_verified=True, 
               is_mobile_phone_verified=False, 
               reference_code=None, status=None
               ):
        
        user_id             = generate_user_id()
        if is_empty(reference_code):
            reference_code      = random_number(16)
        else:
            reference_code = reference_code.replace("-", "")
                 
        birth_date_date_str = None
        birth_day_in_year   = 0
        
        if birth_date:
            birth_date_date_str = birth_date.strftime('%d/%m')
            birth_day_in_year   = to_day_of_year(birth_date)
            
        if mobile_phone:
            mobile_phone = mobile_phone.replace(" ", "")    
        
        created_user = cls(user_id=user_id, name=name, email=email, mobile_phone=mobile_phone, 
                           gender=gender, birth_date=birth_date, birth_date_date_str=birth_date_date_str,  birth_day_in_year=birth_day_in_year,
                           reference_code=reference_code, status=status,
                           )
        
        hashed_password             = hash_password(user_id, password)
        created_user.password       = hashed_password
        created_user.referral_code  = cls._generate_referral_code()
        
        
        created_user.is_email_verified          = is_email_verified
        created_user.is_mobile_phone_verified   = is_mobile_phone_verified
        
        if is_email_verified==False:
            created_user.email_vc                               = random_number(6)
            created_user.email_vc_expiry_datetime               = datetime.utcnow() + timedelta(minutes=10)
        
        if is_mobile_phone_verified==False:
            created_user.mobile_phone_vc                        = random_number(6)
            created_user.mobile_phone_vc_expiry_datetime        = datetime.utcnow() + timedelta(minutes=10)
        
        created_user.put()
        
        return created_user
    
    @classmethod
    def update(cls, user_acct=None, **kwargs):
        logger.debug('**kwargs=%s', kwargs)
        
        mobile_phone    = kwargs.get('mobile_phone')
        password        = kwargs.get('password')
        #status          = kwargs.get('status')
        
        if mobile_phone:
            mobile_phone = mobile_phone.replace(" ", "")
        
        if is_empty(user_acct.referral_code):
            user_acct.referral_code = cls._generate_referral_code()
        
        kwargs['mobile_phone'] = mobile_phone
        
        for key, value in kwargs.items():
            setattr(user_acct, key, value)
        
        if password:
            hashed_password = hash_password(user_acct.user_id, password)
            user_acct.password = hashed_password
        
        user_acct.put()
        
        return user_acct
        
    
    @classmethod
    def update_contact(cls, user_acct, address=None, city=None, state=None, postcode=None, country=None):
        user_acct.address    = address
        user_acct.city       = city
        user_acct.state      = state
        user_acct.postcode   = postcode
        user_acct.country    = country
        user_acct.put()
        
    @classmethod
    def update_biodata(cls, user_acct, gender=None, birth_date=None):
        user_acct.gender        = gender
        user_acct.birth_date    = birth_date
        birth_day_in_year       = 0
        
        if birth_date:
            birth_date_date_str = birth_date.strftime('%d/%m')
            birth_day_in_year   = to_day_of_year(birth_date)
        
        user_acct.birth_date_date_str   = birth_date_date_str
        user_acct.birth_day_in_year     = birth_day_in_year
        
        user_acct.put() 
    
    def reset_password_request(self):
        self.request_reset_password_token = random_string(16)
        self.request_reset_password_datetime = datetime.utcnow()
        self.request_reset_password_expiry_datetime = self.request_reset_password_datetime + timedelta(minutes=5)
        self.put()
        
    def set_reset_password_token(self, request_reset_password_token):
        self.request_reset_password_token = request_reset_password_token
        self.request_reset_password_datetime = datetime.utcnow()
        self.request_reset_password_expiry_datetime = self.request_reset_password_datetime + timedelta(minutes=5)
        self.put()
        
    def reset_password(self, new_password):
        hashed_password = hash_password(self.user_id, new_password)
        self.password   = hashed_password
        self.try_count  = 0
        self.locked     = False
        self.reset_password_updated_datetime = datetime.utcnow()
        self.put()    
        
    def mark_email_verified(self):
        self.is_email_verified = True
        self.email_verified_datetime = datetime.now()
        self.put()
        
    def mark_mobile_phone_verified(self):
        self.is_mobile_phone_verified = True
        self.mobile_phone_verified_datetime = datetime.utcnow()
        self.put()    
    
    def reset_email_vc(self):
        self.email_vc = random_number(6)
        self.email_vc_expiry_datetime = datetime.utcnow() + timedelta(minutes=2)
        self.put() 
        
    def reset_mobile_phone_vc(self):
        self.mobile_phone_vc = random_number(6)
        #self.mobile_phone_vc_expiry_datetime = datetime.utcnow() + timedelta(minutes=10)
        self.mobile_phone_vc_expiry_datetime = datetime.utcnow() + timedelta(minutes=10)  
        self.put()   
        
class User(UserBase):
    redeem_pin                 = ndb.StringProperty(required=False)
    status                     = ndb.StringProperty(required=False, default=USER_STATUS_ANONYMOUS)
    new_message_count          = ndb.IntegerProperty(required=False, default=0)
    device_details             = ndb.JsonProperty()
    
    dict_properties            = [
                                    'mobile_phone', 'email', 'password', 'name', 'birth_date', 'gender',
                                    'reference_code', 'country', 'state', 'city', 'postcode', 
                                    'address', 'redeem_pin', 'new_message_count', 'status',
                                    'device_details', 'signin_device_session', 'referral_code',
                                    'last_login_datetime',
                                    ]

    #unique_attributes = 'email,username'

    audit_properties            = [
                                    'mobile_phone', 'email', 'password', 'name', 'birth_date', 'gender',
                                    'reference_code', 'country', 'state', 'city', 'postcode', 
                                    'address', 'redeem_pin', 'status', 'device_details', 

                                    ]

    unicode_properties = ['name', 'address', 'city']

    export_properties = (
        ('User Id','user_id'),
        ('Name','name'),
        ('Reference Code','reference_code'),
        ('Mobile Phone','mobile_phone'),
        ('Email','email'),
        ('Gender','gender'),
        ('Date of Birth','birth_date'),
        ('Country','country_desc'),
        ('State','state_desc'),
        ('City','city'),
        ('Address','address'),
        ('Registered Datetime','created_datetime'),

    )

    def __repr__(self):
        return '''
                User[key=%s, 
                name=%s, 
                email=%s, 
                mobile_phone=%s, 
                country=%s, 
                locked=%s,
                active=%s
                ]
                ''' % (self.key_in_str, self.name, self.email, self.mobile_phone, self.country, self.locked, self.active)

    
        
    @property
    def is_active(self):
        """Returns `True` if the user is active."""
        logger.info('calling is_active')
        return self.active
    
    def update_device_details(self, platform, device_token):
        if self.device_details:
            found_device_details_list_by_platform = self.device_details.get(platform)
            if found_device_details_list_by_platform:
                is_found = False
                for device_details_by_platform in  found_device_details_list_by_platform:
                    device_token_by_platform = device_details_by_platform.get('device_token')
                    logger.info('device_token_by_platform=%s', device_token_by_platform)
                    if device_token_by_platform:
                        device_details_by_platform['last_updated_datetime'] = datetime.utcnow().strftime("%d-%m-%Y %H:%M:%S")
                        is_found = True
                        break
                
                if is_found == False:
                    found_device_details_list_by_platform.append(
                                                                {
                                                                'device_token'              : device_token,
                                                                'last_updated_datetime'     : datetime.utcnow().strftime("%d-%m-%Y %H:%M:%S"),
                                                                }
                                                            )
                        
                else:
                    device_details_by_platform['device_token']          = device_token
                    device_details_by_platform['last_updated_datetime'] = datetime.utcnow().strftime("%d-%m-%Y %H:%M:%S"),
            else:
                self.device_details[platform] = [
                                                    {
                                                    'device_token'              : device_token,
                                                    'last_updated_datetime'     : datetime.utcnow().strftime("%d-%m-%Y %H:%M:%S"),
                                                    }
                                                ]
        else:
            self.device_details = {
                                    platform : [
                                                {
                                                    'device_token'              : device_token,
                                                    'last_updated_datetime'     : datetime.utcnow().strftime("%d-%m-%Y %H:%M:%S"),
                                                    }
                                                ]
                                }
        self.put()

class DeletedUser(User):
    deleted_datetime            = ndb.DateTimeProperty(required=False, auto_now_add=True)
    
    
    def __repr__(self):
        return '''
                DeletedUser[key=%s, 
                name=%s, 
                email=%s, 
                mobile_phone=%s, 
                country=%s, 
                locked=%s,
                deleted_datetime=%s
                ]
                ''' % (self.key_in_str, self.name, self.email, self.mobile_phone, self.country, self.locked, self.deleted_datetime)
                
    @property
    def is_active(self):
        return False
    
    @staticmethod
    def create_from_user(user):
        deleted_user = DeletedUser(
                        
                        user_id             = user.user_id,
                        name                = user.name,
                        email               = user.email,
                        mobile_phone        = user.mobile_phone,
                        gender              = user.gender,
                        country             = user.country,
                        birth_date          = user.birth_date, 
                        birth_date_date_str = user.birth_date_date_str,  
                        birth_day_in_year   = user.birth_day_in_year,
                        reference_code      = user.reference_code,
                        referral_code       = user.referral_code,
                        active              = False,
                        )
        
        
        '''
        for key, value in vars(user).items():
            setattr(deleted_user, key, value)
        '''
        deleted_user.put()
        
        logger.debug('deleted_user=%s', deleted_user)
      
class LoggedInUser(UserMixin, DictModel):
    
    def __init__(self, json_object, is_super_user=False, is_admin_user=False, is_merchant_user=False, country=lib_conf.DEFAULT_COUNTRY_CODE):
        
        logging.debug('json_object=%s', json_object)
        
        self.user_id            = json_object.get('user_id') 
        self.name               = json_object.get('name')
        self.email              = json_object.get('email')
        self.gravatar_url       = json_object.get('gravatar_url')
        self.active             = json_object.get('active')
        self.locked             = json_object.get('locked')
        self.permission         = json_object.get('permission')
        self.is_super_user      = json_object.get('is_super_user') or is_super_user
        self.is_admin_user      = json_object.get('is_admin_user') or is_admin_user
        self.is_merchant_user   = json_object.get('is_merchant_user') or is_merchant_user
        self.permission         = json_object.get('permission')
        self.country            = country
        
        self.show_key_in_dict   = False
        
        self.dict_properties     = ['user_id', 'name', 'gravatar_url', 'active', 'locked', 
                                    'is_super_user', 'is_admin_user', 'is_merchant_user', 'permission', 'country']
        
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_active(self):
        return self.active
    
    @property
    def is_anonymous(self):
        return False    

    
