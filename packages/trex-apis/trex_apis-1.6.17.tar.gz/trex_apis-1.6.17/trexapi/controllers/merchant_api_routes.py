'''
Created on 30 Jun 2021

@author: jacklok
'''

from flask import Blueprint, request
import flask 
from flask_restful import Resource, abort
import logging
from trexlib.utils.log_util import get_tracelog
from flask_httpauth import HTTPBasicAuth
from trexconf import conf
from flask_restful import Api
from trexmodel.utils.model.model_util import create_db_client
from trexmodel.models.datastore.merchant_models import MerchantUser,\
    MerchantAcct, Outlet
import hashlib
from trexlib.utils.string_util import is_not_empty
from flask.json import jsonify
from trexapi import conf as api_conf
from trexapi.decorators.api_decorators import auth_token_required,\
    user_auth_token_required_pass_reference_code, user_auth_token_required
from trexmodel.models.datastore.loyalty_models import LoyaltyDeviceSetting
from trexmodel.models.datastore.pos_models import POSSetting
from trexapi.controllers.api_routes import APIBaseResource
from trexmodel.models import merchant_helpers
from trexmodel.models.datastore.customer_models import Customer,\
    CustomerMembership, CustomerTierMembership
from trexmodel.models.datastore.rating_models import MerchantRatingResult
from trexmodel.models.datastore.membership_models import MerchantMembership
from trexapi.utils.api_helpers import StatusCode, create_api_message
from trexapi.libs.api_decorator import elapsed_time_trace
from trexmodel.models.datastore.user_models import User
from trexlib.utils.crypto_util import aes_encrypt_json
from trexlib.libs.flask_wtf.request_wrapper import request_headers,\
    request_values, request_json

#logger = logging.getLogger('api')
logger = logging.getLogger('target_debug')

auth = HTTPBasicAuth()
#auth = HTTPBasicAuthWrapper()


merchant_api_bp = Blueprint('merchant_api_bp', __name__,
                                 template_folder='templates',
                                 static_folder='static',
                                 url_prefix='/api/v1/merchant')

merchant_api = Api(merchant_api_bp)



@merchant_api_bp.route('/ping', methods=['GET'])
def ping():
    return 'Pong', 200

@auth.verify_password
def verify_user_auth(username, password):
    if not (username and password):
        return False
    
    db_client   = create_db_client(caller_info="verify_user_auth")
    valid_auth  = False
    
    logger.debug('username=%s', username)
    logger.debug('password=%s', password)
    
    with db_client.context():
        merchant_user = MerchantUser.get_by_username(username)
        
        logger.debug('merchant_user=%s', merchant_user)
        
        if merchant_user:
            
            md5_hashed_password = hashlib.md5(password.encode('utf-8')).hexdigest()
            
            logger.debug('verify_user_auth: md5_hashed_password=%s', md5_hashed_password)
            
            if merchant_user.is_valid_password(md5_hashed_password):
                valid_auth = True
            else:
                logger.warn('Invalid merchant password')
        else:
            logger.warn('Invalid merchant username=%s', username)    
        
    return valid_auth

@merchant_api_bp.route('/<merchant_acct_code>/details', methods=['GET'])
@user_auth_token_required_pass_reference_code
def read_merchant_acct(merchant_acct_code, reference_code):
    
    merchant_acct           = None
    
    logger.debug('merchant_acct_code=%s', merchant_acct_code)
    logger.debug('reference_code=%s', reference_code)
    
    if is_not_empty(merchant_acct_code):
        db_client = create_db_client(caller_info="read_merchant_acct")
        try:
            with db_client.context():
                merchant_acct   = MerchantAcct.get_by_account_code(merchant_acct_code)
                logger.debug('merchant_acct=%s', merchant_acct)
                user_acct       = User.get_by_reference_code(reference_code)
                logger.debug('user_acct=%s', user_acct)
                #logger.debug('industry=%s', merchant_acct.industry)
                merchant_info = merchant_helpers.construct_merchant_acct_info(merchant_acct, referrer_code = user_acct.referral_code) 
                logger.debug('merchant_info.industry_type=%s', merchant_info.get('industry_type'))
                
                merchant_rating_result  = MerchantRatingResult.get_by_merchant_acct(merchant_acct)
                
                
                if merchant_rating_result:
                    logger.debug('rating_result=%s', merchant_rating_result.rating_result)
                    merchant_info['rating_result'] = {
                                                        'score'                 : merchant_rating_result.score,
                                                        'total_rating_count'    : merchant_rating_result.score,
                                                        'reviews_details'       : merchant_rating_result.rating_result,
                                                    }
                
                    
            #logger.debug('merchant_info=%s', merchant_info)
                
            return create_api_message(status_code=StatusCode.OK,
                                                   **merchant_info
                                                   )
        except:
            logger.error('Failed due to %s', get_tracelog())
            return create_api_message("Failed to read merchant details", status_code=StatusCode.BAD_REQUEST)
    else:
        return create_api_message("Missing merchant account key", status_code=StatusCode.BAD_REQUEST)
    
