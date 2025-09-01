'''
Created on 7 Jul 2021

@author: jacklok
'''

from flask import Blueprint
import logging
from trexlib.utils.log_util import get_tracelog
from trexmodel.utils.model.model_util import create_db_client
from datetime import datetime, timedelta
from trexlib.utils.string_util import is_not_empty, random_number, random_string,\
    is_empty, boolify
from trexmodel.models.datastore.user_models import User
from trexapi.utils.api_helpers import StatusCode, create_api_message,\
    encrypt_user_auth_token
from werkzeug.datastructures import ImmutableMultiDict
from trexapi.forms.user_api_forms import UserRegistrationForm, UserUpdateForm,\
    OutletReviewsForm, UserStatusForm
from trexconf.conf import APPLICATION_NAME, APPLICATION_BASE_URL, MOBILE_APP_NAME,\
    USE_VERIFICATION_REQUEST_ID, SEND_REAL_MESSAGE, MOBILE_PHONE_EXPIRY_LENGTH_IN_MINUTE, EMAIL_EXPIRY_LENGTH_IN_MINUTE
from trexmail.email_helper import trigger_send_email
from trexmodel.models.datastore.merchant_models import MerchantAcct, Outlet
from trexmodel.models.datastore.customer_models import Customer
from trexmodel.models.datastore.reward_models import CustomerEntitledVoucher,\
    CustomerPointReward, CustomerEntitledTierRewardSummary
from trexapi.utils.api_helpers import generate_user_auth_token
from trexapi.decorators.api_decorators import user_auth_token_required,\
    show_request_info,\
    user_auth_token_required_and_check_duplicated_session,\
    user_auth_token_required_pass_reference_code
from flask.json import jsonify
from trexconf.conf import PRODUCTION_MODE, DEPLOYMENT_MODE, DEMO_MODE
from flask_babel import gettext
from trexconf import conf as model_conf
import os
from trexlib.utils.sms_util import send_sms
from trexmodel.models.datastore.message_models import Message
from trexlib.utils.common.date_util import from_utc_datetime_to_local_datetime
from trexmodel.conf import USER_STATUS_REGISTERED, GENDER_UNKNOWN_CODE
from trexmodel.models.datastore.model_decorators import model_transactional
from trexlib.libs.facebook.util.whatsapp_util import send_whatsapp_verification_message
from trexanalytics.bigquery_upstream_data_config import create_merchant_registered_customer_upstream_for_merchant,\
    create_registered_customer_upstream_for_system
from trexlib.libs.flask_wtf.request_wrapper import request_json, request_headers,\
    request_values, request_args, request_debug
from trexprogram.referral.referral_program import giveaway_referral_program_reward
from trexlib.utils.crypto_util import decrypt_json
from trexapi.utils.push_notification_helper import create_push_notification
from trexmodel.models.datastore.helper.reward_transaction_helper import check_user_joined_merchant_birthday_reward
from trexmodel.models.datastore.transaction_models import CustomerTransaction
from trexmodel.models.datastore.redeem_models import CustomerRedemption
from trexapi.libs.api_decorator import elapsed_time_trace
from trexmodel.models.merchant_helpers import return_customer_details

user_api_bp = Blueprint('user_api_bp', __name__,
                                 template_folder='templates',
                                 static_folder='static',
                                 url_prefix='/api/v1/users')

#logger = logging.getLogger('api')
logger = logging.getLogger('target_debug')


@user_api_bp.route('/ping', methods=['GET'])
@user_auth_token_required_and_check_duplicated_session()
def ping(reference_code):
    return create_api_message(reference_code=reference_code, status_code=StatusCode.OK)
    

@user_api_bp.route('/guest-register', methods=['POST'])
@request_json
@request_headers
def guest_register(user_data_in_json, request_headers):
    logger.debug('---guest_register---')
    
    try:
        #user_data_in_json   = request.get_json()
        device_id           = request_headers.get('x-device-id', random_string(12, True))
        logger.debug('guest_register: user_data_in_json=%s', user_data_in_json)
        
        register_user_form  = UserRegistrationForm(ImmutableMultiDict(user_data_in_json))
        if register_user_form.validate():
            logger.debug('guest_register:  registration input is valid')
            db_client = create_db_client(caller_info="guest_register")
            
            registered_user_acct    = None
            
            with db_client.context():
                name            = register_user_form.name.data
                
                logger.debug('name=%s', name)
                
                registered_user_acct = User.create(name=name)
                        
                
                                
            if registered_user_acct is not None:
                
                token                       = generate_user_auth_token(registered_user_acct.user_id, registered_user_acct.reference_code, device_id)
                encrypted_auth_token        = encrypt_user_auth_token(token)
                
                return create_api_message(status_code=StatusCode.OK, 
                                           auth_token                           = encrypted_auth_token,
                                           reference_code                       = registered_user_acct.reference_code,
                                           )
            else:
                return create_api_message(status_code=StatusCode.BAD_REQUEST)
            
        else:
            logger.warn('user_register: user registration input is invalid')
            error_message = register_user_form.create_rest_return_error_message()
            
            return create_api_message(error_message, status_code=StatusCode.BAD_REQUEST)
            
    except:
        logger.error('user_register: Fail to register user due to %s', get_tracelog())
        
        return create_api_message(status_code=StatusCode.BAD_REQUEST)
    
def _user_register(user_data_in_json, request_headers):
    
    try:
        #user_data_in_json   = request.get_json()
        device_id           = request_headers.get('x-device-id', random_string(12, True))
        logger.debug('user_register: device_id=%s', device_id)
        logger.debug('user_register: user_data_in_json=%s', user_data_in_json)
        
        register_user_form  = UserRegistrationForm(ImmutableMultiDict(user_data_in_json))
        if register_user_form.validate():
            logger.debug('user_register:  registration input is valid')
            
            
            
            email           = register_user_form.email.data
            name            = register_user_form.name.data
            mobile_phone    = register_user_form.mobile_phone.data
            birth_date      = register_user_form.birth_date.data
            gender          = register_user_form.gender.data
            password        = register_user_form.password.data
            status          = register_user_form.status.data
            referrer_code   = register_user_form.referrer_code.data
            
            if is_not_empty(birth_date):
                birth_date = datetime.strptime(birth_date, '%d-%m-%Y')
            else:
                birth_date = None
                
            if is_empty(gender):
                gender = model_conf.GENDER_UNKNOWN_CODE
            
            logger.debug('email=%s', email)
            logger.debug('name=%s', name)
            logger.debug('mobile_phone=%s', mobile_phone)
            logger.debug('birth_date=%s', birth_date)
            logger.debug('gender=%s', gender)
            logger.debug('password=%s', password)
            logger.debug('status=%s', status)
            logger.debug('referrer_code=%s', referrer_code)
            
            checking_registered_user_acct = None
            
            if is_not_empty(email):
                checking_registered_user_acct = User.get_by_email(email)
            #elif is_not_empty(mobile_phone):
            #    checking_registered_user_acct = User.get_by_mobile_phone(mobile_phone)
                
            if checking_registered_user_acct is None:
                if is_not_empty(mobile_phone):
                    checking_registered_user_acct = User.get_by_mobile_phone(mobile_phone)
                    if checking_registered_user_acct is None:
                        registered_user_acct = User.create(
                                                            name                        = name, 
                                                            email                       = email, 
                                                            mobile_phone                = mobile_phone, 
                                                            birth_date                  = birth_date,
                                                            gender                      = gender,
                                                            password                    = password, 
                                                            is_email_verified           = True, 
                                                            is_mobile_phone_verified    = True,
                                                            status                      = USER_STATUS_REGISTERED,
                                                           )
                        logger.debug('new registered_user_acct=%s', registered_user_acct)
                    else:
                        if checking_registered_user_acct.is_mobile_phone_verified==True:
                            return create_api_message('Mobile Phone have been taken', status_code=StatusCode.BAD_REQUEST)
                else:
                    
                    registered_user_acct = User.create(
                                                            name                = name, 
                                                            email               = email, 
                                                            birth_date          = birth_date,
                                                            gender              = gender,
                                                            password            = password, 
                                                            is_email_verified   = True,
                                                            status              = USER_STATUS_REGISTERED,
                                                           )
                    
                    
                    logger.debug('new registered_user_acct=%s', registered_user_acct)
                    
            else:
                #return create_api_message('Email have been taken', status_code=StatusCode.BAD_REQUEST)
                raise Exception(gettext('Email have been taken'))
                
            token                       = generate_user_auth_token(registered_user_acct.user_id, registered_user_acct.reference_code, device_id)
            registered_user_acct.signin_device_session = token
            registered_user_acct.put()
            
            return registered_user_acct
            
            
        else:
            logger.warn('user_register: user registration input is invalid')
            error_message = register_user_form.create_rest_return_error_message()
            
            #return create_api_message(error_message, status_code=StatusCode.BAD_REQUEST)
            raise Exception(gettext(error_message))
            
    except:
        logger.error('user_register: Fail to register user due to %s', get_tracelog())
        
        #return create_api_message(status_code=StatusCode.BAD_REQUEST)
        raise

@user_api_bp.route('/register', methods=['POST'])
@user_api_bp.route('/user-register', methods=['POST'])
@request_json
@request_headers
def user_register(user_data_in_json, request_headers):
    logger.debug('---user_register---')
    try:
        
        db_client = create_db_client(caller_info="user_register")
        with db_client.context():
            
            registered_user_acct    = _user_register(user_data_in_json, request_headers)
        
            #token                       = generate_user_auth_token(registered_user_acct.user_id, registered_user_acct.reference_code, device_id)
            token                       = registered_user_acct.signin_device_session
            encrypted_auth_token        = encrypt_user_auth_token(token)
            
            registered_user_acct.signin_device_session = token
            registered_user_acct.put()
            
            logger.debug('token=%s', token)
            logger.debug('encrypted_auth_token=%s', encrypted_auth_token)
        
        return create_api_message(status_code=StatusCode.OK, 
                                   auth_token                           = encrypted_auth_token,
                                   reference_code                       = registered_user_acct.reference_code,
                                   email_vc_expiry_datetime             = registered_user_acct.email_vc_expiry_datetime.strftime('%d-%m-%Y %H:%M:%S') if registered_user_acct.email_vc_expiry_datetime is not None else None,
                                   mobile_phone_vc_expiry_datetime      = registered_user_acct.mobile_phone_vc_expiry_datetime.strftime('%d-%m-%Y %H:%M:%S') if registered_user_acct.mobile_phone_vc_expiry_datetime is not None else None,
                                   status                               = registered_user_acct.status,
                                   )
    except Exception as e:
        return create_api_message(str(e), status_code=StatusCode.BAD_REQUEST)
    
    
    
@user_api_bp.route('/customer-register', methods=['POST'])
@request_json
@request_headers
def customer_register(user_data_in_json, request_headers):
    logger.debug('---customer_register---')
    
    try:
        db_client = create_db_client(caller_info="_customer_register")
    
        with db_client.context():
            registered_user_acct    = _customer_register(user_data_in_json, request_headers)
        
        token                   = registered_user_acct.signin_device_session
        encrypted_auth_token    = encrypt_user_auth_token(token)
        
        logger.debug('token=%s', token)
        logger.debug('encrypted_auth_token=%s', encrypted_auth_token)
        
        return create_api_message(status_code=StatusCode.OK, 
                                   auth_token                           = encrypted_auth_token,
                                   reference_code                       = registered_user_acct.reference_code,
                                   email_vc_expiry_datetime             = registered_user_acct.email_vc_expiry_datetime.strftime('%d-%m-%Y %H:%M:%S') if registered_user_acct.email_vc_expiry_datetime is not None else None,
                                   mobile_phone_vc_expiry_datetime      = registered_user_acct.mobile_phone_vc_expiry_datetime.strftime('%d-%m-%Y %H:%M:%S') if registered_user_acct.mobile_phone_vc_expiry_datetime is not None else None,
                                   status                               = registered_user_acct.status,
                                   )
          
    except Exception as e:
        return create_api_message(str(e), status_code=StatusCode.BAD_REQUEST)  

