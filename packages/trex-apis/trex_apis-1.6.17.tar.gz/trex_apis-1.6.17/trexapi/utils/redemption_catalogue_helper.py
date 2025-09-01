'''
Created on 17 Dec 2023

@author: jacklok
'''

from datetime import datetime, date
from trexmodel import program_conf
from dateutil.relativedelta import relativedelta
import logging
from trexprogram.reward_program.reward_program_base import EntitledVoucherSummary
from trexmodel.models.datastore.voucher_models import MerchantVoucher
from trexmodel.models.datastore.reward_models import CustomerEntitledVoucher
from trexlib.utils.string_util import is_not_empty
from trexmodel.models.datastore.model_decorators import model_transactional
from trexmodel.utils.model.model_util import generate_transaction_id
from trexmodel.models.datastore.redeem_models import RedemptionCatalogueTransaction,\
    CustomerRedemption
from trexanalytics.bigquery_upstream_data_config import create_partnership_transaction_upstream_for_merchant
from trexmodel.models.datastore.customer_model_helpers import update_customer_entiteld_voucher_summary_with_customer_new_voucher
from trexmodel.models.datastore.message_model_helper import create_redeem_catalogue_item_message
from trexprogram.utils.reward_program_helper import calculate_effective_date,\
    calculate_expiry_date
from trexconf.program_conf import REWARD_PROGRAM_DATE_FORMAT
from google.cloud import ndb
from trexmodel.models.datastore.merchant_models import Outlet
from trexmodel.models.datastore.customer_models import Customer
from trexmodel.models.datastore.partnership_models import PartnershipRewardTransaction

logger = logging.getLogger('helper')

@model_transactional(desc='giveaway_redeem_catalogue_item')
def giveaway_redeem_catalogue_item(customer, redeem_item_details, redeem_reward_format, 
                                   redemption_catalogue_key, voucher_key, transaction_id=None, 
                                   is_partnership_redemption=False, partner_merchant_acct=None):
    redeemed_datetime       = datetime.utcnow()
    redeem_reward_amount    = redeem_item_details.get('redeem_reward_amount')
    
    if redeem_reward_format in (program_conf.REWARD_FORMAT_POINT,program_conf.REWARD_FORMAT_STAMP) :
        reward_summary      = customer.reward_summary
        
        logger.debug('********************************')
        logger.debug('customer reward_summary=%s', reward_summary)
        logger.debug('********************************')
        
        
        
        if is_partnership_redemption==False and reward_summary.get(redeem_reward_format).get('amount') < redeem_reward_amount:
            raise Exception('Not sufficient reward amount to redeem')
    
        else:
            if transaction_id is None:
                transaction_id = generate_transaction_id(prefix='r')
                
            redemption_catalogue_transction_summary = {
                                                        'redemption_catalogue_key'  : redemption_catalogue_key,
                                                        'voucher_key'               : voucher_key,
                                                        
                                                        }
            
            if is_partnership_redemption==False:
                CustomerRedemption.create(customer, 
                                    reward_format                           = redeem_reward_format,
                                    redeemed_amount                         = redeem_reward_amount,
                                    redeemed_datetime                       = redeemed_datetime, 
                                    transaction_id                          = transaction_id,
                                    redemption_catalogue_transction_summary = redemption_catalogue_transction_summary,
                                    is_partnership_redemption               = is_partnership_redemption,
                                    )
            
            redemption_catalogue_transaction = RedemptionCatalogueTransaction.create(
                                                  ndb.Key(urlsafe=redemption_catalogue_key).get(),
                                                  voucher_key, 
                                                  customer,
                                                  transaction_id,
                                                  redeemed_datetime,
                                                  reward_format=redeem_reward_format,
                                                  redeem_reward_amount=redeem_reward_amount,
                                                  )
            
            reward_summary = __giveaway_voucher_from_redemption_catalogue_item(customer, redeem_item_details, transaction_id, redeemed_datetime, partner_merchant_acct=partner_merchant_acct)
            
            create_redeem_catalogue_item_message(customer, reward_summary.entitled_voucher_summary, redemption_catalogue_transaction)
            
            return reward_summary
                


