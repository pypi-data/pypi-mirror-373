from unittest.mock import MagicMock, Mock

import pytest
from requests import Response
from requests.exceptions import ConnectionError
from tc_etl_lib import exceptions


@pytest.fixture
def mock_iota_manager_patch(monkeypatch):
    """
    Fixture que mockea iotaManager para evitar conexiones HTTP reales.

    - Mockea los métodos send_http y send_batch_http
    - Permite simular respuestas exitosas y errores
    - Simula el comportamiento de requests.Session
    - Permite testear funciones que usan iotaManager sin hacer llamadas HTTP reales

    Uso básico:
        def test_send_success(mock_iota_manager_patch):
            mock_iota = mock_iota_manager_patch(
                "modulo.iotaManager",
                send_http_return=True
            )
            resultado = mock_iota.send_http({"temperatura": 25})
            assert resultado is True
    """

    def _patch(
        ruta_clase_mockear: str,
        retornar_constructor=False,
        send_http_return=None,
        send_http_side_effect=None,
        send_batch_http_return=None,
        send_batch_http_side_effect=None,
        endpoint="http://mock-endpoint",
        device_id="mock_device",
        api_key="mock_api_key",
        sleep_send_batch=0,
        timeout=10,
        post_retry_connect=3,
        post_retry_backoff_factor=20,
    ):
        """
        Función interna para configurar el mock de iotaManager.

        Args:
            ruta_clase_mockear: Ruta donde se importa iotaManager (ej: "modulo.iotaManager")
            send_http_return: Valor de retorno para send_http (por defecto True)
            send_http_side_effect: Excepción a lanzar en send_http
            send_batch_http_return: Valor de retorno para send_batch_http (por defecto True)
            send_batch_http_side_effect: Excepción a lanzar en send_batch_http
            endpoint, device_id, api_key, etc.: Parámetros del constructor
        """

        mock_iota_instance = MagicMock()

        mock_iota_instance.endpoint = endpoint
        mock_iota_instance.device_id = device_id
        mock_iota_instance.api_key = api_key
        mock_iota_instance.sleep_send_batch = sleep_send_batch
        mock_iota_instance.timeout = timeout
        mock_iota_instance.post_retry_connect = post_retry_connect
        mock_iota_instance.post_retry_backoff_factor = post_retry_backoff_factor

        mock_session = MagicMock()
        mock_iota_instance.session = mock_session

        mock_iota_instance.send_http.return_value = send_http_return or True
        mock_iota_instance.send_batch_http.return_value = send_batch_http_return or True

        if send_http_side_effect:
            mock_iota_instance.send_http.side_effect = send_http_side_effect

        if send_batch_http_side_effect:
            mock_iota_instance.send_batch_http.side_effect = send_batch_http_side_effect

        mock_constructor = MagicMock(return_value=mock_iota_instance)
        monkeypatch.setattr(ruta_clase_mockear, mock_constructor)

        if retornar_constructor:
            return mock_constructor, mock_iota_instance

        return mock_iota_instance

    return _patch


@pytest.fixture
def mock_iota_manager_with_response_patch(monkeypatch):
    """
    Fixture avanzada que mockea iotaManager con control detallado sobre las respuestas HTTP.

    Permite simular respuestas HTTP específicas, códigos de estado, y errores de conexión.

    Uso:
        def test_http_response_codes(mock_iota_manager_with_response_patch):
            mock_iota = mock_iota_manager_with_response_patch(
                "modulo.iotaManager",
                http_status_code=500,
                response_json={"error": "Internal Server Error"}
            )
            with pytest.raises(Exception):  # FetchError se lanzará
                mock_iota.send_http({"data": "test"})
    """

    def _patch(ruta_clase_mockear: str, http_status_code=200, response_json=None, connection_error=False, **kwargs):
        mock_iota_instance = MagicMock()

        for attr, value in kwargs.items():
            setattr(mock_iota_instance, attr, value)

        mock_response = Mock(spec=Response, status_code=http_status_code, **{"json.return_value": response_json or {}})

        mock_session = MagicMock()
        mock_iota_instance.session = mock_session

        if connection_error:
            mock_session.post.side_effect = ConnectionError("Connection failed")
        else:
            mock_session.post.return_value = mock_response

        def mock_send_http(data):
            if not isinstance(data, dict):
                raise TypeError("The 'data' parameter should be a dictionary with key-value pairs.")

            if connection_error:
                raise ConnectionError("Connection failed")

            if http_status_code == 200:
                return True
            else:
                raise exceptions.FetchError(
                    response=mock_response,
                    method="POST",
                    url=mock_iota_instance.endpoint,
                    params={
                        "i": mock_iota_instance.device_id,
                        "k": mock_iota_instance.api_key,
                    },
                    headers={"Content-Type": "application/json"},
                )

        mock_iota_instance.send_http.side_effect = mock_send_http

        mock_constructor = MagicMock(return_value=mock_iota_instance)
        monkeypatch.setattr(ruta_clase_mockear, mock_constructor)

        return mock_iota_instance

    return _patch