@merchant_api_bp.route('/<merchant_acct_code>/minimum-details-for-system', methods=['GET'])
def read_minimum_merchant_acct_for_system(merchant_acct_code):
    
    merchant_acct           = None
    
    logger.debug('merchant_acct_code=%s', merchant_acct_code)
    
    if is_not_empty(merchant_acct_code):
        db_client = create_db_client(caller_info="read_minimum_merchant_acct_for_system")
        with db_client.context():
            merchant_acct   = MerchantAcct.get_by_account_code(merchant_acct_code)
            merchant_info = merchant_helpers.construct_merchant_acct_info(merchant_acct, read_minimum=True) 
            
        return create_api_message(status_code=StatusCode.OK,
                                               **merchant_info
                                               )
    else:
        return create_api_message("Missing merchant account key", status_code=StatusCode.BAD_REQUEST)
        
    
@merchant_api_bp.route('/<merchant_acct_code>/referred-code/<referrer_code>/read-details', methods=['GET'])
@request_values
def read_customer_brief_and_merchant_acct_and_referred_code(request_values, merchant_acct_code, referrer_code):
    
    reference_code = request_values.get('reference_code')
    
    logger.debug('merchant_acct_code=%s', merchant_acct_code)
    logger.debug('referrer_code=%s', referrer_code)
    logger.debug('reference_code=%s', reference_code)
    
    db_client = create_db_client(caller_info="read_customer_brief_and_merchant_acct_from_referred_code")
    customer_acct = None
    
    with db_client.context():
        merchant_acct   = MerchantAcct.get_by_account_code(merchant_acct_code)
        
    if is_not_empty(reference_code):
        with db_client.context():
            customer_acct   = Customer.get_by_reference_code(reference_code, merchant_acct)
            
    
    if is_not_empty(merchant_acct_code):
        try:
            with db_client.context():
                merchant_info   = merchant_helpers.construct_merchant_acct_info(merchant_acct, referrer_code=referrer_code) 
                referrer_user   = User.get_by_referral_code(referrer_code)
                '''
                if merchant_info and referrer_user:
                    
                    if merchant_info.get('referral_program_settings'):
                        
                        refer_a_friend_url      = '{base_url}/referral/program/merchant-code/{merchant_code}/referrer-code/{referrer_code}/join'
                        refer_a_friend_message  = 'Hi, \n\n{referee_promote_desc}. Please join {brand_name} via below link:\n\n{refer_a_friend_url}'
                        referee_promote_desc    = merchant_info.get('referral_program_settings').get('referee_promote_desc')
                        
                        referrer_data = {
                            'merchant_acct_code': merchant_acct_code,
                            'referrer_code': referrer_code,
                            }
                        
                        encrypted_referrer_data = aes_encrypt_json(referrer_data)
                        
                        logger.debug('encrypted_referrer_data=%s', encrypted_referrer_data)
                        
                        logger.debug('refer_a_friend_url before=%s', refer_a_friend_url)
                            
                        refer_a_friend_url = refer_a_friend_url.format(
                                                    base_url        = conf.REFER_BASE_URL,
                                                    merchant_code   = merchant_acct_code,
                                                    referrer_code   = referrer_code,
                                                    )
                        
                        logger.debug('refer_a_friend_url after=%s', refer_a_friend_url)
                        
                        refer_a_friend_deep_link = conf.REFER_A_FRIEND_DEEP_LINK.format(
                                                    referrer_data = encrypted_referrer_data
                                                    )
                        
                        logger.debug('refer_a_friend_deep_link=%s', refer_a_friend_deep_link)
                        
                        refer_a_friend_message = refer_a_friend_message.format(
                                                    referee_promote_desc    = referee_promote_desc,
                                                    brand_name              = merchant_acct.brand_name,
                                                    refer_a_friend_url      = refer_a_friend_url,
                                                    )
                        logger.debug('refer_a_friend_message=%s', refer_a_friend_message)
                        
                        merchant_info['referral_program_settings']['refer_a_friend_url']        = refer_a_friend_url
                        merchant_info['referral_program_settings']['refer_a_friend_message']    = refer_a_friend_message
                        merchant_info['referral_program_settings']['refer_a_friend_deep_link']  = refer_a_friend_deep_link
                        
                    merchant_rating_result  = MerchantRatingResult.get_by_merchant_acct(merchant_acct)
                    
                    
                    
                    if merchant_rating_result:
                        logger.debug('rating_result=%s', merchant_rating_result.rating_result)
                        merchant_info['rating_reviews'] = merchant_rating_result.rating_result
                '''
        except:
            logger.error('faield due to %s', get_tracelog())
        
        if referrer_user is None or merchant_info is None:  
            
            return create_api_message(status_code=StatusCode.BAD_REQUEST)
        else:   
                
            logger.debug('merchant_info=%s', merchant_info)
            
            data = {
                        'merchant_info' : merchant_info,
                        'referrer_name' : referrer_user.name,
                        }
            
            if customer_acct is not None:
                data['customer_brief'] = {
                                        'name'              : customer_acct.name,
                                        'reference_code'    : reference_code,
                                        'customer_key'      : customer_acct.key_in_str,
                                        }
                
            return create_api_message(status_code=StatusCode.OK,
                                                   **data
                                                   )
    else:
        return create_api_message("Missing merchant account key", status_code=StatusCode.BAD_REQUEST)    
    
