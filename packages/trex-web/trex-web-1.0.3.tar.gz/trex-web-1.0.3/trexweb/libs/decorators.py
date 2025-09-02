'''
Created on Jan 22, 2012

@author: lokjac
'''
from functools import wraps
from utils.cache_util import CacheUtil 
from utils.url_util import base64_url_encode  

import traceback, logging, conf
import hashlib
from libs.http import StatusCode 
from google.appengine.ext import db, ndb
from utils.string_util import str_to_bool, resolve_unicode_value
from utils.http_util import get_request_cookies 
from utils.log_util import get_tracelog
import types


def http_debug(debug=False):
    def wrapper(fn):
        def http_debug_wrapper(*args, **kwargs):
            handler     = args[0]
            request     = handler.request
            show_debug  = str_to_bool(request.headers.get('X-http-debug'))
            if show_debug or debug:
                logging.debug('\n\n================== start: debug http request ====================')
                for key in request.headers:
                    logging.debug('%s = %s', key, request.headers.get(key))

                logging.debug('\n================== end: debug http request ====================\n\n')

            return fn(*args, **kwargs)

        return http_debug_wrapper
    return wrapper

def cookie_debug(debug=False):
    def wrapper(fn):
        def http_debug_wrapper(*args, **kwargs):
            handler     = args[0]
            request     = handler.request
            response    = handler.response
            show_debug  = str_to_bool(request.headers.get('X-http-debug'))
            if show_debug or debug:
                logging.debug('\n\n================== start: debug cookies ====================')
                request_cookies = get_request_cookies(request)
                cookies_str = ''
                for name in request_cookies:
                    cookies_str+='%s=%s|'%(name, request_cookies[name])

                for cookie in response.headers.getall('Set-Cookie'):
                    cookies_str+='%s|'%cookie

                if cookies_str:
                    cookies_str = cookies_str[:-1]

                logging.debug('cookies_str=%s', cookies_str)
                logging.debug('\n================== end: debug cookies ====================\n\n')

            return fn(*args, **kwargs)

        return http_debug_wrapper
    return wrapper


