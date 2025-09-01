from synapse_sdk.clients.ray.core import CoreClientMixin
from synapse_sdk.clients.ray.serve import ServeClientMixin


class RayClient(ServeClientMixin, CoreClientMixin):
    name = 'Ray'