@merchant_api_bp.route('/<merchant_acct_code>/joined-brand-details/reference-code/<reference_code>', methods=['GET'])
@elapsed_time_trace(trace_key='read_joined_brand_details')
def read_joined_brand_details(merchant_acct_code, reference_code):
    
    merchant_acct           = None
    logger.info('merchant_acct_code=%s', merchant_acct_code)
    logger.info('reference_code=%s', reference_code)
    try:
        if is_not_empty(merchant_acct_code) and is_not_empty(reference_code):    
            db_client = create_db_client(caller_info="read_merchant_acct")
            with db_client.context():
                merchant_acct           = MerchantAcct.get_by_account_code(merchant_acct_code)
                
                logger.info('merchant_acct.brand_name=%s', merchant_acct.brand_name)
                
                customer                = Customer.get_by_reference_code(reference_code, merchant_acct)
                if customer:
                    user_acct               = customer.registered_user_acct
                    merchant_info           = merchant_helpers.construct_merchant_acct_info(merchant_acct, referrer_code=user_acct.referral_code) 
                    merchant_rating_result  = MerchantRatingResult.get_by_merchant_acct(merchant_acct)
                    '''
                    if merchant_info.get('referral_program_settings'):
                        
                        refer_a_friend_url      = '{base_url}/referral/program/merchant-acct-code/{merchant_acct_code}/referrer-code/{referrer_code}/join'
                        refer_a_friend_message  = 'Hi, \n\n{referee_promote_desc}. Please join {brand_name} via below link:\n\n{refer_a_friend_url}'
                        referee_promote_desc    = merchant_info.get('referral_program_settings').get('referee_promote_desc')
                            
                        refer_a_friend_url = refer_a_friend_url.format(
                                                    base_url            = conf.REFER_BASE_URL,
                                                    merchant_acct_code  = merchant_acct.account_code,
                                                    referrer_code       = user_acct.referral_code,
                                                    )
                        
                        referrer_data = {
                            'merchant_acct_code'    : merchant_acct.account_code,
                            'referrer_code'         : user_acct.referral_code,
                            }
                        
                        encrypted_referrer_data = aes_encrypt_json(referrer_data)
                        
                        refer_a_friend_deep_link = conf.REFER_A_FRIEND_DEEP_LINK.format(
                                                    referrer_data   = encrypted_referrer_data,
                                                    )
                        
                        
                        refer_a_friend_message = refer_a_friend_message.format(
                                                    referee_promote_desc    = referee_promote_desc,
                                                    brand_name              = merchant_acct.brand_name,
                                                    refer_a_friend_url      = refer_a_friend_url,
                                                    )
                        
                        merchant_info['referral_program_settings']['refer_a_friend_url']        = refer_a_friend_url
                        merchant_info['referral_program_settings']['refer_a_friend_message']    = refer_a_friend_message
                        merchant_info['referral_program_settings']['refer_a_friend_deep_link']  = refer_a_friend_deep_link
                    '''
                    
                    if merchant_rating_result:
                        logger.debug('rating_result=%s', merchant_rating_result.rating_result)
                        merchant_info['rating_reviews'] = merchant_rating_result.rating_result
                    
                    user_details                                        = customer.registered_user_acct
                    customer_details = customer.to_dict(date_format="%d-%m-%Y", datetime_format="%d-%m-%Y %H:%M:%S")
                    customer_details['customer_key']               = customer.key_in_str
                    customer_details['is_email_verified']          = user_details.is_email_verified
                    customer_details['is_mobile_phone_verified']   = user_details.is_mobile_phone_verified
                    
                    customer_basic_memberships_list = _list_customer_basic_memberships(customer)
                    if customer_basic_memberships_list:
                        customer_details['basic_memberships'] = customer_basic_memberships_list
                    
                    tier_membership_data = _get_tier_membership(customer)
                    if tier_membership_data:
                        customer_details['tier_membership'] = tier_membership_data
                        
                    
                    logger.debug('merchant_info=%s', merchant_info)
                    
                    return create_api_message(status_code=StatusCode.OK,
                                                       merchant_info    = merchant_info,
                                                       customer_details = customer_details,
                                                       )
                else:
                    logger.info('Failed to find customer account')    
            
                    return create_api_message(status_code=StatusCode.BAD_REQUEST)
                                                   
        else:
            return create_api_message("Missing merchant account code or customer reference code", status_code=StatusCode.BAD_REQUEST)    
    except:
        logger.error('Fail to read customer joined brand details due to %s', get_tracelog())
        
        return create_api_message(status_code=StatusCode.BAD_REQUEST)
    
