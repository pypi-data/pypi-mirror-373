'''
Created on 7 Jul 2021

@author: jacklok
'''

from flask import Blueprint, request 
import logging
from trexlib.utils.log_util import get_tracelog
from flask_restful import Api
from trexmodel.utils.model.model_util import create_db_client
from flask.json import jsonify
from datetime import datetime
from trexapi.decorators.api_decorators import auth_token_required,\
    outlet_key_required, device_is_activated, show_request_info,\
    user_auth_token_required
from trexlib.utils.string_util import is_not_empty
from trexmodel.models.datastore.customer_models import Customer,\
    CustomerMembership, CustomerTierMembership
from trexmodel.models.datastore.user_models import User
from trexapi.utils.api_helpers import StatusCode, create_api_message
from trexmodel.models.datastore.merchant_models import Outlet,\
    MerchantAcct, MerchantUser
from trexapi.forms.customer_api_forms import CustomerDetailsNewForm, CustomerDetailsUpdateForm,\
    CustomerSearchForm
from werkzeug.datastructures import ImmutableMultiDict
from trexapi.controllers.user_api_routes import user_details_dict
from trexmodel.models.datastore.transaction_models import CustomerTransaction
from trexapi.utils.api_helpers import get_logged_in_api_username
from trexmodel.models.datastore.redeem_models import CustomerRedemption
from trexmodel.models.datastore.model_decorators import model_transactional
from trexmodel.models.datastore.helper.reward_transaction_helper import revert_redemption,\
    revert_transaction
from trexanalytics.bigquery_upstream_data_config import create_merchant_registered_customer_upstream_for_merchant,\
    create_registered_customer_upstream_for_system
from trexmodel.models.datastore.membership_models import MerchantMembership
from flask_babel import gettext
from trexlib.libs.flask_wtf.request_wrapper import request_json, request_headers,\
    request_values
from trexlib.utils.common.date_util import parse_generic_date
from trexmodel.models.datastore.reward_models import CustomerPointReward,\
    CustomerStampReward, CustomerEntitledVoucher, RevertedCustomerPointReward,\
    RevertedCustomerStampReward, CustomerEntitledTierRewardSummary
from trexmodel.models.datastore.prepaid_models import CustomerPrepaidReward
from trexapi.libs.api_decorator import elapsed_time_trace
from trexmodel.models.merchant_helpers import return_customer_details

logger = logging.getLogger('api')


customer_api_bp = Blueprint('customer_api_base_bp', __name__,
                                 template_folder='templates',
                                 static_folder='static',
                                 url_prefix='/api/v1/customers')

logger = logging.getLogger('target_debug')

customer_api = Api(customer_api_bp)



@customer_api_bp.route('/register', methods=['POST'])
@auth_token_required
@outlet_key_required
@device_is_activated
@request_values
@request_headers
def create_customer(customer_data_in_json, request_headers):
    register_customer_form  = CustomerDetailsNewForm(ImmutableMultiDict(customer_data_in_json))
    
    logger.debug('create_customer: customer_data_in_json=%s', customer_data_in_json)
    
    try:
        if register_customer_form.validate():
            logger.debug('customer registration input is valid')
            db_client = create_db_client(caller_info="create_customer")
            
            is_email_used           = False
            is_mobile_phone_used    = False
            customer_is_exist       = False
            created_customer        = None
            created_user_acct       = None
            
            outlet_key  = request_headers.get('x-outlet-key')
            acct_id     = request_headers.get('x-acct-id')
            
            logger.debug('outlet_key=%s', outlet_key)
            logger.debug('acct_id=%s', acct_id)
            
            with db_client.context():
                merchant_acct           = MerchantAcct.fetch(acct_id)
                outlet                  = Outlet.fetch(outlet_key)
                
                email                   = customer_data_in_json.get('email')
                mobile_phone            = customer_data_in_json.get('mobile_phone')
                merchant_reference_code = customer_data_in_json.get('merchant_reference_code')
                
                birth_date              = customer_data_in_json.get('birth_date')
                            
                if is_not_empty(birth_date):
                    birth_date = parse_generic_date(birth_date)
                
                logger.debug('birth_date=%s', birth_date)

                
                logger.debug('email=%s', email)
                logger.debug('mobile_phone=%s', mobile_phone)
                logger.debug('merchant_reference_code=%s', merchant_reference_code)
                
                if is_not_empty(email):
                    created_user_acct = User.get_by_email(email)
                    
                    #if created_user_acct and created_user_acct.is_email_verified:
                    if created_user_acct:    
                        is_email_used = True
                
                if is_not_empty(mobile_phone):
                    mobile_phone = mobile_phone.replace(" ", "")
                    created_user_acct = User.get_by_mobile_phone(mobile_phone)
                    
                    #if created_user_acct and created_user_acct.is_mobile_phone_verified:
                    if created_user_acct:
                        is_mobile_phone_used = True
                
                
                logger.debug('is_email_used=%s', is_email_used)
                logger.debug('is_mobile_phone_used=%s', is_mobile_phone_used)
                
                if merchant_acct and outlet:
                        
                    logger.debug('merchant_acct.key_in_str=%s', merchant_acct.key_in_str)
                    logger.debug('outlet.merchant_acct_key=%s', outlet.merchant_acct_key)
                    
                    if merchant_acct.key_in_str == outlet.merchant_acct_key: 
                        logger.debug('Valid granted outlet key for merchant acct')
                                                    
                        if is_email_used:
                            created_customer = Customer.get_by_email(email, merchant_acct=merchant_acct)
                        
                        if created_customer is None:    
                            if is_mobile_phone_used:
                                created_customer = Customer.get_by_mobile_phone(mobile_phone, merchant_acct=merchant_acct)
                        
                        if is_email_used or is_mobile_phone_used:
                            if created_customer is None:
                                logger.debug('User account have been created, but customer account is not yet created')
                                
                                created_user_acct = User.update(created_user_acct,
                                                                name                    = customer_data_in_json.get('name'), 
                                                                email                   = customer_data_in_json.get('email'), 
                                                                gender                  = customer_data_in_json.get('gender'),
                                                                birth_date              = birth_date,
                                                                mobile_phone            = mobile_phone, 
                                                                password                = customer_data_in_json.get('password'),
                                                                )
                                
                                created_customer        = Customer.create_from_user(outlet, created_user_acct, customer_data_in_json.get('merchant_reference_code'))
                            
                            else:
                                customer_is_exist = True
                                logger.warn('Customer account using same email or mobile phone have been created')
                        else:
                            if is_not_empty(merchant_reference_code):
                                checking_customer = Customer.get_by_merchant_reference_code(merchant_reference_code, merchant_acct)
                                if checking_customer is not None:
                                    return create_api_message('Merchant reference code (%s) have been taken' % (merchant_reference_code), status_code=StatusCode.BAD_REQUEST)
                                
                                
                            created_customer        = Customer.create( 
                                                            outlet                  = outlet, 
                                                            name                    = customer_data_in_json.get('name'), 
                                                            email                   = customer_data_in_json.get('email'), 
                                                            gender                  = customer_data_in_json.get('gender'),
                                                            birth_date              = birth_date,
                                                            mobile_phone            = mobile_phone, 
                                                            merchant_reference_code = merchant_reference_code, 
                                                            password                = customer_data_in_json.get('password'),
                                                            )
                            
                            create_merchant_registered_customer_upstream_for_merchant(created_customer)
                            create_registered_customer_upstream_for_system(created_customer)
                            
                        logger.debug('created_customer=%s', created_customer)
                    else:
                        logger.warn('Invalid granted outlet key')
                else:
                    logger.warn('Invalid granted outlet key')
            
                if customer_is_exist:
                    if is_email_used==True:
                        return create_api_message('Email have been taken', status_code=StatusCode.BAD_REQUEST)
                    
                    elif is_mobile_phone_used==True:
                        return create_api_message('Mobile phone have been taken', status_code=StatusCode.BAD_REQUEST)
                    
                
                if created_customer:
                    created_user_acct = created_customer.registered_user_acct
                    response_data = {
                                'customer_key'              : created_customer.key_in_str,
                                'registered_datetime'       : created_customer.registered_datetime.strftime("%d-%m-%Y %H:%M:%S"),
                                'modified_datetime'         : created_customer.modified_datetime.strftime("%d-%m-%Y %H:%M:%S"),
                                'merchant_reference_code'   : created_customer.merchant_reference_code,
                                'reference_code'            : created_customer.reference_code,
                                'referral_code'             : created_customer.referral_code,
                                'registered_outlet_key'     : created_customer.registered_outlet_key,
                                #'merchant_account_key'      : acct_id,
                                #'company_name'              : merchant_acct.company_name,
                                #'outlet_key'                : outlet_key,  
                                
                                }
                
                    logger.debug('response_data=%s', response_data)
                    
                    response_data.update(user_details_dict(created_user_acct))
                    
                    return create_api_message(status_code=StatusCode.OK, **response_data)
                    
                else:
                    return create_api_message(status_code=StatusCode.BAD_REQUEST)
            
        else:
            logger.warn('customer registration input is invalid')
            error_message = register_customer_form.create_rest_return_error_message()
            
            return create_api_message(error_message, status_code=StatusCode.BAD_REQUEST)
    except:
        logger.error('Fail to register customer due to %s', get_tracelog())
        
        return create_api_message(status_code=StatusCode.BAD_REQUEST)

