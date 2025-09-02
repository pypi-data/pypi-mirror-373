'''
Created on 23 Dec 2020

@author: jacklok
'''

from wtforms.validators import DataRequired, InputRequired, Optional
from trexlib.utils.string_util import is_not_empty, is_empty
import logging
logger = logging.getLogger('debug')

class RequiredIfOtherFieldValueIsFalse(DataRequired):
    """Validator which makes a field required if another field is set and has a false value.

    Sources:
        - http://wtforms.simplecodes.com/docs/1.0.1/validators.html
        - http://stackoverflow.com/questions/8463209/how-to-make-a-field-conditionally-optional-in-wtforms

    """
    field_flags = ('requiredif',)

    def __init__(self, other_field_name, message=None, *args, **kwargs):
        self.other_field_name = other_field_name
        self.message = message

    def __call__(self, form, field):
        other_field = form[self.other_field_name]
        if other_field is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)
        if bool(other_field.data)==False:
            super(RequiredIfOtherFieldValueIsFalse, self).__call__(form, field)
            
class RequiredIfOtherFieldValueIsTrue(DataRequired):
    """Validator which makes a field required if another field is set and has a truthy value.

    Sources:
        - http://wtforms.simplecodes.com/docs/1.0.1/validators.html
        - http://stackoverflow.com/questions/8463209/how-to-make-a-field-conditionally-optional-in-wtforms

    """
    field_flags = ('requiredif',)

    def __init__(self, other_field_name, message=None, *args, **kwargs):
        self.other_field_name = other_field_name
        self.message = message

    def __call__(self, form, field):
        other_field = form[self.other_field_name]
        if other_field is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)
        if bool(other_field.data)==True:
            super(RequiredIfOtherFieldValueIsTrue, self).__call__(form, field)  
            
class RequiredIfOtherFieldsValueIsEmpty(DataRequired):
    """Validator which makes a field required if another field(s) are empty value.

    Sources:
        - http://wtforms.simplecodes.com/docs/1.0.1/validators.html
        - http://stackoverflow.com/questions/8463209/how-to-make-a-field-conditionally-optional-in-wtforms

    """
    field_flags = ('requiredif',)

    def __init__(self, other_field_name_list, message=None, *args, **kwargs):
        self.other_field_name_list = other_field_name_list
        self.message = message

    def __call__(self, form, field):
        other_fields = []
        
        logger.debug('self.other_field_name_list=%s', self.other_field_name_list)
        
        for f in self.other_field_name_list:
            other_fields.append(form[f])
        
        if len(other_fields)==0:
            raise Exception('no field named "%s" in form' % self.other_field_name)
        
        is_other_fields_value_empty = True
        
        for f in other_fields:
            f_data = f.data
            
            logger.debug('other field=%s', f)
            logger.debug('f_data=%s', f_data)
            
            if is_not_empty(f_data):
                is_other_fields_value_empty = False
                break
        
        logger.debug('is_other_fields_value_empty=%s', is_other_fields_value_empty)
        
        if is_other_fields_value_empty:
            super(RequiredIfOtherFieldsValueIsEmpty, self).__call__(form, field)   
            
class RequiredIf(DataRequired):
    """Validates field conditionally.
    Usage::
        login_method = StringField('', [AnyOf(['email', 'facebook'])])
        email = StringField('', [RequiredIf(login_method='email')])
        password = StringField('', [RequiredIf(login_method='email')])
        facebook_token = StringField('', [RequiredIf(login_method='facebook')])
    """
    field_flags = ('requiredif',)

    def __init__(self, message=None, *args, **kwargs):
        super(RequiredIf).__init__()
        self.message = message
        self.conditions = kwargs

    # field is requiring that name field in the form is data value in the form
    def __call__(self, form, field):
        for name, data in self.conditions.items():
            other_field = form[name]
            
            logger.debug('RequiredIf: other_field=%s', other_field)
            
            logger.debug('RequiredIf: field=%s', field)
            logger.debug('RequiredIf: name=%s', name)
            logger.debug('RequiredIf: data=%s', data)
            
            logger.debug('RequiredIf: field=%s', field)
            
            if other_field is None:
                raise Exception('no field named "%s" in form' % name)
            if isinstance(data, list):
                if other_field.data in data and not field.data:
                    InputRequired.__call__(self, form, field)
                
            else:
                logger.debug('RequiredIf: other_field.data=%s', other_field.data)
                logger.debug('RequiredIf: field.data=%s', field.data)
                
                if other_field.data == data and not field.data:
                    InputRequired.__call__(self, form, field)
            
            
