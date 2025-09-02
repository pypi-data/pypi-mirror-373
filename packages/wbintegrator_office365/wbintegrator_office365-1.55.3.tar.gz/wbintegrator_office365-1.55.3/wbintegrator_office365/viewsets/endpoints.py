from rest_framework.reverse import reverse
from wbcore.metadata.configs.endpoints import EndpointViewConfig


class TenantUserEndpointConfig(EndpointViewConfig):
    def get_update_endpoint(self, **kwargs):
        return None

    def get_delete_endpoint(self, **kwargs):
        return None

    def get_create_endpoint(self, **kwargs):
        return None


class EventEndpointConfig(EndpointViewConfig):
    def get_update_endpoint(self, **kwargs):
        return None

    def get_delete_endpoint(self, **kwargs):
        return None

    def get_create_endpoint(self, **kwargs):
        return None


class CallUserEndpointConfig(EndpointViewConfig):
    def get_update_endpoint(self, **kwargs):
        return None

    def get_delete_endpoint(self, **kwargs):
        return None

    def get_create_endpoint(self, **kwargs):
        return None


class CallEventEndpointConfig(EndpointViewConfig):
    def get_update_endpoint(self, **kwargs):
        return None

    def get_delete_endpoint(self, **kwargs):
        return None

    def get_create_endpoint(self, **kwargs):
        return None


class SubscriptionEndpointConfig(EndpointViewConfig):
    def get_update_endpoint(self, **kwargs):
        return None

    def get_delete_endpoint(self, **kwargs):
        return None

    def get_create_endpoint(self, **kwargs):
        return None


class EventLogEndpointConfig(EndpointViewConfig):
    def get_update_endpoint(self, **kwargs):
        return None

    def get_delete_endpoint(self, **kwargs):
        return None

    def get_create_endpoint(self, **kwargs):
        return None


class EventLogEventEndpointConfig(EndpointViewConfig):
    def get_endpoint(self, **kwargs):
        return None

    def get_instance_endpoint(self, **kwargs):
        if event_id := self.view.kwargs.get("last_event_id", None):
            return reverse("wbintegrator_office365:event-eventlog-list", args=[event_id], request=self.request)
        return None