#@model_transactional(desc="register_cusomer")
def _customer_register(user_data_in_json, request_headers):
    merchant_acct_key       = request_headers.get('x-acct-id', )
    merchant_acct_code      = request_headers.get('x-acct-code', )
    device_id               = request_headers.get('x-device-id', random_string(12, True))
    registered_user_acct    = _user_register(user_data_in_json, request_headers)
    
    referrer_code   = user_data_in_json.get('referrer_code')
    
    logger.info('_customer_register info: merchant_acct_key=%s', merchant_acct_key)
    logger.info('_customer_register info: merchant_acct_code=%s', merchant_acct_code)
    logger.info('_customer_register info: referrer_code=%s', referrer_code)
    
    token                   = generate_user_auth_token(registered_user_acct.user_id, registered_user_acct.reference_code, device_id)
    
    registered_user_acct.signin_device_session = token
    registered_user_acct.put()
    
    if is_not_empty(merchant_acct_key):
        merchant_acct           = MerchantAcct.get_or_read_from_cache(merchant_acct_key)
    elif is_not_empty(merchant_acct_code):
        merchant_acct           = MerchantAcct.get_by_account_code(merchant_acct_code)
    
    if merchant_acct:   
        referrer_customer_acct  = None
        outlet                  = None
        if is_not_empty(referrer_code):
            referrer_user_acct      = User.get_by_referral_code(referrer_code)
            if referrer_user_acct:
                referrer_customer_acct  = Customer.get_by_reference_code(referrer_user_acct.reference_code, merchant_acct)
                if referrer_customer_acct:
                    outlet                  = referrer_customer_acct.registered_outlet
                    if outlet:
                        logger.info('referrer registered outlet=%s', outlet.name)
                    else:
                        logger.info('referrer registered outlet is None')
                else: 
                    raise Exception(gettext('Your friend account is invalid'))
            else:
                raise Exception(gettext('Invalid invitation code'))
        if outlet is None:    
            outlet                  = Outlet.get_head_quarter_outlet(merchant_acct)
            if outlet:
                logger.info('merchant headquarter outlet=%s', outlet.name)
            else:
                logger.info('merchant headquarter outlet is None')
        
        if outlet:
            created_customer        = Customer.create_from_user(outlet, registered_user_acct, )
            
            if created_customer is None:
                raise Exception(gettext('Failed to register customer'))
            else:
                if is_not_empty(referrer_code) and referrer_customer_acct:
                    created_customer.referrer_code = referrer_code
                    created_customer.put()
                    user_acct = created_customer.registered_user_acct
                    logger.debug('registerd user_acct=%s', user_acct)
                    
                    if user_acct:
                        giveaway_referral_program_reward(merchant_acct, 
                                         created_customer, 
                                         referrer_customer_acct, 
                                         outlet, 
                                         create_upstream=True
                                         )
        else:
            raise Exception(gettext('Missing Headquarter outlet'))
    
        return registered_user_acct
    else:
        raise Exception(gettext('Missing merchant account data'))

@user_api_bp.route('/update', methods=['POST'])
@user_auth_token_required_and_check_duplicated_session()
@request_json
def user_update(user_data_in_json, reference_code):
    logger.debug('user_update: ---user_register---')
    
    try:
        #user_data_in_json   = request.get_json()
        logger.debug('user_update: user_data_in_json=%s', user_data_in_json)
        
        update_user_form  = UserUpdateForm(ImmutableMultiDict(user_data_in_json))
        if update_user_form.validate():
            logger.debug('update_user_form:  update input is valid')
            db_client = create_db_client(caller_info="user_update")
            
            with db_client.context():
                reference_code  = update_user_form.reference_code.data
                name            = update_user_form.name.data
                email           = update_user_form.email.data
                mobile_phone    = update_user_form.mobile_phone.data
                birth_date      = update_user_form.birth_date.data
                gender          = update_user_form.gender.data
                status          = update_user_form.status.data
                
                if is_not_empty(birth_date):
                    birth_date = datetime.strptime(birth_date, '%d-%m-%Y')
                else:
                    birth_date = None
                    
                if is_empty(gender):
                    gender = GENDER_UNKNOWN_CODE    
                
                
                logger.debug('reference_code=%s', reference_code)
                logger.debug('name=%s', name)
                logger.debug('email=%s', email)
                logger.debug('mobile_phone=%s', mobile_phone)
                logger.debug('birth_date=%s', birth_date)
                logger.debug('gender=%s', gender)
                logger.debug('status=%s', status)
                
                user_acct = User.get_by_reference_code(reference_code)
                if user_acct:
                    
                    original_mobile_phone   = user_acct.mobile_phone
                    original_email          = user_acct.email
                    
                    is_gender_changed       = user_acct.gender!=gender
                    is_dob_changed          = user_acct.birth_date!=birth_date
                    is_name_changed         = user_acct.name!=name
                    is_mobile_phone_changed = original_mobile_phone!=mobile_phone
                    is_email_changed        = original_email!=mobile_phone
                    
                    update_upstream = is_gender_changed or is_dob_changed
                    
                    update_user_data        =  is_gender_changed or is_dob_changed or is_name_changed or is_mobile_phone_changed or is_email_changed
                    
                    if update_user_data and is_not_empty(mobile_phone):
                        logger.debug('going to update user details with mobile phone=%s', mobile_phone)
                        if is_mobile_phone_changed:
                            logger.debug('mobile phone have been changed thus going to check whether new mobile phone is taken or not')
                            checking_mobile_phone_user_acct = User.get_by_mobile_phone(mobile_phone)
                            
                            if checking_mobile_phone_user_acct is None:
                                logger.debug('mobile phone is not taken')
                                
                                '''
                                _update_user_acct(user_acct, 
                                            mobile_phone    = mobile_phone,
                                            name            = name,
                                            birth_date      = birth_date,
                                            gender          = gender,
                                            status          = status,
                                            update_upstream = update_upstream,
                                            ) 
                                '''
                            else:
                                if user_acct.reference_code != checking_mobile_phone_user_acct.reference_code:
                                    return create_api_message(gettext('Mobile Phone have been taken'), status_code=StatusCode.BAD_REQUEST)
                            
                    if update_user_data and is_not_empty(email):
                        logger.debug('going to update user details with email=%s', email)
                        if is_email_changed:
                            logger.debug('mobile phone have been changed thus going to check whether new mobile phone is taken or not')
                            checking_email_user_acct = User.get_by_email(email)
                            
                            if checking_email_user_acct is None:
                                logger.debug('email is not taken')
                                
                                '''
                                _update_user_acct(user_acct, 
                                            mobile_phone    = mobile_phone,
                                            name            = name,
                                            birth_date      = birth_date,
                                            gender          = gender,
                                            status          = status,
                                            update_upstream = update_upstream,
                                            ) 
                                '''
                            else:
                                if user_acct.reference_code != checking_email_user_acct.reference_code:
                                    return create_api_message(gettext('Mobile Phone have been taken'), status_code=StatusCode.BAD_REQUEST)
                        
                                
                    
                    
                    
                    if update_user_data:
                        logger.debug('going to update user details')
                        
                        update_dict = {
                                        'name'              : name,
                                        'email'             : email,
                                        'mobile_phone'      : mobile_phone,
                                        'birth_date'        : birth_date,     
                                        'gender'            : gender,
                                        'update_upstream'   : update_upstream,
                                        'status'            : status,
                                        }
                        '''    
                        if is_dob_changed:
                            update_dict['birth_date'] = birth_date
                            
                        if is_name_changed:
                            update_dict['name'] = name
                            
                        if is_mobile_phone_changed:
                            update_dict['mobile_phone'] = mobile_phone
                            
                        if is_email_changed:
                            update_dict['email'] = email
                        '''
                        logger.debug('update_dict=%s', update_dict)
                        
                        if is_dob_changed:
                            check_user_joined_merchant_birthday_reward(user_acct)
                        
                        _update_user_acct(user_acct, 
                                            **update_dict
                                            )
                        
                    
                else:
                    return create_api_message('User account is not found', status_code=StatusCode.BAD_REQUEST)
                
                                
            return create_api_message(status_code=StatusCode.OK)
            
        else:
            logger.warn('user_register: user registration input is invalid')
            error_message = update_user_form.create_rest_return_error_message()
            
            return create_api_message(error_message, status_code=StatusCode.BAD_REQUEST)
            
    except:
        logger.error('user_register: Fail to update user due to %s', get_tracelog())
        
        return create_api_message('Failed to update user account', status_code=StatusCode.BAD_REQUEST)

@model_transactional(desc="_update_user_account")
def _update_user_acct(user_acct, email=None, mobile_phone=None, name=None, birth_date=None, gender=None, status=None, update_upstream=True):
    User.update(user_acct, 
            email           = email,    
            mobile_phone    = mobile_phone,
            name            = name,
            birth_date      = birth_date,
            gender          = gender,
            status          = status,
            )  
    __update_customer_data(user_acct, update_upstream=update_upstream)
    

def __update_customer_data(user_acct, update_upstream=True):
    
    customer_acct_list = Customer.list_by_user_account(user_acct)
    if customer_acct_list:
        for c in customer_acct_list:
            c.update_from_user_acct(user_acct)
            
            if update_upstream:
                create_merchant_registered_customer_upstream_for_merchant(c)
                create_registered_customer_upstream_for_system(c)    
    
@user_api_bp.route('/update-status', methods=['PUT'])
@request_headers
@request_json
def user_update_status(request_headers, user_data_in_json):
    logger.debug('---user_update_status---')
    
    reference_code      = request_headers.get('x-reference-code')
    
    try:
        #user_data_in_json   = request.get_json()
        logger.debug('user_update_status: user_data_in_json=%s', user_data_in_json)
        
        update_user_status_form  = UserStatusForm(ImmutableMultiDict(user_data_in_json))
        if update_user_status_form.validate():
            logger.debug('update_user_status_form:  update input is valid')
            db_client = create_db_client(caller_info="user_update_status")
            
            with db_client.context():
                user = User.get_by_reference_code(reference_code)
                user.status = update_user_status_form.status.data
                user.put()
                
            return create_api_message(status_code=StatusCode.ACCEPTED)

    except:
        logger.error('Fail to update user status due to %s', get_tracelog())
        
        return create_api_message(status_code=StatusCode.BAD_REQUEST)
        
@user_api_bp.route('/account-auth', methods=['POST'])
@user_auth_token_required_and_check_duplicated_session()
@request_json
def account_auth(user_data_in_json, reference_code):
    logger.debug('reference_code=%s', reference_code)
    logger.debug('user_data_in_json=%s', user_data_in_json)
    password            = user_data_in_json.get('password')
    db_client = create_db_client(caller_info="account_auth")
    account_is_valid = False
    with db_client.context():
        user_acct = User.get_by_reference_code(reference_code)
        if user_acct.is_valid_password(password):
            account_is_valid = True
    
    if account_is_valid:
        
        return create_api_message(status_code=StatusCode.OK)
    else:
        return create_api_message("You are not authorized to proceed", status_code=StatusCode.BAD_REQUEST)
            
    

        
@user_api_bp.route('/email-auth', methods=['POST'])
@request_json
@request_headers
def auth_user_thru_email(user_data_in_json, request_headers):
    
    #user_data_in_json   = request.get_json()
    email               = user_data_in_json.get('email')
    password            = user_data_in_json.get('password')
    device_id           = request_headers.get('x-device-id', random_string(12, True))
    
    logger.debug('request_headers=%s', request_headers)
    
    logger.debug('email=%s', email)
    logger.debug('password=%s', password)
    logger.debug('device_id=%s', device_id)
    
    if is_not_empty(email) and is_not_empty(password):
        db_client = create_db_client(caller_info="auth_user")
        user_acct = None
        with db_client.context():
            user_acct = User.get_by_email(email)
        
        if user_acct:
            
            logger.debug('auth_user: found user account by email=%s', email)    
            logger.debug('auth_user: found user account by password=%s', password)
            
            if user_acct.is_still_lock:
                return create_api_message('User account is locked after many trials for security purpose. Please try after an hour', status_code=StatusCode.BAD_REQUEST)
            else:
                if user_acct.deleted:
                    return create_api_message('User email or password is invalid', status_code=StatusCode.BAD_REQUEST)
                else:
                    if user_acct.is_valid_password(password):
                    
                        token                       = generate_user_auth_token(user_acct.user_id, user_acct.reference_code, device_id)
                        encrypted_auth_token        = encrypt_user_auth_token(token)
                        
                        logger.debug('auth_user debug: token=%s', token)
                        
                        with db_client.context():
                            user_acct.signin_device_session = token
                            user_acct.last_login_datetime = datetime.utcnow()
                            user_acct.put()
                        
                        response_data = {
                                            'auth_token'      : encrypted_auth_token,
                                            'expiry_datetime' : token.get('expiry_datetime'),
                                            'device_id'       : device_id,
                                            }
                            
                        response_data.update(user_details_dict(user_acct))
                        
                        logger.debug('auth_user debug: response_data=%s', response_data)
                        
                        return create_api_message(status_code=StatusCode.OK, 
                                                   **response_data
                                                   
                                                   )
                    else:
                        
                        logger.warn('auth_user: user password is invalid')
                        with db_client.context():
                            user_acct.add_try_count()
                        
                        return create_api_message('User email or password is not match', status_code=StatusCode.BAD_REQUEST)
            
        else:
            return create_api_message('User email or password is not match', status_code=StatusCode.BAD_REQUEST)
            
    else:
        logger.warn('auth_user: user verify input is invalid')
        return create_api_message('Missing email or password', status_code=StatusCode.BAD_REQUEST)
    