class RequiredIfOtherFieldEmpty(InputRequired):
    
    field_flags = ('requiredif',)

    def __init__(self, other_empty_field_name_list=[], message=None, *args, **kwargs):
        self.other_empty_field_name_list    = other_empty_field_name_list
        self.message                        = message
        self.conditions                     = kwargs

    def __call__(self, form, field):
        is_required_condition = False     
        
        for name in self.other_empty_field_name_list:
            other_field = form[name]
            
            logger.debug('RequiredIfOtherFieldEmpty: other_field=%s', other_field)
            logger.debug('RequiredIfOtherFieldEmpty: other_field.data=%s', other_field.data)
            
            if other_field is None:
                raise Exception('no field named "%s" in form' % name)
            
            if is_empty(other_field.data):
                logger.debug('other field is None')
                is_required_condition = True
                break
        
        logger.debug('RequiredIfOtherFieldEmpty: is_required_condition=%s', is_required_condition)
                
        if is_required_condition:
            super(RequiredIfOtherFieldEmpty, self).__call__(form, field)
                
              
            
class RequiredIfConditionFieldAndOtherFieldsValueIsEmpty(DataRequired):
    """Validator which makes a field required if another field(s) are empty value.

    Sources:
        - http://wtforms.simplecodes.com/docs/1.0.1/validators.html
        - http://stackoverflow.com/questions/8463209/how-to-make-a-field-conditionally-optional-in-wtforms

    """
    field_flags = ('requiredif',)

    def __init__(self, other_empty_field_name_list=[], message=None, *args, **kwargs):
        self.other_empty_field_name_list    = other_empty_field_name_list
        self.message                        = message
        self.conditions                     = kwargs

    def __call__(self, form, field):
        is_required_condition = False
        
        logger.debug('RequiredIfConditionFieldAndOtherFieldsValueIsEmpty: self.conditions=%s', self.conditions)
        
        for name, data in self.conditions.items():
            other_field = form[name]
            
            logger.debug('RequiredIfConditionFieldAndOtherFieldsValueIsEmpty: field=%s', field)
            logger.debug('RequiredIfConditionFieldAndOtherFieldsValueIsEmpty: name=%s', name)
            logger.debug('RequiredIfConditionFieldAndOtherFieldsValueIsEmpty: data=%s', data)
            logger.debug('RequiredIfConditionFieldAndOtherFieldsValueIsEmpty: other_field=%s', other_field)
            logger.debug('RequiredIfConditionFieldAndOtherFieldsValueIsEmpty: other_field.data=%s', other_field.data)
            
            if other_field is None:
                raise Exception('no field named "%s" in form' % name)
            
            logger.debug('RequiredIfConditionFieldAndOtherFieldsValueIsEmpty: data type=%s', type(data))
            
            if isinstance(data, tuple):
                logger.debug('RequiredIfConditionFieldAndOtherFieldsValueIsEmpty: other_field.data list in data=%s', (other_field.data in data))
                if other_field.data in data:
                    is_required_condition = True
                    break
                
            else:
                logger.debug('RequiredIfConditionFieldAndOtherFieldsValueIsEmpty: other_field.data string in data=%s', (other_field.data == data))
                
                #if other_field.data == data and not field.data:
                '''
                if other_field.data == data:
                    is_required_condition = True
                    break
                '''
                if other_field.data != data:
                    is_required_condition = False
                    break
        logger.debug('RequiredIfConditionFieldAndOtherFieldsValueIsEmpty: is_required_condition=%s', is_required_condition)
        
        if is_required_condition:
            other_fields = []
            for f in self.other_empty_field_name_list:
                other_fields.append(form[f])
            
            logger.debug('RequiredIfConditionFieldAndOtherFieldsValueIsEmpty: -------------> other_fields=%s', other_fields)
            
            if len(other_fields)==0:
                raise Exception('no field named "%s" in form' % self.other_field_name)
            
            is_other_fields_value_empty = True
            
            for f in other_fields:
                f_data = f.data
                if is_not_empty(f_data):
                    is_other_fields_value_empty = False
                    break
            
            if is_other_fields_value_empty:
                super(RequiredIfConditionFieldAndOtherFieldsValueIsEmpty, self).__call__(form, field)                                           
        
        
