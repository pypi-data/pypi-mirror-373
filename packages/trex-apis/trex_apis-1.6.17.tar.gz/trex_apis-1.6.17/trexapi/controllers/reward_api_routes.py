'''
Created on 14 Jul 2021

@author: jacklok
'''

from flask import Blueprint 
import logging
from trexlib.utils.log_util import get_tracelog
from trexmodel.utils.model.model_util import create_db_client
from datetime import datetime, timedelta
from trexapi.decorators.api_decorators import auth_token_required,\
    outlet_key_required, device_is_activated
from trexlib.utils.string_util import is_not_empty
from trexmodel.models.datastore.customer_models import Customer
from trexapi.utils.api_helpers import create_api_message, StatusCode
from trexmodel.models.datastore.merchant_models import Outlet,MerchantUser,\
    MerchantAcct
from trexapi.forms.reward_api_forms import GiveRewardTransactionForm, RedeemRewardTransactionForm,\
    PrepaidTopupForm, PrepaidRedeemForm, PointRedeemForm
from werkzeug.datastructures import ImmutableMultiDict
from trexmodel.models.datastore.transaction_models import CustomerTransaction
from trexmodel.models.datastore.helper.reward_transaction_helper import create_reward_transaction,\
    redeem_reward_transaction, create_topup_prepaid_transaction
from trexapi.utils.api_helpers import get_logged_in_api_username
from trexmodel.models.datastore.voucher_models import MerchantVoucher
from trexmodel.models.datastore.prepaid_models import PrepaidSettings
from trexconf import program_conf
from trexlib.libs.flask_wtf.request_wrapper import request_json, request_headers,\
    request_values
from trexmodel.models.datastore.reward_models import CustomerEntitledTierRewardSummary,\
    CustomerPointReward
from trexlib.utils.common.currency_util import currency_amount_based_on_currency
from trexconf.config_util import get_currency_config_by_currency_code

reward_api_bp = Blueprint('reward_api_bp', __name__,
                                 template_folder='templates',
                                 static_folder='static',
                                 url_prefix='/api/v1/reward')

#logger = logging.getLogger('api')
logger = logging.getLogger('target_debug')


@reward_api_bp.route('/reference-code/<reference_code>/read', methods=['GET'])
@auth_token_required
@device_is_activated
@request_headers
def read_reward(request_headers, reference_code):
    acct_id  = request_headers.get('x-acct-id')
    logger.debug('acct_id=%s', acct_id)
    logger.debug('reference_code=%s', reference_code)
    
    customer = None
    
    if is_not_empty(reference_code):
        tier_rewards    = []
        db_client = create_db_client(caller_info="read_reward")
        with db_client.context():
            merchant_acct   = MerchantAcct.fetch(acct_id)
            if merchant_acct:
                customer        = Customer.get_by_reference_code(reference_code, merchant_acct)
            
            '''
            if customer:
                
                all_reward_summary = {}
                
                for k, v in customer.reward_summary.items():
                    all_reward_summary[k] = v.get('amount')
                
                all_voucher_list = []
                    
                for k, v in customer.entitled_voucher_summary.items():
                    for redeem_info in v.get('redeem_info_list'):
                        all_voucher_list.append({
                                            'key'           : k,
                                            'label'         : v.get('label'),
                                            'image_url'     : v.get('image_url'),
                                            'label'         : v.get('label'),
                                            'redeem_code'   : redeem_info.get('redeem_code'),
                                            'effective_date': redeem_info.get('effective_date'),
                                            'expiry_date'   : redeem_info.get('expiry_date'),
                                            })
            '''
            '''
                if all_voucher_list:        
                    all_reward_summary['vouchers'] = all_voucher_list        
            '''
        
        result = {
            #'tier_rewards'      : tier_rewards,
            #'reward_summary'    : customer.reward_summary,
            #'prepaid_summary'   : customer.prepaid_summary,
            #'voucher_summary'   : customer.entitled_voucher_summary,
            }
        if customer:
            currency = get_currency_config_by_currency_code(merchant_acct.currency_code)
            '''
            if tier_rewards:
                result['tier_rewards'] = tier_rewards
            '''
            if customer.reward_summary:
                for reward_type, rewarad_details in customer.reward_summary.items():
                    result[reward_type] = rewarad_details.get('amount')
                
            if customer.prepaid_summary:
                
                result['prepaid'] = currency_amount_based_on_currency(currency, customer.prepaid_summary.get('amount'))
            
            if customer.entitled_voucher_summary:
                all_voucher_list = []
                for k, v in customer.entitled_voucher_summary.items():
                    for redeem_info in v.get('redeem_info_list'):
                        all_voucher_list.append({
                                            'voucher_program_key'   : k,
                                            'label'                 : v.get('label'),
                                            'image_url'             : v.get('image_url'),
                                            'label'                 : v.get('label'),
                                            'redeem_code'           : redeem_info.get('redeem_code'),
                                            'effective_date'        : redeem_info.get('effective_date'),
                                            'expiry_date'           : redeem_info.get('expiry_date'),
                                            })
                result['vouchers'] = all_voucher_list                 
            
            return create_api_message(
                                        entitled_reward_summary  = result, 
                                        status_code=StatusCode.OK
                                        )
        else:    
        
            return create_api_message('Reference code is invalid', status_code=StatusCode.BAD_REQUEST)
            
    else:
        return create_api_message('Reference code is required', status_code=StatusCode.BAD_REQUEST)
    

