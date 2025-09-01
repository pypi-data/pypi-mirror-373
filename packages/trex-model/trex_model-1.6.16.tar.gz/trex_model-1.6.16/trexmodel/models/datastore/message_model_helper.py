'''
Created on 9 Nov 2023

@author: jacklok
'''
from trexmodel.program_conf import REWARD_FORMAT_MAP, REWARD_FORMAT_PREPAID
from trexmodel.models.datastore.message_models import Message
from trexconf.conf import MESSAGE_CATEGORY_REWARD, MESSAGE_STATUS_NEW,\
    MESSAGE_CATEGORY_REDEEM, MESSAGE_CATEGORY_REDEMPTION_CATALOGUE,\
    MESSAGE_CATEGORY_PAYMENT
from trexconf import program_conf
from babel.numbers import format_currency
import logging
from flask_babel import gettext
from trexlib.utils.string_util import is_not_empty


logger = logging.getLogger('helper')

entitled_reward_message_template = '''{amount} {reward_format}'''
                                    
entitled_voucher_message_template = '''{amount} voucher - {label}'''

redeemed_voucher_message_template = '''{amount} voucher - {label}'''
                                    
entitled_lucky_draw_message_template = '''{amount} lucky draw ticket(s)'''                                                                        


entitled_messages_template = '''
<html>
 
    <head>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.2.3/css/bootstrap.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.2.3/js/bootstrap.bundle.min.js"></script>
    </head>
    <body>
    
    <table cellpadding="0" cellspacing="0"
       style="width: 100%; height: 100%; background-color: #f4f4f5; text-align: center;">
        <tbody>
        <tr>
            <td style="text-align: center;">
                <table align="center" cellpadding="0" cellspacing="0" id="body" style="background-color: #fff; width: 100%; max-width: 680px; height: 100%;">
                    <tbody>
                    <tr>
                        <td>
                            <table align="center" cellpadding="0" cellspacing="0" class="page-center"
                                   style="text-align: left; padding-bottom: 88px; width: 100%; padding-left: 120px; padding-right: 120px;">
                                <tbody>
                                {message_banner_image}
                                {message_congrat_image}
                                <tr>
                                    <td width="20%">&nbsp;</td>
                                    <td width="60%" class="pt-3">
                                        <p class="text-left">You have entitled</p>
                                        <div class="pl-3">
                                        <ul class="pt-3">
                                        {message_list}
                                            </ul>
                                        </div>
                                    </td>
                                    <td width="20%">&nbsp;</td>
                                </tr>
                                
                                <tr>
                                    <td width="20%">&nbsp;</td>
                                    <td width="60%" class="text-left pt-5">
                                        <p>From</p>
                                        
                                        {merchant_logo}
                                        
                                    </td>
                                    <td width="20%">&nbsp;</td>
                                </tr>
    
                                <tr>
                                    <td colspan="100%" style="padding-top: 48px; padding-bottom: 48px;">
                                        <table cellpadding="0" cellspacing="0" style="width: 100%>
                                            <tbody>
                                            <tr>
                                                <td style="width: 100%; height: 1px; max-height: 1px; background-color: #d9dbe0; opacity: 0.81">
                                                </td>
                                            </tr>
                                            </tbody>
                                        </table>
                                    </td>
                                </tr>
                                
    
    
                                </tbody>
                            </table>
                        </td>
                    </tr>
                    </tbody>
                </table>
            </td>
        </tr>
        </tbody>
    </table>
    

    </body>
</html>
                                '''


message_banner_image_template = '''
<tr>
    <td colspan="100%" class="text-center pt-3">
        <img src="https://storage.googleapis.com/augmigo-image-storage/app/customer-rewards-min.png"
             style="width: auto;height:250px"/>
    </td>
</tr>
'''

message_congrat_image_template = '''
<tr>
    <td colspan="100%" class="text-center">
        <img src="https://storage.googleapis.com/augmigo-image-storage/app/congratulations-min.png"
             style="width: auto;height:150px"/>
    </td>
</tr>
'''

message_logo_image_template = '''
<tr>
    <td width="20%">&nbsp;</td>
    <td width="60%" class="text-left pt-5">
        <p>From</p>
        <div class="pl-3">
        <img src="{merchant_logo}"
             style="width: auto;height:100px"/>
        </div>     
    </td>
    <td width="20%">&nbsp;</td>
</tr>
'''






