import json
import os


class GeneradorPayload:
    def __init__(self, carpeta: str):
        self.carpeta = carpeta

    def generar_payload(self, nombre_archivo: str) -> list[dict]:
        ruta = os.path.join(self.carpeta, nombre_archivo)
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)