@user_api_bp.route('/mobile-phone-auth', methods=['POST'])
@request_json
@request_headers
def auth_user_thru_mobile_phone(user_data_in_json, request_headers):
    
    #user_data_in_json   = request.get_json()
    mobile_phone        = user_data_in_json.get('mobile_phone')
    password            = user_data_in_json.get('password')
    device_id           = request_headers.get('x-device-id', random_string(12, True))
    
    logger.debug('mobile_phone=%s', mobile_phone)
    logger.debug('password=%s', password)
    logger.debug('device_id=%s', device_id)
    
    if is_not_empty(mobile_phone) and is_not_empty(password):
        db_client = create_db_client(caller_info="auth_user")
        user_acct = None
        with db_client.context():
            user_acct = User.get_by_mobile_phone(mobile_phone)
        
        if user_acct:
            
            logger.debug('auth_user: found user account by mobile_phone=%s', mobile_phone)    
            logger.debug('auth_user: found user account by password=%s', password)
            
            if user_acct.is_still_lock:
                return create_api_message('User account is locked after many trials for security purpose. Please try after an hour', status_code=StatusCode.BAD_REQUEST)
            else:
                if user_acct.deleted:
                    return create_api_message('User mobile phone or password is invalid', status_code=StatusCode.BAD_REQUEST)
                else:
                    if user_acct.is_valid_password(password):
                    
                        token                       = generate_user_auth_token(user_acct.user_id, user_acct.reference_code, device_id)
                        encrypted_auth_token        = encrypt_user_auth_token(token)
                        
                        logger.debug('auth_user debug: token=%s', token)
                        
                        with db_client.context():
                            user_acct.signin_device_session = token
                            user_acct.last_login_datetime = datetime.utcnow()
                            user_acct.put()
                        
                        response_data = {
                                            'auth_token'      : encrypted_auth_token,
                                            'expiry_datetime' : token.get('expiry_datetime'),
                                            'device_id'       : device_id,  
                                            }
                            
                        response_data.update(user_details_dict(user_acct))
                        
                        logger.debug('auth_user debug: response_data=%s', response_data)
                        
                        return create_api_message(status_code=StatusCode.OK, 
                                                   **response_data
                                                   
                                                   )
                    else:
                        
                        logger.warn('auth_user: user password is invalid')
                        with db_client.context():
                            user_acct.add_try_count()
                        
                        return create_api_message('User mobile phone or password is not match', status_code=StatusCode.BAD_REQUEST)
            
        else:
            return create_api_message('User mobile phone or password is not match', status_code=StatusCode.BAD_REQUEST)
            
    else:
        logger.warn('auth_user: user verify input is invalid')
        return create_api_message('Missing mobile phone or password', status_code=StatusCode.BAD_REQUEST)    


@user_api_bp.route('/set-email-verified', methods=['POST'])
@user_auth_token_required_pass_reference_code
def set_email_verified(reference_code):
    
    db_client = create_db_client(caller_info="set_email_verified")
    
    logger.debug('set_email_verified: going to find user account by reference code=%s', reference_code)
    
    with db_client.context():
        user_acct   = User.get_by_reference_code(reference_code)
    
    if user_acct:
        with db_client.context():
            user_acct.mark_email_verified()
        
        return create_api_message(status_code=StatusCode.OK)
    
    else:
        return create_api_message(status_code=StatusCode.BAD_REQUEST)
    
@user_api_bp.route('/set-mobile-phone-verified', methods=['POST'])
@user_auth_token_required_pass_reference_code
def set_mobile_phone_verified(reference_code):
    
    db_client = create_db_client(caller_info="set_mobile_phone_verified")
    
    logger.debug('set_mobile_phone_verified: going to find user account by reference code=%s', reference_code)
    
    with db_client.context():
        user_acct   = User.get_by_reference_code(reference_code)
    
    logger.debug('set_mobile_phone_verified: user_acct=%s', user_acct)
    
    if user_acct:
        with db_client.context():
            user_acct.mark_mobile_phone_verified()
        
        return create_api_message(status_code=StatusCode.OK)
    
    else:
        return create_api_message(status_code=StatusCode.BAD_REQUEST)    
            
      
@user_api_bp.route('/verify-email', methods=['POST'])
@request_json
def verify_email_account(user_data_in_json):
    
    #user_data_in_json   = request.get_json()
    email               = user_data_in_json.get('email')
    verification_code   = user_data_in_json.get('verification_code')
    
    
    if is_not_empty(email) and is_not_empty(verification_code):
        db_client = create_db_client(caller_info="verify_email_account")
        user_acct = None
        
        logger.debug('verify_email_account: going to find user account by email=%s', email)
        
        with db_client.context():
            user_acct   = User.get_by_email(email)
        
        if user_acct:
            logger.debug('verify_email_account: found user account by email=%s', email)    
            if user_acct.email_vc==verification_code:
                is_within_seconds = (user_acct.email_vc_expiry_datetime - datetime.now()).seconds
                if is_within_seconds>0:
                    with db_client.context():
                        user_acct.mark_email_verified()
                    return create_api_message(status_code=StatusCode.OK)
                else:
                    return create_api_message("Verification Code is expired already", status_code=StatusCode.BAD_REQUEST)
            
            else:
                logger.warn('verify_email_account: verification code is invalid')
                return create_api_message("Invalid verification code", status_code=StatusCode.BAD_REQUEST)
            
        else:
            return create_api_message(status_code=StatusCode.BAD_REQUEST)
            
    else:
        logger.warn('verify_email_account: user verify input is invalid')
        return create_api_message(status_code=StatusCode.BAD_REQUEST)    
    
@user_api_bp.route('/verify-mobile-phone', methods=['POST'])
@request_json
@request_headers
def verify_mobile_phone_account(user_data_in_json, request_headers):
    
    #user_data_in_json   = request.get_json()
    mobile_phone        = user_data_in_json.get('mobile_phone')
    verification_code   = user_data_in_json.get('verification_code')
    reference_code      = request_headers.get('x-reference-code')
    
    if is_not_empty(mobile_phone) and is_not_empty(verification_code):
        db_client = create_db_client(caller_info="verify_mobile_phone_account")
        user_acct = None
        with db_client.context():
            user_acct_by_mobile_phone   = User.get_by_mobile_phone(mobile_phone)
            user_acct                   = User.get_by_reference_code(reference_code)
        
        if user_acct_by_mobile_phone is None or user_acct_by_mobile_phone.reference_code == reference_code:
            if user_acct:
                logger.debug('verify_mobile_phone_account: found user account by mobile_phone=%s', mobile_phone)    
                if user_acct.mobile_phone_vc==verification_code:
                    is_within_seconds = (user_acct.mobile_phone_vc_expiry_datetime - datetime.utcnow()).seconds
                    if is_within_seconds>0:
                        with db_client.context():
                            user_acct.mark_email_verified()
                        return create_api_message(status_code=StatusCode.OK)
                    else:
                        return create_api_message("Verification Code is expired already", status_code=StatusCode.BAD_REQUEST)
                
                else:
                    logger.warn('verify_mobile_phone_account: verification code is invalid')
                    return create_api_message("Invalid verification code", status_code=StatusCode.BAD_REQUEST)
                
            else:
                
                return create_api_message(gettext('Invalid user account'), status_code=StatusCode.BAD_REQUEST)
        else:
            return create_api_message(gettext('Mobile phone have been taken'), status_code=StatusCode.BAD_REQUEST)
            
    else:
        logger.warn('verify_mobile_phone_account: user verify input is invalid')
        return create_api_message(status_code=StatusCode.BAD_REQUEST)        

@user_api_bp.route('/register-as-customer', methods=['POST'])
@request_json
#@user_auth_token_required
def register_user_as_customer(user_data_in_json):
    #user_data_in_json           = request.get_json()
    reference_code              = user_data_in_json.get('reference_code')
    merchant_reference_code     = user_data_in_json.get('merchant_reference_code')
    outlet_key                  = user_data_in_json.get('outlet_key')
    
    logger.debug('register_user_as_customer: user_data_in_json=%s', user_data_in_json)
    
    try:
        if is_not_empty(reference_code):
            logger.debug('customer registration input is valid')
            db_client = create_db_client(caller_info="register_user_as_customer")
            
            created_customer        = None
            existing_user_acct      = None
            is_email_used           = False
            is_mobile_phone_used    = False
            merchant_act_key        = None
            
            merchant_acct           = None
            
            with db_client.context():
                existing_user_acct  = User.get_by_reference_code(reference_code)
                if existing_user_acct:
                    outlet              = Outlet.fetch(outlet_key)
                        
                    if outlet:
                        merchant_acct       = outlet.merchant_acct_entity
                        merchant_act_key    = outlet.merchant_acct_key  
                        logger.debug('Valid granted outlet key for merchant acct')
                        
                        created_customer = Customer.get_by_reference_code(reference_code, merchant_acct)
                         
                        if created_customer is None:
                            
                            
                            email           = existing_user_acct.email
                            mobile_phone    = existing_user_acct.mobile_phone
                            
                            logger.debug('email=%s', email)
                            logger.debug('mobile_phone=%s', mobile_phone)
                            
                            checking_customer = Customer.get_by_email(email, merchant_acct=merchant_acct) 
                            
                            if checking_customer:
                                is_email_used = True
                            else:
                                if is_not_empty(mobile_phone):
                                    checking_customer = Customer.get_by_mobile_phone(mobile_phone, merchant_acct=merchant_acct)
                                    if checking_customer:
                                        is_mobile_phone_used = True
                            
                            logger.debug('is_email_used=%s', is_email_used)
                            logger.debug('is_mobile_phone_used=%s', is_mobile_phone_used)
                            
                            if is_email_used == False and is_mobile_phone_used == False:
                            
                                created_customer = Customer.create_from_user(outlet, existing_user_acct, merchant_reference_code=merchant_reference_code)
                        
                            
                        logger.debug('created_customer=%s', created_customer)
                        
                    else:
                        logger.warn('Invalid granted outlet key or merchant account id')
                
                if created_customer:
                    
                    
                    
                    response_data = {
                                    'customer_key'              : created_customer.key_in_str,
                                    'registered_datetime'       : created_customer.registered_datetime.strftime("%d-%m-%Y %H:%M:%S"),
                                    'merchant_reference_code'   : created_customer.merchant_reference_code,
                                    'reference_code'            : created_customer.reference_code,
                                    'merchant_account_key'      : merchant_act_key,
                                    'company_name'              : merchant_acct.company_name,
                                    'outlet_key'                : outlet_key,  
                                    #'user_details'              : user_details_dict(existing_user_acct),
                                    }
                    
                    response_data.update(user_details_dict(existing_user_acct))
                    
                    logger.debug('register_user_as_customer debug: response_data=%s', response_data)
                    
                    return create_api_message(status_code=StatusCode.OK, **response_data)
                    
                else:
                    if is_email_used==True:
                        return create_api_message('Email have been taken', status_code=StatusCode.BAD_REQUEST)
                    
                    elif is_mobile_phone_used==True:
                        return create_api_message('Mobile phone have been taken', status_code=StatusCode.BAD_REQUEST)
                    else:
                        return create_api_message('Failed to register customer', status_code=StatusCode.BAD_REQUEST)
            
        else:
            logger.warn('customer registration input is invalid')
            
            return create_api_message("Missing register customer input data", status_code=StatusCode.BAD_REQUEST)
    except:
        logger.error('Fail to register customer due to %s', get_tracelog())
        
        return create_api_message(status_code=StatusCode.BAD_REQUEST)


