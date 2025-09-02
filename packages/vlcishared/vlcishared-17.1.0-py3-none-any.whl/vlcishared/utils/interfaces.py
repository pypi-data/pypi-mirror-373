from abc import ABC, abstractmethod


class ConnectionInterface(ABC):
    '''Esta clase esta pensada para obligar a las demás clases que
    usan conexiones a recursos a estandarizar el funcionamiento'''

    @abstractmethod
    def connect(self):
        """Método para conectarse a un recurso"""
        pass

    @abstractmethod
    def close(self):
        """Método que cierra la conexión a un recurso"""
        pass