'''
def _return_customer_details(customer):
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

def _return_customer_reward(customer):
    customer_reward_dict = customer.to_dict(
                                        date_format="%d-%m-%Y", 
                                        datetime_format="%d-%m-%Y %H:%M:%S",
                                        dict_properties = [
                                                'reward_summary', 'entitled_voucher_summary', 'prepaid_summary', 
                                                'entitled_lucky_draw_ticket_summary', 
                                                
                                                
                                                ],
                                        )
    customer_reward_dict['customer_key']               = customer.key_in_str
    
    
    customer_basic_memberships_list = _list_customer_basic_memberships(customer)
    if customer_basic_memberships_list:
        customer_reward_dict['basic_memberships'] = customer_basic_memberships_list
    
    customer_tier_membership = _get_tier_membership(customer)
    if customer_tier_membership:
        customer_reward_dict['tier_membership']  = customer_tier_membership
    
    return customer_reward_dict

def _return_customer_minimum_details(customer):
    customer_details_dict = customer.to_dict(
                                        date_format="%d-%m-%Y", 
                                        datetime_format="%d-%m-%Y %H:%M:%S",
                                        excluded_dict_properties = [
                                                'registered_merchant_acct', 
                                                'memberships_list', 
                                                'tier_membership_key',
                                                'registered_user_acct',
                                                'kpi_summary',
                                                'entitled_lucky_draw_ticket_summary',
                                                'reward_summary',
                                                'tags_list',
                                                'entitled_membership_reward_summary',
                                                'entitled_birthday_reward_summary',
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
'''
    
@customer_api_bp.route('/reference-code/<ref_code>', methods=['GET'])
@auth_token_required
@device_is_activated
@request_headers
def read_customer(request_headers, ref_code):
    
    logger.debug('ref_code=%s', ref_code)
    
    if is_not_empty(ref_code):
        db_client = create_db_client(caller_info="read_customer")
        
        acct_id     = request_headers.get('x-acct-id')
        
        with db_client.context():
            merchant_acct = MerchantAcct.fetch(acct_id)
            customer = Customer.get_by_reference_code(ref_code, merchant_acct)
            
        
        if customer:
            with db_client.context():
                customer_details_dict = return_customer_details(customer)
            
            customer_details_json =  jsonify(customer_details_dict)
            
            
            logger.debug('customer_details_json=%s', customer_details_json)
            
            return customer_details_json
            
        else:
            logger.warn('Customer with reference code (%s) is not found', ref_code)
            return create_api_message('Customer with reference code (%s) is not found' % ref_code, 
                                      status_code=StatusCode.BAD_REQUEST)
            
    else:
        return create_api_message(status_code=StatusCode.BAD_REQUEST)

