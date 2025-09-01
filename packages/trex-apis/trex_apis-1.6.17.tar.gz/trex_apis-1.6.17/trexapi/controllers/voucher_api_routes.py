'''
Created on 19 Jul 2021

@author: jacklok
'''

from flask import Blueprint 
import logging
from trexlib.utils.log_util import get_tracelog
from trexmodel.utils.model.model_util import create_db_client
from datetime import datetime, timedelta
from trexapi.decorators.api_decorators import auth_token_required,\
    device_is_activated,\
    user_auth_token_required_pass_reference_code
from trexlib.utils.string_util import is_not_empty
from trexapi.utils.api_helpers import create_api_message, StatusCode
from trexmodel.models.datastore.merchant_models import Outlet,\
    MerchantUser, MerchantAcct
from trexapi.forms.reward_api_forms import VoucherRedeemForm
from werkzeug.datastructures import ImmutableMultiDict
import json
from trexapi.utils.api_helpers import get_logged_in_api_username
from trexmodel.models.datastore.voucher_models import MerchantVoucher
from trexmodel.models.datastore.reward_models import CustomerEntitledVoucher

from trexmodel.models.datastore.redeem_models import CustomerRedemption
from trexanalytics.bigquery_upstream_data_config import create_merchant_customer_redemption_upstream_for_merchant,\
    create_removed_customer_voucher_to_upstream_for_merchant,\
    create_redeemed_customer_voucher_to_upstream_for_merchant
from trexmodel import program_conf
from trexmodel.models.datastore.user_models import User
from flask.json import jsonify
from trexmodel.models.datastore.model_decorators import model_transactional
from trexmodel.models.datastore.helper.reward_model_helpers import check_redeem_voucher_is_valid
from flask_babel import gettext
from trexlib.libs.flask_wtf.request_wrapper import request_json, request_headers,\
    request_values
from trexmodel.models.datastore.customer_models import Customer

logger = logging.getLogger('api')


voucher_api_bp = Blueprint('voucher_api_bp', __name__,
                                 template_folder='templates',
                                 static_folder='static',
                                 url_prefix='/api/v1/vouchers')

#logger = logging.getLogger('api')
logger = logging.getLogger('target_debug')

@voucher_api_bp.route('/ping', methods=['GET'])
def ping():
    return create_api_message('Pong', status_code=StatusCode.OK)

@voucher_api_bp.route('/voucher/<redeem_code>/details', methods=['POST','GET'])
@voucher_api_bp.route('/redeem-code/<redeem_code>', methods=['GET'])
@auth_token_required
@device_is_activated
def read_voucher(redeem_code):
    logger.info('redeem_code=%s', redeem_code)
    if is_not_empty(redeem_code):
        voucher_details = None
        db_client = create_db_client(caller_info="read_voucher")
        
        with db_client.context():
            customer_voucher    = CustomerEntitledVoucher.get_by_redeem_code(redeem_code)
            if customer_voucher:
                merchant_voucher    = MerchantVoucher.fetch(customer_voucher.entitled_voucher_key)
                voucher_conf        = merchant_voucher.configuration
                if merchant_voucher.configuration:
                    if isinstance(merchant_voucher.configuration, str):
                        voucher_conf = json.loads(merchant_voucher.configuration)
                else:
                    voucher_conf = {}
                voucher_details = {
                                    'key'                   : merchant_voucher.key_in_str,
                                    'label'                 : merchant_voucher.label,
                                    'desc'                  : merchant_voucher.desc,
                                    'terms_and_conditions'  : merchant_voucher.terms_and_conditions,
                                    'configuration'         : voucher_conf,
                                    'image_url'             : merchant_voucher.image_public_url,
                                    'redeem_info_list'      : [
                                                                {
                                                                    'effective_date'    : customer_voucher.effective_date.strftime('%d-%m-%Y'),
                                                                    'expiry_date'       : customer_voucher.expiry_date.strftime('%d-%m-%Y'),
                                                                    'redeem_code'       : redeem_code,
                                                                    'is_redeem'         : customer_voucher.is_used,
                                                                    'is_revert'         : customer_voucher.is_reverted,
                                                                }
                                                            ],
                                    }
                
        
        if voucher_details is None:
            return create_api_message('Invalid voucher code', status_code=StatusCode.BAD_REQUEST)
        else:
            #return create_api_message(voucher_details=voucher_details, status_code=StatusCode.OK)
            
            logging.debug('voucher_details=%s', voucher_details)
            
            return jsonify(voucher_details)
    else:
        return create_api_message('Voucher code is required', status_code=StatusCode.BAD_REQUEST) 
    
