from vlcishared.tokens.arcgis_token_provider_config import ArcGISTokenProviderConfig


class ArcGISSigvalTokenProviderConfig(ArcGISTokenProviderConfig):
    """
    Configuración para el proveedor de tokens de ArcGIS Sigval.
    """

    def __init__(self, url_token_provider, username, password, format, client, expiration):
        super().__init__(url_token_provider, username, password, format, expiration)
        self.client = client