@customer_api_bp.route('/customer-key/<customer_key>/customer-reward', methods=['GET'])
@auth_token_required
@device_is_activated
@elapsed_time_trace(trace_key='read_customer_reward')
def read_customer_reward(customer_key):
    
    logger.debug('customer_key=%s', customer_key)
    
    if is_not_empty(customer_key):
        db_client = create_db_client(caller_info="read_customer_reward")
        
        with db_client.context():
            customer = Customer.fetch(customer_key)
            
        
        if customer:
            with db_client.context():
                customer_details_dict = _return_customer_reward(customer)
            
            customer_details_json =  jsonify(customer_details_dict)
            
            
            logger.debug('customer_details_json=%s', customer_details_json)
            
            return customer_details_json
            
        else:
            logger.warn('Customer with customer key (%s) is not found', customer_key)
            return create_api_message('Customer with customer key (%s) is not found' % customer_key, 
                                      status_code=StatusCode.BAD_REQUEST)
            
    else:
        return create_api_message(status_code=StatusCode.BAD_REQUEST)

@customer_api_bp.route('/reference-code/<reference_code>/read-or-register', methods=['GET'])
@auth_token_required
@device_is_activated
@request_headers
def read_and_register_customer(request_headers, reference_code):
    
    logger.debug('reference_code=%s', reference_code)
    
    if is_not_empty(reference_code):
        db_client = create_db_client(caller_info="read_and_register_customer")
        
        acct_id     = request_headers.get('x-acct-id')
        
        with db_client.context():
            merchant_acct = MerchantAcct.fetch(acct_id)
            customer = Customer.get_by_reference_code(reference_code, merchant_acct)
            
        
        if customer:
            with db_client.context():
                #customer_details_dict = _return_customer_minimum_details(customer)
                customer_details_dict = {
                                        'name': customer.name,
                                        'reference_code': customer.reference_code,
                                        'customer_key'  : customer.key_in_str,
                                        }
            
            customer_details_json =  jsonify(customer_details_dict)
            
            
            logger.debug('customer_details_json=%s', customer_details_json)
            
            return customer_details_json
            
        else:
            logger.warn('Customer with reference code (%s) is not found', reference_code)
            with db_client.context():
                existing_user_acct  = User.get_by_reference_code(reference_code)
                outlet_key  = request_headers.get('x-outlet-key')
                outlet      = Outlet.fetch(outlet_key)
                
                created_customer = __register_user_as_customer(existing_user_acct, outlet)
                
            if created_customer:
                with db_client.context():
                    #customer_details_dict = _return_customer_minimum_details(customer)
                    customer_details_dict = {
                                        'name': customer.name,
                                        'reference_code': customer.reference_code,
                                        'customer_key'  : customer.key_in_str,
                                        }
                
                return jsonify(customer_details_dict)
                    
            
            return create_api_message(status_code=StatusCode.BAD_REQUEST)
            
    else:
        return create_api_message(status_code=StatusCode.BAD_REQUEST)    
    
@customer_api_bp.route('/customer-key/<customer_key>', methods=['GET'])
@show_request_info
@auth_token_required
@device_is_activated
def read_customer_by_customer_key(customer_key):
    
    logger.debug('customer_key=%s', customer_key)
    
    if is_not_empty(customer_key):
        customer_details_dict = None
        db_client = create_db_client(caller_info="read_customer_by_customer_key")
        
        with db_client.context():
            customer = Customer.fetch(customer_key)
            
            if customer:
                customer_details_dict = return_customer_details(customer)
            
        if customer_details_dict:
            return jsonify(customer_details_dict)
            
            
        else:
            logger.warn('Customer with customer_key (%s) is not found', customer_key)
            return create_api_message(status_code=StatusCode.BAD_REQUEST)
            
    else:
        return create_api_message(status_code=StatusCode.BAD_REQUEST)    


def _update_customer(updating_customer, customer_data_in_json):
    
    is_email_used                           = False
    is_mobile_phone_used                    = False
    customer_is_exist                       = False
    checking_user_acct                      = None
    is_customer_email_changed               = False
    is_customer_mobile_phone_changed        = False
    is_used_email_same_user_acct            = False
    is_used_mobile_phone_same_user_acct     = False
    
    email               = customer_data_in_json.get('email')
    mobile_phone        = customer_data_in_json.get('mobile_phone')
    
    if mobile_phone:
        mobile_phone = mobile_phone.replace(" ", "")
    
    if updating_customer:
        customer_is_exist = True
        is_customer_email_changed           = updating_customer.email!=email
        is_customer_mobile_phone_changed    = updating_customer.mobile_phone!=mobile_phone
    
    if is_customer_email_changed:
        if is_not_empty(email):
            checking_user_acct = User.get_by_email(email)
            
            if checking_user_acct:
                is_email_used = True
                is_used_email_same_user_acct = checking_user_acct.reference_code == updating_customer.reference_code
            
    if is_customer_mobile_phone_changed:
        if is_not_empty(mobile_phone):
            checking_user_acct = User.get_by_mobile_phone(mobile_phone)
        
            if checking_user_acct:
                is_mobile_phone_used = True
                is_used_mobile_phone_same_user_acct = checking_user_acct.reference_code == updating_customer.reference_code
                    
    logger.debug('is_customer_email_changed=%s', is_customer_email_changed)
    logger.debug('is_customer_mobile_phone_changed=%s', is_customer_mobile_phone_changed)
    logger.debug('is_email_used=%s', is_email_used)
    logger.debug('is_mobile_phone_used=%s', is_mobile_phone_used)
    logger.debug('is_used_email_same_user_acct=%s', is_used_email_same_user_acct)
    logger.debug('is_used_mobile_phone_same_user_acct=%s', is_used_mobile_phone_same_user_acct)
    
    if is_email_used==False and is_mobile_phone_used==False:
        logger.debug('Going to update customer details') 
        
        birth_date              = customer_data_in_json.get('birth_date')
            
        if is_not_empty(birth_date):
            birth_date = parse_generic_date(birth_date)
        
        logger.debug('birth_date=%s', birth_date)
        
        Customer.update(customer                = updating_customer, 
                        name                    = customer_data_in_json.get('name'), 
                        email                   = customer_data_in_json.get('email'), 
                        gender                  = customer_data_in_json.get('gender'),
                        birth_date              = birth_date,
                        mobile_phone            = mobile_phone, 
                        password                = customer_data_in_json.get('password'),
                        merchant_reference_code = customer_data_in_json.get('merchant_reference_code')
                        )
    
    
    if customer_is_exist:
        if is_email_used==True:
            return create_api_message('Email have been taken', status_code=StatusCode.BAD_REQUEST)
        
        elif is_mobile_phone_used==True:
            return create_api_message('Mobile phone have been taken', status_code=StatusCode.BAD_REQUEST)
        else:
            return create_api_message(status_code=StatusCode.OK)
    else:
        return create_api_message(gettext('Customer is not exist'), status_code=StatusCode.BAD_REQUEST)
    

