from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from vlcishared.mail.mail_server import EmailServer


class EmailSender:
    def __init__(self, email_server: EmailServer, sender, sender_name, subject, to, cc=None):
        """Inicializa el EmailSender con la configuración del correo."""
        self.email_server = email_server
        self.sender = sender
        self.sender_name = sender_name
        self.subject = subject
        self.to = to
        self.cc = cc if cc else ""

        self.msg = MIMEMultipart()
        self.msg['From'] = f'{self.sender_name} <{self.sender}>'
        self.msg['To'] = self.to
        self.msg['Cc'] = self.cc
        self.msg['Subject'] = self.subject
        self.body = ""

    def append_line(self, message):
        """Añade una línea al cuerpo del correo en HTML."""
        self.body += message + '<br>'

    def add_attachment(self, file_path, subtype='octet-stream'):
        """Adjunta un archivo al correo."""
        file_name = file_path.split('/')[-1]
        with open(file_path, 'rb') as file:
            attachment = MIMEApplication(file.read(), _subtype=subtype)
            attachment.add_header('content-disposition', 'attachment', filename=file_name)
            self.msg.attach(attachment)

    def send(self):
        """Envía el correo usando la conexión SMTP."""
        self.msg.attach(MIMEText(self.body, 'html'))
        recipients = self.to.split(",") + self.cc.split(",")

        smtp_connection = self.email_server.get_smtp_connection()
        smtp_connection.sendmail(self.sender, recipients, self.msg.as_string())
        smtp_connection.quit()
