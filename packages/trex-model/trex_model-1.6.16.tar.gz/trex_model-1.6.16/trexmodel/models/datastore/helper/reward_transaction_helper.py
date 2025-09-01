'''
Created on 20 Apr 2021

@author: jacklok
'''
from trexlib.utils.google.cloud_tasks_util import create_task
from trexconf import conf
from trexconf.conf import CHECK_CUSTOMER_ENTITLE_REWARD_TASK_URL, SYSTEM_TASK_SERVICE_CREDENTIAL_PATH, SYSTEM_TASK_GCLOUD_PROJECT_ID, SYSTEM_TASK_GCLOUD_LOCATION, SYSTEM_TASK_SERVICE_ACCOUNT_EMAIL  
import logging
from trexprogram.reward_program.reward_program_factory import RewardProgramFactory
from trexmodel.models.datastore.reward_models import CustomerPointReward,\
    CustomerStampReward, CustomerEntitledVoucher, VoucherRewardDetailsForUpstreamData,\
    CustomerEntitledTierRewardSummary
from datetime import datetime
from trexmodel import program_conf
from trexmodel.models.datastore.customer_model_helpers import update_customer_entiteld_voucher_summary_after_reverted_voucher,\
    update_reward_summary_with_new_reward,\
    update_prepaid_summary_with_new_prepaid,\
    update_customer_entiteld_voucher_summary_with_customer_new_voucher,\
    update_prepaid_summary_with_reverted_prepaid,\
    update_reward_summary_with_reverted_reward
from trexanalytics.bigquery_upstream_data_config import create_merchant_customer_transaction_upstream_for_merchant,\
    create_merchant_customer_redemption_upstream_for_merchant,\
    create_merchant_customer_prepaid_upstream_for_merchant,\
    create_merchant_customer_redemption_reverted_upstream_for_merchant,\
    create_revert_entitled_customer_voucher_upstream_for_merchant,\
    create_redeemed_customer_voucher_to_upstream_for_merchant,\
    create_merchant_sales_transaction_upstream_for_merchant,\
    create_merchant_customer_reward_upstream_for_merchant
from trexmodel.models.datastore.membership_models import MerchantTierMembership
from trexmodel.models.datastore.transaction_models import CustomerTransaction,\
    SalesTransaction
from trexmodel.models.datastore.model_decorators import model_transactional
from trexmodel.models.datastore.prepaid_models import CustomerPrepaidReward
from trexprogram.reward_program.reward_program_base import EntitledVoucherSummary
from trexmodel.models.datastore.customer_models import Customer,\
    CustomerMembership, CustomerTierMembership
from trexmodel.models.datastore.redeem_models import CustomerRedemption
from trexlib.utils.string_util import is_not_empty
from trexlib.utils.log_util import get_tracelog
from trexmodel.models.datastore.lucky_draw_models import LuckyDrawTicket
from trexmodel.models.datastore.message_model_helper import create_transaction_message,\
    create_redemption_message, create_payment_message
from trexmodel.models.datastore.helper.reward_model_helpers import list_merchant_birthday_program_configuration
from dateutil.relativedelta import relativedelta
from trexmodel.utils.model.model_util import create_db_client

logger = logging.getLogger('helper')
#logger = logging.getLogger('debug')


@model_transactional(desc='check_user_joined_merchant_birthday_reward')
def check_user_joined_merchant_birthday_reward(user_acct):
    user_this_year_birth_date   = None
    transact_datetime           = datetime.utcnow()
    current_year                = transact_datetime.year
    #today                       = transact_datetime.today()
    
    if user_acct.birth_date is not None:
        user_this_year_birth_date   = datetime(year=current_year, month=user_acct.birth_date.month, day=user_acct.birth_date.day)
    
    logger.debug('user_this_year_birth_date=%s', user_this_year_birth_date)
    
    if user_this_year_birth_date:
        
        customer_acct_list          = Customer.list_by_user_account(user_acct)
        
        
        for customer_acct in customer_acct_list:
            merchant_acct = customer_acct.registered_merchant_acct
            birthday_program_configurations_list = list_merchant_birthday_program_configuration(merchant_acct)
            
            logger.debug('merchant_acct(%s) birthday_program_configurations_list=%s', merchant_acct.brand_name, birthday_program_configurations_list)
            
            for program_configuration in birthday_program_configurations_list:
                 
                #program_start_date  = datetime.strptime(program_configuration.get('start_date'), '%d-%m-%Y')
                #program_end_date    = datetime.strptime(program_configuration.get('end_date'), '%d-%m-%Y')
                
                #is_program_still_valid = today>=program_start_date and today<=program_end_date
                
                #logger.debug('program(%s) is_program_still_valid=%s', program_configuration.get('label'), is_program_still_valid)
                
                #if is_program_still_valid:
                
                is_dob_match = _is_user_dob_match_program(user_this_year_birth_date, transact_datetime, program_configuration)
                
                logger.debug('program(%s) is_dob_match=%s', program_configuration.get('label'), is_dob_match)
                
                if is_dob_match:
                    _giveaway_birthday_reward_to_customer(
                        customer_acct, program_configuration, transact_datetime, merchant_acct, is_test_account=user_acct.is_test_account)
            

def _is_user_dob_match_program(user_this_year_birth_date, transact_datetime, program_configuration):
    program_settings            = program_configuration.get('program_settings')
    giveaway_when               = program_settings.get('scheme').get('giveaway_when')
    advance_in_day              = program_settings.get('scheme').get('advance_in_day',0)
    today                       = transact_datetime.today()
    
    logger.debug('giveaway_when=%s', giveaway_when)
     
    if  giveaway_when == program_conf.ADVANCE_IN_DAY:
        date_range_start    = user_this_year_birth_date-relativedelta(days=int(advance_in_day))
        
        logger.debug('date_range_start=%s', date_range_start)
        
        if today>=date_range_start and today<=user_this_year_birth_date:
            return True
        
        
    elif  giveaway_when == program_conf.FIRST_DAY_OF_MONTH:
        if transact_datetime.month == user_this_year_birth_date.month:
            return True
    
    return False

@model_transactional(desc='check_for_customer_birthday_reward')
def check_for_customer_birthday_reward(customer_acct):
    
    transact_datetime = datetime.utcnow()
    user_acct = customer_acct.registered_user_acct
    merchant_acct = customer_acct.merchant_acct_entity
    birthday_program_configurations_list = list_merchant_birthday_program_configuration(merchant_acct)
    
    logger.debug('merchant_acct(%s) birthday_program_configurations_list=%s', merchant_acct.brand_name, birthday_program_configurations_list)
    
    for program_configuration in birthday_program_configurations_list:
        _giveaway_birthday_reward_to_customer(
            customer_acct, program_configuration, transact_datetime, merchant_acct, is_test_account=user_acct.is_test_account)
        


def create_sales_transaction(transact_outlet=None, sales_amount=.0, tax_amount=.0, invoice_id=None, remarks=None, 
                            transact_by=None, transact_datetime=None, invoice_details=None, promotion_code=None):
    
    logger.debug('---create_sales_transaction---')
    
    logger.debug('invoice_details=%s', invoice_details)
    
    @model_transactional(desc='create_sales_transaction')
    def __start_transaction_for_sales_transaction(): 
        sales_transaction = SalesTransaction.create(
                                       transact_outlet      = transact_outlet,
                                       
                                       transact_amount      = sales_amount, 
                                       tax_amount           = tax_amount,
                                       
                                       invoice_id           = invoice_id, 
                                       remarks              = remarks,
                                       
                                       transact_by          = transact_by,
                                       
                                       transact_datetime    = transact_datetime,
                                       
                                       )
            
        create_merchant_sales_transaction_upstream_for_merchant(sales_transaction,)
        
        return sales_transaction
        
    return __start_transaction_for_sales_transaction()

def create_reward_transaction(customer, transact_outlet=None, sales_amount=.0, tax_amount=.0, invoice_id=None, remarks=None, 
                            transact_by=None, transact_datetime=None, invoice_details=None, promotion_code=None):
    
    logger.debug('---create_reward_transaction---')
    
    logger.debug('invoice_details=%s', invoice_details)
    
    @model_transactional(desc='create_reward_transaction')
    def __start_transaction_for_customer_transaction():
        
        sales_transaction = SalesTransaction.create(
                                       transact_outlet      = transact_outlet,
                                       
                                       transact_amount      = sales_amount, 
                                       tax_amount           = tax_amount,
                                       
                                       invoice_id           = invoice_id, 
                                       remarks              = remarks,
                                       
                                       transact_by          = transact_by,
                                       
                                       transact_datetime    = transact_datetime,
                                       
                                       )
        create_merchant_sales_transaction_upstream_for_merchant(sales_transaction)
        
        #customer_transaction = give_reward_from_sales_transaction(customer, sales_transaction)
        
        customer_transaction = CustomerTransaction.create_system_transaction(
                                       customer, 
                                       transact_outlet      = transact_outlet,
                                       
                                       transact_amount      = sales_amount, 
                                       tax_amount           = tax_amount,
                                       
                                       invoice_id           = invoice_id, 
                                       remarks              = remarks,
                                       
                                       transact_by          = transact_by,
                                       
                                       transact_datetime    = transact_datetime,
                                       
                                       is_sales_transaction = True,
                                       promotion_code       = promotion_code,
                                       
                                       )
            
        trigger_check_reward_success = trigger_spending_reward_for_transaction(customer_transaction)
        
        logger.debug('trigger_check_reward_success=%s', trigger_check_reward_success)
        
        if trigger_check_reward_success:
            create_transaction_message(customer_transaction)
            create_merchant_customer_transaction_upstream_for_merchant(customer_transaction, )
        
        
        return customer_transaction
        
    return __start_transaction_for_customer_transaction()

