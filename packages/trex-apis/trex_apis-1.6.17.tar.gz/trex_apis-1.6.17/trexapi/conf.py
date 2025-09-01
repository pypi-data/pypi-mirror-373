'''
Created on 30 Jun 2021

@author: jacklok
'''
import os
APPLICATION_NAME                                                = os.environ.get('APPLICATION_NAME')
MOBILE_APP_NAME                                                 = os.environ.get('MOBILE_APP_NAME')
APPLICATION_BASE_URL                                            = os.environ.get('APPLICATION_BASE_URL')
SECRET_KEY                                                      = os.environ.get('SECRET_KEY')
VERSION                                                         = '1.0.0'
UPDATED_DATE                                                    = '5 July 2021'

API_TOKEN_EXPIRY_LENGTH_IN_MINUTE                               = os.environ.get('API_TOKEN_EXPIRY_LENGTH_IN_MINUTE') 

API_ERR_CODE_INVALID_ACTIVATION_CODE                            = 'invalid.activation.code';
API_ERR_CODE_USED_ACTIVATION_CODE                               = 'used.activation.code';
API_ERR_CODE_INVALID_SESSION                                    = 'invalid.session';
API_ERR_CODE_EXPIRED_SESSION                                    = 'expired.session';
API_ERR_CODE_DUPLICATED_SESSION                                 = 'duplicated.session';

EARN_INSTANT_REWARD_URL                                         = os.environ.get('EARN_INSTANT_REWARD_URL')

LUCKY_DRAW_URL                                                  = os.environ.get('LUCKY_DRAW_URL')

FIREBASE_SERVICE_ACCOUNT_KEY_PATH                               = os.environ.get('FIREBASE_SERVICE_ACCOUNT_KEY_PATH')

MOBILE_PHONE_EXPIRY_LENGTH_IN_MINUTE                            = os.environ.get('MOBILE_PHONE_EXPIRY_LENGTH_IN_MINUTE')
EMAIL_EXPIRY_LENGTH_IN_MINUTE                                   = os.environ.get('EMAIL_EXPIRY_LENGTH_IN_MINUTE')

USE_VERIFICATION_REQUEST_ID                                     = os.environ.get('USE_VERIFICATION_REQUEST_ID')

SEND_REAL_MESSAGE                                               = os.environ.get('SEND_REAL_MESSAGE')

REFER_BASE_URL                                                  = os.environ.get('REFER_BASE_URL')


