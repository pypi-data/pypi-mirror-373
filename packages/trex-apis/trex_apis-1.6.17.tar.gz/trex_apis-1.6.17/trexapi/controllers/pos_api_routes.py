'''
Created on 28 Oct 2021

@author: jacklok
'''

from flask import Blueprint, request, url_for, jsonify
import logging, json
from trexapi.decorators.api_decorators import auth_token_required,\
    device_activated_is_required
from trexlib.utils.string_util import is_not_empty, is_empty
from trexmodel.models.datastore.pos_models import POSSetting
from trexmodel.utils.model.model_util import create_db_client
from trexmodel.models import merchant_helpers
from trexmodel.models.datastore.product_models import ProductCatalogue,\
    ProductCategory
from trexlib.utils.common.common_util import sort_list
from firebase_admin import firestore
from datetime import datetime
from trexapi.conf import API_ERR_CODE_INVALID_ACTIVATION_CODE,\
    API_ERR_CODE_USED_ACTIVATION_CODE
from trexapi.utils.api_helpers import create_api_message, StatusCode
from trexlib.utils.log_util import get_tracelog
from trexlib.libs.flask_wtf.request_wrapper import request_values, request_args


#logger = logging.getLogger('api')
logger = logging.getLogger('debug')

pos_api_bp = Blueprint('pos_api_bp', __name__,
                                 template_folder='templates',
                                 static_folder='static',
                                 url_prefix='/api/v1/pos')

@pos_api_bp.route('/check-activation', methods=['POST'])
@request_args
def check_activation(request_args):
    
    activation_code = request_args.get('activation_code')
    logger.debug('activation_code=%s', activation_code)
    
    if is_not_empty(activation_code):
        db_client = create_db_client(caller_info="check_activation")
        with db_client.context():
            pos_setting = POSSetting.get_by_activation_code(activation_code)
        
        if pos_setting:
            if pos_setting.activated==False:
                return create_api_message(status_code=StatusCode.OK)
            else:
                return create_api_message('The code have been used to activate before', status_code=StatusCode.BAD_REQUEST)
        else:
            return create_api_message('Invalid activate code', status_code=StatusCode.BAD_REQUEST)
    else:
        return create_api_message('Activation code is required', status_code=StatusCode.BAD_REQUEST)

@pos_api_bp.route('/read-settings/activation-code', methods=['POST'])
@request_values
def read_device_setting(request_values):
    activation_code     = request_values.get('activation_code')
    device_id           = request_values.get('device_id')
    
    logger.info('activation_code=%s', activation_code)
    logger.info('device_id=%s', device_id)
    
    if is_not_empty(activation_code):
        db_client = create_db_client(caller_info="read_device_setting")
        with db_client.context():
            device_setting = POSSetting.get_by_activation_code(activation_code)
        
        if device_setting:
            logger.info('Found device setting');
            if device_setting.activated==False:
            #if True:
                logger.info('device activation code is valid');
                device_setting_details = None
                with db_client.context():
                    device_setting_details                              = merchant_helpers.construct_setting_by_outlet(device_setting.assigned_outlet_entity, device_setting=device_setting, is_pos_device=True) 
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

@pos_api_bp.route('/activation-code/<activation_code>', methods=['GET'])
def check_activation_code(activation_code):
    
    
    logger.info('activation_code=%s', activation_code)
    
    if is_not_empty(activation_code):
        db_client = create_db_client(caller_info="check_activation_code")
        with db_client.context():
            device_setting = POSSetting.get_by_activation_code(activation_code)
        
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

