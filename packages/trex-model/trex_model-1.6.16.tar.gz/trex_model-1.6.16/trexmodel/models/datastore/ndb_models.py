'''
Created on 13 Apr 2020

@author: jacklok
'''
from google.cloud import ndb
from trexlib.utils.common.float_util import format_float
from datetime import datetime, date, time
from trexlib.utils.string_util import is_not_empty 
from trexlib.utils.log_util import get_tracelog
from six import string_types 
from trexlib.utils.common.date_util import increase_date 
import logging
#from google.cloud.ndb._datastore_query import Cursor
#from google.cloud.ndb import Cursor
from trexconf import conf as lib_conf 
from trexconf import conf as model_conf
from google.cloud.datastore.helpers import GeoPoint
from trexlib.utils.common.cache_util import getFromCache, setCache
 
logger = logging.getLogger('model')
#logger = logging.getLogger('target_debug') 

def clone_entity(entity, parent=None, **extra_args):
    """
    Clone an NDB entity and return the clone.
    
    Args:
        entity: The NDB entity to be cloned.
        extra_args: Additional properties to override in the cloned entity.
        
    Returns:
        A new instance of the entity's class with copied properties.
    """
    klass = entity.__class__
    props = {}
    
    for prop_name, prop in klass._properties.items():
        logger.debug('clone prop_name=%s',  prop_name)
        if not isinstance(prop, ndb.ComputedProperty):
            props[prop_name] = getattr(entity, prop_name)
    
    props.update(extra_args)
    if parent:
        return klass(parent=parent, **props)
    else:
        return klass(**props)

def convert_to_serializable_value(val, none_as_empty_string=False, gmt=0, 
                                  datetime_format=lib_conf.DEFAULT_DATETIME_FORMAT, 
                                  date_format=lib_conf.DEFAULT_DATE_FORMAT, 
                                  time_format=lib_conf.DEFAULT_TIME_FORMAT,
                                  excluded_dict_properties=None
                                  ):
    
    if isinstance(val, (list, tuple)):
        _list = []
        for item in val:
            _list.append(convert_to_serializable_value(item, excluded_dict_properties=excluded_dict_properties))
        value = _list
    elif isinstance(val, float):
        value = format_float(val)
    elif isinstance(val, (dict, int, bool)):
        #logger.debug('>>>>found dict, int, float, bool value=%s', val)
        value = val
    elif isinstance(val, datetime):
        gmt_datetime = increase_date(val, hour=gmt)
        value = gmt_datetime.strftime(datetime_format)
    elif isinstance(val, date):
        value = val.strftime(date_format)
    elif isinstance(val, time):
        #gmt_datetime = increase_date(val, hours=gmt)
        value = val.strftime(time_format)
    elif isinstance(val, GeoPoint):
        value = '%s,%s' % (val.latitude, val.longitude)    
    else:
        if none_as_empty_string:
            if val:
                value = str(val)
            else:
                value = ''
        else:
            if val is None:
                value = None
            else:
                value = str(val)
    #logger.debug('convert_to_serializable_value: value=%s', value)
    return value

