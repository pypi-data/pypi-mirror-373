from azure.core.credentials import AccessToken

class CustomTokenCredential:
    def __init__(self, token, expires_on):
        self.token = token
        self.expires_on = expires_on

    def get_token(self, *scopes, **kwargs):
        return AccessToken(self.token, self.expires_on)

    async def close(self):
        """No-op async close to satisfy adlfs cleanup requirements."""
        return

    async def __aenter__(self):
        """Support async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Support async context manager exit."""
        await self.close()
