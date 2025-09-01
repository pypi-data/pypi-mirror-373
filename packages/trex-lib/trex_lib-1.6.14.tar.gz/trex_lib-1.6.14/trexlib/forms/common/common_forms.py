'''
Created on 16 Dec 2020

@author: jacklok
'''

from wtforms import StringField, PasswordField, validators, BooleanField
from trexlib.forms.base_forms import ValidationBaseForm

from datetime import datetime
import logging
from trexlib.utils.string_util import is_not_empty
from wtforms.fields.html5 import DateField
from wtforms.fields.core import IntegerField

logger=logging.getLogger("debug")

class ResetPasswordForm(ValidationBaseForm):
    key                 = StringField('User Key', [
                                        ]
                                        )    
    
    password            = PasswordField('Password', [
                                        validators.DataRequired(message="Password is required"),
                                        validators.EqualTo('confirm_password', message='Passwords must match')
                                        ]
                                        )
    confirm_password    = PasswordField('Confirm Password',[
                                        validators.DataRequired(message="Confirm password is required")
                                        ]
                                        )

class CheckBoxField(BooleanField):
    true_values = (True, 'on', 'yes', 'y')
    
    def __init__(self, label=None, validators=None, true_values=None, default=False, **kwargs):
        super(BooleanField, self).__init__(label, validators, default=default, **kwargs)
        if true_values is not None:
            self.true_values = true_values
        
            
    def process_formdata(self, valuelist):
        if not valuelist or valuelist[0] in self.true_values:
            self.data = True
        else:
            self.data = False        

class CustomDateField(DateField):
    def __init__(self, label=None, validators=None, format='%Y-%m-%d', **kwargs):
        logger.debug('CustomDateField: validators=%s', validators)
        super(CustomDateField, self).__init__(label, validators, format, **kwargs)

    def process_formdata(self, valuelist):
        logger.debug('CustomDateField: valuelist=%s', valuelist)
        logger.debug('CustomDateField: type of valuelist=%s', type(valuelist))
        if is_not_empty(valuelist):
            logger.debug('Going to parse date value')
            date_str = ' '.join(valuelist)
            
            logger.debug('date_str=%s', date_str)
            
            if is_not_empty(date_str):
                logger.debug('date_str is not empty')
                try:
                    self.data = datetime.strptime(date_str, self.format).date()
                except ValueError:
                    self.data = None
                    raise ValueError(self.gettext('Not a valid date value'))
            else:
                logger.debug('ignore due to empty date value')
                self.data = None
                
        else:
            logger.debug('ignore due to empty date value')
            self.data = None

            
class CustomIntegerField(IntegerField):
    
    def process_formdata(self, valuelist):
        if is_not_empty(valuelist) and is_not_empty(valuelist[0]):
            try:
                self.data = int(valuelist[0])
            except ValueError:
                self.data = None
                raise ValueError(self.gettext('%s Not a valid integer value' % self.label))
                
