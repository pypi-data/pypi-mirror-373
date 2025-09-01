'''
Created on 28 Jul 2025

@author: jacklok
'''

from flask import Blueprint, request, url_for
import logging
from trexlib.utils.string_util import is_not_empty
from trexapi.utils.api_helpers import StatusCode, create_api_message
from trexmodel.utils.model.model_util import create_db_client
from trexlib.libs.flask_wtf.request_wrapper import request_values
from trexlib.utils.log_util import get_tracelog
from trexmodel.models.datastore.support_models import ErrorReport


logger = logging.getLogger('api')
#logger = logging.getLogger('debug')

support_api_bp = Blueprint('support_api_bp', __name__,
                                 template_folder='templates',
                                 static_folder='static',
                                 url_prefix='/api/v1/support')

@support_api_bp.route('/report-error', methods=['POST'])
@request_values
def report_error(request_values):
    platform        = request_values.get('platform')
    activation_code = request_values.get('activation_code')
    error_message   = request_values.get('error_message')
    stack_trace     = request_values.get('stack_trace')
    
    logger.info('request_values=%s', request_values)
    
    logger.info('activation_code=%s', activation_code)
    logger.info('platform=%s', platform)
    logger.info('error_message=%s', error_message)
    logger.info('stack_trace=%s', stack_trace)
    
    if is_not_empty(platform) and is_not_empty(error_message):
        db_client                           = create_db_client(caller_info="update_device_details")
        
        with db_client.context():
            ErrorReport.create(platform, error_message, activation_code=activation_code, stack_trace=stack_trace)
            
        return create_api_message(status_code=StatusCode.ACCEPTED)
    else:
        return create_api_message('Missing required data', status_code=StatusCode.BAD_REQUEST)       
