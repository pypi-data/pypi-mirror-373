'''
Created on 30 Jan 2024

@author: jacklok
'''
from firebase_admin import credentials, messaging
from trexlib.utils.string_util import is_not_empty, random_string

def create_prepaid_push_notification(title_data=None, speech=None, message_data=None, device_token=None, language_code=None, message_id=None):
    
    data = {
            'speech': speech,
            }
    if message_id is None:
        data['message_id'] = random_string(6)
        
    if is_not_empty(language_code):
        data['language_code'] = language_code
    
    message = messaging.Message(
        notification=messaging.Notification(
            title   = title_data,
            body    = message_data,
            
        ),
        data=data,
        token=device_token,
    )
    
    messaging.send(message)
    
def create_push_notification(title_data=None, speech=None, message_data=None, device_token=None, language_code=None):
    
    data = {
            'speech': speech,
            }
    if is_not_empty(language_code):
        data['language_code'] = language_code
    
    message = messaging.Message(
        notification=messaging.Notification(
            title   = title_data,
            body    = message_data,
            
        ),
        data=data,
        token=device_token,
    )
    
    messaging.send(message)    
