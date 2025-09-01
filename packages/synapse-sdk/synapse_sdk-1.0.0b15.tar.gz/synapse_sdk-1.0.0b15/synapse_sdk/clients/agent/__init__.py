from synapse_sdk.clients.agent.core import CoreClientMixin
from synapse_sdk.clients.agent.ray import RayClientMixin
from synapse_sdk.clients.agent.service import ServiceClientMixin
from synapse_sdk.clients.exceptions import ClientError


class AgentClient(CoreClientMixin, RayClientMixin, ServiceClientMixin):
    name = 'Agent'
    agent_token = None
    user_token = None
    tenant = None
    long_poll_handler = None

    def __init__(self, base_url, agent_token, user_token=None, tenant=None, long_poll_handler=None, timeout=None):
        # Use shorter timeouts for agent connections for better UX
        agent_timeout = timeout or {
            'connect': 3,  # Connection timeout: 3 seconds
            'read': 10,  # Read timeout: 10 seconds
        }
        super().__init__(base_url, timeout=agent_timeout)
        self.agent_token = agent_token
        self.user_token = user_token
        self.tenant = tenant
        self.long_poll_handler = long_poll_handler

    def _get_headers(self):
        headers = {'Authorization': self.agent_token}
        if self.user_token:
            headers['SYNAPSE-User'] = f'Token {self.user_token}'
        if self.tenant:
            headers['SYNAPSE-Tenant'] = f'Token {self.tenant}'
        return headers

    def _request(self, method, path, **kwargs):
        if self.long_poll_handler:
            return self._request_long_poll(method, path, **kwargs)
        return super()._request(method, path, **kwargs)

    def _request_long_poll(self, method, path, **kwargs):
        headers = self._get_headers()

        if kwargs.get('files'):
            raise ClientError(400, 'file is not allowed when long polling')

        headers['Content-Type'] = 'application/json'

        request_id = self.long_poll_handler.set_request({'method': method, 'path': path, 'headers': headers, **kwargs})
        try:
            response = self.long_poll_handler.get_response(request_id)
        except TimeoutError:
            raise ClientError(408, f'{self.name} is not responding')

        if 400 <= response['status'] < 600:
            raise ClientError(response['status'], response.json() if response['status'] == 400 else response['reason'])

        return response['data']
