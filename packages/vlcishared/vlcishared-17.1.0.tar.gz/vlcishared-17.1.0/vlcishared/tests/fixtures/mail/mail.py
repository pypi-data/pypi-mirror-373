import pytest
from unittest.mock import MagicMock
from vlcishared.mail.mail_sender import EmailSender


@pytest.fixture
def mock_mail_patch(monkeypatch):
    """
    Fixture que permite parchear EmailSender para cualquier test.

    Uso:
        def test_algo(mock_mail_patch):
            mock_sender = mock_mail_patch("ruta.al.EmailSender", send_side_effect=Exception("fallo"))
            ...
    """

    def _patch(
        ruta_importacion: str,
        send_side_effect=None,
    ):
        smtp_mock = MagicMock()

        class DummyEmailServer:
            def get_smtp_connection(self):
                return smtp_mock

        sender = EmailSender(
            email_server=DummyEmailServer(),
            sender="test@correo.com",
            sender_name="ETL Test",
            subject="Carga IBI OK",
            to="destinatario@correo.com",
        )

        if send_side_effect is not None:
            sender.send = MagicMock(side_effect=send_side_effect)
        else:
            original_send = sender.send
            sender.send = MagicMock(side_effect=original_send)

        monkeypatch.setattr(ruta_importacion, lambda *args, **kwargs: sender)

        return sender

    return _patch
