from vlcishared.tokens.arcgis_sigval_token_provider_config import ArcGISSigvalTokenProviderConfig
from vlcishared.tokens.arcgis_token_provider import ArcGISTokenProvider


class ArcGISSigvalTokenProvider(ArcGISTokenProvider):
    """
    Proveedor de tokens para ArcGIS que usa 'client' en el payload.
    """

    def __init__(self, config: ArcGISSigvalTokenProviderConfig):
        super().__init__(config.url_token_provider, config.username, config.password, config.format, config.expiration)
        self.client = config.client

    def get_payload(self):
        return {
            "username": self.username,
            "password": self.password,
            "f": self.format,
            "client": self.client,
            "expiration": self.expiration,
        }
    