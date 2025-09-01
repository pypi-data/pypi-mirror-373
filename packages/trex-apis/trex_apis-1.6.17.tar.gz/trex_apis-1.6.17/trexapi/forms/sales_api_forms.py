from wtforms import StringField, DecimalField, validators
from flask_babel import gettext
from trexlib.forms.base_forms import ValidationBaseForm
from trexlib.libs.wtforms.fields import OptionalDateTimeField

class SalesTransactionForm(ValidationBaseForm):
    sales_amount                    = DecimalField('Sales Amount',[
                                                validators.InputRequired(message="Sales Amount is required"),
                                            ])
    
    tax_amount                      = DecimalField('Tax Amount',[
                                                validators.Optional()
                                            ])  
    
    invoice_id                      = StringField('Invoice No',[
                                                validators.Optional(),
                                                validators.Length(max=30, message="Invoice No length must not more than 30 characters")
                                            ])
    
    promotion_code                  = StringField('Promotion Code',[
                                                validators.Optional(),
                                                validators.Length(max=30, message="Promotion Code length must not more than 30 characters")
                                            ])
    
    remarks                         = StringField('Remarks',[
                                                validators.Optional(),
                                                validators.Length(max=300, message="Remarks length must not more than 300 characters")
                                            ])
    
    transact_datetime               = OptionalDateTimeField('Transact Datetime', format='%d-%m-%Y %H:%M:%S') 
    
     
    
    