class ArcGISGeoportalConfig:
    """
    Configuración base común para servicios ArcGIS.

    Parámetros comunes:
        url_geoportal: URL base del geoportal ArcGIS.
        endpoint_api_features: Endpoint API de features.
        true_curve: Booleano para mantener curvas en geometrías.
    """

    def __init__(self, url_geoportal, endpoint_api_features, format, true_curve):
        self.url_geoportal = url_geoportal
        self.endpoint_api_features = endpoint_api_features
        self.format = format
        self.true_curve = true_curve
