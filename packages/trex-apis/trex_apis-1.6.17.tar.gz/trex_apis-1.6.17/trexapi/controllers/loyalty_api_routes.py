'''
Created on 28 Oct 2021

@author: jacklok
'''

from flask import Blueprint, request, url_for
import logging
from trexapi.decorators.api_decorators import device_activated_is_required
from trexlib.utils.string_util import is_not_empty
from trexapi.utils.api_helpers import StatusCode, create_api_message
from trexmodel.models.datastore.loyalty_models import LoyaltyDeviceSetting
from trexmodel.utils.model.model_util import create_db_client
from trexmodel.models import merchant_helpers
from trexapi.conf import API_ERR_CODE_INVALID_ACTIVATION_CODE,\
    API_ERR_CODE_USED_ACTIVATION_CODE
from trexconf import conf
from trexlib.libs.flask_wtf.request_wrapper import request_headers, request_args,\
    request_values
from trexlib.utils.log_util import get_tracelog


logger = logging.getLogger('api')
#logger = logging.getLogger('debug')

loyalty_api_bp = Blueprint('loyalty_api_bp', __name__,
                                 template_folder='templates',
                                 static_folder='static',
                                 url_prefix='/api/v1/program')

@loyalty_api_bp.route('/check-activation', methods=['POST'])
@request_args
def check_activation(request_args):
    
    #activation_code = request.args.get('activation_code') or request.form.get('activation_code') or request.json.get('activation_code')
    activation_code = request_args.get('activation_code')
    
    
    logger.debug('activation_code=%s', activation_code)
    
    if is_not_empty(activation_code):
        db_client = create_db_client(caller_info="check_activation")
        with db_client.context():
            device_setting = LoyaltyDeviceSetting.get_by_activation_code(activation_code)
        
        if device_setting:
            if device_setting.activated==False:
                return create_api_message(status_code=StatusCode.OK)
            else:
                return create_api_message('The code have been used to activate before', status_code=StatusCode.BAD_REQUEST)
        else:
            return create_api_message('Invalid activate code', status_code=StatusCode.BAD_REQUEST)
    else:
        return create_api_message('Activation code is required', status_code=StatusCode.BAD_REQUEST)

def get_device_setting(activation_code, device_id=None, platform=None):
    if is_not_empty(activation_code):
        db_client = create_db_client(caller_info="get_device_setting")
        with db_client.context():
            device_setting = LoyaltyDeviceSetting.get_by_activation_code(activation_code)
            
        if device_setting:
            device_token = None
            
            logger.debug('get_device_setting debug: platform=%s', platform);
            logger.debug('get_device_setting debug: device_setting.device_details=%s', device_setting.device_details);
            try:
                if is_not_empty(device_setting.device_details.get(platform)):
                    device_token = device_setting.device_details.get(platform).get('device_token')
            except:
                logger.error('Failed to get device token due to %s', get_tracelog());
                
            logger.info('Found device setting');
            if device_setting.activated==False:
            #if True:
                logger.info('device activation code is valid');
                device_setting_details = None
                with db_client.context():
                    if device_setting.is_test_setting==False:
                        device_setting.activate(device_id)
                    
                    device_setting_details                              = merchant_helpers.construct_setting_by_outlet(device_setting.assigned_outlet_entity, device_setting=device_setting) 
                    
                    device_setting_details['logo_image_url']            = url_for('system_bp.merchant_logo_image_url', merchant_act_key=device_setting_details.get('account_id'))
                    if device_token:
                        device_setting_details['device_token'] = device_token
                
                return create_api_message(status_code=StatusCode.OK,
                                               **device_setting_details
                                               )
            else:
                if device_id == device_setting.device_id: 
                    with db_client.context():
                        device_setting_details                              = merchant_helpers.construct_setting_by_outlet(device_setting.assigned_outlet_entity, device_setting=device_setting) 
                        
                        device_setting_details['logo_image_url']            = url_for('system_bp.merchant_logo_image_url', merchant_act_key=device_setting_details.get('account_id'))
                    
                    if device_token:
                        device_setting_details['device_token'] = device_token
                    
                    return create_api_message(status_code=StatusCode.OK,
                                               **device_setting_details
                                               )
                else:
                    return create_api_message('The code have been used in other device', status_code=StatusCode.BAD_REQUEST)
            '''
            else:
                logger.info('Device activation code have been used');
                return create_api_message('The code have been used to activate before', status_code=StatusCode.BAD_REQUEST)
            '''
        else:
            logger.info('Device setting record is not found');
            return create_api_message('Invalid activate code', status_code=StatusCode.BAD_REQUEST, error_code=API_ERR_CODE_INVALID_ACTIVATION_CODE)
    else:
        logger.info('activation_code is empty');
        return create_api_message('Activation code is required', status_code=StatusCode.BAD_REQUEST)
    
    
