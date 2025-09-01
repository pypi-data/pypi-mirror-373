'''
Created on 29 Nov 2023

@author: jacklok
'''
from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel
from google.cloud import ndb
from trexmodel.models.datastore.merchant_models import MerchantAcct, Outlet
from trexmodel.models.datastore.user_models import User
from trexconf import conf
from datetime import datetime, timedelta
import logging
from trexmodel.models.datastore.transaction_models import CustomerTransaction
from trexmodel.models.datastore.model_decorators import model_transactional
from trexlib.utils.common.date_util import convert_date_to_datetime

#logger = logging.getLogger('model')
logger = logging.getLogger('target_debug')

class RatingBase(BaseNModel, DictModel):
    user_acct                           = ndb.KeyProperty(name="user_acct", kind=User)
    modified_datetime                   = ndb.DateTimeProperty(required=True, auto_now=True)
    updated                             = ndb.BooleanProperty(required=True, default=False)
    score                               = ndb.FloatProperty(required=False, default=.0)
    rating_result                        = ndb.JsonProperty()
    previous_rating_result               = ndb.JsonProperty()

class TransactionRating(RatingBase):
    outlet                              = ndb.KeyProperty(name="outlet", kind=Outlet)
    merchant_acct                       = ndb.KeyProperty(name="merchant_acct", kind=MerchantAcct)
    transaction_id                      = ndb.StringProperty(required=True)
    industry                            = ndb.StringProperty(required=False, default="fb")
    
    remarks                             = ndb.StringProperty(required=False)
    
    created_datetime                    = ndb.DateTimeProperty(required=True, auto_now_add=True)
    
    dict_properties         = ['transaction_id','rating_result', 'remarks', 'industry', 'score', 'created_datetime',
                               ]
    
    @property
    def merchant_acct_entity(self):
        return self.merchant_acct.get()
    
    @property
    def user_acct_key(self):
        return self.user_acct.urlsafe().decode('utf-8')
    
    @staticmethod
    def list_transaction_by_date(enquiry_date, outlet=None,  offset=0, limit=conf.PAGINATION_SIZE, return_with_cursor=False, start_cursor=None):
        start_datetime  = convert_date_to_datetime(enquiry_date)
        end_datetime    = start_datetime + timedelta(days=1)
        query = TransactionRating.query(
                        ndb.AND(
                            TransactionRating.outlet==outlet.create_ndb_key(),
                            TransactionRating.created_datetime>=start_datetime,
                            TransactionRating.created_datetime<end_datetime,
                        ))
        if return_with_cursor:
            (result, next_cursor) = TransactionRating.list_all_with_condition_query(query, order_by=TransactionRating.created_datetime, start_cursor=start_cursor, return_with_cursor=True, limit=limit)
        
            return (result, next_cursor)
        else:
            return query.order(TransactionRating.created_datetime).fetch(offset=offset, limit=limit)
    
    @staticmethod
    @model_transactional(desc="update rating changes")
    def create(user_acct, transaction_id, rating_result={}, 
               remarks=None, for_testing=False, rating_datetime=None):
        logger.info('---TransactionRating.create---')
        customer_transaction = CustomerTransaction.get_by_transaction_id(transaction_id)
        
        logger.info('customer_transaction=%s', customer_transaction)
        logger.info('for_testing=%s', for_testing)
        
        if customer_transaction is not None:
            outlet         = customer_transaction.transact_outlet_entity
            merchant_acct  = customer_transaction.transact_merchant_acct
        
            transaction_rating = TransactionRating.get_by_transaction_id(transaction_id)
            
            logger.info('transaction_rating=%s', transaction_rating)
            to_update_rating = False
            
            if transaction_rating is None:
                transaction_rating       = TransactionRating(
                                                user_acct               = user_acct.create_ndb_key(),
                                                merchant_acct           = merchant_acct.create_ndb_key(),
                                                outlet                  = outlet.create_ndb_key(),
                                                transaction_id          = transaction_id,
                                                industry                = merchant_acct.industry,
                                                rating_result           = rating_result,
                                                remarks                 = remarks,
                                                modified_datetime       = rating_datetime,
                                                
                                                )
                to_update_rating = True
            else:
                
                logger.debug('Going to check whether the rating have been changed')
                previous_rating_result = transaction_rating.previous_rating_result or {}
                
                for rating_type, rating_value in rating_result.items():
                    previous_rating_value = previous_rating_result.get(rating_type,0)
                    if previous_rating_value!=rating_value:
                        to_update_rating = True
                        break
                        
                if to_update_rating:
                    transaction_rating.previous_rating_result   = transaction_rating.rating_result
                    transaction_rating.rating_result            = rating_result
                    transaction_rating.remarks                  = remarks
                    transaction_rating.modified_datetime        = rating_datetime
                
            if for_testing==False:
                if to_update_rating:
                    
                    score = .0
                    
                    for rating_value in rating_result.values():
                        score +=rating_value
                    
                    score = score/len(rating_result)
                    
                    logger.info('Going to update rating for the changes')
                    transaction_rating.score = score
                    transaction_rating.put()
                
                    outlet_rating = OutletRating.update_by_transaction_rating(user_acct, outlet, 
                                            merchant_acct, transaction_rating)
                    
                    to_update = outlet_rating.to_update
                    
                    logger.info('outlet_rating.to_update=%s', to_update)
                    
                    if to_update:
                        outlet_rating_result = OutletRatingResult.update_by_outlet_rating(outlet, outlet_rating)
                        MerchantRatingResult.update_by_outlet_rating_result(merchant_acct, outlet_rating_result)
                else:
                    logger.info('ignore the rating changes because there is no changes indeed')
    
    @staticmethod
    def get_by_transaction_id(transaction_id):
        return TransactionRating.query(ndb.AND(TransactionRating.transaction_id==transaction_id)).get()    

