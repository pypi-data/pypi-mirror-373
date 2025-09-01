'''
Created on 5 Jul 2021

@author: jacklok
'''
from flask_httpauth import HTTPBasicAuth
from flask import request, session, abort
import logging
from functools import wraps
from trexlib.utils.string_util import is_not_empty
from trexmodel.models.datastore.merchant_models import MerchantAcct,\
    MerchantUser


logger = logging.getLogger('debug')

class HTTPBasicAuthWrapper(HTTPBasicAuth):
    def login_required(self, f=None, role=None, optional=None):
        
        auth        = self.get_auth()
        username    = auth.username
        
        api_key     = request.headers.get('x-api-key')
        
        logger.debug('auth=%s', auth)
        logger.debug('api_key=%s', api_key)
        
        if is_not_empty(api_key):
            
            merchant_acct   = MerchantAcct.get_by_api_key(api_key)
            merchant_user   = MerchantUser.get_by_username(username) 
            if merchant_user.merchant_acct_key == merchant_acct.key_in_str:
            
                return super(self).login_required(f, role=role, optional=optional)
            else:
                abort(401)
        else:
            abort(401)