@user_api_bp.route('/register-referred-user-as-customer', methods=['POST'])
@user_auth_token_required_pass_reference_code
@request_json
def register_referred_user_as_customer(user_data_in_json, reference_code):
    #user_data_in_json           = request.get_json()
    #reference_code              = user_data_in_json.get('reference_code')
    referred_code               = user_data_in_json.get('referred_code')
    merchant_acct_code          = user_data_in_json.get('merchant_acct_code')
    
    logger.debug('register_referred_user_as_customer: user_data_in_json=%s', user_data_in_json)
    
    try:
        if is_not_empty(reference_code):
            logger.debug('customer registration input is valid')
            db_client = create_db_client(caller_info="register_referred_user_as_customer")
            
            created_customer        = None
            existing_user_acct      = None
            is_email_used           = False
            is_mobile_phone_used    = False
            merchant_act_key        = None
            
            with db_client.context():
                existing_user_acct  = User.get_by_reference_code(reference_code)
                if existing_user_acct:
                    referrer_user_acct      = User.get_by_referral_code(referred_code)
                    merchant_acct           = MerchantAcct.get_by_account_code(merchant_acct_code)
                    
                    referrer_customer_acct  = Customer.get_by_reference_code(referrer_user_acct.reference_code, merchant_acct)
                    
                    logger.debug('register_referred_user_as_customer: referrer_customer_acct=%s', referrer_customer_acct)
                    
                    if referrer_customer_acct:
                        outlet                  = referrer_customer_acct.registered_outlet
                        merchant_act_key        = merchant_acct.key_in_str
                        outlet_key              = outlet.key_in_str    
                        
                        created_customer        = Customer.get_by_reference_code(reference_code, merchant_acct)
                         
                        if created_customer is None:
                            
                            email           = existing_user_acct.email
                            mobile_phone    = existing_user_acct.mobile_phone
                            
                            logger.debug('email=%s', email)
                            logger.debug('mobile_phone=%s', mobile_phone)
                            
                            checking_customer = Customer.get_by_email(email, merchant_acct=merchant_acct) 
                            
                            if checking_customer:
                                is_email_used = True
                            else:
                                if is_not_empty(mobile_phone):
                                    checking_customer = Customer.get_by_mobile_phone(mobile_phone, merchant_acct=merchant_acct)
                                    if checking_customer:
                                        is_mobile_phone_used = True
                            
                            logger.debug('is_email_used=%s', is_email_used)
                            logger.debug('is_mobile_phone_used=%s', is_mobile_phone_used)
                            
                            if is_email_used == False and is_mobile_phone_used == False:
                            
                                created_customer = __create_referred_user_as_customer(existing_user_acct, merchant_acct, outlet, referrer_customer_acct, referred_code)
                            
                                
                            logger.debug('created_customer=%s', created_customer)
                        
                    else:
                        logger.warn('Customer account not found for referral code=%s', referred_code)
                
                if created_customer:
                    
                    response_data = {
                                    'customer_key'              : created_customer.key_in_str,
                                    'registered_datetime'       : created_customer.registered_datetime.strftime("%d-%m-%Y %H:%M:%S"),
                                    'merchant_reference_code'   : created_customer.merchant_reference_code,
                                    'reference_code'            : created_customer.reference_code,
                                    'merchant_account_key'      : merchant_act_key,
                                    'company_name'              : merchant_acct.company_name,
                                    'outlet_key'                : outlet_key,  
                                    #'user_details'              : user_details_dict(existing_user_acct),
                                    }
                    
                    response_data.update(user_details_dict(existing_user_acct))
                    
                    logger.debug('register_user_as_customer debug: response_data=%s', response_data)
                    
                    return create_api_message(status_code=StatusCode.OK, **response_data)
                    
                else:
                    if is_email_used==True:
                        return create_api_message('Email have been taken', status_code=StatusCode.BAD_REQUEST)
                    
                    elif is_mobile_phone_used==True:
                        return create_api_message('Mobile phone have been taken', status_code=StatusCode.BAD_REQUEST)
                    else:
                        return create_api_message('Failed to register customer', status_code=StatusCode.BAD_REQUEST)
            
        else:
            logger.warn('customer registration input is invalid')
            
            return create_api_message("Missing register customer input data", status_code=StatusCode.BAD_REQUEST)
    except:
        logger.error('Fail to register customer due to %s', get_tracelog())
        
        return create_api_message(status_code=StatusCode.BAD_REQUEST)    

@model_transactional(desc="__create_referred_user_as_customer")
def __create_referred_user_as_customer(user_acct, merchant_acct, referred_outlet, referrer_customer_acct, referrer_code):
    
    created_referee_customer = Customer.create_from_user(referred_outlet, user_acct)
    created_referee_customer.referrer_code = referrer_code
    created_referee_customer.put()
    
    #create_upstream = False
    create_upstream = True
    
    if create_upstream:
        create_merchant_registered_customer_upstream_for_merchant(created_referee_customer)
        create_registered_customer_upstream_for_system(created_referee_customer)
    
    #trigger referral program reward here
    giveaway_referral_program_reward(merchant_acct, 
                                     created_referee_customer, 
                                     referrer_customer_acct, 
                                     referred_outlet, 
                                     create_upstream=create_upstream
                                     )
    return created_referee_customer
    

def user_details_dict(user_acct):
    is_email_verified           = user_acct.is_email_verified
    is_mobile_phone_verified    = user_acct.is_mobile_phone_verified
    
    logger.debug('user_details_dict debug: is_email_verified=%s', is_email_verified)
    logger.debug('user_details_dict debug: is_mobile_phone_verified=%s', is_mobile_phone_verified)
    '''
    email_vc_expiry_datetime            = None
    mobile_phone_vc_expiry_datetime     = None
    
    email_verified_datetime             = None
    mobile_phone_verified_datetime      = None
    
    if is_email_verified == False and user_acct.email_vc_expiry_datetime is not None:
        email_vc_expiry_datetime = user_acct.email_vc_expiry_datetime.strftime('%d-%m-%Y %H:%M:%S') 
    else:
        if user_acct.email_verified_datetime is not None:
            email_verified_datetime = user_acct.email_verified_datetime.strftime('%d-%m-%Y %H:%M:%S') 
            
    if is_mobile_phone_verified == False and user_acct.mobile_phone_vc_expiry_datetime is not None:
        mobile_phone_vc_expiry_datetime = user_acct.mobile_phone_vc_expiry_datetime.strftime('%d-%m-%Y %H:%M:%S')
    else:
        if user_acct.mobile_phone_verified_datetime is not None:
            mobile_phone_verified_datetime = user_acct.mobile_phone_verified_datetime.strftime('%d-%m-%Y %H:%M:%S')
    '''    
    birth_date_str = None
    if is_not_empty(user_acct.birth_date):
        birth_date_str = user_acct.birth_date.strftime('%d-%m-%Y')
         
    
    status = user_acct.status
    
    #for imported customer case
    if is_empty(status):
        status = 'completedRegistration'
    
    user_details = {
                       'reference_code'                       : user_acct.reference_code, 
                       'name'                                 : user_acct.name, 
                       'email'                                : user_acct.email,
                       'gender'                               : user_acct.gender,
                       'is_email_verified'                    : is_email_verified,
                       'is_mobile_phone_verified'             : is_mobile_phone_verified,
                       #'status'                               : status,
                    }
    
    if is_not_empty(user_acct.mobile_phone):
        user_details['mobile_phone'] = user_acct.mobile_phone
        
    if is_not_empty(birth_date_str):
        user_details['birth_date'] = birth_date_str    
    '''
    if is_not_empty(email_vc_expiry_datetime):
        user_details['email_vc_expiry_datetime'] = email_vc_expiry_datetime
        
    if is_not_empty(mobile_phone_vc_expiry_datetime):
        user_details['mobile_phone_vc_expiry_datetime'] = mobile_phone_vc_expiry_datetime
        
    
    if is_not_empty(email_verified_datetime):
        user_details['email_verified_datetime'] = email_verified_datetime
        
    if is_not_empty(mobile_phone_verified_datetime):
        user_details['mobile_phone_verified_datetime'] = mobile_phone_verified_datetime        
    '''
    return user_details
    
@user_api_bp.route('/customer/<reference_code>', methods=['GET'])
@request_headers
def read_user_customer_acct(request_headers, reference_code):
    logger.debug('read_user_customer_acct: reference_code=%s', reference_code)
    
    try:
        if is_not_empty(reference_code):
            logger.debug('customer registration input is valid')
            db_client = create_db_client(caller_info="register_user_as_customer")
            
            customer                = None
            outlet_key              = request_headers.get('x-outlet-key')
            merchant_acct           = None
            existing_user_acct      = None
            
            logger.debug('outlet_key=%s', outlet_key)
            
            with db_client.context():
                outlet          = Outlet.fetch(outlet_key)
                    
                if outlet:
                    merchant_acct = outlet.merchant_acct_entity    
                    logger.debug('outlet.merchant_acct_key=%s', outlet.merchant_acct_key)
                    
                    
                    customer = Customer.get_by_reference_code(reference_code, merchant_acct)
                    existing_user_acct = User.get_by_reference_code(reference_code)
                     
                else:
                    logger.warn('Invalid granted outlet key or merchant account id')
                
                if customer:
                    '''
                    response_data = {
                                    'customer_key'              : customer.key_in_str,
                                    'registered_datetime'       : customer.registered_datetime.strftime("%d-%m-%Y %H:%M:%S"),
                                    'merchant_reference_code'   : customer.merchant_reference_code,
                                    'reference_code'            : customer.reference_code,
                                    'merchant_account_key'      : customer.registered_merchant_acct_key,
                                    'outlet_key'                : outlet_key,  
                                    #'user_details'              : user_details_dict(existing_user_acct), 
                                    }
                    response_data.update(user_details_dict(existing_user_acct))
                    '''
                    response_data = return_customer_details(customer)
                    
                    
                    logger.debug('read_user_customer_acct debug: response_data=%s', response_data)
                    
                    return create_api_message(status_code=StatusCode.OK, **response_data)
                    
                else:
                    return create_api_message('Customer account not found', status_code=StatusCode.BAD_REQUEST)
            
        else:
            logger.warn('customer registration input is invalid')
            
            return create_api_message("Missing register customer input data", status_code=StatusCode.BAD_REQUEST)
    except:
        logger.error('Fail to read customer details due to %s', get_tracelog())
        
        return create_api_message(status_code=StatusCode.BAD_REQUEST)    

@user_api_bp.route('/customer/<customer_key>/reward/summary', methods=['GET'])
@user_auth_token_required_pass_reference_code
@elapsed_time_trace(trace_key='read_customer_reward_summary')
def read_customer_reward_summary(customer_key, reference_code):
    logger.debug('reference_code=%s', reference_code)
    #vouchers_list   = []
    tier_rewards    = []
    customer_reward_dict = {}
    
    db_client = create_db_client(caller_info="read_customer_reward_summary")
    with db_client.context():
        customer = Customer.fetch(customer_key)
        if customer:
            customer_reward_dict = customer.to_dict(
                                        date_format="%d-%m-%Y", 
                                        datetime_format="%d-%m-%Y %H:%M:%S",
                                        dict_properties = [
                                                'reference_code',
                                                'reward_summary', 'entitled_voucher_summary', 'prepaid_summary', 
                                                'entitled_lucky_draw_ticket_summary', 
                                                
                                                
                                                ],
                                        )
            
            
            customer_tier_reward_summary    = CustomerEntitledTierRewardSummary.list_tier_reward_summary_by_customer(customer)
            CustomerPointReward.list_by_customer(customer)
            
            if customer_tier_reward_summary:
                for v in customer_tier_reward_summary:
                    tier_rewards.append(v.to_dict())
    
    customer_reward_dict['tier_rewards'] = tier_rewards
    
    logger.debug('customer_reward_dict=%s', customer_reward_dict)
    return jsonify(customer_reward_dict)
    
@user_api_bp.route('/check-auth-token', methods=['POST'])
@user_auth_token_required_pass_reference_code
@request_headers
def check_auth_token(request_headers, reference_code):
    
    db_client = create_db_client(caller_info="check_auth_token")
    
    logger.debug('check_auth_token debug: reference_code=%s', reference_code)
    logger.debug('check_auth_token debug: request_headers=%s', request_headers)
    
    
    with db_client.context():
        user_acct = User.get_by_reference_code(reference_code)
        user_auth_token     = request_headers.get('x-auth-token')
        
        logger.debug('check_auth_token debug: user_auth_token=%s', user_auth_token)
        
        
        response_data = {
                        'auth_token'              : user_auth_token,
                        }
        
        response_data.update(user_details_dict(user_acct))
    
    return create_api_message(status_code=StatusCode.OK, **response_data)


    