def render_dict_value(val, full=False, show_key=True, gmt=0, 
                      datetime_format=lib_conf.DEFAULT_DATETIME_FORMAT, 
                      date_format=lib_conf.DEFAULT_DATE_FORMAT, 
                      time_format=lib_conf.DEFAULT_TIME_FORMAT,
                      excluded_dict_properties=None,
                      deep_level=99
                      ):
    #logger.debug('---render_dict_value---, deep_level=%d', deep_level)
    value = None
    if deep_level>0:
        if isinstance(val, DictModel):
            
            value = val.to_dict(full=full, show_key=show_key, gmt=gmt, 
                                date_format=date_format, datetime_format=datetime_format, time_format=time_format, 
                                excluded_dict_properties=excluded_dict_properties, deep_level=deep_level-1)
    
        elif isinstance(val, ndb.Model):
            value = val.key.urlsafe()
    
        elif isinstance(val, (list, tuple)):
            _list = []
            for item in val:
                _list.append(render_dict_value(
                                item, full=full, show_key=show_key, gmt=gmt, 
                                date_format=date_format, datetime_format=datetime_format, time_format=time_format, 
                                excluded_dict_properties=excluded_dict_properties,
                                deep_level=deep_level-1
                                ))
            value = _list
    
        elif isinstance(val, DictObject):
            value = val.to_dict(gmt=gmt, excluded_dict_properties=excluded_dict_properties, deep_level=deep_level-1)
        else:
            value = convert_to_serializable_value(val, gmt=gmt, date_format=date_format, datetime_format=datetime_format, time_format=time_format, excluded_dict_properties=excluded_dict_properties)
    return value

class DictObject(object):
    dict_properties = None
    
    def get_class_members(self, klass):
        ret = dir(klass)
        if hasattr(klass,'__bases__'):
            for base in klass.__bases__:
                ret = ret + self.get_class_members(base)
        return ret
    
    def uniq(self, seq ): 
        return list(set(seq))
    
    def properties(self):
        return self.__dict__

    def to_dict(self, full=True, show_key=True, dict_properties=None, 
                        excluded_dict_properties=None, 
                        #gmt=lib_conf.DEFAULT_GMT,
                        gmt=0, 
                        datetime_format=lib_conf.DEFAULT_DATETIME_FORMAT, 
                        date_format=lib_conf.DEFAULT_DATE_FORMAT, 
                        time_format=lib_conf.DEFAULT_TIME_FORMAT, 
                        deep_level=99,
                        ):
        logger.info('calling DictObject.to_dict')
        result = {}
        #logger.debug('properties = %s, object = %s', self.properties(), self)

        _dict_properties = dict_properties or self.dict_properties

        if _dict_properties:
            for p in _dict_properties:

                val = getattr(self, p)
                if val is not None:
                    #logger.debug('attribute=%s', p)
                    result[p] = render_dict_value(val, full=full, show_key=show_key, gmt=gmt, 
                                                  datetime_format=datetime_format, 
                                                  date_format=date_format, 
                                                  time_format=time_format,
                                                  excluded_dict_properties=excluded_dict_properties,
                                                  deep_level=deep_level,
                                                  )
        return result
    
class DictModel(ndb.Model):
    
    dict_properties             = None
    dict_full_properties        = None
    show_key_in_dict            = True

    def __get_attr_value(self, obj, attr_name):
        val = getattr(obj, attr_name)
        if isinstance(val, GeoPoint):
            return '%s,%s' % (val.latitude, val.longitude)
        
        return val

    def put(self, **kwargs):
        super(DictModel, self).put(**kwargs)
        
    def __str__(self):
        return '%s' % self.to_dict(deep_level=1) 

    def to_dict(self, full=False, show_key=True, dict_properties=None, excluded_dict_properties=None, 
                        gmt=0, 
                        datetime_format=lib_conf.DEFAULT_DATETIME_FORMAT, 
                        date_format=lib_conf.DEFAULT_DATE_FORMAT,time_format=lib_conf.DEFAULT_TIME_FORMAT,
                        deep_level=99,
                        ):
        result = {}
        logger.debug('DictModel: full=%s', full)
        logger.debug('DictModel: show_key=%s', show_key)
        
        #if self.show_key_in_dict or show_key:
        if show_key:
            try:
                result['key'] = self.key.urlsafe().decode("utf-8")
            except:
                pass 
        
        _dict_properties = dict_properties or self.dict_properties

        if full and self.dict_full_properties:
            _dict_properties = self.dict_full_properties

        if _dict_properties:
            for p in _dict_properties:
                if excluded_dict_properties is not None:
                    if p in excluded_dict_properties:
                        continue
                    
                if p=='key':
                    if result.get('key'):
                        continue
                    
                _p = p.split('.')

                if len(_p)>1:
                    ref_array   = _p[:-1]
                    ref_obj     = self
                    for _a in ref_array:
                        ref_obj = self.__get_attr_value(ref_obj, _a)

                    if ref_obj:
                        ref_value = self.__get_attr_value(ref_obj, _p[-1])
                else:
                    ref_value = self.__get_attr_value(self, p)

                if is_not_empty(ref_value):
                #if ref_value:
                    p = p.replace('.', '_')
                    result[p] = render_dict_value(ref_value, full=full, show_key=show_key, gmt=gmt, date_format=date_format, datetime_format=datetime_format, time_format=time_format, deep_level=deep_level)
                                        
        #logger.debug('DictModel: result=%s', result)
        
        return result    