def auto_cache(expiration=600, key=None, namespace='',
               args_indexes=None, kwargs_list=None):
    """
    A decorator to memoize the results of a function call in memcache. Use this
    in preference to doing your own memcaching, as this function avoids version
    collisions etc...

    Note that if you are not providing a key (or a function to create one) then your
    arguments need to provide consistent str representations of themselves. Without an
    implementation you could get the memory address as part of the result - "<... object at 0x1aeff0>"
    which is going to vary per request and thus defeat the caching.
    
    Usage:
    @auto_cache
    get_by_type(type):
        return MyModel.all().filter("type =", type)
    
    :param expiration: Number of seconds before the value is forced to re-cache, 0
    for indefinite caching
    
    :param key: Option manual key, use in combination with expiration=0 to have
    memcaching with manual updating (eg by cron job). Key can be a func(*args, **kwargs)
    
    :param namespace: Namespace of memcache
    
    :rtype: Memoized return value of function
    """

    def wrapper(fn):

        def construct_key_from_args_indexes(key, args, args_indexes):
            #logging.debug('---construct_key_from_args_indexes(%s)---', args_indexes)
            if args_indexes:
                index_count=0
                for a in args:
                    if index_count in args_indexes:
                        #logging.info('cached argument=%s', a)

                        if isinstance(a, db.Model):
                            key+=str(a.key())
                            #logging.debug('args_key=%s', args_key)

                        elif isinstance(a, ndb.Model):
                            key+=str(a.key.urlsafe())

                        else:
                            key+=str(a)      
                            #logging.debug('args_key=%s', args_key)
                    else:
                        #logging.debug('not found from args')
                        pass
                    index_count+=1
            
            return key
        
        def construct_key_from_kwargs_list(key, kwargs, kwargs_list):
            if kwargs_list:
                for a in kwargs_list:
                    _key = kwargs.get(a)
                    #logging.info('construct_key_from_kwargs_list: kwargs=%s, cached key=%s', kwargs, a)
                    if _key:

                        if isinstance(_key, db.Model):
                            _key=str(_key.key())

                        elif isinstance(a, ndb.Model):
                            key+=str(a.key.urlsafe())

                        elif isinstance(a, dict):
                            import json
                            _key+=json.dumps(_key)
                        else:
                            _key=str(_key)
                    else:
                        _key=''

                    #logging.debug('construct_key_from_kwargs_list: %s=%s', a, _key)

                    key+=_key

            #logging.debug('auto_cache: construct_key_from_kwargs_list key=%s', key)
                    
            return key
        
        def cache_decorator(*args, **kwargs):
            #logging.debug('\n\n\n\n=========== auto cache for %s =============', namespace)
            #logging.debug('args_indexes=%s', args_indexes)
            #logging.debug('kwargs_list=%s', kwargs_list)

            cache_enabled = conf.MODEL_CACHE_ENABLED
            if not cache_enabled:
                return fn(*args, **kwargs)
            
            args_key        = ''
            if key:
                if callable(key):
                    args_key = key(*args, **kwargs)
                else:
                    args_key = key


            args_key        = construct_key_from_args_indexes(args_key, args, args_indexes)
            args_key        = construct_key_from_kwargs_list(args_key, kwargs, kwargs_list)
                         
            mc_key = '%s:%s' % ("auto_cache", args_key)
            #logging.info('============== cached mc_key=%s from namespace=%s', mc_key, namespace)
            hashed_mc_key = hashlib.md5(mc_key).hexdigest()
            #logging.debug('============== hashed mc_key=%s in namespace=%s\n\n', hashed_mc_key, namespace)
            
            
            
            result = CacheUtil.get_cache_repo().get(hashed_mc_key, namespace=namespace)
            #logging.debug('============== result=%s', result)
            if not result:
                result = fn(*args, **kwargs)

                try:
                    CacheUtil.get_cache_repo().set(hashed_mc_key, result, time=expiration, namespace=namespace)
                    #logging.debug('cache object for namespace=%s where %s', namespace, result);
                except:
                    logging.error("Received error from memcache %s", get_tracelog())

            else:
                logging.debug('Found from cache with key=%s in namespace=%s', mc_key, namespace)        
                pass
            
            #logging.debug('\n\n=========== completed auto cache for %s =============\n\n', namespace)
            
            return result


        return cache_decorator
    return wrapper


