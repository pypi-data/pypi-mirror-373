from flask import Blueprint, request
import logging
from trexmodel.utils.model.model_util import create_db_client
from trexmodel.models.datastore.merchant_models import MerchantAcct, Outlet,\
    MerchantUser
from trexmodel.models.datastore.customer_models import Customer,\
    CustomerMembership, CustomerTierMembership
from trexapi.decorators.api_decorators import auth_token_required
#from trexadmin.libs.decorators import elapsed_time_trace
from trexmodel.models.datastore.model_decorators import model_transactional
from trexmodel.models.datastore.membership_models import MerchantMembership
from trexapi.utils.api_helpers import get_logged_in_api_username,\
    create_api_message, StatusCode
from trexmodel.models.datastore.transaction_models import CustomerTransaction
from trexmodel.models.datastore.helper.reward_transaction_helper import check_giveaway_reward_for_membership_purchase_transaction
from datetime import datetime
from trexlib.libs.flask_wtf.request_wrapper import request_headers,\
    request_values
from trexlib.utils.string_util import is_not_empty
from flask.json import jsonify


customer_membership_api_bp = Blueprint('customer_membership_api_bp', __name__,
                                 template_folder='templates',
                                 static_folder='static',
                                 url_prefix='/api/v1/customer-membership')

logger = logging.getLogger('debug')


@customer_membership_api_bp.route('/ping', methods=['GET'])
def ping():
    return create_api_message('OK', status_code=StatusCode.OK)

@customer_membership_api_bp.route('/customer/reference-code/<reference_code>', methods=['GET'])
@auth_token_required
@request_headers
def read_customer_membership(request_headers, reference_code):
    acct_id         = request_headers.get('x-acct-id')
    
    
    logger.debug('reference_code=%s', reference_code)
    logger.debug('acct_id=%s', acct_id)
    
    db_client = create_db_client(caller_info="with db_client.context():")
    
    membership_details_list = []
    
    with db_client.context():
        merchant_acct = MerchantAcct.fetch(acct_id)
        customer = Customer.get_by_reference_code(reference_code, merchant_acct)
        if customer:
            customer_memberships_list = CustomerMembership.list_active_by_customer(customer)
            
            if customer_memberships_list:
                for custome_membership in customer_memberships_list:
                    merchant_membership_program = custome_membership.merchant_membership_entity
                    membership_details = {
                                        'label'                     : merchant_membership_program.label,
                                        'desc'                      : merchant_membership_program.desc,
                                        'terms_and_conditions'      : merchant_membership_program.terms_and_conditions,
                                        'entitled_date'             : datetime.strftime(custome_membership.entitled_date, '%d-%m-%Y'),
                                        'expiry_date'               : datetime.strftime(custome_membership.expiry_date, '%d-%m-%Y'),
                                        
                            }
                    membership_details_list.append(membership_details)
                
            customer_tier_memberships_list = CustomerTierMembership.list_active_by_customer(customer)
            
            if customer_tier_memberships_list:
                for custome_membership in customer_tier_memberships_list:
                    merchant_membership_program = custome_membership.merchant_tier_membership_entity
                    membership_details = {
                                        'label'                     : merchant_membership_program.label,
                                        'desc'                      : merchant_membership_program.desc,
                                        'terms_and_conditions'      : merchant_membership_program.terms_and_conditions,
                                        'entitled_date'             : datetime.strftime(custome_membership.entitled_date, '%d-%m-%Y'),
                                        'expiry_date'               : datetime.strftime(custome_membership.expiry_date, '%d-%m-%Y'),
                                        
                            }
                    membership_details_list.append(membership_details)
    
    return jsonify(membership_details_list)            
        