#@customer_api_bp.route('/customer-key/<customer_key>', methods=['PUT'])
@customer_api_bp.route('/reference-code/<reference_code>', methods=['PUT'])
@show_request_info
@auth_token_required
@device_is_activated
@request_values
@request_headers
def update_customer_by_reference_code(request_values, request_headers, reference_code):
    customer_data_in_json   = request_values
    updating_customer_form  = CustomerDetailsUpdateForm(ImmutableMultiDict(customer_data_in_json))
    
    logger.debug('update_customer: customer_data_in_json=%s', customer_data_in_json)
    
    try:
        if updating_customer_form.validate():
            
                
            logger.debug('customer update input is valid')
            customer_data_in_json = request_values
            db_client = create_db_client(caller_info="update_customer")
            
            with db_client.context():
                account_id        = request_headers.get('x-acct-id')
                logger.debug('update_customer: account_id=%s', account_id)
                logger.debug('update_customer: reference_code=%s', reference_code)
                
                merchant_acct       = MerchantAcct.fetch(account_id)
                if merchant_acct:
                    updating_customer = Customer.get_by_reference_code(reference_code, merchant_acct)
                else:
                    updating_customer = None
            
            if updating_customer:
                logger.debug('update_customer: updating_customer is not none')
                with db_client.context():
                    return _update_customer(updating_customer, customer_data_in_json)
            else:
                return create_api_message(gettext('Customer is not exist'), status_code=StatusCode.BAD_REQUEST)
                
                
            
        else:
            logger.warn('customer registration input is invalid')
            error_message = updating_customer_form.create_rest_return_error_message()
            
            return create_api_message(error_message, status_code=StatusCode.BAD_REQUEST)
    except:
        logger.error('Fail to update customer due to %s', get_tracelog())
        
        return create_api_message(status_code=StatusCode.BAD_REQUEST)
    
@customer_api_bp.route('/customer-key/<customer_key>', methods=['PUT'])
@show_request_info
@auth_token_required
@device_is_activated
@request_values
def update_customer_by_customer_key(request_values, customer_key):
    customer_data_in_json   = request_values
    updating_customer_form  = CustomerDetailsUpdateForm(ImmutableMultiDict(customer_data_in_json))
    
    logger.debug('update_customer: customer_data_in_json=%s', customer_data_in_json)
    
    try:
        if updating_customer_form.validate():
            
                
            logger.debug('customer update input is valid')
            customer_data_in_json = request_values
            db_client = create_db_client(caller_info="update_customer")
            
            with db_client.context():
                updating_customer   = Customer.fetch(customer_key)
                
                return _update_customer(updating_customer, customer_data_in_json)
            
        else:
            logger.warn('customer registration input is invalid')
            error_message = updating_customer_form.create_rest_return_error_message()
            
            return create_api_message(error_message, status_code=StatusCode.BAD_REQUEST)
    except:
        logger.error('Fail to register customer due to %s', get_tracelog())
        
        return create_api_message(status_code=StatusCode.BAD_REQUEST)    
        
@customer_api_bp.route('/customer-key/<customer_key>', methods=['DELETE'])
@auth_token_required 
@device_is_activated
def delete_customer(customer_key):
    if is_not_empty(customer_key):
        is_found = False
        db_client = create_db_client(caller_info="delete_customer")
        with db_client.context():
            customer = Customer.fetch(customer_key) 
            if customer:
                _delete_customer(customer)
                is_found = True
        
        if is_found:
            return create_api_message(status_code=StatusCode.NO_CONTENT)
        else:
            return create_api_message(gettext('Customer is not exist'), status_code=StatusCode.BAD_REQUEST)
    else:
        return create_api_message(status_code=StatusCode.BAD_REQUEST) 
    
@customer_api_bp.route('/reference-code/<reference_code>', methods=['DELETE'])
@auth_token_required 
@device_is_activated
@request_headers
def delete_customer_by_reference_code(request_headers, reference_code):
    if is_not_empty(reference_code):
        is_found = False
        db_client = create_db_client(caller_info="delete_customer")
        with db_client.context():
            account_id        = request_headers.get('x-acct-id')
            logger.debug('update_customer: account_id=%s', account_id)
            logger.debug('update_customer: reference_code=%s', reference_code)
            
            merchant_acct       = MerchantAcct.fetch(account_id)
            if merchant_acct:
                customer = Customer.get_by_reference_code(reference_code, merchant_acct) 
            
            if customer:
                _delete_customer(customer)
                is_found = True
        
        if is_found:
            return create_api_message(status_code=StatusCode.NO_CONTENT)
        else:
            return create_api_message(gettext('Customer is not exist'), status_code=StatusCode.BAD_REQUEST)
    else:
        return create_api_message(status_code=StatusCode.BAD_REQUEST)            


@model_transactional(desc='Delete customer transaction')
def _delete_customer(customer):
    CustomerMembership.delete_all_by_customer(customer)
    CustomerTierMembership.delete_all_by_customer(customer)
    CustomerTransaction.delete_all_by_customer(customer)
    CustomerPointReward.delete_all_by_customer(customer)
    CustomerStampReward.delete_all_by_customer(customer)
    CustomerPrepaidReward.delete_all_by_customer(customer)
    CustomerEntitledVoucher.delete_all_by_customer(customer)
    RevertedCustomerPointReward.delete_all_by_customer(customer)
    RevertedCustomerStampReward.delete_all_by_customer(customer)
    CustomerEntitledTierRewardSummary.delete_all_by_customer(customer)
    customer.delete()

