'''
Created on 23 Jul 2021

@author: jacklok
'''
from google.cloud import ndb
from trexmodel.models.datastore.ndb_models import BaseNModel, DictModel, FullTextSearchable
from trexmodel.models.datastore.merchant_models import MerchantAcct, MerchantUser
from trexlib.utils.string_util import is_empty, is_not_empty
import logging
from trexconf import conf
from trexlib.utils.string_util import random_string
import trexmodel.conf as model_conf
from trexmodel.models.datastore.model_decorators import model_transactional
from flask_babel import gettext


#logger = logging.getLogger('model')
logger = logging.getLogger('debug')

class ProductBase(BaseNModel,DictModel):
    
    @property
    def merchant_acct_entity(self):
        return MerchantAcct.fetch(self.key.parent().urlsafe())
'''
class ProductCategorySetup(ProductBase):
    
    setup_label             = ndb.StringProperty(required=True)
    created_datetime        = ndb.DateTimeProperty(required=True, auto_now_add=True)
    modified_datetime       = ndb.DateTimeProperty(required=True, auto_now=True)
    created_by              = ndb.KeyProperty(name="created_by", kind=MerchantUser)
    modified_by             = ndb.KeyProperty(name="modified_by", kind=MerchantUser)
    
    dict_properties = ['setup_label', 'created_datetime', 'modified_datetime']
    
    @staticmethod
    @model_transactional(desc='ProductCategorySetup.create')
    def create(setup_label, merchant_acct, created_by=None):
        created_by_key = None
        if created_by:
            created_by_key = created_by.create_ndb_key()
        created_category_setup = ProductCategorySetup(
                                            parent               = merchant_acct.create_ndb_key(),
                                            setup_label          = setup_label,
                                            created_by           = created_by_key,
                                            )
        
        created_category_setup.put()
'''    