@reward_api_bp.route('/reference-code/<reference_code>/give', methods=['POST'])
@auth_token_required
@outlet_key_required
@device_is_activated
@request_values
@request_headers
def give_reward(transaction_data_in_json, request_headers, reference_code):
    
    logger.debug('reference_code=%s', reference_code)
    
    if is_not_empty(reference_code):
    
        #transaction_data_in_json   = request.get_json()
        
        logger.debug('transaction_data_in_json=%s', transaction_data_in_json)
        
        reward_transaction_form = GiveRewardTransactionForm(ImmutableMultiDict(transaction_data_in_json))
        
        if reward_transaction_form.validate():
            logger.debug('reward transaction data is valid')
            
            sales_amount        = float(reward_transaction_form.sales_amount.data)
            tax_amount          = reward_transaction_form.tax_amount.data
            invoice_id          = reward_transaction_form.invoice_id.data
            remarks             = reward_transaction_form.remarks.data
            promotion_code      = reward_transaction_form.promotion_code.data
            invoice_details     = transaction_data_in_json.get('invoice_details')
            
            transact_datetime   = None
            
            
            if tax_amount is None:
                tax_amount = .0
            else:
                tax_amount = float(tax_amount)
             
            logger.debug('sales_amount=%s', sales_amount)
            logger.debug('tax_amount=%s', tax_amount)
            logger.debug('invoice_id=%s', invoice_id)
            logger.debug('remarks=%s', remarks)
            logger.debug('invoice_details=%s', invoice_details)
            logger.debug('promotion_code=%s', promotion_code)
            
            db_client = create_db_client(caller_info="give_reward")
            
            check_transaction_by_invoice_id = None
            
            if is_not_empty(invoice_id):
                with db_client.context():
                    check_transaction_by_invoice_id = CustomerTransaction.get_by_invoice_id(invoice_id, promotion_code=promotion_code)
            
            if check_transaction_by_invoice_id:
                return create_api_message("The transaction have been submitted", status_code=StatusCode.BAD_REQUEST)
            else:
                transact_datetime_in_gmt    = reward_transaction_form.transact_datetime.data
                merchant_username           = get_logged_in_api_username()
                
                logger.debug('transact_datetime_in_gmt=%s', transact_datetime_in_gmt)
                
                if merchant_username:
                    try:
                        with db_client.context():
                            transact_outlet         = Outlet.fetch(request_headers.get('x-outlet-key'))
                            merchant_acct           = transact_outlet.merchant_acct_entity
                            customer                = Customer.get_by_reference_code(reference_code, merchant_acct)
                            
                                
                            if transact_datetime_in_gmt:
                                transact_datetime    =  transact_datetime_in_gmt - timedelta(hours=merchant_acct.gmt_hour)
                                
                                now                  = datetime.utcnow()
                                if transact_datetime > now:
                                    return create_api_message('Transact datetime cannot be future', status_code=StatusCode.BAD_REQUEST)
                            
                            
                            
                            transact_merchant_user = MerchantUser.get_by_username(merchant_username)
                            
                            logger.debug('going to call give_reward_transaction')
                            
                            customer_transaction = create_reward_transaction(customer, 
                                                                            transact_outlet     = transact_outlet, 
                                                                            sales_amount        = sales_amount,
                                                                            tax_amount          = tax_amount,
                                                                            invoice_id          = invoice_id,
                                                                            remarks             = remarks,
                                                                            transact_by         = transact_merchant_user,
                                                                            transact_datetime   = transact_datetime,
                                                                            invoice_details     = invoice_details,
                                                                            promotion_code      = promotion_code,
                                                                        )
                            
                        if customer_transaction:
                            
                            transaction_details =  {
                                                    "transaction_id"            : customer_transaction.transaction_id,
                                                    }
                            
                            if customer_transaction.entitled_reward_summary:
                                for k, reward_details in customer_transaction.entitled_reward_summary.items():
                                    transaction_details[k] = reward_details.get('amount')
                                
                            customer_entitled_voucher_list = []
                            
                            if customer_transaction.entitled_prepaid_summary:
                                transaction_details['prepaid'] = customer_transaction.entitled_prepaid_summary.get('amount')
                                
                            
                            logger.debug('entitled_voucher_summary=%s', customer_transaction.entitled_voucher_summary)
                            
                            if customer_transaction.entitled_voucher_summary:
                                
                                for k, voucher_details in customer_transaction.entitled_voucher_summary.items():
                                    
                                    for redeem_info in voucher_details.get('redeem_info_list'):
                                        customer_entitled_voucher_list.append({
                                                                            'voucher_program_key'   : k,
                                                                            'label'                 : voucher_details.get('label'),
                                                                            'image_url'             : voucher_details.get('image_url'),
                                                                            'effective_date'        : redeem_info.get('effective_date'),
                                                                            'expiry_date'           : redeem_info.get('expiry_date'),
                                                                            'redeem_code'           : redeem_info.get('redeem_code'), 
                                                                        })
                            
                                transaction_details['vouchers'] = customer_entitled_voucher_list 
                            
                                
                        
                        return (transaction_details, StatusCode.OK)
                    except:
                        logger.error('Failed to proceed transaction due to %s', get_tracelog())
                        return create_api_message('Failed to proceed transaction', status_code=StatusCode.BAD_REQUEST)
                                
                else:
                    return create_api_message('Missing transact user account', status_code=StatusCode.BAD_REQUEST)
        else:
            logger.warn('reward transaction data input is invalid')
            error_message = reward_transaction_form.create_rest_return_error_message()
            
            return create_api_message(error_message, status_code=StatusCode.BAD_REQUEST)
    else:
        return create_api_message('Reference code is required', status_code=StatusCode.BAD_REQUEST)
    
