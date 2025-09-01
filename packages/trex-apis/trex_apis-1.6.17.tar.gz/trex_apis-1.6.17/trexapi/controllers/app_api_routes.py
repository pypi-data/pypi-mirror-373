from flask import Blueprint
import logging
from trexmodel.utils.model.model_util import create_db_client
from trexmodel.models.datastore.admin_models import AppBannerFile
 
from flask.json import jsonify
from trexapi.conf import APPLICATION_NAME
from trexconf.conf import API_VERSION

app_api_bp = Blueprint('app_api_bp', __name__,
                                 template_folder='templates',
                                 static_folder='static',
                                 url_prefix='/api/v1/app')

logger = logging.getLogger('debug')


@app_api_bp.route('/ping', methods=['GET'])
def ping():
    
    return '%s-%s'% (APPLICATION_NAME, API_VERSION), 200

@app_api_bp.route('/app-package-info/app/<app_name>/platform/<platform>', methods=['GET'])
def app_package_info(app_name, platform):
    logger.debug('---app_package_info---')
    
    logger.info('app_name=%s, plaform=%s', app_name, platform)
    package_info = {}
    
    if platform=='android':
        if app_name.lower() == 'memberasia':
            package_info =  {
                        'app_name'      : app_name,
                        'platform'      : platform,
                        'version'       : '1.5.2',
                        'can_update'    : False,
                        'update_url'    : '',    
        
                    }
        elif app_name.lower() == 'memberla':
            package_info =  {
                        'app_name'      : app_name,
                        'platform'      : platform,
                        'version'       : '1.5.0',
                        'can_update'    : True,
                        'update_url'    : 'https://play.google.com/store/apps/details?id=com.augmigo.memberla',
        
                    }
        
    elif platform=='ios':
        
        if app_name.lower() == 'memberasia':
            package_info =  {
                        'app_name'      : app_name,
                        'platform'      : platform,
                        'version'       : '1.5.2',
                        'can_update'    : False,
                        'update_url'    : '',
        
                    }
        elif app_name.lower() == 'memberla':
            package_info =  {
                        'app_name'      : app_name,
                        'platform'      : platform,
                        'version'       : '1.5.0',
                        'can_update'    : False,
                        'update_url'    : '',
        
                    }
            
    elif platform=='window':
        
        if app_name == 'memberasia':
            package_info =  {
                        'app_name'      : app_name,
                        'platform'      : platform,
                        'version'       : '1.5.2',
                        'can_update'    : False,
                        'update_url'    : '',
        
                    }
        elif app_name == 'memberla':
            package_info =  {
                        'app_name'      : app_name,
                        'platform'      : platform,
                        'version'       : '1.0.1',
                        'can_update'    : False,
                        'update_url'    : '',
        
                    }        
               
    return package_info

@app_api_bp.route('/settings', methods=['GET'])
def app_setting():
    logger.debug('---app_setting---')
    
    banner_file_list = []
    db_client = create_db_client(caller_info="app_setting")
    with db_client.context():
        
        result_listing = AppBannerFile.list()
        
                
        if result_listing:
            for banner_file in result_listing:
                #banner_file_list.append(banner_file.to_dict(dict_properties=['banner_file_public_url','sequence'], show_key=False))
                banner_file_list.append({
                                        'image_url': banner_file.banner_file_public_url,
                                        'sequence': banner_file.sequence,
                                        })
                
    ##sorted_banner_file_list = sort_dict_list(banner_file_list, sort_attr_name='sequence')
    
    app_settings =  {
                        'banners': banner_file_list,
                        'message_box_settings'  : {
                                                'max_read_count'                : 2,
                                                'read_interval_in_second'       : 60,
                                                'list_message_pagination_limit' : 10,
                                                },
                        'transaction_history_settings'  : {
                                                'max_read_count'                    : 2,
                                                'read_interval_in_second'           : 60,
                                                'list_transaction_pagination_limit' : 10,
                                                },
                        'account_settings'      :{
                                                'login_session_length_in_hour'  : 720,
                                                },
                        'outlet_order_enabled'          : False,
                        'cache_settings': {
                            
                                            'cache_length_in_minute'        : 60,
                                            'login_session_length_in_hour'  : 120,
                                        }
                        
                        
        
                    }
    '''
    return create_rest_message(status_code=StatusCode.OK,
                                               **app_settings,
                                               )
    '''
    logger.debug('app_settings=%s', app_settings)
    return app_settings

@app_api_bp.route('/promotions', methods=['GET'])
def list_app_promotions():
    logger.debug('---list_app_promotions---')
    result_listing = [
            
            {
                'title':'GoodTaste',
                'content':'10% Discount for member during June 2023',
            },
            {
                'title':'Anviet',
                'content':'Entitled RM10 cash voucher for miniumum RM50 spending per receipt during June 2023',
            }
            
        
        ]
    '''
    db_client = create_db_client(caller_info="list_app_promotions")
    with db_client.context():
        
        result_listing = AppPromotion.list()
        logger.debug('result_listing=%s', result_listing)
    '''
    
        
    return jsonify({
            'promotions': result_listing,
            })
    
@app_api_bp.route('/messages', methods=['GET'])
def list_app_messages():
    logger.debug('---list_app_messages---')
    result_listing = [
            {
                'title':'Welcome',
                'content':'Welcome on board',
            }
        ]
    '''
    db_client = create_db_client(caller_info="list_app_highlights")
    with db_client.context():
        
        result_listing = AppMessage.list()
        logger.debug('result_listing=%s', result_listing)
    '''
    
        
    return jsonify({
            'messages': result_listing,
            })    