def give_reward_from_sales_transaction(customer, sales_transaction, for_testing=False, ):
    
    logger.debug('---give_reward_from_sales_transaction---')
    
    @model_transactional(desc='give_reward_from_sales_transaction')
    def __start_transaction(customer, sales_transaction):
        customer_transaction = CustomerTransaction.create_from_sales_transaction(customer, sales_transaction, for_testing=for_testing,)
        if for_testing==False:
            trigger_check_reward_success = trigger_spending_reward_for_transaction(customer_transaction)
            
            logger.debug('trigger_check_reward_success=%s', trigger_check_reward_success)
            
            if trigger_check_reward_success:
                create_transaction_message(customer_transaction)
                create_merchant_customer_transaction_upstream_for_merchant(customer_transaction,)
        
        return customer_transaction
    
    customer_transaction = CustomerTransaction.get_by_transaction_id(sales_transaction.transaction_id)
    logger.debug('customer_transaction=%s', customer_transaction)
    
    if customer_transaction is None:
        customer_transaction = __start_transaction(customer, sales_transaction)
    else:
        logger.info('customer transaction have been created thus ignore to give reward')
    return customer_transaction
    

def create_non_sales_system_transaction(customer, transact_datetime=None, remarks=None, system_remarks=None):
    
    logger.debug('---create_non_sales_system_transaction---')
    
    #@model_transactional(desc='create_non_sales_system_transaction')
    def __start_transaction_for_customer_transaction():
        customer_transaction = CustomerTransaction.create_system_transaction(
                                       customer, 
                                       transact_datetime    = transact_datetime,
                                       allow_to_revert      = False,
                                       is_sales_transaction = False,
                                       remarks              = remarks,
                                       system_remarks       = system_remarks,
                                       )
            
        return customer_transaction
        
    return __start_transaction_for_customer_transaction()
    
def trigger_spending_reward_for_transaction(transaction_details):
    logger.debug('trigger_spending_reward_for_transaction: promotion_code=%s', transaction_details.promotion_code)
    
    if conf.CHECK_ENTITLE_REWARD_THRU_TASKQUEUE:
        transaction_key                 = transaction_details.key_in_str
        
        task_url                        = CHECK_CUSTOMER_ENTITLE_REWARD_TASK_URL
        
        logger.debug('trigger_spending_reward_for_transaction: transaction_key=%s', transaction_key)
        logger.debug('trigger_spending_reward_for_transaction: task_url=%s', task_url)
        
        queue_name      = 'giveaway-reward' 
        payload         = {
                            'transaction_key' : transaction_key
                        }
        
        logger.debug('trigger_spending_reward_for_transaction: payload=%s', payload)
        
        
                        
        create_task(task_url, queue_name, payload=payload, 
                        in_seconds      = 1, 
                        http_method     = 'POST',
                        credential_path = SYSTEM_TASK_SERVICE_CREDENTIAL_PATH, 
                        project_id      = SYSTEM_TASK_GCLOUD_PROJECT_ID,
                        location        = SYSTEM_TASK_GCLOUD_LOCATION,
                        service_email   = SYSTEM_TASK_SERVICE_ACCOUNT_EMAIL
                        )
        
        return True
    else:
        
        customer_acct       = transaction_details.transact_customer_acct
        #merchant_acct       = transaction_details.transact_merchant_acct
        check_reward_status = check_spending_reward_for_transaction(customer_acct, transaction_details)
        
        return check_reward_status

def update_customer_kpi_summary_and_transact_summary(customer_acct, transaction_details):
    
    logger.debug('---update_customer_kpi_summary_and_transact_summary---')
    
    kpi_summary = customer_acct.kpi_summary
    
    transaction_entitled_point      = .0
    transaction_entitled_prepaid    = .0
    transaction_entitled_stamp      = 0
    
    if transaction_details.entitled_reward_summary:        
        if transaction_details.entitled_reward_summary.get(program_conf.REWARD_FORMAT_POINT):
            transaction_entitled_point = transaction_details.entitled_reward_summary.get(program_conf.REWARD_FORMAT_POINT).get('amount') or .0
            
        if transaction_details.entitled_reward_summary.get(program_conf.REWARD_FORMAT_STAMP):
            transaction_entitled_stamp = transaction_details.entitled_reward_summary.get(program_conf.REWARD_FORMAT_STAMP).get('amount') or 0
    
    if transaction_details.entitled_prepaid_summary:    
        transaction_entitled_prepaid = transaction_details.entitled_prepaid_summary.get('amount') or .0    
        
    
    if kpi_summary is None:
        kpi_summary = {
                        'total_transact_amount'             : .0,
                        'total_accumulated_point'           : .0,
                        'total_accumulated_stamp'           : 0,
                        'total_accumulated_point'           : .0,
                        'total_accumulated_prepaid'         : .0,
                        }
    
    customer_acct.previous_transact_datetime    = customer_acct.last_transact_datetime
    customer_acct.last_transact_datetime        = transaction_details.transact_datetime
    
    kpi_summary['total_transact_amount']        += transaction_details.transact_amount
    kpi_summary['total_accumulated_point']      += transaction_entitled_point
    kpi_summary['total_accumulated_stamp']      += transaction_entitled_stamp
    kpi_summary['total_accumulated_prepaid']    += transaction_entitled_prepaid
    
    customer_acct.kpi_summary = kpi_summary
    customer_acct.put()
    
def update_customer_kpi_summary_from_transaction_list(customer_acct, transaction_list):
    
    logger.debug('---update_customer_kpi_summary_from_transaction_list---')
    
    kpi_summary = customer_acct.kpi_summary
    
    transaction_entitled_point      = .0
    transaction_entitled_prepaid    = .0
    transaction_entitled_stamp      = 0
    transaction_transact_amount     = .0
    
    for transaction_details in transaction_list:
        
        if transaction_details.entitled_reward_summary:        
            if transaction_details.entitled_reward_summary.get(program_conf.REWARD_FORMAT_POINT):
                transaction_entitled_point += transaction_details.entitled_reward_summary.get(program_conf.REWARD_FORMAT_POINT).get('amount') or .0
                
            if transaction_details.entitled_reward_summary.get(program_conf.REWARD_FORMAT_STAMP):
                transaction_entitled_stamp += transaction_details.entitled_reward_summary.get(program_conf.REWARD_FORMAT_STAMP).get('amount') or 0
        
        if transaction_details.entitled_prepaid_summary:    
            transaction_entitled_prepaid += transaction_details.entitled_prepaid_summary.get('amount') or .0    
            
        transaction_transact_amount+=transaction_details.transact_amount
        
        logger.debug('update_customer_kpi_summary_from_transaction_list debug: transaction_entitled_point=%s', transaction_entitled_point)
        logger.debug('update_customer_kpi_summary_from_transaction_list debug: transaction_entitled_prepaid=%s', transaction_entitled_prepaid)
        logger.debug('update_customer_kpi_summary_from_transaction_list debug: transaction_entitled_stamp=%s', transaction_entitled_stamp)
        logger.debug('update_customer_kpi_summary_from_transaction_list debug: transaction_transact_amount=%s', transaction_transact_amount)
        
        if kpi_summary is None:
            kpi_summary = {
                            'total_transact_amount'             : .0,
                            'total_accumulated_point'           : .0,
                            'total_accumulated_stamp'           : 0,
                            'total_accumulated_point'           : .0,
                            'total_accumulated_prepaid'         : .0,
                            }
        if transaction_details.transact_datetime > customer_acct.last_transact_datetime:    
            customer_acct.previous_transact_datetime    = customer_acct.last_transact_datetime
            customer_acct.last_transact_datetime        = transaction_details.transact_datetime
    
    kpi_summary['total_transact_amount']        += transaction_transact_amount
    kpi_summary['total_accumulated_point']      += transaction_entitled_point
    kpi_summary['total_accumulated_stamp']      += transaction_entitled_stamp
    kpi_summary['total_accumulated_prepaid']    += transaction_entitled_prepaid
    
    logger.debug('update_customer_kpi_summary_from_transaction_list debug: kpi_summary=%s', kpi_summary)
    
    customer_acct.kpi_summary = kpi_summary
    customer_acct.put()    
    
    logger.debug('update_customer_kpi_summary_from_transaction_list debug: customer_acct.kpi_summary after updated=%s', customer_acct.kpi_summary)
    