def __register_user_as_customer(existing_user_acct, outlet):
    created_customer    = None
    merchant_acct       = outlet.merchant_acct_entity
    logger.debug('Valid granted outlet key for merchant acct')
    
    email           = existing_user_acct.email
    mobile_phone    = existing_user_acct.mobile_phone
    
    logger.debug('email=%s', email)
    logger.debug('mobile_phone=%s', mobile_phone)
    
    checking_customer = Customer.get_by_email(email, merchant_acct=merchant_acct) 
    
    if checking_customer:
        is_email_used = True
    else:
        if is_not_empty(mobile_phone):
            checking_customer = Customer.get_by_mobile_phone(mobile_phone, merchant_acct=merchant_acct)
            if checking_customer:
                is_mobile_phone_used = True
    
    logger.debug('is_email_used=%s', is_email_used)
    logger.debug('is_mobile_phone_used=%s', is_mobile_phone_used)
    
    if is_email_used == False and is_mobile_phone_used == False:
    
        created_customer = Customer.create_from_user(outlet, existing_user_acct)
        
        create_merchant_registered_customer_upstream_for_merchant(created_customer)
        create_registered_customer_upstream_for_system(created_customer)
    
        
    logger.debug('created_customer=%s', created_customer)
    
    return created_customer
        
            

@customer_api_bp.route('/register-as-customer', methods=['POST'])
@auth_token_required
@device_is_activated
@request_json
@request_headers
def register_user_as_customer(user_data_in_json, request_headers):
    reference_code              = user_data_in_json.get('reference_code')
    
    logger.debug('register_user_as_customer: user_data_in_json=%s', user_data_in_json)
    
    try:
        if is_not_empty(reference_code):
            logger.debug('customer registration input is valid')
            db_client = create_db_client(caller_info="register_user_as_customer")
            
            created_customer        = None
            existing_user_acct      = None
            is_email_used           = False
            is_mobile_phone_used    = False
            merchant_act_key        = None
            
            merchant_acct           = None
            
            outlet_key  = request_headers.get('x-outlet-key')
            acct_id     = request_headers.get('x-acct-id')
            
            logger.debug('register_user_as_customer: outlet_key=%s', outlet_key)
            logger.debug('register_user_as_customer: acct_id=%s', acct_id)
            logger.debug('register_user_as_customer: reference_code=%s', reference_code)
            
            with db_client.context():
                existing_user_acct  = User.get_by_reference_code(reference_code)
                
                logger.debug('register_user_as_customer: existing_user_acct=%s', existing_user_acct)
                
                if existing_user_acct:
                    
                    outlet              = Outlet.fetch(outlet_key)
                        
                    if outlet:
                        merchant_acct       = outlet.merchant_acct_entity
                        logger.debug('Valid granted outlet key for merchant acct')
                        
                        created_customer = Customer.get_by_reference_code(reference_code, merchant_acct)
                         
                        logger.debug('register_user_as_customer: created_customer=%s', created_customer) 
                         
                        if created_customer is None:
                            
                            created_customer = __register_user_as_customer(existing_user_acct, outlet)
                            

                        logger.debug('created_customer=%s', created_customer)
                        
                    else:
                        logger.warn('Invalid granted outlet key or merchant account id')
                
                if created_customer:
                    
                    
                    '''
                    response_data = {
                                    'customer_key'              : created_customer.key_in_str,
                                    'registered_datetime'       : created_customer.registered_datetime.strftime("%d-%m-%Y %H:%M:%S"),
                                    'reference_code'            : created_customer.reference_code,
                                    'merchant_account_key'      : merchant_act_key,
                                    'company_name'              : merchant_acct.company_name,
                                    'outlet_key'                : outlet_key,  
                                    #'user_details'              : user_details_dict(existing_user_acct),
                                    }
                    
                    response_data.update(user_details_dict(existing_user_acct))
                    '''
                    response_data = return_customer_details(created_customer)
                    
                    logger.debug('register_user_as_customer debug: response_data=%s', response_data)
                    
                    return create_api_message(status_code=StatusCode.OK, **response_data)
                    
                else:
                    if is_email_used==True:
                        return create_api_message('Email have been taken', status_code=StatusCode.BAD_REQUEST)
                    
                    elif is_mobile_phone_used==True:
                        return create_api_message('Mobile phone have been taken', status_code=StatusCode.BAD_REQUEST)
                    else:
                        return create_api_message('Failed to register customer', status_code=StatusCode.BAD_REQUEST)
            
        else:
            logger.warn('customer registration input is invalid')
            
            return create_api_message("Missing register customer input data", status_code=StatusCode.BAD_REQUEST)
    except:
        logger.error('Fail to register customer due to %s', get_tracelog())
        
        return create_api_message(status_code=StatusCode.BAD_REQUEST)

