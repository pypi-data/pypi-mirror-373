from ftplib import FTP
import os
from vlcishared.utils.interfaces import ConnectionInterface


class FTPClient(ConnectionInterface):
    '''Clase que se conecta a un servidor FTP para listar ficheros'''

    def __init__(self, host: str, username: str, password: str, port=21):
        '''Inicializa el cliente FTP con los datos de conexión'''
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.ftp = None

    def connect(self) -> None:
        '''Intenta conectarse al servidor FTP'''
        try:
            self.ftp = FTP()
            self.ftp.connect(self.host, self.port)
            self.ftp.login(self.username, self.password)
        except Exception as e:
            raise ConnectionRefusedError(f"Conexión fallida: {str(e)}")

    def list(self, remote_path: str) -> list:
        '''Devuelve una lista con los ficheros en el directorio indicado'''
        try:
            self.ftp.cwd(remote_path) 
            return self.ftp.nlst() 
        except Exception as e:
            raise ConnectionAbortedError(
                f"Fallo al listar los archivos: {str(e)}")

    def close(self):
        '''Cierra la conexión al servidor FTP'''
        if self.ftp:
            self.ftp.quit()
            print(f"Conexión a {self.host} cerrada.")

    def upload(self, local_file: str, remote_path: str):
        '''Sube el fichero indicado desde la máquina local al servidor FTP'''
        try:
            remote_path = os.path.join(remote_path, os.path.basename(local_file))
            with open(local_file, 'rb') as file:
                self.ftp.storbinary(f"STOR {remote_path}", file)
        except Exception as e:
            raise ConnectionAbortedError(f"Subida fallida: {str(e)}")