@merchant_api_bp.route('/<merchant_acct_code>/customer-details/reference-code/<reference_code>', methods=['GET'])
@user_auth_token_required
@elapsed_time_trace(trace_key='read_customer_details')
def read_customer_details(merchant_acct_code, reference_code):
    
    merchant_acct           = None
    logger.info('merchant_acct_code=%s', merchant_acct_code)
    logger.info('reference_code=%s', reference_code)
    try:
        if is_not_empty(merchant_acct_code) and is_not_empty(reference_code):    
            db_client = create_db_client(caller_info="read_customer_details")
            with db_client.context():
                merchant_acct           = MerchantAcct.get_by_account_code(merchant_acct_code)
                
                logger.info('merchant_acct.brand_name=%s', merchant_acct.brand_name)
                
                customer                = Customer.get_by_reference_code(reference_code, merchant_acct)
                if customer:
                    user_details                                   = customer.registered_user_acct
                    customer_details = customer.to_dict(
                                                    date_format="%d-%m-%Y", 
                                                    datetime_format="%d-%m-%Y %H:%M:%S",
                                                    excluded_dict_properties=[
                                                        'reward_summary', 'entitled_voucher_summary', 'prepaid_summary', 
                                                        'entitled_lucky_draw_ticket_summary', 'kpi_summary',
                                                        'entitled_birthday_reward_summary', 'registered_merchant_acct',
                                                        'registered_user_acct','device_details',
                                                        ],
                                                    
                                                    )
                    customer_details['customer_key']               = customer.key_in_str
                    customer_details['is_email_verified']          = user_details.is_email_verified
                    customer_details['is_mobile_phone_verified']   = user_details.is_mobile_phone_verified
                    
                    logger.debug('is_referred_by_friend=%s', customer_details['is_referred_by_friend'])
                    
                    customer_basic_memberships_list = _list_customer_basic_memberships(customer)
                    if customer_basic_memberships_list:
                        customer_details['basic_memberships'] = customer_basic_memberships_list
                    
                    tier_membership_data = _get_tier_membership(customer)
                    if tier_membership_data:
                        customer_details['tier_membership'] = tier_membership_data
                        
                    return create_api_message(status_code=StatusCode.OK,
                                                       customer_details = customer_details,
                                                       )
                else:
                    logger.info('Failed to find customer account')    
            
                    return create_api_message(status_code=StatusCode.BAD_REQUEST)
                                                   
        else:
            return create_api_message("Missing merchant account code or customer reference code", status_code=StatusCode.BAD_REQUEST)    
    except:
        logger.error('Fail to read customer joined brand details due to %s', get_tracelog())
        
        return create_api_message(status_code=StatusCode.BAD_REQUEST)   

 
        

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
                                                        'entitled_date'         : cm.entitled_date.strftime('%d-%m-%Y'),
                                                        'expiry_date'           : cm.expiry_date.strftime('%d-%m-%Y'),
                                                        'card_image'            : mm.membership_card_image,
                                                        'desc'                  : mm.desc if is_not_empty(mm.desc) else '',
                                                        'terms_and_conditions'  : mm.terms_and_conditions if is_not_empty(mm.terms_and_conditions) else '',
                                                        'is_tier'               : False,
                                                        }
                        
                        if cm.renewed_date is not None:
                            membership_data['renewed_date'] = cm.renewed_date.strftime('%d-%m-%Y'),
                        
                        customer_membership_final_list.append(membership_data)
                        break
    return customer_membership_final_list

