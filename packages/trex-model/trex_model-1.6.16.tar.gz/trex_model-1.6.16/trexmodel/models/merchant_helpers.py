from trexmodel.models.datastore.pos_models import InvoiceNoGeneration,\
    RoundingSetup, DinningOption, PosPaymentMethod
from trexmodel.models.datastore.merchant_models import ReceiptSetup, Outlet,\
    BannerFile, MerchantAcct
from trexlib.utils.string_util import is_not_empty
from trexconf import conf
from datetime import datetime
import logging
from trexlib.utils.crypto_util import aes_encrypt_json
from trexmodel.models.datastore.customer_models import CustomerTierMembership,\
    CustomerMembership
from trexmodel.models.datastore.membership_models import MerchantMembership

logger = logging.getLogger('helper')

def construct_merchant_acct_info(merchant_acct, referrer_code=None, read_minimum=False):
    account_settings        = {
                                'account_code'  : merchant_acct.account_code,
                                'currency'      : merchant_acct.currency_code,
                                'locale'        : merchant_acct.locale,
                                'gmt_hour'      : merchant_acct.gmt_hour,   
                                }
    if read_minimum==False:
        outlet_list = Outlet.list_by_merchant_acct(merchant_acct)
        outlet_json_list = []
        for o in outlet_list:
            if o.is_physical_store:
                outlet_info = construct_outlet_info(o)
                outlet_info['industry_type'] = merchant_acct.industry
                outlet_json_list.append(outlet_info)
        
    if read_minimum==False:
        banner_file_listing =  BannerFile.list_by_merchant_acct(merchant_acct)
        banner_listing = []
        if banner_file_listing:
            for banner_file in banner_file_listing:
                banner_listing.append(banner_file.banner_file_public_url)
            
    
    invoice_no_generation   = InvoiceNoGeneration.getByMerchantAcct(merchant_acct)
    
    if invoice_no_generation:
        account_settings['invoice_settings']    = {
                                                     'invoice_no_generators'    : invoice_no_generation.generators_list,
                                                                     
                                                    }
    if read_minimum==False:
        referral_program_settings = None
        if merchant_acct.program_settings is not None:
            referral_program_settings = merchant_acct.program_settings.get('referral_program', {})
    
    
    
    
    merchant_news_list=[]
    
    if read_minimum==False:
        if merchant_acct.published_news_configuration:
            merchant_news_list = merchant_acct.published_news_configuration['news']
            
            for news in merchant_news_list:
                logger.debug('news public url=%s', news.get('news_public_url'))
        
    if read_minimum==False:
        published_redemption_catalogue_configuration = merchant_acct.published_redemption_catalogue_configuration
        catalogues_list = []    
        if published_redemption_catalogue_configuration:
            catalogues_list = published_redemption_catalogue_configuration.get('catalogues')
            
            if len(catalogues_list)>0:
                for catalogue in catalogues_list:
                    catalogue['items'] = __resolve_catalogue_items_details(catalogue.get('items'), merchant_acct.published_voucher_configuration.get('vouchers'))
                    
    
    if read_minimum==False:    
        partner_redemption_catalogue_configuration = merchant_acct.partner_redemption_catalogue_configuration
           
        if partner_redemption_catalogue_configuration:
            partner_catalogues_list = partner_redemption_catalogue_configuration.get('catalogues')
            
            if len(partner_catalogues_list)>0:
                for catalogue in partner_catalogues_list:
                    catalogue['from_partner']   = True
                    partner_merchant_account    = MerchantAcct.get_or_read_from_cache(catalogue['merchant_acct_key'])
                    catalogue['items'] = __resolve_catalogue_items_details(catalogue.get('items'), partner_merchant_account.published_voucher_configuration.get('vouchers'))            
        
                catalogues_list.extend(partner_catalogues_list)
    
    partner_merchants_list = []
    
    if read_minimum==False:
        approved_partner_merchant_configuration = merchant_acct.approved_partner_merchant_configuration
        if approved_partner_merchant_configuration and approved_partner_merchant_configuration.get('partners'):
            partner_merchants_list = list(approved_partner_merchant_configuration.get('partners').values())
            
        
    
    info =  {
                'key'                               : merchant_acct.key_in_str,
                'company_name'                      : merchant_acct.company_name,
                'name'                              : merchant_acct.brand_name,
                'brand_name'                        : merchant_acct.brand_name,
                'website'                           : merchant_acct.website,
                'account_id'                        : merchant_acct.key_in_str,
                'api_key'                           : merchant_acct.api_key,
                'logo_image_url'                    : merchant_acct.logo_public_url,
                'image_default_base_url'            : merchant_acct.image_default_base_url,
                'account_settings'                  : account_settings,
                'outlets'                           : outlet_json_list,
                'banners'                           : banner_listing,
                'merchant_news'                     : merchant_news_list,
                'redemption_catalogues'             : catalogues_list,
                'published_voucher_configuration'   : merchant_acct.published_voucher_configuration,
                'partner_merchants'                 : partner_merchants_list, 
                'industry_type'                     : merchant_acct.industry,
                } 
    if is_not_empty(referral_program_settings):
        
        refer_a_friend_url      = '{base_url}/referral/program/merchant-acct-code/{merchant_code}/referrer-code/{referrer_code}/join'
        refer_a_friend_message  = 'Hi, \n\n{referee_promote_desc}. Please join {brand_name} via below link:\n\n{refer_a_friend_url}'
        referee_promote_desc    = referral_program_settings.get('referee_promote_desc')
        
        referrer_data = {
            'merchant_acct_code': merchant_acct.account_code,
            'referrer_code': referrer_code,
            }
        
        encrypted_referrer_data = aes_encrypt_json(referrer_data)
        
        logger.debug('encrypted_referrer_data=%s', encrypted_referrer_data)
        
        logger.debug('refer_a_friend_url before=%s', refer_a_friend_url)
            
        refer_a_friend_url = refer_a_friend_url.format(
                                    base_url        = conf.REFER_BASE_URL,
                                    merchant_code   = merchant_acct.account_code,
                                    referrer_code   = referrer_code,
                                    )
        
        logger.debug('refer_a_friend_url after=%s', refer_a_friend_url)
        
        refer_a_friend_deep_link = conf.REFER_A_FRIEND_DEEP_LINK.format(
                                    #referrer_data = encrypted_referrer_data
                                    merchant_acct_code  = merchant_acct.account_code,
                                    referrer_code       = referrer_code,
                                    )
        
        referrer_merchant_and_friend_code = conf.REFERRER_MERCHANT_AND_FRIEND_CODE.format(
                                                #referrer_data = encrypted_referrer_data
                                                merchant_acct_code  = merchant_acct.account_code,
                                                referrer_code       = referrer_code,
                                                )
        
        logger.debug('refer_a_friend_deep_link=%s', refer_a_friend_deep_link)
        
        refer_a_friend_message = refer_a_friend_message.format(
                                    referee_promote_desc    = referee_promote_desc,
                                    brand_name              = merchant_acct.brand_name,
                                    refer_a_friend_url      = refer_a_friend_url,
                                    )
        logger.debug('refer_a_friend_message=%s', refer_a_friend_message)
        
        info['referral_program_settings'] = {
                                                'program_count'                     : merchant_acct.effective_referral_program_count,
                                                'referrer_promote_title'            : referral_program_settings.get('referrer_promote_title'),
                                                'referrer_promote_desc'             : referral_program_settings.get('referrer_promote_desc'),
                                                'referrer_promote_image'            : referral_program_settings.get('referrer_promote_image', conf.REFERRAL_DEFAULT_PROMOTE_IMAGE),
                                                'referee_promote_title'             : referral_program_settings.get('referee_promote_title'),
                                                'referee_promote_desc'              : referral_program_settings.get('referee_promote_desc'),
                                                'referee_promote_image'             : referral_program_settings.get('referee_promote_image'),
                                                'refer_a_friend_url'                : refer_a_friend_url,
                                                'refer_a_friend_message'            : refer_a_friend_message,
                                                'refer_a_friend_deep_link'          : refer_a_friend_deep_link,
                                                'referrer_merchant_and_friend_code' : referrer_merchant_and_friend_code,
                                                'referrer_code'                     : referrer_code,
                                            }
        
        
    
    return info

