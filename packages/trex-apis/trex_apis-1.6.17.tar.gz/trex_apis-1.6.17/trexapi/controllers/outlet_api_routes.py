'''
Created on 20 Jul 2022

@author: jacklok
'''
#from flask.blueprints import Blueprint
import logging
from flask import abort
from flask.blueprints import Blueprint
from trexlib.utils.string_util import is_not_empty
from trexmodel.models.datastore.merchant_models import Outlet, BannerFile,\
    MerchantUser
from trexmodel.utils.model.model_util import create_db_client
from trexmodel.models.datastore.product_models import ProductCatalogue
from trexapi.controllers.pos_api_routes import get_product_category_structure_code_label_json
from trexmodel.models import merchant_helpers
from trexmodel.models.datastore.transaction_models import CustomerTransaction,\
    SalesTransaction
from flask.json import jsonify
from trexapi.decorators.api_decorators import auth_token_required
from trexapi.utils.api_helpers import get_logged_in_api_username,\
    create_api_message, StatusCode
from flask_babel import gettext
from trexmodel.models.datastore.helper.reward_transaction_helper import revert_redemption,\
    revert_transaction
from trexmodel.models.datastore.redeem_models import CustomerRedemption 
from trexmodel.models.datastore.model_decorators import model_transactional
from datetime import datetime
from trexapi.libs.api_decorator import elapsed_time_trace
from trexmodel.models.datastore.helper.sales_transaction_helpers import revert_sales_transaction


outlet_api_bp = Blueprint('outlet_api_bp', __name__,
                                 template_folder='templates',
                                 static_folder='static',
                                 url_prefix='/api/v1/outlets')

logger = logging.getLogger('debug')

@outlet_api_bp.route('/<outlet_key>/details', methods=['GET'])
def read_outlet(outlet_key):
    
    outlet_details          = None
    merchant_acct           = None
    catalogue_details       = None
    outlet_setting_in_json  = {}   
    output_json             = {
                                'score': 0.0
                                } 
    
    if is_not_empty(outlet_key):
        db_client = create_db_client(caller_info="read_outlet")
        with db_client.context():
            outlet_details      = Outlet.fetch(outlet_key)
            if outlet_details:
                merchant_acct           = outlet_details.merchant_acct_entity
                catalogue_key           = outlet_details.assigned_catalogue_key
                outlet_setting_in_json  = merchant_helpers.construct_setting_by_outlet(outlet_details)
                logger.debug('assigned catalogue_key=%s', catalogue_key)
                banner_listing = []
                
                banner_file_listing =  BannerFile.list_by_merchant_acct(merchant_acct)
                logger.debug('banner_file_listing=%s', banner_file_listing)
                if banner_file_listing:
                    for banner_file in banner_file_listing:
                        banner_listing.append(banner_file.banner_file_public_url)
                    
                    outlet_setting_in_json['banners'] = banner_listing
                        
                product_catalogue   = ProductCatalogue.fetch(catalogue_key)
            
                if product_catalogue:
                    logger.debug('Found catalogue')
                    last_updated_datetime               = outlet_details.modified_datetime
                        
                    category_tree_structure_in_json     = get_product_category_structure_code_label_json(merchant_acct)
                    
                    catalogue_details =  {
                                        'key'                       : catalogue_key,    
                                        'category_list'             : category_tree_structure_in_json,
                                        'product_by_category_map'   : product_catalogue.published_menu_settings,
                                        'last_updated_datetime'     : last_updated_datetime.strftime('%d-%m-%Y %H:%M:%S')
                                    }
    
    if outlet_setting_in_json:
        output_json['settings'] = outlet_setting_in_json
        
        if catalogue_details:
            output_json['product_catalogue'] = catalogue_details
        
        
        return output_json
    else:
        abort
        
        
