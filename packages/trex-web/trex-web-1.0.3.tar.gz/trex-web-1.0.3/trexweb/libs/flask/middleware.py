'''
Created on 22 Jun 2020

@author: jacklok
'''
class SimpleMiddleWare(object):
    def __init__(self, app):
        self.app = app
    
    def __call__(self, environ, start_response):
        
        
        
        return self.app(environ, start_response)