@reward_api_bp.route('/reference-code/<reference_code>/redeem', methods=['POST'])
@auth_token_required
@outlet_key_required
@device_is_activated
@request_json
@request_headers
def redeem_reward(transaction_data_in_json, request_headers, reference_code):
    
    logger.debug('reference_code=%s', reference_code)
    
    if is_not_empty(reference_code):
    
        #transaction_data_in_json   = request.get_json()
        
        logger.debug('transaction_data_in_json=%s', transaction_data_in_json)
        
        redeem_reward_transaction_form = RedeemRewardTransactionForm(ImmutableMultiDict(transaction_data_in_json))
        
        if redeem_reward_transaction_form.validate():
            logger.debug('reward transaction data is valid')
            
            reward_format           = redeem_reward_transaction_form.reward_format.data
            reward_amount           = redeem_reward_transaction_form.reward_amount.data
            invoice_id              = redeem_reward_transaction_form.invoice_id.data
            remarks                 = redeem_reward_transaction_form.remarks.data
            redeem_datetime_in_gmt  = redeem_reward_transaction_form.redeem_datetime.data
            merchant_username       = get_logged_in_api_username()
            
            if reward_amount:
                reward_amount = float(reward_amount)
            else:
                reward_amount = .0
             
            logger.debug('reward_format=%s', reward_format)
            logger.debug('reward_amount=%s', reward_amount)
            logger.debug('invoice_id=%s', invoice_id)
            logger.debug('remarks=%s', remarks)
            logger.debug('redeem_datetime_in_gmt=%s', redeem_datetime_in_gmt)
            
            db_client = create_db_client(caller_info="redeem_reward")
            with db_client.context():
                redeemed_by_outlet      = Outlet.fetch(request_headers.get('x-outlet-key'))
                merchant_acct           = redeemed_by_outlet.merchant_acct_entity
            
            if redeem_datetime_in_gmt:
                redeem_datetime    =  redeem_datetime_in_gmt - timedelta(hours=merchant_acct.gmt_hour)
                
                now                  = datetime.utcnow()
                if redeem_datetime > now:
                    return create_api_message('Redeem datetime cannot be future', status_code=StatusCode.BAD_REQUEST)
                
                
                
            if merchant_username:
                try:
                    with db_client.context():
                        customer = Customer.get_by_reference_code(reference_code)
                        if customer:
                            merchant_acct   = customer.registered_merchant_acct
                            redeem_outlet = Outlet.fetch(request_headers.get('x-outlet-key'))
                            
                        redeem_by_merchant_user = MerchantUser.get_by_username(merchant_username)
                        
                        logger.debug('going to call redeem_reward_transaction')
                        
                        customer_redemption = redeem_reward_transaction(customer, 
                                                                        redeem_outlet       = redeem_outlet, 
                                                                        reward_format       = reward_format,
                                                                        reward_amount       = reward_amount,
                                                                        invoice_id          = invoice_id,
                                                                        remarks             = remarks,
                                                                        redeemed_by         = redeem_by_merchant_user,
                                                                        redeemed_datetime   = redeem_datetime,
                                                                        
                                                                    )
                        
                    if customer_redemption:
                        
                        transaction_details =  {
                                                "transaction_id"            : customer_redemption.transaction_id,
                                                }
                            
                    return (transaction_details, StatusCode.OK)
                
                except Exception as e:
                    logger.error('Failed to proceed transaction due to %s', get_tracelog())
                    error_message = e.message
                    
                    logger.error('Failed to proceeed transaction due to %s'. error_message)
                    
                    return create_api_message('Failed to proceed transaction', status_code=StatusCode.BAD_REQUEST)
                            
            else:
                return create_api_message('Missing redeem user account', status_code=StatusCode.BAD_REQUEST)
        
        else:
            error_message = redeem_reward_transaction_form.create_rest_return_error_message()
        
            return create_api_message(error_message, status_code=StatusCode.BAD_REQUEST)
        
    else:
        return create_api_message('Reference code is required', status_code=StatusCode.BAD_REQUEST)   
    
