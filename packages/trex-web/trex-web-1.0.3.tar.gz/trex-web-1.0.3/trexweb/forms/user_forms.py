'''
Created on 21 Apr 2020

@author: jacklok
'''
from wtforms import StringField, PasswordField, validators
from trexweb.forms.base_forms import ValidationBaseForm

class UserSearchForm(ValidationBaseForm):
    fullname            = StringField('Full name', [
                                        validators.DataRequired(message="Fullname is required"),
                                        validators.Length(min=3, max=150, message='Fullname length must be within 3 and 150 characters')
                                        ]
                                        )
    email               = StringField('Email Address', [
                                        validators.DataRequired(message="Email is required"),
                                        validators.Length(min=7, max=150, message="Emaill address length must be within 7 and 150 characters"),
                                        validators.Email("Please enter valid email address.")
                                        ]
                                        )

class UserDetailsForm(UserSearchForm):
    city                = StringField('City', [
                                        validators.Length(max=100, message="City length must not more than 100 characters")
                                        ]
                                        )
    country             = StringField('Country', [])
    gender              = StringField('Gender', [])
    
class RegistrationForm(UserDetailsForm):
    password            = PasswordField('Password', [
                                        validators.DataRequired(message="Password is required"),
                                        validators.EqualTo('confirm_password', message='Passwords must match')
                                        ]
                                        )
    confirm_password    = PasswordField('Confirm Password',[
                                        validators.DataRequired(message="Confirm password is required")
                                        ]
                                        )    

class SignInForm(ValidationBaseForm):
    signin_email            = StringField('Signin Email', [
                                        validators.DataRequired(message="Email is required"),
                                        validators.Length(min=7, max=150, message="Emaill address length must be within 7 and 150 characters"),
                                        validators.Email("Please enter valid email address.")
                                        ]
                                        )
    password                = PasswordField('New Password', [
                                        validators.InputRequired()
                                        ]
                                        ) 
    

        
    
class ChangePasswordForm(ValidationBaseForm):
    existing_password       = PasswordField('Existing Password')
    new_password            = PasswordField('New Password', [
                                        validators.InputRequired(), 
                                        validators.EqualTo('confirm_password', message='New passwords must match')
                                        ]
                                        )
    confirm_password        = PasswordField('Repeat Password')    


