'''
Created on 8 May 2020

@author: jacklok
'''
from wtforms import StringField, validators, PasswordField
from forms.base_forms import ValidationBaseForm

class AdminDetailsForm(ValidationBaseForm):
    key                 = StringField('Key')
    name                = StringField('Full name', [
                                        validators.DataRequired(message="Full name is required"),
                                        validators.Length(min=3, max=150, message='Full name length must be within 3 and 150 characters')
                                        ]
                                        )
    email               = StringField('Email Address', [
                                        validators.DataRequired(message="Email is required"),
                                        validators.Length(min=7, max=150, message="Emaill address length must be within 7 and 150 characters"),
                                        validators.Email("Please enter valid email address.")
                                        ]
                                        )
    
    
    
class AdminDetailsAddForm(AdminDetailsForm):
    password            = PasswordField('Password', [
                                        validators.DataRequired(message="Password is required"),
                                        validators.EqualTo('confirm_password', message='Passwords must match')
                                        ]
                                        )
    confirm_password    = PasswordField('Confirm Password',[
                                        validators.DataRequired(message="Confirm password is required")
                                        ]
                                        )    

    