@user_api_bp.route('/reference-code/<reference_code>', methods=['GET'])
@show_request_info
@user_auth_token_required_pass_reference_code
def read_user_acct(reference_code):
    
    if is_not_empty(reference_code):
        db_client = create_db_client(caller_info="read_user_acct")
        user_acct = None
        with db_client.context():
            user_acct = User.get_by_reference_code(reference_code)
        
        if user_acct:
            logger.debug('read_user_acct: found user account by reference_code=%s', reference_code)    
            is_email_verified           = user_acct.is_email_verified
            is_mobile_phone_verified    = user_acct.is_email_verified
            
            email_vc_expiry_datetime             = None
            mobile_phone_vc_expiry_datetime      = None
            
            if is_email_verified == False:
                #vg_generated_datetime = user_acct.vg_generated_datetime.strftime(user_acct.vg_generated_datetime, '%d/%m/%Y, %H:%M:%S')
                #email_vc_expiry_datetime = str(user_acct.email_vc_expiry_datetime)
                email_vc_expiry_datetime = user_acct.email_vc_expiry_datetime.strftime('%d-%m-%Y %H:%M:%S'),
                
            if is_mobile_phone_verified == False:
                #vg_generated_datetime = user_acct.vg_generated_datetime.strftime(user_acct.vg_generated_datetime, '%d/%m/%Y, %H:%M:%S')
                mobile_phone_vc_expiry_datetime = str(user_acct.mobile_phone_vc_expiry_datetime)    
                
            return create_api_message(status_code=StatusCode.OK, 
                                       reference_code                       = user_acct.reference_code, 
                                       name                                 = user_acct.name, 
                                       email                                = user_acct.email, 
                                       is_email_verified                    = is_email_verified,
                                       is_mobile_phone_verified             = is_mobile_phone_verified,
                                       email_vc_expiry_datetime             = email_vc_expiry_datetime,
                                       mobile_phone_vc_expiry_datetime      = mobile_phone_vc_expiry_datetime,
                                       status                               = user_acct.status,
                                       )
        else:
            logger.debug('user account is not found')
            return create_api_message(status_code=StatusCode.BAD_REQUEST)
            
    else:
        logger.warn('verify_user: user verify input is invalid')
        return create_api_message(status_code=StatusCode.BAD_REQUEST) 

@user_api_bp.route('/test-push-notification', methods=['POST'])
@show_request_info
@user_auth_token_required_pass_reference_code
@request_values
def test_push_notification(reference_code, request_values):
    if is_not_empty(reference_code):
        db_client = create_db_client(caller_info="test_push_notification")
        user_acct = None
        with db_client.context():
            user_acct = User.get_by_reference_code(reference_code)
        
        if user_acct:
            title           = request_values.get('title')
            message         = request_values.get('message')
            device_token    = request_values.get('device_token')
            language_code   = request_values.get('language_code')
            
            create_push_notification(
                                title_data      = title, 
                                message_data    = message,
                                speech          = message,
                                device_token    = device_token,
                                language_code   = language_code,
                                
                            )
            return create_api_message(status_code=StatusCode.OK) 
        else:
            return create_api_message(status_code=StatusCode.BAD_REQUEST)
    else:
        return create_api_message(status_code=StatusCode.BAD_REQUEST) 
    

    
@user_api_bp.route('/delete-account-request', methods=['DELETE'])
@user_auth_token_required_pass_reference_code
@request_values
def delete_user_acct(request_values, reference_code):
    
    
    db_client = create_db_client(caller_info="delete_user_acct")
    
    #password   = request.args.get('password') or request.form.get('password') or request.json.get('password')
    password = request_values.get('password')
    logger.debug('reference_code=%s', reference_code)
    
    with db_client.context():
        user_acct = User.get_by_reference_code(reference_code)
    
    logger.debug('user_acct=%s', user_acct)
    
    if user_acct:
        if user_acct.is_still_lock:
            return create_api_message('User account is locked after many trials for security purpose. Please try after an hour.', status_code=StatusCode.BAD_REQUEST)
        else:
            if user_acct.is_valid_password(password):
                logger.debug('delete_user_acct: found user account by reference_code=%s', reference_code)
                if user_acct.demo_account==True:
                    logger.debug('This is demo account, it is not allow to delete')
                    return create_api_message('Demo account is not allow to delete', status_code=StatusCode.BAD_REQUEST)
                else:
                    logger.debug('Going to delete account')
                    with db_client.context():
                        user_acct.request_to_delete() 
                    
                    return create_api_message(status_code=StatusCode.ACCEPTED,)
            else:
                with db_client.context():
                    user_acct.add_try_count()
                
                return create_api_message('Password is not match', status_code=StatusCode.BAD_REQUEST)
    
    else:
        logger.debug('user account is not found')
        return create_api_message(status_code=StatusCode.BAD_REQUEST)
            
          

@user_api_bp.route('/read-user-new-message-count', methods=['GET'])
@user_auth_token_required_pass_reference_code
def read_user_new_message_count(reference_code):
    #reference_code = request.headers.get('x-referene-code') 
    logger.info('reference_code=%s', reference_code)
    if is_not_empty(reference_code):
        db_client = create_db_client(caller_info="read_user_new_message_count")
        user_acct = None
        new_message_count = 0
        with db_client.context():
            user_acct = User.get_by_reference_code(reference_code)
        
            if user_acct:
                new_message_count = Message.count_new_message(user_acct)
        
        return create_api_message(status_code=StatusCode.OK, 
                                       new_message_count = new_message_count
                                       )
            
        
    else:
        logger.warn('verify_user: user verify input is invalid')
        return create_api_message(status_code=StatusCode.BAD_REQUEST)        

        
@user_api_bp.route('/joined-brands-list', methods=['GET'])
@show_request_info
@user_auth_token_required_pass_reference_code
@request_args
def list_joined_brands(request_args, reference_code):
    
    limit           = request_args.get('limit')
    start_cursor    = request_args.get('start_cursor')
    
    logger.debug('limit=%s', limit)
    logger.debug('start_cursor=%s', start_cursor)
    
    if is_not_empty(reference_code):
        db_client = create_db_client(caller_info="list_joined_brands")
        brands_list     = []
        user_acct       = None
        result_data     = {}
        
        if is_not_empty(limit):
            limit = int(limit)
        
        with db_client.context():
            user_acct = User.get_by_reference_code(reference_code)
        
        if user_acct:
            logger.debug('verify_user: found user account by reference_code=%s', reference_code)
            
            
            
            with db_client.context():
                (customer_accts_list, next_cursor) = Customer.list_paginated_by_user_account(user_acct, start_cursor=start_cursor, limit=limit)
                
                for customer_acct in customer_accts_list:
                    merchant_acct = customer_acct.registered_merchant_acct
                    brands_list.append({
                                        'key'       : merchant_acct.key_in_str,
                                        'account_id': merchant_acct.account_code,
                                        'name'      : merchant_acct.brand_name,
                                        'logo_url'  : merchant_acct.logo_public_url,
                                        
                                        })
                '''
                new_brand_list = []
                for brand in brands_list:
                    new_brand_list.append({
                                        'key'       : brand['key'],
                                        'account_id': brand['account_id'],
                                        'name'      : random_string(10),
                                        'logo_url'  : brand['logo_url'],
                                        
                                        })
                    new_brand_list.append({
                                        'key'       : brand['key'],
                                        'account_id': brand['account_id'],
                                        'name'      : random_string(10),
                                        'logo_url'  : brand['logo_url'],
                                        
                                        })
                    
                    new_brand_list.append({
                                        'key'       : brand['key'],
                                        'account_id': brand['account_id'],
                                        'name'      : random_string(10),
                                        'logo_url'  : brand['logo_url'],
                                        
                                        })
                    
                '''                       
                result_data= {
                                'result'        : brands_list,
                                'count'         : len(brands_list),
                                }
                  
                if is_not_empty(next_cursor):
                    result_data['next_cursor'] = next_cursor  
        
        
        
        return create_api_message(status_code=StatusCode.OK,**result_data,)
        
        #return create_rest_message('Authenticated token is not longer valid', status_code=StatusCode.UNAUTHORIZED, error_code=API_ERR_CODE_EXPIRED_SESSION)
    else:
        return create_api_message(status_code=StatusCode.BAD_REQUEST) 
    
@user_api_bp.route('/all-joined-brands-list', methods=['GET'])
@user_auth_token_required_pass_reference_code
def list_all_joined_brands(reference_code):
    
    
    if is_not_empty(reference_code):
        db_client = create_db_client(caller_info="list_all_joined_brands")
        brands_list     = []
        user_acct       = None
        result_data     = {}
        
        with db_client.context():
            user_acct = User.get_by_reference_code(reference_code)
        
        if user_acct:
            logger.debug('verify_user: found user account by reference_code=%s', reference_code)
            
            
            
            with db_client.context():
                customer_accts_list = Customer.list_by_user_account(user_acct)
                
                for customer_acct in customer_accts_list:
                    merchant_acct = customer_acct.registered_merchant_acct
                    brands_list.append({
                                        'key'       : merchant_acct.key_in_str,
                                        'account_id': merchant_acct.account_code,
                                        'name'      : merchant_acct.brand_name,
                                        'logo_url'  : merchant_acct.logo_public_url,
                                        
                                        })
                                     
                result_data= {
                                'result'        : brands_list,
                                'count'         : len(brands_list),
                                }
                  
        
        return create_api_message(status_code=StatusCode.OK,
                                   **result_data, 
                                   )
    else:
        return create_api_message(status_code=StatusCode.BAD_REQUEST)       
    
@user_api_bp.route('/reset-email-vc', methods=['PUT'])
@request_values
@request_headers
def reset_email_verification_code(request_values, request_headers):
    #email = request.args.get('email') or request.form.get('email') or request.json.get('email')
    email = request_values.get('email')
    
    
    logger.info('reset_email_verification_code: going to reset email verification code by email=%s', email)
    
    if is_not_empty(email):
        db_client = create_db_client(caller_info="reset_email_verification_code")
        user_acct = None
        
        
        
        with db_client.context():
            user_acct = User.get_by_email(email)
        
        if user_acct is None:
            
            #email_vc_expiry_datetime    = datetime.utcnow() + timedelta(minutes=10)
            email_vc_expiry_datetime    = _generate_email_expiry_datetime()
            email_vc                    = random_number(6)
            email_vc_prefix             = random_string(4, is_human_mistake_safe=True)
            
            send_email_verification_code_email(email, email_vc, email_vc_prefix)
            
            logger.info('reset_email_verification_code: email_vc_expiry_datetime=%s', email_vc_expiry_datetime)
            logger.info('reset_email_verification_code: verification code=%s', email_vc)
                
            return create_api_message(status_code=StatusCode.OK, 
                                       #email_vc_expiry_datetime          = str(email_vc_expiry_datetime),
                                       expiry_datetime     = email_vc_expiry_datetime.strftime('%d-%m-%Y %H:%M:%S'),
                                       prefix              = email_vc_prefix, 
                                       code                = email_vc,
                                       
                                       )
        else:
            reference_code = request_headers.get('x-reference-code')
            logger.debug('reference_code from header=%s', reference_code)
            logger.debug('reference_code from database=%s', user_acct.reference_code)
            
            if reference_code == user_acct.reference_code:
                email_vc_expiry_datetime    = _generate_email_expiry_datetime()
                email_vc                    = random_number(6)
                
                if USE_VERIFICATION_REQUEST_ID:
                    email_vc_prefix             = random_string(4, is_human_mistake_safe=True)
                else:
                    email_vc_prefix             = ''
                
                send_email_verification_code_email(email, email_vc, email_vc_prefix)
                
                return create_api_message(status_code=StatusCode.OK, 
                                       #email_vc_expiry_datetime          = str(email_vc_expiry_datetime),
                                       expiry_datetime      = email_vc_expiry_datetime.strftime('%d-%m-%Y %H:%M:%S'),
                                       prefix               = email_vc_prefix,
                                       code                 = email_vc,
                                       )
            else:
                return create_api_message('The email have been taken %s' % email, status_code=StatusCode.BAD_REQUEST)
            
    else:
        logger.warn('reset_email_verification_code: reference code is invalid')
        return create_api_message(status_code=StatusCode.BAD_REQUEST) 
    

