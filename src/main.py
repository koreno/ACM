import jinja2
import os

jinja_environment = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__)))


import webapp2
from acm.viewes import MainPage
from acm.resources import RESTResource

DEBUG = True


urls_patterns = RESTResource.ALL_ROUTES + [ 
                     ('/(.*)',   MainPage),
                ]

application = webapp2.WSGIApplication(urls_patterns, debug=DEBUG)