@voucher_api_bp.route('/voucher/redeem', methods=['post'])
@voucher_api_bp.route('/redeem', methods=['post'])
@auth_token_required
@device_is_activated
@request_values
@request_headers
def redeem_voucher(redeem_voucher_data_in_json, request_headers):
    
    #redeem_voucher_data_in_json   = request.get_json()
    
    redeem_voucher_form = VoucherRedeemForm(ImmutableMultiDict(redeem_voucher_data_in_json))
    
    if redeem_voucher_form.validate():
    
        redeem_code         = redeem_voucher_data_in_json.get('redeem_code')
        invoice_id          = redeem_voucher_form.invoice_id.data
        remarks             = redeem_voucher_form.remarks.data
        redeemed_datetime   = redeem_voucher_form.redeem_datetime.data
        merchant_acct       = None
        redeemed_by         = None
        redeemed_by_outlet  = None
        
        logger.info('redeem_code=%s', redeem_code)
        logger.info('redeemed_datetime=%s', redeemed_datetime)
        
        
        if redeem_code:
            redeem_code_list = redeem_code.split(',')
            
            if redeemed_datetime is None:
                redeemed_datetime = datetime.utcnow();
            
            db_client = create_db_client(caller_info="redeem_voucher")
            with db_client.context():
                redeemed_by_outlet      = Outlet.fetch(request_headers.get('x-outlet-key'))
                merchant_acct           = MerchantAcct.fetch(request_headers.get('x-acct-id'))
            
            redeem_datetime             = redeem_voucher_form.redeem_datetime.data
            merchant_username           = get_logged_in_api_username()
            
            
            if redeem_datetime:
                redeem_datetime_in_gmt      = redeem_datetime - timedelta(hours=merchant_acct.gmt_hour)
                now                         = datetime.utcnow()
                if redeem_datetime_in_gmt > now:
                    return create_api_message('Redeem datetime cannot be future', status_code=StatusCode.BAD_REQUEST)
            
            
            
            to_redeem_voucher_keys_list                             = []
            customer                                                = None
            customer_vouchers_list                                  = []
            
            with db_client.context():
                merchant_username       = get_logged_in_api_username()
                redeemed_by             = MerchantUser.get_by_username(merchant_username)
                
                for redeem_code in redeem_code_list:
                    customer_voucher    = CustomerEntitledVoucher.get_by_redeem_code(redeem_code)
                    customer_vouchers_list.append(customer_voucher)
                    to_redeem_voucher_keys_list.append(customer_voucher.key_in_str)
                    
                    if customer is None:
                        customer = customer_voucher.entitled_customer_entity
                    else:
                        #this is used to check every voucher must same customer
                        checking_customer = customer_voucher.entitled_customer_entity
                        if checking_customer.key_in_str!=customer.key_in_str:
                            return create_api_message(gettext('Voucher must from same customer'), status_code=StatusCode.BAD_REQUEST)
                            
                
            try:
                with db_client.context():
                    check_redeem_voucher_is_valid(customer, customer_vouchers_list, redeem_datetime=redeem_datetime)
                
                logger.info('after completed redeem voucher checking')
            except Exception as error:
                logger.error('Failed due to %s', get_tracelog())
                return create_api_message(str(error), status_code=StatusCode.BAD_REQUEST)
            
            if to_redeem_voucher_keys_list:
                with db_client.context():
                    if to_redeem_voucher_keys_list:
                        
                        customer_redemption = __start_transaction_for_redeem_voucher(customer, redeemed_by_outlet, redeemed_by, redeemed_datetime, invoice_id, remarks, customer_vouchers_list, to_redeem_voucher_keys_list, )
                        
                        logger.debug('customer_redemption=%s', customer_redemption)
                        
        
                    if customer_redemption:
                        create_merchant_customer_redemption_upstream_for_merchant(customer_redemption, )
                
                if customer_redemption:        
                    return create_api_message(transaction_id = customer_redemption.transaction_id, status_code=StatusCode.OK)
                else:
                    return create_api_message("Failed to redeem voucher", status_code=StatusCode.BAD_REQUEST)
            else:
                return create_api_message('Voucher redeem code is required', status_code=StatusCode.BAD_REQUEST)
                
    else:
        logger.warn('redeem voucher data input is invalid')
        error_message = redeem_voucher_form.create_rest_return_error_message()
            
        return create_api_message(error_message, status_code=StatusCode.BAD_REQUEST)

@model_transactional(desc='redeem_voucher')
def __start_transaction_for_redeem_voucher(customer, redeemed_by_outlet, redeemed_by, redeemed_datetime, invoice_id, remarks, customer_vouchers_list, to_redeem_voucher_keys_list, ):
    
    customer_redemption = CustomerRedemption.create(customer, program_conf.REWARD_FORMAT_VOUCHER , 
                                              redeemed_outlet               = redeemed_by_outlet,
                                              redeemed_amount               = 1,            
                                              redeemed_voucher_keys_list    = to_redeem_voucher_keys_list, 
                                              redeemed_by                   = redeemed_by, 
                                              redeemed_datetime             = redeemed_datetime,
                                              invoice_id                    = invoice_id,
                                              remarks                       = remarks,
                                              )
    
    transaction_id = customer_redemption.transaction_id
    
    logger.info('voucher redemption transaction_id=%s', transaction_id)
    
    for voucher in customer_vouchers_list:
        voucher.redeem(redeemed_by=redeemed_by, 
                       redeemed_outlet=redeemed_by_outlet, 
                       redeemed_datetime=redeemed_datetime, 
                       transaction_id=transaction_id)
        
    for customer_voucher in customer_vouchers_list:
        
        create_redeemed_customer_voucher_to_upstream_for_merchant(customer_voucher) 
    
    return customer_redemption
        