class ProductCategory(ProductBase):
    '''
    merchant_acct as ancestor
    '''
    category_label          = ndb.StringProperty(required=True)
    parent_category_key     = ndb.StringProperty(required=False)
    product_modifier        = ndb.JsonProperty()
    
    product_items           = ndb.JsonProperty()
    child_category_keys     = ndb.JsonProperty()
    
    created_datetime        = ndb.DateTimeProperty(required=True, auto_now_add=True)
    modified_datetime       = ndb.DateTimeProperty(required=True, auto_now=True)
    created_by              = ndb.KeyProperty(name="created_by", kind=MerchantUser)
    modified_by             = ndb.KeyProperty(name="modified_by", kind=MerchantUser)
    
    #category_setup          = ndb.KeyProperty(name="category_setup", kind=ProductCategorySetup)
    
    
    dict_properties = ['category_label', 'parent_category_key', 'is_main_category', 'has_child', 'child_category_keys', 'product_item_count', 'product_modifier',
                       'product_items', 'category_label_and_other_details', 'category_label_and_product_name']
    
    @property
    def is_main_category(self):
        return is_empty(self.parent_category_key)
    
    @property
    def has_child(self):
        if is_not_empty(self.child_category_keys):
            return True
        return False
    
    @property
    def parent_category(self):
        if is_not_empty(self.parent_category_key):
            return ProductCategory.fetch(self.parent_category_key)
    
    @property
    def product_item_count(self):
        if self.product_items:
            return len(self.product_items)
        else:
            return 0
    
    def child_categories_list(self, category_dict_list):
        child_category_dict_list = []
        for c in category_dict_list:
            if c.key_in_str in self.child_category_keys:
                child_category_dict_list.append(c)
        
        return child_category_dict_list
        
    @property
    def category_label_and_other_details(self):
        return '%s (%s %s)' % (self.category_label, self.product_item_count, gettext('items'))
    
    @property
    def category_label_and_product_name(self):
        product_name_list = []
        if self.product_item_count>0:
            for product_key in self.product_items:
                product = Product.fetch(product_key)
                if product:
                    product_name_list.append(product.product_name)
        
        return '%s (%s)' % (self.category_label, '|'.join(product_name_list))
    
    @staticmethod
    @model_transactional(desc='ProductCategory.create')
    def create(category_label, merchant_acct, created_by=None, parent_category_key=None, product_modifier=None):
        created_by_key = None
        if created_by:
            created_by_key = created_by.create_ndb_key()
        created_category = ProductCategory(
                                            parent                  = merchant_acct.create_ndb_key(),
                                            category_label          = category_label,
                                            parent_category_key     = parent_category_key,
                                            product_modifier        = product_modifier or [],
                                            created_by              = created_by_key,
                                            )
        
        created_category.put()
        
        if is_not_empty(parent_category_key):
            parent_category = ProductCategory.fetch(parent_category_key)
            if parent_category:
                parent_category.add_child_category(created_category)
        
        return created_category
        
    @staticmethod
    @model_transactional(desc='ProductCategory.update')
    def update(category, category_label, modified_by=None, product_modifier=None):
        
        modified_by_key = None
        if modified_by:
            modified_by_key = modified_by.create_ndb_key()
            
        new_product_modifier = []
        if is_not_empty(product_modifier):
            for pm in product_modifier:
                if is_not_empty(pm) and len(pm)>0:
                    new_product_modifier.append(pm)
        
        
        if is_empty(new_product_modifier):
            new_product_modifier = None
        
        logger.debug('new_product_modifier=%s', new_product_modifier)
        
        previous_product_modifier_list  = category.product_modifier 
            
        category.product_modifier       = new_product_modifier
        category.category_label         = category_label
        category.modified_by            = modified_by_key
        category.put()
        
        product_item_keys = []
        
        if category.product_items:
            for k in category.product_items:
                product_item_keys.append(ndb.Key(urlsafe=k))
            
            if product_item_keys:
                logger.debug('There are %d product items configured to %s', len(product_item_keys), category.key_in_str)
                category_product_items = Product.list_by_product_keys(product_item_keys)
                #updating_product_list = []
                
                logger.debug('previous_product_modifier_list=%s', previous_product_modifier_list)
                logger.debug('new_product_modifier=%s', new_product_modifier)
    
                
                for product in category_product_items:
                    
                    changed_product_modifier = product.product_modifier or []
                    logger.debug('changed_product_modifier=%s', changed_product_modifier)
                                    
                    if changed_product_modifier:
                        #remove previous product modifier
                        if previous_product_modifier_list:
                            for product_modifier_key in previous_product_modifier_list:
                                if product_modifier_key in changed_product_modifier:
                                    changed_product_modifier.remove(product_modifier_key)
                                    logger.debug('remove previous product modifier for %s', product.product_name)
                    
                    #update product to new product modifier            
                    if new_product_modifier:
                        changed_product_modifier = list(set(new_product_modifier) | set(changed_product_modifier))
                        logger.debug('add new product modifier for %s', product.product_name)
                    
                    product.product_modifier = changed_product_modifier
                    product.put()
                #updating_product_list.append(product)
                
                #ndb.put_multi(updating_product_list)
            else:
                logger.debug('No product is configured under %s category', category.category_label)
        else:
                logger.debug('No product is configured under %s category', category.category_label)
        
    
    def add_child_category(self, child_category):
        child_category_key = child_category.key_in_str
        logger.debug('child_category key=%s', child_category_key)
        if self.child_category_keys is not None:
            self.child_category_keys = list(set(self.child_category_keys) | set([child_category_key]))
            
        else:
            self.child_category_keys = [child_category_key]
        
        self.put()
        
    def remove_child_category(self, child_category):
        logger.debug('child_category=%s', child_category.category_label)
        if self.child_category_keys is not None:
            child_category_key = child_category.key_in_str
            self.child_category_keys.remove(child_category_key)
        else:
            self.child_category_keys = []
            
        self.put()
        
    @staticmethod
    def add_product(product_category, product):
        product_key         = product.key_in_str
        merchant_acct       = product.merchant_acct_entity
        
        product_items = product_category.product_items
        if product_items:
            if not product_key in product_items:
                product_items.append(product_key)
            else:
                logger.debug('Already in product category product items reference')
        else:
            product_items = [product_key]
        
        product_category.product_items = list(set(product_items))
        
        product_category.put()
        
        if is_not_empty(product_category.parent_category_key):
            parent_product_category = ProductCategory.fetch(product_category.parent_category_key)
            product_category.update_parent_category_with_product_items_reference(parent_product_category, product_category.product_items, merchant_acct)
    
    @staticmethod
    def remove_product(product_category, product):
        product_key         = product.key_in_str
        merchant_acct       = product.merchant_acct_entity
        
        product_items = product_category.product_items
        if product_items:
            if product_key in product_items:
                product_items.remove(product_key)
            else:
                logger.debug('cant find product item from category product items reference')
        else:
            product_items = []
            
        product_category.product_items = list(set(product_items))
        product_category.put()
        
        if is_not_empty(product_category.parent_category_key):
            parent_product_category                 = ProductCategory.fetch(product_category.parent_category_key)
            parent_product_category.remove_parent_category_from_product_items_reference(product_key, merchant_acct)
        
    @staticmethod
    def update_product_after_change_category(product, previous_category_key):
        new_product_category                    = ProductCategory.fetch(product.category_key)
        previous_product_category               = ProductCategory.fetch(previous_category_key)
        
        ProductCategory.add_product(new_product_category, product)
        ProductCategory.remove_product(previous_product_category, product)
        
    
    def remove_parent_category_from_product_items_reference(self, product_key, merchant_acct):
        if self.parent_category_key:
            parent_product_category                 = ProductCategory.fetch(self.parent_category_key)
            if parent_product_category.product_items:
                parent_product_category.product_items.remove(product_key)
        
            parent_product_category.remove_parent_category_from_product_items_reference(product_key, merchant_acct)    
            
            
    def update_parent_category_with_product_items_reference(self,  parent_product_category, product_items, merchant_acct):
        if is_not_empty(self.parent_category_key):
            logger.debug('parent_category_key=%s', self.parent_category_key)
            
            parent_product_items = parent_product_category.product_items
            if parent_product_items:
                parent_product_items = list(set(parent_product_items) | set(product_items))
                
            else:
                parent_product_items = product_items
            
            logger.debug('product_items count=%s from %s', len(product_items), self.category_label)
            
            parent_product_category.product_items = parent_product_items
            
            logger.debug('parent_product_category product items count=%s', len(parent_product_items))
            
            parent_product_category.put()
            
            if is_not_empty(parent_product_category.parent_category_key):
                grand_parent_product_category = ProductCategory.fetch(parent_product_category.parent_category_key)
                parent_product_category.update_parent_category_with_product_items_reference(grand_parent_product_category, parent_product_category.product_items, merchant_acct)
    
    @staticmethod
    @model_transactional(desc='delete_with_child')
    def delete_with_child(product_category, merchant_acct):
        product_category.delete_child_category(merchant_acct)
        product_category.delete()
        
    @staticmethod
    def get_structure_by_merchant_acct(merchant_acct):
        product_category_list = ProductCategory.query(ancestor=merchant_acct.create_ndb_key()).fetch(limit=conf.MAX_FETCH_RECORD)
        
        product_category_dict_list = []
        
        for pc in product_category_list:
            product_category_dict_list.append(pc)
        
        return product_category_dict_list
    
    @staticmethod
    def list_by_parent_category_key(merchant_acct, parent_category_key):
        product_category_list = ProductCategory.query(ndb.AND(ProductCategory.parent_category_key==parent_category_key),
                                                        ancestor=merchant_acct.create_ndb_key()).fetch(limit=conf.MAX_FETCH_RECORD)
        return product_category_list
    
    @staticmethod
    def list_by_merchant_acct(merchant_acct):
        product_category_list = ProductCategory.query(ancestor=merchant_acct.create_ndb_key()).fetch(limit=conf.MAX_FETCH_RECORD)
        return product_category_list
    
    @staticmethod
    @model_transactional(desc='ProductCategory.remove')
    def remove(product_category, merchant_acct):
        if product_category.has_child:
            product_category.delete_child_category(merchant_acct)
        
        if is_not_empty(product_category.parent_category_key):
            parent_product_category = ProductCategory.fetch(product_category.parent_category_key)
            
            if parent_product_category:
                parent_product_category.remove_child_category(product_category)
        
        logger.debug('Going to delete product category (%s)', product_category.category_label)
        product_category.delete()
        
    def delete_child_category(self, merchant_acct):
        category_key                = self.key_in_str
        child_category_list         = ProductCategory.list_by_parent_category_key(merchant_acct, category_key)
        
        logger.debug('child_category_list=%s', child_category_list)
        
        if child_category_list:
            for c in child_category_list:
                if c.has_child:
                    c.delete_child_category(merchant_acct)
                    logger.debug('Going to delete product category (%s)', c.category_label)
                    c.delete()
                else:
                    logger.debug('Going to delete product category (%s)', c.category_label)
                    c.delete()
    
    
