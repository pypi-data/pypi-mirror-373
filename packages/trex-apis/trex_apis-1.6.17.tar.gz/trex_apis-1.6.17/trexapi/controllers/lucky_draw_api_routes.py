

import random, logging
from flask import request
from flask.blueprints import Blueprint
from trexmodel.models.datastore.lucky_draw_models import LuckyDrawTicket
from trexmodel.utils.model.model_util import create_db_client
from flask.json import jsonify
from trexlib.utils.log_util import get_tracelog
from trexmodel.models.datastore.merchant_models import MerchantAcct
from trexapi.decorators.api_decorators import user_auth_token_required
from trexmodel.models.datastore.customer_models import Customer
from trexmodel.models.datastore.model_decorators import model_transactional
from trexmodel.models.datastore.transaction_models import CustomerTransaction
from datetime import datetime
from trexmodel import program_conf
from trexprogram.reward_program.lucky_draw_program import LuckyDrawRewardProgram
from trexapi.utils.api_helpers import create_api_message, StatusCode
from trexlib.libs.flask_wtf.request_wrapper import request_headers, request_json

lucky_draw_api_bp = Blueprint('lucky_draw_api_bp', __name__,
                                 template_folder='templates',
                                 static_folder='static',
                                 url_prefix='/api/v1/lucky-draw')

logger = logging.getLogger('target_debug')

@lucky_draw_api_bp.route('/draw', methods=['GET'])
def draw():

    # Define the prizes and their respective weights (i.e., the likelihood of winning each prize)
    prizes = {"First Prize": 1, "Second Prize": 4, "Third Prize": 10, "Consolation Prize": 40, "Try again": 144}
    
    # Get the total weight of all the prizes
    total_weight = sum(prizes.values())
    
    # Generate a random number between 1 and the total weight
    random_num = random.randint(1, total_weight)
    
    # Determine the prize based on the random number and the weights of the prizes
    draw_prize = None
    for prize, weight in prizes.items():
        if random_num <= weight:
            print(f"You've won the {prize}!")
            draw_prize = prize
            break
        else:
            random_num -= weight
            
    return draw_prize, 200

@lucky_draw_api_bp.route('/<ticket_key>/draw', methods=['POST'])
#@user_auth_token_required
@request_json
def lucky_draw(request_json, ticket_key):
    
    drawed_data_in_json   = request_json#request.get_json()
    db_client = create_db_client(caller_info="lucky_draw")
    
    logger.debug('drawed_data_in_json=%s', drawed_data_in_json)
    
    selected_index = drawed_data_in_json.get('selected_index')
    
    logger.debug('selected_index=%s', selected_index)
    
    
    drawed_prize_sequence_indexes   = []
    
    try:
        with db_client.context():
            
            lucky_draw_ticket   = LuckyDrawTicket.get_by_ticket_key(ticket_key)
            logger.debug('lucky_draw_ticket=%s', lucky_draw_ticket)
        
        
        if lucky_draw_ticket:
            #lucky_draw_ticket.patch_prize_image_base_url()
            drawed_prize_sequence_indexes = lucky_draw_ticket.drawed_details.get('drawed_prize_sequence_indexes')
            ticket_image_url = lucky_draw_ticket.drawed_details.get('ticket_image_url')
            
            logger.debug('>>>>>>>>>>>>>>before draw ticket_image_url=%s', ticket_image_url)
            
            if lucky_draw_ticket.used==False:
                logger.debug('Going to draw')
                with db_client.context():
                    lucky_draw_ticket.draw(selected_index=selected_index)
                    
                drawed_prize_sequence_indexes = lucky_draw_ticket.drawed_details.get('drawed_prize_sequence_indexes')    
                    
                logger.debug('drawed_prize_sequence_indexes=%s', drawed_prize_sequence_indexes)
                
                ticket_image_url = lucky_draw_ticket.drawed_details.get('ticket_image_url')
                logger.debug('>>>>>>>>>>>>>>after draw ticket_image_url=%s', ticket_image_url)
                
                return create_api_message(status_code=StatusCode.OK, 
                                           won_prize                        = lucky_draw_ticket.drawed_details.get('won_prize'),
                                           drawed_prize_sequence_indexes    = drawed_prize_sequence_indexes,
                                           selected_index                   = lucky_draw_ticket.drawed_details.get('selected_index'),
                                           drawed_datetime                  = lucky_draw_ticket.used_datetime.strftime('%d-%m-%Y %H:%M:%s'),
                                           )
            else:
                if drawed_prize_sequence_indexes is None:
                    with db_client.context(): 
                        lucky_draw_ticket.draw_update_prize_sequence(selected_index=selected_index)
                        drawed_prize_sequence_indexes = lucky_draw_ticket.drawed_details.get('drawed_prize_sequence_indexes')
                
                with db_client.context():
                    customer_acct = lucky_draw_ticket.customer_acct_entity
                    Customer.update_ticket_into_lucky_draw_ticket_summary(customer_acct, lucky_draw_ticket.to_configuration())        
                    
                logger.debug('Ticket have been drawed already, thus return drawed details')
                
                logger.debug('drawed_prize_sequence_indexes=%s', drawed_prize_sequence_indexes)
                
                return create_api_message(status_code=StatusCode.OK, 
                                            won_prize                       = lucky_draw_ticket.drawed_details.get('won_prize'),
                                            drawed_prize_sequence_indexes   = drawed_prize_sequence_indexes,
                                            selected_index                  = lucky_draw_ticket.drawed_details.get('selected_index'),
                                            )
        else:
            return create_api_message('Invalid lucky draw ticket', status_code=StatusCode.BAD_REQUEST)
            
            
    
    except Exception as err:
        logger.error('Failed due to %s', get_tracelog())
        return create_api_message(str(err), status_code=StatusCode.BAD_REQUEST)
    
