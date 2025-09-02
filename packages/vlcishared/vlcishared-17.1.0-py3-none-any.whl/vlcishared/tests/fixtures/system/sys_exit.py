from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_sys_exit(monkeypatch):
    """
    Fixture que mockea la función sys.exit para evitar que termine el proceso durante la ejecución de tests.

    - Reemplaza sys.exit por un MagicMock, permitiendo verificar si fue llamado sin detener el test.

    Uso:
        def test_mi_funcion(mock_sys_exit):
            ...
            mock_sys_exit.assert_called_once_with(0)
    """
    mock_sys_exit = MagicMock()
    monkeypatch.setattr("sys.exit", mock_sys_exit)
    return mock_sys_exit


@pytest.fixture
def mock_sys_exit_con_excepcion(monkeypatch):
    """
    Fixture que mockea la función sys.exit para poder verificar si fue llamado, pero si lanza la excepción SystemExit para detener la ejecución.

    Uso:
        def test_mi_funcion(mock_sys_exit_con_excepcion):
            ...
            with pytest.raises(SystemExit):
                main()

            mock_sys_exit_con_excepcion.assert_called_once_with(1)
    """

    def excepcion(code):
        raise SystemExit(code)

    mock_exit = MagicMock(side_effect=excepcion)
    monkeypatch.setattr("sys.exit", mock_exit)
    return mock_exit
