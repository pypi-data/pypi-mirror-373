'''
Created on 29 Jul 2025

@author: jacklok
'''

from flask import Blueprint
import logging
from trexlib.utils.string_util import is_not_empty
from trexapi.utils.api_helpers import StatusCode, create_api_message
from trexmodel.utils.model.model_util import create_db_client
from trexlib.libs.flask_wtf.request_wrapper import request_values, outlet_key,\
    request_args
from trexapi.decorators.api_decorators import auth_token_required
from trexmodel.models.datastore.merchant_models import Outlet
from trexmodel.models.datastore.transaction_models import SalesTransaction
from trexconf import conf
from datetime import datetime
from flask.json import jsonify

#logger = logging.getLogger('api')
logger = logging.getLogger('target_debug')

outlet_report_api_bp = Blueprint('outlet_report_api_bp', __name__,
                                 template_folder='templates',
                                 static_folder='static',
                                 url_prefix='/api/v1/outlet-report')

@outlet_report_api_bp.route('/sales-report-by-date', methods=['GET'])
@auth_token_required
@outlet_key
@request_args
def get_outlet_today_sales_report(outlet_key, request_args):
    db_client = create_db_client(caller_info="get_outlet_today_sales_report")
    transactions_list = []
    
    enquiry_date_str            = request_args.get('enquiry_date')
    
    logger.debug('enquiry_date=%s', enquiry_date_str)
    logger.debug('outlet_key=%s', outlet_key)
    
    with db_client.context():
        outlet = Outlet.fetch(outlet_key)
        
        
    
    if outlet:
        dict_properties  = ['transaction_id', 'invoice_id', 'remarks', 'tax_amount', 'transact_amount', 
                           'transact_datetime', 
                           ]
        with db_client.context():
            enquiry_date                = datetime.strptime(enquiry_date_str, '%d-%m-%Y')
                
            logger.debug('enquiry_date=%s', enquiry_date)
            result       = SalesTransaction.list_transaction_by_date(enquiry_date, transact_outlet=outlet, including_reverted_transaction=False, limit=conf.MAX_FETCH_RECORD)
            
            for r in result:
                transactions_list.append(r.to_dict(dict_properties=dict_properties,  date_format="%d-%m-%Y", datetime_format="%d-%m-%Y %H:%M:%S"))
        
        logger.debug('transactions_list=%s', transactions_list)
        
        return create_api_message(result=transactions_list,  status_code=StatusCode.OK)
        
    else:
        return create_api_message(status_code=StatusCode.BAD_REQUEST)   