@lucky_draw_api_bp.route('/<ticket_key>/read', methods=['GET'])
#@user_auth_token_required
def read_lucky_draw(ticket_key):
    
    db_client = create_db_client(caller_info="read_lucky_draw")
    
    try:
        with db_client.context():
            
            lucky_draw_ticket   = LuckyDrawTicket.get_by_ticket_key(ticket_key)
            logger.debug('lucky_draw_ticket=%s', lucky_draw_ticket)
        
        
        if lucky_draw_ticket:
            
                
            return create_api_message(status_code=StatusCode.OK, 
                                        won_prize                       = lucky_draw_ticket.drawed_details.get('won_prize'),
                                        drawed_prize_sequence_indexes   = lucky_draw_ticket.drawed_details.get('drawed_prize_sequence_indexes'),
                                        selected_index                  = lucky_draw_ticket.drawed_details.get('selected_index'),
                                        )
        else:
            return create_api_message('Invalid lucky draw ticket', status_code=StatusCode.BAD_REQUEST)
            
            
    
    except Exception as err:
        logger.error('Failed due to %s', get_tracelog())
        return create_api_message(str(err), status_code=StatusCode.BAD_REQUEST)    
    
@lucky_draw_api_bp.route('/<ticket_key>/remove', methods=['DELETE'])
@user_auth_token_required
def remove_lucky_draw_ticket(ticket_key):

    db_client = create_db_client(caller_info="remove_lucky_draw_ticket")
    try:
        with db_client.context():
            
            lucky_draw_ticket   = LuckyDrawTicket.get_by_ticket_key(ticket_key)
            logger.debug('lucky_draw_ticket=%s', lucky_draw_ticket)
        
        
        if lucky_draw_ticket:
            with db_client.context():
                lucky_draw_ticket.remove()
        
            return create_api_message(status_code=StatusCode.ACCEPTED)
        
        else:
            return create_api_message('Invalid lucky draw ticket', status_code=StatusCode.BAD_REQUEST)
           
        return create_api_message(status_code=StatusCode.ACCEPTED)    
    
    except Exception as err:
        logger.error('Failed due to %s', get_tracelog())
        return create_api_message(str(err), status_code=StatusCode.BAD_REQUEST)   
    
@lucky_draw_api_bp.route('/<ticket_key>/grab-prize', methods=['POST'])
@user_auth_token_required
def grab_lucky_draw_prize(ticket_key):

    db_client = create_db_client(caller_info="grab_lucky_draw_prize")
    try:
        with db_client.context():
            
            lucky_draw_ticket   = LuckyDrawTicket.get_by_ticket_key(ticket_key)
            logger.debug('lucky_draw_ticket=%s', lucky_draw_ticket)
        
        
        if lucky_draw_ticket:
            
            if lucky_draw_ticket.grabbed:
                return create_api_message('Prize have been grabbed before', status_code=StatusCode.BAD_REQUEST)
            else:
                with db_client.context():
                    customer = lucky_draw_ticket.customer_acct_entity
                    __start_for_lucky_draw_prize(lucky_draw_ticket, customer)
                    
                    
                    customer = Customer.fetch(customer.key_in_str)
                    
                    user_details = customer.registered_user_acct
                    customer_details_dict = customer.to_dict(date_format="%d-%m-%Y", datetime_format="%d-%m-%Y %H:%M:%S")
                    
                    customer_details_dict['customer_key']               = customer.key_in_str
                    customer_details_dict['is_email_verified']          = user_details.is_email_verified
                    customer_details_dict['is_mobile_phone_verified']   = user_details.is_mobile_phone_verified
                    
                return create_api_message(status_code=StatusCode.OK, customer_rewards=customer_details_dict)
        else:
            return create_api_message('Invalid lucky draw ticket', status_code=StatusCode.BAD_REQUEST)
            
            
    
    except Exception as err:
        logger.error('Failed due to %s', get_tracelog())
        return create_api_message(str(err), status_code=StatusCode.BAD_REQUEST)        

