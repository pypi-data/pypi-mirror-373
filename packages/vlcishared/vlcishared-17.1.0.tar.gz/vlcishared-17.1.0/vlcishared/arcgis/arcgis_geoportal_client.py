from calendar import c
import json
import logging

from vlcishared.arcgis.arcgis_geoportal_config import ArcGISGeoportalConfig
from vlcishared.http.http import ClienteHTTP
from vlcishared.tokens.arcgis_geoportal_token_provider import ArcGISGeoportalTokenProvider
from vlcishared.tokens.arcgis_geoportal_token_provider_config import ArcGISGeoportalTokenProviderConfig
from vlcishared.tokens.token_handler import TokenHandler


class ArcGISGeoportalClient:
    """
    Cliente para interactuar con servicios del geoportal de ArcGIS. Utiliza un token de autenticación
    para realizar operaciones como consultar y actualizar datos.

    Parámetros del constructor:
    - config: Instancia de ArcGISConfig que contiene todos los valores de configuración necesarios.
    """

    def __init__(self, config: ArcGISGeoportalConfig, config_token_provider=ArcGISGeoportalTokenProviderConfig):
        self.url_geoportal = config.url_geoportal
        self.endpoint_api_features = config.endpoint_api_features
        self.token_provider = ArcGISGeoportalTokenProvider(config_token_provider)
        self.format = config.format
        self.true_curve = config.true_curve
        self.clienteHTTP = ClienteHTTP(timeout=60)
        self.log = logging.getLogger()

    def obtener_identificadores(self, query):
        """
        Ejecuta una consulta sobre la capa de features del geoportal y extrae los atributos de cada entidad encontrada.

        Parámetros:
        - query: Parte de la URL que contiene los filtros o parámetros de búsqueda.

        Retorna:
        - Lista de diccionarios con los atributos de cada entidad encontrada.
        """
        url = f"{self.url_geoportal}/{self.endpoint_api_features}/{query}"

        url = TokenHandler.aplicar_token_url(url, self.token_provider.token)

        respuesta = self.clienteHTTP.get(url=url)
        lista_entidades = respuesta.get("features", [])

        lista_identificadores = []
        for entidad in lista_entidades:
            atributos = entidad.get("attributes", {})
            lista_identificadores.append(atributos)
        return lista_identificadores

    def enviar_datos_geoportal(self, atributos_payload):
        """
        Envía datos de actualización a la capa de features del geoportal.

        Parámetros:
        - atributos_payload: Lista de atributos con estructura compatible con el endpoint de updateFeatures.

        Retorna:
        - Resultado del proceso de actualización.
        """
        endpoint = f"{self.url_geoportal}/{self.endpoint_api_features}/updateFeatures"
        payload = self._preparar_datos_geoportal(atributos_payload)

        payload = TokenHandler.aplicar_token_body(payload, self.token_provider.token)
        respuesta_json = self.clienteHTTP.post(
            endpoint,
            data=payload,
        )
        updateResults = respuesta_json["updateResults"]
        return updateResults

    def _preparar_datos_geoportal(self, atributos_payload):
        """
        Crea el cuerpo de la petición para actualizar entidades en el geoportal.

        Parámetros:
        - atributos_payload: Lista de diccionarios con datos de entidades a actualizar.

        Retorna:
        - Diccionario que representa el payload final a enviar al API de ArcGIS.
        """
        return {"f": self.format, "trueCurveClient": self.true_curve, "features": json.dumps(atributos_payload)}