class Product(ProductBase, FullTextSearchable):
    '''
    merchant_acct as ancestor
    '''
    product_sku                 = ndb.StringProperty(required=True)
    product_name                = ndb.StringProperty(required=True)
    product_desc                = ndb.StringProperty(required=False)
    category_key                = ndb.StringProperty(required=False)
    
    barcode                     = ndb.StringProperty(required=False)   
    
    price                       = ndb.FloatProperty(required=False, default=.0)
    cost                        = ndb.FloatProperty(required=False, default=.0)
    
    #for shipping purpose
    weight                      = ndb.FloatProperty(required=False, default=.0)
    length                      = ndb.FloatProperty(required=False, default=.0)
    width                       = ndb.FloatProperty(required=False, default=.0)
    height                      = ndb.FloatProperty(required=False, default=.0)
    
    tax_details                 = ndb.JsonProperty()
    
    product_modifier            = ndb.JsonProperty()
    
    created_datetime            = ndb.DateTimeProperty(required=True, auto_now_add=True)
    modified_datetime           = ndb.DateTimeProperty(required=True, auto_now=True)
    created_by                  = ndb.KeyProperty(name="created_by", kind=MerchantUser)
    modified_by                 = ndb.KeyProperty(name="modified_by", kind=MerchantUser)  
    
    pos_settings                = ndb.JsonProperty()
    
    fulltextsearch_field_name   = 'product_name'
    
    dict_properties = ['product_sku', 'product_name', 'category_key', 'price', 'cost', 
                       'product_desc', 'barcode', 'pos_settings', 'tax_details', 'product_modifier']
    
    @property
    def product_default_image(self):
        return self.pos_settings.get('representation_settings').get('image_url')
    
    def setting_details_for_pos(self, merchant_acct):
        modifier_keys_list              = self.product_modifier
        modifier_setting_list_for_pos   = []
        
        
        if modifier_keys_list:
            product_modifiers_list = ProductModifier.list_by_merchant_account(merchant_acct)
        
            if product_modifiers_list:
                for modifier_key in modifier_keys_list:
                    for modifier_details in product_modifiers_list:
                        if modifier_details.key_in_str == modifier_key:
                            modifier_setting_list_for_pos.append(modifier_details.setting_details_for_pos())
                            break  
        
        details_in_dict = {
                            'sku'                   : self.product_sku,
                            'label'                 : self.product_name,
                            'desc'                  : self.product_desc,
                            'price'                 : self.price,
                            'category_key'          : self.category_key,
                            'barcode'               : self.barcode,   
                            'modifiers'             : modifier_setting_list_for_pos, 
                            'representation_on_pos' : self.pos_settings,
                            }
        
        return details_in_dict
    
    @staticmethod
    def search_merchant_product(merchant_acct, product_name=None, product_sku=None, category_key=None,
                                 offset=0, start_cursor=None, limit=model_conf.MAX_FETCH_RECORD):
        
        search_text_list    = None
        query               = None
        
        if is_not_empty(product_name):
            search_text_list = product_name.split(' ')
            
        if merchant_acct:
            query = Product.query(ancestor=merchant_acct.create_ndb_key())
        else:
            query = Product.query()
            
        
        if is_not_empty(product_sku):
            query = query.filter(Product.product_sku==product_sku)
            
        elif is_not_empty(category_key):
            query = query.filter(Product.category_key==category_key)
        
        total_count                         = Product.full_text_count(search_text_list, query, conf.MAX_FETCH_RECORD_FULL_TEXT_SEARCH)
        
        (search_results, next_cursor)       = Product.full_text_search(search_text_list, query, offset=offset, 
                                                                   start_cursor=start_cursor, return_with_cursor=True, 
                                                                   limit=limit)
        
        return (search_results, total_count, next_cursor)
    
    @staticmethod
    @model_transactional(desc='Product.create')
    def create(product_sku, product_name, category_key, merchant_acct, product_desc=None, price=.0, cost=.0, barcode=None, product_modifier=None, created_by=None):
        created_by_key = None
        if created_by:
            created_by_key = created_by.create_ndb_key()
        
        pos_settings        = {
                                    'represenation_sku'             : product_sku,
                                    'represenation_name'            : product_name,
                                    'product_shortcut_key'          : '',
                                    }
        
        created_product = Product(
                                            parent              = merchant_acct.create_ndb_key(),
                                            product_sku         = product_sku,
                                            product_name        = product_name,
                                            barcode             = barcode,
                                            product_desc        = product_desc,
                                            category_key        = category_key, 
                                            product_modifier    = product_modifier,
                                            created_by          = created_by_key,
                                            price               = price,
                                            cost                = cost,
                                            pos_settings        = pos_settings,
                                            )
        
        
        
        created_product.put()
        
        
        product_category = ProductCategory.fetch(category_key)
        ProductCategory.add_product(product_category, created_product)
        
        return created_product
        
    @staticmethod
    @model_transactional(desc='Product.create')
    def update(product, updated_by=None):
        product_history = Product.fetch(product.key_in_str)
        
        modified_by_key = None
        
        if updated_by:
            modified_by_key = updated_by.create_ndb_key()
        
        
        new_product_modifier = []
        if is_not_empty(product.product_modifier):
            for pm in product.product_modifier:
                if is_not_empty(pm) and len(pm)>0:
                    new_product_modifier.append(pm)
        
        
        if is_empty(new_product_modifier):
            new_product_modifier = None
        
        logger.debug('new_product_modifier=%s', new_product_modifier)
            
        product.product_modifier    = new_product_modifier
        
        product.modified_by         = modified_by_key
        product.put() 
        
        if product_history.category_key!=product.category_key:
            logger.debug('Going to update product category product item reference')
            ProductCategory.update_product_after_change_category(product, product_history.category_key)
        else:
            logger.debug('product category remain same')
    
    
    @staticmethod
    @model_transactional(desc='Product.remove')
    def remove(product, product_file_bucket):
        product_category    = ProductCategory.fetch(product.category_key)
        
        ProductCategory.remove_product(product_category, product)
        ProductFile.remove_file_by_product(product, product_file_bucket)
        product.delete()
        
        
    @staticmethod
    def list_by_merchant_acct(merchant_acct, limit=conf.MAX_FETCH_RECORD):
        return Product.query(ancestor=merchant_acct.create_ndb_key()).fetch(limit = limit)
    
    @staticmethod
    def get_by_product_sku(product_sku, merchant_acct):
        result = Product.query(ndb.AND(Product.product_sku==product_sku), ancestor=merchant_acct.create_ndb_key()).fetch(limit = 1)
        if result:
            return result[0]
        
    @staticmethod
    def list_by_product_keys(product_keys):
        return Product.query(ndb.AND(Product.key.IN(product_keys))).fetch(limit = conf.MAX_FETCH_RECORD)
        
        
        
        
