from vlcishared.tokens.arcgis_token_provider_config import ArcGISTokenProviderConfig

class ArcGISGeoportalTokenProviderConfig(ArcGISTokenProviderConfig):
    """
    Configuración para el proveedor de tokens de ArcGIS Geoportal.
    """

    def __init__(self, url_token_provider, username, password, format, referer, expiration):
        super().__init__(url_token_provider, username, password, format, expiration)
        self.referer = referer