def check_for_tier_membership_upgrade_downgrade(customer_acct, merchant_acct, transaction_details):
    
    logger.debug('---check_for_tier_membership_upgrade_downgrade---')
    if merchant_acct.is_tier_membership_configured:
        merchant_tier_membership_list   = MerchantTierMembership.list_by_merchant_acct(merchant_acct)
        existing_tier_membership_key    = customer_acct.tier_membership_key
        existing_tier_membership        = None
        membership_to_assign            = None
        
        customer_kpi_summary            = customer_acct.kpi_summary or {}
        
        total_transact_amount           = customer_kpi_summary.get('total_transact_amount',0)
        total_accumulated_point         = customer_kpi_summary.get('total_accumulated_point',0)
        total_accumulated_stamp         = customer_kpi_summary.get('total_accumulated_stamp',0) 
        total_accumulated_prepaid       = customer_kpi_summary.get('total_accumulated_prepaid',0)
        
        logger.debug('check_for_tier_membership_upgrade_downgrade: total_transact_amount=%s', total_transact_amount)
        logger.debug('check_for_tier_membership_upgrade_downgrade: total_accumulated_point=%s', total_accumulated_point)
        logger.debug('check_for_tier_membership_upgrade_downgrade: total_accumulated_stamp=%s', total_accumulated_stamp)
        logger.debug('check_for_tier_membership_upgrade_downgrade: total_accumulated_prepaid=%s', total_accumulated_prepaid)
        
        existing_membership_qualification_details                   = {}
        highest_entitle_qualification_details                       = {}
        no_membership_or_existing_membership_is_auto_assigned       = False
        
        if existing_tier_membership_key:
            existing_tier_membership        = MerchantTierMembership.fetch(existing_tier_membership_key)
            
            if existing_tier_membership:
                if existing_tier_membership.archived==True:
                    existing_tier_membership = None
                    no_membership_or_existing_membership_is_auto_assigned = True
                else:
                    if existing_tier_membership.entitle_qualification_type == program_conf.MEMBERSHIP_ENTITLE_QUALIFICATION_TYPE_AUTO_ASSIGN:
                        no_membership_or_existing_membership_is_auto_assigned = True
                    else:
                        existing_membership_qualification_details[existing_tier_membership.entitle_qualification_type] = existing_tier_membership.entitle_qualification_value
        else:
            no_membership_or_existing_membership_is_auto_assigned = True
                
        for membership in merchant_tier_membership_list:
            logger.debug('checking tier membership %s, entitle_qualification_type=%s', membership.label, membership.entitle_qualification_type)
            
            if membership.entitle_qualification_type == program_conf.MEMBERSHIP_ENTITLE_QUALIFICATION_TYPE_AUTO_ASSIGN:
                if membership_to_assign is None:
                    membership_to_assign = membership
                    
                    logger.debug('Found auto assign tier membership')
                    
            if membership.entitle_qualification_type == program_conf.MEMBERSHIP_ENTITLE_QUALIFICATION_TYPE_EXCEED_SPENDING_AMOUNT:
                logger.debug('checking tier membership is based on spending amount')
                if transaction_details.transact_amount >= membership.entitle_qualification_value:
                    highest_entitle_qualification_value =  highest_entitle_qualification_details.get(membership.entitle_qualification_type) or 0
                    if membership.entitle_qualification_value > highest_entitle_qualification_value:
                        membership_to_assign = membership
                        highest_entitle_qualification_details[membership.entitle_qualification_type] = membership.entitle_qualification_value
                        
                        logger.debug('Found %s tier membership to assign', membership.label)
                
                    
            if membership.entitle_qualification_type == program_conf.MEMBERSHIP_ENTITLE_QUALIFICATION_TYPE_ACCUMULATED_SPENDING_AMOUNT:
                logger.debug('checking tier membership is based on accumulated spending amount, where amount is %s', membership.entitle_qualification_value)
                if total_transact_amount >= membership.entitle_qualification_value:
                    highest_entitle_qualification_value =  highest_entitle_qualification_details.get(membership.entitle_qualification_type) or 0
                    if membership.entitle_qualification_value > highest_entitle_qualification_value:
                        membership_to_assign = membership
                        highest_entitle_qualification_details[membership.entitle_qualification_type] = membership.entitle_qualification_value
                        
                        logger.debug('Found %s tier membership to assign', membership.label)
                        
                    
            if membership.entitle_qualification_type == program_conf.MEMBERSHIP_ENTITLE_QUALIFICATION_TYPE_ACCUMULATED_POINT_AMOUNT:
                logger.debug('checking tier membership is based on accumulated point amount, where amount is %s', membership.entitle_qualification_value)
                if total_accumulated_point >= membership.entitle_qualification_value:
                    highest_entitle_qualification_value =  highest_entitle_qualification_details.get(membership.entitle_qualification_type) or 0
                    if membership.entitle_qualification_value > highest_entitle_qualification_value:
                        membership_to_assign = membership
                        highest_entitle_qualification_details[membership.entitle_qualification_type] = membership.entitle_qualification_value
                        
                        logger.debug('Found %s tier membership to assign', membership.label)
                
                                        
            if membership.entitle_qualification_type == program_conf.MEMBERSHIP_ENTITLE_QUALIFICATION_TYPE_ACCUMULATED_STAMP_AMOUNT:
                logger.debug('checking tier membership is based on accumulated stamp amount, where amount is %s', membership.entitle_qualification_value)
                if total_accumulated_stamp >= membership.entitle_qualification_value:
                    highest_entitle_qualification_value =  highest_entitle_qualification_details.get(membership.entitle_qualification_type) or 0
                    if membership.entitle_qualification_value > highest_entitle_qualification_value:
                        membership_to_assign = membership
                        highest_entitle_qualification_details[membership.entitle_qualification_type] = membership.entitle_qualification_value
                        
                        logger.debug('Found %s tier membership to assign', membership.label)
                        
                    
            if membership.entitle_qualification_type == program_conf.MEMBERSHIP_ENTITLE_QUALIFICATION_TYPE_ACCUMULATED_PREPAID_AMOUNT:
                logger.debug('checking tier membership is based on accumulated prepaid amount, where amount is %s', membership.entitle_qualification_value)
                if total_accumulated_prepaid >= membership.entitle_qualification_value:
                    highest_entitle_qualification_value =  highest_entitle_qualification_details.get(membership.entitle_qualification_type) or 0
                    if membership.entitle_qualification_value > highest_entitle_qualification_value:
                        membership_to_assign = membership
                        highest_entitle_qualification_details[membership.entitle_qualification_type] = membership.entitle_qualification_value
                        
                        logger.debug('Found %s tier membership to assign', membership.label)
                        
        
        if membership_to_assign:
            logger.debug('membership_to_assign=%s, ', membership_to_assign.label)
            
            
            is_membership_change = membership_to_assign.key_in_str!=existing_tier_membership_key
            
            logger.debug('is_membership_change=%s', is_membership_change)
            
            if existing_tier_membership:
                logger.debug('existing_tier_membership=%s', existing_tier_membership.label)
                
                if is_membership_change:
                    logger.debug('check_for_tier_membership_upgrade_downgrade: found upgrading tier membership to assign')
                    
                    CustomerTierMembership.change(customer_acct,
                                              membership_to_assign, 
                                              transaction_details,
                                              entitled_datetime=transaction_details.transact_datetime,
                                              )
                    
                    
                    
                    logger.debug('existing_membership_qualification_details=%s', existing_membership_qualification_details)
                    logger.debug('no_membership_or_existing_membership_is_auto_assigned=%s', no_membership_or_existing_membership_is_auto_assigned)
                    
                    check_reward_for_new_membership(customer_acct, transaction_details, membership_to_assign)
                    
                    '''
                    #if existing_membership_qualification_details.get(membership_to_assign.entitle_qualification_type):
                    if no_membership_or_existing_membership_is_auto_assigned:
                        logger.debug('going to check reward for new tier membership')
                        check_reward_for_new_membership(customer_acct, transaction_details, membership_to_assign)
                    else:
                        if highest_entitle_qualification_details.get(membership_to_assign.entitle_qualification_type) > existing_membership_qualification_details.get(membership_to_assign.entitle_qualification_type):
                            logger.debug('Membership is upgrading')
                            check_reward_for_new_membership(customer_acct, transaction_details, membership_to_assign)
                        else:
                            logger.debug('Membership is downgrading')
                    '''
                    
                    
                else:
                    logger.debug('check_for_tier_membership_upgrade_downgrade: remain as existing tier membership')
            else:
                logger.debug('check_for_tier_membership_upgrade_downgrade: found new tier membership to assign')
                CustomerTierMembership.create(customer_acct, 
                                              membership_to_assign, 
                                              transaction_details,
                                              entitled_datetime=transaction_details.transact_datetime,
                                              
                                              )
                #customer_acct.tier_membership = new_tier_membership_key
                
                check_reward_for_new_membership(customer_acct, transaction_details, membership_to_assign)
                
                #customer_acct.put()
        else:
            if existing_tier_membership:
                #should be downgrade and remove membership
                customer_acct.tier_membership           = None
                customer_acct.put()
                logger.debug('check_for_tier_membership_upgrade_downgrade: not tier membership to upgrade, thus remain as existing tier membership')
            else:
                logger.debug('check_for_tier_membership_upgrade_downgrade: not yet entitle any tier membership')
    else:
        logger.debug('no tier membership is configured thus ignore')

