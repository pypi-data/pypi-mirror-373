'''
Created on 2 Sep 2021

@author: jacklok
'''
def calc_used_topup_amount(paid_prepaid, prepaid_scheme_details):
    return paid_prepaid/prepaid_scheme_details.get('prepaid_rate')

def calc_used_bonus_amount(paid_prepaid, prepaid_scheme_details):
    return paid_prepaid - paid_prepaid/prepaid_scheme_details.get('prepaid_rate')

