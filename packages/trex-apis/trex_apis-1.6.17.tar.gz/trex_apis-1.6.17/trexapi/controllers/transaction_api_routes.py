from flask import Blueprint
import logging
from trexapi.decorators.api_decorators import auth_token_required
from trexlib.utils.string_util import is_not_empty, is_empty
from trexmodel.models.datastore.pos_models import POSSetting
from trexmodel.utils.model.model_util import create_db_client
from datetime import datetime
from trexlib.libs.flask_wtf.request_wrapper import request_headers


#logger = logging.getLogger('api')
logger = logging.getLogger('debug')

transaction_api_bp = Blueprint('transaction_api_bp', __name__,
                                 template_folder='templates',
                                 static_folder='static',
                                 url_prefix='/api/v1/transaction')

@transaction_api_bp.route('/ping', methods=['GET'])
def ping():
    return 'pong',200

@transaction_api_bp.route('/reference-code/<reference_code>/read', methods=['GET'])
@auth_token_required
@request_headers
def list_customer_transaction():
    
    db_client = create_db_client(caller_info="list_customer_transaction")
    
    