@customer_membership_api_bp.route('/customer/reference-code/<reference_code>/assign-membership', methods=['POST'])
@auth_token_required
@request_values
@request_headers
#@elapsed_time_trace(trace_key="assign_membership")
def assign_membership(request_values, request_headers, reference_code):
    acct_id         = request_headers.get('x-acct-id')
    outlet_key      = request_headers.get('x-outlet-key')
    
    logger.debug('reference_code=%s', reference_code)
    logger.debug('outlet_key=%s', outlet_key)
    logger.debug('acct_id=%s', acct_id)
    
    merchant_membership_key     = request_values.get('merchant_membership_key')
    number_of_year              = request_values.get('number_of_year')
    
    if is_not_empty(number_of_year):
        number_of_year = int(number_of_year)
    
    if is_not_empty(merchant_membership_key):
    
        db_client = create_db_client(caller_info="assign_membership")
        customer_membership = None
        
        with db_client.context():
            merchant_acct = MerchantAcct.fetch(acct_id)
            customer = Customer.get_by_reference_code(reference_code, merchant_acct)
            if customer:
                merchant_membership = MerchantMembership.fetch(merchant_membership_key)
                            
                customer_membership = CustomerMembership.get_by_customer_and_merchant_membership(customer, merchant_membership)
                
        if customer_membership:
            return create_api_message('The customer membership has already been assigned.', status_code=StatusCode.BAD_REQUEST)
        else:
            with db_client.context():    
                merchant_username       = get_logged_in_api_username()
                assigned_by             = MerchantUser.get_by_username(merchant_username)
                assigned_outlet         = Outlet.fetch(outlet_key)
                if customer:
                    __assign_membership(customer, merchant_membership, assigned_by, assigned_outlet, number_of_year=number_of_year)
                
                
        
            return create_api_message(status_code=StatusCode.OK)
            
        
        return create_api_message(status_code=StatusCode.OK)
    else:
        return create_api_message('Missing membership program key', status_code=StatusCode.BAD_REQUEST)

@model_transactional(desc="assign customer membership")
def __assign_membership(customer, merchant_membership, assigned_by, assigned_outlet, number_of_year=None):
    customer_membership = CustomerMembership.create(customer, merchant_membership, assigned_by=assigned_by, assigned_outlet=assigned_outlet, number_of_year=number_of_year)
    
    customer_transaction = CustomerTransaction.create_membership_purchase_transaction(
                                customer, customer_membership, 
                                system_remarks= "Joined Membership", 
                                transact_outlet=assigned_outlet, 
                                transact_by=assigned_by, 
                                )
    
    check_giveaway_reward_for_membership_purchase_transaction(customer, customer_transaction)
    
@customer_membership_api_bp.route('/customer/reference-code/<reference_code>/renew-membership', methods=['POST'])
@auth_token_required
#@elapsed_time_trace(trace_key="renew_membership")
def renew_membership(reference_code):
    acct_id         = request.headers.get('x-acct-id')
    outlet_key      = request.headers.get('x-outlet-key')
    logger.debug('reference_code=%s', reference_code)
    logger.debug('acct_id=%s', acct_id)
    logger.debug('outlet_key=%s', outlet_key)
    
    merchant_membership_key = request.args.get('merchant_membership_key') or request.form.get('merchant_membership_key') or request.json.get('merchant_membership_key')
    
    db_client = create_db_client(caller_info="renew_membership")
    customer_membership = None
    
    with db_client.context():
        merchant_acct = MerchantAcct.fetch(acct_id)
        customer = Customer.get_by_reference_code(reference_code, merchant_acct)
        if customer:
            merchant_membership = MerchantMembership.fetch(merchant_membership_key)
            merchant_username       = get_logged_in_api_username()
            renewed_by              = MerchantUser.get_by_username(merchant_username)
            renewed_outlet          = Outlet.fetch(outlet_key)
            #CustomerMembership.renew(customer, merchant_membership, renewed_datetime=datetime.utcnow())
            try:
                customer_membership = __renew_membership(customer, merchant_membership, renewed_by, renewed_outlet)
            except Exception as e:
                return create_api_message(e.args[0], status_code=StatusCode.BAD_REQUEST)
            
    if customer_membership:
        return create_api_message('Customer membership have been renew successfully', status_code=StatusCode.OK)
    else:
        return create_api_message('Customer membership is not found', status_code=StatusCode.BAD_REQUEST)
        
    
    return create_api_message(status_code=StatusCode.OK)    


@model_transactional(desc="renew customer membership")
def __renew_membership(customer, merchant_membership, renewed_by, renewed_outlet):
    customer_membership = CustomerMembership.renew(customer, merchant_membership, renewed_datetime=datetime.utcnow(), renewed_outlet=renewed_outlet, renewed_by=renewed_by)
    
    customer_transaction = CustomerTransaction.create_membership_purchase_transaction(
                                customer, customer_membership, 
                                system_remarks= "Renewed Membership", 
                                transact_outlet=renewed_outlet, 
                                transact_by=renewed_by, 
                                )
    
    check_giveaway_reward_for_membership_purchase_transaction(customer, customer_transaction)
    
    return  customer_membership   