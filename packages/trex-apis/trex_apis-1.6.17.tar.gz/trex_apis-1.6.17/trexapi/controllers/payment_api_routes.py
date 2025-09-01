import logging
from flask import request
from flask.blueprints import Blueprint
from trexlib.utils.string_util import is_not_empty
from flask_restful import abort
import stripe
import os

payment_api_bp = Blueprint('payment_api_bp', __name__,
                                 template_folder='templates',
                                 static_folder='static',
                                 url_prefix='/api/v1/payments')



logger = logging.getLogger('debug')

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
webhook_secret = os.environ.get("WEBHOOK_SECRET")

@payment_api_bp.route('/version', methods=['GET'])
def version():
    return '1.0.0', 200

@payment_api_bp.route('/stripe-webhook', methods=['POST'])
def stripe_payment():
    payload = request.data.decode("utf-8")
    received_sig = request.headers.get("Stripe-Signature", None)
    logger.debug('payload=%s', payload)
    logger.debug('received_sig=%s', received_sig)
    
    try:
        event = stripe.Webhook.construct_event(
                    payload, received_sig, webhook_secret
                )
        
        
        logger.debug('event=%s', event)
        
        return 'Success', 200
        
    except ValueError:
        logger.error("Error while decoding event!")
        return "Bad payload", 400
    
    except stripe.error.SignatureVerificationError:
        logger.error("Invalid signature!")
        return "Bad signature", 400