class ProductFile(BaseNModel, DictModel):
    '''
    Product as ancestor
    '''
    product_file_label              = ndb.StringProperty(required=False)
    product_file_type               = ndb.StringProperty(required=True)
    product_file_public_url         = ndb.StringProperty(required=True)
    product_file_storage_filename   = ndb.StringProperty(required=True)
    
    dict_properties = ['product_file_public_url', 'product_file_storage_filename', 'product_file_type']
    
    @staticmethod
    def list_by_product(product):
        return ProductFile.query(ancestor=product.create_ndb_key()).fetch(limit=conf.MAX_FETCH_RECORD)
    
    @staticmethod
    def upload_file(uploading_file, product, merchant_acct, bucket, product_file_type=None):
        file_prefix                         = random_string(8)
        product_file_storage_filename       = 'merchant/'+merchant_acct.key_in_str+'/product/'+file_prefix+'-'+uploading_file.filename
        blob                                = bucket.blob(product_file_storage_filename)
        
        logger.debug('product_file_storage_filename=%s', product_file_storage_filename)
        
        blob.upload_from_string(
                uploading_file.read(),
                content_type=uploading_file.content_type
            )
        
        uploaded_url        = blob.public_url
        
        logger.debug('uploaded_url=%s', uploaded_url)
        logger.debug('product_file_type=%s', product_file_type)
        
        
        pos_settings = product.pos_settings or {}
        if is_empty(pos_settings.get('representation_on_pos_option')):
            
            pos_settings['representation_on_pos_option']    = 'image'
            pos_settings['representation_settings']         = {
                                                                'image_url': uploaded_url,
                                                                }
            product.pos_settings = pos_settings
            product.put()
                
        product_file = ProductFile(
                            parent = product.create_ndb_key(),
                            product_file_public_url             = uploaded_url,
                            product_file_storage_filename       = product_file_storage_filename,
                            product_file_type                   = product_file_type,
                            )
        
        product_file.put()
        
        return product_file
    
    @staticmethod
    def remove_file(product_file, bucket):
        
        old_logo_blob = bucket.get_blob(product_file.product_file_storage_filename) 
        if old_logo_blob:
            old_logo_blob.delete()
            product_file.delete()
            
    @staticmethod
    def remove_file_by_product(product, bucket):
        if bucket:
            product_files_list = ProductFile.list_by_product(product)
            for pf in product_files_list:
                ProductFile.remove_file(pf, bucket)
        
        
