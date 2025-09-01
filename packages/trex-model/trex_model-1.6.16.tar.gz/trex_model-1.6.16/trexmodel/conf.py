import os, config_path


INTERNAL_MAX_FETCH_RECORD                       = 9999
MAX_FETCH_RECORD_FULL_TEXT_SEARCH               = 1000
MAX_FETCH_RECORD_FULL_TEXT_SEARCH_PER_PAGE      = 10
MAX_FETCH_RECORD                                = 99999999
MAX_FETCH_IMAGE_RECORD                          = 100
MAX_CHAR_RANDOM_UUID4                           = 20
PAGINATION_SIZE                                 = 10
VISIBLE_PAGE_COUNT                              = 10

DEFAULT_GMT_HOURS                               = 8

GENDER_MALE_CODE                                = 'm'
GENDER_FEMALE_CODE                              = 'f'
GENDER_UNKNOWN_CODE                             = 'u'

APPLICATION_ACCOUNT_PROVIDER                    = 'app'

MODEL_PROJECT_ID                                = os.environ['GCLOUD_PROJECT_ID']

DATASTORE_SERVICE_ACCOUNT_KEY_FILEPATH          = os.environ['SERVICE_ACCOUNT_KEY']

ACCOUNT_LOCKED_IN_MINUTES                       = os.environ['ACCOUNT_LOCKED_IN_MINUTES']

DATASTORE_CREDENTIAL_PATH                       = os.path.abspath(os.path.dirname(config_path.__file__)) + '/' + DATASTORE_SERVICE_ACCOUNT_KEY_FILEPATH

MERCHANT_STAT_FIGURE_UPDATE_INTERVAL_IN_MINUTES = os.environ.get('MERCHANT_STAT_FIGURE_UPDATE_INTERVAL_IN_MINUTES') or 60

MESSAGE_CATEGORY_ANNOUNCEMENT           = 'announcement'
MESSAGE_CATEGORY_ALERT                  = 'alert'
MESSAGE_CATEGORY_PROMOTION              = 'promotion'
MESSAGE_CATEGORY_SURVEY                 = 'survey'
MESSAGE_CATEGORY_SYSTEM                 = 'system'
MESSAGE_CATEGORY_REWARD                 = 'reward'
MESSAGE_CATEGORY_REFERRAL               = 'referral'
MESSAGE_CATEGORY_BIRTHDAY               = 'birthday'
MESSAGE_CATEGORY_REDEEM                 = 'redeem'
MESSAGE_CATEGORY_PAYMENT                = 'payment'
MESSAGE_CATEGORY_REDEMPTION_CATALOGUE   = 'redemption_catalogue'

MESSAGE_CATEGORIES = (
                        MESSAGE_CATEGORY_ANNOUNCEMENT, 
                        MESSAGE_CATEGORY_ALERT, 
                        MESSAGE_CATEGORY_PROMOTION, 
                        MESSAGE_CATEGORY_SURVEY, 
                        MESSAGE_CATEGORY_SYSTEM, 
                        MESSAGE_CATEGORY_REWARD, 
                        MESSAGE_CATEGORY_REDEEM,
                        MESSAGE_CATEGORY_REDEMPTION_CATALOGUE,
                        MESSAGE_CATEGORY_PAYMENT,
                        )

MESSAGE_STATUS_NEW      = 'n'
MESSAGE_STATUS_READ     = 'r'

USER_STATUS_ANONYMOUS       = 'anonymous'
USER_STATUS_REGISTERED      = 'registered'
USER_STATUS_ENTER_BIODATA   = 'enterBiodata'
USER_STATUS_COMPLETED       = 'completedRegistration'

USER_STATUS_SET = (USER_STATUS_REGISTERED, USER_STATUS_ENTER_BIODATA, USER_STATUS_COMPLETED)


MESSAGE_STATUS_SET      = (MESSAGE_STATUS_NEW, MESSAGE_STATUS_READ)

PREPAID_REDEEM_URL          = os.environ['PREPAID_REDEEM_URL']