#@outlet_api_bp.route('/outlet-key/<outlet_key>/sales-transaction/limit/<limit>', methods=['GET'])
@outlet_api_bp.route('/outlet-key/<outlet_key>/customer-transaction/limit/<limit>', methods=['GET'])
@auth_token_required
#@elapsed_time_trace(trace_key='list_outlet_customer_transaction')
#@test_session_expired
def list_outlet_customer_transaction(outlet_key, limit):
    db_client = create_db_client(caller_info="list_outlet_customer_transaction")
    transactions_list = []
    limit_int = int(limit)
    
    with db_client.context():
        outlet = Outlet.fetch(outlet_key)
        
        
    
    if outlet:
        dict_properties  = ['transaction_id', 'invoice_id', 'remarks', 'tax_amount', 'transact_amount', 'reward_giveaway_method',
                           'entitled_reward_summary', 'entitled_voucher_summary', 'entitled_prepaid_summary', 
                           #'transact_customer_acct',
                           'transact_datetime', 'created_datetime',  'transact_outlet_key', 'is_revert', 'reverted_datetime',
                           'transact_by_username', 'is_reward_redeemed', 'is_sales_transaction', 'allow_to_revert',
                           'is_membership_purchase', 'purchased_merchant_membership_key', 'is_membership_renew',
                           ]
        with db_client.context():
            result       = CustomerTransaction.list_outlet_transaction(outlet, limit=limit_int)
            for r in result:
                transactions_list.append(r.to_dict(dict_properties=dict_properties,  date_format="%d-%m-%Y", datetime_format="%d-%m-%Y %H:%M:%S"))
        
        return jsonify(transactions_list)
        
    else:
        return create_api_message(status_code=StatusCode.BAD_REQUEST)   
    
@outlet_api_bp.route('/outlet-key/<outlet_key>/sales-transaction/limit/<limit>', methods=['GET'])
@auth_token_required
#@elapsed_time_trace(trace_key='list_outlet_sales_transaction')
#@test_session_expired
def list_outlet_sales_transaction(outlet_key, limit):
    db_client = create_db_client(caller_info="list_outlet_sales_transaction")
    transactions_list = []
    limit_int = int(limit)
    
    with db_client.context():
        outlet = Outlet.fetch(outlet_key)
        
        
    
    if outlet:
        dict_properties  = ['transaction_id', 'invoice_id', 'remarks', 'tax_amount', 'transact_amount', 'used',
                           'transact_datetime', 'created_datetime',  'transact_outlet_key', 'is_revert', 'reverted_datetime',
                           'transact_by_username', 'is_sales_transaction', 'allow_to_revert',
                           ]
        with db_client.context():
            result       = SalesTransaction.list_outlet_transaction(outlet, limit=limit_int)
            for r in result:
                transactions_list.append(r.to_dict(dict_properties=dict_properties,  date_format="%d-%m-%Y", datetime_format="%d-%m-%Y %H:%M:%S"))
        
        return jsonify(transactions_list)
        
    else:
        return create_api_message(status_code=StatusCode.BAD_REQUEST)   


@outlet_api_bp.route('/outlet-key/<outlet_key>/redemption/limit/<limit>', methods=['GET'])
@auth_token_required
#@test_session_expired
def list_outlet_redemption(outlet_key, limit):
    db_client = create_db_client(caller_info="list_outlet_transaction")
    redemptions_list = []
    limit_int = int(limit)
    
    with db_client.context():
        outlet = Outlet.fetch(outlet_key)
        
        
    
    if outlet:
        dict_properties  = ['transaction_id', 'invoice_id', 'remarks', 'reward_format', 'redeemed_amount', 'redeemed_summary',
                           'redeemed_datetime', 'is_revert', 'reverted_datetime', 
                           #'redeemed_customer_acct',
                           'redeemed_by_username', 
                           ]
        with db_client.context():
            result       = CustomerRedemption.list_by_outlet(outlet, limit=limit_int)
            for r in result:
                redemption_dict = r.to_dict(
                                            dict_properties=dict_properties,
                                            excluded_dict_properties=['redeemed_customer_acct','redeemed_merchant_acct'], 
                                            date_format="%d-%m-%Y", 
                                            datetime_format="%d-%m-%Y %H:%M:%S",
                                            
                                            )
                logger.debug('redemption_dict=%s', redemption_dict)
                redemptions_list.append(redemption_dict)
        
        return jsonify(redemptions_list)
        
    else:
        return create_api_message(status_code=StatusCode.BAD_REQUEST)        