class ProductModifier(ProductBase):
    '''
    merchant_acct as ancestor
    '''
    modifier_name               = ndb.StringProperty(required=True)
    modifier_label              = ndb.StringProperty(required=False)
    have_default_option         = ndb.BooleanProperty(required=True, default=False)
    modifier_options            = ndb.JsonProperty()
    
    allow_multiple_option       = ndb.BooleanProperty(required=False, default=False)
    option_is_mandatory         = ndb.BooleanProperty(required=False, default=True)
    enabled                     = ndb.BooleanProperty(required=True, default=True)
    archived                    = ndb.BooleanProperty(required=False, default=False)
    
    created_datetime            = ndb.DateTimeProperty(required=True, auto_now_add=True)
    modified_datetime           = ndb.DateTimeProperty(required=True, auto_now=True)
    
    dict_properties = ['modifier_name', 'modifier_label', 'modifier_options', 'have_default_option', 'allow_multiple_option', 'option_is_mandatory', 'enabled', 'archived']
    
    @property
    def is_enabled(self):
        return self.enabled
    
    @property
    def is_disabled(self):
        return self.enabled==False
    
    @property
    def is_archived(self):
        return self.archived
    
    def setting_details_for_pos(self):
        return {
                'modifier_key'          : self.key_in_str,
                'modifier_name'         : self.modifier_name,
                'modifier_label'        : self.modifier_label,
                'have_default_option'   : self.have_default_option,
                'allow_multiple_option' : self.allow_multiple_option,
                'option_is_mandatory'   : self.option_is_mandatory,
                'modifier_options'      : self.modifier_options,
                }
        
    
    
    @staticmethod
    def create(merchant_acct, modifier_name, modifier_label=None, modifier_options={}, have_default_option=False, allow_multiple_option=False, option_is_mandatory=False):
        product_modifier = ProductModifier(
                                    parent                  = merchant_acct.create_ndb_key(),
                                    modifier_name           = modifier_name,
                                    modifier_label          = modifier_label,
                                    have_default_option     = have_default_option,
                                    allow_multiple_option   = allow_multiple_option,
                                    modifier_options        = modifier_options,
                                    option_is_mandatory     = option_is_mandatory,
                                    )
        
        product_modifier.put()
        return product_modifier
    
    @staticmethod
    def update(product_modifier, modifier_name, modifier_label=None, modifier_options={}, have_default_option=False, allow_multiple_option=False, option_is_mandatory=False):
        product_modifier.modifier_name              = modifier_name
        product_modifier.modifier_label             = modifier_label
        product_modifier.modifier_options           = modifier_options
        product_modifier.have_default_option        = have_default_option
        product_modifier.allow_multiple_option      = allow_multiple_option
        product_modifier.option_is_mandatory        = option_is_mandatory
        product_modifier.put()
    
    @staticmethod
    def list_by_merchant_account(merchant_acct, limit = conf.MAX_FETCH_RECORD):
        result = ProductModifier.query(ancestor=merchant_acct.create_ndb_key()).fetch(limit=limit)
        active_product_modifiers_list = []
        for r in result:
            if not r.archived:
                active_product_modifiers_list.append(r)
            
        return active_product_modifiers_list
    
    def __update_merchant_account_product_modifier_configuration(self):
        merchant_acct = self.merchant_acct_entity    
        merchant_acct.update_product_modifier(self.setting_details_for_pos())
        merchant_acct.put()
    
    @staticmethod
    def enable(product_modifier):
        product_modifier.enabled = True
        product_modifier.put()
        
        product_modifier.__update_merchant_account_product_modifier_configuration()
        
    @staticmethod
    def disable(product_modifier):
        product_modifier.enabled = False
        product_modifier.put() 
        
        merchant_acct = product_modifier.merchant_acct_entity    
        merchant_acct.remove_product_modifier_configuration(product_modifier.key_in_str)
        merchant_acct.put() 
        
    @staticmethod
    def archive(product_modifier):
        product_modifier.archived = True
        product_modifier.put() 
        
        merchant_acct = product_modifier.merchant_acct_entity    
        merchant_acct.remove_product_modifier_configuration(product_modifier.key_in_str)
        merchant_acct.put()   
        
