'''
Created on 26 Mar 2024

@author: jacklok
'''
from wtforms import StringField, validators
from trexweb.forms.base_forms import ValidationBaseForm
from trexweb.libs.wtforms.fields import IgnoreChoiceSelectMultipleField
from wtforms.fields.core import SelectMultipleField

class TokenVerifyForm(ValidationBaseForm):
    verify_token        = StringField('Verify Token', [
                                        validators.DataRequired(message="Verify token is required"),
                                        validators.Length(max=1000, message="Verify token length must not more than 1000 characters")
                                        ]
                                        )


class LinkedProfileForm(ValidationBaseForm):
    linkedin_profile        = StringField('LinkedIn Profile', [
                                        validators.DataRequired(message="LinkedIn Profile is required"),
                                        validators.Length(max=1000, message="LinkedIn Profile length must not more than 1000 characters")
                                        ]
                                        )    

class RecruitForm(TokenVerifyForm):
    name                = StringField('Contact name', [
                                        validators.DataRequired(message="Contact name is required"),
                                        validators.Length(min=3, max=200, message='Contact name length must be within 3 and 200 characters')
                                        ]
                                        )
    email               = StringField('Email Address', [
                                        validators.DataRequired(message="Email is required"),
                                        validators.Length(min=7, max=150, message="Emaill address length must be within 7 and 150 characters"),
                                        validators.Email("Please enter valid email address.")
                                        ]
                                        )
    mobile_phone                = StringField('Mobile Phone', [
                                        validators.Length(min=0, max=20, message="Mobile Phone length must be within 20 characters"),
                                        ]
                                        )
    
    address                 = StringField('Address', [
                                        validators.Length(min=0, max=1000, message="Address length must be within 1000 characters"),
                                        ]
                                        )
    
class CoFounderForm(RecruitForm, LinkedProfileForm):
    '''
    skill               = SelectMultipleField(
                                    label='Skill', 
                                    validators=[
                                        validators.DataRequired(message="Skill is required"),
                                    ],
                                    
                                    )
    '''
    skill      = StringField('Skill', [
                                        validators.DataRequired(message="Skill is required"),
                                        ]
                                        )
    other_skill      = StringField('Other skill', [
                                        validators.Optional()
                                        ]
                                        )
    
    employment_time      = StringField('Employment time', [
                                        validators.DataRequired(message="Employment time is required"),
                                        ]
                                        )
    
    involved_in_founding      = StringField('Founding a startup before', [
                                        validators.DataRequired(message="Founding a startup before is required"),
                                        ]
                                        )
        
    founding_details                 = StringField('Founding Details', [
                                        validators.Optional(),
                                        ]
                                        )