def _generate_email_expiry_datetime():
    return datetime.utcnow() + timedelta(minutes=int(EMAIL_EXPIRY_LENGTH_IN_MINUTE))

def _generate_mobile_phone_expiry_datetime():
    return datetime.utcnow() + timedelta(minutes=int(MOBILE_PHONE_EXPIRY_LENGTH_IN_MINUTE))

def _generate_verification_request_id():
    if boolify(USE_VERIFICATION_REQUEST_ID):
        return random_string(4, is_human_mistake_safe=True)
    else:
        return ''
    
@user_api_bp.route('/reset-mobile-phone-vc', methods=['PUT'])
@request_values
@request_headers
def reset_mobile_phone_verification_code(request_values, request_headers):
    mobile_phone    = request_values.get('mobile_phone')
    send_method     = request_values.get('send_method')

    logger.debug('mobile_phone=%s', mobile_phone)
    logger.debug('send_method=%s', send_method)
    
    
    if is_not_empty(mobile_phone):
        db_client                           = create_db_client(caller_info="reset_mobile_phone_verification_code")
        
        with db_client.context():
            user_by_mobile_phone    = User.get_by_mobile_phone(mobile_phone)
        
            logger.debug('user_by_mobile_phone=%s', user_by_mobile_phone)
        
        if user_by_mobile_phone is None:
            
            reference_code = request_headers.get('x-reference-code')
            logger.debug('reference_code=%s', reference_code)
            
            if is_not_empty(reference_code):
                with db_client.context():
                    user_acct    = User.get_by_reference_code(reference_code)
                
                if user_acct is not None:
                    with db_client.context():
                        user_acct.reset_mobile_phone_vc()
                        
                    mobile_phone_vc                     = user_acct.mobile_phone_vc
                    
                    
                    logger.debug('reset_mobile_phone_verification_code: verification code=%s', user_acct.mobile_phone_vc)    
                    logger.debug('reset_mobile_phone_verification_code: USE_VERIFICATION_REQUEST_ID=%s', USE_VERIFICATION_REQUEST_ID)
                    
                    
                else:
                    #return create_api_message(gettext('Invalid input'), status_code=StatusCode.BAD_REQUEST)
                    mobile_phone_vc                     = random_number(6)
                        
            else:
                mobile_phone_vc                     = random_number(6)
            
            try:
                mobile_phone_vc_prefix = _generate_verification_request_id()
                
                mobile_phone_vc_expiry_datetime     = datetime.utcnow() + timedelta(minutes=10)
                
                logger.debug('reset_mobile_phone_verification_code: mobile_phone_vc_expiry_datetime=%s', mobile_phone_vc_expiry_datetime)
                
                send_mobile_phone_verification_code(mobile_phone, mobile_phone_vc, mobile_phone_vc_prefix, send_method=send_method)
                
                return create_api_message(status_code=StatusCode.OK, 
                                           expiry_datetime      = mobile_phone_vc_expiry_datetime.strftime('%d-%m-%Y %H:%M:%S'),
                                           code                 = mobile_phone_vc,
                                           prefix               = mobile_phone_vc_prefix,
                                           
                                           )
            except:
                logger.error('Cannot send verification code due to %s', get_tracelog())
                return create_api_message(
                                            'Could not send verification code at the moment',
                                            status_code=StatusCode.BAD_REQUEST,
                                           
                                           )
            
        else:
            reference_code = request_headers.get('x-reference-code')
            logger.debug('reference_code=%s', reference_code)
            
            if is_not_empty(reference_code) and reference_code==user_by_mobile_phone.reference_code:
                #logger.debug('reset_mobile_phone_verification_code: found user account by mobile_phone=%s', mobile_phone)    
                #is_mobile_phone_verified           = user_acct.is_mobile_phone_verified
                
                with db_client.context():
                    user_by_mobile_phone.reset_mobile_phone_vc()
                
                mobile_phone_vc = user_by_mobile_phone.mobile_phone_vc
                mobile_phone_vc_expiry_datetime     = datetime.utcnow() + timedelta(minutes=10)
                    
                logger.debug('reset_mobile_phone_verification_code: mobile_phone_vc_expiry_datetime=%s', mobile_phone_vc_expiry_datetime)
                logger.debug('reset_mobile_phone_verification_code: verification code=%s', mobile_phone_vc)
                logger.debug('reset_mobile_phone_verification_code: USE_VERIFICATION_REQUEST_ID=%s', USE_VERIFICATION_REQUEST_ID)   
                
                mobile_phone_vc_prefix = _generate_verification_request_id()
                
                try:
                    send_mobile_phone_verification_code(mobile_phone, mobile_phone_vc, mobile_phone_vc_prefix, send_method=send_method)
                    
                    return create_api_message(status_code=StatusCode.OK, 
                                               expiry_datetime      = mobile_phone_vc_expiry_datetime.strftime('%d-%m-%Y %H:%M:%S'),
                                               code                 = mobile_phone_vc,
                                               prefix               = mobile_phone_vc_prefix,
                                               )
                except:
                    logger.error('Cannot send verification code due to %s', get_tracelog())
                    return create_api_message(
                                                'Could not send verification code at the moment',
                                                status_code=StatusCode.BAD_REQUEST,
                                               
                                               )
            else:
                return create_api_message(gettext('Mobile phone have been taken'), status_code=StatusCode.BAD_REQUEST)
        
            
                
                
    else:
        logger.warn('reset_mobile_phone_verification_code: mobile phone is invalid')
        return create_api_message(gettext('Missing mobile phone'), status_code=StatusCode.BAD_REQUEST)  
    
    
    

@user_api_bp.route('/change-password', methods=['PUT'])
@user_auth_token_required_pass_reference_code
@request_values
def change_password(request_values, reference_code):
    
    #existing_password   = request.args.get('existing_password') or request.form.get('existing_password') or request.json.get('existing_password')
    #new_password        = request.args.get('new_password') or request.form.get('new_password') or request.json.get('new_password')
    existing_password   = request_values.get('existing_password')
    new_password        = request_values.get('new_password')
    
    if is_not_empty(existing_password) and is_not_empty(new_password):
        db_client = create_db_client(caller_info="change_password")
        user_acct = None
        is_existing_password_valid = False
        with db_client.context():
            user_acct = User.get_by_reference_code(reference_code)
        
        if user_acct:
            logger.debug('change_password: found user account by reference_code=%s', reference_code)    
            logger.debug('change_password: existing_password=%s', existing_password)
            logger.debug('change_password: new_password=%s', new_password)
            
            with db_client.context():
                if user_acct.is_valid_password(existing_password):
                    is_existing_password_valid = True
                    user_acct.change_password(new_password)
                
        if is_existing_password_valid:    
            return create_api_message(
                                    status_code=StatusCode.OK
                                       
                                       )
        else:
            return create_api_message('existing password is not valid', status_code=StatusCode.BAD_REQUEST)
            
    else:
        return create_api_message('Missing password input', status_code=StatusCode.BAD_REQUEST)  
    
@user_api_bp.route('/set-password', methods=['PUT'])
@request_values
def set_password(request_values):
    
    #new_password        = request.args.get('new_password') or request.form.get('new_password') or request.json.get('new_password')
    #reset_password_token = request.args.get('reset_password_token') or request.form.get('reset_password_token') or request.json.get('reset_password_token')
    
    new_password            = request_values.get('new_password')
    reset_password_token    = request_values.get('reset_password_token')
    
    logger.debug('set_password debug: new_password=%s', new_password)
    logger.debug('set_password debug: reset_password_token=%s', reset_password_token)
    
    if is_not_empty(new_password) and is_not_empty(reset_password_token):
        db_client = create_db_client(caller_info="set_password")
        user_acct = None
        
        
        with db_client.context():
            user_acct = User.get_by_reset_password_token(reset_password_token)
        
        if user_acct:
            logger.debug('set_password: found user account by reset_password_token=%s', user_acct)    
            
            
            with db_client.context():
                user_acct.change_password(new_password)
                
            
            return create_api_message(
                                    status_code=StatusCode.OK
                                       
                                       )
        else:
            return create_api_message('Invalid request to set password', status_code=StatusCode.BAD_REQUEST)
            
    else:
        return create_api_message('Missing password input', status_code=StatusCode.BAD_REQUEST)          
    
@user_api_bp.route('/request-reset-password-via-email', methods=['POST'])
@request_values
def request_reset_password_via_email_post(request_values):
    #email = request.args.get('email') or request.form.get('email') or request.json.get('email')
    email = request_values.get('email')
    
    logger.debug('reset_password_request_post: going to reset email verification code by email=%s', email)
    
    if is_not_empty(email):
        db_client = create_db_client(caller_info="reset_email_verification_code")
        user_acct = None
        
        
        
        with db_client.context():
            user_acct = User.get_by_email(email)
        
        if user_acct:
            logger.debug('request_reset_password_via_email_post: found user account by email=%s', email)    
            is_email_verified           = user_acct.is_email_verified
            
            logger.debug('request_reset_password_via_email_post: is_email_verified=%s', is_email_verified)
            
            #if is_email_verified:
            with db_client.context():
                user_acct.reset_password_request()
            
            send_reset_password_request_email(user_acct)
                
            return create_api_message(status_code=StatusCode.OK
                                       
                                       )
        else:
            return create_api_message('Cannot find user by email %s' % email, status_code=StatusCode.BAD_REQUEST)
            
    else:
        logger.warn('reset_password_post: email is invalid')
        return create_api_message(status_code=StatusCode.BAD_REQUEST) 
    
@user_api_bp.route('/request-reset-password-via-mobile-phone', methods=['POST'])
@request_values
def request_reset_password_via_mobile_phone_post(request_values):
    #mobile_phone = request.args.get('mobile_phone') or request.form.get('mobile_phone') or request.json.get('mobile_phone')
    #send_method = request.args.get('send_method') or request.form.get('send_method') or request.json.get('send_method')
    
    mobile_phone    = request_values.get('mobile_phone')
    send_method     = request_values.get('send_method')
    
    logger.info('mobile_phone=%s', mobile_phone)
    logger.info('send_method=%s', send_method)
    
    if is_not_empty(mobile_phone):
        db_client                   = create_db_client(caller_info="request_reset_password_via_mobile_phone_post")
        
        with db_client.context():
            user_by_mobile_phone    = User.get_by_mobile_phone(mobile_phone)
        
            logger.debug('user_by_mobile_phone=%s', user_by_mobile_phone)
        
        if user_by_mobile_phone:
            with db_client.context():
                user_by_mobile_phone.reset_mobile_phone_vc()
                
                
                
            logger.debug('request_reset_password_via_mobile_phone_post debug: mobile_phone_vc_expiry_datetime=%s', user_by_mobile_phone.mobile_phone_vc_expiry_datetime)
            logger.debug('request_reset_password_via_mobile_phone_post debug: verification code=%s', user_by_mobile_phone.mobile_phone_vc)   
            
            if boolify(USE_VERIFICATION_REQUEST_ID):
                mobile_phone_vc_prefix             = random_string(4, is_human_mistake_safe=True)
            else:
                mobile_phone_vc_prefix = ''
            try:
                send_mobile_phone_verification_code(mobile_phone, user_by_mobile_phone.mobile_phone_vc, mobile_phone_vc_prefix, send_method=send_method)
            except:
                logger.error('Cannot send verification code due to %s', get_tracelog())
                return create_api_message(
                                                'Could not send verification code at the moment',
                                                status_code=StatusCode.BAD_REQUEST,
                                               
                                               )
            
            with db_client.context():
                reset_password_token = '%s-%s' % (mobile_phone_vc_prefix, user_by_mobile_phone.mobile_phone_vc)
                logger.debug('request_reset_password_via_mobile_phone_post debug: reset_password_token=%s', reset_password_token)
                user_by_mobile_phone.set_reset_password_token(reset_password_token)
            
            return create_api_message(status_code=StatusCode.OK, 
                                       expiry_datetime      = user_by_mobile_phone.mobile_phone_vc_expiry_datetime.strftime('%d-%m-%Y %H:%M:%S'),
                                       code                 = user_by_mobile_phone.mobile_phone_vc,
                                       prefix               = mobile_phone_vc_prefix,
                                       is_invalid_account   = False,
                                       )
        else:
            #return create_api_message(status_code=StatusCode.OK, is_invalid_account=True,)
            logger.error('Cannot send verification code due to %s', get_tracelog())
            return create_api_message(
                                    'Could not send verification code at the moment',
                                    status_code=StatusCode.BAD_REQUEST,
                                   
                                   )
                
                
    else:
        logger.warn('request_reset_password_via_mobile_phone_post: mobile phone is invalid')
        return create_api_message(gettext('Missing mobile phone'), status_code=StatusCode.BAD_REQUEST) 
    

