'''
Created on 8 Jul 2021

@author: jacklok
'''
from flask import request
import logging
from trexlib.utils.crypto_util import decrypt_json
from datetime import datetime, timedelta
from trexconf import conf as api_conf
from trexlib.utils.crypto_util import encrypt_json
import six
from six import string_types

logger = logging.getLogger('helper')


def get_logged_in_api_username():
    auth_token  = request.headers.get('x-auth-token')
    username    = None
    try:
        auth_details_json = decrypt_json(auth_token)
    except:
        logger.error('Failed to decrypt authenticated token')
        
    logger.debug('auth_details_json=%s', auth_details_json)
    
    if auth_details_json:
        username = auth_details_json.get('username')
        
    return username

def generate_user_auth_token(acct_id, reference_code, device_id):
    expiry_datetime = datetime.now() + timedelta(minutes = int(api_conf.API_TOKEN_EXPIRY_LENGTH_IN_MINUTE))
    
    logger.debug('expiry_datetime=%s', expiry_datetime)
    
    token_content =  {
                        'acct_id'           : acct_id,
                        'reference_code'    : reference_code,
                        'expiry_datetime'   : expiry_datetime.strftime('%d-%m-%Y %H:%M:%S'),
                        'device_id'         : device_id,
                        }
    
    logger.debug('token_content=%s', token_content)
    
    return token_content

def encrypt_user_auth_token(auth_token):
    logger.debug('auth_token=%s', auth_token)
    
    return encrypt_json(auth_token)

class StatusCode(object):
    OK                          = 200
    CREATED                     = 201
    ACCEPTED                    = 202
    NO_CONTENT                  = 204
    RESET_CONTENT               = 205
    BAD_REQUEST                 = 400
    UNAUTHORIZED                = 401
    FORBIDDEN                   = 403
    NOT_FOUND                   = 404
    METHOD_NOT_ALLOW            = 405
    PRECONDITION_FAILED         = 412
    RESOURCE_LOCKED             = 423
    INTERNAL_SERVER_ERROR       = 500
    SERVICE_NOT_AVAILABLE       = 503
    GATEWAY_TIMEOUT             = 504
    HTTP_VERSION_NOT_SUPPORT    = 505
    # add more status code according to your need

def create_api_message(message=None, status_code=StatusCode.BAD_REQUEST, **kwargs):
    
    request_content_type = request.headers.get('content-type')
    reply_message = {}
    logger.debug('create_api_message: request_content_type=%s', request_content_type)
    logger.debug('create_api_message: message=%s', message)
    
    if kwargs is not None:
        for key, value in six.iteritems(kwargs):
            reply_message[key] = value
        
    if message:
        if isinstance(message, string_types):
            reply_message['msg'] = [message]
        
        elif isinstance(message, (tuple, list)):
            reply_message['msg'] = message
            
        elif isinstance(message, dict):
            reply_message['msg'] = message['msg']    
    #else:
    #    reply_message['msg'] = []
    
    logger.debug('reply_message=%s', reply_message)
    
    return reply_message, status_code