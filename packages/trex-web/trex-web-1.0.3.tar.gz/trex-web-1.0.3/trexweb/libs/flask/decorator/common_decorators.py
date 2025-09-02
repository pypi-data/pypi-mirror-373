'''
Created on 5 May 2020

@author: jacklok
'''

from functools import wraps

import logging

def page_title(title=None):
    def decorator(fn):
        @wraps(fn)
        def decorated_function(*args, **kwargs):
            ctx = fn(*args, **kwargs)
            
            logging.debug('page title=%s', title)
            if ctx:
                
                kwargs['page_title'] = title
            logging.debug('args=%s', args)
            logging.debug('kwargs=%s', kwargs)
            return ctx
        return decorated_function
    return decorator

