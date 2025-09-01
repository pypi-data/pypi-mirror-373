'''
Created on 19 Feb 2021

@author: jacklok
'''
from trexmodel.models.datastore.program_models import MerchantProgram

class MerchantRewardProgramSpendingBase(MerchantProgram):
    
    @classmethod
    def create(cls, merchant_acct, desc=None, start_date=None, end_date=None, program_settings=None):
        program = cls(
                    merchant_acct   = merchant_acct.create_ndb_key(),
                    desc            = desc,
                    start_date      = start_date,
                    end_date        = end_date,
                    
                    )
        program.put()
