'''
Created on 3 Jan 2024

@author: jacklok
'''

from flask import Blueprint
import logging
from firebase_admin import messaging

from trexapi.utils.api_helpers import create_api_message, StatusCode
from trexlib.libs.flask_wtf.request_wrapper import request_json

message_api_bp = Blueprint('message_api_bp', __name__,
                                 template_folder='templates',
                                 static_folder='static',
                                 url_prefix='/api/v1/message')

#cred = credentials.Certificate(conf.FIREBASE_SERVICE_ACCOUNT_KEY_PATH)
#firebase_admin.initialize_app(cred)


logger = logging.getLogger('api')

@message_api_bp.route('/private/create', methods=['POST'])
@request_json
def create_private_message(notification_data_in_json):
    #notification_data_in_json   = request.get_json()
    title_data                  = notification_data_in_json.get('title')
    message_data                = notification_data_in_json.get('message')
    analytics_label             = notification_data_in_json.get('analytics_label')
    device_token                = notification_data_in_json.get('device_token')
    speech                      = notification_data_in_json.get('speech')
    
    logger.info('title_data=%s', title_data)
    logger.info('message_data=%s', message_data)
    logger.info('device_token=%s', device_token)
    logger.info('speech=%s', speech)
    
    message = messaging.Message(
        data={
            'title': title_data,
            'body': message_data,
            'speech': speech,
        },
        token=device_token,
        #analyticsLabel=analytics_label,
    )
    
    # Send a message to the device corresponding to the provided
    # registration token.
    response = messaging.send(message)
    
    logger.debug('response=%s', response)
    
    return create_api_message(status_code=StatusCode.OK,)

@message_api_bp.route('/private/notification/create', methods=['POST'])
@request_json
def create_private_notification(notification_data_in_json):
    #notification_data_in_json   = request.get_json()
    title_data                  = notification_data_in_json.get('title')
    message_data                = notification_data_in_json.get('message')
    analytics_label             = notification_data_in_json.get('analytics_label')
    image                       = notification_data_in_json.get('image')
    device_token                = notification_data_in_json.get('device_token')
    speech                      = notification_data_in_json.get('speech')
    
    logger.info('title_data=%s', title_data)
    logger.info('message_data=%s', message_data)
    logger.info('image=%s', image)
    logger.info('device_token=%s', device_token)
    logger.info('speech=%s', speech)
    
    
    message = messaging.Message(
        notification=messaging.Notification(
            title   = title_data,
            body    = message_data,
            
        ),
        data={
            'image': image,
            'speech': speech,
        },
        token=device_token,
        #analyticsLabel=analytics_label,
    )
    '''
    message = messaging.Message(
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            alert=messaging.ApsAlert(
                                title=title_data,
                                body=message_data
                            ),
                            category='CATEGORY_IDENTIFIER'  # Replace with the category identifier for iOS action
                        ),
                    ),
                ),
                android=messaging.AndroidConfig(
                    notification=messaging.AndroidNotification(
                        title=title_data,
                        body=message_data,
                        click_action='ACTION_NAME'  # Replace with the desired action name for Android
                    )
                ),
                token=device_token,
    )
    '''
    # Send a message to the device corresponding to the provided
    # registration token.
    response = messaging.send(message)
    
    logger.debug('response=%s', response)
    
    return create_api_message(status_code=StatusCode.OK,)
                              
@message_api_bp.route('/topic/create', methods=['POST'])
@request_json
def create_topic_message(notification_data_in_json):
    #notification_data_in_json   = request.get_json()
    title_data                  = notification_data_in_json.get('title')
    message_data                = notification_data_in_json.get('message')
    analytics_label             = notification_data_in_json.get('analytics_label')
    image                       = notification_data_in_json.get('image')
    topic                       = notification_data_in_json.get('topic')
    speech                      = notification_data_in_json.get('speech')
    
    logger.info('title_data=%s', title_data)
    logger.info('message_data=%s', message_data)
    logger.info('topic=%s', topic)
    logger.info('speech=%s', speech)
    
    message = messaging.Message(
        notification=messaging.Notification(
            title   = title_data,
            body    = message_data,
            
        ),
        data={
            'image': image,
            'speech': speech,
        },
        topic=topic,
        #analyticsLabel=analytics_label,
    )
    
    # Send a message to the device corresponding to the provided
    # registration token.
    response = messaging.send(message)
    
    logger.debug('response=%s', response)
    
    return create_api_message(status_code=StatusCode.OK,)

@message_api_bp.route('/topic/notification/create', methods=['POST'])
@request_json
def create_topic_notification(notification_data_in_json):
    #notification_data_in_json   = request.get_json()
    title_data                  = notification_data_in_json.get('title')
    message_data                = notification_data_in_json.get('message')
    analytics_label             = notification_data_in_json.get('analytics_label')
    image                       = notification_data_in_json.get('image')
    topic                       = notification_data_in_json.get('topic')
    
    logger.info('title_data=%s', title_data)
    logger.info('message_data=%s', message_data)
    logger.info('topic=%s', topic)
    
    message = messaging.Message(
        notification=messaging.Notification(
            title   = title_data,
            body    = message_data,
            
        ),
        data={
            'image': image,
        },
        topic=topic,
        #analyticsLabel=analytics_label,
    )
    
    # Send a message to the device corresponding to the provided
    # registration token.
    response = messaging.send(message)
    
    logger.debug('response=%s', response)
    
    return create_api_message(status_code=StatusCode.OK,)

@message_api_bp.route('/topic/notification/unsubscribe', methods=['POST'])
@request_json
def unsubscribe_topic_notification(notification_data_in_json):
    #notification_data_in_json   = request.get_json()
    device_token                = notification_data_in_json.get('device_token')
    topic                       = notification_data_in_json.get('topic')
    
    logger.info('topic=%s', topic)
    logger.info('device_token=%s', device_token)
    
    messaging.unsubscribe_from_topic(device_token, topic)
    
    return create_api_message(status_code=StatusCode.OK,)
    
    