def check_reward_for_new_membership(customer_acct, transaction_details, new_membership):
    
    logger.debug('---check_reward_for_new_membership---')
    
    merchant_acct                           = transaction_details.transact_merchant_acct
    merchant_program_configuration_list     = merchant_acct.published_program_configuration.get('programs')
    
    membership_program_configuration_list = []
    
    logger.debug('Found merchant_program_configuration_list count=%d', len(merchant_program_configuration_list))
    
    for program_configuration in merchant_program_configuration_list:
        
        program_desc = program_configuration.get('desc')
        program_reward_base = program_configuration.get('reward_base')
        
        logger.debug('check_reward_for_new_membership: program_desc=%s', program_desc)
        logger.debug('check_reward_for_new_membership: program_reward_base=%s', program_reward_base)
        
        if  program_reward_base== program_conf.REWARD_BASE_ON_GIVEAWAY:
            
            program_giveaway_method = program_configuration.get('giveaway_method')
            
            logger.debug('check_reward_for_new_membership: program_giveaway_method=%s', program_giveaway_method)
            
            if  program_giveaway_method== program_conf.PROGRAM_REWARD_GIVEAWAY_METHOD_SYSTEM:
                logger.debug('found giveaway method is system')
                giveaaway_system_settings = program_configuration.get('program_settings').get('giveaway_system_settings')
                
                logger.debug('check_reward_for_new_membership: giveaaway_system_settings=%s', giveaaway_system_settings)
                
                if giveaaway_system_settings is not None and giveaaway_system_settings.get('giveaway_system_condition') == program_conf.GIVEAWAY_SYSTEM_CONDITION_NEW_MEMBERSHIP:
                    logger.debug('giveaway tier memberships=%s', giveaaway_system_settings.get('giveaway_tier_memberships'))
                    if giveaaway_system_settings.get('giveaway_tier_memberships'):
                        if new_membership.key_in_str in giveaaway_system_settings.get('giveaway_tier_memberships'):
                            membership_program_configuration_list.append(program_configuration)
    
    logger.debug('membership_program_configuration_list=%s', membership_program_configuration_list)
    
    if membership_program_configuration_list:
        return RewardProgramFactory(merchant_acct).get_giveaway_reward(customer_acct, transaction_details, 
                                                                            program_configuration_list  = membership_program_configuration_list, 
                                                                            )
    
    
def check_tier_reward_for_transaction(customer_acct, transaction_details, program_configuration_list=None):
    
    logger.debug('---check_tier_reward_for_transaction---')
    
    merchant_acct   = transaction_details.transact_merchant_acct
    
    return RewardProgramFactory(merchant_acct).get_tier_reward(customer_acct, 
                                                            transaction_details, 
                                                            program_configuration_list=program_configuration_list, 
                                                            )    

    
def check_spending_reward_for_transaction(customer_acct, transaction_details, program_configuration_list=None):
    merchant_acct   = transaction_details.transact_merchant_acct
    
    give_reward_status = RewardProgramFactory(merchant_acct).get_spending_reward(customer_acct, 
                                                            transaction_details, 
                                                            program_configuration_list=program_configuration_list,
                                                            
                                                            )
    
    
    if give_reward_status:
        #check if the giveaway reward format match tier reward program setting
        is_promotion_transaction = is_not_empty(transaction_details.promotion_code)
        logger.info('is_promotion_transaction=%s', is_promotion_transaction)
        
        if is_promotion_transaction==False:
            check_tier_reward_for_transaction(customer_acct, transaction_details)
            check_for_tier_membership_upgrade_downgrade(customer_acct, merchant_acct, transaction_details)
            check_entitled_lucky_draw_ticket_for_transaction(customer_acct, merchant_acct, transaction_details)
            
        update_customer_kpi_summary_and_transact_summary(customer_acct, transaction_details)
        
        
    return give_reward_status

def check_entitled_lucky_draw_ticket_for_transaction(customer_acct, merchant_acct, transaction_details):
    
    if merchant_acct.lucky_draw_program_count>0:
        entries_list = LuckyDrawTicket.create_for_customer_from_sales_amount(customer_acct, 
                                                                             sales_amount=transaction_details.transact_amount, 
                                                                             merchant_acct=merchant_acct, 
                                                                             transact_outlet=transaction_details.transact_outlet_entity)
        ticket_configurations_list = []
        logger.debug('entries_list count=%d', len(entries_list))
        
        for e in entries_list:
            ticket_configurations_list.append(e.to_configuration())
        
        if ticket_configurations_list:
            Customer.add_new_tickets_list_into_lucky_draw_ticket_summary(customer_acct, ticket_configurations_list)
            transaction_details.update_entitled_lucky_draw_ticket_summary(ticket_configurations_list)
            
            
def check_giveaway_reward_for_transaction(customer_acct, transaction_details, program_configuration_list=None, reward_set=1):
    merchant_acct                   = transaction_details.transact_merchant_acct
    program_configuration_list      = merchant_acct.program_configuration_list if program_configuration_list is None else program_configuration_list
    
    give_reward_status =  RewardProgramFactory(merchant_acct).get_giveaway_reward(customer_acct, 
                                                            transaction_details, 
                                                            program_configuration_list=program_configuration_list, 
                                                            reward_set=reward_set)
    
    if give_reward_status:
        #check if the giveaway reward format match tier reward program setting
        check_tier_reward_for_transaction(customer_acct, transaction_details)
        update_customer_kpi_summary_and_transact_summary(customer_acct, transaction_details)
        check_for_tier_membership_upgrade_downgrade(customer_acct, merchant_acct, transaction_details)
    
    return give_reward_status

def check_giveaway_reward_for_membership_purchase_transaction(customer_acct, transaction_details, program_configuration_list=None, reward_set=1):
    logger.debug('---check_giveaway_reward_for_membership_purchase_transaction---')
    merchant_acct                   = transaction_details.transact_merchant_acct
    program_configuration_list      = merchant_acct.program_configuration_list if program_configuration_list is None else program_configuration_list
    
    give_reward_status =  RewardProgramFactory(merchant_acct).get_purchase_membership_giveaway_reward(customer_acct, 
                                                            transaction_details, 
                                                            program_configuration_list=program_configuration_list, 
                                                            reward_set=reward_set)
    
    '''
    if give_reward_status:
        #check if the giveaway reward format match tier reward program setting
        check_tier_reward_for_transaction(customer_acct, transaction_details)
    '''
    return give_reward_status

def redeem_reward_transaction(customer, redeem_outlet=None, reward_format=None, reward_amount=.0, invoice_id=None, remarks=None, 
                            redeemed_by=None, redeemed_datetime=None, transaction_id=None, prepaid_redeem_code=None,
                            redeemed_voucher_keys_list=None,
                            ):
    logger.debug('---redeem_reward_transaction---')
    
    if reward_format in program_conf.REWARD_FORMAT_SET:
    
        @model_transactional(desc='redeem_reward_transaction')
        def __start_transaction_for_customer_transaction():
            
            logger.debug('reward_format=%s', reward_format)
            
            customer_redemption = CustomerRedemption.create(customer, reward_format, 
                                      redeemed_outlet               = redeem_outlet, 
                                      redeemed_amount               = reward_amount,
                                      redeemed_voucher_keys_list    = redeemed_voucher_keys_list,                      
                                      prepaid_redeem_code           = prepaid_redeem_code,
                                      invoice_id                    = invoice_id, 
                                      transaction_id                = transaction_id,
                                      remarks                       = remarks, 
                                      redeemed_by                   = redeemed_by, 
                                      redeemed_datetime             = redeemed_datetime,
                                      )
            
            if customer_redemption:
                create_redemption_message(customer_redemption)
                create_merchant_customer_redemption_upstream_for_merchant(customer_redemption, )
                if reward_format == program_conf.REWARD_FORMAT_VOUCHER:
                    for voucher_key in redeemed_voucher_keys_list:
                        customer_voucher        = CustomerEntitledVoucher.fetch(voucher_key)
                        if customer_voucher:
                            create_redeemed_customer_voucher_to_upstream_for_merchant(customer_voucher)
                    
            
            return customer_redemption
            
        return __start_transaction_for_customer_transaction()
    else:
        raise Exception("Invalid reward format")

def prepaid_payment_transaction(customer, redeem_outlet=None, reward_format=None, reward_amount=.0, invoice_id=None, remarks=None, 
                            redeemed_by=None, redeemed_datetime=None, transaction_id=None, prepaid_redeem_code=None,
                            
                            ):
    logger.debug('---prepaid_payment_transaction---')
    
    if reward_format in program_conf.REWARD_FORMAT_SET:
    
        @model_transactional(desc='redeem_reward_transaction')
        def __start_transaction_for_customer_transaction():
            
            logger.debug('reward_format=%s', reward_format)
            
            customer_redemption = CustomerRedemption.create(customer, reward_format, 
                                      redeemed_outlet               = redeem_outlet, 
                                      redeemed_amount               = reward_amount,
                                      prepaid_redeem_code           = prepaid_redeem_code,
                                      invoice_id                    = invoice_id, 
                                      transaction_id                = transaction_id,
                                      remarks                       = remarks, 
                                      redeemed_by                   = redeemed_by, 
                                      redeemed_datetime             = redeemed_datetime,
                                      )
            
            if customer_redemption:
                create_payment_message(customer_redemption)
                create_merchant_customer_redemption_upstream_for_merchant(customer_redemption, )
            
            return customer_redemption
            
        return __start_transaction_for_customer_transaction()
    else:
        raise Exception("Invalid reward format") 