def __giveaway_voucher_from_redemption_catalogue_item(customer, redeem_item_details, transaction_id, transact_datetime, partner_merchant_acct=None):
    logger.debug('---__giveaway_voucher_from_redemption_catalogue_item---')
    
    voucher_key             = redeem_item_details.get('voucher_key')
    effective_type          = redeem_item_details.get('effective_type')
    effective_value         = redeem_item_details.get('effective_value')
    effective_date_str      = redeem_item_details.get('effective_date')
    
    if effective_type == program_conf.REWARD_EFFECTIVE_TYPE_SPECIFIC_DATE:
        if is_not_empty(effective_date_str):
            effective_date = datetime.strptime(effective_date_str, REWARD_PROGRAM_DATE_FORMAT)
    else:
        effective_date = calculate_effective_date(effective_type, effective_value, start_date = transact_datetime)
    
    expiration_type         = redeem_item_details.get('expiration_type')
    expiration_value        = redeem_item_details.get('expiration_value')
     
    expiry_date             = calculate_expiry_date(expiration_type, expiration_value, start_date=effective_date)
    
    voucher_amount          = redeem_item_details.get('voucher_amount')
    
    merchant_voucher = MerchantVoucher.fetch(voucher_key)
    customer_entitled_voucher_list = []
    reward_summary = EntitledVoucherSummary(transaction_id=transaction_id)
    
    logger.debug('merchant_voucher=%s', merchant_voucher)
    logger.debug('voucher_amount=%s', voucher_amount)
    
    if merchant_voucher:
        entitled_voucher_summary = customer.entitled_voucher_summary or {}
        
        logger.debug('entitled_voucher_summary=%s', entitled_voucher_summary)
        
        for v in range(voucher_amount):
            customer_entitled_voucher = CustomerEntitledVoucher.create(
                                                            merchant_voucher,
                                                            customer, 
                                                            transaction_id          = transaction_id,
                                                            rewarded_datetime       = transact_datetime,
                                                            effective_date          = effective_date,
                                                            expiry_date             = expiry_date,
                                                            partner_merchant_acct   = partner_merchant_acct,
                                                            )
            
            logger.debug('customer_entitled_voucher=%s', customer_entitled_voucher)
            
            update_customer_entiteld_voucher_summary_with_customer_new_voucher(entitled_voucher_summary, customer_entitled_voucher)
            customer_entitled_voucher_list.append(customer_entitled_voucher)
        
        customer.entitled_voucher_summary = entitled_voucher_summary    
        customer.put()
        
        reward_summary.add(merchant_voucher, 
                                   customer_entitled_voucher_list) 
        
    return reward_summary

def __get_redemption_voucher_label(partner_merchant_acct, voucher_key):
    published_voucher_configuration = partner_merchant_acct.published_voucher_configuration
    for voucher_details in published_voucher_configuration.get('vouchers'):
        if voucher_details.get('voucher_key') == voucher_key:
            return voucher_details.get('label')
    return ''


@model_transactional(desc='_giveaway_redemption_catalogue_item_to_partner_customer_and_transfer_reward_to_partner_customer')
def giveaway_redemption_catalogue_item_to_partner_customer_and_transfer_reward_to_partner_customer(
        merchant_acct, partner_merchant_acct, merchant_customer, redeem_item_details, redeem_reward_format, redemption_catalogue_key, voucher_key,
        ):
    hq_outlet       = Outlet.get_head_quarter_outlet(partner_merchant_acct)
    if hq_outlet is None:
        raise Exception('The merchant do not have head quarter outlet')
    else:
        logger.info('hq_outlet=%s', hq_outlet)
        
        if redeem_item_details:
            user_acct               = merchant_customer.registered_user_acct
            transact_datetime       = datetime.utcnow()
            redeem_reward_amount    = redeem_item_details.get('redeem_reward_amount')
            
            logger.info('redeem_reward_amount=%s', redeem_reward_amount)
            
            partner_customer = Customer.get_by_reference_code(user_acct.reference_code, partner_merchant_acct)
            if partner_customer is None:
                partner_customer = Customer.create_from_user(hq_outlet, user_acct, merchant_acct=partner_merchant_acct)
                logger.info('Partner customer account have been created')
            
            if partner_customer is not None:
                
                logger.info('Partner customer_reward_summary=%s', partner_customer.reward_summary)
                logger.info('Merchant customer_reward_summary=%s', merchant_customer.reward_summary)
                
                voucher_label = __get_redemption_voucher_label(partner_merchant_acct, voucher_key)
                customer_redemption = CustomerRedemption.create(merchant_customer, 
                                        reward_format                           = redeem_reward_format,
                                        redeemed_amount                         = redeem_reward_amount,
                                        redeemed_datetime                       = transact_datetime, 
                                        is_partnership_redemption               = True,
                                        is_allow_to_revert                      = True,
                                        remarks                                 = 'This partnership point redemption, where point have been transferred to %s for %s entitlement' % (partner_merchant_acct.brand_name, voucher_label),
                                    )
                
                transaction_id = customer_redemption.transaction_id
                
                logger.info('transaction_id=%s', transaction_id)
                
                reward_summary = giveaway_redeem_catalogue_item(partner_customer, redeem_item_details, redeem_reward_format, 
                                                       redemption_catalogue_key, voucher_key,
                                                       is_partnership_redemption    = True,
                                                       transaction_id               = transaction_id,
                                                       partner_merchant_acct        = merchant_acct,
                                                       )
                
                logger.info('Partner customer redeemed item have been giveaway')
                
                
                
                
                
                partnership_reward_transaction = PartnershipRewardTransaction.create(merchant_acct, partner_merchant_acct, 
                                                    user_acct, redeem_reward_amount,
                                                    reward_summary  = reward_summary,
                                                    )
                
                logger.info('Partnership reward transaction have been created')
                
                create_partnership_transaction_upstream_for_merchant(partnership_reward_transaction)
                
                return merchant_customer    
        else:
            raise Exception('Redeem item is not found')