class OutletRating(RatingBase):
    '''
    ancestor = merchant_acct
    '''
    
    outlet                              = ndb.KeyProperty(name="outlet", kind=Outlet)
    merchant_acct                       = ndb.KeyProperty(name="merchant_acct", kind=MerchantAcct)
    
    dict_properties         = ['rating_result', 'previous_rating_result', 'score',
                               ]
    
    @staticmethod
    def get_user_rating_by_outlet(user_acct, outlet):
        return OutletRating.query(ndb.AND(OutletRating.user_acct==user_acct.create_ndb_key(), OutletRating.outlet==outlet.create_ndb_key())).get()
    
    @staticmethod
    def list_by_outlet(outlet):
        return OutletRating.query(ndb.AND(OutletRating.outlet==outlet.create_ndb_key())).fetch(limit=conf.MAX_FETCH_RECORD)
    
    @staticmethod
    def list_new_rating_by_outlet(outlet, checking_datetime_from=None):
        #return OutletRating.query(ndb.AND(OutletRating.outlet==outlet.create_ndb_key(), OutletRating.updated==False, OutletRating.modified_datetime>checking_datetime_from)).fetch(limit=conf.MAX_FETCH_RECORD)
        return OutletRating.query(ndb.AND(OutletRating.outlet==outlet.create_ndb_key(), OutletRating.updated==False)).fetch(limit=conf.MAX_FETCH_RECORD)
    
    @staticmethod
    def list_updated_rating_by_outlet(outlet, checking_datetime_from=None):
        #return OutletRating.query(ndb.AND(OutletRating.outlet==outlet.create_ndb_key(), OutletRating.updated==True, OutletRating.modified_datetime>checking_datetime_from)).fetch(limit=conf.MAX_FETCH_RECORD)
        return OutletRating.query(ndb.AND(OutletRating.outlet==outlet.create_ndb_key(), OutletRating.updated==True, )).fetch(limit=conf.MAX_FETCH_RECORD)
    
    @staticmethod
    def list_by_merchant(merchant_acct):
        return OutletRating.query(ancestor=merchant_acct.create_ndb_key()).fetch(limit=conf.MAX_FETCH_RECORD)
    
    @staticmethod
    def list_new_rating_by_merchant(merchant_acct, checking_datetime_from=None):
        #return OutletRating.query(ndb.AND(OutletRating.updated==False, OutletRating.modified_datetime>checking_datetime_from), ancestor=merchant_acct.create_ndb_key()).fetch(limit=conf.MAX_FETCH_RECORD)
        return OutletRating.query(ndb.AND(OutletRating.updated==False, ), ancestor=merchant_acct.create_ndb_key()).fetch(limit=conf.MAX_FETCH_RECORD)
    
    @staticmethod
    def list_updated_rating_by_merchant(merchant_acct, checking_datetime_from=None):
        #return OutletRating.query(ndb.AND(OutletRating.updated==True, OutletRating.modified_datetime>checking_datetime_from), ancestor=merchant_acct.create_ndb_key()).fetch(limit=conf.MAX_FETCH_RECORD)
        return OutletRating.query(ndb.AND(OutletRating.updated==True, ), ancestor=merchant_acct.create_ndb_key()).fetch(limit=conf.MAX_FETCH_RECORD)
    
    @staticmethod
    def create(user_acct, outlet, merchant_acct=None, rating_result={}, rating_datetime=None):
        logger.info('---OutletRating.create---')
        outlet_rating = OutletRating.get_user_rating_by_outlet(user_acct, outlet)
        to_update = False
        if outlet_rating is None:
            logger.info('outlet_rating is None')
            if merchant_acct is None:
                merchant_acct   = outlet.merchant_acct_entity
            outlet_rating       = OutletRating(
                                    user_acct               = user_acct.create_ndb_key(),
                                    merchant_acct           = merchant_acct.create_ndb_key(),
                                    outlet                  = outlet.create_ndb_key(),
                                    rating_result           = rating_result,
                                    previous_rating_result  = {},
                                    modified_datetime       = rating_datetime,
                                    
                                    )
            to_update = True
            
        else:
            logger.info('Found outlet_rating')
            
            for rating_type, rating_value in rating_result.items():
                previous_rating_value = outlet_rating.rating_result.get(rating_type, 0)
                if previous_rating_value!=rating_value:
                    logger.info('Found rating change where %s from %s to %s', rating_type, previous_rating_value, rating_value)
                    to_update = True
            
            if to_update:
                outlet_rating.rating_result             = rating_result
                outlet_rating.previous_rating_result    = outlet_rating.rating_result
                outlet_rating.modified_datetime         = rating_datetime
            
            
        logger.info('Update outlet to_update=%s, rating with %s', to_update, rating_result)
        
        if to_update:
            outlet_rating.updated = not to_update
            outlet_rating.put()
            
        new_created_rating_result_list = OutletRating.list_new_rating_by_outlet(outlet)
        
        logger.info('new_created_rating_result_list=%s', new_created_rating_result_list)
        
    @staticmethod
    def update_by_transaction_rating(user_acct, outlet, merchant_acct, transaction_rating):
        logger.info('---OutletRating.update_by_transaction_rating---')
        rating_datetime = transaction_rating.modified_datetime
        rating_result   = transaction_rating.rating_result
        
        outlet_rating = OutletRating.get_user_rating_by_outlet(user_acct, outlet)
        to_update                       = False
        existing_rating_result_found    = False
        
        if outlet_rating is None:
            logger.info('outlet_rating is None')
            if merchant_acct is None:
                merchant_acct   = outlet.merchant_acct_entity
            outlet_rating       = OutletRating(
                                    user_acct               = user_acct.create_ndb_key(),
                                    merchant_acct           = merchant_acct.create_ndb_key(),
                                    outlet                  = outlet.create_ndb_key(),
                                    rating_result           = rating_result,
                                    previous_rating_result  = {},
                                    modified_datetime       = rating_datetime,
                                    
                                    )
            to_update                       = True
            
            
        else:
            logger.info('Found outlet_rating')
            
            for rating_type, rating_value in rating_result.items():
                previous_rating_value = outlet_rating.rating_result.get(rating_type, 0)
                if previous_rating_value!=rating_value:
                    logger.info('Found rating change where %s from %s to %s', rating_type, previous_rating_value, rating_value)
                    to_update = True
            
            if to_update:
                outlet_rating.previous_rating_result    = outlet_rating.rating_result
                outlet_rating.rating_result             = rating_result
                outlet_rating.modified_datetime         = rating_datetime
            
            existing_rating_result_found    = True
            
            
        logger.info('Update outlet to_update=%s, rating with %s', to_update, rating_result)
        
        if to_update:
            outlet_rating.to_update     = to_update
            outlet_rating.updated       = not to_update
            outlet_rating.is_new_rating = not existing_rating_result_found
            outlet_rating.put()
            
            logger.info('outlet_rating.is_new_rating=%s', outlet_rating.is_new_rating)
            
        return outlet_rating
        
    @staticmethod
    def update(user_acct, outlet, rating_result={}):
        
        outlet_rating = OutletRating.get_user_rating_by_outlet(user_acct, outlet)
        if outlet_rating:
            outlet_rating.previous_rating_result    = outlet_rating.rating_result
            
            outlet_rating.rating_result             = rating_result
            
            outlet_rating.put()    
    
    @staticmethod
    def __calculate_rating(rating_list):
        
        total_rating_count  = len(rating_list)
        final_rating_details = {}
        
        for r in rating_list:
            for rating_type, rating_value in r.items():
                total_rating = final_rating_details.get(rating_type, 0)
                total_rating += rating_value
                final_rating_details[rating_type] = total_rating
        
        for rating_type, rating_value in final_rating_details.items():
            average_rating = final_rating_details[rating_type]/ total_rating_count
            final_rating_details[rating_type] = average_rating
            logger.debug('%s=%s', rating_type, average_rating)
            
        
        
        return final_rating_details
    
    @staticmethod    
    def get_outlet_rating(outlet):
        outlet_rating_list = OutletRating.list_by_outlet(outlet)
        
        return OutletRating.__calculate_rating(outlet_rating_list)
    
    @staticmethod    
    def get_merchant_rating(merchant_acct):
        merchant_rating_list = OutletRating.list_by_outlet(merchant_acct)
        
        return OutletRating.__calculate_rating(merchant_rating_list)

            
