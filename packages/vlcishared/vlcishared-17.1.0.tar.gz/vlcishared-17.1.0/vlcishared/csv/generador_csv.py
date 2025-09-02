import csv
import os
from typing import List, Optional


class GeneradorCSV:
    def __init__(self, carpeta_exportacion: str, delimitador: str = ";"):
        self._carpeta_exportacion = carpeta_exportacion
        self._delimitador = delimitador

    def exportar(self, nombre_fichero: str, filas: List[List], cabecera: Optional[List[str]] = None) -> str:
        """
        Exporta los datos a un archivo CSV en la carpeta de exportación.

        Args:
            nombre_fichero (str): Nombre del fichero, ej. 'datos.csv'.
            filas (List[List]): Lista de listas con las filas del CSV.
            cabecera (Optional[List[str]]): Cabecera del CSV, si se desea incluir.

        Returns:
            str: Ruta absoluta del fichero generado.
        """
        ruta_csv = self._construir_ruta(nombre_fichero)
        self._escribir_csv(ruta_csv, filas, cabecera)
        return ruta_csv

    def _construir_ruta(self, nombre_fichero: str) -> str:
        """Crea la carpeta si no existe y devuelve la ruta completa del archivo."""
        os.makedirs(self._carpeta_exportacion, exist_ok=True)
        ruta_exportacion = os.path.join(self._carpeta_exportacion, nombre_fichero)
        return ruta_exportacion

    def _escribir_csv(self, ruta: str, filas: List[List], cabecera: Optional[List[str]]) -> None:
        """Escribe el contenido en un archivo CSV."""
        with open(ruta, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=self._delimitador)
            if cabecera:
                writer.writerow(cabecera)
            writer.writerows(filas)
