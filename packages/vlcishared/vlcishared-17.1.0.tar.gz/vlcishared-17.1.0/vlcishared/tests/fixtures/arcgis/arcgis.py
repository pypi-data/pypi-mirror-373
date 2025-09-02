import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_arcgisclient_patch(monkeypatch):
    """
    Fixture base que crea un MagicMock que simula el cliente ArcGIS.

    Recibe la ruta completa donde se importa ArcGISClient (como string).
    Reemplaza en esa ruta la clase/función por un MagicMock para simular el cliente.

    Retorna la instancia mock creada, para poder configurarla o comprobar llamadas.
    """

    def _patch(ruta_importacion):
        mock_client = MagicMock()
        monkeypatch.setattr(ruta_importacion, lambda *args, **kwargs: mock_client)
        return mock_client

    return _patch


@pytest.fixture
def mock_arcgis_token_provider_patch():
    """
    Fixture para mockear el método obtener_token del token_provider dentro del cliente ArcGIS.

    Recibe un mock_arcgisclient (creado con mock_arcgisclient_patch),
    y opcionalmente un return_value o side_effect para configurar el método obtener_token.

    Devuelve el mismo mock_arcgisclient, con obtener_token configurado para devolver
    el valor deseado o lanzar la excepción indicada.

    Uso:
        mock_arcgis_token_provider = mock_arcgis_token_provider_patch(
            mock_arcgisclient=mock_arcgisclient_patch("modulo.donde.importa.ArcGISClient"),
            return_value="mock_token",
            side_effect=None,
        )
    """

    def _patch(mock_arcgisclient, return_value=None, side_effect=None):
        metodo_mock = getattr(mock_arcgisclient.token_provider, "obtener_token")
        if side_effect:
            metodo_mock.side_effect = side_effect
        else:
            metodo_mock.return_value = return_value  
        return mock_arcgisclient

    return _patch


@pytest.fixture
def mock_arcgis_obtener_identificadores_patch():
    """
    Fixture para mockear el método obtener_identificadores del cliente ArcGIS.

    Recibe un mock_arcgisclient (creado con mock_arcgisclient_patch),
    y opcionalmente un return_value o side_effect para configurar el método obtener_identificadores.

    Devuelve el mismo mock_arcgisclient, con obtener_identificadores configurado para devolver
    el valor deseado o lanzar la excepción indicada.

    Uso:
        mock_arcgis_obtener_identificadores = mock_arcgis_obtener_identificadores_patch(
            mock_arcgisclient=mock_arcgisclient_patch("modulo.donde.importa.ArcGISClient"),
            return_value=[{"gid": 549805, "idpm": 1006}, {"gid": 550388, "idpm": 20042001}],
            side_effect=None,
        )
    """

    def _patch(mock_arcgisclient, return_value=None, side_effect=None):
        metodo_mock = getattr(mock_arcgisclient, "obtener_identificadores")
        if side_effect:
            metodo_mock.side_effect = side_effect
        else:
            metodo_mock.return_value = return_value
        return mock_arcgisclient

    return _patch


@pytest.fixture
def mock_arcgis_enviar_datos_geoportal_patch():
    """
    Fixture para mockear el método enviar_datos_geoportal del cliente ArcGIS.

    Recibe un mock_arcgisclient (creado con mock_arcgisclient_patch), y opcionalmente return_value o side_effect,
    para simular el comportamiento esperado de enviar_datos_geoportal.

    Devuelve el mismo mock_arcgisclient.

    Uso:
        mock_arcgis_enviar_datos_geoportal = mock_arcgis_enviar_datos_geoportal_patch(
            mock_arcgisclient=mock_arcgisclient_patch("modulo.donde.importa.ArcGISClient"),
            return_value=None,
            side_effect=Exception("Error al enviar datos"),
        )
    """

    def _patch(mock_arcgisclient, return_value=None, side_effect=None):
        metodo_mock = getattr(mock_arcgisclient, "enviar_datos_geoportal")
        if side_effect:
            metodo_mock.side_effect = side_effect
        else:
            metodo_mock.return_value = return_value
        return mock_arcgisclient

    return _patch
