from os import environ

from configurations import values


class Office365:
    WBINTEGRATOR_OFFICE365_TENANT_ID = values.Value("", environ_prefix=None)
    WBINTEGRATOR_OFFICE365_CLIENT_ID = values.Value("", environ_prefix=None)
    WBINTEGRATOR_OFFICE365_CLIENT_SECRET = values.Value("", environ_prefix=None)
    WBINTEGRATOR_OFFICE365_REDIRECT_URI = values.Value("", environ_prefix=None)
    WBINTEGRATOR_OFFICE365_TOKEN_ENDPOINT = values.Value("", environ_prefix=None)
    WBINTEGRATOR_OFFICE365_NOTIFICATION_URL = values.Value("", environ_prefix=None)
    WBINTEGRATOR_OFFICE365_GRAPH_API_VERSION = values.Value("", environ_prefix=None)
    WBINTEGRATOR_OFFICE365_AUTHORITY_PREFIX = values.Value("", environ_prefix=None)
    WBINTEGRATOR_OFFICE365_GRAPH_URL_PREFIX = values.Value("", environ_prefix=None)

    @property
    def WBINTEGRATOR_OFFICE365_AUTHORITY(self):
        return self.WBINTEGRATOR_OFFICE365_AUTHORITY_PREFIX + self.WBINTEGRATOR_OFFICE365_TENANT_ID

    @property
    def WBINTEGRATOR_OFFICE365_GRAPH_URL(self):
        return self.WBINTEGRATOR_OFFICE365_GRAPH_URL_PREFIX + self.WBINTEGRATOR_OFFICE365_GRAPH_API_VERSION