def create_transaction_message(customer_transaction, remarks=None, title=None, message_category=None):
    user_acct       = customer_transaction.transact_user_acct
    source_key      = customer_transaction.key_in_str
    customer        = customer_transaction.transact_customer_acct
    merchant_acct   = customer.registered_merchant_acct
    message         = Message.get_by_source_key(source_key)
    
    if message is None:
        message = Message(
                    parent              = user_acct.create_ndb_key(),
                    message_to          = user_acct.create_ndb_key(),
                    title               = title if is_not_empty(title) else 'Transaction Reward',
                    message_category    = message_category if is_not_empty(message_category) else MESSAGE_CATEGORY_REWARD,
                    message_content     = __create_entiled_message_from_customer_transaction(customer_transaction, remarks=remarks),
                    message_data        = __create_message_data_from_transaction(customer_transaction),
                    status              = MESSAGE_STATUS_NEW,
                    message_from        = merchant_acct.brand_name, 
                    )
        message.put()
        #user_acct.new_message_count+=1
        #user_acct.put()
        
    return message
    
def create_redemption_message(customer_redemption):
    user_acct       = customer_redemption.redeemed_user_acct
    merchant_acct   = customer_redemption.redeemed_merchant_acct
    source_key      = customer_redemption.key_in_str
    message = Message.get_by_source_key(source_key)
    
    if message is None:
        message = Message(
                    parent              = user_acct.create_ndb_key(),
                    source_key          = source_key,
                    message_to          = user_acct.create_ndb_key(),
                    title               = 'Redemption',
                    message_category    = MESSAGE_CATEGORY_REDEEM,
                    message_content     = __create_message_from_redeem_transaction(merchant_acct, customer_redemption),
                    message_data        = __create_message_data_from_redemption(customer_redemption),
                    status              = MESSAGE_STATUS_NEW,
                    message_from        = merchant_acct.brand_name, 
                    )
        message.put()
        #user_acct.new_message_count+=1
        #user_acct.put()
            
    return message

def create_payment_message(customer_redemption):
    user_acct       = customer_redemption.redeemed_user_acct
    merchant_acct   = customer_redemption.redeemed_merchant_acct
    source_key      = customer_redemption.key_in_str
    message = Message.get_by_source_key(source_key)
    
    if message is None:
        message = Message(
                    parent              = user_acct.create_ndb_key(),
                    source_key          = source_key,
                    message_to          = user_acct.create_ndb_key(),
                    title               = 'Payment',
                    message_category    = MESSAGE_CATEGORY_PAYMENT,
                    message_content     = __create_message_from_redeem_transaction(merchant_acct, customer_redemption),
                    message_data        = __create_message_data_from_redemption(customer_redemption),
                    status              = MESSAGE_STATUS_NEW,
                    message_from        = merchant_acct.brand_name, 
                    )
        message.put()
        #user_acct.new_message_count+=1
        #user_acct.put()
            
    return message

    
def create_redeem_catalogue_item_message(customer, entitled_vouchers_summary, redemption_catalogue_transaction):
    user_acct       = customer.registered_user_acct
    merchant_acct   = customer.registered_merchant_acct
    source_key      = redemption_catalogue_transaction.key_in_str
    message         = Message.get_by_source_key(source_key)
    
    if message is None:
        message = Message(
                    parent              = user_acct.create_ndb_key(),
                    message_to          = user_acct.create_ndb_key(),
                    title               = gettext('Redemption Catalogue Reward'),
                    message_category    = MESSAGE_CATEGORY_REDEMPTION_CATALOGUE,
                    message_content     = __create_message_from_redeem_catalogue_transaction(customer, entitled_vouchers_summary),
                    message_data        = __create_message_data_from_redemption_catalogue(redemption_catalogue_transaction),
                    status              = MESSAGE_STATUS_NEW,
                    message_from        = merchant_acct.brand_name,    
                    
                    )
        message.put()
        #user_acct.new_message_count+=1
        #user_acct.put()  
    
    return message  

def __create_message_data_from_transaction(customer_transaction):
    return {
            'reward_transaction_key'   : customer_transaction.key_in_str,
            
            }
    
def __create_message_data_from_redemption_catalogue(redemption_catalogue_transaction):
    return {
            'redemption_catalogue_transaction_key'   : redemption_catalogue_transaction.key_in_str,
            
            }
    
def __create_message_data_from_redemption(redemption_transaction):
    return {
            'redemption_transaction_key'   : redemption_transaction.key_in_str,
            
            }        