@reward_api_bp.route('/reference-code/<reference_code>/prepaid-topup', methods=['POST'])
@auth_token_required
@outlet_key_required
@device_is_activated
@request_json
@request_headers
def prepaid_topup(prepaid_topup_data_in_json, request_headers, reference_code):
    
    logger.debug('reference_code=%s', reference_code)
    
    if is_not_empty(reference_code):  
        #prepaid_topup_data_in_json   = request.get_json()
          
        logger.debug('prepaid_topup_data_in_json=%s', prepaid_topup_data_in_json)
        
        prepaid_topup_form      = PrepaidTopupForm(ImmutableMultiDict(prepaid_topup_data_in_json))
        
        
        
        
        if prepaid_topup_form.validate():
            
            prepaid_program_key     = prepaid_topup_form.prepaid_program_key.data
            topup_amount            = float(prepaid_topup_form.topup_amount.data)
            invoice_id              = prepaid_topup_form.invoice_id.data
            remarks                 = prepaid_topup_form.remarks.data
            merchant_username       = get_logged_in_api_username()
            customer_transaction    = None    
            prepaid_summary         = {}
            
            db_client = create_db_client(caller_info="prepaid_topup")
            with db_client.context():
                topup_outlet            = Outlet.fetch(request_headers.get('x-outlet-key'))
                merchant_acct           = topup_outlet.merchant_acct_entity
                customer_acct           = Customer.get_by_reference_code(reference_code, merchant_acct)
                prepaid_program         = PrepaidSettings.fetch(prepaid_program_key)
                topup_by_merchant_user  = MerchantUser.get_by_username(merchant_username)
                
                if customer_acct and prepaid_program:
                    
                    (customer_transaction, prepaid_summary) = create_topup_prepaid_transaction(customer_acct, prepaid_program, 
                                                                                                topup_amount=topup_amount, 
                                                                                                topup_outlet=topup_outlet, 
                                                                                                topup_by=topup_by_merchant_user, 
                                                                                                invoice_id=invoice_id, 
                                                                                                remarks = remarks,
                                                                                                system_remarks = 'Topup Prepaid',
                                                                                                )
                    
                    
            if customer_transaction is not None:
                
                return create_api_message('Prepaid have been topup successfully',
                                            status_code=StatusCode.OK
                                            )
            else:
                return create_api_message('Failed to topup prepaid', status_code=StatusCode.BAD_REQUEST)
                
        else:
            error_message = prepaid_topup_form.create_rest_return_error_message()
            
            return create_api_message(error_message, status_code=StatusCode.BAD_REQUEST)
        
