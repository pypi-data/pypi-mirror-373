'''
Created on 29 Nov 2023

@author: jacklok
'''
from flask import Blueprint
import logging
from trexmodel.utils.model.model_util import create_db_client
from datetime import datetime
from trexlib.utils.string_util import is_not_empty
from trexmodel.models.datastore.user_models import User
from trexmodel.models.datastore.merchant_models import MerchantAcct, Outlet
from trexapi.utils.api_helpers import StatusCode,\
    create_api_message
from trexapi.decorators.api_decorators import user_auth_token_required,\
    user_auth_token_required_pass_reference_code
from flask.json import jsonify
from trexmodel.models.datastore.rating_models import OutletRating,\
    OutletRatingResult, MerchantRatingResult, TransactionRating
from trexlib.libs.flask_wtf.request_wrapper import request_values
from trexmodel.models.datastore.transaction_models import CustomerTransaction

rating_api_bp = Blueprint('rating_api_bp', __name__,
                                 template_folder='templates',
                                 static_folder='static',
                                 url_prefix='/api/v1/rating')

#logger = logging.getLogger('api')
logger = logging.getLogger('target_debug')

@rating_api_bp.route('/outlet/<outlet_key>/review', methods=['POST'])
@user_auth_token_required_pass_reference_code
@request_values
def give_outlet_rating(request_values, reference_code, outlet_key):
    logger.debug('---give_outlet_rating---')
    
    service_rating              = request_values.get('service_rating')
    ambience_rating             = request_values.get('ambience_rating')
    food_rating                 = request_values.get('food_rating')
    value_rating                = request_values.get('value_rating')
    
    
    db_client = create_db_client(caller_info="give_outlet_rating")
    
    logger.debug('give_outlet_rating: user account by reference code=%s', reference_code)
    logger.debug('give_outlet_rating: outlet_key=%s', outlet_key)
    
    with db_client.context():
        user_acct       = User.get_by_reference_code(reference_code)
        outlet          = Outlet.fetch(outlet_key)
        merchant_acct   = outlet.merchant_acct_entity
    
    if user_acct and outlet:
        with db_client.context():
            OutletRating.create(user_acct, outlet, 
                                    merchant_acct   = merchant_acct,
                                    service_rating  = service_rating, 
                                    ambience_rating = ambience_rating, 
                                    food_rating     = food_rating, 
                                    value_rating    = value_rating,
                                    )
            MerchantRatingResult.update(merchant_acct)
        
        return create_api_message(status_code=StatusCode.OK)
    else:
        return create_api_message(status_code=StatusCode.BAD_REQUEST)
    
  

@rating_api_bp.route('/outlet/<outlet_key>/review', methods=['GET'])
def read_outlet_rating(outlet_key):   
    logger.debug('give_outlet_rating: outlet_key=%s', outlet_key)
    
    db_client = create_db_client(caller_info="read_outlet_rating")
    
    with db_client.context():
        outlet                  = Outlet.fetch(outlet_key) 
        merchant_acct           = outlet.merchant_acct_entity
        outlet_rating_result    = OutletRatingResult.get_by_outlet(outlet)
        industry                = merchant_acct.industry
    
    
    if outlet_rating_result:
        result = {
                'industry'              : industry,
                'rating_result'         :{
                                        'score'                 : outlet_rating_result.score,
                                        'total_rating_count'    : outlet_rating_result.total_rating_count,
                                        'reviews_details'       : outlet_rating_result.rating_result,
                                        }
            }
    else:
        result = {
                'industry'              : industry,
                'rating_result'         : {
                                            'score'                 : outlet_rating_result.score,
                                            'total_rating_count'    : outlet_rating_result.total_rating_count,
                                            'reviews_details'       : outlet_rating_result.rating_result,
                    }
                
            }
    logger.debug('result=%s', result)    
    #return create_api_message(status_code=StatusCode.OK, result = result)
    return jsonify(result)
    
@rating_api_bp.route('/merchant/<merchant_acct_key>/review', methods=['GET'])
def read_merchant_rating(merchant_acct_key):   
    logger.debug('read_merchant_rating: merchant_acct_key=%s', merchant_acct_key)
    
    db_client = create_db_client(caller_info="read_merchant_rating")
    
    with db_client.context():
        merchant_acct           = MerchantAcct.fetch(merchant_acct_key)
        industry                = merchant_acct.industry 
        merchant_rating_result  = MerchantRatingResult.get_by_merchant_acct(merchant_acct)
    
    
    if merchant_rating_result:
        result = {
                'industry'              : industry,
                'rating_result'         :{
                                        'score'                 : merchant_rating_result.score,
                                        'total_rating_count'    : merchant_rating_result.total_rating_count,
                                        'reviews_details'       : merchant_rating_result.rating_result,
                                        }
            }
    else:
        result = {
                'industry'              : industry,
                'rating_result'         : {
                                            'score'                 : merchant_rating_result.score,
                                            'total_rating_count'    : merchant_rating_result.total_rating_count,
                                            'reviews_details'       : merchant_rating_result.rating_result,
                    }
                
            }
        
    logger.debug('result=%s', result)    
    
    #return create_api_message(status_code=StatusCode.OK, result = result)
    return jsonify(result)
        
    
