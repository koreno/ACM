from google.appengine.ext import webapp


class MainPage(webapp.RequestHandler):
    
    
    def get(self, what=None):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Unrecognized resource: %s' % what)

