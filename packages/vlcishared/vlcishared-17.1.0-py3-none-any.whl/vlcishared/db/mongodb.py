import logging

from pymongo import MongoClient, errors


class MongoDBConnector():
    def __init__(self, host: str, port: str, auth_source: str, user: str, password: str):
        self.uri = (
            f"mongodb://{user}:{password}@"
            f"{host}:{port}/"
            f"{auth_source}?authSource={auth_source}"
        )
        self.host = host
        self.port = port
        self.auth_source = auth_source
        self.user = user
        self.password = password
        self.client = None
        self.log = logging.getLogger()

    def get_db_connection(self):
        """Función que se conecta a la base de datos de MongoDB
            definida en el constructor"""
        try:
            self.log.info('Conectando a MongoDB')
            self.client = MongoClient(self.uri)
            return self.client.get_database()
        except errors.ConnectionFailure as e:
            raise ConnectionError(f"Error de conexión a MongoDB: {e}")

    def disconnect(self):
        if self.client:
            self.log.info('Desconectando de MongoDB')
            self.client.close()

    def insert_data(self, collection_name: str, data):
        """
        Function to insert data into a specified MongoDB collection.
        """

        db = self.get_db_connection()
        collection = db[collection_name]

        try:
            if isinstance(data, list):
                self.log.info(f'Insert multiple docs into {collection_name}')
                result = collection.insert_many(data)
                self.log.info(f'Inserted documents')
            else:
                self.log.info(f'Insert a single doc into {collection_name}')
                result = collection.insert_one(data)
                self.log.info(f'Inserted document ID: {result.inserted_id}')
        except errors.PyMongoError as e:
            self.log.error(f"Error while inserting data into MongoDB: {e}")
            raise
        finally:
            self.disconnect()
