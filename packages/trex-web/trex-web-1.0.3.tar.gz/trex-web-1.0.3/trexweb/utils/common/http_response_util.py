'''
Created on 21 Apr 2020

@author: jacklok
'''
from flask import Response
from datetime import datetime, timedelta
import uuid
import hashlib
from trexconf.conf import AGE_TIME_FIVE_MINUTE, AGE_TIME_ONE_HOUR

MINE_TYPE_HTML = 'text/html'
MINE_TYPE_JAVASCRIPT = 'application/javascript; charset=utf-8'
MINE_TYPE_JSON = 'application/json'


def create_max_age(seconds=AGE_TIME_FIVE_MINUTE):
    return datetime.now() + timedelta(seconds=seconds)


def create_etag():
    return uuid.uuid4().hex


def create_cached_response(response_object, max_age_in_seconds=AGE_TIME_ONE_HOUR,
                           mime_type=MINE_TYPE_HTML, cache_control='must-revalidate',
                           e_tag=None,
                           public=True):
    resp = Response(
                    response=response_object,
                    mimetype=mime_type,
                    status=200
                    )
    
    resp.headers['Cache-Control'] = cache_control
    resp.age = max_age_in_seconds
    resp.expires = create_max_age(seconds=max_age_in_seconds)
    resp.public = False
    if e_tag is None:
        e_tag   = hashlib.md5(response_object.encode('utf-8')).hexdigest()
        resp.set_etag(create_etag())
    else:
        resp.set_etag(e_tag)
    
    return resp
    
