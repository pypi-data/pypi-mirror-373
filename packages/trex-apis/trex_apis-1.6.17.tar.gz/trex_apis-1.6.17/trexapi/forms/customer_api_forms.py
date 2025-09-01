'''
Created on 12 Jul 2021

@author: jacklok
'''

from wtforms import StringField, validators, DateField
from trexlib.forms.base_forms import ValidationBaseForm
from trexlib.libs.wtforms import validators as custom_validator
from flask_babel import gettext
from datetime import date
from wtforms.fields.simple import HiddenField

class CustomerDetailsBaseForm(ValidationBaseForm):
    customer_key        = HiddenField(gettext('Customer Key'), validators=[
                                        ]
                                        )
    name                = StringField(gettext('Name'), validators=[
                                        validators.InputRequired(gettext('Name is required')),
                                        validators.Length(min=3, max=300, message='Name length must be within 3 and 300 characters'),
                                        
                                        ]
                                        )
    gender              = StringField(gettext('Gender'), [
                                        validators.Optional(),
                                        validators.Length(min=1, max=1, message=gettext('Gender value is either m or f')),
                                        
                                        ]
                                        )
    
    birth_date          = DateField('Date of Birth', format='%d-%m-%Y', validators=[
                                            validators.InputRequired(gettext('Birth date is required')),
                                        ])
    
    email               = StringField('Email Address', validators=[
                                        validators.Email(gettext("Please enter valid email address.")),
                                        custom_validator.RequiredIfOtherFieldEmpty(
                                                        ['mobile_phone'],
                                                        message=gettext("Either email or mobile phone is required"),
                                                        
                                                        ),
                                        ]
                                        )
    
    mobile_phone        = StringField('Mobile Phone', validators=[
                                        custom_validator.RequiredIfOtherFieldEmpty(
                                                        ['email'],
                                                        message=gettext("Either email or mobile phone is required"),
                                                        
                                                        ),
                                        
                                        ]
                                        )
    
    merchant_reference_code       = StringField('Member code', validators=[
                                        validators.Optional(),
                                        validators.Length(max=16, message=gettext("Member code length must not more than 16 characters"))
                                        ]
                                        )
    
    
    
class CustomerDetailsNewForm(CustomerDetailsBaseForm):
    
    
    password                      = StringField(gettext('Password'), validators=[
                                        validators.InputRequired(gettext('Password is required')),
                                        
                                        ]
                                        )
    
class CustomerDetailsUpdateForm(CustomerDetailsBaseForm):
    
    password                      = StringField(gettext('Password'), validators=[
                                        validators.Optional(),
                                        ]
                                        )  
    
    
class CustomerSearchForm(ValidationBaseForm):
    name                            = StringField('Name', [
                                        validators.Optional(),
                                        validators.Length(min=3, max=300, message='Name length must be within 3 and 300 characters'),
                                        custom_validator.RequiredIfOtherFieldsValueIsEmpty(
                                                        ['mobile_phone', 'email', 'reference_code', 'merchant_reference_code', ],
                                                        message=gettext("Either one input is required")),
                                        ]
                                        )
    email                           = StringField('Email Address', [
                                        validators.Optional(),
                                        validators.Email("Please enter valid email address."),
                                        custom_validator.RequiredIfOtherFieldsValueIsEmpty(
                                                        ['name', 'mobile_phone', 'reference_code', 
                                                         'merchant_reference_code', ],
                                                        message=gettext("Either one input is required")),
                                        
                                        ]
                                        )
    
    mobile_phone                    = StringField('Mobile Phone', [
                                        validators.Optional(),
                                        custom_validator.RequiredIfOtherFieldsValueIsEmpty(
                                                        ['name', 'email', 'reference_code', 'merchant_reference_code', ],
                                                        message=gettext("Either one input is required")),
                                        
                                        ]
                                        )
    
    reference_code                  = StringField('Reference code', [
                                        validators.Optional(),
                                        custom_validator.RequiredIfOtherFieldsValueIsEmpty(
                                                        ['mobile_phone', 'email', 'name', 'merchant_reference_code',  ],
                                                        message=gettext("Either one input is required")),
                                        validators.Length(max=16, message="Reference code length must not more than 16 characters")
                                        ]
                                        )
    
    merchant_reference_code         = StringField('Member code', [
                                        validators.Optional(),
                                        custom_validator.RequiredIfOtherFieldsValueIsEmpty(
                                                        ['mobile_phone', 'email', 'name', 'merchant_reference_code', 
                                                         ],
                                                        message=gettext("Either one input is required")),
                                        validators.Length(max=16, message="Member code length must not more than 16 characters")
                                        ]
                                        )
    
    customer_data                   = StringField('Customer Data', [
                                        validators.Optional(),
                                        ]
                                        )
    