def getPOSAccountSetting(activation_code):
    if is_not_empty(activation_code):
        db_client = create_db_client(caller_info="getPOSAccountSetting")
        with db_client.context():
            pos_setting = POSSetting.get_by_activation_code(activation_code)
        
        if pos_setting:
            logger.info('Found POS setting');
            #if pos_setting.activated==False:
            if True:
                logger.info('POS activation code is valid');
                pos_setting_details = None
                with db_client.context():
                    if pos_setting.is_test_setting==False:
                        pos_setting.activate(activation_code)
                    
                    outlet                                              = pos_setting.assigned_outlet_entity
                    pos_setting_details                                 = merchant_helpers.construct_setting_by_outlet(outlet, device_setting=pos_setting, is_pos_device=True) 
                    
                    pos_setting_details['logo_image_url']               = url_for('system_bp.merchant_logo_image_url', merchant_act_key=pos_setting_details.get('account_id'))
                
                #if is_activated:
                if True:
                    
                    logger.debug('pos_setting_details=%s', pos_setting_details);
                    
                    return create_api_message(status_code=StatusCode.OK,
                                               **pos_setting_details
                                               )
                else:
                    return create_api_message('Failed to activate', status_code=StatusCode.BAD_REQUEST)
            else:
                logger.info('POS activation code have been used');
                return create_api_message('The code have been used to activate before', status_code=StatusCode.BAD_REQUEST)
        else:
            logger.info('POS setting record is not found');
            return create_api_message('Invalid activation code', status_code=StatusCode.BAD_REQUEST, error_code=API_ERR_CODE_INVALID_ACTIVATION_CODE)
    else:
        logger.info('activation_code is empty');
        return create_api_message('Activation code is required', status_code=StatusCode.BAD_REQUEST)
    
    
def updateActivationAndGetPOSAccountSetting(activation_code, device_id):
    
    if is_not_empty(activation_code) and is_not_empty(device_id):
        logger.info('activation_code=%s', activation_code)
        logger.info('device_id=%s', device_id)
        
        db_client = create_db_client(caller_info="updateActivationAndGetPOSAccountSetting")
        with db_client.context():
            pos_setting = POSSetting.get_by_activation_code(activation_code)
        
        if pos_setting:
            logger.info('POS activation code is valid')
            
            is_valid = False
            pos_setting_details = None
            
            with db_client.context():
                if pos_setting.is_test_setting==False:
                    logger.info('pos_setting.activated=%s', pos_setting.activated)
                    logger.info('pos_setting.device_id=%s', pos_setting.device_id)
                    
                    
                    if pos_setting.activated:
                        logger.info('pos_setting.device_id==device_id %s', pos_setting.device_id==device_id)
                        
                        if pos_setting.device_id == device_id:
                            is_valid = True
                    else:
                        is_valid = True
                        pos_setting.activate(device_id)
                else:
                    logger.info('POS activation code is test code')
                    is_valid = True
                    
                if is_valid:    
                    
                    pos_setting_details                                 = merchant_helpers.construct_setting_by_outlet(pos_setting.assigned_outlet_entity, device_setting=pos_setting, is_pos_device=True)
                    #pos_setting_details['logo_image_url']               = url_for('system_bp.merchant_logo_image_url', merchant_act_key=pos_setting_details.get('account_id'))
            
            if is_valid:
                
                logger.debug('pos_setting_details=%s', pos_setting_details);
                
                return create_api_message(status_code=StatusCode.OK,
                                           **pos_setting_details
                                           )
            else:
                if pos_setting.activated and pos_setting.device_id != device_id:
                    return create_api_message('The code have been used to activate before', status_code=StatusCode.BAD_REQUEST)
                else:
                    return create_api_message('Failed to activate', status_code=StatusCode.BAD_REQUEST)
            
        else:
            logger.info('POS setting record is not found');
            return create_api_message('Invalid activate code', status_code=StatusCode.BAD_REQUEST)
    else:
        logger.info('activation_code is empty or device id is empty');
        return create_api_message('Activation code and device id are required', status_code=StatusCode.BAD_REQUEST)
        
    
@pos_api_bp.route('/account-sync', methods=['get'])
def activate():
    try:
        activation_code = request.args.get('activation_code') or request.form.get('activation_code') or request.json.get('activation_code')
        logger.debug('activation_code=%s', activation_code)
        return getPOSAccountSetting(activation_code)
    except:
        logger.error('Missing activation code')
        return create_api_message('Missing activate code', status_code=StatusCode.BAD_REQUEST)
    
@pos_api_bp.route('/activate', methods=['POST'])
def activate_post():
    
    try:
        
        activation_code = request.args.get('activation_code') or request.form.get('activation_code') or request.json.get('activation_code')
        device_id       = request.args.get('device_id') or request.form.get('device_id') or request.json.get('device_id')
        
        logger.debug('activation_code=%s', activation_code)
        logger.debug('device_id=%s', device_id)
        
        return updateActivationAndGetPOSAccountSetting(activation_code, device_id)
    
    except:
        logger.error('Failed to activate due to %s', get_tracelog())
        return create_api_message('Missing activate code', status_code=StatusCode.BAD_REQUEST)    
       
    