def _get_tier_membership(customer):
            
    if is_not_empty(customer.tier_membership):
        merchant_tier_membership = customer.tier_membership_entity
        if merchant_tier_membership:
            customer_tier_membership = CustomerTierMembership.get_by_customer_and_merchant_tier_membership(customer, merchant_tier_membership)
            if customer_tier_membership:
                membership_data = {
                                'key'                   : customer_tier_membership.merchant_tier_membership_key,
                                'label'                 : merchant_tier_membership.label,
                                'entitled_date'         : customer_tier_membership.entitled_date.strftime('%d-%m-%Y'),
                                'expiry_date'           : customer_tier_membership.expiry_date.strftime('%d-%m-%Y'),
                                'card_image'            : merchant_tier_membership.membership_card_image,
                                'desc'                  : merchant_tier_membership.desc if is_not_empty(merchant_tier_membership.desc) else '',
                                'terms_and_conditions'  : merchant_tier_membership.terms_and_conditions if is_not_empty(merchant_tier_membership.terms_and_conditions) else '',
                                'is_tier'               : True,
                                }
                
                return membership_data

@merchant_api_bp.route('/<merchant_key>/customer-details/reference-code/<reference_code>', methods=['GET'])
@elapsed_time_trace(trace_key='read_merchant_customer_details')
def read_merchant_customer_details(merchant_key, reference_code):
    
    merchant_acct           = None
    customer_details_dict   = {} 
    
    if is_not_empty(merchant_key) and is_not_empty(reference_code):
        db_client = create_db_client(caller_info="read_merchant_customer_details")
        with db_client.context():
            merchant_acct = MerchantAcct.fetch(merchant_key)
            customer = Customer.get_by_reference_code(reference_code, merchant_acct) 
        
            if customer:
            
                user_details = customer.registered_user_acct
                customer_details_dict = customer.to_dict(date_format="%d-%m-%Y", datetime_format="%d-%m-%Y %H:%M:%S",
                                                         excluded_dict_properties=[
                                                            'reward_summary', 'entitled_voucher_summary', 'prepaid_summary', 
                                                            'entitled_lucky_draw_ticket_summary', 'kpi_summary',
                                                            'entitled_birthday_reward_summary', 'registered_merchant_acct',
                                                            'registered_user_acct','device_details',
                                                            ],
                                                         )
                customer_details_dict['customer_key']               = customer.key_in_str
                customer_details_dict['is_email_verified']          = user_details.is_email_verified
                customer_details_dict['is_mobile_phone_verified']   = user_details.is_mobile_phone_verified
                
                customer_basic_memberships_list = _list_customer_basic_memberships(customer)
                if customer_basic_memberships_list:
                    customer_details_dict['basic_memberships'] = customer_basic_memberships_list
                
                tier_membership_data = _get_tier_membership(customer)
                if tier_membership_data:
                    customer_details_dict['tier_membership'] = tier_membership_data
                
                '''
                if 'entitled_voucher_summary' in customer_details_dict:
                    customer_details_dict['voucher_summary']            = customer.entitled_voucher_summary
                    del customer_details_dict['entitled_voucher_summary']
                '''
        return jsonify(customer_details_dict)
            
    
    else:
        return create_api_message("Missing merchant account key or user reference code", status_code=StatusCode.BAD_REQUEST)