def __check_is_still_active(catalogue):
    today = datetime.utcnow().date()
    start_date  = datetime.strptime(catalogue.get('start_date'), '%d-%m-%Y').date()
    end_date    = datetime.strptime(catalogue.get('end_date'), '%d-%m-%Y').date()
    
    if today>=start_date and today<=end_date:
        logger.info('catalogue is still valid')
        return True
    else:
        logger.info('catalogue is expired')
        return False
    
def __resolve_catalogue_items_details(catalogue_items_list, vouchers_list):
    resolved_items_list = []
    voucher_dict = __convert_vouchers_list_to_dict(vouchers_list)
    for item in catalogue_items_list:
        voucher = voucher_dict.get(item.get('voucher_key'))
        if voucher:
            resolved_items_list.append(
                    {
                        'voucher_key'           : item.get('voucher_key'),
                        'amount'                : item.get('voucher_amount'),
                        'label'                 : voucher.get('label'),
                        'image_url'             : voucher.get('image_url'),
                        'terms_and_conditions'  : voucher.get('terms_and_conditions'),
                        'redeem_reward_amount'  : item.get('redeem_reward_amount'),
                    }
                
                )
        else:
            resolved_items_list.append(item)
        
    return resolved_items_list    

def __convert_vouchers_list_to_dict(vouchers_list):
    voucher_dict = {}
    for voucher in vouchers_list:
        voucher_dict[voucher.get('voucher_key')] = voucher
    
    return voucher_dict

