'''
Created on 14 Jul 2021

@author: jacklok
'''

from wtforms import StringField, DecimalField, validators
from trexlib.forms.base_forms import ValidationBaseForm
from trexlib.libs.wtforms.fields import OptionalDateTimeField
from flask_babel import gettext
from trexapi.forms.sales_api_forms import SalesTransactionForm

class GiveRewardTransactionForm(SalesTransactionForm):
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
    
class RedeemRewardTransactionForm(ValidationBaseForm):
    reward_format                   = StringField('Reward format',[
                                                validators.InputRequired(message="Reward format is required"),
                                            ])
    
    reward_amount                   = DecimalField('Reward Amount',[
                                                validators.InputRequired(message="Reward amount is required"),
                                            ])  
    
    invoice_id                      = StringField('Invoice No',[
                                                validators.Optional(),
                                                validators.Length(max=30, message="Invoice No length must not more than 30 characters")
                                            ])
    
    remarks                         = StringField('Remarks',[
                                                validators.Optional(),
                                                validators.Length(max=300, message="Remarks length must not more than 300 characters")
                                            ])
    
    redeem_datetime                 = OptionalDateTimeField('Transact Datetime', format='%d-%m-%Y %H:%M:%S')    
     
    
    
    
class VoucherRedeemForm(ValidationBaseForm):
    redeem_code                     = StringField('Voucher Code',[
                                                validators.InputRequired(message="Voucher Code is required"),
                                            ])
    invoice_id                      = StringField('Invoice No',[
                                                validators.Optional(),
                                                validators.Length(max=30, message="Invoice No length must not more than 30 characters")
                                            ])
    
    remarks                         = StringField('Remarks',[
                                                validators.Optional(),
                                                validators.Length(max=300, message="Remarks length must not more than 300 characters")
                                            ])
    
    redeem_datetime               = OptionalDateTimeField('Redeem Datetime', format='%d-%m-%Y %H:%M:%S')  
    
class VoucherRemoveForm(ValidationBaseForm):
    redeem_code                     = StringField('Voucher Code',[
                                                validators.InputRequired(message="Voucher Code is required"),
                                            ])
    remarks                         = StringField('Remarks',[
                                                validators.Optional(),
                                                validators.Length(max=300, message="Remarks length must not more than 300 characters")
                                            ])
    
    remove_datetime               = OptionalDateTimeField('Remove Datetime', format='%d-%m-%Y %H:%M:%S')      
            
    
class PrepaidTopupForm(ValidationBaseForm):
    prepaid_program_key                  = StringField('Prepaid program Key', [
                                            validators.DataRequired(message=gettext("Prepaid program key is required")),
                                            ]
                                            )
    
    topup_amount                        = DecimalField('Topup Amount',[
                                                validators.InputRequired(message="Topup amount is required"),
                                            ])
    
    invoice_id                          = StringField('Invoice Id', [
                                                validators.Length(max=50)
                                            ]
                                            )
    
    remarks                             = StringField('Remarks', [
                                                validators.Length(max=500)
                                            ]
                                            )
    
class PrepaidRedeemForm(ValidationBaseForm):
    redeem_amount                        = DecimalField('Redeem Amount',[
                                                validators.InputRequired(message="Redeem amount is required"),
                                            ])
    
    invoice_id                          = StringField('Invoice Id', [
                                                validators.Length(max=50)
                                            ]
                                            )
    
    remarks                             = StringField('Remarks', [
                                                validators.Length(max=500)
                                            ]
                                            )  
    
class PointRedeemForm(ValidationBaseForm):
    redeem_amount                        = DecimalField('Redeem Amount',[
                                                validators.InputRequired(message="Redeem amount is required"),
                                            ])
    
    invoice_id                          = StringField('Invoice Id', [
                                                validators.Length(max=50)
                                            ]
                                            )
    
    remarks                             = StringField('Remarks', [
                                                validators.Length(max=500)
                                            ]
                                            )        
    
    