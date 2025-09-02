from abc import ABC, abstractmethod
from vlcishared.tokens.token_provider import TokenProvider


class ArcGISTokenProvider(TokenProvider, ABC):
    """
    Clase base abstracta para proveedores de tokens de ArcGIS.
    Define la estructura y delega en las subclases la generación
    del payload concreto.
    """

    def __init__(self, url_token_provider, username, password, format, expiration):
        super().__init__(url_token_provider)
        self.username = username
        self.password = password
        self.format = format
        self.expiration = expiration

    @abstractmethod
    def get_payload(self):
        """
        Cada subclase debe implementar este método para generar el
        payload específico de la solicitud de token.
        """
        pass

    def obtener_token(self):
        """
        Realiza la solicitud del token al servidor ArcGIS usando las credenciales
        y parámetros configurados. Asigna el token recibido a self.token.

        Lanza:
            ValueError: Si la respuesta no contiene un token válido.
        """
        payload = self.get_payload()
        respuesta = self._solicitar_nuevo_token(data=payload)
        token = respuesta.get("token")
        if token is None:
            raise ValueError("No se ha podido obtener el token.")
        self.token = token