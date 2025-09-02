from datetime import datetime

import pytest


@pytest.fixture
def mock_datetime_patch(monkeypatch):
    """
    Fixture que permite fijar datetime.now() a una fecha específica durante un test.

    - Mockea datetime.now() devolviendo siempre la misma fecha.
    - Requiere la ruta del import del módulo que usa datetime (para que surta efecto).

    Parámetros:
    - ruta_importacion (str): Ruta completa donde se importa `datetime` (ej. "mi_paquete.mi_modulo.datetime").
    - fecha (datetime.datetime): Fecha fija que se desea devolver cuando se llama a `now()` o `utcnow()`.

    Uso:
        def test_xxx(mock_datetime_patch):
            mock_datetime_patch(datetime(2025, 5, 29), "paquete.modulo.datetime")
    """

    def _patch(ruta_importacion, fecha):
        class MockDateTime(datetime):
            @classmethod
            def now(cls, tz=None):
                return fecha

            @classmethod
            def utcnow(cls):
                return fecha

        monkeypatch.setattr(ruta_importacion, MockDateTime)

    return _patch
