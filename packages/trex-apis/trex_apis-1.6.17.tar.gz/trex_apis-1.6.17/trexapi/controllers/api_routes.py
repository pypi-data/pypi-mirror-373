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
from trexlib.utils.string_util import random_string
from datetime import datetime, timedelta
from trexconf import conf as api_conf
from trexlib.utils.crypto_util import encrypt_json
from trexlib.libs.flask_wtf.request_wrapper import session_value

#logger = logging.getLogger('api')
logger = logging.getLogger('target_debug')

auth = HTTPBasicAuth()
#auth = HTTPBasicAuthWrapper()


api_bp = Blueprint('api_base_bp', __name__,
                                 template_folder='templates',
                                 static_folder='static',
                                 url_prefix='/api/v1')

api = Api(api_bp)


@auth.verify_password
def verify_user_auth(username, password):
    if not (username and password):
        return False
    
    db_client   = create_db_client(caller_info="verify_user_auth")
    valid_auth  = False
    
    logger.debug('username=%s', username)
    logger.debug('password=%s', password)
    
    with db_client.context():
        merchant_user = MerchantUser.get_by_username(username)
        
        logger.debug('merchant_user=%s', merchant_user)
        
        if merchant_user:
            
            md5_hashed_password = hashlib.md5(password.encode('utf-8')).hexdigest()
            
            logger.debug('verify_user_auth: username=%s', username)
            logger.debug('verify_user_auth: password=%s', password)
            logger.debug('verify_user_auth: md5_hashed_password=%s', md5_hashed_password)
            
            if merchant_user.is_valid_password(md5_hashed_password):
                valid_auth = True
            else:
                logger.warn('Invalid merchant password')
        else:
            logger.warn('Invalid merchant username=%s', username)    
        
    return valid_auth

def __generate_random():
    return hashlib.md5(str(random_string(6)).encode('utf-8')).hexdigest()

def default_generate_nonce():
    session["auth_nonce"] = __generate_random()
    return session["auth_nonce"]
 
@session_value
def default_verify_nonce(session_value, nonce):
    return nonce == session_value.get("auth_nonce")

def default_generate_opaque():
    session["auth_opaque"] = __generate_random()
    return session["auth_opaque"]

@session_value
def default_verify_opaque(session_value, opaque):
    return opaque == session_value.get("auth_opaque")
    
class APIBaseResource(Resource):
    @property
    def realm(self):
        return 'base'
    
    def generate_ha1(self, username, password):
        
        a1 = username + ":" + self.realm + ":" + password
        a1 = a1.encode('utf-8')
        return hashlib.md5(a1).hexdigest()
        
    
    def generate_token(self, acct_id, username, api_access=False):
        expiry_datetime = datetime.now() + timedelta(minutes = int(api_conf.API_TOKEN_EXPIRY_LENGTH_IN_MINUTE))
        
        logger.debug('expiry_datetime=%s', expiry_datetime)
        
        token_content =  {
                            'acct_id'           : acct_id,
                            'username'          : username,
                            'expiry_datetime'   : expiry_datetime.strftime('%d-%m-%Y %H:%M:%S'),
                            'api_access'        : api_access,
                            }
        
        logger.debug('token_content=%s', token_content)
        
        return (expiry_datetime, encrypt_json(token_content))
    
    
class APIVersionResource(APIBaseResource):
    
    @auth.login_required
    def get(self):
        output_json =  {
                        'version'   :   api_conf.API_VERSION,
                        'username'  :   auth.current_user()
                        }
        
        return output_json
    
class APIResource(APIBaseResource):
    
    def get(self):
        return api_conf.API_VERSION    

'''
class SecureAPIResource(AuthenticateAPIResource):  
    
    def __init__(self):
        super(SecureAPIResource, self).__init__()  
    
    
class CheckAuthTokenResource(SecureAPIResource):
    
    @auth_token_required
    def get(self):
        return 'Ping'             
'''    
     
api.add_resource(APIResource,                   '/')
api.add_resource(APIVersionResource,            '/version')
#api.add_resource(CheckAuthTokenResource,        '/auth-check')

        
        
        
        