class NDBModel(object):
    @classmethod
    def get_by_ndb_id(cls, ndb_id):
        if isinstance(ndb_id, string_types):
            return cls.get_by_key_name(ndb_id)
        else:
            return cls.get_by_id(ndb_id)

    def ndb_id(self):
        return self.key().id()

    def create_ndb_key(self):
        return ndb.Key(flat=self.key.flat())
    
    def clone(self, parent=None, **overrides):
        return clone_entity(self, parent=parent, **overrides)
        
    
class BaseNModel(DictModel, NDBModel):

    saved = False

    def is_saved(self):
        return self.saved

    @classmethod
    def _post_get_hook(cls, key, future):
        obj = future.get_result()
        if obj is not None:
            # test needed because post_get_hook is called even if get() fails!
            obj.saved = True

    def _post_put_hook(self, future):
        self.saved = True
    
    @classmethod
    def get_or_read_from_cache(cls, model_key):
        cache_key = f"{model_key}"
        
        def read_by_key(model_key):
            logger.debug('>>> going to read from DB')
            return ndb.Key(urlsafe=model_key).get()
        
        result = getFromCache(cache_key)
        if result is None:
            result = read_by_key(model_key)
            setCache(cache_key, result, timeout=300)
            
        else:
            logger.debug('>>> read from cache')
        return result
            
            
    @property
    def parent_key(self):
        return self.key.parent().urlsafe().decode('utf-8')

    @property
    def key_in_str(self):
        return self.key.urlsafe().decode('utf-8')
    
    @property
    def key_in_urlsafe(self):
        return self.key.urlsafe()

    @property
    def key_name(self):
        return self.key.id()

    def equal(self, another_instance):
        if another_instance:
            return self.key_in_str == another_instance.key_in_str
        else:
            return False

    def not_equal(self, another_instance):
        if another_instance:
            return self.key_in_str != another_instance.key_in_str
        else:
            return True
    
    def delete(self):
        self.key.delete()
    
    @classmethod
    def fetch(cls, model_key):
        try:
            if model_key:
                return ndb.Key(urlsafe=model_key).get()

        except:
            logger.error('Failed to fetch entity due to %s', get_tracelog())

        return None
    
    @classmethod
    def fetch_multi(cls, model_keys_list):
        try:
            if model_keys_list:
                return ndb.get_multi(model_keys_list)

        except:
            logger.error('Failed to fetch entity due to %s', get_tracelog())

        return None
    
    @classmethod
    def count(cls, limit=model_conf.MAX_FETCH_RECORD): 
        query = cls.query()
        
        return cls.count_with_condition_query(query, limit=limit)
    
    @classmethod
    def count_with_condition_query(cls, query, limit=model_conf.MAX_FETCH_RECORD):    
        
        
        return query.count(limit=limit)
    
    @classmethod
    def list_all(cls, offset=0,  start_cursor=None, return_with_cursor=False, keys_only=False, 
                 limit=model_conf.MAX_FETCH_RECORD):
        
        query = cls.query()
        
        return cls.list_all_with_condition_query(query, 
                                                 offset=offset, start_cursor=start_cursor,
                                                 return_with_cursor = return_with_cursor,
                                                 keys_only = keys_only, limit=limit
                                                 )
    
    @classmethod
    def list_all_with_condition_query(cls, query, offset=0,  start_cursor=None, return_with_cursor=False, 
                                      keys_only=False,limit=model_conf.MAX_FETCH_RECORD, order_by=None):
        
        
        logger.debug('list_all: start_cursor=%s, order_by=%s, return_with_cursor=%s', start_cursor, order_by, return_with_cursor)
        
        if start_cursor or return_with_cursor:
            if is_not_empty(start_cursor):
                if isinstance(start_cursor, string_types):
                    start_cursor = ndb.Cursor(urlsafe = start_cursor) if start_cursor else ndb.Cursor()
            else:
                start_cursor = ndb.Cursor()
            
            if order_by:
                (search_results, next_cursor, more)       = query.order(order_by).fetch_page(page_size=limit, start_cursor=start_cursor, keys_only=keys_only)
            else:
                (search_results, next_cursor, more)       = query.fetch_page(page_size=limit, start_cursor=start_cursor, keys_only=keys_only)
            logger.debug('##########################################')
            logger.debug('list_all: results=%s', search_results)
            logger.debug('list_all: next_cursor=%s', next_cursor)
            logger.debug('list_all: more=%s', more) 
            logger.debug('list_all: return_with_cursor=%s', return_with_cursor) 
            
            logger.debug('##########################################')
            
            if more:
                return search_results, next_cursor.to_websafe_string().decode('utf-8')  
            else:    
                #return search_results, 'None'
                return search_results, None
            
        else:
            search_results = query.fetch(limit=limit, offset=offset, keys_only=keys_only)
            
            return search_results
    
    @classmethod
    def delete_multiples(cls, query, limit=model_conf.MAX_FETCH_RECORD):
        list_of_keys = query.fetch(limit=limit, offset=0, keys_only=True)
        ndb.delete_multi(list_of_keys)
        
    def before_put(self):
        pass
    
    def after_put(self):
        pass
    
    def put(self, **kwargs):
        self.before_put()
        super(BaseNModel, self).put(**kwargs)
        self.after_put()
    
    
