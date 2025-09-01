'''
Created on 30 Jun 2021

@author: jacklok
'''

from flask import Blueprint, session 
from flask_restful import Resource, abort
import logging
from flask_httpauth import HTTPBasicAuth
from flask_restful import Api
from trexmodel.utils.model.model_util import create_db_client
from trexmodel.models.datastore.merchant_models import MerchantUser
import hashlib
from trexlib.utils.string_util import random_string, is_not_empty
from datetime import datetime, timedelta
from trexconf import conf as api_conf
from trexlib.utils.crypto_util import encrypt_json
from trexlib.libs.flask_wtf.request_wrapper import session_value, request_values,\
    request_headers
from trexmodel.models.datastore.loyalty_models import LoyaltyDeviceSetting
from trexapi.utils.push_notification_helper import create_push_notification
from trexweb.libs.http import create_rest_message
from trexapi.utils.api_helpers import StatusCode
from trexconf.conf import DEFAULT_LANGUAGE

logger = logging.getLogger('api')
#logger = logging.getLogger('debug')



device_util_bp = Blueprint('device_util_bp', __name__,
                                 template_folder='templates',
                                 static_folder='static',
                                 url_prefix='/api/v1/device-util')


@device_util_bp.route('/test-push-notification', methods=['post'])
@device_util_bp.route('/test-terminal-push-notification', methods=['post'])
@request_headers
@request_values
def test_push_notification(request_headers, request_values):
    title               = request_values.get('title')
    message             = request_values.get('message')
    language_code       = request_values.get('languageCode', DEFAULT_LANGUAGE)
    device_type         = request_values.get('device_type')
    platform            = request_headers.get('x-platform')
    activation_code     = request_values.get('activation_code')
    
    logger.info('platform=%s', platform)
    logger.info('activation_code=%s', activation_code)
    logger.info('title=%s', title)
    logger.info('message=%s', message)
    logger.info('device_type=%s', device_type)
    logger.info('language_code=%s', language_code)
    
    if is_not_empty(activation_code) and is_not_empty(device_type) and is_not_empty(title) and is_not_empty(message) and is_not_empty(platform):
        db_client = create_db_client(caller_info="test_push_notification")
        with db_client.context():
            if device_type=='loyalty':
                device_setting = LoyaltyDeviceSetting.get_by_activation_code(activation_code)
        
        if device_setting:
            logger.debug('Found device setting')
            logger.info('device_setting.device_details=%s', device_setting.device_details)
            device_details_by_platform = device_setting.device_details.get(platform)
            if is_not_empty(device_details_by_platform):
                device_token = device_details_by_platform.get('device_token')
                logger.info('device_token=%s', device_token)
                if is_not_empty(device_token):
                    create_push_notification(
                                title_data      = title, 
                                message_data    = message,
                                speech          = message,
                                device_token    = device_token,
                                language_code   = language_code,
                                
                            )
                else:
                    logger.debug('Device token is empty')
            else:
                logger.debug('Device details is empty')
        
    return create_rest_message(status_code=StatusCode.OK) 

@device_util_bp.route('/test-device-push-notification', methods=['post'])
@request_values
def test_device_push_notification(request_values):
    
    title               = request_values.get('title')
    message             = request_values.get('message')
    language_code       = request_values.get('languageCode', DEFAULT_LANGUAGE)
    device_token        = request_values.get('device_token')
    
    logger.info('device_token=%s', device_token)
    logger.info('title=%s', title)
    logger.info('message=%s', message)
    logger.info('language_code=%s', language_code)
    
    if is_not_empty(device_token) and is_not_empty(language_code) and is_not_empty(title) and is_not_empty(message):
        create_push_notification(
                                title_data      = title, 
                                message_data    = message,
                                speech          = message,
                                device_token    = device_token,
                                language_code   = language_code,
                                
                            )
        
    return create_rest_message(status_code=StatusCode.OK) 
    

        
        
        
        