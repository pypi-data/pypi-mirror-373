from synapse_sdk.clients.backend.annotation import AnnotationClientMixin
from synapse_sdk.clients.backend.core import CoreClientMixin
from synapse_sdk.clients.backend.data_collection import DataCollectionClientMixin
from synapse_sdk.clients.backend.hitl import HITLClientMixin
from synapse_sdk.clients.backend.integration import IntegrationClientMixin
from synapse_sdk.clients.backend.ml import MLClientMixin


class BackendClient(
    AnnotationClientMixin,
    CoreClientMixin,
    DataCollectionClientMixin,
    IntegrationClientMixin,
    MLClientMixin,
    HITLClientMixin,
):
    """BackendClient is a client for the synapse backend API.

    * Access token overrides authorization token and tenant token.

    Attrs:
        access_token (str): The synapse access token for the synapse backend API.
        authorization_token (str): The authorization token for the synapse backend API.
        tenant_token (str): The tenant token for the synapse backend API.
        agent_token (str): The agent token for the backend API.
        timeout (Dict): Set reasonable default timeouts for better UX. It can receive keys called 'connect' and 'read'.
    """

    name = 'Backend'
    access_token = None
    authorization_token = None
    tenant_token = None
    agent_token = None

    def __init__(self, base_url, access_token=None, token=None, tenant=None, agent_token=None, timeout=None, **kwargs):
        super().__init__(base_url, timeout=timeout)
        self.access_token = access_token
        self.authorization_token = token
        self.tenant_token = tenant
        self.agent_token = agent_token

    def _get_headers(self):
        headers = {}
        if self.access_token:
            headers['Synapse-Access-Token'] = f'Token {self.access_token}'
        if self.authorization_token:
            headers['Authorization'] = f'Token {self.authorization_token}'
        if self.tenant_token:
            headers['Synapse-Tenant'] = f'Token {self.tenant_token}'
        if self.agent_token:
            headers['SYNAPSE-Agent'] = f'Token {self.agent_token}'
        return headers
