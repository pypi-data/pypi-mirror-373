'''
Created on 24 Jan 2024

@author: jacklok
'''

from flask import Blueprint, request
import logging
from trexmodel.utils.model.model_util import create_db_client
from datetime import datetime
from trexlib.utils.string_util import is_not_empty
from trexapi.utils.api_helpers import StatusCode,\
    create_api_message
from trexapi.decorators.api_decorators import user_auth_token_required,\
    user_auth_token_required_pass_reference_code
from trexmodel.models.datastore.prepaid_models import PrepaidRedeemSettings
from trexmodel.models.datastore.customer_models import Customer
from flask_babel import gettext
from trexmodel.models.datastore.helper.reward_transaction_helper import prepaid_payment_transaction
from trexmodel import program_conf
from trexlib.utils.crypto_util import decrypt
from trexmodel.models.datastore.loyalty_models import LoyaltyDeviceSetting
from trexapi.utils.push_notification_helper import create_prepaid_push_notification
from trexlib.utils.log_util import get_tracelog

prepaid_api_bp = Blueprint('prepaid_api_bp', __name__,
                                 template_folder='templates',
                                 static_folder='static',
                                 url_prefix='/api/v1/prepaid')

logger = logging.getLogger('api')

@prepaid_api_bp.route('/redeem/<redeem_code>', methods=['GET'])
@user_auth_token_required_pass_reference_code
def prepaid_redeem_get(reference_code, redeem_code):
    logger.debug('---prepaid_redeem_get---')
    
    db_client = create_db_client(caller_info="prepaid_redeem_get")
    
    logger.debug('prepaid_redeem: redeem_code=%s', redeem_code)
    
    redeem_outlet_details = {}
    if is_not_empty(redeem_code):
        decrypt_redeem_code = decrypt(redeem_code)
        
        logger.debug('prepaid_redeem: decrypt_redeem_code=%s', decrypt_redeem_code)
        
        with db_client.context():
            prepaid_redeem_settings = PrepaidRedeemSettings.get_by_redeem_code(decrypt_redeem_code)
            
        if prepaid_redeem_settings:
            with db_client.context():
                outlet          = prepaid_redeem_settings.assigned_outlet_entity
                merchant_acct   = outlet.merchant_acct_entity
                customer        = Customer.get_by_reference_code(reference_code, merchant_acct)
                
            
            if outlet:
                prepaid_amount = .0
                if customer and is_not_empty(customer.prepaid_summary):
                    prepaid_amount = customer.prepaid_summary.get('amount')
                    
                redeem_outlet_details = {
                                        'outlet_key'        : outlet.key_in_str,
                                        'outlet_name'       : outlet.name,
                                        'redeem_code'       : decrypt_redeem_code,
                                        'redeem_code_label' : prepaid_redeem_settings.label,
                                        'device_type'       : prepaid_redeem_settings.device_type,
                                        'locale'            : merchant_acct.locale,
                                        'currency'          : merchant_acct.currency_code,
                                        'prepaid_amount'    : prepaid_amount,
                                        
                                        }
        
            
                #return create_api_message(redeem_outlet_details=redeem_outlet_details, status_code=StatusCode.BAD_REQUEST)
                
                logger.debug('redeem_outlet_details=%s', redeem_outlet_details)
                return redeem_outlet_details
            else:
                return create_api_message(gettext('Missing configured outlet'), status_code=StatusCode.BAD_REQUEST)
        
            
        else:
            return create_api_message(gettext('Invalid redeem code'), status_code=StatusCode.BAD_REQUEST)
    else:
        return create_api_message(gettext('Missing redeem code'), status_code=StatusCode.BAD_REQUEST)
    

@prepaid_api_bp.route('/redeem', methods=['POST'])
@user_auth_token_required_pass_reference_code
def prepaid_redeem_post(reference_code):
    logger.debug('---prepaid_redeem_post---')
    redeem_in_json      = request.get_json()
    redeem_code         = redeem_in_json.get('redeem_code')
    redeem_amount       = redeem_in_json.get('redeem_amount')
    remarks             = redeem_in_json.get('remarks')
    
    
    db_client = create_db_client(caller_info="prepaid_redeem")
    
    logger.debug('prepaid_redeem: user account by reference code=%s', reference_code)
    logger.debug('prepaid_redeem: redeem_code=%s', redeem_code)
    logger.debug('prepaid_redeem: redeem_amount=%s', redeem_amount)
    logger.debug('prepaid_redeem: remarks=%s', remarks)
    
    is_insufficient_amount  = False
    target_device           = None
    
    with db_client.context():
        prepaid_redeem_settings = PrepaidRedeemSettings.get_by_redeem_code(redeem_code)
        
    if prepaid_redeem_settings:
        
        with db_client.context():
            device_activation_code = prepaid_redeem_settings.device_activation_code
            
            if is_not_empty(device_activation_code) and prepaid_redeem_settings.is_loyalty_device:
                target_device = LoyaltyDeviceSetting.get_by_activation_code(device_activation_code)
             
            merchant_acct   = prepaid_redeem_settings.merchant_acct_entity
            outlet          = prepaid_redeem_settings.assigned_outlet_entity
            customer_acct   = Customer.get_by_reference_code(reference_code, merchant_acct)
            
            prepaid_summary = customer_acct.prepaid_summary
            
            
            if prepaid_summary.get('amount') < redeem_amount:
                is_insufficient_amount = True
                
            if is_insufficient_amount==False:
                redeemed_datetime = datetime.utcnow()
                redemption_details  = prepaid_payment_transaction(customer_acct, 
                                                                redeem_outlet               = outlet,
                                                                reward_format               = program_conf.REWARD_FORMAT_PREPAID,
                                                                reward_amount               = redeem_amount,
                                                                redeemed_datetime           = redeemed_datetime,
                                                                prepaid_redeem_code         = redeem_code,
                                                                remarks                     = remarks,
                                                                )
    
        if is_insufficient_amount==True:
            return create_api_message(gettext('Insufficient prepaid amount'), status_code=StatusCode.BAD_REQUEST)
        else:
            if redemption_details:
                
                if target_device is not None:
                    logger.debug('going to send push notification to device if it is configured')
                    for device_token in target_device.device_tokens_list:
                        try:
                            create_prepaid_push_notification(
                                title_data='Received Paid Prepaid', 
                                message_data = 'You have received %s prepaid' % redeem_amount,
                                speech = 'You have received %s prepaid' % redeem_amount,
                                device_token = device_token
                                
                            )
                        except:
                            logger.error('Failed to send push notification due to %s', get_tracelog())
                    
                return create_api_message(
                            transaction_id=redemption_details.transaction_id, 
                            redeemed_datetime=redeemed_datetime.strftime('%d-%m-%Y %H:%M:%S'),
                            status_code=StatusCode.OK)
            else:
                return create_api_message(gettext('Fail to redeem prepaid'), status_code=StatusCode.BAD_REQUEST)
    else:
        return create_api_message(gettext('Invalid redeem code'), status_code=StatusCode.BAD_REQUEST)
        
        
            