class FullTextSearchable(ndb.Model):
    full_text_search_field      = ndb.StringProperty(repeated=True)
    
    fulltextsearch_field_name           = None
    fulltextsearch_field_to_lowercase   = True
    
    
    def _pre_put_hook(self):
        """before save, parse searchable field into strings"""
        
        _searchable_field_name = self.fulltextsearch_field_name
        
        logger.debug('_searchable_field_name=%s', _searchable_field_name)
        if _searchable_field_name:
            searchable_field_value = getattr(self, _searchable_field_name)
            logger.debug('searchable_field_value=%s', searchable_field_value)
            
            if is_not_empty(searchable_field_value):
                if self.fulltextsearch_field_to_lowercase:
                    splitted_words = searchable_field_value.lower().split(' ')
                else:
                    splitted_words = searchable_field_value.split(' ')
                
                logger.debug('splitted_words=%s', splitted_words)
                
                searchable_words_list = [x for x in splitted_words if x and len(x) >= 2]
                logger.debug('searchable_words_list=%s', searchable_words_list)
                
                self.full_text_search_field = searchable_words_list
    
            else:
                self.full_text_search_field = []
                
            
    
    @classmethod
    def full_text_count(cls, search_text_list, query=None, limit=model_conf.MAX_FETCH_RECORD_FULL_TEXT_SEARCH_PER_PAGE, to_lowercase=True):
        
        logger.debug('full_text_count: search_text_list=%s', search_text_list)
        
        lowercase_words_list = []
        
        if is_not_empty(search_text_list):
            if to_lowercase:
                lowercase_words_list = [x.lower() for x in search_text_list]
            else:
                lowercase_words_list = search_text_list
        
            logger.debug('full_text_search: lowercase_words_list=%s', lowercase_words_list)
            
        if query is None:
            query = cls.query()
            
        
        for word in lowercase_words_list:
            query = query.filter(cls.full_text_search_field == word)
            
        logger.debug('query=%s', query)
        
        return query.count(limit=limit)
            
           
        
    @classmethod
    def full_text_search(cls, text_search = None, query=None, offset=0,  start_cursor=None, return_with_cursor=False, keys_only=False, 
                         limit=model_conf.MAX_FETCH_RECORD_FULL_TEXT_SEARCH_PER_PAGE, to_lowercase=True):
        if query is None:
            query = cls.query()
        
        logger.debug('##########################################')
        logger.debug('full_text_search: text_search=%s', text_search)
        logger.debug('full_text_search: query=%s', query)
        logger.debug('full_text_search: start_cursor=%s', start_cursor)
        logger.debug('full_text_search: offset=%s', offset)
        logger.debug('full_text_search: return_with_cursor=%s', return_with_cursor)
        
        logger.debug('##########################################')
        
            
        if is_not_empty(text_search):
            if to_lowercase:
                lowercase_words_list = [x.lower() for x in text_search]
            else:
                lowercase_words_list = text_search
            
            logger.debug('full_text_search: lowercase_words_list=%s', lowercase_words_list)
            
            for word in lowercase_words_list:
                query = query.filter(cls.full_text_search_field == word)
        
        if start_cursor or return_with_cursor:
            if is_not_empty(start_cursor):
                if isinstance(start_cursor, string_types):
                    start_cursor = ndb.Cursor(urlsafe = start_cursor) if start_cursor else ndb.Cursor()
            #else:
            #    start_cursor = ndb.Cursor()
            '''
            if is_not_empty(start_cursor):
                if isinstance(start_cursor, string_types):
                    start_cursor = Cursor.from_websafe_string(start_cursor)
            else:
                start_cursor = None
            '''
            if is_not_empty(start_cursor):
                logger.debug('start_cursor is empty or none')
                (search_results, next_cursor, more)       = query.fetch_page(page_size=limit, 
                                                                         start_cursor=start_cursor, 
                                                                         keys_only=keys_only)
            else:
                (search_results, next_cursor, more)       = query.fetch_page(page_size=limit, offset=offset, 
                                                                         keys_only=keys_only)
            
            logger.debug('==========================================')
            logger.debug('full_text_search: query=%s', query)
            logger.debug('full_text_search: offset=%s', offset)
            logger.debug('full_text_search: search_results count =%s', len(search_results))
            logger.debug('full_text_search: next_cursor=%s', next_cursor)
            logger.debug('full_text_search: more=%s', more) 
            
            logger.debug('==========================================')
            
            if more:
                return search_results, next_cursor.to_websafe_string().decode('utf-8')  
            else:    
                return search_results, 'None'
            
        else:
            search_results = query.fetch(limit=limit, offset=offset)
            
            logger.debug('==========================================')
            logger.debug('full_text_search: query=%s', query)
            logger.debug('full_text_search: offset=%s', offset)
            logger.debug('full_text_search: search_results count =%s', len(search_results))
            
            logger.debug('==========================================')
            
            return search_results
        
    @classmethod
    def full_text_search_query(cls, text_search = None, query=None, to_lowercase=True):
        if query is None:
            query = cls.query()
            
        if is_not_empty(text_search):
            if to_lowercase:
                lowercase_words_list = [x.lower() for x in text_search]
            else:
                lowercase_words_list = text_search
            
            logger.debug('full_text_search: lowercase_words_list=%s', lowercase_words_list)
            
            for word in lowercase_words_list:
                query = query.filter(ndb.AND(cls.full_text_search_field == word))
        
        return query        
            

    
