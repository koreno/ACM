from acm.rest import RESTResource
import acm.models as models


from acm.auth import authenticate

class Resources(RESTResource):
    
    URI = r'/resources'

    def get(self):
        return {typ.__name__:typ.URI for typ in self.ALL_RESOURCES}


class Paper(RESTResource):

    URI = r'/<domain>/papers/<model_id><:/.*>'
    MODEL = models.Paper

    def _initialize(self, model_id, domain):
        self.parent = self.MODEL.find_parent(domain=domain)
        self.model = models.Paper.get_by_id(int(model_id), parent=self.parent)

    @classmethod
    def get_uri_params_for(cls, model):
        return dict(domain = model.parent_key().name(),
                    model_id = model.id
                    )

    def get(self):
        if not self.model:
            self.abort(404)
        else:
            return self.model

    @authenticate
    def put(self):
        if not self.model:
            self.abort(404)
        return self._update_resource(self.model) 

    @authenticate
    def delete(self):
        if not self.model:
            self.abort(404)
        self.model.delete()

    @authenticate
    def post(self):
        "new proposition"
        prop = self.model.create_proposition()
        self._update_resource(prop)
        self.redirect_to_resource(prop)


class Papers(RESTResource):

    URI = r'/<domain>/papers'

    def _initialize(self, domain):
        self.domain = models.Domain.get_or_insert(domain)

    @classmethod
    def get_uri_params_for(self, model):
        return dict(domain=model.key().name())

    def get(self):
        limit = int(self.request.get('limit','20'))
        offset = int(self.request.get('offset', '0'))
        return list(models.Paper.all().ancestor(self.domain).fetch(limit, offset))

    @authenticate
    def post(self):
        paper = models.Paper(parent=self.domain)
        self._update_resource(paper)
        self.redirect_to_resource(paper)