def construct_outlet_info(outlet):
    geo_location = None
    if outlet.geo_location:
        geo_location = '%s,%s' % (outlet.geo_location.latitude, outlet.geo_location.longitude)
    return {
            'outlet_key'        : outlet.key_in_str,
            'outlet_name'       : outlet.name,
            'address'           : outlet.address,
            'business_hour'     : outlet.business_hour,
            'geo_location'      : geo_location,
            
        }

def construct_setting_by_outlet(outlet, device_setting=None, is_pos_device=False):


    merchant_acct           = outlet.merchant_acct_entity
    invoice_no_generation   = InvoiceNoGeneration.getByMerchantAcct(merchant_acct)
    rounding_setup          = RoundingSetup.get_by_merchant_acct(merchant_acct)
    receipt_setup           = ReceiptSetup.get_by_merchant_acct(merchant_acct)
    dinning_option_json     = []
    dinning_option_list     = DinningOption.list_by_merchant_acct(merchant_acct)
    
    account_settings        = {
                                'account_code'  : merchant_acct.account_code,
                                'currency'      : merchant_acct.currency_code,
                                'locale'        : merchant_acct.locale,    
                                'gmt_hour'      : merchant_acct.gmt_hour,    
                                }
    
    logger.info('is_pos_device=%s', is_pos_device)
    if is_pos_device:
        if dinning_option_list:
            for d in dinning_option_list:
                dinning_option_json.append({
                                            'option_key'                : d.key_in_str,
                                            'option_name'               : d.name,
                                            'option_prefix'             : d.prefix,
                                            'is_default'                : d.is_default,
                                            'is_dinning_input'          : d.is_dinning_input,
                                            'is_delivery_input'         : d.is_delivery_input,
                                            'is_takeaway_input'         : d.is_takeaway_input,
                                            'is_self_order_input'       : d.is_self_order_input,
                                            'is_self_payment_mandatory' : d.is_self_payment_mandatory,
                                            'dinning_table_is_required' : d.dinning_table_is_required,
                                            'assign_queue'              : d.assign_queue,
                                            })
    
    if is_pos_device:
        account_settings['dinning_option_list'] = dinning_option_json
        account_settings['package_type']        = merchant_acct.pos_package
    else:
        account_settings['package_type']        = merchant_acct.loyalty_package
        
    if invoice_no_generation:
        account_settings['invoice_settings']    = {
                                                     'invoice_no_generators'    : invoice_no_generation.generators_list,
                                                                     
                                                    }
    else:
        account_settings['invoice_settings'] = {}
    
    if receipt_setup:
        account_settings['receipt_settings'] = {
                                                'header_data_list': receipt_setup.receipt_header_settings,
                                                'footer_data_list': receipt_setup.receipt_footer_settings or [],
                                                }
    
    if rounding_setup:
        account_settings['rounding_settings']     = {
                                                    'rounding_interval' : rounding_setup.rounding_interval,
                                                    'rounding_rule'     : rounding_setup.rounding_rule,
                                                    }
    pos_payment_method_json = []
    pos_payment_method_list = PosPaymentMethod.list_by_merchant_acct(merchant_acct)
    
    if pos_payment_method_list:
        for d in pos_payment_method_list:
            pos_payment_method_json.append({
                                        'code'                  : d.code,
                                        'key'                   : d.key_in_str,
                                        'label'                 : d.label,
                                        'is_default'            : d.is_default,
                                        'is_rounding_required'  : d.is_rounding_required,
                                        })
    
    if is_pos_device:
        account_settings['assigned_service_charge_setup']   = outlet.service_charge_settings
        account_settings['assigned_tax_setup']              = outlet.assigned_tax_setup
        account_settings['dinning_table_list']              = outlet.assigned_dinning_table_list
        account_settings['show_dinning_table_occupied']     = outlet.show_dinning_table_occupied
        account_settings['payment_methods']                 = pos_payment_method_json
    
    
    outlet_details = {
                    'key'                        : outlet.key_in_str,
                    'id'                         : outlet.id,
                    'outlet_name'                : outlet.name,
                    'company_name'               : outlet.company_name,
                    'brand_name'                 : merchant_acct.brand_name,
                    'business_reg_no'            : outlet.business_reg_no,
                    'address'                    : outlet.address,
                    'email'                      : outlet.email,
                    'phone'                      : outlet.office_phone,
                    'website'                    : merchant_acct.website or '',  
                    'industry_type'              : merchant_acct.industry,
                    'gmt_hour'                   : merchant_acct.gmt_hour,   
                    }
    
    program_configurations = {
                            'prepaid_configuration' : merchant_acct.prepaid_configuration,
                            'days_of_return_policy' : merchant_acct.program_settings.get('days_of_return_policy') if merchant_acct.program_settings is not None else MerchantAcct.default_program_settings().get('days_of_return_policy'),
                            }
    
    setting =  {
                'company_name'                      : merchant_acct.company_name,
                'brand_name'                        : merchant_acct.brand_name,
                'website'                           : merchant_acct.website,
                'account_id'                        : merchant_acct.key_in_str,
                'api_key'                           : merchant_acct.api_key,
                'logo_image_url'                    : merchant_acct.logo_public_url,
                'image_default_base_url'            : merchant_acct.image_default_base_url,
                'account_settings'                  : account_settings,
                'outlet_details'                    : outlet_details,
                'program_configurations'            : program_configurations,
                'membership_configurations'         : merchant_acct.membership_configuration, 
                'rating_review'                     : merchant_acct.program_settings.get('rating_review', False) if merchant_acct.program_settings is not None else MerchantAcct.default_program_settings().get('rating_review', False),
                } 
    if device_setting:
        setting['activation_code']              = device_setting.activation_code
        setting['device_name']                  = device_setting.device_name
        setting['device_id']                    = device_setting.device_id
        setting['enable_lock_screen']           = device_setting.enable_lock_screen
        setting['lock_screen_code']             = device_setting.lock_screen_code
        setting['lock_screen_length_in_second'] = device_setting.lock_screen_length_in_second
        
    return setting