def parse_category_to_json(category_tree_structure):
    data_list = []
    
    for category in category_tree_structure:
        data = {
                    'code'                  : category.get('key'),
                    'label'                 : category.get('category_label'),
                    'label_with_item_count' : category.get('category_label_and_other_details'),
                    'group'                 : category.get('has_child'),
                    'product_modifier'      : category.get('product_modifier'),
                    'product_items'         : category.get('product_items'),
                }
        if category.get('childs'):
            child_data_list = parse_category_to_json(category.get('childs'))
            if child_data_list:
                data['childs'] = child_data_list   
        
        data_list.append(data)
    
    return data_list

def construct_category_tree_structure(category_tree_structure, category_list):
    for category in category_list:
        if is_empty(category.get('parent_category_key')):
            #top most category
            category_tree_structure.append(category)
            __find_child_category(category, category_list)
                

def __lookup_category_from_category_list(category_code, category_list):
    for category in category_list:
        if category.get('key') == category_code:
            return category  

    
def __find_child_category(category, category_list):
    if is_not_empty(category.get('child_category_keys')):
        childs                      = []
        parent_product_modifier     = category.get('product_modifier') or []
        
        for child_category_key in category.get('child_category_keys'):
            child = __lookup_category_from_category_list(child_category_key, category_list)
            
            logger.debug('category product_modifier of %s =%s', category.get('key'), parent_product_modifier)
            if child:
                child_product_modifier      = child.get('product_modifier') or []
                child_product_modifier      = list(set(parent_product_modifier) | set(child_product_modifier) )
                child['product_modifier']   = child_product_modifier
                
                logger.debug('child_product_modifier of %s =%s', category.get('key'), child_product_modifier)
                
                if is_not_empty(child.get('child_category_keys')):
                    __find_child_category(child, category_list)
                childs.append(child)
        
        category['childs'] = childs

def get_product_category_structure_code_label_json(merchant_acct):
    category_list       = get_product_category_structure(merchant_acct)
    
    category_tree_structure = []
    
    construct_category_tree_structure(category_tree_structure, category_list)
    
    return parse_category_to_json(category_tree_structure)

def get_product_category_structure(merchant_acct):
    
    sorted_category_structure = []
    
    category_structure      = ProductCategory.get_structure_by_merchant_acct(merchant_acct)
    category_structure      = sort_list(category_structure, sort_attr_name='category_label')
    
    #logger.debug('category_structure=%s', category_structure)
    
    for c in category_structure:
        sorted_category_structure.append(c.to_dict())
    
    
    logger.debug('sorted_category_structure=%s', sorted_category_structure)
            
    return sorted_category_structure

@pos_api_bp.route('/check-catalogue-status', methods=['GET'])
@auth_token_required
def check_catalogue_status():
    activation_code = request.args.get('activation_code') or request.form.get('activation_code') or request.json.get('activation_code')
    
    if is_not_empty(activation_code):
        pos_setting = None
        db_client = create_db_client(caller_info="check_catalogue_status")
        with db_client.context():
            pos_setting = POSSetting.get_by_activation_code(activation_code)
            if pos_setting:
                
                assigned_outlet = pos_setting.assigned_outlet_entity
                
                catalogue_key   = assigned_outlet.assigned_catalogue_key
                
                if is_not_empty(catalogue_key):
                    product_catalogue   = ProductCatalogue.fetch(catalogue_key)
                    if product_catalogue:
                        return {
                                    'last_updated_datetime' : product_catalogue.modified_datetime.strftime('%d-%m-%Y %H:%M:%S')
                                } 
                    else:
                        return create_api_message('Invalid catalogue data', status_code=StatusCode.BAD_REQUEST)
        
        if pos_setting is None:
            return create_api_message('Invalid activation code', status_code=StatusCode.BAD_REQUEST, err_code=API_ERR_CODE_INVALID_ACTIVATION_CODE)
        else:
            return create_api_message('Not catqalogue have been assigned or published', status_code=StatusCode.BAD_REQUEST)
                
    else:
        return create_api_message('Activation code is required', status_code=StatusCode.BAD_REQUEST)
    
