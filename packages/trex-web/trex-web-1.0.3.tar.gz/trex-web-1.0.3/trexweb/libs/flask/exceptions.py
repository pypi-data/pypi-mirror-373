'''
Created on 22 Jun 2020

@author: jacklok
'''
from flask import jsonify
from werkzeug.exceptions import Unauthorized
import json

class RESTUnauthorized(Unauthorized):
    
    description = 'You have no authorized session'
    
    def get_body(self, environ=None):
        return json.dumps({
                        'msg': self.description
                        })
          
    
    def get_description(self, environ=None):
        return self.description
    
    def get_headers(self, environ=None):
        """Get a list of headers."""
        return [("Content-Type", "application/json; charset=utf-8")]