def update_customer_reward_summary(customer):
    entitled_point_details_list     = CustomerPointReward.list_by_customer(customer)
    entitled_stamp_details_list     = CustomerStampReward.list_by_customer(customer)      
    
    entitled_reward_summary         = {}
    
    logger.debug('update_customer_reward_summary: entitled_point_details_list=%s', entitled_point_details_list)
    logger.debug('update_customer_reward_summary: entitled_stamp_details_list=%s', entitled_stamp_details_list)
    
    for reward in  entitled_point_details_list:
        entiteld_reward_details = reward.to_reward_summary()
        entitled_reward_summary = update_reward_summary_with_new_reward(entitled_reward_summary, entiteld_reward_details)
        
    for reward in  entitled_stamp_details_list:
        entiteld_reward_details = reward.to_reward_summary()
        entitled_reward_summary = update_reward_summary_with_new_reward(entitled_reward_summary, entiteld_reward_details)
     
    logger.debug('entitled_reward_summary=%s', entitled_reward_summary) 
        
    customer.reward_summary    = entitled_reward_summary
    
    customer.put()
    
def update_customer_prepaid_summary(customer):
    prepaid_reward_list     = CustomerPrepaidReward.list_by_customer(customer)    
    prepaid_summary         = {}
    
    for prepaid in  prepaid_reward_list:
        prepaid = prepaid.to_prepaid_summary()
        prepaid_summary = update_prepaid_summary_with_new_prepaid(prepaid_summary, prepaid)
    
    customer.prepaid_summary = prepaid_summary
    customer.put()
    
def update_customer_memberships_list(customer):
    customer_memberships_list     = CustomerMembership.list_all_by_customer(customer)
    memberships_list              = []
    
    
    for customer_membership in  customer_memberships_list:
        if customer_membership.is_valid():
            memberships_list.append(customer_membership.merchant_membership_key)
        
        
    customer.memberships_list    = memberships_list
    
    customer.put()    

def revert_transaction(transaction_details, reverted_by, reverted_datetime=None, create_upstream=True):
    merchant_acct                       = transaction_details.transact_merchant_acct
    transaction_id                      = transaction_details.transaction_id
    customer_acct                       = transaction_details.transact_customer_acct
    is_from_instant_transaction         = transaction_details.is_from_instant_transaction
    
    if transaction_details.is_membership_purchase:
        #remove membership
        
        merchant_membership_key         = transaction_details.purchased_merchant_membership_key
        merchant_membership             = transaction_details.purchased_merchant_membership_entity
        purchased_customer_membership   = CustomerMembership.get_by_customer_and_merchant_membership(customer_acct, merchant_membership)
        if purchased_customer_membership:
            try:
                 
                purchased_customer_membership.delete()
            except:
                logger.error('Failed due to %s', get_tracelog())
        
        else:
            logger.warn('Customer membership is not found')
        
        if is_not_empty(customer_acct.memberships_list):
            customer_acct.memberships_list.remove(merchant_membership_key)
        
        customer_acct.put()
        
        return True
        
    elif transaction_details.is_membership_renew:
        #revert renewal
        renewed_customer_membership = transaction_details.purchased_customer_membership_entity
        renewed_customer_membership.revert_renewal()    
        customer_acct.put()
        
        return True
    else:    
        if is_not_empty(transaction_details.entitled_reward_summary):
            is_stamp_entitled_in_transaction    = transaction_details.entitled_reward_summary.get(program_conf.REWARD_FORMAT_STAMP) is not None
            is_point_entitled_in_transaction    = transaction_details.entitled_reward_summary.get(program_conf.REWARD_FORMAT_POINT) is not None
            is_voucher_entitled_in_transaction  = transaction_details.entitled_voucher_summary is not None
            is_prepaid_entitled_in_transaction  = transaction_details.entitled_prepaid_summary is not None
        else:
            is_stamp_entitled_in_transaction    = False
            is_point_entitled_in_transaction    = False
            is_voucher_entitled_in_transaction  = False
            is_prepaid_entitled_in_transaction  = False
        
        
        logger.debug('transaction_details.entitled_reward_summary=%s', transaction_details.entitled_reward_summary)
        logger.debug('transaction_details.entitled_prepaid_summary=%s', transaction_details.entitled_prepaid_summary)
        
        is_transaction_reward_used          = False
        
        if is_stamp_entitled_in_transaction or is_point_entitled_in_transaction or is_voucher_entitled_in_transaction or is_prepaid_entitled_in_transaction: 
        
            reverting_point_details_list        = CustomerPointReward.list_by_transaction_id(transaction_id) if is_point_entitled_in_transaction else []
            reverting_stamp_details_list        = CustomerStampReward.list_by_transaction_id(transaction_id) if is_stamp_entitled_in_transaction else []
            reverting_vouchers_list             = CustomerEntitledVoucher.list_by_transaction_id(transaction_id) if is_voucher_entitled_in_transaction else []
            reverting_prepaid_list              = CustomerPrepaidReward.list_by_transaction_id(transaction_id) if is_prepaid_entitled_in_transaction else []
            
            
            customer_reward_summary             = customer_acct.reward_summary or {}
            customer_prepaid_summary            = customer_acct.prepaid_summary or {}
            entitled_voucher_summary            = customer_acct.entitled_voucher_summary or {}
            
            
            if reverted_datetime is None:
                reverted_datetime = datetime.utcnow()
            
            logger.debug('revert_transaction: transaction_id=%s', transaction_id)
            logger.debug('revert_transaction: reverted_datetime=%s', reverted_datetime)
            logger.debug('revert_transaction: reverting_point_details_list count=%s', len(reverting_point_details_list))
            logger.debug('revert_transaction: reverting_stamp_details_list count=%s', len(reverting_stamp_details_list))
            logger.debug('revert_transaction: reverting_vouchers_list count=%s', len(reverting_vouchers_list))
            logger.debug('revert_transaction: reverting_prepaid_list count=%s', len(reverting_prepaid_list))
            
            for p in reverting_point_details_list:
                if p.is_used:
                    is_transaction_reward_used = True
                    break
            
            if is_transaction_reward_used is False:
                for p in reverting_stamp_details_list:
                    if p.is_used:
                        is_transaction_reward_used = True
                        break
                    
            if is_transaction_reward_used is False:
                for p in reverting_vouchers_list:
                    if p.is_used:
                        is_transaction_reward_used = True
                        break
                    
            if is_transaction_reward_used is False:
                for p in reverting_prepaid_list:
                    if p.is_used:
                        is_transaction_reward_used = True
                        break        
        
        logger.debug('revert: is_transaction_reward_used=%s', is_transaction_reward_used)
        
        if is_transaction_reward_used is False:
            
            logger.debug('Going to revert transaction')
            
            reverted_by_key                                = reverted_by.create_ndb_key()
            transaction_details.is_revert                  = True
            transaction_details.reverted_datetime          = reverted_datetime
            transaction_details.reverted_by                = reverted_by_key
            transaction_details.reverted_by_username       = reverted_by.username
            transaction_details.put()
            
            create_merchant_customer_transaction_upstream_for_merchant(transaction_details, Reverted=True)
            
            if transaction_details.is_from_instant_transaction:
                sales_transaction = SalesTransaction.get_by_transaction_id(transaction_id)
                
                if sales_transaction:
                    sales_transaction.used                  = False
                    sales_transaction.put()
            
            if is_stamp_entitled_in_transaction or is_point_entitled_in_transaction or is_voucher_entitled_in_transaction or is_prepaid_entitled_in_transaction:
                for p in reverting_point_details_list:
                    if p.is_valid:
                        p.status                        = program_conf.REWARD_STATUS_REVERTED
                        p.reverted_datetime             = reverted_datetime
                        p.reverted_by                   = reverted_by_key
                        p.reverted_by_username          = reverted_by.username
                        p.put()
                        
                        customer_reward_summary = update_reward_summary_with_reverted_reward(customer_reward_summary, p.to_reward_summary())
                        if create_upstream:
                            create_merchant_customer_reward_upstream_for_merchant(transaction_details, p, Reverted=True)
                        
                    
                for p in reverting_stamp_details_list:
                    if p.is_valid:
                        p.status                        = program_conf.REWARD_STATUS_REVERTED
                        p.reverted_datetime             = reverted_datetime
                        p.reverted_by                   = reverted_by_key
                        p.reverted_by_username          = reverted_by.username
                        p.put()
                        
                        customer_reward_summary = update_reward_summary_with_reverted_reward(customer_reward_summary, p.to_reward_summary())
                        if create_upstream:
                            create_merchant_customer_reward_upstream_for_merchant(transaction_details, p, Reverted=True)
                    
                for p in reverting_vouchers_list:
                    if p.is_valid:
                        p.status                        = program_conf.REWARD_STATUS_REVERTED
                        p.reverted_datetime             = reverted_datetime
                        p.reverted_by                   = reverted_by_key
                        p.reverted_by_username          = reverted_by.username
                        p.put()
                        
                        create_revert_entitled_customer_voucher_upstream_for_merchant(p)
                        
                        entitled_voucher_summary = update_customer_entiteld_voucher_summary_after_reverted_voucher(entitled_voucher_summary, p)
                        
                        voucher_key         = p.entitled_voucher_key
                        expiry_date         = p.expiry_date
                        rewarded_datetime   = p.rewarded_datetime
                        
                        voucher_reward_brief = VoucherRewardDetailsForUpstreamData(voucher_key, 1, expiry_date, rewarded_datetime)
                        if create_upstream:
                            create_merchant_customer_reward_upstream_for_merchant(transaction_details, voucher_reward_brief, Reverted=True)
                
                for p in reverting_prepaid_list:
                    if p.is_valid:
                        p.status                        = program_conf.REWARD_STATUS_REVERTED
                        p.reverted_datetime             = reverted_datetime
                        p.reverted_by                   = reverted_by_key
                        p.reverted_by_username          = reverted_by.username
                        p.put()
                        
                        customer_prepaid_summary = update_prepaid_summary_with_reverted_prepaid(customer_prepaid_summary, p.to_prepaid_summary())
                        if create_upstream:
                            create_merchant_customer_prepaid_upstream_for_merchant(transaction_details, p, Reverted=True)
                
                
            
                if is_stamp_entitled_in_transaction or is_point_entitled_in_transaction:
                    #update_customer_reward_summary(customer_acct)
                    customer_acct.reward_summary           = customer_reward_summary
                
                if is_prepaid_entitled_in_transaction:
                    #update_customer_prepaid_summary(customer_acct)
                    customer_acct.prepaid_summary           = customer_prepaid_summary
                
                if is_voucher_entitled_in_transaction:
                    customer_acct.entitled_voucher_summary  = entitled_voucher_summary
                
                total_transact_amount       = .0
                total_accumulated_point     = .0
                total_accumulated_stamp     = 0
                total_accumulated_topup     = .0
                total_accumulated_prepaid   = .0
                
                
                if customer_acct.kpi_summary:
                    total_transact_amount           = customer_acct.kpi_summary.get('total_transact_amount') or .0
                    total_accumulated_point         = customer_acct.kpi_summary.get('total_accumulated_point') or .0
                    total_accumulated_stamp         = customer_acct.kpi_summary.get('total_accumulated_stamp') or 0
                    total_accumulated_topup         = customer_acct.kpi_summary.get('total_accumulated_topup') or .0
                    total_accumulated_prepaid       = customer_acct.kpi_summary.get('total_accumulated_prepaid') or .0
                
                else:
                    customer_acct.kpi_summary = {}
                
                transaction_entitled_point      = .0
                transaction_entitled_stamp      = 0
                transaction_topup_prepaid       = .0
                transaction_entitled_prepaid    = .0
                
                logger.debug('is_point_entitled_in_transaction=%s', is_point_entitled_in_transaction)
                logger.debug('is_stamp_entitled_in_transaction=%s', is_stamp_entitled_in_transaction)
                logger.debug('is_prepaid_entitled_in_transaction=%s', is_prepaid_entitled_in_transaction)
                
                if is_point_entitled_in_transaction:
                    logger.debug('transaction_details entitled point summary=%s', transaction_details.entitled_reward_summary.get(program_conf.REWARD_FORMAT_POINT))
                    transaction_entitled_point = transaction_details.entitled_reward_summary.get(program_conf.REWARD_FORMAT_POINT).get('amount') or 0
                    
                if is_stamp_entitled_in_transaction:
                    logger.debug('transaction_details entitled stamp summary=%s', transaction_details.entitled_reward_summary.get(program_conf.REWARD_FORMAT_STAMP))
                    transaction_entitled_stamp = transaction_details.entitled_reward_summary.get(program_conf.REWARD_FORMAT_STAMP).get('amount') or 0
                    
                if is_prepaid_entitled_in_transaction:
                    logger.debug('transaction_details entitled prepaid summary=%s', transaction_details.entitled_prepaid_summary)
                    transaction_topup_prepaid = transaction_details.entitled_prepaid_summary.get('amount') or .0
                    
                customer_acct.last_transact_datetime    = customer_acct.previous_transact_datetime
                
                total_transact_amount                   -= transaction_details.transact_amount
                total_accumulated_point                 -= transaction_entitled_point
                total_accumulated_stamp                 -= transaction_entitled_stamp
                total_accumulated_topup                 -= transaction_topup_prepaid
                total_accumulated_prepaid               -= transaction_entitled_prepaid
                
                if total_transact_amount<0:
                    total_transact_amount = .0
                    
                if total_accumulated_point<0:
                    total_accumulated_point = .0
                    
                if total_accumulated_stamp<0:
                    total_accumulated_stamp = 0        
                    
                if total_accumulated_topup<0:
                    total_accumulated_topup = .0
                    
                if total_accumulated_prepaid<0:
                    total_accumulated_prepaid = .0        
                    
                customer_acct.kpi_summary['total_transact_amount']          = total_transact_amount
                customer_acct.kpi_summary['total_accumulated_point']        = total_accumulated_point
                customer_acct.kpi_summary['total_accumulated_stamp']        = total_accumulated_stamp
                customer_acct.kpi_summary['total_accumulated_topup']        = total_accumulated_topup
                customer_acct.kpi_summary['total_accumulated_prepaid']      = total_accumulated_prepaid
            
            
                customer_acct.put()
             
                check_for_tier_membership_upgrade_downgrade(customer_acct, merchant_acct, transaction_details) 
            
            __revert_tier_reward(customer_acct, transaction_details)
            
            
            return True
        
        else:
            raise Exception('Transaction reward have been used')
    