def flush_cache(key=None, namespace=None, args_indexes=None, kwargs_list=None):
    """
    A decorator to flush memcache entry.

    Note that if you are not providing a key (or a function to create one) then your
    arguments need to provide consistent str representations of themselves. Without an
    implementation you could get the memory address as part of the result - "<... object at 0x1aeff0>"
    which is going to vary per request and thus defeat the caching.
    
    Usage:
    @flush_cache
    update_by_type(self):
        self.type=type
        self.put()
    
    :param key: Option manual key, use in combination with expiration=0 to have
    memcaching with manual updating (eg by cron job). Key can be a func(*args, **kwargs)
    
    :param namespace: Namespace of memcache
    
    :param args_indexes: argument index like required args[0] and args[1], then the value is [0,1]
    """
    def wrapper(fn):
        
        def construct_key_from_args_indexes(key, args, args_indexes):
            if args_indexes:
                index_count=0
                for a in args:
                    #logging.debug('argument=%s', a)
                    if index_count in args_indexes:
                        if isinstance(a, db.Model):
                            if a.is_saved():
                                key+=str(a.key())
                            #logging.debug('args_key=%s', args_key)

                        elif isinstance(a, ndb.Model):
                            if a.key:
                                key+=str(a.key.urlsafe())

                        else:
                            key+=resolve_unicode_value(str(a))
                            #logging.debug('args_key=%s', args_key)
                    else:
                        #logging.debug('not found from args')
                        pass
                    index_count+=1
            
            return key
        
        def construct_key_from_kwargs_list(key, kwargs, kwargs_list):
            if kwargs_list:
                for a in kwargs_list:
                    #logging.debug('key argument=%s', a)
                    _key = kwargs.get(a)
                    if _key:
                        if isinstance(_key, db.Model):
                            if _key.is_saved():
                                _key=str(_key.key())

                        elif isinstance(a, ndb.Model):
                            key+=str(a.key.urlsafe())

                        else:
                            _key=str(_key)
                    else:
                        _key=''
                    key+=_key
            #logging.debug('flush_cache: construct_key_from_kwargs_list=%s', key)
            return key
        
        def cache_decorator(*args, **kwargs):
            #logging.debug('\n\n\n\n=========== flush cache for %s =============', namespace)
            cache_enabled = conf.MODEL_CACHE_ENABLED
            if not cache_enabled:
                return fn(*args, **kwargs)

            args_key = ''
            if key:
                if callable(key):
                    args_key = key(*args, **kwargs)
                else:
                    args_key = key

            args_key        = construct_key_from_args_indexes(args_key, args, args_indexes)
            args_key        = construct_key_from_kwargs_list(args_key, kwargs, kwargs_list)
                    
                
            mc_key = '%s:%s' % ("auto_cache", args_key)
            logging.debug('============== flushed mc_key=%s from namespace=%s', mc_key, namespace)
            hashed_mc_key = hashlib.md5(mc_key).hexdigest()
            #logging.debug('============== hashed mc_key=%s in namespace=%s\n\n', hashed_mc_key, namespace)
            
            try:
                result = fn(*args, **kwargs)
                CacheUtil.get_cache_repo().delete(hashed_mc_key, namespace=namespace)
                #logging.debug('test find result from cache=%s', CacheUtil.get_cache_repo().get(hashed_mc_key, namespace=namespace))
                #logging.debug('flush memcache entry by mc_key=%s from namespace=%s', mc_key, namespace)
                
                #logging.debug('\n\n=========== completed flush cache for %s =============\n\n', namespace)
                
                return result    
            except ValueError as e:
                logging.critical("Recevied error from memcache", exc_info=e)
            
        return cache_decorator
    return wrapper

def hooked_model_class(original_class): #decorator
    original_put    = original_class.put

    def put(self, **kwargs):
        logging.debug('---hooked_model_class(%s)---', original_class)

        pre_func = getattr(self, 'before_put', None)
        #logging.debug('getting hooked before_put_func=%s', pre_func)

        if callable(pre_func):
            pre_func()
            logging.debug('called pre_func')

        try:
            original_put(self, **kwargs)

            post_func = getattr(self, 'after_put', None)

            #logging.debug('getting hooked after_put_func=%s', post_func)
            if callable(post_func):
                post_func()
                logging.debug('called post_func')
        except:
            logging.debug('ignore post function due to error=%s', get_tracelog())
            #raise

    original_class.put = put
    return original_class

def elapsed_time_trace(debug=False, trace_key=None):
    def wrapper(fn):
        import time
        def elapsed_time_trace_wrapper(*args, **kwargs):
            start = time.time()
            result      = fn(*args, **kwargs)
            end = time.time()
            elapsed_time = end - start
            trace_name      = trace_key or fn.func_name
            first_argument  = args[0] if args else None
            logging.info('==================== Start Elapsed Time Trace %s(%s) ===========================', trace_name, first_argument)
            logging.info('elapsed time=%s', ("%.2gs" % (elapsed_time)))
            logging.info('================================================================================')
            return result

        return elapsed_time_trace_wrapper
    return wrapper

def _add_hook_for(cls, target):
    def hook_decorator(hook):
        def hooked(s, *p, **k):
            ret = target(s, *p, **k)
            # some magic happens here
            logging.debug('applied hook here')
            logging.debug('hook_decorator: %s', hook(s, *p, **k))
            return ret
        setattr(cls, target.__name__, hooked)
        return hook
    return hook_decorator

def unicode_decode_deco(cls):
    @_add_hook_for(cls, cls.put)
    def before_put(s, *p, **k):
        return 'before put to %s' % cls.__name__

    return cls

