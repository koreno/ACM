from acm.rest import RESTResource
import acm.models as models
import time
from google.appengine.ext import db
from acm.constants import PAPER_STATUS

class Resources(RESTResource):
    
    URI = r'/resources'

    def get(self):
        return {typ.__name__:typ.URI for typ in self.ALL_RESOURCES}

class Paper(RESTResource):

    URI = r'/<domain>/papers/<paper_id><:/.*>'

    def set_params(self, domain, paper_id):
        self.domain = models.Domain.get_or_insert(domain)
        self.paper_id = "ACM-%09d" % int(paper_id)

    def post(self):
        pass

    def get(self):
        paper = models.Paper.get_by_key_name(self.paper_id, parent=self.domain)
        if not paper:
            paper = models.Paper(key_name=self.paper_id, parent=self.domain)
            paper.title = "Paper from %s" % time.asctime()
            paper.status = PAPER_STATUS.DRAFT
            paper.put()
        return paper

    def put(self):
        pass

    def delete(self):
        pass