def __revert_tier_reward(customer, transaction_details):
    customer_tier_reward_summary_list    = CustomerEntitledTierRewardSummary.list_tier_reward_summary_by_customer(customer)
    transaction_id = transaction_details.transaction_id
    
    logger.debug('__revert_tier_reward debug: transation id to revert tier reward = %s', transaction_id)
    
    if is_not_empty(customer_tier_reward_summary_list):
        for customer_tier_reward_summary in customer_tier_reward_summary_list:
            tier_summary = customer_tier_reward_summary.tier_summary
            is_tier_summary_reverted = False
            logger.debug('tier_summary before =%s', tier_summary)
            
            for tier in tier_summary.get('tiers'):
                unlock_value = tier.get('unlock_value')
                
                #for unlock_source in tier.get('unlock_source_details'):
                unlock_sources_list = []
                for index, unlock_source in enumerate(tier.get('unlock_source_details')):    
                    if unlock_source.get('transaction_id') == transaction_id:
                        logger.debug('__revert_tier_reward debug: Found unlock source based on transaction id, tier no=%d, unlock amount=%d', index, unlock_source.get('amount'))
                        unlock_value -= unlock_source.get('amount')
                        
                        tier['unlock_status']   = False
                        tier['unlock_value']    = unlock_value
                        
                        is_tier_summary_reverted = True
                    else:
                        unlock_sources_list.append(unlock_source)
                
                tier['unlock_source_details'] = unlock_sources_list    
                
            logger.debug('tier_summary after =%s', tier_summary)
            
            if is_tier_summary_reverted:
                customer_tier_reward_summary.put() 
    else:
        logger.debug('__revert_tier_reward debug: not found any tier reward cycle for customer')
        
        
def create_topup_prepaid_transaction(customer, prepaid_program, topup_outlet=None, topup_amount=.0, invoice_id=None, remarks=None, system_remarks=None,
                            topup_by=None):
    
    logger.debug('---create_topup_prepaid_transaction---')
    
    transact_datetime   = datetime.now()
    prepaid_summary     = {}
    
    @model_transactional(desc='create_topup_prepaid_transaction')
    def __start_transaction_for_customer_transaction():
        
        logger.debug('topup_amount=%s', topup_amount)
        
        customer_transaction = CustomerTransaction.create_system_transaction(
                                       customer, 
                                       transact_outlet      = topup_outlet,
                                       
                                       transact_amount      = topup_amount, 
                                       
                                       invoice_id           = invoice_id, 
                                       remarks              = remarks,
                                       system_remarks       = system_remarks,
                                       
                                       transact_by          = topup_by,
                                       
                                       is_sales_transaction = True,
                                       
                                       )
            
        prepaid_topup_reward = CustomerPrepaidReward.topup(customer, topup_amount, prepaid_program, topup_outlet=topup_outlet, 
                                                           topup_by=topup_by, transaction_id=customer_transaction.transaction_id)
        
        
        if prepaid_topup_reward:
            customer_transaction.entitled_prepaid_summary = prepaid_topup_reward.to_prepaid_summary()
            customer_transaction.put()
            
            prepaid_summary = customer.prepaid_summary
            
            logger.debug('Customer existing , prepaid_summary=%s', prepaid_summary)
            
            prepaid_summary = update_prepaid_summary_with_new_prepaid(prepaid_summary, prepaid_topup_reward.to_prepaid_summary())
            
            logger.debug('After new topup, customer(%s) prepaid_summary=%s', customer.name,prepaid_summary)
            
            customer.prepaid_summary = prepaid_summary
            customer.put()
            
            update_customer_kpi_summary_and_transact_summary(customer, customer_transaction)
            
            create_transaction_message(customer_transaction)
            create_merchant_customer_prepaid_upstream_for_merchant(customer_transaction, prepaid_topup_reward, )
            create_merchant_customer_transaction_upstream_for_merchant(customer_transaction, )
        
        return (customer_transaction, prepaid_summary)
        
    return __start_transaction_for_customer_transaction()  


