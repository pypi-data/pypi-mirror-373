class TokenHandler:
    """
    Utilidad para aplicar un token de autenticación en distintas partes de una petición HTTP.
    Todos los métodos son estáticos y retornan una copia del objeto modificado.
    """

    @staticmethod
    def aplicar_token_bearer(headers: dict, token: str) -> dict:
        """
        Aplica el token en los headers como 'Bearer {token}'.
        Devuelve una copia de los headers modificados.
        """
        updated_headers = headers.copy()
        updated_headers["Authorization"] = f"Bearer {token}"
        return updated_headers

    @staticmethod
    def aplicar_token_url(url: str, token: str) -> dict:
        """
        Aplica el token en la URL.
        Devuelve un diccionario con la URL modificada.
        """
        updated_url = f"{url}{token}"
        return updated_url

    @staticmethod
    def aplicar_token_body(data: dict, token: str, param_name: str = "token") -> dict:
        """
        Aplica el token en el cuerpo de la petición.
        Devuelve una copia del cuerpo de la petición modificado.
        """
        updated_data = data.copy()
        updated_data[param_name] = token
        return updated_data