@model_transactional(desc='grab_lucky_draw_prize')
def __start_for_lucky_draw_prize(lucky_draw_ticket, customer_acct):
    transact_outlet     = lucky_draw_ticket.transact_outlet_entity
    transact_datetime   = datetime.utcnow()
    
    lucky_draw_ticket.grab_the_prize(customer_acct=customer_acct)
    
    lucky_draw_prize_transaction = CustomerTransaction.create_system_transaction(
                                                        customer_acct, 
                                                        system_remarks='Lucky Draw Prize',
                                                        transact_outlet=transact_outlet, 
                                                        transact_datetime=transact_datetime, 
                                                        reward_giveaway_method=program_conf.PROGRAM_REWARD_GIVEAWAY_METHOD_SYSTEM,
                                                        is_sales_transaction = True, 
                                                        allow_to_revert=False, 
                                                        )
    
    program = LuckyDrawRewardProgram(
                drawed_details      = lucky_draw_ticket.drawed_details,
                transact_outlet     = transact_outlet,
                transaction_details = lucky_draw_prize_transaction,
                customer_acct       = customer_acct,
                )
    
    program.give()
    
    
    
@lucky_draw_api_bp.route('/<ticket_key>/view', methods=['GET'])
def view_lucky_draw(ticket_key):

    db_client = create_db_client(caller_info="lucky_draw")
    try:
        with db_client.context():
            lucky_draw_details = LuckyDrawTicket.get_by_ticket_key(ticket_key)
            if lucky_draw_details:
                #lucky_draw_details.patch_prize_image_base_url()
                lucky_draw_details = lucky_draw_details.to_dict()
        
        if lucky_draw_details:
            return jsonify(lucky_draw_details)
        else:
            return create_api_message('Fail to draw', status_code=StatusCode.BAD_REQUEST)    
    except Exception as err:
        logger.error('Failed due to %s', get_tracelog())
        return create_api_message(str(err), status_code=StatusCode.BAD_REQUEST)    


@lucky_draw_api_bp.route('/merchant/<merchant_key>/create-draw-ticket', methods=['GET'])
def create_merchant_lucky_draw_ticket(merchant_key):

    db_client = create_db_client(caller_info="create_merchant_lucky_draw_ticket")
    try:
        logger.debug('merchant_key=%s', merchant_key)
        with db_client.context():
            merchant_acct = MerchantAcct.fetch(merchant_key)
            draw_ticket = LuckyDrawTicket.create(merchant_acct)
        
        logger.debug('draw_ticket=%s', draw_ticket)
        
        if draw_ticket:
            return create_api_message(status_code=StatusCode.OK, draw_ticket=draw_ticket.to_dict())
        else:
            return create_api_message('Failed to create lucky draw ticket', status_code=StatusCode.BAD_REQUEST)    
    except Exception as err:
        logger.error('Failed due to %s', get_tracelog())
        return create_api_message(str(err), status_code=StatusCode.BAD_REQUEST)

@lucky_draw_api_bp.route('/create-draw-link', methods=['GET'])
@user_auth_token_required
@request_headers
def create_lucky_draw_link(request_headers):
    
    acct_id   = request_headers.get('x-acct-id')
    db_client = create_db_client(caller_info="create_lucky_draw_ticket")
    try:
        logger.debug('acct_id=%s', acct_id)
        with db_client.context():
            merchant_acct = MerchantAcct.fetch(acct_id)
            draw_ticket = LuckyDrawTicket.create(merchant_acct)
        
        logger.debug('draw_ticket=%s', draw_ticket)
        
        if draw_ticket:
            return create_api_message(status_code=StatusCode.OK, draw_ticket=draw_ticket.to_dict())
        else:
            return create_api_message('Failed to create lucky draw ticket', status_code=StatusCode.BAD_REQUEST)    
    except Exception as err:
        logger.error('Failed due to %s', get_tracelog())
        return create_api_message(str(err), status_code=StatusCode.BAD_REQUEST)        
        
        
        