def update_customer_all_entitled_reward_summary(customer):
    point_reward_list       = CustomerPointReward.list_by_customer(customer)
    stamp_reward_list       = CustomerStampReward.list_by_customer(customer)
    vouchers_list           = CustomerEntitledVoucher.list_by_customer(customer)
    prepaid_reward_list     = CustomerPrepaidReward.list_by_customer(customer) 
    
    customer_reward_summary              = {}
    customer_prepaid_summary             = {}
    customer_entitled_voucher_summary    = {}
    
    if point_reward_list:
        for point in point_reward_list:
            customer_reward_summary = update_reward_summary_with_new_reward(customer_reward_summary, point.to_reward_summary())
            
    if stamp_reward_list:
        for stamp in stamp_reward_list:
            customer_reward_summary = update_reward_summary_with_new_reward(customer_reward_summary, stamp.to_reward_summary())
            
    if vouchers_list:
        for voucher in vouchers_list:
            customer_entitled_voucher_summary = update_customer_entiteld_voucher_summary_with_customer_new_voucher(customer_entitled_voucher_summary, voucher)
                    
    
    if prepaid_reward_list:    
        for prepaid in prepaid_reward_list:
            customer_prepaid_summary = update_prepaid_summary_with_new_prepaid(customer_prepaid_summary, prepaid.to_prepaid_summary())
            
    customer.reward_summary             = customer_reward_summary
    customer.prepaid_summary            = customer_prepaid_summary
    customer.entitled_voucher_summary   = customer_entitled_voucher_summary
    
    customer.put()
    
def update_customer_entitled_reward_summary(customer):
    point_reward_list       = CustomerPointReward.list_by_customer(customer)
    stamp_reward_list       = CustomerStampReward.list_by_customer(customer)
    
    customer_reward_summary              = {}
    if point_reward_list:
        for point in point_reward_list:
            customer_reward_summary = update_reward_summary_with_new_reward(customer_reward_summary, point.to_reward_summary())
            
    if stamp_reward_list:
        for stamp in stamp_reward_list:
            customer_reward_summary = update_reward_summary_with_new_reward(customer_reward_summary, stamp.to_reward_summary())
            
    customer.reward_summary             = customer_reward_summary
    
    customer.put()    
    
def update_customer_entitled_voucher_summary(customer):
    vouchers_list           = CustomerEntitledVoucher.list_by_customer(customer)
    customer_entitled_voucher_summary    = {}
    
    if vouchers_list:
        for voucher in vouchers_list:
            customer_entitled_voucher_summary = update_customer_entiteld_voucher_summary_with_customer_new_voucher(customer_entitled_voucher_summary, voucher)
                    
    
    customer.entitled_voucher_summary   = customer_entitled_voucher_summary
    
    customer.put()    

        
def update_transaction_all_entitled_reward_summary(transaction_id):
    customer_transaction = CustomerTransaction.get_by_transaction_id(transaction_id)
    if customer_transaction:
        
        logger.debug('customer_transaction=%s', customer_transaction)
        
        point_reward_list       = CustomerPointReward.list_by_transaction_id(transaction_id)
        stamp_reward_list       = CustomerStampReward.list_by_transaction_id(transaction_id)
        vouchers_list           = CustomerEntitledVoucher.list_by_transaction_id(transaction_id)
        prepaid_reward_list     = CustomerPrepaidReward.list_by_transaction_id(transaction_id)
        
        
        logger.debug('prepaid_reward_list count=%d' , len(prepaid_reward_list))
        
        customer_reward_summary             = {}
        customer_entitled_voucher_summary   = {}
        customer_prepaid_summary            = {}
        
        if point_reward_list:
            for p in point_reward_list:
                customer_reward_summary = update_reward_summary_with_new_reward(customer_reward_summary, p.to_reward_summary())
                
        
        if stamp_reward_list:
            for p in stamp_reward_list:
                customer_reward_summary = update_reward_summary_with_new_reward(customer_reward_summary, p.to_reward_summary())
                
        
        if vouchers_list:
            logger.debug('found entitled voucher list')
            entiteld_voucher_brief          = EntitledVoucherSummary(transaction_id=transaction_id)
            
            for customer_voucher in vouchers_list:
                merchant_voucher = customer_voucher.entitled_voucher_entity
                entiteld_voucher_brief.add(merchant_voucher, [customer_voucher])
                
            
            customer_entitled_voucher_summary = entiteld_voucher_brief.entitled_voucher_summary
            logger.debug('customer_entitled_voucher_summary=%s', customer_entitled_voucher_summary)
        
        if prepaid_reward_list:
            for prepaid in prepaid_reward_list:
                customer_prepaid_summary = update_prepaid_summary_with_new_prepaid(customer_prepaid_summary, prepaid.to_prepaid_summary())
        
        customer_transaction.entitled_reward_summary    = customer_reward_summary
        customer_transaction.entitled_voucher_summary   = customer_entitled_voucher_summary
        customer_transaction.entitled_prepaid_summary   = customer_prepaid_summary
        
        customer_transaction.put()
        
        return customer_transaction
        
    else:
        logger.warn('customer_transaction is not found')
        
@model_transactional(desc="giveaway_birthday_reward_to_customer")                
def giveaway_birthday_reward_to_customer(customer, program_configuration, transact_datetime, merchant_acct ):
    return _giveaway_birthday_reward_to_customer(customer, program_configuration, transact_datetime, merchant_acct)
    
def _giveaway_birthday_reward_to_customer(customer, program_configuration, transact_datetime, merchant_acct, is_test_account=False):
    
    try:
        this_year               = transact_datetime.year
        program_key             = program_configuration.get('program_key')
        remarks                 = program_configuration.get('remarks')
        program_desc            = program_configuration.get('desc')
        is_entitled_before      = False
        
        logger.debug('------> going to check for program_key=%s for %s', program_key, customer.name)
        if is_test_account==False:
            is_entitled_before = Customer.check_birthday_reward_have_entitled_before(customer, this_year, program_key)
        else:
            logger.debug('Skip, because it is test user account')    
            
        logger.debug('------> Customer(%s) entitled before (%s)', customer.name, program_desc)
        logger.debug('------> remarks=%s', remarks)
        
        if is_entitled_before == False:
            transaction_details = create_non_sales_system_transaction(customer, transact_datetime=transact_datetime, remarks=remarks)
            
            logger.debug('transaction_details=%s', transaction_details)
               
            RewardProgramFactory(merchant_acct).get_birthday_reward(customer, transaction_details, 
                                                                                program_configuration_list  = [program_configuration], 
                                                                                )
            Customer.update_customer_entitled_birthday_reward_summary(customer, program_key)
            create_transaction_message(transaction_details, remarks=remarks, message_category=conf.MESSAGE_CATEGORY_BIRTHDAY)
        else:
            logger.info('Customer(%s) have entitled birthday reward (%s) on year %d', customer.name, program_desc, this_year)
    except:
        logger.error('Failed to process for customer=%s, due to %s', customer.name, get_tracelog())
        
@model_transactional(desc="giveaway_membership_reward_to_customer")                
def giveaway_membership_reward_to_customer(customer, program_configuration, transact_datetime, merchant_acct ):
    
    try:
        this_year               = transact_datetime.year
        program_key             = program_configuration.get('program_key')
        program_label           = program_configuration.get('label')
        remarks                 = program_configuration.get('remarks')
        program_desc            = program_configuration.get('desc')
        
        logger.debug('------> going to check for program_key=%s for %s', program_key, customer.name)
        
        is_entitled_before = Customer.check_membership_year_reward_have_entitled_before(customer, this_year, program_key)
        logger.debug('------> Customer(%s) entitled %s', customer.name, program_desc)
        
        if is_entitled_before == False:
            system_remarks = 'Giveaway reward from %s' % program_label
            transaction_details = create_non_sales_system_transaction(customer, remarks=remarks, system_remarks=system_remarks)
            
            logger.debug('transaction_details=%s', transaction_details)
               
            RewardProgramFactory(merchant_acct).get_giveaway_reward(customer, transaction_details, 
                                                                                program_configuration_list  = [program_configuration], 
                                                                                )
            Customer.update_customer_entitled_membership_reward_summary(customer, program_key)
        else:
            logger.info('Customer(%s) have entitled membership reward (%s) on year %d', customer.name, program_desc, this_year)
    except:
        logger.error('Failed to process for customer=%s, due to %s', customer.name, get_tracelog())  
        raise      
        

