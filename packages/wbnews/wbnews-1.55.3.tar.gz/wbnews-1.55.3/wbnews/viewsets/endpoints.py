from rest_framework.reverse import reverse
from wbcore.metadata.configs.endpoints import EndpointViewConfig
from wbcore.utils.urls import get_urlencode_endpoint


class NewsEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return None

    def get_instance_endpoint(self, **kwargs):
        return reverse("wbnews:news-list", request=self.request)


class NewsSourceEndpointConfig(NewsEndpointConfig):
    pass


class NewsRelationshipEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return reverse("wbnews:newsrelationship-list", args=[], request=self.request)

    def get_create_endpoint(self, **kwargs):
        params = {}
        if ct := self.view.content_type:
            params["content_type"] = ct.id
        if object_id := self.view.object_id:
            params["object_id"] = object_id
        return get_urlencode_endpoint(self.get_endpoint(**kwargs), params)

    # def get_instance_endpoint(self, **kwargs):
    #     return reverse("wbnews:news-list", args=[], request=self.request)
    #
    # def get_update_endpoint(self, **kwargs):
    #     return self.get_endpoint(**kwargs)
