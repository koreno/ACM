import webapp2
from functools import wraps
from logging import getLogger
import simplejson
from google.appengine.ext import db
_logger = getLogger(__name__)


REST_VERBS = "post", "get", "put", "delete"



CONTENT_TYPE_HEADER = "Content-Type"
XML_CONTENT_TYPE = "application/xml"
TEXT_CONTENT_TYPE = "text/plain"
JSON_CONTENT_TYPE = "application/json"
METHOD_OVERRIDE_HEADER = "X-HTTP-Method-Override"
RANGE_HEADER = "Range"
BINARY_CONTENT_TYPE = "application/octet-stream"
FORMDATA_CONTENT_TYPE = "multipart/form-data"


def encoder_helper(m):
    if isinstance(m, db.Model):
        return {p:str(getattr(m,p)) for p in m.properties()}
    raise TypeError()
        

json_encoder = simplejson.encoder.JSONEncoderForHTML(default=encoder_helper)

def processed_response(func):
    @wraps(func)
    def inner(self, *args, **kwargs):
        self.set_params(*args, **kwargs)
        ret = func(self)
        self.response.headers[CONTENT_TYPE_HEADER] = JSON_CONTENT_TYPE
        self.response.write(json_encoder.encode(ret))
    return inner

class RESTResource(webapp2.RequestHandler):
    ALL_RESOURCES = []
    URI = None
    class __metaclass__(type):
        def __new__(cls, name, bases, d):
            _logger.debug("Defining resource: %s (%s)", name, d['URI'])
            for verb in REST_VERBS:
                func = d.get(verb, None)
                if func and callable(func):
                    d[verb] = func = processed_response(func)
                    _logger.debug("    verb: %s (%s)", verb, func)
            typ = type.__new__(cls, name, bases, d)
            if typ.URI:
                typ.ALL_RESOURCES.append(typ) 
            return typ

    def set_params(self, **kw):
        pass
        
    
    @classmethod
    def makeRouter(cls):
        return webapp2.Route(cls.URI, handler=cls, name=cls.__name__.lower())