class ProductCatalogue(ProductBase):
    '''
    merchant_acct as ancestor
    '''
    catalogue_name              = ndb.StringProperty(required=True)
    desc                        = ndb.StringProperty(required=False) 
    menu_settings               = ndb.JsonProperty()  
    published_menu_settings     = ndb.JsonProperty()
    
    
    
    is_publish                  = ndb.BooleanProperty(default=False)
    
    created_datetime            = ndb.DateTimeProperty(required=True, auto_now_add=True)
    modified_datetime           = ndb.DateTimeProperty(required=True, auto_now=True)  
    
    created_by                  = ndb.KeyProperty(name="created_by", kind=MerchantUser)
    modified_by                 = ndb.KeyProperty(name="modified_by", kind=MerchantUser)
    
    dict_properties = ['catalogue_name', 'desc', 'menu_settings', 'total_product_items_count', 'is_publish']
    
    @property
    def total_product_items_count(self):
        total_count = 0
        if self.menu_settings:
            for k, v in self.menu_settings.items():
                total_count+=len(v)
        return total_count
    
    def publish(self):
        self.published_menu_settings = self.setting_details_for_pos
        self.is_publish = True
        self.put()
    
    def unpublish(self):
        self.is_publish = False
        self.put()
    
    @property
    def setting_details_for_pos(self):
        self.published_menu_settings = self.menu_settings
        merchant_acct           = self.merchant_acct_entity
        product_details_listing = Product.list_by_merchant_acct(merchant_acct)
        categories_list         = ProductCategory.list_by_merchant_acct(merchant_acct)
        
        if product_details_listing and categories_list:
            menu_group_by_cateogry_dict = {}
            for category_key, product_keys_list in self.menu_settings.items():
                category_details        = self.__lookup_category_details(category_key, categories_list)
                items_details_list      = []
                for product_key in product_keys_list:
                    product_details = self.__lookup_product_details(product_key, product_details_listing)
                    if product_details:
                        product_setting_on_pos = product_details.setting_details_for_pos(merchant_acct)
                        items_details_list.append(product_setting_on_pos)
                
                menu_group_by_cateogry_dict[category_key] = {
                                                            'label'         : category_details.category_label,
                                                            'count'         : len(items_details_list),
                                                            'items'         : items_details_list,
                                                            }
                
        
        return menu_group_by_cateogry_dict
                
    
    def __lookup_category_details(self, category_key, categories_list):
        for category_details in categories_list:
            if category_details.key_in_str == category_key:
                return category_details
    
    def __lookup_product_details(self, product_key, product_details_list):
        for product_details in product_details_list:
            if product_details.key_in_str == product_key:
                return product_details
    
    @staticmethod
    def create(catalogue_name, menu_settings=[], merchant_acct=None, desc=None, created_by=None):
        created_by_key = None
        if created_by:
            created_by_key = created_by.create_ndb_key()
            
        product_catalogue =  ProductCatalogue(
                                parent                  = merchant_acct.create_ndb_key(),
                                catalogue_name          = catalogue_name,
                                menu_settings           = menu_settings,
                                published_menu_settings = {},
                                desc                    = desc,
                                created_by              = created_by_key
                                )
        
        product_catalogue.put()
        return product_catalogue
    
    @staticmethod
    def update(product_catalogue, catalogue_name, menu_settings=[], desc=None, modified_by=None):
        modified_by_key = None
        if modified_by:
            modified_by_key = modified_by.create_ndb_key()
        
        product_catalogue.catalogue_name    = catalogue_name
        product_catalogue.menu_settings     = menu_settings
        product_catalogue.desc              = desc
        product_catalogue.modified_by       = modified_by_key
            
        product_catalogue.put()
        
        return product_catalogue
    
    @staticmethod
    def list_published_by_merchant_acct(merchant_acct, limit=conf.MAX_FETCH_RECORD):
        result =  ProductCatalogue.query(ancestor=merchant_acct.create_ndb_key()).fetch(limit=limit)
        published_catalogue = []
        if result:
            for r in result:
                if r.is_publish:
                    published_catalogue.append(r)
        
        return published_catalogue
    
    @staticmethod
    def list_by_merchant_acct(merchant_acct, limit=conf.MAX_FETCH_RECORD):
        return  ProductCatalogue.query(ancestor=merchant_acct.create_ndb_key()).fetch(limit=limit)
        
