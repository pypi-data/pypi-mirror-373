import logging

import requests


class ClienteHTTP:
    """
    Cliente para realizar llamadas HTTP reutilizables basado en requests.Session.
    Permite descargar archivos y está diseñado para ser fácilmente ampliable en caso de que se necesiten agregar funcionalidades adicionales.
    """

    def __init__(self, headers=None, timeout=10, verify_ssl=True):
        self.log = logging.getLogger()
        self.headers = headers or {}
        self.timeout = timeout
        self.verify_ssl = verify_ssl

        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get(self, url, params=None, headers=None):
        params = params or {}
        request_headers = self.session.headers.copy()
        request_headers.update(headers or {})
        try:
            response = self.session.get(url, params=params, headers=request_headers, timeout=self.timeout, verify=self.verify_ssl)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.log.error(f"Error HTTP en GET a {url}: {e}")
            raise


    def post(self, url, *, data=None, files=None, headers=None):
        data = data or {}
        request_headers = self.session.headers.copy()
        request_headers.update(headers or {})
        try:
            response = self.session.post(
                url,
                data=data,
                files=files,
                headers=request_headers,
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.log.error(f"Error HTTP en POST a {url}: {e}")
            raise



    def descargar_archivo(self, url, destino):
        """
        Descarga un archivo desde la URL dada y lo guarda en la ruta 'destino'.
        """
        try:
            response = self.session.get(url, stream=True, timeout=self.timeout, verify=self.verify_ssl)
            response.raise_for_status()

            with open(destino, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            self.log.info(f"Archivo descargado correctamente desde {url} a {destino}")

            return True

        except requests.RequestException as e:
            self.log.error(f"Error HTTP al descargar {url}: {e}")
            raise

        except Exception as e:
            self.log.error(f"Error general al descargar {url}: {e}")
            raise

    def cerrar(self):
        """
        Cierra la sesión HTTP y libera recursos.
        """
        if self.session:
            self.session.close()
        self.log.info("Sesión HTTP cerrada correctamente.")