@customer_api_bp.route('/search/<limit>', methods=['POST'])
@auth_token_required
@device_is_activated
@request_json
@request_headers
#@test_session_expired
def search_customer(search_member_data_in_json, request_headers, limit):
    
    #search_member_data_in_json   = request.get_json()
    search_customer_form         = CustomerSearchForm(ImmutableMultiDict(search_member_data_in_json))
    
    logger.debug('search_member_data_in_json=%s', search_member_data_in_json)
    
    db_client = create_db_client(caller_info="search_customer")
    customer_list = []
    
    if search_customer_form.validate():
        name                        = search_customer_form.name.data
        mobile_phone                = search_customer_form.mobile_phone.data
        email                       = search_customer_form.email.data
        reference_code              = search_customer_form.reference_code.data
        merchant_reference_code     = search_customer_form.merchant_reference_code.data
        #customer_data               = search_customer_form.customer_data.data
    
        acct_id     = request_headers.get('x-acct-id')
        
        logger.debug('acct_id=%s', acct_id)
        logger.debug('name=%s', name)
        logger.debug('email=%s', email)
        logger.debug('mobile_phone=%s', mobile_phone)
        logger.debug('reference_code=%s', reference_code)
        logger.debug('merchant_reference_code=%s', merchant_reference_code)
        
        limit_int = int(limit)
        
        with db_client.context():
            merchant_acct   = MerchantAcct.fetch(acct_id)
            (search_results, total_count, next_cursor)  = Customer.search_merchant_customer(merchant_acct, 
                                                                                            name                    = name, 
                                                                                            email                   = email, 
                                                                                            mobile_phone            = mobile_phone, 
                                                                                            reference_code          = reference_code,
                                                                                            merchant_reference_code = merchant_reference_code,
                                                                                            limit                   = limit_int,
                                                                                            )
            
            logger.debug('total_count=%s', total_count)
            logger.debug('next_cursor=%s', next_cursor)
            
            for c in search_results:
                user_details = c.registered_user_acct
                customer_details_dict = c.to_dict(
                                            date_format="%d-%m-%Y", 
                                            datetime_format="%d-%m-%Y %H:%M:%S",
                                            excluded_dict_properties=['registered_merchant_acct'],
                                            )
                customer_details_dict['customer_key']               = c.key_in_str
                customer_details_dict['is_email_verified']          = user_details.is_email_verified
                customer_details_dict['is_mobile_phone_verified']   = user_details.is_mobile_phone_verified
                
                #if 'reward' in customer_data:
                
                if 'entitled_voucher_summary' in customer_details_dict:
                    customer_details_dict['voucher_summary']            = c.entitled_voucher_summary
                    #del customer_details_dict['entitled_voucher_summary'] 
                
                
                logger.debug('customer_details_dict=%s', customer_details_dict)
                
                #if 'membership' in customer_data
                customer_basic_memberships_list = _list_customer_basic_memberships(c)
                if customer_basic_memberships_list:
                    customer_details_dict['basic_memberships'] = customer_basic_memberships_list
                
                tier_membership_data = _get_tier_membership(c)
                if tier_membership_data:
                    customer_details_dict['tier_membership'] = tier_membership_data
                
                customer_list.append(customer_details_dict)
    
        #return create_api_message(status_code=customer_list.OK, customer_list=customer_list)
        customer_details_list_json =  jsonify(customer_list)
            
            
        logger.debug('customer_details_list_json=%s', customer_details_list_json)
            
        return customer_details_list_json
    else:
        error_message = search_customer_form.create_rest_return_error_message()
        return create_api_message(error_message, status_code=StatusCode.BAD_REQUEST)
        #return create_api_message(gettext('Invalid input'), status_code=StatusCode.BAD_REQUEST)
        #return create_api_message('Invalid input', status_code=StatusCode.BAD_REQUEST)

@customer_api_bp.route('/search/customer/<limit>', methods=['POST'])
@auth_token_required
@device_is_activated
@request_json
@request_headers
#@test_session_expired
def search_customer_details_only(search_member_data_in_json, request_headers, limit):
    
    #search_member_data_in_json   = request.get_json()
    search_customer_form         = CustomerSearchForm(ImmutableMultiDict(search_member_data_in_json))
    
    logger.debug('search_member_data_in_json=%s', search_member_data_in_json)
    
    db_client = create_db_client(caller_info="search_customer_details_only")
    customer_list = []
    
    if search_customer_form.validate():
        name                        = search_customer_form.name.data
        mobile_phone                = search_customer_form.mobile_phone.data
        email                       = search_customer_form.email.data
        reference_code              = search_customer_form.reference_code.data
        merchant_reference_code     = search_customer_form.merchant_reference_code.data
        #customer_data               = search_customer_form.customer_data.data
    
        acct_id     = request_headers.get('x-acct-id')
        
        logger.debug('acct_id=%s', acct_id)
        logger.debug('name=%s', name)
        logger.debug('email=%s', email)
        logger.debug('mobile_phone=%s', mobile_phone)
        logger.debug('reference_code=%s', reference_code)
        logger.debug('merchant_reference_code=%s', merchant_reference_code)
        
        limit_int = int(limit)
        
        with db_client.context():
            merchant_acct   = MerchantAcct.fetch(acct_id)
            (search_results, total_count, next_cursor)  = Customer.search_merchant_customer(merchant_acct, 
                                                                                            name                    = name, 
                                                                                            email                   = email, 
                                                                                            mobile_phone            = mobile_phone, 
                                                                                            reference_code          = reference_code,
                                                                                            merchant_reference_code = merchant_reference_code,
                                                                                            limit                   = limit_int,
                                                                                            )
            
            logger.debug('total_count=%s', total_count)
            logger.debug('next_cursor=%s', next_cursor)
            
            for c in search_results:
                user_details = c.registered_user_acct
                customer_details_dict = c.to_dict(
                                            date_format="%d-%m-%Y", 
                                            datetime_format="%d-%m-%Y %H:%M:%S",
                                            excluded_dict_properties=[
                                                'registered_merchant_acct', 'tier_membership', 'memberships_list',
                                                'reward_summary', 'prepaid_summary',
                                                'entitled_voucher_summary', 'entitled_birthday_reward_summary',
                                                'entitled_membership_reward_summary', 'entitled_lucky_draw_ticket_summary',
                                                'kpi_summary','device_details',
                                                ],
                                            )
                customer_details_dict['customer_key']               = c.key_in_str
                customer_details_dict['is_email_verified']          = user_details.is_email_verified
                customer_details_dict['is_mobile_phone_verified']   = user_details.is_mobile_phone_verified
                
                logger.debug('customer_details_dict=%s', customer_details_dict)
                
                customer_list.append(customer_details_dict)
    
        #return create_api_message(status_code=customer_list.OK, customer_list=customer_list)
        customer_details_list_json =  jsonify(customer_list)
            
            
        logger.debug('customer_details_list_json=%s', customer_details_list_json)
            
        return customer_details_list_json
    else:
        error_message = search_customer_form.create_rest_return_error_message()
        return create_api_message(error_message, status_code=StatusCode.BAD_REQUEST)

