from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from acm.viewes import MainPage


DEBUG = True


urls_patterns = [

        ('/(.*)',   MainPage),

        ]



application = webapp.WSGIApplication(urls_patterns, debug=DEBUG)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