class AccountActivatedAPIResource(APIBaseResource):  
    
    @auth.login_required
    @request_headers
    def post(self, request_headers):
        username    = auth.current_user()
        
        acct_id     = request_headers.get('x-acct-id')
        api_key     = request_headers.get('x-api-key')
        outlet_key  = request_headers.get('x-outlet-key')
        
        logger.debug('username=%s', username)
        logger.debug('acct_id=%s', acct_id)    
        logger.debug('api_key=%s', api_key)
        logger.debug('outlet_key=%s', outlet_key)
        
        is_valid            = False
        is_authorized       = False
        output_json = {}
        
        if is_not_empty(acct_id) and is_not_empty(api_key):
            db_client = create_db_client(caller_info="AccountActivatedAPIResource.post")
            with db_client.context():
                merchant_acct = MerchantAcct.fetch(acct_id)
                
                #logger.debug('merchant_acct=%s', merchant_acct)
                
                if merchant_acct:
                    logger.debug('merchant_acct api key=%s', merchant_acct.api_key)
                    
                    if api_key == merchant_acct.api_key:
                        merchant_user               = MerchantUser.get_by_username(username)
                        
                        is_authorized = self.is_outlet_authorized(merchant_user, outlet_key)
                        if is_authorized:
                            (expiry_datetime, token)    = self.generate_token(acct_id, username)
                            logger.debug('outlet is_authorized=%s', is_authorized)
                            logger.debug('expiry_datetime=%s', expiry_datetime)
                            
                            output_json =  {
                                            'auth_token'        : token,
                                            'expires_in'        : int(api_conf.API_TOKEN_EXPIRY_LENGTH_IN_MINUTE) * 60,
                                            #'expiry_datetime'   : expiry_datetime.strftime('%d-%m-%Y %h:%M:$S'),
                                            'granted_outlet'    : merchant_user.granted_outlet_details_list,
                                            'username'          : merchant_user.username,
                                            'name'              : merchant_user.name,
                                            'is_admin'          : merchant_user.is_admin,
                                            'granted_access'    : merchant_user.permission.get('granted_access'),
                                            'gravatar_url'      : merchant_user.gravatar_url,
                                            }
                
                            logger.debug('output_json=%s', output_json)
                            
                            is_valid = True
                    
            if is_valid:
                return output_json
            
            elif is_authorized==False:
                abort(400, msg=["User is not authorized due to outlet is not granted"])
                    
        abort(400, msg=["Failed to authenticate"])
        
    
    def is_outlet_authorized(self, merchant_user, outlet_key):
        return True 
    
class AuthenticateAPIResource(APIBaseResource):  
    
    @auth.login_required
    @request_headers
    def post(self, request_headers):
        username    = auth.current_user()
        
        #acct_id     = request.headers.get('x-acct-id')
        #api_key     = request.headers.get('x-api-key')
        #outlet_key  = request.headers.get('x-outlet-key')
        
        acct_id     = request_headers.get('x-acct-id')
        api_key     = request_headers.get('x-api-key')
        outlet_key  = request_headers.get('x-outlet-key')
        
        logger.debug('username=%s', username)  
        logger.debug('acct_id=%s', acct_id)    
        logger.debug('api_key=%s', api_key)
        logger.debug('outlet_key=%s', outlet_key)
        
        is_authenticated    = False
        is_authorized       = False
        output_json = {}
        
        if is_not_empty(acct_id) and is_not_empty(api_key):
            if is_not_empty(outlet_key):
                db_client = create_db_client(caller_info="AuthenticateAPIResource.post")
                with db_client.context():
                    merchant_acct = MerchantAcct.fetch(acct_id)
                
                    if merchant_acct:
                        if api_key == merchant_acct.api_key:
                            merchant_user               = MerchantUser.get_by_username(username)
                            
                            is_authorized = self.is_outlet_authorized(merchant_user, outlet_key)
                            logger.debug('outlet is_authorized=%s', is_authorized)
                            
                            if is_authorized:
                                outlet = Outlet.fetch(outlet_key)
                                (expiry_datetime, token)    = self.generate_token(acct_id, username, api_access=True)
                                #session['auth_username']    = username
                                #session['acct_id']          = acct_id
                                
                                logger.debug('token=%s', token)
                                logger.debug('expiry_datetime=%s', expiry_datetime)
                                logger.debug('auth_username=%s', username)
                    
                                output_json =  {
                                                'auth_token'        : token,
                                                'expires_in_seconds': int(api_conf.API_TOKEN_EXPIRY_LENGTH_IN_MINUTE) * 60,
                                                #'granted_outlet'    : merchant_user.granted_outlet_details_list,
                                                'username'          : merchant_user.username,
                                                'name'              : merchant_user.name,
                                                'is_admin'          : merchant_user.is_admin,
                                                'outlet_name'       : outlet.name,
                                                'granted_access'    : merchant_user.permission.get('granted_access'),
                                                #'gravatar_url'      : merchant_user.gravatar_url,
                                                }
                    
                                logger.debug('output_json=%s', output_json)
                                
                                is_authenticated = True
                    
                if is_authenticated:
                    return output_json
                elif is_authorized==False:
                    abort(400, msg=["User is not authorized due to outlet is not granted"])
            else:
                abort(400, msg=["Missing outlet key"])
        else:
            abort(400, msg=["Missing account id or api key"])
                    
        abort(400, msg=["Failed to authenticate"])
        
    
    def is_outlet_authorized(self, merchant_user, outlet_key):
        
        outlet_keys_list = merchant_user.granted_outlets_search_list
        if outlet_key in outlet_keys_list:
            return True
        return False    