@rating_api_bp.route('/outlet/<outlet_key>/update', methods=['POST'])
@user_auth_token_required
@request_values
def update_outlet_rating(request_values, outlet_key):   
    logger.debug('update_outlet_rating: outlet_key=%s', outlet_key)
    updated_datetime_from       = request_values.get('updated_datetime_from')
    
    db_client = create_db_client(caller_info="update_outlet_rating")
    
    if is_not_empty(updated_datetime_from):
        updated_datetime_from = datetime.strptime(updated_datetime_from, '%d-%m-%Y %H:%M')
    
    with db_client.context():
        outlet      = Outlet.fetch(outlet_key) 
        OutletRatingResult.update(outlet, updated_datetime_from)
    
    
    return create_api_message(triggered_datetime=datetime.now(), status_code=StatusCode.OK)

@rating_api_bp.route('/transaction-id/<transaction_id>/review', methods=['POST'])
@user_auth_token_required_pass_reference_code
@request_values
def give_transaction_rating(request_values, reference_code, transaction_id):
    logger.debug('---give_transaction_rating---')
    
    rating_result              = request_values.get('rating_result')
    remarks                    = rating_result.get('remarks','')
    
    if 'remarks' in rating_result:
        del rating_result['remarks']
    
    db_client = create_db_client(caller_info="give_outlet_rating")
    
    logger.debug('give_transaction_rating: user account by reference code=%s', reference_code)
    logger.debug('give_transaction_rating: transaction_id=%s', transaction_id)
    logger.debug('give_transaction_rating: remarks=%s', remarks)
    logger.debug('give_transaction_rating: rating_result=%s', rating_result)
    
    with db_client.context():
        user_acct       = User.get_by_reference_code(reference_code)
        
    
    if user_acct and transaction_id:
        
        with db_client.context():
            TransactionRating.create(user_acct, transaction_id, 
                                rating_result   = rating_result, 
                                remarks         = remarks,
                                for_testing     = False,
                                rating_datetime = datetime.utcnow(),
                                )
            
        
        return create_api_message(status_code=StatusCode.OK)
    else:
        return create_api_message(status_code=StatusCode.BAD_REQUEST)  
    
@rating_api_bp.route('/transaction-id/<transaction_id>/review', methods=['GET'])
@user_auth_token_required_pass_reference_code
def read_transaction_rating(reference_code, transaction_id):
    logger.debug('---read_transaction_rating---')
    
    db_client = create_db_client(caller_info="read_transaction_rating")
    
    logger.debug('read_transaction_rating: user account by reference code=%s', reference_code)
    logger.debug('read_transaction_rating: transaction_id=%s', transaction_id)
    
    
    transaction_review_json = {}
    if transaction_id:
        with db_client.context():
            transaction_review = TransactionRating.get_by_transaction_id(transaction_id)
            logger.debug('read_transaction_rating: transaction_review=%s', transaction_review)
            if transaction_review:
                transaction_review_json = transaction_review.to_dict()
                transaction_review_json['rating_result']['remarks'] = transaction_review_json['remarks']
            else:
                customer_transaction = CustomerTransaction.get_by_transaction_id(transaction_id)
                if customer_transaction:
                    transaction_review_json['industry'] = customer_transaction.industry
                    
                    
        #return create_api_message(status_code=StatusCode.OK, transaction_review=transaction_review_json)
        logger.debug('transaction_review_json=%s', transaction_review_json)
        return jsonify(transaction_review_json)
    else:
        return create_api_message(status_code=StatusCode.BAD_REQUEST)      


@rating_api_bp.route('/merchant/<merchant_acct_key>/update', methods=['POST'])
@request_values
def update_merchant_rating(request_values, merchant_acct_key):   
    logger.debug('update_merchant_rating: merchant_acct_key=%s', merchant_acct_key)
    updated_datetime_from       = request_values.get('updated_datetime_from')
    
    db_client = create_db_client(caller_info="update_merchant_rating")
    
    if is_not_empty(updated_datetime_from):
        updated_datetime_from = datetime.strptime(updated_datetime_from, '%d-%m-%Y %H:%M')
    
    with db_client.context():
        merchant_acct      = MerchantAcct.fetch(merchant_acct_key) 
        MerchantRatingResult.update(merchant_acct, updated_datetime_from)
    
    
    return create_api_message(triggered_datetime=datetime.now(), status_code=StatusCode.OK)    
    