@pos_api_bp.route('/get-catalogue', methods=['GET'])
#@auth_token_required
@request_args
def get_catalogue(request_args):
    #activation_code = request.args.get('activation_code') or request.form.get('activation_code') or request.json.get('activation_code')
    activation_code = request_args.get('activation_code')
    
    logger.debug('activation_code=%s', activation_code);
    
    if is_not_empty(activation_code):
        pos_setting         = None
        db_client           = create_db_client(caller_info="get_catalogue")
        valid_return        = None
        product_catalogue   = None
        with db_client.context():
            pos_setting = POSSetting.get_by_activation_code(activation_code)
            if pos_setting:
                
                assigned_outlet = pos_setting.assigned_outlet_entity
                
                logger.info('assigned_outlet name=%s', assigned_outlet.name)
                
                catalogue_key   = assigned_outlet.assigned_catalogue_key
                
                logger.debug('catalogue_key=%s', catalogue_key);
                
                if is_not_empty(catalogue_key):
                    product_catalogue   = ProductCatalogue.fetch(catalogue_key)
                    merchant_acct       = pos_setting.merchant_acct_entity
                    
                    #category_tree_structure_in_json  = json.dumps(get_product_category_structure_code_label_json(merchant_acct), sort_keys = True, separators = (',', ': '))
                    category_tree_structure_in_json  = get_product_category_structure_code_label_json(merchant_acct)
                    
                    if product_catalogue:
                        last_updated_datetime = product_catalogue.modified_datetime
                        if assigned_outlet.modified_datetime is not None and assigned_outlet.modified_datetime>last_updated_datetime:
                            last_updated_datetime = assigned_outlet.modified_datetime
                        valid_return =  {
                                                'key'                       : catalogue_key,    
                                                'category_list'             : category_tree_structure_in_json,
                                                'product_by_category_map'   : product_catalogue.published_menu_settings,
                                                'last_updated_datetime'     : last_updated_datetime.strftime('%d-%m-%Y %H:%M:%S')
                                            } 
                    
                
                    
        if valid_return:
            return valid_return
        else:
            if product_catalogue==None:
                logger.debug('No catalogue have been assigned or published');
                return create_api_message('No catqalogue have been assigned or published', status_code=StatusCode.BAD_REQUEST)
            else:
                if pos_setting is None:
                    logger.debug('Invalid activation code');
                    return create_api_message('Invalid activation code', status_code=StatusCode.BAD_REQUEST, err_code=API_ERR_CODE_INVALID_ACTIVATION_CODE)
                else:
                    logger.debug('No catalogue have been assigned or published');
                    return create_api_message('No catqalogue have been assigned or published', status_code=StatusCode.BAD_REQUEST)
                
    else:
        return create_api_message('Activation code is required', status_code=StatusCode.BAD_REQUEST)    

@pos_api_bp.route('/update-device-notification-details', methods=['POST'])
@device_activated_is_required
@request_values
def update_device_details(activation_code, request_values):
    
    platform        = request_values.get('platform')
    device_token    = request_values.get('device_token')
    
    logger.info('request_values=%s', request_values)
    
    logger.info('activation_code=%s', activation_code)
    logger.info('platform=%s', platform)
    logger.info('device_token=%s', device_token)
    
    if is_not_empty(platform) and is_not_empty(device_token):
        db_client                           = create_db_client(caller_info="update_device_details")
        
        with db_client.context():
            pos_setting = POSSetting.get_by_activation_code(activation_code)
            
            pos_setting.update_device_details(platform, device_token)
            
        
        return create_api_message(status_code=StatusCode.ACCEPTED)
    else:
        return create_api_message('Missing required data', status_code=StatusCode.BAD_REQUEST)  

@pos_api_bp.route('/version-sync', methods=['get'])
def version_sync():
    db_client       = create_db_client(caller_info="version_sync")
    
    with db_client.context():
        '''
        'setting':[
                    {
                        "table_name": "setting",
                        "version" : 1,
                        "script": "ALTER TABLE setting ADD COLUMN account_settings TEXT",
                    }
                       
                ],
        'user'  :[
                    {
                        "table_name": "user",
                        "version" : 1,
                        "script": "ALTER TABLE user ADD COLUMN token_expiry_datetime TEXT",
                        
                    }
                ]
                
        '''
        version =  {
                                
                                'ordering'  :[
                                            {
                                                "table_name": "ordering",
                                                "version" : 4,
                                                "script": "ALTER TABLE ordering ADD COLUMN sales_date TEXT",
                                                
                                            }
                                            
                                        ]
                                       
                            }
                                
    
            
    
    return version