@customer_api_bp.route('/search/customer-for-membership/<limit>', methods=['POST'])
@auth_token_required
@device_is_activated
@request_json
@request_headers
#@test_session_expired
def search_customer_for_membership(search_member_data_in_json, request_headers, limit):
    
    #search_member_data_in_json   = request.get_json()
    search_customer_form         = CustomerSearchForm(ImmutableMultiDict(search_member_data_in_json))
    
    logger.debug('search_member_data_in_json=%s', search_member_data_in_json)
    
    db_client = create_db_client(caller_info="search_customer")
    customer_list = []
    
    if search_customer_form.validate():
        name                        = search_customer_form.name.data
        mobile_phone                = search_customer_form.mobile_phone.data
        email                       = search_customer_form.email.data
        reference_code              = search_customer_form.reference_code.data
        merchant_reference_code     = search_customer_form.merchant_reference_code.data
        #customer_data               = search_customer_form.customer_data.data
    
        acct_id     = request_headers.get('x-acct-id')
        
        logger.debug('acct_id=%s', acct_id)
        logger.debug('name=%s', name)
        logger.debug('email=%s', email)
        logger.debug('mobile_phone=%s', mobile_phone)
        logger.debug('reference_code=%s', reference_code)
        logger.debug('merchant_reference_code=%s', merchant_reference_code)
        
        limit_int = int(limit)
        
        with db_client.context():
            merchant_acct   = MerchantAcct.fetch(acct_id)
            (search_results, total_count, next_cursor)  = Customer.search_merchant_customer(merchant_acct, 
                                                                                            name                    = name, 
                                                                                            email                   = email, 
                                                                                            mobile_phone            = mobile_phone, 
                                                                                            reference_code          = reference_code,
                                                                                            merchant_reference_code = merchant_reference_code,
                                                                                            limit                   = limit_int,
                                                                                            )
            
            logger.debug('total_count=%s', total_count)
            logger.debug('next_cursor=%s', next_cursor)
            
            for c in search_results:
                customer_details_dict = c.to_dict(
                                            date_format="%d-%m-%Y", 
                                            datetime_format="%d-%m-%Y %H:%M:%S",
                                            excluded_dict_properties=[
                                                'registered_merchant_acct', 'tier_membership', 'memberships_list',
                                                'reward_summary', 'prepaid_summary',
                                                'entitled_voucher_summary', 'entitled_birthday_reward_summary',
                                                'entitled_membership_reward_summary', 'entitled_lucky_draw_ticket_summary',
                                                'kpi_summary','device_details',
                                                ],
                                            )
                customer_details_dict['customer_key']               = c.key_in_str
                
                logger.debug('customer_details_dict=%s', customer_details_dict)
                
                #if 'membership' in customer_data
                customer_basic_memberships_list = _list_customer_basic_memberships(c)
                if customer_basic_memberships_list:
                    customer_details_dict['basic_memberships'] = customer_basic_memberships_list
                
                tier_membership_data = _get_tier_membership(c)
                if tier_membership_data:
                    customer_details_dict['tier_membership'] = tier_membership_data
                
                customer_list.append(customer_details_dict)
    
        #return create_api_message(status_code=customer_list.OK, customer_list=customer_list)
        customer_details_list_json =  jsonify(customer_list)
            
            
        logger.debug('customer_details_list_json=%s', customer_details_list_json)
            
        return customer_details_list_json
    else:
        error_message = search_customer_form.create_rest_return_error_message()
        return create_api_message(error_message, status_code=StatusCode.BAD_REQUEST)



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
        
@customer_api_bp.route('/customer-key/<customer_key>/customer-membership', methods=['GET'])
@auth_token_required
def read_customer_membership(customer_key):
    db_client = create_db_client(caller_info="read_customer_membership")
    
    with db_client.context():
        customer        = Customer.fetch(customer_key)
        customer_membershis_list = _list_customer_basic_memberships(customer)
        tier_membership_data = _get_tier_membership(customer)
        if tier_membership_data:
            customer_membershis_list.append(tier_membership_data)

    return jsonify(customer_membershis_list)  

@customer_api_bp.route('/reference-code/<reference_code>/list-membership', methods=['GET'])
@auth_token_required
@request_headers
#@test_session_expired
def list_customer_membership(request_headers, reference_code):
    if is_not_empty(reference_code):
        acct_id   = request_headers.get('x-acct-id')
        db_client = create_db_client(caller_info="list_customer_membership")
        customer_membershis_list = []
        
        logger.debug('reference_code=%s', reference_code)
        
        with db_client.context():
            merchant_acct   = MerchantAcct.fetch(acct_id)
            customer        = Customer.get_by_reference_code(reference_code, merchant_acct)
            
            customer_membershis_list = _list_customer_basic_memberships(customer)
            tier_membership_data = _get_tier_membership(customer)
            if tier_membership_data:
                customer_membershis_list.append(tier_membership_data)
    
        return jsonify(customer_membershis_list)
    else:
        return create_api_message(status_code=StatusCode.BAD_REQUEST)    
                


@customer_api_bp.route('/reference-code/<reference_code>/transaction/limit/<limit>', methods=['GET'])
@auth_token_required
@request_headers
#@test_session_expired
def list_customer_transaction(request_headers, reference_code, limit):
    
    logger.debug('reference_code=%s', reference_code)
    
    if is_not_empty(reference_code):
        limit_int = int(limit, 10)
        acct_id   = request_headers.get('x-acct-id')
        db_client = create_db_client(caller_info="read_customer_sales_transaction")
        transactions_list = []
        with db_client.context():
            merchant_acct = MerchantAcct.fetch(acct_id)
            customer = Customer.get_by_reference_code(reference_code, merchant_acct)
            
        
        if customer:
            dict_properties  = ['transaction_id', 'invoice_id', 'remarks', 'tax_amount', 'transact_amount', 'reward_giveaway_method',
                               'entitled_reward_summary', 'entitled_voucher_summary', 'entitled_prepaid_summary', 
                               #'transact_outlet_details', 
                               'transact_datetime', 'created_datetime',  'transact_outlet_key', 'is_revert', 'reverted_datetime',
                               'transact_by_username', 'is_reward_redeemed', 'is_sales_transaction', 'allow_to_revert',
                               'is_membership_purchase', 'purchased_merchant_membership_key', 'is_membership_renew',
                               ]
            with db_client.context():
                result       = CustomerTransaction.list_customer_transaction(customer, limit=limit_int)
                for r in result:
                    transactions_list.append(r.to_dict(dict_properties=dict_properties,  date_format="%d-%m-%Y", datetime_format="%d-%m-%Y %H:%M:%S"))
            
            return jsonify(transactions_list)
            
        else:
            logger.warn('Customer transaction with reference code (%s) is not found', reference_code)
            return create_api_message(status_code=StatusCode.BAD_REQUEST)
            
    else:
        return create_api_message(status_code=StatusCode.BAD_REQUEST)
    