@reward_api_bp.route('/reference-code/<reference_code>/prepaid-redeem', methods=['POST'])
@auth_token_required
@outlet_key_required
@device_is_activated
@request_json
@request_headers
def prepaid_redeem(prepaid_redeem_data_in_json, request_headers, reference_code):
    
    logger.debug('reference_code=%s', reference_code)
    
    if is_not_empty(reference_code):  
        #prepaid_redeem_data_in_json   = request.get_json()
          
        logger.debug('prepaid_redeem_data_in_json=%s', prepaid_redeem_data_in_json)
        
        prepaid_redeem_form      = PrepaidRedeemForm(ImmutableMultiDict(prepaid_redeem_data_in_json))
        
        
        
        
        if prepaid_redeem_form.validate():
            
            redeem_amount           = float(prepaid_redeem_form.redeem_amount.data)
            invoice_id              = prepaid_redeem_form.invoice_id.data
            remarks                 = prepaid_redeem_form.remarks.data
            merchant_username       = get_logged_in_api_username()
            
            redemption_details      = None
            
            db_client = create_db_client(caller_info="prepaid_redeem")
            with db_client.context():
                redeemed_outlet         = Outlet.fetch(request_headers.get('x-outlet-key'))
                merchant_acct           = redeemed_outlet.merchant_acct_entity
                customer_acct           = Customer.get_by_reference_code(reference_code, merchant_acct)
                redeem_by_merchant_user = MerchantUser.get_by_username(merchant_username)
                
                if customer_acct:
                    redemption_details  = redeem_reward_transaction(customer_acct,  
                                                                redeem_outlet               = redeemed_outlet,
                                                                reward_format               = program_conf.REWARD_FORMAT_PREPAID,
                                                                reward_amount               = redeem_amount,
                                                                invoice_id                  = invoice_id,
                                                                remarks                     = remarks,
                                                                redeemed_by                 = redeem_by_merchant_user, 
                                                                redeemed_datetime           = datetime.utcnow(), 
                                                                )
                    
                    logger.debug('redemption_details=%s', redemption_details)
                    
                    
            if redemption_details is not None:
                
                
                return create_api_message('Prepaid have been redeemed successfully',
                                            status_code=StatusCode.OK
                                            )
            else:
                return create_api_message('Failed to redeem prepaid', status_code=StatusCode.BAD_REQUEST)
                
        else:
            error_message = prepaid_redeem_form.create_rest_return_error_message()
            
            return create_api_message(error_message, status_code=StatusCode.BAD_REQUEST)
        
@reward_api_bp.route('/reference-code/<reference_code>/point-redeem', methods=['POST'])
@auth_token_required
@outlet_key_required
@device_is_activated
@request_json
@request_headers
def point_redeem(point_redeem_data_in_json, request_headers, reference_code):
    
    logger.debug('reference_code=%s', reference_code)
    
    if is_not_empty(reference_code):  
        #point_redeem_data_in_json   = request.get_json()
          
        logger.debug('point_redeem_data_in_json=%s', point_redeem_data_in_json)
        
        point_redeem_form      = PointRedeemForm(ImmutableMultiDict(point_redeem_data_in_json))
        
        
        
        
        if point_redeem_form.validate():
            
            redeem_amount           = float(point_redeem_form.redeem_amount.data)
            invoice_id              = point_redeem_form.invoice_id.data
            remarks                 = point_redeem_form.remarks.data
            merchant_username       = get_logged_in_api_username()
            
            redemption_details      = None
            
            db_client = create_db_client(caller_info="prepaid_redeem")
            with db_client.context():
                redeemed_outlet         = Outlet.fetch(request_headers.get('x-outlet-key'))
                merchant_acct           = redeemed_outlet.merchant_acct_entity
                customer_acct           = Customer.get_by_reference_code(reference_code, merchant_acct)
                redeem_by_merchant_user = MerchantUser.get_by_username(merchant_username)
                
                if customer_acct:
                    redemption_details  = redeem_reward_transaction(customer_acct,  
                                                                redeem_outlet               = redeemed_outlet,
                                                                reward_format               = program_conf.REWARD_FORMAT_POINT,
                                                                reward_amount               = redeem_amount,
                                                                invoice_id                  = invoice_id,
                                                                remarks                     = remarks,
                                                                redeemed_by                 = redeem_by_merchant_user, 
                                                                redeemed_datetime           = datetime.utcnow(), 
                                                                )
                    
                    logger.debug('redemption_details=%s', redemption_details)
                    
                    
            if redemption_details is not None:
                
                
                return create_api_message('Point have been redeemed successfully',
                                            status_code=StatusCode.OK
                                            )
            else:
                return create_api_message('Failed to redeem point', status_code=StatusCode.BAD_REQUEST)
                
        else:
            error_message = point_redeem_form.create_rest_return_error_message()
            
            return create_api_message(error_message, status_code=StatusCode.BAD_REQUEST)        
                