@outlet_api_bp.route('/outlet-key/<outlet_key>/transaction/transaction-id/<transaction_id>/revert', methods=['POST'])
@outlet_api_bp.route('/outlet-key/<outlet_key>/customer-transaction/transaction-id/<transaction_id>/revert', methods=['POST'])
@auth_token_required
def revert_outlet_customer_transaction(outlet_key, transaction_id):
    
    logger.debug('transaction_id=%s', transaction_id)
    
    if is_not_empty(outlet_key) and is_not_empty(transaction_id):
        db_client = create_db_client(caller_info="revert_outlet_customer_transaction")
        
        with db_client.context():
            customer_transactionn    = CustomerTransaction.get_by_transaction_id(transaction_id);
        
        if customer_transactionn:
            logger.debug('outlet_key=%s', outlet_key)
            logger.debug('customer_transactionn.transact_outlet_key=%s', customer_transactionn.transact_outlet_key)
            if customer_transactionn.transact_outlet_key == outlet_key:
                with db_client.context():
                    merchant_username       = get_logged_in_api_username()
                    reverted_by             = MerchantUser.get_by_username(merchant_username)
                    reverted_datetime_utc   = datetime.utcnow()
                    
                    __revert_customer_transaction(customer_transactionn, reverted_by, reverted_datetime=reverted_datetime_utc)
                
                return create_api_message(status_code=StatusCode.OK, reverted_datetime = datetime.now().strftime('%d-%m-%Y %H:%M:%S'))
                #return create_api_message(status_code=StatusCode.OK)
            else:
                return create_api_message(gettext('Not allow to revert from different outlet'), status_code=StatusCode.BAD_REQUEST)
        else:    
            return create_api_message(gettext('Failed to find customer transaction'), status_code=StatusCode.BAD_REQUEST)
        
        
            
    else:
        return create_api_message(gettext('Missing transaction id'), status_code=StatusCode.BAD_REQUEST) 
    
@outlet_api_bp.route('/outlet-key/<outlet_key>/sales-transaction/transaction-id/<transaction_id>/revert', methods=['POST'])
@auth_token_required
def revert_outlet_sales_transaction(outlet_key, transaction_id):
    
    logger.debug('transaction_id=%s', transaction_id)
    
    if is_not_empty(outlet_key) and is_not_empty(transaction_id):
        db_client = create_db_client(caller_info="revert_outlet_sales_transaction")
        
        with db_client.context():
            sales_transactionn    = SalesTransaction.get_by_transaction_id(transaction_id);
        
        if sales_transactionn:
            logger.debug('outlet_key=%s', outlet_key)
            logger.debug('sales_transactionn.transact_outlet_key=%s', sales_transactionn.transact_outlet_key)
            if sales_transactionn.transact_outlet_key == outlet_key:
                with db_client.context():
                    merchant_username       = get_logged_in_api_username()
                    reverted_by             = MerchantUser.get_by_username(merchant_username)
                    reverted_datetime_utc   = datetime.utcnow()
                    __revert_sales_transaction(sales_transactionn, reverted_by, reverted_datetime=reverted_datetime_utc)
                
                return create_api_message(status_code=StatusCode.OK, reverted_datetime = datetime.now().strftime('%d-%m-%Y %H:%M:%S'))
                #return create_api_message(status_code=StatusCode.OK)
            else:
                return create_api_message(gettext('Not allow to revert from different outlet'), status_code=StatusCode.BAD_REQUEST)
        else:    
            return create_api_message(gettext('Failed to find sales transaction'), status_code=StatusCode.BAD_REQUEST)
        
        
            
    else:
        return create_api_message(gettext('Missing transaction id'), status_code=StatusCode.BAD_REQUEST)     
    
