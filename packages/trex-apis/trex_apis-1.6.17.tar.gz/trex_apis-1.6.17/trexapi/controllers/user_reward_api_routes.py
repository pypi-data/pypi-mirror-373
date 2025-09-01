from flask import Blueprint, request
import logging
from trexmodel.utils.model.model_util import create_db_client
from trexmodel.models.datastore.user_models import User
from trexmodel.models.datastore.customer_models import Customer
from trexmodel.models.datastore.reward_models import CustomerEntitledTierRewardSummary, CustomerPointReward
from trexapi.decorators.api_decorators import user_auth_token_required_pass_reference_code, elapsed_time_trace
from flask.json import jsonify
from trexapi.utils.api_helpers import create_api_message, StatusCode

user_reward_api_bp = Blueprint('user_reward_api_bp', __name__,
                                 template_folder='templates',
                                 static_folder='static',
                                 url_prefix='/api/v1/user-reward')

logger = logging.getLogger('debug')


@user_reward_api_bp.route('/ping', methods=['GET'])
def ping():
    return create_api_message('OK', status_code=StatusCode.OK)

@user_reward_api_bp.route('/customer/<customer_key>/summary', methods=['GET'])
@user_auth_token_required_pass_reference_code
@elapsed_time_trace(trace_key="read_customer_reward_summary")
def read_user_reward_summary(reference_code, customer_key):
    logger.debug('reference_code=%s', reference_code)
    #vouchers_list   = []
    tier_rewards    = []
    
    db_client = create_db_client(caller_info="read_user_reward_summary")
    with db_client.context():
        customer = Customer.fetch(customer_key)
        if customer:
            customer_tier_reward_summary    = CustomerEntitledTierRewardSummary.list_tier_reward_summary_by_customer(customer)
            CustomerPointReward.list_by_customer(customer)
            '''
            if customer_vouchers_list:
                for v in customer_vouchers_list:
                    vouchers_list.append(v.to_dict())
            '''        
            if customer_tier_reward_summary:
                for v in customer_tier_reward_summary:
                    tier_rewards.append(v.to_dict())
    
    
    
    result = {
            'reference_code'    : reference_code,
            #'vouchers'          : vouchers_list,
            'tier_rewards'      : tier_rewards,
            'reward_summary'    : customer.reward_summary,
            'prepaid_summary'   : customer.prepaid_summary,
            'voucher_summary'   : customer.entitled_voucher_summary,
            }
    
    return jsonify(result)

    