@pos_api_bp.route('/sales-overview/merchant/<merchant_code>/outlet/<outlet_key>/date/<transact_date>', methods=['GET'])
#@auth_token_required
def sales_overview_stat(merchant_code, outlet_key, transact_date):
    total_sales_amount              = .0
    total_tax_amount                = .0
    total_service_charge_amount     = .0
    total_paid_count                = 0
    total_voided_count              = 0
    total_item_sold_count           = 0
    
    firebase        = firestore.client()        
    invoice_path    = 'merchant/%s/outlet/%s/date/%s/invoice' % (merchant_code, outlet_key, transact_date)
    
    logger.debug('invoice_path=%s', invoice_path)
    
    invoice_list_ref = firebase.collection(invoice_path).stream()
    #invoice_list_ref = firebase.collection('merchant').document(merchant_code).collection('outlet').document(outlet_key).collection('date').document(transact_date).collection('invoice').stream()
    
    
    try:
        for invoice_ref in invoice_list_ref:
            invoice = invoice_ref.to_dict()
            logger.debug('invoice=%s', invoice)
            
            if invoice.get('status') == 'voided':
                total_voided_count+=1
                
            elif invoice.get('status') == 'paid':
                payment_details     = json.loads(invoice.get('payment_details'))
                transaction_items   = json.loads(invoice.get('transaction_items'))
                total_sales_amount+= payment_details.get('net_total_amount')
                total_paid_count+=1
                
                for tax_details in payment_details.get('tax_details_list'):
                    total_tax_amount+=tax_details.get('tax_amount')
                    
                for service_charge_details in payment_details.get('service_charge_details_list'):
                    total_service_charge_amount+=service_charge_details.get('charge_amount')
                
                for item in transaction_items:
                    total_item_sold_count+=item.get('ordered_quantity')
                
                
            
                
    except Exception as e:
        logger.error('%s', e)
    
    return jsonify({
                    'total_paid_count'              : total_paid_count,
                    'total_voided_count'            : total_voided_count,
                    'total_sales_amount'            : total_sales_amount,
                    'total_tax_amount'              : total_tax_amount,
                    'total_service_charge_amount'   : total_service_charge_amount,
                    'total_item_sold_count'         : total_item_sold_count,
                    })
    
  
#@pos_api_bp.route('/counter/<date_value>', methods=['POST'])
#@auth_token_required
@pos_api_bp.route('/counter/merchant/<merchant_code>/outlet/<outlet_key>/date/<transact_date>', methods=['POST'])
def counter_post(merchant_code, outlet_key, transact_date):
    value = request.args.get('value') or request.form.get('value') or request.json.get('value')
    firebase = firestore.client()
           
    #counter_ref = firebase.collection('test').document('counter').collection(date_value).document('details')
    counter_ref = firebase.collection('merchant').document(merchant_code).collection('outlet').document(str(outlet_key)).collection('date').document(transact_date).collection('counter').document('details')
    
    if counter_ref is None:
        logger.debug('Counter is not found')
        counter_ref.set({'value':value})
    else:    
        logger.debug('Counter is found')
        counter_ref.set({'value':value})
    
    return 'OK'

#@pos_api_bp.route('/counter/<date_value>', methods=['GET'])
@pos_api_bp.route('/counter/merchant/<merchant_code>/outlet/<outlet_key>/date/<transact_date>', methods=['GET'])
#@auth_token_required
def counter_get(merchant_code, outlet_key, transact_date):
    firebase = firestore.client()
     
    counter_ref = firebase.collection('merchant').document(merchant_code).collection('outlet').document(str(outlet_key)).collection('date').document(transact_date).collection('counter').document('details')
    #counter_ref = firebase.collection('test').document('counter').collection(date_value).document('details')
    counter_value = 0
    if counter_ref is not None:
        counter_value = counter_ref.get().get('value')
    
    return jsonify({
                    'value': counter_value,
                })



 