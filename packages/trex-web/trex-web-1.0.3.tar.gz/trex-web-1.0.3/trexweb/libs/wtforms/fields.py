'''
Created on 4 Jan 2021

@author: jacklok
'''

from wtforms.fields.core import StringField, SelectMultipleField, DecimalField, DateTimeField,\
    SelectField
from datetime import datetime
from trexlib.utils.string_util import is_not_empty
import json, logging
from trexlib.utils.log_util import get_tracelog

#logger = logging.getLogger('lib')
logger = logging.getLogger('debug')

class NoPrevalidateSelectMultipleField(SelectMultipleField):
    
    def pre_validate(self, form):
        if self.data:
            if self.choices:
                values = list(c[0] for c in self.choices)
                for d in self.data:
                    if d not in values:
                        raise ValueError(self.gettext("'%(value)s' is not a valid choice for this field") % dict(value=d))
            

class CurrencyField(DecimalField):
    def process_formdata(self, valuelist):
        
        logger.debug('valuelist=%s', valuelist)
        
        if len(valuelist) == 1:
            self.data = [valuelist[0].replace(',', '')]
            if self.data[0]=='':
                self.data = ['0']
        else:
            self.data = ['0']
        
            
        super(CurrencyField, self).process_formdata(self.data)
             
        
class OptionalDateTimeField(DateTimeField):
    def __init__(self, label=None, validators=None, format='%d/%m/%Y %H:%M:%S', **kwargs):
        super(OptionalDateTimeField, self).__init__(label, validators, format=format, **kwargs)

    def process_formdata(self, valuelist):
        if valuelist:
            date_str = ' '.join(valuelist)
            if is_not_empty(date_str):
                try:
                    self.data = datetime.strptime(date_str, self.format)
                except ValueError:
                    self.data = None
                    raise ValueError(self.gettext('Not a valid datetime value'))           
     
class IgnoreChoiceSelectMultipleField(SelectMultipleField):
    def pre_validate(self, form):
        pass
    
    def iter_choices(self):
        return []
    
class IgnoreChoiceSelectField(SelectField):
    def pre_validate(self, form):
        pass    
    
    def iter_choices(self):
        return []
    

class JSONField(StringField):
    def _value(self):
        logger.debug('JSONField: self.data=%s', self.data)
        return json.dumps(self.data) if self.data else ''

    def process_formdata(self, valuelist):
        logger.debug('JSONField: valuelist=%s', valuelist)
        if valuelist:
            if isinstance(valuelist[0], str) :
                logger.debug('It is string thus require json.loads')
                try:
                    self.data = json.loads(valuelist[0])
                #except ValueError:
                #    raise ValueError('This field contains invalid JSON')
                except Exception as err:
                    logger.error('Failed to parse json due to %s', get_tracelog())
                    raise
            else:
                self.data = valuelist[0]
                
        elif self.data is None:
            self.data = {}

    def pre_validate(self, form):
        super().pre_validate(form)
        if self.data:
            try:
                json.dumps(self.data)
            except TypeError:
                raise ValueError('This field contains invalid JSON')    
                
                