@voucher_api_bp.route('/voucher/<redeem_code>/remove', methods=['DELETE'])
@auth_token_required
@device_is_activated
def remove_voucher(redeem_code):
    
    #remove_voucher_data_in_json   = request.get_json()
    
    if redeem_code:
        #redeem_code_list = redeem_code_list.split(',')
        redeem_code_list = redeem_code.split(',')
        
        db_client = create_db_client(caller_info="remove_voucher")
        
        to_remove_voucher_keys_list                         = []
        found_not_valid_redeem_code_list                    = []
        customer_vouchers_list                              = []
        removed_by                                          = None    
        
        with db_client.context():
            #merchant_acct           = MerchantAcct.fetch(request_headers.get('x-acct-id'))
            merchant_username       = get_logged_in_api_username()
            removed_by              = MerchantUser.get_by_username(merchant_username)
            
            
            for redeem_code in redeem_code_list:
                customer_voucher    = CustomerEntitledVoucher.get_by_redeem_code(redeem_code)
                if customer_voucher:
                    to_remove_voucher_keys_list.append(customer_voucher.key_in_str)
                else:
                    found_not_valid_redeem_code_list.append(redeem_code)
        
        @model_transactional(desc='remove_voucher')
        def __start_transaction_for_remove_voucher():
            for customer_voucher in customer_vouchers_list:
                create_removed_customer_voucher_to_upstream_for_merchant(customer_voucher)
                
                customer_voucher.remove(removed_by)
                            
                customer = customer_voucher.entitled_customer_acct
                customer.update_after_removed_voucher(customer_voucher)
        
        if found_not_valid_redeem_code_list:
            
            return create_api_message("Voucher ({redeem_codes_list}) is not valid".format(redeem_codes_list=",".join(found_not_valid_redeem_code_list)), 
                                       status_code=StatusCode.BAD_REQUEST)            
        else:
            if to_remove_voucher_keys_list:
                with db_client.context():
                    if to_remove_voucher_keys_list:
                        for voucher_key in to_remove_voucher_keys_list:
                            customer_voucher = CustomerEntitledVoucher.fetch(voucher_key)
                            customer_vouchers_list.append(customer_voucher)
                            
                        __start_transaction_for_remove_voucher()
                        
                return create_api_message(status_code=StatusCode.OK)
                
            else:
                return create_api_message('Voucher redeem code is required', status_code=StatusCode.BAD_REQUEST)
    
    else:
        return create_api_message('Voucher redeem code is required', status_code=StatusCode.BAD_REQUEST)
                
             

@voucher_api_bp.route('/entitled/<reference_code>', methods=['GET'])
def list_entitled_voucher(reference_code):
    
    logger.debug('list_entitled_voucher: going to list entitled voucher by reference code=%s', reference_code)
    
    if is_not_empty(reference_code):
        db_client       = create_db_client(caller_info="list_entitled_voucher")
        user_acct       = None
        voucher_list    = []
        
        
        with db_client.context():
            user_acct = User.get_by_reference_code(reference_code)
        
            if user_acct:
                result = CustomerEntitledVoucher.list_all_by_user_acct(user_acct)
                if result:
                    for r in result:
                        voucher_list.append(r.to_dict())    
            
            
        
                                       
        return {
                'vouchers': voucher_list,
            }
            
    else:
        logger.warn('reset_password_post: email is invalid')
        return create_api_message(status_code=StatusCode.BAD_REQUEST)       
    
@voucher_api_bp.route('/voucher/<redeem_code>/remove-by-user', methods=['DELETE'])
@user_auth_token_required_pass_reference_code
@request_headers
def remove_user_voucher(request_headers, reference_code, redeem_code):
    logger.info('reference_code=%s', reference_code)
    logger.info('redeem_code=%s', redeem_code)
    
    if is_not_empty(redeem_code):
        reference_code      = request_headers.get('x-reference-code')
        
        logger.debug('reference_code=%s', reference_code)
        db_client = create_db_client(caller_info="remove_user_voucher")
        
        with db_client.context():
            customer_voucher    = CustomerEntitledVoucher.get_by_redeem_code(redeem_code)
            
            if customer_voucher: 
                
                customer_voucher.remove()  
                customer = customer_voucher.entitled_customer_acct
                customer.update_after_removed_voucher(customer_voucher)
                return create_api_message(status_code=StatusCode.OK)
            else:
                merchant_acct_key = request_headers.get('x-acct-id')
                if is_not_empty(merchant_acct_key):
                    merchant_acct           = MerchantAcct.fetch(merchant_acct_key)
                    if merchant_acct:
                        customer = Customer.get_by_reference_code(reference_code, merchant_acct)
                        if customer:
                            customer.update_after_removed_voucher_by_redeem_code(redeem_code)
                            
                            return create_api_message(status_code=StatusCode.OK)
        
    else:
        return create_api_message('Missing voucher redeem code', status_code=StatusCode.BAD_REQUEST)