@outlet_api_bp.route('/outlet-key/<outlet_key>/redemption/transaction-id/<transaction_id>/revert', methods=['POST'])
@outlet_api_bp.route('/outlet/<outlet_key>/redemption/transaction-id/<transaction_id>/revert', methods=['POST'])
@auth_token_required
def revert_outlet_redemption(outlet_key, transaction_id):
    
    logger.debug('transaction_id=%s', transaction_id)
    
    if is_not_empty(outlet_key) and is_not_empty(transaction_id):
        db_client = create_db_client(caller_info="revert_outlet_redemption")
        
        with db_client.context():
            customer_redemption    = CustomerRedemption.get_by_transaction_id(transaction_id);
        
        if customer_redemption:
            if customer_redemption.redeemed_outlet_key == outlet_key:
                with db_client.context():
                    merchant_username       = get_logged_in_api_username()
                    reverted_by             = MerchantUser.get_by_username(merchant_username)
                    
                    reverted_datetime_utc   = datetime.utcnow()
                    __revert_customer_redemption(customer_redemption, reverted_by, reverted_datetime=reverted_datetime_utc)
                
                return create_api_message(status_code=StatusCode.OK, reverted_datetime = customer_redemption.reverted_datetime.strftime('%d-%m-%Y %H:%M:%S'))
            else:
                return create_api_message(gettext('Not allow to revert from different outlet'), status_code=StatusCode.BAD_REQUEST)
        else:    
            return create_api_message(gettext('Failed to find redemption'), status_code=StatusCode.BAD_REQUEST)
        
        
            
    else:
        return create_api_message(gettext('Missing transaction id'), status_code=StatusCode.BAD_REQUEST)

@outlet_api_bp.route('/sales-transaction/<transaction_id>/customert-brief', methods=['GET'])
#@elapsed_time_trace(trace_key='read_outlet_reward_transaction_customer_brief')
@auth_token_required
#@test_session_expired
def read_outlet_reward_transaction_customer_brief(transaction_id):
    db_client = create_db_client(caller_info="read_outlet_reward_transaction_customer_brief")
    transact_user_acct = None
    with db_client.context():
        custome_transaction     = CustomerTransaction.get_by_transaction_id(transaction_id)
        if custome_transaction:
            transact_user_acct  = custome_transaction.transact_customer_acct
            if transact_user_acct:
                dict_properties  = ['name', 'reference_code','customer_key']
                transact_user_acct = transact_user_acct.to_dict(dict_properties=dict_properties)
        
        
    
    if transact_user_acct:
        logger.debug('transact_user_acct=%s', transact_user_acct)
        return jsonify(transact_user_acct)
        
    else:
        return create_api_message(status_code=StatusCode.BAD_REQUEST)
    
@outlet_api_bp.route('/redemption/<transaction_id>/customert-brief', methods=['GET'])
#@elapsed_time_trace(trace_key='read_outlet_redemption_customer_brief')
@auth_token_required
#@test_session_expired
def read_outlet_redemption_customer_brief(transaction_id):
    db_client = create_db_client(caller_info="read_outlet_redemption_customer_brief")
    redeemed_user_acct = None
    with db_client.context():
        custome_redemption     = CustomerRedemption.get_by_transaction_id(transaction_id)
        if custome_redemption:
            redeemed_user_acct  = custome_redemption.redeemed_customer_acct
            if redeemed_user_acct:
                dict_properties  = ['name', 'reference_code','customer_key']
                redeemed_user_acct = redeemed_user_acct.to_dict(dict_properties=dict_properties)
        
        
    
    if redeemed_user_acct:
        logger.debug('redeemed_user_acct=%s', redeemed_user_acct)
        return jsonify(redeemed_user_acct)
        
    else:
        return create_api_message(status_code=StatusCode.BAD_REQUEST)    

@model_transactional(desc="revert_outlet_customer_transaction")
def __revert_customer_transaction(customer_transction, reverted_by, reverted_datetime):     
    return revert_transaction(customer_transction, reverted_by, reverted_datetime=reverted_datetime)

@model_transactional(desc="revert_outlet_sales_transaction")
def __revert_sales_transaction(sales_transction, reverted_by, reverted_datetime):     
    return revert_sales_transaction(sales_transction, reverted_by, reverted_datetime=reverted_datetime)
    
@model_transactional(desc="revert_outlet_redemption")
def __revert_customer_redemption(customer_redemption, reverted_by, reverted_datetime=None):     
       
    return revert_redemption(customer_redemption, reverted_by, reverted_datetime=reverted_datetime)