class RatingResult(BaseNModel, DictModel):
    total_rating_count      = ndb.IntegerProperty(required=True, default=0)
    rating_result           = ndb.JsonProperty()
    previous_rating_result  = ndb.JsonProperty()
    score                   = ndb.FloatProperty(required=False, default=.0)
    modified_datetime       = ndb.DateTimeProperty(required=True, auto_now=True)
    

class OutletRatingResult(RatingResult):
    outlet                  = ndb.KeyProperty(name="outlet", kind=Outlet)
    
    
    dict_properties         = ['total_rating_count', 'rating_result', 'previous_rating_result', 'modified_datetime', 'outlet_key']
    
    @property
    def outlet_key(self):
        return self.outlet.urlsafe().decode('utf-8')
    
    @staticmethod
    def get_by_outlet(outlet):
        return OutletRatingResult.query(ndb.AND(OutletRatingResult.outlet==outlet.create_ndb_key())).get()
    
    @staticmethod
    def list_by_merchant_acct(merchant_acct):
        return OutletRatingResult.query(ancestor=merchant_acct.create_ndb_key()).fetch(limit=conf.MAX_FETCH_RECORD)
    
    @staticmethod
    def list_new_rating_by_merchant_acct(merchant_acct):
        return OutletRatingResult.query(ndb.AND(OutletRatingResult.updated==False), ancestor=merchant_acct.create_ndb_key()).fetch(limit=conf.MAX_FETCH_RECORD)
    
    @staticmethod
    def list_updated_rating_by_merchant_acct(merchant_acct):
        return OutletRatingResult.query(ndb.AND(OutletRatingResult.updated==True), ancestor=merchant_acct.create_ndb_key()).fetch(limit=conf.MAX_FETCH_RECORD)
    
    @staticmethod
    def update_by_outlet_rating(outlet, outlet_rating):
        logger.info('---OutletRatingResult.update_by_outlet_rating---, outlet_rating=%s', outlet_rating)
        
        merchant_acct               = outlet.merchant_acct_entity
        outlet_rating_result        = OutletRatingResult.get_by_outlet(outlet)
        existing_rating_result      = {}
        existing_total_rating_count = 0
        existing_rating_result_found= False
        rating_datetime             = outlet_rating.modified_datetime
        
        if outlet_rating_result is None:
            logger.info('outlet_rating result is None')
            outlet_rating_result = OutletRatingResult(
                                        parent = merchant_acct.create_ndb_key(),
                                        outlet = outlet.create_ndb_key(),
                                        modified_datetime = rating_datetime,
                                        )
            
            
            existing_total_rating_count = 0
            
            
        else:
            logger.info('Found outlet_rating result')
            existing_rating_result      = outlet_rating_result.rating_result
            existing_total_rating_count = outlet_rating_result.total_rating_count
            
            existing_rating_result_found = True
        
        total_new_rating_count      = 1
        
        
        new_rating_result                    = {}
        existing_rating_result_changed_count = 0
        
        logger.info('outlet_rating.rating_result=%s', outlet_rating.rating_result)
        logger.info('outlet_rating.is_new_rating=%s', outlet_rating.is_new_rating)
        
        for rating_type, rating_value in outlet_rating.rating_result.items():
            
            if existing_rating_result_found:
                if outlet_rating.is_new_rating==False:
                    #only check for rating different for existing rating
                    previous_rating_value   = outlet_rating.previous_rating_result.get(rating_type, 0)
                    rating_value_difference = rating_value - outlet_rating.previous_rating_result.get(rating_type, 0)
                    
                    logger.info('rating_type=%s, rating_value=%s, previous_rating_value=%s', rating_type, rating_value, previous_rating_value)
                    
                else:
                    #use new rating if it is new rating
                    rating_value_difference = rating_value
                    logger.info('rating_type=%s, rating_value=%s', rating_type, rating_value)
                
            else:
                rating_value_difference = rating_value
            
            logger.info('rating_type=%s, rating_value_difference=%s', rating_type, rating_value_difference)
                 
            new_rating_result[rating_type] = rating_value_difference
        
        #here to determine the outlet rating is new added outlet rating
        if outlet_rating.is_new_rating==False:
            outlet_rating_result.new_added_outlet_rating = False
        else:
            outlet_rating_result.new_added_outlet_rating = True
        
        if existing_rating_result_found:
            logger.debug('Going to add existing rating result change counter')
            if outlet_rating.is_new_rating==False:
                existing_rating_result_changed_count+=1
                
        
        logger.info('new_rating_result=%s', new_rating_result)
        
        updated_rating_result = {}
        
        if existing_rating_result_found:
            for rating_type, rating_value in existing_rating_result.items():
                updated_rating_result[rating_type] = rating_value * existing_total_rating_count
            
        logger.info('updated_rating_result=%s', updated_rating_result)
        
            
        latest_rating_result = {}
        
        total_rating_count = existing_total_rating_count + total_new_rating_count  - existing_rating_result_changed_count
        logger.info('total_rating_count=%s', total_rating_count)
        
        
        for rating_type, rating_value in new_rating_result.items():
            latest_rating_result[rating_type] = (rating_value + updated_rating_result.get(rating_type, 0))/total_rating_count
        
        logger.info('latest_rating_result=%s', latest_rating_result)
        
        score=0
        for rating_value in latest_rating_result.values():
            score+=rating_value
        
        if score>0:
            score = score/len(latest_rating_result)
        
        
        outlet_rating_result.total_rating_count     = total_rating_count
        outlet_rating_result.previous_rating_result = outlet_rating_result.rating_result
        outlet_rating_result.rating_result          = latest_rating_result
        
        outlet_rating_result.score                  = score
        outlet_rating_result.modified_datetime      = rating_datetime
        outlet_rating_result.updated                = False
        outlet_rating_result.is_new_rating          = not existing_rating_result_found
        outlet_rating_result.put()
        
        logger.info('outlet_rating_result.is_new_rating=%s', outlet_rating_result.is_new_rating)
        
        return outlet_rating_result
    
    @staticmethod
    def update(outlet, updated_datetime_from=None, rating_datetime=None):
        logger.info('---OutletRatingResult.update---')
        merchant_acct               = outlet.merchant_acct_entity
        outlet_rating_result        = OutletRatingResult.get_by_outlet(outlet)
        existing_rating_result      = {}
        existing_total_rating_count = 0
        existing_rating_result_found= False
        
        if outlet_rating_result is None:
            logger.info('outlet_rating result is None')
            outlet_rating_result = OutletRatingResult(
                                        parent = merchant_acct.create_ndb_key(),
                                        outlet = outlet.create_ndb_key(),
                                        modified_datetime = rating_datetime,
                                        )
            
            
            existing_total_rating_count = 0
            updated_datetime_from       = outlet.created_datetime
            
            
        else:
            logger.info('Found outlet_rating result')
            existing_rating_result      = outlet_rating_result.rating_result
            existing_total_rating_count = outlet_rating_result.total_rating_count
            updated_datetime_from       = outlet_rating_result.modified_datetime
            
            existing_rating_result_found = True
        
        new_rating_list             = []
        if existing_rating_result_found==False:
            logger.info('no outlet rating result has found, thus going to read all outlet rating')
            new_rating_list = OutletRating.list_by_outlet(outlet)
        else:
            logger.info('going to read new rating result from last updated datetime=%s', updated_datetime_from)
            
            new_rating_list = OutletRating.list_new_rating_by_outlet(outlet, updated_datetime_from)
        
        total_new_rating_count      = len(new_rating_list)
        
        logger.info('new_rating_list=%s', new_rating_list)
        logger.info('total_new_rating_count=%s', total_new_rating_count)
        
        new_rating_result                    = {}
        existing_rating_result_changed_count = 0
        
        if total_new_rating_count>0:
            logger.info('going to accumulate new rating result')
            for r in new_rating_list:
                for rating_type, rating_value in r.rating_result.items():
                    total_rating = new_rating_result.get(rating_type, 0)
                    is_existing_result_changed = len(r.previous_rating_result)!=0 if r.previous_rating_result is not None else False
                    
                    if existing_rating_result_found:
                        rating_value_difference = rating_value - r.previous_rating_result.get(rating_type, 0)
                        logger.debug('rating_value_difference = %s-%s', rating_value, r.previous_rating_result.get(rating_type, 0))
                        
                    else:
                        rating_value_difference = rating_value
                        logger.debug('rating_value_difference = %s', new_rating_result.get(rating_type, 0),) 
                    
                    total_rating += rating_value_difference
                    new_rating_result[rating_type] = total_rating
                    
                    if existing_rating_result_found:
                        logger.debug('Going to add existing rating result change counter')
                        if is_existing_result_changed:
                            existing_rating_result_changed_count+=1
        else:
            logger.info('no new rating result')
            
        logger.info('new_rating_result=%s', new_rating_result)
        
        updated_rating_result = {}
        
        if existing_rating_result_found:
            for rating_type, rating_value in existing_rating_result.items():
                updated_rating_result[rating_type] = rating_value * existing_total_rating_count
            
        '''
        else:
            updated_rating_list         = OutletRating.list_updated_rating_by_outlet(outlet, updated_datetime_from)
            total_updated_rating_count  = len(updated_rating_list)
            
            logger.info('updated_rating_list=%s', updated_rating_list)
            logger.info('total_updated_rating_count=%s', total_updated_rating_count)
            
            if total_updated_rating_count>0:
                for r in updated_rating_list:
                    for rating_type, rating_value in r.rating_result.items():
                        total_rating_value = updated_rating_result.get(rating_type, 0)
                        total_rating_value+= rating_value
                        updated_rating_result[rating_type] = total_rating_value
                
        '''
                
        logger.info('updated_rating_result=%s', updated_rating_result)
        
            
        latest_rating_result = {}
        
        total_rating_count = existing_total_rating_count + total_new_rating_count  - existing_rating_result_changed_count
        
        if new_rating_result: 
            for rating_type, rating_value in new_rating_result.items():
                latest_rating_result[rating_type] = (rating_value + updated_rating_result.get(rating_type, 0))/total_rating_count
        else:
            for rating_type, rating_value in updated_rating_result.items():
                latest_rating_result[rating_type] = (rating_value)/total_rating_count
            
        logger.info('latest_rating_result=%s', latest_rating_result)
        
        score=0
        for rating_value in latest_rating_result.values():
            score+=rating_value
        
        if score>0:
            score = score/len(latest_rating_result)
        
        logger.info('score=%s', score)
        
        outlet_rating_result.total_rating_count     = total_rating_count
        outlet_rating_result.previous_rating_result = outlet_rating_result.rating_result
        outlet_rating_result.rating_result          = latest_rating_result
        
        outlet_rating_result.score                  = score
        outlet_rating_result.modified_datetime      = rating_datetime
        outlet_rating_result.updated                = False
        
        outlet_rating_result.put()
    
