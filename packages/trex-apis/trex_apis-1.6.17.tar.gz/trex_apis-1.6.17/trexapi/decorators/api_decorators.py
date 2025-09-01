'''
Created on 1 Jul 2021

@author: jacklok
'''
from functools import wraps
from flask import request, session, abort
from trexlib.utils.string_util import is_not_empty
from trexlib.utils.crypto_util import decrypt_json
import logging
from datetime import datetime
from trexlib.utils.log_util import get_tracelog
from trexmodel.models.datastore.loyalty_models import LoyaltyDeviceSetting
from trexmodel.models.datastore.pos_models import POSSetting
from trexmodel.utils.model.model_util import create_db_client
from trexmodel.models.datastore.user_models import User
from trexapi.conf import API_ERR_CODE_INVALID_SESSION,\
    API_ERR_CODE_EXPIRED_SESSION, API_ERR_CODE_DUPLICATED_SESSION
from trexapi.utils.api_helpers import create_api_message, StatusCode

#logger = logging.getLogger('decorator')
logger = logging.getLogger('target_debug')

def test_session_expired(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return ("Authenticated token is expired", 401)
    
    return decorated_function

def auth_token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_token  = request.headers.get('x-auth-token')
        acct_id     = request.headers.get('x-acct-id')
            
        logger.debug('auth_token=%s', auth_token)
        logger.debug('acct_id=%s', acct_id)
        
        if is_not_empty(auth_token):
            try:
                auth_details_json = decrypt_json(auth_token)
                  
            except:
                logger.error('Authenticated token is not valid')
                return ("Authenticated token is not valid", 401)
            
            logger.debug('auth_details_json=%s', auth_details_json)
            
            if auth_details_json:
                expiry_datetime     = auth_details_json.get('expiry_datetime')
                acct_id_from_token  = auth_details_json.get('acct_id')
                
                logger.debug('acct_id from decrypted token=%s', acct_id_from_token)
                logger.debug('expiry_datetime from decrypted token=%s', expiry_datetime)
                
                if is_not_empty(expiry_datetime) and is_not_empty(acct_id_from_token) and acct_id==acct_id_from_token:
                    expiry_datetime = datetime.strptime(expiry_datetime, '%d-%m-%Y %H:%M:%S')
                    logger.debug('expiry_datetime=%s', expiry_datetime)
                    
                    now             = datetime.now()
                    if now < expiry_datetime: 
                        logger.debug('auth token is still valid')
                        return f(*args, **kwargs)
                    else:
                        logger.debug('auth token is not logger valid')
                        
                        return create_api_message('Authenticated token is expired', status_code=StatusCode.UNAUTHORIZED,)
                else:
                    return create_api_message('Authenticated token is invalid', status_code=StatusCode.UNAUTHORIZED,)
        
        return create_api_message('Authenticated token is required', status_code=StatusCode.UNAUTHORIZED,)

    return decorated_function

def show_request_info(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logger.info('----------------------------->>>>> request url=%s, method=%s, function=%s', request.url, request.method, f.__name__)
        return f(*args, **kwargs)
    
    return decorated_function

      
def user_auth_token_required_and_check_duplicated_session(check_duplicated_session=True):
    
    def decorator(f):
        return _user_auth_token_required_decorated_function(f, check_duplicated_session=check_duplicated_session, pass_reference_code=True)
        '''
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_auth_token     = request.headers.get('x-auth-token')
            user_reference_code = request.headers.get('x-reference-code')
            
            logger.debug('user_auth_token=%s', user_auth_token)
            logger.debug('user_reference_code=%s', user_reference_code)
            logger.debug('check_duplicated_session=%s', check_duplicated_session)
            
            logger.debug('args=%s', args)
            logger.debug('kwargs=%s', kwargs)
            
            if is_not_empty(user_auth_token):
                logger.debug('user_auth_token is not empty, going to decrypt it')
                try:
                    auth_details_json   = decrypt_json(user_auth_token)
                    logger.debug('auth_details_json=%s', auth_details_json)
                    
                except:
                    logger.error('Failed due to %s', get_tracelog())
                    return create_api_message('Authenticated token is not valid', status_code=StatusCode.UNAUTHORIZED,)
                
                
                
                if auth_details_json:
                    expiry_datetime                 = auth_details_json.get('expiry_datetime')
                    user_reference_code_from_token  = auth_details_json.get('reference_code')
                    decrypted_device_id             = auth_details_json.get('device_id')
                    
                    
                    if is_not_empty(expiry_datetime) and is_not_empty(user_reference_code_from_token) and user_reference_code_from_token == user_reference_code:
                        
                        expiry_datetime = datetime.strptime(expiry_datetime, '%d-%m-%Y %H:%M:%S')
                        logger.debug('expiry_datetime=%s', expiry_datetime)
                        
                        now             = datetime.now()
                        if now < expiry_datetime: 
                            logger.debug('auth token is still valid')
                            logger.debug('new args=%s', (user_reference_code, *args))
                            logger.debug('new kwargs=%s', kwargs)
                            
                            
                            db_client = create_db_client(caller_info="user_auth_token_required_and_check_duplicated_session")
                            
                            
                            with db_client.context():
                                user_acct           = User.get_by_reference_code(user_reference_code_from_token)
                                signin_device_id    = user_acct.signin_device_id
                            
                            if decrypted_device_id==signin_device_id:
                            
                                return f(*(user_reference_code, *args), **kwargs)
                            else:
                                logger.debug('auth token is not logger valid, due to request device id is not same as latest device id')
                            
                                return create_api_message('Authenticated token is not longer valid', status_code=StatusCode.UNAUTHORIZED, error_code=API_ERR_CODE_DUPLICATED_SESSION)
                            
                            
                            
                        else:
                            logger.debug('auth token is not logger valid')
                            
                            #return ("Authenticated token is expired", 401)
                            return create_api_message('Authenticated token is expired', status_code=StatusCode.UNAUTHORIZED, error_code=API_ERR_CODE_EXPIRED_SESSION)
                else:
                    #return ("Authenticated token is invalid", 401)    
                    return create_api_message('Authenticated token is invalid', status_code=StatusCode.UNAUTHORIZED, error_code=API_ERR_CODE_INVALID_SESSION)
            
            #return ("Authenticated token is required", 401)
            return create_api_message('Authenticated token is required', status_code=StatusCode.UNAUTHORIZED, )
            
        return decorated_function
        '''
    return decorator
    
def _user_auth_token_required_decorated_function(f, check_duplicated_session=False, pass_reference_code=False):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_auth_token     = request.headers.get('x-auth-token')
        user_reference_code = request.headers.get('x-reference-code')
        
        
        logger.debug('user_auth_token=%s', user_auth_token)
        logger.debug('user_reference_code=%s', user_reference_code)
        logger.debug('check_duplicated_session=%s', check_duplicated_session)
        
        if pass_reference_code:
            kwargs['reference_code'] = user_reference_code
        
        logger.debug('args=%s', args)
        logger.debug('kwargs=%s', kwargs)
        
        
        
        if is_not_empty(user_auth_token):
            logger.debug('user_auth_token is not empty, going to decrypt it')
            try:
                auth_details_json   = decrypt_json(user_auth_token)
                logger.debug('auth_details_json=%s', auth_details_json)
                
            except:
                logger.error('Failed due to %s', get_tracelog())
                return create_api_message('Authenticated token is not valid', status_code=StatusCode.UNAUTHORIZED,)
            
            
            
            if auth_details_json:
                expiry_datetime                 = auth_details_json.get('expiry_datetime')
                user_reference_code_from_token  = auth_details_json.get('reference_code')
                decrypted_device_id             = auth_details_json.get('device_id')
                
                
                if is_not_empty(expiry_datetime) and is_not_empty(user_reference_code_from_token) and user_reference_code_from_token == user_reference_code:
                    
                    expiry_datetime = datetime.strptime(expiry_datetime, '%d-%m-%Y %H:%M:%S')
                    logger.debug('expiry_datetime=%s', expiry_datetime)
                    
                    now             = datetime.now()
                    if now < expiry_datetime: 
                        logger.debug('auth token is still valid')
                        logger.debug('new args=%s', (user_reference_code, *args))
                        logger.debug('new kwargs=%s', kwargs)
                        
                        
                        
                        if check_duplicated_session:
                            db_client = create_db_client(caller_info="user_auth_token_required")
                            
                            
                            with db_client.context():
                                user_acct           = User.get_by_reference_code(user_reference_code_from_token)
                                signin_device_id    = user_acct.signin_device_id
                            
                            if decrypted_device_id==signin_device_id:
                            
                                return f(*args, **kwargs)
                                #return f(*(user_reference_code, *args), **kwargs)
                                #return f(user_reference_code, *args, **kwargs)
                            else:
                                logger.debug('auth token is not logger valid, due to request device id is not same as latest device id')
                            
                                return create_api_message('Authenticated token is not longer valid', status_code=StatusCode.UNAUTHORIZED, error_code=API_ERR_CODE_DUPLICATED_SESSION)
                        
                        else:
                            #return f(*(user_reference_code, *args), **kwargs)
                            #return f(user_reference_code, *args, **kwargs)
                            return f(*args, **kwargs)
                        
                    else:
                        logger.debug('auth token is not logger valid')
                        
                        #return ("Authenticated token is expired", 401)
                        return create_api_message('Authenticated token is expired', status_code=StatusCode.UNAUTHORIZED, error_code=API_ERR_CODE_EXPIRED_SESSION)
            else:
                #return ("Authenticated token is invalid", 401)    
                return create_api_message('Authenticated token is invalid', status_code=StatusCode.UNAUTHORIZED, error_code=API_ERR_CODE_INVALID_SESSION)
        
        #return ("Authenticated token is required", 401)
        return create_api_message('Authenticated token is required', status_code=StatusCode.UNAUTHORIZED, )

    return decorated_function

def user_auth_token_required_pass_reference_code(f):
    logger.debug("Calling function: %s", f.__name__)
    return _user_auth_token_required_decorated_function(f, check_duplicated_session=False, pass_reference_code=True)

def user_auth_token_required(f):
    logger.debug("Calling function: %s", f.__name__)
    return _user_auth_token_required_decorated_function(f, check_duplicated_session=False, pass_reference_code=False)
    '''
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_auth_token     = request.headers.get('x-auth-token')
        user_reference_code = request.headers.get('x-reference-code')
        check_duplicated_session = False
        if kwargs:
            check_duplicated_session = kwargs.get('check_duplicated_session')
        
        logger.debug('user_auth_token=%s', user_auth_token)
        logger.debug('user_reference_code=%s', user_reference_code)
        logger.debug('check_duplicated_session=%s', check_duplicated_session)
        
        logger.debug('args=%s', args)
        logger.debug('kwargs=%s', kwargs)
        
        if is_not_empty(user_auth_token):
            logger.debug('user_auth_token is not empty, going to decrypt it')
            try:
                auth_details_json   = decrypt_json(user_auth_token)
                logger.debug('auth_details_json=%s', auth_details_json)
                
            except:
                logger.error('Failed due to %s', get_tracelog())
                return create_api_message('Authenticated token is not valid', status_code=StatusCode.UNAUTHORIZED,)
            
            
            
            if auth_details_json:
                expiry_datetime                 = auth_details_json.get('expiry_datetime')
                user_reference_code_from_token  = auth_details_json.get('reference_code')
                decrypted_device_id             = auth_details_json.get('device_id')
                
                
                if is_not_empty(expiry_datetime) and is_not_empty(user_reference_code_from_token) and user_reference_code_from_token == user_reference_code:
                    
                    expiry_datetime = datetime.strptime(expiry_datetime, '%d-%m-%Y %H:%M:%S')
                    logger.debug('expiry_datetime=%s', expiry_datetime)
                    
                    now             = datetime.now()
                    if now < expiry_datetime: 
                        logger.debug('auth token is still valid')
                        logger.debug('new args=%s', (user_reference_code, *args))
                        logger.debug('new kwargs=%s', kwargs)
                        
                        
                        
                        if check_duplicated_session:
                            db_client = create_db_client(caller_info="user_auth_token_required")
                            
                            
                            with db_client.context():
                                user_acct           = User.get_by_reference_code(user_reference_code_from_token)
                                signin_device_id    = user_acct.signin_device_id
                            
                            if decrypted_device_id==signin_device_id:
                            
                                return f(*(user_reference_code, *args), **kwargs)
                            else:
                                logger.debug('auth token is not logger valid, due to request device id is not same as latest device id')
                            
                                return create_api_message('Authenticated token is not longer valid', status_code=StatusCode.UNAUTHORIZED, error_code=API_ERR_CODE_DUPLICATED_SESSION)
                        
                        else:
                            return f(*(user_reference_code, *args), **kwargs)
                        
                    else:
                        logger.debug('auth token is not logger valid')
                        
                        #return ("Authenticated token is expired", 401)
                        return create_api_message('Authenticated token is expired', status_code=StatusCode.UNAUTHORIZED, error_code=API_ERR_CODE_EXPIRED_SESSION)
            else:
                #return ("Authenticated token is invalid", 401)    
                return create_api_message('Authenticated token is invalid', status_code=StatusCode.UNAUTHORIZED, error_code=API_ERR_CODE_INVALID_SESSION)
        
        #return ("Authenticated token is required", 401)
        return create_api_message('Authenticated token is required', status_code=StatusCode.UNAUTHORIZED, )
        '''
    return decorated_function

def verify_device(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_auth_token     = request.headers.get('x-auth-token')
        user_reference_code = request.headers.get('x-reference-code')
        
        logger.debug('user_auth_token=%s', user_auth_token)
        
        logger.debug('args=%s', args)
        logger.debug('kwargs=%s', kwargs)
        
        if is_not_empty(user_auth_token):
            logger.debug('user_auth_token is not empty, going to decrypt it')
            try:
                auth_details_json   = decrypt_json(user_auth_token)
                logger.debug('auth_details_json=%s', auth_details_json)
                
            except:
                logger.error('Failed due to %s', get_tracelog())
                return create_api_message('Authenticated token is not valid', status_code=StatusCode.UNAUTHORIZED,)
            
            
            
            if auth_details_json:
                expiry_datetime                 = auth_details_json.get('expiry_datetime')
                user_reference_code_from_token  = auth_details_json.get('reference_code')
                decrypted_device_id             = auth_details_json.get('device_id')
                
                if is_not_empty(expiry_datetime) and is_not_empty(user_reference_code_from_token) and user_reference_code_from_token == user_reference_code:
                    
                    expiry_datetime = datetime.strptime(expiry_datetime, '%d-%m-%Y %H:%M:%S')
                    logger.debug('expiry_datetime=%s', expiry_datetime)
                    
                    now             = datetime.now()
                    if now < expiry_datetime: 
                        logger.debug('auth token is still valid')
                        logger.debug('new args=%s', (user_reference_code, *args))
                        logger.debug('new kwargs=%s', kwargs)
                        
                        db_client = create_db_client(caller_info="user_auth_token_required_and_verify_device_token")
                        
                        with db_client.context():
                            user_acct           = User.get_by_reference_code(user_reference_code_from_token)
                            signin_device_id    = user_acct.signin_device_id
                        
                        if decrypted_device_id==signin_device_id:
                        
                            return f(**kwargs)
                        else:
                            logger.debug('auth token is not logger valid, due to ')
                        
                            return create_api_message('Authenticated token is not longer valid', status_code=StatusCode.UNAUTHORIZED,)
                        
                    else:
                        logger.debug('auth token is not logger valid')
                        
                        #return ("Authenticated token is expired", 401)
                        return create_api_message('Authenticated token is expired', status_code=StatusCode.UNAUTHORIZED,)
            else:
                #return ("Authenticated token is invalid", 401)    
                return create_api_message('Authenticated token is invalid', status_code=StatusCode.UNAUTHORIZED,)
        
        #return ("Authenticated token is required", 401)
        return create_api_message('Authenticated token is required', status_code=StatusCode.UNAUTHORIZED,)

    return decorated_function

def device_is_activated(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_token          = request.headers.get('x-auth-token')
        api_access          = False
        
        if is_not_empty(auth_token):
            try:
                auth_details_json = decrypt_json(auth_token)
                logger.debug('auth_details_json=%s', auth_details_json)
                api_access          = auth_details_json.get('api_access', False)
                
                
            except:
                logger.error('Authenticated token is not valid')
                return ("Authenticated token is not valid", 401)
        
        logger.debug('api_access=%s', api_access)
        
        if api_access:
            logger.info('this is api access, thus ignore device activation checking')
            return f(*args, **kwargs)
        else:
            activation_code     = request.headers.get('x-activation-code')
            device_id           = request.headers.get('x-device-id')
            device_type         = request.headers.get('x-device-type')
                
            logger.debug('activation_code=%s', activation_code)
            logger.debug('device_id=%s', device_id)
            logger.debug('device_type=%s', device_type)
            
            if is_not_empty(activation_code) and is_not_empty(device_id):
                device_settings = None
                try:
                    db_client = create_db_client(caller_info="device_is_activated")
                    if 'loyalty' == device_type:
                        with db_client.context():
                            device_settings = LoyaltyDeviceSetting.get_by_activation_code(activation_code)
                    elif 'pos' == device_type:
                        with db_client.context():
                            device_settings = POSSetting.get_by_activation_code(activation_code)
                    
                    if device_settings is not None:
                        if device_settings.testing:
                            logger.info('Activation device id is meant for testing thus, it can be by pass')
                        else:
                            if device_settings.device_id != device_id:
                                logger.info('Access device id is not same as activation device id')
                                return create_api_message('Device is not activated or it is deactivated already', status_code=StatusCode.BAD_REQUEST)
                            
                            logger.info('Access device id is authorized')
                        return f(*args, **kwargs)
                    
                    return create_api_message('Device is not activated or it is deactivated already', status_code=StatusCode.BAD_REQUEST)
                    
                except:
                    logger.error('failed due to %s ', get_tracelog())
                    #return ("Failed to check device authorization", 401)
                    return create_api_message('Failed to check device authorization', status_code=StatusCode.BAD_REQUEST)
                
        
            

    return decorated_function

def device_activated_is_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        activation_code     = request.headers.get('x-activation-code')
        device_id           = request.headers.get('x-device-id')
        device_type         = request.headers.get('x-device-type')
            
        logger.debug('activation_code=%s', activation_code)
        logger.debug('device_id=%s', device_id)
        logger.debug('device_type=%s', device_type)
        
        if is_not_empty(activation_code) and is_not_empty(device_id):
            device_settings = None
            try:
                db_client = create_db_client(caller_info="device_is_activated")
                if 'loyalty' == device_type:
                    with db_client.context():
                        device_settings = LoyaltyDeviceSetting.get_by_activation_code(activation_code)
                elif 'pos' == device_type:
                    with db_client.context():
                        device_settings = POSSetting.get_by_activation_code(activation_code)
                
                if device_settings is not None:
                    if device_settings.testing:
                        logger.info('Activation device id is meant for testing thus, it can be by pass')
                    else:
                        if device_settings.device_id != device_id:
                            logger.info('Access device id is not same as activation device id')
                            return create_api_message('Device is not activated or it is deactivated already', status_code=StatusCode.BAD_REQUEST)
                    
                    return f(*(activation_code, *args), *args, **kwargs)
                
                return create_api_message('Device is not activated or it is deactivated already', status_code=StatusCode.BAD_REQUEST)
                
            except:
                logger.error('failed due to %s ', get_tracelog())
                #return ("Failed to check device authorization", 401)
                return create_api_message('Failed to check device is activated', status_code=StatusCode.BAD_REQUEST)
            
        else:  
            return create_api_message('Missing activation code, or device type or device id', status_code=StatusCode.BAD_REQUEST)  

    return decorated_function

def outlet_key_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        outlet_key = request.headers.get('x-outlet-key')
            
        logger.debug('outlet_key=%s', outlet_key)
        
        if is_not_empty(outlet_key):
            logger.debug('Going to execute')
            return f(*args, **kwargs)
            
        
        #return ("Outlet Key is required", 401)
        return create_api_message('Missing outlet key', status_code=StatusCode.UNAUTHORIZED)

    return decorated_function

def merchant_key_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        acct_id = request.headers.get('x-acct-id')
            
        logger.debug('acct_id=%s', acct_id)
        
        if is_not_empty(acct_id):
            logger.debug('Going to execute')
            return f(*args, **kwargs)
            
        
        #return ("Merchant account id is required", 401)
        return create_api_message('Missing merchant account id', status_code=StatusCode.UNAUTHORIZED)

    return decorated_function

def customer_key_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        customer_key = request.headers.get('x-customer-key')
            
        logger.debug('customer_key=%s', customer_key)
        
        if is_not_empty(customer_key):
            logger.debug('Going to execute')
            return f(*args, customer_key, **kwargs)
            
        
        #return ("Outlet Key is required", 401)
        return create_api_message('Missing customer key', status_code=StatusCode.UNAUTHORIZED)

    return decorated_function

def elapsed_time_trace(debug=False, trace_key=None):
    def wrapper(fn):
        import time
        def elapsed_time_trace_wrapper(*args, **kwargs):
            start = time.time()
            result      = fn(*args, **kwargs)
            end = time.time()
            elapsed_time = end - start
            trace_name      = trace_key or fn.func_name
            first_argument  = args[0] if args else None
            logger.info('==================== Start Elapsed Time Trace %s(%s) ===========================', trace_name, first_argument)
            logger.info('elapsed time=%s', ("%.2gs" % (elapsed_time)))
            logger.info('================================================================================')
            return result

        return elapsed_time_trace_wrapper
    return wrapper