@user_api_bp.route('/outlet-reviews', methods=['POST'])
@user_auth_token_required_pass_reference_code
@request_json
def outlet_reviews(request_json, reference_code):
    logger.debug('---outlet_reviews---')
    logger.debug('outlet_reviews: reference_code=%s', reference_code)
    try:
        reviews_data_in_json   = request_json#request.get_json()
        logger.debug('outlet_reviews: reviews_data_in_json=%s', reviews_data_in_json)
        
        reviews_data_form  = OutletReviewsForm(ImmutableMultiDict(reviews_data_in_json))
        
        if reviews_data_form.validate():
            food_score              = reviews_data_form.food_score.data
            service_score           = reviews_data_form.service_score.data
            ambience_score          = reviews_data_form.ambience_score.data
            value_for_money_score   = reviews_data_form.value_for_money_score.data
            
            logger.debug('outlet_reviews: food_score=%s', food_score)
            logger.debug('outlet_reviews: service_score=%s', service_score)
            logger.debug('outlet_reviews: ambience_score=%s', ambience_score)
            logger.debug('outlet_reviews: value_for_money_score=%s', value_for_money_score)
            
            return create_api_message(status_code=StatusCode.OK)
        
        else:
            logger.warn('outlet_reviews: outlet reviews input is invalid')
            error_message = reviews_data_form.create_rest_return_error_message()
            
            return create_api_message(error_message, status_code=StatusCode.BAD_REQUEST)
    except:
        return create_api_message('Failed to process outlet reviews', status_code=StatusCode.BAD_REQUEST)   
        
@user_api_bp.route('/voucher/<redeem_code>/remove', methods=['DELETE'])
@user_auth_token_required_pass_reference_code
def remove_user_voucher(redeem_code, reference_code):
    logger.info('reference_code=%s', reference_code)
    logger.info('redeem_code=%s', redeem_code)
        
    if is_not_empty(redeem_code):
        #reference_code = request.headers.get('x-reference-code')
        
        db_client = create_db_client(caller_info="remove_user_voucher")
        with db_client.context():
            customer_voucher    = CustomerEntitledVoucher.get_by_redeem_code(redeem_code)
            
            if customer_voucher: 
                
                customer_voucher.remove()  
                customer = customer_voucher.entitled_customer_acct
                customer.update_after_removed_voucher(customer_voucher)
            else:
                logger.info('voucher is not found')    

        if customer_voucher and customer_voucher.is_removed:        
            return create_api_message(status_code=StatusCode.OK)
        else:
            logger.info('Invalid voucher redeem code')
            return create_api_message('Invalid voucher redeem code', status_code=StatusCode.BAD_REQUEST)
    else:
        logger.info('Missing voucher redeem code')
        return create_api_message('Missing voucher redeem code', status_code=StatusCode.BAD_REQUEST)

def send_email_verification_code_email(email, verification_code, request_id):
    
    final_verification_code = verification_code
    if is_not_empty(request_id):
        final_verification_code = '%s-%s' % (request_id, verification_code)
        
    
    message = '''
                Dear,
                
                Please enter below code to verify your email for {mobile_app_name}.
                
                
                {verification_code}
                
                
                The code will be expired after {email_expiry_in_minute} minutes.
                
                Cheers,
                {application_name} Team
                
                
                ***Please do not reply to this email. This is an auto-generated email.***
    
            '''.format(email=email, verification_code=final_verification_code, 
                       application_name=APPLICATION_NAME,
                       mobile_app_name=MOBILE_APP_NAME,
                       email_expiry_in_minute=os.environ.get('EMAIL_EXPIRY_LENGTH_IN_MINUTE'))
    
    subject      = 'Email Verification from {mobile_app_name}'.format(mobile_app_name=MOBILE_APP_NAME)
    
    logger.info('DEPLOYMENT_MODE=%s', DEPLOYMENT_MODE)
    
    logger.info(message)
    
    if boolify(SEND_REAL_MESSAGE):
        trigger_send_email(recipient_address = email, subject=subject, message=message)
    else:
        logger.debug('not send email for development or local mode')
        

def send_mobile_phone_verification_code(mobile_phone, verification_code, request_id, send_method='sms'):
    logger.info('SEND_REAL_MESSAGE=%s', SEND_REAL_MESSAGE)
    
    if send_method=='sms':
        if is_not_empty(request_id):
            message = '{mobile_app_name} {request_id}-{verification_code} is your Verification Code. It will be expired after {expiry_in_minute} minutes'.format(mobile_app_name=MOBILE_APP_NAME, verification_code=verification_code, 
                           request_id = request_id, 
                           expiry_in_minute=MOBILE_PHONE_EXPIRY_LENGTH_IN_MINUTE)
        else:
            message = '{mobile_app_name} {verification_code} is your Verification Code. It will be expired after {expiry_in_minute} minutes'.format(mobile_app_name=MOBILE_APP_NAME, verification_code=verification_code, 
                           expiry_in_minute=MOBILE_PHONE_EXPIRY_LENGTH_IN_MINUTE)
        
        logger.info('sms message: %s', message)
        
        if boolify(SEND_REAL_MESSAGE):
            logger.info('Going to send sms to %s', mobile_phone)
            send_sms(to_number=mobile_phone, body=message)
        
            
    elif send_method == 'whatsapp':
        
        logger.info('whatsapp verification_code: %s', verification_code)
        
        if boolify(SEND_REAL_MESSAGE):
            logger.info('Going to send whatsapp to %s', mobile_phone)
            send_whatsapp_verification_message(mobile_phone, verification_code, request_id=request_id)
        
        
def send_reset_password_request_email(user_acct):
    reset_password_link = '{base_url}/user/reset-password-request/{request_reset_password_token}'.format(base_url=APPLICATION_BASE_URL, request_reset_password_token=user_acct.request_reset_password_token)
    
    message = '''
                Dear {name},
                
                
                Forgot your password? No worries.
                We received your request to reset the password for your {mobile_app_name} account. 
                
                Just one more step to reset the password, please click the below link:
                
                
                {reset_password_link}
                
                
                
                Or copy and paste the URL into your web browser.
                
                Cheers,
                {application_name} Team
                
                
                ***Please do not reply to this email. This is an auto-generated email.***
    
            '''.format(name=user_acct.name, email=user_acct.email, 
                       reset_password_link=reset_password_link, 
                       application_name=APPLICATION_NAME,
                       mobile_app_name=MOBILE_APP_NAME,
                       )
    
    subject = 'Request to reset password fors {mobile_app_name}'.format(mobile_app_name=MOBILE_APP_NAME,application_name=APPLICATION_NAME)
    
    logger.info('email message: %s', message)
            
    trigger_send_email(recipient_address = user_acct.email, subject=subject, message=message)
    '''
    send_email(sender           = DEFAULT_SENDER, 
                   to_address   = [user_acct.email], 
                   subject      = subject, 
                   body         = message,
                   app          = current_app
                   )    
    ''' 

def send_reset_password_request_sms(mobile_phone, verification_code, request_id):
    message = '{mobile_app_name} {request_id}-{verification_code} is your Verification Code. It will be expired after {expiry_in_minute} minutes'.format(mobile_app_name=MOBILE_APP_NAME, verification_code=verification_code, 
                       request_id = request_id, 
                       expiry_in_minute=os.environ.get('MOBILE_PHONE_EXPIRY_LENGTH_IN_MINUTE'))
    
    logger.info('DEPLOYMENT_MODE=%s', DEPLOYMENT_MODE)
    
    logger.info('sms message: %s', message)
    
    if DEPLOYMENT_MODE in (PRODUCTION_MODE, DEMO_MODE):
        logger.info('Going to send sms to %s', mobile_phone)
        send_sms(to_number=mobile_phone, body=message)
    else:
        logger.debug('not send sms for development or local mode')
        
@user_api_bp.route('/user-messages/list', methods=['GET'])
#@request_debug
@show_request_info
@user_auth_token_required_pass_reference_code
@request_args
def list_user_messages(request_args, reference_code):
    #reference_code = request.headers.get('x-reference-code')
    limit           = request_args.get('limit')
    start_cursor    = request_args.get('start_cursor')
    
    logger.debug('limit=%s', limit)
    logger.debug('start_cursor=%s', start_cursor)
    logger.debug('reference_code=%s', reference_code)
    
    if is_not_empty(reference_code):
        db_client = create_db_client(caller_info="list_user_messages")
        user_acct               = None
        user_messages_list      = []
        result_data             = {}
        
        if is_not_empty(limit):
            limit = int(limit)
        
        with db_client.context():
            user_acct = User.get_by_reference_code(reference_code)
        
        if user_acct:
            logger.debug('verify_user: found user account by reference_code=%s', reference_code)
            
            
            
            with db_client.context():
                (messages_list, next_cursor) = Message.list_paginated_by_user_account(user_acct, start_cursor=start_cursor, limit=limit)
                
                logger.debug('messages_list=%s', messages_list)
                
                for message in messages_list:
                    logger.debug('message.created_datetime=%s', message.created_datetime)
                    local_datetime = from_utc_datetime_to_local_datetime(message.created_datetime, country_code=user_acct.country,)
                    
                    user_messages_list.append(
                                {
                                'message_key'       : message.key_in_str,
                                'message_title'     : message.title,
                                'message_category'  : message.message_category,
                                'message_content'   : message.message_content,
                                'message_data'      : message.message_data,
                                'message_status'    : message.status,
                                'message_from'      : message.message_from,
                                #'message_status'    : 'n',
                                #'created_datetime'  : local_datetime.strftime('%d-%m-%Y %H:%M'),
                                'created_datetime'  : message.created_datetime.strftime('%d-%m-%Y %H:%M'),
                                }
                                )
                    
                
                result_data= {
                                'result'        : user_messages_list,
                                'count'         : len(user_messages_list),
                                }
                logger.debug('result_data=%s', result_data)
                  
                if is_not_empty(next_cursor):
                    result_data['next_cursor'] = next_cursor  
        
        
        
        return create_api_message(status_code=StatusCode.OK, **result_data,)
        
        #return create_rest_message('Authenticated token is not longer valid', status_code=StatusCode.UNAUTHORIZED, error_code=API_ERR_CODE_EXPIRED_SESSION)
    else:
        return create_api_message(status_code=StatusCode.BAD_REQUEST)          
    

@user_api_bp.route('/user-messages/message-key/<message_key>', methods=['POST'])
@user_auth_token_required_pass_reference_code
#@request_values
def mark_user_message_read(reference_code, message_key):
    #message_key     = request_values.get('message_key')
    #reference_code  = request_values.get('reference_code')
    
    logger.info('message_key=%s', message_key)
    logger.info('reference_code=%s', reference_code)
    
    if is_not_empty(message_key):
        db_client = create_db_client(caller_info="update_user_message_as_read")
        
        with db_client.context():
            Message.update_read(message_key)
            
            message = Message.fetch(message_key)
            
            logger.debug('message status=%s', message.status)

        return create_api_message(status_code=StatusCode.ACCEPTED,)
    else:
        return create_api_message(status_code=StatusCode.BAD_REQUEST)
 
@user_api_bp.route('/user-messages/message-key/<message_key>', methods=['DELETE'])
#@user_auth_token_required_pass_reference_code
@user_auth_token_required
#@request_values
def delete_user_message(message_key):
    
    if is_not_empty(message_key):
        db_client = create_db_client(caller_info="delete_user_message")
        
        with db_client.context():
            Message.update_delete(message_key)
            
        return create_api_message(status_code=StatusCode.ACCEPTED,)
    else:
        return create_api_message(status_code=StatusCode.BAD_REQUEST)
    
