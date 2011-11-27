import webapp2
from functools import wraps
from logging import getLogger
_logger = getLogger(__name__)

import simplejson
from google.appengine.ext import db
from acm.auth import authenticate
from webob import Request

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
        return dict(id=m.key().id(), key=m.key().name(), 
                    **{p:str(getattr(m,p)) for p in m.properties()})
    elif isinstance(m, type):
        return "%s.%s" % (m.__module__, m.__name__)
    raise TypeError("Unkown type: %s" % m)
        

json_encoder = simplejson.encoder.JSONEncoderForHTML(default=encoder_helper, sort_keys=True, indent=4)
json_decoder = simplejson.loads

def processed_response(func):
    @wraps(func)
    def inner(self, *args, **kwargs):
        assert not args
        if kwargs:
            self._initialize(**kwargs)
        ret = func(self)
        self.response.headers[CONTENT_TYPE_HEADER] = JSON_CONTENT_TYPE
        self.response.write(json_encoder.encode(ret))
    return inner

class RESTResource(webapp2.RequestHandler):

    URI = None
    MODEL = None

    ALL_RESOURCES = []
    ALL_ROUTES = []
    MODEL_RESOURCES = {}

    class __metaclass__(type):
        def __new__(cls, name, bases, d):
            _logger.debug("Defining resource: %s (%s)", name, d['URI'])
            for verb in REST_VERBS:
                func = d.get(verb, None)
                if func and callable(func):
                    d[verb] = func = processed_response(func)
                    _logger.debug("    verb: %s (%s)", verb, func)
            d['name'] = name.lower()
            typ = type.__new__(cls, name, bases, d)
            typ.ALL_RESOURCES.append(typ)
            if typ.URI:
                # There's a URI for this rest-resource - create a Route
                typ.ROUTE = webapp2.Route(typ.URI, handler=typ, name=typ.name) 
                typ.ALL_ROUTES.append(typ.ROUTE)
                if typ.MODEL:
                    # There's an explicit MODEL object for this rest-resource - create a Metadata Route
                    typ.METADATA_ROUTE = webapp2.Route("/metadata/" + typ.name, handler=typ, 
                                                       handler_method="get_metadata", 
                                                       name=typ.name+"_metadata")
                    typ.ALL_ROUTES.append(typ.METADATA_ROUTE)
            if typ.MODEL:
                typ.MODEL_RESOURCES[typ.MODEL] = typ
            return typ

    def _initialize(self, **kw):
        pass

    def _update_resource(self, resource, put=True):
        data = dict(self.request.params)
        if self.request.headers[CONTENT_TYPE_HEADER] == JSON_CONTENT_TYPE:
            data.update(json_decoder(self.request.body))
        updated = False
        for param in resource.properties():
            value = data.pop(param, None)
            if value is not None:
                _logger.debug("    %s: %s", param, value)
                setattr(resource, param, value)
                updated = True
        if not updated:
            _logger.warning("Nothing was updated in %s!", resource)
            _logger.debug("%s", data)
        elif put:
            _logger.debug("Storing resources: %s", resource)
            resource.put()
        if data:
            _logger.warning("Unused data: %s", data)
        return resource

    def abort_not_found(self):
        self.abort(404)
    def abort_read_only(self):
        self.abort(403)
    def abort_invalid(self):
        self.abort(406)

    @classmethod
    def get_uri_params_for(cls, model):
        return {v:getattr(model,v) for v in cls.ROUTE.variables}

    @processed_response
    def get_metadata(self):
        cls = self.__class__
        return dict(kind = cls.MODEL.kind(),
                    properties = {k:v.data_type for k,v in cls.MODEL.properties().iteritems()},
                    )

    def redirect_to_resource(self, model, resource=None):
        if not resource:
            resource = self.MODEL_RESOURCES[type(model)]
        params = resource.get_uri_params_for(model)
        self.redirect_to(resource.name, _permanent=True, _body="redirecting", **params)


