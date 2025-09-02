from frogml.core.clients.administration.eco_system.client import EcosystemClient


class EcosystemUtils:
    def __init__(self):
        self._client = EcosystemClient()

    def get_user_context(self):
        return self._client.get_authenticated_user_context().user

    def get_default_environment_id(self) -> str:
        return self.get_user_context().account_details.default_environment_id

    def get_current_environment_name(self) -> str:
        return self.get_user_context().environment_details.name.lower()