def convert_points_between_merchants(
    required_points_a: float,
    merchant_a_point_value: float,
    merchant_b_point_value: float
    ) -> float:
    """
    Convert Merchant A's required points into Merchant B's equivalent points.
    """
    # Convert required points to monetary value
    monetary_value = required_points_a * merchant_a_point_value
    
    # Convert monetary value to Merchant B points
    required_points_b = monetary_value / merchant_b_point_value
    
    return round(required_points_b, 2)

def return_customer_details(customer):
    customer_details_dict = customer.to_dict(
                                        date_format="%d-%m-%Y", 
                                        datetime_format="%d-%m-%Y %H:%M:%S",
                                        excluded_dict_properties = [
                                                'registered_merchant_acct', 
                                                'memberships_list', 
                                                'tier_membership_key',
                                                'registered_user_acct',
                                                
                                                ],
                                        )
    customer_details_dict['customer_key']               = customer.key_in_str
    
    
    customer_basic_memberships_list = _list_customer_basic_memberships(customer)
    if customer_basic_memberships_list:
        customer_details_dict['basic_memberships'] = customer_basic_memberships_list
    
    customer_tier_membership = _get_tier_membership(customer)
    if customer_tier_membership:
        customer_details_dict['tier_membership']  = customer_tier_membership
    
    if 'entitled_voucher_summary' in customer_details_dict:
        customer_details_dict['voucher_summary']            = customer.entitled_voucher_summary
        del customer_details_dict['entitled_voucher_summary']
    
    return customer_details_dict

