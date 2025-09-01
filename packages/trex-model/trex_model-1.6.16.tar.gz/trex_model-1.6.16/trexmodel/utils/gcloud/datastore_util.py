'''
Created on 27 May 2020

@author: jacklok
'''

from google.cloud import datastore
import logging


def read(client, entity_key):
    # [START datastore_basic_entity]
    entity = datastore.Entity(client.key(entity_key))
    
    logging.debug('entity=%s', entity)
    
    return entity