class ProgramDeviceAuthenticate(AccountActivatedAPIResource):
    
    @request_json
    def is_outlet_authorized(self, merchant_user, outlet_key, data_in_json):
        logger.debug('data_in_json=%s', data_in_json)
        if merchant_user.is_admin:
            logger.debug('it is merchant admin user, thus it is authorized for all outlet')
            return True
        else:
            #data_in_json        = request.get_json()
            activation_code     = data_in_json.get('activation_code')
            device_setting      = LoyaltyDeviceSetting.get_by_activation_code(activation_code)
            access_outlet       = Outlet.fetch(outlet_key)
            assigned_outlet_key = device_setting.assigned_outlet_key
            
            logger.debug('device assigned outlet name=%s', device_setting.assigned_outlet_entity.name)
            logger.debug('access outlet name=%s', access_outlet.name)
            
            if outlet_key == device_setting.assigned_outlet_key:
                logger.debug('login outlet is same as device setting assigned outlet')
                if outlet_key in merchant_user.granted_outlet:
                    logger.debug('login outlet is authorized by login merchant user granted outlet')
                    if assigned_outlet_key in merchant_user.granted_outlet:
                        logger.debug('device assigned outlet is authorized by login merchant user granted outlet')
                        return True
                    else:
                        logger.debug('device setting assigned outlet is not granted outlet')
                else:
                    logger.debug('login outlet is not granted outlet')    
            else:
                logger.debug('login outlet is not same as device setting assigned outlet')
                        
        return False
            
class POSDeviceAuthenticate(AccountActivatedAPIResource):
    @request_json
    def is_outlet_authorized(self, merchant_user, outlet_key, data_in_json):
        if merchant_user.is_admin:
            return True
        else:
            #data_in_json        = request.get_json()
            activation_code     = data_in_json.get('activation_code')
            device_setting      = POSSetting.get_by_activation_code(activation_code)
            access_outlet       = Outlet.fetch(outlet_key)
            assigned_outlet_key = device_setting.assigned_outlet_key
            
            logger.debug('device assigned outlet name=%s', device_setting.assigned_outlet_entity.name)
            logger.debug('access outlet name=%s', access_outlet.name)
            
            if outlet_key == device_setting.assigned_outlet_key:
                logger.debug('login outlet is same as device setting assigned outlet')
                if outlet_key in merchant_user.granted_outlet:
                    logger.debug('login outlet is authorized by login merchant user granted outlet')
                    if assigned_outlet_key in merchant_user.granted_outlet:
                        logger.debug('device assigned outlet is authorized by login merchant user granted outlet')
                        return True
                    else:
                        logger.debug('device setting assigned outlet is not granted outlet')
                else:
                    logger.debug('login outlet is not granted outlet')    
            else:
                logger.debug('login outlet is not same as device setting assigned outlet')
        
        return False            

class SecureAPIResource(AuthenticateAPIResource):  
    
    def __init__(self):
        super(SecureAPIResource, self).__init__()  
    
    
class CheckAuthTokenResource(SecureAPIResource):
    
    @auth_token_required
    def get(self):
        return 'Ping'             
    
     
merchant_api.add_resource(AuthenticateAPIResource,       '/auth')
merchant_api.add_resource(ProgramDeviceAuthenticate,     '/program-auth')
merchant_api.add_resource(POSDeviceAuthenticate,         '/pos-auth')      
    
        
        
        
        