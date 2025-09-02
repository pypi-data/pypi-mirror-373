from vlcishared.tokens.arcgis_geoportal_token_provider_config import ArcGISGeoportalTokenProviderConfig
from vlcishared.tokens.arcgis_token_provider import ArcGISTokenProvider


class ArcGISGeoportalTokenProvider(ArcGISTokenProvider):
    """
    Proveedor de tokens para ArcGIS que usa 'referer' en el payload.
    """

    def __init__(self, config: ArcGISGeoportalTokenProviderConfig):
        super().__init__(config.url_token_provider, config.username, config.password, config.format, config.expiration)
        self.referer = config.referer

    def get_payload(self):
        return {
            "username": self.username,
            "password": self.password,
            "f": self.format,
            "referer": self.referer,
            "expiration": self.expiration,
        }