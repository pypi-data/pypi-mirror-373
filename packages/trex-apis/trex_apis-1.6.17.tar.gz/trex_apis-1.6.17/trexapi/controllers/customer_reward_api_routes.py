from flask import Blueprint
import logging
from trexmodel.utils.model.model_util import create_db_client
from trexmodel.models.datastore.merchant_models import MerchantAcct
from trexmodel.models.datastore.customer_models import Customer
from trexmodel.models.datastore.reward_models import CustomerEntitledTierRewardSummary, CustomerPointReward
from trexapi.decorators.api_decorators import auth_token_required
from flask.json import jsonify
from trexapi.utils.api_helpers import StatusCode, create_api_message
from trexlib.libs.flask_wtf.request_wrapper import request_headers

customer_reward_api_bp = Blueprint('customer_reward_api_bp', __name__,
                                 template_folder='templates',
                                 static_folder='static',
                                 url_prefix='/api/v1/customers/reward')

logger = logging.getLogger('target_debug')


@customer_reward_api_bp.route('/ping', methods=['GET'])
def ping():
    return create_api_message('OK', status_code=StatusCode.OK)

@customer_reward_api_bp.route('/reference-code/<reference_code>', methods=['GET'])
@auth_token_required
@request_headers
def read_customer_reward_summary(request_headers, reference_code):
    acct_id  = request_headers.get('x-acct-id')
    
    logger.debug('reference_code=%s', reference_code)
    logger.debug('acct_id=%s', acct_id)
    
    tier_rewards    = []
    
    db_client = create_db_client(caller_info="read_customer_reward_summary")
    with db_client.context():
        merchant_acct = MerchantAcct.fetch(acct_id)
        customer = Customer.get_by_reference_code(reference_code, merchant_acct)
        if customer:
            #customer_vouchers_list          = CustomerEntitledVoucher.list_all_by_customer(customer)
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
            #'tier_rewards'      : tier_rewards,
            #'reward_summary'    : customer.reward_summary,
            #'prepaid_summary'   : customer.prepaid_summary,
            #'voucher_summary'   : customer.entitled_voucher_summary,
            }
    
    if tier_rewards:
        result['tier_rewards'] = tier_rewards
    
    if customer.reward_summary:
        result['reward_summary'] = customer.reward_summary
        
    if customer.prepaid_summary:
        result['prepaid_summary'] = customer.prepaid_summary
    
    if customer.entitled_voucher_summary:
        result['voucher_summary'] = customer.entitled_voucher_summary            
    
    return jsonify(result)

@customer_reward_api_bp.route('/reference-code/<reference_code>/give', methods=['POST'])
@auth_token_required
@request_headers
def give_customer_reward(request_headers, reference_code):
    acct_id  = request_headers.get('x-acct-id')
    logger.debug('reference_code=%s', reference_code)
    logger.debug('acct_id=%s', acct_id)
    #vouchers_list   = []
    tier_rewards    = []
    
    db_client = create_db_client(caller_info="give_customer_reward")
    with db_client.context():
        merchant_acct = MerchantAcct.fetch(acct_id)
        customer = Customer.get_by_reference_code(reference_code, merchant_acct)
        
        if customer:
            #customer_vouchers_list          = CustomerEntitledVoucher.list_all_by_customer(customer)
            customer_tier_reward_summary    = CustomerEntitledTierRewardSummary.list_tier_reward_summary_by_customer(customer)
            CustomerPointReward.list_by_customer(customer)
            
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

    