@user_api_bp.route('/update-device-details', methods=['PUT'])
@user_auth_token_required_pass_reference_code
@request_values
def update_device_details(request_values, reference_code):
    #platform        = request.args.get('platform') or request.form.get('platform') or request.json.get('platform')
    #device_token    = request.args.get('device_token') or request.form.get('device_token') or request.json.get('device_token')
    platform        = request_values.get('platform')
    device_token    = request_values.get('device_token')

    logger.info('platform=%s', platform)
    logger.info('device_token=%s', device_token)
    logger.info('reference_code=%s', reference_code)
    
    if is_not_empty(platform) and is_not_empty(device_token):
        db_client                           = create_db_client(caller_info="update_device_details")
        user_acct                           = None
        
        with db_client.context():
            user_acct = User.get_by_reference_code(reference_code)
            if user_acct:
                user_acct.update_device_details(platform, device_token)
            
        
        if user_acct:
            logger.info('update_device_details: found user account by reference_code=%s', reference_code)
            return create_api_message(status_code=StatusCode.ACCEPTED)
        
        else:
            logger.info('update_device_details: user account not found by reference_code=%s', reference_code)
            return create_api_message('Invalid user data', status_code=StatusCode.BAD_REQUEST)
    else:
        return create_api_message('Missing required data', status_code=StatusCode.BAD_REQUEST)
    
@user_api_bp.route('/verify-auth-auth', methods=['POST','GET'])
@request_headers
def verify_auth_token(request_headers):
    user_auth_token     = request_headers.get('x-auth-token')
    user_reference_code = request_headers.get('x-reference-code')
    
    logger.debug('user_auth_token=%s', user_auth_token)
    
    
    if is_not_empty(user_auth_token):
        logger.debug('user_auth_token is not empty, going to decrypt it')
        try:
            auth_details_json   = decrypt_json(user_auth_token)
            logger.debug('auth_details_json=%s', auth_details_json)
            
        except:
            logger.error('Failed due to %s', get_tracelog())
            return create_api_message('Authenticated token is not valid', status_code=StatusCode.UNAUTHORIZED,)
        
        
        
        if auth_details_json:
            expiry_datetime                 = auth_details_json.get('expiry_datetime')
            user_reference_code_from_token  = auth_details_json.get('reference_code')
            decrypted_device_id             = auth_details_json.get('device_id')
            
            if is_not_empty(expiry_datetime) and is_not_empty(user_reference_code_from_token) and user_reference_code_from_token == user_reference_code:
                
                expiry_datetime = datetime.strptime(expiry_datetime, '%d-%m-%Y %H:%M:%S')
                logger.debug('expiry_datetime=%s', expiry_datetime)
                
                now             = datetime.now()
                if now < expiry_datetime: 
                    logger.debug('auth token is still valid')
                    
                    db_client = create_db_client(caller_info="verify_auth_token")
                    
                    with db_client.context():
                        user_acct           = User.get_by_reference_code(user_reference_code_from_token)
                        signin_device_id    = user_acct.signin_device_id
                    
                    if decrypted_device_id==signin_device_id:
                    
                        return create_api_message(status_code=StatusCode.OK)
                    else:
                        logger.debug('auth token is not logger valid, due to ')
                    
                        return create_api_message('Authenticated token is not longer valid', status_code=StatusCode.UNAUTHORIZED,)
                    
                else:
                    logger.debug('auth token is not logger valid')
                    
                    return create_api_message('Authenticated token is expired', status_code=StatusCode.UNAUTHORIZED,)
        else:
            return create_api_message('Authenticated token is invalid', status_code=StatusCode.UNAUTHORIZED,)
    
    return create_api_message('Authenticated token is required', status_code=StatusCode.UNAUTHORIZED,)

@user_api_bp.route('transaction/merchant-account/<merchant_account_id>/list', methods=['GET'])
@request_debug
@show_request_info
@user_auth_token_required_pass_reference_code
@request_args
def list_transaction_by_merchant(request_args, reference_code, merchant_account_id):
    limit           = request_args.get('limit')
    start_cursor    = request_args.get('start_cursor')
    
    logger.debug('limit=%s', limit)
    logger.debug('start_cursor=%s', start_cursor)
    logger.debug('reference_code=%s', reference_code)
    logger.debug('merchant_account_id=%s', merchant_account_id)
    
    if is_not_empty(reference_code):
        db_client = create_db_client(caller_info="list_transaction_by_merchant")
        transactions_list       = []
        result_data             = {}
        
        if is_not_empty(limit):
            limit = int(limit)
        
        with db_client.context():
            merchant_account    = MerchantAcct.fetch(merchant_account_id)
            customer            = Customer.get_by_reference_code(reference_code, merchant_account)
            
            dict_properties  = ['transaction_id', 'invoice_id', 'remarks', 'tax_amount', 'transact_amount', 'reward_giveaway_method',
                           'entitled_reward_summary', 'entitled_voucher_summary', 'entitled_prepaid_summary', 'entitled_lucky_draw_ticket_summary',
                           'transact_datetime', 'created_datetime',  'transact_outlet_key', 'is_revert', 'reverted_datetime',
                           'transact_by_username', 'is_reward_redeemed', 'is_sales_transaction', 'allow_to_revert',
                           'is_membership_purchase', 'purchased_merchant_membership_key', 'is_membership_renew',
                           'transact_outlet_name','is_sales_transaction','is_revert','is_membership_purchase','remarks',
                           'system_remarks'
                           ]
            
            if customer:
                (paginated_transaction_list, next_cursor) = CustomerTransaction.list_customer_transaction(customer, start_cursor=start_cursor, return_with_cursor=True, limit=limit)
                
                logger.debug('paginated_transaction_list=%s', paginated_transaction_list)
                
                for transaction in paginated_transaction_list:
                    
                    transactions_list.append(transaction.to_dict(dict_properties=dict_properties,  date_format="%d-%m-%Y", datetime_format="%d-%m-%Y %H:%M:%S"))
                    
                    
                    
                
                result_data= {
                                'result'        : transactions_list,
                                'count'         : len(transactions_list),
                                }
                logger.debug('result_data=%s', result_data)
                  
                if is_not_empty(next_cursor):
                    result_data['next_cursor'] = next_cursor  
        
        
        
        return create_api_message(status_code=StatusCode.OK, **result_data,)
        
        #return create_rest_message('Authenticated token is not longer valid', status_code=StatusCode.UNAUTHORIZED, error_code=API_ERR_CODE_EXPIRED_SESSION)
    else:
        return create_api_message(status_code=StatusCode.BAD_REQUEST)  
    
@user_api_bp.route('redemption/merchant-account/<merchant_account_id>/list', methods=['GET'])
@request_debug
@show_request_info
@user_auth_token_required_pass_reference_code
@request_args
def list_redemption_by_merchant(request_args, reference_code, merchant_account_id):
    limit           = request_args.get('limit')
    start_cursor    = request_args.get('start_cursor')
    
    logger.debug('limit=%s', limit)
    logger.debug('start_cursor=%s', start_cursor)
    logger.debug('reference_code=%s', reference_code)
    logger.debug('merchant_account_id=%s', merchant_account_id)
    
    if is_not_empty(reference_code):
        db_client = create_db_client(caller_info="list_transaction_by_merchant")
        transactions_list       = []
        result_data             = {}
        
        if is_not_empty(limit):
            limit = int(limit)
        
        with db_client.context():
            merchant_account    = MerchantAcct.fetch(merchant_account_id)
            customer            = Customer.get_by_reference_code(reference_code, merchant_account)
            
            dict_properties  = ['transaction_id', 'invoice_id', 'remarks', 'reward_format', 'redeemed_amount', 'redeemed_summary',
                                   'redeemed_datetime', 'is_revert', 'reverted_datetime', 'redeemed_outlet_name',
                                   'redeemed_by_username', 
                                   ]
            
            if customer:
                (paginated_transaction_list, next_cursor) = CustomerRedemption.list_customer_redemption(customer, start_cursor=start_cursor, return_with_cursor=True, limit=limit)
                
                logger.debug('paginated_transaction_list=%s', paginated_transaction_list)
                
                for transaction in paginated_transaction_list:
                    
                    transactions_list.append(transaction.to_dict(dict_properties=dict_properties,  date_format="%d-%m-%Y", datetime_format="%d-%m-%Y %H:%M:%S"))
                    
                    
                    
                
                result_data= {
                                'result'        : transactions_list,
                                'count'         : len(transactions_list),
                                }
                logger.debug('result_data=%s', result_data)
                  
                if is_not_empty(next_cursor):
                    result_data['next_cursor'] = next_cursor  
        
        
        
        return create_api_message(status_code=StatusCode.OK, **result_data,)
        
        #return create_rest_message('Authenticated token is not longer valid', status_code=StatusCode.UNAUTHORIZED, error_code=API_ERR_CODE_EXPIRED_SESSION)
    else:
        return create_api_message(status_code=StatusCode.BAD_REQUEST)
    
@user_api_bp.route('/enter-referrer-code', methods=['POST'])
@user_auth_token_required_pass_reference_code
@request_json
def enter_referrer_code(request_data_in_json, reference_code, ):
    logger.debug('enter_referrer_code: reference_code=%s', reference_code)
    logger.debug('enter_referrer_code: request_data_in_json=%s', request_data_in_json)
    referrer_code            = request_data_in_json.get('referrer_code')
    merchant_account_id      = request_data_in_json.get('merchant_acct_id')
    
    logger.debug('enter_referrer_code: referrer_code=%s', referrer_code)
    logger.debug('enter_referrer_code: merchant_account_id=%s', merchant_account_id)
    
    
    db_client = create_db_client(caller_info="enter_referrer_code")
    
    with db_client.context():
        merchant_acct    = MerchantAcct.get_or_read_from_cache(merchant_account_id)
        
        if merchant_acct:
            try:
                _enter_referrer_code(merchant_acct, reference_code, referrer_code)
                
                return create_api_message(status_code=StatusCode.ACCEPTED)
            except Exception as e:
                return create_api_message(str(e), status_code=StatusCode.BAD_REQUEST)  
    
@user_api_bp.route('/verify-referrer-code', methods=['POST'])
@request_json
def check_referrer_code(request_data_in_json):
    referrer_code            = request_data_in_json.get('referrer_code')
    merchant_acct_code      = request_data_in_json.get('merchant_acct_code')
    
    logger.debug('check_referrer_code: referrer_code=%s', referrer_code)
    logger.debug('check_referrer_code: merchant_acct_code=%s', merchant_acct_code)
    
    db_client = create_db_client(caller_info="enter_referrer_code")
    
    with db_client.context():
        merchant_acct    = MerchantAcct.get_by_account_code(merchant_acct_code)
        
        if merchant_acct:
            try:
                referrer_user_acct      = User.get_by_referral_code(referrer_code)
                if referrer_user_acct:
                    referrer_customer_acct  = Customer.get_by_reference_code(referrer_user_acct.reference_code, merchant_acct)
                    
                    if referrer_customer_acct:
                        logger.info('referrer_code(%s) is valid', referrer_code)
                        return create_api_message(status_code=StatusCode.OK)
                    else:
                        logger.info('referrer_code(%s) is invalid', referrer_code)
                        
                return create_api_message(gettext('Invalid invitation code'),  status_code=StatusCode.BAD_REQUEST)
            
            except Exception as e:
                return create_api_message(str(e), status_code=StatusCode.BAD_REQUEST)  
        else:    
            return create_api_message(gettext('Invalid merchant account code'), status_code=StatusCode.BAD_REQUEST)
            
        
#@model_transactional(desc="_enter_referrer_code")
def _enter_referrer_code(merchant_acct, reference_code, referrer_code):
    referrer_user_acct      = User.get_by_referral_code(referrer_code)
    logger.debug('referrer_user_acct=%s', referrer_user_acct)
    
    if referrer_user_acct:
        referrer_customer_acct  = Customer.get_by_reference_code(referrer_user_acct.reference_code, merchant_acct)
        logger.debug('referrer_customer_acct=%s', referrer_customer_acct.name)
        if referrer_customer_acct:
            
            customer_acct       = Customer.get_by_reference_code(reference_code, merchant_acct)
            
            logger.debug('customer_acct=%s', customer_acct.name)
            
            if is_empty(customer_acct.referrer_code):
                logger.debug('customer not yet refer by friend')
                
                if customer_acct.referral_code != referrer_code:
                    logger.debug('The referrer code is not same as customer referral code')
                    registered_outlet   = customer_acct.registered_outlet
                    
                    customer_acct.referrer_code = referrer_code
                    customer_acct.put()
                    
                    giveaway_referral_program_reward(merchant_acct, 
                                         customer_acct, 
                                         referrer_customer_acct, 
                                         registered_outlet, 
                                         create_upstream=True
                                     )
                else:
                    logger.debug('The referrer code is same as customer referral code')
                    raise Exception(gettext('You are not allow to use your invitation code'))
                
            else:
                raise Exception(gettext('You have already referred by friend'))
        else:
            raise Exception(gettext('Your friend account is not found'))
    else:
        raise Exception(gettext('Invalid invitation code'))