@customer_api_bp.route('/reference-code/<reference_code>/transaction/transaction_id/<transaction_id>/revert', methods=['POST'])
@auth_token_required
def revert_customer_transaction(reference_code, transaction_id):
    
    logger.debug('transaction_id=%s', transaction_id)
    
    if is_not_empty(reference_code) and is_not_empty(transaction_id):
        #acct_id   = request_headers.get('x-acct-id')
        db_client = create_db_client(caller_info="revert_customer_sales_transaction")
        
        with db_client.context():
            customer_transactionn       = CustomerTransaction.get_by_transaction_id(transaction_id);
        
        if customer_transactionn:
            with db_client.context():
                merchant_username       = get_logged_in_api_username()
                reverted_by             = MerchantUser.get_by_username(merchant_username)
                
                reverted_datetime_utc   = datetime.utcnow()
                __revert_customer_transaction(customer_transactionn, reverted_by, reverted_datetime=reverted_datetime_utc)
            
            return create_api_message(status_code=StatusCode.OK, reverted_datetime = customer_transactionn.reverted_datetime.strftime('%d-%m-%Y %H:%M:%S'))
        else:    
            return create_api_message(gettext('Failed to find transaction'), status_code=StatusCode.BAD_REQUEST)
        
        
            
    else:
        return create_api_message(gettext('Missing reference code or transaction id'), status_code=StatusCode.BAD_REQUEST)    

@model_transactional(desc="revert_customer_transaction")
def __revert_customer_transaction(customer_transction, reverted_by, reverted_datetime):     
    return revert_transaction(customer_transction, reverted_by, reverted_datetime=reverted_datetime)

    
@customer_api_bp.route('/reference-code/<reference_code>/redemption/limit/<limit>', methods=['GET'])
@auth_token_required
@request_headers
#@test_session_expired
def list_customer_redemption(request_headers, reference_code, limit):
    
    logger.debug('reference_code=%s', reference_code)
    
    if is_not_empty(reference_code):
        limit_int = int(limit, 10)
        acct_id   = request_headers.get('x-acct-id')
        db_client = create_db_client(caller_info="read_customer_sales_transaction")
        redemptions_list = []
        with db_client.context():
            merchant_acct = MerchantAcct.fetch(acct_id)
            customer = Customer.get_by_reference_code(reference_code, merchant_acct)
            
        
        if customer:
            dict_properties  = ['transaction_id', 'invoice_id', 'remarks', 'reward_format', 'redeemed_amount', 'redeemed_summary',
                                   'redeemed_datetime', 'is_revert', 'reverted_datetime',
                                   'redeemed_by_username', 
                                   ]
            with db_client.context():
                result       = CustomerRedemption.list_customer_redemption(customer, limit=limit_int)
                for customer_redemption in result:
                    #fixed reward int and float convertion issue
                    _resolve_int_and_float_for_redeem_summary(customer_redemption.redeemed_summary)
                    customer_redemption_dict = customer_redemption.to_dict(dict_properties=dict_properties,  date_format="%d-%m-%Y", datetime_format="%d-%m-%Y %H:%M:%S")
                    redemptions_list.append(customer_redemption_dict)
            
            return jsonify(redemptions_list)
            
        else:
            logger.warn('Customer transaction with reference code (%s) is not found', reference_code)
            return create_api_message(status_code=StatusCode.BAD_REQUEST)
            
    else:
        return create_api_message(status_code=StatusCode.BAD_REQUEST)    

def _resolve_int_and_float_for_redeem_summary(redeem_summary):
    if 'prepaid' in redeem_summary:
        redeem_summary['prepaid']['amount'] = float(redeem_summary['prepaid']['amount'])
    elif 'point' in redeem_summary:
        redeem_summary['point']['amount'] = float(redeem_summary['point']['amount'])

    return redeem_summary

    
@customer_api_bp.route('/reference-code/<reference_code>/redemption/transaction_id/<transaction_id>/revert', methods=['POST'])
@auth_token_required
@request_headers
def revert_customer_redemption(request_headers, reference_code, transaction_id):
    
    logger.debug('transaction_id=%s', transaction_id)
    
    if is_not_empty(reference_code) and is_not_empty(transaction_id):
        #acct_id   = request_headers.get('x-acct-id')
        db_client = create_db_client(caller_info="revert_customer_sales_transaction")
        
        with db_client.context():
            customer_redemption    = CustomerRedemption.get_by_transaction_id(transaction_id);
        
        if customer_redemption:
            with db_client.context():
                merchant_username       = get_logged_in_api_username()
                reverted_by             = MerchantUser.get_by_username(merchant_username)
                
                reverted_datetime_utc   = datetime.utcnow()
                __revert_customer_redemption(customer_redemption, reverted_by, reverted_datetime=reverted_datetime_utc)
            
            return create_api_message(status_code=StatusCode.OK, reverted_datetime = customer_redemption.reverted_datetime.strftime('%d-%m-%Y %H:%M:%S'))
        else:    
            return create_api_message(gettext('Failed to find transaction'), status_code=StatusCode.BAD_REQUEST)
        
        
            
    else:
        return create_api_message(gettext('Missing reference code or transaction id'), status_code=StatusCode.BAD_REQUEST)
    
@model_transactional(desc="revert_customer_redemption")
def __revert_customer_redemption(customer_redemption, reverted_by, reverted_datetime=None):     
       
    return revert_redemption(customer_redemption, reverted_by, reverted_datetime=reverted_datetime)


          