def __create_entiled_message_from_customer_transaction(customer_transaction, remarks=None):

    entitled_messages_list = []
    if customer_transaction.entitled_reward_summary:
        entitled_messages_list.extend(__create_entitled_reward_message(customer_transaction))
        
    if customer_transaction.entitled_prepaid_summary:
        entitled_messages_list.extend(__create_entitled_prepaid_message(customer_transaction))    
    
    if customer_transaction.entitled_voucher_summary:
        entitled_messages_list.extend(__create_entitled_voucher_message(customer_transaction))
    
    if customer_transaction.entitled_lucky_draw_ticket_summary:    
        entitled_messages_list.extend(__create_entitled_lucky_draw_ticket_message(customer_transaction))
    
    message_list = []
    merchant_acct = customer_transaction.transact_merchant_acct
    merchant_logo = merchant_acct.logo_public_url
    
    messages_for_json_list = []
    
    header_message_list = [
                            {
                            'type': 'image',
                            'value': {
                                        'url': 'https://storage.googleapis.com/augmigo-image-storage/app/customer-rewards-min.png',
                                        'height': 100,
                                    }
                            
                            },
                            {
                            'type': 'image',    
                            'value': {
                                    'url': 'https://storage.googleapis.com/augmigo-image-storage/app/congratulations-min.png',
                                    'height': 80,
                                    }
                            
                            },
                        ]
    
    if is_not_empty(remarks):
        header_message_list.append({
                                    'type'      : 'text',
                                    'value'     : remarks,
                                    'font-size' : 20,
                                    })
    
    for message in entitled_messages_list:
        message_list.append('<li class="pt-2">{message}</li>'.format(message=message))
        messages_for_json_list.append({
                                    'type'      : 'text',
                                    'value'     : message,
                                    'font-size' : 20,
                                    })
    
    return {
            'type'      : 'json',
            'content'   : {
                            'header':header_message_list,
                            'title':[
                                        {
                                        'type':'text',
                                        'value': 'You have entitled',
                                        'font-size': 25,
                                        }
                                    ],
                            
                            'body':messages_for_json_list,
                            
                            'footer':[
                                
                                    {
                                        'type':'text',
                                        'value': 'From',
                                        'font-size': 25,
                                    },
                                    {
                                        'type':'image',
                                        'value': {
                                                'url': merchant_logo,
                                                'height': 100,
                                            }
                                        }
                                ]
                            }
        }
    
def __create_message_from_redeem_catalogue_transaction(customer, entitled_vouchers_summary):

    entitled_messages_list = []
    
    message_list = []
    merchant_acct = customer.registered_merchant_acct
    merchant_logo = merchant_acct.logo_public_url
    
    messages_for_json_list = []
    
    entitled_messages_list.extend(__create_entitled_voucher_message_from_entitled_voucher_summary(entitled_vouchers_summary))
    
    for message in entitled_messages_list:
        message_list.append('<li class="pt-2">{message}</li>'.format(message=message))
        messages_for_json_list.append({
                                    'type'      : 'text',
                                    'value'     : message,
                                    'font-size' : 20,
                                    })
    
    return {
            'type'      : 'json',
            'content'   : {
                            'header':[
                                    {
                                    'type': 'image',
                                    'value': {
                                                'url': 'https://storage.googleapis.com/augmigo-image-storage/app/customer-rewards-min.png',
                                                'height': 100,
                                            }
                                    
                                    },
                                    {
                                    'type': 'image',    
                                    'value': {
                                            'url': 'https://storage.googleapis.com/augmigo-image-storage/app/congratulations-min.png',
                                            'height': 80,
                                            }
                                    
                                    },
                                ],
                            'title':[
                                        {
                                        'type':'text',
                                        'value': 'You have entitled',
                                        'font-size': 25,
                                        }
                                    ],
                            
                            'body':messages_for_json_list,
                            
                            'footer':[
                                
                                    {
                                        'type':'text',
                                        'value': 'From',
                                        'font-size': 25,
                                    },
                                    {
                                        'type':'image',
                                        'value': {
                                                'url': merchant_logo,
                                                'height': 100,
                                            }
                                        }
                                ]
                            }
        }    

def __create_message_from_redeem_transaction(merchant_acct, customer_redemption):

    messages_list   = []
    
    message_list    = []
    #merchant_logo   = merchant_acct.logo_public_url
    brand_name      = merchant_acct.brand_name
    
    messages_for_json_list = []
    
    messages_list.extend(__create_customer_redemption_message(customer_redemption))
    
    for message in messages_list:
        message_list.append('<li class="pt-2">{message}</li>'.format(message=message))
        messages_for_json_list.append({
                                    'type'      : 'text',
                                    'value'     : message,
                                    'font-size' : 20,
                                    })
    
    return {
            'type'      : 'json',
            'content'   : {
                            'header':[
                                    {
                                    'type': 'text',
                                    'value': 'Redemption'
                                    
                                    },
                                ],
                            'title':[
                                        {
                                        'type':'text',
                                        'value': __create_customer_redemption_title(customer_redemption),
                                        'font-size': 25,
                                        }
                                    ],
                            
                            'body':messages_for_json_list,
                            
                            'footer':[
                                
                                    {
                                        'type':'text',
                                        'value': 'To %s' % brand_name,
                                        'font-size': 25,
                                    }
                                ]
                            }
            }    
    