def revert_redemption(redemption_details, reverted_by, reverted_datetime=None):
    
    if reverted_datetime is None:
        reverted_datetime = datetime.utcnow()
    
    redeem_transaction_id       = redemption_details.transaction_id
    redeemed_summary            = redemption_details.redeemed_summary
    customer                    = redemption_details.redeemed_customer_acct
    
    if program_conf.REWARD_FORMAT_VOUCHER in redeemed_summary.keys():
        #found voucher have been redeem in the transaction
        
        '''
        Example of voucher redeemed_summary
        
        redeemed_summary: {
            voucher: {
                vouchers: {
                    ag50cmV4LWFkbWluLWRldnI1CxIMTWVyY2hhbnRBY2N0GICAgPiW0IcKDAsSD01lcmNoYW50Vm91Y2hlchiAgIC4iqmKCgw: {
                    amount: 1,
                    customer_entitled_vouchers: [
                        {
                            customer_entitled_voucher_key: "ag50cmV4LWFkbWluLWRldnJKCxIEVXNlchiAgIC4y6nFCAwLEghDdXN0b21lchiAgICE3I-JCQwLEhdDdXN0b21lckVudGl0bGVkVm91Y2hlchiAgIDY36afCgw",
                            redeem_code: "pW1QXNSMVxa6"
                        }
                    ],
                    image_url: "https://backofficedev.augmigo.com/static/app/assets/img/voucher/voucher-sample-image.png",
                    label: "Lemon Glass Ginger"
                    }
                }
            }
        },
        
        '''
        
        
        redeemed_vouchers_details = redeemed_summary.get('voucher').get('vouchers')
        for merchant_voucher_key, details in redeemed_vouchers_details.items():
            redeemed_customer_entitled_vouchers_list = details.get('customer_entitled_vouchers')
            customer_transaction_map_by_transaction_id = {}
            
            for redeemed_customer_entitled_voucher_details in redeemed_customer_entitled_vouchers_list:
                redeemed_customer_entitled_voucher = CustomerEntitledVoucher.fetch(redeemed_customer_entitled_voucher_details.get('customer_entitled_voucher_key'))
                if redeemed_customer_entitled_voucher:
                    redeemed_customer_entitled_voucher.revert_from_redemption()
                    redeemed_customer_entitled_voucher_transaction_id = redeemed_customer_entitled_voucher.transaction_id
                    
                    redeemed_customer_transaction = customer_transaction_map_by_transaction_id.get(redeemed_customer_entitled_voucher_transaction_id)
                    
                    if redeemed_customer_transaction is None:
                        redeemed_customer_transaction = CustomerTransaction.get_by_transaction_id(redeemed_customer_entitled_voucher_transaction_id)
                        customer_transaction_map_by_transaction_id[redeemed_customer_entitled_voucher_transaction_id] = redeemed_customer_transaction
                    
                    logger.debug('customer_transation_key=%s', redeemed_customer_transaction.key_in_str)
                    
                    customer_transaction_entitled_voucher_summary = redeemed_customer_transaction.entitled_voucher_summary
                    logger.debug('customer_transaction_entitled_voucher_summary=%s', customer_transaction_entitled_voucher_summary)
                    
                    '''
                    Example of entitled_voucher_summary
                    entitled_voucher_summary: {
                        ag50cmV4LWFkbWluLWRldnI1CxIMTWVyY2hhbnRBY2N0GICAgPiW0IcKDAsSD01lcmNoYW50Vm91Y2hlchiAgIC4iqmKCgw: {
                            amount: 2,
                            redeem_info_list: [
                                {
                                    effective_date: "14-02-2023",
                                    expiry_date: "14-05-2023",
                                    is_redeem: true,
                                    redeem_code: "LheTuNnRr51j",
                                    redeem_transaction_id: "r230214154932958705"
                                },
                                {
                                    effective_date: "14-02-2023",
                                    expiry_date: "14-05-2023",
                                    is_redeem: true,
                                    redeem_code: "pW1QXNSMVxa6",
                                    redeem_transaction_id: "r230214170508014950"
                                }
                            ],
                            voucher_key: "ag50cmV4LWFkbWluLWRldnI1CxIMTWVyY2hhbnRBY2N0GICAgPiW0IcKDAsSD01lcmNoYW50Vm91Y2hlchiAgIC4iqmKCgw"
                        }
                    },
'''                     
                    
                    customer_transaction_entitled_voucher_details = customer_transaction_entitled_voucher_summary.get(merchant_voucher_key)
                    
                    logger.debug('customer_transaction_entitled_voucher_details=%s', customer_transaction_entitled_voucher_details)
                    logger.debug('Going to unmark voucher have been redeemed from customer.entitled_voucher_summary.redeem_info_list')
                    
                    for redeem_info in customer_transaction_entitled_voucher_details.get('redeem_info_list'):
                        if redeem_info.get('redeem_transaction_id')==redeem_transaction_id:
                            del redeem_info['redeem_transaction_id']
                            del redeem_info['is_redeem']
                            
                        
                    logger.debug('entitled_voucher_summary before reverted=%s', customer.entitled_voucher_summary)
                    logger.debug('redeemed entitled_voucher_summary =%s', redeemed_customer_transaction.entitled_voucher_summary)
                    
                    #redeemed_customer_transaction.entitled_voucher_summary = entitled_voucher_summary
                    redeemed_customer_transaction.put()
                    
                    customer_new_entitled_voucher_summary = update_customer_entiteld_voucher_summary_with_customer_new_voucher(customer.entitled_voucher_summary, redeemed_customer_entitled_voucher)
                    
                    #customer = customer_entitled_voucher.entitled_customer_entity
                    
                    customer.entitled_voucher_summary = customer_new_entitled_voucher_summary
                    
                    logger.debug('entitled_voucher_summary before reverted=%s', customer.entitled_voucher_summary)
                    
                    customer.put()
        
    
    if program_conf.REWARD_FORMAT_POINT in redeemed_summary.keys():
        '''
        Example of point redeemed_summary
        redeemed_summary: {
            point: {
                amount: 2,
                customer_point_rewards: [
                    {
                    key: "ag50cmV4LWFkbWluLWRldnJGCxIEVXNlchiAgIC4y6nFCAwLEghDdXN0b21lchiAgICE3I-JCQwLEhNDdXN0b21lclN0YW1wUmV3YXJkGICAgNjfrZAJDA",
                    redeemed_amount: 2
                    }
                ]
            }
        },
        '''
        redeemed_details_list   = redeemed_summary.get(program_conf.REWARD_FORMAT_POINT).get('customer_point_rewards')
        
        for redeemed_details in redeemed_details_list:
            customer_point_reward = CustomerPointReward.fetch(redeemed_details.get('key'))
            redeemed_amount = redeemed_details.get('amount')
            customer_point_reward.update_used_reward_amount( -redeemed_amount )
            customer.reward_summary[program_conf.REWARD_FORMAT_POINT]['amount'] += redeemed_amount
        
        customer.put()
        
    if program_conf.REWARD_FORMAT_STAMP in redeemed_summary.keys():
        '''
        Example of stamp redeemed_summary
        redeemed_summary: {
            stamp: {
                amount: 2,
                customer_stamp_rewards: [
                    {
                    key: "ag50cmV4LWFkbWluLWRldnJGCxIEVXNlchiAgIC4y6nFCAwLEghDdXN0b21lchiAgICE3I-JCQwLEhNDdXN0b21lclN0YW1wUmV3YXJkGICAgNjfrZAJDA",
                    redeemed_amount: 2
                    }
                ]
            }
        },
        '''
        redeemed_details_list   = redeemed_summary.get(program_conf.REWARD_FORMAT_STAMP).get('customer_stamp_rewards')
        
        for redeemed_details in redeemed_details_list:
            customer_stamp_reward = CustomerStampReward.fetch(redeemed_details.get('key'))
            redeemed_amount = redeemed_details.get('amount')
            customer_stamp_reward.update_used_reward_amount( -redeemed_amount )
            
            customer.reward_summary[program_conf.REWARD_FORMAT_STAMP]['amount'] += redeemed_amount
        
        customer.put()
        
    if program_conf.REWARD_FORMAT_PREPAID in redeemed_summary.keys(): 
        #found voucher have been redeem in the transaction
        '''
        Example of prepaid redeemed_summary
        redeemed_summary: {
            prepaid: {
                amount: 25,
                customer_prepaid_reward: [
                {
                    key: "ag50cmV4LWFkbWluLWRldnJICxIEVXNlchiAgIC4y6nFCAwLEghDdXN0b21lchiAgICE3I-JCQwLEhVDdXN0b21lclByZXBhaWRSZXdhcmQYgICAmP-6lAoM",
                    redeemed_amount: 25,
                    }
                ]
            }
        },
        '''
        redeemed_details_list   = redeemed_summary.get(program_conf.REWARD_FORMAT_PREPAID).get('customer_prepaid_rewards')
        
        for redeemed_details in redeemed_details_list:
            customer_prepaid_reward = CustomerPrepaidReward.fetch(redeemed_details.get('key'))
            if customer_prepaid_reward:
                redeemed_amount = redeemed_details.get('amount')
                customer_prepaid_reward.update_used_reward_amount( -redeemed_amount )
                
                customer.prepaid_summary['amount'] += redeemed_amount
        
        customer.put()
        
    redemption_details.revert(reverted_by, reverted_datetime=reverted_datetime)
    
    
    create_merchant_customer_redemption_reverted_upstream_for_merchant(redemption_details)
    
        

        