class MerchantRatingResult(RatingResult):
    merchant_acct           = ndb.KeyProperty(name="merchant_acct", kind=MerchantAcct)
    
    
    dict_properties         = ['total_rating_count', 'rating_result', 'modified_datetime',]
    
    @staticmethod
    def get_by_merchant_acct(merchant_acct):
        return MerchantRatingResult.query(ndb.AND(MerchantRatingResult.merchant_acct==merchant_acct.create_ndb_key())).get()
    
    @staticmethod
    def update_by_outlet_rating_result(merchant_acct, outlet_rating_result):
        logger.info('---MerchantRatingResult.update_by_outlet_rating_result---')
        merchant_rating_result          = MerchantRatingResult.get_by_merchant_acct(merchant_acct)
        existing_rating_result          = {}
        existing_total_rating_count     = 0
        existing_rating_result_found    = False
        rating_datetime                 = outlet_rating_result.modified_datetime
        
        if merchant_rating_result:
            merchant_rating_result.modified_datetime = rating_datetime
            existing_rating_result          = merchant_rating_result.rating_result
            existing_total_rating_count     = merchant_rating_result.total_rating_count
            existing_rating_result_found    = True
            logger.info('Found existing merchant rating result')
            logger.info('merchant_rating_result=%s', merchant_rating_result)
            
        else:
            merchant_rating_result = MerchantRatingResult(
                                        merchant_acct       = merchant_acct.create_ndb_key(),
                                        modified_datetime   = rating_datetime,
                                )
            logger.info('Existing merchant rating result is not found')
        
        
        
        total_new_rating_count                  = 1
        new_rating_result                       = {}
        existing_rating_result_changed_count    = 0
        
        logger.info('outlet_rating_result.is_new_rating=%s', outlet_rating_result.is_new_rating)
        logger.info('outlet_rating_result.new_added_outlet_rating=%s', outlet_rating_result.new_added_outlet_rating)
        
        for rating_type, rating_value in outlet_rating_result.rating_result.items():
            
            if existing_rating_result_found:
                if outlet_rating_result.is_new_rating or outlet_rating_result.new_added_outlet_rating:
                    rating_value_difference = rating_value
                else:
                    rating_value_difference = rating_value - outlet_rating_result.previous_rating_result.get(rating_type, 0)
                    logger.debug('%s rating_value_difference = %s-%s', rating_type, rating_value, outlet_rating_result.previous_rating_result.get(rating_type, 0))
            else:
                rating_value_difference = rating_value
                logger.debug('%s rating_value_difference = %s', rating_type, rating_value_difference,) 
            
            new_rating_result[rating_type] = rating_value_difference
            
        if existing_rating_result_found:
            logger.debug('Going to add existing rating result change counter')
            if outlet_rating_result.is_new_rating == False:
                if outlet_rating_result.new_added_outlet_rating==True:
                    logger.info('this is existing outlet rating result, but new outlet rating is added.')
                else:
                    logger.info('this is existing outlet rating result changes')
                    existing_rating_result_changed_count+=1
            else:
                logger.info('this is new outlet rating result')
                
        logger.info('new_rating_result=%s', new_rating_result)
        
        updated_rating_result = {}
        logger.info('existing_total_rating_count=%s', existing_total_rating_count)
        if existing_rating_result_found:
            for rating_type, rating_value in existing_rating_result.items():
                updated_rating_result[rating_type] = rating_value * existing_total_rating_count
                
        logger.info('updated_rating_result=%s', updated_rating_result)
        latest_rating_result = {}
        
        total_rating_count = existing_total_rating_count + total_new_rating_count  - existing_rating_result_changed_count
        logger.info('existing_total_rating_count=%s', existing_total_rating_count)
        logger.info('existing_rating_result_changed_count=%s', existing_rating_result_changed_count)
        logger.info('total_rating_count=%s', total_rating_count)
        
        if new_rating_result: 
            for rating_type, rating_value in new_rating_result.items():
                latest_rating_result[rating_type] = (rating_value + updated_rating_result.get(rating_type, 0))/total_rating_count
        else:
            for rating_type, rating_value in updated_rating_result.items():
                latest_rating_result[rating_type] = (rating_value)/total_rating_count
            
        logger.info('latest_rating_result=%s', latest_rating_result)
        
        score=0
        for rating_value in latest_rating_result.values():
            score+=rating_value
        
        if score>0:
            score = score/len(latest_rating_result)
        
        logger.info('score=%s', score)
        
        merchant_rating_result.total_rating_count     = total_rating_count
        merchant_rating_result.previous_rating_result = merchant_rating_result.rating_result
        merchant_rating_result.rating_result          = latest_rating_result
        
        merchant_rating_result.score                  = score
        merchant_rating_result.modified_datetime      = rating_datetime
        merchant_rating_result.updated                = False
        merchant_rating_result.is_new_rating          = not existing_rating_result_found
        
        merchant_rating_result.put()
        
        return merchant_rating_result 
    
    @staticmethod
    def update(merchant_acct, rating_datetime=None):
        logger.info('---MerchantRatingResult.update---')
        merchant_rating_result          = MerchantRatingResult.get_by_merchant_acct(merchant_acct)
        existing_rating_result          = {}
        existing_total_rating_count     = 0
        existing_rating_result_found    = False
        
        if merchant_rating_result:
            merchant_rating_result.modified_datetime = rating_datetime
            existing_rating_result          = merchant_rating_result.rating_result
            existing_total_rating_count     = merchant_rating_result.total_rating_count
            existing_rating_result_found    = True
            logger.info('Found existing merchant rating result')
            
        else:
            merchant_rating_result = MerchantRatingResult(
                                        merchant_acct       = merchant_acct.create_ndb_key(),
                                        modified_datetime   = rating_datetime,
                                )
            logger.info('Existing merchant rating result is not found')
        
        if existing_rating_result_found:
            new_rating_list = OutletRatingResult.list_new_rating_by_merchant_acct(merchant_acct)
        else:
            new_rating_list = OutletRatingResult.list_by_merchant_acct(merchant_acct)
        
        total_new_rating_count      = len(new_rating_list)
        
        logger.info('new_rating_list=%s', new_rating_list)
        logger.info('total_new_rating_count=%s', total_new_rating_count)
        
        new_rating_result                       = {}
        existing_rating_result_changed_count    = 0
        
        if total_new_rating_count>0:
            for r in new_rating_list:
                for rating_type, rating_value in r.rating_result.items():
                    total_rating = new_rating_result.get(rating_type, 0)
                    
                    is_existing_result_changed = len(r.previous_rating_result)!=0 if r.previous_rating_result is not None else False
                    
                    if existing_rating_result_found:
                        rating_value_difference = rating_value - r.previous_rating_result.get(rating_type, 0)
                        logger.debug('rating_value_difference = %s-%s', rating_value, r.previous_rating_result.get(rating_type, 0))
                        
                    else:
                        rating_value_difference = rating_value
                        logger.debug('rating_value_difference = %s', new_rating_result.get(rating_type, 0),) 
                    
                    total_rating += rating_value_difference
                    new_rating_result[rating_type] = total_rating
                    
                    if existing_rating_result_found:
                        logger.debug('Going to add existing rating result change counter')
                        if is_existing_result_changed:
                            existing_rating_result_changed_count+=1
                    
        logger.info('new_rating_result=%s', new_rating_result)
        
        updated_rating_result = {}
        
        if existing_rating_result_found:
            for rating_type, rating_value in existing_rating_result.items():
                updated_rating_result[rating_type] = rating_value * existing_total_rating_count
                
        
        latest_rating_result = {}
        
        total_rating_count = existing_total_rating_count + total_new_rating_count  - existing_rating_result_changed_count
        
        if new_rating_result: 
            for rating_type, rating_value in new_rating_result.items():
                latest_rating_result[rating_type] = (rating_value + updated_rating_result.get(rating_type, 0))/total_rating_count
        else:
            for rating_type, rating_value in updated_rating_result.items():
                latest_rating_result[rating_type] = (rating_value)/total_rating_count
            
        logger.info('latest_rating_result=%s', latest_rating_result)
        
        score=0
        for rating_value in latest_rating_result.values():
            score+=rating_value
        
        if score>0:
            score = score/len(latest_rating_result)
        
        
        merchant_rating_result.total_rating_count     = total_rating_count
        merchant_rating_result.previous_rating_result = merchant_rating_result.rating_result
        merchant_rating_result.rating_result          = latest_rating_result
        
        merchant_rating_result.score                  = score
        merchant_rating_result.modified_datetime      = rating_datetime
        merchant_rating_result.updated                = False
        
        merchant_rating_result.put() 
        
    
    '''
    @staticmethod
    def update(merchant_acct, updated_datetime_from=None, rating_datetime=None):
        
        logger.info('updated_datetime_from=%s', updated_datetime_from)
        
        merchant_rating_result = MerchantRatingResult.query(ndb.AND(MerchantRatingResult.merchant_acct==merchant_acct.create_ndb_key())).get()
        existing_total_rating_count = 0
        #if updated_datetime_from is None:
        #    updated_datetime_from = datetime.utcnow() - timedelta(days=1)
        is_new_rating_result    = False
        
        if merchant_rating_result is None:
            logger.info('merchant_rating_result is None')
            merchant_rating_result = MerchantRatingResult(
                                        merchant_acct = merchant_acct.create_ndb_key(),
                                        )
            rating_result = {
                            'reviews_details':{}
                            }
            
            is_new_rating_result = True
            
            if updated_datetime_from is None:
                updated_datetime_from = merchant_acct.registered_datetime
            
        else:
            logger.info('Found merchant_rating_result')
            rating_result               = merchant_rating_result.rating_result
            existing_total_rating_count = merchant_rating_result.total_rating_count
            
            if updated_datetime_from is None:
                updated_datetime_from = merchant_rating_result.modified_datetime
        
        logger.info('rating_result=%s', rating_result)
        
        logger.info('updated_datetime_from=%s', updated_datetime_from)
        
        new_rating_list             = OutletRating.list_new_rating_by_merchant(merchant_acct, updated_datetime_from)
        updated_rating_list         = OutletRating.list_updated_rating_by_merchant(merchant_acct, updated_datetime_from)
        
        logger.info('new_rating_list=%s', new_rating_list)
        logger.info('updated_rating_list=%s', updated_rating_list)
        
        total_new_rating_count      = len(new_rating_list)
        total_updated_rating_count  = len(updated_rating_list)
        
        logger.info('total_new_rating_count=%s', total_new_rating_count)
        logger.info('total_updated_rating_count=%s', total_updated_rating_count)
        logger.info('existing_total_rating_count=%s', existing_total_rating_count)
        
        new_rating_result = {}
        
        for r in new_rating_list:
            logger.info('r.rating_result=%s', r.rating_result)
            for rating_type, rating_value in r.rating_result.items():
                if rating_type!='remarks':
                    logger.debug('rating_type=%s, rating_value=%s', rating_type, rating_value)
                    total_rating_value = new_rating_result.get(rating_type, 0)
                    logger.debug('total_rating_value=%s', total_rating_value)
                    total_rating_value += rating_value
                    new_rating_result[rating_type] =  total_rating_value
            
            #mark new rating have been updated
            r.updated = True
        
        ndb.put_multi(new_rating_list)    
        
        for rating_type, rating_value in new_rating_result.items():
            logger.info('new %s=%s', rating_type, rating_value)
        
        updated_rating_result = {}
        
        for rating_type, rating_value in rating_result.get('reviews_details').items():
            if rating_type!='remarks':
                updated_rating_result[rating_type] = rating_value * existing_total_rating_count
                
                logger.info('updated %s b4=%s', rating_type, rating_value)
        
        
        for r in updated_rating_list:
            logger.debug('updated rating = %s', r)
            for rating_type, rating_value in r.rating_result.items():
                if rating_type!='remarks':
                    if is_new_rating_result:
                        updated_rating_value = updated_rating_result.get(rating_type, 0)
                        updated_rating_value += rating_value
                        updated_rating_result[rating_type] = updated_rating_value
                        
                    else:
                        updated_rating_value += (r.rating_result.get(rating_type,0) - r.previous_rating_result.get(rating_type,0))
                        updated_rating_result[rating_type] = updated_rating_value
        
        for rating_type, rating_value in  updated_rating_result.items():
            logger.info('%s after=%s', rating_type, rating_value)
        
        
        latest_rating_result = {}
        
        if is_new_rating_result:
            for rating_type, rating_value in new_rating_result.items():
                if rating_type!='remarks':
                    latest_rating_result[rating_type] = (rating_value +  updated_rating_result.get(0)) / (total_updated_rating_count + total_new_rating_count)
            
            merchant_rating_result.total_rating_count = total_updated_rating_count + total_new_rating_count
            
        else:
            
            for rating_type, rating_value in new_rating_result.items():
                if rating_type!='remarks':
                    latest_rating_result[rating_type] = (rating_value +  updated_rating_result.get(0)) / (existing_total_rating_count + total_new_rating_count)
                
            merchant_rating_result.total_rating_count = existing_total_rating_count + total_new_rating_count
        
        score = 0
        for rating_type, rating_value in latest_rating_result.items():
            score += rating_value
            logger.info('latest %s=%s', rating_type, rating_value)
        score = score/len(latest_rating_result)
        
        logger.info('score=%s', score)
        
        
        merchant_rating_result.rating_result = {
                                                'reviews_details':latest_rating_result,
                                                'total_reviews'     : merchant_rating_result.total_rating_count,
                                                'score'             : score,
                                                
                                                }
        logger.info('merchant_rating_result.rating_result=%s', rating_result)
        
        merchant_rating_result.put()
    ''' 
        
        
            
        
            
        
        
    
    
    