def __create_entitled_reward_message(customer_transaction):    
    entitled_reward_summary             = customer_transaction.entitled_reward_summary
    entitled_messages_list = []
    for reward_format, reward_details in  entitled_reward_summary.items():
        if reward_details.get('amount')>0:
            entitled_messages_list.append(
                    entitled_reward_message_template.format(
                        amount          = reward_details.get('amount'),
                        reward_format   = REWARD_FORMAT_MAP.get(reward_format),
                        )
                    )
            
    return entitled_messages_list

def __create_entitled_prepaid_message(customer_transaction):    
    entitled_prepaid_summary             = customer_transaction.entitled_prepaid_summary
    entitled_messages_list = [
                                entitled_reward_message_template.format(
                                    amount          = entitled_prepaid_summary.get('amount'),
                                    reward_format   = REWARD_FORMAT_MAP.get(REWARD_FORMAT_PREPAID),
                                    )
                                ]
    return entitled_messages_list

def __create_entitled_voucher_message(customer_transaction):    
    entitled_voucher_summary             = customer_transaction.entitled_voucher_summary
    entitled_messages_list = []
    for voucher_key, voucher_details in  entitled_voucher_summary.items():
        entitled_messages_list.append(
                entitled_voucher_message_template.format(
                    label           = voucher_details.get('label'),
                    amount          = voucher_details.get('amount'),
                    )
                )
            
    return entitled_messages_list

def __create_entitled_voucher_message_from_entitled_voucher_summary(entitled_vouchers_summary):    
    entitled_messages_list = []
    for voucher_key, voucher_details in  entitled_vouchers_summary.items():
        entitled_messages_list.append(
                entitled_voucher_message_template.format(
                    label           = voucher_details.get('label'),
                    amount          = voucher_details.get('amount'),
                    )
                )
            
    return entitled_messages_list

def __create_customer_redemption_message(customer_redemption):
    messages_list = []    
    if customer_redemption.reward_format == program_conf.FEATURE_CODE_PREPAID_REWARD_FORMAT:
        merchant_acct = customer_redemption.redeemed_merchant_acct
        
        logger.debug('redeemed_amount=%d', customer_redemption.redeemed_amount)
        logger.debug('currency_code=%s', merchant_acct.currency_code)
        
        formated_redeem_amount = format_currency(customer_redemption.redeemed_amount, 
                                                 merchant_acct.currency_code,
                                                 u'#,##0.00',
                                                 locale='en_US',
                                                 currency_digits=False,
                                                 )
        logger.debug('formated_redeem_amount=%s', formated_redeem_amount)
        
        messages_list.append("%s prepaid" % (formated_redeem_amount))
        
    elif customer_redemption.reward_format == program_conf.FEATURE_CODE_VOUCHER_REWARD_FORMAT:
        redeemed_summary = customer_redemption.redeemed_summary
        redeemed_vouchers_list = redeemed_summary.get('voucher').get('vouchers')
        for voucher_key, voucher_details in redeemed_vouchers_list.items():
            
            messages_list.append(
                    redeemed_voucher_message_template.format(
                        label           = voucher_details.get('label'),
                        amount          = voucher_details.get('amount'),
                        )
                    )
        
    return messages_list

def __create_customer_redemption_title(customer_redemption):
    
    if customer_redemption.reward_format == program_conf.FEATURE_CODE_PREPAID_REWARD_FORMAT:
        return "You have paid"
        
    elif customer_redemption.reward_format == program_conf.FEATURE_CODE_VOUCHER_REWARD_FORMAT:
        return "You have redeemed"

def __create_entitled_lucky_draw_ticket_message(customer_transaction):    
    entitled_lucky_draw_ticket_summary             = customer_transaction.entitled_lucky_draw_ticket_summary
    entitled_messages_list = [
        entitled_lucky_draw_message_template.format(
                    amount           = entitled_lucky_draw_ticket_summary.get('count'),
                    )
                
        ]
            
    return entitled_messages_list
''