def _list_customer_basic_memberships(customer):
    customer_membership_final_list = []
    
    if is_not_empty(customer.memberships_list):
        customer_memberships_list = CustomerMembership.list_all_by_customer(customer)
        if is_not_empty(customer_memberships_list):
            merchant_acct = customer.registered_merchant_acct
            merchant_memberships_list = MerchantMembership.list_by_merchant_acct(merchant_acct)
            
            for cm in customer_memberships_list:
                for mm in merchant_memberships_list:
                    logger.debug('cm=%s', cm)
                    if mm.key_in_str == cm.merchant_membership_key:
                        membership_data = {
                                                        'key'                   : mm.key_in_str,
                                                        'label'                 : mm.label,
                                                        'card_image'            : mm.membership_card_image,
                                                        'desc'                  : mm.desc if is_not_empty(mm.desc) else '',
                                                        'terms_and_conditions'  : mm.terms_and_conditions if is_not_empty(mm.terms_and_conditions) else '',
                                                        'is_tier'               : False,
                                                        'entitled_date'         : cm.entitled_date.strftime('%d-%m-%Y'),
                                                        'expiry_date'           : cm.expiry_date.strftime('%d-%m-%Y'),
                                                        
                                                        }
                        
                        if cm.renewed_date is not None:
                            membership_data['renewed_date'] = cm.renewed_date.strftime('%d-%m-%Y'),
                        
                        customer_membership_final_list.append(membership_data)
                        break
    return customer_membership_final_list

def _get_tier_membership(customer):
            
    if is_not_empty(customer.tier_membership):
        merchant_tier_membership = customer.tier_membership_entity
        customer_tier_membership = CustomerTierMembership.get_by_customer_and_merchant_tier_membership(customer, merchant_tier_membership)
        
        membership_data = {
                        'key'                   : customer_tier_membership.merchant_tier_membership_key,
                        'label'                 : merchant_tier_membership.label,
                        'card_image'            : merchant_tier_membership.membership_card_image,
                        'desc'                  : merchant_tier_membership.desc if is_not_empty(merchant_tier_membership.desc) else '',
                        'terms_and_conditions'  : merchant_tier_membership.terms_and_conditions if is_not_empty(merchant_tier_membership.terms_and_conditions) else '',
                        'entitled_date'         : customer_tier_membership.entitled_date.strftime('%d-%m-%Y'),
                        'expiry_date'           : customer_tier_membership.expiry_date.strftime('%d-%m-%Y'),
                        'is_tier'               : True,
                        }
        
        return membership_data