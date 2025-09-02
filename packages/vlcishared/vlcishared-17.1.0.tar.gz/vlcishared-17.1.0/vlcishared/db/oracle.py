import logging
from typing import Any, Dict, List, Sequence

import oracledb
from sqlalchemy import Row, create_engine, text
from sqlalchemy.orm import sessionmaker

from vlcishared.utils.interfaces import ConnectionInterface


class OracleConnector(ConnectionInterface):
    _instance = None

    def __new__(cls, host: str, port: str, sid: str,
            user: str, password: str):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_oracle(host, port, sid, user, password)
        return cls._instance

    def _initialize_oracle(self,
                 host: str,
                 port: str,
                 sid: str,
                 user: str,
                 password: str):

        self.log = logging.getLogger()
        self.engine = None
        self.Session = None
        self.session = None
        self.connection_string =\
            f"oracle+oracledb://{user}:{password}@{host}:{port}/{sid}"

    def connect(self):
        """Función que se conecta a la base de datos
        definida en el constructor"""
        try:
            self.engine = create_engine(self.connection_string)
            self.Session = sessionmaker(bind=self.engine)
            self.session = self.Session()
            self.log.info('Conexión a Oracle exitosa')
        except Exception as e:
            self.log.error(f"Error al conectar a la base de datos: {e}")
            raise e

    def close(self):
        """Cierra la conexión con la base de datos"""
        if self.session:
            self.session.close()
        if self.engine:
            self.engine.dispose()

    def commit(self):
        """Realiza un commit de la transacción actual"""
        try:
            self.session.commit()
            self.log.info("Transacción realizada con éxito.")
        except Exception as e:
            self.rollback()
            self.log.error(f"Error al hacer commit: {e}")
            raise e
        
    def execute_query(self, query: str, *params: Any) -> Any:
        try:
            if params:
                result = self.session.execute(text(query), params)
            else:
                result = self.session.execute(text(query))

            return result
        except Exception as e:
            self.log.error(f"Error al ejecutar la query: {e}")
            raise e
        
    def execute_many_query(self, query: str, params_list: List[Dict[str, Any]]) -> None:
        try:
            self.session.execute(text(query), params_list)
        except Exception as e:
            self.log.error(f"Error al ejecutar múltiples queries: {e}")
            raise 

    def rollback(self):
        """Revierte la transacción actual"""
        try:
            self.session.rollback()
            self.log.info("Transacción revertida.")
        except Exception as e:
            self.log.error(f"Error al hacer rollback: {e}")
            raise e


    def call_procedure(
            self,
            procedure_name: str,
            *params: Any) -> Sequence[Row[Any]]:
        """Llama a procedimientos almacenados en BD,
        recibe el nombre y los parámetros"""
        try:
            param_placeholders = ', '.join(
                [f':p{i}' for i in range(len(params))])
            param_dict = {f'p{i}': params[i] for i in range(len(params))}
            sql = text(f'BEGIN {procedure_name}({param_placeholders}); END;')
            self.session.execute(sql, param_dict)
            self.commit()
        except Exception as e:
            self.rollback()
            self.log.error(f"Fallo llamando a {procedure_name}: {e}")
            raise 

    
    def call_function(self, function_name: str, *params: Any, out_type=oracledb.STRING) -> Any:
        """
        Llama a una función de Oracle y retorna el resultado.

        Parámetros:
        ----------
        function_name : str
            Nombre de la función Oracle (puede incluir paquete).
        *params : cualquier tipo
            Parámetros de entrada pasados como argumentos posicionales en orden.
        out_type : tipo oracledb (por defecto STRING)
            Tipo del parámetro de salida (oracledb.STRING, NUMBER, DATE, etc.)

        Retorna:
        -------
        Valor devuelto por la función.
        """
        try:
            conn = self.session.connection()
            cursor = conn.connection.cursor()

            out_var = cursor.var(out_type)

            param_dict = {f"{i+1}": v for i, v in enumerate(params)}
            param_dict["result"] = out_var

            placeholders = ", ".join(f":{i+1}" for i in range(len(params)))
            plsql = f"BEGIN :result := {function_name}({placeholders}); END;"

            cursor.execute(plsql, param_dict)
            self.commit()

            return out_var.getvalue()

        except Exception as e:
            self.rollback()
            self.log.error(f"Error al llamar a función {function_name}: {e}")
            raise


