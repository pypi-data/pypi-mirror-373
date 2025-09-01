from wtforms import StringField, PasswordField, validators, DateField
from trexlib.forms.base_forms import ValidationBaseForm
from trexlib.libs.wtforms import validators as custom_validator
from flask_babel import gettext
from wtforms.fields.core import FloatField


class UserMinForm(ValidationBaseForm):
    name                = StringField(gettext('Name'), validators=[
                                        validators.InputRequired(gettext('Name is required')),
                                        validators.Length(min=3, max=300, message='Name length must be within 3 and 300 characters'),
                                        
                                        ]
                                        )
    email               = StringField('Email', validators=[
                                        #validators.Email(gettext("Please enter valid email address.")),
                                        #validators.InputRequired(gettext('Email is required')),
                                        custom_validator.RequiredIfOtherFieldsValueIsEmpty(
                                                        ['mobile_phone'],
                                                        message=gettext("Either email or mobile phone is required")),
                                        
                                        ]
                                        )
    mobile_phone        = StringField('Mobile Phone', validators=[
                                        custom_validator.RequiredIfOtherFieldsValueIsEmpty(
                                                        ['email'],
                                                        message=gettext("Either email or mobile phone is required")),
                                        ]
                                        )
    
    gender              = StringField('Gender', validators=[
                                        #validators.InputRequired(gettext('Gender is required')),
                                        ]
                                        )
    referrer_code       = StringField('Referrer Code', validators=[
                                        ]
                                        )
    
    birth_date          = StringField('Date of Birth', validators=[
                                        #validators.InputRequired(gettext('Birth date is required')),
                                        ]
                                        )
    
    
    
class UserRegistrationForm(UserMinForm):
    password            = StringField(gettext('Password'), validators=[
                                        validators.InputRequired(gettext('Password is required')),
                                        
                                        ]
                                        ) 
    status              = StringField('Status', validators=[
                                        
                                        ]
                                        ) 
    
class UserUpdateForm(UserMinForm):
    reference_code      = StringField('User Reference Code', validators=[
                                        validators.InputRequired(gettext('User Reference Code is required')),
                                        ]
                                        )
    status      = StringField('User Status', validators=[
                                        ]
                                        )
    
class UserStatusForm(ValidationBaseForm):
    status      = StringField('User Status', validators=[
                                        validators.InputRequired(gettext('User status is required')),
                                        ]
                                        )          
    
class OutletReviewsForm(ValidationBaseForm):
    outlet_key               = StringField('Outlet Key', validators=[
                                        validators.InputRequired(gettext('Outlet key is required')),
                                        ]
                                        )
    
    food_score               = FloatField('Food Score', validators=[
                                        validators.InputRequired(gettext('Food score is required')),
                                        ]
                                        )
    
    service_score               = FloatField('Service Score', validators=[
                                        validators.InputRequired(gettext('Service score is required')),
                                        ]
                                        )
    
    ambience_score          = FloatField('Ambience Score', validators=[
                                        validators.InputRequired(gettext('Ambience score is required')),
                                        ]
                                        )
    
    value_for_money_score   = FloatField('Value for money Score', validators=[
                                        validators.InputRequired(gettext('Value for money score is required')),
                                        ]
                                        )    