def reset_deviceSetting(activation_code, device_id):
    if is_not_empty(activation_code):
        db_client = create_db_client(caller_info="reset_deviceSetting")
        with db_client.context():
            device_setting = LoyaltyDeviceSetting.get_by_activation_code(activation_code)
        
        logger.debug('device_setting=%s', device_setting);
        
        if device_setting:
            logger.info('Found device setting');
            if device_setting.activated==True:
            
                if device_id == device_setting.device_id: 
                    
                    with db_client.context():
                        device_setting.reset()
                    
                    return create_api_message(status_code=StatusCode.OK,
                                               )
                else:
                    return create_api_message('The code have been used in other device', status_code=StatusCode.BAD_REQUEST)
            
        else:
            logger.info('Device setting record is not found, thus the activation code should be invalid');
            return create_api_message('Invalid activate code', status_code=StatusCode.BAD_REQUEST, error_code=API_ERR_CODE_INVALID_ACTIVATION_CODE)
    else:
        logger.info('activation_code is empty');
        return create_api_message('Activation code is required', status_code=StatusCode.BAD_REQUEST)    
    
    
def updateActivationAndGetDeviceSetting(activation_code, device_id):
    if is_not_empty(activation_code) and is_not_empty(device_id):
        db_client = create_db_client(caller_info="updateActivationAndGetDeviceSetting")
        with db_client.context():
            device_setting = LoyaltyDeviceSetting.get_by_activation_code(activation_code)
        
        logger.debug('device_setting=%s by activation_code=%s', device_setting, activation_code);
        
        if device_setting:
            logger.info('Device activation code is valid');
            
            is_valid = False
            device_setting_details = None
            is_production = conf.IS_PRODUCTION
            
            logger.info('is_production=%s', is_production);
            
            with db_client.context():
                #device_setting = LoyaltyDeviceSetting.get_by_activation_code(activation_code)
                if device_setting.is_test_setting==False:
                    if device_setting.activated:
                        if device_setting.device_id == device_id:
                            is_valid = True
                        
                    else:
                        is_valid = True
                        #if is_production:
                        device_setting.activate(device_id)
                else:
                    is_valid = True
                
                if is_valid:    
                    device_setting_details  = merchant_helpers.construct_setting_by_outlet(device_setting.assigned_outlet_entity, device_setting=device_setting)
                    #pos_setting_details['logo_image_url']               = url_for('system_bp.merchant_logo_image_url', merchant_act_key=pos_setting_details.get('account_id'))
                
            if is_valid:
                
                logger.debug('device_setting_details=%s', device_setting_details);
                
                return create_api_message(status_code=StatusCode.OK,
                                           **device_setting_details
                                           )
            else:
                if device_setting.activated and device_setting.device_id != device_id:
                    return create_api_message('The code have been used in other device', status_code=StatusCode.BAD_REQUEST)
                else:
                    return create_api_message('Failed to activate', status_code=StatusCode.BAD_REQUEST)
            
        else:
            logger.info('Setting record is not found');
            return create_api_message('Invalid activate code', status_code=StatusCode.BAD_REQUEST)
    else:
        logger.info('activation_code is empty or device id is empty');
        return create_api_message('Activation code and device id are required', status_code=StatusCode.BAD_REQUEST)

@loyalty_api_bp.route('/read-settings/activation-code', methods=['POST'])
@request_values
def read_device_setting(request_values):
    
    
    #device_id           = request.args.get('device_id') or request.form.get('device_id') or request.json.get('device_id')
    #activation_code     = request.args.get('activation_code') or request.form.get('activation_code') or request.json.get('activation_code')
    activation_code     = request_values.get('activation_code')
    device_id           = request_values.get('device_id')
    
    logger.info('device_id=%s', device_id)
    logger.info('activation_code=%s', activation_code)
    
    if is_not_empty(activation_code):
        db_client = create_db_client(caller_info="read_device_setting")
        with db_client.context():
            device_setting = LoyaltyDeviceSetting.get_by_activation_code(activation_code)
        
        if device_setting:
            logger.info('Found device setting')
            if device_setting.activated==False:
            #if True:
                logger.info('device activation code is valid');
                device_setting_details = None
                with db_client.context():
                    device_setting_details                              = merchant_helpers.construct_setting_by_outlet(device_setting.assigned_outlet_entity, device_setting=device_setting, is_pos_device=False) 
                    device_setting_details['logo_image_url']            = url_for('system_bp.merchant_logo_image_url', merchant_act_key=device_setting_details.get('account_id'))
                    device_setting_details['device_id']                 = device_id
                    
                logger.debug('device_setting_details=%s', device_setting_details)
                
                return create_api_message(status_code=StatusCode.OK,
                                               **device_setting_details
                                               )
            else:
                return create_api_message('The code have been used in other device', status_code=StatusCode.BAD_REQUEST)
            
        else:
            logger.info('Device setting record is not found');
            return create_api_message('Invalid activate code', status_code=StatusCode.BAD_REQUEST, error_code=API_ERR_CODE_INVALID_ACTIVATION_CODE)
    else:
        logger.info('activation_code is empty');
        return create_api_message('Activation code is required', status_code=StatusCode.BAD_REQUEST)

