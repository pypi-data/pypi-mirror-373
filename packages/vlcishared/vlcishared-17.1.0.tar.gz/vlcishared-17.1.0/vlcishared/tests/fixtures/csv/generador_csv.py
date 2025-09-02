import pytest
from unittest.mock import MagicMock
import gestion_csv.gestor_csv as gestor_csv


@pytest.fixture
def mock_exportar_csv(monkeypatch):
    """
    Fixture que mockea el método exportar de GeneradorCSV para observar el 
    comportamiento del código a la hora de escribir en archivos CSV.

    - Reemplaza _generador_csv.exportar por un MagicMock que mantiene el comportamiento
      original (llama al método real) pero permite inspeccionar llamadas.

    Uso:
        def test_exportar_csv(mock_exportar_csv):
            # Obtener las entradas para comprobar que se han escrito los datos esperados
            nombre_fichero, filas_enviadas = mock_exportar_csv.call_args[0]

            # Obtener la salida del método exportar
            ruta_csv = mock_exportar_csv.return_value
    """
    generador_instancia = gestor_csv._generador_csv

    original_exportar = generador_instancia.exportar

    def side_effect(*args, **kwargs):
        resultado = original_exportar(*args, **kwargs)
        mock_method.return_value = resultado
        return resultado

    mock_method = MagicMock(side_effect=side_effect)
    monkeypatch.setattr(generador_instancia, "exportar", mock_method)

    mock_method.return_value = None

    yield mock_method
