'''
Created on 13 Apr 2020

@author: jacklok
'''
from google.cloud import ndb
from trexconf import conf as model_conf
from trexmodel.models.datastore.ndb_models import BaseNModel

 
class Todo(BaseNModel):
    
    name                    = ndb.StringProperty(required=True)
    desc                    = ndb.TextProperty(required=False, indexed=False)
    created_datetime        = ndb.DateTimeProperty(auto_now_add=True)
    modified_datetime       = ndb.DateTimeProperty(auto_now=True)
    
    dict_properties         = ['name', 'desc']
    dict_full_properties    = ['key','name', 'desc', 'created_datetime', 'modified_datetime']
    
    @staticmethod
    def create(name, desc=None):
        return Todo(name=name, desc=desc).put()
    
    @staticmethod
    def update(todo_key, name=None, desc=None):
        todo =  Todo.get(todo_key)
        if todo:
            todo.name = name
            todo.desc = desc
            todo.put()
    
    @staticmethod
    def list():
        return Todo.query().fetch(limit=model_conf.MAX_FETCH_RECORD)
    
    @staticmethod
    def get(todo_key_str):
        todo_key = ndb.Key(urlsafe=todo_key_str)
        return todo_key.get()
    
    @staticmethod
    def delete(todo_key_str):
        todo_key = ndb.Key(urlsafe=todo_key_str)
        
        todo_key.delete()
        
      