@loyalty_api_bp.route('/activation-code/<activation_code>', methods=['GET'])
def check_activation_code(activation_code):
    
    
    logger.info('activation_code=%s', activation_code)
    
    if is_not_empty(activation_code):
        db_client = create_db_client(caller_info="check_activation_code")
        with db_client.context():
            device_setting = LoyaltyDeviceSetting.get_by_activation_code(activation_code)
        
        if device_setting:
            logger.info('Found device setting');
            if device_setting.activated==False:
                return create_api_message(status_code=StatusCode.OK
                                               )
            else:
                return create_api_message('The code have been used in other device', status_code=StatusCode.BAD_REQUEST, error_code=API_ERR_CODE_USED_ACTIVATION_CODE)
            
        else:
            logger.info('Device setting record is not found');
            return create_api_message('Invalid activation code', status_code=StatusCode.BAD_REQUEST, error_code=API_ERR_CODE_INVALID_ACTIVATION_CODE)
    else:
        logger.info('activation_code is empty');
        return create_api_message('Activation code is required', status_code=StatusCode.BAD_REQUEST)    
        
    
@loyalty_api_bp.route('/account-sync', methods=['GET'])
@request_headers
@request_args
def account_sync(request_headers, request_args):
    #activation_code = request.args.get('activation_code') or request.form.get('activation_code') or request.json.get('activation_code')
    #device_id       = request.args.get('device_id') or request.form.get('device_id') or request.json.get('device_id')
    activation_code     = request_args.get('activation_code')
    device_id           = request_args.get('device_id')
    platform            = request_headers.get('x-platform')
    
    logger.info('activation_code=%s', activation_code)
    logger.info('device_id=%s', device_id)
    logger.info('platform=%s', platform)
    
    return get_device_setting(activation_code, device_id, platform=platform)
    
    
@loyalty_api_bp.route('/activate', methods=['POST'])
@request_values
def activate_post(request_values):
    
    #activation_code = request.args.get('activation_code') or request.form.get('activation_code') or request.json.get('activation_code')
    #device_id       = request.args.get('device_id') or request.form.get('device_id') or request.json.get('device_id')
    activation_code     = request_values.get('activation_code')
    device_id           = request_values.get('device_id')
    
    logger.info('activation_code=%s', activation_code)
    logger.info('device_id=%s', device_id)
    
    return updateActivationAndGetDeviceSetting(activation_code, device_id)
        

@loyalty_api_bp.route('/activate-reset', methods=['POST'])
@request_args
def reset_post(request_args):
    
    #activation_code = request.args.get('activation_code') or request.form.get('activation_code') or request.json.get('activation_code')
    #device_id       = request.args.get('device_id') or request.form.get('device_id') or request.json.get('device_id')
    activation_code     = request_args.get('activation_code')
    device_id           = request_args.get('device_id')
    
    logger.info('activation_code=%s', activation_code)
    logger.info('device_id=%s', device_id)
    
    return reset_deviceSetting(activation_code, device_id)

@loyalty_api_bp.route('/update-device-notification-details', methods=['POST'])
@device_activated_is_required
@request_values
def update_device_details(activation_code, request_values):
    #platform        = request.args.get('platform') or request.form.get('platform') or request.json.get('platform')
    #device_token    = request.args.get('device_token') or request.form.get('device_token') or request.json.get('device_token')
    
    platform        = request_values.get('platform')
    device_token    = request_values.get('device_token')
    
    logger.info('request_values=%s', request_values)
    
    logger.info('activation_code=%s', activation_code)
    logger.info('platform=%s', platform)
    logger.info('device_token=%s', device_token)
    
    if is_not_empty(platform) and is_not_empty(device_token):
        db_client                           = create_db_client(caller_info="update_device_details")
        
        with db_client.context():
            device_setting = LoyaltyDeviceSetting.get_by_activation_code(activation_code)
            
            device_setting.update_device_details(platform, device_token)
            
        
        return create_api_message(status_code=StatusCode.ACCEPTED)
    else:
        return create_api_message('Missing required data', status_code=StatusCode.BAD_REQUEST)       
    
@loyalty_api_bp.route('/version-sync', methods=['get'])
def version_sync():
    db_client       = create_db_client(caller_info="version_sync")
    
    with db_client.context():
        version =  {
                               
                                'setting':[
                                            
                                            {
                                                "table_name": "setting",
                                                "version" : 10,
                                                "script": "ALTER TABLE setting ADD COLUMN gmt_hour TEXT DEFAULT 8;"
                                                
                                                
                                            },
                                            {
                                                "table_name": "setting",
                                                "version" : 8,
                                                "script": "ALTER TABLE setting ADD COLUMN industry_type TEXT DEFAULT 'fb';"
                                                
                                                
                                            }
                                            
                                               
                                        ],
                                       
                            }
                                
    
            
    
    return version




 